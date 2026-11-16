"""Deterministic scalar finite certificates only; no cryptographic sampling."""
from fractions import Fraction as F
from pathlib import Path
from math import factorial
import hashlib
import json
import sys

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
ROOT = Path(__file__).resolve().parents[1]
MASS = [9288,8720,7216,5264,3384,1918,958,422,164,56,17,4,1]
W = {x:MASS[abs(x)] for x in range(-12,13)}
n,q,h0,r0 = 640,32768,450,3500
assert sum(W.values()) == 65536
nu = {d:sum(W[x]*W.get(x-d,0) for x in W) for d in range(-24,25)}
assert sum(nu.values()) == 65536**2
assert all(nu[d] == nu[-d] for d in nu)

def enc(x):
    return {'numerator':str(x.numerator),'denominator':str(x.denominator)}

def digest_int(x):
    return hashlib.sha256(x.to_bytes((x.bit_length()+7)//8,'big')).hexdigest()

def binary_cert(num,den):
    b = den.bit_length()-num.bit_length()
    def ok(k):
        return (num<<k)<=den if k>=0 else num<=(den<<(-k))
    while not ok(b): b-=1
    while ok(b+1): b+=1
    return dict(exponent=b,ratio_le_two_to_minus_exponent=True,
                next_exponent_fails=True,numerator_bits=num.bit_length(),
                denominator_bits=den.bit_length(),numerator_binary_sha256=digest_int(num),
                denominator_binary_sha256=digest_int(den))

def up(x,bits):
    scale=1<<bits
    v=F((x.numerator*scale+x.denominator-1)//x.denominator,scale)
    assert v>=x and v-x<F(1,scale)
    return v

def em(x):
    assert x>=0
    s=sum((x**k/F(factorial(k)) for k in range(25)),F(0))
    v=up(1/s,64)
    assert v*s>=1 and 0<v<=1
    return v

def power(x):
    assert 0<=x<=1
    return up(x**640,80)

p0,p1=F(W[0],65536),F(W[1],65536)
# Uniform in the entire fixed matrix A and the conditioning value u.
zh=F(2,5)
gh=p0+(1-p0)*zh
hn=pow(gh.numerator,n)*pow(zh.denominator,h0)
hd=pow(gh.denominator,n)*pow(zh.numerator,h0)
hc=binary_cert(hn,hd)
assert hc['exponent']>=70
zr=F(31,32)
gr=sum((F(w,65536)*zr**(x*x) for x,w in W.items()),F(0))
rn=pow(gr.numerator,n)*pow(zr.denominator,r0)
rd=pow(gr.denominator,n)*pow(zr.numerator,r0)
rc=binary_cert(rn,rd)
assert rc['exponent']>=27
delta_sum=F(1,2**hc['exponent'])+F(1,2**rc['exponent'])
delta=F(1,2**26)
assert delta_sum<=delta
print('H/R2 tail exponents',hc['exponent'],rc['exponent'])

v=sum((F(w*x*x,65536) for x,w in W.items()),F(0))
m4=sum((F(w*x**4,65536) for x,w in W.items()),F(0))
curv={s:2*F(157,50)**2*v-F(2,3)*F(22,7)**4*m4/F(s*s) for s in (16,32)}
pos={s:1-2*F(22,7)**2*v/F(s*s) for s in (16,32)}
assert curv[32]>=144 and curv[16]>=108 and min(pos.values())>0

groups=[]
for name,lo,hi,K,t,dmax in [
    ('L1',1,1,144,1,24),('L23',2,3,144,2,24),
    ('L47',4,7,108,4,24),('M815',8,15,144,8,4),
    ('M1663',16,63,144,16,1)]:
    table={d:em(F(K*(h0+r0)*t*t*d*d,q*q)) for d in range(dmax+1)}
    R=1-sum((2*F(nu[d],65536**2)*(1-table[d]) for d in range(1,dmax+1)),F(0))
    P=power(R)
    domain=1024 if K==144 else 2048
    assert hi*dmax*12<=domain
    groups.append(dict(name=name,range=[lo,hi],count=hi-lo+1,K=K,
                       representative_frequency=t,difference_max=dmax,
                       largest_unwrapped_argument=hi*dmax*12,analytic_domain=domain,
                       exp_upper={str(d):enc(z) for d,z in table.items()},
                       R=enc(R),R_power640_up=enc(P)))
    print(name,'R',float(R),'power',float(P))

# High frequencies: no unproved coefficient-size or no-wrap assumptions.
xs=F(144*h0*64**2,q*q)
xg=F(h0,64)*p0*p1
assert xs>=xg>0
rho=em(xg)
Rh=1-2*F(nu[1],65536**2)*(1-rho)
Ph=power(Rh)
groups.append(dict(name='H64',range=[64,q//2],count=q//2-63,
                   R=enc(Rh),R_power640_up=enc(Ph),rho=enc(rho),
                   small_exponent_at64=enc(xs),global_exponent=enc(xg)))
print('H64','rho',float(rho),'R',float(Rh),'power',float(Ph))
assert sum(g['count'] for g in groups)==q//2
assert groups[0]['range'][0]==1 and groups[-1]['range'][1]==q//2
assert all(groups[i]['range'][1]+1==groups[i+1]['range'][0] for i in range(len(groups)-1))
read=lambda x:F(int(x['numerator']),int(x['denominator']))
Z=F(1,2)*sum((g['count']*read(g['R_power640_up']) for g in groups),F(0))
C8=F(21845,16384)
Fgood=F(1,4**8)+C8*Z
U=(1-delta)*Fgood+delta
L=((1-delta)*(F(1,4)-Z))**8
init_fail=F(1,2**132)
Uc=U/(1-init_fail)
Lc=(L-init_fail)/(1-init_fail)
print('Z',float(Z),'Fgood',float(Fgood),'U',float(U),'L',float(L))
assert 0<Z<F(1,4) and 0<L<U<F(1,4)
# Final outward endpoints are bound by exact integer comparison.
upper_display=F((Uc.numerator*10**9+Uc.denominator-1)//Uc.denominator,10**9)
lower_display=F((Lc.numerator*10**10)//Lc.denominator,10**10)
assert U<=upper_display and Uc<=upper_display<F(1,4)
assert 0<lower_display<=L and lower_display<=Lc
# Here the H64 group also uses a64-bit exponential enclosure. Charge all
# 16384 representatives; the old uniform-Setup49-bit subtotal excluded it.
rounding_extra=F(q,4)*(640*F(1,2**64)+F(1,2**80))
assert rounding_extra<F(1,2**41)

# Replay the A-free initial product-noise Chernoff comparison.
z=F(21,20)
gchi=sum((F(w,65536)*z**x for x,w in W.items()),F(0))
gprod=sum((F(wx*wy,65536**2)*z**(x*y) for x,wx in W.items() for y,wy in W.items()),F(0))
inn=2*gchi.numerator*pow(gprod.numerator,1280)*pow(z.denominator,4096)
ind=gchi.denominator*pow(gprod.denominator,1280)*pow(z.numerator,4096)
ic=binary_cert(inn,ind)
assert ic['exponent']>=138
print('Initial coordinate failure exponent',ic['exponent'])

def decimal_exact(x,places):
    scale=10**places
    v=x*scale
    assert v.denominator==1
    return f'{v.numerator//scale}.{v.numerator%scale:0{places}d}'

out=dict(schema='fi640-fixed-A/finite-certificates/1',date_asia_shanghai='2026-11-10',
    arithmetic='Exact integers and Fraction; 64/80-bit directed upward dyadics',
    scope='Scalar finite laws, analytic envelopes, and deterministic integer comparisons; no cryptographic sampling',
    parameters=dict(n=n,q=q,D=15,h0=h0,R2_min=r0),
    chi=dict(denominator=65536,mass_zero_and_each_sign=MASS,max_atom=enc(p0),
             variance=enc(v),fourth_moment=enc(m4)),
    nu=dict(denominator=65536**2,mass={str(d):nu[d] for d in nu}),
    environment=dict(H=dict(cover='w<450 contained in L<=450',z=enc(zh),PGF_upper=enc(gh),certificate=hc),
                     R2=dict(cover='R2<3500 contained in R2<=3500',z=enc(zr),PGF=enc(gr),certificate=rc),
                     sum_dyadic_upper=enc(delta_sum),adopted_delta=enc(delta),
                     quantifier='Every fixed A before every raw chi draw'),
    analytic_psi=dict(pi_lower='157/50',pi_upper='22/7',
        domain1024_curvature=enc(curv[32]),domain1024_positive=enc(pos[32]),
        domain2048_curvature=enc(curv[16]),domain2048_positive=enc(pos[16]),
        constants=[144,108],global_exponent='p0*p1/64'),
    exponent_enclosure=dict(positive_Taylor_degree=24,ceiling_per_exponential_bits=64,
        ceiling_after_exact_mixture_power640_bits=80,tiny_positive_powers='Rounded upward, never set to zero'),
    frequency_groups=groups,all_positive_representatives_covered=True,
    negative_frequency_handling='Paired; Nyquist counted twice conservatively',
    unused_nu_mass='Retained with absolute characteristic-function upper1',
    uncharged_truncation_loss=0,Z=enc(Z),chord_slope=enc(C8),good_row_upper=enc(Fgood),
    row_and_full_correct_upper=enc(U),row_lower_Jensen=enc(L),
    initial_correct_conditioned_row_and_full_upper=enc(Uc),initial_correct_conditioned_row_lower=enc(Lc),
    row_outward_lower=decimal_exact(lower_display,10),
    row_and_full_outward_upper=decimal_exact(upper_display,9),
    full_error_outward_lower=decimal_exact(1-upper_display,9),
    full_error_percent_outward_lower=decimal_exact(100*(1-upper_display),7)+'%',
    displayed_values_certified_by_exact_comparison=True,
    dyadic_slack_already_in_Z=enc(rounding_extra),dyadic_slack_less_than='2^-41',
    initial=dict(z=enc(z),chi_PGF=enc(gchi),product_PGF=enc(gprod),
                 coordinate_tail_certificate=ic,full_failure_upper='2^-132',A_quantifier='Every fixed A'),
    comparisons=dict(new_uniform_A_scope='Every pre-fixed A and hence every prior A law',
                     new_upper_less_than_quarter=True,old_uniform_Setup_upper='0.000030345',
                     numerical_tightening_of_old_uniform_Setup_upper=False),
    cryptographic_samples_generated=0)
(ROOT/'FINITE_CERTIFICATES.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Displayed row lower/upper',out['row_outward_lower'],out['row_and_full_outward_upper'])
print('Displayed full error lower',out['full_error_percent_outward_lower'])
