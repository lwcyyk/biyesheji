"""Check whether representations of the same uniform matroid separate."""
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import argparse
import json
from kernel_minimax import Field,solve,geometry


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args()
    root=Path(__file__).resolve().parent;out=(root/args.out).resolve();assert out.is_relative_to(root);out.mkdir(parents=True,exist_ok=False)
    f=Field(3,2,[1,0]);records=[]
    for a,b in combinations(range(2,9),2):
        cols=[(0,0,1)]+[(1,t,f.mul(t,t)) for t in (0,1,a,b)]
        points,allowed,bases=geometry(f,cols);assert len(bases)==10
        row=solve(f,cols);row['labels']=['infinity',0,1,a,b];records.append(row)
    (out/'raw.json').write_text(json.dumps(records,indent=2))
    groups={}
    for row in records:groups.setdefault(row['exact_achieved_radius'],[]).append(row['labels'])
    summary={'pass':True,'q':9,'matroid':'U_3_5','rank_exactly':2,'representations':len(records),
             'achieved_radii_and_numeric_optima':groups,'representation_separation_certified':False}
    (out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))


if __name__=='__main__':main()
