"""Public ten-column best/worst incidence witnesses over GF(2^15).

On-the-fly binary arithmetic avoids allocating a q-by-q multiplication table.
The fixed RNG is for public witness discovery only, never privacy evidence.
"""
from collections import defaultdict
from itertools import combinations
from pathlib import Path
import argparse,json,random
from compact_certificate import construct

BITS=15;Q=1<<BITS;MODULUS=(1<<BITS)|3


def mul(a,b):
    z=0
    while b:
        if b&1:z^=a
        b>>=1;a<<=1
        if a&Q:a^=MODULUS
    return z


def power(a,k):
    z=1
    while k:
        if k&1:z=mul(z,a)
        a=mul(a,a);k>>=1
    return z


def remainder(a,b):
    while a.bit_length()>=b.bit_length():a^=b<<(a.bit_length()-b.bit_length())
    return a


def gcd(a,b):
    while b:a,b=b,remainder(a,b)
    return a


def check_field():
    x=2
    for _ in range(15):x=mul(x,x)
    assert x==2
    for k in (3,5):
        x=2
        for _ in range(15//k):x=mul(x,x)
        assert gcd(x^2,MODULUS)==1


def cross(a,b):return (mul(a[1],b[2])^mul(a[2],b[1]),mul(a[2],b[0])^mul(a[0],b[2]),mul(a[0],b[1])^mul(a[1],b[0]))
def dot(a,b):return mul(a[0],b[0])^mul(a[1],b[1])^mul(a[2],b[2])
def arc(cols):return all(dot(cols[i],cross(cols[j],cols[k])) for i,j,k in combinations(range(len(cols)),3))
def norm(v):
    inv=power(next(x for x in v if x),Q-2)
    return tuple(mul(x,inv) for x in v)


def compile_binary(cols):
    assert arc(cols);n=len(cols);edges=list(combinations(range(n),2));lines={e:cross(cols[e[0]],cols[e[1]]) for e in edges};points=defaultdict(set)
    for e,f in combinations(edges,2):
        if set(e)&set(f):continue
        p=norm(cross(lines[e],lines[f]));points[p].update((e,f))
    multis=[]
    for p,T in sorted(points.items()):
        T=tuple(sorted(T));assert len({i for e in T for i in e})==2*len(T)
        multis.append({'point':p,'edges':T})
    return {'base_q':Q,'field_polynomial':MODULUS,'columns':cols,'n':n,'multisecant_points':multis,
            'pair_intersections':3*len(list(combinations(range(n),4))),
            'overlap_correction':sum(len(x['edges'])-1 for x in multis)}


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args()
    here=Path(__file__).resolve().parent;out=(here/args.out).resolve();assert out.is_relative_to(here);out.mkdir(parents=True,exist_ok=False)
    check_field();rng=random.Random(5161103);attempts=0
    while attempts<100:
        attempts+=1;cols=[(1,rng.randrange(Q),rng.randrange(Q)) for _ in range(10)]
        if not arc(cols):continue
        best=compile_binary(cols)
        if all(len(x['edges'])==2 for x in best['multisecant_points']):break
    else:raise AssertionError('no witness found within public search budget')
    generator=next(power(a,(Q-1)//7) for a in range(2,256) if power(a,(Q-1)//7)!=1)
    beta=next(power(generator,k) for k in range(1,7) if power(power(generator,k),3)^power(generator,k)^1==0)
    subfield=[]
    for code in range(8):
        value=0
        for j in range(3):
            if (code>>j)&1:value^=power(beta,j)
        subfield.append(value)
    assert len(set(subfield))==8 and all(power(x,8)==x for x in subfield)
    max_cols=[(1,a,mul(a,a)) for a in subfield]+[(0,0,1),(0,1,0)]
    worst=compile_binary(max_cols);assert len(worst['multisecant_points'])==63
    assert all(len(x['edges'])==5 for x in worst['multisecant_points'])
    records=[]
    for name,profile,expected in [('best',best,0),('worst',worst,378)]:
        T=sum((len(x['edges'])-1)*(len(x['edges'])-2)//2 for x in profile['multisecant_points']);assert T==expected
        cert=construct(profile,Q);(out/(name+'_certificate.json')).write_text(json.dumps(cert,indent=2))
        records.append({'kind':name,'q':Q,'n':10,'field_polynomial':MODULUS,'columns':profile['columns'],
                        'multisecant_points':len(profile['multisecant_points']),'T':T,'J':profile['overlap_correction'],'exact_value':cert['exact_value']})
    summary={'pass':True,'field_irreducibility':'Rabin criterion verified','public_search_attempts':attempts,
             'GF8_generator_image':beta,'records':records,'scope':'public geometric witnesses and analytic certificates, not MPC'}
    (out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))


if __name__=='__main__':main()
