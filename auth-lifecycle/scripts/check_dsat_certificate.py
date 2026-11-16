"""Independent DSAT mathematical checker. Standard library; no optimizer import.

Only an explicit CLI invocation reads/writes files. check_certificate is pure.
Valid hashes bind bytes; source authenticity and native closure remain outside
this synthetic-only checker.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re


class Rejected(ValueError):
    def __init__(self, code="INVALID_CERTIFICATE"):
        self.code = code
        super().__init__(code)


DEFAULT = {"attempts": 256, "witnesses": 256, "edges": 16384,
           "records": 4096, "integer_bits": 128, "input_bytes": 4194304}


def _encoded(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True, allow_nan=False).encode("utf-8")
    except (ValueError, TypeError, OverflowError, RecursionError):
        raise Rejected() from None


def _hash(component, value):
    return hashlib.sha256(_encoded({"schema": "dsat-proof-binding/1",
                                  "component": component, "payload": value})).hexdigest()


def _keys(value, keys):
    if type(value) is not dict or set(value) != set(keys):
        raise Rejected()


def _id(value):
    if type(value) is not str or not re.fullmatch(r"[A-Za-z0-9_.:/-]{1,160}", value):
        raise Rejected()
    return value


def _int(value, bits, nonnegative=True):
    if type(value) is not int or (nonnegative and value < 0):
        raise Rejected()
    if value.bit_length() > bits:
        raise Rejected("UNKNOWN_RESOURCE_LIMIT")
    return value


def _bool(value):
    if type(value) is not bool:
        raise Rejected()
    return value


def _list(value, count):
    if type(value) is not list:
        raise Rejected()
    if len(value) > count:
        raise Rejected("UNKNOWN_RESOURCE_LIMIT")
    return value


def _ids(value, count):
    result = [_id(v) for v in _list(value, count)]
    if len(result) != len(set(result)):
        raise Rejected()
    return result


def _sha(value):
    if type(value) is not str or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise Rejected()
    return value


def _math(value, lim):
    _keys(value, ("I", "T", "c", "U", "E", "D_P"))
    I = _ids(value["I"], lim["attempts"])
    U = _ids(value["U"], lim["witnesses"])
    T = _ids(value["T"], lim["attempts"])
    D = _ids(value["D_P"], lim["witnesses"])
    if not set(T) <= set(I) or not set(D) <= set(U):
        raise Rejected()
    if type(value["c"]) is not dict or set(value["c"]) != set(I):
        raise Rejected()
    capacities = {i: _int(value["c"][i], lim["integer_bits"]) for i in I}
    edges = []
    for row in _list(value["E"], lim["edges"]):
        if type(row) is not list or len(row) != 2:
            raise Rejected()
        u, i = _id(row[0]), _id(row[1])
        if u not in U or i not in I:
            raise Rejected()
        edges.append((u, i))
    if len(edges) != len(set(edges)):
        raise Rejected()
    return {"I": sorted(I), "T": sorted(T), "c": {i: capacities[i] for i in sorted(I)},
            "U": sorted(U), "E": [list(e) for e in sorted(edges)], "D_P": sorted(D)}


def _network(value, mode):
    # Deliberately independent of the engineering network builder.
    h = len(value["U"])
    nodes = {"s", "t"} | {"U:" + u for u in value["U"]} | {"I:" + i for i in value["I"]}
    arcs = []
    for u in value["U"]:
        arcs.append(("s", "U:" + u, 1, 0))
    for u, i in value["E"]:
        weight = 1 if i in value["T"] and (mode == "m" or u in value["D_P"]) else 0
        arcs.append(("U:" + u, "I:" + i, 1, weight))
    for i in value["I"]:
        arcs.append(("I:" + i, "t", min(value["c"][i], h), 0))
    return nodes, arcs


def _flow(rows, value, nodes, arcs, lim):
    supplied = {}
    legal = {(a, b) for a, b, _, _ in arcs}
    for row in _list(rows, len(arcs)):
        if type(row) is not list or len(row) != 3 or type(row[0]) is not str or type(row[1]) is not str:
            raise Rejected()
        pair = (row[0], row[1])
        if pair not in legal or pair in supplied:
            raise Rejected()
        supplied[pair] = _int(row[2], lim["integer_bits"])
    balance = {n: 0 for n in nodes}
    cost = 0
    for a, b, cap, weight in arcs:
        x = supplied.get((a, b), 0)
        if x > cap:
            raise Rejected()
        balance[a] -= x
        balance[b] += x
        cost += weight * x
    if any(balance[n] != (-value if n == "s" else value if n == "t" else 0) for n in nodes):
        raise Rejected()
    return supplied, cost


def _optimal(cert, value, mode, lim):
    _keys(cert, ("flow", "potentials", "cost"))
    nodes, arcs = _network(value, mode)
    x, cost = _flow(cert["flow"], len(value["U"]), nodes, arcs, lim)
    if _int(cert["cost"], lim["integer_bits"]) != cost:
        raise Rejected()
    potentials = cert["potentials"]
    if type(potentials) is not dict or set(potentials) != nodes:
        raise Rejected()
    pi = {n: _int(potentials[n], lim["integer_bits"], nonnegative=False) for n in nodes}
    residual_count = 0
    for a, b, cap, weight in arcs:
        flow = x.get((a, b), 0)
        if flow < cap:
            residual_count += 1
            if weight + pi[a] - pi[b] < 0:
                raise Rejected()
        if flow > 0:
            residual_count += 1
            if -weight + pi[b] - pi[a] < 0:
                raise Rejected()
    return cost, residual_count


def _bindings(value, math_input, lim):
    names = {"evidence_bundle": "evidence_bundle_digest", "contract": "contract_digest",
             "scope": "scope_digest", "dependency": "dependency_digest",
             "cost_ledger": "cost_ledger_digest", "O_before": "O_before_digest"}
    _keys(value, names)
    for item in _list(value["evidence_bundle"], lim["records"]):
        _sha(item)
    c = value["contract"]
    _keys(c, ("source_version", "source_complete", "capacity_complete", "frontier_complete",
              "external_writers_excluded", "derivations_covered", "inactivity_frames"))
    _id(c["source_version"])
    checks = ("source_complete", "capacity_complete", "frontier_complete", "external_writers_excluded", "derivations_covered")
    for k in checks:
        _bool(c[k])
    _ids(c["inactivity_frames"], lim["records"])
    scope = value["scope"]
    _keys(scope, ("target_attempts", "paths", "open_frontiers", "coverage_complete", "material_scope_only"))
    if sorted(_ids(scope["target_attempts"], lim["attempts"])) != math_input["T"]:
        raise Rejected()
    paths = _ids(scope["paths"], lim["records"])
    fronts = _ids(scope["open_frontiers"], lim["records"])
    _bool(scope["coverage_complete"])
    if _bool(scope["material_scope_only"]) is not True:
        raise Rejected()
    dep = value["dependency"]
    _keys(dep, ("authority_version", "source_version", "evidence_version", "now", "valid_until"))
    for k in ("authority_version", "evidence_version", "now", "valid_until"):
        _int(dep[k], lim["integer_bits"])
    _id(dep["source_version"])
    obs = set()
    for o in _list(value["O_before"], lim["records"]):
        _keys(o, ("id", "kind", "refs", "strict"))
        oid = _id(o["id"])
        if oid in obs:
            raise Rejected()
        obs.add(oid); _id(o["kind"]); _ids(o["refs"], lim["records"]); _bool(o["strict"])
    cost_ids = set()
    for cost in _list(value["cost_ledger"], lim["records"]):
        _keys(cost, ("id", "category", "amount", "unit", "historical"))
        cid = _id(cost["id"])
        if cid in cost_ids:
            raise Rejected()
        cost_ids.add(cid); _id(cost["category"]); _id(cost["unit"])
        _int(cost["amount"], lim["integer_bits"]); _bool(cost["historical"])
    ready = (all(c[k] for k in checks) and scope["coverage_complete"] and bool(paths) and not fronts
             and dep["now"] <= dep["valid_until"] and dep["source_version"] == c["source_version"])
    return names, obs, ready


def check_certificate(packet, expected_math_digest=None, expected_scope_digest=None, limits=None, expected_digests=None):
    """Check mathematics and synthetic binding; never grant native closure."""
    try:
        lim = dict(DEFAULT)
        if limits is not None:
            if type(limits) is not dict or not set(limits) <= set(lim):
                raise Rejected()
            for key, val in limits.items():
                if type(val) is not int or val < 0:
                    raise Rejected()
                lim[key] = val
        return _check(packet, expected_math_digest, expected_scope_digest, lim, expected_digests)
    except Rejected as error:
        return {"status": error.code, "mathematics_accepted": False,
                "native_admission": "SOURCE_OR_REFINEMENT_GAP", "obligation_action": "KEEP_EXISTING"}
    except (KeyError, ValueError, TypeError, RecursionError, OverflowError):
        return {"status": "INVALID_CERTIFICATE", "mathematics_accepted": False,
                "native_admission": "SOURCE_OR_REFINEMENT_GAP", "obligation_action": "KEEP_EXISTING"}


def _check(packet, expected_math, expected_scope, lim, expected_digests):
    if len(_encoded(packet)) > lim["input_bytes"]:
        raise Rejected("UNKNOWN_RESOURCE_LIMIT")
    _keys(packet, ("schema", "mode", "math_input", "bindings", "digests", "proof", "claims", "packet_digest"))
    if packet["schema"] != "dsat-proof/1" or packet["mode"] != "SYNTHETIC_CONTRACT":
        raise Rejected()
    expected_packet = hashlib.sha256(_encoded({"schema": "dsat-packet/1", "packet": {
        k: v for k, v in packet.items() if k != "packet_digest"}})).hexdigest()
    if _sha(packet["packet_digest"]) != expected_packet:
        raise Rejected()
    value = _math(packet["math_input"], lim)
    math_hash = hashlib.sha256(_encoded({"schema": "dsat-math-input/1", "input": value})).hexdigest()
    names, O_ids, ready = _bindings(packet["bindings"], value, lim)
    ds = packet["digests"]
    _keys(ds, ["math_input_digest"] + list(names.values()))
    if _sha(ds["math_input_digest"]) != math_hash:
        raise Rejected()
    if expected_math is not None and _sha(expected_math) != math_hash:
        raise Rejected()
    for component, field in names.items():
        if _sha(ds[field]) != _hash(component, packet["bindings"][component]):
            raise Rejected()
    if expected_scope is not None and _sha(expected_scope) != ds["scope_digest"]:
        raise Rejected()
    if expected_digests is not None:
        if type(expected_digests) is not dict or not set(expected_digests) <= set(ds):
            raise Rejected()
        for field, pinned in expected_digests.items():
            if _sha(pinned) != ds[field]:
                raise Rejected()
    proof, claims = packet["proof"], packet["claims"]
    if type(proof) is not dict or type(claims) is not dict:
        raise Rejected()
    if (claims.get("native_admission") != "SOURCE_OR_REFINEMENT_GAP"
            or claims.get("global_complete") is not False):
        raise Rejected()
    remaining = set(_ids(claims.get("remaining_obligations"), lim["records"]))
    if not O_ids <= remaining:
        raise Rejected()
    if proof.get("kind") == "INFEASIBLE":
        _keys(proof, ("kind", "flow", "cut", "value"))
        _keys(claims, ("result", "conditional_material_closed", "native_admission", "global_complete", "remaining_obligations"))
        nodes, arcs = _network(value, "m")
        v = _int(proof["value"], lim["integer_bits"])
        if v >= len(value["U"]):
            raise Rejected()
        _flow(proof["flow"], v, nodes, arcs, lim)
        cut_rows = _list(proof["cut"], len(nodes))
        if any(type(n) is not str or n not in nodes for n in cut_rows) or len(set(cut_rows)) != len(cut_rows):
            raise Rejected()
        cut = set(cut_rows)
        if "s" not in cut or "t" in cut:
            raise Rejected()
        capacity = sum(cap for a, b, cap, _ in arcs if a in cut and b not in cut)
        if capacity != v or claims["result"] != "EVIDENCE_CONFLICT" or claims["conditional_material_closed"] is not False:
            raise Rejected()
        return {"status": "VALID_MATH_INFEASIBILITY", "result": "EVIDENCE_CONFLICT",
                "mathematics_accepted": True, "F_nonempty": False, "flow_value": v,
                "required_flow": len(value["U"]), "cut_capacity": capacity, "R_T": None, "H_T": None,
                "conditional_material_closed": False, "native_admission": "SOURCE_OR_REFINEMENT_GAP",
                "global_complete": False, "remaining_obligations": sorted(remaining), "solver_called": False}
    _keys(proof, ("kind", "m", "d"))
    if proof["kind"] != "OPTIMUM":
        raise Rejected()
    _keys(claims, ("C_T", "m_T", "d_T", "R_T", "H_T", "conditional_material_closed",
                   "native_admission", "global_complete", "remaining_obligations"))
    m, residual_m = _optimal(proof["m"], value, "m", lim)
    d, residual_d = _optimal(proof["d"], value, "d", lim)
    total = sum(value["c"][i] for i in value["T"])
    expected = {"C_T": total, "m_T": m, "d_T": d, "R_T": total - m, "H_T": total - d}
    if not 0 <= expected["R_T"] <= expected["H_T"]:
        raise Rejected()
    for key, val in expected.items():
        if _int(claims[key], lim["integer_bits"] + 16) != val:
            raise Rejected()
    closed = bool(expected["H_T"] == 0 and ready)
    if _bool(claims["conditional_material_closed"]) != closed:
        raise Rejected()
    return {"status": "VALID_MATH_OPTIMUM", "mathematics_accepted": True, "F_nonempty": True,
            **expected, "conditional_material_closed": closed,
            "native_admission": "SOURCE_OR_REFINEMENT_GAP", "global_complete": False,
            "remaining_obligations": sorted(remaining), "math_input_digest": math_hash,
            "residual_arcs_checked": residual_m + residual_d, "solver_called": False,
            "source_authentication_performed": False}


def _strict_load(raw):
    def pairs(rows):
        result = {}
        for key, value in rows:
            if key in result:
                raise Rejected()
            result[key] = value
        return result

    def constant(_):
        raise Rejected()

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("proof")
    parser.add_argument("--out")
    parser.add_argument("--expected-math-digest")
    parser.add_argument("--expected-scope-digest")
    parser.add_argument("--expected-dependency-digest")
    args = parser.parse_args()
    try:
        path = Path(args.proof)
        if path.stat().st_size > DEFAULT["input_bytes"]:
            raise Rejected("UNKNOWN_RESOURCE_LIMIT")
        result = check_certificate(_strict_load(path.read_text(encoding="utf-8")),
                                   args.expected_math_digest, args.expected_scope_digest,
                                   expected_digests=({"dependency_digest": args.expected_dependency_digest}
                                       if args.expected_dependency_digest else None))
    except (OSError, UnicodeError, ValueError) as error:
        result = {"status": error.code if isinstance(error, Rejected) else "INVALID_CERTIFICATE",
                  "mathematics_accepted": False, "obligation_action": "KEEP_EXISTING"}
    rendered = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.out:
        Path(args.out).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result.get("mathematics_accepted") else 1


if __name__ == "__main__":
    raise SystemExit(main())
