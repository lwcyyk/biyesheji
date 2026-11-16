"""Finite exact algebra checks for the phase-2 informed supplement review."""
from pathlib import Path
from fractions import Fraction
from itertools import product
from math import prod
import json

OUT = Path(__file__).resolve().parent

def rational(value):
    return {'numerator': value.numerator, 'denominator': value.denominator}

def span(rows, q, dimension):
    current = {(0,) * dimension}
    for row in rows:
        current = {tuple((base[j] + coefficient * row[j]) % q for j in range(dimension))
                   for base in current for coefficient in range(q)}
    return current

joint_cases = []
for q, support, description in [
        (3, [(0,0),(1,0)], 'constant zero update coefficient'),
        (4, [(1,1),(1,3)], 'sign coefficients and fixed parent feature'),
        (6, [(0,0),(0,2),(1,0),(1,2)], 'composite modulus and even update coefficients')]:
    for count in range(6):
        misses = 0
        for rows in product(support, repeat=count):
            module = span(rows, q, 2)
            misses += sum(target not in module for target in support)
        denominator = len(support) ** (count+1)
        probability = Fraction(misses, denominator)
        # Exact comparison p <= 2 log_2(q)/(Q+1), without floating logarithms.
        bound_verified = 2 ** (probability.numerator * (count+1)) <= q ** (2 * probability.denominator)
        assert bound_verified
        joint_cases.append({'q':q,'dimension':2,'Q':count,'support':support,
                            'description':description,'miss_count':misses,
                            'total_count':denominator,'probability':rational(probability),
                            'bound':'min(1,2*log2(q)/(Q+1))','bound_verified_exactly':True})

chi_tables = {
    'chi640':[9288,8720,7216,5264,3384,1918,958,422,164,56,17,4,1],
    'chi976':[11278,10277,7774,4882,2545,1101,396,118,29,6,1],
    'chi1344':[18286,14320,6876,2023,364,40,2]
}
parity = []
for name, weights in chi_tables.items():
    total = weights[0] + 2*sum(weights[1:])
    odd = 2*sum(weights[1::2])
    even = total-odd
    assert total == 65536
    parity.append({'name':name,'total':total,'odd':odd,'even':even,'balanced':odd==even})
assert parity[0]['balanced'] and parity[1]['balanced'] and not parity[2]['balanced']

biased_rank = []
for even_probability in [Fraction(1,3),Fraction(1,2),Fraction(3,4)]:
    for difference_rows in range(1,5):
        probability = Fraction(0)
        for bits in product(range(2), repeat=difference_rows+1):
            mass = prod((even_probability if bit==0 else 1-even_probability for bit in bits), start=Fraction(1))
            if all(bit==bits[0] for bit in bits[1:]):
                probability += mass
        formula = even_probability**(difference_rows+1)+(1-even_probability)**(difference_rows+1)
        assert probability == formula
        biased_rank.append({'even_probability':rational(even_probability),'s':difference_rows,
                            'rank_failure':rational(probability),'formula':rational(formula)})

sign_rows = [(1,1),(1,3)]
full_sign_module = span(sign_rows,4,2)
sign_actions = [{
    'target':target,
    'action_W0':0,
    'action_W1':(2*target[0]+2*target[1])%4
} for target in sorted(full_sign_module)]
assert all(row['action_W0']==row['action_W1'] for row in sign_actions)

budget = []
for lam in [2,3,4,8,16,32,64,128,256,512]:
    n=8*lam
    D=8*(n-1).bit_length()
    old_Q=4*n*D*D
    joint_Q=4*(n*D+n)*D
    old_calls=n+lam+2+2*old_Q+5
    joint_calls=2*joint_Q+5
    assert joint_calls-old_calls==8*n*D-n-lam-2
    budget.append({'lambda':lam,'n':n,'D':D,'old_Q':old_Q,'joint_Q':joint_Q,
                   'old_calls':old_calls,'joint_calls':joint_calls,
                   'difference':joint_calls-old_calls})

result={
    'schema':'round007.phase2-finite-exact/1',
    'identity':'phase2_informed_review_first_seen_supplement',
    'general_proof':'COMPARISON.md',
    'joint_module_cases':joint_cases,
    'official_table_parity_checks':parity,
    'biased_rank_checks':biased_rank,
    'nonidentifiable_N_supported_joint_actions':{
        'q':4,'H':1,'r_support':[1,3],'W0':[0,0],'W1':[2,2],
        'module_action_rows':sign_actions
    },
    'coin_law_mismatch_counterexample':{
        'q':2,'dimension':2,'Q':4,'training_X':[0,0],'target_X':[0,1],
        'miss_probability':rational(Fraction(1)),
        'iid_formula_bound_if_misapplied':rational(Fraction(2,5))
    },
    'stopping_counterexample':{
        'q':2,'g':1,'N':8,'tau_values':[0,8],'tau_probabilities':['1/2','1/2'],
        'miss_probability':rational(Fraction(1,4)+Fraction(1,2**10)),
        'incorrect_expected_count_bound':rational(Fraction(1,5))
    },
    'budgets':budget,
    'checks_passed':True,
    'scope':'Finite scalar and small-module algebra. No oracle protocol or attack prototype.'
}
(OUT/'FINITE_EXACT_RESULTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'joint_cases':len(joint_cases),'biased_rank_cases':len(biased_rank),
                  'parity':parity,'lambda2_budget':budget[0],'all_checks':'PASS'},ensure_ascii=False))
