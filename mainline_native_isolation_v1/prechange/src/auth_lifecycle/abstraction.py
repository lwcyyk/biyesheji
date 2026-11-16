"""Check a finite conservative relation. No claims about an unmodelled website."""
from .schema import ModelError, validate
from ._reference_kernel import expand, is_goal, is_safe, state_record


def check_relation(concrete, abstract, relation, action_map, observation_map, bindings):
    """relation maps concrete (world,state) to a set of abstract references.

    Obligation and capability labels are identity-mapped in v2.16. This is a
    deliberate restriction, not a general abstraction discovery algorithm.
    bindings maps concrete action IDs to executable, zero-arg L0 callables.
    The checker inspects availability, not truth of an arbitrary Python callable.
    """
    issues = []
    try:
        validate(concrete); validate(abstract)
        cs = {(w, s) for w, x in concrete["worlds"].items() for s in x["states"]}
        ats = {(w, s) for w, x in abstract["worlds"].items() for s in x["states"]}
        if set(relation) != cs:issues.append("state_coverage")
        for c in cs:
            if not relation.get(c) or not set(relation[c]) <= ats:issues.append(f"state_coverage:{c}")
        if issues:return {"valid": False, "issues": sorted(set(issues)), "external_adapter_proof": "NOT_PROVED"}
        if set(action_map) != set(abstract["actions"]):issues.append("action_coverage")
        if set(concrete["tasks"]) != set(abstract["tasks"]):issues.append("task_mapping")
        mapped_initial = set().union(*(set(relation[tuple(c)]) for c in concrete["initial"])) if concrete["initial"] else set()
        if not concrete["initial"] or not abstract["initial"] or not mapped_initial <= {tuple(a) for a in abstract["initial"]}:
            issues.append("initial_coverage")
        for aa, ca in action_map.items():
            if aa not in abstract["actions"] or ca not in concrete["actions"]:
                issues.append(f"action_mapping:{aa}"); continue
            if ca not in bindings or not callable(bindings[ca]):issues.append(f"executable_binding:{ca}")
            a_op, c_op = abstract["actions"][aa], concrete["actions"][ca]
            for field in ["account", "approval", "task"]:
                if a_op[field] != c_op[field]:issues.append(f"action_{field}:{aa}")
            for resource, cost in c_op["cost"].items():
                if a_op["cost"].get(resource, -1) < cost:issues.append(f"cost_underestimate:{aa}:{resource}")
        for c in sorted(cs):
            cn = state_record(concrete, c)
            for a in sorted(relation[c]):
                an = state_record(abstract, a)
                if is_safe(abstract, a) and not is_safe(concrete, c):issues.append(f"safety_reflection:{c}:{a}")
                if is_goal(abstract, [a]) and not is_goal(concrete, [c]):issues.append(f"terminal_reflection:{c}:{a}")
                if not set(cn["obligations"]) <= set(an["obligations"]):issues.append(f"obligation_omission:{c}:{a}")
                if set(cn["capabilities"]) != set(an["capabilities"]):issues.append(f"capability_mapping:{c}:{a}")
                if not set(an["approvals"]) <= set(cn["approvals"]):issues.append(f"approval_enlargement:{c}:{a}")
                if any(v > cn["budget"].get(k, -1) for k, v in an["budget"].items()):issues.append(f"budget_overestimate:{c}:{a}")
                for aa, ca in action_map.items():
                    if aa not in abstract["actions"] or ca not in concrete["actions"]:continue
                    _, aerr = expand(abstract, frozenset([a]), aa)
                    if aerr:continue  # abstract disabling is conservative
                    _, cerr = expand(concrete, frozenset([c]), ca)
                    if cerr:
                        issues.append(f"precondition_preservation:{c}:{a}:{aa}"); continue
                    aedges = an["transitions"][aa]
                    for ce in cn["transitions"][ca]:
                        co = ce["observation"]
                        if co not in observation_map:
                            issues.append(f"observation_mapping:{co}"); continue
                        mapped = relation[tuple(ce["target"])]
                        matches = [ae for ae in aedges if ae["observation"] == observation_map[co] and tuple(ae["target"]) in mapped]
                        if not matches:issues.append(f"transition_simulation:{c}:{a}:{aa}:{co}")
                        elif not any(set(ce["effects"]) <= set(ae["effects"]) for ae in matches):
                            issues.append(f"effect_omission:{c}:{a}:{aa}:{co}")
        return {"valid": not issues, "issues": sorted(set(issues)), "scope": "finite_table_relation_only",
                "checked_pairs": sum(len(v) for v in relation.values()),
                "external_adapter_proof": "NOT_PROVED"}
    except (ModelError, KeyError, TypeError, AttributeError) as exc:
        return {"valid": False, "issues": ["malformed_mapping:" + str(exc)], "external_adapter_proof": "NOT_PROVED"}


def lift_policy(concrete, abstract, policy, relation, action_map, observation_map, bindings):
    """Construct a concrete observation policy from an accepted finite abstraction.

    No candidate search is invoked; this is a recursive action/observation
    translation. The result is independently checked before being returned.
    """
    from .checker import check_policy
    from .schema import refs_json
    report = check_relation(concrete, abstract, relation, action_map, observation_map, bindings)
    if not report["valid"]:raise ModelError("invalid abstraction: " + str(report["issues"]))
    h = policy.get("remaining")
    if check_policy(abstract, policy, horizon=h).verdict != "ACCEPTED":raise ModelError("invalid abstract policy")

    def translate(proof, belief, remaining):
        result = {"belief": refs_json(belief), "remaining": remaining, "kind": proof["kind"]}
        if proof["kind"] == "done":return result
        concrete_action = action_map[proof["action"]]
        nexts, errors = expand(concrete, belief, concrete_action)
        if errors:raise ModelError("non-executable refined action")
        result["action"] = concrete_action
        result["children"] = {o: translate(proof["children"][observation_map[o]], child, remaining - 1) for o, child in nexts.items()}
        return result
    lifted = translate(policy, frozenset(tuple(x) for x in concrete["initial"]), h)
    if check_policy(concrete, lifted, horizon=h).verdict != "ACCEPTED":raise ModelError("refined policy failed checking")
    return lifted
