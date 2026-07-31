package cryptokit

import (
	"bytes"
	"crypto/sha256"
	"errors"
	"testing"

	"vdns.local/vdns/internal/protocol"
)

func TestAllSixFieldTypesRoundTripWithIndependentMaterials(t *testing.T) {
	t.Parallel()

	fieldRoot := newScopedTestKey(t, purposeCredentialWrap, 1)
	t.Cleanup(fieldRoot.Destroy)
	fieldTypes := []FieldType{FieldOrigin, FieldUsername, FieldPassword, FieldTOTP, FieldRecoveryCodes, FieldNote}
	objects := make(map[FieldObjectID]struct{})
	envelopes := make(map[FieldEnvelopeID]struct{})
	nonces := make(map[[GCMNonceSize]byte]struct{})

	for index, fieldType := range fieldTypes {
		context := testFieldContext(fieldType, 1)
		plaintextValue := fieldType.String() + "-secret-value"
		plaintext, _ := NewSecret([]byte(plaintextValue))
		random := bytes.NewReader(sequence(fieldRandomMaterialLen, byte(10+index*fieldRandomMaterialLen)))
		encrypted, err := encryptFieldWithReader(fieldRoot, context, plaintext, random)
		plaintext.Destroy()
		if err != nil {
			t.Fatalf("Encrypt %s: %v", fieldType, err)
		}
		if encrypted.object.ObjectID == FieldObjectID(encrypted.dekEnvelope.EnvelopeID) {
			t.Fatalf("%s object and envelope IDs are equal", fieldType)
		}
		if encrypted.object.Nonce == encrypted.dekEnvelope.Nonce {
			t.Fatalf("%s field and wrap nonces are equal", fieldType)
		}
		if _, exists := objects[encrypted.object.ObjectID]; exists {
			t.Fatalf("duplicate field object ID for %s", fieldType)
		}
		objects[encrypted.object.ObjectID] = struct{}{}
		if _, exists := envelopes[encrypted.dekEnvelope.EnvelopeID]; exists {
			t.Fatalf("duplicate envelope ID for %s", fieldType)
		}
		envelopes[encrypted.dekEnvelope.EnvelopeID] = struct{}{}
		for _, nonce := range [][GCMNonceSize]byte{encrypted.object.Nonce, encrypted.dekEnvelope.Nonce} {
			if _, exists := nonces[nonce]; exists {
				t.Fatalf("duplicate nonce for %s", fieldType)
			}
			nonces[nonce] = struct{}{}
		}

		encoded, err := encrypted.MarshalBinary()
		if err != nil {
			t.Fatalf("Marshal %s: %v", fieldType, err)
		}
		parsed, err := ParseEncryptedField(encoded)
		if err != nil {
			t.Fatalf("Parse %s: %v", fieldType, err)
		}
		opened, err := DecryptField(fieldRoot, context, parsed)
		if err != nil {
			t.Fatalf("Decrypt %s: %v", fieldType, err)
		}
		assertSecretEquals(t, opened, plaintextValue)
		opened.Destroy()
	}
}

func TestPasswordOnlyReplacementPreservesOtherFieldReferences(t *testing.T) {
	t.Parallel()

	fieldRoot := newScopedTestKey(t, purposeCredentialWrap, 41)
	t.Cleanup(fieldRoot.Destroy)
	fieldTypes := []FieldType{FieldOrigin, FieldUsername, FieldPassword, FieldTOTP, FieldRecoveryCodes, FieldNote}
	before := make(map[FieldType]FieldReference)
	after := make(map[FieldType]FieldReference)

	for index, fieldType := range fieldTypes {
		plaintext, _ := NewSecret([]byte(fieldType.String() + "-v1"))
		encrypted, err := encryptFieldWithReader(
			fieldRoot,
			testFieldContext(fieldType, 1),
			plaintext,
			bytes.NewReader(sequence(fieldRandomMaterialLen, byte(10+index*17))),
		)
		plaintext.Destroy()
		if err != nil {
			t.Fatalf("encrypt %s: %v", fieldType, err)
		}
		reference, err := encrypted.Reference()
		if err != nil {
			t.Fatalf("Reference %s: %v", fieldType, err)
		}
		before[fieldType] = reference
		after[fieldType] = reference
	}

	newPassword, _ := NewSecret([]byte("PASSWORD-v2"))
	replacement, err := encryptFieldWithReader(
		fieldRoot,
		testFieldContext(FieldPassword, 2),
		newPassword,
		bytes.NewReader(sequence(fieldRandomMaterialLen, 201)),
	)
	newPassword.Destroy()
	if err != nil {
		t.Fatalf("encrypt password replacement: %v", err)
	}
	after[FieldPassword], _ = replacement.Reference()

	for _, fieldType := range fieldTypes {
		if fieldType == FieldPassword {
			if before[fieldType] == after[fieldType] {
				t.Fatal("password field reference did not change")
			}
			continue
		}
		if before[fieldType] != after[fieldType] {
			t.Fatalf("unchanged %s reference changed:\nbefore=%#v\nafter=%#v", fieldType, before[fieldType], after[fieldType])
		}
	}
}

func TestReusedFieldReferenceCarriesOriginalEncryptionContext(t *testing.T) {
	t.Parallel()

	fieldRoot := newScopedTestKey(t, purposeCredentialWrap, 61)
	v1Context := testFieldContext(FieldUsername, 1)
	plaintext, _ := NewSecret([]byte("alice@example.test"))
	defer plaintext.Destroy()
	encryptedV1, err := encryptFieldWithReader(
		fieldRoot,
		v1Context,
		plaintext,
		bytes.NewReader(sequence(fieldRandomMaterialLen, 101)),
	)
	if err != nil {
		t.Fatalf("encrypt v1 field: %v", err)
	}
	reference, err := encryptedV1.Reference()
	if err != nil {
		t.Fatalf("Reference: %v", err)
	}
	if reference.EncryptionVersion != 1 || reference.KeyGeneration != v1Context.KeyGeneration {
		t.Fatalf("reference lost original context: %#v", reference)
	}

	// A credential-v2 mapping reuses the v1 reference verbatim. Decryption must
	// reconstruct v1 AAD rather than pretending the old object was encrypted as
	// part of v2.
	opened, err := DecryptFieldByReference(
		fieldRoot,
		v1Context.NamespaceID,
		v1Context.CredentialID,
		reference,
		encryptedV1,
	)
	if err != nil {
		t.Fatalf("decrypt reused v1 reference from v2 mapping: %v", err)
	}
	assertSecretEquals(t, opened, "alice@example.test")
	opened.Destroy()

	v2Context := v1Context
	v2Context.CredentialVersion = 2
	if opened, err := DecryptField(fieldRoot, v2Context, encryptedV1); opened != nil || !errors.Is(err, ErrRejectAEAD) {
		t.Fatalf("old field accepted under v2 AAD: %v, %v", opened, err)
	}

	wrongVersion := reference
	wrongVersion.EncryptionVersion = 2
	if opened, err := DecryptFieldByReference(fieldRoot, v1Context.NamespaceID, v1Context.CredentialID, wrongVersion, encryptedV1); opened != nil || !errors.Is(err, ErrRejectAEAD) {
		t.Fatalf("forged encryption version accepted: %v, %v", opened, err)
	}
	wrongGeneration := reference
	wrongGeneration.KeyGeneration++
	if opened, err := DecryptFieldByReference(fieldRoot, v1Context.NamespaceID, v1Context.CredentialID, wrongGeneration, encryptedV1); opened != nil || !errors.Is(err, ErrRejectAEAD) {
		t.Fatalf("forged generation accepted: %v, %v", opened, err)
	}
}

func TestFieldReferenceAndWrappedDEKPersistenceProjection(t *testing.T) {
	t.Parallel()
	fieldRoot := newScopedTestKey(t, purposeCredentialWrap, 71)
	t.Cleanup(fieldRoot.Destroy)
	plaintext, _ := NewSecret([]byte("persisted-password"))
	defer plaintext.Destroy()
	encrypted, err := encryptFieldWithReader(
		fieldRoot,
		testFieldContext(FieldPassword, 4),
		plaintext,
		bytes.NewReader(sequence(fieldRandomMaterialLen, 141)),
	)
	if err != nil {
		t.Fatal(err)
	}
	reference, err := encrypted.Reference()
	if err != nil {
		t.Fatal(err)
	}
	encoded, err := EncodeFieldReference(reference)
	if err != nil {
		t.Fatal(err)
	}
	digest, err := FieldReferenceDigest(reference)
	if err != nil {
		t.Fatal(err)
	}
	if digest != sha256.Sum256(encoded) {
		t.Fatal("field reference digest differs from canonical bytes")
	}
	wrapped, suite, err := encrypted.WrappedDEKProjection()
	if err != nil || suite != protocol.SuiteID || len(wrapped) != KeySize+GCMTagSize {
		t.Fatalf("wrapped projection = %d bytes, %q, %v", len(wrapped), suite, err)
	}
	wrapped[0] ^= 1
	again, _, err := encrypted.WrappedDEKProjection()
	if err != nil || bytes.Equal(wrapped, again) {
		t.Fatal("wrapped DEK projection exposed mutable storage")
	}
	invalid := reference
	invalid.EncryptionVersion = 0
	if _, err := EncodeFieldReference(invalid); !errors.Is(err, ErrInvalidInput) {
		t.Fatalf("invalid reference error = %v", err)
	}
}

func TestFieldTamperingAlwaysRejectsWithoutPlaintext(t *testing.T) {
	t.Parallel()

	fieldRoot := newScopedTestKey(t, purposeCredentialWrap, 19)
	t.Cleanup(fieldRoot.Destroy)
	context := testFieldContext(FieldPassword, 1)
	plaintext, _ := NewSecret([]byte("password-value"))
	encrypted, err := encryptFieldWithReader(
		fieldRoot,
		context,
		plaintext,
		bytes.NewReader(sequence(fieldRandomMaterialLen, 77)),
	)
	plaintext.Destroy()
	if err != nil {
		t.Fatalf("encryptFieldWithReader: %v", err)
	}

	tests := []struct {
		name   string
		mutate func(*EncryptedField)
	}{
		{name: "field nonce", mutate: func(value *EncryptedField) { value.object.Nonce[0] ^= 1 }},
		{name: "field aad", mutate: func(value *EncryptedField) { value.object.AAD[0] ^= 1 }},
		{name: "field ciphertext", mutate: func(value *EncryptedField) { value.object.Ciphertext[0] ^= 1 }},
		{name: "field hash", mutate: func(value *EncryptedField) { value.object.ContentHash[0] ^= 1 }},
		{name: "wrap nonce", mutate: func(value *EncryptedField) { value.dekEnvelope.Nonce[0] ^= 1 }},
		{name: "wrap aad", mutate: func(value *EncryptedField) { value.dekEnvelope.AAD[0] ^= 1 }},
		{name: "wrapped dek", mutate: func(value *EncryptedField) { value.dekEnvelope.WrappedDEK[0] ^= 1 }},
		{name: "envelope hash", mutate: func(value *EncryptedField) { value.dekEnvelope.ContentHash[0] ^= 1 }},
		{name: "object linkage", mutate: func(value *EncryptedField) { value.dekEnvelope.FieldObjectID[0] ^= 1 }},
	}
	for _, test := range tests {
		test := test
		t.Run(test.name, func(t *testing.T) {
			t.Parallel()
			changed := encrypted.Clone()
			test.mutate(changed)
			opened, decryptErr := DecryptField(fieldRoot, context, changed)
			if opened != nil || !errors.Is(decryptErr, ErrRejectAEAD) {
				t.Fatalf("DecryptField = %v, %v; want nil, %v", opened, decryptErr, ErrRejectAEAD)
			}
		})
	}
}

func TestFieldRejectsWrongContextRootAndTestEntropy(t *testing.T) {
	t.Parallel()

	fieldRoot := newScopedTestKey(t, purposeCredentialWrap, 1)
	t.Cleanup(fieldRoot.Destroy)
	context := testFieldContext(FieldTOTP, 3)
	plaintext, _ := NewSecret([]byte("totp-seed"))
	defer plaintext.Destroy()
	if _, err := EncryptFieldWithEntropy(
		fieldRoot,
		context,
		plaintext,
		NewTestOnlyEntropySource(bytes.NewReader(make([]byte, fieldRandomMaterialLen))),
	); err != ErrRandomSource {
		t.Fatalf("test entropy = %v, want %v", err, ErrRandomSource)
	}
	encrypted, _ := encryptFieldWithReader(
		fieldRoot,
		context,
		plaintext,
		bytes.NewReader(sequence(fieldRandomMaterialLen, 33)),
	)

	wrongVersion := context
	wrongVersion.CredentialVersion++
	if opened, err := DecryptField(fieldRoot, wrongVersion, encrypted); opened != nil || err != ErrRejectAEAD {
		t.Fatalf("wrong version = %v, %v", opened, err)
	}
	wrongType := context
	wrongType.FieldType = FieldNote
	if opened, err := DecryptField(fieldRoot, wrongType, encrypted); opened != nil || err != ErrRejectAEAD {
		t.Fatalf("wrong type = %v, %v", opened, err)
	}
	wrongGeneration := context
	wrongGeneration.KeyGeneration++
	if opened, err := DecryptField(fieldRoot, wrongGeneration, encrypted); opened != nil || err != ErrRejectAEAD {
		t.Fatalf("wrong generation = %v, %v", opened, err)
	}
	wrongPolicy := context
	wrongPolicy.CryptoPolicyHash[0] ^= 1
	if opened, err := DecryptField(fieldRoot, wrongPolicy, encrypted); opened != nil || err != ErrRejectAEAD {
		t.Fatalf("wrong crypto policy = %v, %v", opened, err)
	}
	wrongOrigin := context
	wrongOrigin.OriginBinding[0] ^= 1
	if opened, err := DecryptField(fieldRoot, wrongOrigin, encrypted); opened != nil || err != ErrRejectAEAD {
		t.Fatalf("wrong origin binding = %v, %v", opened, err)
	}
	wrongRoot := newScopedTestKey(t, purposeCredentialWrap, 2)
	defer wrongRoot.Destroy()
	if opened, err := DecryptField(wrongRoot, context, encrypted); opened != nil || err != ErrRejectAEAD {
		t.Fatalf("wrong root = %v, %v", opened, err)
	}
}

func FuzzParseAndDecryptField(f *testing.F) {
	fieldRoot := newScopedTestKey(f, purposeCredentialWrap, 1)
	context := testFieldContext(FieldPassword, 1)
	plaintext, _ := NewSecret([]byte("fuzz-password"))
	encrypted, _ := encryptFieldWithReader(
		fieldRoot,
		context,
		plaintext,
		bytes.NewReader(sequence(fieldRandomMaterialLen, 13)),
	)
	seed, _ := encrypted.MarshalBinary()
	plaintext.Destroy()
	defer fieldRoot.Destroy()
	f.Add(seed)
	f.Add([]byte{0xa1, 0x01, 0x02})
	f.Fuzz(func(t *testing.T, encoded []byte) {
		parsed, err := ParseEncryptedField(encoded)
		if err != nil {
			return
		}
		opened, err := DecryptField(fieldRoot, context, parsed)
		if err == nil {
			opened.Destroy()
		}
	})
}

func testFieldContext(fieldType FieldType, version uint64) FieldContext {
	var namespaceID protocol.NamespaceID
	copy(namespaceID[:], sequence(len(namespaceID), 1))
	var credentialID protocol.CredentialID
	copy(credentialID[:], sequence(len(credentialID), 51))
	return FieldContext{
		NamespaceID:       namespaceID,
		CredentialID:      credentialID,
		CredentialVersion: version,
		FieldType:         fieldType,
		KeyGeneration:     1,
		CryptoPolicyHash:  sha256.Sum256([]byte("CP-2/default-policy")),
		OriginBinding:     sha256.Sum256([]byte("https://example.test|alice")),
	}
}
