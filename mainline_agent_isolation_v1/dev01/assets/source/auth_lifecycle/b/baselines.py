"""B-B portfolio. Every rule-admitted configuration is planned and checked.

Rules never add an interface, grant, approval or synthetic independent root.
No arbitrary single representative or post-hoc winning heuristic is selected.
"""
from .model import prepare, Result, Work, Cutoff, ModelError
from . import engine
from .checker import check_delivery


def structural_rules(m, config):
    by_task = {t: [p for p in config if m["paths"][p]["task"] == t] for t in m["tasks"]}
    if any(not p for p in by_task.values()):return []
    units = {t: engine.resources(m, ps)[2] for t, ps in by_task.items()}
    envs = engine.resources(m, config)[1]; labels = []
    if len(envs) == 1:
        e = m["environments"][next(iter(envs))]
        if e["kind"] == "broker" and e["controlled"]:labels.append("shared_broker")
    tasks = sorted(by_task)
    if all(not units[t].intersection(units[s]) for i, t in enumerate(tasks) for s in tasks[i + 1:]):labels.append("independent")
    signatures = {t: tuple((t in sc["local"], t in sc["remote"], t in sc["preserve"])
                           for _, sc in sorted(m["scenarios"].items())) for t in tasks}
    if all(len(units[t]) == 1 for t in tasks) and all(
            (units[t] == units[s]) == (signatures[t] == signatures[s]) for t in tasks for s in tasks):labels.append("static_signatures")
    return labels


def greedy_configurations(m, work):
    options = {t: list(engine.subsets(p for p, x in m["paths"].items() if x["task"] == t)) for t in m["tasks"]}
    output = set(); seen = set()

    def visit(todo, config):
        key = (tuple(sorted(todo)), tuple(sorted(config)))
        if key in seen:return
        seen.add(key); work.tick("greedy_nodes")
        if not todo:output.add(tuple(sorted(config))); return
        # Branch on every possible next task, equivalent to all permutations.
        before = engine.resources(m, config)[0]
        for task in sorted(todo):
            ranked = []
            for choice in options[task]:
                combined = list(config) + list(choice)
                refs, _ = engine.inspect(m, combined)
                if any(r != "catalog.coverage" for r in refs):continue
                added = engine.resources(m, combined)[0] - before
                # Pure privilege rule: minimum newly acquired permission atoms.
                # All ties retained, including multiple alternative paths.
                rank = sum(len(m["credentials"][g]["scope"]) for g in added)
                ranked.append((rank, combined))
            if ranked:
                minimum = min(x[0] for x in ranked)
                for rank, combined in ranked:
                    if rank == minimum:visit(todo - {task}, combined)
    visit(set(m["tasks"]), [])
    return output


def solve(spec, *, limit=1_000_000):
    records = []; best = None
    try:
        m = prepare(spec); work = Work(limit); greedy = greedy_configurations(m, work)
        names = sorted(m["paths"])
        for mask in range(1 << len(names)):
            work.tick("baseline_catalog_masks")
            config = [p for i, p in enumerate(names) if mask & (1 << i)]
            labels = structural_rules(m, config)
            if tuple(config) in greedy:labels.append("privilege_greedy")
            if not labels:continue
            work.tick("baseline_configurations")
            delivery = engine.deliver(m, config, work)
            if delivery is None:
                records.append({"configuration": config, "rules": labels, "verdict": "NO_LEGAL_PLAN"}); continue
            checked = check_delivery(m, delivery, work=work)
            if checked["verdict"] == "INCONCLUSIVE":raise Cutoff()
            if checked["verdict"] != "ACCEPTED":raise RuntimeError("baseline/checker disagreement: " + str(checked))
            metrics = checked["metrics"]
            records.append({"configuration": config, "rules": labels, "verdict": "ACCEPTED", "metrics": metrics, "delivery": delivery})
            key = (metrics["G"], config)
            if best is None or key < best[0]:best = (key, delivery, metrics)
        if best is None:
            # B-B is not a complete synthesis procedure over arbitrary configs.
            return Result("NO_BASELINE_SOLUTION", "all applicable portfolio candidates exhausted; not global IMPOSSIBLE", stats=work.counts, candidates=records)
        return Result("FEASIBLE", "best of every legal portfolio candidate", best[1]["configuration"], best[1], best[2], True, work.counts, records)
    except Cutoff:
        return Result("INCONCLUSIVE", "portfolio generation/planning/checking incomplete",
                      delivery=best[1] if best else None, stats=work.counts, candidates=records)
    except ModelError as exc:return Result("UNKNOWN", str(exc))
