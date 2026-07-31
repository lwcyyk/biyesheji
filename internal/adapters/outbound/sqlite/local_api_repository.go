package sqlite

import (
	"context"
	"crypto/sha256"
	"database/sql"
	"encoding/json"
	"errors"
	"math"
	"strings"

	localports "vdns.local/vdns/internal/localapi/ports"
)

var (
	ErrInvalidLocalAPIRecord = errors.New("invalid local API persistence record")
	ErrLocalAPIConflict      = errors.New("local API idempotency conflict")
)

type LocalAPIRepository struct {
	database *Database
}

func NewLocalAPIRepository(database *Database) (*LocalAPIRepository, error) {
	if database == nil || database.db == nil {
		return nil, ErrInvalidLocalAPIRecord
	}
	return &LocalAPIRepository{database: database}, nil
}

func (repository *LocalAPIRepository) Load(
	ctx context.Context,
	keyHash [sha256.Size]byte,
	nowMS uint64,
) (localports.IdempotencyResponse, bool, error) {
	if repository == nil || repository.database == nil || ctx == nil ||
		bytesAllZero(keyHash[:]) || nowMS > math.MaxInt64 {
		return localports.IdempotencyResponse{}, false, ErrInvalidLocalAPIRecord
	}
	var (
		scope, headersJSON string
		requestHash, body  []byte
		status             int
		createdAt, expires int64
	)
	err := repository.database.QueryRowContext(
		ctx,
		`SELECT operation_scope, request_hash, response_status,
		        response_headers_json, response_body, created_at_ms, expires_at_ms
		   FROM local_api_idempotency_v2
		  WHERE key_hash = ? AND expires_at_ms > ?`,
		keyHash[:], int64(nowMS),
	).Scan(&scope, &requestHash, &status, &headersJSON, &body, &createdAt, &expires)
	if errors.Is(err, sql.ErrNoRows) {
		return localports.IdempotencyResponse{}, false, nil
	}
	if err != nil {
		return localports.IdempotencyResponse{}, false, err
	}
	var headers map[string][]string
	if len(requestHash) != sha256.Size || status < 200 || status > 299 ||
		createdAt < 0 || expires <= createdAt ||
		json.Unmarshal([]byte(headersJSON), &headers) != nil ||
		!safePersistedHeaders(headers) {
		clear(body)
		return localports.IdempotencyResponse{}, false, ErrInvalidLocalAPIRecord
	}
	var requestDigest [sha256.Size]byte
	copy(requestDigest[:], requestHash)
	return localports.IdempotencyResponse{
		KeyHash: keyHash, OperationScope: scope, RequestHash: requestDigest,
		Status: status, Headers: headers, Body: body,
		CreatedAtMS: uint64(createdAt), ExpiresAtMS: uint64(expires),
	}, true, nil
}

func (repository *LocalAPIRepository) Put(
	ctx context.Context,
	record localports.IdempotencyResponse,
) error {
	if repository == nil || repository.database == nil || ctx == nil ||
		bytesAllZero(record.KeyHash[:]) || bytesAllZero(record.RequestHash[:]) ||
		strings.TrimSpace(record.OperationScope) == "" ||
		len(record.OperationScope) > 512 || record.Status < 200 || record.Status > 299 ||
		len(record.Body) > 1024*1024 || record.CreatedAtMS > math.MaxInt64 ||
		record.ExpiresAtMS > math.MaxInt64 || record.ExpiresAtMS <= record.CreatedAtMS ||
		!safePersistedHeaders(record.Headers) {
		return ErrInvalidLocalAPIRecord
	}
	headers, err := json.Marshal(record.Headers)
	if err != nil || len(headers) < 2 || len(headers) > 16384 {
		return ErrInvalidLocalAPIRecord
	}
	result, err := repository.database.ExecContext(
		ctx,
		`INSERT INTO local_api_idempotency_v2 (
		   key_hash, operation_scope, request_hash, response_status,
		   response_headers_json, response_body, created_at_ms, expires_at_ms
		 ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
		 ON CONFLICT(key_hash) DO NOTHING`,
		record.KeyHash[:], record.OperationScope, record.RequestHash[:],
		record.Status, headers, record.Body,
		int64(record.CreatedAtMS), int64(record.ExpiresAtMS),
	)
	clear(headers)
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
	existing, found, err := repository.Load(ctx, record.KeyHash, record.CreatedAtMS)
	if err != nil {
		return err
	}
	if !found || existing.OperationScope != record.OperationScope ||
		existing.RequestHash != record.RequestHash {
		return ErrLocalAPIConflict
	}
	return nil
}

func (repository *LocalAPIRepository) PurgeExpired(ctx context.Context, nowMS uint64) error {
	if repository == nil || repository.database == nil || ctx == nil || nowMS > math.MaxInt64 {
		return ErrInvalidLocalAPIRecord
	}
	_, err := repository.database.ExecContext(
		ctx, "DELETE FROM local_api_idempotency_v2 WHERE expires_at_ms <= ?", int64(nowMS),
	)
	return err
}

func safePersistedHeaders(headers map[string][]string) bool {
	if len(headers) > 16 {
		return false
	}
	for name, values := range headers {
		canonical := strings.ToLower(name)
		switch canonical {
		case "content-type", "location":
		default:
			return false
		}
		if len(values) > 4 {
			return false
		}
		for _, value := range values {
			if value == "" || len(value) > 1024 || strings.ContainsAny(value, "\r\n") {
				return false
			}
		}
	}
	return true
}
