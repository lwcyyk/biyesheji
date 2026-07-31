#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}"

env -u GOPATH go run ./cmd/g7-research-runner \
  -dataset experiments/g7/datasets.json \
  -out test-results/g7
env -u GOPATH go run ./cmd/g7-fault-runner \
  -out test-results/g7/faults
env -u GOPATH go run ./cmd/g7-ablation-runner \
  -out test-results/g7
./scripts/check-g7-crypto.sh
./scripts/drill-g7-recovery.sh
env -u GOPATH go run ./cmd/g7-evidence-manifest

echo "g7-experiments-ok"
