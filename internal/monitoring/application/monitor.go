// Package application persists findings produced by pure monitor comparisons.
package application

import (
	"context"
	"errors"

	monitoringdomain "vdns.local/vdns/internal/monitoring/domain"
	"vdns.local/vdns/internal/monitoring/ports"
)

var ErrMonitorUnavailable = errors.New("monitor repository unavailable")

type Monitor struct {
	repository ports.EvidenceRepository
}

func New(repository ports.EvidenceRepository) (*Monitor, error) {
	if repository == nil {
		return nil, ErrMonitorUnavailable
	}
	return &Monitor{repository: repository}, nil
}

func (monitor *Monitor) Preserve(
	ctx context.Context,
	evidence *monitoringdomain.Evidence,
) error {
	if evidence == nil {
		return nil
	}
	if monitor == nil || monitor.repository == nil || ctx == nil {
		return ErrMonitorUnavailable
	}
	return monitor.repository.Save(ctx, *evidence)
}
