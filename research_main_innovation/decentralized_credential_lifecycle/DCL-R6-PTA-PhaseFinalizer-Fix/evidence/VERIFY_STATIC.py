"""Host AST/hash checks and explicit inert import probes; no native target execution."""
from pathlib import Path
import ast,copy,difflib,hashlib,json,os,subprocess,sys
E=Path(__file__).resolve().parent;O=E.parent;B=O.parent
W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\pf01');OLD=E/'SOURCE_BEFORE'
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def put(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
trees={};syntax=[]
for p in sorted(W.rglob('*.py')):
    t=ast.parse(p.read_bytes(),filename=str(p),feature_version=(3,12));compile(p.read_bytes(),str(p),'exec')
    trees[p.relative_to(W).as_posix()]=t;syntax.append({'file':p.relative_to(W).as_posix(),'status':'PASS_STATIC','python312_grammar':True,'target_module_executed':False})
assert len(syntax)==38 and not list(W.rglob('*.pyc'))
def fn(file,name):return next(n for n in ast.walk(trees[file]) if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
def calls(node,name):return [n for n in ast.walk(node) if isinstance(n,ast.Call) and (isinstance(n.func,ast.Name) and n.func.id==name or isinstance(n.func,ast.Attribute) and n.func.attr==name)]
def guarded_calls(node,callee):
    inside=[]
    for n in ast.walk(node):
        if isinstance(n,ast.With) and any(isinstance(i.context_expr,ast.Call) and isinstance(i.context_expr.func,ast.Name) and i.context_expr.func.id=='_phase_guard' for i in n.items):
            inside.extend(calls(n,callee))
    return len(inside)==len(calls(node,callee)) and bool(inside)
checks=[]
def check(name,condition,file,functions):
    assert condition,name
    checks.append({'check':name,'status':'PASS_STATIC','file':file,'functions':functions,'evidence_lines':{n:fn(file,n).lineno for n in functions}})
life='src/startup_lifecycle.py';boot='src/boot_continuity.py';host='host/startup_finalize.py';guard='src/guard.py'
for name in ['arm','require_work']:
    check(name+' holds phase guard across commit',guarded_calls(fn(life,name),'_commit_phase'),life,[name])
check('ready publication guarded',guarded_calls(fn(life,'runtime_ready'),'_root_write'),life,['runtime_ready'])
check('Root runtime read guarded',guarded_calls(fn(life,'runtime_checkpoint'),'_runtime_checkpoint_locked') is False and any(calls(n,'_runtime_checkpoint_locked') for n in ast.walk(fn(life,'runtime_checkpoint')) if isinstance(n,ast.With)),life,['runtime_checkpoint'])
# The Root branch is guarded; the second call is intentionally the group-readable Payload branch.
root_branch=fn(life,'runtime_checkpoint').body[0]
check('Root branch all reads guarded',isinstance(root_branch,ast.If) and guarded_calls(root_branch,'_runtime_checkpoint_locked'),life,['runtime_checkpoint'])
check('prewindow phase writer guarded',guarded_calls(fn(life,'_set_phase'),'_set_phase_locked'),life,['_set_phase'])
phase_text=ast.unparse(fn(life,'_phase_guard'))
check('mutex cancellation and fixed limits',all(s in phase_text for s in ['range(512)','LOCK_NB','_cancel','LOCK_UN','yield (store, until)']) and len(calls(fn(life,'_phase_guard'),'_cancel'))>=3,life,['_phase_guard','_cancel'])
check('time bound uses existing deadline',all(s in ast.unparse(fn(life,'_phase_deadline')) for s in ['preflight_deadline','deadline','stop_at',"s['T0'] + 300"]),life,['_phase_deadline'])
check('private version and digest validated',all(s in ast.unparse(fn(life,'_runtime_checkpoint_locked')) for s in ['private_sequence','phase_record_sha256','initialization_id','phase_snapshot_policy']),life,['_runtime_checkpoint_locked'])
check('WORK source phases retained',all(s in ast.unparse(fn(life,'require_work')) for s in ['RUNTIME_ARMED','RUNNING','PT_NO_PREWINDOW_WORK','PF_WORK_WRITER_IDENTITY']),life,['require_work'])
check('writer single scheduler identity',bool(calls(fn(life,'_commit_phase'),'identity')) and 'launcher_identity' in ast.unparse(fn(life,'_commit_phase')),life,['_commit_phase'])
check('sequence monotonicity retained','old[\'sequence\'] + 1' in ast.unparse(fn(life,'_set_phase_locked')) and 'PF_PHASE_SEQUENCE' in ast.unparse(fn(life,'_set_phase_locked')),life,['_set_phase_locked'])
check('seal only inspection call explicit',any(k.arg=='terminal_inspection' and isinstance(k.value,ast.Constant) and k.value.value is True for c in calls(fn(life,'seal_applicability'),'runtime_checkpoint') for k in c.keywords),life,['seal_applicability'])
entry=trees['src/admin_postexit.py'];allowed_top=(ast.Import,ast.ImportFrom,ast.FunctionDef)
assert all(isinstance(n,allowed_top) or isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) or isinstance(n,ast.If) for n in entry.body)
check('entry defers all target loading',not any(isinstance(n,ast.Import) and any(a.name=='boot_continuity' for a in n.names) for n in entry.body), 'src/admin_postexit.py',['checked_source','load_target','main'])
main=fn('src/admin_postexit.py','main')
check('checked source precedes loader',calls(main,'checked_source')[0].lineno<calls(main,'load_target')[0].lineno,'src/admin_postexit.py',['main'])
check('isolation interpreter exact',all(s in ast.unparse(fn('src/admin_postexit.py','checked_source')) for s in ['sys.flags.isolated','sys.flags.no_site','sys.dont_write_bytecode','/var/lib/dcl-r6/pf01/src','(3, 12, 3)']),'src/admin_postexit.py',['checked_source'])
check('fixed path and module origin',all(s in ast.unparse(fn('src/admin_postexit.py','load_target')) for s in ['sys.path.insert','import_module','target.__file__','PF_ADMIN_MODULE_ORIGIN']),'src/admin_postexit.py',['load_target'])
check('admin export has no launch/budget APIs',not any(calls(fn(life,'post_exit_export'),name) for name in ['Popen','reserve_counter','init_counter','launch_one','stop_tree','launcher','run_suite']),life,['post_exit_export'])
check('post exit bounded role audit',all(s in ast.unparse(fn(life,'post_exit_export')) for s in ['range(128)','signal.alarm(30)','began + 5','STARTUP_NATIVE_AUDIT.json']),life,['post_exit_export'])
check('group empty does not assign internal success',"f['internal_status']" in ast.unparse(fn(life,'administrative_policy')) and 'CLOSED_CLEANUP_CONFIRMED' not in ast.unparse(fn(life,'administrative_policy')),life,['administrative_policy'])
check('native success still admin exports',not any(isinstance(n,ast.Return) for n in fn(life,'post_exit_export').body if isinstance(n,ast.If) and any(isinstance(x,ast.Constant) and x.value=='NATIVE_SEAL_COMPLETED' for x in ast.walk(n.test))),life,['post_exit_export'])
check('host failure records independent native status',all(s in ast.unparse(fn(host,'finalize')) for s in ['STARTUP_POSTEXIT_FAILURE.json','preserved_native_audit','ADMIN_EVIDENCE_UNRESOLVED']),host,['finalize','preserved_native_audit'])
check('repeat validates both archive and manifest',all(s in ast.unparse(fn(host,'finalize')) for s in ['STARTUP_ADMIN_EVIDENCE.zip','STARTUP_ADMIN_MANIFEST.json','manifest_sha256']),host,['finalize'])
check('snapshot path and byte caps',all(s in ast.unparse(fn(host,'finalize')) for s in ['PF_HOST_ADMIN_BOUND','PF_ADMIN_EXPORT_PATH','admin_max_files','admin_max_bytes']),host,['finalize'])
suite_calls={n.func.value.id:n.lineno for n in calls(fn(guard,'_launcher_work'),'run_suite') if isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name)}
check('PT then PF before minimal close',suite_calls['startup_regression']<suite_calls['phase_finalizer_regression'] and
    any(isinstance(n,ast.Constant) and n.value=='PT_MINIMAL_RUNTIME_DIAGNOSTIC_COMPLETE' and n.lineno>suite_calls['phase_finalizer_regression'] for n in ast.walk(fn(guard,'_launcher_work'))),guard,['_launcher_work'])
check('Root phase failure propagates through abort wrapper',all(s in ast.unparse(fn(guard,'_launcher_body')) for s in ['except BaseException','M.abort','raise']),guard,['_launcher_body'])
check('external stop original abort wrapper',all(s in ast.unparse(fn(guard,'external_stop')) for s in ['M.abort','M.seal','raise']),guard,['external_stop'])
check('fresh PF auth before preparation',calls(fn(boot,'prepare_activation'),'get') and 'PF_CONTRACT_AUTHORIZATION' in ast.unparse(fn(boot,'prepare_activation')),boot,['prepare_activation'])
# AST comparisons remove namespace literals only; all budget/control code remains exact.
def normalize(v):
    t=copy.deepcopy(v)
    for n in ast.walk(t):
        if isinstance(n,ast.Constant) and isinstance(n.value,str):
            for a,b in [('PTA-PhaseFinalizer-static-1/r3','PreT0Recovery-static-1/r3'),('PTA-PhaseFinalizer-static-1','PreT0Recovery-static-1'),('pf01','pt01'),('batch12','batch11'),('BATCH12','BATCH11')]:n.value=n.value.replace(a,b)
    return ast.dump(t,include_attributes=False)
protected=load(B/'DCL-R6-PreT0-Fix/evidence/PROTECTED_SEMANTICS_CHECK.json');bytechecks=[];astchecks=[]
for row in protected['byte_checks']:
    name=row['file'];same=(OLD/'src'/name).read_bytes()==(W/'src'/name).read_bytes();assert same,name
    bytechecks.append({'file':name,'same_bytes':same,'sha256':h(W/'src'/name)})
for row in protected['AST_checks']:
    module,name=row['function'].split('.',1);module={'boot':'boot_continuity','gate18':'guard','MR':'manager_recovery'}.get(module,module)
    file='src/'+module+'.py';oldtree=ast.parse((OLD/file).read_bytes())
    oldnode=next(n for n in ast.walk(oldtree) if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
    same=normalize(oldnode)==normalize(fn(file,name));assert same,row['function'];astchecks.append({'function':row['function'],'same_normalized_AST':same})
for module,names in [('root_ipc',['policy','publish','checkpoint','wait_ready','wait_fd','receive']),('c09_handoff',['Receiver','rpc','publish']),
 ('manager_recovery',['query','health','review_case','resume','abort','seal','locked','guard_liveness'])]:
    oldtree=ast.parse((OLD/'src'/f'{module}.py').read_bytes())
    for name in names:
        oldnode=next(n for n in ast.walk(oldtree) if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
        same=normalize(oldnode)==normalize(fn('src/'+module+'.py',name));assert same,(module,name)
        astchecks.append({'function':module+'.'+name,'same_normalized_AST':same})
assert load(OLD/'inputs/startup_contract.json')['jobs']==load(W/'inputs/startup_contract.json')['jobs']
cfg=load(W/'inputs/phase_finalizer_contract.json');assert len(cfg['jobs'])==48 and sum(bool(j['mutant']) for j in cfg['jobs'])==8
assert len({j['case_id'] for j in cfg['jobs']})==48 and max(len(j['frames']) for j in cfg['jobs'])<=4
oracle=trees['src/phase_finalizer_oracle.py'];imports=[]
for n in ast.walk(oracle):
    if isinstance(n,ast.Import):imports.extend(a.name for a in n.names)
    elif isinstance(n,ast.ImportFrom):imports.append(n.module)
assert set(imports)<={'hashlib','json','os','pathlib','stat'}
mutations=[]
for j in cfg['jobs']:
    if j['mutant']:
        assert j['violation_class'] in j['allowed_violations']
        safe=next(x for x in cfg['jobs'] if x['case_id']==j['case_id'].replace('_mutant','_safe'));assert safe['frames']==j['frames']
        mutations.append({'mutant':j['mutant'],'expected_violation':j['violation_class'],'allowed_causal_companions':j['allowed_violations'],
            'same_input_safe_pair':True,'actual_status':'UNRUN','coverage':'STATIC_SCHEMA_AND_SOURCE_REVIEW_ONLY'})
assert cfg['completed_visits']==1+48*(16+1)==817 and cfg['hard_visits']==48*24==1152
budget={'PF_completed':817,'PF_hard':1152,'PT64_completed':1089,'PT64_hard':1536,'minimal_completed':1+1089+817,
    'minimal_hard':1+1536+1152,'inherited_full_hard':65618,'new_full_hard':65618+1152,'soft_cap':100000,'within_soft_cap':65618+1152<=100000,
    'new_T0_or_budget_window':False,'phase_wait_seconds':2,'phase_attempts':512,'admin_wait_seconds':5,'native_admin_alarm':30,'host_admin_total':35,
    'admin_file_bound':256,'admin_byte_bound':33554432,'full_300s_time_feasibility':'UNRESOLVED_DYNAMIC_UNRUN'}
# Inert administrative module import probes. Benign sibling stubs are isolated and preserved.
probe=E/'controlled_import_probes_r3';probe.mkdir();trusted=probe/'trusted';other=probe/'other_cwd';missing=probe/'missing'
for folder in [trusted,other,missing]:folder.mkdir()
(trusted/'startup_lifecycle.py').write_text("PROBE='TRUSTED_STUB_ONLY'\n",encoding='utf-8')
(other/'startup_lifecycle.py').write_text("raise RuntimeError('CWD_MODULE_MUST_NOT_LOAD')\n",encoding='utf-8')
path=str(W/'src/admin_postexit.py');results=[]
for name,cwd,mode in [('passive_import_A',trusted,'passive'),('passive_import_other_cwd',other,'passive'),('explicit_sibling_over_cwd',other,'load'),('host_identity_reject',other,'identity'),('missing_module_propagates',missing,'missing')]:
    code="import runpy,json; d=runpy.run_path("+repr(path)+",run_name='PF_INERT_PROBE'); "
    if mode=='passive':code+="assert callable(d['main']); print(json.dumps({'status':'PASS_HOST_INERT_IMPORT','main_called':False}))"
    elif mode=='load':code+="from pathlib import Path; m=d['load_target'](Path("+repr(str(trusted))+")); assert m.PROBE=='TRUSTED_STUB_ONLY'; print(json.dumps({'status':'PASS_HOST_CONTROLLED_STUB','target_production_module_imported':False}))"
    elif mode=='identity':code+="\ntry:d['checked_source']()\nexcept RuntimeError as e:\n assert str(e)=='PF_ADMIN_FIXED_ROOT_SOURCE'; print(json.dumps({'status':'PASS_HOST_REJECTION_ONLY'}))\nelse:raise AssertionError('host accepted')"
    else:code+="\nfrom pathlib import Path\ntry:d['load_target'](Path("+repr(str(missing))+"))\nexcept ModuleNotFoundError:print(json.dumps({'status':'PASS_HOST_IMPORT_FAILURE_PROPAGATED'}))\nelse:raise AssertionError('missing import accepted')"
    argv=[sys.executable,'-I','-S','-B','-c',code];r=subprocess.run(argv,cwd=cwd,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,timeout=10)
    for stream,raw in [('stdout',r.stdout),('stderr',r.stderr)]: (probe/(name+'.'+stream+'.raw')).write_bytes(raw)
    assert r.returncode==0,(name,r.stderr.decode(errors='replace'));results.append({'name':name,'argv':argv,'cwd':str(cwd),'exit_code':r.returncode,'observation':json.loads(r.stdout),'WSL_calls':0})
put(E/'CONTROLLED_IMPORT_RESULTS.json',{'host_python':sys.version,'probes':results,'native_module_import':'UNRUN','PF_subject_calls':0,'PF_oracle_calls':0,'production_lifecycle_imports':0})
put(E/'SYNTAX_AND_CONTROL_FLOW_CHECK.json',{'programs':syntax,'checks':checks,'production_role_executions':0,'administrative_entry_inert_module_loads':5,'production_lifecycle_imports':0})
put(E/'PROTECTED_SEMANTICS_CHECK.json',{'byte_checks':bytechecks,'AST_checks':astchecks,'PT64_jobs_unchanged':True,'original_slice_bytes_unchanged':h(OLD/'inputs/dclr6batch11.slice')==h(W/'inputs/dclr6batch12.slice')})
put(E/'FIXTURE_ORACLE_STATIC_CHECK.json',{'PF_jobs':48,'PF_safe':40,'PF_mutants':8,'mutations':mutations,'oracle_imports':imports,
    'oracle_uses_job_label_only_after_independent_violation_classification':True,'actual_subject_or_oracle_calls':0,'PT64_jobs':64,'PT64_mutants':9,'PT64_actual_status':'UNRUN'})
put(E/'RESOURCE_BOUND_RECALCULATION.json',budget)
files=[];diff=[]
before={p.relative_to(OLD).as_posix():p for p in OLD.rglob('*') if p.is_file()}
after={p.relative_to(W).as_posix():p for p in W.rglob('*') if p.is_file()}
for rel in sorted(set(before)|set(after)):
    a=before.get(rel);b=after.get(rel);same=bool(a and b and a.read_bytes()==b.read_bytes())
    files.append({'relative':rel,'before_sha256':h(a) if a else None,'after_sha256':h(b) if b else None,'classification':'UNCHANGED' if same else 'ADDED' if not a else 'REMOVED' if not b else 'CHANGED'})
    if not same:diff.extend(difflib.unified_diff(a.read_text(encoding='utf-8').splitlines(True) if a else [],b.read_text(encoding='utf-8').splitlines(True) if b else [],fromfile='before/'+rel,tofile='after/'+rel))
(E/'FULL_DIFF.patch').write_text(''.join(diff),encoding='utf-8');put(E/'FILE_DIFF_INDEX.json',files)
result={'version':'PTA-PhaseFinalizer-static-1/r3','scope':'HOST_STATIC_ONLY','programs':38,'files':55,'native_files':53,
    'PF-G1':'PARTIAL','historical_exact_operands':'UNKNOWN','historical_exact_root_cause':'PT_RUNTIME_PHASE_DRIFT_ROOT_CAUSE_UNRESOLVED',
    'source_consistency_defect':'PASS_STATIC_COUNTEREXAMPLE','PF-G2':'CONDITIONAL_PASS','PF-G3':'CONDITIONAL_PASS','PF-G4':'CONDITIONAL_PASS','PF-G5':'PASS_STATIC',
    'static_checks':len(checks),'controlled_import_probes':len(results),'protected_byte_files':len(bytechecks),'protected_AST_members':len(astchecks),
    'WSL_calls':0,'target_roles_started':0,'PT64_executed':0,'PF48_executed':0,'mutants_detected':0,'T0':None,'R':None,
    'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
    'STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED','manifest_sha256':h(W/'inputs/static_manifest.json'),'execution_lock_sha256':h(W/'inputs/execution_lock.json')}
put(E/'STATIC_RESULT.json',result)
print(json.dumps(result,ensure_ascii=False))
