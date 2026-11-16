"""Independent geometric verifier: determinant tests and explicit point lists.

No incidence/compiler/optimizer imports. GF16 multiplication uses shift/reduce,
not the producer's polynomial-coefficient multiplication table.
"""
from collections import Counter
from itertools import combinations,permutations
from pathlib import Path
import argparse,json


def det7(a,b,c):return (a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0]))%7
def arc7(cols):return all(det7(cols[i],cols[j],cols[k]) for i,j,k in combinations(range(len(cols)),3))


def canonical(C,matchings):
    positions={T:i for i,T in enumerate(matchings)};best=None
    for p in permutations(range(6)):
        renamed=[tuple(sorted(tuple(sorted((p[i],p[j]))) for i,j in T)) for T in C]
        code=sum(1<<positions[T] for T in renamed)
        if best is None or code<best:best=code
    return best


def mul16(a,b):
    value=0
    while b:
        if b&1:value^=a
        b>>=1;a<<=1
        if a&16:a^=19
    return value


def dot16(a,b):
    out=0
    for x,y in zip(a,b):out^=mul16(x,y)
    return out


def det16(rows):
    value=0
    for p in permutations(range(3)):
        term=1
        for i in range(3):term=mul16(term,rows[i][p[i]])
        value^=term
    return value


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
    here=Path(__file__).resolve().parent;out=(here/args.out).resolve();assert out.is_relative_to(here);out.mkdir(parents=True,exist_ok=False)
    edges=tuple(combinations(range(6),2));matchings=tuple(T for T in combinations(edges,3) if len({v for e in T for v in e})==6)
    frame=[(1,0,0),(0,1,0),(0,0,1),(1,1,1)]
    P7=[(0,0,1)]+[(0,1,b) for b in range(7)]+[(1,a,b) for a in range(7) for b in range(7)]
    extras=sorted(x for x in P7 if x not in frame and arc7(frame+[x]));assert len(extras)==20
    all_pairs={tuple(sorted((a,b))) for a,b in combinations(extras,2) if arc7(frame+[a,b])}
    rows=json.loads((here/'results/classify02/instances.json').read_text());seen=set();groups=Counter();checks=[]
    for row in rows:
        cols=[tuple(v) for v in row['columns']];pair=tuple(sorted(cols[4:]));assert pair in all_pairs and pair not in seen;seen.add(pair)
        counts=Counter()
        for point in P7:
            if point in cols:continue
            T=tuple(e for e in edges if det7(point,cols[e[0]],cols[e[1]])==0);counts[T]+=1
        C=tuple(sorted(T for T in counts if len(T)==3));assert all(counts[T]==1 for T in C)
        declared=tuple(sorted(tuple(tuple(e) for e in T) for T in row['concurrent_perfect_matchings']));assert C==declared
        code=canonical(C,matchings);assert code==row['canonical_bitmask'];groups[code]+=1
        histogram={str(k):sum(v for T,v in counts.items() if len(T)==k) for k in range(4)};assert histogram==row['signature_histogram']
        checks.append({'extra_pair':pair,'class':code,'t':len(C),'histogram':histogram})
    assert seen==all_pairs and len(all_pairs)==70
    W=json.loads((here/'results/extremal01/witnesses.json').read_text());P16=[(0,0,1)]+[(0,1,b) for b in range(16)]+[(1,a,b) for a in range(16) for b in range(16)]
    witnesses=[]
    for key,expected in [('minimum_t',0),('maximum_t',15)]:
        cols=[tuple(v) for v in W[key]['dictionary_columns']]
        triple_values=[det16([cols[i],cols[j],cols[k]]) for i,j,k in combinations(range(6),3)];assert all(triple_values)
        lines={}
        for e in edges:
            candidates=[ell for ell in P16 if dot16(ell,cols[e[0]])==0 and dot16(ell,cols[e[1]])==0]
            assert len(candidates)==1;lines[e]=candidates[0]
        values=[det16([lines[e] for e in T]) for T in matchings];t=values.count(0);assert t==expected
        witnesses.append({'kind':key,'dictionary_columns':cols,'triple_determinants':triple_values,'matching_determinants':values,'t':t})
    report={'pass':True,'complete_GF7_normalized_pairs':len(seen),'classes':dict(groups),'GF7_checks':checks,
            'GF16_witnesses':witnesses,'scope':'finite geometry only; extension embedding and minimax theorem separate'}
    (out/'checks.json').write_text(json.dumps(report,indent=2));print(json.dumps({'pass':True,'normalized_GF7_cases':len(seen),'classes':dict(groups),'GF16_extreme_t':[x['t'] for x in witnesses]}))


if __name__=='__main__':main()
