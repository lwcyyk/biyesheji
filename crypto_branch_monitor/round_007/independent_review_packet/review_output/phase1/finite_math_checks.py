"""Bounded exact mathematics only. No cryptographic protocol or attack is implemented."""
from fractions import Fraction
from itertools import product
from pathlib import Path
from math import gcd, prod
import json

OUT = Path(__file__).resolve().parent

def rational(value):
    return {'numerator': value.numerator, 'denominator': value.denominator}

def binary_rank(rows, columns):
    basis = [0] * columns
    rank = 0
    for row in rows:
        for column in reversed(range(columns)):
            if not (row >> column) & 1:
                continue
            if basis[column]:
                row ^= basis[column]
            else:
                basis[column] = row
                rank += 1
                break
    return rank

rank_checks = []
for t in range(1, 4):
    for kappa in range(2):
        s = t + kappa
        counts = []
        for base in range(2 ** t):
            success = sum(binary_rank([row ^ base for row in rows], t) == t
                          for rows in product(range(2 ** t), repeat=s))
            counts.append(success)
        expected = prod((1 - Fraction(2 ** i, 2 ** s) for i in range(t)), start=Fraction(1))
        actual = Fraction(sum(counts), 2 ** ((s + 1) * t))
        assert actual == expected
        assert len(set(counts)) == 1
        rank_checks.append({'t': t, 'kappa': kappa, 's': s,
                            'success_counts_by_base': counts,
                            'denominator_per_base': 2 ** (s * t),
                            'actual': rational(actual), 'formula': rational(expected)})

weights = [9288, 8720, 7216, 5264, 3384, 1918, 958, 422, 164, 56, 17, 4, 1]
total = weights[0] + 2 * sum(weights[1:])
odd = 2 * sum(weights[i] for i in range(1, 13, 2))
even = weights[0] + 2 * sum(weights[i] for i in range(2, 13, 2))
assert total == 65536 and odd == even == 32768

omission_checks = []
for weights_small in [[1,1,1,1], [3,1,0,0], [0,0,1,1]]:
    denominator = sum(weights_small)
    for count in range(5):
        miss = Fraction(0)
        for rows in product(range(4), repeat=count):
            divisor = gcd(4, *rows)
            mass = Fraction(prod(weights_small[row] for row in rows), denominator ** count)
            fresh_miss = Fraction(sum(weights_small[h] for h in range(4) if h % divisor), denominator)
            miss += mass * fresh_miss
        bound = min(Fraction(1), Fraction(2, count+1))
        assert miss <= bound
        omission_checks.append({'q':4,'g':1,'Q':count,'distribution_weights':weights_small,
                                'miss':rational(miss),'bound':rational(bound)})

parameter_checks = []
worst_ratio = None
worst_lambda = None
for security_parameter in range(2,513):
    n = 8 * security_parameter
    D = 8 * (n-1).bit_length()
    q = 2 ** D
    B0 = 288*n + 12
    W = 288*n*n*D + 3456*n*n + 12*n*D + 144*n
    accumulated = B0 + 2*W
    ratio = Fraction(q, 8*accumulated)
    assert accumulated < q // 8
    if worst_ratio is None or ratio < worst_ratio:
        worst_ratio, worst_lambda = ratio, security_parameter
    if security_parameter in [2,3,4,5,8,16,32,64,128,256,512]:
        parameter_checks.append({'lambda':security_parameter,'n':n,'D':D,'q':q,
                                 'B0':B0,'W':W,'B0_plus_2W':accumulated,'q_over_8':q//8,
                                 'oracle_calls':n+security_parameter+2+8*n*D*D+5})

result = {
    'scope':'finite_exact_mathematics',
    'general_proofs_live_in':'PHASE1_DERIVATION.md',
    'rank_checks':rank_checks,
    'chi640':{'weights_per_signed_value':weights,'denominator':65536,'total_weight':total,
              'odd_weight':odd,'even_weight':even,'support_min':-12,'support_max':12},
    'omission_checks':omission_checks,
    'iid_necessity_counterexample':{'q':2,'g':1,'Q':4,'training':'H_i = X for one common fair bit X',
                                   'fresh':'independent fair bit','miss':rational(Fraction(1,4)),
                                   'claimed_iid_bound':rational(Fraction(1,5))},
    'zero_divisor_example':{'q':8,'rows':[2,4],'target':6,'coefficients':[1,1],
                           'target_mod_2':0,'all_rows_mod_2':[0,0],
                           'coefficients_verify':(2+4)%8==6},
    'parameter_checks':parameter_checks,
    'finite_parameter_prefix':{'lambda_min':2,'lambda_max':512,'count':511,'all_strict':True,
                               'minimum_threshold_to_noise_ratio':rational(worst_ratio),'at_lambda':worst_lambda},
    'no_attack_or_protocol_implementation':True
}
(OUT/'FINITE_EXACT_RESULTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'rank_cases':len(rank_checks),'omission_cases':len(omission_checks),
                  'chi_parity_balanced':odd==even,'parameter_cases':511,
                  'first_parameter_case':parameter_checks[0],'finite_min_ratio':rational(worst_ratio)},ensure_ascii=False))
