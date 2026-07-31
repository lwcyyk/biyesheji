#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
python3 "$SCRIPT_DIR/check_spec_trace.py"
exec python3 "$SCRIPT_DIR/check_spec_baseline.py"
