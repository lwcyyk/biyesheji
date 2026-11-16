"""Small-domain discovery only: numeric LP is not a proof of optimality.

Fresh exploration; does not import or mutate the accepted mainline or r1 audit.
"""
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
import argparse
import json
import time


class Field:
    def __init__(self, p, m=1, polynomial=None):
        self.p, self.m, self.q = p, m, p ** m
        self.polynomial = polynomial
        self.add_table = [[self.encode([(a+b) % p for a,b in zip(self.digits(x),self.digits(y))]) for y in range(self.q)] for x in range(self.q)]
        self.mul_table = [[self.raw_mul(x,y) for y in range(self.q)] for x in range(self.q)]
        assert all(any(self.mul(a,b) == 1 for b in range(1,self.q)) for a in range(1,self.q))
    def digits(self,x):
        values=[]
        for _ in range(self.m): values.append(x % self.p); x //= self.p
        return values
    def encode(self,d): return sum(x*self.p**i for i,x in enumerate(d))
    def raw_mul(self,a,b):
        if self.m == 1: return a*b % self.p
        x,y=self.digits(a),self.digits(b); z=[0]*(2*self.m-1)
        for i,u in enumerate(x):
            for j,v in enumerate(y): z[i+j]=(z[i+j]+u*v)%self.p
        for j in range(len(z)-1,self.m-1,-1):
            for i in range(self.m): z[j-self.m+i]=(z[j-self.m+i]-z[j]*self.polynomial[i])%self.p
        return self.encode(z[:self.m])
    def add(self,x,y): return self.add_table[x][y]
    def neg(self,x): return self.encode([(-a)%self.p for a in self.digits(x)])
    def mul(self,x,y): return self.mul_table[x][y]
    def power(self,x,e):
        value=1
        while e:
            if e&1: value=self.mul(value,x)
            x=self.mul(x,x);e//=2
        return value
    def div(self,x,y):
        assert y
        return self.mul(x,self.power(y,self.q-2))


def roots_to_vectors(f):
    # q is infinity. For finite root t, mask (-t,1); infinity is mask(1,0).
    return [(f.neg(t),1) for t in range(f.q)]+[(1,0)]


def column(f,label): return (1,label) if label < f.q else (0,1)


def evaluate(f,mask,label):
    v=column(f,label)
    return f.add(f.mul(mask[0],v[0]),f.mul(mask[1],v[1]))


def transformations(f,labels):
    masks=roots_to_vectors(f); result=[]
    for left,right in combinations(labels,2):
        ratios=[]
        for m in masks:
            a,b=evaluate(f,m,left),evaluate(f,m,right)
            ratios.append(f.div(b,a) if a else f.q)
        assert len(set(ratios))==f.q+1
        inverse={v:i for i,v in enumerate(ratios)}
        for t in range(2,f.q):
            permutation=[inverse[f.mul(t,x) if x != f.q else f.q] for x in ratios]
            result.append((left,right,t,permutation))
    return result


def exact_tv(weights,permutation):
    return sum(abs(weights[i]-weights[j]) for i,j in enumerate(permutation))/2


def maximum_tv(f,labels,weights):
    return max((exact_tv(weights,perm) for *_,perm in transformations(f,labels)),default=Fraction(0))


def solve(f,labels,eta=Fraction(0)):
    import numpy as np
    from scipy.optimize import linprog
    from scipy.sparse import coo_matrix
    trans=transformations(f,labels); size=f.q+1; zero=size; ep=size+1
    count=size+2+size*len(trans); rr=[];cc=[];dd=[];upper=[]
    def row(items,rhs):
        i=len(upper);upper.append(rhs)
        for j,v in items: rr.append(i);cc.append(j);dd.append(v)
    for j in labels: row([(j,1),(zero,1)],float(eta))
    for h,(*_,perm) in enumerate(trans):
        start=size+2+h*size
        for i,j in enumerate(perm):
            row([(i,1),(j,-1),(start+i,-1)],0)
            row([(i,-1),(j,1),(start+i,-1)],0)
        row([(start+i,.5) for i in range(size)]+[(ep,-1)],0)
    a=coo_matrix((dd,(rr,cc)),shape=(len(upper),count)).tocsr()
    obj=np.zeros(count);obj[ep]=1
    eq=coo_matrix(([1]*(size+1),([0]*(size+1),list(range(size+1)))),shape=(1,count)).tocsr()
    start_time=time.perf_counter()
    solution=linprog(obj,A_ub=a,b_ub=np.array(upper),A_eq=eq,b_eq=[1],bounds=(0,None),method='highs')
    assert solution.success, solution.message
    weights=[Fraction(float(x)).limit_denominator(1000000) for x in solution.x[:size]]
    zero_weight=Fraction(float(solution.x[zero])).limit_denominator(1000000)
    assert sum(weights)+zero_weight==1
    assert all(weights[j]+zero_weight<=eta for j in labels)
    actual=maximum_tv(f,labels,weights)
    assert abs(float(actual)-solution.fun)<1e-7
    uniform=[Fraction(int(i not in labels),size-len(labels)) for i in range(size)]
    return {'q':f.q,'labels_infinity_is_q':labels,'eta_bound':str(eta),
            'numeric_lp_optimum_NOT_A_PROOF':float(solution.fun),'exact_candidate_TV':str(actual),
            'weights':[str(x) for x in weights],'zero_mask_weight':str(zero_weight),
            'uniform_noerasure_TV':str(maximum_tv(f,labels,uniform)),
            'variables':count,'constraints':len(upper),'solver_seconds':time.perf_counter()-start_time}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
    base=Path(__file__).resolve().parent;out=(base/args.out).resolve()
    assert out.is_relative_to(base);out.mkdir(parents=True,exist_ok=False)
    fields=[Field(3),Field(2,2,[1,1]),Field(5),Field(7),Field(2,3,[1,1,0]),Field(3,2,[1,0]),Field(11),Field(2,4,[1,1,0,0])]
    triangles=[];exact_cases=[]
    for f in fields:
        for eta in (Fraction(0),Fraction(1,2*(f.q+1)),Fraction(1,f.q+1)):
            row=solve(f,[f.q,0,1],eta)
            expected=max(Fraction(0),(1-(f.q+1)*eta)/(f.q-2))
            assert row['exact_candidate_TV']==str(expected)
            row['proved_formula_target']=str(expected);triangles.append(row)
        # Full output-distribution check for the no-erasure construction, all amplitudes.
        if f.q<=9:
            labels=[f.q,0,1];masks=roots_to_vectors(f);accepted=[i for i in range(f.q+1) if i not in labels]
            for pair in combinations(labels,2):
                reference=None;maximum=Fraction(0)
                for amps in product(range(1,f.q),repeat=2):
                    law=Counter(tuple(f.mul(a,f.mul(rho,evaluate(f,masks[t],label))) for label,a in zip(pair,amps)) for t in accepted for rho in range(1,f.q))
                    if reference is None: reference=law
                    distance=Fraction(sum(abs(law[k]-reference[k]) for k in law.keys()|reference.keys()),2*sum(law.values()))
                    maximum=max(maximum,distance)
                    assert all(all(y) for y in law)
                assert maximum==Fraction(1,f.q-2)
                exact_cases.append({'q':f.q,'support':pair,'full_output_TV':str(maximum),'amplitudes_exhausted':(f.q-1)**2})
    sublines=[]
    for Q,f in [(2,fields[1]),(3,fields[5]),(4,fields[7]),(5,Field(5,2,[2,0]))]:
        subfield=[x for x in range(f.q) if f.power(x,Q)==x];assert len(subfield)==Q
        labels=subfield+[f.q];row=solve(f,labels)
        assert row['exact_candidate_TV']==str(Fraction(1,Q))
        row['Q']=Q;row['proved_formula_target']=str(Fraction(1,Q));sublines.append(row)
    general=[];f=Field(11)
    for extra in ([2],[3],[4],[5],[2,3],[2,4],[2,5],[3,5]): general.append(solve(f,[f.q,0,1]+extra))
    result={'triangles':triangles,'sublines':sublines,'general_dictionary_probes':general,
            'full_output_checks':exact_cases,'LP_lower_bounds':'NUMERIC_ONLY_NOT_CERTIFIED',
            'purpose':'discovery and falsification, no novelty or deployment safety claim'}
    (out/'raw.json').write_text(json.dumps(result,indent=2))
    summary={'pass':True,'triangle_cases':len(triangles),'subline_cases':len(sublines),
             'full_output_support_checks':len(exact_cases),'general_probes':len(general),
             'nonuniform_improvements':[x for x in general if Fraction(x['exact_candidate_TV'])<Fraction(x['uniform_noerasure_TV'])]}
    (out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))


if __name__=='__main__':main()
