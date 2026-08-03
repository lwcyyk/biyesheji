package domain

import (
	"bytes"
	"crypto/sha256"
	"errors"
	"sync"
	"testing"
	"time"

	"vpass.local/vpass/internal/cryptokit"
	"vpass.local/vpass/internal/protocol"
)

func TestVaultSessionSingleUseHandleAndContextBinding(t *testing.T) {
	now := time.Unix(1_700_000_000, 0).UTC()
	bundle := sessionRootBundle(t)
	namespaceID, deviceID := sessionIDs()
	allowed := sessionBytes32(71)
	session, err := newVaultSessionWithReader(
		bundle,
		namespaceID,
		deviceID,
		VaultSessionConfig{
			CreatedAt: now, IdleTimeout: 5 * time.Minute,
			AbsoluteTimeout: time.Hour, MaxHandles: 2,
			AllowedOriginBindings: [][cryptokit.OriginBindingSize]byte{allowed},
		},
		bytes.NewReader(sessionBytes(16, 1)),
	)
	if err != nil {
		t.Fatal(err)
	}
	defer session.Lock()
	context := sessionHandleContext(allowed)
	secret, _ := cryptokit.NewSecret([]byte("one-time-password"))
	defer secret.Destroy()
	handleID, err := session.IssueSecretHandle(now, 30*time.Second, context, secret)
	if err != nil {
		t.Fatal(err)
	}
	if session.ActiveHandleCount(now) != 1 {
		t.Fatal("issued handle not counted")
	}

	wrong := context
	wrong.OriginBinding[0] ^= 1
	if opened, openErr := session.ConsumeSecretHandle(now, handleID, wrong); opened != nil || !errors.Is(openErr, ErrSecretHandle) {
		t.Fatalf("cross-origin consume = %v, %v", opened, openErr)
	}
	opened, err := session.ConsumeSecretHandle(now, handleID, context)
	if err != nil {
		t.Fatal(err)
	}
	if opened.Len() != len("one-time-password") {
		t.Fatal("returned secret has wrong length")
	}
	opened.Destroy()
	if replay, replayErr := session.ConsumeSecretHandle(now, handleID, context); replay != nil || !errors.Is(replayErr, ErrSecretHandle) {
		t.Fatalf("handle replay = %v, %v", replay, replayErr)
	}
}

func TestVaultSessionLockAndTimeoutDestroyHandlesAndRoots(t *testing.T) {
	now := time.Unix(1_700_000_000, 0).UTC()
	for name, lockAt := range map[string]time.Time{
		"explicit": now.Add(time.Second),
		"idle":     now.Add(2 * time.Minute),
		"absolute": now.Add(11 * time.Minute),
	} {
		t.Run(name, func(t *testing.T) {
			bundle := sessionRootBundle(t)
			namespaceID, deviceID := sessionIDs()
			allowed := sessionBytes32(81)
			session, err := newVaultSessionWithReader(
				bundle,
				namespaceID,
				deviceID,
				VaultSessionConfig{
					CreatedAt: now, IdleTimeout: time.Minute,
					AbsoluteTimeout: 10 * time.Minute, MaxHandles: 2,
					AllowedOriginBindings: [][cryptokit.OriginBindingSize]byte{allowed},
				},
				bytes.NewReader(sessionBytes(16, 21)),
			)
			if err != nil {
				t.Fatal(err)
			}
			secret, _ := cryptokit.NewSecret([]byte("destroy-on-lock"))
			context := sessionHandleContext(allowed)
			handleID, err := session.IssueSecretHandle(now, 30*time.Second, context, secret)
			secret.Destroy()
			if err != nil {
				t.Fatal(err)
			}
			if name == "explicit" {
				session.Lock()
			} else if session.ActiveHandleCount(lockAt) != 0 {
				t.Fatal("expired session retained a handle")
			}
			if session.ID() != (SessionID{}) {
				t.Fatal("locked session retained its public identifier")
			}
			if opened, openErr := session.ConsumeSecretHandle(lockAt, handleID, context); opened != nil ||
				(!errors.Is(openErr, ErrVaultSessionLocked) && !errors.Is(openErr, ErrVaultSessionExpired)) {
				t.Fatalf("consume after lock = %v, %v", opened, openErr)
			}
			if root, rootErr := bundle.NamespaceRootCopy(); root != nil || !errors.Is(rootErr, cryptokit.ErrSecretDestroyed) {
				t.Fatalf("root survived session lock = %v, %v", root, rootErr)
			}
		})
	}
}

func TestVaultSessionOriginAllowlistQuotaAndHandleExpiry(t *testing.T) {
	now := time.Unix(1_700_000_000, 0).UTC()
	bundle := sessionRootBundle(t)
	namespaceID, deviceID := sessionIDs()
	allowed := sessionBytes32(91)
	session, err := newVaultSessionWithReader(
		bundle,
		namespaceID,
		deviceID,
		VaultSessionConfig{
			CreatedAt: now, IdleTimeout: 5 * time.Minute,
			AbsoluteTimeout: time.Hour, MaxHandles: 1,
			AllowedOriginBindings: [][cryptokit.OriginBindingSize]byte{allowed, allowed},
		},
		bytes.NewReader(sessionBytes(16, 31)),
	)
	if err != nil {
		t.Fatal(err)
	}
	defer session.Lock()
	secret, _ := cryptokit.NewSecret([]byte("secret"))
	defer secret.Destroy()
	context := sessionHandleContext(allowed)
	first, err := session.IssueSecretHandle(now, time.Second, context, secret)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := session.IssueSecretHandle(now, time.Second, context, secret); !errors.Is(err, ErrSecretHandleQuota) {
		t.Fatalf("quota error = %v", err)
	}
	if opened, err := session.ConsumeSecretHandle(now.Add(2*time.Second), first, context); opened != nil || !errors.Is(err, ErrSecretHandle) {
		t.Fatalf("expired handle = %v, %v", opened, err)
	}
	wrongOrigin := context
	wrongOrigin.OriginBinding[0] ^= 1
	if _, err := session.IssueSecretHandle(now.Add(3*time.Second), time.Second, wrongOrigin, secret); !errors.Is(err, ErrSecretHandle) {
		t.Fatalf("non-allowlisted origin = %v", err)
	}
}

func TestVaultSessionConcurrentLockAndConsumeIsRaceFree(t *testing.T) {
	now := time.Unix(1_700_000_000, 0).UTC()
	bundle := sessionRootBundle(t)
	namespaceID, deviceID := sessionIDs()
	allowed := sessionBytes32(101)
	session, err := newVaultSessionWithReader(
		bundle,
		namespaceID,
		deviceID,
		VaultSessionConfig{
			CreatedAt: now, IdleTimeout: 5 * time.Minute,
			AbsoluteTimeout: time.Hour, MaxHandles: 32,
			AllowedOriginBindings: [][cryptokit.OriginBindingSize]byte{allowed},
		},
		bytes.NewReader(sessionBytes(16, 41)),
	)
	if err != nil {
		t.Fatal(err)
	}
	context := sessionHandleContext(allowed)
	var ids []SecretHandleID
	for index := 0; index < 16; index++ {
		secret, _ := cryptokit.NewSecret([]byte("concurrent"))
		id, issueErr := session.IssueSecretHandle(now, time.Minute, context, secret)
		secret.Destroy()
		if issueErr != nil {
			t.Fatal(issueErr)
		}
		ids = append(ids, id)
	}
	var workers sync.WaitGroup
	for _, id := range ids {
		id := id
		workers.Add(1)
		go func() {
			defer workers.Done()
			if secret, consumeErr := session.ConsumeSecretHandle(now, id, context); consumeErr == nil {
				secret.Destroy()
			}
		}()
	}
	session.Lock()
	workers.Wait()
	if session.ActiveHandleCount(now) != 0 {
		t.Fatal("locked session retained concurrent handles")
	}
}

func TestVaultSessionOwnsRouteAndFieldKeysEndToEnd(t *testing.T) {
	now := time.Unix(1_700_000_000, 0).UTC()
	bundle := sessionRootBundle(t)
	namespaceID, deviceID := sessionIDs()
	session, err := newVaultSessionWithReader(
		bundle,
		namespaceID,
		deviceID,
		VaultSessionConfig{
			CreatedAt: now, IdleTimeout: 5 * time.Minute,
			AbsoluteTimeout: time.Hour, MaxHandles: 4,
			AllowedOriginBindings: [][cryptokit.OriginBindingSize]byte{sessionBytes32(111)},
		},
		bytes.NewReader(sessionBytes(16, 51)),
	)
	if err != nil {
		t.Fatal(err)
	}
	defer session.Lock()
	metadata, err := session.Metadata(now)
	if err != nil || metadata.NamespaceID != namespaceID ||
		metadata.DeviceID != deviceID || metadata.SecretGeneration != 1 {
		t.Fatalf("session metadata = %+v, %v", metadata, err)
	}
	origin, err := NormalizeOrigin("https://Example.COM")
	if err != nil {
		t.Fatal(err)
	}
	defer origin.Destroy()
	accountID := []byte("alice@example.test")
	binding, err := session.AuthorizeOriginForAccount(now, origin, accountID)
	if err != nil {
		t.Fatal(err)
	}
	var credentialID protocol.CredentialID
	copy(credentialID[:], sessionBytes(len(credentialID), 71))
	entry, err := session.BuildEncryptedRouteEntry(
		now, origin, accountID, credentialID, 1,
	)
	if err != nil || entry.Lookup().OriginBinding != binding {
		t.Fatalf("route entry = %v, %v", entry, err)
	}
	lookup, err := session.BuildRouteLookup(now, origin, accountID)
	if err != nil || lookup != entry.Lookup() {
		t.Fatalf("route lookup = %+v, %v", lookup, err)
	}
	plaintext, _ := cryptokit.NewSecret([]byte("generated-password"))
	defer plaintext.Destroy()
	context := cryptokit.FieldContext{
		NamespaceID: namespaceID, CredentialID: credentialID,
		CredentialVersion: 1, FieldType: cryptokit.FieldPassword,
		KeyGeneration:    metadata.SecretGeneration,
		CryptoPolicyHash: sha256.Sum256([]byte("policy")),
		OriginBinding:    binding,
	}
	encrypted, err := session.EncryptCredentialField(now, context, plaintext)
	if err != nil {
		t.Fatal(err)
	}
	reference, _ := encrypted.Reference()
	decrypted, err := session.DecryptCredentialField(
		now, credentialID, reference, encrypted,
	)
	if err != nil {
		t.Fatal(err)
	}
	if decrypted.Len() != plaintext.Len() {
		t.Fatal("decrypted secret length changed")
	}
	handleContext := SecretHandleContext{
		InstallationID: sessionHandleContext(binding).InstallationID,
		OriginBinding:  binding, CredentialID: credentialID,
		FieldType: cryptokit.FieldPassword,
	}
	handle, err := session.IssueSecretHandle(
		now, time.Second, handleContext, decrypted,
	)
	decrypted.Destroy()
	if err != nil {
		t.Fatal(err)
	}
	consumed, err := session.ConsumeSecretHandle(now, handle, handleContext)
	if err != nil {
		t.Fatal(err)
	}
	consumed.Destroy()
}

func sessionHandleContext(binding [cryptokit.OriginBindingSize]byte) SecretHandleContext {
	var installation InstallationID
	var credentialID protocol.CredentialID
	copy(installation[:], sessionBytes(len(installation), 11))
	copy(credentialID[:], sessionBytes(len(credentialID), 31))
	return SecretHandleContext{
		InstallationID: installation, OriginBinding: binding,
		CredentialID: credentialID, FieldType: cryptokit.FieldPassword,
	}
}

func sessionRootBundle(t *testing.T) *cryptokit.RootSecretBundle {
	t.Helper()
	bundle, _, err := cryptokit.GenerateRootSecretBundle(1, 1)
	if err != nil {
		t.Fatal(err)
	}
	return bundle
}

func sessionIDs() (protocol.NamespaceID, protocol.DeviceID) {
	var namespaceID protocol.NamespaceID
	var deviceID protocol.DeviceID
	copy(namespaceID[:], sessionBytes(len(namespaceID), 1))
	copy(deviceID[:], sessionBytes(len(deviceID), 41))
	return namespaceID, deviceID
}

func sessionBytes32(start byte) [cryptokit.OriginBindingSize]byte {
	var value [cryptokit.OriginBindingSize]byte
	copy(value[:], sessionBytes(len(value), start))
	return value
}

func sessionBytes(size int, start byte) []byte {
	result := make([]byte, size)
	for index := range result {
		result[index] = start + byte(index)
	}
	return result
}
