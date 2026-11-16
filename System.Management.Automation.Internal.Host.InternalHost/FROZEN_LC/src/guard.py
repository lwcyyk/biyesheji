"""Linux R6 static deployment candidate. Dynamic authorization is separate.

The root launcher and external stop service are trusted infrastructure. Payload
admission checks kernel facts in addition to root-owned authorization records.
No role is executed by py_compile. Historical Windows sources stay archived.
"""
import argparse
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
ROOTS = (Path('/var/lib/dcl-r6/lc01'), Path('/var/lib/dcl-r6/batch02'))
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
def atomic(path, data, root_record=False):
    _check_root()
    p = _inside(path, ROOT if root_record and os.geteuid() == 0 else OUT)
    p.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2).encode('utf-8')
    tmp = p.with_name(p.name + '.tmp.%s.%s' % (os.getpid(), threading.get_ident()))
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o640 if root_record else 0o600)
    try:
        if root_record:
            os.fchown(fd,0,pwd.getpwnam('dcl-r6').pw_gid)
            os.fchmod(fd,0o640)
        _full(fd, raw); os.fsync(fd)
    finally: os.close(fd)
    os.replace(tmp, p)
    d = os.open(p.parent, os.O_RDONLY | os.O_DIRECTORY)
    try: os.fsync(d)
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
    if ROOT.name != 'batch02' or a['batch_id'] != 'batch02' or a['scope'] != 'CALIBRATE_THEN_F1_F4':
        raise AdmissionBlocked('NO_DYNAMIC_BATCH02_AUTHORIZATION')
    if a['profile'] != 'CPY312-UBU24/1' or a['limits'] != [1000000,1800,1740,AS_CAP,4]:
        raise AdmissionBlocked('CONTRACT_MISMATCH')
    if a['static_manifest_sha256'] != digest(SOURCE.parent/'inputs/static_manifest.json'):
        raise AdmissionBlocked('STATIC_LOCK_MISMATCH')
    if a['execution_lock_sha256'] != digest(SOURCE.parent/'inputs/execution_lock.json'):
        raise AdmissionBlocked('EXECUTION_LOCK_MISMATCH')
    if a['authorization_text_sha256'] != digest(ROOT/'inputs/BATCH02_AUTHORIZATION_TEXT.txt'):
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
def require_formal_admission():
    if _TICKET is None or _TICKET['case'] != 'FORMAL' or _TICKET['main_identity'] != identity():
        raise AdmissionBlocked('CONTROLLER_CONTEXT_REQUIRED')
    kernel_admission(_TICKET); guardian_check()
    q=trusted(ROOT/'inputs/RESOURCE_QUALIFICATION.json')
    if q['boot_id']!=boot_id() or q['source_manifest']!=digest(SOURCE.parent/'inputs/static_manifest.json'):
        raise AdmissionBlocked('QUALIFICATION_BINDING_MISMATCH')
    if set(q['cases'])!=set(CASES): raise AdmissionBlocked('INCOMPLETE_CALIBRATION')
    for c,h in q['cases'].items():
        p=ROOT/('inputs/result_'+c+'.json'); r=trusted(p)
        if digest(p)!=h or r['status']!='PASS' or r['case']!=c:
            raise AdmissionBlocked('CALIBRATION_EVIDENCE_MISMATCH')
def request_stop(reason):
    write(OUT/'STOP_REQUEST.json',{'reason':reason,**stamp()})
def init_counter(path,cap):
    p=_inside(path,OUT)
    if p==OUT/'visits.bin' and os.geteuid()!=0: raise AdmissionBlocked('ROOT_INITIALIZATION_REQUIRED')
    p.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    try: _full(fd,bytes(8)+struct.pack('<QQ',0,cap)); os.fsync(fd)
    finally: os.close(fd)
    if os.geteuid()==0:
        u=pwd.getpwnam('dcl-r6'); os.chown(p,u.pw_uid,u.pw_gid)
    atomic(p.with_suffix(p.suffix+'.intent.json'),{'status':'COMMITTED','after':0,'cap':cap})
    if os.geteuid()==0:
        os.chown(p.with_suffix(p.suffix+'.intent.json'),u.pw_uid,u.pw_gid)
def count(path=None):
    p=OUT/'visits.bin' if path is None else _inside(path,OUT)
    with p.open('rb') as f:
        raw=f.read()
    if len(raw)!=24 or raw[:8]!=bytes(8): raise AdmissionBlocked('COUNTER_FORMAT')
    used,cap=struct.unpack('<QQ',raw[8:])
    if used>cap: raise AdmissionBlocked('COUNTER_OVERFLOW')
    return used
def reserve_counter(path,cap, fault=None):
    p=_inside(path,OUT); local=p!=OUT/'visits.bin'
    if fault and not local: raise AdmissionBlocked('FAULT_IN_GLOBAL_LEDGER_FORBIDDEN')
    with _LOCKS_LOCK: lock=_LOCKS.setdefault(str(p),threading.RLock())
    with lock:
        fd=os.open(p,os.O_RDWR|os.O_NOFOLLOW)
        acquired=False
        try:
            while not acquired:
                try: fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB); acquired=True
                except BlockingIOError: guardian_check(); state(); time.sleep(.005)
            raw=os.pread(fd,24,0)
            if len(raw)!=24 or raw[:8]!=bytes(8): raise AdmissionBlocked('TORN_COUNTER')
            used,storedcap=struct.unpack('<QQ',raw[8:])
            if storedcap!=cap or used>cap: raise AdmissionBlocked('COUNTER_CAP_MISMATCH')
            intent=p.with_suffix(p.suffix+'.intent.json')
            old=read(intent)
            if old['status']!='COMMITTED' or old['after']!=used or old['cap']!=cap:
                raise AdmissionBlocked('AMBIGUOUS_RESERVATION')
            if used>=cap: raise LimitReached('VISIT_LIMIT')
            record={'status':'PREPARED','before':used,'after':used+1,'cap':cap,**stamp()}
            atomic(intent,record)
            if fault=='prepared': raise OSError('INJECTED_AFTER_PREPARED')
            journal=p.with_suffix(p.suffix+'.journal.jsonl')
            j=os.open(journal,os.O_WRONLY|os.O_CREAT|os.O_APPEND|os.O_NOFOLLOW,0o600)
            try: _full(j,(json.dumps(record,sort_keys=True)+'\n').encode()); os.fsync(j)
            finally: os.close(j)
            payload=struct.pack('<Q',used+1)
            if fault=='short_write': payload=payload[:3]
            n=os.pwrite(fd,payload,8)
            if n!=8: raise AdmissionBlocked('SHORT_COUNTER_WRITE')
            os.fsync(fd)
            if fault=='counter_fsynced': raise OSError('INJECTED_AFTER_COUNTER_FSYNC')
            record['status']='COMMITTED'
            j=os.open(journal,os.O_WRONLY|os.O_APPEND|os.O_NOFOLLOW)
            try: _full(j,(json.dumps(record,sort_keys=True)+'\n').encode()); os.fsync(j)
            finally: os.close(j)
            if fault=='journal_fsynced': raise OSError('INJECTED_BEFORE_COMMITTED_INTENT')
            atomic(intent,record)
            return used+1
        finally:
            if acquired: fcntl.flock(fd,fcntl.LOCK_UN)
            os.close(fd)
class Budget:
    def __init__(self,local=None):
        if _TICKET is None: raise AdmissionBlocked('PAYLOAD_CONTEXT_REQUIRED')
        kernel_admission(_TICKET); guardian_check()
        self.local=Path(local) if local else None; self.calls=0
    def visit(self):
        guardian_check(); s=state()
        if stopped() or now()>=min(s['stop_at'],_TICKET['case_deadline']): raise LimitReached('WALL_OR_STOP_LIMIT')
        if _TICKET['case']!='FORMAL' and count()>=100000: raise LimitReached('CALIBRATION_SOFT_VISITS')
        reserve_counter(OUT/'visits.bin',VISIT_CAP); self.calls+=1
        if self.local: reserve_counter(self.local,17)
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
    unit='dclr6batch02-'+case.lower()+'.service'
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
    if close:
        p=ROOT/'inputs/CLOSED.json'
        if p.exists(): p=ROOT/('inputs/stop_event_%s_%s.json'%(os.getpid(),time.time_ns()))
        _root_write(p,{'reason':reason,**stamp()})
    r=subprocess.run(['/usr/bin/systemctl','stop',PARENT],capture_output=True,timeout=15)
    until=now()+5
    while not _empty() and now()<until: time.sleep(.05)
    if not _empty(): raise AdmissionBlocked('STOP_UNCONFIRMED')
    result={'empty':True,'stop_exit':r.returncode,'before_stop_charged_snapshot':before,
            'peak_scope':'observed charge peak for this group generation; no exact RSS tree peak inferred',
            'after_stop_group_exists':parent.exists(),'sample':stamp()}
    _root_write(ROOT/('inputs/stop_result_%s_%s.json'%(os.getpid(),time.time_ns())),result)
    return result
def external_stop():
    if os.geteuid()!=0: raise AdmissionBlocked('TRUSTED_LAUNCHER_ONLY')
    authorization(); s=state(); monitored=None; fd=None
    _root_write(ROOT/'inputs/STOP_ARMED.json',{'identity':identity(),'stop_at':s['stop_at'],'boot_id':boot_id()})
    while True:
        s=trusted(ROOT/'inputs/batch_state.json')
        if (ROOT/'inputs/CLOSED.json').exists():
            stop_tree('CLOSED_BATCH_CLEANUP',False); return 0
        if s['boot_id']!=boot_id() or now()>=s['stop_at'] or (OUT/'STOP_REQUEST.json').exists():
            stop_tree('ABSOLUTE_STOP_OR_REQUEST'); return 124
        target=s.get('launcher_identity')
        if target and target!=monitored:
            if fd is not None: os.close(fd)
            try: valid=identity(target['pid'])==target
            except OSError: valid=False
            if not valid: stop_tree('LAUNCHER_IDENTITY_CHANGED'); return 125
            try:
                fd=os.pidfd_open(target['pid'])
                if identity(target['pid'])!=target: raise ProcessLookupError('PID_REUSED')
            except OSError:
                stop_tree('LAUNCHER_PIDFD_NOT_STABLE'); return 125
            monitored=target
        if fd is not None and select.select([fd],[],[],.1)[0]:
            if s.get('expected_launcher_exit')=='C09' and s.get('resume_count',0)==0:
                cleanup=stop_tree('EXPECTED_C09',False)
                marker=read(OUT/'C09.ready.json')
                if marker['case']!='C09' or marker['counter']!=count() or marker['identity']!=ticket('C09')['main_identity']:
                    stop_tree('C09_LEDGER_OR_MARKER_MISMATCH'); return 125
                _root_write(ROOT/'inputs/result_C09.json',{'case':'C09','status':'PASS',
                    'actual':{'launcher_exit_observed':True,'cleanup':cleanup,'marker':marker},'sample':stamp()})
                s['status']='AWAIT_EXPECTED_RESUME';s['launcher_identity']=None;s['expected_launcher_exit']=None
                _root_write(ROOT/'inputs/batch_state.json',s)
                os.close(fd);fd=None;monitored=None
            else: stop_tree('UNEXPECTED_LAUNCHER_EXIT'); return 125
        else: time.sleep(.05)
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
            require_formal_admission()
            sys.argv=[str(SOURCE/'run_batch.py'),'--batch-root',str(ROOT),'--session','1']
            runpy.run_path(str(SOURCE/'run_batch.py'),run_name='__main__')
            return 0
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
def launch_one(case):
    argv=service_argv(case)
    lock=trusted(SOURCE.parent/'inputs/execution_lock.json')
    if argv!=lock['payload_commands'][case]: raise AdmissionBlocked('PAYLOAD_ARGV_DRIFT')
    _run(argv)
    unit='dclr6batch02-'+case.lower()+'.service'; until=now()+14
    info={}
    while now()<until:
        info=unit_show(unit); pid=int(info.get('MainPID','0'))
        if pid: break
        time.sleep(.02)
    else: raise AdmissionBlocked('NO_CONTROLLER_PID')
    s=state()
    limit=s['stop_at'] if case=='FORMAL' else min(s['stop_at'],s['T0']+300,now()+(2 if case=='C06' else 300))
    t={'case':case,'unit':unit,'main_identity':identity(pid),'boot_id':boot_id(),
       'source_manifest':digest(SOURCE.parent/'inputs/static_manifest.json'),'case_deadline':limit,
       'unit_before_ticket':info,'argv':argv}
    _root_write(ROOT/('inputs/ticket_'+case+'.json'),t)
    if case=='C09':
        while not (OUT/'C09.ready.json').exists() and now()<limit: time.sleep(.05)
        if not (OUT/'C09.ready.json').exists(): raise AdmissionBlocked('C09_NOT_READY')
        s=state();s['expected_launcher_exit']='C09';_root_write(ROOT/'inputs/batch_state.json',s)
        os._exit(23)  # one predeclared crash; resume retains T0/deadline/ledger
    while now()<limit+5:
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
    # Wait for the independent writer to finish before freezing evidence.
    until=now()+20
    while now()<until:
        if unit_show('dclr6batch02-stop.service').get('ActiveState') in ('inactive','failed'): break
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
def launcher(resume=False):
    if os.geteuid()!=0: raise AdmissionBlocked('TRUSTED_ROOT_LAUNCHER_REQUIRED')
    _,m=authorization()
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
            if (ROOT/'inputs/batch_state.json').exists() or (OUT/'visits.bin').exists():
                raise AdmissionBlocked('BATCH_ALREADY_INITIALIZED')
            if any(OUT.iterdir()): raise AdmissionBlocked('NEW_BATCH_OUTPUT_MUST_BE_EMPTY')
            t0=now(); s={'status':'CALIBRATING','boot_id':boot_id(),'T0':t0,'stop_at':t0+1740,
                'deadline':t0+1800,'launcher_identity':identity(),'resume_count':0,'expected_launcher_exit':None}
            _root_write(ROOT/'inputs/batch_state.json',s);init_counter(OUT/'visits.bin',VISIT_CAP)
            stop_argv=['/usr/bin/systemd-run','--no-block','--unit=dclr6batch02-stop.service','--property=Type=exec',
                  '--property=Restart=no','--property=User=root',PYTHON,'-I','-S','-B',str(SOURCE/'guard.py'),
                  '--role','external-stop','--batch-root',str(ROOT)]
            if stop_argv!=trusted(SOURCE.parent/'inputs/execution_lock.json')['external_stop_command']:
                raise AdmissionBlocked('STOP_ARGV_DRIFT')
            _run(stop_argv)
            until=now()+14
            while not (ROOT/'inputs/STOP_ARMED.json').exists() and now()<until: time.sleep(.02)
            armed=trusted(ROOT/'inputs/STOP_ARMED.json')
            if armed['stop_at']!=s['stop_at'] or identity(armed['identity']['pid'])!=armed['identity']:
                raise AdmissionBlocked('EXTERNAL_STOP_NOT_ARMED')
            remaining=CASES
        else:
            s=state()
            until=min(s['stop_at'],now()+14)
            while s['status']=='CALIBRATING' and s.get('expected_launcher_exit')=='C09' and now()<until:
                time.sleep(.05);s=state()
            if s['status']!='AWAIT_EXPECTED_RESUME' or s['resume_count']!=0:
                raise AdmissionBlocked('NO_EXPECTED_C09_RESUME')
            if trusted(ROOT/'inputs/result_C09.json')['status']!='PASS': raise AdmissionBlocked('C09_NOT_PASSED')
            s['status']='CALIBRATING';s['resume_count']=1;s['launcher_identity']=identity()
            _root_write(ROOT/'inputs/batch_state.json',s);remaining=CASES[10:]
        _run(['/usr/bin/systemctl','start',PARENT])
        verify_runtime_tree(manifest())
        info=unit_show(PARENT)
        if info.get('TasksMax')!='4': raise AdmissionBlocked('PARENT_LIMIT_NOT_CONFIGURED')
        for c in remaining:
            r=launch_one(c)
            if r['status']!='PASS': stop_tree('CALIBRATION_'+r['status']);return 65
        receipts={c:digest(ROOT/('inputs/result_'+c+'.json')) for c in CASES}
        for c in CASES:
            if trusted(ROOT/('inputs/result_'+c+'.json'))['status']!='PASS': raise AdmissionBlocked('INCOMPLETE_QUALIFICATION')
        _root_write(ROOT/'inputs/RESOURCE_QUALIFICATION.json',{'cases':receipts,'boot_id':boot_id(),
            'source_manifest':digest(SOURCE.parent/'inputs/static_manifest.json'),'sample':stamp()})
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
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--role',choices=('controller','watchdog','external-stop','launcher'),required=True)
    parser.add_argument('--batch-root',choices=tuple(map(str,ROOTS)),required=True)
    parser.add_argument('--case',choices=CASES+('FORMAL',))
    parser.add_argument('--parent',type=int);parser.add_argument('--parent-start',type=int)
    parser.add_argument('--resume',action='store_true')
    args=parser.parse_args()
    if args.role=='launcher': return launcher(args.resume)
    if args.role=='external-stop': return external_stop()
    if args.role=='watchdog': return watchdog(args.case,args.parent,args.parent_start)
    return controller(args.case)
if __name__=='__main__':
    try: rc=main()
    except LimitReached as e: print('INCONCLUSIVE_LIMIT',str(e),file=sys.stderr);rc=124
    except BaseException: traceback.print_exc();rc=125
    sys.exit(rc)
