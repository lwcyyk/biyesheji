"""Task-relative value cells + counterexample-guided singleton refinement.
Generic certificate abstraction control deliberately receives the same mechanism.
"""
import bootstrap
from kernel import State

class Cells:
    def __init__(self,g,checker):self.g=g;self.ck=checker;self.cells={};self.log=[];self.refined=set()
    def key(self,s):
        self.g.meter.tick('abstraction_summary_states')
        contexts=[]
        for ref in s.knowledge:
            p=self.g.point(ref);n=self.g.d['worlds'][ref[0]]['states'][ref[1]]
            contexts.append((n['account'],tuple(sorted(p['budget'].items())),tuple(p['approved']),tuple(p['sessions']),tuple(p['configuration'] or []),tuple(p['stopped'])))
        return s.remaining,tuple(sorted(set(contexts)))
    def add(self,s,value,policy):
        # Equality with an admissible lower bound proves this member optimal.
        if self.ck.lower(s)!=value:return
        key=self.key(s);self.cells.setdefault(key,[]).append((s,value,policy))
    def find(self,s):
        key=self.key(s)
        if s in self.refined:return None
        for old,v,p in self.cells.get(key,[]):
            self.g.meter.tick('abstraction_merge_attempts')
            union=State(old.knowledge|s.knowledge,s.remaining)
            eligibility=set(self.g.allowed(s))
            if eligibility!=set(self.g.allowed(old)) or eligibility!=set(self.g.allowed(union)):
                self.log.append({'status':'REFINED','reason':'winning-action eligibility differs','refinement':'singleton concrete belief'});self.refined.add(s);return None
            st,up,uv,why=self.ck.replay(p,union)
            if st!='VALID' or uv!=v or self.ck.lower(s)!=v:
                self.log.append({'status':'REFINED','reason':why if st!='VALID' else 'member value bound differs','refinement':'singleton concrete belief'});self.refined.add(s);return None
            st,lifted,lv,why=self.ck.replay(up,s)
            if st!='VALID' or lv!=v:raise AssertionError('union policy lifting mismatch')
            self.g.meter.tick('abstraction_hits');self.log.append({'status':'MERGED','value':v,'union_points':len(union.knowledge),'safe_actions':len(eligibility),'reason':'union witness and both member lower bounds match'})
            return v,lifted
        return None

