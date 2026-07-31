#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
cd "$PROJECT_ROOT"

FUZZ_TIME=${G5_FUZZ_TIME:-5s}

env -u GOPATH go test ./internal/adapters/inbound/httpapi \
  -run '^$' -fuzz '^FuzzStrictJSONDecoder$' -fuzztime="$FUZZ_TIME"

env -u GOPATH go test ./internal/adapters/inbound/nativemessaging \
  -run '^$' -fuzz '^FuzzNativeMessageDecoder$' -fuzztime="$FUZZ_TIME"

echo "g5-fuzz-ok"
