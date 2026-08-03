// Package domain defines the public checkpoint whitelist and signed
// announcement receipts. No credential body or user secret is representable by
// these types.
package domain

import (
	"crypto/ed25519"
	"crypto/sha256"
	"crypto/subtle"
	"errors"

	"vpass.local/vpass/internal/protocol"
)

var (
	ErrInvalidCheckpoint      = errors.New("invalid checkpoint")
	ErrCheckpointContext      = errors.New("checkpoint context mismatch")
	ErrCheckpointVerification = errors.New("checkpoint signature verification failed")
)

// ProviderKind prevents an in-process simulator or local Anvil run from being
// described as a production consensus announcement.
type ProviderKind uint8

const (
	ProviderSimulated ProviderKind = 1
	ProviderAnvil     ProviderKind = 2
	ProviderConsensus ProviderKind = 3
)

func (kind ProviderKind) Valid() bool {
	return kind >= ProviderSimulated && kind <= ProviderConsensus
}

func (kind ProviderKind) Name() string {
	switch kind {
	case ProviderSimulated:
		return "SIMULATED"
	case ProviderAnvil:
		return "ANVIL"
	case ProviderConsensus:
		return "CONSENSUS"
	default:
		return "UNKNOWN"
	}
}

// CheckpointPayload is an allowlist, not an extensible metadata map. Adding a
// field is a protocol change and must pass the baseline process.
type CheckpointPayload struct {
	NamespaceID         protocol.NamespaceID `cbor:"namespace_id"`
	NamespaceStateRoot  [sha256.Size]byte    `cbor:"namespace_state_root"`
	DeviceStateRoot     [sha256.Size]byte    `cbor:"device_state_root"`
	CredentialStateRoot [sha256.Size]byte    `cbor:"credential_state_root"`
	AuditLogRoot        [sha256.Size]byte    `cbor:"audit_log_root"`
	RevocationRoot      [sha256.Size]byte    `cbor:"revocation_root"`
	CryptoPolicyHash    [sha256.Size]byte    `cbor:"crypto_policy_hash"`
	CheckpointHeight    uint64               `cbor:"checkpoint_height"`
	FinalSequence       uint64               `cbor:"final_sequence"`
	ProviderKind        ProviderKind         `cbor:"provider_kind"`
	VRFOutputHash       *[sha256.Size]byte   `cbor:"vrf_output_hash"`
}

func (payload CheckpointPayload) Validate() error {
	if bytesZero(payload.NamespaceID[:]) ||
		bytesZero(payload.NamespaceStateRoot[:]) ||
		bytesZero(payload.DeviceStateRoot[:]) ||
		bytesZero(payload.CredentialStateRoot[:]) ||
		bytesZero(payload.AuditLogRoot[:]) ||
		bytesZero(payload.RevocationRoot[:]) ||
		bytesZero(payload.CryptoPolicyHash[:]) ||
		payload.CheckpointHeight == 0 || payload.FinalSequence == 0 ||
		!payload.ProviderKind.Valid() {
		return ErrInvalidCheckpoint
	}
	if payload.VRFOutputHash != nil && bytesZero(payload.VRFOutputHash[:]) {
		return ErrInvalidCheckpoint
	}
	return nil
}

// SignedCheckpoint owns the canonical universal SigInput and signature.
type SignedCheckpoint struct {
	payload   CheckpointPayload
	sigInput  []byte
	signature protocol.Signature
	digest    [sha256.Size]byte
}

type signedCheckpointWire struct {
	SigInputCBOR []byte             `cbor:"sig_input_cbor"`
	Signature    protocol.Signature `cbor:"signature"`
}

func SignCheckpoint(
	privateKey ed25519.PrivateKey,
	chainID string,
	keyGeneration uint64,
	payload CheckpointPayload,
) (*SignedCheckpoint, error) {
	if payload.Validate() != nil || len(privateKey) != ed25519.PrivateKeySize {
		return nil, ErrInvalidCheckpoint
	}
	publicKey := privateKey.Public().(ed25519.PublicKey)
	keyID, err := protocol.KeyIDFromPublicKey(publicKey)
	if err != nil {
		return nil, ErrInvalidCheckpoint
	}
	payloadCBOR, err := protocol.MarshalDeterministic(payload)
	if err != nil {
		return nil, ErrInvalidCheckpoint
	}
	input := protocol.NewSigInput(
		protocol.ObjectTypeCheckpoint, chainID, payload.NamespaceID,
		keyID, keyGeneration, payloadCBOR,
	)
	signature, err := protocol.Sign(privateKey, input)
	if err != nil {
		return nil, errors.Join(ErrCheckpointVerification, err)
	}
	encoded, err := protocol.EncodeSigInput(input)
	if err != nil {
		return nil, ErrInvalidCheckpoint
	}
	return newSignedCheckpoint(payload, encoded, signature), nil
}

func ParseAndVerifyCheckpoint(
	encodedSigInput []byte,
	signature protocol.Signature,
	publicKey ed25519.PublicKey,
	expected protocol.VerificationContext,
) (*SignedCheckpoint, error) {
	var input protocol.SigInput
	if err := protocol.UnmarshalDeterministic(encodedSigInput, &input); err != nil {
		return nil, ErrInvalidCheckpoint
	}
	if err := protocol.Verify(publicKey, input, signature, expected); err != nil {
		return nil, errors.Join(ErrCheckpointVerification, err)
	}
	if input.ObjectType != protocol.ObjectTypeCheckpoint {
		return nil, ErrCheckpointContext
	}
	var payload CheckpointPayload
	if err := protocol.UnmarshalDeterministic(input.Payload, &payload); err != nil ||
		payload.Validate() != nil {
		return nil, ErrInvalidCheckpoint
	}
	if payload.NamespaceID != input.NamespaceID {
		return nil, ErrCheckpointContext
	}
	canonical, err := protocol.EncodeSigInput(input)
	if err != nil || subtle.ConstantTimeCompare(canonical, encodedSigInput) != 1 {
		return nil, ErrInvalidCheckpoint
	}
	return newSignedCheckpoint(payload, canonical, signature), nil
}

func newSignedCheckpoint(
	payload CheckpointPayload,
	encoded []byte,
	signature protocol.Signature,
) *SignedCheckpoint {
	payload.VRFOutputHash = cloneHash(payload.VRFOutputHash)
	hasher := sha256.New()
	_, _ = hasher.Write(encoded)
	_, _ = hasher.Write(signature[:])
	var digest [sha256.Size]byte
	copy(digest[:], hasher.Sum(nil))
	return &SignedCheckpoint{
		payload: payload, sigInput: append([]byte(nil), encoded...),
		signature: signature, digest: digest,
	}
}

func (checkpoint *SignedCheckpoint) Payload() CheckpointPayload {
	if checkpoint == nil {
		return CheckpointPayload{}
	}
	payload := checkpoint.payload
	payload.VRFOutputHash = cloneHash(payload.VRFOutputHash)
	return payload
}

func (checkpoint *SignedCheckpoint) SigInputCBOR() []byte {
	if checkpoint == nil {
		return nil
	}
	return append([]byte(nil), checkpoint.sigInput...)
}

func (checkpoint *SignedCheckpoint) Signature() protocol.Signature {
	if checkpoint == nil {
		return protocol.Signature{}
	}
	return checkpoint.signature
}

func (checkpoint *SignedCheckpoint) Digest() [sha256.Size]byte {
	if checkpoint == nil {
		return [sha256.Size]byte{}
	}
	return checkpoint.digest
}

func (checkpoint *SignedCheckpoint) MarshalBinary() ([]byte, error) {
	if checkpoint == nil || len(checkpoint.sigInput) == 0 {
		return nil, ErrInvalidCheckpoint
	}
	return protocol.MarshalDeterministic(signedCheckpointWire{
		SigInputCBOR: checkpoint.sigInput, Signature: checkpoint.signature,
	})
}

func ParseAndVerifyCheckpointObject(
	encoded []byte,
	publicKey ed25519.PublicKey,
	expected protocol.VerificationContext,
) (*SignedCheckpoint, error) {
	var wire signedCheckpointWire
	if err := protocol.UnmarshalDeterministic(encoded, &wire); err != nil ||
		len(wire.SigInputCBOR) == 0 {
		return nil, ErrInvalidCheckpoint
	}
	canonical, err := protocol.MarshalDeterministic(wire)
	if err != nil || subtle.ConstantTimeCompare(canonical, encoded) != 1 {
		return nil, ErrInvalidCheckpoint
	}
	return ParseAndVerifyCheckpoint(
		wire.SigInputCBOR, wire.Signature, publicKey, expected,
	)
}

func cloneHash(value *[sha256.Size]byte) *[sha256.Size]byte {
	if value == nil {
		return nil
	}
	cloned := *value
	return &cloned
}

func bytesZero(value []byte) bool {
	var combined byte
	for _, item := range value {
		combined |= item
	}
	return combined == 0
}
