"""Independent L0 execution scorer. No actual point is passed to the selector."""
from ..schema import State, canonical, prepare, refs_json
from ..checker import check_policy
from .._reference_kernel import expand, is_goal, is_safe
from . import _plant_reference as plant
from .evidence import update, contract, usable
from ..b._kernel import native_units


def evaluate(bundle, result, *, trace_limit=100_000, diagnostic_unchecked=False):
    cap = bundle["source"]["budget"]["requests"]
    if result.status != "FEASIBLE":
        return {"status": result.status, "completion": 0, "refusal": int(result.status == "IMPOSSIBLE"),
                "UNKNOWN": int(result.status == "UNKNOWN"), "INCONCLUSIVE": int(result.status == "INCONCLUSIVE"),
                "external_requests": 0, "C_Q": cap + 1, "probe_side_effects": 0, "unresolved_obligations": 0,
                "safety_counterexamples": [], "traces": [], "execution": "not dispatched"}
    checked = check_policy(bundle["l0"], result.policy)
    if checked.verdict != "ACCEPTED" and not diagnostic_unchecked:return {"status": "INVALID_POLICY", "completion": 0, "safety_counterexamples": [checked.reason], "traces": []}
    data, root = prepare(bundle["l0"]); source = bundle["source"]; traces = []; failures = []; visits = 0

    class Limit(Exception):pass

    def walk(actual_ref, actual, belief, policy, history, created, evidence):
        nonlocal visits
        visits += 1
        if visits > trace_limit:raise Limit()
        unsafe, finished, _ = plant.predicates(source, actual)
        if unsafe:failures.append({"kind": "preserve_violation", "history": history})
        if policy["kind"] == "done":
            good = finished and not actual["sessions"] and not unsafe and is_goal(data, belief.knowledge)
            if not good:failures.append({"kind": "false_completion", "history": history})
            traces.append({"initial_world": history[0]["initial_world"], "completion": int(good),
                           "configuration": actual["configuration"], "G": len(native_units(source["worlds"][actual["world"]], actual["configuration"] or [])),
                           "requests": cap - actual["budget"]["requests"], "approval_charges": source["budget"]["approvals"] - actual["budget"]["approvals"],
                           "probe_side_effects": created, "unresolved_obligations": len(actual["sessions"]),
                           "steps": len(history) - 1, "history": history, "final_evidence": contract(bundle, belief, history)})
            return
        aid = policy["action"]; groups, errors = expand(data, belief.knowledge, aid)
        if errors:failures.append({"kind": "unauthorized_dispatch", "errors": errors, "history": history}); return
        concrete = plant.step(source, actual, aid)
        if not concrete:failures.append({"kind": "source_dispatch_rejected", "history": history}); return
        w, sid = actual_ref
        for observation, target in concrete:
            choices = [tuple(edge["target"]) for edge in data["worlds"][w]["states"][sid]["transitions"][aid]
                       if edge["observation"] == observation and canonical(bundle["points"]["/".join(edge["target"])]["point"]) == canonical(target)]
            if not choices:failures.append({"kind": "compiler_effect_mismatch", "history": history}); continue
            after = update(bundle, belief, aid, observation)
            if after.boundary or after.knowledge != groups[observation] or not after.knowledge:
                failures.append({"kind": "belief_update", "history": history}); continue
            if choices[0] not in after.knowledge:failures.append({"kind": "lost_actual_state", "history": history}); continue
            fresh = len(set(target["sessions"]) - set(actual["sessions"]))
            event = {"action": aid, "observation": observation, "remaining_before": belief.remaining,
                     "remaining_after": after.remaining, "belief_size": len(after.knowledge),
                     "requests_charged": actual["budget"]["requests"] - target["budget"]["requests"],
                     "sessions_created": fresh, "unresolved_obligations": len(target["sessions"]),
                     "previous_evidence_usable": usable(evidence, bundle, after),
                     "declared_fault_schedule_triggered": aid in source["faults"]}
            # Actual state is scorer-local; branch selection uses only the observation.
            walk(choices[0], target, after, policy["children"][observation], history + [event], created + fresh,
                 contract(bundle, after, history + [event]))
    try:
        for ref in sorted(root.knowledge):
            actual = bundle["points"]["/".join(ref)]["point"]
            walk(ref, actual, root, result.policy, [{"initial_world": ref[0]}], 0, contract(bundle, root))
    except Limit:
        return {"status": "INCONCLUSIVE", "completion": 0, "refusal": 0, "UNKNOWN": 0, "INCONCLUSIVE": 1,
                "C_Q": cap + 1, "traces": traces, "safety_counterexamples": failures, "reason": "trace validation incomplete"}
    complete = bool(traces) and all(t["completion"] for t in traces) and not failures
    return {"status": "COMPLETED" if complete else "SAFETY_FAILURE", "completion": int(complete), "refusal": 0,
            "UNKNOWN": 0, "INCONCLUSIVE": 0, "external_requests": max((t["requests"] for t in traces), default=0),
            "C_Q": max(t["requests"] for t in traces) if complete else cap + 1,
            "probe_side_effects": max((t["probe_side_effects"] for t in traces), default=0),
            "unresolved_obligations": max((t["unresolved_obligations"] for t in traces), default=0),
            "max_G": max((t["G"] for t in traces), default=0),
            "probe_actions_used": sorted({event["action"] for t in traces for event in t["history"] if event.get("action", "").startswith("probe:")}),
            "fault_schedules_triggered": sorted({event["action"] for t in traces for event in t["history"] if event.get("declared_fault_schedule_triggered")}),
            "fault_schedules_not_triggered": sorted(set(source["faults"]) - {event.get("action") for t in traces for event in t["history"]}),
            "trace_count": len(traces), "safety_counterexamples": failures, "policy_check": checked.verdict, "traces": traces}
