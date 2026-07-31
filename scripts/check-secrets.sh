#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
cd "$PROJECT_ROOT"

if ! command -v rg >/dev/null 2>&1; then
  echo "secret scan requires ripgrep (rg)" >&2
  exit 2
fi

# Print file names only. A failed build must never echo a discovered secret into
# CI logs. The scanner itself is excluded because it necessarily contains the
# detection expressions.
set +e
SECRET_HITS=$(rg -l --hidden \
  -g '!.git/**' \
  -g '!.tools/**' \
  -g '!docs/答辩/node_modules/**' \
  -g '!dist/**' \
  -g '!scripts/check-secrets.sh' \
  -e '-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----' \
  -e 'AKIA[0-9A-Z]{16}' \
  -e 'ASIA[0-9A-Z]{16}' \
  -e 'gh[pousr]_[A-Za-z0-9]{36,}' \
  -e 'github_pat_[A-Za-z0-9_]{50,}' \
  -e 'glpat-[A-Za-z0-9_-]{20,}' \
  -e 'sk-(?:proj-)?[A-Za-z0-9_-]{20,}' \
  -e 'xox[baprs]-[A-Za-z0-9-]{20,}' \
  -e 'AIza[0-9A-Za-z_-]{35}' \
  -e 'sk_live_[0-9A-Za-z]{16,}' \
  -e 'npm_[A-Za-z0-9]{30,}' \
  -e '(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis)://[^/@[:space:]]+:[^/@[:space:]]+@' \
  .)
SCAN_STATUS=$?
set -e

if [ "$SCAN_STATUS" -gt 1 ]; then
  echo "secret scan failed to inspect the workspace" >&2
  exit "$SCAN_STATUS"
fi
if [ -n "$SECRET_HITS" ]; then
  echo "potential committed secret detected in:" >&2
  echo "$SECRET_HITS" >&2
  exit 1
fi

set +e
SENSITIVE_FILES=$(rg --files --hidden \
  -g '!.git/**' \
  -g '!.tools/**' \
  -g '!docs/答辩/node_modules/**' \
  -g '!dist/**' |
  awk '
    /(^|\/)\.env$/ ||
    /(^|\/)id_(rsa|dsa|ecdsa|ed25519)$/ ||
    /\.(p12|pfx|jks|keystore)$/ ||
    /(^|\/)(private|secret)[^/]*\.(key|pem)$/ {
      print
    }
  ')
FILE_SCAN_STATUS=$?
set -e

if [ "$FILE_SCAN_STATUS" -ne 0 ]; then
  echo "secret filename scan failed" >&2
  exit "$FILE_SCAN_STATUS"
fi
if [ -n "$SENSITIVE_FILES" ]; then
  echo "sensitive key material filename detected:" >&2
  echo "$SENSITIVE_FILES" >&2
  exit 1
fi

echo "secret-scan-ok"
