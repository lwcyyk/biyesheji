"""Explicit reviewed runtime relock; never reads new hashes automatically at execution."""
from pathlib import Path
import hashlib,json,shutil,difflib
E=Path(__file__).resolve().parent;B=E.parent.parent;W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\ra01')
def load(p):return json.loads(Path(p).read_bytes())
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
identity=load(W/'inputs/runtime_identity_contract.json');observed=load(E/'PLATFORM_EXPORT.json');decision=load(E/'PROVENANCE_DECISION.json')
assert decision['static_baseline_admissible'] and len(observed['runtime_differences'])==3
updates={r['path']:r['actual_sha256'] for r in observed['runtime_differences']}
assert {r['path']:r['sha256'] for r in identity['components']}==updates
critical=load(W/'inputs/runtime_critical.json');tree=load(W/'inputs/runtime_tree_lock.json');m=load(W/'inputs/static_manifest.json');l=load(W/'inputs/execution_lock.json')
changed=[]
for row in identity['components']:
    path=row['path'];expected=next(x['expected_sha256'] for x in observed['runtime_differences'] if x['path']==path)
    assert critical['files'][path]==m['runtime_files'][path]==expected
    critical['files'][path]=m['runtime_files'][path]=row['sha256']
    for tree_path,record in tree['files'].items():
        if tree_path==path or record['sha256']==expected:
            assert record['sha256']==expected
            record['sha256']=row['sha256']
            for key in ['bytes','size']:
                if key in record:record[key]=row['bytes']
    changed.append({'path':path,'old_sha256':expected,'new_sha256':row['sha256'],'build_id':row['build_id'],'package':'libc6:amd64','package_revision':'2.39-0ubuntu8.12'})
critical['runtime_adaptation']='Explicit RA1 review of exactly3 changed glibc artifacts; other pins retained'
put(W/'inputs/runtime_critical.json',critical);put(W/'inputs/runtime_tree_lock.json',tree)
def totals(obj):
    if isinstance(obj,dict):
        for k,v in obj.items():
            if k in ['full_calibration_hard','full_calibration_hard_visits','calibration_hard_bound','calibration_hard_visit_upper_bound','calibration_total_max_visits','new_calibration_hard'] and v==67730:obj[k]=68498
            elif k in ['normal_minimal_hard','normal_minimal_visits_hard'] and v==3649:obj[k]=4417
            elif k=='normal_minimal_completed' and v==2588:obj[k]=3133
            else:totals(v)
    elif isinstance(obj,list):
        for v in obj:totals(v)
totals(m);totals(l)
for obj in [m,l]:obj['freeze_revision']=1;obj['export_lock_revision']='RA-r1'
m['profile']='CPY312-UBU24/1';m['profile_approval']='RUNTIME_ADAPT_HOST_STATIC_AND_READONLY_ONLY; explicit Root/package provenance assumptions plus new native qualification required'
m['runtime_identity_profile']=identity['profile'];m['runtime_adaptation']={'upstream':'GNU libc2.39','Ubuntu_revision':'2.39-0ubuntu8.12','changed_artifacts':changed,
 'provenance_status':decision['classification'],'signature_evidence':'Two cached Ubuntu InRelease signatures/index hashes valid; local installed catalog trusted',
 'missing_payload_reconstruction':True,'execution_time_boundary':'No atomic path-to-exec or protection from privileged updates after check','dynamic_compatibility':'UNRUN'}
m['runtime_regression_delta']={'jobs':32,'safe':24,'mutants':8,'completed_visits':545,'hard_visits':768,'normal_minimal_completed':3133,'normal_minimal_hard':4417,'full_calibration_hard':68498,'dynamic_status':'UNRUN'}
m['source_hashes']={p.name:h(p) for p in sorted((W/'src').glob('*.py'))}
for p in sorted((W/'inputs').iterdir()):
    if p.is_file() and p.name not in ['static_manifest.json','execution_lock.json']:m['bound_inputs']['inputs/'+p.name]=h(p)
for rel,sha in m['bound_inputs'].items():
    key=Path(rel).stem+'_sha256'
    if key in m or key in ['runtime_identity_contract_sha256','runtime_regression_contract_sha256']:m[key]=sha
m['runtime_check_rule_sha256']=h(W/'src/runtime_identity.py')
put(W/'inputs/static_manifest.json',m)
for key in list(l):
    if key.endswith('_sha256') and key in m:l[key]=m[key]
l['static_manifest_sha256']=h(W/'inputs/static_manifest.json');l['windows_entry_sha256']=h(W/'host/windows_entry.py');l['startup_host_finalizer_sha256']=h(W/'host/startup_finalize.py')
l['runtime_identity_contract_sha256']=h(W/'inputs/runtime_identity_contract.json');l['runtime_regression_contract_sha256']=h(W/'inputs/runtime_regression_contract.json');l['runtime_check_rule_sha256']=h(W/'src/runtime_identity.py')
l['authorization_receipt_required_fields']=list(dict.fromkeys(l['authorization_receipt_required_fields']+['runtime_identity_contract_sha256','runtime_regression_contract_sha256','RuntimeAdapt_diagnostic_explicitly_approved','RuntimeAdapt_provenance_assumptions_explicitly_approved']))
l['runtime_identity_profile']=identity['profile'];l['runtime_adaptation']=m['runtime_adaptation'];l['runtime_regression_limits']=m['runtime_regression_delta']
l['runtime_recheck_points']=['preflight artifact_check initial/final','Guard.manifest pinned-byte+own-map check','pre-service launch full package/path/hash','post-exec kernel_admission package/own-map','native seal full runtime check','automatic admin before target import']
l['phase_A_diagnostic']={'scope':'PT_STARTUP_DIAGNOSTIC_ONLY','mode':'NORMAL_START','through':'C00/PT64/PF48/TR40/RA32 then close/terminal/native/admin','models_allowed':False,'automatic_retry':False,'new_time_window':False}
l['phase_A_modes']['NORMAL_START']='Fresh reviewed runtime and new batch14; C00/PT64/PF48/TR40/RA32 then close/readonly/native/admin. No MR/C09/full C/S/gates/models'
l['phase_A_identity_rule']='Fresh batch14-r1 only. Old batch13 attempt remains sealed. Every later phase/mode needs new identity/lock/approval.'
index=l['calibration_schedule'].index('TR40');l['calibration_schedule'].insert(index+1,'RA32');l['startup_schedule'][-1]='PT64/PF48/TR40/RA32 then minimal normal close; terminal/native/admin; no full chain under A2'
l['phase_B']='REQUEST_ONLY; no inherited RESOURCE_GATE_PASS. Requires successful new runtime/terminal A2 and independent full-chain identity/digests/authorization.'
put(W/'inputs/execution_lock.json',l)
rows=[{'relative':p.relative_to(W).as_posix(),'bytes':p.stat().st_size,'sha256':h(p)} for p in sorted(W.rglob('*')) if p.is_file()]
assert len(rows)==64 and sum(r['relative'].endswith('.py') for r in rows)==44
put(E/'STATIC_WORKSPACE_LOCK.json',{'version':'RuntimeAdapt-static-1/r1','host':str(W),'planned_linux':'/var/lib/dcl-r6/ra01','planned_runtime':'/var/lib/dcl-r6/batch14','files':rows,'provenance_condition':decision['trust_assumptions'],'dynamic_authority':False})
template=load(B/'DCL-R6-TerminalRead-Fix/evidence/PHASE_A_NORMAL_START_AUTHORIZATION_TEMPLATE.json')
template.update(batch_id='batch14',static_revision='RuntimeAdapt-static-1/r1',status='TEMPLATE_UNAPPROVED',authorization_text_sha256=None,
 static_manifest_sha256=h(W/'inputs/static_manifest.json'),execution_lock_sha256=h(W/'inputs/execution_lock.json'),runtime_identity_contract_sha256=h(W/'inputs/runtime_identity_contract.json'),
 runtime_regression_contract_sha256=h(W/'inputs/runtime_regression_contract.json'),RuntimeAdapt_diagnostic_explicitly_approved=False,RuntimeAdapt_provenance_assumptions_explicitly_approved=False)
for key in template:
    if key.endswith('_sha256') and key in m:template[key]=m[key]
for key in template:
    if key.endswith('_explicitly_approved'):template[key]=False
put(E/'TR_A2_AUTHORIZATION_TEMPLATE.json',template)
shutil.copytree(W,E/'SOURCE_FINAL_R1')
put(E/'RUNTIME_PIN_DIFF.json',{'changed_runtime_pins':changed,'other1241_baseline_pins_changed':0,'identity_contract':identity['profile'],'explicit_review':True})
before={p.relative_to(E/'SOURCE_BEFORE').as_posix():p for p in (E/'SOURCE_BEFORE').rglob('*') if p.is_file()};after={p.relative_to(W).as_posix():p for p in W.rglob('*') if p.is_file()};diff=[];index=[]
for rel in sorted(set(before)|set(after)):
    a=before.get(rel);b=after.get(rel);same=bool(a and b and a.read_bytes()==b.read_bytes());index.append({'relative':rel,'before_sha256':h(a) if a else None,'after_sha256':h(b) if b else None,'classification':'UNCHANGED' if same else 'ADDED' if not a else 'REMOVED' if not b else 'CHANGED'})
    if not same:diff.extend(difflib.unified_diff(a.read_text(encoding='utf-8').splitlines(True) if a else [],b.read_text(encoding='utf-8').splitlines(True) if b else [],fromfile='before/'+rel,tofile='after/'+rel))
(E/'FULL_DIFF.patch').write_text(''.join(diff),encoding='utf-8');put(E/'FILE_DIFF_INDEX.json',index)
r=load(E/'STATIC_RESULT.json');r.update(manifest_sha256=h(W/'inputs/static_manifest.json'),execution_lock_sha256=h(W/'inputs/execution_lock.json'))
put(E/'STATIC_RESULT.json',r)
print(json.dumps({'files':64,'programs':44,'Linux_files':62,'manifest':r['manifest_sha256'],'execution_lock':r['execution_lock_sha256'],'changed_glibc_pins':3,'minimal_completed':3133,'minimal_hard':4417,'full_hard':68498,'actual_receipt_created':False},ensure_ascii=False))
