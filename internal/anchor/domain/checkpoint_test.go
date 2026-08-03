package domain

import (
	"crypto/ed25519"
	"encoding/hex"
	"testing"

	"vpass.local/vpass/internal/protocol"
)

func TestCheckpointKATWhitelistAndProvider(t *testing.T) {
	privateKey := checkpointKey(0x61)
	namespace := checkpointNamespace(0x21)
	payload := CheckpointPayload{
		NamespaceID:         namespace,
		NamespaceStateRoot:  checkpointHash(1),
		DeviceStateRoot:     checkpointHash(2),
		CredentialStateRoot: checkpointHash(3),
		AuditLogRoot:        checkpointHash(4),
		RevocationRoot:      checkpointHash(5),
		CryptoPolicyHash:    checkpointHash(6),
		CheckpointHeight:    7,
		FinalSequence:       11,
		ProviderKind:        ProviderAnvil,
	}
	checkpoint, err := SignCheckpoint(privateKey, "kat-chain", 2, payload)
	if err != nil {
		t.Fatal(err)
	}
	digest := checkpoint.Digest()
	got := hex.EncodeToString(digest[:])
	const want = "44a000ac8f6526437d2aec2306cc286e641729fd84a1caa9050852a6480977d0"
	if got != want {
		t.Fatalf("digest = %s, want %s", got, want)
	}
	object, err := checkpoint.MarshalBinary()
	if err != nil {
		t.Fatal(err)
	}
	publicKey := privateKey.Public().(ed25519.PublicKey)
	keyID, _ := protocol.KeyIDFromPublicKey(publicKey)
	parsed, err := ParseAndVerifyCheckpointObject(
		object, publicKey,
		protocol.VerificationContext{
			ObjectType: protocol.ObjectTypeCheckpoint,
			ChainID:    "kat-chain", NamespaceID: namespace,
			KeyID: keyID, KeyGeneration: 2,
		},
	)
	if err != nil || parsed.Payload().ProviderKind.Name() != "ANVIL" {
		t.Fatalf("parse/provider = %v, %v", parsed, err)
	}
	mutated := payload
	mutated.ProviderKind = 9
	if _, err := SignCheckpoint(privateKey, "kat-chain", 2, mutated); err == nil {
		t.Fatal("unknown provider kind accepted")
	}
}

func checkpointKey(marker byte) ed25519.PrivateKey {
	seed := make([]byte, ed25519.SeedSize)
	for index := range seed {
		seed[index] = marker + byte(index)
	}
	return ed25519.NewKeyFromSeed(seed)
}

func checkpointNamespace(marker byte) protocol.NamespaceID {
	var value protocol.NamespaceID
	for index := range value {
		value[index] = marker
	}
	return value
}

func checkpointHash(marker byte) [32]byte {
	var value [32]byte
	for index := range value {
		value[index] = marker
	}
	return value
}
