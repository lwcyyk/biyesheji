"""Frozen C00-C12 Linux resource probes. Static BudgetFix delivery, never run in LC.

Probe child loops use explicit parent-prepaid operation bounds. Business
modules are never imported here. No production credentials or network target.
"""
import argparse
import errno
import json
import mmap
import os
from pathlib import Path
import resource
import signal
import socket
import subprocess
import sys
import threading
import time
sys.path.insert(0,str(Path(__file__).resolve().parent))
import guard as G

def record(case,**kw):
    return {'case':case,'category':'RESOURCE_CALIBRATION','actual':kw,'sample':G.stamp()}
def mark(case,**kw): G.write(G.OUT/(case+'.ready.json'),{'case':case,**kw,**G.stamp()})
def prepaid_child(case,budget,operations):
    task_id={'C02':'C02.memory.v1','C03':'C03.shared.v1','C04':'C04.fifth-task.v1'}[case]
    reservation=budget.reserve_exact(task_id,operations)
    fact=reservation.dispatch_once()
    path=G.OUT/(case+'.child.json')
    argv=[G.PYTHON,'-I','-S','-B',str(G.SOURCE/'guard_probe.py'),'--batch-root',str(G.ROOT),
          '--child',case,'--output',str(path),'--prepaid',str(operations),
          '--task-id',task_id,'--lease-id',fact['lease_id']]
    G.execution_deadline(case)
    started=G.stamp();started_mono_ns=G.monotonic_ns()
    G.timing_event('child.spawn_request')
    r=subprocess.run(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                     timeout=max(.1,min(240,G._TICKET['case_deadline']-G.now())),check=False)
    exited=G.stamp();exited_mono_ns=G.monotonic_ns();G.timing_event('child.wait_return')
    G.write(G.OUT/(case+'.child_process.json'),{'argv':argv,'exit_code':r.returncode,
        'stdout':r.stdout.decode(errors='replace'),'stderr':r.stderr.decode(errors='replace'),
        'prepaid_operations':operations,'reservation_fact':fact,'spawn_request':started,
        'wait_return':exited,'observed_process_span_ns':exited_mono_ns-started_mono_ns,
        'exit_time_scope':'wait-return observation; exact kernel exit instruction is unobserved','sample':G.stamp()})
    if r.returncode!=0 or not path.exists(): raise G.AdmissionBlocked('CHILD_PROBE_FAILED')
    result=G.read(path)
    if not(0<=result['operations']<=result['credit_used']<=operations) or result['lease_id']!=fact['lease_id']:
        raise G.AdmissionBlocked('CHILD_PREPAID_BOUND_EXCEEDED_OR_IDENTITY_CHANGED')
    return result
def child(case,output,prepaid,task_id,lease_id):
    t=G.ticket(case);G.kernel_admission(t)
    if os.getppid()!=t['main_identity']['pid'] or G.identity(os.getppid())!=t['main_identity']:
        raise G.AdmissionBlocked('PROBE_PARENT_MISMATCH')
    credits=G.claim_exact(task_id,prepaid,lease_id)
    operations=0; data={}; ok=False
    if case=='C02':
        page=os.sysconf('SC_PAGE_SIZE'); bound=128*(1+(1024*1024)//page)
        if prepaid!=bound: raise G.AdmissionBlocked('WRONG_MEMORY_PRECHARGE')
        resource.setrlimit(resource.RLIMIT_AS,(96*1024**2,96*1024**2))
        chunks=[]; failed=False; samples=[]
        try:
            for _ in range(128):
                credits.visit();operations+=1; block=bytearray(1024*1024)
                for j in range(0,len(block),page): credits.visit();operations+=1;block[j]=37
                chunks.append(block)
                samples.append(G.proc_memory())
        except MemoryError: failed=True
        held=G.proc_memory(); n=len(chunks); chunks.clear()
        data={'memory_error':failed,'successful_chunks':n,'held':held,'released':G.proc_memory(),
              'samples_while_held':samples,'cause':'AS exhaustion candidate; MemoryError alone is not a unique cause proof'}
        ok=failed and resource.getrlimit(resource.RLIMIT_AS)==(96*1024**2,96*1024**2)
    elif case=='C03':
        size=16*1024**2; page=os.sysconf('SC_PAGE_SIZE')
        if prepaid!=size//page: raise G.AdmissionBlocked('WRONG_SHARED_PRECHARGE')
        with (G.OUT/'C03.shared').open('r+b') as f, mmap.mmap(f.fileno(),size) as m:
            for j in range(0,size,page): credits.visit();operations+=1;m[j]=43
            data={'held':G.proc_memory(),'maps':G.mapping_snapshot(),'first_byte':m[0]}
            ok=m[0]==43
    elif case=='C04':
        before=G.cg_snapshot(Path('/sys/fs/cgroup')/G.PARENT)
        denied=False; error=None;credits.visit();operations=1
        try:
            p=subprocess.Popen([G.PYTHON,'--version'],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        except OSError as exc: denied=exc.errno==errno.EAGAIN;error=repr(exc)
        else: p.kill();p.communicate()
        after=G.cg_snapshot(Path('/sys/fs/cgroup')/G.PARENT)
        def event(x): return int(dict(line.split() for line in x['values']['pids.events'].splitlines()).get('max','0'))
        ok=denied and event(after)>event(before)
        data={'fifth_task_denied_EAGAIN':denied,'error':error,'before':before,'after':after,
              'rlimit_nproc':list(resource.getrlimit(resource.RLIMIT_NPROC))}
    else: raise ValueError(case)
    G.write(output,{'status':'PASS' if ok else 'FAIL','case':case,'operations':operations,
        'task_id':task_id,'lease_id':lease_id,'credit_total':credits.N,'credit_used':credits.used,
        'unused_burned':credits.N-credits.used,'debited_but_not_observed_operations':credits.used-operations,
        'actual':data,'timing':G.timing_snapshot(),'sample':G.stamp()})
    credits.close()
    return 0 if ok else 65

def run_case(case,budget):
    budget.visit(); result=record(case); ok=False
    if case=='C00':
        facts=G.kernel_admission(G._TICKET); maps=G.mapping_snapshot()
        # Kernel-provided special VMAs are always reported separately. Their
        # scope must be explicitly accepted in the future root authorization.
        ok=not maps['unreviewed_special_flags']
        result['actual']={'facts':facts,'maps':maps,'conditional_proof':'AS4-PAYLOAD/1 ordinary AS-accounted mappings only',
                          'special_scope':'KERNEL_SPECIALS_REQUIRE_EXPLICIT_REVIEW; not a Windows WS proof'}
    elif case=='C01':
        result['actual']={'watchdog_identity':G.identity(G._WATCH.pid),'self':G.proc_memory(),'group':G.cg_snapshot()};ok=True
    elif case=='C02':
        page=os.sysconf('SC_PAGE_SIZE');result['actual']=prepaid_child(case,budget,128*(1+(1024*1024)//page))
        ok=result['actual']['status']=='PASS'
    elif case=='C03':
        path=G.OUT/'C03.shared'
        fd=os.open(path,os.O_RDWR|os.O_CREAT|os.O_EXCL,0o600);os.ftruncate(fd,16*1024**2)
        try:
            with mmap.mmap(fd,16*1024**2) as parent_map:
                r=prepaid_child(case,budget,16*1024**2//os.sysconf('SC_PAGE_SIZE'))
                result['actual']={'child':r,'parent_held':G.proc_memory(),'visible_shared_value':parent_map[0]}
                ok=r['status']=='PASS' and parent_map[0]==43
        finally: os.close(fd)
    elif case=='C04':
        result['actual']=prepaid_child(case,budget,1);ok=result['actual']['status']=='PASS'
    elif case=='C05':
        path=G.OUT/'C05.local.bin';G.init_counter(path,17)
        lock=threading.Lock(); stats={'processed':0,'denied':0};errors=[]
        def work(n):
            b=G.Budget(path)
            try:
                for _ in range(n):
                    try: b.visit()
                    except G.LimitReached:
                        with lock: stats['denied']+=1
                    else:
                        with lock: stats['processed']+=1
            except BaseException as exc: errors.append(repr(exc))
            finally: b.close()
        t=threading.Thread(target=work,args=(9,));t.start();work(9);t.join()
        result['actual']={**stats,'local_counter':G.count(path),'errors':errors}
        ok=stats=={'processed':17,'denied':1} and G.count(path)==17 and not errors
    elif case=='C06':
        mark(case,case_deadline=G._TICKET['case_deadline'],counter=G.count())
        time.sleep(20);result['actual']={'unexpected_return':True};ok=False
    elif case=='C07':
        mark(case,counter=G.count(),identity=G.identity());os._exit(23)
    elif case=='C08':
        mark(case,counter=G.count(),watchdog=G.identity(G._WATCH.pid))
        fd=os.pidfd_open(G._WATCH.pid)
        signal.pidfd_send_signal(fd,signal.SIGKILL);os.close(fd)
        G._WATCH.wait(timeout=3)
        try: budget.visit()
        except G.AdmissionBlocked as exc: ok=str(exc)=='WATCHDOG_NOT_ALIVE' and G._WATCH.poll() is not None
        result['actual']={'grant_after_watchdog_death_denied':ok,'watchdog_exit':G._WATCH.returncode}
    elif case=='C09':
        mark(case,counter=G.count(),identity=G.identity())
        while True: time.sleep(.1)  # actual external launcher crash/stop test
    elif case=='C10':
        findings={}
        try: resource.setrlimit(resource.RLIMIT_AS,(G.AS_CAP+4096,G.AS_CAP+4096))
        except ValueError as exc: findings['raise_as_denied']=repr(exc)
        except OSError as exc: findings['raise_as_denied']=repr(exc) if exc.errno in (errno.EPERM,errno.EACCES) else False
        else: findings['raise_as_denied']=False
        for name,path in (('cgroup_write',Path('/sys/fs/cgroup')/G.PARENT/'cgroup.procs'),
                          ('manager_socket',Path('/run/systemd/private'))):
            try:
                if name=='cgroup_write': fd=os.open(path,os.O_WRONLY);os.close(fd)
                else:
                    sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
                    try: sock.connect(str(path))
                    finally: sock.close()
            except OSError as exc:
                findings[name+'_denied']=repr(exc) if exc.errno in (errno.EACCES,errno.EPERM,errno.EROFS,errno.ENOENT) else False
            else: findings[name+'_denied']=False
        try: sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        except OSError as exc:
            findings['inet_family_denied']=repr(exc) if exc.errno in (errno.EAFNOSUPPORT,errno.EPROTONOSUPPORT,errno.EPERM,errno.EACCES) else False
        else: sock.close();findings['inet_family_denied']=False
        result['actual']=findings;ok=all(findings.values())
    elif case=='C11':
        rows=[]
        for fault in ('prepared','short_write','counter_fsynced','journal_fsynced'):
            budget.visit();p=G.OUT/('C11.'+fault+'.bin');G.init_counter(p,17);caught=None;poisoned=False
            try: G.reserve_counter(p,17,fault=fault)
            except (OSError,G.AdmissionBlocked) as exc: caught=repr(exc)
            try: G.reserve_counter(p,17)
            except G.AdmissionBlocked: poisoned=True
            rows.append({'fault':fault,'caught':caught,'ambiguous_credit_refused':poisoned})
        result['actual']={'local_mirror_faults':rows,'global_ledger_untouched_by_injection':True}
        expected={'prepared':'INJECTED_AFTER_PREPARED','short_write':'SHORT_COUNTER_WRITE',
                  'counter_fsynced':'INJECTED_AFTER_COUNTER_FSYNC','journal_fsynced':'INJECTED_BEFORE_COMMITTED_INTENT'}
        ok=all(r['caught'] and expected[r['fault']] in r['caught'] and r['ambiguous_credit_refused'] for r in rows)
    elif case=='C12':
        s=G.state();mismatch_checks=[]
        bad_boot={**s,'boot_id':'invalid-local-fixture'}
        expired={**s,'deadline':G.now()-1}
        closed={**s,'status':'CLOSED'}
        checks=(('boot_id',lambda:G.validate_state_document(bad_boot)),
                ('past_deadline',lambda:G.validate_state_document(expired)),
                ('closed',lambda:G.validate_state_document(closed)),
                ('root_scope',lambda:G.validate_root('/tmp/other')),
                ('global_counter_reinitialize',lambda:G.init_counter(G.OUT/'visits.bin',G.VISIT_CAP)),
                ('standalone_formal_admission',G.require_formal_admission))
        expected={'boot_id':'BOOT_ID_MISMATCH','past_deadline':'ABSOLUTE_WALL_LIMIT','closed':'BATCH_CLOSED',
                  'root_scope':'UNAPPROVED_ROOT','global_counter_reinitialize':'ROOT_INITIALIZATION_REQUIRED',
                  'standalone_formal_admission':'CONTROLLER_CONTEXT_REQUIRED'}
        for name,fn in checks:
            budget.visit();denied=False;error=None
            try: fn()
            except (G.AdmissionBlocked,G.LimitReached) as exc: error=str(exc);denied=error==expected[name]
            mismatch_checks.append({'kind':name,'rejected':denied,'error':error})
        result['actual']={'identity_predicates':mismatch_checks,'real_state_not_modified':True,
                          'restart_cleanup':'root coordinator separately confirms each whole group empty'}
        ok=all(r['rejected'] for r in mismatch_checks)
    else: raise ValueError(case)
    result['status']='PASS' if ok else 'FAIL'
    result['actual']['counter_upper_bound']=G.count()
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--batch-root',required=True)
    p.add_argument('--child',choices=('C02','C03','C04'),required=True)
    p.add_argument('--output',required=True);p.add_argument('--prepaid',type=int,required=True)
    p.add_argument('--task-id',required=True);p.add_argument('--lease-id',required=True)
    a=p.parse_args();return child(a.child,G._inside(a.output,G.OUT),a.prepaid,a.task_id,a.lease_id)
if __name__=='__main__':
    try: code=main()
    except BaseException as exc: print(repr(exc),file=sys.stderr);code=65
    sys.exit(code)
