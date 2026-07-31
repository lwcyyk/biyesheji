package cryptokit

import (
	"bytes"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"strings"
	"testing"
)

func TestEncodeExactPreservesPasswordBytes(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name     string
		password string
	}{
		{name: "case lower", password: "password"},
		{name: "case upper", password: "Password"},
		{name: "leading space", password: " password"},
		{name: "trailing space", password: "password "},
		{name: "composed", password: "caf\u00e9"},
		{name: "decomposed", password: "cafe\u0301"},
	}

	seen := make(map[string]string)
	for _, test := range tests {
		test := test
		t.Run(test.name, func(t *testing.T) {
			encoded, err := EncodeExact([]byte(test.password))
			if err != nil {
				t.Fatalf("EncodeExact: %v", err)
			}
			defer wipe(encoded)
			if got, want := binary.BigEndian.Uint64(encoded[:8]), uint64(len([]byte(test.password))); got != want {
				t.Fatalf("length prefix = %d, want %d", got, want)
			}
			if !bytes.Equal(encoded[8:], []byte(test.password)) {
				t.Fatalf("payload = %x, want %x", encoded[8:], []byte(test.password))
			}
			key := string(encoded)
			if previous, exists := seen[key]; exists {
				t.Fatalf("encoding collided with %s", previous)
			}
			seen[key] = test.name
		})
	}
}

func TestReuseTagExactnessAndConstantTimeAPI(t *testing.T) {
	t.Parallel()

	key := newScopedTestKey(t, purposeAudit, 41)
	t.Cleanup(key.Destroy)
	password, _ := NewSecret([]byte("caf\u00e9 "))
	t.Cleanup(password.Destroy)
	tag, err := ComputeReuseTag(key, password)
	if err != nil {
		t.Fatalf("ComputeReuseTag: %v", err)
	}

	same, _ := NewSecret([]byte("caf\u00e9 "))
	t.Cleanup(same.Destroy)
	matches, err := MatchesReuseTag(key, same, tag)
	if err != nil || !matches {
		t.Fatalf("MatchesReuseTag(same) = %v, %v", matches, err)
	}

	different, _ := NewSecret([]byte("cafe\u0301 "))
	t.Cleanup(different.Destroy)
	matches, err = MatchesReuseTag(key, different, tag)
	if err != nil || matches {
		t.Fatalf("MatchesReuseTag(different) = %v, %v", matches, err)
	}

	changed := tag
	changed[0] ^= 1
	if ReuseTagsEqual(tag, changed) {
		t.Fatal("ReuseTagsEqual accepted changed tag")
	}
}

func TestReuseTagCannotEnterNormalFormattingOrJSON(t *testing.T) {
	t.Parallel()

	var tag ReuseTag
	copy(tag[:], []byte("tag-material-that-must-not-leak!!"))
	for _, output := range []string{
		fmt.Sprint(tag),
		fmt.Sprintf("%x", tag),
		fmt.Sprintf("%#v", tag),
	} {
		if !strings.Contains(output, redactedSecret) {
			t.Fatalf("tag output was not redacted: %q", output)
		}
	}
	if _, err := json.Marshal(tag); err == nil {
		t.Fatal("json.Marshal(ReuseTag) succeeded; want refusal")
	}
}

func TestEncodeExactRejectsInvalidUTF8AndResourceExhaustion(t *testing.T) {
	t.Parallel()

	if _, err := EncodeExact([]byte{0xff}); err != ErrInvalidInput {
		t.Fatalf("invalid UTF-8 = %v, want %v", err, ErrInvalidInput)
	}
	if _, err := EncodeExact(make([]byte, MaxExactSecretSize+1)); err != ErrInvalidInput {
		t.Fatalf("oversized password = %v, want %v", err, ErrInvalidInput)
	}
}

func FuzzEncodeExact(f *testing.F) {
	f.Add([]byte("password"))
	f.Add([]byte("caf\u00e9"))
	f.Add([]byte{0xff})
	f.Fuzz(func(t *testing.T, value []byte) {
		if len(value) > MaxExactSecretSize {
			return
		}
		encoded, err := EncodeExact(value)
		if err != nil {
			return
		}
		defer wipe(encoded)
		if got := binary.BigEndian.Uint64(encoded[:8]); got != uint64(len(value)) {
			t.Fatalf("length prefix = %d, want %d", got, len(value))
		}
		if !bytes.Equal(encoded[8:], value) {
			t.Fatal("EncodeExact changed input bytes")
		}
	})
}
