"""Independent exact checker for saved extension-field incidence LP certificates.

No producer, SciPy, incidence.py, or compressed_lp imports. Fixed model only.
"""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import argparse,json


def matchings(vertices,size):
    if size==0:return [()]
    if len(vertices)<2*size:return []
    first=vertices[0];out=matchings(vertices[1:],size)
    for j in vertices[1:]:
        rest=tuple(x for x in vertices[1:] if x!=j)
        out += [tuple(sorted(((first,j),)+T)) for T in matchings(rest,size-1)]
    return out


def check(cert,expected_C):
    try:
        q=cert['q'];C=tuple(sorted(tuple(sorted(tuple(e) for e in T)) for T in cert['C']))
        expected_fields={'q','C','t','U','outside','exact_optimum','low_density','high_density','primal','dual_inequality','dual_equality','basis_data','variables','constraints','scope'}
        if set(cert)!=expected_fields:return {'status':'INVALID_CERTIFICATE'}
        if type(q) is not int or q not in (16,49,343):return {'status':'OUT_OF_SCOPE'}
        M={k:set(matchings(tuple(range(6)),k)) for k in (1,2,3)}
        if len(set(C))!=len(C) or not set(C)<=M[3] or C not in expected_C:return {'status':'INVALID_CONTEXT'}
        c={T:1 for T in C}
        for T in M[2]:
            if not any(set(T)<=set(P) for P in C):c[T]=1
        for (e,) in M[1]:
            used=sum(e in T for T in c)
            c[(e,)]=q-1-used
        c[()]=q*q+q-5-sum(c.values());c={T:n for T,n in c.items() if n}
        if any(n<0 for n in c.values()):return {'status':'INVALID_CONTEXT'}
        union=sum(n for T,n in c.items() if T);outside=c.get((),0)
        if any(type(cert[k]) is not int or cert[k]!=v for k,v in [('t',len(C)),('U',union),('outside',outside)]):return {'status':'INVALID_CERTIFICATE'}
        signatures=sorted(c);R=len(signatures);E=q*q+q+1-6*(q+1)+15;s=(q-1)**2
        W=R+1;U=W+100;ep=U+20*(R+1);variables=ep+1
        if len(cert['primal'])!=variables:return {'status':'INVALID_CERTIFICATE'}
        x=[F(v) for v in cert['primal']];mu=[F(v) for v in cert['dual_inequality']];nu=[F(v) for v in cert['dual_equality']]
        rows=[];eq=[[(i,c[T]) for i,T in enumerate(signatures)]+[(R,E)]]
        if len(cert['basis_data'])!=20:return {'status':'INVALID_CERTIFICATE'}
        for b,B in enumerate(combinations(range(6),3)):
            datum=cert['basis_data'][b];cB=sum(any(set(e)<=set(B) for e in T) for T in C);ell=F(3*q-12+2*cB-len(C),12)
            if set(datum)!={'basis','lambda','ell'} or datum['basis']!=list(B) or F(datum['ell'])!=ell or F(datum['lambda'])!=3*ell/union:return {'status':'INVALID_CERTIFICATE'}
            edges=list(combinations(B,2));a=W+5*b;full=a+4;rU=U+b*(R+1)+R
            eq.append([(a,s),(a+1,q-1),(a+2,q-1),(a+3,q-1),(full,s)])
            rows.extend([[(R,1),(a,-1),(rU,-1)],[(R,-1),(a,1),(rU,-1)]])
            for i,T in enumerate(signatures):
                e=next((e for e in edges if e in T),None);z=full if e is None else a+1+edges.index(e);j=U+b*(R+1)+i
                rows.extend([[(i,1),(z,-1),(j,-1)],[(i,-1),(z,1),(j,-1)]])
            rows.append([(rU,F(E,2)),(a,F(s-E,2)),(full,F(3,2))]+[(U+b*(R+1)+i,F(c[T],2)) for i,T in enumerate(signatures)]+[(ep,-1)])
        if len(mu)!=len(rows) or len(nu)!=len(eq):return {'status':'INVALID_CERTIFICATE'}
        if cert['variables']!=variables or cert['constraints']!=len(rows)+len(eq):return {'status':'INVALID_CERTIFICATE'}
        D=union-3*(q-1);Z=(q-1)*union-3*outside
        if F(cert['low_density'])!=F(D,(q-1)*Z) or F(cert['high_density'])!=F(D+3,(q-1)*Z):return {'status':'INVALID_CERTIFICATE'}
        if cert['scope']!='EXACT_INCIDENCE_LP; representation premise external unless supplied by classification/extension':return {'status':'INVALID_CERTIFICATE'}
        if any(v<0 for v in x) or any(v>0 for v in mu):return {'status':'INVALID_CERTIFICATE'}
        if any(sum(x[j]*v for j,v in row)>0 for row in rows):return {'status':'INVALID_CERTIFICATE'}
        if any(sum(x[j]*v for j,v in row)!=1 for row in eq):return {'status':'INVALID_CERTIFICATE'}
        residual=[F(int(i==ep)) for i in range(variables)]
        for z,row in zip(mu,rows):
            for j,v in row:residual[j]-=z*v
        for z,row in zip(nu,eq):
            for j,v in row:residual[j]-=z*v
        if any(v<0 for v in residual) or sum(nu)!=x[ep] or str(x[ep])!=cert['exact_optimum']:return {'status':'INVALID_CERTIFICATE'}
        return {'status':'VERIFIED','q':q,'t':len(C),'exact_optimum':str(x[ep]),
                'scope':'FIXED_PUBLIC_MODEL_INCIDENCE_LP; general reduction and field embedding are separate proofs',
                'authorizes_execution':False,'priority_verified':False}
    except (KeyError,TypeError,ValueError,IndexError,ZeroDivisionError):return {'status':'INVALID_CERTIFICATE'}


def main():
    from copy import deepcopy
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args()
    here=Path(__file__).resolve().parent;out=(here/args.out).resolve();assert out.is_relative_to(here);out.mkdir(parents=True,exist_ok=False)
    reps=json.loads((here/'results/classify02/summary.json').read_text())['class_representatives']
    expected_extension_C={tuple(sorted(tuple(sorted(tuple(e) for e in T)) for T in r['concurrent_perfect_matchings'])) for r in reps}
    all_matchings=tuple(sorted(matchings(tuple(range(6)),3)))
    expected_GF16_C={(),all_matchings}
    results=[];attacks=[]
    paths=sorted((here/'results/analytic01').glob('q*.json'))+sorted((here/'results/gf16_exact01').glob('q*.json'))
    for path in paths:
        cert=json.loads(path.read_text());expected_C=expected_GF16_C if cert['q']==16 else expected_extension_C
        actual=check(cert,expected_C);assert actual['status']=='VERIFIED';results.append({'file':path.name,**actual})
        for mode in ('value','primal','dual','context','field','metadata'):
            bad=deepcopy(cert)
            if mode=='value':bad['exact_optimum']='0'
            elif mode=='primal':bad['primal'][0]='1'
            elif mode=='dual':bad['dual_equality'][0]=str(F(bad['dual_equality'][0])+1)
            elif mode=='context':bad['C']=[all_matchings[0]] if cert['q']==16 else []
            elif mode=='metadata':bad['t']+=1
            else:bad['q']=13
            outcome=check(bad,expected_C);assert outcome['status']!='VERIFIED';attacks.append({'file':path.name,'attack':mode,'actual':outcome['status']})
    report={'pass':True,'results':results,'tampering':attacks,'independent_from_producer':True}
    (out/'checks.json').write_text(json.dumps(report,indent=2));print(json.dumps({'pass':True,'certificates':len(results),'tampering_checks':len(attacks)}))


if __name__=='__main__':main()
