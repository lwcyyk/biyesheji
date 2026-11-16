"""Independent MR raw trace oracle; imports no subject, guard or production policy."""
import hashlib
import json
import os
from pathlib import Path
import stat
import select

def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def read(path):
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
    try:
        s=os.fstat(fd)
        if not stat.S_ISREG(s.st_mode) or s.st_size>131072:raise ValueError('MR_RAW_FILE_BOUND')
        raw=os.read(fd,s.st_size+1)
        if len(raw)!=s.st_size:raise ValueError('MR_RAW_SHORT_READ')
        return raw
    finally:os.close(fd)

def check_job(root,job,index,binding):
    try:
        raw=read(Path(root)/('mr_case_%03d.json'%index));row=json.loads(raw)
        if row['origin']!='MR-SIMULATION/1' or row['binding']!=binding or row['case_id']!=job['case_id'] or row['input_sha256']!=hashlib.sha256(canonical(job)).hexdigest():raise ValueError('MR_RAW_BINDING')
        if len(row['trace'])!=len(job['frames']):raise ValueError('MR_FRAME_COUNT')
        violations=set();terminal=False;stop=False;first=None;grants=0
        for frame,actual in zip(job['frames'],row['trace']):
            f=frame['facts'];truth=actual['actual_facts']
            if truth!=f:raise ValueError('MR_FACT_SOURCE')
            if actual['injection_point']!=frame['injection_point'] or actual['fault_source']!=frame['fault_source']:raise ValueError('MR_INJECTION_SOURCE')
            closed=f['closed'] or terminal;stopped=f['stop'] or stop
            sufficient=(not closed and not stopped and f['binding'] and f['identity'] and f['fresh'] and f['expected_kind'] and
                f['budget'] and f['window'] and f['exit_observed'] and f['review_complete'] and f['result_proof'] and
                f['ack'] and f['receiver'] and f['witness'] and f['supervision'])
            if actual['decision']=='REVIEWED_EXPECTED' and not sufficient:violations.add('UNREVIEWED_SUCCESS')
            if actual['grant']:
                if not sufficient:violations.add('UNREVIEWED_RESUME')
                if terminal or closed:violations.add('REACTIVATION')
                grants+=1
            if grants>1 or actual['resume_count']>1:violations.add('DUPLICATE_RESUME')
            critical=frame['critical'] or frame['action']=='close'
            if critical:
                if first is None:first=frame['event_id']
                if not actual['stop'] or not actual['closed']:violations.add('NO_AUTOMATIC_CLOSE')
                if actual['first_failure']!=first:violations.add('FIRST_FAILURE_LOST')
                if actual['closure']=='CLOSED_CLEANUP_CONFIRMED' and (not frame['payload_empty'] or not frame['other_roles_exited'] or frame['cleanup_errors']):violations.add('FALSE_EXIT_SUCCESS')
                terminal=True;stop=True
            if actual['T0']!=10 or actual['R']!=31:violations.add('BUDGET_OR_WINDOW_RESET')
            if terminal and not actual['closed']:violations.add('REACTIVATION')
        expected=set(job['allowed_violations'])
        if job['mutant']:
            accepted=bool(violations) and job['expected_violation'] in violations and violations<=expected
            status='MUTATION_DETECTED' if accepted else ('UNEXPECTED_VIOLATION' if violations-expected else 'MUTATION_NOT_DETECTED')
        else:
            accepted=not violations;status='PASS' if accepted else 'FAIL'
        return {'case_id':job['case_id'],'accepted':accepted,'status':status,'violations':sorted(violations),'raw_sha256':hashlib.sha256(raw).hexdigest()}
    except (OSError,ValueError,KeyError,TypeError) as exc:
        return {'case_id':job['case_id'],'accepted':False,'status':'EVIDENCE_MISSING','error':repr(exc)}

def check_suite(root,cfg,binding):
    results=[check_job(root,job,i,binding) for i,job in enumerate(cfg['jobs'])]
    return {'accepted':all(row['accepted'] for row in results),'binding':binding,'results':results,'origin':'MR-SIMULATION/1'}

def native_diagnostic(G,exit_code):
    """Read actual protected failure/exit evidence; no mutation expected-result shortcut."""
    p=G.ROOT/'inputs/root_private/boot/mr_diag_injection.json';marker=G.trusted(p)
    first=G.trusted(G.ROOT/'inputs/root_private/boot/mr_first_failure.json')
    closed=G.trusted(G.ROOT/'inputs/CLOSED.json');review=G.trusted(G.ROOT/'inputs/MR_RECOVERY_REVIEW.json')
    state=G.trusted(G.ROOT/'inputs/batch_state.json')
    binding={'batch_id':G.ROOT.name,'boot_id':state['boot_id'],'T0':state['T0'],
        'batch_identity_sha256':G.digest(G.SOURCE.parent/'inputs/batch_identity.json'),
        'static_manifest_sha256':G.digest(G.SOURCE.parent/'inputs/static_manifest.json'),
        'execution_lock_sha256':G.digest(G.SOURCE.parent/'inputs/execution_lock.json'),
        'fixture_contract_sha256':G.digest(G.SOURCE.parent/'inputs/safety_contract.json'),
        'child_contracts_sha256':G.digest(G.SOURCE.parent/'inputs/child_contracts.json')}
    if (marker['binding']!=binding or marker['expected_exit']!=78 or exit_code!=78 or
        not first['expected_diagnostic'] or first['reason']!='MR_EXPECTED_DIAGNOSTIC_FAILURE' or
        G.digest(G.ROOT/'inputs/result_C10.json')!=marker['C10_sha256'] or review['status']!='RESUMED' or
        closed['boot_id']!=G.boot_id() or not G._empty()):raise G.AdmissionBlocked('MR_NATIVE_DIAGNOSTIC_FAILED')
    close=G.trusted(G.ROOT/'inputs/root_private/boot/mr_close_state.json')
    if close['status']!='CLOSED_CLEANUP_CONFIRMED':raise G.AdmissionBlocked('MR_NATIVE_CLEANUP_UNKNOWN')
    first_path=G.ROOT/'inputs/root_private/boot/mr_first_failure.json'
    if close['first_failure_sha256']!=G.digest(first_path):raise G.AdmissionBlocked('MR_NATIVE_FIRST_FAILURE')
    if first['window']!={k:state[k] for k in ('T0','deadline','stop_at')}:raise G.AdmissionBlocked('MR_NATIVE_WINDOW_CHANGED')
    for name in ('visits.bin','visits.bin.intent.json','visits.bin.journal.jsonl'):
        if first['budget'][name].get('sha256')!=G.digest(G.OUT/name):raise G.AdmissionBlocked('MR_NATIVE_BUDGET_CHANGED')
    registry=G.trusted(G.ROOT/'inputs/root_private/boot/mr_scheduler.json')
    arm=G.trusted(G.ROOT/'inputs/STOP_ARMED.json')
    wait=G.trusted(G.ROOT/('inputs/root_private/waitpid_'+str(registry['child']['pid'])+'.json'))
    if (registry['owner']!=G.identity() or registry['phase']!='resume' or first['actor']!=registry['child'] or
        wait['child']!=registry['child'] or wait['coordinator']!=G.identity() or wait['exit_code']!=78 or
        os.waitstatus_to_exitcode(wait['raw_wait_status'])!=78):raise G.AdmissionBlocked('MR_NATIVE_WAITPID_PROOF')
    attempts=read(G.ROOT/'inputs/root_private/boot/mr_close_attempts.jsonl').splitlines()
    if any(json.loads(line)['errors'] for line in attempts):raise G.AdmissionBlocked('MR_NATIVE_UNEXPECTED_CLEANUP_ERROR')
    for ident in [registry['child'],arm['identity']]:
        try:
            fd=os.pidfd_open(ident['pid'])
            try:
                if G.identity(ident['pid'])==ident and not select.select([fd],[],[],0)[0]:raise G.AdmissionBlocked('MR_NATIVE_ROLE_STILL_LIVE')
            finally:os.close(fd)
        except ProcessLookupError:pass
    return {'schema':'MR-NATIVE-DIAGNOSTIC/1','status':'EXPECTED_FAILURE_CLOSED','binding':binding,
        'exit_code':exit_code,'failure_sha256':G.digest(G.ROOT/'inputs/root_private/boot/mr_first_failure.json'),
        'CLOSED_sha256':G.digest(G.ROOT/'inputs/CLOSED.json'),'close_result_sha256':G.digest(G.ROOT/'inputs/root_private/boot/mr_close_state.json'),
        'caller_exit_pending':True,'other_writer_exit_confirmed':True,'sample':G.stamp()}
