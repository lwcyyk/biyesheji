"""Exact finite convolution and probability bounds, without cryptographic algorithms."""
import json
from fractions import Fraction
from math import comb
from pathlib import Path
from datetime import datetime, timezone

profiles = [
    ('640',640,15,[9288,8720,7216,5264,3384,1918,958,422,164,56,17,4,1]),
    ('976',976,16,[11278,10277,7774,4882,2545,1101,396,118,29,6,1]),
    ('1344',1344,16,[18286,14320,6876,2023,364,40,2]),
]
w0=64

def binary_bound(value):
    if value>=1:
        return None
    b=value.denominator.bit_length()-value.numerator.bit_length()
    if value.numerator<<b > value.denominator:
        b-=1
    assert value.numerator<<b <= value.denominator
    assert value.numerator<<(b+1) > value.denominator
    return b

rows=[]
for name,n,D,masses in profiles:
    s=len(masses)-1
    coefficients=[masses[abs(z)] for z in range(-s,s+1)]
    assert sum(coefficients)==65536
    convolution=[1]
    for _ in range(w0):
        updated=[0]*(len(convolution)+len(coefficients)-1)
        for i,x in enumerate(convolution):
            for j,y in enumerate(coefficients):
                updated[i+j]+=x*y
        convolution=updated
    denominator=65536**w0
    assert sum(convolution)==denominator
    assert 2*s*w0 < 1<<D
    mu=Fraction(max(convolution),denominator)
    a=Fraction(max(coefficients),65536)
    h=2*s+1
    parent_bad=comb(n,w0-1)*a**(n-w0+1)
    support_bad=(h*mu)**n
    total=parent_bad+support_bad
    assert h*mu<1
    rows.append({'profile':name,'n':n,'D':D,'w0':w0,'support_h':h,
        'a':str(a),'mu_w0':str(mu),'h_times_mu_approx':float(h*mu),
        'maximum_locations':[i-s*w0 for i,x in enumerate(convolution) if x==max(convolution)],
        'parent_bad_upper_binary_exponent':binary_bound(parent_bad),
        'support_bad_upper_binary_exponent':binary_bound(support_bad),
        'total_upper_binary_exponent':binary_bound(total),
        'no_modular_aliasing_at_w0':True})
result={'created_utc':datetime.now(timezone.utc).isoformat(),
    'status':'FINITE_ARITHMETIC_PASS_GENERAL_PROOF_PENDING_ADVERSARIAL_REVIEW',
    'bound':'binom(n,w0-1)*a^(n-w0+1)+(h*mu_w0)^n',
    'exponent_convention':'integer b certifies bound<=2^(-b) by exact comparison',
    'rows':rows,'scope':'Independent chi samples, arbitrary fixed A; applicability is a hand-proof obligation.',
    'code_scope':'Finite scalar distribution convolution only. No UE, PKE, attack, native service or protection mechanism implementation.'}
path=Path(__file__).with_name('FIXED_A_BOUND_CHECKS.json')
path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps([{k:r[k] for k in ['profile','h_times_mu_approx','parent_bad_upper_binary_exponent','support_bad_upper_binary_exponent','total_upper_binary_exponent']} for r in rows],ensure_ascii=False))
