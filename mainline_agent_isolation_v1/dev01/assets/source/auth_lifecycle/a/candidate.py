"""A1, B-A and paired AB1/B-AB selectors over the identical W_r shield."""
from itertools import combinations
from ..schema import prepare, ModelError, State, refs_json, canonical
from ..semantics import terminal, safe, branches
from .model import properties
from .bridge import Feedback
from .joint_reference import Result
from ..b.engine import resources as b_resources


class Limit(Exception):
    pass


class Shield:
    def __init__(self, data, limit):
        self.data = data; self.limit = limit; self.memo = {}; self.edges = {}; self.nodes = 0; self.hits = 0

    def winning(self, state):
        if state in self.memo:self.hits += 1; return self.memo[state]
        if self.nodes >= self.limit:raise Limit()
        self.nodes += 1
        if terminal(self.data, state):answer = True
        elif not state.knowledge or state.boundary or state.remaining == 0 or any(not safe(self.data, x) for x in state.knowledge):answer = False
        else:
            answer = False
            for aid in sorted(self.data["actions"]):
                children, errors = branches(self.data, state, aid); self.edges[(state, aid)] = (children, errors)
                if not errors and children and all(self.winning(c) for c in children.values()):answer = True; break
        self.memo[state] = answer; return answer

    def menu(self, state):
        allowed = {}
        for aid in sorted(self.data["actions"]):
            children, errors = self.edges.get((state, aid), (None, None))
            if children is None:children, errors = branches(self.data, state, aid); self.edges[(state, aid)] = (children, errors)
            if not errors and children and all(self.winning(c) for c in children.values()):allowed[aid] = children
        return allowed


def solve(bundle, *, method="A1", feedback=False, node_limit=100_000, b_limit=100_000):
    """feedback is the ONLY AB paired switch. B-A uses the same safety/controls."""
    diagnostics = []; selector_cache = {}; feedback_provider = None
    try:
        if method not in {"A1", "B-A"}:raise ModelError("unknown selector")
        if type(feedback) is not bool or method == "B-A" and feedback:raise ModelError("invalid feedback mode")
        data, root = prepare(bundle["l0"])
        if not root.knowledge:return Result("UNKNOWN", "empty possibility support")
        if type(node_limit) is not int or node_limit < 0:raise ModelError("candidate limit")
        shield = Shield(data, node_limit)
        if not shield.winning(root):return Result("IMPOSSIBLE", "complete bounded W query", stats={"shield_nodes": shield.nodes})
        if feedback:feedback_provider = Feedback(bundle, b_limit=b_limit)
        source = bundle["source"]; cap = source["budget"]["requests"]

        def point(ref):return bundle["points"][ref[0] + "/" + ref[1]]["point"]
        def signatures(state):return {canonical(properties(source["worlds"][point(ref)["world"]])) for ref in state.knowledge}

        def choose(state, allowed):
            metas = bundle["catalog"]
            # Identical controls and stopping criterion across all selectors.
            for kind in ["cleanup", "stop", "configure"]:
                choices = []
                for aid, children in allowed.items():
                    if metas[aid]["kind"] != kind:continue
                    if kind == "cleanup" and not any(point(x)["sessions"] for x in state.knowledge):continue
                    if kind == "cleanup" and max(len(point(x)["sessions"]) for c in children.values() for x in c.knowledge) >= max(len(point(x)["sessions"]) for x in state.knowledge):continue
                    if kind == "configure":
                        config = metas[aid]["configuration"]
                        g = max(len(b_resources(source["worlds"][point(x)["world"]], config)[2]) for x in state.knowledge)
                        choices.append((g, config, aid))
                    else:choices.append((metas[aid]["requests"], aid))
                if choices:return min(choices)[-1]
            queries = [aid for aid in allowed if metas[aid]["kind"] == "probe"]
            if not queries:return min(allowed)
            base_sigs = signatures(state); count = len(base_sigs)
            weighted_pairs = []
            if feedback_provider is not None:
                report = feedback_provider.get(state)
                if report["status"] == "COMPLETE":weighted_pairs = report["pairs"]
                diagnostics.append({"belief": refs_json(state.knowledge), "remaining": state.remaining, "feedback": report})
            rankings = []
            for aid in queries:
                children = allowed[aid]
                if weighted_pairs:
                    # Pair endpoints are current possible points, projected through
                    # this action's entire transition relation for each observation.
                    remaining = []
                    for observation in children:
                        compatible = set()
                        for ref in state.knowledge:
                            raw = data["worlds"][ref[0]]["states"][ref[1]]["transitions"].get(aid, [])
                            if any(e["observation"] == observation for e in raw):compatible.add(ref[0] + "/" + ref[1])
                        remaining.append(sum(l in compatible and r in compatible for l, r in weighted_pairs))
                    gain = len(weighted_pairs) - max(remaining)
                elif method == "B-A":gain = count - max(len(signatures(c)) for c in children.values())
                else:gain = count * (count - 1) // 2 - max(len(signatures(c)) * (len(signatures(c)) - 1) // 2 for c in children.values())
                cost = max(1, metas[aid]["requests"])
                liabilities = max(len(point(x)["sessions"]) for c in children.values() for x in c.knowledge)
                rankings.append((-gain / cost, liabilities, metas[aid]["requests"], aid))
            picked = min(rankings)[-1]
            diagnostics.append({"belief": refs_json(state.knowledge), "remaining": state.remaining,
                                "selector": method, "feedback_enabled": feedback, "rankings": rankings, "chosen": picked})
            return picked

        def build(state):
            if state in selector_cache:return selector_cache[state]
            head = {"belief": refs_json(state.knowledge), "remaining": state.remaining}
            if terminal(data, state):answer = dict(head, kind="done")
            else:
                allowed = shield.menu(state); aid = choose(state, allowed)
                answer = dict(head, kind="act", action=aid, children={o: build(c) for o, c in allowed[aid].items()})
            selector_cache[state] = answer; return answer
        policy = build(root)
        def value(p):
            if p["kind"] == "done":return max(cap - data["worlds"][w]["states"][n]["budget"]["requests"] for w, n in p["belief"])
            return max(value(c) for c in p["children"].values())
        return Result("FEASIBLE", "all selected actions enter W_(r-1)", policy, value(policy),
                      {"shield_nodes": shield.nodes, "shield_cache_hits": shield.hits, "selector_states": len(selector_cache),
                       "feedback_calls": feedback_provider.calls if feedback_provider else 0, "B_work": feedback_provider.b_work if feedback_provider else 0,
                       "B_guard_checks": feedback_provider.guard_checks if feedback_provider else 0}, diagnostics)
    except Limit:return Result("INCONCLUSIVE", "shield/menu limit; no partial policy accepted", stats={"shield_nodes": shield.nodes}, diagnostics=diagnostics)
    except (ModelError, KeyError, ValueError) as exc:return Result("UNKNOWN", str(exc))
