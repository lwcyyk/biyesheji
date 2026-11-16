"""Static source/provenance/ABI checks and pure ELF-note probes; no workload tests."""
from pathlib import Path
import ast,copy,difflib,hashlib,json,re,struct,sys
E=Path(__file__).resolve().parent;B=E.parent.parent;W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\ra01');OLD=E/'SOURCE_BEFORE'
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def put(name,x):(E/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
trees={};syntax=[]
for p in sorted(W.rglob('*.py')):
    t=ast.parse(p.read_bytes(),feature_version=(3,12));compile(p.read_bytes(),str(p),'exec');trees[p.relative_to(W).as_posix()]=t;syntax.append({'file':p.relative_to(W).as_posix(),'status':'PASS_STATIC','role_executed':False})
assert len(syntax)==44 and not list(W.rglob('*.pyc'))
def fn(file,name):return next(n for n in ast.walk(trees[file]) if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
def text(file,name):return ast.unparse(fn(file,name))
def normalize(node):
    t=copy.deepcopy(node)
    for n in ast.walk(t):
        if isinstance(n,ast.Constant) and isinstance(n.value,str):
            for a,z in [('RuntimeAdapt-static-1/r1','TerminalRead-static-1/r1'),('RuntimeAdapt-static-1','TerminalRead-static-1'),('ra01','tr01'),('batch14','batch13'),('BATCH14','BATCH13')]:n.value=n.value.replace(a,z)
    return ast.dump(t,include_attributes=False)
checks=[]
def check(name,condition,file,functions):
    assert condition,name;checks.append({'check':name,'status':'PASS_STATIC','file':file,'lines':{n:fn(file,n).lineno for n in functions}})
file='src/runtime_identity.py';verify=text(file,'verify');package=text(file,'_packages');reader=text(file,'_root_bytes')
check('explicit contract hash from immutable input','runtime_identity_contract_sha256' in verify and 'RA_CONTRACT_DIGEST' in verify,file,['verify'])
check('source/batch profile exact','N.load' in verify and 'RA_CONTRACT_IDENTITY' in verify and 'GLIBC-UBU24-2.39-8.12/1' in verify,file,['verify'])
check('digest and build-id comparisons retained','RA_COMPONENT_DIGEST_OR_BUILD_ID' in verify and '_build_id(raw)' in verify,file,['verify','_build_id'])
check('aliases exact including symlink text',all(x in verify for x in ['RA_ALIAS_IDENTITY','link_text','is_symlink']),file,['verify'])
check('runtime replacement during read rejected','RA_COMPONENT_CHANGED_DURING_READ' in verify and 'st_mtime_ns' in verify,file,['verify'])
check('installed package metadata exact',all(x in package for x in ['install ok installed','Version','Architecture','RA_PACKAGE_IDENTITY','RA_PACKAGE_CATALOG']),file,['_packages'])
check('loader overrides rejected','LD_PRELOAD' in verify and 'LD_LIBRARY_PATH' in verify and 'LD_AUDIT' in verify and 'ld.so.preload' in verify,file,['verify'])
check('loader config hashes checked','RA_LOADER_CONFIGURATION' in verify and 'loader_configuration' in verify,file,['verify'])
check('live map inode/device and deleted state',all(x in verify for x in ['RA_LOADED_OBJECT_MISMATCH','disk_and_loaded_object_match',' (deleted)','os.major','os.minor']),file,['verify'])
check('read-only matcher no filesystem/process mutation',not any(x in ast.unparse(trees[file]) for x in ['O_WRONLY','O_RDWR','O_CREAT','O_TRUNC','write_bytes','write_text','subprocess','reserve_counter','init_counter']),file,['verify','_root_bytes'])
check('bounded clock and boot recheck','begun + 5' in verify and 'RA_BOOT_OR_READ_BOUND' in text(file,'_bound'),file,['verify','_bound'])
check('no arbitrary version range','version' in package and '>' not in package and '<' not in package,file,['_packages'])
check('preflight retains original hard hash reject','BC_ARTIFACT_DRIFT' in text('src/boot_continuity.py','artifact_check') and 'runtime_identity.verify' in text('src/boot_continuity.py','artifact_check'),'src/boot_continuity.py',['artifact_check'])
check('manifest retains runtime hash checks and adds mappings','RUNTIME_CLOSURE_DRIFT' in text('src/guard.py','manifest') and 'full=False, packages=False' in text('src/guard.py','manifest'),'src/guard.py',['manifest'])
check('service prelaunch full package check','full=True, packages=True' in text('src/guard.py','launch_one'),'src/guard.py',['launch_one'])
check('payload postexec packages and own map check','runtime_identity.verify' in text('src/guard.py','kernel_admission') and 'runtime_identity' in text('src/guard.py','kernel_admission'),'src/guard.py',['kernel_admission'])
check('seal runtime check uses raw terminal deadline','runtime_identity.verify' in text('src/guard.py','seal') and "trusted(ROOT / 'inputs/batch_state.json')['deadline']" in text('src/guard.py','seal'),'src/guard.py',['seal'])
admin=text('src/admin_postexit.py','main')
check('admin resources still precede new import',admin.index('setrlimit')<admin.index('runtime_identity.verify')<admin.index('load_target'),'src/admin_postexit.py',['main'])
check('provenance assumptions require explicit approval','RuntimeAdapt_provenance_assumptions_explicitly_approved' in text('src/boot_continuity.py','prepare_activation') and 'RA_NOT_APPROVED' in text('src/guard.py','authorization'),'src/boot_continuity.py',['prepare_activation'])
check('RA suite billed after TR',text('src/guard.py','_launcher_work').index('terminal_regression.run_suite')<text('src/guard.py','_launcher_work').index('runtime_regression.run_suite'),'src/guard.py',['_launcher_work'])
previous=load(B/'DCL-R6-TerminalRead-Fix/evidence/PROTECTED_SEMANTICS_CHECK.json');bytechecks=[];astchecks=[]
for row in previous['byte_checks']:
    file=row['file'];assert (W/file).read_bytes()==(OLD/file).read_bytes(),file;bytechecks.append({'file':file,'same_bytes':True,'sha256':h(W/file)})
for row in previous['AST_checks']:
    module,name=row['function'].split('.',1);module={'boot':'boot_continuity','gate18':'guard','MR':'manager_recovery'}.get(module,module);file='src/'+module+'.py'
    oldnode=next(n for n in ast.walk(ast.parse((OLD/file).read_bytes())) if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
    assert normalize(oldnode)==normalize(fn(file,name)),row['function'];astchecks.append({'function':row['function'],'same_normalized_AST':True})
for file in ['src/root_ipc.py','src/manager_recovery.py','src/terminal_evidence.py','src/terminal_regression.py','src/terminal_oracle.py']:
    assert normalize(trees[file])==normalize(ast.parse((OLD/file).read_bytes())),file
assert (W/'host/startup_finalize.py').read_bytes()==(OLD/'host/startup_finalize.py').read_bytes()
assert (W/'host/windows_entry.py').read_bytes()==(OLD/'host/windows_entry.py').read_bytes()
for name in ['startup_contract.json','phase_finalizer_contract.json','terminal_contract.json']:
    assert load(W/'inputs'/name)['jobs']==load(OLD/'inputs'/name)['jobs']
identity=load(W/'inputs/runtime_identity_contract.json');cfg=load(W/'inputs/runtime_regression_contract.json')
assert len(cfg['jobs'])==32 and sum(bool(j['mutant']) for j in cfg['jobs'])==8 and cfg['completed_visits']==1+32*17==545 and cfg['hard_visits']==768
jobs={j['case_id']:j for j in cfg['jobs']};assert len(jobs)==32
mutations=[]
for job in cfg['jobs']:
    if job['mutant']:
        assert job['frames']==jobs[job['safe_control']]['frames'] and job['expected_violation'] in job['allowed_violations']
        mutations.append({'mutant':job['mutant'],'expected':job['expected_violation'],'allowed':job['allowed_violations'],'safe_control':job['safe_control'],'actual':'UNRUN'})
imports=[]
for n in ast.walk(trees['src/runtime_oracle.py']):
    if isinstance(n,ast.Import):imports.extend(a.name for a in n.names)
    elif isinstance(n,ast.ImportFrom):imports.append(n.module)
assert set(imports)<={'hashlib','json','os','stat','pathlib'}
# A pure parser probe on preserved ELF bytes is a host static compatibility check, not a workload/RA-suite run.
node=copy.deepcopy(fn('src/runtime_identity.py','_build_id'));module=ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[]));namespace={'struct':struct,'RuntimeError':RuntimeError}
exec(compile(module,'RA_BUILD_ID_STATIC_PROBE','exec'),namespace)
abi=load(E/'ELF_ABI_AUDIT.json');export=load(E/'PLATFORM_EXPORT.json');parser_checks=[]
for row in export['files']:
    if row['linux_path'] not in abi['three_components']:continue
    raw=(E/row['relative']).read_bytes();parsed=namespace['_build_id'](raw);expected=abi['three_components'][row['linux_path']]['build_id'];assert parsed==expected
    index=list(abi['three_components']).index(row['linux_path']);notes=(E/'elf_raw'/('%02d-n.stdout.raw'%index)).read_text()
    assert expected in notes;parser_checks.append({'path':row['linux_path'],'build_id':parsed,'native_readelf_and_pure_parser_match':True})
assert len(parser_checks)==3
provenance=load(E/'PROVENANCE_AUDIT.json');decision=load(E/'PROVENANCE_DECISION.json')
assert all(x['gpgv_exit']==0 and x['index_matches_signed_release'] for x in provenance['repositories'])
assert not abi['unresolved_needed'] and not abi['missing_versions'] and decision['static_baseline_admissible']
comparison=load(E/'OLD_NEW_SYMBOL_COMPARISON.json');assert all(not x['removed_version_definitions'] for x in comparison['components'])
budget={'RA_completed':545,'RA_hard':768,'prior_minimal_completed':2588,'new_minimal_completed':3133,'prior_minimal_hard':3649,'new_minimal_hard':4417,
 'prior_full_hard':67730,'new_full_hard':68498,'soft_cap':100000,'soft_margin':31502,'identity_queries_model_visits':0,
 'identity_query_scope':'Bounded5s metadata/hash/map IO, no model traversal or budget mutation; actual new suite billed16+1 per job plus entry1',
 'global_visits':1000000,'wall_seconds':1800,'calibration_seconds':300,'preflight_seconds':120,'AS_bytes':1073741824,'payload_tasks':4,
 'new_identity_role_processes':0,'new_identity_payload_children':0,'full300s_time_feasibility':'UNRESOLVED'}
put('SYNTAX_AND_IDENTITY_CONTROL_CHECK.json',{'programs':syntax,'checks':checks,'role_executions':0,'pure_host_ELF_parser_probes':parser_checks})
put('PROTECTED_SEMANTICS_CHECK.json',{'byte_checks':bytechecks,'AST_checks':astchecks,'whole_RootIPC_MR_Terminal_modules_preserved':True,
 'host_entry_and_finalizer_bytes_preserved':True,'PT_PF_TR_jobs_preserved':True,'slice_bytes_preserved':(W/'inputs/dclr6batch14.slice').read_bytes()==(OLD/'inputs/dclr6batch13.slice').read_bytes()})
put('RUNTIME_REGRESSION_STATIC_CHECK.json',{'jobs':32,'safe':24,'mutants':8,'mutations':mutations,'oracle_imports':imports,'actual_RA_suite_or_oracle_calls':0})
put('RESOURCE_BOUND_RECALCULATION.json',budget)
result={'version':'RuntimeAdapt-static-1/r1','date':'2026-11-13 Asia/Shanghai','RA-1':'CONDITIONAL_PASS','RA-2':'CONDITIONAL_PASS','RA-3':'CONDITIONAL_PASS','RA-4':'PASS_STATIC',
 'source_files':64,'programs':44,'Linux_files_planned':62,'static_checks':len(checks),'protected_byte_files':len(bytechecks),'protected_AST_members':len(astchecks),
 'pure_ELF_parser_host_probes':3,'read_only_WSL_queries':7,'business_dynamic_tests':0,'Launcher_or_service_starts':0,'T0':None,'R':None,
 'RA32_status':'UNRUN','PT_PF_TR_status':'UNRUN_NEW_VERSION','provenance_classification':decision['classification'],'execution_identity_boundary':'No atomic filesystem-to-exec/ongoing privileged-update exclusion; explicit TCB assumption required',
 'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],'STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED'}
put('STATIC_RESULT.json',result)
print(json.dumps(result,ensure_ascii=False))
