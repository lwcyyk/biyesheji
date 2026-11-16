"""Independent raw-interpreter exact reference for the A early-commit policy class.
 No imports from common.Graph, candidate search or DRD-bound implementation.
 Same declared policy class; full graph first, then restricted bottom-up values.
 """
from collections import deque
from auth_lifecycle.schema import prepare,refs_json
from auth_lifecycle._reference_kernel import expand,is_goal,is_safe
from auth_lifecycle.b._kernel import native_units

def solve(bundle):
 d,root=prepare(bundle['l0'])
 if not root.knowledge:return {'status':'UNKNOWN','reason':'empty K'}
 start=(root.remaining,root.knowledge);todo=deque([start]);seen={start};graph={}
 while todo:
  r,k=todo.popleft();edges={}
  if r and not is_goal(d,k) and all(is_safe(d,x) for x in k):
   for a in sorted(d['actions']):
    cs,err=expand(d,k,a)
    if err or not cs:continue
    edges[a]={o:(r-1,c) for o,c in cs.items()}
    for child in edges[a].values():
     if child not in seen:seen.add(child);todo.append(child)
  graph[(r,k)]=edges
 order=sorted(graph,key=lambda x:(x[0],sorted(x[1])));winning=set()
 for key in order:
  if is_goal(d,key[1]) or any(all(c in winning for c in cs.values()) for cs in graph[key].values()):winning.add(key)
 values={};policies={};cap=bundle['source']['budget']['requests']
 for key in order:
  r,k=key;head={'belief':refs_json(k),'remaining':r}
  if is_goal(d,k):
   values[key]=max(cap-d['worlds'][w]['states'][n]['budget']['requests'] for w,n in k);policies[key]=dict(head,kind='done');continue
  menu={a:cs for a,cs in graph[key].items() if all(c in winning for c in cs.values())}
  choices=[]
  for a in menu:
   if not a.startswith('configure:'):continue
   C=bundle['catalog'][a]['configuration'];worlds={bundle['points']['/'.join(x)]['point']['world'] for x in k}
   G=max(len(native_units(bundle['source']['worlds'][w],C)) for w in worlds);choices.append((G,C,a))
  if choices:
   a=min(choices)[2];menu={a:menu[a]}
  vals=[(max(values[c] for c in cs.values()),a) for a,cs in menu.items() if all(c in values for c in cs.values())]
  if vals:
   v,a=min(vals);values[key]=v;policies[key]=dict(head,kind='act',action=a,children={o:policies[c] for o,c in menu[a].items()})
 if start not in values:return {'status':'IMPOSSIBLE','states':len(graph)}
 return {'status':'FEASIBLE','Q':values[start],'policy':policies[start],'states':len(graph)}
