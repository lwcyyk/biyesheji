"""Tiny finite-ring counts and scalar cost formulas only; no UE or attack prototype."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
from math import prod
import json

ROOT = Path(__file__).resolve().parent


def rank_binary(rows):
    pivots = {}
    for value in rows:
        while value:
            index = value.bit_length() - 1
            if index in pivots:
                value ^= pivots[index]
            else:
                pivots[index] = value
                break
    return len(pivots)


rank_checks = []
for d, kappa in [(1, 0), (1, 2), (2, 0), (2, 1), (3, 2)]:
    total = 2 ** ((d + kappa) * d)
    count = sum(rank_binary(rows) == d for rows in product(range(2 ** d), repeat=d + kappa))
    formula = prod(1 - F(1, 2 ** (d + kappa - i)) for i in range(d))
    assert F(count, total) == formula
    assert 1 - formula < F(1, 2 ** kappa)
    rank_checks.append({"d": d, "kappa": kappa, "full_rank_count": count,
                        "total": total, "exact_probability": str(formula), "matches": True})


def collision_check(q, d, t, masses):
    denominator = sum(masses)
    symbols = [i for i, mass in enumerate(masses) if mass]
    average = F(0)
    for matrix in product(range(q), repeat=t * d):
        counts = {}
        for row in product(symbols, repeat=t):
            out = tuple(sum(row[i] * matrix[i * d + j] for i in range(t)) % q for j in range(d))
            counts[out] = counts.get(out, 0) + prod(masses[x] for x in row)
        average += F(sum(x*x for x in counts.values()), denominator ** (2*t))
    average /= q ** (t*d)
    D = q.bit_length() - 1
    collisions = []
    for j in range(1, D + 1):
        buckets = [sum(masses[i] for i in range(q) if i % (2 ** j) == z) for z in range(2 ** j)]
        collisions.append(F(sum(x*x for x in buckets), denominator ** 2))
    excess = sum((2 ** (j*d) - 2 ** ((j-1)*d)) * collisions[j-1] ** t for j in range(1, D+1))
    assert average == (1 + excess) / q ** d
    return {"q": q, "d": d, "t": t, "masses": masses,
            "direct_average_collision": str(average), "formula_average_collision": str((1+excess)/q**d),
            "excess": str(excess), "matches": True}


collision_checks = [collision_check(*x) for x in
                    [(2, 1, 2, [3, 1]), (4, 1, 2, [2, 1, 0, 1]), (4, 2, 2, [2, 1, 0, 1])]]

# A fixed CDF is used solely for a scalar row-count/cost illustration.
cdf = [4643, 13363, 20579, 25843, 29227, 31145, 32103, 32525,
       32689, 32745, 32762, 32766, 32767]
weights = {0: 2 * (cdf[0] + 1)}
for i in range(1, len(cdf)):
    weights[i] = weights[-i] = cdf[i] - cdf[i-1]
assert sum(weights.values()) == 65536
n, ell, D, eta, kappa = 640, 8, 15, 128, 128
d = n + ell
residue_collisions = []
for j in range(1, D+1):
    buckets = {}
    for x, weight in weights.items():
        residue = x % (2**j)
        buckets[residue] = buckets.get(residue, 0) + weight
    residue_collisions.append(F(sum(v*v for v in buckets.values()), 65536**2))


def scalar_certificate(t):
    return sum((2**(j*d)-2**((j-1)*d))*residue_collisions[j-1]**t for j in range(1,D+1)) <= F(4,2**(2*eta))


lower, upper = 0, 16384
assert scalar_certificate(upper)
while upper-lower > 1:
    mid = (lower+upper)//2
    if scalar_certificate(mid):
        upper = mid
    else:
        lower = mid
t_stat = upper
assert scalar_certificate(t_stat) and not scalar_certificate(t_stat-1)
t_comp = 2*d+kappa
costs = []
for log_base in [1,2,4]:
    g = n * ((D+log_base-1)//log_base)
    stat_bits, comp_bits = (g+t_stat)*d*D, (g+t_comp)*d*D
    costs.append({"b": 2**log_base, "g": g, "t_stat_collision_certificate": t_stat,
                  "t_comp": t_comp, "stat_token_bits": stat_bits, "comp_token_bits": comp_bits,
                  "raw_ratio": str(F(stat_bits,comp_bits)),
                  "optimized_comp_baseline_token_bits": comp_bits,
                  "common_security_and_correctness_certified": False})

record = {"scope": "Finite mathematical counts and scalar accounting; no Enc/TG/Upd or distinguisher implementation",
          "rank_counts": rank_checks, "collision_identity_checks": collision_checks,
          "modulus_counterexample": {"q":3,"B":[[1,2],[2,1]],"integer_det":-3,
                                      "mod2_rank":2,"det_mod3":0},
          "parity_counterexample_gap": "1-2^(-d) for chi uniform on {-1,+1}, q=2^D",
          "cost_illustration": {"n":n,"ell":ell,"D":D,"eta_stat":eta,"kappa":kappa,
                                "chi":"Frozen 640 signed CDF; illustrative scalar ledger only",
                                "minimal_rows_for_this_collision_certificate":t_stat,"costs":costs},
          "smudging_control": "W=Z: equality event separates (W,Z) from (W,Z+t) for nonzero unwrapped t",
          "cryptographic_feasibility_or_real_performance_claimed":False}
(ROOT/'finite_mathematical_checks.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({"rank_checks":len(rank_checks),"collision_checks":len(collision_checks),
                  "illustrative_t_stat":t_stat,"t_comp":t_comp,"costs":costs},ensure_ascii=False,indent=2))
