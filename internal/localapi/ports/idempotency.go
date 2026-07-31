// Package ports defines technology-neutral local API persistence boundaries.
package ports

import (
	"context"
	"crypto/sha256"
)

type IdempotencyResponse struct {
	KeyHash        [sha256.Size]byte
	OperationScope string
	RequestHash    [sha256.Size]byte
	Status         int
	Headers        map[string][]string
	Body           []byte
	CreatedAtMS    uint64
	ExpiresAtMS    uint64
}

// IdempotencyStore stores only a key hash. Vault sessions and one-use secret
// handles remain process-local and are deliberately not persisted through this
// port.
type IdempotencyStore interface {
	Load(context.Context, [sha256.Size]byte, uint64) (IdempotencyResponse, bool, error)
	Put(context.Context, IdempotencyResponse) error
	PurgeExpired(context.Context, uint64) error
}
