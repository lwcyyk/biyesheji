import copy
import unittest
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch
from auth_lifecycle.a import compiler, fixtures, candidate, joint_reference, audit, runtime, evidence, plant
from auth_lifecycle.a import ablations
from auth_lifecycle.a.bridge import Feedback
from auth_lifecycle.schema import State, prepare, canonical
from auth_lifecycle.reference import solve as old_reference
from auth_lifecycle.checker import check_policy


class AcquisitionTests(unittest.TestCase):
    def compiled(self, source):
        c = compiler.compile_model(source)
        self.assertEqual("COMPILED", c.status, c.reason)
        return c.bundle

    def test_named_cases_and_independent_reference(self):
        for name, source, expected in fixtures.cases():
            with self.subTest(case=name):
                bundle = self.compiled(source)
                self.assertEqual("ACCEPTED", audit.check_compilation(bundle)["verdict"])
                ref = joint_reference.solve(bundle)
                self.assertEqual(expected, ref.status)
                self.assertEqual(ref.status, old_reference(bundle["l0"]).status.value)
                for method, feedback in [("A1", False), ("A1", True), ("B-A", False)]:
                    result = candidate.solve(bundle, method=method, feedback=feedback)
                    self.assertEqual(ref.status, result.status)
                    if result.status == "FEASIBLE":
                        self.assertGreaterEqual(result.worst_requests, ref.worst_requests)
                        measured = runtime.evaluate(bundle, result)
                        self.assertEqual(1, measured["completion"], measured.get("safety_counterexamples"))
                        self.assertEqual(result.worst_requests, measured["external_requests"])

    def test_feedback_is_only_pair_switch(self):
        bundle = self.compiled(fixtures.acquisition(nuisance=2))
        with patch.object(Feedback, "get", side_effect=AssertionError("feedback prohibited")):
            off = candidate.solve(bundle, feedback=False)
            baseline = candidate.solve(bundle, method="B-A")
        on = candidate.solve(bundle, feedback=True)
        self.assertEqual(off.status, on.status)
        self.assertEqual("probe:z_native", on.policy["action"])
        self.assertEqual("probe:z_native", off.policy["action"])
        self.assertEqual("probe:z_native", baseline.policy["action"])
        self.assertTrue(on.diagnostics[0]["feedback"]["semantic_disagreements"])
        self.assertEqual(0, off.stats["feedback_calls"])

    def test_B_feedback_certificates_are_checked(self):
        bundle = self.compiled(fixtures.acquisition()); state = prepare(bundle["l0"])[1]
        message = Feedback(bundle).get(state)
        self.assertEqual("COMPLETE", message["status"])
        proofs = [x for rows in message["rows"].values() for x in rows if "certificate" in x]
        self.assertTrue(proofs)
        self.assertTrue(all(x["check"]["verdict"] == "ACCEPTED" and x["certificate"]["scope"] == "fixed_configuration" for x in proofs))

    def test_direct_feedback_fences_empty_and_unknown(self):
        bundle = self.compiled(fixtures.acquisition()); valid = prepare(bundle["l0"])[1]
        for state in [State(frozenset(), 3), State(valid.knowledge, 3, "out_of_model"), State(valid.knowledge, True)]:
            report = Feedback(bundle).get(state)
            self.assertEqual("UNKNOWN", report["status"])
            self.assertEqual([], report["pairs"])

    def test_no_observation_hidden_world_selection(self):
        source = fixtures.acquisition()
        for w in source["worlds"]:source["probes"]["z_native"]["outcomes"][w][0][0]["observation"] = "same"
        bundle = self.compiled(source)
        self.assertEqual("IMPOSSIBLE", joint_reference.solve(bundle).status)
        self.assertEqual("IMPOSSIBLE", candidate.solve(bundle, feedback=True).status)

    def test_nonempty_union_and_unknown_fence(self):
        source = next(s for n, s, _ in fixtures.cases() if n == "lost_probe_unknown_handle")
        bundle = self.compiled(source); state = prepare(bundle["l0"])[1]
        after = evidence.update(bundle, state, "probe:z_native", "LOST")
        self.assertEqual(4, len(after.knowledge)); self.assertEqual(state.remaining - 1, after.remaining)
        unexpected = evidence.update(bundle, state, "probe:z_native", "unregistered-provider-v3")
        self.assertTrue(unexpected.knowledge); self.assertEqual("out_of_model_observation", unexpected.boundary)
        self.assertEqual("UNKNOWN", evidence.contract(bundle, unexpected)["status"])
        self.assertEqual(unexpected, evidence.update(bundle, unexpected, "probe:z_native", "m0"))

    def test_evidence_scope_and_invalidation(self):
        bundle = self.compiled(fixtures.acquisition()); before = prepare(bundle["l0"])[1]
        first = evidence.contract(bundle, before)
        self.assertNotIn("/revocations/x/coverage", first["claims"])
        after = evidence.update(bundle, before, "probe:z_native", "m0")
        proven = evidence.contract(bundle, after)
        self.assertEqual("all_material", proven["claims"]["/revocations/x/coverage"])
        self.assertFalse(evidence.usable(first, bundle, after)); self.assertTrue(evidence.usable(proven, bundle, after))
        changed = copy.deepcopy(bundle); changed["source"]["caller"] = "other"
        self.assertFalse(evidence.usable(proven, changed, after))

    def test_independent_compiler_and_reference(self):
        bundle = self.compiled(fixtures.side_effect())
        with patch.object(plant, "step", side_effect=AssertionError), patch.object(plant, "flags", side_effect=AssertionError), patch.object(candidate, "solve", side_effect=AssertionError):
            self.assertEqual("ACCEPTED", audit.check_compilation(bundle)["verdict"])
            ref = joint_reference.solve(bundle)
            self.assertEqual(1, runtime.evaluate(bundle, ref)["completion"])

    def test_omitted_physical_outcome_rejected(self):
        source = next(s for n, s, _ in fixtures.cases() if n == "lost_probe_unknown_handle")
        bundle = self.compiled(source); w, sid = bundle["l0"]["initial"][0]
        bundle["l0"]["worlds"][w]["states"][sid]["transitions"]["probe:z_native"].pop()
        self.assertEqual("REJECTED", audit.check_compilation(bundle)["verdict"])

    def test_lost_stop_idempotent_retry(self):
        source = next(s for n, s, _ in fixtures.cases() if n == "lost_stop_ambiguous_effect")
        bundle = self.compiled(source); result = candidate.solve(bundle)
        measured = runtime.evaluate(bundle, result)
        self.assertEqual(1, measured["completion"])
        self.assertTrue(any(sum(e.get("action", "").startswith("stop:") for e in t["history"]) == 2 for t in measured["traces"]))

    def test_partial_policy_and_omitted_observation_rejected(self):
        bundle = self.compiled(fixtures.acquisition()); result = candidate.solve(bundle)
        proof = copy.deepcopy(result.policy); proof["children"].pop(next(iter(proof["children"])))
        self.assertEqual("REJECTED", check_policy(bundle["l0"], proof).verdict)

    def test_limits_do_not_prove_infeasibility(self):
        source = fixtures.acquisition()
        self.assertEqual("INCONCLUSIVE", compiler.compile_model(source, node_limit=0).status)
        bundle = self.compiled(source)
        self.assertEqual("INCONCLUSIVE", candidate.solve(bundle, node_limit=0).status)
        self.assertEqual("INCONCLUSIVE", joint_reference.solve(bundle, node_limit=0).status)
        self.assertEqual("INCONCLUSIVE", runtime.evaluate(bundle, candidate.solve(bundle), trace_limit=0)["status"])

    def test_bad_schema_and_unsafe_handle_access(self):
        for mutate in [lambda s: s.update(horizon=True), lambda s: s.update(horizon=9),
                       lambda s: s["budget"].update(requests=99),
                       lambda s: s["cleanups"]["sessions"].update(mode="known_handle")]:
            source = fixtures.side_effect(opaque=True); mutate(source)
            self.assertEqual("UNKNOWN", compiler.compile_model(source).status)

    def test_joint_reference_can_be_cheaper(self):
        source = next(s for n, s, _ in fixtures.cases() if n == "joint_planning_cheaper_than_early_configure")
        bundle = self.compiled(source); a = candidate.solve(bundle, feedback=True); r = joint_reference.solve(bundle)
        self.assertLess(r.worst_requests, a.worst_requests)

    def test_negative_control_needs_no_queries(self):
        source = next(s for n, s, _ in fixtures.cases() if n == "local_only_no_learning_negative_control")
        bundle = self.compiled(source)
        for method, fb in [("A1", False), ("A1", True), ("B-A", False)]:
            r = candidate.solve(bundle, method=method, feedback=fb)
            self.assertTrue(r.policy["action"].startswith("configure:"))
            self.assertEqual(0, r.stats["feedback_calls"])

    def test_unsafe_ablation_is_rejected_and_scored(self):
        bundle = self.compiled(fixtures.side_effect(opaque=True, clean=False))
        for enabled in [False, True]:
            result = ablations.missing_obligation_abstraction(bundle, feedback=enabled)
            self.assertEqual("REJECTED", result["audit"]["verdict"])
            self.assertEqual("FEASIBLE", result["controller_result"].status)
            self.assertEqual(0, result["scorer"]["completion"])
            self.assertGreater(result["scorer"]["unresolved_obligations"], 0)
            self.assertTrue(result["scorer"]["safety_counterexamples"])

    def test_no_acquisition_coupling_ablation(self):
        bundle = self.compiled(fixtures.acquisition())
        self.assertEqual("IMPOSSIBLE", ablations.no_acquisition(bundle).status)
        self.assertEqual("FEASIBLE", joint_reference.solve(bundle).status)

    def test_goal_projection_does_not_claim_full_scope(self):
        bundle = self.compiled(fixtures.acquisition(nuisance=2)); state = prepare(bundle["l0"])[1]
        claims = evidence.contract(bundle, state)["claims"]
        self.assertNotIn("/credentials/z/scope", claims)
        self.assertEqual(["use"], claims["/credentials/z/scope_for_task_permissions"])

    def test_probe_after_configuration(self):
        source = next(s for n, s, _ in fixtures.cases() if n == "probe_after_configure")
        bundle = self.compiled(source)
        for r in [candidate.solve(bundle, feedback=True), joint_reference.solve(bundle)]:
            self.assertTrue(r.policy["action"].startswith("configure:"))
            self.assertEqual("probe:z_native", r.policy["children"]["ok"]["action"])
            self.assertEqual(1, runtime.evaluate(bundle, r)["completion"])

    def test_observable_epoch_change_invalidates_prior(self):
        source = next(s for n, s, _ in fixtures.cases() if n == "observable_regime_change")
        bundle = self.compiled(source); before = prepare(bundle["l0"])[1]
        prior = evidence.contract(bundle, before)
        after = evidence.update(bundle, before, "probe:z_native", "observable-regime-change")
        current = evidence.contract(bundle, after)
        self.assertEqual("refresh_only", current["claims"]["/revocations/x/coverage"])
        self.assertIn(1, current["scope"]["epochs"])
        self.assertFalse(evidence.usable(prior, bundle, after))

    def test_cli_roundtrip(self):
        script = Path(__file__).resolve().parents[1] / "scripts/a_cli.py"
        with tempfile.TemporaryDirectory() as directory:
            src = Path(directory) / "source.json"; out = Path(directory) / "result.json"
            src.write_text(json.dumps(fixtures.acquisition()), encoding="utf-8")
            result = subprocess.run([sys.executable, str(script), "solve", str(src), "--out", str(out)], capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stderr)
            checked = subprocess.run([sys.executable, str(script), "check", str(src), str(out)], capture_output=True, text=True)
            self.assertEqual("ACCEPTED", json.loads(checked.stdout)["verdict"])


if __name__ == "__main__":unittest.main()
