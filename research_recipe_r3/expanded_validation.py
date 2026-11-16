"""Expanded finite checks for the resource-spectrum theorem.

Historical validation functions are imported read-only. Formula and direct task
movement remain separate paths. This script has no native-service integration.
"""

from hashlib import sha256
from pathlib import Path
from random import Random
import argparse
import importlib.util
import json
import math
import sys
import time
import traceback

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
DEPENDENCY = ROOT.parent / "research_recipe_r2" / "verify_rebinding.py"
loader = importlib.util.spec_from_file_location("r2_validation_read_only", DEPENDENCY)
r2 = importlib.util.module_from_spec(loader)
loader.loader.exec_module(r2)


class Mismatch(Exception):
    def __init__(self, record):
        self.record = record
        super().__init__(str(record))


def require(condition, record):
    if not condition:
        raise Mismatch(record)


def emit(stream, record):
    stream.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")


def build_random_inputs():
    random = Random(20261104)
    global_rows = []
    seen = set()
    while len(global_rows) < 5000:
        task_count = 5 + len(global_rows) % 2
        demand_count = random.choice([0, 1, 2, 3, 4, 6, 8, 12, 16, 24, 32])
        demands = tuple(sorted(random.sample(range(1 << task_count), demand_count)))
        key = (task_count, demands)
        if key in seen:
            continue
        seen.add(key)
        global_rows.append({"id": len(global_rows), "tasks": task_count, "demands": demands})
    fixed_rows = []
    seen = set()
    while len(fixed_rows) < 500:
        task_count = 7 + len(fixed_rows) % 2
        root_count = random.choice([2, 3])
        demands = tuple(sorted(random.sample(range(1 << task_count), random.randint(1, 5))))
        key = (task_count, demands)
        if key in seen:
            continue
        seen.add(key)
        binding = tuple(random.randrange(root_count) for _ in range(task_count))
        fixed_rows.append({"id": len(fixed_rows), "tasks": task_count, "roots": root_count,
                           "binding": binding, "demands": demands})
    return global_rows, fixed_rows


def exhaustive_tables(output):
    tables = {}
    context_count = 0
    query_count = 0
    direct_nodes = 0
    with (output / "exhaustive_contexts.jsonl").open("w", encoding="utf-8") as stream:
        for task_count in range(1, 7):
            options = []
            for binding in r2.partitions(task_count):
                occupied = max(binding) + 1
                for root_count in range(occupied, task_count + 1):
                    formula_masks = [0] * 5
                    direct_masks = [0] * 5
                    for stop_mask in range(1 << task_count):
                        predicted = r2.formula_distance(binding, root_count, stop_mask)
                        actual, witness, work = r2.direct_search(binding, root_count, stop_mask, 4)
                        direct_nodes += work
                        context_count += 1
                        for budget in range(5):
                            expected = predicted <= budget
                            observed = actual is not None and actual <= budget
                            require(expected == observed, {"stage": "exhaustive", "tasks": task_count,
                                "binding": binding, "roots": root_count, "stop": stop_mask,
                                "r": budget, "predicted": expected, "actual": observed})
                            query_count += 1
                            if expected:
                                formula_masks[budget] |= 1 << stop_mask
                            if observed:
                                direct_masks[budget] |= 1 << stop_mask
                        emit(stream, {"tasks": task_count, "binding": binding, "roots": root_count,
                                      "stop": stop_mask, "D": predicted if math.isfinite(predicted) else "INF",
                                      "reference_distance_within_4": actual, "reference_witness": witness,
                                      "reference_nodes": work})
                    options.append({"roots": root_count, "binding": binding,
                                    "formula_masks": formula_masks, "direct_masks": direct_masks})
            tables[task_count] = sorted(options, key=lambda item: item["roots"])
            print("exhaustive tasks", task_count, "contexts", context_count, flush=True)
    return tables, {"contexts": context_count, "budget_queries": query_count, "direct_nodes": direct_nodes}


def check_random_families(output, tables, global_rows, fixed_rows):
    global_queries = 0
    fixed_queries = 0
    with (output / "random_global_results.jsonl").open("w", encoding="utf-8") as stream:
        for row in global_rows:
            family_mask = sum(1 << demand for demand in row["demands"])
            expected_values = []
            actual_values = []
            for budget in range(5):
                expected = next(item["roots"] for item in tables[row["tasks"]]
                                if family_mask & ~item["formula_masks"][budget] == 0)
                actual = next(item["roots"] for item in tables[row["tasks"]]
                              if family_mask & ~item["direct_masks"][budget] == 0)
                require(expected == actual, {"stage": "random_global", "input": row,
                                             "r": budget, "predicted": expected, "actual": actual})
                expected_values.append(expected)
                actual_values.append(actual)
                global_queries += 1
            k = r2.signature_count(row["tasks"], row["demands"])
            require(actual_values[0] == k, {"stage": "r0", "input": row, "values": actual_values, "k": k})
            require(all(a >= b for a, b in zip(actual_values, actual_values[1:])),
                    {"stage": "monotonicity", "input": row, "values": actual_values})
            emit(stream, {**row, "signature_count": k, "formula_G": expected_values, "reference_G": actual_values})
    with (output / "random_fixed_results.jsonl").open("w", encoding="utf-8") as stream:
        for row in fixed_rows:
            predicted_max = 0
            actual_max = 0
            per_demand = []
            for demand in row["demands"]:
                predicted = r2.formula_distance(row["binding"], row["roots"], demand)
                actual, path, work = r2.direct_search(row["binding"], row["roots"], demand, 4)
                require(actual == predicted, {"stage": "random_fixed", "input": row,
                                             "stop": demand, "predicted": predicted, "actual": actual})
                predicted_max = max(predicted_max, predicted)
                actual_max = max(actual_max, actual)
                per_demand.append({"stop": demand, "D": predicted, "reference": actual,
                                   "witness": path, "nodes": work})
            for budget in range(5):
                require((predicted_max <= budget) == (actual_max <= budget),
                        {"stage": "fixed_family_budget", "input": row, "r": budget})
                fixed_queries += 1
            emit(stream, {**row, "signature_count": r2.signature_count(row["tasks"], row["demands"]),
                          "worst_formula_D": predicted_max, "worst_reference_D": actual_max,
                          "per_demand": per_demand})
    return {"global_families": len(global_rows), "global_optimum_queries": global_queries,
            "fixed_binding_families": len(fixed_rows), "fixed_binding_budget_queries": fixed_queries}


def isolated_construction(k, budget, saving):
    optimum = k - saving
    heavy_count = optimum - 1
    light_count = k - optimum + 1
    repetitions = heavy_count * budget + 1
    classes = [list(range(i * repetitions, (i + 1) * repetitions)) for i in range(heavy_count)]
    lights = list(range(heavy_count * repetitions, heavy_count * repetitions + light_count))
    first = sum(1 << task for task in classes[0] + lights)
    demands = [first] + [sum(1 << task for task in group) for group in classes[1:]]
    moves = [[] for _ in demands]
    for task in lights:
        demands.append(1 << task)
        moves.append([[task, 0, heavy_count]])
    binding = tuple([i for i in range(heavy_count) for _ in range(repetitions)] + [0] * light_count)
    return {"construction": "isolated_R3", "k": k, "r": budget, "saving": saving,
            "task_count": len(binding), "root_count": optimum, "binding": binding,
            "stop_masks": demands, "witnesses": moves, "rigid_classes": classes,
            "repetitions": repetitions, "lower_hypothesis_roots": heavy_count,
            "lower_kind": "all_roots_forced_keep", "trap": 1 << lights[0]}


def check_construction(instance):
    binding = instance["binding"]
    roots = instance["root_count"]
    k = instance["k"]
    budget = instance["r"]
    require(r2.signature_count(len(binding), instance["stop_masks"]) == k,
            {"stage": "spectrum_signature_count", "instance": instance})
    for stop, moves in zip(instance["stop_masks"], instance["witnesses"]):
        current = list(binding)
        require(len(moves) <= budget, {"stage": "witness_budget", "instance": instance})
        for task, old, new in moves:
            require(current[task] == old and old != new and 0 <= new < roots,
                    {"stage": "witness_step", "instance": instance, "move": [task, old, new]})
            current[task] = new
        require(r2.terminal_by_deleting_roots(tuple(current), roots, stop),
                {"stage": "witness_goal", "instance": instance, "stop": stop})
    classes = instance["rigid_classes"]
    signatures = []
    for group in classes:
        group_signatures = {tuple(bool(stop & (1 << task)) for stop in instance["stop_masks"]) for task in group}
        require(len(group_signatures) == 1, {"stage": "rigid_class", "instance": instance})
        signatures.append(next(iter(group_signatures)))
        require(len(group) > instance["lower_hypothesis_roots"] * budget,
                {"stage": "heavy_threshold", "instance": instance})
    require(len(set(signatures)) == len(classes), {"stage": "heavy_separation", "instance": instance})
    if instance["lower_kind"] == "packing":
        require(len(classes) > instance["lower_hypothesis_roots"], {"stage": "packing", "instance": instance})
    else:
        trap = instance["trap"]
        require(trap in instance["stop_masks"] and trap != 0,
                {"stage": "trap_membership", "instance": instance})
        require(all(not trap & (1 << task) for group in classes for task in group),
                {"stage": "trap_preserves_heavy", "instance": instance})


def spectrum_checks(output):
    rows = []
    for k in range(2, 9):
        for budget in range(1, 5):
            for saving in range(k - 1):
                old = r2.spectrum_instance(k, budget, saving)
                old["construction"] = "R2_anchor"
                old["lower_kind"] = "packing" if saving == 0 else "all_roots_forced_keep"
                if saving:
                    old["trap"] = old["stop_masks"][0]
                for instance in [old, isolated_construction(k, budget, saving)]:
                    check_construction(instance)
                    if instance["task_count"] <= 8:
                        instance["exhaustive_lower_configurations"] = r2.exhaustive_below_upper(instance)
                        instance["verification"] = "EXHAUSTIVE_BELOW_VERIFIED_UPPER"
                    else:
                        instance["verification"] = "WITNESS_AND_LOWER_LEMMA_PREMISES"
                    portable = dict(instance)
                    portable["stop_masks_hex"] = [hex(stop) for stop in portable.pop("stop_masks")]
                    if "trap" in portable:
                        portable["trap_hex"] = hex(portable.pop("trap"))
                    rows.append(portable)
    (output / "spectrum.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"spectrum_instances": len(rows), "k_max": 8, "r_max": 4,
            "full_lower_enumeration_instances": sum(row["verification"].startswith("EXHAUSTIVE") for row in rows),
            "max_constructed_tasks": max(row["task_count"] for row in rows)}


def regression_checks(output):
    records = []
    demands = [12, 13, 14]
    best_at_most = None
    best_exact = None
    for roots in range(1, 4):
        for binding in r2.partitions(4, roots):
            if max(binding) >= roots:
                continue
            at_most = all(r2.direct_search(binding, roots, stop, 1)[0] is not None for stop in demands)
            exact = all(r2.exact_move_feasible(binding, roots, stop, 1) for stop in demands)
            if at_most and best_at_most is None:
                best_at_most = roots
            if exact and best_exact is None:
                best_exact = roots
            records.append({"roots": roots, "binding": binding, "at_most_one": at_most, "exact_one": exact})
    require((best_at_most, best_exact) == (2, 3), {"stage": "independent_exact_counterexample", "actual": [best_at_most, best_exact]})
    require(r2.formula_distance((0, 0, 0, 1, 1, 1), 2, 9) == 3,
            {"stage": "both_labels_required"})
    require(not r2.exact_move_feasible((0, 1), 2, 1, 1), {"stage": "fixed_exact_one"})
    require(r2.exact_move_feasible((0, 0), 2, 1, 1), {"stage": "optimized_exact_one"})
    result = {"pass": True, "global_at_most_optimum": best_at_most, "global_exact_optimum": best_exact,
              "demands": demands, "k": r2.signature_count(4, demands), "bindings_checked": records,
              "other_regressions": ["both labels required", "fixed versus optimized binding"]}
    (output / "regressions.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"global_exact_regression_pass": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="results/expanded01")
    args = parser.parse_args()
    output = ROOT / args.out
    output.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    global_rows, fixed_rows = build_random_inputs()
    (output / "random_inputs.json").write_text(json.dumps({"seed": 20261104,
        "global_families": global_rows, "fixed_binding_families": fixed_rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    registry = {"source_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
                "dependency": str(DEPENDENCY), "dependency_sha256": sha256(DEPENDENCY.read_bytes()).hexdigest(),
                "plan_sha256": sha256((ROOT / "VALIDATION_PLAN.json").read_bytes()).hexdigest(),
                "input_sha256": sha256((output / "random_inputs.json").read_bytes()).hexdigest(),
                "inputs_saved_before_evaluation": True}
    (output / "registry.json").write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        tables, exhaustive = exhaustive_tables(output)
        random_results = check_random_families(output, tables, global_rows, fixed_rows)
        print("random families checked", flush=True)
        spectrum = spectrum_checks(output)
        regressions = regression_checks(output)
        summary = {"pass": True, "exhaustive": exhaustive, "random": random_results,
                   "spectrum": spectrum, "regressions": regressions,
                   "elapsed_seconds": time.perf_counter() - started,
                   "scope": "finite verification and lower-lemma premise checks, separated from manual proof and external review"}
    except Exception as error:
        failure = {"pass": False, "error": type(error).__name__, "details": str(error),
                   "traceback": traceback.format_exc(), "counterexample": getattr(error, "record", None)}
        (output / "FAILURE.json").write_text(json.dumps(failure, ensure_ascii=False, indent=2), encoding="utf-8")
        raise
    (output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
