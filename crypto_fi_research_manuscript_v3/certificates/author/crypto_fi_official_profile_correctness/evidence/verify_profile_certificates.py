"""Read-only checking of the finite certificate and historical-input immutability.

This is certificate checking in the same informed AI context, not an independent review.
"""
from pathlib import Path
from fractions import Fraction as F
from math import factorial
import hashlib, json, sys
sys.stdout.reconfigure(encoding='utf-8',line_buffering=True)
sys.set_int_max_str_digits(100000)
ROOT=Path(__file__).resolve().parents[1]; E=ROOT/'evidence'
checks=[]
def check(name,truth):
 if not truth: raise AssertionError(name)
 checks.append(name)
def rd(x): return F(int(x['numerator']),int(x['denominator']))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def binary_check(tag,num,den,c):
 k=c['exponent']
 valid=lambda b: (num<<b)<=den if b>=0 else num<=(den<<(-b))
 check(tag+'/power-of-two',valid(k) and not valid(k+1))
 check(tag+'/integer-bit-lengths',(num.bit_length(),den.bit_length())==(c['numerator_bits'],c['denominator_bits']))
 for label,value in [('numerator',num),('denominator',den)]:
  check(tag+'/'+label+'-hash',hashlib.sha256(value.to_bytes((value.bit_length()+7)//8,'big')).hexdigest()==c[label+'_binary_sha256'])
def tail_check(tag,g,z,n,h,c):
 binary_check(tag,g.numerator**n*z.denominator**h,g.denominator**n*z.numerator**h,c)
def exp_check(tag,x,y):
 S=sum((x**k/F(factorial(k)) for k in range(25)),F())
 check(tag+'/directed-exponential',y*S>=1 and (y-F(1,2**64))*S<1 and 0<y<=1)

cert=json.loads((ROOT/'OFFICIAL_PROFILE_CERTIFICATES.json').read_text(encoding='utf-8'))
check('script-binding',cert['script_sha256']==sha(E/'compute_profile_certificates.py'))
for item in json.loads((E/'INPUT_SNAPSHOT.json').read_text(encoding='utf-8')):
 p=Path(item['path']); check('historical-read-only/'+p.parent.name+'/'+p.name,sha(p)==item['sha256'] and p.stat().st_size==item['bytes'])
for item in json.loads((E/'SOURCE_PAGES.json').read_text(encoding='utf-8')):
 check('source-byte-binding/'+item['tag']+'/'+str(item['page']),sha(Path(item['path']))==item['sha256'])
for key,p in cert['profiles'].items():
 n=int(key); par=p['parameters']; q=par['q']; s=par['support_radius']; pi=rd(par['pi0']); B=par['B']
 W={int(x):m for x,m in p['distribution']['signed_mass'].items()}; cdf=p['distribution']['cdf']; en=p['environment']
 check(key+'/CDF-derived-zero',W[0]==2*(cdf[0]+1))
 check(key+'/CDF-derived-positive',all(W[x]==cdf[x]-cdf[x-1] for x in range(1,s+1)))
 check(key+'/normalization-symmetry-support',sum(W.values())==65536 and all(W[x]==W[-x]>0 for x in range(-s,s+1)))
 v=sum((F(m*x*x,65536) for x,m in W.items()),F()); m4=sum((F(m*x**4,65536) for x,m in W.items()),F())
 check(key+'/exact-moments',v==rd(p['distribution']['variance']) and m4==rd(p['distribution']['fourth_moment']))
 ev=sum(m for x,m in W.items() if x%2==0); od=65536-ev
 check(key+'/parity',(ev,od)==(p['distribution']['even_numerator'],p['distribution']['odd_numerator']))
 nu={d:sum(mx*W.get(x-d,0) for x,mx in W.items()) for d in range(-2*s,2*s+1)}
 check(key+'/entire-difference-law',{str(d):m for d,m in nu.items()}==p['difference_law']['mass'] and sum(nu.values())==65536**2)
 check(key+'/decode-cardinality',p['decode']['cardinality']==q//2**B and pi==F(1,2**B))
 half=par['decode_half_width']
 for label in range(2**B):
  for r in range(q):
   got=((((label*(q//2**B)+r)%q)*2**B+q//2)//q)%(2**B)
   expected=(r<half or r>=q-half)
   if (got==label)!=expected: raise AssertionError((key,label,r))
 check(key+'/decode-all-labels-all-residues',True)
 hh=en['fixed_A_H']; zh=rd(hh['z']); common=65536*zh.denominator**16
 stream=hashlib.sha256(); maxval=-1; ties=[]
 for a in range(q):
  value=sum(m*zh.numerator**((a+x)%q).bit_count()*zh.denominator**(16-((a+x)%q).bit_count()) for x,m in W.items())
  stream.update(str(value).encode('ascii')+b'\n')
  if value>maxval: maxval=value; ties=[a]
  elif value==maxval: ties.append(a)
 gh=F(maxval,common)
 check(key+'/all-translations-H-PGF',gh==rd(hh['g']) and stream.hexdigest()==hh['all_numerators_ascii_line_sha256'] and ties==hh['maximizing_shifts'])
 check(key+'/new-H-strict-improvement',gh<rd(hh['nonzero_only_PGF']))
 tail_check(key+'/H-tail',gh,zh,n,hh['threshold'],hh['tail_certificate'])
 rr=en['R2']; zr=rd(rr['z']); gr=sum((F(m,65536)*zr**(x*x) for x,m in W.items()),F())
 check(key+'/R2-PGF',gr==rd(rr['g']))
 tail_check(key+'/R2-tail',gr,zr,n,rr['threshold'],rr['tail_certificate'])
 uu=en['uniform_H']; zu=rd(uu['z']); gu=(1+zu)/2
 tail_check(key+'/uniform-H-tail',gu,zu,n*16,uu['threshold'],uu['conditional_tail_certificate'])
 unit=F(ev,65536)**n; check(key+'/actual-biased-unit-event',unit==rd(uu['all_u_even_probability']))
 binary_check(key+'/unit-event',unit.numerator,unit.denominator,uu['all_u_even_certificate'])
 for j,dom in p['analytic_psi']['domains'].items():
  j=int(j)
  cp=2*F(157,50)**2*v-F(2,3)*F(22,7)**4*m4/(j*j)
  positive=1-2*F(22,7)**2*v/(j*j)
  check(key+'/psi-domain-'+str(j),cp==rd(dom['curvature_lower']) and cp>=dom['K']>0 and positive==rd(dom['positive_lower'])>0)
 ini=p['initial']; z=rd(ini['tilt'])
 ga=sum((F(m,65536)*z**x for x,m in W.items()),F())
 gb=sum((F(mx*my,65536**2)*z**(x*y) for x,mx in W.items() for y,my in W.items()),F())
 check(key+'/initial-full-PGF',ga==rd(ini['chi_PGF']) and gb==rd(ini['product_PGF']))
 binary_check(key+'/initial-tail',2*ga.numerator*gb.numerator**(2*n)*z.denominator**half,
    ga.denominator*gb.denominator**(2*n)*z.numerator**half,ini['coordinate_tail_certificate'])
 alpha=rd(ini['full_failure_upper'])
 check(key+'/initial-64-union',alpha==64*rd(ini['coordinate_failure_upper']) and alpha<1)
 for mode in ('fixed_A','uniform_Setup'):
  e=p[mode]; h=e['H_min']; r=e['R2_min']; delta=rd(e['adopted_delta']); groups=e['frequency_groups']; last=0; zz=F()
  htail=F(1,2**hh['tail_certificate']['exponent']) if mode=='fixed_A' else F(1,2**uu['conditional_tail_certificate']['exponent'])+unit
  check(key+'/'+mode+'/bad-probability',htail+F(1,2**rr['tail_certificate']['exponent'])<=delta)
  for g in groups:
   tag=key+'/'+mode+'/'+g['name']; lo,hi=g['range']
   check(tag+'/coverage',lo==last+1 and g['count']==hi-lo+1); last=hi
   if 'difference_max' in g:
    dmax=g['difference_max']; j=g['denominator_of_small_domain']; K=g['K']
    check(tag+'/unwrapped-domain',hi*dmax*s<=q//j and K==p['analytic_psi']['domains'][str(j)]['K'])
    es={int(d):rd(y) for d,y in g['exp_upper'].items()}
    check(tag+'/difference-mass-kept',set(es)==set(range(1,dmax+1)))
    for d,y in es.items(): exp_check(tag+'/'+str(d),F(K*(h+r)*lo*lo*d*d,q*q),y)
    R=1-sum((2*F(nu[d],65536**2)*(1-y) for d,y in es.items()),F())
   else:
    K=p['analytic_psi']['domains']['32']['K']; p0=F(W[0],65536); p1=F(W[1],65536)
    exponent=min(F(K*h*lo*lo,q*q),F(h,64)*p0*p1); rho=rd(g['rho'])
    check(tag+'/high-frequency-exponent',exponent==rd(g['adopted_exponent']))
    exp_check(tag,exponent,rho)
    R=1-2*F(nu[1],65536**2)*(1-rho)
   P=rd(g['R_power_n_up'])
   check(tag+'/mixture',R==rd(g['R_upper']) and 0<=R<=1)
   check(tag+'/directed-nth-power',R**n<=P<R**n+F(1,2**80))
   zz+=2*pi*g['count']*P
  check(key+'/'+mode+'/whole-spectrum-and-Z',last==q//2 and zz==rd(e['Z']))
  C=sum((pi**j for j in range(8)),F()); raw=pi**8+C*zz
  up=(1-delta)*min(F(1),raw,pi+zz)+delta
  low=(1-delta)*max(F(),pi-zz)**8
  scalarup=(1-delta)*min(F(1),pi+zz)+delta
  scalarlow=(1-delta)*max(F(),pi-zz)
  check(key+'/'+mode+'/parameterized-moment',C==rd(e['C']) and up==rd(e['row_correct_upper']) and low==rd(e['row_correct_lower']))
  check(key+'/'+mode+'/scalar',scalarup==rd(e['scalar_correct_upper']) and scalarlow==rd(e['scalar_correct_lower']))
  co=e['conditioned_on_initial']; disp=e['display']
  check(key+'/'+mode+'/conditioning',rd(co['row_correct_upper'])==up/(1-alpha) and rd(co['row_correct_lower'])==max(F(),(low-alpha)/(1-alpha)))
  check(key+'/'+mode+'/display-upper',F(disp['row_full_upper'])>=up/(1-alpha) and F(disp['scalar_upper'])>=scalarup/(1-alpha))
  check(key+'/'+mode+'/display-lower',F(disp['row_lower'])<=rd(co['row_correct_lower']) and F(disp['scalar_lower'])<=rd(co['scalar_correct_lower']))
  check(key+'/'+mode+'/display-error',F(disp['full_error_lower'])==1-F(disp['row_full_upper']) and F(disp['full_error_percent_lower'])==100*F(disp['full_error_lower']))
  check(key+'/'+mode+'/high-error',up/(1-alpha)<F(1,2))
 print('Verified profile',key)

# Direct specialization of the abstract formula to the sealed640 certificate.
old=json.loads((ROOT.parent/'crypto_fi_640_fixed_A_correctness/FINITE_CERTIFICATES.json').read_text(encoding='utf-8'))
z=rd(old['Z']); delta=rd(old['environment']['adopted_delta']); pi=F(1,4)
chord=sum(pi**j for j in range(8))
check('640-specialization-C',chord==rd(old['chord_slope']))
check('640-specialization-U',(1-delta)*(pi**8+chord*z)+delta==rd(old['row_and_full_correct_upper']))

out=dict(schema='fi-official-profile-certificate-check/1',status='PASS',check_count=len(checks),
 scope='Read-only deterministic scalar certificate check in same informed AI context',
 certificate_sha256=sha(ROOT/'OFFICIAL_PROFILE_CERTIFICATES.json'),script_sha256=sha(Path(__file__)),
 historical_inputs_unchanged=True,new_independent_reviews=0,checks=checks)
(E/'CERTIFICATE_CHECK.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS',len(checks),'certificate comparisons')
