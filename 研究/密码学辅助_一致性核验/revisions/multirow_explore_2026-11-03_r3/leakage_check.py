"""The sampling class bit is input-independent but not harmless to privacy."""
from collections import defaultdict
from fractions import Fraction
from itertools import product
from pathlib import Path
import argparse,json
from full_matrix_check import Field,kernel


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args()
    here=Path(__file__).resolve().parent;out=(here/args.out).resolve();assert out.is_relative_to(here);out.mkdir(parents=True,exist_ok=False)
    records=[]
    for f in (Field(3),Field(2,2,[1,1])):
        T=f.q*f.q-3;hi=Fraction(1,T);lo=Fraction(f.q-2,(f.q-1)*T);gl=(f.q*f.q-1)*(f.q*f.q-f.q)
        forbidden={(1,0,0),(0,1,0),(0,0,1),(1,1,1)};samples=[];simulator={}
        for values in product(range(f.q),repeat=6):
            m=(values[:3],values[3:]);k=kernel(f,m)
            if k is None:continue
            pattern=sum(1<<i for i,v in enumerate(k) if v)
            if pattern==5:simulator[(1,values)]=hi/gl
            elif pattern in (3,6,7):simulator[(0,values)]=lo/gl
            if k in forbidden:continue
            bit=int(k[1]==0 or k[0]==k[2]);samples.append((values,bit,(hi if bit else lo)/gl))
        assert sum(simulator.values())==sum(w for _,_,w in samples)==1
        distances=[]
        for amps in product(range(1,f.q),repeat=3):
            observed=defaultdict(Fraction)
            for values,bit,w in samples:
                y=tuple(f.mul(v,amps[i%3]) for i,v in enumerate(values));observed[(bit,y)]+=w
            delta=sum(abs(observed.get(y,0)-simulator.get(y,0)) for y in observed.keys()|simulator.keys())/2
            assert delta==Fraction(f.q-2,T);distances.append(str(delta))
        records.append({'q':f.q,'without_class_bit':str(lo),'with_class_bit_to_declared_simulator':distances[0],
                        'amplitudes':len(distances),'factor':str(Fraction(f.q-2,T)/lo),
                        'optimality_of_joint_simulator':'hand orbit-capacity argument, not established by this check alone'})
    (out/'raw.json').write_text(json.dumps(records,indent=2));print(json.dumps({'pass':True,'results':records}))


if __name__=='__main__':main()
