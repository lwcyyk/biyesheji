"""Shared, metered finite semantics. No native requests, hidden-world oracle or reset."""
import sys,time,math,json,hashlib
from pathlib import Path
from collections import Counter
sys.dont_write_bytecode=True
ROOT=Path('D:/毕业设计/auth-lifecycle');sys.path.insert(0,str(ROOT/'src'))
from auth_lifecycle.schema import prepare,State,refs_json
from auth_lifecycle.semantics import terminal,branches,safe
from auth_lifecycle.a.joint_reference import Result

class Cutoff(Exception):pass
class Meter:
 def __init__(self,seconds=30,limit=1_000_000):
  self.start=time.perf_counter();self.cpu_start=time.process_time();self.seconds=seconds;self.limit=limit;self.counts=Counter()
 def tick(self,label,n=1):
  self.counts[label]+=n
  if time.perf_counter()-self.start>self.seconds or sum(self.counts.values())>self.limit:raise Cutoff('shared cycle deadline/work budget')
 def elapsed(self):return time.perf_counter()-self.start

class Graph:
 """Identity state projection shared by all methods: approval, effects, observation,
 budgets, obligations and transitions are retained. No predicate-only slicing.
 """
 def __init__(self,bundle,meter):
  self.b=bundle;self.meter=meter;self.d,self.root=prepare(bundle['l0']);self.cache={};self.win={};self.optimistic={}
 def edges(self,s):
  if s in self.cache:return self.cache[s]
  self.meter.tick('menu_states');out={}
  for a in self.d['actions']:
   self.meter.tick('edge_checks');children,err=branches(self.d,s,a)
   if not err and children:out[a]=children
  self.cache[s]=out;return out
 def winning(self,s):
  if s in self.win:return self.win[s]
  self.meter.tick('shield_states')
  if terminal(self.d,s):ok=True
  elif not s.knowledge or s.boundary or s.remaining==0:ok=False
  else:ok=any(all(self.winning(c) for c in cs.values()) for cs in self.edges(s).values())
  self.win[s]=ok;return ok
 def allowed(self,s):return {a:cs for a,cs in self.edges(s).items() if all(self.winning(c) for c in cs.values())}
 def spent(self,s):return max(self.b['source']['budget']['requests']-self.d['worlds'][w]['states'][n]['budget']['requests'] for w,n in s.knowledge)
 def lb(self,s):
  """Perfect-information, favourable-outcome relaxation; available to every method."""
  def one(ref,r):
   key=(ref,r)
   if key in self.optimistic:return self.optimistic[key]
   self.meter.tick('relaxed_states');single=State(frozenset([ref]),r)
   if terminal(self.d,single):v=self.spent(single)
   elif r==0 or not safe(self.d,ref):v=math.inf
   else:
    vals=[]
    for a,cs in self.edges(single).items():
     vals.extend(one(x,r-1) for c in cs.values() for x in c.knowledge)
    v=min(vals,default=math.inf)
   self.optimistic[key]=v;return v
  return max((one(x,s.remaining) for x in s.knowledge),default=math.inf)
 def point(self,ref):return self.b['points']['/'.join(ref)]['point']

def fixed_b_choice(graph,actions,state):
 """B2 catalog adapter: all candidates already pass identical robust W checking;
 minimize registered native-unit cardinality, then the unchanged lexical tie.
 No B2 speedup is charged to A or AB from this cheap adapter.
 """
 from auth_lifecycle.b._kernel import native_units
 rows=[]
 for a in actions:
  meta=graph.b['catalog'][a]
  if meta['kind']!='configure':continue
  config=meta['configuration']
  possible={graph.point(x)['world'] for x in state.knowledge}
  g=max(len(native_units(graph.b['source']['worlds'][w],config)) for w in possible)
  rows.append((g,config,a))
 return min(rows)[2] if rows else None
