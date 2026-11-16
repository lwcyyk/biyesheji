"""Deterministic scalar recheck, authored for the visible-proof review.
No matrix, key, token, ciphertext, PRG or random sampling is performed.
Historical files are opened for reading only. Outputs stay beside this script.
"""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal, localcontext
from collections import defaultdict
import hashlib
import json
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
sys.set_int_max_str_digits(0)
BASE = Path(r'D:\毕业设计')
OUT = Path(__file__).resolve().parent
S = BASE / 'crypto_fi_640_correctness_audit'
J = BASE / 'crypto_fi_640_joint_correctness'
Q = 32768
checks = []
started = time.perf_counter()

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(name, obj): (OUT/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def enc(x):
    x = F(x)
    return {'numerator': str(x.numerator), 'denominator': str(x.denominator)}
def dec(x):
    with localcontext() as ctx:
        ctx.prec = 48
        return str(Decimal(x.numerator)/Decimal(x.denominator))
def ratio(x): return F(int(x['numerator']), int(x['denominator']))
def check(name, ok):
    checks.append({'check': name, 'pass': bool(ok)})
    if not ok: raise AssertionError(name)
def eq(name, a, b): check(name, a == b)
def pin(p):
    p = Path(p)
    b = p.read_bytes()
    return {'path': str(p), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}

# Freeze actual input bytes, including every historical sidecar, before calculation.
inputs = [pin(p) for root in [S,J] for p in sorted(root.rglob('*')) if p.is_file()]
manuscript_names = ['CRYPTOANALYSIS_DRAFT.md', 'CLAIM_EVIDENCE_MATRIX.json', 'REVIEW_RESPONSE_AND_READINESS.md', 'MANIFEST.json']
inputs += [pin(BASE/'crypto_fi_research_manuscript_v1'/n) for n in manuscript_names]
record_checks = []
def walk(obj, origin):
    if isinstance(obj, dict):
        if all(k in obj for k in ('path','bytes','sha256')):
            actual = pin(obj['path'])
            ok = all(actual[k] == obj[k] for k in ('bytes','sha256'))
            record_checks.append({'record_in': str(origin), 'path': obj['path'], 'match': ok})
            check('input-record:'+str(origin.relative_to(BASE))+':'+obj['path'], ok)
        for value in obj.values(): walk(value, origin)
    elif isinstance(obj, list):
        for value in obj: walk(value, origin)
for root in [S,J]:
    for p in sorted(root.rglob('*.json')): walk(read(p),p)
for name in ['FI_journal_20261110.pdf','articlev08.tex','official_frodo_2021.pdf']:
    eq('source-copy:'+name, pin(S/'sources'/name)['sha256'], pin(J/'sources'/name)['sha256'])
eq('inherited scalar byte identity', pin(S/'evidence/SCALAR_CERTIFICATES.json')['sha256'], pin(J/'sources/INHERITED_SCALAR_CERTIFICATES.json')['sha256'])
save('INPUT_HASH_CHECK.json', {'inputs':inputs, 'referenced_records':record_checks, 'all_match':True})
print('Historical byte records verified:',len(record_checks),'records;',len(inputs),'locked files')

# Exact finite laws, using ordered-pair accumulation for both difference/product.
mass = [9288,8720,7216,5264,3384,1918,958,422,164,56,17,4,1]
W = {x:mass[abs(x)] for x in range(-12,13)}
eq('chi normalization',sum(W.values()),1<<16)
eq('parity masses',[sum(w for x,w in W.items() if x%2==b) for b in range(2)],[32768,32768])
diff, prod = defaultdict(int), defaultdict(int)
for x,wx in W.items():
    for y,wy in W.items():
        diff[x-y] += wx*wy
        prod[x*y] += wx*wy
eq('difference normalization',sum(diff.values()),1<<32)
v = sum(F(w*x*x,65536) for x,w in W.items())
m4 = sum(F(w*x**4,65536) for x,w in W.items())
eq('variance',v,F(64895,8192)); eq('fourth moment',m4,F(384929,2048))
eq('difference unit mass',F(diff[1],1<<32),F(1629101,16777216))
sc = read(S/'evidence/SCALAR_CERTIFICATES.json')
jc = read(J/'evidence/JOINT_SCALAR_CERTIFICATES.json')
eq('all 49 difference masses',{str(k):diff[k] for k in sorted(diff)},jc['difference_mass'])
eq('scalar variance',v,ratio(sc['variance'])); eq('scalar fourth moment',m4,ratio(sc['fourth_moment']))

def sum_pgf(weights,den,z,exponent):
    return sum((F(w,den)*z**exponent(x) for x,w in weights.items()),F(0))
def integer_digest(x): return hashlib.sha256(x.to_bytes((x.bit_length()+7)//8,'big')).hexdigest()
def binary_certificate(num,den):
    b = den.bit_length()-num.bit_length()
    def ok(k): return (num<<k)<=den if k>=0 else num<=(den<<(-k))
    while not ok(b): b-=1
    while ok(b+1): b+=1
    return {'exponent':b,'numerator_bits':num.bit_length(),'denominator_bits':den.bit_length(),
            'numerator_binary_sha256':integer_digest(num),'denominator_binary_sha256':integer_digest(den)}
def binary_match(name,own,author):
    for k,val in own.items(): eq(name+':'+k,val,author[k])
def lower_square(N,K,z):
    g = sum_pgf(W,65536,z,lambda x:x*x)
    return g,binary_certificate(pow(g.numerator,N)*pow(z.denominator,K),pow(g.denominator,N)*pow(z.numerator,K))

gkey,bkey = lower_square(1280,8000,F(63,64))
gr,br = lower_square(640,3500,F(31,32))
bw = binary_certificate(16**9600*17**4500,17**9600*15**4500)
punit = F(W[1]+W[-1],65536)
gj = 1-punit/2
bj = binary_certificate((1<<128)*gj.numerator**1280,gj.denominator**1280)
for name,own,author in [('key',bkey,sc['environment']['key_norm']['certificate']),('r',br,sc['environment']['update_row_norm']['certificate']),('w',bw,sc['environment']['weight']['certificate']),('J',bj,sc['environment']['key_unit_count']['certificate'])]:
    binary_match(name,own,author)
eq('key PGF',gkey,ratio(sc['environment']['key_norm']['scalar_PGF']))
eq('r PGF',gr,ratio(sc['environment']['update_row_norm']['scalar_PGF']))
eq('joint r PGF',gr,ratio(jc['base_environment']['square_PGF']))
delta_env_sum = F(1,2**640)+sum(F(1,2**b['exponent']) for b in [bkey,br,bw,bj])
delta_base_sum = F(1,2**640)+F(2,2**27)
check('single bad budget strict',delta_env_sum<F(1,2**22))
check('joint bad budget strict',delta_base_sum<F(1,2**25))

def taylor(x,degree):
    # Recurrence rather than independently exponentiating all monomials.
    term,total = F(1),F(1)
    for k in range(1,degree+1):
        term *= x/k
        total += term
    return total
envelopes = {}
for s,k in [(32,144),(16,108)]:
    curvature = 2*F(157,50)**2*v - F(2,3)*F(22,7)**4*m4/(s*s)
    positive = 1-2*F(22,7)**2*v/(s*s)
    check('curvature:'+str(s),curvature>=k)
    check('positive psi:'+str(s),positive>0)
    author = jc['small_envelope_original' if s==32 else 'small_envelope_extension']
    eq('curvature author:'+str(s),curvature,ratio(author['curvature_lower']))
    eq('positivity author:'+str(s),positive,ratio(author['positive_lower']))
    envelopes[str(s)] = {'curvature':enc(curvature),'positive':enc(positive),'K':k}

C = F(144*8000*8001,Q*Q)
check('positive Taylor exceeds 5300',taylor(C,24)>5300)
eq('scalar C',C,ratio(sc['Fourier']['C']))
eq('scalar Taylor recurrence',taylor(C,24),ratio(sc['Fourier']['Taylor_lower']))
tail_exponents = [F(144*4500*8001*8**2,Q*Q),F(144*4500*128*86**2,Q*Q),F(4500*128,64)*F(W[0]*W[1],65536**2)]
floors = [x.numerator//x.denominator for x in tail_exponents]
eq('scalar exponent floors',floors,[309,571,169])
for i,x in enumerate(tail_exponents): eq('scalar tail exponent:'+str(i),x,ratio(sc['Fourier']['exponent_lower_values'][i]))
single_ranges = [(1,7),(8,85),(86,1024),(1025,Q//2)]
eq('single all frequencies exactly once',[t for lo,hi in single_ranges for t in range(lo,hi+1)],list(range(1,Q//2+1)))
eg = F(1,2)*(sum(F(1,5300**(t*t)) for t in range(1,8))+sum(c*F(1,2**b) for c,b in zip([78,939,15360],floors)))
eg_adopt = F(1,10600)+F(1,2**46)
check('single good epsilon enclosure',eg<=eg_adopt)
eq('scalar good epsilon',eg,ratio(sc['Fourier']['good_probability_error_exact_envelope']))
eps = eg_adopt+F(1,2**22)
LC,UC = F(1,4)-eps,F(1,4)+eps
eq('single exact lower',LC,ratio(sc['single_coordinate']['exact_lower']))
eq('single exact upper',UC,ratio(sc['single_coordinate']['exact_upper']))

# Directed exponential enclosures and powers. Minimal ceiling checked on both sides.
def ceil_grid(x,bits):
    scale = 1<<bits
    k = -((-x.numerator*scale)//x.denominator)
    y = F(k,scale)
    check('minimal upward dyadic '+str(bits),y>=x and y-F(1,scale)<x)
    return y
def exp_u(x): return ceil_grid(1/taylor(x,24),64)
groups = []
for name,lo,hi,K,t,dmax in [('L1',1,1,144,1,24),('L23',2,3,144,2,24),('L47',4,7,108,4,24),('M815',8,15,144,8,4),('M1663',16,63,144,16,1)]:
    # The upper endpoint verifies domains, minimum frequency sets the weaker envelope.
    check('domain:'+name,hi*12*dmax<=(1024 if K==144 else 2048))
    table = {d:exp_u(F(K*8000*t*t*d*d,Q*Q)) for d in range(0 if dmax==24 else 1,dmax+1)}
    if dmax==24:
        Rg = sum(F(diff[d],1<<32)*table[abs(d)] for d in range(-24,25))
    else:
        Rg = 1-sum(F(2*diff[d],1<<32)*(1-table[d]) for d in range(1,dmax+1))
    Pg = ceil_grid(Rg**640,80)
    ag = next(g for g in jc['frequency_groups'] if g['name']==name)
    for d,x in table.items(): eq('exponential certificate:'+name+':'+str(d),x,ratio(ag['exp_upper'][str(d)]))
    eq('group R:'+name,Rg,ratio(ag['R']))
    eq('group Q:'+name,Pg,ratio(ag['R_power640_up']))
    groups.append({'name':name,'lo':lo,'hi':hi,'count':hi-lo+1,'R':enc(Rg),'Q':enc(Pg),'R_display':dec(Rg),'Q_display':dec(Pg)})
xsmall=F(144*4500*64**2,Q*Q)
xhigh=F(4500,64)*F(W[0]*W[1],65536**2)
check('high branch small exp>2',xsmall>2)
check('high branch Taylor>3',taylor(xhigh,3)>3)
Rh = 1-F(4,3)*F(diff[1],1<<32)
Ph = ceil_grid(Rh**640,80)
ag = jc['frequency_groups'][-1]
eq('H64 R',Rh,ratio(ag['R'])); eq('H64 Q',Ph,ratio(ag['R_power640_up']))
groups.append({'name':'H64','lo':64,'hi':16384,'count':16321,'R':enc(Rh),'Q':enc(Ph),'R_display':dec(Rh),'Q_display':dec(Ph)})
eq('joint all frequencies exactly once',[t for g in groups for t in range(g['lo'],g['hi']+1)],list(range(1,Q//2+1)))
Z = sum(g['count']*ratio(g['Q']) for g in groups)/2
alpha,delta = F(1,4),F(1,2**25)
slope = sum(alpha**k for k in range(8))
eq('chord slope',slope,F(21845,16384))
Fstar = alpha**8+slope*Z
Ustar = (1-delta)*Fstar+delta
Lstar = ((1-delta)*(alpha-Z))**8
for name,value,key in [('Z',Z,'Z'),('F',Fstar,'good_environment_row_upper'),('U',Ustar,'unconditional_row_upper'),('L',Lstar,'unconditional_row_lower_Jensen')]:
    eq('joint aggregate:'+name,value,ratio(jc[key]))
check('good F below 1',0<=Fstar<1)
check('Jensen input positive',0<alpha-Z)
check('joint upper below twice uniform',Ustar<F(1,32768))
rounding = F(63,2)*640/F(2**64)+F(8192,2**80)
eq('dyadic slack',rounding,ratio(jc['explicit_dyadic_rounding_slack']))
check('slack below 2^-49',rounding<F(1,2**49))
print('All single/joint frequency enclosures and directed dyadics reproduced')

# Exact initial PGF, no normal approximation, and Frechet conditioning.
z = F(21,20)
Az = sum_pgf(W,65536,z,lambda x:x)
Bz = sum_pgf(prod,1<<32,z,lambda x:x)
eq('initial chi PGF',Az,ratio(sc['initial_encryption']['chi_PGF']))
eq('initial product PGF',Bz,ratio(sc['initial_encryption']['product_PGF']))
init = binary_certificate(2*Az.numerator*Bz.numerator**1280*z.denominator**4096,Az.denominator*Bz.denominator**1280*z.numerator**4096)
binary_match('initial Chernoff',init,sc['initial_encryption']['single_failure'])
eq('initial per-coordinate exponent',init['exponent'],138)
eq('64-coordinate union exponent',init['exponent']-6,132)
a=F(1,2**132)
conditional = {'coord_lower':(LC-a)/(1-a),'coord_upper':UC/(1-a),'row_lower':(Lstar-a)/(1-a),'row_upper':Ustar/(1-a)}
for name,own,author in [('coord_lower',conditional['coord_lower'],sc['condition_initial_full_correct']['coordinate_lower']),('coord_upper',conditional['coord_upper'],sc['condition_initial_full_correct']['coordinate_upper']),('row_lower',conditional['row_lower'],jc['initial_correct_conditioned_lower']),('row_upper',conditional['row_upper'],jc['initial_correct_conditioned_upper'])]:
    eq('conditional endpoint:'+name,own,ratio(author))
CL,CU = F('0.2499054'),F('0.2500946')
RL,RU = F('0.0000152532'),F('0.000030345')
for name,L,U,dl,du in [('coordinate',LC,UC,CL,CU),('row',Lstar,Ustar,RL,RU),('conditioned coordinate',conditional['coord_lower'],conditional['coord_upper'],CL,CU),('conditioned row',conditional['row_lower'],conditional['row_upper'],RL,RU)]:
    check('display outward:'+name,dl<=L<=U<=du)
eq('error percentage',100*(1-RU),F('99.9969655'))

# Fixed-parameter statement of Theorem 6.3, plus explicit initial-noise repair.
n,D,s = 640,15,12
B0=2*n*s*s+s
Usharp=2*(n*n*D*s*s+n*n*s**3)+n*D*s+n*s*s
Uloose=2*(n*n*D*s**3+n*n*s**3)+n*D*s+n*s*s
check('source premise fails for all T>=1',Uloose>Q//8)
check('s12 slack absorbs initial for T>=1',Uloose-Usharp>=B0)

# All inputs still have their original bytes after the computation.
check('all historical inputs unchanged',all(pin(x['path'])==x for x in inputs))
result = {'schema':'fi640-probability-review/scalar-recomputation/1','scope':'exact deterministic scalar laws and rational inequalities',
    'sample_count':0,'historical_inputs_changed':False,
    'mass':mass,'difference_mass':{str(k):diff[k] for k in sorted(diff)},'variance':enc(v),'fourth_moment':enc(m4),
    'Chernoff':{'w':bw,'key':bkey,'r':br,'J':bj,'initial':init},
    'bad_environment':{'single_sum':enc(delta_env_sum),'single_budget':'2^-22','joint_sum':enc(delta_base_sum),'joint_budget':'2^-25'},
    'envelopes':envelopes,'single':{'C':enc(C),'tail_exponents':[enc(x) for x in tail_exponents],'good_error':enc(eg),'lower':enc(LC),'upper':enc(UC),'lower_display':dec(LC),'upper_display':dec(UC)},
    'joint':{'groups':groups,'Z':enc(Z),'F':enc(Fstar),'U':enc(Ustar),'L':enc(Lstar),'Z_display':dec(Z),'F_display':dec(Fstar),'U_display':dec(Ustar),'L_display':dec(Lstar),'rounding_slack':enc(rounding)},
    'initial':{'z':enc(z),'chi_PGF':enc(Az),'product_PGF':enc(Bz),'single_failure_exponent':138,'full_failure_exponent':132,'union_count':64},
    'conditional':{k:{'exact':enc(x),'display':dec(x)} for k,x in conditional.items()},
    'decimal_margin':{'coord_lower':enc(conditional['coord_lower']-CL),'coord_upper':enc(CU-conditional['coord_upper']),'row_lower':enc(conditional['row_lower']-RL),'row_upper':enc(RU-conditional['row_upper'])},
    'theorem63_at640':{'initial_bound':B0,'sharp_update_bound':Usharp,'printed_update_bound':Uloose,'decode_halfwidth':Q//8,'slack':Uloose-Usharp},
    'checks':checks,'checks_passed':len(checks),'all_passed':True,'elapsed_seconds_display_only':time.perf_counter()-started}
save('RECOMPUTED_CERTIFICATES.json',result)
print('PASS',len(checks),'checks; Z =',dec(Z),'U =',dec(Ustar),'L =',dec(Lstar))
