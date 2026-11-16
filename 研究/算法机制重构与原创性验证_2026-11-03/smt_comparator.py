"""Direct Z3 Optimize encoding of the original monotone B model, no path-mask
 generator or candidate solve call. Same min(G, lexical configuration) objective.
 Ordinary solver internals are not an independent UNSAT proof certificate.
 """
from pathlib import Path
import sys,json,time,subprocess,argparse,hashlib
BASE=Path(__file__).resolve().parent;sys.path[:0]=[str(BASE/'prototype'),str(BASE/'.deps')]
from resource_guard import install,peak_memory
from common import Meter,Cutoff
from auth_lifecycle.b import model,checker

def solve(spec,meter):
 import z3 as z
 m=model.prepare(spec);o=z.Optimize();o.set(priority='lex');names=sorted(m['paths']);x={p:z.Bool('path_'+p) for p in names}
 used={g:z.Or([x[p] for p in names if g in m['paths'][p]['grants']]) for g in m['credentials']}
 envs={e:z.Or([x[p] for p in names if m['paths'][p]['environment']==e]) for e in m['environments']}
 units={u:z.Or([used[g] for g in v['affects']]) for u,v in m['revocations'].items()}
 def charge(flag,op,field):return z.If(flag,op[field],0)
 def allowed(flag,op):
  if op['approval'] is not None and op['approval'] not in m['approved']:o.add(z.Not(flag))
 setup_q=[];setup_a=[]
 for flag,op in [(used[g],v['issue']) for g,v in m['credentials'].items()]+[(envs[e],v['create']) for e,v in m['environments'].items()]+[(x[p],m['paths'][p]['delegate']) for p in names]:
  allowed(flag,op);setup_q.append(charge(flag,op,'requests'));setup_a.append(charge(flag,op,'approvals'))
 for t in m['tasks']:o.add(z.Or([x[p] for p in names if m['paths'][p]['task']==t]))
 for p in names:
  route=m['paths'][p];task=m['tasks'][route['task']];scope={s for g in route['grants'] for s in m['credentials'][g]['scope']}
  if any(m['credentials'][g]['account']!=task['account'] for g in route['grants']) or not set(task['permissions'])<=scope:o.add(z.Not(x[p]))
 G=z.Sum([z.If(v,1,0) for v in units.values()]);o.add(G<=m['budgets']['units'])
 o.add(z.Sum([z.If(envs[e],1,0) for e,v in m['environments'].items() if v['kind']=='isolated'])<=m['budgets']['isolated_environments'])
 plans={}
 for sid,sc in m['scenarios'].items():
  actions={};ops={}
  for u,v in m['revocations'].items():
   if v['coverage']=='all_material' and v['revoke'] is not None:
    aid='revoke:'+u;actions[aid]=z.Bool(sid+'_'+aid);ops[aid]=v['revoke'];o.add(z.Implies(actions[aid],units[u]))
  for e,v in m['environments'].items():
   if not v['controlled'] or v['stop'] is None:continue
   if v['kind']=='isolated':
    aid='close:'+e;actions[aid]=z.Bool(sid+'_'+aid);ops[aid]=v['stop'];o.add(z.Implies(actions[aid],envs[e]))
   elif v['kind']=='broker':
    for t in m['tasks']:
     aid=f'gate:{e}:{t}';actions[aid]=z.Bool(sid+'_'+aid);ops[aid]=v['stop'];o.add(z.Implies(actions[aid],z.Or([x[p] for p in names if m['paths'][p]['environment']==e and m['paths'][p]['task']==t])))
  for aid,op in ops.items():allowed(actions[aid],op)
  def hit(p,native=False):
   route=m['paths'][p];parts=[actions['revoke:'+u] for u,v in m['revocations'].items() if 'revoke:'+u in actions and set(route['grants'])&set(v['affects'])]
   if not native:
    for a in ['close:'+route['environment'],f"gate:{route['environment']}:{route['task']}"]:
     if a in actions:parts.append(actions[a])
   return z.Or(parts)
  for t in sc['remote']:
   for p in names:
    if m['paths'][p]['task']==t:o.add(z.Implies(x[p],hit(p,True)))
  for t in sc['local']:
   for p in names:
    if m['paths'][p]['task']==t:o.add(z.Implies(x[p],hit(p)))
  for t in sc['preserve']:o.add(z.Or([z.And(x[p],z.Not(hit(p))) for p in names if m['paths'][p]['task']==t]))
  o.add(z.Sum(setup_q+[charge(actions[a],ops[a],'requests') for a in actions])<=m['budgets']['requests'])
  o.add(z.Sum(setup_a+[charge(actions[a],ops[a],'approvals') for a in actions])<=m['budgets']['approvals'])
  o.add(z.Sum([z.If(v,1,0) for v in actions.values()])<=m['horizon']);plans[sid]=actions
 o.minimize(G)
 # Encode the sorted configuration list padded by zero. A strict prefix sorts first.
 for pos in range(len(names)):
  terms=[]
  for i,p in enumerate(names):
   before=z.Sum([z.If(x[q],1,0) for q in names[:i]])
   terms.append(z.If(z.And(x[p],before==pos),i+1,0))
  o.minimize(z.Sum(terms))
 meter.tick('encoded_constraints',len(o.assertions()));remaining=max(1,int((30-meter.elapsed())*1000));o.set(timeout=remaining)
 status=o.check();meter.tick('solver_return')
 if status==z.unknown:return {'status':'INCONCLUSIVE','reason':o.reason_unknown(),'solver':z.get_version_string()}
 if status==z.unsat:return {'status':'IMPOSSIBLE','solver':z.get_version_string(),'proof':'Z3 result, no exported UNSAT proof; cross-checked with R-B'}
 mm=o.model();C=[p for p in names if z.is_true(mm.eval(x[p]))]
 grants=sorted({g for p in C for g in m['paths'][p]['grants']});en=sorted({m['paths'][p]['environment'] for p in C})
 delivery={'configuration':C,'setup':['issue:'+g for g in grants]+['create:'+e for e in en]+['delegate:'+p for p in C],
           'plans':{sid:sorted(a for a,v in aa.items() if z.is_true(mm.eval(v))) for sid,aa in plans.items()}}
 ck=checker.check_delivery(m,delivery);meter.tick('independent_check')
 if ck['verdict']!='ACCEPTED':raise RuntimeError(ck)
 return {'status':'FEASIBLE','delivery':delivery,'metrics':ck['metrics'],'check':ck,'solver':z.get_version_string()}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input');ap.add_argument('--out');a=ap.parse_args()
 if a.input:
  guards=install();loading=time.perf_counter();import z3;library_seconds=time.perf_counter()-loading
  meter=Meter();spec=json.loads(Path(a.input).read_text(encoding='utf-8'))
  try:row=solve(spec,meter)
  except Exception as e:row={'status':'INCONCLUSIVE' if isinstance(e,Cutoff) else 'ERROR','reason':str(e)}
  row.update(seconds=meter.elapsed(),cpu_seconds=time.process_time()-meter.cpu_start,memory=peak_memory(),guards=guards,library_initialization_seconds=library_seconds)
  if meter.elapsed()>30:row['status']='TIMEOUT'
  Path(a.out).write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8');return
 out=Path(a.out) if a.out else BASE/'runs/smt02';out.mkdir(parents=True,exist_ok=False)
 files=sorted((BASE/'runs/final02/inputs').glob('B_*.json'));rows=[]
 (out/'registry.json').write_text(json.dumps({'version':'Z3-4.15.4.0-direct-B/1','inputs':[p.name for p in files],'created_before_runs':True,'objective':'lex(min G, sorted configuration list)','constraints':'exact monotone model, same budgets/approvals; no additional native API','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2))
 for p in files:
  dest=out/p.name
  try:
   r=subprocess.run([sys.executable,__file__,'--input',str(p),'--out',str(dest)],capture_output=True,text=True,timeout=32,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
   x=json.loads(dest.read_text(encoding='utf-8')) if dest.exists() else {'status':'ERROR','reason':r.stderr}
  except subprocess.TimeoutExpired:x={'status':'TIMEOUT'};dest.write_text(json.dumps(x))
  baseline=json.loads((BASE/'runs/final02/raw'/(p.stem+'_R-B.json')).read_text(encoding='utf-8'))
  good=x['status']==baseline['status']
  if x['status']=='FEASIBLE':good &= x['metrics']['G']==baseline['result']['metrics']['G'] and x['delivery']['configuration']==baseline['result']['configuration']
  rows.append({'case':p.stem,'status':x['status'],'G':x.get('metrics',{}).get('G'),'seconds':x.get('seconds'),'pass':bool(good)})
  print(p.stem,x['status'],good,flush=True)
 (out/'summary.json').write_text(json.dumps({'rows':rows,'pass':bool(rows) and all(x['pass'] for x in rows)},indent=2),encoding='utf-8')
if __name__=='__main__':main()
