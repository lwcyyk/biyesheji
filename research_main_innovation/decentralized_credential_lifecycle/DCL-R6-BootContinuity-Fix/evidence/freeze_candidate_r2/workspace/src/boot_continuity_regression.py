"""BC restart simulation fixtures. No real WSL shutdown or restart is issued."""
import copy
import hashlib
import json
import boot_continuity as BC


class Kernel:
    def __init__(self):
        self.epoch=1;self.pid=101;self.ticks=10;self.alive=True
        self.static=True;self.resources=True;self.privileges=True;self.closed=False;self.stop=False
        self.window=False;self.counter=False;self.used=0;self.cap=False;self.sealed=False;self.active=False
        self.cache=None;self.cache_rule=True;self.chain={};self.last_good=None
        self.binding={'batch_id':'batch07','execution_lock_sha256':'frozen-lock','source':'frozen-source'}
    def owner(self):return {'pid':self.pid,'start_ticks':self.ticks,'boot_id':self.boot()}
    def boot(self):return '00000000-0000-4000-8000-%012d'%self.epoch
    def observe(self):
        return {'boot_id':self.boot(),'owner':self.owner(),'process_alive':self.alive,'identity_valid':self.privileges,
                'static_valid':self.static,'resource_valid':self.resources,'closed':self.closed,'stop':self.stop,
                'window_exists':self.window,'counter_exists':self.counter,'budget_used':self.used,
                'chain_boots':[self.chain.get(k) for k in ['inspect','prepare','final']],
                'binding':dict(self.binding),'cap_live':self.cap,'sealed':self.sealed,'now':1,
                'service_active':self.active,'stable_main_pid':self.alive and self.active}
    def event(self,e):
        if e=='static_cache':self.cache={'source':'frozen-source','rule':'BC-A/1'}
        elif e=='cache_rule_change':self.cache_rule=False
        elif e=='artifact_drift':self.static=False
        elif e=='prior_window':self.window=True;self.counter=True;self.used=37
        elif e=='prior_closed':self.closed=True
        elif e in ('inspect','prepare','final'):
            if e=='inspect':self.chain={}
            self.chain[e]=self.boot()
        elif e=='reboot':
            self.last_good=self.observe();self.epoch+=1;self.alive=False;self.cap=False;self.sealed=False;self.active=False
        elif e in ('new_process','recycle_owner'):
            self.alive=True;self.pid=101 if e=='recycle_owner' else self.pid+1;self.ticks=10
        elif e=='reload_old_cap':self.cap=True;self.sealed=True
        elif e=='stop':self.stop=True
        elif e in ('orchestrator_exit','launcher_exit'):self.alive=False;self.cap=False;self.active=False
        elif e=='resources_change':self.resources=False
        elif e=='identity_change':self.privileges=False
        elif e=='service_active':self.active=True
        elif e=='initialize_window':
            if not self.window:self.window=True;self.counter=True;self.used=1


class Subject:
    def __init__(self,mutant=None):
        self.k=Kernel();self.mutant=mutant;self.ticket=None;self.claim={'initial_entered':False}
        self.activations=0;self.started=False;self.reset=False
    def observed(self):
        e=self.k.observe();m=self.mutant
        if m=='cached_snapshot' and self.k.last_good is not None:e=copy.deepcopy(self.k.last_good)
        if m=='ignore_closed':e['closed']=False;e['stop']=False
        if m=='reset_budget':e['window_exists']=False;e['counter_exists']=False
        if m=='ignore_resources':e['resource_valid']=True
        if m=='ignore_identity':e['identity_valid']=True
        if m=='ignore_static':e['static_valid']=True
        return e
    def step(self,event):
        before=self.k.observe();self.k.event(event);decision='NONE';error=None;observed=None
        try:
            if event=='issue':
                observed=self.observed();BC.eligibility(observed)
                self.ticket={'boot_id':observed['boot_id'],'owner':observed['owner'],
                             'binding':observed['binding'],'expires':100}
                self.k.cap=True;self.k.sealed=True;decision='ISSUED'
                if self.mutant=='reset_budget' and self.k.used:
                    self.k.used=0;self.k.window=False;self.k.counter=False;self.reset=True
            elif event in ('bad_batch','bad_lock'):
                if self.ticket is None:raise BC.Rejected('SIM_TICKET_MISSING')
                self.ticket['binding']=dict(self.ticket['binding'])
                self.ticket['binding']['batch_id' if event=='bad_batch' else 'execution_lock_sha256']='wrong'
                # A new current sealed object is constructed with wrong binding;
                # this simulates an issuer error, never mutation of a sealed fd.
                self.k.cap=True;self.k.sealed=True
            elif event=='exec':
                if self.ticket is None:raise BC.Rejected('SIM_TICKET_MISSING')
                observed=self.observed();ticket=copy.deepcopy(self.ticket);claim=dict(self.claim)
                if self.mutant=='ignore_epoch':
                    ticket['boot_id']=observed['boot_id'];ticket['owner']=observed['owner']
                if self.mutant=='ignore_binding':ticket['binding']=observed['binding']
                if self.mutant=='ignore_once':claim['initial_entered']=False
                BC.ticket_policy(ticket,observed,claim)
                self.claim['initial_entered']=True;self.activations+=1;decision='ACTIVATED'
            elif event in ('service_active','confirm'):
                observed=self.observed();observed['same_boot']=self.ticket is not None and self.ticket['boot_id']==self.k.boot()
                BC.service_policy(observed)
                if self.activations!=1:raise BC.Rejected('SIM_ACTIVATION_COUNT')
                self.started=True;decision='STARTED'
            elif event=='request_ok' and self.mutant=='request_is_start':self.started=True;decision='STARTED'
        except BC.Rejected as exc:decision='REJECTED';error=str(exc)
        return {'event':event,'before':before,'facts':self.k.observe(),'subject_observed':observed,
                'ticket':copy.deepcopy(self.ticket),'decision':decision,'error':error,
                'activations':self.activations,'started':self.started,'reset':self.reset}


def run_suite(G):
    import boot_continuity_oracle as oracle
    cfg=G.trusted(G.SOURCE.parent/'inputs/boot_contract.json')
    a,m=G.authorization()
    if G.digest(G.SOURCE.parent/'inputs/boot_contract.json')!=m['boot_contract_sha256']:raise G.AdmissionBlocked('BC_TEST_CONTRACT')
    old=G._TICKET;G._TICKET=G.ticket('C09H');base=G.count();binding=G.safety_binding()
    def charge():
        if G.count()-base>=cfg['test_hard_visits']:raise G.LimitReached('BC_TEST_VISIT_CAP')
        G.c09h_charge()
    try:
        charge()
        with BC.Store() as store:
            for i,job in enumerate(cfg['jobs']):
                G.root_checkpoint();start=G.count()
                for _ in range(cfg['driver_prepay']):charge()
                subject=Subject(job['mutant']);trace=[subject.step(e) for e in job['events']]
                row={'schema':'BC-SIM-RAW/1','profile':'SIMULATED_RESTART/1','case_id':job['case_id'],
                     'input_sha256':hashlib.sha256(BC.canon(job)).hexdigest(),'binding':binding,
                     'actor':G.identity(),'stamp':G.stamp(),'global_before':start,'global_after':G.count(),'trace':trace}
                store.put('bc_case_%03d.json'%i,row,exclusive=True)
                result=oracle.check_job(G.ROOT/'inputs/root_private/boot',job,i,binding)
                if not result['accepted']:raise G.AdmissionBlocked('BC_TEST_FIRST_FAILURE:'+job['case_id'])
            for job in cfg['jobs']:charge()
            report=oracle.check_suite(G.ROOT/'inputs/root_private/boot',cfg,binding)
            if not report['accepted']:raise G.AdmissionBlocked('BC_RAW_ORACLE_FAILED')
            report.update(checker_sha256=G.digest(G.SOURCE/'boot_continuity_oracle.py'),
                          contract_sha256=G.digest(G.SOURCE.parent/'inputs/boot_contract.json'),
                          start_sha256=G.digest(G.ROOT/'inputs/BOOT_START.json'),
                          global_before=base,global_after=G.count(),sample=G.stamp())
            store.put('BOOT_CONTINUITY_QUALIFICATION.json',report,public=True)
            return report
    finally:G._TICKET=old
