"""A2 complete continuation-cost search; AB2 static DRD bound on a joint search.
 The generic BB equivalence control intentionally has identical common optimizations.
 """
import math
from functools import lru_cache
from common import Graph,Meter,Cutoff,Result,State,refs_json,fixed_b_choice,terminal
from auth_lifecycle.a.model import properties
from auth_lifecycle.schema import canonical
from auth_lifecycle import reference as ri
from auth_lifecycle._reference_kernel import expand

def drd_bound(g,s):
 """Returns an admissible TOTAL-Q bound only under a checked static-test profile.
 Outside that profile it returns the public generic bound, never a speculative cut.
 """
 b=g.b;source=b['source'];base=g.lb(s)
 points=[g.point(x) for x in s.knowledge]
 if source['faults'] or any(x['configuration'] is not None or x['sessions'] for x in points):return base,None
 if len({x['budget']['requests'] for x in points})!=1:return base,None
 probes=[]
 for name,p in source['probes'].items():
  if p['phase']!='before':return base,None
  for w,schedule in p['outcomes'].items():
   if any(len(outs)!=1 or outs[0]['to_world']!=w or outs[0]['sessions'] or outs[0]['withdraw'] for outs in schedule):return base,None
   if len({outs[0]['observation'] for outs in schedule})!=1:return base,None
  probes.append('probe:'+name)
 refs=sorted(s.knowledge);n=len(refs);regions=[];configs=[a for a in b['catalog'] if a.startswith('configure:')]
 for aid in configs:
  mask=0
  for i,ref in enumerate(refs):
   g.meter.tick('region_checks');single=State(frozenset([ref]),s.remaining)
   cs=g.allowed(single).get(aid)
   if cs:mask|=1<<i
   # Independent raw interpreter + R-I verify this conditional viability entry.
   groups,err=expand(g.d,single.knowledge,aid)
   statuses=[ri.solve(g.d,knowledge=k,horizon=s.remaining-1).status.value for k in groups.values()] if not err else []
   if any(x not in {'FEASIBLE','IMPOSSIBLE'} for x in statuses):return base,None
   expected=not err and bool(groups) and all(x=='FEASIBLE' for x in statuses)
   g.meter.tick('region_reference_checks')
   if bool(cs)!=expected:raise RuntimeError('region/reference disagreement')
  if mask:regions.append({'action':aid,'mask':mask})
 tests=[]
 for aid in probes:
  if aid not in g.edges(s):continue
  groups={}
  for i,ref in enumerate(refs):
   p=g.point(ref);obj=source['probes'][aid.split(':')[1]]
   ob=obj['outcomes'][p['world']][p['attempts'].get(aid,0)][0]['observation']
   groups[ob]=groups.get(ob,0)|(1<<i)
  tests.append({'action':aid,'cost':b['catalog'][aid]['requests'],'groups':list(groups.values())})
 @lru_cache(None)
 def information(mask):
  g.meter.tick('drd_states')
  if any(mask&r['mask']==mask for r in regions):return 0
  choices=[]
  for t in tests:
   children=[mask&x for x in t['groups'] if mask&x]
   if any(x==mask for x in children):continue
   choices.append(t['cost']+max(information(c) for c in children))
  return min(choices,default=math.inf)
 full=(1<<n)-1;info=information(full)
 # The terminal/control cost floor is a MIN over all worlds, avoiding an invalid
 # sum of maxima attained on different observation branches.
 spent=g.spent(s);tail=min(g.lb(State(frozenset([r]),s.remaining))-spent for r in refs)
 bound=max(base,spent+info+tail)
 cert={'schema':'static-decision-region-bound/1','refs':refs,'regions':regions,'tests':tests,'information_cost':info,'minimum_tail_cost':tail,'spent':spent,'bound':bound,'scope':'static profile only; optimistic single-world configurations; no general dynamic DRD theorem'}
 # Independent bottom-up subset calculation (no call to information()).
 values={}
 for size in range(1,n+1):
  for mask in range(1,1<<n):
   if mask.bit_count()!=size:continue
   g.meter.tick('drd_certificate_states')
   if any(mask&r['mask']==mask for r in regions):values[mask]=0;continue
   vals=[]
   for t in tests:
    cs=[mask&x for x in t['groups'] if mask&x]
    if mask not in cs:vals.append(t['cost']+max(values[x] for x in cs))
   values[mask]=min(vals,default=math.inf)
 if values[full]!=info:raise RuntimeError('DRD certificate mismatch')
 return bound,cert

def solve(bundle,*,mode='A2',feedback=False,meter=None):
 meter=meter or Meter();g=Graph(bundle,meter);memo={};policies={};certificates=[];sig_cache={};quotient_cache={}
 quotient=mode in {'A_QUOTIENT','GENERIC_QUOTIENT'}
 joint=mode in {'AB2','RJOINT_DP','GENERIC_JOINT_BB'}
 greedy=mode=='BA_PROPERTY';prune=mode not in {'ACQUIRE_DP','RJOINT_DP'}
 lower_cache={}
 def lower(s):
  if s not in lower_cache:
   v,cert=drd_bound(g,s) if feedback else (g.lb(s),None)
   lower_cache[s]=v
   if cert is not None:certificates.append(cert)
  return lower_cache[s]
 def visit(s):
  if s in memo:meter.tick('policy_cache_hits');return memo[s]
  if quotient:
   qkey=(s.remaining,frozenset(continuation_signature(g,x,s.remaining,sig_cache) for x in s.knowledge))
   if qkey in quotient_cache:
    meter.tick('quotient_hits');value,template=quotient_cache[qkey]
    def lift(p,state):
     meter.tick('lift_nodes');head={'belief':refs_json(state.knowledge),'remaining':state.remaining,'kind':p['kind']}
     if p['kind']=='done':
      if not terminal(g.d,state):raise RuntimeError('quotient terminal mismatch')
      return head
     children=g.allowed(state).get(p['action'])
     if children is None or set(children)!=set(p['children']):raise RuntimeError('quotient action/observation mismatch')
     return dict(head,action=p['action'],children={o:lift(p['children'][o],c) for o,c in children.items()})
    memo[s]=value
    if template is not None:policies[s]=lift(template,s)
    return value
  meter.tick('policy_states');head={'belief':refs_json(s.knowledge),'remaining':s.remaining}
  if terminal(g.d,s):memo[s]=g.spent(s);policies[s]=dict(head,kind='done');return memo[s]
  if not g.winning(s):memo[s]=math.inf;return math.inf
  allowed=g.allowed(s)
  if not joint:
   picked=fixed_b_choice(g,allowed,s)
   if picked:allowed={picked:allowed[picked]}
  if greedy and all(g.point(x)['configuration'] is None for x in s.knowledge):
   controls=[a for a in allowed if not a.startswith('probe:')]
   if controls:allowed={min(controls,key=lambda a:(g.b['catalog'][a]['requests'],a)):allowed[min(controls,key=lambda a:(g.b['catalog'][a]['requests'],a))]}
   else:
    # Full outcome-labelled continuation signatures, not a current-predicate slice.
    def signatures(c):return {continuation_signature(g,ref,c.remaining,sig_cache) for ref in c.knowledge}
    scores=[];count=len(signatures(s))
    for a,cs in allowed.items():
     size=max(len(signatures(c)) for c in cs.values());cost=max(1,g.b['catalog'][a]['requests'])
     scores.append((-(count-size)/cost,a))
    if scores:
     a=min(scores)[1];allowed={a:allowed[a]}
  ordered=sorted(allowed,key=lambda a:(max(lower(c) for c in allowed[a].values()),a))
  best=math.inf;choice=None
  for a in ordered:
   cs=allowed[a]
   if prune and choice is not None and max(lower(c) for c in cs.values())>=best:
    meter.tick('bound_prunes');continue
   value=-math.inf;complete=True
   for c in sorted(cs.values(),key=lower,reverse=True):
    value=max(value,visit(c))
    if prune and value>=best and choice is not None:complete=False;meter.tick('branch_prunes');break
   if complete and value<best:best=value;choice=a
  memo[s]=best
  if choice is not None:policies[s]=dict(head,kind='act',action=choice,children={o:policies[c] for o,c in allowed[choice].items()})
  if quotient:quotient_cache[qkey]=(best,policies.get(s))
  return best
 try:
  if not g.root.knowledge:return Result('UNKNOWN','empty K')
  value=visit(g.root)
  if math.isinf(value):return Result('IMPOSSIBLE','complete finite query within the stated policy class',stats=dict(meter.counts))
  return Result('FEASIBLE','complete continuation minimax; A mode commits at common configuration, AB mode does not',policies[g.root],value,dict(meter.counts),certificates)
 except Cutoff:return Result('INCONCLUSIVE','shared deadline/work limit; no partial policy accepted',stats=dict(meter.counts),diagnostics=certificates)

def continuation_signature(g,ref,r,memo):
 key=(ref,r)
 if key in memo:return memo[key]
 g.meter.tick('projection_states');w,n=ref;obj=g.d['worlds'][w]['states'][n]
 from auth_lifecycle.b._kernel import native_units
 point=g.point(ref);world=g.b['source']['worlds'][point['world']]
 native_costs=tuple((a,len(native_units(world,x['configuration']))) for a,x in g.b['catalog'].items() if x['kind']=='configure')
 label=(obj['account'],tuple(obj['facts']),tuple(obj['approvals']),tuple(sorted(obj['budget'].items())),tuple(obj['capabilities']),tuple(obj['obligations']),native_costs)
 if r==0:answer=(label,())
 else:
  edges=g.edges(State(frozenset([ref]),r))
  tail=tuple((a,tuple((o,tuple(sorted(continuation_signature(g,x,r-1,memo) for x in c.knowledge))) for o,c in cs.items())) for a,cs in sorted(edges.items()))
  answer=(label,tail)
 memo[key]=answer;return answer
