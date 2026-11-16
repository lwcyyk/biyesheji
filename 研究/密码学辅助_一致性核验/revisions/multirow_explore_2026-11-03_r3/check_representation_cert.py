"""Independent exact GF7 checker. No producer, optimizer, or field imports."""
from fractions import Fraction
from itertools import combinations,product
from pathlib import Path
import argparse,hashlib,json


def determinant(a):
    return (a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])
           -a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])
           +a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0]))%7


def check(cert):
    try:
        p=cert['profile'];cols=p['dictionary_columns']
        required={'q':7,'field':'prime_mod_7','dictionary_columns':cols,'rows':2,'allowed_supports':'all_size_at_most_3',
                  'amplitudes':'arbitrary_nonzero_independent_coordinates','mask':'input_independent','erasure':'probability_zero_all_columns',
                  'observation':'indexed_masked_columns','metric':'worst_support_minimax_simulator_TV','scope':'PUBLIC_ALGEBRA_ONLY'}
        if p!=required:return {'status':'MODEL_NOT_APPLICABLE'}
        if set(cert)!={'profile','profile_sha256','primal','dual_inequality','dual_equality','objective','authorizes_execution','priority_verified'}:return {'status':'INVALID_CERTIFICATE'}
        if cert['authorizes_execution'] is not False or cert['priority_verified'] is not False:return {'status':'INVALID_CERTIFICATE'}
        if cert['profile_sha256']!=hashlib.sha256(json.dumps(p,sort_keys=True,separators=(',',':')).encode()).hexdigest():return {'status':'INVALID_CERTIFICATE'}
        if len(cols)!=6 or any(len(v)!=3 or any(type(a) is not int or not 0<=a<7 for a in v) or not any(v) for v in cols):return {'status':'OUT_OF_SCOPE'}
        def norm(v):
            t=pow(next(a for a in v if a),5,7)
            return tuple(a*t%7 for a in v)
        points=sorted({norm(v) for v in product(range(7),repeat=3) if any(v)})
        assert len(points)==57
        forbidden2={norm(v) for v in cols}
        fixed=[i for i,w in enumerate(points) if any(sum(a*b for a,b in zip(w,v))%7==0 for v in cols)]
        fixed += [57+i for i,w in enumerate(points) if w in forbidden2]
        all_patterns=[]
        for S in combinations(range(6),3):
            a=[[cols[j][i] for j in S] for i in range(3)];det=determinant(a)
            if not det:return {'status':'MODEL_NOT_APPLICABLE','reason':'NOT_U_3_6'}
            # Cofactor inverse, deliberately not producer's elimination.
            inv=[]
            for i in range(3):
                row=[]
                for j in range(3):
                    sub=[[a[r][c] for c in range(3) if c!=i] for r in range(3) if r!=j]
                    row.append(((-1)**(i+j))*(sub[0][0]*sub[1][1]-sub[0][1]*sub[1][0])*pow(det,5,7)%7)
                inv.append(row)
            ps1=[sum(1<<j for j,c in enumerate(S) if sum(w[i]*cols[c][i] for i in range(3))%7) for w in points]
            ps2=[7+sum(1<<j for j in range(3) if sum(inv[j][i]*w[i] for i in range(3))%7) for w in points]
            all_patterns.append(ps1+ps2)
        N=114;W=N;U=N+20*14;ep=U+20*N;n=ep+1
        rows=[];equations=[[(i,Fraction(1)) for i in range(N)]]
        for b,ps in enumerate(all_patterns):
            counts={p:ps.count(p) for p in set(ps)}
            equations.append([(W+b*14+p-1,Fraction(count)) for p,count in sorted(counts.items())])
            for i,p in enumerate(ps):
                w=W+b*14+p-1;u=U+b*N+i
                rows.append([(i,1),(w,-1),(u,-1)]);rows.append([(i,-1),(w,1),(u,-1)])
            rows.append([(U+b*N+i,Fraction(1,2)) for i in range(N)]+[(ep,-1)])
        if any(len(cert[k])!=count for k,count in [('primal',n),('dual_inequality',len(rows)),('dual_equality',len(equations))]):return {'status':'INVALID_CERTIFICATE'}
        x=[Fraction(v) for v in cert['primal']];mu=[Fraction(v) for v in cert['dual_inequality']];nu=[Fraction(v) for v in cert['dual_equality']]
        if not all(v>=0 for v in x) or any(x[i] for i in fixed):return {'status':'INVALID_CERTIFICATE'}
        if any(sum(x[j]*v for j,v in row)>0 for row in rows):return {'status':'INVALID_CERTIFICATE'}
        if any(sum(x[j]*v for j,v in row)!=1 for row in equations):return {'status':'INVALID_CERTIFICATE'}
        if any(v>0 for v in mu):return {'status':'INVALID_CERTIFICATE'}
        slack=[Fraction(int(j==ep)) for j in range(n)]
        for coefficient,row in zip(mu,rows):
            for j,v in row:slack[j]-=coefficient*v
        for coefficient,row in zip(nu,equations):
            for j,v in row:slack[j]-=coefficient*v
        if any(v<0 for j,v in enumerate(slack) if j not in fixed):return {'status':'INVALID_CERTIFICATE'}
        if sum(nu)!=x[ep] or str(x[ep])!=cert['objective']:return {'status':'INVALID_CERTIFICATE'}
        return {'status':'VERIFIED','exact_optimum':str(x[ep]),'bases_checked':20,'kernel_states':114,
                'scope':'PUBLIC_FINITE_LP_CONDITIONAL_ON_KERNEL_REDUCTION','authorizes_execution':False,'priority_verified':False}
    except (KeyError,TypeError,ValueError,ZeroDivisionError,StopIteration,IndexError):return {'status':'INVALID_CERTIFICATE'}


def main():
    from copy import deepcopy
    parser=argparse.ArgumentParser();parser.add_argument('--cert-dir',required=True);parser.add_argument('--out',required=True);args=parser.parse_args()
    here=Path(__file__).resolve().parent;out=(here/args.out).resolve();assert out.is_relative_to(here);out.mkdir(parents=True,exist_ok=False)
    results=[];attacks=[]
    for path in sorted((here/args.cert_dir).glob('certificate_*.json')):
        cert=json.loads(path.read_text());result=check(cert);assert result['status']=='VERIFIED';results.append({'file':str(path.relative_to(here)),**result})
        for mode in ('objective','primal','dual','model','binding','authority'):
            forged=deepcopy(cert)
            if mode=='objective':forged['objective']='0'
            elif mode=='primal':forged['primal'][0]='1'
            elif mode=='dual':forged['dual_equality'][0]=str(Fraction(forged['dual_equality'][0])+1)
            elif mode=='model':forged['profile']['amplitudes']='equal_only'
            elif mode=='binding':forged['profile_sha256']='0'*64
            else:forged['authorizes_execution']=True
            actual=check(forged);assert actual['status']!='VERIFIED';attacks.append({'file':path.name,'attack':mode,'actual':actual['status'],'expected':'NOT_VERIFIED'})
    values=sorted(Fraction(x['exact_optimum']) for x in results);assert values==[Fraction(31,576),Fraction(11,204)]
    report={'results':results,'tampering':attacks,'exact_separation':str(values[1]-values[0]),'pass':True}
    (out/'checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))


if __name__=='__main__':main()
