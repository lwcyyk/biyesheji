package domain

import (
	"crypto/ed25519"
	"crypto/sha256"
	"crypto/subtle"
	"errors"

	"vpass.local/vpass/internal/protocol"
)

const (
	MaxRootChainObjects  = 8
	MaxStatusProofHashes = 64
)

var (
	ErrInvalidProofBundle      = errors.New("invalid proof bundle")
	ErrProofBundleContext      = errors.New("proof bundle context mismatch")
	ErrProofBundleVerification = errors.New("proof bundle signature verification failed")
)

// RootChainDigest commits to the ordered root-control chain carried by a
// ProofBundle. The receiver independently constructs the expected chain from
// local trust state; merely including bytes is never sufficient.
func RootChainDigest(objects [][]byte) ([sha256.Size]byte, error) {
	if len(objects) == 0 || len(objects) > MaxRootChainObjects {
		return [sha256.Size]byte{}, ErrInvalidProofBundle
	}
	cloned := make([][]byte, len(objects))
	for index, object := range objects {
		if len(object) == 0 {
			return [sha256.Size]byte{}, ErrInvalidProofBundle
		}
		cloned[index] = append([]byte(nil), object...)
	}
	encoded, err := protocol.MarshalDeterministic(struct {
		Objects [][]byte `cbor:"objects"`
	}{
		Objects: cloned,
	})
	if err != nil {
		return [sha256.Size]byte{}, ErrInvalidProofBundle
	}
	return sha256.Sum256(encoded), nil
}

// ProofBundlePayload binds every input needed to advance from a locally
// trusted checkpoint to a candidate log head. Private authorization objects
// remain inside this point-to-point proof object and are never checkpoint
// fields or public log leaves.
type ProofBundlePayload struct {
	NamespaceID              protocol.NamespaceID `cbor:"namespace_id"`
	SubjectDigest            [sha256.Size]byte    `cbor:"subject_digest"`
	LeafIndex                uint64               `cbor:"leaf_index"`
	Leaf                     LogLeaf              `cbor:"leaf"`
	StartingCheckpointObject []byte               `cbor:"starting_checkpoint_object"`
	CandidateTreeHeadObject  []byte               `cbor:"candidate_tree_head_object"`
	InclusionProof           [][sha256.Size]byte  `cbor:"inclusion_proof"`
	ConsistencyProof         [][sha256.Size]byte  `cbor:"consistency_proof"`
	RootChainObjects         [][]byte             `cbor:"root_chain_objects"`
	DeviceCredentialObject   []byte               `cbor:"device_credential_object"`
	CapabilityStatusProof    [][sha256.Size]byte  `cbor:"capability_status_proof"`
	StateDescriptorDigest    [sha256.Size]byte    `cbor:"state_descriptor_digest"`
	LocalPolicyInputHash     [sha256.Size]byte    `cbor:"local_policy_input_hash"`
}

func (payload ProofBundlePayload) Validate() error {
	if proofZero(payload.NamespaceID[:]) || proofZero(payload.SubjectDigest[:]) ||
		payload.Leaf.Validate() != nil ||
		len(payload.StartingCheckpointObject) == 0 ||
		len(payload.CandidateTreeHeadObject) == 0 ||
		len(payload.InclusionProof) > MaxProofHashes ||
		len(payload.ConsistencyProof) > MaxProofHashes ||
		len(payload.RootChainObjects) == 0 ||
		len(payload.RootChainObjects) > MaxRootChainObjects ||
		len(payload.DeviceCredentialObject) == 0 ||
		len(payload.CapabilityStatusProof) == 0 ||
		len(payload.CapabilityStatusProof) > MaxStatusProofHashes ||
		proofZero(payload.StateDescriptorDigest[:]) ||
		proofZero(payload.LocalPolicyInputHash[:]) {
		return ErrInvalidProofBundle
	}
	if payload.Leaf.ObjectDigest != payload.SubjectDigest {
		return ErrInvalidProofBundle
	}
	for _, object := range payload.RootChainObjects {
		if len(object) == 0 {
			return ErrInvalidProofBundle
		}
	}
	for _, proof := range [][][sha256.Size]byte{
		payload.InclusionProof, payload.ConsistencyProof, payload.CapabilityStatusProof,
	} {
		for _, item := range proof {
			if proofZero(item[:]) {
				return ErrInvalidProofBundle
			}
		}
	}
	return nil
}

type SignedProofBundle struct {
	payload   ProofBundlePayload
	sigInput  []byte
	signature protocol.Signature
	digest    [sha256.Size]byte
}

type signedProofBundleWire struct {
	SigInputCBOR []byte             `cbor:"sig_input_cbor"`
	Signature    protocol.Signature `cbor:"signature"`
}

func SignProofBundle(
	privateKey ed25519.PrivateKey,
	chainID string,
	keyGeneration uint64,
	payload ProofBundlePayload,
) (*SignedProofBundle, error) {
	if payload.Validate() != nil || len(privateKey) != ed25519.PrivateKeySize {
		return nil, ErrInvalidProofBundle
	}
	publicKey := privateKey.Public().(ed25519.PublicKey)
	keyID, err := protocol.KeyIDFromPublicKey(publicKey)
	if err != nil {
		return nil, ErrInvalidProofBundle
	}
	payloadCBOR, err := protocol.MarshalDeterministic(payload)
	if err != nil {
		return nil, ErrInvalidProofBundle
	}
	input := protocol.NewSigInput(
		protocol.ObjectTypeProofBundle, chainID, payload.NamespaceID,
		keyID, keyGeneration, payloadCBOR,
	)
	signature, err := protocol.Sign(privateKey, input)
	if err != nil {
		return nil, errors.Join(ErrProofBundleVerification, err)
	}
	encoded, err := protocol.EncodeSigInput(input)
	if err != nil {
		return nil, ErrInvalidProofBundle
	}
	return newSignedProofBundle(payload, encoded, signature), nil
}

func ParseAndVerifyProofBundle(
	encodedSigInput []byte,
	signature protocol.Signature,
	publicKey ed25519.PublicKey,
	expected protocol.VerificationContext,
) (*SignedProofBundle, error) {
	var input protocol.SigInput
	if err := protocol.UnmarshalDeterministic(encodedSigInput, &input); err != nil {
		return nil, ErrInvalidProofBundle
	}
	if err := protocol.Verify(publicKey, input, signature, expected); err != nil {
		return nil, errors.Join(ErrProofBundleVerification, err)
	}
	if input.ObjectType != protocol.ObjectTypeProofBundle {
		return nil, ErrProofBundleContext
	}
	var payload ProofBundlePayload
	if err := protocol.UnmarshalDeterministic(input.Payload, &payload); err != nil ||
		payload.Validate() != nil {
		return nil, ErrInvalidProofBundle
	}
	if payload.NamespaceID != input.NamespaceID {
		return nil, ErrProofBundleContext
	}
	canonical, err := protocol.EncodeSigInput(input)
	if err != nil || subtle.ConstantTimeCompare(canonical, encodedSigInput) != 1 {
		return nil, ErrInvalidProofBundle
	}
	return newSignedProofBundle(payload, canonical, signature), nil
}

func newSignedProofBundle(
	payload ProofBundlePayload,
	encoded []byte,
	signature protocol.Signature,
) *SignedProofBundle {
	payload = cloneProofBundlePayload(payload)
	hasher := sha256.New()
	_, _ = hasher.Write(encoded)
	_, _ = hasher.Write(signature[:])
	var digest [sha256.Size]byte
	copy(digest[:], hasher.Sum(nil))
	return &SignedProofBundle{
		payload: payload, sigInput: append([]byte(nil), encoded...),
		signature: signature, digest: digest,
	}
}

func (bundle *SignedProofBundle) Payload() ProofBundlePayload {
	if bundle == nil {
		return ProofBundlePayload{}
	}
	return cloneProofBundlePayload(bundle.payload)
}

func (bundle *SignedProofBundle) SigInputCBOR() []byte {
	if bundle == nil {
		return nil
	}
	return append([]byte(nil), bundle.sigInput...)
}

func (bundle *SignedProofBundle) Signature() protocol.Signature {
	if bundle == nil {
		return protocol.Signature{}
	}
	return bundle.signature
}

func (bundle *SignedProofBundle) Digest() [sha256.Size]byte {
	if bundle == nil {
		return [sha256.Size]byte{}
	}
	return bundle.digest
}

func (bundle *SignedProofBundle) MarshalBinary() ([]byte, error) {
	if bundle == nil || len(bundle.sigInput) == 0 {
		return nil, ErrInvalidProofBundle
	}
	return protocol.MarshalDeterministic(signedProofBundleWire{
		SigInputCBOR: bundle.sigInput, Signature: bundle.signature,
	})
}

func ParseAndVerifyProofBundleObject(
	encoded []byte,
	publicKey ed25519.PublicKey,
	expected protocol.VerificationContext,
) (*SignedProofBundle, error) {
	var wire signedProofBundleWire
	if err := protocol.UnmarshalDeterministic(encoded, &wire); err != nil ||
		len(wire.SigInputCBOR) == 0 {
		return nil, ErrInvalidProofBundle
	}
	canonical, err := protocol.MarshalDeterministic(wire)
	if err != nil || subtle.ConstantTimeCompare(canonical, encoded) != 1 {
		return nil, ErrInvalidProofBundle
	}
	return ParseAndVerifyProofBundle(
		wire.SigInputCBOR, wire.Signature, publicKey, expected,
	)
}

func cloneProofBundlePayload(payload ProofBundlePayload) ProofBundlePayload {
	payload.StartingCheckpointObject = append([]byte(nil), payload.StartingCheckpointObject...)
	payload.CandidateTreeHeadObject = append([]byte(nil), payload.CandidateTreeHeadObject...)
	payload.InclusionProof = append([][sha256.Size]byte(nil), payload.InclusionProof...)
	payload.ConsistencyProof = append([][sha256.Size]byte(nil), payload.ConsistencyProof...)
	payload.DeviceCredentialObject = append([]byte(nil), payload.DeviceCredentialObject...)
	payload.CapabilityStatusProof = append([][sha256.Size]byte(nil), payload.CapabilityStatusProof...)
	rootChainObjects := payload.RootChainObjects
	payload.RootChainObjects = make([][]byte, len(rootChainObjects))
	for index, object := range rootChainObjects {
		payload.RootChainObjects[index] = append([]byte(nil), object...)
	}
	return payload
}

func proofZero(value []byte) bool {
	var combined byte
	for _, item := range value {
		combined |= item
	}
	return combined == 0
}
