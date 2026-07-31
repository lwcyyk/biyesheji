package e2e_test

import (
	"bytes"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"net/http/httptest"
	"sync/atomic"
	"testing"

	"github.com/google/uuid"

	"vdns.local/vdns/internal/adapters/inbound/httpapi"
	"vdns.local/vdns/internal/adapters/inbound/mocksiteweb"
	"vdns.local/vdns/internal/adapters/inbound/nativemessaging"
	"vdns.local/vdns/internal/cryptokit"
	localapp "vdns.local/vdns/internal/localapi/application"
)

const (
	e2eToken  = "e2e-install-token-00000000000000000000000001"
	e2eOrigin = "chrome-extension://aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
)

type dailyClient struct {
	t       *testing.T
	url     string
	session string
	counter atomic.Uint64
}

func TestDailyMockSiteRegisterLoginChangeSyncRevokeAndOffline(t *testing.T) {
	master := []byte("e2e-master-input")
	agent, err := localapp.NewAgent(localapp.Config{
		UnlockVerifier: digestUnlock(sha256.Sum256(master)),
	})
	if err != nil {
		t.Fatal(err)
	}
	apiHandler, err := httpapi.New(agent, httpapi.Config{
		InstallToken: e2eToken, AllowedExtensionOrigins: []string{e2eOrigin},
	})
	if err != nil {
		t.Fatal(err)
	}
	apiServer := httptest.NewServer(apiHandler)
	defer apiServer.Close()
	nativeHost, err := nativemessaging.New(agent, nativemessaging.Config{
		BaseURL: apiServer.URL, InstallToken: e2eToken,
	})
	if err != nil {
		t.Fatal(err)
	}
	site := mocksiteweb.New()
	siteServer := httptest.NewServer(site)

	client := &dailyClient{t: t, url: apiServer.URL}
	deviceID := e2eID(16, 1)
	masterStage := nativeCall(t, nativeHost, map[string]any{
		"requestId": "master", "command": "stageMasterPassword",
		"deviceId": deviceID, "secretValue": string(master),
	})
	unlocked := client.post("/api/v2/vault-sessions", "unlock-session-0001", map[string]any{
		"deviceId": deviceID, "masterPasswordHandle": masterStage["secretHandle"],
	}, http.StatusCreated)
	client.session = unlocked["sessionId"].(string)

	origin := "https://mock-site.example"
	account := "alice"
	generated := client.post("/api/v2/password-generations", "generate-password-0001", map[string]any{
		"origin": origin, "accountId": account, "policyVersion": 1, "length": 20,
	}, http.StatusCreated)
	usernameStage := nativeCall(t, nativeHost, map[string]any{
		"requestId": "username", "command": "stageCredentialField",
		"sessionId": client.session, "origin": origin, "accountId": account,
		"fieldType": "USERNAME", "secretValue": account,
	})
	created := client.post("/api/v2/credentials", "create-credential-0001", map[string]any{
		"origin": origin, "accountId": account,
		"usernameHandle":   usernameStage["secretHandle"],
		"passwordHandle":   generated["secretHandle"],
		"cryptoPolicyHash": e2eID(32, 8),
	}, http.StatusCreated)
	credentialID := created["credentialId"].(string)
	password := authorizeAndConsume(t, client, nativeHost, credentialID, origin, "PASSWORD", 1)
	sitePost(t, siteServer.URL, "/register", map[string]any{
		"accountId": account, "password": password,
	}, http.StatusCreated)
	sitePost(t, siteServer.URL, "/login", map[string]any{
		"accountId": account, "password": password,
	}, http.StatusOK)

	replacement := "replacement-password-e2e"
	replacementStage := nativeCall(t, nativeHost, map[string]any{
		"requestId": "replacement", "command": "stageCredentialField",
		"sessionId": client.session, "origin": origin, "accountId": account,
		"fieldType": "PASSWORD", "secretValue": replacement,
	})
	candidate := client.post("/api/v2/credentials/"+credentialID+"/versions", "create-version-0001", map[string]any{
		"expectedVersion": 1, "previousDescriptorHash": created["descriptorHash"],
		"fieldUpdates": []map[string]any{{
			"fieldType": "PASSWORD", "secretHandle": replacementStage["secretHandle"],
		}},
	}, http.StatusCreated)
	candidateStage := nativeCall(t, nativeHost, map[string]any{
		"requestId": "candidate", "command": "authorizeCandidateField",
		"sessionId": client.session, "credentialId": credentialID,
		"candidateVersion": 2, "origin": origin, "fieldType": "PASSWORD",
	})
	candidatePassword := nativeCall(t, nativeHost, map[string]any{
		"requestId": "candidate-consume", "command": "consumeSecretHandle",
		"sessionId": client.session, "secretHandle": candidateStage["secretHandle"],
		"origin": origin, "fieldType": "PASSWORD",
	})["secretValue"].(string)
	if candidatePassword != replacement {
		t.Fatal("candidate Native Messaging value mismatch")
	}
	receipt := sitePost(t, siteServer.URL, "/change-password", map[string]any{
		"accountId": account, "currentPassword": password, "newPassword": candidatePassword,
	}, http.StatusOK)
	confirmed := client.post(
		"/api/v2/credentials/"+credentialID+"/site-confirmations",
		"confirm-site-0001",
		map[string]any{
			"expectedVersion": 1, "candidateVersion": 2,
			"outcome": receipt["outcome"], "evidenceLevel": "USER_SIGNED_CONFIRMATION",
			"receiptDigest": receipt["receiptDigest"],
		},
		http.StatusCreated,
	)
	if confirmed["state"] != "ACTIVE" || candidate["state"] != "CANDIDATE_LOCAL" {
		t.Fatalf("candidate=%#v confirmed=%#v", candidate, confirmed)
	}
	sitePost(t, siteServer.URL, "/login", map[string]any{
		"accountId": account, "password": replacement,
	}, http.StatusOK)

	checkpoint := e2eID(32, 11)
	publication := client.post("/api/v2/sync-publications", "sync-publish-0001", map[string]any{
		"baseCheckpointHash": checkpoint, "maxObjects": 100,
	}, http.StatusAccepted)
	pull := client.post("/api/v2/sync-pulls", "sync-pull-0000001", map[string]any{
		"trustedCheckpointHash": checkpoint, "limit": 100,
	}, http.StatusAccepted)
	if publication["state"] != "PENDING" || pull["state"] != "PENDING" {
		t.Fatalf("sync must not overclaim completion: publish=%#v pull=%#v", publication, pull)
	}
	newDeviceID := e2eID(16, 31)
	enrollment := client.post("/api/v2/device-enrollments", "enroll-device-0001", map[string]any{
		"challengeId": uuid.NewString(), "newDeviceId": newDeviceID,
		"authPublicKey": e2eID(32, 41), "hpkePublicKey": e2eID(32, 51),
		"requestedCapabilities": []string{"READ", "AUTOFILL"}, "shortCodeConfirmed": true,
	}, http.StatusCreated)
	revocation := client.post("/api/v2/device-revocations", "revoke-device-0001", map[string]any{
		"deviceId": newDeviceID, "reason": "E2E lost device", "expectedIssuanceCounter": 1,
	}, http.StatusAccepted)
	if enrollment["state"] != "PENDING" || revocation["state"] != "PENDING" {
		t.Fatalf("device operation status: enroll=%#v revoke=%#v", enrollment, revocation)
	}

	// The site is now offline. The already verified local vault can still
	// retrieve the active v2 object; no database edit or cloud current-version
	// hint is involved.
	siteServer.Close()
	offlinePassword := authorizeAndConsume(t, client, nativeHost, credentialID, origin, "PASSWORD", 2)
	if offlinePassword != replacement {
		t.Fatal("offline active password mismatch")
	}
	if _, err := http.Post(siteServer.URL+"/login", "application/json", bytes.NewReader(nil)); err == nil {
		t.Fatal("mock site unexpectedly remained online")
	}
}

func (client *dailyClient) post(path, idempotency string, input any, want int) map[string]any {
	client.t.Helper()
	body, err := json.Marshal(input)
	if err != nil {
		client.t.Fatal(err)
	}
	request, err := http.NewRequest(http.MethodPost, client.url+path, bytes.NewReader(body))
	if err != nil {
		client.t.Fatal(err)
	}
	request.Header.Set("Authorization", "Bearer "+e2eToken)
	request.Header.Set("Origin", e2eOrigin)
	request.Header.Set("Content-Type", "application/json")
	request.Header.Set("X-VDNS-Request-Nonce", fmt.Sprintf("e2e-request-nonce-%012d", client.counter.Add(1)))
	if client.session != "" {
		request.Header.Set("X-VDNS-Vault-Session", client.session)
	}
	if idempotency != "" {
		request.Header.Set("Idempotency-Key", idempotency)
	}
	response, err := http.DefaultClient.Do(request)
	if err != nil {
		client.t.Fatal(err)
	}
	defer response.Body.Close()
	var result map[string]any
	if err := json.NewDecoder(response.Body).Decode(&result); err != nil {
		client.t.Fatal(err)
	}
	if response.StatusCode != want {
		client.t.Fatalf("%s status=%d want=%d body=%#v", path, response.StatusCode, want, result)
	}
	return result
}

func authorizeAndConsume(
	t *testing.T,
	client *dailyClient,
	host *nativemessaging.Host,
	credentialID, origin, fieldType string,
	version int,
) string {
	t.Helper()
	authorization := client.post(
		"/api/v2/credentials/"+credentialID+"/autofill-authorizations",
		fmt.Sprintf("autofill-%s-%04d", fieldType, client.counter.Load()+1),
		map[string]any{
			"origin": origin, "fieldType": fieldType, "expectedVersion": version,
		},
		http.StatusCreated,
	)
	result := nativeCall(t, host, map[string]any{
		"requestId": fmt.Sprintf("consume-%d", client.counter.Load()),
		"command":   "consumeSecretHandle", "sessionId": client.session,
		"secretHandle": authorization["secretHandle"], "origin": origin, "fieldType": fieldType,
	})
	return result["secretValue"].(string)
}

func nativeCall(t *testing.T, host *nativemessaging.Host, input any) map[string]any {
	t.Helper()
	encoded, err := json.Marshal(input)
	if err != nil {
		t.Fatal(err)
	}
	reply := host.Handle(encoded)
	var result map[string]any
	if err := json.Unmarshal(reply, &result); err != nil {
		t.Fatal(err)
	}
	if ok, _ := result["ok"].(bool); !ok {
		t.Fatalf("native call rejected: %#v", result)
	}
	return result
}

func sitePost(t *testing.T, baseURL, path string, input any, want int) map[string]any {
	t.Helper()
	body, _ := json.Marshal(input)
	response, err := http.Post(baseURL+path, "application/json", bytes.NewReader(body))
	if err != nil {
		t.Fatal(err)
	}
	defer response.Body.Close()
	var result map[string]any
	if err := json.NewDecoder(response.Body).Decode(&result); err != nil {
		t.Fatal(err)
	}
	if response.StatusCode != want {
		t.Fatalf("site %s status=%d want=%d body=%#v", path, response.StatusCode, want, result)
	}
	return result
}

func digestUnlock(expected [sha256.Size]byte) func(string, *cryptokit.Secret) error {
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

func e2eID(size int, seed byte) string {
	value := make([]byte, size)
	for index := range value {
		value[index] = seed + byte(index)
	}
	return base64.RawURLEncoding.EncodeToString(value)
}
