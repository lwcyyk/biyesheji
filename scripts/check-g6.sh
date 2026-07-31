#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
EVIDENCE_DIR=${G6_EVIDENCE_DIR:-"$PROJECT_ROOT/test-results/g6"}
mkdir -p "$EVIDENCE_DIR"
cd "$PROJECT_ROOT"

UNFORMATTED=$(gofmt -l cmd internal tests migrations)
if [ -n "$UNFORMATTED" ]; then
  echo "gofmt required:" >&2
  echo "$UNFORMATTED" >&2
  exit 1
fi

EXPECTED_MIGRATION_CHECKSUM=bda97d75cd1717c7afa0f1172be04781f01ac0e327647d423883746db8cc67eb
MIGRATION_INSERT_LINE=$(rg -n '^INSERT INTO schema_migrations' migrations/0007_g6_privacy_response.sql | cut -d: -f1)
ACTUAL_MIGRATION_CHECKSUM=$(head -n $((MIGRATION_INSERT_LINE - 1)) migrations/0007_g6_privacy_response.sql | sha256sum | cut -d' ' -f1)
if [ "$ACTUAL_MIGRATION_CHECKSUM" != "$EXPECTED_MIGRATION_CHECKSUM" ]; then
  echo "G6 migration checksum mismatch" >&2
  exit 1
fi

env -u GOPATH go vet ./...
env -u GOPATH go test ./...
env -u GOPATH go test -race ./... \
  -skip 'TestResolveL1L5P95At100KLeaves|TestDailyAutofillEndToEndP95|TestAuditScan100KUnderFiveSeconds'

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
  ".read migrations/0007_g6_privacy_response.sql" \
  ".read migrations/tests/0007_constraints.sql" \
  >"$EVIDENCE_DIR/migration-constraints.txt"

env -u GOPATH go test -json -count=1 \
  ./internal/audit/domain ./internal/audit/application \
  ./internal/localapi/application \
  ./internal/adapters/inbound/nativemessaging \
  -run 'PrivateUseEvent|PublishUse|AuthorizedAnalysis|PublishAudit|SecurityAnalysis' \
  >"$EVIDENCE_DIR/e7-audit-security.json"

env -u GOPATH go test -json -count=1 -v \
  ./internal/audit/application \
  -run '^TestAuditScan100KUnderFiveSeconds$' \
  >"$EVIDENCE_DIR/e7-100k-scan.json"

env -u GOPATH go test -json -count=1 \
  ./internal/exposure/... ./internal/remediation/... \
  -run 'IncidentSnapshot|AffectedRoot|DisabledScopeZK|ConfiguredProvider|Planner|RotationRoot' \
  >"$EVIDENCE_DIR/e8-response-security.json"

env -u GOPATH go run ./cmd/g6-research-runner -out "$EVIDENCE_DIR" \
  >"$EVIDENCE_DIR/research-runner.txt"

python3 - "$EVIDENCE_DIR" <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
e7 = json.loads((root / "e7-privacy-overhead.json").read_text())
e8 = json.loads((root / "e8-optional-response.json").read_text())
assert e7["records"] == 100000
assert e7["targetMet"] is True
assert e7["stablePublicTagHits"] == 0
assert e7["crossEpochPublicLinkRate"] == 0
assert e8["changedSetEqualsCompleted"] is True
assert e8["outOfScopeAccepted"] is False
assert e8["replayAccepted"] is False
assert e8["unrelatedChangedBytes"] == 0
assert e8["optionalDailyPathCalls"] == 0
providers = {item["name"]: item for item in e8["providers"]}
assert providers["SCOPE_ZK"]["status"] == "UNAVAILABLE"
assert providers["SCOPE_ZK"]["reasonCode"] == "OPTIONAL_FEATURE_UNAVAILABLE"
PY

echo "g6-check-ok"
