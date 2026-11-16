"""R21 final documentation/integrity review only; never runs project code."""
import ast
import datetime
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(r"D:\毕业设计");BASE=ROOT/'research_g2_dsat_implementation'
OUT=BASE/'2026-11-11_r21';R20=BASE/'2026-11-11_r20'
RUNTIME=BASE/'2026-11-11_r21_d1b1_offline';PROJECT=ROOT/'auth-lifecycle'
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
checks=[]
def check(label,value,detail=None):checks.append({'label':label,'passed':bool(value),'detail':detail})

reports=['01_IMPLEMENTATION_SUMMARY.md','02_INSTANCE_IDENTITY_AND_SINGLE_ACTIVE.md','03_LIFECYCLE_AND_RESOURCE_OWNERSHIP.md',
         '04_FAILURE_CLEANUP_AND_RECOVERY_RESULTS.md','05_TEST_RESULTS_AND_COST.md','06_CODE_DIFF_AND_INTEGRITY.md','07_FINAL_VERDICT_AND_NEXT_STEP.md']
required=reports+['D1B1_FILE_LOCK.json','D1B1_ACTUAL_RESULTS.json','D1B1_TEST_RUNS.json','D1B1_FAILURE_COVERAGE.json',
    'D1B1_RESOURCE_LEDGER.json','D1B1_COMMAND_LOCK.json','CODE_DIFF.json','SOURCE_LOCK.json']
check('ALL_15_REQUIRED_FILES',all((OUT/x).is_file() for x in required))
text=(OUT/reports[-1]).read_text(encoding='utf-8')
check('ALL_14_USER_QUESTIONS_ANSWERED',all(re.search(r'\| Q'+str(i)+r'\b',text) for i in range(1,15)))
pre=load(OUT/'sources/PRECHECK_LOCK.json');lock=load(OUT/'D1B1_FILE_LOCK.json')
mods={x['path']:x for x in pre['allowed_modifications']}
unapproved=[]
for x in pre['protected_files']:
    if x['path'] not in mods and sha(x['path'])!=x['sha256']:unapproved.append(x['path'])
check('1155_OTHER_PROTECTED_FILES_UNCHANGED',len(pre['protected_files'])==1158 and len(mods)==3 and not unapproved,unapproved)
check('THREE_ORIGINAL_SNAPSHOTS',all(sha(OUT/'sources/original'/(Path(x['path']).name+'.txt'))==x['before_sha256'] for x in mods.values()))
old_group=load(R20/'sources/PRECHECK_LOCK.json')['files']
check('R20_1133_GROUP_1130_UNCHANGED',len(old_group)==1133 and sum(x['path'] not in mods for x in old_group)==1130 and all(x['path'] in mods or sha(x['path'])==x['sha256'] for x in old_group))
check('NINE_EXACT_TARGETS',len(lock['targets'])==9 and [x['path'] for x in lock['targets']]==[x['path'] for x in pre['targets']])
check('CURRENT_CODE_MATCHES_FROZEN_FINAL_MANIFEST',len(lock['executed_code'])==8 and all(sha(x['path'])==x['sha256'] for x in lock['executed_code']))
for x in lock['executed_code']:ast.parse(Path(x['path']).read_text(encoding='utf-8'))
check('FIXTURE_HASHES_STABLE',all(sha(x['path'])==x['sha256'] for x in lock['inputs']))

history=load(OUT/'D1B1_TEST_RUNS.json')
check('EXACTLY_SIX_AUTHORIZED_SUITE_INVOCATIONS',history['direct_invocations']==len(history['runs'])==6)
all_runs=[load(x['path']) for x in history['runs']]
check('ALL_SIX_ORIGINAL_RESULT_HASHES',all(sha(x['path'])==x['sha256'] for x in history['runs']))
check('TWO_INVOCATIONS_EACH',all(sum(r['suite']==s for r in all_runs)==2 for s in ['new52','r19_24','legacy44']))
check('240_REPEATED_EXECUTIONS_120_DISTINCT_FINAL',sum(r['executed'] for r in all_runs)==240 and history['distinct_final_ids']==120)
final=[load(RUNTIME/(s+'_002')/'RESULTS.json') for s in ['new52','r19_24','legacy44']]
check('FINAL_SUITES_SHARE_CURRENT_CODE',all(r['code']==lock['executed_code'] for r in final))
check('FINAL_RAW_120_PASS_2366_CHECKS',sum(r['counts']['PASS'] for r in final)==120 and sum(len(c['checks']) for r in final for c in r['details'])==2366 and all(v['satisfied'] for r in final for c in r['details'] for v in c['checks']))
expected_ids=[['F%02d'%i for i in range(1,29)]+['T%02d'%i for i in range(29,53)],['D%02d'%i for i in range(1,25)],['A%02d'%i for i in range(1,21)]+['H%02d'%i for i in range(1,25)]]
check('ALL_FROZEN_IDS_PRESERVED',all([c['id'] for c in r['cases']]==ids for r,ids in zip(final,expected_ids)))
new,D,AH=final
check('ORIGINAL_DOMAIN_IMPORT_BOUNDARIES',D['production_modules_imported']==AH['production_modules_imported']==[] and AH['cryptography_imported'] is False and D['cryptography_imported'] is True)
check('NEW_DOMAIN_IMPORT_IS_ACTUAL_TEST_STORE_ONLY',set(new['production_modules_imported'])=={'auth_lifecycle.online_state.services','auth_lifecycle.online_state.storage','auth_lifecycle.online_state.materials'})
check('NO_UNEXPECTED_RUNTIME_VIOLATIONS',all(r['audit']['unexpected_violations']==[] for r in all_runs))
check('NO_SOCKET_OR_PRIVATE_OUTSIDE_OR_DEPLOYMENT',all(all(r['audit'][k]==0 for k in ['socket_attempts','deployment_access','private_outside_access','outside_writes','forbidden_process_attempts']) for r in all_runs))
snap=[]
for row,r in zip(history['runs'],all_runs):
    folder=Path(row['path']).parent
    for c in r['code']:
        path=folder/'code_snapshot'/(Path(c['path']).name+'.txt')
        snap.append(path.is_file() and sha(path)==c['sha256'])
check('ALL_48_EXECUTED_CODE_SNAPSHOTS_PRESERVED',len(snap)==48 and all(snap))
check('SIX_FINAL_CHILD_PROCESS_HANDLES_EXPLICITLY_CLOSED',len(new['owned_children'])==6 and all(c['result']['pipes_closed'] and c['result']['process_handle_closed'] and not c['result']['terminated_owned_stub'] for c in new['owned_children']))
check('ACTUAL_CHILD_EXIT_CODES',sorted(c['result']['exit_code'] for c in new['owned_children'])==[0,0,0,0,73,74])
check('ACTUAL_NEW_RESOURCE_CAPS',new['audit']['file_SQLite_connections']==11 and max(new['audit']['SQLite_by_case'].values())<=2 and new['scope_counts']['test_state_keys_generated']==2 and new['scope_counts']['test_TLS_material_generated']==1 and new['scope_counts']['test_SSLContext_loads']==2 and new['audit']['threads_created']+1<=16 and new['audit']['threads_peak']<=4)
check('OLD_MEMORY_CAPS',D['audit']['memory_SQLite_connections']==1 and AH['audit']['memory_SQLite_connections']==18)
resource=load(OUT/'D1B1_RESOURCE_LEDGER.json');totals=resource['all_runs_totals']
check('CUMULATIVE_RESOURCE_CAPS',totals['owned_test_child_launches']==12<=16 and totals['file_SQLite_connections']==22<=208 and totals['temporary_state_key_generations']==4 and totals['temporary_TLS_key_certificate_generations']==2<=4 and totals['test_SSLContext_load_calls']==4 and totals['owned_child_forced_terminations']==0)
check('COST_WINDOW_SUM_CORRECT',resource['inclusive_suite_total_ns']==sum(r['elapsed_ns'] for r in final)==13518908800)
check('NEW_REAL_PEAK_MEMORY_RECORDED',new['memory']['peak_working_set_bytes']>=new['memory']['working_set_bytes']>0)

combined=load(OUT/'D1B1_ACTUAL_RESULTS.json');faults=load(OUT/'D1B1_FAILURE_COVERAGE.json')
check('RAW_VS_ACCEPTANCE_STATISTICS_EXPLICIT',combined['TOTAL']==120 and combined['raw_execution_counts']['PASS']==120 and combined['contract_acceptance_counts']=={'PASS':117,'FAIL':0,'ERROR':0,'SKIP':0,'BLOCKED':3,'NOT_RUN':0})
check('EXACT_AUDIT_BLOCKERS',set(combined['audit_blockers'])=={'F23','F26','T45'} and {c['id'] for c in combined['cases'] if c['contract_acceptance_status']=='BLOCKED'}=={'F23','F26','T45'})
check('FAULT_28_EXECUTED_26_ACCEPTED_2_BLOCKED',faults['TOTAL']==faults['raw_executed']==faults['raw_PASS']==28 and faults['full_contract_PASS']==26 and faults['full_contract_BLOCKED']==2)
check('FROZEN_FAULT_DEFINITIONS_RETAINED',all(x['injection_point']==y['injection_point'] and x['name']==y['name'] for x,y in zip(faults['rows'],load(R20/'D1B_FAILURE_AND_CLEANUP_MATRIX.json')['rows'])))
check('OVERALL_PARTIAL_NOT_DEPLOYMENT_COMPLETE',load(OUT/'FINAL_STATUS.json')['overall']=='D1B1_PARTIAL_IMPLEMENTATION' and combined['full_frozen_contract_accepted'] is False)
commands=load(OUT/'D1B1_COMMAND_LOCK.json')
check('D1B2_COMMAND_AND_AUTHORIZATION_CLOSED',commands['D1B2_actual_argv'] is None and commands['D1B2_command_executable'] is commands['D1B2_authorized'] is False)
request=load(OUT/'SUPPLEMENTAL_AUTHORIZATION_REQUEST.json')
check('SUPPLEMENT_NOT_EXECUTED_OR_APPROVED',request['approved'] is request['executed'] is False and request['future_tests']['total']==122 and request['future_tests']['direct_invocations']==3)
check('FORMAL_DEPLOYMENT_ROOT_ABSENT_METADATA_ONLY',not(ROOT/'h2_test_runtime/h2-authority-synth-001').exists())
semantic=load(OUT/'CODE_DIFF.json')['semantic_preservation']
check('OLD_BUSINESS_AST_PRESERVED',all(semantic['storage_business_methods_unchanged'].values()) and all(semantic[k] for k in ['SingleActive_AST_unchanged','Controller_AST_unchanged','FakeProvider_AST_unchanged']))
source=load(OUT/'SOURCE_LOCK.json')
check('CURRENT_SOURCE_LOCK_BINDS_FILE_LOCK_AND_REQUEST',source['file_lock_sha256']==sha(OUT/'D1B1_FILE_LOCK.json') and source['supplemental_request']['sha256']==sha(OUT/'SUPPLEMENTAL_AUTHORIZATION_REQUEST.json'))

# Private test material is an authorized resource, never a public evidence sink.
canary_paths=[PROJECT/'tests/fixtures'/x/'CANARIES.json' for x in ['dsat_authority_live_lifecycle','dsat_authority_runtime','dsat_authority_host_activation','dsat_authority_read_host']]
values={v for p in canary_paths for v in load(p)['values'].values()}
needles=[x for v in values for x in [v.encode('utf-8'),json.dumps(v,ensure_ascii=True)[1:-1].encode('ascii')]]
private_files=[p for p in RUNTIME.rglob('*') if p.is_file() and p.suffix in {'.key','.pem','.pfx'}]
for p in private_files:
    raw=p.read_bytes()
    if raw:needles.extend([raw,raw.hex().encode('ascii')])
public=[p for d in [OUT,RUNTIME] for p in d.rglob('*') if p.is_file() and p.suffix not in {'.key','.pem','.pfx','.db','.db-wal','.db-shm'} and p.name!='DELIVERY_QA.json']
hits=[];json_errors=[];style_errors=[]
for p in public:
    raw=p.read_bytes()
    if any(x in raw for x in needles):hits.append(str(p))
    if p.suffix=='.json':
        try:load(p)
        except Exception:json_errors.append(str(p))
    if p.parent==OUT and p.suffix=='.md' and '不是' in raw.decode('utf-8-sig'):style_errors.append(str(p))
check('PUBLIC_CANARY_AND_TEST_KEY_SCAN_CLEAN',not hits,{'hits':hits,'canary_values':len(values),'private_material_files_checked':len(private_files)})
check('DELIVERY_JSON_VALID',not json_errors,json_errors)
check('PROSE_STYLE',not style_errors,style_errors)
check('FINAL_HISTORICAL_RECHECK',all(x['path'] in mods or sha(x['path'])==x['sha256'] for x in pre['protected_files']))

manifest=[]
for p in sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='DELIVERY_QA.json'):
    manifest.append({'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size})
result={'schema':'r21-document-integrity-qa/1','reviewed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'kind':'DOCUMENT_AND_HASH_REVIEW_ONLY','project_test_invocations_in_this_review':0,
    'passed':all(c['passed'] for c in checks),'checks':checks,'files':manifest,
    'raw_test_result':{'PASS':120},'full_contract_result':{'PASS':117,'BLOCKED':3},
    'overall':'D1B1_PARTIAL_IMPLEMENTATION','new_runtime_or_production_probes':0,'self_excluded':True}
(OUT/'sources/DELIVERY_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'documentation_QA_passed':result['passed'],'review_items':len(checks),'delivery_files':len(manifest),
    'protected_unique':1158,'other_unchanged':1155,'public_scan_hits':len(hits),
    'project_tests_executed_now':0,'overall':result['overall'],'failed':[x['label'] for x in checks if not x['passed']]}))
raise SystemExit(0 if result['passed'] else 1)
