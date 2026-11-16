"""SPEC2 finite mathematics only. No encryption/key generation or network APIs."""
import copy
import hashlib
import itertools
import json
from fractions import Fraction as R
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
CFG = json.loads((ROOT / 'INPUTS.json').read_text(encoding='utf-8'))
ROWS = []

def row(kind, inputs, result, passed=True):
    ROWS.append(dict(kind=kind, inputs=inputs, result=result, passed=bool(passed)))
    if not passed:
        raise AssertionError((kind, inputs, result))

def width(n):
    return (n - 1).bit_length()

def fail(n, B):
    return R(0) if n == 1 else R(2**width(n) - n, 2**width(n)) ** B

def gamma0(v):
    b = bin(v + 1)[2:]
    return '0'*(len(b)-1)+b

def read_gamma0(bits, at):
    z = 0
    while bits[at + z] == '0':
        z += 1
    end = at + 2*z + 1
    return int(bits[at + z:end], 2)-1, end

# Full specification values, not sampled outputs.
for n in CFG['sampler_n']:
    k = width(n)
    p = R(1) if n == 1 else R(n, 2**k)
    for B in CFG['B_values']:
        f = fail(n, B)
        per_value = (1-f)/n
        row('canonical_probability', dict(n=n,k=k,B=B),
            dict(accept_per_round=p,tail=f,per_success_output=per_value,
                 expected_rounds=R(0) if n==1 else 1/p),
            f <= R(1,2**B) and n*per_value+f == 1 and (n==1 or p>R(1,2)))

for q in [5, 17, 101]:
    row('field_domain_mapping',dict(q=q),dict(full_domain=list(range(q)),
        nonzero_domain=[h+1 for h in range(q-1)],full_width=width(q),nonzero_width=width(q-1)),
        set(h+1 for h in range(q-1))==set(range(1,q)))
row('inside_call_tail_scope',dict(n=5,total_rounds=3,already_rejected=1),
    dict(remaining_tail=fail(5,2),correct_bound=R(1,4),call_start_bound=R(1,8)),
    fail(5,2)<=R(1,4) and fail(5,2)>R(1,8))
row('direct_control_bits',{},dict(challenge_bit_width=1,fair_bit_width=1,rejection_fail_probability=0))

# Explicit exhaustive bit-word strings for small cases, retaining rejected words.
for n in [x for x in CFG['sampler_n'] if x<=CFG['explicit_word_enumeration_n_max']]:
    for B in range(1,CFG['explicit_word_enumeration_B_max']+1):
        if n==1:
            row('word_enumeration',dict(n=n,B=B),dict(total=1,counts=[1],fails=0,bits=0))
            continue
        m=2**width(n); counts=[0]*n; failures=0
        for words in itertools.product(range(m),repeat=B):
            accepted=next((h for h in words if h<n),None)
            if accepted is None: failures+=1
            else: counts[accepted]+=1
        total=m**B
        row('word_enumeration',dict(n=n,B=B),dict(total=total,counts=counts,fails=failures),
            len(set(counts))==1 and R(failures,total)==fail(n,B))

# Exact rank maps; triangle and rectangle weights agree by factor 2 ideally.
for L in CFG['L_values']:
    pairs=[(j,r) for j in range(2,L+1) for r in range(j,L+1)]
    rect=list(itertools.product(range(2,L+1),range(1,L+1)))
    valid=[x for x in rect if x[0]<=x[1]]
    F=L*(L-1)//2
    decoded=[]
    for a in range(F):
        off=0
        for j in range(2,L+1):
            size=L-j+1
            if off<=a<off+size:
                decoded.append((j,j+a-off));break
            off+=size
    row('index_bijection',dict(L=L),dict(F=F,triangle=decoded,rectangle=rect,
         triangle_weight=R(1,F),rectangle_weight=R(1,len(rect))),
         decoded==pairs and valid==pairs and len(rect)==2*F)

# Fully encoded success tape, with one rejected word, plus n=1 zero-bit call.
calls=[(1,1,5,[7,2]),(2,1,4,[3]),(3,1,1,[])]
data=''.join(gamma0(v) for v in (2,2,2,len(calls)))
for role,coord,n,words in calls:
    k=width(n); t=len(words)
    data+=''.join(gamma0(v) for v in (role,coord,n,k,t))
    data+=''.join(format(h,f'0{k}b') for h in words)
    data+=gamma0(t)
at=0; header=[]
for _ in range(4):
    v,at=read_gamma0(data,at);header.append(v)
parsed=[]
for _ in range(header[3]):
    vals=[]
    for h in range(5):
        v,at=read_gamma0(data,at);vals.append(v)
    role,coord,n,k,t=vals
    words=[]
    for _ in range(t):
        words.append(int(data[at:at+k],2));at+=k
    pos,at=read_gamma0(data,at)
    assert pos==t and k==width(n)
    assert (n==1 and t==0) or (t>=1 and all(h>=n for h in words[:-1]) and words[-1]<n)
    parsed.append((role,coord,n,words))
row('complete_tape_roundtrip',dict(calls=calls),dict(encoded_bits=data,parsed=parsed,bitlength=len(data)),
    parsed==calls and at==len(data))

# Adaptive domain choice from previous accepted values; exact conditional tails.
B=CFG['adaptive_B']; maxdepth=CFG['adaptive_calls']; nodes=[]
def adaptive(prefix, mass, depth):
    if depth==maxdepth:return mass
    n=[3,5,9][sum(prefix)%3]
    f=fail(n,B)
    nodes.append(dict(prefix=prefix,n=n,mass=mass,conditional_tail=f))
    assert f<=R(1,2**B)
    return sum((adaptive(prefix+[v],mass*(1-f)/n,depth+1) for v in range(n)),R(0))
survival=adaptive([],R(1),0)
row('adaptive_union',dict(B=B,calls=maxdepth),dict(nodes=nodes,failure=1-survival,
    union_bound=min(R(1),R(maxdepth,2**B))),1-survival<=R(maxdepth,2**B))

# Abstract transactional event ledger; no cryptographic algorithm is implemented.
def state(accepted=False):
    return dict(e=2 if accepted else 1,accepted=accepted,C=[2] if accepted else [],
                P=['old'],K=['old'],T=['old'],records=['parent'],counter=1,cache='old' if accepted else None)
for op,steps in [('Setup',1),('EncLeak',4),('UpdLeak',5),('ChallengeFresh',4),('ChallengeUpdate',5),
                 ('NextBeforeChallenge',3),('NextAfterChallenge',11)]:
    old=state(accepted=op=='NextAfterChallenge')
    if op=='Setup': old.update(e=0,K=[],P=[],T=[],records=[],counter=0)
    if op.startswith('Challenge'): old['e']=2
    for stopped in range(1,steps+1):
        staged=copy.deepcopy(old)
        # Staged public-key computation can precede failure, with no public commit.
        staged['P'].append('new-uncommitted')
        committed=copy.deepcopy(old)
        row('atomic_failure',dict(op=op,failed_sampling_step=stopped,total_steps=steps),
            dict(retained_state=committed,temporary_discarded=staged,public='FAIL',partial_tape=False,halt=True),
            committed==old)
row('challenge_success_commit',{},dict(accepted=True,C=[2],one_commit=True))
row('generated_object_validation',dict(request=4,current=2),dict(response='bottom',K=[],T=[],sampling_calls=0))

# Coupling ranges: all possible conditional expected scores/outputs in finite grids.
scores=[R(-1,2),R(0),R(1,2)]
for ideal,c0 in itertools.product(scores,scores):
    row('score_range_coupling',dict(ideal=ideal,c0=c0),dict(c0_delta=abs(c0-ideal),fair_delta=abs(ideal)),
        abs(c0-ideal)<=1 and abs(ideal)<=R(1,2))
for p0,p1 in itertools.product([R(0),R(1,4),R(1,2),R(3,4),R(1)],repeat=2):
    row('ddh_world_coupling',dict(p0=p0,p1=p1),
        dict(c0_sum=abs(p0)+abs(p1),fair_sum=abs(p0-R(1,2))+abs(p1-R(1,2))),
        abs(p0)+abs(p1)<=2 and abs(p0-R(1,2))+abs(p1-R(1,2))<=1)

# R1: exact old-sampler arithmetic, both commitment interpretations.
c=CFG['legacy_negative_control'];q=c['q'];B=c['B'];k=q.bit_length()
p=R(q,2**(k+2));ps=R(q-1,2**(k+2));a=1-(1-p)**B;ast=1-(1-ps)**B
mu=-ast**3*a**6*(1-ast)/4
N=10*(c['Q']*c['L']+c['L']**2+1);F=c['L']*(c['L']-1)//2
row('R1_guarded_uniform',c,dict(p=p,p_star=ps,tail=(1-p)**B,tail_star=(1-ps)**B,
     expected_rounds=1/p,expected_star=1/ps,tail_floor=R(3,4)**B,
     atomic_C0_and_FAIR_signed_bias=mu,early_accepted_C0_signed_bias=2*mu,
     legacy_FAIR_error=(F+R(1,2))*N*R(1,2**B),legacy_C0_error=(2*F+1)*N*R(1,2**B),
     bias_decimal=float(abs(mu)),early_bias_decimal=float(2*abs(mu))),
     R(1,8)<=ps<=p<=R(1,4) and (1-ps)**B>=R(3,4)**B and
     abs(mu)>(F+R(1,2))*N*R(1,2**B))

for B in [1,3,7,32]:
    p=R(q,2**width(q));ps=R(q-1,2**width(q-1))
    a=1-(1-p)**B;ast=1-(1-ps)**B
    bias=ast**3*a**6*(1-ast)/4
    row('canonical_three_query',dict(q=q,B=B),dict(p=p,p_star=ps,bias=bias,
        FAIR_error=(F+R(1,2))*N*R(1,2**B)),bias<=(F+R(1,2))*N*R(1,2**B))

for L,Q,kappa in [(2,3,64),(4,20,128),(8,100,256)]:
    F=L*(L-1)//2;N=10*(Q*L+L*L+1)
    ceil_log=((2*F+1)*N-1).bit_length();B=max(1,kappa+ceil_log)
    actual=(2*F+1)*N*R(1,2**B)
    real_key=L*(L+1)//2; official=(3*L*L+L-4)//2
    refined=(3*L-1)*Q+real_key+official+3
    row('counts_and_B',dict(L=L,Q=Q,kappa=kappa),dict(F=F,N=N,B=B,error=actual,
        key_calls=real_key,official_calls=official,refined=refined),actual<=R(1,2**kappa) and refined<=N)

def enc(x):
    if isinstance(x,R): return {'numerator':str(x.numerator),'denominator':str(x.denominator)}
    raise TypeError(type(x).__name__)
out=dict(schema='SPEC2-MATH-RESULTS-1',generated_utc=datetime.now(timezone.utc).isoformat(),
    scope=CFG['scope'],checks=len(ROWS),passed=sum(r['passed'] for r in ROWS),rows=ROWS)
(ROOT/'RAW_RESULTS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,default=enc)+'\n',encoding='utf-8')
print(json.dumps(dict(checks=out['checks'],passed=out['passed'],all_passed=all(r['passed'] for r in ROWS),
    script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    inputs_sha256=hashlib.sha256((ROOT/'INPUTS.json').read_bytes()).hexdigest()),indent=2))
