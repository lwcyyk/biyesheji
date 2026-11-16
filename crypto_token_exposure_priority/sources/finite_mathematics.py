"""Finite group, Bernoulli rank and scalar rounding checks; no UE/attack implementation."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
from math import comb
import json

SRC=Path(__file__).resolve().parent


def extend(group,row,q):
    return tuple(sorted({tuple((x[j]+a*row[j])%q for j in range(len(row)))
                         for x in group for a in range(q)}))


def joint_omission(q,constant_H,Qmax=7):
    support=[(1,1),(1,q-1)] if constant_H else [(h,r) for h in [0,1] for r in [1,q-1]]
    support=list(dict.fromkeys(support));weight=F(1,len(support))
    states={((0,0),):F(1)};probs=[];capacity=(q*q).bit_length()-1
    for Q in range(Qmax+1):
        miss=sum(mass*sum(weight for row in support if row not in group)
                 for group,mass in states.items())
        assert miss<=min(F(1),F(capacity,Q+1))
        if probs: assert miss<=probs[-1]
        probs.append(miss)
        following={}
        for group,mass in states.items():
            for row in support:
                new=extend(group,row,q)
                following[new]=following.get(new,F(0))+mass*weight
        states=following
    if constant_H: assert probs==[F(1,2**i) for i in range(Qmax+1)]
    return {'q':q,'constant_H':constant_H,'joint_support':support,'p_Q':[str(x) for x in probs],
            'integer_growth_capacity':capacity,'all_bounds_hold':True}


joint=[joint_omission(q,h) for q in [3,4,6] for h in [False,True]]
escape=[]
for q in [3,5,7]:
    for t in [1,2,3]:
        worst=F(0)
        for normal in product(range(q),repeat=t):
            if not any(normal):continue
            inside=sum(sum(a*b for a,b in zip(normal,row))%q==0 for row in product([0,1],repeat=t))
            probability=F(inside,2**t);assert probability<=F(1,2);worst=max(worst,probability)
        escape.append({'odd_prime_q':q,'t':t,'maximum_hyperplane_hit_probability':str(worst),
                       'minimum_escape_at_least_half':True})

rounding=[]
for q in range(2,32):
    center=q//2;radius=F(q,4)-(F(q,2)-center);cases=0
    for bit in [0,1]:
        for error in range(-q,q+1):
            if abs(error)>=radius:continue
            value=(bit*center+error)%q
            nearest=(4*value+q)//(2*q)%2
            assert nearest==bit,(q,bit,error)
            cases+=1
    rounding.append({'q':q,'strict_symmetric_radius':str(radius),'integer_cases':cases,'passes':True})
q=5;value=((q//2)-1)%q
assert (4*value+q)//(2*q)%2==0
assert F(1)<F(q,4)

for r in [1,-1]: assert (0+r*0)%4==(2+r*2)%4==0
scalar={'fresh_omission':F(1,4),'e0':F(0),'e1':F(0)}
gap=1-scalar['fresh_omission']-scalar['e0']-scalar['e1']
assert gap==F(3,4) and F(1,2)+gap/2==F(7,8)

record={'round':'ROUND-008','scope':'Finite mathematical verification only; no protocol or attack prototype',
        'joint_module_cases':joint,'conditional_odd_prime_hyperplane_cases':escape,
        'rounding_margin_cases':rounding,
        'rounding_control':{'q':5,'message_bit':1,'error':-1,'absolute_error_below_q_over4':True,
                            'decoded_bit':0,'consequence':'Use conservative radius q/4-1/2 for odd q in the newly derived sufficient bound'},
        'separate_N_nonidentifiability':{'q':4,'H':1,'pairs':[[0,0],[2,2]],
                                       'legal_target_actions_equal_for_both_signs':True},
        'joint_advantage_example':{'gap':str(gap),'bias':str(gap/2),'success':str(F(1,2)+gap/2)},
        'cryptographic_implementations':0}
(SRC/'finite_mathematical_checks.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'joint_module_cases':len(joint),'hyperplane_cases':len(escape),
                  'rounding_q_values':len(rounding),'status':'PASS'},ensure_ascii=False))
