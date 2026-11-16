"""Immutable-history and local research delivery verification only."""
from pathlib import Path
import hashlib,json,re,time,zipfile
from datetime import datetime,timezone
O=Path(__file__).resolve().parent.parent;P=O.parent;E=O/'evidence';I=Path(r'D:\毕业设计\DCL-R6-isolated-verification');tick=time.perf_counter()
NAV=['CURRENT_VERDICT.md','NEXT_ACTION.md','README.md','DECISION_HISTORY.md']
def h(p):
 d=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):d.update(b)
 return d.hexdigest()
def j(p):return json.loads(p.read_bytes())
def save(p,x):
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
baseline=j(E/'HISTORY_BASELINE.json')['files'];mismatch=[]
for r in baseline:
 p=Path(r['path'])
 if not p.is_file() or p.stat().st_size!=r['bytes'] or h(p)!=r['sha256']:mismatch.append(str(p))
expected={r['path'] for r in baseline};current={str(p) for root in [P,I] for p in root.rglob('*') if p.is_file() and not p.is_relative_to(O) and not(root==P and p.parent==P and p.name in NAV)}
extras=sorted(current-expected);assert not mismatch and not extras,(mismatch,extras)
nav=[]
for n in NAV:
 original=(E/'NAV_ORIGINALS'/n).read_bytes();actual=(P/n).read_bytes();assert actual.endswith(original)
 nav.append({'file':n,'old_bytes_preserved_as_suffix':True,'old_sha256':hashlib.sha256(original).hexdigest(),'new_sha256':hashlib.sha256(actual).hexdigest()})
mis=j(P/'DCL-R6-batch02-Perf/evidence/DUPLICATE_REGISTER.json');miserr=[r['relative'] for r in mis['files'] if h(Path(mis['path'])/r['relative'])!=r['duplicate_sha256']];assert not miserr
history_result={'status':'PASS_ADMIN_IMMUTABILITY','history_files':len(baseline),'mismatches':mismatch,'new_files_outside_delivery':extras,'navigation':nav,'mispath_files':47,'mispath_mismatches':miserr}
if (E/'HISTORY_AFTER_CHECK.json').exists():assert j(E/'HISTORY_AFTER_CHECK.json')==history_result
else:save(E/'HISTORY_AFTER_CHECK.json',history_result)
locks=j(E/'SOURCE_AND_REVIEW_CHECK.json');A=P/'DCL-R6-FullChain-AdmissionFix'
for r in locks['frozen_runtime_files']:
 assert h(I/'ra01'/r['relative'])==h(E/'FROZEN_RA_ORIGINALS'/r['relative'])==r['sha256']
for r in locks['review_files']:
 assert h(A/r['relative'])==h(E/'ADMISSIONFIX_REVIEW_ORIGINALS'/r['relative'])==r['sha256']
assert len(locks['frozen_runtime_files'])==64 and len(locks['review_files'])==8
count=j(E/'FINAL_COUNT_CLOSURE_CALCULATION.json');assert sum(f['count'] for f in count['families'])==4450
assert count['native_members_upper']==4451 and count['admin_originals_upper']==4452 and count['admin_zip_members_upper']==4467
graph=j(E/'EVIDENCE_GRAPH_DELIVERY.json');ids={n['evidence_id'] for n in graph['nodes']};pos={n:i for i,n in enumerate(graph['topological_order'])}
assert len(ids)==len(pos)==1142 and all(pos[a]<pos[b] for a,b in graph['edges'])
assert all(d in ids for n in graph['nodes'] for d in n['dependency_ids'])
assert set(graph['rank'])==ids and all(graph['rank'][a]<graph['rank'][b] for a,b in graph['edges'])
cycles=j(E/'MINIMAL_CYCLE_WITNESSES.json')['witnesses'];assert [r['edge_count'] for r in cycles]==[3,3,2]
rule=O/'proposals/MR_CROSS_INSTANCE_RULE_DRAFT.json';policy=j(rule)
assert not policy['user_approved'] and not policy['runtime_enabled'] and not policy['evidence_usable_now']
assert policy['recommendation']=='APPROVE_RECOMMENDED' and h(rule) in (O/'MR_CROSS_INSTANCE_ADMISSION_APPROVAL.md').read_text(encoding='utf-8')
decision=j(E/'FINAL_REVIEW_DECISION.json');assert all(decision[k]==0 for k in ['production_guard_changes','runtime_source_edits','packaging_implementation','cross_gate_implementation','WSL_calls','dynamic_tests'])
assert decision['T0'] is None and decision['R'] is None and decision['RESOURCE_GATE_PASS']=='NOT_OBTAINED'
reports=[p for p in O.glob('*.md') if p.name!='EVIDENCE_INDEX.md'];assert len(reports)==12
assert '|14|' in (O/'FINAL_DECISION.md').read_text(encoding='utf-8')
future={'evidence/DELIVERY_CHECK.json','EVIDENCECONTRACT_MANIFEST.json','EVIDENCECONTRACT_EVIDENCE.zip','EVIDENCECONTRACT_EVIDENCE.zip.sha256'}
linkerr=[];links=0
for p in O.glob('*.md'):
 s=p.read_text(encoding='utf-8');assert '不是' not in s
 for name in re.findall(r'\]\(([^)]+)\)',s):
  links+=1
  if name in future or name.startswith(('http:','https:','#')):continue
  if not(p.parent/name.strip('<>')).exists():linkerr.append({'file':p.name,'target':name})
assert not linkerr,linkerr
parsed=0
for p in O.rglob('*.json'):j(p);parsed+=1
assert not list(O.rglob('*.pyc'))
save(E/'FINAL_CONTRACT_REVIEW_LOCK.json',{'date':'2026-11-14','review_version':'EvidenceContract-Closure/review-1','effective_runtime_change':False,
 'source_originals':64,'prior_review_objects':8,'formal_contract_models_only':True,
 'files':[{'relative':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':h(p)} for p in sorted(list(O.glob('*.md'))+list((O/'proposals').glob('*.json'))+[E/'FINAL_COUNT_CLOSURE_CALCULATION.json',E/'EVIDENCE_GRAPH_DELIVERY.json',E/'LIFECYCLE_FORMAL_MODEL.json'])],
 'runtime_execution_lock':'NOT_ISSUED','dynamic_receipt':'NOT_ISSUED','approval_receipt':'NOT_ISSUED'})
exclude={'EVIDENCECONTRACT_MANIFEST.json','EVIDENCECONTRACT_EVIDENCE.zip','EVIDENCECONTRACT_EVIDENCE.zip.sha256','evidence/DELIVERY_CHECK.json'}
rows=[{'relative':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':h(p)} for p in sorted(O.rglob('*')) if p.is_file() and p.relative_to(O).as_posix() not in exclude]
save(O/'EVIDENCECONTRACT_MANIFEST.json',{'schema':'DCL-EVIDENCE-CONTRACT-RESEARCH-DELIVERY/1','scope':'Static review artifacts only; no native runtime seal',
 'date':'2026-11-14','files':rows,'excluded':sorted(exclude),'utc':datetime.now(timezone.utc).isoformat()})
zp=O/'EVIDENCECONTRACT_EVIDENCE.zip'
with zipfile.ZipFile(zp,'x',zipfile.ZIP_DEFLATED) as z:
 for r in rows:z.write(O/r['relative'],r['relative'])
 z.write(O/'EVIDENCECONTRACT_MANIFEST.json','EVIDENCECONTRACT_MANIFEST.json')
with zipfile.ZipFile(zp) as z:
 assert len(z.namelist())==len(rows)+1==len(set(z.namelist())) and z.testzip() is None
 for r in rows:
  raw=z.read(r['relative']);assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['sha256']==h(O/r['relative'])
zh=h(zp)
with(O/'EVIDENCECONTRACT_EVIDENCE.zip.sha256').open('x',encoding='ascii') as f:f.write(zh+'  EVIDENCECONTRACT_EVIDENCE.zip\n')
receipt={'schema':'DCL-EVIDENCECONTRACT-DELIVERY/1','status':'PASS_ADMINISTRATIVE_DELIVERY_ONLY','date':'2026-11-14',
 'overall':decision['overall'],'reports':12,'final_answers':14,'history_files':len(baseline),'history_mismatches':mismatch,'nav_original_suffixes_preserved':4,'mispath_files':47,'mispath_mismatches':miserr,
 'source_originals_unchanged':64,'prior_review_objects_unchanged':8,'DAG_nodes':1142,'DAG_edges':len(graph['edges']),'DAG_acyclic':True,
 'DAG_rank_max':max(graph['rank'].values()),'fixed_point_iterations_upper':graph['closure_iterations_upper'],
 'raw_count_upper':4450,'native_member_upper':4451,'admin_originals_upper':4452,'admin_final_members_upper':4467,
 'count_proof_scope':'Conservative closed-world frozen-source manual abstraction; no least-maximum or full CPython semantic proof claim',
 'raw_byte_upper':'EVIDENCE_MAX_BOUND_UNRESOLVED','end_to_end_work':'UNRESOLVED','time300s':'UNRESOLVED',
 'old_guards':'256/257_UNCHANGED','capacity_draft_effective':False,'MR_rule_recommendation':'APPROVE_RECOMMENDED','MR_rule_sha256':h(rule),'user_approved':False,'MR_certificate_usable':False,
 'native_runtime_tests':'UNRUN','WSL_calls':0,'new_dynamic_tests':0,'runtime_edits':0,'packaging_mechanism_code':0,'cross_gate_code':0,
 'T0':None,'deadline':None,'R':None,'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
 'STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED','native_seal':'NOT_APPLICABLE_NO_RUNTIME','administrative_runtime_seal':'NOT_APPLICABLE_NO_ENTRY',
 'research_archive':'SEALED_AND_VERIFIED','links_checked':links,'link_errors':linkerr,'JSON_parsed':parsed,'manifest_rows':len(rows),'ZIP_entries':len(rows)+1,
 'manifest_sha256':h(O/'EVIDENCECONTRACT_MANIFEST.json'),'ZIP_sha256':zh,'ZIP_bytes':zp.stat().st_size,'self_excluded_from_manifest_and_zip':True,
 'utc':datetime.now(timezone.utc).isoformat(),'admin_elapsed_seconds':time.perf_counter()-tick}
save(E/'DELIVERY_CHECK.json',receipt)
print(json.dumps({k:receipt[k] for k in ['overall','reports','history_files','DAG_nodes','raw_count_upper','native_member_upper','admin_originals_upper','manifest_rows','ZIP_entries','ZIP_sha256','ZIP_bytes']}))
