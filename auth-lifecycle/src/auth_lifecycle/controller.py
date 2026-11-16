"""L0 bounded dispatch gate; never selects an action from hidden true state."""
from dataclasses import dataclass
from .schema import State, Status, digest, prepare, refs_json
from ._reference_kernel import expand, is_goal
from .reference import solve as reference_solve


@dataclass
class Dispatch:
    status: str
    reason: str
    observation: str | None = None


class BoundedController:
    def __init__(self, spec):
        self.spec, self.state = prepare(spec)
        self.events = []
        self.pending_action = None
        self.pending_context = None
        self.last_valid_state = self.state

    def step(self, action, adapter, *, outcome_index=0, node_limit=100_000):
        before = self.state
        if before.boundary or not before.knowledge:return Dispatch("UNKNOWN", before.boundary or "empty_knowledge")
        if is_goal(self.spec, before.knowledge):return Dispatch("COMPLETED", "already_terminal")
        if before.remaining == 0:return Dispatch("REJECTED", "horizon_exhausted")
        if getattr(adapter,"contract_digest",None) != digest(self.spec):return Dispatch("UNKNOWN", "adapter_contract_mismatch")
        groups, reasons = expand(self.spec, before.knowledge, action)
        if reasons:return Dispatch("REJECTED", ",".join(reasons))
        # Independent bounded successor checks, not a candidate-generated permission.
        for k in groups.values():
            answer = reference_solve(self.spec, knowledge=k, horizon=before.remaining-1, node_limit=node_limit)
            if answer.status in {Status.UNKNOWN, Status.INCONCLUSIVE}:return Dispatch(answer.status.value, answer.reason)
            if answer.status is not Status.FEASIBLE:return Dispatch("REJECTED", "successor_not_bounded_winning")
        self.pending_action = action
        self.pending_context = {"action":action,"model_digest":digest(self.spec),
            "belief_before":refs_json(before.knowledge),"remaining_before":before.remaining,
            "possible_successors":{o:refs_json(k) for o,k in groups.items()},
            "unmodelled_effects_possible":False}
        try:
            observed = adapter.execute(action, outcome_index=outcome_index)
        except Exception as exc:
            self.pending_context["unmodelled_effects_possible"] = True
            self.state = State(frozenset(), before.remaining-1, "adapter_exception_result_unknown")
            self.events.append({"action":action,"remaining_before":before.remaining,"remaining_after":self.state.remaining,
                                "boundary":self.state.boundary,"exception_type":type(exc).__name__})
            return Dispatch("UNKNOWN", self.state.boundary)
        if not isinstance(observed,str) or observed not in groups:
            self.pending_context["unmodelled_effects_possible"] = True
            self.state = State(frozenset(), before.remaining-1, "out_of_model_observation")
            self.events.append({"action":action,"remaining_before":before.remaining,"remaining_after":self.state.remaining,
                                "boundary":self.state.boundary})
            return Dispatch("UNKNOWN", self.state.boundary)
        self.state = State(groups[observed], before.remaining-1)
        self.last_valid_state = self.state
        self.pending_action = None
        self.pending_context = None
        self.events.append({"action":action,"observation":observed,"remaining_before":before.remaining,
                            "remaining_after":self.state.remaining})
        return Dispatch("COMPLETED" if is_goal(self.spec,self.state.knowledge) else "CONTINUE", "bounded_transition", observed)
