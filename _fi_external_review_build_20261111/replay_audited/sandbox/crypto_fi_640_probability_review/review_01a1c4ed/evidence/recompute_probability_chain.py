"""New deterministic scalar checker, written in this review after proof exposure.
No candidate mechanism, matrices, keys, tokens, ciphertexts, or random sampling.
"""
from pathlib import Path
import os
from fractions import Fraction as F
from decimal import Decimal, localcontext
from collections import defaultdict
from math import factorial
import hashlib, json, sys, subprocess

sys.set_int_max_str_digits(0)
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
BASE=Path(os.environ['FRODO_FI_SANDBOX'])
OUT=Path(__file__).resolve().parents[1]
EV=OUT/'evidence'
SINGLE=BASE/'crypto_fi_640_correctness_audit'
JOINT=BASE/'crypto_fi_640_joint_correctness'
REF1=json.loads((SINGLE/'evidence/SCALAR_CERTIFICATES.json').read_text(encoding='utf-8'))
REF2=json.loads((JOINT/'evidence/JOINT_SCALAR_CERTIFICATES.json').read_text(encoding='utf-8'))
checks=[]
def check(name, condition):
    checks.append({'name':name,'pass':bool(condition)})
    if not condition: raise AssertionError(name)
def rf(v): return F(int(v['numerator']),int(v['denominator']))
def fstr(v): return {'numerator':str(v.numerator),'denominator':str(v.denominator)}
def dec(v):
    with localcontext() as c:
        c.prec=65
        return str(Decimal(v.numerator)/Decimal(v.denominator))
def record(v): return {'exact':fstr(v),'display_only':dec(v)}
def same(name, value, reference): check(name, value==rf(reference))
def ihash(v): return hashlib.sha256(v.to_bytes((v.bit_length()+7)//8,'big')).hexdigest()
def binary_certificate(num,den):
    exponent=den.bit_length()-num.bit_length()
    def holds(b): return (num<<b)<=den if b>=0 else num<=(den<<(-b))
    while not holds(exponent): exponent-=1
    while holds(exponent+1): exponent+=1
    return dict(exponent=exponent,ratio_le_two_to_minus_exponent=holds(exponent),next_exponent_fails=not holds(exponent+1),
        numerator_bits=num.bit_length(),denominator_bits=den.bit_length(),numerator_binary_sha256=ihash(num),denominator_binary_sha256=ihash(den))

# Recreate mass law from the official table, with zero counted once.
mass=[9288,8720,7216,5264,3384,1918,958,422,164,56,17,4,1]
weights={0:mass[0]}
for x in range(1,13): weights[x]=weights[-x]=mass[x]
den=1<<16
q=1<<15
check('mass normalized',sum(weights.values())==den)
check('parity exactly balanced',all(sum(w for x,w in weights.items() if x%2==b)==den//2 for b in [0,1]))
v=sum(F(w*x*x,den) for x,w in weights.items())
m4=sum(F(w*x**4,den) for x,w in weights.items())
same('variance',v,REF1['variance']); same('fourth moment',m4,REF1['fourth_moment'])
p0,p1=F(mass[0],den),F(mass[1],den)
diff=defaultdict(int); product=defaultdict(int)
for x,wx in weights.items():
    for y,wy in weights.items():
        diff[x-y]+=wx*wy
        product[x*y]+=wx*wy
check('difference total',sum(diff.values())==den**2)
for d in range(-24,25):
    check(f'difference {d}',diff[d]==REF2['difference_mass'][str(d)] and diff[d]==diff[-d])
nu={d:F(diff[d],den**2) for d in diff}
check('difference one exact',nu[1]==F(1629101,16777216))

# Chernoff envelopes use unreduced numerator/denominator convention of source certificates.
def square_pgf(z): return sum(F(w,den)*z**(x*x) for x,w in weights.items())
chernoff={}
for label,count,cut,z,key in [('key',1280,8000,F(63,64),'key_norm'),('R',640,3500,F(31,32),'update_row_norm')]:
    g=square_pgf(z)
    num=g.numerator**count*z.denominator**cut
    de=g.denominator**count*z.numerator**cut
    cert=binary_certificate(num,de)
    check(label+' binary certificate',cert==REF1['environment'][key]['certificate'])
    same(label+' PGF',g,REF1['environment'][key]['scalar_PGF'])
    chernoff[label]=dict(PGF=fstr(g),certificate=cert)
wcert=binary_certificate(16**9600*17**4500,17**9600*15**4500)
check('weight binary certificate',wcert==REF1['environment']['weight']['certificate'])
unit_probability=2*p1
jg=1-unit_probability/2
jcert=binary_certificate((1<<128)*jg.numerator**1280,jg.denominator**1280)
check('unit-count binary certificate',jcert==REF1['environment']['key_unit_count']['certificate'])
bad_single=F(1,2**640)+sum(F(1,2**k) for k in [wcert['exponent'],chernoff['key']['certificate']['exponent'],chernoff['R']['certificate']['exponent'],jcert['exponent']])
bad_base=F(1,2**640)+2*F(1,2**27)
check('single bad budget strict',bad_single<F(1,2**22))
check('base bad budget strict',bad_base<F(1,2**25))
same('single bad union',bad_single,REF1['environment']['dyadic_sum_upper'])
same('joint bad union',bad_base,REF2['base_environment']['bad_sum'])

envelopes={}
for s,K,key in [(32,144,'small_envelope_original'),(16,108,'small_envelope_extension')]:
    curvature=2*F(157,50)**2*v-F(2,3)*F(22,7)**4*m4/s**2
    positive=1-2*F(22,7)**2*v/s**2
    check(f'curvature {s}',curvature>=K)
    check(f'positive {s}',positive>0)
    same(f'author curvature {s}',curvature,REF2[key]['curvature_lower'])
    same(f'author positive {s}',positive,REF2[key]['positive_lower'])
    envelopes[str(s)]=dict(K=K,curvature=record(curvature),positive=record(positive))

# Recurrent positive Taylor sum, separate from author's direct power/factorial sum.
def taylor(x,degree=24):
    term=F(1); total=term
    for k in range(1,degree+1):
        term=term*x/k
        total+=term
    return total
def ceiling_grid(x,bits):
    scale=1<<bits
    k,rem=divmod(x.numerator*scale,x.denominator)
    ans=F(k+(rem!=0),scale)
    check(f'ceiling {bits} valid {len(checks)}',ans>=x and ans-x<F(1,scale))
    return ans

C=F(144*8000*8001,q*q)
check('exp C lower >5300',taylor(C)>5300)
same('single C',C,REF1['Fourier']['C'])
single_ranges=[(1,7),(8,85),(86,1024),(1025,q//2)]
check('single frequency coverage',[(a,b) for a,b in single_ranges]==[(1,7),(8,85),(86,1024),(1025,16384)] and sum(b-a+1 for a,b in single_ranges)==q//2)
check('single low largest argument',7*12*12<=1024)
check('single middle largest argument',85*12<=1024)
exps=[F(144*4500*8001*8**2,q*q),F(144*4500*128*86**2,q*q),F(4500*128,64)*p0*p1]
floors=[x.numerator//x.denominator for x in exps]
check('single tail exponent floors',floors==[309,571,169])
for k,x in enumerate(exps): same(f'single exponent {k}',x,REF1['Fourier']['exponent_lower_values'][k])
eps_exact=(sum(F(1,5300**(t*t)) for t in range(1,8))+sum(c*F(1,2**b) for c,b in zip([78,939,15360],floors)))/2
eps_good=F(1,10600)+F(1,2**46)
eps=eps_good+F(1,2**22)
check('single good Fourier budget',eps_exact<=eps_good)
coord_low,coord_up=F(1,4)-eps,F(1,4)+eps
same('coordinate lower',coord_low,REF1['single_coordinate']['exact_lower'])
same('coordinate upper',coord_up,REF1['single_coordinate']['exact_upper'])
same('single exact Fourier envelope',eps_exact,REF1['Fourier']['good_probability_error_exact_envelope'])
check('single decimal endpoints',F('0.2499054')<=coord_low<=coord_up<=F('0.2500946'))

# Joint mixture bounds: full difference law or selected improvements with all other mass =1.
groups=[]
maxargs=[]
for name,lo,hi,K,t,dmax in [('L1',1,1,144,1,24),('L23',2,3,144,2,24),('L47',4,7,108,4,24),('M815',8,15,144,8,4),('M1663',16,63,144,16,1)]:
    table={d:ceiling_grid(1/taylor(F(K*8000*t*t*d*d,q*q)),64) for d in range(dmax+1)}
    R=1-2*sum(nu[d]*(1-table[d]) for d in range(1,dmax+1))
    check(name+' R in [0,1]',0<=R<=1)
    Q=ceiling_grid(R**640,80)
    ref=next(g for g in REF2['frequency_groups'] if g['name']==name)
    same(name+' mixture R',R,ref['R']); same(name+' Q',Q,ref['R_power640_up'])
    for d,item in ref['exp_upper'].items(): same(name+' exponent enclosure '+d,table[int(d)],item)
    maxarg=hi*dmax*12
    check(name+' maximal argument in small domain',maxarg<=(2048 if K==108 else 1024))
    maxargs.append(maxarg)
    groups.append(dict(name=name,range=[lo,hi],count=hi-lo+1,R=fstr(R),Q=fstr(Q),exp_upper={str(d):fstr(x) for d,x in table.items()},partial_remaining_mass=fstr(1-2*sum(nu[d] for d in range(1,dmax+1)))))
xlo=F(144*4500*64**2,q*q); xhi=F(4500,64)*p0*p1
check('joint high small exponent',xlo>2)
check('joint high global Taylor >3',taylor(xhi,3)>3)
Rh=1-F(4,3)*nu[1]; Qh=ceiling_grid(Rh**640,80)
same('H64 R',Rh,REF2['frequency_groups'][-1]['R'])
same('H64 Q',Qh,REF2['frequency_groups'][-1]['R_power640_up'])
groups.append(dict(name='H64',range=[64,q//2],count=16321,R=fstr(Rh),Q=fstr(Qh)))
coverage=[t for g in groups for t in range(g['range'][0],g['range'][1]+1)]
check('joint exact frequency coverage',coverage==list(range(1,q//2+1)))
check('Fourier negative pairing and Nyquist count',2*(q//2)==q and (q//2-1)*2+1==q-1)
# D contains an even number of consecutive residues, so its Nyquist coefficient is exactly zero.
check('Nyquist decode coefficient zero',sum(1 if k%2==0 else -1 for k in range(-4096,4096))==0)
Z=sum(g['count']*rf(g['Q']) for g in groups)/2
alpha=F(1,4); slope=sum(alpha**j for j in range(8))
check('chord exact slope',slope==F(21845,16384))
Fg=alpha**8+slope*Z; delta=F(1,2**25)
U=(1-delta)*Fg+delta
L=((1-delta)*(alpha-Z))**8
for name,value,key in [('Z',Z,'Z'),('F',Fg,'good_environment_row_upper'),('U',U,'unconditional_row_upper'),('L',L,'unconditional_row_lower_Jensen')]:
    same('joint final '+name,value,REF2[key])
check('F <1 and positive mean lower',0<Fg<1 and alpha-Z>0)
check('row decimals',F('0.0000152532')<=L<=U<=F('0.000030345'))
roundslack=F(63,2)*640/F(2**64)+F(8192,2**80)
same('rounding slack',roundslack,REF2['explicit_dyadic_rounding_slack'])
check('rounding slack <2^-49',roundslack<F(1,2**49))

# Initial exact PGF. The positive two-sided tail envelope covers all relevant failure residues.
z=F(21,20)
Az=sum(F(w,den)*z**x for x,w in weights.items())
Bz=sum(F(w,den**2)*z**k for k,w in product.items())
same('initial chi PGF',Az,REF1['initial_encryption']['chi_PGF'])
same('initial product PGF',Bz,REF1['initial_encryption']['product_PGF'])
inum=2*Az.numerator*Bz.numerator**1280*z.denominator**4096
iden=Az.denominator*Bz.denominator**1280*z.numerator**4096
icert=binary_certificate(inum,iden)
check('initial PGF binary certificate',icert==REF1['initial_encryption']['single_failure'])
check('initial per-coordinate <=2^-138',inum*(1<<138)<=iden)
check('initial64 union <=2^-132',64*inum*(1<<132)<=iden)
a=F(1,2**132)
conditional={'coordinate_lower':(coord_low-a)/(1-a),'coordinate_upper':coord_up/(1-a),'row_lower':(L-a)/(1-a),'row_upper':U/(1-a)}
check('conditional coord decimals',F('0.2499054')<=conditional['coordinate_lower'] and conditional['coordinate_upper']<=F('0.2500946'))
check('conditional row decimals',F('0.0000152532')<=conditional['row_lower'] and conditional['row_upper']<=F('0.000030345'))
same('joint conditional lower',conditional['row_lower'],REF2['initial_correct_conditioned_lower'])
same('joint conditional upper',conditional['row_upper'],REF2['initial_correct_conditioned_upper'])

# Source Theorem6.3: account for initial noise and conservative printed slack.
n,D,s=640,15,12
initial_max=2*n*s*s+s
W=2*n*n*D*s*s+2*n*n*s**3+n*D*s+n*s*s
Wprinted=2*(n*n*D*s**3+n*n*s**3)+n*D*s+n*s*s
check('printed worst-case constants', (initial_max,W,Wprinted)==(184332,3185256960,22649448960))
check('printed slack absorbs initial for support12',Wprinted-W>=initial_max)
check('official640 printed premise fails for every T>=1',Wprinted>q//8)

result=dict(schema='fi640-review/recomputed-probability-chain/2',scope='Exact deterministic scalar arithmetic; author proofs and prior review visible',
    mass=mass,variance=fstr(v),fourth_moment=fstr(m4),difference_mass={str(d):diff[d] for d in range(-24,25)},difference_denominator=den**2,
    Chernoff=dict(weight=wcert,unit_count=jcert,**chernoff),single_bad_union=fstr(bad_single),base_bad_union=fstr(bad_base),
    analytic_envelopes=envelopes,single=dict(C=fstr(C),tail_exponents=[fstr(x) for x in exps],epsilon=fstr(eps),lower=record(coord_low),upper=record(coord_up)),
    joint=dict(groups=groups,Z=record(Z),F=record(Fg),U=record(U),L=record(L),rounding_slack=fstr(roundslack)),
    initial=dict(chi_PGF=fstr(Az),product_PGF=fstr(Bz),binary_certificate=icert,union_coordinate_count=64,failure_upper='2^-132'),
    conditional_initial_correct={k:record(v) for k,v in conditional.items()},
    Theorem63=dict(initial_bound=initial_max,sharp_update_bound=W,printed_update_bound=Wprinted,slack=Wprinted-W,halfwidth=q//8),
    checks=checks,checks_passed=len(checks),all_checks_passed=True)
(EV/'RECOMPUTED_PROBABILITY_CHAIN.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(checks_passed=len(checks),Z=dec(Z),F=dec(Fg),U=dec(U),L=dec(L),initial_exponent=icert['exponent']),ensure_ascii=False))
