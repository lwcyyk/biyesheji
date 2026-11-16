"""Independent raw-catalog interpreter used by B reference and proof checker.

No imports from candidate search, baseline generation or candidate semantics.
State is (live credential names, open environments, open task gates, q, a, r).
"""


def native_units(m, config):
    """Compute G from registered effect footprints, without token labels/domain claims."""
    used = set()
    for name in config:used.update(m["paths"][name]["grants"])
    return [key for key, domain in sorted(m["revocations"].items()) if any(g in used for g in domain["affects"])]


def configuration(m, config):
    issues = []; tasks = set(); grants = set(); envs = set(); need = {}
    for name in config:
        p = m["paths"][name]; tasks.add(p["task"]); envs.add(p["environment"])
        scope = set(); target = m["tasks"][p["task"]]
        for g in p["grants"]:
            grants.add(g); need.setdefault(g, set()).update(target["permissions"])
            c = m["credentials"][g]; scope.update(c["scope"])
            if c["account"] != target["account"]:issues.append("account.binding")
        if any(permission not in scope for permission in target["permissions"]):issues.append("native.scope")
    if any(t not in tasks for t in m["tasks"]):issues.append("catalog.coverage")
    steps = []; ops = []
    for g in sorted(grants):steps.append("issue:" + g); ops.append(m["credentials"][g]["issue"])
    for e in sorted(envs):steps.append("create:" + e); ops.append(m["environments"][e]["create"])
    for p in sorted(config):steps.append("delegate:" + p); ops.append(m["paths"][p]["delegate"])
    q = a = 0
    for op in ops:
        if op["approval"] is not None and op["approval"] not in m["approved"]:issues.append("approval.membership")
        q += op["requests"]; a += op["approvals"]
    isolated = len([e for e in envs if m["environments"][e]["kind"] == "isolated"])
    gcount = len(native_units(m, config))
    for v, cap, ref in [(q, "requests", "budget.requests"), (a, "approvals", "budget.approvals"),
                        (isolated, "isolated_environments", "budget.isolation"), (gcount, "units", "budget.units")]:
        if v > m["budgets"][cap]:issues.append(ref)
    gates = frozenset((m["paths"][p]["environment"], m["paths"][p]["task"]) for p in config)
    state = (frozenset(grants), frozenset(envs), gates, q, a, m["horizon"])
    metrics = {"G": gcount, "setup_requests": q, "setup_approvals": a, "isolated_environments": isolated,
               "scope_excess": sum(len(set(m["credentials"][g]["scope"]) - need[g]) for g in grants)}
    return sorted(set(issues)), state, steps, metrics


def live(m, config, state, task, native=False):
    for key in config:
        path = m["paths"][key]
        if path["task"] != task:continue
        if any(g not in state[0] for g in path["grants"]):continue
        if native or (path["environment"] in state[1] and (path["environment"], task) in state[2]):return True
    return False


def final(m, config, state, scenario):
    for t in scenario["preserve"]:
        if not live(m, config, state, t):return False
    for t in scenario["local"]:
        if live(m, config, state, t):return False
    for t in scenario["remote"]:
        if live(m, config, state, t, native=True):return False
    return True


def menu(m, config):
    result = {}; envs = set(m["paths"][p]["environment"] for p in config)
    for u in native_units(m, config):
        x = m["revocations"][u]
        if x["coverage"] == "all_material" and x["revoke"] is not None:result["revoke:" + u] = x["revoke"]
    for e in envs:
        x = m["environments"][e]
        if x["stop"] is None or x["controlled"] is not True:continue
        if x["kind"] == "isolated":result["close:" + e] = x["stop"]
        if x["kind"] == "broker":
            for p in config:
                if m["paths"][p]["environment"] == e:result[f"gate:{e}:{m['paths'][p]['task']}"] = x["stop"]
    return dict(sorted(result.items()))


def transition(m, config, state, scenario, action):
    choices = menu(m, config)
    if action not in choices:return None, ["catalog.action"]
    if state[5] <= 0:return None, ["horizon"]
    op = choices[action]; refs = []
    if op["approval"] is not None and op["approval"] not in m["approved"]:refs.append("approval.membership")
    q = state[3] + op["requests"]; a = state[4] + op["approvals"]
    if q > m["budgets"]["requests"]:refs.append("budget.requests")
    if a > m["budgets"]["approvals"]:refs.append("budget.approvals")
    grants, envs, gates = map(set, state[:3]); parts = action.split(":")
    if parts[0] == "revoke":grants.difference_update(m["revocations"][parts[1]]["affects"])
    elif parts[0] == "close":envs.discard(parts[1])
    else:gates.discard((parts[1], parts[2]))
    nxt = (frozenset(grants), frozenset(envs), frozenset(gates), q, a, state[5] - 1)
    if any(not live(m, config, nxt, t) for t in scenario["preserve"]):refs.append("preserve.every_prefix")
    return (None if refs else nxt), sorted(refs)
