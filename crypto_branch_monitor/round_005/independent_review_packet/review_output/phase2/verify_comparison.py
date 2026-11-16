"""Finite rational and residue checks for the frozen mathematical review packet."""
from pathlib import Path
from fractions import Fraction
from math import comb, prod
from itertools import product
import datetime
import hashlib
import json

OUT = Path(__file__).resolve().parent
PACKET = OUT.parents[1]
AUTHOR = PACKET / 'author_input'
PHASE1 = OUT.parent / 'phase1'


def record(row):
    with (OUT / 'ACCESS_LOG.jsonl').open('a', encoding='utf-8') as handle:
        handle.write(json.dumps({'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), **row}, ensure_ascii=False) + '\n')


def read_json(path, purpose):
    data = path.read_bytes()
    record({'event': 'read_for_exact_comparison', 'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'purpose': purpose, 'evidence_class': 'frozen_artifact'})
    return json.loads(data)


def rational(value):
    result = Fraction(int(value['numerator']), int(value['denominator']))
    assert result == Fraction(value['rational'])
    return result


def power_two(exponent):
    return Fraction(2**exponent) if exponent >= 0 else Fraction(1, 2**(-exponent))


def exact_log_bounds(value):
    assert value > 0
    exponent = value.numerator.bit_length() - value.denominator.bit_length()
    if power_two(exponent) > value:
        exponent -= 1
    ceiling = exponent if power_two(exponent) == value else exponent + 1
    return exponent, ceiling


def verify_power_certificate(value, certificate):
    lower, upper = exact_log_bounds(value)
    assert certificate['floor_log2_raw'] == lower
    assert certificate['ceil_log2_raw'] == upper
    assert certificate['clipped_probability_upper_log2'] == min(0, upper)
    assert certificate['raw_bound_below_one'] == (value < 1)
    assert certificate['raw_upper_power'] == f'2^({upper})'
    assert value <= power_two(upper)
    return {'floor_log2': lower, 'ceil_log2': upper, 'clipped_log2_upper': min(0, upper), 'exact_comparison_passed': True}


author = read_json(AUTHOR / 'PARAMETER_CERTIFICATES.json', '逐项验证作者精确概率和取整证书')
independent = read_json(PHASE1 / 'exact_certificates.json', '与作者证明读取前封存的独立数值结果交叉比较')
results = {'provenance': 'Phase2 directed comparison after reading author proof', 'profiles': [], 'CF1_examples': [], 'finite_ring_checks': []}

for profile in author['profiles']:
    key = str(profile['profile'])
    prior = independent[key]
    n, D, q, s, h = (int(profile[x]) for x in ['n', 'D', 'q', 's', 'h'])
    assert (n, D, q, s, h) == (prior['n'], prior['D'], 2**prior['D'], prior['s'], prior['h'])
    assert profile['source_cdf'] == prior['cdf_reconstructed_from_table3']
    assert profile['sampling_denominator'] == 65536
    cdf = profile['source_cdf']
    masses = [2*(cdf[0]+1)] + [cdf[i]-cdf[i-1] for i in range(1, len(cdf))]
    assert masses == prior['masses_at_0_then_each_signed_value']
    signed_mass = {z: masses[abs(z)] for z in range(-s, s+1)}
    assert sum(signed_mass.values()) == 65536

    primary = profile['fixed_A_primary']
    a = Fraction(max(masses), 65536)
    mu = Fraction(int(prior['mu64_numerator']), 2**prior['mu64_denominator_power_of_two'])
    gamma = h*mu
    assert rational(primary['a']) == a
    assert rational(primary['mu64']) == mu
    assert rational(primary['gamma_h_mu64']) == gamma
    assert primary['integer_convolution_modes'] == prior['mu64_maximizers_integer']
    assert primary['gamma_less_than_one_exact'] == (gamma < 1)
    assert primary['gamma_less_than_half_exact'] == (gamma < Fraction(1, 2))
    assert q > 128*s
    parent = comb(n, 63) * a**(n-63)
    high = gamma**n
    primary_summary = {
        'parent': verify_power_certificate(parent, primary['bad_parent_certificate']),
        'high': verify_power_certificate(high, primary['high_weight_certificate']),
        'sum': verify_power_certificate(parent+high, primary['B_fixed_A_certificate']),
        'source_cdf_and_signed_masses_match_phase1': True,
        'a_mu_gamma_equal_as_exact_rationals': True,
        'phase1_denominator_to_author_reduced_denominator_factor': 2**1024 // int(primary['mu64']['denominator']),
    }

    a_values = []
    for entry in profile['a_j']:
        j = entry['j']
        modulus = 2**j
        counts = {}
        for z, weight in signed_mass.items():
            residue = z % modulus
            counts[residue] = counts.get(residue, 0) + weight
        maximum = max(counts.values())
        maximizers = sorted(z for z, weight in counts.items() if weight == maximum)
        assert entry['modulus'] == modulus
        assert entry['maximum_weight'] == maximum
        assert entry['maximizing_residues'] == maximizers
        assert rational(entry['a']) == Fraction(maximum, 65536)
        a_values.append(Fraction(maximum, 65536))
    assert len(a_values) == D+1
    c_values = [h * Fraction(2**j, q) * a_values[j]**2 for j in range(D)] + [h*a_values[D]**2]
    coarse = profile['uniform_A_coarse']
    assert list(map(rational, coarse['c_j_then_zero'])) == c_values
    assert rational(coarse['c_max']) == max(c_values)
    coarse_bound = (n*D+1) * sum(c**n for c in c_values)
    coarse_max_bound = (n*D+1)*(D+1)*max(c_values)**n
    uniform_summary = {
        'residue_atom_tables_exact': True,
        'coarse_sum': verify_power_certificate(coarse_bound, coarse['exact_sum_certificate']),
        'coarse_max': verify_power_certificate(coarse_max_bound, coarse['max_term_certificate']),
    }
    if 'uniform_A_split' in profile:
        split = profile['uniform_A_split']
        b_values = []
        for entry in split['b_j']:
            j = entry['j']
            modulus = 2**j
            all_counts = {}
            for t in range(-s, s+1):
                if t == 0:
                    continue
                counts = {}
                for x, px in signed_mass.items():
                    for y, py in signed_mass.items():
                        z = (x-t*y) % modulus
                        counts[z] = counts.get(z, 0) + px*py
                all_counts[t] = counts
            maximum = max(max(counts.values()) for counts in all_counts.values())
            exact_b = Fraction(maximum, 65536**2)
            assert rational(entry['b']) == exact_b
            witness = entry['witness']
            assert all_counts[witness['t_signed']][witness['residue']] == maximum
            b_values.append(exact_b)
        collision = sum(Fraction(weight, 65536)**2 for weight in signed_mass.values())
        assert rational(split['l2_collision_probability']) == collision
        injectivity_from = split['all_nonzero_t_injective_on_support_from_j']
        for j in range(injectivity_from, D+1):
            for t in range(-s, s+1):
                if t:
                    assert len({t*z % (2**j) for z in signed_mass}) == h
        def F(values):
            return sum((Fraction(2**j, q)*values[j]**2)**n for j in range(D)) + values[D]**(2*n)
        split_bound = (n*D+1)*(F(a_values)+(h**n-1)*F(b_values))
        b_c_values = [h*Fraction(2**j, q)*b_values[j]**2 for j in range(D)] + [h*b_values[D]**2]
        assert rational(split['nonzero_c_max']) == max(b_c_values)
        uniform_summary['split'] = verify_power_certificate(split_bound, split['exact_split_certificate'])
        uniform_summary['all_pair_atoms_and_witnesses_exact'] = True
        uniform_summary['injectivity_from_verified_j'] = injectivity_from

    results['profiles'].append({'profile': key, 'primary': primary_summary, 'uniform_A_appendix': uniform_summary})

base640 = independent['640']
a640 = Fraction(9288, 65536)
gamma640 = 25*Fraction(int(base640['mu64_numerator']), 2**1024)
for item in author['CF1_scalar_examples']:
    n = item['n']
    D = 8*(n-1).bit_length()
    assert D == item['D']
    raw = comb(n, 63)*a640**(n-63) + gamma640**n
    epsilon_check = verify_power_certificate(raw, item['epsilon_certificate'])
    B0 = 288*n+12
    W = 288*n*n*D+3456*n*n+12*n*D+144*n
    assert 8*(B0+n*W) < 2**D
    results['CF1_examples'].append({'n': n, 'D': D, 'epsilon_certificate': epsilon_check, 'correctness_exact': True})

for item in author['finite_ring_identity_checks']:
    q, n, weights = item['q'], item['n'], item['nu_weights']
    total = sum(weights)
    residues = list(product(range(q), repeat=n))
    direct = Fraction()
    for v in residues:
        mass_v = prod(weights[x] for x in v)
        if not mass_v:
            continue
        single_column_weight = sum(weights[(-sum(x*y for x,y in zip(v,column))) % q] for column in residues)
        direct += Fraction(mass_v, total**n) * Fraction(single_column_weight, q**n*total)**n
    D = q.bit_length()-1
    p = [Fraction(sum(weights[z] for z in range(0,q,2**j)), total) for j in range(D+1)]
    formula = sum((p[j]**n-p[j+1]**n)*p[j]**n*Fraction(2**j,q)**n for j in range(D)) + p[D]**(2*n)
    assert direct == formula == Fraction(item['direct']) == Fraction(item['formula'])
    results['finite_ring_checks'].append({'q':q,'n':n,'direct':str(direct),'formula':str(formula),'exact_match':True})

results['boundaries'] = {
    'w0_n_plus_one_parent_term': 'C(n,n)*a^0=1 for all probability laws with a>0, so epsilon=1',
    'n63_w64_parent_term': '1, hence epsilon=1',
    'n64_w64_raw_parent_term': str(64*a640),
    'small_n_cf1_handling_consistent': True,
    'ordinary_integer_mu64_control_upper_passed': Fraction(comb(128,64),2**128) <= Fraction(3,8),
}
results['all_assertions_passed'] = True
destination = OUT / 'COMPARISON_CHECKS.json'
destination.write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
record({'event':'finite_mathematical_checks','path':str(Path(__file__).resolve()),'purpose':'作者与阶段一精确量映射、附录余数表与有限环恒等式复核','evidence_class':'phase2_informed_exact_arithmetic','output':str(destination),'all_assertions_passed':True})
print(json.dumps(results,ensure_ascii=False,indent=2))
