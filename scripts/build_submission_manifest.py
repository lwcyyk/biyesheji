#!/usr/bin/env python3
"""Create or verify a deterministic SHA-256 submission manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", default="SUBMISSION-MANIFEST.json")
    parser.add_argument("--verify", action="store_true")
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect(root: Path, output: Path) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if path == output:
            continue
        if path.is_symlink():
            raise ValueError(f"submission contains symlink: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        entries.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return entries


def aggregate(entries: list[dict[str, object]]) -> str:
    digest = hashlib.sha256()
    for entry in entries:
        digest.update(
            (
                f"{entry['path']}\0{entry['bytes']}\0{entry['sha256']}\n"
            ).encode("utf-8")
        )
    return digest.hexdigest()


def create(root: Path, output: Path) -> None:
    entries = collect(root, output)
    result = {
        "schemaVersion": "1.0.0",
        "project": "VPass",
        "version": "2.1.0",
        "classification": "GRADUATE_DESIGN_SOURCE_DOCUMENTS_AND_TEST_EVIDENCE",
        "containsRealUserData": False,
        "files": entries,
        "aggregateSha256": aggregate(entries),
        "claimBoundary": (
            "Research prototype. Optional ZK providers, production consensus, "
            "browser compatibility matrix and school-specific formatting remain explicit."
        ),
    }
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"submission-manifest-ok files={len(entries)}")


def verify(root: Path, output: Path) -> None:
    expected = json.loads(output.read_text(encoding="utf-8"))
    actual_entries = collect(root, output)
    if actual_entries != expected.get("files"):
        raise SystemExit("submission manifest file list or digest mismatch")
    actual_aggregate = aggregate(actual_entries)
    if actual_aggregate != expected.get("aggregateSha256"):
        raise SystemExit("submission manifest aggregate digest mismatch")
    print(f"submission-manifest-verify-ok files={len(actual_entries)}")


def main() -> None:
    args = parse_args()
    root = Path(args.root).resolve()
    output = (root / args.output).resolve()
    if args.verify:
        verify(root, output)
    else:
        create(root, output)


if __name__ == "__main__":
    main()
