"""Host-only input construction. No target import, WSL command or batch07 directory."""
from pathlib import Path
import json

W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\bc01')
def dump(name,x):(W/'inputs'/name).write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
jobs=[]
def add(name,events,last,activations,mutant=None,violation=None,allowed=None):
    assert len(events)<=10
    jobs.append({'case_id':name,'events':events,'variant':'mutant' if mutant else 'safe','mutant':mutant,
      'expected_last':last,'expected_activations':activations,'expected_violation':violation,
      'allowed_violations':allowed or [],'initial':'fresh simulated kernel epoch1; persistent ledger empty',
      'state_source':'SIMULATED_RESTART/1: epoch transition kills process and invalidates fd/manager state; persistent artifacts remain',
      'evidence':['frozen input','event order','actual simulator facts','subject observation','decision','activation count','budget before/after'],
      'native_scope':'No physical WSL shutdown; real entry/exec/service confirmation remains separate dynamic evidence'})
start=['inspect','prepare','final','issue']
scenarios=[
 ('same_boot',start+['exec','initialize_window','service_active'],'STARTED',1),
 ('cache_refresh',['static_cache','reboot','new_process']+start+['exec','initialize_window','service_active'],'STARTED',1),
 ('after_first',['inspect','reboot','new_process','prepare','final','issue','exec'],'REJECTED',0),
 ('during_prepare',['inspect','prepare','reboot','new_process','final','issue','exec'],'REJECTED',0),
 ('after_final',['inspect','prepare','final','reboot','new_process','issue','exec'],'REJECTED',0),
 ('during_exec',start+['reboot','new_process','exec'],'REJECTED',0),
 ('old_receipt',start+['reboot','recycle_owner','reload_old_cap','exec'],'REJECTED',0),
 ('duplicate',start+['exec','exec'],'REJECTED',1),
 ('request_only',start+['exec','request_ok','confirm'],'REJECTED',1),
 ('launcher_exit',start+['exec','launcher_exit','confirm'],'REJECTED',1),
 ('orchestrator_exit',start+['orchestrator_exit','exec'],'REJECTED',0),
 ('stop',['inspect','prepare','stop','final','issue','exec'],'REJECTED',0),
 ('bad_batch',start+['bad_batch','exec'],'REJECTED',0),
 ('bad_lock',start+['bad_lock','exec'],'REJECTED',0),
 ('closed',['prior_closed']+start+['exec'],'REJECTED',0),
 ('resources',start+['resources_change','exec'],'REJECTED',0),
 ('identity',start+['identity_change','exec'],'REJECTED',0),
 ('cache_invalid',['static_cache','cache_rule_change']+start+['exec','initialize_window','service_active'],'STARTED',1),
 ('artifact_drift',['static_cache','artifact_drift']+start+['exec'],'REJECTED',0),
 ('old_window',['prior_window','reboot','new_process']+start+['exec'],'REJECTED',0)]
for name,events,last,count in scenarios:add('P.'+name,events,last,count)
lookup={name:(events,last,count) for name,events,last,count in scenarios}
mutants=[
 ('epoch','old_receipt','ignore_epoch','BC-1',['BC-1','BC-3']),
 ('snapshot','during_exec','cached_snapshot','BC-3',['BC-1','BC-3','BC-8']),
 ('duplicate','duplicate','ignore_once','BC-4',['BC-4']),
 ('request','request_only','request_is_start','BC-7',['BC-7']),
 ('closed','closed','ignore_closed','BC-5',['BC-3','BC-5']),
 ('budget','old_window','reset_budget','BC-6',['BC-6']),
 ('binding','bad_lock','ignore_binding','BC-3',['BC-3']),
 ('resources','resources','ignore_resources','BC-2',['BC-2','BC-5']),
 ('identity','identity','ignore_identity','BC-8',['BC-8']),
 ('cache','artifact_drift','ignore_static','BC-2',['BC-2','BC-3','BC-5'])]
for label,scenario,mutation,prop,allowed in mutants:
    events,last,count=lookup[scenario]
    add('M.'+label+'.safe',events,last,count)
    add('M.'+label+'.mutant',events,last,count,mutation,prop,allowed)
assert len(jobs)==40
dump('boot_contract.json',{'schema':'BC-CONTRACT/1','version':'BootContinuity-static-1','freeze_revision':'r4',
 'profile':'BC-SINGLE-SESSION/1','future_batch_id':'batch07','source_mode':'SOURCE_ONLY/1',
 'preflight_external_TCB_seconds':120,'preflight_and_coordinator_AS':1073741824,'activation_receipt_seconds':10,
 'same_process_exec':True,'same_process_C09_resume_once':True,'memfd_seals_required':['WRITE','GROW','SHRINK','SEAL'],
 'test_profile':'SIMULATED_RESTART/1','jobs':jobs,'max_jobs':40,'driver_prepay':11,'test_hard_visits':512,
 'test_completed_visits':481,'joint_C09H_RootIPC_BC_completed':3231,'joint_hard_visits':5000,
 'full_calibration_hard_visits':62034,'calibration_seconds':300,'total_visits':1000000,'total_seconds':1800,
 'native_execution':'UNRUN','physical_WSL_restart_test':'UNRUN_NOT_AUTHORIZED'})
for name in ['c09_contract.json','root_ipc_contract.json','safety_contract.json']:
    p=W/'inputs'/name;x=json.loads(p.read_text(encoding='utf-8-sig'))
    x['future_batch_id']='batch07'
    for j in x['jobs']:
        if 'batch_id'in j:j['batch_id']='batch07'
    dump(name,x)
old=W/'inputs/dclr6batch06.slice';new=W/'inputs/dclr6batch07.slice'
if old.exists():old.rename(new)
new.write_text(new.read_text(encoding='utf-8').replace('batch06','batch07'),encoding='utf-8')
print(json.dumps({'jobs':40,'safe':30,'mutants':10,'completed_visits':481,'joint_completed':3231,'WSL_calls':0,'batch07_created':False}))
