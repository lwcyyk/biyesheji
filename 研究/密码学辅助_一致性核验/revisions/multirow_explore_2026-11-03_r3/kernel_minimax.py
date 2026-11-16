"""Exploratory rank-(d-1) kernel minimax; LP outputs are not novelty proofs."""
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
import argparse
import importlib.util
import json

HERE=Path(__file__).resolve().parent
dependency=HERE.parent/'novelty_search_2026-11-03_r2/frontier_probe.py'
spec=importlib.util.spec_from_file_location('r2_field_readonly',dependency)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
Field=module.Field


def projectivize(f,x):
    pivot=next(v for v in x if v)
    return tuple(f.div(v,pivot) for v in x)


def inverse(f,a):
    n=len(a);a=[list(row)+[int(i==j) for j in range(n)] for i,row in enumerate(a)]
    for j in range(n):
        t=next((i for i in range(j,n) if a[i][j]),None)
        if t is None:return None
        a[t],a[j]=a[j],a[t];factor=a[j][j];a[j]=[f.div(x,factor) for x in a[j]]
        for i in range(n):
            if i==j:continue
            c=a[i][j];a[i]=[f.add(x,f.neg(f.mul(c,y))) for x,y in zip(a[i],a[j])]
    return [row[n:] for row in a]


def matvec(f,a,x):
    result=[]
    for row in a:
        v=0
        for u,w in zip(row,x):v=f.add(v,f.mul(u,w))
        result.append(v)
    return result


def geometry(f,columns):
    d=len(columns[0]);points=sorted({projectivize(f,x) for x in product(range(f.q),repeat=d) if any(x)})
    forbidden={projectivize(f,c) for c in columns};allowed=[i for i,x in enumerate(points) if x not in forbidden]
    bases=[]
    for selected in combinations(range(len(columns)),d):
        b=[[columns[j][i] for j in selected] for i in range(d)];bi=inverse(f,b)
        if bi is None:continue
        patterns=[sum(1<<i for i,v in enumerate(matvec(f,bi,x)) if v) for x in points]
        sizes={pattern:patterns.count(pattern) for pattern in set(patterns)}
        assert all(size==(f.q-1)**(pattern.bit_count()-1) for pattern,size in sizes.items())
        bases.append({'columns':selected,'patterns':patterns,'sizes':sizes})
    return points,allowed,bases


def solve(f,columns,fixed_weights=None):
    import numpy as np
    from scipy.optimize import linprog
    from scipy.sparse import coo_matrix
    points,allowed,bases=geometry(f,columns);N=len(points);B=len(bases);d=len(columns[0]);orbit_count=2**d-1
    wstart=N;ustart=N+B*orbit_count;ep=ustart+B*N;variables=ep+1
    rr=[];cc=[];vv=[];rhs=[];er=[];ec=[];ev=[];eh=[]
    def row(items,b,equality=False):
        a,bcols,c,values=(er,ec,ev,eh) if equality else (rr,cc,vv,rhs)
        i=len(values);values.append(b)
        for j,v in items:a.append(i);bcols.append(j);c.append(v)
    row([(i,1) for i in range(N)],1,True)
    for b,base in enumerate(bases):
        row([(wstart+b*orbit_count+pattern-1,size) for pattern,size in base['sizes'].items()],1,True)
        for i,pattern in enumerate(base['patterns']):
            w=wstart+b*orbit_count+pattern-1;u=ustart+b*N+i
            row([(i,1),(w,-1),(u,-1)],0);row([(i,-1),(w,1),(u,-1)],0)
        row([(ustart+b*N+i,.5) for i in range(N)]+[(ep,-1)],0)
    bounds=[(0,None)]*variables
    for i in range(N):
        if i not in allowed:bounds[i]=(0,0)
        if fixed_weights is not None:bounds[i]=(float(fixed_weights[i]),float(fixed_weights[i]))
    A=coo_matrix((vv,(rr,cc)),shape=(len(rhs),variables)).tocsr();E=coo_matrix((ev,(er,ec)),shape=(len(eh),variables)).tocsr()
    obj=np.zeros(variables);obj[ep]=1
    result=linprog(obj,A_ub=A,b_ub=np.array(rhs),A_eq=E,b_eq=np.array(eh),bounds=bounds,method='highs')
    assert result.success,result.message
    p=[Fraction(float(x)).limit_denominator(10000000) for x in result.x[:N]]
    assert sum(p)==1 and all(p[i]==0 for i in range(N) if i not in allowed)
    centers=[];distances=[]
    for b,base in enumerate(bases):
        densities={pattern:Fraction(float(result.x[wstart+b*orbit_count+pattern-1])).limit_denominator(10000000) for pattern in base['sizes']}
        assert sum(base['sizes'][t]*densities[t] for t in densities)==1
        distance=sum(abs(p[i]-densities[t]) for i,t in enumerate(base['patterns']))/2
        centers.append({str(k):str(v) for k,v in densities.items()});distances.append(distance)
    value=max(distances);assert abs(float(value)-result.fun)<1e-7
    return {'q':f.q,'d':d,'rank':d-1,'dictionary_columns':columns,'points':points,'allowed_count':len(allowed),
            'kernel_weights':[str(x) for x in p],'simulator_densities':centers,
            'basis_indices':[x['columns'] for x in bases],'exact_achieved_radius':str(value),
            'numeric_LP_lower_value_NOT_PROOF':float(result.fun),'variables':variables,'constraints':len(rhs)+len(eh)}


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args()
    target=(HERE/args.out).resolve();assert target.is_relative_to(HERE);target.mkdir(parents=True,exist_ok=False)
    rows=[]
    for f in (Field(3),Field(2,2,[1,1]),Field(5),Field(7),Field(2,3,[1,1,0]),Field(3,2,[1,0])):
        columns=[(1,0,0),(0,1,0),(0,0,1),(1,1,1)]
        points,allowed,_=geometry(f,columns);uniform=[Fraction(int(i in allowed),len(allowed)) for i in range(len(points))]
        candidate=solve(f,columns);baseline=solve(f,columns,uniform)
        candidate['uniform_baseline_exact_radius']=baseline['exact_achieved_radius']
        candidate['strict_improvement']=Fraction(candidate['exact_achieved_radius'])<Fraction(baseline['exact_achieved_radius'])
        rows.append(candidate)
    result={'cases':rows,'scope':'fixed rank d-1, no erasure, all independent supports; numeric lower bounds not exact certificates'}
    (target/'raw.json').write_text(json.dumps(result,indent=2))
    summary={'pass':True,'cases':len(rows),'results':[{k:x[k] for k in ('q','exact_achieved_radius','uniform_baseline_exact_radius','strict_improvement')} for x in rows]}
    (target/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))


if __name__=='__main__':main()
