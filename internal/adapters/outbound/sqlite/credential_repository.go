package sqlite

import (
	"bytes"
	"context"
	"crypto/sha256"
	"database/sql"
	"errors"
	"fmt"
	"math"

	"vdns.local/vdns/internal/credential/domain"
	"vdns.local/vdns/internal/cryptokit"
	"vdns.local/vdns/internal/platform"
	"vdns.local/vdns/internal/protocol"
)

var ErrInvalidCredentialCommit = errors.New("invalid credential version commit request")

// CredentialCASConflictError returns the current local version so an API can
// emit a deterministic 409 response without another read.
type CredentialCASConflictError struct {
	CurrentLocalVersion *uint64
}

func (err *CredentialCASConflictError) Error() string {
	if err == nil || err.CurrentLocalVersion == nil {
		return "credential CAS conflict: no current local version"
	}
	return fmt.Sprintf("credential CAS conflict: current local version=%d", *err.CurrentLocalVersion)
}

func (err *CredentialCASConflictError) Is(target error) bool {
	_, ok := target.(*CredentialCASConflictError)
	return ok
}

// CommitCredentialVersionRequest references descriptor and field objects that
// have already been fsynced and atomically published by the object store.
type CommitCredentialVersionRequest struct {
	NamespaceID            protocol.NamespaceID
	OriginCommitment       [sha256.Size]byte
	ExpectedLocalVersion   *uint64
	Draft                  *domain.VersionDraft
	DescriptorObject       platform.ObjectRef
	DescriptorStoragePath  string
	FieldStoragePaths      map[cryptokit.FieldType]string
	AdvanceLocalPointer    bool
	AdvanceAcceptedPointer bool
	CreatedAtMilliseconds  uint64
}

type CommittedCredentialVersion struct {
	CredentialID           protocol.CredentialID
	Version                uint64
	DescriptorHash         [sha256.Size]byte
	CurrentLocalVersion    uint64
	CurrentAcceptedVersion *uint64
}

// LoadFieldMapping returns the exact immutable object address and reference
// accepted for one credential version.
func (repository *CredentialRepository) LoadFieldMapping(
	ctx context.Context,
	credentialID protocol.CredentialID,
	version uint64,
	fieldType cryptokit.FieldType,
) (domain.FieldMapping, error) {
	if repository == nil || repository.database == nil || ctx == nil ||
		bytesAllZero(credentialID[:]) || version == 0 || !fieldType.Valid() {
		return domain.FieldMapping{}, ErrInvalidCredentialCommit
	}
	var storedType, suite string
	var encryptionVersion, keyGeneration, objectSize uint64
	var objectID, fieldObjectHash, envelopeID, envelopeHash, storageHash,
		wrappedDEK, policyHash, originBinding, fieldDigest []byte
	err := repository.database.QueryRowContext(
		ctx,
		`SELECT f.field_type, f.encryption_version,
        f.field_object_id, f.field_object_hash,
        f.envelope_id, f.envelope_hash,
        f.object_hash, c.ciphertext_length,
        f.wrapped_dek, f.wrapped_dek_suite,
        f.crypto_policy_hash, f.origin_binding,
        f.field_digest, f.secret_generation
 FROM credential_version_fields f
 JOIN content_objects c ON c.object_hash = f.object_hash
 WHERE f.credential_id = ? AND f.version = ? AND f.field_type = ?`,
		credentialID[:], version, fieldType.String(),
	).Scan(
		&storedType, &encryptionVersion,
		&objectID, &fieldObjectHash, &envelopeID, &envelopeHash,
		&storageHash, &objectSize, &wrappedDEK, &suite,
		&policyHash, &originBinding, &fieldDigest, &keyGeneration,
	)
	if errors.Is(err, sql.ErrNoRows) {
		return domain.FieldMapping{}, ErrInvalidCredentialCommit
	}
	if err != nil {
		return domain.FieldMapping{}, err
	}
	parsedType, err := cryptokit.ParseFieldType(storedType)
	if err != nil || parsedType != fieldType ||
		len(objectID) != cryptokit.FieldObjectIDSize ||
		len(fieldObjectHash) != sha256.Size ||
		len(envelopeID) != cryptokit.FieldObjectIDSize ||
		len(envelopeHash) != sha256.Size || len(storageHash) != sha256.Size ||
		len(policyHash) != sha256.Size ||
		len(originBinding) != cryptokit.OriginBindingSize ||
		len(fieldDigest) != sha256.Size || objectSize == 0 {
		return domain.FieldMapping{}, ErrObjectRecordConflict
	}
	reference := cryptokit.FieldReference{
		FieldType: parsedType, EncryptionVersion: encryptionVersion,
		KeyGeneration: keyGeneration,
	}
	copy(reference.ObjectID[:], objectID)
	copy(reference.ObjectHash[:], fieldObjectHash)
	copy(reference.EnvelopeID[:], envelopeID)
	copy(reference.EnvelopeHash[:], envelopeHash)
	copy(reference.CryptoPolicyHash[:], policyHash)
	copy(reference.OriginBinding[:], originBinding)
	var storageDigest, typedFieldDigest [sha256.Size]byte
	copy(storageDigest[:], storageHash)
	copy(typedFieldDigest[:], fieldDigest)
	return domain.RestoreFieldMapping(
		reference,
		platform.ObjectRef{Digest: storageDigest, Size: objectSize},
		wrappedDEK, suite, typedFieldDigest,
	)
}

type CredentialRepository struct {
	database *Database
}

func NewCredentialRepository(database *Database) (*CredentialRepository, error) {
	if database == nil || database.db == nil {
		return nil, ErrInvalidCredentialCommit
	}
	return &CredentialRepository{database: database}, nil
}

// CommitVersion owns a short BEGIN IMMEDIATE transaction. Application flows
// that also create an operation event use CreateVersion with the same concrete
// transaction before committing once.
func (repository *CredentialRepository) CommitVersion(
	ctx context.Context,
	request CommitCredentialVersionRequest,
) (CommittedCredentialVersion, error) {
	if repository == nil || repository.database == nil {
		return CommittedCredentialVersion{}, ErrInvalidCredentialCommit
	}
	transaction, err := repository.database.BeginImmediate(ctx)
	if err != nil {
		return CommittedCredentialVersion{}, err
	}
	defer func() { _ = transaction.Rollback() }()
	result, err := repository.CreateVersion(ctx, transaction, request)
	if err != nil {
		return CommittedCredentialVersion{}, err
	}
	if err := transaction.Commit(); err != nil {
		return CommittedCredentialVersion{}, err
	}
	return result, nil
}

// CreateVersion validates expected_version and previous_descriptor_hash in the
// same transaction that inserts the immutable version and optionally advances
// local/accepted pointers.
func (repository *CredentialRepository) CreateVersion(
	ctx context.Context,
	transaction *Transaction,
	request CommitCredentialVersionRequest,
) (CommittedCredentialVersion, error) {
	if repository == nil || transaction == nil || ctx == nil {
		return CommittedCredentialVersion{}, ErrInvalidCredentialCommit
	}
	fields, statusName, err := validateCredentialCommit(request)
	if err != nil {
		return CommittedCredentialVersion{}, err
	}

	credentialID := request.Draft.CredentialID()
	state, found, err := loadCredentialCASState(ctx, transaction, credentialID)
	if err != nil {
		return CommittedCredentialVersion{}, err
	}
	if err := validateCredentialCAS(request, state, found); err != nil {
		return CommittedCredentialVersion{}, err
	}
	if found {
		var versionExists int
		if err := transaction.QueryRowContext(
			ctx,
			"SELECT count(*) FROM credential_versions WHERE credential_id = ? AND version = ?",
			credentialID[:],
			request.Draft.Version(),
		).Scan(&versionExists); err != nil {
			return CommittedCredentialVersion{}, err
		}
		if versionExists != 0 {
			return CommittedCredentialVersion{}, newCredentialCASConflict(state.currentLocal)
		}
	} else {
		aggregateStatus, _ := domain.AggregateActive.DatabaseName()
		if _, err := transaction.ExecContext(
			ctx,
			`INSERT INTO credentials (
  credential_id, namespace_id, aggregate_status, current_local_version,
  current_accepted_version, origin_commitment, created_at_ms, updated_at_ms
) VALUES (?, ?, ?, NULL, NULL, ?, ?, ?)`,
			credentialID[:],
			request.NamespaceID[:],
			aggregateStatus,
			request.OriginCommitment[:],
			request.CreatedAtMilliseconds,
			request.CreatedAtMilliseconds,
		); err != nil {
			return CommittedCredentialVersion{}, err
		}
	}

	if err := registerCredentialContentObjects(ctx, transaction, request, fields); err != nil {
		return CommittedCredentialVersion{}, err
	}
	descriptorHash := request.Draft.DescriptorHash()
	previousHash := request.Draft.PreviousDescriptorHash()
	policyHash := request.Draft.PolicyHash()
	if _, err := transaction.ExecContext(
		ctx,
		`INSERT INTO credential_versions (
  credential_id, version, password_version, status, descriptor_hash,
  descriptor_object_hash, previous_descriptor_hash, policy_hash,
  created_at_ms, updated_at_ms
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
		credentialID[:],
		request.Draft.Version(),
		request.Draft.PasswordVersion(),
		statusName,
		descriptorHash[:],
		request.DescriptorObject.Digest[:],
		optionalHash(previousHash),
		policyHash[:],
		request.CreatedAtMilliseconds,
		request.CreatedAtMilliseconds,
	); err != nil {
		return CommittedCredentialVersion{}, err
	}
	for _, field := range fields {
		if err := insertCredentialField(ctx, transaction, credentialID, request.Draft.Version(), field); err != nil {
			return CommittedCredentialVersion{}, err
		}
	}

	currentLocal := state.currentLocal
	currentAccepted := state.currentAccepted
	if request.AdvanceLocalPointer {
		if err := advanceCredentialPointers(ctx, transaction, request, found); err != nil {
			return CommittedCredentialVersion{}, err
		}
		newVersion := request.Draft.Version()
		currentLocal = &newVersion
		if request.AdvanceAcceptedPointer {
			currentAccepted = &newVersion
		}
	}
	if currentLocal == nil {
		return CommittedCredentialVersion{}, ErrInvalidCredentialCommit
	}
	return CommittedCredentialVersion{
		CredentialID:           credentialID,
		Version:                request.Draft.Version(),
		DescriptorHash:         descriptorHash,
		CurrentLocalVersion:    *currentLocal,
		CurrentAcceptedVersion: cloneUint64(currentAccepted),
	}, nil
}

type credentialCASState struct {
	namespaceID       []byte
	originCommitment  []byte
	currentLocal      *uint64
	currentAccepted   *uint64
	currentDescriptor []byte
}

func loadCredentialCASState(
	ctx context.Context,
	transaction *Transaction,
	credentialID protocol.CredentialID,
) (credentialCASState, bool, error) {
	var namespaceID, origin, descriptor []byte
	var local, accepted sql.NullInt64
	err := transaction.QueryRowContext(
		ctx,
		`SELECT c.namespace_id, c.origin_commitment, c.current_local_version,
        c.current_accepted_version, v.descriptor_hash
 FROM credentials c
 LEFT JOIN credential_versions v
   ON v.credential_id = c.credential_id AND v.version = c.current_local_version
 WHERE c.credential_id = ?`,
		credentialID[:],
	).Scan(&namespaceID, &origin, &local, &accepted, &descriptor)
	if errors.Is(err, sql.ErrNoRows) {
		return credentialCASState{}, false, nil
	}
	if err != nil {
		return credentialCASState{}, false, err
	}
	state := credentialCASState{
		namespaceID:       namespaceID,
		originCommitment:  origin,
		currentDescriptor: descriptor,
	}
	if local.Valid {
		value := uint64(local.Int64)
		state.currentLocal = &value
	}
	if accepted.Valid {
		value := uint64(accepted.Int64)
		state.currentAccepted = &value
	}
	return state, true, nil
}

func validateCredentialCAS(
	request CommitCredentialVersionRequest,
	state credentialCASState,
	found bool,
) error {
	if !found {
		if request.ExpectedLocalVersion != nil || request.Draft.Version() != 1 ||
			request.Draft.PreviousDescriptorHash() != nil || !request.AdvanceLocalPointer {
			return newCredentialCASConflict(nil)
		}
		return nil
	}
	if request.ExpectedLocalVersion == nil || state.currentLocal == nil ||
		*request.ExpectedLocalVersion != *state.currentLocal ||
		request.Draft.Version() != *state.currentLocal+1 ||
		!bytes.Equal(state.namespaceID, request.NamespaceID[:]) ||
		!bytes.Equal(state.originCommitment, request.OriginCommitment[:]) {
		return newCredentialCASConflict(state.currentLocal)
	}
	previous := request.Draft.PreviousDescriptorHash()
	if previous == nil || !bytes.Equal(previous[:], state.currentDescriptor) {
		return newCredentialCASConflict(state.currentLocal)
	}
	return nil
}

func validateCredentialCommit(
	request CommitCredentialVersionRequest,
) ([]domain.FieldMapping, string, error) {
	if request.Draft == nil || request.CreatedAtMilliseconds > math.MaxInt64 ||
		request.DescriptorObject.Size == 0 || request.DescriptorObject.Size > math.MaxInt64 ||
		request.DescriptorStoragePath != eventObjectRelativePath(request.DescriptorObject.Digest) ||
		request.DescriptorObject.Digest != request.Draft.DescriptorHash() ||
		request.DescriptorObject.Size != uint64(len(request.Draft.DescriptorCBOR())) ||
		request.AdvanceAcceptedPointer && !request.AdvanceLocalPointer {
		return nil, "", ErrInvalidCredentialCommit
	}
	if request.AdvanceAcceptedPointer && (request.Draft.Version() != 1 || request.Draft.Status() != domain.VersionActive) {
		return nil, "", ErrInvalidCredentialCommit
	}
	if request.AdvanceLocalPointer && request.Draft.Version() > 1 &&
		request.Draft.Status() != domain.VersionSiteChangedLocalCommitPending &&
		request.Draft.Status() != domain.VersionActiveLocalPendingProof {
		return nil, "", ErrInvalidCredentialCommit
	}
	statusName, err := request.Draft.Status().DatabaseName()
	if err != nil {
		return nil, "", ErrInvalidCredentialCommit
	}
	fields := request.Draft.Fields()
	if len(fields) != len(request.FieldStoragePaths) {
		return nil, "", ErrInvalidCredentialCommit
	}
	for _, field := range fields {
		fieldType := field.Reference().FieldType
		if request.FieldStoragePaths[fieldType] != eventObjectRelativePath(field.ObjectReference().Digest) {
			return nil, "", ErrInvalidCredentialCommit
		}
	}
	return fields, statusName, nil
}

func registerCredentialContentObjects(
	ctx context.Context,
	transaction *Transaction,
	request CommitCredentialVersionRequest,
	fields []domain.FieldMapping,
) error {
	if err := registerCredentialObject(
		ctx,
		transaction,
		request.DescriptorObject,
		request.DescriptorStoragePath,
		"CREDENTIAL_DESCRIPTOR",
		nil,
		request.CreatedAtMilliseconds,
	); err != nil {
		return err
	}
	for _, field := range fields {
		generation := field.Reference().KeyGeneration
		if err := registerCredentialObject(
			ctx,
			transaction,
			field.ObjectReference(),
			request.FieldStoragePaths[field.Reference().FieldType],
			"CREDENTIAL_FIELD",
			&generation,
			request.CreatedAtMilliseconds,
		); err != nil {
			return err
		}
	}
	return nil
}

func registerCredentialObject(
	ctx context.Context,
	transaction *Transaction,
	reference platform.ObjectRef,
	storagePath string,
	objectType string,
	keyGeneration *uint64,
	createdAt uint64,
) error {
	if _, err := transaction.ExecContext(
		ctx,
		`INSERT INTO content_objects (
  object_hash, object_type, cipher_suite, key_generation,
  ciphertext_length, storage_relpath, state, created_at_ms, verified_at_ms
) VALUES (?, ?, ?, ?, ?, ?, 'COMMITTED', ?, ?)
ON CONFLICT(object_hash) DO NOTHING`,
		reference.Digest[:],
		objectType,
		protocol.SuiteID,
		optionalUint64(keyGeneration),
		reference.Size,
		storagePath,
		createdAt,
		createdAt,
	); err != nil {
		return err
	}
	var storedType, suite, path, state string
	var storedGeneration sql.NullInt64
	var storedSize int64
	if err := transaction.QueryRowContext(
		ctx,
		`SELECT object_type, cipher_suite, key_generation, ciphertext_length,
        storage_relpath, state FROM content_objects WHERE object_hash = ?`,
		reference.Digest[:],
	).Scan(&storedType, &suite, &storedGeneration, &storedSize, &path, &state); err != nil {
		return err
	}
	if storedType != objectType || suite != protocol.SuiteID || storedSize != int64(reference.Size) ||
		path != storagePath || state != "COMMITTED" || !equalOptionalUint64(keyGeneration, storedGeneration) {
		return ErrObjectRecordConflict
	}
	return nil
}

func insertCredentialField(
	ctx context.Context,
	transaction *Transaction,
	credentialID protocol.CredentialID,
	version uint64,
	field domain.FieldMapping,
) error {
	reference := field.Reference()
	objectReference := field.ObjectReference()
	fieldDigest := field.FieldDigest()
	_, err := transaction.ExecContext(
		ctx,
		`INSERT INTO credential_version_fields (
  credential_id, version, field_type, encryption_version,
  field_object_id, field_object_hash, envelope_id, envelope_hash,
  object_hash, wrapped_dek, wrapped_dek_suite, crypto_policy_hash,
  origin_binding, field_digest, secret_generation
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
		credentialID[:],
		version,
		reference.FieldType.String(),
		reference.EncryptionVersion,
		reference.ObjectID[:],
		reference.ObjectHash[:],
		reference.EnvelopeID[:],
		reference.EnvelopeHash[:],
		objectReference.Digest[:],
		field.WrappedDEK(),
		field.WrappedDEKSuite(),
		reference.CryptoPolicyHash[:],
		reference.OriginBinding[:],
		fieldDigest[:],
		reference.KeyGeneration,
	)
	return err
}

func advanceCredentialPointers(
	ctx context.Context,
	transaction *Transaction,
	request CommitCredentialVersionRequest,
	found bool,
) error {
	credentialID := request.Draft.CredentialID()
	query := `UPDATE credentials
SET current_local_version = ?,
    current_accepted_version = CASE WHEN ? THEN ? ELSE current_accepted_version END,
    updated_at_ms = CASE WHEN updated_at_ms > ? THEN updated_at_ms ELSE ? END
WHERE credential_id = ? AND current_local_version IS NULL`
	args := []any{
		request.Draft.Version(), request.AdvanceAcceptedPointer, request.Draft.Version(),
		request.CreatedAtMilliseconds, request.CreatedAtMilliseconds, credentialID[:],
	}
	if found {
		query = `UPDATE credentials
SET current_local_version = ?,
    current_accepted_version = CASE WHEN ? THEN ? ELSE current_accepted_version END,
    updated_at_ms = CASE WHEN updated_at_ms > ? THEN updated_at_ms ELSE ? END
WHERE credential_id = ? AND current_local_version = ?`
		args = append(args, *request.ExpectedLocalVersion)
	}
	result, err := transaction.ExecContext(ctx, query, args...)
	if err != nil {
		return err
	}
	affected, err := result.RowsAffected()
	if err != nil {
		return err
	}
	if affected != 1 {
		return newCredentialCASConflict(request.ExpectedLocalVersion)
	}
	return nil
}

func newCredentialCASConflict(current *uint64) error {
	return &CredentialCASConflictError{CurrentLocalVersion: cloneUint64(current)}
}

func cloneUint64(value *uint64) *uint64 {
	if value == nil {
		return nil
	}
	copyValue := *value
	return &copyValue
}
