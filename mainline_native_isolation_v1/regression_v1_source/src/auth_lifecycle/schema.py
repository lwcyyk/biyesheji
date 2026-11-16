"""Shared data contract only; search/evaluation algorithms live elsewhere."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
import hashlib
import json

MAX_HORIZON = 8
MAX_TASKS = 4
Ref = tuple[str, str]


class Status(str, Enum):
    FEASIBLE = "FEASIBLE"
    IMPOSSIBLE = "IMPOSSIBLE"  # only the specified finite model and horizon
    INCONCLUSIVE = "INCONCLUSIVE"  # computational search unfinished
    UNKNOWN = "UNKNOWN"  # invalid/empty/out-of-model knowledge


class ModelError(ValueError):
    pass


@dataclass(frozen=True)
class State:
    knowledge: frozenset[Ref]
    remaining: int
    boundary: str | None = None


@dataclass
class Result:
    status: Status
    reason: str
    explored: int = 0
    policy: dict | None = None
    refutation: dict | None = None


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def digest(value) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def refs_json(refs) -> list[list[str]]:
    return [list(x) for x in sorted(refs)]


def fail(condition, message):
    if not condition:
        raise ModelError(message)


def strings(value, where):
    fail(isinstance(value, list), f"{where}: list required")
    fail(all(isinstance(x, str) and x for x in value), f"{where}: nonempty strings required")
    fail(len(set(value)) == len(value), f"{where}: duplicates")


def integer(value, where):
    fail(type(value) is int and value >= 0, f"{where}: nonnegative integer required")


def ref(value, spec):
    fail(isinstance(value, (list, tuple)) and len(value) == 2, "invalid state reference")
    w, s = value
    fail(isinstance(w, str) and isinstance(s, str), "invalid state reference types")
    fail(w in spec["worlds"] and s in spec["worlds"][w]["states"], f"unknown state {value}")
    return w, s


def validate(spec: dict) -> None:
    """Reject malformed models, inconsistent delta ledgers and silent authority creation.

    Empty initial knowledge is syntactically representable for boundary testing;
    every reasoning entry point must return UNKNOWN for it, never vacuous success.
    """
    try:
        canonical(spec)  # Require a finite JSON-serializable contract, no NaN/cycles.
        fail(spec["schema"] == "auth-lifecycle-l0/1", "unsupported schema")
        strings(spec["tasks"], "tasks")
        fail(0 < len(spec["tasks"]) <= MAX_TASKS, "task bound exceeded")
        integer(spec["horizon"], "horizon")
        fail(spec["horizon"] <= MAX_HORIZON, "horizon bound exceeded")
        fail(isinstance(spec["worlds"], dict) and spec["worlds"], "world universe must be nonempty")
        fail(isinstance(spec["actions"], dict), "actions must be a mapping")
        strings(spec["goal"]["facts"], "goal facts")
        fail(isinstance(spec["goal"]["account"], str) and spec["goal"]["account"], "goal account")
        strings(spec["safety"]["forbidden_facts"], "forbidden facts")
        strings(spec["safety"]["preserve_capabilities"], "protected capabilities")
        for aid, action in spec["actions"].items():
            fail(isinstance(aid, str) and aid, "action identifier")
            fail(action["task"] in spec["tasks"], f"task:{aid}")
            for field in ["account", "approval", "operation"]:
                fail(isinstance(action[field], str) and action[field], f"{field}:{aid}")
            fail(action["kind"] in {"probe", "control", "wait"}, "unknown action kind")
            strings(action["requires"], f"requires:{aid}")
            fail(isinstance(action["cost"], dict), f"cost:{aid}")
            for key, amount in action["cost"].items():
                fail(isinstance(key, str) and key, "budget key")
                integer(amount, f"cost:{aid}:{key}")
            fail(isinstance(action["independent"], list), "independence list")
            for pair in action["independent"]:
                fail(isinstance(pair, list) and len(pair) == 2, "independence pair")
                fail(all(isinstance(x, str) and x for x in pair), "independence names")
        for wid, world in spec["worlds"].items():
            fail(isinstance(wid, str) and wid and isinstance(world["semantics"], str), "world identifier")
            fail(isinstance(world["native_roots"], dict), "native roots")
            fail(all(isinstance(k, str) and k and isinstance(v, str) and v for k, v in world["native_roots"].items()), "native root identifiers")
            fail(isinstance(world["states"], dict) and world["states"], "empty world state space")
            for sid, node in world["states"].items():
                fail(isinstance(sid, str) and sid, "state identifier")
                fail(isinstance(node["account"], str) and node["account"], "state account")
                for field in ["facts", "approvals", "obligations", "capabilities"]:
                    strings(node[field], f"{wid}/{sid}/{field}")
                fail(isinstance(node["budget"], dict), "budget mapping")
                for key, amount in node["budget"].items():
                    fail(isinstance(key, str) and key, "state budget key")
                    integer(amount, f"budget:{wid}/{sid}/{key}")
                fail(isinstance(node["transitions"], dict), "transition mapping")
        fail(isinstance(spec["initial"], list), "initial list")
        initial = [ref(x, spec) for x in spec["initial"]]
        fail(len(set(initial)) == len(initial), "duplicate initial state")
        for wid, world in spec["worlds"].items():
            for sid, node in world["states"].items():
                for aid, edges in node["transitions"].items():
                    fail(aid in spec["actions"] and isinstance(edges, list), "transition action")
                    action = spec["actions"][aid]
                    # Empty edges intentionally denote unavailable native operation.
                    for edge in edges:
                        fail(isinstance(edge["observation"], str) and edge["observation"], "observation required")
                        tw, ts = ref(edge["target"], spec)
                        target = spec["worlds"][tw]["states"][ts]
                        fail(target["account"] == node["account"], "silent account migration")
                        strings(edge["effects"], "effect references")
                        delta = edge["delta"]
                        for field in ["facts", "capabilities", "obligations"]:
                            add, remove = delta[field]["add"], delta[field]["remove"]
                            strings(add, f"{field}.add"); strings(remove, f"{field}.remove")
                            fail(set(remove) <= set(node[field]), "removing absent state")
                            fail(not (set(add) & set(remove)), "ambiguous state delta")
                            fail(set(target[field]) == (set(node[field]) - set(remove)) | set(add), f"unaccounted {field} delta")
                        strings(delta["withdraw_approvals"], "withdrawals")
                        fail(set(delta["withdraw_approvals"]) <= set(node["approvals"]), "unknown withdrawal")
                        fail(set(target["approvals"]) == set(node["approvals"]) - set(delta["withdraw_approvals"]), "silent approval issuance")
                        fail(set(target["budget"]) == set(node["budget"]), "budget domain changed")
                        fail(set(action["cost"]) <= set(node["budget"]), "unknown action budget")
                        fail(isinstance(delta["external_debit"], dict), "external debit mapping")
                        fail(set(delta["external_debit"]) <= set(node["budget"]), "unknown debit budget")
                        for amount in delta["external_debit"].values():integer(amount, "external debit")
                        for key, old in node["budget"].items():
                            expected = old - action["cost"].get(key, 0) - delta["external_debit"].get(key, 0)
                            fail(target["budget"][key] == expected and expected >= 0, "unaccounted budget delta")
                        if action["kind"] == "probe":
                            for cap in delta["capabilities"]["add"]:
                                fail(f"close:{cap}" in target["obligations"], "probe capability without strict obligation")
                        for cap in delta["capabilities"]["remove"]:
                            fail(f"close:{cap}" not in target["obligations"], "closed capability with unresolved close obligation")
                        fail(not any(x.startswith("close:") and x[6:] not in node["capabilities"] for x in node["obligations"]), "dangling close obligation")
    except (KeyError, TypeError, AttributeError, ValueError, RecursionError) as exc:
        raise ModelError(f"malformed model: {exc}") from exc


def prepare(spec, knowledge=None, horizon=None, boundary=None):
    data = deepcopy(spec)
    validate(data)
    r = data["horizon"] if horizon is None else horizon
    integer(r, "remaining horizon")
    fail(r <= MAX_HORIZON, "remaining horizon bound exceeded")
    fail(boundary is None or (isinstance(boundary, str) and bool(boundary)), "invalid boundary marker")
    values = data["initial"] if knowledge is None else knowledge
    k = frozenset(ref(x, data) for x in values)
    return data, State(k, r, boundary)
