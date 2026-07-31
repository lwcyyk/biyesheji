//go:build linux

package sqlite

import (
	"bytes"
	"context"
	"crypto/ed25519"
	"crypto/sha256"
	"errors"
	"testing"
	"time"

	credential "vdns.local/vdns/internal/credential/domain"
	"vdns.local/vdns/internal/cryptokit"
	"vdns.local/vdns/internal/protocol"
	siteapp "vdns.local/vdns/internal/site/application"
	sitedomain "vdns.local/vdns/internal/site/domain"
)

func TestSiteChangeRepositoryRequiresDurableCandidateAndPersistsRecoveryState(t *testing.T) {
	t.Parallel()
	fixture := newSiteChangeRepositoryFixture(t)
	ctx := context.Background()
	if err := fixture.repository.Create(ctx, fixture.attempt); err != nil {
		t.Fatal(err)
	}
	if err := fixture.repository.Transition(
		ctx, fixture.attempt.ChangeID,
		siteapp.AttemptCandidateDurable,
		siteapp.AttemptSiteUpdatePending,
		nil, nil, nil,
	); err != nil {
		t.Fatal(err)
	}
	receiptKey := ed25519.NewKeyFromSeed(
		bytes.Repeat([]byte{0x51}, ed25519.SeedSize),
	)
	request := sitedomain.ChangeRequest{
		ChangeID:        fixture.attempt.ChangeID,
		CredentialID:    fixture.attempt.CredentialID,
		ExpectedVersion: 1, NewVersion: 2,
		PolicyHash:      fixture.attempt.PolicyHash,
		CurrentPassword: fixture.currentPassword,
		NewPassword:     fixture.newPassword,
	}
	receipt, err := sitedomain.SignReceipt(
		receiptKey,
		sitedomain.NewReceiptPayload(
			request, sitedomain.ReceiptApplied,
			fixture.attempt.PolicyHash, 2,
		),
	)
	if err != nil {
		t.Fatal(err)
	}
	if err := fixture.repository.Transition(
		ctx, fixture.attempt.ChangeID,
		siteapp.AttemptSiteUpdatePending,
		siteapp.AttemptSiteChangedLocalCommitPending,
		receipt, nil, nil,
	); err != nil {
		t.Fatal(err)
	}
	if err := fixture.repository.Transition(
		ctx, fixture.attempt.ChangeID,
		siteapp.AttemptSiteChangedLocalCommitPending,
		siteapp.AttemptSiteConfirmPending,
		nil, nil, nil,
	); err != nil {
		t.Fatal(err)
	}
	restored, err := fixture.repository.Load(ctx, fixture.attempt.ChangeID)
	if err != nil {
		t.Fatal(err)
	}
	if restored.Status != siteapp.AttemptSiteConfirmPending ||
		restored.NamespaceID != fixture.attempt.NamespaceID ||
		restored.CandidateDescriptorHash != fixture.attempt.CandidateDescriptorHash ||
		restored.ReceiptStatus == nil ||
		*restored.ReceiptStatus != sitedomain.ReceiptApplied ||
		restored.ReceiptDigest == nil ||
		*restored.ReceiptDigest != receipt.Digest() {
		t.Fatalf("restored attempt mismatch: %+v", restored)
	}
}

func TestSiteChangeRepositoryRejectsMissingCandidateObjectAndStaleTransition(t *testing.T) {
	t.Parallel()
	t.Run("missing-candidate-object", func(t *testing.T) {
		t.Parallel()
		fixture := newSiteChangeRepositoryFixture(t)
		if _, err := fixture.identity.database.ExecContext(
			context.Background(),
			`UPDATE content_objects
 SET state = 'MISSING'
 WHERE object_hash = (
   SELECT object_hash FROM credential_version_fields
   WHERE credential_id = ? AND version = 2 LIMIT 1
 )`,
			fixture.attempt.CredentialID[:],
		); err != nil {
			t.Fatal(err)
		}
		if err := fixture.repository.Create(
			context.Background(), fixture.attempt,
		); !errors.Is(err, ErrSiteCandidateNotDurable) {
			t.Fatalf("missing object error=%v", err)
		}
	})
	t.Run("stale-transition", func(t *testing.T) {
		t.Parallel()
		fixture := newSiteChangeRepositoryFixture(t)
		ctx := context.Background()
		if err := fixture.repository.Create(ctx, fixture.attempt); err != nil {
			t.Fatal(err)
		}
		if err := fixture.repository.Transition(
			ctx, fixture.attempt.ChangeID,
			siteapp.AttemptSiteUpdatePending,
			siteapp.AttemptFailedRetryable,
			nil, nil, nil,
		); !errors.Is(err, ErrInvalidSiteChangeAttempt) {
			t.Fatalf("stale transition error=%v", err)
		}
		restored, err := fixture.repository.Load(ctx, fixture.attempt.ChangeID)
		if err != nil || restored.Status != siteapp.AttemptCandidateDurable {
			t.Fatalf("stale transition changed state: %+v %v", restored, err)
		}
	})
}

func TestSiteChangeRepositoryRecoversAfterEveryMainTransition(t *testing.T) {
	t.Run("confirmed-path", func(t *testing.T) {
		fixture := newSiteChangeRepositoryFixture(t)
		ctx := context.Background()
		if err := fixture.repository.Create(ctx, fixture.attempt); err != nil {
			t.Fatal(err)
		}
		fixture.restartAndRequireStatus(t, siteapp.AttemptCandidateDurable)
		path := []siteapp.AttemptStatus{
			siteapp.AttemptSiteUpdatePending,
			siteapp.AttemptSiteChangedLocalCommitPending,
			siteapp.AttemptSiteConfirmPending,
			siteapp.AttemptActive,
		}
		current := siteapp.AttemptCandidateDurable
		for _, next := range path {
			var evidence *protocol.EvidenceLevel
			var eventID *protocol.EventID
			if next == siteapp.AttemptActive {
				level := protocol.EvidenceUserSignedConfirmation
				evidence = &level
				operationRepository, err := NewOperationRepository(
					fixture.identity.database,
				)
				if err != nil {
					t.Fatal(err)
				}
				fixture.identity.repository = operationRepository
				sealed := fixture.identity.sealAndSign(
					t, fixture.identity.eventID, 1, nil,
					[]byte("user confirmation event"),
				)
				if _, err := operationRepository.CommitEvent(
					ctx, sealed.request,
				); err != nil {
					t.Fatal(err)
				}
				value := fixture.identity.eventID
				eventID = &value
			}
			if err := fixture.repository.Transition(
				ctx, fixture.attempt.ChangeID, current, next,
				nil, evidence, eventID,
			); err != nil {
				t.Fatalf("%v -> %v: %v", current, next, err)
			}
			fixture.restartAndRequireStatus(t, next)
			current = next
		}
	})
	t.Run("uncertain-retry-review-path", func(t *testing.T) {
		fixture := newSiteChangeRepositoryFixture(t)
		ctx := context.Background()
		if err := fixture.repository.Create(ctx, fixture.attempt); err != nil {
			t.Fatal(err)
		}
		type edge struct {
			next     siteapp.AttemptStatus
			evidence *protocol.EvidenceLevel
		}
		e1, e2 := protocol.EvidenceSubmitObserved, protocol.EvidencePageSuccessIndicated
		path := []edge{
			{next: siteapp.AttemptSiteUpdatePending},
			{next: siteapp.AttemptFailedRetryable},
			{next: siteapp.AttemptSiteUpdatePending},
			{next: siteapp.AttemptSiteStatusUnknown, evidence: &e1},
			{next: siteapp.AttemptReviewRequired, evidence: &e2},
			{next: siteapp.AttemptSiteConfirmPending},
		}
		current := siteapp.AttemptCandidateDurable
		for _, item := range path {
			if err := fixture.repository.Transition(
				ctx, fixture.attempt.ChangeID, current, item.next,
				nil, item.evidence, nil,
			); err != nil {
				t.Fatalf("%v -> %v: %v", current, item.next, err)
			}
			fixture.restartAndRequireStatus(t, item.next)
			current = item.next
		}
	})
	t.Run("abort-paths", func(t *testing.T) {
		for _, viaFailure := range []bool{false, true} {
			fixture := newSiteChangeRepositoryFixture(t)
			ctx := context.Background()
			if err := fixture.repository.Create(ctx, fixture.attempt); err != nil {
				t.Fatal(err)
			}
			current := siteapp.AttemptCandidateDurable
			if viaFailure {
				if err := fixture.repository.Transition(
					ctx, fixture.attempt.ChangeID, current,
					siteapp.AttemptSiteUpdatePending, nil, nil, nil,
				); err != nil {
					t.Fatal(err)
				}
				fixture.restartAndRequireStatus(t, siteapp.AttemptSiteUpdatePending)
				if err := fixture.repository.Transition(
					ctx, fixture.attempt.ChangeID,
					siteapp.AttemptSiteUpdatePending,
					siteapp.AttemptFailedRetryable, nil, nil, nil,
				); err != nil {
					t.Fatal(err)
				}
				fixture.restartAndRequireStatus(t, siteapp.AttemptFailedRetryable)
				current = siteapp.AttemptFailedRetryable
			}
			if err := fixture.repository.Transition(
				ctx, fixture.attempt.ChangeID, current,
				siteapp.AttemptAborted, nil, nil, nil,
			); err != nil {
				t.Fatal(err)
			}
			fixture.restartAndRequireStatus(t, siteapp.AttemptAborted)
		}
	})
}

type siteChangeRepositoryFixture struct {
	identity        *operationFixture
	repository      *SiteChangeAttemptRepository
	attempt         siteapp.ChangeAttempt
	currentPassword *cryptokit.Secret
	newPassword     *cryptokit.Secret
}

func (fixture *siteChangeRepositoryFixture) restartAndRequireStatus(
	t *testing.T,
	expected siteapp.AttemptStatus,
) {
	t.Helper()
	ctx := context.Background()
	var sequence int
	var name, path string
	if err := fixture.identity.database.QueryRowContext(
		ctx, "PRAGMA database_list",
	).Scan(&sequence, &name, &path); err != nil || path == "" {
		t.Fatalf("database path = %q (%d/%s), %v", path, sequence, name, err)
	}
	if err := fixture.identity.database.Close(); err != nil {
		t.Fatal(err)
	}
	reopened, err := Open(ctx, path)
	if err != nil {
		t.Fatal(err)
	}
	fixture.identity.database = reopened
	repository, err := NewSiteChangeAttemptRepository(
		reopened, staticClock{value: time.UnixMilli(1_700_000_003_000)},
	)
	if err != nil {
		t.Fatal(err)
	}
	fixture.repository = repository
	restored, err := repository.Load(ctx, fixture.attempt.ChangeID)
	if err != nil || restored.Status != expected {
		t.Fatalf("restart status = %v, want %v, err=%v", restored.Status, expected, err)
	}
}

func newSiteChangeRepositoryFixture(t *testing.T) *siteChangeRepositoryFixture {
	t.Helper()
	ctx := context.Background()
	identity := newOperationFixture(t)
	identity.credentialID[0] ^= 0x79
	repository, err := NewCredentialRepository(identity.database)
	if err != nil {
		t.Fatal(err)
	}
	fieldRoot := credentialFieldRoot(t, identity.namespaceID)
	policyHash := sha256.Sum256([]byte("test-policy"))
	origin := sha256.Sum256([]byte("site-origin"))
	passwordV1, passwordV1Path := storedCredentialField(
		t, identity, fieldRoot, identity.credentialID, 1,
		cryptokit.FieldPassword, "password-v1",
	)
	v1, err := credential.NewVersionDraft(
		identity.credentialID, 1, 1, credential.VersionActive,
		nil, policyHash, []credential.FieldMapping{passwordV1},
	)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := repository.CommitVersion(ctx, storedCredentialRequest(
		t, identity, v1, identity.namespaceID, origin, nil,
		map[cryptokit.FieldType]string{
			cryptokit.FieldPassword: passwordV1Path,
		},
		true, true, 1_700_000_001_000,
	)); err != nil {
		t.Fatal(err)
	}
	previous := v1.DescriptorHash()
	passwordV2, passwordV2Path := storedCredentialField(
		t, identity, fieldRoot, identity.credentialID, 2,
		cryptokit.FieldPassword, "password-v2",
	)
	v2, err := credential.NewVersionDraft(
		identity.credentialID, 2, 2,
		credential.VersionPendingCandidate,
		&previous, policyHash, []credential.FieldMapping{passwordV2},
	)
	if err != nil {
		t.Fatal(err)
	}
	expected := uint64(1)
	if _, err := repository.CommitVersion(ctx, storedCredentialRequest(
		t, identity, v2, identity.namespaceID, origin, &expected,
		map[cryptokit.FieldType]string{
			cryptokit.FieldPassword: passwordV2Path,
		},
		false, false, 1_700_000_002_000,
	)); err != nil {
		t.Fatal(err)
	}
	siteRepository, err := NewSiteChangeAttemptRepository(
		identity.database,
		staticClock{value: time.UnixMilli(1_700_000_003_000)},
	)
	if err != nil {
		t.Fatal(err)
	}
	var changeID sitedomain.ChangeID
	copy(changeID[:], bytes.Repeat([]byte{0x65}, len(changeID)))
	current, _ := cryptokit.NewSecret([]byte("password-v1"))
	replacement, _ := cryptokit.NewSecret([]byte("password-v2"))
	t.Cleanup(current.Destroy)
	t.Cleanup(replacement.Destroy)
	return &siteChangeRepositoryFixture{
		identity: identity, repository: siteRepository,
		attempt: siteapp.ChangeAttempt{
			ChangeID: changeID, NamespaceID: identity.namespaceID,
			CredentialID:    identity.credentialID,
			PreviousVersion: 1, CandidateVersion: 2,
			CandidateDescriptorHash: v2.DescriptorHash(),
			PolicyHash:              policyHash,
			RequestHash:             sha256.Sum256([]byte("public-request")),
			Status:                  siteapp.AttemptCandidateDurable,
		},
		currentPassword: current, newPassword: replacement,
	}
}

type staticClock struct {
	value time.Time
}

func (clock staticClock) Now() time.Time { return clock.value }
