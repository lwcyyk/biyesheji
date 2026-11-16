"""Readiness policy simulations; production native collector accepts no fixture backend."""
import copy
import hashlib
import service_readiness as R
import boot_continuity as BC


def frame(name,sequence):
    target={'pid':101,'start_ticks':10,'boot_id':'SIM-BOOT-A'}
    d={'schema':'READINESS-SIM/1','expected_boot':'SIM-BOOT-A','boot_before':'SIM-BOOT-A','boot_after':'SIM-BOOT-A',
       'stopped':False,'error':None,'binding_valid':True,'hard_aux_valid':True,'coherent':True,'expired':False,
       'phases':['READY','READY'],'process_identity':target,'identity_before':target,'identity_after':dict(target),
       'status_version_before':'inv1/version1','status_version_after':'inv1/version1','T0':10,'deadline':1810,
       'ready_until':24,'now':10+sequence,'checks':[],'frame_name':name}
    values=[[999],[989],[989],0,1,'1073741824','1073741824','/dclr6batch11.slice/dclr6batch11-c00.service']
    expected=copy.deepcopy(values)
    bad={'uid_wrong':0,'gid_wrong':1,'groups_wrong':2,'caps_wrong':3,'nnp_wrong':4,'as_hard_wrong':5,'as_soft_wrong':6,'cg_wrong':7}
    if name in bad:
        i=bad[name];values[i]=[0] if i<3 else 1 if i==3 else 0 if i==4 else '536870912' if i<7 else '/wrong.service'
    starting=name in ('starting','pid0','pid_assigned','cg_pending','transition','timeout')
    if starting:
        d['phases']=['STARTING','READY'] if name=='transition' else ['STARTING','STARTING']
        d['coherent']=name!='transition'
        if name=='pid0':d['process_identity']=None
        if name=='cg_pending':values[7]=''
    if name in ('wrong_unit','wrong_type','tasks_wrong','proc_as_wrong','proc_cg_wrong'):d['hard_aux_valid']=False
    if name=='pid_reused':d['error']={'type':'ProcessLookupError'};d['identity_after']={'pid':102,'start_ticks':11,'boot_id':'SIM-BOOT-A'}
    if name=='target_exit':d['error']={'type':'ProcessLookupError','errno':3}
    if name=='read_error':d['error']={'type':'OSError','errno':5}
    if name=='field_missing':d['error']={'type':'KeyError','field':'NoNewPrivs'}
    if name=='cross_version':d['coherent']=False;d['status_version_after']='inv1/version2'
    if name=='boot_wrong':d['boot_after']='SIM-BOOT-B'
    if name in ('stop','closed'):d['stopped']=True
    if name=='missing_lock':d['binding_valid']=False
    if name=='service_failed':d['phases']=['FAILED','FAILED']
    if name=='timeout':d['expired']=True;d['now']=24
    for i,cid in enumerate(R.IDS):
        observed=[copy.deepcopy(values[i]),copy.deepcopy(values[i])]
        result='MATCH' if values[i]==expected[i] else 'MISMATCH';error=None
        if starting and (i<5 or (i==7 and name=='cg_pending')):observed=None;result='NOT_READY'
        if name=='read_error' or (name=='field_missing' and i==4):observed=None;result='READ_ERROR';error=d['error']
        d['checks'].append({'check_id':cid,'expected':expected[i],'observed':observed,'result':result,
          'read_success':observed is not None,'error':error,'evidence_source':'FROZEN_SIMULATED_STATE/1'})
    return d


class Subject:
    def __init__(self,mutation):self.mutation=mutation;self.terminal=False;self.cached=None
    def sample(self,facts):
        if self.terminal:return {'decision':'FAILED','shadow':None}
        shadow=copy.deepcopy(facts);m=self.mutation
        if self.cached is None:self.cached=copy.deepcopy(facts)
        if m and m.startswith('ignore_CR-'):
            for c in shadow['checks']:
                if c['check_id']==m[len('ignore_'):]:c['result']='MATCH'
        elif m=='read_error_match':
            shadow['error']=None
            for c in shadow['checks']:c['result']='MATCH'
        elif m=='reuse_snapshot':shadow=copy.deepcopy(self.cached)
        elif m=='only_uid':shadow['checks']=shadow['checks'][:1]
        elif m=='wrong_pid':shadow['error']=None;shadow['coherent']=True
        elif m=='other_boot':shadow['boot_before']=shadow['expected_boot'];shadow['boot_after']=shadow['expected_boot']
        elif m=='stable_as_starting' and any(c['result']=='MISMATCH' for c in shadow['checks']):
            shadow['phases']=['STARTING','STARTING']
            for c in shadow['checks']:c['result']='NOT_READY'
        elif m=='timeout_extend':shadow['expired']=False
        elif m=='missing_lock':shadow['binding_valid']=True
        elif m=='cross_version':shadow['coherent']=True
        decision=R.policy(shadow)
        if decision=='FAILED':self.terminal=True
        return {'decision':decision,'shadow':shadow}


def run_suite(G):
    import readiness_oracle as O
    cfg,a=R.contract(G);old=G._TICKET;G._TICKET=G.ticket('C00');base=G.count();binding=G.safety_binding()
    def charge():
        G.execution_deadline('C00')
        if G.count()-base>=cfg['regression_hard_visits']:raise G.LimitReached('READY_REGRESSION_VISIT_CAP')
        G.reserve_counter(G.OUT/'visits.bin',G.VISIT_CAP)
    try:
        charge()
        with BC.Store() as store:
            for index,job in enumerate(cfg['jobs']):
                G.root_checkpoint();before=G.count()
                for _ in range(cfg['driver_prepay']):charge()
                subject=Subject(job['mutant']);trace=[]
                for i,event in enumerate(job['frames']):
                    facts=frame(event,i);response=subject.sample(facts)
                    trace.append({'event':event,'facts':facts,'response':response})
                row={'schema':'READY-SIM-RAW/1','origin':'SIMULATION_ONLY/1','case_id':job['case_id'],
                     'input_sha256':hashlib.sha256(BC.canon(job)).hexdigest(),'binding':binding,'actor':G.identity(),
                     'stamp':G.stamp(),'global_before':before,'global_after':G.count(),'trace':trace}
                store.put('ready_case_%03d.json'%index,row,exclusive=True)
                immediate=O.check_job(G.ROOT/'inputs/root_private/boot',job,index,binding)
                if not immediate['accepted']:raise G.AdmissionBlocked('READY_REGRESSION_FIRST_FAILURE:'+job['case_id'])
            for job in cfg['jobs']:charge()
            report=O.check_suite(G.ROOT/'inputs/root_private/boot',cfg,binding)
            if not report['accepted']:raise G.AdmissionBlocked('READY_REGRESSION_ORACLE')
            report.update(contract_sha256=G.digest(G.SOURCE.parent/'inputs/readiness_contract.json'),
                          checker_sha256=G.digest(G.SOURCE/'readiness_oracle.py'),sample=G.stamp(),
                          global_before=base,global_after=G.count(),scope=a['scope'])
            store.put('C00_READY_QUALIFICATION.json',report,public=True)
            return report
    finally:G._TICKET=old
