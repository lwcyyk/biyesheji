"""M5 development tests; OS integration is distinct from acceptance sampling."""
import importlib.util
import json
import os
from pathlib import Path
import secrets
import unittest

from auth_lifecycle.online_state.isolation_acceptance import IsolationLab, run_scene, scoped, source_lock

SCORER = Path(__file__).resolve().parents[1] / "scripts" / "score_agent_isolation.py"
spec = importlib.util.spec_from_file_location("independent_m5_rules", SCORER)
rules = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rules)


class IsolationContractTests(unittest.TestCase):
    def test_path_boundary(self):
        root = Path(__file__).resolve().parent
        self.assertEqual(scoped(root, root / "case"), root / "case")
        with self.assertRaises(ValueError): scoped(root, root.parent)

    def test_source_lock_includes_independent_checker(self):
        paths = {p["path"] for p in source_lock()["files"]}
        self.assertIn("scripts/score_agent_isolation.py", paths)
        self.assertIn("src/auth_lifecycle/online_state/windows_isolation.py", paths)


@unittest.skipUnless(os.name == "nt", "M5 uses Windows kernel access checks")
class IsolationOSDevelopmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parent = Path(os.environ.get("M5_TEST_ROOT", r"D:\毕业设计\mainline_agent_isolation_v1\dev_work"))
        parent.mkdir(parents=True, exist_ok=True)
        cls.root = parent / ("integration_" + secrets.token_hex(5))
        cls.env = IsolationLab(cls.root)
        cls.addClassCleanup(cls.env.close)
        cls.env.start()
        cls.rows = {}
        for i in range(1, 13):
            row = run_scene(cls.env, i)
            path = cls.root / (f"M5-{i:02d}.json")
            path.write_text(json.dumps(row))
            cls.rows[i] = row
            verdict = rules.score_scene(cls.root, path.name)
            (cls.root / (f"M5-{i:02d}.devscore.json")).write_text(json.dumps(verdict))
            if verdict["status"] == "FAIL_SECURITY":
                raise AssertionError(json.dumps([x for x in verdict["checks"] if not x["pass"]]))

    def test_all_twelve_development_paths_and_rules(self):
        for i in self.rows:
            with self.subTest(scene=i):
                result = rules.score_scene(self.root, f"M5-{i:02d}.json")
                self.assertEqual(result["status"], "PASS", [c for c in result["checks"] if not c["pass"]])

    def altered_score(self, number, mutate):
        row = json.loads(json.dumps(self.rows[number]))
        mutate(row)
        path = self.root / "deliberately_invalid.json"
        path.write_text(json.dumps(row))
        return rules.score_scene(self.root, path.name)

    def test_checker_rejects_forced_file_access_pass(self):
        def mutate(row): row["attacks"][0].update(allowed=True, winerror=0)
        self.assertEqual(self.altered_score(3, mutate)["status"], "FAIL_SECURITY")

    def test_checker_rejects_missing_target_as_denial(self):
        def mutate(row): row["attacks"][0].update(allowed=False, winerror=2)
        self.assertEqual(self.altered_score(3, mutate)["status"], "INCONCLUSIVE")

    def test_checker_rejects_management_call_not_reaching_service(self):
        def mutate(row): row["attacks"][0].update(reached=False)
        self.assertEqual(self.altered_score(6, mutate)["status"], "INCONCLUSIVE")

    def test_checker_rejects_secret_in_error(self):
        def mutate(row): row["parse"][0]["result"]["reason"] = self.env.markers["RT"]
        self.assertEqual(self.altered_score(9, mutate)["status"], "FAIL_SECURITY")

    def test_checker_requires_positive_control(self):
        def mutate(row): row["call"]["result"]["status"] = "REJECTED"
        self.assertEqual(self.altered_score(1, mutate)["status"], "INCONCLUSIVE")


if __name__ == "__main__": unittest.main()
