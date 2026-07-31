package application

import (
	"crypto/ed25519"
	"crypto/rand"
	"crypto/sha256"
	"errors"
	"testing"

	auditdomain "vdns.local/vdns/internal/audit/domain"
	credentialdomain "vdns.local/vdns/internal/credential/domain"
	"vdns.local/vdns/internal/cryptokit"
	operationdomain "vdns.local/vdns/internal/operation/domain"
	"vdns.local/vdns/internal/protocol"
	resolverdomain "vdns.local/vdns/internal/resolver/domain"
	transparencydomain "vdns.local/vdns/internal/transparency/domain"
)

type oneUseAnalysisHandle struct {
	secret   *cryptokit.Secret
	consumed bool
}

func (handle *oneUseAnalysisHandle) Consume(fn func(*cryptokit.Secret) error) error {
	if handle == nil || handle.secret == nil || handle.consumed || fn == nil {
		return ErrAuditHandleRejected
	}
	handle.consumed = true
	return fn(handle.secret)
}

func TestAuthorizedAnalysisPrecisionRecallAndResultMinimization(t *testing.T) {
	authorization := analysisAuthorizationFixture(t, protocol.CapabilityAuditAnalyze)
	tagShared := cryptokit.ReuseTag{9}
	tagUnique := cryptokit.ReuseTag{10}
	records := []AnalysisRecord{
		{
			CredentialID: protocol.CredentialID{1}, Version: 2, Epoch: 7,
			ObservedTimeBucket: 100, UpdatedTimeBucket: 10, Witness: tagShared,
			DeviceAuthorized: true, EvidenceDigests: [][32]byte{{1}, {2}},
		},
		{
			CredentialID: protocol.CredentialID{2}, Version: 1, Epoch: 7,
			ObservedTimeBucket: 101, UpdatedTimeBucket: 95, Witness: tagShared,
			DeviceAuthorized: false, RollbackObserved: true,
			ConflictObserved: true, EvidenceDigests: [][32]byte{{3}, {4}},
		},
		{
			CredentialID: protocol.CredentialID{3}, Version: 3, Epoch: 7,
			ObservedTimeBucket: 102, UpdatedTimeBucket: 90, Witness: tagUnique,
			DeviceAuthorized: true, EvidenceDigests: [][32]byte{{5}},
		},
	}
	authorization.TargetIDs = []protocol.CredentialID{
		records[0].CredentialID, records[1].CredentialID, records[2].CredentialID,
	}
	findings, err := RunAuthorizedAnalysis(AnalysisRequest{
		Authorization: authorization, Records: records,
		CurrentBucket: 110, StaleAfterBucket: 50, AnalysisSalt: [32]byte{88},
		DeriveWitness: func(epoch uint64, _ *cryptokit.Secret) (cryptokit.ReuseTag, error) {
			if epoch != 7 {
				return cryptokit.ReuseTag{}, ErrAuditAnalysis
			}
			return tagShared, nil
		},
	})
	if err != nil {
		t.Fatal(err)
	}
	counts := map[auditdomain.RiskKind]int{}
	for _, finding := range findings {
		counts[finding.Kind]++
		if finding.Confidence == auditdomain.ConfidenceWeak ||
			len(finding.EvidenceObjectDigests) == 0 {
			t.Fatalf("finding lacks evidence confidence: %+v", finding)
		}
	}
	want := map[auditdomain.RiskKind]int{
		auditdomain.RiskPasswordReuse:   2,
		auditdomain.RiskHistoricalUse:   2,
		auditdomain.RiskStaleCredential: 1,
		auditdomain.RiskAnomalousDevice: 1,
		auditdomain.RiskRollback:        1,
		auditdomain.RiskConflict:        1,
	}
	for kind, count := range want {
		if counts[kind] != count {
			t.Fatalf("kind %d count=%d want=%d (precision/recall mismatch)", kind, counts[kind], count)
		}
	}
	if !authorization.SecretHandle.(*oneUseAnalysisHandle).consumed {
		t.Fatal("one-use analysis handle was not consumed")
	}

	page, err := PaginateFindings(findings, "", 2, "analysis-1", [32]byte{77})
	if err != nil || len(page.Items) != 2 || page.NextCursor == "" {
		t.Fatalf("page 1 = %+v, %v", page, err)
	}
	next, err := PaginateFindings(findings, page.NextCursor, 200, "analysis-1", [32]byte{77})
	if err != nil || len(next.Items) != len(findings)-2 {
		t.Fatalf("page 2 = %+v, %v", next, err)
	}
	if _, err := PaginateFindings(findings, page.NextCursor+"x", 2, "analysis-1", [32]byte{77}); !errors.Is(err, ErrAuditCursor) {
		t.Fatalf("tampered cursor = %v", err)
	}
}

func TestPublishAuditDoesNotImplyAnalyzeAndHandleSurvivesDeniedRequest(t *testing.T) {
	authorization := analysisAuthorizationFixture(t, protocol.CapabilityPublishAudit)
	handle := authorization.SecretHandle.(*oneUseAnalysisHandle)
	err := AuthorizeAnalysis(authorization)
	if !errors.Is(err, ErrAuditAnalyzeDenied) {
		t.Fatalf("publish-only authorization = %v", err)
	}
	if handle.consumed {
		t.Fatal("denied request consumed secret handle")
	}
}

func TestAnalysisGateRejectsScopeGenerationProofAndMissingHandle(t *testing.T) {
	tests := []struct {
		name   string
		mutate func(*AnalysisAuthorization)
	}{
		{
			name: "scope",
			mutate: func(input *AnalysisAuthorization) {
				input.TargetIDs = []protocol.CredentialID{{9}}
			},
		},
		{
			name: "generation",
			mutate: func(input *AnalysisAuthorization) {
				input.SecretGeneration++
			},
		},
		{
			name: "proof bundle",
			mutate: func(input *AnalysisAuthorization) {
				input.Resolution.ProofDigest[0] ^= 1
			},
		},
		{
			name: "handle",
			mutate: func(input *AnalysisAuthorization) {
				input.SecretHandle = nil
			},
		},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			input := analysisAuthorizationFixture(t, protocol.CapabilityAuditAnalyze)
			test.mutate(&input)
			if err := AuthorizeAnalysis(input); !errors.Is(err, ErrAuditAnalyzeDenied) {
				t.Fatalf("AuthorizeAnalysis = %v", err)
			}
		})
	}
}

func analysisAuthorizationFixture(
	t *testing.T,
	capabilities protocol.Capability,
) AnalysisAuthorization {
	t.Helper()
	namespaceID := protocol.NamespaceID{1}
	deviceID := protocol.DeviceID{2}
	targetID := protocol.CredentialID{3}
	statusReference := sha256.Sum256([]byte("status"))
	_, rootPrivate, _ := ed25519.GenerateKey(rand.Reader)
	authPublic, _, _ := ed25519.GenerateKey(rand.Reader)
	hpkePublic, hpkePrivate, err := cryptokit.GenerateHPKEKeyPair()
	if err != nil {
		t.Fatal(err)
	}
	defer hpkePrivate.Destroy()
	scope, err := operationdomain.NewCredentialSetScope([]protocol.CredentialID{
		{1}, {2}, {3},
	})
	if err != nil {
		t.Fatal(err)
	}
	scopeDigest, _ := scope.Digest()
	credential, err := operationdomain.IssueDeviceOperationCredential(
		rootPrivate, "audit-chain", 1,
		operationdomain.DeviceOperationCredentialPayload{
			CredentialVersion: operationdomain.DeviceOperationCredentialVersion,
			NamespaceID:       namespaceID, DeviceID: deviceID,
			AuthPublicKey: [ed25519.PublicKeySize]byte(authPublic),
			HPKEPublicKey: hpkePublic, Capabilities: capabilities,
			Scope: scope, ScopeDigest: scopeDigest,
			ValidFromSequence: 1, ValidUntilSequence: 100,
			IssuanceCounter: 1, StatusReference: statusReference,
			SecretGeneration: 2,
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	subject := sha256.Sum256([]byte("analysis-operation"))
	leaf := transparencydomain.LogLeaf{
		NamespaceCommitment: [32]byte{1}, SubjectPseudonym: [32]byte{2},
		ObjectType: protocol.ObjectTypeAuditEvent, ObjectDigest: subject,
		OperationType: protocol.OperationAuditAnalyze,
		FinalSequence: 8, Epoch: 7,
	}
	bundleKey := ed25519.NewKeyFromSeed(make([]byte, ed25519.SeedSize))
	bundle, err := transparencydomain.SignProofBundle(
		bundleKey, "audit-chain", 1,
		transparencydomain.ProofBundlePayload{
			NamespaceID: namespaceID, SubjectDigest: subject,
			LeafIndex: 0, Leaf: leaf,
			StartingCheckpointObject: []byte{1},
			CandidateTreeHeadObject:  []byte{2},
			RootChainObjects:         [][]byte{{3}},
			DeviceCredentialObject:   []byte{4},
			CapabilityStatusProof:    [][32]byte{{5}},
			StateDescriptorDigest:    [32]byte{6},
			LocalPolicyInputHash:     [32]byte{7},
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	layers := [5]resolverdomain.LayerResult{}
	for index := range layers {
		layers[index] = resolverdomain.LayerResult{
			Layer: resolverdomain.Layer(index + 1), Passed: true, Code: resolverdomain.CodeOK,
		}
	}
	secret, _ := cryptokit.NewSecret([]byte("candidate-password"))
	t.Cleanup(secret.Destroy)
	return AnalysisAuthorization{
		Resolution: resolverdomain.Resolution{
			State: credentialdomain.StateDescriptorPayload{LastOperationEvent: subject},
			Principal: resolverdomain.Principal{
				NamespaceID: namespaceID, DeviceID: deviceID,
				DeviceCredentialHash: credential.Digest(), SecretGeneration: 2,
			},
			Authorization: resolverdomain.Authorization{
				Operation:    protocol.OperationAuditAnalyze,
				Capabilities: capabilities, ScopeDigest: scopeDigest,
				FinalSequence: 8, IssuanceCounter: 1,
			},
			ProofDigest: bundle.Digest(), Verdict: protocol.VerdictAccept,
			Layers: layers,
		},
		DeviceCredential: credential, ProofBundle: bundle,
		TargetIDs: []protocol.CredentialID{targetID}, SecretGeneration: 2,
		SecretHandle: &oneUseAnalysisHandle{secret: secret},
	}
}
