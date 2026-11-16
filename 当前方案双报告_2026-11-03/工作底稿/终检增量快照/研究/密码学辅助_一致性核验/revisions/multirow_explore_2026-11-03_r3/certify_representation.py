"""Produce rational primal/dual witnesses for two GF7 U_3_6 representations."""
from fractions import Fraction
from pathlib import Path
import argparse,hashlib,json
from kernel_minimax import Field,geometry


def dot(f,x,y):
    z=0
    for a,b in zip(x,y):z=f.add(z,f.mul(a,b))
    return z


def build(cols):
    f=Field(7);points,allowed2,bases=geometry(f,cols);N=len(points);B=len(bases)
    allowed1=[i for i,w in enumerate(points) if all(dot(f,w,v) for v in cols)]
    patterns=[]
    for b in bases:
        patterns.append([sum(1<<j for j,i in enumerate(b['columns']) if dot(f,w,cols[i])) for w in points]+[7+x for x in b['patterns']])
    states=2*N;wstart=states;ustart=states+14*B;ep=ustart+B*states;variables=ep+1
    rows=[];eq=[[(i,1) for i in range(states)]]
    for b,ps in enumerate(patterns):
        sizes={p:ps.count(p) for p in set(ps)};eq.append([(wstart+b*14+p-1,size) for p,size in sorted(sizes.items())])
        for i,p in enumerate(ps):
            w=wstart+b*14+p-1;u=ustart+b*states+i
            rows.append([(i,1),(w,-1),(u,-1)]);rows.append([(i,-1),(w,1),(u,-1)])
        rows.append([(ustart+b*states+i,Fraction(1,2)) for i in range(states)]+[(ep,-1)])
    fixed=[i for i in range(states) if (i<N and i not in allowed1) or (i>=N and i-N not in allowed2)]
    return rows,eq,variables,ep,fixed


def main():
    import numpy as np
    from scipy.optimize import linprog
    from scipy.sparse import coo_matrix
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args()
    root=Path(__file__).resolve().parent;out=(root/args.out).resolve();assert out.is_relative_to(root);out.mkdir(parents=True,exist_ok=False)
    scan=json.loads((root/'results/arcs_extended01/raw.json').read_text());selected={}
    for x in scan:
        if x['q']==7:selected.setdefault(x['exact_achieved_radius'],x['dictionary_columns'])
    receipts=[]
    for number,(label,cols) in enumerate(sorted(selected.items())):
        rows,eq,n,ep,fixed=build(cols)
        def sparse(rs):
            triples=[(i,j,float(v)) for i,row in enumerate(rs) for j,v in row]
            return coo_matrix(([v for i,j,v in triples],([i for i,j,v in triples],[j for i,j,v in triples])),shape=(len(rs),n)).tocsr()
        c=np.zeros(n);c[ep]=1;bounds=[(0,None)]*n
        for i in fixed:bounds[i]=(0,0)
        result=linprog(c,A_ub=sparse(rows),b_ub=np.zeros(len(rows)),A_eq=sparse(eq),b_eq=np.ones(len(eq)),bounds=bounds,method='highs');assert result.success
        def rational(xs):return [Fraction(float(v)).limit_denominator(10000000) for v in xs]
        x=rational(result.x);mu=rational(result.ineqlin.marginals);nu=rational(result.eqlin.marginals)
        assert all(v>=0 for v in x) and all(x[i]==0 for i in fixed)
        assert all(sum(x[j]*v for j,v in row)<=0 for row in rows)
        assert all(sum(x[j]*v for j,v in row)==1 for row in eq)
        assert all(v<=0 for v in mu)
        residual=[Fraction(int(i==ep)) for i in range(n)]
        for z,row in zip(mu,rows):
            for j,v in row:residual[j]-=z*v
        for z,row in zip(nu,eq):
            for j,v in row:residual[j]-=z*v
        assert all(v>=0 for j,v in enumerate(residual) if j not in fixed)
        assert x[ep]==sum(nu)==Fraction(label),(x[ep],sum(nu),label)
        profile={'q':7,'field':'prime_mod_7','dictionary_columns':cols,'rows':2,'allowed_supports':'all_size_at_most_3',
                 'amplitudes':'arbitrary_nonzero_independent_coordinates','mask':'input_independent','erasure':'probability_zero_all_columns',
                 'observation':'indexed_masked_columns','metric':'worst_support_minimax_simulator_TV','scope':'PUBLIC_ALGEBRA_ONLY'}
        digest=hashlib.sha256(json.dumps(profile,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        cert={'profile':profile,'profile_sha256':digest,'primal':[str(v) for v in x],
              'dual_inequality':[str(v) for v in mu],'dual_equality':[str(v) for v in nu],
              'objective':str(x[ep]),'authorizes_execution':False,'priority_verified':False}
        name=f'certificate_{number}.json';(out/name).write_text(json.dumps(cert,indent=2))
        receipts.append({'file':name,'objective':str(x[ep]),'variables':n,'inequalities':len(rows),'equalities':len(eq),
                         'exact_primal_dual_verified_by_producer':True,'profile_sha256':digest})
    assert len(receipts)==2
    (out/'summary.json').write_text(json.dumps(receipts,indent=2));print(json.dumps(receipts))


if __name__=='__main__':main()
