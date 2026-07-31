package cryptokit

import (
	"bytes"
	"crypto/ed25519"
	"encoding/json"
	"errors"
	"fmt"
	"testing"

	"vdns.local/vdns/internal/protocol"
)

func TestRootCapsuleRoundTripAndDeviceBinding(t *testing.T) {
	bundle := testRootBundle(t)
	if wire, wireErr := bundle.toWire(); wireErr != nil {
		t.Fatalf("bundle.toWire: %v", wireErr)
	} else if _, marshalErr := protocol.MarshalDeterministic(wire); marshalErr != nil {
		t.Fatalf("marshal bundle wire: %v", marshalErr)
	}
	master, _ := NewSecret([]byte("correct horse battery staple"))
	deviceSecret, _ := NewSecret(sequence(KeySize, 181))
	defer master.Destroy()
	defer deviceSecret.Destroy()
	namespaceID, deviceID := testCapsuleIDs()
	var diagnosticSalt [Argon2SaltSize]byte
	copy(diagnosticSalt[:], sequence(Argon2SaltSize, 1))
	passwordKey, passwordErr := derivePasswordKey(master, diagnosticSalt, testArgon2Params())
	if passwordErr != nil {
		t.Fatalf("derivePasswordKey: %v", passwordErr)
	}
	defer passwordKey.Destroy()
	assertKeyPurpose(t, passwordKey, purposePasswordKDF)
	unlockKey, unlockErr := deriveUnlockKey(passwordKey, deviceSecret, namespaceID, deviceID)
	if unlockErr != nil {
		t.Fatalf("deriveUnlockKey: %v", unlockErr)
	}
	defer unlockKey.Destroy()
	assertKeyPurpose(t, unlockKey, purposeRootUnlock)

	capsule, err := sealRootCapsuleWithReader(
		master,
		deviceSecret,
		namespaceID,
		deviceID,
		testArgon2Params(),
		bundle,
		bytes.NewReader(sequence(Argon2SaltSize+CapsuleNonceSize, 1)),
	)
	if err != nil {
		t.Fatalf("sealRootCapsuleWithReader: %v", err)
	}
	encoded, err := capsule.MarshalBinary()
	if err != nil {
		t.Fatalf("MarshalBinary: %v", err)
	}
	if bytes.Contains(encoded, []byte("correct horse battery staple")) ||
		bytes.Contains(encoded, sequence(KeySize, 181)) {
		t.Fatal("root capsule serialized an unlocking secret")
	}
	parsed, err := ParseRootCapsule(encoded)
	if err != nil {
		t.Fatalf("ParseRootCapsule: %v", err)
	}
	opened, err := OpenRootCapsule(master, deviceSecret, namespaceID, deviceID, parsed)
	if err != nil {
		t.Fatalf("OpenRootCapsule: %v", err)
	}
	defer opened.Destroy()
	assertRootBundlesEqual(t, bundle, opened)

	wrongPassword, _ := NewSecret([]byte("wrong password"))
	defer wrongPassword.Destroy()
	wrongDeviceSecret, _ := NewSecret(sequence(KeySize, 201))
	defer wrongDeviceSecret.Destroy()
	wrongDeviceID := deviceID
	wrongDeviceID[0] ^= 1
	for name, open := range map[string]func() (*RootSecretBundle, error){
		"password": func() (*RootSecretBundle, error) {
			return OpenRootCapsule(wrongPassword, deviceSecret, namespaceID, deviceID, parsed)
		},
		"device secret": func() (*RootSecretBundle, error) {
			return OpenRootCapsule(master, wrongDeviceSecret, namespaceID, deviceID, parsed)
		},
		"device id": func() (*RootSecretBundle, error) {
			return OpenRootCapsule(master, deviceSecret, namespaceID, wrongDeviceID, parsed)
		},
	} {
		t.Run(name, func(t *testing.T) {
			result, openErr := open()
			if result != nil || !errors.Is(openErr, ErrRejectCapsule) {
				t.Fatalf("OpenRootCapsule = %v, %v; want unified rejection", result, openErr)
			}
		})
	}
}

func TestRootCapsuleRejectsMetadataCiphertextAndEncodingTampering(t *testing.T) {
	bundle := testRootBundle(t)
	master, _ := NewSecret([]byte("capsule tamper password"))
	deviceSecret, _ := NewSecret(sequence(KeySize, 81))
	defer master.Destroy()
	defer deviceSecret.Destroy()
	namespaceID, deviceID := testCapsuleIDs()
	capsule, err := sealRootCapsuleWithReader(
		master,
		deviceSecret,
		namespaceID,
		deviceID,
		testArgon2Params(),
		bundle,
		bytes.NewReader(sequence(Argon2SaltSize+CapsuleNonceSize, 31)),
	)
	if err != nil {
		t.Fatal(err)
	}
	tests := []struct {
		name   string
		mutate func(*RootCapsule)
	}{
		{"protocol", func(value *RootCapsule) { value.ProtocolVersion-- }},
		{"suite", func(value *RootCapsule) { value.SuiteID = "VDNS-CP-1" }},
		{"namespace", func(value *RootCapsule) { value.NamespaceID[0] ^= 1 }},
		{"device", func(value *RootCapsule) { value.DeviceID[0] ^= 1 }},
		{"salt", func(value *RootCapsule) { value.ArgonSalt[0] ^= 1 }},
		{"argon params", func(value *RootCapsule) { value.ArgonParams.Iterations++ }},
		{"nonce", func(value *RootCapsule) { value.Nonce[0] ^= 1 }},
		{"ciphertext", func(value *RootCapsule) { value.Ciphertext[0] ^= 1 }},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			changed := *capsule
			changed.Ciphertext = append([]byte(nil), capsule.Ciphertext...)
			test.mutate(&changed)
			result, openErr := OpenRootCapsule(master, deviceSecret, namespaceID, deviceID, &changed)
			if result != nil || !errors.Is(openErr, ErrRejectCapsule) {
				t.Fatalf("tampered capsule = %v, %v; want unified rejection", result, openErr)
			}
		})
	}

	encoded, _ := capsule.MarshalBinary()
	encoded[len(encoded)-1] ^= 1
	if parsed, parseErr := ParseRootCapsule(encoded); parsed != nil || !errors.Is(parseErr, ErrRejectCapsule) {
		t.Fatalf("tampered encoding = %v, %v; want unified rejection", parsed, parseErr)
	}
}

func TestRecoveryCapsuleRoundTripAndHighEntropySecretRequirement(t *testing.T) {
	bundle := testRootBundle(t)
	recoverySecret, _ := NewSecret(sequence(KeySize, 211))
	wrongSecret, _ := NewSecret(sequence(KeySize, 7))
	shortSecret, _ := NewSecret([]byte("not-32-byte-recovery-secret"))
	defer recoverySecret.Destroy()
	defer wrongSecret.Destroy()
	defer shortSecret.Destroy()
	namespaceID, _ := testCapsuleIDs()

	capsule, err := sealRecoveryCapsuleWithReader(
		recoverySecret,
		namespaceID,
		3,
		9,
		bundle,
		bytes.NewReader(sequence(Argon2SaltSize+CapsuleNonceSize, 101)),
	)
	if err != nil {
		t.Fatalf("sealRecoveryCapsuleWithReader: %v", err)
	}
	encoded, err := capsule.MarshalBinary()
	if err != nil {
		t.Fatal(err)
	}
	parsed, err := ParseRecoveryCapsule(encoded)
	if err != nil {
		t.Fatal(err)
	}
	opened, err := OpenRecoveryCapsule(recoverySecret, namespaceID, parsed)
	if err != nil {
		t.Fatalf("OpenRecoveryCapsule: %v", err)
	}
	defer opened.Destroy()
	assertRootBundlesEqual(t, bundle, opened)

	if result, openErr := OpenRecoveryCapsule(wrongSecret, namespaceID, parsed); result != nil || !errors.Is(openErr, ErrRejectCapsule) {
		t.Fatalf("wrong recovery secret = %v, %v", result, openErr)
	}
	if _, sealErr := SealRecoveryCapsule(shortSecret, namespaceID, 3, 10, bundle); !errors.Is(sealErr, ErrInvalidInput) {
		t.Fatalf("short recovery secret = %v, want %v", sealErr, ErrInvalidInput)
	}
	changed := *parsed
	changed.Ciphertext = append([]byte(nil), parsed.Ciphertext...)
	changed.PolicyVersion++
	if result, openErr := OpenRecoveryCapsule(recoverySecret, namespaceID, &changed); result != nil || !errors.Is(openErr, ErrRejectCapsule) {
		t.Fatalf("tampered recovery policy = %v, %v", result, openErr)
	}
}

func TestArgon2PolicyBoundsAndRootBundleRedaction(t *testing.T) {
	valid := testArgon2Params()
	if err := valid.Validate(); err != nil {
		t.Fatalf("valid Argon2id params: %v", err)
	}
	for name, params := range map[string]Argon2Params{
		"version":    {Version: Argon2Version - 1, MemoryKiB: MinArgon2MemoryKiB, Iterations: 1, Lanes: 1},
		"low memory": {Version: Argon2Version, MemoryKiB: MinArgon2MemoryKiB - 1, Iterations: 1, Lanes: 1},
		"high memory": {
			Version: Argon2Version, MemoryKiB: MaxArgon2MemoryKiB + 1, Iterations: 1, Lanes: 1,
		},
		"iterations": {Version: Argon2Version, MemoryKiB: MinArgon2MemoryKiB, Iterations: 0, Lanes: 1},
		"lanes":      {Version: Argon2Version, MemoryKiB: MinArgon2MemoryKiB, Iterations: 1, Lanes: 0},
	} {
		t.Run(name, func(t *testing.T) {
			if !errors.Is(params.Validate(), ErrArgon2Params) {
				t.Fatalf("params %#v were accepted", params)
			}
		})
	}

	bundleForInvalidSeal := testRootBundle(t)
	master, _ := NewSecret([]byte("invalid-parameter-check"))
	deviceSecret, _ := NewSecret(sequence(KeySize, 151))
	defer master.Destroy()
	defer deviceSecret.Destroy()
	namespaceID, deviceID := testCapsuleIDs()
	invalidVersion := testArgon2Params()
	invalidVersion.Version--
	if capsule, err := SealRootCapsule(
		master, deviceSecret, namespaceID, deviceID, invalidVersion, bundleForInvalidSeal,
	); capsule != nil || !errors.Is(err, ErrInvalidInput) {
		t.Fatalf("invalid Argon2 version was normalized at seal: %v, %v", capsule, err)
	}

	bundle := testRootBundle(t)
	if got := fmt.Sprintf("%#v", *bundle); got != redactedSecret {
		t.Fatalf("bundle formatting leaked: %q", got)
	}
	if encoded, err := json.Marshal(bundle); encoded != nil || !errors.Is(err, ErrSecretSerialization) {
		t.Fatalf("bundle JSON = %q, %v", encoded, err)
	}

	namespaceRoot, _ := NewSecret(sequence(KeySize, 1))
	malformedSigning, _ := NewSecret(sequence(ed25519.PrivateKeySize, 2))
	mapping, _ := NewSecret(sequence(KeySize, 3))
	defer namespaceRoot.Destroy()
	defer malformedSigning.Destroy()
	defer mapping.Destroy()
	if malformed, err := NewRootSecretBundle(namespaceRoot, malformedSigning, mapping, 1, 1); malformed != nil || !errors.Is(err, ErrInvalidInput) {
		t.Fatalf("malformed Ed25519 root key = %v, %v", malformed, err)
	}
}

func FuzzParseRootCapsule(f *testing.F) {
	bundle := testRootBundle(f)
	master, _ := NewSecret([]byte("root-capsule-fuzz-seed"))
	deviceSecret, _ := NewSecret(sequence(KeySize, 171))
	defer master.Destroy()
	defer deviceSecret.Destroy()
	namespaceID, deviceID := testCapsuleIDs()
	capsule, err := sealRootCapsuleWithReader(
		master,
		deviceSecret,
		namespaceID,
		deviceID,
		testArgon2Params(),
		bundle,
		bytes.NewReader(sequence(Argon2SaltSize+CapsuleNonceSize, 61)),
	)
	if err != nil {
		f.Fatal(err)
	}
	seed, _ := capsule.MarshalBinary()
	f.Add(seed)
	f.Add([]byte{0xa1, 0x01, 0x02})
	f.Fuzz(func(t *testing.T, encoded []byte) {
		parsed, parseErr := ParseRootCapsule(encoded)
		if parseErr == nil {
			roundTrip, marshalErr := parsed.MarshalBinary()
			if marshalErr != nil || !bytes.Equal(roundTrip, encoded) {
				t.Fatal("accepted RootCapsule was not canonical")
			}
		}
	})
}

func FuzzParseRecoveryCapsule(f *testing.F) {
	bundle := testRootBundle(f)
	recoverySecret, _ := NewSecret(sequence(KeySize, 211))
	defer recoverySecret.Destroy()
	namespaceID, _ := testCapsuleIDs()
	capsule, err := sealRecoveryCapsuleWithReader(
		recoverySecret,
		namespaceID,
		3,
		9,
		bundle,
		bytes.NewReader(sequence(Argon2SaltSize+CapsuleNonceSize, 101)),
	)
	if err != nil {
		f.Fatal(err)
	}
	seed, _ := capsule.MarshalBinary()
	f.Add(seed)
	f.Add([]byte{0xa1, 0x01, 0x02})
	f.Fuzz(func(t *testing.T, encoded []byte) {
		parsed, parseErr := ParseRecoveryCapsule(encoded)
		if parseErr == nil {
			roundTrip, marshalErr := parsed.MarshalBinary()
			if marshalErr != nil || !bytes.Equal(roundTrip, encoded) {
				t.Fatal("accepted RecoveryCapsule was not canonical")
			}
		}
	})
}

func testArgon2Params() Argon2Params {
	return Argon2Params{
		Version: Argon2Version, MemoryKiB: MinArgon2MemoryKiB,
		Iterations: MinArgon2Iterations, Lanes: MinArgon2Lanes,
	}
}

func testCapsuleIDs() (protocol.NamespaceID, protocol.DeviceID) {
	var namespaceID protocol.NamespaceID
	var deviceID protocol.DeviceID
	copy(namespaceID[:], sequence(len(namespaceID), 17))
	copy(deviceID[:], sequence(len(deviceID), 47))
	return namespaceID, deviceID
}

func testRootBundle(t testing.TB) *RootSecretBundle {
	t.Helper()
	namespaceRoot, _ := NewSecret(sequence(KeySize, 1))
	signingPrivate := ed25519.NewKeyFromSeed(sequence(ed25519.SeedSize, 41))
	signing, _ := NewSecret(signingPrivate)
	mapping, _ := NewSecret(sequence(KeySize, 101))
	wipe(signingPrivate)
	bundle, err := NewRootSecretBundle(namespaceRoot, signing, mapping, 3, 1)
	namespaceRoot.Destroy()
	signing.Destroy()
	mapping.Destroy()
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(bundle.Destroy)
	return bundle
}

func assertRootBundlesEqual(t *testing.T, left, right *RootSecretBundle) {
	t.Helper()
	if left.RecoveryPolicyVersion() != right.RecoveryPolicyVersion() ||
		left.SecretGeneration() != right.SecretGeneration() {
		t.Fatal("root bundle metadata changed")
	}
	for name, pair := range map[string][2]*Secret{
		"namespace": {left.namespaceRoot, right.namespaceRoot},
		"signing":   {left.rootSigningPrivate, right.rootSigningPrivate},
		"mapping":   {left.localMappingSeed, right.localMappingSeed},
	} {
		var leftBytes, rightBytes []byte
		if err := pair[0].withBytes(func(raw []byte) error {
			leftBytes = append([]byte(nil), raw...)
			return nil
		}); err != nil {
			t.Fatal(err)
		}
		if err := pair[1].withBytes(func(raw []byte) error {
			rightBytes = append([]byte(nil), raw...)
			return nil
		}); err != nil {
			t.Fatal(err)
		}
		if !bytes.Equal(leftBytes, rightBytes) {
			t.Fatalf("%s root material changed", name)
		}
		wipe(leftBytes)
		wipe(rightBytes)
	}
}
