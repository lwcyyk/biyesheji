package domain

import (
	"crypto/ed25519"
	"crypto/sha256"
	"crypto/subtle"
	"errors"

	"vdns.local/vdns/internal/protocol"
)

var (
	ErrInvalidTreeHead      = errors.New("invalid signed tree head")
	ErrTreeHeadContext      = errors.New("signed tree head context mismatch")
	ErrTreeHeadVerification = errors.New("signed tree head verification failed")
)

// TreeHeadPayload is the exact public projection signed by a log key.
type TreeHeadPayload struct {
	NamespaceID   protocol.NamespaceID `cbor:"namespace_id"`
	LogID         LogID                `cbor:"log_id"`
	TreeSize      uint64               `cbor:"tree_size"`
	RootHash      [sha256.Size]byte    `cbor:"root_hash"`
	FinalSequence uint64               `cbor:"final_sequence"`
	SuiteID       string               `cbor:"suite_id"`
}

// SignedTreeHead owns the canonical universal SigInput and signature.
type SignedTreeHead struct {
	payload   TreeHeadPayload
	sigInput  []byte
	signature protocol.Signature
	digest    [sha256.Size]byte
}

type signedTreeHeadWire struct {
	SigInputCBOR []byte             `cbor:"sig_input_cbor"`
	Signature    protocol.Signature `cbor:"signature"`
}

// SignTreeHead signs one non-empty tree head. The empty tree is a local trust
// bootstrap value and is never published as an accepted log head.
func SignTreeHead(
	privateKey ed25519.PrivateKey,
	chainID string,
	keyGeneration uint64,
	payload TreeHeadPayload,
) (*SignedTreeHead, error) {
	if validateTreeHeadPayload(payload) != nil || len(privateKey) != ed25519.PrivateKeySize {
		return nil, ErrInvalidTreeHead
	}
	publicKey := privateKey.Public().(ed25519.PublicKey)
	keyID, err := protocol.KeyIDFromPublicKey(publicKey)
	if err != nil {
		return nil, ErrInvalidTreeHead
	}
	payloadCBOR, err := protocol.MarshalDeterministic(payload)
	if err != nil {
		return nil, ErrInvalidTreeHead
	}
	input := protocol.NewSigInput(
		protocol.ObjectTypeSignedTreeHead, chainID, payload.NamespaceID,
		keyID, keyGeneration, payloadCBOR,
	)
	signature, err := protocol.Sign(privateKey, input)
	if err != nil {
		return nil, errors.Join(ErrTreeHeadVerification, err)
	}
	encoded, err := protocol.EncodeSigInput(input)
	if err != nil {
		return nil, ErrInvalidTreeHead
	}
	return newSignedTreeHead(payload, encoded, signature), nil
}

// ParseAndVerifyTreeHead checks receiver-owned chain, namespace, key ID and
// generation before exposing the signed projection.
func ParseAndVerifyTreeHead(
	encodedSigInput []byte,
	signature protocol.Signature,
	publicKey ed25519.PublicKey,
	expected protocol.VerificationContext,
) (*SignedTreeHead, error) {
	var input protocol.SigInput
	if err := protocol.UnmarshalDeterministic(encodedSigInput, &input); err != nil {
		return nil, ErrInvalidTreeHead
	}
	if err := protocol.Verify(publicKey, input, signature, expected); err != nil {
		return nil, errors.Join(ErrTreeHeadVerification, err)
	}
	if input.ObjectType != protocol.ObjectTypeSignedTreeHead {
		return nil, ErrTreeHeadContext
	}
	var payload TreeHeadPayload
	if err := protocol.UnmarshalDeterministic(input.Payload, &payload); err != nil ||
		validateTreeHeadPayload(payload) != nil {
		return nil, ErrInvalidTreeHead
	}
	if payload.NamespaceID != input.NamespaceID {
		return nil, ErrTreeHeadContext
	}
	canonical, err := protocol.EncodeSigInput(input)
	if err != nil || subtle.ConstantTimeCompare(canonical, encodedSigInput) != 1 {
		return nil, ErrInvalidTreeHead
	}
	return newSignedTreeHead(payload, canonical, signature), nil
}

func validateTreeHeadPayload(payload TreeHeadPayload) error {
	if zero(payload.NamespaceID[:]) || zero(payload.LogID[:]) ||
		payload.TreeSize == 0 || payload.TreeSize >= MaxTreeLeaves ||
		zero(payload.RootHash[:]) || payload.FinalSequence == 0 ||
		payload.SuiteID != protocol.SuiteID {
		return ErrInvalidTreeHead
	}
	return nil
}

func newSignedTreeHead(
	payload TreeHeadPayload,
	encoded []byte,
	signature protocol.Signature,
) *SignedTreeHead {
	hasher := sha256.New()
	_, _ = hasher.Write(encoded)
	_, _ = hasher.Write(signature[:])
	var digest [sha256.Size]byte
	copy(digest[:], hasher.Sum(nil))
	return &SignedTreeHead{
		payload: payload, sigInput: append([]byte(nil), encoded...),
		signature: signature, digest: digest,
	}
}

func (head *SignedTreeHead) Payload() TreeHeadPayload {
	if head == nil {
		return TreeHeadPayload{}
	}
	return head.payload
}

func (head *SignedTreeHead) SigInputCBOR() []byte {
	if head == nil {
		return nil
	}
	return append([]byte(nil), head.sigInput...)
}

func (head *SignedTreeHead) Signature() protocol.Signature {
	if head == nil {
		return protocol.Signature{}
	}
	return head.signature
}

func (head *SignedTreeHead) Digest() [sha256.Size]byte {
	if head == nil {
		return [sha256.Size]byte{}
	}
	return head.digest
}

func (head *SignedTreeHead) MarshalBinary() ([]byte, error) {
	if head == nil || len(head.sigInput) == 0 {
		return nil, ErrInvalidTreeHead
	}
	return protocol.MarshalDeterministic(signedTreeHeadWire{
		SigInputCBOR: head.sigInput, Signature: head.signature,
	})
}

func ParseAndVerifyTreeHeadObject(
	encoded []byte,
	publicKey ed25519.PublicKey,
	expected protocol.VerificationContext,
) (*SignedTreeHead, error) {
	var wire signedTreeHeadWire
	if err := protocol.UnmarshalDeterministic(encoded, &wire); err != nil ||
		len(wire.SigInputCBOR) == 0 {
		return nil, ErrInvalidTreeHead
	}
	canonical, err := protocol.MarshalDeterministic(wire)
	if err != nil || subtle.ConstantTimeCompare(canonical, encoded) != 1 {
		return nil, ErrInvalidTreeHead
	}
	return ParseAndVerifyTreeHead(
		wire.SigInputCBOR, wire.Signature, publicKey, expected,
	)
}
