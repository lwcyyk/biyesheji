// Package domain defines the public, secret-free final-order model.
package domain

import (
	"crypto/ed25519"
	"crypto/sha256"
	"crypto/subtle"
	"errors"
	"sort"
	"strings"

	"vdns.local/vdns/internal/protocol"
)

const (
	AdapterKind       = "RESEARCH_ADAPTER"
	MaxResolutionNote = 256
)

var (
	ErrInvalidCandidate    = errors.New("invalid final-order candidate")
	ErrCandidateNotFound   = errors.New("final-order candidate not found")
	ErrPredecessor         = errors.New("final-order predecessor mismatch")
	ErrIdempotency         = errors.New("final-order idempotency conflict")
	ErrConflictRequired    = errors.New("credential conflict requires explicit resolution")
	ErrInvalidResolution   = errors.New("invalid credential conflict resolution")
	ErrPersistenceConflict = errors.New("final-order persistence revision conflict")
	ErrReceiptSignature    = errors.New("final-order receipt signature invalid")
	ErrCheckpointSignature = errors.New("final-order checkpoint signature invalid")
)

type CredentialState string

const (
	StateCandidate  CredentialState = "CANDIDATE"
	StateActive     CredentialState = "ACTIVE"
	StateConflicted CredentialState = "CONFLICTED"
)

type CandidateDisposition string

const (
	DispositionPending  CandidateDisposition = "PENDING"
	DispositionOrdered  CandidateDisposition = "ORDERED"
	DispositionConflict CandidateDisposition = "CONFLICTED"
	DispositionSelected CandidateDisposition = "SELECTED"
	DispositionRejected CandidateDisposition = "REJECTED"
)

type Candidate struct {
	NamespaceID        protocol.NamespaceID  `json:"namespaceId"`
	CredentialID       protocol.CredentialID `json:"credentialId"`
	BaseVersion        uint64                `json:"baseVersion"`
	CandidateVersion   uint64                `json:"candidateVersion"`
	BaseDescriptorHash [sha256.Size]byte     `json:"baseDescriptorHash"`
	DescriptorHash     [sha256.Size]byte     `json:"descriptorHash"`
	EnvelopeHash       [sha256.Size]byte     `json:"envelopeHash"`
	DeviceID           protocol.DeviceID     `json:"deviceId"`
	SubmittedBy        string                `json:"submittedBy"`
	IdempotencyKeyHash [sha256.Size]byte     `json:"idempotencyKeyHash"`
}

type candidateProjection struct {
	Domain             string                `cbor:"domain"`
	NamespaceID        protocol.NamespaceID  `cbor:"namespace_id"`
	CredentialID       protocol.CredentialID `cbor:"credential_id"`
	BaseVersion        uint64                `cbor:"base_version"`
	CandidateVersion   uint64                `cbor:"candidate_version"`
	BaseDescriptorHash [sha256.Size]byte     `cbor:"base_descriptor_hash"`
	DescriptorHash     [sha256.Size]byte     `cbor:"descriptor_hash"`
	EnvelopeHash       [sha256.Size]byte     `cbor:"envelope_hash"`
	DeviceID           protocol.DeviceID     `cbor:"device_id"`
	SubmittedBy        string                `cbor:"submitted_by"`
}

func (candidate Candidate) Validate() error {
	if zero(candidate.NamespaceID[:]) || zero(candidate.CredentialID[:]) ||
		candidate.BaseVersion == 0 ||
		candidate.CandidateVersion != candidate.BaseVersion+1 ||
		zero(candidate.BaseDescriptorHash[:]) ||
		zero(candidate.DescriptorHash[:]) ||
		zero(candidate.EnvelopeHash[:]) ||
		zero(candidate.DeviceID[:]) ||
		candidate.DescriptorHash == candidate.BaseDescriptorHash ||
		strings.TrimSpace(candidate.SubmittedBy) == "" ||
		len(candidate.SubmittedBy) > 128 ||
		zero(candidate.IdempotencyKeyHash[:]) {
		return ErrInvalidCandidate
	}
	return nil
}

func (candidate Candidate) Digest() ([sha256.Size]byte, error) {
	if err := candidate.Validate(); err != nil {
		return [sha256.Size]byte{}, err
	}
	encoded, err := protocol.MarshalDeterministic(candidateProjection{
		Domain:      protocol.DomainPrefix + "FINAL-ORDER-CANDIDATE",
		NamespaceID: candidate.NamespaceID, CredentialID: candidate.CredentialID,
		BaseVersion: candidate.BaseVersion, CandidateVersion: candidate.CandidateVersion,
		BaseDescriptorHash: candidate.BaseDescriptorHash,
		DescriptorHash:     candidate.DescriptorHash, EnvelopeHash: candidate.EnvelopeHash,
		DeviceID: candidate.DeviceID, SubmittedBy: candidate.SubmittedBy,
	})
	if err != nil {
		return [sha256.Size]byte{}, ErrInvalidCandidate
	}
	return sha256.Sum256(encoded), nil
}

type CandidateRecord struct {
	Candidate       Candidate            `json:"candidate"`
	CandidateDigest [sha256.Size]byte    `json:"candidateDigest"`
	Disposition     CandidateDisposition `json:"disposition"`
	FinalSequence   uint64               `json:"finalSequence,omitempty"`
	ReceiptDigest   [sha256.Size]byte    `json:"receiptDigest,omitempty"`
}

type FinalOrderReceiptPayload struct {
	Domain                 string                `cbor:"domain" json:"domain"`
	ProtocolID             string                `cbor:"protocol_id" json:"protocolId"`
	ProtocolVersion        uint64                `cbor:"protocol_version" json:"protocolVersion"`
	SuiteID                string                `cbor:"suite_id" json:"suiteId"`
	AdapterKind            string                `cbor:"adapter_kind" json:"adapterKind"`
	NamespaceID            protocol.NamespaceID  `cbor:"namespace_id" json:"namespaceId"`
	CredentialID           protocol.CredentialID `cbor:"credential_id" json:"credentialId"`
	OrderedObjectDigest    [sha256.Size]byte     `cbor:"ordered_object_digest" json:"orderedObjectDigest"`
	FinalSequence          uint64                `cbor:"final_sequence" json:"finalSequence"`
	PreviousOrderedDigest  *[sha256.Size]byte    `cbor:"previous_ordered_digest,omitempty" json:"previousOrderedDigest,omitempty"`
	AuthorityKeyID         [sha256.Size]byte     `cbor:"authority_key_id" json:"authorityKeyId"`
	AuthorityKeyGeneration uint64                `cbor:"authority_key_generation" json:"authorityKeyGeneration"`
}

type FinalOrderReceipt struct {
	Payload   FinalOrderReceiptPayload `json:"payload"`
	Signature protocol.Signature       `json:"signature"`
	Digest    [sha256.Size]byte        `json:"digest"`
}

type finalOrderReceiptWire struct {
	Payload   FinalOrderReceiptPayload `cbor:"payload"`
	Signature protocol.Signature       `cbor:"signature"`
}

func SignReceipt(
	privateKey ed25519.PrivateKey,
	payload FinalOrderReceiptPayload,
) (FinalOrderReceipt, error) {
	if len(privateKey) != ed25519.PrivateKeySize || validateReceiptPayload(payload) != nil {
		return FinalOrderReceipt{}, ErrInvalidCandidate
	}
	encoded, err := protocol.MarshalDeterministic(payload)
	if err != nil {
		return FinalOrderReceipt{}, ErrInvalidCandidate
	}
	raw := ed25519.Sign(privateKey, encoded)
	var signature protocol.Signature
	copy(signature[:], raw)
	digest := receiptDigest(encoded, signature)
	return FinalOrderReceipt{Payload: payload, Signature: signature, Digest: digest}, nil
}

func VerifyReceipt(receipt FinalOrderReceipt, publicKey ed25519.PublicKey) error {
	if len(publicKey) != ed25519.PublicKeySize ||
		validateReceiptPayload(receipt.Payload) != nil {
		return ErrReceiptSignature
	}
	encoded, err := protocol.MarshalDeterministic(receipt.Payload)
	expected := receiptDigest(encoded, receipt.Signature)
	if err != nil ||
		!ed25519.Verify(publicKey, encoded, receipt.Signature[:]) ||
		subtle.ConstantTimeCompare(expected[:], receipt.Digest[:]) != 1 {
		return ErrReceiptSignature
	}
	return nil
}

// MarshalBinary returns the deterministic CP-2 research-adapter wire object.
// Digest is derived from the signed payload and is therefore not duplicated on
// the wire.
func (receipt FinalOrderReceipt) MarshalBinary() ([]byte, error) {
	if validateReceiptPayload(receipt.Payload) != nil {
		return nil, ErrInvalidCandidate
	}
	encodedPayload, err := protocol.MarshalDeterministic(receipt.Payload)
	if err != nil ||
		receiptDigest(encodedPayload, receipt.Signature) != receipt.Digest {
		return nil, ErrInvalidCandidate
	}
	return protocol.MarshalDeterministic(finalOrderReceiptWire{
		Payload: receipt.Payload, Signature: receipt.Signature,
	})
}

// ParseReceipt accepts only deterministic CBOR and reconstructs the derived
// receipt digest. Signature trust is checked separately by VerifyReceipt.
func ParseReceipt(encoded []byte) (FinalOrderReceipt, error) {
	var wire finalOrderReceiptWire
	if len(encoded) == 0 ||
		protocol.UnmarshalDeterministic(encoded, &wire) != nil ||
		validateReceiptPayload(wire.Payload) != nil {
		return FinalOrderReceipt{}, ErrInvalidCandidate
	}
	canonical, err := protocol.MarshalDeterministic(wire)
	if err != nil || subtle.ConstantTimeCompare(canonical, encoded) != 1 {
		return FinalOrderReceipt{}, ErrInvalidCandidate
	}
	payload, err := protocol.MarshalDeterministic(wire.Payload)
	if err != nil {
		return FinalOrderReceipt{}, ErrInvalidCandidate
	}
	return FinalOrderReceipt{
		Payload: wire.Payload, Signature: wire.Signature,
		Digest: receiptDigest(payload, wire.Signature),
	}, nil
}

func validateReceiptPayload(payload FinalOrderReceiptPayload) error {
	if payload.Domain != protocol.DomainPrefix+"FINAL-ORDER-RECEIPT" ||
		payload.ProtocolID != protocol.ProtocolID ||
		payload.ProtocolVersion != protocol.ProtocolVersion ||
		payload.SuiteID != protocol.SuiteID ||
		payload.AdapterKind != AdapterKind ||
		zero(payload.NamespaceID[:]) || zero(payload.CredentialID[:]) ||
		zero(payload.OrderedObjectDigest[:]) ||
		payload.FinalSequence == 0 || zero(payload.AuthorityKeyID[:]) ||
		payload.AuthorityKeyGeneration == 0 {
		return ErrInvalidCandidate
	}
	return nil
}

func receiptDigest(encoded []byte, signature protocol.Signature) [sha256.Size]byte {
	hasher := sha256.New()
	_, _ = hasher.Write([]byte(protocol.DomainPrefix + "FINAL-ORDER-RECEIPT-DIGEST"))
	_, _ = hasher.Write(encoded)
	_, _ = hasher.Write(signature[:])
	var result [sha256.Size]byte
	copy(result[:], hasher.Sum(nil))
	return result
}

type FinalizedState struct {
	NamespaceID     protocol.NamespaceID  `json:"namespaceId"`
	CredentialID    protocol.CredentialID `json:"credentialId"`
	Status          CredentialState       `json:"status"`
	CurrentVersion  uint64                `json:"currentVersion"`
	DescriptorHash  [sha256.Size]byte     `json:"descriptorHash"`
	FinalSequence   uint64                `json:"finalSequence"`
	ConflictDigests [][sha256.Size]byte   `json:"conflictDigests,omitempty"`
}

type ResolutionRequest struct {
	NamespaceID              protocol.NamespaceID  `json:"namespaceId"`
	CredentialID             protocol.CredentialID `json:"credentialId"`
	CandidateDigests         [][sha256.Size]byte   `json:"candidateDigests"`
	SelectedCandidateDigest  [sha256.Size]byte     `json:"selectedCandidateDigest"`
	ResolutionDescriptorHash [sha256.Size]byte     `json:"resolutionDescriptorHash"`
	ResolvedBy               string                `json:"resolvedBy"`
	Basis                    string                `json:"basis"`
	IdempotencyKeyHash       [sha256.Size]byte     `json:"idempotencyKeyHash"`
}

func (request ResolutionRequest) Validate() error {
	if zero(request.NamespaceID[:]) || zero(request.CredentialID[:]) ||
		len(request.CandidateDigests) < 2 ||
		zero(request.SelectedCandidateDigest[:]) ||
		zero(request.ResolutionDescriptorHash[:]) ||
		strings.TrimSpace(request.ResolvedBy) == "" || len(request.ResolvedBy) > 128 ||
		strings.TrimSpace(request.Basis) == "" || len(request.Basis) > MaxResolutionNote ||
		zero(request.IdempotencyKeyHash[:]) {
		return ErrInvalidResolution
	}
	seen := make(map[[sha256.Size]byte]bool, len(request.CandidateDigests))
	for _, digest := range request.CandidateDigests {
		if zero(digest[:]) || seen[digest] {
			return ErrInvalidResolution
		}
		seen[digest] = true
	}
	if !seen[request.SelectedCandidateDigest] {
		return ErrInvalidResolution
	}
	return nil
}

type ResolutionRecord struct {
	Request          ResolutionRequest `json:"request"`
	ResolutionDigest [sha256.Size]byte `json:"resolutionDigest"`
	NewVersion       uint64            `json:"newVersion"`
	Receipt          FinalOrderReceipt `json:"receipt"`
}

type TrustedCheckpoint struct {
	Domain            string               `cbor:"domain" json:"domain"`
	AdapterKind       string               `cbor:"adapter_kind" json:"adapterKind"`
	NamespaceID       protocol.NamespaceID `cbor:"namespace_id" json:"namespaceId"`
	FinalSequence     uint64               `cbor:"final_sequence" json:"finalSequence"`
	StateRoot         [sha256.Size]byte    `cbor:"state_root" json:"stateRoot"`
	LastReceiptDigest [sha256.Size]byte    `cbor:"last_receipt_digest" json:"lastReceiptDigest"`
	AuthorityKeyID    [sha256.Size]byte    `cbor:"authority_key_id" json:"authorityKeyId"`
	KeyGeneration     uint64               `cbor:"key_generation" json:"keyGeneration"`
	Signature         protocol.Signature   `cbor:"-" json:"signature"`
	Digest            [sha256.Size]byte    `cbor:"-" json:"digest"`
}

type checkpointBody TrustedCheckpoint

func SignCheckpoint(privateKey ed25519.PrivateKey, checkpoint TrustedCheckpoint) (TrustedCheckpoint, error) {
	if len(privateKey) != ed25519.PrivateKeySize ||
		checkpoint.Domain != protocol.DomainPrefix+"FINAL-ORDER-CHECKPOINT" ||
		checkpoint.AdapterKind != AdapterKind || zero(checkpoint.NamespaceID[:]) ||
		checkpoint.FinalSequence == 0 || zero(checkpoint.StateRoot[:]) ||
		zero(checkpoint.LastReceiptDigest[:]) || zero(checkpoint.AuthorityKeyID[:]) ||
		checkpoint.KeyGeneration == 0 {
		return TrustedCheckpoint{}, ErrInvalidCandidate
	}
	checkpoint.Signature = protocol.Signature{}
	checkpoint.Digest = [sha256.Size]byte{}
	encoded, err := protocol.MarshalDeterministic(checkpointUnsigned(checkpoint))
	if err != nil {
		return TrustedCheckpoint{}, ErrInvalidCandidate
	}
	copy(checkpoint.Signature[:], ed25519.Sign(privateKey, encoded))
	checkpoint.Digest = sha256.Sum256(append(encoded, checkpoint.Signature[:]...))
	return checkpoint, nil
}

// VerifyCheckpoint authenticates a research-adapter bootstrap checkpoint. A
// valid signature does not turn the single-node adapter into consensus; the
// caller must already trust the authority key through an out-of-band policy.
func VerifyCheckpoint(checkpoint TrustedCheckpoint, publicKey ed25519.PublicKey) error {
	keyID := sha256.Sum256(publicKey)
	if len(publicKey) != ed25519.PublicKeySize ||
		checkpoint.Domain != protocol.DomainPrefix+"FINAL-ORDER-CHECKPOINT" ||
		checkpoint.AdapterKind != AdapterKind || zero(checkpoint.NamespaceID[:]) ||
		checkpoint.FinalSequence == 0 || zero(checkpoint.StateRoot[:]) ||
		zero(checkpoint.LastReceiptDigest[:]) || zero(checkpoint.AuthorityKeyID[:]) ||
		checkpoint.KeyGeneration == 0 ||
		subtle.ConstantTimeCompare(
			checkpoint.AuthorityKeyID[:], keyID[:],
		) != 1 {
		return ErrCheckpointSignature
	}
	encoded, err := protocol.MarshalDeterministic(checkpointUnsigned(checkpoint))
	expected := sha256.Sum256(append(encoded, checkpoint.Signature[:]...))
	if err != nil ||
		!ed25519.Verify(publicKey, encoded, checkpoint.Signature[:]) ||
		subtle.ConstantTimeCompare(expected[:], checkpoint.Digest[:]) != 1 {
		return ErrCheckpointSignature
	}
	return nil
}

func checkpointUnsigned(checkpoint TrustedCheckpoint) struct {
	Domain            string               `cbor:"domain"`
	AdapterKind       string               `cbor:"adapter_kind"`
	NamespaceID       protocol.NamespaceID `cbor:"namespace_id"`
	FinalSequence     uint64               `cbor:"final_sequence"`
	StateRoot         [sha256.Size]byte    `cbor:"state_root"`
	LastReceiptDigest [sha256.Size]byte    `cbor:"last_receipt_digest"`
	AuthorityKeyID    [sha256.Size]byte    `cbor:"authority_key_id"`
	KeyGeneration     uint64               `cbor:"key_generation"`
} {
	return struct {
		Domain            string               `cbor:"domain"`
		AdapterKind       string               `cbor:"adapter_kind"`
		NamespaceID       protocol.NamespaceID `cbor:"namespace_id"`
		FinalSequence     uint64               `cbor:"final_sequence"`
		StateRoot         [sha256.Size]byte    `cbor:"state_root"`
		LastReceiptDigest [sha256.Size]byte    `cbor:"last_receipt_digest"`
		AuthorityKeyID    [sha256.Size]byte    `cbor:"authority_key_id"`
		KeyGeneration     uint64               `cbor:"key_generation"`
	}{
		checkpoint.Domain, checkpoint.AdapterKind, checkpoint.NamespaceID,
		checkpoint.FinalSequence, checkpoint.StateRoot,
		checkpoint.LastReceiptDigest, checkpoint.AuthorityKeyID,
		checkpoint.KeyGeneration,
	}
}

type PersistentState struct {
	NextSequence uint64                       `json:"nextSequence"`
	Revision     uint64                       `json:"revision"`
	Candidates   []CandidateRecord            `json:"candidates"`
	States       []FinalizedState             `json:"states"`
	Receipts     []FinalOrderReceipt          `json:"receipts"`
	Resolutions  []ResolutionRecord           `json:"resolutions"`
	Checkpoints  []TrustedCheckpoint          `json:"checkpoints"`
	Idempotency  map[string][sha256.Size]byte `json:"idempotency"`
}

func SortedDigests(values [][sha256.Size]byte) [][sha256.Size]byte {
	result := append([][sha256.Size]byte(nil), values...)
	sort.Slice(result, func(i, j int) bool {
		return strings.Compare(string(result[i][:]), string(result[j][:])) < 0
	})
	return result
}

func zero(value []byte) bool {
	var accumulator byte
	for _, item := range value {
		accumulator |= item
	}
	return accumulator == 0
}
