"""Symbolic algebra and sufficient-bound checks, separate from general proofs."""
from pathlib import Path
import argparse,json
import sympy as S


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args()
    here=Path(__file__).resolve().parent;out=(here/args.out).resolve();assert out.is_relative_to(here);out.mkdir(parents=True,exist_ok=False)
    n,q,U,U1,U2,w,si,sj,x,y=S.symbols('n q U U1 U2 w si sj x y');m=n-3;N=q*q+q+1-n;O=N-U;D=U-3*(q-1);Z=(q-1)*U-3*O
    E=N-n*q+n*(n-1)/2;s=(q-1)**2;lo=D/((q-1)*Z);hi=(D+m)/((q-1)*Z);delta=m*lo
    f=lambda A:m*(A-3*(q-1))/((q-1)*((q-1)*A-3*(N-A)))
    A=1/(n-4);B=-1/((n-4)*(n-3));C=2/((n-4)*(n-3)*(n-2))
    expressions={
      'primal_normalization':U*hi+O*lo-1,
      'simulator_normalization':3*(q-1)*hi+s*lo-1,
      'external_line_count':s-E-m*(q-n/2),
      'full_orbit_balance':D*(hi-lo)-m*lo,
      'duality_value':delta-(3*m/Z)*(U/(3*(q-1))-1),
      'uniform_gap':m*(s-m)/(N*s)-delta-3*m*m*O/(N*(q-1)**2*Z),
      'representation_gap':f(U2)-f(U1)-3*m*m*(U2-U1)/((q-1)*((q-1)*U1-3*(N-U1))*((q-1)*U2-3*(N-U2))),
      'triangle_right_inverse':A*((n-4)*w+si+sj)+B*((n-3)*(si+sj)+2*U)+C*(n-2)*U-w}
    checks=[]
    for name,expr in expressions.items():
        value=S.cancel(expr);assert value==0;checks.append({'identity':name,'actual':'0','expected':'0'})
    polys={
      'perturbation_bound_n_ge5':(9*n*n-39*n-24).subs(n,x+5),
      'ell_lower':(q/2-1-4*n*(n-2)).subs(q,16*n*n+y).subs(n,x+5),
      'singleton_count':(q/2-1-(n-2)*(n-3)/2).subs(q,16*n*n+y).subs(n,x+5),
      'edge_load_lower':(q/4-1-(n-2)*(n-3)/4).subs(q,16*n*n+y).subs(n,x+5),
      'capacity_strict':(q*q-32*(n-3)).subs(q,16*n*n+y).subs(n,x+5)}
    bounds=[]
    for name,expr in polys.items():
        poly=S.Poly(S.expand(expr),x,y);assert all(c>=0 for c in poly.coeffs()) and poly.eval({x:0,y:0})>0
        bounds.append({'bound':name,'polynomial':str(poly.as_expr()),'variables_nonnegative':['x=n-5','y=q-16n^2']})
    report={'pass':True,'identities':checks,'positive_bounds':bounds,'scope':'symbolic identities, not a proof assistant security development'}
    (out/'checks.json').write_text(json.dumps(report,indent=2));print(json.dumps({'pass':True,'identities':len(checks),'positive_bounds':len(bounds)}))


if __name__=='__main__':main()
