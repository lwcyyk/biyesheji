"""Shared exact-range object under test. No role runs on import.
Test capabilities are minted only by guard.safety_mode; production uses mode=None.
"""
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import select
import struct
import threading
_MINT = object()

def canonical(v):
    return json.dumps(v, sort_keys=True, separators=(',', ':'))
def request_hash(v):
    return hashlib.sha256(canonical(v).encode()).hexdigest()
def fact_path(ledger, task):
    return ledger.parent / (ledger.name+'.facts') / (hashlib.sha256(task.encode()).hexdigest()+'.json')

class Store:
    def __init__(self, G, ledger, cap, request, mode=None):
        self.G=G;self.path=G._inside(ledger,G.OUT);self.cap=cap
        self.request=json.loads(canonical(request));self.mode=mode
        if mode is None:
            if self.path!=G.OUT/'visits.bin' or cap!=G.VISIT_CAP:
                raise G.AdmissionBlocked('PRODUCTION_RANGE_LEDGER_REQUIRED')
            checked,t=G._task_contract(request['task_id'],request['N'])
            if checked!=request:raise G.AdmissionBlocked('RANGE_REQUEST_BINDING')
            self.ticket=t
        else:
            G.safety_mode()
            mode.validate_store(self.path,cap,self.request)
            self.ticket=G.ticket('RANGE')
    def event(self, kind, **fields):
        if self.mode:self.mode.event(kind,task_id=self.request['task_id'],**fields)
    def hit(self, point):
        if self.mode:self.mode.hit(point,self)
    def valid(self):
        self.G.execution_deadline(self.request['case'])
        if self.mode:self.mode.validity()
    def sync(self, fd, stage):
        self.hit(stage+'.before_fsync')
        try:
            if self.mode and self.mode.inject_io(stage+'.before_fsync','fsync_error'):
                self.event('IO_RESULT',stage=stage,errno=5,syscall_invoked=False)
                raise OSError(5,'INJECTED_FSYNC_EIO')
        except OSError:
            if not(self.mode and self.mode.mutant=='ignore_fsync'):raise
            self.event('IGNORED_ERROR',stage=stage)
            return
        self.G.sync_fd(fd,'range.'+stage)
        self.hit(stage+'.sync_return_unobserved')
        self.hit(stage+'.after_fsync')
    def full(self,fd,raw,stage):
        self.hit(stage+'.before_write')
        short=self.mode and self.mode.inject_io(stage+'.before_write','short_write')
        written=self.G.timed('range.'+stage+'.write',os.write,fd,raw[:max(1,len(raw)//2)] if short else raw)
        self.event('WRITE_RESULT',stage=stage,requested=len(raw),written=written)
        if short:self.mode.capture_partial(fd,stage,written)
        if written!=len(raw):
            if not(self.mode and self.mode.mutant=='ignore_short_write'):
                raise self.G.AdmissionBlocked('SHORT_WRITE')
            self.event('IGNORED_ERROR',stage=stage)
        self.hit(stage+'.after_write')
    def atomic(self,path,data,stage):
        p=self.G._inside(path,self.G.OUT);p.parent.mkdir(parents=True,exist_ok=True)
        raw=self.G.timed('range.'+stage+'.encode',lambda:canonical(data).encode())
        if len(raw)>16384:raise self.G.AdmissionBlocked('RANGE_RECORD_SIZE')
        tmp=p.with_name(p.name+'.tmp.%s.%s'%(os.getpid(),threading.get_ident()))
        fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        try:self.full(fd,raw,stage);self.sync(fd,stage+'.file')
        finally:os.close(fd)
        os.replace(tmp,p);self.hit(stage+'.after_rename')
        fd=os.open(p.parent,os.O_RDONLY|os.O_DIRECTORY)
        try:self.sync(fd,stage+'.directory')
        finally:os.close(fd)
        self.hit(stage+'.after_dirsync')
    def journal(self,record,stage):
        raw=self.G.timed('range.'+stage+'.encode',lambda:(canonical(record)+'\n').encode())
        fd=os.open(self.path.with_suffix(self.path.suffix+'.journal.jsonl'),
                   os.O_WRONLY|os.O_CREAT|os.O_APPEND|os.O_NOFOLLOW,0o600)
        try:self.full(fd,raw,stage);self.sync(fd,stage)
        finally:os.close(fd)
    @contextmanager
    def lock(self):
        if self.mode and self.mode.mutant=='lost_update':
            fd=os.open(self.path,os.O_RDWR|os.O_NOFOLLOW)
            try:
                raw=os.pread(fd,24,0)
                if len(raw)!=24 or raw[:8]!=self.G.COUNTER_MAGIC:
                    raise self.G.AdmissionBlocked('BAD_TEST_COUNTER')
                used,cap=struct.unpack('<QQ',raw[8:])
                if cap!=self.cap or used>cap:raise self.G.AdmissionBlocked('BAD_TEST_CAP')
                self.mode.rendezvous('read')
                yield fd,used,self.path
            finally:os.close(fd)
        else:
            with self.G._counter_lock(self.path,self.cap,self.request['case']) as v:yield v
    def validate_fact(self,fact,used):
        G=self.G
        if fact.get('protocol')!=G.BUDGET_PROTOCOL:raise G.AdmissionBlocked('FACT_PROTOCOL_MISMATCH')
        if fact['request']!=self.request:raise G.AdmissionBlocked('TASK_ID_REQUEST_CONFLICT')
        lo,hi=fact['credit_range']
        if type(lo) is not int or type(hi) is not int or not(0<=lo<hi<=used) or hi-lo!=self.request['N']:
            raise G.AdmissionBlocked('EXACT_FACT_RANGE_MISMATCH')
        material={'request':self.request,'credit_range':[lo,hi],'owner':fact['owner']}
        if request_hash(material)!=fact['lease_id']:raise G.AdmissionBlocked('EXACT_FACT_IDENTITY_MISMATCH')
        if fact['delivery_state'] not in ('UNCLAIMED','CLAIMED'):
            raise G.AdmissionBlocked('EXACT_FACT_DELIVERY_STATE')
    def reserve(self):
        G=self.G
        G.timing_event('reserve.request')
        if self.mode:self.mode.before_call('reserve')
        self.valid()
        if self.mode:
            self.mode.refund_prepared(self)
            if self.mode.mutant=='early_grant' and self.mode.phase=='primary':
                self.event('GRANT',lease_id='INVALID_EARLY',N=self.request['N'])
                self.mode.semantic(1)
        self.event('RESERVE_REQUEST',request=self.request,request_sha256=request_hash(self.request))
        self.hit('before_reserve')
        try:
            with self.lock() as (fd,used,p):
                self.valid()
                if self.mode is None:
                    checked,t=G._task_contract(self.request['task_id'],self.request['N'])
                    if checked!=self.request or G._TICKET is None or t['main_identity']!=G.identity():
                        raise G.AdmissionBlocked('EXACT_RESERVATION_OWNER_REQUIRED')
                fp=fact_path(p,self.request['task_id'])
                if fp.exists() and not(self.mode and self.mode.mutant=='duplicate_task'):
                    fact=G.read(fp);self.validate_fact(fact,used)
                    self.event('IDEMPOTENT_FACT',lease_id=fact['lease_id'])
                    return Reservation(self,fact,False,_MINT)
                n=self.request['N']
                soft=100000 if p==G.OUT/'visits.bin' and G._TICKET['case']!='FORMAL' else self.cap
                if used+n>min(self.cap,soft):raise G.LimitReached('VISIT_OR_CALIBRATION_LIMIT')
                rec={'protocol':G.BUDGET_PROTOCOL,'status':'PREPARED','before':used,'after':used+n,
                     'amount':n,'cap':self.cap,'request':self.request,**G.stamp()}
                intent=p.with_suffix(p.suffix+'.intent.json')
                self.atomic(intent,rec,'prepared')
                self.journal(rec,'journal_prepared')
                self.hit('counter.before_write')
                if G.timed('range.counter.write',os.pwrite,fd,struct.pack('<Q',used+n),8)!=8:
                    raise G.AdmissionBlocked('SHORT_COUNTER_WRITE')
                self.hit('counter.after_write');self.sync(fd,'counter')
                rec={**rec,'status':'COMMITTED',**G.stamp()}
                self.journal(rec,'journal_committed')
                fact={'protocol':G.BUDGET_PROTOCOL,'request':self.request,'credit_range':[used,used+n],
                      'owner':G.identity(),'delivery_state':'UNCLAIMED','executor':None,'reserved_at':G.stamp()}
                fact['lease_id']=request_hash({'request':self.request,'credit_range':fact['credit_range'],'owner':fact['owner']})
                self.atomic(fp,fact,'registry')
                self.atomic(intent,rec,'committed')
                G.timing_event('reserve.committed_barriers_done')
                self.event('COMMIT',lease_id=fact['lease_id'],before=used,after=used+n,request=self.request)
                self.valid()
                return Reservation(self,fact,True,_MINT)
        except G.LimitReached:raise
        except BaseException as exc:
            if self.mode is None:G.halt_budget(exc)
            raise
    def claim(self,lease_id):
        G=self.G
        if self.mode:self.mode.before_call('claim')
        self.valid()
        if self.mode is None:
            G.kernel_admission(self.ticket)
            if os.getppid()!=self.ticket['main_identity']['pid'] or G.identity(os.getppid())!=self.ticket['main_identity']:
                raise G.AdmissionBlocked('LOCAL_CREDIT_PARENT_MISMATCH')
        try:
            with self.lock() as (_,used,_):
                fact=G.read(fact_path(self.path,self.request['task_id']));self.validate_fact(fact,used)
                if fact['lease_id']!=lease_id:raise G.AdmissionBlocked('LOCAL_CREDIT_LEASE_MISMATCH')
                bypass=self.mode and self.mode.mutant in ('reissue','reset_claim')
                owner_ok=(fact['owner']==G.identity()) if self.mode else (fact['owner']==self.ticket['main_identity'])
                if not owner_ok and not bypass:raise G.AdmissionBlocked('LOCAL_CREDIT_OWNER_MISMATCH')
                if fact['delivery_state']!='UNCLAIMED' and not(self.mode and self.mode.mutant=='reset_claim'):
                    raise G.AdmissionBlocked('LOCAL_CREDIT_ALREADY_CLAIMED')
                fact={**fact,'delivery_state':'CLAIMED','executor':G.identity(),'claimed_at':G.stamp()}
                self.atomic(fact_path(self.path,self.request['task_id']),fact,'claimed')
                self.event('CLAIM',lease_id=lease_id,owner=fact['owner'],executor=fact['executor'])
                self.valid()
                credits=Credits(self,fact,_MINT)
                self.event('GRANT',lease_id=lease_id,N=self.request['N'])
                G.timing_event('local_credit.granted_to_executor')
                return credits
        except G.LimitReached:raise
        except BaseException as exc:
            if self.mode is None:G.halt_budget(exc)
            raise

class Reservation:
    def __init__(self,store,fact,created,_mint=None):
        if _mint is not _MINT:raise store.G.AdmissionBlocked('RESERVATION_FACTORY_REQUIRED')
        self.store=store;self.fact=json.loads(canonical(fact));self.created=created
        self.issued=False;self.lock=threading.Lock()
    def dispatch_once(self):
        s=self.store;G=s.G
        if s.mode:s.mode.before_call('dispatch')
        with self.lock:
            bypass=s.mode and s.mode.mutant in ('reissue','reset_claim')
            if (not self.created or self.issued or self.fact['owner']!=G.identity()) and not bypass:
                raise G.AdmissionBlocked('RESERVATION_FACT_IS_NOT_FRESH_EXECUTION_CREDIT')
            s.valid();self.issued=True
            s.event('DISPATCH',lease_id=self.fact['lease_id'],owner=self.fact['owner'])
            G.timing_event('local_credit.dispatch_once')
            return json.loads(canonical(self.fact))

class Credits:
    def __init__(self,store,fact,_mint=None):
        if _mint is not _MINT:raise store.G.AdmissionBlocked('CREDIT_FACTORY_REQUIRED')
        self.store=store;self.fact=fact;self.N=fact['request']['N'];self.used=0
        self.actor=store.G.identity();self.lock=threading.Lock();self.parent=None
        if fact['delivery_state']!='CLAIMED' or fact['executor']!=self.actor:
            raise store.G.AdmissionBlocked('CLAIMED_FACTORY_REQUIRED')
        if store.mode is None:
            owner=fact['owner'];G=store.G
            if os.getppid()!=owner['pid'] or G.identity(owner['pid'])!=owner:
                raise G.AdmissionBlocked('LOCAL_PARENT_IDENTITY_CHANGED')
            self.parent=os.pidfd_open(owner['pid'])
            if os.getppid()!=owner['pid'] or G.identity(owner['pid'])!=owner:
                os.close(self.parent);raise G.AdmissionBlocked('LOCAL_PARENT_PIDFD_RACE')
    def visit(self):
        s=self.store;G=s.G;begin=G.monotonic_ns();utc_begin=G.time.time_ns()
        if s.mode:s.mode.before_call('visit')
        with self.lock:
            if G.identity()!=self.actor:raise G.AdmissionBlocked('LOCAL_CREDIT_INCARNATION_MISMATCH')
            if self.parent is not None and select.select([self.parent],[],[],0)[0]:
                raise G.AdmissionBlocked('LOCAL_CREDIT_PARENT_EXIT')
            s.valid()
            allow=s.mode and s.mode.mutant=='allow_extra' and self.used==self.N
            if self.used>=self.N and not allow:raise G.LimitReached('LOCAL_EXACT_CREDIT_EXHAUSTED')
            self.used+=1
            s.event('DEBIT',lease_id=self.fact['lease_id'],local_used=self.used,N=self.N)
        if s.mode is None:
            end=G.monotonic_ns();G._timing('local_credit.debit',begin,end,utc_begin,G.time.time_ns())
    def close(self):
        if self.parent is not None:os.close(self.parent);self.parent=None
