package domain

import (
	"crypto/sha256"
	"errors"

	"vpass.local/vpass/internal/cryptokit"
	"vpass.local/vpass/internal/protocol"
)

var ErrInvalidRouteEntry = errors.New("invalid encrypted route entry")

// RouteLookup contains only keyed private indexes and an OriginBinding. It is
// safe for the local repository but must not be published to cloud/log layers.
type RouteLookup struct {
	RouteID       cryptokit.RouteID
	OriginIndex   cryptokit.RouteOriginIndex
	OriginBinding [cryptokit.OriginBindingSize]byte
}

// EncryptedRouteEntry contains no plaintext Origin or AccountID.
type EncryptedRouteEntry struct {
	namespaceID      protocol.NamespaceID
	credentialID     protocol.CredentialID
	lookup           RouteLookup
	routeVersion     uint64
	encryptedOrigin  []byte
	encryptedAccount []byte
}

// BuildRouteLookup derives exact and origin-only indexes from a normalized
// Origin without allowing its canonical bytes to escape the callback.
func BuildRouteLookup(
	nameKey *cryptokit.Key,
	origin Origin,
	accountID []byte,
) (RouteLookup, error) {
	var result RouteLookup
	if nameKey == nil || len(accountID) == 0 {
		return result, ErrInvalidRouteEntry
	}
	err := origin.UseCanonical(func(canonical []byte) error {
		var deriveErr error
		result.RouteID, deriveErr = cryptokit.DeriveRouteID(nameKey, canonical, accountID)
		if deriveErr != nil {
			return deriveErr
		}
		result.OriginIndex, deriveErr = cryptokit.DeriveRouteOriginIndex(nameKey, canonical)
		if deriveErr != nil {
			return deriveErr
		}
		result.OriginBinding, deriveErr = cryptokit.DeriveOriginBinding(
			nameKey, canonical, accountID,
		)
		return deriveErr
	})
	if err != nil || routeDomainAllZero(result.RouteID[:]) ||
		routeDomainAllZero(result.OriginIndex[:]) ||
		routeDomainAllZero(result.OriginBinding[:]) {
		return RouteLookup{}, ErrInvalidRouteEntry
	}
	return result, nil
}

// BuildEncryptedRouteEntry encrypts both relationship values with independent
// nonces and AAD while retaining only keyed indexes in the database row.
func BuildEncryptedRouteEntry(
	nameKey *cryptokit.Key,
	namespaceID protocol.NamespaceID,
	origin Origin,
	accountID []byte,
	credentialID protocol.CredentialID,
	routeVersion uint64,
) (*EncryptedRouteEntry, error) {
	if nameKey == nil || routeDomainAllZero(namespaceID[:]) ||
		routeDomainAllZero(credentialID[:]) || routeVersion == 0 ||
		len(accountID) == 0 {
		return nil, ErrInvalidRouteEntry
	}
	lookup, err := BuildRouteLookup(nameKey, origin, accountID)
	if err != nil {
		return nil, err
	}
	var encryptedOrigin []byte
	err = origin.UseCanonical(func(canonical []byte) error {
		plaintext, createErr := cryptokit.NewSecret(canonical)
		if createErr != nil {
			return createErr
		}
		defer plaintext.Destroy()
		encrypted, encryptErr := cryptokit.EncryptRouteValue(
			nameKey,
			cryptokit.RouteContext{
				NamespaceID: namespaceID, RouteID: lookup.RouteID,
				OriginIndex: lookup.OriginIndex, RouteVersion: routeVersion,
				ValueType: cryptokit.RouteValueOrigin,
			},
			plaintext,
		)
		if encryptErr != nil {
			return encryptErr
		}
		encryptedOrigin, encryptErr = encrypted.MarshalBinary()
		return encryptErr
	})
	if err != nil {
		clear(encryptedOrigin)
		return nil, ErrInvalidRouteEntry
	}
	accountSecret, err := cryptokit.NewSecret(accountID)
	if err != nil {
		clear(encryptedOrigin)
		return nil, ErrInvalidRouteEntry
	}
	defer accountSecret.Destroy()
	encrypted, err := cryptokit.EncryptRouteValue(
		nameKey,
		cryptokit.RouteContext{
			NamespaceID: namespaceID, RouteID: lookup.RouteID,
			OriginIndex: lookup.OriginIndex, RouteVersion: routeVersion,
			ValueType: cryptokit.RouteValueAccount,
		},
		accountSecret,
	)
	if err != nil {
		clear(encryptedOrigin)
		return nil, ErrInvalidRouteEntry
	}
	encryptedAccount, err := encrypted.MarshalBinary()
	if err != nil {
		clear(encryptedOrigin)
		return nil, ErrInvalidRouteEntry
	}
	return &EncryptedRouteEntry{
		namespaceID: namespaceID, credentialID: credentialID, lookup: lookup,
		routeVersion:    routeVersion,
		encryptedOrigin: encryptedOrigin, encryptedAccount: encryptedAccount,
	}, nil
}

func (entry *EncryptedRouteEntry) NamespaceID() protocol.NamespaceID {
	if entry == nil {
		return protocol.NamespaceID{}
	}
	return entry.namespaceID
}

func (entry *EncryptedRouteEntry) CredentialID() protocol.CredentialID {
	if entry == nil {
		return protocol.CredentialID{}
	}
	return entry.credentialID
}

func (entry *EncryptedRouteEntry) Lookup() RouteLookup {
	if entry == nil {
		return RouteLookup{}
	}
	return entry.lookup
}

func (entry *EncryptedRouteEntry) RouteVersion() uint64 {
	if entry == nil {
		return 0
	}
	return entry.routeVersion
}

func (entry *EncryptedRouteEntry) EncryptedOrigin() []byte {
	if entry == nil {
		return nil
	}
	return append([]byte(nil), entry.encryptedOrigin...)
}

func (entry *EncryptedRouteEntry) EncryptedAccount() []byte {
	if entry == nil {
		return nil
	}
	return append([]byte(nil), entry.encryptedAccount...)
}

// ValidateEncryptedRouteEntry authenticates both ciphertext projections
// without returning either plaintext.
func ValidateEncryptedRouteEntry(
	nameKey *cryptokit.Key,
	entry *EncryptedRouteEntry,
) error {
	if nameKey == nil || entry == nil || routeDomainAllZero(entry.namespaceID[:]) ||
		routeDomainAllZero(entry.credentialID[:]) || entry.routeVersion == 0 ||
		routeDomainAllZero(entry.lookup.RouteID[:]) ||
		routeDomainAllZero(entry.lookup.OriginIndex[:]) ||
		routeDomainAllZero(entry.lookup.OriginBinding[:]) {
		return ErrInvalidRouteEntry
	}
	for _, value := range []struct {
		encoded   []byte
		valueType cryptokit.RouteValueType
	}{
		{entry.encryptedOrigin, cryptokit.RouteValueOrigin},
		{entry.encryptedAccount, cryptokit.RouteValueAccount},
	} {
		encrypted, err := cryptokit.ParseRouteCiphertext(value.encoded)
		if err != nil {
			return ErrInvalidRouteEntry
		}
		plaintext, err := cryptokit.OpenRouteValue(
			nameKey,
			cryptokit.RouteContext{
				NamespaceID: entry.namespaceID, RouteID: entry.lookup.RouteID,
				OriginIndex: entry.lookup.OriginIndex, RouteVersion: entry.routeVersion,
				ValueType: value.valueType,
			},
			encrypted,
		)
		if err != nil {
			return ErrInvalidRouteEntry
		}
		plaintext.Destroy()
	}
	return nil
}

// RestoreEncryptedRouteEntry validates adapter-loaded bytes before rebuilding
// a domain object.
func RestoreEncryptedRouteEntry(
	nameKey *cryptokit.Key,
	namespaceID protocol.NamespaceID,
	credentialID protocol.CredentialID,
	lookup RouteLookup,
	routeVersion uint64,
	encryptedOrigin []byte,
	encryptedAccount []byte,
) (*EncryptedRouteEntry, error) {
	entry := &EncryptedRouteEntry{
		namespaceID: namespaceID, credentialID: credentialID, lookup: lookup,
		routeVersion:     routeVersion,
		encryptedOrigin:  append([]byte(nil), encryptedOrigin...),
		encryptedAccount: append([]byte(nil), encryptedAccount...),
	}
	if err := ValidateEncryptedRouteEntry(nameKey, entry); err != nil {
		clear(entry.encryptedOrigin)
		clear(entry.encryptedAccount)
		return nil, err
	}
	return entry, nil
}

// RouteFingerprint is a local diagnostic digest that does not reveal route
// plaintext and is never used as a public identity.
func (entry *EncryptedRouteEntry) RouteFingerprint() [sha256.Size]byte {
	if entry == nil {
		return [sha256.Size]byte{}
	}
	hash := sha256.New()
	_, _ = hash.Write(entry.lookup.RouteID[:])
	_, _ = hash.Write(entry.credentialID[:])
	_, _ = hash.Write(entry.encryptedOrigin)
	_, _ = hash.Write(entry.encryptedAccount)
	var result [sha256.Size]byte
	copy(result[:], hash.Sum(nil))
	return result
}

func routeDomainAllZero(input []byte) bool {
	var combined byte
	for _, value := range input {
		combined |= value
	}
	return combined == 0
}
