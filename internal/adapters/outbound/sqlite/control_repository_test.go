//go:build linux

package sqlite

import (
	"bytes"
	"context"
	"crypto/ed25519"
	"crypto/sha256"
	"errors"
	"sync"
	"testing"

	credential "vdns.local/vdns/internal/credential/domain"
	"vdns.local/vdns/internal/cryptokit"
	"vdns.local/vdns/internal/protocol"
)

func TestCredentialControlRepositoryAcceptLoadAndIdempotentReplay(t *testing.T) {
	t.Parallel()
	ctx := context.Background()
	fixture := newControlFixture(t)
	accepted, err := fixture.repository.Accept(ctx, fixture.request)
	if err != nil {
		t.Fatal(err)
	}
	if accepted.AcceptedVersion != 1 ||
		accepted.Envelope.Digest() != fixture.envelope.Digest() ||
		accepted.DescriptorHash != fixture.descriptor.Digest() {
		t.Fatal("accepted state projection mismatch")
	}
	replayed, err := fixture.repository.Accept(ctx, fixture.request)
	if err != nil || replayed.DescriptorHash != accepted.DescriptorHash {
		t.Fatalf("idempotent replay = %+v, %v", replayed, err)
	}
	loaded, err := fixture.repository.LoadAccepted(
		ctx, fixture.identity.namespaceID, fixture.identity.credentialID,
	)
	if err != nil {
		t.Fatal(err)
	}
	if loaded.AcceptedVersion != 1 || loaded.UpdatedSequence != 7 ||
		loaded.Envelope.Digest() != fixture.envelope.Digest() ||
		loaded.DescriptorHash != fixture.descriptor.Digest() {
		t.Fatal("loaded accepted state mismatch")
	}
	keyID, _ := protocol.KeyIDFromPublicKey(
		fixture.identity.devicePrivateKey.Public().(ed25519.PublicKey),
	)
	expected := protocol.VerificationContext{
		ObjectType: protocol.ObjectTypeStateDescriptor,
		ChainID:    fixture.identity.chainID, NamespaceID: fixture.identity.namespaceID,
		KeyID: keyID, KeyGeneration: 1,
	}
	verified, err := credential.ParseAndVerifyStateDescriptor(
		loaded.DescriptorSigInput, loaded.DescriptorSignature,
		fixture.identity.devicePrivateKey.Public().(ed25519.PublicKey), expected,
	)
	if err != nil || verified.Digest() != loaded.DescriptorHash {
		t.Fatalf("loaded descriptor verification = %v", err)
	}
	assertScalar(t, fixture.identity.database, "SELECT count(*) FROM credential_envelopes_v2", 1)
	assertScalar(t, fixture.identity.database, "SELECT count(*) FROM state_descriptors_v2", 1)
	assertScalar(t, fixture.identity.database, "SELECT count(*) FROM credential_acceptance_v2", 1)
	assertScalar(
		t,
		fixture.identity.database,
		"SELECT current_accepted_version FROM credentials WHERE credential_id = x'"+
			hexID(fixture.identity.credentialID[:])+"'",
		1,
	)
}

func TestCredentialControlRepositoryCASAllowsOneConcurrentTransition(t *testing.T) {
	t.Parallel()
	ctx := context.Background()
	fixture := newControlFixture(t)
	initial, err := fixture.repository.Accept(ctx, fixture.request)
	if err != nil {
		t.Fatal(err)
	}
	version := uint64(1)
	previous := initial.DescriptorHash
	requests := make([]AcceptCredentialStateRequest, 2)
	for index := range requests {
		payload := fixture.descriptor.Payload()
		payload.PreviousDescriptorHash = &previous
		payload.FinalSequence = uint64(8 + index)
		payload.AuditCheckpoint = sha256.Sum256([]byte{byte(0x80 + index)})
		if index == 1 {
			payload.LifecycleStatus = protocol.LifecycleSuspended
		}
		descriptor, signErr := credential.SignStateDescriptor(
			fixture.identity.devicePrivateKey, fixture.identity.chainID, 1, payload,
		)
		if signErr != nil {
			t.Fatal(signErr)
		}
		requests[index] = AcceptCredentialStateRequest{
			NamespaceID: fixture.identity.namespaceID,
			Envelope:    fixture.envelope, Descriptor: descriptor,
			ExpectedAcceptedVersion: &version, ExpectedDescriptorHash: &previous,
			CreatedAtMilliseconds: uint64(1_700_000_003_000 + index),
		}
	}

	results := make([]error, len(requests))
	var wait sync.WaitGroup
	for index := range requests {
		index := index
		wait.Add(1)
		go func() {
			defer wait.Done()
			_, results[index] = fixture.repository.Accept(ctx, requests[index])
		}()
	}
	wait.Wait()
	successes, conflicts := 0, 0
	for _, result := range results {
		switch {
		case result == nil:
			successes++
		case errors.Is(result, &ControlCASConflictError{}):
			conflicts++
		default:
			t.Fatalf("unexpected concurrent result: %v", result)
		}
	}
	if successes != 1 || conflicts != 1 {
		t.Fatalf("concurrent transition results: success=%d conflict=%d", successes, conflicts)
	}
	assertScalar(t, fixture.identity.database, "SELECT count(*) FROM credential_envelopes_v2", 1)
	assertScalar(t, fixture.identity.database, "SELECT count(*) FROM state_descriptors_v2", 2)
	assertScalar(t, fixture.identity.database, "SELECT count(*) FROM credential_acceptance_v2", 1)
	assertScalar(
		t,
		fixture.identity.database,
		"SELECT current_accepted_version FROM credentials WHERE credential_id = x'"+
			hexID(fixture.identity.credentialID[:])+"'",
		1,
	)
}

func TestCredentialControlRepositoryRollbackAndTamperDetection(t *testing.T) {
	t.Parallel()
	ctx := context.Background()
	fixture := newControlFixture(t)
	if _, err := fixture.identity.database.ExecContext(
		ctx,
		`CREATE TRIGGER fail_control_accept
 BEFORE INSERT ON credential_acceptance_v2
 BEGIN
   SELECT RAISE(ABORT, 'injected acceptance failure');
 END`,
	); err != nil {
		t.Fatal(err)
	}
	if _, err := fixture.repository.Accept(ctx, fixture.request); err == nil {
		t.Fatal("injected acceptance failure was ignored")
	}
	assertScalar(t, fixture.identity.database, "SELECT count(*) FROM credential_envelopes_v2", 0)
	assertScalar(t, fixture.identity.database, "SELECT count(*) FROM state_descriptors_v2", 0)
	assertScalar(t, fixture.identity.database, "SELECT count(*) FROM credential_acceptance_v2", 0)
	assertScalar(t, fixture.identity.database, "SELECT count(current_accepted_version) FROM credentials", 0)
	if _, err := fixture.identity.database.ExecContext(
		ctx, "DROP TRIGGER fail_control_accept",
	); err != nil {
		t.Fatal(err)
	}
	if _, err := fixture.repository.Accept(ctx, fixture.request); err != nil {
		t.Fatal(err)
	}
	if _, err := fixture.identity.database.ExecContext(
		ctx,
		"UPDATE credential_envelopes_v2 SET envelope_cbor = X'A0'",
	); err != nil {
		t.Fatal(err)
	}
	if _, err := fixture.repository.LoadAccepted(
		ctx, fixture.identity.namespaceID, fixture.identity.credentialID,
	); !errors.Is(err, ErrControlCorrupt) {
		t.Fatalf("tampered envelope error = %v", err)
	}
}

type controlFixture struct {
	identity   *operationFixture
	repository *CredentialControlRepository
	envelope   *credential.CredentialEnvelope
	descriptor *credential.SignedStateDescriptor
	request    AcceptCredentialStateRequest
}

func newControlFixture(t *testing.T) *controlFixture {
	t.Helper()
	ctx := context.Background()
	identity := newOperationFixture(t)
	// newOperationFixture seeds an unrelated credential for event FK tests.
	// The control fixture creates its own aggregate through CredentialRepository.
	identity.credentialID[0] ^= 0x6a
	credentialRepository, err := NewCredentialRepository(identity.database)
	if err != nil {
		t.Fatal(err)
	}
	fieldRoot := credentialFieldRoot(t, identity.namespaceID)
	username, usernamePath := storedCredentialField(
		t, identity, fieldRoot, identity.credentialID, 1,
		cryptokit.FieldUsername, "alice@example.test",
	)
	password, passwordPath := storedCredentialField(
		t, identity, fieldRoot, identity.credentialID, 1,
		cryptokit.FieldPassword, "password-v1",
	)
	policyHash := sha256.Sum256([]byte("test-policy"))
	draft, err := credential.NewVersionDraft(
		identity.credentialID, 1, 1, credential.VersionActive, nil,
		policyHash, []credential.FieldMapping{password, username},
	)
	if err != nil {
		t.Fatal(err)
	}
	commit := storedCredentialRequest(
		t, identity, draft, identity.namespaceID,
		sha256.Sum256([]byte("origin commitment")), nil,
		map[cryptokit.FieldType]string{
			cryptokit.FieldUsername: usernamePath,
			cryptokit.FieldPassword: passwordPath,
		},
		true, false, 1_700_000_002_000,
	)
	if _, err := credentialRepository.CommitVersion(ctx, commit); err != nil {
		t.Fatal(err)
	}
	originBinding := sha256.Sum256([]byte("test-origin-binding"))
	envelope, err := credential.NewCredentialEnvelope(identity.namespaceID, draft, originBinding)
	if err != nil {
		t.Fatal(err)
	}
	payload := credential.StateDescriptorPayload{
		NamespaceID: identity.namespaceID, CredentialID: identity.credentialID,
		ActiveVersion: 1, ActiveEnvelopeHash: envelope.Digest(),
		LifecycleStatus:      protocol.LifecycleActive,
		LastOperationEvent:   sha256.Sum256([]byte("create-event")),
		AuthorizedDeviceRoot: sha256.Sum256([]byte("authorized-devices")),
		AuditCheckpoint:      sha256.Sum256([]byte("audit-checkpoint")),
		FinalSequence:        7, UpdaterDeviceID: identity.deviceID,
	}
	descriptor, err := credential.SignStateDescriptor(
		identity.devicePrivateKey, identity.chainID, 1, payload,
	)
	if err != nil {
		t.Fatal(err)
	}
	repository, err := NewCredentialControlRepository(identity.database)
	if err != nil {
		t.Fatal(err)
	}
	return &controlFixture{
		identity: identity, repository: repository,
		envelope: envelope, descriptor: descriptor,
		request: AcceptCredentialStateRequest{
			NamespaceID: identity.namespaceID, Envelope: envelope,
			Descriptor: descriptor, CreatedAtMilliseconds: 1_700_000_002_100,
		},
	}
}

func TestCredentialControlRepositoryRejectsMismatchedEnvelope(t *testing.T) {
	t.Parallel()
	fixture := newControlFixture(t)
	payload := fixture.descriptor.Payload()
	payload.ActiveEnvelopeHash = sha256.Sum256(bytes.Repeat([]byte{0x55}, 2))
	descriptor, err := credential.SignStateDescriptor(
		fixture.identity.devicePrivateKey, fixture.identity.chainID, 1, payload,
	)
	if err != nil {
		t.Fatal(err)
	}
	request := fixture.request
	request.Descriptor = descriptor
	if _, err := fixture.repository.Accept(
		context.Background(), request,
	); !errors.Is(err, ErrInvalidControlCommit) {
		t.Fatalf("mismatched descriptor error = %v", err)
	}
}
