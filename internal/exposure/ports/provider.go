// Package ports contains the optional proof-provider boundary. Daily password
// management never imports or calls this package.
package ports

import (
	"context"
	"crypto/sha256"
	"errors"

	exposuredomain "vpass.local/vpass/internal/exposure/domain"
)

var ErrOptionalFeatureUnavailable = errors.New("OPTIONAL_FEATURE_UNAVAILABLE")

type ProofSystem string

const (
	ProofSystemScopeZK     ProofSystem = "SCOPE_ZK"
	ProofSystemGenericZKVM ProofSystem = "GENERIC_ZKVM"
)

type Request struct {
	Snapshot        exposuredomain.IncidentSnapshot
	IncidentWitness []byte
}

type Result struct {
	Affected    exposuredomain.AffectedSet
	ProofBytes  []byte
	ProofDigest [sha256.Size]byte
	System      ProofSystem
}

type Provider interface {
	Analyze(context.Context, Request) (Result, error)
}

// DisabledProvider is the stable production default until an independently
// reviewed SCOPE-ZK implementation is configured.
type DisabledProvider struct{}

func (DisabledProvider) Analyze(context.Context, Request) (Result, error) {
	return Result{}, ErrOptionalFeatureUnavailable
}
