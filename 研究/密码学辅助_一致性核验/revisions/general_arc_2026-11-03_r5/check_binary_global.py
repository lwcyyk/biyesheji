"""Independent GF(2^15) witness and compact algebra verification.

Uses convolution/reduction and 2x3 kernel solving, not the producer's cross
product field implementation. Does not import any candidate module.
"""
from collections import defaultdict
from fractions import Fraction as F
from itertools import combinations,permutations
from pathlib import Path
import argparse,json

Q=32768;MOD=32771


def multiply(a,b):
    value=0
    for i in range(15):
        if (b>>i)&1:value^=a<<i
    while value.bit_length()>15:value^=MOD<<(value.bit_length()-16)
    return value


def power(a,n):
    value=1
    for bit in bin(n)[2:]:
        value=multiply(value,value)
        if bit=='1':value=multiply(value,a)
    return value


def check_field():
    def remainder(a,b):
        while a.bit_length()>=b.bit_length():a^=b<<(a.bit_length()-b.bit_length())
        return a
    def gcd(a,b):
        while b:a,b=b,remainder(a,b)
        return a
    assert power(2,1<<15)==2
    values=[gcd(power(2,1<<k)^2,MOD) for k in (5,3)]
    assert values==[1,1]
    return {'frobenius_remainder':2,'gcd_results':values,'irreducibility_criterion':'Rabin'}


def norm(v):
    inverse=power(next(x for x in v if x),Q-2)
    return tuple(multiply(x,inverse) for x in v)


def kernel_pair(a,b):
    for i,j in combinations(range(3),2):
        determinant=multiply(a[i],b[j])^multiply(a[j],b[i])
        if determinant:
            k=next(k for k in range(3) if k not in (i,j));inv=power(determinant,Q-2);v=[0,0,0];v[k]=1
            v[i]=multiply(multiply(b[j],a[k])^multiply(a[j],b[k]),inv)
            v[j]=multiply(multiply(b[i],a[k])^multiply(a[i],b[k]),inv)
            return norm(v)
    raise AssertionError('dependent rows')


def determinant(rows):
    value=0
    for p in permutations(range(3)):
        term=1
        for i in range(3):term=multiply(term,rows[i][p[i]])
        value^=term
    return value


def check(cert):
    b=cert['base_profile'];cols=[tuple(v) for v in b['columns']];n=len(cols)
    assert cert['q']==b['base_q']==Q and b['field_polynomial']==MOD and n==10
    assert cert['authorizes_execution'] is False and cert['priority_verified'] is False and b['n']==n
    assert all(len(v)==3 and all(type(x) is int and 0<=x<Q for x in v) for v in cols)
    assert all(determinant([cols[i],cols[j],cols[k]]) for i,j,k in combinations(range(n),3))
    edges=list(combinations(range(n),2));lines={e:kernel_pair(cols[e[0]],cols[e[1]]) for e in edges};points=defaultdict(set)
    for e,f in combinations(edges,2):
        if set(e)&set(f):continue
        points[kernel_pair(lines[e],lines[f])].update((e,f))
    multi={tuple(sorted(T)):p for p,T in points.items()}
    declared={tuple(tuple(e) for e in x['edges']):tuple(x['point']) for x in b['multisecant_points']};assert declared==multi
    counts={T:1 for T in multi}
    for e in edges:counts[(e,)]=Q-1-sum(e in T for T in multi)
    U=sum(counts.values());N=Q*Q+Q+1-n;O=N-U;counts[()]=O
    assert {tuple(tuple(e) for e in x['matching']):x['count'] for x in cert['counts']}==counts
    J=sum(len(T)-1 for T in multi);Tstat=sum((len(T)-1)*(len(T)-2)//2 for T in multi)
    assert sum(len(T)*(len(T)-1)//2 for T in multi)==630 and b['overlap_correction']==J
    W={e:sum(F(c,len(T)) for T,c in counts.items() if e in T) for e in edges};E=Q*Q+Q+1-n*(Q+1)+45;s=(Q-1)**2
    value=F(cert['exact_value']);low=F(cert['low']);high=F(cert['high']);kappa=F(cert['kappa']);D=U-3*(Q-1);Z=(Q-1)*U-3*O
    assert all(cert[key]==v for key,v in [('N',N),('U',U),('O',O),('D',D),('Z',Z),('rank1_legal',E)])
    assert low==F(D,(Q-1)*Z) and high==F(D+7,(Q-1)*Z) and value==7*low and kappa==F(21,Z)
    assert U*high+O*low==1 and 3*(Q-1)*high+s*low==1
    assert {tuple(x['edge']):F(x['value']) for x in cert['edge_loads']}==W
    ell={tuple(x['basis']):F(x['ell']) for x in cert['basis_weights']};lam={tuple(x['basis']):F(x['lambda']) for x in cert['basis_weights']}
    assert set(ell)==set(combinations(range(n),3)) and all(lam[B]==3*ell[B]/U for B in ell)
    assert sum(lam.values())==1 and all(sum(L for B,L in ell.items() if set(e)<=set(B))==W[e] for e in edges)
    coverage={T:F(0) for T in counts};dual=F(1,2)-kappa
    for B,L in ell.items():
        allocation={}
        for T,c in counts.items():
            hit=[e for e in T if set(e)<=set(B)]
            if not T:d=kappa*lam[B]
            elif not hit:d=F(0)
            elif len(T)>=2:d=kappa/F(8*len(T))
            else:
                e=T[0];A=sum(F(c,len(R)) for R,c in counts.items() if len(R)>=2 and e in R)
                d=kappa*(L-A/8)/counts[T]
            assert 0<=d<=lam[B]
            if not T or hit:assert 0<d<lam[B]
            allocation[T]=d;coverage[T]+=d
        assert all(sum(counts[T]*allocation[T] for T in counts if e in T)==kappa*L for e in combinations(B,2))
        assert (s-E)*lam[B]-(Q-1)*kappa*L>0
        dual+=kappa*L/(Q-1)-lam[B]/2
    assert all(v==kappa for v in coverage.values()) and dual==value
    return {'n':n,'q':Q,'J':J,'T':Tstat,'multisecant_points':len(multi),'exact_value':str(value),'status':'VERIFIED_PUBLIC_MODEL_ONLY'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
    here=Path(__file__).resolve().parent;out=(here/args.out).resolve();assert out.is_relative_to(here);out.mkdir(parents=True,exist_ok=False)
    field_check=check_field();results=[]
    for name in ('best','worst'):
        cert=json.loads((here/'results/global01'/f'{name}_certificate.json').read_text());results.append({'kind':name,**check(cert)})
    assert results[0]['T']==0 and results[1]['T']==378
    gap=F(results[1]['exact_value'])-F(results[0]['exact_value']);assert gap>0
    report={'pass':True,'field_check':field_check,'results':results,'exact_gap':str(gap),'scope':'finite inputs, field validity and dual feasibility; general optimality argument separate'}
    (out/'checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))


if __name__=='__main__':main()
