"""Administrative final byte/history/contract/math seal; no runtime roles."""
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
history=j(E/'HISTORY_BASELINE.json')['files'];mismatches=[]
for r in history:
 p=Path(r['path'])
 if not p.is_file() or p.stat().st_size!=r['bytes'] or h(p)!=r['sha256']:mismatches.append(str(p))
current={str(p) for root in [P,I] for p in root.rglob('*') if p.is_file() and not p.is_relative_to(O) and not(root==P and p.parent==P and p.name in NAV)}
extra=sorted(current-{r['path'] for r in history});assert not mismatches and not extra,(mismatches,extra)
nav=[]
for n in NAV:
 old=(E/'NAV_ORIGINALS'/n).read_bytes();new=(P/n).read_bytes();assert new.endswith(old)
 nav.append({'file':n,'old_suffix_preserved':True,'old_sha256':hashlib.sha256(old).hexdigest(),'new_sha256':hashlib.sha256(new).hexdigest()})
mis=j(P/'DCL-R6-batch02-Perf/evidence/DUPLICATE_REGISTER.json');miserr=[r['relative'] for r in mis['files'] if h(Path(mis['path'])/r['relative'])!=r['duplicate_sha256']];assert not miserr
save(E/'HISTORY_AFTER_CHECK.json',{'status':'PASS_ADMIN_IMMUTABILITY','history_files':len(history),'mismatches':mismatches,'new_files_outside_delivery':extra,
 'navigation':nav,'mispath_files':47,'mispath_mismatches':miserr})
lock=j(E/'SOURCE_AND_PRIOR_LOCK_CHECK.json')
for r in lock['runtime_files']:assert h(I/'ra01'/r['relative'])==h(E/'FROZEN_RA_ORIGINALS'/r['relative'])==r['sha256']
for r in lock['review_objects']:assert h(P/'DCL-R6-FullChain-AdmissionFix'/r['relative'])==h(E/'PRIOR_REVIEW_ORIGINALS'/r['relative'])==r['sha256']
for r in lock['previous_contract_review_files']:assert h(P/'DCL-R6-EvidenceContract-Closure'/r['relative'])==r['sha256']
assert len(lock['runtime_files'])==64 and len(lock['review_objects'])==8
qpath=O/'proposals/C09_LOG_QUOTA_CONTRACT_PROPOSAL.json';mpath=O/'proposals/MR_CROSS_INSTANCE_FINAL_RULE_DRAFT.json'
q=j(qpath);mr=j(mpath);cap=j(O/'proposals/EVIDENCE_CAPACITY_CONTRACT_PROPOSAL.json')
assert q['classification_attempts']==256 and q['pending_record_max']==256 and q['pending_max_successful_handoff']==255
assert q['all_C09_native_rows_max']==263 and q['single_record_max_bytes']==1322 and q['main_log_total_max_bytes']==345148
assert q['main_log_actual_sharp_upper']==max(256*1298,255*1298+1322)+6*948+1028==339028
assert q['sidecar_max_bytes']==956 and q['failure_record_max_bytes']==334 and q['total_quota_evidence_max_bytes']==348684
assert q['quota_total_write_upper']==345148+266*956+334==599778 and q['fsync_attempts_upper']==798
assert not q['user_approved'] and not q['runtime_enabled'] and not cap['effective'] and cap['status']=='CAPACITY_CONTRACT_NOT_READY'
assert not mr['user_approved'] and not mr['runtime_enabled'] and mr['MR_CROSS_INSTANCE_ADMISSION']=='PROPOSED_NOT_EFFECTIVE'
assert h(mpath) in (O/'MR_CROSS_INSTANCE_FINAL_APPROVAL_TEXT.md').read_text(encoding='utf-8')
assert h(qpath) in (O/'CONTRACT_APPROVAL_CHECKLIST.md').read_text(encoding='utf-8')
count=j(E/'COUNT_SCOPE_COVERAGE_REVIEW.json');boot=next(r for r in count['families'] if r['id']=='BOOT_FIXED')
assert len(boot['paths'])==boot['count']==41 and 'inputs/root_private/boot/mr_events.lock' in boot['paths']
assert 'inputs/root_private/boot/pt_expected_abort.json' not in boot['paths'] and sum(r['count'] for r in count['families'])==4450
orig=j(E/'HISTORICAL_NATIVE_LOG_ACCOUNTING.json');assert orig['rows']==24 and orig['verdicts']['PENDING']==17 and orig['budget_journal_appends_in_pending_span']==0
verify=j(E/'INDEPENDENT_MATHEMATICAL_REVIEW.json');assert len(verify['historical_files'])==8 and all(r['matches_original_export_lock'] for r in verify['historical_files'])
rep=j(E/'REPRESENTATION_LIMIT_CAVEAT.json');assert rep['native_pending_line_lower']==1099 and rep['minimal_n_exceeding32MiB_from_skeleton']==30532
assert rep['pending_complete_records_upper']==((1<<63)-1)//1099
dpath=E/'FINAL_ANALYSIS_DECISION.json';d=j(dpath);d['gates']=j(E/'BC_GATE_DECISIONS.json')
d['representation_limit_note']='An additional off_t64/no-rotation ABI hypothesis gives a huge coarse ceiling; usable32MiB count/byte/work contract remains unclosed.'
dpath.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert all(d[k]==0 for k in ['producer_edits','budget_core_edits','sealer_edits','count_guard_changes','cross_gate_code','WSL_calls','dynamic_tests','native_faults','F1_F4_runs'])
assert all(d[k] is None for k in ['T0','deadline','R']) and d['RESOURCE_GATE_PASS']=='NOT_OBTAINED'
reports=[p for p in O.glob('*.md') if p.name!='EVIDENCE_INDEX.md'];assert len(reports)==13
assert '|17|' in (O/'FINAL_DECISION.md').read_text(encoding='utf-8')
future={'evidence/DELIVERY_CHECK.json','C09BOUND_MANIFEST.json','C09BOUND_EVIDENCE.zip','C09BOUND_EVIDENCE.zip.sha256'}
links=0;errors=[]
for p in O.glob('*.md'):
 s=p.read_text(encoding='utf-8');assert not re.search(r'不是[^\n。]*而是',s)
 for name in re.findall(r'\]\(([^)]+)\)',s):
  links+=1
  if name in future or name.startswith(('http:','https:','#')):continue
  if not(p.parent/name.strip('<>')).exists():errors.append({'file':p.name,'target':name})
assert not errors,errors
parsed=0
for p in O.rglob('*.json'):j(p);parsed+=1
assert not list(O.rglob('*.pyc'))
locked_files=sorted(list(O.glob('*.md'))+list((O/'proposals').glob('*.json'))+[E/'FINAL_ANALYSIS_DECISION.json',E/'NATIVE_RECORD_BYTE_ALGEBRA.json',
 E/'COUNTEREXAMPLE_FAMILY.json',E/'COUNT_SCOPE_COVERAGE_REVIEW.json',E/'INDEPENDENT_MATHEMATICAL_REVIEW.json',E/'REPRESENTATION_LIMIT_CAVEAT.json'])
save(E/'FINAL_BOUND_REVIEW_LOCK.json',{'date':'2026-11-15','review_version':'C09-BoundClosure/review-1','scope':'Research/contracts/math only; no effective policy or executable lock',
 'files':[{'relative':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':h(p)} for p in locked_files],
 'runtime_files_unchanged':64,'prior_review_unchanged':8,'approval_receipt':'NOT_ISSUED','dynamic_receipt':'NOT_ISSUED','new_runtime_namespace':None})
exclude={'C09BOUND_MANIFEST.json','C09BOUND_EVIDENCE.zip','C09BOUND_EVIDENCE.zip.sha256','evidence/DELIVERY_CHECK.json'}
rows=[{'relative':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':h(p)} for p in sorted(O.rglob('*')) if p.is_file() and p.relative_to(O).as_posix() not in exclude]
save(O/'C09BOUND_MANIFEST.json',{'schema':'DCL-C09-BOUND-RESEARCH-DELIVERY/1','date':'2026-11-15','status':d['overall'],
 'scope':'Local research artifact seal only; no native/admin active-run seal occurred','files':rows,'excluded':sorted(exclude),'utc':datetime.now(timezone.utc).isoformat()})
zp=O/'C09BOUND_EVIDENCE.zip'
with zipfile.ZipFile(zp,'x',zipfile.ZIP_DEFLATED) as z:
 for r in rows:z.write(O/r['relative'],r['relative'])
 z.write(O/'C09BOUND_MANIFEST.json','C09BOUND_MANIFEST.json')
with zipfile.ZipFile(zp) as z:
 assert len(z.namelist())==len(rows)+1==len(set(z.namelist())) and z.testzip() is None
 for r in rows:
  raw=z.read(r['relative']);assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['sha256']==h(O/r['relative'])
zh=h(zp)
with(O/'C09BOUND_EVIDENCE.zip.sha256').open('x',encoding='ascii') as f:f.write(zh+'  C09BOUND_EVIDENCE.zip\n')
receipt={'schema':'DCL-C09BOUND-DELIVERY/1','date':'2026-11-15','status':'PASS_ADMINISTRATIVE_DELIVERY_ONLY','overall':d['overall'],
 'reports':13,'final_answers':17,'source_files_unchanged':64,'prior_review_objects_unchanged':8,'previous_contract_lock_objects_unchanged':len(lock['previous_contract_review_files']),
 'historical_files':len(history),'historical_mismatches':mismatches,'nav_original_suffixes_preserved':4,'mispath_files':47,'mispath_mismatches':miserr,
 'historical_native_C09_rows':24,'historical_native_PENDING':17,'historical_raw_originals_lock_matched':8,'new_handoff_or_replay_runs':0,
 'native_log_sites':3,'native_pending_direct_sites':1,'conditional_single_row_max':1322,'conditional_PENDING_row_max':1298,
 'source_state_pending_quota':'ABSENT','physical_ABI_ceiling_separately_qualified':True,'coarse_off_t64_pending_bound':rep['pending_complete_records_upper'],
 'quota_attempts_proposed':256,'quota_PENDING_all_outcomes':256,'quota_PENDING_successful':255,'quota_all_native_rows_proposed':263,
 'quota_main_reserved_bytes':345148,'quota_typed_log_sharp_upper':339028,'quota_cursor_max':956,'quota_failure_max':334,
 'quota_retained_with_failed_staging':348684,'quota_write_upper':599778,'quota_durability_attempt_upper':798,
 'quota_sha256':h(qpath),'quota_effective':False,'capacity':'CAPACITY_CONTRACT_NOT_READY','MR_CROSS_INSTANCE_ADMISSION':'PROPOSED_NOT_EFFECTIVE','MR_rule_sha256':h(mpath),'approval_received':False,
 'old_guards':'256/257_UNCHANGED','old_count_scope_coverage':'mr_events.lock added and full-scope-unreachable pt_expected_abort excluded;4450/4451/4452 preserved conditionally',
 'WSL_calls':0,'dynamic_tests':0,'native_faults':0,'runtime_source_edits':0,'logger_or_quota_implementation':0,'packager_or_gate_implementation':0,
 'T0':None,'deadline':None,'R':None,'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
 'STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED','native_seal':'NOT_APPLICABLE_NO_RUNTIME','administrative_runtime_seal':'NOT_APPLICABLE_NO_ENTRY',
 'research_archive':'SEALED_AND_VERIFIED','links_checked':links,'link_errors':errors,'JSON_parsed':parsed,'manifest_rows':len(rows),'ZIP_entries':len(rows)+1,
 'manifest_sha256':h(O/'C09BOUND_MANIFEST.json'),'ZIP_sha256':zh,'ZIP_bytes':zp.stat().st_size,'self_excluded_from_manifest_and_zip':True,
 'utc':datetime.now(timezone.utc).isoformat(),'admin_elapsed_seconds':time.perf_counter()-tick}
save(E/'DELIVERY_CHECK.json',receipt)
print(json.dumps({k:receipt[k] for k in ['overall','reports','historical_files','historical_native_PENDING','quota_attempts_proposed','quota_main_reserved_bytes','manifest_rows','ZIP_entries','ZIP_sha256','ZIP_bytes']}))
