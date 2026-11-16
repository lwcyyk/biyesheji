"""Exact finite sampling/domain checks; not a candidate cryptographic protocol."""
import json
from fractions import Fraction as F

checks = []
raw = {}


def check(name, inputs, expected, actual):
    checks.append({"id": name, "inputs": inputs, "expected": expected,
                   "actual": actual, "pass": expected == actual})


def scalar_domain(m, B):
    k = (m-1).bit_length()
    a = F(m, 1 << k)
    return k, a, (1-a)**B


domain_rows = []
uniform = rank_bijection = signed = True
for L in range(2, 31):
    rectangle = [(j, r) for j in range(2, L+1) for r in range(1, L+1)]
    triangle = [(j, r) for j, r in rectangle if r >= j]
    lam, f = L*(L-1), L*(L-1)//2
    p_valid = F(len(triangle), len(rectangle))
    uniform &= p_valid == F(1, 2) and all(F(1, lam)/p_valid == F(1, f) for _ in triangle)
    decoded = []
    for index in range(f):
        offset = 0
        for j in range(2, L+1):
            size = L-j+1
            if index < offset+size:
                decoded.append((j, j+index-offset))
                break
            offset += size
    rank_bijection &= decoded == triangle
    delta_tri = sum((F((-1)**(j+r)*(j+r), 20*L)-F((-1)**r*r, 30*L))/f for j, r in triangle)
    delta_rect = sum((F(0) if r < j else F((-1)**(j+r)*(j+r), 20*L)-F((-1)**r*r, 30*L))/lam for j, r in rectangle)
    signed &= delta_tri == 2*delta_rect
    domain_rows.append({"L": L, "rectangle": lam, "triangle": f,
                        "admissible_probability": str(p_valid),
                        "conditional_pair_probability": str(F(1, lam)/p_valid),
                        "signed_rect_delta": str(delta_rect), "signed_tri_delta": str(delta_tri)})
raw["domain_rows"] = domain_rows
check("ideal_conditional_triangle_uniform", {"L": [2, 30]}, True, uniform)
check("rank_decoder_bijection", {"L": [2, 30]}, True, rank_bijection)
check("signed_decision_gap_double", {"L": [2, 30]}, True, signed)

L, B = 6, 1
f = L*(L-1)//2
s_rect = (1-scalar_domain(L-1, B)[2])*(1-scalar_domain(L, B)[2])
s_tri = 1-scalar_domain(f, B)[2]
ratio = s_rect/(2*s_tri)
check("finite_index_survival_L6_B1", {"L": L, "B": B},
      ["15/32", "15/16", "1/4"], list(map(str, [s_rect, s_tri, ratio])))
check("finite_ratio_not_ideal_half", {"finite_ratio": str(ratio)}, False, ratio == F(1, 2))
check("finite_decision_gap_example", {"per_pair_gap": "1/5"}, ["3/64", "3/16"],
      list(map(str, [s_rect*F(1, 2)*F(1, 5), s_tri*F(1, 5)])))

L = 7
f = L*(L-1)//2
rect_bits = F(scalar_domain(L-1, 1)[0], scalar_domain(L-1, 1)[1]) + F(scalar_domain(L, 1)[0], scalar_domain(L, 1)[1])
tri_bits = F(scalar_domain(f, 1)[0], scalar_domain(f, 1)[1])
check("expected_metadata_bits_L7", {"L": L}, ["52/7", "160/21"], list(map(str, [rect_bits, tri_bits])))

count_ok = diff_ok = True
for L in range(2, 41):
    for Q in range(41):
        n_tri = (3*L-1)*Q+2*L*L+L+1
        n_rect = (3*L-1)*Q+2*L*L+L+2
        diff_ok &= n_rect-n_tri == 1
        count_ok &= n_tri <= n_rect <= 10*(Q*L+L*L+1)
check("refined_count_difference", {"L": [2, 40], "Q": [0, 40]}, True, diff_ok)
check("common_N_envelope", {"L": [2, 40], "Q": [0, 40]}, True, count_ok)

tau_ok = True
for q in [3, 5, 7, 11]:
    tau = F(q-1, q)
    p_real = tau*F(3, 5)+(1-tau)*F(1, 2)
    p_rand = tau*F(2, 5)+(1-tau)*F(1, 2)
    tau_ok &= p_real-p_rand == tau*F(1, 5)
check("nonzero_conditioning_exact", {"orders": [3, 5, 7, 11]}, True, tau_ok)

general_ok = fair_ok = True
grid = [F(0), F(1, 4), F(1, 2), F(3, 4), F(1)]
for eps in [F(1, 8), F(1, 4)]:
    for p, t in [(F(1, 4), v) for v in grid]:
        ideal = (1-eps)*p+eps*t
        general_ok &= abs(ideal-(1-eps)*p) <= eps
        fair_ok &= abs(ideal-((1-eps)*p+eps*F(1, 2))) <= eps/2
    for r, s in [(r, s) for r in grid for s in grid]:
        ideal_gap = ((1-eps)*F(1, 4)+eps*r)-((1-eps)*F(3, 4)+eps*s)
        zero_gap = (1-eps)*F(1, 4)-(1-eps)*F(3, 4)
        fair_gap = ((1-eps)*F(1, 4)+eps/2)-((1-eps)*F(3, 4)+eps/2)
        general_ok &= abs(ideal_gap-zero_gap) <= 2*eps
        fair_ok &= abs(ideal_gap-fair_gap) <= eps
check("conservative_coupling_errors", {"failure_masses": ["1/8", "1/4"], "conditional_outputs": list(map(str, grid))}, True, general_ok)
check("fair_failure_half_constants", {"same_exact_grid": True}, True, fair_ok)

raw["global_bit_control_flow_example"] = {"correct_single_bit_correlation": "1",
                                          "correlation_after_independent_resample": "1/2",
                                          "scope": "Abstract consistency example only, not a construction attack"}
check("one_global_bit_required", {"abstract_old_response_equals_bit": True}, "1/2",
      str(F(sum(old == new for old in [0, 1] for new in [0, 1]), 4)))
print(json.dumps({"schema": "SELECT-PHASE2-FINITE-CHECKS-1", "checks": checks,
                  "counts": {"total": len(checks), "passed": sum(x["pass"] for x in checks)},
                  "all_pass": all(x["pass"] for x in checks), "raw_data": raw,
                  "general_theorem_verified_by_enumeration": False,
                  "cryptographic_implementation": False}, ensure_ascii=False, indent=2))
