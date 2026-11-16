"""C09-only durable handoff and classifier. No role runs on import."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import select
import socket
import struct
import time
import fcntl

PROFILE='C09-DURABLE-RPC/1'
STAGES=('HANDOFF_PREPARING','HANDOFF_READY','HANDOFF_COMMITTED','LAUNCHER_EXIT_OBSERVED','HANDOFF_VERIFIED','RESUMED','HANDOFF_FAILED')
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def sha(x):return hashlib.sha256(canonical(x).encode()).hexdigest()

def classify(f):
    """Single immutable safety predicate, also used by synthetic regression."""
    if f['closed']:return 'CLOSED'
    if not all(f[k] for k in ('binding_ok','sender_ok','version_ok','window_ok','budget_ok',
                              'receiver_ready','receiver_alive','stop_alive')):
        return 'FAILED'
    if f['witness'] is not None and f['witness']!=23:return 'FAILED'
    if f['now']>=f['expires']:return 'FAILED'
    if f['prepared'] and f['commit'] and f['durable_ack'] and f['exit_observed'] and f['witness']==23:
        return 'VERIFIED'
    return 'PENDING'

def synthetic_initial():
    return dict(closed=False,binding_ok=True,sender_ok=True,version_ok=True,window_ok=True,
                budget_ok=True,receiver_ready=True,receiver_alive=True,stop_alive=True,
                witness=None,now=0,expires=12,prepared=False,commit=False,durable_ack=False,
                exit_observed=False)

def paths(G):
    return {'state':G.ROOT/'inputs/c09_handoff.json','commit':G.ROOT/'inputs/c09_commit.json',
            'witness':G.ROOT/'inputs/c09_exit_witness.json','socket':G.ROOT/'inputs/c09_control.sock'}
@contextmanager
def lifecycle_lock(G):
    if os.geteuid()!=0:raise G.AdmissionBlocked('ROOT_LIFECYCLE_LOCK_REQUIRED')
    fd=os.open(G.ROOT/'inputs/c09_lifecycle.lock',os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600)
    acquired=False;until=G.now()+2
    try:
        while not acquired:
            try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);acquired=True
            except BlockingIOError:
                if G.now()>=until:raise G.AdmissionBlocked('LIFECYCLE_LOCK_TIMEOUT')
                time.sleep(.005)
        yield
    finally:
        if acquired:fcntl.flock(fd,fcntl.LOCK_UN)
        os.close(fd)
def window(G,s):
    return {'batch_id':G.ROOT.name,'boot_id':s['boot_id'],'T0':s['T0'],'deadline':s['deadline'],
            'stop_at':s['stop_at'],'execution_mode':s['execution_mode'],
            'source_manifest_sha256':G.digest(G.SOURCE.parent/'inputs/static_manifest.json'),
            'execution_lock_sha256':G.digest(G.SOURCE.parent/'inputs/execution_lock.json'),
            'contract_sha256':G.digest(G.SOURCE.parent/'inputs/c09_contract.json'),
            'authorization_sha256':G.digest(G.ROOT/'inputs/execution_authorization.json')}
def counter(G):
    p=G.OUT/'visits.bin';st=p.stat()
    intent=G.read(p.with_suffix('.bin.intent.json'))
    n=G.count()
    if intent['status']!='COMMITTED' or intent['after']!=n or intent['cap']!=G.VISIT_CAP:
        raise G.AdmissionBlocked('C09_BUDGET_NOT_HEALTHY')
    return {'used':n,'cap':G.VISIT_CAP,'device':st.st_dev,'inode':st.st_ino,'sha256':G.digest(p)}
def alive(G,ident):
    try:
        if G.identity(ident['pid'])!=ident:return False
        fd=os.pidfd_open(ident['pid'])
        try:return G.identity(ident['pid'])==ident and not select.select([fd],[],[],0)[0]
        finally:os.close(fd)
    except (OSError,KeyError):return False
def event(G,h,kind,**data):
    # Root-owned append log; state publication follows a completed log barrier.
    rec={'event':kind,'handoff_id':h['id'],'revision':h['revision'],'identity':G.identity(),
         'window':h['window'],**G.stamp(),**data}
    p=G.ROOT/'inputs/root_private/c09_events.jsonl'
    fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_APPEND|os.O_NOFOLLOW,0o600)
    try:
        os.fchown(fd,0,0);os.fchmod(fd,0o600)
        G._full(fd,(canonical(rec)+'\n').encode());os.fsync(fd)
    finally:os.close(fd)
def publish(G,h,stage,**extra):
    G.root_checkpoint()
    h={**h,**extra,'stage':stage,'revision':h['revision']+1,'updated':G.stamp()}
    event(G,h,stage)
    G._root_write(paths(G)['state'],h)
    return h
def checked_receiver(G,h=None):
    arm=G.trusted(G.ROOT/'inputs/STOP_ARMED.json')
    ident=arm['identity']
    if h is not None and ident!=h['receiver']:raise G.AdmissionBlocked('C09_RECEIVER_IDENTITY')
    if not alive(G,ident):raise G.AdmissionBlocked('C09_RECEIVER_DEAD')
    info=G.unit_show('dclr6batch06-stop.service')
    if info.get('ActiveState')!='active' or int(info.get('MainPID','0'))!=ident['pid']:
        raise G.AdmissionBlocked('C09_STOP_SOURCE_NOT_ACTIVE')
    if info.get('ControlGroup','')=='/'+G.PARENT or info.get('ControlGroup','').startswith('/'+G.PARENT+'/'):
        raise G.AdmissionBlocked('C09_STOP_SOURCE_NOT_INDEPENDENT')
    return ident
def resources_ready(G):
    t=G.ticket('C09');info=G.unit_show(t['unit'])
    startup=G.read(G.OUT/'C09.startup.json')
    if (info.get('ActiveState')!='active' or int(info.get('MainPID','0'))!=t['main_identity']['pid'] or
        not alive(G,t['main_identity']) or not alive(G,startup['watchdog_identity'])):
        raise G.AdmissionBlocked('C09_PAYLOAD_SUPERVISION_LOST')
    parent=G.cg_snapshot(Path('/sys/fs/cgroup')/G.PARENT)
    child=G.cg_snapshot(Path('/sys/fs/cgroup')/G.PARENT/t['unit'])
    if (parent['values']['pids.max']!='4' or int(parent['values']['pids.current'])>4 or
        parent['values']['memory.max']!=str(4*G.AS_CAP) or child['values']['memory.swap.max']!='0' or
        info.get('LimitAS')!=str(G.AS_CAP) or info.get('LimitASSoft')!=str(G.AS_CAP)):
        raise G.AdmissionBlocked('C09_RESOURCE_CONTRACT')
    return {'parent':parent,'child':child,'unit':info,'watchdog':startup['watchdog_identity']}
def check_base(G,h,require_sender_live=False):
    if G.stopped():raise G.AdmissionBlocked('C09_CLOSED_OR_STOP')
    s=G.state()
    if not G.root_ipc().same_binding(h['window'],window(G,s)) or h['id']!=sha({'nonce':h['nonce'],'window':h['window'],
                                                'sender':h['sender'],'coordinator':h['coordinator']}):
        raise G.AdmissionBlocked('C09_BINDING_MISMATCH')
    if h['expected_exit']!=23 or h['case']!='C09' or h['revision']<1:
        raise G.AdmissionBlocked('C09_STATE_FORMAT')
    if G.now()>=h['observe_until']:raise G.LimitReached('C09_HANDOFF_DEADLINE')
    if s['resume_count']!=0 or s['launcher_identity']!=h['sender'] or s.get('coordinator_identity')!=h['coordinator']:
        raise G.AdmissionBlocked('C09_SENDER_WINDOW_IDENTITY')
    checked_receiver(G,h)
    if counter(G)!=h['counter']:raise G.AdmissionBlocked('C09_COUNTER_CHANGED')
    t=G.ticket('C09');marker=G.read(G.OUT/'C09.ready.json')
    if (G.digest(G.ROOT/'inputs/ticket_C09.json')!=h['ticket_sha256'] or
        G.digest(G.OUT/'C09.ready.json')!=h['ready_sha256'] or marker['case']!='C09' or
        marker['counter']!=h['counter']['used'] or marker['identity']!=t['main_identity']):
        raise G.AdmissionBlocked('C09_CASE_PROVENANCE')
    if require_sender_live and not alive(G,h['sender']):raise G.AdmissionBlocked('C09_SENDER_NOT_LIVE')
    return s
def peer(sock):
    pid,uid,gid=struct.unpack('3i',sock.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
    return pid,uid,gid
def rpc(G,message,expected_peer,until):
    G.root_checkpoint()
    remaining=min(12,until-G.now())
    if remaining<=0:raise G.LimitReached('C09_RPC_DEADLINE')
    c=socket.socket(socket.AF_UNIX,socket.SOCK_SEQPACKET)
    c.settimeout(min(.05,remaining))
    try:
        G.root_ipc().connect(G,c,paths(G)['socket'],until)
        pid,uid,_=peer(c)
        if uid!=0 or G.identity(pid)!=expected_peer:raise G.AdmissionBlocked('C09_RPC_PEER')
        raw=canonical(message).encode()
        if len(raw)>65536:raise G.AdmissionBlocked('C09_RPC_SIZE')
        G.root_ipc().send_packet(G,c,raw,until)
        reply=G.root_ipc().receive(G,c,until)
        if len(reply)>65536:raise G.AdmissionBlocked('C09_RPC_REPLY_SIZE')
        out=json.loads(reply)
        if out.get('error'):raise G.AdmissionBlocked('C09_RPC_REJECTED:'+out['error'])
        return out
    finally:c.close()
def qualified_regression(G):
    import c09_oracle
    G.root_ipc().verify_qualification(G)
    q=G.trusted(G.ROOT/'inputs/C09H_QUALIFICATION.json')
    if (q['binding']!=G.safety_binding() or q['checker_sha256']!=G.digest(G.SOURCE/'c09_oracle.py') or
        q['contract_sha256']!=G.digest(G.SOURCE.parent/'inputs/c09_contract.json')):
        raise G.AdmissionBlocked('C09H_QUALIFICATION_BINDING')
    report=c09_oracle.check_suite(G.OUT/'c09_tests',G.c09_contract(),G.safety_binding())
    if not report['accepted'] or report['results']!=q['results']:
        raise G.AdmissionBlocked('C09H_QUALIFICATION_RAW_EVIDENCE')

def sender_prepare(G,coordinator):
    if os.geteuid()!=0 or coordinator is None:raise G.AdmissionBlocked('C09_COORDINATOR_REQUIRED')
    cfg=G.c09_contract()
    qualified_regression(G)
    with lifecycle_lock(G):
        if G.stopped():raise G.AdmissionBlocked('C09_CLOSED_ABSORBING')
        if paths(G)['state'].exists():raise G.AdmissionBlocked('C09_HANDOFF_ALREADY_EXISTS')
        s=G.state();receiver=checked_receiver(G)
        marker=G.read(G.OUT/'C09.ready.json');t=G.ticket('C09')
        if marker['identity']!=t['main_identity'] or marker['counter']!=G.count():
            raise G.AdmissionBlocked('C09_READY_MISMATCH')
        h={'schema':PROFILE,'nonce':os.urandom(16).hex(),'revision':0,'case':'C09',
           'sender':G.identity(),'coordinator':coordinator,'receiver':receiver,
           'window':window(G,s),'counter':counter(G),'expected_exit':23,
           'ticket_sha256':G.digest(G.ROOT/'inputs/ticket_C09.json'),
           'regression_sha256':G.digest(G.ROOT/'inputs/C09H_QUALIFICATION.json'),
           'ready_sha256':G.digest(G.OUT/'C09.ready.json'),'classification_count':0,
           'observe_until':min(s['T0']+300,s['stop_at'],G.now()+cfg['handoff_seconds'])}
        h['id']=sha({'nonce':h['nonce'],'window':h['window'],'sender':h['sender'],'coordinator':coordinator})
        h=publish(G,h,'HANDOFF_PREPARING')
    reply=rpc(G,{'op':'PREPARE','id':h['id']},receiver,h['observe_until'])
    with lifecycle_lock(G):
        fresh=G.trusted(paths(G)['state']);check_base(G,fresh,True)
        commit=G.trusted(paths(G)['commit'])
        if (fresh['stage']!='HANDOFF_COMMITTED' or reply.get('id')!=h['id'] or
            reply.get('commit_sha256')!=G.digest(paths(G)['commit']) or commit['handoff_id']!=h['id']):
            raise G.AdmissionBlocked('C09_DURABLE_ACK_MISSING')
        # A response from the live authenticated receiver is required after its fsync.
        event(G,fresh,'SENDER_ACK_OBSERVED',commit_sha256=reply['commit_sha256'])
    return fresh

class Receiver:
    def __init__(self,G):
        self.G=G;self.durable={};self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_SEQPACKET)
        self.sock.bind(str(paths(G)['socket']));os.chmod(paths(G)['socket'],0o600)
        self.sock.listen(2);self.sock.setblocking(False)
    def close(self):self.sock.close()
    def poll(self):
        G=self.G
        G.root_checkpoint()
        try:c,_=self.sock.accept()
        except BlockingIOError:return
        c.settimeout(.05)
        try:
            pid,uid,_=peer(c)
            if uid!=0:raise G.AdmissionBlocked('C09_CONTROL_UID')
            raw=G.root_ipc().receive(G,c,min(G.state()['deadline'],G.now()+.5))
            if len(raw)>65536:raise G.AdmissionBlocked('C09_CONTROL_SIZE')
            request=json.loads(raw)
            with lifecycle_lock(G):
                if G.stopped():raise G.AdmissionBlocked('C09_CLOSED_ABSORBING')
                h=G.trusted(paths(G)['state'])
                if request.get('id')!=h['id']:raise G.AdmissionBlocked('C09_CONTROL_NONCE')
                if request.get('op')=='PREPARE':
                    if G.identity(pid)!=h['sender']:raise G.AdmissionBlocked('C09_PREPARE_PEER')
                    check_base(G,h,True)
                    if h['stage']=='HANDOFF_PREPARING':
                        resources=resources_ready(G)
                        h=publish(G,h,'HANDOFF_READY')
                        commit={'schema':PROFILE,'handoff_id':h['id'],'commit_version':1,
                                'window':h['window'],'sender':h['sender'],'coordinator':h['coordinator'],
                                'receiver':h['receiver'],'counter':h['counter'],'expected_exit':23,
                                'acknowledged_at':G.stamp(),'resources':resources}
                        G._root_write(paths(G)['commit'],commit)
                        h=publish(G,h,'HANDOFF_COMMITTED',commit_sha256=G.digest(paths(G)['commit']))
                        self.durable[h['id']]=h['commit_sha256']
                    if h['stage']!='HANDOFF_COMMITTED' or self.durable.get(h['id'])!=h['commit_sha256']:
                        raise G.AdmissionBlocked('C09_COMMIT_NOT_ACKNOWLEDGED')
                    reply={'id':h['id'],'commit_sha256':h['commit_sha256'],'receiver':G.identity()}
                elif request.get('op')=='WITNESS':
                    if G.identity(pid)!=h['coordinator']:raise G.AdmissionBlocked('C09_WITNESS_PEER')
                    w=G.trusted(paths(G)['witness'])
                    if w['handoff_id']!=h['id'] or w['sender']!=h['sender'] or w['coordinator']!=h['coordinator']:
                        raise G.AdmissionBlocked('C09_WITNESS_IDENTITY')
                    reply={'id':h['id'],'witness_observed':True}
                else:raise G.AdmissionBlocked('C09_UNKNOWN_CONTROL_OP')
            with lifecycle_lock(G):
                G.root_checkpoint()
                G.root_ipc().send_packet(G,c,canonical(reply).encode(),min(h['observe_until'],G.now()+.5))
        except BaseException as exc:
            try:c.sendall(canonical({'error':str(exc)}).encode())
            except OSError:pass
            raise
        finally:c.close()
    def observe_exit(self):
        G=self.G
        with lifecycle_lock(G):
            if G.stopped():return 'CLOSED'
            if not paths(G)['state'].exists():raise G.AdmissionBlocked('UNEXPECTED_LAUNCHER_EXIT')
            h=G.trusted(paths(G)['state'])
            if h['stage']=='HANDOFF_VERIFIED':return 'VERIFIED'
            if h['stage'] not in ('HANDOFF_COMMITTED','LAUNCHER_EXIT_OBSERVED'):
                raise G.AdmissionBlocked('C09_EXIT_BEFORE_COMMIT')
            check_base(G,h)
            if h['stage']=='HANDOFF_COMMITTED':h=publish(G,h,'LAUNCHER_EXIT_OBSERVED')
            commit=G.trusted(paths(G)['commit'])
            w=G.trusted(paths(G)['witness']) if paths(G)['witness'].exists() else None
            facts=synthetic_initial()
            facts.update(prepared=True,commit=True,durable_ack=(self.durable.get(h['id'])==G.digest(paths(G)['commit'])),
                         exit_observed=True,witness=(w['exit_code'] if w else None),now=G.now(),expires=h['observe_until'],
                         version_ok=(commit['commit_version']==1 and h['commit_sha256']==G.digest(paths(G)['commit'])),
                         binding_ok=(commit['window']==h['window'] and commit['handoff_id']==h['id'] and
                            commit['sender']==h['sender'] and commit['receiver']==h['receiver'] and
                            commit['coordinator']==h['coordinator'] and commit['counter']==h['counter'] and
                            commit['expected_exit']==23))
            if w and (w['handoff_id']!=h['id'] or w['sender']!=h['sender'] or
                      w['coordinator']!=h['coordinator'] or w['window']!=h['window']):
                facts['sender_ok']=False
            verdict=classify(facts)
            event(G,h,'EXIT_CLASSIFICATION_CHECK',facts=facts,verdict=verdict)
            if verdict=='PENDING':return 'PENDING'
            if verdict!='VERIFIED':raise G.AdmissionBlocked('C09_HANDOFF_'+verdict)
            resources_ready(G)
        cleanup=G.stop_tree('EXPECTED_C09_HANDOFF',False)
        with lifecycle_lock(G):
            if G.stopped():return 'CLOSED'
            h=G.trusted(paths(G)['state']);s=check_base(G,h)
            if h['classification_count']!=0:raise G.AdmissionBlocked('C09_DUPLICATE_CLASSIFICATION')
            h=publish(G,h,'HANDOFF_VERIFIED',classification_count=1,cleanup=cleanup,
                      witness_sha256=G.digest(paths(G)['witness']))
            G._root_write(G.ROOT/'inputs/result_C09.json',{'case':'C09','status':'PASS',
                'actual':{'handoff_id':h['id'],'handoff_revision':h['revision'],
                          'commit_sha256':h['commit_sha256'],'witness_sha256':h['witness_sha256'],
                          'native_exit':23,'cleanup':cleanup},'sample':G.stamp()})
            s['status']='AWAIT_EXPECTED_RESUME';s['launcher_identity']=None
            s['coordinator_identity']=None;s['expected_launcher_exit']=None
            G._root_write(G.ROOT/'inputs/batch_state.json',s)
        return 'VERIFIED'

def coordinator_witness(G,child_identity,raw_status):
    if not paths(G)['state'].exists() or (G.ROOT/'inputs/CLOSED.json').exists():return None
    with lifecycle_lock(G):
        h=G.trusted(paths(G)['state'])
        if h['sender']!=child_identity or h['coordinator']!=G.identity():return None
        if G.stopped():return None
        code=os.waitstatus_to_exitcode(raw_status)
        witness={'schema':PROFILE,'handoff_id':h['id'],'sender':child_identity,'coordinator':G.identity(),
                 'window':h['window'],'raw_wait_status':raw_status,'exit_code':code,'sample':G.stamp(),
                 'source':'direct-parent os.waitpid'}
        if paths(G)['witness'].exists():
            if G.trusted(paths(G)['witness'])!=witness:raise G.AdmissionBlocked('C09_DUPLICATE_WITNESS')
        else:G._root_write(paths(G)['witness'],witness)
    rpc(G,{'op':'WITNESS','id':h['id']},h['receiver'],h['observe_until'])
    while G.now()<h['observe_until']:
        with lifecycle_lock(G):
            if G.stopped():raise G.AdmissionBlocked('C09_CLOSED_BEFORE_RESUME')
            fresh=G.trusted(paths(G)['state'])
            if fresh['stage']=='HANDOFF_VERIFIED':
                if fresh['id']!=h['id'] or fresh['classification_count']!=1 or code!=23:
                    raise G.AdmissionBlocked('C09_TERMINAL_VERDICT_MISMATCH')
                checked_receiver(G,fresh)
                return fresh
        time.sleep(.01)
    raise G.LimitReached('C09_VERDICT_DEADLINE')

def resume_admission(G,coordinator):
    with lifecycle_lock(G):
        if G.stopped():raise G.AdmissionBlocked('C09_CLOSED_ABSORBING')
        h=G.trusted(paths(G)['state']);s=G.state()
        if h['stage']!='HANDOFF_VERIFIED' or h['classification_count']!=1 or s['status']!='AWAIT_EXPECTED_RESUME' or s['resume_count']!=0:
            raise G.AdmissionBlocked('C09_NO_VALID_RESUME')
        if h['window']!=window(G,s) or counter(G)!=h['counter']:
            raise G.AdmissionBlocked('C09_RESUME_WINDOW_OR_BUDGET')
        checked_receiver(G,h)
        qualified_regression(G)
        if G.digest(G.ROOT/'inputs/C09H_QUALIFICATION.json')!=h['regression_sha256']:
            raise G.AdmissionBlocked('C09H_RECEIPT_CHANGED')
        if G.digest(paths(G)['commit'])!=h['commit_sha256'] or G.digest(paths(G)['witness'])!=h['witness_sha256']:
            raise G.AdmissionBlocked('C09_RESUME_RECEIPT_HASH')
        if G.trusted(paths(G)['witness'])['exit_code']!=23:
            raise G.AdmissionBlocked('C09_RESUME_EXIT_STATUS')
        result=G.trusted(G.ROOT/'inputs/result_C09.json')
        if result['status']!='PASS' or result['actual']['handoff_id']!=h['id']:
            raise G.AdmissionBlocked('C09_RESUME_PROVENANCE')
        # Window remains unchanged; only the new supervisor identities and once bit change.
        h=publish(G,h,'RESUMED')
        s['status']='CALIBRATING';s['resume_count']=1;s['launcher_identity']=G.identity()
        s['coordinator_identity']=coordinator
        G._root_write(G.ROOT/'inputs/batch_state.json',s)
        return s
def verify_completed_handoff(G):
    with lifecycle_lock(G):
        if G.stopped():raise G.AdmissionBlocked('C09_CLOSED_ABSORBING')
        h=G.trusted(paths(G)['state']);s=G.state()
        if h['stage']!='RESUMED' or h['classification_count']!=1 or s['resume_count']!=1 or h['window']!=window(G,s):
            raise G.AdmissionBlocked('C09_FORMAL_HANDOFF_NOT_COMPLETE')
        if G.digest(paths(G)['commit'])!=h['commit_sha256'] or G.digest(paths(G)['witness'])!=h['witness_sha256']:
            raise G.AdmissionBlocked('C09_FORMAL_PROVENANCE')
        if G.trusted(paths(G)['witness'])['exit_code']!=23:
            raise G.AdmissionBlocked('C09_FORMAL_EXIT_STATUS')
        checked_receiver(G,h);qualified_regression(G)
