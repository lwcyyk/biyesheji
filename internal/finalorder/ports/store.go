package ports

import (
	"context"

	finalorderdomain "vpass.local/vpass/internal/finalorder/domain"
)

// SnapshotStore persists the complete public state of the research adapter.
// CompareAndSwap prevents two local authority instances from losing updates.
type SnapshotStore interface {
	Load(context.Context) (finalorderdomain.PersistentState, error)
	CompareAndSwap(
		context.Context,
		uint64,
		finalorderdomain.PersistentState,
	) error
}
