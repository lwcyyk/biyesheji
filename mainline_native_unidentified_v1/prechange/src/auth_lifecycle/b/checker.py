"""Untrusted delivery and exhaustive conflict checking. No candidate imports."""
from .model import prepare, ModelError, canonical, digest, CONSTRAINTS, Work, Cutoff
from . import _kernel as k


def require(condition, message):
    if not condition:raise ValueError(message)


def paths(m, config):
    require(isinstance(config, list) and all(isinstance(p, str) for p in config), "path list")
    require(config == sorted(set(config)) and set(config) <= set(m["paths"]), "duplicate/unknown/unsorted path")


def check_delivery(spec, delivery, *, limit=1_000_000, work=None):
    try:
        work = work if work is not None else Work(limit)
        m = prepare(spec)
        require(set(delivery) == {"configuration", "setup", "plans"}, "delivery fields")
        config = delivery["configuration"]; paths(m, config); work.tick("check_configurations")
        errors, initial, steps, metrics = k.configuration(m, config)
        require(not errors, ",".join(errors))
        require(canonical(delivery["setup"]) == canonical(steps), "setup.order")
        require(set(delivery["plans"]) == set(m["scenarios"]), "missing/invented scenario")
        ends = []
        for sid, scenario in m["scenarios"].items():
            plan = delivery["plans"][sid]; state = initial
            require(isinstance(plan, list) and all(isinstance(a, str) for a in plan), "plan list")
            require(len(plan) <= m["horizon"], "horizon")
            require(all(k.live(m, config, state, t) for t in scenario["preserve"]), "preserve.initial")
            for action in plan:
                work.tick("check_steps")
                state, errors = k.transition(m, config, state, scenario, action)
                require(not errors, ",".join(errors))
            require(k.final(m, config, state, scenario), "stop.local/stop.remote/support.all_alternatives")
            ends.append(state)
        metrics.update(worst_lifecycle_requests=max(s[3] for s in ends),
                       worst_lifecycle_approvals=max(s[4] for s in ends),
                       max_stop_steps=max(len(x) for x in delivery["plans"].values()),
                       native_units=k.native_units(m, config))
        return {"verdict": "ACCEPTED", "reason": "configuration, setup and every stop prefix checked", "metrics": metrics}
    except Cutoff:return {"verdict": "INCONCLUSIVE", "reason": "checking work limit"}
    except (ModelError, ValueError, TypeError, KeyError, AttributeError, RecursionError) as exc:
        return {"verdict": "REJECTED", "reason": str(exc)}


def check_conflict(spec, certificate, *, limit=1_000_000):
    try:
        m = prepare(spec); work = Work(limit)
        require(certificate["schema"] == "auth-lifecycle-b-conflict/1", "certificate schema")
        require(certificate["model_digest"] == digest(m), "model digest")
        require(canonical(certificate["context"]) == canonical(m), "context changed, including approvals/budgets/interfaces")
        require(certificate["constraint_refs"] == CONSTRAINTS, "constraint references")
        require(certificate["minimality"] == "not_claimed", "unsupported minimality claim")
        scope = certificate["scope"]
        require(scope in {"fixed_configuration", "finite_catalog"}, "scope")
        names = sorted(m["paths"])
        if scope == "fixed_configuration":
            paths(m, certificate["configuration"]); expected = [certificate["configuration"]]
        else:
            expected = ([p for i, p in enumerate(names) if mask & (1 << i)] for mask in range(1 << len(names)))
        rows = certificate["rows"]; require(isinstance(rows, list), "rows")
        count = 0
        for count, config in enumerate(expected, start=1):
            work.tick("certificate_configurations")
            require(count <= len(rows), "omitted configuration")
            row = rows[count - 1]; require(row["configuration"] == config, "configuration coverage/order")
            errors, initial, _, _ = k.configuration(m, config)
            if errors:
                require(row["kind"] == "invalid" and row["refs"] == errors, "false configuration conflict")
                continue
            require(row["kind"] == "unplannable" and row["scenario"] in m["scenarios"], "missing scenario refutation")
            scenario = m["scenarios"][row["scenario"]]

            def walk(proof, state, used):
                work.tick("certificate_nodes")
                require(not k.final(m, config, state, scenario), "refutes an achieved goal")
                if state[5] == 0:require(proof == {"kind": "horizon"}, "horizon leaf"); return
                require(proof["kind"] == "all_actions", "refutation kind")
                todo = set(k.menu(m, config)) - used
                require(set(proof["actions"]) == todo, "omitted/invented action")
                for action in sorted(todo):
                    child = proof["actions"][action]
                    successor, refs = k.transition(m, config, state, scenario, action)
                    if refs:require(child == {"kind": "blocked", "refs": refs}, "blocking references")
                    else:
                        require(child["kind"] == "child", "missing legal successor")
                        walk(child["proof"], successor, used | {action})
            walk(row["proof"], initial, set())
        require(len(rows) == count, "extra rows")
        return {"verdict": "ACCEPTED", "reason": "complete finite conflict cover checked",
                "scope": scope, "work": work.counts,
                "claim": "no legal bounded plan for this configuration" if scope == "fixed_configuration" else "no configuration and bounded plan in this finite catalog"}
    except Cutoff:return {"verdict": "INCONCLUSIVE", "reason": "checking work limit"}
    except (ModelError, ValueError, TypeError, KeyError, AttributeError, RecursionError) as exc:
        return {"verdict": "REJECTED", "reason": str(exc)}


def audit_G(spec, configuration):
    """Auditable native footprint computation, separate from B/B-B generators."""
    try:
        m = prepare(spec); paths(m, configuration)
        used = sorted({g for p in configuration for g in m["paths"][p]["grants"]})
        units = k.native_units(m, configuration)
        return {"status": "VERIFIED_WITHIN_DECLARED_CONTRACT", "model_digest": digest(m), "G": len(units),
                "acquired_credentials": used,
                "units": {u: {"affects": m["revocations"][u]["affects"], "evidence": m["revocations"][u]["evidence"],
                              "coverage": m["revocations"][u]["coverage"], "revoke": m["revocations"][u]["revoke"]} for u in units},
                "token_labels_used_for_counting": False,
                "boundary": "checks declared partition/effects; does not authenticate real provider evidence"}
    except (ModelError, ValueError, TypeError, KeyError) as exc:return {"status": "UNKNOWN", "reason": str(exc)}
