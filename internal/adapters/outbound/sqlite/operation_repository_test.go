//go:build linux

package sqlite

import (
	"bytes"
	"context"
	"crypto/ed25519"
	"crypto/sha256"
	"errors"
	"path/filepath"
	"testing"

	"vpass.local/vpass/internal/adapters/outbound/objectfs"
	"vpass.local/vpass/internal/cryptokit"
	operation "vpass.local/vpass/internal/operation/domain"
	"vpass.local/vpass/internal/protocol"
)

func TestOperationRepositoryRetryReturnsFirstPersistedCiphertext(t *testing.T) {
	t.Parallel()
	ctx := context.Background()
	fixture := newOperationFixture(t)

	first := fixture.sealAndSign(t, fixture.eventID, 1, nil, []byte("same logical usage payload"))
	firstResult, err := fixture.repository.CommitEvent(ctx, first.request)
	if err != nil {
		t.Fatal(err)
	}
	if !firstResult.Created || firstResult.PublicationState != "OBJECT_STORED" {
		t.Fatalf("first result = %+v", firstResult)
	}

	// A caller that incorrectly reseals the same EventID gets a different GCM
	// object. The repository must ignore that candidate and return the exact
	// first durable retry material.
	second := fixture.sealAndSign(t, fixture.eventID, 1, nil, []byte("same logical usage payload"))
	if second.request.Object.Reference == first.request.Object.Reference {
		t.Fatal("independent GCM seals unexpectedly produced the same object")
	}
	secondResult, err := fixture.repository.CommitEvent(ctx, second.request)
	if err != nil {
		t.Fatal(err)
	}
	if secondResult.Created || secondResult.ObjectReference != firstResult.ObjectReference ||
		!bytes.Equal(secondResult.SigInputCBOR, firstResult.SigInputCBOR) ||
		secondResult.DeviceSignature != firstResult.DeviceSignature ||
		secondResult.EventDigest != firstResult.EventDigest {
		t.Fatal("retry did not return the exact first persisted event and object")
	}

	assertScalar(t, fixture.database, "SELECT count(*) FROM operation_events", 1)
	assertScalar(t, fixture.database, "SELECT count(*) FROM event_publication_outbox", 1)
	assertScalar(t, fixture.database, "SELECT count(*) FROM content_objects", 1)
	assertScalar(t, fixture.database, "SELECT last_accepted_counter FROM devices", 1)
}

func TestOperationRepositoryRejectsIDCounterAndChainConflictsAtomically(t *testing.T) {
	t.Parallel()
	ctx := context.Background()
	fixture := newOperationFixture(t)
	first := fixture.sealAndSign(t, fixture.eventID, 1, nil, []byte("event one"))
	firstResult, err := fixture.repository.CommitEvent(ctx, first.request)
	if err != nil {
		t.Fatal(err)
	}

	differentProjection := first.request
	payload := differentProjection.Event.Payload()
	payload.OperationType = protocol.OperationExposureAnalyze
	differentProjection.Event, err = operation.Sign(fixture.devicePrivateKey, fixture.chainID, 1, payload)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := fixture.repository.CommitEvent(ctx, differentProjection); !errors.Is(err, ErrEventIDConflict) {
		t.Fatalf("EventID projection conflict error = %v", err)
	}

	newEventID := fixture.eventID
	newEventID[0] ^= 0x7f
	replayedCounter := fixture.sealAndSign(t, newEventID, 1, nil, []byte("counter replay"))
	if _, err := fixture.repository.CommitEvent(ctx, replayedCounter.request); !errors.Is(err, &CounterConflictError{}) {
		t.Fatalf("counter conflict error = %v", err)
	}

	wrongPrevious := sha256.Sum256([]byte("wrong previous event"))
	secondEventID := fixture.eventID
	secondEventID[1] ^= 0x55
	brokenChain := fixture.sealAndSign(t, secondEventID, 2, &wrongPrevious, []byte("event two"))
	if _, err := fixture.repository.CommitEvent(ctx, brokenChain.request); !errors.Is(err, ErrPreviousEventMismatch) {
		t.Fatalf("previous digest error = %v", err)
	}

	validChain := fixture.sealAndSign(t, secondEventID, 2, &firstResult.EventDigest, []byte("event two"))
	if _, err := fixture.repository.CommitEvent(ctx, validChain.request); err != nil {
		t.Fatalf("valid chained event: %v", err)
	}
	assertScalar(t, fixture.database, "SELECT count(*) FROM operation_events", 2)
	assertScalar(t, fixture.database, "SELECT count(*) FROM event_publication_outbox", 2)
	assertScalar(t, fixture.database, "SELECT count(*) FROM content_objects", 2)
	assertScalar(t, fixture.database, "SELECT last_accepted_counter FROM devices", 2)
}

type operationFixture struct {
	database         *Database
	repository       *OperationRepository
	objectStore      *objectfs.Store
	chainID          string
	namespaceID      protocol.NamespaceID
	deviceID         protocol.DeviceID
	credentialID     protocol.CredentialID
	credentialHash   [sha256.Size]byte
	devicePrivateKey ed25519.PrivateKey
	eventKey         *cryptokit.Key
	eventID          protocol.EventID
	pseudonym        [cryptokit.DevicePseudonymSize]byte
}

type sealedOperation struct {
	request CommitEventRequest
}

func newOperationFixture(t *testing.T) *operationFixture {
	t.Helper()
	ctx := context.Background()
	database := openTestDatabase(t)
	repository, err := NewOperationRepository(database)
	if err != nil {
		t.Fatal(err)
	}
	objectStore, err := objectfs.New(filepath.Join(t.TempDir(), "data"))
	if err != nil {
		t.Fatal(err)
	}

	fixture := &operationFixture{
		database:         database,
		repository:       repository,
		objectStore:      objectStore,
		chainID:          "vpass-integration-chain",
		credentialHash:   sha256.Sum256([]byte("device operation credential")),
		devicePrivateKey: ed25519.NewKeyFromSeed(bytes.Repeat([]byte{0x61}, ed25519.SeedSize)),
		pseudonym:        [cryptokit.DevicePseudonymSize]byte{1, 3, 3, 7},
	}
	copy(fixture.namespaceID[:], bytes.Repeat([]byte{0x11}, len(fixture.namespaceID)))
	copy(fixture.deviceID[:], bytes.Repeat([]byte{0x22}, len(fixture.deviceID)))
	copy(fixture.credentialID[:], bytes.Repeat([]byte{0x33}, len(fixture.credentialID)))
	copy(fixture.eventID[:], bytes.Repeat([]byte{0x44}, len(fixture.eventID)))
	fixture.seedIdentity(t, ctx)
	fixture.eventKey = fixture.deriveEventKey(t)
	t.Cleanup(fixture.eventKey.Destroy)
	return fixture
}

func (fixture *operationFixture) seedIdentity(t *testing.T, ctx context.Context) {
	t.Helper()
	rootPrivate := ed25519.NewKeyFromSeed(bytes.Repeat([]byte{0x51}, ed25519.SeedSize))
	rootPublic := rootPrivate.Public().(ed25519.PublicKey)
	rootKeyID, err := protocol.KeyIDFromPublicKey(rootPublic)
	if err != nil {
		t.Fatal(err)
	}
	devicePublic := fixture.devicePrivateKey.Public().(ed25519.PublicKey)
	hpkePublic := bytes.Repeat([]byte{0x77}, 32)
	createdAt := int64(1_700_000_000_000)

	statements := []struct {
		query string
		args  []any
	}{
		{
			`INSERT INTO namespaces (
  namespace_id, protocol_version, suite_id, chain_id, root_signing_public_key,
  root_key_id, current_secret_generation, status, created_at_ms, updated_at_ms
) VALUES (?, ?, ?, ?, ?, ?, 1, 'ACTIVE', ?, ?)`,
			[]any{fixture.namespaceID[:], protocol.ProtocolVersion, protocol.SuiteID, fixture.chainID, rootPublic, rootKeyID[:], createdAt, createdAt},
		},
		{
			`INSERT INTO namespace_key_generations (
  namespace_id, generation, secure_store_ref, status, created_at_ms
) VALUES (?, 1, 'test://namespace/root-generation-1', 'ACTIVE', ?)`,
			[]any{fixture.namespaceID[:], createdAt},
		},
		{
			`INSERT INTO devices (
  device_id, namespace_id, signing_public_key, hpke_public_key,
  current_key_generation, status, last_accepted_counter,
  current_credential_hash, created_at_ms, updated_at_ms
) VALUES (?, ?, ?, ?, 1, 'ACTIVE', 0, ?, ?, ?)`,
			[]any{fixture.deviceID[:], fixture.namespaceID[:], devicePublic, hpkePublic, fixture.credentialHash[:], createdAt, createdAt},
		},
		{
			`INSERT INTO device_key_generations (
  device_id, key_generation, signing_public_key, hpke_public_key,
  signing_secret_ref, hpke_secret_ref, status, created_at_ms
) VALUES (?, 1, ?, ?, 'test://device/signing-1', 'test://device/hpke-1', 'ACTIVE', ?)`,
			[]any{fixture.deviceID[:], devicePublic, hpkePublic, createdAt},
		},
		{
			`INSERT INTO device_operation_credentials (
  credential_hash, namespace_id, device_id, credential_cbor, scope_kind,
  valid_from_ms, valid_until_ms, secret_generation, status_reference_hash,
  issuer_key_id, root_signature, issued_at_ms
) VALUES (?, ?, ?, x'a0', 'NAMESPACE', ?, ?, 1, ?, ?, zeroblob(64), ?)`,
			[]any{
				fixture.credentialHash[:], fixture.namespaceID[:], fixture.deviceID[:], createdAt - 1,
				createdAt + 1_000_000, sha256Bytes("status reference"), rootKeyID[:], createdAt,
			},
		},
		{
			`INSERT INTO credentials (
  credential_id, namespace_id, aggregate_status, origin_commitment,
  created_at_ms, updated_at_ms
) VALUES (?, ?, 'ACTIVE', ?, ?, ?)`,
			[]any{fixture.credentialID[:], fixture.namespaceID[:], sha256Bytes("origin commitment"), createdAt, createdAt},
		},
	}
	for _, statement := range statements {
		if _, err := fixture.database.ExecContext(ctx, statement.query, statement.args...); err != nil {
			t.Fatal(err)
		}
	}
}

func (fixture *operationFixture) deriveEventKey(t *testing.T) *cryptokit.Key {
	t.Helper()
	root, err := cryptokit.NewSecret(bytes.Repeat([]byte{0x91}, cryptokit.KeySize))
	if err != nil {
		t.Fatal(err)
	}
	defer root.Destroy()
	prk, err := cryptokit.ExtractNamespacePRK(root, fixture.namespaceID, 1)
	if err != nil {
		t.Fatal(err)
	}
	defer prk.Destroy()
	keys, err := cryptokit.DeriveNamespaceKeys(prk)
	if err != nil {
		t.Fatal(err)
	}
	defer keys.Destroy()
	auditKey, err := cryptokit.DeriveAuditKey(keys.Audit, fixture.chainID, fixture.namespaceID, 1, 7, []byte("verified beacon"))
	if err != nil {
		t.Fatal(err)
	}
	defer auditKey.Destroy()
	eventKey, err := cryptokit.DeriveEventKey(auditKey, fixture.eventID, fixture.pseudonym)
	if err != nil {
		t.Fatal(err)
	}
	return eventKey
}

func (fixture *operationFixture) sealAndSign(
	t *testing.T,
	eventID protocol.EventID,
	counter uint64,
	previous *[sha256.Size]byte,
	plaintextBytes []byte,
) sealedOperation {
	t.Helper()
	// Each EventID has a distinct derived key. The fixture's first fixed key is
	// reused only for its original ID; derive another key for subsequent IDs.
	eventKey := fixture.eventKey
	if eventID != fixture.eventID {
		root, err := cryptokit.NewSecret(bytes.Repeat([]byte{0x91}, cryptokit.KeySize))
		if err != nil {
			t.Fatal(err)
		}
		defer root.Destroy()
		prk, err := cryptokit.ExtractNamespacePRK(root, fixture.namespaceID, 1)
		if err != nil {
			t.Fatal(err)
		}
		defer prk.Destroy()
		keys, err := cryptokit.DeriveNamespaceKeys(prk)
		if err != nil {
			t.Fatal(err)
		}
		defer keys.Destroy()
		auditKey, err := cryptokit.DeriveAuditKey(keys.Audit, fixture.chainID, fixture.namespaceID, 1, 7, []byte("verified beacon"))
		if err != nil {
			t.Fatal(err)
		}
		defer auditKey.Destroy()
		eventKey, err = cryptokit.DeriveEventKey(auditKey, eventID, fixture.pseudonym)
		if err != nil {
			t.Fatal(err)
		}
		defer eventKey.Destroy()
	}
	plaintext, err := cryptokit.NewSecret(plaintextBytes)
	if err != nil {
		t.Fatal(err)
	}
	defer plaintext.Destroy()
	epoch := uint64(7)
	envelope, err := cryptokit.SealEvent(eventKey, cryptokit.EventContext{
		NamespaceID:     fixture.namespaceID,
		EventID:         eventID,
		ObjectType:      protocol.ObjectTypeOperationEvent,
		DevicePseudonym: fixture.pseudonym,
		KeyGeneration:   1,
		VRFEpoch:        epoch,
	}, plaintext)
	if err != nil {
		t.Fatal(err)
	}
	objectBytes, err := envelope.MarshalBinary()
	if err != nil {
		t.Fatal(err)
	}
	reference, err := fixture.objectStore.PutIfAbsent(context.Background(), objectBytes)
	clear(objectBytes)
	if err != nil {
		t.Fatal(err)
	}
	relativePath, err := fixture.objectStore.RelativePath(reference)
	if err != nil {
		t.Fatal(err)
	}
	observed := uint64(1_700_000_000_123)
	payload := operation.Payload{
		EventID:                eventID,
		NamespaceID:            fixture.namespaceID,
		DeviceID:               fixture.deviceID,
		DeviceCredentialHash:   fixture.credentialHash,
		CredentialID:           &fixture.credentialID,
		OperationType:          protocol.OperationUseObserved,
		DevicePseudonym:        fixture.pseudonym,
		OriginCommitment:       pointerToHash(sha256.Sum256([]byte("origin commitment"))),
		EventPayloadHash:       envelope.PayloadHash(),
		VRFEpoch:               &epoch,
		SecretGeneration:       1,
		DeviceCounter:          counter,
		PreviousEventHash:      previous,
		ObservedAtMilliseconds: &observed,
	}
	event, err := operation.Sign(fixture.devicePrivateKey, fixture.chainID, 1, payload)
	if err != nil {
		t.Fatal(err)
	}
	return sealedOperation{request: CommitEventRequest{
		Event: event,
		Object: EventObject{
			Reference:           reference,
			StorageRelativePath: relativePath,
			KeyGeneration:       1,
		},
		CreatedAtMilliseconds: 1_700_000_000_500 + counter,
	}}
}

func sha256Bytes(value string) []byte {
	digest := sha256.Sum256([]byte(value))
	return digest[:]
}

func pointerToHash(value [sha256.Size]byte) *[sha256.Size]byte { return &value }
