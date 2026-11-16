"""Review-only native A test entry. No standalone role or import-time actions.

Integration and dynamic receipt remain unissued. The same A batch is CLOSED.
Normal MR classifier, RootIPC policy and C09 protocol remain unmodified.
"""
import hashlib,json,os,resource,sys,time
from pathlib import Path

def command(G):
    old=G.service_argv('C10');cut=old.index(G.PYTHON)
    unit=G.NAMESPACE['service_prefix']+'mr-native-fault.service'
    argv=[('--unit='+unit if x.startswith('--unit=') else x) for x in old[:cut]]
    return argv+[G.PYTHON,'-I','-S','-B',str(G.SOURCE/'mr_native_entry.py'),'--worker','--batch-root',str(G.ROOT)]

def run(G,contract):
    import manager_recovery as M
    import boot_continuity as BC
    a,_=G.authorization()
    if (a['scope']!='MR_RECOVERY_DIAGNOSTIC_ONLY' or a.get('MR_native_fault_explicitly_approved') is not True or
        a.get('mr_native_contract_sha256')!=hashlib.sha256(json.dumps(contract,sort_keys=True,separators=(',',':')).encode()).hexdigest() or
        contract.get('runtime_enabled') is not True or contract.get('source_revision')!=G.NAMESPACE['revision']):
        raise G.AdmissionBlocked('MR_NATIVE_EXECUTION_UNAPPROVED')
    if contract['fault_exit']!=79 or contract['scheduler_exit']!=78 or contract['prepaid_visits']!=512:raise G.AdmissionBlocked('MR_NATIVE_CONTRACT')
    if Path(__file__).resolve().parent!=G.SOURCE or G.stopped():raise G.AdmissionBlocked('MR_NATIVE_CONTEXT')
    G.root_checkpoint();cfg=M.contract(G);unit=G.NAMESPACE['service_prefix']+'mr-native-fault.service'
    if unit in cfg['historical_closed_units']:raise G.AdmissionBlocked('MR_NATIVE_FAULT_UNIT_PREAPPROVED')
    expected=command(G)
    if expected!=contract['unit_argv']:raise G.AdmissionBlocked('MR_NATIVE_ARGV')
    if G.trusted(G.ROOT/'inputs/result_C10.json')['status']!='PASS':raise G.AdmissionBlocked('MR_NATIVE_C10')
    old_ticket=G._TICKET;G._TICKET=G.ticket('C10')
    try:
        for _ in range(512):G.execution_deadline('C10');G.reserve_counter(G.OUT/'visits.bin',G.VISIT_CAP)
        before=G.count();until=min(G.now()+5,G.state()['T0']+300,G.state()['stop_at'])
        failed_before=M.failed_set(G,until)
        if unit in failed_before:raise G.AdmissionBlocked('MR_NATIVE_UNIT_EXISTS')
        # Query errors or missed live identity cause a frozen abort, never a retry.
        G._run(expected,timeout=max(.001,min(2,until-G.now())))
        start=None;finish=None
        for _ in range(64):
            G.root_checkpoint()
            if G.now()>=until:break
            v=M.show(G,unit,until)['values']
            if v['ActiveState']=='active' and int(v['MainPID'])>0:
                if start is None:start={'native':v,'identity':G.identity(int(v['MainPID'])),'sample':G.stamp()}
            if v['ActiveState']=='failed':finish={'native':v,'sample':G.stamp()};break
            time.sleep(.025)
        if start is None or finish is None:raise G.AdmissionBlocked('MR_NATIVE_EVENT_MISSING')
        f=finish['native'];s=start['native']
        if (f['Id']!=unit or f['InvocationID']!=s['InvocationID'] or f['Result']!='exit-code' or
            f['ExecMainStatus']!='79' or f['ExecMainCode']!='1' or int(f['ExecMainPID'])!=start['identity']['pid'] or
            int(f['ExecMainExitTimestampMonotonic'])<=0):raise G.AdmissionBlocked('MR_NATIVE_EVENT_IDENTITY')
        failed_after=M.failed_set(G,until)
        if set(failed_after)!=set(failed_before)|{unit}:raise G.AdmissionBlocked('MR_NATIVE_FAILED_SET_RACE')
        try:M.historical(G,unit,cfg,until)
        except G.AdmissionBlocked as ex:
            if str(ex)!='MR_UNREVIEWED_MANAGER_FAILURE:'+unit:raise
            rejection=str(ex)
        else:raise G.AdmissionBlocked('MR_NATIVE_UNREVIEWED_ACCEPTED')
        journal=M.query(G,['/usr/bin/journalctl','--boot','--no-pager','--all','--output=json',
            '--output-fields=MESSAGE,_BOOT_ID,_SYSTEMD_UNIT,_SYSTEMD_INVOCATION_ID,__MONOTONIC_TIMESTAMP','--unit='+unit],until)
        if G.count()!=before:raise G.AdmissionBlocked('MR_NATIVE_POST_PREPAY_BUDGET_CHANGED')
        with BC.Store() as store:
            store.put('mr_native_case.json',{'origin':'NATIVE_RECORDED_EVENT','binding':G.safety_binding(),'unit':unit,'start':start,'finish':finish,
                'failed_before':failed_before,'failed_after':failed_after,'journal':journal,'rejection':rejection,
                'prepaid':512,'counter_after_prepaid':before,'window':{k:G.state()[k] for k in ['T0','deadline','stop_at']},'sample':G.stamp()},exclusive=True)
            store.put('mr_diag_injection.json',{'binding':G.safety_binding(),'case':'C10',
                'C10_sha256':G.digest(G.ROOT/'inputs/result_C10.json'),'expected_exit':78,'sample':G.stamp()},exclusive=True)
        return M.fail(G,'MR_EXPECTED_DIAGNOSTIC_FAILURE',78,True)
    finally:G._TICKET=old_ticket

def worker():
    # Future worker: exact dedicated service sandbox; no account/credential use.
    import batch_identity as N
    cfg=N.load(Path(__file__).resolve().parent.parent)
    if (sys.platform!='linux' or os.geteuid()!=999 or os.getegid()!=989 or
        resource.getrlimit(resource.RLIMIT_AS)!=(1073741824,1073741824) or
        sys.argv!=[str(Path(__file__).resolve()),'--worker','--batch-root',cfg['runtime_root']]):raise RuntimeError('MR_NATIVE_WORKER_CONTEXT')
    path=next(s[3:] for s in Path('/proc/self/cgroup').read_text().splitlines() if s.startswith('0::'))
    unit=cfg['service_prefix']+'mr-native-fault.service'
    if not path.endswith('/'+cfg['slice']+'/'+unit):raise RuntimeError('MR_NATIVE_WORKER_CGROUP')
    print(json.dumps({'event':'MR_NATIVE_FAULT_READY','batch_id':cfg['batch_id'],
        'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'pid':os.getpid(),'exit':79}),flush=True)
    time.sleep(1)
    os._exit(79)

if __name__=='__main__':
    if '--worker' not in sys.argv:raise SystemExit('REVIEW_COMPONENT_NO_ACTIVE_ENTRY')
    worker()
