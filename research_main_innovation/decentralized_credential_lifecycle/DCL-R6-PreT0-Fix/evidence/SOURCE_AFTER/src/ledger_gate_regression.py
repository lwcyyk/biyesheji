"""Frozen GATE-LEDGER-ANOMALY specimens. Runtime only inside the Root RANGE audit."""
import copy
import hashlib
import json
import os
from pathlib import Path
import stat
import struct
import boot_continuity as BC
import ledger_gate as L
import ledger_gate_oracle as O

def contract(G):
    a,m=G.authorization();p=G.SOURCE.parent/'inputs/ledger_gate_contract.json'
    if G.digest(p)!=m['ledger_gate_contract_sha256'] or a.get('ledger_gate_contract_sha256')!=m['ledger_gate_contract_sha256']:
        raise G.AdmissionBlocked('LEDGER_GATE_CONTRACT_HASH')
    cfg=G.trusted(p)
    if cfg['schema']!='GATE-LEDGER-ANOMALY/1' or cfg['batch_id']!=G.ROOT.name or len(cfg['jobs'])!=18 or cfg['prepay_per_job']!=32:
        raise G.AdmissionBlocked('LEDGER_GATE_CONTRACT')
    return cfg

def specimens(job,binding):
    """Create native-format bytes in memory; future writes use fresh private dirs."""
    cap=1000000
    request={'protocol':'EXACT-RANGE/1','batch_id':binding['batch_id'],'boot_id':binding['boot_id'],
        'T0':binding['T0'],'task_id':'C04.fifth-task.v1','N':1,'case':'C04',
        'source_manifest':binding['static_manifest_sha256'],'contract_sha256':binding['child_contracts_sha256']}
    rows=[]
    for n in range(2):
        prepared={'protocol':'EXACT-RANGE/1','status':'PREPARED','before':n,'after':n+1,'amount':1,
            'cap':cap,'request':request if n==0 else None,'boot_id':binding['boot_id'],
            'boottime':binding['T0']+n+1,'utc_ns':100+n*2}
        rows.extend([prepared,{**prepared,'status':'COMMITTED','boottime':binding['T0']+n+1.5,'utc_ns':101+n*2}])
    intent=copy.deepcopy(rows[-1]);used=2;kind=job['kind']
    if kind=='missing_commit':rows.pop()
    elif kind=='duplicate_commit':rows.append(copy.deepcopy(rows[-1]))
    elif kind=='pair_mismatch':rows[1]['amount']=2
    elif kind=='wrong_order':rows[0],rows[1]=rows[1],rows[0]
    elif kind=='overflow':used=cap+1
    elif kind=='batch':rows[0]['request']['batch_id']='other-batch'
    elif kind=='boot':rows[0]['boot_id']='other-boot'
    elif kind=='sequence_gap':rows[2]['before']=3;rows[2]['after']=4
    blobs={'counter':b'BRNGv001'+struct.pack('<QQ',used,cap),
        'intent':O.canonical(intent),'journal':b''.join(O.canonical(row)+b'\n' for row in rows)}
    if kind=='truncated':blobs['journal']=blobs['journal'][:-1]
    descriptor={'schema':L.PROFILE,'binding':dict(binding),'cap':cap,'files':{
        role:{'name':L.NAMES[role],'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()} for role,raw in blobs.items()}}
    if kind=='lock':descriptor['binding']['execution_lock_sha256']='different-lock'
    elif kind=='foreign_journal':descriptor['files']['journal']['name']='../historical/visits.bin.journal.jsonl'
    elif kind=='digest':blobs['journal']=blobs['journal'].replace(b':',b': ',1)
    elif kind=='missing_evidence':del blobs['intent']
    return blobs,descriptor

def subject(base,descriptor,binding,mutation):
    result=L.evaluate(base,descriptor,1000000,binding)
    bypass={
        'ignore_commit_missing':('GLOBAL_COUNTER_JOURNAL_MISMATCH',),
        'ignore_cumulative_overflow':('COUNTER_OVERFLOW',),
        'ignore_batch_mismatch':('GLOBAL_REQUEST_IDENTITY',),
        'ignore_log_digest':('GATE_LEDGER_DIGEST',),
    }
    if mutation is not None:
        if mutation not in bypass:raise ValueError('UNKNOWN_LEDGER_MUTATION')
        if result['decision']=='REJECT_LEDGER_ANOMALY' and result['reason'].startswith(bypass[mutation]):
            return {'decision':'ACCEPT_LEDGER_HEALTHY','reason':'MUTANT_SWALLOWED:'+result['reason'],'ignored_result':result}
    return result

def write_bytes(directory,name,raw):
    fd=os.open(directory/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    try:
        if os.write(fd,raw)!=len(raw):raise ValueError('LEDGER_SPECIMEN_SHORT_WRITE')
        os.fsync(fd)
    finally:os.close(fd)

def run_suite(G):
    if os.geteuid()!=0 or not G._ROOT_SAFETY_AUDIT:raise G.AdmissionBlocked('ROOT_LEDGER_TEST_CONTEXT')
    G.safety_mode();cfg=contract(G);binding=G.safety_binding();root=G.ROOT/'inputs/root_private/boot'
    start=G.count();calls=0
    def charge():
        nonlocal calls
        if calls>=cfg['hard_visits']:raise G.LimitReached('LEDGER_GATE_VISIT_CAP')
        G.safety_charge();calls+=1
    charge()
    with BC.Store() as store:
        os.mkdir('ledger_gate',0o700,dir_fd=store.fd)
        parent=os.open('ledger_gate',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=store.fd)
        try:
            for i,job in enumerate(cfg['jobs']):
                G.root_checkpoint()
                for _ in range(cfg['prepay_per_job']):charge()
                os.mkdir('%03d'%i,0o700,dir_fd=parent)
                base=root/'ledger_gate'/('%03d'%i)
                blobs,descriptor=specimens(job,binding)
                for role,raw in blobs.items():write_bytes(base,L.NAMES[role],raw)
                directory=os.open(base,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
                try:os.fsync(directory)
                finally:os.close(directory)
                answer=subject(base,descriptor,binding,job['mutant'])
                store.put('ledger_case_%03d.json'%i,{'case_id':job['case_id'],'binding':binding,
                    'input_sha256':hashlib.sha256(O.canonical(job)).hexdigest(),'descriptor':descriptor,
                    'subject':answer,'origin':'ISOLATED_NATIVE_FORMAT/1','actor':G.identity(),'sample':G.stamp()},exclusive=True)
                immediate=O.check_case(root,job,i,binding)
                if not immediate['accepted']:raise G.AdmissionBlocked('LEDGER_GATE_FIRST_FAILURE:'+job['case_id']+':'+immediate['status'])
            os.fsync(parent);os.fsync(store.fd)
        finally:os.close(parent)
        for job in cfg['jobs']:charge()
        result=O.check_suite(root,cfg,binding)
        if not result['accepted']:raise G.AdmissionBlocked('LEDGER_GATE_RAW_AUDIT')
        result.update(schema='GATE-LEDGER-QUALIFICATION/1',contract_sha256=G.digest(G.SOURCE.parent/'inputs/ledger_gate_contract.json'),
            checker_sha256=G.digest(G.SOURCE/'ledger_gate_oracle.py'),subject_sha256=G.digest(G.SOURCE/'ledger_gate.py'),
            global_before=start,global_after=G.count(),charged=calls,sample=G.stamp())
        store.put('GATE_LEDGER_QUALIFICATION.json',result,exclusive=True,public=True)
    return verify_qualification(G,binding)

def verify_qualification(G,binding):
    cfg=contract(G);root=G.ROOT/'inputs/root_private/boot';path=G.ROOT/'inputs/GATE_LEDGER_QUALIFICATION.json';q=G.trusted(path)
    if (q['schema']!='GATE-LEDGER-QUALIFICATION/1' or q['binding']!=binding or not q['accepted'] or
        q['contract_sha256']!=G.digest(G.SOURCE.parent/'inputs/ledger_gate_contract.json') or
        q['checker_sha256']!=G.digest(G.SOURCE/'ledger_gate_oracle.py') or q['subject_sha256']!=G.digest(G.SOURCE/'ledger_gate.py')):
        raise G.AdmissionBlocked('LEDGER_GATE_QUALIFICATION_BINDING')
    # Qualifier rechecks actual bytes, rather than trusting the stored PASS label.
    if os.geteuid()==0:
        for job in cfg['jobs']:
            if G.count()-q['global_before']>=cfg['hard_visits']:
                raise G.LimitReached('LEDGER_GATE_REAUDIT_VISIT_CAP')
            G.safety_charge()
        fresh=O.check_suite(root,cfg,binding)
        if not fresh['accepted'] or fresh['results']!=q['results']:raise G.AdmissionBlocked('LEDGER_GATE_RAW_CHANGED')
    if len(q['results'])!=18 or {r['case_id'] for r in q['results']}!={j['case_id'] for j in cfg['jobs']}:
        raise G.AdmissionBlocked('LEDGER_GATE_RESULT_SET')
    for row,job in zip(q['results'],cfg['jobs']):
        target='MUTATION_DETECTED' if job['variant']=='mutant' else ('PASS' if job['kind']=='healthy' else 'REJECT_LEDGER_ANOMALY')
        if row['case_id']!=job['case_id'] or not row['accepted'] or row['status']!=target or not row['raw_files']:
            raise G.AdmissionBlocked('LEDGER_GATE_REQUIRED_RESULT')
    return {'qualification_sha256':G.digest(path),'status':'REJECT_LEDGER_ANOMALY','subcases':len(q['results']),
            'mutants_detected':sum(row['status']=='MUTATION_DETECTED' for row in q['results'])}
