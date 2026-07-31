package domain

import (
	"crypto/ed25519"
	"crypto/sha256"
	"crypto/subtle"
	"errors"

	"vdns.local/vdns/internal/protocol"
)

var (
	ErrInvalidStateDescriptor      = errors.New("invalid credential state descriptor")
	ErrStateDescriptorContext      = errors.New("credential state descriptor context mismatch")
	ErrStateDescriptorVerification = errors.New("credential state descriptor signature verification failed")
)

// StateDescriptorPayload is the exact signed state projection. The signature
// remains in the universal SigInput wrapper so protocol, suite, chain,
// namespace, key ID and key generation are all signed as well.
type StateDescriptorPayload struct {
	NamespaceID            protocol.NamespaceID     `cbor:"namespace_id"`
	CredentialID           protocol.CredentialID    `cbor:"credential_id"`
	ActiveVersion          uint64                   `cbor:"active_version"`
	ActiveEnvelopeHash     [sha256.Size]byte        `cbor:"active_envelope_hash"`
	PreviousDescriptorHash *[sha256.Size]byte       `cbor:"previous_descriptor_hash"`
	LifecycleStatus        protocol.LifecycleStatus `cbor:"lifecycle_status"`
	LastOperationEvent     [sha256.Size]byte        `cbor:"last_operation_event"`
	AuthorizedDeviceRoot   [sha256.Size]byte        `cbor:"authorized_device_set_root"`
	AuditCheckpoint        [sha256.Size]byte        `cbor:"audit_checkpoint"`
	FinalSequence          uint64                   `cbor:"final_sequence"`
	UpdaterDeviceID        protocol.DeviceID        `cbor:"updater_device_id"`
}

// SignedStateDescriptor owns the canonical SigInput and signature bytes.
type SignedStateDescriptor struct {
	payload   StateDescriptorPayload
	sigInput  []byte
	signature protocol.Signature
	digest    [sha256.Size]byte
}

type signedStateDescriptorWire struct {
	SigInputCBOR []byte             `cbor:"sig_input_cbor"`
	Signature    protocol.Signature `cbor:"signature"`
}

// SignStateDescriptor signs one validated state transition projection.
func SignStateDescriptor(
	privateKey ed25519.PrivateKey,
	chainID string,
	keyGeneration uint64,
	payload StateDescriptorPayload,
) (*SignedStateDescriptor, error) {
	if validateStateDescriptorPayload(payload) != nil || len(privateKey) != ed25519.PrivateKeySize {
		return nil, ErrInvalidStateDescriptor
	}
	publicKey, ok := privateKey.Public().(ed25519.PublicKey)
	if !ok {
		return nil, ErrInvalidStateDescriptor
	}
	keyID, err := protocol.KeyIDFromPublicKey(publicKey)
	if err != nil {
		return nil, ErrInvalidStateDescriptor
	}
	payloadCBOR, err := protocol.MarshalDeterministic(payload)
	if err != nil {
		return nil, errors.Join(ErrInvalidStateDescriptor, err)
	}
	input := protocol.NewSigInput(
		protocol.ObjectTypeStateDescriptor,
		chainID,
		payload.NamespaceID,
		keyID,
		keyGeneration,
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
	return newSignedStateDescriptor(payload, encoded, signature), nil
}

// ParseAndVerifyStateDescriptor verifies receiver-owned trust context before
// exposing the signed state.
func ParseAndVerifyStateDescriptor(
	encodedSigInput []byte,
	signature protocol.Signature,
	publicKey ed25519.PublicKey,
	expected protocol.VerificationContext,
) (*SignedStateDescriptor, error) {
	var input protocol.SigInput
	if err := protocol.UnmarshalDeterministic(encodedSigInput, &input); err != nil {
		return nil, ErrInvalidStateDescriptor
	}
	if err := protocol.Verify(publicKey, input, signature, expected); err != nil {
		return nil, errors.Join(ErrStateDescriptorVerification, err)
	}
	if input.ObjectType != protocol.ObjectTypeStateDescriptor {
		return nil, ErrStateDescriptorContext
	}
	var payload StateDescriptorPayload
	if err := protocol.UnmarshalDeterministic(input.Payload, &payload); err != nil ||
		validateStateDescriptorPayload(payload) != nil {
		return nil, ErrInvalidStateDescriptor
	}
	if subtle.ConstantTimeCompare(payload.NamespaceID[:], input.NamespaceID[:]) != 1 {
		return nil, ErrStateDescriptorContext
	}
	canonical, err := protocol.EncodeSigInput(input)
	if err != nil || subtle.ConstantTimeCompare(canonical, encodedSigInput) != 1 {
		return nil, ErrInvalidStateDescriptor
	}
	return newSignedStateDescriptor(payload, canonical, signature), nil
}

func validateStateDescriptorPayload(payload StateDescriptorPayload) error {
	if allZero(payload.NamespaceID[:]) || allZero(payload.CredentialID[:]) ||
		payload.ActiveVersion == 0 || allZero(payload.ActiveEnvelopeHash[:]) ||
		!payload.LifecycleStatus.Valid() || allZero(payload.LastOperationEvent[:]) ||
		allZero(payload.AuthorizedDeviceRoot[:]) || allZero(payload.AuditCheckpoint[:]) ||
		payload.FinalSequence == 0 || allZero(payload.UpdaterDeviceID[:]) {
		return ErrInvalidStateDescriptor
	}
	if payload.PreviousDescriptorHash != nil && allZero(payload.PreviousDescriptorHash[:]) {
		return ErrInvalidStateDescriptor
	}
	return nil
}

func newSignedStateDescriptor(
	payload StateDescriptorPayload,
	encoded []byte,
	signature protocol.Signature,
) *SignedStateDescriptor {
	hasher := sha256.New()
	_, _ = hasher.Write(encoded)
	_, _ = hasher.Write(signature[:])
	var digest [sha256.Size]byte
	copy(digest[:], hasher.Sum(nil))
	payload.PreviousDescriptorHash = cloneHash(payload.PreviousDescriptorHash)
	return &SignedStateDescriptor{
		payload:   payload,
		sigInput:  append([]byte(nil), encoded...),
		signature: signature,
		digest:    digest,
	}
}

func (descriptor *SignedStateDescriptor) Payload() StateDescriptorPayload {
	if descriptor == nil {
		return StateDescriptorPayload{}
	}
	result := descriptor.payload
	result.PreviousDescriptorHash = cloneHash(result.PreviousDescriptorHash)
	return result
}

func (descriptor *SignedStateDescriptor) SigInputCBOR() []byte {
	if descriptor == nil {
		return nil
	}
	return append([]byte(nil), descriptor.sigInput...)
}

func (descriptor *SignedStateDescriptor) Signature() protocol.Signature {
	if descriptor == nil {
		return protocol.Signature{}
	}
	return descriptor.signature
}

func (descriptor *SignedStateDescriptor) Digest() [sha256.Size]byte {
	if descriptor == nil {
		return [sha256.Size]byte{}
	}
	return descriptor.digest
}

// MarshalBinary returns the complete deterministic cloud object. Descriptor
// identity remains SHA-256(SigInput || Signature); a content-addressed store
// independently hashes these wrapper bytes.
func (descriptor *SignedStateDescriptor) MarshalBinary() ([]byte, error) {
	if descriptor == nil || len(descriptor.sigInput) == 0 {
		return nil, ErrInvalidStateDescriptor
	}
	encoded, err := protocol.MarshalDeterministic(signedStateDescriptorWire{
		SigInputCBOR: descriptor.sigInput,
		Signature:    descriptor.signature,
	})
	if err != nil {
		return nil, errors.Join(ErrInvalidStateDescriptor, err)
	}
	return encoded, nil
}

// ParseAndVerifyStateDescriptorObject verifies complete cloud bytes with
// receiver-owned trust context. Embedded key metadata is never a trust root.
func ParseAndVerifyStateDescriptorObject(
	encoded []byte,
	publicKey ed25519.PublicKey,
	expected protocol.VerificationContext,
) (*SignedStateDescriptor, error) {
	var wire signedStateDescriptorWire
	if err := protocol.UnmarshalDeterministic(encoded, &wire); err != nil ||
		len(wire.SigInputCBOR) == 0 {
		return nil, ErrInvalidStateDescriptor
	}
	canonical, err := protocol.MarshalDeterministic(wire)
	if err != nil || subtle.ConstantTimeCompare(canonical, encoded) != 1 {
		return nil, ErrInvalidStateDescriptor
	}
	return ParseAndVerifyStateDescriptor(
		wire.SigInputCBOR, wire.Signature, publicKey, expected,
	)
}
