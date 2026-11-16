"""TR/1 read-only terminal evidence. No import-time role, write or grant."""
from contextlib import contextmanager
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import stat
import struct
import sys
import time
import zipfile
import batch_identity as N

class EvidenceError(RuntimeError):pass

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def digest(x):return hashlib.sha256(canonical(x)).hexdigest()

def terminal_policy(f):
    """Pure policy surface for TR-SIMULATION/1; IO facts are checked separately."""
    out={'read_status':'REJECTED','work_allowed':False,'budget_init_allowed':False,'phase_write_allowed':False,
         'launcher_allowed':False,'native_ready':False,'internal_status':f['internal_status'],'native_status':'NATIVE_SEAL_UNRESOLVED'}
    if f['purpose']=='ACTIVE':
        out['work_allowed']=not(f['closed'] or f['stop']) and all(f[k] for k in ('identity','window','budget','version','same_boot','window_live'))
        return out
    if not(f['closed'] or f['stop']) or not f['identity']:return out
    if not all(f[k] for k in ('window','budget','version','required_records')):
        out['read_status']='UNKNOWN';return out
    out['read_status']='VALID'
    out['native_status']='NATIVE_SEAL_COMPLETED' if f['native_verified'] else 'NATIVE_SEAL_FAILED' if f['seal_error'] else 'NATIVE_SEAL_UNRESOLVED'
    out['native_ready']=(f['purpose']=='NATIVE_SEAL' and f['closed'] and f['same_boot'] and f['window_live'] and f['exit_proof'] and
        not f['seal_error'] and not f['partial_archive'])
    return out

def check_active_runtime(G):
    """Preserve the original active RootIPC/identity/resource/terminal guards."""
    return G.root_checkpoint()

def _deadline(G,until):
    if G.now()>=until:raise EvidenceError('TR_READ_BOUND_EXPIRED')

def _open(directory,name,owners,maximum):
    if Path(name).name!=name or name in ('.','..'):raise EvidenceError('TR_FIXED_NAME')
    fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=directory)
    try:
        s=os.fstat(fd)
        if (not stat.S_ISREG(s.st_mode) or s.st_nlink!=1 or s.st_size>maximum or
            (s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode)) not in owners or
            any(n.startswith('system.posix_acl_') for n in os.listxattr(fd))):raise EvidenceError('TR_FILE_METADATA:'+name)
        return fd
    except BaseException:os.close(fd);raise

def _json(directory,name,owners,hashes,label):
    fd=_open(directory,name,owners,4194304)
    try:
        s=os.fstat(fd);raw=os.read(fd,s.st_size+1)
        if len(raw)!=s.st_size:raise EvidenceError('TR_SHORT_READ:'+label)
        hashes[label]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
        return json.loads(raw)
    finally:os.close(fd)

@contextmanager
def _shared(G,fd,until):
    acquired=False;limit=min(until,G.now()+2)
    try:
        for _ in range(512):
            _deadline(G,limit)
            try:fcntl.flock(fd,fcntl.LOCK_SH|fcntl.LOCK_NB);acquired=True;break
            except BlockingIOError:time.sleep(min(.005,max(0,limit-G.now())))
        if not acquired:raise EvidenceError('TR_SHARED_LOCK_BOUND')
        yield
        _deadline(G,until)
    finally:
        if acquired:fcntl.flock(fd,fcntl.LOCK_UN)

def _context(G):
    if sys.platform!='linux' or os.geteuid()!=0:raise EvidenceError('TR_ROOT_READER')
    source=Path(__file__).resolve().parent;identity=N.load(source.parent)
    if (G.NAMESPACE!=identity or str(G.ROOT)!=identity['runtime_root'] or str(G.SOURCE)!=str(source) or
        str(source)!=identity['source_root']+'/src'):raise EvidenceError('TR_NAMESPACE')
    m=G.trusted(source.parent/'inputs/static_manifest.json');l=G.trusted(source.parent/'inputs/execution_lock.json')
    mh=G.digest(source.parent/'inputs/static_manifest.json');lh=G.digest(source.parent/'inputs/execution_lock.json')
    if mh!=l['static_manifest_sha256']:raise EvidenceError('TR_MANIFEST_BINDING')
    for name,expected in m['source_hashes'].items():
        if Path(name).name!=name or G.digest(source/name)!=expected:raise EvidenceError('TR_SOURCE_BINDING')
    a=G.trusted(G.ROOT/'inputs/execution_authorization.json')
    if (a['batch_id']!=identity['batch_id'] or a['static_revision']!=identity['revision'] or
        a['static_manifest_sha256']!=mh or a['execution_lock_sha256']!=lh or
        a['batch_identity_sha256']!=G.digest(source.parent/'inputs/batch_identity.json') or
        a['authorization_text_sha256']!=G.digest(G.ROOT/'inputs'/identity['authorization_text_filename'])):raise EvidenceError('TR_AUTHORIZATION_BINDING')
    cfg=G.trusted(source.parent/'inputs/terminal_contract.json')
    if (G.digest(source.parent/'inputs/terminal_contract.json')!=m['terminal_contract_sha256'] or
        a.get('terminal_contract_sha256')!=m['terminal_contract_sha256'] or cfg['read_seconds']!=5 or
        cfg['journal_max_bytes']!=33554432):raise EvidenceError('TR_CONTRACT_BINDING')
    return identity,mh,lh,G.digest(G.ROOT/'inputs/execution_authorization.json')

def _journal(G,fd,R,cap,boot_id,until,hashes):
    total=0;position=0;pending=None;transactions=0;last_commit=None;sha=hashlib.sha256()
    with os.fdopen(os.dup(fd),'rb') as stream:
        for _ in range(2*cap+1):
            _deadline(G,until);line=stream.readline(32769)
            if not line:break
            total+=len(line)
            if len(line)>32768 or not line.endswith(b'\n') or total>33554432:raise EvidenceError('TR_JOURNAL_BOUND')
            sha.update(line);q=json.loads(line)
            if any(type(q[k]) is not int for k in ('before','after','amount','cap')):raise EvidenceError('TR_JOURNAL_INTEGER_FIELDS')
            if q['protocol']!='EXACT-RANGE/1' or q['boot_id']!=boot_id or q['cap']!=cap:raise EvidenceError('TR_JOURNAL_IDENTITY')
            if q['status']=='PREPARED' and pending is None:
                if type(q['amount']) is not int or q['amount']<=0 or q['before']!=position or q['after']!=position+q['amount'] or q['after']>cap:raise EvidenceError('TR_JOURNAL_RANGE')
                pending=q
            elif q['status']=='COMMITTED' and pending is not None:
                if any(q[k]!=pending[k] for k in ('before','after','amount','cap','request','protocol','boot_id')):raise EvidenceError('TR_JOURNAL_PAIR')
                position=q['after'];last_commit=q;pending=None;transactions+=1
            else:raise EvidenceError('TR_JOURNAL_ORDER')
        else:raise EvidenceError('TR_JOURNAL_RECORD_BOUND')
    if pending is not None or position!=R:raise EvidenceError('TR_JOURNAL_COUNTER_MISMATCH')
    hashes['out/visits.bin.journal.jsonl']={'sha256':sha.hexdigest(),'bytes':total}
    return transactions,last_commit

def _exit_evidence(G,ds,bootfd,s,activation,hashes,original_boot,purpose):
    owners={(0,0,0o600)};scheduler=_json(bootfd,'mr_scheduler.json',owners,hashes,'mr_scheduler')
    if scheduler['binding']!={'batch_id':G.ROOT.name,'boot_id':original_boot,'source_manifest':activation['ticket']['binding']['static_manifest_sha256']}:
        raise EvidenceError('TR_EXIT_BINDING')
    child=scheduler['child'];owner=scheduler['owner']
    if child!=s['launcher_identity'] or owner!=s['coordinator_identity'] or owner!=activation['ticket']['owner']:raise EvidenceError('TR_EXIT_ROLE_IDENTITY')
    if type(child['pid']) is not int or child['pid']<=0:raise EvidenceError('TR_CHILD_PID')
    try:w=_json(ds['private'],'waitpid_%s.json'%child['pid'],owners,hashes,'waitpid')
    except FileNotFoundError:return {'status':'UNKNOWN','waitpid':None,'seal_exit_ready':False}
    if w['child']!=child or w['coordinator']!=owner or w['sample']['boot_id']!=original_boot or os.waitstatus_to_exitcode(w['raw_wait_status'])!=w['exit_code']:
        raise EvidenceError('TR_WAITPID_IDENTITY_OR_STATUS')
    if purpose=='HISTORICAL_AUDIT' or G.boot_id()!=original_boot:
        return {'status':'HISTORICAL_WITNESS_ONLY','waitpid':w,'seal_exit_ready':False}
    import c09_handoff as H
    arm=_json(ds['inputs'],'STOP_ARMED.json',{(0,989,0o640)},hashes,'STOP_ARMED')
    if arm['boot_id']!=original_boot or arm['stop_at']!=s['stop_at']:raise EvidenceError('TR_STOPPER_BINDING')
    me=G.identity();known=[child,owner,arm['identity']]
    others=all(ident==me or not H.alive(G,ident) for ident in known)
    ready=me in (owner,arm['identity']) and others and G._empty()
    return {'status':'CURRENT_EXIT_EVIDENCE' if ready else 'EXIT_PENDING_OR_UNKNOWN','waitpid':w,'seal_exit_ready':ready,'reader':me}

def _native_artifact(G,ds,hashes,until,child_pid,original_boot):
    present=lambda name:bool(_exists(ds['out'],name))
    result={'zip_present':present('EVIDENCE.zip'),'manifest_present':present('EVIDENCE_MANIFEST.json'),
        'verified':False,'seal_error':_exists(ds['inputs'],'SEAL_ERROR.json'),'errors':[]}
    if result['seal_error']:
        error=_json(ds['inputs'],'SEAL_ERROR.json',{(0,989,0o640)},hashes,'SEAL_ERROR')
        if not isinstance(error['error'],str) or not error['error'] or error['sample']['boot_id']!=original_boot:raise EvidenceError('TR_SEAL_ERROR_RECORD')
        result['error_record']=error
    if not(result['zip_present'] and result['manifest_present']):return result
    try:
        manifest=_json(ds['out'],'EVIDENCE_MANIFEST.json',{(0,0,0o600)},hashes,'native_manifest')
        declared=manifest['files'];fd=_open(ds['out'],'EVIDENCE.zip',{(0,0,0o600),(0,0,0o644)},33554432)
        try:
            with os.fdopen(os.dup(fd),'rb') as raw,zipfile.ZipFile(raw) as z:
                names=z.namelist()
                if len(names)>257 or len(names)!=len(set(names)) or set(names)!=set(declared)|{'out/EVIDENCE_MANIFEST.json'}:raise EvidenceError('TR_NATIVE_MEMBER_SET')
                if z.getinfo('out/EVIDENCE_MANIFEST.json').file_size>4194304:raise EvidenceError('TR_NATIVE_MANIFEST_BOUND')
                with z.open('out/EVIDENCE_MANIFEST.json') as item:mf=item.read(4194305)
                if len(mf)>4194304:raise EvidenceError('TR_NATIVE_MANIFEST_BOUND')
                if hashlib.sha256(mf).hexdigest()!=hashes['native_manifest']['sha256']:raise EvidenceError('TR_NATIVE_MANIFEST_BYTES')
                total=len(mf)
                for name,row in declared.items():
                    if Path(name).is_absolute() or '..' in Path(name).parts:raise EvidenceError('TR_NATIVE_MEMBER_PATH')
                    sha=hashlib.sha256();size=0
                    with z.open(name) as member:
                        while True:
                            _deadline(G,until);block=member.read(65536)
                            if not block:break
                            size+=len(block);total+=len(block)
                            if total>33554432:raise EvidenceError('TR_NATIVE_UNCOMPRESSED_BOUND')
                            sha.update(block)
                    if size!=row['bytes'] or sha.hexdigest()!=row['sha256']:raise EvidenceError('TR_NATIVE_STREAM_DIGEST')
                paths={'activation':'inputs/root_private/boot/activation.json','CLOSED':'inputs/CLOSED.json','STOP_REQUEST':'out/STOP_REQUEST.json',
                    'batch_state':'inputs/batch_state.json','runtime_checkpoint':'inputs/PT_RUNTIME_CHECKPOINT.json','phase':'inputs/root_private/boot/pt_phase.json',
                    'runtime_intent':'inputs/root_private/boot/pt_runtime_intent.json','budget_intent':'out/visits.bin.intent.json',
                    'waitpid':'inputs/root_private/waitpid_%s.json'%child_pid,'mr_scheduler':'inputs/root_private/boot/mr_scheduler.json',
                    'internal_close':'inputs/root_private/boot/mr_close_state.json','STOP_ARMED':'inputs/STOP_ARMED.json','SEAL_ERROR':'inputs/SEAL_ERROR.json'}
                for label,row in hashes.items():
                    if label=='native_manifest':continue
                    target=paths.get(label,label)
                    if target not in declared or declared[target]['sha256']!=row['sha256']:raise EvidenceError('TR_NATIVE_CURRENT_EVIDENCE')
                result['verified']=True
        finally:os.close(fd)
    except (OSError,ValueError,KeyError,EvidenceError,zipfile.BadZipFile) as exc:result['errors']=[type(exc).__name__+':'+str(exc)[:160]]
    return result

def _exists(directory,name):
    try:os.stat(name,dir_fd=directory,follow_symlinks=False);return True
    except FileNotFoundError:return False

def read_terminal_evidence(G,purpose='REVIEW'):
    """Read existing fixed-batch originals. No state, ledger, service or grant writes."""
    if purpose not in ('REVIEW','NATIVE_SEAL','HISTORICAL_AUDIT'):raise EvidenceError('TR_READ_PURPOSE')
    until=G.now()+5;identity,mh,lh,ah=_context(G);hashes={}
    RI=G.root_ipc()
    with RI.directories(G) as ds:
        bootfd=RI._dir(ds['private'],'boot',(0,0,0o700))
        try:
            rootowner={(0,0,0o600)};public={(0,989,0o640)};dataowner={(999,989,0o600)}
            activation=_json(bootfd,'activation.json',rootowner,hashes,'activation');ticket=activation['ticket'];original_boot=ticket['boot_id'];bound=ticket['binding']
            if (not activation['initial_entered'] or bound['batch_id']!=identity['batch_id'] or bound['static_manifest_sha256']!=mh or
                bound['execution_lock_sha256']!=lh or bound['authorization_receipt_sha256']!=ah):raise EvidenceError('TR_ACTIVATION_BINDING')
            closed=None;stop=None
            try:closed=_json(ds['inputs'],'CLOSED.json',public,hashes,'CLOSED')
            except FileNotFoundError:pass
            try:stop=_json(ds['out'],'STOP_REQUEST.json',dataowner,hashes,'STOP_REQUEST')
            except FileNotFoundError:pass
            if closed is None and stop is None:raise EvidenceError('TR_NOT_TERMINAL')
            for marker in [m for m in (closed,stop) if m is not None]:
                if marker['boot_id']!=original_boot:raise EvidenceError('TR_TERMINAL_BOOT')
            counter=_open(ds['out'],'visits.bin',dataowner,24)
            try:
                # Match the original writer order: counter lock, then phase lock.
                with _shared(G,counter,until):
                    phasefd=_open(bootfd,'pt_phase.lock',rootowner,0)
                    try:
                        with _shared(G,phasefd,until):
                            s=_json(ds['inputs'],'batch_state.json',public,hashes,'batch_state')
                            cp=_json(ds['inputs'],'PT_RUNTIME_CHECKPOINT.json',public,hashes,'runtime_checkpoint')
                            phase=_json(bootfd,'pt_phase.json',rootowner,hashes,'phase')
                            initial=_json(bootfd,'pt_runtime_intent.json',rootowner,hashes,'runtime_intent')
                            binding={'batch_id':identity['batch_id'],'root':str(G.ROOT),'boot_id':original_boot,'manifest_sha256':mh,
                                'execution_lock_sha256':lh,'authorization_sha256':ah,'startup_contract_sha256':G.digest(G.SOURCE.parent/'inputs/startup_contract.json')}
                            window={k:s[k] for k in ('T0','deadline','stop_at')}
                            if (s['boot_id']!=original_boot or not all(type(v) in (int,float) and math.isfinite(v) and v>=0 for v in window.values()) or
                                abs(s['deadline']-s['T0']-1800)>1e-6 or abs(s['stop_at']-s['T0']-1740)>1e-6):raise EvidenceError('TR_WINDOW_EVIDENCE')
                            indexes={'RUNTIME_READY':4,'RUNTIME_ARMED':5,'RUNNING':6}
                            if (cp['schema']!='PT-RUNTIME-CHECKPOINT/1' or cp['binding']!=binding or phase['binding']!=binding or initial['binding']!=binding or
                                cp['window']!=window or cp['phase'] not in indexes or cp['sequence']!=indexes[cp['phase']] or
                                phase['phase']!=cp['phase'] or phase['sequence']!=cp['sequence'] or cp.get('committed') is not True or
                                cp['phase_record_sha256']!=digest(phase) or cp['initialization_id']!=digest(initial)):raise EvidenceError('TR_PHASE_EVIDENCE')
                            raw=os.pread(counter,25,0);meta=os.fstat(counter)
                            if len(raw)!=24 or raw[:8]!=b'BRNGv001':raise EvidenceError('TR_COUNTER_FORMAT')
                            R,cap=struct.unpack('<QQ',raw[8:]);counter_id={'device':meta.st_dev,'inode':meta.st_ino,'cap':cap,'magic':'BRNGv001'}
                            if cap!=G.VISIT_CAP or R>cap or cp['counter']!=counter_id:raise EvidenceError('TR_COUNTER_IDENTITY')
                            hashes['out/visits.bin']={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':24}
                            intent=_json(ds['out'],'visits.bin.intent.json',dataowner,hashes,'budget_intent')
                            if intent['protocol']!='EXACT-RANGE/1' or intent['status']!='COMMITTED' or intent['after']!=R or intent['cap']!=cap:raise EvidenceError('TR_BUDGET_INTENT')
                            with os.scandir(ds['out']) as entries:
                                for i,entry in enumerate(entries):
                                    if i>=1024:raise EvidenceError('TR_OUT_NAME_BOUND')
                                    if entry.name.startswith('visits.bin.intent.json.tmp.'):raise EvidenceError('TR_AMBIGUOUS_BUDGET_TEMP')
                            journal=_open(ds['out'],'visits.bin.journal.jsonl',dataowner|rootowner,33554432)
                            try:transactions,last=_journal(G,journal,R,cap,original_boot,until,hashes)
                            finally:os.close(journal)
                            if last is not None and any(last[k]!=intent[k] for k in last):raise EvidenceError('TR_FINAL_INTENT_JOURNAL')
                            try:internal=_json(bootfd,'mr_close_state.json',rootowner,hashes,'internal_close').get('status','UNKNOWN')
                            except FileNotFoundError:internal='UNKNOWN'
                            exits=_exit_evidence(G,ds,bootfd,s,activation,hashes,original_boot,purpose)
                            artifact=_native_artifact(G,ds,hashes,until,s['launcher_identity']['pid'],original_boot)
                            same=G.boot_id()==original_boot
                            facts={'purpose':purpose,'closed':closed is not None,'stop':stop is not None,'identity':True,'window':True,'budget':True,
                                'version':True,'required_records':True,'same_boot':same,'window_live':same and G.now()<s['deadline'],
                                'exit_proof':exits['seal_exit_ready'],'internal_status':internal,'native_verified':artifact['verified'],
                                'seal_error':artifact['seal_error'],'partial_archive':(artifact['zip_present'] or artifact['manifest_present']) and not artifact['verified']}
                            policy=terminal_policy(facts);_deadline(G,until)
                            return {'schema':'TERMINAL-EVIDENCE/1','binding':binding,'original_boot_id':original_boot,'observation_boot_id':G.boot_id(),
                                'purpose':purpose,'window':window,'R':R,'cap':cap,'journal_status':'CONSISTENT','transactions':transactions,
                                'closed':closed,'stop_request':stop,'phase':cp['phase'],'sequence':cp['sequence'],'exit_evidence':exits,
                                'internal_status':internal,'evidence_digests':hashes,'decision':policy,'sample':G.stamp(),
                                'native_seal_status':policy['native_status'],'native_artifact':artifact,'runtime_authority':'NONE'}
                    finally:os.close(phasefd)
            finally:os.close(counter)
        finally:os.close(bootfd)
