package application

import (
	"crypto/sha256"

	exposuredomain "vdns.local/vdns/internal/exposure/domain"
	"vdns.local/vdns/internal/protocol"
)

// ValidatedAffectedScope adapts a previously validated AffectedSet to the
// remediation domain without weakening the AffectedRoot boundary.
type ValidatedAffectedScope struct {
	set exposuredomain.AffectedSet
}

func NewValidatedAffectedScope(
	snapshot exposuredomain.IncidentSnapshot,
	set exposuredomain.AffectedSet,
) (ValidatedAffectedScope, error) {
	if set.Validate(snapshot) != nil {
		return ValidatedAffectedScope{}, exposuredomain.ErrInvalidAffectedSet
	}
	return ValidatedAffectedScope{set: set}, nil
}

func (scope ValidatedAffectedScope) Contains(id protocol.CredentialID) bool {
	return scope.set.Contains(id)
}

func (scope ValidatedAffectedScope) Root() [sha256.Size]byte {
	return scope.set.AffectedRoot
}
