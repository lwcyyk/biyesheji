package cryptokit

import (
	"bytes"
	"crypto/aes"
	"crypto/cipher"
	"errors"
	"testing"

	"vdns.local/vdns/internal/protocol"
)

func TestAES256GCMNISTVector(t *testing.T) {
	t.Parallel()

	key := make([]byte, 32)
	nonce := make([]byte, 12)
	plaintext := make([]byte, 16)
	want := mustDecodeHexKDF(t, "cea7403d4d606b6e074ec5d3baf39d18d0d1c8a799996bf0265b98b5d48ab919")
	block, err := aes.NewCipher(key)
	if err != nil {
		t.Fatalf("aes.NewCipher: %v", err)
	}
	gcm, err := cipher.NewGCM(block)
	if err != nil {
		t.Fatalf("cipher.NewGCM: %v", err)
	}
	got := gcm.Seal(nil, nonce, plaintext, nil)
	if !bytes.Equal(got, want) {
		t.Fatalf("AES-256-GCM = %x, want %x", got, want)
	}
	opened, err := gcm.Open(nil, nonce, got, nil)
	if err != nil || !bytes.Equal(opened, plaintext) {
		t.Fatalf("GCM Open = %x, %v", opened, err)
	}
}

func TestEventEnvelopeRoundTripAndImmutableRetry(t *testing.T) {
	t.Parallel()

	key := newScopedTestKey(t, purposeEvent, 1)
	t.Cleanup(key.Destroy)
	plaintext, _ := NewSecret([]byte("deterministic usage event payload"))
	t.Cleanup(plaintext.Destroy)
	context := testEventContext()
	random := bytes.NewReader(sequence(GCMNonceSize, 91))
	envelope, err := sealEventWithReader(key, context, plaintext, random)
	if err != nil {
		t.Fatalf("sealEventWithReader: %v", err)
	}

	first, err := envelope.MarshalBinary()
	if err != nil {
		t.Fatalf("MarshalBinary: %v", err)
	}
	second, err := envelope.Clone().MarshalBinary()
	if err != nil {
		t.Fatalf("Clone.MarshalBinary: %v", err)
	}
	if !bytes.Equal(first, second) {
		t.Fatal("immutable retry envelope bytes changed")
	}

	parsed, err := ParseEventEnvelope(first)
	if err != nil {
		t.Fatalf("ParseEventEnvelope: %v", err)
	}
	opened, err := OpenEvent(key, context, parsed)
	if err != nil {
		t.Fatalf("OpenEvent: %v", err)
	}
	defer opened.Destroy()
	assertSecretEquals(t, opened, "deterministic usage event payload")
}

func TestEventEnvelopeTamperingAlwaysRejectsWithoutPlaintext(t *testing.T) {
	t.Parallel()

	key := newScopedTestKey(t, purposeEvent, 1)
	t.Cleanup(key.Destroy)
	plaintext, _ := NewSecret([]byte("no partial plaintext"))
	t.Cleanup(plaintext.Destroy)
	context := testEventContext()
	envelope, err := sealEventWithReader(key, context, plaintext, bytes.NewReader(sequence(GCMNonceSize, 51)))
	if err != nil {
		t.Fatalf("sealEventWithReader: %v", err)
	}

	tests := []struct {
		name   string
		mutate func(*EventEnvelope)
	}{
		{name: "nonce", mutate: func(value *EventEnvelope) { value.nonce[0] ^= 1 }},
		{name: "aad", mutate: func(value *EventEnvelope) { value.aad[len(value.aad)-1] ^= 1 }},
		{name: "ciphertext", mutate: func(value *EventEnvelope) { value.ciphertext[0] ^= 1 }},
		{name: "tag", mutate: func(value *EventEnvelope) { value.ciphertext[len(value.ciphertext)-1] ^= 1 }},
		{name: "hash", mutate: func(value *EventEnvelope) { value.payloadHash[0] ^= 1 }},
		{name: "suite", mutate: func(value *EventEnvelope) { value.suiteID = "VDNS-CP-X" }},
	}
	for _, test := range tests {
		test := test
		t.Run(test.name, func(t *testing.T) {
			t.Parallel()
			changed := envelope.Clone()
			test.mutate(changed)
			opened, openErr := OpenEvent(key, context, changed)
			if opened != nil || !errors.Is(openErr, ErrRejectAEAD) {
				t.Fatalf("OpenEvent = %v, %v; want nil, %v", opened, openErr, ErrRejectAEAD)
			}
		})
	}
}

func TestEventEnvelopeRejectsContextChanges(t *testing.T) {
	t.Parallel()

	key := newScopedTestKey(t, purposeEvent, 11)
	t.Cleanup(key.Destroy)
	plaintext, _ := NewSecret([]byte("context-bound"))
	t.Cleanup(plaintext.Destroy)
	context := testEventContext()
	envelope, _ := sealEventWithReader(key, context, plaintext, bytes.NewReader(sequence(GCMNonceSize, 131)))

	changedEpoch := context
	changedEpoch.VRFEpoch++
	if opened, err := OpenEvent(key, changedEpoch, envelope); opened != nil || err != ErrRejectAEAD {
		t.Fatalf("changed epoch = %v, %v", opened, err)
	}
	changedGeneration := context
	changedGeneration.KeyGeneration++
	if opened, err := OpenEvent(key, changedGeneration, envelope); opened != nil || err != ErrRejectAEAD {
		t.Fatalf("changed generation = %v, %v", opened, err)
	}
	changedEvent := context
	changedEvent.EventID[0] ^= 1
	if opened, err := OpenEvent(key, changedEvent, envelope); opened != nil || err != ErrRejectAEAD {
		t.Fatalf("changed EventID = %v, %v", opened, err)
	}
}

func TestEventEnvelopeAcceptsEpochZero(t *testing.T) {
	t.Parallel()

	key := newScopedTestKey(t, purposeEvent, 19)
	defer key.Destroy()
	plaintext, _ := NewSecret([]byte("genesis epoch event"))
	defer plaintext.Destroy()
	context := testEventContext()
	context.VRFEpoch = 0
	envelope, err := sealEventWithReader(key, context, plaintext, bytes.NewReader(sequence(GCMNonceSize, 201)))
	if err != nil {
		t.Fatalf("seal epoch 0: %v", err)
	}
	opened, err := OpenEvent(key, context, envelope)
	if err != nil {
		t.Fatalf("open epoch 0: %v", err)
	}
	opened.Destroy()
}

func TestEventSealRejectsTestEntropyAndLimits(t *testing.T) {
	t.Parallel()

	key := newScopedTestKey(t, purposeEvent, 7)
	t.Cleanup(key.Destroy)
	plaintext, _ := NewSecret([]byte("payload"))
	t.Cleanup(plaintext.Destroy)
	context := testEventContext()
	if _, err := SealEventWithEntropy(key, context, plaintext, NewTestOnlyEntropySource(bytes.NewReader(make([]byte, 64)))); err != ErrRandomSource {
		t.Fatalf("test entropy = %v, want %v", err, ErrRandomSource)
	}

	oversized, _ := NewSecret(make([]byte, MaxEventPlaintextSize+1))
	defer oversized.Destroy()
	if _, err := sealEventWithReader(key, context, oversized, bytes.NewReader(make([]byte, 64))); err != ErrInvalidInput {
		t.Fatalf("oversized plaintext = %v, want %v", err, ErrInvalidInput)
	}

	shortRandom := bytes.NewReader(make([]byte, GCMNonceSize-1))
	if _, err := sealEventWithReader(key, context, plaintext, shortRandom); err != ErrRandomSource {
		t.Fatalf("short random = %v, want %v", err, ErrRandomSource)
	}
}

func FuzzParseAndOpenEventEnvelope(f *testing.F) {
	key := newScopedTestKey(f, purposeEvent, 1)
	plaintext, _ := NewSecret([]byte("fuzz seed payload"))
	context := testEventContext()
	envelope, _ := sealEventWithReader(key, context, plaintext, bytes.NewReader(sequence(GCMNonceSize, 1)))
	seed, _ := envelope.MarshalBinary()
	plaintext.Destroy()
	defer key.Destroy()
	f.Add(seed)
	f.Add([]byte{0xa1, 0x01, 0x02})
	f.Fuzz(func(t *testing.T, encoded []byte) {
		parsed, err := ParseEventEnvelope(encoded)
		if err != nil {
			return
		}
		opened, err := OpenEvent(key, context, parsed)
		if err == nil {
			opened.Destroy()
		}
	})
}

func testEventContext() EventContext {
	var namespaceID protocol.NamespaceID
	copy(namespaceID[:], sequence(len(namespaceID), 3))
	var eventID protocol.EventID
	copy(eventID[:], sequence(len(eventID), 43))
	var pseudonym [DevicePseudonymSize]byte
	copy(pseudonym[:], sequence(DevicePseudonymSize, 83))
	return EventContext{
		NamespaceID:     namespaceID,
		EventID:         eventID,
		ObjectType:      protocol.ObjectTypeOperationEvent,
		DevicePseudonym: pseudonym,
		KeyGeneration:   1,
		VRFEpoch:        7,
	}
}

func assertSecretEquals(t *testing.T, secret *Secret, want string) {
	t.Helper()
	if err := secret.withBytes(func(value []byte) error {
		if got := string(value); got != want {
			t.Fatalf("secret = %q, want %q", got, want)
		}
		return nil
	}); err != nil {
		t.Fatalf("secret.withBytes: %v", err)
	}
}
