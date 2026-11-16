from pathlib import Path
import sys,json,itertools,math,hashlib
from copy import deepcopy
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE/'prototype'))
from common import Meter,Graph,State,terminal
from b_units import solve,check_lower_bound
from a_ab_search import drd_bound
from auth_lifecycle.b import fixtures as bf,reference as br
from auth_lifecycle.a import fixtures as af,compiler,ablations
from auth_lifecycle import reference as ri,certificates,checker
from dataclasses import asdict
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def triple_source():
 b=bf.base(['job','keep']);bf.env(b)
 for u in ['x','y','z','k']:bf.grant(b,u)
 for u in ['x','y','z']:bf.path(b,'job_'+u,'job',[u])
 bf.path(b,'keep','keep',['k']);b['scenarios']={'stop':{'local':[],'remote':['job'],'preserve':['keep']}};b['approved']+=['probe'];b['budgets'].update(requests=8,approvals=8);b['horizon']=3
 worlds={}
 for i,u in enumerate(['z','x','y']):
  m=deepcopy(b);m['revocations'][u]['coverage']='refresh_only';worlds['w'+str(i)]=m
 s={'schema':'auth-lifecycle-a/1','account':'alice','caller':'agent-client','worlds':worlds,'initial':list(worlds),'scenario':'stop','probes':{},'cleanups':{},'faults':{},'budget':{'requests':8,'approvals':8},'horizon':3}
 af.probe(s,'split',{'w0':'single','w1':'pair','w2':'pair'})
 return s
def main(out=None):
 out=Path(out) if out else BASE/'runs/mechanisms01';out.mkdir(parents=True,exist_ok=False);checks=[]
 # All 3-world / 3-plan incidence matrices with nonempty single-world plan sets.
 rows=[]
 for masks in itertools.product(range(1,8),repeat=3):
  pairs=all(masks[i]&masks[j] for i,j in itertools.combinations(range(3),2));common=masks[0]&masks[1]&masks[2]
  rows.append({'plan_masks':masks,'all_pairs_compatible':bool(pairs),'common_plan_mask':common,'higher_order_conflict':bool(pairs and not common)})
 dump(out/'all_343_plan_matrices.json',rows);checks.append({'name':'three_world_pairwise_failure','pass':sum(x['higher_order_conflict'] for x in rows)==6})
 s=triple_source();c=compiler.compile_model(s);g=Graph(c.bundle,Meter());lb,cert=drd_bound(g,g.root);opt=ri.solve(c.bundle['l0'])
 dump(out/'three_world_runtime.json',{'input':s,'lb':lb,'certificate':cert,'RI':asdict(opt)})
 checks.append({'name':'three_world_runtime','pass':cert is not None and cert['information_cost']==1 and lb==4 and opt.status.value=='FEASIBLE'})
 s2=deepcopy(s)
 for w,p in s2['probes']['split']['outcomes'].items():p[0][0]['to_world']='w0';p[0][0]['observation']='same-visible-label'
 c2=compiler.compile_model(s2);g2=Graph(c2.bundle,Meter());v2,cert2=drd_bound(g2,g2.root)
 dump(out/'dynamic_guard.json',{'input':s2,'bound':v2,'certificate':cert2,'RI':asdict(ri.solve(c2.bundle['l0']))})
 checks.append({'name':'state_change_disables_static_Drd','pass':cert2 is None})
 # Certificate tampering and a real positive independent check.
 m=bf.aliases();m['scenarios']['stop']={'local':[],'remote':['a'],'preserve':['b']}
 r=solve(m);valid=check_lower_bound(m,r['certificate'],Meter());bad=deepcopy(r['certificate']);bad['context']['approved']=[]
 tampered=check_lower_bound(m,bad,Meter());dump(out/'certificate_tamper.json',{'input':m,'result':r,'accepted':valid,'tampered':bad,'tampered_accepted':tampered})
 checks.append({'name':'certificate_context_tamper','pass':valid and not tampered})
 limited=solve(bf.local_only(4),meter=Meter(limit=0));dump(out/'cutoff.json',limited);checks.append({'name':'budget_cutoff_not_impossible','pass':limited['status']=='INCONCLUSIVE'})
 source=af.side_effect(opaque=True,clean=False);compiled=compiler.compile_model(source);diag=ablations.missing_obligation_abstraction(compiled.bundle,feedback=False);diag['controller_result']=asdict(diag['controller_result']);dump(out/'omitted_obligation.json',diag)
 checks.append({'name':'omitted_obligation_rejected','pass':diag['audit']['verdict']=='REJECTED' and diag['scorer']['completion']==0})
 dump(out/'summary.json',{'checks':checks,'pass':all(x['pass'] for x in checks),'formal':'NOT_TESTED','scope':'343 incidence matrices plus named finite checks; not sampled independent families'})
 print(json.dumps(checks,ensure_ascii=False,indent=2))
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--out');args=ap.parse_args();main(args.out)
