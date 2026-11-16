"""Finite set/field/score checks only. No UE implementation or crypto prototype."""
import itertools
import json
from fractions import Fraction


def closure(L, K, T, C):
    K, T, C = set(K), set(T), set(C)
    while True:
        prev = (set(K), set(T), set(C))
        K |= {j-1 for j in K if j >= 2 and j in T}
        T |= {j for j in range(2, L+1) if {j-1, j} <= K}
        C |= {j for j in range(2, L+1) if j-1 in C and j in T}
        if prev == (K, T, C):
            return {"K": sorted(K), "T": sorted(T), "C": sorted(C),
                    "intersection": sorted(K & C), "legal": not bool(K & C)}


def staged(L, K, T, C):
    K, T, C = set(K), set(T), set(C)
    while True:
        nxt = K | {j-1 for j in K if j >= 2 and j in T}
        if nxt == K:
            break
        K = nxt
    T |= {j for j in range(2, L+1) if {j-1, j} <= K}
    while True:
        nxt = C | {j for j in range(2, L+1) if j-1 in C and j in T}
        if nxt == C:
            break
        C = nxt
    return {"K": sorted(K), "T": sorted(T), "C": sorted(C),
            "intersection": sorted(K & C), "legal": not bool(K & C)}


def subsets(values):
    values = list(values)
    return [{values[i] for i in range(len(values)) if mask & (1 << i)}
            for mask in range(1 << len(values))]


checks = []


def check(name, inputs, expected, actual):
    checks.append({"id": name, "input": inputs, "expected": expected,
                   "actual": actual, "pass": expected == actual})


witnesses = [
    ("all_adaptive_history", [2], [2, 3, 4], [3],
     {"K": [1, 2], "T": [2, 3, 4], "C": [3, 4], "intersection": [], "legal": True}),
    ("select_future_K4", [4], [2, 4], [2],
     {"K": [3, 4], "T": [2, 4], "C": [2], "intersection": [], "legal": True}),
    ("select_publish_Delta3", [4], [2, 3, 4], [2],
     {"K": [1, 2, 3, 4], "T": [2, 3, 4], "C": [2, 3, 4], "intersection": [2, 3, 4], "legal": False}),
    ("select_publish_C3", [4], [2, 4], [2, 3],
     {"K": [3, 4], "T": [2, 4], "C": [2, 3, 4], "intersection": [3, 4], "legal": False}),
    ("select_publish_C4", [4], [2, 4], [2, 4],
     {"K": [3, 4], "T": [2, 4], "C": [2, 4], "intersection": [4], "legal": False}),
]
for name, K, T, C, expected in witnesses:
    check(name, {"L": 4, "K": K, "T": T, "C": C}, expected, closure(4, K, T, C))

count = 0
equal = True
monotone = True
for K in subsets(range(1, 5)):
    for T in subsets(range(2, 5)):
        for C in subsets(range(1, 5)):
            count += 1
            a = closure(4, K, T, C)
            equal &= a == staged(4, K, T, C)
            if not a["legal"]:
                for key in range(1, 5):
                    monotone &= not closure(4, K | {key}, T, C)["legal"]
                for edge in range(2, 5):
                    monotone &= not closure(4, K, T | {edge}, C)["legal"]
                for version in range(1, 5):
                    monotone &= not closure(4, K, T, C | {version})["legal"]
check("joint_vs_GP_staged_closure", {"L": 4, "exhaustive_cases": count}, True, equal)
check("historical_bad_monotonicity", {"L": 4, "exhaustive_cases": count}, True, monotone)

# Finite field bijection and a polynomial identity, not an encryption routine.
p = 7
uniform_reset = True
bridge = True
for x, d in itertools.product(range(1, p), repeat=2):
    values = [(y * pow(x*d % p, -1, p)) % p for y in range(1, p)]
    uniform_reset &= sorted(values) == list(range(1, p))
for x, y, rho, a, s in itertools.product(range(1, p), range(1, p), range(p), range(1, p), range(p)):
    delta = y * pow(x, -1, p) % p
    bridge &= (x*rho*delta + y*(a+s)) % p == (y*(rho+a+s)) % p
check("hidden_boundary_bijection", {"field": p, "nonzero_pairs": 36}, True, uniform_reset)
check("ordinary_bridge_polynomial", {"field": p, "evaluations": 6*6*7*6*7}, True, bridge)

# Future complete-vector consistency: a deterministic field identity.
x = 3
y = [2, 4, 5]
delta4 = [2, 3, 4]
future = [(a*b) % 7 for a, b in zip(y, delta4)] + [6]
recovered = [future[i] * pow(delta4[i], -1, 7) % 7 for i in range(3)]
check("complete_future_vector_after_public_edge", {"field": 7, "future_vector": future, "public_ratios": delta4}, y, recovered)

# Signed scores may cancel; do not replace the proof by independent hit odds.
a = [Fraction(1, 8), Fraction(-1, 12), Fraction(1, 9)]
check("all_signed_mixture", {"scores": list(map(str, a)), "M": 3},
      str(sum(a) / 3), str(sum(v / 3 for v in a)))
mu = {1: Fraction(0), 2: Fraction(1, 8), 3: Fraction(-1, 16), 4: Fraction(1, 10)}
pairs = [(j, r) for j in range(2, 5) for r in range(j, 5)]
parts = []
for j in range(2, 5):
    delta = mu[j] - mu[j-1]
    denom = sum(range(1, 6-j))
    parts.extend(delta * Fraction(r-j+1, denom) for r in range(j, 5))
check("select_weighted_telescope", {"L": 4, "triangular_pairs": pairs, "mu": {str(k): str(v) for k, v in mu.items()}},
      str(mu[4] / len(pairs)), str(sum(parts) / len(pairs)))
check("triangular_guess_count", {"L": 4}, 4*3//2, len(pairs))

print(json.dumps({
    "kind": "FINITE_CLOSURE_AND_ARITHMETIC_AUDIT",
    "checks": checks,
    "counts": {"total": len(checks), "passed": sum(c["pass"] for c in checks)},
    "exhaustive_closure_states": count,
    "all_pass": all(c["pass"] for c in checks),
    "protocol_implementation": False,
    "security_proof_by_experiment": False,
    "Frodo_parameter_experiments": 0,
}, ensure_ascii=False, indent=2))
