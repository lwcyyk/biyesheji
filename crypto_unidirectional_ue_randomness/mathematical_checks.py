"""Deterministic finite arithmetic audit; not a UE implementation or prototype.

No keys, ciphertexts, randomness generation, providers, or cryptographic library.
Checks matrix/field equalities, counting arguments and closure examples only.
"""
import itertools
import json
import math
from fractions import Fraction

checks = []


def check(name, inputs, expected, actual):
    checks.append({"id": name, "input": inputs, "expected": expected,
                   "actual": actual, "pass": expected == actual})


def binary_rank(rows, n):
    rows = list(rows)
    pivot = 0
    for bit in range(n):
        k = next((k for k in range(pivot, n) if rows[k] & (1 << bit)), None)
        if k is None:
            continue
        rows[pivot], rows[k] = rows[k], rows[pivot]
        for j in range(n):
            if j != pivot and rows[j] & (1 << bit):
                rows[j] ^= rows[pivot]
        pivot += 1
    return pivot


for n, expected_count in [(1, 1), (2, 6), (3, 168)]:
    count = sum(binary_rank(rows, n) == n for rows in itertools.product(range(1 << n), repeat=n))
    check("GL_count_" + str(n), {"n": n}, expected_count, count)
    formula = math.prod(Fraction((1 << i) - 1, 1 << i) for i in range(1, n + 1))
    check("GL_probability_" + str(n), {"n": n}, str(formula), str(Fraction(count, 1 << (n*n))))

# Bit-layer ordering / tensor identity, with no cryptographic sampling.
C = [[3, 6], [7, 1]]
S = [[2], [5]]
D = 3
ordinary = [[sum(c[j] * S[j][0] for j in range(2)) % 8] for c in C]
bits = [[(c[j] >> k) & 1 for k in range(D) for j in range(2)] for c in C]
tensor = [S[j][0] * (1 << k) for k in range(D) for j in range(2)]
expanded = [[sum(x*y for x, y in zip(row, tensor)) % 8] for row in bits]
check("Ord_Tensor", {"C": C, "S": S, "D": D, "q": 8}, ordinary, expanded)

# Invertible matrix action on a small support over Z_8.
P = [[1, 2], [0, 1]]
P_inv = [[1, -2], [0, 1]]
support = {0, 1, 7}
accepted = 0
for y in itertools.product(range(8), repeat=2):
    preimage = [sum(y[j] * P_inv[j][i] for j in range(2)) % 8 for i in range(2)]
    accepted += all(v in support for v in preimage)
check("support_count_under_bijection", {"q": 8, "dimension": 2, "P": P, "support": sorted(support)}, 9, accepted)
check("support_probability", {"count": accepted, "total": 64}, str(Fraction(3, 8)**2), str(Fraction(accepted, 64)))

# Full-field freshening remains uniform even with a nonzero extra shift.
frequencies = [sum((3+a+s) % 7 == t for a in range(1, 7) for s in range(7)) for t in range(7)]
check("freshening_full_field", {"old": 3, "a_domain": [1, 6], "s_domain": [0, 6], "q": 7}, [6]*7, frequencies)
frequencies = [sum((4+z) % 7 == t for z in range(7)) for t in range(7)]
check("pad_translation", {"old": 4, "q": 7}, [1]*7, frequencies)

# Rational exponent identities, no group or cipher API.
for vals in [(2, 3, 4, 5, 6, 7, 8), (5, 2, 0, 1, 3, 4, 2)]:
    x, delta, old, a, s, old_pad, new_pad = vals
    residual = Fraction(old+a+s+old_pad+new_pad) - Fraction(x*delta*(old+a+s), x*delta)
    check("decryption_exponent_identity_" + str(x), {"values": vals}, str(old_pad+new_pad), str(residual))


def backward_closure(keys, tokens):
    out = set(keys)
    while True:
        nxt = out | {j-1 for j in out if j in tokens}
        if nxt == out:
            return sorted(out)
        out = nxt


check("legal_old_key_closure", {"keys": [1], "tokens": [2, 3]}, [1], backward_closure([1], [2, 3]))
check("forbidden_future_key_closure", {"keys": [3], "tokens": [2, 3]}, [1, 2, 3], backward_closure([3], [2, 3]))
check("constant_bias_counting_formula", {"alpha": "3/8", "theta": "9/64"},
      str(Fraction(1, 2)+Fraction(3, 8)*(1-Fraction(9, 64))/2),
      str(Fraction(1, 2)+(Fraction(3, 8)-Fraction(3, 8)*Fraction(9, 64))/2))

nominal = []
for n, D, B in [(640, 15, 2), (976, 16, 3), (1344, 16, 4)]:
    s = 1
    B0 = 2*n*s*s+s
    W = 2*n*n*D*s*s+2*n*n*s**3+n*D*s+n*s*s
    cap = Fraction(1 << D, 1 << (B+1))
    nominal.append({"n": n, "D": D, "B": B, "s_lower_bound_example": s,
                    "initial_bound": B0, "update_bound": W,
                    "decoding_bound": str(cap), "sufficient_condition_T1": B0+W < cap,
                    "actual_paper_parameter_conformance": "UNVERIFIED_INPUT_EXAMPLE_ONLY"})

p640 = math.prod(1-2.0**(-i) for i in range(1, 641))
print(json.dumps({
    "kind": "FINITE_MATHEMATICAL_AUDIT_ONLY",
    "checks": checks,
    "counts": {"total": len(checks), "passed": sum(c["pass"] for c in checks)},
    "all_pass": all(c["pass"] for c in checks),
    "uniform_matrix_invertibility_approx_n640": p640,
    "nominal_parameter_examples": nominal,
    "crypto_implementation": False,
    "actual_Frodo_or_group_experiments": 0,
    "proves_general_security": False,
}, ensure_ascii=False, indent=2))
