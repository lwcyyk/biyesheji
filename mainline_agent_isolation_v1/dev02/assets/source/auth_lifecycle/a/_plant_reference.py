"""Independent source-level effects and predicates. Does not import plant/compiler.

Uses the already independent B kernel for goal interpretation, not B search.
"""
from copy import deepcopy
from ..b import _kernel as bk


def physical(source, point):
    m = source["worlds"][point["world"]]; config = point["configuration"]
    if config is None:return None
    live = set(); envs = set(); gates = set()
    for key in config:
        p = m["paths"][key]; live.update(p["grants"]); envs.add(p["environment"]); gates.add((p["environment"], p["task"]))
    for a in point["stopped"]:
        fields = a.split(":")
        if fields[0] == "revoke":live.difference_update(m["revocations"][fields[1]]["affects"])
        elif fields[0] == "close":envs.discard(fields[1])
        else:gates.discard((fields[1], fields[2]))
    return (frozenset(live), frozenset(envs), frozenset(gates),
            source["budget"]["requests"] - point["budget"]["requests"],
            source["budget"]["approvals"] - point["budget"]["approvals"], m["horizon"] - point["stop_steps"])


def predicates(source, point):
    state = physical(source, point)
    if state is None:return False, False, []
    m = source["worlds"][point["world"]]; config = point["configuration"]; sc = m["scenarios"][source["scenario"]]
    unsafe = any(not bk.live(m, config, state, t) for t in sc["preserve"])
    return unsafe, bk.final(m, config, state, sc), sorted(t for t in m["tasks"] if bk.live(m, config, state, t))


def descriptor(source, action):
    m = next(iter(source["worlds"].values())); tag, name = action.split(":", 1)
    if tag == "configure":
        mask = int(name, 16); names = sorted(m["paths"])
        if mask <= 0 or mask >= 1 << len(names):raise ValueError("configuration mask")
        config = [p for i, p in enumerate(names) if mask & (1 << i)]
        grants = sorted({g for p in config for g in m["paths"][p]["grants"]})
        envs = sorted({m["paths"][p]["environment"] for p in config})
        ops = [m["credentials"][g]["issue"] for g in grants] + [m["environments"][e]["create"] for e in envs] + [m["paths"][p]["delegate"] for p in config]
    elif tag == "probe":ops = [source["probes"][name]["operation"]]; config = None
    elif tag == "cleanup":ops = [source["cleanups"][name]["operation"]]; config = None
    else:
        prefix, rest = name.split(":", 1); config = None
        op = m["revocations"][rest]["revoke"] if prefix == "revoke" else m["environments"][rest.split(":")[0]]["stop"]
        ops = [op]
    return tag, name, config, ops


def step(source, point, action):
    tag, name, config, ops = descriptor(source, action); m = source["worlds"][point["world"]]
    q = sum(op["requests"] for op in ops); a = sum(op["approvals"] for op in ops)
    if q > point["budget"]["requests"] or a > point["budget"]["approvals"]:return []
    if any(op["approval"] is not None and op["approval"] not in point["approved"] for op in ops):return []
    attempt = point["attempts"].get(action, 0)
    if tag == "configure":
        if point["configuration"] is not None:return []
        adjusted = deepcopy(m); adjusted["approved"] = point["approved"]; adjusted["budgets"].update(point["budget"])
        errors, _, _, _ = bk.configuration(adjusted, config)
        if errors:return []
    if tag == "stop":
        if point["configuration"] is None or point["stop_steps"] >= m["horizon"]:return []
        if name not in bk.menu(m, point["configuration"]):return []
    if tag == "probe":
        p = source["probes"][name]
        if p["caller"] != source["caller"]:return []
        if p["phase"] != "both" and (p["phase"] == "before") != (point["configuration"] is None):return []
        if attempt >= len(p["outcomes"][point["world"]]):return []
        choices = p["outcomes"][point["world"]][attempt]
    else:
        schedules = source["faults"].get(action, [[{"observation": "ok", "applied": True, "withdraw": []}]])
        choices = schedules[min(attempt, len(schedules) - 1)]
    outputs = []
    for choice in choices:
        nxt = deepcopy(point); nxt["budget"] = {"requests": point["budget"]["requests"] - q, "approvals": point["budget"]["approvals"] - a}
        nxt["attempts"][action] = attempt + 1
        nxt["approved"] = [approval for approval in sorted(point["approved"]) if approval not in choice["withdraw"]]
        if tag == "configure":nxt["configuration"] = config
        elif tag == "probe":
            nxt["world"] = choice["to_world"]; nxt["epoch"] += int(nxt["world"] != point["world"])
            added = [s + "#" + name + "#" + str(attempt) for s in choice["sessions"]]
            nxt["sessions"] = sorted(set(point["sessions"] + added))
        elif tag == "stop":
            nxt["stop_steps"] += 1
            if choice["applied"]:nxt["stopped"] = sorted(set(nxt["stopped"] + [name]))
        elif choice["applied"]:
            clean = source["cleanups"][name]; keep = []
            for session in point["sessions"]:
                in_scope = session.split("#")[0] in clean["sessions"]
                if not in_scope or clean["mode"] == "known_handle" and session.startswith("opaque:"):keep.append(session)
            nxt["sessions"] = keep
        outputs.append((choice["observation"], nxt))
    return outputs
