// Package application contains orchestration support for remediation.
package application

import (
	"crypto/sha256"
	"sync"

	"vpass.local/vpass/internal/protocol"
	remediationdomain "vpass.local/vpass/internal/remediation/domain"
)

type attemptKey struct {
	campaign protocol.CampaignID
	item     [sha256.Size]byte
}

// MemoryAttemptRegistry is the deterministic reference adapter used by tests
// and the local research runner. Production persists the same monotonic value
// in remediation_items_v2.
type MemoryAttemptRegistry struct {
	mu       sync.Mutex
	attempts map[attemptKey]uint64
}

func NewMemoryAttemptRegistry() *MemoryAttemptRegistry {
	return &MemoryAttemptRegistry{attempts: make(map[attemptKey]uint64)}
}

func (registry *MemoryAttemptRegistry) LastAttempt(
	campaignID protocol.CampaignID,
	itemID [sha256.Size]byte,
) uint64 {
	registry.mu.Lock()
	defer registry.mu.Unlock()
	return registry.attempts[attemptKey{campaign: campaignID, item: itemID}]
}

func (registry *MemoryAttemptRegistry) CommitAttempt(
	campaignID protocol.CampaignID,
	itemID [sha256.Size]byte,
	attempt uint64,
) error {
	registry.mu.Lock()
	defer registry.mu.Unlock()
	key := attemptKey{campaign: campaignID, item: itemID}
	if attempt == 0 || attempt <= registry.attempts[key] {
		return remediationdomain.ErrAttemptReplay
	}
	registry.attempts[key] = attempt
	return nil
}
