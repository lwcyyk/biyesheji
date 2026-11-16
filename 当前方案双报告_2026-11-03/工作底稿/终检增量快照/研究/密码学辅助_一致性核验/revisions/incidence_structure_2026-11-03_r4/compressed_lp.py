"""Incidence-count LP: no enumeration of the q^2 projective point set."""
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import argparse,json
from incidence import compiled_counts


def build(q,C):
    counts=compiled_counts(q,C);signatures=sorted(counts);E=q*q-5*q+10;s=(q-1)**2
    assert E>=0
    B=list(combinations(range(6),3));R=len(signatures);W=R+1;U=W+5*len(B);ep=U+len(B)*(R+1);n=ep+1
    rows=[];equations=[[(i,counts[T]) for i,T in enumerate(signatures)]+[(R,E)]]
    for b,base in enumerate(B):
        edges=list(combinations(base,2));a=W+5*b;full=a+4
        equations.append([(a,s)]+[(a+1+j,q-1) for j in range(3)]+[(full,s)])
        uR=U+b*(R+1)+R
        rows.append([(R,1),(a,-1),(uR,-1)]);rows.append([(R,-1),(a,1),(uR,-1)])
        for i,T in enumerate(signatures):
            selected=[e for e in T if set(e)<=set(base)];assert len(selected)<=1
            z=full if not selected else a+1+edges.index(selected[0]);u=U+b*(R+1)+i
            rows.append([(i,1),(z,-1),(u,-1)]);rows.append([(i,-1),(z,1),(u,-1)])
        rows.append([(uR,Fraction(E,2)),(a,Fraction(s-E,2)),(full,Fraction(3,2))]
                    +[(U+b*(R+1)+i,Fraction(counts[T],2)) for i,T in enumerate(signatures)]+[(ep,-1)])
    return rows,equations,n,ep,signatures,counts


def solve(q,C):
    import numpy as np
    from scipy.optimize import linprog
    from scipy.sparse import coo_matrix
    rows,eq,n,ep,signatures,counts=build(q,C)
    def sparse(rs):
        t=[(i,j,float(v)) for i,row in enumerate(rs) for j,v in row]
        return coo_matrix(([x[2] for x in t],([x[0] for x in t],[x[1] for x in t])),shape=(len(rs),n)).tocsr()
    # Scale all primal densities and objective by q^2 to avoid tiny values.
    c=np.zeros(n);c[ep]=1
    result=linprog(c,A_ub=sparse(rows),b_ub=np.zeros(len(rows)),A_eq=sparse(eq),b_eq=np.full(len(eq),q*q),bounds=(0,None),method='highs')
    assert result.success,result.message
    return {'q':q,'concurrent_count':len(C),'scaled_numeric_radius':float(result.fun),'numeric_radius_NOT_PROOF':float(result.fun/(q*q)),
            'variables':n,'constraints':len(rows)+len(eq),'signatures':len(signatures),
            'suggested_rational_NOT_CERTIFIED':str(Fraction(float(result.fun/(q*q))).limit_denominator(10**10)),
            'scaled_density_values':sorted(set(round(x,10) for x in result.x[:len(signatures)+1]))}


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--classification',default='results/classify02/summary.json');args=p.parse_args()
    here=Path(__file__).resolve().parent;out=(here/args.out).resolve();assert out.is_relative_to(here);out.mkdir(parents=True,exist_ok=False)
    classified=json.loads((here/args.classification).read_text());records=[]
    certified={x['canonical_bitmask']:x['objective'] for x in classified['certified_representatives']}
    for rep in classified['class_representatives']:
        C=tuple(tuple(tuple(e) for e in T) for T in rep['concurrent_perfect_matchings'])
        for q in (7,49,343):
            row=solve(q,C);row['class']=rep['canonical_bitmask'];row['GF7_previous_certified_value']=certified.get(rep['canonical_bitmask'])
            if q==7 and rep['canonical_bitmask'] in certified:assert abs(row['numeric_radius_NOT_PROOF']-float(Fraction(certified[rep['canonical_bitmask']])))<1e-9
            records.append(row)
    (out/'raw.json').write_text(json.dumps(records,indent=2));print(json.dumps(records))


if __name__=='__main__':main()
