"""Administrative evidence packaging; explicitly not the failed native auto-seal."""
from pathlib import Path
import hashlib
import json
import re
import sys
import time
import zipfile
from datetime import datetime,timezone
B=Path(r'D:\毕业设计\research_main_innovation\decentralized_credential_lifecycle');O=B/'DCL-R6-MR-A';E=O/'evidence'
I=Path(r'D:\毕业设计\DCL-R6-isolated-verification\batch10');W=I.parent/'mr01';tick=time.perf_counter()
def load(p):return json.loads(Path(p).read_bytes())
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not(O/'MRA_EVIDENCE.zip').exists() and not(E/'DELIVERY_CHECK.json').exists()
result=load(E/'MRA_RESULT.json');audit=load(E/'POSTRUN_AUDIT.json');source=load(E/'SOURCE_AND_SCOPE_ADMISSION.json')
assert result['T0'] is None and result['R'] is None and not audit['payload_processes'] and not audit['root_role_processes']
assert audit['closed_marker_exists'] and audit['STOP_REQUEST_exists'] and not audit['native_seal_exists']
source_errors=[]
for row in source['files']:
    for root in [W,E/'FROZEN_SOURCE_REFERENCE',I/'FROZEN_MR']:
        if h(root/row['relative'])!=row['sha256']:source_errors.append(str(root/row['relative']))
assert not source_errors and not list(W.rglob('*.pyc'))
native_errors=[]
for row in load(E/'NATIVE_EXPORT_LOCK.json')['files']:
    if h(row['host'])!=row['sha256']:native_errors.append(row['host'])
assert not native_errors
baseline=load(E/'BASELINE_LOCK.json');history_errors=[]
for row in baseline['files']:
    p=Path(row['host'])
    if not p.is_file() or p.stat().st_size!=row['bytes'] or h(p)!=row['sha256']:history_errors.append(row['host'])
assert not history_errors
dups=load(B/'DCL-R6-batch02-Perf/evidence/DUPLICATE_REGISTER.json');dup_errors=[]
for row in dups['files']:
    if h(Path(dups['path'])/row['relative'])!=row['duplicate_sha256']:dup_errors.append(row['relative'])
assert not dup_errors
head='''# DCL-R6-MR-A 最新动态裁决（2026-11-12）

STARTUP_FAILED_PRE_T0。ManagerRecovery-static-1/r5/batch10-r5实际入口1次；预检及same-PID exec通过，boot038cf87f…、Root12242/start699487。初始health在T0之前调用query(record=True)，query要求运行态root_checkpoint，抛IPC_STATE_MISSING。T0/deadline/R及counter/journal从未建立，C00/C09/MR64均未到达，期望C10后返回78未注入。

自动STOP/CLOSED真实发生，父协调器COORDINATOR_STOP_REQUEST的stop_tree返回0并确认组空；abort内后备stop/kill记录TimeoutExpired，内部结果UNKNOWN。Payload及独立停止器服务均未启动；事后所有受控角色为空，人工清理0。原生seal因缺batch_state而失败，行政ZIP另作证据保存，绝不升级为自动seal通过。

64实际执行/接受0、8变异检出0，状态UNRUN；systemd三次预检及事后仅mnt-e.mount基线。host调用2.0633844秒，完整300秒时间证据仍未决。当前batch10已有CLOSED/claim，不复用其目录/回执；下一步先静态修复PRE_WINDOW/ACTIVE检查点、预窗停止期限和封存。

[最终裁决](DCL-R6-MR-A/MRA_FINAL_DECISION.md) · [首错](DCL-R6-MR-A/MRA_COUNTEREXAMPLES.md) · [自动关闭](DCL-R6-MR-A/MRA_AUTOMATIC_CLOSURE_RESULTS.md) · [证据索引](DCL-R6-MR-A/EVIDENCE_INDEX.md)

历史CalDiag C09 PASS及38,729账保持。RESOURCE_GATE_PASS尚未取得，F1/F4未运行，严格分离0、IMPLEMENTATION_GATE=CLOSED。以下完整保留先前记录。

---

'''
nexthead='''# DCL-R6-MR-A 下一步（2026-11-12）

先审阅[最小静态补缺](DCL-R6-MR-A/NEXT_STATIC_REPAIR_REQUEST.md)：初始PRE_WINDOW只读健康查询与ACTIVE运行态检查点分离；无T0时使用已认证启动TCB期限和Owner/child证据完成有限停止；预窗封存明确记录未初始化并保留原件。恢复/正式阶段仍严格要求state和预算，不能全局放开allow_uninitialized。

本轮保持r5源码，未重跑。batch10-r5已有CLOSED，实际T0/R仍null；Root角色已退，producer UNKNOWN与原生seal失败保持。重新静态冻结并取得新明确独立A授权后，再验证合法启动、MR64、真实C09恢复及预声明自动关闭。当前不具备完整资源链/S34/门18/F1F4准入。

[最终裁决](DCL-R6-MR-A/MRA_FINAL_DECISION.md) · [时间/资源](DCL-R6-MR-A/MRA_RUNTIME_AND_RESOURCE.md)。原资源硬限、历史事实及协议实施门保持。

以下完整保留先前下一步。

---

'''
readhead='''# DCL-R6-MR-A 阶段A交付（2026-11-12）

真实入口在T0前因IPC_STATE_MISSING退出125；预检/exec通过，C00/C09/MR64未启动。自动STOP/CLOSED与父停止已取证，事后角色全空；内部UNKNOWN及原生seal失败保持，人工清理0。9份结果报告及行政证据包已交付，下一步先修复预窗检查点/关闭/封存。

[最终裁决](DCL-R6-MR-A/MRA_FINAL_DECISION.md) · [新缺口](DCL-R6-MR-A/MRA_COUNTEREXAMPLES.md) · [证据索引](DCL-R6-MR-A/EVIDENCE_INDEX.md)

以下完整保留原入口。

---

'''
historyhead='''# 2026-11-12 MR-A：r5有限动态启动失败于T0前

46项/31程序核验、45份Linux部署及原生预检通过，唯一冻结入口启动Root12242/start699487、scheduler12300/start699639，IPC_STATE_MISSING出现在初始health/query的运行态checkpoint。T0/deadline/预算counter/journal均未创建，C00/C09/MR64及预声明78故障点未到达。64执行0/变异检出0。

自动STOP/CLOSED及父协调器stop_tree成功，producer关闭结果UNKNOWN（DEADLINE_UNKNOWN及后备超时），原生seal缺state失败；最终角色全空，人工cleanup0、源修改/重跑0，22原件及46源导出保存。完整时间/资格未决，F1/F4未运行。新静态建议只限PRE_WINDOW/ACTIVE、启动TCB关闭期限及预窗seal，旧batch10关闭/claim保持。原CalDiag真实C09及所有历史/误路径保持，强G/严格分离0/实施门CLOSED保持。

[最终裁决](DCL-R6-MR-A/MRA_FINAL_DECISION.md)

以下保留此前决策。

---

'''
heads={'CURRENT_VERDICT.md':head,'NEXT_ACTION.md':nexthead,'README.md':readhead,'DECISION_HISTORY.md':historyhead};nav=[]
for name,text in heads.items():
    old=(E/'navigation_before'/name).read_bytes();assert(B/name).read_bytes()==old,'CONCURRENT_NAVIGATION_CHANGE:'+name
    (B/name).write_bytes(text.encode('utf-8')+old);nav.append({'name':name,'original_sha256':hashlib.sha256(old).hexdigest(),'original_exact_suffix_preserved':(B/name).read_bytes().endswith(old),'new_sha256':h(B/name)})
put(E/'HISTORY_PROTECTION_CHECK.json',{'status':'PASS_ADMIN_ONLY','historical_files':len(baseline['files']),'mismatches':history_errors,'navigation':nav,'mispath_files':47,'mispath_mismatches':dup_errors,'mispath_action':'READ_HASH_ONLY','old_policy_rejection':'blocked by policy retained','old_budgets_written':0,'r5_source_changes':0})
required=['MRA_AUTHORIZATION_AND_LOCK.md','MRA_MANAGER_EVENT_RESULTS.md','MRA_RECOVERY_HEALTH_RESULTS.md','MRA_AUTOMATIC_CLOSURE_RESULTS.md','MRA_REGRESSION_RESULTS.md','MRA_RUNTIME_AND_RESOURCE.md','MRA_EXECUTION_TIMELINE.md','MRA_COUNTEREXAMPLES.md','MRA_FINAL_DECISION.md']
assert all((O/n).exists() for n in required)
links=0;link_errors=[]
for p in O.glob('*.md'):
    text=p.read_text(encoding='utf-8');assert '不是' not in text
    for match in re.finditer(r'\[[^\]\n]+\]\(([^)\n]+)\)',text):
        target=match.group(1).strip('<>').split('#',1)[0]
        if not target or re.match('https?://',target):continue
        q=(p.parent/target).resolve();links+=1
        if q==E/'DELIVERY_CHECK.json':continue
        if not q.exists():link_errors.append({'file':p.name,'target':target})
assert not link_errors
json_count=0
for p in O.rglob('*.json'):load(p);json_count+=1
put(O/'SOURCE_INDEX.json',{'version':result['version'],'source46':source['files'],'request_sha256':h(E/'TASK_REQUEST.txt'),'native_snapshot':'D:/毕业设计/DCL-R6-isolated-verification/batch10/native_snapshot','source_export':'D:/毕业设计/DCL-R6-isolated-verification/batch10/FROZEN_MR','reports':required,'actual_entry_calls':1,'manual_cleanup':0,'test_replays':0,'native_seal':False})
exclude={O/'OUTPUT_MANIFEST.json',O/'MRA_EVIDENCE.zip',E/'DELIVERY_CHECK.json'};rows=[]
for p in sorted(O.rglob('*')):
    if p.is_file() and p not in exclude:rows.append({'host':str(p),'archive_path':'research/'+p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':h(p)})
for folder,prefix in [('native_snapshot','runtime_original'),('FROZEN_MR','native_frozen_source')]:
    for p in sorted((I/folder).rglob('*')):
        if p.is_file():rows.append({'host':str(p),'archive_path':prefix+'/'+p.relative_to(I/folder).as_posix(),'bytes':p.stat().st_size,'sha256':h(p)})
for name in heads:
    p=B/name;rows.append({'host':str(p),'archive_path':'navigation/'+name,'bytes':p.stat().st_size,'sha256':h(p)})
put(O/'OUTPUT_MANIFEST.json',{'schema':'MRA-output-manifest/1','scope':'Administrative evidence package of actual startup failure; native automatic seal remains absent','files':rows,'exclusions':['manifest self','ZIP self','DELIVERY_CHECK external final receipt']})
with zipfile.ZipFile(O/'MRA_EVIDENCE.zip','x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for row in rows:z.write(row['host'],row['archive_path'])
    z.write(O/'OUTPUT_MANIFEST.json','OUTPUT_MANIFEST.json')
errors=[]
with zipfile.ZipFile(O/'MRA_EVIDENCE.zip') as z:
    for row in rows:
        data=z.read(row['archive_path'])
        if len(data)!=row['bytes'] or hashlib.sha256(data).hexdigest()!=row['sha256']:errors.append(row['archive_path'])
    assert z.read('OUTPUT_MANIFEST.json')==(O/'OUTPUT_MANIFEST.json').read_bytes();entries=len(z.namelist())
assert not errors
delivery={'schema':'MRA-delivery/1','status':'PASS_ADMIN_ONLY','research_verdict':'STARTUP_FAILED_PRE_T0','required_reports':9,'source_files':46,'programs':31,'source_errors':source_errors,'native_files':22,'native_snapshot_errors':native_errors,'historical_files':len(baseline['files']),'history_mismatches':history_errors,'mispath_files':47,'mispath_mismatches':dup_errors,'active_entry_calls':1,'test_retries':0,'source_changes':0,'T0':None,'R':None,'MR_jobs_executed':0,'mutants_detected':0,'automatic_STOP_REQUEST':True,'automatic_CLOSED':True,'parent_stop_success':True,'internal_cleanup_status':'UNKNOWN','native_seal':False,'manual_cleanup':False,'all_roles_final_empty':True,'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],'STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED','JSON_parsed_before_manifest':json_count,'links_checked':links,'link_errors':link_errors,'manifest_rows':len(rows),'ZIP_entries':entries,'ZIP_stream_errors':errors,'manifest_sha256':h(O/'OUTPUT_MANIFEST.json'),'ZIP_sha256':h(O/'MRA_EVIDENCE.zip'),'ZIP_bytes':(O/'MRA_EVIDENCE.zip').stat().st_size,'native_automatic_seal_and_administrative_archive_distinguished':True,'sealed_utc':datetime.now(timezone.utc).isoformat(),'admin_elapsed_seconds':time.perf_counter()-tick,'self_excluded_from_manifest_and_zip':True}
put(E/'DELIVERY_CHECK.json',delivery);print(json.dumps(delivery,ensure_ascii=False))
