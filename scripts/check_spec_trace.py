#!/usr/bin/env python3
"""Fail when the frozen VPass requirements lose traceability.

This gate intentionally reads the human-owned Markdown sources instead of a
second generated manifest.  A missing or malformed ID therefore fails at the
same boundary reviewers use.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "specs/001-vdns-audit-rotation/spec.md"
TASKS = ROOT / "specs/001-vdns-audit-rotation/tasks.md"
REPORT = ROOT / "docs/VPass研究生毕业设计开发报告.md"


def fail(message: str) -> None:
    print(f"trace-error: {message}", file=sys.stderr)


def expand_ids(text: str, prefix: str) -> set[str]:
    """Expand PREFIX-001～003 and ordinary PREFIX-001 references."""

    result: set[str] = set()
    pattern = re.compile(
        rf"{re.escape(prefix)}-(\d{{3}})(?:[～~](?:{re.escape(prefix)}-)?(\d{{3}}))?"
    )
    for match in pattern.finditer(text):
        start = int(match.group(1))
        end = int(match.group(2) or match.group(1))
        if end < start:
            fail(f"reversed range {match.group(0)}")
            continue
        result.update(f"{prefix}-{number:03d}" for number in range(start, end + 1))
    return result


def table_ids(markdown: str, prefix_pattern: str) -> set[str]:
    return set(re.findall(rf"^\| ({prefix_pattern}) \|", markdown, flags=re.MULTILINE))


def require_contiguous(ids: set[str], prefix: str, first: int, last: int) -> list[str]:
    expected = {f"{prefix}-{number:03d}" for number in range(first, last + 1)}
    errors: list[str] = []
    missing = sorted(expected - ids)
    extra = sorted(ids - expected)
    if missing:
        errors.append(f"{prefix} missing: {', '.join(missing)}")
    if extra:
        errors.append(f"{prefix} outside frozen range: {', '.join(extra)}")
    return errors


def mapped_acceptance_ids(spec: str, requirement: str) -> set[str]:
    row = re.search(rf"^\| {re.escape(requirement)} \|.*$", spec, flags=re.MULTILINE)
    return expand_ids(row.group(0), "AC") if row else set()


def task_inventory(markdown: str) -> tuple[list[str], list[str]]:
    """Return the current P0-P3 task IDs and structural inventory errors.

    The Markdown headings are the source of truth.  This deliberately avoids a
    frozen task count: adding or removing a task is allowed when its priority
    section and per-priority sequence remain explicit and reviewable.
    """

    ids: list[str] = []
    errors: list[str] = []
    current_priority: str | None = None
    task_heading = re.compile(r"^###\s+(\S+)(?:\s|$)")
    valid_task = re.compile(r"^(P[0-3])-(\d{3})$")

    for line_number, line in enumerate(markdown.splitlines(), start=1):
        priority_match = re.match(r"^##\s+(P[0-3])(?:\s|$)", line)
        if priority_match:
            current_priority = priority_match.group(1)
            continue
        heading_match = task_heading.match(line)
        if not heading_match:
            continue
        token = heading_match.group(1)
        if not token.startswith("P"):
            continue
        match = valid_task.match(token)
        if not match:
            errors.append(f"unknown task ID {token!r} at tasks.md:{line_number}")
            continue
        task_id, priority = token, match.group(1)
        ids.append(task_id)
        if current_priority != priority:
            errors.append(
                f"{task_id} is under {current_priority or 'no priority section'}, "
                f"expected {priority}"
            )

    seen: set[str] = set()
    duplicates: set[str] = set()
    for task_id in ids:
        if task_id in seen:
            duplicates.add(task_id)
        seen.add(task_id)
    if duplicates:
        errors.append("duplicate task IDs: " + ", ".join(sorted(duplicates)))

    for priority in ("P0", "P1", "P2", "P3"):
        numbers = sorted(
            int(task_id.split("-")[1])
            for task_id in seen
            if task_id.startswith(priority + "-")
        )
        if not numbers:
            errors.append(f"{priority} has no tasks")
            continue
        expected = list(range(1, numbers[-1] + 1))
        missing = sorted(set(expected) - set(numbers))
        if missing:
            errors.append(
                f"{priority} missing task IDs: "
                + ", ".join(f"{priority}-{number:03d}" for number in missing)
            )

    return ids, errors


def main() -> int:
    errors: list[str] = []
    for path in (SPEC, TASKS, REPORT):
        if not path.is_file():
            errors.append(f"missing required artifact: {path.relative_to(ROOT)}")
    if errors:
        for error in errors:
            fail(error)
        return 1

    spec = SPEC.read_text(encoding="utf-8")
    tasks = TASKS.read_text(encoding="utf-8")
    report = REPORT.read_text(encoding="utf-8")

    spec_frs = table_ids(spec, r"FR-\d{3}")
    spec_acs = set(re.findall(r"^### (AC-\d{3})\b", spec, flags=re.MULTILINE))
    spec_nfrs = table_ids(spec, r"NFR-[A-Z]+-\d{3}")
    errors.extend(require_contiguous(spec_frs, "FR", 1, 43))
    errors.extend(require_contiguous(spec_acs, "AC", 1, 21))

    report_frs = expand_ids(report, "FR")
    report_acs = expand_ids(report, "AC")
    if spec_frs - report_frs:
        errors.append("report omits FR IDs: " + ", ".join(sorted(spec_frs - report_frs)))
    if spec_acs - report_acs:
        errors.append("report omits AC IDs: " + ", ".join(sorted(spec_acs - report_acs)))

    task_frs = expand_ids(tasks, "FR")
    task_acs = expand_ids(tasks, "AC")
    task_nfrs = set(re.findall(r"NFR-[A-Z]+-\d{3}", tasks))
    if spec_frs - task_frs:
        errors.append("requirements without task mapping: " + ", ".join(sorted(spec_frs - task_frs)))
    if spec_acs - task_acs:
        errors.append("acceptance scenarios without task/test plan: " + ", ".join(sorted(spec_acs - task_acs)))
    if spec_nfrs - task_nfrs and "全部 NFR" not in tasks:
        errors.append("NFRs without task mapping: " + ", ".join(sorted(spec_nfrs - task_nfrs)))

    for requirement in sorted(spec_frs | spec_nfrs):
        if not mapped_acceptance_ids(spec, requirement):
            errors.append(f"{requirement} has no acceptance mapping in spec")

    task_ids, task_errors = task_inventory(tasks)
    errors.extend(task_errors)

    forbidden = re.compile(r"\b(?:TODO|TBD|FIXME)\b", flags=re.IGNORECASE)
    for name, content in (("spec", spec), ("tasks", tasks), ("report", report)):
        if forbidden.search(content):
            errors.append(f"{name} contains an unresolved placeholder")

    if errors:
        for error in errors:
            fail(error)
        return 1

    print(
        "trace-ok: "
        f"{len(spec_frs)} FR, {len(spec_nfrs)} NFR, {len(spec_acs)} AC, "
        f"{len(task_ids)} tasks"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
