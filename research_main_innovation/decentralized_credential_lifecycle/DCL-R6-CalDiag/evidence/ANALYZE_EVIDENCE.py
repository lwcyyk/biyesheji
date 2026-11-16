"""Administrative extraction/hash/accounting. Never imports/replays a target checker."""
from pathlib import Path
from collections import Counter,defaultdict
import hashlib
import json
import re
import struct
import zipfile

E=Path(__file__).resolve().parent
R=Path(r'D:\毕业设计\DCL-R6-isolated-verification\batch09\final_snapshot')
INITIAL=R.parent/'native_snapshot'
W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\cr09')
def load(p):return json.loads(Path(p).read_bytes())
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,x):(E/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
state=load(R/'inputs/batch_state.json');t0=state['T0'];boot=state['boot_id'];closed=load(R/'inputs/CLOSED.json')
cleanup=load(E/'FROZEN_FAILURE_CLEANUP.json');finalaudit=load(E/'FINAL_POSTRUN_AUDIT.json')
events=[]
for line in (E/'windows_entry.stdout.raw').read_text(encoding='utf-8',errors='replace').splitlines():
    try:d=json.loads(line)
    except ValueError:continue
    if 'event' in d:events.append(d)
assert {d['identity']['boot_id'] for d in events}=={boot}
keyevents=[{k:d[k] for k in ['event','identity','sample','phase','case','main_identity','deadline'] if k in d}
    for d in events if d['event'] in ['PREFLIGHT_BEGIN','PREFLIGHT_QUALIFIED','ACTIVATION_REQUESTED_ONLY','ENTRY_VERIFIED','ACTUAL_SERVICE_CONFIRMED']]
waits=[load(p) for p in sorted((R/'inputs/root_private').glob('waitpid_*.json'))]
failed=next(d for d in waits if d['exit_code']==125);sender=next(d for d in waits if d['exit_code']==23)
resume_entry=load(R/'inputs/root_private/boot/entry_resume.json')
child_resume=load(R/'inputs/root_private/boot/child_resume.json')
failure_lo=child_resume['sample']['boottime'];failure_hi=failed['sample']['boottime']
put('BOOT_IDENTITY_AND_FAILURE.json',{'run_boot_id':boot,'events':keyevents,'sender_wait':sender,'resume_wait':failed,
    'resume_entry_owner':resume_entry['owner'],'same_PID_across_exec_and_resume':True,
    'failure_interval_boottime':[failure_lo,failure_hi],'failure_interval_from_T0':[failure_lo-t0,failure_hi-t0],
    'failure':'UNREVIEWED_MANAGER_FAILURE','first_failed_checkpoint':'RESUME_MANAGER_HEALTH_CHECK',
    'last_completed_case':'C09','first_unrun_case':'C10','actual_resume_count':state['resume_count'],
    'internal_resume_claims':1,'successful_resume_admissions':0})

# Parse the actual global accounting stream. This verifies storage consistency;
# target algorithms, semantic fixtures and model reference code remain untouched.
raw=(R/'out/visits.bin').read_bytes();assert raw[:8]==b'BRNGv001' and len(raw)==24
used,cap=struct.unpack('<QQ',raw[8:]);journal=[json.loads(line) for line in (R/'out/visits.bin.journal.jsonl').read_bytes().splitlines()]
running=0;pending=None;transactions=[]
for row in journal:
    assert row['boot_id']==boot and row['cap']==cap
    if row['status']=='PREPARED':
        assert pending is None and row['before']==running and row['after']-row['before']==row['amount']
        pending=row
    else:
        assert row['status']=='COMMITTED' and pending is not None
        assert all(row.get(k)==pending.get(k) for k in ['before','after','amount','cap','request','protocol','boot_id'])
        transactions.append({'before':pending['before'],'after':pending['after'],'amount':pending['amount'],
            'prepared':pending['boottime'],'committed':row['boottime'],'span':row['boottime']-pending['boottime'],
            'task_id':pending['request']['task_id'] if pending['request'] else None})
        running=row['after'];pending=None
assert pending is None and running==used==38729 and cap==1000000
assert load(R/'out/visits.bin.intent.json')==journal[-1]
assert len(transactions)==1739 and len(journal)==3478
assert all(h(INITIAL/'out'/name)==h(R/'out'/name) for name in ['visits.bin','visits.bin.intent.json','visits.bin.journal.jsonl'])
put('JOURNAL_ACCOUNTING.json',{'status':'PASS_ADMIN_STORAGE_INTEGRITY','used':used,'cap':cap,'transactions':len(transactions),'journal_lines':len(journal),'amount_distribution':dict(Counter(d['amount'] for d in transactions)),
    'components':{'C00_C08':37020,'READY64':449,'C09H34_and_Root_raw_audit':273,'RootIPC56':505,'BC40':481,'real_C09':1},
    'sum':37020+449+273+505+481+1,'initial_and_final_budget_bytes_identical':True,'transactions_detail':transactions,
    'meaning':'Host storage/format arithmetic only; no target suite or model reference re-executed'})

suites=[];integrity_errors=[]
configs={n:load(W/'inputs'/n) for n in ['readiness_contract.json','c09_contract.json','root_ipc_contract.json','boot_contract.json']}
for filename,cfgname,checker,pattern in [
 ('C00_READY_QUALIFICATION.json','readiness_contract.json','readiness_oracle.py','inputs/root_private/boot/ready_case_%03d.json'),
 ('ROOT_IPC_QUALIFICATION.json','root_ipc_contract.json','root_ipc_oracle.py','inputs/root_private/ipc_case_%03d.json'),
 ('BOOT_CONTINUITY_QUALIFICATION.json','boot_contract.json','boot_continuity_oracle.py','inputs/root_private/boot/bc_case_%03d.json'),
 ('C09H_QUALIFICATION.json','c09_contract.json','c09_oracle.py',None)]:
    q=load(R/'inputs'/filename);cfg=configs[cfgname]
    assert q['accepted'] and q['checker_sha256']==h(W/'src'/checker) and q['contract_sha256']==h(W/'inputs'/cfgname)
    assert {v['case_id'] for v in q['results']}=={v['case_id'] for v in cfg['jobs']} and all(v['accepted'] for v in q['results'])
    for i,row in enumerate(q['results']):
        if pattern:
            p=R/(pattern%i)
            if h(p)!=row['raw_sha256']:integrity_errors.append(str(p))
        else:
            for name,digest in row['raw_files'].items():
                p=R/'out/c09_tests'/row['case_id']/name
                if h(p)!=digest:integrity_errors.append(str(p))
    start=q.get('global_before');end=q.get('global_after');sample=q.get('sample')
    if start is None:start=37469;end=37742
    first=next(tx['prepared'] for tx in transactions if tx['before']==start)
    last=next(tx['committed'] for tx in transactions if tx['after']==end)
    observed_end=sample['boottime'] if sample else last
    suites.append({'receipt':filename,'jobs':len(q['results']),'counts':dict(Counter(v['status'] for v in q['results'])),
        'accepted':True,'native_raw_checker':checker,'raw_hash_integrity':'PASS_ADMIN_ONLY','global_before':start,'global_after':end,'visits':end-start,
        'charged_phase_first_PREP':first,'last_COMMITTED':last,'receipt_sample':sample,'charged_work_observed_span':observed_end-first,
        'time_scope':('First persisted charge to receipt sample; final receipt publication is outside this span' if sample else 'First PREP to last COMMITTED timestamp; final raw oracle/publication are outside this observed span'),
        'rows':q['results']})
assert not integrity_errors
put('COMPLETED_NATIVE_AUDITS.json',{'native_independent_audits':suites,'host_raw_hash_errors':integrity_errors,
    'new_host_target_oracle_calls':0,'full_chain_raw_audit':'UNRUN_AFTER_RESUME_FAILURE'})

# C09 evidence: expose binding/times/hashes only, retaining all nonces privately.
hand=load(R/'inputs/c09_handoff.json');ack=load(R/'inputs/c09_commit.json');witness=load(R/'inputs/c09_exit_witness.json');c09=load(R/'inputs/result_C09.json')
assert hand['stage']=='HANDOFF_VERIFIED' and hand['classification_count']==1 and c09['status']=='PASS'
assert hand['commit_sha256']==h(R/'inputs/c09_commit.json') and hand['witness_sha256']==h(R/'inputs/c09_exit_witness.json')
assert witness['exit_code']==23 and witness['raw_wait_status']==5888
assert hand['window']==ack['window']==witness['window'] and hand['counter']['used']==used
put('C09_ACTUAL_HANDOFF.json',{'status':'PASS_REAL_C09_HANDOFF','stage':hand['stage'],'classification_count':hand['classification_count'],
    'sender':hand['sender'],'receiver':hand['receiver'],'coordinator':hand['coordinator'],'window':hand['window'],
    'acknowledged_at':ack['acknowledged_at'],'exit_witness_sample':witness['sample'],'raw_wait_status':5888,'exit_code':23,
    'verified_update':hand['updated'],'C09_result_sample':c09['sample'],'commit_sha256':h(R/'inputs/c09_commit.json'),
    'witness_sha256':h(R/'inputs/c09_exit_witness.json'),'regression_sha256':hand['regression_sha256'],
    'budget_snapshot':hand['counter'],'resume_attempt':'PARENT_ENTRY_VERIFIED_BUT_MANAGER_CHECK_REJECTED','resume_count':0,
    'handoff_vs_complete_continuity':'Actual handoff PASS; C10/service-resume qualification remains UNRUN'})

ready=[]
for p in sorted((R/'inputs/root_private/boot').glob('ready_C00_*.json')):
    d=load(p);ready.append({'file':p.relative_to(R).as_posix(),'begin':d['check_time_begin']['boottime'],'end':d['check_time_end']['boottime'],'phases':d['phases'],'result':d['overall_result'],
        'pid':d['process_pid'],'start_ticks':d['process_starttime'],'checks':d['checks'],'sha256':h(p)})
assert all(row['result']=='MATCH' for row in ready[-1]['checks'])
cert=load(R/'inputs/C00_READINESS.json');until=cert['readiness_until'];request=until-14
firstready=next(d for d in ready if d['result']=='READY');confirmation=ready[-1]
put('C00_ACTUAL_FIELDS_AND_TIMING.json',{'status':'C00_PASS','run_boot_id':boot,'samples':ready,'request_time_inferred':request,
    'inference':'until=start+14; other window boundaries are later','wait_return_interval':[firstready['end']-request,confirmation['begin']-request],
    'second_validation_end_from_request':confirmation['end']-request,'pidfd_separate_times':'UNRECORDED','diagnostic_integrity':'FIELD_EVIDENCE_PARTIAL'})

# Journal has its own MONOTONIC clock. Do not combine absolute times with BOOTTIME.
jrows=[]
for line in (E/'FINAL_RUN_BOOT_JOURNAL.stdout.raw').read_text(encoding='utf-8',errors='replace').splitlines():
    d=json.loads(line);assert d['_BOOT_ID']==boot.replace('-','')
    unit=d.get('UNIT') or d.get('_SYSTEMD_UNIT')
    jrows.append({'unit':unit,'message':d.get('MESSAGE'),'monotonic_seconds':int(d['__MONOTONIC_TIMESTAMP'])/1e6,
        'exit_code':d.get('EXIT_CODE'),'exit_status':d.get('EXIT_STATUS'),'job_result':d.get('JOB_RESULT')})
put('JOURNAL_TIMELINE.json',{'clock':'journal MONOTONIC','boot':boot,'rows':jrows})
durations=[]
for case in ['C%02d'%i for i in range(13)]+['C09H','RANGE']:
    path=R/'inputs'/('result_'+case+'.json');unit='dclr6batch09-'+case.lower()+'.service'
    rows=[d for d in jrows if d['unit']==unit]
    starting=next((d['monotonic_seconds'] for d in rows if str(d['message']).startswith('Starting ')),None)
    active=next((d['monotonic_seconds'] for d in rows if str(d['message']).startswith('Started ')),None)
    terminal=next((d['monotonic_seconds'] for d in rows if 'Deactivated successfully.' in str(d['message']) or 'Failed with result' in str(d['message'])),None)
    result=load(path) if path.exists() else None
    timing_path=R/'out'/(case+'.timing.json');timing=load(timing_path).get('timing',{}) if timing_path.exists() else {}
    fsync={k:{key:v[key] for key in ['count','total_ns','max_ns']} for k,v in timing.items() if k.endswith('.fsync')}
    child_path=R/'out'/(case+'.child_process.json');child=load(child_path) if child_path.exists() else None
    durations.append({'case_id':case,'status':result['status'] if result else 'UNRUN_AFTER_RESUME_FAILURE',
        'journal_start':starting,'journal_active':active,'journal_terminal':terminal,
        'service_startup_span':active-starting if active is not None and starting is not None else None,
        'service_active_to_terminal_span':terminal-active if terminal is not None and active is not None else None,
        'service_envelope_span':terminal-starting if terminal is not None and starting is not None else None,
        'Root_result_sample':result.get('sample') if result else None,'child_span':child.get('observed_process_span_ns',0)/1e9 if child else None,
        'fsync_aggregates':fsync,'fsync_count':sum(v['count'] for v in fsync.values()),'fsync_total_seconds':sum(v['total_ns'] for v in fsync.values())/1e9,
        'timing_scope':'Instrumented stages only; categories can overlap; pure program/wait/cleanup/write split UNMEASURED when no separate markers'})
put('CASE_DURATIONS.json',{'clock_policy':'journal service spans MONOTONIC; child/Root samples BOOTTIME; each span uses its own clock',
    'cases':durations,'Root_suites':[{k:v for k,v in d.items() if k!='rows'} for d in suites],
    'incomplete_timing_categories':'Pure execution, supervision, cleanup and writing are partial; no synthetic exact split'})

peaks=[];tasks=[];caps=[]
def walk(x,path):
    if isinstance(x,dict):
        if 'values' in x and isinstance(x['values'],dict):
            v=x['values']
            if str(v.get('memory.peak','')).isdigit():peaks.append({'bytes':int(v['memory.peak']),'source':path})
            if str(v.get('pids.current','')).isdigit():tasks.append({'tasks':int(v['pids.current']),'source':path})
        for k,v in x.items():walk(v,path+'/'+k)
    elif isinstance(x,list):
        for i,v in enumerate(x):walk(v,path+'/'+str(i))
for p in (R/'out').glob('C*.json'):
    try:walk(load(p),p.relative_to(R).as_posix())
    except (ValueError,UnicodeDecodeError):pass
for p in (R/'inputs').glob('result_C*.json'):walk(load(p),p.relative_to(R).as_posix())
peak=max(peaks,key=lambda d:d['bytes']);max_tasks=max(tasks,key=lambda d:d['tasks'])
put('RESOURCE_ACCOUNTING.json',{'T0':t0,'deadline':state['deadline'],'stop_at':state['stop_at'],'used':used,'cap':cap,
    'global_transactions':len(transactions),'journal_lines':len(journal),'peak_observed_charged_memory':peak,'max_observed_tasks':max_tasks,
    'exact_RSS_tree_peak':'UNMEASURED','Root_RSS_peak':'UNMEASURED','C09_completed_from_T0':c09['sample']['boottime']-t0,
    'failure_from_T0_interval':[failure_lo-t0,failure_hi-t0],'CLOSED_marker_from_T0':closed['boottime']-t0,
    'frozen_cleanup_finish_from_T0':cleanup['cleanup_finished']-t0,'close_to_all_roles_empty':cleanup['cleanup_finished']-closed['boottime'],
    'close_reason':closed['reason'],'state_document_status_retained':state['status'],'CLOSED_marker_authoritative':True,
    'initial_automatic_close':False,'supplemental_frozen_cleanup':True,'controlled_roles_final_empty':finalaudit['controlled_roles_empty'],
    'budget_unchanged_during_cleanup':cleanup['budget_unchanged'],'calibration_complete':False,'RESOURCE_GATE_PASS':'NOT_OBTAINED'})

manifest=load(R/'out/EVIDENCE_MANIFEST.json');errors=[]
with zipfile.ZipFile(R/'out/EVIDENCE.zip') as z:
    for name,digest in manifest['files'].items():
        if isinstance(digest,dict):digest=digest['sha256']
        if hashlib.sha256(z.read(name)).hexdigest()!=digest:errors.append(name)
    entries=len(z.namelist())
put('NATIVE_ZIP_CHECK.json',{'manifest_rows':len(manifest['files']),'ZIP_entries':entries,'errors':errors,'bytes':(R/'out/EVIDENCE.zip').stat().st_size,'sha256':h(R/'out/EVIDENCE.zip'),'seal_origin':'Authorized frozen cleanup invoked guard.seal after initial automatic seal absent'})
assert not errors
put('CALDIAG_RESULT.json',{'status':'RESOURCE_GATE_FAILED','failure_class':'VERIFICATION_INFRASTRUCTURE_RESUME_MANAGER_AND_FAILURE_CLOSURE',
    'TIME_FEASIBILITY':'TIME_FEASIBILITY_UNRESOLVED_EARLY_FAILURE','completed_C_cases':['C%02d'%i for i in range(10)],
    'READY64':{'PASS':47,'MUTATION_DETECTED':17},'C09H34':{'PASS':28,'MUTATION_DETECTED':6},
    'RootIPC56':{'PASS':48,'MUTATION_DETECTED':8},'BC40':{'PASS':30,'MUTATION_DETECTED':10},
    'C10_C12':'UNRUN_AFTER_RESUME_FAILURE','S34':'UNRUN_AFTER_RESUME_FAILURE','GATE18':'UNRUN_AFTER_RESUME_FAILURE',
    'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
    'R':used,'T0':t0,'run_boot_id':boot,'active_entry_calls':1,'test_retries':0,'source_repairs':0,
    'internal_resume_attempts':1,'successful_resumes':0,'CLOSED_marker':True,'final_processes_empty':True,
    'IMPLEMENTATION_GATE':'CLOSED','STRICT_SEPARATION_INSTANCES':0})
print(json.dumps({'R':used,'transactions':len(transactions),'journal_lines':len(journal),'native_audit_counts':[{k:d[k] for k in ['receipt','counts','visits','charged_work_observed_span']} for d in suites],
    'failure_from_T0':[failure_lo-t0,failure_hi-t0],'C09_completed_from_T0':c09['sample']['boottime']-t0,'CLOSED_from_T0':closed['boottime']-t0,
    'cleanup_finish_from_T0':cleanup['cleanup_finished']-t0,'peak_observed_charged_bytes':peak['bytes'],'max_tasks':max_tasks['tasks'],
    'native_zip_rows':len(manifest['files']),'native_zip_entries':entries,'actual_target_oracle_reruns':0},ensure_ascii=False))
