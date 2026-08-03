package domain

import (
	"crypto/sha256"
	"crypto/subtle"
	"errors"
	"sort"

	"vpass.local/vpass/internal/cryptokit"
	"vpass.local/vpass/internal/protocol"
)

var (
	ErrInvalidCredentialEnvelope = errors.New("invalid credential envelope")
	ErrCredentialEnvelopeContext = errors.New("credential envelope context mismatch")
)

// EnvelopeFieldReference is the public, non-secret projection used to locate
// and authenticate a ciphertext object and its independently wrapped DEK.
// FieldCommitment is all-zero when plaintext commitment disclosure is disabled.
type EnvelopeFieldReference struct {
	FieldType         cryptokit.FieldType `cbor:"field_type"`
	EncryptionVersion uint64              `cbor:"encryption_version"`
	CiphertextDigest  [sha256.Size]byte   `cbor:"ciphertext_digest"`
	WrappedKeyDigest  [sha256.Size]byte   `cbor:"wrapped_key_digest"`
	FieldCommitment   [sha256.Size]byte   `cbor:"field_commitment"`
}

type credentialEnvelopeWire struct {
	ProtocolID        string                   `cbor:"protocol_id"`
	ProtocolVersion   uint64                   `cbor:"protocol_version"`
	SuiteID           string                   `cbor:"suite_id"`
	NamespaceID       protocol.NamespaceID     `cbor:"namespace_id"`
	CredentialID      protocol.CredentialID    `cbor:"credential_id"`
	CredentialVersion uint64                   `cbor:"credential_version"`
	Fields            []EnvelopeFieldReference `cbor:"fields"`
	OriginBinding     [sha256.Size]byte        `cbor:"origin_binding"`
	DescriptorHash    [sha256.Size]byte        `cbor:"descriptor_hash"`
	CryptoPolicyHash  [sha256.Size]byte        `cbor:"crypto_policy_hash"`
}

// CredentialEnvelope is an immutable deterministic control object. It never
// embeds a domain, account name, password or wrapped key bytes.
type CredentialEnvelope struct {
	wire    credentialEnvelopeWire
	encoded []byte
	digest  [sha256.Size]byte
}

// NewCredentialEnvelope binds an already validated VersionDraft to its
// namespace and Origin. The descriptor hash is the immutable VersionDraft
// binding hash, not a StateDescriptor hash, which avoids circular references.
func NewCredentialEnvelope(
	namespaceID protocol.NamespaceID,
	draft *VersionDraft,
	originBinding [sha256.Size]byte,
) (*CredentialEnvelope, error) {
	if draft == nil || allZero(namespaceID[:]) || allZero(originBinding[:]) {
		return nil, ErrInvalidCredentialEnvelope
	}
	fields := draft.Fields()
	if len(fields) < 1 || len(fields) > 6 {
		return nil, ErrInvalidCredentialEnvelope
	}
	wireFields := make([]EnvelopeFieldReference, 0, len(fields))
	policyHash := draft.PolicyHash()
	for _, field := range fields {
		reference := field.Reference()
		if subtle.ConstantTimeCompare(reference.OriginBinding[:], originBinding[:]) != 1 ||
			subtle.ConstantTimeCompare(reference.CryptoPolicyHash[:], policyHash[:]) != 1 {
			return nil, ErrCredentialEnvelopeContext
		}
		wireFields = append(wireFields, EnvelopeFieldReference{
			FieldType:         reference.FieldType,
			EncryptionVersion: reference.EncryptionVersion,
			CiphertextDigest:  reference.ObjectHash,
			WrappedKeyDigest:  reference.EnvelopeHash,
			// A plaintext commitment is deliberately omitted for CP-2. In
			// particular, low-entropy password hashes must never be exposed.
			FieldCommitment: [sha256.Size]byte{},
		})
	}
	sort.Slice(wireFields, func(i, j int) bool {
		return wireFields[i].FieldType < wireFields[j].FieldType
	})
	wire := credentialEnvelopeWire{
		ProtocolID:        protocol.ProtocolID,
		ProtocolVersion:   protocol.ProtocolVersion,
		SuiteID:           protocol.SuiteID,
		NamespaceID:       namespaceID,
		CredentialID:      draft.CredentialID(),
		CredentialVersion: draft.Version(),
		Fields:            wireFields,
		OriginBinding:     originBinding,
		DescriptorHash:    draft.DescriptorHash(),
		CryptoPolicyHash:  policyHash,
	}
	return buildCredentialEnvelope(wire)
}

// ParseCredentialEnvelope strictly parses canonical CP-2 CBOR and validates
// all field ordering and context-independent invariants.
func ParseCredentialEnvelope(encoded []byte) (*CredentialEnvelope, error) {
	var wire credentialEnvelopeWire
	if err := protocol.UnmarshalDeterministic(encoded, &wire); err != nil {
		return nil, errors.Join(ErrInvalidCredentialEnvelope, err)
	}
	envelope, err := buildCredentialEnvelope(wire)
	if err != nil {
		return nil, err
	}
	if subtle.ConstantTimeCompare(envelope.encoded, encoded) != 1 {
		return nil, ErrInvalidCredentialEnvelope
	}
	return envelope, nil
}

func buildCredentialEnvelope(wire credentialEnvelopeWire) (*CredentialEnvelope, error) {
	if wire.ProtocolID != protocol.ProtocolID || wire.ProtocolVersion != protocol.ProtocolVersion ||
		wire.SuiteID != protocol.SuiteID || allZero(wire.NamespaceID[:]) ||
		allZero(wire.CredentialID[:]) || wire.CredentialVersion == 0 ||
		len(wire.Fields) < 1 || len(wire.Fields) > 6 ||
		allZero(wire.OriginBinding[:]) || allZero(wire.DescriptorHash[:]) ||
		allZero(wire.CryptoPolicyHash[:]) {
		return nil, ErrInvalidCredentialEnvelope
	}
	fields := append([]EnvelopeFieldReference(nil), wire.Fields...)
	hasPassword := false
	var previous cryptokit.FieldType
	for _, field := range fields {
		if !field.FieldType.Valid() || field.FieldType <= previous ||
			field.EncryptionVersion == 0 || field.EncryptionVersion > wire.CredentialVersion ||
			allZero(field.CiphertextDigest[:]) || allZero(field.WrappedKeyDigest[:]) {
			return nil, ErrInvalidCredentialEnvelope
		}
		previous = field.FieldType
		hasPassword = hasPassword || field.FieldType == cryptokit.FieldPassword
	}
	if !hasPassword {
		return nil, ErrInvalidCredentialEnvelope
	}
	wire.Fields = fields
	encoded, err := protocol.MarshalDeterministic(wire)
	if err != nil {
		return nil, errors.Join(ErrInvalidCredentialEnvelope, err)
	}
	return &CredentialEnvelope{
		wire:    wire,
		encoded: encoded,
		digest:  sha256.Sum256(encoded),
	}, nil
}

func (envelope *CredentialEnvelope) NamespaceID() protocol.NamespaceID {
	if envelope == nil {
		return protocol.NamespaceID{}
	}
	return envelope.wire.NamespaceID
}

func (envelope *CredentialEnvelope) CredentialID() protocol.CredentialID {
	if envelope == nil {
		return protocol.CredentialID{}
	}
	return envelope.wire.CredentialID
}

func (envelope *CredentialEnvelope) Version() uint64 {
	if envelope == nil {
		return 0
	}
	return envelope.wire.CredentialVersion
}

func (envelope *CredentialEnvelope) OriginBinding() [sha256.Size]byte {
	if envelope == nil {
		return [sha256.Size]byte{}
	}
	return envelope.wire.OriginBinding
}

func (envelope *CredentialEnvelope) DescriptorBindingHash() [sha256.Size]byte {
	if envelope == nil {
		return [sha256.Size]byte{}
	}
	return envelope.wire.DescriptorHash
}

func (envelope *CredentialEnvelope) PolicyHash() [sha256.Size]byte {
	if envelope == nil {
		return [sha256.Size]byte{}
	}
	return envelope.wire.CryptoPolicyHash
}

func (envelope *CredentialEnvelope) Fields() []EnvelopeFieldReference {
	if envelope == nil {
		return nil
	}
	return append([]EnvelopeFieldReference(nil), envelope.wire.Fields...)
}

func (envelope *CredentialEnvelope) MarshalBinary() ([]byte, error) {
	if envelope == nil || len(envelope.encoded) == 0 {
		return nil, ErrInvalidCredentialEnvelope
	}
	return append([]byte(nil), envelope.encoded...), nil
}

func (envelope *CredentialEnvelope) Digest() [sha256.Size]byte {
	if envelope == nil {
		return [sha256.Size]byte{}
	}
	return envelope.digest
}
