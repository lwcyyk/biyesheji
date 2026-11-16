"""Prepare batch06 request data only. No batch06 directory or runtime is created."""
from pathlib import Path
import json

W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\ri01')


def dump(name,x):
    (W/'inputs'/name).write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')


jobs=[]
def add(case,kind,scenario,variant='safe',mutant=None,violation=None,expected=None):
    if expected is None:expected='ADMITTED' if scenario in ('read','replace','repeat','umask','ready','receipt_read') else 'BLOCKED'
    jobs.append({'case_id':case,'kind':kind,'scenario':scenario,'variant':variant,'mutant':mutant,
                 'expected_violation':violation,'expected_subject':expected,
                 'allowed_violation_set':({'root600':['IPC-1','IPC-3'],'ignore_permissions':['IPC-1','IPC-3'],
                    'ignore_closed':['IPC-7','IPC-8']}.get(mutant,[violation]) if mutant else []),
                 'initial':'fresh synthetic object/namespace; live global ledger excluded from faults',
                 'raw_limit_bytes':131072,'driver_charge_bound':8,'independent_audit_charges':1,
                 'charge_rule':'Prepay8 fixture semantic steps plus immediate oracle; burn unused'})
for s in ['read','replace','unauthorized','private_write','private_read','receipt_read','receipt_write','historical','bad_metadata',
          'outside','symlink','hardlink','fault_after_create','fault_file_fsync','fault_rename',
          'fault_directory_fsync','bad_batch','bad_boot','bad_lock','bad_digest','umask','repeat']:
    add('P.'+s,'file',s)
for s in ['ready','stop_before','stop_after_ready','closed_wait','closed','ack_stop','repeat_stop',
          'payload_dead','receiver_dead','read_error','stale','late_ack','timeout','exception','deadline',
          'fd_cancel','socket_cancel','socket_eof']:
    add('T.'+s,'wait',s)
for label,kind,scenario,mutant,violation,safe_expected in [
    ('root600','file','read','root600','IPC-1','ADMITTED'),
    ('permissions','file','bad_metadata','ignore_permissions','IPC-1','BLOCKED'),
    ('stop','wait','stop_before','ignore_stop','IPC-7','BLOCKED'),
    ('closed','wait','closed','ignore_closed','IPC-8','BLOCKED'),
    ('exit23','semantic','exit_only','exit23','IPC-6','PENDING'),
    ('reactivate','semantic','reactivate','reactivate','IPC-8','CLOSED'),
    ('batch','file','bad_batch','ignore_batch','IPC-5','BLOCKED'),
    ('duplicate','semantic','duplicate','duplicate','IPC-9','VERIFIED')]:
    add('M.'+label+'.safe',kind,scenario,expected=safe_expected)
    add('M.'+label+'.mutant',kind,scenario,'mutant',mutant,violation,None)
assert len(jobs)==56
dump('root_ipc_contract.json',{
    'schema':'ROOT-IPC-CONTRACT/1','version':'RootIPC-static-1','future_batch_id':'batch06',
    'profile':'ROOT-IPC/1','jobs':jobs,'max_jobs':56,'expected_safe':48,'expected_mutants':8,
    'hard_visits':512,'completed_visit_upper_bound':9*len(jobs)+1,
    'charging_context':'Root C09H ticket; original C09H and IPC combined ceiling5000',
    'combined_C09H_completed_upper_bound':2245+9*len(jobs)+1,
    'combined_C09H_hard_visits':5000,'full_calibration_hard_visits':62034,
    'calibration_window_seconds':300,'total_visits':1000000,'total_seconds':1800,
    'probe_child':{'uid_options':[999,65534],'gid_options':[989,65534],'max_live':1,
                   'rlimit_as':1073741824,'alarm_seconds':2,'parent_wait_seconds':3,
                   'cleanup_seconds':3,'location':'external trusted Root test infrastructure'},
    'helper_authorization_required':True,'dynamic_status':'UNRUN',
    'limits_note':'Window and fsync latency measured only by future dynamic run; no real-time bound claimed'})
for name in ['c09_contract.json','safety_contract.json']:
    p=W/'inputs'/name;x=json.loads(p.read_text('utf-8-sig'))
    # Namespace binding changes only. Frozen events/N/assertions and all17 negatives stay exact.
    x['future_batch_id']='batch06'
    for job in x['jobs']:
        if 'batch_id' in job:job['batch_id']='batch06'
    dump(name,x)
old=W/'inputs/dclr6batch05.slice';new=W/'inputs/dclr6batch06.slice'
if old.exists():old.rename(new)
new.write_text(new.read_text(encoding='utf-8').replace('batch05','batch06'),encoding='utf-8')
print(json.dumps({'jobs':len(jobs),'completed_visits':9*len(jobs)+1,'combined_completed':2245+9*len(jobs)+1,
                  'hard_C09H_combined':5000,'full_calibration_hard':62034,'batch06_created':False}))
