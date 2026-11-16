"""有限构造性检查；不访问服务，不代表协议或真实账户实验。"""
from itertools import product
from pathlib import Path
import json

def partitions(items):
    if not items:
        yield []
        return
    first,*tail=items
    for rest in partitions(tail):
        yield [[first]]+[b[:] for b in rest]
        for j in range(len(rest)):
            new=[b[:] for b in rest]
            new[j]=[first]+new[j]
            yield new

def realizable_sets(partition):
    block_masks=[sum(1<<x for x in b) for b in partition]
    values={0}
    for block in block_masks:values|={s|block for s in list(values)}
    return values

counts=[]
for n in range(1,5):
    masks=list(range(1,(1<<n)-1))
    ps=list(partitions(list(range(n))))
    options=[]
    for p in ps:
        reachable=realizable_sets(p)
        options.append((len(p),sum(1<<j for j,s in enumerate(masks) if s in reachable)))
    mismatches=0
    for fam in range(1<<len(masks)):
        required=[s for j,s in enumerate(masks) if fam&(1<<j)]
        # independent reference enumerates partitions and realizable unions
        brute=min(k for k,can in options if fam&~can==0)
        # structural prediction uses only future stop-membership signatures
        signatures={tuple(bool(s&(1<<i)) for s in required) for i in range(n)}
        predicted=len(signatures)
        mismatches+=brute!=predicted
    counts.append({'tasks':n,'partitions':len(ps),'termination_families':1<<len(masks),'mismatches':mismatches})

# A finite non-anticipativity example: neither hidden world is directly observable.
worlds=['m0','m1']
plans=['close_u','close_v']
good={'m0':{'close_u'},'m1':{'close_v'}}
per_world=all(any(p in good[m] for p in plans) for m in worlds)
uniform=[p for p in plans if all(p in good[m] for m in worlds)]
observations={'m0':'o0','m1':'o1'}
policies=[dict(zip(['o0','o1'],p)) for p in product(plans,repeat=2)]
winning=[p for p in policies if all(p[observations[m]] in good[m] for m in worlds)]
# A probe may itself consume the only remaining approval slot needed for cleanup.
post_probe={'m0':{'budget':0,'cleanup_needed':False},'m1':{'budget':0,'cleanup_needed':True}}
recoverable=all((not s['cleanup_needed']) or s['budget']>=1 for s in post_probe.values())

report={'kind':'finite_constructive_checks_only','date':'2026-11-02','partition_checks':counts,'total_families':sum(x['termination_families'] for x in counts),'total_mismatches':sum(x['mismatches'] for x in counts),'policy_example':{'forall_model_exists_plan':per_world,'uniform_open_loop_winners':uniform,'observation_policy_winners':winning,'permitted_probe_with_unclosable_obligation_is_viable':recoverable},'limits':['disjoint indivisible remote revocation blocks','exact fixed termination family','no rebinding or new grants during stop','every task has one block','toy observations assumed accurate','not website validation or full protocol proof']}
assert report['total_mismatches']==0
assert per_world and not uniform and len(winning)==1 and not recoverable
out=Path(__file__).parent/'finite_examples.json'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
