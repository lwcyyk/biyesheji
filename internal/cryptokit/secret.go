package cryptokit

import (
	"crypto/hmac"
	"crypto/sha256"
	"crypto/subtle"
	"fmt"
	"io"
	"log/slog"
	"runtime"
	"sync"

	"vdns.local/vdns/internal/protocol"
)

const redactedSecret = "[REDACTED]"

// Secret owns a mutable copy of sensitive bytes.
//
// Secret deliberately cannot be marshaled to JSON or text and all fmt verbs
// render a fixed redaction. Call Destroy as soon as the value is no longer
// needed. Go and the operating system can retain copies outside this buffer,
// so destruction is a best-effort lifecycle control rather than a guarantee.
// Copies are thin handles to the same state, so destruction is observed by
// every copy.
type Secret struct {
	state *secretState
}

type secretState struct {
	mu        sync.RWMutex
	material  []byte
	destroyed bool
}

// NewSecret copies material into a new owned mutable buffer. Empty secrets are
// rejected because every VDNS secret input has a non-zero protocol length.
func NewSecret(material []byte) (*Secret, error) {
	if len(material) == 0 {
		return nil, ErrInvalidInput
	}

	owned := make([]byte, len(material))
	copy(owned, material)
	return &Secret{state: &secretState{material: owned}}, nil
}

// Len returns the current secret length, or zero after destruction.
func (s *Secret) Len() int {
	if s == nil || s.state == nil {
		return 0
	}

	s.state.mu.RLock()
	defer s.state.mu.RUnlock()
	if s.state.destroyed {
		return 0
	}
	return len(s.state.material)
}

// withBytes supplies a temporary copy to fn and clears that copy immediately
// afterward. The callback must not retain the slice.
func (s *Secret) withBytes(fn func([]byte) error) error {
	if s == nil || s.state == nil || fn == nil {
		return ErrInvalidInput
	}

	s.state.mu.RLock()
	if s.state.destroyed {
		s.state.mu.RUnlock()
		return ErrSecretDestroyed
	}
	temporary := make([]byte, len(s.state.material))
	copy(temporary, s.state.material)
	s.state.mu.RUnlock()

	defer wipe(temporary)
	return fn(temporary)
}

// Use supplies a short-lived copy of the secret to an explicitly trusted
// boundary such as local field encryption or the Native Messaging host. The
// callback must not retain the slice; the temporary copy is wiped on return.
//
// This method deliberately uses a callback instead of returning bytes so
// ordinary HTTP DTOs, loggers and persistence adapters cannot accidentally
// retain secret material.
func (s *Secret) Use(fn func([]byte) error) error {
	return s.withBytes(fn)
}

// Clone creates an independently destroyable protected copy.
func (s *Secret) Clone() (*Secret, error) {
	if s == nil {
		return nil, ErrInvalidInput
	}
	var result *Secret
	err := s.withBytes(func(material []byte) error {
		var createErr error
		result, createErr = NewSecret(material)
		return createErr
	})
	return result, err
}

// SecretsEqual compares two live secrets without exposing either byte slice.
// Length and contents are compared in constant time for equal-length inputs.
func SecretsEqual(left, right *Secret) (bool, error) {
	if left == nil || right == nil {
		return false, ErrInvalidInput
	}
	equal := false
	err := left.withBytes(func(leftBytes []byte) error {
		return right.withBytes(func(rightBytes []byte) error {
			equal = len(leftBytes) == len(rightBytes) &&
				subtle.ConstantTimeCompare(leftBytes, rightBytes) == 1
			return nil
		})
	})
	if err != nil {
		return false, err
	}
	return equal, nil
}

// Destroy overwrites the owned buffer and makes future use fail. It is safe to
// call multiple times.
func (s *Secret) Destroy() {
	if s == nil || s.state == nil {
		return
	}

	s.state.mu.Lock()
	defer s.state.mu.Unlock()
	if s.state.destroyed {
		return
	}
	wipe(s.state.material)
	s.state.material = nil
	s.state.destroyed = true
}

// String implements fmt.Stringer without exposing material.
func (Secret) String() string { return redactedSecret }

// GoString implements fmt.GoStringer without exposing material.
func (Secret) GoString() string { return redactedSecret }

// Format prevents alternate fmt verbs (including %x and %#v) from bypassing
// String or GoString.
func (Secret) Format(state fmt.State, _ rune) {
	_, _ = io.WriteString(state, redactedSecret)
}

// MarshalJSON refuses generic JSON serialization.
func (Secret) MarshalJSON() ([]byte, error) {
	return nil, ErrSecretSerialization
}

// MarshalText refuses generic text serialization.
func (Secret) MarshalText() ([]byte, error) {
	return nil, ErrSecretSerialization
}

// LogValue prevents structured slog handlers from reflecting private state.
func (Secret) LogValue() slog.Value { return slog.StringValue(redactedSecret) }

// Key is a fixed-length secret used by VDNS symmetric primitives. Its material
// is private so generic formatters and serializers cannot enumerate it.
// Copies are thin handles to the same state, so destruction is observed by
// every copy.
type Key struct {
	state *keyState
}

// keyPurpose is deliberately package-private: callers can receive scoped keys
// only from the corresponding KDF transition, never forge a purpose tag around
// arbitrary bytes.
type keyPurpose uint8

const (
	purposeUnscoped keyPurpose = iota
	purposeNamespacePRK
	purposeCredentialWrap
	purposeCredentialName
	purposeAuditRoot
	purposeRelation
	purposeRotationRoot
	purposeAudit
	purposeEvent
	purposeRotation
	purposeFieldDEK
	purposeFieldEnvelope
	purposePasswordKDF
	purposeRootUnlock
	purposeRecovery
)

func (purpose keyPurpose) valid() bool {
	return purpose >= purposeUnscoped && purpose <= purposeRecovery
}

type keyState struct {
	mu        sync.RWMutex
	material  [KeySize]byte
	purpose   keyPurpose
	destroyed bool
}

// NewKey copies exactly 32 bytes into an unscoped protected value. Unscoped
// keys are intentionally rejected by every protocol primitive; production
// scoped keys can only be obtained from the corresponding KDF transition.
func NewKey(material []byte) (*Key, error) {
	return newKeyWithPurpose(material, purposeUnscoped)
}

func newKeyWithPurpose(material []byte, purpose keyPurpose) (*Key, error) {
	if len(material) != KeySize || !purpose.valid() {
		return nil, ErrInvalidInput
	}

	key := &Key{state: &keyState{purpose: purpose}}
	copy(key.state.material[:], material)
	return key, nil
}

func newKeyFromArray(material [KeySize]byte, purpose keyPurpose) (*Key, error) {
	if !purpose.valid() {
		return nil, ErrInvalidInput
	}
	return &Key{state: &keyState{material: material, purpose: purpose}}, nil
}

func (k *Key) requirePurpose(expected keyPurpose) error {
	if k == nil || k.state == nil {
		return ErrInvalidInput
	}
	k.state.mu.RLock()
	defer k.state.mu.RUnlock()
	if k.state.destroyed {
		return ErrSecretDestroyed
	}
	if k.state.purpose != expected {
		return ErrInvalidKeyPurpose
	}
	return nil
}

func (k *Key) withPurposeBytes(expected keyPurpose, fn func([]byte) error) error {
	if k == nil || k.state == nil || fn == nil {
		return ErrInvalidInput
	}

	k.state.mu.RLock()
	if k.state.destroyed {
		k.state.mu.RUnlock()
		return ErrSecretDestroyed
	}
	if k.state.purpose != expected {
		k.state.mu.RUnlock()
		return ErrInvalidKeyPurpose
	}
	temporary := make([]byte, KeySize)
	copy(temporary, k.state.material[:])
	k.state.mu.RUnlock()

	defer wipe(temporary)
	return fn(temporary)
}

// PolicyHMAC exposes only the rotation PRF operation required by PolicyEncode;
// it never exports Krotate bytes.
func (k *Key) PolicyHMAC(input []byte) ([sha256.Size]byte, error) {
	var output [sha256.Size]byte
	if len(input) == 0 || len(input) > protocol.MaxCBORBytes {
		return output, ErrInvalidInput
	}
	err := k.withPurposeBytes(purposeRotation, func(keyBytes []byte) error {
		mac := hmac.New(sha256.New, keyBytes)
		_, _ = mac.Write(input)
		sum := mac.Sum(nil)
		copy(output[:], sum)
		wipe(sum)
		return nil
	})
	if err != nil {
		wipe(output[:])
		return [sha256.Size]byte{}, err
	}
	return output, nil
}

// Destroy overwrites the key and makes future use fail. It is idempotent.
func (k *Key) Destroy() {
	if k == nil || k.state == nil {
		return
	}

	k.state.mu.Lock()
	defer k.state.mu.Unlock()
	if k.state.destroyed {
		return
	}
	wipe(k.state.material[:])
	k.state.destroyed = true
}

// String implements fmt.Stringer without exposing key material.
func (Key) String() string { return redactedSecret }

// GoString implements fmt.GoStringer without exposing key material.
func (Key) GoString() string { return redactedSecret }

// Format prevents alternate fmt verbs from exposing key material.
func (Key) Format(state fmt.State, _ rune) {
	_, _ = io.WriteString(state, redactedSecret)
}

// MarshalJSON refuses generic JSON serialization.
func (Key) MarshalJSON() ([]byte, error) {
	return nil, ErrSecretSerialization
}

// MarshalText refuses generic text serialization.
func (Key) MarshalText() ([]byte, error) {
	return nil, ErrSecretSerialization
}

// LogValue prevents structured slog handlers from reflecting private state.
func (Key) LogValue() slog.Value { return slog.StringValue(redactedSecret) }

func wipe(buf []byte) {
	for i := range buf {
		buf[i] = 0
	}
	runtime.KeepAlive(buf)
}
