"""Check compilation against independent source effects, not just the output table."""
from collections import deque
from ..schema import canonical, digest, validate, ModelError
from ..b import _kernel as bk
from .model import prepare, initial
from . import _plant_reference as ref


def check_compilation(bundle):
    try:
        source = prepare(bundle["source"]); data = bundle["l0"]; points = bundle["points"]; validate(data)
        def need(x, message):
            if not x:raise ValueError(message)
        need(digest(source) == bundle["source_digest"], "source digest")
        first = next(iter(source["worlds"].values())); path_names = sorted(first["paths"])
        expected_actions = set(); configs = []
        for mask in range(1, 1 << len(path_names)):
            config = [p for i, p in enumerate(path_names) if mask & (1 << i)]
            if {first["paths"][p]["task"] for p in config} != set(first["tasks"]):continue
            expected_actions.add(f"configure:{mask:x}"); configs.append(config)
        for model in source["worlds"].values():
            for config in configs:expected_actions.update("stop:" + a for a in bk.menu(model, config))
        expected_actions.update("probe:" + name for name in source["probes"])
        expected_actions.update("cleanup:" + name for name in source["cleanups"])
        need(set(data["actions"]) == expected_actions == set(bundle["catalog"]), "omitted/invented source action")
        need(data["tasks"] == sorted(first["tasks"]) and data["horizon"] == source["horizon"], "task/H mapping")
        need(data["goal"] == {"account": source["account"], "facts": ["stop_goal"]}, "goal mapping")
        need(data["safety"] == {"forbidden_facts": ["unsafe"], "preserve_capabilities": []}, "safety mapping")
        for aid in expected_actions:
            kind, name, config, ops = ref.descriptor(source, aid)
            expected = {"task": sorted(first["tasks"])[0], "account": source["account"], "approval": "__model_internal__",
                        "cost": {k: sum(op[k] for op in ops) for k in ["requests", "approvals"]}, "requires": [], "independent": [],
                        "kind": "probe" if kind == "probe" else "control", "operation": aid}
            need(canonical(expected) == canonical(data["actions"][aid]), "action cost/authority mapping")
            meta = bundle["catalog"][aid]
            need(meta["kind"] == kind and all(meta[k] == expected["cost"][k] for k in expected["cost"]), "selector metadata")
            if kind == "configure":need(meta["configuration"] == config, "configuration metadata")
        starts = []; initial_keys = []
        for w in source["worlds"]:
            matches = [key for key, x in points.items() if x["depth"] == 0 and canonical(x["point"]) == canonical(initial(source, w))]
            need(len(matches) == 1, "initial state mapping"); starts += matches
            if w in source["initial"]:initial_keys.append(matches[0].split("/", 1))
        need(sorted(initial_keys) == sorted(data["initial"]), "initial belief mapping")
        reached = set(starts); queue = deque(starts); edges_checked = 0
        while queue:
            key = queue.popleft(); w, sid = key.split("/", 1); record = points[key]; point = record["point"]; depth = record["depth"]
            node = data["worlds"][w]["states"][sid]; unsafe, done, tasks = ref.predicates(source, point)
            need(point["world"] == w, "wrong concrete world")
            facts = (["configured"] if point["configuration"] is not None else []) + (["stop_goal"] if done else []) + (["unsafe"] if unsafe else [])
            need(set(node["facts"]) == set(facts), "goal/safety not reflected")
            need(node["budget"] == point["budget"] and node["account"] == source["account"], "state budget/account")
            need(node["approvals"] == sorted(set(point["approved"]) | {"__model_internal__"}), "state approval mapping")
            need(node["capabilities"] == sorted(["session:" + s for s in point["sessions"]] + ["task:" + t for t in tasks]), "side-effect capability omitted")
            need(node["obligations"] == sorted("close:session:" + s for s in point["sessions"]), "strict obligation omitted")
            for aid in sorted(expected_actions):
                expected = [] if depth == source["horizon"] or unsafe else ref.step(source, point, aid)
                actual = []
                for edge in node["transitions"].get(aid, []):
                    tw, ts = edge["target"]; dest = tw + "/" + ts; p2 = points[dest]
                    need(p2["depth"] == depth + 1, "step mapping")
                    actual.append((edge["observation"], p2["point"]))
                    edges_checked += 1
                    if dest not in reached:reached.add(dest); queue.append(dest)
                need(sorted(map(canonical, expected)) == sorted(map(canonical, actual)), "omitted/invented physical outcome: " + key + ":" + aid)
        need(reached == set(points), "unreachable/missing source mapping")
        need(len(points) == sum(len(w["states"]) for w in data["worlds"].values()), "unmapped table node")
        return {"verdict": "ACCEPTED", "states": len(reached), "edges": edges_checked,
                "scope": "all compiled source transitions, within finite H; no real provider proof"}
    except (ModelError, KeyError, ValueError, TypeError, AttributeError) as exc:return {"verdict": "REJECTED", "reason": str(exc)}
