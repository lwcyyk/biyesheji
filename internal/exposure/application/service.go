// Package application coordinates explicit, optional incident analysis.
package application

import (
	"context"
	"crypto/sha256"
	"errors"

	exposuredomain "vdns.local/vdns/internal/exposure/domain"
	exposureports "vdns.local/vdns/internal/exposure/ports"
)

var ErrExposureAnalysis = errors.New("exposure analysis failed")

type Service struct {
	provider exposureports.Provider
}

func NewService(provider exposureports.Provider) *Service {
	if provider == nil {
		provider = exposureports.DisabledProvider{}
	}
	return &Service{provider: provider}
}

// Analyze is called only after an explicit incident-analysis user action.
// IncidentWitness is cleared before returning regardless of provider outcome.
func (service *Service) Analyze(
	ctx context.Context,
	snapshot exposuredomain.IncidentSnapshot,
	incidentWitness []byte,
) (exposureports.Result, error) {
	if service == nil || ctx == nil || snapshot.Validate() != nil ||
		len(incidentWitness) == 0 {
		clear(incidentWitness)
		return exposureports.Result{}, ErrExposureAnalysis
	}
	defer clear(incidentWitness)
	providerWitness := append([]byte(nil), incidentWitness...)
	defer clear(providerWitness)
	result, err := service.provider.Analyze(ctx, exposureports.Request{
		Snapshot: snapshot, IncidentWitness: providerWitness,
	})
	if err != nil {
		if errors.Is(err, exposureports.ErrOptionalFeatureUnavailable) {
			return exposureports.Result{}, exposureports.ErrOptionalFeatureUnavailable
		}
		return exposureports.Result{}, errors.Join(ErrExposureAnalysis, err)
	}
	if result.Affected.Validate(snapshot) != nil || len(result.ProofBytes) == 0 ||
		result.ProofDigest != sha256.Sum256(result.ProofBytes) ||
		(result.System != exposureports.ProofSystemScopeZK &&
			result.System != exposureports.ProofSystemGenericZKVM) {
		return exposureports.Result{}, ErrExposureAnalysis
	}
	return result, nil
}
