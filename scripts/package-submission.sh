#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
dist_dir="${repo_root}/dist"
evidence_dir="${repo_root}/test-results/g7/submission"
archive_name="vdns-pm-graduate-design-v2.0.0.tar.gz"
archive_path="${dist_dir}/${archive_name}"

cd "${repo_root}"

required_files=(
  "README.md"
  "go.mod"
  "go.sum"
  "docs/论文/VDNS-PM研究生毕业论文.md"
  "docs/论文/VDNS-PM研究生毕业论文.docx"
  "docs/答辩/VDNS-PM答辩演示.pptx"
  "docs/答辩/vdns-pm-defense.js"
  "test-results/g7/final-gate-summary.json"
  "test-results/g7/evidence-manifest.json"
)
for file in "${required_files[@]}"; do
  if [[ ! -f "${file}" ]]; then
    echo "missing submission artifact: ${file}" >&2
    exit 1
  fi
done

./scripts/check-spec-trace.sh >/dev/null
./scripts/check-secrets.sh >/dev/null
python3 scripts/check_thesis_docx.py \
  docs/论文/VDNS-PM研究生毕业论文.docx >/dev/null
unzip -t docs/答辩/VDNS-PM答辩演示.pptx >/dev/null
jq -e '.result == "PASSED"' test-results/g7/final-gate-summary.json >/dev/null
jq -e '.acceptancePassed == 21 and .acceptanceTotal == 21' \
  test-results/g7/evidence-manifest.json >/dev/null

staging_parent="$(mktemp -d)"
verification_parent="$(mktemp -d)"
trap 'rm -rf -- "${staging_parent}" "${verification_parent}"' EXIT
package_root="${staging_parent}/vdns-pm-graduate-design-v2.0.0"
mkdir -p "${package_root}" "${dist_dir}" "${evidence_dir}"

tar \
  --exclude='docs/答辩/node_modules' \
  --exclude='docs/答辩/node_modules/**' \
  --exclude='.tools' \
  --exclude='dist' \
  --exclude='test-results/g7/submission' \
  --exclude='test-results/g7/submission/**' \
  --exclude='*.db' \
  --exclude='*.db-shm' \
  --exclude='*.db-wal' \
  --exclude='*.pem' \
  --exclude='*.key' \
  --exclude='.env' \
  -cf - \
  .github .gitignore README.md go.mod go.sum \
  apps cmd docs experiments internal migrations scripts specs \
  test-results testdata tests |
  tar -xf - -C "${package_root}"

python3 scripts/build_submission_manifest.py --root "${package_root}"

tar \
  --sort=name \
  --mtime='UTC 1970-01-01' \
  --owner=0 \
  --group=0 \
  --numeric-owner \
  -C "${staging_parent}" \
  -cf - "$(basename "${package_root}")" |
  gzip -n >"${archive_path}"

archive_digest="$(sha256sum "${archive_path}" | awk '{print $1}')"
printf '%s  dist/%s\n' "${archive_digest}" "${archive_name}" >"${dist_dir}/SHA256SUMS"

tar -tzf "${archive_path}" >"${evidence_dir}/archive-files.txt"
if rg -n '(^|/)(node_modules|\\.tools|dist)(/|$)|\\.db(-shm|-wal)?$|\\.pem$|\\.key$|(^|/)\\.env$' \
  "${evidence_dir}/archive-files.txt"; then
  echo "submission archive contains forbidden path" >&2
  exit 1
fi

tar -xzf "${archive_path}" -C "${verification_parent}"
verified_root="${verification_parent}/$(basename "${package_root}")"
python3 scripts/build_submission_manifest.py \
  --root "${verified_root}" \
  --verify >"${evidence_dir}/manifest-verification.txt"

file_count="$(jq '.files | length' "${package_root}/SUBMISSION-MANIFEST.json")"
aggregate_digest="$(jq -r '.aggregateSha256' "${package_root}/SUBMISSION-MANIFEST.json")"
archive_bytes="$(stat -c '%s' "${archive_path}")"

jq -n \
  --arg schemaVersion "1.0.0" \
  --arg result "PASSED" \
  --arg archive "dist/${archive_name}" \
  --arg archiveSha256 "${archive_digest}" \
  --arg manifestAggregateSha256 "${aggregate_digest}" \
  --argjson archiveBytes "${archive_bytes}" \
  --argjson fileCount "${file_count}" \
  '{
    schemaVersion: $schemaVersion,
    result: $result,
    archive: $archive,
    archiveBytes: $archiveBytes,
    archiveSha256: $archiveSha256,
    fileCount: $fileCount,
    manifestAggregateSha256: $manifestAggregateSha256,
    forbiddenPaths: 0,
    containsRealUserData: false,
    verification: [
      "spec baseline and trace",
      "project secret scan",
      "thesis DOCX OOXML",
      "defense PPTX OOXML",
      "G7 final gate",
      "AC 21/21 evidence",
      "archive extraction and per-file SHA-256"
    ]
  }' >"${evidence_dir}/submission-summary.json"

echo "submission-package-ok archive=${archive_path}"
