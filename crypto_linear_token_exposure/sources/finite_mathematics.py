"""Tiny group/rank counts and scalar inequalities only; no cryptographic attack implementation."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
from math import prod
import json

ROOT = Path(__file__).resolve().parent


def binary_rank(rows):
    pivots = {}
    for value in rows:
        while value:
            lead = value.bit_length()-1
            if lead in pivots:
                value ^= pivots[lead]
            else:
                pivots[lead] = value
                break
    return len(pivots)


rank_checks = []
for t, kappa in [(1,0),(1,2),(2,0),(2,1),(3,1)]:
    s = t+kappa
    formula = prod(1-F(1,2**(s-i)) for i in range(t))
    base_results = []
    for base in range(2**t):
        count = sum(binary_rank([r^base for r in rows])==t
                    for rows in product(range(2**t),repeat=s))
        assert F(count,2**(t*s))==formula
        base_results.append(count)
    assert 1-formula<F(1,2**kappa)
    rank_checks.append({'t':t,'kappa':kappa,'s':s,'bases_checked':2**t,
                        'conditional_counts':base_results,'total_per_base':2**(t*s),
                        'exact_full_rank':str(formula),'matches':True})


def add(x,y,q):
    return tuple((a+b)%q for a,b in zip(x,y))


def extend_group(group,h,q):
    result=set(group)
    for coefficient in range(q):
        shift=tuple((coefficient*x)%q for x in h)
        result.update(add(x,shift,q) for x in group)
    return tuple(sorted(result))


def module_check(q,g,weighted_support,Qmax):
    support={tuple(x):F(w,sum(v for _,v in weighted_support)) for x,w in weighted_support}
    zero=(0,)*g
    states={(zero,):F(1)}
    ps=[]
    capacity=g*(q.bit_length()-1)
    for Q in range(Qmax+1):
        miss=sum(mass*sum(p for h,p in support.items() if h not in group)
                 for group,mass in states.items())
        assert miss<=min(F(1),F(capacity,Q+1))
        if ps: assert miss<=ps[-1]
        ps.append(miss)
        new={}
        for group,mass in states.items():
            for h,p in support.items():
                expanded=extend_group(group,h,q)
                if h not in group: assert len(expanded)>=2*len(group)
                new[expanded]=new.get(expanded,F(0))+mass*p
        states=new
    assert sum(ps)<=capacity
    return {'q':q,'g':g,'Qmax':Qmax,'capacity':capacity,
            'p_Q':[str(p) for p in ps],'sum_probabilities':str(sum(ps)),
            'all_bounds_and_monotonicity_verified':True}


module_checks=[
    module_check(4,1,[((0,),2),((1,),1),((2,),1)],7),
    module_check(4,2,[((0,0),1),((1,0),1),((0,2),1),((1,1),1)],7),
    module_check(8,1,[((0,),1),((2,),2),((4,),1)],9),
    module_check(4,2,[((0,0),1)],5)]


def closure(K,T,C,bidirectional=False):
    K,T,C=map(set,(K,T,C))
    while True:
        previous=(K.copy(),T.copy(),C.copy())
        for j in [2,3]:
            if j in T and j in K:K.add(j-1)
            if bidirectional and j in T and j-1 in K:K.add(j)
            if j-1 in K and j in K:T.add(j)
            if j in T and j-1 in C:C.add(j)
            if bidirectional and j in T and j in C:C.add(j-1)
        if previous==(K,T,C):break
    return {'Kstar':sorted(K),'Tstar':sorted(T),'Cstar':sorted(C),
            'intersection':sorted(K&C),'valid':not bool(K&C)}


closure_checks={
    'SELECT_base':closure([3],[],[2]),
    'FI_Next_records_challenge':closure([3],[],[2,3]),
    'CANS_IEICE_score_base':closure([3],[],[2],True),
    'SELECT_plus_Get3':closure([3],[],[2,3]),
    'SELECT_plus_Token3':closure([3],[3],[2])}
assert closure_checks['SELECT_base']['valid'] and closure_checks['CANS_IEICE_score_base']['valid']
assert all(not closure_checks[name]['valid'] for name in
           ['FI_Next_records_challenge','SELECT_plus_Get3','SELECT_plus_Token3'])

correctness=[]
for lam in [2,3,4,8,16,32,64,128]:
    n=8*lam;D=8*(n-1).bit_length();q=2**D
    B0=288*n+12;W=288*n*n*D+3456*n*n+12*n*D+144*n
    assert B0+2*W<5055*n**3<n**8//8<=q//8
    Qtrain=4*n*D*D;kappa=lam+2
    correctness.append({'lambda':lam,'n':n,'D':D,'B0_plus_2W':B0+2*W,
                        'decode_radius':q//8,'Qtrain':Qtrain,
                        'maximum_oracle_calls':n+kappa+2*Qtrain+5,'verified':True})

weights=[9288,8720,7216,5264,3384,1918,958,422,164,56,17,4,1]
assert weights[0]+2*sum(weights[1:])==65536
even=weights[0]+2*sum(weights[2::2]);assert even==32768

a=F(3,4);m=F(1,4);e0=e1=F(0);rho=1-a
p0=rho/2+a*(m+e0);p1=rho/2+a*(1-e1)
gap=p1-p0;success=(1-p0+p1)/2
assert gap==F(9,16) and success==F(25,32) and success-F(1,2)==gap/2
stop_N=16;stop_miss=F(1,4)+F(1,2**(stop_N+2));bad_bound=F(1,F(stop_N,2)+1)
assert stop_miss>bad_bound

record={'round':'ROUND-007','scope':'Finite mathematical identities; no token-extraction routine, no UE/attack prototype',
        'conditional_rank_checks':rank_checks,'module_checks':module_checks,'closure_checks':closure_checks,
        'CF2_scalar_examples':correctness,'chi640_even_mass':f'{even}/65536',
        'advantage_scalar_example':{'a':str(a),'fresh_miss':str(m),'p0':str(p0),'p1':str(p1),
                                    'gap':str(gap),'success':str(success),'bias':str(gap/2)},
        'random_stopping_counterexample':{'N':stop_N,'actual_miss':str(stop_miss),
                                          'invalid_mean_denominator_bound':str(bad_bound)},
        'sign_obstruction':{'q':4,'H':1,'parameter_pairs':[[0,0],[2,2]],
                            'statement':'K+rN=0 for both parameter pairs and both r=+1,-1'},
        'cryptographic_implementations':0}
(ROOT/'finite_mathematical_checks.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'rank_cases':len(rank_checks),'module_distributions':len(module_checks),
                  'closure_cases':len(closure_checks),'correctness_examples':len(correctness),
                  'advantage_example':record['advantage_scalar_example']},ensure_ascii=False,indent=2))
