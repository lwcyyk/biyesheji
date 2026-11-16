"""Scoped version-space evidence and non-vacuous conservative updates."""
from ..schema import State, canonical, digest, refs_json
from ..semantics import branches
from .model import properties


def update(bundle, state, action, observation):
    if state.boundary or not state.knowledge:return state
    groups, errors = branches(bundle["l0"], state, action)
    if errors:return State(state.knowledge, state.remaining, "invalid_dispatch_no_execution")
    if isinstance(observation, str) and observation in groups:return groups[observation]
    # Retain ALL modeled successors and fence them; they are not claimed to cover
    # the unmodeled real state. No empty-support vacuous success, no best-world guess.
    support = frozenset(x for child in groups.values() for x in child.knowledge)
    return State(support or state.knowledge, max(0, state.remaining - 1), "out_of_model_observation")


def contract(bundle, state, transcript=()):
    if state.boundary or not state.knowledge:return {"status": "UNKNOWN", "claims": {}, "boundary": state.boundary or "empty_support"}
    source = bundle["source"]; values = []; epochs = set()
    for w, n in state.knowledge:
        p = bundle["points"][w + "/" + n]["point"]
        values.append(properties(source["worlds"][p["world"]])); epochs.add(p["epoch"])
    shared = set.intersection(*(set(v) for v in values))
    claims = {path: values[0][path] for path in sorted(shared) if all(canonical(v[path]) == canonical(values[0][path]) for v in values)}
    return {"status": "MODEL_CONDITIONAL", "claims": claims,
            "derived_predicates": "credentials/*/scope_for_task_permissions is native scope intersected with the permissions of registered task paths; it is NOT a statement of full native scope",
            "scope": {"account": source["account"], "caller": source["caller"], "source_digest": bundle["source_digest"],
                      "belief": refs_json(state.knowledge), "epochs": sorted(epochs), "remaining": state.remaining},
            "transcript_digest": digest(list(transcript)),
            "invalidated_by": ["unregistered observation", "source/catalog or caller change", "regime/epoch change", "approval withdrawal or budget/state change"],
            "meaning": "entailed by every surviving declared hypothesis; not universal provider attestation"}


def usable(evidence, bundle, state):
    current = contract(bundle, state)
    return evidence.get("status") == current["status"] == "MODEL_CONDITIONAL" and canonical(evidence.get("scope")) == canonical(current["scope"]) and canonical(evidence.get("claims")) == canonical(current["claims"])
