"""Independent RA reference, no production imports or prefilled verdict use."""
import hashlib,json,os,stat
from pathlib import Path
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def reference(f):
    if f['silent_relock']:return 'DENY_SILENT_RELOCK'
    if any(not f[k] for k in ['digests','paths','build_ids','packages','symbols','preload_absent','read_ok','fresh','batch_binding']):return 'DENY_RUNTIME_IDENTITY'
    if f['purpose']=='WORK' and f['closed']:return 'DENY_CLOSED_WORK'
    return 'IDENTITY_MATCH'
def check_job(root,job,index,binding):
    try:
        fd=os.open(Path(root)/('ra_case_%03d.json'%index),os.O_RDONLY|os.O_NOFOLLOW)
        try:
            s=os.fstat(fd)
            if not stat.S_ISREG(s.st_mode) or s.st_size>131072:raise ValueError('RA_RAW_BOUND')
            raw=os.read(fd,s.st_size+1)
            if len(raw)!=s.st_size:raise ValueError('RA_RAW_SHORT')
        finally:os.close(fd)
        q=json.loads(raw)
        if q['origin']!='RA-SIMULATION/1' or q['binding']!=binding or q['case_id']!=job['case_id'] or q['input_sha256']!=hashlib.sha256(canonical(job)).hexdigest() or len(q['trace'])!=len(job['frames']):raise ValueError('RA_RAW_BINDING')
        violations=set()
        for f,a in zip(job['frames'],q['trace']):
            if a['actual_input']!=f or a['origin']!='RA-SIMULATION/1':raise ValueError('RA_INPUT_SOURCE')
            expected=reference(f)
            if a['decision']!=expected:
                reason='SILENT_RELOCK' if f['silent_relock'] else 'IDENTITY_BYPASS' if expected=='DENY_RUNTIME_IDENTITY' else 'CLOSED_REACTIVATION' if expected=='DENY_CLOSED_WORK' else 'FALSE_REJECTION'
                violations.add(reason)
            if a['system_files_modified'] or a['runtime_lock_modified']:violations.add('FORBIDDEN_WRITE')
        if job['mutant']:
            ok=job['expected_violation'] in violations and violations<=set(job['allowed_violations']);status='MUTATION_DETECTED' if ok else 'MUTATION_NOT_DETECTED' if not violations-set(job['allowed_violations']) else 'UNEXPECTED_VIOLATION'
        else:ok=not violations;status='PASS' if ok else 'FAIL'
        return {'case_id':job['case_id'],'accepted':ok,'status':status,'violations':sorted(violations),'raw_sha256':hashlib.sha256(raw).hexdigest()}
    except (OSError,ValueError,KeyError,TypeError) as exc:return {'case_id':job['case_id'],'accepted':False,'status':'EVIDENCE_MISSING','error':repr(exc)}
def check_suite(root,cfg,binding):
    rows=[check_job(root,j,i,binding) for i,j in enumerate(cfg['jobs'])]
    return {'origin':'RA-SIMULATION/1','binding':binding,'accepted':all(r['accepted'] for r in rows),'results':rows}
