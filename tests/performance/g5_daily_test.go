package performance_test

import (
	"bytes"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"net/http/httptest"
	"runtime"
	"sort"
	"testing"
	"time"

	"vdns.local/vdns/internal/adapters/inbound/httpapi"
	"vdns.local/vdns/internal/cryptokit"
	localapp "vdns.local/vdns/internal/localapi/application"
)

const performanceToken = "performance-install-token-000000000000000000001"

func TestDailyAutofillEndToEndP95(t *testing.T) {
	if testing.Short() {
		t.Skip("performance evidence is skipped in short mode")
	}
	master := []byte("performance-master-input")
	agent, err := localapp.NewAgent(localapp.Config{
		UnlockVerifier: performanceUnlock(sha256.Sum256(master)),
	})
	if err != nil {
		t.Fatal(err)
	}
	deviceID := performanceID(16, 1)
	masterHandle, _ := agent.StageMasterPassword(deviceID, master)
	session, fault := agent.CreateVaultSession(localapp.CreateVaultSessionRequest{
		DeviceID: deviceID, MasterPasswordHandle: masterHandle,
	})
	if fault != nil {
		t.Fatal(fault)
	}
	origin, account := "https://performance.example", "benchmark"
	username, _ := agent.StageCredentialField(
		session.SessionID, origin, account, "USERNAME", []byte(account),
	)
	password, _ := agent.StageCredentialField(
		session.SessionID, origin, account, "PASSWORD", []byte("benchmark-password-value"),
	)
	created, fault := agent.CreateCredential(session.SessionID, localapp.CreateCredentialRequest{
		Origin: origin, AccountID: account, UsernameHandle: username,
		PasswordHandle: password, CryptoPolicyHash: performanceID(32, 11),
	})
	if fault != nil {
		t.Fatal(fault)
	}
	handler, err := httpapi.New(agent, httpapi.Config{
		InstallToken: performanceToken,
		AllowedExtensionOrigins: []string{
			"chrome-extension://aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
		},
		GeneralRequestsPerMinute: 100_000,
	})
	if err != nil {
		t.Fatal(err)
	}
	body, _ := json.Marshal(map[string]any{
		"origin": origin, "fieldType": "PASSWORD", "expectedVersion": 1,
	})
	const repetitions = 1000
	durations := make([]time.Duration, repetitions)
	runtime.GC()
	var before, after runtime.MemStats
	runtime.ReadMemStats(&before)
	for index := range durations {
		request := httptest.NewRequest(
			http.MethodPost,
			"/api/v2/credentials/"+created.CredentialID+"/autofill-authorizations",
			bytes.NewReader(body),
		)
		request.RemoteAddr, request.Host = "127.0.0.1:41000", "127.0.0.1:43821"
		request.Header.Set("Authorization", "Bearer "+performanceToken)
		request.Header.Set("Origin", "chrome-extension://aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
		request.Header.Set("Content-Type", "application/json")
		request.Header.Set("X-VDNS-Vault-Session", session.SessionID)
		request.Header.Set("X-VDNS-Request-Nonce", fmt.Sprintf("performance-request-nonce-%012d", index))
		request.Header.Set("Idempotency-Key", fmt.Sprintf("performance-autofill-key-%012d", index))
		response := httptest.NewRecorder()
		started := time.Now()
		handler.ServeHTTP(response, request)
		if response.Code != http.StatusCreated {
			t.Fatalf("iteration %d status=%d body=%s", index, response.Code, response.Body.String())
		}
		var authorization localapp.AutofillAuthorization
		if err := json.Unmarshal(response.Body.Bytes(), &authorization); err != nil {
			t.Fatal(err)
		}
		if err := agent.ConsumeNativeHandle(
			session.SessionID, authorization.SecretHandle.SecretHandle,
			origin, "PASSWORD", func(value []byte) error {
				if len(value) != len("benchmark-password-value") {
					return errors.New("unexpected secret length")
				}
				return nil
			},
		); err != nil {
			t.Fatal(err)
		}
		durations[index] = time.Since(started)
	}
	runtime.ReadMemStats(&after)
	sort.Slice(durations, func(i, j int) bool { return durations[i] < durations[j] })
	p50 := percentile(durations, 50)
	p95 := percentile(durations, 95)
	p99 := percentile(durations, 99)
	if p95 > 100*time.Millisecond {
		t.Fatalf("autofill P95=%s exceeds 100ms", p95)
	}
	evidence := map[string]any{
		"experiment":          "E2_G5_LOCAL_AUTOFILL",
		"repetitions":         repetitions,
		"p50Micros":           p50.Microseconds(),
		"p95Micros":           p95.Microseconds(),
		"p99Micros":           p99.Microseconds(),
		"thresholdMicros":     (100 * time.Millisecond).Microseconds(),
		"passed":              true,
		"goVersion":           runtime.Version(),
		"os":                  runtime.GOOS,
		"arch":                runtime.GOARCH,
		"cpuCount":            runtime.NumCPU(),
		"heapAllocDeltaBytes": signedDelta(after.HeapAlloc, before.HeapAlloc),
		"path":                "HTTP auth+nonce+VDNS projection+object clone+Native handle consume",
		"waitsForChainOrVRF":  false,
	}
	encoded, _ := json.Marshal(evidence)
	t.Log(string(encoded))
}

func BenchmarkDailyAutofillAuthorization(b *testing.B) {
	master := []byte("benchmark-master-input")
	agent, _ := localapp.NewAgent(localapp.Config{
		UnlockVerifier: performanceUnlock(sha256.Sum256(master)),
	})
	device := performanceID(16, 21)
	handle, _ := agent.StageMasterPassword(device, master)
	session, _ := agent.CreateVaultSession(localapp.CreateVaultSessionRequest{
		DeviceID: device, MasterPasswordHandle: handle,
	})
	origin, account := "https://benchmark.example", "alice"
	username, _ := agent.StageCredentialField(session.SessionID, origin, account, "USERNAME", []byte(account))
	password, _ := agent.StageCredentialField(session.SessionID, origin, account, "PASSWORD", []byte("benchmark-password-value"))
	created, _ := agent.CreateCredential(session.SessionID, localapp.CreateCredentialRequest{
		Origin: origin, AccountID: account, UsernameHandle: username,
		PasswordHandle: password, CryptoPolicyHash: performanceID(32, 31),
	})
	b.ResetTimer()
	for index := 0; index < b.N; index++ {
		authorization, fault := agent.AuthorizeAutofill(
			session.SessionID, created.CredentialID,
			localapp.AutofillAuthorizationRequest{
				Origin: origin, FieldType: "PASSWORD", ExpectedVersion: 1,
			},
		)
		if fault != nil {
			b.Fatal(fault)
		}
		if err := agent.ConsumeNativeHandle(
			session.SessionID, authorization.SecretHandle.SecretHandle,
			origin, "PASSWORD", func([]byte) error { return nil },
		); err != nil {
			b.Fatal(err)
		}
	}
}

func percentile(values []time.Duration, percent int) time.Duration {
	index := (percent*len(values) + 99) / 100
	if index < 1 {
		index = 1
	}
	return values[index-1]
}

func signedDelta(after, before uint64) int64 {
	if after >= before {
		return int64(after - before)
	}
	return -int64(before - after)
}

func performanceUnlock(expected [sha256.Size]byte) func(string, *cryptokit.Secret) error {
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

func performanceID(size int, seed byte) string {
	value := make([]byte, size)
	for index := range value {
		value[index] = seed + byte(index)
	}
	return base64.RawURLEncoding.EncodeToString(value)
}
