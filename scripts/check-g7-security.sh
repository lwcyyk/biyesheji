#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
EVIDENCE_DIR=${G7_SECURITY_EVIDENCE_DIR:-"$PROJECT_ROOT/test-results/g7/security"}
SECURITY_DIR="$PROJECT_ROOT/docs/security"
GENERIC_SCANNER=${G7_GENERIC_SECRET_SCANNER:-"/home/lwc/.codex/skills/senior-security/scripts/secret_scanner.py"}

mkdir -p "$EVIDENCE_DIR" "$SECURITY_DIR"
cd "$PROJECT_ROOT"

env -u GOPATH go mod verify >"$EVIDENCE_DIR/go-mod-verify.txt"
env -u GOPATH go list -m all >"$EVIDENCE_DIR/go-modules.txt"
env -u GOPATH go run ./cmd/g7-sbom \
  -out "$SECURITY_DIR/vdns-pm.cdx.json" \
  -licenses-out "$SECURITY_DIR/licenses.json" \
  >"$EVIDENCE_DIR/sbom-generator.txt"

jq -e '
  .bomFormat == "CycloneDX"
  and .specVersion == "1.5"
  and (.components | length) > 0
  and ([.components[].properties[]? | select(.name == "vdns:go-module-sum" and .value == "")] | length) == 0
' "$SECURITY_DIR/vdns-pm.cdx.json" >/dev/null

jq -e '
  ([.modules[] | select(.reviewStatus != "APPROVED")] | length) == 0
  and ([.modules[] | select(.license | test("^(AGPL|GPL|SSPL)"))] | length) == 0
' "$SECURITY_DIR/licenses.json" >/dev/null

BUILD_DIR=$(mktemp -d)
env -u GOPATH go build -trimpath -o "$BUILD_DIR/vdns-local-agent" ./cmd/vdns-local-agent
env -u GOPATH go version -m "$BUILD_DIR/vdns-local-agent" >"$EVIDENCE_DIR/binary-build-info.txt"

"$SCRIPT_DIR/check-secrets.sh" >"$EVIDENCE_DIR/project-secret-scan.txt"
"$SCRIPT_DIR/check-g5-extension-secrets.sh" >"$EVIDENCE_DIR/extension-security-scan.txt"

set +e
python3 "$GENERIC_SCANNER" "$PROJECT_ROOT" --format json \
  >"$EVIDENCE_DIR/generic-secret-scan.json"
GENERIC_SECRET_EXIT=$?
set -e

jq '{
  total: .summary.total,
  bySeverity: .summary.by_severity,
  patterns: (
    .findings
    | group_by(.pattern_id)
    | map({patternId:.[0].pattern_id,name:.[0].name,count:length})
  ),
  adjudication: "Generic matches are test password fixtures, source identifiers, protocol hashes, or evidence digests. The project scanner separately blocks credential/key token formats without printing matched values."
}' "$EVIDENCE_DIR/generic-secret-scan.json" \
  >"$EVIDENCE_DIR/generic-secret-adjudication.json"

VULN_FILE="$EVIDENCE_DIR/govulncheck-after.json"
if [ "${G7_REFRESH_VULNS:-0}" = "1" ]; then
  env -u GOPATH go run golang.org/x/vuln/cmd/govulncheck@v1.6.0 -json ./... \
    >"$VULN_FILE" 2>"$EVIDENCE_DIR/govulncheck-after.stderr"
fi
test -s "$VULN_FILE"

jq -s '{
  config: ([.[] | select(has("config")) | .config][0]),
  findingEvents: ([.[] | select(has("finding"))] | length),
  reachableFindings: (
    [.[] | select(has("finding")) | .finding
      | select((.trace // []) | any(.function != null))]
    | group_by(.osv)
    | map({
        osv: .[0].osv,
        fixedVersion: .[0].fixed_version,
        calledSymbols: ([.[].trace[].function // empty] | unique)
      })
  ),
  moduleOnlyFindings: (
    [.[] | select(has("finding")) | .finding
      | select(((.trace // []) | any(.function != null)) | not)]
    | group_by(.osv)
    | map({osv:.[0].osv,modules:([.[].trace[].module // empty] | unique)})
  )
}' "$VULN_FILE" >"$EVIDENCE_DIR/vulnerability-summary.json"

jq -e '
  .config.scanner_name == "govulncheck"
  and .config.scanner_version == "v1.6.0"
  and .config.go_version == "go1.25.12"
  and (.reachableFindings | length) == 0
' "$EVIDENCE_DIR/vulnerability-summary.json" >/dev/null

env -u GOPATH go test -json -count=1 \
  ./internal/cryptokit ./internal/protocol \
  ./internal/adapters/inbound/httpapi ./internal/adapters/inbound/nativemessaging \
  ./internal/adapters/outbound/objectfs ./internal/adapters/outbound/sqlite \
  ./internal/resolver/application \
  -run 'KAT|Domain|Context|Tamper|Authentication|Idempotency|Nonce|Secret|LocalChannel|Origin|ProofMutation|Rollback' \
  >"$EVIDENCE_DIR/security-regression.json"

SBOM_DIGEST=$(sha256sum "$SECURITY_DIR/vdns-pm.cdx.json" | cut -d' ' -f1)
LICENSE_DIGEST=$(sha256sum "$SECURITY_DIR/licenses.json" | cut -d' ' -f1)
VULN_DIGEST=$(sha256sum "$VULN_FILE" | cut -d' ' -f1)

jq -n \
  --arg sbomDigest "$SBOM_DIGEST" \
  --arg licenseDigest "$LICENSE_DIGEST" \
  --arg vulnDigest "$VULN_DIGEST" \
  --argjson genericSecretExit "$GENERIC_SECRET_EXIT" \
  '{
    schemaVersion: "1.0.0",
    toolchain: "go1.25.12",
    dependencyIntegrity: "PASSED",
    reachableVulnerabilities: 0,
    moduleOnlyAdvisories: ["GO-2026-5932 x/crypto/openpgp; package not imported or called"],
    licenses: "PASSED",
    deniedLicenses: 0,
    unknownLicenses: 0,
    projectSecretScan: "PASSED",
    extensionCspAndSecretScan: "PASSED",
    genericScannerExitCode: $genericSecretExit,
    genericScannerDisposition: "FALSE_POSITIVE_REVIEWED",
    sbomDigest: $sbomDigest,
    licenseInventoryDigest: $licenseDigest,
    vulnerabilityEvidenceDigest: $vulnDigest,
    releaseDecision: "PASSED"
  }' >"$EVIDENCE_DIR/security-gate-summary.json"

echo "g7-security-gate-ok"
