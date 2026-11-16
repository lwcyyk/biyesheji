"""Symbolic identities in the hand proof, not a formal proof of group reductions."""
from pathlib import Path
import argparse,json
import sympy as s


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args()
    here=Path(__file__).resolve().parent;out=(here/args.out).resolve();assert out.is_relative_to(here);out.mkdir(parents=True,exist_ok=False)
    q,a,E=s.symbols('q a E');T=q*q-3;k=q-2;A=k/(q-1);L=A/T;h=1/T;z=E-k*a
    u=(1-(q-1)**2*(a+z))/(3*(q-1));uniform=q*(q-2)/((q-1)**2*(q*q+q-3))
    identities={
      'probability_normalizes':(2*q-3)*h+q*(q-1)*L-1,
      'high_low_balance':(q-2)*(h-L)-L,
      'mixed_rank_lower_algebra':3*k*(u-z)-(A-(q*q-4)*E+k*(q*q-q-3)*a),
      'lower_bound_crossing':(A-(q*q-5)*L)/2-L,
      'uniform_gap':uniform-L-(q-2)*(q-3)/((q-1)**2*(q*q+q-3)*(q*q-3)),
      'relative_gap':(uniform-L)/uniform-(q-3)/(q*(q*q-3))}
    records=[]
    for name,value in identities.items():
        reduced=s.cancel(value);assert reduced==0;records.append({'identity':name,'expected':'0','actual':str(reduced)})
    report={'pass':True,'identities':records,'scope':'rational identities only; geometric/counting and simulation reductions remain hand proofs'}
    (out/'checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))


if __name__=='__main__':main()
