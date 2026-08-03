package sqlite

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/binary"
	"errors"
	"path/filepath"
	"strconv"
	"testing"

	"vpass.local/vpass/internal/credential/domain"
	"vpass.local/vpass/internal/cryptokit"
	"vpass.local/vpass/internal/protocol"
)

func TestRouteRepositorySameOriginAccountsRestartAndRemoval(t *testing.T) {
	t.Parallel()
	ctx := context.Background()
	path := filepath.Join(t.TempDir(), "routes.db")
	database, repository, nameKey, namespaceID := routeRepositoryFixture(t, path)
	origin, err := domain.NormalizeOrigin("HTTPS://BÜCHER.example:443/")
	if err != nil {
		t.Fatal(err)
	}
	defer origin.Destroy()

	aliceID := repeatedCredentialID(0x51)
	bobID := repeatedCredentialID(0x62)
	insertBareCredential(t, database, namespaceID, aliceID)
	insertBareCredential(t, database, namespaceID, bobID)
	alice, err := domain.BuildEncryptedRouteEntry(
		nameKey, namespaceID, origin, []byte("alice"), aliceID, 1,
	)
	if err != nil {
		t.Fatal(err)
	}
	bob, err := domain.BuildEncryptedRouteEntry(
		nameKey, namespaceID, origin, []byte("bob"), bobID, 1,
	)
	if err != nil {
		t.Fatal(err)
	}
	if err := repository.Create(ctx, nameKey, alice, 100); err != nil {
		t.Fatal(err)
	}
	if err := repository.Create(ctx, nameKey, bob, 101); err != nil {
		t.Fatal(err)
	}
	if err := repository.Create(ctx, nameKey, bob, 102); !errors.Is(err, ErrRouteConflict) {
		t.Fatalf("duplicate route error = %v", err)
	}

	resolvedAlice, err := repository.Resolve(
		ctx, nameKey, namespaceID, origin, []byte("alice"),
	)
	if err != nil || resolvedAlice.CredentialID != aliceID {
		t.Fatalf("alice resolution = %#v, %v", resolvedAlice, err)
	}
	resolvedBob, err := repository.Resolve(
		ctx, nameKey, namespaceID, origin, []byte("bob"),
	)
	if err != nil || resolvedBob.CredentialID != bobID {
		t.Fatalf("bob resolution = %#v, %v", resolvedBob, err)
	}
	accounts, err := repository.ListByOrigin(ctx, nameKey, namespaceID, origin, 10)
	if err != nil || len(accounts) != 2 {
		t.Fatalf("same-origin accounts = %d, %v", len(accounts), err)
	}
	if _, err := repository.Resolve(
		ctx, nameKey, namespaceID, origin, []byte("mallory"),
	); !errors.Is(err, ErrRouteNotFound) {
		t.Fatalf("unknown account error = %v", err)
	}

	if err := database.Close(); err != nil {
		t.Fatal(err)
	}
	database, err = Open(ctx, path)
	if err != nil {
		t.Fatal(err)
	}
	defer database.Close()
	repository, _ = NewRouteRepository(database)
	restarted, err := repository.Resolve(
		ctx, nameKey, namespaceID, origin, []byte("alice"),
	)
	if err != nil || restarted.CredentialID != aliceID {
		t.Fatalf("restart resolution = %#v, %v", restarted, err)
	}
	lookup, _ := domain.BuildRouteLookup(nameKey, origin, []byte("alice"))
	if err := repository.Remove(ctx, namespaceID, lookup.RouteID, 1, 200); err != nil {
		t.Fatal(err)
	}
	if _, err := repository.Resolve(
		ctx, nameKey, namespaceID, origin, []byte("alice"),
	); !errors.Is(err, ErrRouteNotFound) {
		t.Fatalf("removed route error = %v", err)
	}
	if err := repository.Remove(
		ctx, namespaceID, lookup.RouteID, 1, 201,
	); !errors.Is(err, ErrRouteCASConflict) {
		t.Fatalf("stale remove error = %v", err)
	}
}

func TestRouteRepositoryRejectsCiphertextAndBindingTamper(t *testing.T) {
	t.Parallel()
	ctx := context.Background()
	database, repository, nameKey, namespaceID := routeRepositoryFixture(
		t, filepath.Join(t.TempDir(), "routes.db"),
	)
	origin, _ := domain.NormalizeOrigin("https://example.test")
	defer origin.Destroy()
	credentialID := repeatedCredentialID(0x73)
	insertBareCredential(t, database, namespaceID, credentialID)
	entry, err := domain.BuildEncryptedRouteEntry(
		nameKey, namespaceID, origin, []byte("alice"), credentialID, 1,
	)
	if err != nil {
		t.Fatal(err)
	}
	if err := repository.Create(ctx, nameKey, entry, 100); err != nil {
		t.Fatal(err)
	}
	lookup := entry.Lookup()
	if _, err := database.ExecContext(
		ctx,
		`UPDATE route_entries
SET encrypted_account_id = substr(encrypted_account_id, 1, length(encrypted_account_id)-1)
WHERE namespace_id = ? AND route_id = ?`,
		namespaceID[:],
		lookup.RouteID[:],
	); err != nil {
		t.Fatal(err)
	}
	if _, err := repository.Resolve(
		ctx, nameKey, namespaceID, origin, []byte("alice"),
	); !errors.Is(err, ErrRouteCorrupt) {
		t.Fatalf("ciphertext tamper error = %v", err)
	}

	if _, err := database.ExecContext(
		ctx,
		"UPDATE route_entries SET origin_binding = randomblob(32) WHERE namespace_id = ? AND route_id = ?",
		namespaceID[:],
		lookup.RouteID[:],
	); err != nil {
		t.Fatal(err)
	}
	if _, err := repository.Resolve(
		ctx, nameKey, namespaceID, origin, []byte("alice"),
	); !errors.Is(err, ErrRouteCorrupt) {
		t.Fatalf("binding tamper error = %v", err)
	}
}

func routeRepositoryFixture(
	t testing.TB,
	path string,
) (*Database, *RouteRepository, *cryptokit.Key, protocol.NamespaceID) {
	t.Helper()
	ctx := context.Background()
	request, master, deviceSecret, recoverySecret, _ := vaultProfileFixture(t)
	t.Cleanup(master.Destroy)
	t.Cleanup(deviceSecret.Destroy)
	t.Cleanup(recoverySecret.Destroy)
	database, err := Open(ctx, path)
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { _ = database.Close() })
	profiles, _ := NewVaultProfileRepository(database)
	record, err := profiles.Create(ctx, request)
	if err != nil {
		t.Fatal(err)
	}
	bundle, err := cryptokit.OpenRootCapsule(
		master, deviceSecret, request.NamespaceID, request.DeviceID, record.RootCapsule,
	)
	if err != nil {
		t.Fatal(err)
	}
	root, err := bundle.NamespaceRootCopy()
	if err != nil {
		t.Fatal(err)
	}
	prk, err := cryptokit.ExtractNamespacePRK(
		root, request.NamespaceID, request.ActiveSecretGeneration,
	)
	root.Destroy()
	bundle.Destroy()
	if err != nil {
		t.Fatal(err)
	}
	keys, err := cryptokit.DeriveNamespaceKeys(prk)
	prk.Destroy()
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(keys.Destroy)
	repository, err := NewRouteRepository(database)
	if err != nil {
		t.Fatal(err)
	}
	return database, repository, keys.Name, request.NamespaceID
}

func insertBareCredential(
	t testing.TB,
	database *Database,
	namespaceID protocol.NamespaceID,
	credentialID protocol.CredentialID,
) {
	t.Helper()
	originCommitment := repeatedHash(credentialID[0])
	if _, err := database.ExecContext(
		context.Background(),
		`INSERT INTO credentials (
  credential_id, namespace_id, aggregate_status, origin_commitment,
  created_at_ms, updated_at_ms
) VALUES (?, ?, 'ACTIVE', ?, 1, 1)`,
		credentialID[:],
		namespaceID[:],
		originCommitment[:],
	); err != nil {
		t.Fatal(err)
	}
}

func repeatedCredentialID(value byte) protocol.CredentialID {
	var result protocol.CredentialID
	copy(result[:], bytes.Repeat([]byte{value}, len(result)))
	return result
}

func repeatedHash(value byte) [32]byte {
	var result [32]byte
	copy(result[:], bytes.Repeat([]byte{value}, len(result)))
	return result
}

func BenchmarkRouteRepositoryResolveLookup(b *testing.B) {
	for _, size := range []int{10_000, 100_000} {
		b.Run(strconv.Itoa(size)+"entries", func(b *testing.B) {
			ctx := context.Background()
			database, repository, nameKey, namespaceID := routeRepositoryFixture(
				b, filepath.Join(b.TempDir(), "routes.db"),
			)
			credentialID := repeatedCredentialID(0x7a)
			insertBareCredential(b, database, namespaceID, credentialID)
			origin, err := domain.NormalizeOrigin("https://benchmark.example")
			if err != nil {
				b.Fatal(err)
			}
			defer origin.Destroy()
			target, err := domain.BuildEncryptedRouteEntry(
				nameKey, namespaceID, origin, []byte("target"), credentialID, 1,
			)
			if err != nil {
				b.Fatal(err)
			}
			if err := repository.Create(ctx, nameKey, target, 1); err != nil {
				b.Fatal(err)
			}
			originCiphertext := target.EncryptedOrigin()
			accountCiphertext := target.EncryptedAccount()
			transaction, err := database.BeginImmediate(ctx)
			if err != nil {
				b.Fatal(err)
			}
			for index := 1; index < size; index++ {
				var counter [8]byte
				binary.BigEndian.PutUint64(counter[:], uint64(index))
				routeID := sha256.Sum256(append([]byte("route"), counter[:]...))
				originIndex := sha256.Sum256(append([]byte("origin"), counter[:]...))
				binding := sha256.Sum256(append([]byte("binding"), counter[:]...))
				if _, err := transaction.ExecContext(
					ctx,
					`INSERT INTO route_entries (
  namespace_id, route_id, origin_index, credential_id,
  encrypted_origin, encrypted_account_id, origin_binding,
  route_version, status, created_at_ms, updated_at_ms
) VALUES (?, ?, ?, ?, ?, ?, ?, 1, 'ACTIVE', 1, 1)`,
					namespaceID[:], routeID[:], originIndex[:], credentialID[:],
					originCiphertext, accountCiphertext, binding[:],
				); err != nil {
					_ = transaction.Rollback()
					b.Fatal(err)
				}
			}
			if err := transaction.Commit(); err != nil {
				b.Fatal(err)
			}
			lookup := target.Lookup()
			b.ReportMetric(float64(size), "entries")
			b.ResetTimer()
			for iteration := 0; iteration < b.N; iteration++ {
				resolved, err := repository.ResolveLookup(ctx, namespaceID, lookup)
				if err != nil || resolved.CredentialID != credentialID {
					b.Fatalf("resolve = %+v, %v", resolved, err)
				}
			}
		})
	}
}
