package protocol

import (
	"crypto/ed25519"
	"crypto/sha256"
	"encoding/hex"
	"testing"
)

func TestRFC8032Ed25519VectorOne(t *testing.T) {
	vectors := []struct {
		name      string
		seed      string
		publicKey string
		message   string
		signature string
	}{
		{
			name:      "test-1-empty-message",
			seed:      "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60",
			publicKey: "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a",
			message:   "",
			signature: "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e06522490155" +
				"5fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b",
		},
		{
			name:      "test-2-one-byte-message",
			seed:      "4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb",
			publicKey: "3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c",
			message:   "72",
			signature: "92a009a9f0d4cab8720e820b5f642540a2b27b5416503f8fb3762223ebdb69da" +
				"085ac1e43e15996e458f3613d0f11d8c387b2eaeb4302aeeb00d291612bb0c00",
		},
		{
			name:      "test-3-two-byte-message",
			seed:      "c5aa8df43f9f837bedb7442f31dcb7b166d38535076f094b85ce3a2e0b4458f7",
			publicKey: "fc51cd8e6218a1a38da47ed00230f0580816ed13ba3303ac5deb911548908025",
			message:   "af82",
			signature: "6291d657deec24024827e69c3abe01a30ce548a284743a445e3680d7db5ac3ac" +
				"18ff9b538d16f290ae67f760984dc6594a7c15e9716ed28dc027beceea1ec40a",
		},
	}
	for _, vector := range vectors {
		t.Run(vector.name, func(t *testing.T) {
			seed := mustHex(t, vector.seed)
			wantPublic := mustHex(t, vector.publicKey)
			message := mustHex(t, vector.message)
			wantSignature := mustHex(t, vector.signature)
			privateKey := ed25519.NewKeyFromSeed(seed)
			if got := privateKey.Public().(ed25519.PublicKey); !equalBytes(got, wantPublic) {
				t.Fatalf("public key = %x, want %x", got, wantPublic)
			}
			signature, err := signEd25519(privateKey, message)
			if err != nil {
				t.Fatalf("signEd25519: %v", err)
			}
			if !equalBytes(signature[:], wantSignature) {
				t.Fatalf("signature = %x, want %x", signature, wantSignature)
			}
			if !ed25519.Verify(wantPublic, message, signature[:]) {
				t.Fatal("RFC 8032 signature did not verify")
			}
			signature[0] ^= 1
			if ed25519.Verify(wantPublic, message, signature[:]) {
				t.Fatal("bit-flipped signature verified")
			}
		})
	}
}

func TestSigInputSignVerifyDigestAndDomainSeparation(t *testing.T) {
	seed := mustHex(t, "4ccd089b28ff96da9db6c346ec114e0f"+
		"5b8a319f35aba624da8cf6ed4fb8a6fb")
	privateKey := ed25519.NewKeyFromSeed(seed)
	publicKey := privateKey.Public().(ed25519.PublicKey)
	keyID, err := KeyIDFromPublicKey(publicKey)
	if err != nil {
		t.Fatal(err)
	}
	namespaceID, _ := NamespaceIDFromBytes(mustHex(t,
		"000102030405060708090a0b0c0d0e0f"))
	payload, err := MarshalDeterministic(struct {
		Operation uint64 `cbor:"operation"`
		Counter   uint64 `cbor:"counter"`
	}{Operation: 3, Counter: 9})
	if err != nil {
		t.Fatal(err)
	}
	input := NewSigInput(ObjectTypeOperationEvent, "anvil-31337", namespaceID, keyID, 2, payload)
	expected := VerificationContext{
		ObjectType:    ObjectTypeOperationEvent,
		ChainID:       "anvil-31337",
		NamespaceID:   namespaceID,
		KeyID:         keyID,
		KeyGeneration: 2,
	}
	signature, err := Sign(privateKey, input)
	if err != nil {
		t.Fatalf("Sign: %v", err)
	}
	if err := Verify(publicKey, input, signature, expected); err != nil {
		t.Fatalf("Verify: %v", err)
	}

	digest, err := EventDigest(input, signature)
	if err != nil {
		t.Fatal(err)
	}
	encoded, _ := EncodeSigInput(input)
	wantDigest := sha256.Sum256(append(append([]byte(nil), encoded...), signature[:]...))
	if digest != wantDigest {
		t.Fatalf("digest = %x, want %x", digest, wantDigest)
	}

	mutations := []struct {
		name   string
		mutate func(*SigInput)
	}{
		{"protocol", func(value *SigInput) { value.ProtocolID = "OTHER" }},
		{"suite", func(value *SigInput) { value.SuiteID = "OTHER" }},
		{"object type", func(value *SigInput) { value.ObjectType = ObjectTypeRemediationCampaign }},
		{"chain", func(value *SigInput) { value.ChainID = "chain-other" }},
		{"namespace", func(value *SigInput) { value.NamespaceID[0] ^= 1 }},
		{"key generation", func(value *SigInput) { value.KeyGeneration++ }},
		{"payload", func(value *SigInput) {
			value.Payload, _ = MarshalDeterministic(struct {
				Operation uint64 `cbor:"operation"`
			}{Operation: 4})
		}},
	}
	for _, mutation := range mutations {
		t.Run(mutation.name, func(t *testing.T) {
			changed := input
			changed.Payload = append([]byte(nil), input.Payload...)
			mutation.mutate(&changed)
			if err := Verify(publicKey, changed, signature, expected); err == nil {
				t.Fatal("cross-domain mutation verified")
			}
		})
	}

	replayed := input
	replayed.ChainID = "chain-other"
	replayedSignature, err := Sign(privateKey, replayed)
	if err != nil {
		t.Fatal(err)
	}
	if err := verifySignatureOnly(publicKey, replayed, replayedSignature); err != nil {
		t.Fatalf("self-contained valid signature failed: %v", err)
	}
	if err := Verify(publicKey, replayed, replayedSignature, expected); code(err) != CodeContextMismatch {
		t.Fatalf("cross-context replay code = %q", code(err))
	}
}

func TestSignatureRejectsWrongKeysContextAndPayload(t *testing.T) {
	privateKey := ed25519.NewKeyFromSeed(make([]byte, ed25519.SeedSize))
	publicKey := privateKey.Public().(ed25519.PublicKey)
	keyID, _ := KeyIDFromPublicKey(publicKey)
	namespaceID, _ := NamespaceIDFromBytes(make([]byte, NamespaceIDSize))
	payload, _ := MarshalDeterministic(struct {
		Value uint64 `cbor:"value"`
	}{Value: 1})
	input := NewSigInput(ObjectTypeOperationEvent, "test-chain", namespaceID, keyID, 1, payload)
	expected := VerificationContext{
		ObjectType:    ObjectTypeOperationEvent,
		ChainID:       "test-chain",
		NamespaceID:   namespaceID,
		KeyID:         keyID,
		KeyGeneration: 1,
	}

	if _, err := Sign(ed25519.PrivateKey{1}, input); code(err) != CodeInvalidKey {
		t.Fatalf("short private key code = %q", code(err))
	}
	if _, err := KeyIDFromPublicKey(ed25519.PublicKey{1}); code(err) != CodeInvalidKey {
		t.Fatalf("short public key code = %q", code(err))
	}

	wrongContext := input
	wrongContext.KeyID[0] ^= 1
	if _, err := Sign(privateKey, wrongContext); code(err) != CodeContextMismatch {
		t.Fatalf("wrong key ID code = %q", code(err))
	}

	nonCanonical := input
	nonCanonical.Payload = mustHex(t, "a16576616c75651801")
	if _, err := Sign(privateKey, nonCanonical); code(err) != CodeCBORInvalid {
		t.Fatalf("non-canonical payload code = %q (err=%v)", code(err), err)
	}

	signature, err := Sign(privateKey, input)
	if err != nil {
		t.Fatal(err)
	}
	signature[len(signature)-1] ^= 1
	if err := Verify(publicKey, input, signature, expected); code(err) != CodeInvalidSignature {
		t.Fatalf("tampered signature code = %q", code(err))
	}

	otherPrivate := ed25519.NewKeyFromSeed(append([]byte{1}, make([]byte, ed25519.SeedSize-1)...))
	if err := Verify(otherPrivate.Public().(ed25519.PublicKey), input, signature, expected); code(err) != CodeContextMismatch {
		t.Fatalf("wrong public key code = %q", code(err))
	}
}

func TestSigInputValidationRejectsUnknownDomainsAndLimits(t *testing.T) {
	payload, _ := MarshalDeterministic(struct {
		Value uint64 `cbor:"value"`
	}{Value: 1})
	base := NewSigInput(ObjectTypeOperationEvent, "chain", NamespaceID{}, KeyID{}, 1, payload)
	tests := []struct {
		name   string
		mutate func(*SigInput)
		want   ErrorCode
	}{
		{"protocol", func(value *SigInput) { value.ProtocolVersion = 1 }, CodeUnsupportedProtocol},
		{"suite", func(value *SigInput) { value.SuiteID = "unknown" }, CodeUnsupportedSuite},
		{"object", func(value *SigInput) { value.ObjectType = 999 }, CodeUnsupportedObject},
		{"empty chain", func(value *SigInput) { value.ChainID = "" }, CodeContextMismatch},
		{"long chain", func(value *SigInput) { value.ChainID = string(make([]byte, MaxChainIDBytes+1)) }, CodeContextMismatch},
		{"generation", func(value *SigInput) { value.KeyGeneration = 0 }, CodeContextMismatch},
		{"payload size", func(value *SigInput) { value.Payload = make([]byte, MaxPayloadBytes+1) }, CodeResourceLimit},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			value := base
			test.mutate(&value)
			if err := value.Validate(); code(err) != test.want {
				t.Fatalf("code = %q, want %q (err=%v)", code(err), test.want, err)
			}
		})
	}
}

func FuzzVerifySigInput(f *testing.F) {
	privateKey := ed25519.NewKeyFromSeed(make([]byte, ed25519.SeedSize))
	publicKey := privateKey.Public().(ed25519.PublicKey)
	keyID, _ := KeyIDFromPublicKey(publicKey)
	payload, _ := MarshalDeterministic(struct {
		Value uint64 `cbor:"value"`
	}{Value: 1})
	input := NewSigInput(ObjectTypeOperationEvent, "chain", NamespaceID{}, keyID, 1, payload)
	expected := VerificationContext{
		ObjectType:    ObjectTypeOperationEvent,
		ChainID:       "chain",
		NamespaceID:   NamespaceID{},
		KeyID:         keyID,
		KeyGeneration: 1,
	}
	signature, _ := Sign(privateKey, input)
	f.Add("chain", uint64(1), signature[:])
	f.Fuzz(func(t *testing.T, chain string, generation uint64, rawSignature []byte) {
		candidate := input
		candidate.ChainID = chain
		candidate.KeyGeneration = generation
		var candidateSignature Signature
		copy(candidateSignature[:], rawSignature)
		_ = Verify(publicKey, candidate, candidateSignature, expected)
	})
}

func mustHex(t *testing.T, value string) []byte {
	t.Helper()
	decoded, err := hex.DecodeString(value)
	if err != nil {
		t.Fatal(err)
	}
	return decoded
}

func equalBytes(left, right []byte) bool {
	if len(left) != len(right) {
		return false
	}
	var difference byte
	for i := range left {
		difference |= left[i] ^ right[i]
	}
	return difference == 0
}
