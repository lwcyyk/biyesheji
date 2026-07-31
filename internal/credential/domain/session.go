package domain

import (
	"crypto/rand"
	"crypto/subtle"
	"errors"
	"io"
	"sync"
	"time"

	"vdns.local/vdns/internal/cryptokit"
	"vdns.local/vdns/internal/protocol"
)

const (
	SessionIDSize           = 16
	SecretHandleIDSize      = 16
	ExtensionInstallationID = 32
	MaxSessionHandles       = 128
	MaxSecretHandleTTL      = time.Minute
	MaxSessionOrigins       = 4096
)

var (
	ErrInvalidVaultSession = errors.New("invalid vault session")
	ErrVaultSessionLocked  = errors.New("vault session is locked")
	ErrVaultSessionExpired = errors.New("vault session expired")
	ErrSecretHandle        = errors.New("secret handle rejected")
	ErrSecretHandleQuota   = errors.New("secret handle quota exceeded")
)

type (
	SessionID      [SessionIDSize]byte
	SecretHandleID [SecretHandleIDSize]byte
	InstallationID [ExtensionInstallationID]byte
)

type VaultSessionConfig struct {
	CreatedAt             time.Time
	IdleTimeout           time.Duration
	AbsoluteTimeout       time.Duration
	MaxHandles            int
	AllowedOriginBindings [][cryptokit.OriginBindingSize]byte
}

type SecretHandleContext struct {
	InstallationID InstallationID
	OriginBinding  [cryptokit.OriginBindingSize]byte
	CredentialID   protocol.CredentialID
	FieldType      cryptokit.FieldType
}

type secretHandle struct {
	secret    *cryptokit.Secret
	context   SecretHandleContext
	expiresAt time.Time
}

// VaultSessionMetadata contains no secret material.
type VaultSessionMetadata struct {
	SessionID        SessionID
	NamespaceID      protocol.NamespaceID
	DeviceID         protocol.DeviceID
	SecretGeneration uint64
}

// VaultSession is an in-memory-only owner of an unlocked root bundle,
// generation keys and short-lived single-use secret handles.
type VaultSession struct {
	mu             sync.Mutex
	id             SessionID
	namespaceID    protocol.NamespaceID
	deviceID       protocol.DeviceID
	createdAt      time.Time
	lastUsedAt     time.Time
	expiresAt      time.Time
	idleTimeout    time.Duration
	maxHandles     int
	allowedOrigins [][cryptokit.OriginBindingSize]byte
	bundle         *cryptokit.RootSecretBundle
	keys           *cryptokit.NamespaceKeys
	handles        map[SecretHandleID]*secretHandle
	locked         bool
}

func NewVaultSession(
	bundle *cryptokit.RootSecretBundle,
	namespaceID protocol.NamespaceID,
	deviceID protocol.DeviceID,
	config VaultSessionConfig,
) (*VaultSession, error) {
	return newVaultSessionWithReader(bundle, namespaceID, deviceID, config, rand.Reader)
}

func newVaultSessionWithReader(
	bundle *cryptokit.RootSecretBundle,
	namespaceID protocol.NamespaceID,
	deviceID protocol.DeviceID,
	config VaultSessionConfig,
	random io.Reader,
) (*VaultSession, error) {
	if bundle == nil || random == nil || bundle.SecretGeneration() == 0 ||
		allZero(namespaceID[:]) || allZero(deviceID[:]) ||
		config.CreatedAt.IsZero() || config.IdleTimeout <= 0 ||
		config.AbsoluteTimeout <= 0 || config.IdleTimeout > config.AbsoluteTimeout ||
		config.MaxHandles < 1 || config.MaxHandles > MaxSessionHandles ||
		len(config.AllowedOriginBindings) == 0 {
		return nil, ErrInvalidVaultSession
	}
	origins, err := normalizeOriginAllowlist(config.AllowedOriginBindings)
	if err != nil {
		return nil, err
	}
	var sessionID SessionID
	if _, err := io.ReadFull(random, sessionID[:]); err != nil || allZero(sessionID[:]) {
		return nil, ErrInvalidVaultSession
	}

	root, err := bundle.NamespaceRootCopy()
	if err != nil {
		return nil, ErrInvalidVaultSession
	}
	defer root.Destroy()
	prk, err := cryptokit.ExtractNamespacePRK(root, namespaceID, bundle.SecretGeneration())
	if err != nil {
		return nil, ErrInvalidVaultSession
	}
	defer prk.Destroy()
	keys, err := cryptokit.DeriveNamespaceKeys(prk)
	if err != nil {
		return nil, ErrInvalidVaultSession
	}

	return &VaultSession{
		id: sessionID, namespaceID: namespaceID, deviceID: deviceID,
		createdAt: config.CreatedAt, lastUsedAt: config.CreatedAt,
		expiresAt:   config.CreatedAt.Add(config.AbsoluteTimeout),
		idleTimeout: config.IdleTimeout, maxHandles: config.MaxHandles,
		allowedOrigins: origins, bundle: bundle, keys: keys,
		handles: make(map[SecretHandleID]*secretHandle),
	}, nil
}

func (session *VaultSession) ID() SessionID {
	if session == nil {
		return SessionID{}
	}
	session.mu.Lock()
	defer session.mu.Unlock()
	if session.locked {
		return SessionID{}
	}
	return session.id
}

func (session *VaultSession) ExpiresAt() time.Time {
	if session == nil {
		return time.Time{}
	}
	session.mu.Lock()
	defer session.mu.Unlock()
	if session.locked {
		return time.Time{}
	}
	return session.expiresAt
}

// Metadata returns the public context needed to build signed control objects.
func (session *VaultSession) Metadata(now time.Time) (VaultSessionMetadata, error) {
	if session == nil {
		return VaultSessionMetadata{}, ErrVaultSessionLocked
	}
	session.mu.Lock()
	defer session.mu.Unlock()
	if err := session.requireActiveLocked(now); err != nil {
		return VaultSessionMetadata{}, err
	}
	session.lastUsedAt = now
	return VaultSessionMetadata{
		SessionID: session.id, NamespaceID: session.namespaceID,
		DeviceID:         session.deviceID,
		SecretGeneration: session.bundle.SecretGeneration(),
	}, nil
}

// AuthorizeOriginForAccount derives and adds one private OriginBinding to this
// unlocked session. The trusted local agent calls it only after an explicit
// create/autofill user gesture; browser page data cannot call it directly.
func (session *VaultSession) AuthorizeOriginForAccount(
	now time.Time,
	origin Origin,
	accountID []byte,
) ([cryptokit.OriginBindingSize]byte, error) {
	var binding [cryptokit.OriginBindingSize]byte
	if session == nil || len(accountID) == 0 {
		return binding, ErrInvalidVaultSession
	}
	session.mu.Lock()
	defer session.mu.Unlock()
	if err := session.requireActiveLocked(now); err != nil {
		return binding, err
	}
	err := origin.UseCanonical(func(canonical []byte) error {
		var deriveErr error
		binding, deriveErr = cryptokit.DeriveOriginBinding(
			session.keys.Name, canonical, accountID,
		)
		return deriveErr
	})
	if err != nil || allZero(binding[:]) {
		return [cryptokit.OriginBindingSize]byte{}, ErrOriginBinding
	}
	if !constantTimeOriginMember(session.allowedOrigins, binding) {
		if len(session.allowedOrigins) >= MaxSessionOrigins {
			return [cryptokit.OriginBindingSize]byte{}, ErrInvalidVaultSession
		}
		session.allowedOrigins = append(session.allowedOrigins, binding)
	}
	session.lastUsedAt = now
	return binding, nil
}

func (session *VaultSession) ComputeOriginBinding(
	now time.Time,
	origin Origin,
	accountID []byte,
) ([cryptokit.OriginBindingSize]byte, error) {
	var binding [cryptokit.OriginBindingSize]byte
	if session == nil {
		return binding, ErrVaultSessionLocked
	}
	session.mu.Lock()
	defer session.mu.Unlock()
	if err := session.requireActiveLocked(now); err != nil {
		return binding, err
	}
	err := origin.UseCanonical(func(canonical []byte) error {
		var deriveErr error
		binding, deriveErr = cryptokit.DeriveOriginBinding(session.keys.Name, canonical, accountID)
		return deriveErr
	})
	if err != nil {
		return [cryptokit.OriginBindingSize]byte{}, ErrOriginBinding
	}
	session.lastUsedAt = now
	return binding, nil
}

// BuildRouteLookup derives private local indexes without exposing K_name.
func (session *VaultSession) BuildRouteLookup(
	now time.Time,
	origin Origin,
	accountID []byte,
) (RouteLookup, error) {
	if session == nil {
		return RouteLookup{}, ErrVaultSessionLocked
	}
	session.mu.Lock()
	defer session.mu.Unlock()
	if err := session.requireActiveLocked(now); err != nil {
		return RouteLookup{}, err
	}
	lookup, err := BuildRouteLookup(session.keys.Name, origin, accountID)
	if err != nil {
		return RouteLookup{}, err
	}
	session.lastUsedAt = now
	return lookup, nil
}

// BuildEncryptedRouteEntry encrypts a local RouteMap row without exposing
// K_name to the application layer.
func (session *VaultSession) BuildEncryptedRouteEntry(
	now time.Time,
	origin Origin,
	accountID []byte,
	credentialID protocol.CredentialID,
	routeVersion uint64,
) (*EncryptedRouteEntry, error) {
	if session == nil {
		return nil, ErrVaultSessionLocked
	}
	session.mu.Lock()
	defer session.mu.Unlock()
	if err := session.requireActiveLocked(now); err != nil {
		return nil, err
	}
	entry, err := BuildEncryptedRouteEntry(
		session.keys.Name, session.namespaceID, origin, accountID,
		credentialID, routeVersion,
	)
	if err != nil {
		return nil, err
	}
	if !constantTimeOriginMember(session.allowedOrigins, entry.Lookup().OriginBinding) {
		return nil, ErrSecretHandle
	}
	session.lastUsedAt = now
	return entry, nil
}

// EncryptCredentialField creates one CP-2 field object without allowing the
// purpose-scoped wrap key to leave the session.
func (session *VaultSession) EncryptCredentialField(
	now time.Time,
	context cryptokit.FieldContext,
	plaintext *cryptokit.Secret,
) (*cryptokit.EncryptedField, error) {
	if session == nil || plaintext == nil {
		return nil, ErrVaultSessionLocked
	}
	session.mu.Lock()
	defer session.mu.Unlock()
	if err := session.requireActiveLocked(now); err != nil {
		return nil, err
	}
	if context.NamespaceID != session.namespaceID ||
		context.KeyGeneration != session.bundle.SecretGeneration() ||
		!constantTimeOriginMember(session.allowedOrigins, context.OriginBinding) {
		return nil, ErrSecretHandle
	}
	encrypted, err := cryptokit.EncryptField(session.keys.Wrap, context, plaintext)
	if err != nil {
		return nil, err
	}
	session.lastUsedAt = now
	return encrypted, nil
}

// DecryptCredentialField authenticates an immutable reference and returns a
// protected Secret owned by the caller.
func (session *VaultSession) DecryptCredentialField(
	now time.Time,
	credentialID protocol.CredentialID,
	reference cryptokit.FieldReference,
	encrypted *cryptokit.EncryptedField,
) (*cryptokit.Secret, error) {
	if session == nil || encrypted == nil {
		return nil, ErrVaultSessionLocked
	}
	session.mu.Lock()
	defer session.mu.Unlock()
	if err := session.requireActiveLocked(now); err != nil {
		return nil, err
	}
	if reference.KeyGeneration != session.bundle.SecretGeneration() ||
		!constantTimeOriginMember(session.allowedOrigins, reference.OriginBinding) {
		return nil, ErrSecretHandle
	}
	secret, err := cryptokit.DecryptFieldByReference(
		session.keys.Wrap, session.namespaceID, credentialID, reference, encrypted,
	)
	if err != nil {
		return nil, err
	}
	session.lastUsedAt = now
	return secret, nil
}

// AuthorizeAutofill recomputes trusted browser Origin context without exposing
// K_name.
func (session *VaultSession) AuthorizeAutofill(
	now time.Time,
	frame TrustedFrameContext,
	request AutofillRouteRequest,
	policy FrameAuthorizationPolicy,
) (AutofillAuthorization, error) {
	if session == nil {
		return AutofillAuthorization{}, ErrVaultSessionLocked
	}
	session.mu.Lock()
	defer session.mu.Unlock()
	if err := session.requireActiveLocked(now); err != nil {
		return AutofillAuthorization{}, err
	}
	authorization, err := AuthorizeAutofillRoute(
		session.keys.Name, frame, request, policy,
	)
	if err != nil || !constantTimeOriginMember(
		session.allowedOrigins, authorization.OriginBinding,
	) {
		return AutofillAuthorization{}, ErrAutofillOriginRejected
	}
	session.lastUsedAt = now
	return authorization, nil
}

// SealAuditEvent derives the epoch and per-event keys inside the unlocked
// session, returning only a public pseudonym and encrypted envelope.
func (session *VaultSession) SealAuditEvent(
	now time.Time,
	chainID string,
	eventID protocol.EventID,
	epoch uint64,
	verifiedBeacon []byte,
	plaintext *cryptokit.Secret,
) (*cryptokit.EventEnvelope, [cryptokit.DevicePseudonymSize]byte, error) {
	var pseudonym [cryptokit.DevicePseudonymSize]byte
	if session == nil || plaintext == nil {
		return nil, pseudonym, ErrVaultSessionLocked
	}
	session.mu.Lock()
	defer session.mu.Unlock()
	if err := session.requireActiveLocked(now); err != nil {
		return nil, pseudonym, err
	}
	generation := session.bundle.SecretGeneration()
	auditKey, err := cryptokit.DeriveAuditKey(
		session.keys.Audit, chainID, session.namespaceID,
		generation, epoch, verifiedBeacon,
	)
	if err != nil {
		return nil, pseudonym, err
	}
	defer auditKey.Destroy()
	pseudonym, err = cryptokit.DeriveDevicePseudonym(
		session.keys.Audit, session.deviceID, epoch,
	)
	if err != nil {
		return nil, [cryptokit.DevicePseudonymSize]byte{}, err
	}
	eventKey, err := cryptokit.DeriveEventKey(auditKey, eventID, pseudonym)
	if err != nil {
		return nil, [cryptokit.DevicePseudonymSize]byte{}, err
	}
	defer eventKey.Destroy()
	envelope, err := cryptokit.SealEvent(eventKey, cryptokit.EventContext{
		NamespaceID: session.namespaceID, EventID: eventID,
		ObjectType:      protocol.ObjectTypeOperationEvent,
		DevicePseudonym: pseudonym, KeyGeneration: generation, VRFEpoch: epoch,
	}, plaintext)
	if err != nil {
		return nil, [cryptokit.DevicePseudonymSize]byte{}, err
	}
	session.lastUsedAt = now
	return envelope, pseudonym, nil
}

// ComputeAuditReuseTag derives the epoch-scoped hidden password witness inside
// the unlocked session. The returned value is deliberately non-serializable
// and must only be embedded in an encrypted audit-event plaintext.
func (session *VaultSession) ComputeAuditReuseTag(
	now time.Time,
	chainID string,
	epoch uint64,
	verifiedBeacon []byte,
	password *cryptokit.Secret,
) (cryptokit.ReuseTag, error) {
	if session == nil || password == nil {
		return cryptokit.ReuseTag{}, ErrVaultSessionLocked
	}
	session.mu.Lock()
	defer session.mu.Unlock()
	if err := session.requireActiveLocked(now); err != nil {
		return cryptokit.ReuseTag{}, err
	}
	auditKey, err := cryptokit.DeriveAuditKey(
		session.keys.Audit, chainID, session.namespaceID,
		session.bundle.SecretGeneration(), epoch, verifiedBeacon,
	)
	if err != nil {
		return cryptokit.ReuseTag{}, err
	}
	defer auditKey.Destroy()
	tag, err := cryptokit.ComputeReuseTag(auditKey, password)
	if err != nil {
		return cryptokit.ReuseTag{}, err
	}
	session.lastUsedAt = now
	return tag, nil
}

func (session *VaultSession) IssueSecretHandle(
	now time.Time,
	ttl time.Duration,
	context SecretHandleContext,
	secret *cryptokit.Secret,
) (SecretHandleID, error) {
	if session == nil || secret == nil || secret.Len() == 0 || ttl <= 0 ||
		ttl > MaxSecretHandleTTL || !context.FieldType.Valid() ||
		allZero(context.InstallationID[:]) || allZero(context.OriginBinding[:]) ||
		allZero(context.CredentialID[:]) {
		return SecretHandleID{}, ErrSecretHandle
	}
	session.mu.Lock()
	defer session.mu.Unlock()
	if err := session.requireActiveLocked(now); err != nil {
		return SecretHandleID{}, err
	}
	if !constantTimeOriginMember(session.allowedOrigins, context.OriginBinding) {
		return SecretHandleID{}, ErrSecretHandle
	}
	if len(session.handles) >= session.maxHandles {
		return SecretHandleID{}, ErrSecretHandleQuota
	}
	expiresAt := now.Add(ttl)
	if expiresAt.After(session.expiresAt) {
		expiresAt = session.expiresAt
	}
	copyOfSecret, err := secret.Clone()
	if err != nil {
		return SecretHandleID{}, ErrSecretHandle
	}
	var id SecretHandleID
	for attempt := 0; attempt < 4; attempt++ {
		if _, err := io.ReadFull(rand.Reader, id[:]); err != nil || allZero(id[:]) {
			continue
		}
		if _, exists := session.handles[id]; !exists {
			session.handles[id] = &secretHandle{
				secret: copyOfSecret, context: context, expiresAt: expiresAt,
			}
			session.lastUsedAt = now
			return id, nil
		}
	}
	copyOfSecret.Destroy()
	return SecretHandleID{}, ErrSecretHandle
}

// ConsumeSecretHandle removes a handle before returning its protected secret.
// The caller owns and must destroy the returned Secret.
func (session *VaultSession) ConsumeSecretHandle(
	now time.Time,
	id SecretHandleID,
	expected SecretHandleContext,
) (*cryptokit.Secret, error) {
	if session == nil || allZero(id[:]) {
		return nil, ErrSecretHandle
	}
	session.mu.Lock()
	defer session.mu.Unlock()
	if err := session.requireActiveLocked(now); err != nil {
		return nil, err
	}
	handle, exists := session.handles[id]
	if !exists || handle == nil {
		return nil, ErrSecretHandle
	}
	if !now.Before(handle.expiresAt) {
		handle.secret.Destroy()
		delete(session.handles, id)
		return nil, ErrSecretHandle
	}
	if !secretHandleContextEqual(handle.context, expected) {
		return nil, ErrSecretHandle
	}
	delete(session.handles, id)
	session.lastUsedAt = now
	return handle.secret, nil
}

func (session *VaultSession) ActiveHandleCount(now time.Time) int {
	if session == nil {
		return 0
	}
	session.mu.Lock()
	defer session.mu.Unlock()
	if session.requireActiveLocked(now) != nil {
		return 0
	}
	for id, handle := range session.handles {
		if handle == nil || !now.Before(handle.expiresAt) {
			if handle != nil && handle.secret != nil {
				handle.secret.Destroy()
			}
			delete(session.handles, id)
		}
	}
	return len(session.handles)
}

// Lock implements explicit lock, timeout and OS-lock-screen destruction.
func (session *VaultSession) Lock() {
	if session == nil {
		return
	}
	session.mu.Lock()
	defer session.mu.Unlock()
	session.lockLocked()
}

func (session *VaultSession) requireActiveLocked(now time.Time) error {
	if session.locked || session.bundle == nil || session.keys == nil {
		return ErrVaultSessionLocked
	}
	if now.IsZero() || now.Before(session.createdAt) {
		return ErrInvalidVaultSession
	}
	if !now.Before(session.expiresAt) || now.Sub(session.lastUsedAt) >= session.idleTimeout {
		session.lockLocked()
		return ErrVaultSessionExpired
	}
	return nil
}

func (session *VaultSession) lockLocked() {
	if session.locked {
		return
	}
	for id, handle := range session.handles {
		if handle != nil && handle.secret != nil {
			handle.secret.Destroy()
		}
		delete(session.handles, id)
	}
	if session.keys != nil {
		session.keys.Destroy()
		session.keys = nil
	}
	if session.bundle != nil {
		session.bundle.Destroy()
		session.bundle = nil
	}
	session.allowedOrigins = nil
	session.id = SessionID{}
	session.locked = true
}

func normalizeOriginAllowlist(
	input [][cryptokit.OriginBindingSize]byte,
) ([][cryptokit.OriginBindingSize]byte, error) {
	result := make([][cryptokit.OriginBindingSize]byte, 0, len(input))
	for _, candidate := range input {
		if allZero(candidate[:]) {
			return nil, ErrInvalidVaultSession
		}
		if constantTimeOriginMember(result, candidate) {
			continue
		}
		result = append(result, candidate)
	}
	return result, nil
}

func constantTimeOriginMember(
	values [][cryptokit.OriginBindingSize]byte,
	target [cryptokit.OriginBindingSize]byte,
) bool {
	found := 0
	for _, value := range values {
		found |= subtle.ConstantTimeCompare(value[:], target[:])
	}
	return found == 1
}

func secretHandleContextEqual(left, right SecretHandleContext) bool {
	matches := subtle.ConstantTimeCompare(left.InstallationID[:], right.InstallationID[:])
	matches &= subtle.ConstantTimeCompare(left.OriginBinding[:], right.OriginBinding[:])
	matches &= subtle.ConstantTimeCompare(left.CredentialID[:], right.CredentialID[:])
	if left.FieldType != right.FieldType {
		matches = 0
	}
	return matches == 1
}

func allZero(input []byte) bool {
	var combined byte
	for _, value := range input {
		combined |= value
	}
	return combined == 0
}
