// Package sqlite provides the production database boundary for VDNS.
//
// The adapter owns one connection for the lifetime of a database and
// deliberately exposes no way to enlarge the pool. This keeps BEGIN IMMEDIATE,
// WAL durability and outbox ordering independent of driver pool behavior.
// Other processes, including monitors, must use the VDNS API instead of
// opening the database file directly.
package sqlite

import (
	"context"
	"database/sql"
	"encoding/hex"
	"errors"
	"fmt"
	"net/url"
	"path/filepath"
	"strings"
	"sync"

	_ "modernc.org/sqlite"

	"vdns.local/vdns/internal/platform"
	"vdns.local/vdns/migrations"
)

const (
	driverName         = "sqlite"
	legacyVersion      = 1
	cp2BaseVersion     = 2
	g2CoreVersion      = 3
	g3LifecycleVersion = 4
	g4VDNSVersion      = 5
	g5LocalAPIVersion  = 6
	g6PrivacyVersion   = 7
	currentVersion     = 8
	initialName        = "0002_v2_initial"
	initialChecksum    = "18bd457a1fbf4e5d904c46512402c31dcc8bb96cb51b75eb62b8cca0566af152"
	g2CoreName         = "0003_g2_core"
	g2CoreChecksum     = "70934a17beba6ac5cd942c57f5b310d04ca9257a5e6dda9d3f6d027a1a696a9e"
	g3LifecycleName    = "0004_g3_lifecycle_sync"
	g3LifecycleCheck   = "c064e22d26cd0b703c82a3b8f53145110c799d6cd8a7ba5b03fb4501b89b2ac7"
	g4VDNSName         = "0005_g4_vdns_transparency"
	g4VDNSChecksum     = "8706b8da3cab1a182d70ae1d053556d1274c7d88ea612988abc3c53bce043f9b"
	g5LocalAPIName     = "0006_g5_local_api"
	g5LocalAPIChecksum = "8d0f548d0dc65ab00f4b9e4a13b4cc80b64b09c4ffe0e7fb8527200c1d45e056"
	g6PrivacyName      = "0007_g6_privacy_response"
	g6PrivacyChecksum  = "bda97d75cd1717c7afa0f1172be04781f01ac0e327647d423883746db8cc67eb"
	stage2Name         = "0008_stage2_protocol_closure"
	stage2Checksum     = "7c11ff6b5af6959c41c160789f395187440aa385aec441dbe034a32276b13b07"
	busyTimeoutMilli   = 5000
)

var (
	ErrInvalidDatabasePath  = errors.New("invalid SQLite database path")
	ErrSchemaVersion        = errors.New("unsupported SQLite schema version")
	ErrExplicitCP2Migration = errors.New("CP-1 database requires explicit export, re-encryption, and CP-2 import")
	ErrMigrationIntegrity   = errors.New("SQLite migration integrity check failed")
	ErrTransactionDone      = errors.New("SQLite transaction is already complete")
)

// Database owns the single permitted SQLite connection.
type Database struct {
	db *sql.DB
}

// Open creates or validates a file-backed VDNS database. In-memory databases
// are rejected because they cannot exercise the required WAL durability mode.
func Open(ctx context.Context, path string) (*Database, error) {
	if ctx == nil || strings.TrimSpace(path) == "" || path == ":memory:" {
		return nil, ErrInvalidDatabasePath
	}
	absolute, err := filepath.Abs(path)
	if err != nil {
		return nil, fmt.Errorf("%w: %v", ErrInvalidDatabasePath, err)
	}

	dsn := databaseDSN(absolute)
	db, err := sql.Open(driverName, dsn)
	if err != nil {
		return nil, fmt.Errorf("open SQLite: %w", err)
	}
	// Security invariant: changing the pool size requires a concurrency and
	// WAL-reset review plus a recorded architecture decision.
	db.SetMaxOpenConns(1)
	db.SetMaxIdleConns(1)
	db.SetConnMaxLifetime(0)

	database := &Database{db: db}
	if err := db.PingContext(ctx); err != nil {
		_ = db.Close()
		return nil, fmt.Errorf("ping SQLite: %w", err)
	}
	if err := database.migrateAndVerify(ctx); err != nil {
		_ = db.Close()
		return nil, err
	}
	return database, nil
}

func databaseDSN(path string) string {
	location := &url.URL{Scheme: "file", Path: path}
	query := url.Values{}
	query.Set("mode", "rwc")
	query.Add("_pragma", fmt.Sprintf("busy_timeout(%d)", busyTimeoutMilli))
	query.Add("_pragma", "foreign_keys(ON)")
	query.Add("_pragma", "journal_mode(WAL)")
	query.Add("_pragma", "synchronous(FULL)")
	query.Add("_pragma", "trusted_schema(OFF)")
	location.RawQuery = query.Encode()
	return location.String()
}

func (database *Database) migrateAndVerify(ctx context.Context) error {
	var version int
	if err := database.db.QueryRowContext(ctx, "PRAGMA user_version").Scan(&version); err != nil {
		return fmt.Errorf("read SQLite schema version: %w", err)
	}
	switch version {
	case 0:
		if _, err := database.db.ExecContext(ctx, migrations.InitialSQL); err != nil {
			return fmt.Errorf("apply migration %s: %w", initialName, err)
		}
		if _, err := database.db.ExecContext(ctx, migrations.G2CoreSQL); err != nil {
			return fmt.Errorf("apply migration %s: %w", g2CoreName, err)
		}
		if _, err := database.db.ExecContext(ctx, migrations.G3LifecycleSyncSQL); err != nil {
			return fmt.Errorf("apply migration %s: %w", g3LifecycleName, err)
		}
		if _, err := database.db.ExecContext(ctx, migrations.G4VDNSTransparencySQL); err != nil {
			return fmt.Errorf("apply migration %s: %w", g4VDNSName, err)
		}
		if _, err := database.db.ExecContext(ctx, migrations.G5LocalAPISQL); err != nil {
			return fmt.Errorf("apply migration %s: %w", g5LocalAPIName, err)
		}
		if _, err := database.db.ExecContext(ctx, migrations.G6PrivacyResponseSQL); err != nil {
			return fmt.Errorf("apply migration %s: %w", g6PrivacyName, err)
		}
	case legacyVersion:
		// CP-1 uses different identifier widths, domains, keys and ciphertext
		// AAD. Reading it through CP-2 would create an ambiguous downgrade
		// path, so migration is an explicit re-encryption workflow.
		return fmt.Errorf("%w: %w", ErrSchemaVersion, ErrExplicitCP2Migration)
	case cp2BaseVersion:
		if err := database.verifyMigration(
			ctx, cp2BaseVersion, initialName, initialChecksum,
		); err != nil {
			return err
		}
		if _, err := database.db.ExecContext(ctx, migrations.G2CoreSQL); err != nil {
			return fmt.Errorf("apply migration %s: %w", g2CoreName, err)
		}
		if _, err := database.db.ExecContext(ctx, migrations.G3LifecycleSyncSQL); err != nil {
			return fmt.Errorf("apply migration %s: %w", g3LifecycleName, err)
		}
		if _, err := database.db.ExecContext(ctx, migrations.G4VDNSTransparencySQL); err != nil {
			return fmt.Errorf("apply migration %s: %w", g4VDNSName, err)
		}
		if _, err := database.db.ExecContext(ctx, migrations.G5LocalAPISQL); err != nil {
			return fmt.Errorf("apply migration %s: %w", g5LocalAPIName, err)
		}
		if _, err := database.db.ExecContext(ctx, migrations.G6PrivacyResponseSQL); err != nil {
			return fmt.Errorf("apply migration %s: %w", g6PrivacyName, err)
		}
	case g2CoreVersion:
		if err := database.verifyMigration(
			ctx, cp2BaseVersion, initialName, initialChecksum,
		); err != nil {
			return err
		}
		if err := database.verifyMigration(
			ctx, g2CoreVersion, g2CoreName, g2CoreChecksum,
		); err != nil {
			return err
		}
		if _, err := database.db.ExecContext(ctx, migrations.G3LifecycleSyncSQL); err != nil {
			return fmt.Errorf("apply migration %s: %w", g3LifecycleName, err)
		}
		if _, err := database.db.ExecContext(ctx, migrations.G4VDNSTransparencySQL); err != nil {
			return fmt.Errorf("apply migration %s: %w", g4VDNSName, err)
		}
		if _, err := database.db.ExecContext(ctx, migrations.G5LocalAPISQL); err != nil {
			return fmt.Errorf("apply migration %s: %w", g5LocalAPIName, err)
		}
		if _, err := database.db.ExecContext(ctx, migrations.G6PrivacyResponseSQL); err != nil {
			return fmt.Errorf("apply migration %s: %w", g6PrivacyName, err)
		}
	case g3LifecycleVersion:
		if err := database.verifyMigration(
			ctx, cp2BaseVersion, initialName, initialChecksum,
		); err != nil {
			return err
		}
		if err := database.verifyMigration(
			ctx, g2CoreVersion, g2CoreName, g2CoreChecksum,
		); err != nil {
			return err
		}
		if err := database.verifyMigration(
			ctx, g3LifecycleVersion, g3LifecycleName, g3LifecycleCheck,
		); err != nil {
			return err
		}
		if _, err := database.db.ExecContext(ctx, migrations.G4VDNSTransparencySQL); err != nil {
			return fmt.Errorf("apply migration %s: %w", g4VDNSName, err)
		}
		if _, err := database.db.ExecContext(ctx, migrations.G5LocalAPISQL); err != nil {
			return fmt.Errorf("apply migration %s: %w", g5LocalAPIName, err)
		}
		if _, err := database.db.ExecContext(ctx, migrations.G6PrivacyResponseSQL); err != nil {
			return fmt.Errorf("apply migration %s: %w", g6PrivacyName, err)
		}
	case g4VDNSVersion:
		if err := database.verifyMigration(
			ctx, cp2BaseVersion, initialName, initialChecksum,
		); err != nil {
			return err
		}
		if err := database.verifyMigration(
			ctx, g2CoreVersion, g2CoreName, g2CoreChecksum,
		); err != nil {
			return err
		}
		if err := database.verifyMigration(
			ctx, g3LifecycleVersion, g3LifecycleName, g3LifecycleCheck,
		); err != nil {
			return err
		}
		if err := database.verifyMigration(
			ctx, g4VDNSVersion, g4VDNSName, g4VDNSChecksum,
		); err != nil {
			return err
		}
		if _, err := database.db.ExecContext(ctx, migrations.G5LocalAPISQL); err != nil {
			return fmt.Errorf("apply migration %s: %w", g5LocalAPIName, err)
		}
		if _, err := database.db.ExecContext(ctx, migrations.G6PrivacyResponseSQL); err != nil {
			return fmt.Errorf("apply migration %s: %w", g6PrivacyName, err)
		}
	case g5LocalAPIVersion:
		if _, err := database.db.ExecContext(ctx, migrations.G6PrivacyResponseSQL); err != nil {
			return fmt.Errorf("apply migration %s: %w", g6PrivacyName, err)
		}
	case g6PrivacyVersion:
		// The common tail below applies Stage 2.
	case currentVersion:
		// Already migrated; the immutable migration identity is checked below.
	default:
		return fmt.Errorf("%w: got %d, support %d", ErrSchemaVersion, version, currentVersion)
	}
	if version < currentVersion && version != legacyVersion {
		if _, err := database.db.ExecContext(ctx, migrations.Stage2ProtocolClosureSQL); err != nil {
			return fmt.Errorf("apply migration %s: %w", stage2Name, err)
		}
	}

	if err := database.verifyMigrationIdentity(ctx); err != nil {
		return err
	}
	if err := database.verifyConnectionProfile(ctx); err != nil {
		return err
	}
	var integrity string
	if err := database.db.QueryRowContext(ctx, "PRAGMA integrity_check").Scan(&integrity); err != nil {
		return fmt.Errorf("run SQLite integrity check: %w", err)
	}
	if integrity != "ok" {
		return fmt.Errorf("%w: integrity_check=%q", ErrMigrationIntegrity, integrity)
	}
	return nil
}

func (database *Database) verifyMigrationIdentity(ctx context.Context) error {
	if err := database.verifyMigration(
		ctx, cp2BaseVersion, initialName, initialChecksum,
	); err != nil {
		return err
	}
	if err := database.verifyMigration(
		ctx, g2CoreVersion, g2CoreName, g2CoreChecksum,
	); err != nil {
		return err
	}
	if err := database.verifyMigration(
		ctx, g3LifecycleVersion, g3LifecycleName, g3LifecycleCheck,
	); err != nil {
		return err
	}
	if err := database.verifyMigration(
		ctx, g4VDNSVersion, g4VDNSName, g4VDNSChecksum,
	); err != nil {
		return err
	}
	if err := database.verifyMigration(
		ctx, g5LocalAPIVersion, g5LocalAPIName, g5LocalAPIChecksum,
	); err != nil {
		return err
	}
	if err := database.verifyMigration(
		ctx, g6PrivacyVersion, g6PrivacyName, g6PrivacyChecksum,
	); err != nil {
		return err
	}
	return database.verifyMigration(ctx, currentVersion, stage2Name, stage2Checksum)
}

func (database *Database) verifyMigration(
	ctx context.Context,
	version int,
	expectedName string,
	expectedChecksum string,
) error {
	var name string
	var checksum []byte
	err := database.db.QueryRowContext(
		ctx,
		"SELECT name, checksum_sha256 FROM schema_migrations WHERE version = ?",
		version,
	).Scan(&name, &checksum)
	if err != nil {
		return fmt.Errorf("%w: migration row: %v", ErrMigrationIntegrity, err)
	}
	if name != expectedName || hex.EncodeToString(checksum) != expectedChecksum {
		return fmt.Errorf("%w: migration %d identity mismatch", ErrMigrationIntegrity, version)
	}
	return nil
}

func (database *Database) verifyConnectionProfile(ctx context.Context) error {
	expectations := []struct {
		pragma string
		want   string
	}{
		{pragma: "foreign_keys", want: "1"},
		{pragma: "busy_timeout", want: fmt.Sprint(busyTimeoutMilli)},
		{pragma: "journal_mode", want: "wal"},
		{pragma: "synchronous", want: "2"},
		{pragma: "trusted_schema", want: "0"},
	}
	for _, expectation := range expectations {
		var actual string
		if err := database.db.QueryRowContext(ctx, "PRAGMA "+expectation.pragma).Scan(&actual); err != nil {
			return fmt.Errorf("read SQLite PRAGMA %s: %w", expectation.pragma, err)
		}
		if !strings.EqualFold(actual, expectation.want) {
			return fmt.Errorf(
				"%w: PRAGMA %s=%q, want %q",
				ErrMigrationIntegrity,
				expectation.pragma,
				actual,
				expectation.want,
			)
		}
	}
	if database.db.Stats().MaxOpenConnections != 1 {
		return fmt.Errorf("%w: connection pool is not single-connection", ErrMigrationIntegrity)
	}
	return nil
}

// Close releases the sole SQLite connection.
func (database *Database) Close() error {
	if database == nil || database.db == nil {
		return nil
	}
	return database.db.Close()
}

// ExecContext executes adapter-owned SQL outside an explicit transaction.
// Domain repositories should prefer Begin and keep write transactions short.
func (database *Database) ExecContext(ctx context.Context, query string, args ...any) (sql.Result, error) {
	if database == nil || database.db == nil {
		return nil, sql.ErrConnDone
	}
	return database.db.ExecContext(ctx, query, args...)
}

// QueryRowContext reads one row using the sole database connection.
func (database *Database) QueryRowContext(ctx context.Context, query string, args ...any) *sql.Row {
	return database.db.QueryRowContext(ctx, query, args...)
}

// Stats exposes non-secret pool telemetry for health checks.
func (database *Database) Stats() sql.DBStats {
	if database == nil || database.db == nil {
		return sql.DBStats{}
	}
	return database.db.Stats()
}

// Begin opens a BEGIN IMMEDIATE transaction on the sole connection. Network,
// filesystem fsync, chain RPC and expensive cryptography must remain outside
// this boundary.
func (database *Database) Begin(ctx context.Context) (platform.Transaction, error) {
	return database.BeginImmediate(ctx)
}

// BeginImmediate returns the concrete transaction for SQLite repositories.
func (database *Database) BeginImmediate(ctx context.Context) (*Transaction, error) {
	if database == nil || database.db == nil || ctx == nil {
		return nil, sql.ErrConnDone
	}
	connection, err := database.db.Conn(ctx)
	if err != nil {
		return nil, err
	}
	if _, err := connection.ExecContext(ctx, "BEGIN IMMEDIATE"); err != nil {
		_ = connection.Close()
		return nil, err
	}
	return &Transaction{connection: connection}, nil
}

// Transaction is a manually controlled BEGIN IMMEDIATE transaction. Its
// methods serialize completion so copied pointers cannot commit twice.
type Transaction struct {
	mu         sync.Mutex
	connection *sql.Conn
	done       bool
}

// ExecContext executes a statement inside the transaction.
func (transaction *Transaction) ExecContext(ctx context.Context, query string, args ...any) (sql.Result, error) {
	transaction.mu.Lock()
	defer transaction.mu.Unlock()
	if transaction.done || transaction.connection == nil {
		return nil, ErrTransactionDone
	}
	return transaction.connection.ExecContext(ctx, query, args...)
}

// QueryRowContext reads one row inside the transaction.
func (transaction *Transaction) QueryRowContext(ctx context.Context, query string, args ...any) *sql.Row {
	transaction.mu.Lock()
	defer transaction.mu.Unlock()
	return transaction.connection.QueryRowContext(ctx, query, args...)
}

// QueryContext streams rows inside the transaction. Callers must close Rows
// before issuing the next statement on the single owned connection.
func (transaction *Transaction) QueryContext(ctx context.Context, query string, args ...any) (*sql.Rows, error) {
	transaction.mu.Lock()
	defer transaction.mu.Unlock()
	if transaction.done || transaction.connection == nil {
		return nil, ErrTransactionDone
	}
	return transaction.connection.QueryContext(ctx, query, args...)
}

// Commit atomically publishes the transaction and releases its connection.
func (transaction *Transaction) Commit() error {
	return transaction.finish("COMMIT")
}

// Rollback discards the transaction and releases its connection.
func (transaction *Transaction) Rollback() error {
	return transaction.finish("ROLLBACK")
}

func (transaction *Transaction) finish(statement string) error {
	if transaction == nil {
		return ErrTransactionDone
	}
	transaction.mu.Lock()
	defer transaction.mu.Unlock()
	if transaction.done || transaction.connection == nil {
		return ErrTransactionDone
	}
	_, execErr := transaction.connection.ExecContext(context.Background(), statement)
	closeErr := transaction.connection.Close()
	transaction.done = true
	transaction.connection = nil
	return errors.Join(execErr, closeErr)
}

var _ platform.TransactionManager = (*Database)(nil)
var _ platform.Transaction = (*Transaction)(nil)
