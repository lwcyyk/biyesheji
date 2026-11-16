"""B3 second route: exact independent native-resource components, shared budget
 frontier convolution; coupled instances fall back to B2. Not a new decomposition
 theorem. Full sorted configuration tie is retained by not discarding configurations
 merely because another equal-G configuration uses less budget.
 """
from itertools import product
from common import Meter,Cutoff
from b_units import solve as fallback,subsets,SharedWork
from auth_lifecycle.b import engine,checker
from auth_lifecycle.b.model import prepare

def solve(spec,meter=None):
 meter=meter or Meter();m=prepare(spec);tasks=sorted(m['tasks']);parent={t:t for t in tasks}
 def root(t):
  while parent[t]!=t:t=parent[t]
  return t
 def join(a,b):parent[root(b)]=root(a)
 native={t:engine.resources(m,[p for p in m['paths'] if m['paths'][p]['task']==t])[2] for t in tasks}
 environments={t:{m['paths'][p]['environment'] for p in m['paths'] if m['paths'][p]['task']==t} for t in tasks}
 for i,t in enumerate(tasks):
  for u in tasks[i+1:]:
   meter.tick('component_relation_checks');shared=environments[t]&environments[u]
   if native[t]&native[u] or any(m['environments'][e]['kind']=='isolated' or m['environments'][e]['create']['requests'] or m['environments'][e]['create']['approvals'] for e in shared):join(t,u)
 comps={}
 for t in tasks:comps.setdefault(root(t),set()).add(t)
 if len(comps)==1:
  r=fallback(spec,meter=meter);r['decomposition']='coupled-fallback';return r
 best=None
 try:
  frontiers=[];scenarios=sorted(m['scenarios'])
  for component in comps.values():
   paths=sorted(p for p in m['paths'] if m['paths'][p]['task'] in component);frontier=[]
   for config in subsets(paths):
    meter.tick('component_configurations')
    if {m['paths'][p]['task'] for p in config}!=component:continue
    refs,metrics=engine.inspect(m,config)
    if any(r!='catalog.coverage' for r in refs):continue
    menu=engine.actions(m,config);scplans=[]
    for sid in scenarios:
     sc={k:[t for t in ts if t in component] for k,ts in m['scenarios'][sid].items()};opts=[]
     for actions in subsets(menu):
      meter.tick('component_stop_subsets')
      if len(actions)>m['horizon'] or not engine.goal(m,config,set(actions),sc):continue
      if any(not engine.authorized(m,menu[a]) for a in actions):continue
      q=metrics['setup_requests']+sum(menu[a]['requests'] for a in actions);ap=metrics['setup_approvals']+sum(menu[a]['approvals'] for a in actions)
      if q>m['budgets']['requests'] or ap>m['budgets']['approvals']:continue
      vec=(q,ap,len(actions))
      if any(all(x<=y for x,y in zip(v,vec)) for v,_ in opts):continue
      opts=[(v,a) for v,a in opts if not all(x<=y for x,y in zip(vec,v))];opts.append((vec,list(actions)))
     if not opts:break
     scplans.append(opts)
    if len(scplans)!=len(scenarios):continue
    for choices in product(*scplans):
     frontier.append({'configuration':list(config),'G':metrics['G'],'iso':metrics['isolated_environments'],'vectors':[x[0] for x in choices],'plans':{sid:choices[i][1] for i,sid in enumerate(scenarios)}})
   if not frontier:return {'status':'IMPOSSIBLE','optimal':True,'stats':dict(meter.counts),'decomposition':'component_infeasible','certificate_scope':'requires reference cross-check; no exported unsat proof'}
   frontiers.append(frontier)
  # Every component configuration is retained; budget convolution prunes prefixes.
  states=[{'configuration':[],'G':0,'iso':0,'vectors':[(0,0,0) for _ in scenarios],'plans':{s:[] for s in scenarios}}]
  for frontier in frontiers:
   nxt=[]
   for a,b in product(states,frontier):
    meter.tick('frontier_combinations');g=a['G']+b['G'];iso=a['iso']+b['iso'];vectors=[tuple(x+y for x,y in zip(v,w)) for v,w in zip(a['vectors'],b['vectors'])]
    if g>m['budgets']['units'] or iso>m['budgets']['isolated_environments']:continue
    if any(v[0]>m['budgets']['requests'] or v[1]>m['budgets']['approvals'] or v[2]>m['horizon'] for v in vectors):continue
    nxt.append({'configuration':sorted(a['configuration']+b['configuration']),'G':g,'iso':iso,'vectors':vectors,'plans':{sid:sorted(a['plans'][sid]+b['plans'][sid]) for sid in scenarios}})
   states=nxt
  for s in states:
   delivery={'configuration':s['configuration'],'setup':[x for x,_ in engine.setup(m,s['configuration'])],'plans':s['plans']}
   ck=checker.check_delivery(m,delivery,work=SharedWork(meter))
   if ck['verdict']!='ACCEPTED':raise RuntimeError(ck)
   key=(ck['metrics']['G'],s['configuration'])
   if best is None or key<best[0]:best=(key,delivery,ck['metrics'])
  if best is None:return {'status':'IMPOSSIBLE','optimal':True,'stats':dict(meter.counts),'decomposition':'global_budget_infeasible'}
  return {'status':'FEASIBLE','configuration':best[1]['configuration'],'delivery':best[1],'metrics':best[2],'optimal':True,'stats':dict(meter.counts),'decomposition':'independent_components','components':[sorted(c) for c in comps.values()],'component_frontier_sizes':[len(f) for f in frontiers],'lower_bound':None,'certificate_scope':'exact decomposition result checked by independent R-B; no general machine proof'}
 except Cutoff:return {'status':'INCONCLUSIVE','optimal':False,'stats':dict(meter.counts),'delivery':best[1] if best else None}
