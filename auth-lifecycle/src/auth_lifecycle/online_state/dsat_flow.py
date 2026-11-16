"""Offline integer-flow adapter and proof producer for approved NetworkX 3.7.

The optimizer runs only in an isolated environment with the pinned distribution.
The independent checker is not imported. Native/authority operations are absent.
"""
import importlib.util
import importlib.metadata
from pathlib import Path
import sys
from time import perf_counter_ns

from .dsat_types import (
    DEFAULT_LIMITS, InputError, canonical, digest, fields, integer, math_digest,
    normalize_math, packet_digest,
)


class BackendUnavailable(RuntimeError):
    pass


def _load_backend():
    if sys.prefix == sys.base_prefix:
        raise BackendUnavailable("ISOLATED_ENVIRONMENT_REQUIRED")
    spec = importlib.util.find_spec("networkx")
    if spec is None or spec.origin is None:
        raise BackendUnavailable("MATURE_BACKEND_NOT_INSTALLED")
    if not Path(spec.origin).resolve().is_relative_to(Path(sys.prefix).resolve()):
        raise BackendUnavailable("BACKEND_ORIGIN_OUTSIDE_ENVIRONMENT")
    if importlib.metadata.version("networkx") != "3.7":
        raise BackendUnavailable("DEPENDENCY_INCOMPATIBLE")
    import networkx as nx
    if nx.__version__ != "3.7":
        raise BackendUnavailable("DEPENDENCY_INCOMPATIBLE")
    return nx


def _backend_info(nx):
    return {"name": "NetworkX", "version": nx.__version__, "module": nx.__file__,
            "environment": sys.prefix, "configured": True, "status": "BACKEND_READY",
            "flow_algorithm": "network_simplex", "cut_algorithm": "edmonds_karp",
            "potential_algorithm": "single_source_bellman_ford_path_length", "builtin_backend_only": True}


def backend_status():
    try:
        return _backend_info(_load_backend())
    except (BackendUnavailable, ImportError, importlib.metadata.PackageNotFoundError) as error:
        return {"candidate": "NetworkX", "configured": False, "status": "BACKEND_UNAVAILABLE",
                "reason": str(error) if isinstance(error, BackendUnavailable) else "MATURE_BACKEND_NOT_INSTALLED"}


def build_network(math_input, mode, limits=DEFAULT_LIMITS):
    value = normalize_math(math_input, limits)
    if mode not in {"m", "d"}:
        raise InputError()
    h = len(value["U"])
    target = set(value["T"])
    inactive = set(value["D_P"])
    nodes = ["s", "t"] + ["U:" + u for u in value["U"]] + ["I:" + i for i in value["I"]]
    arcs = []

    def add(tail, head, capacity, cost):
        arcs.append({"id": "a" + str(len(arcs)), "tail": tail, "head": head,
                     "capacity": capacity, "cost": cost})

    for u in value["U"]:
        add("s", "U:" + u, 1, 0)
    for u, i in value["E"]:
        cost = int(i in target and (mode == "m" or u in inactive))
        add("U:" + u, "I:" + i, 1, cost)
    for i in value["I"]:
        add("I:" + i, "t", min(value["c"][i], h), 0)
    return {"mode": mode, "math_input": value, "math_input_digest": math_digest(value),
            "nodes": nodes, "arcs": arcs, "demand": {n: (-h if n == "s" else h if n == "t" else 0) for n in nodes},
            "required_flow": h, "C_T": sum(value["c"][i] for i in value["T"])}


def _graph(nx, spec):
    graph = nx.DiGraph()
    for n in spec["nodes"]:
        graph.add_node(n, demand=spec["demand"][n])
    for a in spec["arcs"]:
        graph.add_edge(a["tail"], a["head"], capacity=a["capacity"], weight=a["cost"])
    return graph


def _sparse_flow(spec, flow, expected_value):
    legal = {(a["tail"], a["head"]) for a in spec["arcs"]}
    if type(flow) is not dict or set(flow) != set(spec["nodes"]):
        raise InputError("INVALID_CERTIFICATE")
    for u, adjacent in flow.items():
        if type(adjacent) is not dict:
            raise InputError("INVALID_CERTIFICATE")
        for v, x in adjacent.items():
            if (u, v) not in legal or type(x) is not int or x < 0:
                raise InputError("INVALID_CERTIFICATE")
    sparse, balance, cost = [], {n: 0 for n in spec["nodes"]}, 0
    for a in spec["arcs"]:
        x = flow[a["tail"]].get(a["head"], 0)
        if type(x) is not int or not 0 <= x <= a["capacity"]:
            raise InputError("INVALID_CERTIFICATE")
        if x:
            sparse.append([a["tail"], a["head"], x])
        balance[a["tail"]] -= x
        balance[a["head"]] += x
        cost += x * a["cost"]
    if any(balance[n] != (-expected_value if n == "s" else expected_value if n == "t" else 0) for n in balance):
        raise InputError("INVALID_CERTIFICATE")
    return sparse, cost


def _potentials(nx, spec, sparse, metrics):
    start = perf_counter_ns()
    flow = {(u, v): x for u, v, x in sparse}
    residual = nx.MultiDiGraph()
    residual.add_nodes_from(spec["nodes"])
    arcs = []
    for a in spec["arcs"]:
        u, v, cap, cost = a["tail"], a["head"], a["capacity"], a["cost"]
        x = flow.get((u, v), 0)
        if x < cap:
            residual.add_edge(u, v, key=a["id"] + ":forward", weight=cost)
            arcs.append((u, v, cost))
        if x > 0:
            residual.add_edge(v, u, key=a["id"] + ":reverse", weight=-cost)
            arcs.append((v, u, -cost))
    super_source = "__dsat_potential_source__"
    residual.add_node(super_source)
    for n in spec["nodes"]:
        residual.add_edge(super_source, n, key="super:" + n, weight=0)
    metrics["backend_calls"].append("bellman_ford:" + spec["mode"])
    distances = nx.single_source_bellman_ford_path_length(residual, super_source, weight="weight", backend="networkx")
    pi = {n: distances[n] for n in spec["nodes"]}
    if any(type(x) is not int for x in pi.values()) or any(c + pi[u] - pi[v] < 0 for u, v, c in arcs):
        raise InputError("INVALID_CERTIFICATE")
    metrics["potential_generation_ns"] += perf_counter_ns() - start
    metrics["residual_arcs"] += len(arcs)
    return pi


def _optimize(nx, spec, metrics):
    if spec["required_flow"] == 0:
        return {"flow": [], "potentials": {n: 0 for n in spec["nodes"]}, "cost": 0}
    graph_start = perf_counter_ns()
    graph = _graph(nx, spec)
    metrics["library_graph_build_ns"] += perf_counter_ns() - graph_start
    metrics["backend_calls"].append("network_simplex:" + spec["mode"])
    start = perf_counter_ns()
    try:
        cost, flow = nx.network_simplex(graph, demand="demand", capacity="capacity", weight="weight", backend="networkx")
    finally:
        metrics[spec["mode"] + "_flow_ns"] += perf_counter_ns() - start
    sparse, actual = _sparse_flow(spec, flow, spec["required_flow"])
    if type(cost) is not int or cost != actual:
        raise InputError("INVALID_CERTIFICATE")
    return {"flow": sparse, "potentials": _potentials(nx, spec, sparse, metrics), "cost": cost}


def _cut_proof(nx, spec, metrics):
    start = perf_counter_ns()
    graph = _graph(nx, spec)
    def algorithm(graph, source, sink, **kwargs):
        return nx.algorithms.flow.edmonds_karp(graph, source, sink, backend="networkx", **kwargs)
    metrics["backend_calls"].append("maximum_flow")
    value, flow = nx.maximum_flow(graph, "s", "t", capacity="capacity", flow_func=algorithm, backend="networkx")
    metrics["backend_calls"].append("minimum_cut")
    cut_value, partition = nx.minimum_cut(graph, "s", "t", capacity="capacity", flow_func=algorithm, backend="networkx")
    if type(value) is not int or type(cut_value) is not int or value != cut_value or not 0 <= value < spec["required_flow"]:
        raise InputError("UNVERIFIED_INFEASIBILITY")
    sparse, _ = _sparse_flow(spec, flow, value)
    left, right = partition
    if "s" not in left or "t" in left or set(left) | set(right) != set(spec["nodes"]) or set(left) & set(right):
        raise InputError("UNVERIFIED_INFEASIBILITY")
    actual_cut = sum(a["capacity"] for a in spec["arcs"] if a["tail"] in left and a["head"] not in left)
    if actual_cut != value:
        raise InputError("UNVERIFIED_INFEASIBILITY")
    metrics["cut_generation_ns"] += perf_counter_ns() - start
    return {"kind": "INFEASIBLE", "flow": sparse, "cut": sorted(left), "value": value}


def solve(math_input, limits=DEFAULT_LIMITS, *, bindings=None):
    """Optimize both integer objectives; a bound proof packet is optional."""
    started = perf_counter_ns()
    try:
        mnet = build_network(math_input, "m", limits)
        dnet = build_network(math_input, "d", limits)
    except InputError as error:
        return {"status": error.code, "obligation_action": "KEEP_EXISTING", "solved": False}
    common = {
            "math_input_digest": mnet["math_input_digest"], "C_T": mnet["C_T"],
            "network_nodes": len(mnet["nodes"]), "network_arcs": len(mnet["arcs"]),
            "network_build_ns": perf_counter_ns() - started,
            "m_network": mnet, "d_network": dnet,
            "obligation_action": "KEEP_EXISTING", "native_admission": "SOURCE_OR_REFINEMENT_GAP", "global_complete": False}
    load_start = perf_counter_ns()
    try:
        nx = _load_backend()
    except (BackendUnavailable, ImportError, importlib.metadata.PackageNotFoundError) as error:
        return {**common, "status": "BACKEND_UNAVAILABLE", "solved": False,
                "backend": {"configured": False, "reason": str(error) if isinstance(error, BackendUnavailable) else "MATURE_BACKEND_NOT_INSTALLED"},
                "m_T": None, "d_T": None, "R_T": None, "H_T": None, "C_flow_ns": None}
    metrics = {"backend_import_ns": perf_counter_ns() - load_start, "network_build_ns": common["network_build_ns"],
               "library_graph_build_ns": 0, "m_flow_ns": 0, "d_flow_ns": 0,
               "potential_generation_ns": 0, "cut_generation_ns": 0, "proof_packet_ns": 0,
               "backend_calls": [], "residual_arcs": 0}
    try:
        try:
            m = _optimize(nx, mnet, metrics)
        except (nx.NetworkXUnfeasible, nx.NetworkXError):
            cut = _cut_proof(nx, mnet, metrics)
            packet_start = perf_counter_ns()
            packet = (assemble_infeasible_packet(mnet["math_input"], bindings, cut["flow"], cut["cut"], cut["value"])
                      if bindings is not None else None)
            metrics["proof_packet_ns"] = perf_counter_ns() - packet_start
            metrics["total_solver_ns"] = perf_counter_ns() - started
            return {**common, "status": "EVIDENCE_CONFLICT", "solved": True, "feasible": False,
                    "backend": _backend_info(nx), "certificate": cut, "proof_packet": packet,
                    "m_T": None, "d_T": None, "R_T": None, "H_T": None,
                    "C_flow_ns": metrics["m_flow_ns"], "metrics": metrics}
        d = _optimize(nx, dnet, metrics)
        R, H = common["C_T"] - m["cost"], common["C_T"] - d["cost"]
        if not 0 <= R <= H:
            raise InputError("INVALID_CERTIFICATE")
        packet_start = perf_counter_ns()
        packet = assemble_optimum_packet(mnet["math_input"], bindings, m, d) if bindings is not None else None
        metrics["proof_packet_ns"] = perf_counter_ns() - packet_start
        metrics["total_solver_ns"] = perf_counter_ns() - started
        return {**common, "status": "MATH_OPTIMAL", "solved": True, "feasible": True,
                "backend": _backend_info(nx), "certificates": {"m": m, "d": d}, "proof_packet": packet,
                "m_T": m["cost"], "d_T": d["cost"], "R_T": R, "H_T": H,
                "C_flow_ns": metrics["m_flow_ns"] + metrics["d_flow_ns"], "metrics": metrics}
    except MemoryError:
        error_code = "UNKNOWN_RESOURCE_LIMIT"
    except InputError as error:
        error_code = error.code
    except nx.NetworkXUnbounded:
        error_code = "INVALID_CERTIFICATE"
    except (nx.NetworkXException, KeyError, TypeError, ValueError):
        error_code = "INVALID_CERTIFICATE"
    metrics["total_solver_ns"] = perf_counter_ns() - started
    return {**common, "status": error_code, "solved": False, "backend": _backend_info(nx),
            "m_T": None, "d_T": None, "R_T": None, "H_T": None, "metrics": metrics}


def make_bindings(bundle, projection):
    """Redacted synthetic context only; no evidence payload, handle or token is exported."""
    if bundle.get("mode") != "SYNTHETIC_CONTRACT" or projection.get("math_input") is None:
        raise InputError()
    scope = projection["scope"]
    return {
        "evidence_bundle": sorted(digest("envelope", e) for e in bundle["history"] + bundle["envelopes"]),
        "contract": dict(bundle["contract"]),
        "scope": {"target_attempts": list(projection["math_input"]["T"]), "paths": list(scope["paths"]),
                  "open_frontiers": list(projection["open_frontiers"]),
                  "coverage_complete": projection["source_scope_preconditions_declared"], "material_scope_only": True},
        "dependency": {"authority_version": projection["authority_version"],
                       "source_version": bundle["contract"]["source_version"],
                       "evidence_version": 1, "now": bundle["authority"]["now"],
                       "valid_until": bundle["authority"]["now"]},
        "cost_ledger": list(projection["costs_retained"]),
        "O_before": list(projection["obligations_proposed"]),
    }


_BINDINGS = {"evidence_bundle": "evidence_bundle_digest", "contract": "contract_digest",
             "scope": "scope_digest", "dependency": "dependency_digest",
             "cost_ledger": "cost_ledger_digest", "O_before": "O_before_digest"}


def _base_packet(math_input, bindings):
    value = normalize_math(math_input)
    fields(bindings, _BINDINGS)
    # Copy via JSON-equivalent serialization to prevent caller mutation of a bound packet.
    import json
    bindings = json.loads(canonical(bindings))
    return {"schema": "dsat-proof/1", "mode": "SYNTHETIC_CONTRACT", "math_input": value,
            "bindings": bindings, "digests": {"math_input_digest": math_digest(value),
                **{field: digest(key, bindings[key]) for key, field in _BINDINGS.items()}}}


def assemble_optimum_packet(math_input, bindings, m_certificate, d_certificate):
    """Serialize supplied vectors; this function neither solves nor verifies them."""
    packet = _base_packet(math_input, bindings)
    value = packet["math_input"]
    total = sum(value["c"][i] for i in value["T"])
    m = integer(m_certificate["cost"])
    d = integer(d_certificate["cost"])
    context = packet["bindings"]
    contract, scope, dep = context["contract"], context["scope"], context["dependency"]
    source_ready = (scope["coverage_complete"] and bool(scope["paths"]) and not scope["open_frontiers"]
                    and all(contract[k] for k in ("source_complete", "capacity_complete", "frontier_complete",
                                                  "external_writers_excluded", "derivations_covered"))
                    and dep["now"] <= dep["valid_until"] and dep["source_version"] == contract["source_version"])
    packet["proof"] = {"kind": "OPTIMUM", "m": m_certificate, "d": d_certificate}
    packet["claims"] = {"C_T": total, "m_T": m, "d_T": d, "R_T": total - m, "H_T": total - d,
                        "conditional_material_closed": bool(total == d and source_ready),
                        "native_admission": "SOURCE_OR_REFINEMENT_GAP", "global_complete": False,
                        "remaining_obligations": [o["id"] for o in context["O_before"]]}
    packet["packet_digest"] = packet_digest(packet)
    return packet


def assemble_infeasible_packet(math_input, bindings, flow, cut, value):
    packet = _base_packet(math_input, bindings)
    packet["proof"] = {"kind": "INFEASIBLE", "flow": flow, "cut": cut, "value": value}
    packet["claims"] = {"result": "EVIDENCE_CONFLICT", "conditional_material_closed": False,
                        "native_admission": "SOURCE_OR_REFINEMENT_GAP", "global_complete": False,
                        "remaining_obligations": [o["id"] for o in packet["bindings"]["O_before"]]}
    packet["packet_digest"] = packet_digest(packet)
    return packet
