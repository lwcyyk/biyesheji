"""Probe outside the proven large-field range; any result is kept as such."""
from fractions import Fraction as F
from pathlib import Path
import argparse,json,sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'multirow_explore_2026-11-03_r3'))
from kernel_minimax import Field,solve
from general_incidence import compile_arc,extension_counts


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args()
    out=(HERE/args.out).resolve();assert out.is_relative_to(HERE);out.mkdir(parents=True,exist_ok=False);records=[]
    for n,q in ((6,5),(7,11),(8,11),(8,13),(10,13)):
        cols=[(1,a,a*a%q) for a in range(min(n,q))]
        if n==q+1:cols.append((0,0,1))
        assert len(cols)==n
        compiled=compile_arc(cols,q);counts,U,O=extension_counts(compiled,q)
        D=U-3*(q-1);Z=(q-1)*U-3*O;formula=F((n-3)*D,(q-1)*Z)
        result=solve(Field(q),cols);actual=F(result['exact_achieved_radius'])
        records.append({'n':n,'q':q,'proven_range':q>=16*n*n,'U':U,'outside':O,'two_density_upper_bound':str(formula),
                        'exact_feasible_radius':str(actual),'strict_counterexample_to_unrestricted_formula':actual<formula,
                        'reference_result':result})
    (out/'raw.json').write_text(json.dumps(records,indent=2))
    summary={'cases':len(records),'counterexamples':[{'n':r['n'],'q':r['q'],'candidate':r['exact_feasible_radius'],'formula':r['two_density_upper_bound']} for r in records if r['strict_counterexample_to_unrestricted_formula']],
             'absence_of_counterexample_is_not_a_proof':True}
    (out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))


if __name__=='__main__':main()
