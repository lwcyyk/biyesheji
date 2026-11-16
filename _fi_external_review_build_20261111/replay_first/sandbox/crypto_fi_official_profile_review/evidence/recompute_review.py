"""Independent deterministic scalar reconstruction; no cryptographic sampling.

Configurations transcribed from the primary tables and erratum. Author code is
never imported. Fractions and integer cross products carry all decisions.
"""
from pathlib import Path
import os
from fractions import Fraction as F
from collections import Counter
from bisect import bisect_left
from decimal import Decimal, localcontext
import hashlib, json, math, struct, sys, time
sys.stdout.reconfigure(encoding='utf-8',line_buffering=True)
sys.set_int_max_str_digits(2000000)
ROOT=Path(__file__).resolve().parents[1]; E=ROOT/'evidence'; Q=65536; D=16
SOURCE=Path(os.environ['FRODO_FI_SANDBOX'])/'crypto_fi_official_profile_correctness/OFFICIAL_PROFILE_CERTIFICATES.json'
AUTHOR=json.loads(SOURCE.read_text(encoding='utf-8'))
CHECKS=[]
def ck(tag,b):
 if not b: raise AssertionError(tag)
 CHECKS.append(tag)
def enc(x):
 x=F(x); return {'numerator':str(x.numerator),'denominator':str(x.denominator)}
def rd(v): return F(int(v['numerator']),int(v['denominator']))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ceilbits(x,bits):
 num,rem=divmod(x.numerator*(1<<bits),x.denominator)
 return F(num+(rem>0),1<<bits)
def floorbits(x,bits): return F((x.numerator*(1<<bits))//x.denominator,1<<bits)
def expup(x):
 # Horner evaluation of the degree-24 positive Taylor polynomial.
 v=F(1)
 for j in range(24,0,-1): v=1+x*v/j
 return ceilbits(1/v,64)
def exp_interval(x):
 # A second analytic certificate: alternating exp(-y), then interval squaring.
 m=0; y=x
 while y>F(1,16): y/=2; m+=1
 term=F(1); partial=F(1); low=F(0); high=F(1)
 for j in range(1,34):
  term*=-y/j; partial+=term
  if j==32: high=partial
  if j==33: low=partial
 low=floorbits(low,192); high=ceilbits(high,192)
 for _ in range(m):
  low=floorbits(low*low,192); high=ceilbits(high*high,192)
 return low,high
def dyad_check(tag,x,y,bits):
 ck(tag,x<=y and y-x<F(1,1<<bits) and (y*(1<<bits)).denominator==1)
def power_exponent(num,den):
 e=den.bit_length()-num.bit_length()
 ok=lambda k:(num<<k)<=den if k>=0 else num<=(den<<-k)
 while not ok(e): e-=1
 while ok(e+1): e+=1
 return e
def binary_record(num,den):
 e=power_exponent(num,den)
 return dict(exponent=e,next_exponent_fails=True,numerator_bits=num.bit_length(),denominator_bits=den.bit_length(),
  numerator_binary_sha256=hashlib.sha256(num.to_bytes((num.bit_length()+7)//8,'big')).hexdigest(),
  denominator_binary_sha256=hashlib.sha256(den.to_bytes((den.bit_length()+7)//8,'big')).hexdigest())
def tail(tag,g,z,n,h,target,author):
 num=g.numerator**n*z.denominator**h; den=g.denominator**n*z.numerator**h
 rec=binary_record(num,den); ck(tag+'/target',rec['exponent']>=target)
 for k in rec: ck(tag+'/'+k,rec[k]==author[k])
 return rec
def decimal(x):
 with localcontext() as c:
  c.prec=70; return str(Decimal(x.numerator)/Decimal(x.denominator))
def labelled(x): return dict(exact=enc(x),decimal=decimal(x))
CONFIG={
 976:dict(cdf=[5638,15915,23689,28571,31116,32217,32613,32731,32760,32766,32767],
  table=[11278,10277,7774,4882,2545,1101,396,118,29,6,1],B=3,h=1477,z=F(33,40),r=3669,zr=F(123,128),hu=7339,zi=F(107,100),initial_exponent=199),
 1344:dict(cdf=[9142,23462,30338,32361,32725,32765,32767],
  table=[18286,14320,6876,2023,364,40,2],B=4,h=1644,z=F(9,10),r=2030,zr=F(59,64),hu=10205,zi=F(59,50),initial_exponent=252)}
POP=[0]*Q
for a in range(1,Q): POP[a]=POP[a>>1]+(a&1)

def one(n,c):
 t0=time.perf_counter(); ap=AUTHOR['profiles'][str(n)]; prefix=str(n); s=len(c['cdf'])-1; pi=F(1,2**c['B']); half=Q//2**(c['B']+1)
 counts=Counter()
 for word in range(Q):
  a=bisect_left(c['cdf'][:-1],word>>1)
  counts[a*(-1 if word&1 else 1)]+=1
 W=dict(sorted(counts.items()))
 ck(prefix+'/all-input-words-normalization',sum(W.values())==Q)
 ck(prefix+'/cdf-vs-official-mass-table',[W[i] for i in range(s+1)]==c['table'])
 ck(prefix+'/author-signed-mass',W=={int(k):v for k,v in ap['distribution']['signed_mass'].items()})
 ck(prefix+'/support-symmetry',set(W)==set(range(-s,s+1)) and all(W[x]==W[-x] for x in W))
 ck(prefix+'/unique-max-atom',[x for x in W if W[x]==max(W.values())]==[0])
 even=sum(v for x,v in W.items() if x%2==0); odd=Q-even; theta=F(even-odd,Q)
 v=sum(F(w*x*x,Q) for x,w in W.items()); fourth=sum(F(w*x**4,Q) for x,w in W.items())
 for k,x in [('variance',v),('fourth_moment',fourth),('psi_at_nyquist',theta),('max_atom',F(W[0],Q))]:
  ck(prefix+'/'+k,rd(ap['distribution'][k])==x)
 ck(prefix+'/actual-parity',even==ap['distribution']['even_numerator'] and odd==ap['distribution']['odd_numerator'])
 nu=Counter(); product=Counter()
 for x,wx in W.items():
  for y,wy in W.items(): nu[x-y]+=wx*wy; product[x*y]+=wx*wy
 ck(prefix+'/entire-difference-law',dict(sorted(nu.items()))=={int(k):m for k,m in ap['difference_law']['mass'].items()})
 ck(prefix+'/difference-normalization',sum(nu.values())==Q*Q and all(nu[d]==nu[-d] for d in nu))
 ck(prefix+'/difference-parity',sum(m for d,m in nu.items() if d%2==0)==even**2+odd**2)
 # All labels and all residues, using a circular distance membership test.
 for label in range(1<<c['B']):
  for e in range(Q):
   cy=((label*(Q>>c['B'])+e)&(Q-1))
   labelout=((cy+(Q>>(c['B']+1)))>>(D-c['B']))&((1<<c['B'])-1)
   ck_result=((e+half)&(Q-1))<2*half
   if (labelout==label)!=ck_result: raise AssertionError((n,label,e))
 ck(prefix+'/decode-all-labels-all-residues',True)
 # All translations are retained in the coverage map; one exact comparison per vector.
 started=time.perf_counter(); vectors={}; ids=[]; records=[]; stream=hashlib.sha256()
 z=c['z']; a=z.numerator; b=z.denominator; scale=[a**j*b**(D-j) for j in range(D+1)]
 for shift in range(Q):
  mass=[0]*(D+1)
  for x,wx in W.items(): mass[POP[(shift+x)&(Q-1)]]+=wx
  key=tuple(mass)
  if key not in vectors:
   rid=len(records); vectors[key]=rid
   records.append(dict(id=rid,first_shift=shift,shift_count=0,weight_mass=mass,
      pgf_common_numerator=str(sum(mass[j]*scale[j] for j in range(D+1)))))
  rid=vectors[key]; records[rid]['shift_count']+=1; ids.append(rid)
  stream.update(records[rid]['pgf_common_numerator'].encode('ascii')+b'\n')
 best=max(int(r['pgf_common_numerator']) for r in records)
 winners=[shift for shift,rid in enumerate(ids) if int(records[rid]['pgf_common_numerator'])==best]
 for rec in records:
  gap=best-int(rec['pgf_common_numerator']); rec['gap_to_max_numerator']=str(gap)
  ck(prefix+'/PGF-representative-'+str(rec['id']),gap>=0 and sum(rec['weight_mass'])==Q)
 ck(prefix+'/full-shift-coverage',len(ids)==Q and sum(r['shift_count'] for r in records)==Q and set(ids)==set(range(len(records))))
 mp=E/f'PGF_SHIFT_TO_REP_{n}.u16le'; mp.write_bytes(struct.pack('<'+'H'*Q,*ids))
 ck(prefix+'/map-roundtrip',list(struct.unpack('<'+'H'*Q,mp.read_bytes()))==ids)
 pgfdoc=dict(profile=n,q=Q,D=D,tilt=enc(z),common_denominator=str(Q*b**D),
  map_path=str(mp),map_format='65536 little-endian unsigned16 representative ids; entry offset=2*shift',
  map_sha256=sha(mp),translations=Q,representatives=len(records),maximizing_shifts=winners,
  maximum_common_numerator=str(best),all_shift_numerator_ascii_sha256=stream.hexdigest(),representative_records=records)
 dump(E/f'PGF_FULL_COVERAGE_{n}.json',pgfdoc)
 gh=F(best,Q*b**D); ha=ap['environment']['fixed_A_H']
 ck(prefix+'/PGF-author-match',gh==rd(ha['g']) and winners==ha['maximizing_shifts'] and stream.hexdigest()==ha['all_numerators_ascii_line_sha256'])
 ck(prefix+'/PGF-max-vector',records[ids[winners[0]]]['weight_mass']==ha['witness_weight_mass'])
 ck(prefix+'/PGF-unique-translation',winners==[4 if n==976 else 2])
 htime=time.perf_counter()-started
 ht=tail(prefix+'/H-tail-inclusive',gh,z,n,c['h'],40,ha['tail_certificate'])
 gr=sum(F(wx,Q)*c['zr']**(x*x) for x,wx in W.items())
 rt=tail(prefix+'/R2-tail-inclusive',gr,c['zr'],n,c['r'],40,ap['environment']['R2']['tail_certificate'])
 gu=F(19,20); zu=F(9,10)
 ut=tail(prefix+'/uniform-H-tail',gu,zu,n*D,c['hu'],40,ap['environment']['uniform_H']['conditional_tail_certificate'])
 unit=F(even,Q)**n
 ck(prefix+'/unit-exact',unit==rd(ap['environment']['uniform_H']['all_u_even_probability']))
 unit_exp=power_exponent(unit.numerator,unit.denominator)
 ck(prefix+'/unit-binary',unit_exp==(976 if n==976 else 1343))
 K={}; domains={}
 for j in [128,64,32,16]:
  pos=1-2*F(22,7)**2*v/j**2
  curvature=2*F(157,50)**2*v-F(2,3)*F(22,7)**4*fourth/j**2
  K[j]=curvature.numerator//curvature.denominator
  ck(prefix+'/psi-positive-curvature-'+str(j),pos>0 and K[j]>0 and curvature>=K[j])
  ck(prefix+'/psi-author-'+str(j),rd(ap['analytic_psi']['domains'][str(j)]['positive_lower'])==pos and ap['analytic_psi']['domains'][str(j)]['K']==K[j])
  domains[str(j)]=dict(positive_lower=enc(pos),curvature=enc(curvature),K=K[j])
 zi=c['zi']; ga=sum(F(wx,Q)*zi**x for x,wx in W.items()); gb=sum(F(wx,Q*Q)*zi**x for x,wx in product.items())
 ck(prefix+'/initial-PGF-exact',ga==rd(ap['initial']['chi_PGF']) and gb==rd(ap['initial']['product_PGF']))
 num=2*ga.numerator*gb.numerator**(2*n)*zi.denominator**half
 den=ga.denominator*gb.denominator**(2*n)*zi.numerator**half
 ini=binary_record(num,den)
 for k in ini: ck(prefix+'/initial-tail-'+k,ini[k]==ap['initial']['coordinate_tail_certificate'][k])
 ck(prefix+'/initial-coordinate-exponent',ini['exponent']==c['initial_exponent'])
 alpha=F(64,1<<ini['exponent']); ck(prefix+'/initial-full-union',alpha==rd(ap['initial']['full_failure_upper']))
 modes={}
 for mode,h,delta in [('fixed_A',c['h'],F(1,2**39)),('uniform_Setup',c['hu'],F(1,2**38))]:
  tag=f'{n}/{mode}'; author=ap[mode]
  budget=F(1,2**ht['exponent'])+F(1,2**rt['exponent']) if mode=='fixed_A' else F(1,2**ut['exponent'])+F(1,2**rt['exponent'])+unit
  ck(tag+'/bad-environment-budget',budget<=delta)
  groups=[]
  # Fixed primary-derived ranges, rather than reading the author group list.
  lowranges=([(1,2,128),(3,5,64),(6,10,32),(11,20,16)] if n==976 else [(1,7,128),(8,14,64),(15,28,32),(29,56,16)])
  midranges=([(21,31,32,6),(32,63,32,3),(64,127,32,1)] if n==976 else [(57,63,32,5),(64,127,32,2)])
  specifications=[(t,t,j,2*s) for lo,hi,j in lowranges for t in range(lo,hi+1)]+midranges
  for lo,hi,j,dmax in specifications:
   ck(tag+f'/domain-{lo}',hi*dmax*s<=Q//j)
   es={}
   for d in range(1,dmax+1):
    x=F(K[j]*(h+c['r'])*lo*lo*d*d,Q*Q); upper=expup(x)
    poly=sum((x**k/F(math.factorial(k)) for k in range(25)),F())
    dyad_check(tag+f'/exp64-{lo}-{d}',1/poly,upper,64)
    el,eu=exp_interval(x); ck(tag+f'/alternative-exp-interval-{lo}-{d}',0<=el<=eu<=upper<=1)
    es[d]=upper
   # Retained and unretained atoms are summed explicitly.
   R=F(nu[0],Q*Q)+sum(2*F(nu[d],Q*Q)*(es[d] if d<=dmax else 1) for d in range(1,2*s+1))
   P=ceilbits(R**n,80); dyad_check(tag+f'/power80-{lo}',R**n,P,80)
   groups.append(dict(range=[lo,hi],count=hi-lo+1,exp_upper={str(d):enc(e) for d,e in es.items()},R_upper=enc(R),R_power_n_up=enc(P)))
  xhigh=min(F(K[32]*h*128**2,Q*Q),F(h,64)*F(W[0]*W[1],Q*Q)); rho=expup(xhigh)
  ck(tag+'/high-exponential-independent-interval',exp_interval(xhigh)[1]<=rho<=1)
  R=1-2*F(nu[1],Q*Q)*(1-rho); P=ceilbits(R**n,80)
  dyad_check(tag+'/high-power80',R**n,P,80)
  groups.append(dict(range=[128,Q//2],count=Q//2-127,adopted_exponent=enc(xhigh),rho=enc(rho),R_upper=enc(R),R_power_n_up=enc(P)))
  coverage=[t for g in groups for t in range(g['range'][0],g['range'][1]+1)]
  ck(tag+'/all-positive-frequency-representatives',coverage==list(range(1,Q//2+1)))
  ck(tag+'/all-nonzero-frequencies',set(coverage+[Q-t for t in coverage])==set(range(1,Q)))
  ck(tag+'/author-group-count',len(groups)==len(author['frequency_groups']))
  for i,(g,ag) in enumerate(zip(groups,author['frequency_groups'])):
   for key in g: ck(tag+f'/author-group-{i}-{key}',g[key]==ag[key])
  Z=2*pi*sum(g['count']*rd(g['R_power_n_up']) for g in groups)
  C=sum(pi**j for j in range(8)); f=pi**8+C*Z
  uraw=(1-delta)*f+delta; ur=(1-delta)*min(F(1),f,pi+Z)+delta
  lr=(1-delta)*max(F(0),pi-Z)**8
  us=(1-delta)*min(F(1),pi+Z)+delta; ls=(1-delta)*max(F(0),pi-Z)
  endpoints=dict(scalar_correct_lower=ls,scalar_correct_upper=us,row_correct_lower=lr,row_correct_upper=ur,full_correct_upper=ur,full_error_lower=1-ur)
  for key,x in endpoints.items(): ck(tag+'/'+key,rd(author[key])==x)
  ck(tag+'/Z',Z==rd(author['Z'])); ck(tag+'/C',C==rd(author['C']))
  cond=dict(scalar_correct_lower=max(F(0),(ls-alpha)/(1-alpha)),scalar_correct_upper=min(F(1),us/(1-alpha)),
   row_correct_lower=max(F(0),(lr-alpha)/(1-alpha)),row_correct_upper=min(F(1),ur/(1-alpha)),
   full_correct_upper=min(F(1),ur/(1-alpha)),full_error_lower=1-min(F(1),ur/(1-alpha)))
  for key,x in cond.items(): ck(tag+'/conditioned-'+key,rd(author['conditioned_on_initial'][key])==x)
  disp=author['display']; target=F(disp['row_full_upper'])
  ck(tag+'/display-full-upper',ur<=cond['full_correct_upper']<=target)
  ck(tag+'/display-scalar-interval',F(disp['scalar_lower'])<=cond['scalar_correct_lower'] and cond['scalar_correct_upper']<=F(disp['scalar_upper']))
  ck(tag+'/display-row-lower',F(disp['row_lower'])<=cond['row_correct_lower'])
  ck(tag+'/display-error',F(disp['full_error_lower'])==1-target and F(disp['full_error_percent_lower'])==100*(1-target))
  slack=Q*pi*(F(n,2**64)+F(1,2**80)); ck(tag+'/dyadic-loss',slack==rd(author['dyadic_slack_already_in_Z']) and slack<F(1,2**41))
  modes[mode]=dict(Z=labelled(Z),C=enc(C),F=labelled(f),raw_upper=enc(uraw),
   endpoints={key:labelled(x) for key,x in endpoints.items()},
   conditioned_endpoints={key:labelled(x) for key,x in cond.items()},display=disp,
   margin_after_conditioning=labelled(target-cond['full_correct_upper']),adopted_delta=enc(delta),bad_budget=enc(budget),frequency_groups=groups)
 B0=2*n*s*s+s; W=2*n*n*D*s*s+2*n*n*s**3+n*D*s+n*s*s; Wprint=2*(n*n*D*s**3+n*n*s**3)+n*D*s+n*s*s
 ck(prefix+'/theorem63-left',Wprint==ap['printed_theorem63']['left_hand_side'])
 ck(prefix+'/theorem63-frontier',Wprint>half and Wprint-W>=B0)
 print(n,'PASS; shifts',Q,'representatives',len(records),'maximum',winners,'initial2^-',ini['exponent'])
 return dict(parameters=ap['parameters'],distribution=dict(cdf=c['cdf'],signed_frequency=W,variance=enc(v),fourth_moment=enc(fourth),
  even_numerator=even,odd_numerator=odd,theta=enc(theta),difference_mass=dict(sorted(nu.items())),difference_denominator=Q*Q),
  H=dict(g=enc(gh),maximizing_shifts=winners,maximizing_weight_mass=records[ids[winners[0]]]['weight_mass'],
   representatives=len(records),translations=Q,enumeration_seconds=htime,inclusive_tail_certificate=ht),
  R2=dict(g=enc(gr),inclusive_tail_certificate=rt),uniform_H=dict(tail=ut,unit_probability=enc(unit),unit_exponent=unit_exp),
  psi_domains=domains,initial=dict(tilt=enc(zi),chi_PGF=enc(ga),product_PGF=enc(gb),product_law=dict(sorted(product.items())),
   coordinate_tail_certificate=ini,full_failure=enc(alpha)),modes=modes,
  theorem63=dict(initial_B0=B0,W=W,W_print=Wprint,half_width=half,surplus=Wprint-W,initial_absorbed_for_integer_T_at_least1=True),
  total_seconds=time.perf_counter()-t0)

START=time.perf_counter(); profiles={str(n):one(n,c) for n,c in CONFIG.items()}
# Independent finite stress checks of the abstract pointwise chord and endpoints.
for k in [1,2,8]:
 for pi in [F(0),F(1,16),F(1,8),F(1,4),F(1)]:
  C=sum(pi**j for j in range(k))
  for b in range(65):
   x=F(b,64); ck(f'abstract-pointwise/{k}/{pi}/{b}',x**k<=pi**k+C*max(F(0),x-pi))
old=json.loads((Path(os.environ['FRODO_FI_SANDBOX'])/'crypto_fi_640_fixed_A_correctness/FINITE_CERTIFICATES.json').read_text(encoding='utf-8'))
pi=F(1,4); C=sum(pi**j for j in range(8)); Z=rd(old['Z']); delta=rd(old['environment']['adopted_delta'])
ck('640-specialization',C==rd(old['chord_slope']) and (1-delta)*(pi**8+C*Z)+delta==rd(old['row_and_full_correct_upper']))
result=dict(schema='fi-profile-targeted-review/recomputed/1',status='PASS',
 identity='Independent formula reconstruction inside the same author-proof-visible Codex review context',
 independence_of_models_or_error_processes=False,source_certificate_sha256=sha(SOURCE),script_sha256=sha(Path(__file__)),
 check_count=len(CHECKS),checks=CHECKS,profiles=profiles,seconds=time.perf_counter()-START,
 all_decisions_exact=True,decimal_strings_for_display_only=True,cryptographic_samples=0,monte_carlo_runs=0,candidate_implementations=0)
dump(E/'INDEPENDENT_RECOMPUTATION.json',result)
print('PASS',len(CHECKS),'named comparisons;',result['seconds'],'seconds')
