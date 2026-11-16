"""Independent public geometry checks and fixed-width field validation."""
from pathlib import Path
from fractions import Fraction
from math import comb
import hashlib
import importlib.util
import json
import sys
import time
import numpy as np

ROOT=Path(__file__).resolve().parent
BASE=ROOT.parents[1]


def mul(a,b,degree,tail):
    result=0
    mask=(1<<degree)-1
    while b:
        if b&1:result^=a
        b>>=1
        carry=a>>(degree-1)
        a=(a<<1)&mask
        if carry:a^=tail
    return result


def power(a,n,degree,tail):
    value=1
    while n:
        if n&1:value=mul(value,a,degree,tail)
        a=mul(a,a,degree,tail);n>>=1
    return value


def polynomial_gcd(a,b):
    while b:
        while a and a.bit_length()>=b.bit_length():a^=b<<(a.bit_length()-b.bit_length())
        a,b=b,a
    return a


def check_field_and_embedding(params):
    modulus=(1<<128)|0x87
    assert params['modulus']==modulus
    value=2
    middle=None
    for i in range(128):
        value=mul(value,value,128,0x87)
        if i==63:middle=value
    assert value==2 and polynomial_gcd(middle^2,modulus)==1
    theta=params['theta']
    assert power(theta,256,128,0x87)==theta
    assert power(theta,8,128,0x87)^power(theta,4,128,0x87)^power(theta,3,128,0x87)^theta^1==0
    basis=[power(theta,i,128,0x87) for i in range(8)]
    expected=[]
    for byte in range(256):
        value=0
        for i in range(8):
            if byte>>i&1:value^=basis[i]
        expected.append(value)
    assert expected==params['embed'] and len(set(expected))==256
    return {'binary_modulus_irreducible':True,'subfield_embedding_verified':True}


def verify_r5(model,params):
    started=time.monotonic_ns()
    q=model['q'];n=model['n']
    assert q==1<<128 and model['k']==3 and model['d']==3 and model['r']==2
    assert model['field_bits']==128 and model['modulus']==(1<<128)|0x87
    assert n>=5 and q>=16*n*n
    table=np.array([[mul(i,j,8,0x1b) for j in range(256)] for i in range(256)],dtype=np.int64)
    inverse=np.array([0]+[power(i,254,8,0x1b) for i in range(1,256)],dtype=np.int64)
    members=np.zeros(256,dtype=bool);members[:n]=True
    histogram={}
    labels=np.arange(n,dtype=np.int64)
    for x in range(256):
        selected=labels[labels!=x]
        # For nonzero h, solve v=x+h/(u+x). Both orientations are counted.
        hs=np.arange(1,256,dtype=np.int64)
        partners=x ^ table[hs[:,None],inverse[selected^x][None,:]]
        count=np.sum(members[partners] & (partners!=selected[None,:]),axis=1)
        assert np.all(count%2==0)
        for value,multiplicity in zip(*np.unique(count//2,return_counts=True)):
            if value:histogram[str(int(value))]=histogram.get(str(int(value)),0)+int(multiplicity)
    for total in range(1,256):
        count=int(np.sum(members[labels^total]))
        assert count%2==0
        if count:histogram[str(count//2)]=histogram.get(str(count//2),0)+1
    assert histogram==model['subfield_histogram']
    sub_union=sum(histogram.values())
    U=sub_union+comb(n,2)*(q-256)
    assert U==model['U']
    N=q*q+q+1-n;O=N-U;m=n-3;D=U-3*(q-1);Z=(q-1)*U-3*O
    assert (O,D,Z)==(model['O'],model['D'],model['Z']) and min(O,D,Z)>0
    high=Fraction(model['high_density']);low=Fraction(model['low_density'])
    assert high==Fraction(D+m,(q-1)*Z) and low==Fraction(D,(q-1)*Z)
    assert U*high+O*low==1 and Fraction(model['delta'])==m*low
    embedding=params['embed']
    assert model['dictionary']==[[1,embedding[i],embedding[int(table[i,i])]] for i in range(n)]
    assert model['labels']==embedding[:n] and len(set(model['labels']))==n
    products={}
    for i in range(n):
        for j in range(i+1,n):products.setdefault(str(i^j),set()).add(int(table[i,j]))
    assert model['products_by_sum']=={key:sorted(values) for key,values in products.items()}
    theorem=BASE/'revisions/general_arc_2026-11-03_r5/GENERAL_THEOREM.md'
    assert model['proof_source_sha256']==hashlib.sha256(theorem.read_bytes()).hexdigest()
    return {'verified':True,'kind':'R5_THEOREM_INSTANCE','n':n,'delta':model['delta'],
            'independent_point_count':sub_union,'verification_ns':time.monotonic_ns()-started,
            'scope':'conditional on the manually proved r5 theorem, not sampler attestation'}


def verify_t2(model):
    # The probability LP uses integer field cardinality. Field applicability is
    # separately justified for the canonical frame in SECURITY_PROOFS.md.
    q=model['q'];r=model['r'];Q=q-1;T=q*q+q-3
    assert q==1<<128 and model['n']==5 and model['d']==model['k']==4 and r in (2,3)
    assert model['field_bits']==128 and model['modulus']==(1<<128)|0x87
    assert model['dictionary']==[[int(i==j) for j in range(4)] for i in range(4)]+[[1]*4]
    Z=3*q**4+3*q**3-4*q*q-7*q+3 if r==2 else 2*q**3+2*q*q+2*q-3
    low=Fraction(3 if r==2 else 2,Z)
    high=low*(1+Fraction(T,6*Q*Q)) if r==2 else low*(1+Fraction(1,4*Q))
    assert model['low_density']==str(low) and model['high_density']==str(high)
    assert Fraction(model['delta'])==(T*low if r==2 else low)
    path=BASE/'revisions/final_closure_2026-11-04/verify_dual.py'
    spec=importlib.util.spec_from_file_location('archived_independent_checker',path)
    checker=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    sizes,categories,edges=checker.independent_counts(q,r)
    certificate=model['paired_certificate']
    assert certificate['left_sizes']==sizes and certificate['right_categories']==categories
    x={key:Fraction(value) for key,value in certificate['primal']['x'].items()}
    y={key:Fraction(value) for key,value in certificate['primal']['y'].items()}
    assert set(x)==set(sizes) and set(y)==set(categories)
    assert sum(x.values())==sum(y.values())==1 and min([*x.values(),*y.values()])>=0
    alpha=Fraction(certificate['dual']['alpha']);beta=Fraction(certificate['dual']['beta'])
    left={key:Fraction(0) for key in x};right={key:Fraction(0) for key in y}
    supplied={(e['left'],e['right']):e for e in certificate['edges']}
    assert len(supplied)==len(certificate['edges']) and set(supplied)==set(edges)
    overlap=Fraction(0)
    for (label,category),(f,g,count,degree) in edges.items():
        edge=supplied[label,category]
        assert Fraction(edge['f'])==f and Fraction(edge['g'])==g
        h,u,v=[Fraction(edge[key]) for key in ['h','u','v']]
        assert min(h,u,v,f*x[label]-h,g*y[category]-h,u+v-1)>=0
        assert u*(f*x[label]-h)==v*(g*y[category]-h)==h*(u+v-1)==0
        overlap+=h;left[label]+=f*u;right[category]+=g*v
    assert all(alpha>=left[key] and x[key]*(alpha-left[key])==0 for key in x)
    assert all(beta>=right[key] and y[key]*(beta-right[key])==0 for key in y)
    assert overlap==alpha+beta and 1-overlap==Fraction(model['delta'])
    assert Fraction(certificate['delta'])==Fraction(model['delta'])
    assert Fraction(certificate['primal_overlap'])==Fraction(certificate['dual_overlap'])==overlap
    for label in sizes:
        assert Fraction(certificate['primal']['kernel_densities'][label])==x[label]/sizes[label]
    for category,data in categories.items():
        assert Fraction(certificate['primal']['simulator_densities'][category])==y[category]/(data['size']*data['orbits'])
    return {'verified':True,'kind':'T2_CANONICAL_FRAME_CONDITIONAL_EXTENSION','n':5,'r':r,
            'delta':model['delta'],'primal_dual_gap':'0','scope':'manual characteristic-independence proof plus independent exact paired certificate check'}


if __name__=='__main__':
    params=json.loads((ROOT/'public/aes_parameters.json').read_text())
    report={'field':check_field_and_embedding(params),'models':[]}
    for path in sorted((ROOT/'public').glob('model_*.json')):
        model=json.loads(path.read_text())
        entry=verify_r5(model,params) if model['variant']=='r5' else verify_t2(model)
        entry['model_sha256']=hashlib.sha256(json.dumps(model,sort_keys=True).encode()).hexdigest()
        report['models'].append(entry)
    (ROOT/'public/MODEL_VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({'field_verified':True,'models_verified':len(report['models'])}))
