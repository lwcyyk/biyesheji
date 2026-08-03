package protocol

// OperationType is the VPass v2 frozen wire enum. Database and JSON names are
// projections; signed deterministic CBOR carries these integer values.
type OperationType uint16

const (
	OperationCreate            OperationType = 1
	OperationResolve           OperationType = 2
	OperationAutofill          OperationType = 3
	OperationUseObserved       OperationType = 4
	OperationUpdatePrepare     OperationType = 5
	OperationUpdateConfirm     OperationType = 6
	OperationSyncPublish       OperationType = 7
	OperationSyncAccept        OperationType = 8
	OperationRotate            OperationType = 9
	OperationMigrate           OperationType = 10
	OperationSuspend           OperationType = 11
	OperationRevoke            OperationType = 12
	OperationDeviceEnroll      OperationType = 13
	OperationRelationPublish   OperationType = 14
	OperationAuditAnalyze      OperationType = 15
	OperationExposureAnalyze   OperationType = 16
	OperationRemediationCommit OperationType = 17
)

// Valid reports whether operation belongs to the VPass v2 registry.
func (operation OperationType) Valid() bool {
	return operation >= OperationCreate && operation <= OperationRemediationCommit
}

// DatabaseName returns the stable SQLite/JSON projection for an operation.
func (operation OperationType) DatabaseName() (string, error) {
	switch operation {
	case OperationCreate:
		return "CREATE", nil
	case OperationResolve:
		return "RESOLVE", nil
	case OperationAutofill:
		return "AUTOFILL", nil
	case OperationUseObserved:
		return "USE_OBSERVED", nil
	case OperationUpdatePrepare:
		return "UPDATE_PREPARE", nil
	case OperationUpdateConfirm:
		return "UPDATE_CONFIRM", nil
	case OperationSyncPublish:
		return "SYNC_PUBLISH", nil
	case OperationSyncAccept:
		return "SYNC_ACCEPT", nil
	case OperationRotate:
		return "ROTATE", nil
	case OperationMigrate:
		return "MIGRATE", nil
	case OperationSuspend:
		return "SUSPEND", nil
	case OperationRevoke:
		return "REVOKE", nil
	case OperationDeviceEnroll:
		return "DEVICE_ENROLL", nil
	case OperationRelationPublish:
		return "RELATION_PUBLISH", nil
	case OperationAuditAnalyze:
		return "AUDIT_ANALYZE", nil
	case OperationExposureAnalyze:
		// The v1 SQLite prototype used this projection. Keeping the spelling is
		// not wire compatibility: protocol/suite and integer enum have changed.
		return "ANALYZE_EXPOSURE", nil
	case OperationRemediationCommit:
		return "REMEDIATION_COMMIT", nil
	default:
		return "", reject(CodeUnsupportedObject, "operationType", nil)
	}
}

// ParseOperationDatabaseName converts the stable projection back to its v2
// wire enum. Unknown and old rotation names fail closed.
func ParseOperationDatabaseName(name string) (OperationType, error) {
	switch name {
	case "CREATE":
		return OperationCreate, nil
	case "RESOLVE":
		return OperationResolve, nil
	case "AUTOFILL":
		return OperationAutofill, nil
	case "USE_OBSERVED":
		return OperationUseObserved, nil
	case "UPDATE_PREPARE":
		return OperationUpdatePrepare, nil
	case "UPDATE_CONFIRM":
		return OperationUpdateConfirm, nil
	case "SYNC_PUBLISH":
		return OperationSyncPublish, nil
	case "SYNC_ACCEPT":
		return OperationSyncAccept, nil
	case "ROTATE":
		return OperationRotate, nil
	case "MIGRATE":
		return OperationMigrate, nil
	case "SUSPEND":
		return OperationSuspend, nil
	case "REVOKE":
		return OperationRevoke, nil
	case "DEVICE_ENROLL":
		return OperationDeviceEnroll, nil
	case "RELATION_PUBLISH":
		return OperationRelationPublish, nil
	case "AUDIT_ANALYZE":
		return OperationAuditAnalyze, nil
	case "ANALYZE_EXPOSURE":
		return OperationExposureAnalyze, nil
	case "REMEDIATION_COMMIT":
		return OperationRemediationCommit, nil
	default:
		return 0, reject(CodeUnsupportedObject, "operationType", nil)
	}
}

// Capability is a root-signed bit capability. A credential may carry several
// bits, while RequiredCapability always returns one exact bit.
type Capability uint16

const (
	CapabilityRead            Capability = 1 << 0
	CapabilityAutofill        Capability = 1 << 1
	CapabilityPublishAudit    Capability = 1 << 2
	CapabilityCreate          Capability = 1 << 3
	CapabilityUpdate          Capability = 1 << 4
	CapabilityRotate          Capability = 1 << 5
	CapabilityMigrate         Capability = 1 << 6
	CapabilityRevoke          Capability = 1 << 7
	CapabilityDeviceEnroll    Capability = 1 << 8
	CapabilityRelationPublish Capability = 1 << 9
	CapabilityAuditAnalyze    Capability = 1 << 10
)

const allCapabilities = CapabilityRead | CapabilityAutofill |
	CapabilityPublishAudit | CapabilityCreate | CapabilityUpdate |
	CapabilityRotate | CapabilityMigrate | CapabilityRevoke |
	CapabilityDeviceEnroll | CapabilityRelationPublish |
	CapabilityAuditAnalyze

// Valid reports whether a non-empty capability set contains only registered
// VPass v2 frozen wire bits.
func (capability Capability) Valid() bool {
	return capability != 0 && capability&^allCapabilities == 0
}

// Allows reports whether a capability set includes one required bit.
func (capability Capability) Allows(required Capability) bool {
	return capability.Valid() && required.Valid() &&
		required&(required-1) == 0 && capability&required == required
}

// CredentialScopeType is the frozen authorization-scope enum carried by a
// root-signed DeviceOperationCredential. Scope contents remain private to the
// credential object and are not copied into public transparency-log leaves.
type CredentialScopeType uint8

const (
	ScopeNamespaceAll     CredentialScopeType = 1
	ScopeCredentialSet    CredentialScopeType = 2
	ScopeOriginBindingSet CredentialScopeType = 3
	ScopeSingleCredential CredentialScopeType = 4
)

// Valid reports whether the scope belongs to the VPass v2 registry.
func (scope CredentialScopeType) Valid() bool {
	return scope >= ScopeNamespaceAll && scope <= ScopeSingleCredential
}

// RequiredCapability returns the authorization required for one operation.
func (operation OperationType) RequiredCapability() (Capability, error) {
	switch operation {
	case OperationCreate:
		return CapabilityCreate, nil
	case OperationResolve, OperationSyncAccept:
		return CapabilityRead, nil
	case OperationAutofill:
		return CapabilityAutofill, nil
	case OperationUseObserved:
		return CapabilityPublishAudit, nil
	case OperationUpdatePrepare, OperationUpdateConfirm, OperationSyncPublish:
		return CapabilityUpdate, nil
	case OperationRotate, OperationRemediationCommit:
		return CapabilityRotate, nil
	case OperationMigrate:
		return CapabilityMigrate, nil
	case OperationSuspend, OperationRevoke:
		return CapabilityRevoke, nil
	case OperationDeviceEnroll:
		return CapabilityDeviceEnroll, nil
	case OperationRelationPublish:
		return CapabilityRelationPublish, nil
	case OperationAuditAnalyze, OperationExposureAnalyze:
		return CapabilityAuditAnalyze, nil
	default:
		return 0, reject(CodeUnsupportedObject, "operationType", nil)
	}
}

// EvidenceLevel is the v2.1 E0-E5 confirmation taxonomy. Value zero is a
// deliberate E0 observation, not an unspecified value; persisted objects must
// also carry evidence schema version 2.
type EvidenceLevel uint8

const (
	EvidenceAutofillObserved            EvidenceLevel = 0
	EvidenceSubmitObserved              EvidenceLevel = 1
	EvidencePageSuccessIndicated        EvidenceLevel = 2
	EvidenceNewPasswordReloginConfirmed EvidenceLevel = 3
	EvidenceSiteSignedReceipt           EvidenceLevel = 4
	EvidenceUserSignedConfirmation      EvidenceLevel = 5
)

// Valid reports whether evidence belongs to the VPass v2 registry.
func (evidence EvidenceLevel) Valid() bool {
	return evidence <= EvidenceUserSignedConfirmation
}

// EvidenceActivationPolicy records the trust checks already completed by L5.
type EvidenceActivationPolicy struct {
	AllowStrictRelogin    bool
	TrustedSiteConnector  bool
	AllowUserConfirmation bool
}

// CanActivateCredential applies the frozen E0-E5 policy without conflating a
// browser observation, a trusted site receipt and a user statement.
func (evidence EvidenceLevel) CanActivateCredential(policy EvidenceActivationPolicy) bool {
	switch evidence {
	case EvidenceNewPasswordReloginConfirmed:
		return policy.AllowStrictRelogin
	case EvidenceSiteSignedReceipt:
		return policy.TrustedSiteConnector
	case EvidenceUserSignedConfirmation:
		return policy.AllowUserConfirmation
	default:
		return false
	}
}

// ActivatesCredential is the post-verification domain gate used by aggregate
// code whose caller has already authenticated E4/E5. E3 always requires the
// explicit policy method above.
func (evidence EvidenceLevel) ActivatesCredential() bool {
	return evidence == EvidenceSiteSignedReceipt ||
		evidence == EvidenceUserSignedConfirmation
}

func (evidence EvidenceLevel) DatabaseName() (string, error) {
	switch evidence {
	case EvidenceAutofillObserved:
		return "AUTOFILL_OBSERVED", nil
	case EvidenceSubmitObserved:
		return "SUBMIT_OBSERVED", nil
	case EvidencePageSuccessIndicated:
		return "PAGE_SUCCESS_INDICATED", nil
	case EvidenceNewPasswordReloginConfirmed:
		return "NEW_PASSWORD_RELOGIN_CONFIRMED", nil
	case EvidenceSiteSignedReceipt:
		return "SITE_SIGNED_RECEIPT", nil
	case EvidenceUserSignedConfirmation:
		return "USER_SIGNED_CONFIRMATION", nil
	default:
		return "", reject(CodeUnsupportedObject, "evidenceLevel", nil)
	}
}

func ParseEvidenceDatabaseName(name string) (EvidenceLevel, error) {
	switch name {
	case "AUTOFILL_OBSERVED":
		return EvidenceAutofillObserved, nil
	case "SUBMIT_OBSERVED":
		return EvidenceSubmitObserved, nil
	case "PAGE_SUCCESS_INDICATED":
		return EvidencePageSuccessIndicated, nil
	case "NEW_PASSWORD_RELOGIN_CONFIRMED":
		return EvidenceNewPasswordReloginConfirmed, nil
	case "SITE_SIGNED_RECEIPT":
		return EvidenceSiteSignedReceipt, nil
	case "USER_SIGNED_CONFIRMATION":
		return EvidenceUserSignedConfirmation, nil
	default:
		return 0, reject(CodeUnsupportedObject, "evidenceLevel", nil)
	}
}

// LifecycleStatus is the frozen externally resolved credential state. It is
// intentionally distinct from the crash-recovery state of a local candidate
// version.
type LifecycleStatus uint8

const (
	LifecycleActive             LifecycleStatus = 1
	LifecycleUpdatePending      LifecycleStatus = 2
	LifecycleSiteConfirmPending LifecycleStatus = 3
	LifecycleSuspended          LifecycleStatus = 4
	LifecycleSuperseded         LifecycleStatus = 5
	LifecycleRevoked            LifecycleStatus = 6
	LifecycleConflicted         LifecycleStatus = 7
)

// Valid reports whether status belongs to the VPass v2 registry.
func (status LifecycleStatus) Valid() bool {
	return status >= LifecycleActive && status <= LifecycleConflicted
}

// Verdict is the frozen L5 outcome registry. Rejection values deliberately
// preserve the layer that failed so callers never collapse a security failure
// into a successful API response.
type Verdict uint8

const (
	VerdictAccept             Verdict = 1
	VerdictDegradedOffline    Verdict = 2
	VerdictDegradedPendingLog Verdict = 3
	VerdictReviewRequired     Verdict = 4
	VerdictRejectIdentity     Verdict = 5
	VerdictRejectCapability   Verdict = 6
	VerdictRejectRevoked      Verdict = 7
	VerdictRejectCausal       Verdict = 8
	VerdictRejectProof        Verdict = 9
	VerdictRejectOrigin       Verdict = 10
	VerdictRejectPolicy       Verdict = 11
	VerdictRejectObject       Verdict = 12
)

// Valid reports whether verdict belongs to the VPass v2 registry.
func (verdict Verdict) Valid() bool {
	return verdict >= VerdictAccept && verdict <= VerdictRejectObject
}

// Accepted reports whether the caller may proceed under the returned mode.
// REVIEW_REQUIRED and every REJECT value fail closed.
func (verdict Verdict) Accepted() bool {
	return verdict == VerdictAccept ||
		verdict == VerdictDegradedOffline ||
		verdict == VerdictDegradedPendingLog
}

// DatabaseName returns the stable API/SQLite spelling frozen by the registry.
func (verdict Verdict) DatabaseName() (string, error) {
	switch verdict {
	case VerdictAccept:
		return "ACCEPT", nil
	case VerdictDegradedOffline:
		return "DEGRADED_OFFLINE", nil
	case VerdictDegradedPendingLog:
		return "DEGRADED_PENDING_LOG", nil
	case VerdictReviewRequired:
		return "REVIEW_REQUIRED", nil
	case VerdictRejectIdentity:
		return "REJECT_IDENTITY", nil
	case VerdictRejectCapability:
		return "REJECT_CAPABILITY", nil
	case VerdictRejectRevoked:
		return "REJECT_REVOKED", nil
	case VerdictRejectCausal:
		return "REJECT_CAUSAL", nil
	case VerdictRejectProof:
		return "REJECT_PROOF", nil
	case VerdictRejectOrigin:
		return "REJECT_ORIGIN", nil
	case VerdictRejectPolicy:
		return "REJECT_POLICY", nil
	case VerdictRejectObject:
		return "REJECT_OBJECT", nil
	default:
		return "", reject(CodeUnsupportedObject, "verdict", nil)
	}
}

// DatabaseName returns the stable SQLite/API spelling.
func (status LifecycleStatus) DatabaseName() (string, error) {
	switch status {
	case LifecycleActive:
		return "ACTIVE", nil
	case LifecycleUpdatePending:
		return "UPDATE_PENDING", nil
	case LifecycleSiteConfirmPending:
		return "SITE_CONFIRM_PENDING", nil
	case LifecycleSuspended:
		return "SUSPENDED", nil
	case LifecycleSuperseded:
		return "SUPERSEDED", nil
	case LifecycleRevoked:
		return "REVOKED", nil
	case LifecycleConflicted:
		return "CONFLICTED", nil
	default:
		return "", reject(CodeUnsupportedObject, "lifecycleStatus", nil)
	}
}

// ParseLifecycleDatabaseName converts the stable projection to the wire enum.
func ParseLifecycleDatabaseName(name string) (LifecycleStatus, error) {
	switch name {
	case "ACTIVE":
		return LifecycleActive, nil
	case "UPDATE_PENDING":
		return LifecycleUpdatePending, nil
	case "SITE_CONFIRM_PENDING":
		return LifecycleSiteConfirmPending, nil
	case "SUSPENDED":
		return LifecycleSuspended, nil
	case "SUPERSEDED":
		return LifecycleSuperseded, nil
	case "REVOKED":
		return LifecycleRevoked, nil
	case "CONFLICTED":
		return LifecycleConflicted, nil
	default:
		return 0, reject(CodeUnsupportedObject, "lifecycleStatus", nil)
	}
}

// RiskClass is the optional privacy-analysis result enum.
type RiskClass uint8

const (
	RiskCurrentDirect        RiskClass = 1
	RiskHistoricalExposure   RiskClass = 2
	RiskInsufficientEvidence RiskClass = 3
	RiskRemediated           RiskClass = 4
	RiskUnaffected           RiskClass = 5
)

func (risk RiskClass) Valid() bool {
	return risk >= RiskCurrentDirect && risk <= RiskUnaffected
}

// CheckpointType identifies independently committed state roots.
type CheckpointType uint8

const (
	CheckpointIdentity      CheckpointType = 1
	CheckpointAuthorization CheckpointType = 2
	CheckpointRevocation    CheckpointType = 3
	CheckpointCredential    CheckpointType = 4
	CheckpointAudit         CheckpointType = 5
	CheckpointAffected      CheckpointType = 6
	CheckpointRotation      CheckpointType = 7
	CheckpointVRF           CheckpointType = 8
)

func (checkpointType CheckpointType) Valid() bool {
	return checkpointType >= CheckpointIdentity && checkpointType <= CheckpointVRF
}
