package domain

import (
	"bytes"
	"crypto/sha256"
	"errors"
	"testing"

	"vpass.local/vpass/internal/cryptokit"
	"vpass.local/vpass/internal/platform"
	"vpass.local/vpass/internal/protocol"
)

func TestVersionStateMachineAllowsOnlyFrozenEdges(t *testing.T) {
	t.Parallel()
	allowed := map[[2]VersionStatus]bool{
		{VersionPendingCandidate, VersionSiteUpdatePending}:                    true,
		{VersionPendingCandidate, VersionAborted}:                              true,
		{VersionSiteUpdatePending, VersionFailedRetryable}:                     true,
		{VersionSiteUpdatePending, VersionSiteStatusUnknown}:                   true,
		{VersionSiteUpdatePending, VersionSiteChangedLocalCommitPending}:       true,
		{VersionFailedRetryable, VersionSiteUpdatePending}:                     true,
		{VersionFailedRetryable, VersionAborted}:                               true,
		{VersionSiteStatusUnknown, VersionSiteUpdatePending}:                   true,
		{VersionSiteChangedLocalCommitPending, VersionActiveLocalPendingProof}: true,
		{VersionActiveLocalPendingProof, VersionActive}:                        true,
		{VersionActive, VersionSuperseded}:                                     true,
	}
	for current := VersionPendingCandidate; current <= VersionAborted; current++ {
		for next := VersionPendingCandidate; next <= VersionAborted; next++ {
			want := allowed[[2]VersionStatus{current, next}]
			if got := current.CanTransitionTo(next); got != want {
				t.Fatalf("transition %d -> %d = %v, want %v", current, next, got, want)
			}
			err := RequireTransition(current, next)
			if want && err != nil {
				t.Fatalf("allowed transition %d -> %d: %v", current, next, err)
			}
			if !want && !errors.Is(err, ErrInvalidVersionTransition) {
				t.Fatalf("forbidden transition %d -> %d error = %v", current, next, err)
			}
		}
	}
}

func FuzzVersionStatusTransition(f *testing.F) {
	for current := VersionPendingCandidate; current <= VersionAborted; current++ {
		for next := VersionPendingCandidate; next <= VersionAborted; next++ {
			f.Add(uint8(current), uint8(next))
		}
	}
	f.Fuzz(func(t *testing.T, currentRaw, nextRaw uint8) {
		current, next := VersionStatus(currentRaw), VersionStatus(nextRaw)
		allowed := current.CanTransitionTo(next)
		err := RequireTransition(current, next)
		if current.Valid() && next.Valid() && allowed && err != nil {
			t.Fatalf("allowed transition %d -> %d rejected: %v", current, next, err)
		}
		if (!current.Valid() || !next.Valid() || !allowed) && err == nil {
			t.Fatalf("invalid transition %d -> %d accepted", current, next)
		}
	})
}

func TestVersionDescriptorIsDeterministicAndPreservesUnchangedField(t *testing.T) {
	t.Parallel()
	fieldRoot, namespaceID, credentialID := testFieldRoot(t)
	username := testFieldMapping(t, fieldRoot, namespaceID, credentialID, 1, cryptokit.FieldUsername, "alice")
	passwordV1 := testFieldMapping(t, fieldRoot, namespaceID, credentialID, 1, cryptokit.FieldPassword, "password-v1")
	policyHash := sha256.Sum256([]byte("policy-v1"))

	v1, err := NewVersionDraft(
		credentialID,
		1,
		1,
		VersionActive,
		nil,
		policyHash,
		[]FieldMapping{passwordV1, username},
	)
	if err != nil {
		t.Fatal(err)
	}
	v1Reordered, err := NewVersionDraft(
		credentialID,
		1,
		1,
		VersionActive,
		nil,
		policyHash,
		[]FieldMapping{username, passwordV1},
	)
	if err != nil {
		t.Fatal(err)
	}
	if v1.DescriptorHash() != v1Reordered.DescriptorHash() || !bytes.Equal(v1.DescriptorCBOR(), v1Reordered.DescriptorCBOR()) {
		t.Fatal("descriptor depends on caller field ordering")
	}

	passwordV2 := testFieldMapping(t, fieldRoot, namespaceID, credentialID, 2, cryptokit.FieldPassword, "password-v2")
	previous := v1.DescriptorHash()
	v2, err := NewVersionDraft(
		credentialID,
		2,
		2,
		VersionPendingCandidate,
		&previous,
		policyHash,
		[]FieldMapping{username, passwordV2},
	)
	if err != nil {
		t.Fatal(err)
	}
	fields := v2.Fields()
	if fields[0].Reference().FieldType != cryptokit.FieldUsername || fields[0].Reference() != username.Reference() ||
		fields[0].ObjectReference() != username.ObjectReference() || fields[0].FieldDigest() != username.FieldDigest() {
		t.Fatal("v2 changed the reused username field mapping")
	}
	if fields[1].Reference() == passwordV1.Reference() {
		t.Fatal("v2 password field did not change")
	}
	if v2.DescriptorHash() == v1.DescriptorHash() {
		t.Fatal("new password version retained the old descriptor hash")
	}
}

func TestVersionAndFieldMappingRejectInvalidInputs(t *testing.T) {
	t.Parallel()
	fieldRoot, namespaceID, credentialID := testFieldRoot(t)
	password := testFieldMapping(t, fieldRoot, namespaceID, credentialID, 1, cryptokit.FieldPassword, "secret")
	username := testFieldMapping(t, fieldRoot, namespaceID, credentialID, 1, cryptokit.FieldUsername, "alice")
	policyHash := sha256.Sum256([]byte("policy"))

	if _, err := NewVersionDraft(credentialID, 1, 1, VersionActive, nil, policyHash, []FieldMapping{username}); !errors.Is(err, ErrInvalidCredentialVersion) {
		t.Fatalf("missing password error = %v", err)
	}
	if _, err := NewVersionDraft(credentialID, 1, 1, VersionActive, nil, policyHash, []FieldMapping{password, password}); !errors.Is(err, ErrInvalidCredentialVersion) {
		t.Fatalf("duplicate field error = %v", err)
	}
	previous := sha256.Sum256([]byte("not allowed for v1"))
	if _, err := NewVersionDraft(credentialID, 1, 1, VersionActive, &previous, policyHash, []FieldMapping{password}); !errors.Is(err, ErrInvalidCredentialVersion) {
		t.Fatalf("v1 previous descriptor error = %v", err)
	}

	plaintext, _ := cryptokit.NewSecret([]byte("object mismatch"))
	defer plaintext.Destroy()
	encrypted, err := cryptokit.EncryptField(fieldRoot, cryptokit.FieldContext{
		NamespaceID:       namespaceID,
		CredentialID:      credentialID,
		CredentialVersion: 1,
		FieldType:         cryptokit.FieldPassword,
		KeyGeneration:     1,
		CryptoPolicyHash:  policyHash,
		OriginBinding:     sha256.Sum256([]byte("origin-binding")),
	}, plaintext)
	if err != nil {
		t.Fatal(err)
	}
	wrong := platform.ObjectRef{Digest: sha256.Sum256([]byte("wrong")), Size: 5}
	if _, err := NewFieldMapping(encrypted, wrong); !errors.Is(err, ErrFieldObjectMismatch) {
		t.Fatalf("wrong object reference error = %v", err)
	}
}

func TestVersionCrashRecoveryActionsAndEvidenceGate(t *testing.T) {
	t.Parallel()
	tests := []struct {
		status VersionStatus
		action RecoveryAction
	}{
		{VersionPendingCandidate, RecoveryStartSiteChange},
		{VersionSiteUpdatePending, RecoveryQuerySiteReceipt},
		{VersionFailedRetryable, RecoveryRetrySiteChange},
		{VersionSiteStatusUnknown, RecoveryRequireReview},
		{VersionSiteChangedLocalCommitPending, RecoveryCommitLocalCandidate},
		{VersionActiveLocalPendingProof, RecoveryPublishCandidate},
		{VersionActive, RecoveryNone},
		{VersionSuperseded, RecoveryNone},
		{VersionAborted, RecoveryNone},
	}
	for _, test := range tests {
		got, err := test.status.RecoveryAction()
		if err != nil || got != test.action {
			t.Fatalf("status %d recovery = %d, %v", test.status, got, err)
		}
	}
	if _, err := VersionStatus(0).RecoveryAction(); !errors.Is(err, ErrInvalidCredentialVersion) {
		t.Fatalf("unknown recovery status error = %v", err)
	}
	if err := RequireEvidenceTransition(
		VersionActiveLocalPendingProof, VersionActive,
		protocol.EvidenceNewPasswordReloginConfirmed,
	); !errors.Is(err, ErrInvalidVersionTransition) {
		t.Fatalf("weak activation evidence = %v", err)
	}
	if err := RequireEvidenceTransition(
		VersionActiveLocalPendingProof, VersionActive,
		protocol.EvidenceSiteSignedReceipt,
	); err != nil {
		t.Fatal(err)
	}
	if err := RequireEvidenceTransition(
		VersionSiteStatusUnknown, VersionActive,
		protocol.EvidenceSiteSignedReceipt,
	); !errors.Is(err, ErrInvalidVersionTransition) {
		t.Fatalf("UNKNOWN activated directly: %v", err)
	}
}

func testFieldRoot(t *testing.T) (*cryptokit.Key, protocol.NamespaceID, protocol.CredentialID) {
	t.Helper()
	var namespaceID protocol.NamespaceID
	copy(namespaceID[:], bytes.Repeat([]byte{0x21}, len(namespaceID)))
	var credentialID protocol.CredentialID
	copy(credentialID[:], bytes.Repeat([]byte{0x31}, len(credentialID)))
	root, err := cryptokit.NewSecret(bytes.Repeat([]byte{0x41}, cryptokit.KeySize))
	if err != nil {
		t.Fatal(err)
	}
	prk, err := cryptokit.ExtractNamespacePRK(root, namespaceID, 1)
	root.Destroy()
	if err != nil {
		t.Fatal(err)
	}
	keys, err := cryptokit.DeriveNamespaceKeys(prk)
	prk.Destroy()
	if err != nil {
		t.Fatal(err)
	}
	keys.Name.Destroy()
	keys.Audit.Destroy()
	keys.Relation.Destroy()
	keys.Rotation.Destroy()
	t.Cleanup(keys.Wrap.Destroy)
	return keys.Wrap, namespaceID, credentialID
}

func testFieldMapping(
	t *testing.T,
	fieldRoot *cryptokit.Key,
	namespaceID protocol.NamespaceID,
	credentialID protocol.CredentialID,
	version uint64,
	fieldType cryptokit.FieldType,
	value string,
) FieldMapping {
	t.Helper()
	plaintext, err := cryptokit.NewSecret([]byte(value))
	if err != nil {
		t.Fatal(err)
	}
	defer plaintext.Destroy()
	encrypted, err := cryptokit.EncryptField(fieldRoot, cryptokit.FieldContext{
		NamespaceID:       namespaceID,
		CredentialID:      credentialID,
		CredentialVersion: version,
		FieldType:         fieldType,
		KeyGeneration:     1,
		CryptoPolicyHash:  sha256.Sum256([]byte("test-policy")),
		OriginBinding:     sha256.Sum256([]byte("test-origin-binding")),
	}, plaintext)
	if err != nil {
		t.Fatal(err)
	}
	encoded, err := encrypted.MarshalBinary()
	if err != nil {
		t.Fatal(err)
	}
	reference := platform.ObjectRef{Digest: sha256.Sum256(encoded), Size: uint64(len(encoded))}
	clear(encoded)
	mapping, err := NewFieldMapping(encrypted, reference)
	if err != nil {
		t.Fatal(err)
	}
	return mapping
}
