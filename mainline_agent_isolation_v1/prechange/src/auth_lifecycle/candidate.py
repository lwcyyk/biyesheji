"""Memoized bounded AND/OR search; policies have observation-only branches."""
from .schema import ModelError, Result, State, Status, prepare, refs_json
from .semantics import branches, safe, terminal


def solve(spec, *, knowledge=None, horizon=None, boundary=None, node_limit=100_000):
    try:
        data, initial = prepare(spec, knowledge, horizon, boundary)
    except (ModelError, ValueError) as exc:
        return Result(Status.UNKNOWN, str(exc))
    if initial.boundary or not initial.knowledge:
        return Result(Status.UNKNOWN, initial.boundary or "empty_knowledge")
    if type(node_limit) is not int or node_limit < 0:
        return Result(Status.UNKNOWN, "invalid_search_limit")
    memo = {}; explored = 0

    class Exhausted(Exception):
        pass

    def visit(state):
        nonlocal explored
        if state in memo:return memo[state]
        if explored >= node_limit:raise Exhausted()
        explored += 1
        head = {"belief": refs_json(state.knowledge), "remaining": state.remaining}
        if terminal(data, state):
            answer = (True, dict(head, kind="done"))
        elif not all(safe(data, x) for x in state.knowledge):
            answer = (False, dict(head, kind="unsafe"))
        elif state.remaining == 0:
            answer = (False, dict(head, kind="horizon"))
        else:
            failures = {}
            for aid in sorted(data["actions"]):
                children, errors = branches(data, state, aid)
                if errors:
                    failures[aid] = {"kind": "blocked", "constraint_refs": errors}
                    continue
                policies = {}; losing = None
                for observation, child in children.items():
                    win, proof = visit(child)
                    if not win:
                        losing = {"kind": "losing_observation", "observation": observation, "child": proof}
                        break
                    policies[observation] = proof
                if losing is None:
                    answer = (True, dict(head, kind="act", action=aid, children=policies))
                    memo[state] = answer
                    return answer
                failures[aid] = losing
            answer = (False, dict(head, kind="all_actions_fail", actions=failures))
        memo[state] = answer
        return answer

    try:
        winning, proof = visit(initial)
        return Result(Status.FEASIBLE if winning else Status.IMPOSSIBLE,
                      "complete_bounded_search", explored,
                      policy=proof if winning else None,
                      refutation=None if winning else proof)
    except Exhausted:
        return Result(Status.INCONCLUSIVE, "search_limit", explored)


def allowed_actions(spec, state, *, node_limit=100_000):
    """Only actions whose complete observation branches win at remaining-1.

    Any unfinished child makes the menu INCONCLUSIVE (not a complete safe menu).
    """
    if state.boundary or not state.knowledge:return Status.UNKNOWN, []
    try:
        data, state = prepare(spec, state.knowledge, state.remaining, state.boundary)
    except ModelError:return Status.UNKNOWN, []
    if terminal(data, state):return Status.FEASIBLE, []
    allowed = []
    for aid in sorted(data["actions"]):
        nexts, errors = branches(data, state, aid)
        if errors:continue
        results = [solve(data, knowledge=s.knowledge, horizon=s.remaining, node_limit=node_limit) for s in nexts.values()]
        if any(r.status in {Status.INCONCLUSIVE, Status.UNKNOWN} for r in results):
            return Status.INCONCLUSIVE, []
        if all(r.status is Status.FEASIBLE for r in results):allowed.append(aid)
    return (Status.FEASIBLE if allowed else Status.IMPOSSIBLE), allowed
