"""Deterministic finite probability certificates. No keys, ciphertexts or token generation.

Only scalar integer/Fraction arithmetic certifies bounds. Candidate-selection float logs
are excluded from this file. All writes stay inside the new delivery directory.
"""
from fractions import Fraction as F
from pathlib import Path
from math import factorial
import hashlib, json, sys

sys.stdout.reconfigure(encoding='utf-8',line_buffering=True)
sys.set_int_max_str_digits(100000)
ROOT=Path(__file__).resolve().parents[1]
EVID=ROOT/'evidence'
DEN=65536
def enc(x):
 x=F(x); return dict(numerator=str(x.numerator),denominator=str(x.denominator))
def dec(x): return F(int(x['numerator']),int(x['denominator']))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def ih(x): return hashlib.sha256(x.to_bytes((x.bit_length()+7)//8,'big')).hexdigest()
def binary(num,den):
 assert num>0 and den>0
 b=den.bit_length()-num.bit_length()
 def ok(k): return num<<k<=den if k>=0 else num<=den<<(-k)
 while not ok(b): b-=1
 while ok(b+1): b+=1
 return dict(exponent=b,inequality='ratio <= 2^(-exponent)',next_exponent_fails=True,
  numerator_bits=num.bit_length(),denominator_bits=den.bit_length(),
  numerator_binary_sha256=ih(num),denominator_binary_sha256=ih(den))
def tail(g,z,n,h):
 return binary(g.numerator**n*z.denominator**h,g.denominator**n*z.numerator**h)
def up(x,b=64):
 x=F(x); y=F((x.numerator*(1<<b)+x.denominator-1)//x.denominator,1<<b)
 assert x<=y<x+F(1,1<<b); return y
def em(x):
 assert x>=0
 S=sum((x**k/F(factorial(k)) for k in range(25)),F())
 y=up(1/S); assert y*S>=1 and 0<y<=1; return y
def power(x,n):
 assert 0<=x<=1
 return up(x**n,80)
def outward(x,places=9,upper=True):
 x=F(x); sc=10**places
 a=(x.numerator*sc+x.denominator-1)//x.denominator if upper else x.numerator*sc//x.denominator
 r=F(a,sc); assert (r>=x if upper else r<=x)
 return f'{a//sc}.{a%sc:0{places}d}'

CDF={976:[5638,15915,23689,28571,31116,32217,32613,32731,32760,32766,32767],
     1344:[9142,23462,30338,32361,32725,32765,32767]}
CHOICES={976:dict(B=3,H=1477,zh=F(33,40),R=3669,zr=F(123,128),hu=7339,zu=F(9,10),zi=F(107,100)),
         1344:dict(B=4,H=1644,zh=F(9,10),R=2030,zr=F(59,64),hu=10205,zu=F(9,10),zi=F(59,50))}
old=json.loads((ROOT.parent/'crypto_fi_research_manuscript_v2_1/evidence/DISTRIBUTION_TABLES.json').read_text(encoding='utf-8'))

def build(n):
 c=CHOICES[n]; q=65536; D=16; B=c['B']; cols=rows=8; pi=F(1,2**B); half=q//2**(B+1)
 cdf=CDF[n]; s=len(cdf)-1
 mass=[2*(cdf[0]+1)]+[cdf[i]-cdf[i-1] for i in range(1,s+1)]
 W={x:mass[abs(x)] for x in range(-s,s+1)}
 assert sum(W.values())==DEN and min(W.values())>0
 assert mass==old['profiles'][str(n)]['mass_zero_then_each_signed_value']
 assert cdf==old['profiles'][str(n)]['cdf']
 count={x:0 for x in W}
 for word in range(DEN):
  t=word>>1; a=sum(t>v for v in cdf[:-1]); x=-a if word&1 else a; count[x]+=1
 assert count==W
 ev=sum(m for x,m in W.items() if x%2==0); od=DEN-ev
 theta=F(ev-od,DEN); v=sum((F(m*x*x,DEN) for x,m in W.items()),F())
 m4=sum((F(m*x**4,DEN) for x,m in W.items()),F()); p0=F(W[0],DEN); p1=F(W[1],DEN)
 nu={d:sum(W[x]*W.get(x-d,0) for x in W) for d in range(-2*s,2*s+1)}
 assert sum(nu.values())==DEN**2 and all(nu[d]==nu[-d] for d in nu)
 assert sum(nu[d] for d in nu if d%2==0)==ev**2+od**2
 # Actual integer half-up Decode, every label and residue representative.
 DD={x%q for x in range(-half,half)}
 for label in range(2**B):
  actual={e for e in range(q) if (((((label*(q//2**B)+e)%q)*2**B+q//2)//q)%(2**B))==label}
  assert actual==DD
 assert len(DD)==q//2**B
 print(n,'CDF, moments, parity and all Decode labels PASS')
 # New full bit-weight PGF: every possible parent-coordinate translation.
 a,b=c['zh'].numerator,c['zh'].denominator
 powers=[a**k*b**(D-k) for k in range(D+1)]
 best=-1; witness=None; ties=[]; stream=hashlib.sha256(); patterns=set()
 for t in range(q):
  weights=[0]*(D+1)
  for x,m in W.items(): weights[((t+x)%q).bit_count()]+=m
  val=sum(x*y for x,y in zip(weights,powers)); patterns.add(tuple(weights))
  stream.update(str(val).encode('ascii')+b'\n')
  if val>best: best=val; witness=weights; ties=[t]
  elif val==best: ties.append(t)
 gh=F(best,DEN*b**D)
 baseline=p0+(1-p0)*c['zh']; assert gh<baseline
 hc=tail(gh,c['zh'],n,c['H']); assert hc['exponent']>=40
 gr=sum((F(m,DEN)*c['zr']**(x*x) for x,m in W.items()),F())
 rc=tail(gr,c['zr'],n,c['R']); assert rc['exponent']>=40
 gu=(1+c['zu'])/2; uc=tail(gu,c['zu'],n*D,c['hu']); assert uc['exponent']>=40
 unit=F(ev,DEN)**n; unit_cert=binary(unit.numerator,unit.denominator)
 if n==976: assert ev==od==32768 and unit_cert['exponent']==976
 else: assert (ev,od)==(32770,32766) and unit_cert['exponent']==1343
 delta_fixed=F(1,2**39); delta_uniform=F(1,2**38)
 assert F(1,2**hc['exponent'])+F(1,2**rc['exponent'])<=delta_fixed
 assert F(1,2**uc['exponent'])+F(1,2**rc['exponent'])+unit<=delta_uniform
 curv={j:2*F(157,50)**2*v-F(2,3)*F(22,7)**4*m4/F(j*j) for j in (16,32,64,128)}
 pos={j:1-2*F(22,7)**2*v/F(j*j) for j in curv}
 K={j:curv[j].numerator//curv[j].denominator for j in curv}
 assert min(pos.values())>0 and min(K.values())>0
 # Exact PGF: one chi plus 2n independent chi-products.
 zi=c['zi']; ga=sum((F(m,DEN)*zi**x for x,m in W.items()),F())
 gb=sum((F(mx*my,DEN**2)*zi**(x*y) for x,mx in W.items() for y,my in W.items()),F())
 ini=binary(2*ga.numerator*gb.numerator**(2*n)*zi.denominator**half,
            ga.denominator*gb.denominator**(2*n)*zi.numerator**half)
 expect=199 if n==976 else 252
 assert ini['exponent']==expect
 alpha=F(rows*cols,2**ini['exponent']); assert 0<alpha<1
 print(n,'H/R/uniform-H exponents',hc['exponent'],rc['exponent'],uc['exponent'],'initial',ini['exponent'])

 def profile_envelope(h,delta,quantifier):
  groups=[]
  def group(name,lo,hi,j,dmax):
   assert hi*dmax*s<=q//j
   es={d:em(F(K[j]*(h+c['R'])*lo*lo*d*d,q*q)) for d in range(1,dmax+1)}
   rr=1-sum((2*F(nu[d],DEN**2)*(1-es[d]) for d in es),F())
   pp=power(rr,n)
   groups.append(dict(name=name,range=[lo,hi],count=hi-lo+1,denominator_of_small_domain=j,
    K=K[j],difference_max=dmax,representative_frequency=lo,
    max_unwrapped_argument=hi*dmax*s,analytic_domain=q//j,
    exp_upper={str(d):enc(x) for d,x in es.items()},R_upper=enc(rr),R_power_n_up=enc(pp)))
  full16=(q//16)//(2*s*s)
  for t in range(1,full16+1):
   j=max(j for j in curv if t*2*s*s<=q//j)
   group('L'+str(t),t,t,j,2*s)
  lo=full16+1
  while lo<128:
   hi=min(127,(1<<lo.bit_length())-1)
   dmax=min(2*s,(q//32)//(hi*s))
   assert dmax>=1
   group('M'+str(lo)+'_'+str(hi),lo,hi,32,dmax)
   lo=hi+1
  xs=F(K[32]*h*128**2,q*q); xg=F(h,64)*p0*p1
  xhigh=min(xs,xg); rho=em(xhigh)
  rh=1-2*F(nu[1],DEN**2)*(1-rho); ph=power(rh,n)
  groups.append(dict(name='H128',range=[128,q//2],count=q//2-127,
   small_exponent_at128=enc(xs),global_exponent=enc(xg),adopted_exponent=enc(xhigh),
   rho=enc(rho),R_upper=enc(rh),R_power_n_up=enc(ph)))
  assert sum(g['count'] for g in groups)==q//2
  assert all(groups[i]['range'][1]+1==groups[i+1]['range'][0] for i in range(len(groups)-1))
  ZZ=2*pi*sum((g['count']*dec(g['R_power_n_up']) for g in groups),F())
  C=sum((pi**j for j in range(cols)),F()); assert C==(1-pi**cols)/(1-pi)
  frow=pi**cols+C*ZZ
  uscalar=(1-delta)*min(1,pi+ZZ)+delta
  lscalar=(1-delta)*max(F(),pi-ZZ)
  urow=(1-delta)*min(1,frow,pi+ZZ)+delta
  lrow=(1-delta)*max(F(),pi-ZZ)**cols
  ucscalar=min(F(1),uscalar/(1-alpha)); ucrow=min(F(1),urow/(1-alpha))
  lcscalar=max(F(),(lscalar-alpha)/(1-alpha))
  lcrow=max(F(),(lrow-alpha)/(1-alpha))
  U=outward(ucrow); E=outward(1-F(U),upper=False)
  slack=F(q,1)*pi*(n*F(1,2**64)+F(1,2**80))
  assert slack<F(1,2**41)
  assert urow<=ucrow<=F(U)<F(1,2)
  return dict(A_quantifier=quantifier,H_min=h,R2_min=c['R'],adopted_delta=enc(delta),
   frequency_groups=groups,positive_representatives=q//2,coverage_complete=True,
   paired_frequency_multiplier=enc(2*pi),nyquist_counted_twice_conservatively=True,
   unused_difference_mass_upper=1,uncharged_truncation_loss=0,Z=enc(ZZ),C=enc(C),
   raw_good_row_chord=enc(frow),scalar_correct_lower=enc(lscalar),scalar_correct_upper=enc(uscalar),
   row_correct_lower=enc(lrow),row_correct_upper=enc(urow),full_correct_upper=enc(urow),
   positive_scalar_row_lower_factorization=dict(base=enc(p0),exponent=3*n),
   full_correct_lower_factorization=dict(base=enc(p0),exponent=3*rows*n),
   full_error_lower=enc(1-urow),
   conditioned_on_initial=dict(scalar_correct_lower=enc(lcscalar),scalar_correct_upper=enc(ucscalar),
     row_correct_lower=enc(lcrow),row_correct_upper=enc(ucrow),full_correct_upper=enc(ucrow),
     full_error_lower=enc(1-ucrow),full_correct_lower_factorization=dict(base=enc(p0),exponent=3*rows*n)),
   display=dict(scalar_lower=outward(lcscalar,upper=False),scalar_upper=outward(ucscalar),
     row_lower=outward(lcrow,places=15,upper=False),row_full_upper=U,full_error_lower=E,
     full_error_percent_lower=outward(100*F(E),places=7,upper=False)),
   dyadic_slack_already_in_Z=enc(slack),verdict='CERTIFIED_HIGH_ERROR')

 fixed=profile_envelope(c['H'],delta_fixed,'EVERY_PRE_FIXED_A')
 uniform=profile_envelope(c['hu'],delta_uniform,'UNIFORM_FULL_MATRIX_SETUP_AVERAGE_ONLY')
 print(n,'fixed Z/U',float(dec(fixed['Z'])),fixed['display'])
 print(n,'uniform Z/U',float(dec(uniform['Z'])),uniform['display'])
 return dict(parameters=dict(n=n,D=D,q=q,mbar=rows,nbar=cols,B=B,message_bits=B*rows*cols,
       support_radius=s,decode_half_width=half,pi0=enc(pi)),
  distribution=dict(source='Official 2021 Table3; 2023 A.3/A.4 plus issue35 erratum for1344',
       cdf=cdf,denominator=DEN,mass_zero_then_each_sign=mass,
       signed_mass={str(x):m for x,m in W.items()},sum_numerators=sum(W.values()),
       support=[-s,s],symmetric=True,sampler_all_65536_words_match=True,
       even_numerator=ev,odd_numerator=od,max_atom=enc(p0),unique_maximizer=0,
       variance=enc(v),fourth_moment=enc(m4),psi_at_nyquist=enc(theta)),
  difference_law=dict(denominator=DEN**2,mass={str(d):nu[d] for d in nu},
       nu1=enc(F(nu[1],DEN**2)),even_numerator=ev**2+od**2,odd_numerator=2*ev*od),
  decode=dict(rule='floor(c*2^B/q+1/2) mod2^B',correct_integer_interval=[-half,half-1],
       cardinality=len(DD),all_labels_all_residues_checked=2**B*q,pi0=enc(pi)),
  environment=dict(fixed_A_H=dict(method='maximal translated full bit-weight PGF',z=enc(c['zh']),
       g=enc(gh),g_numerator_common_denominator=str(best),common_denominator=str(DEN*b**D),
       maximizing_shifts=ties,witness_weight_mass=witness,translations_enumerated=q,
       distinct_weight_patterns=len(patterns),all_numerators_ascii_line_sha256=stream.hexdigest(),
       nonzero_only_PGF=enc(baseline),strictly_improves_nonzero_PGF=True,
       threshold=c['H'],tail_certificate=hc),
     R2=dict(z=enc(c['zr']),g=enc(gr),threshold=c['R'],tail_certificate=rc),
     uniform_H=dict(z=enc(c['zu']),g_per_bit=enc(gu),number_fair_bits=n*D,
       threshold=c['hu'],conditional_tail_certificate=uc,
       all_u_even_probability=enc(unit),all_u_even_certificate=unit_cert)),
  analytic_psi=dict(pi_lower='157/50',pi_upper='22/7',
       domains={str(j):dict(radius=q//j,positive_lower=enc(pos[j]),curvature_lower=enc(curv[j]),K=K[j]) for j in curv},
       global_bound_squared='1 - 8*p0*p1*sin(pi*t/q)^2',
       global_exponent_per_H_draw='p0*p1/64 for |t|>=q/32',
       aperiodicity_witness='positive atoms0 and1; d=+/-1 retained at high frequencies'),
  initial=dict(tilt=enc(zi),chi_PGF=enc(ga),product_PGF=enc(gb),product_power=2*n,
       coordinate_tail_certificate=ini,coordinate_failure_upper=enc(F(1,2**ini['exponent'])),
       full_failure_upper=enc(alpha),full_failure_power_of_two=ini['exponent']-6,
       PGF_identity='A_chi(z)*B_chi(z)^(2n)',quantifier='EVERY_PRE_FIXED_A'),
  printed_theorem63=dict(T=1,left_hand_side=2*(n*n*D*s**3+n*n*s**3)+n*D*s+n*s*s,
       right_hand_side=half,sufficient_premise_holds=False),
  fixed_A=fixed,uniform_Setup=uniform)

result=dict(schema='fi-official-profile-correctness/1',date_asia_shanghai='2026-11-11',
 identity='INFORMED_PARAMETRIC_PROBABILITY_RESEARCH_AND_DETERMINISTIC_FINITE_CERTIFICATE_CHECK',
 arithmetic='Exact integers/Fraction; positive Taylor reciprocal degree24; upward dyadics64 then80 bits',
 candidate_mechanisms_implemented=0,cryptographic_samples=0,monte_carlo_runs=0,
 source_distribution_audit_sha256=sha(ROOT.parent/'crypto_fi_research_manuscript_v2_1/evidence/DISTRIBUTION_TABLES.json'),
 script_sha256=sha(Path(__file__)),profiles={str(n):build(n) for n in (976,1344)},
 new_independent_reviews=0,new_human_reviews=0,new_subagents=0,new_proof_assistant_checks=0)
(ROOT/'OFFICIAL_PROFILE_CERTIFICATES.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Wrote OFFICIAL_PROFILE_CERTIFICATES.json')
