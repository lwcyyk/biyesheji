package sqlite

import (
	"bytes"
	"context"
	"crypto/sha256"
	"database/sql"
	"errors"
	"fmt"

	credential "vpass.local/vpass/internal/credential/domain"
	"vpass.local/vpass/internal/protocol"
)

var (
	ErrInvalidControlCommit = errors.New("invalid credential control object commit")
	ErrControlCorrupt       = errors.New("credential control objects are corrupt")
	ErrAcceptedStateMissing = errors.New("accepted credential state is missing")
)

// ControlCASConflictError reports the complete current acceptance token. Both
// values are needed because lifecycle transitions may retain a version while
// changing the signed descriptor.
type ControlCASConflictError struct {
	CurrentVersion        *uint64
	CurrentDescriptorHash *[sha256.Size]byte
}

func (err *ControlCASConflictError) Error() string {
	if err == nil || err.CurrentVersion == nil || err.CurrentDescriptorHash == nil {
		return "credential control CAS conflict: no accepted state"
	}
	return fmt.Sprintf(
		"credential control CAS conflict: current accepted version=%d descriptor=%x",
		*err.CurrentVersion,
		err.CurrentDescriptorHash[:],
	)
}

func (err *ControlCASConflictError) Is(target error) bool {
	_, ok := target.(*ControlCASConflictError)
	return ok
}

// AcceptCredentialStateRequest atomically persists the immutable Envelope and
// signed StateDescriptor and advances the one accepted pointer.
type AcceptCredentialStateRequest struct {
	NamespaceID             protocol.NamespaceID
	Envelope                *credential.CredentialEnvelope
	Descriptor              *credential.SignedStateDescriptor
	ExpectedAcceptedVersion *uint64
	ExpectedDescriptorHash  *[sha256.Size]byte
	CreatedAtMilliseconds   uint64
}

type AcceptedCredentialState struct {
	NamespaceID         protocol.NamespaceID
	CredentialID        protocol.CredentialID
	AcceptedVersion     uint64
	Envelope            *credential.CredentialEnvelope
	DescriptorHash      [sha256.Size]byte
	DescriptorSigInput  []byte
	DescriptorSignature protocol.Signature
	UpdatedSequence     uint64
}

type CredentialControlRepository struct {
	database *Database
}

func NewCredentialControlRepository(database *Database) (*CredentialControlRepository, error) {
	if database == nil || database.db == nil {
		return nil, ErrInvalidControlCommit
	}
	return &CredentialControlRepository{database: database}, nil
}

// Accept owns one short BEGIN IMMEDIATE transaction.
func (repository *CredentialControlRepository) Accept(
	ctx context.Context,
	request AcceptCredentialStateRequest,
) (AcceptedCredentialState, error) {
	if repository == nil || repository.database == nil {
		return AcceptedCredentialState{}, ErrInvalidControlCommit
	}
	transaction, err := repository.database.BeginImmediate(ctx)
	if err != nil {
		return AcceptedCredentialState{}, err
	}
	defer func() { _ = transaction.Rollback() }()
	result, err := repository.AcceptState(ctx, transaction, request)
	if err != nil {
		return AcceptedCredentialState{}, err
	}
	if err := transaction.Commit(); err != nil {
		return AcceptedCredentialState{}, err
	}
	return result, nil
}

// AcceptState joins a caller-owned transaction. Credential version, CREATE
// event and outbox writes can therefore commit with the accepted control state.
func (repository *CredentialControlRepository) AcceptState(
	ctx context.Context,
	transaction *Transaction,
	request AcceptCredentialStateRequest,
) (AcceptedCredentialState, error) {
	if repository == nil || transaction == nil || ctx == nil {
		return AcceptedCredentialState{}, ErrInvalidControlCommit
	}
	envelopeCBOR, envelopeHash, descriptorPayload, descriptorHash, err :=
		validateControlCommit(request)
	if err != nil {
		return AcceptedCredentialState{}, err
	}
	defer clear(envelopeCBOR)

	aggregate, err := loadControlAggregate(
		ctx, transaction, request.NamespaceID, request.Envelope.CredentialID(),
		request.Envelope.Version(),
	)
	if err != nil {
		return AcceptedCredentialState{}, err
	}
	if isIdempotentControlReplay(
		request, aggregate, descriptorPayload, envelopeHash, descriptorHash,
	) {
		return acceptedStateFromRequest(request, envelopeHash, descriptorHash), nil
	}
	if err := validateControlAggregate(request, aggregate, descriptorPayload); err != nil {
		return AcceptedCredentialState{}, err
	}
	if err := insertEnvelope(
		ctx, transaction, request, envelopeCBOR, envelopeHash,
	); err != nil {
		return AcceptedCredentialState{}, err
	}
	if err := insertStateDescriptor(
		ctx, transaction, request, descriptorPayload, descriptorHash,
	); err != nil {
		return AcceptedCredentialState{}, err
	}
	if err := advanceControlAcceptance(
		ctx, transaction, request, aggregate, descriptorPayload,
		envelopeHash, descriptorHash,
	); err != nil {
		return AcceptedCredentialState{}, err
	}
	return acceptedStateFromRequest(request, envelopeHash, descriptorHash), nil
}

// LoadAccepted returns immutable bytes for the verifier. A caller must still
// verify the descriptor with receiver-owned key and chain context before use.
func (repository *CredentialControlRepository) LoadAccepted(
	ctx context.Context,
	namespaceID protocol.NamespaceID,
	credentialID protocol.CredentialID,
) (AcceptedCredentialState, error) {
	if repository == nil || repository.database == nil || ctx == nil ||
		bytesAllZero(namespaceID[:]) || bytesAllZero(credentialID[:]) {
		return AcceptedCredentialState{}, ErrInvalidControlCommit
	}
	var version, sequence uint64
	var envelopeCBOR, envelopeHashBytes, descriptorHashBytes, sigInput, signatureBytes []byte
	err := repository.database.db.QueryRowContext(
		ctx,
		`SELECT a.accepted_version, a.updated_sequence,
        e.envelope_cbor, e.envelope_hash,
        d.descriptor_hash, d.sig_input_cbor, d.updater_signature
 FROM credential_acceptance_v2 a
 JOIN credential_envelopes_v2 e
   ON e.envelope_hash = a.accepted_envelope_hash
 JOIN state_descriptors_v2 d
   ON d.descriptor_hash = a.accepted_descriptor_hash
 WHERE a.namespace_id = ? AND a.credential_id = ?`,
		namespaceID[:],
		credentialID[:],
	).Scan(
		&version, &sequence, &envelopeCBOR, &envelopeHashBytes,
		&descriptorHashBytes, &sigInput, &signatureBytes,
	)
	if errors.Is(err, sql.ErrNoRows) {
		return AcceptedCredentialState{}, ErrAcceptedStateMissing
	}
	if err != nil {
		return AcceptedCredentialState{}, err
	}
	envelope, err := credential.ParseCredentialEnvelope(envelopeCBOR)
	clear(envelopeCBOR)
	envelopeDigest := [sha256.Size]byte{}
	if envelope != nil {
		envelopeDigest = envelope.Digest()
	}
	if err != nil || envelope.NamespaceID() != namespaceID ||
		envelope.CredentialID() != credentialID || envelope.Version() != version ||
		len(envelopeHashBytes) != sha256.Size || len(descriptorHashBytes) != sha256.Size ||
		len(signatureBytes) != len(protocol.Signature{}) ||
		!bytes.Equal(envelopeDigest[:], envelopeHashBytes) {
		return AcceptedCredentialState{}, ErrControlCorrupt
	}
	var envelopeHash, descriptorHash [sha256.Size]byte
	var signature protocol.Signature
	copy(envelopeHash[:], envelopeHashBytes)
	copy(descriptorHash[:], descriptorHashBytes)
	copy(signature[:], signatureBytes)
	if signedDigest(sigInput, signature) != descriptorHash {
		return AcceptedCredentialState{}, ErrControlCorrupt
	}
	return AcceptedCredentialState{
		NamespaceID: namespaceID, CredentialID: credentialID,
		AcceptedVersion: version, Envelope: envelope,
		DescriptorHash:      descriptorHash,
		DescriptorSigInput:  append([]byte(nil), sigInput...),
		DescriptorSignature: signature, UpdatedSequence: sequence,
	}, nil
}

type controlAggregate struct {
	namespaceID            protocol.NamespaceID
	localVersion           uint64
	versionDescriptorHash  [sha256.Size]byte
	versionPolicyHash      [sha256.Size]byte
	currentAcceptedPointer *uint64
	acceptedVersion        *uint64
	acceptedDescriptorHash *[sha256.Size]byte
	acceptedEnvelopeHash   *[sha256.Size]byte
	updatedSequence        *uint64
}

func loadControlAggregate(
	ctx context.Context,
	transaction *Transaction,
	namespaceID protocol.NamespaceID,
	credentialID protocol.CredentialID,
	version uint64,
) (controlAggregate, error) {
	var rawNamespace, draftHash, policyHash []byte
	var localVersion uint64
	var acceptedPointer sql.NullInt64
	err := transaction.QueryRowContext(
		ctx,
		`SELECT c.namespace_id, c.current_local_version,
        c.current_accepted_version, v.descriptor_hash, v.policy_hash
 FROM credentials c
 JOIN credential_versions v
   ON v.credential_id = c.credential_id AND v.version = ?
 WHERE c.credential_id = ?`,
		version,
		credentialID[:],
	).Scan(&rawNamespace, &localVersion, &acceptedPointer, &draftHash, &policyHash)
	if errors.Is(err, sql.ErrNoRows) {
		return controlAggregate{}, ErrInvalidControlCommit
	}
	if err != nil {
		return controlAggregate{}, err
	}
	if len(rawNamespace) != protocol.NamespaceIDSize || len(draftHash) != sha256.Size ||
		len(policyHash) != sha256.Size {
		return controlAggregate{}, ErrControlCorrupt
	}
	var aggregate controlAggregate
	copy(aggregate.namespaceID[:], rawNamespace)
	aggregate.localVersion = localVersion
	copy(aggregate.versionDescriptorHash[:], draftHash)
	copy(aggregate.versionPolicyHash[:], policyHash)
	if acceptedPointer.Valid {
		value := uint64(acceptedPointer.Int64)
		aggregate.currentAcceptedPointer = &value
	}

	var acceptedVersion, sequence uint64
	var acceptedDescriptor, acceptedEnvelope []byte
	err = transaction.QueryRowContext(
		ctx,
		`SELECT accepted_version, accepted_descriptor_hash,
        accepted_envelope_hash, updated_sequence
 FROM credential_acceptance_v2
 WHERE namespace_id = ? AND credential_id = ?`,
		namespaceID[:],
		credentialID[:],
	).Scan(&acceptedVersion, &acceptedDescriptor, &acceptedEnvelope, &sequence)
	if errors.Is(err, sql.ErrNoRows) {
		return aggregate, nil
	}
	if err != nil {
		return controlAggregate{}, err
	}
	if len(acceptedDescriptor) != sha256.Size || len(acceptedEnvelope) != sha256.Size {
		return controlAggregate{}, ErrControlCorrupt
	}
	aggregate.acceptedVersion = &acceptedVersion
	aggregate.updatedSequence = &sequence
	var descriptorHash, envelopeHash [sha256.Size]byte
	copy(descriptorHash[:], acceptedDescriptor)
	copy(envelopeHash[:], acceptedEnvelope)
	aggregate.acceptedDescriptorHash = &descriptorHash
	aggregate.acceptedEnvelopeHash = &envelopeHash
	return aggregate, nil
}

func validateControlCommit(
	request AcceptCredentialStateRequest,
) ([]byte, [sha256.Size]byte, credential.StateDescriptorPayload, [sha256.Size]byte, error) {
	if request.Envelope == nil || request.Descriptor == nil ||
		request.CreatedAtMilliseconds == 0 || bytesAllZero(request.NamespaceID[:]) ||
		(request.ExpectedAcceptedVersion == nil) != (request.ExpectedDescriptorHash == nil) {
		return nil, [sha256.Size]byte{}, credential.StateDescriptorPayload{}, [sha256.Size]byte{}, ErrInvalidControlCommit
	}
	envelopeCBOR, err := request.Envelope.MarshalBinary()
	if err != nil {
		return nil, [sha256.Size]byte{}, credential.StateDescriptorPayload{}, [sha256.Size]byte{}, ErrInvalidControlCommit
	}
	envelopeHash := request.Envelope.Digest()
	payload := request.Descriptor.Payload()
	descriptorHash := request.Descriptor.Digest()
	if request.Envelope.NamespaceID() != request.NamespaceID ||
		payload.NamespaceID != request.NamespaceID ||
		payload.CredentialID != request.Envelope.CredentialID() ||
		payload.ActiveVersion != request.Envelope.Version() ||
		payload.ActiveEnvelopeHash != envelopeHash ||
		bytesAllZero(descriptorHash[:]) {
		clear(envelopeCBOR)
		return nil, [sha256.Size]byte{}, credential.StateDescriptorPayload{}, [sha256.Size]byte{}, ErrInvalidControlCommit
	}
	return envelopeCBOR, envelopeHash, payload, descriptorHash, nil
}

func validateControlAggregate(
	request AcceptCredentialStateRequest,
	aggregate controlAggregate,
	payload credential.StateDescriptorPayload,
) error {
	if aggregate.namespaceID != request.NamespaceID ||
		aggregate.localVersion < request.Envelope.Version() ||
		aggregate.versionDescriptorHash != request.Envelope.DescriptorBindingHash() ||
		aggregate.versionPolicyHash != request.Envelope.PolicyHash() {
		return ErrInvalidControlCommit
	}
	if (aggregate.currentAcceptedPointer == nil) != (aggregate.acceptedVersion == nil) ||
		(aggregate.acceptedVersion == nil) != (aggregate.acceptedDescriptorHash == nil) {
		return ErrControlCorrupt
	}
	if aggregate.acceptedVersion == nil {
		if request.ExpectedAcceptedVersion != nil || request.ExpectedDescriptorHash != nil ||
			request.Envelope.Version() != 1 || payload.PreviousDescriptorHash != nil {
			return newControlConflict(aggregate)
		}
		return nil
	}
	if request.ExpectedAcceptedVersion == nil || request.ExpectedDescriptorHash == nil ||
		*request.ExpectedAcceptedVersion != *aggregate.acceptedVersion ||
		*request.ExpectedDescriptorHash != *aggregate.acceptedDescriptorHash ||
		*aggregate.currentAcceptedPointer != *aggregate.acceptedVersion ||
		payload.PreviousDescriptorHash == nil ||
		*payload.PreviousDescriptorHash != *aggregate.acceptedDescriptorHash ||
		aggregate.updatedSequence == nil || payload.FinalSequence <= *aggregate.updatedSequence {
		return newControlConflict(aggregate)
	}
	nextVersion := request.Envelope.Version()
	currentVersion := *aggregate.acceptedVersion
	if nextVersion < currentVersion || nextVersion > currentVersion+1 ||
		(nextVersion == currentVersion && request.Envelope.Digest() != *aggregate.acceptedEnvelopeHash) {
		return newControlConflict(aggregate)
	}
	return nil
}

func isIdempotentControlReplay(
	request AcceptCredentialStateRequest,
	aggregate controlAggregate,
	payload credential.StateDescriptorPayload,
	envelopeHash [sha256.Size]byte,
	descriptorHash [sha256.Size]byte,
) bool {
	return aggregate.acceptedVersion != nil &&
		aggregate.acceptedDescriptorHash != nil &&
		aggregate.acceptedEnvelopeHash != nil &&
		aggregate.updatedSequence != nil &&
		*aggregate.acceptedVersion == payload.ActiveVersion &&
		*aggregate.acceptedDescriptorHash == descriptorHash &&
		*aggregate.acceptedEnvelopeHash == envelopeHash &&
		*aggregate.updatedSequence == payload.FinalSequence &&
		request.Envelope.Version() == payload.ActiveVersion
}

func insertEnvelope(
	ctx context.Context,
	transaction *Transaction,
	request AcceptCredentialStateRequest,
	encoded []byte,
	digest [sha256.Size]byte,
) error {
	envelope := request.Envelope
	credentialID := envelope.CredentialID()
	descriptorBindingHash := envelope.DescriptorBindingHash()
	policyHash := envelope.PolicyHash()
	originBinding := envelope.OriginBinding()
	if _, err := transaction.ExecContext(
		ctx,
		`INSERT INTO credential_envelopes_v2 (
  envelope_hash, namespace_id, credential_id, credential_version,
  envelope_cbor, descriptor_binding_hash, crypto_policy_hash,
  origin_binding, created_at_ms
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(envelope_hash) DO NOTHING`,
		digest[:], request.NamespaceID[:], credentialID[:], envelope.Version(),
		encoded, descriptorBindingHash[:], policyHash[:],
		originBinding[:], request.CreatedAtMilliseconds,
	); err != nil {
		return err
	}
	var matching int
	if err := transaction.QueryRowContext(
		ctx,
		`SELECT count(*) FROM credential_envelopes_v2
 WHERE envelope_hash = ? AND namespace_id = ? AND credential_id = ?
   AND credential_version = ? AND envelope_cbor = ?
   AND descriptor_binding_hash = ? AND crypto_policy_hash = ?
   AND origin_binding = ?`,
		digest[:], request.NamespaceID[:], credentialID[:], envelope.Version(),
		encoded, descriptorBindingHash[:], policyHash[:], originBinding[:],
	).Scan(&matching); err != nil {
		return err
	}
	if matching != 1 {
		return ErrControlCorrupt
	}
	return nil
}

func insertStateDescriptor(
	ctx context.Context,
	transaction *Transaction,
	request AcceptCredentialStateRequest,
	payload credential.StateDescriptorPayload,
	digest [sha256.Size]byte,
) error {
	status, err := payload.LifecycleStatus.DatabaseName()
	if err != nil {
		return ErrInvalidControlCommit
	}
	signature := request.Descriptor.Signature()
	_, err = transaction.ExecContext(
		ctx,
		`INSERT INTO state_descriptors_v2 (
  descriptor_hash, namespace_id, credential_id, active_version,
  active_envelope_hash, previous_descriptor_hash, lifecycle_status,
  last_operation_event, authorized_device_set_root, audit_checkpoint,
  final_sequence, updater_device_id, sig_input_cbor, updater_signature,
  created_at_ms
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
		digest[:], request.NamespaceID[:], payload.CredentialID[:], payload.ActiveVersion,
		payload.ActiveEnvelopeHash[:], optionalHash(payload.PreviousDescriptorHash), status,
		payload.LastOperationEvent[:], payload.AuthorizedDeviceRoot[:], payload.AuditCheckpoint[:],
		payload.FinalSequence, payload.UpdaterDeviceID[:], request.Descriptor.SigInputCBOR(),
		signature[:], request.CreatedAtMilliseconds,
	)
	return err
}

func advanceControlAcceptance(
	ctx context.Context,
	transaction *Transaction,
	request AcceptCredentialStateRequest,
	aggregate controlAggregate,
	payload credential.StateDescriptorPayload,
	envelopeHash [sha256.Size]byte,
	descriptorHash [sha256.Size]byte,
) error {
	if aggregate.acceptedVersion == nil {
		if _, err := transaction.ExecContext(
			ctx,
			`INSERT INTO credential_acceptance_v2 (
  namespace_id, credential_id, accepted_version,
  accepted_descriptor_hash, accepted_envelope_hash, updated_sequence
) VALUES (?, ?, ?, ?, ?, ?)`,
			request.NamespaceID[:], payload.CredentialID[:], payload.ActiveVersion,
			descriptorHash[:], envelopeHash[:], payload.FinalSequence,
		); err != nil {
			return err
		}
		result, err := transaction.ExecContext(
			ctx,
			`UPDATE credentials
 SET current_accepted_version = ?, updated_at_ms = ?
 WHERE credential_id = ? AND namespace_id = ?
   AND current_accepted_version IS NULL`,
			payload.ActiveVersion, request.CreatedAtMilliseconds,
			payload.CredentialID[:], request.NamespaceID[:],
		)
		if err != nil {
			return err
		}
		return requireOneRow(result, newControlConflict(aggregate))
	}
	result, err := transaction.ExecContext(
		ctx,
		`UPDATE credential_acceptance_v2
 SET accepted_version = ?, accepted_descriptor_hash = ?,
     accepted_envelope_hash = ?, updated_sequence = ?
 WHERE namespace_id = ? AND credential_id = ?
   AND accepted_version = ? AND accepted_descriptor_hash = ?`,
		payload.ActiveVersion, descriptorHash[:], envelopeHash[:], payload.FinalSequence,
		request.NamespaceID[:], payload.CredentialID[:],
		*request.ExpectedAcceptedVersion, request.ExpectedDescriptorHash[:],
	)
	if err != nil {
		return err
	}
	if err := requireOneRow(result, newControlConflict(aggregate)); err != nil {
		return err
	}
	result, err = transaction.ExecContext(
		ctx,
		`UPDATE credentials
 SET current_accepted_version = ?, updated_at_ms = ?
 WHERE credential_id = ? AND namespace_id = ?
   AND current_accepted_version = ?`,
		payload.ActiveVersion, request.CreatedAtMilliseconds,
		payload.CredentialID[:], request.NamespaceID[:],
		*request.ExpectedAcceptedVersion,
	)
	if err != nil {
		return err
	}
	return requireOneRow(result, newControlConflict(aggregate))
}

func acceptedStateFromRequest(
	request AcceptCredentialStateRequest,
	envelopeHash [sha256.Size]byte,
	descriptorHash [sha256.Size]byte,
) AcceptedCredentialState {
	payload := request.Descriptor.Payload()
	return AcceptedCredentialState{
		NamespaceID: request.NamespaceID, CredentialID: payload.CredentialID,
		AcceptedVersion: payload.ActiveVersion, Envelope: request.Envelope,
		DescriptorHash:      descriptorHash,
		DescriptorSigInput:  request.Descriptor.SigInputCBOR(),
		DescriptorSignature: request.Descriptor.Signature(),
		UpdatedSequence:     payload.FinalSequence,
	}
}

func newControlConflict(aggregate controlAggregate) error {
	return &ControlCASConflictError{
		CurrentVersion:        cloneUint64(aggregate.acceptedVersion),
		CurrentDescriptorHash: cloneHash32(aggregate.acceptedDescriptorHash),
	}
}

func cloneHash32(value *[sha256.Size]byte) *[sha256.Size]byte {
	if value == nil {
		return nil
	}
	copyValue := *value
	return &copyValue
}

func requireOneRow(result sql.Result, conflict error) error {
	count, err := result.RowsAffected()
	if err != nil {
		return err
	}
	if count != 1 {
		return conflict
	}
	return nil
}

func signedDigest(sigInput []byte, signature protocol.Signature) [sha256.Size]byte {
	hasher := sha256.New()
	_, _ = hasher.Write(sigInput)
	_, _ = hasher.Write(signature[:])
	var result [sha256.Size]byte
	copy(result[:], hasher.Sum(nil))
	return result
}
