package domain

import (
	"crypto/ed25519"
	"encoding/hex"
	"testing"

	"vdns.local/vdns/internal/protocol"
)

func TestSignedTreeHeadKATAndContext(t *testing.T) {
	privateKey := deterministicKey(0x41)
	namespace := testNamespace(0x11)
	payload := TreeHeadPayload{
		NamespaceID:   namespace,
		LogID:         LogID{1, 2, 3, 4},
		TreeSize:      7,
		RootHash:      fillHash(0x31),
		FinalSequence: 19,
		SuiteID:       protocol.SuiteID,
	}
	head, err := SignTreeHead(privateKey, "kat-chain", 3, payload)
	if err != nil {
		t.Fatal(err)
	}
	digest := head.Digest()
	got := hex.EncodeToString(digest[:])
	const want = "0b78a3464cbbde287468e2dbdd52b778bcac214333c73d578504e55b31266d48"
	if got != want {
		t.Fatalf("digest = %s, want %s", got, want)
	}
	object, err := head.MarshalBinary()
	if err != nil {
		t.Fatal(err)
	}
	publicKey := privateKey.Public().(ed25519.PublicKey)
	keyID, _ := protocol.KeyIDFromPublicKey(publicKey)
	parsed, err := ParseAndVerifyTreeHeadObject(
		object, publicKey,
		protocol.VerificationContext{
			ObjectType: protocol.ObjectTypeSignedTreeHead,
			ChainID:    "kat-chain", NamespaceID: namespace,
			KeyID: keyID, KeyGeneration: 3,
		},
	)
	if err != nil || parsed.Digest() != head.Digest() {
		t.Fatalf("parse = %v, %v", parsed, err)
	}
	bad := protocol.VerificationContext{
		ObjectType: protocol.ObjectTypeSignedTreeHead,
		ChainID:    "kat-chain", NamespaceID: namespace,
		KeyID: keyID, KeyGeneration: 4,
	}
	if _, err := ParseAndVerifyTreeHeadObject(object, publicKey, bad); err == nil {
		t.Fatal("wrong key generation accepted")
	}
}

func TestProofBundleKATAndMutation(t *testing.T) {
	privateKey := deterministicKey(0x51)
	namespace := testNamespace(0x22)
	leaf := testLeaf(7, 7)
	payload := ProofBundlePayload{
		NamespaceID:              namespace,
		SubjectDigest:            leaf.ObjectDigest,
		LeafIndex:                6,
		Leaf:                     leaf,
		StartingCheckpointObject: []byte{0xa1, 0x01, 0x01},
		CandidateTreeHeadObject:  []byte{0xa1, 0x01, 0x02},
		InclusionProof:           [][32]byte{fillHash(0x12)},
		ConsistencyProof:         [][32]byte{fillHash(0x13)},
		RootChainObjects:         [][]byte{{0xa1, 0x01, 0x03}},
		DeviceCredentialObject:   []byte{0xa1, 0x01, 0x04},
		CapabilityStatusProof:    [][32]byte{fillHash(0x14)},
		StateDescriptorDigest:    fillHash(0x15),
		LocalPolicyInputHash:     fillHash(0x16),
	}
	bundle, err := SignProofBundle(privateKey, "kat-chain", 2, payload)
	if err != nil {
		t.Fatal(err)
	}
	digest := bundle.Digest()
	got := hex.EncodeToString(digest[:])
	const want = "9cba0907a51781e0fa722017a7e701ff8b0970c8a4f6a614933a38d7668065da"
	if got != want {
		t.Fatalf("digest = %s, want %s", got, want)
	}
	publicKey := privateKey.Public().(ed25519.PublicKey)
	keyID, _ := protocol.KeyIDFromPublicKey(publicKey)
	parsed, err := ParseAndVerifyProofBundle(
		bundle.SigInputCBOR(), bundle.Signature(), publicKey,
		protocol.VerificationContext{
			ObjectType: protocol.ObjectTypeProofBundle,
			ChainID:    "kat-chain", NamespaceID: namespace,
			KeyID: keyID, KeyGeneration: 2,
		},
	)
	if err != nil || parsed.Digest() != bundle.Digest() {
		t.Fatalf("parse = %v, %v", parsed, err)
	}
	copiedPayload := bundle.Payload()
	copiedPayload.RootChainObjects[0][0] ^= 1
	if bundle.Payload().RootChainObjects[0][0] !=
		payload.RootChainObjects[0][0] {
		t.Fatal("proof bundle exposed mutable root-chain storage")
	}
	object, err := bundle.MarshalBinary()
	if err != nil {
		t.Fatal(err)
	}
	parsedObject, err := ParseAndVerifyProofBundleObject(
		object, publicKey,
		protocol.VerificationContext{
			ObjectType: protocol.ObjectTypeProofBundle,
			ChainID:    "kat-chain", NamespaceID: namespace,
			KeyID: keyID, KeyGeneration: 2,
		},
	)
	if err != nil || parsedObject.Digest() != bundle.Digest() {
		t.Fatalf("object parse = %v, %v", parsedObject, err)
	}
	signature := bundle.Signature()
	signature[0] ^= 0x80
	if _, err := ParseAndVerifyProofBundle(
		bundle.SigInputCBOR(), signature, publicKey,
		protocol.VerificationContext{
			ObjectType: protocol.ObjectTypeProofBundle,
			ChainID:    "kat-chain", NamespaceID: namespace,
			KeyID: keyID, KeyGeneration: 2,
		},
	); err == nil {
		t.Fatal("mutated proof bundle accepted")
	}
}

func FuzzParseProofBundle(f *testing.F) {
	privateKey := deterministicKey(0x71)
	namespace := testNamespace(0x33)
	leaf := testLeaf(9, 9)
	bundle, err := SignProofBundle(
		privateKey, "fuzz-chain", 1,
		ProofBundlePayload{
			NamespaceID: namespace, SubjectDigest: leaf.ObjectDigest,
			Leaf:                     leaf,
			StartingCheckpointObject: []byte{1},
			CandidateTreeHeadObject:  []byte{2},
			RootChainObjects:         [][]byte{{3}},
			DeviceCredentialObject:   []byte{4},
			CapabilityStatusProof:    [][32]byte{fillHash(5)},
			StateDescriptorDigest:    fillHash(6),
			LocalPolicyInputHash:     fillHash(7),
		},
	)
	if err != nil {
		f.Fatal(err)
	}
	publicKey := privateKey.Public().(ed25519.PublicKey)
	keyID, _ := protocol.KeyIDFromPublicKey(publicKey)
	expected := protocol.VerificationContext{
		ObjectType: protocol.ObjectTypeProofBundle,
		ChainID:    "fuzz-chain", NamespaceID: namespace,
		KeyID: keyID, KeyGeneration: 1,
	}
	signature := bundle.Signature()
	f.Add(bundle.SigInputCBOR(), signature[:])
	f.Fuzz(func(t *testing.T, encoded, rawSignature []byte) {
		if len(rawSignature) != ed25519.SignatureSize {
			return
		}
		var candidate protocol.Signature
		copy(candidate[:], rawSignature)
		_, _ = ParseAndVerifyProofBundle(encoded, candidate, publicKey, expected)
	})
}

func deterministicKey(marker byte) ed25519.PrivateKey {
	seed := make([]byte, ed25519.SeedSize)
	for index := range seed {
		seed[index] = marker + byte(index)
	}
	return ed25519.NewKeyFromSeed(seed)
}

func testNamespace(marker byte) protocol.NamespaceID {
	var value protocol.NamespaceID
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
