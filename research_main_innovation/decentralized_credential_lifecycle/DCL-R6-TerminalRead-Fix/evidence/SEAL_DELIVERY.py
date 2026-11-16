"""Static administrative packaging only; no WSL or target function execution."""
from pathlib import Path
import hashlib,json,re,shutil,time,zipfile
from datetime import datetime,timezone
E=Path(__file__).resolve().parent;O=E.parent;B=O.parent;W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\tr01');tick=time.perf_counter()
def load(p):return json.loads(Path(p).read_bytes())
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
    if Path(p).exists():
        assert load(p)==x,'ADMIN_EXISTING_DATA_DIFFERS:'+str(p)
        return
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
assert not(O/'TERMINAL_READ_EVIDENCE.zip').exists() and not(E/'DELIVERY_CHECK.json').exists()
r=load(E/'STATIC_RESULT.json');lock=load(E/'STATIC_WORKSPACE_LOCK.json');history=load(E/'BASELINE_LOCK.json')
source_errors=[]
for row in lock['files']:
    for base in [W,E/'SOURCE_FINAL_R1']:
        if h(base/row['relative'])!=row['sha256']:source_errors.append(str(base/row['relative']))
assert not source_errors and not list(W.rglob('*.pyc'))
assert len(lock['files'])==59 and len(list(W.rglob('*.py')))==41
assert {p.relative_to(W).as_posix() for p in W.rglob('*') if p.is_file()}=={row['relative'] for row in lock['files']}
m=load(W/'inputs/static_manifest.json');l=load(W/'inputs/execution_lock.json')
assert h(W/'inputs/static_manifest.json')==r['manifest_sha256']==l['static_manifest_sha256']
assert h(W/'inputs/execution_lock.json')==r['execution_lock_sha256']
for rel,sha in m['source_hashes'].items():assert h(W/'src'/rel)==sha
for rel,sha in m['bound_inputs'].items():assert h(W/rel)==sha
assert not Path(load(W/'inputs/batch_identity.json')['host_control']).exists()
template=load(E/'PHASE_A_NORMAL_START_AUTHORIZATION_TEMPLATE.json')
assert template['status']=='TEMPLATE_UNAPPROVED' and template['authorization_text_sha256'] is None
assert all(value is False for key,value in template.items() if key.endswith('_explicitly_approved'))
history_errors=[]
for row in history['files']:
    p=Path(row['host'])
    if not p.is_file() or p.stat().st_size!=row['bytes'] or h(p)!=row['sha256']:history_errors.append(row['host'])
assert not history_errors
dups=load(B/'DCL-R6-batch02-Perf/evidence/DUPLICATE_REGISTER.json');dup_errors=[]
for row in dups['files']:
    if h(Path(dups['path'])/row['relative'])!=row['duplicate_sha256']:dup_errors.append(row['relative'])
assert len(dups['files'])==47 and not dup_errors
prefix=('## DCL-R6-TerminalRead 最终静态增量（2026-11-13）\n\n'
 '**TerminalRead-static-1/r1已冻结，新增原生执行0。** 独立终态只读接口复用原window/journal/phase/关闭/退出证据，活动态守卫保持；native在原退出等待之后接入只读前提及CLOSED活动拒绝回执。'
 '原host finalizer/entry字节保持，内部缺关闭收据的UNKNOWN不升级。\n\n'
 '59文件/41程序、28静态断言、13字节程序/70成员AST核验；新增TR40/8mutant全部UNRUN。正常A硬3649、完整硬67730；本轮WSL/T0/预算/套件/模型运行0。'
 'TR-G1=PASS_STATIC、G2=CONDITIONAL_PASS、G3=PARTIAL、G4=PASS_STATIC。历史PFA native UNRESOLVED/internal UNKNOWN/admin成功保持。\n\n'
 'RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。'
 '下一步限于审阅独立新batch13-r1正常A，当前没有实际回执或运行实体。\n\n'
 '[最终裁决](DCL-R6-TerminalRead-Fix/FINAL_DECISION.md) · [只读合同](DCL-R6-TerminalRead-Fix/TERMINAL_EVIDENCE_CONTRACT.md) · '
 '[native依赖](DCL-R6-TerminalRead-Fix/NATIVE_SEAL_DEPENDENCY_ANALYSIS.md) · [下一申请](DCL-R6-TerminalRead-Fix/NEXT_DYNAMIC_AUTHORIZATION.md) · '
 '[证据索引](DCL-R6-TerminalRead-Fix/EVIDENCE_INDEX.md)\n\n以下逐字节保留先前记录。\n\n---\n\n')
navigation=[];(E/'navigation_after').mkdir(exist_ok=True)
for name in history['nav']:
    before=(E/'navigation_before'/name).read_bytes();target=prefix.encode('utf-8')+before
    current=(B/name).read_bytes();assert current in (before,target),'CONCURRENT_NAV_CHANGE:'+name
    if current==before:(B/name).write_bytes(target)
    dest=E/'navigation_after'/name
    if dest.exists():assert dest.read_bytes()==target
    else:shutil.copyfile(B/name,dest)
    navigation.append({'name':name,'original_sha256':hashlib.sha256(before).hexdigest(),'original_exact_suffix':(B/name).read_bytes().endswith(before),'new_sha256':h(B/name)})
put(E/'HISTORY_PROTECTION_CHECK.json',{'status':'MATCH','historical_files':len(history['files']),'history_mismatches':history_errors,
 'mispath_files':47,'mispath_mismatches':dup_errors,'mispath_actions':'READ_HASH_ONLY','navigation':navigation,
 'old_policy_rejection':'blocked by policy retained','historical_budgets_or_sources_modified':0,
 'historical_PFA_native':'NATIVE_SEAL_UNRESOLVED','historical_PFA_internal':'UNKNOWN','historical_PFA_admin':'ADMIN_EVIDENCE_SEALED'})
required=['TERMINAL_READ_FAILURE_TIMELINE.md','ACTIVE_TERMINAL_INTERFACE_AUDIT.md','TERMINAL_EVIDENCE_CONTRACT.md','DEADLINE_READ_ROOT_CAUSE.md',
 'NATIVE_SEAL_DEPENDENCY_ANALYSIS.md','INTERNAL_UNKNOWN_ANALYSIS.md','TERMINAL_READ_SAFETY_PROPERTIES.md','TERMINAL_READ_FIX_IMPLEMENTATION.md',
 'REGRESSION_AND_MUTATION_PLAN.md','STATIC_VERIFICATION_RESULTS.md','SOURCE_AND_INPUT_LOCK.md','NEXT_DYNAMIC_AUTHORIZATION.md','FINAL_DECISION.md']
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
put(O/'SOURCE_INDEX.json',{'schema':'TR-SOURCE-INDEX/1','version':r['version'],'files':lock['files'],'before':'evidence/SOURCE_BEFORE',
 'after':'evidence/SOURCE_FINAL_R1','diff':'evidence/FULL_DIFF.patch','historical_originals':'evidence/PFA_ORIGINALS',
 'new_dynamic_status':'UNRUN','next_authorization':'REQUEST_ONLY','WSL_calls':0})
rows=[]
for p in sorted(O.rglob('*')):
    if p.is_file() and p.name not in ['OUTPUT_MANIFEST.json','TERMINAL_READ_EVIDENCE.zip','TERMINAL_READ_EVIDENCE.zip.sha256','DELIVERY_CHECK.json']:
        rows.append({'host':str(p),'archive_path':'research/'+p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':h(p)})
assert len({row['archive_path'] for row in rows})==len(rows)
put(O/'OUTPUT_MANIFEST.json',{'schema':'TR-STATIC-MANIFEST/1','version':r['version'],'classification':'Static source/facts/checks/request evidence; native behavior unrun','files':rows,
 'exclusions':['OUTPUT_MANIFEST.json (extra ZIP member)','TERMINAL_READ_EVIDENCE.zip','TERMINAL_READ_EVIDENCE.zip.sha256','evidence/DELIVERY_CHECK.json']})
with zipfile.ZipFile(O/'TERMINAL_READ_EVIDENCE.zip','x',zipfile.ZIP_DEFLATED) as z:
    for row in rows:z.write(row['host'],row['archive_path'])
    z.write(O/'OUTPUT_MANIFEST.json','OUTPUT_MANIFEST.json')
errors=[]
with zipfile.ZipFile(O/'TERMINAL_READ_EVIDENCE.zip') as z:
    assert z.testzip() is None
    for row in rows:
        raw=z.read(row['archive_path'])
        if len(raw)!=row['bytes'] or hashlib.sha256(raw).hexdigest()!=row['sha256']:errors.append(row['archive_path'])
    assert z.read('OUTPUT_MANIFEST.json')==(O/'OUTPUT_MANIFEST.json').read_bytes();entries=len(z.namelist())
assert not errors
zipsha=h(O/'TERMINAL_READ_EVIDENCE.zip');(O/'TERMINAL_READ_EVIDENCE.zip.sha256').write_text(zipsha+'  TERMINAL_READ_EVIDENCE.zip\n',encoding='ascii')
delivery={'schema':'TR-DELIVERY/1','status':'PASS_STATIC_ADMIN_DELIVERY_ONLY','version':r['version'],'report_date':'2026-11-13 Asia/Shanghai',
 'TR-G1':r['TR-G1'],'TR-G2':r['TR-G2'],'TR-G3':r['TR-G3'],'TR-G4':r['TR-G4'],'required_reports':13,'files':59,'programs':41,'Linux_files_planned':57,
 'static_checks':28,'source_errors':source_errors,'protected_byte_files':13,'protected_AST_members':70,'host_finalizer_and_entry_byte_unchanged':True,
 'historical_files':len(history['files']),'history_mismatches':history_errors,'mispath_files':47,'mispath_mismatches':dup_errors,
 'WSL_calls':0,'roles_started':0,'T0':None,'R':None,'PT64_new_executions':0,'PF48_new_executions':0,'TR40_executions':0,'oracle_executions':0,'mutants_detected':0,
 'historical_PFA_native_seal':'NATIVE_SEAL_UNRESOLVED','historical_internal':'UNKNOWN','historical_auto_admin':'ADMIN_EVIDENCE_SEALED',
 'new_native_success':'UNRUN','minimal_completed':2588,'minimal_hard':3649,'full_calibration_hard':67730,'actual_receipts_created':0,
 'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
 'STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED','JSON_parsed_before_manifest':parsed,'links_checked':links,'link_errors':link_errors,
 'manifest_rows':len(rows),'ZIP_entries':entries,'ZIP_stream_errors':errors,'manifest_sha256':h(O/'OUTPUT_MANIFEST.json'),'ZIP_sha256':zipsha,
 'ZIP_bytes':(O/'TERMINAL_READ_EVIDENCE.zip').stat().st_size,'source_manifest_sha256':r['manifest_sha256'],'execution_lock_sha256':r['execution_lock_sha256'],
 'sealed_utc':datetime.now(timezone.utc).isoformat(),'admin_elapsed_seconds':time.perf_counter()-tick,'self_excluded_from_manifest_and_zip':True}
put(E/'DELIVERY_CHECK.json',delivery)
print(json.dumps({k:delivery[k] for k in ['status','version','historical_files','manifest_rows','ZIP_entries','ZIP_sha256','ZIP_bytes','links_checked']},ensure_ascii=False))
