"""Finite integer/probability mathematics, with no group/encryption implementation."""
from pathlib import Path
from fractions import Fraction as R
from collections import Counter
import itertools, json, hashlib
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parent
inp=json.loads((ROOT/'INPUTS.json').read_text(encoding='utf-8'))
rows=[]
def add(kind,arguments,result,passed):
    assert passed,(kind,arguments,result)
    rows.append(dict(kind=kind,input=arguments,result=result,passed=True))

for q in inp['q_values']:
    for rho,eta in inp['parent_coordinates']:
        actual=set()
        fibres=Counter()
        for a,s,z in itertools.product(range(1,q),range(q),range(q)):
            rp=(rho+a+s)%q;ep=(eta+z)%q
            actual.add((rp,ep,a,s,z));fibres[rp,ep]+=1
        opened=set()
        for rp,ep,a in itertools.product(range(q),range(q),range(1,q)):
            s=(rp-rho-a)%q;z=(ep-eta)%q
            opened.add((rp,ep,a,s,z))
        add('scalar_joint_bijection',dict(q=q,rho=rho,eta=eta),dict(domain_size=len(actual),
            output_count=len(fibres),fibre_sizes=sorted(set(fibres.values())),
            per_joint_point=str(R(1,(q-1)*q*q)),per_output=str(R(1,q*q)),
            per_conditional_opening=str(R(1,q-1))),
            actual==opened and len(fibres)==q*q and set(fibres.values())=={q-1})

# Same-parent repetitions: product conditional fibres for all pairs of target outputs.
q=3
cnt=Counter()
for rp,ep,a,rp2,ep2,a2 in itertools.product(range(q),range(q),range(1,q),range(q),range(q),range(1,q)):
    cnt[rp,ep,rp2,ep2]+=1
add('two_independent_children',dict(q=q),dict(target_pairs=len(cnt),fibre_sizes=sorted(set(cnt.values()))),
    len(cnt)==q**4 and set(cnt.values())=={(q-1)**2})

for n in inp['bit_domain_sizes']:
    if n==1:
        add('singleton_tape',dict(n=n),dict(bits='',mass='1'),True)
        continue
    k=(n-1).bit_length();m=2**k;p=R(n,m)
    rejected=list(range(n,m))
    for t in inp['bit_rounds']:
        explicit_prefixes=list(itertools.product(rejected,repeat=t-1))
        per_cond=R(n,m**t)
        mass=per_cond*len(explicit_prefixes)
        expected=(1-p)**(t-1)*p
        finite_B=3
        normalized_mass=mass/(1-(1-p)**finite_B)
        add('bit_conditional_mass',dict(n=n,t=t,B=finite_B),dict(
            prefix_count=len(explicit_prefixes),per_specific_prefix=str(per_cond),
            length_mass=str(mass),finite_conditioned_length_mass=str(normalized_mass)),
            mass==expected and sum((1-p)**(j-1)*p for j in range(1,finite_B+1))/(1-(1-p)**finite_B)==1)

def close(K,T,C,L):
    K,T,C=map(set,(K,T,C))
    while True:
        old=(set(K),set(T),set(C))
        for j in range(2,L+1):
            if j in K and j in T:K.add(j-1)
            if j-1 in K and j in K:T.add(j)
            if j-1 in C and j in T:C.add(j)
        if old==(K,T,C):break
    return dict(K=sorted(K),T=sorted(T),C=sorted(C),valid=not bool(K&C))
w=inp['closure_witness']
sel=close(w['keys'],w['tokens'],w['SELECT_C'],w['L'])
pub=close(w['keys'],w['tokens'],w['GP23_literal_Next_C'],w['L'])
add('published_Next_vs_SELECT',w,dict(SELECT=sel,GP23_literal=pub),sel['valid'] and not pub['valid'])

out=dict(schema='SELECT-PRIORITY-MATH-RESULTS-1',generated_at_utc=datetime.now(timezone.utc).isoformat(),
    scope=inp['scope'],checks=len(rows),passed=len(rows),rows=rows)
(ROOT/'RAW_RESULTS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
summary=dict(checks=len(rows),passed=len(rows),categories=dict(Counter(x['kind'] for x in rows)),
    source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    input_sha256=hashlib.sha256((ROOT/'INPUTS.json').read_bytes()).hexdigest())
(ROOT/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,indent=2))
