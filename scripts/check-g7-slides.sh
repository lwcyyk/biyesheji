#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
deck_dir="${repo_root}/docs/答辩"
result_dir="${repo_root}/test-results/g7/slides"
mkdir -p "${result_dir}"

(
  cd "${deck_dir}"
  node vpass-defense.js
) >"${result_dir}/generation.txt" 2>&1

if rg -n '❌|exceeds slide bounds|Found [1-9]' "${result_dir}/generation.txt"; then
  echo "slide geometry warning found" >&2
  exit 1
fi

deck="${deck_dir}/VPass答辩演示.pptx"
unzip -t "${deck}" >"${result_dir}/ooxml-integrity.txt"
slide_count="$(
  unzip -Z1 "${deck}" |
    awk '/^ppt\/slides\/slide[0-9]+\.xml$/ {count++} END {print count+0}'
)"
if [[ "${slide_count}" -ne 17 ]]; then
  echo "expected 17 slides, got ${slide_count}" >&2
  exit 1
fi

presentation_xml="$(unzip -p "${deck}" ppt/presentation.xml)"
if [[ "${presentation_xml}" != *'cx="12192000"'* || "${presentation_xml}" != *'cy="6858000"'* ]]; then
  echo "deck is not 16:9 wide layout" >&2
  exit 1
fi

render_status="NOT_AVAILABLE_NO_LIBREOFFICE"
validation_mode="PPTXGENJS_GEOMETRY_AND_OOXML_ONLY"
if command -v soffice >/dev/null 2>&1; then
  rendered_dir="${result_dir}/rendered"
  rm -rf "${rendered_dir}"
  python3 /home/lwc/.codex/skills/slides/scripts/render_slides.py \
    "${deck}" --output_dir "${rendered_dir}" \
    >"${result_dir}/render.txt" 2>&1
  python3 /home/lwc/.codex/skills/slides/scripts/slides_test.py \
    "${deck}" >"${result_dir}/overflow.txt" 2>&1
  render_status="PASSED"
  validation_mode="RENDERED_AND_GEOMETRY"
fi

deck_digest="$(sha256sum "${deck}" | awk '{print $1}')"
source_digest="$(sha256sum "${deck_dir}/vpass-defense.js" | awk '{print $1}')"
deck_bytes="$(stat -c '%s' "${deck}")"

jq -n \
  --arg schemaVersion "1.0.0" \
  --arg result "PASSED" \
  --arg validationMode "${validation_mode}" \
  --arg renderStatus "${render_status}" \
  --arg deck "docs/答辩/VPass答辩演示.pptx" \
  --arg source "docs/答辩/vpass-defense.js" \
  --arg deckSha256 "${deck_digest}" \
  --arg sourceSha256 "${source_digest}" \
  --argjson deckBytes "${deck_bytes}" \
  --argjson slideCount "${slide_count}" \
  '{
    schemaVersion: $schemaVersion,
    result: $result,
    validationMode: $validationMode,
    renderStatus: $renderStatus,
    limitation: (if $renderStatus == "PASSED" then null else "LibreOffice is not installed; visual raster review was not performed." end),
    deck: $deck,
    source: $source,
    slideCount: $slideCount,
    layout: "LAYOUT_WIDE_16_9",
    geometryWarnings: 0,
    deckBytes: $deckBytes,
    deckSha256: $deckSha256,
    sourceSha256: $sourceSha256
  }' >"${result_dir}/slides-validation.json"

echo "g7-slides-ok"
