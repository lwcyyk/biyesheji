"""B: complete task-wise subset search, monotone G bound, common final checker."""
from .model import prepare, Result, Work, Cutoff, ModelError
from . import engine
from .checker import check_delivery


def solve(spec, *, limit=1_000_000):
    best = None
    try:
        m = prepare(spec); work = Work(limit); tasks = sorted(m["tasks"])
        options = {t: list(engine.subsets(p for p, x in m["paths"].items() if x["task"] == t)) for t in tasks}

        def visit(index, chosen):
            nonlocal best
            work.tick("search_nodes")
            if best is not None and len(engine.resources(m, chosen)[2]) > best[0][0]:return
            # All non-coverage setup constraints are monotone under adding paths.
            refs, _ = engine.inspect(m, chosen)
            if any(r != "catalog.coverage" for r in refs):return
            if index < len(tasks):
                for subset in options[tasks[index]]:visit(index + 1, chosen + list(subset))
                return
            work.tick("candidate_configurations"); config = sorted(chosen)
            delivery = engine.deliver(m, config, work)
            if delivery is None:return
            checked = check_delivery(m, delivery, work=work)
            if checked["verdict"] == "INCONCLUSIVE":raise Cutoff()
            if checked["verdict"] != "ACCEPTED":raise RuntimeError("candidate/checker disagreement: " + str(checked))
            metrics = checked["metrics"]; key = (metrics["G"], config)
            if best is None or key < best[0]:best = (key, delivery, metrics)
        visit(0, [])
        if best is None:return Result("IMPOSSIBLE", "complete finite catalog search", optimal=True, stats=work.counts)
        return Result("FEASIBLE", "complete finite catalog search", best[1]["configuration"], best[1], best[2], True, work.counts)
    except Cutoff:
        return Result("INCONCLUSIVE", "work limit; incumbent is not an optimality claim",
                      delivery=best[1] if best else None, stats=work.counts)
    except ModelError as exc:return Result("UNKNOWN", str(exc))
