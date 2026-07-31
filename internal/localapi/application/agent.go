package application

import (
	"crypto/hmac"
	"crypto/rand"
	"crypto/sha256"
	"crypto/subtle"
	"encoding/base64"
	"errors"
	"io"
	"sort"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/google/uuid"

	credentialdomain "vdns.local/vdns/internal/credential/domain"
	"vdns.local/vdns/internal/cryptokit"
	passworddomain "vdns.local/vdns/internal/password/domain"
	"vdns.local/vdns/internal/protocol"
)

const (
	defaultHandleTTL       = 45 * time.Second
	defaultSessionIdle     = 10 * time.Minute
	defaultSessionAbsolute = 30 * time.Minute
)

type Config struct {
	UnlockVerifier         func(deviceID string, secret *cryptokit.Secret) error
	RecoveryVerifier       func(namespaceID, deviceID string, secret *cryptokit.Secret) error
	Now                    func() time.Time
	SessionIdleTimeout     time.Duration
	SessionAbsoluteTimeout time.Duration
	AllowStrictRelogin     bool
	TrustedSiteConnector   bool
	// VDNSResolver is the composition boundary for the real L1-L5 verifier.
	// Leaving it nil is an explicit unavailable capability; the local reference
	// agent must never synthesize successful layer results.
	VDNSResolver func(VDNSResolutionRequest) (VDNSResolution, *Fault)
}

type handleBinding struct {
	Purpose   string
	SessionID string
	Origin    string
	AccountID string
	FieldType string
	DeviceID  string
}

type secretEntry struct {
	secret    *cryptokit.Secret
	binding   handleBinding
	expiresAt time.Time
}

type sessionRecord struct {
	id        string
	deviceID  string
	createdAt time.Time
	lastUsed  time.Time
	expiresAt time.Time
}

type versionRecord struct {
	summary       CredentialVersion
	fields        map[string]*cryptokit.Secret
	receiptDigest string
}

type credentialRecord struct {
	summary      Credential
	origin       string
	accountID    string
	envelopeHash string
	versions     map[uint64]*versionRecord
	updatedAt    time.Time
}

type deviceRecord struct {
	issuanceCounter uint64
	revoked         bool
}

// Agent is a deterministic local reference composition for the /api/v2
// adapter. It stores only process-local protected secrets; durable ciphertext
// and transparency remain behind application ports. Full L1-L5 results are
// available only through the explicitly configured VDNSResolver boundary.
type Agent struct {
	mu                  sync.Mutex
	config              Config
	handles             map[string]*secretEntry
	sessions            map[string]*sessionRecord
	credentials         map[string]*credentialRecord
	operations          map[string]OperationStatus
	devices             map[string]*deviceRecord
	pendingAuditHandles map[string]string
	securityResults     map[string][]SecurityFinding
	cursorKey           [sha256.Size]byte
}

func NewAgent(config Config) (*Agent, error) {
	if config.UnlockVerifier == nil {
		return nil, errors.New("master password verifier is required")
	}
	if config.Now == nil {
		config.Now = time.Now
	}
	if config.SessionIdleTimeout <= 0 {
		config.SessionIdleTimeout = defaultSessionIdle
	}
	if config.SessionAbsoluteTimeout <= 0 {
		config.SessionAbsoluteTimeout = defaultSessionAbsolute
	}
	if config.SessionIdleTimeout > config.SessionAbsoluteTimeout {
		return nil, errors.New("invalid session timeouts")
	}
	var key [sha256.Size]byte
	if _, err := io.ReadFull(rand.Reader, key[:]); err != nil {
		return nil, err
	}
	agent := &Agent{
		config: config, handles: make(map[string]*secretEntry),
		sessions:            make(map[string]*sessionRecord),
		credentials:         make(map[string]*credentialRecord),
		operations:          make(map[string]OperationStatus),
		devices:             make(map[string]*deviceRecord),
		pendingAuditHandles: make(map[string]string),
		securityResults:     make(map[string][]SecurityFinding),
	}
	agent.cursorKey = key
	return agent, nil
}

// StageMasterPassword models the secure-input/Native Messaging boundary. It is
// intentionally not exposed as an HTTP endpoint.
func (agent *Agent) StageMasterPassword(deviceID string, secret []byte) (string, error) {
	return agent.stageSecret(secret, handleBinding{Purpose: "MASTER_PASSWORD", DeviceID: deviceID}, defaultHandleTTL)
}

// StageRecoverySecret models high-entropy recovery input outside HTTP.
func (agent *Agent) StageRecoverySecret(namespaceID, deviceID string, secret []byte) (string, error) {
	return agent.stageSecret(secret, handleBinding{
		Purpose: "RECOVERY_SECRET", AccountID: namespaceID, DeviceID: deviceID,
	}, defaultHandleTTL)
}

// StageAuditAnalysisSecret binds a one-use candidate password to the active
// session without placing it in the HTTP request body.
func (agent *Agent) StageAuditAnalysisSecret(sessionID string, secret []byte) (string, error) {
	if _, fault := agent.requireSession(sessionID); fault != nil {
		return "", fault
	}
	handle, err := agent.stageSecret(
		secret, handleBinding{Purpose: "AUDIT_ANALYSIS", SessionID: sessionID},
		defaultHandleTTL,
	)
	if err != nil {
		return "", err
	}
	agent.mu.Lock()
	if previous := agent.pendingAuditHandles[sessionID]; previous != "" && previous != handle {
		if entry := agent.handles[previous]; entry != nil {
			entry.secret.Destroy()
			delete(agent.handles, previous)
		}
	}
	agent.pendingAuditHandles[sessionID] = handle
	agent.mu.Unlock()
	return handle, nil
}

// StageCredentialField models trusted form capture. It never serializes the
// supplied value and binds the resulting handle to session, Origin and account.
func (agent *Agent) StageCredentialField(
	sessionID, origin, accountID, fieldType string,
	secret []byte,
) (string, error) {
	canonical, err := canonicalOrigin(origin)
	if err != nil || accountID == "" || !validFieldType(fieldType) {
		return "", NewFault("VALIDATION_FAILED", "secure input binding is invalid")
	}
	if _, fault := agent.requireSession(sessionID); fault != nil {
		return "", fault
	}
	return agent.stageSecret(secret, handleBinding{
		Purpose: "CREDENTIAL_FIELD", SessionID: sessionID,
		Origin: canonical, AccountID: accountID, FieldType: fieldType,
	}, defaultHandleTTL)
}

// ConsumeNativeHandle gives an explicitly trusted Native Messaging callback a
// temporary plaintext copy. The handle is deleted before the callback runs.
func (agent *Agent) ConsumeNativeHandle(
	sessionID, handleID, origin, fieldType string,
	fn func([]byte) error,
) error {
	canonical, err := canonicalOrigin(origin)
	if err != nil || fn == nil {
		return NewFault("SECRET_HANDLE_REJECTED", "secret handle binding is invalid")
	}
	secret, fault := agent.consumeHandle(handleID, func(binding handleBinding) bool {
		return binding.Purpose == "AUTOFILL_OUTPUT" &&
			binding.SessionID == sessionID && binding.Origin == canonical &&
			binding.FieldType == fieldType
	})
	if fault != nil {
		return fault
	}
	defer secret.Destroy()
	return secret.Use(fn)
}

func (agent *Agent) stageSecret(secret []byte, binding handleBinding, ttl time.Duration) (string, error) {
	if agent == nil || len(secret) == 0 || ttl <= 0 {
		return "", NewFault("VALIDATION_FAILED", "secure input is invalid")
	}
	protected, err := cryptokit.NewSecret(secret)
	if err != nil {
		return "", NewFault("VALIDATION_FAILED", "secure input is invalid")
	}
	id := uuid.NewString()
	agent.mu.Lock()
	defer agent.mu.Unlock()
	agent.purgeExpiredLocked(agent.config.Now())
	agent.handles[id] = &secretEntry{
		secret: protected, binding: binding, expiresAt: agent.config.Now().Add(ttl),
	}
	return id, nil
}

func (agent *Agent) CreateVaultSession(request CreateVaultSessionRequest) (VaultSession, *Fault) {
	if !validIdentifier(request.DeviceID, 16) || uuid.Validate(request.MasterPasswordHandle) != nil {
		return VaultSession{}, NewFault("VALIDATION_FAILED", "vault session request is invalid")
	}
	secret, fault := agent.consumeHandle(request.MasterPasswordHandle, func(binding handleBinding) bool {
		return binding.Purpose == "MASTER_PASSWORD" && binding.DeviceID == request.DeviceID
	})
	if fault != nil {
		return VaultSession{}, NewFault("UNLOCK_REJECTED", "vault unlock was rejected")
	}
	defer secret.Destroy()
	if err := agent.config.UnlockVerifier(request.DeviceID, secret); err != nil {
		return VaultSession{}, NewFault("UNLOCK_REJECTED", "vault unlock was rejected")
	}
	now := agent.config.Now()
	id := uuid.NewString()
	expires := now.Add(agent.config.SessionAbsoluteTimeout)
	agent.mu.Lock()
	agent.sessions[id] = &sessionRecord{
		id: id, deviceID: request.DeviceID, createdAt: now, lastUsed: now, expiresAt: expires,
	}
	if agent.devices[request.DeviceID] == nil {
		agent.devices[request.DeviceID] = &deviceRecord{issuanceCounter: 1}
	}
	agent.mu.Unlock()
	return VaultSession{
		SessionID: id, DeviceID: request.DeviceID, State: "UNLOCKED", ExpiresAt: expires,
	}, nil
}

func (agent *Agent) DeleteVaultSession(sessionID string) *Fault {
	if uuid.Validate(sessionID) != nil {
		return NewFault("RESOURCE_NOT_FOUND", "vault session was not found")
	}
	agent.mu.Lock()
	defer agent.mu.Unlock()
	if agent.sessions[sessionID] == nil {
		return NewFault("RESOURCE_NOT_FOUND", "vault session was not found")
	}
	delete(agent.sessions, sessionID)
	delete(agent.pendingAuditHandles, sessionID)
	for id, entry := range agent.handles {
		if entry.binding.SessionID == sessionID {
			entry.secret.Destroy()
			delete(agent.handles, id)
		}
	}
	return nil
}

func (agent *Agent) GeneratePassword(sessionID string, request PasswordGenerationRequest) (SecretHandle, *Fault) {
	if _, fault := agent.requireSession(sessionID); fault != nil {
		return SecretHandle{}, fault
	}
	canonical, err := canonicalOrigin(request.Origin)
	if err != nil || request.AccountID == "" || len(request.AccountID) > 512 || request.PolicyVersion == 0 {
		return SecretHandle{}, NewFault("VALIDATION_FAILED", "password generation request is invalid")
	}
	policy, err := passworddomain.DefaultPasswordPolicy(request.PolicyVersion)
	if err != nil {
		return SecretHandle{}, NewFault("POLICY_REJECTED", "password policy is invalid")
	}
	generated, err := passworddomain.GeneratePassword(policy, request.Length)
	if err != nil {
		return SecretHandle{}, NewFault("POLICY_REJECTED", "password policy cannot be satisfied")
	}
	id := uuid.NewString()
	expires := agent.config.Now().Add(defaultHandleTTL)
	agent.mu.Lock()
	agent.purgeExpiredLocked(agent.config.Now())
	agent.handles[id] = &secretEntry{
		secret: generated,
		binding: handleBinding{
			Purpose: "CREDENTIAL_FIELD", SessionID: sessionID, Origin: canonical,
			AccountID: request.AccountID, FieldType: "PASSWORD",
		},
		expiresAt: expires,
	}
	agent.mu.Unlock()
	return SecretHandle{SecretHandle: id, FieldType: "PASSWORD", SingleUse: true, ExpiresAt: expires}, nil
}

func (agent *Agent) ResolveRoute(sessionID string, request RouteResolutionRequest) (RouteResolution, *Fault) {
	if _, fault := agent.requireSession(sessionID); fault != nil {
		return RouteResolution{}, fault
	}
	if request.TopFrame != nil && !*request.TopFrame {
		return RouteResolution{}, NewFault("ORIGIN_REJECTED", "autofill is restricted to the top frame")
	}
	canonical, err := canonicalOrigin(request.Origin)
	if err != nil {
		return RouteResolution{}, NewFault("VALIDATION_FAILED", "Origin is invalid")
	}
	agent.mu.Lock()
	defer agent.mu.Unlock()
	var matches []*credentialRecord
	for _, record := range agent.credentials {
		if record.origin == canonical && (request.AccountID == "" || record.accountID == request.AccountID) &&
			record.summary.LifecycleStatus != "REVOKED" {
			matches = append(matches, record)
		}
	}
	if len(matches) == 0 {
		return RouteResolution{}, NewFault("RESOURCE_NOT_FOUND", "credential route was not found")
	}
	if len(matches) > 1 {
		labels := make([]string, 0, len(matches))
		for _, record := range matches {
			labels = append(labels, record.accountID)
		}
		sort.Strings(labels)
		return RouteResolution{}, &Fault{
			Code: "ACCOUNT_SELECTION_REQUIRED", Message: "select an account before autofill",
			Details: map[string]any{"accountLabels": labels},
		}
	}
	record := matches[0]
	return RouteResolution{
		CredentialID: record.summary.CredentialID,
		AccountLabel: record.accountID, OriginVerified: true,
	}, nil
}

func (agent *Agent) CreateCredential(sessionID string, request CreateCredentialRequest) (Credential, *Fault) {
	if _, fault := agent.requireSession(sessionID); fault != nil {
		return Credential{}, fault
	}
	canonical, err := canonicalOrigin(request.Origin)
	if err != nil || request.AccountID == "" || len(request.AccountID) > 512 ||
		!validIdentifier(request.CryptoPolicyHash, 32) {
		return Credential{}, NewFault("VALIDATION_FAILED", "credential request is invalid")
	}
	fieldHandles := map[string]string{
		"USERNAME": request.UsernameHandle, "PASSWORD": request.PasswordHandle,
		"TOTP": request.TOTPHandle, "RECOVERY_CODES": request.RecoveryCodesHandle,
		"NOTE": request.NotesHandle,
	}
	fields := make(map[string]*cryptokit.Secret)
	for field, handle := range fieldHandles {
		if handle == "" {
			continue
		}
		secret, fault := agent.consumeHandle(handle, func(binding handleBinding) bool {
			return binding.Purpose == "CREDENTIAL_FIELD" && binding.SessionID == sessionID &&
				binding.Origin == canonical && binding.AccountID == request.AccountID &&
				binding.FieldType == field
		})
		if fault != nil {
			destroyFields(fields)
			return Credential{}, NewFault("SECRET_HANDLE_REJECTED", "credential handle was rejected")
		}
		fields[field] = secret
	}
	if fields["USERNAME"] == nil || fields["PASSWORD"] == nil {
		destroyFields(fields)
		return Credential{}, NewFault("SECRET_HANDLE_REJECTED", "required credential handles are missing")
	}
	id, err := randomIdentifier(32)
	if err != nil {
		destroyFields(fields)
		return Credential{}, NewFault("INTERNAL_ERROR", "credential could not be created")
	}
	descriptor := digestIdentifier("descriptor", id, "1", request.CryptoPolicyHash)
	envelope := digestIdentifier("envelope", id, descriptor)
	summary := Credential{
		CredentialID: id, AccountLabel: request.AccountID, ActiveVersion: 1,
		LifecycleStatus: "ACTIVE", Verdict: "ACCEPT", DescriptorHash: descriptor,
	}
	version := &versionRecord{summary: CredentialVersion{
		CredentialID: id, Version: 1, State: "ACTIVE", DescriptorHash: descriptor,
	}, fields: fields}
	agent.mu.Lock()
	defer agent.mu.Unlock()
	for _, record := range agent.credentials {
		if record.origin == canonical && record.accountID == request.AccountID &&
			record.summary.LifecycleStatus != "REVOKED" {
			destroyFields(fields)
			return Credential{}, NewFault("LIFECYCLE_CONFLICT", "credential route already exists")
		}
	}
	agent.credentials[id] = &credentialRecord{
		summary: summary, origin: canonical, accountID: request.AccountID,
		envelopeHash: envelope, versions: map[uint64]*versionRecord{1: version},
		updatedAt: agent.config.Now(),
	}
	return summary, nil
}

func (agent *Agent) ListCredentials(sessionID, cursor string, limit int) (CredentialPage, *Fault) {
	session, fault := agent.requireSession(sessionID)
	if fault != nil {
		return CredentialPage{}, fault
	}
	if limit == 0 {
		limit = 50
	}
	if limit < 1 || limit > 200 {
		return CredentialPage{}, NewFault("VALIDATION_FAILED", "limit is outside the allowed range")
	}
	offset, fault := agent.decodeCursor(cursor, session.deviceID, "credentials")
	if fault != nil {
		return CredentialPage{}, fault
	}
	agent.mu.Lock()
	items := make([]Credential, 0, len(agent.credentials))
	for _, record := range agent.credentials {
		items = append(items, record.summary)
	}
	agent.mu.Unlock()
	sort.Slice(items, func(i, j int) bool {
		if items[i].AccountLabel == items[j].AccountLabel {
			return items[i].CredentialID < items[j].CredentialID
		}
		return items[i].AccountLabel < items[j].AccountLabel
	})
	if offset > len(items) {
		return CredentialPage{}, NewFault("CURSOR_REJECTED", "cursor is invalid or expired")
	}
	end := offset + limit
	if end > len(items) {
		end = len(items)
	}
	page := CredentialPage{Items: append([]Credential(nil), items[offset:end]...)}
	if end < len(items) {
		page.NextCursor = agent.encodeCursor(end, session.deviceID, "credentials")
	}
	return page, nil
}

func (agent *Agent) GetCredential(sessionID, credentialID string) (Credential, *Fault) {
	if _, fault := agent.requireSession(sessionID); fault != nil {
		return Credential{}, fault
	}
	if !validIdentifier(credentialID, 32) {
		return Credential{}, NewFault("RESOURCE_NOT_FOUND", "credential was not found")
	}
	agent.mu.Lock()
	defer agent.mu.Unlock()
	record := agent.credentials[credentialID]
	if record == nil {
		return Credential{}, NewFault("RESOURCE_NOT_FOUND", "credential was not found")
	}
	return record.summary, nil
}

func (agent *Agent) AuthorizeAutofill(
	sessionID, credentialID string,
	request AutofillAuthorizationRequest,
) (AutofillAuthorization, *Fault) {
	if _, fault := agent.requireSession(sessionID); fault != nil {
		return AutofillAuthorization{}, fault
	}
	canonical, err := canonicalOrigin(request.Origin)
	if err != nil || !oneOf(request.FieldType, "USERNAME", "PASSWORD", "TOTP") ||
		request.ExpectedVersion == 0 {
		return AutofillAuthorization{}, NewFault("VALIDATION_FAILED", "autofill request is invalid")
	}
	agent.mu.Lock()
	record := agent.credentials[credentialID]
	if record == nil {
		agent.mu.Unlock()
		return AutofillAuthorization{}, NewFault("RESOURCE_NOT_FOUND", "credential was not found")
	}
	if record.origin != canonical {
		agent.mu.Unlock()
		return AutofillAuthorization{}, NewFault("ORIGIN_REJECTED", "Origin verification failed")
	}
	if record.summary.Verdict != "ACCEPT" && !strings.HasPrefix(record.summary.Verdict, "DEGRADED_") {
		agent.mu.Unlock()
		return AutofillAuthorization{}, NewFault("VDNS_REJECTED", "VDNS verification rejected autofill")
	}
	if strings.HasPrefix(record.summary.Verdict, "DEGRADED_") && !request.AllowCachedDegradedRead {
		agent.mu.Unlock()
		return AutofillAuthorization{}, NewFault("PROOF_UNAVAILABLE", "fresh proof is unavailable and degraded read was not allowed")
	}
	if record.summary.ActiveVersion != request.ExpectedVersion {
		agent.mu.Unlock()
		return AutofillAuthorization{}, NewFault("VERSION_CONFLICT", "credential version changed")
	}
	version := record.versions[record.summary.ActiveVersion]
	secret := version.fields[request.FieldType]
	if secret == nil {
		agent.mu.Unlock()
		return AutofillAuthorization{}, NewFault("RESOURCE_NOT_FOUND", "credential field was not found")
	}
	cloned, err := secret.Clone()
	if err != nil {
		agent.mu.Unlock()
		return AutofillAuthorization{}, NewFault("CURRENT_OBJECT_UNAVAILABLE", "credential object is unavailable")
	}
	handleID := uuid.NewString()
	expires := agent.config.Now().Add(defaultHandleTTL)
	agent.handles[handleID] = &secretEntry{
		secret: cloned, expiresAt: expires,
		binding: handleBinding{
			Purpose: "AUTOFILL_OUTPUT", SessionID: sessionID,
			Origin: canonical, FieldType: request.FieldType,
		},
	}
	summary := record.summary
	agent.mu.Unlock()
	return AutofillAuthorization{
		SecretHandle: SecretHandle{
			SecretHandle: handleID, FieldType: request.FieldType,
			SingleUse: true, ExpiresAt: expires,
		},
		CredentialID: credentialID, CredentialVersion: summary.ActiveVersion,
		Verdict: summary.Verdict, OriginVerified: true,
	}, nil
}

// AuthorizeCandidateField is a Native Messaging-only bridge used by the
// password-change assistant after a candidate is durably stored but before
// site confirmation. It never changes ACTIVE and rejects old/unknown versions.
func (agent *Agent) AuthorizeCandidateField(
	sessionID, credentialID string,
	candidateVersion uint64,
	origin, fieldType string,
) (SecretHandle, *Fault) {
	if _, fault := agent.requireSession(sessionID); fault != nil {
		return SecretHandle{}, fault
	}
	canonical, err := canonicalOrigin(origin)
	if err != nil || fieldType != "PASSWORD" || candidateVersion < 2 {
		return SecretHandle{}, NewFault("VALIDATION_FAILED", "candidate field request is invalid")
	}
	agent.mu.Lock()
	defer agent.mu.Unlock()
	record := agent.credentials[credentialID]
	if record == nil {
		return SecretHandle{}, NewFault("RESOURCE_NOT_FOUND", "credential was not found")
	}
	if record.origin != canonical || candidateVersion != record.summary.ActiveVersion+1 {
		return SecretHandle{}, NewFault("ORIGIN_REJECTED", "candidate Origin or version was rejected")
	}
	version := record.versions[candidateVersion]
	if version == nil || !oneOf(
		version.summary.State,
		"CANDIDATE_LOCAL", "SITE_CHANGE_IN_PROGRESS", "SITE_CONFIRM_PENDING", "UNKNOWN",
	) {
		return SecretHandle{}, NewFault("LIFECYCLE_CONFLICT", "candidate is not available for site change")
	}
	secret := version.fields[fieldType]
	if secret == nil {
		return SecretHandle{}, NewFault("RESOURCE_NOT_FOUND", "candidate password is unavailable")
	}
	cloned, err := secret.Clone()
	if err != nil {
		return SecretHandle{}, NewFault("CURRENT_OBJECT_UNAVAILABLE", "candidate object is unavailable")
	}
	id := uuid.NewString()
	expires := agent.config.Now().Add(defaultHandleTTL)
	agent.handles[id] = &secretEntry{
		secret: cloned, expiresAt: expires,
		binding: handleBinding{
			Purpose: "AUTOFILL_OUTPUT", SessionID: sessionID,
			Origin: canonical, FieldType: fieldType,
		},
	}
	return SecretHandle{
		SecretHandle: id, FieldType: fieldType, SingleUse: true, ExpiresAt: expires,
	}, nil
}

func (agent *Agent) CreateVersion(
	sessionID, credentialID string,
	request CreateVersionRequest,
) (CredentialVersion, *Fault) {
	if _, fault := agent.requireSession(sessionID); fault != nil {
		return CredentialVersion{}, fault
	}
	if request.ExpectedVersion == 0 || !validIdentifier(request.PreviousDescriptorHash, 32) ||
		len(request.FieldUpdates) < 1 || len(request.FieldUpdates) > 6 {
		return CredentialVersion{}, NewFault("VALIDATION_FAILED", "version request is invalid")
	}
	agent.mu.Lock()
	record := agent.credentials[credentialID]
	if record == nil {
		agent.mu.Unlock()
		return CredentialVersion{}, NewFault("RESOURCE_NOT_FOUND", "credential was not found")
	}
	if record.summary.ActiveVersion != request.ExpectedVersion {
		agent.mu.Unlock()
		return CredentialVersion{}, NewFault("VERSION_CONFLICT", "active version changed")
	}
	if record.summary.DescriptorHash != request.PreviousDescriptorHash {
		agent.mu.Unlock()
		return CredentialVersion{}, NewFault("DESCRIPTOR_CONFLICT", "descriptor changed")
	}
	base := record.versions[request.ExpectedVersion]
	fields := cloneFields(base.fields)
	origin, account := record.origin, record.accountID
	agent.mu.Unlock()
	if fields == nil {
		return CredentialVersion{}, NewFault("CURRENT_OBJECT_UNAVAILABLE", "active fields are unavailable")
	}
	seen := make(map[string]bool)
	for _, update := range request.FieldUpdates {
		if !oneOf(update.FieldType, "ORIGIN", "USERNAME", "PASSWORD", "TOTP", "RECOVERY_CODES", "NOTE") ||
			seen[update.FieldType] || uuid.Validate(update.SecretHandle) != nil {
			destroyFields(fields)
			return CredentialVersion{}, NewFault("VALIDATION_FAILED", "field update is invalid")
		}
		seen[update.FieldType] = true
		secret, fault := agent.consumeHandle(update.SecretHandle, func(binding handleBinding) bool {
			return binding.Purpose == "CREDENTIAL_FIELD" && binding.SessionID == sessionID &&
				binding.Origin == origin && binding.AccountID == account &&
				binding.FieldType == update.FieldType
		})
		if fault != nil {
			destroyFields(fields)
			return CredentialVersion{}, NewFault("SECRET_HANDLE_REJECTED", "version field handle was rejected")
		}
		if previous := fields[update.FieldType]; previous != nil {
			previous.Destroy()
		}
		fields[update.FieldType] = secret
	}
	next := request.ExpectedVersion + 1
	descriptor := digestIdentifier("descriptor", credentialID, strconv.FormatUint(next, 10), request.PreviousDescriptorHash)
	version := CredentialVersion{
		CredentialID: credentialID, Version: next,
		State: "CANDIDATE_LOCAL", DescriptorHash: descriptor,
	}
	agent.mu.Lock()
	defer agent.mu.Unlock()
	record = agent.credentials[credentialID]
	if record == nil || record.summary.ActiveVersion != request.ExpectedVersion ||
		record.summary.DescriptorHash != request.PreviousDescriptorHash ||
		record.versions[next] != nil {
		destroyFields(fields)
		return CredentialVersion{}, NewFault("VERSION_CONFLICT", "credential changed while creating candidate")
	}
	record.versions[next] = &versionRecord{summary: version, fields: fields}
	record.summary.LifecycleStatus = "UPDATE_PENDING"
	return version, nil
}

func (agent *Agent) ConfirmSite(
	sessionID, credentialID string,
	request SiteConfirmationRequest,
) (CredentialVersion, *Fault) {
	if _, fault := agent.requireSession(sessionID); fault != nil {
		return CredentialVersion{}, fault
	}
	if request.ExpectedVersion == 0 || request.CandidateVersion < 2 ||
		!oneOf(request.Outcome, "SUCCEEDED", "FAILED", "MFA_REQUIRED", "POLICY_REJECTED", "UNKNOWN") ||
		!oneOf(request.EvidenceLevel,
			"AUTOFILL_OBSERVED", "SUBMIT_OBSERVED",
			"PAGE_SUCCESS_INDICATED", "NEW_PASSWORD_RELOGIN_CONFIRMED",
			"SITE_SIGNED_RECEIPT", "USER_SIGNED_CONFIRMATION") ||
		(request.ReceiptDigest != "" && !validIdentifier(request.ReceiptDigest, 32)) {
		return CredentialVersion{}, NewFault("VALIDATION_FAILED", "site confirmation is invalid")
	}
	agent.mu.Lock()
	defer agent.mu.Unlock()
	record := agent.credentials[credentialID]
	if record == nil {
		return CredentialVersion{}, NewFault("RESOURCE_NOT_FOUND", "credential was not found")
	}
	if record.summary.ActiveVersion != request.ExpectedVersion ||
		request.CandidateVersion != request.ExpectedVersion+1 {
		return CredentialVersion{}, NewFault("VERSION_CONFLICT", "site confirmation version changed")
	}
	candidate := record.versions[request.CandidateVersion]
	if candidate == nil {
		return CredentialVersion{}, NewFault("LIFECYCLE_CONFLICT", "candidate version was not found")
	}
	candidate.summary.EvidenceLevel = request.EvidenceLevel
	candidate.receiptDigest = request.ReceiptDigest
	switch request.Outcome {
	case "SUCCEEDED":
		evidence, parseErr := protocol.ParseEvidenceDatabaseName(request.EvidenceLevel)
		if parseErr != nil {
			return CredentialVersion{}, NewFault("VALIDATION_FAILED", "site confirmation evidence is invalid")
		}
		policy := protocol.EvidenceActivationPolicy{
			AllowStrictRelogin:    agent.config.AllowStrictRelogin,
			TrustedSiteConnector:  agent.config.TrustedSiteConnector,
			AllowUserConfirmation: true,
		}
		if evidence == protocol.EvidenceSiteSignedReceipt &&
			(!agent.config.TrustedSiteConnector || request.ReceiptDigest == "") {
			candidate.summary.State = "REVIEW_REQUIRED"
			record.summary.LifecycleStatus = "SITE_CONFIRM_PENDING"
			return candidate.summary, NewFault(
				"OPTIONAL_FEATURE_UNAVAILABLE",
				"trusted E4 site connector is not configured",
			)
		}
		if !evidence.CanActivateCredential(policy) {
			switch evidence {
			case protocol.EvidenceAutofillObserved, protocol.EvidenceSubmitObserved:
				candidate.summary.State = "UNKNOWN"
			default:
				candidate.summary.State = "REVIEW_REQUIRED"
			}
			record.summary.LifecycleStatus = "SITE_CONFIRM_PENDING"
			return candidate.summary, nil
		}
		active := record.versions[request.ExpectedVersion]
		active.summary.State = "SUPERSEDED"
		candidate.summary.State = "ACTIVE"
		record.summary.ActiveVersion = request.CandidateVersion
		record.summary.DescriptorHash = candidate.summary.DescriptorHash
		record.summary.LifecycleStatus = "ACTIVE"
		record.envelopeHash = digestIdentifier("envelope", credentialID, candidate.summary.DescriptorHash)
		record.updatedAt = agent.config.Now()
	case "FAILED", "POLICY_REJECTED":
		candidate.summary.State = "FAILED"
		record.summary.LifecycleStatus = "ACTIVE"
	case "MFA_REQUIRED":
		candidate.summary.State = "SITE_CHANGE_IN_PROGRESS"
		record.summary.LifecycleStatus = "UPDATE_PENDING"
	case "UNKNOWN":
		candidate.summary.State = "UNKNOWN"
		record.summary.LifecycleStatus = "SITE_CONFIRM_PENDING"
	}
	return candidate.summary, nil
}

func (agent *Agent) ListVersions(
	sessionID, credentialID, cursor string, limit int,
) (CredentialVersionPage, *Fault) {
	session, fault := agent.requireSession(sessionID)
	if fault != nil {
		return CredentialVersionPage{}, fault
	}
	if limit == 0 {
		limit = 50
	}
	if limit < 1 || limit > 200 {
		return CredentialVersionPage{}, NewFault("VALIDATION_FAILED", "limit is outside the allowed range")
	}
	offset, fault := agent.decodeCursor(cursor, session.deviceID, "versions:"+credentialID)
	if fault != nil {
		return CredentialVersionPage{}, fault
	}
	agent.mu.Lock()
	record := agent.credentials[credentialID]
	if record == nil {
		agent.mu.Unlock()
		return CredentialVersionPage{}, NewFault("RESOURCE_NOT_FOUND", "credential was not found")
	}
	items := make([]CredentialVersion, 0, len(record.versions))
	for _, version := range record.versions {
		items = append(items, version.summary)
	}
	agent.mu.Unlock()
	sort.Slice(items, func(i, j int) bool { return items[i].Version > items[j].Version })
	if offset > len(items) {
		return CredentialVersionPage{}, NewFault("CURSOR_REJECTED", "cursor is invalid or expired")
	}
	end := offset + limit
	if end > len(items) {
		end = len(items)
	}
	page := CredentialVersionPage{Items: append([]CredentialVersion(nil), items[offset:end]...)}
	if end < len(items) {
		page.NextCursor = agent.encodeCursor(end, session.deviceID, "versions:"+credentialID)
	}
	return page, nil
}

func (agent *Agent) QueueOperation(sessionID, kind string) (OperationStatus, *Fault) {
	if sessionID != "" {
		if _, fault := agent.requireSession(sessionID); fault != nil {
			return OperationStatus{}, fault
		}
	}
	status := OperationStatus{
		OperationID: uuid.NewString(), State: "PENDING",
		ResultReference: "local-operation:" + strings.ToLower(kind),
	}
	agent.mu.Lock()
	agent.operations[status.OperationID] = status
	agent.mu.Unlock()
	return status, nil
}

// CreateSecurityAnalysis consumes the Native Messaging-staged secret and
// materializes only minimized local findings. The production composition
// supplies the G6 AUDIT_ANALYZE gate before this reference projection.
func (agent *Agent) CreateSecurityAnalysis(
	sessionID string,
	request SecurityAnalysisRequest,
) (OperationStatus, *Fault) {
	session, fault := agent.requireSession(sessionID)
	if fault != nil {
		return OperationStatus{}, fault
	}
	if len(request.AnalysisTypes) == 0 ||
		!validIdentifier(request.SourceCheckpointHash, 32) ||
		request.WindowStart != nil && request.WindowEnd != nil &&
			request.WindowEnd.Before(*request.WindowStart) {
		return OperationStatus{}, NewFault("VALIDATION_FAILED", "security analysis request is invalid")
	}
	allowed := make(map[string]bool, len(request.AnalysisTypes))
	for _, analysisType := range request.AnalysisTypes {
		if !oneOf(
			analysisType, "PASSWORD_REUSE", "HISTORICAL_USE",
			"STALE_CREDENTIAL", "ANOMALOUS_DEVICE", "ROLLBACK", "CONFLICT",
		) || allowed[analysisType] {
			return OperationStatus{}, NewFault("VALIDATION_FAILED", "security analysis type is invalid")
		}
		allowed[analysisType] = true
	}
	agent.mu.Lock()
	handleID := agent.pendingAuditHandles[sessionID]
	delete(agent.pendingAuditHandles, sessionID)
	agent.mu.Unlock()
	secret, fault := agent.consumeHandle(handleID, func(binding handleBinding) bool {
		return binding.Purpose == "AUDIT_ANALYSIS" && binding.SessionID == sessionID
	})
	if fault != nil {
		return OperationStatus{}, NewFault("SECRET_HANDLE_REJECTED", "audit analysis handle was rejected")
	}
	defer secret.Destroy()

	analysisID := uuid.NewString()
	bucket := uint64(agent.config.Now().Unix() / 86400)
	if bucket == 0 {
		bucket = 1
	}
	agent.mu.Lock()
	findings := agent.analyzeLocalLocked(secret, analysisID, bucket, allowed)
	agent.mu.Unlock()
	sort.Slice(findings, func(i, j int) bool {
		if findings[i].CredentialPseudonym == findings[j].CredentialPseudonym {
			return findings[i].Kind < findings[j].Kind
		}
		return findings[i].CredentialPseudonym < findings[j].CredentialPseudonym
	})
	status := OperationStatus{
		OperationID: uuid.NewString(), State: "COMPLETED",
		ResultReference: "native-security-analysis:" + analysisID,
	}
	agent.mu.Lock()
	agent.securityResults[analysisID] = append([]SecurityFinding(nil), findings...)
	agent.operations[status.OperationID] = status
	agent.mu.Unlock()
	_ = session
	return status, nil
}

func (agent *Agent) analyzeLocalLocked(
	candidate *cryptokit.Secret,
	analysisID string,
	bucket uint64,
	allowed map[string]bool,
) []SecurityFinding {
	activeGroups := make(map[[sha256.Size]byte][]string, len(agent.credentials))
	findings := make([]SecurityFinding, 0)
	appendFinding := func(kind string, record *credentialRecord) {
		if record == nil || !allowed[kind] {
			return
		}
		findings = append(findings, SecurityFinding{
			Kind: kind,
			CredentialPseudonym: digestIdentifier(
				"analysis-pseudonym", analysisID, record.summary.CredentialID,
			),
			Confidence: "STRONG",
			EvidenceObjectDigests: []string{
				record.summary.DescriptorHash,
				digestIdentifier("proof", record.summary.DescriptorHash),
			},
			ObservedTimeBucket: bucket, CurrentVersion: record.summary.ActiveVersion,
		})
	}
	for id, record := range agent.credentials {
		version := record.versions[record.summary.ActiveVersion]
		if version != nil && version.fields["PASSWORD"] != nil {
			if tag, err := ephemeralAnalysisTag(
				agent.cursorKey, analysisID, version.fields["PASSWORD"],
			); err == nil {
				activeGroups[tag] = append(activeGroups[tag], id)
			}
		}
		if allowed["HISTORICAL_USE"] {
			for _, historical := range record.versions {
				if historical.fields["PASSWORD"] == nil {
					continue
				}
				equal, err := cryptokit.SecretsEqual(candidate, historical.fields["PASSWORD"])
				if err == nil && equal {
					appendFinding("HISTORICAL_USE", record)
					break
				}
			}
		}
		if allowed["STALE_CREDENTIAL"] && !record.updatedAt.IsZero() &&
			agent.config.Now().Sub(record.updatedAt) >= 90*24*time.Hour {
			appendFinding("STALE_CREDENTIAL", record)
		}
		if allowed["ROLLBACK"] && record.summary.Verdict == "REJECT_CAUSAL" {
			appendFinding("ROLLBACK", record)
		}
		if allowed["CONFLICT"] && record.summary.LifecycleStatus == "CONFLICTED" {
			appendFinding("CONFLICT", record)
		}
	}
	if allowed["PASSWORD_REUSE"] {
		for tag, ids := range activeGroups {
			if len(ids) > 1 {
				for _, id := range ids {
					appendFinding("PASSWORD_REUSE", agent.credentials[id])
				}
			}
			clear(tag[:])
		}
	}
	return findings
}

func ephemeralAnalysisTag(
	key [sha256.Size]byte,
	analysisID string,
	secret *cryptokit.Secret,
) ([sha256.Size]byte, error) {
	var result [sha256.Size]byte
	err := secret.Use(func(value []byte) error {
		mac := hmac.New(sha256.New, key[:])
		_, _ = mac.Write([]byte("VDNS-PM/2/LOCAL-ANALYSIS-TAG"))
		_, _ = mac.Write([]byte(analysisID))
		_, _ = mac.Write(value)
		copy(result[:], mac.Sum(nil))
		return nil
	})
	return result, err
}

func (agent *Agent) ListSecurityFindings(
	sessionID, resultReference, cursor string, limit int,
) (SecurityFindingPage, *Fault) {
	session, fault := agent.requireSession(sessionID)
	if fault != nil {
		return SecurityFindingPage{}, fault
	}
	const prefix = "native-security-analysis:"
	if !strings.HasPrefix(resultReference, prefix) ||
		uuid.Validate(strings.TrimPrefix(resultReference, prefix)) != nil {
		return SecurityFindingPage{}, NewFault("RESOURCE_NOT_FOUND", "security analysis was not found")
	}
	analysisID := strings.TrimPrefix(resultReference, prefix)
	if limit == 0 {
		limit = 50
	}
	if limit < 1 || limit > 200 {
		return SecurityFindingPage{}, NewFault("VALIDATION_FAILED", "limit is outside the allowed range")
	}
	offset, fault := agent.decodeCursor(cursor, session.deviceID, "security:"+analysisID)
	if fault != nil {
		return SecurityFindingPage{}, fault
	}
	agent.mu.Lock()
	items, exists := agent.securityResults[analysisID]
	items = append([]SecurityFinding(nil), items...)
	agent.mu.Unlock()
	if !exists || offset > len(items) {
		return SecurityFindingPage{}, NewFault("RESOURCE_NOT_FOUND", "security analysis was not found")
	}
	end := offset + limit
	if end > len(items) {
		end = len(items)
	}
	page := SecurityFindingPage{Items: append([]SecurityFinding(nil), items[offset:end]...)}
	if end < len(items) {
		page.NextCursor = agent.encodeCursor(end, session.deviceID, "security:"+analysisID)
	}
	return page, nil
}

func (agent *Agent) GetOperation(sessionID, operationID string) (OperationStatus, *Fault) {
	if _, fault := agent.requireSession(sessionID); fault != nil {
		return OperationStatus{}, fault
	}
	if uuid.Validate(operationID) != nil {
		return OperationStatus{}, NewFault("RESOURCE_NOT_FOUND", "operation was not found")
	}
	agent.mu.Lock()
	defer agent.mu.Unlock()
	status, ok := agent.operations[operationID]
	if !ok {
		return OperationStatus{}, NewFault("RESOURCE_NOT_FOUND", "operation was not found")
	}
	return status, nil
}

func (agent *Agent) EnrollDevice(sessionID string, request DeviceEnrollmentRequest) (OperationStatus, *Fault) {
	if _, fault := agent.requireSession(sessionID); fault != nil {
		return OperationStatus{}, fault
	}
	if uuid.Validate(request.ChallengeID) != nil || !validIdentifier(request.NewDeviceID, 16) ||
		!validIdentifier(request.AuthPublicKey, 32) || !validIdentifier(request.HPKEPublicKey, 32) ||
		!request.ShortCodeConfirmed || len(request.RequestedCapabilities) == 0 {
		return OperationStatus{}, NewFault("VALIDATION_FAILED", "device enrollment is invalid")
	}
	for _, capability := range request.RequestedCapabilities {
		if !oneOf(capability, "READ", "AUTOFILL", "PUBLISH_AUDIT", "CREATE", "UPDATE", "ROTATE", "MIGRATE", "REVOKE", "DEVICE_ENROLL", "RELATION_PUBLISH", "AUDIT_ANALYZE") {
			return OperationStatus{}, NewFault("CAPABILITY_REJECTED", "requested capability is invalid")
		}
	}
	agent.mu.Lock()
	if agent.devices[request.NewDeviceID] != nil {
		agent.mu.Unlock()
		return OperationStatus{}, NewFault("LIFECYCLE_CONFLICT", "device already exists")
	}
	agent.devices[request.NewDeviceID] = &deviceRecord{issuanceCounter: 1}
	agent.mu.Unlock()
	return agent.QueueOperation(sessionID, "DEVICE_ENROLL")
}

func (agent *Agent) RevokeDevice(sessionID string, request DeviceRevocationRequest) (OperationStatus, *Fault) {
	session, fault := agent.requireSession(sessionID)
	if fault != nil {
		return OperationStatus{}, fault
	}
	if !validIdentifier(request.DeviceID, 16) || request.Reason == "" ||
		len(request.Reason) > 512 || request.ExpectedIssuanceCounter == 0 {
		return OperationStatus{}, NewFault("VALIDATION_FAILED", "device revocation is invalid")
	}
	if session.deviceID == request.DeviceID {
		return OperationStatus{}, NewFault("CAPABILITY_REJECTED", "a device cannot revoke its own active session")
	}
	agent.mu.Lock()
	device := agent.devices[request.DeviceID]
	if device == nil {
		agent.mu.Unlock()
		return OperationStatus{}, NewFault("RESOURCE_NOT_FOUND", "device was not found")
	}
	if device.issuanceCounter != request.ExpectedIssuanceCounter {
		agent.mu.Unlock()
		return OperationStatus{}, NewFault("VERSION_CONFLICT", "device issuance counter changed")
	}
	device.revoked = true
	agent.mu.Unlock()
	return agent.QueueOperation(sessionID, "DEVICE_REVOKE")
}

func (agent *Agent) Recover(request RecoverySessionRequest) (OperationStatus, *Fault) {
	if !validIdentifier(request.NamespaceID, 16) || !validIdentifier(request.NewDeviceID, 16) ||
		uuid.Validate(request.RecoverySecretHandle) != nil || agent.config.RecoveryVerifier == nil {
		return OperationStatus{}, NewFault("RECOVERY_REJECTED", "recovery request was rejected")
	}
	secret, fault := agent.consumeHandle(request.RecoverySecretHandle, func(binding handleBinding) bool {
		return binding.Purpose == "RECOVERY_SECRET" &&
			binding.AccountID == request.NamespaceID && binding.DeviceID == request.NewDeviceID
	})
	if fault != nil {
		return OperationStatus{}, NewFault("RECOVERY_REJECTED", "recovery request was rejected")
	}
	defer secret.Destroy()
	if err := agent.config.RecoveryVerifier(request.NamespaceID, request.NewDeviceID, secret); err != nil {
		return OperationStatus{}, NewFault("RECOVERY_REJECTED", "recovery request was rejected")
	}
	agent.mu.Lock()
	agent.devices[request.NewDeviceID] = &deviceRecord{issuanceCounter: 1}
	agent.mu.Unlock()
	return agent.QueueOperation("", "RECOVERY")
}

func (agent *Agent) ResolveVDNS(sessionID string, request VDNSResolutionRequest) (VDNSResolution, *Fault) {
	if _, fault := agent.requireSession(sessionID); fault != nil {
		return VDNSResolution{}, fault
	}
	if !validIdentifier(request.CredentialID, 32) ||
		!validIdentifier(request.TrustedCheckpointHash, 32) ||
		!oneOf(request.Operation, "RESOLVE", "AUTOFILL", "CREATE", "UPDATE_PREPARE", "UPDATE_CONFIRM", "SYNC_ACCEPT", "ROTATE", "MIGRATE", "REVOKE", "AUDIT_ANALYZE") {
		return VDNSResolution{}, NewFault("VALIDATION_FAILED", "VDNS resolution request is invalid")
	}
	if agent.config.VDNSResolver == nil {
		return VDNSResolution{}, NewFault(
			"OPTIONAL_FEATURE_UNAVAILABLE",
			"the complete L1-L5 resolver is not configured",
		)
	}
	result, resolverFault := agent.config.VDNSResolver(request)
	if resolverFault != nil {
		return VDNSResolution{}, resolverFault
	}
	if result.CredentialID != request.CredentialID ||
		result.ResolutionID == "" || result.Verdict == "" ||
		result.LayerResults.L1 == "" || result.LayerResults.L2 == "" ||
		result.LayerResults.L3 == "" || result.LayerResults.L4 == "" ||
		result.LayerResults.L5 == "" {
		return VDNSResolution{}, NewFault(
			"VDNS_VERIFICATION_REJECTED",
			"the L1-L5 resolver returned an incomplete result",
		)
	}
	return result, nil
}

func (agent *Agent) requireSession(sessionID string) (*sessionRecord, *Fault) {
	if uuid.Validate(sessionID) != nil {
		return nil, NewFault("VAULT_SESSION_INVALID", "vault session is invalid")
	}
	now := agent.config.Now()
	agent.mu.Lock()
	defer agent.mu.Unlock()
	agent.purgeExpiredLocked(now)
	session := agent.sessions[sessionID]
	if session == nil {
		return nil, NewFault("VAULT_SESSION_INVALID", "vault session is invalid or expired")
	}
	if device := agent.devices[session.deviceID]; device != nil && device.revoked {
		delete(agent.sessions, sessionID)
		return nil, NewFault("DEVICE_REVOKED", "device has been revoked")
	}
	session.lastUsed = now
	copy := *session
	return &copy, nil
}

func (agent *Agent) consumeHandle(
	handleID string,
	accept func(handleBinding) bool,
) (*cryptokit.Secret, *Fault) {
	if uuid.Validate(handleID) != nil || accept == nil {
		return nil, NewFault("SECRET_HANDLE_REJECTED", "secret handle was rejected")
	}
	now := agent.config.Now()
	agent.mu.Lock()
	defer agent.mu.Unlock()
	agent.purgeExpiredLocked(now)
	entry := agent.handles[handleID]
	if entry == nil {
		return nil, NewFault("SECRET_HANDLE_REJECTED", "secret handle was rejected")
	}
	delete(agent.handles, handleID)
	if !accept(entry.binding) {
		entry.secret.Destroy()
		return nil, NewFault("SECRET_HANDLE_REJECTED", "secret handle was rejected")
	}
	return entry.secret, nil
}

func (agent *Agent) purgeExpiredLocked(now time.Time) {
	for id, session := range agent.sessions {
		if !now.Before(session.expiresAt) || now.Sub(session.lastUsed) >= agent.config.SessionIdleTimeout {
			delete(agent.sessions, id)
		}
	}
	for id, entry := range agent.handles {
		if !now.Before(entry.expiresAt) {
			entry.secret.Destroy()
			delete(agent.handles, id)
		}
	}
}

func (agent *Agent) encodeCursor(offset int, deviceID, scope string) string {
	payload := strconv.Itoa(offset) + "|" + deviceID + "|" + scope
	tag := cursorMAC(agent.cursorKey, payload)
	return base64.RawURLEncoding.EncodeToString([]byte(payload + "|" + base64.RawURLEncoding.EncodeToString(tag[:16])))
}

func (agent *Agent) decodeCursor(cursor, deviceID, scope string) (int, *Fault) {
	if cursor == "" {
		return 0, nil
	}
	if len(cursor) > 512 {
		return 0, NewFault("CURSOR_REJECTED", "cursor is invalid or expired")
	}
	decoded, err := base64.RawURLEncoding.DecodeString(cursor)
	if err != nil {
		return 0, NewFault("CURSOR_REJECTED", "cursor is invalid or expired")
	}
	parts := strings.Split(string(decoded), "|")
	if len(parts) != 4 || parts[1] != deviceID || parts[2] != scope {
		return 0, NewFault("CURSOR_REJECTED", "cursor is invalid or expired")
	}
	payload := strings.Join(parts[:3], "|")
	tag := cursorMAC(agent.cursorKey, payload)
	expected := base64.RawURLEncoding.EncodeToString(tag[:16])
	if subtle.ConstantTimeCompare([]byte(parts[3]), []byte(expected)) != 1 {
		return 0, NewFault("CURSOR_REJECTED", "cursor is invalid or expired")
	}
	offset, err := strconv.Atoi(parts[0])
	if err != nil || offset < 0 {
		return 0, NewFault("CURSOR_REJECTED", "cursor is invalid or expired")
	}
	return offset, nil
}

func canonicalOrigin(raw string) (string, error) {
	origin, err := credentialdomain.NormalizeOrigin(raw)
	if err != nil {
		return "", err
	}
	defer origin.Destroy()
	var result string
	err = origin.UseCanonical(func(value []byte) error {
		result = string(value)
		return nil
	})
	return result, err
}

func randomIdentifier(size int) (string, error) {
	value := make([]byte, size)
	if _, err := io.ReadFull(rand.Reader, value); err != nil {
		clear(value)
		return "", err
	}
	defer clear(value)
	return base64.RawURLEncoding.EncodeToString(value), nil
}

func cursorMAC(key [sha256.Size]byte, payload string) [sha256.Size]byte {
	mac := hmac.New(sha256.New, key[:])
	_, _ = mac.Write([]byte(payload))
	var result [sha256.Size]byte
	copy(result[:], mac.Sum(nil))
	return result
}

func digestIdentifier(parts ...string) string {
	hash := sha256.New()
	for _, part := range parts {
		hash.Write([]byte{byte(len(part) >> 8), byte(len(part))})
		hash.Write([]byte(part))
	}
	return base64.RawURLEncoding.EncodeToString(hash.Sum(nil))
}

func validIdentifier(value string, size int) bool {
	decoded, err := base64.RawURLEncoding.DecodeString(value)
	return err == nil && len(decoded) == size && base64.RawURLEncoding.EncodeToString(decoded) == value
}

func validFieldType(value string) bool {
	return oneOf(value, "ORIGIN", "USERNAME", "PASSWORD", "TOTP", "RECOVERY_CODES", "NOTE")
}

func oneOf(value string, allowed ...string) bool {
	for _, candidate := range allowed {
		if value == candidate {
			return true
		}
	}
	return false
}

func cloneFields(input map[string]*cryptokit.Secret) map[string]*cryptokit.Secret {
	output := make(map[string]*cryptokit.Secret, len(input))
	for field, value := range input {
		cloned, err := value.Clone()
		if err != nil {
			destroyFields(output)
			return nil
		}
		output[field] = cloned
	}
	return output
}

func destroyFields(fields map[string]*cryptokit.Secret) {
	for _, value := range fields {
		value.Destroy()
	}
}

func allZero(value []byte) bool {
	var combined byte
	for _, current := range value {
		combined |= current
	}
	return combined == 0
}
