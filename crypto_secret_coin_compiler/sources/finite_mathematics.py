"""Abstract finite distributions and stopped-word identities only; no UE, PRF or PRP implementation."""
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations, permutations, product
import json

SRC=Path(__file__).resolve().parent

# Count every abstract permutation on a four-element set.
permutation_checks=[]
for pi in permutations(range(4)):
    masses=[sum(pi[x]==y for x in range(4)) for y in range(4)]
    assert masses==[1,1,1,1]
    inverse=[pi.index(y) for y in range(4)]
    assert all(inverse[pi[x]]==x for x in range(4))
    collisions=sum(pi[x]==pi[y] for x,y in product(range(4),repeat=2))
    assert collisions==4
    permutation_checks.append(pi)

# Finite hidden-half-set distribution, not a cryptographic construction.
half_checks=[]
for N in [4,8]:
    subsets=list(combinations(range(N),N//2));law={}
    for subset in subsets:
        for x,y in product(subset,repeat=2):
            law[(x,y)]=law.get((x,y),F(0))+F(1,len(subsets)*(N//2)**2)
    marginal=[sum(p for (x,y),p in law.items() if x==z) for z in range(N)]
    assert marginal==[F(1,N)]*N
    collision=sum(p for (x,y),p in law.items() if x==y)
    tv=sum(abs(law.get((x,y),F(0))-F(1,N*N)) for x,y in product(range(N),repeat=2))/2
    assert collision==F(2,N) and tv==F(1,N)
    assert F(N//2,N)==F(1,2)
    half_checks.append({'N':N,'hidden_subsets':len(subsets),'single_output_uniform':True,
                        'two_query_collision':str(collision),'random_function_collision':str(F(1,N)),
                        'two_query_total_variation':str(tv),
                        'known_set_update_accept':1,'known_set_fresh_accept':'1/2'})

# One two-word stopped sampler: domain size3, words of2 bits, cap2.
def trace(pool):
    first,second=divmod(pool,4)
    if first<3:return (first,)
    if second<3:return (3,second)
    return None

# An arbitrary small test bijection; it is not a proposed cipher.
pi={x:(5*x+3)%16 for x in range(16)};inverse={y:x for x,y in pi.items()}
assert len(inverse)==16
real={};prefix_law={}
for rho in range(16):
    tr=trace(pi[rho]);key=(tr,None if tr is None else rho)
    real[key]=real.get(key,F(0))+F(1,16)
for pool in range(16):
    tr=trace(pool);prefix_law[tr]=prefix_law.get(tr,F(0))+F(1,16)
simulated={}
for tr,mass in prefix_law.items():
    if tr is None:
        simulated[(None,None)]=mass
        continue
    completions=[pool for pool in range(16) if trace(pool)==tr]
    for pool in completions:
        key=(tr,inverse[pool]);simulated[key]=simulated.get(key,F(0))+mass/len(completions)
assert real==simulated
assert prefix_law[None]==F(1,16)
for tr,rho in real:
    if tr is not None:assert trace(pi[rho])==tr

def closure(K,T,C):
    K,T,C=map(set,(K,T,C))
    while True:
        old=(K.copy(),T.copy(),C.copy())
        for j in [2,3,4]:
            if j in K and j in T:K.add(j-1)
            if j-1 in K and j in K:T.add(j)
            if j-1 in C and j in T:C.add(j)
        if old==(K,T,C):break
    known_seeds={j+1 for j in K}|T
    return {'Kstar':sorted(K),'Tstar':sorted(T),'Cstar':sorted(C),
            'known_seed_indices':sorted(known_seeds),'valid':not bool(K&C)}

histories={
    'hidden3_then_Key3':closure([3],[],[2]),
    'public_incoming_token2':closure([],[2],[2]),
    'late_token3_without_key':closure([],[3],[2]),
    'late_token3_and_Key3':closure([3],[3],[2]),
    'interleaved_hidden3':closure([1,4],[4],[2]),
    'EncLeak_keymask_no_direct_key':closure([],[],[2])}
assert histories['hidden3_then_Key3']['valid'] and 3 not in histories['hidden3_then_Key3']['known_seed_indices']
assert histories['public_incoming_token2']['valid']
assert histories['late_token3_without_key']['valid'] and not histories['late_token3_and_Key3']['valid']
assert histories['interleaved_hidden3']['valid']
assert histories['EncLeak_keymask_no_direct_key']['valid']

nonce_gap=F(1)-F(1,2);assert F(1,2)+nonce_gap/2==F(3,4)
cost=[]
for kappa,e,B,h in [(16,1,16,17),(32,2,40,33),(128,5,160,129)]:
    slots=B*(e*h+2*(e+1)*h)
    pool=2*max(kappa,(slots+1)//2)
    assert pool>=slots and pool%2==0
    cost.append({'kappa':kappa,'source_epoch':e,'B':B,'conservative_hstar':h,
                 'slot_bits':slots,'pool_bits':pool,'token_extra_bits':4*kappa,
                 'key_extra_bits':4*kappa,'feasibility_or_measured_performance_claimed':False})

result={'scope':'Finite probability, prefix completion and scalar accounting only',
        'abstract_permutations_checked':len(permutation_checks),'half_image_checks':half_checks,
        'stopped_word_completion':{'uniform_pool_size':16,'raw_and_inverse_completion_joint_laws_equal':True,
                                   'failure_probability':'1/16','late_key_replay_consistent':True},
        'history_checks':histories,
        'BadPRF_counterexample':{'gap':'1/2','bias':'1/4','success':'3/4'},
        'independent_late_key_mismatch_example':{'domain_size':16,'single_pair_pass':'1/16'},
        'scalar_cost_examples':cost,'protocol_implementations':0,'attack_prototypes':0}
(SRC/'finite_mathematical_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'abstract_permutations':len(permutation_checks),'half_image_cases':len(half_checks),
                  'stopped_word_joint_law':'PASS','histories':len(histories),'status':'PASS'},ensure_ascii=False))
