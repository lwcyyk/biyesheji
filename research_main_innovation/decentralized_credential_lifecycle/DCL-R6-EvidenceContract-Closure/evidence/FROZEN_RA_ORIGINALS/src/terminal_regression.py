"""TR40 synthetic policy observations, prepaid in the original active window."""
import copy
import hashlib
import os
import boot_continuity as BC
import terminal_evidence as T
import terminal_oracle as O

def contract(G):
    a,m=G.authorization();p=G.SOURCE.parent/'inputs/terminal_contract.json';c=G.trusted(p)
    if (c['version']!='RuntimeAdapt-static-1/r1' or c['batch_id']!=G.ROOT.name or len(c['jobs'])!=40 or
        len({j['case_id'] for j in c['jobs']})!=40 or any(len(j['frames'])>4 for j in c['jobs']) or
        G.digest(p)!=m['terminal_contract_sha256'] or a.get('terminal_contract_sha256')!=G.digest(p) or
        c['driver_prepay']!=16 or c['hard_visits']!=960):raise G.AdmissionBlocked('TR_CONTRACT_BINDING')
    return c

def subject_step(frame,mutant):
    source=copy.deepcopy(frame);f=copy.deepcopy(frame['facts'])
    if mutant=='skip_identity':f['identity']=True
    if mutant=='default_deadline':f['window']=True
    if mutant=='ignore_journal':f['budget']=True
    out=T.terminal_policy(f);out.update(budget_delta=0,phase_delta=0,originals_modified=False,used_default_deadline=False)
    if mutant=='grant_terminal_work':out['work_allowed']=True
    if mutant=='rebuild_budget':out['budget_init_allowed']=True;out['budget_delta']=-1907
    if mutant=='default_deadline':out['used_default_deadline']=True
    if mutant=='upgrade_unknown':out['internal_status']='CLOSED_CLEANUP_CONFIRMED'
    if mutant=='false_seal':out['native_ready']=True;out['native_status']='NATIVE_SEAL_COMPLETED'
    if mutant=='write_original':out['originals_modified']=True
    return {'origin':'TR-SIMULATION/1','actual_input':source,'observed':out}

def run_suite(G):
    if os.geteuid()!=0:raise G.AdmissionBlocked('TR_ROOT_SUITE')
    cfg=contract(G);old=G._TICKET;G._TICKET=G.ticket('C00');base=G.count();binding=G.safety_binding()
    def charge():
        if G.count()-base>=cfg['hard_visits']:raise G.LimitReached('TR_REGRESSION_CAP')
        G.execution_deadline('C00');G.reserve_counter(G.OUT/'visits.bin',G.VISIT_CAP)
    try:
        charge()
        with BC.Store() as store:
            for i,job in enumerate(cfg['jobs']):
                before=G.count()
                for _ in range(cfg['driver_prepay']):charge()
                trace=[subject_step(frame,job['mutant']) for frame in job['frames']]
                store.put('tr_case_%03d.json'%i,{'schema':'TR-RAW/1','origin':'TR-SIMULATION/1','case_id':job['case_id'],'binding':binding,
                    'input_sha256':hashlib.sha256(T.canonical(job)).hexdigest(),'trace':trace,'before':before,'after':G.count(),'sample':G.stamp()},exclusive=True)
                q=O.check_job(G.ROOT/'inputs/root_private/boot',job,i,binding)
                if not q['accepted']:raise G.AdmissionBlocked('TR_FIRST_TEST_FAILURE:'+job['case_id']+':'+q['status'])
            for job in cfg['jobs']:charge()
            q=O.check_suite(G.ROOT/'inputs/root_private/boot',cfg,binding)
            if not q['accepted']:raise G.AdmissionBlocked('TR_SUITE_FAILED')
            q.update(contract_sha256=G.digest(G.SOURCE.parent/'inputs/terminal_contract.json'),checker_sha256=G.digest(G.SOURCE/'terminal_oracle.py'),
                before=base,after=G.count(),sample=G.stamp())
            store.put('tr_qualification.json',q,exclusive=True);return q
    finally:G._TICKET=old

def verify(G):
    cfg=contract(G)
    with BC.Store() as store:q=store.read('tr_qualification.json')
    if (not q['accepted'] or q['binding']!=G.safety_binding() or q['contract_sha256']!=G.digest(G.SOURCE.parent/'inputs/terminal_contract.json') or
        q['checker_sha256']!=G.digest(G.SOURCE/'terminal_oracle.py') or {r['case_id'] for r in q['results']}!={j['case_id'] for j in cfg['jobs']} or
        len(q['results'])!=40):raise G.AdmissionBlocked('TR_QUALIFICATION')
    jobs={j['case_id']:j for j in cfg['jobs']}
    for row in q['results']:
        if not row['accepted'] or row['status']!=('MUTATION_DETECTED' if jobs[row['case_id']]['mutant'] else 'PASS'):raise G.AdmissionBlocked('TR_REQUIRED_RESULT')
