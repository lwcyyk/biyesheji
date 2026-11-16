"""Offline host grammar, source/AST and input-bound checks; no target imports."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import sys

E=Path(__file__).resolve().parent
W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\cr01')
OLD=Path(r'D:\毕业设计\DCL-R6-isolated-verification\bc01')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
def norm(s):return s.replace('bc01','cr01').replace('batch07','batch08').replace('BATCH07','BATCH08')
def nodes(s):return {n.name:n for n in ast.parse(s,feature_version=(3,12)).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
def tree(n):return ast.dump(n,include_attributes=False)
syntax=[]
for p in [*sorted((W/'src').glob('*.py')),*sorted((W/'host').glob('*.py'))]:
    text=p.read_text(encoding='utf-8');ast.parse(text,filename=str(p),feature_version=(3,12));compile(text,str(p),'exec',dont_inherit=True)
    syntax.append({'relative':p.relative_to(W).as_posix(),'host_syntax':'PASS','Python3_12_grammar':'PASS','sha256':sha(p)})
assert len(syntax)==24 and not list(W.rglob('*.pyc'))
b=nodes(norm((OLD/'src/guard.py').read_text()));n=nodes((W/'src/guard.py').read_text())
core=['halt_budget','budget_health','execution_deadline','validate_state_document','init_counter','count',
 '_counter_lock','_canonical','_task_contract','_fact_path','_validate_fact','_append_journal','_reserve',
 'reserve_counter','claim_exact','Budget','safety_charge','root_verify_safety','exercise_gate_negatives',
 'verify_gate_audit','verify_sealed_safety','c09h_charge','root_verify_c09h','require_formal_admission']
assert all(tree(b[k])==tree(n[k]) for k in core)
for name in ['c09_handoff.py','root_ipc.py','boot_continuity_regression.py']:
    assert ast.dump(ast.parse(norm((OLD/'src'/name).read_text())),include_attributes=False)==ast.dump(ast.parse((W/'src'/name).read_text()),include_attributes=False)
oldboot=nodes(norm((OLD/'src/boot_continuity.py').read_text()));newboot=nodes((W/'src/boot_continuity.py').read_text())
protected=['read_capability','ticket_policy','eligibility','identity','child_admission','guard_admission','service_policy','before_seal','formal_gate','verify_regression']
assert all(tree(oldboot[k])==tree(newboot[k]) for k in protected)
oldtext=norm((OLD/'src/boot_continuity.py').read_text());newtext=(W/'src/boot_continuity.py').read_text()
assert oldtext[oldtext.index('    lockfd=None;capfd=None'):oldtext.index('def read_capability')]==newtext[newtext.index('    lockfd=None;capfd=None'):newtext.index('def read_capability')]
same=[];changed=[];added=[]
for p in sorted((W/'src').glob('*.py')):
    old=OLD/'src'/p.name;(same if old.exists() and sha(old)==sha(p) else changed if old.exists() else added).append(p.name)
assert len(same)==15 and len(changed)==5 and len(added)==3
for name in ['business_plan_original.json','child_contracts.json','runtime_critical.json','runtime_tree_lock.json']:assert sha(W/'inputs'/name)==sha(OLD/'inputs'/name)
for name in ['root_ipc_contract.json','c09_contract.json','boot_contract.json','safety_contract.json']:assert json.loads(norm((OLD/'inputs'/name).read_text()))==load(W/'inputs'/name)
cfg=load(W/'inputs/readiness_contract.json')
assert len(cfg['jobs'])==64 and len({j['case_id'] for j in cfg['jobs']})==64
assert sum(j['variant']=='mutant' for j in cfg['jobs'])==17
assert max(len(j['frames']) for j in cfg['jobs'])+1<=cfg['driver_prepay']==6
assert 1+64*(6+1)==cfg['regression_completed_visits']==449
assert cfg['global_calibration_hard_bound']==62034+512==62546<100000
oracle_imports=[]
for x in ast.walk(ast.parse((W/'src/readiness_oracle.py').read_text())):
    if isinstance(x,ast.Import):oracle_imports.extend(a.name for a in x.names)
    elif isinstance(x,ast.ImportFrom):oracle_imports.append(x.module)
assert not set(oracle_imports)&{'guard','service_readiness','readiness_regression','boot_continuity'}
dump(E/'STATIC_CHECKS.json',{'schema':'CR-static/1','host_interpreter':sys.version,'syntax':syntax,
 'native_CPython_compile':'UNRUN','target_imports_and_tests':0,'native_calls':0,
 'same_source_bytes':same,'modified_source_files':changed,'added_Linux_modules':added,
 'budget_gate_AST_unchanged':core,'protected_Boot_functions_AST_unchanged':protected,
 'sealed_memfd_claim_exec_block_unchanged':True,'RootIPC_C09_BC40_AST_namespace_only':True,
 'original_input_semantics_unchanged_except_namespace':True,'new_jobs':64,'mutants':17,
 'completed_visits':449,'regression_hard':512,'full_calibration_hard':62546,'oracle_imports':oracle_imports})
m=load(OLD/'inputs/static_manifest.json')
m.update(schema='C00Ready-static-manifest/1',version='C00Ready-static-1',freeze_revision='r2',
 source_directory='/var/lib/dcl-r6/cr01/src',source_hashes={p.name:sha(p) for p in sorted((W/'src').glob('*.py'))},
 profile_approval='C00READY_HOST_STATIC_ONLY; native deployment/diagnosis/execution not authorized',
 runtime_compatibility='UNVERIFIED_CURRENT_PLATFORM',resource_enforcement='UNVERIFIED_DYNAMIC')
m['unit_template_hashes']['slice']=sha(W/'inputs/dclr6batch08.slice')
for name,key in [('root_ipc_contract.json','root_ipc_contract_sha256'),('c09_contract.json','c09_contract_sha256'),('boot_contract.json','boot_contract_sha256'),('safety_contract.json','safety_contract_sha256'),('readiness_contract.json','readiness_contract_sha256')]:m[key]=sha(W/'inputs'/name)
m['bound_inputs']={'inputs/'+p.name:sha(p) for p in sorted((W/'inputs').iterdir()) if p.name not in ['static_manifest.json','execution_lock.json']}
m['readiness_delta']={'profile':'C00-READY/1','cases':['C00','C10'],'readiness_seconds':14,'poll_seconds':0.05,
 'sample_cap':300,'diagnostic_row_limit':131072,'jobs':64,'mutants':17,'completed_visits':449,'hard_visits':512,
 'old_calibration_hard':62034,'new_calibration_hard':62546,'soft_calibration_cap':100000,'calibration_seconds':300,
 'counter_context':'Original C00 ticket; separate512 ceiling before C09H; no budget core change',
 'modes':['C00_DIAGNOSTIC_ONLY','CALIBRATE_S1S9_THEN_F1_F4'],'new_actual_processes':0}
dump(W/'inputs/static_manifest.json',m)
l=json.loads(norm((OLD/'inputs/execution_lock.json').read_text()))
l.update(schema='C00Ready-execution-lock/1',source_version='C00Ready-static-1',freeze_revision='r2',
 static_manifest_sha256=sha(W/'inputs/static_manifest.json'),unit_slice_sha256=m['unit_template_hashes']['slice'],
 root_ipc_contract_sha256=m['root_ipc_contract_sha256'],c09_contract_sha256=m['c09_contract_sha256'],
 boot_contract_sha256=m['boot_contract_sha256'],safety_contract_sha256=m['safety_contract_sha256'],
 readiness_contract_sha256=m['readiness_contract_sha256'],required_readiness_profile='C00-READY/1',
 windows_entry_sha256=sha(W/'host/windows_entry.py'),allowed_scopes=['C00_DIAGNOSTIC_ONLY','CALIBRATE_S1S9_THEN_F1_F4'])
l['readiness_modes']={'C00_DIAGNOSTIC_ONLY':'Real C00 native fields/probe then64 synthetic jobs; close/seal; no other C/S/gates/models',
 'CALIBRATE_S1S9_THEN_F1_F4':'Explicit full authorization required; then all original C/BC40/IPC56/H34/S34/negative17 and gate->F1->F4'}
l['readiness_limits']=m['readiness_delta']
l['readiness_schedule']=['single-session preflight/exec','C00 bounded native lease + field diagnostics before ticket','C00 probe',
 'READY64 + independent raw audit','DIAGNOSTIC_ONLY close OR explicitly authorized C01-C08','C09H34','RootIPC56','BC40','real C09',
 'same-process once resume','C10 native lease','C11-C12','S34','negative17','resource gate','F1','F4','close/seal']
l['authorization_receipt_required_fields']+=['readiness_contract_sha256','readiness_profile','C00_diagnostic_explicitly_approved','Full_conditional_chain_explicitly_approved']
dump(W/'inputs/execution_lock.json',l)
for name in ['static_manifest.json','execution_lock.json','readiness_contract.json','boot_contract.json','root_ipc_contract.json','c09_contract.json','safety_contract.json']:(E/name).write_bytes((W/'inputs'/name).read_bytes())
rows=[{'relative':p.relative_to(W).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p),
 'future_linux':'/var/lib/dcl-r6/cr01/'+p.relative_to(W).as_posix() if p.relative_to(W).parts[0]!='host' else None} for p in sorted(W.rglob('*')) if p.is_file()]
assert len(rows)==36
dump(E/'STATIC_WORKSPACE_LOCK.json',{'schema':'CR-workspace/1','version':'C00Ready-static-1/r2','host':str(W),
 'future_linux':'/var/lib/dcl-r6/cr01','deployed':False,'files':rows,'Linux_sources':23,'Windows_sources':1,'inputs':12,'runtime_pyc':0})
diff=[]
for p in sorted((W/'src').glob('*.py')):
    old=OLD/'src'/p.name
    if not old.exists() or old.read_bytes()!=p.read_bytes():diff.extend(difflib.unified_diff(old.read_text().splitlines(True) if old.exists() else [],p.read_text().splitlines(True),fromfile='BootContinuity-static-1/r4/'+p.name if old.exists() else '/dev/null',tofile='C00Ready-static-1/r2/'+p.name))
diff.extend(difflib.unified_diff((OLD/'host/windows_entry.py').read_text().splitlines(True),(W/'host/windows_entry.py').read_text().splitlines(True),fromfile='old/host/windows_entry.py',tofile='new/host/windows_entry.py'))
(E/'SOURCE_COMPLETE.diff').write_text(''.join(diff),encoding='utf-8')
diff=[]
for name in sorted({p.name for p in (OLD/'inputs').iterdir()}|{p.name for p in (W/'inputs').iterdir()}):
    a=OLD/'inputs'/name;b=W/'inputs'/name
    if not a.exists() or not b.exists() or a.read_bytes()!=b.read_bytes():diff.extend(difflib.unified_diff(a.read_text().splitlines(True) if a.exists() else [],b.read_text().splitlines(True) if b.exists() else [],fromfile='old/inputs/'+name,tofile='new/inputs/'+name))
(E/'INPUT_COMPLETE.diff').write_text(''.join(diff),encoding='utf-8')
print(json.dumps({'version':'C00Ready-static-1/r2','files':36,'programs':24,'preserved_source_bytes':15,'protected_budget_AST':24,
 'native_calls':0,'static_manifest_sha256':sha(W/'inputs/static_manifest.json'),'execution_lock_sha256':sha(W/'inputs/execution_lock.json'),
 'readiness_contract_sha256':sha(W/'inputs/readiness_contract.json')}))
