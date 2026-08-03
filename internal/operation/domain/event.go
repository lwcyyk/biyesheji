// Package domain contains the infrastructure-independent operation event
// model. Signed events are immutable: their canonical SigInput bytes and
// signature are the exact bytes persisted and later published.
package domain

import (
	"crypto/ed25519"
	"crypto/sha256"
	"crypto/subtle"
	"errors"

	"vpass.local/vpass/internal/cryptokit"
	"vpass.local/vpass/internal/protocol"
)

var (
	ErrInvalidEvent      = errors.New("invalid operation event")
	ErrEventContext      = errors.New("operation event context mismatch")
	ErrEventVerification = errors.New("operation event signature verification failed")
)

// Payload is the canonical, signed operation event payload. Nullable values
// are represented as CBOR null; zero is never overloaded as absence.
type Payload struct {
	EventID                protocol.EventID                    `cbor:"event_id"`
	NamespaceID            protocol.NamespaceID                `cbor:"namespace_id"`
	DeviceID               protocol.DeviceID                   `cbor:"device_id"`
	DeviceCredentialHash   [sha256.Size]byte                   `cbor:"device_credential_hash"`
	CredentialID           *protocol.CredentialID              `cbor:"credential_id"`
	OperationType          protocol.OperationType              `cbor:"operation_type"`
	OldVersion             *uint64                             `cbor:"old_version"`
	NewVersion             *uint64                             `cbor:"new_version"`
	DevicePseudonym        [cryptokit.DevicePseudonymSize]byte `cbor:"device_pseudonym"`
	OriginCommitment       *[sha256.Size]byte                  `cbor:"origin_commitment"`
	EventPayloadHash       [sha256.Size]byte                   `cbor:"event_payload_hash"`
	VRFEpoch               *uint64                             `cbor:"vrf_epoch"`
	SecretGeneration       uint64                              `cbor:"secret_generation"`
	DeviceCounter          uint64                              `cbor:"device_counter"`
	PreviousEventHash      *[sha256.Size]byte                  `cbor:"previous_event_hash"`
	ObservedAtMilliseconds *uint64                             `cbor:"observed_at_ms"`
}

// Validate enforces invariants independent of repository state. Counter
// continuity and the exact previous digest are checked in the transaction
// that advances the device counter.
func (payload Payload) Validate() error {
	if !payload.OperationType.Valid() || payload.SecretGeneration == 0 || payload.DeviceCounter == 0 {
		return ErrInvalidEvent
	}
	for _, version := range []*uint64{payload.OldVersion, payload.NewVersion} {
		if version != nil && *version == 0 {
			return ErrInvalidEvent
		}
	}
	if payload.DeviceCounter == 1 {
		if payload.PreviousEventHash != nil {
			return ErrInvalidEvent
		}
	} else if payload.PreviousEventHash == nil {
		return ErrInvalidEvent
	}
	if payload.OperationType == protocol.OperationCreate {
		if payload.CredentialID == nil || payload.OldVersion != nil || payload.NewVersion == nil || *payload.NewVersion != 1 {
			return ErrInvalidEvent
		}
	}
	return nil
}

// SignedEvent owns the canonical encoded SigInput and its signature.
type SignedEvent struct {
	payload   Payload
	sigInput  []byte
	signature protocol.Signature
	digest    [sha256.Size]byte
}

// Sign constructs and signs one canonical operation event.
func Sign(
	privateKey ed25519.PrivateKey,
	chainID string,
	signingKeyGeneration uint64,
	payload Payload,
) (*SignedEvent, error) {
	if err := payload.Validate(); err != nil {
		return nil, err
	}
	if len(privateKey) != ed25519.PrivateKeySize {
		return nil, ErrInvalidEvent
	}
	publicKey, ok := privateKey.Public().(ed25519.PublicKey)
	if !ok {
		return nil, ErrInvalidEvent
	}
	keyID, err := protocol.KeyIDFromPublicKey(publicKey)
	if err != nil {
		return nil, err
	}
	payloadCBOR, err := protocol.MarshalDeterministic(payload)
	if err != nil {
		return nil, ErrInvalidEvent
	}
	input := protocol.NewSigInput(
		protocol.ObjectTypeOperationEvent,
		chainID,
		payload.NamespaceID,
		keyID,
		signingKeyGeneration,
		payloadCBOR,
	)
	signature, err := protocol.Sign(privateKey, input)
	if err != nil {
		return nil, err
	}
	encoded, err := protocol.EncodeSigInput(input)
	if err != nil {
		return nil, err
	}
	return newSignedEvent(payload, encoded, signature), nil
}

// ParseAndVerify verifies the receiver-supplied trust context before exposing
// the strongly typed payload.
func ParseAndVerify(
	encodedSigInput []byte,
	signature protocol.Signature,
	publicKey ed25519.PublicKey,
	expected protocol.VerificationContext,
) (*SignedEvent, error) {
	var input protocol.SigInput
	if err := protocol.UnmarshalDeterministic(encodedSigInput, &input); err != nil {
		return nil, ErrInvalidEvent
	}
	if err := protocol.Verify(publicKey, input, signature, expected); err != nil {
		return nil, errors.Join(ErrEventVerification, err)
	}
	if input.ObjectType != protocol.ObjectTypeOperationEvent {
		return nil, ErrEventContext
	}
	var payload Payload
	if err := protocol.UnmarshalDeterministic(input.Payload, &payload); err != nil || payload.Validate() != nil {
		return nil, ErrInvalidEvent
	}
	if subtle.ConstantTimeCompare(payload.NamespaceID[:], input.NamespaceID[:]) != 1 {
		return nil, ErrEventContext
	}
	canonical, err := protocol.EncodeSigInput(input)
	if err != nil || subtle.ConstantTimeCompare(canonical, encodedSigInput) != 1 {
		return nil, ErrInvalidEvent
	}
	return newSignedEvent(payload, canonical, signature), nil
}

func newSignedEvent(payload Payload, encoded []byte, signature protocol.Signature) *SignedEvent {
	hasher := sha256.New()
	_, _ = hasher.Write(encoded)
	_, _ = hasher.Write(signature[:])
	var digest [sha256.Size]byte
	copy(digest[:], hasher.Sum(nil))
	return &SignedEvent{
		payload:   clonePayload(payload),
		sigInput:  append([]byte(nil), encoded...),
		signature: signature,
		digest:    digest,
	}
}

// Payload returns a defensive copy of the signed projection.
func (event *SignedEvent) Payload() Payload {
	if event == nil {
		return Payload{}
	}
	return clonePayload(event.payload)
}

// SigInputCBOR returns the exact canonical bytes covered by the signature.
func (event *SignedEvent) SigInputCBOR() []byte {
	if event == nil {
		return nil
	}
	return append([]byte(nil), event.sigInput...)
}

// Signature returns the fixed-size signature by value.
func (event *SignedEvent) Signature() protocol.Signature {
	if event == nil {
		return protocol.Signature{}
	}
	return event.signature
}

// Digest is SHA-256(canonical SigInput bytes || signature bytes).
func (event *SignedEvent) Digest() [sha256.Size]byte {
	if event == nil {
		return [sha256.Size]byte{}
	}
	return event.digest
}

func clonePayload(payload Payload) Payload {
	cloned := payload
	if payload.CredentialID != nil {
		value := *payload.CredentialID
		cloned.CredentialID = &value
	}
	if payload.OldVersion != nil {
		value := *payload.OldVersion
		cloned.OldVersion = &value
	}
	if payload.NewVersion != nil {
		value := *payload.NewVersion
		cloned.NewVersion = &value
	}
	if payload.OriginCommitment != nil {
		value := *payload.OriginCommitment
		cloned.OriginCommitment = &value
	}
	if payload.VRFEpoch != nil {
		value := *payload.VRFEpoch
		cloned.VRFEpoch = &value
	}
	if payload.PreviousEventHash != nil {
		value := *payload.PreviousEventHash
		cloned.PreviousEventHash = &value
	}
	if payload.ObservedAtMilliseconds != nil {
		value := *payload.ObservedAtMilliseconds
		cloned.ObservedAtMilliseconds = &value
	}
	return cloned
}
