"""B2: native-unit layers + independently checkable separation relaxations.
 Novelty not established: relates to parameterized enumeration / branch-and-bound.
 """
from itertools import combinations
from dataclasses import asdict
from common import Meter,Cutoff
from auth_lifecycle.b import engine,checker
from auth_lifecycle.b.model import prepare,Work
from auth_lifecycle.schema import digest

class SharedWork(Work):
 def __init__(self,meter):super().__init__(10**9);self.meter=meter
 def tick(self,label):super().tick(label);self.meter.tick('planner_'+label)

def subsets(items):
 items=sorted(items)
 for k in range(len(items)+1):yield from combinations(items,k)

def relaxed_reject(m,U,meter):
 """Optimistic: may choose different configuration per scenario; ignores local,
 numeric and ordering constraints. Rejection is therefore a necessary-condition cut.
 """
 U=set(U);units={g:u for u,x in m['revocations'].items() for g in x['affects']}
 options={t:[] for t in m['tasks']}
 for p,x in m['paths'].items():
  meter.tick('cut_path_checks')
  if not {units[g] for g in x['grants']}<=U:continue
  # Ignore approval/numeric constraints here to keep the relaxation safely broad.
  if any(m['credentials'][g]['account']!=m['tasks'][x['task']]['account'] for g in x['grants']):continue
  scopes=set().union(*(set(m['credentials'][g]['scope']) for g in x['grants']))
  if not set(m['tasks'][x['task']]['permissions'])<=scopes:continue
  options[x['task']].append(set(x['grants']))
 for t,ps in options.items():
  if not ps:return {'kind':'coverage','task':t,'units':sorted(U),'refs':['catalog.coverage','native.scope','account.binding']}
 removable=[u for u in U if m['revocations'][u]['coverage']=='all_material' and m['revocations'][u]['revoke'] is not None and (m['revocations'][u]['revoke']['approval'] is None or m['revocations'][u]['revoke']['approval'] in m['approved'])]
 for sid,sc in m['scenarios'].items():
  for R in subsets(removable):
   meter.tick('cut_revoke_subsets');dead=set().union(*(set(m['revocations'][u]['affects']) for u in R)) if R else set()
   if all(any(bool(p&dead) for p in options[t]) for t in sc['remote']) and all(any(not p&dead for p in options[t]) for t in sc['preserve']):break
  else:return {'kind':'separation','scenario':sid,'units':sorted(U),'refs':['stop.remote','preserve.every_prefix','native.partition','approval.membership']}
 return None

def solve(spec,*,method='B2',meter=None):
 meter=meter or Meter();m=prepare(spec);work=SharedWork(meter);cuts={};best=None;tested=0
 try:
  # Common negative-control fast path: exhaust only G=1 domains first. If one
  # succeeds, the empty-domain coverage cut certifies the global cost lower bound.
  empty=relaxed_reject(m,[],meter)
  for u in sorted(m['revocations']):
   cut=relaxed_reject(m,[u],meter)
   if cut is not None:continue
   names=[p for p in m['paths'] if engine.resources(m,[p])[2]<={u}]
   for C in subsets(names):
    meter.tick('singleton_configurations');delivery=engine.deliver(m,C,work)
    if delivery is None:continue
    ck=checker.check_delivery(m,delivery,work=work)
    if ck['verdict']!='ACCEPTED':raise RuntimeError(ck)
    key=(ck['metrics']['G'],list(C))
    if best is None or key<best[0]:best=(key,delivery,ck['metrics'])
  if best is not None and best[0][0]==1 and empty is not None:
   cert={'schema':'native-unit-relaxation/1','model_digest':digest(m),'context':{'world_scope':'single_declared_contract','approved':m['approved'],'budgets':m['budgets'],'actions':{u:x['revoke'] for u,x in m['revocations'].items()}},'lower_bound':1,'cuts':[empty]}
   return {'status':'FEASIBLE','configuration':best[1]['configuration'],'delivery':best[1],'metrics':best[2],'optimal':True,'lower_bound':1,'gap':0,'certificate':cert,'stats':dict(meter.counts),'optimality_certificate_complete':True,'fast_path':'shared singleton-domain exact lower bound'}
  # Same cuts/lower bound preprocessing is supplied to both exact search methods.
  for U in subsets(m['revocations']):
   meter.tick('unit_sets');cuts[tuple(U)]=relaxed_reject(m,U,meter)
  feasible_units=[u for u,c in cuts.items() if c is None]
  lower=min(map(len,feasible_units),default=None)
  cert={'schema':'native-unit-relaxation/1','model_digest':digest(m),'context':{'world_scope':'single_declared_contract','approved':m['approved'],'budgets':m['budgets'],'actions':{u:x['revoke'] for u,x in m['revocations'].items()}},'lower_bound':lower,'cuts':[c for c in cuts.values() if c is not None and (lower is None or len(c['units'])<lower)]}
  if lower is None:return {'status':'IMPOSSIBLE','certificate':cert,'stats':dict(meter.counts),'optimal':True}
  configs=[]
  if method=='B2':
   for U in sorted(feasible_units,key=lambda u:(len(u),u)):
    if best and len(U)>best[0][0]:break
    candidates=[p for p in m['paths'] if set(engine.resources(m,[p])[2])<=set(U)]
    for C in subsets(candidates):
     meter.tick('configuration_masks')
     if set(engine.resources(m,C)[2])!=set(U):continue
     tested+=1;delivery=engine.deliver(m,C,work)
     if delivery is None:continue
     checked=checker.check_delivery(m,delivery,work=work)
     if checked['verdict']!='ACCEPTED':raise RuntimeError(checked)
     key=(checked['metrics']['G'],list(C))
     if best is None or key<best[0]:best=(key,delivery,checked['metrics'])
  elif method=='GENERIC_BB':
   # Include/exclude branch-and-bound, same unit cuts, G bound, memo and planner.
   names=sorted(m['paths']);seen=set()
   def visit(i,C):
    nonlocal best,tested
    meter.tick('configuration_nodes');U=tuple(sorted(engine.resources(m,C)[2]))
    if best and len(U)>best[0][0]:return
    possible=engine.resources(m,C+names[i:])[2]
    if not any(set(U)<=set(v)<=possible for v in feasible_units):return
    refs,_=engine.inspect(m,C)
    if any(x!='catalog.coverage' for x in refs):return
    if i<len(names):visit(i+1,C);visit(i+1,C+[names[i]]);return
    if U not in cuts or cuts[U] is not None:return
    tested+=1;delivery=engine.deliver(m,C,work)
    if delivery is None:return
    ck=checker.check_delivery(m,delivery,work=work)
    if ck['verdict']!='ACCEPTED':raise RuntimeError(ck)
    key=(ck['metrics']['G'],C)
    if best is None or key<best[0]:best=(key,delivery,ck['metrics'])
   visit(0,[])
  else:raise ValueError(method)
  if best is None:return {'status':'IMPOSSIBLE','certificate':cert,'optimal':True,'stats':dict(meter.counts),'certificate_scope':'lower bound only; whole-search failure requires reference verification'}
  return {'status':'FEASIBLE','configuration':best[1]['configuration'],'delivery':best[1],'metrics':best[2],'optimal':True,'lower_bound':lower,'gap':best[0][0]-lower,'certificate':cert,'stats':dict(meter.counts),'tested_configurations':tested,'optimality_certificate_complete':best[0][0]==lower}
 except Cutoff:
  return {'status':'INCONCLUSIVE','delivery':best[1] if best else None,'metrics':best[2] if best else None,'lower_bound':locals().get('lower'),'optimal':False,'stats':dict(meter.counts)}

def check_lower_bound(spec,certificate,meter):
 """Independent necessary-cut verifier: does not call solve/relaxed_reject/engine.
 It reconstructs raw credential effects and checks every domain below claimed LB.
 """
 m=prepare(spec);bound=certificate['lower_bound'];index={tuple(c['units']):c for c in certificate['cuts']}
 if certificate.get('model_digest')!=digest(m):return False
 if certificate.get('context')!={'world_scope':'single_declared_contract','approved':m['approved'],'budgets':m['budgets'],'actions':{u:x['revoke'] for u,x in m['revocations'].items()}}:return False
 if bound is not None and (type(bound) is not int or not 0<=bound<=len(m['revocations'])):return False
 allu=sorted(m['revocations'])
 for size in range(len(allu)+1 if bound is None else bound):
  for chosen in combinations(allu,size):
   meter.tick('certificate_domains')
   if chosen not in index:return False
   allowed={g for u in chosen for g in m['revocations'][u]['affects']};routes={t:[] for t in m['tasks']}
   for route in m['paths'].values():
    gs=set(route['grants']);task=m['tasks'][route['task']]
    if not gs<=allowed:continue
    if any(m['credentials'][g]['account']!=task['account'] for g in gs):continue
    if any(perm not in {v for g in gs for v in m['credentials'][g]['scope']} for perm in task['permissions']):continue
    routes[route['task']].append(gs)
   c=index[chosen]
   if c['kind']=='coverage':
    if c.get('refs')!=['catalog.coverage','native.scope','account.binding']:return False
    if c.get('task') not in routes or routes[c['task']]:return False
   elif c['kind']=='separation':
    if c.get('refs')!=['stop.remote','preserve.every_prefix','native.partition','approval.membership']:return False
    if c.get('scenario') not in m['scenarios']:return False
    sc=m['scenarios'][c['scenario']];acts=[]
    for u in chosen:
     obj=m['revocations'][u];op=obj['revoke']
     if obj['coverage']=='all_material' and op and (op['approval'] is None or op['approval'] in m['approved']):acts.append(u)
    for bits in range(1<<len(acts)):
     meter.tick('certificate_revoke_masks');removed={g for j,u in enumerate(acts) if bits&(1<<j) for g in m['revocations'][u]['affects']}
     blocked=any(not any(route&removed for route in routes[t]) for t in sc['remote'])
     blocked |= any(not any(route.isdisjoint(removed) for route in routes[t]) for t in sc['preserve'])
     if not blocked:return False
   else:return False
 return True
