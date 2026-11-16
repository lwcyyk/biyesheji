"""Exact reference: global bitmask enumeration + independent concrete-state BFS."""
from collections import deque
from .model import prepare, ModelError, Result, Work, Cutoff
from . import _kernel as k


def plan(m, config, scenario, initial, work):
    pending = deque([(initial, [])]); seen = {initial}; menu = k.menu(m, config)
    while pending:
        state, prefix = pending.popleft(); work.tick("reference_states")
        if k.final(m, config, state, scenario):return prefix
        if not state[5]:continue
        for action in menu:
            successor, refs = k.transition(m, config, state, scenario, action)
            if refs:continue
            # Repeating an irreversible action changes only nonnegative costs/r.
            # Removing that repetition preserves all predicates and frees budget.
            if successor[:3] == state[:3]:continue
            if successor not in seen:
                seen.add(successor); pending.append((successor, prefix + [action]))
    return None


def solve(spec, *, limit=1_000_000):
    best = None
    try:
        m = prepare(spec); work = Work(limit); names = sorted(m["paths"])
        for mask in range(1 << len(names)):
            work.tick("reference_configurations")
            config = [p for i, p in enumerate(names) if mask & (1 << i)]
            refs, initial, setup, metrics = k.configuration(m, config)
            if refs:continue
            plans = {}; ends = []
            for sid, scenario in sorted(m["scenarios"].items()):
                route = plan(m, config, scenario, initial, work)
                if route is None:break
                plans[sid] = route; state = initial
                for action in route:state, _ = k.transition(m, config, state, scenario, action)
                ends.append(state)
            if len(plans) != len(m["scenarios"]):continue
            metrics.update(worst_lifecycle_requests=max(s[3] for s in ends),
                           worst_lifecycle_approvals=max(s[4] for s in ends),
                           max_stop_steps=max(len(p) for p in plans.values()), native_units=k.native_units(m, config))
            delivery = {"configuration": config, "setup": setup, "plans": plans}
            key = (metrics["G"], config)
            if best is None or key < best[0]:best = (key, delivery, metrics)
        if best is None:return Result("IMPOSSIBLE", "complete finite catalog", optimal=True, stats=work.counts)
        return Result("FEASIBLE", "complete finite catalog", best[1]["configuration"], best[1], best[2], True, work.counts)
    except Cutoff:
        return Result("INCONCLUSIVE", "reference work limit; no optimum/impossibility claim",
                      delivery=best[1] if best else None, stats=work.counts)
    except ModelError as exc:return Result("UNKNOWN", str(exc))
