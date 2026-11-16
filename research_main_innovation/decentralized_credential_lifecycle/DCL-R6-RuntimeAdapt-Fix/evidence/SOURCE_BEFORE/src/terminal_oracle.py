"""Independent TR reference; stdlib only; no production subject or budget imports."""
import hashlib
import json
import os
from pathlib import Path
import stat

def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()

def reference(frame):
    f=frame['facts'];out={'read_status':'REJECTED','work_allowed':False,'budget_init_allowed':False,'phase_write_allowed':False,
        'launcher_allowed':False,'native_ready':False,'internal_status':f['internal_status'],'native_status':'NATIVE_SEAL_UNRESOLVED',
        'budget_delta':0,'phase_delta':0,'originals_modified':False,'used_default_deadline':False}
    if f['purpose']=='ACTIVE':
        out['work_allowed']=(f['closed'],f['stop'])==(False,False) and all(f[k] for k in ['identity','window','budget','version','same_boot','window_live'])
    elif f['identity'] and (f['closed'] or f['stop']):
        if f['window'] and f['budget'] and f['version'] and f['required_records']:
            out['read_status']='VALID'
            if f['native_verified']:out['native_status']='NATIVE_SEAL_COMPLETED'
            elif f['seal_error']:out['native_status']='NATIVE_SEAL_FAILED'
            out['native_ready']=(f['purpose']=='NATIVE_SEAL' and f['closed'] and f['same_boot'] and f['window_live'] and
                f['exit_proof'] and not f['seal_error'] and not f['partial_archive'])
        else:out['read_status']='UNKNOWN'
    return out

def check_job(root,job,index,binding):
    try:
        fd=os.open(Path(root)/('tr_case_%03d.json'%index),os.O_RDONLY|os.O_NOFOLLOW)
        try:
            s=os.fstat(fd)
            if not stat.S_ISREG(s.st_mode) or s.st_size>131072:raise ValueError('TR_RAW_BOUND')
            raw=os.read(fd,s.st_size+1)
            if len(raw)!=s.st_size:raise ValueError('TR_RAW_SHORT')
        finally:os.close(fd)
        d=json.loads(raw)
        if d['origin']!='TR-SIMULATION/1' or d['binding']!=binding or d['case_id']!=job['case_id'] or d['input_sha256']!=hashlib.sha256(canonical(job)).hexdigest():raise ValueError('TR_RAW_BINDING')
        if len(d['trace'])!=len(job['frames']):raise ValueError('TR_FRAME_COUNT')
        violations=set()
        for frame,a in zip(job['frames'],d['trace']):
            if a['actual_input']!=frame or a['origin']!='TR-SIMULATION/1':raise ValueError('TR_RAW_INPUT')
            expected=reference(frame);actual=a['observed'];facts=frame['facts']
            if set(expected)!=set(actual):violations.add('UNEXPECTED_FIELDS')
            for key in expected:
                if actual.get(key)==expected[key]:continue
                if key=='work_allowed':violations.add('TERMINAL_WORK_GRANTED')
                elif key in ('budget_init_allowed','budget_delta'):violations.add('BUDGET_REBUILT')
                elif key in ('phase_write_allowed','phase_delta','launcher_allowed'):violations.add('REACTIVATION')
                elif key=='originals_modified':violations.add('ORIGINAL_EVIDENCE_MODIFIED')
                elif key=='used_default_deadline':violations.add('DEFAULT_DEADLINE_USED')
                elif key=='internal_status':violations.add('UNKNOWN_UPGRADED')
                elif key in ('native_ready','native_status'):violations.add('FALSE_SEAL_SUCCESS')
                elif not facts['identity']:violations.add('IDENTITY_CHECK_SKIPPED')
                elif not facts['window']:violations.add('DEFAULT_DEADLINE_USED')
                elif not facts['budget']:violations.add('JOURNAL_CORRUPTION_IGNORED')
                else:violations.add('UNEXPECTED_DECISION')
        if job['mutant']:
            accepted=job['expected_violation'] in violations and violations<=set(job['allowed_violations'])
            status='MUTATION_DETECTED' if accepted else ('UNEXPECTED_VIOLATION' if violations-set(job['allowed_violations']) else 'MUTATION_NOT_DETECTED')
        else:accepted=not violations;status='PASS' if accepted else 'FAIL'
        return {'case_id':job['case_id'],'accepted':accepted,'status':status,'violations':sorted(violations),'raw_sha256':hashlib.sha256(raw).hexdigest()}
    except (OSError,ValueError,KeyError,TypeError) as exc:return {'case_id':job['case_id'],'accepted':False,'status':'EVIDENCE_MISSING','error':repr(exc)}

def check_suite(root,cfg,binding):
    rows=[check_job(root,j,i,binding) for i,j in enumerate(cfg['jobs'])]
    return {'origin':'TR-SIMULATION/1','binding':binding,'accepted':all(r['accepted'] for r in rows),'results':rows}
