package application

import (
	"bytes"
	"context"
	"crypto/ed25519"
	"crypto/sha256"
	"errors"
	"testing"

	"vdns.local/vdns/internal/adapters/outbound/memorysync"
	credential "vdns.local/vdns/internal/credential/domain"
	"vdns.local/vdns/internal/cryptokit"
	"vdns.local/vdns/internal/platform"
	"vdns.local/vdns/internal/protocol"
	syncdomain "vdns.local/vdns/internal/sync/domain"
)

func TestAcceptanceVerifiesCompleteCandidateBeforeSingleCommit(t *testing.T) {
	t.Parallel()
	fixture := newAcceptanceFixture(t, true)
	service := fixture.service(t)
	if err := service.AcceptManifest(
		context.Background(), fixture.record,
		fixture.namespaceID, fixture.checkpoint,
	); err != nil {
		t.Fatal(err)
	}
	if fixture.committer.calls != 1 || len(fixture.committer.summaries) != 1 {
		t.Fatalf("commit calls=%d summaries=%d", fixture.committer.calls, len(fixture.committer.summaries))
	}
	summary := fixture.committer.summaries[0]
	if summary.credentialID != fixture.credentialID ||
		summary.version != 1 || summary.objectCount != 3 ||
		summary.checkpoint != fixture.checkpoint {
		t.Fatalf("unexpected committed candidate: %+v", summary)
	}
}

func TestAcceptanceRejectsMissingCorruptAndIncompleteObjectsWithoutCommit(t *testing.T) {
	t.Parallel()
	tests := []struct {
		name   string
		fault  func(*acceptanceFixture)
		target error
	}{
		{
			name: "missing",
			fault: func(fixture *acceptanceFixture) {
				digest := fixture.references[2].ObjectDigest
				fixture.cloud.SetFaults(memorysync.Faults{OmitObject: &digest})
			},
			target: ErrIncompleteCandidate,
		},
		{
			name: "corrupt",
			fault: func(fixture *acceptanceFixture) {
				digest := fixture.references[0].ObjectDigest
				fixture.cloud.SetFaults(memorysync.Faults{CorruptObject: &digest})
			},
			target: ErrIncompleteCandidate,
		},
		{
			name:   "field-object-not-in-manifest",
			fault:  func(fixture *acceptanceFixture) {},
			target: ErrCandidateMismatch,
		},
	}
	for _, test := range tests {
		test := test
		t.Run(test.name, func(t *testing.T) {
			t.Parallel()
			includeField := test.name != "field-object-not-in-manifest"
			fixture := newAcceptanceFixture(t, includeField)
			test.fault(fixture)
			err := fixture.service(t).AcceptManifest(
				context.Background(), fixture.record,
				fixture.namespaceID, fixture.checkpoint,
			)
			if !errors.Is(err, test.target) {
				t.Fatalf("error=%v, want %v", err, test.target)
			}
			if fixture.committer.calls != 0 {
				t.Fatal("partial candidate reached committer")
			}
		})
	}
}

func TestAcceptanceRejectsCloudRollbackAndTrustedStateMismatch(t *testing.T) {
	t.Parallel()
	t.Run("receiver-checkpoint-wins", func(t *testing.T) {
		t.Parallel()
		fixture := newAcceptanceFixture(t, true)
		newer := sha256.Sum256([]byte("receiver-newer-checkpoint"))
		err := fixture.service(t).AcceptManifest(
			context.Background(), fixture.record, fixture.namespaceID, newer,
		)
		if !errors.Is(err, ErrUntrustedManifest) {
			t.Fatalf("rollback error=%v", err)
		}
		if fixture.committer.calls != 0 {
			t.Fatal("rollback candidate committed")
		}
	})
	t.Run("trusted-envelope-hash-wins", func(t *testing.T) {
		t.Parallel()
		fixture := newAcceptanceFixture(t, true)
		fixture.trusted.EnvelopeHash = sha256.Sum256([]byte("other-envelope"))
		err := fixture.service(t).AcceptManifest(
			context.Background(), fixture.record,
			fixture.namespaceID, fixture.checkpoint,
		)
		if !errors.Is(err, ErrCandidateMismatch) {
			t.Fatalf("mismatch error=%v", err)
		}
		if fixture.committer.calls != 0 {
			t.Fatal("mismatched candidate committed")
		}
	})
}

type acceptanceFixture struct {
	namespaceID  protocol.NamespaceID
	credentialID protocol.CredentialID
	deviceID     protocol.DeviceID
	checkpoint   [sha256.Size]byte
	manifestKey  ed25519.PrivateKey
	stateKey     ed25519.PrivateKey
	record       syncdomain.ManifestRecord
	references   []syncdomain.ObjectReference
	cloud        *memorysync.Store
	trusted      TrustedCredentialState
	committer    *recordingCommitter
}

func newAcceptanceFixture(t *testing.T, includeField bool) *acceptanceFixture {
	t.Helper()
	fixture := &acceptanceFixture{
		manifestKey: ed25519.NewKeyFromSeed(bytes.Repeat([]byte{0x81}, ed25519.SeedSize)),
		stateKey:    ed25519.NewKeyFromSeed(bytes.Repeat([]byte{0x82}, ed25519.SeedSize)),
		checkpoint:  sha256.Sum256([]byte("trusted-checkpoint")),
		cloud:       memorysync.New(),
		committer:   &recordingCommitter{},
	}
	copy(fixture.namespaceID[:], bytes.Repeat([]byte{0x11}, len(fixture.namespaceID)))
	copy(fixture.credentialID[:], bytes.Repeat([]byte{0x22}, len(fixture.credentialID)))
	copy(fixture.deviceID[:], bytes.Repeat([]byte{0x33}, len(fixture.deviceID)))

	root, err := cryptokit.NewSecret(bytes.Repeat([]byte{0x41}, cryptokit.KeySize))
	if err != nil {
		t.Fatal(err)
	}
	prk, err := cryptokit.ExtractNamespacePRK(root, fixture.namespaceID, 1)
	root.Destroy()
	if err != nil {
		t.Fatal(err)
	}
	keys, err := cryptokit.DeriveNamespaceKeys(prk)
	prk.Destroy()
	if err != nil {
		t.Fatal(err)
	}
	defer keys.Destroy()

	policyHash := sha256.Sum256([]byte("policy"))
	originBinding := sha256.Sum256([]byte("origin"))
	plaintext, err := cryptokit.NewSecret([]byte("complex-password"))
	if err != nil {
		t.Fatal(err)
	}
	encrypted, err := cryptokit.EncryptField(keys.Wrap, cryptokit.FieldContext{
		NamespaceID: fixture.namespaceID, CredentialID: fixture.credentialID,
		CredentialVersion: 1, FieldType: cryptokit.FieldPassword,
		KeyGeneration: 1, CryptoPolicyHash: policyHash,
		OriginBinding: originBinding,
	}, plaintext)
	plaintext.Destroy()
	if err != nil {
		t.Fatal(err)
	}
	fieldBytes, err := encrypted.MarshalBinary()
	if err != nil {
		t.Fatal(err)
	}
	fieldReference := platform.ObjectRef{
		Digest: sha256.Sum256(fieldBytes), Size: uint64(len(fieldBytes)),
	}
	mapping, err := credential.NewFieldMapping(encrypted, fieldReference)
	if err != nil {
		t.Fatal(err)
	}
	draft, err := credential.NewVersionDraft(
		fixture.credentialID, 1, 1, credential.VersionActive,
		nil, policyHash, []credential.FieldMapping{mapping},
	)
	if err != nil {
		t.Fatal(err)
	}
	envelope, err := credential.NewCredentialEnvelope(
		fixture.namespaceID, draft, originBinding,
	)
	if err != nil {
		t.Fatal(err)
	}
	envelopeBytes, err := envelope.MarshalBinary()
	if err != nil {
		t.Fatal(err)
	}
	state, err := credential.SignStateDescriptor(
		fixture.stateKey, "sync-chain", 1,
		credential.StateDescriptorPayload{
			NamespaceID: fixture.namespaceID, CredentialID: fixture.credentialID,
			ActiveVersion: 1, ActiveEnvelopeHash: envelope.Digest(),
			LifecycleStatus:      protocol.LifecycleActive,
			LastOperationEvent:   sha256.Sum256([]byte("operation")),
			AuthorizedDeviceRoot: sha256.Sum256([]byte("devices")),
			AuditCheckpoint:      fixture.checkpoint, FinalSequence: 7,
			UpdaterDeviceID: fixture.deviceID,
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	stateBytes, err := state.MarshalBinary()
	if err != nil {
		t.Fatal(err)
	}
	version := uint64(1)
	references := []syncdomain.ObjectReference{
		{
			ObjectDigest: sha256.Sum256(envelopeBytes),
			ObjectType:   protocol.ObjectTypeCredentialEnvelope,
			CredentialID: &fixture.credentialID, Version: &version,
			Size: uint64(len(envelopeBytes)),
		},
		{
			ObjectDigest: sha256.Sum256(stateBytes),
			ObjectType:   protocol.ObjectTypeStateDescriptor,
			CredentialID: &fixture.credentialID, Version: &version,
			Size: uint64(len(stateBytes)),
		},
	}
	objectBytes := [][]byte{envelopeBytes, stateBytes}
	if includeField {
		references = append(references, syncdomain.ObjectReference{
			ObjectDigest: fieldReference.Digest,
			ObjectType:   protocol.ObjectTypeSecretEnvelope,
			CredentialID: &fixture.credentialID, Version: &version,
			Size: fieldReference.Size,
		})
		objectBytes = append(objectBytes, fieldBytes)
	}
	manifest, err := syncdomain.SignManifest(
		fixture.manifestKey, "sync-chain", 1,
		fixture.namespaceID, fixture.deviceID,
		sha256.Sum256([]byte("base-checkpoint")), fixture.checkpoint,
		5, 7, references,
	)
	if err != nil {
		t.Fatal(err)
	}
	fixture.record, err = syncdomain.RecordFromManifest(manifest)
	if err != nil {
		t.Fatal(err)
	}
	fixture.references = manifest.Objects()
	for index, reference := range references {
		if err := fixture.cloud.PutObject(
			context.Background(),
			platform.ObjectRef{Digest: reference.ObjectDigest, Size: reference.Size},
			objectBytes[index],
		); err != nil {
			t.Fatal(err)
		}
	}
	if err := fixture.cloud.PublishManifest(
		context.Background(), fixture.record, references,
	); err != nil {
		t.Fatal(err)
	}
	fixture.trusted = TrustedCredentialState{
		NamespaceID: fixture.namespaceID, CredentialID: fixture.credentialID,
		Version: 1, EnvelopeHash: envelope.Digest(),
		DescriptorHash: state.Digest(), CryptoPolicyHash: policyHash,
		DescriptorBindingHash: draft.DescriptorHash(),
		Checkpoint:            fixture.checkpoint,
	}
	return fixture
}

func (fixture *acceptanceFixture) service(t *testing.T) *AcceptanceService {
	t.Helper()
	manifestKeyID, _ := protocol.KeyIDFromPublicKey(
		fixture.manifestKey.Public().(ed25519.PublicKey),
	)
	stateKeyID, _ := protocol.KeyIDFromPublicKey(
		fixture.stateKey.Public().(ed25519.PublicKey),
	)
	service, err := NewAcceptanceService(
		fixture.cloud,
		testManifestVerifier{
			publicKey: fixture.manifestKey.Public().(ed25519.PublicKey),
			expected: protocol.VerificationContext{
				ObjectType: protocol.ObjectTypeSyncManifest,
				ChainID:    "sync-chain", NamespaceID: fixture.namespaceID,
				KeyID: manifestKeyID, KeyGeneration: 1,
			},
		},
		testDescriptorVerifier{
			publicKey: fixture.stateKey.Public().(ed25519.PublicKey),
			expected: protocol.VerificationContext{
				ObjectType: protocol.ObjectTypeStateDescriptor,
				ChainID:    "sync-chain", NamespaceID: fixture.namespaceID,
				KeyID: stateKeyID, KeyGeneration: 1,
			},
		},
		testTrustResolver{state: fixture.trusted},
		fixture.committer,
	)
	if err != nil {
		t.Fatal(err)
	}
	return service
}

type testManifestVerifier struct {
	publicKey ed25519.PublicKey
	expected  protocol.VerificationContext
}

func (verifier testManifestVerifier) VerifyManifest(
	_ context.Context,
	record syncdomain.ManifestRecord,
) (*syncdomain.SignedManifest, error) {
	return syncdomain.ParseAndVerifyManifest(
		record.SigInputCBOR, record.Signature, verifier.publicKey, verifier.expected,
	)
}

type testDescriptorVerifier struct {
	publicKey ed25519.PublicKey
	expected  protocol.VerificationContext
}

func (verifier testDescriptorVerifier) VerifyStateDescriptorObject(
	_ context.Context,
	_ protocol.NamespaceID,
	object []byte,
) (*credential.SignedStateDescriptor, error) {
	return credential.ParseAndVerifyStateDescriptorObject(
		object, verifier.publicKey, verifier.expected,
	)
}

type testTrustResolver struct {
	state TrustedCredentialState
	err   error
}

func (resolver testTrustResolver) ResolveCredentialState(
	_ context.Context,
	_ protocol.NamespaceID,
	_ [sha256.Size]byte,
	_ protocol.CredentialID,
	_ uint64,
) (TrustedCredentialState, error) {
	return resolver.state, resolver.err
}

type candidateSummary struct {
	credentialID protocol.CredentialID
	version      uint64
	objectCount  int
	checkpoint   [sha256.Size]byte
}

type recordingCommitter struct {
	calls     int
	summaries []candidateSummary
	err       error
}

func (committer *recordingCommitter) CommitCandidates(
	_ context.Context,
	candidates []CandidateBundle,
) error {
	committer.calls++
	for _, candidate := range candidates {
		committer.summaries = append(committer.summaries, candidateSummary{
			credentialID: candidate.Envelope.CredentialID(),
			version:      candidate.Envelope.Version(), objectCount: len(candidate.Objects),
			checkpoint: candidate.Checkpoint,
		})
	}
	return committer.err
}
