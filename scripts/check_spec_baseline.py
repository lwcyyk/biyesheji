#!/usr/bin/env python3
"""Verify the immutable G0 specification baseline."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "specs/001-vdns-audit-rotation/BASELINE.json"


def normalized_bytes(path: Path, mode: str | None) -> bytes:
    data = path.read_bytes()
    if mode == "task-checkbox-status":
        text = data.decode("utf-8")
        text = re.sub(r"(?m)^- \[[ x]\] ", "- [ ] ", text)
        return text.encode("utf-8")
    if mode is not None:
        raise ValueError(f"unsupported normalization mode: {mode}")
    return data


def main() -> int:
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        print(f"baseline-error: cannot read manifest: {error}", file=sys.stderr)
        return 1

    normalizations = manifest.get("normalization", {})
    failures: list[str] = []
    for relative, expected in manifest.get("artifacts", {}).items():
        path = ROOT / relative
        if not path.is_file():
            failures.append(f"missing {relative}")
            continue
        try:
            content = normalized_bytes(path, normalizations.get(relative))
        except (OSError, UnicodeError, ValueError) as error:
            failures.append(f"cannot normalize {relative}: {error}")
            continue
        actual = hashlib.sha256(content).hexdigest()
        if actual != expected:
            failures.append(f"hash mismatch {relative}: {actual}")

    if failures:
        for failure in failures:
            print(f"baseline-error: {failure}", file=sys.stderr)
        return 1
    print(f"baseline-ok: {manifest['baselineId']} ({len(manifest['artifacts'])} artifacts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
