"""MR/1: native manager review and current-batch failure closure. No role on import."""
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import select
import signal
import stat
import subprocess
import time
import boot_continuity as BC

PROFILE='MANAGER-RECOVERY/1'
FIELDS=('Id','LoadState','ActiveState','SubState','MainPID','ExecMainPID','ExecMainCode','ExecMainStatus',
        'Result','InvocationID','ExecMainStartTimestampMonotonic','ExecMainExitTimestampMonotonic','ControlGroup')

def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def sha(v):return hashlib.sha256(canonical(v)).hexdigest()
def contract(G):
    a,m=G.authorization();p=G.SOURCE.parent/'inputs/manager_contract.json'
    if G.digest(p)!=m['manager_contract_sha256'] or a.get('manager_contract_sha256')!=m['manager_contract_sha256']:
        raise G.AdmissionBlocked('MR_CONTRACT_BINDING')
    c=G.trusted(p)
    if (c['schema']!='MANAGER-RECOVERY-CONTRACT/1' or c['profile']!=PROFILE or c['version']!='PTA-PhaseFinalizer-static-1/r3' or
        c['batch_id']!=G.ROOT.name or len(c['jobs'])!=64 or len({j['case_id'] for j in c['jobs']})!=64 or
        c['native_review_credit']!=256 or c['driver_prepay']!=12 or c['phase_hard_visits']!=1536 or
        any(len(j['frames'])>2 for j in c['jobs'])):raise G.AdmissionBlocked('MR_CONTRACT_IDENTITY')
    return c

@contextmanager
def locked(G,name):
    with BC.Store() as store:
        fd=os.open(name,os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=store.fd)
        s=os.fstat(fd)
        if (s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)!=(0,0,0o600,1):
            os.close(fd);raise G.AdmissionBlocked('MR_LOCK_METADATA')
        until=G.now()+2;acquired=False
        try:
            while not acquired:
                try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);acquired=True
                except BlockingIOError:
                    if G.now()>=until:raise G.AdmissionBlocked('MR_LOCK_TIMEOUT')
                    time.sleep(.005)
            yield store
        finally:
            if acquired:fcntl.flock(fd,fcntl.LOCK_UN)
            os.close(fd)

def event(G,kind,**data):
    row={'schema':PROFILE,'event':kind,'batch_id':G.ROOT.name,'boot_id':G.boot_id(),
         'actor':G.identity(),'sample':G.stamp(),**data}
    raw=canonical(row)+b'\n'
    if len(raw)>32768:raise G.AdmissionBlocked('MR_EVENT_BYTES')
    with locked(G,'mr_events.lock') as store:
        fd=os.open('mr_events.jsonl',os.O_WRONLY|os.O_CREAT|os.O_APPEND|os.O_NOFOLLOW,0o600,dir_fd=store.fd)
        try:os.fchown(fd,0,0);os.fchmod(fd,0o600);G._full(fd,raw);os.fsync(fd);os.fsync(store.fd)
        finally:os.close(fd)
    return row

def credit(G,label):
    """Only finite MR checks consume the already charged Root review block."""
    G.root_checkpoint()
    with locked(G,'mr_credit.lock') as store:
        q=store.read('mr_credit.json')
        if q['binding']!=G.safety_binding() or q['used']>=q['N']:raise G.AdmissionBlocked('MR_CREDIT_EXHAUSTED_OR_BINDING')
        q['used']+=1;q['last_label']=label;store.put('mr_credit.json',q)

def classify(f):
    """Pure policy shared with synthetic subjects; native facts are collected below."""
    if f['closed']:return 'CLOSED'
    if f['stop']:return 'STOP_REQUESTED'
    if not all(f[k] for k in ('binding','identity','fresh','expected_kind','budget','window')):return 'REVIEWED_UNEXPECTED'
    if not f['exit_observed']:return 'MANAGER_ACTIVE' if f['active'] else 'REVIEW_PENDING'
    if not all(f[k] for k in ('review_complete','result_proof','ack','receiver','witness')):return 'REVIEW_PENDING'
    return 'REVIEWED_EXPECTED' if f['supervision'] else 'REVIEWED_UNEXPECTED'

def closure_status(closed,payload_empty,other_roles_exited,errors):
    return 'CLOSED_CLEANUP_CONFIRMED' if closed and payload_empty and other_roles_exited and not errors else 'UNKNOWN'

def query(G,argv,until,record=True):
    if record:
        import startup_lifecycle as P
        P.manager_checkpoint(G);until=P.query_deadline(G,until)
    before=G.stamp();remaining=until-G.now()
    if remaining<=0:raise G.LimitReached('MR_REVIEW_DEADLINE')
    p=subprocess.run(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=min(1,remaining))
    if len(p.stdout)>8192 or len(p.stderr)>2048:raise G.AdmissionBlocked('MR_MANAGER_OUTPUT_BOUND')
    row={'argv':argv,'before':before,'after':G.stamp(),'exit_code':p.returncode,
         'stdout':p.stdout.decode('utf-8'),'stderr':p.stderr.decode('utf-8')}
    if record:event(G,'MANAGER_QUERY',raw=row)
    if p.returncode:raise G.AdmissionBlocked('MR_MANAGER_QUERY_FAILED')
    return row

def show(G,unit,until,record=True):
    q=query(G,['/usr/bin/systemctl','show','--all','--no-pager',unit,*['--property='+k for k in FIELDS]],until,record)
    q['values']=dict(s.split('=',1) for s in q['stdout'].splitlines() if '=' in s)
    if any(k not in q['values'] for k in FIELDS):raise G.AdmissionBlocked('MR_MANAGER_FIELDS_MISSING')
    return q

def failed_set(G,until,record=True):
    q=query(G,['/usr/bin/systemctl','list-units','--state=failed','--all','--no-pager','--no-legend'],until,record)
    units=[]
    for line in q['stdout'].splitlines():
        parts=line.replace('●','').split()
        if parts:units.append(parts[0])
    if len(units)>16 or len(set(units))!=len(units):raise G.AdmissionBlocked('MR_FAILED_SET_BOUND')
    return sorted(units)

def stable(G,unit,until,record=True):
    a=show(G,unit,until,record);b=show(G,unit,until,record)
    if a['values']!=b['values']:raise G.AdmissionBlocked('MR_REVIEW_PENDING_VERSION')
    return a['values']

def capture(G,case,t):
    if case not in ('C06','C07','C09'):return
    credit(G,'capture:'+case);until=min(G.now()+2,G.state()['T0']+300,t['case_deadline'])
    v=stable(G,t['unit'],until)
    if (v['Id']!=t['unit'] or v['LoadState']!='loaded' or int(v['MainPID'])!=t['main_identity']['pid'] or
        not v['InvocationID'] or G.identity(int(v['MainPID']))!=t['main_identity']):
        raise G.AdmissionBlocked('MR_START_IDENTITY')
    d={'schema':'MR-START/1','case':case,'binding':G.safety_binding(),'unit':t['unit'],
       'main_identity':t['main_identity'],'invocation_id':v['InvocationID'],'native_start':v,'argv_sha256':sha(t['argv']),'sample':G.stamp()}
    with BC.Store() as store:store.put('mr_start_'+case+'.json',d,exclusive=True)
    t['manager_start_sha256']=G.digest(G.ROOT/('inputs/root_private/boot/mr_start_'+case+'.json'))

def handoff_facts(G,coordinator,allow_resumed=False):
    """Additional review; durable ACK protocol and its admission function stay intact."""
    import c09_handoff as H
    s=G.state();h=G.trusted(H.paths(G)['state']);c=G.trusted(H.paths(G)['commit']);w=G.trusted(H.paths(G)['witness'])
    r=G.trusted(G.ROOT/'inputs/result_C09.json');owner=G.trusted(G.ROOT/'inputs/BOOT_START.json')['owner']
    if (h['stage'] not in (('HANDOFF_VERIFIED','RESUMED') if allow_resumed else ('HANDOFF_VERIFIED',)) or
        h['classification_count']!=1 or h['window']!=H.window(G,s) or owner!=coordinator or h['coordinator']!=owner or
        not H.alive(G,owner) or G.now()>=min(s['T0']+300,s['stop_at'],s['deadline'])):
        raise G.AdmissionBlocked('MR_HANDOFF_OWNER_OR_PHASE')
    H.checked_receiver(G,h)
    expected_id=H.sha({'nonce':h['nonce'],'window':h['window'],'sender':h['sender'],'coordinator':h['coordinator']})
    expected_revision=r['actual']['handoff_revision']+(1 if h['stage']=='RESUMED' else 0)
    if h['id']!=expected_id or h['case']!='C09' or h['expected_exit']!=23 or h['revision']!=expected_revision:
        raise G.AdmissionBlocked('MR_HANDOFF_EVENT_ID')
    if (G.digest(H.paths(G)['commit'])!=h['commit_sha256'] or G.digest(H.paths(G)['witness'])!=h['witness_sha256'] or
        any(c[k]!=h[k] for k in ('window','sender','coordinator','receiver','counter','expected_exit')) or
        c['handoff_id']!=h['id'] or c['commit_version']!=1 or w['handoff_id']!=h['id'] or
        w['sender']!=h['sender'] or w['coordinator']!=owner or w['window']!=h['window'] or
        w['source']!='direct-parent os.waitpid' or w['exit_code']!=23 or os.waitstatus_to_exitcode(w['raw_wait_status'])!=23 or
        r['status']!='PASS' or r['actual']['handoff_id']!=h['id'] or r['actual']['native_exit']!=23 or
        r['actual']['commit_sha256']!=h['commit_sha256'] or r['actual']['witness_sha256']!=h['witness_sha256']):
        raise G.AdmissionBlocked('MR_HANDOFF_EVIDENCE')
    if not allow_resumed and H.counter(G)!=h['counter']:raise G.AdmissionBlocked('MR_HANDOFF_COUNTER')
    return h

def review_case(G,case):
    credit(G,'review:'+case);s=G.state();cfg=contract(G);until=min(G.now()+2,s['T0']+300,s['stop_at'],s['deadline'])
    with BC.Store() as store:start=store.read('mr_start_'+case+'.json')
    t=G.ticket(case);result=G.trusted(G.ROOT/('inputs/result_'+case+'.json'))
    event(G,'EXIT_OBSERVED',case=case,unit=t['unit'])
    event(G,'REVIEW_PENDING',case=case,until=until)
    if (start['binding']!=G.safety_binding() or start['main_identity']!=t['main_identity'] or
        t.get('manager_start_sha256')!=G.digest(G.ROOT/('inputs/root_private/boot/mr_start_'+case+'.json')) or
        start['argv_sha256']!=sha(t['argv']) or result['case']!=case or result['status']!='PASS' or result['sample']['boot_id']!=G.boot_id()):
        raise G.AdmissionBlocked('MR_CASE_PROVENANCE')
    if case in ('C06','C07') and result['actual']['ticket']!=t:raise G.AdmissionBlocked('MR_RESULT_TICKET')
    v=stable(G,t['unit'],until);spec=cfg['expected_cases'][case]
    good=(v['Id']==t['unit'] and v['LoadState']=='loaded' and v['ActiveState']=='failed' and
        v['MainPID']=='0' and v['InvocationID']==start['invocation_id'] and int(v['ExecMainPID'])==t['main_identity']['pid'] and
        v['Result']==spec['Result'] and v['ExecMainCode']==str(spec['ExecMainCode']) and v['ExecMainStatus']==str(spec['ExecMainStatus']) and
        int(v['ExecMainExitTimestampMonotonic'])>0)
    if case=='C06':good=good and result['actual']['watchdog']['expired'] is True and G.read(G.OUT/'C06.watchdog_stop.json')==result['actual']['watchdog']
    if case=='C07':good=good and G.read(G.OUT/'C07.ready.json')['identity']==t['main_identity']
    if case=='C09':handoff_facts(G,G.trusted(G.ROOT/'inputs/BOOT_START.json')['owner'])
    facts=dict(closed=G.stopped(),stop=False,binding=True,identity=good,fresh=True,expected_kind=True,budget=True,window=True,
        exit_observed=True,active=False,review_complete=True,result_proof=True,ack=True,receiver=True,witness=True,supervision=True)
    verdict=classify(facts)
    event(G,verdict,case=case,unit=t['unit'],facts=facts)
    if verdict!='REVIEWED_EXPECTED':raise G.AdmissionBlocked('MR_UNEXPECTED_UNIT_EXIT:'+case)
    proof={'schema':'MR-EXIT-REVIEW/1','case':case,'binding':G.safety_binding(),'native_exit':v,
        'ticket_sha256':G.digest(G.ROOT/('inputs/ticket_'+case+'.json')),'result_sha256':G.digest(G.ROOT/('inputs/result_'+case+'.json')),
        'start_sha256':t['manager_start_sha256'],'status':verdict}
    proof['event_id']=sha(proof);proof['sample']=G.stamp()
    with locked(G,'mr_review.lock') as store:
        try:old=store.read('mr_review_'+case+'.json')
        except FileNotFoundError:old=None
        if old is not None:
            if old['event_id']!=proof['event_id']:raise G.AdmissionBlocked('MR_EVENT_CONFLICT')
            return old
        store.put('mr_review_'+case+'.json',proof,exclusive=True)
    return proof

def historical(G,unit,cfg,until,record=True):
    """Read-only, exact retired-unit provenance; never grants current responsibility."""
    spec=cfg['historical_closed_units'].get(unit)
    if spec is None:raise G.AdmissionBlocked('MR_UNREVIEWED_MANAGER_FAILURE:'+unit)
    if G.boot_id()!=spec['boot_id']:raise G.AdmissionBlocked('MR_HISTORICAL_BOOT')
    base=Path(spec['root'])
    for rel,expected in spec['files'].items():
        p=base/rel;data=G.trusted(p)
        if G.digest(p)!=expected:raise G.AdmissionBlocked('MR_HISTORICAL_DIGEST')
    if G.trusted(base/'inputs/CLOSED.json')['boot_id']!=spec['boot_id']:raise G.AdmissionBlocked('MR_HISTORICAL_CLOSURE')
    v=stable(G,unit,until,record)
    if (v['Id']!=unit or v['InvocationID']!=spec['InvocationID'] or v['MainPID']!='0' or
        v['ActiveState']!='failed' or v['Result']!=spec['Result'] or v['ExecMainStatus']!=str(spec['ExecMainStatus']) or
        v['ExecMainCode']!=str(spec['ExecMainCode']) or v['ExecMainPID']!=str(spec['ExecMainPID'])):
        raise G.AdmissionBlocked('MR_HISTORICAL_INSTANCE')
    return {'unit':unit,'scope':'REVIEWED_EXPECTED_HISTORICAL_CLOSED_ONLY','native':v}

def health(G,resume=False,record=True):
    cfg=contract(G);s=G.trusted(G.ROOT/'inputs/batch_state.json') if (G.ROOT/'inputs/batch_state.json').exists() else None
    until=min(G.now()+2,s['T0']+300,s['stop_at'],s['deadline']) if s else G.now()+2
    if resume:
        credit(G,'resume-health')
        handoff_facts(G,G.trusted(G.ROOT/'inputs/BOOT_START.json')['owner'])
        for case in ('C06','C07','C09'):review_case(G,case)
    before=failed_set(G,until,record);current={G.batch_unit(c):c for c in ('C06','C07','C09')};rows=[]
    for unit in before:
        if unit=='mnt-e.mount':continue
        if unit in current and resume:
            with BC.Store() as store:q=store.read('mr_review_'+current[unit]+'.json')
            if stable(G,unit,until,record)!=q['native_exit']:raise G.AdmissionBlocked('MR_STALE_MANAGER_EVENT')
            rows.append({'unit':unit,'event_id':q['event_id'],'status':'REVIEWED_EXPECTED'})
        else:rows.append(historical(G,unit,cfg,until,record))
    after=failed_set(G,until,record)
    if before!=after:raise G.AdmissionBlocked('MR_REVIEW_PENDING_FAILED_SET')
    if record:event(G,'MANAGER_HEALTH_REVIEWED',resume=resume,units=before,reviews=rows)
    return {'units':before,'reviews':rows,'sample':G.stamp()}

def resume(G,coordinator):
    import c09_handoff as H
    if G.stopped():raise G.AdmissionBlocked('MR_CLOSED_ABSORBING')
    s=G.state()
    if s['resume_count']==1:
        h=handoff_facts(G,coordinator,True)
        if h['stage']!='RESUMED' or s['coordinator_identity']!=coordinator:raise G.AdmissionBlocked('MR_REPEAT_IDENTITY')
        return {'dispatch':False,'status':'ALREADY_RESUMED','state':s}
    health(G,True)
    fresh=H.resume_admission(G,coordinator)
    event(G,'MANAGER_ACTIVE',coordinator=coordinator,launcher=G.identity())
    with BC.Store() as store:
        reviews={case:store.read('mr_review_'+case+'.json')['event_id'] for case in ('C06','C07','C09')}
        store.put('MR_RECOVERY_REVIEW.json',{'binding':G.safety_binding(),'status':'RESUMED','coordinator':coordinator,
            'scheduler':G.identity(),'reviews':reviews,'sample':G.stamp()},exclusive=True,public=True)
    return {'dispatch':True,'status':'RESUMED','state':fresh}

def scheduler(G,child,owner,phase):
    with BC.Store() as store:store.put('mr_scheduler.json',{'binding':{'batch_id':G.ROOT.name,'boot_id':G.boot_id(),
        'source_manifest':G.digest(G.SOURCE.parent/'inputs/static_manifest.json')},'child':child,'owner':owner,'phase':phase,'sample':G.stamp()})

def spawn_pending(G,owner,phase):
    scheduler(G,None,owner,'SPAWNING:'+phase)

def supervision(G,s):
    """Independent stop source keeps the live Root owner through AWAIT."""
    import c09_handoff as H
    owner=s.get('coordinator_identity')
    if s['status']=='AWAIT_EXPECTED_RESUME':
        h=G.trusted(H.paths(G)['state'])
        if h['stage']!='HANDOFF_VERIFIED' or h['window']!=H.window(G,s):raise G.AdmissionBlocked('MR_PENDING_OWNER_EVIDENCE')
        owner=h['coordinator']
        expected=G.trusted(G.ROOT/'inputs/BOOT_START.json')['owner']
        if owner!=expected:raise G.AdmissionBlocked('MR_PENDING_OWNER_IDENTITY')
    if owner is None or not H.alive(G,owner):raise G.AdmissionBlocked('MR_COORDINATOR_LOST')
    limit=min(s['deadline'],s['stop_at'],s['T0']+300 if s['status'] in ('CALIBRATING','AWAIT_EXPECTED_RESUME') else s['stop_at'])
    if G.now()>=limit:raise G.LimitReached('MR_SUPERVISION_DEADLINE')
    return owner

def budget_snapshot(G):
    rows={}
    for name in ('visits.bin','visits.bin.intent.json','visits.bin.journal.jsonl'):
        p=G.OUT/name
        try:
            fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW);digest=hashlib.sha256();size=0
            try:
                while True:
                    block=os.read(fd,65536)
                    if not block:break
                    digest.update(block);size+=len(block)
            finally:os.close(fd)
            rows[name]={'sha256':digest.hexdigest(),'bytes':size}
        except (OSError,ValueError) as exc:rows[name]={'status':'UNKNOWN','error':type(exc).__name__}
    return rows

def _targets(G):
    """Only Root-protected current owner/scheduler identities are signal targets."""
    with BC.Store() as store:
        q=store.read('mr_scheduler.json')
    if q['binding']!={'batch_id':G.ROOT.name,'boot_id':G.boot_id(),'source_manifest':G.digest(G.SOURCE.parent/'inputs/static_manifest.json')}:
        raise G.AdmissionBlocked('MR_STOP_TARGET_BINDING')
    if q['child'] is None:raise G.AdmissionBlocked('MR_STOP_TARGET_UNPUBLISHED')
    return [q['child'],q['owner']]

def _stop_other_roots(G,deadline):
    import c09_handoff as H
    targets=_targets(G);me=G.identity();child,owner=targets
    if me==child:
        return {'known_other_roles_exited':False,'delegated_to_owner':True,'owner_exit_pending':True,'targets':[]}
    if me!=owner:
        if G.trusted(G.ROOT/'inputs/STOP_ARMED.json')['identity']!=me:
            raise G.AdmissionBlocked('MR_STOP_CALLER_IDENTITY')
    fds=[];facts=[]
    try:
        for ident in targets:
            if ident==G.identity() or not H.alive(G,ident):continue
            fd=os.pidfd_open(ident['pid'])
            if G.identity(ident['pid'])!=ident:os.close(fd);raise G.AdmissionBlocked('MR_STOP_PIDFD_IDENTITY')
            fds.append((fd,ident))
        until=min(deadline,G.now()+30)
        while any(not select.select([fd],[],[],0)[0] for fd,_ in fds) and G.now()<until:time.sleep(.05)
        for fd,ident in fds:
            if not select.select([fd],[],[],0)[0]:signal.pidfd_send_signal(fd,signal.SIGKILL)
        until=min(deadline,G.now()+5)
        while any(not select.select([fd],[],[],0)[0] for fd,_ in fds) and G.now()<until:time.sleep(.05)
        for fd,ident in fds:facts.append({'identity':ident,'exit_observed':bool(select.select([fd],[],[],0)[0])})
        return {'known_other_roles_exited':all(x['exit_observed'] for x in facts),'targets':facts}
    finally:
        for fd,_ in fds:os.close(fd)

def abort(G,reason,error=None,expected=False,announce_only=False):
    """STOP first, immutable first failure, existing frozen stop, bounded fallback."""
    if os.geteuid()!=0 or str(G.ROOT)!=G.NAMESPACE['runtime_root'] or G.PARENT!=G.NAMESPACE['slice']:
        return {'status':'UNKNOWN','reason':'MR_ABORT_UNBOUND_CONTEXT'}
    if (G.ROOT/'inputs/CLOSED.json').exists() and (G.OUT/'EVIDENCE.zip').exists():
        G._HALTED.set()
        try:
            with BC.Store() as store:return store.read('mr_close_state.json')
        except BaseException:return {'status':'UNKNOWN','closed':True,'sealed':True,'reason':'MR_TERMINAL_EVIDENCE_UNREADABLE'}
    G._HALTED.set();notes=[]
    try:
        if not(G.OUT/'STOP_REQUEST.json').exists():G.request_stop('MR_CRITICAL:'+reason)
    except BaseException as exc:notes.append('STOP_PUBLISH:'+type(exc).__name__)
    snapshot=budget_snapshot(G)
    p=G.ROOT/'inputs/batch_state.json'
    try:s=G.trusted(p) if p.exists() else None
    except BaseException as exc:s=None;notes.append('STATE_UNKNOWN:'+type(exc).__name__)
    if s and s['boot_id']!=G.boot_id():
        notes.append('STATE_BOOT_MISMATCH');s=None
    deadline=s['deadline'] if s else G.now()
    if s is None:
        authority=None
        try:
            import startup_lifecycle as P
            authority=P.cleanup_deadline(G);deadline=authority['deadline']
        except BaseException:pass
        if authority is None:
            try:
                start=G.trusted(G.ROOT/'inputs/BOOT_START.json')
                if start['boot_id']!=G.boot_id():raise G.AdmissionBlocked('MR_STOP_BOOT')
                deadline=start['window']['deadline'];authority={'source':'BOOT_START'}
            except BaseException:pass
        if authority is None:
            try:
                arm=G.trusted(G.ROOT/'inputs/STOP_ARMED.json')
                if arm['boot_id']!=G.boot_id():raise G.AdmissionBlocked('MR_STOP_BOOT')
                deadline=arm['stop_at']+60;authority={'source':'STOP_ARMED existing runtime bound'}
            except BaseException:notes.append('DEADLINE_UNKNOWN')
    first={'schema':PROFILE,'reason':reason,'error_type':type(error).__name__ if error else None,
        'error':str(error)[:2048] if error else None,'expected_diagnostic':expected,'sample':G.stamp(),
        'batch_id':G.ROOT.name,'actor':G.identity(),'window':{k:s[k] for k in ('T0','deadline','stop_at')} if s else None,'budget':snapshot}
    try:
        with locked(G,'mr_close.lock') as store:
            try:first=store.read('mr_first_failure.json')
            except FileNotFoundError:store.put('mr_first_failure.json',first,exclusive=True)
            try:
                arm=G.trusted(G.ROOT/'inputs/STOP_ARMED.json')
                if arm['identity']==G.identity():store.put('mr_external_closing.json',{'actor':G.identity(),'batch_id':G.ROOT.name,'sample':G.stamp()})
            except FileNotFoundError:pass
            store.put('mr_close_state.json',{'phase':'ABORTING','first_failure_sha256':sha(first),'sample':G.stamp()})
    except BaseException as exc:notes.append('FAILURE_PERSIST:'+type(exc).__name__)
    if announce_only:return {'status':'STOP_REQUESTED','first_failure_sha256':sha(first),'errors':notes}
    cleanup=None
    try:
        if deadline-G.now()<20:raise G.LimitReached('MR_CLEANUP_REMAINING_WINDOW')
        cleanup=G.stop_tree('MR_CRITICAL:'+first['reason'],True)
        if cleanup.get('closure_persistence_error'):raise G.AdmissionBlocked('MR_CLOSED_WRITE_FAILED')
    except BaseException as exc:
        notes.append('PRIMARY_CLEANUP:'+type(exc).__name__)
        # Presence of CLOSED and the original STOP marker dominates all admission.
        try:
            import c09_handoff as H
            with H.lifecycle_lock(G):
                if not(G.ROOT/'inputs/CLOSED.json').exists():G._root_write(G.ROOT/'inputs/CLOSED.json',{'reason':'MR_FALLBACK:'+first['reason'],**G.stamp()})
        except BaseException as e:notes.append('CLOSED_FALLBACK:'+type(e).__name__)
        for argv in [['/usr/bin/systemctl','stop',G.PARENT],['/usr/bin/systemctl','kill','--kill-whom=all','--signal=KILL',G.PARENT]]:
            try:subprocess.run(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=max(.001,min(5,deadline-G.now())))
            except BaseException as e:notes.append('EXTERNAL_STOP:'+type(e).__name__)
    try:roles=_stop_other_roots(G,deadline)
    except BaseException as exc:roles={'known_other_roles_exited':False,'error':type(exc).__name__};notes.append('ROLE_EXIT_UNKNOWN')
    if getattr(G,'_MR_CHILD_REAP_PENDING',False):
        roles['known_other_roles_exited']=False;roles['local_child_reap_pending']=True
    closed=(G.ROOT/'inputs/CLOSED.json').exists();empty=G._empty()
    result={'schema':PROFILE,'phase':'CLEANUP','status':closure_status(closed,empty,roles['known_other_roles_exited'],notes),
        'closed':closed,'payload_empty':empty,'other_roles':roles,'first_failure_sha256':sha(first),
        'errors':notes,'budget_after':budget_snapshot(G),'sample':G.stamp(),'caller_exit_pending':True}
    try:
        with locked(G,'mr_close.lock') as store:
            fd=os.open('mr_close_attempts.jsonl',os.O_WRONLY|os.O_CREAT|os.O_APPEND|os.O_NOFOLLOW,0o600,dir_fd=store.fd)
            try:os.fchown(fd,0,0);os.fchmod(fd,0o600);G._full(fd,canonical(result)+b'\n');os.fsync(fd)
            finally:os.close(fd)
            store.put('mr_close_state.json',result)
    except BaseException as exc:result['status']='UNKNOWN';result['errors'].append('FINAL_EVIDENCE:'+type(exc).__name__)
    return result

def fail(G,reason,code=65,expected=False):
    abort(G,reason,expected=expected);return code

def permit_external_seal(G):
    import c09_handoff as H
    if not(G.ROOT/'inputs/CLOSED.json').exists() or not G._empty():return False
    arm=G.trusted(G.ROOT/'inputs/STOP_ARMED.json')
    if arm['identity']!=G.identity():return False
    try:targets=_targets(G)
    except BaseException:return False
    return all(ident==G.identity() or not H.alive(G,ident) for ident in targets)

def seal(G,external_tail=False):
    import startup_lifecycle as P
    applicability=P.seal_applicability(G)
    if applicability!='RUNTIME_NATIVE_SEAL_APPLICABLE':return P.defer_startup_seal(G,applicability)
    if G._COORDINATOR_ID is not None and G.identity()!=G._COORDINATOR_ID:return None
    with locked(G,'mr_seal.lock') as store:
        if (G.OUT/'EVIDENCE.zip').exists():return G.digest(G.OUT/'EVIDENCE.zip')
        if not(G.ROOT/'inputs/CLOSED.json').exists() or not G._empty():raise G.AdmissionBlocked('MR_SEAL_CLOSED_OR_PAYLOAD_UNKNOWN')
        if external_tail and not permit_external_seal(G):return None
        if getattr(G,'_MR_CHILD_REAP_PENDING',False):raise G.AdmissionBlocked('MR_SEAL_CHILD_REAP_UNKNOWN')
        if not external_tail:
            try:
                import c09_handoff as H
                delegate=store.read('mr_external_closing.json')
                if delegate['batch_id']==G.ROOT.name and H.alive(G,delegate['actor']):return None
            except FileNotFoundError:pass
        return G.seal(external_tail=external_tail)

def preflight(source,manifest,failed_text,deadline,epoch):
    """Read-only manager classification before a new runtime namespace exists."""
    cfg=BC.trusted(Path(source).parent/'inputs/manager_contract.json')
    if BC.digest(Path(source).parent/'inputs/manager_contract.json')!=manifest['manager_contract_sha256']:
        raise BC.Rejected('MR_PREFLIGHT_CONTRACT')
    if cfg['profile']!=PROFILE or cfg['batch_id']!=BC.NAMESPACE['batch_id']:raise BC.Rejected('MR_PREFLIGHT_IDENTITY')
    class Context:
        AdmissionBlocked=BC.Rejected
        LimitReached=BC.Rejected
        trusted=staticmethod(BC.trusted)
        digest=staticmethod(BC.digest)
        now=staticmethod(BC.now)
        boot_id=staticmethod(BC.boot)
        stamp=staticmethod(BC.stamp)
    units=sorted(line.replace('●','').split()[0] for line in failed_text.splitlines() if line.replace('●','').split())
    rows=[];until=min(deadline,BC.now()+2)
    for unit in units:
        if unit!='mnt-e.mount':rows.append(historical(Context(),unit,cfg,until,False))
    if BC.boot()!=epoch or failed_set(Context(),until,False)!=units:raise BC.Rejected('MR_PREFLIGHT_MANAGER_CHANGED')
    return {'units':units,'historical_reviews':rows,'scope':'Read-only historical closed-unit classification, no current execution qualification'}

def prepay(G):
    """Finite native review work is charged before C09 fixes the handoff counter."""
    G.root_checkpoint();cfg=contract(G)
    with BC.Store() as store:
        try:existing=store.read('mr_credit.json')
        except FileNotFoundError:existing=None
        if existing is not None:
            if existing['binding']!=G.safety_binding() or existing['N']!=cfg['native_review_credit']:raise G.AdmissionBlocked('MR_PREPAY_CONFLICT')
            return existing
    old=G._TICKET;G._TICKET=G.ticket('C00');before=G.count()
    try:
        for _ in range(cfg['native_review_credit']):G.execution_deadline('C00');G.reserve_counter(G.OUT/'visits.bin',G.VISIT_CAP)
        with BC.Store() as store:store.put('mr_credit.json',{'binding':G.safety_binding(),'N':cfg['native_review_credit'],
            'used':0,'charged_before':before,'charged_after':G.count(),'sample':G.stamp()},exclusive=True)
    finally:G._TICKET=old

def formal_gate(G):
    cfg=contract(G);q=G.trusted(G.ROOT/'inputs/MR_QUALIFICATION.json')
    if (q['binding']!=G.safety_binding() or not q['accepted'] or q['contract_sha256']!=G.digest(G.SOURCE.parent/'inputs/manager_contract.json') or
        q['checker_sha256']!=G.digest(G.SOURCE/'manager_recovery_oracle.py')):
        raise G.AdmissionBlocked('MR_QUALIFICATION_BINDING')
    expected={j['case_id']:j for j in cfg['jobs']}
    if len(q['results'])!=len(expected) or {r['case_id'] for r in q['results']}!=set(expected):raise G.AdmissionBlocked('MR_QUALIFICATION_SET')
    for row in q['results']:
        target='MUTATION_DETECTED' if expected[row['case_id']]['mutant'] else 'PASS'
        if row['status']!=target or not row['accepted']:raise G.AdmissionBlocked('MR_QUALIFICATION_RESULT')
    review=G.trusted(G.ROOT/'inputs/MR_RECOVERY_REVIEW.json')
    if review['binding']!=G.safety_binding() or review['status']!='RESUMED' or review['coordinator']!=G.trusted(G.ROOT/'inputs/BOOT_START.json')['owner']:
        raise G.AdmissionBlocked('MR_NATIVE_RECOVERY_REQUIRED')

def diagnostic_marker(G):
    a,_=G.authorization()
    if (a['scope']!='MR_RECOVERY_DIAGNOSTIC_ONLY' or a.get('ManagerRecovery_diagnostic_explicitly_approved') is not True or
        a.get('Diagnostic_auto_close_injection_explicitly_approved') is not True):raise G.AdmissionBlocked('MR_DIAGNOSTIC_SCOPE')
    proof=G.trusted(G.ROOT/'inputs/result_C10.json')
    if proof['status']!='PASS':raise G.AdmissionBlocked('MR_DIAGNOSTIC_C10_REQUIRED')
    with BC.Store() as store:store.put('mr_diag_injection.json',{'binding':G.safety_binding(),'case':'C10',
        'C10_sha256':G.digest(G.ROOT/'inputs/result_C10.json'),'expected_exit':78,'sample':G.stamp()},exclusive=True)
    return fail(G,'MR_EXPECTED_DIAGNOSTIC_FAILURE',78,True)

def guard_liveness(G,s):
    if not s or G.stopped() or not s.get('mr_stop_required'):return
    import c09_handoff as H
    arm=G.trusted(G.ROOT/'inputs/STOP_ARMED.json')
    if arm['boot_id']!=G.boot_id() or not H.alive(G,arm['identity']):raise G.AdmissionBlocked('MR_INDEPENDENT_STOP_SOURCE_LOST')

def diagnostic_report(G,exit_code):
    import manager_recovery_oracle as O
    raw=G.trusted(G.ROOT/'inputs/batch_state.json');until=min(raw['deadline'],G.now()+20)
    while G.now()<until:
        if G.unit_show(G.batch_unit('STOP')).get('ActiveState') in ('inactive','failed'):break
        time.sleep(.05)
    else:raise G.AdmissionBlocked('MR_DIAGNOSTIC_STOP_NOT_EXITED')
    result=O.native_diagnostic(G,exit_code)
    with BC.Store() as store:store.put('MR_DIAGNOSTIC_RESULT.json',result,exclusive=True,public=True)
    return result
