"""Source contract syntax; the fixed B package is a dependency, never rewritten."""
from copy import deepcopy
from ..schema import ModelError, canonical, digest, fail, integer, strings
from ..b.model import prepare as prepare_b, operation


def pointers(obj, prefix=""):
    if isinstance(obj, dict):
        for k, v in sorted(obj.items()):yield from pointers(v, prefix + "/" + k)
    else:yield prefix, obj


def properties(contract):
    """Public goal-relevant projection, available to A1, B-A and feedback-off."""
    paths = contract["paths"]; grants = {g for p in paths.values() for g in p["grants"]}
    envs = {p["environment"] for p in paths.values()}
    needed = {g: {permission for p in paths.values() if g in p["grants"] for permission in contract["tasks"][p["task"]]["permissions"]} for g in grants}
    fields = {"tasks": contract["tasks"], "scenarios": contract["scenarios"],
              "credentials": {g: {"account": contract["credentials"][g]["account"],
                                  "scope_for_task_permissions": sorted(set(contract["credentials"][g]["scope"]) & needed[g])} for g in sorted(grants)},
              "revocations": {u: {k: v for k, v in x.items() if k in {"affects", "coverage"}} for u, x in contract["revocations"].items() if grants.intersection(x["affects"])},
              "environments": {e: {"controlled": contract["environments"][e]["controlled"]} for e in sorted(envs)}}
    return dict(pointers(fields))


def prepare(source):
    try:
        canonical(source)
        fail(set(source) == {"schema", "account", "caller", "worlds", "initial", "scenario", "probes", "cleanups", "faults", "budget", "horizon"}, "A source fields")
        fail(source["schema"] == "auth-lifecycle-a/1", "A schema")
        for f in ["account", "caller", "scenario"]:fail(isinstance(source[f], str) and source[f], f)
        fail(isinstance(source["worlds"], dict) and 0 < len(source["worlds"]) <= 8, "world bound")
        strings(source["initial"], "initial"); fail(set(source["initial"]) <= set(source["worlds"]), "initial world")
        integer(source["horizon"], "horizon"); fail(source["horizon"] <= 8, "horizon bound")
        fail(set(source["budget"]) == {"requests", "approvals"}, "budget fields")
        for v in source["budget"].values():integer(v, "budget")
        common = None
        for w, b in source["worlds"].items():
            fail(isinstance(w, str) and w and "/" not in w, "world id"); prepare_b(b)
            fail(len(b["tasks"]) <= 4 and len(b["paths"]) <= 6, "joint finite profile bound")
            fail(source["scenario"] in b["scenarios"], "scenario missing")
            fail(all(x["account"] == source["account"] for x in b["tasks"].values()), "task account boundary")
            fail(b["budgets"]["requests"] == source["budget"]["requests"] and b["budgets"]["approvals"] == source["budget"]["approvals"], "B/shared budget mismatch")
            # All hypotheses have the same proposed operations, recipients and price list.
            # Effects/scopes/control semantics may differ. No privileged variant catalog.
            catalog = {"tasks": b["tasks"], "paths": b["paths"], "scenarios": b["scenarios"],
                       "issues": {g: x["issue"] for g, x in b["credentials"].items()},
                       "env": {e: {k: x[k] for k in ["kind", "create", "stop"]} for e, x in b["environments"].items()},
                       "revoke": {u: x["revoke"] for u, x in b["revocations"].items()},
                       "approved": b["approved"], "budgets": b["budgets"], "horizon": b["horizon"]}
            if common is None:common = catalog
            fail(canonical(common) == canonical(catalog), "worlds must share operations, approvals, tasks and budgets")
        fail(isinstance(source["probes"], dict) and len(source["probes"]) <= 4, "probe bound")
        for name, p in source["probes"].items():
            fail(isinstance(name, str) and name and ":" not in name, "probe id")
            fail(set(p) == {"operation", "phase", "caller", "scope", "outcomes"}, "probe fields")
            operation(p["operation"], "probe operation")
            fail(p["phase"] in {"before", "after", "both"}, "probe phase")
            fail(isinstance(p["caller"], str) and p["caller"], "probe caller")
            strings(p["scope"], "probe scope")
            fail(set(p["outcomes"]) == set(source["worlds"]), "incomplete probe worlds")
            lengths = set()
            for w, schedule in p["outcomes"].items():
                fail(isinstance(schedule, list) and 0 < len(schedule) <= 3, "probe attempts")
                lengths.add(len(schedule))
                for outcomes in schedule:
                    fail(isinstance(outcomes, list) and 0 < len(outcomes) <= 4, "probe outcome bound")
                    for edge in outcomes:
                        fail(set(edge) == {"observation", "to_world", "sessions", "withdraw"}, "probe edge fields")
                        fail(isinstance(edge["observation"], str) and edge["observation"], "probe observation")
                        fail(edge["to_world"] in source["worlds"], "world transition")
                        # Regime changes after setup need a separate state migration proof.
                        fail(edge["to_world"] == w or p["phase"] == "before", "regime migration only before setup")
                        strings(edge["sessions"], "session types"); strings(edge["withdraw"], "withdrawals")
                        fail(all("#" not in s for s in edge["sessions"]), "reserved session delimiter")
                        fail(set(edge["withdraw"]) <= set(common["approved"]), "unknown approval withdrawal")
            fail(len(lengths) == 1, "attempt availability cannot identify hidden world")
        fail(isinstance(source["cleanups"], dict) and len(source["cleanups"]) <= 4, "cleanup bound")
        for name, c in source["cleanups"].items():
            fail(isinstance(name, str) and name and ":" not in name, "cleanup id")
            fail(set(c) == {"operation", "mode", "sessions"}, "cleanup fields")
            operation(c["operation"], "cleanup operation"); strings(c["sessions"], "cleanup scope")
            fail(all("#" not in s for s in c["sessions"]), "reserved cleanup delimiter")
            fail(c["mode"] in {"known_handle", "account_root"}, "cleanup mode")
            if c["mode"] == "known_handle":fail(all(not s.startswith("opaque:") for s in c["sessions"]), "unknown handle cannot be addressed directly")
        fail(isinstance(source["faults"], dict), "fault registry")
        for action, schedule in source["faults"].items():
            fail(action.startswith("stop:") or action.startswith("cleanup:"), "only stop/cleanup fault schedules")
            fail(isinstance(schedule, list) and 0 < len(schedule) <= 3, "fault attempts")
            for outcomes in schedule:
                fail(isinstance(outcomes, list) and 0 < len(outcomes) <= 4, "fault outcomes")
                for edge in outcomes:
                    fail(set(edge) == {"observation", "applied", "withdraw"}, "fault fields")
                    fail(isinstance(edge["observation"], str) and edge["observation"], "fault observation")
                    fail(type(edge["applied"]) is bool, "applied boolean")
                    strings(edge["withdraw"], "fault withdrawals"); fail(set(edge["withdraw"]) <= set(common["approved"]), "fault approval")
        return deepcopy(source)
    except (ModelError, ValueError, KeyError, TypeError, AttributeError, RecursionError) as exc:
        raise ModelError(str(exc)) from exc


def initial(source, world):
    return {"world": world, "configuration": None, "stopped": [], "sessions": [],
            "approved": sorted(source["worlds"][world]["approved"]), "budget": deepcopy(source["budget"]),
            "attempts": {}, "stop_steps": 0, "epoch": 0}


def adjusted(source, point):
    b = deepcopy(source["worlds"][point["world"]])
    b["approved"] = list(point["approved"])
    b["budgets"].update(point["budget"])
    return b
