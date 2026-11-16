"""Independent BC event oracle: imports no gate, simulator, guard or business code."""
import hashlib
import json
import os
from pathlib import Path
import stat


def check_job(base,job,index,binding):
    try:
        p=Path(base)/('bc_case_%03d.json'%index);fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
        try:
            s=os.fstat(fd)
            if (s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)!=(0,0,0o600,1) or s.st_size>131072:raise ValueError('BC_RAW_METADATA')
            raw=os.read(fd,s.st_size+1)
            if len(raw)!=s.st_size:raise ValueError('BC_RAW_SHORT')
        finally:os.close(fd)
        row=json.loads(raw);input_bytes=json.dumps(job,sort_keys=True,separators=(',',':')).encode()
        if row['binding']!=binding or row['case_id']!=job['case_id'] or row['input_sha256']!=hashlib.sha256(input_bytes).hexdigest():raise ValueError('BC_RAW_BINDING')
        if row['profile']!='SIMULATED_RESTART/1' or row['global_after']-row['global_before']!=11:raise ValueError('BC_SCOPE_OR_CHARGE')
        if len(row['trace'])!=len(job['events']):raise ValueError('BC_TRACE_LENGTH')
        epoch=1;alive=True;static_ok=True;resources=True;identity_ok=True;closed=False;stop=False;violations=set();prior_budget=0
        for event,x in zip(job['events'],row['trace']):
            if x['event']!=event:raise ValueError('BC_EVENT_ORDER')
            if event=='reboot':epoch+=1;alive=False
            if event in ('new_process','recycle_owner'):alive=True
            if event in ('orchestrator_exit','launcher_exit'):alive=False
            if event=='artifact_drift':static_ok=False
            if event=='resources_change':resources=False
            if event=='identity_change':identity_ok=False
            if event=='prior_closed':closed=True
            if event=='stop':stop=True
            if event=='prior_window':prior_budget=37
            f=x['facts'];expected='00000000-0000-4000-8000-%012d'%epoch
            if (f['boot_id']!=expected or f['process_alive']!=alive or f['static_valid']!=static_ok or
                f['resource_valid']!=resources or f['identity_valid']!=identity_ok or f['closed']!=closed or f['stop']!=stop):raise ValueError('BC_INDEPENDENT_KERNEL_TRUTH')
            t=x['ticket']
            if x['decision']=='ISSUED' and len(set(f['chain_boots']+[expected]))!=1:violations.add('BC-1')
            if x['decision']=='ACTIVATED':
                if t['boot_id']!=expected:violations.update(['BC-1','BC-3'])
                if not resources or not static_ok:violations.add('BC-2')
                if not static_ok or t['binding']!=f['binding']:violations.add('BC-3')
                if closed or stop:violations.update(['BC-3','BC-5'])
                if not alive or not identity_ok or not f['cap_live']:violations.add('BC-8')
                if not resources or not static_ok:violations.add('BC-5')
            if x['activations']>1:violations.add('BC-4')
            if x['started'] and (not f['service_active'] or not alive or t is None or t['boot_id']!=expected):violations.add('BC-7')
            if x['reset'] or f['budget_used']<prior_budget:violations.add('BC-6')
        last=row['trace'][-1]
        if job['variant']=='safe':
            accepted=not violations and last['decision']==job['expected_last'] and last['activations']==job['expected_activations']
        else:accepted=job['expected_violation'] in violations and set(violations).issubset(job['allowed_violations'])
        return {'case_id':job['case_id'],'accepted':accepted,'status':('PASS' if job['variant']=='safe' else 'MUTATION_DETECTED') if accepted else 'FAIL',
                'violations':sorted(violations),'raw_sha256':hashlib.sha256(raw).hexdigest()}
    except (OSError,ValueError,KeyError,TypeError) as exc:
        return {'case_id':job['case_id'],'accepted':False,'status':'EVIDENCE_MISSING','error':repr(exc)}


def check_suite(base,cfg,binding):
    expected={'bc_case_%03d.json'%i for i in range(len(cfg['jobs']))}
    if {p.name for p in Path(base).glob('bc_case_*.json')}!=expected:raise ValueError('BC_JOB_SET')
    rows=[check_job(base,j,i,binding) for i,j in enumerate(cfg['jobs'])]
    return {'schema':'BC-SIM-QUALIFICATION/1','profile':'SIMULATED_RESTART/1','binding':binding,
            'accepted':all(r['accepted'] for r in rows),'results':rows}
