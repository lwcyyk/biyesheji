package sqlite

import (
	"bytes"
	"context"
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"errors"
	"fmt"
	"math"
	"strings"

	operation "vdns.local/vdns/internal/operation/domain"
	"vdns.local/vdns/internal/platform"
	"vdns.local/vdns/internal/protocol"
)

var (
	ErrInvalidEventCommit    = errors.New("invalid event commit request")
	ErrEventIDConflict       = errors.New("event ID already belongs to another operation")
	ErrPreviousEventMismatch = errors.New("previous event digest mismatch")
	ErrObjectRecordConflict  = errors.New("content object metadata conflict")
)

// CounterConflictError reports the durable device counter without mutating it.
type CounterConflictError struct {
	Current   uint64
	Attempted uint64
}

func (err *CounterConflictError) Error() string {
	return fmt.Sprintf("device counter conflict: current=%d attempted=%d", err.Current, err.Attempted)
}

// Is lets callers classify every counter conflict without parsing text.
func (err *CounterConflictError) Is(target error) bool {
	_, ok := target.(*CounterConflictError)
	return ok
}

// EventObject describes bytes already committed to the filesystem object
// store. The database transaction must never precede that durable write.
type EventObject struct {
	Reference           platform.ObjectRef
	StorageRelativePath string
	KeyGeneration       uint64
}

// CommitEventRequest atomically joins one immutable event to its durable
// ciphertext object, advances the device counter, and creates its outbox row.
type CommitEventRequest struct {
	Event                 *operation.SignedEvent
	Object                EventObject
	CreatedAtMilliseconds uint64
}

// PersistedEvent contains only immutable retry material. A retry worker must
// use these returned bytes and object address, never a newly sealed candidate.
type PersistedEvent struct {
	EventID          protocol.EventID
	SigInputCBOR     []byte
	DeviceSignature  protocol.Signature
	EventDigest      [sha256.Size]byte
	ObjectReference  platform.ObjectRef
	PublicationState string
	Created          bool
}

// OperationRepository persists signed event facts and their publication work.
type OperationRepository struct {
	database *Database
}

func NewOperationRepository(database *Database) (*OperationRepository, error) {
	if database == nil || database.db == nil {
		return nil, ErrInvalidEventCommit
	}
	return &OperationRepository{database: database}, nil
}

// CommitEvent owns a short BEGIN IMMEDIATE transaction.
func (repository *OperationRepository) CommitEvent(
	ctx context.Context,
	request CommitEventRequest,
) (PersistedEvent, error) {
	if repository == nil || repository.database == nil {
		return PersistedEvent{}, ErrInvalidEventCommit
	}
	transaction, err := repository.database.BeginImmediate(ctx)
	if err != nil {
		return PersistedEvent{}, err
	}
	defer func() { _ = transaction.Rollback() }()

	result, err := repository.CreateOrLoad(ctx, transaction, request)
	if err != nil {
		return PersistedEvent{}, err
	}
	if err := transaction.Commit(); err != nil {
		return PersistedEvent{}, err
	}
	return result, nil
}

// CreateOrLoad joins an application-owned transaction. EventID is first-write
// wins: a logical retry returns the exact original CBOR/signature/object, while
// a different operation reusing that ID is rejected.
func (repository *OperationRepository) CreateOrLoad(
	ctx context.Context,
	transaction *Transaction,
	request CommitEventRequest,
) (PersistedEvent, error) {
	if repository == nil || transaction == nil || ctx == nil {
		return PersistedEvent{}, ErrInvalidEventCommit
	}
	payload, operationName, err := validateEventCommit(request)
	if err != nil {
		return PersistedEvent{}, err
	}

	existing, existingProjection, found, err := loadPersistedEvent(ctx, transaction, payload.EventID)
	if err != nil {
		return PersistedEvent{}, err
	}
	if found {
		if !sameLogicalProjection(payload, operationName, existingProjection) {
			return PersistedEvent{}, ErrEventIDConflict
		}
		return existing, nil
	}

	if err := registerEventObject(ctx, transaction, request); err != nil {
		return PersistedEvent{}, err
	}
	currentCounter, err := currentDeviceCounter(ctx, transaction, payload.NamespaceID, payload.DeviceID)
	if err != nil {
		return PersistedEvent{}, err
	}
	if payload.DeviceCounter != currentCounter+1 {
		return PersistedEvent{}, &CounterConflictError{Current: currentCounter, Attempted: payload.DeviceCounter}
	}
	if err := verifyPreviousEvent(ctx, transaction, payload, currentCounter); err != nil {
		return PersistedEvent{}, err
	}

	createdAt := int64(request.CreatedAtMilliseconds)
	result, err := transaction.ExecContext(
		ctx,
		`UPDATE devices
SET last_accepted_counter = ?,
    updated_at_ms = CASE WHEN updated_at_ms > ? THEN updated_at_ms ELSE ? END
WHERE namespace_id = ? AND device_id = ? AND last_accepted_counter = ?`,
		payload.DeviceCounter,
		createdAt,
		createdAt,
		payload.NamespaceID[:],
		payload.DeviceID[:],
		currentCounter,
	)
	if err != nil {
		return PersistedEvent{}, err
	}
	affected, err := result.RowsAffected()
	if err != nil {
		return PersistedEvent{}, err
	}
	if affected != 1 {
		latest, queryErr := currentDeviceCounter(ctx, transaction, payload.NamespaceID, payload.DeviceID)
		if queryErr != nil {
			return PersistedEvent{}, queryErr
		}
		return PersistedEvent{}, &CounterConflictError{Current: latest, Attempted: payload.DeviceCounter}
	}

	if err := insertOperationEvent(ctx, transaction, request, payload, operationName); err != nil {
		return PersistedEvent{}, err
	}
	if _, err := transaction.ExecContext(
		ctx,
		`INSERT INTO event_publication_outbox (
  event_id, object_hash, publication_state, retry_count,
  created_at_ms, updated_at_ms
) VALUES (?, ?, 'OBJECT_STORED', 0, ?, ?)`,
		payload.EventID[:],
		request.Object.Reference.Digest[:],
		createdAt,
		createdAt,
	); err != nil {
		return PersistedEvent{}, err
	}

	return PersistedEvent{
		EventID:          payload.EventID,
		SigInputCBOR:     request.Event.SigInputCBOR(),
		DeviceSignature:  request.Event.Signature(),
		EventDigest:      request.Event.Digest(),
		ObjectReference:  request.Object.Reference,
		PublicationState: "OBJECT_STORED",
		Created:          true,
	}, nil
}

func validateEventCommit(request CommitEventRequest) (operation.Payload, string, error) {
	if request.Event == nil || request.CreatedAtMilliseconds > math.MaxInt64 ||
		request.Object.Reference.Size == 0 || request.Object.Reference.Size > math.MaxInt64 ||
		request.Object.KeyGeneration == 0 || request.Object.StorageRelativePath == "" {
		return operation.Payload{}, "", ErrInvalidEventCommit
	}
	payload := request.Event.Payload()
	if err := payload.Validate(); err != nil || request.Object.KeyGeneration != payload.SecretGeneration {
		return operation.Payload{}, "", ErrInvalidEventCommit
	}
	operationName, err := payload.OperationType.DatabaseName()
	if err != nil {
		return operation.Payload{}, "", ErrInvalidEventCommit
	}
	wantPath := eventObjectRelativePath(request.Object.Reference.Digest)
	if request.Object.StorageRelativePath != wantPath || strings.Contains(request.Object.StorageRelativePath, "..") ||
		strings.HasPrefix(request.Object.StorageRelativePath, "/") {
		return operation.Payload{}, "", ErrInvalidEventCommit
	}
	return payload, operationName, nil
}

func eventObjectRelativePath(digest [sha256.Size]byte) string {
	encoded := hex.EncodeToString(digest[:])
	return "objects/sha256/" + encoded[:2] + "/" + encoded[2:4] + "/" + encoded + ".obj"
}

func registerEventObject(ctx context.Context, transaction *Transaction, request CommitEventRequest) error {
	createdAt := int64(request.CreatedAtMilliseconds)
	if _, err := transaction.ExecContext(
		ctx,
		`INSERT INTO content_objects (
  object_hash, object_type, cipher_suite, key_generation,
  nonce, aad_hash, ciphertext_length, storage_relpath,
  state, created_at_ms, verified_at_ms
) VALUES (?, 'AUDIT_EVENT', ?, ?, NULL, NULL, ?, ?, 'COMMITTED', ?, ?)
ON CONFLICT(object_hash) DO NOTHING`,
		request.Object.Reference.Digest[:],
		protocol.SuiteID,
		request.Object.KeyGeneration,
		request.Object.Reference.Size,
		request.Object.StorageRelativePath,
		createdAt,
		createdAt,
	); err != nil {
		return err
	}

	var objectType, suite, path, state string
	var keyGeneration, size int64
	err := transaction.QueryRowContext(
		ctx,
		`SELECT object_type, cipher_suite, key_generation, ciphertext_length,
        storage_relpath, state
 FROM content_objects WHERE object_hash = ?`,
		request.Object.Reference.Digest[:],
	).Scan(&objectType, &suite, &keyGeneration, &size, &path, &state)
	if err != nil {
		return err
	}
	if objectType != "AUDIT_EVENT" || suite != protocol.SuiteID || keyGeneration != int64(request.Object.KeyGeneration) ||
		size != int64(request.Object.Reference.Size) || path != request.Object.StorageRelativePath || state != "COMMITTED" {
		return ErrObjectRecordConflict
	}
	return nil
}

func currentDeviceCounter(
	ctx context.Context,
	transaction *Transaction,
	namespaceID protocol.NamespaceID,
	deviceID protocol.DeviceID,
) (uint64, error) {
	var current int64
	err := transaction.QueryRowContext(
		ctx,
		"SELECT last_accepted_counter FROM devices WHERE namespace_id = ? AND device_id = ?",
		namespaceID[:],
		deviceID[:],
	).Scan(&current)
	if err != nil {
		return 0, err
	}
	return uint64(current), nil
}

func verifyPreviousEvent(
	ctx context.Context,
	transaction *Transaction,
	payload operation.Payload,
	currentCounter uint64,
) error {
	if currentCounter == 0 {
		if payload.PreviousEventHash != nil {
			return ErrPreviousEventMismatch
		}
		return nil
	}
	var previous []byte
	err := transaction.QueryRowContext(
		ctx,
		`SELECT event_digest FROM operation_events
 WHERE namespace_id = ? AND device_id = ? AND device_counter = ?`,
		payload.NamespaceID[:],
		payload.DeviceID[:],
		currentCounter,
	).Scan(&previous)
	if err != nil {
		return err
	}
	if payload.PreviousEventHash == nil || !bytes.Equal(previous, payload.PreviousEventHash[:]) {
		return ErrPreviousEventMismatch
	}
	return nil
}

func insertOperationEvent(
	ctx context.Context,
	transaction *Transaction,
	request CommitEventRequest,
	payload operation.Payload,
	operationName string,
) error {
	eventDigest := request.Event.Digest()
	deviceSignature := request.Event.Signature()
	_, err := transaction.ExecContext(
		ctx,
		`INSERT INTO operation_events (
  event_id, namespace_id, device_id, device_credential_hash, credential_id,
  operation_type, old_version, new_version, device_pseudonym, origin_commitment,
  event_payload_hash, vrf_epoch, secret_generation, device_counter,
  previous_event_hash, event_cbor, event_digest, device_signature,
  observed_at_ms, created_at_ms
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
		payload.EventID[:],
		payload.NamespaceID[:],
		payload.DeviceID[:],
		payload.DeviceCredentialHash[:],
		credentialIDValue(payload.CredentialID),
		operationName,
		optionalUint64(payload.OldVersion),
		optionalUint64(payload.NewVersion),
		payload.DevicePseudonym[:],
		optionalHash(payload.OriginCommitment),
		payload.EventPayloadHash[:],
		optionalUint64(payload.VRFEpoch),
		payload.SecretGeneration,
		payload.DeviceCounter,
		optionalHash(payload.PreviousEventHash),
		request.Event.SigInputCBOR(),
		eventDigest[:],
		deviceSignature[:],
		optionalUint64(payload.ObservedAtMilliseconds),
		request.CreatedAtMilliseconds,
	)
	return err
}

type storedProjection struct {
	namespaceID          []byte
	deviceID             []byte
	deviceCredentialHash []byte
	credentialID         []byte
	operationName        string
	oldVersion           sql.NullInt64
	newVersion           sql.NullInt64
	devicePseudonym      []byte
	originCommitment     []byte
	vrfEpoch             sql.NullInt64
	secretGeneration     int64
	deviceCounter        int64
	previousEventHash    []byte
	observedAt           sql.NullInt64
}

func loadPersistedEvent(
	ctx context.Context,
	transaction *Transaction,
	eventID protocol.EventID,
) (PersistedEvent, storedProjection, bool, error) {
	var projection storedProjection
	var eventCBOR, signature, digest, objectHash []byte
	var objectSize int64
	var publicationState string
	err := transaction.QueryRowContext(
		ctx,
		`SELECT e.namespace_id, e.device_id, e.device_credential_hash, e.credential_id,
        e.operation_type, e.old_version, e.new_version, e.device_pseudonym,
        e.origin_commitment, e.vrf_epoch, e.secret_generation, e.device_counter,
        e.previous_event_hash, e.observed_at_ms, e.event_cbor, e.device_signature,
        e.event_digest, o.object_hash, c.ciphertext_length, o.publication_state
 FROM operation_events e
 JOIN event_publication_outbox o ON o.event_id = e.event_id
 JOIN content_objects c ON c.object_hash = o.object_hash
 WHERE e.event_id = ?`,
		eventID[:],
	).Scan(
		&projection.namespaceID,
		&projection.deviceID,
		&projection.deviceCredentialHash,
		&projection.credentialID,
		&projection.operationName,
		&projection.oldVersion,
		&projection.newVersion,
		&projection.devicePseudonym,
		&projection.originCommitment,
		&projection.vrfEpoch,
		&projection.secretGeneration,
		&projection.deviceCounter,
		&projection.previousEventHash,
		&projection.observedAt,
		&eventCBOR,
		&signature,
		&digest,
		&objectHash,
		&objectSize,
		&publicationState,
	)
	if errors.Is(err, sql.ErrNoRows) {
		return PersistedEvent{}, storedProjection{}, false, nil
	}
	if err != nil {
		return PersistedEvent{}, storedProjection{}, false, err
	}
	if len(signature) != len(protocol.Signature{}) || len(digest) != sha256.Size || len(objectHash) != sha256.Size || objectSize <= 0 {
		return PersistedEvent{}, storedProjection{}, false, ErrMigrationIntegrity
	}
	var storedSignature protocol.Signature
	copy(storedSignature[:], signature)
	var storedDigest, storedObjectHash [sha256.Size]byte
	copy(storedDigest[:], digest)
	copy(storedObjectHash[:], objectHash)
	return PersistedEvent{
		EventID:          eventID,
		SigInputCBOR:     append([]byte(nil), eventCBOR...),
		DeviceSignature:  storedSignature,
		EventDigest:      storedDigest,
		ObjectReference:  platform.ObjectRef{Digest: storedObjectHash, Size: uint64(objectSize)},
		PublicationState: publicationState,
		Created:          false,
	}, projection, true, nil
}

func sameLogicalProjection(payload operation.Payload, operationName string, stored storedProjection) bool {
	return bytes.Equal(payload.NamespaceID[:], stored.namespaceID) &&
		bytes.Equal(payload.DeviceID[:], stored.deviceID) &&
		bytes.Equal(payload.DeviceCredentialHash[:], stored.deviceCredentialHash) &&
		bytes.Equal(credentialIDValue(payload.CredentialID), stored.credentialID) &&
		operationName == stored.operationName &&
		equalOptionalUint64(payload.OldVersion, stored.oldVersion) &&
		equalOptionalUint64(payload.NewVersion, stored.newVersion) &&
		bytes.Equal(payload.DevicePseudonym[:], stored.devicePseudonym) &&
		bytes.Equal(optionalHash(payload.OriginCommitment), stored.originCommitment) &&
		equalOptionalUint64(payload.VRFEpoch, stored.vrfEpoch) &&
		payload.SecretGeneration == uint64(stored.secretGeneration) &&
		payload.DeviceCounter == uint64(stored.deviceCounter) &&
		bytes.Equal(optionalHash(payload.PreviousEventHash), stored.previousEventHash) &&
		equalOptionalUint64(payload.ObservedAtMilliseconds, stored.observedAt)
}

func optionalUint64(value *uint64) any {
	if value == nil {
		return nil
	}
	return *value
}

func optionalHash(value *[sha256.Size]byte) []byte {
	if value == nil {
		return nil
	}
	return value[:]
}

func credentialIDValue(value *protocol.CredentialID) []byte {
	if value == nil {
		return nil
	}
	return value[:]
}

func equalOptionalUint64(value *uint64, stored sql.NullInt64) bool {
	if value == nil {
		return !stored.Valid
	}
	return stored.Valid && *value == uint64(stored.Int64)
}
