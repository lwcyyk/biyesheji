"""Hash DAG and unapproved next-run locks; performs host file IO only."""
from pathlib import Path
import hashlib,json,shutil
W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\pf01');E=Path(__file__).resolve().parent;O=E.parent;B=O.parent
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def put(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=load(W/'inputs/static_manifest.json');l=load(W/'inputs/execution_lock.json')
# Current aggregate totals change; component historical deltas stay labelled as inherited.
def aggregates(v):
    if isinstance(v,dict):
        for k,item in v.items():
            if k in ('full_calibration_hard','full_calibration_hard_visits','calibration_hard_bound','calibration_hard_visit_upper_bound','calibration_total_max_visits','new_calibration_hard') and item==65618:v[k]=66770
            else:aggregates(item)
    elif isinstance(v,list):
        for item in v:aggregates(item)
aggregates(m);aggregates(l)
for obj in [m,l]:obj['freeze_revision']=3;obj['export_lock_revision']='PF-r3'
m['profile_approval']='PF_HOST_STATIC_ONLY; native deployment/import/diagnosis/execution require independent authorization'
m['input_binding_scope']='batch12-r3; PT64 unchanged jobs plus PF48; scope authority remains the exact future receipt'
m['phase_finalizer_delta']={'jobs':48,'safe':40,'mutants':8,'completed_visits':817,'hard_visits':1152,
    'normal_minimal_completed':1907,'normal_minimal_hard':2689,'full_calibration_hard':66770,
    'phase_lock_seconds':2,'phase_lock_attempts':512,'admin_quiescence_seconds':5,'admin_quiescence_samples':128,
    'native_admin_alarm_seconds':30,'host_postexit_seconds':35,'dynamic_status':'UNRUN'}
m['startup_delta']['normal_minimal_visits_hard']=2689
m['source_hashes']={p.name:h(p) for p in sorted((W/'src').glob('*.py'))}
for p in sorted((W/'inputs').iterdir()):
    if p.is_file() and p.name not in ('static_manifest.json','execution_lock.json'):
        m['bound_inputs']['inputs/'+p.name]=h(p)
for rel,digest in m['bound_inputs'].items():
    stem=Path(rel).stem;key=stem+'_sha256'
    if key in m or stem in ('startup_contract','phase_finalizer_contract'):m[key]=digest
m['unit_template_hashes']['slice']=h(W/'inputs/dclr6batch12.slice')
put(W/'inputs/static_manifest.json',m)
l['static_manifest_sha256']=h(W/'inputs/static_manifest.json')
for key in list(l):
    if key.endswith('_sha256') and key in m:l[key]=m[key]
l['windows_entry_sha256']=h(W/'host/windows_entry.py');l['startup_host_finalizer_sha256']=h(W/'host/startup_finalize.py')
l['phase_finalizer_contract_sha256']=h(W/'inputs/phase_finalizer_contract.json')
l['unit_slice_sha256']=h(W/'inputs/dclr6batch12.slice')
l['startup_post_exit_command'][-2]='/var/lib/dcl-r6/pf01/src/admin_postexit.py'
l['authorization_receipt_required_fields']+=['phase_finalizer_contract_sha256','PhaseFinalizer_diagnostic_explicitly_approved']
l['authorization_receipt_required_fields']=list(dict.fromkeys(l['authorization_receipt_required_fields']))
l['phase_finalizer_schedule']=['C00 PASS','unchanged PT64','PF48 with8 mutants','close and native seal','automatic checked admin_postexit entry','quiescent audit/snapshot and separate host administrative ZIP']
l['phase_finalizer_limits']=m['phase_finalizer_delta']
l['startup_limits']['normal_minimal_visits_hard']=2689
l['phase_A_diagnostic']={'scope':'PT_STARTUP_DIAGNOSTIC_ONLY','mode':'NORMAL_START','through':'C00/PT64/PF48 then close',
    'models_allowed':False,'automatic_retry':False,'new_time_window':False}
l['phase_A_modes']['NORMAL_START']='Fresh prewindow/runtime/C00/PT64/PF48 then close/native and automatic admin seal. No READY64/MR64/C09/full C/S/gates/models'
l['phase_A_identity_rule']='NORMAL_START only for planned batch12-r3. PREWINDOW_ABORT and later stages require a separately frozen identity/lock and new authorization; no second free window'
l['startup_schedule'][-1]='NORMAL_START: PT64 then PF48 then close; full inherited chain requires a future independently approved version/scope'
l['calibration_schedule']=['C00','PT64','PF48','READY64','MR_PREPAY_AND_MR64','C01','C02','C03','C04','C05','C06','C07','C08',
    'C09H','ROOT_IPC56','BOOT_CONTINUITY40','C09_EXPECTED_EXIT_RESUME_ONCE','C10','C11','C12','RANGE_34_JOBS','ROOT_RAW_AND_18_GATE_NEGATIVES','RESOURCE_QUALIFICATION','FORMAL_OR_CLOSE_AS_AUTHORIZED']
l['phase_B']='REQUEST_ONLY: requires additional successful independent A evidence, new identity/digests and explicit authorization; current planned batch closes after minimal NORMAL_START'
put(W/'inputs/execution_lock.json',l)
rows=[{'relative':p.relative_to(W).as_posix(),'bytes':p.stat().st_size,'sha256':h(p)} for p in sorted(W.rglob('*')) if p.is_file()]
assert len(rows)==55 and len([r for r in rows if r['relative'].endswith('.py')])==38
put(E/'STATIC_WORKSPACE_LOCK.json',{'version':'PTA-PhaseFinalizer-static-1/r3','host':str(W),'planned_linux':'/var/lib/dcl-r6/pf01',
    'planned_runtime':'/var/lib/dcl-r6/batch12','files':rows,'source_only':True,'Linux_entities_created':False})
template=load(B/'DCL-R6-PreT0-Fix/evidence/PHASE_A_NORMAL_START_AUTHORIZATION_TEMPLATE.json')
template.update(batch_id='batch12',static_revision='PTA-PhaseFinalizer-static-1/r3',status='TEMPLATE_UNAPPROVED',
    static_manifest_sha256=h(W/'inputs/static_manifest.json'),execution_lock_sha256=h(W/'inputs/execution_lock.json'),authorization_text_sha256=None,
    phase_finalizer_contract_sha256=h(W/'inputs/phase_finalizer_contract.json'),PhaseFinalizer_diagnostic_explicitly_approved=False)
for key in template:
    if key.endswith('_sha256') and key in m:template[key]=m[key]
for key in template:
    if key.endswith('_explicitly_approved'):template[key]=False
put(E/'PHASE_A_NORMAL_START_AUTHORIZATION_TEMPLATE.json',template)
shutil.copytree(W,E/'SOURCE_FINAL_R3')
print(json.dumps({'files':55,'programs':38,'Linux_files':53,'manifest':h(W/'inputs/static_manifest.json'),'execution_lock':h(W/'inputs/execution_lock.json'),
    'PF_completed':817,'PF_hard':1152,'minimal_hard':2689,'full_hard':66770,'future_receipt_created':False},ensure_ascii=False))
