package application

import (
	"bytes"
	"crypto/ed25519"
	"testing"

	"vpass.local/vpass/internal/protocol"
	transparencydomain "vpass.local/vpass/internal/transparency/domain"
)

func TestLogAppendSignsMonotonicHeadsAndProofs(t *testing.T) {
	namespace := protocol.NamespaceID{1, 2, 3}
	logID := transparencydomain.LogID{4, 5, 6}
	privateKey := ed25519.NewKeyFromSeed(bytes.Repeat([]byte{0x41}, ed25519.SeedSize))
	log, err := NewLog(namespace, logID, "log-chain", 2, privateKey)
	if err != nil {
		t.Fatal(err)
	}
	var heads []*transparencydomain.SignedTreeHead
	for index := 1; index <= 7; index++ {
		_, _, head, err := log.Append(logLeaf(byte(index), uint64(index)))
		if err != nil {
			t.Fatal(err)
		}
		heads = append(heads, head)
	}
	if heads[6].Payload().TreeSize != 7 ||
		heads[6].Payload().FinalSequence != 7 {
		t.Fatalf("head = %+v", heads[6].Payload())
	}
	inclusion, err := log.InclusionProof(3, 7)
	if err != nil || transparencydomain.VerifyInclusion(
		mustLeafHash(t, logLeaf(4, 4)), 3, 7, inclusion,
		heads[6].Payload().RootHash,
	) != nil {
		t.Fatalf("inclusion = %v", err)
	}
	consistency, err := log.ConsistencyProof(3, 7)
	if err != nil || transparencydomain.VerifyConsistency(
		3, 7, heads[2].Payload().RootHash, heads[6].Payload().RootHash,
		consistency,
	) != nil {
		t.Fatalf("consistency = %v", err)
	}
	if _, _, _, err := log.Append(logLeaf(8, 7)); err != ErrLogSequence {
		t.Fatalf("non-monotonic sequence error = %v", err)
	}
}

func logLeaf(marker byte, sequence uint64) transparencydomain.LogLeaf {
	hash := func(value byte) [32]byte {
		var result [32]byte
		for index := range result {
			result[index] = value
		}
		return result
	}
	return transparencydomain.LogLeaf{
		NamespaceCommitment: hash(marker),
		SubjectPseudonym:    hash(marker + 1),
		ObjectType:          protocol.ObjectTypeOperationEvent,
		ObjectDigest:        hash(marker + 2),
		OperationType:       protocol.OperationResolve,
		FinalSequence:       sequence, Epoch: 1,
	}
}

func mustLeafHash(
	t *testing.T,
	leaf transparencydomain.LogLeaf,
) [32]byte {
	t.Helper()
	hash, err := transparencydomain.LeafHash(leaf)
	if err != nil {
		t.Fatal(err)
	}
	return hash
}
