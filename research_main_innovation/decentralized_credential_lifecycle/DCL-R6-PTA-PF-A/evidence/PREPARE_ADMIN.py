"""Authorized administrative preparation; never imports frozen target programs."""
from pathlib import Path
import ast,hashlib,json,shutil,zipfile
from datetime import datetime,timezone
B=Path(r'D:\毕业设计\research_main_innovation\decentralized_credential_lifecycle')
O=B/'DCL-R6-PTA-PF-A';E=O/'evidence';F=B/'DCL-R6-PTA-PhaseFinalizer-Fix'
W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\pf01')
REQUEST=Path(r'C:\Users\a1887\.codex\attachments\a10dc94c-a87f-4b4e-8236-db571af5b262\已粘贴的文本.txt')
def load(p):return json.loads(Path(p).read_bytes())
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
assert not (E/'BASELINE_LOCK.json').exists()
lock=load(F/'evidence/STATIC_WORKSPACE_LOCK.json');rows=lock['files']
assert len(rows)==55 and sum(r['relative'].endswith('.py') for r in rows)==38
assert {p.relative_to(W).as_posix() for p in W.rglob('*') if p.is_file()}=={r['relative'] for r in rows}
for row in rows:
    p=W/row['relative'];assert p.stat().st_size==row['bytes'] and h(p)==row['sha256']
    assert h(F/'evidence/SOURCE_FINAL_R3'/row['relative'])==row['sha256']
    if p.suffix=='.py':ast.parse(p.read_bytes(),feature_version=(3,12));compile(p.read_bytes(),str(p),'exec')
assert h(W/'inputs/static_manifest.json')=='31be4cdcf2bebff97b8eca38fe1b4b606b7499921ff6babd1da23fd2c6f91c1d'
assert h(W/'inputs/execution_lock.json')=='31c6fe1ba61cd9acbc4c4c1d62f5f641a0d0be8c0ac6ca816df88cbebec0b0a7'
identity=load(W/'inputs/batch_identity.json');execution=load(W/'inputs/execution_lock.json');m=load(W/'inputs/static_manifest.json')
control=Path(identity['host_control']);assert not control.exists()
assert identity['batch_id']=='batch12' and identity['revision']=='PTA-PhaseFinalizer-static-1/r3'
assert identity['runtime_root']=='/var/lib/dcl-r6/batch12' and identity['source_root']=='/var/lib/dcl-r6/pf01'
assert execution['authorization_sources']['receipt']==identity['linux_control']+'/execution_authorization.json'
assert execution['startup_post_exit_command'][-2]=='/var/lib/dcl-r6/pf01/src/admin_postexit.py'
pt=load(W/'inputs/startup_contract.json');pf=load(W/'inputs/phase_finalizer_contract.json')
assert len(pt['jobs'])==64 and sum(bool(j['mutant']) for j in pt['jobs'])==9
assert len(pf['jobs'])==48 and sum(bool(j['mutant']) for j in pf['jobs'])==8
assert pt['driver_prepay']==pf['driver_prepay']==16
assert pt['regression_completed_visits']==1+64*(16+1)==1089
assert pf['completed_visits']==1+48*(16+1)==817
assert 1+pt['regression_hard_visits']+pf['hard_visits']==2689
assert 65618+pf['hard_visits']==66770<=100000
budget={'status':'PASS_HOST_BOUND_RECALCULATION','PT64':{'jobs':64,'mutants_included':9,'completed':1089,'hard':1536},
 'PF48':{'jobs':48,'mutants_included':8,'completed':817,'hard':1152},'C00':{'completed':1,'hard':1},
 'total_jobs':112,'total_mutants':17,'minimal_completed':1907,'minimal_hard':2689,'full_inherited_hard':65618,
 'PF_hard_increment':1152,'full_new_hard':66770,'calibration_soft_visits':100000,'remaining_soft_margin':33230,
 'failure_and_cleanup':'Frozen abort/stop/seal and read-only admin do not traverse model/test search states or debit additional visits; existing finite TCB bounds unchanged',
 'oracle_accounting':'Each job16 prepaid includes its bounded synthetic frames/first check; separate per-job Root audit1 and per-suite entry1; no extra unbilled replay',
 'observational_IO':'Source/auth/process/cgroup/hash/closure IO are frozen finite administrative operations, not model visits',
 'phase_lock_seconds':2,'phase_lock_attempts':512,'postexit_alarm_seconds':30,'postexit_host_seconds':35,
 'dynamic_wall_and_memory':'UNMEASURED_BEFORE_EXECUTION','models_authorized':False}
put(E/'RESOURCE_ADMISSION_PROOF.json',budget)
old=load(F/'evidence/BASELINE_LOCK.json');nav=old['nav']
paths={Path(r['host']) for r in old['files']}
paths.update(p for p in B.rglob('*') if p.is_file() and not p.is_relative_to(O))
paths.update(p for p in W.rglob('*') if p.is_file());paths.difference_update(B/n for n in nav)
put(E/'BASELINE_LOCK.json',{'created_utc':datetime.now(timezone.utc).isoformat(),'files':[{'host':str(p),'bytes':p.stat().st_size,'sha256':h(p)} for p in sorted(paths)],'nav':nav,'active_started':False})
(E/'navigation_before').mkdir();(E/'commands').mkdir()
for name in nav:shutil.copyfile(B/name,E/'navigation_before'/name)
shutil.copytree(W,E/'FROZEN_SOURCE_REFERENCE');shutil.copyfile(REQUEST,E/'TASK_REQUEST.txt')
archive_checks=[]
for stage,archive in [('DCL-R6-PTA-PhaseFinalizer-Fix','PHASE_FINALIZER_EVIDENCE.zip'),('DCL-R6-PreT0-A','PTA_EVIDENCE.zip'),('DCL-R6-MR-A','MRA_EVIDENCE.zip')]:
    folder=B/stage;q=load(folder/'OUTPUT_MANIFEST.json');items=q.get('files',q) if isinstance(q,dict) else q;errors=[]
    with zipfile.ZipFile(folder/archive) as z:
        for row in items:
            if hashlib.sha256(z.read(row['archive_path'])).hexdigest()!=row['sha256']:errors.append(row['archive_path'])
        entries=len(z.namelist())
    assert not errors;archive_checks.append({'stage':stage,'manifest_rows':len(items),'ZIP_entries':entries,'ZIP_sha256':h(folder/archive),'errors':errors})
put(E/'HISTORICAL_ARCHIVE_CHECK.json',archive_checks)
auth=load(F/'evidence/PHASE_A_NORMAL_START_AUTHORIZATION_TEMPLATE.json')
for name in ['RootIPC_helpers_explicitly_approved','SingleSession_exec_explicitly_approved','SameProcess_C09_resume_explicitly_approved',
    'Calibrate_only_explicitly_approved','PreT0_diagnostic_explicitly_approved','PhaseFinalizer_diagnostic_explicitly_approved']:auth[name]=True
auth['status']='APPROVED_PFA_NORMAL_START_ONLY';auth['authorization_text_sha256']=h(REQUEST)
assert auth['scope']=='PT_STARTUP_DIAGNOSTIC_ONLY' and auth['startup_probe_mode']=='NORMAL_START'
assert auth['Full_conditional_chain_explicitly_approved'] is False and auth['ManagerRecovery_diagnostic_explicitly_approved'] is False
assert auth['PreWindow_abort_injection_explicitly_approved'] is False
control.mkdir(parents=True);shutil.copyfile(REQUEST,control/'TASK_REQUEST.txt');put(control/'execution_authorization.json',auth)
shutil.copyfile(control/'execution_authorization.json',E/'execution_authorization.json')
put(E/'AUTHORIZATION_RECEIPT_LOCK.json',{'control_directory':str(control),'receipt_sha256':h(control/'execution_authorization.json'),
 'request_sha256':h(REQUEST),'mode':'NORMAL_START','scope':auth['scope'],'compatibility_flags':'SameProcess_C09 flag is frozen schema compatibility; actual C09 dispatch excluded by scope'})
put(E/'SOURCE_AND_SCOPE_ADMISSION.json',{'status':'PASS_HOST_STATIC','files':rows,'programs':38,'linux_files':53,'version':identity['revision'],
 'batch_id':identity['batch_id'],'mode':'NORMAL_START','minimal_hard':2689,'full_hard':66770,'historic_files':len(paths),
 'authorization_receipt_sha256':h(control/'execution_authorization.json'),'control_directory':str(control),'source_changes':0,
 'observability_limits':['Per-call successful lock acquire/release times are not emitted by frozen code','Module-import start/cwd/sys.path and live AS have no separate telemetry','Preserve UNKNOWN where no actual receipt exists; never infer full dynamic proof from code alone'],
 'IMPLEMENTATION_GATE':'CLOSED','STRICT_SEPARATION_INSTANCES':0})
print(json.dumps({'status':'PASS_HOST_STATIC','files':55,'programs':38,'linux_files':53,'history':len(paths),'jobs':112,'mutants':17,'minimal_hard':2689,'full_hard':66770},ensure_ascii=False))
