"""Public prime-field arc incidence compiler; no secret data or MPC."""
from collections import defaultdict
from fractions import Fraction as F
from itertools import combinations


def dot(a,b,q):return sum(x*y for x,y in zip(a,b))%q
def cross(a,b,q):return ((a[1]*b[2]-a[2]*b[1])%q,(a[2]*b[0]-a[0]*b[2])%q,(a[0]*b[1]-a[1]*b[0])%q)
def norm(x,q):
    z=next(v%q for v in x if v%q);inverse=pow(z,q-2,q)
    return tuple(v*inverse%q for v in x)


def compile_arc(columns,base_q):
    n=len(columns);edges=list(combinations(range(n),2));lines={e:cross(columns[e[0]],columns[e[1]],base_q) for e in edges}
    assert all(dot(columns[i],cross(columns[j],columns[k],base_q),base_q) for i,j,k in combinations(range(n),3))
    incidence=defaultdict(set)
    for e,f in combinations(edges,2):
        if set(e)&set(f):continue
        point=norm(cross(lines[e],lines[f],base_q),base_q);incidence[point].update((e,f))
    multis=[]
    for point,signature in sorted(incidence.items()):
        signature=tuple(sorted(signature));assert len({v for e in signature for v in e})==2*len(signature)
        assert all(dot(lines[e],point,base_q)==0 for e in signature)
        multis.append({'point':point,'edges':signature})
    return {'base_q':base_q,'columns':columns,'n':n,'multisecant_points':multis,
            'pair_intersections':3*len(list(combinations(range(n),4))),
            'overlap_correction':sum(len(x['edges'])-1 for x in multis)}


def extension_counts(compiled,q):
    n=compiled['n'];edges=list(combinations(range(n),2));signatures={tuple(tuple(e) for e in x['edges']):1 for x in compiled['multisecant_points']}
    for e in edges:signatures[(e,)]=q-1-sum(e in T for T in signatures if len(T)>=2)
    U=sum(signatures.values());N=q*q+q+1-n;O=N-U
    if O:signatures[()]=O
    assert O>=0 and all(c>=0 for c in signatures.values())
    assert U==len(edges)*(q-1)-compiled['overlap_correction']
    return {T:c for T,c in signatures.items() if c},U,O


def weights(compiled,q):
    n=compiled['n'];edges=list(combinations(range(n),2));counts,U,O=extension_counts(compiled,q)
    W={e:sum(F(c,len(T)) for T,c in counts.items() if e in T) for e in edges}
    vertex={i:sum(W[e] for e in edges if i in e) for i in range(n)}
    ell={B:(sum(W[e] for e in combinations(B,2))-sum(vertex[i] for i in B)/F(n-3)+F(2*U,(n-3)*(n-2)))/F(n-4) for B in combinations(range(n),3)}
    assert sum(W.values())==U and sum(ell.values())==F(U,3)
    for e in edges:assert sum(v for B,v in ell.items() if set(e)<=set(B))==W[e]
    return counts,U,O,W,ell
