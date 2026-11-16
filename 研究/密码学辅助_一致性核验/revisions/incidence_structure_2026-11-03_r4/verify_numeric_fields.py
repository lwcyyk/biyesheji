"""Uncompressed GF16 reference cross-check, not the source of the formula."""
from pathlib import Path
from fractions import Fraction as F
import argparse,json,sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'multirow_explore_2026-11-03_r3'))
from kernel_minimax import Field,solve


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args()
    out=(HERE/args.out).resolve();assert out.is_relative_to(HERE);out.mkdir(parents=True,exist_ok=False)
    witnesses=json.loads((HERE/'results/extremal01/witnesses.json').read_text());f=Field(2,4,[1,1,0,0]);rows=[]
    for key in ('minimum_t','maximum_t'):
        w=witnesses[key];result=solve(f,w['dictionary_columns']);t=w['t'];q=16
        target=F(3*(12*q-57+t),(q-1)*(12*q*q+(t-33)*q+2*t-105))
        assert F(result['exact_achieved_radius'])==target
        result.update(kind=key,t=t,closed_formula=str(target));rows.append(result)
    (out/'raw.json').write_text(json.dumps(rows,indent=2));print(json.dumps({'pass':True,'results':[{k:r[k] for k in ('kind','t','exact_achieved_radius','closed_formula')} for r in rows]}))


if __name__=='__main__':main()
