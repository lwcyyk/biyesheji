"""Static delivery sealing only; never grants dynamic execution authority."""
from pathlib import Path
import hashlib,json,re,shutil,time,zipfile
from datetime import datetime,timezone
E=Path(__file__).resolve().parent;O=E.parent;B=O.parent
W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\pf01');tick=time.perf_counter()
def load(p):return json.loads(Path(p).read_bytes())
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
assert not (O/'PHASE_FINALIZER_EVIDENCE.zip').exists() and not (E/'DELIVERY_CHECK.json').exists()
result=load(E/'STATIC_RESULT.json');lock=load(E/'STATIC_WORKSPACE_LOCK.json');history=load(E/'BASELINE_LOCK.json')
assert result['version']=='PTA-PhaseFinalizer-static-1/r3' and result['WSL_calls']==0
source_errors=[]
for row in lock['files']:
    for base in [W,E/'SOURCE_FINAL_R3']:
        if h(base/row['relative'])!=row['sha256']:source_errors.append(str(base/row['relative']))
assert not source_errors and not list(W.rglob('*.pyc'))
assert {p.relative_to(W).as_posix() for p in W.rglob('*') if p.is_file()}=={r['relative'] for r in lock['files']}
candidate_checks=[]
for revision in ['r1','r2']:
    prior=load(E/'versions'/revision/'STATIC_WORKSPACE_LOCK.json');errors=[]
    folder=E/('SOURCE_FINAL_'+revision.upper())
    for row in prior['files']:
        if h(folder/row['relative'])!=row['sha256']:errors.append(row['relative'])
    assert not errors;candidate_checks.append({'revision':revision,'files':len(prior['files']),'errors':errors})
put(E/'CANDIDATE_SNAPSHOT_CHECK.json',candidate_checks)
m=load(W/'inputs/static_manifest.json');execution=load(W/'inputs/execution_lock.json')
assert h(W/'inputs/static_manifest.json')==result['manifest_sha256']==execution['static_manifest_sha256']
assert h(W/'inputs/execution_lock.json')==result['execution_lock_sha256']
for rel,expected in m['source_hashes'].items():assert h(W/'src'/rel)==expected
for rel,expected in m['bound_inputs'].items():assert h(W/rel)==expected
assert h(W/'host/windows_entry.py')==execution['windows_entry_sha256'] and h(W/'host/startup_finalize.py')==execution['startup_host_finalizer_sha256']
assert execution['startup_post_exit_command'][-2]=='/var/lib/dcl-r6/pf01/src/admin_postexit.py'
template=load(E/'PHASE_A_NORMAL_START_AUTHORIZATION_TEMPLATE.json')
assert template['status']=='TEMPLATE_UNAPPROVED' and template['authorization_text_sha256'] is None
assert all(v is False for k,v in template.items() if k.endswith('_explicitly_approved'))
assert not Path(load(W/'inputs/batch_identity.json')['host_control']).exists()
history_errors=[]
for row in history['files']:
    p=Path(row['host'])
    if not p.is_file() or p.stat().st_size!=row['bytes'] or h(p)!=row['sha256']:history_errors.append(row['host'])
assert not history_errors
dups=load(B/'DCL-R6-batch02-Perf/evidence/DUPLICATE_REGISTER.json');dup_errors=[]
for row in dups['files']:
    if h(Path(dups['path'])/row['relative'])!=row['duplicate_sha256']:dup_errors.append(row['relative'])
assert len(dups['files'])==47 and not dup_errors
prefix=('## PTA-PhaseFinalizer 最终静态增量（2026-11-12）\n\n'
 '**PTA-PhaseFinalizer-static-1/r3已冻结，新增Native执行0。** 阶段发布与Root读取共享有界锁；行政收尾使用固定Root源bootstrap，装载前设置AS1GiB和单次30秒界，当前回执/登记角色身份与native/admin证据分轴。'
 '历史精确phase操作数继续UNKNOWN，PF-G1=PARTIAL；G2–4=CONDITIONAL_PASS，G5=PASS_STATIC。\n\n'
 '55文件/38程序、28静态断言、最终5项主机受控探针通过；PT64保持，PF48/8mutant实际UNRUN。新完整访问硬界66770，正常A硬2689；WSL/服务/预算/模型执行0。'
 '旧batch11 native成功与自动post失败原件保持；研究实施门CLOSED、严格分离0、F1/F4=UNRUN_RESOURCE_GATE。\n\n'
 '[最终裁决](DCL-R6-PTA-PhaseFinalizer-Fix/FINAL_DECISION.md) · [根因精化](DCL-R6-PTA-PhaseFinalizer-Fix/PHASE_DRIFT_ROOT_CAUSE.md) · '
 '[源码锁](DCL-R6-PTA-PhaseFinalizer-Fix/SOURCE_AND_INPUT_LOCK.md) · [下一有限申请](DCL-R6-PTA-PhaseFinalizer-Fix/NEXT_DYNAMIC_AUTHORIZATION.md) · '
 '[证据索引](DCL-R6-PTA-PhaseFinalizer-Fix/EVIDENCE_INDEX.md)\n\n以下逐字节保留先前记录。\n\n---\n\n')
navigation=[];(E/'navigation_after').mkdir()
for name in history['nav']:
    before=(E/'navigation_before'/name).read_bytes();assert (B/name).read_bytes()==before,'CONCURRENT_NAV_CHANGE:'+name
    (B/name).write_bytes(prefix.encode('utf-8')+before);shutil.copyfile(B/name,E/'navigation_after'/name)
    navigation.append({'name':name,'original_sha256':hashlib.sha256(before).hexdigest(),'exact_original_suffix':(B/name).read_bytes().endswith(before),'new_sha256':h(B/name)})
put(E/'HISTORY_PROTECTION_CHECK.json',{'status':'MATCH','historical_files':len(history['files']),'history_mismatches':history_errors,
 'mispath_files':47,'mispath_mismatches':dup_errors,'mispath_actions':'READ_HASH_ONLY','navigation':navigation,
 'old_policy_rejection':'blocked by policy retained','old_budgets_modified':0,'historical_source_or_archives_modified':0,
 'candidate_snapshots':candidate_checks,'Linux_state_inspected_this_round':False})
required=['PHASE_DRIFT_ROOT_CAUSE.md','PHASE_TRANSITION_TIMELINE.md','PHASE_CONSISTENCY_CONTRACT.md','ADMIN_FINALIZER_IMPORT_ROOT_CAUSE.md',
 'ADMIN_FINALIZER_EXECUTION_CONTRACT.md','AUTOMATIC_SHUTDOWN_AUDIT.md','PHASE_FINALIZER_FIX_IMPLEMENTATION.md','REGRESSION_AND_MUTATION_PLAN.md',
 'STATIC_VERIFICATION_RESULTS.md','SOURCE_AND_INPUT_LOCK.md','NEXT_DYNAMIC_AUTHORIZATION.md','FINAL_DECISION.md']
assert all((O/n).exists() for n in required)
links=0;link_errors=[]
for p in O.glob('*.md'):
    raw=p.read_text(encoding='utf-8');assert '不是' not in raw
    for match in re.finditer(r'\[[^\]\n]+\]\(([^)\n]+)\)',raw):
        rel=match.group(1).split('#',1)[0]
        if not rel or re.match(r'^[a-z]+://',rel):continue
        links+=1;target=p.parent/rel
        if not target.exists() and target!=E/'DELIVERY_CHECK.json':link_errors.append({'file':p.name,'target':rel})
assert not link_errors,link_errors
parsed=0
for p in O.rglob('*.json'):load(p);parsed+=1
put(O/'SOURCE_INDEX.json',{'schema':'PF-SOURCE-INDEX/1','version':result['version'],'files':lock['files'],'final_source':'evidence/SOURCE_FINAL_R3',
 'original_source':'evidence/SOURCE_BEFORE','full_diff':'evidence/FULL_DIFF.patch','historical_originals':'evidence/PTA_ORIGINALS',
 'historical_facts':'evidence/HISTORICAL_FAILURE_FACTS.json','new_dynamic_tests':'UNRUN','WSL_calls':0,'next_authorization':'REQUEST_ONLY'})
rows=[]
for p in sorted(O.rglob('*')):
    if p.is_file() and p.name not in ('OUTPUT_MANIFEST.json','PHASE_FINALIZER_EVIDENCE.zip','PHASE_FINALIZER_EVIDENCE.zip.sha256','DELIVERY_CHECK.json'):
        rows.append({'host':str(p),'archive_path':'research/'+p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':h(p)})
assert len({r['archive_path'] for r in rows})==len(rows)
put(O/'OUTPUT_MANIFEST.json',{'schema':'PF-STATIC-ADMIN-MANIFEST/1','version':result['version'],'files':rows,
 'scope':'Static source/facts/checks/requests only; no native execution','exclusions':['OUTPUT_MANIFEST.json (extra ZIP member)','PHASE_FINALIZER_EVIDENCE.zip','PHASE_FINALIZER_EVIDENCE.zip.sha256','evidence/DELIVERY_CHECK.json']})
with zipfile.ZipFile(O/'PHASE_FINALIZER_EVIDENCE.zip','x',zipfile.ZIP_DEFLATED) as z:
    for row in rows:z.write(row['host'],row['archive_path'])
    z.write(O/'OUTPUT_MANIFEST.json','OUTPUT_MANIFEST.json')
zip_errors=[]
with zipfile.ZipFile(O/'PHASE_FINALIZER_EVIDENCE.zip') as z:
    assert z.testzip() is None
    for row in rows:
        raw=z.read(row['archive_path'])
        if len(raw)!=row['bytes'] or hashlib.sha256(raw).hexdigest()!=row['sha256']:zip_errors.append(row['archive_path'])
    assert z.read('OUTPUT_MANIFEST.json')==(O/'OUTPUT_MANIFEST.json').read_bytes();entries=len(z.namelist())
assert not zip_errors
zipsha=h(O/'PHASE_FINALIZER_EVIDENCE.zip');(O/'PHASE_FINALIZER_EVIDENCE.zip.sha256').write_text(zipsha+'  PHASE_FINALIZER_EVIDENCE.zip\n',encoding='ascii')
delivery={'schema':'PF-DELIVERY/1','status':'PASS_STATIC_ADMIN_DELIVERY_ONLY','version':result['version'],
 'PF-G1':'PARTIAL','PF-G2':'CONDITIONAL_PASS','PF-G3':'CONDITIONAL_PASS','PF-G4':'CONDITIONAL_PASS','PF-G5':'PASS_STATIC',
 'required_reports':12,'files':55,'programs':38,'Linux_files_planned':53,'source_errors':source_errors,'static_AST_checks':28,
 'host_inert_probes_final':5,'host_inert_probes_all_candidates':15,'protected_byte_files':13,'protected_AST_members':57,
 'historical_files':len(history['files']),'history_mismatches':history_errors,'mispath_files':47,'mispath_mismatches':dup_errors,
 'WSL_calls':0,'native_imports':0,'roles_started':0,'PT64_executed':0,'PF48_executed':0,'mutants_detected':0,'T0':None,'R':None,
 'historical_native_seal':'NATIVE_SEAL_COMPLETED (batch11)','historical_automatic_admin':'ADMIN_EVIDENCE_UNRESOLVED (batch11)',
 'new_full_calibration_hard':66770,'new_minimal_hard':2689,'next_dynamic_authorization':'REQUEST_ONLY','actual_receipts_created':0,
 'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
 'STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED','JSON_parsed_before_manifest':parsed,'links_checked':links,'link_errors':link_errors,
 'manifest_rows':len(rows),'ZIP_entries':entries,'ZIP_stream_errors':zip_errors,'manifest_sha256':h(O/'OUTPUT_MANIFEST.json'),
 'ZIP_sha256':zipsha,'ZIP_bytes':(O/'PHASE_FINALIZER_EVIDENCE.zip').stat().st_size,'source_manifest_sha256':result['manifest_sha256'],
 'execution_lock_sha256':result['execution_lock_sha256'],'sealed_utc':datetime.now(timezone.utc).isoformat(),
 'admin_elapsed_seconds':time.perf_counter()-tick,'self_excluded_from_manifest_and_zip':True}
put(E/'DELIVERY_CHECK.json',delivery)
print(json.dumps({k:delivery[k] for k in ['status','version','historical_files','manifest_rows','ZIP_entries','ZIP_sha256','ZIP_bytes','links_checked']},ensure_ascii=False))
