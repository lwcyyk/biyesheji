"""Finite theorem validator. It implements no deployment or candidate optimizer.

The closed-form distance and the direct single-task transition search are separate.
All output directories are new and all inputs remain local synthetic instances.
"""

from collections import deque
from hashlib import sha256
from itertools import product
from pathlib import Path
import argparse
import json
import math
import time


ROOT = Path(__file__).resolve().parent


def partitions(task_count, maximum_blocks=None):
    """Restricted-growth strings enumerate every unlabeled nonempty partition."""
    maximum_blocks = maximum_blocks or task_count

    def extend(prefix, largest):
        if len(prefix) == task_count:
            yield tuple(prefix)
            return
        for root in range(min(largest + 2, maximum_blocks)):
            yield from extend(prefix + [root], max(root, largest))

    yield from extend([0], 0)


def formula_distance(binding, root_count, stop_mask):
    task_count = len(binding)
    if stop_mask in (0, (1 << task_count) - 1):
        return 0
    if root_count < 2:
        return math.inf
    stop_counts = [0] * root_count
    keep_counts = [0] * root_count
    for task, root in enumerate(binding):
        counts = stop_counts if stop_mask & (1 << task) else keep_counts
        counts[root] += 1
    preferred = [int(keep < stop) for stop, keep in zip(stop_counts, keep_counts)]
    lower_cost = sum(min(stop, keep) for stop, keep in zip(stop_counts, keep_counts))
    if len(set(preferred)) == 2:
        return lower_cost
    if preferred[0] == 0:
        return lower_cost + min(keep - stop for stop, keep in zip(stop_counts, keep_counts))
    return lower_cost + min(stop - keep for stop, keep in zip(stop_counts, keep_counts))


def terminal_by_deleting_roots(binding, root_count, stop_mask):
    """Raw endpoint interpretation, without a distance or majority calculation."""
    stopped_roots = {binding[task] for task in range(len(binding)) if stop_mask & (1 << task)}
    for task, root in enumerate(binding):
        if not stop_mask & (1 << task) and root in stopped_roots:
            return False
    return True


def moved_states(binding, root_count):
    for task, old_root in enumerate(binding):
        for new_root in range(root_count):
            if new_root == old_root:
                continue
            after = list(binding)
            after[task] = new_root
            yield tuple(after), (task, old_root, new_root)


def direct_search(binding, root_count, stop_mask, move_limit):
    queue = deque([(binding, ())])
    seen = {binding}
    inspected = 0
    while queue:
        current, history = queue.popleft()
        inspected += 1
        if terminal_by_deleting_roots(current, root_count, stop_mask):
            return len(history), history, inspected
        if len(history) == move_limit:
            continue
        for successor, action in moved_states(current, root_count):
            if successor not in seen:
                seen.add(successor)
                queue.append((successor, history + (action,)))
    return None, None, inspected


def exact_move_feasible(binding, root_count, stop_mask, moves):
    layer = {binding}
    for _ in range(moves):
        layer = {after for current in layer for after, _ in moved_states(current, root_count)}
    return any(terminal_by_deleting_roots(current, root_count, stop_mask) for current in layer)


def signature_count(task_count, stop_masks):
    signatures = {tuple(bool(mask & (1 << task)) for mask in stop_masks) for task in range(task_count)}
    return len(signatures)


def spectrum_instance(k, budget, saving):
    if saving == 0:
        repetitions = k * budget + 1
        classes = [list(range(i * repetitions, (i + 1) * repetitions)) for i in range(k)]
        stops = [sum(1 << task for task in group) for group in classes]
        binding = tuple(i for i in range(k) for _ in range(repetitions))
        return {"k": k, "r": budget, "saving": saving, "task_count": len(binding),
                "rigid_classes": classes, "repetitions": repetitions, "light_tasks": [],
                "stop_masks": stops, "binding": binding, "root_count": k,
                "witnesses": [[] for _ in stops], "lower_hypothesis_roots": k - 1}
    rigid_count = k - saving - 1
    light_count = saving + 1
    repetitions = rigid_count * budget + 1
    classes = [list(range(i * repetitions, (i + 1) * repetitions)) for i in range(rigid_count)]
    lights = list(range(rigid_count * repetitions, rigid_count * repetitions + light_count))
    all_light = sum(1 << task for task in lights)
    stops = [all_light]
    witnesses = [[]]
    for group in classes[1:]:
        stops.append(sum(1 << task for task in group))
        witnesses.append([])
    for task in lights:
        stops.append(all_light ^ (1 << task))
        witnesses.append([[task, rigid_count, 0]])
    binding = tuple([i for i in range(rigid_count) for _ in range(repetitions)] + [rigid_count] * light_count)
    return {"k": k, "r": budget, "saving": saving, "task_count": len(binding),
            "rigid_classes": classes, "repetitions": repetitions, "light_tasks": lights,
            "stop_masks": stops, "binding": binding, "root_count": rigid_count + 1,
            "witnesses": witnesses, "lower_hypothesis_roots": rigid_count}


def check_spectrum_witness(instance):
    binding = instance["binding"]
    root_count = instance["root_count"]
    assert signature_count(len(binding), instance["stop_masks"]) == instance["k"]
    for stop_mask, moves in zip(instance["stop_masks"], instance["witnesses"]):
        current = list(binding)
        assert len(moves) <= instance["r"]
        for task, old_root, new_root in moves:
            assert current[task] == old_root and old_root != new_root
            assert 0 <= new_root < root_count
            current[task] = new_root
        assert terminal_by_deleting_roots(tuple(current), root_count, stop_mask)
    assert instance["repetitions"] > instance["lower_hypothesis_roots"] * instance["r"]
    representatives = [group[0] for group in instance["rigid_classes"]]
    signatures = {tuple(bool(mask & (1 << task)) for mask in instance["stop_masks"]) for task in representatives}
    assert len(signatures) == len(representatives)
    if instance["light_tasks"]:
        first_request = instance["stop_masks"][0]
        assert all(first_request & (1 << task) for task in instance["light_tasks"])
        assert all(not first_request & (1 << task) for group in instance["rigid_classes"] for task in group)


def exhaustive_below_upper(instance):
    """Enumerates every initial assignment with fewer roots than the checked upper bound."""
    task_count = instance["task_count"]
    upper = instance["root_count"]
    tested = 0
    for binding in partitions(task_count, upper - 1):
        occupied = max(binding) + 1
        for root_count in range(occupied, upper):
            tested += 1
            feasible = True
            for stop_mask in instance["stop_masks"]:
                distance, _, _ = direct_search(binding, root_count, stop_mask, instance["r"])
                if distance is None:
                    feasible = False
                    break
            assert not feasible, (instance, binding, root_count)
    return tested


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="results/rebinding01")
    args = parser.parse_args()
    output = ROOT / args.out
    output.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    contexts = 0
    queries = 0
    nodes = 0
    family_options = {}
    with (output / "contexts.jsonl").open("w", encoding="utf-8") as stream:
        for task_count in range(1, 6):
            options = []
            stop_masks = list(range(1, (1 << task_count) - 1))
            for binding in partitions(task_count):
                occupied = max(binding) + 1
                extra_counts = range(task_count - occupied + 1) if task_count <= 4 else range(2)
                for extras in extra_counts:
                    root_count = occupied + extras
                    predicted_masks = [0, 0, 0]
                    actual_masks = [0, 0, 0]
                    for index, stop_mask in enumerate(stop_masks):
                        predicted = formula_distance(binding, root_count, stop_mask)
                        actual, path, work = direct_search(binding, root_count, stop_mask, 2)
                        nodes += work
                        contexts += 1
                        for budget in range(3):
                            expected = predicted <= budget
                            observed = actual is not None and actual <= budget
                            assert expected == observed, (binding, root_count, stop_mask, budget)
                            queries += 1
                            if expected:
                                predicted_masks[budget] |= 1 << index
                            if observed:
                                actual_masks[budget] |= 1 << index
                        row = {"tasks": task_count, "binding": binding, "roots": root_count,
                               "stop_mask": stop_mask, "formula_distance": predicted if math.isfinite(predicted) else None,
                               "reference_distance_within_2": actual, "reference_witness": path, "reference_nodes": work}
                        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
                    options.append((root_count, predicted_masks, actual_masks))
            if task_count <= 4:
                family_options[task_count] = options
    family_count = 0
    with (output / "families.jsonl").open("w", encoding="utf-8") as stream:
        for task_count, options in family_options.items():
            masks = list(range(1, (1 << task_count) - 1))
            for family_mask in range(1 << len(masks)):
                family_count += 1
                demands = [mask for i, mask in enumerate(masks) if family_mask & (1 << i)]
                values = []
                for budget in range(3):
                    predicted = min(roots for roots, pm, _ in options if not family_mask & ~pm[budget])
                    actual = min(roots for roots, _, am in options if not family_mask & ~am[budget])
                    assert actual == predicted
                    values.append(actual)
                assert values[0] == signature_count(task_count, demands)
                assert values[0] >= values[1] >= values[2]
                if demands:
                    assert min(values) >= 2
                stream.write(json.dumps({"tasks": task_count, "family_mask": family_mask, "G_by_r": values}) + "\n")
    spectrum_rows = []
    for k, budget in product(range(2, 7), range(1, 4)):
        for saving in range(k - 1):
            instance = spectrum_instance(k, budget, saving)
            check_spectrum_witness(instance)
            instance["upper_witness_verified"] = True
            instance["lower_lemma_premises_verified"] = True
            if instance["task_count"] <= 8:
                instance["complete_lower_configurations_tested"] = exhaustive_below_upper(instance)
                instance["optimality_finite_check"] = "EXHAUSTIVE_BELOW_CHECKED_UPPER"
            else:
                instance["optimality_finite_check"] = "LEMMA_PREMISES_ONLY"
            spectrum_rows.append(instance)
    exact_example = {str(moves): exact_move_feasible((0, 1), 2, 1, moves) for moves in range(3)}
    assert exact_example == {"0": True, "1": False, "2": True}
    assert exact_move_feasible((0, 1), 3, 1, 1)
    (output / "spectrum.json").write_text(json.dumps(spectrum_rows, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = {"pass": True, "formula_reference_contexts": contexts, "budget_queries": queries,
               "reference_nodes": nodes, "requirement_families": family_count,
               "family_budgets": [0, 1, 2], "spectrum_instances": len(spectrum_rows),
               "spectrum_exhaustive_instances": sum(x["optimality_finite_check"].startswith("EXHAUSTIVE") for x in spectrum_rows),
               "exact_count_counterexample": exact_example, "exact_one_with_paid_spare": True,
               "source_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
               "elapsed_seconds": time.perf_counter() - started,
               "scope": "finite theorem-validator consistency; conditional proofs and priority remain separate"}
    (output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
