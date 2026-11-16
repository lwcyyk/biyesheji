"""Exact scalar PGF/moment/Fourier-envelope certificates; no matrix/crypto experiment."""
from pathlib import Path
from fractions import Fraction as F
from math import factorial
import hashlib
import json
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
ROOT = Path(__file__).resolve().parents[1]
MASS = [9288, 8720, 7216, 5264, 3384, 1918, 958, 422, 164, 56, 17, 4, 1]
W = {x: MASS[abs(x)] for x in range(-12, 13)}
assert sum(W.values()) == 65536
parity_counts = [sum(w for x,w in W.items() if x%2==b) for b in (0,1)]
assert parity_counts == [32768,32768]
Q = 32768


def frac(x):
    return dict(numerator=str(x.numerator), denominator=str(x.denominator))


def digest_int(x):
    return hashlib.sha256(x.to_bytes((x.bit_length() + 7)//8, "big")).hexdigest()


def binary_upper(num, den):
    """Largest integer b certified by num/den <= 2^-b, without floating point."""
    assert num > 0 and den > 0
    b = den.bit_length() - num.bit_length()
    def ok(k):
        return (num << k) <= den if k >= 0 else num <= (den << -k)
    while not ok(b): b -= 1
    while ok(b+1): b += 1
    return dict(exponent=b, ratio_le_two_to_minus_exponent=ok(b),
                next_exponent_fails=not ok(b+1), numerator_bits=num.bit_length(),
                denominator_bits=den.bit_length(), numerator_binary_sha256=digest_int(num),
                denominator_binary_sha256=digest_int(den))


def mgf_square(z):
    return sum((F(w, 65536) * z**(x*x) for x,w in W.items()), F(0))


def lower_sum_square(n, cutoff, z):
    g = mgf_square(z)
    num = pow(g.numerator, n) * pow(z.denominator, cutoff)
    den = pow(g.denominator, n) * pow(z.numerator, cutoff)
    cert = binary_upper(num, den)
    return dict(event=f"sum_{n}_chi_squared <= {cutoff}", z=frac(z),
                scalar_PGF=frac(g), formula="z^(-cutoff)*PGF(z)^n", certificate=cert)


started=time.perf_counter()
v = sum((F(w*x*x,65536) for x,w in W.items()),F(0))
m4 = sum((F(w*x**4,65536) for x,w in W.items()),F(0))
p0,p1=F(W[0],65536),F(W[1],65536)
curvature = 2*F(314,100)**2*v-F(2,3)*F(22,7)**4*m4/F(32**2)
positive = 1-2*F(22,7)**2*v/F(32**2)
assert curvature >= 144 and positive > 0
print("Exact moments and curvature verified")

# Upper bounds include the cutoff itself, hence cover the strict bad events used.
key = lower_sum_square(1280,8000,F(63,64))
print("Key norm exponent",key['certificate']['exponent'])
rnorm = lower_sum_square(640,3500,F(31,32))
print("Update row norm exponent",rnorm['certificate']['exponent'])
w_num = pow(16,9600)*pow(17,4500)
w_den = pow(17,9600)*pow(15,4500)
wcert = binary_upper(w_num,w_den)
jprob = F(W[1]+W[-1],65536)
jgf = 1-jprob/2
jcert = binary_upper((1<<128)*pow(jgf.numerator,1280),pow(jgf.denominator,1280))
print("Weight/J exponents",wcert['exponent'],jcert['exponent'])
env_bound = F(1,2**640) + sum((F(1,2**x) for x in [wcert['exponent'],key['certificate']['exponent'],rnorm['certificate']['exponent'],jcert['exponent']]),F(0))
env_budget = F(1,2**22)
assert env_bound <= env_budget

# All Fourier frequencies accounted for, using exact rational/exponential envelopes.
C = F(144*8000*8001,Q*Q)
taylor = sum((C**k/F(factorial(k)) for k in range(25)),F(0))
assert taylor > 5300
mid1 = F(144*4500*8001*8**2,Q*Q)
mid2 = F(144*4500*128*86**2,Q*Q)
high = F(4500*128,64)*p0*p1
floors = [x.numerator//x.denominator for x in [mid1,mid2,high]]
low = sum((F(1,5300**(t*t)) for t in range(1,8)),F(0))
eps_good = F(1,2)*(low+78*F(1,2**floors[0])+939*F(1,2**floors[1])+15360*F(1,2**floors[2]))
eps_good_budget = F(1,10600)+F(1,2**46)
assert eps_good <= eps_good_budget
eps_total = eps_good_budget+env_budget
lower,upper=F(1,4)-eps_total,F(1,4)+eps_total
display_lower,display_upper=F(2499054,10**7),F(2500946,10**7)
assert display_lower <= lower and upper <= display_upper
boundary_upper = F(2,Q)+F(8,Q)*eps_good_budget+env_budget
print("Single-coordinate interval",float(lower),float(upper))

# Initial encryption: exact product-noise PGF Chernoff, no Gaussian approximation.
prod={}
for x,wx in W.items():
    for y,wy in W.items():prod[x*y]=prod.get(x*y,0)+wx*wy
z=F(21,20)
gchi=sum((F(w,65536)*z**x for x,w in W.items()),F(0))
gprod=sum((F(w,65536**2)*z**k for k,w in prod.items()),F(0))
num=2*gchi.numerator*pow(gprod.numerator,1280)*pow(z.denominator,4096)
den=gchi.denominator*pow(gprod.denominator,1280)*pow(z.numerator,4096)
initcert=binary_upper(num,den)
init_full_exponent=initcert['exponent']-6
assert init_full_exponent > 0
print("Initial single/full failure exponents",initcert['exponent'],init_full_exponent)
initial_fail=F(1,2**init_full_exponent)
conditional_initial_lower=(lower-initial_fail)/(1-initial_fail)
conditional_initial_upper=upper/(1-initial_fail)
assert display_lower<=conditional_initial_lower and conditional_initial_upper<=display_upper

result=dict(schema="fi640/scalar-probability-certificates/1", date_asia_shanghai="2026-11-10",
            scope="Exact scalar sums and integer comparisons only; no LWE/ciphertext/key/token sampling",
            mass_denominator=65536,masses_zero_and_each_signed_point=MASS,parity_mass_numerators=parity_counts,
            variance=frac(v),fourth_moment=frac(m4),
            characteristic_envelope=dict(pi_lower="3.14",pi_upper="22/7",domain_abs_x="<=q/32=1024",
                curvature_lower=frac(curvature),psi_positive_lower=frac(positive),certified_constant=144),
            environment=dict(parent_nonunit_probability="2^-640",
                weight=dict(event="w<4500",covering_PGF_event="Bin(9600,1/2)<=4500",z="15/17",formula="(17/15)^4500*(16/17)^9600",certificate=wcert),
                key_norm=key,update_row_norm=rnorm,
                key_unit_count=dict(event="J<128",cover="J<=128",n=1280,probability=frac(jprob),tilt="1/2",formula="2^128*(1-p/2)^1280",certificate=jcert),
                dyadic_sum_upper=frac(env_bound),adopted_bad_budget=frac(env_budget),budget_verified=True),
            Fourier=dict(low_frequencies=[1,7],C=frac(C),exp_lower_Taylor_degree=24,
                Taylor_lower=frac(taylor),exp_C_gt_5300=True,
                remaining_ranges=[[8,85],[86,1024],[1025,16384]],counts=[78,939,15360],
                exponent_lower_values=[frac(x) for x in [mid1,mid2,high]],
                adopted_exp_upper_powers=[f"2^-{x}" for x in floors],
                good_probability_error_exact_envelope=frac(eps_good),adopted_good_error=frac(eps_good_budget),
                total_error=frac(eps_total),all_frequencies_covered=True),
            single_coordinate=dict(exact_lower=frac(lower),exact_upper=frac(upper),
                outward_decimal_lower="0.2499054",outward_decimal_upper="0.2500946",outward_rounding_checked=True),
            full_message=dict(lower="(1161/8192)^15360 > 2^-46080",upper=frac(upper),
                outward_decimal_upper="0.2500946",relation="all64correct implies chosen coordinate correct; lower event U0=F0=R=0, G0 free"),
            tie_boundary_mass_upper=frac(boundary_upper),
            initial_encryption=dict(z=frac(z),chi_PGF=frac(gchi),product_PGF=frac(gprod),
                formula="2*z^-4096*PGF_chi(z)*PGF_XY(z)^1280",single_failure=initcert,
                full_failure_upper=f"2^-{init_full_exponent}",coordinate_union_count=64),
            condition_initial_full_correct=dict(coordinate_lower=frac(conditional_initial_lower),
                coordinate_upper=frac(conditional_initial_upper),
                full_message_upper=frac(conditional_initial_upper),same_outward_decimal_bounds_verified=True,
                method="Event/Frechet bounds using initial failure<=2^-132; no independence assumption"),
            rounding="All certifying operations exact Fraction/integer; decimal display follows exact rational comparison; no floating-point value is an acceptance criterion",
            truncations="No sampler/support/environment truncation silently discarded; bad environment budget charged; Fourier ranges1..q/2 fully enclosed; Taylor retained as positive lower sum only",
            elapsed_seconds_display_only=time.perf_counter()-started)
(ROOT/'evidence/SCALAR_CERTIFICATES.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print("Scalar certificates written")
