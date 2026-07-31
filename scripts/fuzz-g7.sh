#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
output_dir="${repo_root}/test-results/g7/fuzz"
mkdir -p "${output_dir}"

run_stage() {
  local stage="$1"
  shift
  (
    cd "${repo_root}"
    env -u GOPATH FUZZ_TIME="${G7_FUZZ_TIME:-1s}" G5_FUZZ_TIME="${G7_FUZZ_TIME:-1s}" "$@"
  ) >"${output_dir}/${stage}.txt" 2>&1
}

run_stage g1 ./scripts/fuzz-g1.sh
run_stage g2 ./scripts/fuzz-g2.sh
run_stage g3 ./scripts/fuzz-g3.sh
run_stage g4 ./scripts/fuzz-g4.sh
run_stage g5 ./scripts/fuzz-g5.sh
run_stage g6 ./scripts/fuzz-g6.sh

jq -n \
  --arg schemaVersion "1.0.0" \
  --arg result "PASSED" \
  --arg fuzzTime "${G7_FUZZ_TIME:-1s}" \
  '{
    schemaVersion: $schemaVersion,
    result: $result,
    perTargetFuzzTime: $fuzzTime,
    stages: ["G1", "G2", "G3", "G4", "G5", "G6"],
    note: "Fuzzing is time-bounded regression evidence, not exhaustive input-space proof."
  }' >"${output_dir}/fuzz-summary.json"

echo "g7-fuzz-ok"
