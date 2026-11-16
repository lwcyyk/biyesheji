"""Untrusted certificate PRODUCER. Checker is in checker.py, not this module."""
from copy import deepcopy
from .schema import ModelError, Status, digest, prepare, refs_json
from .candidate import solve


def context(data, belief, horizon):
    names = sorted({w for w, _ in belief})
    # Include the entire declared universe: external transitions may change regime.
    return {"world_subset": names, "root_belief": refs_json(belief), "horizon": horizon,
            "worlds": deepcopy(data["worlds"]), "actions": deepcopy(data["actions"]),
            "goal": deepcopy(data["goal"]), "safety": deepcopy(data["safety"]),
            "constraint_refs": ["approval", "account", "budget", "requires", "independence",
                                "successors", "safe", "goal", "strict_obligations", "remaining_steps"]}


def produce(spec, *, horizon=None, scope="bounded_policy_impossible", reduce_core=True,
            node_limit=100_000):
    try:
        data, initial = prepare(spec, horizon=horizon)
    except ModelError as exc:return Status.UNKNOWN, None, str(exc)
    if scope not in {"bounded_policy_impossible", "no_common_immediate_completion"}:
        return Status.UNKNOWN, None, "unknown certificate scope"
    if not initial.knowledge:return Status.UNKNOWN, None, "empty_knowledge"
    r = initial.remaining if scope == "bounded_policy_impossible" else min(1, initial.remaining)
    if scope == "no_common_immediate_completion" and r != 1:
        return Status.UNKNOWN, None, "immediate scope requires at least one available step"
    belief = initial.knowledge
    result = solve(data, knowledge=belief, horizon=r, node_limit=node_limit)
    if result.status is not Status.IMPOSSIBLE:return result.status, None, result.reason
    core_checks = 0
    if reduce_core:
        for name in sorted({w for w, _ in belief}):
            smaller = frozenset(point for point in belief if point[0] != name)
            if not smaller:continue
            attempt = solve(data, knowledge=smaller, horizon=r, node_limit=node_limit); core_checks += 1
            if attempt.status is Status.IMPOSSIBLE:belief, result = smaller, attempt
    certificate = {"schema": "auth-lifecycle-certificate/1", "scope": scope,
                   "model_digest": digest(data), "query": {"initial": refs_json(initial.knowledge), "horizon": initial.remaining},
                   "context": context(data, belief, r), "proof": result.refutation,
                   "core_minimality": "not_claimed", "core_checks": core_checks}
    return Status.IMPOSSIBLE, certificate, "bounded certificate generated; see scope"
