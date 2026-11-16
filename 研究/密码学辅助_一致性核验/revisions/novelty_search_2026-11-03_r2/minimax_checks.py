"""Exact small-field checks plus numerical simulator LP; never a priority proof."""
import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
import json
from pathlib import Path
from frontier_probe import Field


def dot(f,a,b):
    value=0
    for x,y in zip(a,b): value=f.add(value,f.mul(x,y))
    return value


def rank(f,cols,d):
    rows=[[v[i] for v in cols] for i in range(d)]; lead=0
    for j in range(len(cols)):
        pivot=next((i for i in range(lead,d) if rows[i][j]),None)
        if pivot is None:continue
        rows[lead],rows[pivot]=rows[pivot],rows[lead]
        rows[lead]=[f.div(x,rows[lead][j]) for x in rows[lead]]
        for i in range(d):
            if i==lead:continue
            coefficient=rows[i][j]
            rows[i]=[f.add(x,f.neg(f.mul(coefficient,y))) for x,y in zip(rows[i],rows[lead])]
        lead+=1
        if lead==d:break
    return lead


def simulator_lp(f,basis,masks,weights):
    import numpy as np
    from scipy.optimize import linprog
    from scipy.sparse import coo_matrix
    universe=list(product(range(1,f.q),repeat=len(basis)));ix={x:i for i,x in enumerate(universe)}
    distributions=[]
    for amps in universe:
        law=[0.]*len(universe)
        for m,w in zip(masks,weights):
            y=tuple(f.mul(a,dot(f,m,v)) for a,v in zip(amps,basis))
            law[ix[y]]+=float(w)
        distributions.append(law)
    N=len(universe); ep=N; variables=N+1+N*len(distributions); rr=[];cc=[];dd=[];rhs=[]
    def row(items,b):
        k=len(rhs);rhs.append(b)
        for j,x in items: rr.append(k);cc.append(j);dd.append(x)
    for h,law in enumerate(distributions):
        first=N+1+h*N
        for j,value in enumerate(law):
            row([(j,1),(first+j,-1)],value)
            row([(j,-1),(first+j,-1)],-value)
        row([(first+j,.5) for j in range(N)]+[(ep,-1)],0)
    A=coo_matrix((dd,(rr,cc)),shape=(len(rhs),variables)).tocsr()
    eq=coo_matrix(([1]*N,([0]*N,list(range(N)))),shape=(1,variables)).tocsr()
    objective=np.zeros(variables);objective[ep]=1
    result=linprog(objective,A_ub=A,b_ub=np.array(rhs),A_eq=eq,b_eq=[1],bounds=(0,None),method='highs')
    assert result.success
    return float(result.fun)


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args()
    base=Path(__file__).resolve().parent;out=(base/args.out).resolve();assert out.is_relative_to(base)
    out.mkdir(parents=True,exist_ok=False);records=[];lp_records=[];distribution_checks=0
    dictionaries=[[(1,0),(0,1)],[(1,0),(0,1),(1,1)],[(1,0),(1,0),(0,1)],
                  [(1,0,0),(0,1,0),(0,0,1),(1,1,0),(0,1,1)],
                  [(1,0,0),(0,1,0),(0,0,1),(1,1,1)],
                  [(1,0),(0,1),(0,0)]]
    for f in (Field(3),Field(2,2,[1,1]),Field(5)):
        for dictionary in dictionaries:
            d=len(dictionary[0]);n=len(dictionary);assert rank(f,dictionary,d)==d
            masks=[m for m in product(range(f.q),repeat=d) if all(dot(f,m,v) for v in dictionary)]
            chi=sum((-1)**len(T)*f.q**(d-rank(f,[dictionary[j] for j in T],d))
                    for size in range(n+1) for T in combinations(range(n),size))
            assert chi==len(masks)
            row={'q':f.q,'dictionary_columns':dictionary,'rank':d,'chi_q':chi,'enumerated_masks':len(masks)}
            if not masks:
                row['status']='NO_ZERO_ERASURE_SINGLE_ROW_MASK';records.append(row);continue
            N=(f.q-1)**d; optimum=1-Fraction(chi,N)
            row['simulation_error_formula']=str(optimum)
            for size in range(d+1):
                for S in combinations(range(n),size):
                    vs=[dictionary[j] for j in S]
                    if rank(f,vs,d)!=size:continue
                    U=list(product(range(1,f.q),repeat=size));u=Fraction(1,len(U))
                    for amplitudes in U:
                        law=Counter(tuple(f.mul(a,dot(f,m,v)) for a,v in zip(amplitudes,vs)) for m in masks)
                        delta=sum(abs(Fraction(law[y],chi)-u) for y in U)/2
                        assert delta<=optimum
                        if size==d:assert delta==optimum
                        distribution_checks+=1
            # Generic simulator LP, independent of the averaging argument, small N only.
            if N<=16 and chi>1:
                basis=next([dictionary[j] for j in S] for S in combinations(range(n),d) if rank(f,[dictionary[j] for j in S],d)==d)
                uniform=[Fraction(1,chi)]*chi
                skew=[Fraction(1,N)]*chi;skew[0]=1-Fraction(chi-1,N)
                concentrated=[Fraction(int(i==0)) for i in range(chi)]
                for label,weights in [('uniform',uniform),('optimal_skew',skew),('point_mass',concentrated)]:
                    expected=1-sum(min(w,Fraction(1,N)) for w in weights)
                    actual=simulator_lp(f,basis,masks,weights)
                    assert abs(actual-float(expected))<1e-8
                    lp_records.append({'q':f.q,'n':n,'d':d,'distribution':label,'formula':str(expected),'numeric_simulator_optimum_NOT_PROOF':actual})
            records.append(row)
    # Reuse attack: y_t/y'_t reveals the ratio of amplitudes with certainty.
    reuse={'field':3,'same_mask_same_coordinate':True,'world0_amplitudes':[1,1],'world1_amplitudes':[1,2],
           'world0_observed_ratios':[1],'world1_observed_ratios':[2],'TV':1,
           'conclusion':'fresh masks per query mandatory; no amortization by mask reuse'}
    report={'profiles':records,'simulator_LP':lp_records,'same_seed_reuse_counterexample':reuse,
            'distribution_checks':distribution_checks,'scope':'finite verification; numeric LP is corroboration only'}
    (out/'raw.json').write_text(json.dumps(report,indent=2))
    summary={'pass':True,'profiles':len(records),'distribution_checks':distribution_checks,'simulator_LPs':len(lp_records),
             'universal_proof_by_tests':False,'originality_verified':False}
    (out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))


if __name__=='__main__':main()
