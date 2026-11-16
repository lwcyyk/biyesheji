"""Fresh deterministic scalar verifier. Imports no author code; samples no matrices."""
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json
import platform

OUT = Path(__file__).resolve().parents[1]
SRC = OUT  # Verify the regenerated v2.2 certificate.
AUTHOR = json.loads((SRC / 'FINITE_CERTIFICATES.json').read_text(encoding='utf-8'))
checks = []

def enc(v):
    v = Q(v)
    return {'numerator': str(v.numerator), 'denominator': str(v.denominator)}

def dec(v):
    with localcontext() as ctx:
        ctx.prec = 55
        return str(Decimal(v.numerator) / Decimal(v.denominator))

def read(v):
    return Q(int(v['numerator']), int(v['denominator']))

def test(name, condition):
    checks.append({'id': name, 'pass': bool(condition)})
    if not condition:
        raise AssertionError(name)

def same(name, value, submitted):
    test(name, value == (read(submitted) if isinstance(submitted, dict) else submitted))

def ceil_grid(v, b):
    scale = 1 << b
    quotient, remainder = divmod(v.numerator * scale, v.denominator)
    answer = Q(quotient + bool(remainder), scale)
    test('ceil_grid_' + str(b) + '_' + str(len(checks)),
         0 <= answer - v < Q(1, scale))
    return answer

def taylor_reciprocal(v):
    # Horner form: 1 + x(1 + x/2(1 + ... + x/24)).
    poly = Q(1)
    for k in range(24, 0, -1):
        poly = 1 + v * poly / k
    return 1 / poly

def exponential_up(v):
    return ceil_grid(taylor_reciprocal(v), 64)

def int_hash(v):
    return hashlib.sha256(v.to_bytes((v.bit_length() + 7) // 8, 'big')).hexdigest()

def tail_check(name, num, den, target, submitted):
    test(name + '_claimed_power', (num << target) <= den)
    k = den.bit_length() - num.bit_length()
    while (num << k) > den:
        k -= 1
    while (num << (k + 1)) <= den:
        k += 1
    result = {'exponent': k, 'ratio_le_two_to_minus_exponent': True,
              'next_exponent_fails': True,
              'numerator_bits': num.bit_length(), 'denominator_bits': den.bit_length(),
              'numerator_binary_sha256': int_hash(num),
              'denominator_binary_sha256': int_hash(den)}
    for key in result:
        same(name + '_author_' + key, result[key], submitted[key])
    return result

def pgf(mass, denom, z):
    # Evaluate an aggregated finite law (different aggregation from author code).
    return sum((Q(weight, denom) * z ** value for value, weight in mass.items()), Q(0))

def tail_fraction_parts(g, z, power, threshold, multiplier=1):
    return (multiplier * pow(g.numerator, power) * pow(z.denominator, threshold),
            pow(g.denominator, power) * pow(z.numerator, threshold))

def main():
    N, MOD = 640, 32768
    signed_mass = [9288, 8720, 7216, 5264, 3384, 1918, 958, 422, 164, 56, 17, 4, 1]
    mass = {x: signed_mass[abs(x)] for x in range(-12, 13)}
    den = 1 << 16
    same('chi_total', sum(mass.values()), den)
    same('chi_table', signed_mass, AUTHOR['chi']['mass_zero_and_each_sign'])
    for key, value in {'n': N, 'q': MOD, 'D': 15, 'h0': 450, 'R2_min': 3500}.items():
        same('parameter_' + key, value, AUTHOR['parameters'][key])
    p0, p1 = Q(mass[0], den), Q(mass[1], den)
    variance = sum((Q(x*x*w, den) for x, w in mass.items()), Q(0))
    fourth = sum((Q(x**4*w, den) for x, w in mass.items()), Q(0))
    for key, value in [('max_atom', p0), ('variance', variance), ('fourth_moment', fourth)]:
        same('chi_' + key, value, AUTHOR['chi'][key])
    differences, products, squares = Counter(), Counter(), Counter()
    for x, wx in mass.items():
        squares[x*x] += wx
        for y, wy in mass.items():
            differences[x-y] += wx*wy
            products[x*y] += wx*wy
    same('difference_total', sum(differences.values()), den**2)
    same('product_total', sum(products.values()), den**2)
    same('difference_support', sorted(differences), list(range(-24, 25)))
    for d in range(-24, 25):
        same('difference_mass_' + str(d), differences[d], AUTHOR['nu']['mass'][str(d)])
        same('difference_symmetry_' + str(d), differences[d], differences[-d])
    same('nu1', Q(differences[1], den**2), Q(1629101, 16777216))
    max_atoms = [Q(mass.get((-shift) % MOD, 0) + mass.get((-shift) % MOD - MOD, 0), den)
                 for shift in range(MOD)]
    test('all_32768_translated_zero_atoms', max(max_atoms) == p0)
    test('all_32768_Ord_scalar_weights', all(c.bit_count() >= (c != 0) for c in range(MOD)))
    test('all_32768_Ord_scalar_reconstructions',
         all(sum(((c >> b) & 1) << b for b in range(15)) == c for c in range(MOD)))
    # Exhaustive scalar rounding identity for all 4 labels, including wrap/ties.
    decode = lambda c: ((c + 4096) // 8192) % 4
    correct = lambda r: r < 4096 or r >= MOD - 4096
    test('decode_all_131072_label_residue_cases',
         all((decode((8192*k+r) % MOD) == k) == correct(r)
             for k in range(4) for r in range(MOD)))
    test('decode_negative_tie_correct', decode((-4096) % MOD) == 0)
    test('decode_positive_tie_wrong', decode(4096) == 1)
    zh = Q(2, 5)
    gh = p0 + (1-p0)*zh
    same('H_PGF', gh, AUTHOR['environment']['H']['PGF_upper'])
    hn, hd = tail_fraction_parts(gh, zh, N, 450)
    Hcert = tail_check('H', hn, hd, 73, AUTHOR['environment']['H']['certificate'])
    zr = Q(31, 32)
    gr = pgf(squares, den, zr)
    same('R2_PGF', gr, AUTHOR['environment']['R2']['PGF'])
    rn, rd = tail_fraction_parts(gr, zr, N, 3500)
    Rcert = tail_check('R2', rn, rd, 27, AUTHOR['environment']['R2']['certificate'])
    delta = Q(1, 2**26)
    dyadic_bad = Q(1, 2**73) + Q(1, 2**27)
    same('bad_sum', dyadic_bad, AUTHOR['environment']['sum_dyadic_upper'])
    same('delta', delta, AUTHOR['environment']['adopted_delta'])
    test('bad_budget_strict', dyadic_bad < delta)
    analytic = {}
    for s, K in [(32, 144), (16, 108)]:
        curvature = 2*Q(157, 50)**2*variance - Q(2, 3)*Q(22, 7)**4*fourth/(s*s)
        positive = 1-2*Q(22, 7)**2*variance/(s*s)
        test('curvature_' + str(s), curvature >= K)
        test('positive_' + str(s), positive > 0)
        prefix = 'domain' + str(MOD//s)
        same(prefix + '_curvature', curvature, AUTHOR['analytic_psi'][prefix + '_curvature'])
        same(prefix + '_positive', positive, AUTHOR['analytic_psi'][prefix + '_positive'])
        analytic[str(s)] = {'curvature': enc(curvature), 'positivity_lower': enc(positive)}
    specs = [('L1', 1, 1, 144, 24, 1024), ('L23', 2, 3, 144, 24, 1024),
             ('L47', 4, 7, 108, 24, 2048), ('M815', 8, 15, 144, 4, 1024),
             ('M1663', 16, 63, 144, 1, 1024)]
    groups = []
    for name, lo, hi, K, dmax, domain in specs:
        author = next(g for g in AUTHOR['frequency_groups'] if g['name'] == name)
        exps = {d: exponential_up(Q(K*3950*lo*lo*d*d, MOD*MOD)) for d in range(dmax+1)}
        for d in exps:
            same(name + '_exp_' + str(d), exps[d], author['exp_upper'][str(d)])
        kept = 2*sum(differences[d] for d in range(1, dmax+1))
        bound = Q(den**2-kept, den**2) + sum(
            (2*Q(differences[d], den**2)*exps[d] for d in range(1, dmax+1)), Q(0))
        powered = ceil_grid(bound**N, 80)
        test(name + '_domain_all_kept_t_d_r', all(t*d*12 <= domain
             for t in range(lo, hi+1) for d in range(1, dmax+1)))
        test(name + '_mixture_in_01', 0 <= bound <= 1)
        same(name + '_R', bound, author['R'])
        same(name + '_power', powered, author['R_power640_up'])
        same(name + '_range', [lo, hi], author['range'])
        same(name + '_count', hi-lo+1, author['count'])
        groups.append({'name': name, 'range': [lo, hi], 'count': hi-lo+1,
                       'max_unwrapped_argument': hi*dmax*12, 'domain': domain,
                       'exponential_upper': {str(d): enc(v) for d,v in exps.items()},
                       'R': enc(bound), 'Q': enc(powered),
                       'R_decimal': dec(bound), 'Q_decimal': dec(powered)})
    xs = Q(144*450*64**2, MOD**2)
    xg = 450*p0*p1/64
    test('high_frequency_exponent_comparison', xs >= xg > 0)
    test('high_frequency_small_segment', all(Q(144*450*t*t, MOD**2) >= xg for t in range(64, 1025)))
    test('high_frequency_global_segment', all(t >= MOD//32 for t in range(1025, MOD//2+1)))
    rho = exponential_up(xg)
    high = 1-2*Q(differences[1], den**2)*(1-rho)
    high_pow = ceil_grid(high**N, 80)
    ah = AUTHOR['frequency_groups'][-1]
    for key, value in [('rho', rho), ('small_exponent_at64', xs), ('global_exponent', xg),
                       ('R', high), ('R_power640_up', high_pow)]:
        same('H64_' + key, value, ah[key])
    groups.append({'name': 'H64', 'range': [64, MOD//2], 'count': MOD//2-63,
                   'rho': enc(rho), 'small_exponent_at64': enc(xs), 'global_exponent': enc(xg),
                   'R': enc(high), 'Q': enc(high_pow), 'R_decimal': dec(high), 'Q_decimal': dec(high_pow)})
    covered = [t for g in groups for t in range(g['range'][0], g['range'][1]+1)]
    same('all_positive_representatives_once', covered, list(range(1, MOD//2+1)))
    same('negative_pairs_plus_single_nyquist', 2*(len(covered)-1)+1, MOD-1)
    test('Nyquist_indicator_coefficient_zero', sum(1 if r % 2 == 0 else -1 for r in range(-4096,4096)) == 0)
    Z = sum((g['count']*read(g['Q']) for g in groups), Q(0))/2
    slope = sum((Q(1,4)**j for j in range(8)), Q(0))
    good = Q(1,4)**8 + slope*Z
    upper = good + delta*(1-good)
    lower = ((1-delta)*(Q(1,4)-Z))**8
    init = Q(1,2**132)
    uc, lc = upper/(1-init), (lower-init)/(1-init)
    rounded_slack = Q(8192)*(Q(640,2**64)+Q(1,2**80))
    test('rounding_slack_all_representatives', rounded_slack < Q(1,2**41))
    endpoints = {'Z': Z, 'chord_slope': slope, 'good_row_upper': good,
                 'row_and_full_correct_upper': upper, 'row_lower_Jensen': lower,
                 'initial_correct_conditioned_row_and_full_upper': uc,
                 'initial_correct_conditioned_row_lower': lc,
                 'dyadic_slack_already_in_Z': rounded_slack}
    for key, value in endpoints.items():
        same('endpoint_' + key, value, AUTHOR[key])
    UD, LD = Q('0.005043360'), Q('0.0000135117')
    test('outward_unconditional_upper', upper <= UD)
    test('outward_conditional_upper', uc <= UD)
    test('outward_unconditional_lower', LD <= lower)
    test('outward_conditional_lower', LD <= lc)
    test('good_range_for_chord_and_Jensen', 0 < Z < Q(1,4) and 0 < lower < upper < Q(1,4) and good < 1)
    test('full_error_display', 1-UD == Q('0.994956640') and 100*(1-UD) == Q('99.4956640'))
    zi = Q(21,20)
    gi = pgf(mass, den, zi)
    gp = pgf(products, den**2, zi)
    same('initial_chi_PGF', gi, AUTHOR['initial']['chi_PGF'])
    same('initial_product_PGF', gp, AUTHOR['initial']['product_PGF'])
    inn, ind = tail_fraction_parts(gp, zi, 1280, 4096, multiplier=2)
    inn *= gi.numerator
    ind *= gi.denominator
    Icert = tail_check('initial', inn, ind, 138, AUTHOR['initial']['coordinate_tail_certificate'])
    test('64_coordinate_union', 64*Q(1,2**138) == init)
    result = {'schema': 'fi640-fixed-A-review/recomputed-certificates/1',
              'date_asia_shanghai': '2026-11-11', 'python': platform.python_version(),
              'script_basis': 'Fresh source-derived scalar checker; no author imports or execution',
              'arithmetic': 'Exact integers/Fraction, upward fractional grids 2^-64 and 2^-80; decimals for display only',
              'check_count': len(checks), 'all_passed': True, 'checks': checks,
              'chi_moments': {'max_atom': enc(p0), 'p1': enc(p1), 'variance': enc(variance), 'fourth': enc(fourth)},
              'difference_mass': {str(k):v for k,v in sorted(differences.items())},
              'H_tail': Hcert, 'R2_tail': Rcert, 'bad_sum': enc(dyadic_bad), 'delta': enc(delta),
              'analytic': analytic, 'frequency_groups': groups,
              'endpoints': {k: {'exact': enc(v), 'decimal': dec(v)} for k,v in endpoints.items()},
              'display_margins': {'upper_unconditional': enc(UD-upper), 'upper_conditional': enc(UD-uc),
                                  'lower_unconditional': enc(lower-LD), 'lower_conditional': enc(lc-LD)},
              'initial': {'chi_PGF': enc(gi), 'product_PGF': enc(gp), 'tail': Icert, 'full_failure_upper': enc(init)},
              'symbolic_cases': ['A=0: c_k=f_k; zero-atom bound exact',
                                 'A=I: c_k=u_k+f_k after fixing u',
                                 'A=XY: c_k=((uX)Y)_k+f_k after fixing u,X,Y'],
              'cryptographic_samples': 0, 'Monte_Carlo_runs': 0}
    (OUT/'evidence'/'RECOMPUTED_CERTIFICATES.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'all_passed': True, 'checks': len(checks),
                      'H_exponent': Hcert['exponent'], 'R2_exponent': Rcert['exponent'],
                      'initial_exponent': Icert['exponent'],
                      'Z': dec(Z), 'U': dec(upper), 'L': dec(lower), 'rho': dec(rho)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
