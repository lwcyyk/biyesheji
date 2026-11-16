"""Shared syntax only. No feasibility, plan, cost or configuration search here."""
from copy import deepcopy
from dataclasses import dataclass, field
from ..schema import ModelError, canonical, digest, fail, integer, strings

SCHEMA = "auth-lifecycle-b/1"
CONSTRAINTS = ["catalog.coverage", "native.partition", "native.evidence", "native.scope",
               "account.binding", "approval.membership", "budget.approvals", "budget.requests",
               "budget.isolation", "budget.units", "setup.order", "stop.local", "stop.remote",
               "preserve.every_prefix", "horizon", "support.all_alternatives"]


def operation(value, where):
    fail(isinstance(value, dict), where)
    fail(set(value) == {"interface", "approval", "approvals", "requests"}, where + ": fields")
    fail(isinstance(value["interface"], str) and value["interface"], where + ": interface")
    fail(value["approval"] is None or isinstance(value["approval"], str) and value["approval"], where + ": approval")
    integer(value["approvals"], where + ": approvals")
    integer(value["requests"], where + ": requests")
    fail(value["approval"] is not None or value["approvals"] == 0, where + ": unbound approval charge")


def prepare(spec):
    try:
        canonical(spec)
        fail(set(spec) == {"schema", "tasks", "credentials", "revocations", "environments", "paths",
                           "scenarios", "approved", "budgets", "horizon"}, "model fields")
        fail(spec["schema"] == SCHEMA, "schema")
        for name, bound in [("tasks", 8), ("credentials", 16), ("revocations", 16),
                            ("environments", 16), ("paths", 16), ("scenarios", 16)]:
            fail(isinstance(spec[name], dict) and 0 < len(spec[name]) <= bound, name + ": finite nonempty catalog required")
            fail(all(isinstance(k, str) and k and ":" not in k for k in spec[name]), name + ": invalid identifier")
        integer(spec["horizon"], "horizon"); fail(spec["horizon"] <= 8, "horizon > 8")
        strings(spec["approved"], "approved")
        fail(set(spec["budgets"]) == {"approvals", "requests", "isolated_environments", "units"}, "budget fields")
        for k, v in spec["budgets"].items():integer(v, "budgets." + k)
        for t, x in spec["tasks"].items():
            fail(set(x) == {"account", "permissions"}, "task fields")
            fail(isinstance(x["account"], str) and x["account"], "task account")
            strings(x["permissions"], t + ": permissions"); fail(bool(x["permissions"]), "empty task permissions")
        for g, x in spec["credentials"].items():
            fail(set(x) == {"account", "type", "scope", "token_labels", "issue"}, "credential fields")
            fail(isinstance(x["account"], str) and x["account"], "credential account")
            fail(isinstance(x["type"], str) and x["type"], "credential type")
            strings(x["scope"], g + ": scope"); strings(x["token_labels"], g + ": labels")
            operation(x["issue"], "issue." + g)
        members = []
        for u, x in spec["revocations"].items():
            fail(set(x) == {"affects", "verified", "evidence", "coverage", "revoke"}, "native fields")
            strings(x["affects"], u + ": affects")
            fail(x["affects"] and set(x["affects"]) <= set(spec["credentials"]), "native footprint")
            fail(x["verified"] is True and isinstance(x["evidence"], str) and bool(x["evidence"]), "unverified native semantics")
            fail(x["coverage"] in {"all_material", "refresh_only"}, "native coverage")
            if x["revoke"] is not None:operation(x["revoke"], "revoke." + u)
            members.extend(x["affects"])
        fail(sorted(members) == sorted(spec["credentials"]), "native footprints must partition credentials; overlapping/correlated units unsupported")
        for e, x in spec["environments"].items():
            fail(set(x) == {"kind", "controlled", "create", "stop"}, "environment fields")
            fail(x["kind"] in {"broker", "isolated", "direct"} and type(x["controlled"]) is bool, "environment kind/control")
            operation(x["create"], "create." + e)
            if x["stop"] is not None:operation(x["stop"], "stop." + e)
        for p, x in spec["paths"].items():
            fail(set(x) == {"task", "grants", "environment", "delegate"}, "path fields")
            fail(x["task"] in spec["tasks"] and x["environment"] in spec["environments"], "path binding")
            strings(x["grants"], p + ": grants")
            fail(x["grants"] and set(x["grants"]) <= set(spec["credentials"]), "empty or unknown AND support")
            operation(x["delegate"], "delegate." + p)
        for s, x in spec["scenarios"].items():
            fail(set(x) == {"local", "remote", "preserve"}, "scenario fields")
            for k in x:
                strings(x[k], s + ": " + k); fail(set(x[k]) <= set(spec["tasks"]), "scenario unknown task")
            fail(not (set(x["preserve"]) & (set(x["local"]) | set(x["remote"]))), "stop/preserve conflict")
        return deepcopy(spec)
    except (KeyError, TypeError, AttributeError, ValueError, RecursionError) as exc:
        raise ModelError(str(exc)) from exc


@dataclass
class Result:
    status: str
    reason: str
    configuration: list | None = None
    delivery: dict | None = None
    metrics: dict | None = None
    optimal: bool = False
    stats: dict = field(default_factory=dict)
    candidates: list = field(default_factory=list)


class Cutoff(Exception):
    pass


class Work:
    def __init__(self, limit=1_000_000):
        if type(limit) is not int or limit < 0:raise ModelError("invalid work limit")
        self.limit = limit
        self.counts = {}

    def tick(self, kind):
        if sum(self.counts.values()) >= self.limit:raise Cutoff()
        self.counts[kind] = self.counts.get(kind, 0) + 1
