package cryptokit

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/hmac"
	"crypto/rand"
	"crypto/sha256"
	"crypto/subtle"
	"errors"
	"io"
	"unicode/utf8"

	"vdns.local/vdns/internal/protocol"
)

const (
	RouteCiphertextVersion = uint64(1)
	MaxRouteValueSize      = 4096
	MaxRouteCiphertextSize = 8192
)

var ErrRejectRouteCiphertext = errors.New("REJECT_ROUTE_CIPHERTEXT")

type (
	RouteID          [sha256.Size]byte
	RouteOriginIndex [sha256.Size]byte
)

type RouteValueType uint8

const (
	RouteValueOrigin  RouteValueType = 1
	RouteValueAccount RouteValueType = 2
)

func (valueType RouteValueType) valid() bool {
	return valueType == RouteValueOrigin || valueType == RouteValueAccount
}

// RouteContext binds one local encrypted route value to its namespace, exact
// private index, origin-only index and CAS version.
type RouteContext struct {
	NamespaceID  protocol.NamespaceID
	RouteID      RouteID
	OriginIndex  RouteOriginIndex
	RouteVersion uint64
	ValueType    RouteValueType
}

type routeAAD struct {
	Domain          string               `cbor:"domain"`
	ProtocolID      string               `cbor:"protocol_id"`
	ProtocolVersion uint64               `cbor:"protocol_version"`
	SuiteID         string               `cbor:"suite_id"`
	NamespaceID     protocol.NamespaceID `cbor:"namespace_id"`
	RouteID         RouteID              `cbor:"route_id"`
	OriginIndex     RouteOriginIndex     `cbor:"origin_index"`
	RouteVersion    uint64               `cbor:"route_version"`
	ValueType       RouteValueType       `cbor:"value_type"`
}

type routeCiphertextWire struct {
	Version    uint64             `cbor:"version"`
	Nonce      [GCMNonceSize]byte `cbor:"nonce"`
	AADHash    [sha256.Size]byte  `cbor:"aad_hash"`
	Ciphertext []byte             `cbor:"ciphertext"`
}

// RouteCiphertext is a deterministic wrapper around randomized local AEAD.
type RouteCiphertext struct {
	wire routeCiphertextWire
}

// DeriveRouteID creates the exact Origin+Account lookup key.
func DeriveRouteID(
	nameKey *Key,
	canonicalOrigin []byte,
	accountID []byte,
) (RouteID, error) {
	var result RouteID
	if !validRouteText(canonicalOrigin, maxCanonicalOrigin) ||
		!validRouteText(accountID, maxAccountIDBytes) {
		return result, ErrInvalidInput
	}
	input, err := encodeDomain(
		protocol.DomainPrefix+"ROUTE-ID",
		append([]byte(nil), canonicalOrigin...),
		append([]byte(nil), accountID...),
	)
	if err != nil {
		return result, err
	}
	defer wipe(input)
	err = nameKey.withPurposeBytes(purposeCredentialName, func(raw []byte) error {
		mac := hmac.New(sha256.New, raw)
		_, _ = mac.Write(input)
		sum := mac.Sum(nil)
		copy(result[:], sum)
		wipe(sum)
		return nil
	})
	if err != nil {
		wipe(result[:])
		return RouteID{}, err
	}
	return result, nil
}

// DeriveRouteOriginIndex creates a private origin-only index for efficient
// same-origin account enumeration without storing the Origin in plaintext.
func DeriveRouteOriginIndex(
	nameKey *Key,
	canonicalOrigin []byte,
) (RouteOriginIndex, error) {
	var result RouteOriginIndex
	if !validRouteText(canonicalOrigin, maxCanonicalOrigin) {
		return result, ErrInvalidInput
	}
	input, err := encodeDomain(
		protocol.DomainPrefix+"ROUTE-ORIGIN-INDEX",
		append([]byte(nil), canonicalOrigin...),
	)
	if err != nil {
		return result, err
	}
	defer wipe(input)
	err = nameKey.withPurposeBytes(purposeCredentialName, func(raw []byte) error {
		mac := hmac.New(sha256.New, raw)
		_, _ = mac.Write(input)
		sum := mac.Sum(nil)
		copy(result[:], sum)
		wipe(sum)
		return nil
	})
	if err != nil {
		wipe(result[:])
		return RouteOriginIndex{}, err
	}
	return result, nil
}

func EncryptRouteValue(
	nameKey *Key,
	context RouteContext,
	plaintext *Secret,
) (*RouteCiphertext, error) {
	return encryptRouteValueWithReader(nameKey, context, plaintext, rand.Reader)
}

func encryptRouteValueWithReader(
	nameKey *Key,
	context RouteContext,
	plaintext *Secret,
	random io.Reader,
) (*RouteCiphertext, error) {
	if nameKey == nil || plaintext == nil || plaintext.Len() == 0 ||
		plaintext.Len() > MaxRouteValueSize || random == nil ||
		validateRouteContext(context) != nil {
		return nil, ErrInvalidInput
	}
	aadBytes, err := protocol.MarshalDeterministic(routeAADFor(context))
	if err != nil {
		return nil, ErrInvalidInput
	}
	defer wipe(aadBytes)
	keyBytes, err := deriveRouteAEADKey(nameKey, context)
	if err != nil {
		return nil, err
	}
	defer wipe(keyBytes)
	block, err := aes.NewCipher(keyBytes)
	if err != nil {
		return nil, ErrInvalidInput
	}
	aead, err := cipher.NewGCM(block)
	if err != nil {
		return nil, ErrInvalidInput
	}
	var nonce [GCMNonceSize]byte
	if _, err := io.ReadFull(random, nonce[:]); err != nil || routeBytesAllZero(nonce[:]) {
		wipe(nonce[:])
		return nil, ErrRandomSource
	}
	var sealed []byte
	err = plaintext.withBytes(func(raw []byte) error {
		sealed = aead.Seal(nil, nonce[:], raw, aadBytes)
		return nil
	})
	if err != nil {
		wipe(sealed)
		return nil, err
	}
	return &RouteCiphertext{wire: routeCiphertextWire{
		Version: RouteCiphertextVersion, Nonce: nonce,
		AADHash: sha256.Sum256(aadBytes), Ciphertext: sealed,
	}}, nil
}

// OpenRouteValue authenticates all private indexes before returning a
// protected plaintext handle.
func OpenRouteValue(
	nameKey *Key,
	expected RouteContext,
	encrypted *RouteCiphertext,
) (*Secret, error) {
	if nameKey == nil || encrypted == nil ||
		validateRouteContext(expected) != nil ||
		validateRouteWire(encrypted.wire) != nil {
		return nil, ErrRejectRouteCiphertext
	}
	aadBytes, err := protocol.MarshalDeterministic(routeAADFor(expected))
	if err != nil || subtle.ConstantTimeCompare(
		sha256Sum(aadBytes), encrypted.wire.AADHash[:],
	) != 1 {
		wipe(aadBytes)
		return nil, ErrRejectRouteCiphertext
	}
	defer wipe(aadBytes)
	keyBytes, err := deriveRouteAEADKey(nameKey, expected)
	if err != nil {
		return nil, ErrRejectRouteCiphertext
	}
	defer wipe(keyBytes)
	block, err := aes.NewCipher(keyBytes)
	if err != nil {
		return nil, ErrRejectRouteCiphertext
	}
	aead, err := cipher.NewGCM(block)
	if err != nil {
		return nil, ErrRejectRouteCiphertext
	}
	opened, err := aead.Open(
		nil,
		encrypted.wire.Nonce[:],
		encrypted.wire.Ciphertext,
		aadBytes,
	)
	if err != nil || len(opened) == 0 || len(opened) > MaxRouteValueSize {
		wipe(opened)
		return nil, ErrRejectRouteCiphertext
	}
	defer wipe(opened)
	secret, err := NewSecret(opened)
	if err != nil {
		return nil, ErrRejectRouteCiphertext
	}
	return secret, nil
}

func (encrypted *RouteCiphertext) MarshalBinary() ([]byte, error) {
	if encrypted == nil || validateRouteWire(encrypted.wire) != nil {
		return nil, ErrInvalidInput
	}
	encoded, err := protocol.MarshalDeterministic(encrypted.wire)
	if err != nil || len(encoded) > MaxRouteCiphertextSize {
		return nil, ErrInvalidInput
	}
	return encoded, nil
}

func ParseRouteCiphertext(encoded []byte) (*RouteCiphertext, error) {
	if len(encoded) == 0 || len(encoded) > MaxRouteCiphertextSize {
		return nil, ErrRejectRouteCiphertext
	}
	var wire routeCiphertextWire
	if err := protocol.UnmarshalDeterministic(encoded, &wire); err != nil ||
		validateRouteWire(wire) != nil {
		return nil, ErrRejectRouteCiphertext
	}
	wire.Ciphertext = append([]byte(nil), wire.Ciphertext...)
	return &RouteCiphertext{wire: wire}, nil
}

func routeAADFor(context RouteContext) routeAAD {
	return routeAAD{
		Domain:     protocol.DomainPrefix + "ROUTE-MAP-AEAD",
		ProtocolID: protocol.ProtocolID, ProtocolVersion: protocol.ProtocolVersion,
		SuiteID: protocol.SuiteID, NamespaceID: context.NamespaceID,
		RouteID: context.RouteID, OriginIndex: context.OriginIndex,
		RouteVersion: context.RouteVersion, ValueType: context.ValueType,
	}
}

func deriveRouteAEADKey(nameKey *Key, context RouteContext) ([]byte, error) {
	input, err := encodeDomain(
		protocol.DomainPrefix+"ROUTE-MAP-KEY",
		context.NamespaceID,
		context.RouteID,
		context.OriginIndex,
		context.RouteVersion,
		uint64(context.ValueType),
	)
	if err != nil {
		return nil, err
	}
	defer wipe(input)
	var result []byte
	err = nameKey.withPurposeBytes(purposeCredentialName, func(raw []byte) error {
		mac := hmac.New(sha256.New, raw)
		_, _ = mac.Write(input)
		result = mac.Sum(nil)
		return nil
	})
	if err != nil {
		wipe(result)
		return nil, err
	}
	return result, nil
}

func validateRouteContext(context RouteContext) error {
	if routeBytesAllZero(context.NamespaceID[:]) ||
		routeBytesAllZero(context.RouteID[:]) ||
		routeBytesAllZero(context.OriginIndex[:]) ||
		context.RouteVersion == 0 || !context.ValueType.valid() {
		return ErrInvalidInput
	}
	return nil
}

func validateRouteWire(wire routeCiphertextWire) error {
	if wire.Version != RouteCiphertextVersion ||
		routeBytesAllZero(wire.Nonce[:]) || routeBytesAllZero(wire.AADHash[:]) ||
		len(wire.Ciphertext) < GCMTagSize ||
		len(wire.Ciphertext) > MaxRouteValueSize+GCMTagSize {
		return ErrRejectRouteCiphertext
	}
	return nil
}

func validRouteText(input []byte, maximum int) bool {
	return len(input) > 0 && len(input) <= maximum && utf8.Valid(input)
}

func sha256Sum(input []byte) []byte {
	sum := sha256.Sum256(input)
	return sum[:]
}

func routeBytesAllZero(input []byte) bool {
	var combined byte
	for _, value := range input {
		combined |= value
	}
	return combined == 0
}
