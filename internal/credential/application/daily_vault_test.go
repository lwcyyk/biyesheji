//go:build linux

package application

import (
	"bytes"
	"context"
	"crypto/ed25519"
	"crypto/sha256"
	"errors"
	"fmt"
	"path/filepath"
	"testing"
	"time"

	"vpass.local/vpass/internal/adapters/outbound/objectfs"
	"vpass.local/vpass/internal/adapters/outbound/sqlite"
	credential "vpass.local/vpass/internal/credential/domain"
	"vpass.local/vpass/internal/cryptokit"
	operation "vpass.local/vpass/internal/operation/domain"
	password "vpass.local/vpass/internal/password/domain"
	"vpass.local/vpass/internal/platform"
	"vpass.local/vpass/internal/protocol"
)

func TestDailyVaultCreateReadAndAtomicDuplicateRollback(t *testing.T) {
	t.Parallel()
	fixture := newDailyVaultFixture(t)
	ctx := context.Background()
	request := fixture.createRequest()
	created, err := fixture.service.CreateCredential(ctx, request)
	if err != nil {
		t.Fatal(err)
	}
	if created.Version != 1 || bytesAllZero(created.CredentialID[:]) ||
		bytesAllZero(created.EnvelopeHash[:]) || bytesAllZero(created.DescriptorHash[:]) ||
		bytesAllZero(created.PasswordHandle[:]) {
		t.Fatalf("create result = %+v", created)
	}
	origin, _ := credential.NormalizeOrigin(request.Origin)
	defer origin.Destroy()
	lookup, err := fixture.session.BuildRouteLookup(
		request.Now, origin, request.AccountID,
	)
	if err != nil {
		t.Fatal(err)
	}
	createdSecret, err := fixture.session.ConsumeSecretHandle(
		request.Now, created.PasswordHandle,
		credential.SecretHandleContext{
			InstallationID: request.InstallationID,
			OriginBinding:  lookup.OriginBinding,
			CredentialID:   created.CredentialID,
			FieldType:      cryptokit.FieldPassword,
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	if createdSecret.Len() != 20 {
		t.Fatalf("generated password length = %d", createdSecret.Len())
	}
	createdSecret.Destroy()

	read, err := fixture.service.ReadCredential(ctx, ReadCredentialRequest{
		Now: request.Now.Add(time.Second), Origin: request.Origin,
		AccountID: request.AccountID, InstallationID: request.InstallationID,
		HandleTTL: 30 * time.Second,
	})
	if err != nil {
		t.Fatal(err)
	}
	if read.CredentialID != created.CredentialID || read.Version != 1 {
		t.Fatalf("read result = %+v", read)
	}
	readSecret, err := fixture.session.ConsumeSecretHandle(
		request.Now.Add(time.Second), read.Handle,
		credential.SecretHandleContext{
			InstallationID: request.InstallationID,
			OriginBinding:  lookup.OriginBinding,
			CredentialID:   created.CredentialID,
			FieldType:      cryptokit.FieldPassword,
		},
	)
	if err != nil || readSecret.Len() != 20 {
		t.Fatalf("read handle secret = %v, %v", readSecret, err)
	}
	readSecret.Destroy()

	assertApplicationScalar(t, fixture.database, "SELECT count(*) FROM credentials", 1)
	assertApplicationScalar(t, fixture.database, "SELECT count(*) FROM credential_versions", 1)
	assertApplicationScalar(t, fixture.database, "SELECT count(*) FROM route_entries", 1)
	assertApplicationScalar(t, fixture.database, "SELECT count(*) FROM operation_events", 1)
	assertApplicationScalar(t, fixture.database, "SELECT count(*) FROM event_publication_outbox", 1)
	assertApplicationScalar(t, fixture.database, "SELECT count(*) FROM credential_acceptance_v2", 1)
	assertApplicationScalar(t, fixture.database, "SELECT last_accepted_counter FROM devices", 1)

	duplicate := request
	duplicate.Now = request.Now.Add(2 * time.Second)
	duplicate.DeviceCounter = 2
	duplicate.FinalSequence = 2
	duplicate.PreviousEventHash = &fixture.signer.lastOperation
	if _, err := fixture.service.CreateCredential(ctx, duplicate); !errors.Is(err, sqlite.ErrRouteConflict) {
		t.Fatalf("duplicate route create error = %v", err)
	}
	// The duplicate's immutable ciphertext files may be GC candidates, but no
	// database pointer, event or counter can escape the failed transaction.
	assertApplicationScalar(t, fixture.database, "SELECT count(*) FROM credentials", 1)
	assertApplicationScalar(t, fixture.database, "SELECT count(*) FROM credential_versions", 1)
	assertApplicationScalar(t, fixture.database, "SELECT count(*) FROM operation_events", 1)
	assertApplicationScalar(t, fixture.database, "SELECT last_accepted_counter FROM devices", 1)
}

func TestDailyVaultReadFailsClosedOnDescriptorAndObjectTamper(t *testing.T) {
	t.Parallel()
	fixture := newDailyVaultFixture(t)
	ctx := context.Background()
	request := fixture.createRequest()
	created, err := fixture.service.CreateCredential(ctx, request)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := fixture.database.ExecContext(
		ctx,
		"UPDATE state_descriptors_v2 SET updater_signature = zeroblob(64)",
	); err != nil {
		t.Fatal(err)
	}
	if _, err := fixture.service.ReadCredential(ctx, ReadCredentialRequest{
		Now: request.Now.Add(time.Second), Origin: request.Origin,
		AccountID: request.AccountID, InstallationID: request.InstallationID,
		HandleTTL: time.Second,
	}); err == nil {
		t.Fatal("tampered descriptor was accepted")
	}
	if _, err := fixture.database.ExecContext(
		ctx,
		"UPDATE state_descriptors_v2 SET updater_signature = ? WHERE descriptor_hash = ?",
		fixture.signer.lastState[:], created.DescriptorHash[:],
	); err != nil {
		t.Fatal(err)
	}
	fixture.service.objectStore = &corruptReadStore{inner: fixture.objectStore}
	if _, err := fixture.service.ReadCredential(ctx, ReadCredentialRequest{
		Now: request.Now.Add(2 * time.Second), Origin: request.Origin,
		AccountID: request.AccountID, InstallationID: request.InstallationID,
		HandleTTL: time.Second,
	}); err == nil {
		t.Fatal("tampered field object was accepted")
	}
}

type testControlSigner struct {
	privateKey    ed25519.PrivateKey
	chainID       string
	keyGeneration uint64
	lastState     protocol.Signature
	lastOperation [sha256.Size]byte
}

func (signer *testControlSigner) ChainID() string { return signer.chainID }

func (signer *testControlSigner) SignOperation(
	payload operation.Payload,
) (*operation.SignedEvent, error) {
	event, err := operation.Sign(
		signer.privateKey, signer.chainID, signer.keyGeneration, payload,
	)
	if err == nil {
		signer.lastOperation = event.Digest()
	}
	return event, err
}

func (signer *testControlSigner) SignState(
	payload credential.StateDescriptorPayload,
) (*credential.SignedStateDescriptor, error) {
	descriptor, err := credential.SignStateDescriptor(
		signer.privateKey, signer.chainID, signer.keyGeneration, payload,
	)
	if err == nil {
		signer.lastState = descriptor.Signature()
	}
	return descriptor, err
}

type testStateVerifier struct {
	publicKey     ed25519.PublicKey
	chainID       string
	keyGeneration uint64
}

func (verifier testStateVerifier) VerifyStateDescriptor(
	_ context.Context,
	namespaceID protocol.NamespaceID,
	descriptorHash [sha256.Size]byte,
	sigInput []byte,
	signature protocol.Signature,
) (credential.StateDescriptorPayload, error) {
	keyID, err := protocol.KeyIDFromPublicKey(verifier.publicKey)
	if err != nil {
		return credential.StateDescriptorPayload{}, err
	}
	descriptor, err := credential.ParseAndVerifyStateDescriptor(
		sigInput, signature, verifier.publicKey,
		protocol.VerificationContext{
			ObjectType: protocol.ObjectTypeStateDescriptor,
			ChainID:    verifier.chainID, NamespaceID: namespaceID,
			KeyID: keyID, KeyGeneration: verifier.keyGeneration,
		},
	)
	if err != nil || descriptor.Digest() != descriptorHash {
		return credential.StateDescriptorPayload{}, ErrDailyVaultVerification
	}
	return descriptor.Payload(), nil
}

type dailyVaultFixture struct {
	database         *sqlite.Database
	objectStore      *objectfs.Store
	session          *credential.VaultSession
	service          *DailyVaultService
	namespaceID      protocol.NamespaceID
	deviceID         protocol.DeviceID
	deviceCredential [sha256.Size]byte
	signer           *testControlSigner
	now              time.Time
}

func newDailyVaultFixture(t testing.TB) *dailyVaultFixture {
	t.Helper()
	ctx := context.Background()
	database, err := sqlite.Open(ctx, filepath.Join(t.TempDir(), "vpass.db"))
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { _ = database.Close() })
	store, err := objectfs.New(filepath.Join(t.TempDir(), "objects"))
	if err != nil {
		t.Fatal(err)
	}
	var namespaceID protocol.NamespaceID
	var deviceID protocol.DeviceID
	copy(namespaceID[:], bytes.Repeat([]byte{0x11}, len(namespaceID)))
	copy(deviceID[:], bytes.Repeat([]byte{0x22}, len(deviceID)))
	devicePrivate := ed25519.NewKeyFromSeed(bytes.Repeat([]byte{0x61}, ed25519.SeedSize))
	devicePublic := devicePrivate.Public().(ed25519.PublicKey)
	rootPrivate := ed25519.NewKeyFromSeed(bytes.Repeat([]byte{0x51}, ed25519.SeedSize))
	rootPublic := rootPrivate.Public().(ed25519.PublicKey)
	rootKeyID, _ := protocol.KeyIDFromPublicKey(rootPublic)
	deviceCredential := sha256.Sum256([]byte("device credential"))
	now := time.UnixMilli(1_700_000_000_000).UTC()
	seedDailyVaultDatabase(
		t, database, namespaceID, deviceID, rootPublic, rootKeyID,
		devicePublic, deviceCredential, uint64(now.UnixMilli()),
	)
	bundle, _, err := cryptokit.GenerateRootSecretBundle(1, 1)
	if err != nil {
		t.Fatal(err)
	}
	session, err := credential.NewVaultSession(
		bundle, namespaceID, deviceID,
		credential.VaultSessionConfig{
			CreatedAt: now, IdleTimeout: 10 * time.Minute,
			AbsoluteTimeout: time.Hour, MaxHandles: 16,
			AllowedOriginBindings: [][cryptokit.OriginBindingSize]byte{
				sha256.Sum256([]byte("bootstrap origin")),
			},
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(session.Lock)
	signer := &testControlSigner{
		privateKey: devicePrivate, chainID: "vpass-test-chain", keyGeneration: 1,
	}
	verifier := testStateVerifier{
		publicKey: devicePublic, chainID: signer.chainID, keyGeneration: 1,
	}
	service, err := NewDailyVaultService(database, store, session, signer, verifier)
	if err != nil {
		t.Fatal(err)
	}
	fixture := &dailyVaultFixture{
		database: database, objectStore: store, session: session, service: service,
		namespaceID: namespaceID, deviceID: deviceID,
		deviceCredential: deviceCredential, signer: signer, now: now,
	}
	return fixture
}

func (fixture *dailyVaultFixture) createRequest() CreateCredentialRequest {
	policy, _ := password.DefaultPasswordPolicy(1)
	var installation credential.InstallationID
	copy(installation[:], bytes.Repeat([]byte{0x77}, len(installation)))
	return CreateCredentialRequest{
		Now: fixture.now.Add(time.Second), Origin: "https://Example.COM",
		AccountID: []byte("alice@example.test"), Policy: policy,
		PasswordLength: 20, InstallationID: installation,
		HandleTTL:            30 * time.Second,
		DeviceCredentialHash: fixture.deviceCredential, DeviceCounter: 1,
		AuditEpoch: 7, VerifiedBeacon: []byte("verified epoch beacon"),
		AuthorizedDeviceRoot: sha256.Sum256([]byte("authorized devices")),
		AuditCheckpoint:      sha256.Sum256([]byte("audit checkpoint")),
		FinalSequence:        1,
	}
}

func seedDailyVaultDatabase(
	t testing.TB,
	database *sqlite.Database,
	namespaceID protocol.NamespaceID,
	deviceID protocol.DeviceID,
	rootPublic ed25519.PublicKey,
	rootKeyID protocol.KeyID,
	devicePublic ed25519.PublicKey,
	deviceCredential [sha256.Size]byte,
	createdAt uint64,
) {
	t.Helper()
	ctx := context.Background()
	hpkePublic := bytes.Repeat([]byte{0x55}, 32)
	statements := []struct {
		query string
		args  []any
	}{
		{
			`INSERT INTO namespaces (
  namespace_id, protocol_version, suite_id, chain_id,
  root_signing_public_key, root_key_id, current_secret_generation,
  status, created_at_ms, updated_at_ms
) VALUES (?, 2, ?, 'vpass-test-chain', ?, ?, 1, 'ACTIVE', ?, ?)`,
			[]any{namespaceID[:], protocol.SuiteID, rootPublic, rootKeyID[:], createdAt, createdAt},
		},
		{
			`INSERT INTO namespace_key_generations (
  namespace_id, generation, secure_store_ref, status, created_at_ms
) VALUES (?, 1, 'test://namespace/generation-1', 'ACTIVE', ?)`,
			[]any{namespaceID[:], createdAt},
		},
		{
			`INSERT INTO devices (
  device_id, namespace_id, signing_public_key, hpke_public_key,
  current_key_generation, status, last_accepted_counter,
  current_credential_hash, created_at_ms, updated_at_ms
) VALUES (?, ?, ?, ?, 1, 'ACTIVE', 0, ?, ?, ?)`,
			[]any{deviceID[:], namespaceID[:], devicePublic, hpkePublic, deviceCredential[:], createdAt, createdAt},
		},
		{
			`INSERT INTO device_key_generations (
  device_id, key_generation, signing_public_key, hpke_public_key,
  signing_secret_ref, hpke_secret_ref, status, created_at_ms
) VALUES (?, 1, ?, ?, 'test://device/signing-1',
          'test://device/hpke-1', 'ACTIVE', ?)`,
			[]any{deviceID[:], devicePublic, hpkePublic, createdAt},
		},
		{
			`INSERT INTO device_operation_credentials (
  credential_hash, namespace_id, device_id, credential_cbor,
  scope_kind, valid_from_ms, valid_until_ms, secret_generation,
  status_reference_hash, issuer_key_id, root_signature, issued_at_ms
) VALUES (?, ?, ?, X'A0', 'NAMESPACE', ?, ?, 1, ?, ?, zeroblob(64), ?)`,
			[]any{
				deviceCredential[:], namespaceID[:], deviceID[:],
				createdAt - 1, createdAt + 1_000_000,
				sha256Bytes("device status"), rootKeyID[:], createdAt,
			},
		},
		{
			`INSERT INTO vault_profiles (
  namespace_id, protocol_version, suite_id, active_secret_generation,
  root_public_key, crypto_policy_hash, created_at_ms
) VALUES (?, 2, ?, 1, ?, ?, ?)`,
			[]any{
				namespaceID[:], protocol.SuiteID, rootPublic,
				sha256Bytes("crypto policy"), createdAt,
			},
		},
	}
	for _, statement := range statements {
		if _, err := database.ExecContext(ctx, statement.query, statement.args...); err != nil {
			t.Fatal(err)
		}
	}
}

type corruptReadStore struct {
	inner platform.CiphertextObjectStore
}

func (store *corruptReadStore) PutIfAbsent(
	ctx context.Context, object []byte,
) (platform.ObjectRef, error) {
	return store.inner.PutIfAbsent(ctx, object)
}

func (store *corruptReadStore) Get(
	ctx context.Context, reference platform.ObjectRef,
) ([]byte, error) {
	object, err := store.inner.Get(ctx, reference)
	if err == nil && len(object) > 0 {
		object[len(object)-1] ^= 1
	}
	return object, err
}

func (store *corruptReadStore) Has(
	ctx context.Context, reference platform.ObjectRef,
) (bool, error) {
	return store.inner.Has(ctx, reference)
}

func assertApplicationScalar(
	t *testing.T,
	database *sqlite.Database,
	query string,
	want int,
) {
	t.Helper()
	var got int
	if err := database.QueryRowContext(context.Background(), query).Scan(&got); err != nil {
		t.Fatal(err)
	}
	if got != want {
		t.Fatalf("%q = %d, want %d", query, got, want)
	}
}

func sha256Bytes(value string) []byte {
	digest := sha256.Sum256([]byte(value))
	return digest[:]
}

func BenchmarkDailyVaultRead(b *testing.B) {
	fixture := newDailyVaultFixture(b)
	ctx := context.Background()
	create := fixture.createRequest()
	created, err := fixture.service.CreateCredential(ctx, create)
	if err != nil {
		b.Fatal(err)
	}
	origin, _ := credential.NormalizeOrigin(create.Origin)
	lookup, _ := fixture.session.BuildRouteLookup(create.Now, origin, create.AccountID)
	origin.Destroy()
	initial, err := fixture.session.ConsumeSecretHandle(
		create.Now, created.PasswordHandle,
		credential.SecretHandleContext{
			InstallationID: create.InstallationID,
			OriginBinding:  lookup.OriginBinding,
			CredentialID:   created.CredentialID,
			FieldType:      cryptokit.FieldPassword,
		},
	)
	if err != nil {
		b.Fatal(err)
	}
	initial.Destroy()
	b.ResetTimer()
	for index := 0; index < b.N; index++ {
		now := create.Now.Add(time.Millisecond)
		result, err := fixture.service.ReadCredential(ctx, ReadCredentialRequest{
			Now: now, Origin: create.Origin, AccountID: create.AccountID,
			InstallationID: create.InstallationID, HandleTTL: time.Second,
		})
		if err != nil {
			b.Fatal(err)
		}
		secret, err := fixture.session.ConsumeSecretHandle(
			now, result.Handle,
			credential.SecretHandleContext{
				InstallationID: create.InstallationID,
				OriginBinding:  lookup.OriginBinding,
				CredentialID:   result.CredentialID,
				FieldType:      cryptokit.FieldPassword,
			},
		)
		if err != nil {
			b.Fatal(err)
		}
		secret.Destroy()
	}
}

func BenchmarkDailyVaultCreate(b *testing.B) {
	fixture := newDailyVaultFixture(b)
	ctx := context.Background()
	b.ResetTimer()
	for index := 0; index < b.N; index++ {
		request := fixture.createRequest()
		request.AccountID = []byte(fmt.Sprintf("benchmark-user-%d", index))
		request.DeviceCounter = uint64(index + 1)
		request.FinalSequence = uint64(index + 1)
		if index > 0 {
			previous := fixture.signer.lastOperation
			request.PreviousEventHash = &previous
		}
		result, err := fixture.service.CreateCredential(ctx, request)
		if err != nil {
			b.Fatal(err)
		}
		origin, _ := credential.NormalizeOrigin(request.Origin)
		lookup, _ := fixture.session.BuildRouteLookup(
			request.Now, origin, request.AccountID,
		)
		origin.Destroy()
		secret, err := fixture.session.ConsumeSecretHandle(
			request.Now, result.PasswordHandle,
			credential.SecretHandleContext{
				InstallationID: request.InstallationID,
				OriginBinding:  lookup.OriginBinding,
				CredentialID:   result.CredentialID,
				FieldType:      cryptokit.FieldPassword,
			},
		)
		if err != nil {
			b.Fatal(err)
		}
		secret.Destroy()
	}
}
