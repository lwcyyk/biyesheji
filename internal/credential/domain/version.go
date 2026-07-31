package domain

import (
	"crypto/sha256"
	"errors"
	"sort"

	"vdns.local/vdns/internal/cryptokit"
	"vdns.local/vdns/internal/platform"
	"vdns.local/vdns/internal/protocol"
)

var (
	ErrInvalidCredentialVersion = errors.New("invalid credential version")
	ErrInvalidVersionTransition = errors.New("invalid credential version transition")
	ErrFieldObjectMismatch      = errors.New("encrypted field object does not match its reference")
)

// RecoveryAction is the deterministic next action after process restart.
type RecoveryAction uint8

const (
	RecoveryNone RecoveryAction = iota + 1
	RecoveryStartSiteChange
	RecoveryQuerySiteReceipt
	RecoveryRetrySiteChange
	RecoveryRequireReview
	RecoveryCommitLocalCandidate
	RecoveryPublishCandidate
)

// AggregateStatus is separate from the lifecycle of any individual version.
type AggregateStatus uint8

const (
	AggregateActive AggregateStatus = iota + 1
	AggregateSuspended
	AggregateRevoked
)

func (status AggregateStatus) Valid() bool {
	return status >= AggregateActive && status <= AggregateRevoked
}

func (status AggregateStatus) DatabaseName() (string, error) {
	switch status {
	case AggregateActive:
		return "ACTIVE", nil
	case AggregateSuspended:
		return "SUSPENDED", nil
	case AggregateRevoked:
		return "REVOKED", nil
	default:
		return "", ErrInvalidCredentialVersion
	}
}

// VersionStatus is the crash-recoverable credential version state machine.
type VersionStatus uint8

const (
	VersionPendingCandidate VersionStatus = iota + 1
	VersionSiteUpdatePending
	VersionFailedRetryable
	VersionSiteStatusUnknown
	VersionSiteChangedLocalCommitPending
	VersionActiveLocalPendingProof
	VersionActive
	VersionSuperseded
	VersionAborted
)

func (status VersionStatus) Valid() bool {
	return status >= VersionPendingCandidate && status <= VersionAborted
}

func (status VersionStatus) DatabaseName() (string, error) {
	switch status {
	case VersionPendingCandidate:
		return "PENDING_CANDIDATE", nil
	case VersionSiteUpdatePending:
		return "SITE_UPDATE_PENDING", nil
	case VersionFailedRetryable:
		return "FAILED_RETRYABLE", nil
	case VersionSiteStatusUnknown:
		return "SITE_STATUS_UNKNOWN", nil
	case VersionSiteChangedLocalCommitPending:
		return "SITE_CHANGED_LOCAL_COMMIT_PENDING", nil
	case VersionActiveLocalPendingProof:
		return "ACTIVE_LOCAL_PENDING_PROOF", nil
	case VersionActive:
		return "ACTIVE", nil
	case VersionSuperseded:
		return "SUPERSEDED", nil
	case VersionAborted:
		return "ABORTED", nil
	default:
		return "", ErrInvalidCredentialVersion
	}
}

// CanTransitionTo is the only lifecycle transition table used by application
// services. Repeating a state is not a transition and is rejected.
func (status VersionStatus) CanTransitionTo(next VersionStatus) bool {
	switch status {
	case VersionPendingCandidate:
		return next == VersionSiteUpdatePending || next == VersionAborted
	case VersionSiteUpdatePending:
		return next == VersionFailedRetryable || next == VersionSiteStatusUnknown ||
			next == VersionSiteChangedLocalCommitPending
	case VersionFailedRetryable:
		return next == VersionSiteUpdatePending || next == VersionAborted
	case VersionSiteStatusUnknown:
		return next == VersionSiteUpdatePending
	case VersionSiteChangedLocalCommitPending:
		return next == VersionActiveLocalPendingProof
	case VersionActiveLocalPendingProof:
		return next == VersionActive
	case VersionActive:
		return next == VersionSuperseded
	default:
		return false
	}
}

// RequireTransition returns a stable domain error for illegal edges.
func RequireTransition(current, next VersionStatus) error {
	if !current.Valid() || !next.Valid() || !current.CanTransitionTo(next) {
		return ErrInvalidVersionTransition
	}
	return nil
}

// RecoveryAction maps every durable internal state to a restart-safe action.
// In particular, an in-flight site request is queried, never blindly replayed.
func (status VersionStatus) RecoveryAction() (RecoveryAction, error) {
	switch status {
	case VersionPendingCandidate:
		return RecoveryStartSiteChange, nil
	case VersionSiteUpdatePending:
		return RecoveryQuerySiteReceipt, nil
	case VersionFailedRetryable:
		return RecoveryRetrySiteChange, nil
	case VersionSiteStatusUnknown:
		return RecoveryRequireReview, nil
	case VersionSiteChangedLocalCommitPending:
		return RecoveryCommitLocalCandidate, nil
	case VersionActiveLocalPendingProof:
		return RecoveryPublishCandidate, nil
	case VersionActive, VersionSuperseded, VersionAborted:
		return RecoveryNone, nil
	default:
		return 0, ErrInvalidCredentialVersion
	}
}

// RequireEvidenceTransition applies the evidence gate to activation. Browser
// fill, submit and inferred-login observations can never activate a candidate.
func RequireEvidenceTransition(
	current, next VersionStatus,
	evidence protocol.EvidenceLevel,
) error {
	if err := RequireTransition(current, next); err != nil {
		return err
	}
	if next == VersionActive && !evidence.ActivatesCredential() {
		return ErrInvalidVersionTransition
	}
	return nil
}

// FieldMapping is an immutable database projection for one encrypted field.
type FieldMapping struct {
	reference       cryptokit.FieldReference
	objectReference platform.ObjectRef
	wrappedDEK      []byte
	wrappedDEKSuite string
	fieldDigest     [sha256.Size]byte
}

// NewFieldMapping validates exact object bytes before accepting their content
// address and derives the canonical seven-field digest.
func NewFieldMapping(encrypted *cryptokit.EncryptedField, objectReference platform.ObjectRef) (FieldMapping, error) {
	if encrypted == nil || objectReference.Size == 0 {
		return FieldMapping{}, ErrFieldObjectMismatch
	}
	encoded, err := encrypted.MarshalBinary()
	if err != nil || uint64(len(encoded)) != objectReference.Size || sha256.Sum256(encoded) != objectReference.Digest {
		clear(encoded)
		return FieldMapping{}, ErrFieldObjectMismatch
	}
	clear(encoded)
	reference, err := encrypted.Reference()
	if err != nil {
		return FieldMapping{}, ErrFieldObjectMismatch
	}
	wrappedDEK, suite, err := encrypted.WrappedDEKProjection()
	if err != nil {
		return FieldMapping{}, ErrFieldObjectMismatch
	}
	fieldDigest, err := cryptokit.FieldReferenceDigest(reference)
	if err != nil {
		clear(wrappedDEK)
		return FieldMapping{}, ErrFieldObjectMismatch
	}
	return restoreFieldMapping(reference, objectReference, wrappedDEK, suite, fieldDigest)
}

func restoreFieldMapping(
	reference cryptokit.FieldReference,
	objectReference platform.ObjectRef,
	wrappedDEK []byte,
	suite string,
	fieldDigest [sha256.Size]byte,
) (FieldMapping, error) {
	wantDigest, err := cryptokit.FieldReferenceDigest(reference)
	if err != nil || wantDigest != fieldDigest || objectReference.Size == 0 ||
		len(wrappedDEK) == 0 || len(wrappedDEK) > 4096 || suite != protocol.SuiteID {
		return FieldMapping{}, ErrFieldObjectMismatch
	}
	return FieldMapping{
		reference:       reference,
		objectReference: objectReference,
		wrappedDEK:      append([]byte(nil), wrappedDEK...),
		wrappedDEKSuite: suite,
		fieldDigest:     fieldDigest,
	}, nil
}

// RestoreFieldMapping validates a database projection before rebuilding the
// immutable domain value.
func RestoreFieldMapping(
	reference cryptokit.FieldReference,
	objectReference platform.ObjectRef,
	wrappedDEK []byte,
	suite string,
	fieldDigest [sha256.Size]byte,
) (FieldMapping, error) {
	return restoreFieldMapping(
		reference, objectReference, wrappedDEK, suite, fieldDigest,
	)
}

func (mapping FieldMapping) Reference() cryptokit.FieldReference { return mapping.reference }
func (mapping FieldMapping) ObjectReference() platform.ObjectRef { return mapping.objectReference }
func (mapping FieldMapping) WrappedDEKSuite() string             { return mapping.wrappedDEKSuite }
func (mapping FieldMapping) FieldDigest() [sha256.Size]byte      { return mapping.fieldDigest }

func (mapping FieldMapping) WrappedDEK() []byte {
	return append([]byte(nil), mapping.wrappedDEK...)
}

// VersionDraft is an immutable descriptor plus its field mappings. Mutable
// lifecycle state is deliberately excluded from the DescriptorHash.
type VersionDraft struct {
	credentialID           protocol.CredentialID
	version                uint64
	passwordVersion        uint64
	status                 VersionStatus
	previousDescriptorHash *[sha256.Size]byte
	policyHash             [sha256.Size]byte
	fields                 []FieldMapping
	descriptorCBOR         []byte
	descriptorHash         [sha256.Size]byte
}

type versionDescriptor struct {
	ProtocolVersion        uint64                     `cbor:"protocol_version"`
	SuiteID                string                     `cbor:"suite_id"`
	CredentialID           protocol.CredentialID      `cbor:"credential_id"`
	Version                uint64                     `cbor:"version"`
	PasswordVersion        uint64                     `cbor:"password_version"`
	PreviousDescriptorHash *[sha256.Size]byte         `cbor:"previous_descriptor_hash"`
	PolicyHash             [sha256.Size]byte          `cbor:"policy_hash"`
	Fields                 []descriptorFieldReference `cbor:"fields"`
}

type descriptorFieldReference struct {
	Reference         cryptokit.FieldReference `cbor:"reference"`
	StorageObjectHash [sha256.Size]byte        `cbor:"storage_object_hash"`
	FieldDigest       [sha256.Size]byte        `cbor:"field_digest"`
}

// NewVersionDraft validates field uniqueness and creates a deterministic
// descriptor sorted by the frozen integer FieldType registry.
func NewVersionDraft(
	credentialID protocol.CredentialID,
	version uint64,
	passwordVersion uint64,
	status VersionStatus,
	previousDescriptorHash *[sha256.Size]byte,
	policyHash [sha256.Size]byte,
	fields []FieldMapping,
) (*VersionDraft, error) {
	if version == 0 || passwordVersion == 0 || passwordVersion > version || !status.Valid() || len(fields) == 0 ||
		(version == 1) != (previousDescriptorHash == nil) {
		return nil, ErrInvalidCredentialVersion
	}
	sortedFields := append([]FieldMapping(nil), fields...)
	sort.Slice(sortedFields, func(i, j int) bool {
		return sortedFields[i].reference.FieldType < sortedFields[j].reference.FieldType
	})
	descriptorFields := make([]descriptorFieldReference, 0, len(sortedFields))
	seen := make(map[cryptokit.FieldType]struct{}, len(sortedFields))
	hasPassword := false
	for _, field := range sortedFields {
		reference := field.Reference()
		if _, exists := seen[reference.FieldType]; exists || !reference.FieldType.Valid() ||
			reference.EncryptionVersion > version {
			return nil, ErrInvalidCredentialVersion
		}
		seen[reference.FieldType] = struct{}{}
		hasPassword = hasPassword || reference.FieldType == cryptokit.FieldPassword
		descriptorFields = append(descriptorFields, descriptorFieldReference{
			Reference:         reference,
			StorageObjectHash: field.ObjectReference().Digest,
			FieldDigest:       field.FieldDigest(),
		})
	}
	if !hasPassword {
		return nil, ErrInvalidCredentialVersion
	}
	descriptor := versionDescriptor{
		ProtocolVersion:        protocol.ProtocolVersion,
		SuiteID:                protocol.SuiteID,
		CredentialID:           credentialID,
		Version:                version,
		PasswordVersion:        passwordVersion,
		PreviousDescriptorHash: cloneHash(previousDescriptorHash),
		PolicyHash:             policyHash,
		Fields:                 descriptorFields,
	}
	encoded, err := protocol.MarshalDeterministic(descriptor)
	if err != nil {
		return nil, ErrInvalidCredentialVersion
	}
	digest := sha256.Sum256(encoded)
	return &VersionDraft{
		credentialID:           credentialID,
		version:                version,
		passwordVersion:        passwordVersion,
		status:                 status,
		previousDescriptorHash: cloneHash(previousDescriptorHash),
		policyHash:             policyHash,
		fields:                 sortedFields,
		descriptorCBOR:         encoded,
		descriptorHash:         digest,
	}, nil
}

func (draft *VersionDraft) CredentialID() protocol.CredentialID { return draft.credentialID }
func (draft *VersionDraft) Version() uint64                     { return draft.version }
func (draft *VersionDraft) PasswordVersion() uint64             { return draft.passwordVersion }
func (draft *VersionDraft) Status() VersionStatus               { return draft.status }
func (draft *VersionDraft) PolicyHash() [sha256.Size]byte       { return draft.policyHash }
func (draft *VersionDraft) DescriptorHash() [sha256.Size]byte   { return draft.descriptorHash }

func (draft *VersionDraft) PreviousDescriptorHash() *[sha256.Size]byte {
	if draft == nil {
		return nil
	}
	return cloneHash(draft.previousDescriptorHash)
}

func (draft *VersionDraft) DescriptorCBOR() []byte {
	if draft == nil {
		return nil
	}
	return append([]byte(nil), draft.descriptorCBOR...)
}

func (draft *VersionDraft) Fields() []FieldMapping {
	if draft == nil {
		return nil
	}
	result := make([]FieldMapping, len(draft.fields))
	for i, field := range draft.fields {
		result[i] = field
		result[i].wrappedDEK = field.WrappedDEK()
	}
	return result
}

func cloneHash(value *[sha256.Size]byte) *[sha256.Size]byte {
	if value == nil {
		return nil
	}
	copyValue := *value
	return &copyValue
}
