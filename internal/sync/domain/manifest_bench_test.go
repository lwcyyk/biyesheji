package domain

import (
	"bytes"
	"crypto/ed25519"
	"crypto/sha256"
	"testing"

	"vpass.local/vpass/internal/protocol"
)

func BenchmarkSyncManifestSignVerify100(b *testing.B) {
	privateKey := ed25519.NewKeyFromSeed(
		bytes.Repeat([]byte{0x51}, ed25519.SeedSize),
	)
	publicKey := privateKey.Public().(ed25519.PublicKey)
	var namespaceID protocol.NamespaceID
	var deviceID protocol.DeviceID
	copy(namespaceID[:], bytes.Repeat([]byte{0x11}, len(namespaceID)))
	copy(deviceID[:], bytes.Repeat([]byte{0x22}, len(deviceID)))
	objects := make([]ObjectReference, 100)
	for index := range objects {
		objects[index] = ObjectReference{
			ObjectDigest: sha256.Sum256([]byte{byte(index), byte(index >> 8)}),
			ObjectType:   protocol.ObjectTypeOperationEvent,
			Size:         uint64(index + 1),
		}
	}
	keyID, _ := protocol.KeyIDFromPublicKey(publicKey)
	expected := protocol.VerificationContext{
		ObjectType: protocol.ObjectTypeSyncManifest,
		ChainID:    "benchmark-chain", NamespaceID: namespaceID,
		KeyID: keyID, KeyGeneration: 1,
	}
	base := sha256.Sum256([]byte("base"))
	target := sha256.Sum256([]byte("target"))
	b.ResetTimer()
	for index := 0; index < b.N; index++ {
		manifest, err := SignManifest(
			privateKey, "benchmark-chain", 1, namespaceID, deviceID,
			base, target, uint64(index+1), uint64(index+1), objects,
		)
		if err != nil {
			b.Fatal(err)
		}
		if _, err := ParseAndVerifyManifest(
			manifest.SigInputCBOR(), manifest.Signature(),
			publicKey, expected,
		); err != nil {
			b.Fatal(err)
		}
	}
}
