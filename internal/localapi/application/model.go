// Package application implements the authenticated local-localClient use cases.
// DTOs in this package mirror the frozen /api/v2 OpenAPI contract. Secret
// values are represented only by one-use handles.
package application

import "time"

type Fault struct {
	Code    string
	Message string
	Details map[string]any
}

func (fault *Fault) Error() string {
	if fault == nil {
		return ""
	}
	return fault.Code
}

func NewFault(code, message string) *Fault {
	return &Fault{Code: code, Message: message}
}

type CreateVaultSessionRequest struct {
	DeviceID             string `json:"deviceId"`
	MasterPasswordHandle string `json:"masterPasswordHandle"`
}

type VaultSession struct {
	SessionID string    `json:"sessionId"`
	DeviceID  string    `json:"deviceId"`
	State     string    `json:"state"`
	ExpiresAt time.Time `json:"expiresAt"`
}

type PasswordGenerationRequest struct {
	Origin        string `json:"origin"`
	AccountID     string `json:"accountId"`
	PolicyVersion uint64 `json:"policyVersion"`
	Length        int    `json:"length,omitempty"`
}

type SecretHandle struct {
	SecretHandle string    `json:"secretHandle"`
	FieldType    string    `json:"fieldType"`
	SingleUse    bool      `json:"singleUse"`
	ExpiresAt    time.Time `json:"expiresAt"`
}

type RouteResolutionRequest struct {
	Origin    string `json:"origin"`
	AccountID string `json:"accountId,omitempty"`
	TopFrame  *bool  `json:"topFrame,omitempty"`
}

type RouteResolution struct {
	CredentialID   string `json:"credentialId"`
	AccountLabel   string `json:"accountLabel"`
	OriginVerified bool   `json:"originVerified"`
}

type CreateCredentialRequest struct {
	Origin              string `json:"origin"`
	AccountID           string `json:"accountId"`
	UsernameHandle      string `json:"usernameHandle"`
	PasswordHandle      string `json:"passwordHandle"`
	TOTPHandle          string `json:"totpHandle,omitempty"`
	RecoveryCodesHandle string `json:"recoveryCodesHandle,omitempty"`
	NotesHandle         string `json:"notesHandle,omitempty"`
	CryptoPolicyHash    string `json:"cryptoPolicyHash"`
}

type Credential struct {
	CredentialID    string `json:"credentialId"`
	AccountLabel    string `json:"accountLabel,omitempty"`
	ActiveVersion   uint64 `json:"activeVersion"`
	LifecycleStatus string `json:"lifecycleStatus"`
	Verdict         string `json:"verdict"`
	DescriptorHash  string `json:"descriptorHash"`
}

type CredentialPage struct {
	Items      []Credential `json:"items"`
	NextCursor string       `json:"nextCursor,omitempty"`
}

type AutofillAuthorizationRequest struct {
	Origin                  string `json:"origin"`
	FieldType               string `json:"fieldType"`
	ExpectedVersion         uint64 `json:"expectedVersion"`
	AllowCachedDegradedRead bool   `json:"allowCachedDegradedRead,omitempty"`
}

type AutofillAuthorization struct {
	SecretHandle
	CredentialID      string `json:"credentialId"`
	CredentialVersion uint64 `json:"credentialVersion"`
	Verdict           string `json:"verdict"`
	OriginVerified    bool   `json:"originVerified"`
}

type FieldUpdate struct {
	FieldType    string `json:"fieldType"`
	SecretHandle string `json:"secretHandle"`
}

type CreateVersionRequest struct {
	ExpectedVersion        uint64        `json:"expectedVersion"`
	PreviousDescriptorHash string        `json:"previousDescriptorHash"`
	FieldUpdates           []FieldUpdate `json:"fieldUpdates"`
}

type CredentialVersion struct {
	CredentialID   string `json:"credentialId"`
	Version        uint64 `json:"version"`
	State          string `json:"state"`
	DescriptorHash string `json:"descriptorHash"`
	EvidenceLevel  string `json:"evidenceLevel,omitempty"`
}

type CredentialVersionPage struct {
	Items      []CredentialVersion `json:"items"`
	NextCursor string              `json:"nextCursor,omitempty"`
}

type SiteConfirmationRequest struct {
	ExpectedVersion  uint64 `json:"expectedVersion"`
	CandidateVersion uint64 `json:"candidateVersion"`
	Outcome          string `json:"outcome"`
	EvidenceLevel    string `json:"evidenceLevel"`
	ReceiptDigest    string `json:"receiptDigest,omitempty"`
}

type SyncPublicationRequest struct {
	BaseCheckpointHash string `json:"baseCheckpointHash"`
	MaxObjects         int    `json:"maxObjects,omitempty"`
}

type SyncPullRequest struct {
	TrustedCheckpointHash string `json:"trustedCheckpointHash"`
	Cursor                string `json:"cursor,omitempty"`
	Limit                 int    `json:"limit,omitempty"`
}

type DeviceEnrollmentRequest struct {
	ChallengeID           string   `json:"challengeId"`
	NewDeviceID           string   `json:"newDeviceId"`
	AuthPublicKey         string   `json:"authPublicKey"`
	HPKEPublicKey         string   `json:"hpkePublicKey"`
	RequestedCapabilities []string `json:"requestedCapabilities"`
	ShortCodeConfirmed    bool     `json:"shortCodeConfirmed"`
}

type DeviceRevocationRequest struct {
	DeviceID                string `json:"deviceId"`
	Reason                  string `json:"reason"`
	ExpectedIssuanceCounter uint64 `json:"expectedIssuanceCounter"`
}

type RecoverySessionRequest struct {
	NamespaceID          string `json:"namespaceId"`
	NewDeviceID          string `json:"newDeviceId"`
	RecoverySecretHandle string `json:"recoverySecretHandle"`
}

type StateResolutionRequest struct {
	CredentialID            string `json:"credentialId"`
	Operation               string `json:"operation"`
	TrustedCheckpointHash   string `json:"trustedCheckpointHash"`
	AllowCachedDegradedRead bool   `json:"allowCachedDegradedRead,omitempty"`
}

type LayerResults struct {
	L1 string `json:"l1"`
	L2 string `json:"l2"`
	L3 string `json:"l3"`
	L4 string `json:"l4"`
	L5 string `json:"l5"`
}

type StateResolution struct {
	ResolutionID       string       `json:"resolutionId"`
	CredentialID       string       `json:"credentialId"`
	ActiveVersion      uint64       `json:"activeVersion"`
	ActiveEnvelopeHash string       `json:"activeEnvelopeHash"`
	DescriptorHash     string       `json:"descriptorHash"`
	Verdict            string       `json:"verdict"`
	LayerResults       LayerResults `json:"layerResults"`
	ProofBundleDigest  string       `json:"proofBundleDigest,omitempty"`
}

type AuditEventRequest struct {
	CredentialID           string `json:"credentialId"`
	EvidenceLevel          string `json:"evidenceLevel"`
	EncryptedPayloadDigest string `json:"encryptedPayloadDigest"`
	Epoch                  uint64 `json:"epoch"`
}

type SecurityAnalysisRequest struct {
	AnalysisTypes        []string   `json:"analysisTypes"`
	SourceCheckpointHash string     `json:"sourceCheckpointHash"`
	WindowStart          *time.Time `json:"windowStart,omitempty"`
	WindowEnd            *time.Time `json:"windowEnd,omitempty"`
}

// SecurityFinding is a minimized local UI projection. Credential, device,
// password, secret-handle and reuse-tag values are intentionally absent.
type SecurityFinding struct {
	Kind                  string   `json:"kind"`
	CredentialPseudonym   string   `json:"credentialPseudonym"`
	Confidence            string   `json:"confidence"`
	EvidenceObjectDigests []string `json:"evidenceObjectDigests"`
	ObservedTimeBucket    uint64   `json:"observedTimeBucket"`
	CurrentVersion        uint64   `json:"currentVersion"`
}

type SecurityFindingPage struct {
	Items      []SecurityFinding `json:"items"`
	NextCursor string            `json:"nextCursor,omitempty"`
}

type OperationStatus struct {
	OperationID     string `json:"operationId"`
	State           string `json:"state"`
	ResultReference string `json:"resultReference,omitempty"`
	Error           any    `json:"error,omitempty"`
}
