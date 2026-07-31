package domain

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"testing"

	"vdns.local/vdns/internal/cryptokit"
	"vdns.local/vdns/internal/platform"
	"vdns.local/vdns/internal/protocol"
)

func TestCredentialEnvelopeV2CanonicalRoundTripAndKAT(t *testing.T) {
	t.Parallel()
	_, namespaceID, credentialID := testFieldRoot(t)
	policyHash := sha256.Sum256([]byte("test-policy"))
	originBinding := sha256.Sum256([]byte("test-origin-binding"))
	fields := make([]FieldMapping, 0, 6)
	for fieldType := cryptokit.FieldOrigin; fieldType <= cryptokit.FieldNote; fieldType++ {
		fields = append(fields, deterministicEnvelopeMapping(t, fieldType, policyHash, originBinding))
	}
	draft, err := NewVersionDraft(
		credentialID, 1, 1, VersionActive, nil, policyHash, fields,
	)
	if err != nil {
		t.Fatal(err)
	}
	envelope, err := NewCredentialEnvelope(namespaceID, draft, originBinding)
	if err != nil {
		t.Fatal(err)
	}
	encoded, err := envelope.MarshalBinary()
	if err != nil {
		t.Fatal(err)
	}
	parsed, err := ParseCredentialEnvelope(encoded)
	if err != nil {
		t.Fatal(err)
	}
	if parsed.Digest() != envelope.Digest() || parsed.Version() != 1 ||
		parsed.CredentialID() != credentialID || parsed.NamespaceID() != namespaceID ||
		parsed.DescriptorBindingHash() != draft.DescriptorHash() ||
		parsed.PolicyHash() != policyHash || parsed.OriginBinding() != originBinding {
		t.Fatal("parsed envelope projection mismatch")
	}
	parsedFields := parsed.Fields()
	if len(parsedFields) != 6 {
		t.Fatalf("field count = %d", len(parsedFields))
	}
	for i, field := range parsedFields {
		if field.FieldType != cryptokit.FieldType(i+1) {
			t.Fatalf("field %d type = %d", i, field.FieldType)
		}
		if field.FieldCommitment != ([sha256.Size]byte{}) {
			t.Fatal("CP-2 unexpectedly exposes a plaintext commitment")
		}
	}
	encoded[0] ^= 1
	again, _ := envelope.MarshalBinary()
	if bytes.Equal(encoded, again) {
		t.Fatal("MarshalBinary exposed mutable storage")
	}

	const wantDigest = "21a6c7370348ab64c2c6cd1021c7bf17c13810959faf5b482780b3c39b3ed3ed"
	digest := envelope.Digest()
	got := hex.EncodeToString(digest[:])
	if wantDigest == "" {
		t.Fatalf("set envelope KAT digest to %s", got)
	}
	if got != wantDigest {
		t.Fatalf("envelope digest = %s, want %s", got, wantDigest)
	}
}

func deterministicEnvelopeMapping(
	t *testing.T,
	fieldType cryptokit.FieldType,
	policyHash [sha256.Size]byte,
	originBinding [sha256.Size]byte,
) FieldMapping {
	t.Helper()
	reference := cryptokit.FieldReference{
		FieldType: fieldType, EncryptionVersion: 1, KeyGeneration: 1,
		CryptoPolicyHash: policyHash, OriginBinding: originBinding,
		ObjectHash:   sha256.Sum256([]byte("field-object-" + fieldType.String())),
		EnvelopeHash: sha256.Sum256([]byte("wrapped-key-" + fieldType.String())),
	}
	for index := range reference.ObjectID {
		reference.ObjectID[index] = byte(fieldType)
		reference.EnvelopeID[index] = byte(fieldType + 16)
	}
	fieldDigest, err := cryptokit.FieldReferenceDigest(reference)
	if err != nil {
		t.Fatal(err)
	}
	mapping, err := restoreFieldMapping(
		reference,
		platform.ObjectRef{
			Digest: sha256.Sum256([]byte("storage-" + fieldType.String())),
			Size:   128,
		},
		bytes.Repeat([]byte{byte(fieldType)}, 48),
		protocol.SuiteID,
		fieldDigest,
	)
	if err != nil {
		t.Fatal(err)
	}
	return mapping
}

func TestCredentialEnvelopeRejectsContextAndWireTampering(t *testing.T) {
	t.Parallel()
	fieldRoot, namespaceID, credentialID := testFieldRoot(t)
	password := testFieldMapping(t, fieldRoot, namespaceID, credentialID, 1, cryptokit.FieldPassword, "secret")
	policyHash := sha256.Sum256([]byte("test-policy"))
	originBinding := sha256.Sum256([]byte("test-origin-binding"))
	draft, err := NewVersionDraft(
		credentialID, 1, 1, VersionActive, nil, policyHash, []FieldMapping{password},
	)
	if err != nil {
		t.Fatal(err)
	}
	wrongOrigin := sha256.Sum256([]byte("wrong origin"))
	if _, err := NewCredentialEnvelope(namespaceID, draft, wrongOrigin); !errors.Is(err, ErrCredentialEnvelopeContext) {
		t.Fatalf("wrong OriginBinding error = %v", err)
	}
	envelope, err := NewCredentialEnvelope(namespaceID, draft, originBinding)
	if err != nil {
		t.Fatal(err)
	}
	wire := envelope.wire
	wire.Fields = append(wire.Fields, wire.Fields[0])
	encoded, err := protocol.MarshalDeterministic(wire)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := ParseCredentialEnvelope(encoded); !errors.Is(err, ErrInvalidCredentialEnvelope) {
		t.Fatalf("duplicate field error = %v", err)
	}
	wire = envelope.wire
	wire.Fields[0].CiphertextDigest = [sha256.Size]byte{}
	encoded, _ = protocol.MarshalDeterministic(wire)
	if _, err := ParseCredentialEnvelope(encoded); !errors.Is(err, ErrInvalidCredentialEnvelope) {
		t.Fatalf("zero field digest error = %v", err)
	}
}

func FuzzParseCredentialEnvelope(f *testing.F) {
	fieldRoot, namespaceID, credentialID := testFieldRootForFuzz(f)
	password := testFieldMappingForFuzz(f, fieldRoot, namespaceID, credentialID)
	policyHash := sha256.Sum256([]byte("test-policy"))
	originBinding := sha256.Sum256([]byte("test-origin-binding"))
	draft, _ := NewVersionDraft(
		credentialID, 1, 1, VersionActive, nil, policyHash, []FieldMapping{password},
	)
	envelope, _ := NewCredentialEnvelope(namespaceID, draft, originBinding)
	seed, _ := envelope.MarshalBinary()
	f.Add(seed)
	f.Fuzz(func(t *testing.T, input []byte) {
		parsed, err := ParseCredentialEnvelope(input)
		if err != nil {
			return
		}
		encoded, err := parsed.MarshalBinary()
		if err != nil || !bytes.Equal(encoded, input) {
			t.Fatal("accepted envelope was not canonical")
		}
	})
}

func testFieldRootForFuzz(tb testing.TB) (*cryptokit.Key, protocol.NamespaceID, protocol.CredentialID) {
	tb.Helper()
	var namespaceID protocol.NamespaceID
	copy(namespaceID[:], bytes.Repeat([]byte{0x21}, len(namespaceID)))
	var credentialID protocol.CredentialID
	copy(credentialID[:], bytes.Repeat([]byte{0x31}, len(credentialID)))
	root, _ := cryptokit.NewSecret(bytes.Repeat([]byte{0x41}, cryptokit.KeySize))
	prk, _ := cryptokit.ExtractNamespacePRK(root, namespaceID, 1)
	root.Destroy()
	keys, _ := cryptokit.DeriveNamespaceKeys(prk)
	prk.Destroy()
	keys.Name.Destroy()
	keys.Audit.Destroy()
	keys.Relation.Destroy()
	keys.Rotation.Destroy()
	tb.Cleanup(keys.Wrap.Destroy)
	return keys.Wrap, namespaceID, credentialID
}

func testFieldMappingForFuzz(
	tb testing.TB,
	fieldRoot *cryptokit.Key,
	namespaceID protocol.NamespaceID,
	credentialID protocol.CredentialID,
) FieldMapping {
	tb.Helper()
	plaintext, _ := cryptokit.NewSecret([]byte("secret"))
	defer plaintext.Destroy()
	encrypted, _ := cryptokit.EncryptField(fieldRoot, cryptokit.FieldContext{
		NamespaceID: namespaceID, CredentialID: credentialID, CredentialVersion: 1,
		FieldType: cryptokit.FieldPassword, KeyGeneration: 1,
		CryptoPolicyHash: sha256.Sum256([]byte("test-policy")),
		OriginBinding:    sha256.Sum256([]byte("test-origin-binding")),
	}, plaintext)
	encoded, _ := encrypted.MarshalBinary()
	mapping, _ := NewFieldMapping(encrypted, platform.ObjectRef{
		Digest: sha256.Sum256(encoded),
		Size:   uint64(len(encoded)),
	})
	clear(encoded)
	return mapping
}
