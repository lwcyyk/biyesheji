"""Frozen Root-only IPC fixtures; invocation is gated by a future batch06 receipt."""
import errno
import hashlib
import json
import os
from pathlib import Path
import resource
import select
import signal
import socket
import stat
import time
import root_ipc as R


def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def metadata(p):
    try:
        s=os.lstat(p)
        return {'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode),
                'inode':s.st_ino,'device':s.st_dev,'nlink':s.st_nlink,'regular':stat.S_ISREG(s.st_mode)}
    except FileNotFoundError:return None


def probe(G,path,uid,write=False):
    # One short-lived extra TCB child, sequential, with its own timer and AS limit.
    read_fd,write_fd=os.pipe2(os.O_CLOEXEC)
    child=os.fork()
    if child==0:
        os.close(read_fd)
        try:
            signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(2)
            resource.setrlimit(resource.RLIMIT_AS,(G.AS_CAP,G.AS_CAP))
            os.setgroups([R.GID] if uid==R.UID else [])
            os.setresgid(R.GID if uid==R.UID else 65534,R.GID if uid==R.UID else 65534,R.GID if uid==R.UID else 65534)
            os.setresuid(uid,uid,uid)
            result={'uid':os.geteuid(),'gid':os.getegid(),'groups':os.getgroups(),
                    'rlimit_as':list(resource.getrlimit(resource.RLIMIT_AS)),'write':write}
            try:
                fd=os.open(path,(os.O_WRONLY if write else os.O_RDONLY)|os.O_NOFOLLOW|os.O_NONBLOCK)
                try:
                    if write:os.write(fd,b'forbidden-write')
                    else:result['sha256']=hashlib.sha256(os.read(fd,65536)).hexdigest()
                finally:os.close(fd)
                result['allowed']=True;result['errno']=None
            except OSError as exc:result.update(allowed=False,errno=exc.errno)
            os.write(write_fd,canonical(result).encode());os.close(write_fd);os._exit(0)
        except BaseException:os._exit(126)
    os.close(write_fd);pidfd=os.pidfd_open(child);until=min(G.now()+3,G.state()['T0']+300,G.state()['stop_at'])
    status=None;data=b''
    try:
        while G.now()<until:
            G.root_checkpoint()
            if select.select([read_fd],[],[],.05)[0]:
                data=os.read(read_fd,65537)
                break
        while G.now()<until:
            ended,status=os.waitpid(child,os.WNOHANG)
            if ended:break
            status=None;G.root_checkpoint();time.sleep(.01)
        if status is None:raise G.LimitReached('IPC_PROBE_TIMEOUT')
        if os.waitstatus_to_exitcode(status)!=0 or not data:raise G.AdmissionBlocked('IPC_PROBE_FAILED')
        out=json.loads(data);out.update(child_pid=child,raw_wait_status=status)
        return out
    finally:
        if status is None:
            try:signal.pidfd_send_signal(pidfd,signal.SIGKILL)
            except ProcessLookupError:pass
            until=G.now()+3
            while G.now()<until:
                ended,_=os.waitpid(child,os.WNOHANG)
                if ended:break
                time.sleep(.01)
            else:raise G.AdmissionBlocked('IPC_PROBE_REAP_UNCONFIRMED')
        os.close(read_fd);os.close(pidfd)


class WaitContext:
    def __init__(self,G,base,trigger=None):
        self.G=G;self.ROOT=base;self.OUT=base/'out';self.trigger=trigger;self.reads=0
        (base/'inputs').mkdir(parents=True);self.OUT.mkdir()
        self.document={'boot_id':G.boot_id(),'status':'CALIBRATING','deadline':G.now()+2,'stop_at':G.now()+2}
        (base/'inputs/batch_state.json').write_text(canonical(self.document))
        self.AdmissionBlocked=G.AdmissionBlocked;self.LimitReached=G.LimitReached
    def now(self):return self.G.now()
    def boot_id(self):return self.G.boot_id()
    def trusted(self,path):
        self.reads+=1
        if self.trigger=='read_error':raise OSError(errno.EIO,'IPC_FIXTURE_READ')
        if self.trigger=='stop_after_read' and self.reads==1:(self.OUT/'STOP_REQUEST.json').write_text('{}')
        if self.trigger=='closed_after_read' and self.reads==1:(self.ROOT/'inputs/CLOSED.json').write_text('{}')
        return json.loads(Path(path).read_text())


def permission_case(G,job,index,binding):
    scenario=job['scenario'];path=G.OUT/('ipc_fixture_%03d.json'%index)
    data={'binding':binding,'case_id':job['case_id']};out={'kind':'file','scenario':scenario}
    private=G.ROOT/'inputs/root_private/ipc_case_999.json'
    if scenario in ('receipt_read','receipt_write'):
        target=G.ROOT/('inputs/ipc_readable_fixture_%03d.json'%index)
        R.publish(G,target,data,True)
        out['probe']=probe(G,target,R.UID,scenario=='receipt_write')
        out['metadata']=metadata(target);out['payload_sha256']=G.digest(target)
        out['subject']='ADMITTED' if scenario=='receipt_read' else 'BLOCKED'
        return out
    if scenario in ('private_write','private_read'):
        R.publish(G,private,data,True);target=private
        out['probe']=probe(G,target,R.UID,scenario=='private_write')
        out['metadata']=metadata(target);out['subject']='BLOCKED';return out
    if scenario in ('bad_batch','bad_boot','bad_lock','bad_digest'):
        actual=dict(binding);key={'bad_batch':'batch_id','bad_boot':'boot_id','bad_lock':'execution_lock_sha256','bad_digest':'static_manifest_sha256'}[scenario]
        actual[key]='wrong-frozen-value';out.update(actual_binding=actual,expected_binding=binding)
        if job.get('mutant')=='ignore_batch':out['subject']='ADMITTED'
        else:out['subject']='BLOCKED' if not R.same_binding(actual,binding) else 'ADMITTED'
        # Same production envelope comparison as the current handoff window checks.
        out['binding_equal']=actual==binding
        return out
    if scenario=='outside':
        try:R.publish(G,G.ROOT.parent/'unregistered.json',data)
        except (G.AdmissionBlocked,OSError) as exc:out.update(subject='BLOCKED',error=str(exc))
        else:out['subject']='ADMITTED'
        return out
    if scenario in ('symlink','hardlink'):
        anchor=G.OUT/('ipc_fixture_%03d.json'%(index+100));R.publish(G,anchor,data)
        if scenario=='symlink':os.symlink(anchor,path)
        else:os.link(anchor,path)
        out['anchor_before']=G.digest(anchor)
        try:R.publish(G,path,data)
        except (G.AdmissionBlocked,OSError) as exc:out.update(subject='BLOCKED',error=str(exc))
        else:out['subject']='ADMITTED'
        out['anchor_after']=G.digest(anchor);out['metadata']=metadata(path);return out
    if scenario.startswith('fault_'):
        try:R.publish(G,path,data,fixture_fault=scenario[6:])
        except OSError as exc:out.update(subject='BLOCKED',errno=exc.errno,error=str(exc))
        else:out['subject']='ADMITTED'
        out['metadata']=metadata(path);return out
    old_umask=os.umask(0o777 if scenario=='umask' else 0o077)
    try:
        R.publish(G,path,data);first=metadata(path)
        if scenario in ('replace','repeat'):
            R.publish(G,path,data);out['before']=first
        if scenario in ('historical','bad_metadata') or job.get('mutant') in ('root600','ignore_permissions'):
            # Mutants affect this synthetic object exclusively, never visits.bin.
            tmp=path.with_name(path.name+'.historical')
            fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
            try:os.fchmod(fd,0o600);G._full(fd,canonical(data).encode());os.fsync(fd)
            finally:os.close(fd)
            os.replace(tmp,path)
        out['metadata']=metadata(path)
        out['probe']=probe(G,path,65534 if scenario=='unauthorized' else R.UID)
        bad=(out['metadata']['uid'],out['metadata']['gid'],out['metadata']['mode'])!=(R.UID,R.GID,0o600)
        out['subject']='BLOCKED' if (bad and job.get('mutant') not in ('root600','ignore_permissions')) or scenario=='unauthorized' else 'ADMITTED'
        out['payload_sha256']=G.digest(path)
        return out
    finally:os.umask(old_umask)


def wait_case(G,job,index,binding):
    scenario=job['scenario'];mutant=job.get('mutant')
    base=G.ROOT/'inputs/root_private'/('wait_fixture_%03d'%index)
    trigger='stop_after_read' if scenario in ('stop_after_ready','ack_stop','stale') else 'closed_after_read' if scenario=='closed_wait' else 'read_error' if scenario=='read_error' else None
    f=WaitContext(G,base,trigger);ready=f.OUT/'ready.json'
    if scenario not in ('timeout','closed_wait'):ready.write_text('{}')
    if scenario in ('stop_before','repeat_stop','socket_cancel','fd_cancel'):(f.OUT/'STOP_REQUEST.json').write_text('{}')
    if scenario in ('closed','late_ack'):(f.ROOT/'inputs/CLOSED.json').write_text('{}')
    if scenario=='deadline':f.document['deadline']=G.now()-1;(base/'inputs/batch_state.json').write_text(canonical(f.document))
    observed=f
    if mutant in ('ignore_stop','ignore_closed'):
        shadow=WaitContext(G,base/'shadow')
        if mutant=='ignore_stop':(f.OUT/'STOP_REQUEST.json').write_text('{}')
        else:(f.ROOT/'inputs/CLOSED.json').write_text('{}')
        f=shadow
    result={'kind':'wait','scenario':scenario,'mutant':mutant,'subject':'BLOCKED'}
    try:
        if scenario=='fd_cancel':
            a,b=os.pipe()
            try:R.wait_fd(f,a,G.now()+.1)
            finally:os.close(a);os.close(b)
        elif scenario in ('socket_cancel','socket_eof'):
            a,b=socket.socketpair(socket.AF_UNIX,socket.SOCK_SEQPACKET)
            try:
                if scenario=='socket_eof':b.close()
                R.receive(f,a,G.now()+.1)
            finally:a.close();b.close()
        else:
            def live():
                if scenario=='exception':raise OSError(errno.EIO,'IPC_FIXTURE_PROCESS_OBSERVATION')
                return scenario not in ('payload_dead','receiver_dead')
            R.wait_ready(f,ready,G.now() if scenario=='timeout' else G.now()+.1,live)
        result['subject']='ADMITTED'
    except (G.AdmissionBlocked,G.LimitReached,OSError) as exc:result['error']=str(exc)
    result['actual_flags']=R.observe(observed);result['state_read_count']=observed.reads
    result['state_document']=observed.document
    return result


def semantic_case(G,job):
    import c09_regression
    mutant=job.get('mutant');mapping={'exit23':'exit23_only','reactivate':'reopen_closed','duplicate':'duplicate_classification'}
    subject=c09_regression.Subject(mapping.get(mutant))
    events={'exit_only':['prepare','exit23','witness23','observe'],
            'reactivate':['prepare','close','commit','exit23','witness23','observe'],
            'duplicate':['prepare','commit','exit23','witness23','observe','repeat']}[job['scenario']]
    rows=[subject.step(e) for e in events]
    return {'kind':'semantic','events':events,'rows':rows,'subject':rows[-1]['subject_state']}


def run_suite(G):
    if os.geteuid()!=0:raise G.AdmissionBlocked('IPC_ROOT_SUITE_REQUIRED')
    cfg=R.contract(G);binding=G.safety_binding();old=G._TICKET
    G._TICKET=G.ticket('C09H');base=G.count();calls=0
    def charge():
        nonlocal calls
        if G.count()-base>=cfg['hard_visits']:raise G.LimitReached('IPC_VISIT_CAP')
        G.c09h_charge();calls+=1
    try:
        charge()
        for index,job in enumerate(cfg['jobs']):
            G.root_checkpoint();start=G.count();charge()
            row={'schema':'ROOT-IPC-RAW/1','case_id':job['case_id'],'input_sha256':hashlib.sha256(canonical(job).encode()).hexdigest(),
                 'binding':binding,'actor':G.identity(),'before':G.stamp()}
            charge()
            if job['kind']=='file':result=permission_case(G,job,index,binding)
            elif job['kind']=='wait':result=wait_case(G,job,index,binding)
            else:result=semantic_case(G,job)
            charge();row.update(result=result,after=G.stamp(),global_before=start,global_after=G.count())
            G._root_write(G.ROOT/('inputs/root_private/ipc_case_%03d.json'%index),row)
            import root_ipc_oracle
            charge()
            immediate=root_ipc_oracle.check_job(G.ROOT/'inputs/root_private',job,index,binding)
            if not immediate['accepted']:raise G.AdmissionBlocked('IPC_FIRST_JOB_FAILURE:'+job['case_id'])
        import root_ipc_oracle
        for job in cfg['jobs']:charge()
        report=root_ipc_oracle.check_suite(G.ROOT/'inputs/root_private',cfg,binding)
        if not report['accepted']:raise G.AdmissionBlocked('IPC_RAW_ORACLE_FAILED')
        report.update(contract_sha256=G.digest(G.SOURCE.parent/'inputs/root_ipc_contract.json'),
                      checker_sha256=G.digest(G.SOURCE/'root_ipc_oracle.py'),
                      global_before=base,global_after=G.count(),root_charges=calls,sample=G.stamp())
        G._root_write(G.ROOT/'inputs/ROOT_IPC_QUALIFICATION.json',report)
        return report
    finally:G._TICKET=old
