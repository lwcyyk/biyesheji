package cryptokit

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"io"
	"testing"

	"golang.org/x/crypto/hkdf"

	"vdns.local/vdns/internal/protocol"
)

func TestRFC5869SHA256Case1(t *testing.T) {
	t.Parallel()

	ikm := bytes.Repeat([]byte{0x0b}, 22)
	salt := mustDecodeHexKDF(t, "000102030405060708090a0b0c")
	info := mustDecodeHexKDF(t, "f0f1f2f3f4f5f6f7f8f9")
	wantPRK := mustDecodeHexKDF(t, "077709362c2e32df0ddc3f0dc47bba6390b6c73bb50f9c3122ec844ad7c2b3e5")
	wantOKM := mustDecodeHexKDF(t, "3cb25f25faacd57a90434f64d0362f2a2d2d0a90cf1a5a4c5db02d56ecc4c5bf34007208d5b887185865")

	prk := hkdf.Extract(sha256.New, ikm, salt)
	if !bytes.Equal(prk, wantPRK) {
		t.Fatalf("PRK = %x, want %x", prk, wantPRK)
	}
	okm := make([]byte, len(wantOKM))
	if _, err := io.ReadFull(hkdf.Expand(sha256.New, prk, info), okm); err != nil {
		t.Fatalf("HKDF-Expand: %v", err)
	}
	if !bytes.Equal(okm, wantOKM) {
		t.Fatalf("OKM = %x, want %x", okm, wantOKM)
	}
}

func TestNamespaceHierarchyDomainSeparation(t *testing.T) {
	t.Parallel()

	rootBytes := sequence(KeySize, 1)
	root, err := NewSecret(rootBytes)
	if err != nil {
		t.Fatalf("NewSecret: %v", err)
	}
	t.Cleanup(root.Destroy)

	var namespace1 protocol.NamespaceID
	copy(namespace1[:], sequence(len(namespace1), 11))
	namespace2 := namespace1
	namespace2[0] ^= 0x80
	prk1, err := ExtractNamespacePRK(root, namespace1, 1)
	if err != nil {
		t.Fatalf("ExtractNamespacePRK: %v", err)
	}
	t.Cleanup(prk1.Destroy)
	prkNamespace, err := ExtractNamespacePRK(root, namespace2, 1)
	if err != nil {
		t.Fatalf("ExtractNamespacePRK namespace: %v", err)
	}
	t.Cleanup(prkNamespace.Destroy)
	prkGeneration, err := ExtractNamespacePRK(root, namespace1, 2)
	if err != nil {
		t.Fatalf("ExtractNamespacePRK generation: %v", err)
	}
	t.Cleanup(prkGeneration.Destroy)

	assertKeysDifferent(t, "namespace", prk1, prkNamespace)
	assertKeysDifferent(t, "generation", prk1, prkGeneration)

	keys, err := DeriveNamespaceKeys(prk1)
	if err != nil {
		t.Fatalf("DeriveNamespaceKeys: %v", err)
	}
	t.Cleanup(keys.Destroy)
	assertKeysDifferent(t, "wrap/name", keys.Wrap, keys.Name)
	assertKeysDifferent(t, "wrap/audit", keys.Wrap, keys.Audit)
	assertKeysDifferent(t, "name/relation", keys.Name, keys.Relation)
	assertKeysDifferent(t, "audit/rotation", keys.Audit, keys.Rotation)

	beacon1 := sequence(64, 31)
	beacon2 := append([]byte(nil), beacon1...)
	beacon2[0] ^= 1
	audit1, err := DeriveAuditKey(keys.Audit, "anvil:31337", namespace1, 1, 7, beacon1)
	if err != nil {
		t.Fatalf("DeriveAuditKey: %v", err)
	}
	t.Cleanup(audit1.Destroy)
	auditEpoch, _ := DeriveAuditKey(keys.Audit, "anvil:31337", namespace1, 1, 8, beacon1)
	t.Cleanup(auditEpoch.Destroy)
	auditBeacon, _ := DeriveAuditKey(keys.Audit, "anvil:31337", namespace1, 1, 7, beacon2)
	t.Cleanup(auditBeacon.Destroy)
	auditChain, _ := DeriveAuditKey(keys.Audit, "anvil:31338", namespace1, 1, 7, beacon1)
	t.Cleanup(auditChain.Destroy)
	assertKeysDifferent(t, "audit epoch", audit1, auditEpoch)
	assertKeysDifferent(t, "audit beacon", audit1, auditBeacon)
	assertKeysDifferent(t, "audit chain", audit1, auditChain)

	var event1 protocol.EventID
	copy(event1[:], sequence(len(event1), 71))
	event2 := event1
	event2[0] ^= 1
	var pseudonym1 [DevicePseudonymSize]byte
	copy(pseudonym1[:], sequence(DevicePseudonymSize, 101))
	pseudonym2 := pseudonym1
	pseudonym2[0] ^= 1
	eventKey1, _ := DeriveEventKey(audit1, event1, pseudonym1)
	t.Cleanup(eventKey1.Destroy)
	eventKeyID, _ := DeriveEventKey(audit1, event2, pseudonym1)
	t.Cleanup(eventKeyID.Destroy)
	eventKeyPseudonym, _ := DeriveEventKey(audit1, event1, pseudonym2)
	t.Cleanup(eventKeyPseudonym.Destroy)
	assertKeysDifferent(t, "event id", eventKey1, eventKeyID)
	assertKeysDifferent(t, "event pseudonym", eventKey1, eventKeyPseudonym)

	var campaign1 protocol.CampaignID
	copy(campaign1[:], sequence(len(campaign1), 131))
	campaign2 := campaign1
	campaign2[0] ^= 1
	root1 := sha256.Sum256([]byte("affected-set-1"))
	root2 := sha256.Sum256([]byte("affected-set-2"))
	rotate1, _ := DeriveRotationKey(keys.Rotation, campaign1, root1, 9, beacon1)
	t.Cleanup(rotate1.Destroy)
	rotateCampaign, _ := DeriveRotationKey(keys.Rotation, campaign2, root1, 9, beacon1)
	t.Cleanup(rotateCampaign.Destroy)
	rotateRoot, _ := DeriveRotationKey(keys.Rotation, campaign1, root2, 9, beacon1)
	t.Cleanup(rotateRoot.Destroy)
	rotateEpoch, _ := DeriveRotationKey(keys.Rotation, campaign1, root1, 10, beacon1)
	t.Cleanup(rotateEpoch.Destroy)
	assertKeysDifferent(t, "rotation campaign", rotate1, rotateCampaign)
	assertKeysDifferent(t, "rotation affected root", rotate1, rotateRoot)
	assertKeysDifferent(t, "rotation epoch", rotate1, rotateEpoch)
}

func TestDevicePseudonymChangesAcrossEpochs(t *testing.T) {
	t.Parallel()

	key := newScopedTestKey(t, purposeAuditRoot, 17)
	t.Cleanup(key.Destroy)
	var deviceID protocol.DeviceID
	copy(deviceID[:], sequence(len(deviceID), 99))
	zero, err := DeriveDevicePseudonym(key, deviceID, 0)
	if err != nil {
		t.Fatalf("DeriveDevicePseudonym(epoch 0): %v", err)
	}
	one, err := DeriveDevicePseudonym(key, deviceID, 1)
	if err != nil {
		t.Fatalf("DeriveDevicePseudonym: %v", err)
	}
	two, err := DeriveDevicePseudonym(key, deviceID, 2)
	if err != nil {
		t.Fatalf("DeriveDevicePseudonym: %v", err)
	}
	if bytes.Equal(one[:], two[:]) {
		t.Fatal("device pseudonym did not change across epochs")
	}
	if bytes.Equal(zero[:], one[:]) {
		t.Fatal("device pseudonym did not distinguish epoch 0 from epoch 1")
	}

	root, _ := NewSecret(sequence(KeySize, 33))
	defer root.Destroy()
	prk, err := ExtractNamespacePRK(root, protocol.NamespaceID{}, 1)
	if err != nil {
		t.Fatalf("ExtractNamespacePRK: %v", err)
	}
	defer prk.Destroy()
	keys, err := DeriveNamespaceKeys(prk)
	if err != nil {
		t.Fatalf("DeriveNamespaceKeys: %v", err)
	}
	defer keys.Destroy()
	auditZero, err := DeriveAuditKey(keys.Audit, "chain", protocol.NamespaceID{}, 1, 0, []byte{1})
	if err != nil {
		t.Fatalf("DeriveAuditKey(epoch 0): %v", err)
	}
	auditZero.Destroy()
	rotationZero, err := DeriveRotationKey(keys.Rotation, protocol.CampaignID{}, [sha256.Size]byte{}, 0, []byte{1})
	if err != nil {
		t.Fatalf("DeriveRotationKey(epoch 0): %v", err)
	}
	rotationZero.Destroy()
}

func TestKDFRejectsInvalidPublicContextAndDestroyedSecrets(t *testing.T) {
	t.Parallel()

	root, _ := NewSecret(sequence(KeySize, 1))
	root.Destroy()
	if _, err := ExtractNamespacePRK(root, protocol.NamespaceID{}, 1); err != ErrSecretDestroyed {
		t.Fatalf("destroyed root = %v, want %v", err, ErrSecretDestroyed)
	}

	key, _ := newKeyWithPurpose(sequence(KeySize, 2), purposeAuditRoot)
	key.Destroy()
	if _, err := DeriveAuditKey(key, "chain", protocol.NamespaceID{}, 1, 1, []byte{1}); err != ErrSecretDestroyed {
		t.Fatalf("destroyed key = %v, want %v", err, ErrSecretDestroyed)
	}
	if _, err := DeriveAuditKey(key, "", protocol.NamespaceID{}, 1, 1, []byte{1}); err != ErrInvalidInput {
		t.Fatalf("empty chain = %v, want %v", err, ErrInvalidInput)
	}
}

// TestVDNSCryptoProfileKnownAnswer freezes CP-2 after an independent
// reproduction with Python canonical-CBOR encoding, hashlib/hmac RFC 5869,
// and cryptography AESGCM. It is intentionally not generated by the Go SUT.
func TestVDNSCryptoProfileKnownAnswer(t *testing.T) {
	root, _ := NewSecret(sequence(KeySize, 0))
	defer root.Destroy()
	var namespaceID protocol.NamespaceID
	copy(namespaceID[:], sequence(len(namespaceID), 0x10))
	prk, _ := ExtractNamespacePRK(root, namespaceID, 1)
	defer prk.Destroy()
	keys, _ := DeriveNamespaceKeys(prk)
	defer keys.Destroy()
	beacon := sequence(64, 0x20)
	audit, _ := DeriveAuditKey(keys.Audit, "vdns-test-chain", namespaceID, 1, 7, beacon)
	defer audit.Destroy()
	var eventID protocol.EventID
	copy(eventID[:], sequence(len(eventID), 0x30))
	var pseudonym [DevicePseudonymSize]byte
	copy(pseudonym[:], sequence(DevicePseudonymSize, 0x40))
	eventKey, _ := DeriveEventKey(audit, eventID, pseudonym)
	defer eventKey.Destroy()
	var campaignID protocol.CampaignID
	copy(campaignID[:], sequence(len(campaignID), 0x60))
	affectedRoot := sha256.Sum256([]byte("affected-set-kat-v2"))
	rotationKey, _ := DeriveRotationKey(keys.Rotation, campaignID, affectedRoot, 7, beacon)
	defer rotationKey.Destroy()
	password, _ := NewSecret([]byte("P@ssw0rd caf\u00e9 "))
	defer password.Destroy()
	tag, _ := ComputeReuseTag(audit, password)
	plaintext, _ := NewSecret([]byte("usage-event-kat-v2"))
	defer plaintext.Destroy()
	context := EventContext{NamespaceID: namespaceID, EventID: eventID, ObjectType: protocol.ObjectTypeOperationEvent, DevicePseudonym: pseudonym, KeyGeneration: 1, VRFEpoch: 7}
	envelope, _ := sealEventWithReader(eventKey, context, plaintext, bytes.NewReader(sequence(GCMNonceSize, 0x50)))
	assertHexEquals(t, "PRK", keySnapshot(t, prk), "c576b3434b7ac16fa8c40bc13cdedf876dc79a185e512fe50b035588dee34db2")
	assertHexEquals(t, "Kwrap", keySnapshot(t, keys.Wrap), "ef22c60c67326504df42e8d706e9877cc3620c32bc36922859a12488be222c94")
	assertHexEquals(t, "Kname", keySnapshot(t, keys.Name), "4acd79ae8855c128b022c86322f1fc58d09128692421921590d7b160165454f0")
	assertHexEquals(t, "KauditRoot", keySnapshot(t, keys.Audit), "9da86fa6338b6aafbb93c87fba43124e8a29d99135bdc5f49f0515e27f018243")
	assertHexEquals(t, "Krelation", keySnapshot(t, keys.Relation), "1ec4af0f8ceb1f76b3de341eb617d0881e1a6d2c62680fbc30432b5f0cc9618c")
	assertHexEquals(t, "KrotationRoot", keySnapshot(t, keys.Rotation), "0d3969e7808744a0aae657e0614c7b685e3d5438527e593eade0156e5e062ce4")
	assertHexEquals(t, "ReuseTag", tag[:], "8fc00335700c53a63982318be14b0e468d750b1dd46c0e62d4d837c2ab57df2c")
	assertHexEquals(t, "Kaudit", keySnapshot(t, audit), "ea24bdeaf27f77d1b7787936533eedbdbcdf218e7a4e511768c7ddb09604c963")
	assertHexEquals(t, "Kevent", keySnapshot(t, eventKey), "4a074b3d6a4e169be9c205344511842e7670a58c8ca6500570341f4468a86025")
	assertHexEquals(t, "Krotate", keySnapshot(t, rotationKey), "efe2c1dbaa77701af901880706427924574b0a25b7796660b52d78532b201572")
	assertHexEquals(t, "nonce", envelope.nonce[:], "505152535455565758595a5b")
	assertHexEquals(t, "EventAAD", envelope.aad, "a9686576656e745f69645820303132333435363738393a3b3c3d3e3f404142434445464748494a4b4c4d4e4f6873756974655f69646c56444e532d504d2d43502d32697672665f65706f6368076b6f626a6563745f74797065066c6e616d6573706163655f696450101112131415161718191a1b1c1d1e1f6e6b65795f67656e65726174696f6e01706465766963655f70736575646f6e796d50404142434445464748494a4b4c4d4e4f7070726f746f636f6c5f76657273696f6e0271636970686572746578745f6c656e6774681822")
	assertHexEquals(t, "ciphertext", envelope.ciphertext, "4c10a6fcca46ba40a5ecea21f2efadc1c70fa0cc28a2b90412b8e3c6d7eee10d8bdf")
	assertHexEquals(t, "EventPayloadHash", envelope.payloadHash[:], "e0d06246135c65256fe98d8e9daf9a709939aec8b714b53c31da80d43f26558c")
}

func assertKeysDifferent(t *testing.T, name string, left, right *Key) {
	t.Helper()
	leftBytes := keySnapshot(t, left)
	rightBytes := keySnapshot(t, right)
	if bytes.Equal(leftBytes, rightBytes) {
		t.Fatalf("%s keys are equal: %x", name, leftBytes)
	}
}

func keySnapshot(t *testing.T, key *Key) []byte {
	t.Helper()
	var result []byte
	key.state.mu.RLock()
	purpose := key.state.purpose
	key.state.mu.RUnlock()
	if err := key.withPurposeBytes(purpose, func(value []byte) error {
		result = append(result, value...)
		return nil
	}); err != nil {
		t.Fatalf("key.withBytes: %v", err)
	}
	return result
}

func newScopedTestKey(tb testing.TB, purpose keyPurpose, start byte) *Key {
	tb.Helper()
	key, err := newKeyWithPurpose(sequence(KeySize, start), purpose)
	if err != nil {
		tb.Fatal(err)
	}
	tb.Cleanup(key.Destroy)
	return key
}

func mustDecodeHexKDF(t *testing.T, value string) []byte {
	t.Helper()
	decoded, err := hex.DecodeString(value)
	if err != nil {
		t.Fatalf("hex.DecodeString: %v", err)
	}
	return decoded
}

func assertHexEquals(t *testing.T, name string, got []byte, wantHex string) {
	t.Helper()
	want := mustDecodeHexKDF(t, wantHex)
	if !bytes.Equal(got, want) {
		t.Fatalf("%s = %x, want %x", name, got, want)
	}
}

func sequence(length int, start byte) []byte {
	result := make([]byte, length)
	for i := range result {
		result[i] = start + byte(i)
	}
	return result
}
