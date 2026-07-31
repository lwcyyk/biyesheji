#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
FUZZ_TIME=${FUZZ_TIME:-1s}
cd "$PROJECT_ROOT"

run_fuzz() {
  package=$1
  target=$2
  env -u GOPATH go test -run='^$' -fuzz="^${target}$" -fuzztime="$FUZZ_TIME" "$package"
}

run_fuzz ./internal/audit/domain FuzzParsePrivateUseEvent
run_fuzz ./internal/exposure/domain FuzzIncidentSnapshotWindow
run_fuzz ./internal/cryptokit FuzzEncodeExact
run_fuzz ./internal/adapters/inbound/nativemessaging FuzzNativeMessageDecoder

echo "g6-fuzz-ok"
