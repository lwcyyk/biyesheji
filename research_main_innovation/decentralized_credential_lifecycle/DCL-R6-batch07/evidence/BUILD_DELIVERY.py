"""Offline reports and sealed batch07 first-failure evidence package. No target execution."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
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
W=WORK/'bc01'
N=WORK/'batch07/native_snapshot'
F=WORK/'batch07/FROZEN_BOOTCONTINUITY'
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def link(p,label=None):return '['+(label or Path(p).name)+'](<'+os.path.relpath(p,P).replace('\\','/')+'>)'
def table(headers,rows):
    def c(x):return str(x).replace('|','\\|').replace('\n','<br>')
    return '\n'.join(['|'+'|'.join(headers)+'|','|'+'|'.join(['---']*len(headers))+'|']+['|'+'|'.join(map(c,r))+'|' for r in rows])
def report(name,title,text):
    (P/name).write_text('# '+title+'\n\nMaterial Passport：DCL-R6-batch07；BootContinuity-static-1/r4；真实启动后首次失败；2026-11-11；复跑0。\n\n'+text.strip()+'\n',encoding='utf-8')

baseline=load(E/'BASELINE_LOCK.json');continuity=load(E/'BOOT_CONTINUITY_ACTUAL.json');account=load(E/'RESOURCE_ACCOUNTING.json')
failure=load(E/'FIRST_FAILURE.json');audit=load(E/'POSTFAIL_AUDIT.json');native=load(E/'NATIVE_EXPORT_LOCK.json');frozen=load(E/'FROZEN_SOURCE_EXPORT_LOCK.json')
state=load(N/'inputs/batch_state.json');closed=load(N/'inputs/CLOSED.json');native_zip=load(E/'NATIVE_ZIP_CHECK.json')
journal=load(E/'JOURNAL_SUMMARY.json');result=load(E/'ACTUAL_RESULTS.json');lock=load(E/'execution_lock.json')
bc=load(E/'boot_contract.json');ipc=load(E/'root_ipc_contract.json');hc=load(E/'c09_contract.json');safety=load(E/'safety_contract.json')
host_exit=load(E/'WINDOWS_ENTRY_EXIT.json');owner=continuity['owner_after_exec'];run_boot=continuity['boot_id'];t0=state['T0']
assert len(native['files'])==23 and len(frozen['files'])==32 and account['R']==0
assert host_exit['exit_code']==125 and continuity['same_PID_start_ticks'] and not continuity['service_certificate_exists']
history=[]
def verify(name,rows,path,key='sha256'):
    errors=[]
    for row in rows:
        p=path(row)
        if not p.is_file() or sha(p)!=row[key] or ('bytes'in row and p.stat().st_size!=row['bytes']):errors.append(str(p))
    history.append({'name':name,'count':len(rows),'mismatches':errors,'status':'PASS_ADMIN_ONLY' if not errors else 'FAIL'})
    assert not errors,(name,errors)
verify('All1920 historical R6 research files',baseline['history'],lambda r:ROOT/r['relative'])
verify('Canonical bc01 final32',baseline['source_files'],lambda r:W/r['relative'])
verify('Actual native23 export',native['files'],lambda r:Path(r['host']))
verify('Actual source31 plus frozen Windows entry',frozen['files'],lambda r:Path(r['host']))
assert {r['relative']:r['sha256'] for r in baseline['source_files']}=={r['relative']:r['sha256'] for r in frozen['files']}
for folder in ['DCL-R6-batch06','DCL-R6-batch05','DCL-R6-batch04']:
    for fn in ['NATIVE_EXPORT_LOCK.json','FROZEN_SOURCE_EXPORT_LOCK.json']:
        x=load(ROOT/folder/'evidence'/fn);verify(folder+'/'+fn,x['files'],lambda r:Path(r['host']))
for folder in ['DCL-R6-RootIPC-Fix','DCL-R6-C09Fix','DCL-R6-GapClosure','DCL-R6-BudgetFix']:
    x=load(ROOT/folder/'evidence/STATIC_WORKSPACE_LOCK.json');directory=Path(x.get('host',str(WORK/'c09f01')))
    if folder=='DCL-R6-C09Fix':directory=WORK/'c09f01'
    verify(folder+' frozen workspace',x['files'],lambda r,directory=directory:directory/r['relative'])
x=load(ROOT/'DCL-R6-batch02-Perf/evidence/BASELINE_LOCK.json');verify('batch02 original51',x['immutable_B02_external'],lambda r:Path(r['path']))
x=load(ROOT/'DCL-R6-batch02-Perf/evidence/DUPLICATE_REGISTER.json');verify('Mispath47 read/hash only',x['files'],lambda r:Path(x['path'])/r['relative'],'duplicate_sha256')
old_budgets={}
for folder,expected in [('batch05',37293),('batch04',37021),('batch02',32191)]:
    p=WORK/folder/'native_snapshot/out/visits.bin'
    if not p.exists():
        matches=list((WORK/folder).rglob('visits.bin'));assert len(matches)==1;p=matches[0]
    assert struct.unpack('<QQ',p.read_bytes()[8:])==(expected,1000000);old_budgets[folder]=expected
for row in baseline['navigation']:assert sha(row['snapshot'])==row['sha256']
archives=[]
for folder,name in [('DCL-R6-BootContinuity-Fix','BOOTCONTINUITY_STATIC_REVIEW.zip'),('DCL-R6-batch06','BATCH06_EVIDENCE.zip'),('DCL-R6-batch05','BATCH05_EVIDENCE.zip')]:
    p=ROOT/folder/name
    with zipfile.ZipFile(p) as z:
        m=json.loads(z.read('OUTPUT_MANIFEST.json'))
        for row in m['files']:
            b=z.read(row['archive_path']);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
        archives.append({'path':str(p),'sha256':sha(p),'entries':len(z.namelist()),'stream_errors':[]})
dump(E/'HISTORY_PROTECTION_CHECK.json',{'schema':'B07-history/1','checks':history,'archives':archives,
 'old_budgets':old_budgets,'modified_history_files':0,'mispath_actions':'read/hash only','prior_policy_rejection':'blocked by policy retained'})

excerpt=[]
for file,a,b in [('src/guard.py',830,866),('src/guard.py',668,688),('src/boot_continuity.py',330,351)]:
    lines=(F/file).read_text(encoding='utf-8').splitlines()
    excerpt.append(file+'\n'+'\n'.join(f'{i+1}: {lines[i]}' for i in range(a-1,min(b,len(lines)))))
(E/'FAILURE_SOURCE_EXCERPTS.txt').write_text('\n\n'.join(excerpt)+'\n',encoding='utf-8')
dump(E/'CAUSE_ASSESSMENT.json',{'schema':'B07-causality/1','primary_observed':'BC_SERVICE_IDENTITY_OR_LIMITS',
 'confirmed_source_gap':'--no-block followed by MainPID>0 acceptance before validating exec-ready state',
 'journal':'C00 Starting followed by KILL, no Started record',
 'observed_cgroup_charge_peak':782336,'precise_mismatch':'UNRESOLVED; actual8 compared fields not persisted',
 'candidate_cause':'Startup pre-exec transient checked as final UID/GID/cap/AS/cgroup',
 'classification':'SUPPORTED_HYPOTHESIS, not a measured failed field',
 'evidence_gap':'ticket_C00/BOOT_START absent; unit_before_ticket and /proc/status remained in local frame',
 'postfailure_manager_defaults':'not-found/default on later boot; excluded from runtime cause inference',
 'proposed_next_static_scope':'Wait boundedly for Type=exec active/stable identity before current metadata check; persist expected/actual snapshots and exact failed predicate before stop; keep all resource, stop, ACK gates',
 'code_or_permissions_repaired':0,'retries':0,'next_batch_created':False})
dump(E/'ADMIN_EVENT.json',{'schema':'B07-admin-event/1','event':'First run-journal query used hyphenated UUID and journalctl rejected descriptor',
 'correction':'Retained original failure; performed read-only same17-unit query with32-hex representation of the same run boot',
 'corrected_exit':0,'corrected_records':7,'test_or_activation_retry':False,
 'exit_layers':{'exec_tool_shell':1,'frozen_windows_entry_WSL_child':125},
 'stderr':'Original raw is mixed WSL UTF16LE prefix plus native UTF8 traceback; decoded sidecar preserves bytes'})

hashrows=[[name,sha(E/name)] for name in ['static_manifest.json','execution_lock.json','boot_contract.json','root_ipc_contract.json','c09_contract.json','safety_contract.json','TASK_REQUEST.txt']]
report('BATCH07_AUTHORIZATION_AND_LOCK.md','batch07授权、冻结锁与真实执行关系',f'''
用户明确批准BootContinuity-static-1/r4的部署、单会话激活、sealed凭据/一次认领、同进程恢复、40/56/34项回归、C/S/门及完整资源资格后自动F1→F4。授权原文和实际回执分别见[TASK_REQUEST](evidence/TASK_REQUEST.txt)、[execution_authorization](evidence/execution_authorization.json)。静态历史材料的未授权标签按其记录时点保留，本次权限由新原文hash绑定。

{table(['对象','SHA-256'],hashrows)}

host32项（21份程序、11输入）摘要一致；部署31项Linux源码/输入为Root0:0/0644、目录0755，无ACL/pyc；Windows入口原字节保持。部署boot只作静态对象观察，激活未把它设为期望常量。实际动态资格由冻结Windows入口的一次WSL子调用自行建立。

```text
{' '.join(lock['windows_single_call'])}
```

本批活动入口仅调用1次；无独立Guard或resume重试。源代码在同一PID执行预检→exec，Root接入复核后fork scheduler；T0创建后C00服务复核首次失败，后续测试停止。冻结实际顺序仍为C00–C08→C09H34→RootIPC56→BC40→真实C09→同进程同窗一次恢复→C10–C12→S34→门17→资格→F1→F4。

新增BC访问上界已复核：entry1＋40×(预付11＋Root审查1)=481；C09H2245＋RootIPC505＋BC481=3231≤共同5000，完整校准62034≤100000。代码将这些测试绑定同一C09H ticket/T0+300软窗；本次未到这些阶段，整套耗时仍待实测，任何窗口不足只能停止。

[部署结果](evidence/DEPLOYMENT_RESULT.json)、[实际Windows调用](evidence/WINDOWS_ENTRY_PLAN.json)、[原始活动stdout](evidence/windows_entry.stdout.raw)、[冻结锁](evidence/execution_lock.json)、[命令索引](COMMAND_SUMMARY.md)。
''')

bootrows=[
 ['单会话预检','实际执行；15条内部预检/准备命令均exit0'],
 ['当前boot',run_boot],['exec前后Owner',f"PID{owner['pid']}/start_ticks{owner['start_ticks']}，两侧完全一致"],
 ['同进程exec','ACTIVATION_REQUESTED_ONLY后仍由相同身份记录ENTRY_VERIFIED；新Guard traceback进一步见证接入'],
 ['sealed凭据',f"实际生成；seals=15，SHA-256 {continuity['capability_sha256']}"],
 ['一次认领','initial_entered=true，resume_issued=false；本次消费一次，重复拒绝专项测试UNRUN'],
 ['Root子进程',f"PID{continuity['child_identity']['pid']}/start_ticks{continuity['child_identity']['start_ticks']}，boot一致"],
 ['初始入口复核','ENTRY_VERIFIED；20份Linux源码native3.12 compile路径已完成，当前静态对象hash重新校验'],
 ['服务内完整复核','C00发生BC_SERVICE_IDENTITY_OR_LIMITS，BOOT_START未发布'],
 ['Preflight.boot=Service.boot完整证书','NOT_VERIFIED_SERVICE；不以Root入口证据替代服务通过'],
 ['整体结论','OBSERVED_SAME_BOOT_EXEC_PREFIX；FAIL_SERVICE_CONFIRMATION']]
report('BATCH07_BOOT_CONTINUITY_RESULTS.md','batch07真实启动连续性证据与边界',f'''
预检至exec/Guard接入的同boot、同PID/starttime前缀已取得真实证据；服务阶段首次失败，完整服务准入未通过。

{table(['检查项','实际结果'],bootrows)}

首次PREFLIGHT_BEGIN={continuity['preflight_begin']:.9f}，ENTRY_VERIFIED事件={continuity['entry_event_time']:.9f}，同BOOTTIME前缀耗时{continuity['observed_prefix_seconds']:.9f}秒。ticket issued={continuity['ticket_issued_at']:.9f}、expires={continuity['ticket_expires']:.9f}；Root私有entry记录在{continuity['entry_private_time']:.9f}，早于失效点。120秒预检期限为{continuity['preflight_deadline']:.9f}。

memfd封印、设备/inode与摘要验证由实际read_capability路径完成后才记录ENTRY_VERIFIED。普通日志仅包含摘要和验证状态；原ticket/认领只在LinuxRoot:Root/0600的private目录，原始私有证据按同一private相对路径归档，不把nonce输出到本报告。memfd与持锁fd随Owner退出结束，持久认领及CLOSED保留。

事后导出观察boot={audit['observation_boot_id']}，用于清理/文件观察；它不参与活动资格，也未被写回旧票据。活动34条BC日志的Owner均为上述同一身份。当前没有观察到batch06式的活动预检跨boot；尚无物理重启/重复认领通过证据。

[脱敏启动摘要](evidence/BOOT_CONTINUITY_ACTUAL.json)、[实际entry文件](<../../../DCL-R6-isolated-verification/batch07/native_snapshot/inputs/root_private/boot/entry_initial.json>)、[原始活动日志](evidence/windows_entry.stdout.raw)、[首次失败](BATCH07_COUNTEREXAMPLES.md)。
''')

report('BATCH07_BOOT_REGRESSION_RESULTS.md','batch07 BootContinuity40执行结果',f'''
计划40项（30 safe、10 mutant）；实际尝试0、完成0、通过0、变异检出0，全部UNRUN_RESOURCE_GATE。源中该套件在原C09H与RootIPC56之后、真实C09之前运行，本次在C00票据发布前停止。

{table(['冻结case','variant','预期末态/违规','实际'],[[j['case_id'],j['variant'],j['expected_violation'] or j['expected_last'],'UNRUN_RESOURCE_GATE'] for j in bc['jobs']])}

没有模拟boot事件、注入、bc_case原始轨迹或BOOT_CONTINUITY_QUALIFICATION。本次真实sealed fd/exec观察与合成40项结果分别登记，Root入口消费一次不等于重复认领拒绝已测试。预付/审查481次是静态完成上界，本批这些语义访问0。
''')

jrows=[[r['unit'],r['mono_us'],r['message']] for r in journal['records']]
report('BATCH07_RUNTIME_AND_RESOURCE.md','batch07运行时、服务与停止证据',f'''
实际入口使用原生Python3.12.3（e50d…150f）、Ubuntu-24.04，运行时/来源字节检查完成后记录PREFLIGHT_QUALIFIED。systemd实际输出255.4-1ubuntu8.18，page4096，专用UID999/GID989及既有65534身份通过冻结断言；20份Linux源码实际语法编译无cache输出。kernel/架构等比较按冻结代码通过，不扩展为任意环境兼容。

Root父协调器PID828/start7252、scheduler子Launcher PID886/start7372、外部停止器PID890/start7379，boot均为{run_boot}。外部stop服务真实启动并发布STOP_ARMED；C00仅到Starting/MainPID观察，复核失败后停止。

{table(['运行boot journal单位','MONOTONIC µs','原始消息'],jrows)}

C00从Starting到Main process KILL的journal同MONOTONIC差为24.861ms，未出现Started。关闭记录使用BOOTTIME，CLOSED在T0+{account['closed_T0']:.9f}，首次组空T0+{account['first_empty_T0']:.9f}；父waitpid在T0+{account['waitpid_T0']:.9f}得到exit125/raw32000；最终父seal前记录T0+{account['final_before_seal_T0']:.9f}。该错误路径未等待至300秒，但C09/RPC/专项停止竞态尚未测试。

受控payload组本generation观测charged peak={account['observed_charged_peak_bytes']}B，pids.current=1/max4，memory.max4GiB，OOM计数0；精确RSS树峰值与Root RSS未采样。Root预检入口按冻结源调用setrlimit1GiB并继续；C00进程的实际8项比较值没有持久化，因此AS/身份失配字段尚未定位。

事后不同boot的manager显示C00/stop为not-found/default，不能用其LimitAS=infinity或User空值回推运行时。post-failure UID999/Root角色扫描为空，父cgroup不存在。源/配置/权限现场修复0，额外顺序Root探针启动0。clock口径：BC/native账为BOOTTIME，journal为MONOTONIC/REALTIME，Host为perf_counter/UTC；不混算未校准时钟。
''')

report('BATCH07_ROOTIPC_RESULTS.md','batch07 RootIPC56与权限实际结果',f'''
RootIPC56计划56（含8 mutant），实际尝试0、完成0、通过0、变异检出0。入口初始化了global counter/intent，metadata为999:989/0600，ACL为空，Root私有boot文件0:0/0600及目录0700；这些是实际元数据与发布路径范围。

UID999读取共享intent的业务证据为NOT_EXERCISED：C00票据未发放，controller未进入Budget/probe，global counter保持0。Root读文件、元数据符合或memfd消费都无法替代非Root实际open。Root私有拒绝写入、65534拒绝、原子替换故障与8个mutant仍UNRUN。

{table(['case','variant','实际'],[[j['case_id'],j['variant'],'UNRUN_RESOURCE_GATE'] for j in ipc['jobs']])}

本次Root直接LAUNCHER_ERROR触发停止，没有STOP_REQUEST。RootIPC关于C09 ready/RPC取消、迟到ACK与全部停止交错仍待动态覆盖。[实际meta导出锁](evidence/NATIVE_EXPORT_LOCK.json)、[资源核算](evidence/RESOURCE_ACCOUNTING.json)。
''')

report('BATCH07_C09_HANDOFF_RESULTS.md','batch07 C09H34与真实C09交接',f'''
真实C09=NOT_EXERCISED。C09H34计划34（原28 safe接受路径、6 mutant），尝试0、完成0、接受0；下列全为UNRUN_RESOURCE_GATE。

{table(['C09H case','variant','actual'],[[j['case_id'],j['variant'],'UNRUN_RESOURCE_GATE'] for j in hc['jobs']])}

C09.ready、handoff意图、commit/持久ACK、receiver确认、handoff退出23见证均未生成。父协调器确实执行普通waitpid并记录child exit125/raw32000，这是首次启动失败的回收见证，未进入交接分类。resume_count=0、内部恢复0、独立resume调用0。

本次bootstrap认领、sealed memfd与C09持久交接属于不同责任：前者有实际前缀证据，后者未执行。exit125和缺ACK均阻断C09成功，原Root/H1–H8条件继续保持。[普通waitpid原件](<../../../DCL-R6-isolated-verification/batch07/native_snapshot/inputs/root_private/waitpid_886.json>)。
''')

calrows=[['C00','FAIL_STARTUP_GATE','服务启动请求1；票据/探针0；BC_SERVICE_IDENTITY_OR_LIMITS']]+[[f'C{i:02}','UNRUN_RESOURCE_GATE','首次失败后保持未运行'] for i in range(1,13)]
report('BATCH07_RESOURCE_CALIBRATION.md','batch07 C00–C12校准结果',f'''
当前C00服务准入失败，校准probe执行0、root机器PASS0；C01–C12均未运行。batch05的C00–C08旧PASS继续保留旧批次范围。

{table(['case','实际结果','阶段'],calrows)}

first C00MainPID由非阻塞systemd-run后的PID轮询取得；新service_confirmed在票据放行前检查8项/执行身份与限额，当前复核拒绝。C00未运行入口kernel/AS映射探针，C02内存/预留、C04第五task、C07/08异常退出、真实C09、C10封闭、C11故障和C12关闭/恢复均UNRUN。

slice配置与停止前kernel快照支持parent4tasks/4GiB这一窄范围；当前没有完整AS4资源资格或300秒整套可完成性结果。时间/预算上限未扩张，T0后0.309秒已关闭。[失败分析](BATCH07_COUNTEREXAMPLES.md)、[实际资源](BATCH07_RUNTIME_AND_RESOURCE.md)。
''')

report('BATCH07_S1_S9_RESULTS.md','batch07 S1–S9 34项结果',f'''
计划34，尝试/完成/通过/变异检出均0，全部UNRUN_RESOURCE_GATE；RANGE与Root独立原始重算未启动。

{table(['job','性质','variant','实际'],[[j['case_id'],j['property'],j['variant'],'UNRUN_RESOURCE_GATE'] for j in safety['jobs']])}

原范围信用/持久化/幂等/并发/CLOSED/N+1安全逻辑与输入保持冻结，当前没有新动态资格。[实际结果](evidence/ACTUAL_RESULTS.json)。
''')

report('BATCH07_GATE_NEGATIVE_RESULTS.md','batch07 17项资格门负向检查',f'''
计划17，实际尝试0、有效拒绝/检出0；Root gate审查及GATE_NEGATIVE_AUDIT未执行/生成。

{table(['case','冻结recipe','期望拒绝','实际'],[[j['case_id'],j['recipe'],j['expected_prefix'],'UNRUN_RESOURCE_GATE'] for j in safety['gate_negative_cases']])}

RESOURCE_GATE_PASS=NOT_OBTAINED。C00失败、其他C与40/56/34/S34/门17未运行均独立阻断FORMAL；bootstrap预检局部通过无法替代资源门。
''')

report('BATCH07_RESOURCE_ACCOUNTING.md','batch07持久预算与时间核算',f'''
本批已初始化持久账：**R=0/1000000**，24字节BRNGv001 counter、COMMITTED/after0/cap1000000 intent对应。无实际reserve事务，journal尚未创建，记录数/事务数0；这一缺件符合首次语义访问之前的状态。独立行政parser没有导入预算核心。

运行boot={run_boot}，T0={t0:.9f}，deadline={state['deadline']:.9f}，stop_at={state['stop_at']:.9f}；差值分别1800和1740，原窗口只初始化一次。没有模型/测试语义访问、退款、重置或resume。

{table(['时间/资源','实际'],[
 ['闭合boottime',f"{closed['boottime']:.9f} / T0+{account['closed_T0']:.9f}"],
 ['首次组空',f"T0+{account['first_empty_T0']:.9f}；close→empty {account['closed_to_empty_seconds']:.9f}s"],
 ['父waitpid',f"T0+{account['waitpid_T0']:.9f}；raw32000/exit125"],
 ['父seal前',f"T0+{account['final_before_seal_T0']:.9f}"],
 ['Windows活动调用',f"{host_exit['host_elapsed_ns']/1e9:.9f}s，包含预检/回传；独立时钟域"],
 ['charged peak/pids','782336B；观测1/max4；精确RSS与Root峰值N/A'],
 ['冻结访问/时间','总1000000/1800；cal100000/300；共同5000；BC481/512；完整cal62034'],
 ['实际测试与模型','语义访问0，搜索0，原判据未放宽']])}

23个native普通文件、32个最终程序/输入副本已保存。原生自动seal实际完成：{native_zip['manifest_rows']}行manifest、{native_zip['entries']}个ZIP条目，SHA `{native_zip['sha256']}`，逐流/逐文件差异0。socket仅保留类型/身份/mode元数据，不复制成普通字节文件。

账内容初始配对核验为PASS_INITIALIZED_ZERO_ACCOUNTING_ONLY；关闭后的账无法重新授权。历史batch05/04/02的R37293/37021/32191原件保持，47误副本及blocked by policy继续只读保留。

[核算JSON](evidence/RESOURCE_ACCOUNTING.json)、[native seal核对](evidence/NATIVE_ZIP_CHECK.json)、[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)。
''')

for model,scopes,note in [
 ('F1',['SMOKE','BRANCH','CHAIN','KEY','冻结mutants','反例重放','INV1–INV8'],'旧钥、历史责任、预算、ReadyState/ReadyUse和迟到IO边界保持。'),
 ('F4',['COST1','CE5/固定夹具','D2-DP','TRACE-REF','G64','压缩开关比较','冻结mutants','反例重放'],'候选与独立参考的业务语义隔离要求保持。')]:
    report(f'BATCH07_{model}_RESULTS.md',f'batch07 {model}实际机器检查结果',f'''
状态**UNRUN_RESOURCE_GATE**，实际模型启动/搜索/语义状态访问均0，PASS_BOUNDED授予0。资源门在C00服务复核阶段失败，FORMAL未启动。

{table(['冻结范围','实际'],[[s,'UNRUN_RESOURCE_GATE'] for s in scopes])}

{note} 冻结文件hash与原始输入匹配只支持版本身份，当前没有有限域完整覆盖、模型反例或运行费用结果。反例数量按“未搜索”记录，不能写作性质成立。
''')

report('BATCH07_COUNTEREXAMPLES.md','batch07首次失败、启动就绪缺口与未决字段',f'''
## CE-B07-01：C00复核在票据前拒绝

真实路径：单会话PREFLIGHT_QUALIFIED → seal/claim → same-PID exec → ENTRY_VERIFIED → 子Launcher初始化T0/预算 → 外部stop启动 → C00 systemd-run --no-block → MainPID轮询非零即退出 → service_confirmed复核 → `BC_SERVICE_IDENTITY_OR_LIMITS` → LAUNCHER_ERROR/CLOSED → 组空/父waitpid125/原生seal。

错误出自boot_continuity.py:338；8路OR涉及Uid、Gid、Groups、CapEff、NoNewPrivs、LimitAS、LimitASSoft和ControlGroup。错误字段值没有持久化，ticket_C00与BOOT_START也尚未发布，实际unit_before_ticket和/proc/status仅位于丢失的局部frame。因此**具体失配项UNRESOLVED**；当前无法把某个UID/限额值写成已观测原因。

源码确认的缺口：guard.py launch_one在--no-block后只等MainPID>0，尚无Type=exec/ActiveState就绪屏障，就要求进程具备最终UID/能力/AS/cgroup。该时序存在合法启动中的临态误拒绝实例。运行journal仅Starting→KILL，缺Started；charged peak仅782336B/1task，也与早期启动相符。这支持“过早检查exec后属性”的竞态假设，未形成具体失败字段的完整因果证明。

## 证据与时钟边界

运行boot始终{run_boot}，前缀Owner始终828/start7252；故障类型并非BC_BOOT_CHAIN/STALE_BOOT。CLOSED在BOOTTIME{closed['boottime']:.9f}，父waitpid/组空/封存均成功。journal的MONOTONIC序列只在自身时钟域计算，不能据未校准MONOTONIC和BOOTTIME差值推导精确错误发生时刻。

事后boot为{audit['observation_boot_id']}，manager查到的not-found/default属性不参与运行因果判定。首次journal读取的带连字符UUID被解析拒绝，原件保留；同一运行boot改用32-hex格式只读补导出，取得7条限定unit消息。该行政读取修正没有重跑任何case或更改目标代码。

## 下一阶段最小静态修复方向

先在冻结startup接线内补有界exec-ready屏障：等待Type=exec进入允许active状态，再fresh读取稳定MainPID/start_ticks、实际/proc身份、资源属性和cgroup；期限仍绑定当前case/deadline。此屏障不能等待依赖尚未发放ticket的应用ready，以免形成票据前死锁。保留全部原UID/AS/能力/ACK/闭合断言，失败或退出直接停止。

在判定前持久保存每个期望/实际值、采样起止、boot/身份、unit状态与确切失败predicate，使下次失败可独立重算。需要声明合法activating→exec、临态UID变化、早退出、属性漂移、超时及STOP交错的正反见证，再冻结新版本与匹配执行申请。本轮源码/权限修复0、case重试0、预算/期限重置0、batch08创建0。

该失败属于验证基础设施的启动准入，未运行F1/F4，未形成协议模型反例或原创性分离实例。[源码原段](evidence/FAILURE_SOURCE_EXCERPTS.txt)、[原始trace解码](evidence/STDERR_DECODE.json)、[因果评估](evidence/CAUSE_ASSESSMENT.json)、[运行journal](evidence/JOURNAL_SUMMARY.json)。
''')

answers=[
 ['1 单会话预检','实际执行，PREFLIGHT_QUALIFIED'],['2 同进程exec','实际成功到Guard入口；PID828/start7252两侧相同'],
 ['3 boot贯穿','预检/Root入口/子scheduler均一致；完整服务证书未通过'],['4 封印凭据','实际生成，seals15及SHA见摘要'],
 ['5 一次认领','实际消费一次；重复拒绝专项测试未运行'],['6 服务内复核','C00失败，BC_SERVICE_IDENTITY_OR_LIMITS'],
 ['7 BC40','尝试/完成0'],['8 10变异','实际检出0，均未运行'],['9 RootIPC56','尝试0/检出0'],
 ['10 C09H/真实C09','34未运行；真实交接NOT_EXERCISED'],['11 C00–C12','C00启动门失败/探针0；C01–C12未运行'],
 ['12 S34/门17','均0'],['13 RESOURCE_GATE_PASS','NOT_OBTAINED'],['14 F1/F4','均UNRUN_RESOURCE_GATE，模型搜索0'],
 ['15 PASS_BOUNDED','授予0'],['16 资源','R0/1000000，T0已建，0.309秒关闭，0.327秒组空；charged peak782336B'],
 ['17 首次失败/下一步','8项复核聚合拒绝；补exec-ready屏障与失败快照，精确字段仍待证']]
report('BATCH07_FINAL_DECISION.md','batch07最终裁决',f'''
**RESOURCE_GATE_FAILED；首个关键失败为C00启动复核BC_SERVICE_IDENTITY_OR_LIMITS。** 本批真实执行了单会话预检、sealed能力/一次认领和same-PID exec；这些前缀成功证据保留，服务内完整资格失败，后续C/40/56/34/S/门和模型停止。

{table(['用户要求','实际结果'],answers)}

运行boot={run_boot}，Root父828/start7252，scheduler886/start7372，外部stop890/start7379。T0={t0:.9f}、deadline={state['deadline']:.9f}、stop_at={state['stop_at']:.9f}，原窗口只建1次。最终R=0、COMMITTED初始intent，journal尚无事务。CLOSED在T0+{account['closed_T0']:.9f}，首次组空+{account['first_empty_T0']:.9f}，普通父waitpid raw32000/exit125；原生自动封存22条目通过字节核对。

当前观测的活动前缀没有batch06式跨boot，具体WSL历史触发源仍非本批诊断范围。事后不同boot仅用于文件/清理观察；当前service默认值不回写运行结果。精确失配字段没有原始采样，源码就绪屏障缺失、Starting-only journal和小charge峰值支持启动临态误拒绝假设，结论保持其证据边界。

主机冻结32项/部署31项与所有版本hash一致，21份程序身份核验完成；native3.12实际语法路径通过20源码。Root/全局资源源代码未改，现场权限修复0、case重跑0、resume0、主动WSL shutdown0、batch08创建0。核查确认专用进程与父组为空；全部23个native普通文件、32最终文件、34条BC事件、15条内部命令双流、7条run-boot journal及私有凭据证据已封存。

1920项R6历史研究、旧工作区/旧原件、47误副本与原包hash保持，旧batch06 PREFLIGHT_FAILED、batch05 R37293及其他历史失败不改。原票据秘密内容只保留private原件，普通报告/日志仅用摘要与验证状态。

D1-PBFT-SEAL/1.1原条件、强G覆盖、STRICT_SEPARATION_INSTANCES=0、IMPLEMENTATION_GATE=CLOSED保持。机器前缀观察与完整资源资格、有限模型性质及原创性分别裁决。

[启动前缀](BATCH07_BOOT_CONTINUITY_RESULTS.md)、[资源核算](BATCH07_RESOURCE_ACCOUNTING.md)、[首次失败](BATCH07_COUNTEREXAMPLES.md)、[证据索引](EVIDENCE_INDEX.md)、[交付核验](evidence/DELIVERY_CHECK.json)。
''')

internal=load(E/'INTERNAL_COMMANDS.json')['commands'];admin=[load(p) for p in sorted((E/'commands').glob('*.result.json'))]
report('COMMAND_SUMMARY.md','batch07命令、时钟与原始双流',f'''
活动入口严格使用冻结windows_entry.py，内部只启动1次WSL。Windows入口原件保存实际argv、PID54916、UTC起止、perf_counter耗时及其WSL子进程exit125；执行工具外层PowerShell报告exit1，两层结果分别保留。

{table(['内部序号','实际argv','BOOTTIME开始','BOOTTIME结束','exit'],[[str(r['order']),' '.join(r['argv']),r['start']['boottime'],r['after']['boottime'],r['exit_code']] for r in internal])}

15条命令的stdout/stderr由原BC事件hex逐字节解码，见[INTERNAL_COMMANDS](evidence/INTERNAL_COMMANDS.json)及[internal_commands](evidence/internal_commands)。Guard后续锁定的stop/C00/systemctl调用按冻结控制流与原journal对应，C00票据未生成，因此没有其argv/实际status局部frame的完整持久快照；不补造execve审计。

{table(['行政编号','用途','exit'],[[link(E/f"commands/{i:02}.result.json",f'{i:02}'),r['purpose'],r['exit_code']] for i,r in enumerate(admin,1)])}

行政1仅静态部署；2–5发生在失败后，仅读状态、导出或限定journal。首次journal错误及更正原件都保存。原始stderr为WSL客户端UTF16LE提示前缀＋native UTF8 traceback，原字节不改，解码说明见[STDERR_DECODE](evidence/STDERR_DECODE.json)。活动日志BOOTTIME、journal MONOTONIC与Host时钟域分别使用。
''')

required=['BATCH07_AUTHORIZATION_AND_LOCK.md','BATCH07_BOOT_CONTINUITY_RESULTS.md','BATCH07_BOOT_REGRESSION_RESULTS.md',
 'BATCH07_RUNTIME_AND_RESOURCE.md','BATCH07_ROOTIPC_RESULTS.md','BATCH07_C09_HANDOFF_RESULTS.md',
 'BATCH07_RESOURCE_CALIBRATION.md','BATCH07_S1_S9_RESULTS.md','BATCH07_GATE_NEGATIVE_RESULTS.md',
 'BATCH07_RESOURCE_ACCOUNTING.md','BATCH07_F1_RESULTS.md','BATCH07_F4_RESULTS.md','BATCH07_COUNTEREXAMPLES.md','BATCH07_FINAL_DECISION.md']
dump(P/'SOURCE_INDEX.json',{'schema':'B07-source-index/1','source_version':'BootContinuity-static-1/r4','canonical_host':str(W),
 'actual_Linux':'/var/lib/dcl-r6/bc01','runtime_Linux':'/var/lib/dcl-r6/batch07','native_host':str(N),'frozen_host':str(F),
 'files':frozen['files'],'native_files':native['files'],'nonregular':native['nonregular'],
 'active_WSL_calls':1,'source_changes':0,'run_boot':run_boot,'observation_boot':audit['observation_boot_id'],
 'private_scope':'Raw Root-private capability records retain original path; ordinary summaries redact nonce',
 'native_seal_sha256':native_zip['sha256'],'resource_verdict':'RESOURCE_GATE_FAILED'})
report('EVIDENCE_INDEX.md','batch07研究证据索引',f'''
{table(['交付材料','范围'],[[link(P/name),name[:-3]] for name in required])}

[单会话原始stdout](evidence/windows_entry.stdout.raw)、[原始stderr](evidence/windows_entry.stderr.raw)、[分编码说明](evidence/STDERR_DECODE.json)、[Windows入口plan](evidence/WINDOWS_ENTRY_PLAN.json)、[Windows退出](evidence/WINDOWS_ENTRY_EXIT.json)、[精确命令索引](COMMAND_SUMMARY.md)。

[脱敏boot前缀](evidence/BOOT_CONTINUITY_ACTUAL.json)、[首次失败](evidence/FIRST_FAILURE.json)、[因果边界](evidence/CAUSE_ASSESSMENT.json)、[原始源码段](evidence/FAILURE_SOURCE_EXCERPTS.txt)、[资源初始账核算](evidence/RESOURCE_ACCOUNTING.json)、[实际结果](evidence/ACTUAL_RESULTS.json)。

[23 native文件锁](evidence/NATIVE_EXPORT_LOCK.json)、[最终32文件锁](evidence/FROZEN_SOURCE_EXPORT_LOCK.json)、[源/native映射](SOURCE_INDEX.json)、[原生22条目seal](evidence/NATIVE_ZIP_CHECK.json)、[事后清理](evidence/POSTFAIL_AUDIT.json)、[run journal7条](evidence/JOURNAL_SUMMARY.json)、[更正查询原件](evidence/RUN_BOOT_JOURNAL_CORRECTED_RESULT.json)、[1920历史保护](evidence/HISTORY_PROTECTION_CHECK.json)。

普通日志只含凭据摘要/验证结果；原ticket与Root私有审查原件位于native_snapshot/inputs/root_private路径，Linux原件mode0600且父目录0700。host导出证明字节，原Linux权限/ACL/inode由元数据锁保留。不存在的BOOT_START/C00ticket/C09ACK、40/56/34/S/门/F1/F4原始结果按未完成阶段登记。

当前[BATCH07_EVIDENCE.zip](BATCH07_EVIDENCE.zip)是授权私有审阅包，含研究、native23、最终32及四导航；Root原件和各日志保持。[OUTPUT_MANIFEST](OUTPUT_MANIFEST.json)逐项列路径/字节/SHA/archive_path，[DELIVERY_CHECK](evidence/DELIVERY_CHECK.json)另记manifest和ZIP摘要。排除自引用，逐流行政核验不升级RESOURCE_GATE或模型性质。四导航旧正文在本轮前完整快照保存。
''')
report('README.md','DCL-R6-batch07','''
实际单会话预检/封印认领/same-PID exec前缀取得证据；C00服务复核BC_SERVICE_IDENTITY_OR_LIMITS首个失败，已CLOSED/组空并原生seal。R0，T0已初始化，后续所有回归/模型未运行。

[最终裁决](BATCH07_FINAL_DECISION.md) · [首次失败](BATCH07_COUNTEREXAMPLES.md) · [证据索引](EVIDENCE_INDEX.md) · [私有审阅包](BATCH07_EVIDENCE.zip)

具体失配字段未采样，启动就绪竞态为有支持的假设。IMPLEMENTATION_GATE=CLOSED；严格分离0。
''')
intro='''# DCL-R6-batch07 最新实际裁决（2026-11-11）

RESOURCE_GATE_FAILED：BootContinuity-static-1/r4已实际单会话预检、sealed fd/一次认领、same-PID exec到Guard；活动boot060a08fc…、父PID828/start7252贯穿前缀。C00票据前服务复核抛BC_SERVICE_IDENTITY_OR_LIMITS，BOOT_START未发布；具体8路失配字段无快照，源码MainPID>0缺exec-ready屏障与Starting-only journal支持启动临态竞态假设。

T0=73.768774900，R0/1000000；T0+0.309347559闭合、+0.327163166组空，普通父waitpid raw32000/exit125。原生22条目seal、23 native文件、32冻结文件、34事件/15内部命令及7条run journal封存；source/权限修复、case重试、resume与batch08创建均0。BC40、RootIPC56、C09H34、真实C09、C01–C12、S34/门17及F1/F4都未完成准入；PASS_BOUNDED授予0。

下一步仅列有界exec-ready/稳定身份屏障及完整失败采样的最小静态修复方向，保持原身份/AS/ACK/停止断言。D1-PBFT-SEAL/1.1原条件、强G覆盖、严格分离0、IMPLEMENTATION_GATE=CLOSED保持。

[batch07最终裁决](DCL-R6-batch07/BATCH07_FINAL_DECISION.md) · [首次失败](DCL-R6-batch07/BATCH07_COUNTEREXAMPLES.md) · [证据索引](DCL-R6-batch07/EVIDENCE_INDEX.md)

以下为本轮启动前完整保留的历史导航，各旧阶段资格/许可/下一步按对应时点理解。

---

'''
for row in baseline['navigation']:(ROOT/row['original']).write_bytes(intro.encode()+Path(row['snapshot']).read_bytes())

planned={P/'OUTPUT_MANIFEST.json',P/'BATCH07_EVIDENCE.zip',E/'DELIVERY_CHECK.json'}
links=0;errors=[]
for path,content in [(q,q.read_text(encoding='utf-8')) for q in P.glob('*.md')]+[(ROOT/'README.md',intro)]:
    assert '不是' not in content
    for dest in re.findall(r'\]\(([^)]+)\)',content):
        dest=dest.strip('<>')
        if '://' in dest or dest.startswith('#'):continue
        links+=1;q=(path.parent/dest.split('#')[0]).resolve()
        if not q.exists() and q not in planned:errors.append({'file':str(path),'target':dest})
assert not errors,errors
for name in required:assert (P/name).is_file()
secret=load(N/'inputs/root_private/boot/activation.json')['ticket']['nonce'].encode()
ordinary=[*P.glob('*.md'),E/'windows_entry.stdout.raw',E/'windows_entry.stderr.raw',
          E/'BOOT_CONTINUITY_ACTUAL.json',E/'FIRST_FAILURE.json',E/'CAUSE_ASSESSMENT.json',E/'STDERR_DECODE.json']
assert all(secret not in q.read_bytes() for q in ordinary)
dump(E/'NONCE_DISCLOSURE_CHECK.json',{'schema':'B07-nonce-scope/1','status':'PASS_ADMIN_ONLY',
 'ordinary_files_checked':len(ordinary),'raw_nonce_matches':0,
 'raw_originals_scope':'native_snapshot/inputs/root_private and authorized private review archives',
 'nonce_value_in_this_check':False})
parsed=0
for directory in [P,N,F]:
    for q in directory.rglob('*.json'):
        if q.name not in ['OUTPUT_MANIFEST.json','DELIVERY_CHECK.json']:load(q);parsed+=1
dump(E/'ADMIN_REPORTING_RECEIPT.json',{'schema':'B07-reporting/1','script':str(Path(__file__).resolve()),
 'new_links_checked':links,'link_errors':errors,'JSON_parsed':parsed,'target_imports_or_replays':0,
 'scope':'Offline byte/schema/source/log parsing; no new target actions; no raw nonce in ordinary summary'})
excluded={P/'OUTPUT_MANIFEST.json',P/'BATCH07_EVIDENCE.zip',E/'DELIVERY_CHECK.json'}
rows=[]
for directory,prefix in [(P,'research'),(N,'native'),(F,'FROZEN_BOOTCONTINUITY')]:
    for q in sorted(directory.rglob('*')):
        if q.is_file() and q not in excluded:rows.append({'host':str(q),'scope':prefix,'archive_path':prefix+'/'+q.relative_to(directory).as_posix(),'bytes':q.stat().st_size,'sha256':sha(q)})
for row in baseline['navigation']:
    q=ROOT/row['original'];rows.append({'host':str(q),'scope':'navigation','archive_path':'navigation/'+q.name,'bytes':q.stat().st_size,'sha256':sha(q)})
manifest={'schema':'B07-output-manifest/1','files':rows,'scope_counts':dict(Counter(r['scope'] for r in rows)),
 'exclusions':['OUTPUT_MANIFEST.json','BATCH07_EVIDENCE.zip','evidence/DELIVERY_CHECK.json'],'nonregular':native['nonregular'],
 'artifact_scope':'Authorized private review; contains Root-private originals; ordinary log summaries contain only digests',
 'resource_verdict':'RESOURCE_GATE_FAILED'}
dump(P/'OUTPUT_MANIFEST.json',manifest);archive=P/'BATCH07_EVIDENCE.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for row in rows:z.write(row['host'],row['archive_path'])
    z.write(P/'OUTPUT_MANIFEST.json','OUTPUT_MANIFEST.json')
with zipfile.ZipFile(archive) as z:
    assert len(set(z.namelist()))==len(rows)+1
    for row in rows:
        b=z.read(row['archive_path']);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'] and sha(row['host'])==row['sha256']
    assert z.read('OUTPUT_MANIFEST.json')==(P/'OUTPUT_MANIFEST.json').read_bytes()
delivery={'schema':'B07-delivery/1','status':'PASS_ADMIN_ONLY','resource_verdict':'RESOURCE_GATE_FAILED',
 'source_version':'BootContinuity-static-1/r4','required_reports':14,'manifest_rows':len(rows),'scope_counts':manifest['scope_counts'],
 'ZIP_entries':len(rows)+1,'ZIP_stream_errors':[],'manifest_sha256':sha(P/'OUTPUT_MANIFEST.json'),'ZIP_sha256':sha(archive),'ZIP_bytes':archive.stat().st_size,
 'active_WSL_calls':1,'same_boot_PID_exec_prefix_observed':True,'service_confirmation':'FAILED',
 'native_files':23,'frozen_files':32,'native_auto_seal':True,'native_zip_entries':22,'run_journal_records':7,
 'BC40_attempted':0,'BC_mutants_detected':0,'RootIPC56_attempted':0,'C09H34_attempted':0,'C09':'NOT_EXERCISED',
 'R':0,'T0':t0,'F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
 'model_searches':0,'postfailure_processes_empty':True,'history_files':1920,'history_mismatches':0,
 'links_checked':links,'link_errors':[],'JSON_parsed':parsed,'source_or_permission_repairs':0,'retries':0,'resume':0,'new_batch08':False,
 'precise_failed_metadata_field':'UNRESOLVED','IMPLEMENTATION_GATE':'CLOSED','strict_separation_instances':0,
 'sealed_utc':datetime.now(timezone.utc).isoformat(),'self_excluded_from_manifest_and_zip':True,
 'scope':'Byte/schema/new links/ZIP verification only; does not certify unrun tests or full boot/service safety'}
dump(E/'DELIVERY_CHECK.json',delivery)
print(json.dumps(delivery,ensure_ascii=False,indent=2))
