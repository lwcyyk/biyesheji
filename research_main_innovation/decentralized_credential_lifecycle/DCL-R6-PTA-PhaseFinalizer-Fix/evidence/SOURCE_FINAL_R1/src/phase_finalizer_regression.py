"""PF-SIMULATION/1, same billed window after PT64; no actual OS fault injection."""
import copy
import hashlib
import os
import boot_continuity as BC
import startup_lifecycle as P
import phase_finalizer_oracle as O

def contract(G):
    a,m=G.authorization();path=G.SOURCE.parent/'inputs/phase_finalizer_contract.json';cfg=G.trusted(path)
    if (cfg['version']!='PTA-PhaseFinalizer-static-1/r1' or cfg['batch_id']!=G.ROOT.name or
        G.digest(path)!=m['phase_finalizer_contract_sha256'] or a.get('phase_finalizer_contract_sha256')!=G.digest(path) or
        len(cfg['jobs'])!=48 or len({j['case_id'] for j in cfg['jobs']})!=48 or
        cfg['driver_prepay']!=16 or cfg['hard_visits']!=1152 or any(len(j['frames'])>4 for j in cfg['jobs'])):
        raise G.AdmissionBlocked('PF_CONTRACT_BINDING')
    return cfg

def subject_step(frame,mutant):
    actual=copy.deepcopy(frame);facts=copy.deepcopy(frame['facts']);domain=frame['domain']
    if mutant=='reactivate_closed':facts['closed']=False;facts['stop']=False
    if domain=='phase':
        decision=P.phase_snapshot_policy(facts)
        if mutant in ('allow_illegal_phase','skip_work','stale_snapshot','ignore_version'):decision='ACCEPT'
        shutdown=decision.startswith('DENY_') and frame['critical']
        if mutant=='no_auto_stop':shutdown=False
        observed={'decision':decision,'work_granted':decision=='ACCEPT' and facts['work'],'automatic_stop':shutdown}
    elif domain=='admin':
        observed=P.administrative_policy(facts)
        if mutant=='swallow_import_error':observed['error_recorded']=False;observed['administrative_export_status']='EXPORT_ALLOWED'
        if mutant=='overwrite_native':observed['native_seal_status']='NATIVE_SEAL_FAILED'
    else:
        # This fixture describes a close-result observation, never calls real shutdown.
        observed={'automatic_stop':facts['critical'],'cleanup':'CLEANUP_CONFIRMED' if facts['roles_empty'] and facts['group_absent'] and not facts['audit_error'] else 'CLEANUP_UNKNOWN',
            'internal':facts['internal_status'],'native':facts['native_status'],'admin':facts['admin_status']}
    return {'actual_input':actual,'observed':observed,'origin':'PF-SIMULATION/1'}

def run_suite(G):
    if os.geteuid()!=0:raise G.AdmissionBlocked('PF_ROOT_REQUIRED')
    cfg=contract(G);old=G._TICKET;G._TICKET=G.ticket('C00');base=G.count();binding=G.safety_binding()
    def charge():
        if G.count()-base>=cfg['hard_visits']:raise G.LimitReached('PF_REGRESSION_CAP')
        G.execution_deadline('C00');G.reserve_counter(G.OUT/'visits.bin',G.VISIT_CAP)
    try:
        charge()
        with BC.Store() as store:
            for i,job in enumerate(cfg['jobs']):
                before=G.count()
                for _ in range(cfg['driver_prepay']):charge()
                trace=[subject_step(f,job['mutant']) for f in job['frames']]
                store.put('pf_case_%03d.json'%i,{'schema':'PF-RAW/1','origin':'PF-SIMULATION/1','case_id':job['case_id'],
                    'binding':binding,'input_sha256':hashlib.sha256(P.canonical(job)).hexdigest(),'trace':trace,
                    'before':before,'after':G.count(),'sample':G.stamp()},exclusive=True)
                result=O.check_job(G.ROOT/'inputs/root_private/boot',job,i,binding)
                if not result['accepted']:raise G.AdmissionBlocked('PF_FIRST_TEST_FAILURE:'+job['case_id']+':'+result['status'])
            for job in cfg['jobs']:charge()
            result=O.check_suite(G.ROOT/'inputs/root_private/boot',cfg,binding)
            if not result['accepted']:raise G.AdmissionBlocked('PF_SUITE_FAILED')
            result.update(contract_sha256=G.digest(G.SOURCE.parent/'inputs/phase_finalizer_contract.json'),
                checker_sha256=G.digest(G.SOURCE/'phase_finalizer_oracle.py'),before=base,after=G.count(),sample=G.stamp())
            store.put('pf_qualification.json',result,exclusive=True)
            return result
    finally:G._TICKET=old

def verify(G):
    cfg=contract(G)
    with BC.Store() as store:q=store.read('pf_qualification.json')
    if (not q['accepted'] or q['binding']!=G.safety_binding() or q['contract_sha256']!=G.digest(G.SOURCE.parent/'inputs/phase_finalizer_contract.json') or
        q['checker_sha256']!=G.digest(G.SOURCE/'phase_finalizer_oracle.py') or len(q['results'])!=len(cfg['jobs'])):raise G.AdmissionBlocked('PF_QUALIFICATION')
    jobs={j['case_id']:j for j in cfg['jobs']}
    if {r['case_id'] for r in q['results']}!=set(jobs):raise G.AdmissionBlocked('PF_JOB_SET')
    for row in q['results']:
        if not row['accepted'] or row['status']!=('MUTATION_DETECTED' if jobs[row['case_id']]['mutant'] else 'PASS'):raise G.AdmissionBlocked('PF_REQUIRED_RESULT')
