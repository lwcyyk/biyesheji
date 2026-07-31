package sqlite

import (
	"bytes"
	"context"
	"crypto/ed25519"
	"crypto/sha256"
	"errors"
	"os"
	"path/filepath"
	"testing"

	"vdns.local/vdns/internal/cryptokit"
	"vdns.local/vdns/internal/protocol"
)

func TestVaultProfileRepositoryRestartRecoveryAndNoBareRoot(t *testing.T) {
	t.Parallel()
	ctx := context.Background()
	path := filepath.Join(t.TempDir(), "vault.db")
	request, masterPassword, deviceSecret, recoverySecret, bareSecrets := vaultProfileFixture(t)
	defer masterPassword.Destroy()
	defer deviceSecret.Destroy()
	defer recoverySecret.Destroy()

	database, err := Open(ctx, path)
	if err != nil {
		t.Fatal(err)
	}
	repository, err := NewVaultProfileRepository(database)
	if err != nil {
		t.Fatal(err)
	}
	created, err := repository.Create(ctx, request)
	if err != nil {
		t.Fatal(err)
	}
	if created.NamespaceID != request.NamespaceID ||
		created.ActiveSecretGeneration != request.ActiveSecretGeneration {
		t.Fatal("created profile projection changed")
	}
	if _, err := repository.Create(ctx, request); !errors.Is(err, ErrVaultProfileExists) {
		t.Fatalf("duplicate create error = %v", err)
	}
	if err := database.Close(); err != nil {
		t.Fatal(err)
	}

	databaseBytes, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	for name, secret := range bareSecrets {
		if bytes.Contains(databaseBytes, secret) {
			t.Fatalf("database contains bare %s", name)
		}
	}
	clear(databaseBytes)

	database, err = Open(ctx, path)
	if err != nil {
		t.Fatal(err)
	}
	defer database.Close()
	repository, _ = NewVaultProfileRepository(database)
	loaded, err := repository.Load(ctx, request.NamespaceID, request.DeviceID)
	if err != nil {
		t.Fatal(err)
	}
	if loaded.RootCapsuleDigest != created.RootCapsuleDigest ||
		loaded.RecoveryCapsuleDigest != created.RecoveryCapsuleDigest ||
		!bytes.Equal(loaded.RootPublicKey, request.RootPublicKey) {
		t.Fatal("restart changed profile or capsule digests")
	}
	rootBundle, err := cryptokit.OpenRootCapsule(
		masterPassword, deviceSecret, request.NamespaceID, request.DeviceID, loaded.RootCapsule,
	)
	if err != nil {
		t.Fatal(err)
	}
	if rootBundle.SecretGeneration() != request.ActiveSecretGeneration {
		t.Fatal("loaded root capsule recovered wrong generation")
	}
	rootBundle.Destroy()
	recovered, err := cryptokit.OpenRecoveryCapsule(
		recoverySecret, request.NamespaceID, loaded.RecoveryCapsule,
	)
	if err != nil {
		t.Fatal(err)
	}
	recovered.Destroy()
}

func TestVaultProfileRepositoryRejectsTamperAndMissing(t *testing.T) {
	t.Parallel()
	ctx := context.Background()
	database := openTestDatabase(t)
	repository, _ := NewVaultProfileRepository(database)
	request, master, deviceSecret, recoverySecret, _ := vaultProfileFixture(t)
	defer master.Destroy()
	defer deviceSecret.Destroy()
	defer recoverySecret.Destroy()
	if _, err := repository.Create(ctx, request); err != nil {
		t.Fatal(err)
	}
	if _, err := database.ExecContext(
		ctx,
		"UPDATE root_capsules SET capsule_cbor = X'A0' WHERE namespace_id = ? AND device_id = ?",
		request.NamespaceID[:],
		request.DeviceID[:],
	); err != nil {
		t.Fatal(err)
	}
	if _, err := repository.Load(
		ctx, request.NamespaceID, request.DeviceID,
	); !errors.Is(err, ErrVaultProfileCorrupt) {
		t.Fatalf("tampered capsule error = %v", err)
	}
	missing := request.NamespaceID
	missing[0] ^= 1
	if _, err := repository.Load(
		ctx, missing, request.DeviceID,
	); !errors.Is(err, ErrVaultProfileMissing) {
		t.Fatalf("missing profile error = %v", err)
	}
}

func TestVaultProfileRepositoryRejectsInvalidInput(t *testing.T) {
	t.Parallel()
	repository, _ := NewVaultProfileRepository(openTestDatabase(t))
	request, master, deviceSecret, recoverySecret, _ := vaultProfileFixture(t)
	defer master.Destroy()
	defer deviceSecret.Destroy()
	defer recoverySecret.Destroy()
	request.CryptoPolicyHash = [sha256.Size]byte{}
	if _, err := repository.Create(
		context.Background(), request,
	); !errors.Is(err, ErrInvalidVaultProfile) {
		t.Fatalf("zero policy error = %v", err)
	}
}

func vaultProfileFixture(t testing.TB) (
	CreateVaultProfileRequest,
	*cryptokit.Secret,
	*cryptokit.Secret,
	*cryptokit.Secret,
	map[string][]byte,
) {
	t.Helper()
	namespaceRootBytes := bytes.Repeat([]byte{0xa1}, cryptokit.KeySize)
	signingSeed := bytes.Repeat([]byte{0xb2}, ed25519.SeedSize)
	signingPrivate := ed25519.NewKeyFromSeed(signingSeed)
	mappingBytes := bytes.Repeat([]byte{0xc3}, cryptokit.KeySize)
	namespaceRoot, _ := cryptokit.NewSecret(namespaceRootBytes)
	signingSecret, _ := cryptokit.NewSecret(signingPrivate)
	mappingSecret, _ := cryptokit.NewSecret(mappingBytes)
	bundle, err := cryptokit.NewRootSecretBundle(
		namespaceRoot, signingSecret, mappingSecret, 1, 1,
	)
	namespaceRoot.Destroy()
	signingSecret.Destroy()
	mappingSecret.Destroy()
	if err != nil {
		t.Fatal(err)
	}
	defer bundle.Destroy()

	var namespaceID protocol.NamespaceID
	var deviceID protocol.DeviceID
	copy(namespaceID[:], bytes.Repeat([]byte{0x31}, len(namespaceID)))
	copy(deviceID[:], bytes.Repeat([]byte{0x42}, len(deviceID)))
	masterPassword, _ := cryptokit.NewSecret([]byte("test master password"))
	deviceSecret, _ := cryptokit.NewSecret(bytes.Repeat([]byte{0xd4}, cryptokit.KeySize))
	recoverySecret, _ := cryptokit.NewSecret(bytes.Repeat([]byte{0xe5}, cryptokit.KeySize))
	rootCapsule, err := cryptokit.SealRootCapsule(
		masterPassword,
		deviceSecret,
		namespaceID,
		deviceID,
		cryptokit.DefaultArgon2Params,
		bundle,
	)
	if err != nil {
		t.Fatal(err)
	}
	recoveryCapsule, err := cryptokit.SealRecoveryCapsule(
		recoverySecret, namespaceID, 1, 1, bundle,
	)
	if err != nil {
		t.Fatal(err)
	}
	var recoveryID RecoveryID
	copy(recoveryID[:], bytes.Repeat([]byte{0x67}, len(recoveryID)))
	rootPublic := append(ed25519.PublicKey(nil), signingPrivate[ed25519.SeedSize:]...)
	return CreateVaultProfileRequest{
			NamespaceID: namespaceID, DeviceID: deviceID, ChainID: "vdns-test-chain",
			ActiveSecretGeneration: 1,
			RootPublicKey:          rootPublic,
			CryptoPolicyHash:       sha256.Sum256([]byte("cp2-default-policy")),
			RootCapsule:            rootCapsule,
			RecoveryID:             recoveryID,
			RecoveryCapsule:        recoveryCapsule,
			CreatedAtMilliseconds:  1_700_000_000_000,
		},
		masterPassword,
		deviceSecret,
		recoverySecret,
		map[string][]byte{
			"namespace root":     namespaceRootBytes,
			"root signing seed":  signingSeed,
			"local mapping seed": mappingBytes,
		}
}
