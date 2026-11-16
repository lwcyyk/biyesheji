"""Research evidence packaging after closed preflight attempt; no runtime re-entry."""
from pathlib import Path
import hashlib,json,re,shutil,time,zipfile
from datetime import datetime,timezone
E=Path(__file__).resolve().parent;O=E.parent;B=O.parent;I=Path(r'D:\毕业设计\DCL-R6-isolated-verification\batch13');W=I.parent/'tr01';tick=time.perf_counter()
def load(p):return json.loads(Path(p).read_bytes())
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
assert not(O/'TRA_EVIDENCE.zip').exists() and not(E/'DELIVERY_CHECK.json').exists()
actual=load(E/'ACTUAL_RESULTS.json');src=load(E/'SOURCE_AND_SCOPE_ADMISSION.json');history=load(E/'BASELINE_LOCK.json')
assert actual['overall']=='PREFLIGHT_FAILED_RUNTIME_DRIFT' and actual['R'] is None and actual['entry_calls']==1
source_errors=[]
for row in src['files']:
    for base in [W,E/'FROZEN_SOURCE_REFERENCE',I/'FROZEN_TR']:
        if h(base/row['relative'])!=row['sha256']:source_errors.append(str(base/row['relative']))
assert not source_errors and not list(W.rglob('*.pyc'))
for row in load(E/'DRIFTED_RUNTIME_EXPORT_LOCK.json')['files']:assert h(row['host'])==row['sha256']
history_errors=[]
for row in history['files']:
    p=Path(row['host'])
    if not p.is_file() or p.stat().st_size!=row['bytes'] or h(p)!=row['sha256']:history_errors.append(row['host'])
assert not history_errors
dups=load(B/'DCL-R6-batch02-Perf/evidence/DUPLICATE_REGISTER.json');dup_errors=[]
for row in dups['files']:
    if h(Path(dups['path'])/row['relative'])!=row['duplicate_sha256']:dup_errors.append(row['relative'])
assert len(dups['files'])==47 and not dup_errors
prefix=('## DCL-R6-TR-A 最新动态增量（2026-11-13）\n\n'
 '**PREFLIGHT_FAILED_RUNTIME_DRIFT。** TerminalRead-static-1/r1/batch13-r1唯一入口exit125；冻结ld-linux摘要不符，完整1241对象核对发现loader/libc/libm三项变化，当前glibc2.39-0ubuntu8.12。'
 '源码/输入保持，未更新锁、安装依赖或重跑。\n\n'
 'WORK/C00/PT/PF/TR均未执行；T0/deadline/R/claim/正式实例未创建，native NOT_APPLICABLE。自动行政14/15封存成功，角色/组空，额外后备0；内部UNKNOWN保留。'
 '先独立审查运行时适配及新资格/身份/锁，当前control与失败证据保留。\n\n'
 'RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。\n\n'
 '[20项回答](DCL-R6-TR-A/TRA_FINAL_DECISION.md) · [具体差异](DCL-R6-TR-A/TRA_COUNTEREXAMPLES.md) · '
 '[行政封存](DCL-R6-TR-A/TRA_ADMIN_FINALIZER_RESULTS.md) · [证据索引](DCL-R6-TR-A/EVIDENCE_INDEX.md) · '
 '[下一适配范围](DCL-R6-TR-A/NEXT_PLATFORM_ADMISSION_REQUEST.md)\n\n以下逐字节保留先前记录。\n\n---\n\n')
navigation=[];(E/'navigation_after').mkdir()
for name in history['nav']:
    before=(E/'navigation_before'/name).read_bytes();assert(B/name).read_bytes()==before,'CONCURRENT_NAV_CHANGE:'+name
    (B/name).write_bytes(prefix.encode('utf-8')+before);shutil.copyfile(B/name,E/'navigation_after'/name)
    navigation.append({'name':name,'original_sha256':hashlib.sha256(before).hexdigest(),'original_exact_suffix':(B/name).read_bytes().endswith(before),'new_sha256':h(B/name)})
put(E/'HISTORY_PROTECTION_CHECK.json',{'status':'MATCH','historical_files':len(history['files']),'history_mismatches':history_errors,
 'mispath_files':47,'mispath_mismatches':dup_errors,'mispath_actions':'READ_HASH_ONLY','navigation':navigation,
 'old_policy_rejection':'blocked by policy retained','frozen_source_edits':0,'historical_budgets_modified':0,
 'new_authorized_control':'DCL-R6-TerminalRead-Fix/authorization/batch13-r1','system_runtime_changes_by_this_task':0})
required=['TRA_AUTHORIZATION_AND_LOCK.md','TRA_BOOT_AND_WORK_RESULTS.md','TRA_TERMINAL_READ_RESULTS.md','TRA_ACTIVE_GUARD_RESULTS.md',
 'TRA_TR40_RESULTS.md','TRA_COMPATIBILITY_RESULTS.md','TRA_NATIVE_SEAL_RESULTS.md','TRA_ADMIN_FINALIZER_RESULTS.md','TRA_INTERNAL_STATE_RESULTS.md',
 'TRA_RESOURCE_ACCOUNTING.md','TRA_EXECUTION_TIMELINE.md','TRA_COUNTEREXAMPLES.md','TRA_FINAL_DECISION.md']
assert all((O/name).exists() for name in required)
links=0;link_errors=[]
for p in O.glob('*.md'):
    text=p.read_text(encoding='utf-8');assert '不是' not in text
    for match in re.finditer(r'\[[^\]\n]+\]\(([^)\n]+)\)',text):
        rel=match.group(1).split('#',1)[0]
        if not rel or re.match(r'^[a-z]+://',rel):continue
        links+=1;target=p.parent/rel
        if not target.exists() and target!=E/'DELIVERY_CHECK.json':link_errors.append({'file':p.name,'target':rel})
assert not link_errors,link_errors
parsed=0
for base in [O,I]:
    for p in base.rglob('*.json'):load(p);parsed+=1
put(O/'SOURCE_INDEX.json',{'schema':'TRA-SOURCE-INDEX/1','version':actual['revision'],'files':src['files'],
 'source_export':'evidence/FROZEN_SOURCE_EXPORT_LOCK.json','current_runtime_export':'evidence/DRIFTED_RUNTIME_EXPORT_LOCK.json',
 'current_runtime_export_status':'Observed drifted platform bytes, not approved execution inputs','first_failure':'evidence/FIRST_FAILURE.json',
 'automatic_admin_verification':'evidence/AUTOMATIC_ADMIN_VERIFICATION.json','test_results':'evidence/UNRUN_CASE_REGISTER.json'})
rows=[]
for p in sorted(O.rglob('*')):
    if p.is_file() and p.name not in ['OUTPUT_MANIFEST.json','TRA_EVIDENCE.zip','TRA_EVIDENCE.zip.sha256','DELIVERY_CHECK.json']:
        rows.append({'host':str(p),'archive_path':'research/'+p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':h(p)})
for name,prefix in [('FROZEN_SOURCE_EXPORT_LOCK.json','export/frozen'),('DRIFTED_RUNTIME_EXPORT_LOCK.json','export/current-runtime')]:
    for row in load(E/name)['files']:
        p=Path(row['host']);rows.append({'host':str(p),'archive_path':prefix+'/'+row['relative'],'bytes':p.stat().st_size,'sha256':h(p)})
assert len({row['archive_path'] for row in rows})==len(rows)
put(O/'OUTPUT_MANIFEST.json',{'schema':'TRA-RESEARCH-MANIFEST/1','classification':'Actual preflight-failure originals, automatic administrative evidence, source/runtime snapshots and reports',
 'native_seal':'NATIVE_SEAL_NOT_APPLICABLE','automatic_admin':'ADMIN_EVIDENCE_SEALED','files':rows,
 'exclusions':['OUTPUT_MANIFEST.json (extra ZIP member)','TRA_EVIDENCE.zip','TRA_EVIDENCE.zip.sha256','evidence/DELIVERY_CHECK.json']})
with zipfile.ZipFile(O/'TRA_EVIDENCE.zip','x',zipfile.ZIP_DEFLATED) as z:
    for row in rows:z.write(row['host'],row['archive_path'])
    z.write(O/'OUTPUT_MANIFEST.json','OUTPUT_MANIFEST.json')
errors=[]
with zipfile.ZipFile(O/'TRA_EVIDENCE.zip') as z:
    assert z.testzip() is None
    for row in rows:
        data=z.read(row['archive_path'])
        if len(data)!=row['bytes'] or hashlib.sha256(data).hexdigest()!=row['sha256']:errors.append(row['archive_path'])
    assert z.read('OUTPUT_MANIFEST.json')==(O/'OUTPUT_MANIFEST.json').read_bytes();entries=len(z.namelist())
assert not errors
zipsha=h(O/'TRA_EVIDENCE.zip');(O/'TRA_EVIDENCE.zip.sha256').write_text(zipsha+'  TRA_EVIDENCE.zip\n',encoding='ascii')
delivery={'schema':'TRA-DELIVERY/1','status':'PASS_ADMINISTRATIVE_DELIVERY_ONLY','overall':'PREFLIGHT_FAILED_RUNTIME_DRIFT','version':actual['revision'],
 'TR-A1':'UNRUN','TR-A2':'UNRUN','TR-A3':'UNRUN','TR-A4':'UNRUN','TR-A5':'UNRUN','TR-A6':'CONDITIONAL_PASS','TR-A7':'UNKNOWN','TR-A8':'FAIL',
 'required_reports':13,'source_files':59,'programs':41,'source_errors':source_errors,'historical_files':len(history['files']),'history_mismatches':history_errors,
 'mispath_files':47,'mispath_mismatches':dup_errors,'active_calls':1,'automatic_post_calls':1,'administrative_WSL_calls':4,'total_WSL_calls':6,
 'runtime_objects_created':False,'T0':None,'R':None,'tests_executed':0,'mutants_exercised':0,'mutants_detected':0,'test_retries':0,'frozen_source_edits':0,
 'runtime_files_checked':1241,'runtime_files_different':3,'runtime_hashes_updated':False,'dependencies_installed':0,
 'native_seal':'NATIVE_SEAL_NOT_APPLICABLE','auto_admin':'ADMIN_EVIDENCE_SEALED','auto_admin_rows':14,'auto_admin_entries':15,
 'internal_state':'UNKNOWN','extra_fallback_archival':0,'manual_cleanup':0,'roles_and_parent_group_empty':True,
 'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
 'STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED','JSON_parsed_before_manifest':parsed,'links_checked':links,'link_errors':link_errors,
 'manifest_rows':len(rows),'ZIP_entries':entries,'ZIP_stream_errors':errors,'manifest_sha256':h(O/'OUTPUT_MANIFEST.json'),'ZIP_sha256':zipsha,
 'ZIP_bytes':(O/'TRA_EVIDENCE.zip').stat().st_size,'sealed_utc':datetime.now(timezone.utc).isoformat(),'admin_elapsed_seconds':time.perf_counter()-tick,
 'self_excluded_from_manifest_and_zip':True}
put(E/'DELIVERY_CHECK.json',delivery)
print(json.dumps({key:delivery[key] for key in ['overall','historical_files','manifest_rows','ZIP_entries','ZIP_sha256','ZIP_bytes','links_checked']},ensure_ascii=False))
