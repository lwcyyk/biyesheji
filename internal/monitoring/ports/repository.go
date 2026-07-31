// Package ports defines monitor evidence persistence boundaries.
package ports

import (
	"context"

	monitoringdomain "vdns.local/vdns/internal/monitoring/domain"
)

type EvidenceRepository interface {
	Save(context.Context, monitoringdomain.Evidence) error
}
