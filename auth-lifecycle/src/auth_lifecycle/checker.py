"""Independent local proof checking, not candidate regeneration.

Only schema + the independent raw reference interpreter are imported. Proofs
cannot choose a hidden world as an observation or omit allowed actions/results.
"""
from dataclasses import dataclass
from .schema import ModelError, canonical, digest, prepare, refs_json
from ._reference_kernel import expand, is_goal, is_safe


@dataclass
class Check:
    verdict: str
    reason: str
    nodes: int = 0
    claim: str | None = None


class Invalid(Exception):
    pass


class Limit(Exception):
    pass


def _require(test, message):
    if not test:raise Invalid(message)


def _header(proof, belief, r):
    _require(isinstance(proof, dict), "proof node must be an object")
    _require(proof.get("belief") == refs_json(belief), "belief mismatch or hidden-world branching")
    _require(type(proof.get("remaining")) is int and proof["remaining"] == r, "remaining-step mismatch")


def check_policy(spec, policy, *, knowledge=None, horizon=None, node_limit=100_000):
    count = 0
    try:
        data, state = prepare(spec, knowledge, horizon)
        _require(bool(state.knowledge), "empty knowledge cannot certify success")
        _require(type(node_limit) is int and node_limit >= 0, "invalid checking limit")

        def walk(proof, belief, r):
            nonlocal count
            if count >= node_limit:raise Limit()
            count += 1; _header(proof, belief, r)
            if proof.get("kind") == "done":
                _require(is_goal(data, belief), "false terminal or unresolved strict obligation")
                return
            _require(proof.get("kind") == "act" and r > 0, "invalid action or exhausted horizon")
            groups, errors = expand(data, belief, proof.get("action"))
            _require(not errors and bool(groups), "unauthorized, unsafe, or empty transition")
            children = proof.get("children")
            _require(isinstance(children, dict) and set(children) == set(groups), "missing or invented observation branch")
            for observation, child_belief in groups.items():walk(children[observation], child_belief, r - 1)
        walk(policy, state.knowledge, state.remaining)
        return Check("ACCEPTED", "all branches independently checked", count, "bounded_feasible_policy")
    except Limit:return Check("INCONCLUSIVE", "checking limit", count)
    except (Invalid, ModelError, KeyError, TypeError, AttributeError, RecursionError) as exc:
        return Check("REJECTED", str(exc), count)


def check_impossibility(spec, certificate, *, horizon=None, node_limit=100_000):
    count = 0
    try:
        data, root = prepare(spec, horizon=horizon)
        _require(bool(root.knowledge), "empty knowledge is UNKNOWN, not impossibility")
        _require(type(node_limit) is int and node_limit >= 0, "invalid checking limit")
        _require(certificate["schema"] == "auth-lifecycle-certificate/1", "certificate version")
        _require(certificate["model_digest"] == digest(data), "model digest mismatch")
        _require(canonical(certificate["query"]) == canonical({"initial": refs_json(root.knowledge), "horizon": root.remaining}), "query mismatch")
        scope = certificate["scope"]
        _require(scope in {"bounded_policy_impossible", "no_common_immediate_completion"}, "unknown scope")
        r = root.remaining if scope == "bounded_policy_impossible" else 1
        _require(root.remaining >= r, "certificate exceeds query horizon")
        ctx = certificate["context"]; names = ctx["world_subset"]
        _require(isinstance(names, list) and names and names == sorted(set(names)), "invalid core worlds")
        _require(set(names) <= {w for w, _ in root.knowledge}, "core not subset of initial worlds")
        k = frozenset(point for point in root.knowledge if point[0] in names)
        _require(ctx["root_belief"] == refs_json(k) and type(ctx["horizon"]) is int and ctx["horizon"] == r, "core initial states mismatch")
        for field in ["worlds", "actions", "goal", "safety"]:
            _require(canonical(ctx[field]) == canonical(data[field]), f"tampered certificate {field}")
        required = ["approval", "account", "budget", "requires", "independence", "successors", "safe", "goal", "strict_obligations", "remaining_steps"]
        _require(ctx["constraint_refs"] == required, "missing constraint references")
        _require(certificate.get("core_minimality") == "not_claimed", "unverified minimality claim")

        def reject_tree(proof, belief, remaining):
            nonlocal count
            if count >= node_limit:raise Limit()
            count += 1; _header(proof, belief, remaining)
            _require(not is_goal(data, belief), "a goal state cannot certify impossibility")
            kind = proof.get("kind")
            if kind == "unsafe":
                _require(any(not is_safe(data, x) for x in belief), "false unsafe leaf"); return
            if kind == "horizon":
                _require(remaining == 0, "premature horizon leaf"); return
            _require(kind == "all_actions_fail" and remaining > 0, "invalid refutation kind")
            entries = proof.get("actions")
            _require(isinstance(entries, dict) and set(entries) == set(data["actions"]), "refutation omits action")
            for aid, entry in entries.items():
                groups, errors = expand(data, belief, aid)
                if errors:
                    _require(entry.get("kind") == "blocked" and entry.get("constraint_refs") == errors, "false blocking reason")
                else:
                    _require(entry.get("kind") == "losing_observation", "legal action has no losing branch")
                    observation = entry.get("observation")
                    _require(observation in groups, "invented counter-observation")
                    reject_tree(entry["child"], groups[observation], remaining - 1)
        reject_tree(certificate["proof"], k, r)
        claim = "no_common_one_step_completion" if scope == "no_common_immediate_completion" else f"no_uniform_observation_policy_within_{r}_steps"
        return Check("ACCEPTED", "complete bounded refutation checked; not unbounded impossibility", count, claim)
    except Limit:return Check("INCONCLUSIVE", "checking limit", count)
    except (Invalid, ModelError, KeyError, TypeError, AttributeError, RecursionError, ValueError) as exc:
        return Check("REJECTED", str(exc), count)
