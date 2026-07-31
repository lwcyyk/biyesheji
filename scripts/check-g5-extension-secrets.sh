#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
EXTENSION_ROOT="$PROJECT_ROOT/apps/browser-extension"

if ! command -v rg >/dev/null 2>&1 || ! command -v jq >/dev/null 2>&1; then
  echo "extension security scan requires rg and jq" >&2
  exit 2
fi

MANIFEST="$EXTENSION_ROOT/manifest.json"
jq -e '
  .manifest_version == 3
  and (.permissions | sort) == (["activeTab","nativeMessaging","scripting"] | sort)
  and .host_permissions == ["http://127.0.0.1/*"]
  and (.content_security_policy.extension_pages | contains("script-src '\''self'\''"))
  and (.content_security_policy.extension_pages | contains("object-src '\''none'\''"))
  and (.content_scripts == null)
' "$MANIFEST" >/dev/null

set +e
UNSAFE_FILES=$(rg -l \
  -g '!**/tests/**' \
  -e '<script[^>]+src=["'"'"']https?://' \
  -e '\beval\s*\(' \
  -e 'new[[:space:]]+Function\s*\(' \
  -e '\b(localStorage|sessionStorage|chrome\.storage)\b' \
  -e '\bconsole\.(log|debug|info|warn|error)\s*\(' \
  -e '\.innerHTML[[:space:]]*=' \
  "$EXTENSION_ROOT")
SCAN_STATUS=$?
set -e

if [ "$SCAN_STATUS" -gt 1 ]; then
  echo "extension security scan failed" >&2
  exit "$SCAN_STATUS"
fi
if [ -n "$UNSAFE_FILES" ]; then
  echo "unsafe extension source detected in:" >&2
  echo "$UNSAFE_FILES" >&2
  exit 1
fi

if rg -q -g '!**/tests/**' 'https?://[^1]' "$EXTENSION_ROOT"/*.json "$EXTENSION_ROOT"/*/*.js 2>/dev/null; then
  echo "non-loopback remote URL detected in extension runtime files" >&2
  exit 1
fi

echo "g5-extension-secret-scan-ok"
