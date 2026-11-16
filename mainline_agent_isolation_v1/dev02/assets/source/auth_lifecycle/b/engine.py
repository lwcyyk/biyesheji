"""Candidate-side AND/OR support semantics and monotone stop planning."""
from itertools import combinations
from .model import Work


def subsets(items, nonempty=True):
    items = sorted(items)
    for n in range(1 if nonempty else 0, len(items) + 1):
        for x in combinations(items, n):yield x


def resources(m, config):
    grants = {g for p in config for g in m["paths"][p]["grants"]}
    envs = {m["paths"][p]["environment"] for p in config}
    units = {u for u, x in m["revocations"].items() if grants.intersection(x["affects"])}
    return grants, envs, units


def setup(m, config):
    grants, envs, _ = resources(m, config)
    ops = [("issue:" + g, m["credentials"][g]["issue"]) for g in sorted(grants)]
    ops += [("create:" + e, m["environments"][e]["create"]) for e in sorted(envs)]
    ops += [("delegate:" + p, m["paths"][p]["delegate"]) for p in sorted(config)]
    return ops


def authorized(m, op):
    return op["approval"] is None or op["approval"] in m["approved"]


def inspect(m, config):
    """Return stable constraint references, never inferred authorization."""
    errors = []
    if {m["paths"][p]["task"] for p in config} != set(m["tasks"]):errors.append("catalog.coverage")
    for p in config:
        x = m["paths"][p]; task = m["tasks"][x["task"]]
        if any(m["credentials"][g]["account"] != task["account"] for g in x["grants"]):errors.append("account.binding")
        if not set(task["permissions"]) <= {s for g in x["grants"] for s in m["credentials"][g]["scope"]}:errors.append("native.scope")
    ops = [op for _, op in setup(m, config)]; grants, envs, units = resources(m, config)
    if any(not authorized(m, op) for op in ops):errors.append("approval.membership")
    a = sum(op["approvals"] for op in ops); q = sum(op["requests"] for op in ops)
    isolated = sum(m["environments"][e]["kind"] == "isolated" for e in envs)
    for excess, key in [(a > m["budgets"]["approvals"], "budget.approvals"),
                        (q > m["budgets"]["requests"], "budget.requests"),
                        (isolated > m["budgets"]["isolated_environments"], "budget.isolation"),
                        (len(units) > m["budgets"]["units"], "budget.units")]:
        if excess:errors.append(key)
    needed = {g: set() for g in grants}
    for p in config:
        for g in m["paths"][p]["grants"]:needed[g].update(m["tasks"][m["paths"][p]["task"]]["permissions"])
    metrics = {"G": len(units), "setup_approvals": a, "setup_requests": q,
               "isolated_environments": isolated,
               "scope_excess": sum(len(set(m["credentials"][g]["scope"]) - needed[g]) for g in grants)}
    return sorted(set(errors)), metrics


def actions(m, config):
    _, envs, units = resources(m, config); result = {}
    for u in sorted(units):
        r = m["revocations"][u]
        if r["coverage"] == "all_material" and r["revoke"] is not None:
            result["revoke:" + u] = r["revoke"]
    for e in sorted(envs):
        env = m["environments"][e]
        if not env["controlled"] or env["stop"] is None:continue
        if env["kind"] == "isolated":result["close:" + e] = env["stop"]
        elif env["kind"] == "broker":
            for t in sorted({m["paths"][p]["task"] for p in config if m["paths"][p]["environment"] == e}):
                result[f"gate:{e}:{t}"] = env["stop"]
    return result


def available(m, config, completed, task, remote=False):
    killed = {g for a in completed if a.startswith("revoke:") for g in m["revocations"][a.split(":")[1]]["affects"]}
    for p in config:
        route = m["paths"][p]
        if route["task"] != task or killed.intersection(route["grants"]):continue
        e = route["environment"]
        if remote or (f"close:{e}" not in completed and f"gate:{e}:{task}" not in completed):return True
    return False


def preserves(m, config, done, scenario):
    return all(available(m, config, done, t) for t in scenario["preserve"])


def goal(m, config, done, scenario):
    return (preserves(m, config, done, scenario)
            and all(not available(m, config, done, t) for t in scenario["local"])
            and all(not available(m, config, done, t, True) for t in scenario["remote"]))


def plan(m, config, scenario, work=None, proof=False):
    """Complete DFS on sets of irreversible actions, with explicit bounded failure trees."""
    work = work or Work(); menu = actions(m, config); _, metrics = inspect(m, config); memo = {}

    def visit(done):
        if done in memo:return memo[done]
        work.tick("plan_states")
        if goal(m, config, done, scenario):answer = ([], {"kind": "goal"})
        elif len(done) == m["horizon"]:answer = (None, {"kind": "horizon"})
        else:
            fails = {}
            a0 = metrics["setup_approvals"] + sum(menu[a]["approvals"] for a in done)
            q0 = metrics["setup_requests"] + sum(menu[a]["requests"] for a in done)
            for action, op in sorted(menu.items()):
                if action in done:continue
                why = []
                if not authorized(m, op):why.append("approval.membership")
                if a0 + op["approvals"] > m["budgets"]["approvals"]:why.append("budget.approvals")
                if q0 + op["requests"] > m["budgets"]["requests"]:why.append("budget.requests")
                after = done | {action}
                if not preserves(m, config, after, scenario):why.append("preserve.every_prefix")
                if why:fails[action] = {"kind": "blocked", "refs": sorted(why)}; continue
                tail, child = visit(after)
                if tail is not None:
                    answer = ([action] + tail, None); memo[done] = answer; return answer
                fails[action] = {"kind": "child", "proof": child}
            answer = (None, {"kind": "all_actions", "actions": fails})
        memo[done] = answer; return answer

    route, tree = visit(frozenset())
    return (route, tree) if proof else route


def deliver(m, config, work):
    errors, _ = inspect(m, config)
    if errors:return None
    plans = {}
    for sid, scenario in sorted(m["scenarios"].items()):
        result = plan(m, config, scenario, work)
        if result is None:return None
        plans[sid] = result
    return {"configuration": sorted(config), "setup": [a for a, _ in setup(m, config)], "plans": plans}
