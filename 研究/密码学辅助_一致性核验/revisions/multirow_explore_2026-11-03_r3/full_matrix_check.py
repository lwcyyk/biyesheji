"""Full matrix/output distribution check, independent of the optimization LP."""
from collections import Counter,defaultdict
from fractions import Fraction
from itertools import combinations,product
from pathlib import Path
import argparse
import json
from kernel_minimax import Field,projectivize


def dot(f,a,b):
    z=0
    for x,y in zip(a,b):z=f.add(z,f.mul(x,y))
    return z


def kernel(f,m):
    a,b=m
    z=(f.add(f.mul(a[1],b[2]),f.neg(f.mul(a[2],b[1]))),
       f.add(f.mul(a[2],b[0]),f.neg(f.mul(a[0],b[2]))),
       f.add(f.mul(a[0],b[1]),f.neg(f.mul(a[1],b[0]))))
    if not any(z):return None
    z=projectivize(f,z);assert all(dot(f,row,z)==0 for row in m)
    return z


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
    here=Path(__file__).resolve().parent;out=(here/args.out).resolve();assert out.is_relative_to(here);out.mkdir(parents=True,exist_ok=False)
    results=[]
    for f in (Field(3),Field(2,2,[1,1])):
        cols=[(1,0,0),(0,1,0),(0,0,1),(1,1,1)];T=f.q*f.q-3
        high=Fraction(1,T);low=Fraction(f.q-2,(f.q-1)*T);gl=(f.q*f.q-1)*(f.q*f.q-f.q)
        all_rank2=[];candidate=[];kernel_counts=Counter()
        for entries in product(range(f.q),repeat=6):
            m=(entries[:3],entries[3:]);k=kernel(f,m)
            if k is None:continue
            all_rank2.append((m,k));kernel_counts[k]+=1
            if k in cols:continue
            weight=high if k[1]==0 or k[0]==k[2] else low
            assert all(any(dot(f,row,c) for row in m) for c in cols)
            candidate.append((m,weight/gl))
        assert set(kernel_counts.values())=={gl}
        assert sum(w for _,w in candidate)==1
        max_tv=Fraction(0);count=0;basis_details=[]
        for S in combinations(range(4),3):
            # Derive the simulator by averaging observed kernel orbit densities.
            mass=defaultdict(Fraction);orbit_points=defaultdict(set)
            for m,w in candidate:
                y=tuple(tuple(dot(f,row,cols[i]) for i in S) for row in m);k=kernel(f,y)
                mask=sum(1<<j for j,x in enumerate(k) if x);mass[mask]+=w
            for _,k in all_rank2:orbit_points[sum(1<<j for j,x in enumerate(k) if x)].add(k)
            simulator={}
            for m,k in all_rank2:
                pattern=sum(1<<j for j,x in enumerate(k) if x)
                simulator[tuple(m[0]+m[1])]=mass[pattern]/len(orbit_points[pattern])/gl
            assert sum(simulator.values())==1
            tvs=[]
            for amplitudes in product(range(1,f.q),repeat=3):
                observed=defaultdict(Fraction)
                for m,w in candidate:
                    y=tuple(f.mul(amplitudes[j],dot(f,row,cols[i])) for row in m for j,i in enumerate(S));observed[y]+=w
                distance=sum(abs(observed.get(y,0)-simulator.get(y,0)) for y in observed.keys()|simulator.keys())/2
                assert distance==low,(f.q,S,amplitudes,distance,low)
                max_tv=max(max_tv,distance);tvs.append(str(distance));count+=1
            basis_details.append({'support':S,'amplitude_cases':len(tvs),'TV_values':sorted(set(tvs))})
        results.append({'q':f.q,'all_rank2_matrices':len(all_rank2),'candidate_matrices':len(candidate),
                        'all_legal_columns_retained':True,'distribution_comparisons':count,'max_TV':str(max_tv),
                        'expected_TV':str(low),'basis_details':basis_details})
    (out/'raw.json').write_text(json.dumps(results,indent=2));summary={'pass':True,'fields':len(results),'comparisons':sum(x['distribution_comparisons'] for x in results)}
    (out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps({'summary':summary,'results':results}))


if __name__=='__main__':main()
