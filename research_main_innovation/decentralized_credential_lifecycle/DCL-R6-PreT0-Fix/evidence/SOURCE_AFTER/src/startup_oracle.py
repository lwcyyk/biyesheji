"""Independent raw PT oracle. No imports of lifecycle, subject, guard or budget core."""
import hashlib
import json
import os
from pathlib import Path
import stat

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def read(p):
    fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
    try:
        s=os.fstat(fd)
        if not stat.S_ISREG(s.st_mode) or s.st_size>131072:raise ValueError('PT_RAW_BOUND')
        raw=os.read(fd,s.st_size+1)
        if len(raw)!=s.st_size:raise ValueError('PT_RAW_SHORT')
        return raw
    finally:os.close(fd)

def check_job(root,job,index,binding):
    try:
        raw=read(Path(root)/('pt_case_%03d.json'%index));d=json.loads(raw)
        if d['origin']!='PT-SIMULATION/1' or d['binding']!=binding or d['input_sha256']!=hashlib.sha256(canonical(job)).hexdigest():raise ValueError('PT_RAW_BINDING')
        if len(d['trace'])!=len(job['frames']):raise ValueError('PT_FRAME_COUNT')
        violations=set();terminal=False;begun=False;lastT0=None;had_state=False
        ref_context=False;ref_qualified=False;ref_state=False;ref_counter=False;ref_cp=False;ref_armed=False
        for frame,a in zip(job['frames'],d['trace']):
            if a['actual_input']!=frame:raise ValueError('PT_INPUT_SOURCE')
            valid=all(frame[k] for k in ['binding','boot','owner','deadline']);op=frame['op']
            if op=='enter' and valid and not terminal:ref_context=True
            if op=='qualify' and ref_context and valid and not terminal and not begun:ref_qualified=True
            if op=='precheck' and not begun and valid and a['pre_context'] and not terminal:
                if a['decision']!='PREWINDOW_ALLOWED_NO_WORK' or a['error'] is not None:violations.add('PREWINDOW_CYCLE')
            if a['decision']=='PREWINDOW_ALLOWED_NO_WORK' and not valid:violations.add('INVALID_PREWINDOW_ACCEPTED')
            if op=='begin' and ref_qualified and not terminal and valid:begun=True
            if op=='state' and begun and not terminal:ref_state=True
            if op=='counter' and ref_state and not terminal:ref_counter=True
            if op=='checkpoint' and ref_state and ref_counter and not terminal:ref_cp=True
            if op=='arm' and ref_cp and valid and not terminal:ref_armed=True
            if op=='lose_checkpoint':ref_cp=False
            if a['state'] and not begun:violations.add('SYNTHETIC_RUNTIME')
            if a['counter'] and not a['state']:violations.add('BUDGET_BEFORE_STATE')
            if a['grant']:
                if terminal:violations.add('REACTIVATION')
                if not(ref_state and ref_counter and ref_cp and ref_armed and begun and valid and frame['checkpoint_integrity']):violations.add('INVALID_RUNTIME_WORK')
            if op=='work' and ref_state and ref_counter and ref_cp and ref_armed and valid and frame['checkpoint_integrity'] and not terminal:
                if not a['grant']:violations.add('FALSE_REJECTION')
            if op in ('fail','repeat_fail'):
                if not a['stop'] or not a['closed']:violations.add('NO_AUTO_STOP')
                terminal=True
            if terminal and (a['initializations']>1 or (not had_state and a['state'])):violations.add('BUDGET_CREATED_AFTER_FAILURE')
            if terminal and not a['closed']:violations.add('REACTIVATION')
            if a['cleanup']=='CLEANUP_CONFIRMED' and (not a['closed'] or not frame['exited']):violations.add('FALSE_CLEANUP')
            if op=='seal':
                if a['admin_sealed'] and (not frame['admin_integrity'] or not frame['exited']):violations.add('FALSE_ADMIN_SEAL')
                if a['native_status']=='NATIVE_SEAL_COMPLETED' and not(a['state'] and a['counter'] and a['checkpoint'] and frame['native_success'] and frame['exited']):violations.add('ADMIN_AS_NATIVE')
                if not begun and a['native_status']!='NATIVE_SEAL_NOT_APPLICABLE':violations.add('PREWINDOW_NATIVE_SEAL')
            if lastT0 is not None and a['T0']!=lastT0:violations.add('WINDOW_RESET')
            if a['T0'] is not None:lastT0=a['T0']
            had_state=a['state']
        if job['mutant']:
            accepted=job['expected_violation'] in violations and violations<=set(job['allowed_violations'])
            status='MUTATION_DETECTED' if accepted else ('UNEXPECTED_VIOLATION' if violations-set(job['allowed_violations']) else 'MUTATION_NOT_DETECTED')
        else:accepted=not violations;status='PASS' if accepted else 'FAIL'
        return {'case_id':job['case_id'],'accepted':accepted,'status':status,'violations':sorted(violations),'raw_sha256':hashlib.sha256(raw).hexdigest()}
    except (OSError,ValueError,KeyError,TypeError) as exc:
        return {'case_id':job['case_id'],'accepted':False,'status':'EVIDENCE_MISSING','error':repr(exc)}

def check_suite(root,cfg,binding):
    rows=[check_job(root,j,i,binding) for i,j in enumerate(cfg['jobs'])]
    return {'accepted':all(r['accepted'] for r in rows),'binding':binding,'results':rows,'origin':'PT-SIMULATION/1'}
