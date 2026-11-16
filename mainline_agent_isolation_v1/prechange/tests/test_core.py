import ast
from copy import deepcopy
from itertools import combinations
import unittest
from unittest.mock import patch

from auth_lifecycle import candidate, reference
from auth_lifecycle.schema import State, Status, ModelError, prepare, validate, refs_json
from auth_lifecycle.semantics import branches, observe, terminal
from auth_lifecycle.certificates import produce
from auth_lifecycle.checker import check_policy, check_impossibility
from auth_lifecycle.fixtures import *


class CoreTests(unittest.TestCase):
    def test_registered_cases(self):
        for name, data, expected in regression_cases():
            with self.subTest(name=name):
                c, r = candidate.solve(data), reference.solve(data)
                self.assertEqual(c.status.value, expected)
                self.assertEqual(r.status.value, expected)
                if c.status is Status.FEASIBLE:
                    self.assertEqual(check_policy(data, c.policy).verdict, "ACCEPTED")
                    self.assertEqual(check_policy(data, r.policy).verdict, "ACCEPTED")
                if c.status is Status.IMPOSSIBLE:
                    status, cert, _ = produce(data, reduce_core=False)
                    self.assertEqual(status, Status.IMPOSSIBLE)
                    self.assertEqual(check_impossibility(data, cert).verdict, "ACCEPTED")

    def test_stay_requires_rank(self):
        m = stay_finish(horizon=8)
        _, st = prepare(m)
        # The unranked legacy condition can repeat the same state without progress.
        legacy_state = ("w", "s")
        for _ in range(20):
            self.assertIn("stay", m["worlds"]["w"]["states"][legacy_state[1]]["transitions"])
        for remaining in range(8, 0, -1):
            self.assertEqual(st.remaining, remaining)
            status, actions = candidate.allowed_actions(m, st)
            self.assertEqual(status, Status.FEASIBLE)
            if remaining > 1:
                self.assertIn("stay", actions); st = observe(m, st, "stay", "same")
            else:
                self.assertNotIn("stay", actions)
                self.assertIn("finish", actions)
                st = observe(m, st, "finish", "finished")
        self.assertEqual(st.remaining, 0)
        self.assertTrue(terminal(m, st))

    def test_three_world_certificate_and_all_pairs(self):
        m = conflict_worlds()
        for selected in combinations(m["worlds"], 2):
            k = [(w, "s") for w in selected]
            self.assertEqual(candidate.solve(m, knowledge=k).status, Status.FEASIBLE)
            self.assertEqual(reference.solve(m, knowledge=k).status, Status.FEASIBLE)
        status, cert, _ = produce(m)
        self.assertEqual(status, Status.IMPOSSIBLE)
        self.assertEqual(len(cert["context"]["world_subset"]), 3)
        self.assertEqual(check_impossibility(m, cert).verdict, "ACCEPTED")

    def test_exact_named_plan_sets(self):
        m = named_three_worlds()
        self.assertEqual({w:set(data["states"]["s"]["transitions"]) for w,data in m["worlds"].items()},
                         {"P1":{"a","b"},"P2":{"b","c"},"P3":{"a","c"}})
        _, cert, _ = produce(m)
        self.assertEqual(cert["context"]["world_subset"],["P1","P2","P3"])
        self.assertEqual(check_impossibility(m,cert).verdict,"ACCEPTED")

    def test_arbitrary_core_not_hardcoded_to_three(self):
        m = conflict_worlds(5)
        _, cert, _ = produce(m)
        self.assertEqual(len(cert["context"]["world_subset"]), 5)
        self.assertEqual(check_impossibility(m, cert).verdict, "ACCEPTED")

    def test_immediate_and_observation_strategy_scopes_differ(self):
        m = conflict_worlds(informative_probe=True)
        self.assertEqual(candidate.solve(m).status, Status.FEASIBLE)
        self.assertEqual(reference.solve(m).status, Status.FEASIBLE)
        status, cert, _ = produce(m, scope="no_common_immediate_completion")
        self.assertEqual(status, Status.IMPOSSIBLE)
        checked = check_impossibility(m, cert)
        self.assertEqual(checked.claim, "no_common_one_step_completion")
        forged = deepcopy(cert); forged["scope"] = "bounded_policy_impossible"
        self.assertEqual(check_impossibility(m, forged).verdict, "REJECTED")

    def test_same_observation_cannot_reveal_hidden_world(self):
        m = conflict_worlds(informative_probe=True)
        for w in m["worlds"].values():
            w["states"]["s"]["transitions"]["probe"][0]["observation"] = "opaque"
        self.assertEqual(candidate.solve(m).status, Status.IMPOSSIBLE)
        self.assertEqual(reference.solve(m).status, Status.IMPOSSIBLE)
        st = observe(m, prepare(m)[1], "probe", "opaque")
        self.assertEqual(len(st.knowledge), 3)

    def test_active_false_does_not_assert_revocation(self):
        m = active_false(); st = observe(m, prepare(m)[1], "inspect", "active:false")
        self.assertEqual(len(st.knowledge), 2)
        self.assertFalse(terminal(m, st))
        self.assertEqual(check_policy(m, {"kind": "done", "belief": refs_json(st.knowledge), "remaining": 0}, knowledge=st.knowledge, horizon=0).verdict, "REJECTED")

    def test_lost_response_keeps_both_possible_effects(self):
        m = response_loss(); st = observe(m, prepare(m)[1], "probe", "response-lost")
        self.assertEqual(st.knowledge, frozenset([("w", "no-effect"), ("w", "unknown-handle")]))
        self.assertFalse(terminal(m, st))
        self.assertEqual(candidate.solve(m, knowledge=st.knowledge, horizon=st.remaining).status, Status.FEASIBLE)

    def test_observable_conflict_invalidates_knowledge(self):
        m = declared_regime_change()
        good = observe(m, prepare(m)[1], "probe", "changed-to-v2")
        self.assertEqual(good.knowledge, frozenset([("v2", "s")]))
        bad = observe(m, prepare(m)[1], "probe", "unregistered-v3")
        self.assertEqual(bad.remaining, 1)
        self.assertTrue(bad.boundary)
        for solver in [candidate.solve, reference.solve]:
            self.assertEqual(solver(m, knowledge=bad.knowledge, horizon=bad.remaining, boundary=bad.boundary).status, Status.UNKNOWN)

    def test_empty_no_vacuous_success(self):
        m = stay_finish(); m["initial"] = []
        for solver in [candidate.solve, reference.solve]:self.assertEqual(solver(m).status, Status.UNKNOWN)
        self.assertEqual(produce(m)[0], Status.UNKNOWN)
        self.assertEqual(check_policy(m, {"kind": "done", "belief": [], "remaining": 2}).verdict, "REJECTED")

    def test_search_limits_are_inconclusive_not_impossible(self):
        for m in [stay_finish(), conflict_worlds()]:
            for solver in [candidate.solve, reference.solve]:
                answer = solver(m, node_limit=0)
                self.assertEqual(answer.status, Status.INCONCLUSIVE)
                self.assertIsNone(answer.policy); self.assertIsNone(answer.refutation)
        status, cert, _ = produce(conflict_worlds(), node_limit=0)
        self.assertEqual(status, Status.INCONCLUSIVE); self.assertIsNone(cert)

    def test_malformed_side_effect_is_unknown_not_feasible(self):
        m = session_probe(); m["worlds"]["w"]["states"]["created"]["obligations"] = []
        self.assertEqual(candidate.solve(m).status, Status.UNKNOWN)
        self.assertEqual(reference.solve(m).status, Status.UNKNOWN)

    def test_no_silent_approval_or_budget_mint(self):
        for field in ["approvals", "budget"]:
            m = stay_finish()
            target = m["worlds"]["w"]["states"]["done"]
            if field == "approvals":target[field].append("admin")
            else:target[field]["calls"] = 1
            self.assertEqual(candidate.solve(m).status, Status.UNKNOWN)

    def test_model_and_horizon_bounds(self):
        for mutate in [lambda m: m.update(horizon=9), lambda m: m.update(tasks=list("ABCDE")), lambda m: m.update(horizon=True)]:
            m = stay_finish(); mutate(m)
            self.assertEqual(candidate.solve(m).status, Status.UNKNOWN)
            self.assertEqual(reference.solve(m).status, Status.UNKNOWN)

    def test_runtime_invalid_values_fail_closed(self):
        m = stay_finish()
        for solver in [candidate.solve, reference.solve]:
            self.assertEqual(solver(m, boundary=[]).status, Status.UNKNOWN)
            self.assertEqual(solver(m, knowledge=[("missing", "s")]).status, Status.UNKNOWN)
        for observation in [None, [], ""]:
            state = observe(m, prepare(m)[1], "stay", observation)
            self.assertTrue(state.boundary)
            self.assertFalse(terminal(m, state))
        bad = deepcopy(m); bad["annotation"] = float("nan")
        cycle = deepcopy(m); cycle["annotation"] = cycle
        for malformed in [bad, cycle]:
            for solver in [candidate.solve, reference.solve]:
                self.assertEqual(solver(malformed).status, Status.UNKNOWN)

    def test_four_tasks_consume_four_steps_and_budget(self):
        m = four_tasks()
        for solver in [candidate.solve, reference.solve]:
            self.assertEqual(solver(m, horizon=3).status, Status.IMPOSSIBLE)
            self.assertEqual(solver(m, horizon=4).status, Status.FEASIBLE)

    def test_unknown_label_is_not_terminal_semantics(self):
        m = session_probe(cleanup=False)
        m["worlds"]["w"]["states"]["s"]["transitions"]["probe"][0]["observation"] = "UNKNOWN"
        state = observe(m, prepare(m)[1], "probe", "UNKNOWN")
        self.assertFalse(state.boundary)  # declared uncertain observation, not model failure
        self.assertFalse(terminal(m, state))
        self.assertEqual(candidate.solve(m).status, Status.IMPOSSIBLE)

    def test_external_budget_debit_is_in_successor_state(self):
        m = withdrawal(external=False)
        for n in m["worlds"]["w"]["states"].values():n["budget"]["calls"] = 1
        m["worlds"]["w"]["states"]["live"]["budget"]["calls"] = 0
        m["worlds"]["w"]["states"]["done"]["budget"]["calls"] = 0
        m["actions"]["finish"]["cost"]["calls"] = 1
        m["worlds"]["w"]["states"]["s"]["transitions"] = {}
        m["worlds"]["w"]["states"]["live"]["transitions"] = {}
        edge(m,("w","s"),"probe","same-result",("w","live"),effects=["external-budget-spend"])
        for solver in [candidate.solve, reference.solve]:self.assertEqual(solver(m).status, Status.IMPOSSIBLE)

    def test_independent_import_boundary(self):
        import auth_lifecycle.checker as checker
        import auth_lifecycle._reference_kernel as raw
        from pathlib import Path
        for module in [reference, checker, raw]:
            tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    self.assertNotIn(node.module, {"candidate", "semantics", "certificates"})
        m = conflict_worlds(); cert = produce(m)[1]
        with patch("auth_lifecycle.candidate.solve", side_effect=AssertionError("generator invoked")), patch("auth_lifecycle.semantics.branches", side_effect=AssertionError("candidate semantics invoked")):
            self.assertEqual(reference.solve(m).status, Status.IMPOSSIBLE)
            self.assertEqual(check_impossibility(m, cert).verdict, "ACCEPTED")


class CertificateMutationTests(unittest.TestCase):
    def test_proof_rejects_mutations(self):
        m = conflict_worlds(); original = produce(m)[1]
        mutations = [
            lambda c: c.update(model_digest="0" * 64),
            lambda c: c["context"]["actions"]["a"].update(approval="admin"),
            lambda c: c["context"]["worlds"]["w0"]["states"]["s"]["budget"].update(calls=99),
            lambda c: c["context"].update(world_subset=[]),
            lambda c: c["proof"]["actions"].pop("a"),
            lambda c: c["proof"].update(kind="horizon"),
            lambda c: c["proof"].update(remaining=0),
            lambda c: c["context"].update(constraint_refs=[]),
            lambda c: c.update(core_minimality="globally_minimum"),
        ]
        for mutation in mutations:
            bad = deepcopy(original); mutation(bad)
            self.assertEqual(check_impossibility(m, bad).verdict, "REJECTED")
        self.assertEqual(check_impossibility(m, original, node_limit=0).verdict, "INCONCLUSIVE")

    def test_policy_cannot_omit_result_or_reuse_remaining(self):
        m = conflict_worlds(informative_probe=True); proof = candidate.solve(m).policy
        bad = deepcopy(proof); bad["children"].pop(next(iter(bad["children"])))
        self.assertEqual(check_policy(m, bad).verdict, "REJECTED")
        bad = deepcopy(proof); child = next(iter(bad["children"].values())); child["remaining"] += 1
        self.assertEqual(check_policy(m, bad).verdict, "REJECTED")
        bad = deepcopy(proof); bad["children"]["secret-world-id"] = bad["children"].pop(next(iter(bad["children"])))
        self.assertEqual(check_policy(m, bad).verdict, "REJECTED")
        self.assertEqual(check_policy(m, proof, node_limit=0).verdict, "INCONCLUSIVE")

    def test_false_impossibility_for_winning_state(self):
        m = stay_finish(); template = produce(conflict_worlds())[1]
        from auth_lifecycle.schema import digest
        template["model_digest"] = digest(m)
        self.assertEqual(check_impossibility(m, template).verdict, "REJECTED")

    def test_boolean_integer_snapshot_substitution_rejected(self):
        m = budget_case(False); cert = produce(m)[1]
        # JSON false and integer zero compare equal in Python; certificate bytes do not.
        cert["context"]["worlds"]["w"]["states"]["s"]["budget"]["calls"] = False
        self.assertEqual(check_impossibility(m, cert).verdict, "REJECTED")


if __name__ == "__main__":unittest.main()
