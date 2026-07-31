"""Regression tests for the dynamic Stage 2 task inventory."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "check_spec_trace.py"
SPEC = importlib.util.spec_from_file_location("check_spec_trace", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TaskInventoryTest(unittest.TestCase):
    def test_current_inventory_is_dynamic_and_valid(self) -> None:
        tasks = (SCRIPT.parents[1] / "specs/001-vdns-audit-rotation/tasks.md").read_text(
            encoding="utf-8"
        )
        task_ids, errors = MODULE.task_inventory(tasks)
        self.assertFalse(errors)
        self.assertGreater(len(task_ids), 0)
        self.assertNotIn("97", MODULE.task_inventory.__doc__ or "")

    def test_duplicate_is_rejected(self) -> None:
        markdown = self.valid_inventory() + "\n### P0-001 duplicate\n"
        _, errors = MODULE.task_inventory(markdown)
        self.assertTrue(any("duplicate task IDs" in error for error in errors))

    def test_missing_sequence_is_rejected(self) -> None:
        markdown = self.valid_inventory().replace("P0-002", "P0-003")
        _, errors = MODULE.task_inventory(markdown)
        self.assertTrue(any("P0-002" in error for error in errors))

    def test_unknown_or_misplaced_task_is_rejected(self) -> None:
        unknown = self.valid_inventory() + "\n### P9-001 unknown\n"
        _, unknown_errors = MODULE.task_inventory(unknown)
        self.assertTrue(any("unknown task ID" in error for error in unknown_errors))

        misplaced = self.valid_inventory().replace("### P1-001", "### P0-002")
        _, misplaced_errors = MODULE.task_inventory(misplaced)
        self.assertTrue(any("expected P0" in error for error in misplaced_errors))

    @staticmethod
    def valid_inventory() -> str:
        return "\n".join(
            (
                "## P0 protocol",
                "### P0-001 one",
                "### P0-002 two",
                "## P1 security",
                "### P1-001 one",
                "## P2 tests",
                "### P2-001 one",
                "## P3 engineering",
                "### P3-001 one",
            )
        )


if __name__ == "__main__":
    unittest.main()
