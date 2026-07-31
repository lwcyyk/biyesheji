// Package platform contains infrastructure-neutral process contracts. Domain
// and application packages may depend on these interfaces; concrete HTTP,
// SQLite, filesystem, and chain adapters must depend in the opposite direction.
package platform

import (
	"context"
	"crypto/sha256"
	"io"
	"time"
)

// Clock makes wall-clock access explicit. Security ordering must still use
// anchor sequence or epoch, never this display/retrieval time.
type Clock interface {
	Now() time.Time
}

// EntropySource is the narrow randomness port used by constructors that need
// injection. Production composition roots provide crypto/rand.Reader; a test
// source must never be accepted by production-safe constructors.
type EntropySource interface {
	io.Reader
}

// ObjectRef identifies an immutable ciphertext object by its complete bytes.
type ObjectRef struct {
	Digest [sha256.Size]byte
	Size   uint64
}

// CiphertextObjectStore persists opaque, immutable envelopes. Plaintext and
// root secrets are intentionally absent from this contract.
type CiphertextObjectStore interface {
	PutIfAbsent(ctx context.Context, object []byte) (ObjectRef, error)
	Get(ctx context.Context, ref ObjectRef) ([]byte, error)
	Has(ctx context.Context, ref ObjectRef) (bool, error)
}

// Transaction is an application-owned unit of work. Repositories join a
// transaction supplied by the composition root instead of opening nested
// database transactions themselves.
type Transaction interface {
	Commit() error
	Rollback() error
}

// TransactionManager supplies a technology-neutral atomic boundary.
type TransactionManager interface {
	Begin(ctx context.Context) (Transaction, error)
}
