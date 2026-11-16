"""Independent direct policy/trace interpreter; never imports f4_dp."""
from itertools import product
from collections import deque
import json,hashlib

def input_problem(model):
    if len(model.get('initial',[]))==0:return 'EMPTY_INITIAL'
    for state in model['states'].values():
        for action in state['actions'].values():
            if action['enabled'] and len(action['segments'])==0:return 'EMPTY_SUCCESSOR'
            for segment in action['segments']:
                if segment['to'] not in model['states'] or segment['obs'] not in model['observations']:return 'UNKNOWN_SUCCESSOR'
                for micro in segment['steps']:
                    if micro['cost']<0:return 'NEGATIVE_COST'
    return None

def interpret(model,h,policy,budget,tree=False):
    if tree and 'per_world' in policy:return {'ok':False,'reason':'NONUNIFORM_WORLD_POLICY','worst_cost':None,'trace':[]}
    q=deque()
    for i,init in enumerate(model['initial']):q.append((init['state'],init['cost'],[],[],0,policy,i))
    leaves=[];uniform={}
    while q:
        sid,total,history,trace,depth,node,world=q.popleft();budget.visit()
        current=model['states'][sid]
        if not current['safe']:return {'ok':False,'reason':'UNSAFE_STATE','trace':trace,'world':world,'worst_cost':None}
        full=bool(current['goal'] and current['safe'] and current['post_inv'] and len(current['obligations'])==0)
        if depth==h:
            if not full:return {'ok':False,'reason':'HORIZON_OR_OPEN_OBLIGATION','trace':trace,'world':world,'cost':total,'worst_cost':None}
            leaves.append({'world':world,'cost':total,'trace':trace});continue
        if tree:
            choice='STOP' if node.get('stop') else node.get('action')
        else:
            choice=policy[0] if depth==0 else policy[1+model['observations'].index(history[-1][1])]
        key=json.dumps(history,separators=(',',':'))
        if key in uniform and uniform[key]!=choice:return {'ok':False,'reason':'NONUNIFORM_OBSERVATION','worst_cost':None,'trace':trace}
        uniform[key]=choice
        if choice=='STOP':
            if not full:return {'ok':False,'reason':'EARLY_STOP','trace':trace,'world':world,'cost':total,'worst_cost':None}
            leaves.append({'world':world,'cost':total,'trace':trace});continue
        row=current['actions'].get(choice)
        if row is None or not row['enabled']:return {'ok':False,'reason':'ACTION_DISABLED','trace':trace,'world':world,'cost':total,'worst_cost':None}
        if len(row['segments'])==0:return {'ok':False,'reason':'EMPTY_SUCCESSOR','trace':trace,'world':world,'worst_cost':None}
        for seg in row['segments']:
            cost=total;microtrace=[]
            for step in seg['steps']:
                cost+=step['cost'];microtrace.append({'cost':cost,'safe':step['safe']})
                if not step['safe']:return {'ok':False,'reason':'BAD_PREFIX','world':world,'cost':cost,'worst_cost':None,'trace':trace+[{'action':choice,'micro':microtrace}]}
            nextnode=node
            if tree:
                if seg['obs'] not in node.get('next',{}):return {'ok':False,'reason':'MISSING_OBSERVATION_BRANCH','world':world,'worst_cost':None,'trace':trace+[{'action':choice,'obs':seg['obs']}]}
                nextnode=node['next'][seg['obs']]
            record={'from':sid,'action':choice,'observation':seg['obs'],'to':seg['to'],'cost_before':total,'cost_after':cost,'micro':microtrace}
            q.append((seg['to'],cost,history+[(choice,seg['obs'])],trace+[record],depth+1,nextnode,world))
    return {'ok':True,'worst_cost':max(x['cost'] for x in leaves),'leaves':leaves,'policy_observation_keys':len(uniform)}

def solve(model,h,budget):
    invalid=input_problem(model)
    if invalid:return {'valid':False,'error':invalid,'optimum':None,'policies':0}
    width=0 if h==0 else (1 if h==1 else 1+len(model['observations']))
    best=None;best_policy=None;best_replay=None;records=[];first_failure=None
    for i,policy in enumerate(product(model['actions'],repeat=width)):
        result=interpret(model,h,policy,budget)
        if not result['ok'] and first_failure is None:first_failure=result
        signature=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        records.append({'policy_index':i,'ok':result['ok'],'worst_cost':result.get('worst_cost'),
                        'reason':result.get('reason'),'first_failure_hash':signature})
        if result['ok'] and (best is None or result['worst_cost']<best):
            best=result['worst_cost'];best_policy=list(policy);best_replay=result
    return {'valid':True,'error':None,'optimum':best,'policy':best_policy,'witness':best_replay,
            'policies':len(records),'policy_records':records,'first_failure':first_failure}
