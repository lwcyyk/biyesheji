"""Independent LP assembly allowing both rank-one and rank-two kernels.

Uses field syntax and projective enumeration, not the candidate weight formula.
Numeric lower values remain corroboration, not a proof certificate.
"""
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import argparse
import json
from kernel_minimax import Field,geometry,matvec


def dot(f,x,y):
    r=0
    for a,b in zip(x,y):r=f.add(r,f.mul(a,b))
    return r


def main():
    import numpy as np
    from scipy.optimize import linprog
    from scipy.sparse import coo_matrix
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
    base=Path(__file__).resolve().parent;out=(base/args.out).resolve();assert out.is_relative_to(base);out.mkdir(parents=True,exist_ok=False)
    records=[]
    for f in (Field(3),Field(2,2,[1,1]),Field(5),Field(7)):
        cols=[(1,0,0),(0,1,0),(0,0,1),(1,1,1)];points,allowed2,bases=geometry(f,cols);N=len(points)
        allowed1=[i for i,w in enumerate(points) if all(dot(f,w,v) for v in cols)]
        all_patterns=[]
        for b in bases:
            p1=[sum(1<<j for j,i in enumerate(b['columns']) if dot(f,w,cols[i])) for w in points]
            all_patterns.append(p1+[7+t for t in b['patterns']])
        states=2*N;wstart=states;ustart=states+4*14;ep=ustart+4*states;variables=ep+1
        ar=[];ac=[];av=[];ab=[];er=[];ec=[];ev=[];eb=[]
        def row(items,rhs,eq=False):
            rr,cc,vv,bb=(er,ec,ev,eb) if eq else (ar,ac,av,ab);i=len(bb);bb.append(rhs)
            for j,x in items:rr.append(i);cc.append(j);vv.append(x)
        row([(i,1) for i in range(states)],1,True)
        for b,patterns in enumerate(all_patterns):
            sizes={p:patterns.count(p) for p in set(patterns)}
            row([(wstart+b*14+p-1,s) for p,s in sizes.items()],1,True)
            for i,p in enumerate(patterns):
                w=wstart+b*14+p-1;u=ustart+b*states+i
                row([(i,1),(w,-1),(u,-1)],0);row([(i,-1),(w,1),(u,-1)],0)
            row([(ustart+b*states+i,.5) for i in range(states)]+[(ep,-1)],0)
        bounds=[(0,None)]*variables
        for i in range(states):
            if (i<N and i not in allowed1) or (i>=N and i-N not in allowed2):bounds[i]=(0,0)
        A=coo_matrix((av,(ar,ac)),shape=(len(ab),variables)).tocsr();E=coo_matrix((ev,(er,ec)),shape=(len(eb),variables)).tocsr()
        objective=np.zeros(variables);objective[ep]=1
        result=linprog(objective,A_ub=A,b_ub=ab,A_eq=E,b_eq=eb,bounds=bounds,method='highs');assert result.success
        expected=Fraction(f.q-2,(f.q-1)*(f.q*f.q-3));assert abs(result.fun-float(expected))<1e-8
        records.append({'q':f.q,'rank1_kernel_count':len(allowed1),'rank2_kernel_count':len(allowed2),
                        'numeric_mixed_rank_minimum_NOT_PROOF':float(result.fun),'hand_proof_value':str(expected),
                        'rank1_probability_in_returned_optimum':float(sum(result.x[:N])),
                        'variables':variables,'constraints':len(ab)+len(eb)})
    (out/'raw.json').write_text(json.dumps(records,indent=2))
    summary={'pass':True,'fields':len(records),'scope':'numeric all-rank mixture corroboration, not general proof'}
    (out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps({'summary':summary,'records':records}))


if __name__=='__main__':main()
