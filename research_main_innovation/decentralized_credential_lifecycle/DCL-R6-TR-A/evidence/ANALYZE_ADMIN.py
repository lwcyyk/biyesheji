"""Verify actual preflight failure/admin artifacts; never replay target functions."""
from pathlib import Path
import hashlib,json,zipfile
E=Path(__file__).resolve().parent;W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\tr01')
C=Path(json.loads((E/'AUTHORIZATION_RECEIPT_LOCK.json').read_bytes())['control_directory'])
def load(p):return json.loads(Path(p).read_bytes())
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,x):
    with(E/name).open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
result=load(C/'STARTUP_FINALIZATION.json');audit=result['native_audit'];manifest=load(C/'STARTUP_ADMIN_MANIFEST.json');errors=[]
with zipfile.ZipFile(C/'STARTUP_ADMIN_EVIDENCE.zip') as z:
    assert z.testzip() is None
    for row in manifest['files']:
        data=z.read(row['archive_path'])
        if hashlib.sha256(data).hexdigest()!=row['sha256'] or len(data)!=row['bytes']:errors.append(row['archive_path'])
        assert h(row['host'])==row['sha256']
    assert z.read('STARTUP_ADMIN_MANIFEST.json')==(C/'STARTUP_ADMIN_MANIFEST.json').read_bytes();entries=len(z.namelist())
assert not errors and h(C/'STARTUP_ADMIN_EVIDENCE.zip')==result['ZIP_sha256'] and h(C/'STARTUP_ADMIN_MANIFEST.json')==result['manifest_sha256']
assert len(manifest['files'])==14 and entries==15 and audit['files']==[]
assert result['active_exit']==125 and result['post_exit_code']==0 and result['administrative_seal_status']=='ADMIN_EVIDENCE_SEALED'
assert audit['native_seal_status']=='NATIVE_SEAL_NOT_APPLICABLE' and audit['T0'] is None and audit['R'] is None
assert not any(audit['runtime_objects'].values()) and not audit['closed_marker']
assert not audit['role_processes'] and not audit['payload_pids'] and not audit['parent_cgroup_exists']
put('AUTOMATIC_ADMIN_VERIFICATION.json',{'status':'ADMIN_EVIDENCE_SEALED','classification':'Automatic preflight-failure administrative evidence; no native runtime seal',
 'manifest_rows':14,'ZIP_entries':15,'ZIP_sha256':result['ZIP_sha256'],'manifest_sha256':result['manifest_sha256'],'ZIP_bytes':result['ZIP_bytes'],
 'stream_errors':errors,'native_original_files':0,'manual_or_fallback_finalizer_calls':0})
source=load(E/'SOURCE_AND_SCOPE_ADMISSION.json')['files'];source_errors=[];export=load(E/'FROZEN_SOURCE_EXPORT_LOCK.json')
for row in source:
    for base in [W,E/'FROZEN_SOURCE_REFERENCE',Path(r'D:\毕业设计\DCL-R6-isolated-verification\batch13\FROZEN_TR')]:
        if h(base/row['relative'])!=row['sha256']:source_errors.append(str(base/row['relative']))
assert not source_errors and not list(W.rglob('*.pyc')) and len(export['files'])==59
put('SOURCE_AFTER_CHECK.json',{'status':'MATCH','files':59,'programs':41,'source_errors':source_errors,'source_edits':0,'pyc_files':[]})
drift=load(E/'RUNTIME_DRIFT_AUDIT.json');assert len(drift['differences'])==3 and not drift['frozen_source_input_mismatches']
for row in load(E/'DRIFTED_RUNTIME_EXPORT_LOCK.json')['files']:assert h(row['host'])==row['sha256']
assert not drift['runtime_root_exists'] and not drift['installed_slice_exists'] and not drift['parent_cgroup_exists'] and not drift['root_roles'] and not drift['payload_pids']
events=[]
for line in (C/'windows_entry.stdout.raw').read_bytes().splitlines():
    try:q=json.loads(line)
    except (ValueError,TypeError):continue
    events.append(q)
assert len(events)==1 and events[0]['event']=='PREFLIGHT_BEGIN'
stderr=(C/'windows_entry.stderr.raw').read_bytes().decode('utf-8',errors='replace')
failure='BC_ARTIFACT_DRIFT:/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2'
assert failure in stderr
cases=[]
for suite,file in [('PT','startup_contract.json'),('PF','phase_finalizer_contract.json'),('TR','terminal_contract.json')]:
    cfg=load(W/'inputs'/file)
    for job in cfg['jobs']:
        cases.append({'suite':suite,'case_id':job['case_id'],'mutant':job['mutant'],'status':'NOT_EXERCISED' if job['mutant'] else 'UNRUN_PREFLIGHT_FAILED',
            'actual_input':None,'trace':None,'oracle_result':None,'visits':None,'elapsed_seconds':None,'reason':'Native runtime closure rejected before claim/T0/C00'})
assert len(cases)==152 and sum(bool(row['mutant']) for row in cases)==25
put('UNRUN_CASE_REGISTER.json',{'cases':cases,'planned':152,'planned_mutants':25,'executed':0,'mutants_exercised':0,'detected':0,'oracle_calls':0})
put('FIRST_FAILURE.json',{'status':'PREFLIGHT_FAILED_RUNTIME_DRIFT','error':failure,'error_type':'boot_continuity.Rejected','exit_code':125,
 'raiser':'boot_continuity.artifact_check','stage':'PREFLIGHT_BEGIN before runtime_snapshot/preparation/claim',
 'native_begin':events[0],'observed_error_stream':'windows_entry.stderr.raw','exact_throw_time':None,
 'expected_and_actual':drift['differences'][0],'counter':None,'T0':None,'sealed_claim_created':False,'runtime_directory_created':False,
 'source_drift':False,'test_failure':False,'runtime_pin_updated':False,'retry':False})
actual={'batch_id':'batch13','revision':'TerminalRead-static-1/r1','mode':'NORMAL_START','overall':'PREFLIGHT_FAILED_RUNTIME_DRIFT',
 'TR-A1':'UNRUN','TR-A2':'UNRUN','TR-A3':'UNRUN','TR-A4':'UNRUN','TR-A5':'UNRUN','TR-A6':'CONDITIONAL_PASS','TR-A7':'UNKNOWN','TR-A8':'FAIL',
 'gate_scope_notes':{'TR-A6':'Actual automatic administrative failure archive succeeded; no runtime terminal-input regression and changed runtime unqualified',
 'TR-A7':'No application/window/close state existed; original admin internal field UNKNOWN retained','TR-A8':'Pinned system runtime closure drift prevented admission; budget uninitialized'},
 'host_static':'PASS','deployment':'PASS_STATIC_DEPLOYMENT_ONLY','readonly_environment':'PASS_BASIC_PLATFORM_ONLY','native_preflight':'FAILED_ARTIFACT_DRIFT',
 'boot_id':audit['observation_boot_id'],'bootstrap_actor':events[0]['identity'],'admin_actor':audit['administrative_actor'],
 'entry_calls':1,'actual_exit':125,'post_exit':0,'T0':None,'deadline':None,'stop_at':None,'R':None,'journal_created':False,
 'runtime_root_exists':False,'runtime_objects':audit['runtime_objects'],'CLOSED_exists':False,'STOP_REQUEST_exists':False,'sealed_claim_created':False,
 'C00':'UNRUN_PREFLIGHT_FAILED','PT64_executed':0,'PF48_executed':0,'TR40_executed':0,'mutants_exercised':0,'mutants_detected':0,'oracle_calls':0,
 'terminal_reader_called':False,'active_guard_after_CLOSED_checked':False,'native_seal_called':False,'native_seal_status':'NATIVE_SEAL_NOT_APPLICABLE',
 'internal_status':'UNKNOWN','administrative_seal_status':'ADMIN_EVIDENCE_SEALED','automatic_finalization':result,
 'active_host':load(C/'WINDOWS_ENTRY_EXIT.json'),'all_host':load(E/'ACTIVE_ENTRY_RETURN.json'),
 'runtime_drift':drift,'runtime_files_different':3,'source_changes':0,'test_retries':0,'manual_cleanup':0,'extra_fallback_archival':0,
 'controlled_roles_empty':True,'parent_group_absent':True,'memory_and_tasks_high_water':None,
 'resource_scope':'No runtime workload; Root/admin RSS not sampled. No initialized counter is represented as0.',
 'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
 'STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED'}
put('ACTUAL_RESULTS.json',actual)
put('EXECUTION_TIMELINE.json',{'native_events':events,'active_host':actual['active_host'],'all_host':actual['all_host'],
 'post_plan':load(C/'STARTUP_POSTEXIT_PLAN.json'),'post_result':{k:v for k,v in result.items() if k!='native_audit'},
 'post_audit':{k:v for k,v in audit.items() if k not in ['files','nonregular']},'drift_observation':{'boot_id':drift['boot_id'],'boottime':drift['observation_boottime']},
 'clock_caution':'Raw guest BOOTTIME/UTC, host UTC, package-log time retained separately; package-log timezone unrecorded'})
print(json.dumps({'overall':actual['overall'],'source_match':True,'runtime_differences':3,'tests_run':0,'T0':None,'R':None,'native':'NOT_APPLICABLE',
 'automatic_admin_rows':14,'automatic_admin_entries':15,'fallback_or_retry':0},ensure_ascii=False))
