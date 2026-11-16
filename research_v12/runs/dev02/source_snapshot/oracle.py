"""Full native B + uniform control-policy completion. No B2Select adapter."""
import bootstrap
from copy import deepcopy
from dataclasses import asdict
from auth_lifecycle.a.model import adjusted
from auth_lifecycle.a._plant_reference import physical
from auth_lifecycle.b import reference as rb
from auth_lifecycle.b import checker as bcheck
from auth_lifecycle.b.model import prepare as prepare_b
from auth_lifecycle.schema import digest
from b_units import solve as b2,SharedWork
from kernel import control_solve
import math,time

class FullB:
    def __init__(self,g,checker,method='B2'):
        self.g=g;self.checker=checker;self.method=method;self.cache={};self.native_cache={};self.transfers=[];self.native_results=[]
    def native(self,s):
        g=self.g;preferred=[]
        for ref in sorted(s.knowledge):
            p=g.point(ref);m=adjusted(g.b['source'],p)
            if p['configuration'] is None:
                m['horizon']=min(m['horizon'],max(0,s.remaining-1));key=('setup',digest(m))
            else:
                m=deepcopy(g.b['source']['worlds'][p['world']]);m['approved']=list(p['approved'])
                state=physical(g.b['source'],p);state=(*state[:5],min(state[5],s.remaining))
                key=('residual',digest(m),tuple(p['configuration']),state)
            if key in self.native_cache:g.meter.tick('native_exact_cache_hits');ans=self.native_cache[key]
            else:
                g.meter.tick('native_B_calls');t=time.perf_counter()
                if p['configuration'] is None:
                    if self.method=='B4':
                        from b4 import solve
                        ans=solve(m,g.meter)
                    else:ans=b2(m,meter=g.meter,method='GENERIC_BB')
                    if ans['status']=='FEASIBLE':
                        ck=bcheck.check_delivery(m,ans['delivery'],work=SharedWork(g.meter))
                        if ck['verdict']!='ACCEPTED':raise AssertionError(ck)
                else:
                    route=rb.plan(prepare_b(m),p['configuration'],m['scenarios'][g.b['source']['scenario']],state,SharedWork(g.meter))
                    ans={'status':'FEASIBLE' if route is not None else 'IMPOSSIBLE','configuration':p['configuration'],'residual_plan':route}
                g.meter.tick('native_B_completed');self.native_cache[key]=ans
                self.native_results.append({'query':digest(str(key)),'status':ans['status'],'seconds':time.perf_counter()-t,'configured':p['configuration'] is not None})
            # Per-world solution is advisory ONLY. It never authorizes a move.
            c=ans.get('configuration')
            if c:
                preferred.extend(a for a,x in g.b['catalog'].items() if x['kind']=='configure' and x['configuration']==c)
        return preferred
    def solve(self,s,receipt=None,enable=False):
        if s in self.cache:self.g.meter.tick('B_exact_cache_hits');return self.cache[s]
        if enable and receipt:
            parent,a,o,cert=receipt
            t=time.perf_counter();r=self.checker.transfer(cert,parent,a,o,s)
            self.g.meter.tick('transfer_'+r['verdict']);self.transfers.append({'action':a,'observation':o,'verdict':r['verdict'],'reason':r['reason'],'seconds':time.perf_counter()-t})
            if r['verdict']=='VALID':
                new=r['certificate']
                if new['status']=='IMPOSSIBLE_IN_MODEL' or self.checker.lower(s,'control')==new['value']:
                    self.g.meter.tick('B_proof_reuses');self.cache[s]=new;return new
        self.g.meter.tick('full_B_calls');t=time.perf_counter();preferred=self.native(s)
        ans=control_solve(self.g,s,preferred)
        verdict,why=self.checker.check_certificate(ans,s)
        if verdict!='VALID':raise AssertionError(('new B certificate failed',verdict,why))
        self.g.meter.tick('new_B_certificates_checked');ans['build_seconds']=time.perf_counter()-t
        self.cache[s]=ans;return ans
