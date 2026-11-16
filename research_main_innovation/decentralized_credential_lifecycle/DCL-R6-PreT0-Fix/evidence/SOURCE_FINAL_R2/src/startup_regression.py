"""PT-SIMULATION/1 fixtures; executed only after real C00 in a valid window."""
import copy
import hashlib
import os
import startup_lifecycle as P
import startup_oracle as O
import boot_continuity as BC

class Subject:
    def __init__(self,job):
        self.mutant=job['mutant'];self.phase='PRE_WINDOW';self.state=False;self.counter=False;self.intent=False
        self.cp=False;self.T0=None;self.R=None;self.closed=False;self.stop=False;self.context=False;self.admin=False;self.native='NATIVE_SEAL_NOT_APPLICABLE';self.initializations=0
    def step(self,frame):
        truth=copy.deepcopy(frame);op=frame['op'];m=self.mutant
        facts={k:frame[k] for k in ['binding','boot','owner','deadline','checkpoint_integrity']}
        facts.update(phase=self.phase,closed=self.closed,stop=self.stop,pre_context=self.context,runtime_intent=self.intent,state=self.state,counter=self.counter,runtime_checkpoint=self.cp)
        if m=='delete_pre_validation':facts.update(binding=True,boot=True,owner=True,deadline=True,pre_context=True)
        if m=='force_runtime_pre':facts['phase']='RUNNING'
        if m=='missing_checkpoint_pass' and self.phase in ('RUNTIME_READY','RUNTIME_ARMED','RUNNING'):
            facts.update(runtime_checkpoint=True,checkpoint_integrity=True)
        if m=='missing_deadline':facts['deadline']=True
        if m=='reactivate_closed':facts['closed']=False;facts['stop']=False;self.closed=False
        decision=P.phase_policy(facts);grant=False;error=None
        if op=='enter':
            if all(frame[k] for k in ['binding','boot','owner','deadline']) or m=='delete_pre_validation':self.context=True
        elif op=='precheck':
            if m=='force_runtime_pre':error='IPC_STATE_MISSING'
        elif op=='qualify' and decision=='PREWINDOW_ALLOWED_NO_WORK':self.phase='PREFLIGHT_QUALIFIED'
        elif op=='begin' and decision=='PREWINDOW_ALLOWED_NO_WORK' and self.phase=='PREFLIGHT_QUALIFIED':
            self.intent=True;self.phase='RUNTIME_INITIALIZING'
        elif op=='state' and self.intent and not self.closed:
            if self.state:error='DUPLICATE_STATE'
            else:self.state=True;self.T0=10;self.initializations+=1
        elif op=='counter' and self.state and not self.closed:
            if self.counter:error='DUPLICATE_COUNTER'
            else:self.counter=True;self.R=0
        elif op=='checkpoint' and self.state and self.counter and not self.closed:
            self.cp=True;self.phase='RUNTIME_READY'
        elif op=='arm' and decision=='RUNTIME_INSPECTION_ALLOWED':self.phase='RUNTIME_ARMED'
        elif op=='work' and decision=='WORK_ALLOWED':self.phase='RUNNING';grant=True;self.R+=1
        elif op=='lose_checkpoint':self.cp=False
        elif op=='corrupt_checkpoint':pass
        elif op=='fail':
            if m!='no_auto_stop':self.stop=True;self.closed=True
        elif op=='repeat_fail':
            self.stop=True;self.closed=True
            if m=='new_budget_after_fail':self.T0=11;self.R=0;self.state=True;self.counter=True;self.initializations+=1
        elif op=='seal':
            self.admin=frame['admin_integrity'] and frame['exited']
            if not self.state and not self.counter and not self.intent:self.native='NATIVE_SEAL_NOT_APPLICABLE'
            else:self.native='NATIVE_SEAL_COMPLETED' if self.cp and frame['native_success'] and frame['exited'] else 'NATIVE_SEAL_UNRESOLVED'
            if m=='admin_as_native' and self.admin:self.native='NATIVE_SEAL_COMPLETED'
        cleanup='CLEANUP_CONFIRMED' if self.closed and frame['exited'] else 'CLEANUP_UNKNOWN'
        if m=='unknown_as_success':cleanup='CLEANUP_CONFIRMED'
        return {'actual_input':truth,'observed':facts,'op':op,'decision':decision,'grant':grant,'error':error,
            'phase':self.phase,'pre_context':self.context,'state':self.state,'counter':self.counter,'runtime_intent':self.intent,
            'checkpoint':self.cp,'T0':self.T0,'R':self.R,'closed':self.closed,'stop':self.stop,'cleanup':cleanup,
            'admin_sealed':self.admin,'native_status':self.native,'initializations':self.initializations}

def run_suite(G):
    if os.geteuid()!=0:raise G.AdmissionBlocked('PT_ROOT_SUITE_REQUIRED')
    cfg=P.config(G);old=G._TICKET;G._TICKET=G.ticket('C00');base=G.count();binding=G.safety_binding()
    def charge():
        if G.count()-base>=cfg['regression_hard_visits']:raise G.LimitReached('PT_REGRESSION_CAP')
        G.execution_deadline('C00');G.reserve_counter(G.OUT/'visits.bin',G.VISIT_CAP)
    try:
        charge()
        with BC.Store() as store:
            for i,job in enumerate(cfg['jobs']):
                before=G.count()
                for _ in range(cfg['driver_prepay']):charge()
                subject=Subject(job);trace=[subject.step(f) for f in job['frames']]
                store.put('pt_case_%03d.json'%i,{'schema':'PT-SIM-RAW/1','origin':'PT-SIMULATION/1','case_id':job['case_id'],
                    'binding':binding,'input_sha256':hashlib.sha256(P.canonical(job)).hexdigest(),'trace':trace,
                    'before':before,'after':G.count(),'sample':G.stamp()},exclusive=True)
                q=O.check_job(G.ROOT/'inputs/root_private/boot',job,i,binding)
                if not q['accepted']:raise G.AdmissionBlocked('PT_FIRST_TEST_FAILURE:'+job['case_id']+':'+q['status'])
            for job in cfg['jobs']:charge()
            q=O.check_suite(G.ROOT/'inputs/root_private/boot',cfg,binding)
            if not q['accepted']:raise G.AdmissionBlocked('PT_SUITE_FAILED')
            q.update(schema='PT-QUALIFICATION/1',contract_sha256=G.digest(G.SOURCE.parent/'inputs/startup_contract.json'),
                checker_sha256=G.digest(G.SOURCE/'startup_oracle.py'),sample=G.stamp(),before=base,after=G.count())
            store.put('PT_QUALIFICATION.json',q,exclusive=True,public=True)
            return q
    finally:G._TICKET=old
