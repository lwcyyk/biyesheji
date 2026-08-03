package domain

import (
	"encoding/hex"
	"fmt"
	"testing"

	"vpass.local/vpass/internal/protocol"
)

func TestMerkleKATAndProofs(t *testing.T) {
	tree := NewTree()
	roots := map[int]string{}
	for index := 1; index <= 7; index++ {
		leaf := testLeaf(byte(index), uint64(index))
		leafIndex, digest, err := tree.Append(leaf)
		if err != nil || leafIndex != uint64(index-1) || zero(digest[:]) {
			t.Fatalf("Append(%d) = %d, %x, %v", index, leafIndex, digest, err)
		}
		if index == 1 || index == 2 || index == 3 || index == 7 {
			root := tree.Root()
			roots[index] = hex.EncodeToString(root[:])
		}
	}
	expected := map[int]string{
		1: "8b49eb056f7433a93142de8f55a1c24148f0fd42b615bab8fc7bc6cbad45b9de",
		2: "4e01f34af56596c9a83e76e72afcd93e013b8d40f4ffa1b8246da0d2a751f523",
		3: "18bf1de9d5e169b9184b035366e964425c6d1e54ad852ba7bb7df50b02b8010e",
		7: "969ae539683a860114143eb2e69bae685f1444e17d268163e585fc9af3f73e79",
	}
	for size, want := range expected {
		if roots[size] != want {
			t.Fatalf("root(%d) = %s, want %s", size, roots[size], want)
		}
	}
	for size := uint64(1); size <= tree.Size(); size++ {
		root, err := tree.RootAt(size)
		if err != nil {
			t.Fatal(err)
		}
		for index := uint64(0); index < size; index++ {
			proof, err := tree.InclusionProof(index, size)
			if err != nil {
				t.Fatalf("InclusionProof(%d,%d): %v", index, size, err)
			}
			if err := VerifyInclusion(
				tree.leaves[index], index, size, proof, root,
			); err != nil {
				t.Fatalf("VerifyInclusion(%d,%d): %v", index, size, err)
			}
			if len(proof) > 3 {
				t.Fatalf("proof hashes(%d,%d) = %d", index, size, len(proof))
			}
		}
	}
}

func TestConsistencyProofExhaustive(t *testing.T) {
	tree := NewTree()
	for index := 1; index <= 257; index++ {
		marker := byte((index % 200) + 1)
		if _, _, err := tree.Append(testLeaf(marker, uint64(index))); err != nil {
			t.Fatal(err)
		}
	}
	for newSize := uint64(1); newSize <= tree.Size(); newSize++ {
		newRoot, _ := tree.RootAt(newSize)
		for oldSize := uint64(0); oldSize <= newSize; oldSize++ {
			oldRoot, _ := tree.RootAt(oldSize)
			proof, err := tree.ConsistencyProof(oldSize, newSize)
			if err != nil {
				t.Fatalf("proof(%d,%d): %v", oldSize, newSize, err)
			}
			if err := VerifyConsistency(
				oldSize, newSize, oldRoot, newRoot, proof,
			); err != nil {
				t.Fatalf("verify(%d,%d,len=%d): %v", oldSize, newSize, len(proof), err)
			}
		}
	}
}

func TestProofMutationRejected(t *testing.T) {
	tree := NewTree()
	for index := 1; index <= 7; index++ {
		_, _, _ = tree.Append(testLeaf(byte(index), uint64(index)))
	}
	root := tree.Root()
	proof, _ := tree.InclusionProof(3, 7)
	proof[0][0] ^= 0x80
	if VerifyInclusion(tree.leaves[3], 3, 7, proof, root) == nil {
		t.Fatal("mutated inclusion proof accepted")
	}
	oldRoot, _ := tree.RootAt(3)
	consistency, _ := tree.ConsistencyProof(3, 7)
	consistency[len(consistency)-1][0] ^= 0x80
	if VerifyConsistency(3, 7, oldRoot, root, consistency) == nil {
		t.Fatal("mutated consistency proof accepted")
	}
}

func TestMillionLeafProofBoundShape(t *testing.T) {
	// The RFC 9162 audit path height is ceil(log2(n)); this boundary test avoids
	// allocating one million leaves while still fixing the requirement.
	size := uint64(1_000_000)
	hashes := 0
	for nodes := size; nodes > 1; nodes = (nodes + 1) / 2 {
		hashes++
	}
	if hashes > 32 {
		t.Fatalf("proof bound for %d leaves = %d", size, hashes)
	}
}

func testLeaf(marker byte, sequence uint64) LogLeaf {
	var namespace, subject, object [32]byte
	for index := range namespace {
		namespace[index] = marker
		subject[index] = marker + 1
		object[index] = marker + 2
	}
	return LogLeaf{
		NamespaceCommitment: namespace,
		SubjectPseudonym:    subject,
		ObjectType:          protocol.ObjectTypeOperationEvent,
		ObjectDigest:        object,
		OperationType:       protocol.OperationResolve,
		FinalSequence:       sequence,
		Epoch:               1 + sequence/100,
	}
}

func ExampleTree() {
	tree := NewTree()
	_, _, _ = tree.Append(testLeaf(1, 1))
	fmt.Println(tree.Size())
	// Output: 1
}

func FuzzVerifyInclusion(f *testing.F) {
	tree := NewTree()
	for index := 1; index <= 7; index++ {
		_, _, _ = tree.Append(testLeaf(byte(index), uint64(index)))
	}
	proof, _ := tree.InclusionProof(3, 7)
	raw := make([]byte, 0, len(proof)*32)
	for _, item := range proof {
		raw = append(raw, item[:]...)
	}
	root := tree.Root()
	leaf := tree.leaves[3]
	f.Add(uint64(3), uint64(7), raw)
	f.Fuzz(func(t *testing.T, index, size uint64, encoded []byte) {
		if len(encoded)%32 != 0 || len(encoded)/32 > MaxProofHashes {
			return
		}
		candidate := make([][32]byte, len(encoded)/32)
		for offset := range candidate {
			copy(candidate[offset][:], encoded[offset*32:(offset+1)*32])
		}
		_ = VerifyInclusion(leaf, index, size, candidate, root)
	})
}
