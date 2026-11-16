"""Freeze source/input artifacts and perform AST/hash checks without importing candidates."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import zipfile

E=Path(__file__).resolve().parent
R=E.parent.parent
W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\ri01')
OLD=Path(r'D:\毕业设计\DCL-R6-isolated-verification\c09f01')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))


def dump(path,x):Path(path).write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
def nodes(p):return {n.name:n for n in ast.parse(Path(p).read_text(encoding='utf-8')).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
def structural(n):return ast.dump(n,include_attributes=False)


core_names=['halt_budget','budget_health','execution_deadline','validate_state_document','init_counter','count',
            '_counter_lock','_canonical','_task_contract','_fact_path','_validate_fact','_append_journal','_reserve',
            'reserve_counter','claim_exact','Budget','safety_charge','root_verify_safety','exercise_gate_negatives',
            'verify_gate_audit','verify_sealed_safety','c09h_charge','root_verify_c09h','require_formal_admission']
before=nodes(OLD/'src/guard.py');after=nodes(W/'src/guard.py')
core_checks=[{'function':name,'AST_unchanged':structural(before[name])==structural(after[name])} for name in core_names]
assert all(r['AST_unchanged'] for r in core_checks)
unchanged=[];modified=[];added=[]
for p in sorted((W/'src').glob('*.py')):
    old=OLD/'src'/p.name
    target=unchanged if old.exists() and sha(old)==sha(p) else modified if old.exists() else added
    target.append(p.name)
assert modified==['c09_handoff.py','guard.py'] and len(unchanged)==12 and len(added)==3
assert set(added)=={'root_ipc.py','root_ipc_oracle.py','root_ipc_regression.py'}
for name in ['business_plan_original.json','child_contracts.json','runtime_critical.json','runtime_tree_lock.json']:
    assert sha(W/'inputs'/name)==sha(OLD/'inputs'/name),name
old_s=load(OLD/'inputs/safety_contract.json');new_s=load(W/'inputs/safety_contract.json')
old_c=load(OLD/'inputs/c09_contract.json');new_c=load(W/'inputs/c09_contract.json')
normalize=lambda x:json.loads(json.dumps(x).replace('batch05','batch06'))
assert normalize(old_s)==new_s and normalize(old_c)==new_c
assert old_s['gate_negative_cases']==new_s['gate_negative_cases']
hb=nodes(OLD/'src/c09_handoff.py');ha=nodes(W/'src/c09_handoff.py')
handoff_preserved=['classify','synthetic_initial','window','counter','resume_admission','verify_completed_handoff']
assert all(structural(hb[n])==structural(ha[n]) for n in handoff_preserved)
oracle_imports=[]
for n in ast.walk(ast.parse((W/'src/root_ipc_oracle.py').read_text())):
    if isinstance(n,ast.Import):oracle_imports.extend(a.name for a in n.names)
    elif isinstance(n,ast.ImportFrom):oracle_imports.append(n.module)
assert not set(oracle_imports)&{'guard','root_ipc','root_ipc_regression','c09_handoff','c09_regression'}

cfg=load(W/'inputs/root_ipc_contract.json')
assert len(cfg['jobs'])==56 and len({j['case_id'] for j in cfg['jobs']})==56
assert sum(j['variant']=='safe' for j in cfg['jobs'])==48
assert cfg['completed_visit_upper_bound']==1+sum(j['driver_charge_bound']+j['independent_audit_charges'] for j in cfg['jobs'])==505
assert cfg['combined_C09H_completed_upper_bound']==2750<5000
dump(E/'AST_AND_INVARIANT_CHECK.json',{
 'schema':'RI-static-invariants/1','status':'PASS_STATIC','budget_core_functions':core_checks,
 'unchanged_source_files':unchanged,'modified_source_files':modified,'added_source_files':added,
 'unchanged_handoff_functions':handoff_preserved,'C09H_jobs_semantically_unchanged':34,
 'S_jobs_semantically_unchanged':34,'negative_cases_unchanged':17,'namespace_only':'batch05 -> batch06',
 'oracle_imports':oracle_imports,'test_jobs':56,'test_variants':{'safe':48,'mutant':8},
 'dynamic_execution_count':0,'target_module_imports':0,
 'scope':'AST/byte/value equality and source control-flow inspection; no behavioral proof'})

m=load(OLD/'inputs/static_manifest.json')
m.update(schema='RootIPC-static-manifest/1',version='RootIPC-static-1',freeze_revision='r4',
         profile_approval='ROOTIPC_STATIC_ONLY; batch06 dynamic authorization absent',
         source_directory='/var/lib/dcl-r6/ri01/src',runtime_compatibility='UNVERIFIED_DYNAMIC',
         resource_enforcement='UNVERIFIED_DYNAMIC')
m['source_hashes']={p.relative_to(W/'src').as_posix():sha(p) for p in sorted((W/'src').rglob('*')) if p.is_file()}
m['unit_template_hashes']['slice']=sha(W/'inputs/dclr6batch06.slice')
m['safety_contract_sha256']=sha(W/'inputs/safety_contract.json')
m['c09_contract_sha256']=sha(W/'inputs/c09_contract.json')
m['root_ipc_contract_sha256']=sha(W/'inputs/root_ipc_contract.json')
m['input_binding_scope']='Original C00-C12, C09H34, S34, gate17 and frozen business; new IPC56; namespace batch06'
m['root_ipc_delta']={
 'contract':'ROOT-IPC/1','jobs':56,'completed_upper_bound':505,'hard_visits':512,
 'combined_C09H_completed_upper_bound':2750,'combined_C09H_hard_visits':5000,
 'full_calibration_hard_visits':62034,'calibration_soft_visits':100000,'calibration_seconds':300,
 'max_extra_root_probe_children':1,'probe_uids':[999,65534],'probe_AS':1073741824,
 'TCB_scope':'Root suite runs between C09H completion and real C09; sequential helper outside payload slice',
 'poststop_child_grace_seconds':30,'cleanup_reap_seconds':5,'latency_guarantee':'UNMEASURED_CONDITIONAL',
 'publication_extra_cost':'one extra directory fsync for cross-directory Root publication; measure dynamically'}
dump(W/'inputs/static_manifest.json',m)
l=normalize(load(OLD/'inputs/execution_lock.json'))
def rewrite(x):
    if isinstance(x,str):return x.replace('c09f01','ri01').replace('BATCH05','BATCH06').replace('C09Fix-static-1','RootIPC-static-1')
    if isinstance(x,list):return [rewrite(v) for v in x]
    if isinstance(x,dict):return {k:rewrite(v) for k,v in x.items()}
    return x
l=rewrite(l)
l.update(schema='RootIPC-execution-lock/1',status='FROZEN_STATIC; DYNAMIC_UNAUTHORIZED',source_version='RootIPC-static-1',
 freeze_revision='r4',
 static_manifest_sha256=sha(W/'inputs/static_manifest.json'),safety_contract_sha256=m['safety_contract_sha256'],
 c09_contract_sha256=m['c09_contract_sha256'],root_ipc_contract_sha256=m['root_ipc_contract_sha256'],
 unit_slice_sha256=m['unit_template_hashes']['slice'],required_root_ipc_profile='ROOT-IPC/1')
l['preparation_commands'].insert(2,['/usr/bin/install','-d','-m','0700','-o','root','-g','root',
                                  '/var/lib/dcl-r6/batch06/inputs/root_private'])
l['authorization_receipt_required_fields']+=['root_ipc_profile','root_ipc_contract_sha256','RootIPC_helpers_explicitly_approved']
l['root_ipc_schedule']=['C00-C08','C09H34','ROOT_C09H_AUDIT','ROOT_IPC56_AND_IMMEDIATE_ORACLE',
 'ROOT_IPC_RAW_AUDIT','ROOT_IPC_QUALIFICATION','REAL_C09_DURABLE_ACK_WAITPID_FRESH_READ',
 'SAME_WINDOW_RESUME_ONCE','C10-C12','S34','GATE17','RESOURCE_GATE_PASS','F1','F4','CLOSE_AND_PARENT_SEAL']
l['root_ipc_internal_call']='root_ipc_regression.run_suite(guard); no standalone argv or new unit'
l['root_ipc_helper_contract']=cfg['probe_child']
l['root_ipc_limits']=m['root_ipc_delta']
l['coordinator_process_contract']+=' RootIPC56 may fork at most one sequential 999/65534 credential probe; child alarm2s/AS1GiB, parent bounded kill+wait; explicit new approval required. Parent records ordinary waitpid and performs final seal after child reap.'
dump(W/'inputs/execution_lock.json',l)
rows=[{'relative':p.relative_to(W).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p),
       'linux':'/var/lib/dcl-r6/ri01/'+p.relative_to(W).as_posix()} for p in sorted(W.rglob('*')) if p.is_file()]
assert len(rows)==44, len(rows)
dump(E/'STATIC_WORKSPACE_LOCK.json',{'schema':'RI-static-workspace/1','version':'RootIPC-static-1',
 'freeze_revision':'r4','host':str(W),'linux':'/var/lib/dcl-r6/ri01','files':rows,
 'source_count':17,'cache_count':17,'input_count':10,'dynamic_authorization':False,'batch06_created':False})
for name in ['static_manifest.json','execution_lock.json','root_ipc_contract.json','safety_contract.json','c09_contract.json']:
    (E/name).write_bytes((W/'inputs'/name).read_bytes())
diffs=[]
for p in sorted((W/'src').glob('*.py')):
    old=OLD/'src'/p.name
    if not old.exists() or old.read_bytes()!=p.read_bytes():
        diffs.extend(difflib.unified_diff(old.read_text().splitlines(True) if old.exists() else [],p.read_text().splitlines(True),
                    fromfile='C09Fix-static-1/r1/'+p.name if old.exists() else '/dev/null',tofile='RootIPC-static-1/r4/'+p.name))
(E/'SOURCE_COMPLETE.diff').write_text(''.join(diffs),encoding='utf-8')
diffs=[]
old_names={p.name for p in (OLD/'inputs').glob('*')};new_names={p.name for p in (W/'inputs').glob('*')}
for name in sorted(old_names|new_names):
    a=OLD/'inputs'/name;b=W/'inputs'/name
    if not a.exists() or not b.exists() or a.read_bytes()!=b.read_bytes():
        diffs.extend(difflib.unified_diff(a.read_text().splitlines(True) if a.exists() else [],b.read_text().splitlines(True) if b.exists() else [],fromfile='old/inputs/'+name,tofile='new/inputs/'+name))
(E/'INPUT_COMPLETE.diff').write_text(''.join(diffs),encoding='utf-8')
dump(E/'SOURCE_DIFF_INDEX.json',{'modified':modified,'added':added,'unchanged':unchanged,
 'source_diff':'SOURCE_COMPLETE.diff','input_diff':'INPUT_COMPLETE.diff','original':'original/',
 'source_diff_sha256':sha(E/'SOURCE_COMPLETE.diff'),'input_diff_sha256':sha(E/'INPUT_COMPLETE.diff'),
 'cache_note':'All17 regenerated by real CPython3.12.3 CHECKED_HASH py_compile; compile filename ri01; body not run'})
print(json.dumps({'frozen_files':len(rows),'modified':modified,'added':added,'unchanged':len(unchanged),
                  'budget_core_ast_preserved':len(core_checks),'static_manifest_sha256':sha(W/'inputs/static_manifest.json'),
                  'execution_lock_sha256':sha(W/'inputs/execution_lock.json'),'IPC_contract_sha256':sha(W/'inputs/root_ipc_contract.json')}))
