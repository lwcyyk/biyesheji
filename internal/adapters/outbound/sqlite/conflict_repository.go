package sqlite

import (
	"context"
	"crypto/sha256"
	"errors"
	"math"

	"vpass.local/vpass/internal/protocol"
)

var (
	ErrInvalidConflictSet = errors.New("invalid credential conflict set")
	ErrConflictResolution = errors.New("credential conflict resolution failed")
)

type ConflictCandidateRecord struct {
	NamespaceID            protocol.NamespaceID
	CredentialID           protocol.CredentialID
	Version                uint64
	DescriptorHash         [sha256.Size]byte
	EnvelopeHash           [sha256.Size]byte
	ObservedManifestDigest [sha256.Size]byte
	ObservedAtMilliseconds uint64
}

type RetainedConflict struct {
	ConflictCandidateRecord
	Disposition      string
	ResolutionEvent  *protocol.EventID
	ResolvedAtMillis *uint64
}

type ConflictRepository struct {
	database *Database
}

func NewConflictRepository(database *Database) (*ConflictRepository, error) {
	if database == nil || database.db == nil {
		return nil, ErrInvalidConflictSet
	}
	return &ConflictRepository{database: database}, nil
}

// Retain atomically stores every competing descriptor. It succeeds only when
// at least two distinct candidates are retained for one credential.
func (repository *ConflictRepository) Retain(
	ctx context.Context,
	candidates []ConflictCandidateRecord,
) error {
	if repository == nil || ctx == nil || len(candidates) < 2 {
		return ErrInvalidConflictSet
	}
	first := candidates[0]
	seen := make(map[[sha256.Size]byte]struct{}, len(candidates))
	for _, candidate := range candidates {
		if candidate.NamespaceID != first.NamespaceID ||
			candidate.CredentialID != first.CredentialID ||
			candidate.Version == 0 ||
			bytesAllZero(candidate.NamespaceID[:]) ||
			bytesAllZero(candidate.CredentialID[:]) ||
			bytesAllZero(candidate.DescriptorHash[:]) ||
			bytesAllZero(candidate.EnvelopeHash[:]) ||
			bytesAllZero(candidate.ObservedManifestDigest[:]) ||
			candidate.ObservedAtMilliseconds > math.MaxInt64 {
			return ErrInvalidConflictSet
		}
		if _, duplicate := seen[candidate.DescriptorHash]; duplicate {
			return ErrInvalidConflictSet
		}
		seen[candidate.DescriptorHash] = struct{}{}
	}
	transaction, err := repository.database.BeginImmediate(ctx)
	if err != nil {
		return err
	}
	defer func() { _ = transaction.Rollback() }()
	for _, candidate := range candidates {
		if _, err := transaction.ExecContext(
			ctx,
			`INSERT INTO credential_conflicts_v2 (
  namespace_id, credential_id, credential_version,
  descriptor_hash, envelope_hash, observed_manifest_digest,
  disposition, observed_at_ms
) VALUES (?, ?, ?, ?, ?, ?, 'RETAINED', ?)
ON CONFLICT(namespace_id, credential_id, credential_version, descriptor_hash)
DO NOTHING`,
			candidate.NamespaceID[:], candidate.CredentialID[:],
			candidate.Version, candidate.DescriptorHash[:],
			candidate.EnvelopeHash[:], candidate.ObservedManifestDigest[:],
			candidate.ObservedAtMilliseconds,
		); err != nil {
			return err
		}
	}
	var retained int
	if err := transaction.QueryRowContext(
		ctx,
		`SELECT count(*) FROM credential_conflicts_v2
 WHERE namespace_id = ? AND credential_id = ? AND disposition = 'RETAINED'`,
		first.NamespaceID[:], first.CredentialID[:],
	).Scan(&retained); err != nil {
		return err
	}
	if retained < 2 {
		return ErrInvalidConflictSet
	}
	return transaction.Commit()
}

// Resolve marks exactly one retained descriptor selected and every other
// retained descriptor rejected. The required RESOLVE event must already be
// durable; accepted credential pointers are advanced by a separate verified
// lifecycle transaction.
func (repository *ConflictRepository) Resolve(
	ctx context.Context,
	namespaceID protocol.NamespaceID,
	credentialID protocol.CredentialID,
	selectedVersion uint64,
	selectedDescriptor [sha256.Size]byte,
	resolutionEventID protocol.EventID,
	resolvedAtMilliseconds uint64,
) error {
	if repository == nil || ctx == nil ||
		bytesAllZero(namespaceID[:]) || bytesAllZero(credentialID[:]) ||
		selectedVersion == 0 || bytesAllZero(selectedDescriptor[:]) ||
		bytesAllZero(resolutionEventID[:]) ||
		resolvedAtMilliseconds > math.MaxInt64 {
		return ErrConflictResolution
	}
	transaction, err := repository.database.BeginImmediate(ctx)
	if err != nil {
		return err
	}
	defer func() { _ = transaction.Rollback() }()
	var eventOperation string
	if err := transaction.QueryRowContext(
		ctx,
		`SELECT operation_type FROM operation_events
 WHERE event_id = ? AND namespace_id = ? AND credential_id = ?`,
		resolutionEventID[:], namespaceID[:], credentialID[:],
	).Scan(&eventOperation); err != nil || eventOperation != "RESOLVE" {
		return ErrConflictResolution
	}
	var retained, selected int
	if err := transaction.QueryRowContext(
		ctx,
		`SELECT count(*),
        sum(CASE WHEN credential_version = ? AND descriptor_hash = ? THEN 1 ELSE 0 END)
 FROM credential_conflicts_v2
 WHERE namespace_id = ? AND credential_id = ? AND disposition = 'RETAINED'`,
		selectedVersion, selectedDescriptor[:],
		namespaceID[:], credentialID[:],
	).Scan(&retained, &selected); err != nil ||
		retained < 2 || selected != 1 {
		return ErrConflictResolution
	}
	result, err := transaction.ExecContext(
		ctx,
		`UPDATE credential_conflicts_v2
 SET disposition = CASE
       WHEN credential_version = ? AND descriptor_hash = ? THEN 'SELECTED'
       ELSE 'REJECTED'
     END,
     resolution_event_id = ?,
     resolved_at_ms = ?
 WHERE namespace_id = ? AND credential_id = ? AND disposition = 'RETAINED'`,
		selectedVersion, selectedDescriptor[:], resolutionEventID[:],
		resolvedAtMilliseconds, namespaceID[:], credentialID[:],
	)
	if err != nil {
		return err
	}
	affected, err := result.RowsAffected()
	if err != nil || affected != int64(retained) {
		return ErrConflictResolution
	}
	return transaction.Commit()
}
