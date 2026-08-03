#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}"

./scripts/build-thesis-docx.sh
python3 scripts/check_thesis_docx.py \
  docs/论文/VPass研究生毕业论文.docx

echo "thesis-docx-check-ok"
