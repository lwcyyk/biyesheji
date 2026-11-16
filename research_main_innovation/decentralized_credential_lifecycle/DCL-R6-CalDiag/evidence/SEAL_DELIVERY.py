"""Host administrative integrity seal. No further WSL or target calls."""
from pathlib import Path
import hashlib
import json
import re
import time
import zipfile
from datetime import datetime,timezone

B=Path(r'D:\毕业设计\research_main_innovation\decentralized_credential_lifecycle')
O=B/'DCL-R6-CalDiag';E=O/'evidence';I=Path(r'D:\毕业设计\DCL-R6-isolated-verification\batch09');W=I.parent/'cr09'
tick=time.perf_counter()
def load(p):return json.loads(Path(p).read_bytes())
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not(O/'CALDIAG_EVIDENCE.zip').exists() and not(E/'DELIVERY_CHECK.json').exists()
result=load(E/'CALDIAG_RESULT.json');final=load(E/'FINAL_POSTRUN_AUDIT.json');cleanup=load(E/'FROZEN_FAILURE_CLEANUP.json')
assert final['controlled_roles_empty'] and not final['parent_cgroup_exists'] and cleanup['budget_unchanged']
assert result['active_entry_calls']==1 and result['successful_resumes']==0 and result['R']==38729
assert load(E/'execution_authorization.json')['scope']=='CALIBRATE_S1S9_ONLY'
assert load(E/'execution_authorization.json')['Full_conditional_chain_explicitly_approved'] is False
source=load(E/'SOURCE_AND_SCOPE_ADMISSION.json');source_errors=[]
for row in source['files']:
    rel=row['relative']
    for root in [W,E/'FROZEN_SOURCE_REFERENCE',I/'FROZEN_B09']:
        if h(root/rel)!=row['sha256']:source_errors.append(str(root/rel))
assert not source_errors and not list(W.rglob('*.pyc'))
export_errors=[]
for name in ['NATIVE_EXPORT_LOCK.json','FROZEN_SOURCE_EXPORT_LOCK.json','FINAL_NATIVE_EXPORT_LOCK.json']:
    for row in load(E/name)['files']:
        if h(row['host'])!=row['sha256']:export_errors.append(row['host'])
assert not export_errors
baseline=load(E/'BASELINE_LOCK.json');history_errors=[]
for row in baseline['files']:
    p=Path(row['host'])
    if not p.is_file() or p.stat().st_size!=row['bytes'] or h(p)!=row['sha256']:history_errors.append(row['host'])
assert not history_errors
dup=load(B/'DCL-R6-batch02-Perf/evidence/DUPLICATE_REGISTER.json');dup_errors=[]
for row in dup['files']:
    if h(Path(dup['path'])/row['relative'])!=row['duplicate_sha256']:dup_errors.append(row['relative'])
assert not dup_errors

heads={
'CURRENT_VERDICT.md':'''# DCL-R6-CalDiag 最新实际裁决（2026-11-12）

RESOURCE_GATE_FAILED / TIME_FEASIBILITY_UNRESOLVED_EARLY_FAILURE。batch09-r1方案B已实际单会话启动，Root4259/start135655跨exec；C00–C09全部PASS，READY64 47/17、C09H34 28/6、RootIPC56 48/8、BC40 30/10分别为PASS/MUTATION_DETECTED。真实C09已取得持久ACK、Receiver、waitpid exit23、fresh-read及一次分类HANDOFF_VERIFIED。

恢复scheduler4804在manager健康检查抛UNREVIEWED_MANAGER_FAILURE、exit125；本批预期c06/c07/c09故障单位仍为failed。失败前言在清理try之外，普通非零返回未自动关闭；AWAIT状态coordinator身份为空使Root停止器继续等待。原607文件快照保存后，按授权调用冻结stop_tree/seal补充关闭，预算不变，最终612文件、610行原生seal/611 ZIP条目保存，受控角色全空/父组不存在。

R38,729，1,739事务/3,478行；真实C09前缀48.592009253秒，失败区间48.699583118–48.738270904秒。CLOSED记录采样T0+299.567904452，发布完成不晚于+299.596399447，seal/角色空观测+299.993796083。全校准尚未完成，C10–C12/S34/门18均UNRUN，资源资格尚未取得，F1/F4未启动。

[最终裁决](DCL-R6-CalDiag/CALDIAG_FINAL_DECISION.md) · [首次反例](DCL-R6-CalDiag/CALDIAG_COUNTEREXAMPLES.md) · [逐case时间](DCL-R6-CalDiag/CALDIAG_CASE_DURATION_REPORT.md) · [证据索引](DCL-R6-CalDiag/EVIDENCE_INDEX.md)

D1/D2原条件、强G、严格分离0及IMPLEMENTATION_GATE=CLOSED保持。以下完整保留此前各阶段记录。

---

''',
'NEXT_ACTION.md':'''# DCL-R6-CalDiag 下一步（2026-11-12）

当前先准备恢复健康检查与失败关闭的最小静态修订，范围见[下一静态修复申请](DCL-R6-CalDiag/NEXT_STATIC_REPAIR_REQUEST.md)。重点为本批受保护PASS所对应的预期failed单位分类/清理策略，恢复前言及普通exit125的关闭收敛，等待恢复期间的Root监督责任与原校准截止。其他未审阅manager失败继续拒绝，原ACK/预算/AS/任务/墙钟合同保持。

本轮源保持B09-AdmissionFix-static-1/r1，目标入口1次、测试重跑0，batch09-r1已由CLOSED吸收标记关闭。后续先新版本静态冻结，再申请新独立身份/执行锁的方案B校准；C10–C12/S34/门18及完整300秒实测责任仍需完成。F1/F4技术准入尚未成立，新的正式模型执行仍需明确授权及当批资源资格。

[最终裁决](DCL-R6-CalDiag/CALDIAG_FINAL_DECISION.md) · [时间裁决](DCL-R6-CalDiag/CALDIAG_TIME_FEASIBILITY.md)。严格分离0及机制实施门CLOSED保持。

以下完整保留此前下一步记录。

---

''',
'README.md':'''# DCL-R6-CalDiag 动态诊断交付（2026-11-12）

本次batch09-r1方案B取得C00–C09、READY64、RootIPC56、BC40、C09H34及真实C09交接证据；恢复入口manager检查失败，随后发现关闭收敛缺口。已追加冻结关闭/封存，预算R38,729保持，受控进程全空。C10–C12/S34/门18未运行，全链时间仍未决，F1/F4未启动。

[最终裁决](DCL-R6-CalDiag/CALDIAG_FINAL_DECISION.md) · [下一修复范围](DCL-R6-CalDiag/NEXT_STATIC_REPAIR_REQUEST.md) · [证据索引](DCL-R6-CalDiag/EVIDENCE_INDEX.md)

以下完整保留此前项目入口。

---

''',
'DECISION_HISTORY.md':'''# 2026-11-12 CalDiag：真实C09通过，恢复健康/关闭编排失败

B09-AdmissionFix-static-1/r1按新明确方案B授权实际运行。预检/same-PID/boot/sealed认领/C00通过，C00–C09全PASS；READY64、RootIPC56、BC40、H34共194项为153 PASS＋41 MUTATION_DETECTED。真实持久ACK、Receiver、Launcher exit23、直接waitpid、fresh-read及HANDOFF_VERIFIED一次分类齐备。

恢复前言manager检查因未审阅failed状态退出125，C10尚未启动。该前言早于清理try，父普通非零返回未自动关闭，等待恢复状态清空Root责任身份，external-stop继续等待。保存初始607文件后按停止授权调用冻结stop_tree/seal，CLOSED发布区间T0+299.567904452–299.596399447，+299.993796083确认清理/seal；最终612原件及原生611条目包保存。counter/journal/intent SHA保持，角色全空，R38,729。

RESOURCE_GATE_FAILED；TIME_FEASIBILITY_UNRESOLVED_EARLY_FAILURE；C10–C12/S34/门18保持UNRUN，完整原始资源门尚未完成；F1/F4=UNRUN_RESOURCE_GATE，PASS_BOUNDED=[]。本轮源码/权限/上限修复0、测试重跑/预算重置/自动下一批0；原历史/误路径保持。下一轮先最小静态修复恢复健康及失败关闭，再申请新独立校准。D1/D2、强G、严格分离0及IMPLEMENTATION_GATE=CLOSED保持。

[最终裁决](DCL-R6-CalDiag/CALDIAG_FINAL_DECISION.md) · [反例](DCL-R6-CalDiag/CALDIAG_COUNTEREXAMPLES.md)

以下完整保留此前决策。

---

'''}
nav=[]
for name,head in heads.items():
    old=(E/'navigation_before'/name).read_bytes();assert (B/name).read_bytes()==old,'NAVIGATION_CHANGED:'+name
    (B/name).write_bytes(head.encode('utf-8')+old)
    nav.append({'name':name,'original_sha256':hashlib.sha256(old).hexdigest(),'exact_original_suffix_preserved':(B/name).read_bytes().endswith(old),'new_sha256':h(B/name)})
put(E/'HISTORY_PROTECTION_CHECK.json',{'status':'PASS_ADMIN_ONLY','historical_files':len(baseline['files']),'mismatches':history_errors,'navigation':nav,'mispath_files':len(dup['files']),'mispath_mismatches':dup_errors,'mispath_actions':'READ_HASH_ONLY','prior_policy_rejection':'blocked by policy retained','historical_budgets_modified':0,'source42_unchanged':True})
required=['CALDIAG_AUTHORIZATION_AND_LOCK.md','CALDIAG_EXECUTION_TIMELINE.md','CALDIAG_CASE_DURATION_REPORT.md','CALDIAG_RESOURCE_CALIBRATION.md','CALDIAG_ROOTIPC_AND_C09_RESULTS.md','CALDIAG_S1_S9_RESULTS.md','CALDIAG_GATE18_RESULTS.md','CALDIAG_RESOURCE_ACCOUNTING.md','CALDIAG_TIME_FEASIBILITY.md','CALDIAG_COUNTEREXAMPLES.md','CALDIAG_FINAL_DECISION.md']
assert all((O/name).exists() for name in required)
json_count=0
for p in O.rglob('*.json'):load(p);json_count+=1
link_errors=[];links=0
for p in O.glob('*.md'):
    raw=p.read_text(encoding='utf-8');assert '不是' not in raw
    for match in re.finditer(r'\[[^\]\n]+\]\(([^)\n]+)\)',raw):
        target=match.group(1).strip('<>').split('#',1)[0]
        if not target or re.match('https?://',target):continue
        q=(p.parent/target).resolve();links+=1
        if q==E/'DELIVERY_CHECK.json':continue
        if not q.exists():link_errors.append({'file':p.name,'target':target})
assert not link_errors
put(O/'SOURCE_INDEX.json',{'version':'B09-AdmissionFix-static-1/r1','frozen_source42':source['files'],'native_initial_lock':'evidence/NATIVE_EXPORT_LOCK.json','native_final_lock':'evidence/FINAL_NATIVE_EXPORT_LOCK.json','frozen_source_export':'evidence/FROZEN_SOURCE_EXPORT_LOCK.json','required_reports':required,'request_sha256':h(E/'TASK_REQUEST.txt'),'actual_scope':'CALIBRATE_S1S9_ONLY','protocol_models_run':0,'actual_operations':'Deployment1, active frozen entry1, initial export1, frozen failure cleanup1, final export1; no target retry'})
rows=[]
exclude={O/'OUTPUT_MANIFEST.json',O/'CALDIAG_EVIDENCE.zip',E/'DELIVERY_CHECK.json'}
for p in sorted(O.rglob('*')):
    if p.is_file() and p not in exclude:rows.append({'host':str(p),'archive_path':'research/'+p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':h(p)})
for folder,prefix in [('native_snapshot','runtime_initial'),('final_snapshot','runtime_final'),('FROZEN_B09','native_frozen_source')]:
    for p in sorted((I/folder).rglob('*')):
        if p.is_file():rows.append({'host':str(p),'archive_path':prefix+'/'+p.relative_to(I/folder).as_posix(),'bytes':p.stat().st_size,'sha256':h(p)})
for name in heads:
    p=B/name;rows.append({'host':str(p),'archive_path':'navigation/'+name,'bytes':p.stat().st_size,'sha256':h(p)})
put(O/'OUTPUT_MANIFEST.json',{'schema':'CalDiag-output-manifest/1','scope':'Actual scope-B diagnostic plus initial/terminal original evidence and static sources','files':rows,'exclusions':['manifest self','archive self','DELIVERY_CHECK external final receipt'],'nonregular_scope':'See native export locks; socket/link metadata preserved'})
with zipfile.ZipFile(O/'CALDIAG_EVIDENCE.zip','x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for row in rows:z.write(row['host'],row['archive_path'])
    z.write(O/'OUTPUT_MANIFEST.json','OUTPUT_MANIFEST.json')
zip_errors=[]
with zipfile.ZipFile(O/'CALDIAG_EVIDENCE.zip') as z:
    for row in rows:
        data=z.read(row['archive_path'])
        if len(data)!=row['bytes'] or hashlib.sha256(data).hexdigest()!=row['sha256']:zip_errors.append(row['archive_path'])
    assert z.read('OUTPUT_MANIFEST.json')==(O/'OUTPUT_MANIFEST.json').read_bytes()
    entries=len(z.namelist())
assert not zip_errors
delivery={'schema':'CalDiag-delivery/1','status':'PASS_ADMIN_ONLY','research_verdict':result['status'],'time_verdict':result['TIME_FEASIBILITY'],'required_reports':len(required),'history_files':len(baseline['files']),'history_mismatches':history_errors,'mispath_files':47,'mispath_mismatches':dup_errors,'frozen_source_files':42,'source_mismatches':source_errors,'initial_native_files':607,'final_native_files':612,'native_seal_rows':610,'native_seal_zip_entries':611,'actual_R':38729,'actual_transactions':1739,'actual_journal_lines':3478,'active_entry_calls':1,'test_retries':0,'source_repairs':0,'internal_resume_attempts':1,'successful_resumes':0,'post_failure_frozen_cleanup':True,'budget_unchanged_during_cleanup':True,'CLOSED_marker':True,'all_controlled_roles_empty':True,'complete_calibration':False,'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],'STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED','JSON_parsed_before_manifest':json_count,'links_checked':links,'link_errors':link_errors,'manifest_rows':len(rows),'ZIP_entries':entries,'ZIP_stream_errors':zip_errors,'manifest_sha256':h(O/'OUTPUT_MANIFEST.json'),'ZIP_sha256':h(O/'CALDIAG_EVIDENCE.zip'),'ZIP_bytes':(O/'CALDIAG_EVIDENCE.zip').stat().st_size,'admin_seal_elapsed_seconds':time.perf_counter()-tick,'sealed_utc':datetime.now(timezone.utc).isoformat(),'self_excluded_from_manifest_and_zip':True,'no_further_native_calls_after_final_export':True}
put(E/'DELIVERY_CHECK.json',delivery)
print(json.dumps(delivery,ensure_ascii=False))
