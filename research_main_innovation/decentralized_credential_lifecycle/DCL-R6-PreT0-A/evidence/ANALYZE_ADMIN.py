"""Read and hash preserved originals only; no subject/oracle imports or replay."""
from pathlib import Path
import hashlib,json,struct,zipfile
from datetime import datetime
E=Path(__file__).resolve().parent;B=E.parent.parent
N=Path(r'D:\毕业设计\DCL-R6-isolated-verification\batch11\native_snapshot')
W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\pt01')
def load(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def put(name,x):
    with (E/name).open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
state=load(N/'inputs/batch_state.json');cp=load(N/'inputs/PT_RUNTIME_CHECKPOINT.json')
events=[json.loads(x) for x in (N/'inputs/root_private/boot/pt_events.jsonl').read_bytes().splitlines()]
assert [x['phase'] for x in events]==['PRE_WINDOW','PREFLIGHT_VALIDATING','PREFLIGHT_QUALIFIED','RUNTIME_INITIALIZING','RUNTIME_READY','RUNTIME_ARMED']
for i,q in enumerate(events):
    assert q['sequence']==i and q['previous_sha256']==(hashlib.sha256(canon(events[i-1])).hexdigest() if i else None)
intent=load(N/'inputs/root_private/boot/pt_runtime_intent.json');context=load(N/'inputs/root_private/boot/pt_context.json')
assert hashlib.sha256(canon(intent)).hexdigest()==cp['initialization_id']
assert cp['window']=={k:state[k] for k in ('T0','deadline','stop_at')} and cp['phase']==events[-1]['phase']
raw=(N/'out/visits.bin').read_bytes();magic=raw[:8];used,cap=struct.unpack('<QQ',raw[8:])
assert magic==b'BRNGv001' and used==0 and cap==1000000
assert load(N/'out/visits.bin.intent.json')=={'after':0,'cap':1000000,'protocol':'EXACT-RANGE/1','status':'COMMITTED'}
assert not (N/'out/visits.bin.journal.jsonl').exists()
assert not list(N.rglob('pt_case_*.json')) and not list(N.rglob('*PT_QUALIFICATION*')) and not list(N.rglob('ticket_C00.json'))
manifest=load(N/'out/EVIDENCE_MANIFEST.json');native_errors=[];native_disk=[]
with zipfile.ZipFile(N/'out/EVIDENCE.zip') as z:
    assert z.testzip() is None
    assert z.read('out/EVIDENCE_MANIFEST.json')==(N/'out/EVIDENCE_MANIFEST.json').read_bytes()
    for name,row in manifest['files'].items():
        a=z.read(name)
        if len(a)!=row['bytes'] or hashlib.sha256(a).hexdigest()!=row['sha256']:native_errors.append(name)
        if sha(N/name)!=row['sha256']:native_disk.append(name)
    native_entries=len(z.namelist())
assert not native_errors and not native_disk
put('NATIVE_SEAL_VERIFICATION.json',{'status':'NATIVE_SEAL_COMPLETED','method':'Read-only stream verification of actual frozen native artifact; no replay',
 'manifest_rows':len(manifest['files']),'zip_entries':native_entries,'manifest_sample':manifest['sample'],'errors':native_errors,
 'postexit_disk_changes':native_disk,'manifest_sha256':sha(N/'out/EVIDENCE_MANIFEST.json'),'zip_sha256':sha(N/'out/EVIDENCE.zip'),
 'zip_bytes':(N/'out/EVIDENCE.zip').stat().st_size,'earlier_disposition':load(N/'inputs/root_private/boot/pt_seal_disposition.json'),
 'automatic_host_finalizer_native_status':load(E/'STARTUP_FINALIZATION.json')['native_seal_status']})
source=load(E/'SOURCE_AND_SCOPE_ADMISSION.json')['files'];source_errors=[]
for row in source:
    for base in [W,E/'FROZEN_SOURCE_REFERENCE',Path(r'D:\毕业设计\DCL-R6-isolated-verification\batch11\FROZEN_PT')]:
        if sha(base/row['relative'])!=row['sha256']:source_errors.append(str(base/row['relative']))
assert not source_errors
put('SOURCE_AFTER_CHECK.json',{'status':'MATCH','files':51,'programs':35,'source_errors':source_errors,'pyc_files':[str(p) for p in W.rglob('*.pyc')],'source_edits':0})
stops=[(p.name,load(p)) for p in N.glob('inputs/stop_result_*.json')]
attempts=[json.loads(x) for x in (N/'inputs/root_private/boot/mr_close_attempts.jsonl').read_bytes().splitlines()]
journal=[json.loads(x) for x in (E/'RUN_BOOT_JOURNAL.stdout.raw').read_bytes().splitlines()]
journal_brief=[{'journal_monotonic_seconds':int(q['__MONOTONIC_TIMESTAMP'])/1e6,'pid':q.get('_PID'),'message':q.get('MESSAGE'),'realtime_us':q.get('__REALTIME_TIMESTAMP')} for q in journal]
put('JOURNAL_MESSAGE_INDEX.json',journal_brief)
first=load(N/'inputs/root_private/boot/mr_first_failure.json');stop=load(N/'out/STOP_REQUEST.json');closed=load(N/'inputs/CLOSED.json')
wait=load(N/'inputs/root_private/waitpid_887.json');final=load(N/'inputs/root_private/boot/mr_close_state.json')
root_exit=[x for a in attempts for x in a.get('other_roles',{}).get('targets',[]) if x.get('exit_observed')]
data={'batch_id':'batch11','revision':'PreT0Recovery-static-1/r3','mode':'NORMAL_START','result':'FAILED_FIRST_UNEXPECTED_RUNTIME_ARMING_RACE',
 'boot_id':state['boot_id'],'entry_calls':1,'preflight':'PASS_ACTUAL','same_pid_exec':'PASS_ACTUAL','owner':state['coordinator_identity'],
 'scheduler':state['launcher_identity'],'external_stop':load(N/'inputs/STOP_ARMED.json')['identity'],
 'phases':events,'context_T0':context['T0'],'context_R':context['R'],'T0':state['T0'],'deadline':state['deadline'],'stop_at':state['stop_at'],
 'preflight_deadline':context['preflight_deadline'],'startup_begin':context['startup_begin_inferred'],'intent_sample':intent['sample'],
 'checkpoint_sample':cp['sample'],'R':used,'counter_cap':cap,'counter_initialized':True,'journal_present':False,'charged_transactions':0,
 'first_causal_error':'PT_RUNTIME_PHASE_DRIFT','causal_source':'Frozen external-stop service traceback, guard.py:777 -> c09_handoff.py:207 -> startup_lifecycle.py:184',
 'causal_error_time':'Exact throw time unavailable; phase-publication/STOP bracket in same boot','immutable_first_failure':first,
 'stop':stop,'closed':closed,'waitpid':wait,'closure_attempts':attempts,'internal_final':final,'stop_results':dict(stops),
 'C00':'UNRUN_BEFORE_DISPATCH','PT_jobs_executed':0,'PT_jobs_accepted':0,'PT_mutants_exercised':0,'PT_mutants_detected':0,
 'prewindow_abort':'UNRUN_MUTUALLY_EXCLUSIVE_MODE','startup_deadline_expiry':'UNRUN','work_grants':0,'RUNNING_entered':False,
 'manual_cleanup_calls':0,'fallback_cleanup_calls':0,'retries':0,'new_budget_windows_after_failure':0,
 'postexit_finalization':load(E/'STARTUP_FINALIZATION.json'),'postexit_error':'ModuleNotFoundError: boot_continuity',
 'native_seal_status':'NATIVE_SEAL_COMPLETED','automatic_admin_status':'ADMIN_EVIDENCE_UNRESOLVED',
 'manual_administrative_archive':'Prepared separately after failure; not automatic success',
 'first_group_absent':min(q['sample']['boottime'] for _,q in stops if not q['after_stop_group_exists']),
 'journal_last_external_exit':next(q for q in journal_brief if 'Main process exited' in q['message']),
 'run_host_active':load(E/'WINDOWS_ENTRY_EXIT.json'),'run_host_including_finalizer':load(E/'ACTIVE_ENTRY_RETURN.json'),
 'charged_memory_peak_observed':0,'payload_tasks_observed':0,'root_RSS_peak':None,'root_roles_concurrent_upper_bound_inferred':3,
 'observation_limits':'Payload empty slice only; Root processes run outside payload slice. No whole-tree RSS/task high-water evidence.',
 'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
 'IMPLEMENTATION_GATE':'CLOSED','STRICT_SEPARATION_INSTANCES':0}
put('ACTUAL_RESULTS.json',data)
timeline=[]
def add(event,t,origin,kind='NATIVE_BOOTTIME'):
    timeline.append({'event':event,'time':t,'clock':kind,'T0_offset':t-state['T0'] if kind=='NATIVE_BOOTTIME' else None,'origin':origin})
add('Startup120s TCB begins',context['startup_begin_inferred'],'sealed preflight deadline minus120')
for q in events:add(q['phase'],q['sample']['boottime'],'pt_events.jsonl sequence'+str(q['sequence']))
add('runtime intent sample',intent['sample']['boottime'],'pt_runtime_intent.json; durability before INITIALIZING event')
add('T0',state['T0'],'batch_state.json')
for name,q in [('public armed checkpoint sample',cp['sample']),('STOP_REQUEST',stop),('first-failure latch',first['sample']),('CLOSED',closed),('waitpid child125',wait['sample']),('final internal cleanup confirmed',final['sample']),('native manifest sample',manifest['sample'])]:add(name,q['boottime'],name)
for name,q in stops:add(name,q['sample']['boottime'],name)
timeline.sort(key=lambda r:r['time']);put('EXECUTION_TIMELINE.json',{'events':timeline,'journal':journal_brief,
 'cross_clock_caution':'Guest BOOTTIME and journal MONOTONIC are separately labelled; host/guest UTC offsets are observations, not exact cross-clock durations',
 'exact_last_exit_time':'Journal systemd exit witness67.405716; exact kernel exit instant unavailable'})
archive_checks=[]
for name,zipname in [('DCL-R6-PreT0-Fix','PRET0_EVIDENCE.zip'),('DCL-R6-MR-A','MRA_EVIDENCE.zip'),('DCL-R6-ManagerRecovery-Fix','MANAGERRECOVERY_EVIDENCE.zip'),('DCL-R6-CalDiag','CALDIAG_EVIDENCE.zip')]:
    folder=B/name;zpath=folder/zipname
    if not zpath.exists():
        choices=list(folder.glob('*EVIDENCE.zip'));assert len(choices)==1;zpath=choices[0]
    rows=load(folder/'OUTPUT_MANIFEST.json');rows=rows.get('files',rows) if isinstance(rows,dict) else rows;errors=[]
    with zipfile.ZipFile(zpath) as z:
        for row in rows:
            if hashlib.sha256(z.read(row['archive_path'])).hexdigest()!=row['sha256']:errors.append(row['archive_path'])
        count=len(z.namelist())
    assert not errors;archive_checks.append({'stage':name,'members':len(rows),'zip_entries':count,'zip_sha256':sha(zpath),'errors':errors})
put('HISTORICAL_ARCHIVE_CHECK.json',archive_checks)
print(json.dumps({'status':'ADMIN_ANALYSIS_COMPLETE','native_members':44,'native_entries':45,'native_integrity':'PASS',
 'T0':state['T0'],'R':used,'tests':0,'mutants':0,'internal_final':final['status'],'archives_verified':len(archive_checks)},ensure_ascii=False))
