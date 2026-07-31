package cryptokit

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"testing"

	"vdns.local/vdns/internal/protocol"
)

func TestRouteIdentifiersFixedKATAndDomainSeparation(t *testing.T) {
	t.Parallel()
	nameKey := newScopedTestKey(t, purposeCredentialName, 0x21)
	origin := []byte("https://example.test")
	account := []byte("alice@example.test")
	routeID, err := DeriveRouteID(nameKey, origin, account)
	if err != nil {
		t.Fatal(err)
	}
	originIndex, err := DeriveRouteOriginIndex(nameKey, origin)
	if err != nil {
		t.Fatal(err)
	}
	const (
		wantRouteID     = "28d30931b3e4d548c0195a34b3c1d0d5238b401f2dbb7ac9fabd83f951bf2576"
		wantOriginIndex = "3e6f72cf2f176f87860f8cc3952d444ca9ba965b82bcda3dbd5b0d530e376cde"
	)
	if got := hex.EncodeToString(routeID[:]); got != wantRouteID {
		t.Fatalf("route ID KAT = %s", got)
	}
	if got := hex.EncodeToString(originIndex[:]); got != wantOriginIndex {
		t.Fatalf("origin index KAT = %s", got)
	}
	other, _ := DeriveRouteID(nameKey, origin, []byte("bob@example.test"))
	if routeID == other || [sha256.Size]byte(routeID) == [sha256.Size]byte(originIndex) {
		t.Fatal("route identifier domains were not separated")
	}
}

func TestRouteCiphertextRoundTripAndContextReplayRejection(t *testing.T) {
	t.Parallel()
	nameKey := newScopedTestKey(t, purposeCredentialName, 0x31)
	context := testRouteContext()
	plaintext, _ := NewSecret([]byte("alice@example.test"))
	defer plaintext.Destroy()
	entropy := bytes.NewReader(bytes.Repeat([]byte{0x77}, GCMNonceSize))
	encrypted, err := encryptRouteValueWithReader(nameKey, context, plaintext, entropy)
	if err != nil {
		t.Fatal(err)
	}
	encoded, err := encrypted.MarshalBinary()
	if err != nil {
		t.Fatal(err)
	}
	parsed, err := ParseRouteCiphertext(encoded)
	if err != nil {
		t.Fatal(err)
	}
	opened, err := OpenRouteValue(nameKey, context, parsed)
	if err != nil {
		t.Fatal(err)
	}
	defer opened.Destroy()
	if err := opened.withBytes(func(raw []byte) error {
		if !bytes.Equal(raw, []byte("alice@example.test")) {
			t.Fatal("route plaintext changed")
		}
		return nil
	}); err != nil {
		t.Fatal(err)
	}

	for name, mutate := range map[string]func(*RouteContext){
		"namespace":    func(value *RouteContext) { value.NamespaceID[0] ^= 1 },
		"route":        func(value *RouteContext) { value.RouteID[0] ^= 1 },
		"origin index": func(value *RouteContext) { value.OriginIndex[0] ^= 1 },
		"version":      func(value *RouteContext) { value.RouteVersion++ },
		"field":        func(value *RouteContext) { value.ValueType = RouteValueOrigin },
	} {
		t.Run(name, func(t *testing.T) {
			wrong := context
			mutate(&wrong)
			if value, openErr := OpenRouteValue(nameKey, wrong, parsed); value != nil ||
				!errors.Is(openErr, ErrRejectRouteCiphertext) {
				t.Fatalf("context replay = %v, %v", value, openErr)
			}
		})
	}
}

func TestRouteCiphertextTamperingFailsClosed(t *testing.T) {
	t.Parallel()
	nameKey := newScopedTestKey(t, purposeCredentialName, 0x41)
	context := testRouteContext()
	plaintext, _ := NewSecret([]byte("https://example.test"))
	defer plaintext.Destroy()
	encrypted, err := encryptRouteValueWithReader(
		nameKey,
		context,
		plaintext,
		bytes.NewReader(bytes.Repeat([]byte{0x66}, GCMNonceSize)),
	)
	if err != nil {
		t.Fatal(err)
	}
	encoded, _ := encrypted.MarshalBinary()
	for index := range encoded {
		mutated := append([]byte(nil), encoded...)
		mutated[index] ^= 1
		parsed, parseErr := ParseRouteCiphertext(mutated)
		if parseErr == nil {
			if opened, openErr := OpenRouteValue(nameKey, context, parsed); opened != nil ||
				!errors.Is(openErr, ErrRejectRouteCiphertext) {
				t.Fatalf("mutation %d returned plaintext", index)
			}
		}
	}
}

func TestRouteCiphertextRejectsWrongKeyPurposeAndInput(t *testing.T) {
	t.Parallel()
	context := testRouteContext()
	plaintext, _ := NewSecret([]byte("value"))
	defer plaintext.Destroy()
	wrongKey := newScopedTestKey(t, purposeCredentialWrap, 0x51)
	if _, err := EncryptRouteValue(wrongKey, context, plaintext); !errors.Is(err, ErrInvalidKeyPurpose) {
		t.Fatalf("wrong key purpose error = %v", err)
	}
	if _, err := DeriveRouteID(wrongKey, []byte("https://example.test"), []byte("a")); !errors.Is(err, ErrInvalidKeyPurpose) {
		t.Fatalf("wrong route ID key error = %v", err)
	}
	if _, err := ParseRouteCiphertext([]byte{0xa0}); !errors.Is(err, ErrRejectRouteCiphertext) {
		t.Fatalf("malformed ciphertext error = %v", err)
	}
}

func FuzzParseAndOpenRouteCiphertext(f *testing.F) {
	nameKey := newScopedTestKey(f, purposeCredentialName, 0x61)
	context := testRouteContext()
	plaintext, _ := NewSecret([]byte("fuzz route value"))
	defer plaintext.Destroy()
	encrypted, err := EncryptRouteValue(nameKey, context, plaintext)
	if err != nil {
		f.Fatal(err)
	}
	seed, _ := encrypted.MarshalBinary()
	f.Add(seed)
	f.Add([]byte{0xa0})
	f.Fuzz(func(t *testing.T, encoded []byte) {
		parsed, parseErr := ParseRouteCiphertext(encoded)
		if parseErr != nil {
			return
		}
		opened, openErr := OpenRouteValue(nameKey, context, parsed)
		if openErr != nil && opened != nil {
			t.Fatal("failed open returned plaintext")
		}
		if opened != nil {
			opened.Destroy()
		}
	})
}

func testRouteContext() RouteContext {
	var namespaceID protocol.NamespaceID
	var routeID RouteID
	var originIndex RouteOriginIndex
	copy(namespaceID[:], bytes.Repeat([]byte{0x11}, len(namespaceID)))
	copy(routeID[:], bytes.Repeat([]byte{0x22}, len(routeID)))
	copy(originIndex[:], bytes.Repeat([]byte{0x33}, len(originIndex)))
	return RouteContext{
		NamespaceID: namespaceID, RouteID: routeID, OriginIndex: originIndex,
		RouteVersion: 1, ValueType: RouteValueAccount,
	}
}
