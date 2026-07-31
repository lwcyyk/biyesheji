package sqlite

import (
	"context"
	"crypto/sha256"
	"crypto/subtle"
	"database/sql"
	"errors"
	"math"

	"vdns.local/vdns/internal/credential/domain"
	"vdns.local/vdns/internal/cryptokit"
	"vdns.local/vdns/internal/protocol"
)

var (
	ErrInvalidRouteCommit = errors.New("invalid route commit")
	ErrRouteConflict      = errors.New("route already exists")
	ErrRouteNotFound      = errors.New("route not found")
	ErrRouteCorrupt       = errors.New("route entry is corrupt")
	ErrRouteCASConflict   = errors.New("route CAS conflict")
)

type RouteResolution struct {
	CredentialID  protocol.CredentialID
	RouteVersion  uint64
	OriginBinding [cryptokit.OriginBindingSize]byte
}

type RouteRepository struct {
	database *Database
}

func NewRouteRepository(database *Database) (*RouteRepository, error) {
	if database == nil || database.db == nil {
		return nil, ErrInvalidRouteCommit
	}
	return &RouteRepository{database: database}, nil
}

func (repository *RouteRepository) Create(
	ctx context.Context,
	nameKey *cryptokit.Key,
	entry *domain.EncryptedRouteEntry,
	createdAtMilliseconds uint64,
) error {
	if repository == nil || repository.database == nil {
		return ErrInvalidRouteCommit
	}
	transaction, err := repository.database.BeginImmediate(ctx)
	if err != nil {
		return err
	}
	defer func() { _ = transaction.Rollback() }()
	if err := repository.CreateRoute(
		ctx, transaction, nameKey, entry, createdAtMilliseconds,
	); err != nil {
		return err
	}
	return transaction.Commit()
}

// CreateRoute joins a caller-owned credential creation transaction.
func (repository *RouteRepository) CreateRoute(
	ctx context.Context,
	transaction *Transaction,
	nameKey *cryptokit.Key,
	entry *domain.EncryptedRouteEntry,
	createdAtMilliseconds uint64,
) error {
	if repository == nil || transaction == nil || ctx == nil || nameKey == nil ||
		entry == nil || createdAtMilliseconds > math.MaxInt64 ||
		domain.ValidateEncryptedRouteEntry(nameKey, entry) != nil {
		return ErrInvalidRouteCommit
	}
	namespaceID := entry.NamespaceID()
	credentialID := entry.CredentialID()
	lookup := entry.Lookup()
	_, err := transaction.ExecContext(
		ctx,
		`INSERT INTO route_entries (
  namespace_id, route_id, origin_index, credential_id,
  encrypted_origin, encrypted_account_id, origin_binding,
  route_version, status, created_at_ms, updated_at_ms
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?, ?)`,
		namespaceID[:],
		lookup.RouteID[:],
		lookup.OriginIndex[:],
		credentialID[:],
		entry.EncryptedOrigin(),
		entry.EncryptedAccount(),
		lookup.OriginBinding[:],
		entry.RouteVersion(),
		createdAtMilliseconds,
		createdAtMilliseconds,
	)
	if sqliteConstraint(err) {
		return ErrRouteConflict
	}
	return err
}

// CreateSealedRoute joins a caller-owned transaction for an entry constructed
// by VaultSession. The type cannot be assembled from raw ciphertext outside
// the credential domain, so the adapter does not require access to K_name.
func (repository *RouteRepository) CreateSealedRoute(
	ctx context.Context,
	transaction *Transaction,
	entry *domain.EncryptedRouteEntry,
	createdAtMilliseconds uint64,
) error {
	if repository == nil || transaction == nil || ctx == nil || entry == nil ||
		createdAtMilliseconds > math.MaxInt64 {
		return ErrInvalidRouteCommit
	}
	namespaceID := entry.NamespaceID()
	credentialID := entry.CredentialID()
	lookup := entry.Lookup()
	if bytesAllZero(namespaceID[:]) || bytesAllZero(credentialID[:]) ||
		bytesAllZero(lookup.RouteID[:]) || bytesAllZero(lookup.OriginIndex[:]) ||
		bytesAllZero(lookup.OriginBinding[:]) || entry.RouteVersion() == 0 {
		return ErrInvalidRouteCommit
	}
	for _, encoded := range [][]byte{entry.EncryptedOrigin(), entry.EncryptedAccount()} {
		if _, err := cryptokit.ParseRouteCiphertext(encoded); err != nil {
			return ErrInvalidRouteCommit
		}
	}
	_, err := transaction.ExecContext(
		ctx,
		`INSERT INTO route_entries (
  namespace_id, route_id, origin_index, credential_id,
  encrypted_origin, encrypted_account_id, origin_binding,
  route_version, status, created_at_ms, updated_at_ms
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?, ?)`,
		namespaceID[:], lookup.RouteID[:], lookup.OriginIndex[:], credentialID[:],
		entry.EncryptedOrigin(), entry.EncryptedAccount(), lookup.OriginBinding[:],
		entry.RouteVersion(), createdAtMilliseconds, createdAtMilliseconds,
	)
	if sqliteConstraint(err) {
		return ErrRouteConflict
	}
	return err
}

// ResolveLookup uses a secret-derived exact RouteID and verifies every public
// binding before returning a credential pointer. CredentialEnvelope performs
// the final OriginBinding check before decryption.
func (repository *RouteRepository) ResolveLookup(
	ctx context.Context,
	namespaceID protocol.NamespaceID,
	lookup domain.RouteLookup,
) (RouteResolution, error) {
	if repository == nil || repository.database == nil || ctx == nil ||
		bytesAllZero(namespaceID[:]) || bytesAllZero(lookup.RouteID[:]) ||
		bytesAllZero(lookup.OriginIndex[:]) || bytesAllZero(lookup.OriginBinding[:]) {
		return RouteResolution{}, ErrInvalidRouteCommit
	}
	var originIndex, credentialID, originBinding, encryptedOrigin, encryptedAccount []byte
	var version uint64
	err := repository.database.QueryRowContext(
		ctx,
		`SELECT origin_index, credential_id, origin_binding,
        encrypted_origin, encrypted_account_id, route_version
 FROM route_entries
 WHERE namespace_id = ? AND route_id = ? AND status = 'ACTIVE'`,
		namespaceID[:], lookup.RouteID[:],
	).Scan(
		&originIndex, &credentialID, &originBinding,
		&encryptedOrigin, &encryptedAccount, &version,
	)
	if errors.Is(err, sql.ErrNoRows) {
		return RouteResolution{}, ErrRouteNotFound
	}
	if err != nil {
		return RouteResolution{}, err
	}
	if subtle.ConstantTimeCompare(originIndex, lookup.OriginIndex[:]) != 1 ||
		subtle.ConstantTimeCompare(originBinding, lookup.OriginBinding[:]) != 1 ||
		len(credentialID) != protocol.CredentialIDSize || version == 0 {
		return RouteResolution{}, ErrRouteCorrupt
	}
	for _, encoded := range [][]byte{encryptedOrigin, encryptedAccount} {
		if _, err := cryptokit.ParseRouteCiphertext(encoded); err != nil {
			return RouteResolution{}, ErrRouteCorrupt
		}
	}
	typedCredential, err := protocol.CredentialIDFromBytes(credentialID)
	if err != nil {
		return RouteResolution{}, ErrRouteCorrupt
	}
	return RouteResolution{
		CredentialID: typedCredential, RouteVersion: version,
		OriginBinding: lookup.OriginBinding,
	}, nil
}

func (repository *RouteRepository) Resolve(
	ctx context.Context,
	nameKey *cryptokit.Key,
	namespaceID protocol.NamespaceID,
	origin domain.Origin,
	accountID []byte,
) (RouteResolution, error) {
	if repository == nil || repository.database == nil || ctx == nil ||
		nameKey == nil || bytesAllZero(namespaceID[:]) {
		return RouteResolution{}, ErrInvalidRouteCommit
	}
	lookup, err := domain.BuildRouteLookup(nameKey, origin, accountID)
	if err != nil {
		return RouteResolution{}, ErrInvalidRouteCommit
	}
	entry, err := repository.loadActive(ctx, nameKey, namespaceID, lookup)
	if err != nil {
		return RouteResolution{}, err
	}
	return RouteResolution{
		CredentialID: entry.CredentialID(), RouteVersion: entry.RouteVersion(),
		OriginBinding: entry.Lookup().OriginBinding,
	}, nil
}

// ListByOrigin returns authenticated local route resolutions for all accounts
// under one canonical Origin. It never returns account plaintext.
func (repository *RouteRepository) ListByOrigin(
	ctx context.Context,
	nameKey *cryptokit.Key,
	namespaceID protocol.NamespaceID,
	origin domain.Origin,
	limit int,
) ([]RouteResolution, error) {
	if repository == nil || repository.database == nil || ctx == nil ||
		nameKey == nil || bytesAllZero(namespaceID[:]) || limit < 1 || limit > 1000 {
		return nil, ErrInvalidRouteCommit
	}
	var originIndex cryptokit.RouteOriginIndex
	err := origin.UseCanonical(func(canonical []byte) error {
		var deriveErr error
		originIndex, deriveErr = cryptokit.DeriveRouteOriginIndex(nameKey, canonical)
		return deriveErr
	})
	if err != nil {
		return nil, ErrInvalidRouteCommit
	}
	rows, err := repository.database.db.QueryContext(
		ctx,
		`SELECT route_id, credential_id, encrypted_origin, encrypted_account_id,
        origin_binding, route_version
FROM route_entries
WHERE namespace_id = ? AND origin_index = ? AND status = 'ACTIVE'
ORDER BY route_id
LIMIT ?`,
		namespaceID[:],
		originIndex[:],
		limit,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	results := make([]RouteResolution, 0)
	for rows.Next() {
		var routeIDBytes, credentialBytes, encryptedOrigin, encryptedAccount, bindingBytes []byte
		var version int64
		if err := rows.Scan(
			&routeIDBytes, &credentialBytes, &encryptedOrigin, &encryptedAccount,
			&bindingBytes, &version,
		); err != nil {
			return nil, err
		}
		entry, err := restoreRouteRow(
			nameKey, namespaceID, routeIDBytes, originIndex[:], credentialBytes,
			encryptedOrigin, encryptedAccount, bindingBytes, version,
		)
		if err != nil {
			return nil, err
		}
		results = append(results, RouteResolution{
			CredentialID: entry.CredentialID(), RouteVersion: entry.RouteVersion(),
			OriginBinding: entry.Lookup().OriginBinding,
		})
	}
	if err := rows.Err(); err != nil {
		return nil, err
	}
	return results, nil
}

func (repository *RouteRepository) Remove(
	ctx context.Context,
	namespaceID protocol.NamespaceID,
	routeID cryptokit.RouteID,
	expectedVersion uint64,
	updatedAtMilliseconds uint64,
) error {
	if repository == nil || repository.database == nil || ctx == nil ||
		bytesAllZero(namespaceID[:]) || bytesAllZero(routeID[:]) ||
		expectedVersion == 0 || updatedAtMilliseconds > math.MaxInt64 {
		return ErrInvalidRouteCommit
	}
	result, err := repository.database.ExecContext(
		ctx,
		`UPDATE route_entries
SET status = 'REMOVED', route_version = route_version + 1,
    updated_at_ms = CASE WHEN updated_at_ms > ? THEN updated_at_ms ELSE ? END
WHERE namespace_id = ? AND route_id = ? AND status = 'ACTIVE' AND route_version = ?`,
		updatedAtMilliseconds,
		updatedAtMilliseconds,
		namespaceID[:],
		routeID[:],
		expectedVersion,
	)
	if err != nil {
		return err
	}
	affected, err := result.RowsAffected()
	if err != nil {
		return err
	}
	if affected != 1 {
		return ErrRouteCASConflict
	}
	return nil
}

func (repository *RouteRepository) loadActive(
	ctx context.Context,
	nameKey *cryptokit.Key,
	namespaceID protocol.NamespaceID,
	lookup domain.RouteLookup,
) (*domain.EncryptedRouteEntry, error) {
	var routeIDBytes, originIndexBytes, credentialBytes, encryptedOrigin, encryptedAccount, bindingBytes []byte
	var version int64
	err := repository.database.QueryRowContext(
		ctx,
		`SELECT route_id, origin_index, credential_id, encrypted_origin,
        encrypted_account_id, origin_binding, route_version
FROM route_entries
WHERE namespace_id = ? AND route_id = ? AND status = 'ACTIVE'`,
		namespaceID[:],
		lookup.RouteID[:],
	).Scan(
		&routeIDBytes, &originIndexBytes, &credentialBytes, &encryptedOrigin,
		&encryptedAccount, &bindingBytes, &version,
	)
	if errors.Is(err, sql.ErrNoRows) {
		return nil, ErrRouteNotFound
	}
	if err != nil {
		return nil, err
	}
	if subtle.ConstantTimeCompare(originIndexBytes, lookup.OriginIndex[:]) != 1 ||
		subtle.ConstantTimeCompare(bindingBytes, lookup.OriginBinding[:]) != 1 {
		return nil, ErrRouteCorrupt
	}
	return restoreRouteRow(
		nameKey, namespaceID, routeIDBytes, originIndexBytes, credentialBytes,
		encryptedOrigin, encryptedAccount, bindingBytes, version,
	)
}

func restoreRouteRow(
	nameKey *cryptokit.Key,
	namespaceID protocol.NamespaceID,
	routeIDBytes []byte,
	originIndexBytes []byte,
	credentialBytes []byte,
	encryptedOrigin []byte,
	encryptedAccount []byte,
	bindingBytes []byte,
	version int64,
) (*domain.EncryptedRouteEntry, error) {
	if len(routeIDBytes) != sha256.Size || len(originIndexBytes) != sha256.Size ||
		len(credentialBytes) != protocol.CredentialIDSize ||
		len(bindingBytes) != cryptokit.OriginBindingSize || version < 1 {
		return nil, ErrRouteCorrupt
	}
	var routeID cryptokit.RouteID
	var originIndex cryptokit.RouteOriginIndex
	var credentialID protocol.CredentialID
	var binding [cryptokit.OriginBindingSize]byte
	copy(routeID[:], routeIDBytes)
	copy(originIndex[:], originIndexBytes)
	copy(credentialID[:], credentialBytes)
	copy(binding[:], bindingBytes)
	entry, err := domain.RestoreEncryptedRouteEntry(
		nameKey,
		namespaceID,
		credentialID,
		domain.RouteLookup{
			RouteID: routeID, OriginIndex: originIndex, OriginBinding: binding,
		},
		uint64(version),
		encryptedOrigin,
		encryptedAccount,
	)
	if err != nil {
		return nil, ErrRouteCorrupt
	}
	return entry, nil
}
