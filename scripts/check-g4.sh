#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
EVIDENCE_DIR=${G4_EVIDENCE_DIR:-"$PROJECT_ROOT/test-results/g4"}
mkdir -p "$EVIDENCE_DIR"
cd "$PROJECT_ROOT"

UNFORMATTED=$(gofmt -l internal tests)
if [ -n "$UNFORMATTED" ]; then
  echo "gofmt required:" >&2
  echo "$UNFORMATTED" >&2
  exit 1
fi

env -u GOPATH go vet ./...
env -u GOPATH go test ./...
env -u GOPATH go test -race ./...
"$SCRIPT_DIR/check-secrets.sh"
"$SCRIPT_DIR/check-spec-trace.sh"

sqlite3 -batch -bail :memory: \
  ".read migrations/0002_v2_initial.sql" \
  ".read migrations/0003_g2_core.sql" \
  ".read migrations/0004_g3_lifecycle_sync.sql" \
  ".read migrations/0005_g4_vdns_transparency.sql" \
  ".read migrations/tests/0005_constraints.sql"

env -u GOPATH go test -json -count=1 \
  ./internal/resolver/application \
  -run 'L1L2L3|L4ProofBundle|ResolverSelects|ResolveL1L5|LifecycleEdge|EventVersion' \
  >"$EVIDENCE_DIR/e5-l1-l5-mutation-matrix.json"

env -u GOPATH go test -json -count=1 \
  ./internal/transparency/domain \
  ./internal/transparency/application \
  -run 'MerkleKAT|ConsistencyProof|ProofMutation|SignedTreeHead|ProofBundle|LogAppend' \
  >"$EVIDENCE_DIR/e5-transparency-proofs.json"

env -u GOPATH go test -json -count=1 \
  ./internal/monitoring/domain \
  ./internal/anchor/application \
  ./internal/adapters/outbound/anvilanchor \
  -run 'Monitor|Publisher|AnvilProvider' \
  >"$EVIDENCE_DIR/e5-monitor-anchor.json"

env -u GOPATH go test ./internal/resolver/application \
  -run '^$' -bench '^BenchmarkResolveL1L5At100KLeaves$' \
  -benchtime=20x -count=1 \
  >"$EVIDENCE_DIR/e5-vdns-100k-benchmark.txt"

echo "g4-check-ok"
