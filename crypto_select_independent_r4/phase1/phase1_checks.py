"""Finite checks from the four allowed inputs; no UE implementation or network."""
import itertools
import json
from collections import Counter
from fractions import Fraction


def closure(E, K, T, C):
    K, T, C = set(K), set(T), set(C)
    while True:
        before = (set(K), set(T), set(C))
        K |= {j-1 for j in K if j >= 2 and j in T}
        T |= {j for j in range(2, E+1) if {j-1, j} <= K}
        C |= {j for j in range(2, E+1) if j-1 in C and j in T}
        if before == (K, T, C):
            return {"K": sorted(K), "T": sorted(T), "C": sorted(C),
                    "intersection": sorted(K & C), "valid": not bool(K & C)}


def subsets(xs):
    xs = list(xs)
    return [{xs[i] for i in range(len(xs)) if b & (1 << i)}
            for b in range(1 << len(xs))]


rows = []


def check(name, inputs, expected, actual):
    rows.append({"id": name, "inputs": inputs, "expected": expected,
                 "actual": actual, "pass": expected == actual})


check("legal_future_key", {"E": 4, "K": [4], "T": [4], "C": [2]},
      {"K": [3, 4], "T": [4], "C": [2], "intersection": [], "valid": True},
      closure(4, [4], [4], [2]))
check("add_token3", {"K": [4], "T": [3, 4], "C": [2]}, False,
      closure(4, [4], [3, 4], [2])["valid"])
check("add_C3", {"K": [4], "T": [4], "C": [2, 3]}, False,
      closure(4, [4], [4], [2, 3])["valid"])
check("add_C4", {"K": [4], "T": [4], "C": [2, 4]}, False,
      closure(4, [4], [4], [2, 4])["valid"])
check("adjacent_keys_generate_token", {"K": [2, 3], "T": [], "C": [2]}, [3],
      closure(4, [2, 3], [], [2])["T"])

count = 0
coverage = abort_sound = True
for E in range(2, 5):
    for K in subsets(range(1, E+1)):
        for T in subsets(range(2, E+1)):
            for C in subsets(range(2, E+1)):
                count += 1
                d = closure(E, K, T, C)
                if not d["valid"]:
                    continue
                for j in C:
                    candidates = [r for r in range(j, E+1)
                                  if set(range(j+1, r+1)) <= set(d["T"])
                                  and (r == E or r+1 not in d["T"])]
                    coverage &= len(candidates) == 1
                    r = candidates[0]
                    abort_sound &= not (K & set(range(j, r+1)))
                    abort_sound &= r == E or r+1 not in T
check("canonical_event_partition", {"E_range": [2, 4], "histories": count}, True, coverage)
check("forbidden_prefix_absent_on_matching_history", {"histories": count}, True, abort_sound)

p = 5
bridge = all((x*r*(y*pow(x, -1, p) % p)+y*(a+s)) % p == y*(r+a+s) % p
             for x, y, r, a, s in itertools.product(range(1, p), range(1, p), range(p), range(1, p), range(p)))
check("ordinary_update_polynomial", {"field": p, "evaluations": 1600}, True, bridge)
reparam = all(sorted(y*pow(x, -1, p) % p for y in range(1, p)) == list(range(1, p)) for x in range(1, p))
check("boundary_bijection", {"field": p}, True, reparam)

# Formal cyclic-group exponent maps only, not actual cryptographic operations.
q = 3
counter_results = {}
for m in [0, 1]:
    honest = Counter()
    real = Counter()
    random = Counter()
    for z1, z2, r1, r2 in itertools.product(range(q), repeat=4):
        honest[(r1, (r1+z1) % q, 2*r2 % q, (r2+z2) % q, (m+z1+z2) % q)] += 1
    for Z, z1, r1, r2 in itertools.product(range(q), repeat=4):
        z2 = (Z-m-z1) % q
        real[(r1, (r1+z1) % q, 2*r2 % q, (r2+z2) % q, Z)] += 1
    for Z, z1, r1, U, V in itertools.product(range(q), repeat=5):
        z2 = (Z-m-z1) % q
        random[(r1, (r1+z1) % q, V, (U+z2) % q, Z)] += 1
    check("honest_embedding_"+str(m), {"q": q, "message_exponent": m}, True, honest == real)
    check("random_embedding_uniform_"+str(m), {"q": q, "message_exponent": m}, [q**5, 1, 1],
          [len(random), min(random.values()), max(random.values())])
    counter_results[str(m)] = {"honest": [[list(k), v] for k, v in sorted(honest.items())],
                                "real": [[list(k), v] for k, v in sorted(real.items())],
                                "random": [[list(k), v] for k, v in sorted(random.items())]}

mu = {1: Fraction(0), 2: Fraction(1, 12), 3: Fraction(-1, 20), 4: Fraction(2, 15)}
L = 4
rectangle = [(j, r) for j in range(2, L+1) for r in range(1, L+1)]
pieces = []
for j, r in rectangle:
    pieces.append(Fraction(0) if r < j else (mu[j]-mu[j-1])/Fraction(L-j+1))
check("rectangular_signed_telescoping", {"L": L, "positions": len(rectangle), "mu": {str(k): str(v) for k,v in mu.items()}},
      str(mu[L]/len(rectangle)), str(sum(pieces)/len(rectangle)))
check("global_draw_count_bound", {"L_range": [2, 20], "Q_range": [0, 20]}, True,
      all((3*L-1)*Q+2*L*L+L+2 <= 10*(Q*L+L*L+1) for L in range(2, 21) for Q in range(21)))

print(json.dumps({"kind": "FINITE_MATHEMATICAL_CHECKS_ONLY", "checks": rows,
                  "counts": {"total": len(rows), "passed": sum(r["pass"] for r in rows)},
                  "all_pass": all(r["pass"] for r in rows),
                  "formal_distribution_counts": counter_results,
                  "uses_other_project_files": False,
                  "cryptographic_implementation": False,
                  "proves_general_security": False}, ensure_ascii=False, indent=2))
