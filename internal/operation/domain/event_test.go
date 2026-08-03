package domain

import (
	"bytes"
	"crypto/ed25519"
	"crypto/sha256"
	"errors"
	"testing"

	"vpass.local/vpass/internal/protocol"
)

func TestSignedEventRoundTripAndDefensiveCopies(t *testing.T) {
	t.Parallel()
	privateKey := ed25519.NewKeyFromSeed(bytes.Repeat([]byte{0x31}, ed25519.SeedSize))
	publicKey := privateKey.Public().(ed25519.PublicKey)
	payload := validPayload()

	event, err := Sign(privateKey, "vpass-test-chain", 3, payload)
	if err != nil {
		t.Fatal(err)
	}
	keyID, err := protocol.KeyIDFromPublicKey(publicKey)
	if err != nil {
		t.Fatal(err)
	}
	expected := protocol.VerificationContext{
		ObjectType:    protocol.ObjectTypeOperationEvent,
		ChainID:       "vpass-test-chain",
		NamespaceID:   payload.NamespaceID,
		KeyID:         keyID,
		KeyGeneration: 3,
	}
	parsed, err := ParseAndVerify(event.SigInputCBOR(), event.Signature(), publicKey, expected)
	if err != nil {
		t.Fatal(err)
	}
	if parsed.Digest() != event.Digest() || parsed.Payload().EventID != payload.EventID {
		t.Fatal("round-trip changed the event")
	}

	encoded := event.SigInputCBOR()
	encoded[0] ^= 0xff
	if bytes.Equal(encoded, event.SigInputCBOR()) {
		t.Fatal("SigInputCBOR exposed mutable storage")
	}
	copyPayload := event.Payload()
	*copyPayload.NewVersion = 9
	if *event.Payload().NewVersion != 1 {
		t.Fatal("Payload exposed pointer-backed mutable storage")
	}
}

func TestSignedEventRejectsTamperingAndContextReplay(t *testing.T) {
	t.Parallel()
	privateKey := ed25519.NewKeyFromSeed(bytes.Repeat([]byte{0x41}, ed25519.SeedSize))
	publicKey := privateKey.Public().(ed25519.PublicKey)
	payload := validPayload()
	event, err := Sign(privateKey, "chain-a", 1, payload)
	if err != nil {
		t.Fatal(err)
	}
	keyID, _ := protocol.KeyIDFromPublicKey(publicKey)
	expected := protocol.VerificationContext{
		ObjectType:    protocol.ObjectTypeOperationEvent,
		ChainID:       "chain-a",
		NamespaceID:   payload.NamespaceID,
		KeyID:         keyID,
		KeyGeneration: 1,
	}

	tampered := event.SigInputCBOR()
	tampered[len(tampered)-1] ^= 1
	if _, err := ParseAndVerify(tampered, event.Signature(), publicKey, expected); err == nil {
		t.Fatal("tampered SigInput was accepted")
	}
	expected.ChainID = "chain-b"
	if _, err := ParseAndVerify(event.SigInputCBOR(), event.Signature(), publicKey, expected); !errors.Is(err, ErrEventVerification) {
		t.Fatalf("context replay error = %v", err)
	}
}

func TestPayloadValidationRejectsCounterAndCreateVersionErrors(t *testing.T) {
	t.Parallel()
	payload := validPayload()
	payload.DeviceCounter = 2
	if err := payload.Validate(); !errors.Is(err, ErrInvalidEvent) {
		t.Fatalf("missing previous hash error = %v", err)
	}
	payload = validPayload()
	zero := uint64(0)
	payload.NewVersion = &zero
	if err := payload.Validate(); !errors.Is(err, ErrInvalidEvent) {
		t.Fatalf("zero version error = %v", err)
	}
	if _, err := Sign(ed25519.PrivateKey{1}, "chain", 1, validPayload()); !errors.Is(err, ErrInvalidEvent) {
		t.Fatalf("short private key error = %v", err)
	}
}

func validPayload() Payload {
	var eventID protocol.EventID
	copy(eventID[:], bytes.Repeat([]byte{0x11}, len(eventID)))
	var namespaceID protocol.NamespaceID
	copy(namespaceID[:], bytes.Repeat([]byte{0x22}, len(namespaceID)))
	var deviceID protocol.DeviceID
	copy(deviceID[:], bytes.Repeat([]byte{0x33}, len(deviceID)))
	var credentialID protocol.CredentialID
	copy(credentialID[:], bytes.Repeat([]byte{0x44}, len(credentialID)))
	newVersion := uint64(1)
	epoch := uint64(7)
	observed := uint64(1_700_000_000_000)
	return Payload{
		EventID:                eventID,
		NamespaceID:            namespaceID,
		DeviceID:               deviceID,
		DeviceCredentialHash:   sha256.Sum256([]byte("device credential")),
		CredentialID:           &credentialID,
		OperationType:          protocol.OperationCreate,
		NewVersion:             &newVersion,
		DevicePseudonym:        [16]byte{1, 2, 3},
		OriginCommitment:       pointerTo(sha256.Sum256([]byte("origin"))),
		EventPayloadHash:       sha256.Sum256([]byte("encrypted event")),
		VRFEpoch:               &epoch,
		SecretGeneration:       1,
		DeviceCounter:          1,
		ObservedAtMilliseconds: &observed,
	}
}

func pointerTo[T any](value T) *T { return &value }
