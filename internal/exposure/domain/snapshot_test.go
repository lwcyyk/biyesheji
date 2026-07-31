package domain

import (
	"testing"

	"vdns.local/vdns/internal/protocol"
)

func TestIncidentSnapshotAndAffectedRootAreCanonicalBindings(t *testing.T) {
	entries := []SnapshotEntry{
		{
			CredentialID: protocol.CredentialID{2}, CredentialVersion: 2,
			EventDigest: [32]byte{4}, Epoch: 8, ObservedBucket: 102,
		},
		{
			CredentialID: protocol.CredentialID{1}, CredentialVersion: 1,
			EventDigest: [32]byte{3}, Epoch: 7, ObservedBucket: 101,
		},
	}
	snapshot, err := NewIncidentSnapshot(
		protocol.NamespaceID{1}, 100, 110, [32]byte{5}, [32]byte{6}, entries,
	)
	if err != nil {
		t.Fatal(err)
	}
	if snapshot.Entries[0].CredentialID != entries[1].CredentialID ||
		snapshot.Validate() != nil {
		t.Fatal("snapshot did not canonicalize its entry order")
	}
	reordered, err := NewIncidentSnapshot(
		protocol.NamespaceID{1}, 100, 110, [32]byte{5}, [32]byte{6},
		[]SnapshotEntry{entries[1], entries[0]},
	)
	if err != nil || reordered.SnapshotRoot != snapshot.SnapshotRoot {
		t.Fatalf("reordered snapshot root mismatch: %v", err)
	}
	affected, err := NewAffectedSet(snapshot, []AffectedItem{
		{CredentialID: entries[0].CredentialID, ReasonDigest: [32]byte{7}},
		{CredentialID: entries[1].CredentialID, ReasonDigest: [32]byte{8}},
	})
	if err != nil || affected.Validate(snapshot) != nil ||
		!affected.Contains(entries[0].CredentialID) {
		t.Fatalf("affected set = %+v, %v", affected, err)
	}
	changedIncident := snapshot
	changedIncident.IncidentCommitment[0] ^= 1
	if affected.Validate(changedIncident) == nil {
		t.Fatal("AffectedRoot accepted a different incident commitment")
	}
}

func TestSnapshotRejectsWindowAndAffectedScopeViolations(t *testing.T) {
	entry := SnapshotEntry{
		CredentialID: protocol.CredentialID{1}, CredentialVersion: 1,
		EventDigest: [32]byte{2}, Epoch: 3, ObservedBucket: 99,
	}
	if _, err := NewIncidentSnapshot(
		protocol.NamespaceID{1}, 100, 110, [32]byte{3}, [32]byte{4}, []SnapshotEntry{entry},
	); err != ErrInvalidIncidentSnapshot {
		t.Fatalf("out-of-window entry = %v", err)
	}
	entry.ObservedBucket = 100
	snapshot, err := NewIncidentSnapshot(
		protocol.NamespaceID{1}, 100, 110, [32]byte{3}, [32]byte{4}, []SnapshotEntry{entry},
	)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := NewAffectedSet(snapshot, []AffectedItem{{
		CredentialID: protocol.CredentialID{9}, ReasonDigest: [32]byte{5},
	}}); err != ErrInvalidAffectedSet {
		t.Fatalf("out-of-snapshot affected item = %v", err)
	}
}

func FuzzIncidentSnapshotWindow(f *testing.F) {
	f.Add(uint64(10), uint64(20), uint64(15))
	f.Add(uint64(20), uint64(10), uint64(15))
	f.Fuzz(func(t *testing.T, start, end, observed uint64) {
		entry := SnapshotEntry{
			CredentialID: protocol.CredentialID{1}, CredentialVersion: 1,
			EventDigest: [32]byte{2}, Epoch: 1, ObservedBucket: observed,
		}
		snapshot, err := NewIncidentSnapshot(
			protocol.NamespaceID{1}, start, end, [32]byte{3}, [32]byte{4},
			[]SnapshotEntry{entry},
		)
		if err != nil {
			return
		}
		if snapshot.Validate() != nil || observed < start || observed > end {
			t.Fatal("accepted snapshot violated its fixed window")
		}
	})
}
