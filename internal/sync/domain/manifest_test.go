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

func TestSyncManifestCanonicalSignVerifyAndKAT(t *testing.T) {
	t.Parallel()
	privateKey := ed25519.NewKeyFromSeed(bytes.Repeat([]byte{0x61}, ed25519.SeedSize))
	publicKey := privateKey.Public().(ed25519.PublicKey)
	namespaceID, deviceID, objects := manifestFixture()
	manifest, err := SignManifest(
		privateKey, "sync-chain", 2, namespaceID, deviceID,
		sha256.Sum256([]byte("base")), sha256.Sum256([]byte("target")),
		9, 17, []ObjectReference{objects[2], objects[0], objects[1]},
	)
	if err != nil {
		t.Fatal(err)
	}
	keyID, _ := protocol.KeyIDFromPublicKey(publicKey)
	parsed, err := ParseAndVerifyManifest(
		manifest.SigInputCBOR(), manifest.Signature(), publicKey,
		protocol.VerificationContext{
			ObjectType: protocol.ObjectTypeSyncManifest, ChainID: "sync-chain",
			NamespaceID: namespaceID, KeyID: keyID, KeyGeneration: 2,
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	if parsed.Digest() != manifest.Digest() ||
		parsed.Payload().ObjectCount != 3 ||
		!objectSetsEqual(parsed.Objects(), manifest.Objects()) {
		t.Fatal("manifest round trip mismatch")
	}
	gotObjects := manifest.Objects()
	gotObjects[0].ObjectDigest[0] ^= 1
	if objectSetsEqual(gotObjects, manifest.Objects()) {
		t.Fatal("Objects exposed mutable storage")
	}
	digest := manifest.Digest()
	const wantDigest = "b1f5a70c236e3df4e68ae3a606c1244b1c40b2776f68f786aa2f789829a949ce"
	got := hex.EncodeToString(digest[:])
	if wantDigest == "" {
		t.Fatalf("set sync manifest KAT digest to %s", got)
	}
	if got != wantDigest {
		t.Fatalf("manifest digest = %s, want %s", got, wantDigest)
	}
}

func TestSyncManifestRejectsDuplicateReorderAndWrongContext(t *testing.T) {
	t.Parallel()
	privateKey := ed25519.NewKeyFromSeed(bytes.Repeat([]byte{0x62}, ed25519.SeedSize))
	publicKey := privateKey.Public().(ed25519.PublicKey)
	namespaceID, deviceID, objects := manifestFixture()
	if _, err := SignManifest(
		privateKey, "sync-chain", 1, namespaceID, deviceID,
		sha256.Sum256([]byte("base")), sha256.Sum256([]byte("target")),
		1, 1, []ObjectReference{objects[0], objects[0]},
	); !errors.Is(err, ErrInvalidSyncManifest) {
		t.Fatalf("duplicate object error = %v", err)
	}
	manifest, err := SignManifest(
		privateKey, "sync-chain", 1, namespaceID, deviceID,
		sha256.Sum256([]byte("base")), sha256.Sum256([]byte("target")),
		1, 1, objects,
	)
	if err != nil {
		t.Fatal(err)
	}
	keyID, _ := protocol.KeyIDFromPublicKey(publicKey)
	if _, err := ParseAndVerifyManifest(
		manifest.SigInputCBOR(), manifest.Signature(), publicKey,
		protocol.VerificationContext{
			ObjectType: protocol.ObjectTypeSyncManifest, ChainID: "other-chain",
			NamespaceID: namespaceID, KeyID: keyID, KeyGeneration: 1,
		},
	); !errors.Is(err, ErrSyncManifestVerification) {
		t.Fatalf("wrong context error = %v", err)
	}
}

func FuzzParseSyncManifest(f *testing.F) {
	privateKey := ed25519.NewKeyFromSeed(bytes.Repeat([]byte{0x63}, ed25519.SeedSize))
	publicKey := privateKey.Public().(ed25519.PublicKey)
	namespaceID, deviceID, objects := manifestFixture()
	manifest, _ := SignManifest(
		privateKey, "sync-chain", 1, namespaceID, deviceID,
		sha256.Sum256([]byte("base")), sha256.Sum256([]byte("target")),
		1, 1, objects,
	)
	keyID, _ := protocol.KeyIDFromPublicKey(publicKey)
	expected := protocol.VerificationContext{
		ObjectType: protocol.ObjectTypeSyncManifest, ChainID: "sync-chain",
		NamespaceID: namespaceID, KeyID: keyID, KeyGeneration: 1,
	}
	signature := manifest.Signature()
	f.Add(manifest.SigInputCBOR(), signature[:])
	f.Fuzz(func(t *testing.T, input, rawSignature []byte) {
		if len(rawSignature) != len(protocol.Signature{}) {
			return
		}
		var candidate protocol.Signature
		copy(candidate[:], rawSignature)
		_, _ = ParseAndVerifyManifest(input, candidate, publicKey, expected)
	})
}

func manifestFixture() (
	protocol.NamespaceID,
	protocol.DeviceID,
	[]ObjectReference,
) {
	var namespaceID protocol.NamespaceID
	var deviceID protocol.DeviceID
	var credentialID protocol.CredentialID
	copy(namespaceID[:], bytes.Repeat([]byte{0x11}, len(namespaceID)))
	copy(deviceID[:], bytes.Repeat([]byte{0x22}, len(deviceID)))
	copy(credentialID[:], bytes.Repeat([]byte{0x33}, len(credentialID)))
	version := uint64(1)
	objects := []ObjectReference{
		{
			ObjectDigest: sha256.Sum256([]byte("field")),
			ObjectType:   protocol.ObjectTypeCredentialEnvelope,
			CredentialID: &credentialID, Version: &version, Size: 123,
		},
		{
			ObjectDigest: sha256.Sum256([]byte("descriptor")),
			ObjectType:   protocol.ObjectTypeStateDescriptor,
			CredentialID: &credentialID, Version: &version, Size: 234,
		},
		{
			ObjectDigest: sha256.Sum256([]byte("event")),
			ObjectType:   protocol.ObjectTypeOperationEvent, Size: 345,
		},
	}
	return namespaceID, deviceID, objects
}
