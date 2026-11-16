"""Exact feasibility certificate for a general-arc analytic dual.

Checks the compact allocation identities; no numerical optimizer is involved.
"""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import argparse,json
from general_incidence import compile_arc,weights


def construct(compiled,q):
    n=compiled['n'];assert n>=5 and q>=16*n*n
    counts,U,O,W,ell=weights(compiled,q);m=n-3;N=q*q+q+1-n;D=U-3*(q-1);Z=(q-1)*U-3*O
    E=q*q+q+1-n*(q+1)+n*(n-1)//2;s=(q-1)**2;kappa=F(3*m,Z)
    low=F(D,(q-1)*Z);high=F(D+m,(q-1)*Z);value=m*low
    assert U*high+O*low==1 and 3*(q-1)*high+s*low==1
    edges=list(combinations(range(n),2));allocations={T:F(0) for T in counts};records=[]
    for B,L in ell.items():
        lam=3*L/U;assert 0<lam and 0<kappa<1
        d={};basis_edges=list(combinations(B,2))
        for T,c in counts.items():
            contained=[e for e in T if set(e)<=set(B)]
            assert len(contained)<=1
            if not T:amount=kappa*lam
            elif not contained:amount=F(0)
            elif len(T)>=2:amount=kappa/F(len(T)*(n-2))
            else:
                e=T[0];g=counts[T]
                multi=sum(F(v,len(P)) for P,v in counts.items() if len(P)>=2 and e in P)
                amount=kappa*(L-multi/F(n-2))/g
            assert 0<=amount<=lam,(n,q,B,T,amount,lam)
            if not T or contained:assert 0<amount<lam
            d[T]=amount;allocations[T]+=amount
        for e in basis_edges:assert sum(counts[T]*d[T] for T in counts if e in T)==kappa*L
        assert (s-E)*lam-(q-1)*kappa*L>0
        records.append({'basis':B,'ell':str(L),'lambda':str(lam)})
    assert all(x==kappa for x in allocations.values())
    assert F(1,2)-kappa+sum(kappa*L/(q-1)-(3*L/U)/2 for L in ell.values())==value
    return {'base_profile':compiled,'q':q,'N':N,'U':U,'O':O,'D':D,'Z':Z,'rank1_legal':E,
            'exact_value':str(value),'low':str(low),'high':str(high),'kappa':str(kappa),
            'counts':[{'matching':T,'count':v} for T,v in sorted(counts.items())],
            'edge_loads':[{'edge':e,'value':str(W[e])} for e in edges],'basis_weights':records,
            'scope':'fixed two-row three-dimensional model; field extension and general theorem are separate proofs',
            'authorizes_execution':False,'priority_verified':False}


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args()
    here=Path(__file__).resolve().parent;out=(here/args.out).resolve();assert out.is_relative_to(here);out.mkdir(parents=True,exist_ok=False)
    records=[]
    for n,power,base_q in [(5,4,7),(7,3,11),(8,3,13),(10,3,13)]:
        cols=[(1,a,a*a%base_q) for a in range(n)];compiled=compile_arc(cols,base_q);q=base_q**power
        cert=construct(compiled,q);name=f'n{n}_q{q}.json';(out/name).write_text(json.dumps(cert,indent=2))
        records.append({'file':name,'n':n,'base_q':base_q,'q':q,'multisecant_points':len(compiled['multisecant_points']),
                        'overlap_correction':compiled['overlap_correction'],'exact_value':cert['exact_value'],
                        'signature_groups':len(cert['counts']),'bases':len(cert['basis_weights'])})
    (out/'summary.json').write_text(json.dumps(records,indent=2));print(json.dumps(records))


if __name__=='__main__':main()
