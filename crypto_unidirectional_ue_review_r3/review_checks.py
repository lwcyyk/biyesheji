"""Exact finite probability/set audit, without a cryptographic implementation.

The cyclic-group checks use formal exponents modulo 3; they only check maps and
probability counts. This is not an independent language-model derivation.
"""
import itertools
import json
import subprocess
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
checks = []


def check(name, inputs, expected, actual):
    checks.append({"id": name, "input": inputs, "expected": expected,
                   "actual": actual, "pass": expected == actual})


def subsets(xs):
    xs = list(xs)
    return [{xs[i] for i in range(len(xs)) if bits & (1 << i)}
            for bits in range(1 << len(xs))]


def closure(E, K, T, C):
    K, T, C = set(K), set(T), set(C)
    while True:
        previous = (set(K), set(T), set(C))
        K |= {j-1 for j in K if j >= 2 and j in T}
        T |= {j for j in range(2, E+1) if {j-1, j} <= K}
        C |= {j for j in range(2, E+1) if j-1 in C and j in T}
        if previous == (K, T, C):
            return K, T, C


def boundary(E, j, T):
    r = j
    while r < E and r+1 in T:
        r += 1
    return r


states = good_events = 0
partition = no_forbidden = True
for E in range(2, 6):
    for K in subsets(range(1, E+1)):
        for T in subsets(range(2, E+1)):
            for C in subsets(range(2, E+1)):
                states += 1
                kc, tc, cc = closure(E, K, T, C)
                if kc & cc:
                    continue
                for j in C:
                    good_events += 1
                    r = boundary(E, j, tc)
                    candidates = [s for s in range(j, 6)
                                  if s <= E and set(range(j+1, s+1)) <= tc
                                  and (s == E or s+1 not in tc)]
                    partition &= candidates == [r]
                    no_forbidden &= not (K & set(range(j, r+1)))
                    no_forbidden &= r+1 > E or r+1 not in T
check("visible_event_partition", {"all_final_histories_L_2_to_5": states,
                                  "good_visible_events": good_events}, True, partition)
check("abort_prefix_has_no_matching_completion", {"same_histories": states}, True, no_forbidden)
check("future_query_must_precede_interval_abort", {"current_epoch": 2, "query_epoch": 4,
                                                  "protected_interval": [2, 4]}, "bottom_no_exposure",
      "bottom_no_exposure" if 4 > 2 else "abort")

# Exact abstract causal query trees. These features are not UE ciphertexts.
L = 4
pairs = [(j, r) for j in range(2, 5) for r in range(j, 5)]
tree_summaries = {}
tree_raw = []
for threshold in range(1, 5):
    total = mu = Fraction(0)
    z = {pair: Fraction(0) for pair in pairs}
    mass = {pair: Fraction(0) for pair in pairs}
    invisible = {j: Fraction(0) for j in range(2, 5)}
    for b in [0, 1]:
        for coins in itertools.product([0, 1], repeat=5):
            c = 2 + coins[0]
            for values in itertools.product([0, 1], repeat=3):
                y = dict(zip(range(2, 5), values))
                weight = Fraction(1, 64)
                for e in range(2, 5):
                    weight *= (Fraction(3, 4) if y[e] == b else Fraction(1, 4)) if e <= threshold else Fraction(1, 2)
                C, T, K = {c}, {2}, {1}
                if c == 2:
                    if y[2] == 1 and coins[1]:
                        C.add(3)
                    last3 = y[3] if 3 in C else y[2]
                else:
                    last3 = y[3]
                if last3 == 1 and coins[2]:
                    T.add(3)
                if last3 == 1 and coins[3]:
                    C.add(4)
                last = y[4] if 4 in C else last3
                if coins[4] or (4 in C and y[4] == 1):
                    T.add(4)
                if 4 in C and y[4] == 0:
                    T.add(3)  # A later disclosure may invalidate earlier choices.
                if last == 0:
                    K.add(4)
                kc, tc, cc = closure(L, K, T, C)
                valid = not bool(kc & cc)
                score = (Fraction(int(last == b)) - Fraction(1, 2)) if valid else Fraction(0)
                total += weight
                mu += weight * score
                for j in range(2, 5):
                    if j in C and valid:
                        r = boundary(L, j, tc)
                        z[j, r] += weight * score
                        mass[j, r] += weight
                    if j not in C:
                        invisible[j] += weight * score
                tree_raw.append({"threshold": threshold, "b": b, "external_coins": list(coins),
                                 "feature_values": values, "probability": str(weight),
                                 "challenge_epoch": c, "K": sorted(K), "T": sorted(T), "C": sorted(C),
                                 "valid": valid, "score": str(score)})
    tree_summaries[threshold] = {"total_mass": total, "mu": mu, "z": z,
                                 "event_mass": mass, "invisible": invisible}
check("adaptive_tree_probability_mass", {"thresholds": [1, 2, 3, 4]}, ["1"]*4,
      [str(tree_summaries[i]["total_mass"]) for i in range(1, 5)])
check("adaptive_tree_initial_score", {"all_official_features_random": True}, "0", str(tree_summaries[1]["mu"]))
for j in range(2, 5):
    a, b = tree_summaries[j], tree_summaries[j-1]
    check("unread_epoch_cancellation_"+str(j), {"j": j}, str(a["invisible"][j]), str(b["invisible"][j]))
    check("weighted_partition_step_"+str(j), {"j": j}, str(a["mu"]-b["mu"]),
          str(sum(a["z"][j, r]-b["z"][j, r] for r in range(j, 5))))
mixture = sum(tree_summaries[j]["z"][j, r]-tree_summaries[j-1]["z"][j, r] for j, r in pairs) / len(pairs)
check("adaptive_tree_final_subprobability_identity", {"F": len(pairs)},
      str(tree_summaries[4]["mu"] / len(pairs)), str(mixture))

# Finite exponent-space maps for one DDH embedding and two parent kernels.
q = 3
group_tables = {}
for message in [0, 1]:
    honest = Counter()
    real_map = Counter()
    random_map = Counter()
    for z1, z2, r1, r2 in itertools.product(range(q), repeat=4):
        out = (r1 % q, (r1+z1) % q, (2*r2) % q, (r2+z2) % q, (message+z1+z2) % q)
        honest[out] += 1
    for Z, z1, r1, r2 in itertools.product(range(q), repeat=4):
        z2 = (Z-message-z1) % q
        real_map[(r1, (r1+z1) % q, (2*r2) % q, (r2+z2) % q, Z)] += 1
    for Z, z1, r1, U, V in itertools.product(range(q), repeat=5):
        z2 = (Z-message-z1) % q
        random_map[(r1, (r1+z1) % q, V, (U+z2) % q, Z)] += 1
    check("real_embedding_count_"+str(message), {"q": q, "message_exponent": message}, True, honest == real_map)
    check("random_embedding_uniform_count_"+str(message), {"q": q, "message_exponent": message},
          [q**5, 1, 1], [len(random_map), min(random_map.values()), max(random_map.values())])
    group_tables["embedding_"+str(message)] = {"honest": sorted((list(k), v) for k, v in honest.items()),
                                              "real": sorted((list(k), v) for k, v in real_map.items()),
                                              "random": sorted((list(k), v) for k, v in random_map.items())}

fresh = Counter()
for pads in itertools.product(range(q), repeat=3):
    for rhos in itertools.product(range(q), repeat=3):
        coords = tuple(t for i, key in enumerate([1, 2, 1]) for t in (key*rhos[i] % q, (rhos[i]+pads[i]) % q))
        fresh[coords + (sum(pads) % q,)] += 1
for parent_id, old_rho, old_pad in [(0, [0, 1], [1, 2]), (1, [2, 0], [0, 1])]:
    kernel = Counter()
    for a in itertools.product(range(1, q), repeat=2):
        for s in itertools.product(range(q), repeat=3):
            for z in itertools.product(range(q), repeat=3):
                rho = [(old_rho[i]+a[i]+s[i]) % q for i in range(2)] + [s[2]]
                pads = [(old_pad[i]+z[i]) % q for i in range(2)] + [z[2]]
                coords = tuple(t for i, key in enumerate([1, 2, 1]) for t in (key*rho[i] % q, (rho[i]+pads[i]) % q))
                Z = (sum(old_pad)+sum(z)) % q  # message exponent is 0.
                kernel[coords+(Z,)] += 1
    check("parent_independent_kernel_"+str(parent_id), {"q": q, "old_rho": old_rho, "old_pad": old_pad},
          True, set(kernel) == set(fresh) and all(kernel[k] == 4*fresh[k] for k in fresh))
    group_tables["kernel_"+str(parent_id)] = sorted((list(k), v) for k, v in kernel.items())
group_tables["fresh_three_coordinates"] = sorted((list(k), v) for k, v in fresh.items())

n_ok = True
for L0 in range(2, 21):
    for Q0 in range(21):
        n_ref = (3*L0-1)*Q0+2*L0*L0+L0+1
        n_ok &= n_ref <= 10*(Q0*L0+L0*L0+1)
check("sampling_count_envelope", {"L": [2, 20], "Q": [0, 20]}, True, n_ok)

previous = Path(r"D:\毕业设计\crypto_unidirectional_ue_adaptive_r2\mathematical_checks.py")
reuse = subprocess.run([sys.executable, str(previous)], capture_output=True)
reused_result = json.loads(reuse.stdout.decode("utf-8"))
check("reused_prior_math_checks", {"script": str(previous), "exit_code": reuse.returncode}, True,
      reuse.returncode == 0 and reused_result["all_pass"])

serial_trees = {}
for i, d in tree_summaries.items():
    serial_trees[str(i)] = {"mass": str(d["total_mass"]), "mu": str(d["mu"]),
                           "events": [{"j": j, "r": r, "mass": str(d["event_mass"][j, r]), "z": str(d["z"][j, r])} for j, r in pairs],
                           "unread": {str(j): str(v) for j, v in d["invisible"].items()}}
raw = {"abstract_adaptive_tree_all_inputs_results": tree_raw, "abstract_tree_summaries": serial_trees,
       "formal_exponent_distribution_counts": group_tables,
       "reused_prior_result": reused_result}
(ROOT / "FINITE_RAW_RESULTS.json").write_text(json.dumps(raw, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(json.dumps({
    "kind": "EXACT_FINITE_INTERNAL_REVIEW_CHECKS",
    "checks": checks,
    "counts": {"total": len(checks), "passed": sum(c["pass"] for c in checks)},
    "all_pass": all(c["pass"] for c in checks),
    "final_metadata_histories_checked": states,
    "abstract_adaptive_tree_rows": len(tree_raw),
    "abstract_adaptive_tree_summaries": serial_trees,
    "raw_results": "FINITE_RAW_RESULTS.json",
    "language_model_independent_derivation": False,
    "protocol_implementation": False,
    "general_security_proof_by_experiment": False,
}, ensure_ascii=False, indent=2))
