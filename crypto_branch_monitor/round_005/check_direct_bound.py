"""Exact scalar and small-ring counting checks for a paper probability lemma."""
import json
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from datetime import datetime, timezone

out = Path(__file__).parent
profiles = [
    ('640',640,15,[9288,8720,7216,5264,3384,1918,958,422,164,56,17,4,1]),
    ('976',976,16,[11278,10277,7774,4882,2545,1101,396,118,29,6,1]),
    ('1344',1344,16,[18286,14320,6876,2023,364,40,2]),
]

def certified_binary_exponent(value):
    if value >= 1:
        return None
    b = value.denominator.bit_length() - value.numerator.bit_length()
    if value.numerator << b > value.denominator:
        b -= 1
    assert value.numerator << b <= value.denominator
    assert value.numerator << (b+1) > value.denominator
    return b

certificates=[]
for name,n,D,masses in profiles:
    q=1<<D
    dist={0:F(masses[0],65536)}
    for z in range(1,len(masses)):
        dist[z]=dist[-z]=F(masses[z],65536)
    assert sum(dist.values())==1
    h=len(dist)
    a=[]
    c=[]
    for j in range(D+1):
        residues={}
        for z,p in dist.items():
            residues[z%(1<<j)]=residues.get(z%(1<<j),F(0))+p
        aj=max(residues.values())
        a.append(aj)
        c.append(h*aj*aj*(F(1<<j,q) if j<D else 1))
    exact_bound=(n*D+1)*sum(x**n for x in c)
    coarse=(n*D+1)*(D+1)*max(c)**n
    assert exact_bound<=coarse
    record={'profile':name,'n':n,'D':D,'h':h,
        'a_j':[str(x) for x in a], 'c_j':[str(x) for x in c],
        'c_max':str(max(c)), 'c_max_approx':float(max(c)),
        'exact_sum_bound_binary_exponent':certified_binary_exponent(exact_bound),
        'coarse_bound_binary_exponent':certified_binary_exponent(coarse),
        'exponent_meaning':'B <= 2^(-b), certified by integer comparison; null means this bound is >=1',
        'ideal_sampling_only':True}
    if name=='1344':
        b=[]
        for j in range(D+1):
            largest=F(0)
            for coefficient in dist:
                if coefficient==0:
                    continue
                residues={}
                for x,px in dist.items():
                    for y,py in dist.items():
                        residue=(x-coefficient*y)%(1<<j)
                        residues[residue]=residues.get(residue,F(0))+px*py
                largest=max(largest,max(residues.values()))
            b.append(largest)
        zero_part=sum((F(1<<j,q)*a[j]**2)**n for j in range(D))+a[D]**(2*n)
        nonzero_part=(h**n-1)*(sum((F(1<<j,q)*b[j]**2)**n for j in range(D))+b[D]**(2*n))
        split=(n*D+1)*(zero_part+nonzero_part)
        record['split_bound']={'b_j':[str(x) for x in b],
            'nonzero_max_c':str(max([h*F(1<<j,q)*b[j]**2 for j in range(D)]+[h*b[D]**2])),
            'binary_exponent':certified_binary_exponent(split)}
    certificates.append(record)

ring_checks=[]
for q,n,raw in [(2,1,[3,1]),(4,1,[2,1,0,1]),(4,2,[2,1,0,1]),(8,2,[4,1,0,1,0,1,0,1])]:
    D=q.bit_length()-1
    pmf=[F(x,sum(raw)) for x in raw]
    vectors=list(product(range(q),repeat=n))
    direct=F(0)
    for v in vectors:
        pv=F(1)
        for x in v: pv*=pmf[x]
        if not pv: continue
        counts=[0]*q
        for col in vectors:
            counts[sum(x*y for x,y in zip(v,col))%q]+=1
        one_column=sum(pmf[e]*F(counts[-e%q],q**n) for e in range(q))
        direct+=pv*one_column**n
    p=[sum(pmf[x] for x in range(0,q,1<<j)) for j in range(D+1)]
    formula=sum((p[j]**n-p[j+1]**n)*p[j]**n*F(1<<j,q)**n for j in range(D))+p[D]**(2*n)
    assert direct==formula
    ring_checks.append({'q':q,'n':n,'distribution':raw,'direct':str(direct),'formula':str(formula),'equal':True})

data={'created_utc':datetime.now(timezone.utc).isoformat(),
    'provenance':'Originating main-session informed derivation and finite checks',
    'parameters':certificates,'finite_ring_identity_checks':ring_checks,
    'limits':'Exact parameter arithmetic and finite ring probability checks only. No UE/Enc/Upd/attack implementation. General proof is a separate hand derivation.'}
(out/'DIRECT_BOUND_CHECKS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'parameters':[{k:r[k] for k in ['profile','c_max_approx','exact_sum_bound_binary_exponent','coarse_bound_binary_exponent']} for r in certificates], 'split1344':certificates[-1]['split_bound'],'ring_identities_passed':len(ring_checks)},ensure_ascii=False))
