package sqlite

import (
	"context"
	"database/sql"
	"errors"
	"path/filepath"
	"testing"

	"vdns.local/vdns/migrations"
)

func TestOpenAppliesMigrationAndSecurityProfile(t *testing.T) {
	t.Parallel()
	database := openTestDatabase(t)

	if got := database.Stats().MaxOpenConnections; got != 1 {
		t.Fatalf("MaxOpenConnections = %d, want 1", got)
	}
	assertScalar(t, database, "PRAGMA user_version", currentVersion)
	assertScalar(t, database, "PRAGMA foreign_keys", 1)
	assertScalar(t, database, "PRAGMA busy_timeout", busyTimeoutMilli)
	assertScalar(t, database, "PRAGMA synchronous", 2)
	assertScalar(t, database, "PRAGMA trusted_schema", 0)

	var journalMode string
	if err := database.QueryRowContext(context.Background(), "PRAGMA journal_mode").Scan(&journalMode); err != nil {
		t.Fatal(err)
	}
	if journalMode != "wal" {
		t.Fatalf("journal_mode = %q, want wal", journalMode)
	}

	var tableCount int
	if err := database.QueryRowContext(
		context.Background(),
		"SELECT count(*) FROM sqlite_schema WHERE type = 'table' AND name NOT LIKE 'sqlite_%'",
	).Scan(&tableCount); err != nil {
		t.Fatal(err)
	}
	if tableCount != 78 {
		t.Fatalf("application table count = %d, want 78", tableCount)
	}
}

func TestOpenIsIdempotentAndRejectsMigrationTampering(t *testing.T) {
	t.Parallel()
	path := filepath.Join(t.TempDir(), "vdns.db")
	database, err := Open(context.Background(), path)
	if err != nil {
		t.Fatal(err)
	}
	if err := database.Close(); err != nil {
		t.Fatal(err)
	}

	database, err = Open(context.Background(), path)
	if err != nil {
		t.Fatalf("second Open: %v", err)
	}
	if _, err := database.ExecContext(
		context.Background(),
		"UPDATE schema_migrations SET checksum_sha256 = zeroblob(32) WHERE version = ?",
		currentVersion,
	); err != nil {
		t.Fatal(err)
	}
	if err := database.Close(); err != nil {
		t.Fatal(err)
	}

	if _, err := Open(context.Background(), path); !errors.Is(err, ErrMigrationIntegrity) {
		t.Fatalf("Open after migration tampering error = %v, want ErrMigrationIntegrity", err)
	}
}

func TestOpenRejectsLegacyCP1WithoutExplicitReencryption(t *testing.T) {
	t.Parallel()
	path := filepath.Join(t.TempDir(), "legacy-vdns.db")
	raw, err := sql.Open(driverName, databaseDSN(path))
	if err != nil {
		t.Fatal(err)
	}
	if _, err := raw.ExecContext(context.Background(), migrations.LegacyInitialSQL); err != nil {
		_ = raw.Close()
		t.Fatal(err)
	}
	if err := raw.Close(); err != nil {
		t.Fatal(err)
	}

	database, err := Open(context.Background(), path)
	if database != nil || !errors.Is(err, ErrSchemaVersion) ||
		!errors.Is(err, ErrExplicitCP2Migration) {
		t.Fatalf("Open(CP-1) = %v, %v; want explicit CP-2 migration error", database, err)
	}
}

func TestOpenUpgradesCP2BaseToCurrentAppendOnly(t *testing.T) {
	t.Parallel()
	path := filepath.Join(t.TempDir(), "cp2-base.db")
	raw, err := sql.Open(driverName, databaseDSN(path))
	if err != nil {
		t.Fatal(err)
	}
	if _, err := raw.ExecContext(context.Background(), migrations.InitialSQL); err != nil {
		_ = raw.Close()
		t.Fatal(err)
	}
	if err := raw.Close(); err != nil {
		t.Fatal(err)
	}
	database, err := Open(context.Background(), path)
	if err != nil {
		t.Fatal(err)
	}
	defer database.Close()
	assertScalar(t, database, "PRAGMA user_version", currentVersion)
	assertScalar(
		t,
		database,
		"SELECT count(*) FROM schema_migrations WHERE version IN (2,3,4,5,6,7,8)",
		7,
	)
	assertScalar(
		t,
		database,
		"SELECT count(*) FROM sqlite_schema WHERE type = 'table' AND name = 'credential_acceptance_v2'",
		1,
	)
}

func TestOpenUpgradesG2ToG3AppendOnly(t *testing.T) {
	t.Parallel()
	path := filepath.Join(t.TempDir(), "g2.db")
	raw, err := sql.Open(driverName, databaseDSN(path))
	if err != nil {
		t.Fatal(err)
	}
	if _, err := raw.ExecContext(context.Background(), migrations.InitialSQL); err != nil {
		_ = raw.Close()
		t.Fatal(err)
	}
	if _, err := raw.ExecContext(context.Background(), migrations.G2CoreSQL); err != nil {
		_ = raw.Close()
		t.Fatal(err)
	}
	if err := raw.Close(); err != nil {
		t.Fatal(err)
	}
	database, err := Open(context.Background(), path)
	if err != nil {
		t.Fatal(err)
	}
	defer database.Close()
	assertScalar(t, database, "PRAGMA user_version", currentVersion)
	assertScalar(
		t, database,
		"SELECT count(*) FROM schema_migrations WHERE version = 4 AND name = '0004_g3_lifecycle_sync'",
		1,
	)
	assertScalar(
		t, database,
		"SELECT count(*) FROM sqlite_schema WHERE type = 'table' AND name = 'sync_manifests_v2'",
		1,
	)
	assertScalar(
		t, database,
		"SELECT count(*) FROM sqlite_schema WHERE type = 'table' AND name = 'proof_bundles_v2'",
		1,
	)
}

func TestOpenUpgradesG3ToG4AppendOnly(t *testing.T) {
	t.Parallel()
	path := filepath.Join(t.TempDir(), "g3.db")
	raw, err := sql.Open(driverName, databaseDSN(path))
	if err != nil {
		t.Fatal(err)
	}
	for _, migration := range []string{
		migrations.InitialSQL, migrations.G2CoreSQL, migrations.G3LifecycleSyncSQL,
	} {
		if _, err := raw.ExecContext(context.Background(), migration); err != nil {
			_ = raw.Close()
			t.Fatal(err)
		}
	}
	if err := raw.Close(); err != nil {
		t.Fatal(err)
	}
	database, err := Open(context.Background(), path)
	if err != nil {
		t.Fatal(err)
	}
	defer database.Close()
	assertScalar(t, database, "PRAGMA user_version", currentVersion)
	assertScalar(
		t, database,
		"SELECT count(*) FROM schema_migrations WHERE version = 5 AND name = '0005_g4_vdns_transparency'",
		1,
	)
	assertScalar(
		t, database,
		"SELECT count(*) FROM sqlite_schema WHERE type = 'table' AND name = 'monitor_evidence_v2'",
		1,
	)
}

func TestOpenUpgradesG4ThroughStage2AppendOnly(t *testing.T) {
	t.Parallel()
	path := filepath.Join(t.TempDir(), "g4.db")
	raw, err := sql.Open(driverName, databaseDSN(path))
	if err != nil {
		t.Fatal(err)
	}
	for _, migration := range []string{
		migrations.InitialSQL, migrations.G2CoreSQL,
		migrations.G3LifecycleSyncSQL, migrations.G4VDNSTransparencySQL,
	} {
		if _, err := raw.ExecContext(context.Background(), migration); err != nil {
			_ = raw.Close()
			t.Fatal(err)
		}
	}
	if err := raw.Close(); err != nil {
		t.Fatal(err)
	}
	database, err := Open(context.Background(), path)
	if err != nil {
		t.Fatal(err)
	}
	defer database.Close()
	assertScalar(t, database, "PRAGMA user_version", currentVersion)
	assertScalar(
		t, database,
		"SELECT count(*) FROM schema_migrations WHERE version = 6 AND name = '0006_g5_local_api'",
		1,
	)
	assertScalar(
		t, database,
		"SELECT count(*) FROM sqlite_schema WHERE type = 'table' AND name = 'local_api_idempotency_v2'",
		1,
	)
	assertScalar(
		t, database,
		"SELECT count(*) FROM schema_migrations WHERE version = 7 AND name = '0007_g6_privacy_response'",
		1,
	)
	assertScalar(
		t, database,
		"SELECT count(*) FROM sqlite_schema WHERE type = 'table' AND name = 'security_findings_v2'",
		1,
	)
	assertScalar(
		t, database,
		"SELECT count(*) FROM schema_migrations WHERE version = 8 AND name = '0008_stage2_protocol_closure'",
		1,
	)
	assertScalar(
		t, database,
		"SELECT count(*) FROM sqlite_schema WHERE type = 'table' AND name = 'final_order_receipts_v2'",
		1,
	)
}

func TestImmediateTransactionCommitAndRollback(t *testing.T) {
	t.Parallel()
	database := openTestDatabase(t)
	ctx := context.Background()

	transaction, err := database.BeginImmediate(ctx)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := transaction.ExecContext(ctx, "CREATE TABLE transaction_probe(value INTEGER NOT NULL) STRICT"); err != nil {
		t.Fatal(err)
	}
	if _, err := transaction.ExecContext(ctx, "INSERT INTO transaction_probe(value) VALUES (1)"); err != nil {
		t.Fatal(err)
	}
	if err := transaction.Rollback(); err != nil {
		t.Fatal(err)
	}
	if err := transaction.Rollback(); !errors.Is(err, ErrTransactionDone) {
		t.Fatalf("second rollback error = %v, want ErrTransactionDone", err)
	}

	var tableCount int
	if err := database.QueryRowContext(
		ctx,
		"SELECT count(*) FROM sqlite_schema WHERE type = 'table' AND name = 'transaction_probe'",
	).Scan(&tableCount); err != nil {
		t.Fatal(err)
	}
	if tableCount != 0 {
		t.Fatal("rolled-back DDL remained visible")
	}

	transaction, err = database.BeginImmediate(ctx)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := transaction.ExecContext(ctx, "CREATE TABLE transaction_probe(value INTEGER NOT NULL) STRICT"); err != nil {
		t.Fatal(err)
	}
	if err := transaction.Commit(); err != nil {
		t.Fatal(err)
	}
	assertScalar(t, database, "SELECT count(*) FROM transaction_probe", 0)
}

func TestOpenRejectsMemoryAndNewerSchema(t *testing.T) {
	t.Parallel()
	if _, err := Open(context.Background(), ":memory:"); !errors.Is(err, ErrInvalidDatabasePath) {
		t.Fatalf("memory Open error = %v", err)
	}

	path := filepath.Join(t.TempDir(), "vdns.db")
	database, err := Open(context.Background(), path)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := database.ExecContext(
		context.Background(), "PRAGMA user_version = 9",
	); err != nil {
		t.Fatal(err)
	}
	if err := database.Close(); err != nil {
		t.Fatal(err)
	}
	if _, err := Open(context.Background(), path); !errors.Is(err, ErrSchemaVersion) {
		t.Fatalf("newer schema Open error = %v, want ErrSchemaVersion", err)
	}
}

func openTestDatabase(t *testing.T) *Database {
	t.Helper()
	database, err := Open(context.Background(), filepath.Join(t.TempDir(), "vdns.db"))
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() {
		if err := database.Close(); err != nil && !errors.Is(err, sql.ErrConnDone) {
			t.Errorf("Close: %v", err)
		}
	})
	return database
}

func assertScalar(t *testing.T, database *Database, query string, expected int) {
	t.Helper()
	var actual int
	if err := database.QueryRowContext(context.Background(), query).Scan(&actual); err != nil {
		t.Fatal(err)
	}
	if actual != expected {
		t.Fatalf("%s = %d, want %d", query, actual, expected)
	}
}
