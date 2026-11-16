"""PT/1 explicit prewindow/runtime contracts. Administrative export has no grant API."""
from contextlib import contextmanager
import hashlib
import fcntl
import json
import math
import os
from pathlib import Path
import stat
import struct
import time
import boot_continuity as BC

PROFILE='PRET0-LIFECYCLE/1'
_QUERY_TOKEN=None
PHASES=('PRE_WINDOW','PREFLIGHT_VALIDATING','PREFLIGHT_QUALIFIED','RUNTIME_INITIALIZING','RUNTIME_READY','RUNTIME_ARMED','RUNNING')

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def sha(x):return hashlib.sha256(canonical(x)).hexdigest()
def phase_policy(f):
    if f['closed'] or f['stop']:return 'DENY_TERMINAL'
    if not all(f[k] for k in ('binding','boot','owner','deadline')):return 'DENY_IDENTITY_OR_DEADLINE'
    if f['phase'] in ('PRE_WINDOW','PREFLIGHT_VALIDATING','PREFLIGHT_QUALIFIED'):
        if not f['pre_context'] or f['runtime_intent'] or f['state'] or f['counter'] or f['runtime_checkpoint']:
            return 'DENY_PREWINDOW_DOWNGRADE'
        return 'PREWINDOW_ALLOWED_NO_WORK'
    if f['phase'] in ('RUNTIME_READY','RUNTIME_ARMED','RUNNING'):
        if not all(f[k] for k in ('runtime_intent','state','counter','runtime_checkpoint','checkpoint_integrity')):
            return 'DENY_RUNTIME_CHECKPOINT'
        return 'RUNTIME_INSPECTION_ALLOWED' if f['phase']=='RUNTIME_READY' else 'WORK_ALLOWED'
    return 'DENY_PHASE'
def config(G):
    a,m=G.authorization();p=G.SOURCE.parent/'inputs/startup_contract.json';c=G.trusted(p)
    if G.digest(p)!=m['startup_contract_sha256'] or a.get('startup_contract_sha256')!=m['startup_contract_sha256']:
        raise G.AdmissionBlocked('PT_CONTRACT_BINDING')
    if c['profile']!=PROFILE or c['batch_id']!=G.ROOT.name:raise G.AdmissionBlocked('PT_CONTRACT_IDENTITY')
    return c

def binding(G):
    return {'batch_id':G.ROOT.name,'root':str(G.ROOT),'boot_id':G.boot_id(),
        'manifest_sha256':G.digest(G.SOURCE.parent/'inputs/static_manifest.json'),
        'execution_lock_sha256':G.digest(G.SOURCE.parent/'inputs/execution_lock.json'),
        'authorization_sha256':G.digest(G.ROOT/'inputs/execution_authorization.json'),
        'startup_contract_sha256':G.digest(G.SOURCE.parent/'inputs/startup_contract.json')}

def _paths(G):
    return [G.ROOT/'inputs/batch_state.json',G.OUT/'visits.bin',G.OUT/'visits.bin.intent.json',
        G.OUT/'visits.bin.journal.jsonl',G.ROOT/'inputs/PT_RUNTIME_CHECKPOINT.json']

def runtime_intent_exists(G):return (G.ROOT/'inputs/root_private/boot/pt_runtime_intent.json').exists()

def _phase(G):
    with BC.Store() as store:return store.read('pt_phase.json')

def _phase_deadline(G):
    if (G.ROOT/'inputs/batch_state.json').exists():
        s=G.state()
        if s['boot_id']!=G.boot_id():raise G.AdmissionBlocked('PF_PHASE_BOOT')
        return min(s['deadline'],s['stop_at'],s['T0']+300 if s['status']=='CALIBRATING' else s['deadline'])
    with BC.Store() as store:c=store.read('pt_context.json')
    if c['binding']!=binding(G):raise G.AdmissionBlocked('PF_PHASE_CONTEXT')
    return c['preflight_deadline']

def _cancel(G,until,terminal_inspection=False):
    if not terminal_inspection and G.stopped():raise G.AdmissionBlocked('PF_TERMINAL_DOMINATES')
    if G.now()>=until:raise G.LimitReached('PF_PHASE_DEADLINE')

@contextmanager
def _phase_guard(G,terminal_inspection=False):
    """One existing Root-private mutex for full phase publication and Root reads."""
    if os.geteuid()!=0:raise G.AdmissionBlocked('PF_PHASE_ROOT_REQUIRED')
    until=min(G.now()+2,_phase_deadline(G));_cancel(G,until,terminal_inspection)
    with BC.Store() as store:
        fd=os.open('pt_phase.lock',os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=store.fd)
        acquired=False
        try:
            s=os.fstat(fd)
            if (s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)!=(0,0,0o600,1):raise G.AdmissionBlocked('PF_PHASE_LOCK_METADATA')
            for _ in range(512):
                _cancel(G,until,terminal_inspection)
                try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);acquired=True;break
                except BlockingIOError:time.sleep(min(.005,max(0,until-G.now())))
            if not acquired:raise G.AdmissionBlocked('PF_PHASE_LOCK_BOUND')
            _cancel(G,until,terminal_inspection)
            yield store,until
            _cancel(G,until,terminal_inspection)
        finally:
            if acquired:fcntl.flock(fd,fcntl.LOCK_UN)
            os.close(fd)

def _set_phase_locked(G,phase,store):
        try:old=store.read('pt_phase.json')
        except FileNotFoundError:old=None
        if old:
            if old['binding']!=binding(G):raise G.AdmissionBlocked('PT_PHASE_BINDING')
            if old['phase'] not in PHASES or old['sequence']!=PHASES.index(old['phase']):raise G.AdmissionBlocked('PF_PHASE_SEQUENCE')
            if old['phase']==phase:return old
            if old['phase'] not in PHASES or phase not in PHASES or PHASES.index(phase)!=PHASES.index(old['phase'])+1:
                raise G.AdmissionBlocked('PT_ILLEGAL_PHASE_TRANSITION')
        elif phase!='PRE_WINDOW':raise G.AdmissionBlocked('PT_PHASE_INITIALIZATION')
        d={'schema':PROFILE,'phase':phase,'sequence':0 if old is None else old['sequence']+1,
           'previous_sha256':sha(old) if old else None,'binding':binding(G),'sample':G.stamp()}
        raw=canonical(d)+b'\n';fd=os.open('pt_events.jsonl',os.O_WRONLY|os.O_CREAT|os.O_APPEND|os.O_NOFOLLOW,0o600,dir_fd=store.fd)
        try:os.fchown(fd,0,0);os.fchmod(fd,0o600);G._full(fd,raw);os.fsync(fd);os.fsync(store.fd)
        finally:os.close(fd)
        store.put('pt_phase.json',d)
        return d

def _set_phase(G,phase):
    with _phase_guard(G) as (store,until):return _set_phase_locked(G,phase,store)

def phase_snapshot_policy(f):
    """Pure decision surface for frozen synthetic PF fixtures; no IO or authority."""
    if f['closed'] or f['stop']:return 'DENY_TERMINAL'
    if not f['binding'] or not f['identity'] or not f['deadline']:return 'DENY_IDENTITY'
    if not f['lock_acquired']:return 'WAIT_BOUNDED'
    if f['phase'] not in PHASES[4:] or f['sequence']!=PHASES.index(f['phase']):return 'DENY_PHASE'
    if not all(f[k] for k in ('committed','checkpoint_integrity','initialization_match')):return 'DENY_CHECKPOINT'
    if f['root_reader'] and (f['phase']!=f['private_phase'] or f['sequence']!=f['private_sequence'] or not f['record_hash_match']):return 'DENY_VERSION'
    if f['work'] and f['phase'] not in ('RUNTIME_ARMED','RUNNING'):return 'DENY_WORK'
    return 'ACCEPT'

def _live_ticket(G):
    if os.geteuid()!=0 or BC._SESSION is None or BC._SESSION['phase']!='initial':raise G.AdmissionBlocked('PT_INITIAL_SESSION_REQUIRED')
    _,_,ticket,claim=BC.read_capability()
    if ticket!=BC._SESSION['ticket'] or not claim['initial_entered'] or ticket['boot_id']!=G.boot_id():raise G.AdmissionBlocked('PT_INITIAL_CLAIM')
    me=G.identity();owner=ticket['owner']
    if me!=owner and G.identity(os.getppid())!=owner:raise G.AdmissionBlocked('PT_CALLER_OWNER')
    import c09_handoff as H
    if not H.alive(G,owner):raise G.AdmissionBlocked('PT_OWNER_NOT_LIVE')
    if (ticket['binding']['batch_id']!=G.ROOT.name or ticket['binding']['static_manifest_sha256']!=G.digest(G.SOURCE.parent/'inputs/static_manifest.json') or
        ticket['binding']['execution_lock_sha256']!=G.digest(G.SOURCE.parent/'inputs/execution_lock.json') or
        ticket['binding']['authorization_receipt_sha256']!=G.digest(G.ROOT/'inputs/execution_authorization.json')):
        raise G.AdmissionBlocked('PT_LIVE_STARTUP_BINDING')
    deadline=ticket['preflight_deadline']
    if not isinstance(deadline,(int,float)) or not math.isfinite(deadline) or G.now()>=deadline:raise G.LimitReached('PT_STARTUP_TCB_DEADLINE')
    return ticket

def enter(G):
    config(G)
    if G.stopped() or runtime_intent_exists(G) or any(p.exists() for p in _paths(G)):raise G.AdmissionBlocked('PT_NOT_FRESH_PREWINDOW')
    ticket=_live_ticket(G)
    with BC.Store() as store:
        try:c=store.read('pt_context.json')
        except FileNotFoundError:
            c={'schema':'PT-STARTUP-CONTEXT/1','binding':binding(G),'owner':ticket['owner'],
                'activation_ticket_sha256':sha(ticket),'preflight_deadline':ticket['preflight_deadline'],
                'startup_begin_inferred':ticket['preflight_deadline']-120,'T0':None,'R':None,'sample':G.stamp()}
            store.put('pt_context.json',c,exclusive=True)
        if c['binding']!=binding(G) or c['activation_ticket_sha256']!=sha(ticket):raise G.AdmissionBlocked('PT_CONTEXT_CONFLICT')
    if not(G.ROOT/'inputs/root_private/boot/pt_phase.json').exists():_set_phase(G,'PRE_WINDOW')
    return c

def prewindow_checkpoint(G):
    if G.stopped() or runtime_intent_exists(G) or any(p.exists() for p in _paths(G)):raise G.AdmissionBlocked('PT_PREWINDOW_DOWNGRADE_REJECTED')
    ticket=_live_ticket(G)
    with BC.Store() as store:c=store.read('pt_context.json')
    if c['binding']!=binding(G) or c['activation_ticket_sha256']!=sha(ticket) or c['owner']!=ticket['owner']:
        raise G.AdmissionBlocked('PT_PREWINDOW_CONTEXT')
    if _phase(G)['phase'] not in ('PRE_WINDOW','PREFLIGHT_VALIDATING','PREFLIGHT_QUALIFIED'):raise G.AdmissionBlocked('PT_PREWINDOW_PHASE')
    facts=dict(phase=_phase(G)['phase'],closed=False,stop=False,binding=True,boot=True,owner=True,deadline=True,
        pre_context=True,runtime_intent=False,state=False,counter=False,runtime_checkpoint=False,checkpoint_integrity=True)
    if phase_policy(facts)!='PREWINDOW_ALLOWED_NO_WORK':raise G.AdmissionBlocked('PT_PREWINDOW_POLICY')
    return c

@contextmanager
def initial_query_scope(G):
    global _QUERY_TOKEN
    c=prewindow_checkpoint(G)
    if _QUERY_TOKEN is not None:raise G.AdmissionBlocked('PT_NESTED_PREWINDOW_SCOPE')
    _set_phase(G,'PREFLIGHT_VALIDATING');_QUERY_TOKEN={'G':G,'context_sha256':sha(c)}
    try:yield
    finally:_QUERY_TOKEN=None

def manager_checkpoint(G):
    if _QUERY_TOKEN is not None and _QUERY_TOKEN['G'] is G:
        c=prewindow_checkpoint(G)
        if sha(c)!=_QUERY_TOKEN['context_sha256']:raise G.AdmissionBlocked('PT_QUERY_CONTEXT_DRIFT')
        return c
    return G.root_checkpoint()

def query_deadline(G,until):
    if _QUERY_TOKEN is not None and _QUERY_TOKEN['G'] is G:return min(until,prewindow_checkpoint(G)['preflight_deadline'])
    return until

def qualify(G):
    prewindow_checkpoint(G)
    return _set_phase(G,'PREFLIGHT_QUALIFIED')

def begin_runtime(G):
    prewindow_checkpoint(G)
    if _phase(G)['phase']!='PREFLIGHT_QUALIFIED':raise G.AdmissionBlocked('PT_PREQUALIFICATION_REQUIRED')
    with BC.Store() as store:
        intent={'schema':'PT-RUNTIME-INTENT/1','binding':binding(G),'prequalified_sha256':sha(_phase(G)),'sample':G.stamp()}
        store.put('pt_runtime_intent.json',intent,exclusive=True)
    _set_phase(G,'RUNTIME_INITIALIZING')

def initialization_guard(G):
    if G.stopped():raise G.AdmissionBlocked('PT_INITIALIZATION_STOPPED')
    _live_ticket(G)
    with BC.Store() as store:intent=store.read('pt_runtime_intent.json')
    if intent['binding']!=binding(G) or _phase(G)['phase']!='RUNTIME_INITIALIZING':raise G.AdmissionBlocked('PT_INITIALIZATION_PHASE')

def _budget_identity(G):
    p=G.OUT/'visits.bin';fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
    try:
        s=os.fstat(fd)
        if not stat.S_ISREG(s.st_mode) or s.st_size!=24 or os.pread(fd,8,0)!=b'BRNGv001' or struct.unpack('<Q',os.pread(fd,8,16))[0]!=G.VISIT_CAP:
            raise G.AdmissionBlocked('PT_COUNTER_IDENTITY')
        return {'device':s.st_dev,'inode':s.st_ino,'cap':G.VISIT_CAP,'magic':'BRNGv001'}
    finally:os.close(fd)

def runtime_ready(G):
    initialization_guard(G);s=G.trusted(G.ROOT/'inputs/batch_state.json');raw=(G.OUT/'visits.bin').read_bytes()
    intent=G.read(G.OUT/'visits.bin.intent.json')
    if (s['boot_id']!=G.boot_id() or s['status']!='CALIBRATING' or abs(s['deadline']-s['T0']-1800)>1e-6 or abs(s['stop_at']-s['T0']-1740)>1e-6 or
        len(raw)!=24 or struct.unpack('<Q',raw[8:16])[0]!=0 or intent.get('status')!='COMMITTED' or intent.get('after')!=0 or intent.get('cap')!=G.VISIT_CAP):
        raise G.AdmissionBlocked('PT_RUNTIME_CREATION_INCOMPLETE')
    with _phase_guard(G) as (store,until):
        initialization_guard(G);ident=_budget_identity(G);initial=store.read('pt_runtime_intent.json')
        phase=_set_phase_locked(G,'RUNTIME_READY',store)
        G._root_write(G.ROOT/'inputs/PT_RUNTIME_CHECKPOINT.json',{'schema':'PT-RUNTIME-CHECKPOINT/1','binding':binding(G),
            'initialization_id':sha(initial),'window':{k:s[k] for k in ('T0','deadline','stop_at')},'counter':ident,
            'phase':phase['phase'],'sequence':phase['sequence'],'phase_record_sha256':sha(phase),'committed':True,'sample':G.stamp()})

def _runtime_checkpoint_locked(G,s,store=None,terminal_inspection=False):
    q=G.trusted(G.ROOT/'inputs/PT_RUNTIME_CHECKPOINT.json')
    if (q['schema']!='PT-RUNTIME-CHECKPOINT/1' or q['binding']!=binding(G) or q['window']!={k:s[k] for k in ('T0','deadline','stop_at')} or
        q['phase'] not in ('RUNTIME_READY','RUNTIME_ARMED','RUNNING') or q['counter']!=_budget_identity(G)):
        raise G.AdmissionBlocked('PT_RUNTIME_CHECKPOINT_CORRUPT')
    p=G.OUT/'visits.bin.intent.json';meta=p.lstat()
    if not stat.S_ISREG(meta.st_mode):raise G.AdmissionBlocked('PT_RUNTIME_INTENT_MISSING_OR_TYPE')
    root=store is not None
    i=store.read('pt_runtime_intent.json') if root else None
    phase=store.read('pt_phase.json') if root else None
    if root and (phase['binding']!=binding(G) or i['binding']!=binding(G)):raise G.AdmissionBlocked('PF_PRIVATE_BINDING')
    facts={'closed':False if terminal_inspection else G.stopped(),'stop':False,'binding':True,'identity':True,
        'deadline':G.now()<min(s['deadline'],s['stop_at']),'lock_acquired':True,
        'phase':q['phase'],'sequence':q['sequence'],'committed':q.get('committed') is True,
        'checkpoint_integrity':True,'initialization_match':not root or sha(i)==q['initialization_id'],
        'root_reader':root,'private_phase':phase['phase'] if root else None,'private_sequence':phase['sequence'] if root else None,
        'record_hash_match':not root or q.get('phase_record_sha256')==sha(phase),'work':False}
    decision=phase_snapshot_policy(facts)
    if decision!='ACCEPT':
        detail={k:facts[k] for k in ('phase','sequence','private_phase','private_sequence','initialization_match','record_hash_match')}
        raise G.AdmissionBlocked('PT_RUNTIME_PHASE_DRIFT:'+decision+':'+json.dumps(detail,sort_keys=True))
    # No concurrent used/intent consistency test here: reserve_core owns its lock.
    return q

def runtime_checkpoint(G,s,terminal_inspection=False):
    if os.geteuid()==0:
        with _phase_guard(G,terminal_inspection) as (store,until):return _runtime_checkpoint_locked(G,s,store,terminal_inspection)
    if terminal_inspection:raise G.AdmissionBlocked('PF_TERMINAL_INSPECTION_ROOT')
    q=_runtime_checkpoint_locked(G,s)
    if G.stopped():raise G.AdmissionBlocked('PF_TERMINAL_DOMINATES')
    return q

def _commit_phase(G,s,q,target,store):
    if G.identity()!=s['launcher_identity']:raise G.AdmissionBlocked('PF_PHASE_WRITER_IDENTITY')
    phase=_set_phase_locked(G,target,store)
    q.update(phase=phase['phase'],sequence=phase['sequence'],phase_record_sha256=sha(phase),committed=True,sample=G.stamp())
    G._root_write(G.ROOT/'inputs/PT_RUNTIME_CHECKPOINT.json',q)
    return q

def arm(G):
    with _phase_guard(G) as (store,until):
        s=G.state();q=_runtime_checkpoint_locked(G,s,store);arm=G.trusted(G.ROOT/'inputs/STOP_ARMED.json')
        import c09_handoff as H
        if q['phase']!='RUNTIME_READY':raise G.AdmissionBlocked('PF_ARM_SOURCE_PHASE')
        if arm['boot_id']!=G.boot_id() or arm['stop_at']!=s['stop_at'] or not H.alive(G,arm['identity']):raise G.AdmissionBlocked('PT_STOP_SOURCE_NOT_ARMED')
        _commit_phase(G,s,q,'RUNTIME_ARMED',store)

def require_work(G):
    with _phase_guard(G) as (store,until):
        s=G.state();q=_runtime_checkpoint_locked(G,s,store)
        if G.identity()!=s['launcher_identity']:raise G.AdmissionBlocked('PF_WORK_WRITER_IDENTITY')
        if q['phase'] not in ('RUNTIME_ARMED','RUNNING'):raise G.AdmissionBlocked('PT_NO_PREWINDOW_WORK')
        if q['phase']=='RUNTIME_ARMED':_commit_phase(G,s,q,'RUNNING',store)

def formal_gate(G):
    cfg=config(G);q=G.trusted(G.ROOT/'inputs/PT_QUALIFICATION.json')
    if (q['binding']!=G.safety_binding() or not q['accepted'] or q['contract_sha256']!=G.digest(G.SOURCE.parent/'inputs/startup_contract.json') or
        q['checker_sha256']!=G.digest(G.SOURCE/'startup_oracle.py') or len(q['results'])!=len(cfg['jobs']) or
        {r['case_id'] for r in q['results']}!={j['case_id'] for j in cfg['jobs']}):raise G.AdmissionBlocked('PT_FORMAL_QUALIFICATION')
    jobs={j['case_id']:j for j in cfg['jobs']}
    for row in q['results']:
        target='MUTATION_DETECTED' if jobs[row['case_id']]['mutant'] else 'PASS'
        if not row['accepted'] or row['status']!=target:raise G.AdmissionBlocked('PT_REQUIRED_RESULT')
    import phase_finalizer_regression as F
    F.verify(G)
    runtime_checkpoint(G,G.state())

def expected_prewindow_abort(G):
    c=prewindow_checkpoint(G);a,_=G.authorization()
    if a['scope']!='PT_STARTUP_DIAGNOSTIC_ONLY' or a.get('startup_probe_mode')!='PREWINDOW_ABORT' or a.get('PreWindow_abort_injection_explicitly_approved') is not True:
        raise G.AdmissionBlocked('PT_ABORT_PROBE_NOT_APPROVED')
    with BC.Store() as store:store.put('pt_expected_abort.json',{'schema':'PT-EXPECTED-ABORT/1','binding':binding(G),
        'context_sha256':sha(c),'expected_exit':77,'T0':None,'R':None,'sample':G.stamp()},exclusive=True)
    import manager_recovery as M
    return M.fail(G,'PT_EXPECTED_PREWINDOW_ABORT',77,True)

def cleanup_deadline(G):
    """Terminal-only authority: existing Root-protected activation, no grant mint."""
    with BC.Store() as store:
        activation=store.read('activation.json');ticket=activation['ticket']
        try:ctx=store.read('pt_context.json')
        except FileNotFoundError:ctx=None
        try:i=store.read('pt_runtime_intent.json')
        except FileNotFoundError:i=None
    if (not activation['initial_entered'] or ticket['boot_id']!=G.boot_id() or
        ticket['binding']['batch_id']!=G.ROOT.name or ticket['binding']['static_manifest_sha256']!=G.digest(G.SOURCE.parent/'inputs/static_manifest.json') or
        ticket['binding']['execution_lock_sha256']!=G.digest(G.SOURCE.parent/'inputs/execution_lock.json')):
        raise G.AdmissionBlocked('PT_ABORT_CONTEXT_UNTRUSTED')
    if i is not None:
        q=G.trusted(G.ROOT/'inputs/PT_RUNTIME_CHECKPOINT.json')
        if q['binding']['boot_id']!=G.boot_id():raise G.AdmissionBlocked('PT_ABORT_RUNTIME_BOOT')
        return {'deadline':q['window']['deadline'],'phase':'RUNTIME','source':'Existing runtime checkpoint'}
    if any(p.exists() for p in _paths(G)):raise G.AdmissionBlocked('PT_PARTIAL_RUNTIME_NOT_PREWINDOW')
    if ctx and ctx['activation_ticket_sha256']!=sha(ticket):raise G.AdmissionBlocked('PT_ABORT_CONTEXT_DIGEST')
    return {'deadline':ticket['preflight_deadline'],'phase':'PRE_WINDOW','source':'Inherited authenticated120s startup TCB; no new window'}

def seal_applicability(G):
    present=[p.exists() for p in _paths(G)]
    if not runtime_intent_exists(G) and not any(present):return 'NATIVE_SEAL_NOT_APPLICABLE'
    try:
        s=G.trusted(G.ROOT/'inputs/batch_state.json');runtime_checkpoint(G,s,terminal_inspection=True)
        with BC.Store() as store:
            try:close=store.read('mr_close_state.json')
            except FileNotFoundError:close=None
        if close and close['status']!='CLOSED_CLEANUP_CONFIRMED':return 'NATIVE_SEAL_UNRESOLVED'
        return 'RUNTIME_NATIVE_SEAL_APPLICABLE'
    except (OSError,ValueError,KeyError,G.AdmissionBlocked):return 'NATIVE_SEAL_UNRESOLVED'

def defer_startup_seal(G,kind):
    with BC.Store() as store:store.put('pt_seal_disposition.json',{'native_seal_status':kind,
        'administrative_seal_status':'POST_EXIT_FINALIZER_PENDING','T0':None if kind=='NATIVE_SEAL_NOT_APPLICABLE' else 'UNRESOLVED',
        'process_cleanup':'Separately audited after caller exit','startup_result':'STARTUP_ABORTED_PRE_T0' if kind=='NATIVE_SEAL_NOT_APPLICABLE' else 'RUNTIME_SEAL_UNRESOLVED',
        'sample':G.stamp()})
    return None

def administrative_policy(f):
    """Independent cleanup/native/admin axes; no writes, grants or budget API."""
    cleanup='CLEANUP_CONFIRMED' if f['roles_empty'] and f['group_absent'] and not f['audit_error'] else 'CLEANUP_UNKNOWN'
    if not f['any_runtime']:native='NATIVE_SEAL_NOT_APPLICABLE'
    elif f['native_verified']:native='NATIVE_SEAL_COMPLETED'
    elif f['native_error']:native='NATIVE_SEAL_FAILED'
    else:native='NATIVE_SEAL_UNRESOLVED'
    admin='EXPORT_ALLOWED' if cleanup=='CLEANUP_CONFIRMED' else 'DEFERRED_ACTIVE_WRITERS'
    failed=any(not f.get(k,True) for k in ('module_ready','permission_ok','evidence_integrity')) or f.get('exception',False)
    if failed:admin='ADMIN_EVIDENCE_UNRESOLVED'
    if f.get('repeated',False):admin='RETURN_EXISTING_ADMIN_SEAL' if f.get('repeat_valid',False) else 'ADMIN_EVIDENCE_UNRESOLVED'
    return {'process_cleanup_status':cleanup,'native_seal_status':native,'administrative_export_status':admin,
        'internal_cleanup_status':f['internal_status'],'error_recorded':failed or (f.get('repeated',False) and not f.get('repeat_valid',False))}

def _postexit_roles(source,root,slice_name):
    roles=[];payload=[];errors=[]
    for p in Path('/proc').glob('[0-9]*'):
        try:
            args=(p/'cmdline').read_bytes().decode(errors='replace').split('\0')
            status=dict(s.split(':',1) for s in (p/'status').read_text().splitlines() if ':' in s)
            if '--batch-root' in args and str(root) in args and any(str(source/name) in args for name in ('guard.py','boot_continuity.py')):
                roles.append({'pid':int(p.name),'start_ticks':BC.identity(int(p.name))['start_ticks'],'args':args})
            if 999 in map(int,status['Uid'].split()):payload.append(int(p.name))
        except FileNotFoundError:pass
        except (OSError,ValueError,KeyError) as exc:errors.append({'pid':p.name,'error':type(exc).__name__})
    return roles,payload,Path('/sys/fs/cgroup',slice_name).exists(),errors

def post_exit_export():
    """Automatic audit/export only; never initializes, resumes or grants work."""
    import resource
    import signal
    resource.setrlimit(resource.RLIMIT_AS,(1<<30,1<<30))
    signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(30)
    source=Path(__file__).resolve().parent;identity=BC.NAMESPACE;root=Path(identity['runtime_root'])
    if os.geteuid()!=0 or str(source)!=identity['source_root']+'/src':raise RuntimeError('PT_POSTEXIT_SOURCE')
    manifest=BC.trusted(source.parent/'inputs/static_manifest.json');lock=BC.trusted(source.parent/'inputs/execution_lock.json')
    if BC.digest(source.parent/'inputs/static_manifest.json')!=lock['static_manifest_sha256']:raise RuntimeError('PT_POSTEXIT_MANIFEST')
    for name,expected in manifest['source_hashes'].items():
        if BC.digest(source/name)!=expected:raise RuntimeError('PT_POSTEXIT_SOURCE_DRIFT')
    for rel,expected in manifest['bound_inputs'].items():
        if BC.digest(source.parent/rel)!=expected:raise RuntimeError('PT_POSTEXIT_INPUT_DRIFT')
    began=BC.now();wait_until=began+5
    # Existing execution expiry only reduces waiting; administrative IO keeps its own30s alarm.
    state_path=root/'inputs/batch_state.json';activation=root/'inputs/root_private/boot/activation.json'
    if state_path.exists():
        try:wait_until=min(wait_until,BC.trusted(state_path)['deadline'])
        except (OSError,ValueError,KeyError):wait_until=began
    elif activation.exists():
        try:wait_until=min(wait_until,BC.trusted(activation)['ticket']['preflight_deadline'])
        except (OSError,ValueError,KeyError):wait_until=began
    audit_history=[]
    for _ in range(128):
        role_processes,payload,group_exists,audit_errors=_postexit_roles(source,root,identity['slice'])
        audit_history.append({'sample':BC.stamp(),'role_pids':[r['pid'] for r in role_processes],'payload_pids':payload,
            'parent_cgroup_exists':group_exists,'errors':audit_errors})
        if (not role_processes and not payload and not group_exists and not audit_errors) or BC.now()>=wait_until or audit_errors:break
        time.sleep(min(.02,max(0,wait_until-BC.now())))
    cp=root/'inputs/PT_RUNTIME_CHECKPOINT.json';state=root/'inputs/batch_state.json';counter=root/'out/visits.bin'
    runtime_intent=root/'inputs/root_private/boot/pt_runtime_intent.json'
    actual={'runtime_intent':runtime_intent.exists(),'state':state.exists(),'counter':counter.exists(),'checkpoint':cp.exists()}
    native_zip=root/'out/EVIDENCE.zip';closed=root/'inputs/CLOSED.json';native_status='NATIVE_SEAL_UNRESOLVED'
    if not any(actual.values()):native_status='NATIVE_SEAL_NOT_APPLICABLE'
    elif all(actual.values()) and native_zip.exists():
        import zipfile
        try:
            declared=json.loads((root/'out/EVIDENCE_MANIFEST.json').read_bytes())['files']
            with zipfile.ZipFile(native_zip) as z:
                for name,row in declared.items():
                    expected=row['sha256'] if isinstance(row,dict) else row
                    if hashlib.sha256(z.read(name)).hexdigest()!=expected:raise ValueError('PT_NATIVE_ARCHIVE_DIGEST')
            native_status='NATIVE_SEAL_COMPLETED'
        except (OSError,ValueError,KeyError,zipfile.BadZipFile):native_status='NATIVE_SEAL_UNRESOLVED'
    elif all(actual.values()) and (root/'inputs/SEAL_ERROR.json').exists():native_status='NATIVE_SEAL_FAILED'
    result={'schema':'PT-POSTEXIT/1','batch_id':identity['batch_id'],'source_revision':identity['revision'],
        'observation_boot_id':BC.boot(),'observation':BC.stamp(),'runtime_objects':actual,'native_seal_status':native_status,
        'role_processes':role_processes,'payload_pids':payload,'parent_cgroup_exists':group_exists,'audit_errors':audit_errors,
        'quiescence_samples':audit_history,'quiescence_wait_bound_seconds':5,'quiescence_sample_bound':128,
        'closed_marker':closed.exists(),'T0':None,'R':None,'files':[],'nonregular':[],
        'source_manifest_sha256':BC.digest(source.parent/'inputs/static_manifest.json'),'execution_lock_sha256':BC.digest(source.parent/'inputs/execution_lock.json')}
    if state.exists():
        try:result['T0']=BC.trusted(state)['T0']
        except (OSError,ValueError,KeyError):result['T0']='UNRESOLVED'
    if counter.exists():
        try:
            raw=counter.read_bytes()
            result['R']=struct.unpack('<Q',raw[8:16])[0] if len(raw)==24 and raw[:8]==b'BRNGv001' else 'UNRESOLVED'
        except (OSError,ValueError):result['R']='UNRESOLVED'
    try:internal=BC.trusted(root/'inputs/root_private/boot/mr_close_state.json')['status']
    except (OSError,ValueError,KeyError):internal='UNKNOWN'
    verdict=administrative_policy({'roles_empty':not role_processes and not payload,'group_absent':not group_exists,
        'audit_error':bool(audit_errors),'any_runtime':any(actual.values()),'native_verified':native_status=='NATIVE_SEAL_COMPLETED',
        'native_error':native_status=='NATIVE_SEAL_FAILED','internal_status':internal})
    result.update(verdict)
    if native_status=='NATIVE_SEAL_COMPLETED':result['native_zip_sha256']=BC.digest(native_zip)
    control=Path(identity['linux_control'])
    # Independent administrative record; runtime originals and native seal records are read-only.
    with (control/'STARTUP_NATIVE_AUDIT.json').open('x',encoding='utf-8') as receipt:
        json.dump(result,receipt,ensure_ascii=False,indent=2);receipt.flush();os.fsync(receipt.fileno())
    if verdict['administrative_export_status']!='EXPORT_ALLOWED':print(json.dumps(result,ensure_ascii=False));return
    cfg=BC.trusted(source.parent/'inputs/startup_contract.json');control=Path(identity['linux_control']);dest=control/'startup_snapshot'
    if dest.exists():raise RuntimeError('PT_POSTEXIT_EXPORT_ALREADY_EXISTS')
    dest.mkdir();count=0;total=0
    for p in sorted(root.rglob('*')):
        s=p.lstat();rel=p.relative_to(root).as_posix()
        if stat.S_ISDIR(s.st_mode):continue
        meta={'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode),'device':s.st_dev,'inode':s.st_ino}
        if not stat.S_ISREG(s.st_mode):result['nonregular'].append({'relative':rel,'type':stat.S_IFMT(s.st_mode),**meta});continue
        count+=1;total+=s.st_size
        if count>cfg['admin_max_files'] or total>cfg['admin_max_bytes']:raise RuntimeError('PT_ADMIN_EVIDENCE_BOUND')
        q=dest/rel;q.parent.mkdir(parents=True,exist_ok=True);digest=hashlib.sha256()
        with p.open('rb') as src,q.open('xb') as out:
            while True:
                b=src.read(65536)
                if not b:break
                out.write(b);digest.update(b)
        result['files'].append({'relative':rel,'bytes':s.st_size,'sha256':digest.hexdigest(),**meta})
    result['administrative_export_status']='EXPORTED_QUIESCENT_STARTUP_EVIDENCE'
    result['startup_status']=('STARTUP_ABORTED_PRE_T0' if not any(actual.values()) else
        'INITIALIZATION_PARTIAL_UNRESOLVED' if not all(actual.values()) else
        'RUNTIME_CLOSED' if closed.exists() else 'RUNTIME_EXIT_UNRESOLVED')
    try:
        first=BC.trusted(root/'inputs/root_private/boot/mr_first_failure.json')
        result['first_failure']={k:first.get(k) for k in ('reason','error_type','expected_diagnostic','sample','window')}
    except (OSError,ValueError,KeyError):pass
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--post-exit-export',action='store_true',required=True);parser.parse_args()
    post_exit_export()
