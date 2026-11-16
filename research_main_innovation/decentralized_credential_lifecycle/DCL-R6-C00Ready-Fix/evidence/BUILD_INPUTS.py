"""Construct frozen readiness fixtures/namespace metadata on host; no behavior execution."""
from pathlib import Path
import json
W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\cr01')
def dump(name,x):(W/'inputs'/name).write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
jobs=[]
def add(case,frames,expected='FAILED',mutant=None,violation=None,allowed=None):
    assert len(frames)<=5
    jobs.append({'case_id':case,'frames':frames,'variant':'mutant' if mutant else 'safe','mutant':mutant,
      'expected':expected,'expected_violation':violation,'allowed_violations':allowed or [],
      'initial':'fixed simulated unit/process snapshot with valid lock/boot and eight expected fields',
      'source':'FROZEN_SIMULATED_STATE/1; never accepted by native collector or lease mint',
      'raw':['actual frame facts','subject shadow','all8 expected/observed values','decision sequence','real run binding/actor/stamp','shared visits'],
      'native_status':'UNRUN; simulation is separate from actual C00 NATIVE_OS/1 qualification'})
base=[('immediate',['ready'],'READY'),('starting',['starting','ready'],'READY'),
 ('pid_pending',['pid0','pid_assigned','ready'],'READY'),('transition',['transition','ready'],'READY'),
 ('field_order',['cg_pending','starting','ready'],'READY'),('stable_lock',['ready'],'READY'),
 ('uid',['uid_wrong'],'FAILED'),('gid',['gid_wrong'],'FAILED'),('groups',['groups_wrong'],'FAILED'),
 ('caps',['caps_wrong'],'FAILED'),('nnp',['nnp_wrong'],'FAILED'),('as_hard',['as_hard_wrong'],'FAILED'),
 ('as_soft',['as_soft_wrong'],'FAILED'),('cgroup',['cg_wrong'],'FAILED'),('unit',['wrong_unit'],'FAILED'),
 ('type',['wrong_type'],'FAILED'),('tasks',['tasks_wrong'],'FAILED'),('proc_as',['proc_as_wrong'],'FAILED'),
 ('proc_cgroup',['proc_cg_wrong'],'FAILED'),('boot',['starting','boot_wrong'],'FAILED'),
 ('pid_reuse',['pid_reused'],'FAILED'),('read_error',['read_error'],'FAILED'),('missing_field',['field_missing'],'FAILED'),
 ('snapshot',['cross_version'],'FAILED'),('exit',['starting','target_exit'],'FAILED'),('service_failed',['service_failed'],'FAILED'),
 ('timeout',['starting','timeout'],'FAILED'),('stop',['starting','stop'],'FAILED'),('closed',['starting','closed'],'FAILED'),
 ('lock',['missing_lock'],'FAILED')]
for name,frames,outcome in base:add('P.'+name,frames,outcome)
fields=['uid_wrong','gid_wrong','groups_wrong','caps_wrong','nnp_wrong','as_hard_wrong','as_soft_wrong','cg_wrong']
for i,f in enumerate(fields,1):
    cid='CR-%02d'%i;add('M.'+cid+'.safe',[f]);add('M.'+cid+'.mutant',[f],mutant='ignore_'+cid,violation=cid,allowed=[cid])
extra=[
 ('read',['read_error'],'read_error_match','CR-READ_ERROR',['CR-%02d'%i for i in range(1,9)]+['CR-READ_ERROR']),
 ('stale',['starting','uid_wrong','timeout'],'reuse_snapshot','CR-STALE',['CR-STALE','CR-WAIT-MISMATCH','CR-TIMEOUT']),
 ('partial',['gid_wrong'],'only_uid','CR-02',['CR-02']),
 ('pid',['pid_reused'],'wrong_pid','CR-PID',['CR-PID','CR-READ_ERROR']),
 ('boot',['boot_wrong'],'other_boot','CR-BOOT',['CR-BOOT']),
 ('stable',['uid_wrong','ready'],'stable_as_starting','CR-WAIT-MISMATCH',['CR-STALE','CR-WAIT-MISMATCH','CR-REACTIVATION']),
 ('timeout',['starting','timeout'],'timeout_extend','CR-TIMEOUT',['CR-STALE','CR-TIMEOUT']),
 ('lock',['missing_lock'],'missing_lock','CR-LOCK',['CR-LOCK']),
 ('version',['cross_version'],'cross_version','CR-SNAPSHOT',['CR-SNAPSHOT'])]
for name,frames,mutation,prop,allowed in extra:
    add('M.'+name+'.safe',frames);add('M.'+name+'.mutant',frames,mutant=mutation,violation=prop,allowed=allowed)
assert len(jobs)==64 and sum(j['variant']=='mutant' for j in jobs)==17
dump('readiness_contract.json',{'schema':'C00-READY-CONTRACT/1','version':'C00Ready-static-1','freeze_revision':'r2',
 'profile':'C00-READY/1','future_batch_id':'batch08','readiness_seconds':14,'poll_seconds':0.05,'sample_cap':300,
 'diagnostic_row_bytes':131072,'read_sources_bytes':65536,'cases':['C00','C10'],
 'source_readiness':'Type=exec active/running; no application READY/ticket cycle',
 '8_fields':['Uid','Gid','Groups','CapEff','NoNewPrivs','LimitAS','LimitASSoft','ControlGroup'],
 'jobs':jobs,'max_jobs':64,'driver_prepay':6,'regression_hard_visits':512,'regression_completed_visits':449,
 'global_calibration_hard_bound':62546,'global_calibration_soft':100000,'calibration_seconds':300,'total_visits':1000000,'total_seconds':1800,
 'diagnostic_mode':'C00_DIAGNOSTIC_ONLY stops after actual C00 and64 synthetic results; no RESOURCE_GATE_PASS',
 'full_mode':'CALIBRATE_S1S9_THEN_F1_F4 requires Full_conditional_chain_explicitly_approved',
 'sample_consistency':'two manager bookends + two proc reads + PID/start/boot/pidfd + cgroup inode; conditional on no privileged ABA/concurrent reconfiguration',
 'actual_status':'UNRUN'})
for name in ['c09_contract.json','root_ipc_contract.json','boot_contract.json','safety_contract.json']:
    p=W/'inputs'/name;x=json.loads(p.read_text(encoding='utf-8-sig'));x['future_batch_id']='batch08'
    for j in x['jobs']:
        if 'batch_id'in j:j['batch_id']='batch08'
    dump(name,x)
old=W/'inputs/dclr6batch07.slice';new=W/'inputs/dclr6batch08.slice'
if old.exists():old.rename(new)
new.write_text(new.read_text(encoding='utf-8').replace('batch07','batch08'),encoding='utf-8')
print(json.dumps({'jobs':64,'mutants':17,'completed_visits':449,'new_static_calibration_hard':62546,'old_calibration_hard':62034,'unchanged_soft_limit':100000,'native_calls':0}))
