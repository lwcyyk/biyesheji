"""Administrative preparation only; frozen target programs are never imported."""
from pathlib import Path
import ast, hashlib, json, shutil
from datetime import datetime, timezone

BASE=Path(r'D:\毕业设计\research_main_innovation\decentralized_credential_lifecycle')
OUT=BASE/'DCL-R6-PreT0-A'; E=OUT/'evidence'
FIX=BASE/'DCL-R6-PreT0-Fix'
W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\pt01')
REQUEST=Path(r'C:\Users\a1887\.codex\attachments\ad6f1050-a112-4d02-89c3-e85d10ccc8bd\已粘贴的文本.txt')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def put(p,x):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')

assert not (E/'BASELINE_LOCK.json').exists()
lock=load(FIX/'evidence/STATIC_WORKSPACE_LOCK.json'); rows=lock['files']
assert len(rows)==51 and len([r for r in rows if r['relative'].endswith('.py')])==35
assert {p.relative_to(W).as_posix() for p in W.rglob('*') if p.is_file()}=={r['relative'] for r in rows}
assert sha(W/'inputs/static_manifest.json')=='34c9c4642c4ff8c68183845b66f49f1670efa3349ec82e07d80e8bbabfd86ab7'
assert sha(W/'inputs/execution_lock.json')=='af8de2c099813d2e3018c6d46b2e95b435c2e75a122d32b73b3f96e3c47b58ec'
for row in rows:
    p=W/row['relative']; assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
    assert sha(FIX/'evidence/SOURCE_FINAL_R3'/row['relative'])==row['sha256']
    if p.suffix=='.py':ast.parse(p.read_bytes(),feature_version=(3,12));compile(p.read_bytes(),str(p),'exec')
identity=load(W/'inputs/batch_identity.json'); execution=load(W/'inputs/execution_lock.json')
control=Path(identity['host_control']);assert not control.exists()
assert identity['revision']=='PreT0Recovery-static-1/r3' and identity['runtime_root']=='/var/lib/dcl-r6/batch11'
assert execution['authorization_sources']['receipt']==identity['linux_control']+'/execution_authorization.json'
assert execution['static_revision']==identity['revision']
nav=['CURRENT_VERDICT.md','NEXT_ACTION.md','README.md','DECISION_HISTORY.md']
(E/'navigation_before').mkdir();(E/'commands').mkdir()
for name in nav:shutil.copyfile(BASE/name,E/'navigation_before'/name)
old=load(FIX/'evidence/BASELINE_LOCK.json')
paths={p.resolve() for p in BASE.rglob('*') if p.is_file() and not p.is_relative_to(OUT) and p.name not in nav}
# Preserve every previous protected path, including the historical mispath copy.
paths.update(Path(r['host']).resolve() for r in old['files'])
paths={p for p in paths if p not in {BASE/n for n in nav}}
baseline=[{'host':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(paths)]
put(E/'BASELINE_LOCK.json',{'created_utc':datetime.now(timezone.utc).isoformat(),'files':baseline,'nav':nav,'active_started':False})
shutil.copytree(W,E/'FROZEN_SOURCE_REFERENCE');shutil.copyfile(REQUEST,E/'TASK_REQUEST.txt')
auth=load(FIX/'evidence/PHASE_A_NORMAL_START_AUTHORIZATION_TEMPLATE.json')
for key in ['RootIPC_helpers_explicitly_approved','SingleSession_exec_explicitly_approved','SameProcess_C09_resume_explicitly_approved','Calibrate_only_explicitly_approved','PreT0_diagnostic_explicitly_approved']:auth[key]=True
auth['authorization_text_sha256']=sha(REQUEST);auth['status']='APPROVED_STAGE_A_NORMAL_START'
assert auth['startup_probe_mode']=='NORMAL_START' and auth['PreWindow_abort_injection_explicitly_approved'] is False
control.mkdir(parents=True)
shutil.copyfile(REQUEST,control/'TASK_REQUEST.txt');put(control/'execution_authorization.json',auth)
shutil.copyfile(control/'execution_authorization.json',E/'execution_authorization.json')
put(E/'SOURCE_AND_SCOPE_ADMISSION.json',{'status':'PASS_HOST_STATIC','files':rows,'programs':35,'linux_files':49,
 'revision':identity['revision'],'batch_id':identity['batch_id'],'mode':'NORMAL_START','authorization_text_sha256':sha(REQUEST),
 'authorization_receipt_sha256':sha(control/'execution_authorization.json'),'actual_control':str(control),
 'label_discrepancy':'Frozen identity and code consistently use batch11-r5 control; prose says batch11-r3; runtime is fresh batch11, revision is r3; exact frozen identity retained',
 'mode_basis':'User section 4 highest-priority normal initialization and section 14 immediate ordered execution; smaller common frozen scope NORMAL_START',
 'historic_files':len(baseline),'implementation_gate':'CLOSED','strict_separation_instances':0,'candidate_mechanisms_added':0})
print(json.dumps({'status':'PASS_HOST_STATIC','files':51,'programs':35,'linux_files':49,'history':len(baseline),'mode':'NORMAL_START','actual_control':str(control)},ensure_ascii=False))
