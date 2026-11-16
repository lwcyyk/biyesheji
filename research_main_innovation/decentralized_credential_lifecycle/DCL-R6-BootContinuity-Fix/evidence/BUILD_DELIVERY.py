"""Offline historical evidence review, reports and byte-sealed static delivery."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import ast
import hashlib
import json
import os
import re
import struct
import zipfile

E=Path(__file__).resolve().parent
P=E.parent
ROOT=P.parent
W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\bc01')
WORK=W.parent
B06=ROOT/'DCL-R6-batch06'
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def link(p,label=None):return '['+(label or Path(p).name)+'](<'+os.path.relpath(p,P).replace('\\','/')+'>)'
def table(headers,rows):
    def c(x):return str(x).replace('|','\\|').replace('\n','<br>')
    return '\n'.join(['|'+'|'.join(headers)+'|','|'+'|'.join(['---']*len(headers))+'|']+['|'+'|'.join(map(c,r))+'|' for r in rows])
def report(name,title,text):
    (P/name).write_text('# '+title+'\n\nMaterial Passport：BootContinuity-static-1/r4；host离线静态修复；2026-11-11；WSL查询/目标执行0。\n\n'+text.strip()+'\n',encoding='utf-8')
def point(file,name):
    n=next(n for n in ast.walk(ast.parse((W/'src'/file).read_text())) if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
    return link(W/'src'/file,file+':'+str(n.lineno)+' '+name)

base=load(E/'BASELINE_LOCK.json');frozen=load(E/'STATIC_WORKSPACE_LOCK.json');static=load(E/'STATIC_CHECKS.json')
assert frozen['version']=='BootContinuity-static-1/r4'
cfg=load(W/'inputs/boot_contract.json');lock=load(W/'inputs/execution_lock.json')
commands=[load(B06/f'evidence/commands/{i:02}.result.json') for i in range(1,20)]
assert all(c['exit_code']==0 for c in commands)
for c in commands:
    for stream in ['stdout','stderr']:assert sha(B06/c[stream+'_file'])==c[stream+'_sha256']
env=load(B06/'evidence/PREFLIGHT_ENV.json');final=load(B06/'evidence/PREFLIGHT_FINAL.json');post=load(B06/'evidence/POSTFAIL_AUDIT.json')
boots=[env['boot_id'],final['boot_id'],post['boot_id']]
assert len(set(boots))==3
span=(datetime.fromisoformat(commands[14]['end_utc'])-datetime.fromisoformat(commands[0]['start_utc'])).total_seconds()
gap=(datetime.fromisoformat(commands[5]['start_utc'])-datetime.fromisoformat(commands[4]['end_utc'])).total_seconds()
assert abs(span-109.295102)<1e-7
timeline=[]
for i,c in enumerate(commands,1):
    epoch=boots[{2:0,15:1,16:2}[i]] if i in [2,15,16] else None
    linux_uid=0 if i==2 else None
    timeline.append({'order':i,'start_utc':c['start_utc'],'end_utc':c['end_utc'],
      'time_source':'Windows datetime.now(timezone.utc); elapsed from host UTC subtraction',
      'elapsed_ms':c['elapsed_ms'],'Windows_argv':c['argv'],'wsl_client_pid':c['wsl_client_pid'],
      'Linux_pid':'UNRECORDED','Linux_stable_identity':'UNRECORDED','Linux_euid_observed':linux_uid,
      'boot_id_observed':epoch,'exit_code':c['exit_code'],'source':str(B06/f'evidence/commands/{i:02}.result.json')})
dump(E/'BOOT_TIMELINE.json',{'schema':'BC-batch06-timeline/1','events':timeline,'boot_observation_commands':[2,15,16],
 'preflight_host_UTC_span_seconds':span,'gap_after_command5_before6_seconds':gap,
 'not_observed':'No Linux PID/start_ticks or boot_id at commands1,3-14,17-19; no host/WSL shutdown event log',
 'cause':'BOOT_CHANGE_CAUSE_UNRESOLVED','target_launcher_calls':0})

history=[]
def verify(name,rows,path,key='sha256'):
    errors=[]
    for r in rows:
        q=path(r)
        if not q.is_file() or sha(q)!=r[key] or ('bytes'in r and q.stat().st_size!=r['bytes']):errors.append(str(q))
    history.append({'name':name,'count':len(rows),'mismatches':errors,'status':'PASS_ADMIN_ONLY' if not errors else 'FAIL'})
    assert not errors,(name,errors)
verify('1120 historical research files',base['history'],lambda r:ROOT/r['relative'])
verify('RootIPC r4 original44',base['original_files'],lambda r:Path(base['original_workspace'])/r['relative'])
verify('BootContinuity final32 host files',frozen['files'],lambda r:W/r['relative'])
for folder in ['DCL-R6-batch06','DCL-R6-batch05','DCL-R6-batch04']:
    for fn in ['NATIVE_EXPORT_LOCK.json','FROZEN_SOURCE_EXPORT_LOCK.json']:
        x=load(ROOT/folder/'evidence'/fn);verify(folder+'/'+fn,x['files'],lambda r:Path(r['host']))
for folder in ['DCL-R6-GapClosure','DCL-R6-BudgetFix']:
    x=load(ROOT/folder/'evidence/STATIC_WORKSPACE_LOCK.json');verify(folder+' old workspace',x['files'],lambda r,x=x:Path(x['host'])/r['relative'])
x=load(ROOT/'DCL-R6-C09Fix/evidence/STATIC_WORKSPACE_LOCK.json');verify('c09f01 original37',x['files'],lambda r:WORK/'c09f01'/r['relative'])
x=load(ROOT/'DCL-R6-batch02-Perf/evidence/BASELINE_LOCK.json');verify('batch02 original51',x['immutable_B02_external'],lambda r:Path(r['path']))
x=load(ROOT/'DCL-R6-batch02-Perf/evidence/DUPLICATE_REGISTER.json');verify('Mispath47 read/hash only',x['files'],lambda r:Path(x['path'])/r['relative'],'duplicate_sha256')
for r in base['navigation']:assert sha(r['snapshot'])==r['sha256']
archives=[]
for folder,name in [('DCL-R6-batch06','BATCH06_EVIDENCE.zip'),('DCL-R6-RootIPC-Fix','ROOTIPC_STATIC_REVIEW.zip'),('DCL-R6-batch05','BATCH05_EVIDENCE.zip')]:
    p=ROOT/folder/name
    with zipfile.ZipFile(p) as z:
        m=json.loads(z.read('OUTPUT_MANIFEST.json'))
        for row in m['files']:
            b=z.read(row['archive_path']);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
        archives.append({'path':str(p),'entries':len(z.namelist()),'sha256':sha(p),'stream_mismatches':[]})
old_budgets={}
for folder,expected in [('batch05',37293),('batch04',37021),('batch02',32191)]:
    p=WORK/folder/'native_snapshot/out/visits.bin'
    if not p.exists():
        matches=list((WORK/folder).rglob('visits.bin'));assert len(matches)==1;p=matches[0]
    assert struct.unpack('<QQ',p.read_bytes()[8:])==(expected,1000000);old_budgets[folder]=expected
dump(E/'HISTORY_PROTECTION_CHECK.json',{'schema':'BC-history/1','checks':history,'archives':archives,
 'budgets':old_budgets,'modified_history_files':0,'mispath_actions':'read/hash only',
 'prior_policy_rejection':'blocked by policy retained','new_native_queries':0})

timeline_rows=[]
labels={1:'静态文件/运行时摘要核对',2:'首次boot/基础环境',3:'systemd Version',4:'单位冲突检查',5:'manager失败检查',
 6:'准备1批根',7:'准备2 out',8:'准备3 private',9:'准备4 slice安装',10:'准备5 unit verify',11:'准备6 daemon-reload',
 12:'授权原文安装',13:'授权回执安装',14:'父slice属性',15:'最终boot/元数据→拒绝',16:'证据导出/事后boot',17:'事后父组状态',18:'事后单位列表',19:'当前boot限定journal'}
for t in timeline:
    timeline_rows.append([link(Path(t['source']),str(t['order'])),labels[t['order']],t['start_utc'],t['end_utc'],
      f"{t['elapsed_ms']:.3f}",str(t['wsl_client_pid']),t['boot_id_observed'] or '未采集',t['exit_code']])
report('BOOT_CHANGE_TIMELINE.md','batch06 三次boot观测与完整事件时间线',f'''
batch06预检/准备由19次相互独立的`wsl.exe --distribution Ubuntu-24.04 --exec …`组成。原Host EXEC_NATIVE逐次Popen/wait，返回后Linux命令进程结束；Host脚本之间还存在间隙。原记录中没有一个Linux受信进程贯穿全部预检、准备和Launcher交接的身份见证。

{table(['原始编号','事件','宿主UTC开始','宿主UTC完成','elapsed ms','Windows wsl PID','实际观测boot','exit'],timeline_rows)}

表中时间全部源于Windows datetime UTC；elapsed为该时钟差，原脚本未使用单调计时。Linux reader PID/start_ticks均未记录；仅命令2明确输出euid0。Windows子PID具有宿主含义，不能代作Linux进程身份。每项精确完整argv含`-c`源及双流见链接原JSON，[机器时间线](evidence/BOOT_TIMELINE.json)保留全部Windows argv。

只在命令2、15、16采集boot：`{boots[0]}`、`{boots[1]}`、`{boots[2]}`。命令1的1326摘要核对exit0，其boot未采集；命令6–14的具体boot同样未知。当前证据不能把六条准备逐一分配给某个boot。两次变化只可界定在相邻boot读取区间之间。

命令1开始至15完成跨度{span:.6f}秒，命令5完成至6开始间隙{gap:.6f}秒。命令14观测父slice inactive/dead、4tasks/4GiB；最终15其余谓词true、same_boot=false，PREFLIGHT_FAILED成立。命令16–19为失败后导出/核查；最终查询进程为空、cgroup不存在。没有Launcher/T0/预算账/目标测试，本轮也没有恢复或重试。

原Windows宿主驱动路径：{link(B06/'evidence/EXEC_NATIVE.py')}、{link(B06/'evidence/PREPARE_AND_RUN.py')}。原包{link(B06/'BATCH06_EVIDENCE.zip')}与157个ZIP条目逐流复核，历史字节保持。
''')

report('WSL_LIFECYCLE_HYPOTHESES.md','WSL生命周期假设及证据边界',f'''
**BOOT_CHANGE_CAUSE_UNRESOLVED**。三个不同boot_id证明发生了运行代次变化，当前记录不足以定位触发者。

{table(['假设','已知证据','当前裁决/反证责任'],[
 ['H1 空闲生命周期','多次独立WSL exec、命令间隙、没有贯穿Linux进程的记录；命令6/16耗时较长','可行解释，尚待证；冷启动样式耗时不足以确证'],
 ['H2 宿主或外部程序','已记录19条argv中没有--shutdown/--terminate；宿主休眠/服务重启/内核事件日志缺失','UNRESOLVED；无法排除未记录的外部事件'],
 ['H3 编排跨实例','命令2/15/16观测不同boot；每条wsl调用独立退出，Host复用base结果直到最终same_boot检查','成立于观测边界；最终防线成功拒绝，未将旧动态资格授予Launcher']])}

Microsoft的2022年官方说明写明“systemd services will NOT keep your WSL instance alive”。这支持“PID1/systemd服务存在不足以证明实例持续存活”的一般判断；该文不能证明本机此次自动退出。[官方说明](https://devblogs.microsoft.com/commandline/systemd-support-is-now-available-in-wsl/)

LC历史裁决也记录过准备前后boot不同，且明确静态配置持久性与运行身份分列：{link(ROOT/'DCL-R6-LC/LC_FINAL_DECISION.md')}。batch06当前事实为最终拒绝、Launcher0、T0/R=null；H3并非一次已经发生的越权启动。

本轮没有执行新的WSL查询、事件日志读取或诊断命令。WSL版本、宿主策略、空闲设置及当前boot均保持未查询状态；已知Ubuntu24.04.5、Python3.12.3、systemd255.4和kernel6.18.33.2是历史观测/未来合同。需要定位具体触发源时，另行申请明确的只读平台诊断范围。

[公开来源元数据](evidence/PRIMARY_SOURCES.json)、[原始时序](BOOT_CHANGE_TIMELINE.md)、[首次失败原件](../DCL-R6-batch06/evidence/FIRST_FAILURE.json)。
''')

layers=[
 ['源/输入/执行锁内容摘要','A','实际当前对象、规则版本、来源与锁匹配时可复用既有陈述；当前字节仍重新hash','文件变更、规则/锁变化失效'],
 ['授权原文/静态许可范围','A','仅复用原文/摘要与已批准范围的事实；不沿用旧运行资格','原文/权限范围/版本变化停止'],
 ['Python版本合同与单位配置内容','A','版本要求和静态配置陈述；当前解释器/单位状态另查','对象漂移停止'],
 ['当前boot/PID/start_ticks/UID/GID/cgroup','B','每次启动同一会话fresh读取','任一身份或代次变化失效'],
 ['systemd版本/manager失败/活动属性','B','入口及激活接入核查，服务启动后再核状态','属性/来源不确定拒绝'],
 ['临时目录/IPC/Root/Launcher/Receiver及成员','B','当前实例对象、实际元数据/ACL和稳定身份','进程退出、对象/归属变化失效'],
 ['预检ticket/memfd/一次认领','B','当前boot和同一Owner PID/start_ticks/锁fd，初始10秒有效','旧boot/新进程/重用/缺cap拒绝'],
 ['C/S/门及RESOURCE_GATE_PASS','运行B','全套当前boot、T0、预算和当前身份联合核验','重启、关闭、漂移后失效，保留原始失败证据']]
report('PREFLIGHT_EVIDENCE_LAYERS.md','分层证据、静态缓存与失效合同',f'''
{table(['对象','层','适用条件','失效'],layers)}

缓存格式固定`rule_version=BC-A/1`、对象路径与摘要、原始来源引用、当前执行锁、source_mode及复用条件。{point('boot_continuity.py','artifact_check')}生成此层陈述；该版始终重新读取当前source/runtime/绑定输入摘要，不用静态缓存跳过当前文件验证。可以复用既有语法/来源的陈述身份，不能复用旧进程、单位或资源资格。

Layer B由同一Linux受信进程依次采集，第一次boot作为资格周期锚。每个命令前后和hash块之间核boot及120秒预检期限；最终快照覆盖当前boot、Root身份/cgroup、账户、残留、当前manager与父slice属性。Root入口在exec后再采集，子scheduler及实际C00/C10服务再核当前身份。

预检结果使用PREFLIGHT_QUALIFIED、ENTRY_VERIFIED、ACTUAL_SERVICE_CONFIRMED等不同状态，RESOURCE_GATE_PASS仅留给完整原资源资格门。新boot导致旧动态资格不可复用；源/输入/授权漂移直接停止，禁止重写旧boot或时间戳。持久认领及既存预算/窗口拒绝路径使跨boot自动补窗无法成立。

本轮静态检查适用host语法与AST，目标3.12编译/当前平台资格均UNRUN。Source-only包不携带旧pyc，未来在实际3.12入口`compile(source)`只检语法、不执行模型或写缓存；此差异列入新许可。
''')

report('BOOT_BOUND_AUTHORIZATION.md','同boot一次性启动资格与执行凭据',f'''
启动资格同时绑定batch07、当前boot_id、同一Owner PID/start_ticks、source manifest、执行锁、授权原文摘要、Boot合同、当前Root cgroup和初始有效期。资格由新boot的真实观测生成；旧记录仅保留历史，不改写为当前代次。

{point('boot_continuity.py','prepare_activation')}在受保护Root私有目录创建`activation.json`（O_EXCL）与排他flock，任何失败保留已认领状态。持久claim先于exec：包含nonce、完整ticket、initial_entered和resume_issued。没有第二个初始激活入口；ROOT已存在或已有state/counter/CLOSED即拒绝。

ticket还写入带WRITE/GROW/SHRINK/SEAL封印的memfd，fd和lock fd显式设为跨exec继承。Guard验证封印、内容摘要、设备/inode、当前持锁文件身份、Owner和boot，再把initial_entered持久化为true。普通JSON或环境变量中的数字单独不足以形成资格。检查点：{point('boot_continuity.py','read_capability')}、{point('boot_continuity.py','guard_admission')}。

内核对象随原进程/实例结束而失去存活见证，持久claim则保留。新boot即使复用相同PID/start_ticks也不满足boot相等；新入口遇到已准备批根/原claim/预算拒绝。memfd/sealing及exec fd继承参考[Linux memfd_create](https://man7.org/linux/man-pages/man2/memfd_create.2.html)、[execve](https://man7.org/linux/man-pages/man2/execve.2.html)，实际平台兼容性待授权验证。

C09预定退出23仍由原持久ACK、receiver、父waitpid、fresh-read和一次分类机制证明。只有原Guard返回验证后的23，外层同一Root进程才进行一次内部resume；新认领位先消耗，原T0/deadline/stop_at和counter读取核对，原handoff.resume_admission保留。初始10秒期限只作用于首次激活，内部恢复使用原运行窗口，无法得到新T0或新预算。

Root/Windows操作员继续属于TCB，授权文件沿用原可信操作流程与受保护安装；本版没有宣称能抵抗恶意Root或伪造Windows操作员。新执行授权必须明确接受单会话exec、同进程C09恢复、source-only封装与预检TCB界。
''')

report('SINGLE_SESSION_LAUNCH_DESIGN.md','单次WSL入口与可复核启动交接',f'''
Windows前台入口只创建一次获准WSL子进程并等待，不运行keep-alive或新常驻服务。Linux入口在同一进程完成fresh检查、六条原准备命令、最终快照和资格认领，再以os.execve替换为Guard。PID/start_ticks与受控fd共同跨交接，切换发生在同一实例中。

```mermaid
flowchart TD
    W[Windows 单次前台调用] --> L[Linux 受信入口 PID p]
    L --> V[当前字节与当前 boot 动态核验]
    V --> P[冻结准备与最终复查]
    P --> C[一次持久认领与 sealed memfd]
    C --> E[exec Guard 同一 PID p]
    E --> R[Root与子scheduler复查]
    R --> S[实际服务确认后登记启动]
    S --> Q[C00至C08 / C09H34 / RootIPC56 / BC40]
    Q --> H[真实C09 ACK和waitpid]
    H --> U[同一Root进程内部一次resume]
    U --> F[C10至C12 / S34 / 门17 / 资格后F1与F4]
    F --> Z[关闭 回收 父最终封存]
    V -->|失效| X[拒绝与保存原始证据]
    C -->|boot或身份改变| X
    R -->|无效| X
```

前置进程exec后转为原Root父协调器，常驻进程增量0、systemd服务增量0。原scheduler、external-stop及RootIPC顺序探针TCB保持；Linux入口设AS1GiB，预检单独120秒上限，初始启动ticket最长10秒。运行T0仍由原Guard在预检后创建，总窗1800/校准300保持；预检TCB开销在T0之前单列，不能用来延长已开始的窗口。

单次原生入口：

```text
{' '.join(lock['windows_single_call'])}
```

Root实际exec argv仍为冻结Guard.launch_command，两个环境fd键由受信入口传递；所有直接Guard启动缺少有效凭据将拒绝。C09后不再发起另一次WSL命令；旧resume argv仅保存参考，不构成启动路径。

NoFalseStart分界：请求成功/exec接入只记录REQUESTED/ENTRY；{point('boot_continuity.py','service_confirmed')}在ticket放行前观测实际C00/C10单位active、稳定MainPID、UID/GID/补充组、CapEff/NoNewPrivs、AS与cgroup匹配后才发布BOOT_START/BOOT_RESUME。该记录表示真实观测，资源资格仍需原完整链。

无法宣称全平台事务原子性。final check到exec之间的强制重启会杀死Owner并销毁cap；systemd成功但没有实际服务则缺少启动证明；同boot的特权文件/单位变更仍有检查间隙，依赖原可信部署/无并发特权更新及服务内重查。Windows记录器丢失不等价于Linux Owner必定退出；原独立停止源和deadline继续负责运行安全。严格实时延迟、掉电持久性和实际fd继承均待动态验证。
''')

properties=[
 ['BC-1 SameBoot','chain boot相等、ticket/Owner/current boot相等，继承cap属于原实例',point('boot_continuity.py','eligibility'),'P.after_first/during_prepare/after_final/during_exec/old_receipt，M.epoch/snapshot'],
 ['BC-2 FreshRuntime','当前source/runtime/UID/cgroup/manager fresh；Guard接入再次读取',point('boot_continuity.py','runtime_snapshot'),'P.resources/identity/artifact_drift；M.resources/cache；真实入口'],
 ['BC-3 NoStaleAuthorization','新boot/新Owner/错binding/无cap/旧窗口拒绝',point('boot_continuity.py','ticket_policy'),'P.bad_batch/bad_lock/old_receipt；M.binding/epoch/snapshot'],
 ['BC-4 SingleActivation','O_EXCL claim＋锁＋持久entered位；初始一次/同窗resume一次',point('boot_continuity.py','guard_admission'),'P.duplicate；M.duplicate；实际同时启动/复用待测'],
 ['BC-5 FailClosed','不确定/缺证/STOP/CLOSED/时间失效异常退出；无fallback放行',point('boot_continuity.py','prepare_activation'),'P.stop/closed；M.closed/resources/cache'],
 ['BC-6 NoBudgetReset','既存Root/state/counter拒绝；24预算函数保持；恢复原window核验',point('boot_continuity.py','entry'),'P.old_window；M.budget；真实C09恢复'],
 ['BC-7 NoFalseStart','请求与实际服务分开，实际身份/active/资源检查后发布证据',point('boot_continuity.py','service_confirmed'),'P.request_only/launcher_exit；M.request；真实C00/C10'],
 ['BC-8 TCBBoundary','单会话Root Owner/封印fd；Windows记录器、既有TCB责任显式',point('boot_continuity.py','read_capability'),'P.orchestrator_exit/identity；M.identity/snapshot；实际故障责任待测']]
report('BOOT_CONTINUITY_SAFETY_PROPERTIES.md','BC-1至BC-8安全性质与未决证明责任',f'''
{table(['性质','实现谓词','检查点','未来验证'],properties)}

证明边界：同一存活Linux进程的exec交接、不可变cap与持久认领提供可检查的代次和一次性边界；系统重启无法把原进程/原fd带入新实例。该论证依赖可信内核/Root/部署及文档接口，当前没有原生行为测试。跨systemd、磁盘和调度的全局原子事务及严格实时性继续CONDITIONAL/UNRESOLVED。

BC40只证明模拟重启模型中的检测责任；模型会改变epoch、杀死旧actor、丢弃cap/manager活动状态并保留持久账与闭合，不能据此写出本机物理重启PASS。真实启动、服务、原C09及资源资格另取当前证据，接口或阶段缺失均阻断。

[启动凭据](BOOT_BOUND_AUTHORIZATION.md)、[回归计划](BOOT_CONTINUITY_REGRESSION_PLAN.md)、[静态检查](STATIC_VERIFICATION_RESULTS.md)。
''')

report('BOOT_CONTINUITY_FIX_IMPLEMENTATION.md','实际修复范围与RootIPC兼容性',f'''
最终host工作区`D:\\毕业设计\\DCL-R6-isolated-verification\\bc01`；未来Linux位置`/var/lib/dcl-r6/bc01`。当前只有host文件，Linux部署/查询0，batch07目录创建0。

修改原guard.py的启动接入/授权/新证据门：Launcher进入BC.entry，Root/子scheduler接入复核；实际C00/C10服务确认；原RootIPC56后增加BC40；FORMAL业务导入前增加BC.formal_gate；父seal前保存启动闭合证据。原预算/原资源门算法24个函数AST保持。

root_ipc.py与c09_handoff.py只把batch06命名绑定改为batch07；权限、RPC、持久ACK、fresh-read、waitpid、CLOSED吸收和一次分类AST在命名归一后全等。14份其余程序逐字节保持，含五业务、预算核心、原探针、runner、C09H/RootIPC驱动与独立检查器。原56/34/34/17输入仅改未来batch命名。

新增boot_continuity.py、boot_continuity_regression.py、boot_continuity_oracle.py及host/windows_entry.py。Root boot私有文件位于原root_private下新子目录，仍用原RootIPC目录fd/ACL检查；新公共启动/BC资格收据0:989/0640，由新固定目标发布器写入。原RootIPC允许目标列表不扩大。

新source-only封装移除运行目录旧pyc：原17份3.12缓存保存在原件44项，不拿旧文件名/旧代码缓存充当新程序编译结果。新包20份Linux源码、1份Windows入口、11输入共32项。当前host解析3.12文法与host编译21份，无target import/body；实际3.12的compile(source)编排已实现，当前运行0。

新BC40在当前共同C09H ticket内计费，完成路径481、硬限512；C09H2245＋RootIPC505＋BC481=3231≤5000，完整校准硬界62034保持。新TCB无常驻增量，预检时间/AS及同进程恢复是需要新许可明确接受的差异。

[完整源码diff](evidence/SOURCE_COMPLETE.diff)、[完整输入diff](evidence/INPUT_COMPLETE.diff)、[原r4全部44项](evidence/original)、[静态检查](evidence/STATIC_CHECKS.json)、[最终锁](SOURCE_AND_INPUT_LOCK.md)。r1/r2/r3中间候选各32项及检查单独保留，最终申请仅绑定r4。
''')

reg_rows=[[j['case_id'],' → '.join(j['events']),j['variant'],j['expected_violation'] or j['expected_last'],','.join(j['allowed_violations']) or '∅','UNRUN'] for j in cfg['jobs']]
report('BOOT_CONTINUITY_REGRESSION_PLAN.md','启动连续性40项正反夹具与独立oracle',f'''
40项＝20个基础场景＋10个变异对照＋10个mutant；当前实际执行0。{point('boot_continuity_regression.py','Kernel')}为显式模拟内核：reboot递增epoch，旧进程死亡、cap/manager活动状态失效；持久静态对象、旧预算和CLOSED保留。新actor必须fresh检查，模拟PID/start_ticks复用仍受boot约束。身份/资源/静态漂移包含具体UID/GID/cgroup、tasks_max和对象摘要值。

每job初态、完整事件、当前模拟状态来源、预期末态/激活数、允许违规集及必须保存证据在[冻结合同](evidence/boot_contract.json)。生产eligibility/ticket_policy/service_policy被fixture实际调用；指定错误行为仅存在合成subject，不改真实boot、预算或系统对象。错误ticket通过“重新构造带错误绑定的对象”注入，未声称改写真实sealed fd。

{table(['case','事件序列','variant','期望末态或违规','允许违规集','actual'],reg_rows)}

独立oracle不导入Guard、生产gate、模拟subject或业务后继；从冻结事件重建epoch/存活、manager代次、权限、资源和静态对象真值，再核实际决策、认领数、service事实和原账单调。原始记录Root:Root/0600，包含当前真实运行binding/actor/时钟/访问占用，模拟字段另标SIMULATED_RESTART/1。物理WSL重启、实际exec fd继承及真实服务启动仍是独立动态责任。

每job最多10个事件，保守预付11次（语义步及即时oracle），另付整套Root重算1次；entry1＋40×12=481，硬限512，不退款。与C09H/RootIPC同一5000硬额、同一T0/300秒校准窗，额外进程0。未命中变异、缺原件、额外违规、错误绑定、超限或意外错误均阻断；首个失败即保存并停止。

需要真实平台重新启动诊断时必须另取许可。本轮这些测试未运行；输入中的“reboot”仅定义模型状态变换，绝不发出wsl shutdown/terminate。
''')

impact=[
 ['RootIPC权限/交接','2份文件仅批名归一；安全AST等同，56输入语义保持','UNRUN'],
 ['C09H34/真实C09','原34驱动/oracle不变；持久ACK、父waitpid、fresh-read与一次分类保留；恢复改为同一Root内部一次调用','UNRUN/NOT_EXERCISED'],
 ['C00–C12','原探针字节保持；仅实际C00/C10票据放行前增加启动证明','UNRUN'],
 ['S34/门17/预算','原核心/驱动/检查器字节保持，24相关函数AST保持，原判据不放宽','UNRUN'],
 ['F1/F4','五业务与正式输入字节保持，原FORMAL门前增加Boot证据门','UNRUN_RESOURCE_GATE'],
 ['目标CPython/WSL','沿用原期望合同；当前只做host静态语法，不执行native compiler或诊断','UNVERIFIED_CURRENT_PLATFORM']]
report('STATIC_VERIFICATION_RESULTS.md','静态语法、控制流和不变量检查',f'''
21份程序通过host compile及Python3.12语法文法解析：20份Linux源码＋1份Windows入口。仅创建代码对象/AST，没有import目标或执行函数、模拟、生命周期测试。当前host解释器版本记录在[STATIC_CHECKS](evidence/STATIC_CHECKS.json)；实际目标CPython3.12编译为UNRUN_PLATFORM_QUERY_NOT_AUTHORIZED。

14份既有源码字节相同；guard中24预算/资格函数AST保持；RootIPC与C09在批名归一后安全AST一致。原四份business_plan/child/runtime_critical/runtime_tree输入字节一致；RootIPC56、C09H34、S34与门17输入只改batch命名。新40job唯一、最大事件数10、10mutant、计费481与共同3231公式逐字面核对。

{table(['范围','静态发现','动态'],impact)}

检查到的关键顺序：最终dynamic→持久认领→封印cap→same-PID exec→Root复查→子接入→原T0初始化；实际服务active/身份确认→票据发布；C09验证返回23→消耗resume位→原resume_admission；BC正反全部raw接受→Root BC资格→FORMAL前重新检查。完整全平台原子性、当前memfd接口/封印/继承、调度与掉电仍依赖未来原生证据。

历史1120研究文件、旧工作区和原包逐字节/逐流核对见[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)。本轮新WSL调用0、全局WSL配置修改0、服务启动0、T0/账初始化0、目标测试0、依赖安装0。原batch06的PREFLIGHT_FAILED、19命令/三boot与157条目包保持。
''')

hashrows=[[name,sha(W/'inputs'/name)] for name in ['static_manifest.json','execution_lock.json','boot_contract.json','root_ipc_contract.json','c09_contract.json','safety_contract.json']]
report('SOURCE_AND_INPUT_LOCK.md','BootContinuity-static-1/r4源码和执行锁',f'''
唯一host静态目录`D:\\毕业设计\\DCL-R6-isolated-verification\\bc01`；未来Linux静态目录`/var/lib/dcl-r6/bc01`。当前部署Linux0，新平台查询0。拟用batch07目录只作为冻结参数，本轮创建0。

{table(['核心对象','SHA-256'],hashrows)}

32项＝Linux源码20＋Windows入口1＋输入11，无运行pyc。全表见[STATIC_WORKSPACE_LOCK](evidence/STATIC_WORKSPACE_LOCK.json)；目标Linux目录是future_linux引用，不能据此宣称已存在/已核验。

{table(['相对路径','SHA-256'],[[r['relative'],r['sha256']] for r in frozen['files']])}

16组原payload argv、34个S worker模板、六准备命令和17-unit journal仅做batch07/source路径适配；新Windows单调用、exec环境fd、内部一次resume和Boot40顺序在[execution_lock](evidence/execution_lock.json)。直接Guard/独立resume不再是合法激活入口；旧resume argv保留参考。

当前授权只覆盖host静态修复。下一动态申请需要接受Root预检120秒/AS1GiB、初始10秒启动ticket、封印fd/一次认领、同进程C09恢复、source-only原生语法核验以及40项模拟回归。任何源/输入/命令改变都须新冻结与匹配授权。
''')

auth={
 'schema':'BATCH07_AUTHORIZATION_TEMPLATE_STATIC_ONLY','authorization_status':'NOT_GRANTED',
 'batch_id':'batch07','scope':'CALIBRATE_S1S9_THEN_F1_F4','profile':'CPY312-UBU24/1','limits':[1000000,1800,1740,1073741824,4],
 'source_version':'BootContinuity-static-1','freeze_revision':'r4','source_mode':'SOURCE_ONLY/1',
 'static_manifest_sha256':sha(W/'inputs/static_manifest.json'),'execution_lock_sha256':sha(W/'inputs/execution_lock.json'),
 'boot_contract_sha256':sha(W/'inputs/boot_contract.json'),'boot_continuity_profile':'BC-SINGLE-SESSION/1',
 'root_ipc_contract_sha256':sha(W/'inputs/root_ipc_contract.json'),'root_ipc_profile':'ROOT-IPC/1',
 'c09_contract_sha256':sha(W/'inputs/c09_contract.json'),'safety_contract_sha256':sha(W/'inputs/safety_contract.json'),
 'handoff_profile':'C09-DURABLE-RPC/1','test_mode':'RANGE_ONLY/1',
 'special_mapping_scope':'ORDINARY_AS_ACCOUNTED;KERNEL_SPECIALS_SEPARATELY_REVIEWED',
 'authorization_text_sha256':None,'Root_coordinator_explicitly_approved':None,'RootIPC_helpers_explicitly_approved':None,
 'SingleSession_exec_explicitly_approved':None,'SameProcess_C09_resume_explicitly_approved':None}
dump(E/'BATCH07_AUTHORIZATION_TEMPLATE.json',auth)
report('BATCH07_EXECUTION_REQUEST.md','batch07独立部署、平台核验与动态执行申请',f'''
本文件为可审阅申请，当前许可范围仍是静态工作。绑定BootContinuity-static-1/r4及下列实际hash；batch06保持原预检失败，无原窗口可恢复。

{table(['锁','SHA-256'],hashrows)}

请求范围：部署bc01源模式包（31个Linux文件，Root0拥有、目录0755/文件0644，禁止残留pyc）、当前平台只读接口/权限核验、单会话受信Root入口及memfd/exec继承验证、同进程C09一次恢复、新40项模拟回归、全部原C/C09H/RootIPC/S/17门链和资源资格后自动F1→F4。原RootIPC顺序探针最多1个、UID999/GID989及现有65534身份保持原授权模型。

本轮未检查当前WSL环境。未来预检fresh核Python3.12.3/e50d…150f、原32关键文件与1224树、kernel6.18.33.2、systemd255.4、cgroup2/page4096、当前UID/GID/ACL/临时对象/残留、boot与Owner。原生3.12语法编译在入口内只生成内存代码对象，不运行模型，不修改冻结源或产生pyc。任何漂移、缺失接口、封印/继承错误或不确定状态即停止。

Windows唯一入口：

```text
python -X utf8 D:\\毕业设计\\DCL-R6-isolated-verification\\bc01\\host\\windows_entry.py --activate
```

其内部唯一WSL argv：

```text
{' '.join(lock['windows_single_call'])}
```

授权原文/回执在未来host batch07研究目录准备，原始路径由execution_lock固定；[模板](evidence/BATCH07_AUTHORIZATION_TEMPLATE.json)批准位及原文hash当前为空，无法作为执行许可。Linux入口完成实际六条冻结准备和授权安装；本轮不会提前创建batch07或安装其单位。新boot私有子目录由入口按Root:Root/0700受控创建。

TCB/资源差异：无新增常驻进程或服务，Linux预检入口exec后就是原Root父协调器；预检在T0之前单列最长120秒、入口设置AS1GiB，初始激活ticket最长10秒。C09验证后在同一个Root进程内调用一次原resume路径，不再调用第二次WSL。原预检/当前实例首映像、可信部署/loader、存储、调度条件保留；当前尚无硬实时认证。

运行合同保持总访问1000000、T0后1800秒、T0+1740停止、校准300秒/100000、payload AS1GiB/父slice4tasks、AS4-PAYLOAD/1条件。Boot40预付/Root重算完成481、硬限512；C09H2245＋RootIPC505＋BC481=3231，三阶段共同硬限5000，校准硬界62034保持。预检TCB不构成运行窗扩展，绝不重置已存在T0或预算。

执行关系：部署资格→单次WSL当前boot预检/准备/exec→Root接入→C00–C08→C09H34/Root审查→RootIPC56→BC40/独立审查→真实C09持久ACK/waitpid/fresh-read/一次分类→同进程同窗一次恢复→C10–C12→S34→17门→RESOURCE_GATE_PASS→F1→F4→停止与父最终seal。所有前置缺证/FAIL/UNRUN/变异未检出阻断正式业务导入。

首次关键失败保存当前boot/PID/fd/认领/单位/预算/时钟及完整双流，按原停止/回收合同关闭已开始的窗口；未开始则保留准备与失败记录。禁止自动重试、新窗口、改锁/权限/阈值续跑、复用CLOSED或自动创建下一批。模拟重启测试不发出真实shutdown/terminate；如要定位宿主触发者，需另列只读诊断或实际生命周期测试授权。

F2/F3、Casdoor、T1–T4、真实账户/凭据、依赖安装、WSL全局配置、无关单位、误副本处置和外发不在申请内。D1/强G原条件、严格分离0、IMPLEMENTATION_GATE=CLOSED保持。
''')

report('FINAL_DECISION.md','BootContinuity-Fix最终静态裁决',f'''
**BootContinuity-static-1/r4 已在host完成有限静态修复与冻结；当前WSL/Launcher/服务/测试执行均为0，batch07实体创建0。**

{table(['验收门','裁决','实际范围'],[
 ['BC-1 生命周期分析','PASS_STATIC','19原命令/三boot/109.295102秒完整还原；未知Linux PID与准备各步boot明确保留；原因UNRESOLVED'],
 ['BC-2 证据分层','PASS_STATIC','A层条件复用陈述与当前字节核验、B层fresh身份/实例资格、显式失效规则实现'],
 ['BC-3 启动安全修复','CONDITIONAL_PASS','单会话exec、sealed fd/一次认领、服务内复核和同进程恢复已接线；原生行为、竞态和全平台原子性待证'],
 ['BC-4 回归与授权','PASS_STATIC','40夹具/10变异、21程序host语法与3.12文法、32项锁/diff及batch07申请完整；动态UNRUN']])}

根因边界为BOOT_CHANGE_CAUSE_UNRESOLVED：多次独立WSL调用跨boot成立，systemd服务不足以维持实例是官方一般性说明；本机具体空闲/外部/宿主触发者尚缺证据。本轮不进行平台诊断，也不把假设写成已证原因。

源码修改guard启动接入，RootIPC与C09两份文件仅批次命名；14既有程序字节和24预算/资格函数AST保持。新增3份Linux模块、1份Windows入口，source-only共32项。host语法/3.12文法21份通过；目标CPython3.12原生编译仍UNRUN。旧r4的44项及17缓存、batch06原件和1120历史研究文件/旧工作区/误副本47hash保持。

Boot40模拟epoch变化会销毁旧进程/FD/manager活动状态并保留持久账；当前执行0，未取得任何BC动态PASS。完成路径481，与既有合计3231≤5000、完整校准硬额62034保持；额外预检TCB120秒/AS1GiB与初始10秒ticket是明确新许可差异，无常驻进程增量。实际停止/启动延迟和校准300秒可完成性仍未测量。

保留条件：可信Root/内核/部署、无并发特权更新、存储屏障与调度；全systemd/磁盘/进程事务原子性、当前memfd/exec接口与物理重启行为继续待证。服务请求与真实服务证据分开，资源门前置完整，新的启动票据无法绕过原C09/C/S/负向门。

RESOURCE_GATE_PASS=NOT_OBTAINED，F1/F4=UNRUN_RESOURCE_GATE，PASS_BOUNDED授予0。D1-PBFT-SEAL/1.1原条件、强G覆盖、严格分离实例0及IMPLEMENTATION_GATE=CLOSED保持。本轮基础设施修复采用通用方法，对最强通用基线预测差距0，没有协议原创性升级。

[batch07申请](BATCH07_EXECUTION_REQUEST.md)、[实际代码和完整diff](BOOT_CONTINUITY_FIX_IMPLEMENTATION.md)、[安全性质](BOOT_CONTINUITY_SAFETY_PROPERTIES.md)、[源锁](SOURCE_AND_INPUT_LOCK.md)、[证据索引](EVIDENCE_INDEX.md)、[交付核对](evidence/DELIVERY_CHECK.json)。
''')

required=['BOOT_CHANGE_TIMELINE.md','WSL_LIFECYCLE_HYPOTHESES.md','PREFLIGHT_EVIDENCE_LAYERS.md',
 'BOOT_BOUND_AUTHORIZATION.md','SINGLE_SESSION_LAUNCH_DESIGN.md','BOOT_CONTINUITY_SAFETY_PROPERTIES.md',
 'BOOT_CONTINUITY_FIX_IMPLEMENTATION.md','BOOT_CONTINUITY_REGRESSION_PLAN.md','STATIC_VERIFICATION_RESULTS.md',
 'SOURCE_AND_INPUT_LOCK.md','BATCH07_EXECUTION_REQUEST.md','FINAL_DECISION.md']
dump(P/'SOURCE_INDEX.json',{'schema':'BC-source-index/1','version':'BootContinuity-static-1/r4','workspace':str(W),
 'future_Linux':'/var/lib/dcl-r6/bc01','deployed':False,'files':frozen['files'],'current_platform_queries':0,
 'native_compile':'UNRUN','host_grammar_files':21,'target_tests':0,'batch07_created_this_task':False,
 'hashes':dict(hashrows),'source_changes':static['modified_source_files'],'unchanged':static['unchanged_source_bytes'],
 'security_AST':static['budget_and_gate_AST_unchanged'],'old_boot_observations':boots})
dump(E/'SOURCE_DIFF_INDEX.json',{'version':'BootContinuity-static-1/r4','source_diff_sha256':sha(E/'SOURCE_COMPLETE.diff'),
 'input_diff_sha256':sha(E/'INPUT_COMPLETE.diff'),'original':'original/','host_final_files':32,
 'semantic_unchanged':14,'namespace_only':['root_ipc.py','c09_handoff.py'],'startup_changes':['guard.py'],
 'new':['src/boot_continuity.py','src/boot_continuity_regression.py','src/boot_continuity_oracle.py','host/windows_entry.py'],
 'cache_policy':'source-only; original17 pyc archived, new native compile deferred'})
report('EVIDENCE_INDEX.md','BootContinuity研究证据索引',f'''
{table(['材料','范围'],[[link(P/name),name[:-3]] for name in required])}

[机器事件时间线](evidence/BOOT_TIMELINE.json)、[静态检查](evidence/STATIC_CHECKS.json)、[最终32项锁](evidence/STATIC_WORKSPACE_LOCK.json)、[Source索引](SOURCE_INDEX.json)、[完整source diff](evidence/SOURCE_COMPLETE.diff)、[完整input diff](evidence/INPUT_COMPLETE.diff)、[diff索引](evidence/SOURCE_DIFF_INDEX.json)。

[原r4全部44项](evidence/original)、[1120历史/旧账/旧包保护](evidence/HISTORY_PROTECTION_CHECK.json)、[专项请求](evidence/TASK_REQUEST.txt)、[范围与分离门](SEPARATION_AND_SCOPE.md)、[公开来源元数据](evidence/PRIMARY_SOURCES.json)。batch06原始19组argv/双流及三boot均通过原始索引访问；本轮没有新native命令日志。

原batch06与RootIPC/B05包逐流校验无差异；本次[BOOTCONTINUITY_STATIC_REVIEW.zip](BOOTCONTINUITY_STATIC_REVIEW.zip)含研究材料、候选32项、四导航及batch06原包。r1/r2/r3中间host候选与检查保留，最终只申请r4。目录/部署/接口的当前Linux属性未查询，future_linux路径不证明已部署。

[OUTPUT_MANIFEST](OUTPUT_MANIFEST.json)列逐项字节/SHA/archive_path；[DELIVERY_CHECK](evidence/DELIVERY_CHECK.json)分列manifest和ZIP摘要。排除manifest自身、最终ZIP、delivery避免自引用；行政PASS_ADMIN_ONLY仅证明所列字节/结构/链接，不产生动态资源或协议结论。
''')
report('README.md','DCL-R6-BootContinuity-Fix','''
host静态版本BootContinuity-static-1/r4：单次WSL入口、同进程exec/恢复、封印fd及持久一次认领、新40项模拟回归已实现。12份报告、32项源码/输入和新执行申请冻结。

[最终裁决](FINAL_DECISION.md) · [batch07申请](BATCH07_EXECUTION_REQUEST.md) · [源与输入锁](SOURCE_AND_INPUT_LOCK.md) · [证据索引](EVIDENCE_INDEX.md) · [审阅包](BOOTCONTINUITY_STATIC_REVIEW.zip)

新WSL查询0、部署0、Launcher/服务/测试0、batch07创建0。RESOURCE_GATE_PASS未取得；IMPLEMENTATION_GATE=CLOSED；严格分离0。
''')

intro='''# DCL-R6-BootContinuity-Fix 最新静态裁决（2026-11-11）

BootContinuity-static-1/r4已在host冻结：单次WSL受信入口、same-PID exec与封印fd/持久一次认领、Root/服务内fresh复查、同一Root进程C09一次恢复；原14份程序字节与24预算/资格函数AST保持。新增40模拟回归/10变异，21程序host语法及3.12文法通过，32项包无旧pyc。

BC-1/BC-2/BC-4=PASS_STATIC；BC-3=CONDITIONAL_PASS。目标3.12原生编译、当前WSL/接口、真实启动及测试全部UNRUN；本轮新WSL调用/部署/服务/T0/账/batch07创建均为0。新许可须明确source-only、预检TCB120秒/AS1GiB、初始10秒ticket与同进程恢复；BC481与既有合计3231≤5000，运行1800/校准300及原硬额保持。

batch06的三boot/109.295102秒/PREFLIGHT_FAILED与目标启动0保持；具体触发源BOOT_CHANGE_CAUSE_UNRESOLVED。D1-PBFT-SEAL/1.1原条件、强G覆盖、严格分离0、IMPLEMENTATION_GATE=CLOSED保持。

[最终裁决](DCL-R6-BootContinuity-Fix/FINAL_DECISION.md) · [batch07申请](DCL-R6-BootContinuity-Fix/BATCH07_EXECUTION_REQUEST.md) · [证据索引](DCL-R6-BootContinuity-Fix/EVIDENCE_INDEX.md)

以下完整保留本轮之前历史导航；旧阶段许可/下一步/未创建文字按各自记录时点理解。

---

'''
for r in base['navigation']:(ROOT/r['original']).write_bytes(intro.encode()+Path(r['snapshot']).read_bytes())

planned={P/'OUTPUT_MANIFEST.json',P/'BOOTCONTINUITY_STATIC_REVIEW.zip',E/'DELIVERY_CHECK.json'}
count=0;errors=[]
for p,content in [(q,q.read_text(encoding='utf-8')) for q in P.glob('*.md')]+[(ROOT/'README.md',intro)]:
    assert '不是' not in content
    for dest in re.findall(r'\]\(([^)]+)\)',content):
        dest=dest.strip('<>')
        if '://' in dest or dest.startswith('#'):continue
        count+=1;q=(p.parent/dest.split('#')[0]).resolve()
        if not q.exists() and q not in planned:errors.append({'file':str(p),'target':dest})
assert not errors,errors
for name in required:assert (P/name).is_file()
parsed=0
for root in [P,W]:
    for q in root.rglob('*.json'):
        if q.name not in ['OUTPUT_MANIFEST.json','DELIVERY_CHECK.json']:load(q);parsed+=1
dump(E/'REPORTING_RECEIPT.json',{'schema':'BC-offline-reporting/1','new_local_links_checked':count,'link_errors':errors,
 'JSON_parsed':parsed,'new_native_commands':0,'target_imports_or_execution':0,'script':str(Path(__file__).resolve()),
 'scope':'Host-only metadata/source/AST/byte/ZIP review; no current Linux platform assertion'})

exclude={P/'OUTPUT_MANIFEST.json',P/'BOOTCONTINUITY_STATIC_REVIEW.zip',E/'DELIVERY_CHECK.json'}
rows=[]
for root,prefix in [(P,'research'),(W,'FROZEN_BOOTCONTINUITY')]:
    for q in sorted(root.rglob('*')):
        if q.is_file() and q not in exclude:rows.append({'host':str(q),'scope':prefix,'archive_path':prefix+'/'+q.relative_to(root).as_posix(),'bytes':q.stat().st_size,'sha256':sha(q)})
for r in base['navigation']:
    q=ROOT/r['original'];rows.append({'host':str(q),'scope':'navigation','archive_path':'navigation/'+q.name,'bytes':q.stat().st_size,'sha256':sha(q)})
q=B06/'BATCH06_EVIDENCE.zip';rows.append({'host':str(q),'scope':'historical','archive_path':'historical/BATCH06_EVIDENCE.zip','bytes':q.stat().st_size,'sha256':sha(q)})
manifest={'schema':'BC-output-manifest/1','version':'BootContinuity-static-1/r4','files':rows,
 'scope_counts':dict(Counter(r['scope'] for r in rows)),'exclusions':['OUTPUT_MANIFEST.json','BOOTCONTINUITY_STATIC_REVIEW.zip','evidence/DELIVERY_CHECK.json'],
 'target_runtime_qualification':'UNRUN','deployed_Linux':False}
dump(P/'OUTPUT_MANIFEST.json',manifest);archive=P/'BOOTCONTINUITY_STATIC_REVIEW.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for row in rows:z.write(row['host'],row['archive_path'])
    z.write(P/'OUTPUT_MANIFEST.json','OUTPUT_MANIFEST.json')
with zipfile.ZipFile(archive) as z:
    assert len(set(z.namelist()))==len(rows)+1
    for row in rows:
        b=z.read(row['archive_path']);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'] and sha(row['host'])==row['sha256']
    assert z.read('OUTPUT_MANIFEST.json')==(P/'OUTPUT_MANIFEST.json').read_bytes()
delivery={'schema':'BC-delivery/1','status':'PASS_ADMIN_ONLY','version':'BootContinuity-static-1/r4',
 'gates':{'BC-1':'PASS_STATIC','BC-2':'PASS_STATIC','BC-3':'CONDITIONAL_PASS','BC-4':'PASS_STATIC'},
 'required_reports':12,'candidate_files':32,'host_grammar_files':21,'native_CPython_compile':'UNRUN',
 'native_queries':0,'new_WSL_calls':0,'target_module_imports':0,'tests_executed':0,'batch07_created_this_task':False,
 'deployed_Linux':False,'source_bytes_preserved':14,'budget_gate_AST_preserved':24,'new_synthetic_jobs':40,'mutants':10,
 'completed_visit_static_bound':481,'combined_completed_bound':3231,'joint_cap':5000,'full_calibration_hard':62034,
 'history_mismatches':0,'history_research_files':1120,'links_checked':count,'link_errors':[],'JSON_parsed':parsed,
 'manifest_rows':len(rows),'ZIP_entries':len(rows)+1,'ZIP_stream_mismatches':[],
 'manifest_sha256':sha(P/'OUTPUT_MANIFEST.json'),'ZIP_sha256':sha(archive),'ZIP_bytes':archive.stat().st_size,
 'source_manifest_sha256':sha(W/'inputs/static_manifest.json'),'execution_lock_sha256':sha(W/'inputs/execution_lock.json'),
 'boot_contract_sha256':sha(W/'inputs/boot_contract.json'),'BOOT_CHANGE_CAUSE':'UNRESOLVED',
 'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
 'strict_separation_instances':0,'IMPLEMENTATION_GATE':'CLOSED',
 'scope':'Offline syntax/AST/hash/schema/new links/ZIP streams only; native guarantees conditional',
 'sealed_utc':datetime.now(timezone.utc).isoformat(),'self_excluded_from_manifest_and_zip':True}
dump(E/'DELIVERY_CHECK.json',delivery)
print(json.dumps(delivery,ensure_ascii=False,indent=2))
