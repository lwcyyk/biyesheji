package domain

import (
	"bytes"
	"crypto/ed25519"
	"crypto/sha256"
	"crypto/subtle"
	"errors"
	"sort"

	"vdns.local/vdns/internal/cryptokit"
	"vdns.local/vdns/internal/protocol"
)

const (
	// DeviceOperationCredentialVersion is the schema version inside the
	// VDNS-PM/2 signed payload. It is distinct from ProtocolVersion and from a
	// password credential's lifecycle version.
	DeviceOperationCredentialVersion = uint64(1)
	MaxDeviceScopeItems              = 4096
)

var (
	ErrInvalidDeviceCredential   = errors.New("invalid device operation credential")
	ErrDeviceCredentialSignature = errors.New("device operation credential signature verification failed")
	ErrDeviceCredentialContext   = errors.New("device operation credential context mismatch")
	ErrDeviceUnauthorized        = errors.New("device operation is not authorized")
	ErrDeviceCredentialStale     = errors.New("device operation credential is stale")
)

// CredentialScope is the canonical private scope contained in a root-signed
// device credential. Exactly one representation is permitted for each Type.
// Set values are sorted and deduplicated before signing.
type CredentialScope struct {
	Type             protocol.CredentialScopeType        `cbor:"type"`
	CredentialIDs    []protocol.CredentialID             `cbor:"credential_ids"`
	OriginBindings   [][cryptokit.OriginBindingSize]byte `cbor:"origin_bindings"`
	SingleCredential *protocol.CredentialID              `cbor:"single_credential"`
}

// NewNamespaceScope authorizes every credential in the namespace.
func NewNamespaceScope() CredentialScope {
	return CredentialScope{Type: protocol.ScopeNamespaceAll}
}

// NewCredentialSetScope returns a canonical sorted, deduplicated set scope.
func NewCredentialSetScope(ids []protocol.CredentialID) (CredentialScope, error) {
	if len(ids) == 0 || len(ids) > MaxDeviceScopeItems {
		return CredentialScope{}, ErrInvalidDeviceCredential
	}
	normalized := append([]protocol.CredentialID(nil), ids...)
	sort.Slice(normalized, func(i, j int) bool {
		return bytes.Compare(normalized[i][:], normalized[j][:]) < 0
	})
	normalized = deduplicateCredentialIDs(normalized)
	scope := CredentialScope{Type: protocol.ScopeCredentialSet, CredentialIDs: normalized}
	if err := scope.Validate(); err != nil {
		return CredentialScope{}, err
	}
	return scope, nil
}

// NewOriginBindingSetScope returns a canonical sorted, deduplicated set scope.
func NewOriginBindingSetScope(
	bindings [][cryptokit.OriginBindingSize]byte,
) (CredentialScope, error) {
	if len(bindings) == 0 || len(bindings) > MaxDeviceScopeItems {
		return CredentialScope{}, ErrInvalidDeviceCredential
	}
	normalized := append([][cryptokit.OriginBindingSize]byte(nil), bindings...)
	sort.Slice(normalized, func(i, j int) bool {
		return bytes.Compare(normalized[i][:], normalized[j][:]) < 0
	})
	normalized = deduplicateOriginBindings(normalized)
	scope := CredentialScope{Type: protocol.ScopeOriginBindingSet, OriginBindings: normalized}
	if err := scope.Validate(); err != nil {
		return CredentialScope{}, err
	}
	return scope, nil
}

// NewSingleCredentialScope authorizes one exact CredentialID.
func NewSingleCredentialScope(id protocol.CredentialID) (CredentialScope, error) {
	if operationBytesAllZero(id[:]) {
		return CredentialScope{}, ErrInvalidDeviceCredential
	}
	return CredentialScope{
		Type:             protocol.ScopeSingleCredential,
		SingleCredential: &id,
	}, nil
}

// Validate rejects non-canonical or ambiguous scope representations.
func (scope CredentialScope) Validate() error {
	if !scope.Type.Valid() {
		return ErrInvalidDeviceCredential
	}
	switch scope.Type {
	case protocol.ScopeNamespaceAll:
		if scope.CredentialIDs != nil || scope.OriginBindings != nil || scope.SingleCredential != nil {
			return ErrInvalidDeviceCredential
		}
	case protocol.ScopeCredentialSet:
		if len(scope.CredentialIDs) == 0 || len(scope.CredentialIDs) > MaxDeviceScopeItems ||
			scope.OriginBindings != nil || scope.SingleCredential != nil ||
			!credentialIDsCanonical(scope.CredentialIDs) {
			return ErrInvalidDeviceCredential
		}
	case protocol.ScopeOriginBindingSet:
		if len(scope.OriginBindings) == 0 || len(scope.OriginBindings) > MaxDeviceScopeItems ||
			scope.CredentialIDs != nil || scope.SingleCredential != nil ||
			!originBindingsCanonical(scope.OriginBindings) {
			return ErrInvalidDeviceCredential
		}
	case protocol.ScopeSingleCredential:
		if scope.CredentialIDs != nil || scope.OriginBindings != nil ||
			scope.SingleCredential == nil || operationBytesAllZero(scope.SingleCredential[:]) {
			return ErrInvalidDeviceCredential
		}
	default:
		return ErrInvalidDeviceCredential
	}
	return nil
}

// Digest commits to the canonical private scope without exposing its members
// in public status rows or log leaves.
func (scope CredentialScope) Digest() ([sha256.Size]byte, error) {
	if err := scope.Validate(); err != nil {
		return [sha256.Size]byte{}, err
	}
	input := struct {
		Domain string          `cbor:"domain"`
		Scope  CredentialScope `cbor:"scope"`
	}{
		Domain: protocol.DomainPrefix + "DEVICE-CREDENTIAL-SCOPE",
		Scope:  cloneCredentialScope(scope),
	}
	encoded, err := protocol.MarshalDeterministic(input)
	if err != nil {
		return [sha256.Size]byte{}, ErrInvalidDeviceCredential
	}
	return sha256.Sum256(encoded), nil
}

// DeviceOperationCredentialPayload is the complete root-authorized projection
// used by L1/L2 verification. Wall-clock time is deliberately absent: validity
// and revocation are evaluated against final log sequence.
type DeviceOperationCredentialPayload struct {
	CredentialVersion  uint64                      `cbor:"credential_version"`
	NamespaceID        protocol.NamespaceID        `cbor:"namespace_id"`
	DeviceID           protocol.DeviceID           `cbor:"device_id"`
	AuthPublicKey      [ed25519.PublicKeySize]byte `cbor:"auth_public_key"`
	HPKEPublicKey      cryptokit.HPKEPublicKey     `cbor:"hpke_public_key"`
	Capabilities       protocol.Capability         `cbor:"capability_bits"`
	Scope              CredentialScope             `cbor:"credential_scope"`
	ScopeDigest        [sha256.Size]byte           `cbor:"scope_digest"`
	ValidFromSequence  uint64                      `cbor:"valid_from_sequence"`
	ValidUntilSequence uint64                      `cbor:"valid_until_sequence"`
	IssuanceCounter    uint64                      `cbor:"issuance_counter"`
	StatusReference    [sha256.Size]byte           `cbor:"status_ref"`
	SecretGeneration   uint64                      `cbor:"secret_generation"`
}

// Validate enforces all state-independent credential invariants.
func (payload DeviceOperationCredentialPayload) Validate() error {
	if payload.CredentialVersion != DeviceOperationCredentialVersion ||
		operationBytesAllZero(payload.NamespaceID[:]) || operationBytesAllZero(payload.DeviceID[:]) ||
		operationBytesAllZero(payload.AuthPublicKey[:]) || !payload.Capabilities.Valid() ||
		payload.ValidFromSequence == 0 ||
		payload.ValidUntilSequence < payload.ValidFromSequence ||
		payload.IssuanceCounter == 0 || operationBytesAllZero(payload.StatusReference[:]) ||
		payload.SecretGeneration == 0 {
		return ErrInvalidDeviceCredential
	}
	if _, err := cryptokit.ParseHPKEPublicKey(payload.HPKEPublicKey[:]); err != nil {
		return ErrInvalidDeviceCredential
	}
	if err := payload.Scope.Validate(); err != nil {
		return ErrInvalidDeviceCredential
	}
	digest, err := payload.Scope.Digest()
	if err != nil || subtle.ConstantTimeCompare(digest[:], payload.ScopeDigest[:]) != 1 {
		return ErrInvalidDeviceCredential
	}
	return nil
}

// SignedDeviceOperationCredential owns the exact canonical signed bytes.
type SignedDeviceOperationCredential struct {
	payload   DeviceOperationCredentialPayload
	sigInput  []byte
	signature protocol.Signature
	digest    [sha256.Size]byte
}

type signedDeviceCredentialWire struct {
	SigInputCBOR []byte             `cbor:"sig_input_cbor"`
	Signature    protocol.Signature `cbor:"signature"`
}

// IssueDeviceOperationCredential creates a root-signed v2 device credential.
func IssueDeviceOperationCredential(
	rootPrivateKey ed25519.PrivateKey,
	chainID string,
	rootKeyGeneration uint64,
	payload DeviceOperationCredentialPayload,
) (*SignedDeviceOperationCredential, error) {
	if err := payload.Validate(); err != nil || len(rootPrivateKey) != ed25519.PrivateKeySize {
		return nil, ErrInvalidDeviceCredential
	}
	rootPublicKey, ok := rootPrivateKey.Public().(ed25519.PublicKey)
	if !ok {
		return nil, ErrInvalidDeviceCredential
	}
	rootKeyID, err := protocol.KeyIDFromPublicKey(rootPublicKey)
	if err != nil {
		return nil, ErrInvalidDeviceCredential
	}
	payloadCBOR, err := protocol.MarshalDeterministic(payload)
	if err != nil {
		return nil, ErrInvalidDeviceCredential
	}
	input := protocol.NewSigInput(
		protocol.ObjectTypeDeviceCredential,
		chainID,
		payload.NamespaceID,
		rootKeyID,
		rootKeyGeneration,
		payloadCBOR,
	)
	signature, err := protocol.Sign(rootPrivateKey, input)
	if err != nil {
		return nil, errors.Join(ErrDeviceCredentialSignature, err)
	}
	encoded, err := protocol.EncodeSigInput(input)
	if err != nil {
		return nil, ErrInvalidDeviceCredential
	}
	return newSignedDeviceCredential(payload, encoded, signature), nil
}

// ParseAndVerifyDeviceOperationCredential verifies the root trust context and
// canonical payload before returning a credential usable for authorization.
func ParseAndVerifyDeviceOperationCredential(
	encodedSigInput []byte,
	signature protocol.Signature,
	rootPublicKey ed25519.PublicKey,
	expected protocol.VerificationContext,
) (*SignedDeviceOperationCredential, error) {
	var input protocol.SigInput
	if err := protocol.UnmarshalDeterministic(encodedSigInput, &input); err != nil {
		return nil, ErrInvalidDeviceCredential
	}
	if err := protocol.Verify(rootPublicKey, input, signature, expected); err != nil {
		return nil, errors.Join(ErrDeviceCredentialSignature, err)
	}
	if input.ObjectType != protocol.ObjectTypeDeviceCredential {
		return nil, ErrDeviceCredentialContext
	}
	var payload DeviceOperationCredentialPayload
	if err := protocol.UnmarshalDeterministic(input.Payload, &payload); err != nil ||
		payload.Validate() != nil {
		return nil, ErrInvalidDeviceCredential
	}
	if subtle.ConstantTimeCompare(payload.NamespaceID[:], input.NamespaceID[:]) != 1 {
		return nil, ErrDeviceCredentialContext
	}
	canonical, err := protocol.EncodeSigInput(input)
	if err != nil || subtle.ConstantTimeCompare(canonical, encodedSigInput) != 1 {
		return nil, ErrInvalidDeviceCredential
	}
	return newSignedDeviceCredential(payload, canonical, signature), nil
}

// DeviceAuthorizationContext contains the receiver's final-sequence state.
// Every value must be loaded from trusted local/VDNS state, never the event.
type DeviceAuthorizationContext struct {
	NamespaceID             protocol.NamespaceID
	DeviceID                protocol.DeviceID
	Operation               protocol.OperationType
	CredentialID            *protocol.CredentialID
	OriginBinding           *[cryptokit.OriginBindingSize]byte
	FinalSequence           uint64
	CurrentIssuanceCounter  uint64
	CurrentStatusReference  [sha256.Size]byte
	CurrentSecretGeneration uint64
	RevokedAtSequence       *uint64
}

// AuthorizeDeviceOperation evaluates capability, scope, final-sequence
// validity, revocation, issuance freshness, status reference and generation.
func AuthorizeDeviceOperation(
	credential *SignedDeviceOperationCredential,
	context DeviceAuthorizationContext,
) error {
	if credential == nil || credential.payload.Validate() != nil ||
		!context.Operation.Valid() || context.FinalSequence == 0 ||
		context.CurrentIssuanceCounter == 0 ||
		operationBytesAllZero(context.CurrentStatusReference[:]) ||
		context.CurrentSecretGeneration == 0 {
		return ErrDeviceUnauthorized
	}
	payload := credential.payload
	if subtle.ConstantTimeCompare(payload.NamespaceID[:], context.NamespaceID[:]) != 1 ||
		subtle.ConstantTimeCompare(payload.DeviceID[:], context.DeviceID[:]) != 1 {
		return ErrDeviceCredentialContext
	}
	if context.FinalSequence < payload.ValidFromSequence ||
		context.FinalSequence > payload.ValidUntilSequence {
		return ErrDeviceCredentialStale
	}
	if context.RevokedAtSequence != nil && context.FinalSequence >= *context.RevokedAtSequence {
		return ErrDeviceCredentialStale
	}
	if payload.IssuanceCounter != context.CurrentIssuanceCounter ||
		payload.SecretGeneration != context.CurrentSecretGeneration ||
		subtle.ConstantTimeCompare(payload.StatusReference[:], context.CurrentStatusReference[:]) != 1 {
		return ErrDeviceCredentialStale
	}
	required, err := context.Operation.RequiredCapability()
	if err != nil || !payload.Capabilities.Allows(required) {
		return ErrDeviceUnauthorized
	}
	if !payload.Scope.allows(context.CredentialID, context.OriginBinding) {
		return ErrDeviceUnauthorized
	}
	return nil
}

// Payload returns a defensive copy of the signed payload.
func (credential *SignedDeviceOperationCredential) Payload() DeviceOperationCredentialPayload {
	if credential == nil {
		return DeviceOperationCredentialPayload{}
	}
	return cloneDeviceCredentialPayload(credential.payload)
}

// SigInputCBOR returns the exact canonical bytes covered by the signature.
func (credential *SignedDeviceOperationCredential) SigInputCBOR() []byte {
	if credential == nil {
		return nil
	}
	return append([]byte(nil), credential.sigInput...)
}

// Signature returns the fixed-size signature by value.
func (credential *SignedDeviceOperationCredential) Signature() protocol.Signature {
	if credential == nil {
		return protocol.Signature{}
	}
	return credential.signature
}

// Digest is SHA-256(canonical SigInput bytes || signature bytes).
func (credential *SignedDeviceOperationCredential) Digest() [sha256.Size]byte {
	if credential == nil {
		return [sha256.Size]byte{}
	}
	return credential.digest
}

// MarshalBinary returns the complete root-signed credential object.
func (credential *SignedDeviceOperationCredential) MarshalBinary() ([]byte, error) {
	if credential == nil || len(credential.sigInput) == 0 {
		return nil, ErrInvalidDeviceCredential
	}
	return protocol.MarshalDeterministic(signedDeviceCredentialWire{
		SigInputCBOR: credential.sigInput, Signature: credential.signature,
	})
}

// ParseAndVerifyDeviceOperationCredentialObject verifies complete object bytes
// with receiver-owned root trust context.
func ParseAndVerifyDeviceOperationCredentialObject(
	encoded []byte,
	rootPublicKey ed25519.PublicKey,
	expected protocol.VerificationContext,
) (*SignedDeviceOperationCredential, error) {
	var wire signedDeviceCredentialWire
	if err := protocol.UnmarshalDeterministic(encoded, &wire); err != nil ||
		len(wire.SigInputCBOR) == 0 {
		return nil, ErrInvalidDeviceCredential
	}
	canonical, err := protocol.MarshalDeterministic(wire)
	if err != nil || subtle.ConstantTimeCompare(canonical, encoded) != 1 {
		return nil, ErrInvalidDeviceCredential
	}
	return ParseAndVerifyDeviceOperationCredential(
		wire.SigInputCBOR, wire.Signature, rootPublicKey, expected,
	)
}

func newSignedDeviceCredential(
	payload DeviceOperationCredentialPayload,
	encoded []byte,
	signature protocol.Signature,
) *SignedDeviceOperationCredential {
	hasher := sha256.New()
	_, _ = hasher.Write(encoded)
	_, _ = hasher.Write(signature[:])
	var digest [sha256.Size]byte
	copy(digest[:], hasher.Sum(nil))
	return &SignedDeviceOperationCredential{
		payload:   cloneDeviceCredentialPayload(payload),
		sigInput:  append([]byte(nil), encoded...),
		signature: signature,
		digest:    digest,
	}
}

func cloneDeviceCredentialPayload(
	payload DeviceOperationCredentialPayload,
) DeviceOperationCredentialPayload {
	cloned := payload
	cloned.Scope = cloneCredentialScope(payload.Scope)
	return cloned
}

func cloneCredentialScope(scope CredentialScope) CredentialScope {
	cloned := scope
	cloned.CredentialIDs = append([]protocol.CredentialID(nil), scope.CredentialIDs...)
	cloned.OriginBindings = append([][cryptokit.OriginBindingSize]byte(nil), scope.OriginBindings...)
	if scope.SingleCredential != nil {
		value := *scope.SingleCredential
		cloned.SingleCredential = &value
	}
	return cloned
}

func (scope CredentialScope) allows(
	credentialID *protocol.CredentialID,
	originBinding *[cryptokit.OriginBindingSize]byte,
) bool {
	switch scope.Type {
	case protocol.ScopeNamespaceAll:
		return true
	case protocol.ScopeCredentialSet:
		if credentialID == nil {
			return false
		}
		match := 0
		for _, candidate := range scope.CredentialIDs {
			match |= subtle.ConstantTimeCompare(candidate[:], credentialID[:])
		}
		return match == 1
	case protocol.ScopeOriginBindingSet:
		if originBinding == nil {
			return false
		}
		match := 0
		for _, candidate := range scope.OriginBindings {
			match |= subtle.ConstantTimeCompare(candidate[:], originBinding[:])
		}
		return match == 1
	case protocol.ScopeSingleCredential:
		return credentialID != nil && scope.SingleCredential != nil &&
			subtle.ConstantTimeCompare(scope.SingleCredential[:], credentialID[:]) == 1
	default:
		return false
	}
}

// Allows evaluates one receiver-supplied target against the private scope.
// It is exported for the VDNS L2 verifier; callers must still verify the
// root-signed credential and current status reference before using the result.
func (scope CredentialScope) Allows(
	credentialID *protocol.CredentialID,
	originBinding *[cryptokit.OriginBindingSize]byte,
) bool {
	if scope.Validate() != nil {
		return false
	}
	return scope.allows(credentialID, originBinding)
}

func credentialIDsCanonical(ids []protocol.CredentialID) bool {
	for index, id := range ids {
		if operationBytesAllZero(id[:]) {
			return false
		}
		if index > 0 && bytes.Compare(ids[index-1][:], id[:]) >= 0 {
			return false
		}
	}
	return true
}

func originBindingsCanonical(bindings [][cryptokit.OriginBindingSize]byte) bool {
	for index, binding := range bindings {
		if operationBytesAllZero(binding[:]) {
			return false
		}
		if index > 0 && bytes.Compare(bindings[index-1][:], binding[:]) >= 0 {
			return false
		}
	}
	return true
}

func deduplicateCredentialIDs(ids []protocol.CredentialID) []protocol.CredentialID {
	result := ids[:0]
	for _, id := range ids {
		if len(result) == 0 || !bytes.Equal(result[len(result)-1][:], id[:]) {
			result = append(result, id)
		}
	}
	return result
}

func deduplicateOriginBindings(
	bindings [][cryptokit.OriginBindingSize]byte,
) [][cryptokit.OriginBindingSize]byte {
	result := bindings[:0]
	for _, binding := range bindings {
		if len(result) == 0 || !bytes.Equal(result[len(result)-1][:], binding[:]) {
			result = append(result, binding)
		}
	}
	return result
}

func operationBytesAllZero(input []byte) bool {
	var combined byte
	for _, value := range input {
		combined |= value
	}
	return combined == 0
}
