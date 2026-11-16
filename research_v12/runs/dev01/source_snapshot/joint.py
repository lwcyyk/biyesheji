"""Same unrestricted joint policy class in every factorial cell."""
import bootstrap
import math
from kernel import Graph,Meter,Cutoff,terminal
from independent import Checker
from oracle import FullB
from auth_lifecycle.checker import check_policy

def solve(bundle,*,ab=False,a4=False,bmethod='B2',mode='BB',meter=None):
    meter=meter or Meter();g=Graph(bundle,meter);ck=Checker(bundle,meter);oracle=FullB(g,ck,bmethod)
    memo={};policies={};cells=None
    if a4:
        from a4 import Cells
        cells=Cells(g,ck)
    def visit(s,receipt=None):
        if s in memo:meter.tick('joint_exact_cache_hits');return memo[s]
        meter.tick('joint_states')
        if not s.knowledge:return math.inf
        if terminal(g.d,s):memo[s]=g.cost(s);policies[s]=dict(g.head(s),kind='done');return memo[s]
        if s.remaining==0:memo[s]=math.inf;return math.inf
        if cells:
            hit=cells.find(s)
            if hit is not None:
                memo[s],policies[s]=hit;return memo[s]
        core=oracle.solve(s,receipt,ab)
        best=core.get('value',math.inf) if core['status']=='FEASIBLE' else math.inf
        policy=core.get('policy')
        edges=g.edges(s)
        def bound(cs):return max(ck.lower(c) for c in cs.values())
        for a,cs in sorted(edges.items(),key=lambda x:(bound(x[1]),x[0])):
            if mode!='DP' and bound(cs)>=best:
                meter.tick('joint_bound_prunes');continue
            rows={};v=0
            for o,c in sorted(cs.items()):
                value=visit(c,(s,a,o,core));v=max(v,value)
                if mode!='DP' and v>=best:break
                if c in policies:rows[o]=policies[c]
            if v<best and len(rows)==len(cs):
                best=v;policy=dict(g.head(s),kind='act',action=a,children=rows)
        memo[s]=best
        if policy is not None:
            policies[s]=policy
            if cells:cells.add(s,best,policy)
        return best
    try:
        if not g.root.knowledge:return {'status':'UNKNOWN','reason':'empty K'}
        v=visit(g.root)
        ans={'status':'FEASIBLE' if math.isfinite(v) else 'IMPOSSIBLE_IN_MODEL','value':v if math.isfinite(v) else None,'policy':policies.get(g.root)}
        if ans['policy']:
            check=check_policy(g.d,ans['policy']);meter.tick('final_policy_check_nodes',check.nodes)
            if check.verdict!='ACCEPTED':raise AssertionError(check)
            ans['check']=vars(check)
        ans.update(stats=dict(meter.counts),transfers=oracle.transfers,native_results=oracle.native_results,cells=cells.log if cells else [])
        return ans
    except Cutoff as e:return {'status':'INCONCLUSIVE','reason':str(e),'stats':dict(meter.counts)}

