"""Independent readiness trace oracle. Imports no native collector, policy or subject."""
import hashlib
import json
import os
from pathlib import Path
import stat


def violations(trace):
    found=set();fatal_seen=False
    bad={'uid_wrong':0,'gid_wrong':1,'groups_wrong':2,'caps_wrong':3,'nnp_wrong':4,'as_hard_wrong':5,'as_soft_wrong':6,'cg_wrong':7}
    expected=[[999],[989],[989],0,1,'1073741824','1073741824','/dclr6batch14.slice/dclr6batch14-c00.service']
    for x in trace:
        name=x['event'];f=x['facts'];decision=x['response']['decision']
        if f['frame_name']!=name or len(f['checks'])!=8:raise ValueError('READY_RAW_FRAME')
        for i,c in enumerate(f['checks']):
            if c['check_id']!='CR-%02d'%(i+1) or c['expected']!=expected[i]:raise ValueError('READY_RAW_EXPECTED')
            if name in bad and i==bad[name] and (c['observed'] is None or all(v==expected[i] for v in c['observed'])):raise ValueError('READY_FAULT_NOT_EXERCISED')
        stable_bad=name in bad or name in ('wrong_unit','wrong_type','tasks_wrong','proc_as_wrong','proc_cg_wrong')
        read_bad=name in ('read_error','field_missing','target_exit')
        pid_bad=name=='pid_reused';boot_bad=name=='boot_wrong';lock_bad=name=='missing_lock';version_bad=name=='cross_version'
        terminal=stable_bad or read_bad or pid_bad or boot_bad or lock_bad or version_bad or name in ('stop','closed','timeout','service_failed')
        if decision=='READY':
            for i,c in enumerate(f['checks']):
                if c['observed'] is None or not all(v==expected[i] for v in c['observed']):found.add(c['check_id'])
            if read_bad or f['error'] is not None:found.add('CR-READ_ERROR')
            if pid_bad or f['identity_before']!=f['identity_after']:found.add('CR-PID')
            if boot_bad or f['boot_before']!=f['expected_boot'] or f['boot_after']!=f['expected_boot']:found.add('CR-BOOT')
            if lock_bad or not f['binding_valid']:found.add('CR-LOCK')
            if version_bad or not f['coherent']:found.add('CR-SNAPSHOT')
            if not f['hard_aux_valid']:found.add('CR-AUX')
            if f['stopped'] or f['expired'] or f['phases']!=['READY','READY']:found.add('CR-GRANT')
            if fatal_seen:found.add('CR-REACTIVATION')
        if terminal and decision=='STARTING':
            found.add('CR-STALE' if x['response']['shadow']!=f else 'CR-WAIT-MISMATCH')
            if stable_bad:found.add('CR-WAIT-MISMATCH')
            if f['expired']:found.add('CR-TIMEOUT')
        if name=='timeout' and decision not in ('FAILED',):found.add('CR-TIMEOUT')
        fatal_seen=fatal_seen or terminal
    return sorted(found)


def check_job(base,job,index,binding):
    try:
        p=Path(base)/('ready_case_%03d.json'%index);fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
        try:
            s=os.fstat(fd)
            if (s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)!=(0,0,0o600,1) or s.st_size>131072:raise ValueError('READY_RAW_METADATA')
            raw=os.read(fd,s.st_size+1)
            if len(raw)!=s.st_size:raise ValueError('READY_RAW_SHORT')
        finally:os.close(fd)
        row=json.loads(raw);inp=json.dumps(job,sort_keys=True,separators=(',',':')).encode()
        if row['case_id']!=job['case_id'] or row['binding']!=binding or row['input_sha256']!=hashlib.sha256(inp).hexdigest():raise ValueError('READY_RAW_BINDING')
        if row['origin']!='SIMULATION_ONLY/1' or row['global_after']-row['global_before']!=6:raise ValueError('READY_SCOPE_OR_CHARGE')
        if [x['event'] for x in row['trace']]!=job['frames']:raise ValueError('READY_RAW_ORDER')
        v=violations(row['trace']);last=row['trace'][-1]['response']['decision']
        accepted=(not v and last==job['expected']) if job['variant']=='safe' else job['expected_violation'] in v and set(v).issubset(job['allowed_violations'])
        return {'case_id':job['case_id'],'accepted':accepted,'status':('PASS' if job['variant']=='safe' else 'MUTATION_DETECTED') if accepted else 'FAIL',
                'violations':v,'raw_sha256':hashlib.sha256(raw).hexdigest()}
    except (OSError,ValueError,KeyError,TypeError) as exc:return {'case_id':job['case_id'],'accepted':False,'status':'EVIDENCE_MISSING','error':repr(exc)}


def check_suite(base,cfg,binding):
    expected={'ready_case_%03d.json'%i for i in range(len(cfg['jobs']))}
    if {p.name for p in Path(base).glob('ready_case_*.json')}!=expected:raise ValueError('READY_RAW_JOB_SET')
    rows=[check_job(base,j,i,binding) for i,j in enumerate(cfg['jobs'])]
    return {'schema':'C00-READY-QUALIFICATION/1','origin':'SIMULATION_ONLY/1','binding':binding,
            'accepted':all(r['accepted'] for r in rows),'results':rows}
