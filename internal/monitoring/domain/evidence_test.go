package domain

import (
	"bytes"
	"crypto/ed25519"
	"testing"

	"vdns.local/vdns/internal/protocol"
	transparencydomain "vdns.local/vdns/internal/transparency/domain"
)

func TestMonitorDetectsForkRollbackAndBadConsistency(t *testing.T) {
	namespace := monitorNamespace(0x11)
	key := ed25519.NewKeyFromSeed(bytes.Repeat([]byte{0x21}, ed25519.SeedSize))
	base := monitorHead(t, key, namespace, 10, monitorHash(1), 20)
	legal := monitorHead(t, key, namespace, 11, monitorHash(2), 21)
	if finding, err := CompareTreeHeads(namespace, base, legal, true); err != nil || finding != nil {
		t.Fatalf("legal append = %+v, %v", finding, err)
	}
	tests := []struct {
		name       string
		head       *transparencydomain.SignedTreeHead
		consistent bool
		want       FindingKind
	}{
		{"split", monitorHead(t, key, namespace, 10, monitorHash(3), 20), true, FindingSplitView},
		{"rollback", monitorHead(t, key, namespace, 9, monitorHash(4), 19), true, FindingTreeRollback},
		{"bad consistency", legal, false, FindingBadConsistency},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			finding, err := CompareTreeHeads(namespace, base, test.head, test.consistent)
			if err != nil || finding == nil || finding.Kind != test.want ||
				evidenceZero(finding.EvidenceDigest[:]) {
				t.Fatalf("finding = %+v, %v", finding, err)
			}
		})
	}
}

func TestMonitorDescriptorAndAnchorEvidence(t *testing.T) {
	namespace := monitorNamespace(0x31)
	subject := monitorHash(0x41)
	finding, err := CompareDescriptors(
		namespace, subject, 7, monitorHash(1), monitorHash(2),
	)
	if err != nil || finding == nil || finding.Kind != FindingDoubleDescriptor ||
		finding.SubjectCommitment == nil {
		t.Fatalf("descriptor finding = %+v, %v", finding, err)
	}
	if none, err := CompareDescriptors(
		namespace, subject, 7, monitorHash(1), monitorHash(1),
	); err != nil || none != nil {
		t.Fatalf("equal descriptor = %+v, %v", none, err)
	}
	anchor, err := CompareAnnouncements(
		namespace, monitorHash(3), monitorHash(4), 9, 8,
	)
	if err != nil || anchor == nil || anchor.Kind != FindingAnchorConflict {
		t.Fatalf("anchor = %+v, %v", anchor, err)
	}
}

func monitorHead(
	t *testing.T,
	key ed25519.PrivateKey,
	namespace protocol.NamespaceID,
	size uint64,
	root [32]byte,
	sequence uint64,
) *transparencydomain.SignedTreeHead {
	t.Helper()
	head, err := transparencydomain.SignTreeHead(
		key, "monitor-chain", 1,
		transparencydomain.TreeHeadPayload{
			NamespaceID: namespace,
			LogID:       transparencydomain.LogID{1, 2, 3},
			TreeSize:    size, RootHash: root,
			FinalSequence: sequence, SuiteID: protocol.SuiteID,
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	return head
}

func monitorNamespace(marker byte) protocol.NamespaceID {
	var value protocol.NamespaceID
	for index := range value {
		value[index] = marker
	}
	return value
}

func monitorHash(marker byte) [32]byte {
	var value [32]byte
	for index := range value {
		value[index] = marker
	}
	return value
}
