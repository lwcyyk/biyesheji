package sqlite

import (
	"context"
	"crypto/sha256"
	"database/sql"
	"errors"
	"math"
	"strings"

	"github.com/google/uuid"

	localports "vpass.local/vpass/internal/localapi/ports"
)

func (repository *LocalAPIRepository) PutOperation(
	ctx context.Context,
	record localports.LocalOperation,
) error {
	if repository == nil || repository.database == nil || ctx == nil ||
		uuid.Validate(record.OperationID) != nil ||
		strings.TrimSpace(record.OperationKind) == "" ||
		len(record.OperationKind) > 64 || bytesAllZero(record.RequestHash[:]) ||
		!validLocalOperationState(record.State) ||
		len(record.ResultReference) > 512 || len(record.ErrorCode) > 64 ||
		(record.State == "FAILED") != (record.ErrorCode != "") ||
		record.CreatedAtMS > math.MaxInt64 || record.UpdatedAtMS > math.MaxInt64 ||
		record.UpdatedAtMS < record.CreatedAtMS ||
		(len(record.NamespaceID) != 0 && len(record.NamespaceID) != 16) ||
		(len(record.DeviceID) != 0 && len(record.DeviceID) != 16) {
		return ErrInvalidLocalAPIRecord
	}
	id, _ := uuid.Parse(record.OperationID)
	var namespace, device any
	if len(record.NamespaceID) == 16 {
		namespace = record.NamespaceID
	}
	if len(record.DeviceID) == 16 {
		device = record.DeviceID
	}
	var resultReference, errorCode any
	if record.ResultReference != "" {
		resultReference = record.ResultReference
	}
	if record.ErrorCode != "" {
		errorCode = record.ErrorCode
	}
	_, err := repository.database.ExecContext(
		ctx,
		`INSERT INTO local_api_operations_v2 (
		   operation_id, operation_kind, namespace_id, device_id, request_hash,
		   state, result_reference, error_code, created_at_ms, updated_at_ms
		 ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
		 ON CONFLICT(operation_id) DO UPDATE SET
		   state = excluded.state,
		   result_reference = excluded.result_reference,
		   error_code = excluded.error_code,
		   updated_at_ms = excluded.updated_at_ms
		 WHERE local_api_operations_v2.operation_kind = excluded.operation_kind
		   AND local_api_operations_v2.request_hash = excluded.request_hash
		   AND local_api_operations_v2.updated_at_ms <= excluded.updated_at_ms`,
		id[:], record.OperationKind, namespace, device, record.RequestHash[:],
		record.State, resultReference, errorCode,
		int64(record.CreatedAtMS), int64(record.UpdatedAtMS),
	)
	return err
}

func (repository *LocalAPIRepository) LoadOperation(
	ctx context.Context,
	operationID string,
) (localports.LocalOperation, bool, error) {
	if repository == nil || repository.database == nil || ctx == nil ||
		uuid.Validate(operationID) != nil {
		return localports.LocalOperation{}, false, ErrInvalidLocalAPIRecord
	}
	id, _ := uuid.Parse(operationID)
	var (
		kind, state          string
		namespace, device    []byte
		requestHash          []byte
		resultRef, errorCode sql.NullString
		createdAt, updatedAt int64
	)
	err := repository.database.QueryRowContext(
		ctx,
		`SELECT operation_kind, namespace_id, device_id, request_hash,
		        state, result_reference, error_code, created_at_ms, updated_at_ms
		   FROM local_api_operations_v2 WHERE operation_id = ?`,
		id[:],
	).Scan(
		&kind, &namespace, &device, &requestHash, &state,
		&resultRef, &errorCode, &createdAt, &updatedAt,
	)
	if errors.Is(err, sql.ErrNoRows) {
		return localports.LocalOperation{}, false, nil
	}
	if err != nil {
		return localports.LocalOperation{}, false, err
	}
	if len(requestHash) != sha256.Size || !validLocalOperationState(state) ||
		createdAt < 0 || updatedAt < createdAt ||
		(len(namespace) != 0 && len(namespace) != 16) ||
		(len(device) != 0 && len(device) != 16) ||
		(state == "FAILED") != errorCode.Valid {
		return localports.LocalOperation{}, false, ErrInvalidLocalAPIRecord
	}
	var digest [sha256.Size]byte
	copy(digest[:], requestHash)
	return localports.LocalOperation{
		OperationID: operationID, OperationKind: kind,
		NamespaceID: append([]byte(nil), namespace...),
		DeviceID:    append([]byte(nil), device...), RequestHash: digest,
		State: state, ResultReference: resultRef.String, ErrorCode: errorCode.String,
		CreatedAtMS: uint64(createdAt), UpdatedAtMS: uint64(updatedAt),
	}, true, nil
}

func validLocalOperationState(value string) bool {
	switch value {
	case "QUEUED", "RUNNING", "COMPLETED", "PENDING", "FAILED", "UNKNOWN":
		return true
	default:
		return false
	}
}
