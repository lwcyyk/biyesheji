"""Compile the explicit finite plant into the accepted v2.16 L0 data contract."""
from collections import deque
from dataclasses import dataclass
from ..schema import digest, canonical, validate, ModelError
from .model import prepare, initial
from . import plant


@dataclass
class Compilation:
    status: str
    reason: str
    bundle: dict | None = None
    nodes: int = 0


def compile_model(source, *, node_limit=20_000):
    try:
        s = prepare(source)
        if type(node_limit) is not int or node_limit < 0:raise ModelError("compile limit")
        catalog = plant.catalog(s)
        if not set(s["faults"]) <= set(catalog):raise ModelError("fault schedule for absent operation")
        first = next(iter(s["worlds"].values()))
        l0 = {"schema": "auth-lifecycle-l0/1", "tasks": sorted(first["tasks"]), "horizon": s["horizon"],
              "worlds": {w: {"semantics": digest(b), "native_roots": {g: u for u, obj in b["revocations"].items() for g in obj["affects"]}, "states": {}} for w, b in s["worlds"].items()},
              "actions": {}, "initial": [], "goal": {"account": s["account"], "facts": ["stop_goal"]},
              "safety": {"forbidden_facts": ["unsafe"], "preserve_capabilities": []}}
        for aid, meta in catalog.items():
            l0["actions"][aid] = {"task": sorted(first["tasks"])[0], "account": s["account"],
                                  "approval": "__model_internal__", "cost": {"requests": meta["requests"], "approvals": meta["approvals"]},
                                  "requires": [], "independent": [], "kind": "probe" if meta["kind"] == "probe" else "control", "operation": aid}
        points = {}; queue = deque(); seen = set()

        def register(p, depth):
            wid = p["world"]; sid = f"d{depth}-" + digest(p)[:24]; key = (wid, sid)
            if key not in seen:
                if len(seen) >= node_limit:raise OverflowError("compile node limit")
                seen.add(key); points[wid + "/" + sid] = {"point": p, "depth": depth}
                unsafe, done, tasks = plant.flags(s, p)
                l0["worlds"][wid]["states"][sid] = {"account": s["account"],
                    "facts": (["configured"] if p["configuration"] is not None else []) + (["stop_goal"] if done else []) + (["unsafe"] if unsafe else []),
                    "approvals": sorted(set(p["approved"]) | {"__model_internal__"}), "budget": p["budget"],
                    "capabilities": sorted(["session:" + x for x in p["sessions"]] + ["task:" + t for t in tasks]),
                    "obligations": sorted("close:session:" + x for x in p["sessions"]), "transitions": {}}
                queue.append(key)
            return key
        # Keep every declared world nonempty, even if it is initially excluded.
        for w in s["worlds"]:
            key = register(initial(s, w), 0)
            if w in s["initial"]:l0["initial"].append(list(key))
        while queue:
            wid, sid = queue.popleft(); record = points[wid + "/" + sid]; p = record["point"]; depth = record["depth"]
            n = l0["worlds"][wid]["states"][sid]
            if depth == s["horizon"] or "unsafe" in n["facts"]:continue
            for aid, meta in catalog.items():
                for observation, target in plant.step(s, p, aid, meta):
                    tw, ts = register(target, depth + 1); after = l0["worlds"][tw]["states"][ts]
                    delta = {f: {"add": sorted(set(after[f]) - set(n[f])), "remove": sorted(set(n[f]) - set(after[f]))}
                             for f in ["facts", "capabilities", "obligations"]}
                    delta.update(withdraw_approvals=sorted(set(n["approvals"]) - set(after["approvals"])), external_debit={})
                    n["transitions"].setdefault(aid, []).append({"observation": observation, "target": [tw, ts],
                        "effects": [meta["kind"] + ":" + aid], "delta": delta})
        validate(l0)
        return Compilation("COMPILED", "complete finite reachable plant", {"source": s, "source_digest": digest(s), "l0": l0, "points": points, "catalog": catalog}, len(seen))
    except OverflowError:return Compilation("INCONCLUSIVE", "compilation limit; partial graph not exposed", nodes=len(seen))
    except (ModelError, KeyError, ValueError, TypeError) as exc:return Compilation("UNKNOWN", str(exc))
