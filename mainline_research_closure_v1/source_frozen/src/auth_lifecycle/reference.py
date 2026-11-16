"""R-I: enumerate reachable information states, then evaluate bottom-up.

This does not call the candidate's search, predicates, transition grouping or
memo tables. It works from the validated raw JSON model with its own interpreter.
"""
from collections import deque
from .schema import ModelError, Result, Status, prepare, refs_json
from ._reference_kernel import expand, is_goal, is_safe


def solve(spec, *, knowledge=None, horizon=None, boundary=None, node_limit=100_000):
    try:
        data, root = prepare(spec, knowledge, horizon, boundary)
    except (ModelError, ValueError) as exc:
        return Result(Status.UNKNOWN, str(exc))
    if root.boundary or not root.knowledge:
        return Result(Status.UNKNOWN, root.boundary or "empty_knowledge")
    if type(node_limit) is not int or node_limit < 0:return Result(Status.UNKNOWN, "invalid_search_limit")
    initial = (root.remaining, root.knowledge)
    pending = deque([initial]); seen = {initial}; graph = {}; explored = 0
    while pending:
        if explored >= node_limit:return Result(Status.INCONCLUSIVE, "search_limit", explored)
        r, k = pending.popleft(); explored += 1; outgoing = {}
        if r > 0 and not is_goal(data, k) and all(is_safe(data, key) for key in k):
            for aid in sorted(data["actions"]):
                groups, why = expand(data, k, aid)
                if why:continue
                outgoing[aid] = {o: (r - 1, child) for o, child in groups.items()}
                for child in outgoing[aid].values():
                    if child not in seen:seen.add(child); pending.append(child)
        graph[(r, k)] = outgoing
    winners = {}; policies = {}
    for key in sorted(graph, key=lambda x: (x[0], sorted(x[1]))):
        r, k = key; header = {"belief": refs_json(k), "remaining": r}
        if is_goal(data, k):
            winners[key] = True; policies[key] = dict(header, kind="done")
            continue
        chosen = None
        if r and all(is_safe(data, point) for point in k):
            for aid, children in graph[key].items():
                if children and all(winners[child] for child in children.values()):
                    chosen = aid; break
        winners[key] = chosen is not None
        if chosen is not None:
            policies[key] = dict(header, kind="act", action=chosen,
                                 children={o: policies[c] for o, c in graph[key][chosen].items()})
    return Result(Status.FEASIBLE if winners[initial] else Status.IMPOSSIBLE,
                  "complete_reachable_graph", explored, policy=policies.get(initial))
