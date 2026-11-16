"""Independent R-J12 and proof checker. No candidate graph/search import.

Shares only the old raw-table interpreter and schema with the checking side.
Compiler/plant correctness is separately checked by the preserved source audit.
"""
import bootstrap
from auth_lifecycle._reference_kernel import expand,is_goal,is_safe
from auth_lifecycle.schema import State,refs_json,digest,prepare
from functools import lru_cache
import math,time

def cost(bundle,k):
    return max((bundle['source']['budget']['requests']-bundle['l0']['worlds'][w]['states'][n]['budget']['requests'] for w,n in k),default=math.inf)
def action_set(bundle,scope):
    return [a for a in bundle['l0']['actions'] if scope=='joint' or bundle['catalog'][a]['kind']!='probe']
def exact(bundle,state=None,*,scope='joint',meter=None,cache=True):
    data,root=prepare(bundle['l0']);root=state or root;memo={}
    def rec(k,r):
        key=(k,r)
        if cache and key in memo:
            if meter:meter.tick('reference_cache_hits')
            return memo[key]
        if meter:meter.tick('reference_states')
        h={'belief':refs_json(k),'remaining':r}
        if not k:return ('UNKNOWN',math.inf,None)
        if is_goal(data,k):return ('FEASIBLE',cost(bundle,k),dict(h,kind='done'))
        best=math.inf;p=None
        if r>0:
            for a in sorted(action_set(bundle,scope)):
                groups,err=expand(data,k,a)
                if err or not groups:continue
                rows={o:rec(c,r-1) for o,c in groups.items()}
                v=max(x[1] for x in rows.values())
                if v<best:
                    best=v;p=dict(h,kind='act',action=a,children={o:x[2] for o,x in rows.items()})
        ans=('FEASIBLE' if p else 'IMPOSSIBLE_IN_MODEL',best,p);memo[key]=ans;return ans
    st,v,p=rec(root.knowledge,root.remaining)
    return {'status':st,'value':None if math.isinf(v) else v,'policy':p,'reference_states':len(memo)}

class Checker:
    def __init__(self,bundle,meter=None):
        self.b=bundle;self.d=bundle['l0'];self.m=meter;self.digest=digest(self.d);self.low_cache={}
    def tick(self,label):
        if self.m:self.m.tick(label)
    def post(self,s,a,o):
        self.tick('independent_post_calls')
        if not s.knowledge or s.remaining<=0:return None
        groups,errs=expand(self.d,s.knowledge,a)
        if errs or o not in groups:return None
        return State(groups[o],s.remaining-1)
    def replay(self,template,s):
        """Policy template is re-bound to ALL current successors; no old K trusted."""
        self.tick('witness_check_nodes')
        h={'belief':refs_json(s.knowledge),'remaining':s.remaining}
        if not s.knowledge:return 'INVALID',None,None,'empty K'
        if not isinstance(template,dict):return 'INCONCLUSIVE',None,None,'missing proof'
        if template.get('kind')=='done':
            if not is_goal(self.d,s.knowledge):return 'INVALID',None,None,'goal/strict obligation violation'
            return 'VALID',dict(h,kind='done'),cost(self.b,s.knowledge),'checked'
        if template.get('kind')!='act' or s.remaining<=0:return 'INVALID',None,None,'horizon/proof kind'
        a=template.get('action');groups,errs=expand(self.d,s.knowledge,a)
        if errs or not groups:return 'INVALID',None,None,'guard/approval/budget/nonempty Post'
        children=template.get('children',{});new={};values=[]
        for o,k in groups.items():
            if o not in children:return 'INCONCLUSIVE',None,None,'new observation needs strategy'
            st,p,v,why=self.replay(children[o],State(k,s.remaining-1))
            if st!='VALID':return st,None,None,why
            new[o]=p;values.append(v)
        return 'VALID',dict(h,kind='act',action=a,children=new),max(values),'checked'
    def refutation(self,p,s):
        self.tick('refutation_check_nodes')
        if not s.knowledge:return 'INCONCLUSIVE','empty K is UNKNOWN'
        if is_goal(self.d,s.knowledge):return 'INVALID','new state is goal'
        if not isinstance(p,dict):return 'INCONCLUSIVE','missing refutation'
        if p.get('kind')=='horizon':
            return ('VALID','zero horizon') if s.remaining==0 else ('INCONCLUSIVE','old horizon not applicable')
        if p.get('kind')!='all_controls':return 'INCONCLUSIVE','unknown refutation'
        if s.remaining<=0:return 'VALID','new zero horizon'
        entries=p.get('actions',{})
        for a in action_set(self.b,'control'):
            e=entries.get(a)
            if not isinstance(e,dict):return 'INCONCLUSIVE','uncovered control'
            groups,err=expand(self.d,s.knowledge,a)
            if err:continue  # independently re-established blocker
            if e.get('kind')!='losing':return 'INCONCLUSIVE','previously blocked action newly enabled'
            o=e.get('observation')
            if o not in groups:return 'INCONCLUSIVE','old adverse branch disappeared'
            st,why=self.refutation(e.get('child'),State(groups[o],s.remaining-1))
            if st!='VALID':return ('INCONCLUSIVE',why) # refuted branch alone does not refute whole claim
        return 'VALID','every control blocked or has checked losing successor'
    def lower(self,s,scope='joint'):
        """Perfect-information AND favourable-outcome relaxation, TOTAL Q.
        This is a fresh admissible bound, not a transported numeric assertion.
        """
        def one(ref,r):
            key=(ref,r,scope)
            if key in self.low_cache:return self.low_cache[key]
            self.tick('independent_lower_states');k=frozenset([ref])
            if is_goal(self.d,k):v=cost(self.b,k)
            elif r==0 or not is_safe(self.d,ref):v=math.inf
            else:
                vals=[]
                for a in action_set(self.b,scope):
                    groups,err=expand(self.d,k,a)
                    if not err:vals.extend(one(x,r-1) for g in groups.values() for x in g)
                v=min(vals,default=math.inf)
            self.low_cache[key]=v;return v
        return max((one(x,s.remaining) for x in s.knowledge),default=math.inf)
    def check_certificate(self,cert,s):
        if cert.get('schema')!='SCCP/1' or cert.get('model_digest')!=self.digest:return 'INVALID','version/model binding'
        if cert.get('scope')!='control_only_bounded_completion' or cert.get('objective')!='total_Q':return 'INVALID','scope/objective'
        refs=['account','approval','budgets','native_effects','all_observations','strict_obligations','remaining_steps','version']
        if cert.get('constraint_refs')!=refs:return 'INVALID','constraint references'
        if cert.get('root')!={'belief':refs_json(s.knowledge),'remaining':s.remaining}:return 'INVALID','root binding'
        if cert.get('status')=='FEASIBLE':
            st,_,v,why=self.replay(cert.get('policy'),s)
            if st=='VALID' and v!=cert.get('value'):return 'INVALID','wrong reported cost'
            return st,why
        if cert.get('status')=='IMPOSSIBLE_IN_MODEL':return self.refutation(cert.get('refutation'),s)
        return 'INCONCLUSIVE','no proof'
    def transfer(self,cert,parent,a,o,child,*,bound=None):
        start=time.perf_counter();actual=self.post(parent,a,o)
        if actual!=child:return {'verdict':'INVALID','reason':'full Post mismatch / dropped successor'}
        st,why=self.check_certificate(cert,parent)
        if st!='VALID':return {'verdict':st,'reason':'old certificate: '+why}
        new=dict(cert,root={'belief':refs_json(child.knowledge),'remaining':child.remaining})
        if cert['status']=='FEASIBLE':
            p=cert['policy']
            if p.get('action')==a:p=p.get('children',{}).get(o)
            st,p,v,why=self.replay(p,child)
            if st=='VALID':new.update(policy=p,value=v)
        else:st,why=self.refutation(cert['refutation'],child)
        result={'verdict':st,'reason':why,'seconds':time.perf_counter()-start}
        if st=='VALID':result['certificate']=new
        if bound is not None:
            fresh=self.lower(child,'control')
            result['bound_verdict']='VALID' if fresh>=bound else 'INCONCLUSIVE'
            if st=='VALID' and new['status']=='FEASIBLE' and new['value']<bound:result['bound_verdict']='INVALID'
            result['fresh_lower']=fresh if math.isfinite(fresh) else None
        return result

