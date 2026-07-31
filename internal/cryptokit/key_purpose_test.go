package cryptokit

import (
	"bytes"
	"crypto/hmac"
	"crypto/sha256"
	"errors"
	"testing"

	"vdns.local/vdns/internal/protocol"
	rotationdomain "vdns.local/vdns/internal/rotation/domain"
)

type policyPRFContract interface {
	PolicyHMAC([]byte) ([sha256.Size]byte, error)
}

var _ policyPRFContract = (*Key)(nil)
var _ rotationdomain.RotationPRF = (*Key)(nil)

func TestKDFMarksEveryDerivedKeyPurpose(t *testing.T) {
	t.Parallel()

	root, _ := NewSecret(sequence(KeySize, 1))
	defer root.Destroy()
	var namespaceID protocol.NamespaceID
	copy(namespaceID[:], sequence(len(namespaceID), 11))
	prk, err := ExtractNamespacePRK(root, namespaceID, 1)
	if err != nil {
		t.Fatalf("ExtractNamespacePRK: %v", err)
	}
	defer prk.Destroy()
	assertKeyPurpose(t, prk, purposeNamespacePRK)

	keys, err := DeriveNamespaceKeys(prk)
	if err != nil {
		t.Fatalf("DeriveNamespaceKeys: %v", err)
	}
	defer keys.Destroy()
	assertKeyPurpose(t, keys.Wrap, purposeCredentialWrap)
	assertKeyPurpose(t, keys.Name, purposeCredentialName)
	assertKeyPurpose(t, keys.Audit, purposeAuditRoot)
	assertKeyPurpose(t, keys.Relation, purposeRelation)
	assertKeyPurpose(t, keys.Rotation, purposeRotationRoot)

	audit, err := DeriveAuditKey(keys.Audit, "purpose-test", namespaceID, 1, 0, []byte("beacon"))
	if err != nil {
		t.Fatalf("DeriveAuditKey: %v", err)
	}
	defer audit.Destroy()
	assertKeyPurpose(t, audit, purposeAudit)

	var eventID protocol.EventID
	copy(eventID[:], sequence(len(eventID), 31))
	event, err := DeriveEventKey(audit, eventID, [DevicePseudonymSize]byte{1})
	if err != nil {
		t.Fatalf("DeriveEventKey: %v", err)
	}
	defer event.Destroy()
	assertKeyPurpose(t, event, purposeEvent)

	rotation, err := DeriveRotationKey(keys.Rotation, protocol.CampaignID{}, [sha256.Size]byte{}, 0, []byte("beacon"))
	if err != nil {
		t.Fatalf("DeriveRotationKey: %v", err)
	}
	defer rotation.Destroy()
	assertKeyPurpose(t, rotation, purposeRotation)

	fieldEnvelope, err := deriveFieldEnvelopeKey(
		keys.Wrap,
		protocol.CredentialID{},
		1,
		FieldPassword,
		FieldEnvelopeID{1},
	)
	if err != nil {
		t.Fatalf("deriveFieldEnvelopeKey: %v", err)
	}
	defer fieldEnvelope.Destroy()
	assertKeyPurpose(t, fieldEnvelope, purposeFieldEnvelope)
}

func TestCrossPurposeKeysAreRejectedByEveryPrimitive(t *testing.T) {
	t.Parallel()

	unscoped, _ := NewKey(sequence(KeySize, 1))
	defer unscoped.Destroy()
	if _, err := DeriveNamespaceKeys(unscoped); !errors.Is(err, ErrInvalidKeyPurpose) {
		t.Fatalf("unscoped KDF input = %v, want %v", err, ErrInvalidKeyPurpose)
	}

	relationKey := newScopedTestKey(t, purposeRelation, 11)
	auditRoot := newScopedTestKey(t, purposeAuditRoot, 12)
	auditKey := newScopedTestKey(t, purposeAudit, 13)
	eventKey := newScopedTestKey(t, purposeEvent, 14)
	rotationKey := newScopedTestKey(t, purposeRotation, 15)
	fieldRoot := newScopedTestKey(t, purposeCredentialWrap, 16)

	if _, err := DeriveEventKey(rotationKey, protocol.EventID{}, [DevicePseudonymSize]byte{}); !errors.Is(err, ErrInvalidKeyPurpose) {
		t.Fatalf("rotation as audit key = %v, want purpose rejection", err)
	}
	if _, err := DeriveAuditKey(auditKey, "chain", protocol.NamespaceID{}, 1, 0, []byte{1}); !errors.Is(err, ErrInvalidKeyPurpose) {
		t.Fatalf("audit as PRK = %v, want purpose rejection", err)
	}
	if _, err := DeriveRotationKey(auditKey, protocol.CampaignID{}, [sha256.Size]byte{}, 0, []byte{1}); !errors.Is(err, ErrInvalidKeyPurpose) {
		t.Fatalf("audit as PRK for rotation = %v, want purpose rejection", err)
	}
	if _, err := deriveFieldEnvelopeKey(relationKey, protocol.CredentialID{}, 1, FieldPassword, FieldEnvelopeID{1}); !errors.Is(err, ErrInvalidKeyPurpose) {
		t.Fatalf("relation as credential wrap key = %v, want purpose rejection", err)
	}

	password, _ := NewSecret([]byte("purpose-bound-password"))
	defer password.Destroy()
	if _, err := ComputeReuseTag(auditRoot, password); !errors.Is(err, ErrInvalidKeyPurpose) {
		t.Fatalf("audit root as epoch audit key = %v, want purpose rejection", err)
	}
	if _, err := DeriveDevicePseudonym(relationKey, protocol.DeviceID{}, 0); !errors.Is(err, ErrInvalidKeyPurpose) {
		t.Fatalf("relation as audit root = %v, want purpose rejection", err)
	}

	eventPlaintext, _ := NewSecret([]byte("event"))
	defer eventPlaintext.Destroy()
	eventContext := testEventContext()
	if _, err := sealEventWithReader(rotationKey, eventContext, eventPlaintext, bytes.NewReader(make([]byte, GCMNonceSize))); !errors.Is(err, ErrInvalidKeyPurpose) {
		t.Fatalf("rotation as event key = %v, want purpose rejection", err)
	}
	envelope, err := sealEventWithReader(eventKey, eventContext, eventPlaintext, bytes.NewReader(make([]byte, GCMNonceSize)))
	if err != nil {
		t.Fatalf("seal with event key: %v", err)
	}
	if opened, err := OpenEvent(rotationKey, eventContext, envelope); opened != nil || !errors.Is(err, ErrRejectAEAD) {
		t.Fatalf("open with rotation key = %v, %v; want unified rejection", opened, err)
	}

	fieldPlaintext, _ := NewSecret([]byte("field"))
	defer fieldPlaintext.Destroy()
	fieldContext := testFieldContext(FieldPassword, 1)
	if _, err := encryptFieldWithReader(relationKey, fieldContext, fieldPlaintext, bytes.NewReader(make([]byte, fieldRandomMaterialLen))); !errors.Is(err, ErrInvalidKeyPurpose) {
		t.Fatalf("relation as credential wrap key = %v, want purpose rejection", err)
	}
	encrypted, err := encryptFieldWithReader(fieldRoot, fieldContext, fieldPlaintext, bytes.NewReader(sequence(fieldRandomMaterialLen, 1)))
	if err != nil {
		t.Fatalf("encrypt with field root: %v", err)
	}
	if opened, err := DecryptField(relationKey, fieldContext, encrypted); opened != nil || !errors.Is(err, ErrRejectAEAD) {
		t.Fatalf("decrypt with relation key = %v, %v; want unified rejection", opened, err)
	}
}

func TestRotationPolicyHMACIsPurposeBoundAndDestroyable(t *testing.T) {
	t.Parallel()

	rotation := newScopedTestKey(t, purposeRotation, 71)
	input := []byte("deterministic-policy-stream-context")
	got, err := rotation.PolicyHMAC(input)
	if err != nil {
		t.Fatalf("PolicyHMAC: %v", err)
	}
	raw := sequence(KeySize, 71)
	mac := hmac.New(sha256.New, raw)
	_, _ = mac.Write(input)
	want := mac.Sum(nil)
	if !hmac.Equal(got[:], want) {
		t.Fatalf("PolicyHMAC output mismatch: got=%x want=%x", got, want)
	}
	wipe(raw)
	wipe(want)

	event := newScopedTestKey(t, purposeEvent, 72)
	if _, err := event.PolicyHMAC(input); !errors.Is(err, ErrInvalidKeyPurpose) {
		t.Fatalf("event PolicyHMAC = %v, want purpose rejection", err)
	}
	if _, err := rotation.PolicyHMAC(nil); !errors.Is(err, ErrInvalidInput) {
		t.Fatalf("empty PolicyHMAC = %v, want invalid input", err)
	}
	rotation.Destroy()
	if _, err := rotation.PolicyHMAC(input); !errors.Is(err, ErrSecretDestroyed) {
		t.Fatalf("destroyed PolicyHMAC = %v, want destroyed", err)
	}
}

func TestDerivedRotationKeyDrivesPolicyEncodeWithoutRawKeyBridge(t *testing.T) {
	t.Parallel()

	root, _ := NewSecret(sequence(KeySize, 91))
	defer root.Destroy()
	var namespaceID protocol.NamespaceID
	copy(namespaceID[:], sequence(len(namespaceID), 21))
	prk, err := ExtractNamespacePRK(root, namespaceID, 1)
	if err != nil {
		t.Fatalf("ExtractNamespacePRK: %v", err)
	}
	defer prk.Destroy()
	keys, err := DeriveNamespaceKeys(prk)
	if err != nil {
		t.Fatalf("DeriveNamespaceKeys: %v", err)
	}
	defer keys.Destroy()
	var campaignID protocol.CampaignID
	copy(campaignID[:], sequence(len(campaignID), 51))
	rotation, err := DeriveRotationKey(keys.Rotation, campaignID, sha256.Sum256([]byte("affected")), 7, []byte("beacon"))
	if err != nil {
		t.Fatalf("DeriveRotationKey: %v", err)
	}
	defer rotation.Destroy()

	policy, err := rotationdomain.NewPasswordPolicy(rotationdomain.PolicySpec{
		Length:   16,
		Alphabet: "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
	})
	if err != nil {
		t.Fatalf("NewPasswordPolicy: %v", err)
	}
	var credentialID protocol.CredentialID
	copy(credentialID[:], sequence(len(credentialID), 71))
	context, err := rotationdomain.NewPolicyContext(credentialID, 2, policy.Hash(), campaignID, 1)
	if err != nil {
		t.Fatalf("NewPolicyContext: %v", err)
	}
	result, err := rotationdomain.PolicyEncode(rotation, context, policy)
	if err != nil {
		t.Fatalf("PolicyEncode with derived Krotate: %v", err)
	}
	result.Password.Destroy()

	rotation.Destroy()
	if _, err := rotationdomain.PolicyEncode(rotation, context, policy); !errors.Is(err, rotationdomain.ErrPolicyPRF) {
		t.Fatalf("PolicyEncode after Krotate destruction = %v, want %v", err, rotationdomain.ErrPolicyPRF)
	}
}

func assertKeyPurpose(t *testing.T, key *Key, want keyPurpose) {
	t.Helper()
	if key == nil || key.state == nil {
		t.Fatal("nil key state")
	}
	key.state.mu.RLock()
	got := key.state.purpose
	key.state.mu.RUnlock()
	if got != want {
		t.Fatalf("key purpose = %d, want %d", got, want)
	}
}
