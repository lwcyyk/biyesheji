package domain

import (
	"errors"

	"vdns.local/vdns/internal/cryptokit"
)

var ErrOriginBinding = errors.New("origin binding failed")

// ComputeOriginBinding converts the private canonical Origin/account pair into
// a namespace-scoped opaque binding. Neither input is returned or persisted by
// this boundary; the result is suitable for local routing and field AAD.
func ComputeOriginBinding(
	nameKey *cryptokit.Key,
	origin Origin,
	accountID []byte,
) ([cryptokit.OriginBindingSize]byte, error) {
	var binding [cryptokit.OriginBindingSize]byte
	if nameKey == nil || len(accountID) == 0 {
		return binding, ErrOriginBinding
	}
	err := origin.UseCanonical(func(canonical []byte) error {
		var deriveErr error
		binding, deriveErr = cryptokit.DeriveOriginBinding(nameKey, canonical, accountID)
		return deriveErr
	})
	if err != nil {
		return [cryptokit.OriginBindingSize]byte{}, ErrOriginBinding
	}
	return binding, nil
}
