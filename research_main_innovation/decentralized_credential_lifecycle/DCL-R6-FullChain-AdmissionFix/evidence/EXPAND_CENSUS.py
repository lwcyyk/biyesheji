"""Enumerate further mandatory file lower bounds and all source write sites."""
from pathlib import Path
import ast,hashlib,json
O=Path(__file__).resolve().parent.parent;E=O/'evidence';S=E/'FROZEN_RA_ORIGINALS'
def load(n):return json.loads((S/'inputs'/(n+'.json')).read_bytes())
def put(n,x):
 with(E/n).open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
old=json.loads((E/'EVIDENCE_CATALOG.json').read_bytes())
rows=[r.copy() for r in old['rows'] if r['origin']=='STATIC_PATH_WITNESS']
def add(path,producer,requirement):
 rows.append({'evidence_id':f'FULL-PATH-{len(rows):04}','producer':producer,'source_path':'<new-batch>/'+path,'relative':path,
  'sha256':None,'size':None,'required_by':requirement,'admin_required':True,'native_required':True,'replay_required':True,
  'independently_verified':'STATIC_PRODUCER_PATH_ONLY; bytes UNRUN','equivalence_class':'UNPROVEN_CONTENT_EQUIVALENCE','origin':'STATIC_PATH_WITNESS'})
for job in load('c09_contract')['jobs']:
 for i in range(len(job['events'])):add(f"out/c09_tests/{job['case_id']}/{i:03}.json",'c09_regression.run_suite','C09H event raw replay')
 add(f"out/c09_tests/{job['case_id']}/oracle.json",'c09_regression.run_suite','C09H immediate oracle')
for i,job in enumerate(load('root_ipc_contract')['jobs']):add(f'inputs/root_private/ipc_case_{i:03}.json','root_ipc_regression.run_suite','RootIPC raw oracle')
for i,job in enumerate(load('boot_contract')['jobs']):add(f'inputs/root_private/boot/bc_case_{i:03}.json','boot_continuity_regression.run_suite','BC raw oracle')
for job in load('safety_contract')['jobs']:
 for n in ['ledger.bin','lifecycle.json','trace.main.jsonl','CLOSED.json','checker_observation.json']:
  add(f"out/safety/{job['case_id']}/{n}",'range_fixtures.run_suite','S34 raw ledger/trace/checker replay')
for i,job in enumerate(load('ledger_gate_contract')['jobs']):
 for n in ['visits.bin','visits.bin.intent.json','visits.bin.journal.jsonl']:
  if n=='visits.bin.intent.json' and job['kind']=='missing_evidence':continue
  add(f'inputs/root_private/boot/ledger_gate/{i:03}/{n}','ledger_gate_regression.run_suite','Ledger anomaly raw native-format specimen')
 add(f'inputs/root_private/boot/ledger_case_{i:03}.json','ledger_gate_regression.run_suite','Ledger descriptor/subject/oracle binding')
f1=['SMOKE_UNKNOWN','RELEASE_EMPTY','BRANCH_UNKNOWN']+['M_'+m for m in ['double_child','drop_rho','drop_hist','drop_dedup','stale_cache','reset_budget','ready_confusion','rollback','relabel_origin']]+['POST_TAKEOVER_B','CHAIN','RECOVERY_ABORT']
for name in f1:
 add('out/generated_inputs/run_s1/F1/'+name+'.json','run_batch.run','F1 frozen input identity')
 add('out/reports/run_s1/F1/'+name+'.json','run_batch.run','F1 baseline/mutation/replay output')
add('out/reports/run_s1/F1/KEY_AUTH_TABLE.json','run_batch.run','KEY finite predicates')
fixtures=['COST1','CE5_FULL','COMP_SAME_X','EMPTY_POST_INVALID','PARTIAL_POST_INVALID','OPEN_UNKNOWN','NONUNIFORM','REAL_QUERY_COST','ZERO_INTERNAL','PREFIX_BAD','VISIBLE_COST','QUOTA_MODE','MISSING_OBSERVATION']
for name in fixtures+[f'G64_{i:02}' for i in range(64)]:
 add('out/generated_inputs/run_s1/F4/'+name+'.json','compare.save_input','F4 input identity')
 add('out/reports/run_s1/F4/'+name+'.json','compare.check_case','F4 reference/DP/compression/witness replay')
for name,mutant in [('COST1','stagewise_max'),('CE5_FULL','drop_mode'),('EMPTY_POST_INVALID','empty_post'),('PARTIAL_POST_INVALID','empty_post'),('OPEN_UNKNOWN','ignore_unknown'),('NONUNIFORM','worldwise'),('REAL_QUERY_COST','zero_query_cost'),('PREFIX_BAD','ignore_prefix'),('QUOTA_MODE','drop_permission'),('MISSING_OBSERVATION','omit_observation')]:
 add('out/reports/run_s1/F4_MUTANTS/'+name+'__'+mutant+'.json','compare.mutant_case','F4 mutant counterexample output')
assert len(rows)==len({r['relative'] for r in rows})==1082,len(rows)
put('EXPANDED_FULLCHAIN_LOWER_WITNESS.json',{'schema':'FC-MANDATORY-LOWER-WITNESS/2','raw_files_lower':len(rows),
 'native_members_lower':len(rows)+1,'admin_excess_lower':len(rows)-256,'native_excess_lower':len(rows)+1-257,
 'scope':'Successful full calibration and F1/F4 completed planned domain; not an actual runtime manifest and not an upper bound',
 'calibration_without_models_lower':len(rows)-195,'excluded':'Other fixed inputs, tickets, service startup/timing/logs, exact registry, snapshots, qualified receipts, waits, locks, errors, temporary files, manifests and ZIPs',
 'rows':rows})
sites=[]
for p in sorted((S/'src').glob('*.py')):
 source=p.read_text(encoding='utf-8-sig');tree=ast.parse(source)
 for n in ast.walk(tree):
  if isinstance(n,ast.Call):
   name=ast.unparse(n.func)
   if name.split('.')[-1] in ['write','put','atomic','_root_write','publish','open','mkdir','makedirs','replace','rename','writestr','writelines','write_bytes','write_text','mkfifo','symlink','link']:
    sites.append({'producer':p.name,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'line':n.lineno,'call':ast.unparse(n),
     'cardinality':'NEEDS_CALLPATH_AND_BRANCH_UPPER_ANALYSIS','content_sha256':None,'role':'Source-site census includes reads and aliases; use semantic callpath before counting'})
put('PRODUCER_SITE_CENSUS.json',{'sites':sites,'count':len(sites),'cardinality_closed':False,'upper_bound':None})
print(json.dumps({'full_mandatory_lower':1082,'native_lower':1083,'calibration_lower':887,'producer_sites':len(sites)}))
