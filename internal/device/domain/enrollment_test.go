package domain

import (
	"bytes"
	"crypto/ed25519"
	"crypto/sha256"
	"errors"
	"testing"

	"vpass.local/vpass/internal/cryptokit"
	"vpass.local/vpass/internal/protocol"
)

func TestEnrollmentChallengePairingApprovalAndOneUseConsumption(t *testing.T) {
	t.Parallel()
	namespaceID, newDeviceID := enrollmentIDs()
	authPublic, _, err := ed25519.GenerateKey(
		bytes.NewReader(bytes.Repeat([]byte{0x31}, 128)),
	)
	if err != nil {
		t.Fatal(err)
	}
	hpkePublic, hpkePrivate, err := cryptokit.GenerateHPKEKeyPair()
	if err != nil {
		t.Fatal(err)
	}
	defer hpkePrivate.Destroy()
	challenge, code, err := newEnrollmentChallengeWithReader(
		namespaceID, newDeviceID, authPublic, hpkePublic,
		protocol.CapabilityRead|protocol.CapabilityAutofill,
		sha256.Sum256([]byte("namespace-scope")), 100,
		bytes.NewReader(bytes.Repeat([]byte{0x41}, 64)),
	)
	if err != nil {
		t.Fatal(err)
	}
	if len(code) != PairingCodeDigits {
		t.Fatalf("pairing code=%q", code)
	}
	if err := challenge.VerifyPairingCode(code); err != nil {
		t.Fatal(err)
	}
	wrong := []byte(code)
	wrong[len(wrong)-1] ^= 1
	if err := challenge.VerifyPairingCode(string(wrong)); !errors.Is(err, ErrPairingCodeMismatch) {
		t.Fatalf("wrong code error=%v", err)
	}

	var approver protocol.DeviceID
	copy(approver[:], bytes.Repeat([]byte{0x55}, len(approver)))
	var eventID protocol.EventID
	copy(eventID[:], bytes.Repeat([]byte{0x66}, len(eventID)))
	envelopeHash := sha256.Sum256([]byte("root-envelope"))
	credentialHash := sha256.Sum256([]byte("device-credential"))
	if err := challenge.Approve(
		80, approver, eventID, envelopeHash, credentialHash,
	); err != nil {
		t.Fatal(err)
	}
	restored, err := RestoreEnrollmentChallenge(challenge.Snapshot())
	if err != nil {
		t.Fatal(err)
	}
	if err := restored.Consume(90); err != nil {
		t.Fatal(err)
	}
	if err := restored.Consume(91); !errors.Is(err, ErrEnrollmentReplay) {
		t.Fatalf("replay error=%v", err)
	}
	snapshot := restored.Snapshot()
	if snapshot.Status != EnrollmentConsumed ||
		snapshot.ConsumedAtSequence == nil ||
		*snapshot.ConsumedAtSequence != 90 ||
		snapshot.RootEnvelopeHash == nil ||
		*snapshot.RootEnvelopeHash != envelopeHash ||
		snapshot.DeviceCredentialHash == nil ||
		*snapshot.DeviceCredentialHash != credentialHash {
		t.Fatalf("consumed snapshot=%+v", snapshot)
	}
}

func TestEnrollmentRejectsExpiryInvalidHPKEAndSnapshotMutation(t *testing.T) {
	t.Parallel()
	namespaceID, newDeviceID := enrollmentIDs()
	authPublic := ed25519.PublicKey(bytes.Repeat([]byte{0x21}, ed25519.PublicKeySize))
	if _, _, err := newEnrollmentChallengeWithReader(
		namespaceID, newDeviceID, authPublic, cryptokit.HPKEPublicKey{},
		protocol.CapabilityRead, sha256.Sum256([]byte("namespace-scope")), 10,
		bytes.NewReader(bytes.Repeat([]byte{0x42}, 64)),
	); !errors.Is(err, ErrInvalidEnrollment) {
		t.Fatalf("invalid HPKE error=%v", err)
	}
	hpkePublic, hpkePrivate, err := cryptokit.GenerateHPKEKeyPair()
	if err != nil {
		t.Fatal(err)
	}
	defer hpkePrivate.Destroy()
	challenge, code, err := newEnrollmentChallengeWithReader(
		namespaceID, newDeviceID, authPublic, hpkePublic,
		protocol.CapabilityRead, sha256.Sum256([]byte("namespace-scope")), 10,
		bytes.NewReader(bytes.Repeat([]byte{0x43}, 64)),
	)
	if err != nil {
		t.Fatal(err)
	}
	snapshot := challenge.Snapshot()
	snapshot.Nonce[0] ^= 1
	if err := challenge.VerifyPairingCode(code); err != nil {
		t.Fatal("snapshot mutation changed challenge")
	}
	var approver protocol.DeviceID
	copy(approver[:], bytes.Repeat([]byte{0x55}, len(approver)))
	var eventID protocol.EventID
	copy(eventID[:], bytes.Repeat([]byte{0x66}, len(eventID)))
	if err := challenge.Approve(
		11, approver, eventID,
		sha256.Sum256([]byte("envelope")),
		sha256.Sum256([]byte("credential")),
	); !errors.Is(err, ErrEnrollmentExpired) {
		t.Fatalf("expired approval error=%v", err)
	}
	if err := challenge.Expire(11); err != nil {
		t.Fatal(err)
	}
}

func enrollmentIDs() (protocol.NamespaceID, protocol.DeviceID) {
	var namespaceID protocol.NamespaceID
	var deviceID protocol.DeviceID
	copy(namespaceID[:], bytes.Repeat([]byte{0x11}, len(namespaceID)))
	copy(deviceID[:], bytes.Repeat([]byte{0x22}, len(deviceID)))
	return namespaceID, deviceID
}
