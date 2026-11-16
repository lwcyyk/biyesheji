"""Metered candidate graph; inherited candidate transition implementation."""
import bootstrap
from common import Meter, Cutoff, Graph as OldGraph
from auth_lifecycle.schema import State, refs_json, digest
from auth_lifecycle.semantics import terminal
from auth_lifecycle.b._kernel import native_units
import time, math

class Graph(OldGraph):
    def __init__(self,bundle,meter):
        super().__init__(bundle,meter)
        self.model_digest=digest(bundle['l0'])
    def cost(self,s):
        return self.spent(s)
    def native_g(self,s):
        return max((len(native_units(self.b['source']['worlds'][self.point(x)['world']], self.point(x)['configuration'] or [])) for x in s.knowledge),default=0)
    def head(self,s):return {'belief':refs_json(s.knowledge),'remaining':s.remaining}
    def controls(self,s):return {a:cs for a,cs in self.edges(s).items() if self.b['catalog'][a]['kind']!='probe'}
    def certificate(self,s,result):
        return {'schema':'SCCP/1','model_digest':self.model_digest,'root':self.head(s),
                'scope':'control_only_bounded_completion','objective':'total_Q',
                'constraint_refs':['account','approval','budgets','native_effects','all_observations','strict_obligations','remaining_steps','version'],
                **result}

def control_solve(g,s,preferred=()):
    """Complete uniform configure/stop/cleanup search, not a catalog adapter."""
    cache={}
    def go(u):
        if u in cache:g.meter.tick('control_cache_hits');return cache[u]
        g.meter.tick('control_states');head=g.head(u)
        if terminal(g.d,u):ans={'status':'FEASIBLE','value':g.cost(u),'policy':dict(head,kind='done')}
        elif not u.knowledge:return {'status':'UNKNOWN','reason':'empty K'}
        elif u.remaining==0:ans={'status':'IMPOSSIBLE_IN_MODEL','refutation':{'kind':'horizon'}}
        else:
            entries={};best=None;edges=g.controls(u)
            aids=sorted(a for a in g.d['actions'] if g.b['catalog'][a]['kind']!='probe')
            for a in sorted(aids,key=lambda x:(x not in preferred,x)):
                if a not in edges:
                    entries[a]={'kind':'blocked'};continue
                rows={o:go(c) for o,c in edges[a].items()}
                bad=next((o for o,x in rows.items() if x['status']!='FEASIBLE'),None)
                if bad is not None:
                    entries[a]={'kind':'losing','observation':bad,'child':rows[bad]['refutation']};continue
                v=max(x['value'] for x in rows.values())
                if best is None or (v,a)<best[:2]:best=(v,a,rows)
            if best is None:ans={'status':'IMPOSSIBLE_IN_MODEL','refutation':{'kind':'all_controls','actions':entries}}
            else:
                v,a,rows=best
                ans={'status':'FEASIBLE','value':v,'policy':dict(head,kind='act',action=a,children={o:x['policy'] for o,x in rows.items()})}
        cache[u]=ans;return ans
    return g.certificate(s,go(s))

