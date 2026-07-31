package nativemessaging

import (
	"bytes"
	"crypto/sha256"
	"encoding/base64"
	"encoding/binary"
	"encoding/json"
	"errors"
	"testing"

	"vdns.local/vdns/internal/cryptokit"
	localapp "vdns.local/vdns/internal/localapi/application"
)

func TestHostSecureInputAndOneUseAutofill(t *testing.T) {
	t.Parallel()
	master := []byte("native-host-test-master")
	agent, err := localapp.NewAgent(localapp.Config{
		UnlockVerifier: verifier(sha256.Sum256(master)),
	})
	if err != nil {
		t.Fatal(err)
	}
	host, err := New(agent, Config{
		BaseURL:      "http://127.0.0.1:43821",
		InstallToken: "native-host-install-token-000000000000000001",
	})
	if err != nil {
		t.Fatal(err)
	}
	deviceID := testID(16, 1)
	stage := decodeNativeResponse(t, host.Handle(encodeRequest(t, map[string]any{
		"requestId": "1", "command": "stageMasterPassword",
		"deviceId": deviceID, "secretValue": string(master),
	})))
	if !stage.OK || stage.SecretHandle == "" || stage.SecretValue != "" {
		t.Fatalf("stage = %+v", stage)
	}
	session, fault := agent.CreateVaultSession(localapp.CreateVaultSessionRequest{
		DeviceID: deviceID, MasterPasswordHandle: stage.SecretHandle,
	})
	if fault != nil {
		t.Fatal(fault)
	}
	username := stageField(t, host, session.SessionID, "https://native.example", "alice", "USERNAME", "alice")
	password := stageField(t, host, session.SessionID, "https://native.example", "alice", "PASSWORD", "native-password-value")
	created, fault := agent.CreateCredential(session.SessionID, localapp.CreateCredentialRequest{
		Origin: "https://native.example", AccountID: "alice",
		UsernameHandle: username, PasswordHandle: password,
		CryptoPolicyHash: testID(32, 9),
	})
	if fault != nil {
		t.Fatal(fault)
	}
	authorization, fault := agent.AuthorizeAutofill(
		session.SessionID, created.CredentialID,
		localapp.AutofillAuthorizationRequest{
			Origin: "https://native.example", FieldType: "PASSWORD", ExpectedVersion: 1,
		},
	)
	if fault != nil {
		t.Fatal(fault)
	}
	consumeRequest := encodeRequest(t, map[string]any{
		"requestId": "4", "command": "consumeSecretHandle",
		"sessionId": session.SessionID, "origin": "https://native.example",
		"fieldType": "PASSWORD", "secretHandle": authorization.SecretHandle.SecretHandle,
	})
	consumed := decodeNativeResponse(t, host.Handle(consumeRequest))
	if !consumed.OK || consumed.SecretValue != "native-password-value" {
		t.Fatalf("consume = %+v", consumed)
	}
	replay := decodeNativeResponse(t, host.Handle(consumeRequest))
	if replay.OK || replay.Code != "SECRET_HANDLE_REJECTED" || replay.SecretValue != "" {
		t.Fatalf("replay = %+v", replay)
	}

	auditStage := decodeNativeResponse(t, host.Handle(encodeRequest(t, map[string]any{
		"requestId": "5", "command": "stageAuditAnalysisSecret",
		"sessionId": session.SessionID, "secretValue": "native-password-value",
	})))
	if !auditStage.OK || auditStage.SecretHandle == "" {
		t.Fatalf("audit stage = %+v", auditStage)
	}
	operation, fault := agent.CreateSecurityAnalysis(
		session.SessionID,
		localapp.SecurityAnalysisRequest{
			AnalysisTypes:        []string{"HISTORICAL_USE"},
			SourceCheckpointHash: testID(32, 10),
		},
	)
	if fault != nil {
		t.Fatal(fault)
	}
	findings := decodeNativeResponse(t, host.Handle(encodeRequest(t, map[string]any{
		"requestId": "6", "command": "readSecurityAnalysisResult",
		"sessionId":       session.SessionID,
		"resultReference": operation.ResultReference, "limit": 20,
	})))
	if !findings.OK || findings.Result == nil ||
		findings.SecretHandle != "" || findings.SecretValue != "" {
		t.Fatalf("security findings = %+v", findings)
	}
}

func TestHostPersistentFramingAndSecretFreeErrors(t *testing.T) {
	t.Parallel()
	agent, _ := localapp.NewAgent(localapp.Config{
		UnlockVerifier: func(string, *cryptokit.Secret) error { return errors.New("rejected") },
	})
	host, _ := New(agent, Config{
		BaseURL:      "http://127.0.0.1:43821",
		InstallToken: "native-host-install-token-000000000000000002",
	})
	var input bytes.Buffer
	writeTestFrame(t, &input, encodeRequest(t, map[string]any{
		"requestId": "connection", "command": "connectionInfo",
	}))
	writeTestFrame(t, &input, encodeRequest(t, map[string]any{
		"requestId": "bad", "command": "unknown",
		"secretValue": "must-never-appear-in-error",
	}))
	var output bytes.Buffer
	if err := host.Run(&input, &output); err != nil {
		t.Fatal(err)
	}
	first, err := readFrame(&output)
	if err != nil {
		t.Fatal(err)
	}
	connection := decodeNativeResponse(t, first)
	if !connection.OK || connection.BaseURL != "http://127.0.0.1:43821" ||
		connection.InstallToken == "" {
		t.Fatalf("connection = %+v", connection)
	}
	second, err := readFrame(&output)
	if err != nil {
		t.Fatal(err)
	}
	if bytes.Contains(second, []byte("must-never-appear")) {
		t.Fatalf("error leaked input: %s", second)
	}
	rejected := decodeNativeResponse(t, second)
	if rejected.OK || rejected.Code != "NATIVE_COMMAND_REJECTED" {
		t.Fatalf("rejected = %+v", rejected)
	}
}

func TestHostRejectsOversizedFrame(t *testing.T) {
	t.Parallel()
	agent, _ := localapp.NewAgent(localapp.Config{
		UnlockVerifier: func(string, *cryptokit.Secret) error { return nil },
	})
	host, _ := New(agent, Config{
		BaseURL:      "http://127.0.0.1:43821",
		InstallToken: "native-host-install-token-000000000000000003",
	})
	var input bytes.Buffer
	if err := binary.Write(&input, binary.LittleEndian, uint32(maxMessageBytes+1)); err != nil {
		t.Fatal(err)
	}
	if err := host.Run(&input, &bytes.Buffer{}); err == nil {
		t.Fatal("oversized frame accepted")
	}
}

func stageField(
	t *testing.T,
	host *Host,
	sessionID, origin, account, field, value string,
) string {
	t.Helper()
	result := decodeNativeResponse(t, host.Handle(encodeRequest(t, map[string]any{
		"requestId": "field-" + field, "command": "stageCredentialField",
		"sessionId": sessionID, "origin": origin, "accountId": account,
		"fieldType": field, "secretValue": value,
	})))
	if !result.OK || result.SecretHandle == "" {
		t.Fatalf("stage %s = %+v", field, result)
	}
	return result.SecretHandle
}

func verifier(expected [sha256.Size]byte) func(string, *cryptokit.Secret) error {
	return func(_ string, secret *cryptokit.Secret) error {
		var actual [sha256.Size]byte
		_ = secret.Use(func(value []byte) error {
			actual = sha256.Sum256(value)
			return nil
		})
		if actual != expected {
			return errors.New("rejected")
		}
		return nil
	}
}

func encodeRequest(t *testing.T, value any) []byte {
	t.Helper()
	encoded, err := json.Marshal(value)
	if err != nil {
		t.Fatal(err)
	}
	return encoded
}

func decodeNativeResponse(t *testing.T, encoded []byte) response {
	t.Helper()
	var value response
	if err := json.Unmarshal(encoded, &value); err != nil {
		t.Fatalf("decode %q: %v", encoded, err)
	}
	return value
}

func writeTestFrame(t *testing.T, output *bytes.Buffer, message []byte) {
	t.Helper()
	if err := writeFrame(output, message); err != nil {
		t.Fatal(err)
	}
}

func testID(size int, seed byte) string {
	value := make([]byte, size)
	for index := range value {
		value[index] = seed + byte(index)
	}
	return base64.RawURLEncoding.EncodeToString(value)
}

func FuzzNativeMessageDecoder(f *testing.F) {
	agent, _ := localapp.NewAgent(localapp.Config{
		UnlockVerifier: func(string, *cryptokit.Secret) error { return errors.New("rejected") },
	})
	host, _ := New(agent, Config{
		BaseURL:      "http://127.0.0.1:43821",
		InstallToken: "native-host-fuzz-token-0000000000000000001",
	})
	f.Add([]byte(`{"requestId":"seed","command":"connectionInfo"}`))
	f.Add([]byte(`{"requestId":"seed","command":"unknown","secretValue":"redact"}`))
	f.Fuzz(func(t *testing.T, message []byte) {
		if len(message) > maxMessageBytes {
			t.Skip()
		}
		response := host.Handle(message)
		if len(response) == 0 || len(response) > maxMessageBytes || !json.Valid(response) {
			t.Fatal("Native Messaging handler returned an invalid frame")
		}
	})
}
