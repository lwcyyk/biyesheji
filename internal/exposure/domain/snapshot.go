// Package domain defines deterministic incident snapshots and affected-set
// commitments. These roots provide binding only; they do not by themselves
// prove semantic correctness or global evidence completeness.
package domain

import (
	"bytes"
	"crypto/sha256"
	"errors"
	"sort"

	"vdns.local/vdns/internal/protocol"
)

const (
	SnapshotFormatVersion = uint64(1)
	MaxSnapshotEntries    = 1_000_000
	MaxAffectedItems      = 100_000
)

var (
	ErrInvalidIncidentSnapshot = errors.New("invalid incident snapshot")
	ErrInvalidAffectedSet      = errors.New("invalid affected set")
)

type SnapshotEntry struct {
	CredentialID      protocol.CredentialID `cbor:"credential_id"`
	CredentialVersion uint64                `cbor:"credential_version"`
	EventDigest       [sha256.Size]byte     `cbor:"event_digest"`
	Epoch             uint64                `cbor:"epoch"`
	ObservedBucket    uint64                `cbor:"observed_bucket"`
}

type IncidentSnapshot struct {
	FormatVersion      uint64               `cbor:"format_version"`
	NamespaceID        protocol.NamespaceID `cbor:"namespace_id"`
	WindowStartBucket  uint64               `cbor:"window_start_bucket"`
	WindowEndBucket    uint64               `cbor:"window_end_bucket"`
	SourceCheckpoint   [sha256.Size]byte    `cbor:"source_checkpoint"`
	IncidentCommitment [sha256.Size]byte    `cbor:"incident_commitment"`
	Entries            []SnapshotEntry      `cbor:"entries"`
	SnapshotRoot       [sha256.Size]byte    `cbor:"snapshot_root"`
}

type snapshotBody struct {
	FormatVersion      uint64               `cbor:"format_version"`
	NamespaceID        protocol.NamespaceID `cbor:"namespace_id"`
	WindowStartBucket  uint64               `cbor:"window_start_bucket"`
	WindowEndBucket    uint64               `cbor:"window_end_bucket"`
	SourceCheckpoint   [sha256.Size]byte    `cbor:"source_checkpoint"`
	IncidentCommitment [sha256.Size]byte    `cbor:"incident_commitment"`
	EntriesRoot        [sha256.Size]byte    `cbor:"entries_root"`
	EntryCount         uint64               `cbor:"entry_count"`
}

func NewIncidentSnapshot(
	namespaceID protocol.NamespaceID,
	windowStart, windowEnd uint64,
	sourceCheckpoint, incidentCommitment [sha256.Size]byte,
	entries []SnapshotEntry,
) (IncidentSnapshot, error) {
	if exposureZero(namespaceID[:]) || windowStart == 0 || windowEnd < windowStart ||
		exposureZero(sourceCheckpoint[:]) || exposureZero(incidentCommitment[:]) ||
		len(entries) == 0 || len(entries) > MaxSnapshotEntries {
		return IncidentSnapshot{}, ErrInvalidIncidentSnapshot
	}
	canonical := append([]SnapshotEntry(nil), entries...)
	for _, entry := range canonical {
		if exposureZero(entry.CredentialID[:]) || entry.CredentialVersion == 0 ||
			exposureZero(entry.EventDigest[:]) || entry.Epoch == 0 ||
			entry.ObservedBucket < windowStart || entry.ObservedBucket > windowEnd {
			return IncidentSnapshot{}, ErrInvalidIncidentSnapshot
		}
	}
	sortSnapshotEntries(canonical)
	for index := 1; index < len(canonical); index++ {
		if canonical[index] == canonical[index-1] {
			return IncidentSnapshot{}, ErrInvalidIncidentSnapshot
		}
	}
	entryRoot, err := merkleRoot(protocol.DomainPrefix+"INCIDENT-SNAPSHOT", canonical)
	if err != nil {
		return IncidentSnapshot{}, ErrInvalidIncidentSnapshot
	}
	body := snapshotBody{
		FormatVersion: SnapshotFormatVersion, NamespaceID: namespaceID,
		WindowStartBucket: windowStart, WindowEndBucket: windowEnd,
		SourceCheckpoint: sourceCheckpoint, IncidentCommitment: incidentCommitment,
		EntriesRoot: entryRoot, EntryCount: uint64(len(canonical)),
	}
	encoded, err := protocol.MarshalDeterministic(body)
	if err != nil {
		return IncidentSnapshot{}, ErrInvalidIncidentSnapshot
	}
	return IncidentSnapshot{
		FormatVersion: SnapshotFormatVersion, NamespaceID: namespaceID,
		WindowStartBucket: windowStart, WindowEndBucket: windowEnd,
		SourceCheckpoint: sourceCheckpoint, IncidentCommitment: incidentCommitment,
		Entries: canonical, SnapshotRoot: sha256.Sum256(encoded),
	}, nil
}

func (snapshot IncidentSnapshot) Validate() error {
	rebuilt, err := NewIncidentSnapshot(
		snapshot.NamespaceID, snapshot.WindowStartBucket, snapshot.WindowEndBucket,
		snapshot.SourceCheckpoint, snapshot.IncidentCommitment, snapshot.Entries,
	)
	if err != nil || rebuilt.FormatVersion != snapshot.FormatVersion ||
		rebuilt.SnapshotRoot != snapshot.SnapshotRoot ||
		!snapshotEntriesEqual(rebuilt.Entries, snapshot.Entries) {
		return ErrInvalidIncidentSnapshot
	}
	return nil
}

type AffectedItem struct {
	CredentialID protocol.CredentialID `cbor:"credential_id"`
	ReasonDigest [sha256.Size]byte     `cbor:"reason_digest"`
}

type AffectedSet struct {
	SnapshotRoot       [sha256.Size]byte `cbor:"snapshot_root"`
	IncidentCommitment [sha256.Size]byte `cbor:"incident_commitment"`
	Items              []AffectedItem    `cbor:"items"`
	AffectedRoot       [sha256.Size]byte `cbor:"affected_root"`
}

type affectedBody struct {
	SnapshotRoot       [sha256.Size]byte `cbor:"snapshot_root"`
	IncidentCommitment [sha256.Size]byte `cbor:"incident_commitment"`
	ItemsRoot          [sha256.Size]byte `cbor:"items_root"`
	ItemCount          uint64            `cbor:"item_count"`
}

func NewAffectedSet(snapshot IncidentSnapshot, items []AffectedItem) (AffectedSet, error) {
	if snapshot.Validate() != nil || len(items) == 0 || len(items) > MaxAffectedItems {
		return AffectedSet{}, ErrInvalidAffectedSet
	}
	inSnapshot := make(map[protocol.CredentialID]struct{}, len(snapshot.Entries))
	for _, entry := range snapshot.Entries {
		inSnapshot[entry.CredentialID] = struct{}{}
	}
	canonical := append([]AffectedItem(nil), items...)
	for _, item := range canonical {
		if exposureZero(item.CredentialID[:]) || exposureZero(item.ReasonDigest[:]) {
			return AffectedSet{}, ErrInvalidAffectedSet
		}
		if _, exists := inSnapshot[item.CredentialID]; !exists {
			return AffectedSet{}, ErrInvalidAffectedSet
		}
	}
	sort.Slice(canonical, func(i, j int) bool {
		return bytes.Compare(canonical[i].CredentialID[:], canonical[j].CredentialID[:]) < 0
	})
	for index := 1; index < len(canonical); index++ {
		if canonical[index].CredentialID == canonical[index-1].CredentialID {
			return AffectedSet{}, ErrInvalidAffectedSet
		}
	}
	itemsRoot, err := merkleRoot(protocol.DomainPrefix+"AFFECTED-SET", canonical)
	if err != nil {
		return AffectedSet{}, ErrInvalidAffectedSet
	}
	body := affectedBody{
		SnapshotRoot:       snapshot.SnapshotRoot,
		IncidentCommitment: snapshot.IncidentCommitment,
		ItemsRoot:          itemsRoot, ItemCount: uint64(len(canonical)),
	}
	encoded, err := protocol.MarshalDeterministic(body)
	if err != nil {
		return AffectedSet{}, ErrInvalidAffectedSet
	}
	return AffectedSet{
		SnapshotRoot:       snapshot.SnapshotRoot,
		IncidentCommitment: snapshot.IncidentCommitment,
		Items:              canonical, AffectedRoot: sha256.Sum256(encoded),
	}, nil
}

func (set AffectedSet) Validate(snapshot IncidentSnapshot) error {
	rebuilt, err := NewAffectedSet(snapshot, set.Items)
	if err != nil || rebuilt.SnapshotRoot != set.SnapshotRoot ||
		rebuilt.IncidentCommitment != set.IncidentCommitment ||
		rebuilt.AffectedRoot != set.AffectedRoot {
		return ErrInvalidAffectedSet
	}
	return nil
}

func (set AffectedSet) Contains(id protocol.CredentialID) bool {
	index := sort.Search(len(set.Items), func(index int) bool {
		return bytes.Compare(set.Items[index].CredentialID[:], id[:]) >= 0
	})
	return index < len(set.Items) && set.Items[index].CredentialID == id
}

func sortSnapshotEntries(entries []SnapshotEntry) {
	sort.Slice(entries, func(i, j int) bool {
		left, right := entries[i], entries[j]
		if comparison := bytes.Compare(left.CredentialID[:], right.CredentialID[:]); comparison != 0 {
			return comparison < 0
		}
		if left.ObservedBucket != right.ObservedBucket {
			return left.ObservedBucket < right.ObservedBucket
		}
		if left.CredentialVersion != right.CredentialVersion {
			return left.CredentialVersion < right.CredentialVersion
		}
		return bytes.Compare(left.EventDigest[:], right.EventDigest[:]) < 0
	})
}

func snapshotEntriesEqual(left, right []SnapshotEntry) bool {
	if len(left) != len(right) {
		return false
	}
	for index := range left {
		if left[index] != right[index] {
			return false
		}
	}
	return true
}

func merkleRoot[T any](domain string, values []T) ([sha256.Size]byte, error) {
	level := make([][sha256.Size]byte, len(values))
	for index, value := range values {
		encoded, err := protocol.MarshalDeterministic(value)
		if err != nil {
			return [sha256.Size]byte{}, err
		}
		hasher := sha256.New()
		_, _ = hasher.Write([]byte{0})
		_, _ = hasher.Write([]byte(domain + "-LEAF"))
		_, _ = hasher.Write(encoded)
		copy(level[index][:], hasher.Sum(nil))
	}
	for len(level) > 1 {
		next := make([][sha256.Size]byte, 0, (len(level)+1)/2)
		for index := 0; index < len(level); index += 2 {
			right := index + 1
			if right == len(level) {
				next = append(next, level[index])
				continue
			}
			hasher := sha256.New()
			_, _ = hasher.Write([]byte{1})
			_, _ = hasher.Write([]byte(domain + "-NODE"))
			_, _ = hasher.Write(level[index][:])
			_, _ = hasher.Write(level[right][:])
			var digest [sha256.Size]byte
			copy(digest[:], hasher.Sum(nil))
			next = append(next, digest)
		}
		level = next
	}
	return level[0], nil
}

func exposureZero(value []byte) bool {
	var combined byte
	for _, item := range value {
		combined |= item
	}
	return combined == 0
}
