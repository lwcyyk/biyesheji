package protocol

import (
	"crypto/ed25519"
	"crypto/sha256"
	"crypto/subtle"
	"errors"
	"unicode/utf8"
)

const (
	ProtocolID      = "VDNS-PM"
	ProtocolVersion = uint64(2)
	SuiteID         = "VDNS-PM-CP-2"
	DomainPrefix    = "VDNS-PM/2/VDNS-PM-CP-2/"
	MaxChainIDBytes = 128
	MaxPayloadBytes = 64 * 1024
)

// ObjectType is a frozen integer enum. New values require a protocol revision
// or explicit extension negotiation.
type ObjectType uint16

const (
	ObjectTypeRootCapsule         ObjectType = 1
	ObjectTypeRecoveryCapsule     ObjectType = 2
	ObjectTypeDeviceCredential    ObjectType = 3
	ObjectTypeCredentialEnvelope  ObjectType = 4
	ObjectTypeStateDescriptor     ObjectType = 5
	ObjectTypeOperationEvent      ObjectType = 6
	ObjectTypeSyncManifest        ObjectType = 7
	ObjectTypeSecretEnvelope      ObjectType = 8
	ObjectTypeAuditEvent          ObjectType = 9
	ObjectTypeLogLeaf             ObjectType = 10
	ObjectTypeSignedTreeHead      ObjectType = 11
	ObjectTypeProofBundle         ObjectType = 12
	ObjectTypeCheckpoint          ObjectType = 13
	ObjectTypeExposureAnalysis    ObjectType = 14
	ObjectTypeRemediationCampaign ObjectType = 15
	ObjectTypeRotationRoot        ObjectType = 16
)

func (objectType ObjectType) valid() bool {
	return objectType >= ObjectTypeRootCapsule && objectType <= ObjectTypeRotationRoot
}

// Valid reports whether the object type belongs to VDNS-PM/2.
func (objectType ObjectType) Valid() bool { return objectType.valid() }

// SigInput contains every protocol domain separator signed by an Ed25519 key.
// Payload is deterministic CBOR carried as a byte string, so the outer schema
// remains fixed and binds the exact payload bytes.
type SigInput struct {
	ProtocolID      string      `cbor:"protocol_id"`
	ProtocolVersion uint64      `cbor:"protocol_version"`
	SuiteID         string      `cbor:"suite_id"`
	ObjectType      ObjectType  `cbor:"object_type"`
	ChainID         string      `cbor:"chain_id"`
	NamespaceID     NamespaceID `cbor:"namespace_id"`
	KeyID           KeyID       `cbor:"key_id"`
	KeyGeneration   uint64      `cbor:"key_generation"`
	Payload         []byte      `cbor:"payload"`
}

// Signature is an Ed25519 signature with its wire length enforced by type.
type Signature [ed25519.SignatureSize]byte

// VerificationContext is the receiver's expected trust domain. It prevents a
// correctly signed object from being replayed into another namespace, chain,
// object type or key generation.
type VerificationContext struct {
	ObjectType    ObjectType
	ChainID       string
	NamespaceID   NamespaceID
	KeyID         KeyID
	KeyGeneration uint64
}

// NewSigInput fills the frozen protocol and suite identifiers.
func NewSigInput(
	objectType ObjectType,
	chainID string,
	namespaceID NamespaceID,
	keyID KeyID,
	keyGeneration uint64,
	payload []byte,
) SigInput {
	return SigInput{
		ProtocolID:      ProtocolID,
		ProtocolVersion: ProtocolVersion,
		SuiteID:         SuiteID,
		ObjectType:      objectType,
		ChainID:         chainID,
		NamespaceID:     namespaceID,
		KeyID:           keyID,
		KeyGeneration:   keyGeneration,
		Payload:         append([]byte(nil), payload...),
	}
}

// Validate checks the complete signature domain before cryptographic use.
func (input SigInput) Validate() error {
	if subtle.ConstantTimeCompare([]byte(input.ProtocolID), []byte(ProtocolID)) != 1 || input.ProtocolVersion != ProtocolVersion {
		return reject(CodeUnsupportedProtocol, "protocol", nil)
	}
	if subtle.ConstantTimeCompare([]byte(input.SuiteID), []byte(SuiteID)) != 1 {
		return reject(CodeUnsupportedSuite, "suiteId", nil)
	}
	if !input.ObjectType.valid() {
		return reject(CodeUnsupportedObject, "objectType", nil)
	}
	if len(input.ChainID) == 0 || len(input.ChainID) > MaxChainIDBytes || !utf8.ValidString(input.ChainID) {
		return reject(CodeContextMismatch, "chainId", nil)
	}
	if input.KeyGeneration == 0 {
		return reject(CodeContextMismatch, "keyGeneration", nil)
	}
	if len(input.Payload) > MaxPayloadBytes {
		return reject(CodeResourceLimit, "payload", nil)
	}
	if err := ValidateDeterministic(input.Payload); err != nil {
		return reject(CodeCBORInvalid, "payload", err)
	}
	return nil
}

// EncodeSigInput validates and deterministically encodes the complete input.
func EncodeSigInput(input SigInput) ([]byte, error) {
	if err := input.Validate(); err != nil {
		return nil, err
	}
	return MarshalDeterministic(input)
}

// Sign signs the complete deterministic SigInput with Ed25519.
func Sign(privateKey ed25519.PrivateKey, input SigInput) (Signature, error) {
	if len(privateKey) != ed25519.PrivateKeySize {
		return Signature{}, reject(CodeInvalidKey, "privateKey", nil)
	}
	expectedKeyID, err := KeyIDFromPublicKey(privateKey.Public().(ed25519.PublicKey))
	if err != nil {
		return Signature{}, err
	}
	if subtle.ConstantTimeCompare(input.KeyID[:], expectedKeyID[:]) != 1 {
		return Signature{}, reject(CodeContextMismatch, "keyId", nil)
	}
	encoded, err := EncodeSigInput(input)
	if err != nil {
		return Signature{}, err
	}
	return signEd25519(privateKey, encoded)
}

// Verify requires the receiver's expected trust domain, then checks the
// signature. The context must come from receiver state, never from input.
func Verify(
	publicKey ed25519.PublicKey,
	input SigInput,
	signature Signature,
	expected VerificationContext,
) error {
	if err := input.Validate(); err != nil {
		return err
	}
	if input.ObjectType != expected.ObjectType ||
		input.KeyGeneration != expected.KeyGeneration ||
		subtle.ConstantTimeCompare([]byte(input.ChainID), []byte(expected.ChainID)) != 1 ||
		subtle.ConstantTimeCompare(input.NamespaceID[:], expected.NamespaceID[:]) != 1 ||
		subtle.ConstantTimeCompare(input.KeyID[:], expected.KeyID[:]) != 1 {
		return reject(CodeContextMismatch, "verificationContext", nil)
	}
	return verifySignatureOnly(publicKey, input, signature)
}

func verifySignatureOnly(publicKey ed25519.PublicKey, input SigInput, signature Signature) error {
	encoded, err := EncodeSigInput(input)
	if err != nil {
		return err
	}
	expectedKeyID, err := KeyIDFromPublicKey(publicKey)
	if err != nil {
		return err
	}
	if subtle.ConstantTimeCompare(input.KeyID[:], expectedKeyID[:]) != 1 {
		return reject(CodeContextMismatch, "keyId", nil)
	}
	if !ed25519.Verify(publicKey, encoded, signature[:]) {
		return reject(CodeInvalidSignature, "signature", nil)
	}
	return nil
}

// KeyIDFromPublicKey derives the frozen SHA-256 key identifier.
func KeyIDFromPublicKey(publicKey ed25519.PublicKey) (KeyID, error) {
	if len(publicKey) != ed25519.PublicKeySize {
		return KeyID{}, reject(CodeInvalidKey, "publicKey", nil)
	}
	digest := sha256.Sum256(publicKey)
	return KeyID(digest), nil
}

// EventDigest computes SHA256(SigInput || signature).
func EventDigest(input SigInput, signature Signature) ([sha256.Size]byte, error) {
	encoded, err := EncodeSigInput(input)
	if err != nil {
		return [sha256.Size]byte{}, err
	}
	hash := sha256.New()
	_, _ = hash.Write(encoded)
	_, _ = hash.Write(signature[:])
	var digest [sha256.Size]byte
	copy(digest[:], hash.Sum(nil))
	return digest, nil
}

func signEd25519(privateKey ed25519.PrivateKey, message []byte) (Signature, error) {
	if len(privateKey) != ed25519.PrivateKeySize {
		return Signature{}, reject(CodeInvalidKey, "privateKey", nil)
	}
	if len(message) > MaxCBORBytes {
		return Signature{}, reject(CodeResourceLimit, "message", nil)
	}
	raw := ed25519.Sign(privateKey, message)
	if len(raw) != ed25519.SignatureSize {
		return Signature{}, reject(CodeInvalidSignature, "signature", errors.New("invalid signer output"))
	}
	var signature Signature
	copy(signature[:], raw)
	return signature, nil
}
