"""BC-SINGLE-SESSION/1. Future Linux entry; this version is statically prepared only."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import pwd
import resource
import stat
import subprocess
import sys
import time

SOURCE=Path(__file__).resolve().parent
ROOT=Path('/var/lib/dcl-r6/batch08')
PROFILE='BC-SINGLE-SESSION/1'
_SESSION=None


class Rejected(RuntimeError):pass
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def boot():return Path('/proc/sys/kernel/random/boot_id').read_text().strip()
def now():return time.clock_gettime(time.CLOCK_BOOTTIME)
def identity(pid=None):
    pid=os.getpid() if pid is None else pid
    raw=Path('/proc/%s/stat'%pid).read_text();fields=raw[raw.rfind(')')+2:].split()
    return {'pid':pid,'start_ticks':int(fields[19]),'boot_id':boot()}
def stamp():return {'boot_id':boot(),'boottime':now(),'utc_ns':time.time_ns()}
def emit(event,**facts):
    print(json.dumps({'schema':'BC-ENTRY-EVENT/1','event':event,'identity':identity(),'sample':stamp(),**facts},sort_keys=True),flush=True)
def trusted(p,maximum=4194304):
    fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        s=os.fstat(fd)
        if not stat.S_ISREG(s.st_mode) or s.st_uid!=0 or s.st_mode&0o022 or s.st_size>maximum:raise Rejected('BC_UNTRUSTED_RECORD')
        raw=os.read(fd,s.st_size+1)
        if len(raw)!=s.st_size:raise Rejected('BC_SHORT_RECORD')
        return json.loads(raw)
    finally:os.close(fd)
def _full(fd,raw):
    if os.write(fd,raw)!=len(raw):raise Rejected('BC_SHORT_WRITE')


def operator_bytes(p):
    fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        s=os.fstat(fd)
        if not stat.S_ISREG(s.st_mode) or s.st_size>4194304:raise Rejected('BC_OPERATOR_INPUT_SIZE')
        b=os.read(fd,s.st_size+1)
        if len(b)!=s.st_size:raise Rejected('BC_OPERATOR_INPUT_SHORT')
        return b
    finally:os.close(fd)


class Context:
    ROOT=ROOT
    AdmissionBlocked=Rejected


class Store:
    """Fixed Root-only boot namespace plus two fixed group-readable certificates."""
    def __enter__(self):
        if str(SOURCE)!='/var/lib/dcl-r6/cr01/src' or os.geteuid()!=0:raise Rejected('BC_ROOT_SOURCE_REQUIRED')
        if str(SOURCE) not in sys.path:sys.path.insert(0,str(SOURCE))
        import root_ipc
        self.owner=root_ipc.directories(Context());self.ds=self.owner.__enter__()
        try:os.mkdir('boot',0o700,dir_fd=self.ds['private'])
        except FileExistsError:pass
        self.fd=root_ipc._dir(self.ds['private'],'boot',(0,0,0o700))
        return self
    def __exit__(self,*exc):
        os.close(self.fd);self.owner.__exit__(*exc)
    def read(self,name):
        if '/' in name or name.startswith('.'):raise Rejected('BC_RECORD_NAME')
        fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW,dir_fd=self.fd)
        try:
            s=os.fstat(fd)
            if (s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)!=(0,0,0o600,1) or s.st_size>131072:raise Rejected('BC_PRIVATE_METADATA')
            return json.loads(os.read(fd,s.st_size+1))
        finally:os.close(fd)
    def put(self,name,doc,exclusive=False,public=False):
        if public:
            if name not in ('BOOT_START.json','BOOT_RESUME.json','BOOT_CONTINUITY_QUALIFICATION.json','C00_READINESS.json','C10_READINESS.json','C00_READY_QUALIFICATION.json'):raise Rejected('BC_PUBLIC_TARGET')
            destination=self.ds['inputs'];gid=989;mode=0o640
        else:
            if '/' in name or name.startswith('.') or not name.endswith('.json'):raise Rejected('BC_PRIVATE_TARGET')
            destination=self.fd;gid=0;mode=0o600
        if exclusive:
            fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,mode,dir_fd=destination)
            try:
                os.fchown(fd,0,gid);os.fchmod(fd,mode);_full(fd,canon(doc));os.fsync(fd)
            finally:os.close(fd)
        else:
            tmp='.bc.'+str(os.getpid())+'.'+os.urandom(12).hex()
            fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=self.fd)
            try:
                os.fchown(fd,0,gid);os.fchmod(fd,mode);_full(fd,canon(doc));os.fsync(fd)
                inode=os.fstat(fd)
                os.replace(tmp,name,src_dir_fd=self.fd,dst_dir_fd=destination)
                after=os.stat(name,dir_fd=destination,follow_symlinks=False)
                if (after.st_dev,after.st_ino)!=(inode.st_dev,inode.st_ino):raise Rejected('BC_PUBLICATION_IDENTITY')
            finally:os.close(fd)
        os.fsync(destination)
        if destination!=self.fd:os.fsync(self.fd)
    def lock(self):
        fd=os.open('activation.lock',os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=self.fd)
        s=os.fstat(fd)
        if (s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)!=(0,0,0o600,1):os.close(fd);raise Rejected('BC_LOCK_METADATA')
        fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        return fd


def eligibility(e):
    """Common native/simulation policy; callers must supply actual current observations."""
    if not e['static_valid']:raise Rejected('BC_STATIC_DRIFT')
    if e['closed'] or e['stop']:raise Rejected('BC_CLOSED_OR_STOP')
    if e['window_exists'] or e['counter_exists']:raise Rejected('BC_EXISTING_WINDOW')
    if not(e['process_alive'] and e['identity_valid']):raise Rejected('BC_PROCESS_IDENTITY')
    if not e['resource_valid']:raise Rejected('BC_RUNTIME_CHANGED')
    if len(set(e['chain_boots']+[e['boot_id']]))!=1:raise Rejected('BC_BOOT_CHAIN')


def ticket_policy(t,e,claim):
    if t['boot_id']!=e['boot_id'] or t['owner']!=e['owner']:raise Rejected('BC_STALE_BOOT_OR_OWNER')
    if not(e['cap_live'] and e['sealed'] and e['process_alive'] and e['identity_valid']):raise Rejected('BC_CAPABILITY_OR_IDENTITY')
    if not e['static_valid'] or not e['resource_valid']:raise Rejected('BC_ACTIVATION_DRIFT')
    if t['binding']!=e['binding']:raise Rejected('BC_ACTIVATION_BINDING')
    if e['closed'] or e['stop'] or e['window_exists'] or e['counter_exists']:raise Rejected('BC_REACTIVATION')
    if claim['initial_entered']:raise Rejected('BC_DUPLICATE_ACTIVATION')
    if e['now']>=t['expires']:raise Rejected('BC_ACTIVATION_EXPIRED')


def service_policy(e):
    if not e['process_alive'] or not e['same_boot'] or not e['service_active'] or not e['stable_main_pid'] or e['closed'] or e['stop']:
        raise Rejected('BC_NO_ACTUAL_SERVICE')


def command(argv,deadline,epoch):
    if boot()!=epoch or now()>=deadline:raise Rejected('BC_PREFLIGHT_EXPIRED')
    start=stamp()
    emit('PREFLIGHT_COMMAND_BEGIN',argv=argv,start=start)
    r=subprocess.run(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                     timeout=max(.001,min(15,deadline-now())),check=False)
    if len(r.stdout)+len(r.stderr)>32768:raise Rejected('BC_COMMAND_OUTPUT_LIMIT')
    emit('PREFLIGHT_COMMAND',argv=argv,start=start,exit_code=r.returncode,stdout_hex=r.stdout.hex(),stderr_hex=r.stderr.hex())
    if r.returncode:raise Rejected('BC_COMMAND_FAILED:'+repr(argv)+':'+r.stderr.decode(errors='replace'))
    if boot()!=epoch or now()>=deadline:raise Rejected('BC_BOOT_OR_TIME_AFTER_COMMAND')
    return r.stdout.decode()


def artifact_check(deadline,epoch):
    m=trusted(SOURCE.parent/'inputs/static_manifest.json');lock=trusted(SOURCE.parent/'inputs/execution_lock.json')
    if m['version']!='C00Ready-static-1' or m['source_directory']!=str(SOURCE):raise Rejected('BC_SOURCE_VERSION')
    if sys.platform!='linux' or tuple(sys.version_info[:3])!=(3,12,3):raise Rejected('BC_PYTHON_VERSION')
    if str(Path(sys.executable).resolve())!='/usr/bin/python3.12':raise Rejected('BC_PYTHON_PATH')
    if not(sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode):raise Rejected('BC_PYTHON_FLAGS')
    if list(SOURCE.rglob('*.pyc')):raise Rejected('BC_UNDECLARED_BYTECODE_CACHE')
    for p in [SOURCE.parent,SOURCE,SOURCE.parent/'inputs',*[SOURCE/k for k in m['source_hashes']]]:
        s=p.lstat()
        if stat.S_ISLNK(s.st_mode) or s.st_uid!=0 or s.st_mode&0o022 or any(k.startswith('system.posix_acl_') for k in os.listxattr(p,follow_symlinks=False)):raise Rejected('BC_PACKAGE_METADATA')
    rows={str(SOURCE/k):v for k,v in m['source_hashes'].items()}
    rows.update(m['runtime_files'])
    rows.update({str(SOURCE.parent/k):v for k,v in m['bound_inputs'].items()})
    tree=trusted(SOURCE.parent/'inputs/runtime_tree_lock.json')
    if digest(SOURCE.parent/'inputs/runtime_tree_lock.json')!=m['runtime_tree_lock_sha256']:raise Rejected('BC_RUNTIME_TREE_LOCK')
    rows.update({p:r['sha256'] for p,r in tree['files'].items()})
    for p,expected in rows.items():
        h=hashlib.sha256()
        with Path(p).open('rb') as f:
            while True:
                if boot()!=epoch or now()>=deadline:raise Rejected('BC_HASH_BOOT_OR_DEADLINE')
                b=f.read(1048576)
                if not b:break
                h.update(b)
        if h.hexdigest()!=expected:raise Rejected('BC_ARTIFACT_DRIFT:'+p)
    # This is native syntax-only compilation in the future entry; no target imports.
    for p in SOURCE.glob('*.py'):compile(p.read_bytes(),str(p),'exec')
    return m,lock,{'rule_version':'BC-A/1','manifest_sha256':digest(SOURCE.parent/'inputs/static_manifest.json'),
                  'execution_lock_sha256':digest(SOURCE.parent/'inputs/execution_lock.json'),
                  'object_digests':rows,'source_mode':'SOURCE_ONLY/1','provenance':'fresh current-byte reads',
                  'reuse_condition':'Frozen object hashes/rule/lock unchanged; dynamic evidence always recollected'}


def runtime_snapshot(m,lock,deadline,epoch,prepared=False):
    version=command(['/usr/bin/systemctl','show','--property=Version','--value'],deadline,epoch).strip()
    failed=command(['/usr/bin/systemctl','list-units','--state=failed','--all','--no-pager','--no-legend'],deadline,epoch)
    if version!=m['systemd']:raise Rejected('BC_SYSTEMD_VERSION')
    if any(s.replace('●','').split()[0]!='mnt-e.mount' for s in failed.splitlines() if s.replace('●','').split()):raise Rejected('BC_MANAGER_FAILED_UNIT')
    user=pwd.getpwuid(999);probe=pwd.getpwuid(65534)
    if user.pw_gid!=989 or os.getgrouplist(user.pw_name,989)!=[989] or probe.pw_gid!=65534:raise Rejected('BC_UID_GID')
    active=[];root_roles=[]
    for p in Path('/proc').glob('[0-9]*'):
        try:
            s=dict(x.split(':',1) for x in (p/'status').read_text().splitlines() if ':' in x)
            if 999 in map(int,s['Uid'].split()):active.append(int(p.name))
            argv=(p/'cmdline').read_bytes().decode(errors='replace').split('\0')
            if int(p.name)!=os.getpid() and '--role' in argv and any(a.startswith('/var/lib/dcl-r6/') and a.endswith('/guard.py') for a in argv):root_roles.append(int(p.name))
        except (OSError,KeyError):pass
    if active:raise Rejected('BC_PAYLOAD_RESIDUALS')
    if root_roles:raise Rejected('BC_ROOT_ROLE_RESIDUALS')
    if os.geteuid()!=0 or os.uname().release!=m['kernel'] or os.uname().machine!=m['architecture'] or os.sysconf('SC_PAGE_SIZE')!=4096:raise Rejected('BC_NATIVE_RUNTIME')
    if not any(s.split()[4]=='/sys/fs/cgroup' and ' - cgroup2 ' in s for s in Path('/proc/self/mountinfo').read_text().splitlines()):raise Rejected('BC_CGROUP_V2')
    if not prepared:
        listed=command(['/usr/bin/systemctl','list-units','dclr6batch08*','--all','--no-pager','--no-legend'],deadline,epoch)
        if (ROOT.exists() or Path('/etc/systemd/system/dclr6batch08.slice').exists() or
            Path('/sys/fs/cgroup/dclr6batch08.slice').exists() or listed.strip()):raise Rejected('BC_BATCH_MUST_BE_NEW')
    state=ROOT/'inputs/batch_state.json';counter=ROOT/'out/visits.bin'
    if state.exists() or counter.exists() or (ROOT/'inputs/CLOSED.json').exists() or (ROOT/'out/STOP_REQUEST.json').exists():raise Rejected('BC_PRIOR_WINDOW_OR_CLOSURE')
    unit={}
    if prepared:
        if digest('/etc/systemd/system/dclr6batch08.slice')!=lock['unit_slice_sha256']:raise Rejected('BC_INSTALLED_UNIT_DRIFT')
        text=command(['/usr/bin/systemctl','show','dclr6batch08.slice','--property=LoadState','--property=ActiveState','--property=TasksMax','--property=MemoryMax','--property=ControlGroup'],deadline,epoch)
        unit=dict(s.split('=',1) for s in text.splitlines() if '='in s)
        if unit.get('ActiveState')!='inactive' or unit.get('TasksMax')!='4' or unit.get('MemoryMax')!='4294967296' or unit.get('ControlGroup'):raise Rejected('BC_PARENT_PRESTART_LIMITS')
        with Store():pass
        if any((ROOT/'out').iterdir()):raise Rejected('BC_OUTPUT_MUST_BE_EMPTY')
    return {'boot_id':boot(),'owner':identity(),'root_cgroup':Path('/proc/self/cgroup').read_text(),
            'systemd':version,'parent':unit,'uid':999,'gid':989,'probe_uid':65534,
            'page_size':4096,'resource_valid':True,'identity_valid':True,'process_alive':True,
            'closed':False,'stop':False,'window_exists':False,'counter_exists':False,'static_valid':True,'sample':stamp()}


def prepare_activation():
    epoch=boot();deadline=now()+120
    resource.setrlimit(resource.RLIMIT_AS,(1<<30,1<<30))
    emit('PREFLIGHT_BEGIN',deadline=deadline,source_mode='SOURCE_ONLY/1')
    m,lock,audit=artifact_check(deadline,epoch)
    if str(SOURCE)!='/var/lib/dcl-r6/cr01/src':raise Rejected('BC_PACKAGE_PATH')
    auth_source=Path(lock['authorization_sources']['receipt']);text_source=Path(lock['authorization_sources']['text'])
    # Host operator supplies these exact approved bytes; no authority is inferred from a cache.
    auth_raw=operator_bytes(auth_source);text_raw=operator_bytes(text_source);auth=json.loads(auth_raw)
    binding={'batch_id':'batch08','static_manifest_sha256':audit['manifest_sha256'],
             'execution_lock_sha256':audit['execution_lock_sha256'],'authorization_text_sha256':hashlib.sha256(text_raw).hexdigest(),
             'boot_contract_sha256':digest(SOURCE.parent/'inputs/boot_contract.json')}
    for k,v in binding.items():
        if auth.get(k)!=v:raise Rejected('BC_AUTHORIZATION_BINDING:'+k)
    if (auth.get('boot_continuity_profile')!=PROFILE or auth.get('SingleSession_exec_explicitly_approved') is not True or
        (auth.get('scope')!='C00_DIAGNOSTIC_ONLY' and auth.get('SameProcess_C09_resume_explicitly_approved') is not True) or (auth.get('scope')!='C00_DIAGNOSTIC_ONLY' and auth.get('RootIPC_helpers_explicitly_approved') is not True) or
        auth.get('limits')!=[1000000,1800,1740,1<<30,4] or auth.get('source_mode')!='SOURCE_ONLY/1' or
        auth.get('scope') not in ('CALIBRATE_S1S9_THEN_F1_F4','C00_DIAGNOSTIC_ONLY')):raise Rejected('BC_EXECUTION_SCOPE_MISSING')
    if auth['scope']=='C00_DIAGNOSTIC_ONLY' and auth.get('C00_diagnostic_explicitly_approved') is not True:raise Rejected('BC_C00_SCOPE')
    if auth['scope']=='CALIBRATE_S1S9_THEN_F1_F4' and auth.get('Full_conditional_chain_explicitly_approved') is not True:raise Rejected('BC_FULL_SCOPE')
    if auth.get('readiness_contract_sha256')!=m.get('readiness_contract_sha256'):raise Rejected('BC_READINESS_BINDING')
    first=runtime_snapshot(m,lock,deadline,epoch)
    for argv in lock['preparation_commands']:command(argv,deadline,epoch)
    for data,target in [(text_raw,'BATCH08_AUTHORIZATION_TEXT.txt'),(auth_raw,'execution_authorization.json')]:
        fd=os.open(ROOT/'inputs'/target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o640)
        try:os.fchown(fd,0,989);os.fchmod(fd,0o640);_full(fd,data);os.fsync(fd)
        finally:os.close(fd)
    m,lock,fresh_audit=artifact_check(deadline,epoch)
    final=runtime_snapshot(m,lock,deadline,epoch,True)
    final['chain_boots']=[first['boot_id'],final['boot_id']];eligibility(final)
    emit('PREFLIGHT_QUALIFIED',first_dynamic=first,final_dynamic=final,resource_gate='NOT_OBTAINED')
    lockfd=None;capfd=None
    try:
        with Store() as store:
            lockfd=store.lock()
            # Exclusive persistent claim burns this attempt even if exec or publication fails.
            ticket={'schema':PROFILE,'nonce':os.urandom(24).hex(),'boot_id':epoch,'owner':identity(),
                    'binding':binding,'root_cgroup':final['root_cgroup'],'issued_at':now(),
                    'expires':min(deadline,now()+10),'preflight_deadline':deadline,
                    'first_dynamic_sha256':hashlib.sha256(canon(first)).hexdigest(),
                    'final_dynamic_sha256':hashlib.sha256(canon(final)).hexdigest()}
            store.put('activation.json',{'ticket':ticket,'initial_entered':False,'resume_issued':False},exclusive=True)
            store.put('static_A.json',fresh_audit)
            store.put('dynamic_initial.json',first);store.put('dynamic_final.json',final)
            capfd=os.memfd_create('dcl-bc-activation',os.MFD_ALLOW_SEALING|os.MFD_CLOEXEC)
            os.fchmod(capfd,0o600);_full(capfd,canon(ticket));os.lseek(capfd,0,os.SEEK_SET)
            seals=fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL
            fcntl.fcntl(capfd,fcntl.F_ADD_SEALS,seals)
            store.put('capability.json',{'sha256':hashlib.sha256(canon(ticket)).hexdigest(),
                      'device':os.fstat(capfd).st_dev,'inode':os.fstat(capfd).st_ino,'seals':seals,'sample':stamp()})
            os.set_inheritable(lockfd,True);os.set_inheritable(capfd,True)
        if boot()!=epoch or now()>=ticket['expires']:raise Rejected('BC_PREEXEC_BOOT_OR_TIME')
        emit('ACTIVATION_REQUESTED_ONLY',ticket_sha256=hashlib.sha256(canon(ticket)).hexdigest(),launcher_started=False)
        env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','LC_ALL':'C.UTF-8',
             'DCL_BC_CAP_FD':str(capfd),'DCL_BC_LOCK_FD':str(lockfd)}
        # Same PID and start_ticks; no daemon or hidden keep-alive is introduced.
        os.execve(lock['launch_command'][0],lock['launch_command'],env)
    finally:
        if capfd is not None:os.close(capfd)
        if lockfd is not None:os.close(lockfd)


def read_capability():
    fd=int(os.environ['DCL_BC_CAP_FD']);lockfd=int(os.environ['DCL_BC_LOCK_FD'])
    s=os.fstat(fd);required=fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL
    if (not stat.S_ISREG(s.st_mode) or s.st_uid!=0 or stat.S_IMODE(s.st_mode)!=0o600 or s.st_size>65536 or
        fcntl.fcntl(fd,fcntl.F_GET_SEALS)&required!=required):raise Rejected('BC_SEALED_FD_REQUIRED')
    raw=os.pread(fd,s.st_size,0);ticket=json.loads(raw)
    with Store() as store:
        cap=store.read('capability.json');claim=store.read('activation.json')
        named=os.stat('activation.lock',dir_fd=store.fd,follow_symlinks=False);actual=os.fstat(lockfd)
        if (named.st_dev,named.st_ino)!=(actual.st_dev,actual.st_ino) or actual.st_uid!=0 or stat.S_IMODE(actual.st_mode)!=0o600:raise Rejected('BC_LOCK_FD_IDENTITY')
        fcntl.flock(lockfd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if cap['sha256']!=hashlib.sha256(raw).hexdigest() or (cap['device'],cap['inode'])!=(s.st_dev,s.st_ino) or claim['ticket']!=ticket:raise Rejected('BC_CAP_PROVENANCE')
    return fd,lockfd,ticket,claim


def guard_admission(G,resume):
    global _SESSION
    if _SESSION is None or bool(resume)!=(_SESSION['phase']=='resume'):raise Rejected('BC_ENTRY_WRAPPER_REQUIRED')
    fd,lockfd,ticket,claim=read_capability()
    if ticket['owner']!=identity() or ticket['boot_id']!=boot():raise Rejected('BC_ENTRY_OWNER')
    if resume:
        if not claim['initial_entered'] or not claim['resume_issued'] or _SESSION.get('resume_entered'):raise Rejected('BC_RESUME_ONCE')
        _SESSION['resume_entered']=True
    else:
        deadline=ticket['expires'];m,lock,_=artifact_check(deadline,boot())
        fresh=runtime_snapshot(m,lock,deadline,boot(),True)
        auth,_=G.authorization()
        actual_binding={'batch_id':G.ROOT.name,'static_manifest_sha256':G.digest(G.SOURCE.parent/'inputs/static_manifest.json'),
          'execution_lock_sha256':G.digest(G.SOURCE.parent/'inputs/execution_lock.json'),
          'authorization_text_sha256':auth['authorization_text_sha256'],
          'boot_contract_sha256':G.digest(G.SOURCE.parent/'inputs/boot_contract.json')}
        if fresh['root_cgroup']!=ticket['root_cgroup']:raise Rejected('BC_ROOT_CGROUP_CHANGED')
        fresh.update(binding=actual_binding,now=now(),sealed=True,cap_live=True)
        ticket_policy(ticket,fresh,claim)
        claim['initial_entered']=True
        with Store() as store:store.put('activation.json',claim)
    with Store() as store:store.put('entry_'+_SESSION['phase']+'.json',{'owner':identity(),'ticket_sha256':hashlib.sha256(canon(ticket)).hexdigest(),'phase':_SESSION['phase'],'sample':stamp()})
    emit('ENTRY_VERIFIED',phase=_SESSION['phase'],launcher_started=False)


def child_admission(G,resume):
    if _SESSION is None or identity(os.getppid())!=_SESSION['ticket']['owner'] or boot()!=_SESSION['ticket']['boot_id']:raise Rejected('BC_CHILD_PARENT_BINDING')
    if not resume and (G.ROOT/'inputs/batch_state.json').exists():raise Rejected('BC_CHILD_EXISTING_WINDOW')
    with Store() as store:store.put('child_'+('resume' if resume else 'initial')+'.json',{'child':G.identity(),'parent':G.identity(os.getppid()),'sample':stamp()})


def service_confirmed(G,t,lease=None):
    if t['case'] not in ('C00','C10'):return
    if _SESSION is None:raise Rejected('BC_CHILD_SESSION_MISSING')
    import service_readiness
    certificate=service_readiness.require_lease(G,t,lease)
    info=lease.info;s=G.state();owner=_SESSION['ticket']['owner']
    service_policy({'process_alive':G.identity(owner['pid'])==owner,'same_boot':s['boot_id']==owner['boot_id'],
                    'service_active':info.get('ActiveState')=='active','stable_main_pid':int(info.get('MainPID','0'))==t['main_identity']['pid'] and G.identity(t['main_identity']['pid'])==t['main_identity'],
                    'closed':G.stopped(),'stop':False})
    record={'schema':PROFILE,'status':'ACTUAL_SERVICE_CONFIRMED','owner':owner,'boot_id':boot(),
            'activation_sha256':hashlib.sha256(canon(_SESSION['ticket'])).hexdigest(),
            'binding':_SESSION['ticket']['binding'],'window':{k:s[k] for k in ['T0','deadline','stop_at','execution_mode']},
            'unit':info,'main_identity':t['main_identity'],'counter_snapshot':G.count(),'sample':stamp()}
    with Store() as store:store.put('BOOT_START.json' if t['case']=='C00' else 'BOOT_RESUME.json',record,exclusive=True,public=True)
    emit('ACTUAL_SERVICE_CONFIRMED',case=t['case'],main_identity=t['main_identity'],launcher_started=True,resource_gate='NOT_OBTAINED')


def formal_gate(G):
    verify_regression(G)
    s=G.state();start=G.trusted(G.ROOT/'inputs/BOOT_START.json');resume=G.trusted(G.ROOT/'inputs/BOOT_RESUME.json')
    q=G.trusted(G.ROOT/'inputs/BOOT_CONTINUITY_QUALIFICATION.json')
    if (start['boot_id']!=G.boot_id() or resume['boot_id']!=G.boot_id() or start['owner']!=resume['owner'] or
        G.identity(start['owner']['pid'])!=start['owner'] or q['binding']!=G.safety_binding() or
        q['start_sha256']!=G.digest(G.ROOT/'inputs/BOOT_START.json') or q['checker_sha256']!=G.digest(G.SOURCE/'boot_continuity_oracle.py') or
        q['contract_sha256']!=G.digest(G.SOURCE.parent/'inputs/boot_contract.json') or not q['accepted']):raise Rejected('BC_FORMAL_PROVENANCE')
    if start['window']!=resume['window'] or resume['window']!={k:s[k] for k in ['T0','deadline','stop_at','execution_mode']}:raise Rejected('BC_FORMAL_WINDOW')


def verify_regression(G):
    import boot_continuity_oracle
    cfg=G.trusted(G.SOURCE.parent/'inputs/boot_contract.json')
    q=G.trusted(G.ROOT/'inputs/BOOT_CONTINUITY_QUALIFICATION.json')
    if (q['binding']!=G.safety_binding() or q['contract_sha256']!=G.digest(G.SOURCE.parent/'inputs/boot_contract.json') or
        q['checker_sha256']!=G.digest(G.SOURCE/'boot_continuity_oracle.py') or not q['accepted']):raise Rejected('BC_QUALIFICATION_BINDING')
    expected={j['case_id']:j for j in cfg['jobs']}
    if len(q['results'])!=len(expected) or {r['case_id'] for r in q['results']}!=set(expected):raise Rejected('BC_QUALIFICATION_SET')
    for row in q['results']:
        j=expected[row['case_id']];target='PASS' if j['variant']=='safe' else 'MUTATION_DETECTED'
        if not row['accepted'] or row['status']!=target or not set(row['violations']).issubset(j['allowed_violations']):raise Rejected('BC_QUALIFICATION_RESULT')
    if os.geteuid()==0:
        fresh=boot_continuity_oracle.check_suite(G.ROOT/'inputs/root_private/boot',cfg,G.safety_binding())
        if not fresh['accepted'] or fresh['results']!=q['results']:raise Rejected('BC_QUALIFICATION_RAW')


def before_seal(G):
    if _SESSION is None or identity()!=_SESSION['ticket']['owner']:return
    with Store() as store:
        try:store.read('final_before_seal.json');return
        except FileNotFoundError:pass
        store.put('final_before_seal.json',{'owner':identity(),'sample':stamp(),'closed':G.stopped(),
                   'phase':_SESSION['phase'],'state':G.trusted(G.ROOT/'inputs/batch_state.json')})


def entry(G,resume=False,calibrate_only=False):
    global _SESSION
    if resume:raise Rejected('BC_NO_STANDALONE_RESUME')
    fd,lockfd,ticket,claim=read_capability()
    _SESSION={'ticket':ticket,'phase':'initial','resume_entered':False}
    try:
        result=G.launcher(False,calibrate_only)
        if result==23:
            a,_=G.authorization()
            if a['scope']!='CALIBRATE_S1S9_THEN_F1_F4' or a.get('SameProcess_C09_resume_explicitly_approved') is not True:raise Rejected('BC_RESUME_NOT_APPROVED')
            verify_regression(G)
            # Same Root process/session remains alive across the verified C09 handoff.
            with Store() as store:
                claim=store.read('activation.json')
                if claim['resume_issued'] or G.stopped() or boot()!=ticket['boot_id']:raise Rejected('BC_RESUME_REJECTED')
                s=G.state()
                if s['status']!='AWAIT_EXPECTED_RESUME' or s['resume_count']!=0:raise Rejected('BC_NO_C09_RESUME_STATE')
                claim['resume_issued']=True;store.put('activation.json',claim)
                store.put('resume_window.json',{'T0':s['T0'],'deadline':s['deadline'],'stop_at':s['stop_at'],'counter':G.count(),'sample':stamp()})
            _SESSION['phase']='resume';result=G.launcher(True,calibrate_only)
            if result==23:raise Rejected('BC_SECOND_HANDOFF_FORBIDDEN')
        return result
    except BaseException:
        if (G.ROOT/'inputs/batch_state.json').exists():
            try:G.stop_tree('BOOT_CONTINUITY_ENTRY_FAILURE');G.seal()
            except BaseException:pass
        raise
    finally:
        os.close(fd);os.close(lockfd);_SESSION=None


def main():
    p=argparse.ArgumentParser();p.add_argument('--activate',action='store_true',required=True)
    p.add_argument('--batch-root',choices=[str(ROOT)],required=True);p.parse_args()
    prepare_activation()


if __name__=='__main__':
    try:main()
    except BaseException as exc:
        print('BOOT_CONTINUITY_REJECTED',repr(exc),file=sys.stderr,flush=True)
        raise SystemExit(125)
