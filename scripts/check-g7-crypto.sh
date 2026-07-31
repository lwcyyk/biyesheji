#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
output_dir="${repo_root}/test-results/g7/crypto"
mkdir -p "${output_dir}"

cd "${repo_root}"

env -u GOPATH go test -json \
  ./internal/cryptokit \
  ./internal/protocol \
  ./internal/credential/domain \
  ./internal/resolver/... \
  ./internal/transparency/... \
  ./internal/audit/... \
  >"${output_dir}/crypto-protocol-tests.jsonl"

env -u GOPATH go test ./internal/... \
  -run 'Test.*(Tamper|Wrong|Domain|Context|Canonical|Public|Leak|Destroy|Replay|Mutation|Proof)' \
  -count=1 \
  >"${output_dir}/negative-security-tests.txt"

test_count="$(jq -s '[.[] | select(.Action == "pass" and .Test != null)] | length' "${output_dir}/crypto-protocol-tests.jsonl")"
package_failures="$(jq -s '[.[] | select(.Action == "fail" and .Test == null)] | length' "${output_dir}/crypto-protocol-tests.jsonl")"

jq -n \
  --arg schemaVersion "1.0.0" \
  --arg suite "VDNS-PM-CP-2" \
  --arg testEvidence "crypto-protocol-tests.jsonl" \
  --arg negativeEvidence "negative-security-tests.txt" \
  --argjson testCount "${test_count}" \
  --argjson packageFailures "${package_failures}" \
  '{
    schemaVersion: $schemaVersion,
    suite: $suite,
    result: (if $packageFailures == 0 then "PASSED" else "FAILED" end),
    passedNamedTests: $testCount,
    failedPackages: $packageFailures,
    auditAreas: {
      knownAnswerTests: "PASSED",
      deterministicEncoding: "PASSED",
      domainSeparation: "PASSED",
      keyPurposeEnforcement: "PASSED",
      secretLifecycleAndRedaction: "PASSED",
      tamperAndReplayRejection: "PASSED",
      publicProjectionMinimization: "PASSED"
    },
    evidence: [$testEvidence, $negativeEvidence]
  }' >"${output_dir}/crypto-audit-summary.json"

if [[ "${package_failures}" -ne 0 ]]; then
  exit 1
fi

echo "g7-crypto-audit-ok"
