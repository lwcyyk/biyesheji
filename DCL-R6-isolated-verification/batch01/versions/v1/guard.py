"""Windows-only R6 resource guard. No model semantics are implemented here."""
import os, sys, json, time, struct, hashlib, traceback, ctypes, subprocess
from pathlib import Path
from ctypes import wintypes as W
import msvcrt, _winapi

ROOT = Path(__file__).resolve().parent.parent
PYTHON = Path(r'C:\Program Files\Python314\python.exe')
GIB = 1024 ** 3
WS_CAP = 768 * 1024 ** 2
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
P.GetProcessMemoryInfo.argtypes = [W.HANDLE,ctypes.c_void_p,W.DWORD]
P.GetProcessMemoryInfo.restype = W.BOOL

def must(ok, action):
    if not ok: raise OSError(ctypes.get_last_error(), action)

def write(path, data):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.tmp.' + str(os.getpid()))
    temp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    os.replace(temp,path)

def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

class LimitReached(Exception): pass

def init_counter(path, cap):
    with open(path,'xb') as f: f.write(bytes(8)+struct.pack('<QQ',0,cap))

def count(path=None):
    with open(path or ROOT/'visits.bin','rb') as f:
        f.seek(8); return struct.unpack('<QQ',f.read(16))[0]

class Budget:
    def __init__(self, local=None):
        self.fd = os.open(ROOT/'visits.bin',os.O_RDWR|os.O_BINARY)
        self.local = os.open(local,os.O_RDWR|os.O_BINARY) if local else None
        self.calls = 0
        self.deadline = read(ROOT/'BATCH_STATE.json')['deadline_monotonic_ns']
    @staticmethod
    def reserve(fd):
        os.lseek(fd,0,os.SEEK_SET); msvcrt.locking(fd,msvcrt.LK_LOCK,1)
        try:
            os.lseek(fd,8,os.SEEK_SET); used,cap=struct.unpack('<QQ',os.read(fd,16))
            if used >= cap: raise LimitReached('VISIT_LIMIT')
            os.lseek(fd,8,os.SEEK_SET); os.write(fd,struct.pack('<Q',used+1))
        finally:
            os.lseek(fd,0,os.SEEK_SET); msvcrt.locking(fd,msvcrt.LK_UNLCK,1)
    def visit(self):
        if time.perf_counter_ns() >= self.deadline: raise LimitReached('WALL_LIMIT')
        self.reserve(self.fd)
        self.calls += 1
        if self.local is not None: self.reserve(self.local)
    def close(self):
        if self.fd is not None: os.close(self.fd); self.fd=None
        if self.local is not None: os.close(self.local); self.local=None

def proc_memory(handle=None):
    m=PMC(); m.cb=ctypes.sizeof(m)
    must(P.GetProcessMemoryInfo(handle or get_current(),ctypes.byref(m),m.cb),'GetProcessMemoryInfo')
    return {'working_set':m.WS,'peak_working_set':m.PeakWS,'private_commit':m.Private,
            'peak_pagefile':m.PeakPagefile}

def ws_limit(handle, cap):
    must(set_ws(handle,65536,cap,4),'SetProcessWorkingSetSizeEx(HARDWS_MAX_ENABLE)')
    lo,hi,flags=SZ(),SZ(),W.DWORD()
    must(get_ws(handle,ctypes.byref(lo),ctypes.byref(hi),ctypes.byref(flags)),'GetProcessWorkingSetSizeEx')
    if not(flags.value & 4) or hi.value > cap: raise RuntimeError('HARD_WORKING_SET_NOT_CONFIRMED')
    return {'min':lo.value,'max':hi.value,'flags':flags.value,'hard_max_enabled':True}

class Job:
    def __init__(self, name=None, memory=4*GIB, ws=WS_CAP, active=4):
        ctypes.set_last_error(0)
        self.handle=create_job(None,name); must(self.handle,'CreateJobObjectW')
        if ctypes.get_last_error()==183: raise RuntimeError('JOB_NAME_ALREADY_EXISTS')
        e=EXT(); e.Basic.Flags=0x2000|0x200|0x8|0x1
        e.Basic.MinWS=65536; e.Basic.MaxWS=ws; e.Basic.ActiveLimit=active
        e.JobMemory=memory
        must(set_job(self.handle,9,ctypes.byref(e),ctypes.sizeof(e)),'SetInformationJobObject')
        self.ws=ws
    def attach(self, hp):
        yes=W.BOOL(); must(in_job(hp,self.handle,ctypes.byref(yes)),'IsProcessInJob')
        if not yes.value: must(assign_job(self.handle,hp),'AssignProcessToJobObject')
    def info(self):
        e=EXT(); must(query_job(self.handle,9,ctypes.byref(e),ctypes.sizeof(e),None),'QueryJobLimits')
        return {'flags':e.Basic.Flags,'active_limit':e.Basic.ActiveLimit,'max_working_set':e.Basic.MaxWS,
                'job_commit_limit':e.JobMemory,'job_peak_commit':e.PeakJob,'process_peak_commit':e.PeakProcess}
    def pids(self):
        buf=ctypes.create_string_buffer(8+8*8)
        must(query_job(self.handle,3,buf,len(buf),None),'QueryJobPids')
        n=struct.unpack_from('<II',buf)[1]
        return list(struct.unpack_from('<'+'Q'*n,buf,8)) if n else []
    def stop(self, code=124): must(terminate_job(self.handle,code),'TerminateJobObject')
    def close(self):
        if self.handle: close_handle(self.handle); self.handle=None

def process_alive(pid):
    hp=open_process(0x100000|0x1000,False,pid)
    if not hp: return False
    try: return wait_one(hp,0)==258
    finally: close_handle(hp)

def wait_dead(pid,seconds=2):
    until=time.perf_counter()+seconds
    while process_alive(pid):
        if time.perf_counter()>=until:return False
        time.sleep(.01)
    return True

def spawn(script,args,tag,job,ws=None,extra_job=None,breakaway=False):
    script=Path(script).resolve()
    if script.parent != (ROOT/'src').resolve(): raise RuntimeError('SCRIPT_OUTSIDE_LOCKED_SRC')
    out=ROOT/'raw'/f'{tag}.stdout.txt'; err=ROOT/'raw'/f'{tag}.stderr.txt'
    files=[open(os.devnull,'rb'),open(out,'wb'),open(err,'wb')]
    handles=[msvcrt.get_osfhandle(f.fileno()) for f in files]
    for h in handles: os.set_handle_inheritable(h,True)
    si=subprocess.STARTUPINFO(); si.dwFlags|=subprocess.STARTF_USESTDHANDLES
    si.hStdInput,si.hStdOutput,si.hStdError=handles
    si.lpAttributeList={'handle_list':handles}
    cmd=[str(PYTHON),'-I','-B',str(script),*map(str,args)]
    flags=0x4|0x08000000|(0x01000000 if breakaway else 0)
    hp=ht=None
    try:
        hp,ht,pid,tid=_winapi.CreateProcess(None,subprocess.list2cmdline(cmd),None,None,True,
            flags,os.environ.copy(),str(ROOT),si)
        job.attach(hp)
        if extra_job: extra_job.attach(hp)
        cap=ws_limit(hp,ws or job.ws)
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
        self.start=time.perf_counter(); self.last_memory=None
    def wait(self,seconds,root_job=None):
        deadline=time.perf_counter()+seconds; timed=False; peak_sample=0
        while True:
            try: self.last_memory=proc_memory(self.hp)
            except OSError: pass
            if root_job:
                sample=0
                for pid in root_job.pids():
                    hp=open_process(0x410,False,pid)
                    if hp:
                        try: sample+=proc_memory(hp)['working_set']
                        except OSError: pass
                        finally: close_handle(hp)
                peak_sample=max(peak_sample,sample)
            if wait_one(self.hp,10)==0: break
            if time.perf_counter()>=deadline:
                timed=True; self.job.stop(124)
                if wait_one(self.hp,5000)!=0: raise RuntimeError('PROCESS_SURVIVED_JOB_TERMINATION')
                break
        code=W.DWORD(); must(exit_code(self.hp,ctypes.byref(code)),'GetExitCodeProcess')
        try: self.last_memory=proc_memory(self.hp)
        except OSError: pass
        result={'pid':self.pid,'command':self.cmd,'exit_code':code.value,'timeout':timed,
                'elapsed_seconds':time.perf_counter()-self.start,'hard_ws':self.ws,
                'process_memory':self.last_memory,'tree_ws_peak_sample_lower_bound':peak_sample}
        write(ROOT/'raw'/f'{self.tag}.process.json',result)
        close_handle(self.hp); self.hp=None
        return result

def watchdog(args):
    name,event_name,parent_pid,deadline=args
    hj=open_job(0x8|0x4,False,name); must(hj,'OpenJobObjectW watchdog')
    he=open_event(0x100000,False,event_name); must(he,'OpenEventW watchdog')
    hp=open_process(0x100000,False,int(parent_pid)); must(hp,'OpenProcess parent')
    hs=(W.HANDLE*2)(he,hp)
    remaining=max(0,(int(deadline)-time.perf_counter_ns())//1000000)
    result=wait_many(2,hs,False,min(remaining,0xfffffffe))
    if result==0: return 0
    reason='WALL_LIMIT' if result==258 else 'GUARD_PARENT_EXIT'
    write(ROOT/'raw'/'WATCHDOG_STOP.json',{'reason':reason,'utc':time.time(),'monotonic_ns':time.perf_counter_ns()})
    must(terminate_job(hj,124),'watchdog TerminateJobObject')
    return 124

def calibrate(job,session):
    cases=[]
    specs=[('normal',5,None),('counter',5,None),('memory',10,96*1024**2),
           ('working_set',15,192*1024**2),('abnormal',5,None),
           ('timeout',1,None),('tree_timeout',1.5,None),('parent_exit',5,None),('containment',5,None)]
    for i,(mode,timeout,mem) in enumerate(specs):
        tag=f'{session}.probe.{i}.{mode}'
        sub=Job(memory=mem or 512*1024**2,ws=32*1024**2 if mode in ('memory','working_set') else WS_CAP)
        result_path=ROOT/'calibration'/f'{tag}.json'
        try:
            ch=spawn(ROOT/'src'/'guard_probe.py',[mode,str(result_path)],tag,job,
                     ws=sub.ws,extra_job=sub)
            result=ch.wait(timeout,root_job=job); result['job']=sub.info()
            payload=read(result_path) if result_path.exists() else None
            result['probe']=payload; result['case']=mode
            if mode in ('timeout','tree_timeout'):
                ok=result['timeout'] and result['exit_code']==124
                if mode=='tree_timeout':
                    ok=ok and payload and wait_dead(payload['child_pid'])
                    ok=bool(ok)
            elif mode=='abnormal': ok=result['exit_code']==23 and payload and payload.get('marker')=='before_abnormal_exit'
            elif mode=='parent_exit': ok=result['exit_code']==23 and payload and wait_dead(payload['child_pid'])
            elif mode=='containment': ok=result['exit_code']==0 and payload and payload['breakaway_denied']
            elif mode=='memory': ok=result['exit_code']==0 and payload and payload.get('memory_error') is True and result['job']['job_peak_commit']<=mem
            elif mode=='working_set':
                ok=result['exit_code']==0 and payload and payload['touched_bytes']>=96*1024**2 and payload['memory']['peak_working_set']<=32*1024**2
            elif mode=='counter': ok=result['exit_code']==0 and payload and payload['local_processed']==17 and payload['local_count']==17 and payload['denied']
            else: ok=result['exit_code']==0 and payload and payload['normal']
            result['pass']=bool(ok); cases.append(result)
            write(ROOT/'reports'/f'RESOURCE_CALIBRATION.{session}.json',{'status':'RUNNING','cases':cases})
            if not ok: return {'status':'RESOURCE_GATE_FAILED','failed_case':mode,'cases':cases}
        except BaseException as exc:
            cases.append({'case':mode,'pass':False,'error':repr(exc),'traceback':traceback.format_exc()})
            return {'status':'RESOURCE_GATE_FAILED','failed_case':mode,'cases':cases}
        finally: sub.close()
    return {'status':'RESOURCE_GATE_PASS','cases':cases}

def main():
    if len(sys.argv)>1 and sys.argv[1]=='--watchdog': return watchdog(sys.argv[2:])
    if '--plan' not in sys.argv or '--qualify-first' not in sys.argv:raise RuntimeError('LOCKED_PLAN_AND_QUALIFICATION_REQUIRED')
    plan_path=(ROOT/sys.argv[sys.argv.index('--plan')+1]).resolve()
    if plan_path!=ROOT/'inputs'/'batch01.json':raise RuntimeError('PLAN_OUTSIDE_APPROVED_LOCATION')
    plan=read(plan_path)
    if plan['limits']!={'visits':1000000,'wall_seconds':1800,'process_tree_peak_bytes':4*GIB}:raise RuntimeError('LIMIT_MISMATCH')
    started=time.perf_counter_ns()
    state_path=ROOT/'BATCH_STATE.json'
    if state_path.exists():
        state=read(state_path); session=state['sessions']+1; state['sessions']=session
    else:
        state={'start_utc':time.time(),'start_monotonic_ns':started,'deadline_monotonic_ns':started+1800*10**9,'sessions':1}
        session=1; init_counter(ROOT/'visits.bin',1000000)
    write(state_path,state)
    if started>=state['deadline_monotonic_ns']:
        write(ROOT/'reports'/f'BATCH.{session}.json',{'status':'INCONCLUSIVE_LIMIT','reason':'previous_deadline_expired','visits':count()}); return 124
    job=Job(name=f'DCL_R6_B01_{os.getpid()}')
    job.attach(get_current()); hard=ws_limit(get_current(),WS_CAP)
    info=job.info()
    if info['active_limit']*hard['max']>4*GIB: raise RuntimeError('TREE_WS_BOUND_NOT_ENFORCED')
    event_name=f'DCL_R6_B01_STOP_{os.getpid()}'
    he=create_event(None,True,False,event_name); must(he,'CreateEvent')
    watch=spawn(ROOT/'src'/'guard.py',['--watchdog',f'DCL_R6_B01_{os.getpid()}',event_name,os.getpid(),state['deadline_monotonic_ns']],f's{session}.watchdog',job)
    report={'session':session,'start':state,'command':sys.argv,'runtime':sys.version,'os':sys.getwindowsversion()._asdict() if hasattr(sys.getwindowsversion(),'_asdict') else str(sys.getwindowsversion()),
            'job_limits':info,'controller_hard_ws':hard,'enforced_tree_ws_upper_bound':info['active_limit']*hard['max'],
            'exact_tree_ws_peak':None,'tree_ws_metric_note':'Hard per-process WS times kernel active-process limit is enforcement; sampled aggregate is only a lower bound.'}
    code=1
    try:
        lock=read(ROOT/'BATCH_LOCK.json')
        for row in lock['files']:
            if digest(ROOT/row['relative'])!=row['sha256']: raise RuntimeError('BATCH_LOCK_MISMATCH:'+row['relative'])
        cal=calibrate(job,f's{session}')
        write(ROOT/'reports'/f'RESOURCE_CALIBRATION.s{session}.json',cal); report['resource_gate']=cal['status']
        if cal['status']!='RESOURCE_GATE_PASS':
            report['status']='RESOURCE_GATE_FAILED'; code=2
        else:
            remaining=(state['deadline_monotonic_ns']-time.perf_counter_ns())/1e9-3
            sub=Job(memory=4*GIB,ws=WS_CAP)
            try:
                ch=spawn(ROOT/'src'/'run_batch.py',['--session',str(session)],f's{session}.models',job,extra_job=sub)
                result=ch.wait(max(0,remaining),root_job=job)
                report['model_process']=result
                report['status']='FINISHED' if result['exit_code']==0 else ('INCONCLUSIVE_LIMIT' if result['timeout'] or result['exit_code']==124 else 'MODEL_ERROR')
                code=0 if result['exit_code']==0 else 3
            finally: sub.close()
    except BaseException as exc:
        report['status']='RESOURCE_GATE_FAILED' if 'resource_gate' not in report else 'MODEL_ERROR'
        report['error']=repr(exc); report['traceback']=traceback.format_exc(); code=2
    finally:
        report.update({'end_utc':time.time(),'elapsed_total_seconds':(time.perf_counter_ns()-state['start_monotonic_ns'])/1e9,
                       'visits_started_upper_bound':count(),'job_end':job.info(),'controller_memory':proc_memory()})
        write(ROOT/'reports'/f'BATCH.{session}.json',report)
        must(signal_event(he),'signal normal watchdog stop')
        watch_result=watch.wait(2)
        write(ROOT/'reports'/f'BATCH.{session}.watchdog.json',watch_result)
    # Root job handle deliberately remains open until process exit (kill-on-close).
    return code

if __name__=='__main__':
    try: rc=main()
    except BaseException:
        traceback.print_exc(); rc=2
    sys.stdout.flush(); sys.stderr.flush(); os._exit(rc)
