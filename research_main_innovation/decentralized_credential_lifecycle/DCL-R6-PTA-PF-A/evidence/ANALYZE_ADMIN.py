"""Read-only Windows artifact/accounting audit. No production oracle or test replay."""
from pathlib import Path
import hashlib,json,struct,zipfile
E=Path(__file__).resolve().parent;B=E.parent.parent;W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\pf01')
N=Path(r'D:\毕业设计\DCL-R6-isolated-verification\batch12\native_snapshot')
C=Path(json.loads((E/'AUTHORIZATION_RECEIPT_LOCK.json').read_bytes())['control_directory'])
def load(p):return json.loads(Path(p).read_bytes())
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def put(name,x):
    with (E/name).open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
final=load(C/'STARTUP_FINALIZATION.json');native=final['native_audit'];manifest=load(C/'STARTUP_ADMIN_MANIFEST.json')
errors=[]
with zipfile.ZipFile(C/'STARTUP_ADMIN_EVIDENCE.zip') as z:
    assert z.testzip() is None
    for row in manifest['files']:
        raw=z.read(row['archive_path'])
        if len(raw)!=row['bytes'] or hashlib.sha256(raw).hexdigest()!=row['sha256']:errors.append(row['archive_path'])
        assert h(row['host'])==row['sha256']
    assert z.read('STARTUP_ADMIN_MANIFEST.json')==(C/'STARTUP_ADMIN_MANIFEST.json').read_bytes()
    admin_entries=len(z.namelist())
assert not errors and h(C/'STARTUP_ADMIN_MANIFEST.json')==final['manifest_sha256'] and h(C/'STARTUP_ADMIN_EVIDENCE.zip')==final['ZIP_sha256']
assert len(manifest['files'])==171 and admin_entries==172
copy_errors=[]
for row in native['files']:
    if h(N/row['relative'])!=row['sha256']:copy_errors.append(row['relative'])
assert not copy_errors
put('AUTOMATIC_ADMIN_VERIFICATION.json',{'status':'ADMIN_EVIDENCE_SEALED','scope':'Frozen automatic host/native flow; later audit reads original ZIP only',
 'manifest_rows':171,'ZIP_entries':172,'ZIP_sha256':final['ZIP_sha256'],'manifest_sha256':final['manifest_sha256'],
 'ZIP_bytes':final['ZIP_bytes'],'stream_errors':errors,'automatic_snapshot_vs_independent_export_errors':copy_errors,
 'native_original_files':len(native['files']),'fallback_archival_calls':0})
rows=load(E/'SOURCE_AND_SCOPE_ADMISSION.json')['files'];source_errors=[]
for row in rows:
    for base in [W,E/'FROZEN_SOURCE_REFERENCE',Path(r'D:\毕业设计\DCL-R6-isolated-verification\batch12\FROZEN_PF')]:
        if h(base/row['relative'])!=row['sha256']:source_errors.append(str(base/row['relative']))
assert not source_errors and not list(W.rglob('*.pyc'))
put('SOURCE_AFTER_CHECK.json',{'status':'MATCH','files':55,'programs':38,'source_errors':source_errors,'frozen_source_edits':0,'pyc_files':[]})
state=load(N/'inputs/batch_state.json');cp=load(N/'inputs/PT_RUNTIME_CHECKPOINT.json');private=load(N/'inputs/root_private/boot/pt_phase.json')
intent=load(N/'inputs/root_private/boot/pt_runtime_intent.json');events=[json.loads(x) for x in (N/'inputs/root_private/boot/pt_events.jsonl').read_bytes().splitlines()]
phases=['PRE_WINDOW','PREFLIGHT_VALIDATING','PREFLIGHT_QUALIFIED','RUNTIME_INITIALIZING','RUNTIME_READY','RUNTIME_ARMED','RUNNING']
assert [x['phase'] for x in events]==phases
for i,event in enumerate(events):assert event['sequence']==i and event['previous_sha256']==(hashlib.sha256(canonical(events[i-1])).hexdigest() if i else None)
assert cp['phase']==private['phase']=='RUNNING' and cp['sequence']==private['sequence']==6 and cp['committed'] is True
assert cp['phase_record_sha256']==hashlib.sha256(canonical(private)).hexdigest()
assert cp['initialization_id']==hashlib.sha256(canonical(intent)).hexdigest()
assert cp['window']=={k:state[k] for k in ['T0','deadline','stop_at']}
assert abs(state['deadline']-state['T0']-1800)<1e-6 and abs(state['stop_at']-state['T0']-1740)<1e-6
raw=(N/'out/visits.bin').read_bytes();assert raw[:8]==b'BRNGv001' and len(raw)==24
used,cap=struct.unpack('<QQ',raw[8:]);assert (used,cap)==(1907,1000000)
journal=[json.loads(x) for x in (N/'out/visits.bin.journal.jsonl').read_bytes().splitlines()];assert len(journal)==3814
position=0;commits={};prepared={};last=0
for i in range(0,len(journal),2):
    a,b=journal[i:i+2];assert a['status']=='PREPARED' and b['status']=='COMMITTED'
    for key in ['protocol','boot_id','cap','request','before','after','amount']:assert a[key]==b[key]
    assert a['before']==position and a['amount']==1 and a['after']==position+1 and a['cap']==cap and a['boot_id']==state['boot_id']
    assert last<=a['boottime']<=b['boottime'];position=b['after'];last=b['boottime'];commits[position]=b;prepared[position]=a
assert position==used and load(N/'out/visits.bin.intent.json')['after']==used
put('BUDGET_AUDIT.json',{'status':'MATCH','R':used,'cap':cap,'transactions':1907,'journal_lines':3814,'amount_per_transaction':1,
 'monotonic_and_contiguous':True,'first_prepare':journal[0]['boottime'],'last_commit':journal[-1]['boottime'],
 'counter_sha256':h(N/'out/visits.bin'),'journal_sha256':h(N/'out/visits.bin.journal.jsonl'),
 'intent_sha256':h(N/'out/visits.bin.intent.json'),'T0':state['T0'],'deadline':state['deadline'],'stop_at':state['stop_at'],
 'source_of_zero_resets':'Single boot/window records plus complete0..1907 journal; no second budget initialization',
 'method':'Structural counter/journal/manifest audit, no target checker execution'})
case_rows=[];suites=[]
for kind,contract_name,qualification_name,prefix,start,audit_start,expected_count,expected_mutants in [
    ('PT','startup_contract.json','inputs/PT_QUALIFICATION.json','pt_case_',1,1027,64,9),
    ('PF','phase_finalizer_contract.json','inputs/root_private/boot/pf_qualification.json','pf_case_',1090,1860,48,8)]:
    cfg=load(W/'inputs'/contract_name);qual=load(N/qualification_name);assert qual['accepted'] and len(qual['results'])==expected_count
    assert qual['contract_sha256']==h(W/'inputs'/contract_name)
    checker='startup_oracle.py' if kind=='PT' else 'phase_finalizer_oracle.py';assert qual['checker_sha256']==h(W/'src'/checker)
    assert qual['before']==start and qual['after']==(1090 if kind=='PT' else 1907)
    statuses={};mutants=0
    for i,(job,row) in enumerate(zip(cfg['jobs'],qual['results'])):
        file=N/'inputs/root_private/boot'/(prefix+('%03d'%i)+'.json');data=load(file)
        assert data['case_id']==row['case_id']==job['case_id'] and data['binding']==qual['binding']
        assert data['input_sha256']==hashlib.sha256(canonical(job)).hexdigest() and row['raw_sha256']==h(file)
        assert len(data['trace'])==len(job['frames']) and all(a['actual_input']==b for a,b in zip(data['trace'],job['frames']))
        target='MUTATION_DETECTED' if job['mutant'] else 'PASS';assert row['status']==target and row['accepted']
        assert data['after']-data['before']==16
        statuses[target]=statuses.get(target,0)+1;mutants+=bool(job['mutant'])
        if not job['mutant']:assert row['violations']==[]
        expected_violation=job.get('expected_violation') if kind=='PT' else job['violation_class'] if job['mutant'] else None
        if job['mutant']:assert expected_violation in row['violations'] and set(row['violations'])<=set(job['allowed_violations'])
        begin=prepared[data['before']+1]['boottime']
        case_rows.append({'suite':kind,'case_id':job['case_id'],'mutant':job['mutant'],'frame_count':len(job['frames']),
            'expected_status':target,'native_oracle_status':row['status'],'native_oracle_accepted':row['accepted'],'violations':row['violations'],
            'raw_original':str(file),'raw_sha256':h(file),'input_sha256':data['input_sha256'],'native_qualification':qualification_name,
            'driver_before':data['before'],'driver_after':data['after'],'driver_charged':16,'allocated_root_audit_charge':1,'allocated_case_total':17,
            'root_audit_prepaid_commit':commits[audit_start+i]['boottime'],'raw_sample':data['sample'],
            'first_driver_prepare_time':begin,'prepare_to_raw_sample_seconds':data['sample']['boottime']-begin,
            'full_case_or_oracle_elapsed_seconds':None,'timing_scope':'Measured charged-prefix to subject sample; includes budget IO, excludes later raw persistence/first oracle and aggregate audit; full per-case elapsed UNKNOWN',
            'test_origin':data['origin'],'post_run_oracle_replay':False})
    assert mutants==expected_mutants
    suites.append({'suite':kind,'jobs':expected_count,'mutants':mutants,'statuses':statuses,'before':qual['before'],'after':qual['after'],
        'charged':qual['after']-qual['before'],'qualification_sample':qual['sample'],'qualification_sha256':h(N/qualification_name),
        'contract_sha256':qual['contract_sha256'],'checker_sha256':qual['checker_sha256'],'test_scope':qual['origin']})
put('TEST_CASE_RESULTS.json',{'cases':case_rows,'suites':suites,'total_jobs':112,'mutants_detected':17,
 'verification_scope':'Native oracle outputs authenticated by raw file/input/binding/manifest hashes; no checker/reference re-execution after closure'})
ready=load(N/'inputs/C00_READINESS.json');c00=load(N/'inputs/result_C00.json');assert c00['status']=='PASS'
wait=load(N/'inputs/root_private/waitpid_838.json');assert wait['exit_code']==0 and wait['raw_wait_status']==0
closed=load(N/'inputs/CLOSED.json');stops=[{'file':p.name,**load(p)} for p in N.glob('inputs/stop_result_*.json')]
assert stops and all(r['stop_exit']==0 and r['empty'] and not r['after_stop_group_exists'] for r in stops)
audit=load(E/'POSTRUN_AUDIT.json');assert not audit['payload_processes'] and not audit['root_role_processes'] and not audit['parent_cgroup_exists']
metadata=load(E/'NATIVE_EXPORT_LOCK.json')['files'];phase_lock=next(r for r in metadata if r['relative']=='inputs/root_private/boot/pt_phase.lock')
assert (phase_lock['uid'],phase_lock['gid'],phase_lock['mode'],phase_lock['nlink'])==(0,0,384,1) and phase_lock['ACL']==[]
put('LOCK_AND_PHASE_EVIDENCE.json',{'phase_events':events,'public_checkpoint':cp,'private_phase':private,'lock_metadata':phase_lock,
 'lock_path':'/var/lib/dcl-r6/batch12/inputs/root_private/boot/pt_phase.lock','observed_final_phase':'RUNNING','expected_final_phase':'RUNNING',
 'phase_version':6,'writer_identity':state['launcher_identity'],'root_coordinator':state['coordinator_identity'],
 'lock_acquire_time':None,'lock_release_time':None,'per_read_expected_and_observed_log':'UNKNOWN_NOT_EMITTED',
 'contention_count':None,'observed_lock_timeout_or_drift_errors':0,'source_path_and_successful_native_control_flow_support_same_lock':True,
 'caution':'Does not certify unobserved interleavings, actual contention, mutex latency or interruption after crashes'})
jrows=[json.loads(x) for x in (E/'RUN_BOOT_JOURNAL.stdout.raw').read_bytes().splitlines()]
jbrief=[{'monotonic_seconds':int(x['__MONOTONIC_TIMESTAMP'])/1e6,'pid':x.get('_PID'),'message':x.get('MESSAGE'),'realtime_us':x.get('__REALTIME_TIMESTAMP')} for x in jrows]
put('JOURNAL_MESSAGE_INDEX.json',jbrief)
physical_errors=[]
for name in ['windows_entry.stderr.raw','STARTUP_POSTEXIT.stderr.raw']:
    raw=(C/name).read_bytes().decode('utf-8',errors='replace')
    for token in ['PT_RUNTIME_PHASE_DRIFT','Traceback (most recent call last)','ModuleNotFoundError','PF_PHASE_LOCK_BOUND','PF_PHASE_DEADLINE']:
        if token in raw:physical_errors.append({'stream':name,'token':token})
assert not physical_errors
disposition=load(N/'inputs/root_private/boot/pt_seal_disposition.json')
assert disposition['native_seal_status']=='NATIVE_SEAL_UNRESOLVED' and not (N/'out/EVIDENCE.zip').exists() and not (N/'inputs/SEAL_ERROR.json').exists()
seal_gap={'status':'NATIVE_SEAL_UNRESOLVED','native_zip_present':False,'native_manifest_present':False,'SEAL_ERROR_present':False,
 'native_disposition':disposition,'first_failed_acceptance_item':'Native sealing after normal CLOSED',
 'deterministic_source_path':['M.seal -> P.seal_applicability','P.runtime_checkpoint(...terminal_inspection=True)',
  'P._phase_guard -> _phase_deadline(G)','_phase_deadline calls active-only G.state()','G.validate_state_document sees CLOSED -> AdmissionBlocked(BATCH_STOPPED)',
  'seal_applicability catches AdmissionBlocked -> NATIVE_SEAL_UNRESOLVED -> defer_startup_seal'],
 'proof_scope':'Original CLOSED precedes disposition; exact frozen call graph deterministically rejects here. Caught exception was not independently logged or replayed.',
 'expected_state':'Read-only terminal inspection of existing authenticated window','actual_path':'Active-only state admission still rejects all stopped batches',
 'manual_seal_replay':False,'source_repair':False,'historical_batch11_native_seal':'NATIVE_SEAL_COMPLETED unchanged'}
put('NATIVE_SEAL_GAP.json',seal_gap)
values=c00['actual']['probe']['actual']['facts'];parent=values['parent']['values'];proc=values['process']
memory_peak=max(int(r.get('before_stop_charged_snapshot',{}).get('values',{}).get('memory.peak','0')) if r.get('before_stop_charged_snapshot') else 0 for r in stops)
data={'batch_id':'batch12','revision':'PTA-PhaseFinalizer-static-1/r3','mode':'NORMAL_START','overall':'PARTIAL_NATIVE_SEAL_UNRESOLVED',
 'PF-A1':'PASS_DYNAMIC','PF-A2':'CONDITIONAL_PASS','PF-A3':'PASS_DYNAMIC','PF-A4':'PASS_DYNAMIC','PF-A5':'CONDITIONAL_PASS','PF-A6':'CONDITIONAL_PASS','PF-A7':'PASS_DYNAMIC',
 'gate_scope_notes':{'PF-A2':'Synthetic rejection policies exercised; OS invalid-state/lock fault injection not performed',
 'PF-A5':'Real normal closure/reaping confirmed; formal Root critical-failure closure not injected',
 'PF-A6':'Actual auto import/export/archive succeeded; exact import-start/live-RLIMIT/lock timestamps not independently emitted',
 'PF-A7':'Independent truthful axes recorded, including native UNRESOLVED; this gate is separation of verdicts, not native completion'},
 'boot_id':state['boot_id'],'owner':state['coordinator_identity'],'scheduler':state['launcher_identity'],'stopper':load(N/'inputs/STOP_ARMED.json')['identity'],
 'T0':state['T0'],'deadline':state['deadline'],'stop_at':state['stop_at'],'R':used,'journal_transactions':1907,'journal_lines':3814,
 'C00':'PASS','C00_sample':c00['sample'],'RUNNING_sample':private['sample'],'checkpoint_sample':cp['sample'],
 'PT64':suites[0],'PF48':suites[1],'tests_executed':112,'mutants_detected':17,'phase_drift_observed':False,
 'CLOSED':closed,'STOP_REQUEST_present':(N/'out/STOP_REQUEST.json').exists(),'waitpid':wait,'stop_results':stops,
 'internal_close_status':'UNKNOWN','internal_close_file_present':(N/'inputs/root_private/boot/mr_close_state.json').exists(),
 'batch_state_status_preserved':state['status'],'actual_controlled_roles_empty':True,'automatic_admin':final,
 'native_seal_status':'NATIVE_SEAL_UNRESOLVED','native_seal_gap':seal_gap,
 'active_host':load(C/'WINDOWS_ENTRY_EXIT.json'),'all_host':load(E/'ACTIVE_ENTRY_RETURN.json'),
 'T0_to_closed_seconds':closed['boottime']-state['T0'],'PT_qualification_offset':suites[0]['qualification_sample']['boottime']-state['T0'],
 'PF_qualification_offset':suites[1]['qualification_sample']['boottime']-state['T0'],
 'charged_memory_peak_observed_bytes':memory_peak,'charged_memory_peak_MiB':memory_peak/(1<<20),'C00_tasks_observed':int(parent['pids.current']),
 'C00_process_limits_and_memory':proc,'Root_RSS_peak':None,'administrative_RLIMIT_live_receipt':None,'administrative_cwd':None,'administrative_full_sys_path':None,
 'admin_resource_order_evidence':'Frozen hash-bound main sets AS1GiB/single30s before source hash/import; Native inherited-envelope checks and post0 succeeded; no separate live numeric RLIMIT/import-time receipt',
 'read_only_export_observation_boot':audit['observation_boot_id'],'manual_cleanup_calls':0,'extra_fallback_archive_calls':0,
 'read_only_administrative_export_calls':1,'target_entry_calls':1,'source_edits':0,'test_retries':0,'post_exit_oracle_replays':0,
 'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
 'STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED'}
put('ACTUAL_RESULTS.json',data)
timeline=[{'event':x['phase'],'boottime':x['sample']['boottime'],'T0_offset':x['sample']['boottime']-state['T0'],'source':'pt_events.jsonl seq'+str(x['sequence'])} for x in events]
for name,t,origin in [('T0',state['T0'],'batch_state'),('C00 PASS',c00['sample']['boottime'],'result_C00'),
 ('PT64 accepted',suites[0]['qualification_sample']['boottime'],'PT_QUALIFICATION'),('PF48 accepted',suites[1]['qualification_sample']['boottime'],'pf_qualification'),
 ('CLOSED',closed['boottime'],'CLOSED'),('child waitpid0',wait['sample']['boottime'],'waitpid_838'),
 ('native applicability unresolved',disposition['sample']['boottime'],'pt_seal_disposition'),('automatic post audit',native['observation']['boottime'],'STARTUP_POSTEXIT.stdout')]:
    timeline.append({'event':name,'boottime':t,'T0_offset':t-state['T0'],'source':origin})
timeline.sort(key=lambda r:r['boottime']);put('EXECUTION_TIMELINE.json',{'native_boottime':timeline,'journal_monotonic':jbrief,
 'host_active':data['active_host'],'host_total':data['all_host'],'automatic_finalization':{k:v for k,v in final.items() if k!='native_audit'},
 'clock_caution':'BOOTTIME/MONOTONIC/guest UTC/host UTC retained separately; no exact cross-clock latency certificate'})
print(json.dumps({'overall':data['overall'],'C00':'PASS','PT64':suites[0]['statuses'],'PF48':suites[1]['statuses'],'R':1907,
 'journal_transactions':1907,'native_seal':'UNRESOLVED','automatic_admin':'SEALED','admin_manifest_rows':171,'admin_zip_entries':172,
 'charged_peak_MiB':data['charged_memory_peak_MiB'],'observed_payload_tasks':data['C00_tasks_observed']},ensure_ascii=False))
