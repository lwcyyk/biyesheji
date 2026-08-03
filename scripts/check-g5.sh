#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
EVIDENCE_DIR=${G5_EVIDENCE_DIR:-"$PROJECT_ROOT/test-results/g5"}
mkdir -p "$EVIDENCE_DIR"
cd "$PROJECT_ROOT"

UNFORMATTED=$(gofmt -l cmd internal tests migrations)
if [ -n "$UNFORMATTED" ]; then
  echo "gofmt required:" >&2
  echo "$UNFORMATTED" >&2
  exit 1
fi

EXPECTED_MIGRATION_CHECKSUM=8d0f548d0dc65ab00f4b9e4a13b4cc80b64b09c4ffe0e7fb8527200c1d45e056
MIGRATION_INSERT_LINE=$(rg -n '^INSERT INTO schema_migrations' migrations/0006_g5_local_api.sql | cut -d: -f1)
ACTUAL_MIGRATION_CHECKSUM=$(head -n $((MIGRATION_INSERT_LINE - 1)) migrations/0006_g5_local_api.sql | sha256sum | cut -d' ' -f1)
if [ "$ACTUAL_MIGRATION_CHECKSUM" != "$EXPECTED_MIGRATION_CHECKSUM" ]; then
  echo "G5 migration checksum mismatch" >&2
  exit 1
fi

env -u GOPATH go vet ./...
env -u GOPATH go test ./...
env -u GOPATH go test -race ./... \
  -skip 'TestResolveL1L5P95At100KLeaves|TestDailyAutofillEndToEndP95'

(cd apps/browser-extension && npm test) >"$EVIDENCE_DIR/extension-tap.txt"
"$SCRIPT_DIR/check-g5-extension-secrets.sh"
"$SCRIPT_DIR/check-secrets.sh"
"$SCRIPT_DIR/check-spec-trace.sh"

sqlite3 -batch -bail :memory: \
  ".read migrations/0002_v2_initial.sql" \
  ".read migrations/0003_g2_core.sql" \
  ".read migrations/0004_g3_lifecycle_sync.sql" \
  ".read migrations/0005_g4_vdns_transparency.sql" \
  ".read migrations/0006_g5_local_api.sql" \
  ".read migrations/tests/0006_constraints.sql" \
  >"$EVIDENCE_DIR/migration-constraints.txt"

env -u GOPATH go test -json -count=1 \
  ./tests/contract \
  ./internal/adapters/inbound/httpapi \
  ./internal/adapters/inbound/nativemessaging \
  -run 'Contract|OpenAPI|Authentication|Idempotency|Nonce|StrictJSON|Native|LocalChannel|RateLimit' \
  >"$EVIDENCE_DIR/api-contract-security.json"

env -u GOPATH go test -json -count=1 \
  ./tests/e2e \
  ./internal/adapters/inbound/mocksiteweb \
  -run 'DailyMockSite|MockSiteRegistration' \
  >"$EVIDENCE_DIR/daily-mocksite-e2e.json"

env -u GOPATH go test -json -count=1 -v \
  ./tests/performance \
  -run '^TestDailyAutofillEndToEndP95$' \
  >"$EVIDENCE_DIR/autofill-p95.json"

env -u GOPATH go test ./tests/performance \
  -run '^$' -bench '^BenchmarkDailyAutofillAuthorization$' \
  -benchtime=1000x -count=1 \
  >"$EVIDENCE_DIR/autofill-benchmark.txt"

BUILD_DIR=$(mktemp -d)
env -u GOPATH go build -trimpath -o "$BUILD_DIR/vpass-local-client" ./cmd/vpass-local-client
test -x "$BUILD_DIR/vpass-local-client"

"$SCRIPT_DIR/demo-g5-daily.sh" >"$EVIDENCE_DIR/daily-demo.txt"

echo "g5-check-ok"
