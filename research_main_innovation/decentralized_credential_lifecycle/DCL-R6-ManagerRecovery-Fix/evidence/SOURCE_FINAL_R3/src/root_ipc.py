"""RootIPC/1 publication and cancellable waits. Runtime requires separate authorization."""
from contextlib import contextmanager
import errno
import json
import os
from pathlib import Path
import re
import select
import socket
import stat
import time

PROFILE = 'ROOT-IPC/1'
UID, GID = 999, 989


def same_binding(observed,expected):
    return type(observed) is dict and type(expected) is dict and observed==expected


def policy(G, path, root_record=False):
    # Lexical containment precedes every open; resolve() would follow an attacker link.
    p = Path(path)
    if not p.is_absolute() or '..' in p.parts or '.' in p.parts:
        raise G.AdmissionBlocked('IPC_LEXICAL_PATH')
    try: rel = p.relative_to(G.ROOT).as_posix()
    except ValueError: raise G.AdmissionBlocked('IPC_PATH_OUTSIDE_BATCH')
    if not root_record and rel == 'out/visits.bin.intent.json':
        return rel, (UID, GID, 0o600)
    if not root_record and rel == 'out/STOP_REQUEST.json':
        return rel, (UID, GID, 0o600)
    if not root_record and rel == 'out/EVIDENCE_MANIFEST.json':
        return rel, (0, 0, 0o600)
    if re.fullmatch(r'out/ipc_fixture_[0-9]{3}\.json', rel):
        return rel, (UID, GID, 0o600)
    if root_record and re.fullmatch(r'inputs/ipc_readable_fixture_[0-9]{3}\.json',rel):
        return rel,(0,GID,0o640)
    if root_record and re.fullmatch(r'inputs/root_private/(waitpid_[0-9]+|ipc_case_[0-9]{3}|ipc_suite)\.json', rel):
        return rel, (0, 0, 0o600)
    allowed = {'batch_state.json','CLOSED.json','STOP_ARMED.json','SEAL_ERROR.json',
               'C09H_QUALIFICATION.json','ROOT_IPC_QUALIFICATION.json','GATE_NEGATIVE_AUDIT.json',
               'RANGE_QUALIFICATION.json','RESOURCE_QUALIFICATION.json','GATE_LEDGER_QUALIFICATION.json','MR_QUALIFICATION.json','MR_RECOVERY_REVIEW.json','MR_DIAGNOSTIC_RESULT.json',
               'c09_handoff.json','c09_commit.json','c09_exit_witness.json'}
    if root_record and rel.startswith('inputs/') and len(Path(rel).parts) == 2:
        name = Path(rel).name
        if name in allowed or re.fullmatch(r'(ticket|result)_(C(?:0[0-9]|1[0-2])|C09H|RANGE|FORMAL)\.json',name) or re.fullmatch(r'stop_(event|result)_[0-9]+_[0-9]+\.json',name):
            return rel, (0, GID, 0o640)
    raise G.AdmissionBlocked('IPC_UNREGISTERED_ROOT_TARGET:'+rel)


def _metadata(st):
    return st.st_uid, st.st_gid, stat.S_IMODE(st.st_mode)


def _no_acl(fd):
    if any(name.startswith('system.posix_acl_') for name in os.listxattr(fd)):
        raise PermissionError('IPC_UNREVIEWED_POSIX_ACL')


def _dir(parent, name, expected=None):
    fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=parent)
    s = os.fstat(fd)
    if not stat.S_ISDIR(s.st_mode) or (expected is not None and _metadata(s) != expected) or (expected is None and (s.st_uid != 0 or s.st_mode & 0o022)):
        os.close(fd)
        raise PermissionError('IPC_DIRECTORY_METADATA:'+name)
    try:_no_acl(fd)
    except BaseException:os.close(fd);raise
    return fd


@contextmanager
def directories(G):
    if os.geteuid() != 0 or str(G.ROOT) != '/var/lib/dcl-r6/batch10':
        raise G.AdmissionBlocked('IPC_ROOT_CURRENT_BATCH_REQUIRED')
    fds=[]
    try:
        fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC);fds.append(fd)
        for name in G.ROOT.parts[1:-1]:
            fd=_dir(fd,name);fds.append(fd)
        batch=_dir(fd,G.ROOT.name,(0,GID,0o750));fds.append(batch)
        inp=_dir(batch,'inputs',(0,GID,0o750));fds.append(inp)
        private=_dir(inp,'root_private',(0,0,0o700));fds.append(private)
        out=_dir(batch,'out',(UID,GID,0o700));fds.append(out)
        if os.fstat(private).st_dev != os.fstat(out).st_dev:
            raise G.AdmissionBlocked('IPC_CROSS_DEVICE_PUBLICATION')
        yield {'inputs':inp,'private':private,'out':out}
    finally:
        for fd in reversed(fds):os.close(fd)


def publish(G,path,data,root_record=False,timing_stage='metadata.atomic',fixture_fault=None):
    rel,expected=policy(G,path,root_record)
    fixture=bool(re.fullmatch(r'out/ipc_fixture_[0-9]{3}\.json',rel))
    if fixture_fault is not None and (not fixture or fixture_fault not in ('after_create','file_fsync','rename','directory_fsync')):
        raise G.AdmissionBlocked('IPC_FAULT_OUTSIDE_SYNTHETIC_FIXTURE')
    raw=G.timed(timing_stage+'.encode',lambda:json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2).encode())
    with directories(G) as ds:
        destination=ds['out'] if rel.startswith('out/') else ds['private'] if '/root_private/' in rel else ds['inputs']
        name=Path(rel).name
        try:
            old=os.stat(name,dir_fd=destination,follow_symlinks=False)
            if not stat.S_ISREG(old.st_mode) or old.st_nlink!=1:
                raise G.AdmissionBlocked('IPC_TARGET_TYPE_OR_LINK')
        except FileNotFoundError:pass
        tmp='.publish.'+str(os.getpid())+'.'+os.urandom(16).hex()
        fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=ds['private'])
        # Failure leaves the private staging object as evidence. No grant follows.
        try:
            os.fchown(fd,expected[0],expected[1]);os.fchmod(fd,expected[2])
            _no_acl(fd)
            if _metadata(os.fstat(fd))!=expected:raise G.AdmissionBlocked('IPC_PREPUBLICATION_METADATA')
            if fixture_fault=='after_create':raise OSError(errno.EIO,'IPC_FIXTURE_AFTER_CREATE')
            G.timed(timing_stage+'.write',G._full,fd,raw)
            if fixture_fault=='file_fsync':raise OSError(errno.EIO,'IPC_FIXTURE_FILE_FSYNC')
            G.sync_fd(fd,timing_stage+'.file')
            published_inode=os.fstat(fd)
            if fixture_fault=='rename':raise OSError(errno.EIO,'IPC_FIXTURE_RENAME')
            os.replace(tmp,name,src_dir_fd=ds['private'],dst_dir_fd=destination)
            if fixture_fault=='directory_fsync':raise OSError(errno.EIO,'IPC_FIXTURE_DIRECTORY_FSYNC')
            # Two directories participate in cross-directory rename.
            G.sync_fd(destination,timing_stage+'.directory')
            if destination!=ds['private']:G.sync_fd(ds['private'],timing_stage+'.staging_directory')
            after=os.stat(name,dir_fd=destination,follow_symlinks=False)
            if (_metadata(after)!=expected or not stat.S_ISREG(after.st_mode) or after.st_nlink!=1 or
                (after.st_dev,after.st_ino)!=(published_inode.st_dev,published_inode.st_ino)):
                raise G.AdmissionBlocked('IPC_POSTPUBLICATION_METADATA_OR_IDENTITY')
            return {'uid':after.st_uid,'gid':after.st_gid,'mode':stat.S_IMODE(after.st_mode),
                    'device':after.st_dev,'inode':after.st_ino,'bytes':after.st_size}
        finally:os.close(fd)


def marker(path):
    # Presence of a malformed marker also cancels; contents never create a grant.
    try:os.lstat(path);return True
    except FileNotFoundError:return False


def observe(G):
    return {'closed':marker(G.ROOT/'inputs/CLOSED.json'),
            'stop_request':marker(G.OUT/'STOP_REQUEST.json')}


def checkpoint(G,allow_uninitialized=False):
    flags=observe(G)
    if flags['closed']:raise G.AdmissionBlocked('IPC_CLOSED_DOMINATES')
    if flags['stop_request']:raise G.AdmissionBlocked('IPC_STOP_REQUEST_DOMINATES')
    p=G.ROOT/'inputs/batch_state.json'
    if not p.exists():
        if allow_uninitialized:return None
        raise G.AdmissionBlocked('IPC_STATE_MISSING')
    s=G.trusted(p)
    if s['boot_id']!=G.boot_id():raise G.AdmissionBlocked('IPC_BOOT_DRIFT')
    if s['status'] not in ('CALIBRATING','FORMAL','AWAIT_EXPECTED_RESUME'):
        raise G.AdmissionBlocked('IPC_TERMINAL_STATE')
    if G.now()>=min(s['deadline'],s['stop_at']):raise G.LimitReached('IPC_ABSOLUTE_LIMIT')
    return s


def wait_ready(G,path,until,live=None):
    while True:
        checkpoint(G)
        if live is not None and not live():raise G.AdmissionBlocked('IPC_REQUIRED_PROCESS_EXITED')
        if marker(path):
            checkpoint(G)
            return
        if G.now()>=until:raise G.LimitReached('IPC_READY_TIMEOUT')
        time.sleep(min(.05,max(0,until-G.now())))


def wait_fd(G,fd,until):
    while G.now()<until:
        checkpoint(G,allow_uninitialized=True)
        if select.select([fd],[],[],min(.05,max(0,until-G.now())))[0]:
            checkpoint(G,allow_uninitialized=True)
            return
    raise G.LimitReached('IPC_FD_TIMEOUT')


def receive(G,sock,until):
    while G.now()<until:
        checkpoint(G)
        sock.settimeout(min(.05,max(.001,until-G.now())))
        try:
            raw=sock.recv(65537)
            checkpoint(G)
            if not raw or len(raw)>65536:raise G.AdmissionBlocked('IPC_PACKET_SIZE_OR_EOF')
            return raw
        except socket.timeout:continue
    raise G.LimitReached('IPC_RECEIVE_TIMEOUT')


def connect(G,sock,path,until):
    sock.setblocking(False)
    while G.now()<until:
        checkpoint(G)
        error=sock.connect_ex(str(path))
        if error in (0,errno.EISCONN):return
        if error not in (errno.EINPROGRESS,errno.EALREADY,errno.EAGAIN,errno.EWOULDBLOCK):raise OSError(error,'IPC_CONNECT')
        select.select([], [sock], [], min(.05,max(0,until-G.now())))
        time.sleep(min(.005,max(0,until-G.now())))
    raise G.LimitReached('IPC_CONNECT_TIMEOUT')


def send_packet(G,sock,raw,until):
    if not 0<len(raw)<=65536:raise G.AdmissionBlocked('IPC_SEND_SIZE')
    sock.setblocking(False)
    while G.now()<until:
        checkpoint(G)
        try:
            sent=sock.send(raw)
            if sent!=len(raw):raise G.AdmissionBlocked('IPC_SHORT_PACKET')
            checkpoint(G)
            return
        except BlockingIOError:
            select.select([], [sock], [], min(.05,max(0,until-G.now())))
    raise G.LimitReached('IPC_SEND_TIMEOUT')


def contract(G):
    p=G.SOURCE.parent/'inputs/root_ipc_contract.json'
    a,m=G.authorization()
    if G.digest(p)!=m['root_ipc_contract_sha256'] or a.get('root_ipc_contract_sha256')!=G.digest(p):
        raise G.AdmissionBlocked('IPC_CONTRACT_BINDING')
    cfg=G.trusted(p)
    if cfg['version']!='RootIPC-static-1' or cfg['future_batch_id']!=G.ROOT.name:
        raise G.AdmissionBlocked('IPC_CONTRACT_VERSION')
    return cfg


def verify_qualification(G):
    import root_ipc_oracle
    q=G.trusted(G.ROOT/'inputs/ROOT_IPC_QUALIFICATION.json')
    cfg=contract(G);binding=G.safety_binding()
    if q['binding']!=binding or q['contract_sha256']!=G.digest(G.SOURCE.parent/'inputs/root_ipc_contract.json') or q['checker_sha256']!=G.digest(G.SOURCE/'root_ipc_oracle.py'):
        raise G.AdmissionBlocked('IPC_QUALIFICATION_BINDING')
    # Raw review records are root-private. Payload verifies their protected receipt;
    # Root rechecks every raw byte before producing it and before resume.
    if os.geteuid()==0:
        fresh=root_ipc_oracle.check_suite(G.ROOT/'inputs/root_private',cfg,binding)
        if not fresh['accepted'] or fresh['results']!=q['results']:raise G.AdmissionBlocked('IPC_RAW_QUALIFICATION')
    expected={j['case_id']:j for j in cfg['jobs']}
    if not q['accepted'] or len(q['results'])!=len(expected) or {r['case_id'] for r in q['results']}!=set(expected):raise G.AdmissionBlocked('IPC_INCOMPLETE_QUALIFICATION')
    for row in q['results']:
        job=expected[row['case_id']]
        target='PASS' if job['variant']=='safe' else 'MUTATION_DETECTED'
        if row['accepted'] is not True or row['status']!=target or not set(row['violations']).issubset(job['allowed_violation_set']):raise G.AdmissionBlocked('IPC_REQUIRED_RESULT')
