// Package domain defines secret-free, independently verifiable monitor
// findings for log, descriptor and announcement equivocation.
package domain

import (
	"crypto/sha256"
	"errors"

	"vpass.local/vpass/internal/protocol"
	transparencydomain "vpass.local/vpass/internal/transparency/domain"
)

var ErrInvalidEvidence = errors.New("invalid monitor evidence")

type FindingKind uint8

const (
	FindingSplitView        FindingKind = 1
	FindingTreeRollback     FindingKind = 2
	FindingBadConsistency   FindingKind = 3
	FindingDoubleDescriptor FindingKind = 4
	FindingAnchorConflict   FindingKind = 5
)

func (kind FindingKind) Valid() bool {
	return kind >= FindingSplitView && kind <= FindingAnchorConflict
}

// Evidence contains only signed-object digests and public counters. Raw
// passwords, Origin, account identifiers and credential objects are absent.
type Evidence struct {
	Kind              FindingKind          `cbor:"kind"`
	NamespaceID       protocol.NamespaceID `cbor:"namespace_id"`
	FirstObjectHash   [sha256.Size]byte    `cbor:"first_object_hash"`
	SecondObjectHash  [sha256.Size]byte    `cbor:"second_object_hash"`
	FirstPosition     uint64               `cbor:"first_position"`
	SecondPosition    uint64               `cbor:"second_position"`
	SubjectCommitment *[sha256.Size]byte   `cbor:"subject_commitment"`
	EvidenceDigest    [sha256.Size]byte    `cbor:"evidence_digest"`
}

type evidenceBody struct {
	Kind              FindingKind          `cbor:"kind"`
	NamespaceID       protocol.NamespaceID `cbor:"namespace_id"`
	FirstObjectHash   [sha256.Size]byte    `cbor:"first_object_hash"`
	SecondObjectHash  [sha256.Size]byte    `cbor:"second_object_hash"`
	FirstPosition     uint64               `cbor:"first_position"`
	SecondPosition    uint64               `cbor:"second_position"`
	SubjectCommitment *[sha256.Size]byte   `cbor:"subject_commitment"`
}

// Validate recomputes the canonical evidence digest.
func (evidence Evidence) Validate() error {
	if !evidence.Kind.Valid() || evidenceZero(evidence.NamespaceID[:]) ||
		evidenceZero(evidence.FirstObjectHash[:]) ||
		evidenceZero(evidence.SecondObjectHash[:]) ||
		evidence.FirstPosition == 0 || evidence.SecondPosition == 0 ||
		evidence.FirstObjectHash == evidence.SecondObjectHash ||
		evidenceZero(evidence.EvidenceDigest[:]) {
		return ErrInvalidEvidence
	}
	if evidence.SubjectCommitment != nil &&
		evidenceZero(evidence.SubjectCommitment[:]) {
		return ErrInvalidEvidence
	}
	body := evidenceBody{
		Kind: evidence.Kind, NamespaceID: evidence.NamespaceID,
		FirstObjectHash:   evidence.FirstObjectHash,
		SecondObjectHash:  evidence.SecondObjectHash,
		FirstPosition:     evidence.FirstPosition,
		SecondPosition:    evidence.SecondPosition,
		SubjectCommitment: cloneEvidenceHash(evidence.SubjectCommitment),
	}
	encoded, err := protocol.MarshalDeterministic(body)
	if err != nil || sha256.Sum256(encoded) != evidence.EvidenceDigest {
		return ErrInvalidEvidence
	}
	return nil
}

func NewEvidence(
	kind FindingKind,
	namespaceID protocol.NamespaceID,
	firstHash, secondHash [sha256.Size]byte,
	firstPosition, secondPosition uint64,
	subject *[sha256.Size]byte,
) (Evidence, error) {
	body := evidenceBody{
		Kind: kind, NamespaceID: namespaceID,
		FirstObjectHash: firstHash, SecondObjectHash: secondHash,
		FirstPosition: firstPosition, SecondPosition: secondPosition,
		SubjectCommitment: cloneEvidenceHash(subject),
	}
	if !kind.Valid() || evidenceZero(namespaceID[:]) ||
		evidenceZero(firstHash[:]) || evidenceZero(secondHash[:]) ||
		firstPosition == 0 || secondPosition == 0 ||
		firstHash == secondHash {
		return Evidence{}, ErrInvalidEvidence
	}
	if subject != nil && evidenceZero(subject[:]) {
		return Evidence{}, ErrInvalidEvidence
	}
	encoded, err := protocol.MarshalDeterministic(body)
	if err != nil {
		return Evidence{}, ErrInvalidEvidence
	}
	digest := sha256.Sum256(encoded)
	return Evidence{
		Kind: body.Kind, NamespaceID: body.NamespaceID,
		FirstObjectHash:  body.FirstObjectHash,
		SecondObjectHash: body.SecondObjectHash,
		FirstPosition:    body.FirstPosition, SecondPosition: body.SecondPosition,
		SubjectCommitment: cloneEvidenceHash(body.SubjectCommitment),
		EvidenceDigest:    digest,
	}, nil
}

// CompareTreeHeads detects same-size split views, rollback and missing
// consistency. A valid monotonic append returns no finding.
func CompareTreeHeads(
	namespaceID protocol.NamespaceID,
	trusted, candidate *transparencydomain.SignedTreeHead,
	consistencyValid bool,
) (*Evidence, error) {
	if trusted == nil || candidate == nil {
		return nil, ErrInvalidEvidence
	}
	left, right := trusted.Payload(), candidate.Payload()
	if left.NamespaceID != namespaceID || right.NamespaceID != namespaceID ||
		left.LogID != right.LogID {
		return nil, ErrInvalidEvidence
	}
	var kind FindingKind
	switch {
	case right.TreeSize == left.TreeSize && right.RootHash != left.RootHash:
		kind = FindingSplitView
	case right.TreeSize < left.TreeSize ||
		right.FinalSequence < left.FinalSequence:
		kind = FindingTreeRollback
	case right.TreeSize > left.TreeSize && !consistencyValid:
		kind = FindingBadConsistency
	default:
		return nil, nil
	}
	evidence, err := NewEvidence(
		kind, namespaceID, trusted.Digest(), candidate.Digest(),
		left.TreeSize, right.TreeSize, nil,
	)
	if err != nil {
		return nil, err
	}
	return &evidence, nil
}

// CompareDescriptors detects two different descriptor objects for the same
// private subject commitment and active version.
func CompareDescriptors(
	namespaceID protocol.NamespaceID,
	subjectCommitment [sha256.Size]byte,
	version uint64,
	firstDescriptor, secondDescriptor [sha256.Size]byte,
) (*Evidence, error) {
	if version == 0 || evidenceZero(subjectCommitment[:]) {
		return nil, ErrInvalidEvidence
	}
	if firstDescriptor == secondDescriptor {
		return nil, nil
	}
	evidence, err := NewEvidence(
		FindingDoubleDescriptor, namespaceID,
		firstDescriptor, secondDescriptor,
		version, version, &subjectCommitment,
	)
	if err != nil {
		return nil, err
	}
	return &evidence, nil
}

// CompareAnnouncements detects rollback or conflicting checkpoint digests.
func CompareAnnouncements(
	namespaceID protocol.NamespaceID,
	trustedDigest, candidateDigest [sha256.Size]byte,
	trustedHeight, candidateHeight uint64,
) (*Evidence, error) {
	if candidateHeight > trustedHeight {
		return nil, nil
	}
	if candidateHeight == trustedHeight && candidateDigest == trustedDigest {
		return nil, nil
	}
	evidence, err := NewEvidence(
		FindingAnchorConflict, namespaceID,
		trustedDigest, candidateDigest,
		trustedHeight, candidateHeight, nil,
	)
	if err != nil {
		return nil, err
	}
	return &evidence, nil
}

func cloneEvidenceHash(value *[sha256.Size]byte) *[sha256.Size]byte {
	if value == nil {
		return nil
	}
	cloned := *value
	return &cloned
}

func evidenceZero(value []byte) bool {
	var combined byte
	for _, item := range value {
		combined |= item
	}
	return combined == 0
}
