"""R22 document/hash review only. Does not import application modules or run tests."""
import datetime
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(r'D:\毕业设计');BASE=ROOT/'research_g2_dsat_implementation';OUT=BASE/'2026-11-11_r22'
RUNTIME=BASE/'2026-11-11_r22_d1b1_closure_offline';PROJECT=ROOT/'auth-lifecycle'
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
checks=[]
def check(label,value,detail=None):checks.append({'label':label,'passed':bool(value),'detail':detail})

reports=['01_IMPLEMENTATION_SUMMARY.md','02_CROSS_PROCESS_ADMISSION.md','03_DURABLE_START_AUTHORIZATION.md','04_FAILURE_AND_RECOVERY_RESULTS.md',
         '05_TEST_RESULTS_AND_COST.md','06_CODE_DIFF_AND_INTEGRITY.md','07_FINAL_VERDICT_AND_NEXT_STEP.md']
required=reports+['R22_SCOPE_LOCK.json','R22_ACTUAL_RESULTS.json','R22_TEST_RUNS.json','R22_CROSS_PROCESS_WITNESSES.json',
    'R22_AUTHORIZATION_CONSUMPTION_AUDIT.json','R22_RESOURCE_LEDGER.json','R22_CODE_DIFF.json','SOURCE_LOCK.json']
check('ALL_15_DELIVERABLES_EXIST',all((OUT/n).is_file() for n in required))
check('Q1_THROUGH_Q14_ANSWERED',all(re.search(r'\| Q'+str(i)+r'\b',(OUT/reports[-1]).read_text(encoding='utf-8')) for i in range(1,15)))
pre=load(OUT/'sources/PRECHECK_LOCK.json');scope=load(OUT/'R22_SCOPE_LOCK.json');lock=load(OUT/'R22_FILE_LOCK.json')
allowed={x['path']:x for x in pre['allowed_modifications']}
check('SIX_TARGETS_FIVE_PYTHON_FILES',len(scope['targets'])==6 and len(allowed)==5 and {x['path'] for x in scope['targets'] if Path(x['path']).suffix=='.py'}==set(allowed))
unapproved=[x['path'] for x in pre['protected'] if x['path'] not in allowed and sha(x['path'])!=x['sha256']]
check('1194_OTHER_PROTECTED_FILES_UNCHANGED',len(pre['protected'])==1199 and not unapproved,unapproved)
check('FIVE_ORIGINAL_BYTE_SNAPSHOTS',all(sha(OUT/'sources/original'/(Path(x['path']).name+'.txt'))==x['before_sha256'] for x in allowed.values()))
check('ORIGINAL_FOUR_FIXTURE_INPUTS_UNCHANGED',all(sha(x['path'])==x['sha256'] for x in pre['fixture_existing']))
check('EXACTLY_ONE_APPENDED_FIXTURE',len(list((PROJECT/'tests/fixtures/dsat_authority_live_lifecycle').glob('*.json')))==5)
check('CURRENT_EIGHT_CODE_HASHES_AND_INPUTS',all(sha(x['path'])==x['sha256'] for x in lock['executed_code']+lock['inputs']))

history=load(OUT/'R22_TEST_RUNS.json');all_runs=[load(x['path']) for x in history['runs']]
slots=list(RUNTIME.glob('SUITE_INVOCATION_*.json'))
extra=load(OUT/'ADDITIONAL_APPROVAL_RECEIPT.json') if (OUT/'ADDITIONAL_APPROVAL_RECEIPT.json').exists() else None
extra_ok=extra is not None and extra.get('approved') is True
cap=4 if extra_ok else 3
check('DIRECT_SUITE_LIMIT_OBSERVED',len(slots)==history['direct_suite_invocations']<=cap)
if extra_ok:
    check('ADDITIONAL_APPROVAL_BINDS_ACTUAL_REPLY',extra['request_sha256']==sha(OUT/'ADDITIONAL_RUN_REQUEST.json') and extra['response_sha256']==sha(extra['response_path']))
check('NO_AUTOMATIC_RERUNS',history['automatic_reruns']==0)
check('ALL_ACTUAL_RESULT_HASHES_PRESERVED',all(sha(x['path'])==x['sha256'] for x in history['runs']))
check('FIRST54_ERROR_PRESERVED',history['first54_counts']=={'PASS':53,'FAIL':0,'ERROR':1,'SKIP':0,'BLOCKED':0,'NOT_RUN':0})
first=load(RUNTIME/'new54_001/RESULTS.json')
check('F24_EXACT_ERROR_RETAINED',next(c for c in first['cases'] if c['id']=='F24')['status']=='ERROR' and 'OSError' in next(c for c in first['cases'] if c['id']=='F24')['detail'])
snaps=[]
for r in all_runs:
    for c in r['code']:
        p=Path(r['run'])/'code_snapshot'/(Path(c['path']).name+'.txt')
        snaps.append(p.is_file() and sha(p)==c['sha256'])
check('ALL_EXECUTED_VERSION_SNAPSHOTS',len(snaps)==8*len(all_runs) and all(snaps))
check('RUNTIME_ISOLATION_AUDIT_CLEAN',all(r['audit']['unexpected_violations']==[] and all(r['audit'][k]==0 for k in ['socket_attempts','forbidden_process_attempts','deployment_access','private_outside_access','outside_writes']) for r in all_runs))
check('OWNED_TEST_CHILD_LIMITS_PER_DOMAIN',all(r['audit']['child_launch_attempts']<=8 for r in all_runs))
check('TEMP_CRYPTO_AND_SQL_CAPS_PER_DOMAIN',all(r['audit']['file_SQLite_connections']<=104 and r['scope_counts'].get('test_state_keys_generated',0)<=2 and r['scope_counts'].get('test_TLS_material_generated',0)<=2 and r['scope_counts'].get('test_SSLContext_loads',0)<=2 for r in all_runs))
check('NO_FORCED_CHILD_TERMINATIONS',all(not c['result']['terminated_owned_stub'] for r in all_runs for c in r['owned_children']))
check('ALL_OWNED_HANDLES_EXPLICITLY_CLOSED',all(c['result']['pipes_closed'] and c['result']['process_handle_closed'] for r in all_runs for c in r['owned_children']))
check('CHILD_STDOUT_STDERR_COMPLETE_PATHS',all(Path(c['result']['stdout_path']).is_file() and Path(c['result']['stderr_path']).is_file() for r in all_runs for c in r['owned_children']))

combined=load(OUT/'R22_ACTUAL_RESULTS.json');wit=load(OUT/'R22_CROSS_PROCESS_WITNESSES.json')
check('ALL_122_DISTINCT_IDS_EXECUTED',len(combined['selected_cases'])==122 and len({c['id'] for c in combined['selected_cases']})==122)
check('X01_X02_ACTUAL_DISTINCT_ACTORS',wit['actors_distinct'] and wit['first_actor_exited_before_second_admission'])
check('F23_ACTUAL_INVALID_MARKERS_REFUSED',wit['first_actor']['probes']['stale_marker']=='RECOVERY_REQUIRED' and wit['first_actor']['probes']['old_epoch']=='STALE_EPOCH' and all(v!='ADMITTED' for v in wit['first_actor']['probes'].values()))
check('F26_ALL_PERSISTED_REPLAYS_REJECTED',set(wit['second_actor']['replays'].values())=={'REPLAY'} and set(wit['second_actor']['aliases'].values())=={'REPLAY'})
check('T45_CONSUMED_AND_STARTED_DISTINCT',wit['first_actor']['first_start']['START_APPROVAL_CONSUMED'] and wit['first_actor']['first_start']['START_SUCCEEDED'] and wit['second_actor']['claimed_failure']['START_APPROVAL_CONSUMED'] and not wit['second_actor']['claimed_failure']['START_SUCCEEDED'])
check('DAMAGED_MISSING_SLOT_FAILS_CLOSED',set(wit['second_actor']['corruption'].values())=={'RECOVERY_REQUIRED'})
check('EXPLICIT_ONE_EFFECT_ONLY',wit['second_actor']['effect_count_A']==1)
status=load(OUT/'FINAL_STATUS.json')
check('NO_FALSE_ALL_PASS_PROMOTION',not('R22_122_TESTS_PASSED' in status['statuses']) or (combined['counts']['PASS']==122 and combined['counts']['ERROR']==0 and combined['same_final_code_version']))
if not extra_ok:
    check('PARTIAL_REPAIR_STAYS_PENDING',status['overall']=='D1B1_PARTIAL_IMPLEMENTATION' and combined['counts']['ERROR']==1 and not combined['all122_contract_accepted'])
wrapper=load(OUT/'sources/COMMAND_WRAPPER_FAILURE_001.json')
check('SHELL_WRAPPER_FAILURE_TRANSPARENT',wrapper['unauthorized_outside_write_attempt']==1 and wrapper['actual_outside_write']==0 and wrapper['suite_launched'] is False and not Path(wrapper['attempted_path']).exists())
check('FORMAL_DEPLOYMENT_ROOT_ABSENT_METADATA_ONLY',not(ROOT/'h2_test_runtime/h2-authority-synth-001').exists())

# Do not publish values or hashes of generated private test keys.
canaries=[PROJECT/'tests/fixtures'/x/'CANARIES.json' for x in ['dsat_authority_live_lifecycle','dsat_authority_runtime','dsat_authority_host_activation','dsat_authority_read_host']]
values={v for p in canaries for v in load(p)['values'].values()}
needles=[n for v in values for n in [v.encode('utf-8'),json.dumps(v,ensure_ascii=True)[1:-1].encode('ascii')]]
private=[p for p in RUNTIME.rglob('*') if p.is_file() and p.suffix in {'.key','.pem','.pfx'}]
for p in private:
    raw=p.read_bytes()
    if raw:needles.extend([raw,raw.hex().encode('ascii')])
public=[p for root in [OUT,RUNTIME] for p in root.rglob('*') if p.is_file() and p.suffix not in {'.key','.pem','.pfx','.db','.db-wal','.db-shm'} and p.name!='DELIVERY_QA.json']
hits=[];invalid_json=[];style=[]
for p in public:
    raw=p.read_bytes()
    if any(n in raw for n in needles):hits.append(str(p))
    if p.suffix=='.json':
        try:load(p)
        except Exception:invalid_json.append(str(p))
    if p.parent==OUT and p.suffix=='.md' and '不是' in raw.decode('utf-8-sig'):style.append(str(p))
check('PUBLIC_SECRET_SCAN_CLEAN',not hits,hits)
check('DELIVERY_JSON_VALID',not invalid_json,invalid_json)
check('PROSE_STYLE',not style,style)
source=load(OUT/'SOURCE_LOCK.json')
check('SOURCE_LOCK_BINDS_CURRENT_MANIFEST',source['file_lock_sha256']==sha(OUT/'R22_FILE_LOCK.json') and source['scope_lock_sha256']==sha(OUT/'R22_SCOPE_LOCK.json'))
check('FINAL_PROTECTED_RECHECK',all(x['path'] in allowed or sha(x['path'])==x['sha256'] for x in pre['protected']))
manifest=[{'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='DELIVERY_QA.json')]
result={'schema':'r22-document-qa/1','kind':'DOCUMENT_HASH_REVIEW_NOT_PROJECT_TEST','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'passed':all(x['passed'] for x in checks),'checks':checks,'manifest':manifest,'self_excluded':True,
    'project_suite_invocations_by_this_review':0,'current_overall':status['overall'],'selected_counts':combined['counts'],
    'budget_or_runtime_limitations':['first failed competitor parent observation window17.953s; actual kernel lifetime unmeasured','OS power-loss/volume rollback/hostile same-SID not verified'],
    'wrapper_error_kept':True}
(OUT/'sources/DELIVERY_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'document_QA_passed':result['passed'],'review_items':len(checks),'protected':len(pre['protected']),'current_state':status['overall'],
    'suite_invocations':used if 'used' in globals() else len(slots),'extra_approved':extra_ok,'public_scan_hits':len(hits),'project_test_runs_now':0,
    'failed':[x['label'] for x in checks if not x['passed']]}))
raise SystemExit(0 if result['passed'] else 1)
