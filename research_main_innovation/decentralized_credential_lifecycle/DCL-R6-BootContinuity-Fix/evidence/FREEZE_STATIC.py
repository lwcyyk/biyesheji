"""Offline host grammar/AST/hash audit. Does not import or run target modules."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import sys

E=Path(__file__).resolve().parent
P=E.parent
W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\bc01')
OLD=Path(r'D:\毕业设计\DCL-R6-isolated-verification\ri01')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
def norm(s):return s.replace('ri01','bc01').replace('batch06','batch07').replace('BATCH06','BATCH07')
def nodes(s):return {n.name:n for n in ast.parse(s,feature_version=(3,12)).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
def tree(n):return ast.dump(n,include_attributes=False)

syntax=[]
for f in [*sorted((W/'src').glob('*.py')),*sorted((W/'host').glob('*.py'))]:
    text=f.read_text(encoding='utf-8');ast.parse(text,filename=str(f),feature_version=(3,12));compile(text,str(f),'exec',dont_inherit=True)
    syntax.append({'file':f.relative_to(W).as_posix(),'host_syntax':'PASS','Python3_12_grammar':'PASS','target_body_executed':0,'sha256':sha(f)})
assert len(syntax)==21 and not list(W.rglob('*.pyc'))
base=nodes(norm((OLD/'src/guard.py').read_text(encoding='utf-8')));new=nodes((W/'src/guard.py').read_text(encoding='utf-8'))
core=['halt_budget','budget_health','execution_deadline','validate_state_document','init_counter','count',
 '_counter_lock','_canonical','_task_contract','_fact_path','_validate_fact','_append_journal','_reserve',
 'reserve_counter','claim_exact','Budget','safety_charge','root_verify_safety','exercise_gate_negatives',
 'verify_gate_audit','verify_sealed_safety','c09h_charge','root_verify_c09h','require_formal_admission']
assert all(tree(base[n])==tree(new[n]) for n in core)
for filename in ['root_ipc.py','c09_handoff.py']:
    assert ast.dump(ast.parse(norm((OLD/'src'/filename).read_text())),include_attributes=False)==ast.dump(ast.parse((W/'src'/filename).read_text()),include_attributes=False)
unchanged=[];changed=[];added=[]
for f in sorted((W/'src').glob('*.py')):
    old=OLD/'src'/f.name
    (unchanged if old.exists() and sha(old)==sha(f) else changed if old.exists() else added).append(f.name)
assert len(unchanged)==14 and changed==['c09_handoff.py','guard.py','root_ipc.py'] and len(added)==3
for filename in ['business_plan_original.json','child_contracts.json','runtime_tree_lock.json','runtime_critical.json']:
    assert sha(W/'inputs'/filename)==sha(OLD/'inputs'/filename)
for filename in ['root_ipc_contract.json','c09_contract.json','safety_contract.json']:
    assert json.loads(norm((OLD/'inputs'/filename).read_text()))==load(W/'inputs'/filename)
cfg=load(W/'inputs/boot_contract.json')
assert len(cfg['jobs'])==40 and len({j['case_id'] for j in cfg['jobs']})==40
assert sum(j['variant']=='mutant' for j in cfg['jobs'])==10
assert max(len(j['events']) for j in cfg['jobs'])<=10
assert cfg['driver_prepay']>=1+max(len(j['events']) for j in cfg['jobs'])
assert cfg['test_completed_visits']==1+40*(cfg['driver_prepay']+1)==481
assert 2245+505+481==cfg['joint_C09H_RootIPC_BC_completed']==3231<5000
imports=[]
for n in ast.walk(ast.parse((W/'src/boot_continuity_oracle.py').read_text())):
    if isinstance(n,ast.Import):imports.extend(a.name for a in n.names)
    elif isinstance(n,ast.ImportFrom):imports.append(n.module)
assert not set(imports)&{'guard','boot_continuity','boot_continuity_regression','root_ipc','c09_handoff'}
dump(E/'STATIC_CHECKS.json',{'schema':'BC-static-checks/1','host_interpreter':sys.version,
 'host_syntax_and_grammar':syntax,'native_CPython3_12_compile':'UNRUN_PLATFORM_QUERY_NOT_AUTHORIZED',
 'unchanged_source_bytes':unchanged,'modified_source_files':changed,'new_Linux_source_files':added,
 'budget_and_gate_AST_unchanged':core,'RootIPC_handoff_AST_unchanged_after_namespace_normalization':True,
 'RootIPC56_C09H34_S34_gate17_values_unchanged_except_batch':True,'oracle_imports':imports,
 'new_tests':40,'mutants':10,'native_calls':0,'target_body_executions':0,'batch07_created':False,
 'checks_scope':'Syntax/AST/literal/data/hash only; no simulation, target imports, OS lifecycle or protocol behavior was run'})

m=load(OLD/'inputs/static_manifest.json')
m.update(schema='BootContinuity-static-manifest/1',version='BootContinuity-static-1',freeze_revision='r4',
 source_directory='/var/lib/dcl-r6/bc01/src',source_hashes={f.name:sha(f) for f in sorted((W/'src').glob('*.py'))},
 profile_approval='BOOTCONTINUITY_STATIC_ONLY; deployment/native compile/dynamic authorization pending',
 runtime_compatibility='UNVERIFIED_CURRENT_PLATFORM',resource_enforcement='UNVERIFIED_DYNAMIC')
m['unit_template_hashes']['slice']=sha(W/'inputs/dclr6batch07.slice')
m['root_ipc_contract_sha256']=sha(W/'inputs/root_ipc_contract.json');m['c09_contract_sha256']=sha(W/'inputs/c09_contract.json');m['safety_contract_sha256']=sha(W/'inputs/safety_contract.json')
m['boot_contract_sha256']=sha(W/'inputs/boot_contract.json')
m['source_mode']='SOURCE_ONLY/1'
m['bound_inputs']={'inputs/'+f.name:sha(f) for f in sorted((W/'inputs').iterdir()) if f.name not in ['static_manifest.json','execution_lock.json']}
m['boot_continuity_delta']={'profile':'BC-SINGLE-SESSION/1','preflight_TCB_seconds':120,'Root_entry_AS_bytes':1<<30,
 'activation_TTL_seconds':10,'resident_process_delta':0,'new_systemd_units':0,'same_process_internal_C09_resume':True,
 'synthetic_jobs':40,'mutants':10,'completed_visits':481,'hard_visits':512,
 'combined_completed_bound':3231,'combined_hard_cap':5000,'calibration_hard_bound':62034,
 'source_cache_policy':'No target pyc; future actual3.12 compile(source) without module execution or cache emission',
 'current_native_status':'UNRUN; host-only workspace'}
dump(W/'inputs/static_manifest.json',m)
lock=json.loads(norm((OLD/'inputs/execution_lock.json').read_text()))
lock.update(schema='BootContinuity-execution-lock/1',source_version='BootContinuity-static-1',freeze_revision='r4',
 static_manifest_sha256=sha(W/'inputs/static_manifest.json'),root_ipc_contract_sha256=m['root_ipc_contract_sha256'],
 c09_contract_sha256=m['c09_contract_sha256'],safety_contract_sha256=m['safety_contract_sha256'],
 unit_slice_sha256=m['unit_template_hashes']['slice'],boot_contract_sha256=m['boot_contract_sha256'],
 source_mode='SOURCE_ONLY/1',required_boot_continuity_profile='BC-SINGLE-SESSION/1',
 status='FROZEN_STATIC; DEPLOYMENT_AND_DYNAMIC_UNAUTHORIZED')
lock['windows_entry_sha256']=sha(W/'host/windows_entry.py')
lock['windows_single_call']=[r'C:\Windows\System32\wsl.exe','--distribution','Ubuntu-24.04','--user','root','--exec',
 '/usr/bin/python3.12','-I','-S','-B','/var/lib/dcl-r6/bc01/src/boot_continuity.py','--activate','--batch-root','/var/lib/dcl-r6/batch07']
lock['authorization_sources']={
 'receipt':'/mnt/d/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-batch07/evidence/execution_authorization.json',
 'text':'/mnt/d/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-batch07/evidence/TASK_REQUEST.txt'}
lock['activation_handoff']={'method':'same PID os.execve plus inherited sealed memfd/exclusive lock','env':['DCL_BC_CAP_FD','DCL_BC_LOCK_FD'],
 'persistent_once_record':'inputs/root_private/boot/activation.json','activation_token_TTL_initial_only':10,
 'actual_start_record':'inputs/BOOT_START.json after active/stable C00 process before ticket release',
 'resume':'Only internal guard.launcher(True) in same live Root process after actual C09 verified exit23; no second WSL call'}
lock['old_resume_argv_reference']=lock.pop('expected_C09_resume_command')
lock['expected_C09_resume_command']={'kind':'INTERNAL_CALL_ONLY','call':'guard.launcher(resume=True,calibrate_only=False)','same_parent_PID':True,'max_count':1}
lock['calibrate_only_C09_resume_command']={'kind':'INTERNAL_CALL_ONLY','call':'guard.launcher(resume=True,calibrate_only=True)'}
lock['authorization_receipt_required_fields']+=['boot_contract_sha256','boot_continuity_profile','SingleSession_exec_explicitly_approved','SameProcess_C09_resume_explicitly_approved','source_mode']
lock['boot_continuity_schedule']=['one Windows WSL call','native artifact/runtime/identity fresh checks','frozen preparation6','same-boot final checks',
 'exclusive claim/sealed inherited FD','same-PID exec of frozen guard argv','Root/child renewed checks','C00-C08',
 'C09H34','RootIPC56','BC40 and independent raw oracle','real C09 ACK/waitpid/fresh-read',
 'one same-process verified resume','C10-C12','S34','negative17','RESOURCE_GATE_PASS','F1','F4','parent final seal']
lock['boot_continuity_limits']=m['boot_continuity_delta']
dump(W/'inputs/execution_lock.json',lock)
for name in ['static_manifest.json','execution_lock.json','boot_contract.json','root_ipc_contract.json','c09_contract.json','safety_contract.json']:
    (E/name).write_bytes((W/'inputs'/name).read_bytes())
rows=[{'relative':f.relative_to(W).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f),
 'future_linux':'/var/lib/dcl-r6/bc01/'+f.relative_to(W).as_posix() if not f.relative_to(W).parts[0]=='host' else None}
 for f in sorted(W.rglob('*')) if f.is_file()]
assert len(rows)==32
dump(E/'STATIC_WORKSPACE_LOCK.json',{'schema':'BC-workspace/1','version':'BootContinuity-static-1/r4','host':str(W),
 'future_linux':'/var/lib/dcl-r6/bc01','files':rows,'source_files':20,'host_entry_files':1,'inputs':11,'runtime_pyc':0,
 'deployed_Linux':False,'batch07_created':False,'native_queries':0})
diff=[]
for f in sorted((W/'src').glob('*.py')):
    old=OLD/'src'/f.name
    if not old.exists() or old.read_bytes()!=f.read_bytes():
        diff.extend(difflib.unified_diff(old.read_text().splitlines(True) if old.exists() else [],f.read_text().splitlines(True),
         fromfile='RootIPC-static-1/r4/'+f.name if old.exists() else '/dev/null',tofile='BootContinuity-static-1/r4/'+f.name))
diff.extend(difflib.unified_diff([], (W/'host/windows_entry.py').read_text().splitlines(True),fromfile='/dev/null',tofile='host/windows_entry.py'))
(E/'SOURCE_COMPLETE.diff').write_text(''.join(diff),encoding='utf-8')
diff=[]
for name in sorted({p.name for p in (W/'inputs').iterdir()}|{p.name for p in (OLD/'inputs').iterdir()}):
    a=OLD/'inputs'/name;b=W/'inputs'/name
    if not a.exists() or not b.exists() or a.read_bytes()!=b.read_bytes():
        diff.extend(difflib.unified_diff(a.read_text().splitlines(True) if a.exists() else [],b.read_text().splitlines(True) if b.exists() else [],fromfile='old/inputs/'+name,tofile='new/inputs/'+name))
(E/'INPUT_COMPLETE.diff').write_text(''.join(diff),encoding='utf-8')
print(json.dumps({'version':'BootContinuity-static-1/r4','files':len(rows),'native_calls':0,'syntax_files':len(syntax),
 'old_source_bytes_unchanged':len(unchanged),'budget_gate_AST_preserved':len(core),
 'static_manifest_sha256':sha(W/'inputs/static_manifest.json'),'execution_lock_sha256':sha(W/'inputs/execution_lock.json'),
 'boot_contract_sha256':sha(W/'inputs/boot_contract.json')},ensure_ascii=False))
