"""Static AST/byte/schema checks only. No production module, fixture or oracle runs."""
from pathlib import Path
import ast,copy,difflib,hashlib,json,sys
E=Path(__file__).resolve().parent;B=E.parent.parent;W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\tr01');OLD=E/'SOURCE_BEFORE'
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def put(name,x):(E/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
trees={};syntax=[]
for p in sorted(W.rglob('*.py')):
    t=ast.parse(p.read_bytes(),feature_version=(3,12));compile(p.read_bytes(),str(p),'exec');trees[p.relative_to(W).as_posix()]=t
    syntax.append({'file':p.relative_to(W).as_posix(),'status':'PASS_STATIC','python312_grammar':True,'executed':False})
assert len(syntax)==41 and not list(W.rglob('*.pyc'))
def function(file,name):return next(n for n in ast.walk(trees[file]) if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
def source(file,name):return ast.unparse(function(file,name))
def callnames(node):
    return [n.func.id if isinstance(n.func,ast.Name) else n.func.attr for n in ast.walk(node) if isinstance(n,ast.Call) and isinstance(n.func,(ast.Name,ast.Attribute))]
def normalize(node):
    t=copy.deepcopy(node)
    for n in ast.walk(t):
        if isinstance(n,ast.Constant) and isinstance(n.value,str):
            for a,z in [('TerminalRead-static-1/r1','PTA-PhaseFinalizer-static-1/r3'),('TerminalRead-static-1','PTA-PhaseFinalizer-static-1'),('tr01','pf01'),('batch13','batch12'),('BATCH13','BATCH12')]:n.value=n.value.replace(a,z)
    return ast.dump(t,include_attributes=False)
checks=[]
def check(name,condition,file,functions):
    assert condition,name;checks.append({'check':name,'status':'PASS_STATIC','file':file,'lines':{n:function(file,n).lineno for n in functions}})
tfile='src/terminal_evidence.py';tf=trees[tfile];functions={n.name:n for n in tf.body if isinstance(n,ast.FunctionDef)}
reader=functions['read_terminal_evidence'];reachable=set();queue=['read_terminal_evidence']
while queue:
    name=queue.pop()
    if name in reachable:continue
    reachable.add(name)
    queue.extend(n for n in callnames(functions[name]) if n in functions and n not in reachable)
bad={'write','write_bytes','write_text','mkdir','makedirs','put','atomic','publish','reserve_counter','init_counter','launcher','launch_one','start','Popen','run','state','root_checkpoint','set_phase','_set_phase','_set_phase_locked'}
seen={n for name in reachable for n in callnames(functions[name])}
check('terminal call graph excludes active state and mutation',not seen&bad,tfile,['read_terminal_evidence','_context'])
check('active wrapper remains strict','G.root_checkpoint()' in source(tfile,'check_active_runtime'),tfile,['check_active_runtime'])
open_flags=source(tfile,'_open')
check('all original opens are read-only no-create','O_RDONLY' in open_flags and not any(x in open_flags for x in ['O_WRONLY','O_RDWR','O_CREAT','O_TRUNC']),tfile,['_open'])
check('terminal uses read-only directories no Store creation','RI.directories(G)' in source(tfile,'read_terminal_evidence') and 'Store' not in seen,tfile,['read_terminal_evidence'])
check('shared kernel lock finite','LOCK_SH' in source(tfile,'_shared') and 'range(512)' in source(tfile,'_shared') and 'G.now() + 2' in source(tfile,'_shared'),tfile,['_shared'])
text=source(tfile,'read_terminal_evidence')
check('counter then phase lock order',text.index('_shared(G, counter, until)')<text.index('_shared(G, phasefd, until)'),tfile,['read_terminal_evidence'])
check('fixed identity/receipt/source binding',all(x in source(tfile,'_context') for x in ['TR_NAMESPACE','TR_AUTHORIZATION_BINDING','static_manifest_sha256','execution_lock_sha256','authorization_text_sha256','source_hashes']),tfile,['_context'])
check('historical original boot retained',all(x in text for x in ['original_boot_id','observation_boot_id','HISTORICAL_AUDIT']),tfile,['read_terminal_evidence'])
check('historical mode never yields current seal exit eligibility',"purpose == 'HISTORICAL_AUDIT'" in source(tfile,'_exit_evidence') and "'seal_exit_ready': False" in source(tfile,'_exit_evidence'),tfile,['_exit_evidence'])
check('no default window fields',"{k: s[k] for k in ('T0', 'deadline', 'stop_at')}" in text and 's.get(' not in text,tfile,['read_terminal_evidence'])
check('original deadline relations preserved',all(x in text for x in ['- 1800','- 1740','math.isfinite']),tfile,['read_terminal_evidence'])
check('phase sequence/digest binding',all(x in text for x in ['phase_record_sha256','initialization_id','TR_PHASE_EVIDENCE','cp[\'window\'] != window']),tfile,['read_terminal_evidence'])
check('counter identity and committed final intent',all(x in text for x in ['BRNGv001','TR_COUNTER_IDENTITY','TR_BUDGET_INTENT','TR_FINAL_INTENT_JOURNAL']),tfile,['read_terminal_evidence'])
check('journal streaming finite and contiguous',all(x in source(tfile,'_journal') for x in ['range(2 * cap + 1)','readline(32769)','33554432','TR_JOURNAL_COUNTER_MISMATCH','TR_JOURNAL_PAIR','TR_JOURNAL_INTEGER_FIELDS']),tfile,['_journal'])
check('missing records never constructed','FileNotFoundError' not in source(tfile,'_json') and 'O_CREAT' not in open_flags,tfile,['_json','_open'])
check('exit identity plus real waitpid tuple',all(x in source(tfile,'_exit_evidence') for x in ['waitstatus_to_exitcode','TR_EXIT_ROLE_IDENTITY','TR_WAITPID_IDENTITY_OR_STATUS','G._empty()']),tfile,['_exit_evidence'])
check('UNKNOWN not derived from group empty',"except FileNotFoundError:\n" in text and "internal = 'UNKNOWN'" in text and 'CLOSED_CLEANUP_CONFIRMED' not in text,tfile,['read_terminal_evidence'])
check('native stream/current-evidence checks bounded',all(x in source(tfile,'_native_artifact') for x in ['TR_NATIVE_STREAM_DIGEST','TR_NATIVE_CURRENT_EVIDENCE','TR_NATIVE_UNCOMPRESSED_BOUND','257','33554432']),tfile,['_native_artifact'])
check('native four-way separation leaves no implicit success',all(x in source(tfile,'terminal_policy') for x in ['NATIVE_SEAL_COMPLETED','NATIVE_SEAL_FAILED','NATIVE_SEAL_UNRESOLVED','native_verified','native_ready']),tfile,['terminal_policy'])
life='src/startup_lifecycle.py';guard='src/guard.py'
app=source(life,'seal_applicability')
check('seal applicability routes independent reader',"T.read_terminal_evidence(G, 'REVIEW')" in app and 'runtime_checkpoint(' not in app,life,['seal_applicability'])
check('pure prewindow remains not-applicable','NATIVE_SEAL_NOT_APPLICABLE' in app and 'runtime_intent_exists' in app,life,['seal_applicability'])
check('terminal error retained by caller','terminal_read_failure' in source(life,'defer_startup_seal') and '_SEAL_READ_FAILURE' in app,life,['seal_applicability','defer_startup_seal'])
seal=source(guard,'seal')
check('review follows original stopper wait',seal.index('EXTERNAL_STOP_NOT_CLOSED')<seal.index("'NATIVE_SEAL'"),guard,['seal'])
check('active closed denial recorded not ignored',all(x in seal for x in ['check_active_runtime','TR_ACTIVE_GUARD_ACCEPTED_CLOSED','active_guard_denial','IPC_CLOSED_DOMINATES']),guard,['seal'])
check('summary write outside readonly API','terminal_seal_review.json' in seal and 'exclusive=True' in seal and 'terminal_seal_review' not in text,guard,['seal'])
check('native review cannot directly complete archive',"'PRE_NATIVE_ARCHIVE_READ_ONLY_REVIEW'" in seal and seal.index('terminal_seal_review.json')<seal.index('ZipFile'),guard,['seal'])
suite=source(guard,'_launcher_work')
check('new suite after original two suites',suite.index('startup_regression.run_suite')<suite.index('phase_finalizer_regression.run_suite')<suite.index('terminal_regression.run_suite')<suite.index('PT_MINIMAL_RUNTIME_DIAGNOSTIC_COMPLETE'),guard,['_launcher_work'])
check('TR auth before active preparation','TR_CONTRACT_AUTHORIZATION' in source('src/boot_continuity.py','prepare_activation'),'src/boot_continuity.py',['prepare_activation'])
# Preserve original active guards, budget core, MR semantics, RootIPC and finalizer.
previous=load(B/'DCL-R6-PTA-PhaseFinalizer-Fix/evidence/PROTECTED_SEMANTICS_CHECK.json');bytes_ok=[];asts=[]
for row in previous['byte_checks']:
    file='src/'+row['file'];assert (W/file).read_bytes()==(OLD/file).read_bytes(),file;bytes_ok.append({'file':file,'same_bytes':True,'sha256':h(W/file)})
for row in previous['AST_checks']:
    name=row['function'];module,member=name.split('.',1);module={'boot':'boot_continuity','gate18':'guard','MR':'manager_recovery'}.get(module,module);file='src/'+module+'.py'
    oldtree=ast.parse((OLD/file).read_bytes());oldnode=next(n for n in ast.walk(oldtree) if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==member)
    assert normalize(oldnode)==normalize(function(file,member)),name;asts.append({'function':name,'same_normalized_AST':True})
active_phase=['_phase_deadline','_cancel','_phase_guard','_set_phase_locked','_set_phase','phase_policy','phase_snapshot_policy','runtime_ready','_runtime_checkpoint_locked','runtime_checkpoint','_commit_phase','arm','require_work']
oldlife=ast.parse((OLD/life).read_bytes())
for member in active_phase:
    oldnode=next(n for n in oldlife.body if isinstance(n,ast.FunctionDef) and n.name==member)
    assert normalize(oldnode)==normalize(function(life,member)),member;asts.append({'function':'startup_lifecycle.'+member,'same_normalized_AST':True})
for member in ['state','validate_state_document','root_checkpoint','init_counter','_counter_lock','_reserve']:
    oldnode=next(n for n in ast.parse((OLD/guard).read_bytes()).body if isinstance(n,ast.FunctionDef) and n.name==member)
    assert normalize(oldnode)==normalize(function(guard,member)),member
for file in ['src/root_ipc.py','src/manager_recovery.py']:
    assert normalize(ast.parse((OLD/file).read_bytes()))==normalize(trees[file]),file
assert (W/'host/startup_finalize.py').read_bytes()==(OLD/'host/startup_finalize.py').read_bytes()
assert (W/'host/windows_entry.py').read_bytes()==(OLD/'host/windows_entry.py').read_bytes()
assert normalize(trees['src/admin_postexit.py'])==normalize(ast.parse((OLD/'src/admin_postexit.py').read_bytes()))
for file in ['startup_contract.json','phase_finalizer_contract.json']:
    assert load(W/'inputs'/file)['jobs']==load(OLD/'inputs'/file)['jobs']
cfg=load(W/'inputs/terminal_contract.json');assert len(cfg['jobs'])==40 and sum(bool(j['mutant']) for j in cfg['jobs'])==8
assert len({j['case_id'] for j in cfg['jobs']})==40
mutations=[];jobs={j['case_id']:j for j in cfg['jobs']}
for job in cfg['jobs']:
    assert len(job['frames'])<=4
    if job['mutant']:
        assert jobs[job['safe_control']]['frames']==job['frames']
        assert job['expected_violation'] in job['allowed_violations']
        mutations.append({'mutant':job['mutant'],'expected_violation':job['expected_violation'],'safe_control':job['safe_control'],'actual_status':'UNRUN','allowed_violations':job['allowed_violations']})
oracle=trees['src/terminal_oracle.py'];imports=[]
for n in ast.walk(oracle):
    if isinstance(n,ast.Import):imports.extend(a.name for a in n.names)
    elif isinstance(n,ast.ImportFrom):imports.append(n.module)
assert set(imports)<={'hashlib','json','os','pathlib','stat'}
assert cfg['completed_visits']==1+40*(16+1)==681 and cfg['hard_visits']==960
budget={'TR_completed':681,'TR_hard':960,'old_minimal_completed':1907,'new_minimal_completed':2588,'old_minimal_hard':2689,'new_minimal_hard':3649,
 'old_full_hard':66770,'new_full_hard':67730,'soft_cap':100000,'within_soft_cap':67730<=100000,
 'read_interface_semantic_visit_debits':0,'read_interface_reason':'No model search or execution grants; readonly administrative scan never updates R',
 'read_bound_seconds':5,'each_shared_lock_seconds':2,'shared_lock_attempts':512,'journal_bytes':33554432,'journal_line_bytes':32768,
 'journal_record_bound':'2*original_cap+1 EOF probe','native_archive_entries_bound':257,'native_uncompressed_bytes':33554432,
 'global_visits':1000000,'wall_seconds':1800,'calibration_seconds':300,'preflight_seconds':120,'AS_bytes':1073741824,'payload_tasks':4,
 'finalizer_caps_unchanged':{'native_alarm_seconds':30,'host_seconds':35,'files':256,'bytes':33554432},'time_feasibility':'UNRESOLVED_DYNAMIC_UNRUN'}
put('SYNTAX_CONTROL_FLOW_READONLY_CHECK.json',{'programs':syntax,'checks':checks,'reader_reachable_functions':sorted(reachable),'reader_call_names':sorted(seen),'forbidden_mutation_calls_found':[],'target_executions':0})
put('PROTECTED_SEMANTICS_CHECK.json',{'byte_checks':bytes_ok,'AST_checks':asts,'active_guard_and_budget_members':6,'whole_RootIPC_and_MR_AST_identical':True,
 'host_finalizer_bytes_identical':True,'host_entry_bytes_identical':True,'admin_bootstrap_normalized_AST_identical':True,'PT64_and_PF48_jobs_identical':True,
 'slice_bytes_identical':(W/'inputs/dclr6batch13.slice').read_bytes()==(OLD/'inputs/dclr6batch12.slice').read_bytes()})
put('FIXTURE_ORACLE_STATIC_CHECK.json',{'TR_jobs':40,'safe':32,'mutants':8,'mutations':mutations,'oracle_imports':imports,'static_pair_and_schema_check':'PASS_STATIC','actual_subject_or_oracle_runs':0})
put('RESOURCE_BOUND_RECALCULATION.json',budget)
before={p.relative_to(OLD).as_posix():p for p in OLD.rglob('*') if p.is_file()};after={p.relative_to(W).as_posix():p for p in W.rglob('*') if p.is_file()};diff=[];rows=[]
for rel in sorted(set(before)|set(after)):
    a=before.get(rel);b=after.get(rel);same=bool(a and b and a.read_bytes()==b.read_bytes())
    rows.append({'relative':rel,'before_sha256':h(a) if a else None,'after_sha256':h(b) if b else None,'classification':'UNCHANGED' if same else 'ADDED' if not a else 'REMOVED' if not b else 'CHANGED'})
    if not same:diff.extend(difflib.unified_diff(a.read_text(encoding='utf-8').splitlines(True) if a else [],b.read_text(encoding='utf-8').splitlines(True) if b else [],fromfile='before/'+rel,tofile='after/'+rel))
put('FILE_DIFF_INDEX.json',rows);(E/'FULL_DIFF.patch').write_text(''.join(diff),encoding='utf-8')
result={'version':'TerminalRead-static-1/r1','report_date':'2026-11-13 Asia/Shanghai','TR-G1':'PASS_STATIC','TR-G2':'CONDITIONAL_PASS','TR-G3':'PARTIAL','TR-G4':'PASS_STATIC',
 'programs':41,'files':59,'Linux_files_planned':57,'static_checks':len(checks),'protected_byte_files':len(bytes_ok),'protected_AST_members':len(asts),
 'TR40_status':'UNRUN','PT64_status':'UNRUN_NEW_VERSION','PF48_status':'UNRUN_NEW_VERSION','WSL_calls':0,'source_target_executions':0,'T0':None,'R':None,
 'historical_native_seal':'NATIVE_SEAL_UNRESOLVED','historical_internal':'UNKNOWN','historical_auto_admin':'ADMIN_EVIDENCE_SEALED',
 'native_success_after_fix':'UNRESOLVED_DYNAMIC_UNRUN','RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
 'IMPLEMENTATION_GATE':'CLOSED','STRICT_SEPARATION_INSTANCES':0}
put('STATIC_RESULT.json',result)
print(json.dumps(result,ensure_ascii=False))
