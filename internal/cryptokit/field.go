package cryptokit

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/sha256"
	"crypto/subtle"

	"vdns.local/vdns/internal/protocol"
)

const (
	FieldFormatV2          = uint64(2)
	FieldObjectIDSize      = 32
	MaxFieldPlaintextSize  = 64 * 1024
	MaxEncryptedFieldSize  = 128 * 1024
	fieldRandomMaterialLen = KeySize + FieldObjectIDSize*2 + GCMNonceSize*2
)

// FieldType is the frozen CP-2 integer enum. New values require a protocol or
// suite revision.
type FieldType uint8

const (
	FieldOrigin        FieldType = 1
	FieldUsername      FieldType = 2
	FieldPassword      FieldType = 3
	FieldTOTP          FieldType = 4
	FieldRecoveryCodes FieldType = 5
	FieldNote          FieldType = 6
)

// Valid reports whether the value belongs to the frozen six-field enum.
func (fieldType FieldType) Valid() bool {
	return fieldType >= FieldOrigin && fieldType <= FieldNote
}

// String returns the stable database/API spelling for a field type.
func (fieldType FieldType) String() string {
	switch fieldType {
	case FieldOrigin:
		return "ORIGIN"
	case FieldUsername:
		return "USERNAME"
	case FieldPassword:
		return "PASSWORD"
	case FieldTOTP:
		return "TOTP"
	case FieldRecoveryCodes:
		return "RECOVERY_CODES"
	case FieldNote:
		return "NOTE"
	default:
		return "UNKNOWN"
	}
}

// ParseFieldType converts the stable database/API projection to the frozen
// wire enum.
func ParseFieldType(value string) (FieldType, error) {
	switch value {
	case "ORIGIN":
		return FieldOrigin, nil
	case "USERNAME":
		return FieldUsername, nil
	case "PASSWORD":
		return FieldPassword, nil
	case "TOTP":
		return FieldTOTP, nil
	case "RECOVERY_CODES":
		return FieldRecoveryCodes, nil
	case "NOTE":
		return FieldNote, nil
	default:
		return 0, ErrInvalidInput
	}
}

// FieldObjectID and FieldEnvelopeID are independent random 256-bit identifiers.
type (
	FieldObjectID   [FieldObjectIDSize]byte
	FieldEnvelopeID [FieldObjectIDSize]byte
)

// FieldContext contains the caller-supplied context for one field object.
type FieldContext struct {
	NamespaceID       protocol.NamespaceID
	CredentialID      protocol.CredentialID
	CredentialVersion uint64
	FieldType         FieldType
	KeyGeneration     uint64
	CryptoPolicyHash  [sha256.Size]byte
	OriginBinding     [OriginBindingSize]byte
}

// FieldAAD is the complete authenticated context for field ciphertext.
type FieldAAD struct {
	ProtocolID        string                  `cbor:"protocol_id"`
	ProtocolVersion   uint64                  `cbor:"protocol_version"`
	SuiteID           string                  `cbor:"suite_id"`
	NamespaceID       protocol.NamespaceID    `cbor:"namespace_id"`
	CredentialID      protocol.CredentialID   `cbor:"credential_id"`
	CredentialVersion uint64                  `cbor:"credential_version"`
	EncryptionVersion uint64                  `cbor:"encryption_version"`
	FieldType         FieldType               `cbor:"field_type"`
	FieldObjectID     FieldObjectID           `cbor:"field_object_id"`
	KeyGeneration     uint64                  `cbor:"key_generation"`
	CryptoPolicyHash  [sha256.Size]byte       `cbor:"crypto_policy_hash"`
	OriginBinding     [OriginBindingSize]byte `cbor:"origin_binding"`
}

// FieldReference is the stable, non-secret reference stored by a credential
// version. Reusing this value preserves unchanged fields byte-for-byte.
type FieldReference struct {
	FieldType         FieldType               `cbor:"field_type"`
	EncryptionVersion uint64                  `cbor:"encryption_version"`
	KeyGeneration     uint64                  `cbor:"key_generation"`
	CryptoPolicyHash  [sha256.Size]byte       `cbor:"crypto_policy_hash"`
	OriginBinding     [OriginBindingSize]byte `cbor:"origin_binding"`
	ObjectID          FieldObjectID           `cbor:"field_object_id"`
	ObjectHash        [sha256.Size]byte       `cbor:"field_object_hash"`
	EnvelopeID        FieldEnvelopeID         `cbor:"envelope_id"`
	EnvelopeHash      [sha256.Size]byte       `cbor:"envelope_hash"`
}

// EncryptedField is an immutable field object plus its independently encrypted
// DEK envelope. It exposes only digests and IDs; serialization returns copies.
type EncryptedField struct {
	object      fieldObjectWire
	dekEnvelope dekEnvelopeWire
}

type encryptedFieldWire struct {
	Object      fieldObjectWire `cbor:"object"`
	DEKEnvelope dekEnvelopeWire `cbor:"dek_envelope"`
}

type fieldObjectWire struct {
	FormatVersion uint64             `cbor:"format_version"`
	SuiteID       string             `cbor:"suite_id"`
	ObjectID      FieldObjectID      `cbor:"object_id"`
	Nonce         [GCMNonceSize]byte `cbor:"nonce"`
	AAD           []byte             `cbor:"aad"`
	Ciphertext    []byte             `cbor:"ciphertext"`
	ContentHash   [sha256.Size]byte  `cbor:"content_hash"`
}

type dekEnvelopeWire struct {
	FormatVersion uint64             `cbor:"format_version"`
	SuiteID       string             `cbor:"suite_id"`
	EnvelopeID    FieldEnvelopeID    `cbor:"envelope_id"`
	FieldObjectID FieldObjectID      `cbor:"field_object_id"`
	Nonce         [GCMNonceSize]byte `cbor:"nonce"`
	AAD           []byte             `cbor:"aad"`
	WrappedDEK    []byte             `cbor:"wrapped_dek"`
	ContentHash   [sha256.Size]byte  `cbor:"content_hash"`
}

// EncryptField creates a per-field DEK, field object, and DEK envelope using
// OS CSPRNG entropy.
func EncryptField(fieldRoot *Key, context FieldContext, plaintext *Secret) (*EncryptedField, error) {
	return EncryptFieldWithEntropy(fieldRoot, context, plaintext, SystemEntropySource())
}

// EncryptFieldWithEntropy accepts only an explicitly production-safe source.
func EncryptFieldWithEntropy(
	fieldRoot *Key,
	context FieldContext,
	plaintext *Secret,
	source EntropySource,
) (*EncryptedField, error) {
	reader, err := source.productionReader()
	if err != nil {
		return nil, err
	}
	return encryptFieldWithReader(fieldRoot, context, plaintext, reader)
}

func encryptFieldWithReader(
	fieldRoot *Key,
	context FieldContext,
	plaintext *Secret,
	randomReader interface{ Read([]byte) (int, error) },
) (*EncryptedField, error) {
	if fieldRoot == nil || plaintext == nil || plaintext.Len() == 0 || plaintext.Len() > MaxFieldPlaintextSize ||
		validateFieldContext(context) != nil {
		return nil, ErrInvalidInput
	}
	if err := fieldRoot.requirePurpose(purposeCredentialWrap); err != nil {
		return nil, err
	}

	randomMaterial := make([]byte, fieldRandomMaterialLen)
	if err := fillRandom(randomReader, randomMaterial); err != nil {
		return nil, err
	}
	defer wipe(randomMaterial)

	dek, err := newKeyWithPurpose(randomMaterial[:KeySize], purposeFieldDEK)
	if err != nil {
		return nil, err
	}
	defer dek.Destroy()
	var objectID FieldObjectID
	copy(objectID[:], randomMaterial[KeySize:KeySize+FieldObjectIDSize])
	var envelopeID FieldEnvelopeID
	copy(envelopeID[:], randomMaterial[KeySize+FieldObjectIDSize:KeySize+FieldObjectIDSize*2])
	var fieldNonce [GCMNonceSize]byte
	copy(fieldNonce[:], randomMaterial[KeySize+FieldObjectIDSize*2:KeySize+FieldObjectIDSize*2+GCMNonceSize])
	var wrapNonce [GCMNonceSize]byte
	copy(wrapNonce[:], randomMaterial[KeySize+FieldObjectIDSize*2+GCMNonceSize:])

	fieldAAD := fieldAADFor(context, objectID)
	fieldAADBytes, err := protocol.MarshalDeterministic(fieldAAD)
	if err != nil {
		return nil, ErrInvalidInput
	}

	var ciphertext []byte
	err = dek.withPurposeBytes(purposeFieldDEK, func(dekBytes []byte) error {
		block, cipherErr := aes.NewCipher(dekBytes)
		if cipherErr != nil {
			return ErrInvalidInput
		}
		gcm, cipherErr := cipher.NewGCM(block)
		if cipherErr != nil {
			return ErrInvalidInput
		}
		return plaintext.withBytes(func(plaintextBytes []byte) error {
			ciphertext = gcm.Seal(nil, fieldNonce[:], plaintextBytes, fieldAADBytes)
			return nil
		})
	})
	if err != nil {
		return nil, err
	}

	fieldHash, err := fieldObjectHash(protocol.SuiteID, objectID, fieldNonce, fieldAADBytes, ciphertext)
	if err != nil {
		wipe(ciphertext)
		return nil, err
	}
	object := fieldObjectWire{
		FormatVersion: FieldFormatV2,
		SuiteID:       protocol.SuiteID,
		ObjectID:      objectID,
		Nonce:         fieldNonce,
		AAD:           fieldAADBytes,
		Ciphertext:    ciphertext,
		ContentHash:   fieldHash,
	}

	wrapAADBytes, err := encodeDomain(fieldAAD, envelopeID)
	if err != nil {
		wipe(ciphertext)
		return nil, err
	}
	wrapKey, err := deriveFieldEnvelopeKey(fieldRoot, context.CredentialID, context.CredentialVersion, context.FieldType, envelopeID)
	if err != nil {
		wipe(ciphertext)
		return nil, err
	}
	defer wrapKey.Destroy()

	var wrappedDEK []byte
	err = wrapKey.withPurposeBytes(purposeFieldEnvelope, func(wrapKeyBytes []byte) error {
		block, cipherErr := aes.NewCipher(wrapKeyBytes)
		if cipherErr != nil {
			return ErrInvalidInput
		}
		gcm, cipherErr := cipher.NewGCM(block)
		if cipherErr != nil {
			return ErrInvalidInput
		}
		return dek.withPurposeBytes(purposeFieldDEK, func(dekBytes []byte) error {
			wrappedDEK = gcm.Seal(nil, wrapNonce[:], dekBytes, wrapAADBytes)
			return nil
		})
	})
	if err != nil {
		wipe(ciphertext)
		return nil, err
	}

	envelopeHash, err := dekEnvelopeHash(
		protocol.SuiteID,
		envelopeID,
		objectID,
		wrapNonce,
		wrapAADBytes,
		wrappedDEK,
	)
	if err != nil {
		wipe(ciphertext)
		wipe(wrappedDEK)
		return nil, err
	}
	encrypted := &EncryptedField{
		object: object,
		dekEnvelope: dekEnvelopeWire{
			FormatVersion: FieldFormatV2,
			SuiteID:       protocol.SuiteID,
			EnvelopeID:    envelopeID,
			FieldObjectID: objectID,
			Nonce:         wrapNonce,
			AAD:           wrapAADBytes,
			WrappedDEK:    wrappedDEK,
			ContentHash:   envelopeHash,
		},
	}
	encoded, err := encrypted.MarshalBinary()
	if err != nil || len(encoded) > MaxEncryptedFieldSize {
		return nil, ErrInvalidInput
	}
	return encrypted, nil
}

// DecryptField validates both content hashes, the complete field context, the
// DEK envelope tag, and the field tag before returning any plaintext. All
// failures are collapsed to ErrRejectAEAD.
func DecryptField(fieldRoot *Key, expected FieldContext, encrypted *EncryptedField) (*Secret, error) {
	if fieldRoot == nil || encrypted == nil || validateFieldContext(expected) != nil || encrypted.validate() != nil ||
		fieldRoot.requirePurpose(purposeCredentialWrap) != nil {
		return nil, ErrRejectAEAD
	}

	var actualAAD FieldAAD
	if err := protocol.UnmarshalDeterministic(encrypted.object.AAD, &actualAAD); err != nil {
		return nil, ErrRejectAEAD
	}
	wantAAD := fieldAADFor(expected, encrypted.object.ObjectID)
	wantAADBytes, err := protocol.MarshalDeterministic(wantAAD)
	if err != nil || subtle.ConstantTimeCompare(wantAADBytes, encrypted.object.AAD) != 1 {
		return nil, ErrRejectAEAD
	}
	wantWrapAAD, err := encodeDomain(actualAAD, encrypted.dekEnvelope.EnvelopeID)
	if err != nil || subtle.ConstantTimeCompare(wantWrapAAD, encrypted.dekEnvelope.AAD) != 1 {
		return nil, ErrRejectAEAD
	}

	wrapKey, err := deriveFieldEnvelopeKey(
		fieldRoot,
		expected.CredentialID,
		expected.CredentialVersion,
		expected.FieldType,
		encrypted.dekEnvelope.EnvelopeID,
	)
	if err != nil {
		return nil, ErrRejectAEAD
	}
	defer wrapKey.Destroy()

	var dekBytes []byte
	err = wrapKey.withPurposeBytes(purposeFieldEnvelope, func(wrapKeyBytes []byte) error {
		block, cipherErr := aes.NewCipher(wrapKeyBytes)
		if cipherErr != nil {
			return ErrRejectAEAD
		}
		gcm, cipherErr := cipher.NewGCM(block)
		if cipherErr != nil {
			return ErrRejectAEAD
		}
		dekBytes, cipherErr = gcm.Open(
			nil,
			encrypted.dekEnvelope.Nonce[:],
			encrypted.dekEnvelope.WrappedDEK,
			encrypted.dekEnvelope.AAD,
		)
		if cipherErr != nil || len(dekBytes) != KeySize {
			wipe(dekBytes)
			dekBytes = nil
			return ErrRejectAEAD
		}
		return nil
	})
	if err != nil {
		return nil, ErrRejectAEAD
	}
	dek, err := newKeyWithPurpose(dekBytes, purposeFieldDEK)
	wipe(dekBytes)
	if err != nil {
		return nil, ErrRejectAEAD
	}
	defer dek.Destroy()

	var plaintext []byte
	err = dek.withPurposeBytes(purposeFieldDEK, func(keyBytes []byte) error {
		block, cipherErr := aes.NewCipher(keyBytes)
		if cipherErr != nil {
			return ErrRejectAEAD
		}
		gcm, cipherErr := cipher.NewGCM(block)
		if cipherErr != nil {
			return ErrRejectAEAD
		}
		plaintext, cipherErr = gcm.Open(
			nil,
			encrypted.object.Nonce[:],
			encrypted.object.Ciphertext,
			encrypted.object.AAD,
		)
		if cipherErr != nil {
			plaintext = nil
			return ErrRejectAEAD
		}
		return nil
	})
	if err != nil || len(plaintext) == 0 || len(plaintext) > MaxFieldPlaintextSize {
		wipe(plaintext)
		return nil, ErrRejectAEAD
	}
	secret, err := NewSecret(plaintext)
	wipe(plaintext)
	if err != nil {
		return nil, ErrRejectAEAD
	}
	return secret, nil
}

// DecryptFieldByReference reconstructs the original encryption context carried
// by a credential-version mapping. A credential v2 can therefore reuse a v1
// field object without falsely authenticating it as a v2 ciphertext.
func DecryptFieldByReference(
	fieldRoot *Key,
	namespaceID protocol.NamespaceID,
	credentialID protocol.CredentialID,
	reference FieldReference,
	encrypted *EncryptedField,
) (*Secret, error) {
	if encrypted == nil || reference.EncryptionVersion == 0 || reference.KeyGeneration == 0 || !reference.FieldType.Valid() {
		return nil, ErrRejectAEAD
	}
	actual, err := encrypted.Reference()
	if err != nil || actual != reference {
		return nil, ErrRejectAEAD
	}
	return DecryptField(fieldRoot, FieldContext{
		NamespaceID:       namespaceID,
		CredentialID:      credentialID,
		CredentialVersion: reference.EncryptionVersion,
		FieldType:         reference.FieldType,
		KeyGeneration:     reference.KeyGeneration,
		CryptoPolicyHash:  reference.CryptoPolicyHash,
		OriginBinding:     reference.OriginBinding,
	}, encrypted)
}

// MarshalBinary returns deterministic CBOR for content-addressed persistence.
func (encrypted *EncryptedField) MarshalBinary() ([]byte, error) {
	if encrypted == nil || encrypted.validate() != nil {
		return nil, ErrInvalidInput
	}
	encoded, err := protocol.MarshalDeterministic(encrypted.wire())
	if err != nil || len(encoded) > MaxEncryptedFieldSize {
		return nil, ErrInvalidInput
	}
	return encoded, nil
}

// ParseEncryptedField strictly parses and authenticates public metadata and
// content hashes. GCM authentication remains deferred until DecryptField.
func ParseEncryptedField(encoded []byte) (*EncryptedField, error) {
	if len(encoded) == 0 || len(encoded) > MaxEncryptedFieldSize {
		return nil, ErrRejectAEAD
	}
	var wire encryptedFieldWire
	if err := protocol.UnmarshalDeterministic(encoded, &wire); err != nil {
		return nil, ErrRejectAEAD
	}
	encrypted := encryptedFieldFromWire(wire)
	if encrypted.validate() != nil {
		return nil, ErrRejectAEAD
	}
	return encrypted, nil
}

// Clone returns a deep immutable copy.
func (encrypted *EncryptedField) Clone() *EncryptedField {
	if encrypted == nil {
		return nil
	}
	return encryptedFieldFromWire(encrypted.wire())
}

// Reference returns the stable IDs and content digests used by credential
// version mappings.
func (encrypted *EncryptedField) Reference() (FieldReference, error) {
	if encrypted == nil || encrypted.validate() != nil {
		return FieldReference{}, ErrInvalidInput
	}
	var aad FieldAAD
	if err := protocol.UnmarshalDeterministic(encrypted.object.AAD, &aad); err != nil {
		return FieldReference{}, ErrInvalidInput
	}
	return FieldReference{
		FieldType:         aad.FieldType,
		EncryptionVersion: aad.CredentialVersion,
		KeyGeneration:     aad.KeyGeneration,
		CryptoPolicyHash:  aad.CryptoPolicyHash,
		OriginBinding:     aad.OriginBinding,
		ObjectID:          encrypted.object.ObjectID,
		ObjectHash:        encrypted.object.ContentHash,
		EnvelopeID:        encrypted.dekEnvelope.EnvelopeID,
		EnvelopeHash:      encrypted.dekEnvelope.ContentHash,
	}, nil
}

// Context returns the authenticated public AAD projection. It contains no
// plaintext and lets a synchronization receiver reject cross-namespace,
// cross-credential and cross-version object substitution before decryption.
func (encrypted *EncryptedField) Context() (FieldContext, error) {
	if encrypted == nil || encrypted.validate() != nil {
		return FieldContext{}, ErrInvalidInput
	}
	var aad FieldAAD
	if err := protocol.UnmarshalDeterministic(encrypted.object.AAD, &aad); err != nil {
		return FieldContext{}, ErrInvalidInput
	}
	context := FieldContext{
		NamespaceID:       aad.NamespaceID,
		CredentialID:      aad.CredentialID,
		CredentialVersion: aad.CredentialVersion,
		FieldType:         aad.FieldType,
		KeyGeneration:     aad.KeyGeneration,
		CryptoPolicyHash:  aad.CryptoPolicyHash,
		OriginBinding:     aad.OriginBinding,
	}
	if validateFieldContext(context) != nil {
		return FieldContext{}, ErrInvalidInput
	}
	return context, nil
}

// EncodeFieldReference returns the canonical CP-2 field reference. It
// is the byte representation used by descriptor and field-digest commitments.
func EncodeFieldReference(reference FieldReference) ([]byte, error) {
	if !reference.FieldType.Valid() || reference.EncryptionVersion == 0 || reference.KeyGeneration == 0 ||
		allZeroBytes(reference.CryptoPolicyHash[:]) || allZeroBytes(reference.OriginBinding[:]) {
		return nil, ErrInvalidInput
	}
	encoded, err := protocol.MarshalDeterministic(reference)
	if err != nil {
		return nil, ErrInvalidInput
	}
	return encoded, nil
}

// FieldReferenceDigest commits to the exact canonical FieldReference bytes.
func FieldReferenceDigest(reference FieldReference) ([sha256.Size]byte, error) {
	encoded, err := EncodeFieldReference(reference)
	if err != nil {
		return [sha256.Size]byte{}, err
	}
	digest := sha256.Sum256(encoded)
	wipe(encoded)
	return digest, nil
}

// WrappedDEKProjection returns the encrypted DEK bytes and frozen suite name
// required by the credential-version mapping. The returned slice is a copy.
func (encrypted *EncryptedField) WrappedDEKProjection() ([]byte, string, error) {
	if encrypted == nil || encrypted.validate() != nil {
		return nil, "", ErrInvalidInput
	}
	return append([]byte(nil), encrypted.dekEnvelope.WrappedDEK...), encrypted.dekEnvelope.SuiteID, nil
}

func (encrypted *EncryptedField) validate() error {
	if encrypted == nil || encrypted.object.FormatVersion != FieldFormatV2 ||
		encrypted.dekEnvelope.FormatVersion != FieldFormatV2 ||
		encrypted.object.SuiteID != protocol.SuiteID || encrypted.dekEnvelope.SuiteID != protocol.SuiteID ||
		encrypted.object.ObjectID != encrypted.dekEnvelope.FieldObjectID ||
		len(encrypted.object.AAD) == 0 || len(encrypted.object.AAD) > maxEncodedEventAADLength ||
		len(encrypted.dekEnvelope.AAD) == 0 || len(encrypted.dekEnvelope.AAD) > maxEncodedEventAADLength ||
		len(encrypted.object.Ciphertext) < GCMTagSize || len(encrypted.object.Ciphertext) > MaxFieldPlaintextSize+GCMTagSize ||
		len(encrypted.dekEnvelope.WrappedDEK) != KeySize+GCMTagSize {
		return ErrRejectAEAD
	}

	var aad FieldAAD
	if err := protocol.UnmarshalDeterministic(encrypted.object.AAD, &aad); err != nil || validateFieldAAD(aad) != nil ||
		aad.FieldObjectID != encrypted.object.ObjectID {
		return ErrRejectAEAD
	}
	wantFieldHash, err := fieldObjectHash(
		encrypted.object.SuiteID,
		encrypted.object.ObjectID,
		encrypted.object.Nonce,
		encrypted.object.AAD,
		encrypted.object.Ciphertext,
	)
	if err != nil || subtle.ConstantTimeCompare(wantFieldHash[:], encrypted.object.ContentHash[:]) != 1 {
		return ErrRejectAEAD
	}
	wantWrapAAD, err := encodeDomain(aad, encrypted.dekEnvelope.EnvelopeID)
	if err != nil || subtle.ConstantTimeCompare(wantWrapAAD, encrypted.dekEnvelope.AAD) != 1 {
		return ErrRejectAEAD
	}
	wantEnvelopeHash, err := dekEnvelopeHash(
		encrypted.dekEnvelope.SuiteID,
		encrypted.dekEnvelope.EnvelopeID,
		encrypted.dekEnvelope.FieldObjectID,
		encrypted.dekEnvelope.Nonce,
		encrypted.dekEnvelope.AAD,
		encrypted.dekEnvelope.WrappedDEK,
	)
	if err != nil || subtle.ConstantTimeCompare(wantEnvelopeHash[:], encrypted.dekEnvelope.ContentHash[:]) != 1 {
		return ErrRejectAEAD
	}
	return nil
}

func (encrypted *EncryptedField) wire() encryptedFieldWire {
	return encryptedFieldWire{
		Object: fieldObjectWire{
			FormatVersion: encrypted.object.FormatVersion,
			SuiteID:       encrypted.object.SuiteID,
			ObjectID:      encrypted.object.ObjectID,
			Nonce:         encrypted.object.Nonce,
			AAD:           append([]byte(nil), encrypted.object.AAD...),
			Ciphertext:    append([]byte(nil), encrypted.object.Ciphertext...),
			ContentHash:   encrypted.object.ContentHash,
		},
		DEKEnvelope: dekEnvelopeWire{
			FormatVersion: encrypted.dekEnvelope.FormatVersion,
			SuiteID:       encrypted.dekEnvelope.SuiteID,
			EnvelopeID:    encrypted.dekEnvelope.EnvelopeID,
			FieldObjectID: encrypted.dekEnvelope.FieldObjectID,
			Nonce:         encrypted.dekEnvelope.Nonce,
			AAD:           append([]byte(nil), encrypted.dekEnvelope.AAD...),
			WrappedDEK:    append([]byte(nil), encrypted.dekEnvelope.WrappedDEK...),
			ContentHash:   encrypted.dekEnvelope.ContentHash,
		},
	}
}

func encryptedFieldFromWire(wire encryptedFieldWire) *EncryptedField {
	return (&EncryptedField{object: wire.Object, dekEnvelope: wire.DEKEnvelope}).deepCopy()
}

func (encrypted *EncryptedField) deepCopy() *EncryptedField {
	copyValue := *encrypted
	copyValue.object.AAD = append([]byte(nil), encrypted.object.AAD...)
	copyValue.object.Ciphertext = append([]byte(nil), encrypted.object.Ciphertext...)
	copyValue.dekEnvelope.AAD = append([]byte(nil), encrypted.dekEnvelope.AAD...)
	copyValue.dekEnvelope.WrappedDEK = append([]byte(nil), encrypted.dekEnvelope.WrappedDEK...)
	return &copyValue
}

func validateFieldContext(context FieldContext) error {
	if context.CredentialVersion == 0 || !context.FieldType.Valid() || context.KeyGeneration == 0 ||
		allZeroBytes(context.NamespaceID[:]) || allZeroBytes(context.CredentialID[:]) ||
		allZeroBytes(context.CryptoPolicyHash[:]) || allZeroBytes(context.OriginBinding[:]) {
		return ErrInvalidInput
	}
	return nil
}

func fieldAADFor(context FieldContext, objectID FieldObjectID) FieldAAD {
	return FieldAAD{
		ProtocolID:        protocol.ProtocolID,
		ProtocolVersion:   protocol.ProtocolVersion,
		SuiteID:           protocol.SuiteID,
		NamespaceID:       context.NamespaceID,
		CredentialID:      context.CredentialID,
		CredentialVersion: context.CredentialVersion,
		EncryptionVersion: FieldFormatV2,
		FieldType:         context.FieldType,
		FieldObjectID:     objectID,
		KeyGeneration:     context.KeyGeneration,
		CryptoPolicyHash:  context.CryptoPolicyHash,
		OriginBinding:     context.OriginBinding,
	}
}

func validateFieldAAD(aad FieldAAD) error {
	if aad.ProtocolID != protocol.ProtocolID ||
		aad.ProtocolVersion != protocol.ProtocolVersion || aad.SuiteID != protocol.SuiteID ||
		aad.CredentialVersion == 0 || aad.EncryptionVersion != FieldFormatV2 ||
		!aad.FieldType.Valid() || aad.KeyGeneration == 0 ||
		allZeroBytes(aad.NamespaceID[:]) || allZeroBytes(aad.CredentialID[:]) ||
		allZeroBytes(aad.CryptoPolicyHash[:]) || allZeroBytes(aad.OriginBinding[:]) {
		return ErrRejectAEAD
	}
	return nil
}

func fieldObjectHash(
	suiteID string,
	objectID FieldObjectID,
	nonce [GCMNonceSize]byte,
	aad []byte,
	ciphertext []byte,
) ([sha256.Size]byte, error) {
	encoded, err := encodeDomain(protocol.DomainPrefix+"FIELD-OBJECT", suiteID, FieldFormatV2, objectID, nonce, aad, ciphertext)
	if err != nil {
		return [sha256.Size]byte{}, ErrInvalidInput
	}
	digest := sha256.Sum256(encoded)
	wipe(encoded)
	return digest, nil
}

func dekEnvelopeHash(
	suiteID string,
	envelopeID FieldEnvelopeID,
	fieldObjectID FieldObjectID,
	nonce [GCMNonceSize]byte,
	aad []byte,
	wrappedDEK []byte,
) ([sha256.Size]byte, error) {
	encoded, err := encodeDomain(
		protocol.DomainPrefix+"FIELD-DEK-ENVELOPE",
		suiteID,
		FieldFormatV2,
		envelopeID,
		fieldObjectID,
		nonce,
		aad,
		wrappedDEK,
	)
	if err != nil {
		return [sha256.Size]byte{}, ErrInvalidInput
	}
	digest := sha256.Sum256(encoded)
	wipe(encoded)
	return digest, nil
}

func allZeroBytes(input []byte) bool {
	var combined byte
	for _, value := range input {
		combined |= value
	}
	return combined == 0
}
