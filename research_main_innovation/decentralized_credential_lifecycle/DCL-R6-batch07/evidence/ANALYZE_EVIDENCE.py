"""Offline raw evidence parsing; no target import, replay, or new platform action."""
from pathlib import Path
import hashlib
import json
import struct
import zipfile

E=Path(__file__).resolve().parent
N=Path(r'D:\毕业设计\DCL-R6-isolated-verification\batch07\native_snapshot')
F=N.parent/'FROZEN_BOOTCONTINUITY'
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(name,x):(E/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

raw=(E/'windows_entry.stdout.raw').read_bytes()
events=[json.loads(s) for s in raw.decode('utf-8').splitlines() if s.strip()]
assert len({r['identity']['boot_id'] for r in events})==1
assert len({(r['identity']['pid'],r['identity']['start_ticks']) for r in events})==1
run_boot=events[0]['identity']['boot_id'];owner=events[0]['identity']
exit_record=load(E/'WINDOWS_ENTRY_EXIT.json');assert exit_record['exit_code']==125
err=(E/'windows_entry.stderr.raw').read_bytes();mark=err.find(b'Traceback (most recent call last):')
assert mark>=0
prefix=err[:mark];trace=err[mark:].decode('utf-8',errors='replace')
assert 'BC_SERVICE_IDENTITY_OR_LIMITS' in trace
encoding='utf-16-le' if b'\x00' in prefix else 'utf-8'
dump('STDERR_DECODE.json',{'schema':'B07-stderr-decoding/1','raw_sha256':sha(E/'windows_entry.stderr.raw'),
 'prefix_encoding':encoding,'prefix':prefix.decode(encoding,errors='replace'),'native_trace_encoding':'utf-8','native_trace':trace,
 'original_raw_unchanged':True,'exec_tool_reported_exit':1,'frozen_wrapper_reported_WSL_exit':125})
decoded=E/'internal_commands';decoded.mkdir(exist_ok=True)
rows=[]
for r in events:
    if r['event']!='PREFLIGHT_COMMAND':continue
    i=len(rows)+1
    item={'order':i,'argv':r['argv'],'start':r['start'],'after':r['sample'],'identity':r['identity'],'exit_code':r['exit_code']}
    for stream in ['stdout','stderr']:
        b=bytes.fromhex(r[stream+'_hex']);p=decoded/f'{i:02}.{stream}.raw';p.write_bytes(b)
        item[stream+'_file']=p.relative_to(E.parent).as_posix();item[stream+'_sha256']=hashlib.sha256(b).hexdigest()
    rows.append(item)
assert len(rows)==15 and all(r['exit_code']==0 for r in rows)
dump('INTERNAL_COMMANDS.json',{'schema':'B07-inner-command-index/1','commands':rows,'scope':'Actual command telemetry from the single active WSL flow'})
state=load(N/'inputs/batch_state.json');closed=load(N/'inputs/CLOSED.json');armed=load(N/'inputs/STOP_ARMED.json')
activation=load(N/'inputs/root_private/boot/activation.json');ticket=activation['ticket'];cap=load(N/'inputs/root_private/boot/capability.json')
entry=load(N/'inputs/root_private/boot/entry_initial.json');child=load(N/'inputs/root_private/boot/child_initial.json')
final=load(N/'inputs/root_private/boot/final_before_seal.json')
static=load(N/'inputs/root_private/boot/static_A.json')
assert owner==ticket['owner']==entry['owner']==child['parent']==state['coordinator_identity']
assert ticket['boot_id']==run_boot==state['boot_id']==closed['boot_id']
canonical=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')).encode()
assert hashlib.sha256(canonical(ticket)).hexdigest()==cap['sha256']==entry['ticket_sha256']
assert cap['seals']==15 and activation['initial_entered'] is True and activation['resume_issued'] is False
before_event=next(r for r in events if r['event']=='ACTIVATION_REQUESTED_ONLY')
after_event=next(r for r in events if r['event']=='ENTRY_VERIFIED')
assert before_event['identity']==after_event['identity']==owner
assert after_event['sample']['boottime']<ticket['expires']
assert not any(r['event']=='ACTUAL_SERVICE_CONFIRMED' for r in events)
assert not (N/'inputs/BOOT_START.json').exists()
dump('BOOT_CONTINUITY_ACTUAL.json',{
 'schema':'B07-boot-prefix/1','scope':'Observed preflight/exec/Guard admission only; service confirmation failed',
 'boot_id':run_boot,'owner_before_exec':before_event['identity'],'owner_after_exec':after_event['identity'],
 'same_PID_start_ticks':True,'same_boot_observed':True,'capability_sha256':cap['sha256'],'seals':cap['seals'],
 'ticket_issued_at':ticket['issued_at'],'ticket_expires':ticket['expires'],'preflight_deadline':ticket['preflight_deadline'],
 'initial_claim_entered':activation['initial_entered'],'resume_issued':activation['resume_issued'],
 'duplicate_claim_test':'UNRUN','entry_private_time':entry['sample']['boottime'],
 'preflight_begin':events[0]['sample']['boottime'],'entry_event_time':after_event['sample']['boottime'],
 'observed_prefix_seconds':after_event['sample']['boottime']-events[0]['sample']['boottime'],
 'child_identity':child['child'],'service_certificate_exists':False,'full_preflight_service_boot_equality':'NOT_VERIFIED_SERVICE',
 'native_syntax_sources':20,'native_syntax_evidence':'Control-flow witness: artifact_check completed before PREFLIGHT_QUALIFIED and ENTRY_VERIFIED',
 'static_objects_freshly_hashed':len(static['object_digests']),'nonce_in_ordinary_summary':False})
counter=(N/'out/visits.bin').read_bytes();assert len(counter)==24 and counter[:8]==b'BRNGv001'
used,cap_value=struct.unpack('<QQ',counter[8:]);intent=load(N/'out/visits.bin.intent.json')
assert used==0 and cap_value==1000000 and intent['after']==0 and intent['cap']==cap_value and intent['status']=='COMMITTED'
assert not (N/'out/visits.bin.journal.jsonl').exists()
cleanup=[load(q) for q in sorted((N/'inputs').glob('stop_result_*.json'))]
assert len(cleanup)==2 and all(q['empty'] and q['stop_exit']==0 and q['closure_persistence_error'] is None for q in cleanup)
first_cleanup=min(cleanup,key=lambda q:q['sample']['boottime'])
wait_files=list((N/'inputs/root_private').glob('waitpid_*.json'));assert len(wait_files)==1
wait=load(wait_files[0]);assert wait['raw_wait_status']==32000 and wait['exit_code']==125
assert not (N/'inputs/ticket_C00.json').exists()
values=first_cleanup['before_stop_charged_snapshot']['values']
dump('RESOURCE_ACCOUNTING.json',{'schema':'B07-accounting/1','R':used,'cap':cap_value,'T0':state['T0'],
 'deadline':state['deadline'],'stop_at':state['stop_at'],'journal_records':0,'committed_transactions':0,
 'intent_status':intent['status'],'status':'PASS_INITIALIZED_ZERO_ACCOUNTING_ONLY',
 'closed_time':closed['boottime'],'closed_T0':closed['boottime']-state['T0'],
 'first_empty_time':first_cleanup['sample']['boottime'],'first_empty_T0':first_cleanup['sample']['boottime']-state['T0'],
 'closed_to_empty_seconds':first_cleanup['sample']['boottime']-closed['boottime'],
 'waitpid_time':wait['sample']['boottime'],'waitpid_T0':wait['sample']['boottime']-state['T0'],
 'final_before_seal_time':final['sample']['boottime'],'final_before_seal_T0':final['sample']['boottime']-state['T0'],
 'observed_charged_peak_bytes':int(values['memory.peak']),'observed_pids_current':int(values['pids.current']),
 'pids_max':int(values['pids.max']),'memory_max':int(values['memory.max']),'exact_RSS_tree_peak':None,
 'Root_RSS_peak':None,'host_active_call_elapsed_ns':exit_record['host_elapsed_ns'],
 'STOP_REQUEST_present':False,'STOP_REQUEST_to_Root_exit':'N/A',
 'clock_scope':'BOOTTIME for native elapsed; journal MONOTONIC separately; host perf_counter separately',
 'refunds':0,'resets':0,'resume':state['resume_count'],'model_searches':0,'semantic_visits':0})
manifest=load(N/'out/EVIDENCE_MANIFEST.json')
with zipfile.ZipFile(N/'out/EVIDENCE.zip') as z:
    for rel,row in manifest['files'].items():
        b=z.read(rel);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
        assert sha(N/rel)==row['sha256']
    assert z.read('out/EVIDENCE_MANIFEST.json')==(N/'out/EVIDENCE_MANIFEST.json').read_bytes()
    dump('NATIVE_ZIP_CHECK.json',{'schema':'B07-native-seal/1','status':'PASS_ADMIN_ONLY','manifest_rows':len(manifest['files']),
         'entries':len(z.namelist()),'sha256':sha(N/'out/EVIDENCE.zip'),'bytes':(N/'out/EVIDENCE.zip').stat().st_size,'mismatches':[]})
journal=load(E/'RUN_BOOT_JOURNAL_CORRECTED_RESULT.json')
jrows=[json.loads(s) for s in journal['stdout'].splitlines() if s.strip()]
assert journal['exit_code']==0 and all(r['_BOOT_ID']==run_boot.replace('-','') for r in jrows)
brief=[{'unit':r.get('UNIT',r.get('_SYSTEMD_UNIT')),'mono_us':int(r['__MONOTONIC_TIMESTAMP']),
        'realtime_us':int(r['__REALTIME_TIMESTAMP']),'message':r['MESSAGE']} for r in jrows]
dump('JOURNAL_SUMMARY.json',{'schema':'B07-journal/1','boot_id':run_boot,'records':brief,
 'earlier_query':'Preserved invalid hyphenated --boot descriptor parse rejection; corrected32-hex query is read-only',
 'C00_started_record':any(r['message'].startswith('Started dclr6batch07-c00.service') for r in brief),
 'current_boot_manager_defaults_not_used_for_runtime_inference':True})
failure={'schema':'B07-first-failure/1','phase':'C00_SERVICE_CONFIRMATION_BEFORE_TICKET',
 'error':'BC_SERVICE_IDENTITY_OR_LIMITS','run_boot_id':run_boot,'C00_start_requested':True,'C00_probe_executed':False,
 'ticket_C00_exists':False,'BOOT_START_exists':False,'native_exit':125,'raw_child_wait_status':32000,
 'precise_failed_predicate':'UNRESOLVED: 8-way metadata disjunction was not logged',
 'startup_readiness_gap':'SOURCE_CONFIRMED: launch_one accepts any MainPID>0 after --no-block before exec-ready barrier',
 'timing_race_causality':'SUPPORTED_HYPOTHESIS: Starting-only journal and tiny charged peak; exact mismatch unavailable',
 'C00_Started_journal_record':False,'CLOSED':closed,'R':0,'T0':state['T0'],
 'retries':0,'postfailure_code_or_permission_changes':0,'new_batch08':False}
dump('FIRST_FAILURE.json',failure)
dump('ACTUAL_RESULTS.json',{'schema':'B07-results/1','preflight':'PREFLIGHT_QUALIFIED','exec':'OBSERVED_SAME_PID_BOOT',
 'startup_gate':'FAILED_SERVICE_IDENTITY_OR_LIMITS','resource':'RESOURCE_GATE_FAILED','RESOURCE_GATE_PASS':'NOT_OBTAINED',
 'BC40':{'planned':40,'attempted':0,'completed':0,'mutants_planned':10,'mutants_detected':0},
 'RootIPC56':{'planned':56,'attempted':0,'completed':0,'mutants_detected':0},
 'C09H34':{'planned':34,'attempted':0,'completed':0,'mutants_detected':0},'C09':'NOT_EXERCISED',
 'C00':'FAIL_STARTUP_GATE; probe UNRUN','C01_C12':'UNRUN_RESOURCE_GATE',
 'S34':{'planned':34,'attempted':0,'completed':0},'negative17':{'planned':17,'attempted':0,'detected':0},
 'F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],'model_searches':0,
 'R':0,'T0':state['T0'],'native_auto_seal':True,'active_WSL_entry_calls':1,'standalone_resume_calls':0,'new_batch08':False})
print(json.dumps({'events':len(events),'internal_logged_commands':len(rows),'native_files':len(load(E/'NATIVE_EXPORT_LOCK.json')['files']),
 'frozen_files':len(load(E/'FROZEN_SOURCE_EXPORT_LOCK.json')['files']),'run_boot':run_boot,'R':used,'T0':state['T0'],
 'closed_elapsed':closed['boottime']-state['T0'],'empty_elapsed':first_cleanup['sample']['boottime']-state['T0'],
 'native_zip':load(E/'NATIVE_ZIP_CHECK.json'),'journal_records':len(brief),'cause':'readiness gap supported; exact failed metadata unavailable'},ensure_ascii=False,indent=2))
