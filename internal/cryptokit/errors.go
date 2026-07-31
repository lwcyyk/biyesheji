package cryptokit

import "errors"

var (
	// ErrRejectAEAD intentionally collapses all authentication, context, digest,
	// and ciphertext failures into one externally observable result.
	ErrRejectAEAD = errors.New("REJECT_AEAD")

	// ErrInvalidInput reports a public-parameter validation failure on an
	// encryption or derivation request. It never includes secret material.
	ErrInvalidInput = errors.New("INVALID_CRYPTO_INPUT")

	// ErrRandomSource reports that the configured random source could not fill
	// the requested buffer.
	ErrRandomSource = errors.New("RANDOM_SOURCE_FAILED")

	// ErrSecretDestroyed reports an attempted use of secret material after its
	// best-effort destruction.
	ErrSecretDestroyed = errors.New("SECRET_DESTROYED")

	// ErrSecretSerialization prevents secrets from crossing generic
	// serialization boundaries.
	ErrSecretSerialization = errors.New("SECRET_SERIALIZATION_FORBIDDEN")

	// ErrInvalidKeyPurpose reports an attempted cross-domain key use. The
	// purpose tag is internal and cannot be selected by callers.
	ErrInvalidKeyPurpose = errors.New("KEY_PURPOSE_MISMATCH")
)
