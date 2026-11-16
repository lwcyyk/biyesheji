"""PT/1 explicit prewindow/runtime contracts. Administrative export has no grant API."""
from contextlib import contextmanager
import hashlib
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

def _set_phase(G,phase):
    import manager_recovery as M
    with M.locked(G,'pt_phase.lock') as store:
        try:old=store.read('pt_phase.json')
        except FileNotFoundError:old=None
        if old:
            if old['binding']!=binding(G):raise G.AdmissionBlocked('PT_PHASE_BINDING')
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
    ident=_budget_identity(G);phase=_set_phase(G,'RUNTIME_READY')
    with BC.Store() as store:initial=store.read('pt_runtime_intent.json')
    G._root_write(G.ROOT/'inputs/PT_RUNTIME_CHECKPOINT.json',{'schema':'PT-RUNTIME-CHECKPOINT/1','binding':binding(G),
        'initialization_id':sha(initial),'window':{k:s[k] for k in ('T0','deadline','stop_at')},'counter':ident,
        'phase':phase['phase'],'sequence':phase['sequence'],'sample':G.stamp()})

def runtime_checkpoint(G,s):
    q=G.trusted(G.ROOT/'inputs/PT_RUNTIME_CHECKPOINT.json')
    if (q['schema']!='PT-RUNTIME-CHECKPOINT/1' or q['binding']!=binding(G) or q['window']!={k:s[k] for k in ('T0','deadline','stop_at')} or
        q['phase'] not in ('RUNTIME_READY','RUNTIME_ARMED','RUNNING') or q['counter']!=_budget_identity(G)):
        raise G.AdmissionBlocked('PT_RUNTIME_CHECKPOINT_CORRUPT')
    p=G.OUT/'visits.bin.intent.json';meta=p.lstat()
    if not stat.S_ISREG(meta.st_mode):raise G.AdmissionBlocked('PT_RUNTIME_INTENT_MISSING_OR_TYPE')
    if os.geteuid()==0:
        with BC.Store() as store:i=store.read('pt_runtime_intent.json')
        if sha(i)!=q['initialization_id'] or _phase(G)['phase']!=q['phase']:raise G.AdmissionBlocked('PT_RUNTIME_PHASE_DRIFT')
    # No concurrent used/intent consistency test here: reserve_core owns its lock.
    return q

def arm(G):
    s=G.state();runtime_checkpoint(G,s);arm=G.trusted(G.ROOT/'inputs/STOP_ARMED.json')
    import c09_handoff as H
    if arm['boot_id']!=G.boot_id() or arm['stop_at']!=s['stop_at'] or not H.alive(G,arm['identity']):raise G.AdmissionBlocked('PT_STOP_SOURCE_NOT_ARMED')
    phase=_set_phase(G,'RUNTIME_ARMED');q=G.trusted(G.ROOT/'inputs/PT_RUNTIME_CHECKPOINT.json');q.update(phase=phase['phase'],sequence=phase['sequence'],sample=G.stamp())
    G._root_write(G.ROOT/'inputs/PT_RUNTIME_CHECKPOINT.json',q)

def require_work(G):
    if G.stopped():raise G.AdmissionBlocked('PT_WORK_AFTER_STOP')
    s=G.state();q=runtime_checkpoint(G,s)
    if q['phase'] not in ('RUNTIME_ARMED','RUNNING'):raise G.AdmissionBlocked('PT_NO_PREWINDOW_WORK')
    if q['phase']=='RUNTIME_ARMED':
        p=_set_phase(G,'RUNNING');q.update(phase=p['phase'],sequence=p['sequence'],sample=G.stamp());G._root_write(G.ROOT/'inputs/PT_RUNTIME_CHECKPOINT.json',q)

def formal_gate(G):
    cfg=config(G);q=G.trusted(G.ROOT/'inputs/PT_QUALIFICATION.json')
    if (q['binding']!=G.safety_binding() or not q['accepted'] or q['contract_sha256']!=G.digest(G.SOURCE.parent/'inputs/startup_contract.json') or
        q['checker_sha256']!=G.digest(G.SOURCE/'startup_oracle.py') or len(q['results'])!=len(cfg['jobs']) or
        {r['case_id'] for r in q['results']}!={j['case_id'] for j in cfg['jobs']}):raise G.AdmissionBlocked('PT_FORMAL_QUALIFICATION')
    jobs={j['case_id']:j for j in cfg['jobs']}
    for row in q['results']:
        target='MUTATION_DETECTED' if jobs[row['case_id']]['mutant'] else 'PASS'
        if not row['accepted'] or row['status']!=target:raise G.AdmissionBlocked('PT_REQUIRED_RESULT')
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
        s=G.trusted(G.ROOT/'inputs/batch_state.json');runtime_checkpoint(G,s)
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

def post_exit_export():
    """Automatic audit/export only; never initializes, resumes or grants work."""
    import resource
    resource.setrlimit(resource.RLIMIT_AS,(1<<30,1<<30))
    source=Path(__file__).resolve().parent;identity=BC.NAMESPACE;root=Path(identity['runtime_root'])
    if os.geteuid()!=0 or str(source)!=identity['source_root']+'/src':raise RuntimeError('PT_POSTEXIT_SOURCE')
    manifest=BC.trusted(source.parent/'inputs/static_manifest.json');lock=BC.trusted(source.parent/'inputs/execution_lock.json')
    if BC.digest(source.parent/'inputs/static_manifest.json')!=lock['static_manifest_sha256']:raise RuntimeError('PT_POSTEXIT_MANIFEST')
    for name,expected in manifest['source_hashes'].items():
        if BC.digest(source/name)!=expected:raise RuntimeError('PT_POSTEXIT_SOURCE_DRIFT')
    for rel,expected in manifest['bound_inputs'].items():
        if BC.digest(source.parent/rel)!=expected:raise RuntimeError('PT_POSTEXIT_INPUT_DRIFT')
    role_processes=[];payload=[]
    for p in Path('/proc').glob('[0-9]*'):
        try:
            args=(p/'cmdline').read_bytes().decode(errors='replace').split('\0')
            status=dict(s.split(':',1) for s in (p/'status').read_text().splitlines() if ':' in s)
            if '--batch-root' in args and str(root) in args and str(source/'guard.py') in args:
                role_processes.append({'pid':int(p.name),'args':args})
            if 999 in map(int,status['Uid'].split()):payload.append(int(p.name))
        except (OSError,ValueError,KeyError):pass
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
        'role_processes':role_processes,'payload_pids':payload,'parent_cgroup_exists':Path('/sys/fs/cgroup',identity['slice']).exists(),
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
    if role_processes or payload or result['parent_cgroup_exists']:
        result['process_cleanup_status']='CLEANUP_UNKNOWN';result['administrative_export_status']='DEFERRED_ACTIVE_WRITERS'
        print(json.dumps(result,ensure_ascii=False));return
    result['process_cleanup_status']='CLEANUP_CONFIRMED'
    if native_status=='NATIVE_SEAL_COMPLETED':
        result['native_zip_sha256']=BC.digest(native_zip);result['administrative_export_status']='NOT_REQUIRED_RUNTIME_NATIVE_SEAL'
        print(json.dumps(result,ensure_ascii=False));return
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
    result['startup_status']='STARTUP_ABORTED_PRE_T0' if not any(actual.values()) else 'RUNTIME_OR_INITIALIZATION_ABORTED_UNRESOLVED'
    try:
        first=BC.trusted(root/'inputs/root_private/boot/mr_first_failure.json')
        result['first_failure']={k:first.get(k) for k in ('reason','error_type','expected_diagnostic','sample','window')}
        internal=BC.trusted(root/'inputs/root_private/boot/mr_close_state.json')
        result['internal_cleanup_status']=internal['status']
    except (OSError,ValueError,KeyError):result['internal_cleanup_status']='UNKNOWN'
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--post-exit-export',action='store_true',required=True);parser.parse_args()
    post_exit_export()
