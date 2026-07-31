package cryptokit

import (
	"crypto/rand"
	"crypto/sha256"
	"crypto/subtle"
	"encoding"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log/slog"
	"sync"

	"github.com/cloudflare/circl/hpke"
	"golang.org/x/crypto/curve25519"

	"vdns.local/vdns/internal/protocol"
)

const (
	HPKEPublicKeySize  = 32
	HPKEPrivateKeySize = 32
	HPKEEncSize        = 32
	HPKETagSize        = 16
	MaxHPKEPlaintext   = 4 << 10
)

var (
	// ErrRejectHPKE deliberately hides whether key parsing, context validation,
	// decapsulation, or AEAD authentication failed.
	ErrRejectHPKE = errors.New("REJECT_HPKE")
	// ErrHPKEPrivateKeySerialization prevents accidental persistence or logging.
	ErrHPKEPrivateKeySerialization = errors.New("HPKE private key serialization is forbidden")
)

var hpkeSuite = hpke.NewSuite(
	hpke.KEM_X25519_HKDF_SHA256,
	hpke.KDF_HKDF_SHA256,
	hpke.AEAD_AES256GCM,
)

// HPKEKeyPurpose is part of the frozen HPKE info context. New values require a
// protocol-version change rather than an uncoordinated local extension.
type HPKEKeyPurpose uint64

const (
	HPKEPurposeRootBundle       HPKEKeyPurpose = 1
	HPKEPurposeSecretGeneration HPKEKeyPurpose = 2
)

// EnvelopeID is a random, public identifier for one immutable envelope.
type EnvelopeID [32]byte

// HPKEPublicKey contains a serialized RFC 9180 X25519 recipient key.
type HPKEPublicKey [HPKEPublicKeySize]byte

// HPKEPrivateKey keeps key bytes opaque to formatting and serialization.
// Call Destroy when the owning key handle reaches the end of its lifecycle.
type HPKEPrivateKey struct {
	state *hpkePrivateKeyState
}

type hpkePrivateKeyState struct {
	mu        sync.RWMutex
	raw       [HPKEPrivateKeySize]byte
	destroyed bool
}

var _ fmt.Formatter = HPKEPrivateKey{}
var _ fmt.Stringer = HPKEPrivateKey{}
var _ fmt.GoStringer = HPKEPrivateKey{}
var _ json.Marshaler = HPKEPrivateKey{}
var _ encoding.TextMarshaler = HPKEPrivateKey{}

// HPKEInfo is encoded with protocol.MarshalDeterministic and used as both HPKE
// info and AEAD associated data. The outer root-signed object must be verified
// by the caller before OpenHPKE is invoked.
type HPKEInfo struct {
	ProtocolID              string               `cbor:"protocol_id"`
	ProtocolVersion         uint64               `cbor:"protocol_version"`
	SuiteID                 string               `cbor:"suite_id"`
	NamespaceID             protocol.NamespaceID `cbor:"namespace_id"`
	DeviceID                protocol.DeviceID    `cbor:"device_id"`
	RecipientKeyFingerprint [sha256.Size]byte    `cbor:"recipient_key_fingerprint"`
	KeyGeneration           uint64               `cbor:"key_generation"`
	IssuanceSequence        uint64               `cbor:"issuance_sequence"`
	KeyPurpose              HPKEKeyPurpose       `cbor:"key_purpose"`
	ObjectType              protocol.ObjectType  `cbor:"object_type"`
	EnvelopeID              EnvelopeID           `cbor:"envelope_id"`
}

// HPKEEnvelope is immutable transport data. Ciphertext contains the RFC 9180
// AEAD tag. No plaintext or private key material belongs in this value.
type HPKEEnvelope struct {
	Version    uint64
	Enc        []byte
	Ciphertext []byte
	InfoHash   [sha256.Size]byte
}

type hpkeEnvelopeWire struct {
	ProtocolID      string              `cbor:"protocol_id"`
	ProtocolVersion uint64              `cbor:"protocol_version"`
	SuiteID         string              `cbor:"suite_id"`
	ObjectType      protocol.ObjectType `cbor:"object_type"`
	Version         uint64              `cbor:"version"`
	Enc             []byte              `cbor:"enc"`
	Ciphertext      []byte              `cbor:"ciphertext"`
	InfoHash        [sha256.Size]byte   `cbor:"info_hash"`
}

// NewHPKEInfo constructs a VDNS-PM/2 recipient-bound context.
func NewHPKEInfo(
	namespaceID protocol.NamespaceID,
	deviceID protocol.DeviceID,
	recipientPublicKey HPKEPublicKey,
	generation uint64,
	issuanceSequence uint64,
	purpose HPKEKeyPurpose,
	objectType protocol.ObjectType,
	envelopeID EnvelopeID,
) HPKEInfo {
	return HPKEInfo{
		ProtocolID:              protocol.ProtocolID,
		ProtocolVersion:         protocol.ProtocolVersion,
		SuiteID:                 protocol.SuiteID,
		NamespaceID:             namespaceID,
		DeviceID:                deviceID,
		RecipientKeyFingerprint: HPKEPublicKeyFingerprint(recipientPublicKey),
		KeyGeneration:           generation,
		IssuanceSequence:        issuanceSequence,
		KeyPurpose:              purpose,
		ObjectType:              objectType,
		EnvelopeID:              envelopeID,
	}
}

// HPKEPublicKeyFingerprint is the fixed SHA-256 identifier bound into Info.
func HPKEPublicKeyFingerprint(publicKey HPKEPublicKey) [sha256.Size]byte {
	return sha256.Sum256(publicKey[:])
}

// GenerateEnvelopeID obtains an identifier directly from the OS CSPRNG.
func GenerateEnvelopeID() (EnvelopeID, error) {
	var id EnvelopeID
	if _, err := io.ReadFull(rand.Reader, id[:]); err != nil {
		return EnvelopeID{}, err
	}
	return id, nil
}

// GenerateHPKEKeyPair generates an independent X25519 HPKE key pair.
func GenerateHPKEKeyPair() (HPKEPublicKey, *HPKEPrivateKey, error) {
	publicKey, privateKey, err := hpke.KEM_X25519_HKDF_SHA256.Scheme().GenerateKeyPair()
	if err != nil {
		return HPKEPublicKey{}, nil, err
	}
	publicBytes, err := publicKey.MarshalBinary()
	if err != nil || len(publicBytes) != HPKEPublicKeySize {
		return HPKEPublicKey{}, nil, ErrRejectHPKE
	}
	privateBytes, err := privateKey.MarshalBinary()
	if err != nil || len(privateBytes) != HPKEPrivateKeySize {
		return HPKEPublicKey{}, nil, ErrRejectHPKE
	}

	var public HPKEPublicKey
	copy(public[:], publicBytes)
	private := &HPKEPrivateKey{state: &hpkePrivateKeyState{}}
	copy(private.state.raw[:], privateBytes)
	wipeHPKEBytes(privateBytes)
	return public, private, nil
}

// ParseHPKEPublicKey accepts only the frozen 32-byte X25519 encoding.
func ParseHPKEPublicKey(raw []byte) (HPKEPublicKey, error) {
	if len(raw) != HPKEPublicKeySize {
		return HPKEPublicKey{}, ErrRejectHPKE
	}
	if _, err := hpke.KEM_X25519_HKDF_SHA256.Scheme().UnmarshalBinaryPublicKey(raw); err != nil {
		return HPKEPublicKey{}, ErrRejectHPKE
	}
	var key HPKEPublicKey
	copy(key[:], raw)
	if err := validateHPKEPublicKey(key); err != nil {
		return HPKEPublicKey{}, ErrRejectHPKE
	}
	return key, nil
}

// Bytes returns a defensive copy suitable for a root-signed public object.
func (key HPKEPublicKey) Bytes() []byte {
	result := make([]byte, len(key))
	copy(result, key[:])
	return result
}

// Destroy makes subsequent use fail and best-effort overwrites key bytes.
func (key *HPKEPrivateKey) Destroy() {
	if key == nil || key.state == nil {
		return
	}
	key.state.mu.Lock()
	defer key.state.mu.Unlock()
	if key.state.destroyed {
		return
	}
	wipeHPKEBytes(key.state.raw[:])
	key.state.destroyed = true
}

func (HPKEPrivateKey) String() string   { return "[REDACTED HPKE PRIVATE KEY]" }
func (HPKEPrivateKey) GoString() string { return "[REDACTED HPKE PRIVATE KEY]" }

// Format redacts even byte-oriented verbs such as %x.
func (HPKEPrivateKey) Format(state fmt.State, _ rune) {
	_, _ = io.WriteString(state, "[REDACTED HPKE PRIVATE KEY]")
}

func (HPKEPrivateKey) MarshalJSON() ([]byte, error) {
	return nil, ErrHPKEPrivateKeySerialization
}

func (HPKEPrivateKey) MarshalText() ([]byte, error) {
	return nil, ErrHPKEPrivateKeySerialization
}

// LogValue prevents structured logging from reflecting private state.
func (HPKEPrivateKey) LogValue() slog.Value {
	return slog.StringValue("[REDACTED HPKE PRIVATE KEY]")
}

// SealHPKE creates a fresh Base Mode context for exactly one plaintext.
func SealHPKE(
	publicKey HPKEPublicKey,
	info HPKEInfo,
	plaintext *Secret,
) (HPKEEnvelope, error) {
	if plaintext == nil || plaintext.Len() == 0 || plaintext.Len() > MaxHPKEPlaintext {
		return HPKEEnvelope{}, ErrRejectHPKE
	}
	if err := validateHPKEPublicKey(publicKey); err != nil {
		return HPKEEnvelope{}, ErrRejectHPKE
	}
	fingerprint := HPKEPublicKeyFingerprint(publicKey)
	if subtle.ConstantTimeCompare(
		fingerprint[:],
		info.RecipientKeyFingerprint[:],
	) != 1 {
		return HPKEEnvelope{}, ErrRejectHPKE
	}
	infoBytes, err := marshalAndValidateHPKEInfo(info)
	if err != nil {
		return HPKEEnvelope{}, ErrRejectHPKE
	}
	parsedPublic, err := hpke.KEM_X25519_HKDF_SHA256.Scheme().UnmarshalBinaryPublicKey(publicKey[:])
	if err != nil {
		return HPKEEnvelope{}, ErrRejectHPKE
	}
	sender, err := hpkeSuite.NewSender(parsedPublic, infoBytes)
	if err != nil {
		return HPKEEnvelope{}, ErrRejectHPKE
	}
	enc, sealer, err := sender.Setup(rand.Reader)
	if err != nil {
		return HPKEEnvelope{}, ErrRejectHPKE
	}
	var ciphertext []byte
	err = plaintext.withBytes(func(raw []byte) error {
		sealed, sealErr := sealer.Seal(raw, infoBytes)
		if sealErr != nil {
			return ErrRejectHPKE
		}
		ciphertext = sealed
		return nil
	})
	if err != nil {
		wipeHPKEBytes(ciphertext)
		return HPKEEnvelope{}, ErrRejectHPKE
	}
	return HPKEEnvelope{
		Version:    protocol.ProtocolVersion,
		Enc:        cloneHPKEBytes(enc),
		Ciphertext: cloneHPKEBytes(ciphertext),
		InfoHash:   sha256.Sum256(infoBytes),
	}, nil
}

// OpenHPKE fails closed for every malformed key, context, or envelope.
func OpenHPKE(
	privateKey *HPKEPrivateKey,
	info HPKEInfo,
	envelope HPKEEnvelope,
) (*Secret, error) {
	if privateKey == nil || privateKey.state == nil || envelope.Version != protocol.ProtocolVersion ||
		len(envelope.Enc) != HPKEEncSize || len(envelope.Ciphertext) < HPKETagSize ||
		len(envelope.Ciphertext) > MaxHPKEPlaintext+HPKETagSize {
		return nil, ErrRejectHPKE
	}
	infoBytes, err := marshalAndValidateHPKEInfo(info)
	if err != nil || sha256.Sum256(infoBytes) != envelope.InfoHash {
		return nil, ErrRejectHPKE
	}
	var plaintext *Secret
	err = privateKey.withBytes(func(privateBytes []byte) error {
		publicBytes, publicErr := curve25519.X25519(privateBytes, curve25519.Basepoint)
		if publicErr != nil {
			return ErrRejectHPKE
		}
		fingerprint := sha256.Sum256(publicBytes)
		wipeHPKEBytes(publicBytes)
		if subtle.ConstantTimeCompare(
			fingerprint[:],
			info.RecipientKeyFingerprint[:],
		) != 1 {
			return ErrRejectHPKE
		}
		parsedPrivate, parseErr := hpke.KEM_X25519_HKDF_SHA256.Scheme().UnmarshalBinaryPrivateKey(privateBytes)
		if parseErr != nil {
			return ErrRejectHPKE
		}
		receiver, receiverErr := hpkeSuite.NewReceiver(parsedPrivate, infoBytes)
		if receiverErr != nil {
			return ErrRejectHPKE
		}
		opener, setupErr := receiver.Setup(envelope.Enc)
		if setupErr != nil {
			return ErrRejectHPKE
		}
		opened, openErr := opener.Open(envelope.Ciphertext, infoBytes)
		if openErr != nil {
			return ErrRejectHPKE
		}
		defer wipeHPKEBytes(opened)
		secret, secretErr := NewSecret(opened)
		if secretErr != nil {
			return ErrRejectHPKE
		}
		plaintext = secret
		return nil
	})
	if err != nil {
		if plaintext != nil {
			plaintext.Destroy()
		}
		return nil, ErrRejectHPKE
	}
	return plaintext, nil
}

// SealRootBundleHPKE transfers the complete root bundle only through the
// recipient-bound HPKE context. RootSecretBundle remains non-serializable to
// callers and plaintext bytes are wiped before return.
func SealRootBundleHPKE(
	publicKey HPKEPublicKey,
	info HPKEInfo,
	bundle *RootSecretBundle,
) (HPKEEnvelope, error) {
	if bundle == nil || info.KeyPurpose != HPKEPurposeRootBundle {
		return HPKEEnvelope{}, ErrRejectHPKE
	}
	wire, err := bundle.toWire()
	if err != nil {
		return HPKEEnvelope{}, ErrRejectHPKE
	}
	defer wipeRootBundleWire(&wire)
	encoded, err := protocol.MarshalDeterministic(wire)
	if err != nil {
		return HPKEEnvelope{}, ErrRejectHPKE
	}
	defer wipeHPKEBytes(encoded)
	plaintext, err := NewSecret(encoded)
	if err != nil {
		return HPKEEnvelope{}, ErrRejectHPKE
	}
	defer plaintext.Destroy()
	return SealHPKE(publicKey, info, plaintext)
}

// OpenRootBundleHPKE opens and validates an HPKE-transferred root bundle. The
// generic plaintext handle is destroyed before the validated bundle escapes.
func OpenRootBundleHPKE(
	privateKey *HPKEPrivateKey,
	info HPKEInfo,
	envelope HPKEEnvelope,
) (*RootSecretBundle, error) {
	if info.KeyPurpose != HPKEPurposeRootBundle {
		return nil, ErrRejectHPKE
	}
	plaintext, err := OpenHPKE(privateKey, info, envelope)
	if err != nil {
		return nil, ErrRejectHPKE
	}
	defer plaintext.Destroy()
	var wire rootSecretBundleWire
	if err := plaintext.withBytes(func(raw []byte) error {
		return protocol.UnmarshalDeterministic(raw, &wire)
	}); err != nil {
		return nil, ErrRejectHPKE
	}
	defer wipeRootBundleWire(&wire)
	bundle, err := rootBundleFromWire(wire)
	if err != nil {
		return nil, ErrRejectHPKE
	}
	return bundle, nil
}

// MarshalBinary returns the canonical opaque SecretEnvelope bytes. HPKE Info
// is carried separately by the signed enrollment or generation record and is
// cryptographically bound through InfoHash.
func (envelope HPKEEnvelope) MarshalBinary() ([]byte, error) {
	if validateHPKEEnvelope(envelope) != nil {
		return nil, ErrRejectHPKE
	}
	encoded, err := protocol.MarshalDeterministic(hpkeEnvelopeWire{
		ProtocolID: protocol.ProtocolID, ProtocolVersion: protocol.ProtocolVersion,
		SuiteID: protocol.SuiteID, ObjectType: protocol.ObjectTypeSecretEnvelope,
		Version: envelope.Version, Enc: envelope.Enc,
		Ciphertext: envelope.Ciphertext, InfoHash: envelope.InfoHash,
	})
	if err != nil {
		return nil, ErrRejectHPKE
	}
	return encoded, nil
}

// ParseHPKEEnvelope strictly parses canonical SecretEnvelope bytes. AEAD and
// recipient context are still verified only by OpenHPKE.
func ParseHPKEEnvelope(encoded []byte) (HPKEEnvelope, error) {
	var wire hpkeEnvelopeWire
	if err := protocol.UnmarshalDeterministic(encoded, &wire); err != nil ||
		wire.ProtocolID != protocol.ProtocolID ||
		wire.ProtocolVersion != protocol.ProtocolVersion ||
		wire.SuiteID != protocol.SuiteID ||
		wire.ObjectType != protocol.ObjectTypeSecretEnvelope {
		return HPKEEnvelope{}, ErrRejectHPKE
	}
	canonical, err := protocol.MarshalDeterministic(wire)
	if err != nil || subtle.ConstantTimeCompare(canonical, encoded) != 1 {
		return HPKEEnvelope{}, ErrRejectHPKE
	}
	envelope := HPKEEnvelope{
		Version: wire.Version, Enc: cloneHPKEBytes(wire.Enc),
		Ciphertext: cloneHPKEBytes(wire.Ciphertext), InfoHash: wire.InfoHash,
	}
	if validateHPKEEnvelope(envelope) != nil {
		return HPKEEnvelope{}, ErrRejectHPKE
	}
	return envelope, nil
}

// Clone returns a defensive copy for durable outbox persistence and retry.
func (envelope HPKEEnvelope) Clone() HPKEEnvelope {
	return HPKEEnvelope{
		Version:    envelope.Version,
		Enc:        cloneHPKEBytes(envelope.Enc),
		Ciphertext: cloneHPKEBytes(envelope.Ciphertext),
		InfoHash:   envelope.InfoHash,
	}
}

func validateHPKEEnvelope(envelope HPKEEnvelope) error {
	if envelope.Version != protocol.ProtocolVersion ||
		len(envelope.Enc) != HPKEEncSize ||
		len(envelope.Ciphertext) < HPKETagSize ||
		len(envelope.Ciphertext) > MaxHPKEPlaintext+HPKETagSize ||
		allZeroHPKE(envelope.InfoHash[:]) {
		return ErrRejectHPKE
	}
	return nil
}

func marshalAndValidateHPKEInfo(info HPKEInfo) ([]byte, error) {
	if info.ProtocolID != protocol.ProtocolID || info.ProtocolVersion != protocol.ProtocolVersion ||
		info.SuiteID != protocol.SuiteID || info.KeyGeneration == 0 ||
		info.IssuanceSequence == 0 || info.ObjectType != protocol.ObjectTypeSecretEnvelope ||
		(info.KeyPurpose != HPKEPurposeRootBundle && info.KeyPurpose != HPKEPurposeSecretGeneration) ||
		allZeroHPKE(info.NamespaceID[:]) || allZeroHPKE(info.DeviceID[:]) ||
		allZeroHPKE(info.RecipientKeyFingerprint[:]) || allZeroHPKE(info.EnvelopeID[:]) {
		return nil, ErrRejectHPKE
	}
	encoded, err := protocol.MarshalDeterministic(info)
	if err != nil {
		return nil, ErrRejectHPKE
	}
	return encoded, nil
}

func (key *HPKEPrivateKey) withBytes(fn func([]byte) error) error {
	if key == nil || key.state == nil || fn == nil {
		return ErrRejectHPKE
	}
	key.state.mu.RLock()
	if key.state.destroyed {
		key.state.mu.RUnlock()
		return ErrRejectHPKE
	}
	privateBytes := cloneHPKEBytes(key.state.raw[:])
	key.state.mu.RUnlock()
	defer wipeHPKEBytes(privateBytes)
	return fn(privateBytes)
}

func cloneHPKEBytes(input []byte) []byte {
	return append([]byte(nil), input...)
}

func wipeHPKEBytes(input []byte) {
	wipe(input)
}

func allZeroHPKE(input []byte) bool {
	var combined byte
	for _, value := range input {
		combined |= value
	}
	return combined == 0
}

// validateHPKEPublicKey rejects X25519 low-order inputs at registration and
// again at use. CIRCL's binary parser intentionally accepts every 32-byte
// string, while RFC 7748 requires consumers to reject an all-zero shared
// secret. The scalar is a public validation constant, not key material.
func validateHPKEPublicKey(publicKey HPKEPublicKey) error {
	validationScalar := sha256.Sum256([]byte(protocol.DomainPrefix + "HPKE-PUBLIC-KEY-VALIDATION"))
	shared, err := curve25519.X25519(validationScalar[:], publicKey[:])
	wipeHPKEBytes(validationScalar[:])
	if err != nil {
		wipeHPKEBytes(shared)
		return ErrRejectHPKE
	}
	invalid := allZeroHPKE(shared)
	wipeHPKEBytes(shared)
	if invalid {
		return ErrRejectHPKE
	}
	return nil
}
