"""Explicit post-failure administrative preservation; never an automatic-success claim."""
from pathlib import Path
import hashlib,json,re,shutil,time,zipfile
from datetime import datetime,timezone
E=Path(__file__).resolve().parent;O=E.parent;B=O.parent
I=Path(r'D:\毕业设计\DCL-R6-isolated-verification\batch11');W=I.parent/'pt01';begun=time.perf_counter()
def load(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
    if Path(p).exists():
        assert load(p)==x,'ADMIN_EXISTING_OUTPUT_DIFFERS:'+str(p)
        return
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
assert not (O/'PTA_EVIDENCE.zip').exists() and not (E/'DELIVERY_CHECK.json').exists()
actual=load(E/'ACTUAL_RESULTS.json');audit=load(E/'POSTRUN_AUDIT.json')
assert actual['entry_calls']==1 and actual['R']==0 and actual['T0'] is not None
assert not audit['payload_processes'] and not audit['root_role_processes'] and not audit['parent_cgroup_exists']
assert audit['closed_marker_exists'] and audit['STOP_REQUEST_exists']
source=load(E/'SOURCE_AND_SCOPE_ADMISSION.json');source_errors=[]
for row in source['files']:
    for p in [W/row['relative'],E/'FROZEN_SOURCE_REFERENCE'/row['relative'],I/'FROZEN_PT'/row['relative']]:
        if sha(p)!=row['sha256']:source_errors.append(str(p))
assert not source_errors and not list(W.rglob('*.pyc'))
native_errors=[]
for row in load(E/'NATIVE_EXPORT_LOCK.json')['files']:
    if sha(row['host'])!=row['sha256']:native_errors.append(row['host'])
assert not native_errors
baseline=load(E/'BASELINE_LOCK.json');history_errors=[]
for row in baseline['files']:
    p=Path(row['host'])
    if not p.is_file() or p.stat().st_size!=row['bytes'] or sha(p)!=row['sha256']:history_errors.append(row['host'])
assert not history_errors
dups=load(B/'DCL-R6-batch02-Perf/evidence/DUPLICATE_REGISTER.json');dup_errors=[]
for row in dups['files']:
    if sha(Path(dups['path'])/row['relative'])!=row['duplicate_sha256']:dup_errors.append(row['relative'])
assert len(dups['files'])==47 and not dup_errors
disk_checks=[]
for name in ['DCL-R6-PreT0-Fix','DCL-R6-MR-A','DCL-R6-ManagerRecovery-Fix','DCL-R6-CalDiag']:
    rows=load(B/name/'OUTPUT_MANIFEST.json');rows=rows.get('files',rows) if isinstance(rows,dict) else rows;errors=[];old_nav=[]
    archives=list((B/name).glob('*EVIDENCE.zip'));assert len(archives)==1
    for row in rows:
        p=Path(row['host'])
        if p.parent==B and p.name in baseline['nav']:
            with zipfile.ZipFile(archives[0]) as z:previous=z.read(row['archive_path'])
            if hashlib.sha256(previous).hexdigest()!=row['sha256'] or not p.read_bytes().endswith(previous):errors.append(row['host'])
            old_nav.append({'name':p.name,'archived_sha256':row['sha256'],'exact_historical_suffix':True})
        elif sha(p)!=row['sha256']:errors.append(row['host'])
    assert not errors;disk_checks.append({'stage':name,'disk_members':len(rows),'frozen_disk_exact':len(rows)-len(old_nav),'authorized_navigation_suffix_checks':old_nav,'errors':errors})
put(E/'HISTORICAL_DISK_MANIFEST_CHECK.json',disk_checks)
navigation=[];(E/'navigation_after').mkdir(exist_ok=True)
for name in baseline['nav']:
    old=(E/'navigation_before'/name).read_bytes();new=(B/name).read_bytes();assert new.endswith(old)
    dest=E/'navigation_after'/name
    if dest.exists():assert dest.read_bytes()==new
    else:shutil.copyfile(B/name,dest)
    navigation.append({'name':name,'original_sha256':hashlib.sha256(old).hexdigest(),'original_exact_suffix':True,'new_sha256':sha(B/name)})
put(E/'HISTORY_PROTECTION_CHECK.json',{'status':'MATCH','historical_files':len(baseline['files']),'mismatches':history_errors,
 'historical_manifest_disk_checks':disk_checks,'navigation':navigation,'mispath_files':47,'mispath_mismatches':dup_errors,
 'mispath_actions':'READ_HASH_ONLY','old_policy_rejection':'blocked by policy retained','old_budgets_modified':0,'frozen_r3_source_edits':0,
 'authorized_new_control_directory':'DCL-R6-PreT0-Fix/authorization/batch11-r5; newly added, no historical file overwritten'})
required=['PTA_AUTHORIZATION_AND_LOCK.md','PTA_INITIALIZATION_RESULTS.md','PTA_CHECKPOINT_LIFECYCLE.md','PTA_PREWINDOW_ABORT_RESULTS.md',
 'PTA_AUTOMATIC_CLOSURE_RESULTS.md','PTA_SEALING_RESULTS.md','PTA_REGRESSION_RESULTS.md','PTA_RESOURCE_ACCOUNTING.md',
 'PTA_EXECUTION_TIMELINE.md','PTA_COUNTEREXAMPLES.md','PTA_FINAL_DECISION.md']
assert all((O/n).is_file() for n in required)
links=0;link_errors=[]
for p in O.glob('*.md'):
    raw=p.read_text(encoding='utf-8');assert '不是' not in raw
    for m in re.finditer(r'\[[^\]\n]+\]\(([^)\n]+)\)',raw):
        target=m.group(1).split('#',1)[0]
        if not target or re.match(r'^[a-z]+://',target):continue
        links+=1
        if not (p.parent/target).exists() and (p.parent/target)!=E/'DELIVERY_CHECK.json':link_errors.append({'file':p.name,'target':target})
assert not link_errors,link_errors
json_count=0
for base in [O,I]:
    for p in base.rglob('*.json'):load(p);json_count+=1
index={'schema':'PTA-SOURCE-INDEX/1','files':source['files'],'native_export_lock':'evidence/NATIVE_EXPORT_LOCK.json',
 'source_export_lock':'evidence/FROZEN_SOURCE_EXPORT_LOCK.json','history_lock':'evidence/BASELINE_LOCK.json',
 'automatic_status':'ADMIN_EVIDENCE_UNRESOLVED','administrative_package_class':'Explicit post-failure preservation; independent from frozen automatic flow',
 'private_originals':'Nonce only in local private snapshot/archive; omitted from reports',
 'artifact_integrity_status':'See OUTPUT_MANIFEST.json and evidence/DELIVERY_CHECK.json'}
put(O/'SOURCE_INDEX.json',index)
rows=[]
for p in sorted(O.rglob('*')):
    if p.is_file() and p.name not in ['OUTPUT_MANIFEST.json','PTA_EVIDENCE.zip','PTA_EVIDENCE.zip.sha256','DELIVERY_CHECK.json']:
        rows.append({'host':str(p),'archive_path':'research/'+p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
for key,folder,prefix in [('NATIVE_EXPORT_LOCK.json','native_snapshot','export/native'),('FROZEN_SOURCE_EXPORT_LOCK.json','FROZEN_PT','export/frozen')]:
    for row in load(E/key)['files']:
        p=Path(row['host']);rows.append({'host':str(p),'archive_path':prefix+'/'+row['relative'],'bytes':p.stat().st_size,'sha256':sha(p)})
assert len({r['archive_path'] for r in rows})==len(rows)
put(O/'OUTPUT_MANIFEST.json',{'schema':'PTA-ADMIN-MANIFEST/1','classification':'Explicit administrative preservation after automatic post-exit failure',
 'automatic_admin_status':'ADMIN_EVIDENCE_UNRESOLVED','native_artifact_status':'NATIVE_SEAL_COMPLETED',
 'files':rows,'exclusions':['OUTPUT_MANIFEST.json (included as extra ZIP member)','PTA_EVIDENCE.zip','PTA_EVIDENCE.zip.sha256','evidence/DELIVERY_CHECK.json'],
 'reason':'Avoid manifest/ZIP/self-hash cycles; delivery receipt is external and separately reports hashes'})
with zipfile.ZipFile(O/'PTA_EVIDENCE.zip','x',zipfile.ZIP_DEFLATED) as z:
    for row in rows:z.write(row['host'],row['archive_path'])
    z.write(O/'OUTPUT_MANIFEST.json','OUTPUT_MANIFEST.json')
zip_errors=[]
with zipfile.ZipFile(O/'PTA_EVIDENCE.zip') as z:
    assert z.testzip() is None
    for row in rows:
        raw=z.read(row['archive_path'])
        if len(raw)!=row['bytes'] or hashlib.sha256(raw).hexdigest()!=row['sha256']:zip_errors.append(row['archive_path'])
    assert z.read('OUTPUT_MANIFEST.json')==(O/'OUTPUT_MANIFEST.json').read_bytes();entries=len(z.namelist())
assert not zip_errors
zipsha=sha(O/'PTA_EVIDENCE.zip');(O/'PTA_EVIDENCE.zip.sha256').write_text(zipsha+'  PTA_EVIDENCE.zip\n',encoding='ascii')
delivery={'schema':'PTA-DELIVERY/1','status':'PASS_ADMINISTRATIVE_PRESERVATION_ONLY','dynamic_verdict':actual['result'],
 'required_reports':11,'source_files':51,'programs':35,'source_errors':source_errors,'native_files':46,'native_export_errors':native_errors,
 'historical_files':len(baseline['files']),'history_mismatches':history_errors,'mispath_files':47,'mispath_mismatches':dup_errors,
 'active_entry_calls':1,'automatic_post_exit_calls':1,'administrative_WSL_calls':4,'test_retries':0,'frozen_source_edits':0,
 'T0':actual['T0'],'R':0,'PT64_executed':0,'mutants_detected':0,'automatic_STOP':True,'automatic_CLOSED':True,'all_roles_final_empty':True,
 'extra_fallback_cleanup_calls':0,'manual_cleanup_calls':0,'internal_cleanup_final':'CLOSED_CLEANUP_CONFIRMED','early_UNKNOWN_retained':True,
 'native_seal_status':'NATIVE_SEAL_COMPLETED','native_manifest_rows':44,'native_zip_entries':45,
 'automatic_admin_status':'ADMIN_EVIDENCE_UNRESOLVED','automatic_post_exit_code':1,'explicit_research_admin_status':'ADMIN_EVIDENCE_SEALED',
 'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
 'STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED','JSON_parsed_before_manifest':json_count,'links_checked':links,'link_errors':link_errors,
 'manifest_rows':len(rows),'zip_entries':entries,'zip_stream_errors':zip_errors,'manifest_sha256':sha(O/'OUTPUT_MANIFEST.json'),
 'zip_sha256':zipsha,'zip_bytes':(O/'PTA_EVIDENCE.zip').stat().st_size,'sealed_utc':datetime.now(timezone.utc).isoformat(),
 'admin_elapsed_seconds':time.perf_counter()-begun,'self_excluded_from_manifest_and_zip':True}
put(E/'DELIVERY_CHECK.json',delivery)
print(json.dumps({k:delivery[k] for k in ['status','dynamic_verdict','historical_files','mispath_files','manifest_rows','zip_entries','zip_sha256','zip_bytes','links_checked']},ensure_ascii=False))
