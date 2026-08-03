// Package ports defines monitor evidence persistence boundaries.
package ports

import (
	"context"

	monitoringdomain "vpass.local/vpass/internal/monitoring/domain"
)

type EvidenceRepository interface {
	Save(context.Context, monitoringdomain.Evidence) error
}
