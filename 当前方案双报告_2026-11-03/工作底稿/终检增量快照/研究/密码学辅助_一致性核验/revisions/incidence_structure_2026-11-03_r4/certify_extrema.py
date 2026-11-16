"""Exact (not floating-point) endpoint witnesses for the actual GF16 examples."""
from pathlib import Path
import argparse,json
from incidence import PERFECT
from analytic_certificate import construct


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args()
    here=Path(__file__).resolve().parent;out=(here/args.out).resolve();assert out.is_relative_to(here);out.mkdir(parents=True,exist_ok=False)
    results=[]
    for label,C in [('min',()),('max',PERFECT)]:
        cert=construct(16,C);name=f'q16_{label}.json';(out/name).write_text(json.dumps(cert,indent=2))
        results.append({'file':name,'t':len(C),'exact_optimum':cert['exact_optimum']})
    (out/'summary.json').write_text(json.dumps(results,indent=2));print(json.dumps(results))


if __name__=='__main__':main()
