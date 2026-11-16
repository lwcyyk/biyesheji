"""Windows-only R6 resource guard. No model semantics are implemented here."""
import os, sys, json, time, struct, hashlib, traceback, ctypes, subprocess, shutil, errno
from pathlib import Path
from ctypes import wintypes as W
import msvcrt, _winapi

_HERE = Path(__file__).resolve()
ROOT = _HERE.parents[2] if _HERE.parent.name == 'v3' and _HERE.parent.parent.name == 'versions' else _HERE.parent.parent
PYTHON = Path(r'C:\Program Files\Python314\python.exe')
GIB = 1024 ** 3
WS_CAP = 768 * 1024 ** 2
GUARD_V3_STATUS = 'STATIC_CANDIDATE_NOT_CALIBRATED'
STRICT_BOUND_STATUS = 'UNRESOLVED_BOOTSTRAP_AND_PEAK_WINDOWS'
_FD_PATHS = {}
_RUNTIME_JOB = None
_GUARDIAN = None
K = ctypes.WinDLL('kernel32', use_last_error=True)
P = ctypes.WinDLL('psapi', use_last_error=True)
SZ = ctypes.c_size_t
U64 = ctypes.c_ulonglong

class BASIC(ctypes.Structure):
    _fields_ = [('ProcessTime', ctypes.c_longlong), ('JobTime', ctypes.c_longlong),
                ('Flags', W.DWORD), ('MinWS', SZ), ('MaxWS', SZ),
                ('ActiveLimit', W.DWORD), ('Affinity', SZ),
                ('Priority', W.DWORD), ('Scheduling', W.DWORD)]

class IO(ctypes.Structure):
    _fields_ = [(x, U64) for x in ('ReadOps','WriteOps','OtherOps','ReadBytes','WriteBytes','OtherBytes')]

class EXT(ctypes.Structure):
    _fields_ = [('Basic', BASIC), ('Io', IO), ('ProcessMemory', SZ), ('JobMemory', SZ),
                ('PeakProcess', SZ), ('PeakJob', SZ)]

class PMC(ctypes.Structure):
    _fields_ = [('cb', W.DWORD), ('PageFaults', W.DWORD)] + [(x, SZ) for x in
        ('PeakWS','WS','PeakPaged','Paged','PeakNonPaged','NonPaged','Pagefile','PeakPagefile','Private')]

class SYSTEM_INFO(ctypes.Structure):
    _fields_=[('ProcessorUnion',W.DWORD),('PageSize',W.DWORD),('MinimumAddress',ctypes.c_void_p),
              ('MaximumAddress',ctypes.c_void_p),('ActiveMask',SZ),('ProcessorCount',W.DWORD),
              ('ProcessorType',W.DWORD),('AllocationGranularity',W.DWORD),('Level',W.WORD),('Revision',W.WORD)]

def api(name, args, restype=W.BOOL):
    fn = getattr(K, name); fn.argtypes = args; fn.restype = restype
    return fn

create_job = api('CreateJobObjectW', [ctypes.c_void_p, W.LPCWSTR], W.HANDLE)
open_job = api('OpenJobObjectW', [W.DWORD, W.BOOL, W.LPCWSTR], W.HANDLE)
set_job = api('SetInformationJobObject', [W.HANDLE,W.INT,ctypes.c_void_p,W.DWORD])
query_job = api('QueryInformationJobObject', [W.HANDLE,W.INT,ctypes.c_void_p,W.DWORD,ctypes.c_void_p])
assign_job = api('AssignProcessToJobObject', [W.HANDLE,W.HANDLE])
in_job = api('IsProcessInJob', [W.HANDLE,W.HANDLE,ctypes.POINTER(W.BOOL)])
terminate_job = api('TerminateJobObject', [W.HANDLE,W.UINT])
close_handle = api('CloseHandle', [W.HANDLE])
resume_thread = api('ResumeThread', [W.HANDLE], W.DWORD)
get_current = api('GetCurrentProcess', [], W.HANDLE)
open_process = api('OpenProcess', [W.DWORD,W.BOOL,W.DWORD], W.HANDLE)
exit_code = api('GetExitCodeProcess', [W.HANDLE,ctypes.POINTER(W.DWORD)])
wait_one = api('WaitForSingleObject', [W.HANDLE,W.DWORD], W.DWORD)
wait_many = api('WaitForMultipleObjects', [W.DWORD,ctypes.POINTER(W.HANDLE),W.BOOL,W.DWORD], W.DWORD)
set_ws = api('SetProcessWorkingSetSizeEx', [W.HANDLE,SZ,SZ,W.DWORD])
get_ws = api('GetProcessWorkingSetSizeEx', [W.HANDLE,ctypes.POINTER(SZ),ctypes.POINTER(SZ),ctypes.POINTER(W.DWORD)])
create_event = api('CreateEventW',[ctypes.c_void_p,W.BOOL,W.BOOL,W.LPCWSTR],W.HANDLE)
open_event = api('OpenEventW',[W.DWORD,W.BOOL,W.LPCWSTR],W.HANDLE)
signal_event = api('SetEvent',[W.HANDLE])
get_process_times = api('GetProcessTimes',[W.HANDLE,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p])
get_system_info = api('GetSystemInfo',[ctypes.c_void_p],None)
P.GetProcessMemoryInfo.argtypes = [W.HANDLE,ctypes.c_void_p,W.DWORD]
P.GetProcessMemoryInfo.restype = W.BOOL

def must(ok, action):
    if not ok: raise OSError(ctypes.get_last_error(), action)

class AdmissionBlocked(RuntimeError): pass

def assert_open_batch():
    """Read-only refusal, before writes, reservations or Job creation."""
    if (ROOT/'reports'/'BATCH_CLOSED.json').exists():
        raise AdmissionBlocked('BATCH_CLOSED: historical accounting is immutable')
    state_path=ROOT/'BATCH_STATE.json'
    if not state_path.exists():
        raise AdmissionBlocked('EXTERNAL_BATCH_INITIALIZATION_REQUIRED; no auto-new clock/counter')
    state=read(state_path)
    if time.perf_counter_ns()>=state['deadline_monotonic_ns']:
        raise AdmissionBlocked('ABSOLUTE_DEADLINE_EXPIRED; no reset/extension')
    receipt=read(ROOT/'AUTHORIZATION_RECEIPT.json')
    if Path(receipt['write_root']).resolve()!=ROOT:
        raise AdmissionBlocked('AUTHORIZATION_ROOT_MISMATCH')
    return state

def stamp(): return {'monotonic_ns':time.perf_counter_ns(),'utc_ns':time.time_ns()}

def require_strict_bound_adapter():
    # A JSON "verified" flag is not a resource proof. The current Windows
    # self-bootstrap architecture has no certified pre-creation envelope.
    raise AdmissionBlocked('STRICT_TREE_BOUND_UNPROVEN: bootstrap/peak-window adapter is not certified; formal execution disabled')

def require_formal_admission():
    assert_open_batch()
    require_strict_bound_adapter()

def assert_guardian_alive():
    if _GUARDIAN is None:raise AdmissionBlocked('LIVE_GUARDIAN_CONTEXT_REQUIRED')
    if wait_one(_GUARDIAN,0)==0:
        if _RUNTIME_JOB is not None:
            write(ROOT/'raw'/f'watchdog_failure.{os.getpid()}.json',{'reason':'GUARDIAN_EXITED',**stamp()})
            _RUNTIME_JOB.stop(125)
        raise AdmissionBlocked('GUARDIAN_EXITED')

def write(path, data):
    assert_open_batch()
    path = Path(path).resolve()
    if not path.is_relative_to(ROOT): raise AdmissionBlocked('WRITE_OUTSIDE_AUTHORIZED_ROOT')
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        history=ROOT/'raw'/'administrative_history'/hashlib.sha256(str(path).encode()).hexdigest()
        history.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,history/f'{time.perf_counter_ns()}.{os.getpid()}.prior')
    temp = path.with_name(path.name + '.tmp.' + str(os.getpid()))
    temp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    os.replace(temp,path)

def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

class LimitReached(Exception): pass

def init_counter(path, cap):
    assert_open_batch()
    if not Path(path).resolve().is_relative_to(ROOT):raise AdmissionBlocked('COUNTER_OUTSIDE_AUTHORIZED_ROOT')
    if Path(path).resolve()==(ROOT/'visits.bin').resolve():
        raise AdmissionBlocked('GLOBAL_COUNTER_MUST_BE_EXTERNALLY_INITIALIZED_UNDER_NEW_GRANT')
    with open(path,'xb') as f: f.write(bytes(8)+struct.pack('<QQ',0,cap))

def count(path=None):
    with open(path or ROOT/'visits.bin','rb') as f:
        f.seek(8); return struct.unpack('<QQ',f.read(16))[0]

class Budget:
    def __init__(self, local=None):
        assert_open_batch()
        require_strict_bound_adapter()
        self.fd = os.open(ROOT/'visits.bin',os.O_RDWR|os.O_BINARY)
        _FD_PATHS[self.fd]=(ROOT/'visits.bin').resolve()
        self.local = os.open(local,os.O_RDWR|os.O_BINARY) if local else None
        if self.local is not None:_FD_PATHS[self.local]=Path(local).resolve()
        self.calls = 0
        self.deadline = read(ROOT/'BATCH_STATE.json')['deadline_monotonic_ns']
    @staticmethod
    def reserve(fd):
        state=assert_open_batch()
        os.lseek(fd,0,os.SEEK_SET)
        while True:
            try:msvcrt.locking(fd,msvcrt.LK_NBLCK,1);break
            except OSError as exc:
                if exc.errno not in (errno.EACCES,errno.EAGAIN,errno.EDEADLK):raise
                if time.perf_counter_ns()>=state['deadline_monotonic_ns']:raise LimitReached('WALL_LIMIT_DURING_COUNTER_LOCK')
                assert_guardian_alive();time.sleep(.005);os.lseek(fd,0,os.SEEK_SET)
        try:
            tag=hashlib.sha256(str(_FD_PATHS[fd]).encode()).hexdigest()
            pending=ROOT/'raw'/f'counter.{tag}.pending.json'
            if pending.exists() and read(pending)['status']!='COMMITTED':
                raise AdmissionBlocked('INCOMPLETE_RESERVATION: stop; never reclaim ambiguous credit')
            os.lseek(fd,8,os.SEEK_SET); raw=os.read(fd,16)
            if len(raw)!=16:raise AdmissionBlocked('TORN_COUNTER')
            used,cap=struct.unpack('<QQ',raw)
            if used>cap:raise AdmissionBlocked('COUNTER_OUT_OF_RANGE')
            if used >= cap: raise LimitReached('VISIT_LIMIT')
            record={'status':'PREPARED','counter':str(_FD_PATHS[fd]),'before':used,'after':used+1,
                    'cap':cap,'pid':os.getpid(),**stamp()}
            with open(ROOT/'raw'/f'counter.{tag}.journal.jsonl','a',encoding='utf-8') as log:
                log.write(json.dumps(record,sort_keys=True)+'\n');log.flush();os.fsync(log.fileno())
            durable_json(pending,record)
            os.lseek(fd,8,os.SEEK_SET)
            if os.write(fd,struct.pack('<Q',used+1))!=8:raise AdmissionBlocked('SHORT_COUNTER_WRITE')
            os.fsync(fd)
            record['status']='COMMITTED';durable_json(pending,record)
            with open(ROOT/'raw'/f'counter.{tag}.journal.jsonl','a',encoding='utf-8') as log:
                log.write(json.dumps(record,sort_keys=True)+'\n');log.flush();os.fsync(log.fileno())
        finally:
            os.lseek(fd,0,os.SEEK_SET); msvcrt.locking(fd,msvcrt.LK_UNLCK,1)
    def visit(self):
        assert_guardian_alive()
        if time.perf_counter_ns() >= self.deadline: raise LimitReached('WALL_LIMIT')
        self.reserve(self.fd)
        self.calls += 1
        if self.local is not None: self.reserve(self.local)
    def close(self):
        if self.fd is not None: _FD_PATHS.pop(self.fd,None);os.close(self.fd); self.fd=None
        if self.local is not None: _FD_PATHS.pop(self.local,None);os.close(self.local); self.local=None

def durable_json(path,data):
    """Reservation intent precedes counter update. Ambiguity poisons recovery."""
    assert_open_batch()
    path=Path(path).resolve()
    if not path.is_relative_to(ROOT):raise AdmissionBlocked('JOURNAL_OUTSIDE_AUTHORIZED_ROOT')
    temp=path.with_name(path.name+f'.{os.getpid()}.tmp')
    path.parent.mkdir(parents=True,exist_ok=True)
    with open(temp,'x',encoding='utf-8') as f:
        json.dump(data,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    os.replace(temp,path)

def process_identity(handle):
    before_status=wait_one(handle,0)
    if before_status==0xffffffff:raise OSError(ctypes.get_last_error(),'Process identity wait requires SYNCHRONIZE')
    values=[ctypes.c_ulonglong() for _ in range(4)]
    must(get_process_times(handle,*[ctypes.byref(x) for x in values]),'GetProcessTimes')
    return {'creation_FILETIME_100ns':values[0].value,
            'exit_FILETIME_100ns':values[1].value if before_status==0 else None,
            'exit_time_scope':'ExitTime is undefined while running; preserved only after pre-query exit signal'}

def system_memory_units():
    value=SYSTEM_INFO();get_system_info(ctypes.byref(value))
    page=value.PageSize
    if not page or page&(page-1):raise AdmissionBlocked('INVALID_SYSTEM_PAGE_SIZE')
    return {'page_size_bytes':page,'allocation_granularity_bytes':value.AllocationGranularity,
            'processor_architecture':value.ProcessorUnion&0xffff,'sample':stamp()}

def abi_contract():
    expected={'pointer':8,'BASIC':64,'IO':48,'EXT':144,'PMC':80,'SYSTEM_INFO':48}
    actual={'pointer':ctypes.sizeof(ctypes.c_void_p),'BASIC':ctypes.sizeof(BASIC),'IO':ctypes.sizeof(IO),
            'EXT':ctypes.sizeof(EXT),'PMC':ctypes.sizeof(PMC),'SYSTEM_INFO':ctypes.sizeof(SYSTEM_INFO)}
    if actual!=expected:raise AdmissionBlocked('ABI_LAYOUT_MISMATCH:'+repr(actual))
    return actual

def proc_memory(handle=None):
    before_query=stamp()
    m=PMC(); m.cb=ctypes.sizeof(m)
    must(P.GetProcessMemoryInfo(handle or get_current(),ctypes.byref(m),m.cb),'GetProcessMemoryInfo')
    after_query=stamp()
    return {'working_set':m.WS,'peak_working_set':m.PeakWS,'private_commit':m.Private,
            'peak_pagefile':m.PeakPagefile,'sdk_fields':{'WorkingSetSize':m.WS,'PeakWorkingSetSize':m.PeakWS,
             'PrivateUsage':m.Private,'PagefileUsage':m.Pagefile,'PeakPagefileUsage':m.PeakPagefile},
            'query_window':{'before':before_query,'after':after_query},'sample':stamp(),
            'process_identity':process_identity(handle or get_current()),
            'scope':'current values and historical process peaks are distinct; no peak reset is inferred'}

def ws_limit(handle, cap):
    abi_contract()
    before=proc_memory(handle)
    units=system_memory_units();minimum=20*units['page_size_bytes']
    if cap<minimum:raise AdmissionBlocked('WS_CAP_BELOW_DOCUMENTED_MINIMUM')
    must(set_ws(handle,minimum,cap,4),'SetProcessWorkingSetSizeEx(HARDWS_MAX_ENABLE)')
    lo,hi,flags=SZ(),SZ(),W.DWORD()
    must(get_ws(handle,ctypes.byref(lo),ctypes.byref(hi),ctypes.byref(flags)),'GetProcessWorkingSetSizeEx')
    if not(flags.value & 4) or hi.value > cap: raise RuntimeError('HARD_WORKING_SET_NOT_CONFIRMED')
    return {'min':lo.value,'max':hi.value,'flags':flags.value,'hard_max_enabled':True,
            'before_limit':before,'after_limit':proc_memory(handle),'applied_at':stamp(),'system_units':units}

class Job:
    def __init__(self, name=None, memory=4*GIB, ws=WS_CAP, active=4):
        assert_open_batch();abi_contract()
        require_strict_bound_adapter()
        self.instance=f'{os.getpid()}:{time.perf_counter_ns()}';self.name=name;self.created_at=stamp()
        ctypes.set_last_error(0)
        self.handle=create_job(None,name); must(self.handle,'CreateJobObjectW')
        if ctypes.get_last_error()==183:
            close_handle(self.handle);self.handle=None;raise RuntimeError('JOB_NAME_ALREADY_EXISTS')
        # Job fixes aggregate commit/active count. Per-process HARDWS flags are
        # separately applied before ResumeThread; JOB_LIMIT_WORKINGSET would
        # prohibit changing member working-set ranges (documented Win32 rule).
        e=EXT(); e.Basic.Flags=0x2000|0x200|0x8
        e.Basic.ActiveLimit=active
        e.JobMemory=memory
        if not set_job(self.handle,9,ctypes.byref(e),ctypes.sizeof(e)):
            err=ctypes.get_last_error()
            write(ROOT/'raw'/f'job_setup_error.{os.getpid()}.json',{'winerror':err,'basic_size':ctypes.sizeof(BASIC),
                'ext_size':ctypes.sizeof(EXT),'flags':e.Basic.Flags,'memory':memory,'active':active,
                'raw_struct_hex':bytes(e).hex()})
            raise OSError(err,'SetInformationJobObject')
        self.ws=ws
    def attach(self, hp):
        yes=W.BOOL(); must(in_job(hp,self.handle,ctypes.byref(yes)),'IsProcessInJob')
        if not yes.value: must(assign_job(self.handle,hp),'AssignProcessToJobObject')
    def info(self):
        before_query=stamp();length=W.DWORD();e=EXT()
        must(query_job(self.handle,9,ctypes.byref(e),ctypes.sizeof(e),ctypes.byref(length)),'QueryJobLimits')
        after_query=stamp()
        if length.value not in (0,ctypes.sizeof(e)):raise AdmissionBlocked('JOB_QUERY_LENGTH_MISMATCH')
        return {'flags':e.Basic.Flags,'active_limit':e.Basic.ActiveLimit,'max_working_set':e.Basic.MaxWS,
                'job_commit_limit':e.JobMemory,'reported_peak_job_memory_used':e.PeakJob,
                'reported_peak_process_memory_used':e.PeakProcess,'instance':self.instance,'job_name':self.name,
                'created_at':self.created_at,'sample':stamp(),'returned_length':length.value,
                'query_window':{'before':before_query,'after':after_query},
                'metric_note':'SDK JobMemoryLimit is a commit limit; peak accounting internals/reset/failure charging are unresolved'}
    def pids(self):
        capacity=4
        for _ in range(8):
            buf=ctypes.create_string_buffer(8+8*capacity)
            ok=query_job(self.handle,3,buf,len(buf),None)
            assigned,n=struct.unpack_from('<II',buf)
            if ok and n==assigned and n<=capacity:
                return list(struct.unpack_from('<'+'Q'*n,buf,8)) if n else []
            err=ctypes.get_last_error()
            if not ok and err!=234:raise OSError(err,'QueryJobPids')
            capacity=max(capacity*2,assigned)
        raise AdmissionBlocked('PROCESS_LIST_UNSTABLE_OR_TRUNCATED')
    def stop(self, code=124): must(terminate_job(self.handle,code),'TerminateJobObject')
    def close(self):
        if self.handle: close_handle(self.handle); self.handle=None

def process_alive(pid):
    hp=open_process(0x100000|0x1000,False,pid)
    if not hp:
        err=ctypes.get_last_error()
        if err==87:return False
        raise OSError(err,'OpenProcess: liveness is unknown, not certified dead')
    try: return wait_one(hp,0)==258
    finally: close_handle(hp)

def wait_dead(pid,seconds=2):
    until=time.perf_counter()+seconds
    while process_alive(pid):
        if time.perf_counter()>=until:return False
        time.sleep(.01)
    return True

def spawn(script,args,tag,job,ws=None,extra_job=None,breakaway=False):
    assert_open_batch();assert_guardian_alive()
    script=Path(script).resolve()
    if script.parent != (ROOT/'src').resolve(): raise RuntimeError('SCRIPT_OUTSIDE_LOCKED_SRC')
    out=ROOT/'raw'/f'{tag}.stdout.txt'; err=ROOT/'raw'/f'{tag}.stderr.txt'
    if any(ch not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-' for ch in tag):raise AdmissionBlocked('INVALID_LOG_TAG')
    files=[open(os.devnull,'rb'),open(out,'xb'),open(err,'xb')]
    handles=[msvcrt.get_osfhandle(f.fileno()) for f in files]
    for h in handles: os.set_handle_inheritable(h,True)
    si=subprocess.STARTUPINFO(); si.dwFlags|=subprocess.STARTF_USESTDHANDLES
    si.hStdInput,si.hStdOutput,si.hStdError=handles
    si.lpAttributeList={'handle_list':handles}
    cmd=[str(PYTHON),'-I','-S','-B',str(script),*map(str,args)]
    flags=0x4|0x08000000|(0x01000000 if breakaway else 0)
    hp=ht=None
    try:
        hp,ht,pid,tid=_winapi.CreateProcess(None,subprocess.list2cmdline(cmd),None,None,True,
            flags,os.environ.copy(),str(ROOT),si)
        job.attach(hp)
        if extra_job: extra_job.attach(hp)
        cap=ws_limit(hp,ws or job.ws)
        cap['before_resume']=proc_memory(hp)
        if resume_thread(ht)==0xffffffff: raise OSError(ctypes.get_last_error(),'ResumeThread')
        return Child(hp,pid,cmd,tag,cap,extra_job or job)
    except BaseException:
        if hp: _winapi.TerminateProcess(hp,126); _winapi.CloseHandle(hp)
        raise
    finally:
        if ht: _winapi.CloseHandle(ht)
        for h in handles: os.set_handle_inheritable(h,False)
        for f in files: f.close()

class Child:
    def __init__(self,hp,pid,cmd,tag,ws,job):
        self.hp,self.pid,self.cmd,self.tag,self.ws,self.job=hp,pid,cmd,tag,ws,job
        self.start=time.perf_counter(); self.last_memory=None;self.last_live_memory=None
    def wait(self,seconds,root_job=None):
        deadline=time.perf_counter()+seconds; timed=False; peak_sample=0;query_errors=[]
        while True:
            if _GUARDIAN is not None and self.hp!=_GUARDIAN:assert_guardian_alive()
            try: self.last_memory=proc_memory(self.hp)
            except OSError as exc:query_errors.append({'pid':self.pid,'error':repr(exc),**stamp()})
            if root_job:
                sample=0
                for pid in root_job.pids():
                    hp=open_process(0x100410,False,pid)
                    if hp:
                        try: sample+=proc_memory(hp)['working_set']
                        except OSError as exc:query_errors.append({'pid':pid,'error':repr(exc),**stamp()})
                        finally: close_handle(hp)
                    else:query_errors.append({'pid':pid,'error':'OpenProcess failed; sample incomplete',**stamp()})
                peak_sample=max(peak_sample,sample)
            observed=wait_one(self.hp,10)
            if observed==0: break
            if observed==0xffffffff:raise OSError(ctypes.get_last_error(),'WaitForSingleObject')
            self.last_live_memory=self.last_memory
            if time.perf_counter()>=deadline:
                timed=True; self.job.stop(124)
                if wait_one(self.hp,5000)!=0: raise RuntimeError('PROCESS_SURVIVED_JOB_TERMINATION')
                break
        code=W.DWORD(); must(exit_code(self.hp,ctypes.byref(code)),'GetExitCodeProcess')
        try: self.last_memory=proc_memory(self.hp)
        except OSError: pass
        result={'pid':self.pid,'command':self.cmd,'exit_code':code.value,'timeout':timed,
                'elapsed_seconds':time.perf_counter()-self.start,'hard_ws':self.ws,
                'last_live_memory':self.last_live_memory,'post_exit_memory':self.last_memory,
                'tree_ws_peak_sample_lower_bound':peak_sample,'query_errors':query_errors,
                'evidence_complete':self.last_live_memory is not None and not query_errors}
        write(ROOT/'raw'/f'{self.tag}.process.json',result)
        close_handle(self.hp); self.hp=None
        return result

def watchdog(args):
    assert_open_batch()
    name,event_name,parent_pid,deadline=args
    hj=open_job(0x8|0x4,False,name); must(hj,'OpenJobObjectW watchdog')
    he=open_event(0x100000,False,event_name); must(he,'OpenEventW watchdog')
    hp=open_process(0x100000,False,int(parent_pid)); must(hp,'OpenProcess parent')
    hs=(W.HANDLE*2)(he,hp)
    remaining=max(0,(int(deadline)-time.perf_counter_ns())//1000000)
    result=wait_many(2,hs,False,min(remaining,0xfffffffe))
    if result==0: return 0
    reason='WALL_LIMIT' if result==258 else ('GUARD_PARENT_EXIT' if result==1 else 'WATCHDOG_WAIT_ERROR')
    write(ROOT/'raw'/'WATCHDOG_STOP.json',{'reason':reason,'utc':time.time(),'monotonic_ns':time.perf_counter_ns()})
    must(terminate_job(hj,124),'watchdog TerminateJobObject')
    return 124

def classify_diagnostic(mode, result, payload):
    """No historical peak is relabelled current; inconclusive never admits F1/F4."""
    if result.get('timeout') and mode not in ('timeout','tree_timeout'):
        return {'status':'FAIL','reason':'unexpected timeout'}
    if mode=='normal':
        return {'status':'PASS' if result['exit_code']==0 and payload and payload.get('normal') else 'FAIL',
                'scope':'normal-exit evidence only'}
    if mode=='counter':
        good=result['exit_code']==0 and payload and payload.get('local_processed')==17 and payload.get('denied')
        return {'status':'PASS' if good else 'FAIL','scope':'local limit via same reserve function; aggregate account separate'}
    if mode in ('memory','memory_vm','working_set'):
        return {'status':'INCONCLUSIVE','reason':'time-window and OS-accounting diagnosis; no certified startup/tree bound',
                'observation':payload,'no_automatic_tolerance':True}
    return {'status':'INCONCLUSIVE','reason':'requires locked failure-matrix and kernel stop evidence'}

def calibrate(job,session):
    assert_open_batch();require_strict_bound_adapter()
    # This boundary is intentionally closed in the static candidate. The
    # diagnosis/failure matrix lives in CALIBRATION_RETRY_PLAN.md; no partial
    # success or editable input boolean can produce RESOURCE_GATE_PASS.
    raise AdmissionBlocked('V3_STATIC_ONLY_UNCALIBRATED')

def main():
    # Neither the closed historical batch nor an uninitialized copied directory
    # is a new execution grant. No counter or deadline is created by v3.
    assert_open_batch();abi_contract()
    require_strict_bound_adapter()
    raise AdmissionBlocked('NO_CERTIFIED_PLATFORM_ADAPTER_OR_RUNTIME_ADMISSION')

if __name__=='__main__':
    try: rc=main()
    except BaseException:
        traceback.print_exc();rc=2
    sys.stdout.flush();sys.stderr.flush();os._exit(rc)
