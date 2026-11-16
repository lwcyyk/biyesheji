import copy
import unittest
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch
from auth_lifecycle.b import search, reference, baselines, certificates, checker, fixtures, engine
from auth_lifecycle.b.model import prepare, ModelError


class BTests(unittest.TestCase):
    def test_named_cases(self):
        for name, model, expected, g in fixtures.cases():
            if name == "eight_task_boundary":continue  # separate bounded test below
            with self.subTest(name=name):
                b = search.solve(model); r = reference.solve(model); bb = baselines.solve(model)
                self.assertEqual(expected, b.status); self.assertEqual(expected, r.status)
                if expected == "FEASIBLE":
                    self.assertEqual(g, b.metrics["G"]); self.assertEqual(g, r.metrics["G"])
                    self.assertEqual(b.configuration, r.configuration)
                    self.assertEqual("ACCEPTED", checker.check_delivery(model, b.delivery)["verdict"])
                    self.assertEqual("ACCEPTED", checker.check_delivery(model, r.delivery)["verdict"])
                    for row in bb.candidates:
                        if row["verdict"] == "ACCEPTED":self.assertEqual("ACCEPTED", checker.check_delivery(model, row["delivery"])["verdict"])
                if expected == "IMPOSSIBLE":
                    cert = certificates.produce(model); self.assertEqual("IMPOSSIBLE", cert["status"])
                    self.assertEqual("ACCEPTED", checker.check_conflict(model, cert["certificate"])["verdict"])

    def test_negative_controls_equal(self):
        for m, label in [(fixtures.local_only(), "shared_broker"), (fixtures.static_groups(), "static_signatures")]:
            b = search.solve(m); bb = baselines.solve(m)
            self.assertEqual(b.metrics["G"], bb.metrics["G"])
            self.assertTrue(any(label in row["rules"] and row["verdict"] == "ACCEPTED" and row["metrics"]["G"] == b.metrics["G"] for row in bb.candidates))

    def test_G_ignores_token_strings(self):
        m = fixtures.aliases(); a = search.solve(m)
        for c in m["credentials"].values():c["token_labels"] = ["same"] * 1 + [f"extra{i}" for i in range(100)]
        b = search.solve(m)
        self.assertEqual(1, a.metrics["G"]); self.assertEqual(a.metrics, b.metrics)
        d = copy.deepcopy(a.delivery); d["plans"]["stop"] = ["revoke:account_root"]
        self.assertEqual("REJECTED", checker.check_delivery(m, d)["verdict"])
        audit = checker.audit_G(m, b.configuration)
        self.assertEqual(1, audit["G"]); self.assertFalse(audit["token_labels_used_for_counting"])
        r = m["revocations"].pop("account_root")
        for g in m["credentials"]:
            m["revocations"][g] = dict(copy.deepcopy(r), affects=[g])
        # Identical token labels do not merge independently registered effects.
        self.assertEqual(2, checker.audit_G(m, b.configuration)["G"])

    def test_alternative_path_cannot_be_ignored(self):
        m = fixtures.alternatives(); b = search.solve(m)
        self.assertIn("keep_a", b.configuration); self.assertIn("keep_b", b.configuration)
        m["scenarios"] = {"stop": {"local": [], "remote": ["keep"], "preserve": []}}
        d = copy.deepcopy(b.delivery); d["plans"] = {"stop": ["revoke:a"]}
        self.assertEqual("REJECTED", checker.check_delivery(m, d)["verdict"])
        d["plans"]["stop"].append("revoke:b")
        self.assertEqual("ACCEPTED", checker.check_delivery(m, d)["verdict"])

    def test_local_gate_is_not_remote_revocation(self):
        m = fixtures.aliases(); b = search.solve(m)
        m["scenarios"]["stop"] = {"local": [], "remote": ["a"], "preserve": ["b"]}
        self.assertEqual("REJECTED", checker.check_delivery(m, b.delivery)["verdict"])

    def test_setup_and_plan_tampering(self):
        m = fixtures.local_only(); b = search.solve(m)
        for edit in [lambda d: d["setup"].pop(), lambda d: d["plans"].clear(),
                     lambda d: d["configuration"].append(d["configuration"][0]),
                     lambda d: d["plans"]["stop"].append("invented:interface")]:
            d = copy.deepcopy(b.delivery); edit(d)
            self.assertEqual("REJECTED", checker.check_delivery(m, d)["verdict"])

    def test_independence_from_candidate(self):
        m = fixtures.local_only(); b = search.solve(m)
        bad = fixtures.aliases(); bad["scenarios"]["stop"] = {"local": [], "remote": ["a"], "preserve": ["b"]}
        cert = certificates.produce(bad)["certificate"]
        with patch.object(search, "solve", side_effect=AssertionError), patch.object(engine, "inspect", side_effect=AssertionError), patch.object(engine, "plan", side_effect=AssertionError), patch.object(engine, "resources", side_effect=AssertionError):
            self.assertEqual("FEASIBLE", reference.solve(m).status)
            self.assertEqual("ACCEPTED", checker.check_delivery(m, b.delivery)["verdict"])
            self.assertEqual("ACCEPTED", checker.check_conflict(bad, cert)["verdict"])

    def test_conflict_cover_tampering_and_scope(self):
        m = fixtures.aliases(); m["scenarios"]["stop"] = {"local": [], "remote": ["a"], "preserve": ["b"]}
        good = certificates.produce(m)["certificate"]
        for edit in [lambda c: c["rows"].pop(), lambda c: c["constraint_refs"].pop(),
                     lambda c: c["context"]["budgets"].update(approvals=False),
                     lambda c: c.update(scope="all_observation_strategies"),
                     lambda c: c["rows"][-1]["proof"]["actions"].clear()]:
            c = copy.deepcopy(good); edit(c)
            self.assertEqual("REJECTED", checker.check_conflict(m, c)["verdict"])
        c = certificates.produce(m, configuration=["a", "b"])["certificate"]
        self.assertEqual("fixed_configuration", checker.check_conflict(m, c)["scope"])

    def test_limits_never_imply_impossibility(self):
        m = fixtures.local_only()
        for f in [search.solve, reference.solve, baselines.solve]:self.assertEqual("INCONCLUSIVE", f(m, limit=0).status)
        self.assertEqual("INCONCLUSIVE", certificates.produce(m, limit=0)["status"])
        b = search.solve(m)
        self.assertEqual("INCONCLUSIVE", checker.check_delivery(m, b.delivery, limit=0)["verdict"])
        self.assertEqual("REJECTED", checker.check_delivery(m, b.delivery, limit=False)["verdict"])

    def test_schema_boundaries(self):
        for mutate in [lambda m: m.update(horizon=True), lambda m: m.update(horizon=9),
                       lambda m: m["budgets"].update(units=False), lambda m: m.update(tasks={})]:
            m = fixtures.local_only(); mutate(m)
            for f in [search.solve, reference.solve, baselines.solve]:self.assertEqual("UNKNOWN", f(m).status)

    def test_eight_tasks_and_eight_steps(self):
        m = fixtures.local_only(8)
        # Restrict to the shared catalog for an exact 8-task, H=8 boundary check.
        m["paths"] = {p: x for p, x in m["paths"].items() if p.endswith("_shared")}
        m["scenarios"]["stop"] = {"local": list(m["tasks"]), "remote": [], "preserve": []}
        b = search.solve(m); r = reference.solve(m)
        self.assertEqual("FEASIBLE", b.status); self.assertEqual(b.configuration, r.configuration)
        # Force exactly eight distinct local gates: no whole-root shortcut.
        m["approved"].remove("revoke")
        b = search.solve(m); r = reference.solve(m)
        self.assertEqual(8, b.metrics["max_stop_steps"])
        self.assertEqual("FEASIBLE", r.status)
        m["horizon"] = 7
        self.assertEqual("IMPOSSIBLE", search.solve(m).status)
        self.assertEqual("IMPOSSIBLE", reference.solve(m).status)

    def test_all_applicable_baseline_candidates_are_checked(self):
        m = fixtures.local_only(); b = baselines.solve(m)
        # Every task has 3 nonempty path subsets; one broker admits all 9.
        self.assertEqual(9, len(b.candidates))
        for row in b.candidates:
            self.assertIn("shared_broker", row["rules"])
            self.assertEqual("ACCEPTED", row["verdict"])
        m = fixtures.local_only(); m["scenarios"]["stop"] = {"local": [], "remote": ["t0"], "preserve": ["t1"]}
        b = baselines.solve(m)
        self.assertTrue(any("independent" in r["rules"] and r["verdict"] == "ACCEPTED" for r in b.candidates))

    def test_seeded_structural_models(self):
        for name, m in fixtures.structural_models():
            with self.subTest(name=name):
                b, r, bb = search.solve(m), reference.solve(m), baselines.solve(m)
                self.assertEqual(b.status, r.status); self.assertEqual(b.configuration, r.configuration)
                if b.status == "FEASIBLE":
                    self.assertEqual(b.metrics["G"], r.metrics["G"])
                    self.assertEqual("ACCEPTED", checker.check_delivery(m, r.delivery)["verdict"])
                if bb.status == "FEASIBLE":self.assertGreaterEqual(bb.metrics["G"], b.metrics["G"])

    def test_cli_roundtrip_and_unknown_audit(self):
        cli = Path(__file__).resolve().parents[1] / "scripts/b_cli.py"
        with tempfile.TemporaryDirectory() as tmp:
            model = Path(tmp) / "model.json"; artifact = Path(tmp) / "result.json"
            model.write_text(json.dumps(fixtures.local_only()), encoding="utf-8")
            solved = subprocess.run([sys.executable, str(cli), "solve", str(model), "--out", str(artifact)], capture_output=True, text=True)
            self.assertEqual(0, solved.returncode, solved.stderr)
            checked = subprocess.run([sys.executable, str(cli), "check", str(model), str(artifact)], capture_output=True, text=True)
            self.assertEqual("ACCEPTED", json.loads(checked.stdout)["verdict"])
            artifact.write_text(json.dumps({"status": "UNKNOWN", "configuration": None, "delivery": None}), encoding="utf-8")
            audited = subprocess.run([sys.executable, str(cli), "audit-g", str(model), str(artifact)], capture_output=True, text=True)
            self.assertEqual(0, audited.returncode, audited.stderr)
            self.assertEqual("UNKNOWN", json.loads(audited.stdout)["status"])

    def test_finite_matrix(self):
        for name, m in fixtures.finite_models():
            with self.subTest(name=name):
                b = search.solve(m); r = reference.solve(m); bb = baselines.solve(m)
                self.assertEqual(b.status, r.status)
                if b.status == "FEASIBLE":
                    self.assertEqual(b.configuration, r.configuration)
                    self.assertEqual(b.metrics["G"], r.metrics["G"])
                    self.assertEqual(b.metrics["G"], bb.metrics["G"])
                    self.assertEqual("ACCEPTED", checker.check_delivery(m, r.delivery)["verdict"])


if __name__ == "__main__":unittest.main()
