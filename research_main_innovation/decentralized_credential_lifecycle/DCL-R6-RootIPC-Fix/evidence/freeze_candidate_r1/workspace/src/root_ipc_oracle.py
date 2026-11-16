"""Independent raw IPC oracle. Imports no guard, publisher, subject or handoff module."""
import hashlib
import json
import os
from pathlib import Path
import stat


def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'))


def load(p):
    fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
    try:
        s=os.fstat(fd)
        if not stat.S_ISREG(s.st_mode) or s.st_nlink!=1 or s.st_uid!=0 or s.st_gid!=0 or stat.S_IMODE(s.st_mode)!=0o600 or s.st_size>131072:
            raise ValueError('IPC_RAW_PROVENANCE')
        raw=os.read(fd,s.st_size+1)
        if len(raw)!=s.st_size:raise ValueError('IPC_RAW_SHORT')
        return raw,json.loads(raw)
    finally:os.close(fd)


def violations(job,r):
    v=set();scenario=job['scenario'];subject=r['subject']
    if r['kind']=='file':
        if 'probe' in r:
            p=r['probe']
            if p['rlimit_as']!=[1073741824,1073741824] or p['raw_wait_status']!=0:raise ValueError('IPC_PROBE_WITNESS')
            expected_uid=65534 if scenario=='unauthorized' else 999
            if p['uid']!=expected_uid or p['gid']!=(65534 if expected_uid==65534 else 989) or p['groups']!= ([] if expected_uid==65534 else [989]):raise ValueError('IPC_PROBE_CREDENTIALS')
            if scenario=='receipt_read':
                m=r['metadata']
                if (m['uid'],m['gid'],m['mode'])!=(0,989,0o640) or not p['allowed']:v.add('IPC-1')
                if p.get('sha256')!=r.get('payload_sha256'):raise ValueError('IPC_PROBE_DIGEST')
            elif scenario=='receipt_write':
                if p['allowed']:v.add('IPC-2')
            elif scenario not in ('unauthorized','private_write','private_read'):
                m=r['metadata'];valid=(m['uid'],m['gid'],m['mode'],m['nlink'],m['regular'])==(999,989,0o600,1,True)
                if subject=='ADMITTED' and (not valid or not p['allowed']):v.add('IPC-1')
                if subject=='ADMITTED' and not valid:v.add('IPC-3')
                if valid and not p['allowed']:v.add('IPC-1')
                if p['allowed'] and p.get('sha256')!=r.get('payload_sha256'):raise ValueError('IPC_PROBE_DIGEST')
            elif p['allowed']:v.add('IPC-2' if scenario.startswith('private') else 'IPC-1')
            if scenario in ('historical','bad_metadata') and (r['metadata']['uid']!=0 or r['metadata']['mode']!=0o600 or p['allowed']):raise ValueError('IPC_HISTORICAL_FAULT_NOT_EXERCISED')
        if 'actual_binding' in r and r['actual_binding']!=r['expected_binding'] and subject=='ADMITTED':v.add('IPC-5')
        if scenario in ('outside','symlink','hardlink'):
            if subject!='BLOCKED':v.add('IPC-4')
            if 'anchor_before' in r and r['anchor_before']!=r['anchor_after']:v.add('IPC-4')
        if scenario.startswith('fault_') and (subject!='BLOCKED' or r.get('errno')!=5):v.add('IPC-3')
        if scenario in ('historical','bad_metadata') and subject!='BLOCKED':v.add('IPC-1')
    elif r['kind']=='wait':
        if any(r['actual_flags'].values()) and subject=='ADMITTED':v.add('IPC-7')
        if r['actual_flags']['closed'] and subject=='ADMITTED':v.add('IPC-8')
        if scenario!='ready' and subject=='ADMITTED' and not job.get('mutant'):v.add('IPC-7')
        if scenario=='ready' and subject!='ADMITTED':v.add('IPC-1')
    else:
        f=dict(closed=False,binding_ok=True,sender_ok=True,version_ok=True,window_ok=True,
               budget_ok=True,receiver_ready=True,receiver_alive=True,stop_alive=True,
               witness=None,now=0,expires=12,prepared=False,commit=False,durable_ack=False,exit_observed=False)
        if len(r['rows'])!=len(r['events']):raise ValueError('IPC_EVENT_SET')
        for e,row in zip(r['events'],r['rows']):
            if e=='prepare':f['prepared']=True
            elif e=='close':f['closed']=True
            elif e=='commit':f['commit']=True;f['durable_ack']=True
            elif e=='exit23':f['exit_observed']=True
            elif e=='witness23':f['witness']=23
            elif e not in ('observe','repeat'):raise ValueError('IPC_UNFROZEN_EVENT')
            if row['facts']!=f or row['event']!=e:raise ValueError('IPC_EVENT_TRUTH')
            if row['subject_state']=='VERIFIED':
                if not(f['prepared'] and f['commit'] and f['durable_ack'] and f['exit_observed'] and f['witness']==23):v.add('IPC-6')
                if f['closed']:v.add('IPC-8')
            if row['classification_count']>1:v.add('IPC-9')
    return sorted(v)


def check_job(base,job,i,binding):
    try:
        raw,row=load(Path(base)/('ipc_case_%03d.json'%i))
        if row['binding']!=binding or row['case_id']!=job['case_id'] or row['input_sha256']!=hashlib.sha256(canon(job).encode()).hexdigest():raise ValueError('IPC_INPUT_BINDING')
        if row['actor']['boot_id']!=binding['boot_id'] or row['after']['boot_id']!=binding['boot_id'] or row['after']['boottime']<row['before']['boottime']:raise ValueError('IPC_ACTOR_TIME')
        if not 0<row['global_after']-row['global_before']<=8:raise ValueError('IPC_RAW_CHARGE')
        if 'expected_binding' in row['result'] and row['result']['expected_binding']!=binding:raise ValueError('IPC_REFERENCE_BINDING')
        v=violations(job,row['result'])
        accepted=(not v) if job['variant']=='safe' else job['expected_violation'] in v
        if not set(v).issubset(job['allowed_violation_set']):accepted=False
        if job['variant']=='safe':
            expected=job['expected_subject']
            accepted=accepted and row['result']['subject']==expected
        return {'case_id':job['case_id'],'accepted':accepted,'status':('PASS' if job['variant']=='safe' else 'MUTATION_DETECTED') if accepted else 'FAIL',
                'violations':v,'raw_sha256':hashlib.sha256(raw).hexdigest()}
    except (OSError,ValueError,KeyError,TypeError) as exc:
        return {'case_id':job['case_id'],'accepted':False,'status':'EVIDENCE_MISSING','error':repr(exc)}


def check_suite(base,cfg,binding):
    expected_files={'ipc_case_%03d.json'%i for i in range(len(cfg['jobs']))}
    actual_files={p.name for p in Path(base).glob('ipc_case_*.json') if p.name!='ipc_case_999.json'}
    if actual_files!=expected_files:raise ValueError('IPC_RAW_JOB_SET')
    results=[check_job(base,job,i,binding) for i,job in enumerate(cfg['jobs'])]
    return {'schema':'ROOT-IPC-QUALIFICATION/1','binding':binding,'accepted':all(r['accepted'] for r in results),'results':results}
