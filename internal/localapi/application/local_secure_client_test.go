package application

import (
	"crypto/sha256"
	"encoding/base64"
	"errors"
	"testing"
	"time"

	"vpass.local/vpass/internal/cryptokit"
)

func TestLocalSecureClientDailyLifecycleAndOriginGates(t *testing.T) {
	t.Parallel()
	now := time.Date(2026, 7, 23, 9, 0, 0, 0, time.UTC)
	master := []byte("unit-test-master-input")
	recovery := []byte("unit-test-high-entropy-recovery-input")
	localClient, err := NewLocalSecureClient(LocalSecureClientConfig{
		UnlockVerifier:   digestVerifier(sha256.Sum256(master)),
		RecoveryVerifier: recoveryDigestVerifier(sha256.Sum256(recovery)),
		Now:              func() time.Time { return now },
	})
	if err != nil {
		t.Fatalf("NewLocalSecureClient: %v", err)
	}
	deviceID := identifier(16, 1)
	masterHandle, err := localClient.StageMasterPassword(deviceID, master)
	if err != nil {
		t.Fatalf("StageMasterPassword: %v", err)
	}
	session, fault := localClient.CreateVaultSession(CreateVaultSessionRequest{
		DeviceID: deviceID, MasterPasswordHandle: masterHandle,
	})
	if fault != nil {
		t.Fatalf("CreateVaultSession: %v", fault)
	}

	generated, fault := localClient.GeneratePassword(session.SessionID, PasswordGenerationRequest{
		Origin: "https://BÜCHER.example:443", AccountID: "alice", PolicyVersion: 1, Length: 24,
	})
	if fault != nil {
		t.Fatalf("GeneratePassword: %v", fault)
	}
	usernameHandle, err := localClient.StageCredentialField(
		session.SessionID, "https://xn--bcher-kva.example", "alice", "USERNAME", []byte("alice"),
	)
	if err != nil {
		t.Fatalf("StageCredentialField: %v", err)
	}
	created, fault := localClient.CreateCredential(session.SessionID, CreateCredentialRequest{
		Origin: "https://bücher.example", AccountID: "alice",
		UsernameHandle: usernameHandle, PasswordHandle: generated.SecretHandle,
		CryptoPolicyHash: identifier(32, 9),
	})
	if fault != nil {
		t.Fatalf("CreateCredential: %v", fault)
	}
	if created.ActiveVersion != 1 || created.LifecycleStatus != "ACTIVE" || created.Verdict != "ACCEPT" {
		t.Fatalf("unexpected created credential: %+v", created)
	}

	resolved, fault := localClient.ResolveRoute(session.SessionID, RouteResolutionRequest{
		Origin: "https://XN--BCHER-KVA.EXAMPLE:443", AccountID: "alice",
	})
	if fault != nil || resolved.CredentialID != created.CredentialID || !resolved.OriginVerified {
		t.Fatalf("ResolveRoute = %+v, %v", resolved, fault)
	}
	if _, fault := localClient.AuthorizeAutofill(session.SessionID, created.CredentialID, AutofillAuthorizationRequest{
		Origin: "https://attacker.example", FieldType: "PASSWORD", ExpectedVersion: 1,
	}); fault == nil || fault.Code != "ORIGIN_REJECTED" {
		t.Fatalf("wrong Origin fault = %v", fault)
	}
	authorization, fault := localClient.AuthorizeAutofill(
		session.SessionID, created.CredentialID,
		AutofillAuthorizationRequest{
			Origin: "https://bücher.example", FieldType: "PASSWORD", ExpectedVersion: 1,
		},
	)
	if fault != nil || !authorization.SingleUse || !authorization.OriginVerified {
		t.Fatalf("AuthorizeAutofill = %+v, %v", authorization, fault)
	}
	var passwordLength int
	err = localClient.ConsumeNativeHandle(
		session.SessionID, authorization.SecretHandle.SecretHandle,
		"https://xn--bcher-kva.example:443", "PASSWORD",
		func(value []byte) error {
			passwordLength = len(value)
			return nil
		},
	)
	if err != nil || passwordLength != 24 {
		t.Fatalf("ConsumeNativeHandle length=%d err=%v", passwordLength, err)
	}
	if err := localClient.ConsumeNativeHandle(
		session.SessionID, authorization.SecretHandle.SecretHandle,
		"https://xn--bcher-kva.example", "PASSWORD",
		func([]byte) error { return nil },
	); err == nil {
		t.Fatal("one-use handle replay succeeded")
	}

	nextPassword, err := localClient.StageCredentialField(
		session.SessionID, "https://bücher.example", "alice", "PASSWORD", []byte("replacement-secret-value"),
	)
	if err != nil {
		t.Fatalf("stage replacement: %v", err)
	}
	candidate, fault := localClient.CreateVersion(session.SessionID, created.CredentialID, CreateVersionRequest{
		ExpectedVersion: 1, PreviousDescriptorHash: created.DescriptorHash,
		FieldUpdates: []FieldUpdate{{FieldType: "PASSWORD", SecretHandle: nextPassword}},
	})
	if fault != nil || candidate.State != "CANDIDATE_LOCAL" || candidate.Version != 2 {
		t.Fatalf("CreateVersion = %+v, %v", candidate, fault)
	}
	unknown, fault := localClient.ConfirmSite(session.SessionID, created.CredentialID, SiteConfirmationRequest{
		ExpectedVersion: 1, CandidateVersion: 2, Outcome: "UNKNOWN",
		EvidenceLevel: "SUBMIT_OBSERVED",
	})
	if fault != nil || unknown.State != "UNKNOWN" {
		t.Fatalf("unknown confirmation = %+v, %v", unknown, fault)
	}
	stillOld, fault := localClient.GetCredential(session.SessionID, created.CredentialID)
	if fault != nil || stillOld.ActiveVersion != 1 || stillOld.LifecycleStatus != "SITE_CONFIRM_PENDING" {
		t.Fatalf("unknown result incorrectly activated: %+v, %v", stillOld, fault)
	}
	active, fault := localClient.ConfirmSite(session.SessionID, created.CredentialID, SiteConfirmationRequest{
		ExpectedVersion: 1, CandidateVersion: 2, Outcome: "SUCCEEDED",
		EvidenceLevel: "USER_SIGNED_CONFIRMATION", ReceiptDigest: identifier(32, 8),
	})
	if fault != nil || active.State != "ACTIVE" {
		t.Fatalf("site confirmation = %+v, %v", active, fault)
	}
	current, _ := localClient.GetCredential(session.SessionID, created.CredentialID)
	if current.ActiveVersion != 2 || current.DescriptorHash != candidate.DescriptorHash {
		t.Fatalf("candidate not activated: %+v", current)
	}
}

func TestStateResolutionNeverSynthesizesFiveLayerSuccess(t *testing.T) {
	localClient, session := testLocalSecureClientAndSession(t)
	request := StateResolutionRequest{
		CredentialID: identifier(32, 0x31), Operation: "RESOLVE",
		TrustedCheckpointHash: identifier(32, 0x41),
	}
	if _, fault := localClient.ResolveState(
		session.SessionID, request,
	); fault == nil || fault.Code != "OPTIONAL_FEATURE_UNAVAILABLE" {
		t.Fatalf("unconfigured resolver fault = %v", fault)
	}

	master := []byte("resolver-fixture-master")
	resolverClient, err := NewLocalSecureClient(LocalSecureClientConfig{
		UnlockVerifier: digestVerifier(sha256.Sum256(master)),
		StateResolver: func(input StateResolutionRequest) (StateResolution, *Fault) {
			return StateResolution{
				ResolutionID: "resolver-result", CredentialID: input.CredentialID,
				ActiveVersion: 2, ActiveEnvelopeHash: identifier(32, 0x51),
				DescriptorHash: identifier(32, 0x61), Verdict: "ACCEPT",
				LayerResults: LayerResults{
					L1: "OK", L2: "OK", L3: "OK", L4: "OK", L5: "OK",
				},
				ProofBundleDigest: identifier(32, 0x71),
			}, nil
		},
	})
	if err != nil {
		t.Fatal(err)
	}
	deviceID := identifier(16, 0x21)
	handle, _ := resolverClient.StageMasterPassword(deviceID, master)
	resolverSession, fault := resolverClient.CreateVaultSession(
		CreateVaultSessionRequest{
			DeviceID: deviceID, MasterPasswordHandle: handle,
		},
	)
	if fault != nil {
		t.Fatal(fault)
	}
	result, fault := resolverClient.ResolveState(resolverSession.SessionID, request)
	if fault != nil || result.ResolutionID != "resolver-result" {
		t.Fatalf("configured resolver = %+v, %v", result, fault)
	}
}

func TestLocalSecureClientMultipleAccountsRequireExplicitSelection(t *testing.T) {
	t.Parallel()
	localClient, session := testLocalSecureClientAndSession(t)
	for index, account := range []string{"alice", "bob"} {
		username, err := localClient.StageCredentialField(
			session.SessionID, "https://accounts.example", account, "USERNAME", []byte(account),
		)
		if err != nil {
			t.Fatal(err)
		}
		password, err := localClient.StageCredentialField(
			session.SessionID, "https://accounts.example", account, "PASSWORD", []byte("password-"+account),
		)
		if err != nil {
			t.Fatal(err)
		}
		if _, fault := localClient.CreateCredential(session.SessionID, CreateCredentialRequest{
			Origin: "https://accounts.example", AccountID: account,
			UsernameHandle: username, PasswordHandle: password,
			CryptoPolicyHash: identifier(32, byte(10+index)),
		}); fault != nil {
			t.Fatal(fault)
		}
	}
	_, fault := localClient.ResolveRoute(session.SessionID, RouteResolutionRequest{Origin: "https://accounts.example"})
	if fault == nil || fault.Code != "ACCOUNT_SELECTION_REQUIRED" {
		t.Fatalf("multi-account route fault = %v", fault)
	}
	labels, ok := fault.Details["accountLabels"].([]string)
	if !ok || len(labels) != 2 || labels[0] != "alice" || labels[1] != "bob" {
		t.Fatalf("account labels = %#v", fault.Details["accountLabels"])
	}
}

func TestLocalSecureClientSessionExpiryAndHandleBinding(t *testing.T) {
	t.Parallel()
	now := time.Date(2026, 7, 23, 10, 0, 0, 0, time.UTC)
	master := []byte("expiry-test-master-input")
	localClient, err := NewLocalSecureClient(LocalSecureClientConfig{
		UnlockVerifier: digestVerifier(sha256.Sum256(master)), Now: func() time.Time { return now },
		SessionIdleTimeout: time.Minute, SessionAbsoluteTimeout: 2 * time.Minute,
	})
	if err != nil {
		t.Fatal(err)
	}
	deviceID := identifier(16, 3)
	handle, _ := localClient.StageMasterPassword(deviceID, master)
	session, fault := localClient.CreateVaultSession(CreateVaultSessionRequest{
		DeviceID: deviceID, MasterPasswordHandle: handle,
	})
	if fault != nil {
		t.Fatal(fault)
	}
	fieldHandle, _ := localClient.StageCredentialField(
		session.SessionID, "https://one.example", "alice", "PASSWORD", []byte("bound-value"),
	)
	_, fault = localClient.CreateCredential(session.SessionID, CreateCredentialRequest{
		Origin: "https://two.example", AccountID: "alice",
		UsernameHandle: fieldHandle, PasswordHandle: fieldHandle,
		CryptoPolicyHash: identifier(32, 1),
	})
	if fault == nil || fault.Code != "SECRET_HANDLE_REJECTED" {
		t.Fatalf("cross-Origin handle fault = %v", fault)
	}
	now = now.Add(time.Minute)
	if _, fault := localClient.GetCredential(session.SessionID, identifier(32, 1)); fault == nil ||
		fault.Code != "VAULT_SESSION_INVALID" {
		t.Fatalf("idle expiry fault = %v", fault)
	}
}

func TestLocalSecureClientNativeCallbackErrorStillConsumesHandle(t *testing.T) {
	t.Parallel()
	localClient, session := testLocalSecureClientAndSession(t)
	username, _ := localClient.StageCredentialField(
		session.SessionID, "https://consume.example", "alice", "USERNAME", []byte("alice"),
	)
	password, _ := localClient.StageCredentialField(
		session.SessionID, "https://consume.example", "alice", "PASSWORD", []byte("one-use-value"),
	)
	created, fault := localClient.CreateCredential(session.SessionID, CreateCredentialRequest{
		Origin: "https://consume.example", AccountID: "alice",
		UsernameHandle: username, PasswordHandle: password,
		CryptoPolicyHash: identifier(32, 2),
	})
	if fault != nil {
		t.Fatal(fault)
	}
	auth, fault := localClient.AuthorizeAutofill(session.SessionID, created.CredentialID, AutofillAuthorizationRequest{
		Origin: "https://consume.example", FieldType: "PASSWORD", ExpectedVersion: 1,
	})
	if fault != nil {
		t.Fatal(fault)
	}
	sentinel := errors.New("consumer failed")
	if err := localClient.ConsumeNativeHandle(
		session.SessionID, auth.SecretHandle.SecretHandle, "https://consume.example", "PASSWORD",
		func([]byte) error { return sentinel },
	); !errors.Is(err, sentinel) {
		t.Fatalf("callback error = %v", err)
	}
	if err := localClient.ConsumeNativeHandle(
		session.SessionID, auth.SecretHandle.SecretHandle, "https://consume.example", "PASSWORD",
		func([]byte) error { return nil },
	); err == nil {
		t.Fatal("handle survived callback failure")
	}
}

func TestLocalSecureClientSecurityAnalysisUsesOneUseNativeSecretAndPagedMinimizedResults(t *testing.T) {
	t.Parallel()
	localClient, session := testLocalSecureClientAndSession(t)
	for index, account := range []string{"alice", "bob"} {
		username, _ := localClient.StageCredentialField(
			session.SessionID, "https://security.example", account,
			"USERNAME", []byte(account),
		)
		password, _ := localClient.StageCredentialField(
			session.SessionID, "https://security.example", account,
			"PASSWORD", []byte("shared-password"),
		)
		if _, fault := localClient.CreateCredential(session.SessionID, CreateCredentialRequest{
			Origin: "https://security.example", AccountID: account,
			UsernameHandle: username, PasswordHandle: password,
			CryptoPolicyHash: identifier(32, byte(40+index)),
		}); fault != nil {
			t.Fatal(fault)
		}
	}
	handle, err := localClient.StageAuditAnalysisSecret(session.SessionID, []byte("shared-password"))
	if err != nil || handle == "" {
		t.Fatalf("StageAuditAnalysisSecret = %q, %v", handle, err)
	}
	status, fault := localClient.CreateSecurityAnalysis(session.SessionID, SecurityAnalysisRequest{
		AnalysisTypes:        []string{"PASSWORD_REUSE", "HISTORICAL_USE"},
		SourceCheckpointHash: identifier(32, 50),
	})
	if fault != nil || status.State != "COMPLETED" ||
		status.ResultReference == "" {
		t.Fatalf("CreateSecurityAnalysis = %+v, %v", status, fault)
	}
	page, fault := localClient.ListSecurityFindings(
		session.SessionID, status.ResultReference, "", 2,
	)
	if fault != nil || len(page.Items) != 2 || page.NextCursor == "" {
		t.Fatalf("finding page = %+v, %v", page, fault)
	}
	for _, finding := range page.Items {
		if finding.CredentialPseudonym == "" || finding.Confidence != "STRONG" ||
			len(finding.EvidenceObjectDigests) == 0 {
			t.Fatalf("non-minimized finding = %+v", finding)
		}
	}
	next, fault := localClient.ListSecurityFindings(
		session.SessionID, status.ResultReference, page.NextCursor, 20,
	)
	if fault != nil || len(next.Items) != 2 {
		t.Fatalf("second finding page = %+v, %v", next, fault)
	}
	if _, fault := localClient.CreateSecurityAnalysis(session.SessionID, SecurityAnalysisRequest{
		AnalysisTypes:        []string{"PASSWORD_REUSE"},
		SourceCheckpointHash: identifier(32, 50),
	}); fault == nil || fault.Code != "SECRET_HANDLE_REJECTED" {
		t.Fatalf("analysis handle replay fault = %v", fault)
	}
}

func testLocalSecureClientAndSession(t *testing.T) (*LocalSecureClient, VaultSession) {
	t.Helper()
	master := []byte("localClient-fixture-master-input")
	localClient, err := NewLocalSecureClient(LocalSecureClientConfig{
		UnlockVerifier:   digestVerifier(sha256.Sum256(master)),
		RecoveryVerifier: recoveryDigestVerifier(sha256.Sum256([]byte("fixture-recovery-input"))),
	})
	if err != nil {
		t.Fatal(err)
	}
	deviceID := identifier(16, 4)
	handle, err := localClient.StageMasterPassword(deviceID, master)
	if err != nil {
		t.Fatal(err)
	}
	session, fault := localClient.CreateVaultSession(CreateVaultSessionRequest{
		DeviceID: deviceID, MasterPasswordHandle: handle,
	})
	if fault != nil {
		t.Fatal(fault)
	}
	return localClient, session
}

func identifier(size int, seed byte) string {
	value := make([]byte, size)
	for index := range value {
		value[index] = seed + byte(index)
	}
	return base64.RawURLEncoding.EncodeToString(value)
}

func digestVerifier(expected [sha256.Size]byte) func(string, *cryptokit.Secret) error {
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

func recoveryDigestVerifier(expected [sha256.Size]byte) func(string, string, *cryptokit.Secret) error {
	return func(_, _ string, secret *cryptokit.Secret) error {
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
