package application

import (
	"bytes"
	"crypto/ed25519"
	"crypto/sha256"
	"sort"
	"testing"
	"time"

	anchordomain "vdns.local/vdns/internal/anchor/domain"
	credentialdomain "vdns.local/vdns/internal/credential/domain"
	"vdns.local/vdns/internal/cryptokit"
	finalorderdomain "vdns.local/vdns/internal/finalorder/domain"
	operationdomain "vdns.local/vdns/internal/operation/domain"
	"vdns.local/vdns/internal/protocol"
	resolverdomain "vdns.local/vdns/internal/resolver/domain"
	transparencydomain "vdns.local/vdns/internal/transparency/domain"
)

func TestL1L2L3CreateAndNegativeMatrix(t *testing.T) {
	fixture := newCreateFixture(t)
	identity, layer, err := VerifyL1(fixture.l1)
	if err != nil || !layer.Passed {
		t.Fatalf("L1 = %+v, %v", layer, err)
	}
	l2Input := L2Input{
		Identity: identity, Operation: protocol.OperationCreate,
		CredentialID: &fixture.credentialID, FinalSequence: 10,
		CurrentIssuanceCounter: fixture.credentialPayload.IssuanceCounter,
		CurrentStatusReference: fixture.credentialPayload.StatusReference,
	}
	authorization, layer, err := VerifyL2(l2Input)
	if err != nil || !layer.Passed ||
		authorization.Operation != protocol.OperationCreate {
		t.Fatalf("L2 = %+v, %+v, %v", authorization, layer, err)
	}
	layer, err = VerifyL3(identity, TrustedDynamicState{
		CurrentSecretGeneration: fixture.credentialPayload.SecretGeneration,
		AcceptedDeviceCounter:   0,
		CandidateFinalSequence:  10,
	})
	if err != nil || !layer.Passed {
		t.Fatalf("L3 = %+v, %v", layer, err)
	}
	orderKey := fixedKey(0x32)
	orderPublicKey := orderKey.Public().(ed25519.PublicKey)
	orderKeyID := sha256.Sum256(orderPublicKey)
	orderedObject := fillHash(0x33)
	receipt, err := finalorderdomain.SignReceipt(
		orderKey,
		finalorderdomain.FinalOrderReceiptPayload{
			Domain:     protocol.DomainPrefix + "FINAL-ORDER-RECEIPT",
			ProtocolID: protocol.ProtocolID, ProtocolVersion: protocol.ProtocolVersion,
			SuiteID: protocol.SuiteID, AdapterKind: finalorderdomain.AdapterKind,
			NamespaceID: fixture.l1.NamespaceID, CredentialID: fixture.credentialID,
			OrderedObjectDigest: orderedObject, FinalSequence: 10,
			AuthorityKeyID: orderKeyID, AuthorityKeyGeneration: 1,
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	layer, err = VerifyL3(identity, TrustedDynamicState{
		CurrentSecretGeneration: fixture.credentialPayload.SecretGeneration,
		AcceptedDeviceCounter:   0,
		CandidateFinalSequence:  10,
		FinalOrder: FinalOrderTrust{
			Required: true, Receipt: &receipt, AuthorityPublicKey: orderPublicKey,
			AuthorityKeyID: orderKeyID, AuthorityKeyGeneration: 1,
			OrderedObjectDigest: orderedObject,
		},
	})
	if err != nil || !layer.Passed {
		t.Fatalf("L3 final order = %+v, %v", layer, err)
	}
	tamperedReceipt := receipt
	tamperedReceipt.Signature[0] ^= 1
	if result, verifyErr := VerifyL3(identity, TrustedDynamicState{
		CurrentSecretGeneration: fixture.credentialPayload.SecretGeneration,
		AcceptedDeviceCounter:   0,
		CandidateFinalSequence:  10,
		FinalOrder: FinalOrderTrust{
			Required: true, Receipt: &tamperedReceipt,
			AuthorityPublicKey: orderPublicKey, AuthorityKeyID: orderKeyID,
			AuthorityKeyGeneration: 1, OrderedObjectDigest: orderedObject,
		},
	}); verifyErr == nil || result.Code != resolverdomain.CodeStateFinalOrder {
		t.Fatalf("tampered final order result = %+v, %v", result, verifyErr)
	}
	if result, verifyErr := VerifyL3(identity, TrustedDynamicState{
		CurrentSecretGeneration: fixture.credentialPayload.SecretGeneration,
		AcceptedDeviceCounter:   0, CandidateFinalSequence: 10,
		ConflictDetected: true,
	}); verifyErr == nil || result.Code != resolverdomain.CodeStateConflict {
		t.Fatalf("conflict result = %+v, %v", result, verifyErr)
	}

	badL1 := fixture.l1
	badL1.RootKeyGeneration++
	if _, result, err := VerifyL1(badL1); err == nil || result.Passed {
		t.Fatal("wrong root key generation accepted")
	}
	badSignature := fixture.l1
	badSignature.EventSignature[0] ^= 0x80
	if _, result, err := VerifyL1(badSignature); err == nil || result.Passed {
		t.Fatal("bad event signature accepted")
	}

	l2Cases := []struct {
		name string
		code resolverdomain.ReasonCode
		edit func(*L2Input)
	}{
		{"operation", resolverdomain.CodeCapabilityOperation, func(value *L2Input) {
			value.Operation = protocol.OperationRevoke
		}},
		{"scope", resolverdomain.CodeCapabilityScope, func(value *L2Input) {
			other := fillCredentialID(0xee)
			value.CredentialID = &other
		}},
		{"sequence", resolverdomain.CodeCapabilitySequence, func(value *L2Input) {
			value.FinalSequence = 101
		}},
		{"issuance", resolverdomain.CodeCapabilityCounter, func(value *L2Input) {
			value.CurrentIssuanceCounter++
		}},
		{"status", resolverdomain.CodeCapabilityStatus, func(value *L2Input) {
			value.CurrentStatusReference[0] ^= 1
		}},
	}
	for _, test := range l2Cases {
		t.Run("L2/"+test.name, func(t *testing.T) {
			candidate := l2Input
			test.edit(&candidate)
			if _, result, err := VerifyL2(candidate); err == nil ||
				result.Code != test.code {
				t.Fatalf("result = %+v, %v", result, err)
			}
		})
	}

	revoked := uint64(10)
	if result, err := VerifyL3(identity, TrustedDynamicState{
		CurrentSecretGeneration: fixture.credentialPayload.SecretGeneration,
		RevokedAtSequence:       &revoked,
		AcceptedDeviceCounter:   0,
		CandidateFinalSequence:  10,
	}); err == nil || result.Code != resolverdomain.CodeStateRevoked {
		t.Fatalf("revocation result = %+v, %v", result, err)
	}
	if result, err := VerifyL3(identity, TrustedDynamicState{
		CurrentSecretGeneration: fixture.credentialPayload.SecretGeneration,
		AcceptedDeviceCounter:   1,
		CandidateFinalSequence:  10,
	}); err == nil || result.Code != resolverdomain.CodeStateCounter {
		t.Fatalf("counter result = %+v, %v", result, err)
	}
	previous := sha256.Sum256([]byte("unexpected predecessor"))
	if result, err := VerifyL3(identity, TrustedDynamicState{
		CurrentSecretGeneration: fixture.credentialPayload.SecretGeneration,
		AcceptedDeviceCounter:   0,
		PreviousEventHash:       &previous,
		CandidateFinalSequence:  10,
	}); err == nil || result.Code != resolverdomain.CodeStatePredecessor {
		t.Fatalf("predecessor result = %+v, %v", result, err)
	}
}

func TestL4ProofBundleAndL5PolicyMatrix(t *testing.T) {
	namespace := fillNamespace(0x31)
	tree := transparencydomain.NewTree()
	leaves := make([]transparencydomain.LogLeaf, 7)
	for index := range leaves {
		leaves[index] = publicLeaf(byte(index+1), uint64(index+1))
		if index == 6 {
			leaves[index].ObjectType = protocol.ObjectTypeStateDescriptor
		}
		if _, _, err := tree.Append(leaves[index]); err != nil {
			t.Fatal(err)
		}
	}
	oldRoot, _ := tree.RootAt(3)
	checkpointKey := fixedKey(0x41)
	checkpoint, err := anchordomain.SignCheckpoint(
		checkpointKey, "resolver-chain", 2,
		anchordomain.CheckpointPayload{
			NamespaceID:         namespace,
			NamespaceStateRoot:  fillHash(1),
			DeviceStateRoot:     fillHash(2),
			CredentialStateRoot: fillHash(3),
			AuditLogRoot:        oldRoot,
			RevocationRoot:      fillHash(5),
			CryptoPolicyHash:    fillHash(6),
			CheckpointHeight:    3,
			FinalSequence:       3,
			ProviderKind:        anchordomain.ProviderSimulated,
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	checkpointObject, _ := checkpoint.MarshalBinary()
	logKey := fixedKey(0x51)
	head, err := transparencydomain.SignTreeHead(
		logKey, "resolver-chain", 4,
		transparencydomain.TreeHeadPayload{
			NamespaceID: namespace, LogID: transparencydomain.LogID{1, 2, 3},
			TreeSize: 7, RootHash: tree.Root(), FinalSequence: 7,
			SuiteID: protocol.SuiteID,
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	headObject, _ := head.MarshalBinary()
	inclusion, _ := tree.InclusionProof(6, 7)
	consistency, _ := tree.ConsistencyProof(3, 7)
	bundleKey := fixedKey(0x61)
	rootChainObjects := [][]byte{{1, 2, 3}}
	deviceCredentialObject := []byte{4, 5, 6}
	bundle, err := transparencydomain.SignProofBundle(
		bundleKey, "resolver-chain", 5,
		transparencydomain.ProofBundlePayload{
			NamespaceID:   namespace,
			SubjectDigest: leaves[6].ObjectDigest,
			LeafIndex:     6, Leaf: leaves[6],
			StartingCheckpointObject: checkpointObject,
			CandidateTreeHeadObject:  headObject,
			InclusionProof:           inclusion, ConsistencyProof: consistency,
			RootChainObjects:       rootChainObjects,
			DeviceCredentialObject: deviceCredentialObject,
			CapabilityStatusProof:  [][32]byte{fillHash(7)},
			StateDescriptorDigest:  leaves[6].ObjectDigest,
			LocalPolicyInputHash:   fillHash(9),
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	trust := L4Trust{
		ChainID: "resolver-chain", NamespaceID: namespace,
		BundlePublicKey:                    bundleKey.Public().(ed25519.PublicKey),
		BundleKeyGeneration:                5,
		CheckpointPublicKey:                checkpointKey.Public().(ed25519.PublicKey),
		CheckpointKeyGeneration:            2,
		LogPublicKey:                       logKey.Public().(ed25519.PublicKey),
		LogKeyGeneration:                   4,
		TrustedCheckpointDigest:            checkpoint.Digest(),
		RequiredProviderKind:               anchordomain.ProviderSimulated,
		ExpectedSubjectDigest:              leaves[6].ObjectDigest,
		ExpectedFinalSequence:              leaves[6].FinalSequence,
		ExpectedRootChainDigest:            mustRootChainDigest(t, rootChainObjects),
		ExpectedDeviceCredentialObjectHash: sha256.Sum256(deviceCredentialObject),
	}
	bundlePayload := bundle.Payload()
	bundleRootChainDigest, _ := transparencydomain.RootChainDigest(
		bundlePayload.RootChainObjects,
	)
	if bundlePayload.SubjectDigest != trust.ExpectedSubjectDigest ||
		bundlePayload.StateDescriptorDigest != trust.ExpectedSubjectDigest ||
		bundlePayload.Leaf.ObjectType != protocol.ObjectTypeStateDescriptor ||
		bundleRootChainDigest != trust.ExpectedRootChainDigest ||
		sha256.Sum256(bundlePayload.DeviceCredentialObject) !=
			trust.ExpectedDeviceCredentialObjectHash {
		t.Fatalf(
			"L4 identity/root proof mismatch subject=%v descriptor=%v type=%v root=%v device=%v",
			bundlePayload.SubjectDigest == trust.ExpectedSubjectDigest,
			bundlePayload.StateDescriptorDigest == trust.ExpectedSubjectDigest,
			bundlePayload.Leaf.ObjectType == protocol.ObjectTypeStateDescriptor,
			bundleRootChainDigest == trust.ExpectedRootChainDigest,
			sha256.Sum256(bundlePayload.DeviceCredentialObject) ==
				trust.ExpectedDeviceCredentialObjectHash,
		)
	}
	audit, _, layer, err := VerifyL4(
		bundle.SigInputCBOR(), bundle.Signature(), trust,
	)
	if err != nil || !layer.Passed || !audit.PendingAnchor ||
		audit.TreeSize != 7 || audit.ProofBytes == 0 {
		t.Fatalf("L4 = %+v, %+v, %v", audit, layer, err)
	}
	badSignature := bundle.Signature()
	badSignature[0] ^= 1
	if _, _, result, err := VerifyL4(
		bundle.SigInputCBOR(), badSignature, trust,
	); err == nil || result.Code != resolverdomain.CodeProofBundle {
		t.Fatalf("mutated bundle result = %+v, %v", result, err)
	}
	for _, mutate := range []func(*transparencydomain.ProofBundlePayload){
		func(payload *transparencydomain.ProofBundlePayload) {
			payload.RootChainObjects[0][0] ^= 1
		},
		func(payload *transparencydomain.ProofBundlePayload) {
			payload.DeviceCredentialObject[0] ^= 1
		},
	} {
		maliciousPayload := bundle.Payload()
		mutate(&maliciousPayload)
		malicious, signErr := transparencydomain.SignProofBundle(
			bundleKey, "resolver-chain", 5, maliciousPayload,
		)
		if signErr != nil {
			t.Fatal(signErr)
		}
		if _, _, result, verifyErr := VerifyL4(
			malicious.SigInputCBOR(), malicious.Signature(), trust,
		); verifyErr == nil || result.Code != resolverdomain.CodeProofBundle {
			t.Fatalf("mismatched identity proof result = %+v, %v", result, verifyErr)
		}
	}
	requireAnchor := trust
	requireAnchor.RequireCandidateAnchor = true
	if _, _, result, err := VerifyL4(
		bundle.SigInputCBOR(), bundle.Signature(), requireAnchor,
	); err == nil || result.Code != resolverdomain.CodeProofAnchor {
		t.Fatalf("required anchor result = %+v, %v", result, err)
	}

	policyCases := []struct {
		name  string
		input PolicyInput
		want  protocol.Verdict
	}{
		{"online", PolicyInput{
			Operation: protocol.OperationResolve, NetworkAvailable: true,
			L4Available: true,
		}, protocol.VerdictAccept},
		{"offline read", PolicyInput{
			Operation: protocol.OperationResolve, HasAcceptedCache: true,
			MaxOfflineCacheAge: 10, CacheAgeSequences: 2,
		}, protocol.VerdictDegradedOffline},
		{"pending autofill", PolicyInput{
			Operation: protocol.OperationAutofill, NetworkAvailable: true,
			L4Available: true, PendingAnchor: true, HasAcceptedCache: true,
			MaxOfflineCacheAge: 10, CacheAgeSequences: 2,
		}, protocol.VerdictDegradedPendingLog},
		{"offline write", PolicyInput{
			Operation: protocol.OperationUpdatePrepare, HasAcceptedCache: true,
			MaxOfflineCacheAge: 10,
		}, protocol.VerdictRejectPolicy},
		{"expired cache", PolicyInput{
			Operation: protocol.OperationResolve, HasAcceptedCache: true,
			MaxOfflineCacheAge: 10, CacheAgeSequences: 11,
		}, protocol.VerdictRejectPolicy},
		{"review", PolicyInput{
			Operation: protocol.OperationResolve, UserReviewRequired: true,
		}, protocol.VerdictReviewRequired},
	}
	for _, test := range policyCases {
		t.Run("L5/"+test.name, func(t *testing.T) {
			got, _ := EvaluateL5(test.input)
			if got != test.want {
				t.Fatalf("verdict = %v, want %v", got, test.want)
			}
		})
	}
}

func TestResolverSelectsVDNSCurrentState(t *testing.T) {
	fixture := newCreateFixture(t)
	bundle, trust := proofForCreateFixture(t, fixture)
	request := ResolveRequest{
		L1: fixture.l1,
		L2: L2Input{
			Operation:              protocol.OperationCreate,
			CredentialID:           &fixture.credentialID,
			FinalSequence:          10,
			CurrentIssuanceCounter: fixture.credentialPayload.IssuanceCounter,
			CurrentStatusReference: fixture.credentialPayload.StatusReference,
		},
		Dynamic: TrustedDynamicState{
			CurrentSecretGeneration: fixture.credentialPayload.SecretGeneration,
			AcceptedDeviceCounter:   0,
			CandidateFinalSequence:  10,
		},
		ProofAvailable:  true,
		BundleSigInput:  bundle.SigInputCBOR(),
		BundleSignature: bundle.Signature(),
		L4Trust:         trust,
		Policy:          PolicyInput{NetworkAvailable: true},
	}
	resolution, err := Resolve(request)
	if err != nil {
		t.Fatal(err)
	}
	if resolution.Verdict != protocol.VerdictAccept ||
		resolution.CurrentVersion != 1 ||
		resolution.State.ActiveEnvelopeHash != fillHash(0x71) ||
		resolution.Principal.DeviceID != fixture.credentialPayload.DeviceID ||
		resolution.Authorization.Operation != protocol.OperationCreate ||
		resolution.Audit.TreeSize != 1 ||
		resolution.ProofDigest != bundle.Digest() {
		t.Fatalf("resolution = %+v", resolution)
	}
	for index, layer := range resolution.Layers {
		if !layer.Passed {
			t.Fatalf("layer %d = %+v", index+1, layer)
		}
	}

	bad := request
	bad.BundleSignature[0] ^= 1
	rejected, err := Resolve(bad)
	if err == nil || rejected.Verdict != protocol.VerdictRejectProof {
		t.Fatalf("bad proof resolution = %+v, %v", rejected, err)
	}
	if rejected.CurrentVersion != 0 ||
		rejected.Principal != (resolverdomain.Principal{}) ||
		rejected.Authorization != (resolverdomain.Authorization{}) ||
		rejected.Audit != (resolverdomain.AuditProof{}) {
		t.Fatalf("rejected result exposed partial projections: %+v", rejected)
	}
}

func TestLifecycleEdgeTable(t *testing.T) {
	tests := []struct {
		name                             string
		current, candidate               protocol.LifecycleStatus
		currentVersion, candidateVersion uint64
		want                             bool
	}{
		{"active use", protocol.LifecycleActive, protocol.LifecycleActive, 2, 2, true},
		{"prepare", protocol.LifecycleActive, protocol.LifecycleUpdatePending, 2, 2, true},
		{"site pending", protocol.LifecycleUpdatePending, protocol.LifecycleSiteConfirmPending, 2, 2, true},
		{"activate next", protocol.LifecycleSiteConfirmPending, protocol.LifecycleActive, 2, 3, true},
		{"suspend revoke", protocol.LifecycleSuspended, protocol.LifecycleRevoked, 2, 2, true},
		{"direct revoke", protocol.LifecycleActive, protocol.LifecycleRevoked, 2, 2, false},
		{"rollback", protocol.LifecycleSiteConfirmPending, protocol.LifecycleActive, 2, 1, false},
		{"skip version", protocol.LifecycleSiteConfirmPending, protocol.LifecycleActive, 2, 4, false},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			if got := lifecycleAllows(
				test.current, test.candidate,
				test.currentVersion, test.candidateVersion,
			); got != test.want {
				t.Fatalf("lifecycleAllows = %v, want %v", got, test.want)
			}
		})
	}
}

func TestEventVersionBinding(t *testing.T) {
	versionOne := uint64(1)
	oldVersion := uint64(2)
	newVersion := uint64(3)
	versionFour := uint64(4)
	tests := []struct {
		name     string
		event    operationdomain.Payload
		accepted uint64
		want     bool
	}{
		{"create", operationdomain.Payload{
			OperationType: protocol.OperationCreate, NewVersion: &versionOne,
		}, 0, true},
		{"create wrong version", operationdomain.Payload{
			OperationType: protocol.OperationCreate, NewVersion: &newVersion,
		}, 0, false},
		{"prepare", operationdomain.Payload{
			OperationType: protocol.OperationUpdatePrepare,
			OldVersion:    &oldVersion, NewVersion: &newVersion,
		}, 2, true},
		{"prepare skip", operationdomain.Payload{
			OperationType: protocol.OperationUpdatePrepare,
			OldVersion:    &oldVersion, NewVersion: &versionFour,
		}, 2, false},
		{"read current", operationdomain.Payload{
			OperationType: protocol.OperationResolve, OldVersion: &oldVersion,
		}, 2, true},
		{"read mutates", operationdomain.Payload{
			OperationType: protocol.OperationResolve, NewVersion: &newVersion,
		}, 2, false},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			if got := eventVersionAllows(test.event, test.accepted); got != test.want {
				t.Fatalf("eventVersionAllows = %v, want %v", got, test.want)
			}
		})
	}
}

type createFixture struct {
	l1                L1Input
	credentialID      protocol.CredentialID
	credentialPayload operationdomain.DeviceOperationCredentialPayload
	deviceCredential  *operationdomain.SignedDeviceOperationCredential
	descriptor        *credentialdomain.SignedStateDescriptor
}

func newCreateFixture(t testing.TB) createFixture {
	t.Helper()
	rootKey := fixedKey(0x11)
	deviceKey := fixedKey(0x21)
	namespace := fillNamespace(0x31)
	deviceID := fillDevice(0x41)
	credentialID := fillCredentialID(0x51)
	scope, err := operationdomain.NewSingleCredentialScope(credentialID)
	if err != nil {
		t.Fatal(err)
	}
	scopeDigest, _ := scope.Digest()
	hpkePublic, hpkePrivate, err := cryptokit.GenerateHPKEKeyPair()
	if err != nil {
		t.Fatal(err)
	}
	defer hpkePrivate.Destroy()
	var authPublic [ed25519.PublicKeySize]byte
	copy(authPublic[:], deviceKey.Public().(ed25519.PublicKey))
	payload := operationdomain.DeviceOperationCredentialPayload{
		CredentialVersion: operationdomain.DeviceOperationCredentialVersion,
		NamespaceID:       namespace, DeviceID: deviceID,
		AuthPublicKey: authPublic, HPKEPublicKey: hpkePublic,
		Capabilities: protocol.CapabilityCreate |
			protocol.CapabilityRead | protocol.CapabilityAutofill,
		Scope: scope, ScopeDigest: scopeDigest,
		ValidFromSequence: 1, ValidUntilSequence: 100,
		IssuanceCounter:  2,
		StatusReference:  sha256.Sum256([]byte("active status")),
		SecretGeneration: 3,
	}
	deviceCredential, err := operationdomain.IssueDeviceOperationCredential(
		rootKey, "resolver-chain", 2, payload,
	)
	if err != nil {
		t.Fatal(err)
	}
	newVersion := uint64(1)
	eventPayload := operationdomain.Payload{
		EventID: fillEvent(0x61), NamespaceID: namespace, DeviceID: deviceID,
		DeviceCredentialHash: deviceCredential.Digest(),
		CredentialID:         &credentialID, OperationType: protocol.OperationCreate,
		NewVersion:       &newVersion,
		DevicePseudonym:  [16]byte{1, 2, 3},
		EventPayloadHash: sha256.Sum256([]byte("event payload")),
		SecretGeneration: 3, DeviceCounter: 1,
	}
	event, err := operationdomain.Sign(deviceKey, "resolver-chain", 3, eventPayload)
	if err != nil {
		t.Fatal(err)
	}
	descriptor, err := credentialdomain.SignStateDescriptor(
		deviceKey, "resolver-chain", 3,
		credentialdomain.StateDescriptorPayload{
			NamespaceID: namespace, CredentialID: credentialID,
			ActiveVersion: 1, ActiveEnvelopeHash: fillHash(0x71),
			LifecycleStatus:      protocol.LifecycleActive,
			LastOperationEvent:   event.Digest(),
			AuthorizedDeviceRoot: fillHash(0x72),
			AuditCheckpoint:      fillHash(0x73),
			FinalSequence:        10, UpdaterDeviceID: deviceID,
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	return createFixture{
		l1: L1Input{
			ChainID: "resolver-chain", NamespaceID: namespace,
			RootPublicKey:             rootKey.Public().(ed25519.PublicKey),
			RootKeyGeneration:         2,
			DeviceCredentialSigInput:  deviceCredential.SigInputCBOR(),
			DeviceCredentialSignature: deviceCredential.Signature(),
			EventSigInput:             event.SigInputCBOR(), EventSignature: event.Signature(),
			DescriptorSigInput:  descriptor.SigInputCBOR(),
			DescriptorSignature: descriptor.Signature(),
		},
		credentialID: credentialID, credentialPayload: payload,
		deviceCredential: deviceCredential, descriptor: descriptor,
	}
}

func proofForCreateFixture(
	t testing.TB,
	fixture createFixture,
) (*transparencydomain.SignedProofBundle, L4Trust) {
	t.Helper()
	namespace := fixture.credentialPayload.NamespaceID
	leaf := transparencydomain.LogLeaf{
		NamespaceCommitment: fillHash(0x81),
		SubjectPseudonym:    fillHash(0x82),
		ObjectType:          protocol.ObjectTypeStateDescriptor,
		ObjectDigest:        fixture.descriptor.Digest(),
		OperationType:       protocol.OperationCreate,
		FinalSequence:       10, Epoch: 1,
	}
	tree := transparencydomain.NewTree()
	if _, _, err := tree.Append(leaf); err != nil {
		t.Fatal(err)
	}
	checkpointKey := fixedKey(0x91)
	checkpoint, err := anchordomain.SignCheckpoint(
		checkpointKey, "resolver-chain", 4,
		anchordomain.CheckpointPayload{
			NamespaceID:         namespace,
			NamespaceStateRoot:  fillHash(1),
			DeviceStateRoot:     fillHash(2),
			CredentialStateRoot: fillHash(3),
			AuditLogRoot:        tree.Root(),
			RevocationRoot:      fillHash(5),
			CryptoPolicyHash:    fillHash(6),
			CheckpointHeight:    1, FinalSequence: 10,
			ProviderKind: anchordomain.ProviderSimulated,
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	checkpointObject, _ := checkpoint.MarshalBinary()
	logKey := fixedKey(0xa1)
	head, err := transparencydomain.SignTreeHead(
		logKey, "resolver-chain", 5,
		transparencydomain.TreeHeadPayload{
			NamespaceID: namespace, LogID: transparencydomain.LogID{8, 9, 10},
			TreeSize: 1, RootHash: tree.Root(), FinalSequence: 10,
			SuiteID: protocol.SuiteID,
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	headObject, _ := head.MarshalBinary()
	bundleKey := fixedKey(0xb1)
	rootTrustObject, err := encodeRootTrustObject(fixture.l1)
	if err != nil {
		t.Fatal(err)
	}
	deviceCredentialObject, err := fixture.deviceCredential.MarshalBinary()
	if err != nil {
		t.Fatal(err)
	}
	bundle, err := transparencydomain.SignProofBundle(
		bundleKey, "resolver-chain", 6,
		transparencydomain.ProofBundlePayload{
			NamespaceID:   namespace,
			SubjectDigest: fixture.descriptor.Digest(),
			LeafIndex:     0, Leaf: leaf,
			StartingCheckpointObject: checkpointObject,
			CandidateTreeHeadObject:  headObject,
			RootChainObjects:         [][]byte{rootTrustObject},
			DeviceCredentialObject:   deviceCredentialObject,
			CapabilityStatusProof:    [][32]byte{fillHash(7)},
			StateDescriptorDigest:    fixture.descriptor.Digest(),
			LocalPolicyInputHash:     fillHash(9),
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	return bundle, L4Trust{
		ChainID: "resolver-chain", NamespaceID: namespace,
		BundlePublicKey:         bundleKey.Public().(ed25519.PublicKey),
		BundleKeyGeneration:     6,
		CheckpointPublicKey:     checkpointKey.Public().(ed25519.PublicKey),
		CheckpointKeyGeneration: 4,
		LogPublicKey:            logKey.Public().(ed25519.PublicKey),
		LogKeyGeneration:        5,
		TrustedCheckpointDigest: checkpoint.Digest(),
		RequiredProviderKind:    anchordomain.ProviderSimulated,
	}
}

func resolveRequestAt100K(t testing.TB) (ResolveRequest, int, int) {
	t.Helper()
	fixture := newCreateFixture(t)
	namespace := fixture.credentialPayload.NamespaceID
	tree := transparencydomain.NewTree()
	for index := 0; index < 99_999; index++ {
		marker := byte((index % 200) + 1)
		if _, _, err := tree.Append(publicLeaf(marker, uint64(index+1))); err != nil {
			t.Fatal(err)
		}
	}
	target := transparencydomain.LogLeaf{
		NamespaceCommitment: fillHash(0xc1),
		SubjectPseudonym:    fillHash(0xc2),
		ObjectType:          protocol.ObjectTypeStateDescriptor,
		ObjectDigest:        fixture.descriptor.Digest(),
		OperationType:       protocol.OperationCreate,
		FinalSequence:       10, Epoch: 1,
	}
	if _, _, err := tree.Append(target); err != nil {
		t.Fatal(err)
	}
	root := tree.Root()
	inclusion, err := tree.InclusionProof(99_999, 100_000)
	if err != nil {
		t.Fatal(err)
	}
	if len(inclusion) > 32 {
		t.Fatalf("100k proof hash count = %d", len(inclusion))
	}
	checkpointKey := fixedKey(0xd1)
	checkpoint, err := anchordomain.SignCheckpoint(
		checkpointKey, "resolver-chain", 4,
		anchordomain.CheckpointPayload{
			NamespaceID:        namespace,
			NamespaceStateRoot: fillHash(1), DeviceStateRoot: fillHash(2),
			CredentialStateRoot: fillHash(3), AuditLogRoot: root,
			RevocationRoot: fillHash(5), CryptoPolicyHash: fillHash(6),
			CheckpointHeight: 100_000, FinalSequence: 10,
			ProviderKind: anchordomain.ProviderSimulated,
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	checkpointObject, _ := checkpoint.MarshalBinary()
	logKey := fixedKey(0xe1)
	head, err := transparencydomain.SignTreeHead(
		logKey, "resolver-chain", 5,
		transparencydomain.TreeHeadPayload{
			NamespaceID: namespace, LogID: transparencydomain.LogID{1, 2, 3},
			TreeSize: 100_000, RootHash: root, FinalSequence: 10,
			SuiteID: protocol.SuiteID,
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	headObject, _ := head.MarshalBinary()
	bundleKey := fixedKey(0xf1)
	rootTrustObject, err := encodeRootTrustObject(fixture.l1)
	if err != nil {
		t.Fatal(err)
	}
	deviceCredentialObject, err := fixture.deviceCredential.MarshalBinary()
	if err != nil {
		t.Fatal(err)
	}
	bundle, err := transparencydomain.SignProofBundle(
		bundleKey, "resolver-chain", 6,
		transparencydomain.ProofBundlePayload{
			NamespaceID:   namespace,
			SubjectDigest: fixture.descriptor.Digest(),
			LeafIndex:     99_999, Leaf: target,
			StartingCheckpointObject: checkpointObject,
			CandidateTreeHeadObject:  headObject,
			InclusionProof:           inclusion,
			RootChainObjects:         [][]byte{rootTrustObject},
			DeviceCredentialObject:   deviceCredentialObject,
			CapabilityStatusProof:    [][32]byte{fillHash(7)},
			StateDescriptorDigest:    fixture.descriptor.Digest(),
			LocalPolicyInputHash:     fillHash(9),
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	request := ResolveRequest{
		L1: fixture.l1,
		L2: L2Input{
			Operation:    protocol.OperationCreate,
			CredentialID: &fixture.credentialID, FinalSequence: 10,
			CurrentIssuanceCounter: fixture.credentialPayload.IssuanceCounter,
			CurrentStatusReference: fixture.credentialPayload.StatusReference,
		},
		Dynamic: TrustedDynamicState{
			CurrentSecretGeneration: fixture.credentialPayload.SecretGeneration,
			AcceptedDeviceCounter:   0, CandidateFinalSequence: 10,
		},
		ProofAvailable:  true,
		BundleSigInput:  bundle.SigInputCBOR(),
		BundleSignature: bundle.Signature(),
		L4Trust: L4Trust{
			ChainID: "resolver-chain", NamespaceID: namespace,
			BundlePublicKey:         bundleKey.Public().(ed25519.PublicKey),
			BundleKeyGeneration:     6,
			CheckpointPublicKey:     checkpointKey.Public().(ed25519.PublicKey),
			CheckpointKeyGeneration: 4,
			LogPublicKey:            logKey.Public().(ed25519.PublicKey),
			LogKeyGeneration:        5,
			TrustedCheckpointDigest: checkpoint.Digest(),
			RequiredProviderKind:    anchordomain.ProviderSimulated,
		},
		Policy: PolicyInput{NetworkAvailable: true},
	}
	proofHashes := len(inclusion)
	proofBytes := len(bundle.SigInputCBOR())
	return request, proofHashes, proofBytes
}

func TestResolveL1L5P95At100KLeaves(t *testing.T) {
	request, proofHashes, proofBytes := resolveRequestAt100K(t)
	const samples = 101
	durations := make([]time.Duration, samples)
	for index := range durations {
		started := time.Now()
		resolution, err := Resolve(request)
		durations[index] = time.Since(started)
		if err != nil || resolution.Verdict != protocol.VerdictAccept {
			t.Fatalf("Resolve = %+v, %v", resolution, err)
		}
	}
	sort.Slice(durations, func(left, right int) bool {
		return durations[left] < durations[right]
	})
	p95 := durations[(samples*95+99)/100-1]
	t.Logf(
		"100k L1-L5 samples=%d p95=%s proof_bytes=%d proof_hashes=%d",
		samples, p95, proofBytes, proofHashes,
	)
	if p95 > 25*time.Millisecond {
		t.Fatalf("100k L1-L5 p95 = %s, limit 25ms", p95)
	}
}

func BenchmarkResolveL1L5At100KLeaves(b *testing.B) {
	request, proofHashes, proofBytes := resolveRequestAt100K(b)
	b.ResetTimer()
	for index := 0; index < b.N; index++ {
		resolution, err := Resolve(request)
		if err != nil || resolution.Verdict != protocol.VerdictAccept {
			b.Fatalf("Resolve = %+v, %v", resolution, err)
		}
	}
	b.ReportMetric(float64(proofHashes), "proof_hashes")
	b.ReportMetric(float64(proofBytes), "proof_bytes")
}

func fixedKey(marker byte) ed25519.PrivateKey {
	return ed25519.NewKeyFromSeed(bytes.Repeat([]byte{marker}, ed25519.SeedSize))
}

func fillNamespace(marker byte) protocol.NamespaceID {
	var value protocol.NamespaceID
	for index := range value {
		value[index] = marker
	}
	return value
}

func fillDevice(marker byte) protocol.DeviceID {
	var value protocol.DeviceID
	for index := range value {
		value[index] = marker
	}
	return value
}

func fillCredentialID(marker byte) protocol.CredentialID {
	var value protocol.CredentialID
	for index := range value {
		value[index] = marker
	}
	return value
}

func fillEvent(marker byte) protocol.EventID {
	var value protocol.EventID
	for index := range value {
		value[index] = marker
	}
	return value
}

func fillHash(marker byte) [32]byte {
	var value [32]byte
	for index := range value {
		value[index] = marker
	}
	return value
}

func mustRootChainDigest(t testing.TB, objects [][]byte) [32]byte {
	t.Helper()
	digest, err := transparencydomain.RootChainDigest(objects)
	if err != nil {
		t.Fatal(err)
	}
	return digest
}

func publicLeaf(marker byte, sequence uint64) transparencydomain.LogLeaf {
	return transparencydomain.LogLeaf{
		NamespaceCommitment: fillHash(marker),
		SubjectPseudonym:    fillHash(marker + 1),
		ObjectType:          protocol.ObjectTypeOperationEvent,
		ObjectDigest:        fillHash(marker + 2),
		OperationType:       protocol.OperationResolve,
		FinalSequence:       sequence, Epoch: 1,
	}
}
