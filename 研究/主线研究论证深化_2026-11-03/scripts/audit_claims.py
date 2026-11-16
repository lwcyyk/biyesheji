from pathlib import Path
import sys,json,hashlib,argparse,itertools,time,platform,zipfile
from fractions import Fraction
from dataclasses import asdict
from copy import deepcopy

BASE=Path(__file__).resolve().parents[1];PROJECT=Path('D:/毕业设计/auth-lifecycle')
sys.dont_write_bytecode=True
sys.path.insert(0,str(PROJECT/'src'))
from auth_lifecycle.a import compiler,candidate,runtime,audit,joint_reference
from auth_lifecycle import reference as ri,certificates,checker
from auth_lifecycle.b import search,baselines,reference as br,fixtures as bf,checker as bc
from auth_lifecycle.b.model import prepare as bp,Work,Result
from auth_lifecycle.b import _kernel as bk
from auth_lifecycle.schema import prepare as lp,canonical
from auth_lifecycle.a.model import properties
from auth_lifecycle.a import fixtures as af
from auth_lifecycle.semantics import branches,observe
from diagnostic_inputs import diagnostic_cases

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def enum_fallback(spec,limit=1_000_000):
 """Supplemental comparator: all masks, independent reference BFS, common checker.
 Not a new algorithm and not a modification/relabel of historical B-B.
 """
 m=bp(spec);names=sorted(m['paths']);work=Work(limit);best=None;records=[]
 for mask in range(1<<len(names)):
  config=[p for i,p in enumerate(names) if mask&(1<<i)]
  work.tick('fallback_masks');refs,initial,setup,metrics=bk.configuration(m,config)
  if refs:continue
  plans={}
  for sid,sc in sorted(m['scenarios'].items()):
   route=br.plan(m,config,sc,initial,work)
   if route is None:break
   plans[sid]=route
  if len(plans)!=len(m['scenarios']):continue
  delivery={'configuration':config,'setup':setup,'plans':plans};checked=bc.check_delivery(m,delivery)
  if checked['verdict']!='ACCEPTED':raise RuntimeError(checked)
  key=(checked['metrics']['G'],config)
  records.append({'configuration':config,'G':key[0],'checked':checked['verdict']})
  if best is None or key<best[0]:best=(key,delivery,checked['metrics'])
 if best is None:return {'status':'IMPOSSIBLE','scope':'supplemental complete finite enumeration','records':records,'stats':work.counts}
 return {'status':'FEASIBLE','configuration':best[1]['configuration'],'delivery':best[1],'metrics':best[2],'records':records,'stats':work.counts,'scope':'supplemental complete finite enumeration; shares reference BFS/kernel, not independent of R-B'}

def algebra(out):
 rows=[];bad=[]
 # Same positive denominators and m>=1: integer pair-count transform strictly increases.
 for n in range(1,17):
  for m1,m2,c in itertools.product(range(1,n+1),range(1,n+1),range(1,9)):
   a1=Fraction(n*(n-1)-m1*(m1-1),2*c);a2=Fraction(n*(n-1)-m2*(m2-1),2*c)
   b1=Fraction(n-m1,c);b2=Fraction(n-m2,c)
   sign=lambda x:(x>0)-(x<0)
   ok=sign(a1-a2)==sign(b1-b2)
   rows.append([n,m1,m2,c,ok])
   if not ok:bad.append(rows[-1])
 dump(out/'algebra/equal_cost.json',{'range':{'n':[1,16],'m':[1,'n'],'c':[1,8]},'rows':rows,'disagreements':bad})
 witness={'n':5,'fine':{'m':1,'cost':3,'A_score':'10/3','BA_score':'4/3'},'coarse':{'m':3,'cost':2,'A_score':'7/2','BA_score':'1'},'A_choice':'coarse','BA_choice':'fine'}
 dump(out/'algebra/unequal_cost.json',witness)
 # GBS paper's expected version-space reduction differs on multivalued uniform tests.
 gbs={'uniform_hypotheses':6,'query_a_branch_sizes':[3,3],'query_z_branch_sizes':[3,1,1,1],
      'existing_minimax_gain':{'a':3,'z':3},'expected_mass_reduction':{'a':'1/2','z':'2/3'},
      'same_tiebreak':'lexicographic: a before z','existing_choice':'a','expected_mass_GBS_choice':'z',
      'scope':'formula witness only; no prior added to running algorithms'}
 dump(out/'algebra/GBS_nonidentity.json',gbs)
 return {'equal_cost_comparisons':len(rows),'disagreements':len(bad),'unequal_cost_witness':witness,'GBS_nonidentity':gbs}

def run_a(out):
 summaries=[]
 for name,source,expected,scope in diagnostic_cases():
  dump(out/'inputs'/f'{name}.json',source)
  start=time.perf_counter();c=compiler.compile_model(source);ct=time.perf_counter()-start
  if c.status!='COMPILED':raise RuntimeError((name,c.status,c.reason))
  checked=audit.check_compilation(c.bundle);r=ri.solve(c.bundle['l0'])
  results={};times={}
  for label,fn in [('A1',lambda:candidate.solve(c.bundle)),('B-A',lambda:candidate.solve(c.bundle,method='B-A')),('AB1',lambda:candidate.solve(c.bundle,feedback=True)),('B-AB',lambda:candidate.solve(c.bundle,feedback=False)),('R-J',lambda:joint_reference.solve(c.bundle))]:
   start=time.perf_counter();answer=fn();elapsed=time.perf_counter()-start
   ev=runtime.evaluate(c.bundle,answer)
   results[label]={'solver':asdict(answer),'evaluation':ev};times[label]=elapsed
  payload={'name':name,'scope':scope,'expected':expected,'compilation_audit':checked,'RI':asdict(r),'results':results}
  dump(out/'artifacts'/f'{name}.json',payload)
  dump(out/'timings'/f'{name}.json',{'compile_seconds':ct,'solve_seconds':times,'scope':'single run descriptive; no speed hypothesis'})
  ok=checked['verdict']=='ACCEPTED' and r.status.value==expected
  row={'name':name,'scope':scope,'expected':expected,'pass':bool(ok),'nodes':c.nodes,'methods':{}}
  for label,obj in results.items():
   a=obj['solver'];v=obj['evaluation'];root_action=(a['policy'] or {}).get('action')
   good=a['status']==expected and not v['safety_counterexamples']
   if expected=='FEASIBLE':good &= v['completion']==1
   row['pass'] &= bool(good)
   row['methods'][label]={'status':a['status'],'root_action':root_action,'Q':a['worst_requests'],'G':v.get('max_G'),
      'trace_G_values':sorted({t['G'] for t in v.get('traces',[])}),
      'completion':v['completion'],'unresolved':v.get('unresolved_obligations'),'side_effects':v.get('probe_side_effects'),
      'feedback_calls':a['stats'].get('feedback_calls',0),'B_work':a['stats'].get('B_work',0),'safety_counterexamples':len(v['safety_counterexamples'])}
  row['same_G_for_RJ_comparison']=len({x['G'] for x in row['methods'].values()})==1
  row['A_BA_policy_equal']=results['A1']['solver']['policy']==results['B-A']['solver']['policy']
  if scope=='INHERITED_REGRESSION':row['pass'] &= row['A_BA_policy_equal']
  if name=='A_different_ranking_equal_total':
   row['pass'] &= row['methods']['A1']['root_action']!=row['methods']['B-A']['root_action'] and row['methods']['A1']['Q']==row['methods']['B-A']['Q']==6
   row['pass'] &= row['methods']['A1']['side_effects']==1 and row['methods']['B-A']['side_effects']==0
  if name=='A_different_ranking_worse_total':row['pass'] &= row['methods']['A1']['Q']==8 and row['methods']['B-A']['Q']==6
  if name=='AB_ranking_changes_projection_sensitive':
   row['pass'] &= row['methods']['AB1']['root_action']!=row['methods']['B-AB']['root_action'] and row['methods']['AB1']['Q']==4 and row['methods']['B-AB']['Q']==5
  if name=='joint_planning_cheaper_than_early_configure':row['pass'] &= row['methods']['A1']['Q']==5 and row['methods']['R-J']['Q']==4 and row['same_G_for_RJ_comparison']
  summaries.append(row);print(name,expected,'PASS' if row['pass'] else 'FAIL', {k:v['Q'] for k,v in row['methods'].items()},flush=True)
 dump(out/'a_summary.json',summaries)
 return summaries

def run_b(out):
 inputs=[('local_shared',bf.local_only()),('static_signature',bf.static_groups())]
 # Retain both historical witnesses, selected by identifier, not regenerated random luck.
 for line in (PROJECT/'results/b/final02/structural.jsonl').read_text(encoding='utf-8').splitlines():
  obj=json.loads(line)
  if str(obj.get('case','')).endswith(('-034','-084')):
   spec=obj.get('input',obj.get('source',obj.get('model')))
   if spec is None:raise RuntimeError('Inspect structural format: '+str(obj.keys()))
   inputs.append((obj['case'],spec))
 if len(inputs)!=4:raise RuntimeError('Missing original B witnesses')
 summaries=[]
 for name,spec in inputs:
  dump(out/'inputs'/f'B_{name}.json',spec)
  values={};times={}
  for label,fn in [('B',lambda:asdict(search.solve(spec))),('B-B',lambda:asdict(baselines.solve(spec))),('R-B',lambda:asdict(br.solve(spec))),('B-B_enum_supplement',lambda:enum_fallback(spec))]:
   start=time.perf_counter();values[label]=fn();times[label]=time.perf_counter()-start
  dump(out/'artifacts'/f'B_{name}.json',values);dump(out/'timings'/f'B_{name}.json',times)
  row={'name':name,'methods':{k:{'status':v['status'],'G':(v.get('metrics') or {}).get('G'),'configuration':v.get('configuration')} for k,v in values.items()}}
  row['pass']=all(values[k]['status']=='FEASIBLE' and values[k]['configuration']==values['B']['configuration'] for k in ['B','R-B','B-B_enum_supplement'])
  row['expected_BB']='NO_BASELINE_SOLUTION' if 'structural' in name else 'FEASIBLE'
  row['pass'] &= values['B-B']['status']==row['expected_BB']
  row['pass'] &= values['B']['metrics']['G']==(1 if name=='local_shared' else 2)
  summaries.append(row);print('B',name,row['pass'],flush=True)
 dump(out/'b_summary.json',summaries);return summaries

def boundaries(out):
 source=next(s for n,s,e,k in diagnostic_cases() if n=='simple_acquisition');bundle=compiler.compile_model(source).bundle
 cases={
  'candidate_cutoff':asdict(candidate.solve(bundle,node_limit=0)),
  'compiler_cutoff':asdict(compiler.compile_model(source,node_limit=0)),
 }
 for filename in ['three_worlds.json','stay_finish.json','adaptive_probe.json']:
  s=json.loads((PROJECT/'examples'/filename).read_text(encoding='utf-8'))
  cases[filename]={'input':s,'RI':asdict(ri.solve(s))}
 s=cases['three_worlds.json']['input']
 status,cert,reason=certificates.produce(s)
 accepted=checker.check_impossibility(s,cert)
 pairs=[]
 for names in itertools.combinations(s['worlds'],2):
  t=deepcopy(s);t['initial']=[x for x in t['initial'] if x[0] in names]
  pairs.append({'worlds':names,'RI':asdict(ri.solve(t))})
 forged=deepcopy(cert);forged['context']['constraint_refs']=[]
 cases['three_world_certificate']={'certificate':cert,'producer_status':status,'check':asdict(accepted),'pairs':pairs,'tampered_check':asdict(checker.check_impossibility(s,forged))}
 # A one-step certificate is weaker than impossibility of an observation policy.
 s=cases['adaptive_probe.json']['input'];status,cert,_=certificates.produce(s,scope='no_common_immediate_completion')
 cases['immediate_vs_joint']={'producer_status':status,'certificate':cert,'check':asdict(checker.check_impossibility(s,cert)),'joint_status':ri.solve(s).status}
 t=deepcopy(cases['stay_finish.json']['input'])
 for world in t['worlds'].values():
  for node in world['states'].values():node['transitions'].pop('finish',None)
 cases['stay_only']={'input':t,'expected':'IMPOSSIBLE','RI':asdict(ri.solve(t))}
 t=cases['stay_finish.json']['input'];d,r=lp(t);obs=observe(d,r,'stay','unregistered-response')
 cases['unmodelled_observation']={'expected_boundary':'out_of_model_observation','boundary':obs.boundary,'knowledge_size':len(obs.knowledge)}
 # Deliberately force an unsafe policy through the existing diagnostic-only scorer.
 from auth_lifecycle.a import ablations
 s=af.side_effect(opaque=True,clean=False);b=compiler.compile_model(s).bundle
 diag=ablations.missing_obligation_abstraction(b,feedback=False)
 diag['controller_result']=asdict(diag['controller_result']);cases['omitted_obligation_negative']=diag
 # World-changing probes can enlarge property support, so gain is not pure information.
 s=af.acquisition(nuisance=2,horizon=5,requests=12)
 for w,m in s['worlds'].items():m['revocations']['z']['coverage']='all_material' if w.endswith('0') else 'refresh_only'
 s['initial']=['m0n0']
 af.probe(s,'spread',{w:'mixed' for w in s['worlds']})
 for w in s['worlds']:s['probes']['spread']['outcomes'][w][0]=[af.outcome(v,'mixed') for v in s['worlds']]
 b=compiler.compile_model(s).bundle;data,state=lp(b['l0']);children,errors=branches(data,state,'probe:spread')
 sigs=lambda state:{canonical(properties(s['worlds'][b['points']['/'.join(x)]['point']['world']])) for x in state.knowledge}
 n=len(sigs(state));m=max(len(sigs(c)) for c in children.values())
 cases['changing_properties']={'input':s,'errors':errors,'before_signatures':n,'max_after_signatures':m,'A_gain':n*(n-1)//2-m*(m-1)//2,'BA_gain':n-m,'scope':'legal raw successor diagnostic; no assumption of a static latent hypothesis'}
 dump(out/'boundaries.json',cases)
 good=accepted.verdict=='ACCEPTED' and len(cases['three_world_certificate']['certificate']['context']['world_subset'])==3
 good &= all(x['RI']['status']=='FEASIBLE' for x in pairs) and cases['three_world_certificate']['tampered_check']['verdict']=='REJECTED'
 good &= cases['immediate_vs_joint']['check']['verdict']=='ACCEPTED' and cases['immediate_vs_joint']['joint_status']=='FEASIBLE'
 good &= bool(diag['scorer']['safety_counterexamples']) and diag['scorer']['completion']==0
 good &= n==1 and m==4
 good &= cases['candidate_cutoff']['status']==cases['compiler_cutoff']['status']=='INCONCLUSIVE'
 good &= cases['stay_only']['RI']['status']=='IMPOSSIBLE' and cases['stay_finish.json']['RI']['status']=='FEASIBLE'
 good &= cases['unmodelled_observation']['boundary']=='out_of_model_observation'
 return {'pass':bool(good),'candidate_cutoff':cases['candidate_cutoff']['status'],'compiler_cutoff':cases['compiler_cutoff']['status'],'three_worlds':cases['three_worlds.json']['RI']['status'],'three_world_core':cases['three_world_certificate']['certificate']['context']['world_subset'],'changing_property_counts':[n,m]}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--replay-of',type=Path);args=ap.parse_args()
 out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
 old=json.loads((BASE/'baseline_hashes.json').read_text(encoding='utf-8'))['files']
 source_hash={str(p):sha(p) for p in sorted((BASE/'scripts').glob('*.py'))}
 with zipfile.ZipFile(out/'source_snapshot.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted((BASE/'scripts').glob('*.py')):z.write(p,'diagnostics/'+p.name)
  for p in sorted((PROJECT/'src').rglob('*.py')):z.write(p,'baseline_src/'+p.relative_to(PROJECT/'src').as_posix())
 dump(out/'environment.json',{'command':[sys.executable,*sys.argv],'python':sys.version,'platform':platform.platform(),'git_commit':None,'source_hashes':source_hash,'scope':'OFFLINE_DEVELOPMENT_AND_ARGUMENT_DIAGNOSTICS','formal_hypotheses':'NOT_TESTED'})
 summary={'algebra':algebra(out),'A':run_a(out),'B':run_b(out),'boundaries':boundaries(out)}
 changed=[p for p,v in old.items() if not Path(p).exists() or sha(Path(p))!=v]
 summary['preserved_files']=len(old);summary['changed_files']=changed
 summary['pass']=not changed and all(x['pass'] for x in summary['A']+summary['B']) and summary['algebra']['disagreements']==0 and summary['boundaries']['pass']
 dump(out/'summary.json',summary)
 if args.replay_of:
  compared=[];diff=[]
  for p in sorted(out.rglob('*.json')):
   rel=p.relative_to(out)
   if rel.parts[0]=='timings' or rel.name in ['environment.json','replay.json']:continue
   prior=args.replay_of/rel
   compared.append(str(rel))
   if not prior.exists() or prior.read_bytes()!=p.read_bytes():diff.append(str(rel))
  dump(out/'replay.json',{'files':compared,'differences':diff,'pass':not diff,'excluded':['timings','environment']})
  summary['pass'] &= not diff
 print('OVERALL',summary['pass'],flush=True)
 return 0 if summary['pass'] else 1
if __name__=='__main__':raise SystemExit(main())
