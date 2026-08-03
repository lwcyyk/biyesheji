package sqlite

import (
	"context"
	"crypto/ed25519"
	"crypto/sha256"
	"crypto/subtle"
	"database/sql"
	"errors"
	"math"
	"strings"

	"vpass.local/vpass/internal/cryptokit"
	"vpass.local/vpass/internal/protocol"
)

var (
	ErrInvalidVaultProfile = errors.New("invalid vault profile")
	ErrVaultProfileExists  = errors.New("vault profile already exists")
	ErrVaultProfileMissing = errors.New("vault profile not found")
	ErrVaultProfileCorrupt = errors.New("vault profile is corrupt")
)

// RecoveryID is a public random identifier for one encrypted recovery capsule.
type RecoveryID [sha256.Size]byte

// CreateVaultProfileRequest contains only public metadata and encrypted
// capsules. Master passwords, device secrets and root bundles cannot be passed
// to this persistence boundary.
type CreateVaultProfileRequest struct {
	NamespaceID            protocol.NamespaceID
	DeviceID               protocol.DeviceID
	ChainID                string
	ActiveSecretGeneration uint64
	RootPublicKey          ed25519.PublicKey
	CryptoPolicyHash       [sha256.Size]byte
	RootCapsule            *cryptokit.RootCapsule
	RecoveryID             RecoveryID
	RecoveryCapsule        *cryptokit.RecoveryCapsule
	CreatedAtMilliseconds  uint64
}

// VaultProfileRecord is a restart-safe copy of the stored public metadata and
// parsed encrypted capsules.
type VaultProfileRecord struct {
	NamespaceID            protocol.NamespaceID
	DeviceID               protocol.DeviceID
	ChainID                string
	ActiveSecretGeneration uint64
	RootPublicKey          ed25519.PublicKey
	CryptoPolicyHash       [sha256.Size]byte
	RootCapsule            *cryptokit.RootCapsule
	RootCapsuleDigest      [sha256.Size]byte
	RecoveryID             RecoveryID
	RecoveryCapsule        *cryptokit.RecoveryCapsule
	RecoveryCapsuleDigest  [sha256.Size]byte
	CreatedAtMilliseconds  uint64
}

type VaultProfileRepository struct {
	database *Database
}

func NewVaultProfileRepository(database *Database) (*VaultProfileRepository, error) {
	if database == nil || database.db == nil {
		return nil, ErrInvalidVaultProfile
	}
	return &VaultProfileRepository{database: database}, nil
}

// Create atomically persists the profile and both encrypted recovery paths.
func (repository *VaultProfileRepository) Create(
	ctx context.Context,
	request CreateVaultProfileRequest,
) (VaultProfileRecord, error) {
	if repository == nil || repository.database == nil || ctx == nil {
		return VaultProfileRecord{}, ErrInvalidVaultProfile
	}
	projection, err := validateVaultProfileCreate(request)
	if err != nil {
		return VaultProfileRecord{}, err
	}
	transaction, err := repository.database.BeginImmediate(ctx)
	if err != nil {
		return VaultProfileRecord{}, err
	}
	defer func() { _ = transaction.Rollback() }()

	rootKeyID, _ := protocol.KeyIDFromPublicKey(request.RootPublicKey)
	createdAt := int64(request.CreatedAtMilliseconds)
	if _, err := transaction.ExecContext(
		ctx,
		`INSERT INTO namespaces (
  namespace_id, protocol_version, suite_id, chain_id,
  root_signing_public_key, root_key_id, current_secret_generation,
  status, created_at_ms, updated_at_ms
) VALUES (?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?, ?)`,
		request.NamespaceID[:],
		protocol.ProtocolVersion,
		protocol.SuiteID,
		request.ChainID,
		request.RootPublicKey,
		rootKeyID[:],
		request.ActiveSecretGeneration,
		createdAt,
		createdAt,
	); err != nil {
		if sqliteConstraint(err) {
			return VaultProfileRecord{}, ErrVaultProfileExists
		}
		return VaultProfileRecord{}, err
	}
	if _, err := transaction.ExecContext(
		ctx,
		`INSERT INTO vault_profiles (
  namespace_id, protocol_version, suite_id, active_secret_generation,
  root_public_key, crypto_policy_hash, created_at_ms
) VALUES (?, ?, ?, ?, ?, ?, ?)`,
		request.NamespaceID[:],
		protocol.ProtocolVersion,
		protocol.SuiteID,
		request.ActiveSecretGeneration,
		request.RootPublicKey,
		request.CryptoPolicyHash[:],
		createdAt,
	); err != nil {
		return VaultProfileRecord{}, err
	}
	root := projection.rootCapsule
	if _, err := transaction.ExecContext(
		ctx,
		`INSERT INTO root_capsules (
  namespace_id, device_id, capsule_version, argon_salt,
  argon_memory_kib, argon_iterations, argon_lanes, nonce, ciphertext,
  bundle_schema_version, capsule_cbor, object_digest, created_at_ms
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
		root.NamespaceID[:],
		root.DeviceID[:],
		root.CapsuleVersion,
		root.ArgonSalt[:],
		root.ArgonParams.MemoryKiB,
		root.ArgonParams.Iterations,
		root.ArgonParams.Lanes,
		root.Nonce[:],
		root.Ciphertext,
		root.BundleSchemaVersion,
		projection.rootCBOR,
		projection.rootDigest[:],
		createdAt,
	); err != nil {
		return VaultProfileRecord{}, err
	}
	recovery := projection.recoveryCapsule
	if _, err := transaction.ExecContext(
		ctx,
		`INSERT INTO recovery_capsules (
  recovery_id, namespace_id, policy_version, created_sequence,
  salt, nonce, ciphertext, capsule_cbor, object_digest, status, created_at_ms
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?)`,
		request.RecoveryID[:],
		recovery.NamespaceID[:],
		recovery.PolicyVersion,
		recovery.CreatedSequence,
		recovery.Salt[:],
		recovery.Nonce[:],
		recovery.Ciphertext,
		projection.recoveryCBOR,
		projection.recoveryDigest[:],
		createdAt,
	); err != nil {
		return VaultProfileRecord{}, err
	}
	if err := transaction.Commit(); err != nil {
		return VaultProfileRecord{}, err
	}
	return repository.Load(ctx, request.NamespaceID, request.DeviceID)
}

// Load reparses canonical capsule bytes and verifies every duplicated database
// projection before returning it to an unlock use case.
func (repository *VaultProfileRepository) Load(
	ctx context.Context,
	namespaceID protocol.NamespaceID,
	deviceID protocol.DeviceID,
) (VaultProfileRecord, error) {
	if repository == nil || repository.database == nil || ctx == nil ||
		bytesAllZero(namespaceID[:]) || bytesAllZero(deviceID[:]) {
		return VaultProfileRecord{}, ErrInvalidVaultProfile
	}
	var (
		protocolVersion, activeGeneration, createdAt int64
		suiteID, chainID                             string
		rootPublic, policyHash, rootCBOR, rootDigest []byte
		recoveryID, recoveryCBOR, recoveryDigest     []byte
	)
	err := repository.database.QueryRowContext(
		ctx,
		`SELECT
  v.protocol_version, v.suite_id, n.chain_id, v.active_secret_generation,
  v.root_public_key, v.crypto_policy_hash, v.created_at_ms,
  r.capsule_cbor, r.object_digest,
  c.recovery_id, c.capsule_cbor, c.object_digest
FROM vault_profiles v
JOIN namespaces n ON n.namespace_id = v.namespace_id
JOIN root_capsules r
  ON r.namespace_id = v.namespace_id AND r.device_id = ?
JOIN recovery_capsules c
  ON c.namespace_id = v.namespace_id AND c.status = 'ACTIVE'
WHERE v.namespace_id = ?`,
		deviceID[:],
		namespaceID[:],
	).Scan(
		&protocolVersion, &suiteID, &chainID, &activeGeneration,
		&rootPublic, &policyHash, &createdAt,
		&rootCBOR, &rootDigest,
		&recoveryID, &recoveryCBOR, &recoveryDigest,
	)
	if errors.Is(err, sql.ErrNoRows) {
		return VaultProfileRecord{}, ErrVaultProfileMissing
	}
	if err != nil {
		return VaultProfileRecord{}, err
	}
	if protocolVersion != int64(protocol.ProtocolVersion) || suiteID != protocol.SuiteID ||
		activeGeneration < 1 || len(rootPublic) != ed25519.PublicKeySize ||
		len(policyHash) != sha256.Size || len(rootDigest) != sha256.Size ||
		len(recoveryID) != sha256.Size || len(recoveryDigest) != sha256.Size ||
		createdAt < 0 || sha256.Sum256(rootCBOR) != toHash(rootDigest) ||
		sha256.Sum256(recoveryCBOR) != toHash(recoveryDigest) {
		return VaultProfileRecord{}, ErrVaultProfileCorrupt
	}
	rootCapsule, err := cryptokit.ParseRootCapsule(rootCBOR)
	if err != nil || subtle.ConstantTimeCompare(rootCapsule.NamespaceID[:], namespaceID[:]) != 1 ||
		subtle.ConstantTimeCompare(rootCapsule.DeviceID[:], deviceID[:]) != 1 {
		return VaultProfileRecord{}, ErrVaultProfileCorrupt
	}
	recoveryCapsule, err := cryptokit.ParseRecoveryCapsule(recoveryCBOR)
	if err != nil || subtle.ConstantTimeCompare(recoveryCapsule.NamespaceID[:], namespaceID[:]) != 1 {
		return VaultProfileRecord{}, ErrVaultProfileCorrupt
	}
	var policy [sha256.Size]byte
	copy(policy[:], policyHash)
	var recoveryIdentifier RecoveryID
	copy(recoveryIdentifier[:], recoveryID)
	return VaultProfileRecord{
		NamespaceID: namespaceID, DeviceID: deviceID, ChainID: chainID,
		ActiveSecretGeneration: uint64(activeGeneration),
		RootPublicKey:          append(ed25519.PublicKey(nil), rootPublic...),
		CryptoPolicyHash:       policy,
		RootCapsule:            rootCapsule,
		RootCapsuleDigest:      toHash(rootDigest),
		RecoveryID:             recoveryIdentifier,
		RecoveryCapsule:        recoveryCapsule,
		RecoveryCapsuleDigest:  toHash(recoveryDigest),
		CreatedAtMilliseconds:  uint64(createdAt),
	}, nil
}

type vaultProfileProjection struct {
	rootCBOR        []byte
	rootDigest      [sha256.Size]byte
	rootCapsule     *cryptokit.RootCapsule
	recoveryCBOR    []byte
	recoveryDigest  [sha256.Size]byte
	recoveryCapsule *cryptokit.RecoveryCapsule
}

func validateVaultProfileCreate(
	request CreateVaultProfileRequest,
) (vaultProfileProjection, error) {
	if bytesAllZero(request.NamespaceID[:]) || bytesAllZero(request.DeviceID[:]) ||
		strings.TrimSpace(request.ChainID) == "" ||
		len(request.ChainID) > protocol.MaxChainIDBytes ||
		request.ActiveSecretGeneration == 0 ||
		len(request.RootPublicKey) != ed25519.PublicKeySize ||
		bytesAllZero(request.RootPublicKey) ||
		bytesAllZero(request.CryptoPolicyHash[:]) ||
		bytesAllZero(request.RecoveryID[:]) ||
		request.RootCapsule == nil || request.RecoveryCapsule == nil ||
		request.CreatedAtMilliseconds > math.MaxInt64 ||
		request.RootCapsule.NamespaceID != request.NamespaceID ||
		request.RootCapsule.DeviceID != request.DeviceID ||
		request.RecoveryCapsule.NamespaceID != request.NamespaceID {
		return vaultProfileProjection{}, ErrInvalidVaultProfile
	}
	rootCBOR, err := request.RootCapsule.MarshalBinary()
	if err != nil {
		return vaultProfileProjection{}, ErrInvalidVaultProfile
	}
	recoveryCBOR, err := request.RecoveryCapsule.MarshalBinary()
	if err != nil {
		clear(rootCBOR)
		return vaultProfileProjection{}, ErrInvalidVaultProfile
	}
	rootCapsule, err := cryptokit.ParseRootCapsule(rootCBOR)
	if err != nil {
		clear(rootCBOR)
		clear(recoveryCBOR)
		return vaultProfileProjection{}, ErrInvalidVaultProfile
	}
	recoveryCapsule, err := cryptokit.ParseRecoveryCapsule(recoveryCBOR)
	if err != nil {
		clear(rootCBOR)
		clear(recoveryCBOR)
		return vaultProfileProjection{}, ErrInvalidVaultProfile
	}
	return vaultProfileProjection{
		rootCBOR: rootCBOR, rootDigest: sha256.Sum256(rootCBOR),
		rootCapsule:  rootCapsule,
		recoveryCBOR: recoveryCBOR, recoveryDigest: sha256.Sum256(recoveryCBOR),
		recoveryCapsule: recoveryCapsule,
	}, nil
}

func toHash(value []byte) [sha256.Size]byte {
	var result [sha256.Size]byte
	copy(result[:], value)
	return result
}

func bytesAllZero(input []byte) bool {
	var combined byte
	for _, value := range input {
		combined |= value
	}
	return combined == 0
}

func sqliteConstraint(err error) bool {
	return err != nil && strings.Contains(strings.ToLower(err.Error()), "constraint")
}
