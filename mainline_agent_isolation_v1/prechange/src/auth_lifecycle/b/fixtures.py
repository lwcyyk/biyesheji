"""Synthetic development contracts. Evidence refs are fixture declarations, not websites."""
from copy import deepcopy
from itertools import product
from random import Random
from .model import SCHEMA


def op(interface, approval=None, approvals=0, requests=0):
    return dict(interface=interface, approval=approval, approvals=approvals, requests=requests)


def base(tasks):
    return {"schema": SCHEMA, "tasks": {t: {"account": "alice", "permissions": ["use"]} for t in tasks},
            "credentials": {}, "revocations": {}, "environments": {}, "paths": {},
            "scenarios": {"stop": {"local": [], "remote": [], "preserve": []}},
            "approved": ["issue", "revoke", "isolate", "delegate"],
            "budgets": {"approvals": 32, "requests": 64, "isolated_environments": 8, "units": 16}, "horizon": 8}


def grant(m, name, *, domain=None, scope=None, labels=None):
    m["credentials"][name] = {"account": "alice", "type": "synthetic_grant", "scope": scope or ["use"],
                              "token_labels": labels or [name + "-access", name + "-refresh"],
                              "issue": op("issue_" + name, "issue", 1, 1)}
    unit = domain or name
    if unit in m["revocations"]:m["revocations"][unit]["affects"].append(name)
    else:m["revocations"][unit] = {"affects": [name], "verified": True, "evidence": "synthetic-fixture:" + unit,
                                   "coverage": "all_material", "revoke": op("revoke_" + unit, "revoke", 0, 1)}


def env(m, name="broker", kind="broker", controlled=True):
    m["environments"][name] = {"kind": kind, "controlled": controlled,
                               "create": op("create_" + name, "isolate" if kind == "isolated" else None,
                                            1 if kind == "isolated" else 0, 0),
                               "stop": op("stop_" + name) if kind != "direct" else None}


def path(m, name, task, grants, environment="broker"):
    m["paths"][name] = {"task": task, "grants": grants, "environment": environment,
                       "delegate": op("delegate_" + name, "delegate")}


def local_only(n=2):
    tasks = [f"t{i}" for i in range(n)]; m = base(tasks); env(m); grant(m, "shared")
    for t in tasks:
        grant(m, t); path(m, t + "_shared", t, ["shared"]); path(m, t + "_own", t, [t])
    m["scenarios"]["stop"] = {"local": [tasks[0]], "remote": [], "preserve": tasks[1:]}
    return m


def static_groups():
    m = base(["a", "b", "c", "d"]); env(m, "direct", "direct")
    for g in ["all", "ab", "cd", "a", "b", "c", "d"]:grant(m, g)
    for t in m["tasks"]:
        for g in ["all", "ab" if t in "ab" else "cd", t]:path(m, t + "_" + g, t, [g], "direct")
    m["scenarios"] = {"ab": {"local": [], "remote": ["a", "b"], "preserve": ["c", "d"]},
                      "cd": {"local": [], "remote": ["c", "d"], "preserve": ["a", "b"]}}
    return m


def alternatives(mixed=False):
    m = base(["a", "b", "keep"]); env(m); grant(m, "a"); grant(m, "b")
    path(m, "a", "a", ["a"]); path(m, "b", "b", ["b"])
    if mixed:env(m, "sandbox", "isolated")
    e = "sandbox" if mixed else "broker"
    path(m, "keep_a", "keep", ["a"], e); path(m, "keep_b", "keep", ["b"], e)
    m["scenarios"] = {"end_a": {"local": ["b"], "remote": ["a"], "preserve": ["keep"]},
                      "end_b": {"local": ["a"], "remote": ["b"], "preserve": ["keep"]}}
    return m


def aliases():
    m = base(["a", "b"]); env(m)
    grant(m, "token_bundle_a", domain="account_root"); grant(m, "token_bundle_b", domain="account_root")
    path(m, "a", "a", ["token_bundle_a"]); path(m, "b", "b", ["token_bundle_b"])
    m["scenarios"]["stop"] = {"local": ["a"], "remote": [], "preserve": ["b"]}
    return m


def cases():
    yield "local_only_negative_control", local_only(), "FEASIBLE", 1
    yield "static_signature_negative_control", static_groups(), "FEASIBLE", 2
    yield "multiple_alternatives", alternatives(), "FEASIBLE", 2
    yield "mixed_environments", alternatives(True), "FEASIBLE", 2
    yield "token_aliases_G", aliases(), "FEASIBLE", 1
    m = aliases(); m["scenarios"]["stop"] = {"local": [], "remote": ["a"], "preserve": ["b"]}
    yield "shared_root_remote_conflict", m, "IMPOSSIBLE", None
    m = local_only(); m["budgets"]["approvals"] = 0
    yield "approval_budget", m, "IMPOSSIBLE", None
    m = aliases(); m["approved"].remove("issue")
    yield "missing_setup_approval", m, "IMPOSSIBLE", None
    m = aliases(); m["scenarios"]["stop"] = {"local": [], "remote": ["a", "b"], "preserve": []}; m["budgets"]["requests"] = 2
    yield "stop_request_budget", m, "IMPOSSIBLE", None
    m = aliases(); m["environments"]["broker"]["controlled"] = False
    yield "uncontrolled_entry", m, "IMPOSSIBLE", None
    m = aliases(); m["revocations"]["account_root"]["coverage"] = "refresh_only"
    yield "refresh_only_local_ok", m, "FEASIBLE", 1
    m = deepcopy(m); m["scenarios"]["stop"] = {"local": [], "remote": ["a", "b"], "preserve": []}
    yield "refresh_only_remote_fails", m, "IMPOSSIBLE", None
    m = aliases(); m["credentials"]["token_bundle_a"]["account"] = "mallory"
    yield "wrong_account", m, "IMPOSSIBLE", None
    m = base(["a"]); env(m); grant(m, "x", scope=["read"]); grant(m, "y", scope=["write"])
    m["tasks"]["a"]["permissions"] = ["read", "write"]; path(m, "joint", "a", ["x", "y"])
    m["scenarios"]["stop"]["remote"] = ["a"]
    yield "AND_support", m, "FEASIBLE", 2
    m = deepcopy(m); m["credentials"]["y"]["scope"] = ["read"]
    yield "scope_not_covered", m, "IMPOSSIBLE", None
    m = aliases(); m["revocations"]["fake"] = deepcopy(m["revocations"]["account_root"])
    yield "overlapping_native_units", m, "UNKNOWN", None
    m = aliases(); m["revocations"]["account_root"]["verified"] = False
    yield "unverified_native_contract", m, "UNKNOWN", None
    m = aliases(); m["horizon"] = 0
    yield "zero_stop_steps", m, "IMPOSSIBLE", None
    m = alternatives(True); m["budgets"]["isolated_environments"] = 0
    yield "isolation_budget", m, "IMPOSSIBLE", None
    m = aliases(); m["approved"].remove("revoke"); m["scenarios"]["stop"] = {"local": [], "remote": ["a", "b"], "preserve": []}
    yield "missing_revoke_approval", m, "IMPOSSIBLE", None
    m = aliases(); m["paths"] = {}
    yield "empty_path_catalog", m, "UNKNOWN", None
    yield "eight_task_boundary", local_only(8), "FEASIBLE", 1


def finite_models():
    """384 explicit parameter tuples; not an exhaustive universe of auth contracts."""
    for mode, preserve, coverage, approval, budget, horizon in product(
            ["local", "remote"], [False, True], ["all_material", "refresh_only"],
            ["both", "issue_only", "revoke_only", "neither"], [1, 3, 8], [0, 1, 2, 3]):
        m = local_only(); m["horizon"] = horizon; m["budgets"]["requests"] = budget
        m["approved"] = ["delegate", "isolate"] + (["issue"] if approval in {"both", "issue_only"} else []) + (["revoke"] if approval in {"both", "revoke_only"} else [])
        for r in m["revocations"].values():r["coverage"] = coverage
        m["scenarios"]["stop"] = {"local": ["t0"] if mode == "local" else [],
                                   "remote": ["t0"] if mode == "remote" else [], "preserve": ["t1"] if preserve else []}
        name = f"{mode}-{int(preserve)}-{coverage}-{approval}-q{budget}-h{horizon}"
        yield name, m


def structural_models(count=96, seed=20261102):
    """Seeded structural fuzzing, explicitly NOT exhaustive or a study sample."""
    rng = Random(seed)
    for index in range(count):
        m = base(["a", "b", "c"])
        env(m, "broker"); env(m, "sandbox", "isolated"); env(m, "direct", "direct")
        for g in ["x", "y", "z"]:grant(m, g, domain="x" if g == "y" and rng.randrange(2) else g)
        for u in m["revocations"].values():
            if rng.randrange(6) == 0:u["coverage"] = "refresh_only"
        for t in m["tasks"]:
            for i in range(2):path(m, t + str(i), t, rng.sample(["x", "y", "z"], rng.choice([1, 1, 2])), rng.choice(["broker", "sandbox", "direct"]))
        m["scenarios"] = {}
        for i in range(2):
            stop = rng.choice(list(m["tasks"])); remote = rng.choice([True, False])
            m["scenarios"][str(i)] = {"local": [] if remote else [stop], "remote": [stop] if remote else [],
                                      "preserve": [t for t in m["tasks"] if t != stop and rng.randrange(2)]}
        m["horizon"] = rng.choice([1, 2, 3, 4]); m["budgets"]["approvals"] = rng.choice([2, 3, 4])
        m["budgets"]["requests"] = rng.choice([3, 5, 8]); m["budgets"]["isolated_environments"] = rng.choice([0, 1])
        yield f"structural-{seed}-{index:03d}", m
