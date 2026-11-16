"""Administrative summary package after frozen A2 close/native/admin completion."""
from pathlib import Path
import hashlib,json,re,shutil,time,zipfile
from datetime import datetime,timezone
E=Path(__file__).resolve().parent;O=E.parent;B=O.parent;I=Path(r'D:\毕业设计\DCL-R6-isolated-verification\batch14');W=I.parent/'ra01';tick=time.perf_counter()
def load(p):return json.loads(Path(p).read_bytes())
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
assert not(O/'TRA2_EVIDENCE.zip').exists() and not(E/'DELIVERY_CHECK.json').exists()
r=load(E/'ACTUAL_RESULTS.json');audit=load(E/'POSTRUN_AUDIT.json');source=load(E/'SOURCE_AND_SCOPE_ADMISSION.json');history=load(E/'BASELINE_LOCK.json')
assert r['R']==3133 and r['checks']==184 and r['mutants_detected']==33 and r['target_entry_calls']==1
assert not audit['payload_processes'] and not audit['root_role_processes'] and not audit['parent_cgroup_exists'] and audit['closed_marker_exists'] and audit['native_seal_exists']
source_errors=[]
for row in source['files']:
    for base in [W,E/'FROZEN_SOURCE_REFERENCE',I/'FROZEN_RA']:
        if h(base/row['relative'])!=row['sha256']:source_errors.append(str(base/row['relative']))
assert not source_errors and not list(W.rglob('*.pyc'))
native_errors=[]
for row in load(E/'NATIVE_EXPORT_LOCK.json')['files']:
    if h(row['host'])!=row['sha256']:native_errors.append(row['host'])
assert not native_errors
history_errors=[]
for row in history['files']:
    p=Path(row['host'])
    if not p.is_file() or p.stat().st_size!=row['bytes'] or h(p)!=row['sha256']:history_errors.append(row['host'])
assert not history_errors
dups=load(B/'DCL-R6-batch02-Perf/evidence/DUPLICATE_REGISTER.json');dup_errors=[]
for row in dups['files']:
    if h(Path(dups['path'])/row['relative'])!=row['duplicate_sha256']:dup_errors.append(row['relative'])
assert len(dups['files'])==47 and not dup_errors
prefix=('## DCL-R6-TR-A2 最新动态增量（2026-11-13）\n\n'
 '**正常最小A2条件性通过。** RuntimeAdapt-static-1/r1/batch14真实新运行时/WORK/C00、PT64/PF48/TR40/RA32共184项与33变异、CLOSED后VALID只读和IPC_CLOSED_DOMINATES、native233/234及自动行政249/250均取得实际证据。'
 'R3133、3133事务/6266行，关键读取摘要与原生包/独立导出一致。\n\n'
 '来源仍CONDITIONAL（受信Root/dpkg/keyring、缺新.deb独立payload），identity原子性/特权更新边界与internal UNKNOWN保留。当前组/角色空，源码修改/重跑/手工seal/后备0；batch14保持CLOSED。'
 '下一步可准备独立MR/C09有限方案，需新身份/摘要与明确许可，未自动开始。\n\n'
 'RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。\n\n'
 '[动态裁决](DCL-R6-TR-A2/TRA2_FINAL_DECISION.md) · [终态读取](DCL-R6-TR-A2/TRA2_TERMINAL_READ_RESULTS.md) · '
 '[native结果](DCL-R6-TR-A2/TRA2_NATIVE_SEAL_RESULTS.md) · [未决边界](DCL-R6-TR-A2/TRA2_COUNTEREXAMPLES.md) · '
 '[证据索引](DCL-R6-TR-A2/EVIDENCE_INDEX.md)\n\n以下逐字节保留先前记录。\n\n---\n\n')
navigation=[];(E/'navigation_after').mkdir()
for name in history['nav']:
    original=(E/'navigation_before'/name).read_bytes();assert(B/name).read_bytes()==original,'CONCURRENT_NAV_CHANGE:'+name
    (B/name).write_bytes(prefix.encode('utf-8')+original);shutil.copyfile(B/name,E/'navigation_after'/name)
    navigation.append({'name':name,'original_sha256':hashlib.sha256(original).hexdigest(),'original_exact_suffix':(B/name).read_bytes().endswith(original),'new_sha256':h(B/name)})
put(E/'HISTORY_PROTECTION_CHECK.json',{'status':'MATCH','historical_files':len(history['files']),'history_mismatches':history_errors,
 'mispath_files':47,'mispath_mismatches':dup_errors,'mispath_actions':'READ_HASH_ONLY','navigation':navigation,'old_policy_rejection':'blocked by policy retained',
 'historical_budgets_or_source_changes':0,'system_runtime_changes_by_task':0,'new_authorized_control':'DCL-R6-RuntimeAdapt-Fix/authorization/batch14-r1'})
required=['TRA2_AUTHORIZATION_AND_LOCK.md','TRA2_RUNTIME_IDENTITY_RESULTS.md','TRA2_NATIVE_COMPATIBILITY_RESULTS.md','TRA2_BOOT_AND_WORK_RESULTS.md',
 'TRA2_TR40_RESULTS.md','TRA2_PT_PF_COMPATIBILITY.md','TRA2_TERMINAL_READ_RESULTS.md','TRA2_ACTIVE_GUARD_RESULTS.md','TRA2_NATIVE_SEAL_RESULTS.md',
 'TRA2_ADMIN_FINALIZER_RESULTS.md','TRA2_INTERNAL_STATE_RESULTS.md','TRA2_RESOURCE_ACCOUNTING.md','TRA2_EXECUTION_TIMELINE.md','TRA2_COUNTEREXAMPLES.md','TRA2_FINAL_DECISION.md']
assert all((O/name).exists() for name in required)
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
for base in [O,I]:
    for p in base.rglob('*.json'):load(p);parsed+=1
put(O/'SOURCE_INDEX.json',{'schema':'TRA2-SOURCE-INDEX/1','version':r['revision'],'source_files':source['files'],'native_originals':'evidence/NATIVE_EXPORT_LOCK.json',
 'frozen_export':'evidence/FROZEN_SOURCE_EXPORT_LOCK.json','runtime_receipts':'evidence/RUNTIME_IDENTITY_RECEIPTS.json','readonly_conservation':'evidence/TERMINAL_READ_CONSERVATION_AUDIT.json',
 'native_verification':'evidence/NATIVE_SEAL_VERIFICATION.json','admin_verification':'evidence/AUTOMATIC_ADMIN_VERIFICATION.json','test_cases':'evidence/TEST_CASE_RESULTS.json',
 'provenance':'CONDITIONAL','internal':'UNKNOWN','private_originals':'Nonce only in private originals/local archive; omitted from reports'})
rows=[]
for p in sorted(O.rglob('*')):
    if p.is_file() and p.name not in ['OUTPUT_MANIFEST.json','TRA2_EVIDENCE.zip','TRA2_EVIDENCE.zip.sha256','DELIVERY_CHECK.json']:
        rows.append({'host':str(p),'archive_path':'research/'+p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':h(p)})
for name,prefix in [('NATIVE_EXPORT_LOCK.json','export/native'),('FROZEN_SOURCE_EXPORT_LOCK.json','export/frozen')]:
    for row in load(E/name)['files']:
        p=Path(row['host']);rows.append({'host':str(p),'archive_path':prefix+'/'+row['relative'],'bytes':p.stat().st_size,'sha256':h(p)})
assert len({row['archive_path'] for row in rows})==len(rows)
put(O/'OUTPUT_MANIFEST.json',{'schema':'TRA2-RESEARCH-MANIFEST/1','classification':'Actual normal A2 native/automatic-admin originals and independent structural/hash audits',
 'provenance':'CONDITIONAL_ROOT_DPKG_KEYRING','internal':'UNKNOWN','native':'NATIVE_SEAL_COMPLETED','automatic_admin':'ADMIN_EVIDENCE_SEALED','files':rows,
 'exclusions':['OUTPUT_MANIFEST.json (extra ZIP member)','TRA2_EVIDENCE.zip','TRA2_EVIDENCE.zip.sha256','evidence/DELIVERY_CHECK.json']})
with zipfile.ZipFile(O/'TRA2_EVIDENCE.zip','x',zipfile.ZIP_DEFLATED) as z:
    for row in rows:z.write(row['host'],row['archive_path'])
    z.write(O/'OUTPUT_MANIFEST.json','OUTPUT_MANIFEST.json')
errors=[]
with zipfile.ZipFile(O/'TRA2_EVIDENCE.zip') as z:
    assert z.testzip() is None
    for row in rows:
        raw=z.read(row['archive_path'])
        if len(raw)!=row['bytes'] or hashlib.sha256(raw).hexdigest()!=row['sha256']:errors.append(row['archive_path'])
    assert z.read('OUTPUT_MANIFEST.json')==(O/'OUTPUT_MANIFEST.json').read_bytes();entries=len(z.namelist())
assert not errors
zipsha=h(O/'TRA2_EVIDENCE.zip');(O/'TRA2_EVIDENCE.zip.sha256').write_text(zipsha+'  TRA2_EVIDENCE.zip\n',encoding='ascii')
delivery={'schema':'TRA2-DELIVERY/1','status':'PASS_ADMINISTRATIVE_DELIVERY_ONLY','overall':'CONDITIONAL_PASS_NORMAL_A2','version':r['revision'],
 'RA-D1':r['RA-D1'],'RA-D2':r['RA-D2'],'TR-D1':r['TR-D1'],'TR-D2':r['TR-D2'],'TR-D3':r['TR-D3'],'TR-D4':r['TR-D4'],'TR-D5':r['TR-D5'],'TR-D6':r['TR-D6'],'TR-D7':r['TR-D7'],'TR-D8':r['TR-D8'],
 'required_reports':15,'source_files':64,'programs':44,'source_errors':source_errors,'native_files':235,'native_export_errors':native_errors,
 'historical_files':len(history['files']),'history_mismatches':history_errors,'mispath_files':47,'mispath_mismatches':dup_errors,
 'active_calls':1,'automatic_post_calls':1,'administrative_WSL_calls':3,'total_WSL_calls':5,'test_retries':0,'source_edits':0,
 'T0':r['T0'],'R':3133,'transactions':3133,'journal_lines':6266,'checks_accepted':184,'mutants_detected':33,
 'PT_accepted':64,'PT_mutants':9,'PF_accepted':48,'PF_mutants':8,'TR_accepted':40,'TR_mutants':8,'RA_accepted':32,'RA_mutants':8,
 'terminal_read':'VALID','terminal_key_originals_unchanged':True,'active_denial':'IPC_CLOSED_DOMINATES','native':'NATIVE_SEAL_COMPLETED','native_rows':233,'native_entries':234,
 'automatic_admin':'ADMIN_EVIDENCE_SEALED','admin_rows':249,'admin_entries':250,'internal':'UNKNOWN','provenance':'RUNTIME_PROVENANCE_CONDITIONAL','new_deb_payload_reconstruction':False,
 'manual_cleanup':0,'extra_fallback_archival':0,'all_roles_and_parent_empty':True,'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
 'STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED','JSON_parsed_before_manifest':parsed,'links_checked':links,'link_errors':link_errors,
 'manifest_rows':len(rows),'ZIP_entries':entries,'ZIP_stream_errors':errors,'manifest_sha256':h(O/'OUTPUT_MANIFEST.json'),'ZIP_sha256':zipsha,'ZIP_bytes':(O/'TRA2_EVIDENCE.zip').stat().st_size,
 'sealed_utc':datetime.now(timezone.utc).isoformat(),'admin_elapsed_seconds':time.perf_counter()-tick,'self_excluded_from_manifest_and_zip':True}
put(E/'DELIVERY_CHECK.json',delivery)
print(json.dumps({key:delivery[key] for key in ['overall','historical_files','manifest_rows','ZIP_entries','ZIP_sha256','ZIP_bytes','links_checked']},ensure_ascii=False))
