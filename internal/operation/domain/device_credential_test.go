package domain

import (
	"bytes"
	"crypto/ed25519"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"testing"

	"vpass.local/vpass/internal/cryptokit"
	"vpass.local/vpass/internal/protocol"
)

func TestDeviceCredentialRoundTripAndDefensiveCopies(t *testing.T) {
	t.Parallel()
	rootPrivate := deviceCredentialRootKey()
	rootPublic := rootPrivate.Public().(ed25519.PublicKey)
	payload := validDeviceCredentialPayload(t, NewNamespaceScope())

	credential, err := IssueDeviceOperationCredential(rootPrivate, "vpass-test-chain", 4, payload)
	if err != nil {
		t.Fatal(err)
	}
	parsed, err := ParseAndVerifyDeviceOperationCredential(
		credential.SigInputCBOR(),
		credential.Signature(),
		rootPublic,
		deviceCredentialVerificationContext(t, rootPublic, payload.NamespaceID, 4),
	)
	if err != nil {
		t.Fatal(err)
	}
	if parsed.Digest() != credential.Digest() ||
		parsed.Payload().DeviceID != payload.DeviceID {
		t.Fatal("round-trip changed device credential")
	}
	object, err := credential.MarshalBinary()
	if err != nil {
		t.Fatal(err)
	}
	parsedObject, err := ParseAndVerifyDeviceOperationCredentialObject(
		object, rootPublic,
		deviceCredentialVerificationContext(t, rootPublic, payload.NamespaceID, 4),
	)
	if err != nil || parsedObject.Digest() != credential.Digest() {
		t.Fatalf("complete object parse = %v, %v", parsedObject, err)
	}

	encoded := credential.SigInputCBOR()
	encoded[0] ^= 0xff
	if bytes.Equal(encoded, credential.SigInputCBOR()) {
		t.Fatal("SigInputCBOR exposed mutable storage")
	}
	setScope, err := NewCredentialSetScope([]protocol.CredentialID{
		filledCredentialID(0x44), filledCredentialID(0x55),
	})
	if err != nil {
		t.Fatal(err)
	}
	setPayload := validDeviceCredentialPayload(t, setScope)
	setCredential, err := IssueDeviceOperationCredential(rootPrivate, "vpass-test-chain", 4, setPayload)
	if err != nil {
		t.Fatal(err)
	}
	copiedPayload := setCredential.Payload()
	copiedPayload.Scope.CredentialIDs[0][0] ^= 0xff
	if setCredential.Payload().Scope.CredentialIDs[0] != setPayload.Scope.CredentialIDs[0] {
		t.Fatal("Payload exposed mutable scope storage")
	}
}

func TestDeviceCredentialRejectsTamperingAndContextReplay(t *testing.T) {
	t.Parallel()
	rootPrivate := deviceCredentialRootKey()
	rootPublic := rootPrivate.Public().(ed25519.PublicKey)
	payload := validDeviceCredentialPayload(t, NewNamespaceScope())
	credential, err := IssueDeviceOperationCredential(rootPrivate, "chain-a", 2, payload)
	if err != nil {
		t.Fatal(err)
	}
	expected := deviceCredentialVerificationContext(t, rootPublic, payload.NamespaceID, 2)
	expected.ChainID = "chain-a"

	tampered := credential.SigInputCBOR()
	tampered[len(tampered)-1] ^= 1
	if _, err := ParseAndVerifyDeviceOperationCredential(
		tampered, credential.Signature(), rootPublic, expected,
	); err == nil {
		t.Fatal("tampered signed input was accepted")
	}
	badSignature := credential.Signature()
	badSignature[0] ^= 1
	if _, err := ParseAndVerifyDeviceOperationCredential(
		credential.SigInputCBOR(), badSignature, rootPublic, expected,
	); !errors.Is(err, ErrDeviceCredentialSignature) {
		t.Fatalf("signature error = %v", err)
	}
	expected.ChainID = "chain-b"
	if _, err := ParseAndVerifyDeviceOperationCredential(
		credential.SigInputCBOR(), credential.Signature(), rootPublic, expected,
	); !errors.Is(err, ErrDeviceCredentialSignature) {
		t.Fatalf("context replay error = %v", err)
	}
}

func TestCredentialScopeCanonicalizationAndValidation(t *testing.T) {
	t.Parallel()
	low := filledCredentialID(0x11)
	high := filledCredentialID(0x88)
	scope, err := NewCredentialSetScope([]protocol.CredentialID{high, low, high})
	if err != nil {
		t.Fatal(err)
	}
	if len(scope.CredentialIDs) != 2 ||
		scope.CredentialIDs[0] != low || scope.CredentialIDs[1] != high {
		t.Fatal("credential scope was not sorted and deduplicated")
	}
	lowBinding := sha256.Sum256([]byte("binding-a"))
	highBinding := sha256.Sum256([]byte("binding-b"))
	if bytes.Compare(lowBinding[:], highBinding[:]) > 0 {
		lowBinding, highBinding = highBinding, lowBinding
	}
	originScope, err := NewOriginBindingSetScope(
		[][cryptokit.OriginBindingSize]byte{highBinding, lowBinding, highBinding},
	)
	if err != nil {
		t.Fatal(err)
	}
	if len(originScope.OriginBindings) != 2 ||
		originScope.OriginBindings[0] != lowBinding ||
		originScope.OriginBindings[1] != highBinding {
		t.Fatal("origin-binding scope was not sorted and deduplicated")
	}

	invalid := []CredentialScope{
		{},
		{Type: protocol.ScopeNamespaceAll, CredentialIDs: []protocol.CredentialID{low}},
		{Type: protocol.ScopeCredentialSet},
		{Type: protocol.ScopeCredentialSet, CredentialIDs: []protocol.CredentialID{high, low}},
		{Type: protocol.ScopeCredentialSet, CredentialIDs: []protocol.CredentialID{low, low}},
		{Type: protocol.ScopeOriginBindingSet},
		{Type: protocol.ScopeOriginBindingSet, OriginBindings: [][32]byte{{}}},
		{Type: protocol.ScopeSingleCredential},
	}
	for index, candidate := range invalid {
		if err := candidate.Validate(); !errors.Is(err, ErrInvalidDeviceCredential) {
			t.Fatalf("invalid scope %d error = %v", index, err)
		}
	}
	if _, err := NewCredentialSetScope(nil); !errors.Is(err, ErrInvalidDeviceCredential) {
		t.Fatalf("empty credential set error = %v", err)
	}
	if _, err := NewSingleCredentialScope(protocol.CredentialID{}); !errors.Is(err, ErrInvalidDeviceCredential) {
		t.Fatalf("zero single-credential error = %v", err)
	}
}

func TestDeviceCredentialPayloadValidation(t *testing.T) {
	t.Parallel()
	valid := validDeviceCredentialPayload(t, NewNamespaceScope())
	tests := []struct {
		name   string
		mutate func(*DeviceOperationCredentialPayload)
	}{
		{"schema version", func(value *DeviceOperationCredentialPayload) { value.CredentialVersion++ }},
		{"namespace", func(value *DeviceOperationCredentialPayload) { value.NamespaceID = protocol.NamespaceID{} }},
		{"device", func(value *DeviceOperationCredentialPayload) { value.DeviceID = protocol.DeviceID{} }},
		{"auth key", func(value *DeviceOperationCredentialPayload) { value.AuthPublicKey = [32]byte{} }},
		{"hpke key", func(value *DeviceOperationCredentialPayload) { value.HPKEPublicKey = cryptokit.HPKEPublicKey{} }},
		{"capability", func(value *DeviceOperationCredentialPayload) { value.Capabilities = 0 }},
		{"scope digest", func(value *DeviceOperationCredentialPayload) { value.ScopeDigest[0] ^= 1 }},
		{"valid from", func(value *DeviceOperationCredentialPayload) { value.ValidFromSequence = 0 }},
		{"valid range", func(value *DeviceOperationCredentialPayload) { value.ValidUntilSequence = value.ValidFromSequence - 1 }},
		{"counter", func(value *DeviceOperationCredentialPayload) { value.IssuanceCounter = 0 }},
		{"status", func(value *DeviceOperationCredentialPayload) { value.StatusReference = [32]byte{} }},
		{"generation", func(value *DeviceOperationCredentialPayload) { value.SecretGeneration = 0 }},
	}
	for _, test := range tests {
		test := test
		t.Run(test.name, func(t *testing.T) {
			value := cloneDeviceCredentialPayload(valid)
			test.mutate(&value)
			if err := value.Validate(); !errors.Is(err, ErrInvalidDeviceCredential) {
				t.Fatalf("validation error = %v", err)
			}
		})
	}
	if _, err := IssueDeviceOperationCredential(
		ed25519.PrivateKey{1}, "chain", 1, valid,
	); !errors.Is(err, ErrInvalidDeviceCredential) {
		t.Fatalf("short root key error = %v", err)
	}
}

func TestAuthorizeDeviceOperationNegativeMatrix(t *testing.T) {
	t.Parallel()
	target := filledCredentialID(0x51)
	scope, err := NewCredentialSetScope([]protocol.CredentialID{target})
	if err != nil {
		t.Fatal(err)
	}
	payload := validDeviceCredentialPayload(t, scope)
	payload.Capabilities = protocol.CapabilityRead |
		protocol.CapabilityAutofill |
		protocol.CapabilityUpdate
	credential := issueDeviceCredentialForTest(t, payload)
	base := validAuthorizationContext(payload, protocol.OperationAutofill)
	base.CredentialID = &target

	if err := AuthorizeDeviceOperation(credential, base); err != nil {
		t.Fatalf("valid authorization rejected: %v", err)
	}

	tests := []struct {
		name   string
		want   error
		mutate func(*DeviceAuthorizationContext)
	}{
		{"wrong namespace", ErrDeviceCredentialContext, func(value *DeviceAuthorizationContext) { value.NamespaceID[0] ^= 1 }},
		{"wrong device", ErrDeviceCredentialContext, func(value *DeviceAuthorizationContext) { value.DeviceID[0] ^= 1 }},
		{"before validity", ErrDeviceCredentialStale, func(value *DeviceAuthorizationContext) { value.FinalSequence = payload.ValidFromSequence - 1 }},
		{"after validity", ErrDeviceCredentialStale, func(value *DeviceAuthorizationContext) { value.FinalSequence = payload.ValidUntilSequence + 1 }},
		{"revoked", ErrDeviceCredentialStale, func(value *DeviceAuthorizationContext) {
			sequence := value.FinalSequence
			value.RevokedAtSequence = &sequence
		}},
		{"old issuance counter", ErrDeviceCredentialStale, func(value *DeviceAuthorizationContext) { value.CurrentIssuanceCounter++ }},
		{"old status reference", ErrDeviceCredentialStale, func(value *DeviceAuthorizationContext) { value.CurrentStatusReference[0] ^= 1 }},
		{"old secret generation", ErrDeviceCredentialStale, func(value *DeviceAuthorizationContext) { value.CurrentSecretGeneration++ }},
		{"missing capability", ErrDeviceUnauthorized, func(value *DeviceAuthorizationContext) { value.Operation = protocol.OperationRotate }},
		{"missing scope value", ErrDeviceUnauthorized, func(value *DeviceAuthorizationContext) { value.CredentialID = nil }},
		{"outside scope", ErrDeviceUnauthorized, func(value *DeviceAuthorizationContext) {
			other := filledCredentialID(0x99)
			value.CredentialID = &other
		}},
	}
	for _, test := range tests {
		test := test
		t.Run(test.name, func(t *testing.T) {
			context := cloneAuthorizationContext(base)
			test.mutate(&context)
			if err := AuthorizeDeviceOperation(credential, context); !errors.Is(err, test.want) {
				t.Fatalf("authorization error = %v; want %v", err, test.want)
			}
		})
	}
}

func TestAuthorizeDeviceOperationAllScopeTypes(t *testing.T) {
	t.Parallel()
	target := filledCredentialID(0x61)
	binding := sha256.Sum256([]byte("allowed origin binding"))
	tests := []struct {
		name          string
		scope         CredentialScope
		credentialID  *protocol.CredentialID
		originBinding *[cryptokit.OriginBindingSize]byte
	}{
		{"namespace", NewNamespaceScope(), nil, nil},
		{"credential set", mustCredentialSetScope(t, target), &target, nil},
		{"origin set", mustOriginSetScope(t, binding), nil, &binding},
		{"single credential", mustSingleCredentialScope(t, target), &target, nil},
	}
	for _, test := range tests {
		test := test
		t.Run(test.name, func(t *testing.T) {
			payload := validDeviceCredentialPayload(t, test.scope)
			credential := issueDeviceCredentialForTest(t, payload)
			context := validAuthorizationContext(payload, protocol.OperationResolve)
			context.CredentialID = test.credentialID
			context.OriginBinding = test.originBinding
			if err := AuthorizeDeviceOperation(credential, context); err != nil {
				t.Fatalf("scope authorization rejected: %v", err)
			}
		})
	}
}

func TestDeviceOperationCredentialFixedKAT(t *testing.T) {
	t.Parallel()
	target := filledCredentialID(0x72)
	payload := validDeviceCredentialPayload(t, mustSingleCredentialScope(t, target))
	// Frozen legacy wire test vector; the chain identifier is part of the signed bytes.
	credential, err := IssueDeviceOperationCredential(
		deviceCredentialRootKey(), "vdns-kat-chain", 9, payload,
	)
	if err != nil {
		t.Fatal(err)
	}
	encodedHash := sha256.Sum256(credential.SigInputCBOR())
	signature := credential.Signature()
	digest := credential.Digest()
	gotEncodedHash := hex.EncodeToString(encodedHash[:])
	gotSignature := hex.EncodeToString(signature[:])
	gotDigest := hex.EncodeToString(digest[:])
	const (
		wantEncodedHash = "96b6d8418fe694b2f45900c36d0d915f2fbea1581266c9948a85b5f0c690e5e0"
		wantSignature   = "75b3fdc09eca3a5a282b0876c930ddf82d3617ad0322b6a669fbcc05a36256458000af9da893403aa26f8d8e21559234bbac18a3d54940b206e60d3db2e8c708"
		wantDigest      = "6e72197e25093fb0df172fccbda57c51aafe5d1981c8894308d09da7c0e5ed38"
	)
	if gotEncodedHash != wantEncodedHash ||
		gotSignature != wantSignature ||
		gotDigest != wantDigest {
		t.Fatalf("update KAT: siginput_sha256=%s signature=%s digest=%s",
			gotEncodedHash, gotSignature, gotDigest)
	}
}

func FuzzParseAndVerifyDeviceOperationCredential(f *testing.F) {
	rootPrivate := deviceCredentialRootKey()
	rootPublic := rootPrivate.Public().(ed25519.PublicKey)
	target := filledCredentialID(0x72)
	payload := validDeviceCredentialPayload(f, mustSingleCredentialScope(f, target))
	credential, err := IssueDeviceOperationCredential(
		rootPrivate, "vpass-fuzz-chain", 5, payload,
	)
	if err != nil {
		f.Fatal(err)
	}
	signature := credential.Signature()
	f.Add(credential.SigInputCBOR(), signature[:])
	f.Add([]byte{0xa0}, bytes.Repeat([]byte{0}, ed25519.SignatureSize))

	keyID, err := protocol.KeyIDFromPublicKey(rootPublic)
	if err != nil {
		f.Fatal(err)
	}
	expected := protocol.VerificationContext{
		ObjectType:    protocol.ObjectTypeDeviceCredential,
		ChainID:       "vpass-fuzz-chain",
		NamespaceID:   payload.NamespaceID,
		KeyID:         keyID,
		KeyGeneration: 5,
	}
	f.Fuzz(func(t *testing.T, encoded, rawSignature []byte) {
		var candidate protocol.Signature
		if len(rawSignature) == len(candidate) {
			copy(candidate[:], rawSignature)
		}
		parsed, parseErr := ParseAndVerifyDeviceOperationCredential(
			encoded, candidate, rootPublic, expected,
		)
		if parseErr == nil {
			if parsed == nil || parsed.Payload().Validate() != nil {
				t.Fatal("accepted device credential is invalid")
			}
		}
	})
}

func validDeviceCredentialPayload(
	t testing.TB,
	scope CredentialScope,
) DeviceOperationCredentialPayload {
	t.Helper()
	digest, err := scope.Digest()
	if err != nil {
		t.Fatal(err)
	}
	authPrivate := ed25519.NewKeyFromSeed(bytes.Repeat([]byte{0x23}, ed25519.SeedSize))
	authPublic := authPrivate.Public().(ed25519.PublicKey)
	var authKey [ed25519.PublicKeySize]byte
	copy(authKey[:], authPublic)
	hpkeRaw, err := hex.DecodeString(
		"430f4b9859665145a6b1ba274024487bd66f03a2dd577d7753c68d7d7d00c00c",
	)
	if err != nil {
		t.Fatal(err)
	}
	hpkePublic, err := cryptokit.ParseHPKEPublicKey(hpkeRaw)
	if err != nil {
		t.Fatal(err)
	}
	var namespaceID protocol.NamespaceID
	copy(namespaceID[:], bytes.Repeat([]byte{0x31}, len(namespaceID)))
	var deviceID protocol.DeviceID
	copy(deviceID[:], bytes.Repeat([]byte{0x42}, len(deviceID)))
	return DeviceOperationCredentialPayload{
		CredentialVersion:  DeviceOperationCredentialVersion,
		NamespaceID:        namespaceID,
		DeviceID:           deviceID,
		AuthPublicKey:      authKey,
		HPKEPublicKey:      hpkePublic,
		Capabilities:       protocol.CapabilityRead | protocol.CapabilityAutofill,
		Scope:              scope,
		ScopeDigest:        digest,
		ValidFromSequence:  10,
		ValidUntilSequence: 20,
		IssuanceCounter:    7,
		StatusReference:    sha256.Sum256([]byte("active device status")),
		SecretGeneration:   3,
	}
}

func deviceCredentialRootKey() ed25519.PrivateKey {
	return ed25519.NewKeyFromSeed(bytes.Repeat([]byte{0x19}, ed25519.SeedSize))
}

func deviceCredentialVerificationContext(
	t testing.TB,
	publicKey ed25519.PublicKey,
	namespaceID protocol.NamespaceID,
	generation uint64,
) protocol.VerificationContext {
	t.Helper()
	keyID, err := protocol.KeyIDFromPublicKey(publicKey)
	if err != nil {
		t.Fatal(err)
	}
	return protocol.VerificationContext{
		ObjectType:    protocol.ObjectTypeDeviceCredential,
		ChainID:       "vpass-test-chain",
		NamespaceID:   namespaceID,
		KeyID:         keyID,
		KeyGeneration: generation,
	}
}

func issueDeviceCredentialForTest(
	t testing.TB,
	payload DeviceOperationCredentialPayload,
) *SignedDeviceOperationCredential {
	t.Helper()
	credential, err := IssueDeviceOperationCredential(
		deviceCredentialRootKey(), "vpass-test-chain", 4, payload,
	)
	if err != nil {
		t.Fatal(err)
	}
	return credential
}

func validAuthorizationContext(
	payload DeviceOperationCredentialPayload,
	operation protocol.OperationType,
) DeviceAuthorizationContext {
	return DeviceAuthorizationContext{
		NamespaceID:             payload.NamespaceID,
		DeviceID:                payload.DeviceID,
		Operation:               operation,
		FinalSequence:           15,
		CurrentIssuanceCounter:  payload.IssuanceCounter,
		CurrentStatusReference:  payload.StatusReference,
		CurrentSecretGeneration: payload.SecretGeneration,
	}
}

func cloneAuthorizationContext(value DeviceAuthorizationContext) DeviceAuthorizationContext {
	cloned := value
	if value.CredentialID != nil {
		item := *value.CredentialID
		cloned.CredentialID = &item
	}
	if value.OriginBinding != nil {
		item := *value.OriginBinding
		cloned.OriginBinding = &item
	}
	if value.RevokedAtSequence != nil {
		item := *value.RevokedAtSequence
		cloned.RevokedAtSequence = &item
	}
	return cloned
}

func filledCredentialID(value byte) protocol.CredentialID {
	var id protocol.CredentialID
	for index := range id {
		id[index] = value
	}
	return id
}

func mustCredentialSetScope(t testing.TB, id protocol.CredentialID) CredentialScope {
	t.Helper()
	scope, err := NewCredentialSetScope([]protocol.CredentialID{id})
	if err != nil {
		t.Fatal(err)
	}
	return scope
}

func mustOriginSetScope(
	t testing.TB,
	binding [cryptokit.OriginBindingSize]byte,
) CredentialScope {
	t.Helper()
	scope, err := NewOriginBindingSetScope([][cryptokit.OriginBindingSize]byte{binding})
	if err != nil {
		t.Fatal(err)
	}
	return scope
}

func mustSingleCredentialScope(
	t testing.TB,
	id protocol.CredentialID,
) CredentialScope {
	t.Helper()
	scope, err := NewSingleCredentialScope(id)
	if err != nil {
		t.Fatal(err)
	}
	return scope
}
