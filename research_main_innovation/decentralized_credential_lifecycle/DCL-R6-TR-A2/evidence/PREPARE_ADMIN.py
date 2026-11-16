"""Authorized A2 administrative preparation. No frozen target imports or retries."""
from pathlib import Path
import ast,hashlib,json,shutil,zipfile
from datetime import datetime,timezone
B=Path(r'D:\毕业设计\research_main_innovation\decentralized_credential_lifecycle');O=B/'DCL-R6-TR-A2';E=O/'evidence';F=B/'DCL-R6-RuntimeAdapt-Fix'
W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\ra01');REQUEST=Path(r'C:\Users\a1887\.codex\attachments\b04bba33-56a9-4138-bbb4-be41a733fa07\已粘贴的文本.txt')
def load(p):return json.loads(Path(p).read_bytes())
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
assert not(E/'BASELINE_LOCK.json').exists()
rows=load(F/'evidence/STATIC_WORKSPACE_LOCK.json')['files'];assert len(rows)==64 and sum(r['relative'].endswith('.py') for r in rows)==44
assert {p.relative_to(W).as_posix() for p in W.rglob('*') if p.is_file()}=={r['relative'] for r in rows}
for row in rows:
    p=W/row['relative'];assert p.stat().st_size==row['bytes'] and h(p)==row['sha256'] and h(F/'evidence/SOURCE_FINAL_R1'/row['relative'])==row['sha256']
    if p.suffix=='.py':ast.parse(p.read_bytes(),feature_version=(3,12));compile(p.read_bytes(),str(p),'exec')
assert h(W/'inputs/static_manifest.json')=='738eb2982953971f94019b913f6b302808f9b7a8d29e784038e8e6babb50de89'
assert h(W/'inputs/execution_lock.json')=='691f2503f2db6906552241692db0b27ec6a982a7c738839d99f3cd93f3729da6'
identity=load(W/'inputs/batch_identity.json');l=load(W/'inputs/execution_lock.json');control=Path(identity['host_control'])
assert not control.exists() and identity['batch_id']=='batch14' and identity['revision']=='RuntimeAdapt-static-1/r1'
assert identity['runtime_root']=='/var/lib/dcl-r6/batch14' and identity['source_root']=='/var/lib/dcl-r6/ra01'
assert l['authorization_sources']['receipt']==identity['linux_control']+'/execution_authorization.json'
suites=[]
for name,file,count,mutants,completed,hard in [('PT','startup_contract.json',64,9,1089,1536),('PF','phase_finalizer_contract.json',48,8,817,1152),('TR','terminal_contract.json',40,8,681,960),('RA','runtime_regression_contract.json',32,8,545,768)]:
    cfg=load(W/'inputs'/file);assert len(cfg['jobs'])==count and sum(bool(j['mutant']) for j in cfg['jobs'])==mutants and cfg['driver_prepay']==16 and completed==1+17*count
    suites.append({'name':name,'jobs':count,'mutants_included':mutants,'completed':completed,'hard':hard})
assert 1+sum(s['completed'] for s in suites)==3133 and 1+sum(s['hard'] for s in suites)==4417
assert 67730+768==68498<=100000
put(E/'RESOURCE_ADMISSION_PROOF.json',{'status':'PASS_HOST_BOUND_RECALCULATION','suites':suites,'C00':1,'jobs_total':184,'mutants_total':33,
 'minimal_completed':3133,'minimal_hard':4417,'previous_full_hard':67730,'RA_increment':768,'new_full_hard':68498,'soft_cap':100000,
 'billing':'Each suite entry1, per-job driver16 + allocated Root audit1, mutants included. No post-closure production checker replays.',
 'runtime_terminal_native_admin':'Frozen finite administrative metadata/hash/map/journal/closure/archive IO does not traverse model states or debit R; original time limits remain',
 'identity_seconds':5,'terminal_read_seconds':5,'shared_lock_seconds':2,'shared_attempts':512,'post_alarm_seconds':30,'host_post_seconds':35,
 'AS_bytes':1073741824,'payload_tasks':4,'wall_seconds':1800,'calibration_seconds':300,'startup_TCB_seconds':120,'models_allowed':False,'new_time_window':False})
old=load(F/'evidence/BASELINE_LOCK.json');nav=old['nav'];paths={Path(r['host']) for r in old['files']}
paths.update(p for p in B.rglob('*') if p.is_file() and not p.is_relative_to(O));paths.update(p for p in W.rglob('*') if p.is_file());paths.difference_update(B/n for n in nav)
put(E/'BASELINE_LOCK.json',{'created_utc':datetime.now(timezone.utc).isoformat(),'report_date':'2026-11-13 Asia/Shanghai',
 'files':[{'host':str(p),'bytes':p.stat().st_size,'sha256':h(p)} for p in sorted(paths)],'nav':nav,'active_started':False})
(E/'navigation_before').mkdir();(E/'commands').mkdir()
for name in nav:shutil.copyfile(B/name,E/'navigation_before'/name)
shutil.copytree(W,E/'FROZEN_SOURCE_REFERENCE');shutil.copyfile(REQUEST,E/'TASK_REQUEST.txt')
checks=[]
for stage,archive in [('DCL-R6-RuntimeAdapt-Fix','RUNTIME_ADAPT_EVIDENCE.zip'),('DCL-R6-TR-A','TRA_EVIDENCE.zip'),('DCL-R6-TerminalRead-Fix','TERMINAL_READ_EVIDENCE.zip')]:
    folder=B/stage;q=load(folder/'OUTPUT_MANIFEST.json');items=q.get('files',q) if isinstance(q,dict) else q;errors=[]
    with zipfile.ZipFile(folder/archive) as z:
        for row in items:
            if hashlib.sha256(z.read(row['archive_path'])).hexdigest()!=row['sha256']:errors.append(row['archive_path'])
        count=len(z.namelist())
    assert not errors;checks.append({'stage':stage,'manifest_rows':len(items),'ZIP_entries':count,'ZIP_sha256':h(folder/archive),'errors':errors})
put(E/'HISTORICAL_ARCHIVE_CHECK.json',checks)
auth=load(F/'evidence/TR_A2_AUTHORIZATION_TEMPLATE.json')
for name in ['RootIPC_helpers_explicitly_approved','SingleSession_exec_explicitly_approved','SameProcess_C09_resume_explicitly_approved',
 'Calibrate_only_explicitly_approved','PreT0_diagnostic_explicitly_approved','PhaseFinalizer_diagnostic_explicitly_approved','TerminalRead_diagnostic_explicitly_approved',
 'RuntimeAdapt_diagnostic_explicitly_approved','RuntimeAdapt_provenance_assumptions_explicitly_approved']:auth[name]=True
auth['status']='APPROVED_TRA2_NORMAL_START_ONLY';auth['authorization_text_sha256']=h(REQUEST)
assert auth['scope']=='PT_STARTUP_DIAGNOSTIC_ONLY' and auth['startup_probe_mode']=='NORMAL_START'
assert not auth['Full_conditional_chain_explicitly_approved'] and not auth['ManagerRecovery_diagnostic_explicitly_approved'] and not auth['PreWindow_abort_injection_explicitly_approved']
control.mkdir(parents=True);shutil.copyfile(REQUEST,control/'TASK_REQUEST.txt');put(control/'execution_authorization.json',auth);shutil.copyfile(control/'execution_authorization.json',E/'execution_authorization.json')
put(E/'AUTHORIZATION_RECEIPT_LOCK.json',{'control_directory':str(control),'receipt_sha256':h(control/'execution_authorization.json'),'request_sha256':h(REQUEST),
 'mode':'NORMAL_START','scope':auth['scope'],'provenance_basis':'User section3.2 permits frozen TCB-conditional validation; keep lack of independent new.deb payload and path-to-exec atomicity boundary',
 'compatibility_note':'SameProcess_C09 bit satisfies frozen schema; actual C09/MR dispatch excluded by minimum scope'})
put(E/'SOURCE_AND_SCOPE_ADMISSION.json',{'status':'PASS_HOST_STATIC','files':rows,'programs':44,'linux_files':62,'version':identity['revision'],
 'batch_id':identity['batch_id'],'mode':'NORMAL_START','minimal_completed':3133,'minimal_hard':4417,'full_hard':68498,'historic_files':len(paths),
 'control_directory':str(control),'authorization_receipt_sha256':h(control/'execution_authorization.json'),'source_changes':0,
 'RUNTIME_PROVENANCE':'CONDITIONAL_ROOT_DPKG_KEYRING','payload_reconstruction':False,'path_to_exec_atomicity':'UNRESOLVED',
 'IMPLEMENTATION_GATE':'CLOSED','STRICT_SEPARATION_INSTANCES':0})
print(json.dumps({'status':'PASS_HOST_STATIC','files':64,'programs':44,'linux_files':62,'history':len(paths),'jobs':184,'mutants':33,'minimal_hard':4417,'full_hard':68498},ensure_ascii=False))
