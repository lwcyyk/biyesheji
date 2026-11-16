"""R-J: full observation-belief graph + bottom-up exact worst-request cost.

No A heuristic, feedback, candidate semantics or hidden actual-world selection.
"""
from collections import deque
from dataclasses import dataclass, field
from ..schema import prepare, ModelError, refs_json
from .._reference_kernel import expand, is_goal, is_safe


@dataclass
class Result:
    status: str
    reason: str
    policy: dict | None = None
    worst_requests: int | None = None
    stats: dict = field(default_factory=dict)
    diagnostics: list = field(default_factory=list)


def solve(bundle, *, node_limit=100_000, use_probes=True):
    try:
        data, root = prepare(bundle["l0"])
        if not root.knowledge:return Result("UNKNOWN", "empty possibility support")
        if type(node_limit) is not int or node_limit < 0 or type(use_probes) is not bool:raise ModelError("reference limit/mode")
    except (ModelError, KeyError) as exc:return Result("UNKNOWN", str(exc))
    start = (root.remaining, root.knowledge); queue = deque([start]); seen = {start}; graph = {}; count = 0
    while queue:
        if count >= node_limit:return Result("INCONCLUSIVE", "R-J graph limit", stats={"reference_nodes": count})
        key = queue.popleft(); r, belief = key; count += 1; arcs = {}
        if r > 0 and not is_goal(data, belief) and all(is_safe(data, x) for x in belief):
            for action in sorted(data["actions"]):
                if not use_probes and action.startswith("probe:"):continue
                groups, errors = expand(data, belief, action)
                if errors:continue
                arcs[action] = {obs: (r - 1, child) for obs, child in groups.items()}
                for nxt in arcs[action].values():
                    if nxt not in seen:seen.add(nxt); queue.append(nxt)
        graph[key] = arcs
    values = {}; policies = {}; cap = bundle["source"]["budget"]["requests"]
    for key in sorted(graph, key=lambda x: (x[0], sorted(x[1]))):
        r, belief = key; head = {"belief": refs_json(belief), "remaining": r}
        if is_goal(data, belief):
            values[key] = max(cap - data["worlds"][w]["states"][s]["budget"]["requests"] for w, s in belief)
            policies[key] = dict(head, kind="done"); continue
        candidates = []
        for aid, children in graph[key].items():
            if children and all(child in policies for child in children.values()):candidates.append((max(values[c] for c in children.values()), aid))
        if candidates:
            value, aid = min(candidates); values[key] = value
            policies[key] = dict(head, kind="act", action=aid, children={o: policies[c] for o, c in graph[key][aid].items()})
    if start not in policies:return Result("IMPOSSIBLE", "complete finite joint graph" if use_probes else "no-acquisition ablation only; not full joint impossibility", stats={"reference_nodes": count})
    return Result("FEASIBLE", "minimum worst total requests in identical finite action model", policies[start], values[start], {"reference_nodes": count})
