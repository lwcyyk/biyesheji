#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

usage() {
  echo "usage: $0 [--data-dir EMPTY_DIRECTORY]" >&2
  exit 2
}

DATA_DIR=
while [ "$#" -gt 0 ]; do
  case "$1" in
    --data-dir)
      [ "$#" -ge 2 ] || usage
      DATA_DIR=$2
      shift 2
      ;;
    *)
      usage
      ;;
  esac
done

if [ -z "$DATA_DIR" ]; then
  DATA_DIR=$(mktemp -d)
fi

case "$DATA_DIR" in
  /|"$PROJECT_ROOT"|"$PROJECT_ROOT/"|"$HOME"|"$HOME/")
    echo "refusing unsafe demo data directory" >&2
    exit 2
    ;;
esac

if [ -e "$DATA_DIR" ]; then
  [ -d "$DATA_DIR" ] || {
    echo "demo target is not a directory" >&2
    exit 2
  }
  if [ -n "$(find "$DATA_DIR" -mindepth 1 -maxdepth 1 -print -quit)" ]; then
    echo "demo data directory must be empty" >&2
    exit 2
  fi
else
  mkdir -p "$DATA_DIR"
fi

EVIDENCE_DIR="$DATA_DIR/evidence"
mkdir -p "$EVIDENCE_DIR"
cd "$PROJECT_ROOT"

sqlite3 -batch -bail "$DATA_DIR/vdns-demo.db" \
  ".read migrations/0002_v2_initial.sql" \
  ".read migrations/0003_g2_core.sql" \
  ".read migrations/0004_g3_lifecycle_sync.sql" \
  ".read migrations/0005_g4_vdns_transparency.sql" \
  ".read migrations/0006_g5_local_api.sql" \
  ".read migrations/0007_g6_privacy_response.sql" \
  ".read migrations/tests/0007_constraints.sql" \
  >"$EVIDENCE_DIR/01-initialize.txt"

env -u GOPATH go test -json -count=1 ./tests/e2e \
  -run '^TestDailyMockSiteRegisterLoginChangeSyncRevokeAndOffline$' \
  >"$EVIDENCE_DIR/02-daily-password-lifecycle.json"

env -u GOPATH go test -json -count=1 ./internal/resolver/application \
  -run 'TestResolverSelectsVDNSCurrentState|TestResolveL1L5P95At100KLeaves' \
  >"$EVIDENCE_DIR/03-vdns-resolution.json"

env -u GOPATH go test -json -count=1 \
  ./internal/audit/application ./internal/localapi/application \
  -run 'TestAuthorizedAnalysis|TestAgentSecurityAnalysis' \
  >"$EVIDENCE_DIR/04-private-audit.json"

env -u GOPATH go test -json -count=1 \
  ./internal/exposure/application ./internal/remediation/domain \
  -run 'TestDisabledScopeZK|TestRotationRoot' \
  >"$EVIDENCE_DIR/05-optional-response.json"

env -u GOPATH go run ./cmd/g6-research-runner -out "$EVIDENCE_DIR" \
  >"$EVIDENCE_DIR/06-g6-research-runner.txt"

env -u GOPATH go run ./cmd/g7-fault-runner -out "$EVIDENCE_DIR/faults" \
  >"$EVIDENCE_DIR/07-fault-runner.txt"

DATABASE_DIGEST=$(sha256sum "$DATA_DIR/vdns-demo.db" | cut -d' ' -f1)
DAILY_DIGEST=$(sha256sum "$EVIDENCE_DIR/02-daily-password-lifecycle.json" | cut -d' ' -f1)
VDNS_DIGEST=$(sha256sum "$EVIDENCE_DIR/03-vdns-resolution.json" | cut -d' ' -f1)
AUDIT_DIGEST=$(sha256sum "$EVIDENCE_DIR/04-private-audit.json" | cut -d' ' -f1)
OPTIONAL_DIGEST=$(sha256sum "$EVIDENCE_DIR/e8-optional-response.json" | cut -d' ' -f1)
FAULT_DIGEST=$(sha256sum "$EVIDENCE_DIR/faults/fault-injection.json" | cut -d' ' -f1)

jq -n \
  --arg databaseDigest "$DATABASE_DIGEST" \
  --arg dailyDigest "$DAILY_DIGEST" \
  --arg vdnsDigest "$VDNS_DIGEST" \
  --arg auditDigest "$AUDIT_DIGEST" \
  --arg optionalDigest "$OPTIONAL_DIGEST" \
  --arg faultDigest "$FAULT_DIGEST" \
  '{
    schemaVersion: "1.0.0",
    product: "VDNS-PM",
    protocol: "VDNS-PM/2",
    suite: "VDNS-PM-CP-2",
    dataClassification: "TEST_ONLY",
    containsRealUserData: false,
    steps: [
      {id:"INITIALIZE",status:"COMPLETED",digest:$databaseDigest},
      {id:"CREATE_AUTOFILL_SYNC_UPDATE_REVOKE_OFFLINE",status:"COMPLETED",digest:$dailyDigest},
      {id:"VDNS_L1_L5",status:"COMPLETED",digest:$vdnsDigest},
      {id:"PRIVATE_AUDIT",status:"COMPLETED",digest:$auditDigest},
      {id:"OPTIONAL_RESPONSE",status:"COMPLETED_WITH_PROVIDERS_UNAVAILABLE",digest:$optionalDigest},
      {id:"FAULT_INJECTION",status:"COMPLETED",digest:$faultDigest}
    ],
    dailyPathWaitsForChainVrfOrScopeZk: false,
    scopeZkStatus: "UNAVAILABLE",
    genericZkvmStatus: "UNAVAILABLE",
    claimBoundary: "研究原型演示；Mock Site/模拟日志/本地适配器不代表生产共识或全部网站。"
  }' >"$EVIDENCE_DIR/demo-summary.json"

{
  echo "step,status"
  echo "INITIALIZE,COMPLETED"
  echo "CREATE_AUTOFILL_SYNC_UPDATE_REVOKE_OFFLINE,COMPLETED"
  echo "VDNS_L1_L5,COMPLETED"
  echo "PRIVATE_AUDIT,COMPLETED"
  echo "OPTIONAL_RESPONSE,COMPLETED_WITH_PROVIDERS_UNAVAILABLE"
  echo "FAULT_INJECTION,COMPLETED"
} >"$EVIDENCE_DIR/demo-steps.csv"

echo "vdns-pm-demo-ok data=$DATA_DIR"
