// Package migrations embeds the append-only database migrations used by the
// production SQLite adapter. Keeping the executable SQL in one place avoids a
// second, silently diverging schema copy inside Go source.
package migrations

import _ "embed"

// LegacyInitialSQL is the immutable CP-1 schema. It is retained only so
// migration tooling can identify legacy databases; production code must not
// interpret its objects as CP-2.
//
//go:embed 0001_initial.sql
var LegacyInitialSQL string

// InitialSQL is the CP-2 schema for VPass installations. The embedded SQL
// retains frozen legacy wire identifiers for database compatibility.
//
//go:embed 0002_v2_initial.sql
var InitialSQL string

// G2CoreSQL adds daily-vault persistence without mutating the frozen CP-2
// new-install baseline.
//
//go:embed 0003_g2_core.sql
var G2CoreSQL string

// G3LifecycleSyncSQL adds crash-recoverable credential lifecycle,
// synchronization, enrollment, generation rollover and recovery state.
//
//go:embed 0004_g3_lifecycle_sync.sql
var G3LifecycleSyncSQL string

// G4VDNSTransparencySQL retains the published legacy migration identifier and
// embeds state decisions, proof bundles, checkpoints and monitor evidence.
//
//go:embed 0005_g4_vdns_transparency.sql
var G4VDNSTransparencySQL string

// G5LocalAPISQL adds hashed installation identity, restart-safe idempotency
// responses and durable local asynchronous operation status.
//
//go:embed 0006_g5_local_api.sql
var G5LocalAPISQL string

// G6PrivacyResponseSQL adds encrypted audit evidence, minimized security
// findings and optional incident/remediation commitments.
//
//go:embed 0007_g6_privacy_response.sql
var G6PrivacyResponseSQL string

// Stage2ProtocolClosureSQL adds the explicitly labelled research final-order
// adapter plus v2.1 evidence and revocation projections.
//
//go:embed 0008_stage2_protocol_closure.sql
var Stage2ProtocolClosureSQL string
