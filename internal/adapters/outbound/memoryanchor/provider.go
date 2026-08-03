// Package memoryanchor implements the explicitly labeled in-process
// announcement simulator used by deterministic tests and demos.
package memoryanchor

import (
	"context"
	"encoding/hex"
	"errors"
	"sync"

	anchordomain "vpass.local/vpass/internal/anchor/domain"
)

var ErrConflictingCheckpoint = errors.New("conflicting simulated checkpoint")

type Provider struct {
	mu       sync.Mutex
	byHeight map[uint64]anchordomain.PublicAnnouncement
}

func New() *Provider {
	return &Provider{byHeight: make(map[uint64]anchordomain.PublicAnnouncement)}
}

func (*Provider) Kind() anchordomain.ProviderKind {
	return anchordomain.ProviderSimulated
}

func (provider *Provider) Announce(
	ctx context.Context,
	announcement anchordomain.PublicAnnouncement,
) (anchordomain.AnnouncementReceipt, error) {
	if provider == nil || ctx == nil || ctx.Err() != nil ||
		announcement.Validate() != nil ||
		announcement.Payload.ProviderKind != anchordomain.ProviderSimulated {
		return anchordomain.AnnouncementReceipt{}, anchordomain.ErrInvalidAnnouncement
	}
	provider.mu.Lock()
	defer provider.mu.Unlock()
	height := announcement.Payload.CheckpointHeight
	if previous, ok := provider.byHeight[height]; ok &&
		previous.CheckpointDigest != announcement.CheckpointDigest {
		return anchordomain.AnnouncementReceipt{}, ErrConflictingCheckpoint
	}
	cloned := announcement
	cloned.CheckpointObject = append([]byte(nil), announcement.CheckpointObject...)
	provider.byHeight[height] = cloned
	return anchordomain.AnnouncementReceipt{
		ProviderKind:      anchordomain.ProviderSimulated,
		CheckpointDigest:  announcement.CheckpointDigest,
		ExternalReference: "simulated:" + hex.EncodeToString(announcement.CheckpointDigest[:8]),
		ObservedHeight:    height,
	}, nil
}

func (provider *Provider) Count() int {
	if provider == nil {
		return 0
	}
	provider.mu.Lock()
	defer provider.mu.Unlock()
	return len(provider.byHeight)
}
