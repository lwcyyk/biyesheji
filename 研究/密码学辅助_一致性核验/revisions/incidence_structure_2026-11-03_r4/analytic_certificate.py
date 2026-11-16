"""Closed-form primal/dual witnesses; no numerical optimizer calls."""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import argparse,json
from incidence import EDGES,PERFECT,compiled_counts
from compressed_lp import build


def construct(q,C):
    C=set(C);t=len(C);U=15*q-60+t;O=q*q-14*q+55-t;N=q*q+q-5;D=U-3*(q-1)
    Z=(q-1)*U-3*O;K=F(9,Z);lo=F(D,(q-1)*Z);hi=lo*(1+F(3,D));delta=3*lo
    rows,eq,n,ep,signatures,counts=build(q,C);R=len(signatures);W=R+1;S=W+5*20;ext=q*q-5*q+10
    p=[F(0)]*n;p[ep]=delta
    for i,T in enumerate(signatures):p[i]=hi if T else lo
    nu=[F(1,2)-K];mu=[];certificate_data=[]
    te={e:sum(e in T for T in C) for e in EDGES}
    for b,B in enumerate(combinations(range(6),3)):
        edges=list(combinations(B,2));cB=sum(any(set(e)<=set(B) for e in T) for T in C)
        ell=F(3*q-12+2*cB-t,12);lam=3*ell/U;L=K*ell
        assert lam>=0 and K<=1
        a=W+5*b;full=a+4
        for j in range(3):p[a+1+j]=hi
        p[full]=lo
        nu.append(L/(q-1)-lam/2)
        # Rank-one absolute values: alpha=lam/2, p_rank1=sim_rank1=0.
        mu.extend([-ext*lam/2,F(0)])
        for i,T in enumerate(signatures):
            selected=[e for e in T if set(e)<=set(B)]
            if not T:d=K*lam
            elif not selected:d=F(0)
            elif len(T)>=2:d=K/F(4*len(T))
            else:
                e=T[0];g=q-7+te[e]
                assert g>0
                d=K*(ell-F(3,4)+F(te[e],6))/g
            assert 0<=d<=lam,('dual interval',q,t,B,T,d,lam)
            mu.extend([-counts[T]*(lam-d)/2,-counts[T]*d/2])
            z=lo if not selected else hi
            p[S+b*(R+1)+i]=abs(p[i]-z)
        mu.append(-lam)
        certificate_data.append({'basis':B,'lambda':str(lam),'ell':str(ell)})
    # Every verification is rational, including primal/dual strong equality.
    assert all(x>=0 for x in p)
    assert all(sum(p[j]*v for j,v in row)<=0 for row in rows)
    assert all(sum(p[j]*v for j,v in row)==1 for row in eq)
    assert len(mu)==len(rows) and len(nu)==len(eq) and all(x<=0 for x in mu)
    slack=[F(int(i==ep)) for i in range(n)]
    for x,row in zip(mu,rows):
        for j,v in row:slack[j]-=x*v
    for x,row in zip(nu,eq):
        for j,v in row:slack[j]-=x*v
    assert all(x>=0 for x in slack),('negative exact slack',q,t,min(slack))
    assert sum(nu)==p[ep]==delta
    return {'q':q,'C':sorted(C),'t':t,'U':U,'outside':O,'exact_optimum':str(delta),
            'low_density':str(lo),'high_density':str(hi),'primal':[str(x) for x in p],
            'dual_inequality':[str(x) for x in mu],'dual_equality':[str(x) for x in nu],
            'basis_data':certificate_data,'variables':n,'constraints':len(rows)+len(eq),
            'scope':'EXACT_INCIDENCE_LP; representation premise external unless supplied by classification/extension'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args()
    here=Path(__file__).resolve().parent;out=(here/args.out).resolve();assert out.is_relative_to(here);out.mkdir(parents=True,exist_ok=False)
    reps=json.loads((here/'results/classify02/summary.json').read_text())['class_representatives'];records=[]
    for rep in reps:
        C=tuple(tuple(tuple(e) for e in T) for T in rep['concurrent_perfect_matchings'])
        for q in (49,343):
            cert=construct(q,C);name=f"q{q}_class{rep['canonical_bitmask']}.json"
            (out/name).write_text(json.dumps(cert,indent=2));records.append({'file':name,'q':q,'class':rep['canonical_bitmask'],'t':len(C),'optimum':cert['exact_optimum']})
    # Synthetic incidence sets stress the algebra; no representability claim.
    probes=[(),PERFECT]+[(T,) for T in PERFECT]
    for C in probes:construct(13,C)
    summary={'pass':True,'extension_certificates':records,'synthetic_q13_cases':len(probes),
             'numerical_optimization_used':False,'general_proof':'separate hand argument, not finite tests'}
    (out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))


if __name__=='__main__':main()
