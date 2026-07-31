// Package application composes receiver-owned trust state with the pure VDNS
// verification rules.
package application

import (
	"crypto/ed25519"
	"crypto/sha256"
	"errors"

	anchordomain "vdns.local/vdns/internal/anchor/domain"
	credentialdomain "vdns.local/vdns/internal/credential/domain"
	"vdns.local/vdns/internal/cryptokit"
	finalorderdomain "vdns.local/vdns/internal/finalorder/domain"
	operationdomain "vdns.local/vdns/internal/operation/domain"
	"vdns.local/vdns/internal/protocol"
	resolverdomain "vdns.local/vdns/internal/resolver/domain"
	transparencydomain "vdns.local/vdns/internal/transparency/domain"
)

var ErrVerificationRejected = errors.New("VDNS verification rejected")

// L1Input contains untrusted bytes plus receiver-owned root context.
type L1Input struct {
	ChainID                   string
	NamespaceID               protocol.NamespaceID
	RootPublicKey             ed25519.PublicKey
	RootKeyGeneration         uint64
	DeviceCredentialSigInput  []byte
	DeviceCredentialSignature protocol.Signature
	EventSigInput             []byte
	EventSignature            protocol.Signature
	DescriptorSigInput        []byte
	DescriptorSignature       protocol.Signature
}

// VerifyL1 verifies the root-authorized device credential, then uses only its
// embedded device key and generation to verify the event and descriptor.
func VerifyL1(input L1Input) (resolverdomain.VerifiedIdentity, resolverdomain.LayerResult, error) {
	fail := func(code resolverdomain.ReasonCode) (
		resolverdomain.VerifiedIdentity, resolverdomain.LayerResult, error,
	) {
		return resolverdomain.VerifiedIdentity{},
			resolverdomain.LayerResult{Layer: resolverdomain.LayerIdentity, Code: code},
			ErrVerificationRejected
	}
	if len(input.RootPublicKey) != ed25519.PublicKeySize || input.RootKeyGeneration == 0 {
		return fail(resolverdomain.CodeIdentityRootChain)
	}
	rootKeyID, err := protocol.KeyIDFromPublicKey(input.RootPublicKey)
	if err != nil {
		return fail(resolverdomain.CodeIdentityRootChain)
	}
	credential, err := operationdomain.ParseAndVerifyDeviceOperationCredential(
		input.DeviceCredentialSigInput, input.DeviceCredentialSignature,
		input.RootPublicKey,
		protocol.VerificationContext{
			ObjectType: protocol.ObjectTypeDeviceCredential,
			ChainID:    input.ChainID, NamespaceID: input.NamespaceID,
			KeyID: rootKeyID, KeyGeneration: input.RootKeyGeneration,
		},
	)
	if err != nil {
		return fail(resolverdomain.CodeIdentityRootChain)
	}
	credentialPayload := credential.Payload()
	if credentialPayload.NamespaceID != input.NamespaceID {
		return fail(resolverdomain.CodeIdentityNamespace)
	}
	devicePublicKey := ed25519.PublicKey(
		append([]byte(nil), credentialPayload.AuthPublicKey[:]...),
	)
	deviceKeyID, err := protocol.KeyIDFromPublicKey(devicePublicKey)
	if err != nil {
		return fail(resolverdomain.CodeIdentitySignature)
	}
	event, err := operationdomain.ParseAndVerify(
		input.EventSigInput, input.EventSignature, devicePublicKey,
		protocol.VerificationContext{
			ObjectType: protocol.ObjectTypeOperationEvent,
			ChainID:    input.ChainID, NamespaceID: input.NamespaceID,
			KeyID: deviceKeyID, KeyGeneration: credentialPayload.SecretGeneration,
		},
	)
	if err != nil {
		return fail(signatureCode(err))
	}
	descriptor, err := credentialdomain.ParseAndVerifyStateDescriptor(
		input.DescriptorSigInput, input.DescriptorSignature, devicePublicKey,
		protocol.VerificationContext{
			ObjectType: protocol.ObjectTypeStateDescriptor,
			ChainID:    input.ChainID, NamespaceID: input.NamespaceID,
			KeyID: deviceKeyID, KeyGeneration: credentialPayload.SecretGeneration,
		},
	)
	if err != nil {
		return fail(signatureCode(err))
	}
	eventPayload := event.Payload()
	descriptorPayload := descriptor.Payload()
	if eventPayload.NamespaceID != input.NamespaceID ||
		descriptorPayload.NamespaceID != input.NamespaceID {
		return fail(resolverdomain.CodeIdentityNamespace)
	}
	if eventPayload.DeviceID != credentialPayload.DeviceID ||
		descriptorPayload.UpdaterDeviceID != credentialPayload.DeviceID ||
		eventPayload.DeviceCredentialHash != credential.Digest() {
		return fail(resolverdomain.CodeIdentitySignature)
	}
	identity := resolverdomain.VerifiedIdentity{
		Principal: resolverdomain.Principal{
			NamespaceID:          input.NamespaceID,
			DeviceID:             credentialPayload.DeviceID,
			DeviceCredentialHash: credential.Digest(),
			SecretGeneration:     credentialPayload.SecretGeneration,
		},
		Credential: credential, Event: event, Descriptor: descriptor,
	}
	return identity, resolverdomain.LayerResult{
		Layer: resolverdomain.LayerIdentity, Passed: true, Code: resolverdomain.CodeOK,
	}, nil
}

func signatureCode(err error) resolverdomain.ReasonCode {
	if code, ok := protocol.CodeOf(err); ok && code == protocol.CodeContextMismatch {
		return resolverdomain.CodeIdentityKeyGeneration
	}
	return resolverdomain.CodeIdentitySignature
}

type L2Input struct {
	Identity               resolverdomain.VerifiedIdentity
	Operation              protocol.OperationType
	CredentialID           *protocol.CredentialID
	OriginBinding          *[cryptokit.OriginBindingSize]byte
	FinalSequence          uint64
	CurrentIssuanceCounter uint64
	CurrentStatusReference [sha256.Size]byte
}

// VerifyL2 evaluates only root-signed static authorization plus the receiver's
// current issuance/status references. Revocation and generation belong to L3.
func VerifyL2(input L2Input) (resolverdomain.Authorization, resolverdomain.LayerResult, error) {
	fail := func(code resolverdomain.ReasonCode) (
		resolverdomain.Authorization, resolverdomain.LayerResult, error,
	) {
		return resolverdomain.Authorization{},
			resolverdomain.LayerResult{Layer: resolverdomain.LayerCapability, Code: code},
			ErrVerificationRejected
	}
	if input.Identity.Credential == nil || input.Identity.Event == nil ||
		!input.Operation.Valid() || input.FinalSequence == 0 {
		return fail(resolverdomain.CodeCapabilityOperation)
	}
	payload := input.Identity.Credential.Payload()
	event := input.Identity.Event.Payload()
	if event.OperationType != input.Operation {
		return fail(resolverdomain.CodeCapabilityOperation)
	}
	if !sameOptionalCredentialID(event.CredentialID, input.CredentialID) {
		return fail(resolverdomain.CodeCapabilityScope)
	}
	required, err := input.Operation.RequiredCapability()
	if err != nil || !payload.Capabilities.Allows(required) {
		return fail(resolverdomain.CodeCapabilityOperation)
	}
	if !payload.Scope.Allows(input.CredentialID, input.OriginBinding) {
		return fail(resolverdomain.CodeCapabilityScope)
	}
	if input.FinalSequence < payload.ValidFromSequence ||
		input.FinalSequence > payload.ValidUntilSequence {
		return fail(resolverdomain.CodeCapabilitySequence)
	}
	if input.CurrentIssuanceCounter == 0 ||
		payload.IssuanceCounter != input.CurrentIssuanceCounter {
		return fail(resolverdomain.CodeCapabilityCounter)
	}
	if hashZero(input.CurrentStatusReference[:]) ||
		payload.StatusReference != input.CurrentStatusReference {
		return fail(resolverdomain.CodeCapabilityStatus)
	}
	return resolverdomain.Authorization{
			Operation: input.Operation, Capabilities: payload.Capabilities,
			ScopeDigest: payload.ScopeDigest, FinalSequence: input.FinalSequence,
			IssuanceCounter: payload.IssuanceCounter,
		}, resolverdomain.LayerResult{
			Layer: resolverdomain.LayerCapability, Passed: true, Code: resolverdomain.CodeOK,
		}, nil
}

// TrustedDynamicState is loaded from locally accepted VDNS state, never from
// the candidate event or cloud response.
type TrustedDynamicState struct {
	CurrentSecretGeneration uint64
	RevokedAtSequence       *uint64
	AcceptedDeviceCounter   uint64
	PreviousEventHash       *[sha256.Size]byte
	AcceptedVersion         uint64
	AcceptedDescriptorHash  *[sha256.Size]byte
	AcceptedLifecycle       *protocol.LifecycleStatus
	CandidateFinalSequence  uint64
	ConflictDetected        bool
	FinalOrder              FinalOrderTrust
}

// FinalOrderTrust binds the descriptor sequence to a receipt from the
// receiver-trusted research authority. Required=false is retained only for
// migration tests and pre-Stage-2 stored objects.
type FinalOrderTrust struct {
	Required               bool
	Receipt                *finalorderdomain.FinalOrderReceipt
	AuthorityPublicKey     ed25519.PublicKey
	AuthorityKeyID         [sha256.Size]byte
	AuthorityKeyGeneration uint64
	OrderedObjectDigest    [sha256.Size]byte
}

func VerifyL3(
	identity resolverdomain.VerifiedIdentity,
	trusted TrustedDynamicState,
) (resolverdomain.LayerResult, error) {
	fail := func(code resolverdomain.ReasonCode) (resolverdomain.LayerResult, error) {
		return resolverdomain.LayerResult{Layer: resolverdomain.LayerDynamicState, Code: code},
			ErrVerificationRejected
	}
	if identity.Credential == nil || identity.Event == nil || identity.Descriptor == nil ||
		trusted.CurrentSecretGeneration == 0 || trusted.CandidateFinalSequence == 0 {
		return fail(resolverdomain.CodeStatePredecessor)
	}
	credential := identity.Credential.Payload()
	event := identity.Event.Payload()
	descriptor := identity.Descriptor.Payload()
	if trusted.ConflictDetected ||
		descriptor.LifecycleStatus == protocol.LifecycleConflicted {
		return fail(resolverdomain.CodeStateConflict)
	}
	if trusted.FinalOrder.Required || trusted.FinalOrder.Receipt != nil {
		if !validFinalOrderReceipt(identity, trusted) {
			return fail(resolverdomain.CodeStateFinalOrder)
		}
	}
	if trusted.RevokedAtSequence != nil &&
		trusted.CandidateFinalSequence >= *trusted.RevokedAtSequence {
		return fail(resolverdomain.CodeStateRevoked)
	}
	if credential.SecretGeneration != trusted.CurrentSecretGeneration ||
		event.SecretGeneration != trusted.CurrentSecretGeneration {
		return fail(resolverdomain.CodeStateRevoked)
	}
	if event.DeviceCounter != trusted.AcceptedDeviceCounter+1 {
		return fail(resolverdomain.CodeStateCounter)
	}
	if !sameOptionalHash(event.PreviousEventHash, trusted.PreviousEventHash) {
		return fail(resolverdomain.CodeStatePredecessor)
	}
	if descriptor.LastOperationEvent != identity.Event.Digest() ||
		descriptor.FinalSequence != trusted.CandidateFinalSequence {
		return fail(resolverdomain.CodeStatePredecessor)
	}
	if event.CredentialID == nil ||
		*event.CredentialID != descriptor.CredentialID ||
		!eventVersionAllows(event, trusted.AcceptedVersion) {
		return fail(resolverdomain.CodeStateVersion)
	}
	if descriptor.ActiveVersion < trusted.AcceptedVersion ||
		descriptor.ActiveVersion > trusted.AcceptedVersion+1 {
		return fail(resolverdomain.CodeStateVersion)
	}
	if trusted.AcceptedVersion == 0 {
		if event.OperationType != protocol.OperationCreate ||
			descriptor.ActiveVersion != 1 || descriptor.PreviousDescriptorHash != nil ||
			descriptor.LifecycleStatus != protocol.LifecycleActive {
			return fail(resolverdomain.CodeStateVersion)
		}
	} else {
		if trusted.AcceptedDescriptorHash == nil ||
			descriptor.PreviousDescriptorHash == nil ||
			*descriptor.PreviousDescriptorHash != *trusted.AcceptedDescriptorHash {
			return fail(resolverdomain.CodeStatePredecessor)
		}
		if trusted.AcceptedLifecycle == nil ||
			!lifecycleAllows(
				*trusted.AcceptedLifecycle, descriptor.LifecycleStatus,
				trusted.AcceptedVersion, descriptor.ActiveVersion,
			) {
			return fail(resolverdomain.CodeStateLifecycle)
		}
		if descriptor.ActiveVersion == trusted.AcceptedVersion &&
			identity.Descriptor.Digest() == *trusted.AcceptedDescriptorHash {
			return fail(resolverdomain.CodeStateConflict)
		}
	}
	return resolverdomain.LayerResult{
		Layer: resolverdomain.LayerDynamicState, Passed: true, Code: resolverdomain.CodeOK,
	}, nil
}

func validFinalOrderReceipt(
	identity resolverdomain.VerifiedIdentity,
	trusted TrustedDynamicState,
) bool {
	order := trusted.FinalOrder
	if order.Receipt == nil ||
		len(order.AuthorityPublicKey) != ed25519.PublicKeySize ||
		hashZero(order.AuthorityKeyID[:]) ||
		order.AuthorityKeyGeneration == 0 ||
		hashZero(order.OrderedObjectDigest[:]) ||
		finalorderdomain.VerifyReceipt(*order.Receipt, order.AuthorityPublicKey) != nil {
		return false
	}
	payload := order.Receipt.Payload
	descriptor := identity.Descriptor.Payload()
	return payload.NamespaceID == descriptor.NamespaceID &&
		payload.CredentialID == descriptor.CredentialID &&
		payload.OrderedObjectDigest == order.OrderedObjectDigest &&
		payload.FinalSequence == trusted.CandidateFinalSequence &&
		payload.AuthorityKeyID == order.AuthorityKeyID &&
		payload.AuthorityKeyGeneration == order.AuthorityKeyGeneration
}

func lifecycleAllows(
	current, candidate protocol.LifecycleStatus,
	currentVersion, candidateVersion uint64,
) bool {
	switch current {
	case protocol.LifecycleActive:
		return candidateVersion == currentVersion &&
			(candidate == protocol.LifecycleActive ||
				candidate == protocol.LifecycleUpdatePending ||
				candidate == protocol.LifecycleSuspended ||
				candidate == protocol.LifecycleConflicted)
	case protocol.LifecycleUpdatePending:
		return candidateVersion == currentVersion &&
			(candidate == protocol.LifecycleSiteConfirmPending ||
				candidate == protocol.LifecycleConflicted)
	case protocol.LifecycleSiteConfirmPending:
		return (candidate == protocol.LifecycleActive &&
			candidateVersion == currentVersion+1) ||
			(candidate == protocol.LifecycleConflicted &&
				candidateVersion == currentVersion)
	case protocol.LifecycleSuspended:
		return candidate == protocol.LifecycleRevoked &&
			candidateVersion == currentVersion
	case protocol.LifecycleConflicted:
		return candidate == protocol.LifecycleActive &&
			candidateVersion >= currentVersion &&
			candidateVersion <= currentVersion+1
	default:
		return false
	}
}

func eventVersionAllows(event operationdomain.Payload, acceptedVersion uint64) bool {
	switch event.OperationType {
	case protocol.OperationCreate:
		return acceptedVersion == 0 && event.OldVersion == nil &&
			event.NewVersion != nil && *event.NewVersion == 1
	case protocol.OperationUpdatePrepare, protocol.OperationUpdateConfirm,
		protocol.OperationRotate, protocol.OperationMigrate,
		protocol.OperationRemediationCommit:
		return acceptedVersion > 0 &&
			event.OldVersion != nil && *event.OldVersion == acceptedVersion &&
			event.NewVersion != nil && *event.NewVersion == acceptedVersion+1
	default:
		if event.NewVersion != nil {
			return false
		}
		return event.OldVersion == nil ||
			(acceptedVersion > 0 && *event.OldVersion == acceptedVersion)
	}
}

type L4Trust struct {
	ChainID                            string
	NamespaceID                        protocol.NamespaceID
	BundlePublicKey                    ed25519.PublicKey
	BundleKeyGeneration                uint64
	CheckpointPublicKey                ed25519.PublicKey
	CheckpointKeyGeneration            uint64
	LogPublicKey                       ed25519.PublicKey
	LogKeyGeneration                   uint64
	TrustedCheckpointDigest            [sha256.Size]byte
	RequiredProviderKind               anchordomain.ProviderKind
	RequireCandidateAnchor             bool
	ExpectedSubjectDigest              [sha256.Size]byte
	ExpectedFinalSequence              uint64
	ExpectedRootChainDigest            [sha256.Size]byte
	ExpectedDeviceCredentialObjectHash [sha256.Size]byte
}

func VerifyL4(
	bundleSigInput []byte,
	bundleSignature protocol.Signature,
	trust L4Trust,
) (resolverdomain.AuditProof, *transparencydomain.SignedProofBundle, resolverdomain.LayerResult, error) {
	fail := func(code resolverdomain.ReasonCode) (
		resolverdomain.AuditProof, *transparencydomain.SignedProofBundle,
		resolverdomain.LayerResult, error,
	) {
		return resolverdomain.AuditProof{}, nil,
			resolverdomain.LayerResult{Layer: resolverdomain.LayerTransparency, Code: code},
			ErrVerificationRejected
	}
	bundleKeyID, err := protocol.KeyIDFromPublicKey(trust.BundlePublicKey)
	if err != nil {
		return fail(resolverdomain.CodeProofBundle)
	}
	bundle, err := transparencydomain.ParseAndVerifyProofBundle(
		bundleSigInput, bundleSignature, trust.BundlePublicKey,
		protocol.VerificationContext{
			ObjectType: protocol.ObjectTypeProofBundle,
			ChainID:    trust.ChainID, NamespaceID: trust.NamespaceID,
			KeyID: bundleKeyID, KeyGeneration: trust.BundleKeyGeneration,
		},
	)
	if err != nil {
		return fail(resolverdomain.CodeProofBundle)
	}
	payload := bundle.Payload()
	if hashZero(trust.ExpectedSubjectDigest[:]) ||
		trust.ExpectedFinalSequence == 0 ||
		hashZero(trust.ExpectedRootChainDigest[:]) ||
		hashZero(trust.ExpectedDeviceCredentialObjectHash[:]) ||
		payload.SubjectDigest != trust.ExpectedSubjectDigest ||
		payload.StateDescriptorDigest != trust.ExpectedSubjectDigest ||
		payload.Leaf.ObjectType != protocol.ObjectTypeStateDescriptor {
		return fail(resolverdomain.CodeProofBundle)
	}
	rootChainDigest, err := transparencydomain.RootChainDigest(payload.RootChainObjects)
	if err != nil || rootChainDigest != trust.ExpectedRootChainDigest ||
		sha256.Sum256(payload.DeviceCredentialObject) !=
			trust.ExpectedDeviceCredentialObjectHash {
		return fail(resolverdomain.CodeProofBundle)
	}
	checkpointKeyID, err := protocol.KeyIDFromPublicKey(trust.CheckpointPublicKey)
	if err != nil {
		return fail(resolverdomain.CodeProofAnchor)
	}
	checkpoint, err := anchordomain.ParseAndVerifyCheckpointObject(
		payload.StartingCheckpointObject, trust.CheckpointPublicKey,
		protocol.VerificationContext{
			ObjectType: protocol.ObjectTypeCheckpoint,
			ChainID:    trust.ChainID, NamespaceID: trust.NamespaceID,
			KeyID: checkpointKeyID, KeyGeneration: trust.CheckpointKeyGeneration,
		},
	)
	if err != nil || checkpoint.Digest() != trust.TrustedCheckpointDigest {
		return fail(resolverdomain.CodeProofAnchor)
	}
	checkpointPayload := checkpoint.Payload()
	if trust.RequiredProviderKind.Valid() &&
		checkpointPayload.ProviderKind != trust.RequiredProviderKind {
		return fail(resolverdomain.CodeProofAnchor)
	}
	logKeyID, err := protocol.KeyIDFromPublicKey(trust.LogPublicKey)
	if err != nil {
		return fail(resolverdomain.CodeProofTreeHead)
	}
	head, err := transparencydomain.ParseAndVerifyTreeHeadObject(
		payload.CandidateTreeHeadObject, trust.LogPublicKey,
		protocol.VerificationContext{
			ObjectType: protocol.ObjectTypeSignedTreeHead,
			ChainID:    trust.ChainID, NamespaceID: trust.NamespaceID,
			KeyID: logKeyID, KeyGeneration: trust.LogKeyGeneration,
		},
	)
	if err != nil {
		return fail(resolverdomain.CodeProofTreeHead)
	}
	headPayload := head.Payload()
	if headPayload.TreeSize < checkpointPayload.CheckpointHeight ||
		headPayload.FinalSequence < checkpointPayload.FinalSequence {
		return fail(resolverdomain.CodeProofTreeHead)
	}
	if payload.Leaf.FinalSequence != trust.ExpectedFinalSequence ||
		headPayload.FinalSequence < trust.ExpectedFinalSequence {
		return fail(resolverdomain.CodeProofTreeHead)
	}
	leafHash, err := transparencydomain.LeafHash(payload.Leaf)
	if err != nil || transparencydomain.VerifyInclusion(
		leafHash, payload.LeafIndex, headPayload.TreeSize,
		payload.InclusionProof, headPayload.RootHash,
	) != nil {
		return fail(resolverdomain.CodeProofInclusion)
	}
	if transparencydomain.VerifyConsistency(
		checkpointPayload.CheckpointHeight, headPayload.TreeSize,
		checkpointPayload.AuditLogRoot, headPayload.RootHash,
		payload.ConsistencyProof,
	) != nil {
		return fail(resolverdomain.CodeProofConsistency)
	}
	pendingAnchor := checkpointPayload.CheckpointHeight != headPayload.TreeSize ||
		checkpointPayload.AuditLogRoot != headPayload.RootHash
	if trust.RequireCandidateAnchor && pendingAnchor {
		return fail(resolverdomain.CodeProofAnchor)
	}
	proofBytes := uint64(
		len(bundleSigInput) + len(payload.StartingCheckpointObject) +
			len(payload.CandidateTreeHeadObject) + ed25519.SignatureSize,
	)
	return resolverdomain.AuditProof{
			LogID: headPayload.LogID, TreeSize: headPayload.TreeSize,
			RootHash: headPayload.RootHash, FinalSequence: headPayload.FinalSequence,
			CheckpointHash: checkpoint.Digest(), PendingAnchor: pendingAnchor,
			ProofBytes: proofBytes,
		}, bundle, resolverdomain.LayerResult{
			Layer: resolverdomain.LayerTransparency, Passed: true, Code: resolverdomain.CodeOK,
		}, nil
}

type PolicyInput struct {
	Operation          protocol.OperationType
	NetworkAvailable   bool
	L4Available        bool
	PendingAnchor      bool
	HasAcceptedCache   bool
	CacheAgeSequences  uint64
	MaxOfflineCacheAge uint64
	UserReviewRequired bool
}

// EvaluateL5 applies the frozen low-risk/high-risk degradation matrix.
func EvaluateL5(input PolicyInput) (protocol.Verdict, resolverdomain.LayerResult) {
	result := resolverdomain.LayerResult{Layer: resolverdomain.LayerLocalPolicy}
	if input.UserReviewRequired {
		result.Code = resolverdomain.CodePolicyUserReview
		return protocol.VerdictReviewRequired, result
	}
	lowRisk := input.Operation == protocol.OperationResolve ||
		input.Operation == protocol.OperationAutofill ||
		input.Operation == protocol.OperationSyncAccept
	if input.L4Available && input.NetworkAvailable && !input.PendingAnchor {
		result.Passed, result.Code = true, resolverdomain.CodeOK
		return protocol.VerdictAccept, result
	}
	if !lowRisk {
		result.Code = resolverdomain.CodePolicyHighRisk
		return protocol.VerdictRejectPolicy, result
	}
	if !input.HasAcceptedCache ||
		input.MaxOfflineCacheAge == 0 ||
		input.CacheAgeSequences > input.MaxOfflineCacheAge {
		result.Code = resolverdomain.CodePolicyCacheExpired
		return protocol.VerdictRejectPolicy, result
	}
	result.Passed = true
	if !input.NetworkAvailable || !input.L4Available {
		result.Code = resolverdomain.CodePolicyOffline
		return protocol.VerdictDegradedOffline, result
	}
	result.Code = resolverdomain.CodePolicyPendingLog
	return protocol.VerdictDegradedPendingLog, result
}

func sameOptionalHash(left, right *[sha256.Size]byte) bool {
	if left == nil || right == nil {
		return left == nil && right == nil
	}
	return *left == *right
}

func sameOptionalCredentialID(
	left, right *protocol.CredentialID,
) bool {
	if left == nil || right == nil {
		return left == nil && right == nil
	}
	return *left == *right
}

func hashZero(value []byte) bool {
	var combined byte
	for _, item := range value {
		combined |= item
	}
	return combined == 0
}
