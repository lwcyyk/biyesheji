#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
venv="${repo_root}/.tools/docx-venv"

if [[ ! -x "${venv}/bin/python" ]]; then
  python3 -m venv "${venv}"
fi

if ! "${venv}/bin/python" -c 'import pypandoc, docx' >/dev/null 2>&1; then
  "${venv}/bin/python" -m pip install \
    --disable-pip-version-check \
    -r "${repo_root}/scripts/requirements-docx.txt"
fi

cd "${repo_root}"
"${venv}/bin/python" scripts/build_thesis_docx.py "$@"
