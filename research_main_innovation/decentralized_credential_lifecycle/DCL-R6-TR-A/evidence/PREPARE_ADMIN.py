"""Authorized TR-A administrative preparation; target modules are not imported."""
from pathlib import Path
import ast,hashlib,json,shutil,zipfile
from datetime import datetime,timezone
B=Path(r'D:\毕业设计\research_main_innovation\decentralized_credential_lifecycle');O=B/'DCL-R6-TR-A';E=O/'evidence'
F=B/'DCL-R6-TerminalRead-Fix';W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\tr01')
REQUEST=Path(r'C:\Users\a1887\.codex\attachments\643b3072-3bd3-497b-af78-72f936af2ad2\已粘贴的文本.txt')
def load(p):return json.loads(Path(p).read_bytes())
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
assert not (E/'BASELINE_LOCK.json').exists()
rows=load(F/'evidence/STATIC_WORKSPACE_LOCK.json')['files']
assert len(rows)==59 and sum(r['relative'].endswith('.py') for r in rows)==41
assert {p.relative_to(W).as_posix() for p in W.rglob('*') if p.is_file()}=={r['relative'] for r in rows}
for row in rows:
    p=W/row['relative'];assert p.stat().st_size==row['bytes'] and h(p)==row['sha256']
    assert h(F/'evidence/SOURCE_FINAL_R1'/row['relative'])==row['sha256']
    if p.suffix=='.py':ast.parse(p.read_bytes(),feature_version=(3,12));compile(p.read_bytes(),str(p),'exec')
assert h(W/'inputs/static_manifest.json')=='d2a6f4f58d7afd5a14287cea1c86da76d137e80dea2b64b35535fd2b145f7aac'
assert h(W/'inputs/execution_lock.json')=='43f362a064209ff8359e410301017741d787cb3acd272d40c75d447820671878'
identity=load(W/'inputs/batch_identity.json');execution=load(W/'inputs/execution_lock.json');control=Path(identity['host_control'])
assert not control.exists() and identity['batch_id']=='batch13' and identity['revision']=='TerminalRead-static-1/r1'
assert identity['runtime_root']=='/var/lib/dcl-r6/batch13' and identity['source_root']=='/var/lib/dcl-r6/tr01'
assert execution['authorization_sources']['receipt']==identity['linux_control']+'/execution_authorization.json'
assert execution['startup_post_exit_command'][-2]=='/var/lib/dcl-r6/tr01/src/admin_postexit.py'
pt=load(W/'inputs/startup_contract.json');pf=load(W/'inputs/phase_finalizer_contract.json');tr=load(W/'inputs/terminal_contract.json')
for cfg,count,mutants in [(pt,64,9),(pf,48,8),(tr,40,8)]:
    assert len(cfg['jobs'])==count and sum(bool(j['mutant']) for j in cfg['jobs'])==mutants and cfg['driver_prepay']==16
assert 1+64*17==1089 and 1+48*17==817 and 1+40*17==681
assert 1+1089+817+681==2588 and 1+1536+1152+960==3649
assert 66770+960==67730<=100000
put(E/'RESOURCE_ADMISSION_PROOF.json',{'status':'PASS_HOST_BOUND_RECALCULATION','suites':[
 {'name':'PT64','jobs':64,'mutants_included':9,'completed':1089,'hard':1536},
 {'name':'PF48','jobs':48,'mutants_included':8,'completed':817,'hard':1152},
 {'name':'TR40','jobs':40,'mutants_included':8,'completed':681,'hard':960}],
 'C00':1,'jobs_total':152,'mutants_total':25,'minimal_completed':2588,'minimal_hard':3649,'prior_full_hard':66770,
 'new_increment':960,'new_full_hard':67730,'soft_cap':100000,'soft_margin':32270,
 'billing':'Per suite entry1; per job16 prepaid bounded frames/first check +1 Root aggregate audit. Mutants included, no extra free windows.',
 'terminal_native_admin_accounting':'Readonly identity/window/journal/archive inspection and original shutdown/seal are finite administrative IO, no model traversal or budget debit; original total/phase time caps remain',
 'terminal_read_seconds':5,'shared_lock_seconds':2,'shared_attempts':512,'journal_bytes':33554432,'journal_line_bytes':32768,
 'journal_record_bound':'2*original_cap+1 EOF probe','postexit_alarm_seconds':30,'postexit_host_seconds':35,
 'admin_max_files':256,'admin_max_bytes':33554432,'models_allowed':False,'new_time_window':False})
old=load(F/'evidence/BASELINE_LOCK.json');nav=old['nav'];paths={Path(r['host']) for r in old['files']}
paths.update(p for p in B.rglob('*') if p.is_file() and not p.is_relative_to(O));paths.update(p for p in W.rglob('*') if p.is_file());paths.difference_update(B/n for n in nav)
put(E/'BASELINE_LOCK.json',{'created_utc':datetime.now(timezone.utc).isoformat(),'report_date':'2026-11-13 Asia/Shanghai',
 'files':[{'host':str(p),'bytes':p.stat().st_size,'sha256':h(p)} for p in sorted(paths)],'nav':nav,'active_started':False})
(E/'navigation_before').mkdir();(E/'commands').mkdir()
for name in nav:shutil.copyfile(B/name,E/'navigation_before'/name)
shutil.copytree(W,E/'FROZEN_SOURCE_REFERENCE');shutil.copyfile(REQUEST,E/'TASK_REQUEST.txt')
archive_checks=[]
for stage,archive in [('DCL-R6-TerminalRead-Fix','TERMINAL_READ_EVIDENCE.zip'),('DCL-R6-PTA-PF-A','PFA_EVIDENCE.zip'),('DCL-R6-PTA-PhaseFinalizer-Fix','PHASE_FINALIZER_EVIDENCE.zip')]:
    folder=B/stage;q=load(folder/'OUTPUT_MANIFEST.json');items=q.get('files',q) if isinstance(q,dict) else q;errors=[]
    with zipfile.ZipFile(folder/archive) as z:
        for row in items:
            if hashlib.sha256(z.read(row['archive_path'])).hexdigest()!=row['sha256']:errors.append(row['archive_path'])
        entries=len(z.namelist())
    assert not errors;archive_checks.append({'stage':stage,'manifest_rows':len(items),'ZIP_entries':entries,'ZIP_sha256':h(folder/archive),'errors':errors})
put(E/'HISTORICAL_ARCHIVE_CHECK.json',archive_checks)
auth=load(F/'evidence/PHASE_A_NORMAL_START_AUTHORIZATION_TEMPLATE.json')
for key in ['RootIPC_helpers_explicitly_approved','SingleSession_exec_explicitly_approved','SameProcess_C09_resume_explicitly_approved',
 'Calibrate_only_explicitly_approved','PreT0_diagnostic_explicitly_approved','PhaseFinalizer_diagnostic_explicitly_approved','TerminalRead_diagnostic_explicitly_approved']:auth[key]=True
auth['status']='APPROVED_TRA_NORMAL_START_ONLY';auth['authorization_text_sha256']=h(REQUEST)
assert auth['scope']=='PT_STARTUP_DIAGNOSTIC_ONLY' and auth['startup_probe_mode']=='NORMAL_START'
assert auth['Full_conditional_chain_explicitly_approved'] is False and auth['ManagerRecovery_diagnostic_explicitly_approved'] is False and auth['PreWindow_abort_injection_explicitly_approved'] is False
control.mkdir(parents=True);shutil.copyfile(REQUEST,control/'TASK_REQUEST.txt');put(control/'execution_authorization.json',auth)
shutil.copyfile(control/'execution_authorization.json',E/'execution_authorization.json')
put(E/'AUTHORIZATION_RECEIPT_LOCK.json',{'control_directory':str(control),'receipt_sha256':h(control/'execution_authorization.json'),
 'request_sha256':h(REQUEST),'mode':'NORMAL_START','scope':auth['scope'],'compatibility_note':'SameProcess C09 bit is frozen schema acceptance; C09 execution excluded by actual scope'})
put(E/'SOURCE_AND_SCOPE_ADMISSION.json',{'status':'PASS_HOST_STATIC','files':rows,'programs':41,'linux_files':57,'version':identity['revision'],
 'batch_id':identity['batch_id'],'mode':'NORMAL_START','minimal_completed':2588,'minimal_hard':3649,'full_hard':67730,'historic_files':len(paths),
 'control_directory':str(control),'authorization_receipt_sha256':h(control/'execution_authorization.json'),'source_changes':0,
 'observability':'Only frozen emitted timestamps/values are claimed; missing per-field IO/lock/Live administrative RLIMIT telemetry stays UNKNOWN.',
 'IMPLEMENTATION_GATE':'CLOSED','STRICT_SEPARATION_INSTANCES':0})
print(json.dumps({'status':'PASS_HOST_STATIC','files':59,'programs':41,'linux_files':57,'history':len(paths),'jobs':152,'mutants':25,'minimal_hard':3649,'full_hard':67730},ensure_ascii=False))
