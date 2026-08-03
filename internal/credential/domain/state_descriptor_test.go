package domain

import (
	"bytes"
	"crypto/ed25519"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"testing"

	"vpass.local/vpass/internal/protocol"
)

func TestStateDescriptorV2SignVerifyRoundTripAndKAT(t *testing.T) {
	t.Parallel()
	privateKey := ed25519.NewKeyFromSeed(bytes.Repeat([]byte{0x61}, ed25519.SeedSize))
	publicKey := privateKey.Public().(ed25519.PublicKey)
	payload := stateDescriptorFixture()
	descriptor, err := SignStateDescriptor(privateKey, "anvil-31337", 3, payload)
	if err != nil {
		t.Fatal(err)
	}
	keyID, _ := protocol.KeyIDFromPublicKey(publicKey)
	expected := protocol.VerificationContext{
		ObjectType: protocol.ObjectTypeStateDescriptor, ChainID: "anvil-31337",
		NamespaceID: payload.NamespaceID, KeyID: keyID, KeyGeneration: 3,
	}
	parsed, err := ParseAndVerifyStateDescriptor(
		descriptor.SigInputCBOR(), descriptor.Signature(), publicKey, expected,
	)
	if err != nil {
		t.Fatal(err)
	}
	if parsed.Digest() != descriptor.Digest() || parsed.Payload() != payload {
		t.Fatal("state descriptor round trip mismatch")
	}
	object, err := descriptor.MarshalBinary()
	if err != nil {
		t.Fatal(err)
	}
	parsedObject, err := ParseAndVerifyStateDescriptorObject(object, publicKey, expected)
	if err != nil {
		t.Fatal(err)
	}
	if parsedObject.Digest() != descriptor.Digest() {
		t.Fatal("complete descriptor object round trip mismatch")
	}
	encoded := descriptor.SigInputCBOR()
	encoded[0] ^= 1
	if bytes.Equal(encoded, descriptor.SigInputCBOR()) {
		t.Fatal("SigInputCBOR exposed mutable storage")
	}

	const wantDigest = "9bfe655da60aac09e5fd0ac4a68a10a2178cd4d120d7ade4012ebae8cf4c9698"
	digest := descriptor.Digest()
	got := hex.EncodeToString(digest[:])
	if wantDigest == "" {
		t.Fatalf("set state descriptor KAT digest to %s", got)
	}
	if got != wantDigest {
		t.Fatalf("state descriptor digest = %s, want %s", got, wantDigest)
	}
}

func TestStateDescriptorObjectRejectsTampering(t *testing.T) {
	t.Parallel()
	privateKey := ed25519.NewKeyFromSeed(bytes.Repeat([]byte{0x45}, ed25519.SeedSize))
	publicKey := privateKey.Public().(ed25519.PublicKey)
	payload := stateDescriptorFixture()
	descriptor, err := SignStateDescriptor(privateKey, "chain", 1, payload)
	if err != nil {
		t.Fatal(err)
	}
	object, err := descriptor.MarshalBinary()
	if err != nil {
		t.Fatal(err)
	}
	keyID, _ := protocol.KeyIDFromPublicKey(publicKey)
	expected := protocol.VerificationContext{
		ObjectType: protocol.ObjectTypeStateDescriptor, ChainID: "chain",
		NamespaceID: payload.NamespaceID, KeyID: keyID, KeyGeneration: 1,
	}
	object[len(object)-1] ^= 1
	if _, err := ParseAndVerifyStateDescriptorObject(object, publicKey, expected); err == nil {
		t.Fatal("tampered complete descriptor object accepted")
	}
}

func TestStateDescriptorRejectsContextSignatureAndInvalidState(t *testing.T) {
	t.Parallel()
	privateKey := ed25519.NewKeyFromSeed(bytes.Repeat([]byte{0x62}, ed25519.SeedSize))
	publicKey := privateKey.Public().(ed25519.PublicKey)
	payload := stateDescriptorFixture()
	descriptor, err := SignStateDescriptor(privateKey, "chain-a", 1, payload)
	if err != nil {
		t.Fatal(err)
	}
	keyID, _ := protocol.KeyIDFromPublicKey(publicKey)
	expected := protocol.VerificationContext{
		ObjectType: protocol.ObjectTypeStateDescriptor, ChainID: "chain-b",
		NamespaceID: payload.NamespaceID, KeyID: keyID, KeyGeneration: 1,
	}
	if _, err := ParseAndVerifyStateDescriptor(
		descriptor.SigInputCBOR(), descriptor.Signature(), publicKey, expected,
	); !errors.Is(err, ErrStateDescriptorVerification) {
		t.Fatalf("wrong chain error = %v", err)
	}
	signature := descriptor.Signature()
	signature[0] ^= 1
	expected.ChainID = "chain-a"
	if _, err := ParseAndVerifyStateDescriptor(
		descriptor.SigInputCBOR(), signature, publicKey, expected,
	); !errors.Is(err, ErrStateDescriptorVerification) {
		t.Fatalf("bad signature error = %v", err)
	}
	invalid := payload
	invalid.LifecycleStatus = 99
	if _, err := SignStateDescriptor(privateKey, "chain-a", 1, invalid); !errors.Is(err, ErrInvalidStateDescriptor) {
		t.Fatalf("invalid status error = %v", err)
	}
	invalid = payload
	previous := [sha256.Size]byte{}
	invalid.PreviousDescriptorHash = &previous
	if _, err := SignStateDescriptor(privateKey, "chain-a", 1, invalid); !errors.Is(err, ErrInvalidStateDescriptor) {
		t.Fatalf("zero predecessor error = %v", err)
	}
}

func FuzzParseStateDescriptor(f *testing.F) {
	privateKey := ed25519.NewKeyFromSeed(bytes.Repeat([]byte{0x63}, ed25519.SeedSize))
	publicKey := privateKey.Public().(ed25519.PublicKey)
	payload := stateDescriptorFixture()
	descriptor, _ := SignStateDescriptor(privateKey, "chain", 1, payload)
	keyID, _ := protocol.KeyIDFromPublicKey(publicKey)
	expected := protocol.VerificationContext{
		ObjectType: protocol.ObjectTypeStateDescriptor, ChainID: "chain",
		NamespaceID: payload.NamespaceID, KeyID: keyID, KeyGeneration: 1,
	}
	signature := descriptor.Signature()
	f.Add(descriptor.SigInputCBOR(), signature[:])
	f.Fuzz(func(t *testing.T, input, rawSignature []byte) {
		if len(rawSignature) != len(protocol.Signature{}) {
			return
		}
		var candidate protocol.Signature
		copy(candidate[:], rawSignature)
		_, _ = ParseAndVerifyStateDescriptor(input, candidate, publicKey, expected)
	})
}

func stateDescriptorFixture() StateDescriptorPayload {
	var namespaceID protocol.NamespaceID
	copy(namespaceID[:], bytes.Repeat([]byte{0x11}, len(namespaceID)))
	var credentialID protocol.CredentialID
	copy(credentialID[:], bytes.Repeat([]byte{0x22}, len(credentialID)))
	var deviceID protocol.DeviceID
	copy(deviceID[:], bytes.Repeat([]byte{0x33}, len(deviceID)))
	return StateDescriptorPayload{
		NamespaceID:          namespaceID,
		CredentialID:         credentialID,
		ActiveVersion:        1,
		ActiveEnvelopeHash:   sha256.Sum256([]byte("envelope")),
		LifecycleStatus:      protocol.LifecycleActive,
		LastOperationEvent:   sha256.Sum256([]byte("create-event")),
		AuthorizedDeviceRoot: sha256.Sum256([]byte("authorized-devices")),
		AuditCheckpoint:      sha256.Sum256([]byte("audit-checkpoint")),
		FinalSequence:        7,
		UpdaterDeviceID:      deviceID,
	}
}
