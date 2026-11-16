"""Linux R6 static deployment candidate. Dynamic authorization is separate.

The root launcher and external stop service are trusted infrastructure. Payload
admission checks kernel facts in addition to root-owned authorization records.
No role is executed by py_compile. Historical Windows sources stay archived.
"""
import argparse
from contextlib import contextmanager
import errno
import fcntl
import hashlib
import json
import os
from pathlib import Path
import pwd
import resource
import runpy
import select
import signal
import stat
import struct
import subprocess
import sys
import threading
import time
import traceback
import zipfile

SOURCE = Path(__file__).resolve().parent
PYTHON = '/usr/bin/python3.12'
PYTHON_SHA = 'e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f'
AS_CAP = 1 << 30
VISIT_CAP = 1000000
CASES = tuple('C%02d' % i for i in range(13))
ROOTS = (Path('/var/lib/dcl-r6/cr01'), Path('/var/lib/dcl-r6/batch08'))
def _arg(name, default=None):
    return sys.argv[sys.argv.index(name)+1] if name in sys.argv else default
ROOT = Path(_arg('--batch-root', str(ROOTS[0]))).resolve()
OUT = ROOT / 'out'
PARENT = 'dclr6' + ROOT.name + '.slice'
_TICKET = None
_WATCH = None
_NORMAL = threading.Event()
_LOCKS = {}
_LOCKS_LOCK = threading.Lock()
BUDGET_PROTOCOL = 'EXACT-RANGE/1'
COUNTER_MAGIC = b'BRNGv001'
_HALTED = threading.Event()
_TIMING = {}
_TIMING_LOCK = threading.Lock()
_RESERVATION_MINT = object()
_LOCAL_CREDIT_MINT = object()
_ROOT_SAFETY_AUDIT = False
_COORDINATOR_ID = None

def monotonic_ns(): return time.clock_gettime_ns(time.CLOCK_BOOTTIME)
def _timing(stage, start, end, utc_start, utc_end, error=None):
    with _TIMING_LOCK:
        r=_TIMING.setdefault(stage,{'count':0,'total_ns':0,'min_ns':None,'max_ns':0,'errors':0,'first_samples':[]})
        duration=end-start;r['count']+=1;r['total_ns']+=duration
        r['min_ns']=duration if r['min_ns'] is None else min(r['min_ns'],duration)
        r['max_ns']=max(r['max_ns'],duration);r['errors']+=int(error is not None)
        sample={'begin_boottime_ns':start,'end_boottime_ns':end,'begin_utc_ns':utc_start,
                'end_utc_ns':utc_end,'duration_ns':duration,'error':error}
        if len(r['first_samples'])<8:r['first_samples'].append(sample)
        r['last_sample']=sample
def timed(stage, fn, *args, **kwargs):
    begin=monotonic_ns();utc_begin=time.time_ns();error=None
    try:return fn(*args,**kwargs)
    except BaseException as exc:error=repr(exc);raise
    finally:_timing(stage,begin,monotonic_ns(),utc_begin,time.time_ns(),error)
def timing_event(stage):
    t=monotonic_ns();u=time.time_ns();_timing(stage,t,t,u,u)
def timing_snapshot():
    with _TIMING_LOCK:return json.loads(json.dumps(_TIMING))
def sync_fd(fd,stage):return timed(stage+'.fsync',os.fsync,fd)
def halt_budget(reason):
    _HALTED.set()
    try:request_stop('BUDGET_HALTED:'+str(reason))
    except BaseException:pass
def budget_health():
    if _HALTED.is_set():raise AdmissionBlocked('BUDGET_HALTED')
def execution_deadline(case=None):
    budget_health();s=state();t=_TICKET if _TICKET is not None else ticket(case)
    if stopped() or now()>=min(s['stop_at'],t['case_deadline']):raise LimitReached('WALL_OR_STOP_LIMIT')
    return s,t

class AdmissionBlocked(RuntimeError): pass
class LimitReached(RuntimeError): pass

def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def boot_id(): return Path('/proc/sys/kernel/random/boot_id').read_text().strip()
def now(): return time.clock_gettime(time.CLOCK_BOOTTIME)
def stamp(): return {'boottime': now(), 'utc_ns': time.time_ns(), 'boot_id': boot_id()}
def _check_root():
    validate_root(ROOT)
def validate_root(path):
    if Path(path).resolve() not in ROOTS: raise AdmissionBlocked('UNAPPROVED_ROOT')
def _inside(path, base):
    p = Path(path).resolve()
    if not p.is_relative_to(base.resolve()): raise AdmissionBlocked('PATH_OUTSIDE_ROOT')
    return p
def trusted(path):
    p = Path(path)
    fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        s = os.fstat(fd)
        if not stat.S_ISREG(s.st_mode) or s.st_uid != 0 or s.st_mode & 0o022:
            raise AdmissionBlocked('UNTRUSTED_ROOT_RECORD:' + str(p))
        if s.st_size > 4*1024*1024: raise AdmissionBlocked('OVERSIZE_RECORD')
        raw = os.read(fd, s.st_size+1)
        if len(raw) != s.st_size: raise AdmissionBlocked('SHORT_RECORD')
        return json.loads(raw.decode('utf-8-sig'))
    finally: os.close(fd)
def _full(fd, data):
    # A short write poisons the operation; the caller never grants credit.
    if os.write(fd, data) != len(data): raise AdmissionBlocked('SHORT_WRITE')
def root_ipc():
    if str(SOURCE) not in sys.path:sys.path.insert(0,str(SOURCE))
    import root_ipc as RI
    return RI
def boot_continuity():
    if str(SOURCE) not in sys.path:sys.path.insert(0,str(SOURCE))
    import boot_continuity as BC
    return BC
def root_checkpoint(allow_uninitialized=False):
    return root_ipc().checkpoint(sys.modules[__name__],allow_uninitialized)
def atomic(path, data, root_record=False, timing_stage='metadata.atomic'):
    _check_root()
    if os.geteuid()==0:
        return root_ipc().publish(sys.modules[__name__],path,data,root_record,timing_stage)
    p = _inside(path, ROOT if root_record and os.geteuid() == 0 else OUT)
    p.parent.mkdir(parents=True, exist_ok=True)
    raw = timed(timing_stage+'.encode',lambda:json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2).encode('utf-8'))
    tmp = p.with_name(p.name + '.tmp.%s.%s' % (os.getpid(), threading.get_ident()))
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o640 if root_record else 0o600)
    try:
        if root_record:
            os.fchown(fd,0,pwd.getpwnam('dcl-r6').pw_gid)
            os.fchmod(fd,0o640)
        timed(timing_stage+'.write',_full,fd,raw); sync_fd(fd,timing_stage+'.file')
    finally: os.close(fd)
    os.replace(tmp, p)
    d = os.open(p.parent, os.O_RDONLY | os.O_DIRECTORY)
    try: sync_fd(d,timing_stage+'.directory')
    finally: os.close(d)
def write(path, data): atomic(path, data)
def identity(pid=None):
    pid = os.getpid() if pid is None else int(pid)
    raw = Path('/proc/%s/stat' % pid).read_text()
    fields = raw[raw.rfind(')')+2:].split()
    return {'pid': pid, 'start_ticks': int(fields[19]), 'boot_id': boot_id()}
def _status(pid='self'):
    return dict(line.split(':',1) for line in Path('/proc/%s/status' % pid).read_text().splitlines() if ':' in line)
def _number(text):
    value = text.strip()
    return value if value == 'max' else int(value)
def cg_path():
    rows = Path('/proc/self/cgroup').read_text().splitlines()
    path = next((r[3:] for r in rows if r.startswith('0::')), None)
    if path is None or '..' in Path(path).parts: raise AdmissionBlocked('CGROUP_V2_REQUIRED')
    return Path('/sys/fs/cgroup') / path.lstrip('/')
def cg_snapshot(path=None):
    p = cg_path() if path is None else Path(path)
    inode=p.stat()
    values = {}
    for name in ('pids.current','pids.max','pids.events','memory.current','memory.peak',
                 'memory.max','memory.swap.max','memory.events','memory.oom.group','cgroup.events','cgroup.procs','cgroup.threads'):
        f = p/name
        values[name] = f.read_text().strip() if f.exists() else None
    return {'path':str(p),'filesystem_identity':{'device':inode.st_dev,'inode':inode.st_ino,'ctime_ns':inode.st_ctime_ns},
            'values':values,'sample':stamp(),'metric':'cgroup charged memory; distinct from RSS'}
def mapping_snapshot():
    special=[]; flags=[]; ordinary_rss=0; current=None
    for line in Path('/proc/self/smaps').read_text().splitlines():
        if line and '-' in line.split()[0] and ':' not in line.split()[0]:
            parts=line.split(maxsplit=5); current=parts[5] if len(parts)>5 else ''
        elif line.startswith('Rss:'):
            n=int(line.split()[1])*1024
            if current in ('[vdso]','[vvar]','[vvar_vclock]','[vsyscall]'):
                special.append({'mapping':current,'rss_bytes':n})
            else: ordinary_rss+=n
        elif line.startswith('VmFlags:'):
            bad=set(line.split()[1:]) & {'io','pf','ht'}
            if bad and current not in ('[vdso]','[vvar]','[vvar_vclock]','[vsyscall]'):
                flags.append({'mapping':current,'flags':sorted(bad)})
    return {'ordinary_rss_snapshot':ordinary_rss,'kernel_specials':special,
            'unreviewed_special_flags':flags,'scope':'snapshot, not an instantaneous tree peak certificate'}
def proc_memory():
    before=stamp(); s=_status()
    return {'vm_size':int(s['VmSize'].split()[0])*1024,'rss_async':int(s['VmRSS'].split()[0])*1024,
            'rss_high_water_async':int(s['VmHWM'].split()[0])*1024,
            'rlimit_as':list(resource.getrlimit(resource.RLIMIT_AS)),
            'identity':identity(),'query_before':before,'query_after':stamp()}
def manifest():
    m=trusted(SOURCE.parent/'inputs/static_manifest.json')
    if str(SOURCE)!='/var/lib/dcl-r6/cr01/src' or str(SOURCE)!=m['source_directory']:
        raise AdmissionBlocked('UNTRUSTED_SOURCE_DIRECTORY')
    if sys.platform != 'linux' or tuple(sys.version_info[:3]) != (3,12,3):
        raise AdmissionBlocked('RUNTIME_VERSION_DRIFT')
    if str(Path(sys.executable).resolve()) != PYTHON or digest(PYTHON) != PYTHON_SHA:
        raise AdmissionBlocked('RUNTIME_HASH_DRIFT')
    if os.uname().release != m['kernel'] or os.uname().machine != m['architecture']:
        raise AdmissionBlocked('KERNEL_OR_ARCHITECTURE_DRIFT')
    if not(sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode):
        raise AdmissionBlocked('ISOLATED_FLAGS_REQUIRED')
    for filename, expected in m['source_hashes'].items():
        if digest(SOURCE/filename) != expected: raise AdmissionBlocked('SOURCE_DRIFT:'+filename)
    for filename, expected in m['runtime_files'].items():
        if digest(filename) != expected: raise AdmissionBlocked('RUNTIME_CLOSURE_DRIFT:'+filename)
    return m
def verify_runtime_tree(m):
    p=SOURCE.parent/'inputs/runtime_tree_lock.json'
    if digest(p)!=m['runtime_tree_lock_sha256']: raise AdmissionBlocked('RUNTIME_TREE_LOCK_DRIFT')
    lock=trusted(p)
    for filename,row in lock['files'].items():
        if digest(filename)!=row['sha256']: raise AdmissionBlocked('STDLIB_TREE_DRIFT:'+filename)
def authorization():
    _check_root(); m=manifest()
    a=trusted(ROOT/'inputs/execution_authorization.json')
    if ROOT.name != 'batch08' or a['batch_id'] != 'batch08' or a['scope'] not in ('CALIBRATE_S1S9_THEN_F1_F4','C00_DIAGNOSTIC_ONLY'):
        raise AdmissionBlocked('NO_DYNAMIC_BATCH08_AUTHORIZATION')
    if a['profile'] != 'CPY312-UBU24/1' or a['limits'] != [1000000,1800,1740,AS_CAP,4]:
        raise AdmissionBlocked('CONTRACT_MISMATCH')
    if a['static_manifest_sha256'] != digest(SOURCE.parent/'inputs/static_manifest.json'):
        raise AdmissionBlocked('STATIC_LOCK_MISMATCH')
    validate_execution_binding(a['execution_lock_sha256'],digest(SOURCE.parent/'inputs/execution_lock.json'))
    if a.get('safety_contract_sha256')!=m['safety_contract_sha256'] or a.get('test_mode')!='RANGE_ONLY/1':
        raise AdmissionBlocked('SAFETY_TEST_SCOPE_MISSING')
    if a.get('c09_contract_sha256')!=m['c09_contract_sha256'] or a.get('handoff_profile')!='C09-DURABLE-RPC/1':
        raise AdmissionBlocked('C09_HANDOFF_SCOPE_MISSING')
    if (a.get('root_ipc_contract_sha256')!=m.get('root_ipc_contract_sha256') or
        a.get('root_ipc_profile')!='ROOT-IPC/1' or (a['scope']!='C00_DIAGNOSTIC_ONLY' and a.get('RootIPC_helpers_explicitly_approved') is not True)):
        raise AdmissionBlocked('ROOT_IPC_SCOPE_MISSING')
    if (a.get('boot_continuity_profile')!='BC-SINGLE-SESSION/1' or
        a.get('boot_contract_sha256')!=m.get('boot_contract_sha256') or a.get('source_mode')!='SOURCE_ONLY/1' or
        a.get('SingleSession_exec_explicitly_approved') is not True or (a['scope']!='C00_DIAGNOSTIC_ONLY' and a.get('SameProcess_C09_resume_explicitly_approved') is not True)):
        raise AdmissionBlocked('BOOT_CONTINUITY_SCOPE_MISSING')
    if (a.get('readiness_profile')!='C00-READY/1' or a.get('readiness_contract_sha256')!=m.get('readiness_contract_sha256')):
        raise AdmissionBlocked('READINESS_SCOPE_MISSING')
    if a['scope']=='C00_DIAGNOSTIC_ONLY' and a.get('C00_diagnostic_explicitly_approved') is not True:
        raise AdmissionBlocked('C00_DIAGNOSTIC_NOT_APPROVED')
    if a['scope']=='CALIBRATE_S1S9_THEN_F1_F4' and a.get('Full_conditional_chain_explicitly_approved') is not True:
        raise AdmissionBlocked('FULL_CHAIN_NOT_APPROVED')
    if a['authorization_text_sha256'] != digest(ROOT/'inputs/BATCH08_AUTHORIZATION_TEXT.txt'):
        raise AdmissionBlocked('AUTHORIZATION_SOURCE_MISMATCH')
    # This is explicit scope acceptance, never a substitute for OS limit checks.
    if a.get('special_mapping_scope') != 'ORDINARY_AS_ACCOUNTED;KERNEL_SPECIALS_SEPARATELY_REVIEWED':
        raise AdmissionBlocked('SPECIAL_MAPPING_SCOPE_UNAPPROVED')
    return a,m
def validate_state_document(s):
    if stopped(): raise AdmissionBlocked('BATCH_STOPPED')
    if s['boot_id'] != boot_id(): raise AdmissionBlocked('BOOT_ID_MISMATCH')
    if now() >= s['deadline']: raise LimitReached('ABSOLUTE_WALL_LIMIT')
    if s['status'] not in ('CALIBRATING','FORMAL','AWAIT_EXPECTED_RESUME'):
        raise AdmissionBlocked('BATCH_CLOSED')
    return s
def state(): return validate_state_document(trusted(ROOT/'inputs/batch_state.json'))
def stopped(): return (ROOT/'inputs/CLOSED.json').exists() or (OUT/'STOP_REQUEST.json').exists()
def kernel_admission(ticket):
    a,m=authorization(); s=state(); status=_status()
    if stopped(): raise AdmissionBlocked('STOP_REQUESTED')
    if os.getuid()!=m['uid'] or os.geteuid()!=m['uid'] or os.getgid()!=m['gid']:
        raise AdmissionBlocked('PAYLOAD_IDENTITY_MISMATCH')
    if set(map(int,status['Uid'].split()))!={m['uid']} or set(map(int,status['Gid'].split()))!={m['gid']}:
        raise AdmissionBlocked('SAVED_OR_FILESYSTEM_IDENTITY_MISMATCH')
    if int(status['CapEff'].strip(),16) or int(status['NoNewPrivs']) != 1:
        raise AdmissionBlocked('PRIVILEGE_BOUNDARY_MISSING')
    if set(map(int,status['Groups'].split()))!={m['gid']}:
        raise AdmissionBlocked('SUPPLEMENTARY_GROUP_DRIFT')
    if resource.getrlimit(resource.RLIMIT_AS) != (AS_CAP,AS_CAP):
        raise AdmissionBlocked('ACTUAL_AS_LIMIT_MISMATCH')
    cg=cg_path(); parent=Path('/sys/fs/cgroup')/PARENT
    if cg != parent/ticket['unit'] or _number((parent/'pids.max').read_text()) != 4:
        raise AdmissionBlocked('ACTUAL_PARENT_MEMBERSHIP_OR_PIDS_MISMATCH')
    if _number((cg/'pids.max').read_text()) != 4: raise AdmissionBlocked('CHILD_PIDS_MISMATCH')
    if _number((parent/'memory.max').read_text())!=4*AS_CAP or _number((cg/'memory.max').read_text())!=4*AS_CAP:
        raise AdmissionBlocked('SECONDARY_CHARGED_LIMIT_MISMATCH')
    if _number((cg/'memory.swap.max').read_text())!=0 or (cg/'memory.oom.group').read_text().strip()!='1':
        raise AdmissionBlocked('SWAP_OR_OOM_POLICY_MISMATCH')
    if int((parent/'pids.current').read_text()) > 4: raise AdmissionBlocked('TASK_CAP_VIOLATION')
    if os.access(parent/'cgroup.procs',os.W_OK) or os.access(parent/'pids.max',os.W_OK):
        raise AdmissionBlocked('PAYLOAD_CAN_MANAGE_GROUP')
    if ticket['boot_id'] != s['boot_id'] or ticket['source_manifest'] != digest(SOURCE.parent/'inputs/static_manifest.json'):
        raise AdmissionBlocked('TICKET_BINDING_MISMATCH')
    if now() >= min(s['stop_at'],ticket['case_deadline']): raise LimitReached('LOCAL_OR_GLOBAL_DEADLINE')
    return {'process':proc_memory(),'cgroup':cg_snapshot(),'parent':cg_snapshot(parent),'sample':stamp()}
def ticket(case): return trusted(ROOT/('inputs/ticket_'+case+'.json'))
def guardian_check():
    if _WATCH is None or _WATCH.poll() is not None: raise AdmissionBlocked('WATCHDOG_NOT_ALIVE')
def validate_execution_binding(observed,expected):
    if observed!=expected:raise AdmissionBlocked('EXECUTION_LOCK_BINDING_MISMATCH')
def require_fresh_initialization(state_exists,counter_exists,closed_exists):
    if state_exists or counter_exists or closed_exists:raise AdmissionBlocked('BATCH_ALREADY_INITIALIZED')
def safety_binding():
    s=state()
    return {'batch_id':ROOT.name,'boot_id':s['boot_id'],'T0':s['T0'],
            'static_manifest_sha256':digest(SOURCE.parent/'inputs/static_manifest.json'),
            'execution_lock_sha256':digest(SOURCE.parent/'inputs/execution_lock.json'),
            'fixture_contract_sha256':digest(SOURCE.parent/'inputs/safety_contract.json'),
            'child_contracts_sha256':digest(SOURCE.parent/'inputs/child_contracts.json')}
def c09_contract():
    a,m=authorization();p=SOURCE.parent/'inputs/c09_contract.json'
    if digest(p)!=m['c09_contract_sha256']:raise AdmissionBlocked('C09_CONTRACT_HASH')
    cfg=trusted(p)
    if cfg['schema']!='C09-HANDOFF-CONTRACT/1' or cfg['version']!='C09Fix-static-1' or cfg['future_batch_id']!=ROOT.name:
        raise AdmissionBlocked('C09_CONTRACT_BINDING')
    return cfg
def c09h_charge(budget=None):
    t=_TICKET
    if t is None or t['case']!='C09H':raise AdmissionBlocked('C09H_CONTEXT_REQUIRED')
    execution_deadline('C09H')
    if count()>=t['c09h_visit_ceiling']:raise LimitReached('C09H_VISIT_LIMIT')
    if budget is None:
        if os.geteuid()!=0:raise AdmissionBlocked('ROOT_C09H_AUDIT_REQUIRED')
        reserve_counter(OUT/'visits.bin',VISIT_CAP)
    else:budget.visit()
def root_verify_c09h():
    global _TICKET
    if os.geteuid()!=0:raise AdmissionBlocked('ROOT_C09H_VERIFIER_REQUIRED')
    sys.path.insert(0,str(SOURCE))
    import c09_oracle
    old=_TICKET;_TICKET=ticket('C09H')
    try:
        cfg=c09_contract()
        for job in cfg['jobs']:c09h_charge()
        report=c09_oracle.check_suite(OUT/'c09_tests',cfg,safety_binding())
        if not report['accepted']:raise AdmissionBlocked('C09H_RAW_ORACLE_FAILED')
        report['checker_sha256']=digest(SOURCE/'c09_oracle.py')
        report['contract_sha256']=digest(SOURCE.parent/'inputs/c09_contract.json')
        _root_write(ROOT/'inputs/C09H_QUALIFICATION.json',report)
        return report
    finally:_TICKET=old
def safety_mode():
    a,m=authorization();s=state();t=_TICKET
    if t is None or t['case']!='RANGE' or s['status']!='CALIBRATING':
        raise AdmissionBlocked('CALIBRATION_RANGE_MODE_ONLY')
    if t['execution_lock_sha256']!=digest(SOURCE.parent/'inputs/execution_lock.json'):
        raise AdmissionBlocked('SAFETY_EXECUTION_LOCK_DRIFT')
    p=SOURCE.parent/'inputs/safety_contract.json'
    if digest(p)!=m['safety_contract_sha256']:raise AdmissionBlocked('SAFETY_CONTRACT_DRIFT')
    cfg=trusted(p)
    if cfg['schema']!='GC-SAFETY-CONTRACT/1' or cfg['version']!='BF-static-2' or cfg['future_batch_id']!=ROOT.name:
        raise AdmissionBlocked('SAFETY_CONTRACT_IDENTITY')
    if cfg['global_safety_charge_cap']!=20000 or cfg['max_jobs']!=34 or len(cfg['jobs'])!=34:
        raise AdmissionBlocked('SAFETY_RESOURCE_CONTRACT')
    execution_deadline('RANGE')
    return cfg
def safety_charge():
    t=_TICKET
    if t is None or t['case']!='RANGE':raise AdmissionBlocked('SAFETY_CHARGE_CONTEXT')
    execution_deadline('RANGE')
    if os.geteuid()==0:
        if not _ROOT_SAFETY_AUDIT:raise AdmissionBlocked('ROOT_SAFETY_AUDIT_CONTEXT')
    elif identity()!=t['main_identity']:
        if identity(os.getppid())!=t['main_identity']:raise AdmissionBlocked('SAFETY_CHARGE_PARENT')
    else:guardian_check()
    reserve_counter(OUT/'visits.bin',VISIT_CAP)
def safety_worker_argv(case_id):
    cfg=safety_mode()
    if case_id not in {j['case_id'] for j in cfg['jobs']}:raise AdmissionBlocked('UNFROZEN_SAFETY_WORKER')
    argv=[PYTHON,'-I','-S','-B',str(SOURCE/'range_fixtures.py'),'--batch-root',str(ROOT),'--case-id',case_id]
    lock=trusted(SOURCE.parent/'inputs/execution_lock.json')
    if argv!=lock['safety_worker_commands'][case_id]:raise AdmissionBlocked('SAFETY_WORKER_ARGV_DRIFT')
    return argv
def verify_sealed_safety(receipt,binding):
    import range_evidence
    if receipt.get('schema')!='GC-RANGE-QUALIFICATION/1' or receipt.get('binding')!=binding:
        raise AdmissionBlocked('RANGE_RECEIPT_BINDING')
    cfg=trusted(SOURCE.parent/'inputs/safety_contract.json')
    rows=receipt['results']
    expected={j['case_id']:j for j in cfg['jobs']}
    if len(rows)!=34 or {r['case_id'] for r in rows}!=set(expected):
        raise AdmissionBlocked('RANGE_RECEIPT_JOB_SET')
    if receipt['checker_sha256']!=digest(SOURCE/'range_evidence.py'):
        raise AdmissionBlocked('RANGE_CHECKER_DRIFT')
    for row in rows:
        job=expected[row['case_id']]
        target='PASS' if job['variant']=='safe' else 'MUTATION_DETECTED'
        if row.get('status')!=target or row.get('accepted') is not True or row.get('binding')!=binding:
            raise AdmissionBlocked('RANGE_REQUIRED_RESULT_'+row['case_id'])
        if not row.get('raw_files'):raise AdmissionBlocked('RANGE_RAW_EVIDENCE_MISSING')
        base=OUT/'safety'/row['case_id']
        _inside(base,OUT)
        if (OUT/'safety').is_symlink() or base.is_symlink():
            raise AdmissionBlocked('SYMLINK_RANGE_EVIDENCE')
        for rel,expected_sha in row['raw_files'].items():
            p=_inside(base/rel,base)
            if p.is_symlink() or hashlib.sha256(range_evidence.bounded(p,4194304)).hexdigest()!=expected_sha:
                raise AdmissionBlocked('RANGE_RAW_HASH_MISMATCH')
def exercise_gate_negatives(report,binding,cfg):
    if os.geteuid()!=0 or not _ROOT_SAFETY_AUDIT:raise AdmissionBlocked('ROOT_GATE_AUDIT_REQUIRED')
    safety_charge()
    verify_sealed_safety(report,binding)
    results=[]
    for spec in cfg['gate_negative_cases']:
        safety_charge()
        candidate=json.loads(json.dumps(report));recipe=spec['recipe']
        row=candidate['results'][0]
        if recipe=='status':row['status']=spec['value'];row['accepted']=True
        elif recipe=='missing_job':candidate['results'].pop()
        elif recipe=='missing_raw':row['raw_files']={}
        elif recipe=='raw_hash':
            key=next(iter(row['raw_files']));row['raw_files'][key]='0'*64
        elif recipe=='binding':
            key=spec['value']
            candidate['binding'][key]=candidate['binding'][key]+1 if key=='T0' else 'invalid-frozen-gate-binding'
        elif recipe=='checker_hash':candidate['checker_sha256']='0'*64
        elif recipe=='forged_PASS':
            row['status']='PASS';row['accepted']=True;row['raw_files']={}
        else:raise AdmissionBlocked('UNFROZEN_GATE_NEGATIVE_RECIPE')
        before=stamp();rejected=None
        try:verify_sealed_safety(candidate,binding)
        except (AdmissionBlocked,OSError,ValueError,KeyError,TypeError) as exc:rejected=str(exc)
        if rejected is None or not rejected.startswith(spec['expected_prefix']):
            raise AdmissionBlocked('GATE_MUTATION_NOT_DETECTED:'+spec['case_id'])
        results.append({'case_id':spec['case_id'],'projection_sha256':hashlib.sha256(
            json.dumps(candidate,sort_keys=True).encode()).hexdigest(),'rejected_by':rejected,
            'before':before,'after':stamp(),'status':'MUTATION_DETECTED'})
    return {'binding':binding,'positive_control':'PASS','results':results,'verifier':identity(),'sample':stamp()}
def verify_gate_audit(receipt,binding):
    cfg=trusted(SOURCE.parent/'inputs/safety_contract.json')
    p=ROOT/'inputs/GATE_NEGATIVE_AUDIT.json'
    if digest(p)!=receipt['gate_audit_sha256']:raise AdmissionBlocked('GATE_AUDIT_HASH_MISMATCH')
    audit=trusted(p)
    if audit['binding']!=binding or audit['positive_control']!='PASS':
        raise AdmissionBlocked('GATE_AUDIT_BINDING')
    expected={s['case_id']:s for s in cfg['gate_negative_cases']}
    rows=audit['results']
    if len(rows)!=len(expected) or {x['case_id'] for x in rows}!=set(expected):
        raise AdmissionBlocked('GATE_AUDIT_SET')
    for row in rows:
        if row['status']!='MUTATION_DETECTED' or not row['rejected_by'].startswith(expected[row['case_id']]['expected_prefix']):
            raise AdmissionBlocked('GATE_AUDIT_REQUIRED_REJECTION')
def root_verify_safety():
    global _TICKET,_ROOT_SAFETY_AUDIT
    if os.geteuid()!=0:raise AdmissionBlocked('ROOT_SAFETY_VERIFIER_REQUIRED')
    sys.path.insert(0,str(SOURCE))
    import range_evidence
    old=_TICKET
    _TICKET=ticket('RANGE');_ROOT_SAFETY_AUDIT=True
    try:
        cfg=safety_mode();binding=safety_binding()
        execution_deadline('RANGE')
        for job in cfg['jobs']:safety_charge()
        report=range_evidence.check_suite(OUT/'safety',cfg,binding)
        if not report['accepted']:raise AdmissionBlocked('RANGE_RAW_VERIFICATION_FAILED')
        health=range_evidence.check_global_ledger(OUT/'visits.bin',VISIT_CAP,binding)
        if not(health['used']<100000 and health['used']<VISIT_CAP):
            raise LimitReached('CALIBRATION_VISIT_ADMISSION')
        execution_deadline('RANGE')
        report.update({'schema':'GC-RANGE-QUALIFICATION/1','checker_sha256':digest(SOURCE/'range_evidence.py'),
                       'global_health':health,'sample':stamp()})
        verify_sealed_safety(report,binding)
        gate_audit=exercise_gate_negatives(report,binding,cfg)
        _root_write(ROOT/'inputs/GATE_NEGATIVE_AUDIT.json',gate_audit)
        report['gate_audit_sha256']=digest(ROOT/'inputs/GATE_NEGATIVE_AUDIT.json')
        # The audit consumed the same global calibration budget; recheck it now.
        report['global_health']=range_evidence.check_global_ledger(OUT/'visits.bin',VISIT_CAP,binding)
        execution_deadline('RANGE')
        verify_gate_audit(report,binding)
        _root_write(ROOT/'inputs/RANGE_QUALIFICATION.json',report)
        return report
    finally:_TICKET=old;_ROOT_SAFETY_AUDIT=False
def require_formal_admission():
    if _TICKET is None or _TICKET['case'] != 'FORMAL' or _TICKET['main_identity'] != identity():
        raise AdmissionBlocked('CONTROLLER_CONTEXT_REQUIRED')
    kernel_admission(_TICKET); guardian_check()
    a,_=authorization()
    if a['scope']!='CALIBRATE_S1S9_THEN_F1_F4':raise AdmissionBlocked('FORMAL_SCOPE_NOT_AUTHORIZED')
    q=trusted(ROOT/'inputs/RESOURCE_QUALIFICATION.json')
    if q['boot_id']!=boot_id() or q['source_manifest']!=digest(SOURCE.parent/'inputs/static_manifest.json'):
        raise AdmissionBlocked('QUALIFICATION_BINDING_MISMATCH')
    if set(q['cases'])!=set(CASES): raise AdmissionBlocked('INCOMPLETE_CALIBRATION')
    for c,h in q['cases'].items():
        p=ROOT/('inputs/result_'+c+'.json'); r=trusted(p)
        if digest(p)!=h or r['status']!='PASS' or r['case']!=c:
            raise AdmissionBlocked('CALIBRATION_EVIDENCE_MISMATCH')
    binding=safety_binding()
    if q.get('binding')!=binding:raise AdmissionBlocked('RESOURCE_QUALIFICATION_BINDING')
    rp=ROOT/'inputs/RANGE_QUALIFICATION.json'
    if digest(rp)!=q['safety_receipt_sha256']:raise AdmissionBlocked('RANGE_RECEIPT_DRIFT')
    receipt=trusted(rp)
    verify_sealed_safety(receipt,binding)
    verify_gate_audit(receipt,binding)
    import c09_handoff
    c09_handoff.verify_completed_handoff(sys.modules[__name__])
    # Fresh raw global-ledger admission occurs before any F1/F4 business import.
    reserve_counter(OUT/'visits.bin',VISIT_CAP)
    import range_evidence
    range_evidence.check_global_ledger(OUT/'visits.bin',VISIT_CAP,binding)
def request_stop(reason):
    write(OUT/'STOP_REQUEST.json',{'reason':reason,**stamp()})
def init_counter(path,cap):
    p=_inside(path,OUT)
    if p==OUT/'visits.bin' and os.geteuid()!=0: raise AdmissionBlocked('ROOT_INITIALIZATION_REQUIRED')
    p.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    try: _full(fd,COUNTER_MAGIC+struct.pack('<QQ',0,cap)); sync_fd(fd,'budget.initialize')
    finally: os.close(fd)
    if os.geteuid()==0:
        u=pwd.getpwnam('dcl-r6'); os.chown(p,u.pw_uid,u.pw_gid)
    atomic(p.with_suffix(p.suffix+'.intent.json'),{'protocol':BUDGET_PROTOCOL,'status':'COMMITTED','after':0,'cap':cap},timing_stage='budget.initialize.intent')
    if os.geteuid()==0:
        os.chown(p.with_suffix(p.suffix+'.intent.json'),u.pw_uid,u.pw_gid)
def count(path=None):
    p=OUT/'visits.bin' if path is None else _inside(path,OUT)
    with p.open('rb') as f:
        raw=f.read()
    if len(raw)!=24 or raw[:8]!=COUNTER_MAGIC: raise AdmissionBlocked('COUNTER_FORMAT_OR_PROTOCOL')
    used,cap=struct.unpack('<QQ',raw[8:])
    if used>cap: raise AdmissionBlocked('COUNTER_OVERFLOW')
    return used
@contextmanager
def _counter_lock(path,cap,case=None):
    budget_health();p=_inside(path,OUT)
    with _LOCKS_LOCK:lock=_LOCKS.setdefault(str(p),threading.RLock())
    begin=monotonic_ns();utc=time.time_ns()
    while not lock.acquire(timeout=.05):execution_deadline(case)
    fd=None;acquired=False
    try:
        fd=os.open(p,os.O_RDWR|os.O_NOFOLLOW)
        while not acquired:
            try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);acquired=True
            except BlockingIOError:execution_deadline(case);time.sleep(.005)
        _timing('budget.lock_wait',begin,monotonic_ns(),utc,time.time_ns())
        execution_deadline(case)
        raw=os.pread(fd,24,0)
        if len(raw)!=24 or raw[:8]!=COUNTER_MAGIC:raise AdmissionBlocked('TORN_COUNTER_OR_OLD_PROTOCOL')
        used,storedcap=struct.unpack('<QQ',raw[8:])
        if list(p.parent.glob(p.name+'.intent.json.tmp.*')):
            raise AdmissionBlocked('AMBIGUOUS_RESERVATION_TEMP')
        old=read(p.with_suffix(p.suffix+'.intent.json'))
        if storedcap!=cap or used>cap:raise AdmissionBlocked('COUNTER_CAP_MISMATCH')
        if old.get('protocol')!=BUDGET_PROTOCOL or old.get('status')!='COMMITTED' or old['after']!=used or old['cap']!=cap:
            raise AdmissionBlocked('AMBIGUOUS_RESERVATION')
        yield fd,used,p
    finally:
        if fd is not None:
            if acquired:fcntl.flock(fd,fcntl.LOCK_UN)
            os.close(fd)
        lock.release()

def _canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'))
def _task_contract(task_id,N):
    if type(N) is not int or N<=0:raise AdmissionBlocked('EXACT_N_MUST_BE_POSITIVE_INTEGER')
    m=manifest();p=SOURCE.parent/'inputs/child_contracts.json'
    if digest(p)!=m['child_contracts_sha256']:raise AdmissionBlocked('CHILD_CONTRACT_DRIFT')
    tasks=trusted(p)['tasks']
    if task_id not in tasks:raise AdmissionBlocked('UNFROZEN_SUBTASK')
    spec=tasks[task_id];s=state();t=ticket(spec['case'])
    page=os.sysconf('SC_PAGE_SIZE')
    if page!=4096 or spec['page_size']!=page:raise AdmissionBlocked('UNPROVEN_CHILD_PAGE_SIZE')
    expected={'C02':128*(1+1048576//page),'C03':16777216//page,'C04':1}[spec['case']]
    if N!=expected or spec['N']!=expected:raise AdmissionBlocked('UNPROVEN_EXACT_N')
    request={'protocol':BUDGET_PROTOCOL,'batch_id':ROOT.name,'boot_id':s['boot_id'],'T0':s['T0'],
             'task_id':task_id,'N':N,'case':spec['case'],'source_manifest':digest(SOURCE.parent/'inputs/static_manifest.json'),
             'contract_sha256':digest(p)}
    return request,t
def _fact_path(task_id):
    return OUT/'reservations'/(hashlib.sha256(task_id.encode()).hexdigest()+'.json')
def _validate_fact(fact,request,used):
    if fact.get('request')!=request:raise AdmissionBlocked('TASK_ID_REQUEST_CONFLICT')
    lo,hi=fact['credit_range']
    if type(lo) is not int or type(hi) is not int or not(0<=lo<hi<=used) or hi-lo!=request['N']:
        raise AdmissionBlocked('EXACT_FACT_RANGE_MISMATCH')
    material={'request':request,'credit_range':[lo,hi],'owner':fact['owner']}
    if fact['lease_id']!=hashlib.sha256(_canonical(material).encode()).hexdigest():
        raise AdmissionBlocked('EXACT_FACT_IDENTITY_MISMATCH')
    if fact['delivery_state'] not in ('UNCLAIMED','CLAIMED'):raise AdmissionBlocked('EXACT_FACT_DELIVERY_STATE')
def _append_journal(p,record,stage):
    data=timed(stage+'.encode',lambda:(_canonical(record)+'\n').encode())
    j=os.open(p.with_suffix(p.suffix+'.journal.jsonl'),os.O_WRONLY|os.O_CREAT|os.O_APPEND|os.O_NOFOLLOW,0o600)
    try:timed(stage+'.write',_full,j,data);sync_fd(j,stage)
    finally:os.close(j)
def _reserve(path,cap,amount=1,request=None,fault=None):
    budget_health();timing_event('reserve.request')
    if request is not None:raise AdmissionBlocked('EXACT_RANGE_CORE_REQUIRED')
    if type(amount) is not int or amount<=0:raise AdmissionBlocked('RESERVATION_AMOUNT')
    p=_inside(path,OUT);global_ledger=p==OUT/'visits.bin'
    if fault and global_ledger:raise AdmissionBlocked('FAULT_IN_GLOBAL_LEDGER_FORBIDDEN')
    if fault:
        allowed=('prepared','short_write','counter_fsynced','journal_fsynced')
        if (_TICKET is None or _TICKET['case']!='C11' or fault not in allowed or
            p!=OUT/('C11.'+fault+'.bin')):
            raise AdmissionBlocked('CALIBRATION_C11_FAULT_MODE_ONLY')
    if amount!=1 and request is None:raise AdmissionBlocked('RANGE_REQUIRES_FROZEN_TASK')
    case=request['case'] if request else None
    try:
        with _counter_lock(p,cap,case) as (fd,used,p):
            if request is not None:
                checked,t=_task_contract(request['task_id'],amount)
                if checked!=request:raise AdmissionBlocked('REQUEST_BINDING_CHANGED')
                if _TICKET is None or _TICKET['case']!=case or t['main_identity']!=identity():
                    raise AdmissionBlocked('EXACT_RESERVATION_OWNER_REQUIRED')
                fp=_fact_path(request['task_id'])
                if fp.exists():
                    fact=read(fp);_validate_fact(fact,request,used)
                    timing_event('reserve.idempotent_fact_only')
                    return {'after':used,'fact':fact,'created':False}
            soft=100000 if global_ledger and (_TICKET is None or _TICKET['case']!='FORMAL') else cap
            if global_ledger and _TICKET is not None and _TICKET['case']=='RANGE':
                soft=min(soft,_TICKET['safety_visit_ceiling'])
            if used+amount>min(cap,soft):raise LimitReached('VISIT_OR_CALIBRATION_LIMIT')
            record={'protocol':BUDGET_PROTOCOL,'status':'PREPARED','before':used,'after':used+amount,
                    'amount':amount,'cap':cap,'request':request,**stamp()}
            intent=p.with_suffix(p.suffix+'.intent.json')
            atomic(intent,record,timing_stage='budget.intent.prepared')
            if fault=='prepared':raise OSError('INJECTED_AFTER_PREPARED')
            _append_journal(p,record,'budget.journal.prepared')
            payload=struct.pack('<Q',used+amount)
            if fault=='short_write':payload=payload[:3]
            written=timed('budget.counter.write',os.pwrite,fd,payload,8)
            if written!=8:raise AdmissionBlocked('SHORT_COUNTER_WRITE')
            sync_fd(fd,'budget.counter')
            if fault=='counter_fsynced':raise OSError('INJECTED_AFTER_COUNTER_FSYNC')
            record={**record,'status':'COMMITTED',**stamp()}
            _append_journal(p,record,'budget.journal.committed')
            if fault=='journal_fsynced':raise OSError('INJECTED_BEFORE_COMMITTED_INTENT')
            fact=None
            if request is not None:
                fact={'protocol':BUDGET_PROTOCOL,'request':request,'credit_range':[used,used+amount],
                      'owner':identity(),'delivery_state':'UNCLAIMED','executor':None,'reserved_at':stamp()}
                material={'request':request,'credit_range':fact['credit_range'],'owner':fact['owner']}
                fact['lease_id']=hashlib.sha256(_canonical(material).encode()).hexdigest()
                # Registry is durable before the global intent becomes ready.
                # A crash in this gap leaves PREPARED and closes the batch.
                atomic(fp,fact,timing_stage='budget.registry.reserved')
            atomic(intent,record,timing_stage='budget.intent.committed')
            timing_event('reserve.committed_barriers_done')
            execution_deadline(case)  # committed late credit is burned, never handed off
            return {'after':used+amount,'fact':fact,'created':True}
    except LimitReached:raise
    except BaseException as exc:
        if global_ledger:halt_budget(exc)
        raise
def reserve_counter(path,cap,fault=None):
    return _reserve(path,cap,1,fault=fault)['after']

def claim_exact(task_id,N,lease_id):
    import range_core
    request,_=_task_contract(task_id,N)
    return range_core.Store(sys.modules[__name__],OUT/'visits.bin',VISIT_CAP,request).claim(lease_id)
class Budget:
    def __init__(self,local=None):
        if _TICKET is None: raise AdmissionBlocked('PAYLOAD_CONTEXT_REQUIRED')
        kernel_admission(_TICKET); guardian_check()
        self.local=Path(local) if local else None; self.calls=0
    def visit(self):
        guardian_check();execution_deadline()
        try:
            reserve_counter(OUT/'visits.bin',VISIT_CAP); self.calls+=1
            if self.local:reserve_counter(self.local,17)
            execution_deadline();timing_event('single_credit.grant_emit')
        except LimitReached:raise
        except BaseException as exc:halt_budget(exc);raise
    def reserve_exact(self,task_id,N):
        if self.local:raise AdmissionBlocked('LOCAL_MIRROR_EXACT_RESERVATION_NOT_APPROVED')
        guardian_check();execution_deadline()
        request,_=_task_contract(task_id,N)
        import range_core
        return range_core.Store(sys.modules[__name__],OUT/'visits.bin',VISIT_CAP,request).reserve()
    def close(self): pass

def _run(argv,timeout=15):
    r=subprocess.run(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout,check=False)
    if r.returncode: raise AdmissionBlocked('MANAGER_COMMAND_FAILED:'+repr(argv)+':'+r.stderr.decode(errors='replace'))
    return r.stdout.decode()
def unit_show(unit):
    fields=('MainPID','ControlGroup','ActiveState','SubState','Result','ExecMainStatus',
            'User','Group','LimitAS','LimitASSoft','TasksMax','KillMode','Restart','Delegate','NoNewPrivileges')
    text=_run(['/usr/bin/systemctl','show',unit,*['--property='+f for f in fields]])
    return dict(line.split('=',1) for line in text.splitlines() if '=' in line)
def service_argv(case):
    unit='dclr6batch08-'+case.lower()+'.service'
    props={'User':'dcl-r6','Group':'dcl-r6','Type':'exec','Slice':PARENT,
           'LimitAS':str(AS_CAP)+':'+str(AS_CAP),'TasksMax':'4','TasksAccounting':'yes',
           'MemoryAccounting':'yes','MemoryMax':str(4*AS_CAP),'MemorySwapMax':'0',
           'OOMPolicy':'kill','OOMScoreAdjust':'0','LimitCORE':'0','Restart':'no',
           'Delegate':'no','NoNewPrivileges':'yes','KillMode':'control-group',
           'KillSignal':'SIGKILL','SendSIGKILL':'yes','TimeoutStartSec':'15','TimeoutStopSec':'5',
           'RuntimeMaxSec':'1740','CapabilityBoundingSet':'','AmbientCapabilities':'',
           'ProtectSystem':'strict','ProtectHome':'yes','ProtectControlGroups':'yes',
           'PrivateDevices':'yes','PrivateTmp':'yes','PrivateNetwork':'yes',
           'RestrictNamespaces':'yes','RestrictAddressFamilies':'AF_UNIX',
           'ReadWritePaths':str(OUT),'WorkingDirectory':str(ROOT),
           'UnsetEnvironment':'LD_PRELOAD LD_LIBRARY_PATH LD_AUDIT PYTHONPATH PYTHONHOME',
           'InaccessiblePaths':'/mnt /init /dev/hugepages /usr/lib/wsl /run/systemd/private /run/dbus /run/user'}
    return ['/usr/bin/systemd-run','--no-block','--unit='+unit,
            *['--property='+k+'='+v for k,v in props.items()],PYTHON,'-I','-S','-B',str(SOURCE/'guard.py'),
            '--role','controller','--batch-root',str(ROOT),'--case',case]
def _root_write(path,data): atomic(path,data,True)
def _empty():
    p=Path('/sys/fs/cgroup')/PARENT/'cgroup.events'
    return not p.exists() or 'populated 0' in p.read_text().splitlines()
def stop_tree(reason,close=True):
    parent=Path('/sys/fs/cgroup')/PARENT
    before=cg_snapshot(parent) if parent.exists() else None
    close_error=None
    if close:
        p=ROOT/'inputs/CLOSED.json'
        try:
            sys.path.insert(0,str(SOURCE))
            import c09_handoff as H
            with H.lifecycle_lock(sys.modules[__name__]):
                if p.exists():p=ROOT/('inputs/stop_event_%s_%s.json'%(os.getpid(),time.time_ns()))
                _root_write(p,{'reason':reason,**stamp()})
        except BaseException as exc:close_error=repr(exc)
    r=subprocess.run(['/usr/bin/systemctl','stop',PARENT],capture_output=True,timeout=15)
    until=now()+5
    while not _empty() and now()<until: time.sleep(.05)
    if not _empty(): raise AdmissionBlocked('STOP_UNCONFIRMED')
    result={'empty':True,'stop_exit':r.returncode,'closure_persistence_error':close_error,'before_stop_charged_snapshot':before,
            'peak_scope':'observed charge peak for this group generation; no exact RSS tree peak inferred',
            'after_stop_group_exists':parent.exists(),'sample':stamp()}
    _root_write(ROOT/('inputs/stop_result_%s_%s.json'%(os.getpid(),time.time_ns())),result)
    return result
def external_stop():
    if os.geteuid()!=0:raise AdmissionBlocked('TRUSTED_LAUNCHER_ONLY')
    authorization();s=state();monitored=None;fd=None
    sys.path.insert(0,str(SOURCE))
    import c09_handoff as H
    receiver=H.Receiver(sys.modules[__name__])
    _root_write(ROOT/'inputs/STOP_ARMED.json',{'identity':identity(),'stop_at':s['stop_at'],
        'boot_id':boot_id(),'handoff_profile':H.PROFILE,'socket':str(H.paths(sys.modules[__name__])['socket'])})
    try:
        while True:
            s=trusted(ROOT/'inputs/batch_state.json')
            if (ROOT/'inputs/CLOSED.json').exists():
                stop_tree('CLOSED_BATCH_CLEANUP',False);return 0
            if s['boot_id']!=boot_id() or now()>=s['stop_at'] or (OUT/'STOP_REQUEST.json').exists():
                stop_tree('ABSOLUTE_STOP_OR_REQUEST');return 124
            receiver.poll()
            # A coordinator is the direct kernel exit witness, independent of the sender.
            fresh=trusted(ROOT/'inputs/batch_state.json')
            coordinator=fresh.get('coordinator_identity')
            if coordinator and not H.alive(sys.modules[__name__],coordinator):
                stop_tree('LAUNCHER_COORDINATOR_LOST');return 125
            target=fresh.get('launcher_identity')
            if target and target!=monitored:
                if fd is not None:os.close(fd);fd=None
                if identity(target['pid'])!=target:raise AdmissionBlocked('LAUNCHER_IDENTITY_CHANGED')
                fd=os.pidfd_open(target['pid'])
                if identity(target['pid'])!=target:raise AdmissionBlocked('LAUNCHER_PIDFD_NOT_STABLE')
                monitored=target
            if fd is not None and select.select([fd],[],[],.05)[0]:
                verdict=receiver.observe_exit()  # lock + current state read after readiness
                if verdict=='VERIFIED':
                    os.close(fd);fd=None;monitored=None
                elif verdict=='CLOSED':
                    stop_tree('C09_CLOSED_DURING_CLASSIFICATION',False);return 125
            else:time.sleep(.02)
    except BaseException as exc:
        try:stop_tree('C09_OR_SUPERVISOR_FAILURE:'+str(exc))
        finally:raise
    finally:
        if fd is not None:os.close(fd)
        receiver.close()
def watchdog(case,parent,parent_start):
    t=ticket(case); kernel_admission(t)
    if identity(parent)['start_ticks']!=parent_start or t['main_identity']!=identity(parent):
        raise AdmissionBlocked('WATCHDOG_PARENT_MISMATCH')
    fd=os.pidfd_open(parent)
    print(json.dumps({'ready':True,'identity':identity()}),flush=True)
    while True:
        if (OUT/(case+'.normal_stop')).exists(): return 0
        limit=min(state()['stop_at'],t['case_deadline'])
        hb=OUT/(case+'.heartbeat.json')
        expired=now()>=limit
        stale=hb.exists() and now()-read(hb)['boottime']>3
        dead=bool(select.select([fd],[],[],.1)[0])
        if expired or stale or dead or stopped():
            write(OUT/(case+'.watchdog_stop.json'),{'expired':expired,'stale':stale,'parent_dead':dead,**stamp()})
            if not dead: signal.pidfd_send_signal(fd,signal.SIGKILL)
            return 124
def controller(case):
    global _TICKET,_WATCH
    if __name__=='__main__': sys.modules['guard']=sys.modules[__name__]
    until=now()+14
    path=ROOT/('inputs/ticket_'+case+'.json')
    while not path.exists() and now()<until: time.sleep(.02)
    t=ticket(case)
    if t['main_identity']!=identity(): raise AdmissionBlocked('MAIN_PID_TICKET_REQUIRED')
    _TICKET=t; startup=kernel_admission(t)
    sys.path.insert(0,str(SOURCE))
    err=(OUT/(case+'.watchdog.stderr')).open('xb')
    watchdog_argv=[PYTHON,'-I','-S','-B',str(SOURCE/'guard.py'),'--role','watchdog',
        '--batch-root',str(ROOT),'--case',case,'--parent',str(os.getpid()),'--parent-start',str(identity()['start_ticks'])]
    _WATCH=subprocess.Popen(watchdog_argv,
        stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=err,text=True)
    if not select.select([_WATCH.stdout],[],[],5)[0]: raise AdmissionBlocked('WATCHDOG_START_TIMEOUT')
    ready=json.loads(_WATCH.stdout.readline())
    if not ready.get('ready') or identity(_WATCH.pid)!=ready['identity']: raise AdmissionBlocked('WATCHDOG_HANDSHAKE')
    startup['watchdog_argv']=watchdog_argv;startup['watchdog_identity']=ready['identity']
    def monitor():
        while not _NORMAL.wait(.2):
            try:
                code=_WATCH.poll()
                if code is not None:
                    write(OUT/(case+'.monitor_failure.json'),{'reason':'WATCHDOG_EXIT','exit_code':code,**stamp()})
                    os._exit(125)
                write(OUT/(case+'.heartbeat.json'),stamp())
            except BaseException: os._exit(126)
    thread=threading.Thread(target=monitor,daemon=True);thread.start()
    try:
        startup['after_watchdog_group']=cg_snapshot()
        write(OUT/(case+'.startup.json'),startup)
        if case=='FORMAL':
            import service_readiness
            service_readiness.formal_gate(sys.modules[__name__])
            boot_continuity().formal_gate(sys.modules[__name__])
            require_formal_admission()
            sys.argv=[str(SOURCE/'run_batch.py'),'--batch-root',str(ROOT),'--session','1']
            runpy.run_path(str(SOURCE/'run_batch.py'),run_name='__main__')
            return 0
        if case=='RANGE':
            import range_fixtures
            result=range_fixtures.run_suite()
            write(OUT/'RANGE.probe.json',result)
            return 0 if result['status']=='PASS' else 65
        if case=='C09H':
            import c09_regression
            result=c09_regression.run_suite(sys.modules[__name__],Budget())
            write(OUT/'C09H.probe.json',result)
            return 0 if result['status']=='PASS' else 65
        import guard_probe
        result=guard_probe.run_case(case,Budget())
        write(OUT/(case+'.probe.json'),result)
        return 0 if result['status']=='PASS' else 65
    finally:
        _NORMAL.set();thread.join(1)
        (OUT/(case+'.normal_stop')).write_text('NORMAL_HANDSHAKE',encoding='ascii')
        try: _WATCH.wait(timeout=3)
        except subprocess.TimeoutExpired: _WATCH.kill();_WATCH.wait()
        err.close()
        write(OUT/(case+'.timing.json'),{'timing':timing_snapshot(),
            'scope':'bounded in-memory aggregates; this final write is outside the snapshot; abrupt exit may lose telemetry',
            'sample':stamp()})
def launch_one(case):
    root_checkpoint()
    argv=service_argv(case)
    lock=trusted(SOURCE.parent/'inputs/execution_lock.json')
    if argv!=lock['payload_commands'][case]: raise AdmissionBlocked('PAYLOAD_ARGV_DRIFT')
    activation_started=now()
    _run(argv)
    unit='dclr6batch08-'+case.lower()+'.service'; until=activation_started+14
    info={};ready_lease=None
    if case in ('C00','C10'):
        import service_readiness
        ready_lease=service_readiness.wait_native(sys.modules[__name__],case,unit,activation_started)
        pid=ready_lease.identity['pid'];info=ready_lease.info
    else:
        until=now()+14
        while now()<until:
            root_checkpoint()
            info=unit_show(unit); pid=int(info.get('MainPID','0'))
            if pid: break
            time.sleep(.02)
        else: raise AdmissionBlocked('NO_CONTROLLER_PID')
    s=state()
    limit=s['stop_at'] if case=='FORMAL' else min(s['stop_at'],s['T0']+300,now()+(2 if case=='C06' else 300))
    t={'case':case,'unit':unit,'main_identity':(ready_lease.identity if ready_lease else identity(pid)),'boot_id':boot_id(),
       'source_manifest':digest(SOURCE.parent/'inputs/static_manifest.json'),'case_deadline':limit,
       'unit_before_ticket':info,'argv':argv}
    t['execution_lock_sha256']=digest(SOURCE.parent/'inputs/execution_lock.json')
    if case=='RANGE':t['safety_visit_ceiling']=min(100000,count()+20000)
    if case=='C09H':t['c09h_visit_ceiling']=min(100000,count()+5000)
    try:
        boot_continuity().service_confirmed(sys.modules[__name__],t,ready_lease)
        if ready_lease:
            root_checkpoint()
            if now()>=ready_lease.until:raise LimitReached('READINESS_TICKET_LATE')
            ready_lease.ticket_admit(sys.modules[__name__],t)
            t['readiness_sha256']=digest(ROOT/('inputs/'+case+'_READINESS.json'))
        _root_write(ROOT/('inputs/ticket_'+case+'.json'),t)
    finally:
        if ready_lease:ready_lease.close()
    if case=='C09':
        import c09_handoff as H
        def c09_live():
            return H.alive(sys.modules[__name__],t['main_identity']) and H.alive(
                sys.modules[__name__],trusted(ROOT/'inputs/STOP_ARMED.json')['identity'])
        root_ipc().wait_ready(sys.modules[__name__],OUT/'C09.ready.json',limit,c09_live)
        root_checkpoint()
        H.sender_prepare(sys.modules[__name__],_COORDINATOR_ID)
        root_checkpoint()
        os._exit(23)  # one predeclared crash; resume retains T0/deadline/ledger
    while now()<limit+5:
        root_checkpoint()
        info=unit_show(unit)
        if info.get('ActiveState') in ('inactive','failed'): break
        time.sleep(.05)
    else:
        _run(['/usr/bin/systemctl','stop',unit]); raise LimitReached('CASE_DID_NOT_EXIT')
    g=Path('/sys/fs/cgroup')/PARENT/unit/'cgroup.events'
    if g.exists() and 'populated 1' in g.read_text(): raise AdmissionBlocked('CASE_DESCENDANTS_REMAIN')
    probe=OUT/(case+'.probe.json'); status='FAIL'; actual={'unit_after':info,'ticket':t}
    if probe.exists():
        payload=read(probe);actual['probe']=payload
        status='PASS' if payload.get('status')=='PASS' and info.get('ExecMainStatus')=='0' else 'FAIL'
        if case=='C08':
            if read(OUT/'C08.ready.json')['counter']!=count(): status='FAIL'
    elif case=='FORMAL':
        p=OUT/'reports/MODEL_SUMMARY.1.json'
        if p.exists():
            payload=read(p);actual['model_summary']=payload
            status='PASS' if payload.get('status')=='FINISHED' and info.get('ExecMainStatus')=='0' else 'FAIL'
    elif case=='C06':
        p=OUT/'C06.watchdog_stop.json'
        status='PASS' if p.exists() and read(p).get('expired') and int(info.get('ExecMainStatus','0'))!=0 else 'FAIL'
        if p.exists(): actual['watchdog']=read(p)
    elif case=='C07': status='PASS' if (OUT/'C07.ready.json').exists() and info.get('ExecMainStatus')=='23' else 'FAIL'
    elif case=='C08':
        p=OUT/'C08.ready.json'
        failure=OUT/'C08.monitor_failure.json'
        status='PASS' if p.exists() and failure.exists() and read(failure)['reason']=='WATCHDOG_EXIT' and read(p)['counter']==count() and info.get('ExecMainStatus')=='125' else 'FAIL'
    result={'case':case,'status':status,'actual':actual,'sample':stamp()}
    _root_write(ROOT/('inputs/result_'+case+'.json'),result)
    return result
def seal():
    if _COORDINATOR_ID is not None and identity()!=_COORDINATOR_ID:return None
    boot_continuity().before_seal(sys.modules[__name__])
    # Wait for the independent writer to finish before freezing evidence.
    until=now()+20
    while now()<until:
        if unit_show('dclr6batch08-stop.service').get('ActiveState') in ('inactive','failed'): break
        time.sleep(.05)
    else: raise AdmissionBlocked('EXTERNAL_STOP_NOT_CLOSED; evidence remains unsealed')
    rows={}
    for p in sorted(ROOT.rglob('*')):
        if p.is_file() and not p.is_symlink() and p.name not in ('EVIDENCE_MANIFEST.json','EVIDENCE.zip'):
            rows[str(p.relative_to(ROOT))]={'bytes':p.stat().st_size,'sha256':digest(p)}
    write(OUT/'EVIDENCE_MANIFEST.json',{'files':rows,'sample':stamp()})
    with zipfile.ZipFile(OUT/'EVIDENCE.zip','x',zipfile.ZIP_DEFLATED) as z:
        for rel in rows: z.write(ROOT/rel,rel)
        z.write(OUT/'EVIDENCE_MANIFEST.json','out/EVIDENCE_MANIFEST.json')
    return digest(OUT/'EVIDENCE.zip')
def _launcher_body(resume=False,calibrate_only=False):
    if os.geteuid()!=0: raise AdmissionBlocked('TRUSTED_ROOT_LAUNCHER_REQUIRED')
    a,m=authorization()
    boot_continuity().child_admission(sys.modules[__name__],resume)
    expected_scope='C00_DIAGNOSTIC_ONLY' if a['scope']=='C00_DIAGNOSTIC_ONLY' else ('CALIBRATE_S1S9_ONLY' if calibrate_only else 'CALIBRATE_S1S9_THEN_F1_F4')
    if a['scope']!=expected_scope:raise AdmissionBlocked('LAUNCH_SCOPE_MODE_MISMATCH')
    if _run(['/usr/bin/systemctl','show','--property=Version','--value']).strip()!=m['systemd']:
        raise AdmissionBlocked('SYSTEMD_VERSION_DRIFT')
    failed=_run(['/usr/bin/systemctl','list-units','--state=failed','--all','--no-pager','--no-legend'])
    for line in failed.splitlines():
        fields=line.replace('●','').split()
        if fields and fields[0]!='mnt-e.mount': raise AdmissionBlocked('UNREVIEWED_MANAGER_FAILURE')
    lock=os.open(ROOT/'inputs/launcher.lock',os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600)
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    try:
        if not resume:
            require_fresh_initialization((ROOT/'inputs/batch_state.json').exists(),
                                         (OUT/'visits.bin').exists(),(ROOT/'inputs/CLOSED.json').exists())
            if any(OUT.iterdir()): raise AdmissionBlocked('NEW_BATCH_OUTPUT_MUST_BE_EMPTY')
            t0=now(); s={'status':'CALIBRATING','boot_id':boot_id(),'T0':t0,'stop_at':t0+1740,
                'deadline':t0+1800,'launcher_identity':identity(),'resume_count':0,'expected_launcher_exit':None}
            s['execution_mode']=expected_scope;s['coordinator_identity']=_COORDINATOR_ID
            _root_write(ROOT/'inputs/batch_state.json',s);init_counter(OUT/'visits.bin',VISIT_CAP)
            stop_argv=['/usr/bin/systemd-run','--no-block','--unit=dclr6batch08-stop.service','--property=Type=exec',
                  '--property=Restart=no','--property=User=root',PYTHON,'-I','-S','-B',str(SOURCE/'guard.py'),
                  '--role','external-stop','--batch-root',str(ROOT)]
            if stop_argv!=trusted(SOURCE.parent/'inputs/execution_lock.json')['external_stop_command']:
                raise AdmissionBlocked('STOP_ARGV_DRIFT')
            _run(stop_argv)
            until=now()+14
            root_ipc().wait_ready(sys.modules[__name__],ROOT/'inputs/STOP_ARMED.json',until)
            armed=trusted(ROOT/'inputs/STOP_ARMED.json')
            if armed['stop_at']!=s['stop_at'] or identity(armed['identity']['pid'])!=armed['identity']:
                raise AdmissionBlocked('EXTERNAL_STOP_NOT_ARMED')
            remaining=CASES
        else:
            import c09_handoff as H
            s=H.resume_admission(sys.modules[__name__],_COORDINATOR_ID)
            if s.get('execution_mode')!=expected_scope:raise AdmissionBlocked('RESUME_SCOPE_MODE_MISMATCH')
            remaining=CASES[10:]
        _run(['/usr/bin/systemctl','start',PARENT])
        verify_runtime_tree(manifest())
        info=unit_show(PARENT)
        if info.get('TasksMax')!='4': raise AdmissionBlocked('PARENT_LIMIT_NOT_CONFIGURED')
        for c in remaining:
            root_checkpoint()
            if c=='C09':
                htest=launch_one('C09H')
                if htest['status']!='PASS':stop_tree('C09H_REGRESSION_FAILED');return 65
                root_verify_c09h()
                root_checkpoint()
                import root_ipc_regression
                root_ipc_regression.run_suite(sys.modules[__name__])
                root_ipc().verify_qualification(sys.modules[__name__])
                import boot_continuity_regression
                boot_continuity_regression.run_suite(sys.modules[__name__])
            r=launch_one(c)
            if r['status']!='PASS': stop_tree('CALIBRATION_'+r['status']);return 65
            if c=='C00':
                import readiness_regression
                readiness_regression.run_suite(sys.modules[__name__])
                if a['scope']=='C00_DIAGNOSTIC_ONLY':
                    stop_tree('C00_DIAGNOSTIC_COMPLETE');seal();return 0
        r=launch_one('RANGE')
        if r['status']!='PASS':stop_tree('RANGE_CALIBRATION_'+r['status']);return 65
        range_report=root_verify_safety()
        receipts={c:digest(ROOT/('inputs/result_'+c+'.json')) for c in CASES}
        for c in CASES:
            if trusted(ROOT/('inputs/result_'+c+'.json'))['status']!='PASS': raise AdmissionBlocked('INCOMPLETE_QUALIFICATION')
        _root_write(ROOT/'inputs/RESOURCE_QUALIFICATION.json',{'cases':receipts,'boot_id':boot_id(),
            'source_manifest':digest(SOURCE.parent/'inputs/static_manifest.json'),
            'binding':range_report['binding'],'safety_receipt_sha256':digest(ROOT/'inputs/RANGE_QUALIFICATION.json'),
            'sample':stamp()})
        if calibrate_only:
            stop_tree('CALIBRATION_S1S9_COMPLETE');seal();return 0
        import c09_handoff as H
        with H.lifecycle_lock(sys.modules[__name__]):
            root_checkpoint()
            s=state();s['status']='FORMAL';_root_write(ROOT/'inputs/batch_state.json',s)
        r=launch_one('FORMAL')
        stop_tree('FORMAL_COMPLETE' if r['status']=='PASS' else 'FORMAL_FAILED')
        seal();return 0 if r['status']=='PASS' else 65
    except BaseException:
        if (ROOT/'inputs/batch_state.json').exists():
            try: stop_tree('LAUNCHER_ERROR')
            except BaseException: pass
        raise
    finally:
        if (ROOT/'inputs/CLOSED.json').exists() and _empty() and not (OUT/'EVIDENCE.zip').exists():
            try: seal()
            except BaseException as exc:
                _root_write(ROOT/'inputs/SEAL_ERROR.json',{'error':repr(exc),'sample':stamp()})
        os.close(lock)
def launcher(resume=False,calibrate_only=False):
    """Root parent is the actual waitpid witness; child retains the old scheduler."""
    global _COORDINATOR_ID
    if os.geteuid()!=0:raise AdmissionBlocked('TRUSTED_ROOT_COORDINATOR_REQUIRED')
    authorization()
    boot_continuity().guard_admission(sys.modules[__name__],resume)
    sys.path.insert(0,str(SOURCE))
    import c09_handoff as H
    coordinator=identity()
    ready_r,ready_w=os.pipe2(os.O_CLOEXEC)
    go_r,go_w=os.pipe2(os.O_CLOEXEC)
    child=os.fork()
    if child==0:
        os.close(ready_r);os.close(go_w)
        _COORDINATOR_ID=coordinator
        raw=json.dumps(identity()).encode()
        try:
            _full(ready_w,raw);os.close(ready_w)
            if os.read(go_r,1)!=b'G':os._exit(125)
            os.close(go_r)
            try:code=_launcher_body(resume,calibrate_only)
            except LimitReached as exc:print('INCONCLUSIVE_LIMIT',str(exc),file=sys.stderr,flush=True);code=124
            except BaseException:traceback.print_exc();code=125
            sys.stdout.flush();sys.stderr.flush();os._exit(code)
        except BaseException:os._exit(125)
    os.close(ready_w);os.close(go_r)
    fd=None;child_reaped=False
    try:
        root_ipc().wait_fd(sys.modules[__name__],ready_r,now()+5)
        child_identity=json.loads(os.read(ready_r,4096))
        if child_identity!=identity(child):raise AdmissionBlocked('COORDINATOR_CHILD_IDENTITY')
        fd=os.pidfd_open(child)
        if child_identity!=identity(child):raise AdmissionBlocked('COORDINATOR_CHILD_PIDFD_RACE')
        _full(go_w,b'G');os.close(go_w);go_w=None
        startup_until=now()+15;terminal_seen=None
        while True:
            ended,status=os.waitpid(child,os.WNOHANG)
            if ended:break
            flags=root_ipc().observe(sys.modules[__name__])
            if any(flags.values()):
                if terminal_seen is None:
                    terminal_seen=now()
                    if not flags['closed']:stop_tree('COORDINATOR_STOP_REQUEST')
                # Child observes cancellation, cleans and returns. Finite grace protects
                # against a scheduler that fails to cooperate; no new work is admitted.
                if now()>=terminal_seen+30:
                    signal.pidfd_send_signal(fd,signal.SIGKILL)
            p=ROOT/'inputs/batch_state.json'
            if p.exists():
                s=trusted(p);limit=s['deadline']
                if s['boot_id']!=boot_id():raise AdmissionBlocked('COORDINATOR_BOOT_DRIFT')
            else:limit=startup_until
            if now()>=limit:raise LimitReached('COORDINATOR_ABSOLUTE_LIMIT')
            time.sleep(.02)
        code=os.waitstatus_to_exitcode(status)
        child_reaped=True
        raw_state=trusted(ROOT/'inputs/batch_state.json') if (ROOT/'inputs/batch_state.json').exists() else None
        _root_write(ROOT/('inputs/root_private/waitpid_%s.json'%child),{
            'schema':'ROOT-IPC-WAITPID/1','child':child_identity,'coordinator':coordinator,
            'raw_wait_status':status,'exit_code':code,'state':raw_state,'sample':stamp()})
        if H.paths(sys.modules[__name__])['state'].exists() and not (ROOT/'inputs/CLOSED.json').exists():
            verified=H.coordinator_witness(sys.modules[__name__],child_identity,status)
            if code==23 and verified is None:raise AdmissionBlocked('C09_NO_VERIFIED_HANDOFF')
        elif code==23:raise AdmissionBlocked('C09_EXIT23_WITHOUT_RECEIPT')
        return code if code>=0 else 128-code
    except BaseException as exc:
        if fd is not None and not select.select([fd],[],[],0)[0]:
            try:signal.pidfd_send_signal(fd,signal.SIGKILL)
            except OSError:pass
        if not child_reaped:
            if fd is None:
                try:os.kill(child,signal.SIGKILL)
                except ProcessLookupError:pass
            reap_until=now()+5
            while now()<reap_until:
                ended,cleanup_status=os.waitpid(child,os.WNOHANG)
                if ended:
                    child_reaped=True
                    try:_root_write(ROOT/('inputs/root_private/waitpid_%s.json'%child),{
                        'schema':'ROOT-IPC-WAITPID/1','child':child_identity if 'child_identity' in locals() else {'pid':child},
                        'coordinator':coordinator,'raw_wait_status':cleanup_status,
                        'exit_code':os.waitstatus_to_exitcode(cleanup_status),'sample':stamp(),'reason':'COORDINATOR_EXCEPTION'})
                    except BaseException:pass
                    break
                time.sleep(.02)
            if not child_reaped:
                try:stop_tree('COORDINATOR_REAP_UNCONFIRMED')
                finally:raise AdmissionBlocked('COORDINATOR_REAP_UNCONFIRMED')
        if (ROOT/'inputs/batch_state.json').exists():
            try:stop_tree('COORDINATOR_FAILURE:'+str(exc))
            except BaseException:pass
        raise
    finally:
        os.close(ready_r)
        if go_w is not None:os.close(go_w)
        if fd is not None:os.close(fd)
        if child_reaped and (ROOT/'inputs/CLOSED.json').exists() and _empty() and not (OUT/'EVIDENCE.zip').exists():
            try:seal()
            except BaseException as exc:
                _root_write(ROOT/'inputs/SEAL_ERROR.json',{'error':repr(exc),'sample':stamp()})
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--role',choices=('controller','watchdog','external-stop','launcher'),required=True)
    parser.add_argument('--batch-root',choices=tuple(map(str,ROOTS)),required=True)
    parser.add_argument('--case',choices=CASES+('C09H','RANGE','FORMAL',))
    parser.add_argument('--parent',type=int);parser.add_argument('--parent-start',type=int)
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--calibrate-only',action='store_true')
    args=parser.parse_args()
    if args.role=='launcher': return boot_continuity().entry(sys.modules[__name__],args.resume,args.calibrate_only)
    if args.role=='external-stop': return external_stop()
    if args.role=='watchdog': return watchdog(args.case,args.parent,args.parent_start)
    return controller(args.case)
if __name__=='__main__':
    try: rc=main()
    except LimitReached as e: print('INCONCLUSIVE_LIMIT',str(e),file=sys.stderr);rc=124
    except BaseException: traceback.print_exc();rc=125
    sys.exit(rc)
