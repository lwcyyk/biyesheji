import sys, os, time, ctypes
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from guard import Budget, LimitReached, ROOT, Job, spawn, write, proc_memory, count, init_counter, stamp, api, K, EXT, query_job, open_job, close_handle, in_job, get_current, must, system_memory_units

def named_job_sample():
    if len(sys.argv)<4:return {'status':'JOB_NAME_NOT_PROVIDED','sample':stamp()}
    name=sys.argv[3];h=open_job(4,False,name);must(h,'OpenJobObject(query only)')
    try:
        member=ctypes.wintypes.BOOL();must(in_job(get_current(),h,ctypes.byref(member)),'probe IsProcessInJob')
        if not member.value:raise RuntimeError('QUERY_JOB_MEMBERSHIP_MISMATCH')
        e=EXT();must(query_job(h,9,ctypes.byref(e),ctypes.sizeof(e),None),'probe QueryJob')
        return {'job_name':name,'is_member':bool(member.value),'JobMemoryLimit':e.JobMemory,
                'PeakJobMemoryUsed':e.PeakJob,'PeakProcessMemoryUsed':e.PeakProcess,
                'sample':stamp(),'scope':'SDK raw fields; no failed-reservation explanation is assumed'}
    finally:close_handle(h)

def observation(label):
    return {'label':label,'process':proc_memory(),'job':named_job_sample(),'sample':stamp()}

def main():
    mode,path=sys.argv[1],Path(sys.argv[2]); b=Budget(); b.visit()
    if mode=='normal': write(path,{'normal':True,'memory':proc_memory()}); return 0
    if mode=='counter':
        local=path.with_suffix('.counter.bin'); init_counter(local,17); x=Budget(local)
        processed=0; denied=False
        try:
            for i in range(18): x.visit(); processed+=1
        except LimitReached: denied=True
        finally: x.close()
        write(path,{'local_processed':processed,'local_count':count(local),'denied':denied}); return 0
    if mode=='memory':
        chunks=[]; caught=False;samples=[observation('before_allocation')]
        try:
            for i in range(16):
                b.visit();samples.append(observation('before_chunk_'+str(i)))
                chunks.append(bytearray(16*1024**2));samples.append(observation('held_chunk_'+str(i)))
        except MemoryError:
            caught=True;samples.append(observation('python_MemoryError_while_held'))
        n=len(chunks);before_release=observation('before_release_while_all_chunks_held')
        chunks.clear();after_release=observation('after_release')
        write(path,{'memory_error':caught,'allocated_chunks':n,'held_bytes_before_release':n*16*1024**2,
            'samples':samples,'before_release':before_release,'after_release':after_release,
            'native_error_cause':'Python MemoryError does not authenticate a particular Win32 allocation failure'});return 0
    if mode=='memory_vm':
        allocate=api('VirtualAlloc',[ctypes.c_void_p,ctypes.c_size_t,ctypes.wintypes.DWORD,ctypes.wintypes.DWORD],ctypes.c_void_p)
        release=api('VirtualFree',[ctypes.c_void_p,ctypes.c_size_t,ctypes.wintypes.DWORD])
        maximum=128*1024**2;unit=1024**2;events=[]
        ctypes.set_last_error(0);base=allocate(None,maximum,0x2000,4);reserve_error=ctypes.get_last_error()
        if not base:
            write(path,{'reserve_failed':True,'last_error':reserve_error,'requested_virtual_bytes':maximum});return 0
        try:
            for offset in range(0,maximum,unit):
                b.visit();before=observation('before_commit_'+str(offset))
                ctypes.set_last_error(0);ptr=allocate(base+offset,unit,0x1000,4)
                native_error=ctypes.get_last_error()  # before any other Win32 call
                after=observation('after_commit_'+str(offset))
                events.append({'offset':offset,'requested_commit_bytes':unit,'success':bool(ptr),
                               'last_error':native_error,'before':before,'after':after})
                if not ptr:break
        finally:
            ctypes.set_last_error(0);freed=release(base,0,0x8000);free_error=ctypes.get_last_error()
        write(path,{'reserve_failed':False,'reserved_virtual_bytes':maximum,'commit_events':events,
                    'free_success':bool(freed),'free_error':free_error,'after_release':observation('after_native_release'),
                    'scope':'Bounded native allocation diagnosis only; commit was not explicitly page-touched'});return 0
    if mode=='working_set':
        before=observation('before_ws_allocation')
        data=bytearray(96*1024**2)
        allocated=observation('before_explicit_touch')
        units=system_memory_units();page=units['page_size_bytes']
        touched=0
        for i in range(0,len(data),page):b.visit();data[i]=37;touched+=page
        held=observation('ws_while_held');del data
        write(path,{'touched_bytes':touched,'system_units':units,'before':before,
                    'allocated':allocated,'held':held,'after_release':observation('ws_released'),
                    'qualification':'UNQUALIFIED until page size/startup envelope and full failure matrix are bound'});return 0
    if mode=='abnormal': write(path,{'marker':'before_abnormal_exit'}); return 23
    if mode=='containment':
        j=Job(memory=192*1024**2)
        try:
            try:
                child=spawn(ROOT/'src'/'guard_probe.py',['timeout',str(path.with_suffix('.escape.json'))],path.stem+'.escape',j,breakaway=True)
            except OSError as e:
                write(path,{'breakaway_denied':True,'winerror':e.errno});return 0
            j.stop(126);child.wait(2)
            write(path,{'breakaway_denied':False});return 0
        finally:j.close()
    if mode=='timeout': write(path,{'marker':'before_timeout'}); time.sleep(20); return 9
    if mode in ('tree_timeout','parent_exit'):
        # Nested holder job: OS closes its last noninherited handle on holder exit.
        j=Job(memory=192*1024**2)
        child=spawn(ROOT/'src'/'guard_probe.py',['timeout',str(path.with_suffix('.child.json'))],path.stem+'.child',j)
        write(path,{'child_pid':child.pid,'holder_pid':os.getpid(),'marker':'child_started'})
        if mode=='parent_exit': return 23
        time.sleep(20); return 9
    raise ValueError(mode)

if __name__=='__main__':
    rc=main(); sys.stdout.flush(); sys.stderr.flush(); os._exit(rc)
