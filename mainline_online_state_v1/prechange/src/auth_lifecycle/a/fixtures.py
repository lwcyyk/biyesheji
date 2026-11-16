"""Declared synthetic service regimes; never user accounts or provider attestations."""
from copy import deepcopy
from itertools import product
from ..b import fixtures as b


def outcome(world, observation, sessions=(), withdraw=()):
    return {"observation": observation, "to_world": world, "sessions": list(sessions), "withdraw": list(withdraw)}


def probe(source, name, observations, *, requests=1, sessions=(), attempts=1, caller=None):
    source["probes"][name] = {"operation": b.op("inspect_" + name, "probe", 0, requests), "phase": "before",
        "caller": caller or source["caller"], "scope": ["/revocations", "/credentials"],
        "outcomes": {w: [[outcome(w, observations[w], sessions)] for _ in range(attempts)] for w in source["worlds"]}}


def cleanup(source, *, opaque=False):
    session = "opaque:verification" if opaque else "verification"
    source["cleanups"]["sessions"] = {"operation": b.op("cleanup_session_root", "cleanup", 0, 1),
                                       "mode": "account_root" if opaque else "known_handle", "sessions": [session]}


def acquisition(*, nuisance=1, requests=8, horizon=4):
    template = b.base(["job", "keep"]); b.env(template)
    for g in ["x", "y", "z"]:b.grant(template, g)
    b.path(template, "job_x", "job", ["x"]); b.path(template, "job_y", "job", ["y"]); b.path(template, "keep_z", "keep", ["z"])
    template["scenarios"] = {"stop": {"local": [], "remote": ["job"], "preserve": ["keep"]}}
    template["approved"] += ["probe", "cleanup"]
    template["budgets"].update(requests=requests, approvals=8)
    worlds = {}
    for mode in range(2):
        for noise in range(nuisance):
            m = deepcopy(template); m["revocations"]["x" if mode else "y"]["coverage"] = "refresh_only"
            m["credentials"]["z"]["scope"] = ["use", f"optional-{noise}"]
            worlds[f"m{mode}n{noise}"] = m
    source = {"schema": "auth-lifecycle-a/1", "account": "alice", "caller": "agent-client",
              "worlds": worlds, "initial": list(worlds), "scenario": "stop", "probes": {}, "cleanups": {}, "faults": {},
              "budget": {"requests": requests, "approvals": 8}, "horizon": horizon}
    probe(source, "z_native", {w: w[:2] for w in worlds})
    if nuisance > 1:probe(source, "a_scope", {w: w[2:] for w in worlds})
    return source


def side_effect(*, opaque=False, clean=True):
    s = acquisition(horizon=4); session = "opaque:verification" if opaque else "verification"
    for w in s["worlds"]:s["probes"]["z_native"]["outcomes"][w][0][0]["sessions"] = [session]
    if clean:cleanup(s, opaque=opaque)
    return s


def cases():
    yield "simple_acquisition", acquisition(), "FEASIBLE"
    yield "irrelevant_scope_negative_control", acquisition(nuisance=2), "FEASIBLE"
    yield "session_side_effect", side_effect(), "FEASIBLE"
    yield "opaque_handle_root_cleanup", side_effect(opaque=True), "FEASIBLE"
    yield "opaque_handle_no_cleanup", side_effect(opaque=True, clean=False), "IMPOSSIBLE"
    s = acquisition(); probe(s, "a_unsafe", {w: w[:2] for w in s["worlds"]}, sessions=["opaque:verification"])
    yield "unsafe_query_filtered", s, "FEASIBLE"
    s = acquisition()
    for w in s["worlds"]:s["probes"]["z_native"]["outcomes"][w][0][0]["observation"] = "UNKNOWN"
    yield "unknown_not_success", s, "IMPOSSIBLE"
    s = acquisition()
    for w in s["worlds"]:s["probes"]["z_native"]["outcomes"][w][0][0]["observation"] = "active:false:caller-restricted"
    yield "query_scoped_active", s, "IMPOSSIBLE"
    s = acquisition(); s["probes"]["z_native"]["caller"] = "different-client"
    yield "wrong_query_caller", s, "IMPOSSIBLE"
    s = acquisition(requests=3)
    yield "shared_budget_insufficient", s, "IMPOSSIBLE"
    s = acquisition(); probe(s, "a_withdraws", {w: w[:2] for w in s["worlds"]})
    for w in s["worlds"]:s["probes"]["a_withdraws"]["outcomes"][w][0][0]["withdraw"] = ["revoke"]
    yield "approval_withdrawal_filtered", s, "FEASIBLE"
    s = acquisition(horizon=5); cleanup(s, opaque=True)
    for w in s["worlds"]:
        s["probes"]["z_native"]["outcomes"][w] = [
            [outcome(w, "LOST", ["opaque:verification"]), outcome(w, "LOST")], [outcome(w, w[:2])]]
    yield "lost_probe_unknown_handle", s, "FEASIBLE"
    s = acquisition(horizon=4)
    for unit in ["x", "y"]:
        s["faults"]["stop:revoke:" + unit] = [[{"observation": "LOST", "applied": True, "withdraw": []}, {"observation": "LOST", "applied": False, "withdraw": []}],
                                               [{"observation": "ok", "applied": True, "withdraw": []}]]
    yield "lost_stop_ambiguous_effect", s, "FEASIBLE"
    s = side_effect(opaque=True); s["horizon"] = 5
    s["faults"]["cleanup:sessions"] = [[{"observation": "LOST", "applied": True, "withdraw": []}, {"observation": "LOST", "applied": False, "withdraw": []}],
                                        [{"observation": "ok", "applied": True, "withdraw": []}]]
    yield "lost_cleanup_ambiguous_effect", s, "FEASIBLE"
    s = acquisition(horizon=3)
    for m in s["worlds"].values():
        m["paths"].pop("job_x"); m["paths"].pop("job_y")
        b.path(m, "job_and", "job", ["x", "y"])
    s["probes"]["z_native"]["phase"] = "after"
    yield "probe_after_configure", s, "FEASIBLE"
    s = acquisition()
    for w in s["worlds"]:
        target = "m1n0"; s["probes"]["z_native"]["outcomes"][w][0] = [dict(outcome(target, "observable-regime-change"))]
    yield "observable_regime_change", s, "FEASIBLE"
    s = acquisition(nuisance=2)
    for w in s["worlds"]:s["worlds"][w]["scenarios"]["stop"] = {"local": ["job"], "remote": [], "preserve": ["keep"]}
    yield "local_only_no_learning_negative_control", s, "FEASIBLE"
    s = acquisition(); s["initial"] = []
    yield "empty_K", s, "UNKNOWN"
    s = acquisition()
    for w in s["worlds"]:
        m = s["worlds"][w]; b.grant(m, "fallback"); m["credentials"]["fallback"]["issue"]["requests"] = 3
        b.path(m, "job_fallback", "job", ["fallback"])
    yield "joint_planning_cheaper_than_early_configure", s, "FEASIBLE"


def finite_models():
    """48 parameter combinations, all explicitly recorded; not all service models."""
    for noise, budget, h, effect in product([1, 2], [3, 4, 6], [2, 3, 4, 5], [False, True]):
        s = acquisition(nuisance=noise, requests=budget, horizon=h)
        if effect:
            cleanup(s)
            for w in s["worlds"]:s["probes"]["z_native"]["outcomes"][w][0][0]["sessions"] = ["verification"]
        yield f"n{noise}-q{budget}-h{h}-effect{int(effect)}", s
