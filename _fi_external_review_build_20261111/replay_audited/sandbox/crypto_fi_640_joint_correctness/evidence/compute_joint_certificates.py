"""Exact scalar mixture-moment/Fourier certificates; no cryptographic sampling."""
from fractions import Fraction as F
from pathlib import Path
from math import factorial
import json
import sys

sys.stdout.reconfigure(encoding='utf-8',line_buffering=True)
ROOT=Path(__file__).resolve().parents[1]
mass=[9288,8720,7216,5264,3384,1918,958,422,164,56,17,4,1]
W={x:mass[abs(x)] for x in range(-12,13)}
Q=32768
assert sum(W.values())==65536
nu={d:sum(W[x]*W.get(x-d,0) for x in W) for d in range(-24,25)}
assert sum(nu.values())==65536**2 and all(nu[d]==nu[-d] for d in nu)


def enc(x):return dict(numerator=str(x.numerator),denominator=str(x.denominator))
def up_dyadic(x,bits):
    scale=1<<bits
    return F((x.numerator*scale+x.denominator-1)//x.denominator,scale)
def exp_minus_upper(x):
    assert x>=0
    # Positive Taylor lower polynomial for exp(x), then exact upward dyadic rounding.
    s=sum((x**k/F(factorial(k)) for k in range(25)),F(0))
    y=up_dyadic(1/s,64)
    assert y*s>=1 and 0<y<=1
    return y
def power_upper(x):
    assert 0<=x<=1
    return up_dyadic(x**640,80)


def full_D_moment(K,t):
    beta=F(K*8000,Q**2)
    table={d:exp_minus_upper(beta*t*t*d*d) for d in range(25)}
    R=sum((F(nu[d],65536**2)*table[abs(d)] for d in range(-24,25)),F(0))
    return R,power_upper(R),table
def partial_D_moment(t,Dmax):
    beta=F(144*8000,Q**2)
    table={d:exp_minus_upper(beta*t*t*d*d) for d in range(1,Dmax+1)}
    R=1-sum((2*F(nu[d],65536**2)*(1-table[d]) for d in range(1,Dmax+1)),F(0))
    return R,power_upper(R),table


v=sum((F(w*x*x,65536) for x,w in W.items()),F(0))
m4=sum((F(w*x**4,65536) for x,w in W.items()),F(0))
curv16=2*F(314,100)**2*v-F(2,3)*F(22,7)**4*m4/F(16**2)
pos16=1-2*F(22,7)**2*v/F(16**2)
assert curv16>=108 and pos16>0
curv32=2*F(314,100)**2*v-F(2,3)*F(22,7)**4*m4/F(32**2)
pos32=1-2*F(22,7)**2*v/F(32**2)
assert curv32>=144 and pos32>0
assert [sum(w for x,w in W.items() if x%2==b) for b in (0,1)]==[32768,32768]
# Recheck the two base-environment scalar Chernoff envelopes used here.
wn=pow(16,9600)*pow(17,4500)
wd=pow(17,9600)*pow(15,4500)
assert (wn<<27)<=wd
zr=F(31,32)
gr=sum((F(w,65536)*zr**(x*x) for x,w in W.items()),F(0))
rn=pow(gr.numerator,640)*pow(zr.denominator,3500)
rd=pow(gr.denominator,640)*pow(zr.numerator,3500)
assert (rn<<27)<=rd
base_bad_sum=F(1,2**640)+2*F(1,2**27)
assert base_bad_sum<=F(1,2**25)

groups=[]
for name,lo,hi,K,t,dmax in [
    ('L1',1,1,144,1,24),('L23',2,3,144,2,24),('L47',4,7,108,4,24),
    ('M815',8,15,144,8,4),('M1663',16,63,144,16,1)]:
    R,P,table=full_D_moment(K,t) if dmax==24 else partial_D_moment(t,dmax)
    groups.append(dict(name=name,range=[lo,hi],count=hi-lo+1,K=K,representative_frequency=t,
                       difference_range=[-dmax,dmax],R=enc(R),R_power640_up=enc(P),
                       exp_upper={str(d):enc(z) for d,z in table.items()}))
    print(name,'R approx',float(R),'power upper',float(P))

p0,p1=F(W[0],65536),F(W[1],65536)
x_small=F(144*4500*64**2,Q**2)
x_global=F(4500,64)*p0*p1
assert x_small>2
assert sum((x_global**k/F(factorial(k)) for k in range(4)),F(0))>3
Rh=1-F(4,3)*F(nu[1],65536**2)
Ph=power_upper(Rh)
groups.append(dict(name='H64',range=[64,16384],count=16321,R=enc(Rh),R_power640_up=enc(Ph),
                   coefficient_CF_upper='1/3 from source small/global envelopes'))
assert sum(g['count'] for g in groups)==16384
ratio=lambda x:F(int(x['numerator']),int(x['denominator']))
Z=F(1,2)*sum((g['count']*ratio(g['R_power640_up']) for g in groups),F(0))
alpha=F(1,4)
chord=(1-alpha**8)/(1-alpha)
Fgood=alpha**8+chord*Z
delta_B=F(1,2**25)
row_upper=(1-delta_B)*Fgood+delta_B
row_lower=((1-delta_B)*(alpha-Z))**8
init_fail=F(1,2**132)
cond_upper=row_upper/(1-init_fail)
cond_lower=(row_lower-init_fail)/(1-init_fail)
print('Z',float(Z),'good row',float(Fgood),'row upper',float(row_upper),'row lower',float(row_lower))
print('Initial-correct conditioned upper',float(cond_upper),'less1/30000',cond_upper<F(1,30000))
assert 0<row_lower<=row_upper<F(1,30000)
assert cond_upper<F(1,30000)
adopted_upper=F(30345,10**9)
adopted_row_lower=F(152532,10**10)
assert row_upper<=adopted_upper and cond_upper<=adopted_upper
assert adopted_row_lower<=row_lower and adopted_row_lower<=cond_lower
assert adopted_upper<F(2500946,10**7)
rounding_extra=F(63,2)*640*F(1,2**64)+F(16384,2)*F(1,2**80)
assert rounding_extra<F(1,2**49)

o=dict(schema='fi640-joint/scalar-certificates/1',date_asia_shanghai='2026-11-10',
       exact_mass_denominator=65536,masses_zero_and_each_sign=mass,
       difference_mass_denominator=65536**2,difference_mass={str(d):nu[d] for d in nu},
       small_envelope_extension=dict(domain_abs_x=2048,curvature_lower=enc(curv16),positive_lower=enc(pos16),constant=108),
       small_envelope_original=dict(domain_abs_x=1024,curvature_lower=enc(curv32),positive_lower=enc(pos32),constant=144),
       base_environment=dict(events=['parent u has an odd entry','w>=4500','sum r_i^2>=3500'],
           bad_upper_terms=['2^-640','2^-27','2^-27'],bad_sum=enc(base_bad_sum),adopted_bad_upper='2^-25',
           binomial_Chernoff_check=True,square_PGF=enc(gr),r_norm_Chernoff_check=True),
       exponential_enclosure=dict(positive_Taylor_degree=24,upward_dyadic_bits=64,power640_upward_dyadic_bits=80,
           rule='exp(-x)<=1/sum_0^24(x^k/k!), then directed ceiling; power also rounded up exactly'),
       high_CF=dict(x_small=enc(x_small),x_global=enc(x_global),exp_global_Taylor_degree=3,
                    bound='abs(varphi_B(t))<=1/3 for64<=t<=q/2'),
       frequency_groups=groups,all16384_positive_frequencies_covered=True,
       Z=enc(Z),chord_slope=enc(chord),good_environment_row_upper=enc(Fgood),
       bad_base_environment_upper=enc(delta_B),unconditional_row_upper=enc(row_upper),
       unconditional_row_lower_Jensen=enc(row_lower),initial_correct_conditioned_upper=enc(cond_upper),
       initial_correct_conditioned_lower=enc(cond_lower),
       adopted_row_and_full_message_upper='0.000030345',adopted_row_lower='0.0000152532',
       initial_correct_condition_same_endpoints=True,upper_comparison_verified=True,
       strict_improvement_over_old_0_2500946=True,
       explicit_dyadic_rounding_slack=enc(rounding_extra),slack_below_two_to_minus49=True,
       sample_count=0,scope='Scalar laws/finite sums/directed exact rational comparisons only')
(ROOT/'evidence/JOINT_SCALAR_CERTIFICATES.json').write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
print('Joint scalar certificate saved')
