#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
FUZZ_TIME=${FUZZ_TIME:-1s}
cd "$PROJECT_ROOT"

run_fuzz() {
  package=$1
  target=$2
  go test -run='^$' -fuzz="^${target}$" -fuzztime="$FUZZ_TIME" "$package"
}

run_fuzz ./internal/cryptokit FuzzParseAndOpenRouteCiphertext
run_fuzz ./internal/credential/domain FuzzParseCredentialEnvelope
run_fuzz ./internal/credential/domain FuzzParseStateDescriptor
run_fuzz ./internal/password/domain FuzzPasswordPolicyParse

echo "g2-fuzz-ok"
