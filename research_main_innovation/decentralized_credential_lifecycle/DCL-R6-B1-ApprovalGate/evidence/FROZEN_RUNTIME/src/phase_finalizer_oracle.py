"""Independent PF reference: only stdlib, no subject/guard/lifecycle/budget imports."""
import hashlib
import json
import os
from pathlib import Path
import stat

def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()

def reference(frame):
    f=frame['facts'];domain=frame['domain']
    if domain=='phase':
        numbers={'RUNTIME_READY':4,'RUNTIME_ARMED':5,'RUNNING':6}
        if f['closed'] or f['stop']:decision='DENY_TERMINAL'
        elif not (f['binding'] and f['identity'] and f['deadline']):decision='DENY_IDENTITY'
        elif not f['lock_acquired']:decision='WAIT_BOUNDED'
        elif numbers.get(f['phase'])!=f['sequence'] or f['phase'] not in numbers:decision='DENY_PHASE'
        elif not(f['committed'] and f['checkpoint_integrity'] and f['initialization_match']):decision='DENY_CHECKPOINT'
        elif f['root_reader'] and (f['private_phase']!=f['phase'] or f['private_sequence']!=f['sequence'] or not f['record_hash_match']):decision='DENY_VERSION'
        elif f['work'] and f['phase']=='RUNTIME_READY':decision='DENY_WORK'
        else:decision='ACCEPT'
        return {'decision':decision,'work_granted':decision=='ACCEPT' and f['work'],'automatic_stop':frame['critical'] and decision.startswith('DENY_')}
    if domain=='admin':
        cleanup='CLEANUP_CONFIRMED' if (f['roles_empty'],f['group_absent'],f['audit_error'])==(True,True,False) else 'CLEANUP_UNKNOWN'
        if not f['any_runtime']:native='NATIVE_SEAL_NOT_APPLICABLE'
        elif f['native_verified']:native='NATIVE_SEAL_COMPLETED'
        elif f['native_error']:native='NATIVE_SEAL_FAILED'
        else:native='NATIVE_SEAL_UNRESOLVED'
        failed=not all(f.get(k,True) for k in ('module_ready','permission_ok','evidence_integrity')) or f.get('exception',False)
        if f.get('repeated',False):admin='RETURN_EXISTING_ADMIN_SEAL' if f.get('repeat_valid',False) else 'ADMIN_EVIDENCE_UNRESOLVED'
        elif failed:admin='ADMIN_EVIDENCE_UNRESOLVED'
        elif cleanup=='CLEANUP_CONFIRMED':admin='EXPORT_ALLOWED'
        else:admin='DEFERRED_ACTIVE_WRITERS'
        return {'process_cleanup_status':cleanup,'native_seal_status':native,'administrative_export_status':admin,
            'internal_cleanup_status':f['internal_status'],'error_recorded':failed or (f.get('repeated',False) and not f.get('repeat_valid',False))}
    return {'automatic_stop':f['critical'],'cleanup':'CLEANUP_CONFIRMED' if f['roles_empty'] and f['group_absent'] and not f['audit_error'] else 'CLEANUP_UNKNOWN',
        'internal':f['internal_status'],'native':f['native_status'],'admin':f['admin_status']}

def check_job(root,job,index,binding):
    try:
        fd=os.open(Path(root)/('pf_case_%03d.json'%index),os.O_RDONLY|os.O_NOFOLLOW)
        try:
            meta=os.fstat(fd)
            if not stat.S_ISREG(meta.st_mode) or meta.st_size>131072:raise ValueError('PF_RAW_BOUND')
            raw=os.read(fd,meta.st_size+1)
            if len(raw)!=meta.st_size:raise ValueError('PF_RAW_SHORT')
        finally:os.close(fd)
        d=json.loads(raw)
        if d['origin']!='PF-SIMULATION/1' or d['binding']!=binding or d['case_id']!=job['case_id'] or d['input_sha256']!=hashlib.sha256(canonical(job)).hexdigest():raise ValueError('PF_RAW_BINDING')
        if len(d['trace'])!=len(job['frames']):raise ValueError('PF_TRACE_COUNT')
        violations=set()
        for source,actual in zip(job['frames'],d['trace']):
            if actual['actual_input']!=source or actual['origin']!='PF-SIMULATION/1':raise ValueError('PF_RAW_INPUT')
            expected=reference(source);observed=actual['observed'];facts=source['facts']
            if set(observed)!=set(expected):violations.add('UNEXPECTED_FIELDS')
            if source['domain']=='phase':
                if observed.get('decision')!=expected['decision'] or observed.get('work_granted')!=expected['work_granted']:
                    if expected['decision']=='DENY_TERMINAL':violations.add('REACTIVATION')
                    elif expected['decision']=='DENY_WORK':violations.add('PREMATURE_WORK')
                    elif expected['decision']=='DENY_PHASE':violations.add('ILLEGAL_PHASE_ACCEPTED')
                    elif expected['decision']=='DENY_VERSION':
                        violations.add('STALE_SNAPSHOT_ACCEPTED' if facts['phase']!=facts['private_phase'] else 'VERSION_MISMATCH_ACCEPTED')
                    else:violations.add('UNEXPECTED_DECISION')
                if observed.get('automatic_stop')!=expected['automatic_stop']:
                    # Re-activation suppresses the same required stop; keep its causal class.
                    violations.add('REACTIVATION' if expected['decision']=='DENY_TERMINAL' else 'NO_AUTO_STOP' if expected['automatic_stop'] else 'UNEXPECTED_STOP')
            elif source['domain']=='admin':
                for key in expected:
                    if observed.get(key)==expected[key]:continue
                    if key=='native_seal_status':violations.add('NATIVE_RESULT_OVERWRITTEN')
                    elif key in ('error_recorded','administrative_export_status') and not facts.get('module_ready',True):violations.add('IMPORT_ERROR_SWALLOWED')
                    else:violations.add('ADMIN_AXIS_MISMATCH')
            elif observed!=expected:violations.add('CLOSURE_AXIS_MISMATCH')
        if job['mutant']:
            accepted=job['violation_class'] in violations and violations<=set(job['allowed_violations'])
            status='MUTATION_DETECTED' if accepted else ('UNEXPECTED_VIOLATION' if violations-set(job['allowed_violations']) else 'MUTATION_NOT_DETECTED')
        else:accepted=not violations;status='PASS' if accepted else 'FAIL'
        return {'case_id':job['case_id'],'accepted':accepted,'status':status,'violations':sorted(violations),'raw_sha256':hashlib.sha256(raw).hexdigest()}
    except (OSError,ValueError,KeyError,TypeError) as exc:
        return {'case_id':job['case_id'],'accepted':False,'status':'EVIDENCE_MISSING','error':repr(exc)}

def check_suite(root,cfg,binding):
    rows=[check_job(root,j,i,binding) for i,j in enumerate(cfg['jobs'])]
    return {'accepted':all(r['accepted'] for r in rows),'binding':binding,'origin':'PF-SIMULATION/1','results':rows}
