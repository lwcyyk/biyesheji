// Package domain implements the infrastructure-independent VPass transparency
// log. Hashing follows the RFC 9162 tree shape while using protocol-frozen
// legacy wire leaf and node domains.
package domain

import (
	"crypto/sha256"
	"crypto/subtle"
	"errors"

	"vpass.local/vpass/internal/protocol"
)

const (
	MaxProofHashes = 64
	MaxTreeLeaves  = uint64(1) << 63
)

var (
	ErrInvalidLeaf        = errors.New("invalid transparency log leaf")
	ErrInvalidTree        = errors.New("invalid transparency tree")
	ErrInvalidInclusion   = errors.New("invalid transparency inclusion proof")
	ErrInvalidConsistency = errors.New("invalid transparency consistency proof")
)

// LogID is a public, random identifier for one append-only log.
type LogID [16]byte

// LogLeaf is the complete public leaf projection. It contains only rotating
// pseudonyms, object/operation types, digests and coarse sequence metadata.
// CredentialID, Origin, account data and encrypted object bodies are absent.
type LogLeaf struct {
	NamespaceCommitment [sha256.Size]byte      `cbor:"namespace_commitment"`
	SubjectPseudonym    [sha256.Size]byte      `cbor:"subject_pseudonym"`
	ObjectType          protocol.ObjectType    `cbor:"object_type"`
	ObjectDigest        [sha256.Size]byte      `cbor:"object_digest"`
	OperationType       protocol.OperationType `cbor:"operation_type"`
	FinalSequence       uint64                 `cbor:"final_sequence"`
	Epoch               uint64                 `cbor:"epoch"`
}

// Validate rejects incomplete and non-registered public projections.
func (leaf LogLeaf) Validate() error {
	if zero(leaf.NamespaceCommitment[:]) || zero(leaf.SubjectPseudonym[:]) ||
		!leaf.ObjectType.Valid() || zero(leaf.ObjectDigest[:]) ||
		!leaf.OperationType.Valid() || leaf.FinalSequence == 0 || leaf.Epoch == 0 {
		return ErrInvalidLeaf
	}
	return nil
}

// EncodeLeaf returns the exact deterministic CBOR bytes committed by LeafHash.
func EncodeLeaf(leaf LogLeaf) ([]byte, error) {
	if err := leaf.Validate(); err != nil {
		return nil, err
	}
	encoded, err := protocol.MarshalDeterministic(leaf)
	if err != nil {
		return nil, ErrInvalidLeaf
	}
	return encoded, nil
}

// LeafHash computes SHA256(0x00 || Domain(LOG-LEAF) || ExactCBOR(leaf)).
func LeafHash(leaf LogLeaf) ([sha256.Size]byte, error) {
	encoded, err := EncodeLeaf(leaf)
	if err != nil {
		return [sha256.Size]byte{}, err
	}
	return hashLeafBytes(encoded), nil
}

func hashLeafBytes(encoded []byte) [sha256.Size]byte {
	hasher := sha256.New()
	_, _ = hasher.Write([]byte{0})
	_, _ = hasher.Write([]byte(protocol.DomainPrefix + "LOG-LEAF"))
	_, _ = hasher.Write(encoded)
	var digest [sha256.Size]byte
	copy(digest[:], hasher.Sum(nil))
	return digest
}

// NodeHash computes SHA256(0x01 || Domain(LOG-NODE) || left || right).
func NodeHash(left, right [sha256.Size]byte) [sha256.Size]byte {
	hasher := sha256.New()
	_, _ = hasher.Write([]byte{1})
	_, _ = hasher.Write([]byte(protocol.DomainPrefix + "LOG-NODE"))
	_, _ = hasher.Write(left[:])
	_, _ = hasher.Write(right[:])
	var digest [sha256.Size]byte
	copy(digest[:], hasher.Sum(nil))
	return digest
}

// EmptyTreeHash is SHA256("") as required by the protocol registry.
func EmptyTreeHash() [sha256.Size]byte { return sha256.Sum256(nil) }

// Tree is a deterministic in-memory decision model. Persistence adapters store
// the same leaf hashes and signed heads; no password material enters this type.
type Tree struct {
	leaves [][sha256.Size]byte
}

// NewTree constructs an empty append-only tree.
func NewTree() *Tree { return &Tree{} }

// RestoreTree verifies and restores already accepted leaf hashes.
func RestoreTree(leaves [][sha256.Size]byte) (*Tree, error) {
	if uint64(len(leaves)) >= MaxTreeLeaves {
		return nil, ErrInvalidTree
	}
	cloned := append([][sha256.Size]byte(nil), leaves...)
	for _, leaf := range cloned {
		if zero(leaf[:]) {
			return nil, ErrInvalidTree
		}
	}
	return &Tree{leaves: cloned}, nil
}

// Append validates and adds exactly one leaf.
func (tree *Tree) Append(leaf LogLeaf) (uint64, [sha256.Size]byte, error) {
	if tree == nil || uint64(len(tree.leaves)) >= MaxTreeLeaves {
		return 0, [sha256.Size]byte{}, ErrInvalidTree
	}
	digest, err := LeafHash(leaf)
	if err != nil {
		return 0, [sha256.Size]byte{}, err
	}
	index := uint64(len(tree.leaves))
	tree.leaves = append(tree.leaves, digest)
	return index, digest, nil
}

// Size returns the accepted leaf count.
func (tree *Tree) Size() uint64 {
	if tree == nil {
		return 0
	}
	return uint64(len(tree.leaves))
}

// Root returns the RFC 9162-shaped Merkle tree hash.
func (tree *Tree) Root() [sha256.Size]byte {
	if tree == nil || len(tree.leaves) == 0 {
		return EmptyTreeHash()
	}
	return treeHash(tree.leaves)
}

// RootAt returns the root for an accepted historical prefix.
func (tree *Tree) RootAt(size uint64) ([sha256.Size]byte, error) {
	if tree == nil || size > uint64(len(tree.leaves)) {
		return [sha256.Size]byte{}, ErrInvalidTree
	}
	if size == 0 {
		return EmptyTreeHash(), nil
	}
	return treeHash(tree.leaves[:size]), nil
}

// InclusionProof returns the audit path for leafIndex in the requested
// historical tree prefix.
func (tree *Tree) InclusionProof(leafIndex, treeSize uint64) ([][sha256.Size]byte, error) {
	if tree == nil || treeSize == 0 || treeSize > uint64(len(tree.leaves)) ||
		leafIndex >= treeSize {
		return nil, ErrInvalidInclusion
	}
	proof := inclusionPath(tree.leaves[:treeSize], int(leafIndex))
	if len(proof) > MaxProofHashes {
		return nil, ErrInvalidInclusion
	}
	return proof, nil
}

// VerifyInclusion checks one RFC 9162 audit path against a receiver-owned root.
func VerifyInclusion(
	leafHash [sha256.Size]byte,
	leafIndex, treeSize uint64,
	proof [][sha256.Size]byte,
	expectedRoot [sha256.Size]byte,
) error {
	if treeSize == 0 || treeSize >= MaxTreeLeaves || leafIndex >= treeSize ||
		len(proof) > MaxProofHashes || zero(leafHash[:]) || zero(expectedRoot[:]) {
		return ErrInvalidInclusion
	}
	index := leafIndex
	last := treeSize - 1
	calculated := leafHash
	for _, sibling := range proof {
		if zero(sibling[:]) {
			return ErrInvalidInclusion
		}
		if index&1 == 1 || index == last {
			calculated = NodeHash(sibling, calculated)
			for index&1 == 0 && index != 0 {
				index >>= 1
				last >>= 1
			}
		} else {
			calculated = NodeHash(calculated, sibling)
		}
		index >>= 1
		last >>= 1
	}
	if last != 0 || subtle.ConstantTimeCompare(calculated[:], expectedRoot[:]) != 1 {
		return ErrInvalidInclusion
	}
	return nil
}

// ConsistencyProof proves that oldSize is a prefix of newSize.
func (tree *Tree) ConsistencyProof(oldSize, newSize uint64) ([][sha256.Size]byte, error) {
	if tree == nil || oldSize > newSize || newSize > uint64(len(tree.leaves)) ||
		newSize == 0 {
		return nil, ErrInvalidConsistency
	}
	if oldSize == 0 || oldSize == newSize {
		return nil, nil
	}
	proof := consistencyPath(tree.leaves[:newSize], int(oldSize), true)
	if len(proof) > MaxProofHashes {
		return nil, ErrInvalidConsistency
	}
	return proof, nil
}

// VerifyConsistency checks an RFC 9162 consistency path.
func VerifyConsistency(
	oldSize, newSize uint64,
	oldRoot, newRoot [sha256.Size]byte,
	proof [][sha256.Size]byte,
) error {
	if oldSize > newSize || newSize == 0 || newSize >= MaxTreeLeaves ||
		len(proof) > MaxProofHashes || zero(oldRoot[:]) || zero(newRoot[:]) {
		return ErrInvalidConsistency
	}
	if oldSize == 0 {
		if len(proof) != 0 || oldRoot != EmptyTreeHash() {
			return ErrInvalidConsistency
		}
		return nil
	}
	if oldSize == newSize {
		if len(proof) != 0 || subtle.ConstantTimeCompare(oldRoot[:], newRoot[:]) != 1 {
			return ErrInvalidConsistency
		}
		return nil
	}

	fn, sn := oldSize-1, newSize-1
	for fn&1 == 1 {
		fn >>= 1
		sn >>= 1
	}
	var first, second [sha256.Size]byte
	offset := 0
	if fn == 0 {
		first, second = oldRoot, oldRoot
	} else {
		if len(proof) == 0 || zero(proof[0][:]) {
			return ErrInvalidConsistency
		}
		first, second = proof[0], proof[0]
		offset = 1
	}
	for ; offset < len(proof); offset++ {
		node := proof[offset]
		if zero(node[:]) || sn == 0 {
			return ErrInvalidConsistency
		}
		if fn&1 == 1 || fn == sn {
			first = NodeHash(node, first)
			second = NodeHash(node, second)
			for fn&1 == 0 && fn != 0 {
				fn >>= 1
				sn >>= 1
			}
		} else {
			second = NodeHash(second, node)
		}
		fn >>= 1
		sn >>= 1
	}
	if sn != 0 ||
		subtle.ConstantTimeCompare(first[:], oldRoot[:]) != 1 ||
		subtle.ConstantTimeCompare(second[:], newRoot[:]) != 1 {
		return ErrInvalidConsistency
	}
	return nil
}

func treeHash(leaves [][sha256.Size]byte) [sha256.Size]byte {
	if len(leaves) == 0 {
		return EmptyTreeHash()
	}
	if len(leaves) == 1 {
		return leaves[0]
	}
	split := largestPowerOfTwoLessThan(len(leaves))
	return NodeHash(treeHash(leaves[:split]), treeHash(leaves[split:]))
}

func inclusionPath(leaves [][sha256.Size]byte, index int) [][sha256.Size]byte {
	if len(leaves) == 1 {
		return nil
	}
	split := largestPowerOfTwoLessThan(len(leaves))
	if index < split {
		path := inclusionPath(leaves[:split], index)
		return append(path, treeHash(leaves[split:]))
	}
	path := inclusionPath(leaves[split:], index-split)
	return append(path, treeHash(leaves[:split]))
}

func consistencyPath(
	leaves [][sha256.Size]byte,
	oldSize int,
	completeOldSubtree bool,
) [][sha256.Size]byte {
	if oldSize == len(leaves) {
		if completeOldSubtree {
			return nil
		}
		return [][sha256.Size]byte{treeHash(leaves)}
	}
	split := largestPowerOfTwoLessThan(len(leaves))
	if oldSize <= split {
		path := consistencyPath(leaves[:split], oldSize, completeOldSubtree)
		return append(path, treeHash(leaves[split:]))
	}
	path := consistencyPath(leaves[split:], oldSize-split, false)
	return append(path, treeHash(leaves[:split]))
}

func largestPowerOfTwoLessThan(value int) int {
	power := 1
	for power<<1 < value {
		power <<= 1
	}
	return power
}

func zero(value []byte) bool {
	var combined byte
	for _, item := range value {
		combined |= item
	}
	return combined == 0
}
