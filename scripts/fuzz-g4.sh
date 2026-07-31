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

run_fuzz ./internal/transparency/domain FuzzVerifyInclusion
run_fuzz ./internal/transparency/domain FuzzParseProofBundle
run_fuzz ./internal/credential/domain FuzzParseStateDescriptor
run_fuzz ./internal/operation/domain FuzzParseAndVerifyDeviceOperationCredential

echo "g4-fuzz-ok"
