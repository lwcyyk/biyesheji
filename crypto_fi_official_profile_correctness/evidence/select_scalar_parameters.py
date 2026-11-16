"""Deterministic scalar design scan. Float logs select candidates only; no bound certification."""
from pathlib import Path
from fractions import Fraction as F
from math import log, exp, floor
import json
OUT=Path(__file__).resolve().parent
raw=json.loads((OUT.parents[1]/'crypto_fi_research_manuscript_v2_1/evidence/DISTRIBUTION_TABLES.json').read_text(encoding='utf-8'))
ans={}
for key in ('976','1344'):
 p=raw['profiles'][key]; n=int(key); s=p['s']; mass=p['mass_zero_then_each_signed_value']
 w={x:mass[abs(x)] for x in range(-s,s+1)}
 patterns={}
 for a in range(65536):
  v=[0]*17
  for x,m in w.items(): v[((a+x)%65536).bit_count()]+=m
  patterns.setdefault(tuple(v),a)
 def choose_h():
  best=None
  for j in range(1,40):
   z=F(j,40); a,b=z.numerator,z.denominator
   table=[a**k*b**(16-k) for k in range(17)]
   val,pattern=max((sum(m*t for m,t in zip(v,table)),v) for v in patterns)
   g=F(val,65536*b**16)
   h=floor((n*log(float(g))+40*log(2))/log(float(z)))
   row=dict(h=h,z=str(z),g=str(g),shift=patterns[pattern],pattern=pattern)
   if best is None or h>best['h']: best=row
  return best
 def choose_r():
  best=None
  for j in range(1,32):
   z=F(128-j,128); g=sum((F(m,65536)*z**(x*x) for x,m in w.items()),F())
   r=floor((n*log(float(g))+40*log(2))/log(float(z)))
   row=dict(r=r,z=str(z),g=str(g))
   if best is None or r>best['r']: best=row
  return best
 def choose_initial():
  best=None; half=4096 if key=='976' else 2048
  for j in range(1,31):
   z=F(100+j,100); zf=float(z)
   ga=sum(m*zf**x for x,m in w.items())/65536
   gb=sum(mx*my*zf**(x*y) for x,mx in w.items() for y,my in w.items())/65536**2
   exponent=(half*log(zf)-log(2)-log(ga)-2*n*log(gb))/log(2)
   row=dict(z=str(z),estimated_exponent=exponent)
   if best is None or exponent>best['estimated_exponent']: best=row
  return best
 h=choose_h(); r=choose_r(); ini=choose_initial()
 v=sum(F(m*x*x,65536) for x,m in w.items()); m4=sum(F(m*x**4,65536) for x,m in w.items())
 ks={d:2*F(157,50)**2*v-F(2,3)*F(22,7)**4*m4/F(d*d) for d in (16,32)}
 hu=[]
 for j in range(1,40):
  z=F(j,40); g=(1+z)/2
  hu.append((floor((n*16*log(float(g))+40*log(2))/log(float(z))),str(z)))
 ans[key]=dict(pattern_count=len(patterns),H=h,R2=r,initial=ini,variance=str(v),fourth=str(m4),
       K16=floor(ks[16]),K32=floor(ks[32]),uniform_H=dict(zip(('h','z'),max(hu))))
(OUT/'PARAMETER_SELECTION_NONCERTIFYING.json').write_text(json.dumps(ans,indent=2)+'\n',encoding='utf-8')
print(json.dumps(ans,indent=2))
