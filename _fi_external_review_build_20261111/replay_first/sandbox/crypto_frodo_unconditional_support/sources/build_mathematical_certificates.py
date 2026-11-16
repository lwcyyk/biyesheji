"""Exact scalar distributions and finite ring counts only. No UE/attack implementation."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal, localcontext
from itertools import product
from math import comb
import hashlib
import json

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "sources"
DATA = json.loads((SRC / "official_cdf_input.json").read_text(encoding="utf-8"))


def ratio(x):
    return {"numerator": str(x.numerator), "denominator": str(x.denominator), "rational": str(x)}


def pow2(e):
    return F(2 ** e) if e >= 0 else F(1, 2 ** (-e))


def log_certificate(x):
    assert x > 0
    t = x.numerator.bit_length() - x.denominator.bit_length()
    floor = t if x >= pow2(t) else t - 1
    ceil = floor if x == pow2(floor) else floor + 1
    assert pow2(floor) <= x <= pow2(ceil)
    assert x < pow2(floor + 1)
    return {"floor_log2_raw": floor, "ceil_log2_raw": ceil,
            "log2_upper_rounding": "toward +infinity to integer, verified by exact cross multiplication",
            "raw_upper_power": f"2^({ceil})", "clipped_probability_upper_log2": min(0, ceil),
            "raw_bound_below_one": x < 1}


def pmf_from_cdf(cdf):
    weights = {0: 2 * (cdf[0] + 1)}
    for i in range(1, len(cdf)):
        weights[i] = weights[-i] = cdf[i] - cdf[i - 1]
    assert sum(weights.values()) == 65536 and min(weights.values()) > 0
    return weights


def maximum_atoms(weights, D):
    result = []
    for j in range(D + 1):
        residues = {}
        for x, w in weights.items():
            residues[x % (2 ** j)] = residues.get(x % (2 ** j), 0) + w
        top = max(residues.values())
        result.append({"j": j, "modulus": 2 ** j, "maximum_weight": top,
                       "maximizing_residues": [x for x, w in sorted(residues.items()) if w == top],
                       "a": ratio(F(top, 65536))})
    return result


def pair_atoms(weights, D):
    result = []
    for j in range(D + 1):
        modulus = 2 ** j
        top, witness = -1, None
        for t in sorted(x for x in weights if x):
            residues = {}
            for x, wx in weights.items():
                for y, wy in weights.items():
                    z = (x - t * y) % modulus
                    residues[z] = residues.get(z, 0) + wx * wy
            value = max(residues.values())
            if value > top:
                top = value
                witness = {"t_signed": t, "residue": min(z for z, w in residues.items() if w == value)}
        result.append({"j": j, "b": ratio(F(top, 65536 ** 2)), "witness": witness})
    return result


def conv64(weights):
    s = max(abs(x) for x in weights)
    base = [weights.get(i, 0) for i in range(-s, s + 1)]
    coeffs = [1]
    for _ in range(64):
        new = [0] * (len(coeffs) + len(base) - 1)
        for i, x in enumerate(coeffs):
            for j, y in enumerate(base):
                new[i + j] += x * y
        coeffs = new
    assert coeffs == coeffs[::-1] and sum(coeffs) == 65536 ** 64
    top = max(coeffs)
    modes = [i - 64 * s for i, value in enumerate(coeffs) if value == top]
    return coeffs, F(top, 65536 ** 64), modes


def residue_sum(d, n, D):
    q = 2 ** D
    return sum((F(2 ** j, q) * d[j] ** 2) ** n for j in range(D)) + d[D] ** (2 * n)


profiles = []
for old in DATA["cdf_checks"]:
    n = old["n"]
    D = 15 if n == 640 else 16
    weights = pmf_from_cdf(old["cdf"])
    s, h = max(weights), len(weights)
    atoms = maximum_atoms(weights, D)
    a = [F(x["a"]["rational"]) for x in atoms]
    cs = [h * F(2 ** j, 2 ** D) * a[j] ** 2 for j in range(D)] + [h * a[D] ** 2]
    B = (n * D + 1) * sum(c ** n for c in cs)
    crude = (n * D + 1) * (D + 1) * max(cs) ** n
    assert B <= crude
    coeffs, mu, modes = conv64(weights)
    convpath = SRC / f"chi_{n}_64fold_coefficients.json"
    convpath.write_text(json.dumps({"offset": -64 * s, "denominator": str(65536 ** 64),
                                   "coefficients": [str(x) for x in coeffs]}, indent=2) + "\n", encoding="utf-8")
    atom = max(F(w, 65536) for w in weights.values())
    bad_parent = comb(n, 63) * atom ** (n - 63)
    gamma = h * mu
    fixed = bad_parent + gamma ** n
    assert 2 ** D > 128 * s and gamma < 1
    profile = {"profile": str(n), "n": n, "D": D, "q": str(2 ** D), "s": s, "h": h,
               "source_cdf": old["cdf"], "sampling_denominator": 65536,
               "a_j": atoms,
               "uniform_A_coarse": {"c_j_then_zero": [ratio(c) for c in cs], "c_max": ratio(max(cs)),
                                    "exact_sum_certificate": log_certificate(B),
                                    "max_term_certificate": log_certificate(crude),
                                    "expression": "(nD+1)*(sum_j<D c_j^n + c_zero^n)"},
               "fixed_A_primary": {"w0": 64, "a": ratio(atom), "mu64": ratio(mu),
                                   "gamma_h_mu64": ratio(gamma), "gamma_less_than_one_exact": True,
                                   "gamma_less_than_half_exact": gamma < F(1, 2),
                                   "integer_convolution_modes": modes,
                                   "no_alias_condition": f"q={2**D}>2*s*64={128*s}",
                                   "convolution_file": str(convpath),
                                   "convolution_sha256": hashlib.sha256(convpath.read_bytes()).hexdigest(),
                                   "bad_parent_certificate": log_certificate(bad_parent),
                                   "high_weight_certificate": log_certificate(gamma ** n),
                                   "B_fixed_A_certificate": log_certificate(fixed),
                                   "expression": "min(1,binom(n,63)*a^(n-63)+(h*mu64)^n)",
                                   "parent_and_high_weight_are_exact_bound_terms": True}}
    with localcontext() as context:
        context.prec = 100
        profile["fixed_A_primary"]["gamma_approx_only"] = str(Decimal(gamma.numerator) / Decimal(gamma.denominator))
        profile["uniform_A_coarse"]["c_max_approx_only"] = str(Decimal(max(cs).numerator) / Decimal(max(cs).denominator))
    if n == 1344:
        bs = pair_atoms(weights, D)
        b = [F(x["b"]["rational"]) for x in bs]
        split = (n * D + 1) * (residue_sum(a, n, D) + (h ** n - 1) * residue_sum(b, n, D))
        nonzero_cs = [h * F(2 ** j, 2 ** D) * b[j] ** 2 for j in range(D)] + [h * b[D] ** 2]
        l2 = sum(F(w, 65536) ** 2 for w in weights.values())
        injection_start = next(j for j in range(D + 1) if all(len({(t*y) % (2**j) for y in weights}) == h for t in weights if t))
        assert all(b[j] == l2 for j in range(injection_start, D + 1))
        profile["uniform_A_split"] = {"b_j": bs, "l2_collision_probability": ratio(l2),
                                      "all_nonzero_t_injective_on_support_from_j": injection_start,
                                      "nonzero_c_max": ratio(max(nonzero_cs)),
                                      "exact_split_certificate": log_certificate(split),
                                      "expression": "(nD+1)*(F(a)+(h^n-1)*F(b)); F(d)=sum_j<D((2^j/q)*d_j^2)^n+d_D^(2n)"}
    profiles.append(profile)


def exact_ring_probability(q, n, raw):
    total = sum(raw)
    nu = [F(x, total) for x in raw]
    vectors = [(v, __import__('functools').reduce(lambda x, y: x*y, (nu[x] for x in v), F(1)))
               for v in product(range(q), repeat=n)]
    direct = F(0)
    for v, pv in vectors:
        counts = {}
        for matrix in product(range(q), repeat=n*n):
            out = tuple(sum(v[i] * matrix[i*n+j] for i in range(n)) % q for j in range(n))
            counts[out] = counts.get(out, 0) + 1
        for e, pe in vectors:
            direct += pv * pe * F(counts.get(tuple((-x) % q for x in e), 0), q ** (n*n))
    D = q.bit_length() - 1
    ps = [sum(nu[x] for x in range(q) if x % (2 ** j) == 0) for j in range(D + 1)]
    formula = sum((ps[j] ** n - ps[j+1] ** n) * ps[j] ** n * F(2 ** j, q) ** n for j in range(D)) + ps[D] ** (2*n)
    assert direct == formula
    return {"q": q, "n": n, "nu_weights": raw, "direct": str(direct), "formula": str(formula)}


ring = [exact_ring_probability(*case) for case in
        [(2, 1, [3, 1]), (4, 1, [4, 1, 2, 1]), (4, 2, [4, 1, 2, 1]), (8, 2, [4, 1, 0, 1, 0, 1, 0, 1])]]
cf_examples = []
atom640 = F(profiles[0]["fixed_A_primary"]["a"]["rational"])
gamma640 = F(profiles[0]["fixed_A_primary"]["gamma_h_mu64"]["rational"])
assert atom640 < F(1, 4) and gamma640 < F(1, 2)
for n in [64, 96, 128, 256, 640, 1024]:
    D = 8 * (n - 1).bit_length()
    q = 2 ** D
    raw = comb(n, 63) * atom640 ** (n - 63) + gamma640 ** n
    W = 288*n*n*D + 3456*n*n + 12*n*D + 144*n
    assert 288*n+12+n*W < q//8
    cf_examples.append({"n": n, "D": D, "chi_profile": "640", "k": n,
                        "epsilon_certificate": log_certificate(raw),
                        "correctness_scalar_inequality": "B0+nW<q/8 verified"})
dependent_actual = sum(F(1, 4) for v, a in product(range(2), repeat=2) if (v*a+v) % 2 == 0)
assert dependent_actual == F(3, 4)
cert = {"schema": "frodo_direct_probability_certificates/1", "round": "ROUND-005", "date": "2026-11-07",
        "provenance": "Informed adversarial review; exact scalar arithmetic; no new independent-review claim",
        "primary_route": "arbitrary fixed A, token F1 anti-concentration with w0=64",
        "log_rounding_rule": "All certified log2 upper bounds are integer ceilings of exact rational expressions, checked without floating point.",
        "large_B_numerators": "Reconstruct from provided rational terms/exponents; huge decimal numerators intentionally not expanded.",
        "profiles": profiles,
        "CF1_scalar_examples": cf_examples,
        "finite_ring_identity_checks": ring,
        "outside_assumption_controls": [
            {"control": "V=E uniform bit, q=2,n=1", "actual": "3/4", "independent_formula": "1/2", "violated": "V/E independence"},
            {"control": "A=0, independent V/E with probabilities3/4,1/4, q=2,n=1", "actual": "3/4", "uniform_A_formula": "11/16", "violated": "uniform A in the 2-adic route"},
            {"control": "Choose a zero parent if either of two independent scalar parents is zero, single-parent zero mass3/4", "actual": "15/16", "single_parent_bound": "3/4", "violated": "one fresh parent without value-based screening"},
            {"control": "chi(-1,0,1)=(1/4,1/2,1/4), q=2", "modular_mu64": "1/2", "integer_mu64_upper": "3/8", "violated": "no aliasing when reusing an integer convolution certificate"}],
        "computation_scope": "Scalar convolution/residue tables and four small-ring identities; no Frodo Enc/Upd or attack prototype."}
(ROOT / "PARAMETER_CERTIFICATES.json").write_text(json.dumps(cert, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
for p in profiles:
    print(p["profile"], "coarse", p["uniform_A_coarse"]["exact_sum_certificate"]["ceil_log2_raw"],
          "fixedA", p["fixed_A_primary"]["B_fixed_A_certificate"]["ceil_log2_raw"],
          "gamma", p["fixed_A_primary"]["gamma_approx_only"][:24])
    if "uniform_A_split" in p: print("split", p["uniform_A_split"]["exact_split_certificate"]["ceil_log2_raw"])
print("finite identities", ring)
