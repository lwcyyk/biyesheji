"""Computed boundary counterexamples, separate from symbolic arguments."""
from collections import Counter
from fractions import Fraction
from itertools import product
from pathlib import Path
import argparse
import json


def tv(a,b):
    return sum(abs(Fraction(a[x],sum(a.values()))-Fraction(b[x],sum(b.values()))) for x in a.keys()|b.keys())/2


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
    base=Path(__file__).resolve().parent;out=(base/args.out).resolve();assert out.is_relative_to(base)
    out.mkdir(parents=True,exist_ok=False);records=[]
    same0=Counter((rho,rho) for rho in (1,2));same1=Counter((rho,2*rho%3) for rho in (1,2))
    assert tv(same0,same1)==1
    records.append({'case':'same_mask_reuse','actual_TV':str(tv(same0,same1)),'expected_TV':'1',
                    'world0_counts':sorted(same0.items()),'world1_counts':sorted(same1.items())})
    laws=[Counter((a*rho*col)%3 for rho in (1,2)) for col in (1,1,2) for a in (1,2)]
    assert all(law==laws[0] for law in laws)
    records.append({'case':'singleton_family_not_all_independent','actual_max_TV':'0','rank1_full_family_formula_not_applicable':'1/2'})
    labels=[(1,0),(0,1),(1,1),(1,2)]
    available=[m for m in product(range(3),repeat=2) if all(sum(a*b for a,b in zip(m,v))%3 for v in labels)]
    assert not available
    records.append({'case':'complete_projective_line_no_legal_mask','actual_legal_masks':available,'expected_legal_masks':[]})
    (out/'checks.json').write_text(json.dumps(records,indent=2))
    summary={'pass':True,'computed_boundaries':len(records),'general_proof':False}
    (out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))


if __name__=='__main__':main()
