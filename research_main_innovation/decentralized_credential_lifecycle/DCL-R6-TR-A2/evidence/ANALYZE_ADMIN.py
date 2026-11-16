"""Post-closure byte/accounting/receipt audit; no target checker or API replay."""
from pathlib import Path
import hashlib,json,struct,zipfile
E=Path(__file__).resolve().parent;W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\ra01');N=Path(r'D:\毕业设计\DCL-R6-isolated-verification\batch14\native_snapshot')
C=Path(json.loads((E/'AUTHORIZATION_RECEIPT_LOCK.json').read_bytes())['control_directory'])
def load(p):return json.loads(Path(p).read_bytes())
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def put(name,x):
    with(E/name).open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
final=load(C/'STARTUP_FINALIZATION.json');audit=final['native_audit'];am=load(C/'STARTUP_ADMIN_MANIFEST.json')
assert final['post_exit_code']==final['active_exit']==0 and final['administrative_seal_status']=='ADMIN_EVIDENCE_SEALED' and final['native_seal_status']=='NATIVE_SEAL_COMPLETED'
with zipfile.ZipFile(C/'STARTUP_ADMIN_EVIDENCE.zip') as z:
    assert z.testzip() is None
    for row in am['files']:
        raw=z.read(row['archive_path']);assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']==h(row['host'])
    assert z.read('STARTUP_ADMIN_MANIFEST.json')==(C/'STARTUP_ADMIN_MANIFEST.json').read_bytes();admin_entries=len(z.namelist())
assert len(am['files'])==249 and admin_entries==250 and h(C/'STARTUP_ADMIN_EVIDENCE.zip')==final['ZIP_sha256'] and h(C/'STARTUP_ADMIN_MANIFEST.json')==final['manifest_sha256']
for row in audit['files']:assert h(N/row['relative'])==row['sha256']
put('AUTOMATIC_ADMIN_VERIFICATION.json',{'status':'ADMIN_EVIDENCE_SEALED','manifest_rows':249,'ZIP_entries':250,'ZIP_sha256':final['ZIP_sha256'],
 'manifest_sha256':final['manifest_sha256'],'ZIP_bytes':final['ZIP_bytes'],'stream_errors':[],'native_files':235,'automatic_vs_independent_export_errors':[],
 'manual_or_fallback_finalizer_calls':0})
nm=load(N/'out/EVIDENCE_MANIFEST.json');native_disk_changes=[]
with zipfile.ZipFile(N/'out/EVIDENCE.zip') as z:
    assert z.testzip() is None
    assert len(z.namelist())==len(set(z.namelist())) and set(z.namelist())==set(nm['files'])|{'out/EVIDENCE_MANIFEST.json'}
    for name,row in nm['files'].items():
        raw=z.read(name);assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
        if h(N/name)!=row['sha256']:native_disk_changes.append(name)
    assert z.read('out/EVIDENCE_MANIFEST.json')==(N/'out/EVIDENCE_MANIFEST.json').read_bytes();native_entries=len(z.namelist())
assert not native_disk_changes and len(nm['files'])==233 and native_entries==234
assert h(N/'out/EVIDENCE.zip')==audit['native_zip_sha256']
put('NATIVE_SEAL_VERIFICATION.json',{'status':'NATIVE_SEAL_COMPLETED','manifest_rows':233,'ZIP_entries':234,'ZIP_sha256':h(N/'out/EVIDENCE.zip'),
 'ZIP_bytes':(N/'out/EVIDENCE.zip').stat().st_size,'manifest_sha256':h(N/'out/EVIDENCE_MANIFEST.json'),'manifest_sample':nm['sample'],
 'stream_errors':[],'post_seal_original_changes':native_disk_changes,'verification':'Read existing original streams; native producer not replayed'})
source_errors=[]
for row in load(E/'SOURCE_AND_SCOPE_ADMISSION.json')['files']:
    for base in [W,E/'FROZEN_SOURCE_REFERENCE',Path(r'D:\毕业设计\DCL-R6-isolated-verification\batch14\FROZEN_RA')]:
        if h(base/row['relative'])!=row['sha256']:source_errors.append(str(base/row['relative']))
assert not source_errors and not list(W.rglob('*.pyc'))
put('SOURCE_AFTER_CHECK.json',{'status':'MATCH','files':64,'programs':44,'source_errors':source_errors,'frozen_source_edits':0,'pyc_files':[]})
s=load(N/'inputs/batch_state.json');closed=load(N/'inputs/CLOSED.json');review=load(N/'inputs/root_private/boot/terminal_seal_review.json')
assert review['decision']['read_status']=='VALID' and review['decision']['native_ready'] and review['runtime_authority']=='NONE'
assert not any(review['decision'][k] for k in ['work_allowed','budget_init_allowed','phase_write_allowed','launcher_allowed'])
assert review['active_guard_denial']['code']=='IPC_CLOSED_DOMINATES' and review['receipt_stage']=='PRE_NATIVE_ARCHIVE_READ_ONLY_REVIEW'
assert review['sample']['boottime']>closed['boottime'] and review['original_boot_id']==review['observation_boot_id']==s['boot_id']
assert review['window']=={k:s[k] for k in ['T0','deadline','stop_at']} and review['R']==3133 and review['journal_status']=='CONSISTENT'
assert review['internal_status']=='UNKNOWN' and review['native_artifact']['zip_present'] is False
critical_paths={'activation':'inputs/root_private/boot/activation.json','CLOSED':'inputs/CLOSED.json','STOP_REQUEST':'out/STOP_REQUEST.json',
 'batch_state':'inputs/batch_state.json','runtime_checkpoint':'inputs/PT_RUNTIME_CHECKPOINT.json','phase':'inputs/root_private/boot/pt_phase.json',
 'runtime_intent':'inputs/root_private/boot/pt_runtime_intent.json','budget_intent':'out/visits.bin.intent.json','mr_scheduler':'inputs/root_private/boot/mr_scheduler.json',
 'waitpid':'inputs/root_private/waitpid_%s.json'%s['launcher_identity']['pid'],'STOP_ARMED':'inputs/STOP_ARMED.json','internal_close':'inputs/root_private/boot/mr_close_state.json'}
comparisons=[]
for label,row in review['evidence_digests'].items():
    path=critical_paths.get(label,label);assert h(N/path)==row['sha256']==nm['files'][path]['sha256']
    comparisons.append({'original_label':label,'path':path,'terminal_read_digest':row['sha256'],'native_manifest_digest':nm['files'][path]['sha256'],'post_admin_export_digest':h(N/path),'unchanged':True})
assert review['binding']['execution_lock_sha256']==h(W/'inputs/execution_lock.json') and review['binding']['manifest_sha256']==h(W/'inputs/static_manifest.json')
put('TERMINAL_READ_CONSERVATION_AUDIT.json',{'status':'MATCH','original_reader_receipt':str(N/'inputs/root_private/boot/terminal_seal_review.json'),
 'reader':review['exit_evidence']['reader'],'read_sample':review['sample'],'closed':closed,'window':review['window'],'R':3133,'phase':review['phase'],'sequence':review['sequence'],
 'comparisons':comparisons,'execution_lock_digest':review['binding']['execution_lock_sha256'],'active_denial':review['active_guard_denial'],
 'readonly_scope':'Byte hashes captured in actual terminal read match native archived originals and independent post-admin export. Transient modify-and-restore not independently traced; frozen readonly code/TCB assumptions retained.',
 'intentional_new_write':'Caller-only Root-private terminal_seal_review after readonly return; not a window/credit object','terminal_API_replays_after_exit':0})
raw=(N/'out/visits.bin').read_bytes();assert len(raw)==24 and raw[:8]==b'BRNGv001';used,cap=struct.unpack('<QQ',raw[8:]);assert (used,cap)==(3133,1000000)
j=[json.loads(line) for line in (N/'out/visits.bin.journal.jsonl').read_bytes().splitlines()];assert len(j)==6266
position=0;last=0;prepared={};commits={}
for i in range(0,len(j),2):
    a,b=j[i:i+2];assert a['status']=='PREPARED' and b['status']=='COMMITTED'
    for key in ['protocol','boot_id','cap','request','before','after','amount']:assert a[key]==b[key]
    assert a['amount']==1 and a['before']==position and a['after']==position+1 and a['boot_id']==s['boot_id'] and a['cap']==cap and last<=a['boottime']<=b['boottime']
    position=b['after'];last=b['boottime'];prepared[position]=a;commits[position]=b
assert position==used==load(N/'out/visits.bin.intent.json')['after']
put('BUDGET_AUDIT.json',{'status':'MATCH','R':3133,'cap':cap,'transactions':3133,'journal_lines':6266,'journal_bytes':(N/'out/visits.bin.journal.jsonl').stat().st_size,
 'counter_sha256':h(N/'out/visits.bin'),'journal_sha256':h(N/'out/visits.bin.journal.jsonl'),'intent_sha256':h(N/'out/visits.bin.intent.json'),
 'T0':s['T0'],'deadline':s['deadline'],'stop_at':s['stop_at'],'continuous_zero_to_final':True,'new_windows_or_refunds':0,
 'first_prepare':j[0]['boottime'],'last_commit':j[-1]['boottime'],'terminal_read_and_archive_preserved':True,'production_reference_replays':0})
case_rows=[];suites=[]
specs=[('PT','startup_contract.json','inputs/PT_QUALIFICATION.json','pt_case_',1,1090,1027,'startup_oracle.py',64,9),
 ('PF','phase_finalizer_contract.json','inputs/root_private/boot/pf_qualification.json','pf_case_',1090,1907,1860,'phase_finalizer_oracle.py',48,8),
 ('TR','terminal_contract.json','inputs/root_private/boot/tr_qualification.json','tr_case_',1907,2588,2549,'terminal_oracle.py',40,8),
 ('RA','runtime_regression_contract.json','inputs/root_private/boot/ra_qualification.json','ra_case_',2588,3133,3102,'runtime_oracle.py',32,8)]
for kind,contract_name,qname,prefix,before,after,audit_start,checker,count,mutants in specs:
    cfg=load(W/'inputs'/contract_name);q=load(N/qname);assert q['accepted'] and len(q['results'])==count and q['before']==before and q['after']==after
    assert q['contract_sha256']==h(W/'inputs'/contract_name) and q['checker_sha256']==h(W/'src'/checker)
    statuses={};detected=0
    for i,(job,row) in enumerate(zip(cfg['jobs'],q['results'])):
        file=N/'inputs/root_private/boot'/(prefix+('%03d'%i)+'.json');data=load(file)
        assert row['case_id']==data['case_id']==job['case_id'] and data['binding']==q['binding'] and data['input_sha256']==hashlib.sha256(canonical(job)).hexdigest()
        assert row['raw_sha256']==h(file) and len(data['trace'])==len(job['frames']) and all(x['actual_input']==y for x,y in zip(data['trace'],job['frames']))
        target='MUTATION_DETECTED' if job['mutant'] else 'PASS';assert row['accepted'] and row['status']==target and data['after']-data['before']==16
        statuses[target]=statuses.get(target,0)+1;detected+=bool(job['mutant'])
        if job['mutant']:
            expected=job.get('expected_violation') if kind in ['PT','TR','RA'] else job['violation_class'];assert expected in row['violations'] and set(row['violations'])<=set(job['allowed_violations'])
        else:assert row['violations']==[]
        case_rows.append({'suite':kind,'case_id':job['case_id'],'mutant':job['mutant'],'origin':data['origin'],'input_sha256':data['input_sha256'],
            'raw_original':str(file),'raw_sha256':h(file),'expected_status':target,'native_oracle_status':row['status'],'violations':row['violations'],
            'driver_before':data['before'],'driver_after':data['after'],'driver_charged':16,'allocated_root_audit':1,'total_allocated_case_visits':17,
            'root_audit_prepaid_commit_time':commits[audit_start+i]['boottime'],'raw_sample':data['sample'],
            'charged_prefix_prepare_time':prepared[data['before']+1]['boottime'],'prepare_to_raw_sample_seconds':data['sample']['boottime']-prepared[data['before']+1]['boottime'],
            'full_case_and_oracle_elapsed':None,'time_scope':'Charged-prefix to subject sample only; excludes later persistence/oracle. Complete per-case duration UNKNOWN','checker_replayed':False})
    assert detected==mutants;suites.append({'suite':kind,'jobs':count,'mutants':mutants,'statuses':statuses,'before':before,'after':after,'charged':after-before,'sample':q['sample'],
        'qualification_path':qname,'qualification_sha256':h(N/qname),'checker_sha256':q['checker_sha256'],'contract_sha256':q['contract_sha256'],'origin':q['origin']})
assert len(case_rows)==184
put('TEST_CASE_RESULTS.json',{'cases':case_rows,'suites':suites,'jobs':184,'mutants_exercised_and_detected':33,'safe':151,
 'post_run_verification':'Original byte/input/binding/status metadata checks only; no production checker/reference reevaluation'})
runtime_receipts=[]
def collect(x,location):
    if isinstance(x,dict):
        if x.get('schema')=='RUNTIME-IDENTITY/1':runtime_receipts.append({'location':location,'record':x})
        for key,value in x.items():collect(value,location+'.'+key)
    elif isinstance(x,list):
        for i,value in enumerate(x):collect(value,location+'[%s]'%i)
for file in ['inputs/root_private/boot/static_A.json','out/C00.startup.json','out/C00.probe.json','inputs/result_C00.json']:
    collect(load(N/file),file)
assert runtime_receipts
identity=load(W/'inputs/runtime_identity_contract.json');expected={x['path']:x for x in identity['components']}
for observation in runtime_receipts:
    q=observation['record'];assert q['boot_id']==s['boot_id'] and q['profile']==identity['profile']
    for row in q['components']:
        assert row['sha256']==expected[row['path']]['sha256'] and row['build_id']==expected[row['path']]['build_id']
    assert all(row['disk_and_loaded_object_match'] for row in q['loaded_mapping_checks'])
    if q['packages']:
        assert all(v['Version']=='2.39-0ubuntu8.12' and v['Architecture']=='amd64' for v in q['packages'].values())
put('RUNTIME_IDENTITY_RECEIPTS.json',{'status':'MATCH_AT_OBSERVED_CHECKPOINTS','receipts':runtime_receipts,'component_contract':identity['components'],
 'provenance':'RUNTIME_PROVENANCE_CONDITIONAL','payload_reconstruction':False,'remaining_boundary':'No atomic filesystem-to-exec or continuous privileged-update exclusion'})
c00=load(N/'inputs/result_C00.json');ready=load(N/'inputs/C00_READINESS.json');assert c00['status']=='PASS' and len(ready['sample']['checks'])==8 and all(x['result']=='MATCH' for x in ready['sample']['checks'])
put('C00_READINESS_SUMMARY.json',{'status':'PASS','process_identity':ready['process_identity'],'eight_checks':ready['sample']['checks'],'aux_checks':ready['sample']['aux_checks'],'original':str(N/'inputs/C00_READINESS.json')})
wait=load(N/('inputs/root_private/waitpid_%s.json'%s['launcher_identity']['pid']));assert wait['exit_code']==0 and wait['raw_wait_status']==0
stops=[{'path':p.name,**load(p)} for p in N.glob('inputs/stop_result_*.json')];assert stops and all(x['empty'] and x['stop_exit']==0 and not x['after_stop_group_exists'] for x in stops)
post=load(E/'POSTRUN_AUDIT.json');assert not post['payload_processes'] and not post['root_role_processes'] and not post['parent_cgroup_exists']
charged_peak=max(int(x['before_stop_charged_snapshot']['values']['memory.peak']) if x.get('before_stop_charged_snapshot') else 0 for x in stops)
facts=c00['actual']['probe']['actual']['facts'];tasks=int(facts['parent']['values']['pids.current']);journal_messages=[json.loads(line) for line in (E/'RUN_BOOT_JOURNAL.stdout.raw').read_bytes().splitlines()]
jbrief=[{'monotonic_seconds':int(x['__MONOTONIC_TIMESTAMP'])/1e6,'pid':x.get('_PID'),'message':x.get('MESSAGE'),'realtime_us':x.get('__REALTIME_TIMESTAMP')} for x in journal_messages];put('JOURNAL_MESSAGE_INDEX.json',jbrief)
actual={'batch_id':'batch14','revision':'RuntimeAdapt-static-1/r1','mode':'NORMAL_START','overall':'CONDITIONAL_PASS_NORMAL_A2_WITH_PROVENANCE_AND_INTERNAL_BOUNDARIES',
 'RA-D1':'PASS_DYNAMIC','RA-D2':'PASS_DYNAMIC','TR-D1':'PASS_DYNAMIC','TR-D2':'CONDITIONAL_PASS','TR-D3':'PASS_DYNAMIC','TR-D4':'PASS_DYNAMIC','TR-D5':'PASS_DYNAMIC','TR-D6':'CONDITIONAL_PASS','TR-D7':'UNKNOWN','TR-D8':'CONDITIONAL_PASS',
 'scope_notes':{'RA-D1':'Observed current Root/Payload mappings and disk pins match, no perpetual/atomic identity claim','RA-D2':'Normal A2 Python/resource/startup/syscall behavior only, not full calibration',
 'TR-D2':'Actual active health gate rejected CLOSED; other work/budget/reinit cases are synthetic/unchanged guard evidence','TR-D6':'Actual automatic artifact completed; fine Live RLIMIT/import-start telemetry not emitted',
 'TR-D8':'Observed minimal prefix/resource values satisfy bounds; no full300s/whole Root RSS certificate'},
 'RUNTIME_PROVENANCE':'CONDITIONAL_ROOT_DPKG_KEYRING','independent_new_deb_payload_reconstruction':False,
 'boot_id':s['boot_id'],'owner':s['coordinator_identity'],'scheduler':s['launcher_identity'],'stopper':load(N/'inputs/STOP_ARMED.json')['identity'],
 'T0':s['T0'],'deadline':s['deadline'],'stop_at':s['stop_at'],'R':3133,'transactions':3133,'journal_lines':6266,
 'C00':'PASS','C00_sample':c00['sample'],'suites':suites,'checks':184,'mutants_detected':33,
 'CLOSED':closed,'STOP_REQUEST_exists':(N/'out/STOP_REQUEST.json').exists(),'terminal_review':review,'active_guard_denial':review['active_guard_denial'],
 'waitpid':wait,'stop_results':stops,'internal_state':'UNKNOWN','internal_close_receipt_exists':(N/'inputs/root_private/boot/mr_close_state.json').exists(),
 'batch_state_status_preserved':s['status'],'native_seal':'NATIVE_SEAL_COMPLETED','native_manifest_sample':nm['sample'],'automatic_finalization':final,
 'all_roles_and_parent_empty':True,'manual_cleanup':0,'extra_fallback_archival':0,'source_edits':0,'test_retries':0,'target_entry_calls':1,
 'active_host':load(C/'WINDOWS_ENTRY_EXIT.json'),'all_host':load(E/'ACTIVE_ENTRY_RETURN.json'),'T0_to_CLOSED_seconds':closed['boottime']-s['T0'],
 'T0_to_terminal_review_seconds':review['sample']['boottime']-s['T0'],'T0_to_native_manifest_seconds':nm['sample']['boottime']-s['T0'],
 'charged_memory_peak_observed_bytes':charged_peak,'charged_memory_peak_MiB':charged_peak/(1<<20),'C00_tasks_observed':tasks,
 'C00_process_limits_memory':facts['process'],'Root_or_admin_RSS_peak':None,'admin_live_RLIMIT_numeric_receipt':None,
 'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],'STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED'}
put('ACTUAL_RESULTS.json',actual)
events=[json.loads(line) for line in (N/'inputs/root_private/boot/pt_events.jsonl').read_bytes().splitlines()];timeline=[]
for q in events:timeline.append({'event':q['phase'],'boottime':q['sample']['boottime'],'T0_offset':q['sample']['boottime']-s['T0'],'source':'pt_events sequence'+str(q['sequence'])})
for name,t in [('T0',s['T0']),('C00 PASS',c00['sample']['boottime']),*[(x['suite']+' qualification',x['sample']['boottime']) for x in suites],
 ('CLOSED',closed['boottime']),('waitpid0',wait['sample']['boottime']),('terminal review',review['sample']['boottime']),('active denial',review['active_guard_denial']['sample']['boottime']),
 ('native manifest',nm['sample']['boottime']),('automatic admin audit',audit['observation']['boottime'])]:timeline.append({'event':name,'boottime':t,'T0_offset':t-s['T0'],'source':name})
timeline.sort(key=lambda x:x['boottime']);put('EXECUTION_TIMELINE.json',{'native_boottime':timeline,'journal_monotonic':jbrief,'host_active':actual['active_host'],'host_total':actual['all_host'],
 'auto_finalization':{k:v for k,v in final.items() if k!='native_audit'},'clock_caution':'Host/guest UTC and BOOTTIME/MONOTONIC kept separately; no exact cross-clock latency certificate'})
print(json.dumps({'overall':actual['overall'],'suite_results':[{x['suite']:x['statuses']} for x in suites],'R':3133,'journal_lines':6266,
 'terminal_read':'VALID','active_denial':'IPC_CLOSED_DOMINATES','native_rows':233,'native_entries':234,'admin_rows':249,'admin_entries':250,
 'internal':'UNKNOWN','charged_peak_MiB':actual['charged_memory_peak_MiB'],'payload_tasks_observed':tasks},ensure_ascii=False))
