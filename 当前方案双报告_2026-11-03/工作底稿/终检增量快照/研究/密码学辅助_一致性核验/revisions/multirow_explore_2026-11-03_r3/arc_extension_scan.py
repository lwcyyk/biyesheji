"""Deterministic negative/positive search, not evidence of absent prior art."""
from itertools import combinations
from pathlib import Path
import argparse,json,random
from kernel_minimax import Field,geometry,solve,inverse


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
    here=Path(__file__).resolve().parent;out=(here/args.out).resolve();assert out.is_relative_to(here);out.mkdir(parents=True,exist_ok=False)
    rows=[]
    for q,limit in ((7,8),(11,4)):
        f=Field(q);frame=[(1,0,0),(0,1,0),(0,0,1),(1,1,1)];points,_,_=geometry(f,frame)
        def arc(cols):return all(inverse(f,[[cols[j][i] for j in s] for i in range(3)]) is not None for s in combinations(range(len(cols)),3))
        extra=[p for p in points if p not in frame and arc(frame+[p])]
        pairs=[(a,b) for a,b in combinations(extra,2) if arc(frame+[a,b])]
        random.Random(2161103+q).shuffle(pairs)
        for a,b in pairs[:limit]:
            cols=frame+[a,b];row=solve(f,cols);row['matroid']='U_3_6';rows.append(row)
    (out/'raw.json').write_text(json.dumps(rows,indent=2))
    groups={}
    for row in rows:groups.setdefault(str(row['q']),{}).setdefault(row['exact_achieved_radius'],0);groups[str(row['q'])][row['exact_achieved_radius']]+=1
    summary={'pass':True,'cases':len(rows),'numeric_and_primal_radius_groups':groups,'separation_certified':False}
    (out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))


if __name__=='__main__':main()
