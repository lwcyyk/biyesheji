"""Construct explicit six-arcs attaining t=0 and t=15 over GF16."""
from pathlib import Path
from itertools import combinations
import argparse,importlib.util,json,random

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('readonly_r2_field',HERE.parent/'novelty_search_2026-11-03_r2/frontier_probe.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);Field=mod.Field
EDGES=tuple(combinations(range(6),2))
MATCHINGS=tuple(T for T in combinations(EDGES,3) if len({v for e in T for v in e})==6)


def cross(f,a,b):
    return tuple(f.add(f.mul(a[i],b[j]),f.neg(f.mul(a[j],b[i]))) for i,j in ((1,2),(2,0),(0,1)))


def dot(f,a,b):
    z=0
    for x,y in zip(a,b):z=f.add(z,f.mul(x,y))
    return z


def arc(f,cols):return all(dot(f,cols[i],cross(f,cols[j],cols[k])) for i,j,k in combinations(range(len(cols)),3))


def concurrence(f,cols):
    lines={e:cross(f,cols[e[0]],cols[e[1]]) for e in EDGES}
    return [T for T in MATCHINGS if dot(f,cross(f,lines[T[0]],lines[T[1]]),lines[T[2]])==0]


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args()
    out=(HERE/args.out).resolve();assert out.is_relative_to(HERE);out.mkdir(parents=True,exist_ok=False)
    f=Field(2,4,[1,1,0,0]);frame=[(1,0,0),(0,1,0),(0,0,1),(1,1,1)]
    subfield=[x for x in range(16) if f.power(x,4)==x];assert len(subfield)==4
    alpha=next(x for x in subfield if x not in (0,1));beta=f.mul(alpha,alpha)
    maximum=frame+[(1,alpha,beta),(1,beta,alpha)];assert arc(f,maximum)
    Cmax=concurrence(f,maximum);assert len(Cmax)==15
    points=[(1,a,b) for a in range(16) for b in range(16)]+[(0,1,a) for a in range(16)]+[(0,0,1)]
    extra=[p for p in points if p not in frame and arc(f,frame+[p])]
    pairs=list(combinations(extra,2));random.Random(4161103).shuffle(pairs)
    minimum=None;examined=0
    for a,b in pairs:
        examined+=1;cols=frame+[a,b]
        if arc(f,cols) and not concurrence(f,cols):minimum=cols;break
    assert minimum is not None,'search found no witness; not a nonexistence proof'
    data={'field':'GF(16), binary polynomial x^4+x+1, integer polynomial-basis encoding',
          'minimum_t':{'dictionary_columns':minimum,'t':0},'maximum_t':{'dictionary_columns':maximum,'t':15},
          'search_pairs_examined':examined,'minimum_witness_is_existence_not_exhaustive_search':True,
          'field_extension_statement':'same coordinates embed into GF(16^m), preserving all zero/nonzero determinants',
          'deployment_security_claim':False}
    (out/'witnesses.json').write_text(json.dumps(data,indent=2));print(json.dumps(data))


if __name__=='__main__':main()
