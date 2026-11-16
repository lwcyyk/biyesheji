"""Administrative immutable-history, review-lock and local delivery seal."""
from pathlib import Path
import ast,hashlib,json,re,time,zipfile
from datetime import datetime,timezone
O=Path(__file__).resolve().parent.parent;P=O.parent;E=O/'evidence';I=Path(r'D:\毕业设计\DCL-R6-isolated-verification')
NAV=['CURRENT_VERDICT.md','NEXT_ACTION.md','README.md','DECISION_HISTORY.md'];tick=time.perf_counter()
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
current={str(p) for root in [P,I] for p in root.rglob('*') if p.is_file() and not p.is_relative_to(O) and not(root==P and p.parent==P and p.name in NAV)}
expected={r['path'] for r in baseline};new=sorted(current-expected)
assert not mismatch and not new,(mismatch,new)
nav=[]
for n in NAV:
 original=(E/'NAV_ORIGINALS'/n).read_bytes();actual=(P/n).read_bytes();assert actual.endswith(original)
 nav.append({'file':n,'original_suffix_preserved':True,'original_sha256':hashlib.sha256(original).hexdigest(),'new_sha256':hashlib.sha256(actual).hexdigest()})
mis=j(P/'DCL-R6-batch02-Perf/evidence/DUPLICATE_REGISTER.json')
miserr=[r['relative'] for r in mis['files'] if h(Path(mis['path'])/r['relative'])!=r['duplicate_sha256']];assert not miserr
save(E/'HISTORY_AFTER_CHECK.json',{'status':'PASS_ADMIN_IMMUTABILITY','history_files':len(baseline),'mismatches':mismatch,'new_files_outside_delivery':new,'nav':nav,'mispath_files':47,'mispath_mismatches':miserr})
lock=j(E/'STATIC_REVIEW_LOCK.json');review=[]
for r in lock['files']:
 p=O/r['relative'];assert p.stat().st_size==r['bytes'] and h(p)==r['sha256'];review.append(r)
assert len(review)==8 and not lock['runtime_enabled']
base=j(E/'SOURCE_BASELINE_LOCK.json');originals=[]
for r in base['files']:
 p=Path(base['source'])/r['relative'];q=E/'FROZEN_RA_ORIGINALS'/r['relative']
 assert h(p)==h(q)==r['sha256'];originals.append({'relative':r['relative'],'change':'UNCHANGED','sha256':r['sha256']})
save(E/'FILE_DIFF_INDEX.json',{'old_runtime_files':originals,'new_review_objects':[dict(r,change='ADDED_REVIEW_ONLY') for r in review],
 'runtime_patches_applied':0,'MR_hook':'PROPOSED_NOT_APPLIED','capacity_delta':'OLD256/257_UNCHANGED_NEW_N_UNSELECTED',
 'old_execution_lock_sha256':h(E/'FROZEN_RA_ORIGINALS/inputs/execution_lock.json'),'new_execution_lock':'NOT_ISSUED'})
syntax=[]
for p in (O/'maintenance').glob('*.py'):
 t=ast.parse(p.read_text(encoding='utf-8-sig'),feature_version=(3,12));compile(t,str(p),'exec');syntax.append(p.name)
assert len(syntax)==4 and not (O/'maintenance/__pycache__').exists()
f=j(E/'FINAL_COMPONENT_CHECKS.json');assert all(h(O/r['relative'])==r['sha256'] for r in f['components'])
assert len(f['archive_fixture_rechecks'])==27 and len(f['historical_archive_rechecks'])==2 and len(f['final_archive_mutations'])==7
summary=j(E/'HOST_ATTEMPT_R2/HOST_CHECK_SUMMARY.json');assert summary['archive_mutants_detected']==7 and summary['MR_mutants_detected']==8
assert summary['archive_cases']+summary['actual_archive_function_cases']+summary['actual_admin_guard_cases']+summary['MR_pure_predicates']+summary['MR_oracle_cases']==64
w=j(E/'EXPANDED_FULLCHAIN_LOWER_WITNESS.json');assert w['raw_files_lower']==1082 and len({r['relative'] for r in w['rows']})==1082
assert all(r['sha256'] is None and r['size'] is None for r in w['rows'])
cat=j(E/'EVIDENCE_CATALOG.json');assert len(cat['rows'])==794 and not cat['full_success_manifest_available']
decision=j(E/'FINAL_STATIC_DECISION.json');assert decision['overall']=='PARTIAL_STATIC_REPAIR_REVIEW_ONLY' and not decision['runtime_cap_raised']
for k in ['WSL_calls','service_starts','native_faults','native_entry_imports','F1_F4_imports','dynamic_retries']:assert decision[k]==0
for k in ['T0','deadline','R']:assert decision[k] is None
reports=[p for p in O.glob('*.md') if p.name!='EVIDENCE_INDEX.md'];assert len(reports)==14
links=0;linkerr=[];future={'evidence/DELIVERY_CHECK.json','ADMISSIONFIX_MANIFEST.json','ADMISSIONFIX_EVIDENCE.zip','ADMISSIONFIX_EVIDENCE.zip.sha256'}
for p in list(O.glob('*.md')):
 s=p.read_text(encoding='utf-8-sig');assert '不是' not in s
 for name in re.findall(r'\]\(([^)]+)\)',s):
  if name in future:links+=1;continue
  if name.startswith(('http:','https:','#')):continue
  links+=1
  if not(p.parent/name.strip('<>')).exists():linkerr.append({'file':p.name,'target':name})
assert not linkerr,linkerr
json_count=0
for p in O.rglob('*.json'):j(p);json_count+=1
exclude={'ADMISSIONFIX_MANIFEST.json','ADMISSIONFIX_EVIDENCE.zip','ADMISSIONFIX_EVIDENCE.zip.sha256','evidence/DELIVERY_CHECK.json'}
rows=[{'relative':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':h(p)} for p in sorted(O.rglob('*')) if p.is_file() and p.relative_to(O).as_posix() not in exclude]
save(O/'ADMISSIONFIX_MANIFEST.json',{'schema':'FC-ADMISSIONFIX-RESEARCH-DELIVERY/1','version':lock['version'],
 'status':'PARTIAL_STATIC_REPAIR_REVIEW_ONLY','files':rows,'excluded':sorted(exclude),'utc':datetime.now(timezone.utc).isoformat()})
zp=O/'ADMISSIONFIX_EVIDENCE.zip'
with zipfile.ZipFile(zp,'x',zipfile.ZIP_DEFLATED) as z:
 for r in rows:z.write(O/r['relative'],r['relative'])
 z.write(O/'ADMISSIONFIX_MANIFEST.json','ADMISSIONFIX_MANIFEST.json')
with zipfile.ZipFile(zp) as z:
 assert len(z.namelist())==len(rows)+1==len(set(z.namelist())) and z.testzip() is None
 for r in rows:
  raw=z.read(r['relative']);assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['sha256']==h(O/r['relative'])
zh=h(zp)
with(O/'ADMISSIONFIX_EVIDENCE.zip.sha256').open('x',encoding='ascii') as f:f.write(zh+'  ADMISSIONFIX_EVIDENCE.zip\n')
receipt={'schema':'FC-ADMISSIONFIX-DELIVERY/1','status':'PASS_ADMINISTRATIVE_DELIVERY_ONLY','overall':decision['overall'],
 'version':lock['version'],'reports':14,'review_components':4,'review_proposal_inputs':4,'review_lock_objects':8,
 'old_source_files_unchanged':64,'historical_files':len(baseline),'historical_mismatches':mismatch,'navigation_suffixes_preserved':4,'mispath_files':47,'mispath_mismatches':miserr,
 'catalog_rows':794,'expanded_full_raw_lower':1082,'expanded_native_lower':1083,'full_maximum':None,'new_production_capacity':None,
 'base_host_cases':64,'archive_mutants':7,'MR_mutants':8,'final_archive_fixture_rechecks':27,'historical_archive_compatibility':2,
 'runtime_hooks_applied':0,'old_runtime_source_edits':0,'native_runtime_tests':'UNRUN','WSL_calls':0,'native_fault_injections':0,'dynamic_retries':0,
 'T0':None,'deadline':None,'R':None,'actual_new_formal_hard_bound':None,'conditional_joint_visit_estimate':71618,
 'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
 'STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED','native_seal':'NOT_APPLICABLE_NO_RUNTIME','automatic_admin_seal':'NOT_APPLICABLE_NO_ENTRY',
 'research_archive':'SEALED_AND_VERIFIED','host_development_failures_preserved':3,'links_checked':links,'link_errors':linkerr,'JSON_parsed':json_count,
 'manifest_rows':len(rows),'ZIP_entries':len(rows)+1,'manifest_sha256':h(O/'ADMISSIONFIX_MANIFEST.json'),'ZIP_sha256':zh,'ZIP_bytes':zp.stat().st_size,
 'self_excluded_from_manifest_and_zip':True,'utc':datetime.now(timezone.utc).isoformat(),'admin_elapsed_seconds':time.perf_counter()-tick}
save(E/'DELIVERY_CHECK.json',receipt)
print(json.dumps({k:receipt[k] for k in ['overall','reports','historical_files','base_host_cases','archive_mutants','MR_mutants','manifest_rows','ZIP_entries','ZIP_sha256','ZIP_bytes']}))
