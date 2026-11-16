"""Independent finite-graph incremental Z3 encoding; no candidate solve call.
Shared solver constraints, push/pop root-cost assumptions; exact over compiled graph.
"""
import bootstrap
import time
import z3 as z
from auth_lifecycle.schema import prepare,State,refs_json
from auth_lifecycle._reference_kernel import expand,is_goal
from independent import cost,action_set

class Incremental:
    def __init__(self,bundle,meter,scope='joint'):
        self.b=bundle;self.d,self.root=prepare(bundle['l0']);self.m=meter;self.scope=scope
        self.s=z.Solver();self.vars={};self.choices={};self.edges={}
    def encode(self,u):
        if u in self.vars:return self.vars[u]
        self.m.tick('smt_encode_nodes');v=z.Int('cost_'+str(len(self.vars)));self.vars[u]=v
        if not u.knowledge:self.s.add(v==-1);return v
        if is_goal(self.d,u.knowledge):self.s.add(v==cost(self.b,u.knowledge));return v
        rows=[];edges={}
        if u.remaining>0:
            for a in action_set(self.b,self.scope):
                groups,err=expand(self.d,u.knowledge,a)
                if err or not groups:continue
                cs={o:State(k,u.remaining-1) for o,k in groups.items()};edges[a]=cs
                vv=[self.encode(c) for c in cs.values()]
                mx=vv[0]
                for x in vv[1:]:mx=z.If(x>mx,x,mx)
                rows.append((a,z.If(z.And([x>=0 for x in vv]),mx,-1)))
        self.edges[u]=edges
        if not rows:self.s.add(v==-1)
        else:
            winner=rows[0][1]
            for _,x in rows[1:]:winner=z.If(z.Or(winner<0,z.And(x>=0,x<winner)),x,winner)
            self.s.add(v==winner)
        return v
    def solve(self,state=None):
        u=state or self.root;v=self.encode(u)
        self.s.push();self.s.add(z.Or(v==-1,v>=0));self.s.set(timeout=max(1,int((self.m.seconds-self.m.elapsed())*1000)))
        status=self.s.check();self.m.tick('smt_checks')
        if status!=z.sat:self.s.pop();return {'status':'INCONCLUSIVE','reason':str(status)}
        model=self.s.model();value=model.eval(v).as_long()
        def policy(s):
            h={'belief':refs_json(s.knowledge),'remaining':s.remaining}
            if is_goal(self.d,s.knowledge):return dict(h,kind='done')
            target=model.eval(self.vars[s]).as_long()
            for a,cs in sorted(self.edges[s].items()):
                values=[model.eval(self.vars[c]).as_long() for c in cs.values()]
                if min(values)>=0 and max(values)==target:return dict(h,kind='act',action=a,children={o:policy(c) for o,c in cs.items()})
            raise AssertionError('SMT policy extraction')
        out={'status':'UNKNOWN' if not u.knowledge else ('FEASIBLE' if value>=0 else 'IMPOSSIBLE_IN_MODEL'),'value':value if value>=0 else None,'policy':policy(u) if value>=0 else None,'solver':z.get_version_string()}
        self.s.pop();return out
