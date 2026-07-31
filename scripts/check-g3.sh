#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
EVIDENCE_DIR=${G3_EVIDENCE_DIR:-"$PROJECT_ROOT/test-results/g3"}
mkdir -p "$EVIDENCE_DIR"
cd "$PROJECT_ROOT"

UNFORMATTED=$(gofmt -l internal tests)
if [ -n "$UNFORMATTED" ]; then
  echo "gofmt required:" >&2
  echo "$UNFORMATTED" >&2
  exit 1
fi

go vet ./...
go test ./...
go test -race ./...
"$SCRIPT_DIR/check-secrets.sh"
"$SCRIPT_DIR/check-spec-trace.sh"

sqlite3 -batch -bail :memory: \
  ".read migrations/0002_v2_initial.sql" \
  ".read migrations/0003_g2_core.sql" \
  ".read migrations/0004_g3_lifecycle_sync.sql" \
  ".read migrations/tests/0004_constraints.sql"

go test -json -count=1 \
  ./internal/sync/domain \
  ./internal/sync/application \
  ./internal/adapters/outbound/memorysync \
  >"$EVIDENCE_DIR/e3-sync-untrusted-cloud.json"

go test -json -count=1 \
  ./internal/credential/domain \
  ./internal/site/domain \
  ./internal/site/application \
  ./internal/adapters/outbound/mocksite \
  ./internal/adapters/outbound/sqlite \
  -run 'Aggregate|VersionCrash|VersionState|Coordinator|MockSite|SiteChangeRepository' \
  >"$EVIDENCE_DIR/e4-lifecycle-site-confirmation.json"

go test -json -count=1 \
  ./internal/device/domain \
  ./internal/device/application \
  ./internal/operation/domain \
  ./internal/cryptokit \
  -run 'Enrollment|Rollover|AuthorizeDeviceOperation|HPKERootBundle' \
  >"$EVIDENCE_DIR/e6-revocation-generation.json"

go test ./internal/sync/domain \
  -run '^$' -bench '^BenchmarkSyncManifestSignVerify100$' \
  -benchtime=20x -count=1 \
  >"$EVIDENCE_DIR/g3-benchmark.txt"

echo "g3-check-ok"
