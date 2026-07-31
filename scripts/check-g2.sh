#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
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
  ".read migrations/tests/0003_constraints.sql"

go test ./internal/credential/application \
  -run '^$' -bench '^BenchmarkDailyVault(Read|Create)$' \
  -benchtime=1x -count=1

echo "g2-check-ok"
