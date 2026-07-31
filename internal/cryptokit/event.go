package cryptokit

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/sha256"
	"crypto/subtle"

	"vdns.local/vdns/internal/protocol"
)

const (
	GCMNonceSize             = 12
	GCMTagSize               = 16
	MaxEventPlaintextSize    = 64 * 1024
	MaxEventEnvelopeSize     = 128 * 1024
	EventEnvelopeFormatV1    = uint64(1)
	maxEncodedEventAADLength = 4096
)

// EventContext contains the caller-supplied context for one encrypted usage
// event. Protocol/suite identifiers and ciphertext length are added by the
// cryptographic boundary and cannot be overridden by callers.
type EventContext struct {
	NamespaceID     protocol.NamespaceID
	EventID         protocol.EventID
	ObjectType      protocol.ObjectType
	DevicePseudonym [DevicePseudonymSize]byte
	KeyGeneration   uint64
	VRFEpoch        uint64
}

// EventAAD is the complete authenticated event context frozen by CP-2.
type EventAAD struct {
	ProtocolVersion  uint64                    `cbor:"protocol_version"`
	SuiteID          string                    `cbor:"suite_id"`
	NamespaceID      protocol.NamespaceID      `cbor:"namespace_id"`
	EventID          protocol.EventID          `cbor:"event_id"`
	ObjectType       protocol.ObjectType       `cbor:"object_type"`
	DevicePseudonym  [DevicePseudonymSize]byte `cbor:"device_pseudonym"`
	KeyGeneration    uint64                    `cbor:"key_generation"`
	VRFEpoch         uint64                    `cbor:"vrf_epoch"`
	CiphertextLength uint64                    `cbor:"ciphertext_length"`
}

// EventEnvelope is an immutable value object. Accessors and serialization
// return copies, allowing retry workers to resend exactly the originally
// persisted nonce, AAD, ciphertext, and digest.
type EventEnvelope struct {
	formatVersion uint64
	suiteID       string
	nonce         [GCMNonceSize]byte
	aad           []byte
	ciphertext    []byte
	payloadHash   [sha256.Size]byte
}

type eventEnvelopeWire struct {
	FormatVersion uint64             `cbor:"format_version"`
	SuiteID       string             `cbor:"suite_id"`
	Nonce         [GCMNonceSize]byte `cbor:"nonce"`
	AAD           []byte             `cbor:"aad"`
	Ciphertext    []byte             `cbor:"ciphertext"`
	PayloadHash   [sha256.Size]byte  `cbor:"payload_hash"`
}

// SealEvent encrypts one new event with OS CSPRNG entropy.
func SealEvent(key *Key, context EventContext, plaintext *Secret) (*EventEnvelope, error) {
	return SealEventWithEntropy(key, context, plaintext, SystemEntropySource())
}

// SealEventWithEntropy encrypts one new event using an explicitly
// production-safe source. Test-only or nil sources are rejected.
func SealEventWithEntropy(
	key *Key,
	context EventContext,
	plaintext *Secret,
	source EntropySource,
) (*EventEnvelope, error) {
	reader, err := source.productionReader()
	if err != nil {
		return nil, err
	}
	return sealEventWithReader(key, context, plaintext, reader)
}

func sealEventWithReader(
	key *Key,
	context EventContext,
	plaintext *Secret,
	randomReader interface{ Read([]byte) (int, error) },
) (*EventEnvelope, error) {
	if key == nil || plaintext == nil || plaintext.Len() == 0 || plaintext.Len() > MaxEventPlaintextSize {
		return nil, ErrInvalidInput
	}
	if err := key.requirePurpose(purposeEvent); err != nil {
		return nil, err
	}
	if err := validateEventContext(context); err != nil {
		return nil, err
	}

	var nonce [GCMNonceSize]byte
	if err := fillRandom(randomReader, nonce[:]); err != nil {
		return nil, err
	}

	var envelope *EventEnvelope
	err := key.withPurposeBytes(purposeEvent, func(keyBytes []byte) error {
		block, err := aes.NewCipher(keyBytes)
		if err != nil {
			return ErrInvalidInput
		}
		gcm, err := cipher.NewGCM(block)
		if err != nil {
			return ErrInvalidInput
		}

		return plaintext.withBytes(func(plaintextBytes []byte) error {
			ciphertextLength := len(plaintextBytes) + gcm.Overhead()
			aadObject := eventAADFor(context, uint64(ciphertextLength))
			aad, err := protocol.MarshalDeterministic(aadObject)
			if err != nil || len(aad) > maxEncodedEventAADLength {
				return ErrInvalidInput
			}
			ciphertext := gcm.Seal(nil, nonce[:], plaintextBytes, aad)
			payloadHash, err := eventPayloadHash(protocol.SuiteID, nonce, aad, ciphertext)
			if err != nil {
				wipe(ciphertext)
				return err
			}
			envelope = &EventEnvelope{
				formatVersion: EventEnvelopeFormatV1,
				suiteID:       protocol.SuiteID,
				nonce:         nonce,
				aad:           aad,
				ciphertext:    ciphertext,
				payloadHash:   payloadHash,
			}
			encoded, err := envelope.MarshalBinary()
			if err != nil || len(encoded) > MaxEventEnvelopeSize {
				envelope = nil
				return ErrInvalidInput
			}
			return nil
		})
	})
	wipe(nonce[:])
	if err != nil {
		return nil, err
	}
	return envelope, nil
}

// OpenEvent validates the immutable envelope, its digest, all expected
// context, and its GCM tag before returning any plaintext. Every failure is
// collapsed to ErrRejectAEAD.
func OpenEvent(key *Key, expected EventContext, envelope *EventEnvelope) (*Secret, error) {
	if key == nil || envelope == nil || validateEventContext(expected) != nil || envelope.validate() != nil ||
		key.requirePurpose(purposeEvent) != nil {
		return nil, ErrRejectAEAD
	}
	expectedAAD := eventAADFor(expected, uint64(len(envelope.ciphertext)))
	expectedAADBytes, err := protocol.MarshalDeterministic(expectedAAD)
	if err != nil || subtle.ConstantTimeCompare(expectedAADBytes, envelope.aad) != 1 {
		return nil, ErrRejectAEAD
	}

	var plaintext []byte
	err = key.withPurposeBytes(purposeEvent, func(keyBytes []byte) error {
		block, cipherErr := aes.NewCipher(keyBytes)
		if cipherErr != nil {
			return ErrRejectAEAD
		}
		gcm, cipherErr := cipher.NewGCM(block)
		if cipherErr != nil {
			return ErrRejectAEAD
		}
		plaintext, cipherErr = gcm.Open(nil, envelope.nonce[:], envelope.ciphertext, envelope.aad)
		if cipherErr != nil {
			plaintext = nil
			return ErrRejectAEAD
		}
		return nil
	})
	if err != nil || len(plaintext) == 0 || len(plaintext) > MaxEventPlaintextSize {
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

// MarshalBinary returns the deterministic CBOR envelope bytes used for
// persistence and identical network retries.
func (envelope *EventEnvelope) MarshalBinary() ([]byte, error) {
	if envelope == nil || envelope.validate() != nil {
		return nil, ErrInvalidInput
	}
	encoded, err := protocol.MarshalDeterministic(envelope.wire())
	if err != nil || len(encoded) > MaxEventEnvelopeSize {
		return nil, ErrInvalidInput
	}
	return encoded, nil
}

// ParseEventEnvelope strictly parses a deterministic-CBOR persisted envelope.
func ParseEventEnvelope(encoded []byte) (*EventEnvelope, error) {
	if len(encoded) == 0 || len(encoded) > MaxEventEnvelopeSize {
		return nil, ErrRejectAEAD
	}
	var wire eventEnvelopeWire
	if err := protocol.UnmarshalDeterministic(encoded, &wire); err != nil {
		return nil, ErrRejectAEAD
	}
	envelope := eventEnvelopeFromWire(wire)
	if envelope.validate() != nil {
		return nil, ErrRejectAEAD
	}
	return envelope, nil
}

// Clone returns a deep immutable retry copy.
func (envelope *EventEnvelope) Clone() *EventEnvelope {
	if envelope == nil {
		return nil
	}
	return eventEnvelopeFromWire(envelope.wire())
}

// PayloadHash returns the content digest by value.
func (envelope *EventEnvelope) PayloadHash() [sha256.Size]byte {
	if envelope == nil {
		return [sha256.Size]byte{}
	}
	return envelope.payloadHash
}

// CiphertextLength returns ciphertext-plus-tag length without exposing bytes.
func (envelope *EventEnvelope) CiphertextLength() int {
	if envelope == nil {
		return 0
	}
	return len(envelope.ciphertext)
}

func (envelope *EventEnvelope) validate() error {
	if envelope == nil || envelope.formatVersion != EventEnvelopeFormatV1 ||
		envelope.suiteID != protocol.SuiteID || len(envelope.aad) == 0 ||
		len(envelope.aad) > maxEncodedEventAADLength || len(envelope.ciphertext) < GCMTagSize ||
		len(envelope.ciphertext) > MaxEventPlaintextSize+GCMTagSize {
		return ErrRejectAEAD
	}
	var aad EventAAD
	if err := protocol.UnmarshalDeterministic(envelope.aad, &aad); err != nil || validateEventAAD(aad) != nil ||
		aad.CiphertextLength != uint64(len(envelope.ciphertext)) {
		return ErrRejectAEAD
	}
	wantHash, err := eventPayloadHash(envelope.suiteID, envelope.nonce, envelope.aad, envelope.ciphertext)
	if err != nil || subtle.ConstantTimeCompare(wantHash[:], envelope.payloadHash[:]) != 1 {
		return ErrRejectAEAD
	}
	return nil
}

func (envelope *EventEnvelope) wire() eventEnvelopeWire {
	return eventEnvelopeWire{
		FormatVersion: envelope.formatVersion,
		SuiteID:       envelope.suiteID,
		Nonce:         envelope.nonce,
		AAD:           append([]byte(nil), envelope.aad...),
		Ciphertext:    append([]byte(nil), envelope.ciphertext...),
		PayloadHash:   envelope.payloadHash,
	}
}

func eventEnvelopeFromWire(wire eventEnvelopeWire) *EventEnvelope {
	return &EventEnvelope{
		formatVersion: wire.FormatVersion,
		suiteID:       wire.SuiteID,
		nonce:         wire.Nonce,
		aad:           append([]byte(nil), wire.AAD...),
		ciphertext:    append([]byte(nil), wire.Ciphertext...),
		payloadHash:   wire.PayloadHash,
	}
}

func validateEventContext(context EventContext) error {
	if context.ObjectType != protocol.ObjectTypeOperationEvent || context.KeyGeneration == 0 {
		return ErrInvalidInput
	}
	return nil
}

func eventAADFor(context EventContext, ciphertextLength uint64) EventAAD {
	return EventAAD{
		ProtocolVersion:  protocol.ProtocolVersion,
		SuiteID:          protocol.SuiteID,
		NamespaceID:      context.NamespaceID,
		EventID:          context.EventID,
		ObjectType:       context.ObjectType,
		DevicePseudonym:  context.DevicePseudonym,
		KeyGeneration:    context.KeyGeneration,
		VRFEpoch:         context.VRFEpoch,
		CiphertextLength: ciphertextLength,
	}
}

func validateEventAAD(aad EventAAD) error {
	if aad.ProtocolVersion != protocol.ProtocolVersion || aad.SuiteID != protocol.SuiteID ||
		aad.ObjectType != protocol.ObjectTypeOperationEvent || aad.KeyGeneration == 0 ||
		aad.CiphertextLength < GCMTagSize || aad.CiphertextLength > MaxEventPlaintextSize+GCMTagSize {
		return ErrRejectAEAD
	}
	return nil
}

func eventPayloadHash(
	suiteID string,
	nonce [GCMNonceSize]byte,
	aad []byte,
	ciphertext []byte,
) ([sha256.Size]byte, error) {
	encoded, err := encodeDomain(suiteID, nonce, aad, ciphertext)
	if err != nil {
		return [sha256.Size]byte{}, ErrInvalidInput
	}
	digest := sha256.Sum256(encoded)
	wipe(encoded)
	return digest, nil
}
