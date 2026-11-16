"""Seal batch06's actual preflight failure, without starting or repairing a runtime."""
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
import hashlib
import json
import os
import re
import struct
import zipfile

E=Path(__file__).resolve().parent
P=E.parent
ROOT=P.parent
WORK=Path(r'D:\毕业设计\DCL-R6-isolated-verification')
W=WORK/'ri01'
N=WORK/'batch06/native_snapshot'
F=WORK/'batch06/FROZEN_ROOTIPC'
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def link(p,label=None):return '['+(label or Path(p).name)+'](<'+os.path.relpath(p,P).replace('\\','/')+'>)'
def table(headers,rows):
    def c(x):return str(x).replace('|','\\|').replace('\n','<br>')
    return '\n'.join(['|'+'|'.join(headers)+'|','|'+'|'.join(['---']*len(headers))+'|']+['|'+'|'.join(map(c,r))+'|' for r in rows])
def report(name,title,text):
    (P/name).write_text('# '+title+'\n\nMaterial Passport：DCL-R6-batch06；RootIPC-static-1/r4；真实预检/准备记录；动态测试0；2026-11-11。\n\n'+text.strip()+'\n',encoding='utf-8')


baseline=load(E/'BASELINE_LOCK.json');pre=load(E/'PREFLIGHT_RESULT.json');final=load(E/'PREFLIGHT_FINAL.json')
audit=load(E/'POSTFAIL_AUDIT.json');native_lock=load(E/'NATIVE_EXPORT_LOCK.json');source_lock=load(E/'FROZEN_SOURCE_EXPORT_LOCK.json')
commands=[load(p) for p in sorted((E/'commands').glob('*.result.json'))]
assert len(commands)==19 and all(c['exit_code']==0 for c in commands)
assert pre['status']=='PREFLIGHT_BASE_PASS' and final['status']=='PREFLIGHT_FAILED'
assert [k for k,v in final['checks'].items() if not v]==['same_boot']
assert not any(c['classification']=='B06_FROZEN_LAUNCHER' for c in commands)
assert not any('--resume' in c['argv'] for c in commands)
for key in ['state_exists','counter_exists','CLOSED_exists','STOP_REQUEST_exists','native_auto_seal_exists','parent_cgroup_exists']:assert audit[key] is False
assert not audit['payload_processes'] and not audit['root_role_processes']
assert not audit['out_entries'] and not audit['private_entries']
assert len(native_lock['files'])==2 and len(source_lock['files'])==44
assert sha(E/'TASK_REQUEST.txt')==final['metadata']['authorization_text_sha256']
assert sha(E/'execution_authorization.json')==final['metadata']['authorization_receipt_sha256']
for c in commands:
    for s in ['stdout','stderr']:assert sha(P/c[s+'_file'])==c[s+'_sha256']
checks=[]


def verify(name,rows,path,key='sha256'):
    errors=[]
    for row in rows:
        p=path(row)
        if not p.is_file() or sha(p)!=row[key] or ('bytes'in row and p.stat().st_size!=row['bytes']):errors.append(str(p))
    checks.append({'name':name,'count':len(rows),'mismatches':errors,'status':'PASS_ADMIN_ONLY' if not errors else 'FAIL'})
    assert not errors,(name,errors)


verify('Historical research originals',baseline['history'],lambda r:ROOT/r['relative'])
verify('Canonical ri01 frozen source/cache/inputs',baseline['source_files'],lambda r:W/r['relative'])
verify('batch06 prepared native bytes',native_lock['files'],lambda r:Path(r['host']))
verify('batch06 frozen Linux export',source_lock['files'],lambda r:Path(r['host']))
expected={r['relative']:r['sha256'] for r in baseline['source_files']}
assert {r['relative']:r['sha256'] for r in source_lock['files']}==expected
for folder in ['DCL-R6-GapClosure','DCL-R6-BudgetFix']:
    old=load(ROOT/folder/'evidence/STATIC_WORKSPACE_LOCK.json')
    verify(folder+' old source',old['files'],lambda r,old=old:Path(old['host'])/r['relative'])
for folder in ['DCL-R6-batch04','DCL-R6-batch05']:
    for fn in ['NATIVE_EXPORT_LOCK.json','FROZEN_SOURCE_EXPORT_LOCK.json']:
        old=load(ROOT/folder/'evidence'/fn);verify(folder+'/'+fn,old['files'],lambda r:Path(r['host']))
old=load(ROOT/'DCL-R6-C09Fix/evidence/STATIC_WORKSPACE_LOCK.json')
verify('Canonical c09f01',old['files'],lambda r:WORK/'c09f01'/r['relative'])
old=load(ROOT/'DCL-R6-batch02-Perf/evidence/BASELINE_LOCK.json')
verify('batch02 original51',old['immutable_B02_external'],lambda r:Path(r['path']))
dup=load(ROOT/'DCL-R6-batch02-Perf/evidence/DUPLICATE_REGISTER.json')
verify('Mispath47 read/hash only',dup['files'],lambda r:Path(dup['path'])/r['relative'],'duplicate_sha256')
for row in baseline['root_navigation']:assert sha(row['snapshot'])==row['sha256']
old_R={}
for folder,value in [('batch04',37021),('batch05',37293),('batch02',32191)]:
    f=WORK/folder/'native_snapshot/out/visits.bin'
    if not f.exists():
        matches=list((WORK/folder).rglob('visits.bin'));assert len(matches)==1;f=matches[0]
    raw=f.read_bytes();assert len(raw)==24 and struct.unpack('<QQ',raw[8:])==(value,1000000)
    old_R[folder]=value
old_archives=[]
for folder,archive in [('DCL-R6-RootIPC-Fix','ROOTIPC_STATIC_REVIEW.zip'),('DCL-R6-batch05','BATCH05_EVIDENCE.zip')]:
    p=ROOT/folder/archive
    with zipfile.ZipFile(p) as z:
        m=json.loads(z.read('OUTPUT_MANIFEST.json'))
        for row in m['files']:
            b=z.read(row['archive_path']);assert hashlib.sha256(b).hexdigest()==row['sha256'] and len(b)==row['bytes']
        old_archives.append({'path':str(p),'entries':len(z.namelist()),'sha256':sha(p),'stream_mismatches':[]})
dump(E/'HISTORY_PROTECTION_CHECK.json',{'schema':'B06-history-protection/1','checks':checks,
 'old_budgets':old_R,'archives':old_archives,'modified_history_files':0,
 'mispath_actions':'read/hash only','prior_policy_rejection':'blocked by policy retained'})

span=(datetime.fromisoformat(commands[14]['end_utc'])-datetime.fromisoformat(commands[0]['start_utc'])).total_seconds()
event={'schema':'B06-first-failure/1','phase':'FINAL_PREFLIGHT_BEFORE_LAUNCH','category':'BOOT_CONTINUITY_MISMATCH',
 'first_observation_command':2,'final_observation_command':15,
 'base_boot_id':pre['boot_id'],'final_boot_id':final['boot_id'],'postfailure_boot_id':audit['boot_id'],
 'observed_utc_interval':{'start':commands[14]['start_utc'],'end':commands[14]['end_utc']},
 'failed_predicate':'same_boot','all_other_final_predicates':True,'launcher_calls':0,
 'runtime_T0':None,'runtime_counter':None,'source_or_permission_repair':0,'dynamic_retry':0,
 'claim_scope':'Administrative preflight continuity; no target protocol or model was executed',
 'WSL_restart_trigger':'UNRESOLVED; multiple distinct boot_ids observed; cold-start latency is suggestive only'}
dump(E/'FIRST_FAILURE.json',event)
results={'schema':'B06-actual-results/1','preflight':'PREFLIGHT_FAILED','base_preflight':'PREFLIGHT_BASE_PASS',
 'resource_verdict':'RESOURCE_GATE_FAILED_PREFLIGHT','RESOURCE_GATE_PASS':'NOT_OBTAINED',
 'C00_C12':{'planned':13,'attempted':0,'passed':0,'status':'UNRUN_PREFLIGHT_FAILED'},
 'C09H':{'planned':34,'attempted':0,'completed':0,'passed':0,'mutants_detected':0},
 'RootIPC':{'planned':56,'planned_mutants':8,'attempted':0,'completed':0,'passed':0,'mutants_detected':0},
 'C09':'NOT_EXERCISED','S1_S9':{'planned':34,'attempted':0,'completed':0,'passed':0},
 'negative17':{'planned':17,'attempted':0,'detected':0},'F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE',
 'PASS_BOUNDED':[],'model_searches':0,'semantic_visits':0,'budget_R':None,'T0':None,'deadline':None,
 'native_preparation_completed':True,'runtime_window_created':False,'native_auto_seal':False,
 'source_changes':0,'postfailure_permission_changes':0,'resumes':0,'new_batch07':False}
dump(E/'ACTUAL_RESULTS.json',results)
dump(E/'RESOURCE_ACCOUNTING.json',{'schema':'B06-accounting/1','budget_initialized':False,'counter':None,'T0':None,
 'deadline':None,'test_visits':0,'model_searches':0,'refunds':0,'resets':0,'resumes':0,
 'nominal_cap':1000000,'nominal_total_seconds':1800,'nominal_calibration_seconds':300,
 'calibration_visits':100000,'joint_C09H_IPC_cap':5000,'IPC_completed_static_bound':505,
 'joint_completed_static_bound':2750,'full_calibration_hard_static_bound':62034,
 'runtime_peak_memory':None,'runtime_peak_RSS':None,'RootIPC_probe_children_started':0,
 'host_UTC_preflight_span_seconds':span,'span_scope':'Administrative evidence span before any runtime T0; not a batch execution duration',
 'controlled_payload_processes_after_failure':[],'controlled_Root_role_processes_after_failure':[],
 'parent_cgroup_exists_after_failure':False})

hashrows=[[name,sha(E/name)] for name in ['static_manifest.json','execution_lock.json','root_ipc_contract.json','c09_contract.json','safety_contract.json','TASK_REQUEST.txt']]
report('BATCH06_AUTHORIZATION_AND_LOCK.md','batch06 专项授权、冻结锁及预检裁决',f'''
本次用户明确批准独立batch06、RootIPC-static-1/r4、56项专项回归、原C/S/门链、额外1个顺序可信Root探针，以及资源资格后同批自动F1→F4。授权原文见[TASK_REQUEST](evidence/TASK_REQUEST.txt)，已安装真实回执见[execution_authorization](evidence/execution_authorization.json)。静态执行锁的DYNAMIC_UNAUTHORIZED历史标签保持原字节，本轮授权由新的用户原文hash与有效回执绑定。

{table(['对象','SHA-256'],hashrows)}

基础预检通过：44项host源/缓存/输入与冻结r4一致；native sha256sum核验1326个唯一Linux文件（原1282加新44）通过；17份最终源码语法记录通过hash绑定继承，本轮重新编译0。五业务、runner、预算核心、探针、C09H34、RootIPC56、S34及门17均按最终输入锁核验。

Python3.12.3 `/usr/bin/python3.12`，摘要e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f；Ubuntu24.04.5、kernel6.18.33.2-microsoft-standard-WSL2/x86_64、systemd255.4-1ubuntu8.18、cgroup2fs、page4096。UID999/GID989且补充组仅989；既有nobody65534/GID65534供获准探针使用；实际探针启动0。Root行政AS为原外部TCB范围，payload AS4条件保持。

6条冻结准备命令实际exit0：建立batch06目录、out、root_private，安装原slice，systemd-analyze verify、daemon-reload；随后安装授权原文及回执。父slice属性TasksMax4、MemoryMax4294967296、inactive/dead；Root:989/0750批根/inputs，999:989/0700 out，Root:Root/0700 private，授权文件Root:989/0640，ACL均空、同设备；out/窗口/账/关闭文件均为空。

最终预检命令15的boot_id={final['boot_id']}，与基础命令2的{pre['boot_id']}不同。`same_boot=false`，其他最终谓词全部true，因此**PREFLIGHT_FAILED**。窗口建立前的证据链已跨boot；Launcher调用0、预算初始化0、动态case0。本轮保留失败记录后仅核查/导出；Source/lock/权限现场修复0。

精确argv及原始双流见[命令索引](COMMAND_SUMMARY.md)。拟使用的冻结顺序为C00–C08→C09H34/Root审查→RootIPC56/Root审查→真实C09→同窗一次恢复→C10–C12→S34→门17→资格→F1→F4；本轮在前置预检处停止。

[基础预检](evidence/PREFLIGHT_RESULT.json)、[最终预检](evidence/PREFLIGHT_FINAL.json)、[首次失败](evidence/FIRST_FAILURE.json)、[源文件索引](SOURCE_INDEX.json)。
''')

permission_rows=[]
for row in audit['native_directories']:
    permission_rows.append([row['relative'],f"{row['uid']}:{row['gid']}",f"{row['mode']:04o}",str(row['ACL']), 'metadata只读观察'])
for row in native_lock['files']:
    permission_rows.append([row['relative'],f"{row['uid']}:{row['gid']}",f"{row['mode']:04o}",str(row['ACL']), '实际安装字节/元数据'])
report('BATCH06_ROOTIPC_PERMISSION_RESULTS.md','batch06 Root/Payload 权限实际范围',f'''
结果为 **UNRUN_PREFLIGHT_FAILED / NOT_EXERCISED**。真实共享counter/intent尚未创建；UID999读取共享intent的实际次数0。Root发布器、临时文件、fchown/fchmod、replace、同步屏障和发布确认均未由本批程序执行。

{table(['已存在对象','UID:GID','mode','ACL','证据范围'],permission_rows)}

元数据对应冻结准备结果，支持目录/授权文件安装正确；授权文件属于payload可读的Root保护收据。私有目录为空。UID999合法读取、65534拒绝、Root私有拒绝写入/伪造、发布前后inode/metadata、错误路径/链接及EIO拒绝都缺少本批动态见证，结果继续UNRUN。元数据观察没有替代非Root实际open测试。

部署源码44项的native副本在失败后逐字节导出，与r4全部对应。RootIPC56原输入及其静态权限策略保持，当前不授予IPC-1/2/3/4动态PASS。[事后审计](evidence/POSTFAIL_AUDIT.json)、[native字节锁](evidence/NATIVE_EXPORT_LOCK.json)、[冻结source锁](evidence/FROZEN_SOURCE_EXPORT_LOCK.json)。
''')

stop_rows=[
['STOP_REQUEST发布','未产生'],['CLOSED发布','未产生；运行窗口尚未建立'],
['Root首次观察停止','N/A；Root协调器未启动'],['ready等待退出','N/A；未进入'],
['RPC等待取消','N/A；未进入'],['父waitpid结束','N/A；未fork Launcher'],
['Root清理开始/退出','N/A；没有本批目标Root角色'],['受控进程退出确认','事后UID999与Root角色扫描为空；父cgroup不存在'],
['STOP_REQUEST→Root退出延迟','N/A，缺少两端运行事件；不填0秒'],['停止后继续发放测试','0；最终预检失败后仅核查/导出']]
report('BATCH06_ROOT_STOP_RESULTS.md','batch06 停止响应与生命周期证据',f'''
RootIPC停止逻辑的动态执行范围为0，实际停止延迟为N/A。首次失败由行政预检发现，目标Launcher/Root协调器、receiver及额外探针都尚未启动。

{table(['测量要求','本批实际'],stop_rows)}

三次boot分别为：基础预检{pre['boot_id']}；最终启动前{final['boot_id']}；事后导出{audit['boot_id']}。这些属于各行政查询时点，没有统一运行T0，禁止跨boot相减构造BOOTTIME延迟。宿主UTC从命令1开始至命令15完成跨度{span:.6f}秒，仅是预检行政记录跨度。

命令17显示父slice inactive/dead、ControlGroup空，MemoryCurrent/TasksCurrent为[not set]；命令18批单位列表空，命令19当前boot精确17-unit journal输出空。没有启动服务后再杀进程的操作，也没有人为制造运行CLOSED文件。本批行政状态为PREFLIGHT_STOPPED；已准备目录/授权及原slice文件保留。

50ms轮询、30秒协作grace、5秒回收等冻结参数保留静态地位，当前实际响应和及时清理结论尚待验证。boot切换的具体WSL生命周期触发源为UNRESOLVED，见[反例与后续审查](BATCH06_COUNTEREXAMPLES.md)。
''')

ipc=load(E/'root_ipc_contract.json');hcfg=load(E/'c09_contract.json');safety=load(E/'safety_contract.json')
ipc_rows=[[j['case_id'],j['kind'],j['variant'],j.get('expected_violation') or '∅','UNRUN_PREFLIGHT_FAILED',0] for j in ipc['jobs']]
report('BATCH06_ROOTIPC_REGRESSION_RESULTS.md','batch06 RootIPC56 与 C09H34 结果',f'''
RootIPC计划56项（48个safe、8个mutant）；实际尝试0、完成0、通过0、变异检出0。8个mutant均保持UNRUN，未形成“已检出”结论。下列输入及独立oracle均在冻结范围内，程序实际调用0。

{table(['case','层','variant','期望违规','实际状态','访问计数'],ipc_rows)}

C09H计划34项；实际尝试0、完成0、28个safe路径和6个mutant均UNRUN_PREFLIGHT_FAILED。batch05的28 PASS+6 MUTATION_DETECTED保留其旧版本/旧批次范围。

{table(['C09H case','冻结variant','本批实际'],[[j['case_id'],j['variant'],'UNRUN_PREFLIGHT_FAILED'] for j in hcfg['jobs']])}

本批实际输入锁与静态源码可复核，逐项实际注入/文件或进程原件/退出/oracle/耗时均N/A，实际访问0。未来完整路径静态505、共同2750≤5000仍是预测上界，本批没有动态验证。ACL拒绝等更强操作覆盖以冻结清单与实际日志为准，当前无实际ACL注入见证。

[冻结RootIPC合同](evidence/root_ipc_contract.json)、[C09H合同](evidence/c09_contract.json)、[实际状态](evidence/ACTUAL_RESULTS.json)。
''')

handoff_checks=['当前批次交接意图','receiver取得并验证交接对象','持久commit/ACK及receiver确认','Launcher实际exit23',
 '父协调器raw_wait_status与稳定身份','pidfd后fresh-read','同一退出一次分类','监督责任和独立停止源','原窗口一次恢复/预算不变']
report('BATCH06_C09_HANDOFF_RESULTS.md','batch06 真实C09交接裁决',f'''
**NOT_EXERCISED / UNRUN_PREFLIGHT_FAILED**。Launcher启动0，实际C09服务启动0；目前没有C09.ready、handoff状态、commit/ACK、receiver确认、waitpid/pidfd退出见证或恢复记录。

{table(['必要真实证据','实际结果'],[[x,'未进入对应阶段；N/A'] for x in handoff_checks])}

C09成功数0；这表示测试尚未运行。无法判断r4的真实交接是否修复成功或仍会失败；本批发现的boot连续性缺口属于启动前行政证据链。RootIPC56与C09H34都未运行，静态断言及旧批次合成PASS无法补充真实C09资格。

[最终预检](evidence/PREFLIGHT_FINAL.json)、[事后缺件与进程核对](evidence/POSTFAIL_AUDIT.json)、[首次失败](BATCH06_COUNTEREXAMPLES.md)。
''')

cal_rows=[[f'C{i:02}', 'UNRUN_PREFLIGHT_FAILED',0,'无当前机器PASS/资源探针记录'] for i in range(13)]
report('BATCH06_RESOURCE_CALIBRATION.md','batch06 C00–C12资源校准实际结果',f'''
计划13个C case，实际尝试0、完成0、PASS0，全部UNRUN_PREFLIGHT_FAILED。C00–C08的batch05历史PASS与当前批次资格分别保留；新源码涉及RootIPC，因此当前仍要求重取完整链证据。

{table(['case','本批状态','尝试次数','证据范围'],cal_rows)}

C02批量预留/内存child、C04第五task拒绝、C07/08异常退出、C09交接、C10封闭、C11持久化故障、C12关闭/恢复拒绝全部未触发。本批只有安装前后的冻结slice配置属性：TasksMax=4、MemoryMax=4GiB；运行时AS、task实际归属、charged peak/RSS峰值均N/A。

T0、deadline、stop_at和校准300秒窗口尚未初始化。共同C09H/IPC5000、完整校准62034≤100000、总额1000000/1800秒保持合同数值，动态验证仍待取得。SOURCE/argv/UID/ACL检查的局部通过不会产生RESOURCE_GATE_PASS。

[资源核算](BATCH06_RESOURCE_ACCOUNTING.md)、[最终预检](evidence/PREFLIGHT_FINAL.json)、[实际汇总](evidence/ACTUAL_RESULTS.json)。
''')

report('BATCH06_S1_S9_RESULTS.md','batch06 S1–S9 34项结果',f'''
计划34项，尝试0、完成0、通过0、变异检出0。RANGE controller及Root独立原始证据重算均未启动，全部UNRUN_PREFLIGHT_FAILED。

{table(['冻结job','性质','variant','本批结果'],[[j['case_id'],j['property'],j['variant'],'UNRUN_PREFLIGHT_FAILED'] for j in safety['jobs']])}

当前不存在S原始操作、故障、credit claim或RANGE_QUALIFICATION。原S34及范围预算源码/输入值保持冻结，[S合同](evidence/safety_contract.json)可审阅；静态完整性与当前动态状态分别登记。
''')

report('BATCH06_GATE_NEGATIVE_RESULTS.md','batch06 17项资格门负向检查',f'''
计划17项，实际尝试0、实际拒绝/变异见证0；均UNRUN_PREFLIGHT_FAILED。Root gate审查与GATE_NEGATIVE_AUDIT未执行/产生。

{table(['case','冻结recipe','期望拒绝前缀','本批实际'],[[j['case_id'],j['recipe'],j['expected_prefix'],'UNRUN_PREFLIGHT_FAILED'] for j in safety['gate_negative_cases']])}

RESOURCE_GATE_PASS=NOT_OBTAINED。任何前置FAIL/UNRUN/NOT_EXERCISED均阻断FORMAL，当前预检失败在启动入口之前已阻断全部链。source/元数据与行政归档核对通过只支持各自证据范围。
''')

report('BATCH06_RESOURCE_ACCOUNTING.md','batch06 预算、时间与进程核算',f'''
本批持久预算账尚未初始化：R=null，T0/deadline/stop_at=null，journal/intent均不存在。实际测试与模型语义访问0、模型搜索0、退款0、重置0、恢复0。这里将“测试访问0”与“有效账R=0”分别记录，当前没有可供运行准入的账。

{table(['资源项','合同','本批实际'],[
 ['全局访问','1000000','未初始化账；实际测试访问0'],['总墙钟/提前停止','1800秒/T0+1740','无T0；实际运行耗时N/A'],
 ['校准窗口/软额','300秒/100000','未进入'],['C09H/IPC共同硬额','5000','未进入；静态完成上界2750'],
 ['IPC56','505完成上界/512硬额','实际访问0'],['完整校准硬额','62034','未验证'],
 ['payload AS/task','1GiB每进程/父4tasks','源/配置保持；实际payload0'],['Root顺序探针','最多1，AS1GiB','启动0'],
 ['峰值内存/RSS/Root开销','按原payload/外部TCB边界解释','N/A，目标程序未运行'],
 ['预检行政跨度','执行窗口之前','宿主UTC差'+f'{span:.6f}'+'秒；跨boot，不作为批次运行耗时']])}

六条准备命令与两条授权安装均执行，只有两份native常规文件。当前out/private为空；事后专用UID与Root角色进程为空，parent cgroup不存在。父slice inactive/dead，未启动服务。原生seal程序执行0，EVIDENCE.zip原生文件未生成，当前封存为行政导出/打包。

历史batch05 R37293、batch04 R37021、batch02 R32191从host原件再次读取，原失败与已关闭状态保持。[独立核算JSON](evidence/RESOURCE_ACCOUNTING.json)、[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)、[事后审计](evidence/POSTFAIL_AUDIT.json)。
''')

for model,scopes,note in [
 ('F1',['SMOKE','BRANCH','CHAIN','KEY','指定mutants','反例重放','INV1–INV8'],'旧钥、历史责任、预算、ReadyState/ReadyUse及迟到IO冻结边界保持。'),
 ('F4',['COST1','CE5/固定夹具','D2-DP','TRACE-REF','压缩开关对照','G64','指定mutants','反例重放'],'独立参考语义和候选后继/终态隔离要求保持。')]:
    report(f'BATCH06_{model}_RESULTS.md',f'batch06 {model}实际有界检查结果',f'''
实际状态 **UNRUN_RESOURCE_GATE**。入口在最终预检时停止，FORMAL及业务模块启动0；模型搜索0、状态/语义访问0，PASS_BOUNDED授予0。

{table(['冻结检查范围','实际'],[[s,'UNRUN_RESOURCE_GATE'] for s in scopes])}

模型反例计数为“未搜索”，覆盖率/状态空间/运行时间保持N/A。{note} source与正式输入hash匹配仅证明冻结版本，当前没有新有界性质通过证据。

[实际结果](evidence/ACTUAL_RESULTS.json)、[资格失败](BATCH06_FINAL_DECISION.md)、[执行锁](evidence/execution_lock.json)。
''')

report('BATCH06_COUNTEREXAMPLES.md','batch06 首次失败与预检连续性缺口',f'''
## CE-B06-PF01：同一准入证据链跨越不同boot

具体输入轨迹：命令1完成1326项hash核对 → 命令2在boot `{pre['boot_id']}`取得运行时/身份/无残留与旧账证据 → 管理命令及宿主间隔 → 命令6–13执行冻结准备/安装授权 → 命令15在boot `{final['boot_id']}`检查最终状态 → `same_boot=false` → PREFLIGHT_FAILED → Launcher调用0。

命令15观测UTC区间 `{commands[14]['start_utc']}` 至 `{commands[14]['end_utc']}`。最终其他检查（限额、metadata/ACL、同设备、fresh窗口、授权摘要、slice hash）全部true；唯一失败谓词为same_boot。证据来源是[PREPARE_AND_RUN.py](evidence/PREPARE_AND_RUN.py)最终核验，依据本次授权对当前boot/完整环境及失败停止的要求建立准入连续性检查。

事后命令16再次观测boot `{audit['boot_id']}`。这支持“独立WSL调用之间存在实例生命周期变化”的行政缺口。命令6和16的较长冷启动样式耗时只提供线索；本轮没有WSL宿主关停/重启事件记录，具体触发源仍UNRESOLVED。当前boot变化前后目标Root/Receiver均未启动，不能归因为RootIPC业务执行缺陷。

## 实际停止及证据边界

首次关键预检失败后，只执行只读状态核对和host字节导出。原准备目录、授权与slice保留；没有重跑预检或case、临时改权限、修改代码/锁、重置窗口或创建batch07。未生成运行CLOSED，因为运行窗口尚未建立。行政状态PREFLIGHT_STOPPED，后续测试发放0。

RootIPC权限、取消、waitpid、ACK和模型算法都未执行，当前无对应协议反例。原batch05 EACCES和300秒停止延迟证据全部保留；本轮无法认证这些修复的动态效果。

## 后续审查目标（当前实现/执行0）

后续先收敛WSL预检编排：在稳定Linux会话或同一受控连续进程中完成fresh runtime/单位/UID/hash核验、准备与最终冻结入口交接，明确该会话生命周期和boot锚；所有最终启动断言以当前boot为准。保留本轮失败样本，核对WSL生命周期触发源，独立冻结可审阅的行政流程，再处理匹配的后续执行授权。当前batch06不自动重启，也不增设新运行窗。

这些是基础设施建议，候选协议实现门继续CLOSED；严格分离实例0。[首次失败JSON](evidence/FIRST_FAILURE.json)、[原命令2](evidence/commands/02.result.json)、[原命令15](evidence/commands/15.result.json)、[原命令16](evidence/commands/16.result.json)。
''')

answers=[
['1 预检','基础通过；最终PREFLIGHT_FAILED（boot变化）'],
['2 UID999读取共享intent','NOT_EXERCISED；共享intent尚未创建'],
['3 Root私有控制','目录0:0/0700/无ACL符合准备合同；实际越权测试UNRUN'],
['4 RootIPC56执行/通过','0/0；全部UNRUN_PREFLIGHT_FAILED'],
['5 8变异检出','实际0；全部未执行'],
['6 STOP_REQUEST→Root退出延迟','N/A；两端运行事件均未产生'],
['7 持久ACK/receiver确认','均未产生'],
['8 Launcher waitpid','N/A；Launcher未调用/未fork'],
['9 C09成功','NOT_EXERCISED'],
['10 C00–C12','13项全部UNRUN_PREFLIGHT_FAILED'],
['11 S34/门17','均执行0'],
['12 RESOURCE_GATE_PASS','NOT_OBTAINED'],
['13 F1/F4启动','均0，UNRUN_RESOURCE_GATE'],
['14 PASS_BOUNDED','授予0'],
['15 预算/时间/峰值','R/T0/deadline=null；测试访问0；实际运行峰值N/A'],
['16 新缺口','预检/准备证据链跨boot；具体WSL触发源待确认；目标协议代码未执行']]
report('BATCH06_FINAL_DECISION.md','batch06 最终预检失败裁决',f'''
**PREFLIGHT_FAILED；RESOURCE_GATE_FAILED_PREFLIGHT；动态Launcher/测试/模型启动均为0。** 本次专项许可已绑定RootIPC-static-1/r4并完成六条冻结准备及授权安装；最终启动前boot连续性检查失败，按首次失败规则停止并封存。

{table(['用户要求的最终问题','真实结果'],answers)}

基础命令2 boot={pre['boot_id']}；最终命令15 boot={final['boot_id']}；事后命令16 boot={audit['boot_id']}。禁止把这些查询拼接为同一运行窗口。源码、输入、授权、目录与原slice属性均未出现已观测的hash/metadata不符；最终唯一失败项是same_boot。宿主UTC预检记录跨度109.295102秒，属于T0之前的行政过程。

当前Linux目录保留批根/inputs/out/reports/root_private和两份授权文件；out/private为空；counter、journal、batch_state、STOP_REQUEST、CLOSED、ACK、waitpid证据及native EVIDENCE.zip均未生成。控制进程为空、父cgroup不存在、slice inactive/dead，无需停止未启动的服务。

19条native调用均exit0，属于只读预检/六条冻结准备/授权安装/事后核对与导出；行政脚本的PREFLIGHT_FAILED与命令exit0分别保留。代码/锁修改0、现场权限修复0、重试0、恢复0、新窗口0、batch07创建0。已保存44个实际Linux冻结文件、2个native准备文件及全部命令原始双流/元数据。

790项历史研究基线、当前ri01与旧静态工作区/原导出、误副本47逐字节核对；RootIPC r4和batch05原包逐流核对无差异。历史R37293/R37021/R32191、batch05 RESOURCE_GATE_FAILED、先前blocked by policy和所有首次失败保持。

后续先处理[预检连续性缺口](BATCH06_COUNTEREXAMPLES.md)及可审阅编排，不自动重启本批。D1-PBFT-SEAL/1.1原条件、强G覆盖、STRICT_SEPARATION_INSTANCES=0、IMPLEMENTATION_GATE=CLOSED保持。当前没有资源资格或协议原创性升级。

[授权与锁](BATCH06_AUTHORIZATION_AND_LOCK.md)、[权限实际范围](BATCH06_ROOTIPC_PERMISSION_RESULTS.md)、[停止记录](BATCH06_ROOT_STOP_RESULTS.md)、[全部实际结果](evidence/ACTUAL_RESULTS.json)、[证据索引](EVIDENCE_INDEX.md)、[交付核验](evidence/DELIVERY_CHECK.json)。
''')

report('COMMAND_SUMMARY.md','batch06 实际命令与双流索引',f'''
19条native命令按调用前登记精确argv，之后保存真实UTC区间/退出/原始双流与SHA。所有native exit0；最终业务准入结果由same_boot谓词单独判为PREFLIGHT_FAILED，管理包装进程exit0无法替代资源门结果。

{table(['编号/精确argv','分类','exit','宿主墙钟ms','用途'],[[link(E/f"commands/{i:02}.result.json",f'{i:02}'),c['classification'],c['exit_code'],f"{c['elapsed_ms']:.3f}",c['purpose']] for i,c in enumerate(commands,1)])}

命令1–5为基础预检，6–11为冻结准备，12–13安装授权，14–15为最终预检；失败后16–19仅审计/导出。所有目标Launcher、resume、controller、watchdog、external-stop和模型角色调用0。WSL localhost代理提示按原stderr保留；未观测的交接/模型输出没有补写。
''')

required=['BATCH06_AUTHORIZATION_AND_LOCK.md','BATCH06_ROOTIPC_PERMISSION_RESULTS.md','BATCH06_ROOT_STOP_RESULTS.md',
 'BATCH06_ROOTIPC_REGRESSION_RESULTS.md','BATCH06_C09_HANDOFF_RESULTS.md','BATCH06_RESOURCE_CALIBRATION.md',
 'BATCH06_S1_S9_RESULTS.md','BATCH06_GATE_NEGATIVE_RESULTS.md','BATCH06_RESOURCE_ACCOUNTING.md',
 'BATCH06_F1_RESULTS.md','BATCH06_F4_RESULTS.md','BATCH06_COUNTEREXAMPLES.md','BATCH06_FINAL_DECISION.md']
index={'schema':'B06-source-index/1','source_version':'RootIPC-static-1/r4','canonical_host':str(W),
 'canonical_linux':'/var/lib/dcl-r6/ri01','native_linux':'/var/lib/dcl-r6/batch06','native_host':str(N),
 'frozen_host':str(F),'source_files':source_lock['files'],'native_files':native_lock['files'],
 'preflight':'PREFLIGHT_FAILED','base_boot':pre['boot_id'],'final_preflight_boot':final['boot_id'],
 'postfailure_boot':audit['boot_id'],'hash_scope':load(E/'HASH_SCOPE.json'),'commands':'evidence/COMMAND_PLAN.json',
 'source_changes':0,'actual_launcher_calls':0,'T0':None,'counter':None,'native_auto_seal':False,
 'native_metadata_scope':'Prepared directories and authorization only; no target case executed'}
dump(P/'SOURCE_INDEX.json',index)
report('EVIDENCE_INDEX.md','batch06 研究证据索引',f'''
最终结果PREFLIGHT_FAILED；资源资格未取得；目标测试/模型实际启动0。行政封存核验与动态资格分列。

{table(['交付文件','范围'],[[link(P/name),name[:-3]] for name in required])}

[精确命令/双流索引](COMMAND_SUMMARY.md)、[源/输入/native映射](SOURCE_INDEX.json)、[全部实际状态](evidence/ACTUAL_RESULTS.json)、[首次失败](evidence/FIRST_FAILURE.json)、[基础预检](evidence/PREFLIGHT_RESULT.json)、[最终预检](evidence/PREFLIGHT_FINAL.json)、[环境元数据](evidence/PREFLIGHT_ENV.json)、[事后核对](evidence/POSTFAIL_AUDIT.json)。

[native两份授权字节](evidence/NATIVE_EXPORT_LOCK.json)、[实际Linux44项冻结副本](evidence/FROZEN_SOURCE_EXPORT_LOCK.json)、[预算状态](evidence/RESOURCE_ACCOUNTING.json)、[790项历史及旧账保护](evidence/HISTORY_PROTECTION_CHECK.json)。ACK/receiver/退出见证与预算等运行缺件按未进入阶段记录。

原生自动seal没有执行；[BATCH06_EVIDENCE.zip](BATCH06_EVIDENCE.zip)是当前行政审阅包，覆盖研究材料、两份native准备文件、44份冻结源/缓存/输入及四份当前导航。[OUTPUT_MANIFEST](OUTPUT_MANIFEST.json)逐项列出路径/字节/SHA；[DELIVERY_CHECK](evidence/DELIVERY_CHECK.json)另列manifest与ZIP摘要，排除自引用并逐流核验。目录/ACL/inode元数据在原始审计中保留，host副本只证明内容字节。

四导航先保存完整启动前字节，再前置新裁决；旧包内导航保留各自封存时点。当前不把行政PASS_ADMIN_ONLY提升为任何资源资格或PASS_BOUNDED。
''')
report('README.md','DCL-R6-batch06','''
最终PREFLIGHT_FAILED：基础与最终预检boot_id发生变化，Launcher调用0、T0/预算账未建立。六条冻结准备与授权安装已完成；事后无受控进程/父cgroup，准备目录和证据保留。

[最终裁决](BATCH06_FINAL_DECISION.md) · [首次失败](BATCH06_COUNTEREXAMPLES.md) · [证据索引](EVIDENCE_INDEX.md) · [完整审阅包](BATCH06_EVIDENCE.zip)

RootIPC56、C09H34、C00–C12、S34、门17及F1/F4全部未运行。IMPLEMENTATION_GATE=CLOSED；严格分离0。
''')

intro='''# DCL-R6-batch06 最新裁决（2026-11-11）

PREFLIGHT_FAILED / RESOURCE_GATE_FAILED_PREFLIGHT：RootIPC-static-1/r4基础hash/runtime/身份预检通过，六条冻结准备和授权安装完成；最终启动前boot由3f63d905…变为c92b8cbc…，same_boot检查失败，按首次失败规则停止。Launcher/模型启动0，T0/预算账未建立；56项RootIPC、34项C09H、C00–C12、S34、门17与F1/F4全部未运行。

事后boot为b69460ad…，专用进程与父cgroup为空；out/private空，仅两份授权文件和44项实际Linux冻结源封存。具体WSL生命周期触发源待确认；后续先收敛同boot预检与入口交接的行政编排，当前重试/恢复/代码修复0、batch07创建0。

batch05的RESOURCE_GATE_FAILED、R37293及原失败保持；D1-PBFT-SEAL/1.1原条件、强G覆盖、严格分离0和IMPLEMENTATION_GATE=CLOSED保持。

[batch06最终裁决](DCL-R6-batch06/BATCH06_FINAL_DECISION.md) · [首次失败](DCL-R6-batch06/BATCH06_COUNTEREXAMPLES.md) · [证据索引](DCL-R6-batch06/EVIDENCE_INDEX.md)

以下为本轮开始前完整保留的历史导航，各旧阶段许可/未创建/下一步文字按其记录时点理解。

---

'''
for row in baseline['root_navigation']:(ROOT/row['original']).write_bytes(intro.encode()+Path(row['snapshot']).read_bytes())

planned={P/'OUTPUT_MANIFEST.json',P/'BATCH06_EVIDENCE.zip',E/'DELIVERY_CHECK.json'}
link_count=0;link_errors=[]
for p,content in [(q,q.read_text(encoding='utf-8')) for q in P.glob('*.md')]+[(ROOT/'README.md',intro)]:
    assert '不是' not in content
    for dest in re.findall(r'\]\(([^)]+)\)',content):
        dest=dest.strip('<>')
        if '://' in dest or dest.startswith('#'):continue
        link_count+=1;q=(p.parent/dest.split('#')[0]).resolve()
        if not q.exists() and q not in planned:link_errors.append({'file':str(p),'target':dest})
assert not link_errors,link_errors
for name in required:assert (P/name).is_file()
json_count=0
for base in [P,N,F]:
    for q in base.rglob('*.json'):
        if q.name not in ['OUTPUT_MANIFEST.json','DELIVERY_CHECK.json']:load(q);json_count+=1
dump(E/'ADMIN_REPORTING_RECEIPT.json',{'schema':'B06-reporting/1','script':str(Path(__file__).resolve()),
 'link_scope':'New batch06 Markdown and navigation prefix; historical bodies unchanged',
 'links_checked':link_count,'link_errors':link_errors,'JSON_parsed':json_count,
 'target_tests_added':0,'candidate_mechanism_implementation':0,'scope':'Offline evidence parsing/reporting/byte sealing'})

excluded={P/'OUTPUT_MANIFEST.json',P/'BATCH06_EVIDENCE.zip',E/'DELIVERY_CHECK.json'}
rows=[]
for base,prefix in [(P,'research'),(N,'native'),(F,'FROZEN_ROOTIPC')]:
    for q in sorted(base.rglob('*')):
        if q.is_file() and q not in excluded:
            rows.append({'host':str(q),'scope':prefix,'archive_path':prefix+'/'+q.relative_to(base).as_posix(),
                         'bytes':q.stat().st_size,'sha256':sha(q)})
for row in baseline['root_navigation']:
    q=ROOT/row['original'];rows.append({'host':str(q),'scope':'navigation','archive_path':'navigation/'+q.name,'bytes':q.stat().st_size,'sha256':sha(q)})
manifest={'schema':'B06-output-manifest/1','files':rows,'counts_by_scope':dict(Counter(r['scope'] for r in rows)),
 'resource_verdict':'RESOURCE_GATE_FAILED_PREFLIGHT','exclusions':['OUTPUT_MANIFEST.json','BATCH06_EVIDENCE.zip','evidence/DELIVERY_CHECK.json'],
 'native_auto_seal':False,'artifact_scope':'Administrative preflight failure review package'}
dump(P/'OUTPUT_MANIFEST.json',manifest)
archive=P/'BATCH06_EVIDENCE.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for row in rows:z.write(row['host'],row['archive_path'])
    z.write(P/'OUTPUT_MANIFEST.json','OUTPUT_MANIFEST.json')
with zipfile.ZipFile(archive) as z:
    assert len(set(z.namelist()))==len(rows)+1
    for row in rows:
        b=z.read(row['archive_path']);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
        assert sha(row['host'])==row['sha256']
    assert z.read('OUTPUT_MANIFEST.json')==(P/'OUTPUT_MANIFEST.json').read_bytes()
delivery={'schema':'B06-delivery/1','status':'PASS_ADMIN_ONLY','preflight':'PREFLIGHT_FAILED',
 'resource_verdict':'RESOURCE_GATE_FAILED_PREFLIGHT','source_version':'RootIPC-static-1/r4',
 'required_reports':13,'manifest_rows':len(rows),'scope_counts':manifest['counts_by_scope'],'zip_entries':len(rows)+1,
 'ZIP_stream_mismatches':[],'manifest_sha256':sha(P/'OUTPUT_MANIFEST.json'),'ZIP_sha256':sha(archive),'ZIP_bytes':archive.stat().st_size,
 'native_commands':19,'launcher_calls':0,'dynamic_test_calls':0,'model_searches':0,'T0':None,'counter':None,
 'native_files':2,'frozen_source_files':44,'native_auto_seal':False,'postfailure_processes_empty':True,
 'history_mismatches':0,'historical_research_baseline_files':790,'links_checked':link_count,'link_errors':[],
 'JSON_parsed':json_count,'PASS_BOUNDED':[],'F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE',
 'source_changes':0,'postfailure_permission_changes':0,'retry':0,'resumes':0,'new_batch07':False,
 'IMPLEMENTATION_GATE':'CLOSED','strict_separation_instances':0,
 'seal_time_utc':datetime.now(timezone.utc).isoformat(),'self_excluded_from_manifest_and_ZIP':True,
 'verification_scope':'Listed byte hashes/ZIP streams/schema/new links only; no target dynamic certification'}
dump(E/'DELIVERY_CHECK.json',delivery)
print(json.dumps(delivery,ensure_ascii=False,indent=2))
