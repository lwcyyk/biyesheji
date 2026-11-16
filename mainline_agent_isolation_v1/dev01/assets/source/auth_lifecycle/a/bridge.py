"""B -> A diagnostic interface over possible contracts; never actual-world truth.

Certificates concern a fixed B configuration/contract, NOT joint observation
strategy impossibility. Cleanup liabilities remain in the joint safety model.
"""
from itertools import combinations
from copy import deepcopy
from ..b import search, certificates
from ..b import _kernel as b_kernel
from ..b.checker import check_conflict
from ..schema import canonical, digest
from .model import adjusted, properties
from ._plant_reference import physical


class Feedback:
    def __init__(self, bundle, *, b_limit=100_000):
        self.bundle = bundle; self.b_limit = b_limit; self.cache = {}; self.calls = 0; self.b_work = 0; self.guard_checks = 0

    def get(self, state):
        if state.boundary or not state.knowledge or type(state.remaining) is not int or not 0 <= state.remaining <= self.bundle["source"]["horizon"]:
            return {"status": "UNKNOWN", "pairs": [], "reason": "boundary, empty support or invalid remaining horizon"}
        key = (self.bundle["source_digest"], tuple(sorted(state.knowledge)), state.remaining)
        if key in self.cache:return self.cache[key]
        self.calls += 1; source = self.bundle["source"]
        points = [(w + "/" + sid, self.bundle["points"][w + "/" + sid]["point"]) for w, sid in sorted(state.knowledge)]
        if any(p["configuration"] is not None for _, p in points):
            if any(p["configuration"] is None for _, p in points):return {"status": "INCONCLUSIVE", "pairs": [], "reason": "mixed setup phase"}
            report = self._configured(state, points)
            self.cache[key] = report
            return report
        configs = [m["configuration"] for m in self.bundle["catalog"].values() if m["kind"] == "configure"]
        rows = {}; best = {}; complete = True
        for point_id, point in points:
            contract = adjusted(source, point); contract["horizon"] = min(contract["horizon"], max(0, state.remaining - 1))
            optimum = search.solve(contract, limit=self.b_limit)
            self.b_work += sum(optimum.stats.values()); best[point_id] = {"status": optimum.status, "configuration": optimum.configuration, "metrics": optimum.metrics}
            rows[point_id] = []
            for config in configs:
                answer = certificates.produce(contract, configuration=config, limit=self.b_limit)
                self.b_work += sum(answer.get("work", {}).values())
                item = {"configuration": config, "status": answer["status"]}
                if answer["status"] == "IMPOSSIBLE":
                    checked = check_conflict(contract, answer["certificate"], limit=self.b_limit)
                    self.b_work += sum(checked.get("work", {}).values())
                    item.update(certificate=answer["certificate"], check=checked)
                    if checked["verdict"] != "ACCEPTED":complete = False
                elif answer["status"] != "FEASIBLE":complete = False
                rows[point_id].append(item)
        pairs = []; diffs = []
        for (left, lp), (right, rp) in combinations(points, 2):
            divergent = [i for i, (l, r) in enumerate(zip(rows[left], rows[right])) if {l["status"], r["status"]} == {"FEASIBLE", "IMPOSSIBLE"}]
            if divergent:
                pairs.append([left, right]); lv = properties(source["worlds"][lp["world"]]); rv = properties(source["worlds"][rp["world"]])
                diffs.append({"points": [left, right], "configurations": [configs[i] for i in divergent],
                              "semantic_refs": [p for p in sorted(set(lv) | set(rv)) if canonical(lv.get(p)) != canonical(rv.get(p))],
                              "resource_refs": [f"budget.{k}" for k in lp["budget"] if lp["budget"][k] != rp["budget"][k]]})
        result = {"status": "COMPLETE" if complete else "INCONCLUSIVE", "pairs": pairs, "semantic_disagreements": diffs,
                  "configurations": configs, "rows": rows, "B_optima": best,
                  "scope": {"source_digest": self.bundle["source_digest"], "belief": [p for p, _ in points], "remaining": state.remaining},
                  "limitations": "fixed-configuration B conflicts; not a proof that all observation strategies fail; outstanding probe cleanup is checked by joint W, not B"}
        self.cache[key] = result
        return result

    def _configured(self, state, points):
        """Concrete immediate B stop conflicts, NOT a residual-policy certificate."""
        source = self.bundle["source"]; names = sorted({a for _, p in points for a in b_kernel.menu(source["worlds"][p["world"]], p["configuration"])})
        rows = {}
        for point_id, point in points:
            contract = deepcopy(source["worlds"][point["world"]]); contract["approved"] = point["approved"]
            concrete = physical(source, point); sc = contract["scenarios"][source["scenario"]]; entries = []
            for action in names:
                self.guard_checks += 1
                _, refs = b_kernel.transition(contract, point["configuration"], concrete, sc, action)
                entries.append({"configuration": point["configuration"], "native_action": action,
                                "status": "BLOCKED_NEXT_STEP" if refs else "LEGAL_NEXT_STEP", "constraint_refs": refs})
            rows[point_id] = entries
        pairs = []; diffs = []
        for (left, lp), (right, rp) in combinations(points, 2):
            differing = [i for i, (l, r) in enumerate(zip(rows[left], rows[right])) if l["status"] != r["status"]]
            if differing:
                pairs.append([left, right]); lv = properties(source["worlds"][lp["world"]]); rv = properties(source["worlds"][rp["world"]])
                diffs.append({"points": [left, right], "native_actions": [names[i] for i in differing],
                              "semantic_refs": [f for f in sorted(set(lv) | set(rv)) if canonical(lv.get(f)) != canonical(rv.get(f))]})
        return {"status": "COMPLETE", "pairs": pairs, "rows": rows, "semantic_disagreements": diffs,
                "scope": {"kind": "configured_immediate_stop_conflicts", "belief": [name for name, _ in points], "remaining": state.remaining,
                          "source_digest": self.bundle["source_digest"]},
                "limitations": "immediate fixed-B stop guards only; no claim that every future observation policy fails; joint W checks faults and cleanup"}
