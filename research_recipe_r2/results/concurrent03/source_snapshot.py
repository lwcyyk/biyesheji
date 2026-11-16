"""Finite synthetic contract checker, with no network or native-service adapter.

It checks post-promise environment closure, bounded uniform control sequences,
and same-semantics time expansion. Provider assumptions are explicit inputs.
"""

from collections import deque
from dataclasses import asdict, dataclass, replace
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import argparse
import json


ROOT = Path(__file__).resolve().parent
KEEP_BIT = 1 << 1


@dataclass(frozen=True)
class State:
    issued: int = 3
    active: int = 3
    pending: int = 0
    fenced: bool = False
    local_closed: bool = False
    effect_pending: bool = False
    effect_emitted: bool = False


@dataclass(frozen=True)
class Profile:
    name: str
    refresh_count: int = 1
    new_unit_birth: bool = False
    revoke_scope: str = "origin"
    commit_fence: bool = True
    receiver_fence: bool = False
    resource: str = "online"
    complete_coverage: bool = True
    bounded_wait: bool = False
    strict_receipt_obligation: bool = False
    fence_response_lost: bool = False
    approved: tuple = ("close_local", "fence", "revoke", "wait")


def initial_state(profile):
    return State(pending=(1 << profile.refresh_count) - 1)


def partition_view(state, profile):
    result = {}
    for material in range(profile.refresh_count + 2):
        if not state.issued & (1 << material):
            continue
        if material == 1:
            unit = "independent"
        elif material >= 2 and profile.new_unit_birth:
            unit = "child-unit-" + str(material)
        else:
            unit = "target-unit"
        result.setdefault(unit, []).append(material)
    return result


def commit_request(state, profile, request):
    pending = state.pending & ~(1 << request)
    if state.fenced and profile.commit_fence:
        return replace(state, pending=pending)
    material_bit = 1 << (request + 2)
    return replace(state, pending=pending, issued=state.issued | material_bit,
                   active=state.active | material_bit)


def environment_edges(state, profile):
    edges = []
    for request in range(profile.refresh_count):
        if state.pending & (1 << request):
            edges.append(("commit_refresh_" + str(request), commit_request(state, profile, request)))
    if state.effect_pending:
        edges.append(("commit_preaccepted_effect", replace(state, effect_pending=False, effect_emitted=True)))
    return edges


def environment_closure(state, profile):
    queue = deque([state])
    seen = {state}
    while queue:
        current = queue.popleft()
        for _, successor in environment_edges(current, profile):
            if successor not in seen:
                seen.add(successor)
                queue.append(successor)
    return frozenset(seen)


def target_is_accepted(state, profile):
    target_materials = state.issued & ~KEEP_BIT
    if profile.resource == "offline_before_expiry":
        return bool(target_materials)
    if profile.receiver_fence and state.fenced:
        return False
    return bool(state.active & target_materials)


def is_bad(state, profile, target):
    if not state.active & KEEP_BIT:
        return True
    if target == "L":
        return not state.local_closed
    if target == "E":
        return state.effect_emitted
    if target == "R+E":
        return target_is_accepted(state, profile) or state.effect_emitted
    return target_is_accepted(state, profile)


def check_promise(state, profile, target="R"):
    # E records new effects relative to this promise cut, preserving prior history.
    cut_state = replace(state, effect_emitted=False)
    queue = deque([(cut_state, ())])
    seen = {cut_state}
    while queue:
        current, trace = queue.popleft()
        if is_bad(current, profile, target):
            return {"status": "REFUTED_IN_MODEL", "trace": list(trace),
                    "counterexample_state": asdict(current),
                    "partition": partition_view(current, profile), "nodes": len(seen)}
        for event, successor in environment_edges(current, profile):
            if successor not in seen:
                seen.add(successor)
                queue.append((successor, trace + (event,)))
    if not profile.complete_coverage:
        return {"status": "UNKNOWN", "reason": "uncovered model or observation boundary", "nodes": len(seen)}
    return {"status": "SAFE_IN_MODEL", "nodes": len(seen)}


def direct_predicate(state, profile, target="R"):
    """Independent closed-form check for this finite workload profile only."""
    def verdict(safe):
        if not safe:
            return "REFUTED_IN_MODEL"
        return "SAFE_IN_MODEL" if profile.complete_coverage else "UNKNOWN"
    if not state.active & KEEP_BIT:
        return "REFUTED_IN_MODEL"
    if target == "L":
        return verdict(state.local_closed)
    effect_safe = not state.effect_pending
    if target == "E":
        return verdict(effect_safe)
    if profile.resource == "offline_before_expiry":
        current_clear = state.issued & ~KEEP_BIT == 0
        pending_blocked = state.fenced and profile.commit_fence
    else:
        enforced_epoch = state.fenced and profile.receiver_fence
        current_clear = enforced_epoch or state.active & ~KEEP_BIT == 0
        pending_blocked = enforced_epoch or state.fenced and profile.commit_fence
    future_clear = current_clear and (state.pending == 0 or pending_blocked)
    if target == "R+E":
        future_clear = future_clear and effect_safe
    return verdict(future_clear)


def control_outcomes(state, profile, action):
    if action not in profile.approved:
        return ()
    if action == "close_local":
        return (replace(state, local_closed=True),)
    if action == "fence":
        fenced = replace(state, fenced=True)
        return (state, fenced) if profile.fence_response_lost else (fenced,)
    if action == "revoke":
        if profile.revoke_scope == "account":
            return (replace(state, active=0),)
        if profile.revoke_scope == "origin":
            return (replace(state, active=state.active & KEEP_BIT),)
        removed = 1
        if not profile.new_unit_birth:
            removed |= ((1 << (profile.refresh_count + 2)) - 1) & ~3
        return (replace(state, active=state.active & ~removed),)
    if action == "wait" and profile.bounded_wait and state.pending:
        return tuple(commit_request(state, profile, request)
                     for request in range(profile.refresh_count) if state.pending & (1 << request))
    if action == "wait":
        return (state,)
    raise ValueError(action)


def complete_finite_states(profile):
    first = initial_state(profile)
    queue = deque([first])
    seen = {first}
    while queue:
        state = queue.popleft()
        successors = [next_state for _, next_state in environment_edges(state, profile)]
        for action in profile.approved:
            successors.extend(control_outcomes(state, profile, action))
        for successor in successors:
            if successor not in seen:
                seen.add(successor)
                queue.append(successor)
    return seen


def bounded_plan(profile, budget, depth, target="R"):
    if not profile.complete_coverage:
        return {"status": "UNKNOWN", "plan": None}
    costs = {"close_local": 0, "fence": 1, "revoke": 1, "wait": 0}
    initial_belief = environment_closure(initial_state(profile), profile)
    examined = 0

    @lru_cache(None)
    def visit(belief, remaining_budget, remaining_depth):
        nonlocal examined
        examined += 1
        goal = all(check_promise(state, profile, target)["status"] == "SAFE_IN_MODEL" for state in belief)
        obligations_closed = not profile.strict_receipt_obligation or all(state.pending == 0 for state in belief)
        if goal and obligations_closed:
            return ()
        if remaining_depth == 0:
            return None
        for action in profile.approved:
            charge = costs[action]
            if charge > remaining_budget:
                continue
            post = set()
            safe_prefix = True
            for state in belief:
                for successor in control_outcomes(state, profile, action):
                    if not successor.active & KEEP_BIT:
                        safe_prefix = False
                    post.update(environment_closure(successor, profile))
            if not post or not safe_prefix:
                continue
            tail = visit(frozenset(post), remaining_budget - charge, remaining_depth - 1)
            if tail is not None:
                return (action,) + tail
        return None

    plan = visit(initial_belief, budget, depth)
    return {"status": "FEASIBLE_IN_MODEL" if plan is not None else "IMPOSSIBLE_WITHIN_BOUND",
            "plan": list(plan) if plan is not None else None, "belief_states": examined,
            "budget": budget, "depth": depth, "observation_model": "one public outcome containing every allowed successor"}


def expansion_sizes(profile, horizon):
    first = control_outcomes(initial_state(profile), profile, "revoke")[0]

    def edges(state):
        # Two differently labeled internal delays make the history-tree distinction explicit.
        return environment_edges(state, profile) + [("delay_a", state), ("delay_b", state)]

    @lru_cache(None)
    def tree_size(state, remaining):
        if remaining == 0:
            return 1
        return 1 + sum(tree_size(child, remaining - 1) for _, child in edges(state))

    layer = {first}
    layered_nodes = 1
    all_states = {first}
    layered_bad = target_is_accepted(first, profile)
    for _ in range(horizon):
        layer = {child for state in layer for _, child in edges(state)}
        layered_nodes += len(layer)
        all_states.update(layer)
        layered_bad = layered_bad or any(target_is_accepted(state, profile) for state in layer)
    direct = check_promise(first, profile)["status"] == "REFUTED_IN_MODEL"
    assert horizon >= profile.refresh_count
    assert layered_bad == direct
    return {"horizon": horizon, "state_graph_nodes": len(all_states), "layered_DAG_nodes": layered_nodes,
            "unshared_history_tree_nodes_counted": tree_size(first, horizon),
            "history_tree_materialized": False, "same_bad_reachability": True,
            "scope": "representation counts; generic memoization obtains the same DAG"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="results/concurrent01")
    args = parser.parse_args()
    output = ROOT / args.out
    output.mkdir(parents=True, exist_ok=False)
    profiles = []
    for pending in range(4):
        profiles.extend([
            Profile("snapshot_" + str(pending), pending, commit_fence=False),
            Profile("commit_fence_" + str(pending), pending),
            Profile("new_unit_" + str(pending), pending, new_unit_birth=True, revoke_scope="unit"),
            Profile("offline_" + str(pending), pending, resource="offline_before_expiry"),
            Profile("receiver_fence_" + str(pending), pending, commit_fence=False, receiver_fence=True),
            Profile("account_scope_" + str(pending), pending, revoke_scope="account"),
        ])
    checks = 0
    state_rows = []
    for profile in profiles:
        for state in sorted(complete_finite_states(profile), key=lambda x: tuple(asdict(x).values())):
            for target in ("L", "R"):
                answer = check_promise(state, profile, target)
                expected = direct_predicate(state, profile, target)
                assert answer["status"] == expected, (profile, state, target, answer, expected)
                checks += 1
                state_rows.append({"profile": profile.name, "state": asdict(state), "partition": partition_view(state, profile),
                                   "target": target, "expected": expected, "actual": answer})
    base = Profile("base", 1)
    revoked = control_outcomes(initial_state(base), base, "revoke")[0]
    counterexamples = {"late_birth": check_promise(revoked, base)}
    assert counterexamples["late_birth"]["status"] == "REFUTED_IN_MODEL"
    fenced = control_outcomes(revoked, base, "fence")[0]
    assert check_promise(fenced, base)["status"] == "SAFE_IN_MODEL"
    stale = replace(base, name="stale_precheck", commit_fence=False)
    counterexamples["stale_precheck"] = check_promise(fenced, stale)
    assert counterexamples["stale_precheck"]["status"] == "REFUTED_IN_MODEL"
    effect = replace(fenced, effect_pending=True)
    counterexamples["R_safe_E_refuted"] = {target: check_promise(effect, base, target) for target in ("R", "E")}
    assert counterexamples["R_safe_E_refuted"]["R"]["status"] == "SAFE_IN_MODEL"
    assert counterexamples["R_safe_E_refuted"]["E"]["status"] == "REFUTED_IN_MODEL"
    unknown = replace(base, name="incomplete_registry", complete_coverage=False)
    assert check_promise(fenced, unknown)["status"] == "UNKNOWN"
    counterexamples["incomplete_with_known_counterexample"] = check_promise(initial_state(base), unknown)
    assert counterexamples["incomplete_with_known_counterexample"]["status"] == "REFUTED_IN_MODEL"
    shared = replace(base, name="account_revoke_with_preserve", revoke_scope="account")
    shared_after = control_outcomes(initial_state(shared), shared, "revoke")[0]
    counterexamples["account_scope_preservation_failure"] = check_promise(shared_after, shared)
    assert counterexamples["account_scope_preservation_failure"]["status"] == "REFUTED_IN_MODEL"
    plans = []
    plan_cases = [
        (base, 2, 3, "R", "FEASIBLE_IN_MODEL"),
        (base, 1, 5, "R", "IMPOSSIBLE_WITHIN_BOUND"),
        (replace(base, approved=("close_local", "revoke", "wait")), 3, 5, "R", "IMPOSSIBLE_WITHIN_BOUND"),
        (replace(base, bounded_wait=True), 1, 2, "R", "FEASIBLE_IN_MODEL"),
        (replace(base, refresh_count=3, bounded_wait=True), 1, 4, "R", "FEASIBLE_IN_MODEL"),
        (replace(base, strict_receipt_obligation=True), 2, 5, "R", "IMPOSSIBLE_WITHIN_BOUND"),
        (replace(base, fence_response_lost=True), 3, 5, "R", "IMPOSSIBLE_WITHIN_BOUND"),
        (replace(base, resource="offline_before_expiry"), 3, 5, "R", "IMPOSSIBLE_WITHIN_BOUND"),
        (base, 0, 1, "L", "FEASIBLE_IN_MODEL"),
        (unknown, 3, 5, "R", "UNKNOWN"),
        (shared, 3, 5, "R", "IMPOSSIBLE_WITHIN_BOUND"),
    ]
    for index, (profile, budget, depth, target, expected) in enumerate(plan_cases):
        result = bounded_plan(profile, budget, depth, target)
        assert result["status"] == expected, (index, result, expected)
        plans.append({"case": index, "profile": asdict(profile), "target": target,
                      "expected": expected, "actual": result})
    expansion = [expansion_sizes(Profile("expansion", pending, commit_fence=False), horizon)
                 for pending in (1, 2, 3) for horizon in (4, 6, 8)]
    (output / "states.jsonl").write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in state_rows) + "\n", encoding="utf-8")
    results = {"pass": True, "profiles": [asdict(profile) for profile in profiles], "state_target_checks": checks,
               "plans": plans, "counterexamples": counterexamples, "expansion": expansion,
               "source_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
               "native_calls": 0, "scope": "finite declared preaccepted requests and registered resources; no native implementation claim"}
    (output / "result.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"pass": True, "profiles": len(profiles), "state_target_checks": checks,
                      "plan_cases": len(plans), "expansion_cases": len(expansion)}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
