"""Administrative delivery archive after a closed frozen run; no seal/test replay."""
from pathlib import Path
import hashlib,json,re,shutil,time,zipfile
from datetime import datetime,timezone
E=Path(__file__).resolve().parent;O=E.parent;B=O.parent
I=Path(r'D:\毕业设计\DCL-R6-isolated-verification\batch12');W=I.parent/'pf01';tick=time.perf_counter()
def load(p):return json.loads(Path(p).read_bytes())
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
    if Path(p).exists():
        assert load(p)==x,'ADMIN_EXISTING_DATA_DIFFERS:'+str(p)
        return
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
assert not (O/'PFA_EVIDENCE.zip').exists() and not (E/'DELIVERY_CHECK.json').exists()
actual=load(E/'ACTUAL_RESULTS.json');audit=load(E/'POSTRUN_AUDIT.json');source=load(E/'SOURCE_AND_SCOPE_ADMISSION.json')
assert actual['target_entry_calls']==1 and actual['R']==1907 and actual['tests_executed']==112 and actual['mutants_detected']==17
assert not audit['payload_processes'] and not audit['root_role_processes'] and not audit['parent_cgroup_exists']
assert audit['closed_marker_exists'] and not audit['native_seal_exists']
source_errors=[]
for row in source['files']:
    for base in [W,E/'FROZEN_SOURCE_REFERENCE',I/'FROZEN_PF']:
        if h(base/row['relative'])!=row['sha256']:source_errors.append(str(base/row['relative']))
assert not source_errors and not list(W.rglob('*.pyc'))
native_errors=[]
for row in load(E/'NATIVE_EXPORT_LOCK.json')['files']:
    if h(row['host'])!=row['sha256']:native_errors.append(row['host'])
assert not native_errors
history=load(E/'BASELINE_LOCK.json');history_errors=[]
for row in history['files']:
    p=Path(row['host'])
    if not p.is_file() or p.stat().st_size!=row['bytes'] or h(p)!=row['sha256']:history_errors.append(row['host'])
assert not history_errors
dups=load(B/'DCL-R6-batch02-Perf/evidence/DUPLICATE_REGISTER.json');dup_errors=[]
for row in dups['files']:
    if h(Path(dups['path'])/row['relative'])!=row['duplicate_sha256']:dup_errors.append(row['relative'])
assert len(dups['files'])==47 and not dup_errors
prefix=('## DCL-R6-PTA-PF-A 最新动态增量（2026-11-12）\n\n'
 '**batch12/r3真实进入RUNNING、C00通过；PT64=55 PASS＋9变异检出，PF48=40 PASS＋8变异检出。完整A验收INCONCLUSIVE。** '
 'R1907、1907事务/3814行；正常自动CLOSED、waitpid0与角色/组空；自动行政包171/172逐流核验通过。native seal在终态期限辅助路径经G.state被拒绝，状态UNRESOLVED、未生成原生包；内部UNKNOWN与观测缺口保持。\n\n'
 '入口1次、源码修改/测试重跑/人工清理/额外兜底归档0。先对终态只读期限与必要观测作最小静态补缺，再新身份/锁/授权验收；当前不恢复MR/C09或模型。'
 'RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。\n\n'
 '[21项回答](DCL-R6-PTA-PF-A/PFA_FINAL_DECISION.md) · [新缺口](DCL-R6-PTA-PF-A/PFA_COUNTEREXAMPLES.md) · '
 '[自动行政](DCL-R6-PTA-PF-A/PFA_ADMIN_FINALIZER_RESULTS.md) · [证据索引](DCL-R6-PTA-PF-A/EVIDENCE_INDEX.md) · '
 '[下一静态范围](DCL-R6-PTA-PF-A/NEXT_STATIC_REPAIR_REQUEST.md)\n\n以下逐字节保留先前记录。\n\n---\n\n')
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
 'old_policy_rejection':'blocked by policy retained','old_budgets_modified':0,'frozen_source_edits':0,
 'historical_batch11_native_success_and_unknown_operands':'Preserved','new_control_authorized_additions':'DCL-R6-PTA-PhaseFinalizer-Fix/authorization/batch12-r3 only'})
required=['PFA_AUTHORIZATION_AND_LOCK.md','PFA_NATIVE_PHASE_RESULTS.md','PFA_LOCK_AND_VERSION_RESULTS.md','PFA_WORK_GUARD_RESULTS.md',
 'PFA_PT64_RESULTS.md','PFA_PF48_RESULTS.md','PFA_AUTOMATIC_CLOSURE_RESULTS.md','PFA_ADMIN_FINALIZER_RESULTS.md','PFA_NATIVE_SEAL_RESULTS.md',
 'PFA_RESOURCE_ACCOUNTING.md','PFA_EXECUTION_TIMELINE.md','PFA_COUNTEREXAMPLES.md','PFA_FINAL_DECISION.md']
assert all((O/n).exists() for n in required)
links=0;link_errors=[]
for p in O.glob('*.md'):
    raw=p.read_text(encoding='utf-8');assert '不是' not in raw
    for match in re.finditer(r'\[[^\]\n]+\]\(([^)\n]+)\)',raw):
        target=match.group(1).split('#',1)[0]
        if not target or re.match(r'^[a-z]+://',target):continue
        links+=1
        if not (p.parent/target).exists() and p.parent/target!=E/'DELIVERY_CHECK.json':link_errors.append({'file':p.name,'target':target})
assert not link_errors,link_errors
parsed=0
for base in [O,I]:
    for p in base.rglob('*.json'):load(p);parsed+=1
put(O/'SOURCE_INDEX.json',{'schema':'PFA-SOURCE-INDEX/1','version':actual['revision'],'source_files':source['files'],
 'native_export_lock':'evidence/NATIVE_EXPORT_LOCK.json','source_export_lock':'evidence/FROZEN_SOURCE_EXPORT_LOCK.json',
 'automatic_admin_verification':'evidence/AUTOMATIC_ADMIN_VERIFICATION.json','case_results':'evidence/TEST_CASE_RESULTS.json',
 'history':'evidence/BASELINE_LOCK.json','native_seal':'NATIVE_SEAL_UNRESOLVED','automatic_admin':'ADMIN_EVIDENCE_SEALED',
 'private_originals':'Nonce preserved only in original private files/local archives; omitted from reports'})
rows=[]
for p in sorted(O.rglob('*')):
    if p.is_file() and p.name not in ['OUTPUT_MANIFEST.json','PFA_EVIDENCE.zip','PFA_EVIDENCE.zip.sha256','DELIVERY_CHECK.json']:
        rows.append({'host':str(p),'archive_path':'research/'+p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':h(p)})
for name,prefix in [('NATIVE_EXPORT_LOCK.json','export/native'),('FROZEN_SOURCE_EXPORT_LOCK.json','export/frozen')]:
    for row in load(E/name)['files']:
        p=Path(row['host']);rows.append({'host':str(p),'archive_path':prefix+'/'+row['relative'],'bytes':p.stat().st_size,'sha256':h(p)})
assert len({r['archive_path'] for r in rows})==len(rows)
put(O/'OUTPUT_MANIFEST.json',{'schema':'PFA-RESEARCH-MANIFEST/1','classification':'Research summary and exact original exports after frozen automatic administrative sealing',
 'automatic_admin_status':'ADMIN_EVIDENCE_SEALED','native_seal_status':'NATIVE_SEAL_UNRESOLVED','files':rows,
 'exclusions':['OUTPUT_MANIFEST.json (extra ZIP member)','PFA_EVIDENCE.zip','PFA_EVIDENCE.zip.sha256','evidence/DELIVERY_CHECK.json']})
with zipfile.ZipFile(O/'PFA_EVIDENCE.zip','x',zipfile.ZIP_DEFLATED) as z:
    for row in rows:z.write(row['host'],row['archive_path'])
    z.write(O/'OUTPUT_MANIFEST.json','OUTPUT_MANIFEST.json')
errors=[]
with zipfile.ZipFile(O/'PFA_EVIDENCE.zip') as z:
    assert z.testzip() is None
    for row in rows:
        raw=z.read(row['archive_path'])
        if len(raw)!=row['bytes'] or hashlib.sha256(raw).hexdigest()!=row['sha256']:errors.append(row['archive_path'])
    assert z.read('OUTPUT_MANIFEST.json')==(O/'OUTPUT_MANIFEST.json').read_bytes();entries=len(z.namelist())
assert not errors
zipsha=h(O/'PFA_EVIDENCE.zip');(O/'PFA_EVIDENCE.zip.sha256').write_text(zipsha+'  PFA_EVIDENCE.zip\n',encoding='ascii')
delivery={'schema':'PFA-DELIVERY/1','status':'PASS_ADMINISTRATIVE_DELIVERY_ONLY','version':actual['revision'],'overall_verdict':'INCONCLUSIVE',
 'reason':'Normal WORK/C00/PT64/PF48 and automatic admin succeeded; native seal unresolved and fine telemetry gaps retained',
 'PF-A1':actual['PF-A1'],'PF-A2':actual['PF-A2'],'PF-A3':actual['PF-A3'],'PF-A4':actual['PF-A4'],'PF-A5':actual['PF-A5'],'PF-A6':actual['PF-A6'],'PF-A7':actual['PF-A7'],
 'required_reports':13,'source_files':55,'programs':38,'source_errors':source_errors,'native_files':157,'native_export_errors':native_errors,
 'historical_files':len(history['files']),'history_mismatches':history_errors,'mispath_files':47,'mispath_mismatches':dup_errors,
 'active_entry_calls':1,'automatic_post_exit_calls':1,'administrative_WSL_calls':3,'total_WSL_calls':5,'test_retries':0,'source_edits':0,
 'T0':actual['T0'],'R':1907,'transactions':1907,'journal_lines':3814,'PT64_accepted':64,'PT_mutants_detected':9,'PF48_accepted':48,'PF_mutants_detected':8,
 'native_seal_status':'NATIVE_SEAL_UNRESOLVED','automatic_admin_status':'ADMIN_EVIDENCE_SEALED','automatic_admin_manifest_rows':171,'automatic_admin_ZIP_entries':172,
 'extra_fallback_archival_calls':0,'manual_cleanup_calls':0,'internal_status':'UNKNOWN','all_roles_and_parent_empty':True,
 'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
 'STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED','JSON_parsed_before_manifest':parsed,'links_checked':links,'link_errors':link_errors,
 'manifest_rows':len(rows),'ZIP_entries':entries,'ZIP_stream_errors':errors,'manifest_sha256':h(O/'OUTPUT_MANIFEST.json'),'ZIP_sha256':zipsha,
 'ZIP_bytes':(O/'PFA_EVIDENCE.zip').stat().st_size,'sealed_utc':datetime.now(timezone.utc).isoformat(),'admin_elapsed_seconds':time.perf_counter()-tick,
 'self_excluded_from_manifest_and_zip':True}
put(E/'DELIVERY_CHECK.json',delivery)
print(json.dumps({k:delivery[k] for k in ['overall_verdict','historical_files','manifest_rows','ZIP_entries','ZIP_sha256','ZIP_bytes','links_checked']},ensure_ascii=False))
