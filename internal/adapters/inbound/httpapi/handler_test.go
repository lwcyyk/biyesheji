package httpapi

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"net/http/httptest"
	"path/filepath"
	"strings"
	"sync/atomic"
	"testing"
	"time"

	sqliteadapter "vpass.local/vpass/internal/adapters/outbound/sqlite"
	"vpass.local/vpass/internal/cryptokit"
	localapp "vpass.local/vpass/internal/localapi/application"
)

const (
	testToken  = "test-only-install-token-000000000000000000000001"
	testOrigin = "chrome-extension://aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
)

type apiFixture struct {
	handler     *Handler
	localClient *localapp.LocalSecureClient
	session     localapp.VaultSession
	nonce       atomic.Uint64
}

func TestHTTPDailyCredentialContract(t *testing.T) {
	t.Parallel()
	fixture := newAPIFixture(t)
	generation := fixture.request(t, http.MethodPost, "/api/v2/password-generations",
		"password-generate-0001", fixture.session.SessionID,
		map[string]any{
			"origin": "https://BÜCHER.example:443", "accountId": "alice",
			"policyVersion": 1, "length": 20,
		})
	if generation.Code != http.StatusCreated {
		t.Fatalf("generation status=%d body=%s", generation.Code, generation.Body.String())
	}
	var generated localapp.SecretHandle
	decodeResponse(t, generation, &generated)
	username, err := fixture.localClient.StageCredentialField(
		fixture.session.SessionID, "https://xn--bcher-kva.example", "alice", "USERNAME", []byte("alice"),
	)
	if err != nil {
		t.Fatal(err)
	}
	createdResponse := fixture.request(t, http.MethodPost, "/api/v2/credentials",
		"credential-create-0001", fixture.session.SessionID,
		map[string]any{
			"origin": "https://bücher.example", "accountId": "alice",
			"usernameHandle": username, "passwordHandle": generated.SecretHandle,
			"cryptoPolicyHash": testIdentifier(32, 9),
		})
	if createdResponse.Code != http.StatusCreated {
		t.Fatalf("create status=%d body=%s", createdResponse.Code, createdResponse.Body.String())
	}
	var created localapp.Credential
	decodeResponse(t, createdResponse, &created)
	listed := fixture.request(
		t, http.MethodGet, "/api/v2/credentials?limit=10", "",
		fixture.session.SessionID, nil,
	)
	if listed.Code != http.StatusOK {
		t.Fatalf("list status=%d body=%s", listed.Code, listed.Body.String())
	}
	var page localapp.CredentialPage
	decodeResponse(t, listed, &page)
	if len(page.Items) != 1 || page.Items[0].CredentialID != created.CredentialID {
		t.Fatalf("credential page = %+v", page)
	}
	fetched := fixture.request(
		t, http.MethodGet, "/api/v2/credentials/"+created.CredentialID, "",
		fixture.session.SessionID, nil,
	)
	if fetched.Code != http.StatusOK {
		t.Fatalf("get status=%d body=%s", fetched.Code, fetched.Body.String())
	}

	route := fixture.request(t, http.MethodPost, "/api/v2/credential-route-resolutions",
		"", fixture.session.SessionID,
		map[string]any{"origin": "https://XN--BCHER-KVA.EXAMPLE:443", "accountId": "alice", "topFrame": true})
	if route.Code != http.StatusOK {
		t.Fatalf("route status=%d body=%s", route.Code, route.Body.String())
	}
	var resolved localapp.RouteResolution
	decodeResponse(t, route, &resolved)
	if resolved.CredentialID != created.CredentialID || !resolved.OriginVerified {
		t.Fatalf("route = %+v", resolved)
	}

	wrongOrigin := fixture.request(t, http.MethodPost,
		"/api/v2/credentials/"+created.CredentialID+"/autofill-authorizations",
		"autofill-wrong-origin-0001", fixture.session.SessionID,
		map[string]any{"origin": "https://attacker.example", "fieldType": "PASSWORD", "expectedVersion": 1})
	if wrongOrigin.Code != http.StatusForbidden || strings.Contains(wrongOrigin.Body.String(), "secretHandle") {
		t.Fatalf("wrong origin status=%d body=%s", wrongOrigin.Code, wrongOrigin.Body.String())
	}
	authorizationResponse := fixture.request(t, http.MethodPost,
		"/api/v2/credentials/"+created.CredentialID+"/autofill-authorizations",
		"autofill-correct-0001", fixture.session.SessionID,
		map[string]any{"origin": "https://bücher.example", "fieldType": "PASSWORD", "expectedVersion": 1})
	if authorizationResponse.Code != http.StatusCreated {
		t.Fatalf("autofill status=%d body=%s", authorizationResponse.Code, authorizationResponse.Body.String())
	}
	var authorization localapp.AutofillAuthorization
	decodeResponse(t, authorizationResponse, &authorization)
	if authorization.Verdict != "ACCEPT" || !authorization.OriginVerified || !authorization.SingleUse {
		t.Fatalf("authorization = %+v", authorization)
	}
	var filled string
	if err := fixture.localClient.ConsumeNativeHandle(
		fixture.session.SessionID, authorization.SecretHandle.SecretHandle,
		"https://xn--bcher-kva.example", "PASSWORD",
		func(value []byte) error {
			filled = string(value)
			return nil
		},
	); err != nil || len(filled) != 20 {
		t.Fatalf("native fill length=%d err=%v", len(filled), err)
	}
	deleted := fixture.request(
		t, http.MethodDelete,
		"/api/v2/vault-sessions/"+fixture.session.SessionID,
		"", fixture.session.SessionID, nil,
	)
	if deleted.Code != http.StatusNoContent {
		t.Fatalf("delete session status=%d body=%s", deleted.Code, deleted.Body.String())
	}
}

func TestHTTPIdempotencyNonceAndStrictJSON(t *testing.T) {
	t.Parallel()
	fixture := newAPIFixture(t)
	body := map[string]any{
		"origin": "https://idempotent.example", "accountId": "alice",
		"policyVersion": 1, "length": 20,
	}
	first := fixture.request(t, http.MethodPost, "/api/v2/password-generations",
		"same-idempotency-key-0001", fixture.session.SessionID, body)
	second := fixture.request(t, http.MethodPost, "/api/v2/password-generations",
		"same-idempotency-key-0001", fixture.session.SessionID, body)
	if first.Code != http.StatusCreated || second.Code != http.StatusCreated ||
		second.Header().Get("Idempotency-Replayed") != "true" ||
		first.Body.String() != second.Body.String() {
		t.Fatalf("idempotency first=%d second=%d replay=%q", first.Code, second.Code, second.Header().Get("Idempotency-Replayed"))
	}
	conflict := fixture.request(t, http.MethodPost, "/api/v2/password-generations",
		"same-idempotency-key-0001", fixture.session.SessionID,
		map[string]any{
			"origin": "https://idempotent.example", "accountId": "alice",
			"policyVersion": 1, "length": 21,
		})
	assertErrorCode(t, conflict, http.StatusConflict, "IDEMPOTENCY_CONFLICT")

	replayNonce := "nonce-replay-value-0000000001"
	request := fixture.rawRequest(http.MethodPost, "/api/v2/credential-route-resolutions",
		"", fixture.session.SessionID, replayNonce,
		[]byte(`{"origin":"https://none.example"}`))
	firstNonce := httptest.NewRecorder()
	fixture.handler.ServeHTTP(firstNonce, request)
	secondRequest := fixture.rawRequest(http.MethodPost, "/api/v2/credential-route-resolutions",
		"", fixture.session.SessionID, replayNonce,
		[]byte(`{"origin":"https://none.example"}`))
	secondNonce := httptest.NewRecorder()
	fixture.handler.ServeHTTP(secondNonce, secondRequest)
	assertErrorCode(t, secondNonce, http.StatusUnauthorized, "REQUEST_NONCE_REPLAYED")

	unknownField := fixture.request(t, http.MethodPost, "/api/v2/password-generations",
		"unknown-field-key-0001", fixture.session.SessionID,
		map[string]any{
			"origin": "https://strict.example", "accountId": "alice",
			"policyVersion": 1, "unexpected": "rejected",
		})
	assertErrorCode(t, unknownField, http.StatusUnprocessableEntity, "VALIDATION_FAILED")
}

func TestHTTPDurableIdempotencySurvivesHandlerRestart(t *testing.T) {
	t.Parallel()
	master := []byte("durable-idempotency-master")
	localClient, err := localapp.NewLocalSecureClient(localapp.LocalSecureClientConfig{
		UnlockVerifier: testUnlockVerifier(sha256.Sum256(master)),
	})
	if err != nil {
		t.Fatal(err)
	}
	database, err := sqliteadapter.Open(
		context.Background(), filepath.Join(t.TempDir(), "vpass.db"),
	)
	if err != nil {
		t.Fatal(err)
	}
	defer database.Close()
	store, err := sqliteadapter.NewLocalAPIRepository(database)
	if err != nil {
		t.Fatal(err)
	}
	newHandler := func() *Handler {
		value, createErr := New(localClient, Config{
			InstallToken: testToken, AllowedExtensionOrigins: []string{testOrigin},
			IdempotencyStore: store, OperationStore: store,
		})
		if createErr != nil {
			t.Fatal(createErr)
		}
		return value
	}
	device := testIdentifier(16, 81)
	masterHandle, _ := localClient.StageMasterPassword(device, master)
	session, fault := localClient.CreateVaultSession(localapp.CreateVaultSessionRequest{
		DeviceID: device, MasterPasswordHandle: masterHandle,
	})
	if fault != nil {
		t.Fatal(fault)
	}
	username, _ := localClient.StageCredentialField(
		session.SessionID, "https://durable.example", "alice", "USERNAME", []byte("alice"),
	)
	password, _ := localClient.StageCredentialField(
		session.SessionID, "https://durable.example", "alice", "PASSWORD", []byte("durable-password-value"),
	)
	body, _ := json.Marshal(map[string]any{
		"origin": "https://durable.example", "accountId": "alice",
		"usernameHandle": username, "passwordHandle": password,
		"cryptoPolicyHash": testIdentifier(32, 82),
	})
	fixture := &apiFixture{handler: newHandler(), localClient: localClient, session: session}
	firstRequest := fixture.rawRequest(
		http.MethodPost, "/api/v2/credentials", "durable-create-key-0001",
		session.SessionID, "durable-first-nonce-000001", body,
	)
	first := httptest.NewRecorder()
	fixture.handler.ServeHTTP(first, firstRequest)
	if first.Code != http.StatusCreated {
		t.Fatalf("first = %d %s", first.Code, first.Body.String())
	}

	fixture.handler = newHandler()
	secondRequest := fixture.rawRequest(
		http.MethodPost, "/api/v2/credentials", "durable-create-key-0001",
		session.SessionID, "durable-second-nonce-00001", body,
	)
	second := httptest.NewRecorder()
	fixture.handler.ServeHTTP(second, secondRequest)
	if second.Code != http.StatusCreated ||
		second.Header().Get("Idempotency-Replayed") != "true" ||
		second.Body.String() != first.Body.String() {
		t.Fatalf(
			"restart replay = %d replay=%q body=%s",
			second.Code, second.Header().Get("Idempotency-Replayed"), second.Body.String(),
		)
	}
	syncResponse := fixture.request(
		t, http.MethodPost, "/api/v2/sync-publications",
		"durable-sync-key-0001", session.SessionID,
		map[string]any{"baseCheckpointHash": testIdentifier(32, 91), "maxObjects": 10},
	)
	if syncResponse.Code != http.StatusAccepted {
		t.Fatalf("sync = %d %s", syncResponse.Code, syncResponse.Body.String())
	}
	var operation localapp.OperationStatus
	decodeResponse(t, syncResponse, &operation)
	persisted, found, err := store.LoadOperation(context.Background(), operation.OperationID)
	if err != nil || !found || persisted.State != "PENDING" {
		t.Fatalf("durable operation = %+v found=%v err=%v", persisted, found, err)
	}
	operationResponse := fixture.request(
		t, http.MethodGet, "/api/v2/operations/"+operation.OperationID,
		"", session.SessionID, nil,
	)
	if operationResponse.Code != http.StatusOK {
		t.Fatalf(
			"get operation = %d %s",
			operationResponse.Code, operationResponse.Body.String(),
		)
	}
}

func TestHTTPLocalChannelAuthenticationAndLimits(t *testing.T) {
	t.Parallel()
	fixture := newAPIFixture(t)
	body := []byte(`{"origin":"https://none.example"}`)
	cases := []struct {
		name       string
		mutate     func(*http.Request)
		wantStatus int
		wantCode   string
	}{
		{
			name: "bad token",
			mutate: func(request *http.Request) {
				request.Header.Set("Authorization", "Bearer wrong-token-value-which-is-long-enough")
			},
			wantStatus: http.StatusUnauthorized, wantCode: "INSTALLATION_TOKEN_INVALID",
		},
		{
			name:       "dns rebinding host",
			mutate:     func(request *http.Request) { request.Host = "evil.example" },
			wantStatus: http.StatusForbidden, wantCode: "LOCAL_CHANNEL_REJECTED",
		},
		{
			name:       "remote peer",
			mutate:     func(request *http.Request) { request.RemoteAddr = "198.51.100.9:443" },
			wantStatus: http.StatusForbidden, wantCode: "LOCAL_CHANNEL_REJECTED",
		},
		{
			name: "foreign extension",
			mutate: func(request *http.Request) {
				request.Header.Set("Origin", "chrome-extension://bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
			},
			wantStatus: http.StatusForbidden, wantCode: "ORIGIN_REJECTED",
		},
		{
			name:       "null origin",
			mutate:     func(request *http.Request) { request.Header.Set("Origin", "null") },
			wantStatus: http.StatusForbidden, wantCode: "ORIGIN_REJECTED",
		},
	}
	for index, test := range cases {
		test := test
		t.Run(test.name, func(t *testing.T) {
			request := fixture.rawRequest(http.MethodPost, "/api/v2/credential-route-resolutions",
				"", fixture.session.SessionID, fmt.Sprintf("channel-case-nonce-%08d", index), body)
			test.mutate(request)
			response := httptest.NewRecorder()
			fixture.handler.ServeHTTP(response, request)
			assertErrorCode(t, response, test.wantStatus, test.wantCode)
		})
	}

	oversized := bytes.Repeat([]byte("x"), int(defaultMaxBodyBytes)+1)
	request := fixture.rawRequest(http.MethodPost, "/api/v2/password-generations",
		"oversized-body-key-0001", fixture.session.SessionID,
		"oversized-body-nonce-00000001", oversized)
	response := httptest.NewRecorder()
	fixture.handler.ServeHTTP(response, request)
	assertErrorCode(t, response, http.StatusUnprocessableEntity, "REQUEST_TOO_LARGE")
}

func TestHTTPVersionUnknownDoesNotActivate(t *testing.T) {
	t.Parallel()
	fixture := newAPIFixture(t)
	created := fixture.createCredential(t, "https://change.example", "alice")
	replacement, err := fixture.localClient.StageCredentialField(
		fixture.session.SessionID, "https://change.example", "alice", "PASSWORD", []byte("replacement-value"),
	)
	if err != nil {
		t.Fatal(err)
	}
	candidateResponse := fixture.request(t, http.MethodPost,
		"/api/v2/credentials/"+created.CredentialID+"/versions",
		"version-candidate-key-0001", fixture.session.SessionID,
		map[string]any{
			"expectedVersion": 1, "previousDescriptorHash": created.DescriptorHash,
			"fieldUpdates": []map[string]any{{"fieldType": "PASSWORD", "secretHandle": replacement}},
		})
	if candidateResponse.Code != http.StatusCreated {
		t.Fatalf("candidate: %s", candidateResponse.Body.String())
	}
	unknown := fixture.request(t, http.MethodPost,
		"/api/v2/credentials/"+created.CredentialID+"/site-confirmations",
		"site-unknown-key-0001", fixture.session.SessionID,
		map[string]any{
			"expectedVersion": 1, "candidateVersion": 2, "outcome": "UNKNOWN",
			"evidenceLevel": "SUBMIT_OBSERVED",
		})
	if unknown.Code != http.StatusCreated {
		t.Fatalf("unknown: %s", unknown.Body.String())
	}
	var version localapp.CredentialVersion
	decodeResponse(t, unknown, &version)
	if version.State != "UNKNOWN" {
		t.Fatalf("version state = %s", version.State)
	}
	get := fixture.request(t, http.MethodGet, "/api/v2/credentials/"+created.CredentialID,
		"", fixture.session.SessionID, nil)
	var current localapp.Credential
	decodeResponse(t, get, &current)
	if current.ActiveVersion != 1 || current.LifecycleStatus != "SITE_CONFIRM_PENDING" {
		t.Fatalf("UNKNOWN activated candidate: %+v", current)
	}
}

func TestHTTPStage2CapabilityBoundaries(t *testing.T) {
	fixture := newAPIFixture(t)
	sessionID := fixture.session.SessionID
	checkpoint := testIdentifier(32, 0x31)

	for _, test := range []struct {
		name, path, key string
		body            map[string]any
		status          int
	}{
		{
			name: "sync publication", path: "/api/v2/sync-publications",
			key: "stage2-sync-publish-0001", status: http.StatusAccepted,
			body: map[string]any{
				"baseCheckpointHash": checkpoint, "maxObjects": 50,
			},
		},
		{
			name: "sync pull", path: "/api/v2/sync-pulls",
			key: "stage2-sync-pull-key-0001", status: http.StatusAccepted,
			body: map[string]any{
				"trustedCheckpointHash": checkpoint, "limit": 50,
			},
		},
		{
			name: "audit queue", path: "/api/v2/audit-events",
			key: "stage2-audit-event-key-0001", status: http.StatusAccepted,
			body: map[string]any{
				"credentialId":           testIdentifier(32, 0x41),
				"evidenceLevel":          "SUBMIT_OBSERVED",
				"encryptedPayloadDigest": testIdentifier(32, 0x51),
				"epoch":                  1,
			},
		},
		{
			name: "state verifier unconfigured", path: "/api/v2/state-resolutions",
			status: http.StatusNotImplemented,
			body: map[string]any{
				"credentialId": testIdentifier(32, 0x61),
				"operation":    "RESOLVE", "trustedCheckpointHash": checkpoint,
			},
		},
		{
			name: "SCOPE-ZK unavailable", path: "/api/v2/exposure-analyses",
			key: "stage2-exposure-key-0001", status: http.StatusNotImplemented,
			body: map[string]any{},
		},
		{
			name: "remediation unavailable", path: "/api/v2/remediation-campaigns",
			key: "stage2-remediation-key-0001", status: http.StatusNotImplemented,
			body: map[string]any{},
		},
	} {
		t.Run(test.name, func(t *testing.T) {
			response := fixture.request(
				t, http.MethodPost, test.path, test.key, sessionID, test.body,
			)
			if response.Code != test.status {
				t.Fatalf(
					"status=%d want=%d body=%s",
					response.Code, test.status, response.Body.String(),
				)
			}
		})
	}

	newDeviceID := testIdentifier(16, 0x71)
	enrollment := fixture.request(
		t, http.MethodPost, "/api/v2/device-enrollments",
		"stage2-enrollment-key-0001", sessionID,
		map[string]any{
			"challengeId":           "0df0e507-91ac-49b7-b884-63f61072bd26",
			"newDeviceId":           newDeviceID,
			"authPublicKey":         testIdentifier(32, 0x72),
			"hpkePublicKey":         testIdentifier(32, 0x73),
			"requestedCapabilities": []string{"READ", "AUTOFILL"},
			"shortCodeConfirmed":    true,
		},
	)
	if enrollment.Code != http.StatusCreated {
		t.Fatalf("enrollment=%d %s", enrollment.Code, enrollment.Body.String())
	}
	revocation := fixture.request(
		t, http.MethodPost, "/api/v2/device-revocations",
		"stage2-revocation-key-0001", sessionID,
		map[string]any{
			"deviceId": newDeviceID, "reason": "stage2 test",
			"expectedIssuanceCounter": 1,
		},
	)
	if revocation.Code != http.StatusAccepted {
		t.Fatalf("revocation=%d %s", revocation.Code, revocation.Body.String())
	}

	recoverySecret := []byte("http-fixture-recovery-input")
	recoveryDevice := testIdentifier(16, 0x74)
	recoveryHandle, err := fixture.localClient.StageRecoverySecret(
		testIdentifier(16, 0x75), recoveryDevice, recoverySecret,
	)
	if err != nil {
		t.Fatal(err)
	}
	recovery := fixture.request(
		t, http.MethodPost, "/api/v2/recovery-sessions",
		"stage2-recovery-key-0001", "",
		map[string]any{
			"namespaceId":          testIdentifier(16, 0x75),
			"newDeviceId":          recoveryDevice,
			"recoverySecretHandle": recoveryHandle,
		},
	)
	if recovery.Code != http.StatusCreated {
		t.Fatalf("recovery=%d %s", recovery.Code, recovery.Body.String())
	}

	if _, err := fixture.localClient.StageAuditAnalysisSecret(
		sessionID, []byte("stage2-audit-candidate"),
	); err != nil {
		t.Fatal(err)
	}
	analysis := fixture.request(
		t, http.MethodPost, "/api/v2/security-analyses",
		"stage2-security-analysis-0001", sessionID,
		map[string]any{
			"analysisTypes":        []string{"PASSWORD_REUSE"},
			"sourceCheckpointHash": checkpoint,
		},
	)
	if analysis.Code != http.StatusAccepted {
		t.Fatalf("security analysis=%d %s", analysis.Code, analysis.Body.String())
	}
}

func TestHTTPLegacyV2RouteAndHeadersRemainReadable(t *testing.T) {
	t.Parallel()
	fixture := newAPIFixture(t)
	checkpoint := testIdentifier(32, 0x71)
	body, err := json.Marshal(map[string]any{
		"credentialId":          testIdentifier(32, 0x72),
		"operation":             "RESOLVE",
		"trustedCheckpointHash": checkpoint,
	})
	if err != nil {
		t.Fatal(err)
	}

	legacyResolution := fixture.rawRequest(
		http.MethodPost, "/api/v2/vdns-resolutions", "", "", "", body,
	)
	legacyResolution.Header.Set("X-VDNS-Vault-Session", fixture.session.SessionID)
	resolutionResponse := httptest.NewRecorder()
	fixture.handler.ServeHTTP(resolutionResponse, legacyResolution)
	if resolutionResponse.Code != http.StatusNotImplemented {
		t.Fatalf("legacy resolution status=%d body=%s", resolutionResponse.Code, resolutionResponse.Body.String())
	}

	generationBody, err := json.Marshal(map[string]any{
		"origin": "https://example.test", "accountId": "legacy",
		"policyVersion": 1, "length": 20,
	})
	if err != nil {
		t.Fatal(err)
	}
	legacyHeaders := fixture.rawRequest(
		http.MethodPost, "/api/v2/password-generations",
		"legacy-header-generation-0001", "", "", generationBody,
	)
	legacyHeaders.Header.Set("X-VDNS-Vault-Session", fixture.session.SessionID)
	legacyHeaders.Header.Set("X-VDNS-Request-Nonce", "legacy-request-nonce-00000001")
	generationResponse := httptest.NewRecorder()
	fixture.handler.ServeHTTP(generationResponse, legacyHeaders)
	if generationResponse.Code != http.StatusCreated {
		t.Fatalf("legacy header status=%d body=%s", generationResponse.Code, generationResponse.Body.String())
	}
}

func TestHTTPRateLimitHasStableError(t *testing.T) {
	t.Parallel()
	master := []byte("rate-limit-master-input")
	localClient, err := localapp.NewLocalSecureClient(localapp.LocalSecureClientConfig{
		UnlockVerifier: testUnlockVerifier(sha256.Sum256(master)),
	})
	if err != nil {
		t.Fatal(err)
	}
	handler, err := New(localClient, Config{
		InstallToken: testToken, AllowedExtensionOrigins: []string{testOrigin},
		UnlocksPerMinute: 1,
	})
	if err != nil {
		t.Fatal(err)
	}
	device := testIdentifier(16, 2)
	for index := 0; index < 2; index++ {
		handle, _ := localClient.StageMasterPassword(device, master)
		body, _ := json.Marshal(map[string]any{"deviceId": device, "masterPasswordHandle": handle})
		request := httptest.NewRequest(http.MethodPost, "/api/v2/vault-sessions", bytes.NewReader(body))
		request.RemoteAddr, request.Host = "127.0.0.1:40100", "127.0.0.1:43821"
		request.Header.Set("Authorization", "Bearer "+testToken)
		request.Header.Set("Content-Type", "application/json")
		request.Header.Set("Origin", testOrigin)
		request.Header.Set("X-VPass-Request-Nonce", fmt.Sprintf("rate-limit-nonce-%08d", index))
		request.Header.Set("Idempotency-Key", fmt.Sprintf("rate-limit-key-%08d", index))
		response := httptest.NewRecorder()
		handler.ServeHTTP(response, request)
		if index == 1 {
			assertErrorCode(t, response, http.StatusTooManyRequests, "UNLOCK_RATE_LIMITED")
			if response.Header().Get("Retry-After") != "60" {
				t.Fatalf("Retry-After = %q", response.Header().Get("Retry-After"))
			}
		}
	}
}

func newAPIFixture(t *testing.T) *apiFixture {
	t.Helper()
	master := []byte("http-fixture-master-input")
	localClient, err := localapp.NewLocalSecureClient(localapp.LocalSecureClientConfig{
		UnlockVerifier:   testUnlockVerifier(sha256.Sum256(master)),
		RecoveryVerifier: testRecoveryVerifier(sha256.Sum256([]byte("http-fixture-recovery-input"))),
	})
	if err != nil {
		t.Fatal(err)
	}
	handler, err := New(localClient, Config{
		InstallToken: testToken, AllowedExtensionOrigins: []string{testOrigin},
	})
	if err != nil {
		t.Fatal(err)
	}
	device := testIdentifier(16, 1)
	masterHandle, err := localClient.StageMasterPassword(device, master)
	if err != nil {
		t.Fatal(err)
	}
	fixture := &apiFixture{handler: handler, localClient: localClient}
	response := fixture.request(t, http.MethodPost, "/api/v2/vault-sessions",
		"vault-session-key-0001", "",
		map[string]any{"deviceId": device, "masterPasswordHandle": masterHandle})
	if response.Code != http.StatusCreated {
		t.Fatalf("unlock status=%d body=%s", response.Code, response.Body.String())
	}
	decodeResponse(t, response, &fixture.session)
	return fixture
}

func (fixture *apiFixture) createCredential(t *testing.T, origin, account string) localapp.Credential {
	t.Helper()
	username, _ := fixture.localClient.StageCredentialField(
		fixture.session.SessionID, origin, account, "USERNAME", []byte(account),
	)
	password, _ := fixture.localClient.StageCredentialField(
		fixture.session.SessionID, origin, account, "PASSWORD", []byte("fixture-password-value"),
	)
	response := fixture.request(t, http.MethodPost, "/api/v2/credentials",
		"create-helper-key-"+account+"-0001", fixture.session.SessionID,
		map[string]any{
			"origin": origin, "accountId": account, "usernameHandle": username,
			"passwordHandle": password, "cryptoPolicyHash": testIdentifier(32, 7),
		})
	if response.Code != http.StatusCreated {
		t.Fatalf("create credential: %s", response.Body.String())
	}
	var result localapp.Credential
	decodeResponse(t, response, &result)
	return result
}

func (fixture *apiFixture) request(
	t *testing.T,
	method, path, idempotencyKey, sessionID string,
	body any,
) *httptest.ResponseRecorder {
	t.Helper()
	var encoded []byte
	if body != nil {
		var err error
		encoded, err = json.Marshal(body)
		if err != nil {
			t.Fatal(err)
		}
	}
	nonce := fmt.Sprintf("fixture-nonce-value-%012d", fixture.nonce.Add(1))
	request := fixture.rawRequest(method, path, idempotencyKey, sessionID, nonce, encoded)
	response := httptest.NewRecorder()
	fixture.handler.ServeHTTP(response, request)
	return response
}

func (fixture *apiFixture) rawRequest(
	method, path, idempotencyKey, sessionID, nonce string,
	body []byte,
) *http.Request {
	request := httptest.NewRequest(method, path, bytes.NewReader(body))
	request.RemoteAddr = "127.0.0.1:40100"
	request.Host = "127.0.0.1:43821"
	request.Header.Set("Authorization", "Bearer "+testToken)
	request.Header.Set("Origin", testOrigin)
	if method == http.MethodPost {
		request.Header.Set("Content-Type", "application/json")
	}
	if idempotencyKey != "" {
		request.Header.Set("Idempotency-Key", idempotencyKey)
	}
	if sessionID != "" {
		request.Header.Set("X-VPass-Vault-Session", sessionID)
	}
	if nonce != "" {
		request.Header.Set("X-VPass-Request-Nonce", nonce)
	}
	return request
}

func decodeResponse(t *testing.T, response *httptest.ResponseRecorder, destination any) {
	t.Helper()
	if err := json.Unmarshal(response.Body.Bytes(), destination); err != nil {
		t.Fatalf("decode response %q: %v", response.Body.String(), err)
	}
}

func assertErrorCode(t *testing.T, response *httptest.ResponseRecorder, status int, code string) {
	t.Helper()
	if response.Code != status {
		t.Fatalf("status=%d want=%d body=%s", response.Code, status, response.Body.String())
	}
	var value struct {
		Code      string `json:"code"`
		Message   string `json:"message"`
		RequestID string `json:"requestId"`
	}
	decodeResponse(t, response, &value)
	if value.Code != code || value.Message == "" || value.RequestID == "" {
		t.Fatalf("error=%+v", value)
	}
}

func testIdentifier(size int, seed byte) string {
	value := make([]byte, size)
	for index := range value {
		value[index] = seed + byte(index)
	}
	return base64.RawURLEncoding.EncodeToString(value)
}

func testUnlockVerifier(expected [sha256.Size]byte) func(string, *cryptokit.Secret) error {
	return func(_ string, secret *cryptokit.Secret) error {
		var actual [sha256.Size]byte
		if err := secret.Use(func(value []byte) error {
			actual = sha256.Sum256(value)
			return nil
		}); err != nil || actual != expected {
			return errors.New("rejected")
		}
		return nil
	}
}

func testRecoveryVerifier(expected [sha256.Size]byte) func(string, string, *cryptokit.Secret) error {
	return func(_, _ string, secret *cryptokit.Secret) error {
		return testUnlockVerifier(expected)("", secret)
	}
}

func TestCacheControlAndCORSNeverUseWildcard(t *testing.T) {
	t.Parallel()
	fixture := newAPIFixture(t)
	response := fixture.request(t, http.MethodGet, "/api/v2/credentials", "", fixture.session.SessionID, nil)
	if response.Header().Get("Cache-Control") != "no-store" ||
		response.Header().Get("Access-Control-Allow-Origin") != testOrigin ||
		strings.Contains(response.Header().Get("Access-Control-Allow-Origin"), "*") {
		t.Fatalf("security headers = %#v", response.Header())
	}
}

func TestSessionExpiresAtIsRFC3339(t *testing.T) {
	t.Parallel()
	fixture := newAPIFixture(t)
	if _, err := time.Parse(time.RFC3339Nano, fixture.session.ExpiresAt.Format(time.RFC3339Nano)); err != nil {
		t.Fatal(err)
	}
}

func FuzzStrictJSONDecoder(f *testing.F) {
	f.Add([]byte(`{"origin":"https://example.com","accountId":"alice","policyVersion":1}`))
	f.Add([]byte(`{"origin":"https://example.com","unknown":"value"}`))
	f.Add([]byte(`null`))
	f.Fuzz(func(t *testing.T, input []byte) {
		if len(input) > 128*1024 {
			t.Skip()
		}
		var request localapp.PasswordGenerationRequest
		_ = decodeStrict(input, &request)
	})
}
