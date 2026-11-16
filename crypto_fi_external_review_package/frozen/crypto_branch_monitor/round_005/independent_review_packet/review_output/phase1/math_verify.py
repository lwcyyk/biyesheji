"""Finite exact arithmetic checks of probability statements, with no protocol implementation."""
from pathlib import Path
from math import comb, log2
from fractions import Fraction
import hashlib, json, datetime

OUT = Path(__file__).resolve().parent
TABLES = {
    '640': {'n': 640, 'D': 15, 'mass': [9288,8720,7216,5264,3384,1918,958,422,164,56,17,4,1], 'claimed_bits':751},
    '976': {'n': 976, 'D': 16, 'mass': [11278,10277,7774,4882,2545,1101,396,118,29,6,1], 'claimed_bits':1118},
    '1344': {'n':1344,'D':16,'mass':[18286,14320,6876,2023,364,40,2], 'claimed_bits':1532},
}

def convolve_integer(left, right):
    result = [0] * (len(left) + len(right) - 1)
    for i, x in enumerate(left):
        for j, y in enumerate(right):
            result[i+j] += x*y
    return result

results = {}
for name, entry in TABLES.items():
    masses = entry['mass']
    s = len(masses)-1
    symmetric = list(reversed(masses[1:])) + masses
    assert sum(symmetric) == 65536
    cdf = [masses[0]//2 - 1]
    for m in masses[1:]:
        cdf.append(cdf[-1]+m)
    assert cdf[-1] == 32767
    polynomial = [1]
    halfway_polynomial = None
    for convolution_count in range(1,65):
        polynomial = convolve_integer(polynomial,symmetric)
        if convolution_count == 32:
            halfway_polynomial = polynomial.copy()
    assert sum(polynomial) == 1 << 1024
    # Signed integer support injects into residues because its width is below q.
    q = 1 << entry['D']
    assert 128*s < q
    peak = max(polynomial)
    peak_from_l2_identity = sum(coefficient**2 for coefficient in halfway_polynomial)
    assert peak == peak_from_l2_identity
    maximizers = [i-64*s for i,x in enumerate(polynomial) if x==peak]
    h = 2*s+1
    n = entry['n']
    common_exponent = 1024*n
    first_numerator = comb(n,63)*max(masses)**(n-63)
    first_exponent = 16*(n-63)
    second_numerator = (h*peak)**n
    total_numerator = (first_numerator << (common_exponent-first_exponent)) + second_numerator
    claimed = entry['claimed_bits']
    certified = total_numerator <= (1 << (common_exponent-claimed))
    largest_integer_exponent = common_exponent - (total_numerator-1).bit_length()
    results[name] = {
        'n':n,'D':entry['D'],'s':s,'h':h,'w0':64,
        'masses_at_0_then_each_signed_value':masses,'denominator':65536,
        'cdf_reconstructed_from_table3':cdf,
        'total_mass_integer':sum(symmetric),'even_mass_integer':sum(masses[z]*(1 if z==0 else 2) for z in range(0,s+1,2)),
        'odd_mass_integer':2*sum(masses[1::2]),
        'integer_sum_support':[-64*s,64*s], 'support_injective_mod_q':True,
        'mu64_numerator':str(peak),'mu64_denominator_power_of_two':1024,
        'mu64_maximizers_integer':maximizers,
        'mu64_zero_l2_identity_passed':peak == peak_from_l2_identity,
        'coefficients_sha256':hashlib.sha256(json.dumps(polynomial,separators=(',',':')).encode()).hexdigest(),
        'peak_below_1_over_2h':2*h*peak < (1 << 1024),
        'mu64_approx':peak/(1<<1024),
        'h_mu64_approx':h*peak/(1<<1024),
        'negative_log2_first_approx':first_exponent-log2(first_numerator),
        'negative_log2_second_approx':common_exponent-log2(second_numerator),
        'negative_log2_sum_approx':common_exponent-log2(total_numerator),
        'claimed_upper_bound_exponent':claimed,
        'exact_integer_comparison_passed':certified,
        'largest_integer_power_bound_exponent':largest_integer_exponent,
        'certificate_rule':'C(n,63)*a_int^(n-63)*2^(1024*n-16*(n-63)) + (h*M)^n <= 2^(1024*n-claimed_bits)',
        'coefficient_symmetry': polynomial==list(reversed(polynomial)),
        'coefficient_nonincreasing_from_zero':all(polynomial[64*s+i]>=polynomial[64*s+i+1] for i in range(64*s)),
    }
    assert certified

# Independent exact finite checks for CF-1 endpoint and integer ceiling transitions.
correctness = []
for lam in range(2,1025):
    n = 8*lam
    D = 8*(n-1).bit_length()
    q = 1 << D
    b0 = 288*n+12
    w = 288*n*n*D + 3456*n*n + 12*n*D + 144*n
    assert 8*(b0+n*w) < q
    if lam <= 9 or n in [128,256,512,1024,2048,4096,8192]:
        correctness.append({'lambda':lam,'n':n,'D':D,'B0':b0,'W':w,'B0_plus_nW':b0+n*w,'q_over_8':q//8})

# Edge cases against accidental convolution assumptions, exactly on Z_4.
wrap_distribution = {0:Fraction(1,2),2:Fraction(1,2)}
wrapped = {0:Fraction(1)}
integer_sums = {0:Fraction(1)}
for _ in range(3):
    next_wrapped = {}
    next_integer = {}
    for x,px in wrapped.items():
        for y,py in wrap_distribution.items():
            next_wrapped[(x+y)%4] = next_wrapped.get((x+y)%4,Fraction()) + px*py
    for x,px in integer_sums.items():
        for y,py in wrap_distribution.items():
            next_integer[x+y] = next_integer.get(x+y,Fraction()) + px*py
    wrapped, integer_sums = next_wrapped, next_integer

# Exact toy conditional check, A=0, n=5, q=8, chi uniform on {-1,0,1}, P2=I.
chi_toy = {7:Fraction(1,3),0:Fraction(1,3),1:Fraction(1,3)}
weight_distribution = {0:Fraction(1)}
for _ in range(5):
    next_weights = {}
    for w,pw in weight_distribution.items():
        for bit_weight in (0,1,3):
            next_weights[w+bit_weight] = next_weights.get(w+bit_weight,Fraction()) + pw/3
    weight_distribution = next_weights
sum_distribution = {0:Fraction(1)}
conditional_accept = Fraction()
for w in range(16):
    coordinate_accept = sum(py*pz for y,py in chi_toy.items() for z,pz in sum_distribution.items() if (y-z)%8 in chi_toy)
    conditional_accept += weight_distribution.get(w,Fraction()) * coordinate_accept**5
    next_sums = {}
    for x,px in sum_distribution.items():
        for y,py in chi_toy.items():
            next_sums[(x+y)%8] = next_sums.get((x+y)%8,Fraction()) + px*py
    sum_distribution = next_sums
toy_epsilon = Fraction(10,27) + Fraction(7,9)**5
assert conditional_accept <= toy_epsilon < 1
bad_selection_probability = Fraction(1,3)**30
results['counterexample_checks']={
    'modular_aliasing_Z4':{'mass_at_0_2':'1/2 each','w':3,'mu3_mod4':str(max(wrapped.values())),'mu3_integer':str(max(integer_sums.values()))},
    'toy_conditional_D1':{'n':5,'q':8,'A':'zero','chi':'uniform {-1,0,1}','P2':'identity','w0':3,'epsilon_exact':str(toy_epsilon),'accept_conditional_on_P2_exact':str(conditional_accept),'bound_passed':True},
    'counterexample_to_H_dependent_selection':{'selection':'J exists iff H=0 and P2=I, one round','p_selected':str(bad_selection_probability),'beta_selected':str(bad_selection_probability),'Delta_selected':'0','epsilon_exact':str(toy_epsilon),'violates_generalized_p_times_epsilon':True},
    'correctness_finite_range':{'lambda_min':2,'lambda_max':1024,'all_passed':True,'selected_rows':correctness},
    'evidence_limit':'Finite arithmetic establishes only the specified distributions and finite range. General claims use symbolic proofs in PHASE1_DERIVATION.md.'
}
(OUT/'exact_certificates.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (OUT/'ACCESS_LOG.jsonl').open('a',encoding='utf-8') as f:
    f.write(json.dumps({'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'event':'mathematical_verification','path':str(Path(__file__).resolve()),'purpose':'整数质量表、64次卷积、dyadic界与有限正确性端点核算','evidence_class':'finite_exact_arithmetic','output':str(OUT/'exact_certificates.json')},ensure_ascii=False)+'\n')
for name in TABLES:
    entry=results[name]
    print(name, json.dumps({k:entry[k] for k in ['cdf_reconstructed_from_table3','even_mass_integer','odd_mass_integer','mu64_approx','h_mu64_approx','negative_log2_first_approx','negative_log2_second_approx','negative_log2_sum_approx','largest_integer_power_bound_exponent','exact_integer_comparison_passed']},ensure_ascii=False))
print('correctness endpoint', correctness[0])
