"""Candidate-side finite semantics. The reference implements its own interpreter."""
from collections import defaultdict
from .schema import State, ModelError, prepare


def node(spec, reference):
    return spec["worlds"][reference[0]]["states"][reference[1]]


def safe(spec, reference):
    n = node(spec, reference)
    return (not (set(n["facts"]) & set(spec["safety"]["forbidden_facts"]))
            and set(spec["safety"]["preserve_capabilities"]) <= set(n["capabilities"]))


def terminal(spec, state):
    return bool(state.knowledge) and not state.boundary and all(
        safe(spec, ref) and node(spec, ref)["account"] == spec["goal"]["account"]
        and set(spec["goal"]["facts"]) <= set(node(spec, ref)["facts"])
        and not node(spec, ref)["obligations"] for ref in state.knowledge)


def branches(spec, state, aid):
    """Universal precondition; union by *visible observation*, not hidden state."""
    if state.boundary or not state.knowledge or state.remaining <= 0:
        return {}, ["knowledge-or-horizon-boundary"]
    if aid not in spec["actions"]:
        return {}, [f"action:{aid}"]
    action = spec["actions"][aid]
    errors, grouped = [], defaultdict(set)
    for wid, sid in sorted(state.knowledge):
        n = node(spec, (wid, sid)); prefix = f"{wid}/{sid}"
        if not safe(spec, (wid, sid)):errors.append(f"safe:{prefix}")
        if n["account"] != action["account"]:errors.append(f"account:{aid}:{prefix}")
        if action["approval"] not in n["approvals"]:errors.append(f"approval:{action['approval']}:{prefix}")
        if not set(action["requires"]) <= set(n["facts"]):errors.append(f"requires:{aid}:{prefix}")
        for key, cost in action["cost"].items():
            if n["budget"].get(key, -1) < cost:errors.append(f"budget:{key}:{prefix}")
        roots = spec["worlds"][wid]["native_roots"]
        for left, right in action["independent"]:
            if left not in roots or right not in roots or roots[left] == roots[right]:
                errors.append(f"independence:{left}:{right}:{prefix}")
        edges = n["transitions"].get(aid, [])
        if not edges:errors.append(f"successors:{aid}:{prefix}")
        for edge in edges:grouped[edge["observation"]].add(tuple(edge["target"]))
    if errors:return {}, sorted(errors)
    return {o: State(frozenset(k), state.remaining - 1) for o, k in sorted(grouped.items())}, []


def observe(spec, state, action, observation):
    """Unpredicted observations invalidate the usable belief; no success fallback."""
    try:
        spec, state = prepare(spec, state.knowledge, state.remaining, state.boundary)
        if not isinstance(observation, str) or not observation:
            return State(frozenset(), max(0, state.remaining - 1), "invalid_observation")
        possible, errors = branches(spec, state, action)
    except (ModelError, TypeError, KeyError, AttributeError):
        return State(frozenset(), 0, "invalid_model_or_state")
    if errors:
        return State(frozenset(), max(0, state.remaining - 1), "invalid_dispatch")
    if observation not in possible:
        return State(frozenset(), state.remaining - 1, "out_of_model_observation")
    return possible[observation]
