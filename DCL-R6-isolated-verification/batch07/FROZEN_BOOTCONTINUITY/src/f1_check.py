"""History/ghost monitors and BFS. Monitors do not call transition guards."""
import sys, copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from collections import deque,Counter
import f1_model as M
from guard import LimitReached

def violations(s):
    errors=[]; childsets={}
    for z in s['stops']:childsets.setdefault(z['parent'],set()).add(z['child'])
    for z in s['stops']:
        if len(set(z['signers']))<3 or not set(z['signers'])<=set(s['cfg'][z['parent']]['members']):errors.append('CERTIFICATE_MEMBERSHIP_OR_THRESHOLD')
    if any(len(v)>1 for v in childsets.values()):errors.append('INV2_UniqueChild')
    activated={}
    for z in s['activations']:
        if z['parent'] is not None:activated.setdefault(z['parent'],set()).add(z['cfg'])
    if any(len(v)>1 for v in activated.values()):errors.append('INV1_UniqueHistory')
    seen_genesis={}
    for z in s['activations']:seen_genesis.setdefault(z['cfg'],set()).add(z['genesis'])
    if any(len(v)>1 for v in seen_genesis.values()):errors.append('INV1_FixedGenesis')
    issued=[g for g in s['ghost'] if g['kind']=='Release'];origins={g['a']:g['origin'] for g in issued}
    for g in issued:
        if g['phase']!='ACTIVE':errors.append('INV3_SealSafety')
        if any(z['parent']==g['cfg'] and g['position']>z['snapshot']['seq'] for z in s['stops']):errors.append('INV3_PostSealRelease')
        if not g['grant_ok']:errors.append('INV8_CurrentAuthority')
        if g['origin'][2]!=g['generation']:errors.append('INV8_CurrentGeneration')
        if not g['ready_ok']:errors.append('INV7_ReadySeparation')
    if any(sum(1 for z in s['send_facts'] if z['a']==a)>1 for a in range(4)):errors.append('INV8_SendRightAtMostOnce')
    for c,x in s['cfg'].items():
        if c in childsets and x['phase']!='SEALED':errors.append('RECOVERY_SealAbsorbing')
        if x['ready_state'] and x['objects']!=15:errors.append('INV7_DataCompleteness')
    # Determine ownership independently from model.heads implementation.
    past_parents={z['parent'] for z in s['activations'] if z['parent'] is not None}
    holders=[x for c,x in s['cfg'].items() if x['active'] and c not in past_parents]
    outstanding={(a,k) for a in origins for k in ('OUTCOME','DERIVATION')}-set(map(tuple,s['closed']))
    spent=[sum(1 for g in issued if g['origin'][0]==t) for t in range(2)]
    for x in holders:
        b=x['biz'];present=set(map(tuple,b['obl']))
        if not outstanding<=present:errors.append('INV4_RHOConservation')
        if b['hist']&s['exposure']!=s['exposure']:errors.append('INV4_HistoryConservation')
        if any(b['dedup'].get(k)!=v for k,v in s['dedup_truth'].items()):errors.append('INV4_DedupConservation')
        if b['charged']!=spent:errors.append('INV5_BudgetConservation')
        if any(b['charged'][t]+b['reserved'][t]>s['_limit'] for t in range(2)):errors.append('INV5_QuotaBound')
        for a,z in enumerate(b['attempts']):
            if a in origins and z['origin']!=origins[a]:errors.append('INV6_OriginPreservation')
            if z['result_origin'] is not None and z['result_origin']!=origins.get(a):errors.append('INV6_ResultOrigin')
    return sorted(set(errors))

def run(params,mutant,budget,soft_limit=60000):
    start=M.initial(params);start['_limit']=params['limit']
    states=[start];parents=[None];edges=[None];queue=deque([0]);seen={M.canonical(start):0}
    visits=0;generated=0;overflow=False;coverage=Counter();fault=None
    while queue:
        if visits>=soft_limit:return {'status':'INCONCLUSIVE_LIMIT','reason':'predeclared_subtask_visit_slice','visited':visits,'generated':generated,'distinct':len(states),'coverage':dict(coverage)}
        budget.visit();visits+=1;i=queue.popleft();s=states[i]
        errors=violations(s)
        if errors:
            ids=[];j=i
            while j is not None:ids.append(j);j=parents[j]
            ids.reverse();trace=[{'event':edges[j],'state':states[j]} for j in ids]
            return {'status':'COUNTEREXAMPLE_FOUND','violations':errors,'visited':visits,'generated':generated,
                    'distinct':len(states),'coverage':dict(coverage),'trace':trace,'length':len(trace)-1,
                    'shortest_scope':'BFS within this frozen parameter/mutant model'}
        if s['domain_overflow']:overflow=True;continue
        for label,n in M.successors(s,params,mutant):
            generated+=1;coverage[label.split(':')[0]]+=1
            key=M.canonical(n)
            if key not in seen:
                seen[key]=len(states);states.append(n);parents.append(i);edges.append(label);queue.append(len(states)-1)
    return {'status':'INCONCLUSIVE_DOMAIN' if overflow else 'PASS_BOUNDED','visited':visits,
            'generated':generated,'distinct':len(states),'coverage':dict(coverage),'violations':[],
            'checked':['INV1','INV2','INV3','INV4','INV5','INV6','INV7','INV8'],
            'scope_note':'Fixed commit oracle, coordinated data availability; no per-replica PBFT network or native handler refinement.'}

def replay(result,params,mutant,budget):
    if not result.get('trace'):return None
    trace=result['trace'];s=M.initial(params);s['_limit']=params['limit']
    if s!=trace[0]['state']:raise AssertionError('Replay initial state differs')
    for row in trace[1:]:
        budget.visit();matches=[n for label,n in M.successors(s,params,mutant) if label==row['event'] and n==row['state']]
        if not matches:raise AssertionError('Replay edge absent: '+row['event'])
        s=matches[0]
    budget.visit();return {'reproduced':violations(s)==result['violations'],'final_violations':violations(s),
                           'independence':'Monitors independent of transition guards; edge replay uses same model relation, not a second model implementation.'}
