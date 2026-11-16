"""MR-SIMULATION/1 finite fixtures. Native OS failures require separate diagnostics."""
import copy
import hashlib
import os
import manager_recovery as M
import manager_recovery_oracle as O
import boot_continuity as BC

class Subject:
    def __init__(self,job):
        self.mutant=job['mutant'];self.saved=None;self.review=None;self.resume_count=0
        self.closed=False;self.stop=False;self.T0=10;self.R=31;self.first_failure=None;self.close_calls=0
    def step(self,frame):
        facts=copy.deepcopy(frame['facts']);action=frame['action'];truth=copy.deepcopy(facts)
        self.closed=self.closed or facts['closed'];self.stop=self.stop or facts['stop']
        facts['closed']=facts['closed'] or self.closed;facts['stop']=facts['stop'] or self.stop
        if self.saved is None:self.saved=copy.deepcopy(facts)
        if self.mutant=='stale_snapshot':facts=copy.deepcopy(self.saved)
        if self.mutant=='missing_ack':facts['ack']=True
        if self.mutant=='ignore_stop':facts['stop']=False
        if self.mutant=='reactivate_closed':facts['closed']=False;self.closed=False;facts['stop']=False
        decision=M.classify(facts)
        if self.mutant=='skip_review' and decision=='REVIEW_PENDING':decision='REVIEWED_EXPECTED'
        grant=False;closure=None
        if action in ('review','resume','repeat_resume'):
            self.review=decision
            if action in ('resume','repeat_resume') and decision=='REVIEWED_EXPECTED':
                if self.resume_count==0:self.resume_count=1;grant=True
        critical=frame['critical'] or action=='close'
        if critical:
            self.close_calls+=1
            if self.first_failure is None:self.first_failure=frame['event_id']
            if self.mutant!='no_auto_close':self.stop=True;self.closed=True
            if self.mutant=='new_window_repeat' and self.close_calls>1:self.T0+=1;self.R=0
            exited=frame['other_roles_exited']
            if self.mutant=='false_cleanup_success':exited=True
            closure=M.closure_status(self.closed,frame['payload_empty'],exited,frame['cleanup_errors'])
        return {'action':action,'injection_point':frame['injection_point'],'fault_source':frame['fault_source'],
            'actual_facts':truth,'observed_facts':facts,'decision':decision,'grant':grant,
            'resume_count':self.resume_count,'stop':self.stop,'closed':self.closed,'T0':self.T0,'R':self.R,
            'first_failure':self.first_failure,'closure':closure,'actual_other_roles_exited':frame['other_roles_exited'],
            'payload_empty':frame['payload_empty'],'cleanup_errors':frame['cleanup_errors']}

def run_suite(G):
    if os.geteuid()!=0:raise G.AdmissionBlocked('MR_ROOT_SUITE_REQUIRED')
    cfg=M.contract(G);old=G._TICKET;G._TICKET=G.ticket('C00');binding=G.safety_binding();base=G.count()
    def charge():
        if G.count()-base>=cfg['regression_hard_visits']:raise G.LimitReached('MR_REGRESSION_VISIT_CAP')
        G.execution_deadline('C00');G.reserve_counter(G.OUT/'visits.bin',G.VISIT_CAP)
    try:
        charge()
        with BC.Store() as store:
            for i,job in enumerate(cfg['jobs']):
                G.root_checkpoint();before=G.count()
                for _ in range(cfg['driver_prepay']):charge()
                subject=Subject(job);trace=[subject.step(frame) for frame in job['frames']]
                row={'schema':'MR-SIM-RAW/1','origin':'MR-SIMULATION/1','case_id':job['case_id'],'binding':binding,
                    'input_sha256':hashlib.sha256(M.canonical(job)).hexdigest(),'trace':trace,'sample':G.stamp(),
                    'global_before':before,'global_after':G.count()}
                store.put('mr_case_%03d.json'%i,row,exclusive=True)
                check=O.check_job(G.ROOT/'inputs/root_private/boot',job,i,binding)
                if not check['accepted']:raise G.AdmissionBlocked('MR_FIRST_TEST_FAILURE:'+job['case_id']+':'+check['status'])
            for job in cfg['jobs']:charge()
            report=O.check_suite(G.ROOT/'inputs/root_private/boot',cfg,binding)
            if not report['accepted']:raise G.AdmissionBlocked('MR_RAW_AUDIT_FAILED')
            report.update(schema='MR-QUALIFICATION/1',checker_sha256=G.digest(G.SOURCE/'manager_recovery_oracle.py'),
                contract_sha256=G.digest(G.SOURCE.parent/'inputs/manager_contract.json'),global_before=base,global_after=G.count(),sample=G.stamp())
            store.put('MR_QUALIFICATION.json',report,exclusive=True,public=True)
            return report
    finally:G._TICKET=old
