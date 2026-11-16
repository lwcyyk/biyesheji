"""RA32 fixed observations, billed inside the original active C00 window."""
import copy,hashlib,os
import boot_continuity as BC
import runtime_identity as I
import runtime_oracle as O
import json
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def contract(G):
    a,m=G.authorization();p=G.SOURCE.parent/'inputs/runtime_regression_contract.json';cfg=G.trusted(p)
    if (cfg['version']!='RuntimeAdapt-static-1/r1' or cfg['batch_id']!=G.ROOT.name or len(cfg['jobs'])!=32 or len({j['case_id'] for j in cfg['jobs']})!=32 or
        G.digest(p)!=m['runtime_regression_contract_sha256'] or a.get('runtime_regression_contract_sha256')!=G.digest(p) or cfg['driver_prepay']!=16 or cfg['hard_visits']!=768):raise G.AdmissionBlocked('RA_REGRESSION_BINDING')
    return cfg
def subject(frame,mutant):
    f=copy.deepcopy(frame);before=copy.deepcopy(f);out=I.policy(f)
    if mutant in ('missing_digest_pass','alias_change_pass','package_change_pass','build_id_pass','loader_override_pass','stale_mapping_pass','cross_batch_pass','silent_relock_pass'):out='IDENTITY_MATCH'
    return {'actual_input':before,'decision':out,'origin':'RA-SIMULATION/1','system_files_modified':False,'runtime_lock_modified':False}
def run_suite(G):
    if os.geteuid()!=0:raise G.AdmissionBlocked('RA_ROOT_SUITE')
    cfg=contract(G);old=G._TICKET;G._TICKET=G.ticket('C00');base=G.count();binding=G.safety_binding()
    def charge():
        if G.count()-base>=cfg['hard_visits']:raise G.LimitReached('RA_VISIT_CAP')
        G.execution_deadline('C00');G.reserve_counter(G.OUT/'visits.bin',G.VISIT_CAP)
    try:
        charge()
        with BC.Store() as store:
            for i,job in enumerate(cfg['jobs']):
                before=G.count()
                for _ in range(cfg['driver_prepay']):charge()
                store.put('ra_case_%03d.json'%i,{'origin':'RA-SIMULATION/1','case_id':job['case_id'],'binding':binding,'input_sha256':hashlib.sha256(canonical(job)).hexdigest(),
                    'trace':[subject(f,job['mutant']) for f in job['frames']],'before':before,'after':G.count(),'sample':G.stamp()},exclusive=True)
                q=O.check_job(G.ROOT/'inputs/root_private/boot',job,i,binding)
                if not q['accepted']:raise G.AdmissionBlocked('RA_FIRST_TEST_FAILURE:'+job['case_id']+':'+q['status'])
            for job in cfg['jobs']:charge()
            q=O.check_suite(G.ROOT/'inputs/root_private/boot',cfg,binding)
            if not q['accepted']:raise G.AdmissionBlocked('RA_SUITE_FAILED')
            q.update(contract_sha256=G.digest(G.SOURCE.parent/'inputs/runtime_regression_contract.json'),checker_sha256=G.digest(G.SOURCE/'runtime_oracle.py'),before=base,after=G.count(),sample=G.stamp())
            store.put('ra_qualification.json',q,exclusive=True);return q
    finally:G._TICKET=old
def verify(G):
    cfg=contract(G)
    with BC.Store() as store:q=store.read('ra_qualification.json')
    if not q['accepted'] or q['binding']!=G.safety_binding() or q['contract_sha256']!=G.digest(G.SOURCE.parent/'inputs/runtime_regression_contract.json') or q['checker_sha256']!=G.digest(G.SOURCE/'runtime_oracle.py') or len(q['results'])!=32:raise G.AdmissionBlocked('RA_QUALIFICATION')
    jobs={j['case_id']:j for j in cfg['jobs']}
    if {r['case_id'] for r in q['results']}!=set(jobs):raise G.AdmissionBlocked('RA_JOB_SET')
    for r in q['results']:
        if not r['accepted'] or r['status']!=('MUTATION_DETECTED' if jobs[r['case_id']]['mutant'] else 'PASS'):raise G.AdmissionBlocked('RA_REQUIRED_RESULT')
