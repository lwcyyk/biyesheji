"""Offline reference checks on captured values. No target modules or cases are replayed."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import struct
import zipfile

E=Path(__file__).resolve().parent
N=Path(r'D:\毕业设计\DCL-R6-isolated-verification\batch08\native_snapshot')
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(name,x):(E/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

events=[json.loads(s) for s in (E/'windows_entry.stdout.raw').read_text(encoding='utf-8').splitlines() if s.strip()]
owners={tuple(r['identity'][k] for k in ['boot_id','pid','start_ticks']) for r in events if r['event']!='ACTUAL_SERVICE_CONFIRMED'}
assert len(owners)==1
state=load(N/'inputs/batch_state.json');closed=load(N/'inputs/CLOSED.json');boot=state['boot_id'];t0=state['T0']
assert state['execution_mode']=='C00_DIAGNOSTIC_ONLY' and closed['reason']=='C00_DIAGNOSTIC_COMPLETE'
assert load(E/'WINDOWS_ENTRY_EXIT.json')['exit_code']==0
expected=[[999],[989],[989],0,1,'1073741824','1073741824','/dclr6batch08.slice/dclr6batch08-c00.service']
fieldnames=['Uid','Gid','Groups','CapEff','NoNewPrivs','LimitAS','LimitASSoft','ControlGroup']
samples=[(p,load(p)) for p in sorted((N/'inputs/root_private/boot').glob('ready_C00_*.json'))]
assert len(samples)==3 and [x['overall_result'] for _,x in samples]==['STARTING','READY','READY']
reference=[]
def parse_status(text):
    f=dict(s.split(':',1) for s in text.splitlines() if ':'in s)
    assert len(f['Uid'].split())==len(f['Gid'].split())==4
    return [sorted(set(map(int,f['Uid'].split()))),sorted(set(map(int,f['Gid'].split()))),
            sorted(set(map(int,f['Groups'].split()))),int(f['CapEff'],16),int(f['NoNewPrivs'])]
for path,sample in samples:
    assert sample['origin']=='NATIVE_OS/1' and sample['boot_before']==sample['boot_after']==sample['expected_boot']==boot
    assert len(sample['checks'])==8 and sample['error'] is None
    u0=sample['raw']['unit_before'];u1=sample['raw']['unit_after']
    for u in [u0,u1]:
        decoded=dict(s.split('=',1) for s in bytes.fromhex(u['stdout_hex']).decode().splitlines() if '='in s)
        assert decoded==u['values'] and u['exit_code']==0
    for index,row in enumerate(sample['checks']):
        assert row['check_id']=='CR-%02d'%(index+1) and row['expected']==expected[index]
        if sample['overall_result']=='STARTING' and index<5:
            assert row['observed'] is None and row['result']=='NOT_READY' and not row['read_success']
        else:assert row['observed']==[expected[index],expected[index]] and row['result']=='MATCH'
    if sample['overall_result']=='READY':
        actual=[]
        for side in ['proc_before','proc_after']:
            p=sample['raw'][side];values=parse_status(p['status']['raw']);actual.append(values)
            assert values==expected[:5]
            line=next(s for s in p['limits']['raw'].splitlines() if s.startswith('Max address space'))
            pair=list(map(int,line[len('Max address space'):].split()[:2]));assert pair==[1073741824,1073741824]
            assert next(s[3:] for s in p['cgroup']['raw'].splitlines() if s.startswith('0::'))==expected[7]
            for source in ['status','limits','cgroup']:
                assert sample['check_time_begin']['boottime']<=p[source]['before']['boottime']<=p[source]['after']['boottime']<=sample['check_time_end']['boottime']
        assert actual[0]==actual[1]
        assert all(r['result']=='MATCH' for r in sample['aux_checks'])
        for source in ['parent_before','parent_after']:
            assert sample['raw'][source]['pids_max']==4 and sample['raw'][source]['memory_max']==4294967296
    reference.append({'path':path.relative_to(N).as_posix(),'sha256':sha(path),'phase':sample['phases'],
                      'overall':sample['overall_result'],'raw_values_recomputed':True})
cert=load(N/'inputs/C00_READINESS.json');start=load(N/'inputs/BOOT_START.json');ticket=load(N/'inputs/ticket_C00.json');c00=load(N/'inputs/result_C00.json')
assert c00['status']=='PASS' and ticket['readiness_sha256']==sha(N/'inputs/C00_READINESS.json')
assert cert['boot_id']==start['boot_id']==boot and cert['process_identity']==ticket['main_identity']==start['main_identity']
assert cert['sample']==samples[-1][1] and cert['execution_lock_sha256']==sha(E/'execution_lock.json')
parent=state['coordinator_identity'];entry=load(N/'inputs/root_private/boot/entry_initial.json');cap=load(N/'inputs/root_private/boot/capability.json')
assert entry['owner']==parent==events[0]['identity']
assert entry['ticket_sha256']==cap['sha256'] and cap['seals']==15
service_event=next(r for r in events if r['event']=='ACTUAL_SERVICE_CONFIRMED')
assert service_event['main_identity']==cert['process_identity']
until=cert['readiness_until'];activation_started=until-14
assert until<min(state['T0']+300,state['stop_at'],state['deadline'])
ready1=samples[1][1];confirm=samples[2][1]
dump('C00_FIELD_ACTUAL.json',{'schema':'D08-fields/1','native_case_status':'PASS','overall':'C00_PASS',
 'process_identity':cert['process_identity'],'boot_id':boot,'samples':reference,
 'fields':[{'check_id':'CR-%02d'%(i+1),'field_name':name,'expected':expected[i],
  'initial_observed':samples[0][1]['checks'][i]['observed'],'initial_result':samples[0][1]['checks'][i]['result'],
  'first_ready_observed':ready1['checks'][i]['observed'],'final_observed':confirm['checks'][i]['observed'],
  'final_result':'MATCH','source':confirm['checks'][i]['evidence_source'],'read_time':confirm['checks'][i]['read_time'],
  'evidence_sha256':sha(samples[2][0])} for i,name in enumerate(fieldnames)],
 'stable_mismatches':[],'read_errors':[],'identity_changed':False,'first_failed_check':None,
 'field_evidence':'FIELD_EVIDENCE_COMPLETE','fine_pidfd_timing':'PARTIAL: successful checks inferred from frozen native control flow and READY; separate fd-check timestamps/results not emitted',
 'old_batch07_failed_field':'C00_FAILED_FIELD_UNRESOLVED'})
dump('READINESS_TIMELINE.json',{'schema':'D08-readiness-time/1','clock':'CLOCK_BOOTTIME','activation_started':activation_started,
 'start_time_derivation':'readiness_until-14; other window deadlines are strictly later',
 'readiness_until':until,'samples':[{'file':p.name,'begin':x['check_time_begin']['boottime'],'end':x['check_time_end']['boottime'],
 'phase':x['phases'],'result':x['overall_result'],'identity':x['process_identity']} for p,x in samples],
 'first_READY_decision_time':ready1['check_time_end']['boottime'],
 'native_wait_return_lower_seconds':ready1['check_time_end']['boottime']-activation_started,
 'native_wait_return_upper_seconds':confirm['check_time_begin']['boottime']-activation_started,
 'second_validation_end_seconds':confirm['check_time_end']['boottime']-activation_started,
 'service_confirmed_event_seconds':service_event['sample']['boottime']-activation_started,
 'exact_wait_function_return_timestamp':'UNRECORDED; interval provided instead',
 'pidfd_check_exact_timestamps':'UNRECORDED; bounded by each native sample interval',
 'C00_result_time':c00['sample']['boottime'],'C00_result_T0':c00['sample']['boottime']-t0})

q=load(N/'inputs/C00_READY_QUALIFICATION.json');cfg=load(E/'readiness_contract.json')
assert q['accepted'] and len(q['results'])==64
raw_base=N/'inputs/root_private/boot';refrows=[]
for i,(job,outcome) in enumerate(zip(cfg['jobs'],q['results'])):
    p=raw_base/('ready_case_%03d.json'%i);raw=load(p)
    assert raw['case_id']==job['case_id']==outcome['case_id'] and raw['binding']==q['binding']
    assert raw['input_sha256']==hashlib.sha256(json.dumps(job,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert sha(p)==outcome['raw_sha256'] and raw['global_after']-raw['global_before']==6
    assert [x['event'] for x in raw['trace']]==job['frames']
    flags=set();fatal=False
    for step in raw['trace']:
        f=step['facts'];decision=step['response']['decision'];checks=f['checks']
        mismatched=[r['check_id'] for r in checks if r['observed'] is not None and any(v!=r['expected'] for v in r['observed'])]
        read_bad=f['error'] is not None or any(r['result']=='READ_ERROR' for r in checks)
        pid_bad=f['identity_before']!=f['identity_after']
        boot_bad=f['boot_before']!=f['expected_boot'] or f['boot_after']!=f['expected_boot']
        terminal=bool(mismatched or read_bad or pid_bad or boot_bad or not f['binding_valid'] or not f['hard_aux_valid'] or f['expired'] or f['stopped'] or (f['phases']==['READY','READY'] and not f['coherent']) or 'FAILED'in f['phases'])
        if decision=='READY':
            flags.update(mismatched)
            if read_bad:flags.add('CR-READ_ERROR')
            if pid_bad:flags.add('CR-PID')
            if boot_bad:flags.add('CR-BOOT')
            if not f['binding_valid']:flags.add('CR-LOCK')
            if not f['coherent']:flags.add('CR-SNAPSHOT')
            if fatal:flags.add('CR-REACTIVATION')
            if terminal:flags.add('UNSAFE_READY')
        if decision=='STARTING' and terminal:
            flags.add('CR-STALE')
            if mismatched:flags.add('CR-WAIT-MISMATCH')
            if f['expired']:flags.add('CR-TIMEOUT')
        fatal=fatal or terminal
    if job['variant']=='safe':
        assert not flags and raw['trace'][-1]['response']['decision']==job['expected'] and outcome['status']=='PASS'
    else:assert job['expected_violation'] in flags and outcome['status']=='MUTATION_DETECTED'
    assert outcome['accepted'] and set(outcome['violations']).issubset(job['allowed_violations'])
    refrows.append({'case_id':job['case_id'],'native_status':outcome['status'],'raw_sha256':sha(p),'offline_reference':'ACCEPTED',
                    'independent_observed_violations':sorted(flags),'root_oracle_violations':outcome['violations']})
dump('REGRESSION_REFERENCE_CHECK.json',{'schema':'D08-admin-reference/1','method':'Independent read-only property checks over captured traces; no candidate import/replay',
 'counts':dict(Counter(r['native_status'] for r in refrows)),'jobs':refrows,'errors':[],
 'not_new_native_resource_qualification':True})

counter=(N/'out/visits.bin').read_bytes();assert len(counter)==24 and counter[:8]==b'BRNGv001'
used,capvalue=struct.unpack('<QQ',counter[8:]);intent=load(N/'out/visits.bin.intent.json')
j=[json.loads(s) for s in (N/'out/visits.bin.journal.jsonl').read_text().splitlines()]
assert used==450 and capvalue==1000000 and len(j)==900
cursor=0
for prepared,committed in zip(j[::2],j[1::2]):
    assert prepared['status']=='PREPARED' and committed['status']=='COMMITTED'
    assert prepared['before']==committed['before']==cursor and prepared['after']==committed['after']==cursor+1
    assert prepared['amount']==committed['amount']==1;cursor+=1
assert cursor==used==intent['after'] and intent['status']=='COMMITTED'
assert q['global_before']==1 and q['global_after']==450
cleanup=[load(p) for p in sorted((N/'inputs').glob('stop_result_*.json'))]
assert all(x['empty'] and x['stop_exit']==0 and x['closure_persistence_error'] is None for x in cleanup)
first=min(cleanup,key=lambda x:x['sample']['boottime']);peak=int(first['before_stop_charged_snapshot']['values']['memory.peak'])
wait=load(next((N/'inputs/root_private').glob('waitpid_*.json')))
assert wait['exit_code']==0 and wait['raw_wait_status']==0
dump('RESOURCE_ACCOUNTING.json',{'schema':'D08-accounting/1','R':used,'cap':capvalue,'transactions':450,'PREPARED':450,'COMMITTED':450,'journal_records':900,
 'intent_status':'COMMITTED','errors':[],'C00_native_visits':1,'regression_root_visits':449,
 'refunds':0,'resets':0,'resume':0,'T0':t0,'deadline':state['deadline'],'stop_at':state['stop_at'],
 'close_time':closed['boottime'],'close_elapsed':closed['boottime']-t0,'closed_to_empty':first['sample']['boottime']-closed['boottime'],
 'first_empty_time':first['sample']['boottime'],'first_empty_elapsed':first['sample']['boottime']-t0,
 'waitpid_time':wait['sample']['boottime'],'waitpid_exit':0,'raw_wait_status':0,
 'observed_charged_peak_bytes':peak,'RSS_tree_peak':None,'Root_RSS_peak':None,
 'host_active_seconds':load(E/'WINDOWS_ENTRY_EXIT.json')['host_elapsed_ns']/1e9,'scope':'Minimal C00 and approved64 only'})
m=load(N/'out/EVIDENCE_MANIFEST.json')
with zipfile.ZipFile(N/'out/EVIDENCE.zip') as z:
    for rel,row in m['files'].items():
        b=z.read(rel);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'] and sha(N/rel)==row['sha256']
    assert z.read('out/EVIDENCE_MANIFEST.json')==(N/'out/EVIDENCE_MANIFEST.json').read_bytes()
    dump('NATIVE_ZIP_CHECK.json',{'schema':'D08-native-zip/1','status':'PASS_ADMIN_ONLY','manifest_rows':len(m['files']),
         'entries':len(z.namelist()),'sha256':sha(N/'out/EVIDENCE.zip'),'bytes':(N/'out/EVIDENCE.zip').stat().st_size,'mismatches':[]})
audit=load(E/'POSTRUN_AUDIT.json');assert audit['journal_exit']==0
journal=[json.loads(s) for s in (E/'RUN_BOOT_JOURNAL.stdout.raw').read_text().splitlines() if s.strip()]
assert all(r['_BOOT_ID']==boot.replace('-','') for r in journal)
dump('JOURNAL_SUMMARY.json',{'schema':'D08-journal/1','run_boot':boot,'records':[
 {'unit':r.get('UNIT',r.get('_SYSTEMD_UNIT')),'mono_us':r['__MONOTONIC_TIMESTAMP'],'realtime_us':r['__REALTIME_TIMESTAMP'],'message':r['MESSAGE']} for r in journal],
 'clock':'journal MONOTONIC/REALTIME; never mixed with BOOTTIME elapsed'})
dump('ACTUAL_RESULTS.json',{'schema':'D08-results/1','D08-1':'PREFLIGHT_PASS','D08-2':'SAME_BOOT_CONFIRMED','D08-3':'C00_PASS',
 'D08-4':'FIELD_EVIDENCE_PARTIAL','D08-4_detail':'Eight fields/double source records complete; separate pidfd check/return timestamps absent',
 'eight_field_values_complete':True,'pidfd_success':'Control-flow witnessed, no distinct fd-check event',
 'regression_planned':64,'regression_completed':64,'safe_PASS':47,'MUTATION_DETECTED':17,
 'C00_probe':'PASS','C00_first_sample':'STARTING','C00_stable_mismatches':[],
 'old_batch07_field':'C00_FAILED_FIELD_UNRESOLVED','closure':'C00_DIAGNOSTIC_COMPLETE',
 'R':450,'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
 'BC40':'UNRUN_UNAUTHORIZED','RootIPC56':'UNRUN_UNAUTHORIZED','C09H34':'UNRUN_UNAUTHORIZED','C09':'UNRUN_UNAUTHORIZED',
 'C01_C12':'UNRUN_UNAUTHORIZED','S34':'UNRUN_UNAUTHORIZED','negative17':'UNRUN_UNAUTHORIZED',
 'entry_calls':1,'retries':0,'source_changes':0,'full_chain':False,'new_batch09':False})
print(json.dumps({'C00':'PASS','samples':len(samples),'sample_results':[x['overall_result'] for _,x in samples],
 'regressions':dict(Counter(r['status'] for r in q['results'])),'R':used,'transactions':len(j)//2,
 'close_elapsed':closed['boottime']-t0,'peak':peak,'native_zip':load(E/'NATIVE_ZIP_CHECK.json'),
 'old_field':'UNRESOLVED','fine_timing':'PARTIAL'},ensure_ascii=False,indent=2))
