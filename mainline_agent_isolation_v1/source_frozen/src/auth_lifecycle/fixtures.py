"""Synthetic finite contracts. No production accounts or network operations."""
from copy import deepcopy


def action(*, task="A", account="acct", approval="permit", cost=0, requires=(), independent=(), kind="control", operation="local.step"):
    return {"task": task, "account": account, "approval": approval,
            "cost": {"calls": cost}, "requires": list(requires),
            "independent": [list(x) for x in independent], "kind": kind, "operation": operation}


def state(*, account="acct", facts=(), approvals=("permit",), budget=0, obligations=(), capabilities=()):
    return {"account": account, "facts": list(facts), "approvals": list(approvals),
            "budget": {"calls": budget}, "obligations": list(obligations),
            "capabilities": list(capabilities), "transitions": {}}


def world(states, *, roots=None, semantics="declared-fixture-v1"):
    return {"semantics": semantics, "native_roots": roots or {}, "states": states}


def model(worlds, actions, *, horizon=2, initial=None, goal=("done",), preserve=()):
    return {"schema": "auth-lifecycle-l0/1", "tasks": ["A"], "horizon": horizon,
            "worlds": worlds, "actions": actions,
            "initial": initial if initial is not None else [[w, "s"] for w in worlds],
            "goal": {"account": "acct", "facts": list(goal)},
            "safety": {"forbidden_facts": ["bad"], "preserve_capabilities": list(preserve)}}


def edge(m, source, aid, observation, target, *, effects=()):
    src = m["worlds"][source[0]]["states"][source[1]]
    dst = m["worlds"][target[0]]["states"][target[1]]
    d = {}
    for field in ["facts", "capabilities", "obligations"]:
        d[field] = {"add": sorted(set(dst[field]) - set(src[field])),
                    "remove": sorted(set(src[field]) - set(dst[field]))}
    d["withdraw_approvals"] = sorted(set(src["approvals"]) - set(dst["approvals"]))
    d["external_debit"] = {k: v - m["actions"][aid]["cost"].get(k, 0) - dst["budget"][k]
                           for k, v in src["budget"].items()
                           if v - m["actions"][aid]["cost"].get(k, 0) != dst["budget"][k]}
    src["transitions"].setdefault(aid, []).append({"observation": observation,
        "target": list(target), "effects": list(effects), "delta": d})
    return m


def stay_finish(*, finish=True, horizon=2):
    actions = {"stay": action(kind="wait")}
    if finish:actions["finish"] = action()
    m = model({"w": world({"s": state(), "done": state(facts=["done"])})}, actions, horizon=horizon)
    edge(m, ("w", "s"), "stay", "same", ("w", "s"))
    if finish:edge(m, ("w", "s"), "finish", "finished", ("w", "done"), effects=["goal-effect"])
    return m


def conflict_worlds(count=3, *, informative_probe=False):
    # World i forbids action i; every proper subset has a common completing action.
    names = [chr(97 + i) for i in range(count)]
    worlds = {f"w{i}": world({"s": state(), "done": state(facts=["done"])}) for i in range(count)}
    actions = {a: action() for a in names}
    if informative_probe:actions["probe"] = action(kind="probe")
    m = model(worlds, actions, horizon=2)
    for i, wid in enumerate(worlds):
        for j, aid in enumerate(names):
            if i != j:edge(m, (wid, "s"), aid, "ok", (wid, "done"))
        if informative_probe:edge(m, (wid, "s"), "probe", f"observed-mode-{i}", (wid, "s"))
    return m


def named_three_worlds():
    allowed = {"P1": {"a", "b"}, "P2": {"b", "c"}, "P3": {"a", "c"}}
    m = model({w: world({"s": state(), "done": state(facts=["done"])}) for w in allowed},
              {a: action() for a in "abc"}, horizon=2)
    for wid, actions in allowed.items():
        for aid in sorted(actions):edge(m, (wid,"s"),aid,"ok",(wid,"done"))
    return m


def account_case(wrong=False):
    account = "other-account" if wrong else "acct"
    m = model({"w": world({"s": state(account=account), "done": state(account=account, facts=["done"])})}, {"finish": action()}, horizon=1)
    return edge(m, ("w", "s"), "finish", "ok", ("w", "done"))


def independence(shared=False):
    roots = {"gA": "root-A", "gB": "root-A" if shared else "root-B"}
    caps = [] if shared else ["B"]
    m = model({"w": world({"s": state(capabilities=["A", "B"]),
                            "done": state(facts=["done"], capabilities=caps)}, roots=roots)},
              {"revoke_A": action(independent=[("gA", "gB")])}, horizon=1, preserve=["B"])
    return edge(m, ("w", "s"), "revoke_A", "200", ("w", "done"), effects=["native-revocation"])


def active_false(*, restricted=True):
    worlds = {"revoked": world({"s": state(facts=["revoked"]),
                                "seen": state(facts=["revoked", "checked"])})}
    if restricted:worlds["not-visible-to-querying-client"] = world({"s": state(facts=["live"]), "seen": state(facts=["live", "checked"])})
    m = model(worlds, {"inspect": action(kind="probe")}, horizon=1, goal=["revoked", "checked"])
    for wid in worlds:edge(m, (wid, "s"), "inspect", "active:false", (wid, "seen"))
    return m


def session_probe(*, cleanup=True, approval=True):
    approvals = ["probe", "cleanup"] if approval else ["probe"]
    states = {"s": state(approvals=approvals, budget=2),
              "created": state(facts=["done", "handle-known"], approvals=approvals, budget=1,
                               capabilities=["temp"], obligations=["close:temp"]),
              "closed": state(facts=["done", "handle-known"], approvals=approvals, budget=0)}
    acts = {"probe": action(approval="probe", cost=1, kind="probe")}
    if cleanup:acts["cleanup"] = action(approval="cleanup", cost=1, requires=["handle-known"])
    m = model({"w": world(states)}, acts, horizon=2)
    edge(m, ("w", "s"), "probe", "authenticated", ("w", "created"), effects=["session-created"])
    if cleanup:edge(m, ("w", "created"), "cleanup", "closed", ("w", "closed"), effects=["session-closed"])
    return m


def response_loss(*, reconciliation=True):
    states = {
        "s": state(budget=3),
        "no-effect": state(facts=["done"], budget=2),
        "unknown-handle": state(facts=["done"], budget=2, capabilities=["temp"], obligations=["close:temp"]),
        "absent": state(facts=["done"], budget=1),
        "known": state(facts=["done", "handle-known"], budget=1, capabilities=["temp"], obligations=["close:temp"]),
        "closed": state(facts=["done", "handle-known"], budget=0),
    }
    acts = {"probe": action(kind="probe", cost=1),
            "cleanup": action(cost=1, requires=["handle-known"])}
    if reconciliation:acts["reconcile"] = action(kind="probe", cost=1)
    m = model({"w": world(states)}, acts, horizon=3)
    edge(m, ("w", "s"), "probe", "response-lost", ("w", "no-effect"), effects=["request-no-effect"])
    edge(m, ("w", "s"), "probe", "response-lost", ("w", "unknown-handle"), effects=["session-created-result-lost"])
    if reconciliation:
        edge(m, ("w", "no-effect"), "reconcile", "absent", ("w", "absent"))
        edge(m, ("w", "unknown-handle"), "reconcile", "found:temp", ("w", "known"))
    edge(m, ("w", "known"), "cleanup", "closed", ("w", "closed"), effects=["session-closed"])
    return m


def withdrawal(*, external=True):
    m = model({"w": world({"s": state(), "live": state(facts=["observed"]),
                            "revoked": state(facts=["observed"], approvals=[]),
                            "done": state(facts=["done"])})},
              {"probe": action(kind="probe"), "finish": action(requires=["observed"])}, horizon=2)
    edge(m, ("w", "s"), "probe", "same-result", ("w", "live"))
    if external:edge(m, ("w", "s"), "probe", "same-result", ("w", "revoked"), effects=["external-approval-withdrawal"])
    edge(m, ("w", "live"), "finish", "ok", ("w", "done"))
    return m


def budget_case(enough=True):
    n = 1 if enough else 0
    m = model({"w": world({"s": state(budget=n), "done": state(budget=0, facts=["done"])})},
              {"finish": action(cost=1)}, horizon=1)
    if enough:edge(m, ("w", "s"), "finish", "ok", ("w", "done"))
    return m


def declared_regime_change():
    m = model({"v1": world({"s": state()}, semantics="v1"),
               "v2": world({"s": state(facts=["v2-known"]), "done": state(facts=["done"])}, semantics="v2")},
              {"probe": action(kind="probe"), "finish": action(requires=["v2-known"])},
              initial=[["v1", "s"]], horizon=2)
    edge(m, ("v1", "s"), "probe", "changed-to-v2", ("v2", "s"), effects=["external-regime-change"])
    edge(m, ("v2", "s"), "finish", "ok", ("v2", "done"))
    return m


def four_tasks():
    names = list("ABCD")
    states = {f"s{i}": state(budget=4-i, facts=[f"done:{t}" for t in names[:i]] + (["done"] if i == 4 else [])) for i in range(5)}
    m = model({"w": world(states)}, {f"finish_{t}": action(task=t, cost=1) for t in names},
              horizon=4, initial=[["w", "s0"]], goal=[f"done:{t}" for t in names])
    m["tasks"] = names
    for i,t in enumerate(names):edge(m, ("w", f"s{i}"), f"finish_{t}", f"completed:{t}", ("w", f"s{i+1}"), effects=[f"task-effect:{t}"])
    return m


def regression_cases():
    cases = [
        ("stay-with-finish", stay_finish(), "FEASIBLE"),
        ("stay-only", stay_finish(finish=False, horizon=8), "IMPOSSIBLE"),
        ("three-world-conflict", conflict_worlds(), "IMPOSSIBLE"),
        ("P1-P2-P3-exact-example", named_three_worlds(), "IMPOSSIBLE"),
        ("five-world-conflict", conflict_worlds(5), "IMPOSSIBLE"),
        ("adaptive-probe", conflict_worlds(informative_probe=True), "FEASIBLE"),
        ("correct-account", account_case(), "FEASIBLE"),
        ("wrong-account", account_case(True), "IMPOSSIBLE"),
        ("independent-grants", independence(), "FEASIBLE"),
        ("shared-native-root", independence(True), "IMPOSSIBLE"),
        ("active-false-revoked", active_false(restricted=False), "FEASIBLE"),
        ("active-false-restricted", active_false(), "IMPOSSIBLE"),
        ("session-cleanup", session_probe(), "FEASIBLE"),
        ("session-no-cleanup", session_probe(cleanup=False), "IMPOSSIBLE"),
        ("session-no-cleanup-approval", session_probe(approval=False), "IMPOSSIBLE"),
        ("lost-response-reconcile", response_loss(), "FEASIBLE"),
        ("lost-response-unknown-handle", response_loss(reconciliation=False), "IMPOSSIBLE"),
        ("approval-stable", withdrawal(external=False), "FEASIBLE"),
        ("approval-withdrawn", withdrawal(), "IMPOSSIBLE"),
        ("budget-enough", budget_case(), "FEASIBLE"),
        ("budget-insufficient", budget_case(False), "IMPOSSIBLE"),
        ("declared-external-change", declared_regime_change(), "FEASIBLE"),
        ("four-task-boundary", four_tasks(), "FEASIBLE"),
    ]
    empty = stay_finish(); empty["initial"] = []
    cases.append(("empty-knowledge", empty, "UNKNOWN"))
    no_successor = stay_finish(finish=False); no_successor["worlds"]["w"]["states"]["s"]["transitions"]["stay"] = []
    cases.append(("empty-successor", no_successor, "IMPOSSIBLE"))
    terminal = stay_finish(horizon=0); terminal["initial"] = [["w", "done"]]
    cases.append(("goal-at-zero", terminal, "FEASIBLE"))
    terminal_obligation = session_probe(); terminal_obligation["initial"] = [["w", "created"]]; terminal_obligation["horizon"] = 0
    cases.append(("goal-with-unclosed-obligation-at-zero", terminal_obligation, "IMPOSSIBLE"))
    return [(name, deepcopy(m), expected) for name, m, expected in cases]
