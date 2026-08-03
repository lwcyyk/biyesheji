package application

import (
	"bytes"
	"context"
	"crypto/ed25519"
	"crypto/sha256"
	"errors"
	"sync"
	"testing"

	"vpass.local/vpass/internal/adapters/outbound/mocksite"
	"vpass.local/vpass/internal/cryptokit"
	"vpass.local/vpass/internal/protocol"
	sitedomain "vpass.local/vpass/internal/site/domain"
)

func TestCoordinatorRequiresSeparateStrongConfirmation(t *testing.T) {
	t.Parallel()
	fixture := newChangeFixture(t, mocksite.BehaviorSuccess, 0x21)
	defer fixture.close()
	status, err := fixture.coordinator.Start(
		context.Background(), fixture.request, fixture.namespaceID,
		fixture.descriptorHash,
	)
	if err != nil || status != AttemptSiteConfirmPending {
		t.Fatalf("Start status=%d error=%v", status, err)
	}
	if fixture.store.current.Status == AttemptActive ||
		fixture.authorizer.calls != 0 {
		t.Fatal("site call activated candidate before confirmation")
	}
	if err := fixture.coordinator.Confirm(
		context.Background(), fixture.request.ChangeID,
		protocol.EvidenceSubmitObserved,
	); !errors.Is(err, ErrConfirmationRequired) {
		t.Fatalf("weak confirmation error=%v", err)
	}
	if fixture.store.current.Status != AttemptSiteStatusUnknown {
		t.Fatal("E1 did not move the ambiguous result to UNKNOWN")
	}
	if err := fixture.coordinator.Confirm(
		context.Background(), fixture.request.ChangeID,
		protocol.EvidenceSiteSignedReceipt,
	); !errors.Is(err, ErrConfirmationRequired) {
		t.Fatalf("mock E4 was accepted as a real site receipt: %v", err)
	}
	if fixture.store.current.Status != AttemptSiteStatusUnknown {
		t.Fatalf("mock E4 changed UNKNOWN state=%v", fixture.store.current.Status)
	}
	if err := fixture.coordinator.Confirm(
		context.Background(), fixture.request.ChangeID,
		protocol.EvidenceUserSignedConfirmation,
	); err != nil {
		t.Fatal(err)
	}
	if fixture.store.current.Status != AttemptActive ||
		fixture.store.current.Evidence == nil ||
		*fixture.store.current.Evidence != protocol.EvidenceUserSignedConfirmation ||
		fixture.store.current.ConfirmationEventID == nil ||
		fixture.authorizer.calls != 1 {
		t.Fatal("strong signed site confirmation did not activate")
	}
}

func TestCoordinatorE0ToE5DecisionMatrix(t *testing.T) {
	t.Parallel()
	tests := []struct {
		name       string
		evidence   protocol.EvidenceLevel
		want       AttemptStatus
		wantActive bool
	}{
		{"E0", protocol.EvidenceAutofillObserved, AttemptSiteStatusUnknown, false},
		{"E1", protocol.EvidenceSubmitObserved, AttemptSiteStatusUnknown, false},
		{"E2", protocol.EvidencePageSuccessIndicated, AttemptReviewRequired, false},
		{"E3-default", protocol.EvidenceNewPasswordReloginConfirmed, AttemptReviewRequired, false},
		{"E4-mock", protocol.EvidenceSiteSignedReceipt, AttemptReviewRequired, false},
		{"E5", protocol.EvidenceUserSignedConfirmation, AttemptActive, true},
	}
	for index, test := range tests {
		test := test
		t.Run(test.name, func(t *testing.T) {
			t.Parallel()
			fixture := newChangeFixture(t, mocksite.BehaviorSuccess, byte(0x70+index))
			defer fixture.close()
			status, err := fixture.coordinator.Start(
				context.Background(), fixture.request, fixture.namespaceID,
				fixture.descriptorHash,
			)
			if err != nil || status != AttemptSiteConfirmPending {
				t.Fatalf("start status=%v err=%v", status, err)
			}
			err = fixture.coordinator.Confirm(
				context.Background(), fixture.request.ChangeID, test.evidence,
			)
			if test.wantActive && err != nil {
				t.Fatal(err)
			}
			if !test.wantActive && !errors.Is(err, ErrConfirmationRequired) {
				t.Fatalf("weak evidence error=%v", err)
			}
			if fixture.store.current.Status != test.want {
				t.Fatalf("status=%v want=%v", fixture.store.current.Status, test.want)
			}
		})
	}
}

func TestCoordinatorAllowsE3OnlyUnderStrictReloginPolicy(t *testing.T) {
	t.Parallel()
	fixture := newChangeFixture(t, mocksite.BehaviorSuccess, 0x7f)
	defer fixture.close()
	coordinator, err := NewCoordinatorWithPolicy(
		fixture.connector, fixture.store, fixture.authorizer,
		protocol.EvidenceActivationPolicy{
			AllowStrictRelogin: true, AllowUserConfirmation: true,
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	fixture.coordinator = coordinator
	if _, err := fixture.coordinator.Start(
		context.Background(), fixture.request, fixture.namespaceID,
		fixture.descriptorHash,
	); err != nil {
		t.Fatal(err)
	}
	if err := fixture.coordinator.Confirm(
		context.Background(), fixture.request.ChangeID,
		protocol.EvidenceNewPasswordReloginConfirmed,
	); err != nil {
		t.Fatal(err)
	}
	if fixture.store.current.Status != AttemptActive {
		t.Fatalf("strict E3 status=%v", fixture.store.current.Status)
	}
}

func TestCoordinatorRecoversLostResponseAndSeparatesUnknownReview(t *testing.T) {
	t.Parallel()
	t.Run("response-lost-after-apply", func(t *testing.T) {
		t.Parallel()
		fixture := newChangeFixture(
			t, mocksite.BehaviorResponseLostAfterApply, 0x31,
		)
		defer fixture.close()
		status, err := fixture.coordinator.Start(
			context.Background(), fixture.request, fixture.namespaceID,
			fixture.descriptorHash,
		)
		if err != nil || status != AttemptSiteConfirmPending ||
			fixture.store.current.ReceiptStatus == nil ||
			*fixture.store.current.ReceiptStatus != sitedomain.ReceiptApplied {
			t.Fatalf("lost response recovery status=%d error=%v", status, err)
		}
	})
	t.Run("timeout-unknown-needs-user", func(t *testing.T) {
		t.Parallel()
		fixture := newChangeFixture(
			t, mocksite.BehaviorTimeoutUnknown, 0x41,
		)
		defer fixture.close()
		status, err := fixture.coordinator.Start(
			context.Background(), fixture.request, fixture.namespaceID,
			fixture.descriptorHash,
		)
		if err != nil || status != AttemptSiteStatusUnknown {
			t.Fatalf("unknown status=%d error=%v", status, err)
		}
		if err := fixture.coordinator.Confirm(
			context.Background(), fixture.request.ChangeID,
			protocol.EvidenceSiteSignedReceipt,
		); !errors.Is(err, ErrConfirmationRequired) {
			t.Fatalf("unknown site confirmation error=%v", err)
		}
		if err := fixture.coordinator.Confirm(
			context.Background(), fixture.request.ChangeID,
			protocol.EvidenceUserSignedConfirmation,
		); err != nil {
			t.Fatal(err)
		}
		if fixture.store.current.Status != AttemptActive {
			t.Fatal("signed user review did not activate unknown outcome")
		}
	})
}

func TestCoordinatorMapsNegativeReceiptsToRetryableWithoutActivation(t *testing.T) {
	t.Parallel()
	for index, behavior := range []mocksite.Behavior{
		mocksite.BehaviorRejected,
		mocksite.BehaviorMFARequired,
		mocksite.BehaviorPolicyRejected,
	} {
		behavior := behavior
		t.Run(string(rune('a'+index)), func(t *testing.T) {
			t.Parallel()
			fixture := newChangeFixture(t, behavior, byte(0x51+index))
			defer fixture.close()
			status, err := fixture.coordinator.Start(
				context.Background(), fixture.request, fixture.namespaceID,
				fixture.descriptorHash,
			)
			if err != nil || status != AttemptFailedRetryable ||
				fixture.store.current.Status == AttemptActive {
				t.Fatalf("negative status=%d error=%v", status, err)
			}
		})
	}
}

type changeFixture struct {
	coordinator    *Coordinator
	connector      *mocksite.Connector
	store          *memoryAttemptStore
	authorizer     *testConfirmationAuthorizer
	request        sitedomain.ChangeRequest
	namespaceID    protocol.NamespaceID
	descriptorHash [sha256.Size]byte
	current        *cryptokit.Secret
	replacement    *cryptokit.Secret
}

func newChangeFixture(
	t *testing.T,
	behavior mocksite.Behavior,
	marker byte,
) *changeFixture {
	t.Helper()
	privateKey := ed25519.NewKeyFromSeed(
		bytes.Repeat([]byte{0x61}, ed25519.SeedSize),
	)
	policyHash := sha256.Sum256([]byte("required-policy"))
	connector, err := mocksite.New(mocksite.Config{
		ReceiptPrivateKey: privateKey, Behavior: behavior,
		RequiredPolicyHash: policyHash,
	})
	if err != nil {
		t.Fatal(err)
	}
	var credentialID protocol.CredentialID
	copy(credentialID[:], bytes.Repeat([]byte{marker}, len(credentialID)))
	current, _ := cryptokit.NewSecret([]byte("current-password"))
	replacement, _ := cryptokit.NewSecret([]byte("replacement-password"))
	if err := connector.SeedCredential(credentialID, 1, current); err != nil {
		t.Fatal(err)
	}
	var changeID sitedomain.ChangeID
	copy(changeID[:], bytes.Repeat([]byte{marker + 1}, len(changeID)))
	var namespaceID protocol.NamespaceID
	copy(namespaceID[:], bytes.Repeat([]byte{marker + 2}, len(namespaceID)))
	store := &memoryAttemptStore{}
	authorizer := &testConfirmationAuthorizer{}
	coordinator, err := NewCoordinator(connector, store, authorizer)
	if err != nil {
		t.Fatal(err)
	}
	return &changeFixture{
		coordinator: coordinator, connector: connector,
		store: store, authorizer: authorizer,
		request: sitedomain.ChangeRequest{
			ChangeID: changeID, CredentialID: credentialID,
			ExpectedVersion: 1, NewVersion: 2, PolicyHash: policyHash,
			CurrentPassword: current, NewPassword: replacement,
		},
		namespaceID:    namespaceID,
		descriptorHash: sha256.Sum256([]byte{marker, 0xdd}),
		current:        current, replacement: replacement,
	}
}

func (fixture *changeFixture) close() {
	fixture.connector.Close()
	fixture.current.Destroy()
	fixture.replacement.Destroy()
}

type memoryAttemptStore struct {
	mu      sync.Mutex
	current ChangeAttempt
	created bool
}

func (store *memoryAttemptStore) Create(
	_ context.Context,
	attempt ChangeAttempt,
) error {
	store.mu.Lock()
	defer store.mu.Unlock()
	if store.created || attempt.Status != AttemptCandidateDurable {
		return ErrChangeTransition
	}
	store.current = attempt
	store.created = true
	return nil
}

func (store *memoryAttemptStore) Load(
	_ context.Context,
	changeID sitedomain.ChangeID,
) (ChangeAttempt, error) {
	store.mu.Lock()
	defer store.mu.Unlock()
	if !store.created || store.current.ChangeID != changeID {
		return ChangeAttempt{}, ErrInvalidChangeFlow
	}
	return store.current, nil
}

func (store *memoryAttemptStore) Transition(
	_ context.Context,
	changeID sitedomain.ChangeID,
	expected AttemptStatus,
	next AttemptStatus,
	receipt *sitedomain.SignedReceipt,
	evidence *protocol.EvidenceLevel,
	eventID *protocol.EventID,
) error {
	store.mu.Lock()
	defer store.mu.Unlock()
	if !store.created || store.current.ChangeID != changeID ||
		store.current.Status != expected || !expected.CanTransitionTo(next) {
		return ErrChangeTransition
	}
	store.current.Status = next
	if receipt != nil {
		status := receipt.Payload().Status
		digest := receipt.Digest()
		store.current.ReceiptStatus = &status
		store.current.ReceiptDigest = &digest
	}
	if evidence != nil {
		value := *evidence
		store.current.Evidence = &value
	}
	if eventID != nil {
		value := *eventID
		store.current.ConfirmationEventID = &value
	}
	return nil
}

type testConfirmationAuthorizer struct {
	calls int
	err   error
}

func (authorizer *testConfirmationAuthorizer) AuthorizeConfirmation(
	_ context.Context,
	attempt ChangeAttempt,
	_ protocol.EvidenceLevel,
) (protocol.EventID, error) {
	authorizer.calls++
	if authorizer.err != nil {
		return protocol.EventID{}, authorizer.err
	}
	var eventID protocol.EventID
	copy(eventID[:], attempt.ChangeID[:])
	eventID[0] ^= 0xff
	return eventID, nil
}
