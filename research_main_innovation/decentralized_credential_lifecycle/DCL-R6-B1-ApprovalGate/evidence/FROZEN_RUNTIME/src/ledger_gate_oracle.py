"""Independent raw reference for ledger-gate specimens; no subject/driver imports."""
import hashlib
import json
import os
from pathlib import Path
import stat
import struct

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def read(path,limit=131072):
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
    try:
        s=os.fstat(fd)
        if not stat.S_ISREG(s.st_mode) or s.st_size>limit:raise ValueError('REFERENCE_FILE_BOUND')
        raw=os.read(fd,s.st_size+1)
        if len(raw)!=s.st_size:raise ValueError('REFERENCE_SHORT_READ')
        return raw
    finally:os.close(fd)

def inspect(base,descriptor,cap,binding):
    """Decode independently, retaining raw faults even when the subject accepts."""
    issues=set();base=Path(base)
    names={'counter':'visits.bin','intent':'visits.bin.intent.json','journal':'visits.bin.journal.jsonl'}
    if descriptor.get('binding')!=binding or descriptor.get('cap')!=cap or descriptor.get('schema')!='GATE-LEDGER-SNAPSHOT/1':issues.add('IDENTITY')
    blobs={}
    for role,name in names.items():
        item=descriptor.get('files',{}).get(role,{})
        if item.get('name')!=name:issues.add('FOREIGN_PATH');continue
        try:raw=read(base/name)
        except (OSError,ValueError):issues.add('MISSING');continue
        blobs[role]=raw
        if item.get('bytes')!=len(raw) or item.get('sha256')!=hashlib.sha256(raw).hexdigest():issues.add('DIGEST')
    if set(blobs)!=set(names):return sorted(issues)
    raw=blobs['counter']
    if len(raw)!=24 or raw[:8]!=b'BRNGv001':issues.add('COUNTER');return sorted(issues)
    used,limit=struct.unpack('<QQ',raw[8:])
    if limit!=cap or used>cap:issues.add('CAPACITY')
    try:state=json.loads(blobs['intent'])
    except (ValueError,UnicodeDecodeError):issues.add('MISSING');return sorted(issues)
    if state.get('protocol')!='EXACT-RANGE/1' or state.get('status')!='COMMITTED' or state.get('after')!=used or state.get('cap')!=cap:issues.add('INTENT')
    if blobs['journal'] and not blobs['journal'].endswith(b'\n'):issues.add('TRUNCATION')
    rows=[]
    try:
        for line in blobs['journal'].splitlines():rows.append(json.loads(line))
    except (ValueError,UnicodeDecodeError):issues.add('TRUNCATION');return sorted(issues)
    cursor=0;awaiting=None;last=None;tasks=set()
    for entry in rows:
        if entry.get('protocol')!='EXACT-RANGE/1' or entry.get('cap')!=cap:issues.add('IDENTITY')
        if entry.get('boot_id')!=binding['boot_id']:issues.add('BOOT')
        request=entry.get('request')
        if request is not None:
            if request.get('batch_id')!=binding['batch_id']:issues.add('BATCH')
            if any(request.get(k)!=binding[k] for k in ('boot_id','T0')):issues.add('IDENTITY')
            if request.get('source_manifest')!=binding['static_manifest_sha256'] or request.get('contract_sha256')!=binding['child_contracts_sha256']:issues.add('IDENTITY')
            exact={'C02.memory.v1':32896,'C03.shared.v1':4096,'C04.fifth-task.v1':1}
            if request.get('task_id') not in exact or request.get('N')!=exact.get(request.get('task_id')) or entry.get('amount')!=request.get('N'):issues.add('RANGE')
        elif entry.get('amount')!=1:issues.add('RANGE')
        try:
            if not 0<=entry['before']<entry['after']<=cap:issues.add('CAPACITY')
            if entry['status']=='PREPARED':
                if awaiting is not None:issues.add('PAIR')
                if entry['before']!=cursor or entry['after']-cursor!=entry['amount']:issues.add('SEQUENCE')
                awaiting=entry
            elif entry['status']=='COMMITTED':
                if awaiting is None or any(entry.get(k)!=awaiting.get(k) for k in ('before','after','amount','cap','request','protocol','boot_id')):issues.add('PAIR')
                cursor=entry['after'];awaiting=None;last=entry
                if request is not None:
                    task=request['task_id']
                    if task in tasks:issues.add('PAIR')
                    tasks.add(task)
            else:issues.add('PAIR')
        except (KeyError,TypeError):issues.add('PAIR')
    if awaiting is not None:issues.add('PAIR')
    if cursor!=used:issues.add('SEQUENCE')
    if last is not None and state!=last:issues.add('INTENT')
    return sorted(issues)

def check_case(boot_root,job,index,binding):
    try:
        root=Path(boot_root);row=json.loads(read(root/('ledger_case_%03d.json'%index)))
        if row['binding']!=binding or row['case_id']!=job['case_id'] or row['input_sha256']!=hashlib.sha256(canonical(job)).hexdigest():raise ValueError('REFERENCE_BINDING')
        base=root/'ledger_gate'/('%03d'%index)
        issues=inspect(base,row['descriptor'],1000000,binding)
        decision=row['subject']['decision'];fault=bool(issues)
        exercised=(not fault) if job['kind']=='healthy' else job['family'] in issues
        if job['variant']=='mutant':
            accepted=exercised and decision=='ACCEPT_LEDGER_HEALTHY'
            status='MUTATION_DETECTED' if accepted else 'MUTATION_NOT_DETECTED'
        elif job['kind']=='healthy':
            accepted=exercised and decision=='ACCEPT_LEDGER_HEALTHY';status='PASS' if accepted else 'FAIL'
        else:
            accepted=exercised and decision=='REJECT_LEDGER_ANOMALY';status='REJECT_LEDGER_ANOMALY' if accepted else 'FAIL'
        files={}
        for p in sorted(base.iterdir()):
            if p.is_symlink() or not p.is_file():raise ValueError('REFERENCE_SPECIMEN_TYPE')
            files[p.name]=hashlib.sha256(read(p)).hexdigest()
        return {'case_id':job['case_id'],'status':status,'accepted':accepted,'fault_exercised':exercised,
                'issues':issues,'subject_decision':decision,'binding':binding,'raw_files':files,
                'row_sha256':hashlib.sha256(read(root/('ledger_case_%03d.json'%index))).hexdigest()}
    except (OSError,ValueError,KeyError,TypeError) as exc:
        return {'case_id':job['case_id'],'status':'EVIDENCE_MISSING','accepted':False,'error':repr(exc),'binding':binding}

def check_suite(boot_root,cfg,binding):
    rows=[check_case(boot_root,job,i,binding) for i,job in enumerate(cfg['jobs'])]
    return {'accepted':all(row['accepted'] for row in rows),'results':rows,'binding':binding}
