package cryptokit

import (
	"bytes"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"sync"
	"testing"

	"github.com/cloudflare/circl/hpke"

	"vdns.local/vdns/internal/protocol"
)

func TestHPKERoundTripAndContextBinding(t *testing.T) {
	publicKey, privateKey, err := GenerateHPKEKeyPair()
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(privateKey.Destroy)
	info := testHPKEInfo(1, 1, publicKey)
	secret := newHPKETestSecret(t, "32-byte namespace generation key")

	envelope, err := SealHPKE(publicKey, info, secret)
	if err != nil {
		t.Fatal(err)
	}
	wrongFingerprint := info
	wrongFingerprint.RecipientKeyFingerprint[0] ^= 1
	if rejected, sealErr := SealHPKE(publicKey, wrongFingerprint, secret); !errors.Is(sealErr, ErrRejectHPKE) ||
		rejected.Version != 0 || rejected.Enc != nil || rejected.Ciphertext != nil ||
		rejected.InfoHash != ([32]byte{}) {
		t.Fatalf("wrong recipient fingerprint was accepted: %#v, %v", rejected, sealErr)
	}
	plaintext, err := OpenHPKE(privateKey, info, envelope)
	if err != nil {
		t.Fatal(err)
	}
	assertSecretEquals(t, plaintext, "32-byte namespace generation key")
	plaintext.Destroy()

	wrongGeneration := info
	wrongGeneration.KeyGeneration++
	if plaintext, err = OpenHPKE(privateKey, wrongGeneration, envelope); !errors.Is(err, ErrRejectHPKE) || plaintext != nil {
		t.Fatalf("context replay was not rejected: plaintext=%v err=%v", plaintext, err)
	}
	wrongDevice := info
	wrongDevice.DeviceID[0] ^= 0xff
	if plaintext, err = OpenHPKE(privateKey, wrongDevice, envelope); !errors.Is(err, ErrRejectHPKE) || plaintext != nil {
		t.Fatalf("cross-device replay was not rejected: plaintext=%v err=%v", plaintext, err)
	}
	wrongIssuance := info
	wrongIssuance.IssuanceSequence++
	if plaintext, err = OpenHPKE(privateKey, wrongIssuance, envelope); !errors.Is(err, ErrRejectHPKE) || plaintext != nil {
		t.Fatalf("cross-issuance replay was not rejected: plaintext=%v err=%v", plaintext, err)
	}
	wrongObjectType := info
	wrongObjectType.ObjectType = protocol.ObjectTypeRootCapsule
	if plaintext, err = OpenHPKE(privateKey, wrongObjectType, envelope); !errors.Is(err, ErrRejectHPKE) || plaintext != nil {
		t.Fatalf("cross-object replay was not rejected: plaintext=%v err=%v", plaintext, err)
	}
}

func TestHPKERootBundleTransferRoundTripAndRecipientBinding(t *testing.T) {
	t.Parallel()
	publicKey, privateKey, err := GenerateHPKEKeyPair()
	if err != nil {
		t.Fatal(err)
	}
	defer privateKey.Destroy()
	bundle := testRootBundle(t)
	defer bundle.Destroy()
	info := testHPKEInfo(0x7a, bundle.SecretGeneration(), publicKey)
	envelope, err := SealRootBundleHPKE(publicKey, info, bundle)
	if err != nil {
		t.Fatal(err)
	}
	encoded, err := envelope.MarshalBinary()
	if err != nil {
		t.Fatal(err)
	}
	parsed, err := ParseHPKEEnvelope(encoded)
	if err != nil {
		t.Fatal(err)
	}
	encoded[0] ^= 1
	if _, err := ParseHPKEEnvelope(encoded); !errors.Is(err, ErrRejectHPKE) {
		t.Fatalf("tampered envelope object error=%v", err)
	}
	opened, err := OpenRootBundleHPKE(privateKey, info, parsed)
	if err != nil {
		t.Fatal(err)
	}
	defer opened.Destroy()
	assertRootBundlesEqual(t, bundle, opened)
	master, _ := NewSecret([]byte("new device master password"))
	deviceSecret, _ := NewSecret(sequence(KeySize, 0x91))
	defer master.Destroy()
	defer deviceSecret.Destroy()
	capsule, err := SealRootCapsule(
		master, deviceSecret, info.NamespaceID, info.DeviceID,
		testArgon2Params(), opened,
	)
	if err != nil {
		t.Fatal(err)
	}
	reopened, err := OpenRootCapsule(
		master, deviceSecret, info.NamespaceID, info.DeviceID, capsule,
	)
	if err != nil {
		t.Fatal(err)
	}
	defer reopened.Destroy()
	assertRootBundlesEqual(t, bundle, reopened)

	wrongInfo := info
	wrongInfo.DeviceID[0] ^= 1
	if rejected, err := OpenRootBundleHPKE(
		privateKey, wrongInfo, envelope,
	); !errors.Is(err, ErrRejectHPKE) || rejected != nil {
		t.Fatalf("wrong recipient context opened bundle: %v, %v", rejected, err)
	}
}

func TestHPKEWrongRecipientAndTamperingFailClosed(t *testing.T) {
	publicKey, privateKey, err := GenerateHPKEKeyPair()
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(privateKey.Destroy)
	_, wrongPrivateKey, err := GenerateHPKEKeyPair()
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(wrongPrivateKey.Destroy)
	info := testHPKEInfo(2, 7, publicKey)
	secret := newHPKETestSecret(t, "new independent generation secret")
	envelope, err := SealHPKE(publicKey, info, secret)
	if err != nil {
		t.Fatal(err)
	}

	if plaintext, openErr := OpenHPKE(wrongPrivateKey, info, envelope); !errors.Is(openErr, ErrRejectHPKE) || plaintext != nil {
		t.Fatalf("wrong recipient obtained data: plaintext=%v err=%v", plaintext, openErr)
	}
	mutations := []func(*HPKEEnvelope){
		func(value *HPKEEnvelope) { value.Enc[0] ^= 1 },
		func(value *HPKEEnvelope) { value.Ciphertext[0] ^= 1 },
		func(value *HPKEEnvelope) { value.InfoHash[0] ^= 1 },
		func(value *HPKEEnvelope) { value.Version++ },
	}
	for index, mutate := range mutations {
		t.Run(fmt.Sprintf("mutation-%d", index), func(t *testing.T) {
			changed := envelope.Clone()
			mutate(&changed)
			plaintext, openErr := OpenHPKE(privateKey, info, changed)
			if !errors.Is(openErr, ErrRejectHPKE) || plaintext != nil {
				t.Fatalf("tampered envelope accepted: plaintext=%v err=%v", plaintext, openErr)
			}
		})
	}
}

func TestHPKERejectsLowOrderPublicKeysBeforeRegistrationOrSeal(t *testing.T) {
	lowOrder := []HPKEPublicKey{{}, {1}}
	secret := newHPKETestSecret(t, "namespace root")
	for index, key := range lowOrder {
		if _, err := ParseHPKEPublicKey(key[:]); !errors.Is(err, ErrRejectHPKE) {
			t.Fatalf("low-order key %d parsed: %v", index, err)
		}
		if _, err := SealHPKE(key, testHPKEInfo(byte(20+index), 1, key), secret); !errors.Is(err, ErrRejectHPKE) {
			t.Fatalf("low-order key %d sealed: %v", index, err)
		}
	}
}

func TestHPKEPrivateKeyCannotLeakThroughFormattingOrJSON(t *testing.T) {
	publicKey, privateKey, err := GenerateHPKEKeyPair()
	if err != nil {
		t.Fatal(err)
	}
	formats := []string{
		fmt.Sprintf("%v", *privateKey),
		fmt.Sprintf("%+v", *privateKey),
		fmt.Sprintf("%#v", *privateKey),
		fmt.Sprintf("%x", *privateKey),
	}
	for _, rendered := range formats {
		if rendered != "[REDACTED HPKE PRIVATE KEY]" {
			t.Fatalf("unexpected private key rendering: %q", rendered)
		}
	}
	if encoded, marshalErr := json.Marshal(privateKey); !errors.Is(marshalErr, ErrHPKEPrivateKeySerialization) || encoded != nil {
		t.Fatalf("private key JSON serialization was not blocked: %q, %v", encoded, marshalErr)
	}
	privateKey.Destroy()
	if plaintext, openErr := OpenHPKE(privateKey, testHPKEInfo(3, 1, publicKey), HPKEEnvelope{}); !errors.Is(openErr, ErrRejectHPKE) || plaintext != nil {
		t.Fatalf("destroyed key did not fail closed: %v, %v", plaintext, openErr)
	}
}

func TestHPKEPrivateKeyCopiesShareDestruction(t *testing.T) {
	publicKey, privateKey, err := GenerateHPKEKeyPair()
	if err != nil {
		t.Fatal(err)
	}
	copyOfKey := *privateKey
	info := testHPKEInfo(4, 2, publicKey)
	secret := newHPKETestSecret(t, "copy lifecycle test")
	envelope, err := SealHPKE(publicKey, info, secret)
	if err != nil {
		t.Fatal(err)
	}
	privateKey.Destroy()
	if plaintext, openErr := OpenHPKE(&copyOfKey, info, envelope); !errors.Is(openErr, ErrRejectHPKE) || plaintext != nil {
		t.Fatalf("copied key survived destruction: plaintext=%v err=%v", plaintext, openErr)
	}
}

func TestHPKERejectsDestroyedOrOversizedSecret(t *testing.T) {
	publicKey, privateKey, err := GenerateHPKEKeyPair()
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(privateKey.Destroy)
	info := testHPKEInfo(6, 1, publicKey)

	destroyed, _ := NewSecret([]byte("destroy-before-seal"))
	destroyed.Destroy()
	if _, err := SealHPKE(publicKey, info, destroyed); !errors.Is(err, ErrRejectHPKE) {
		t.Fatalf("destroyed secret = %v, want %v", err, ErrRejectHPKE)
	}
	oversized, _ := NewSecret(make([]byte, MaxHPKEPlaintext+1))
	defer oversized.Destroy()
	if _, err := SealHPKE(publicKey, info, oversized); !errors.Is(err, ErrRejectHPKE) {
		t.Fatalf("oversized secret = %v, want %v", err, ErrRejectHPKE)
	}
}

func TestHPKEConcurrentOpenAndDestroyIsRaceFree(t *testing.T) {
	publicKey, privateKey, err := GenerateHPKEKeyPair()
	if err != nil {
		t.Fatal(err)
	}
	info := testHPKEInfo(5, 3, publicKey)
	secret := newHPKETestSecret(t, "concurrent lifecycle test")
	envelope, err := SealHPKE(publicKey, info, secret)
	if err != nil {
		t.Fatal(err)
	}

	var workers sync.WaitGroup
	for worker := 0; worker < 8; worker++ {
		workers.Add(1)
		go func() {
			defer workers.Done()
			for attempt := 0; attempt < 50; attempt++ {
				plaintext, openErr := OpenHPKE(privateKey, info, envelope)
				if openErr == nil {
					plaintext.Destroy()
				} else if !errors.Is(openErr, ErrRejectHPKE) {
					t.Errorf("unexpected open error: %v", openErr)
					return
				}
			}
		}()
	}
	privateKey.Destroy()
	workers.Wait()
}

// RFC 9180 vector profile: Base Mode, DHKEM(X25519, HKDF-SHA256),
// HKDF-SHA256, AES-256-GCM. Values are from the RFC vector manifest.
func TestHPKERFC9180BaseAES256GCM(t *testing.T) {
	scheme := hpke.KEM_X25519_HKDF_SHA256.Scheme()
	ikmR := mustDecodeHex(t, "dac33b0e9db1b59dbbea58d59a14e7b5896e9bdf98fad6891e99d1686492b9ee")
	ikmE := mustDecodeHex(t, "2cd7c601cefb3d42a62b04b7a9041494c06c7843818e0ce28a8f704ae7ab20f9")
	publicReceiver, privateReceiver := scheme.DeriveKeyPair(ikmR)
	publicBytes, err := publicReceiver.MarshalBinary()
	if err != nil {
		t.Fatal(err)
	}
	assertHex(t, publicBytes, "430f4b9859665145a6b1ba274024487bd66f03a2dd577d7753c68d7d7d00c00c")
	privateBytes, err := privateReceiver.MarshalBinary()
	if err != nil {
		t.Fatal(err)
	}
	assertHex(t, privateBytes, "497b4502664cfea5d5af0b39934dac72242a74f8480451e1aee7d6a53320333d")

	suite := hpke.NewSuite(hpke.KEM_X25519_HKDF_SHA256, hpke.KDF_HKDF_SHA256, hpke.AEAD_AES256GCM)
	info := mustDecodeHex(t, "4f6465206f6e2061204772656369616e2055726e")
	sender, err := suite.NewSender(publicReceiver, info)
	if err != nil {
		t.Fatal(err)
	}
	enc, sealer, err := sender.Setup(bytes.NewReader(ikmE))
	if err != nil {
		t.Fatal(err)
	}
	assertHex(t, enc, "6c93e09869df3402d7bf231bf540fadd35cd56be14f97178f0954db94b7fc256")
	plaintext := mustDecodeHex(t, "4265617574792069732074727574682c20747275746820626561757479")
	aad := mustDecodeHex(t, "436f756e742d30")
	ciphertext, err := sealer.Seal(plaintext, aad)
	if err != nil {
		t.Fatal(err)
	}
	assertHex(t, ciphertext, "e5d84cd531cfb583096e7cfa9641bd3079cf3a91cda813c52deb5f512be9931980a41de125a925cdad859d5b7a")

	receiver, err := suite.NewReceiver(privateReceiver, info)
	if err != nil {
		t.Fatal(err)
	}
	opener, err := receiver.Setup(enc)
	if err != nil {
		t.Fatal(err)
	}
	opened, err := opener.Open(ciphertext, aad)
	if err != nil || !bytes.Equal(opened, plaintext) {
		t.Fatalf("RFC 9180 vector did not open: plaintext=%x err=%v", opened, err)
	}
}

func FuzzOpenHPKE(f *testing.F) {
	publicKey, privateKey, err := GenerateHPKEKeyPair()
	if err != nil {
		f.Fatal(err)
	}
	defer privateKey.Destroy()
	info := testHPKEInfo(9, 4, publicKey)
	secret := newHPKETestSecret(f, "fuzz seed generation secret")
	seedEnvelope, err := SealHPKE(publicKey, info, secret)
	if err != nil {
		f.Fatal(err)
	}
	f.Add(seedEnvelope.Enc, seedEnvelope.Ciphertext, seedEnvelope.InfoHash[:], uint64(1))
	f.Add([]byte{1}, []byte{2}, []byte{3}, uint64(0))
	f.Fuzz(func(t *testing.T, enc, ciphertext, hash []byte, version uint64) {
		var infoHash [32]byte
		copy(infoHash[:], hash)
		plaintext, openErr := OpenHPKE(privateKey, info, HPKEEnvelope{
			Version:    version,
			Enc:        enc,
			Ciphertext: ciphertext,
			InfoHash:   infoHash,
		})
		if openErr != nil && plaintext != nil {
			t.Fatal("failure returned partial plaintext")
		}
		if plaintext != nil {
			plaintext.Destroy()
		}
	})
}

func newHPKETestSecret(tb testing.TB, value string) *Secret {
	tb.Helper()
	secret, err := NewSecret([]byte(value))
	if err != nil {
		tb.Fatal(err)
	}
	tb.Cleanup(secret.Destroy)
	return secret
}

func testHPKEInfo(
	namespaceByte byte,
	generation uint64,
	publicKey HPKEPublicKey,
) HPKEInfo {
	var namespaceID protocol.NamespaceID
	var deviceID protocol.DeviceID
	var envelopeID EnvelopeID
	for index := range namespaceID {
		namespaceID[index] = namespaceByte
	}
	for index := range deviceID {
		deviceID[index] = namespaceByte + 1
	}
	for index := range envelopeID {
		envelopeID[index] = namespaceByte + 2
	}
	return NewHPKEInfo(
		namespaceID,
		deviceID,
		publicKey,
		generation,
		uint64(namespaceByte)+10,
		HPKEPurposeRootBundle,
		protocol.ObjectTypeSecretEnvelope,
		envelopeID,
	)
}

func mustDecodeHex(t *testing.T, value string) []byte {
	t.Helper()
	decoded, err := hex.DecodeString(value)
	if err != nil {
		t.Fatal(err)
	}
	return decoded
}

func assertHex(t *testing.T, actual []byte, expected string) {
	t.Helper()
	if hex.EncodeToString(actual) != expected {
		t.Fatalf("vector mismatch\n got: %x\nwant: %s", actual, expected)
	}
}
