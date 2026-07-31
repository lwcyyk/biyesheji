// Package ports defines infrastructure boundaries for checkpoint publication.
package ports

import (
	"context"

	"vdns.local/vdns/internal/anchor/domain"
)

type AnnouncementProvider interface {
	Kind() domain.ProviderKind
	Announce(context.Context, domain.PublicAnnouncement) (domain.AnnouncementReceipt, error)
}
