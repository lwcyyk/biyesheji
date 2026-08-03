package cryptokit

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/ed25519"
	"crypto/rand"
	"crypto/sha256"
	"crypto/subtle"
	"errors"
	"fmt"
	"io"
	"log/slog"

	"golang.org/x/crypto/argon2"
	"golang.org/x/crypto/hkdf"

	"vpass.local/vpass/internal/protocol"
)

const (
	Argon2Version          = argon2.Version
	Argon2SaltSize         = 16
	CapsuleNonceSize       = 12
	RootCapsuleVersion     = uint64(1)
	RecoveryCapsuleVersion = uint64(1)
	RootBundleSchemaV1     = uint64(1)

	MinArgon2MemoryKiB  = uint32(8 * 1024)
	MaxArgon2MemoryKiB  = uint32(1024 * 1024)
	MinArgon2Iterations = uint32(1)
	MaxArgon2Iterations = uint32(10)
	MinArgon2Lanes      = uint8(1)
	MaxArgon2Lanes      = uint8(16)
	MaxMasterPassword   = 4 * 1024
	MaxCapsuleBytes     = 16 * 1024
)

var (
	// ErrRejectCapsule deliberately hides whether password, device secret,
	// recovery secret, metadata or authentication failed.
	ErrRejectCapsule = errors.New("REJECT_CAPSULE")
	// ErrArgon2Params reports a public parameter outside the implementation's
	// resource and security policy.
	ErrArgon2Params = errors.New("INVALID_ARGON2_PARAMS")
)

// DefaultArgon2Params is a conservative desktop starting point. Deployment
// code may calibrate upward while remaining within Validate limits.
var DefaultArgon2Params = Argon2Params{
	Version:    Argon2Version,
	MemoryKiB:  64 * 1024,
	Iterations: 3,
	Lanes:      1,
}

// Argon2Params is persisted in every RootCapsule and authenticated as AAD.
type Argon2Params struct {
	Version    uint32 `cbor:"version"`
	MemoryKiB  uint32 `cbor:"memory_kib"`
	Iterations uint32 `cbor:"iterations"`
	Lanes      uint8  `cbor:"lanes"`
}

// Validate enforces both a floor and a resource-exhaustion ceiling.
func (params Argon2Params) Validate() error {
	if params.Version != Argon2Version ||
		params.MemoryKiB < MinArgon2MemoryKiB || params.MemoryKiB > MaxArgon2MemoryKiB ||
		params.Iterations < MinArgon2Iterations || params.Iterations > MaxArgon2Iterations ||
		params.Lanes < MinArgon2Lanes || params.Lanes > MaxArgon2Lanes {
		return ErrArgon2Params
	}
	return nil
}

// WithVersion fills the fixed Argon2 v1.3 version for a caller-selected
// memory/time/parallelism profile.
func (params Argon2Params) WithVersion() Argon2Params {
	params.Version = Argon2Version
	return params
}

// RootSecretBundle owns independent root material. The signing key and
// namespace root are co-packaged but never derived from one another.
type RootSecretBundle struct {
	namespaceRoot         *Secret
	rootSigningPrivate    *Secret
	localMappingSeed      *Secret
	recoveryPolicyVersion uint64
	secretGeneration      uint64
}

type rootSecretBundleWire struct {
	NamespaceRoot         [KeySize]byte                `cbor:"namespace_root"`
	RootSigningPrivate    [ed25519.PrivateKeySize]byte `cbor:"root_signing_private"`
	LocalMappingSeed      [KeySize]byte                `cbor:"local_mapping_seed"`
	RecoveryPolicyVersion uint64                       `cbor:"recovery_policy_version"`
	SecretGeneration      uint64                       `cbor:"secret_generation"`
}

// NewRootSecretBundle takes defensive copies of already independently
// generated secrets.
func NewRootSecretBundle(
	namespaceRoot *Secret,
	rootSigningPrivate *Secret,
	localMappingSeed *Secret,
	recoveryPolicyVersion uint64,
	secretGeneration uint64,
) (*RootSecretBundle, error) {
	if namespaceRoot == nil || rootSigningPrivate == nil || localMappingSeed == nil ||
		namespaceRoot.Len() != KeySize || rootSigningPrivate.Len() != ed25519.PrivateKeySize ||
		localMappingSeed.Len() != KeySize || recoveryPolicyVersion == 0 || secretGeneration == 0 {
		return nil, ErrInvalidInput
	}
	var rootCopy, signingCopy, mappingCopy *Secret
	if err := namespaceRoot.withBytes(func(raw []byte) error {
		var err error
		rootCopy, err = NewSecret(raw)
		return err
	}); err != nil {
		return nil, err
	}
	if err := rootSigningPrivate.withBytes(func(raw []byte) error {
		derived := ed25519.NewKeyFromSeed(raw[:ed25519.SeedSize])
		defer wipe(derived)
		if subtle.ConstantTimeCompare(raw, derived) != 1 {
			return ErrInvalidInput
		}
		var err error
		signingCopy, err = NewSecret(raw)
		return err
	}); err != nil {
		rootCopy.Destroy()
		return nil, err
	}
	if err := localMappingSeed.withBytes(func(raw []byte) error {
		var err error
		mappingCopy, err = NewSecret(raw)
		return err
	}); err != nil {
		rootCopy.Destroy()
		signingCopy.Destroy()
		return nil, err
	}
	return &RootSecretBundle{
		namespaceRoot: rootCopy, rootSigningPrivate: signingCopy,
		localMappingSeed: mappingCopy, recoveryPolicyVersion: recoveryPolicyVersion,
		secretGeneration: secretGeneration,
	}, nil
}

// GenerateRootSecretBundle creates independent namespace, Ed25519 and mapping
// secrets directly from the operating-system CSPRNG.
func GenerateRootSecretBundle(
	recoveryPolicyVersion uint64,
	secretGeneration uint64,
) (*RootSecretBundle, ed25519.PublicKey, error) {
	if recoveryPolicyVersion == 0 || secretGeneration == 0 {
		return nil, nil, ErrInvalidInput
	}
	namespaceBytes := make([]byte, KeySize)
	mappingBytes := make([]byte, KeySize)
	if _, err := io.ReadFull(rand.Reader, namespaceBytes); err != nil {
		wipe(namespaceBytes)
		wipe(mappingBytes)
		return nil, nil, ErrRandomSource
	}
	public, private, err := ed25519.GenerateKey(rand.Reader)
	if err != nil {
		wipe(namespaceBytes)
		wipe(mappingBytes)
		return nil, nil, ErrRandomSource
	}
	if _, err := io.ReadFull(rand.Reader, mappingBytes); err != nil {
		wipe(namespaceBytes)
		wipe(mappingBytes)
		wipe(private)
		return nil, nil, ErrRandomSource
	}
	root, _ := NewSecret(namespaceBytes)
	signing, _ := NewSecret(private)
	mapping, _ := NewSecret(mappingBytes)
	wipe(namespaceBytes)
	wipe(mappingBytes)
	wipe(private)
	bundle, err := NewRootSecretBundle(
		root, signing, mapping, recoveryPolicyVersion, secretGeneration,
	)
	root.Destroy()
	signing.Destroy()
	mapping.Destroy()
	if err != nil {
		return nil, nil, err
	}
	return bundle, append(ed25519.PublicKey(nil), public...), nil
}

// Destroy clears all bundle-owned material.
func (bundle *RootSecretBundle) Destroy() {
	if bundle == nil {
		return
	}
	for _, secret := range []*Secret{
		bundle.namespaceRoot, bundle.rootSigningPrivate, bundle.localMappingSeed,
	} {
		if secret != nil {
			secret.Destroy()
		}
	}
}

// NamespaceRootCopy returns a new protected handle for namespace KDF setup.
func (bundle *RootSecretBundle) NamespaceRootCopy() (*Secret, error) {
	if bundle == nil || bundle.namespaceRoot == nil {
		return nil, ErrSecretDestroyed
	}
	var result *Secret
	err := bundle.namespaceRoot.withBytes(func(raw []byte) error {
		var createErr error
		result, createErr = NewSecret(raw)
		return createErr
	})
	return result, err
}

// RootSigningKeyCopy returns an owned Ed25519 private key copy. The caller must
// overwrite it immediately after importing it into a signing-key owner.
func (bundle *RootSecretBundle) RootSigningKeyCopy() (ed25519.PrivateKey, error) {
	if bundle == nil || bundle.rootSigningPrivate == nil {
		return nil, ErrSecretDestroyed
	}
	var result ed25519.PrivateKey
	err := bundle.rootSigningPrivate.withBytes(func(raw []byte) error {
		result = append(ed25519.PrivateKey(nil), raw...)
		return nil
	})
	return result, err
}

// RecoveryPolicyVersion and SecretGeneration expose non-secret metadata.
func (bundle *RootSecretBundle) RecoveryPolicyVersion() uint64 {
	if bundle == nil {
		return 0
	}
	return bundle.recoveryPolicyVersion
}

func (bundle *RootSecretBundle) SecretGeneration() uint64 {
	if bundle == nil {
		return 0
	}
	return bundle.secretGeneration
}

func (bundle *RootSecretBundle) toWire() (rootSecretBundleWire, error) {
	var wire rootSecretBundleWire
	if bundle == nil || bundle.namespaceRoot == nil || bundle.rootSigningPrivate == nil ||
		bundle.localMappingSeed == nil || bundle.recoveryPolicyVersion == 0 ||
		bundle.secretGeneration == 0 {
		return wire, ErrInvalidInput
	}
	if err := bundle.namespaceRoot.withBytes(func(raw []byte) error {
		if len(raw) != len(wire.NamespaceRoot) {
			return ErrInvalidInput
		}
		copy(wire.NamespaceRoot[:], raw)
		return nil
	}); err != nil {
		return rootSecretBundleWire{}, err
	}
	if err := bundle.rootSigningPrivate.withBytes(func(raw []byte) error {
		if len(raw) != len(wire.RootSigningPrivate) {
			return ErrInvalidInput
		}
		copy(wire.RootSigningPrivate[:], raw)
		return nil
	}); err != nil {
		wipeRootBundleWire(&wire)
		return rootSecretBundleWire{}, err
	}
	if err := bundle.localMappingSeed.withBytes(func(raw []byte) error {
		if len(raw) != len(wire.LocalMappingSeed) {
			return ErrInvalidInput
		}
		copy(wire.LocalMappingSeed[:], raw)
		return nil
	}); err != nil {
		wipeRootBundleWire(&wire)
		return rootSecretBundleWire{}, err
	}
	wire.RecoveryPolicyVersion = bundle.recoveryPolicyVersion
	wire.SecretGeneration = bundle.secretGeneration
	return wire, nil
}

func rootBundleFromWire(wire rootSecretBundleWire) (*RootSecretBundle, error) {
	if allZeroBytes(wire.NamespaceRoot[:]) || allZeroBytes(wire.RootSigningPrivate[:]) ||
		allZeroBytes(wire.LocalMappingSeed[:]) || wire.RecoveryPolicyVersion == 0 ||
		wire.SecretGeneration == 0 {
		return nil, ErrRejectCapsule
	}
	root, _ := NewSecret(wire.NamespaceRoot[:])
	signing, _ := NewSecret(wire.RootSigningPrivate[:])
	mapping, _ := NewSecret(wire.LocalMappingSeed[:])
	bundle, err := NewRootSecretBundle(
		root, signing, mapping, wire.RecoveryPolicyVersion, wire.SecretGeneration,
	)
	root.Destroy()
	signing.Destroy()
	mapping.Destroy()
	if err != nil {
		return nil, ErrRejectCapsule
	}
	return bundle, nil
}

func wipeRootBundleWire(wire *rootSecretBundleWire) {
	if wire == nil {
		return
	}
	wipe(wire.NamespaceRoot[:])
	wipe(wire.RootSigningPrivate[:])
	wipe(wire.LocalMappingSeed[:])
	wire.RecoveryPolicyVersion = 0
	wire.SecretGeneration = 0
}

// RootCapsule is safe ciphertext plus authenticated public KDF metadata.
type RootCapsule struct {
	ProtocolID          string
	ProtocolVersion     uint64
	SuiteID             string
	CapsuleVersion      uint64
	NamespaceID         protocol.NamespaceID
	DeviceID            protocol.DeviceID
	ArgonSalt           [Argon2SaltSize]byte
	ArgonParams         Argon2Params
	Nonce               [CapsuleNonceSize]byte
	Ciphertext          []byte
	BundleSchemaVersion uint64
}

type rootCapsuleWire struct {
	ProtocolID          string                 `cbor:"protocol_id"`
	ProtocolVersion     uint64                 `cbor:"protocol_version"`
	SuiteID             string                 `cbor:"suite_id"`
	ObjectType          protocol.ObjectType    `cbor:"object_type"`
	CapsuleVersion      uint64                 `cbor:"capsule_version"`
	NamespaceID         protocol.NamespaceID   `cbor:"namespace_id"`
	DeviceID            protocol.DeviceID      `cbor:"device_id"`
	ArgonSalt           [Argon2SaltSize]byte   `cbor:"argon_salt"`
	ArgonParams         Argon2Params           `cbor:"argon_params"`
	Nonce               [CapsuleNonceSize]byte `cbor:"nonce"`
	Ciphertext          []byte                 `cbor:"ciphertext"`
	BundleSchemaVersion uint64                 `cbor:"bundle_schema_version"`
}

type rootCapsuleAAD struct {
	ProtocolID          string               `cbor:"protocol_id"`
	ProtocolVersion     uint64               `cbor:"protocol_version"`
	SuiteID             string               `cbor:"suite_id"`
	ObjectType          protocol.ObjectType  `cbor:"object_type"`
	CapsuleVersion      uint64               `cbor:"capsule_version"`
	NamespaceID         protocol.NamespaceID `cbor:"namespace_id"`
	DeviceID            protocol.DeviceID    `cbor:"device_id"`
	ArgonSalt           [Argon2SaltSize]byte `cbor:"argon_salt"`
	ArgonParams         Argon2Params         `cbor:"argon_params"`
	BundleSchemaVersion uint64               `cbor:"bundle_schema_version"`
}

// SealRootCapsule creates a device-bound root capsule using production entropy.
func SealRootCapsule(
	masterPassword *Secret,
	deviceSecret *Secret,
	namespaceID protocol.NamespaceID,
	deviceID protocol.DeviceID,
	params Argon2Params,
	bundle *RootSecretBundle,
) (*RootCapsule, error) {
	return sealRootCapsuleWithReader(
		masterPassword, deviceSecret, namespaceID, deviceID, params, bundle, rand.Reader,
	)
}

func sealRootCapsuleWithReader(
	masterPassword *Secret,
	deviceSecret *Secret,
	namespaceID protocol.NamespaceID,
	deviceID protocol.DeviceID,
	params Argon2Params,
	bundle *RootSecretBundle,
	random io.Reader,
) (*RootCapsule, error) {
	if masterPassword == nil || deviceSecret == nil || deviceSecret.Len() != KeySize ||
		masterPassword.Len() == 0 || masterPassword.Len() > MaxMasterPassword ||
		params.Validate() != nil || allZeroBytes(namespaceID[:]) || allZeroBytes(deviceID[:]) ||
		bundle == nil {
		return nil, ErrInvalidInput
	}
	randomMaterial := make([]byte, Argon2SaltSize+CapsuleNonceSize)
	if err := fillRandom(random, randomMaterial); err != nil {
		return nil, err
	}
	defer wipe(randomMaterial)
	var salt [Argon2SaltSize]byte
	var nonce [CapsuleNonceSize]byte
	copy(salt[:], randomMaterial[:Argon2SaltSize])
	copy(nonce[:], randomMaterial[Argon2SaltSize:])
	if allZeroBytes(salt[:]) || allZeroBytes(nonce[:]) {
		return nil, ErrRandomSource
	}

	passwordKey, err := derivePasswordKey(masterPassword, salt, params)
	if err != nil {
		return nil, err
	}
	defer passwordKey.Destroy()
	unlockKey, err := deriveUnlockKey(passwordKey, deviceSecret, namespaceID, deviceID)
	if err != nil {
		return nil, err
	}
	defer unlockKey.Destroy()

	bundleWire, err := bundle.toWire()
	if err != nil {
		return nil, err
	}
	plaintext, err := protocol.MarshalDeterministic(bundleWire)
	wipeRootBundleWire(&bundleWire)
	if err != nil {
		return nil, ErrInvalidInput
	}
	defer wipe(plaintext)
	aad := rootCapsuleAAD{
		ProtocolID: protocol.ProtocolID, ProtocolVersion: protocol.ProtocolVersion,
		SuiteID: protocol.SuiteID, ObjectType: protocol.ObjectTypeRootCapsule,
		CapsuleVersion: RootCapsuleVersion, NamespaceID: namespaceID, DeviceID: deviceID,
		ArgonSalt: salt, ArgonParams: params, BundleSchemaVersion: RootBundleSchemaV1,
	}
	aadBytes, err := protocol.MarshalDeterministic(aad)
	if err != nil {
		return nil, ErrInvalidInput
	}
	defer wipe(aadBytes)
	ciphertext, err := sealCapsule(unlockKey, purposeRootUnlock, nonce, plaintext, aadBytes)
	if err != nil {
		return nil, err
	}
	return &RootCapsule{
		ProtocolID: protocol.ProtocolID, ProtocolVersion: protocol.ProtocolVersion,
		SuiteID: protocol.SuiteID, CapsuleVersion: RootCapsuleVersion,
		NamespaceID: namespaceID, DeviceID: deviceID, ArgonSalt: salt,
		ArgonParams: params, Nonce: nonce, Ciphertext: ciphertext,
		BundleSchemaVersion: RootBundleSchemaV1,
	}, nil
}

// OpenRootCapsule fails closed without distinguishing password, device or
// authentication failure.
func OpenRootCapsule(
	masterPassword *Secret,
	deviceSecret *Secret,
	expectedNamespace protocol.NamespaceID,
	expectedDevice protocol.DeviceID,
	capsule *RootCapsule,
) (*RootSecretBundle, error) {
	if masterPassword == nil || deviceSecret == nil || capsule == nil ||
		deviceSecret.Len() != KeySize || masterPassword.Len() == 0 ||
		masterPassword.Len() > MaxMasterPassword ||
		capsule.validate() != nil || capsule.NamespaceID != expectedNamespace ||
		capsule.DeviceID != expectedDevice {
		return nil, ErrRejectCapsule
	}
	passwordKey, err := derivePasswordKey(masterPassword, capsule.ArgonSalt, capsule.ArgonParams)
	if err != nil {
		return nil, ErrRejectCapsule
	}
	defer passwordKey.Destroy()
	unlockKey, err := deriveUnlockKey(
		passwordKey, deviceSecret, capsule.NamespaceID, capsule.DeviceID,
	)
	if err != nil {
		return nil, ErrRejectCapsule
	}
	defer unlockKey.Destroy()
	aadBytes, err := protocol.MarshalDeterministic(capsule.aad())
	if err != nil {
		return nil, ErrRejectCapsule
	}
	defer wipe(aadBytes)
	plaintext, err := openCapsule(
		unlockKey, purposeRootUnlock, capsule.Nonce, capsule.Ciphertext, aadBytes,
	)
	if err != nil {
		return nil, ErrRejectCapsule
	}
	defer wipe(plaintext)
	var wire rootSecretBundleWire
	if err := protocol.UnmarshalDeterministic(plaintext, &wire); err != nil {
		return nil, ErrRejectCapsule
	}
	defer wipeRootBundleWire(&wire)
	bundle, err := rootBundleFromWire(wire)
	if err != nil {
		return nil, ErrRejectCapsule
	}
	return bundle, nil
}

// MarshalBinary returns the deterministic, content-addressable ciphertext
// object. It contains no master password or device secret.
func (capsule *RootCapsule) MarshalBinary() ([]byte, error) {
	if capsule == nil || capsule.validate() != nil {
		return nil, ErrInvalidInput
	}
	encoded, err := protocol.MarshalDeterministic(capsule.wire())
	if err != nil || len(encoded) > MaxCapsuleBytes {
		return nil, ErrInvalidInput
	}
	return encoded, nil
}

func ParseRootCapsule(encoded []byte) (*RootCapsule, error) {
	if len(encoded) == 0 || len(encoded) > MaxCapsuleBytes {
		return nil, ErrRejectCapsule
	}
	var wire rootCapsuleWire
	if err := protocol.UnmarshalDeterministic(encoded, &wire); err != nil {
		return nil, ErrRejectCapsule
	}
	capsule := rootCapsuleFromWire(wire)
	if capsule.validate() != nil {
		return nil, ErrRejectCapsule
	}
	return capsule, nil
}

func (capsule *RootCapsule) validate() error {
	if capsule == nil || capsule.ProtocolID != protocol.ProtocolID ||
		capsule.ProtocolVersion != protocol.ProtocolVersion || capsule.SuiteID != protocol.SuiteID ||
		capsule.CapsuleVersion != RootCapsuleVersion ||
		capsule.BundleSchemaVersion != RootBundleSchemaV1 ||
		capsule.ArgonParams.Validate() != nil ||
		allZeroBytes(capsule.NamespaceID[:]) || allZeroBytes(capsule.DeviceID[:]) ||
		allZeroBytes(capsule.ArgonSalt[:]) || allZeroBytes(capsule.Nonce[:]) ||
		len(capsule.Ciphertext) < GCMTagSize || len(capsule.Ciphertext) > MaxCapsuleBytes {
		return ErrRejectCapsule
	}
	return nil
}

func (capsule *RootCapsule) aad() rootCapsuleAAD {
	return rootCapsuleAAD{
		ProtocolID: capsule.ProtocolID, ProtocolVersion: capsule.ProtocolVersion,
		SuiteID: capsule.SuiteID, ObjectType: protocol.ObjectTypeRootCapsule,
		CapsuleVersion: capsule.CapsuleVersion, NamespaceID: capsule.NamespaceID,
		DeviceID: capsule.DeviceID, ArgonSalt: capsule.ArgonSalt,
		ArgonParams: capsule.ArgonParams, BundleSchemaVersion: capsule.BundleSchemaVersion,
	}
}

func (capsule *RootCapsule) wire() rootCapsuleWire {
	return rootCapsuleWire{
		ProtocolID: capsule.ProtocolID, ProtocolVersion: capsule.ProtocolVersion,
		SuiteID: capsule.SuiteID, ObjectType: protocol.ObjectTypeRootCapsule,
		CapsuleVersion: capsule.CapsuleVersion, NamespaceID: capsule.NamespaceID,
		DeviceID: capsule.DeviceID, ArgonSalt: capsule.ArgonSalt,
		ArgonParams: capsule.ArgonParams, Nonce: capsule.Nonce,
		Ciphertext:          append([]byte(nil), capsule.Ciphertext...),
		BundleSchemaVersion: capsule.BundleSchemaVersion,
	}
}

func rootCapsuleFromWire(wire rootCapsuleWire) *RootCapsule {
	if wire.ObjectType != protocol.ObjectTypeRootCapsule {
		return &RootCapsule{}
	}
	return &RootCapsule{
		ProtocolID: wire.ProtocolID, ProtocolVersion: wire.ProtocolVersion,
		SuiteID: wire.SuiteID, CapsuleVersion: wire.CapsuleVersion,
		NamespaceID: wire.NamespaceID, DeviceID: wire.DeviceID,
		ArgonSalt: wire.ArgonSalt, ArgonParams: wire.ArgonParams, Nonce: wire.Nonce,
		Ciphertext:          append([]byte(nil), wire.Ciphertext...),
		BundleSchemaVersion: wire.BundleSchemaVersion,
	}
}

// RecoveryCapsule protects the same root bundle with a 256-bit recovery secret
// and never falls back to the master password.
type RecoveryCapsule struct {
	ProtocolID          string
	ProtocolVersion     uint64
	SuiteID             string
	CapsuleVersion      uint64
	NamespaceID         protocol.NamespaceID
	PolicyVersion       uint64
	CreatedSequence     uint64
	Salt                [Argon2SaltSize]byte
	Nonce               [CapsuleNonceSize]byte
	Ciphertext          []byte
	BundleSchemaVersion uint64
}

type recoveryCapsuleWire struct {
	ProtocolID          string                 `cbor:"protocol_id"`
	ProtocolVersion     uint64                 `cbor:"protocol_version"`
	SuiteID             string                 `cbor:"suite_id"`
	ObjectType          protocol.ObjectType    `cbor:"object_type"`
	CapsuleVersion      uint64                 `cbor:"capsule_version"`
	NamespaceID         protocol.NamespaceID   `cbor:"namespace_id"`
	PolicyVersion       uint64                 `cbor:"policy_version"`
	CreatedSequence     uint64                 `cbor:"created_sequence"`
	Salt                [Argon2SaltSize]byte   `cbor:"salt"`
	Nonce               [CapsuleNonceSize]byte `cbor:"nonce"`
	Ciphertext          []byte                 `cbor:"ciphertext"`
	BundleSchemaVersion uint64                 `cbor:"bundle_schema_version"`
}

type recoveryCapsuleAAD struct {
	ProtocolID          string               `cbor:"protocol_id"`
	ProtocolVersion     uint64               `cbor:"protocol_version"`
	SuiteID             string               `cbor:"suite_id"`
	ObjectType          protocol.ObjectType  `cbor:"object_type"`
	CapsuleVersion      uint64               `cbor:"capsule_version"`
	NamespaceID         protocol.NamespaceID `cbor:"namespace_id"`
	PolicyVersion       uint64               `cbor:"policy_version"`
	CreatedSequence     uint64               `cbor:"created_sequence"`
	Salt                [Argon2SaltSize]byte `cbor:"salt"`
	BundleSchemaVersion uint64               `cbor:"bundle_schema_version"`
}

func SealRecoveryCapsule(
	recoverySecret *Secret,
	namespaceID protocol.NamespaceID,
	policyVersion uint64,
	createdSequence uint64,
	bundle *RootSecretBundle,
) (*RecoveryCapsule, error) {
	return sealRecoveryCapsuleWithReader(
		recoverySecret, namespaceID, policyVersion, createdSequence, bundle, rand.Reader,
	)
}

func sealRecoveryCapsuleWithReader(
	recoverySecret *Secret,
	namespaceID protocol.NamespaceID,
	policyVersion uint64,
	createdSequence uint64,
	bundle *RootSecretBundle,
	random io.Reader,
) (*RecoveryCapsule, error) {
	if recoverySecret == nil || recoverySecret.Len() != KeySize || bundle == nil ||
		policyVersion == 0 || createdSequence == 0 || allZeroBytes(namespaceID[:]) {
		return nil, ErrInvalidInput
	}
	randomMaterial := make([]byte, Argon2SaltSize+CapsuleNonceSize)
	if err := fillRandom(random, randomMaterial); err != nil {
		return nil, err
	}
	defer wipe(randomMaterial)
	var salt [Argon2SaltSize]byte
	var nonce [CapsuleNonceSize]byte
	copy(salt[:], randomMaterial[:Argon2SaltSize])
	copy(nonce[:], randomMaterial[Argon2SaltSize:])
	if allZeroBytes(salt[:]) || allZeroBytes(nonce[:]) {
		return nil, ErrRandomSource
	}
	recoveryKey, err := deriveRecoveryKey(
		recoverySecret, salt, namespaceID, policyVersion,
	)
	if err != nil {
		return nil, err
	}
	defer recoveryKey.Destroy()
	bundleWire, err := bundle.toWire()
	if err != nil {
		return nil, err
	}
	plaintext, err := protocol.MarshalDeterministic(bundleWire)
	wipeRootBundleWire(&bundleWire)
	if err != nil {
		return nil, ErrInvalidInput
	}
	defer wipe(plaintext)
	aad := recoveryCapsuleAAD{
		ProtocolID: protocol.ProtocolID, ProtocolVersion: protocol.ProtocolVersion,
		SuiteID: protocol.SuiteID, ObjectType: protocol.ObjectTypeRecoveryCapsule,
		CapsuleVersion: RecoveryCapsuleVersion, NamespaceID: namespaceID,
		PolicyVersion: policyVersion, CreatedSequence: createdSequence,
		Salt: salt, BundleSchemaVersion: RootBundleSchemaV1,
	}
	aadBytes, err := protocol.MarshalDeterministic(aad)
	if err != nil {
		return nil, ErrInvalidInput
	}
	defer wipe(aadBytes)
	ciphertext, err := sealCapsule(
		recoveryKey, purposeRecovery, nonce, plaintext, aadBytes,
	)
	if err != nil {
		return nil, err
	}
	return &RecoveryCapsule{
		ProtocolID: protocol.ProtocolID, ProtocolVersion: protocol.ProtocolVersion,
		SuiteID: protocol.SuiteID, CapsuleVersion: RecoveryCapsuleVersion,
		NamespaceID: namespaceID, PolicyVersion: policyVersion,
		CreatedSequence: createdSequence, Salt: salt, Nonce: nonce,
		Ciphertext: ciphertext, BundleSchemaVersion: RootBundleSchemaV1,
	}, nil
}

func OpenRecoveryCapsule(
	recoverySecret *Secret,
	expectedNamespace protocol.NamespaceID,
	capsule *RecoveryCapsule,
) (*RootSecretBundle, error) {
	if recoverySecret == nil || recoverySecret.Len() != KeySize || capsule == nil ||
		capsule.validate() != nil || capsule.NamespaceID != expectedNamespace {
		return nil, ErrRejectCapsule
	}
	key, err := deriveRecoveryKey(
		recoverySecret, capsule.Salt, capsule.NamespaceID, capsule.PolicyVersion,
	)
	if err != nil {
		return nil, ErrRejectCapsule
	}
	defer key.Destroy()
	aadBytes, err := protocol.MarshalDeterministic(capsule.aad())
	if err != nil {
		return nil, ErrRejectCapsule
	}
	defer wipe(aadBytes)
	plaintext, err := openCapsule(
		key, purposeRecovery, capsule.Nonce, capsule.Ciphertext, aadBytes,
	)
	if err != nil {
		return nil, ErrRejectCapsule
	}
	defer wipe(plaintext)
	var wire rootSecretBundleWire
	if err := protocol.UnmarshalDeterministic(plaintext, &wire); err != nil {
		return nil, ErrRejectCapsule
	}
	defer wipeRootBundleWire(&wire)
	bundle, err := rootBundleFromWire(wire)
	if err != nil {
		return nil, ErrRejectCapsule
	}
	return bundle, nil
}

func (capsule *RecoveryCapsule) MarshalBinary() ([]byte, error) {
	if capsule == nil || capsule.validate() != nil {
		return nil, ErrInvalidInput
	}
	encoded, err := protocol.MarshalDeterministic(capsule.wire())
	if err != nil || len(encoded) > MaxCapsuleBytes {
		return nil, ErrInvalidInput
	}
	return encoded, nil
}

func ParseRecoveryCapsule(encoded []byte) (*RecoveryCapsule, error) {
	if len(encoded) == 0 || len(encoded) > MaxCapsuleBytes {
		return nil, ErrRejectCapsule
	}
	var wire recoveryCapsuleWire
	if err := protocol.UnmarshalDeterministic(encoded, &wire); err != nil {
		return nil, ErrRejectCapsule
	}
	if wire.ObjectType != protocol.ObjectTypeRecoveryCapsule {
		return nil, ErrRejectCapsule
	}
	capsule := &RecoveryCapsule{
		ProtocolID: wire.ProtocolID, ProtocolVersion: wire.ProtocolVersion,
		SuiteID: wire.SuiteID, CapsuleVersion: wire.CapsuleVersion,
		NamespaceID: wire.NamespaceID, PolicyVersion: wire.PolicyVersion,
		CreatedSequence: wire.CreatedSequence, Salt: wire.Salt, Nonce: wire.Nonce,
		Ciphertext:          append([]byte(nil), wire.Ciphertext...),
		BundleSchemaVersion: wire.BundleSchemaVersion,
	}
	if capsule.validate() != nil {
		return nil, ErrRejectCapsule
	}
	return capsule, nil
}

func (capsule *RecoveryCapsule) validate() error {
	if capsule == nil || capsule.ProtocolID != protocol.ProtocolID ||
		capsule.ProtocolVersion != protocol.ProtocolVersion || capsule.SuiteID != protocol.SuiteID ||
		capsule.CapsuleVersion != RecoveryCapsuleVersion ||
		capsule.BundleSchemaVersion != RootBundleSchemaV1 ||
		capsule.PolicyVersion == 0 || capsule.CreatedSequence == 0 ||
		allZeroBytes(capsule.NamespaceID[:]) || allZeroBytes(capsule.Salt[:]) ||
		allZeroBytes(capsule.Nonce[:]) || len(capsule.Ciphertext) < GCMTagSize ||
		len(capsule.Ciphertext) > MaxCapsuleBytes {
		return ErrRejectCapsule
	}
	return nil
}

func (capsule *RecoveryCapsule) aad() recoveryCapsuleAAD {
	return recoveryCapsuleAAD{
		ProtocolID: capsule.ProtocolID, ProtocolVersion: capsule.ProtocolVersion,
		SuiteID: capsule.SuiteID, ObjectType: protocol.ObjectTypeRecoveryCapsule,
		CapsuleVersion: capsule.CapsuleVersion, NamespaceID: capsule.NamespaceID,
		PolicyVersion: capsule.PolicyVersion, CreatedSequence: capsule.CreatedSequence,
		Salt: capsule.Salt, BundleSchemaVersion: capsule.BundleSchemaVersion,
	}
}

func (capsule *RecoveryCapsule) wire() recoveryCapsuleWire {
	return recoveryCapsuleWire{
		ProtocolID: capsule.ProtocolID, ProtocolVersion: capsule.ProtocolVersion,
		SuiteID: capsule.SuiteID, ObjectType: protocol.ObjectTypeRecoveryCapsule,
		CapsuleVersion: capsule.CapsuleVersion, NamespaceID: capsule.NamespaceID,
		PolicyVersion: capsule.PolicyVersion, CreatedSequence: capsule.CreatedSequence,
		Salt: capsule.Salt, Nonce: capsule.Nonce,
		Ciphertext:          append([]byte(nil), capsule.Ciphertext...),
		BundleSchemaVersion: capsule.BundleSchemaVersion,
	}
}

func derivePasswordKey(
	masterPassword *Secret,
	salt [Argon2SaltSize]byte,
	params Argon2Params,
) (*Key, error) {
	if masterPassword == nil || masterPassword.Len() == 0 ||
		masterPassword.Len() > MaxMasterPassword || allZeroBytes(salt[:]) ||
		params.Validate() != nil {
		return nil, ErrInvalidInput
	}
	var output []byte
	err := masterPassword.withBytes(func(password []byte) error {
		output = argon2.IDKey(
			password, salt[:], params.Iterations, params.MemoryKiB,
			params.Lanes, KeySize,
		)
		return nil
	})
	if err != nil {
		wipe(output)
		return nil, err
	}
	key, err := newKeyWithPurpose(output, purposePasswordKDF)
	wipe(output)
	return key, err
}

func deriveUnlockKey(
	passwordKey *Key,
	deviceSecret *Secret,
	namespaceID protocol.NamespaceID,
	deviceID protocol.DeviceID,
) (*Key, error) {
	if passwordKey == nil || deviceSecret == nil || deviceSecret.Len() != KeySize ||
		allZeroBytes(namespaceID[:]) || allZeroBytes(deviceID[:]) {
		return nil, ErrInvalidInput
	}
	var output [KeySize]byte
	err := passwordKey.withPurposeBytes(purposePasswordKDF, func(passwordBytes []byte) error {
		return deviceSecret.withBytes(func(deviceBytes []byte) error {
			ikm := make([]byte, 0, KeySize*2)
			ikm = append(ikm, passwordBytes...)
			ikm = append(ikm, deviceBytes...)
			defer wipe(ikm)
			info, infoErr := encodeDomain(
				protocol.DomainPrefix+"ROOT-UNLOCK", deviceID,
			)
			if infoErr != nil {
				return infoErr
			}
			defer wipe(info)
			reader := hkdf.New(sha256.New, ikm, namespaceID[:], info)
			_, readErr := io.ReadFull(reader, output[:])
			return readErr
		})
	})
	if err != nil {
		wipe(output[:])
		return nil, err
	}
	key, err := newKeyFromArray(output, purposeRootUnlock)
	wipe(output[:])
	return key, err
}

func deriveRecoveryKey(
	recoverySecret *Secret,
	salt [Argon2SaltSize]byte,
	namespaceID protocol.NamespaceID,
	policyVersion uint64,
) (*Key, error) {
	if recoverySecret == nil || recoverySecret.Len() != KeySize ||
		allZeroBytes(salt[:]) || allZeroBytes(namespaceID[:]) || policyVersion == 0 {
		return nil, ErrInvalidInput
	}
	var output [KeySize]byte
	err := recoverySecret.withBytes(func(secret []byte) error {
		info, infoErr := encodeDomain(
			protocol.DomainPrefix+"RECOVERY-CAPSULE", namespaceID, policyVersion,
		)
		if infoErr != nil {
			return infoErr
		}
		defer wipe(info)
		reader := hkdf.New(sha256.New, secret, salt[:], info)
		_, readErr := io.ReadFull(reader, output[:])
		return readErr
	})
	if err != nil {
		wipe(output[:])
		return nil, err
	}
	key, err := newKeyFromArray(output, purposeRecovery)
	wipe(output[:])
	return key, err
}

func sealCapsule(
	key *Key,
	purpose keyPurpose,
	nonce [CapsuleNonceSize]byte,
	plaintext []byte,
	aad []byte,
) ([]byte, error) {
	if key == nil || len(plaintext) == 0 || len(aad) == 0 || allZeroBytes(nonce[:]) {
		return nil, ErrInvalidInput
	}
	var ciphertext []byte
	err := key.withPurposeBytes(purpose, func(raw []byte) error {
		block, cipherErr := aes.NewCipher(raw)
		if cipherErr != nil {
			return ErrInvalidInput
		}
		gcm, cipherErr := cipher.NewGCM(block)
		if cipherErr != nil {
			return ErrInvalidInput
		}
		ciphertext = gcm.Seal(nil, nonce[:], plaintext, aad)
		return nil
	})
	if err != nil {
		wipe(ciphertext)
		return nil, err
	}
	return ciphertext, nil
}

func openCapsule(
	key *Key,
	purpose keyPurpose,
	nonce [CapsuleNonceSize]byte,
	ciphertext []byte,
	aad []byte,
) ([]byte, error) {
	if key == nil || len(ciphertext) < GCMTagSize || len(aad) == 0 ||
		allZeroBytes(nonce[:]) {
		return nil, ErrRejectCapsule
	}
	var plaintext []byte
	err := key.withPurposeBytes(purpose, func(raw []byte) error {
		block, cipherErr := aes.NewCipher(raw)
		if cipherErr != nil {
			return ErrRejectCapsule
		}
		gcm, cipherErr := cipher.NewGCM(block)
		if cipherErr != nil {
			return ErrRejectCapsule
		}
		plaintext, cipherErr = gcm.Open(nil, nonce[:], ciphertext, aad)
		if cipherErr != nil {
			return ErrRejectCapsule
		}
		return nil
	})
	if err != nil {
		wipe(plaintext)
		return nil, ErrRejectCapsule
	}
	return plaintext, nil
}

func (RootSecretBundle) String() string   { return redactedSecret }
func (RootSecretBundle) GoString() string { return redactedSecret }
func (RootSecretBundle) Format(state fmt.State, _ rune) {
	_, _ = io.WriteString(state, redactedSecret)
}
func (RootSecretBundle) MarshalJSON() ([]byte, error) { return nil, ErrSecretSerialization }
func (RootSecretBundle) LogValue() slog.Value         { return slog.StringValue(redactedSecret) }
