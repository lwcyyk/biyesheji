package sqlite

import (
	"context"
	"crypto/rand"
	"crypto/sha256"
	"database/sql"
	"errors"
	"io"
	"math"
	"strings"

	"vdns.local/vdns/internal/platform"
	"vdns.local/vdns/internal/protocol"
)

const (
	outboxLeaseTokenSize = 16
	maxOutboxClaim       = 100
	maxOutboxLeaseMillis = uint64(10 * 60 * 1000)
)

var (
	ErrInvalidOutboxRequest = errors.New("invalid event outbox request")
	ErrOutboxLeaseLost      = errors.New("event outbox lease is missing or expired")
	ErrOutboxStateConflict  = errors.New("event outbox state conflict")
)

type OutboxLeaseToken [outboxLeaseTokenSize]byte
type LogID [16]byte

// OutboxJob contains the exact immutable event and object address originally
// committed with the event. Workers must publish these bytes, not reseal.
type OutboxJob struct {
	EventID          protocol.EventID
	SigInputCBOR     []byte
	DeviceSignature  protocol.Signature
	EventDigest      [sha256.Size]byte
	ObjectReference  platform.ObjectRef
	RetryCount       uint64
	LeaseToken       OutboxLeaseToken
	LeaseExpiresAtMS uint64
}

type ClaimOutboxRequest struct {
	NowMilliseconds   uint64
	LeaseMilliseconds uint64
	Limit             uint64
}

type MarkOutboxRetryRequest struct {
	EventID         protocol.EventID
	LeaseToken      OutboxLeaseToken
	NowMilliseconds uint64
	NextAttemptAtMS uint64
	ErrorCode       string
}

type MarkLogIncludedRequest struct {
	EventID          protocol.EventID
	LeaseToken       OutboxLeaseToken
	NowMilliseconds  uint64
	LogID            LogID
	LeafIndex        uint64
	IncludedTreeSize uint64
}

// ClaimReadyOutbox leases ready jobs without changing their durable
// publication state. If a worker crashes, another worker can reclaim them only
// after the persisted expiry.
func (repository *OperationRepository) ClaimReadyOutbox(
	ctx context.Context,
	request ClaimOutboxRequest,
) ([]OutboxJob, error) {
	if repository == nil || repository.database == nil || ctx == nil ||
		request.NowMilliseconds > math.MaxInt64 ||
		request.LeaseMilliseconds == 0 || request.LeaseMilliseconds > maxOutboxLeaseMillis ||
		request.Limit == 0 || request.Limit > maxOutboxClaim ||
		request.NowMilliseconds > math.MaxUint64-request.LeaseMilliseconds {
		return nil, ErrInvalidOutboxRequest
	}
	expires := request.NowMilliseconds + request.LeaseMilliseconds
	if expires > math.MaxInt64 {
		return nil, ErrInvalidOutboxRequest
	}
	transaction, err := repository.database.BeginImmediate(ctx)
	if err != nil {
		return nil, err
	}
	defer func() { _ = transaction.Rollback() }()

	rows, err := transaction.QueryContext(
		ctx,
		`SELECT event_id
 FROM event_publication_outbox
 WHERE publication_state IN ('OBJECT_STORED','FAILED_RETRYABLE')
   AND (next_attempt_at_ms IS NULL OR next_attempt_at_ms <= ?)
   AND (lease_expires_at_ms IS NULL OR lease_expires_at_ms <= ?)
 ORDER BY created_at_ms, event_id
 LIMIT ?`,
		request.NowMilliseconds,
		request.NowMilliseconds,
		request.Limit,
	)
	if err != nil {
		return nil, err
	}
	var candidates []protocol.EventID
	for rows.Next() {
		var raw []byte
		if err := rows.Scan(&raw); err != nil {
			_ = rows.Close()
			return nil, err
		}
		eventID, err := protocol.EventIDFromBytes(raw)
		if err != nil {
			_ = rows.Close()
			return nil, ErrMigrationIntegrity
		}
		candidates = append(candidates, eventID)
	}
	if err := rows.Close(); err != nil {
		return nil, err
	}

	jobs := make([]OutboxJob, 0, len(candidates))
	for _, eventID := range candidates {
		token, err := randomOutboxLeaseToken(rand.Reader)
		if err != nil {
			return nil, err
		}
		result, err := transaction.ExecContext(
			ctx,
			`UPDATE event_publication_outbox
 SET lease_token = ?, lease_expires_at_ms = ?, updated_at_ms = ?
 WHERE event_id = ?
   AND publication_state IN ('OBJECT_STORED','FAILED_RETRYABLE')
   AND (next_attempt_at_ms IS NULL OR next_attempt_at_ms <= ?)
   AND (lease_expires_at_ms IS NULL OR lease_expires_at_ms <= ?)`,
			token[:], expires, request.NowMilliseconds, eventID[:],
			request.NowMilliseconds, request.NowMilliseconds,
		)
		if err != nil {
			return nil, err
		}
		affected, err := result.RowsAffected()
		if err != nil {
			return nil, err
		}
		if affected != 1 {
			continue
		}
		job, err := loadOutboxJob(ctx, transaction, eventID, token, expires)
		if err != nil {
			return nil, err
		}
		jobs = append(jobs, job)
	}
	if err := transaction.Commit(); err != nil {
		return nil, err
	}
	return jobs, nil
}

// MarkOutboxRetry records a bounded error code and backoff time and releases
// the exact lease. The retry counter is incremented in the same write.
func (repository *OperationRepository) MarkOutboxRetry(
	ctx context.Context,
	request MarkOutboxRetryRequest,
) error {
	if repository == nil || repository.database == nil || ctx == nil ||
		bytesAllZero(request.EventID[:]) || bytesAllZero(request.LeaseToken[:]) ||
		request.NowMilliseconds > math.MaxInt64 ||
		request.NextAttemptAtMS <= request.NowMilliseconds ||
		request.NextAttemptAtMS > math.MaxInt64 ||
		strings.TrimSpace(request.ErrorCode) == "" || len(request.ErrorCode) > 128 {
		return ErrInvalidOutboxRequest
	}
	result, err := repository.database.db.ExecContext(
		ctx,
		`UPDATE event_publication_outbox
 SET publication_state = 'FAILED_RETRYABLE',
     retry_count = retry_count + 1,
     next_attempt_at_ms = ?,
     lease_token = NULL,
     lease_expires_at_ms = NULL,
     last_error_code = ?,
     updated_at_ms = ?
 WHERE event_id = ? AND lease_token = ?
   AND lease_expires_at_ms >= ?
   AND publication_state IN ('OBJECT_STORED','FAILED_RETRYABLE')`,
		request.NextAttemptAtMS, request.ErrorCode, request.NowMilliseconds,
		request.EventID[:], request.LeaseToken[:], request.NowMilliseconds,
	)
	if err != nil {
		return err
	}
	return requireOutboxLease(result)
}

// MarkLogIncluded completes a leased publication. Replaying the same
// inclusion coordinates is idempotent; conflicting coordinates fail closed.
func (repository *OperationRepository) MarkLogIncluded(
	ctx context.Context,
	request MarkLogIncludedRequest,
) error {
	if repository == nil || repository.database == nil || ctx == nil ||
		bytesAllZero(request.EventID[:]) || bytesAllZero(request.LeaseToken[:]) ||
		bytesAllZero(request.LogID[:]) || request.NowMilliseconds > math.MaxInt64 ||
		request.IncludedTreeSize == 0 || request.IncludedTreeSize > math.MaxInt64 ||
		request.LeafIndex >= request.IncludedTreeSize {
		return ErrInvalidOutboxRequest
	}
	result, err := repository.database.db.ExecContext(
		ctx,
		`UPDATE event_publication_outbox
 SET publication_state = 'LOG_INCLUDED',
     next_attempt_at_ms = NULL,
     log_id = ?,
     leaf_index = ?,
     included_tree_size = ?,
     lease_token = NULL,
     lease_expires_at_ms = NULL,
     last_error_code = NULL,
     updated_at_ms = ?
 WHERE event_id = ? AND lease_token = ?
   AND lease_expires_at_ms >= ?
   AND publication_state IN ('OBJECT_STORED','FAILED_RETRYABLE')`,
		request.LogID[:], request.LeafIndex, request.IncludedTreeSize,
		request.NowMilliseconds, request.EventID[:], request.LeaseToken[:],
		request.NowMilliseconds,
	)
	if err != nil {
		return err
	}
	affected, err := result.RowsAffected()
	if err != nil {
		return err
	}
	if affected == 1 {
		return nil
	}
	var state string
	var logID []byte
	var leafIndex, treeSize sql.NullInt64
	err = repository.database.db.QueryRowContext(
		ctx,
		`SELECT publication_state, log_id, leaf_index, included_tree_size
 FROM event_publication_outbox WHERE event_id = ?`,
		request.EventID[:],
	).Scan(&state, &logID, &leafIndex, &treeSize)
	if errors.Is(err, sql.ErrNoRows) {
		return ErrOutboxLeaseLost
	}
	if err != nil {
		return err
	}
	if state == "LOG_INCLUDED" && bytesEqual(logID, request.LogID[:]) &&
		leafIndex.Valid && uint64(leafIndex.Int64) == request.LeafIndex &&
		treeSize.Valid && uint64(treeSize.Int64) == request.IncludedTreeSize {
		return nil
	}
	if state == "LOG_INCLUDED" {
		return ErrOutboxStateConflict
	}
	return ErrOutboxLeaseLost
}

func loadOutboxJob(
	ctx context.Context,
	transaction *Transaction,
	eventID protocol.EventID,
	token OutboxLeaseToken,
	expires uint64,
) (OutboxJob, error) {
	var eventCBOR, signature, eventDigest, objectDigest []byte
	var objectSize, retryCount int64
	err := transaction.QueryRowContext(
		ctx,
		`SELECT e.event_cbor, e.device_signature, e.event_digest,
        c.object_hash, c.ciphertext_length, o.retry_count
 FROM event_publication_outbox o
 JOIN operation_events e ON e.event_id = o.event_id
 JOIN content_objects c ON c.object_hash = o.object_hash
 WHERE o.event_id = ? AND o.lease_token = ? AND o.lease_expires_at_ms = ?`,
		eventID[:], token[:], expires,
	).Scan(&eventCBOR, &signature, &eventDigest, &objectDigest, &objectSize, &retryCount)
	if err != nil {
		return OutboxJob{}, err
	}
	if len(signature) != len(protocol.Signature{}) ||
		len(eventDigest) != sha256.Size || len(objectDigest) != sha256.Size ||
		objectSize <= 0 || retryCount < 0 {
		return OutboxJob{}, ErrMigrationIntegrity
	}
	var typedSignature protocol.Signature
	var typedEventDigest, typedObjectDigest [sha256.Size]byte
	copy(typedSignature[:], signature)
	copy(typedEventDigest[:], eventDigest)
	copy(typedObjectDigest[:], objectDigest)
	if signedDigest(eventCBOR, typedSignature) != typedEventDigest {
		return OutboxJob{}, ErrMigrationIntegrity
	}
	return OutboxJob{
		EventID: eventID, SigInputCBOR: append([]byte(nil), eventCBOR...),
		DeviceSignature: typedSignature, EventDigest: typedEventDigest,
		ObjectReference: platform.ObjectRef{
			Digest: typedObjectDigest,
			Size:   uint64(objectSize),
		},
		RetryCount: uint64(retryCount), LeaseToken: token,
		LeaseExpiresAtMS: expires,
	}, nil
}

func randomOutboxLeaseToken(reader io.Reader) (OutboxLeaseToken, error) {
	var token OutboxLeaseToken
	if reader == nil {
		return token, ErrInvalidOutboxRequest
	}
	if _, err := io.ReadFull(reader, token[:]); err != nil {
		clear(token[:])
		return token, errors.Join(ErrInvalidOutboxRequest, err)
	}
	if bytesAllZero(token[:]) {
		return token, ErrInvalidOutboxRequest
	}
	return token, nil
}

func requireOutboxLease(result sql.Result) error {
	affected, err := result.RowsAffected()
	if err != nil {
		return err
	}
	if affected != 1 {
		return ErrOutboxLeaseLost
	}
	return nil
}

func bytesEqual(left, right []byte) bool {
	if len(left) != len(right) {
		return false
	}
	var difference byte
	for index := range left {
		difference |= left[index] ^ right[index]
	}
	return difference == 0
}
