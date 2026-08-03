// Package domain contains verifiable state resolution decisions without HTTP, SQL, storage
// storage or chain dependencies.
package domain

import (
	"crypto/sha256"

	credentialdomain "vpass.local/vpass/internal/credential/domain"
	operationdomain "vpass.local/vpass/internal/operation/domain"
	"vpass.local/vpass/internal/protocol"
	transparencydomain "vpass.local/vpass/internal/transparency/domain"
)

// Layer identifies the five ordered verification layers.
type Layer uint8

const (
	LayerIdentity     Layer = 1
	LayerCapability   Layer = 2
	LayerDynamicState Layer = 3
	LayerTransparency Layer = 4
	LayerLocalPolicy  Layer = 5
)

// ReasonCode is stable and safe to expose in API and experiment output.
type ReasonCode string

const (
	CodeOK                    ReasonCode = "OK"
	CodeIdentityRootChain     ReasonCode = "L1_ROOT_CHAIN_INVALID"
	CodeIdentityNamespace     ReasonCode = "L1_NAMESPACE_MISMATCH"
	CodeIdentitySignature     ReasonCode = "L1_SIGNATURE_INVALID"
	CodeIdentityKeyGeneration ReasonCode = "L1_KEY_GENERATION_MISMATCH"
	CodeCapabilityOperation   ReasonCode = "L2_OPERATION_DENIED"
	CodeCapabilityScope       ReasonCode = "L2_SCOPE_DENIED"
	CodeCapabilitySequence    ReasonCode = "L2_SEQUENCE_INVALID"
	CodeCapabilityCounter     ReasonCode = "L2_ISSUANCE_COUNTER_STALE"
	CodeCapabilityStatus      ReasonCode = "L2_STATUS_REFERENCE_STALE"
	CodeStateRevoked          ReasonCode = "L3_DEVICE_REVOKED"
	CodeStateVersion          ReasonCode = "L3_VERSION_ROLLBACK"
	CodeStateCounter          ReasonCode = "L3_DEVICE_COUNTER_INVALID"
	CodeStatePredecessor      ReasonCode = "L3_PREDECESSOR_INVALID"
	CodeStateLifecycle        ReasonCode = "L3_LIFECYCLE_EDGE_INVALID"
	CodeStateConflict         ReasonCode = "L3_DESCRIPTOR_CONFLICT"
	CodeStateFinalOrder       ReasonCode = "L3_FINAL_ORDER_RECEIPT_INVALID"
	CodeProofBundle           ReasonCode = "L4_BUNDLE_INVALID"
	CodeProofTreeHead         ReasonCode = "L4_TREE_HEAD_INVALID"
	CodeProofInclusion        ReasonCode = "L4_INCLUSION_INVALID"
	CodeProofConsistency      ReasonCode = "L4_CONSISTENCY_INVALID"
	CodeProofAnchor           ReasonCode = "L4_ANCHOR_INVALID"
	CodePolicyOffline         ReasonCode = "L5_OFFLINE_CACHE"
	CodePolicyPendingLog      ReasonCode = "L5_PENDING_LOG"
	CodePolicyHighRisk        ReasonCode = "L5_HIGH_RISK_NO_DEGRADE"
	CodePolicyUserReview      ReasonCode = "L5_USER_REVIEW"
	CodePolicyCacheExpired    ReasonCode = "L5_CACHE_EXPIRED"
)

type LayerResult struct {
	Layer  Layer
	Passed bool
	Code   ReasonCode
}

// Principal is the verified operation actor returned to callers.
type Principal struct {
	NamespaceID          protocol.NamespaceID
	DeviceID             protocol.DeviceID
	DeviceCredentialHash [sha256.Size]byte
	SecretGeneration     uint64
}

// Authorization is the verified L2 projection.
type Authorization struct {
	Operation       protocol.OperationType
	Capabilities    protocol.Capability
	ScopeDigest     [sha256.Size]byte
	FinalSequence   uint64
	IssuanceCounter uint64
}

// AuditProof is the verified L4 projection.
type AuditProof struct {
	LogID          transparencydomain.LogID
	TreeSize       uint64
	RootHash       [sha256.Size]byte
	FinalSequence  uint64
	CheckpointHash [sha256.Size]byte
	PendingAnchor  bool
	ProofBytes     uint64
}

// Resolution is the complete current-state answer. Sync-object ordering
// is intentionally absent and therefore cannot select CurrentVersion.
type Resolution struct {
	State          credentialdomain.StateDescriptorPayload
	Principal      Principal
	Authorization  Authorization
	CurrentVersion uint64
	Audit          AuditProof
	ProofDigest    [sha256.Size]byte
	Verdict        protocol.Verdict
	Layers         [5]LayerResult
}

// VerifiedIdentity carries parsed, signature-verified objects between L1-L3.
type VerifiedIdentity struct {
	Principal  Principal
	Credential *operationdomain.SignedDeviceOperationCredential
	Event      *operationdomain.SignedEvent
	Descriptor *credentialdomain.SignedStateDescriptor
}
