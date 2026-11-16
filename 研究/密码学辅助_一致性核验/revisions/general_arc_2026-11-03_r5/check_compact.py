"""Independent prime-field reconstruction and exact dual-allocation checker.

No imports from the compiler, candidate constructor, or numerical optimizer.
"""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
from collections import Counter
import argparse,json


def determinant(a,b,c,p):return (a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0]))%p


def check(cert):
    try:
        base=cert['base_profile'];p=base['base_q'];cols=[tuple(v) for v in base['columns']];n=len(cols);q=cert['q']
        if type(p) is not int or p not in (7,11,13) or not 5<=n<=10 or type(q) is not int or not q>=16*n*n:return {'status':'OUT_OF_SCOPE'}
        quotient=q;power=0
        while quotient%p==0:quotient//=p;power+=1
        if quotient!=1 or not 1<=power<=4:return {'status':'OUT_OF_SCOPE'}
        if any(len(v)!=3 or any(type(x) is not int or not 0<=x<p for x in v) for v in cols):return {'status':'INVALID_INPUT'}
        if not all(determinant(cols[i],cols[j],cols[k],p) for i,j,k in combinations(range(n),3)):return {'status':'MODEL_NOT_APPLICABLE'}
        # Explicit dual/projective-point enumeration, unlike the pair-intersection producer.
        points=[(0,0,1)]+[(0,1,a) for a in range(p)]+[(1,a,b) for a in range(p) for b in range(p)]
        edges=list(combinations(range(n),2));multi={}
        def normalize(v):
            z=pow(next(x for x in v if x),p-2,p);return tuple(x*z%p for x in v)
        dictionary={normalize(v) for v in cols}
        for point in points:
            if point in dictionary:continue
            T=tuple(e for e in edges if determinant(point,cols[e[0]],cols[e[1]],p)==0)
            if len(T)>=2:multi[T]=point
        counts={T:1 for T in multi}
        for e in edges:counts[(e,)]=q-1-sum(e in T for T in multi)
        U=sum(counts.values());O=q*q+q+1-n-U;counts[()]=O
        if not O>0 or any(c<=0 for c in counts.values()):return {'status':'INVALID_CERTIFICATE'}
        declared={tuple(tuple(e) for e in r['matching']):r['count'] for r in cert['counts']}
        if declared!=counts:return {'status':'INVALID_CERTIFICATE'}
        J=sum(len(T)-1 for T in multi);P2=sum(len(T)*(len(T)-1)//2 for T in multi)
        if P2!=3*len(list(combinations(range(n),4))) or J!=base['overlap_correction']:return {'status':'INVALID_CERTIFICATE'}
        actual_multi={tuple(tuple(e) for e in r['edges']):tuple(r['point']) for r in base['multisecant_points']}
        if actual_multi!=multi:return {'status':'INVALID_CERTIFICATE'}
        m=n-3;N=q*q+q+1-n;D=U-3*(q-1);Z=(q-1)*U-3*O;E=q*q+q+1-n*(q+1)+n*(n-1)//2;s=(q-1)**2
        for key,value in [('N',N),('U',U),('O',O),('D',D),('Z',Z),('rank1_legal',E)]:
            if type(cert[key]) is not int or cert[key]!=value:return {'status':'INVALID_CERTIFICATE'}
        low=F(cert['low']);high=F(cert['high']);kappa=F(cert['kappa']);value=F(cert['exact_value'])
        if low!=F(D,(q-1)*Z) or high!=F(D+m,(q-1)*Z) or kappa!=F(3*m,Z) or value!=m*low:return {'status':'INVALID_CERTIFICATE'}
        if U*high+O*low!=1 or 3*(q-1)*high+s*low!=1:return {'status':'INVALID_CERTIFICATE'}
        W={e:sum(F(c,len(T)) for T,c in counts.items() if e in T) for e in edges}
        if {tuple(r['edge']):F(r['value']) for r in cert['edge_loads']}!=W:return {'status':'INVALID_CERTIFICATE'}
        S={i:sum(W[e] for e in edges if i in e) for i in range(n)}
        bases=list(combinations(range(n),3));ell={B:(sum(W[e] for e in combinations(B,2))-sum(S[i] for i in B)/F(n-3)+F(2*U,(n-3)*(n-2)))/F(n-4) for B in bases}
        supplied={tuple(r['basis']):(F(r['ell']),F(r['lambda'])) for r in cert['basis_weights']}
        if len(supplied)!=len(bases) or any(supplied.get(B)!=(L,3*L/U) for B,L in ell.items()):return {'status':'INVALID_CERTIFICATE'}
        if any(sum(L for B,L in ell.items() if set(e)<=set(B))!=W[e] for e in edges):return {'status':'INVALID_CERTIFICATE'}
        coverage={T:F(0) for T in counts};objective=F(1,2)-kappa
        for B,L in ell.items():
            lam=3*L/U
            if lam<=0 or kappa<=0 or kappa>=1:return {'status':'INVALID_CERTIFICATE'}
            allocation={}
            for T,c in counts.items():
                hit=[e for e in T if set(e)<=set(B)]
                if not T:d=kappa*lam
                elif not hit:d=F(0)
                elif len(T)>=2:d=kappa/F((n-2)*len(T))
                else:
                    e=T[0];mass=sum(F(v,len(A)) for A,v in counts.items() if len(A)>=2 and e in A)
                    d=kappa*(L-mass/F(n-2))/counts[T]
                if not 0<=d<=lam:return {'status':'INVALID_CERTIFICATE'}
                if (not T or hit) and not 0<d<lam:return {'status':'INVALID_CERTIFICATE'}
                allocation[T]=d;coverage[T]+=d
            if any(sum(counts[T]*allocation[T] for T in counts if e in T)!=kappa*L for e in combinations(B,2)):return {'status':'INVALID_CERTIFICATE'}
            if (s-E)*lam-(q-1)*kappa*L<=0:return {'status':'INVALID_CERTIFICATE'}
            objective+=kappa*L/(q-1)-lam/2
        if any(v!=kappa for v in coverage.values()) or objective!=value:return {'status':'INVALID_CERTIFICATE'}
        if cert['authorizes_execution'] is not False or cert['priority_verified'] is not False:return {'status':'INVALID_CERTIFICATE'}
        return {'status':'VERIFIED','n':n,'q':q,'base_q':p,'extension_degree':power,'U':U,'J':J,'exact_value':str(value),
                'scope':'PUBLIC_FIXED_MODEL_COMPACT_DUAL; hand reduction and extension theorem separate','authorizes_execution':False}
    except (KeyError,TypeError,ValueError,ZeroDivisionError,StopIteration):return {'status':'INVALID_CERTIFICATE'}


def main():
    from copy import deepcopy
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args()
    here=Path(__file__).resolve().parent;out=(here/args.out).resolve();assert out.is_relative_to(here);out.mkdir(parents=True,exist_ok=False)
    results=[];attacks=[]
    for path in sorted((here/'results/general01').glob('n*.json')):
        cert=json.loads(path.read_text());result=check(cert);assert result['status']=='VERIFIED',result;results.append({'file':path.name,**result})
        for key in ('exact_value','high','kappa','U','basis_weights','authorizes_execution'):
            bad=deepcopy(cert)
            if key=='basis_weights':bad[key][0]['ell']='0'
            elif key=='authorizes_execution':bad[key]=True
            elif key=='U':bad[key]+=1
            else:bad[key]=str(F(bad[key])+1)
            actual=check(bad);assert actual['status']!='VERIFIED';attacks.append({'file':path.name,'field':key,'status':actual['status']})
    report={'pass':True,'results':results,'tampering':attacks,'independent_from_producer':True}
    (out/'checks.json').write_text(json.dumps(report,indent=2));print(json.dumps({'pass':True,'certificates':len(results),'tampering':len(attacks)}))


if __name__=='__main__':main()
