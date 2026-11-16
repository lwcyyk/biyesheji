"""Untrusted finite conflict cover producer, independent of the checker."""
from .model import prepare, digest, CONSTRAINTS, Work, Cutoff, ModelError
from . import engine


def produce(spec, *, configuration=None, limit=1_000_000):
    try:
        m = prepare(spec); work = Work(limit); names = sorted(m["paths"])
        if configuration is not None:
            if not isinstance(configuration, list) or configuration != sorted(set(configuration)) or not set(configuration) <= set(names):
                raise ModelError("invalid configuration")
            configs = [configuration]
        else:configs = ([p for i, p in enumerate(names) if mask & (1 << i)] for mask in range(1 << len(names)))
        rows = []
        for config in configs:
            work.tick("certificate_configurations")
            refs, _ = engine.inspect(m, config)
            if refs:rows.append({"configuration": config, "kind": "invalid", "refs": refs}); continue
            for sid, scenario in sorted(m["scenarios"].items()):
                plan, proof = engine.plan(m, config, scenario, work, proof=True)
                if plan is None:
                    rows.append({"configuration": config, "kind": "unplannable", "scenario": sid, "proof": proof}); break
            else:return {"status": "FEASIBLE", "certificate": None, "reason": "a legal configuration exists in requested scope", "work": work.counts}
        return {"status": "IMPOSSIBLE", "work": work.counts, "certificate": {
            "schema": "auth-lifecycle-b-conflict/1", "model_digest": digest(m), "context": m,
            "scope": "fixed_configuration" if configuration is not None else "finite_catalog",
            "configuration": configuration, "constraint_refs": CONSTRAINTS, "rows": rows,
            "minimality": "not_claimed"}}
    except Cutoff:return {"status": "INCONCLUSIVE", "certificate": None, "reason": "incomplete conflict cover", "work": work.counts}
    except (ModelError, TypeError, ValueError) as exc:return {"status": "UNKNOWN", "certificate": None, "reason": str(exc)}
