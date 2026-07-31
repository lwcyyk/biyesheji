// Package httpapi exposes the loopback-only /api/v2 adapter. It performs
// transport authentication, Origin/Host checks, replay protection, limits and
// idempotency before dispatching to the local-agent application.
package httpapi

import (
	"bytes"
	"crypto/sha256"
	"crypto/subtle"
	"encoding/base64"
	"encoding/json"
	"errors"
	"io"
	"mime"
	"net"
	"net/http"
	"net/url"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/google/uuid"

	localapp "vdns.local/vdns/internal/localapi/application"
	localports "vdns.local/vdns/internal/localapi/ports"
)

const (
	defaultMaxBodyBytes = int64(64 * 1024)
	nonceLifetime       = 5 * time.Minute
	idempotencyLifetime = 24 * time.Hour
)

type Config struct {
	InstallToken             string
	AllowedExtensionOrigins  []string
	MaxBodyBytes             int64
	Now                      func() time.Time
	GeneralRequestsPerMinute int
	UnlocksPerMinute         int
	RecoveriesPerMinute      int
	IdempotencyStore         localports.IdempotencyStore
	OperationStore           localports.OperationStore
}

type nonceRecord struct {
	expiresAt time.Time
}

type cachedResponse struct {
	requestHash [sha256.Size]byte
	status      int
	header      http.Header
	body        []byte
	expiresAt   time.Time
}

type rateWindow struct {
	start time.Time
	count int
}

type Handler struct {
	agent       *localapp.Agent
	config      Config
	tokenDigest [sha256.Size]byte
	origins     map[string]struct{}

	mu          sync.Mutex
	nonces      map[string]nonceRecord
	idempotency map[[sha256.Size]byte]cachedResponse
	idemLocks   map[[sha256.Size]byte]*sync.Mutex
	rates       map[string]rateWindow
}

// ImplementedOperationIDs is the transport implementation inventory used by
// the OpenAPI contract test. A route may return OPTIONAL_FEATURE_UNAVAILABLE
// while its G6 module is disabled, but it must still preserve its v2 contract.
func ImplementedOperationIDs() []string {
	return []string{
		"createVaultSession", "deleteVaultSession",
		"createPasswordGeneration", "createCredentialRouteResolution",
		"listCredentials", "createCredential", "getCredential",
		"createAutofillAuthorization", "listCredentialVersions",
		"createCredentialVersion", "createSiteConfirmation",
		"createSyncPublication", "createSyncPull",
		"createDeviceEnrollment", "createDeviceRevocation",
		"createRecoverySession", "createVdnsResolution", "createAuditEvent",
		"createSecurityAnalysis", "createExposureAnalysis",
		"createRemediationCampaign", "getOperation",
	}
}

func New(agent *localapp.Agent, config Config) (*Handler, error) {
	if agent == nil || len(config.InstallToken) < 32 || len(config.InstallToken) > 512 {
		return nil, errors.New("invalid local API configuration")
	}
	if config.Now == nil {
		config.Now = time.Now
	}
	if config.MaxBodyBytes <= 0 {
		config.MaxBodyBytes = defaultMaxBodyBytes
	}
	if config.MaxBodyBytes > 1024*1024 {
		return nil, errors.New("local API body limit is too large")
	}
	if config.GeneralRequestsPerMinute <= 0 {
		config.GeneralRequestsPerMinute = 600
	}
	if config.UnlocksPerMinute <= 0 {
		config.UnlocksPerMinute = 5
	}
	if config.RecoveriesPerMinute <= 0 {
		config.RecoveriesPerMinute = 3
	}
	origins := make(map[string]struct{}, len(config.AllowedExtensionOrigins))
	for _, origin := range config.AllowedExtensionOrigins {
		if !validExtensionOrigin(origin) {
			return nil, errors.New("invalid extension Origin allowlist")
		}
		origins[origin] = struct{}{}
	}
	return &Handler{
		agent: agent, config: config,
		tokenDigest: sha256.Sum256([]byte(config.InstallToken)),
		origins:     origins, nonces: make(map[string]nonceRecord),
		idempotency: make(map[[sha256.Size]byte]cachedResponse),
		idemLocks:   make(map[[sha256.Size]byte]*sync.Mutex),
		rates:       make(map[string]rateWindow),
	}, nil
}

func (handler *Handler) ServeHTTP(writer http.ResponseWriter, request *http.Request) {
	requestID := uuid.NewString()
	writer.Header().Set("X-Request-Id", requestID)
	writer.Header().Set("Cache-Control", "no-store")
	writer.Header().Set("X-Content-Type-Options", "nosniff")
	if request == nil || !strings.HasPrefix(request.URL.Path, "/api/v2/") {
		writeFault(writer, requestID, http.StatusNotFound, localapp.NewFault("RESOURCE_NOT_FOUND", "resource was not found"))
		return
	}
	if !isLoopbackPeer(request.RemoteAddr) || !validLoopbackHost(request.Host) {
		writeFault(writer, requestID, http.StatusForbidden, localapp.NewFault("LOCAL_CHANNEL_REJECTED", "local channel validation failed"))
		return
	}
	if fault := handler.applyCORS(writer, request); fault != nil {
		writeFault(writer, requestID, http.StatusForbidden, fault)
		return
	}
	if request.Method == http.MethodOptions {
		writer.WriteHeader(http.StatusNoContent)
		return
	}
	if !handler.authenticated(request.Header.Get("Authorization")) {
		writeFault(writer, requestID, http.StatusUnauthorized, localapp.NewFault("INSTALLATION_TOKEN_INVALID", "installation authentication failed"))
		return
	}
	rateClass := classifyRate(request.URL.Path)
	if !handler.allowRate(rateClass) {
		writer.Header().Set("Retry-After", "60")
		code := "REQUEST_RATE_LIMITED"
		if rateClass == "unlock" {
			code = "UNLOCK_RATE_LIMITED"
		} else if rateClass == "recovery" {
			code = "RECOVERY_RATE_LIMITED"
		}
		writeFault(writer, requestID, http.StatusTooManyRequests, localapp.NewFault(code, "request rate limit reached"))
		return
	}

	body, fault := handler.readBody(request)
	if fault != nil {
		writeFault(writer, requestID, http.StatusUnprocessableEntity, fault)
		return
	}
	if requiresNonce(request.Method, request.URL.Path) {
		if fault := handler.consumeNonce(request.Header.Get("X-VDNS-Request-Nonce")); fault != nil {
			writeFault(writer, requestID, http.StatusUnauthorized, fault)
			return
		}
	}
	idempotencyKey := request.Header.Get("Idempotency-Key")
	if requiresIdempotency(request.Method, request.URL.Path) {
		if !validIdempotencyKey(idempotencyKey) {
			writeFault(writer, requestID, http.StatusUnprocessableEntity, localapp.NewFault("IDEMPOTENCY_KEY_INVALID", "Idempotency-Key must contain 16 to 128 visible characters"))
			return
		}
		unlock := handler.lockIdempotency(idempotencyKey)
		defer unlock()
		if served, conflict, err := handler.replayIdempotent(writer, request, body, idempotencyKey); err != nil {
			writeFault(writer, requestID, http.StatusServiceUnavailable, localapp.NewFault("IDEMPOTENCY_UNAVAILABLE", "idempotency state is temporarily unavailable"))
			return
		} else if served {
			if conflict {
				writeFault(writer, requestID, http.StatusConflict, localapp.NewFault("IDEMPOTENCY_CONFLICT", "Idempotency-Key was reused with another request"))
			}
			return
		}
	}

	recorder := newCaptureWriter()
	handler.dispatch(recorder, request, body, requestID)
	if requiresIdempotency(request.Method, request.URL.Path) && recorder.status >= 200 && recorder.status < 300 {
		if err := handler.storeIdempotent(request, body, idempotencyKey, recorder); err != nil {
			failed := newCaptureWriter()
			writeFault(failed, requestID, http.StatusServiceUnavailable, localapp.NewFault("IDEMPOTENCY_UNAVAILABLE", "idempotency result could not be made durable"))
			recorder = failed
		}
	}
	copyResponse(writer, recorder)
}

func (handler *Handler) dispatch(
	writer http.ResponseWriter,
	request *http.Request,
	body []byte,
	requestID string,
) {
	path := strings.TrimPrefix(request.URL.Path, "/api/v2")
	sessionID := request.Header.Get("X-VDNS-Vault-Session")
	segments := splitPath(path)

	switch {
	case request.Method == http.MethodPost && path == "/vault-sessions":
		var input localapp.CreateVaultSessionRequest
		if !decodeStrict(body, &input) {
			writeValidation(writer, requestID)
			return
		}
		result, fault := handler.agent.CreateVaultSession(input)
		if fault != nil {
			writeApplicationFault(writer, requestID, fault)
			return
		}
		writer.Header().Set("Location", "/api/v2/vault-sessions/"+result.SessionID)
		writeJSON(writer, http.StatusCreated, result)
	case request.Method == http.MethodDelete && len(segments) == 2 && segments[0] == "vault-sessions":
		if fault := handler.agent.DeleteVaultSession(segments[1]); fault != nil {
			writeApplicationFault(writer, requestID, fault)
			return
		}
		writer.WriteHeader(http.StatusNoContent)
	case request.Method == http.MethodPost && path == "/password-generations":
		var input localapp.PasswordGenerationRequest
		if !decodeStrict(body, &input) {
			writeValidation(writer, requestID)
			return
		}
		result, fault := handler.agent.GeneratePassword(sessionID, input)
		writeResult(writer, requestID, http.StatusCreated, result, fault)
	case request.Method == http.MethodPost && path == "/credential-route-resolutions":
		var input localapp.RouteResolutionRequest
		if !decodeStrict(body, &input) {
			writeValidation(writer, requestID)
			return
		}
		result, fault := handler.agent.ResolveRoute(sessionID, input)
		writeResult(writer, requestID, http.StatusOK, result, fault)
	case request.Method == http.MethodGet && path == "/credentials":
		limit, fault := parseLimit(request.URL.Query())
		if fault != nil {
			writeApplicationFault(writer, requestID, fault)
			return
		}
		result, appFault := handler.agent.ListCredentials(sessionID, request.URL.Query().Get("cursor"), limit)
		writeResult(writer, requestID, http.StatusOK, result, appFault)
	case request.Method == http.MethodPost && path == "/credentials":
		var input localapp.CreateCredentialRequest
		if !decodeStrict(body, &input) {
			writeValidation(writer, requestID)
			return
		}
		result, fault := handler.agent.CreateCredential(sessionID, input)
		writeResult(writer, requestID, http.StatusCreated, result, fault)
	case len(segments) == 2 && segments[0] == "credentials" && request.Method == http.MethodGet:
		result, fault := handler.agent.GetCredential(sessionID, segments[1])
		writeResult(writer, requestID, http.StatusOK, result, fault)
	case len(segments) == 3 && segments[0] == "credentials" && segments[2] == "autofill-authorizations" && request.Method == http.MethodPost:
		var input localapp.AutofillAuthorizationRequest
		if !decodeStrict(body, &input) {
			writeValidation(writer, requestID)
			return
		}
		result, fault := handler.agent.AuthorizeAutofill(sessionID, segments[1], input)
		writeResult(writer, requestID, http.StatusCreated, result, fault)
	case len(segments) == 3 && segments[0] == "credentials" && segments[2] == "versions" && request.Method == http.MethodPost:
		var input localapp.CreateVersionRequest
		if !decodeStrict(body, &input) {
			writeValidation(writer, requestID)
			return
		}
		result, fault := handler.agent.CreateVersion(sessionID, segments[1], input)
		writeResult(writer, requestID, http.StatusCreated, result, fault)
	case len(segments) == 3 && segments[0] == "credentials" && segments[2] == "versions" && request.Method == http.MethodGet:
		limit, fault := parseLimit(request.URL.Query())
		if fault != nil {
			writeApplicationFault(writer, requestID, fault)
			return
		}
		result, appFault := handler.agent.ListVersions(sessionID, segments[1], request.URL.Query().Get("cursor"), limit)
		writeResult(writer, requestID, http.StatusOK, result, appFault)
	case len(segments) == 3 && segments[0] == "credentials" && segments[2] == "site-confirmations" && request.Method == http.MethodPost:
		var input localapp.SiteConfirmationRequest
		if !decodeStrict(body, &input) {
			writeValidation(writer, requestID)
			return
		}
		result, fault := handler.agent.ConfirmSite(sessionID, segments[1], input)
		writeResult(writer, requestID, http.StatusCreated, result, fault)
	case request.Method == http.MethodPost && path == "/sync-publications":
		var input localapp.SyncPublicationRequest
		if !decodeStrict(body, &input) || !validDigest(input.BaseCheckpointHash) ||
			input.MaxObjects < 0 || input.MaxObjects > 10000 {
			writeValidation(writer, requestID)
			return
		}
		result, fault := handler.agent.QueueOperation(sessionID, "SYNC_PUBLICATION")
		handler.writeDurableOperation(writer, request, body, requestID, http.StatusAccepted, "SYNC_PUBLICATION", result, fault)
	case request.Method == http.MethodPost && path == "/sync-pulls":
		var input localapp.SyncPullRequest
		if !decodeStrict(body, &input) || !validDigest(input.TrustedCheckpointHash) ||
			len(input.Cursor) > 512 || input.Limit < 0 || input.Limit > 10000 {
			writeValidation(writer, requestID)
			return
		}
		result, fault := handler.agent.QueueOperation(sessionID, "SYNC_PULL")
		handler.writeDurableOperation(writer, request, body, requestID, http.StatusAccepted, "SYNC_PULL", result, fault)
	case request.Method == http.MethodPost && path == "/device-enrollments":
		var input localapp.DeviceEnrollmentRequest
		if !decodeStrict(body, &input) {
			writeValidation(writer, requestID)
			return
		}
		result, fault := handler.agent.EnrollDevice(sessionID, input)
		handler.writeDurableOperation(writer, request, body, requestID, http.StatusCreated, "DEVICE_ENROLL", result, fault)
	case request.Method == http.MethodPost && path == "/device-revocations":
		var input localapp.DeviceRevocationRequest
		if !decodeStrict(body, &input) {
			writeValidation(writer, requestID)
			return
		}
		result, fault := handler.agent.RevokeDevice(sessionID, input)
		handler.writeDurableOperation(writer, request, body, requestID, http.StatusAccepted, "DEVICE_REVOKE", result, fault)
	case request.Method == http.MethodPost && path == "/recovery-sessions":
		var input localapp.RecoverySessionRequest
		if !decodeStrict(body, &input) {
			writeValidation(writer, requestID)
			return
		}
		result, fault := handler.agent.Recover(input)
		handler.writeDurableOperation(writer, request, body, requestID, http.StatusCreated, "RECOVERY", result, fault)
	case request.Method == http.MethodPost && path == "/vdns-resolutions":
		var input localapp.VDNSResolutionRequest
		if !decodeStrict(body, &input) {
			writeValidation(writer, requestID)
			return
		}
		result, fault := handler.agent.ResolveVDNS(sessionID, input)
		writeResult(writer, requestID, http.StatusOK, result, fault)
	case request.Method == http.MethodPost && path == "/audit-events":
		var input localapp.AuditEventRequest
		if !decodeStrict(body, &input) || !validDigest(input.CredentialID) ||
			!validDigest(input.EncryptedPayloadDigest) || input.Epoch == 0 ||
			!validEvidence(input.EvidenceLevel) {
			writeValidation(writer, requestID)
			return
		}
		result, fault := handler.agent.QueueOperation(sessionID, "AUDIT_EVENT")
		handler.writeDurableOperation(writer, request, body, requestID, http.StatusAccepted, "AUDIT_EVENT", result, fault)
	case request.Method == http.MethodPost && path == "/security-analyses":
		var input localapp.SecurityAnalysisRequest
		if !decodeStrict(body, &input) || len(input.AnalysisTypes) == 0 ||
			!validDigest(input.SourceCheckpointHash) || !validAnalysisTypes(input.AnalysisTypes) {
			writeValidation(writer, requestID)
			return
		}
		result, fault := handler.agent.CreateSecurityAnalysis(sessionID, input)
		handler.writeDurableOperation(writer, request, body, requestID, http.StatusAccepted, "SECURITY_ANALYSIS", result, fault)
	case request.Method == http.MethodPost && (path == "/exposure-analyses" || path == "/remediation-campaigns"):
		writeFault(writer, requestID, http.StatusNotImplemented, localapp.NewFault("OPTIONAL_FEATURE_UNAVAILABLE", "optional privacy response module is not enabled"))
	case request.Method == http.MethodGet && len(segments) == 2 && segments[0] == "operations":
		result, fault := handler.agent.GetOperation(sessionID, segments[1])
		if fault != nil && fault.Code == "RESOURCE_NOT_FOUND" && handler.config.OperationStore != nil {
			stored, found, err := handler.config.OperationStore.LoadOperation(request.Context(), segments[1])
			if err != nil {
				writeFault(writer, requestID, http.StatusServiceUnavailable, localapp.NewFault("OPERATION_STORE_UNAVAILABLE", "operation status is temporarily unavailable"))
				return
			}
			if found {
				result = localapp.OperationStatus{
					OperationID: stored.OperationID, State: stored.State,
					ResultReference: stored.ResultReference,
				}
				fault = nil
			}
		}
		writeResult(writer, requestID, http.StatusOK, result, fault)
	default:
		writeFault(writer, requestID, http.StatusNotFound, localapp.NewFault("RESOURCE_NOT_FOUND", "resource was not found"))
	}
}

func (handler *Handler) authenticated(header string) bool {
	const prefix = "Bearer "
	if !strings.HasPrefix(header, prefix) || len(header) <= len(prefix) {
		return false
	}
	digest := sha256.Sum256([]byte(header[len(prefix):]))
	return subtle.ConstantTimeCompare(digest[:], handler.tokenDigest[:]) == 1
}

func (handler *Handler) applyCORS(writer http.ResponseWriter, request *http.Request) *localapp.Fault {
	origin := request.Header.Get("Origin")
	if origin == "" {
		return nil
	}
	if origin == "null" {
		return localapp.NewFault("ORIGIN_REJECTED", "request Origin is not allowed")
	}
	if _, ok := handler.origins[origin]; !ok {
		return localapp.NewFault("ORIGIN_REJECTED", "request Origin is not allowed")
	}
	writer.Header().Set("Access-Control-Allow-Origin", origin)
	writer.Header().Set("Vary", "Origin")
	writer.Header().Set("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
	writer.Header().Set("Access-Control-Allow-Headers", "Authorization, Content-Type, Idempotency-Key, X-VDNS-Request-Nonce, X-VDNS-Vault-Session")
	writer.Header().Set("Access-Control-Max-Age", "300")
	return nil
}

func (handler *Handler) readBody(request *http.Request) ([]byte, *localapp.Fault) {
	if request.Body == nil {
		return nil, nil
	}
	if request.Method == http.MethodPost {
		contentType := request.Header.Get("Content-Type")
		mediaType, _, err := mime.ParseMediaType(contentType)
		if err != nil || mediaType != "application/json" {
			return nil, localapp.NewFault("CONTENT_TYPE_REJECTED", "Content-Type must be application/json")
		}
	}
	limited := io.LimitReader(request.Body, handler.config.MaxBodyBytes+1)
	body, err := io.ReadAll(limited)
	if err != nil {
		return nil, localapp.NewFault("REQUEST_READ_FAILED", "request body could not be read")
	}
	if int64(len(body)) > handler.config.MaxBodyBytes {
		clear(body)
		return nil, localapp.NewFault("REQUEST_TOO_LARGE", "request body exceeds the configured limit")
	}
	return body, nil
}

func (handler *Handler) consumeNonce(nonce string) *localapp.Fault {
	if !validNonce(nonce) {
		return localapp.NewFault("REQUEST_NONCE_INVALID", "request nonce is invalid")
	}
	now := handler.config.Now()
	digest := sha256.Sum256([]byte(nonce))
	key := base64.RawURLEncoding.EncodeToString(digest[:])
	handler.mu.Lock()
	defer handler.mu.Unlock()
	for existing, record := range handler.nonces {
		if !now.Before(record.expiresAt) {
			delete(handler.nonces, existing)
		}
	}
	if _, exists := handler.nonces[key]; exists {
		return localapp.NewFault("REQUEST_NONCE_REPLAYED", "request nonce has already been used")
	}
	handler.nonces[key] = nonceRecord{expiresAt: now.Add(nonceLifetime)}
	return nil
}

func (handler *Handler) allowRate(class string) bool {
	limit := handler.config.GeneralRequestsPerMinute
	if class == "unlock" {
		limit = handler.config.UnlocksPerMinute
	} else if class == "recovery" {
		limit = handler.config.RecoveriesPerMinute
	}
	now := handler.config.Now()
	handler.mu.Lock()
	defer handler.mu.Unlock()
	window := handler.rates[class]
	if window.start.IsZero() || now.Sub(window.start) >= time.Minute {
		window = rateWindow{start: now}
	}
	if window.count >= limit {
		handler.rates[class] = window
		return false
	}
	window.count++
	handler.rates[class] = window
	return true
}

func (handler *Handler) replayIdempotent(
	writer http.ResponseWriter,
	request *http.Request,
	body []byte,
	key string,
) (served, conflict bool, loadErr error) {
	keyHash := sha256.Sum256([]byte(key))
	requestHash := canonicalRequestHash(request, body)
	now := handler.config.Now()
	handler.mu.Lock()
	for hash, response := range handler.idempotency {
		if !now.Before(response.expiresAt) {
			clear(response.body)
			delete(handler.idempotency, hash)
		}
	}
	response, ok := handler.idempotency[keyHash]
	handler.mu.Unlock()
	if !ok && handler.config.IdempotencyStore != nil && persistIdempotency(request.URL.Path) {
		stored, found, err := handler.config.IdempotencyStore.Load(
			request.Context(), keyHash, uint64(now.UnixMilli()),
		)
		if err != nil {
			return false, false, err
		}
		if found {
			response = cachedResponse{
				requestHash: stored.RequestHash, status: stored.Status,
				header: http.Header(stored.Headers), body: stored.Body,
				expiresAt: time.UnixMilli(int64(stored.ExpiresAtMS)),
			}
			ok = true
		}
	}
	if !ok {
		return false, false, nil
	}
	if subtle.ConstantTimeCompare(response.requestHash[:], requestHash[:]) != 1 {
		return true, true, nil
	}
	for name, values := range response.header {
		for _, value := range values {
			writer.Header().Add(name, value)
		}
	}
	writer.Header().Set("Idempotency-Replayed", "true")
	writer.WriteHeader(response.status)
	_, _ = writer.Write(response.body)
	return true, false, nil
}

func (handler *Handler) storeIdempotent(
	request *http.Request,
	body []byte,
	key string,
	recorder *captureWriter,
) error {
	keyHash := sha256.Sum256([]byte(key))
	now := handler.config.Now()
	response := cachedResponse{
		requestHash: canonicalRequestHash(request, body), status: recorder.status,
		header: recorder.header.Clone(), body: append([]byte(nil), recorder.body.Bytes()...),
		expiresAt: now.Add(idempotencyLifetime),
	}
	if handler.config.IdempotencyStore != nil && persistIdempotency(request.URL.Path) {
		headers := make(map[string][]string)
		for name, values := range response.header {
			switch strings.ToLower(name) {
			case "content-type", "location":
				headers[name] = append([]string(nil), values...)
			}
		}
		record := localports.IdempotencyResponse{
			KeyHash: keyHash, OperationScope: request.Method + " " + request.URL.RequestURI(),
			RequestHash: response.requestHash, Status: response.status,
			Headers: headers, Body: append([]byte(nil), response.body...),
			CreatedAtMS: uint64(now.UnixMilli()),
			ExpiresAtMS: uint64(response.expiresAt.UnixMilli()),
		}
		if err := handler.config.IdempotencyStore.Put(request.Context(), record); err != nil {
			clear(record.Body)
			return err
		}
		clear(record.Body)
	}
	handler.mu.Lock()
	handler.idempotency[keyHash] = response
	handler.mu.Unlock()
	return nil
}

func (handler *Handler) lockIdempotency(key string) func() {
	keyHash := sha256.Sum256([]byte(key))
	handler.mu.Lock()
	lock := handler.idemLocks[keyHash]
	if lock == nil {
		lock = &sync.Mutex{}
		handler.idemLocks[keyHash] = lock
	}
	handler.mu.Unlock()
	lock.Lock()
	return lock.Unlock
}

func persistIdempotency(path string) bool {
	if path == "/api/v2/vault-sessions" ||
		path == "/api/v2/password-generations" ||
		path == "/api/v2/recovery-sessions" {
		return false
	}
	return !strings.HasSuffix(path, "/autofill-authorizations")
}

func canonicalRequestHash(request *http.Request, body []byte) [sha256.Size]byte {
	canonicalBody := body
	var value any
	decoder := json.NewDecoder(bytes.NewReader(body))
	decoder.UseNumber()
	if len(body) > 0 && decoder.Decode(&value) == nil {
		if encoded, err := json.Marshal(value); err == nil {
			canonicalBody = encoded
		}
	}
	hash := sha256.New()
	_, _ = hash.Write([]byte(request.Method))
	_, _ = hash.Write([]byte{0})
	_, _ = hash.Write([]byte(request.URL.EscapedPath()))
	_, _ = hash.Write([]byte{0})
	_, _ = hash.Write([]byte(request.URL.RawQuery))
	_, _ = hash.Write([]byte{0})
	_, _ = hash.Write(canonicalBody)
	var result [sha256.Size]byte
	copy(result[:], hash.Sum(nil))
	return result
}

func decodeStrict(body []byte, destination any) bool {
	if len(body) == 0 || destination == nil {
		return false
	}
	decoder := json.NewDecoder(bytes.NewReader(body))
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(destination); err != nil {
		return false
	}
	var trailing any
	return decoder.Decode(&trailing) == io.EOF
}

func parseLimit(values url.Values) (int, *localapp.Fault) {
	raw := values.Get("limit")
	if raw == "" {
		return 50, nil
	}
	value, err := strconv.Atoi(raw)
	if err != nil || value < 1 || value > 200 {
		return 0, localapp.NewFault("VALIDATION_FAILED", "limit is outside the allowed range")
	}
	return value, nil
}

func writeValidation(writer http.ResponseWriter, requestID string) {
	writeFault(writer, requestID, http.StatusUnprocessableEntity, localapp.NewFault("VALIDATION_FAILED", "request does not match the API contract"))
}

func writeResult(writer http.ResponseWriter, requestID string, status int, value any, fault *localapp.Fault) {
	if fault != nil {
		writeApplicationFault(writer, requestID, fault)
		return
	}
	writeJSON(writer, status, value)
}

func (handler *Handler) writeDurableOperation(
	writer http.ResponseWriter,
	request *http.Request,
	body []byte,
	requestID string,
	status int,
	kind string,
	value localapp.OperationStatus,
	fault *localapp.Fault,
) {
	if fault != nil {
		writeApplicationFault(writer, requestID, fault)
		return
	}
	if handler.config.OperationStore != nil {
		now := handler.config.Now()
		if now.UnixMilli() < 0 {
			writeFault(writer, requestID, http.StatusServiceUnavailable, localapp.NewFault("OPERATION_STORE_UNAVAILABLE", "operation clock is invalid"))
			return
		}
		record := localports.LocalOperation{
			OperationID: value.OperationID, OperationKind: kind,
			RequestHash: canonicalRequestHash(request, body), State: value.State,
			ResultReference: value.ResultReference,
			CreatedAtMS:     uint64(now.UnixMilli()), UpdatedAtMS: uint64(now.UnixMilli()),
		}
		if err := handler.config.OperationStore.PutOperation(request.Context(), record); err != nil {
			writeFault(writer, requestID, http.StatusServiceUnavailable, localapp.NewFault("OPERATION_STORE_UNAVAILABLE", "operation was not made durable"))
			return
		}
	}
	writeJSON(writer, status, value)
}

func writeApplicationFault(writer http.ResponseWriter, requestID string, fault *localapp.Fault) {
	writeFault(writer, requestID, statusForFault(fault.Code), fault)
}

func writeFault(writer http.ResponseWriter, requestID string, status int, fault *localapp.Fault) {
	message := "request failed"
	code := "INTERNAL_ERROR"
	var details map[string]any
	if fault != nil {
		code, message, details = fault.Code, fault.Message, fault.Details
	}
	writeJSON(writer, status, struct {
		Code      string         `json:"code"`
		Message   string         `json:"message"`
		RequestID string         `json:"requestId"`
		Details   map[string]any `json:"details,omitempty"`
	}{Code: code, Message: message, RequestID: requestID, Details: details})
}

func writeJSON(writer http.ResponseWriter, status int, value any) {
	writer.Header().Set("Content-Type", "application/json")
	writer.WriteHeader(status)
	encoder := json.NewEncoder(writer)
	encoder.SetEscapeHTML(true)
	if err := encoder.Encode(value); err != nil {
		return
	}
}

func statusForFault(code string) int {
	switch code {
	case "INSTALLATION_TOKEN_INVALID", "VAULT_SESSION_INVALID", "UNLOCK_REJECTED",
		"REQUEST_NONCE_INVALID", "REQUEST_NONCE_REPLAYED", "RECOVERY_REJECTED", "DEVICE_REVOKED":
		return http.StatusUnauthorized
	case "ORIGIN_REJECTED", "VDNS_REJECTED", "VDNS_VERIFICATION_REJECTED",
		"CAPABILITY_REJECTED":
		return http.StatusForbidden
	case "RESOURCE_NOT_FOUND":
		return http.StatusNotFound
	case "VERSION_CONFLICT", "DESCRIPTOR_CONFLICT", "LIFECYCLE_CONFLICT":
		return http.StatusConflict
	case "CURRENT_OBJECT_UNAVAILABLE", "PROOF_UNAVAILABLE", "CHECKPOINT_UNAVAILABLE":
		return http.StatusServiceUnavailable
	case "OPTIONAL_FEATURE_UNAVAILABLE":
		return http.StatusNotImplemented
	default:
		return http.StatusUnprocessableEntity
	}
}

func validNonce(value string) bool {
	if len(value) < 22 || len(value) > 128 {
		return false
	}
	for _, current := range value {
		if (current < 'A' || current > 'Z') && (current < 'a' || current > 'z') &&
			(current < '0' || current > '9') && current != '_' && current != '-' {
			return false
		}
	}
	return true
}

func validIdempotencyKey(value string) bool {
	if len(value) < 16 || len(value) > 128 || strings.TrimSpace(value) != value {
		return false
	}
	for _, current := range value {
		if current < 0x21 || current > 0x7e {
			return false
		}
	}
	return true
}

func validDigest(value string) bool {
	decoded, err := base64.RawURLEncoding.DecodeString(value)
	return err == nil && len(decoded) == sha256.Size && base64.RawURLEncoding.EncodeToString(decoded) == value
}

func validEvidence(value string) bool {
	switch value {
	case "AUTOFILL_OBSERVED", "SUBMIT_OBSERVED", "PAGE_SUCCESS_INDICATED",
		"NEW_PASSWORD_RELOGIN_CONFIRMED", "SITE_SIGNED_RECEIPT",
		"USER_SIGNED_CONFIRMATION":
		return true
	default:
		return false
	}
}

func validAnalysisTypes(values []string) bool {
	seen := make(map[string]bool)
	for _, value := range values {
		if seen[value] {
			return false
		}
		seen[value] = true
		switch value {
		case "PASSWORD_REUSE", "HISTORICAL_USE", "STALE_CREDENTIAL", "ANOMALOUS_DEVICE", "ROLLBACK", "CONFLICT":
		default:
			return false
		}
	}
	return true
}

func validExtensionOrigin(origin string) bool {
	if !strings.HasPrefix(origin, "chrome-extension://") {
		return false
	}
	id := strings.TrimPrefix(origin, "chrome-extension://")
	if len(id) != 32 || strings.ContainsAny(id, "?#/ \t\r\n") {
		return false
	}
	for _, current := range id {
		if current < 'a' || current > 'p' {
			return false
		}
	}
	return true
}

func isLoopbackPeer(remote string) bool {
	if remote == "" {
		return true
	}
	host, _, err := net.SplitHostPort(remote)
	if err != nil {
		host = remote
	}
	ip := net.ParseIP(strings.Trim(host, "[]"))
	return ip != nil && ip.IsLoopback()
}

func validLoopbackHost(hostport string) bool {
	host := hostport
	if parsed, _, err := net.SplitHostPort(hostport); err == nil {
		host = parsed
	}
	host = strings.Trim(host, "[]")
	ip := net.ParseIP(host)
	return ip != nil && ip.IsLoopback()
}

func classifyRate(path string) string {
	if path == "/api/v2/vault-sessions" {
		return "unlock"
	}
	if path == "/api/v2/recovery-sessions" {
		return "recovery"
	}
	return "general"
}

func requiresNonce(method, path string) bool {
	if method == http.MethodDelete && strings.HasPrefix(path, "/api/v2/vault-sessions/") {
		return true
	}
	if method != http.MethodPost {
		return false
	}
	switch path {
	case "/api/v2/vault-sessions", "/api/v2/password-generations",
		"/api/v2/credential-route-resolutions", "/api/v2/credentials",
		"/api/v2/device-enrollments", "/api/v2/device-revocations",
		"/api/v2/recovery-sessions", "/api/v2/exposure-analyses",
		"/api/v2/remediation-campaigns":
		return true
	}
	return strings.HasPrefix(path, "/api/v2/credentials/") &&
		(strings.HasSuffix(path, "/autofill-authorizations") ||
			strings.HasSuffix(path, "/versions") ||
			strings.HasSuffix(path, "/site-confirmations"))
}

func requiresIdempotency(method, path string) bool {
	if method != http.MethodPost {
		return false
	}
	return path != "/api/v2/credential-route-resolutions" &&
		path != "/api/v2/vdns-resolutions"
}

func splitPath(path string) []string {
	trimmed := strings.Trim(path, "/")
	if trimmed == "" {
		return nil
	}
	return strings.Split(trimmed, "/")
}

type captureWriter struct {
	header http.Header
	body   bytes.Buffer
	status int
}

func newCaptureWriter() *captureWriter {
	return &captureWriter{header: make(http.Header), status: http.StatusOK}
}

func (writer *captureWriter) Header() http.Header { return writer.header }

func (writer *captureWriter) WriteHeader(status int) {
	if writer.status != http.StatusOK || writer.body.Len() > 0 {
		return
	}
	writer.status = status
}

func (writer *captureWriter) Write(value []byte) (int, error) {
	return writer.body.Write(value)
}

func copyResponse(destination http.ResponseWriter, source *captureWriter) {
	for name, values := range source.header {
		for _, value := range values {
			destination.Header().Add(name, value)
		}
	}
	destination.WriteHeader(source.status)
	_, _ = destination.Write(source.body.Bytes())
}
