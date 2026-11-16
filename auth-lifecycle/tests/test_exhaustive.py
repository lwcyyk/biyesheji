"""Exhaust 1296 explicitly defined small models x horizons 0..3.

Two worlds, states s/done per world, two actions, cost zero. Each action at s
has no edge or one edge to s/done, with observation bit 0/1. Terminal states
have no outgoing edges. No claim of exhausting arbitrary authentication models.
"""
from itertools import product
from pathlib import Path
import json, os, unittest
from auth_lifecycle import candidate, reference
from auth_lifecycle.schema import Status, canonical, digest
from auth_lifecycle.checker import check_policy, check_impossibility
from auth_lifecycle.certificates import produce
from auth_lifecycle.fixtures import model, world, state, action, edge


class ExhaustiveTests(unittest.TestCase):
    def test_complete_declared_grid(self):
        directory = os.environ.get("AUTH_L0_RESULT_DIR")
        stream = open(Path(directory)/"exhaustive.jsonl", "w", encoding="utf-8") if directory else None
        models = open(Path(directory)/"exhaustive_models.jsonl", "w", encoding="utf-8") if directory else None
        totals = {"models": 0, "queries": 0, "feasible": 0, "impossible": 0, "max_candidate_nodes": 0, "max_reference_nodes": 0}
        try:
            for targets in product(range(3), repeat=4):
                for bits in product(range(2), repeat=4):
                    m = model({w: world({"s": state(), "done": state(facts=["done"])}) for w in ["w0", "w1"]},
                              {a: action() for a in ["a", "b"]})
                    for idx, (wid, aid) in enumerate(product(["w0", "w1"], ["a", "b"])):
                        if targets[idx]:edge(m, (wid, "s"), aid, str(bits[idx]), (wid, "s" if targets[idx] == 1 else "done"))
                    mid = totals["models"]; totals["models"] += 1
                    if models:models.write(canonical({"model_id": mid, "targets": targets, "bits": bits, "spec": m})+"\n")
                    was_win = False
                    for h in range(4):
                        c, r = candidate.solve(m, horizon=h), reference.solve(m, horizon=h)
                        row = {"model_id": mid, "horizon": h, "expected_reference": r.status.value,
                               "actual_candidate": c.status.value, "candidate_nodes": c.explored, "reference_nodes": r.explored}
                        self.assertEqual(c.status, r.status, row)
                        self.assertIn(c.status, [Status.FEASIBLE, Status.IMPOSSIBLE])
                        if was_win:self.assertEqual(c.status, Status.FEASIBLE, "horizon monotonicity")
                        was_win = c.status is Status.FEASIBLE
                        if was_win:
                            checked = check_policy(m, c.policy, horizon=h)
                            self.assertEqual(checked.verdict, "ACCEPTED", row)
                            self.assertEqual(check_policy(m, r.policy, horizon=h).verdict, "ACCEPTED")
                            # Restricting initial uncertainty cannot destroy a robust policy's existence.
                            for w in ["w0", "w1"]:
                                self.assertEqual(reference.solve(m, knowledge=[(w, "s")], horizon=h).status, Status.FEASIBLE)
                            totals["feasible"] += 1
                        else:
                            _, cert, _ = produce(m, horizon=h, reduce_core=False)
                            checked = check_impossibility(m, cert, horizon=h)
                            self.assertEqual(checked.verdict, "ACCEPTED", row)
                            totals["impossible"] += 1
                        row["certificate_or_policy_check"] = checked.verdict
                        if stream:stream.write(canonical(row)+"\n")
                        totals["queries"] += 1
                        totals["max_candidate_nodes"] = max(totals["max_candidate_nodes"], c.explored)
                        totals["max_reference_nodes"] = max(totals["max_reference_nodes"], r.explored)
            self.assertEqual(totals["models"], 1296)
            self.assertEqual(totals["queries"], 5184)
        finally:
            if stream:stream.close()
            if models:models.close()
            if directory:(Path(directory)/"exhaustive_summary.json").write_text(json.dumps(totals,indent=2),encoding="utf-8")


if __name__ == "__main__":unittest.main()
