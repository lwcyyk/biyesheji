"""Candidate-side concrete L0 plant; observations are separate from effects."""
from copy import deepcopy
from itertools import combinations
from ..b import engine as b
from .model import adjusted


def catalog(source):
    contract = next(iter(source["worlds"].values())); paths = sorted(contract["paths"]); out = {}
    for mask in range(1, 1 << len(paths)):
        config = [p for i, p in enumerate(paths) if mask & (1 << i)]
        if {contract["paths"][p]["task"] for p in config} != set(contract["tasks"]):continue
        ops = [op for _, op in b.setup(contract, config)]
        out[f"configure:{mask:x}"] = {"kind": "configure", "configuration": config, "operations": ops,
                                      "requests": sum(x["requests"] for x in ops), "approvals": sum(x["approvals"] for x in ops)}
    for world in source["worlds"].values():
        for meta in list(out.values()):
            if meta["kind"] != "configure":continue
            for action, op in b.actions(world, meta["configuration"]).items():
                out["stop:" + action] = dict(kind="stop", native=action, operations=[op], requests=op["requests"], approvals=op["approvals"])
    for kind, field in [("probe", "probes"), ("cleanup", "cleanups")]:
        for name, obj in source[field].items():
            op = obj["operation"]
            out[kind + ":" + name] = dict(kind=kind, name=name, operations=[op], requests=op["requests"], approvals=op["approvals"])
    return dict(sorted(out.items()))


def flags(source, point):
    if point["configuration"] is None:return False, False, []
    contract = source["worlds"][point["world"]]; sc = contract["scenarios"][source["scenario"]]
    config = point["configuration"]; done = point["stopped"]
    unsafe = not b.preserves(contract, config, done, sc)
    finished = b.goal(contract, config, done, sc)
    live = [t for t in contract["tasks"] if b.available(contract, config, done, t)]
    return unsafe, finished, live


def guard(source, point, action, meta):
    errors = []; kind = meta["kind"]
    if any(op["approval"] is not None and op["approval"] not in point["approved"] for op in meta["operations"]):errors.append("approval")
    if any(point["budget"][resource] < meta[resource] for resource in ["requests", "approvals"]):errors.append("budget")
    if kind == "configure":
        if point["configuration"] is not None:errors.append("already_configured")
        else:
            refs, _ = b.inspect(adjusted(source, point), meta["configuration"]); errors.extend(refs)
    elif kind == "stop":
        contract = source["worlds"][point["world"]]
        if point["configuration"] is None:errors.append("not_configured")
        elif meta["native"] not in b.actions(contract, point["configuration"]):errors.append("native_interface_scope")
        if point["stop_steps"] >= contract["horizon"]:errors.append("B_stop_horizon")
    elif kind == "probe":
        p = source["probes"][meta["name"]]
        if p["caller"] != source["caller"]:errors.append("caller_scope")
        if p["phase"] == "before" and point["configuration"] is not None:errors.append("phase")
        if p["phase"] == "after" and point["configuration"] is None:errors.append("phase")
        if point["attempts"].get(action, 0) >= len(p["outcomes"][point["world"]]):errors.append("probe_attempts")
    return sorted(set(errors))


def step(source, point, action, meta):
    if guard(source, point, action, meta):return []
    kind = meta["kind"]; attempt = point["attempts"].get(action, 0)
    if kind == "probe":outcomes = source["probes"][meta["name"]]["outcomes"][point["world"]][attempt]
    elif action in source["faults"]:
        schedule = source["faults"][action]; outcomes = schedule[min(attempt, len(schedule) - 1)]
    else:outcomes = [{"observation": "ok", "applied": True, "withdraw": []}]
    result = []
    for edge in outcomes:
        target = deepcopy(point)
        for resource in ["requests", "approvals"]:target["budget"][resource] -= meta[resource]
        target["approved"] = sorted(set(point["approved"]) - set(edge["withdraw"]))
        target["attempts"][action] = attempt + 1
        if kind == "probe":
            target["world"] = edge["to_world"]
            if target["world"] != point["world"]:target["epoch"] += 1
            target["sessions"] = sorted(set(point["sessions"]) | {f"{s}#{meta['name']}#{attempt}" for s in edge["sessions"]})
        elif kind == "configure":target["configuration"] = list(meta["configuration"])
        elif kind == "stop":
            target["stop_steps"] += 1
            if edge["applied"]:target["stopped"] = sorted(set(point["stopped"]) | {meta["native"]})
        elif edge["applied"]:
            clean = source["cleanups"][meta["name"]]
            target["sessions"] = [s for s in point["sessions"] if not (s.split("#")[0] in clean["sessions"] and (clean["mode"] == "account_root" or not s.startswith("opaque:")))]
        result.append((edge["observation"], target))
    return result
