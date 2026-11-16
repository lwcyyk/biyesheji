import sys, os, time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from guard import Budget, LimitReached, ROOT, Job, spawn, write, proc_memory, count, init_counter

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
        chunks=[]; caught=False
        try:
            for i in range(16): b.visit(); chunks.append(bytearray(16*1024**2))
        except MemoryError: caught=True
        n=len(chunks); chunks.clear()
        write(path,{'memory_error':caught,'allocated_chunks':n,'memory':proc_memory()}); return 0
    if mode=='working_set':
        data=bytearray(96*1024**2)
        for i in range(0,len(data),4096): data[i]=37
        b.visit(); write(path,{'touched_bytes':len(data),'memory':proc_memory()}); return 0
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
