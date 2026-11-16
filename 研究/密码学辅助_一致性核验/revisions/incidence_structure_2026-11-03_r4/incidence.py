"""Prime-field geometric reference; pure integer arithmetic, no LP imports."""
from collections import Counter
from itertools import combinations, permutations, product


EDGES=tuple(combinations(range(6),2))
MATCHINGS={k:tuple(T for T in combinations(EDGES,k) if len({i for e in T for i in e})==2*k) for k in (1,2,3)}
PERFECT=MATCHINGS[3]


def normalize(v,q):
    a=next(x%q for x in v if x%q);t=pow(a,q-2,q)
    return tuple(x*t%q for x in v)


def cross(a,b,q):
    return ((a[1]*b[2]-a[2]*b[1])%q,(a[2]*b[0]-a[0]*b[2])%q,(a[0]*b[1]-a[1]*b[0])%q)


def dot(a,b,q):return sum(x*y for x,y in zip(a,b))%q


def points(q):return sorted({normalize(v,q) for v in product(range(q),repeat=3) if any(v)})


def is_arc(cols,q):
    return all(dot(cols[i],cross(cols[j],cols[k],q),q) for i,j,k in combinations(range(len(cols)),3))


def concurrence(cols,q):
    assert len(cols)==6 and is_arc(cols,q)
    lines={e:cross(cols[e[0]],cols[e[1]],q) for e in EDGES}
    return tuple(T for T in PERFECT if dot(cross(lines[T[0]],lines[T[1]],q),lines[T[2]],q)==0)


def direct_counts(cols,q):
    forbidden={normalize(c,q) for c in cols};lines={e:cross(cols[e[0]],cols[e[1]],q) for e in EDGES};counts=Counter()
    for x in points(q):
        if x in forbidden:continue
        signature=tuple(e for e in EDGES if dot(lines[e],x,q)==0)
        assert len({v for e in signature for v in e})==2*len(signature)
        counts[signature]+=1
    return dict(counts)


def compiled_counts(q,C):
    C=set(C);counts={():q*q-14*q+55-len(C)}
    for (e,) in MATCHINGS[1]:counts[(e,)]=q-7+sum(e in T for T in C)
    for T in MATCHINGS[2]:
        leftover=tuple(i for i in range(6) if i not in {v for e in T for v in e})
        counts[T]=int(tuple(sorted(T+(leftover,))) not in C)
    for T in PERFECT:counts[T]=int(T in C)
    assert all(n>=0 for n in counts.values()),'negative signature count: not a realizability certificate'
    assert sum(counts.values())==q*q+q-5
    return {T:n for T,n in counts.items() if n}


def encode_C(C):return sum(1<<PERFECT.index(T) for T in C)


def relabel_C(C,permutation):
    return tuple(sorted(tuple(sorted(tuple(sorted((permutation[i],permutation[j]))) for i,j in T)) for T in C))


def actions():
    return [(p,tuple(PERFECT.index(relabel_C((T,),p)[0]) for T in PERFECT)) for p in permutations(range(6))]


def canonical_C(C,all_actions):
    indices=[PERFECT.index(T) for T in C];best=None;witness=None
    for p,action in all_actions:
        value=sum(1<<action[i] for i in indices)
        if best is None or value<best:best,witness=value,p
    return best,witness
