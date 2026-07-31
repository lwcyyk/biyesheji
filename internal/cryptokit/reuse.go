package cryptokit

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/binary"
	"fmt"
	"io"
	"log/slog"
	"unicode/utf8"
)

const MaxExactSecretSize = 1 << 20

// ReuseTag is a sensitive HMAC output. All fmt verbs redact it and generic
// JSON/text serialization is forbidden. Its byte-array representation remains
// usable by deterministic CBOR when nested inside an already encrypted audit
// payload.
type ReuseTag [sha256.Size]byte

// EncodeExact preserves the exact UTF-8 password bytes and prefixes their
// uint64 big-endian length. The returned buffer is sensitive and should be
// cleared immediately after use.
func EncodeExact(password []byte) ([]byte, error) {
	if !utf8.Valid(password) || len(password) > MaxExactSecretSize {
		return nil, ErrInvalidInput
	}
	encoded := make([]byte, 8+len(password))
	binary.BigEndian.PutUint64(encoded[:8], uint64(len(password)))
	copy(encoded[8:], password)
	return encoded, nil
}

// ComputeReuseTag computes HMAC-SHA-256 over EncodeExact(password).
func ComputeReuseTag(auditKey *Key, password *Secret) (ReuseTag, error) {
	var tag ReuseTag
	if auditKey == nil || password == nil {
		return tag, ErrInvalidInput
	}
	if err := auditKey.requirePurpose(purposeAudit); err != nil {
		return tag, err
	}

	err := password.withBytes(func(passwordBytes []byte) error {
		encoded, err := EncodeExact(passwordBytes)
		if err != nil {
			return err
		}
		defer wipe(encoded)

		return auditKey.withPurposeBytes(purposeAudit, func(keyBytes []byte) error {
			mac := hmac.New(sha256.New, keyBytes)
			_, _ = mac.Write(encoded)
			sum := mac.Sum(nil)
			copy(tag[:], sum)
			wipe(sum)
			return nil
		})
	})
	if err != nil {
		wipe(tag[:])
		return ReuseTag{}, err
	}
	return tag, nil
}

// ReuseTagsEqual compares two tags in constant time.
func ReuseTagsEqual(left, right ReuseTag) bool {
	return hmac.Equal(left[:], right[:])
}

// MatchesReuseTag recomputes a candidate tag and compares it in constant time.
func MatchesReuseTag(auditKey *Key, password *Secret, expected ReuseTag) (bool, error) {
	actual, err := ComputeReuseTag(auditKey, password)
	if err != nil {
		return false, err
	}
	defer wipe(actual[:])
	return ReuseTagsEqual(actual, expected), nil
}

// String implements fmt.Stringer without exposing the tag.
func (ReuseTag) String() string { return redactedSecret }

// GoString implements fmt.GoStringer without exposing the tag.
func (ReuseTag) GoString() string { return redactedSecret }

// Format prevents alternate fmt verbs from exposing the tag.
func (ReuseTag) Format(state fmt.State, _ rune) {
	_, _ = io.WriteString(state, redactedSecret)
}

// MarshalJSON refuses generic JSON serialization.
func (ReuseTag) MarshalJSON() ([]byte, error) {
	return nil, ErrSecretSerialization
}

// MarshalText refuses generic text serialization.
func (ReuseTag) MarshalText() ([]byte, error) {
	return nil, ErrSecretSerialization
}

// LogValue prevents structured slog handlers from reflecting tag bytes.
func (ReuseTag) LogValue() slog.Value { return slog.StringValue(redactedSecret) }
