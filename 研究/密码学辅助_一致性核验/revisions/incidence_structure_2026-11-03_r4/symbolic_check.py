"""Check identities and polynomial positivity reductions in the written proof."""
from pathlib import Path
import argparse,json
import sympy as S


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args()
    here=Path(__file__).resolve().parent;out=(here/args.out).resolve();assert out.is_relative_to(here);out.mkdir(parents=True,exist_ok=False)
    q,t,t1,t2,x,u=S.symbols('q t t1 t2 x u');U=15*q-60+t;O=q*q-14*q+55-t;D=U-3*(q-1);Z=(q-1)*U-3*O
    lo=D/((q-1)*Z);hi=(D+3)/((q-1)*Z);delta=3*lo;K=9/Z
    formula=lambda v:3*(12*q-57+v)/((q-1)*(12*q*q+(v-33)*q+2*v-105))
    identities={
      'primal_normalization':U*hi+O*lo-1,
      'simulator_normalization':3*(q-1)*hi+(q-1)**2*lo-1,
      'full_orbit_mass_balance':D*(hi-lo)-3*lo,
      'primal_dual_objective':delta-K*(U/(3*(q-1))-1),
      'separation_formula':formula(t2)-formula(t1)-27*(t2-t1)/((q-1)*(12*q*q+(t1-33)*q+2*t1-105)*(12*q*q+(t2-33)*q+2*t2-105)),
      'GF16_minimum':formula(0).subs(q,16)-S.Rational(3,271),
      'GF16_maximum':formula(15).subs(q,16)-S.Rational(10,903),
      'GF16_gap':(formula(15)-formula(0)).subs(q,16)-S.Rational(1,244713)}
    checks=[]
    for name,expr in identities.items():
        value=S.cancel(expr);assert value==0;checks.append({'identity':name,'actual':str(value),'expected':'0'})
    positivity={
      'Z_minus_8q2':S.Poly(S.expand((Z-8*q*q).subs(q,x+13)),x,t),
      'outside_lower':S.Poly(S.expand(O.subs({q:x+13,t:15-u})),x,u)}
    positive=[]
    for name,poly in positivity.items():
        assert all(c>=0 for c in poly.coeffs());positive.append({'name':name,'polynomial':str(poly.as_expr()),'nonnegative_variables':str(poly.gens)})
    report={'pass':True,'identities':checks,'positive_coefficient_bounds':positive,'scope':'symbolic algebra only, not a formalized security proof'}
    (out/'checks.json').write_text(json.dumps(report,indent=2));print(json.dumps({'pass':True,'identities':len(checks),'positivity_bounds':len(positive)}))


if __name__=='__main__':main()
