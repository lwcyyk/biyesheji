"""C09H synthetic event interleavings. Role executes only in an authorized C09H controller."""
import hashlib
import json
from pathlib import Path
import c09_handoff as H

class Subject:
    def __init__(self,mutant=None):
        self.f=H.synthetic_initial();self.state='PENDING';self.count=0;self.old=None;self.mutant=mutant
    def step(self,e):
        f=self.f
        if e=='prepare':f['prepared']=True
        elif e=='read_old':self.old=dict(f)
        elif e=='commit':f['commit']=True;f['durable_ack']=True
        elif e=='exit23':f['exit_observed']=True
        elif e=='exit_other':f['exit_observed']=True
        elif e=='witness23':f['witness']=23
        elif e=='witness_other':f['witness']=17
        elif e=='close':f['closed']=True
        elif e=='expire':f['now']=13
        elif e in ('write_interrupted','fsync_failed'):f['commit']=False;f['durable_ack']=False
        elif e in ('bad_batch','bad_boot','bad_lock'):f['binding_ok']=False
        elif e=='unready':f['receiver_ready']=False
        elif e=='receiver_dead':f['receiver_alive']=False
        elif e=='stop_lost':f['stop_alive']=False
        elif e=='bad_budget':f['budget_ok']=False
        elif e=='bad_sender':f['sender_ok']=False
        elif e=='bad_version':f['version_ok']=False
        elif e=='bad_window':f['window_ok']=False
        elif e not in ('observe','verify','repeat'):raise ValueError('UNFROZEN_EVENT')
        if e not in ('observe','verify','repeat'):return self.snapshot(e)
        check=dict(f)
        if self.mutant=='use_old_snapshot' and self.old is not None:
            verdict='FAILED' if not self.old['commit'] else H.classify(self.old)
        else:
            if self.mutant=='ignore_version':check['version_ok']=True
            if self.mutant=='reopen_closed' and check['closed']:
                check.update(closed=False,prepared=True,commit=True,durable_ack=True,
                             exit_observed=True,witness=23,now=0)
            if self.mutant=='exit23_only' and check['witness']==23:verdict='VERIFIED'
            elif self.mutant=='unknown_success' and check['exit_observed']:verdict='VERIFIED'
            else:verdict=H.classify(check)
        if self.state=='CLOSED' and self.mutant!='reopen_closed':verdict='CLOSED'
        if self.state=='FAILED' and self.mutant is None:verdict='FAILED'
        if verdict=='VERIFIED' and (self.state!='VERIFIED' or self.mutant=='duplicate_classification'):
            self.count+=1
        self.state=verdict
        return self.snapshot(e)
    def snapshot(self,e):
        return {'event':e,'facts':dict(self.f),'subject_state':self.state,'classification_count':self.count}

def run_suite(G,budget):
    if G._TICKET is None or G._TICKET['case']!='C09H' or G.state()['status']!='CALIBRATING':
        raise G.AdmissionBlocked('C09H_CALIBRATION_MODE_ONLY')
    cfg=G.c09_contract();binding=G.safety_binding();base=G.OUT/'c09_tests'
    base.mkdir(exist_ok=False)
    import c09_oracle
    G.c09h_charge(budget)
    for job in cfg['jobs']:
        p=G._inside(base/job['case_id'],G.OUT);p.mkdir(exist_ok=False)
        if len(job['events'])>cfg['max_events_per_job']:raise G.AdmissionBlocked('C09H_EVENT_CAP')
        subject=Subject(job['mutant'])
        for index,e in enumerate(job['events']):
            G.c09h_charge(budget)
            row=subject.step(e)
            row.update({'case_id':job['case_id'],'event_index':index,'binding':binding,
                        'input_sha256':hashlib.sha256(H.canonical(job).encode()).hexdigest(),
                        'actor':G.identity(),'stamp':G.stamp(),'global_reserved':G.count()})
            G.write(p/('%03d.json'%index),row)
        G.c09h_charge(budget)
        result=c09_oracle.check_job(p,job,binding)
        G.write(p/'oracle.json',result)
        if not result['accepted']:raise G.AdmissionBlocked('C09H_'+result['status']+':'+job['case_id'])
    return {'case':'C09H','status':'PASS','jobs':len(cfg['jobs']),'binding':binding,'sample':G.stamp()}
