"""Seal static/read-only runtime review. No system/library/workload mutations."""
from pathlib import Path
import hashlib,json,re,shutil,time,zipfile
from datetime import datetime,timezone
E=Path(__file__).resolve().parent;O=E.parent;B=O.parent;W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\ra01');tick=time.perf_counter()
def load(p):return json.loads(Path(p).read_bytes())
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
assert not(O/'RUNTIME_ADAPT_EVIDENCE.zip').exists() and not(E/'DELIVERY_CHECK.json').exists()
r=load(E/'STATIC_RESULT.json');lock=load(E/'STATIC_WORKSPACE_LOCK.json');history=load(E/'BASELINE_LOCK.json')
source_errors=[]
for row in lock['files']:
    for base in [W,E/'SOURCE_FINAL_R1']:
        if h(base/row['relative'])!=row['sha256']:source_errors.append(str(base/row['relative']))
assert not source_errors and len(lock['files'])==64 and len(list(W.rglob('*.py')))==44 and not list(W.rglob('*.pyc'))
assert {p.relative_to(W).as_posix() for p in W.rglob('*') if p.is_file()}=={row['relative'] for row in lock['files']}
m=load(W/'inputs/static_manifest.json');l=load(W/'inputs/execution_lock.json')
assert h(W/'inputs/static_manifest.json')==r['manifest_sha256']==l['static_manifest_sha256'] and h(W/'inputs/execution_lock.json')==r['execution_lock_sha256']
for name,sha in m['source_hashes'].items():assert h(W/'src'/name)==sha
for name,sha in m['bound_inputs'].items():assert h(W/name)==sha
template=load(E/'TR_A2_AUTHORIZATION_TEMPLATE.json')
assert template['status']=='TEMPLATE_UNAPPROVED' and template['authorization_text_sha256'] is None and all(v is False for k,v in template.items() if k.endswith('_explicitly_approved'))
assert not Path(load(W/'inputs/batch_identity.json')['host_control']).exists()
export=load(E/'PLATFORM_EXPORT.json')
for row in export['files']+export['old_members']:assert h(E/row['relative'])==row['sha256']
history_errors=[]
for row in history['files']:
    p=Path(row['host'])
    if not p.is_file() or p.stat().st_size!=row['bytes'] or h(p)!=row['sha256']:history_errors.append(row['host'])
assert not history_errors
dups=load(B/'DCL-R6-batch02-Perf/evidence/DUPLICATE_REGISTER.json');dup_errors=[]
for row in dups['files']:
    if h(Path(dups['path'])/row['relative'])!=row['duplicate_sha256']:dup_errors.append(row['relative'])
assert len(dups['files'])==47 and not dup_errors
prefix=('## RuntimeAdapt 最终静态/只读增量（2026-11-13）\n\n'
 '**RuntimeAdapt-static-1/r1已形成条件性新运行时基线，业务动态0。** GNU libc上游仍2.39，Ubuntu修订8.9→8.12；三个ELF归属/目录、两个InRelease及完整索引签名哈希、66入口/114对象必要ABI核验齐备。'
 '新8.12包payload未在本地重提取，来源依赖受信Root/dpkg/keyring，未来许可需显式接受；不接受时保持RUNTIME_PROVENANCE_UNRESOLVED。\n\n'
 '64文件/44程序、20静态断言/3纯ELF探针，三项pin显式更新；原严格hash守卫、业务/预算/RootIPC/MR/Terminal判据保持，新包/路径/Build-ID/自身映射重查及RA32/8变异齐备。'
 '正常A2完成3133/硬4417，完整硬68498；path→exec原子性和完整300秒性能未决。当前7次WSL均只读取证，T0/R=null，安装/下载/服务/校准/模型0。\n\n'
 'RA-1/2/3=CONDITIONAL_PASS，RA-4=PASS_STATIC。旧TR-A PREFLIGHT_FAILED及旧账/回执/封存保持，旧attempt不恢复。'
 'RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。\n\n'
 '[最终裁决](DCL-R6-RuntimeAdapt-Fix/FINAL_DECISION.md) · [来源条件](DCL-R6-RuntimeAdapt-Fix/RUNTIME_PROVENANCE_ASSESSMENT.md) · '
 '[新源码锁](DCL-R6-RuntimeAdapt-Fix/SOURCE_AND_INPUT_LOCK.md) · [TR-A2申请](DCL-R6-RuntimeAdapt-Fix/NEXT_DYNAMIC_AUTHORIZATION.md) · '
 '[证据索引](DCL-R6-RuntimeAdapt-Fix/EVIDENCE_INDEX.md)\n\n以下逐字节保留先前记录。\n\n---\n\n')
navigation=[];(E/'navigation_after').mkdir()
for name in history['nav']:
    original=(E/'navigation_before'/name).read_bytes();assert(B/name).read_bytes()==original,'CONCURRENT_NAV_CHANGE:'+name
    (B/name).write_bytes(prefix.encode('utf-8')+original);shutil.copyfile(B/name,E/'navigation_after'/name)
    navigation.append({'name':name,'original_sha256':hashlib.sha256(original).hexdigest(),'original_exact_suffix':(B/name).read_bytes().endswith(original),'new_sha256':h(B/name)})
put(E/'HISTORY_PROTECTION_CHECK.json',{'status':'MATCH','historical_files':len(history['files']),'history_mismatches':history_errors,
 'mispath_files':47,'mispath_mismatches':dup_errors,'mispath_actions':'READ_HASH_ONLY','navigation':navigation,
 'old_policy_rejection':'blocked by policy retained','historical_budgets_or_locks_modified':0,'system_runtime_files_modified':0,
 'system_package_changes_by_task':0,'new_candidate_only':'ra01/RuntimeAdapt-static-1/r1'})
required=['RUNTIME_CHANGE_TIMELINE.md','GLIBC_VERSION_AND_PACKAGE_AUDIT.md','ELF_THREE_COMPONENT_AUDIT.md','RUNTIME_PROVENANCE_ASSESSMENT.md',
 'PYTHON_NATIVE_ABI_COMPATIBILITY.md','RUNTIME_SECURITY_IMPACT_MATRIX.md','RUNTIME_LOCK_REFINEMENT.md','RUNTIME_NEGATIVE_REGRESSION_PLAN.md',
 'STATIC_VERIFICATION_RESULTS.md','SOURCE_AND_INPUT_LOCK.md','NEXT_DYNAMIC_AUTHORIZATION.md','FINAL_DECISION.md']
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
for p in O.rglob('*.json'):load(p);parsed+=1
put(O/'SOURCE_INDEX.json',{'schema':'RA-SOURCE-INDEX/1','version':r['version'],'files':lock['files'],'source_before':'evidence/SOURCE_BEFORE','source_final':'evidence/SOURCE_FINAL_R1',
 'runtime_pin_diff':'evidence/RUNTIME_PIN_DIFF.json','provenance':'evidence/PROVENANCE_AUDIT.json','provenance_decision':'evidence/PROVENANCE_DECISION.json',
 'static_ABI':'evidence/ELF_ABI_AUDIT.json','platform_snapshot':'evidence/PLATFORM_EXPORT.json','runtime_qualification':'UNRUN','next_authorization':'REQUEST_ONLY'})
rows=[]
for p in sorted(O.rglob('*')):
    if p.is_file() and p.name not in ['OUTPUT_MANIFEST.json','RUNTIME_ADAPT_EVIDENCE.zip','RUNTIME_ADAPT_EVIDENCE.zip.sha256','DELIVERY_CHECK.json']:
        rows.append({'host':str(p),'archive_path':'research/'+p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':h(p)})
assert len({row['archive_path'] for row in rows})==len(rows)
put(O/'OUTPUT_MANIFEST.json',{'schema':'RA-STATIC-READONLY-MANIFEST/1','version':r['version'],'classification':'Conditional static runtime identity/provenance/ABI and read-only native query evidence; no workload qualification',
 'files':rows,'exclusions':['OUTPUT_MANIFEST.json (extra ZIP member)','RUNTIME_ADAPT_EVIDENCE.zip','RUNTIME_ADAPT_EVIDENCE.zip.sha256','evidence/DELIVERY_CHECK.json']})
with zipfile.ZipFile(O/'RUNTIME_ADAPT_EVIDENCE.zip','x',zipfile.ZIP_DEFLATED) as z:
    for row in rows:z.write(row['host'],row['archive_path'])
    z.write(O/'OUTPUT_MANIFEST.json','OUTPUT_MANIFEST.json')
errors=[]
with zipfile.ZipFile(O/'RUNTIME_ADAPT_EVIDENCE.zip') as z:
    assert z.testzip() is None
    for row in rows:
        raw=z.read(row['archive_path'])
        if len(raw)!=row['bytes'] or hashlib.sha256(raw).hexdigest()!=row['sha256']:errors.append(row['archive_path'])
    assert z.read('OUTPUT_MANIFEST.json')==(O/'OUTPUT_MANIFEST.json').read_bytes();entries=len(z.namelist())
assert not errors
zipsha=h(O/'RUNTIME_ADAPT_EVIDENCE.zip');(O/'RUNTIME_ADAPT_EVIDENCE.zip.sha256').write_text(zipsha+'  RUNTIME_ADAPT_EVIDENCE.zip\n',encoding='ascii')
delivery={'schema':'RA-DELIVERY/1','status':'PASS_STATIC_READONLY_DELIVERY_ONLY','version':r['version'],'report_date':'2026-11-13 Asia/Shanghai',
 'RA-1':'CONDITIONAL_PASS','RA-2':'CONDITIONAL_PASS','RA-3':'CONDITIONAL_PASS','RA-4':'PASS_STATIC','required_reports':12,
 'source_files':64,'programs':44,'Linux_files_planned':62,'static_checks':20,'pure_host_ELF_parser_probes':3,'source_errors':source_errors,
 'runtime_pins_changed':3,'readonly_WSL_invocations':7,'dynamic_workload_tests':0,'Launcher_or_services':0,'T0':None,'R':None,'package_installs':0,'downloads':0,'WSL_restarts':0,
 'static_ELF_seeds':66,'resolved_objects':114,'unresolved_DT_NEEDED':0,'missing_version_groups':0,
 'cached_Ubuntu_signature_and_index_checks':2,'new_deb_payload_reconstruction':False,'provenance_assumptions_explicitly_required':True,
 'path_to_exec_atomicity':'UNRESOLVED','protected_byte_files':13,'protected_AST_members':70,'historical_files':len(history['files']),'history_mismatches':history_errors,
 'mispath_files':47,'mispath_mismatches':dup_errors,'RA32_executed':0,'mutants_detected':0,'new_minimal_completed':3133,'new_minimal_hard':4417,'new_full_hard':68498,
 'actual_receipts_created':0,'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
 'STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED','JSON_parsed_before_manifest':parsed,'links_checked':links,'link_errors':link_errors,
 'manifest_rows':len(rows),'ZIP_entries':entries,'ZIP_stream_errors':errors,'manifest_sha256':h(O/'OUTPUT_MANIFEST.json'),'ZIP_sha256':zipsha,
 'ZIP_bytes':(O/'RUNTIME_ADAPT_EVIDENCE.zip').stat().st_size,'source_manifest_sha256':r['manifest_sha256'],'execution_lock_sha256':r['execution_lock_sha256'],
 'sealed_utc':datetime.now(timezone.utc).isoformat(),'admin_elapsed_seconds':time.perf_counter()-tick,'self_excluded_from_manifest_and_zip':True}
put(E/'DELIVERY_CHECK.json',delivery)
print(json.dumps({key:delivery[key] for key in ['status','version','historical_files','manifest_rows','ZIP_entries','ZIP_sha256','ZIP_bytes','links_checked']},ensure_ascii=False))
