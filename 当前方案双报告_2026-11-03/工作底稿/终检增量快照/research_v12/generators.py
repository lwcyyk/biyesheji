"""Deterministic public-model development families. No hidden-world oracle."""
import bootstrap
from copy import deepcopy
from itertools import product
from auth_lifecycle.b import fixtures as bf
from auth_lifecycle.a import fixtures as af

def source(sets=(('a','b'),('b','c'),('a','c')),*,h=3,budget=8,remote=False):
    m=bf.base(['job']);bf.env(m)
    for name in ['a','b','c']:bf.grant(m,name);bf.path(m,name,'job',[name])
    m['horizon']=min(3,h);m['approved']+=['probe','cleanup'];m['budgets'].update(requests=budget,approvals=8)
    m['scenarios']['stop']={'local':[],'remote':['job'] if remote else [],'preserve':[]}
    worlds={}
    for i,allowed in enumerate(sets):
        w=deepcopy(m)
        for g in w['credentials']:w['credentials'][g]['scope']=['use'] if g in allowed else ['other']
        worlds['w'+str(i)]=w
    s={'schema':'auth-lifecycle-a/1','account':'alice','caller':'agent-client','worlds':worlds,'initial':list(worlds),'scenario':'stop','probes':{},'cleanups':{},'faults':{},'budget':{'requests':budget,'approvals':8},'horizon':h}
    return s

def controlled():
    s=source((('a',),('a',)));af.probe(s,'observe',{w:w for w in s['worlds']})
    yield 'S1_witness_survives',s,'FEASIBLE'
    s=source();af.probe(s,'observe',{w:w for w in s['worlds']})
    yield 'S1_conflict_disappears',s,'FEASIBLE'
    s=source(((),('a',)));s['initial']=['w0'];af.probe(s,'change',{w:'changed' for w in s['worlds']})
    for w in s['worlds']:s['probes']['change']['outcomes'][w][0][0]['to_world']='w1'
    yield 'S2_new_authorization',s,'FEASIBLE'
    s=source(((),()));af.probe(s,'session',{w:'same' for w in s['worlds']},sessions=['verification']);af.cleanup(s)
    yield 'S2_infeasible_stays',s,'IMPOSSIBLE_IN_MODEL'
    s=source((('a',),('a',)));af.probe(s,'session',{w:'same' for w in s['worlds']},sessions=['verification']);af.cleanup(s)
    yield 'S3_obligation_invalidates_witness',s,'FEASIBLE'
    s=source((('a',),('a',)),budget=1);af.probe(s,'debit',{w:'same' for w in s['worlds']})
    yield 'S3_budget_invalidates_witness',s,'FEASIBLE'
    s=source(((),()),budget=1);af.probe(s,'debit',{w:'same' for w in s['worlds']})
    yield 'S3_infeasibility_survives',s,'IMPOSSIBLE_IN_MODEL'
    s=source();af.probe(s,'same',{w:'UNKNOWN' for w in s['worlds']})
    yield 'S4_core_survives',s,'IMPOSSIBLE_IN_MODEL'
    s=source();af.probe(s,'pair',{w:'pair' if w!='w2' else 'single' for w in s['worlds']})
    yield 'S4_core_removed',s,'FEASIBLE'
    s=source((('a',),('a',)));af.probe(s,'withdraw',{w:'same' for w in s['worlds']})
    for w in s['worlds']:s['probes']['withdraw']['outcomes'][w][0][0]['withdraw']=['issue']
    yield 'approval_withdrawal',s,'FEASIBLE'
    s=source((('a',),('a',)));af.probe(s,'lost',{w:'LOST' for w in s['worlds']});af.cleanup(s,opaque=True)
    for w in s['worlds']:
        s['probes']['lost']['outcomes'][w][0]=[af.outcome(w,'LOST'),af.outcome(w,'LOST',['opaque:verification'])]
    yield 'lost_multiple_successors',s,'FEASIBLE'
    s=source();s['initial']=[]
    yield 'empty_K',s,'UNKNOWN'

def joint_cases():
    yield from controlled()
    for n,q,effect in product([1,2],[3,6],[False,True]):
        s=af.acquisition(nuisance=n,requests=q,horizon=3)
        for m in s['worlds'].values():m['horizon']=3
        if effect:
            af.cleanup(s)
            for w in s['worlds']:s['probes']['z_native']['outcomes'][w][0][0]['sessions']=['verification']
        yield f'acq_n{n}_q{q}_effect{int(effect)}',s,None
    s=source((('a',),('a',)),remote=True);s['faults']['stop:revoke:a']=[[{'observation':'LOST','applied':True,'withdraw':[]},{'observation':'LOST','applied':False,'withdraw':[]}]]
    yield 'late_stop_unknown_effect',s,'IMPOSSIBLE_IN_MODEL'
    # Forced bootstrap, then equivalent task value despite differing unused future observations.
    s=source((('a',),('a',),()),remote=False);s['initial']=['w2']
    af.probe(s,'bootstrap',{w:w for w in s['worlds']})
    s['probes']['bootstrap']['outcomes']['w2'][0]=[af.outcome('w0','left'),af.outcome('w1','right')]
    af.probe(s,'optional',{w:w for w in s['worlds']},requests=1)
    yield 'A4_irrelevant_future',s,'FEASIBLE'

def alias_model(tasks=2,aliases=3,*,cost=0,coupled=False,budget=64):
    m=bf.base([f't{i}' for i in range(tasks)]);bf.env(m)
    for i in range(tasks):
        bf.grant(m,f'g{i}',domain='root' if coupled else None)
        for j in range(aliases):
            name=f'p{j}_{i}';bf.path(m,name,f't{i}',[f'g{i}'])
            m['paths'][name]['delegate']=bf.op('same_delegate_'+str(i),'delegate',0,cost)
    m['horizon']=3;m['budgets']['requests']=budget
    m['scenarios']['stop']={'local':['t0'],'remote':[],'preserve':[f't{i}' for i in range(1,tasks)]}
    return m
def b_cases():
    for t,a,c in product([1,2,3,4],[1,2,3],[False,True]):
        if t*a>12:continue
        yield f'alias_t{t}_a{a}_coupled{int(c)}',alias_model(t,a,coupled=c)
    for cost,budget in [(1,64),(1,2),(0,1)]:yield f'nonmerge_cost{cost}_q{budget}',alias_model(2,3,cost=cost,budget=budget)
    for n,m,_st,_g in bf.cases():
        if len(m['tasks'])<=4:
            m['horizon']=min(m['horizon'],3)
            yield 'legacy_shape_new_v12_'+n,m

