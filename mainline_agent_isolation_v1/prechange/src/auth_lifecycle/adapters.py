"""Executable table-backed L0 adapter. Not a website/OAuth integration.

The actual hidden state is private to the fixture adapter. Policy selection sees
only observations; choosing an outcome index is an explicit test-harness hook.
"""
from copy import deepcopy
from .schema import ModelError, validate, digest
from ._reference_kernel import expand


class TableAdapter:
    def __init__(self, spec, actual, operations=None):
        self._spec = deepcopy(spec); validate(self._spec)
        self.contract_digest = digest(self._spec)
        self._actual = tuple(actual)
        if self._actual[0] not in spec["worlds"] or self._actual[1] not in spec["worlds"][self._actual[0]]["states"]:
            raise ModelError("invalid adapter initial state")
        self.operations = set(operations if operations is not None else [a["operation"] for a in spec["actions"].values()])
        self.history = []

    def execute(self, action_id, *, outcome_index=0):
        action = self._spec["actions"][action_id]
        if action["operation"] not in self.operations:raise ModelError("unbound concrete operation")
        _, errors = expand(self._spec, frozenset([self._actual]), action_id)
        if errors:raise ModelError("adapter denied: " + ",".join(errors))
        w, s = self._actual
        alternatives = self._spec["worlds"][w]["states"][s]["transitions"][action_id]
        if type(outcome_index) is not int or not 0 <= outcome_index < len(alternatives):raise ModelError("invalid harness outcome")
        outcome = alternatives[outcome_index]
        self._actual = tuple(outcome["target"])
        self.history.append({"action": action_id, "observation": outcome["observation"],
                             "effects": deepcopy(outcome["effects"]), "delta": deepcopy(outcome["delta"])})
        return outcome["observation"]

    def audit_state(self):
        """Scorer-only API. Never passed to the candidate solver."""
        w, s = self._actual
        return deepcopy(self._spec["worlds"][w]["states"][s])
