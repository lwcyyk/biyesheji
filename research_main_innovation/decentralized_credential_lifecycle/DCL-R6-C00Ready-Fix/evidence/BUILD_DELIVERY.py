"""Offline evidence, reports and static review sealing. No target import or lifecycle action."""
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
WORK=Path(r'D:\毕业设计\DCL-R6-isolated-verification')
W=WORK/'cr01'
B=ROOT/'DCL-R6-batch07'
N=WORK/'batch07/native_snapshot'
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
    (P/name).write_text('# '+title+'\n\nMaterial Passport：C00Ready-static-1/r2；host有限静态修复；2026-11-11；新增WSL/服务/目标测试0。\n\n'+text.strip()+'\n',encoding='utf-8')
def point(file,name):
    n=next(n for n in ast.walk(ast.parse((W/'src'/file).read_text())) if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
    return link(W/'src'/file,file+':'+str(n.lineno)+' '+name)

base=load(E/'BASELINE_LOCK.json');static=load(E/'STATIC_CHECKS.json');frozen=load(E/'STATIC_WORKSPACE_LOCK.json')
audit=load(E/'EIGHT_FIELD_HISTORICAL_AUDIT.json');timeline=load(E/'BATCH07_FAILURE_TIMELINE.json')
cfg=load(W/'inputs/readiness_contract.json');lock=load(W/'inputs/execution_lock.json')
assert frozen['version']=='C00Ready-static-1/r2' and len(cfg['jobs'])==64
history=[]
def verify(name,rows,path,key='sha256'):
    errors=[]
    for row in rows:
        p=path(row)
        if not p.is_file() or sha(p)!=row[key] or ('bytes'in row and p.stat().st_size!=row['bytes']):errors.append(str(p))
    history.append({'name':name,'count':len(rows),'mismatches':errors,'status':'PASS_ADMIN_ONLY' if not errors else 'FAIL'})
    assert not errors,(name,errors)
verify('All2034 historical R6 research files',base['history'],lambda r:ROOT/r['relative'])
verify('BootContinuity r4 canonical32',base['original_files'],lambda r:Path(base['original_workspace'])/r['relative'])
verify('C00Ready final36 host files',frozen['files'],lambda r:W/r['relative'])
for folder in ['DCL-R6-batch07','DCL-R6-batch06','DCL-R6-batch05','DCL-R6-batch04']:
    for filename in ['NATIVE_EXPORT_LOCK.json','FROZEN_SOURCE_EXPORT_LOCK.json']:
        x=load(ROOT/folder/'evidence'/filename);verify(folder+'/'+filename,x['files'],lambda r:Path(r['host']))
for folder in ['DCL-R6-RootIPC-Fix','DCL-R6-C09Fix','DCL-R6-GapClosure','DCL-R6-BudgetFix']:
    x=load(ROOT/folder/'evidence/STATIC_WORKSPACE_LOCK.json');directory=Path(x.get('host',str(WORK/'c09f01')))
    if folder=='DCL-R6-C09Fix':directory=WORK/'c09f01'
    verify(folder+' old source',x['files'],lambda r,directory=directory:directory/r['relative'])
x=load(ROOT/'DCL-R6-batch02-Perf/evidence/BASELINE_LOCK.json');verify('batch02 original51',x['immutable_B02_external'],lambda r:Path(r['path']))
x=load(ROOT/'DCL-R6-batch02-Perf/evidence/DUPLICATE_REGISTER.json');verify('Mispath47 read/hash only',x['files'],lambda r:Path(x['path'])/r['relative'],'duplicate_sha256')
for row in base['navigation']:assert sha(row['snapshot'])==row['sha256']
budgets={}
for folder,want in [('batch07',0),('batch05',37293),('batch04',37021),('batch02',32191)]:
    f=WORK/folder/'native_snapshot/out/visits.bin'
    if not f.exists():
        matches=list((WORK/folder).rglob('visits.bin'));assert len(matches)==1;f=matches[0]
    assert struct.unpack('<QQ',f.read_bytes()[8:])==(want,1000000);budgets[folder]=want
archives=[]
for folder,name in [('DCL-R6-batch07','BATCH07_EVIDENCE.zip'),('DCL-R6-BootContinuity-Fix','BOOTCONTINUITY_STATIC_REVIEW.zip'),('DCL-R6-batch06','BATCH06_EVIDENCE.zip')]:
    p=ROOT/folder/name
    with zipfile.ZipFile(p) as z:
        m=json.loads(z.read('OUTPUT_MANIFEST.json'))
        for row in m['files']:
            b=z.read(row['archive_path']);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
        archives.append({'path':str(p),'sha256':sha(p),'entries':len(z.namelist()),'stream_errors':[]})
dump(E/'HISTORY_PROTECTION_CHECK.json',{'schema':'CR-history/1','checks':history,'archives':archives,'budgets':budgets,
 'modified_history_files':0,'mispath_actions':'read/hash only','prior_policy_rejection':'blocked by policy retained','live_queries':0})

field_rows=[]
for r in audit['fields']:
    field_rows.append([r['check_id'],r['field'],r['source_line'],str(r['expected']),r['evidence_source'],'未保存；无直接MATCH/MISMATCH',r['rejection_expression']])
report('C00_EIGHT_FIELD_AUDIT.md','C00原八项条件与batch07逐字段裁决',f'''
**C00_FAILED_FIELD_UNRESOLVED**。八项从实际冻结service_confirmed的OR表达式提取，数量与源码逐项绑定，字段定义均有直接源码依据。

{table(['check_id','真实字段','原源码行','expected','原读取来源','batch07 observed/裁决','原拒绝表达式'],field_rows)}

八项运行时实际值、读取时刻与C00 MainPID/starttime都未持久化；原检查发生于Root scheduler，但Root PID886不代表C00 MainPID。OR具有短路语义，不能推断每个后续子表达式都曾完成计算。原函数确实取得unit_show与/proc/status对象，当前只剩聚合拒绝和控制流见证。

LimitAS/LimitASSoft来自manager属性，分别指冻结配置硬/软值1GiB；原第八项读取manager.ControlGroup路径。MainPID、ActiveState/SubState、Type、父slice TasksMax、实际/proc/limits和实际/proc/cgroup在新版本中另列为明确标识的辅助门，历史八项定义保持。

历史间接证据：冻结argv请求User/Group与AS，父kernel快照pids.max4/memory.max4GiB，journal为Starting-only；这些不能证明八项中某项匹配或失配。事后不同boot的not-found/default属性全部排除，禁止把LimitAS=infinity填入observed。

[机器逐字段审计](evidence/EIGHT_FIELD_HISTORICAL_AUDIT.json)、[原源码](evidence/original/src/boot_continuity.py)、[batch07原始失败](../DCL-R6-batch07/BATCH07_COUNTEREXAMPLES.md)。
''')

jrows=[[r['unit'],r['mono_us'],r['message']] for r in timeline['journal']]
report('C00_FAILURE_TIMELINE.md','batch07 C00执行时序与时钟边界',f'''
真实顺序从单会话bootstrap开始：预检→sealed claim→同进程exec进入Guard→Root消费认领→fork scheduler→T0/初始账→systemd外部stop→C00 start请求→manager MainPID轮询→八项聚合复核拒绝→CLOSED/组空/父waitpid/原生seal。systemd为Root创建C00目标进程，Guard未先作为C00服务启动；这些角色应分别记录。

{table(['journal单位','MONOTONIC µs','实际消息'],jrows)}

BC原34条事件、15条内部命令双流及7条run-boot journal均已从原始包复核。运行boot060a08fc…、Owner828/start7252跨exec一致，子scheduler886/start7372。T0=73.768774900；CLOSED=74.078122459，T0+0.309347559；组空74.095938066，T0+0.327163166；父waitpid raw32000/exit125。R0，C00票据、探针和BOOT_START没有生成。

C00 journal在同一MONOTONIC域的Starting→KILL相隔24.861ms。BC/账时钟为BOOTTIME，journal另有REALTIME，Host耗时为perf_counter；未校准的时钟不做跨域差值。八项读取无独立时间戳，具体失败点只能按控制流定位。

私有sealed原件不复制到本报告；审计只使用其摘要。当前未执行新的WSL、systemd查询或诊断。[机器时序](evidence/BATCH07_FAILURE_TIMELINE.json)、[batch07原包](../DCL-R6-batch07/BATCH07_EVIDENCE.zip)。
''')

report('C00_STARTUP_RACE_ANALYSIS.md','启动暂态、真实错误和循环等待审查',f'''
上游systemd v255分别提供MainPID登记和exec完成通知路径：service.c:2198–2205在SERVICE_START登记main pid；3197–3231处理exec-fd事件后进入下一状态。--no-block仅验证/排队。Type=exec的启动完成语义针对成功exec，不等价于应用业务初始化；notify的READY=1属于另一协议。

[v255 service源码](https://raw.githubusercontent.com/systemd/systemd/v255/src/core/service.c)、[v255 service文档](https://raw.githubusercontent.com/systemd/systemd/v255/man/systemd.service.xml)、[v255 systemd-run文档](https://raw.githubusercontent.com/systemd/systemd/v255/man/systemd-run.xml)。本轮查阅公开源码，实际Ubuntu255.4补丁/当前manager没有新查询；不据上游顺序认定batch07某个字段必定处于何值。

原Guard在--no-block后MainPID非零即离开轮询，随即把进程视作最终执行身份。这一屏障缺口已由源码确认。Starting-only消息和782336B的低charged peak支持启动临态假设，因果仍未完成；C00失败不能直接归为竞态、错误资源配置或新协议漏洞。

合法暂态只按manager exec阶段定义：获准start仍排队且无MainPID，或Type=exec处于activating的start/start-pre/start-post。原八项中的最终凭据在exec未确认前不取值，标记NOT_READY；一旦active/running，实际UID/GID、能力、AS或cgroup错误立即FAILED，绝不等待其“变正确”。配置中已确认错误的AS/TasksMax/类型等即使STARTING也失败。

循环依赖审查：controller启动后先等待Root ticket，再做kernel admission/探针。若Root等待依赖ticket的应用ready，双方会死锁。新屏障等待manager认可的exec状态及真实内核身份，不等待应用READY=1、C00.probe或业务访问。READY票据放行后原探针才运行。

[就绪合同](C00_SERVICE_READINESS_CONTRACT.md)、[采样一致性](C00_SNAPSHOT_CONSISTENCY.md)、[公开源码审计](evidence/PUBLIC_SOURCE_AUDIT.json)。
''')

state_rows=[
 ['STARTING','Type=exec；获准start有正Job且inactive/dead/PID0，或activating/start*；无硬配置错/停止/失效','八项最终凭据不取值或明确未就绪，票据关闭；同一窗口fresh采样'],
 ['READY','两侧active/running，8项实际值全MATCH，实际proc AS/CG与parent限额、身份/boot/version书签通过','生成native观察与私有lease，再复核并放行当前票据'],
 ['FAILED','稳定失配、读取错误/缺字段、错误unit/type、身份变化/退出、boot/锁漂移、STOP/CLOSED、超时/写证失败','保存已取得数据、具体失败ID及raw_error，立即关闭，不继续等待']]
report('C00_SERVICE_READINESS_CONTRACT.md','三态有界就绪合同与票据门',f'''
{table(['状态','条件','行为'],state_rows)}

{point('service_readiness.py','phase')}结合manager.Job和Type/ActiveState/SubState判定exec阶段；当前Job渲染按v255官方实现，使用--all确保空属性仍有明确记录。Job只在已由本流程请求启动、唯一批次单位、无并发特权干预的前提下指示排队，不能授权业务。

独立上界14秒来自原MainPID启动轮询上限，C00/C10从start请求前起共用该上界；有效until=min(start+14,T0+300,stop_at,deadline)。poll参数50ms、样本上限300，每行最多131072B；超过限额或未知状态即失败。取样/持久化成本都在既有窗口内，未追加300秒或新T0。阻塞I/O/调度总延迟保留原条件，不宣称硬实时。

只有原生OS collector可以产生Observation的私有mint，Lease还必须绑定case/unit/PID/starttime/boot/当前锁及pidfd。普通JSON或READY布尔标志无法构造有效lease。{point('service_readiness.py','require_lease')}、确认后的再次存活/期限检查及Root ticket摘要绑定组成放行链。

原八项数值完全保持；新增manager单位/类型/User/Group/Tasks/NoNewPrivileges和实际/proc AS/cgroup、parent pids/memory门仅加强证明。单位查询失败、属性缺失、活体UID/GID非法、资源确认错误、错cgroup和已发布终止均不等待。
''')

report('C00_FIELD_LEVEL_DIAGNOSTICS.md','逐字段诊断结构、来源与失败发布',f'''
{point('service_readiness.py','collect_native')}只调用真实systemd、/proc、cgroup与当前boot/授权接口，生产路径没有fixture backend或从JSON读取observed入口。原生origin=NATIVE_OS/1，合成记录另为SIMULATION_ONLY/1且不能mintlease。

顶层字段包含batch/boot、service_unit、case、process_pid/starttime、样本序号、开始/完成BOOTTIME、check_phase、checks[8]、aux_checks、first_failed_check/all_failed_checks、raw_error、overall_result。每项包括expected、双侧observed、来源、read_time、process_identity、state_phase、status_version、read_success、MATCH/MISMATCH/NOT_READY/READ_ERROR及原始错误。

systemd argv/exit/原始双流hex、前后完整属性；/proc status/limits/cgroup原文与采样时间；parent kernel值/device/inode均保存。分项结果独立计算，不靠OR短路。转化/读取中断保留partial_raw；未读字段用null与错误说明，绝不填期望值。STARTING的凭据字段为明确deferred的NOT_READY，不声称已观察正确或错误。

每个采样在进一步判断/等待/放票据前写入Root私有`ready_C00_####.json`或C10对应文件。写入失败输出必要错误并fail-closed；不会以日志失败作为继续理由。稳定READY再完整重采样，发布Root:989/0640的C00_READINESS/C10_READINESS；Root原始行置于既有0700私有目录。无sealed nonce复制到诊断。

辅助门使用独立CR-A-*编号，明确区分原8项；PID/version/boot/stop/deadline及parent/proc错误不再混入未知总拒绝。状态转变/退出后最后合法快照保留其时刻，不用服务退出后的默认配置补现场。
''')

report('C00_SNAPSHOT_CONSISTENCY.md','双次取样、身份锚与一致性前提',f'''
不存在跨systemd、procfs和cgroup的共同原子状态版本。源码使用有限书签和双次收集：unit前读→pidfd/identity锚→proc及parent读→unit后读→proc及parent后读→PID/boot/FD再检查；READY要求全部值符合原约束，两个manager版本及目标身份一致。

manager版本含InvocationID、StateChangeTimestampMonotonic和关键属性的原值；后者只作不透明版本比较，不与BOOTTIME相减。pidfd防止把退出/复用的新PID当作原目标，PID/starttime/boot在采样内与相邻样本均检查；非零MainPID及Invocation改变失败。合法PID0→assigned或STARTING→active只生成新轮次NOT_READY，不拼接成READY。

进程credentials/status为同一proc文件读，实际AS/cgroup及parent限额单独双读；任何稳定不符、退出或读取失败直接终止。lease确认再次进行完整采样，票据写前再核存活/期限/停止，Root票据绑定证书摘要。

一致性前提：冻结controller在ticket前只等待，不自行改变凭据/资源；无并发特权代码/单位/成员更改。两侧相等无法完全排除特权ABA、瞬时资源迁移或读后立刻退出，这些继续CONDITIONAL，原服务内kernel admission和完整资源门仍需fresh检查。源码不把八个时刻的匹配无条件宣称同一原子快照。

当前采样和pidfd均未实际执行；后续动态许可需记录这些书签与未知窗口。[原生collector](<../../../DCL-R6-isolated-verification/cr01/src/service_readiness.py>)、[静态检查](evidence/STATIC_CHECKS.json)。
''')

report('C00_FIX_IMPLEMENTATION.md','最小依赖修复与保留的安全逻辑',f'''
最终C00Ready-static-1/r2只位于host `D:\\毕业设计\\DCL-R6-isolated-verification\\cr01`，当前Linux部署/查询/服务0。实际依赖：原八项位于boot_continuity.service_confirmed，由C00/C10共用；Guard负责票据发布，必须把有界native lease送入该调用。C10只调整相同启动资格，原业务探针字节保持。

新增service_readiness.py、readiness_regression.py、readiness_oracle.py；Guard接入C00/C10屏障、64回归、FORMAL附加门和明确的最小/完整模式。boot_continuity的service_confirmed委托native lease，保留原service_policy、Owner/boot、BOOT_START/RESUME发布逻辑；仅增加固定ready公共文件目标和新范围检查。

sealed cap的生成/封印/继承/exec代码段、read_capability、ticket_policy、guard_admission、child_admission等保护函数AST保持（命名归一后），同进程C09恢复仅额外阻断诊断模式。RootIPC、C09与BC40仅batch08/cr01命名适配。15份既有程序字节、24预算/资格函数AST保持；五业务、原probe、runner、range核心/夹具/oracle不动。

第一模式C00_DIAGNOSTIC_ONLY：真实C00 READY＋原probe＋64合成检查后close/seal，不授RESOURCE_GATE_PASS。第二模式原完整条件链要求Full_conditional_chain_explicitly_approved；原FORMAL scope与C/S/H/负向门均保留，新增ready证明无法绕过原门。最小模式不要求授权未使用的RootIPC探针或C09恢复。

新包23 Linux源码＋1 Windows入口＋12输入=36项，保持source-only。输入只必要批名/路径/版本/锁与新合同适配，原RootIPC56/C09H34/BC40/S34/门17语义归一相同。r1候选36项与检查保留；最终动态申请仅匹配r2。

[原32项](evidence/original)、[完整source diff](evidence/SOURCE_COMPLETE.diff)、[完整input diff](evidence/INPUT_COMPLETE.diff)、[静态结构检查](evidence/STATIC_CHECKS.json)。
''')

regrows=[[j['case_id'],' → '.join(j['frames']),j['variant'],j['expected_violation'] or j['expected'],','.join(j['allowed_violations']) or '∅','UNRUN'] for j in cfg['jobs']]
report('C00_REGRESSION_PLAN.md','64项正反、竞态及17项变异计划',f'''
64＝30基础场景＋17个mutant对照＋17个mutant。每项冻结初态、事件帧、实际模拟状态来源、期望结果、允许违规和原始证据；当前执行0。涵盖立即/阶段性READY、MainPID未赋值、exec阶段变化、字段次序、全部8项稳定错、错误单位/类型/proc/TasksMax/boot/PID、读取缺失、跨版本、退出、失败、超时及STOP/CLOSED。

{table(['job','事件帧','variant','期望末态/违规','允许违规集','actual'],regrows)}

17个mutant包括逐项忽略CR-01…08、读错视为匹配、陈旧快照、只查UID、错误PID/boot、把稳定失配降级STARTING、超时仍等、无锁放行和跨版本拼接。subject使用生产纯分类器；独立oracle不导入collector/policy/subject，依据冻结帧语义与实际observed原件重算，拒绝未触发/未检测/额外未声明违规。

模拟源与原生资格隔离：fixture函数只构建带明确SIMULATION_ONLY标记的过渡状态，不能进入原生collector或构造minted lease。真实系统字段、错误errno与就绪成本另由获准C00动态诊断取得。

计费entry1＋64×(保守预付6＋Root审核1)=449，专项硬限512；共享原C00 ticket及T0+300，不创建独立账/时间窗。该阶段在原共同5000的C09H/RootIPC/BC之前，完整cal硬访问上界62034+512=62546≤100000。原1000000/1800与cal300保持，额外采样/写盘耗时动态待测。
''')

report('STATIC_VERIFICATION_RESULTS.md','最终静态语法、依赖与完整门审查',f'''
24份程序通过host compile及Python3.12文法AST解析：23 Linux模块＋1 Windows入口。目标模块未import/执行，当前3.12原生编译、WSL诊断与合成测试均UNRUN。host解释器与每份SHA记录在[STATIC_CHECKS](evidence/STATIC_CHECKS.json)。

15份旧源码原字节保持；24预算/资格函数AST等同；RootIPC/C09/BC40命名归一等同；protected Boot函数和原sealed claim/exec代码段等同。原business plan/child/runtime_critical/runtime_tree四输入字节相同；56/34/40/S34/门17仅批次命名归一。新64个唯一job、17mutant、最大帧数/预付与449/512、62546<100000公式核对通过。

取证顺序静态审查：已获准unit→exec phase→原生双取样→全部8项和辅助门→私有持久诊断→minted lease→完整再采样/证书→存活期限复核→Root票据；STARTING不发票，不发生模型/计费probe访问；FAILED原关闭逻辑接管。诊断写入/查询/解析错误不变成MATCH。

完整链兼容：C00成功仍需要BC40、C01–C12、RootIPC56/C09H34/真实C09、S34、门17和完整Root重算；FORMAL在原门前增加ready证明与Full批准检查。仅诊断模式成功会关闭，不导入F1/F4。预算核心与C01–C12的业务逻辑没有实现改动。

动态未决：真实systemd255.4字段/Job及版本、pidfd/一致性/错误持久化、14秒响应与300秒全套可完成性均待新许可。上游v255源码支持exec就绪设计，具体batch07失败字段仍UNRESOLVED；无并发特权ABA/调度/存储的原条件保留。

2034项历史研究、旧包、源工作区及47误副本hash核对，旧R0/37293/37021/32191保持；本轮没有安装依赖、改变WSL配置、启动服务、创建batch08/T0/账或运行模型。
''')

hashrows=[[name,sha(W/'inputs'/name)] for name in ['static_manifest.json','execution_lock.json','readiness_contract.json','boot_contract.json','root_ipc_contract.json','c09_contract.json','safety_contract.json']]
report('SOURCE_AND_INPUT_LOCK.md','C00Ready-static-1/r2最终源码和输入锁',f'''
唯一host工作区`D:\\毕业设计\\DCL-R6-isolated-verification\\cr01`，未来Linux路径`/var/lib/dcl-r6/cr01`。当前未部署，未来batch08路径仅为参数，本轮实体创建0。

{table(['锁','SHA-256'],hashrows)}

36项＝23 Linux源码＋1 Windows入口＋12输入，无pyc。未来native编译按source-only入口规则在内存检语法，不执行测试或写入冻结包。全量hash如下，权威机器锁见[STATIC_WORKSPACE_LOCK](evidence/STATIC_WORKSPACE_LOCK.json)。

{table(['相对路径','SHA-256'],[[r['relative'],r['sha256']] for r in frozen['files']])}

新单次WSL/exec流程、16原payload argv、34个S worker、Root额外原探针及14秒readiness/64 Root审核顺序、最小/完整scope均在[execution_lock](evidence/execution_lock.json)。旧参考resume或校准argv不能绕过sealed入口/范围条件。

任何后续源码/输入/阈值/权限改动须新冻结与匹配授权；本次只有静态修复许可，动态默认不获准。21旧程序与新模块的native平台兼容性需要下一阶段实际数据。
''')

auth=load(ROOT/'DCL-R6-BootContinuity-Fix/evidence/BATCH07_AUTHORIZATION_TEMPLATE.json')
auth.update(schema='BATCH08_AUTHORIZATION_TEMPLATE_STATIC_ONLY',authorization_status='NOT_GRANTED',batch_id='batch08',
 scope='C00_DIAGNOSTIC_ONLY',source_version='C00Ready-static-1',freeze_revision='r2',
 static_manifest_sha256=sha(W/'inputs/static_manifest.json'),execution_lock_sha256=sha(W/'inputs/execution_lock.json'),
 readiness_profile='C00-READY/1',readiness_contract_sha256=sha(W/'inputs/readiness_contract.json'),
 boot_contract_sha256=sha(W/'inputs/boot_contract.json'),root_ipc_contract_sha256=sha(W/'inputs/root_ipc_contract.json'),
 c09_contract_sha256=sha(W/'inputs/c09_contract.json'),safety_contract_sha256=sha(W/'inputs/safety_contract.json'),
 authorization_text_sha256=None,Root_coordinator_explicitly_approved=None,SingleSession_exec_explicitly_approved=None,
 C00_diagnostic_explicitly_approved=None,Full_conditional_chain_explicitly_approved=False,
 RootIPC_helpers_explicitly_approved=False,SameProcess_C09_resume_explicitly_approved=False)
dump(E/'BATCH08_DIAGNOSTIC_AUTHORIZATION_TEMPLATE.json',auth)
full=dict(auth);full.update(scope='CALIBRATE_S1S9_THEN_F1_F4',C00_diagnostic_explicitly_approved=True,
 Full_conditional_chain_explicitly_approved=None,RootIPC_helpers_explicitly_approved=None,SameProcess_C09_resume_explicitly_approved=None)
dump(E/'BATCH08_FULL_AUTHORIZATION_TEMPLATE.json',full)
report('BATCH08_EXECUTION_REQUEST.md','batch08最小动态诊断与独立完整条件链申请',f'''
当前文件为可审阅申请，尚无动态许可。绑定C00Ready-static-1/r2，batch07继续CLOSED/R0，不能恢复原窗或借用其许可。

{table(['锁','SHA-256'],hashrows)}

**第一目标/推荐范围：C00_DIAGNOSTIC_ONLY。** 请求部署cr01源模式包（35个Linux文件）、原生3.12语法/当前平台只读核验、单会话bootstrap/sealed claim/same-PID exec、C00真实逐字段/双次采样/就绪lease、原C00 probe、64正反夹具/17mutant及独立raw重算、必要停止与封存。无新增常驻服务/探针进程；最小模式完成即关闭，不进入C01/C09或模型。

Windows入口：

```text
python -X utf8 D:\\毕业设计\\DCL-R6-isolated-verification\\cr01\\host\\windows_entry.py --activate
```

唯一内部WSL argv：

```text
{' '.join(lock['windows_single_call'])}
```

**第二目标独立范围：完整条件链。** 只有新的明确Full_conditional_chain_explicitly_approved及原RootIPC探针/同进程C09恢复接受后，使用scope CALIBRATE_S1S9_THEN_F1_F4；C00/64通过后继续原实际依赖：C01–C08→C09H34→RootIPC56→BC40→真实C09→原窗一次内部恢复→C10新启动屏障→C11–C12→S34→门17→RESOURCE_GATE_PASS→F1→F4。第一目标成功不自动授权第二目标。

两份[最小模板](evidence/BATCH08_DIAGNOSTIC_AUTHORIZATION_TEMPLATE.json)/[完整模板](evidence/BATCH08_FULL_AUTHORIZATION_TEMPLATE.json)仅供审阅，批准位/原文hash尚空。最小模板明确不授予未使用的RootIPC探针与C09恢复。未来实际回执/原文放在冻结的host batch08研究路径，入口内fresh安装和核验；本轮不建立该批运行目录。

原CPY312-UBU24/1、AS4-PAYLOAD/1保持；native环境期望Python3.12.3/e50d…150f、kernel6.18.33.2、systemd255.4、cgroup2/UID999:GID989必须真实重核。当前没有查询这些平台；接口/字段缺失、权限或摘要漂移时停止，不改锁续跑。

资源差异明确：原总1000000/T0后1800、提前1740、cal300/100000、payload AS1GiB/父4tasks保持；预检TCB120秒/AS1GiB、sealed初始10秒继承原流程。C00/C10 readiness复用原14秒启动获取窗口，从请求前计时，写证/等待纳入已建立窗口。样本最多300＋最终确认、每行131072B；新64完成449、硬限512，共用原C00 ticket计费。完整校准硬访问静态上界由62034增加512至62546，仍低于100000，不增加总cap或延长300秒。C09H/RootIPC/BC原共同5000保持，真实全套耗时待测。

首次失败即保存实际8字段、辅助门、原始errno、前后unit/proc/cgroup/身份/boot/锁与时钟。禁止自动重跑、放宽字段、等待稳定错误变好、重置窗口、改源码/权限续跑或自动batch09。源/诊断写失败也fail-closed。原APP_READY不能代替exec-ready，读取旧boot或CLOSED无法发放新资格。

F2/F3、Casdoor、T1–T4、真实账户/凭据、WSL全局配置、依赖安装、无关单位和误副本处置/外发均不在申请内。实际原生验证、合成测试和F1/F4当前均UNRUN；IMPLEMENTATION_GATE=CLOSED。
''')

report('FINAL_DECISION.md','C00Ready-Fix最终静态裁决',f'''
**C00Ready-static-1/r2 已在host完成有限静态修复与冻结。具体batch07失败字段继续C00_FAILED_FIELD_UNRESOLVED；本轮新WSL/服务/诊断/目标测试0，batch08实体创建0。**

{table(['验收门','状态','实际范围'],[
 ['CR-1 失败字段分析','PASS_STATIC','从原源码提取8项；逐项缺口/短路语义明确，未用事后默认值补当时observed'],
 ['CR-2 诊断修复','CONDITIONAL_PASS','Native专用逐字段/原始来源/时刻/version/错误与失败写证实现；实际IO及写证故障待验证'],
 ['CR-3 安全就绪','CONDITIONAL_PASS','exec-ready三态、14秒同窗口、pidfd/双次采样/native mint、稳定错误直接失败；原生一致性/时延条件待证'],
 ['CR-4 回归及准备','PASS_STATIC','64夹具/17mutant、24程序host语法/3.12文法、36项锁/diff及两种独立申请完整']])}

源码依赖限Guard启动接线、共用C00/C10复核及新诊断/夹具。RootIPC/C09/BC40仅命名适配，15旧程序字节和24预算/资格函数AST保持；sealed claim/memfd/exec代码段及关键Boot函数保持，诊断模式新增范围只作收窄和显式完整许可门。原五业务/输入、探针/预算核心和56/34/40/S34/门17语义保持。

新Native路径不会从JSON填observed或以READY布尔直接发票；STARTING不取最终凭据并关闭业务资格，已确认的错身份/资源/读取失败等立即终止。所有8项/辅助门独立保存，公开Root保护证书与私有原始诊断分列；无sealed秘密复制到普通报告。无全局原子快照或硬实时宣称，特权ABA/并发配置变化/存储调度条件保持。

64项当前实际执行0，预付/审核上界449、硬限512；新完整cal硬上界62546≤100000，原1e6/1800及cal300不扩。batch08优先最小C00诊断并关闭；完整C/S/H/资源门及F1/F4必须独立明确批准。RESOURCE_GATE_PASS=NOT_OBTAINED，F1/F4=UNRUN_RESOURCE_GATE，PASS_BOUNDED授予0。

batch07真实单会话/同PID/封印与一次认领前缀、0.309347559秒关闭/0.327163166秒组空、R0、原始7条journal/34事件/15双流和失败保持；2034历史文件、原包、旧工作区/预算和47误副本hash保持。本轮仅host语法/AST/字节核验，目标3.12原生编译UNRUN。

D1-PBFT-SEAL/1.1原条件、强G覆盖、严格分离实例0及IMPLEMENTATION_GATE=CLOSED保持，基础设施修复不构成协议原创性升级。

[八项审计](C00_EIGHT_FIELD_AUDIT.md)、[诊断](C00_FIELD_LEVEL_DIAGNOSTICS.md)、[就绪合同](C00_SERVICE_READINESS_CONTRACT.md)、[batch08申请](BATCH08_EXECUTION_REQUEST.md)、[证据索引](EVIDENCE_INDEX.md)、[交付检查](evidence/DELIVERY_CHECK.json)。
''')

required=['C00_EIGHT_FIELD_AUDIT.md','C00_FAILURE_TIMELINE.md','C00_STARTUP_RACE_ANALYSIS.md','C00_SERVICE_READINESS_CONTRACT.md',
 'C00_FIELD_LEVEL_DIAGNOSTICS.md','C00_SNAPSHOT_CONSISTENCY.md','C00_FIX_IMPLEMENTATION.md','C00_REGRESSION_PLAN.md',
 'STATIC_VERIFICATION_RESULTS.md','SOURCE_AND_INPUT_LOCK.md','BATCH08_EXECUTION_REQUEST.md','FINAL_DECISION.md']
dump(P/'SOURCE_INDEX.json',{'schema':'CR-source-index/1','version':'C00Ready-static-1/r2','host_workspace':str(W),
 'future_linux':'/var/lib/dcl-r6/cr01','deployed':False,'files':frozen['files'],'hashes':dict(hashrows),
 'new_native_queries':0,'target_tests':0,'batch08_created_this_task':False,'historical_field':'C00_FAILED_FIELD_UNRESOLVED',
 'native_syntax':'UNRUN','new_simulated_jobs':64,'new_mutants':17,'resource_full_hard':62546,
 'source_changes':static['modified_source_files'],'source_bytes_preserved':static['same_source_bytes']})
dump(E/'SOURCE_DIFF_INDEX.json',{'version':'C00Ready-static-1/r2','source_sha256':sha(E/'SOURCE_COMPLETE.diff'),
 'input_sha256':sha(E/'INPUT_COMPLETE.diff'),'namespace_only':['root_ipc.py','c09_handoff.py','boot_continuity_regression.py'],
 'startup_changes':['guard.py','boot_continuity.py'],'new_modules':static['added_Linux_modules'],
 'original_source':'original/','protected_budget_AST':static['budget_gate_AST_unchanged']})
report('EVIDENCE_INDEX.md','C00Ready研究证据索引',f'''
{table(['文件','范围'],[[link(P/name),name[:-3]] for name in required])}

[原八字段机器审计](evidence/EIGHT_FIELD_HISTORICAL_AUDIT.json)、[旧事件/时钟](evidence/BATCH07_FAILURE_TIMELINE.json)、[公开v255源码参考](evidence/PUBLIC_SOURCE_AUDIT.json)、[host静态检查](evidence/STATIC_CHECKS.json)、[最终36项锁](evidence/STATIC_WORKSPACE_LOCK.json)、[Source索引](SOURCE_INDEX.json)。

[完整source diff](evidence/SOURCE_COMPLETE.diff)、[完整input diff](evidence/INPUT_COMPLETE.diff)、[diff索引](evidence/SOURCE_DIFF_INDEX.json)、[原BootContinuity32项](evidence/original)、[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)、[原始专项请求](evidence/TASK_REQUEST.txt)、[范围/分离门](SEPARATION_AND_SCOPE.md)。原sealed私有材料只在旧批受控范围，当前审计/报告仅用摘要，未复制其秘密值。

[C00READY_STATIC_REVIEW.zip](C00READY_STATIC_REVIEW.zip)包含本轮研究材料、最终36项和四导航；原batch07包保留外部原位且已逐流复核。[OUTPUT_MANIFEST](OUTPUT_MANIFEST.json)列文件路径/字节/sha/archive_path，[DELIVERY_CHECK](evidence/DELIVERY_CHECK.json)另列manifest与ZIP摘要。排除自引用并逐流核对，行政PASS不授予资源资格或模型性质。

r1候选及其检查保留，下一许可只绑定r2。当前future_linux只表示计划位置，不表示已经部署或核验当前平台；没有新的native命令/服务/目标测试日志可提供。
''')
report('README.md','DCL-R6-C00Ready-Fix','''
C00Ready-static-1/r2 host静态修复：真实八项审计、逐字段诊断、14秒exec-ready/native lease、64正反夹具/17mutant、最小诊断与完整链独立模式已冻结。

[最终裁决](FINAL_DECISION.md) · [batch08申请](BATCH08_EXECUTION_REQUEST.md) · [源码锁](SOURCE_AND_INPUT_LOCK.md) · [证据索引](EVIDENCE_INDEX.md) · [静态审阅包](C00READY_STATIC_REVIEW.zip)

具体batch07失配字段未决；当前native查询/服务/测试0，batch08创建0。RESOURCE_GATE_PASS未取得，IMPLEMENTATION_GATE=CLOSED，严格分离0。
''')

intro='''# DCL-R6-C00Ready-Fix 最新静态裁决（2026-11-11）

C00Ready-static-1/r2在host冻结：原真实8项逐字段审计/诊断、exec-ready三态与14秒同窗口屏障、双次采样/pidfd/native lease、C00/C10票据前复查；具体batch07失败字段仍C00_FAILED_FIELD_UNRESOLVED。原sealed/一次认领/exec与RootIPC/C09逻辑保持，15旧程序字节和24预算/资格函数AST保持。

CR-1/CR-4=PASS_STATIC，CR-2/CR-3=CONDITIONAL_PASS。64夹具/17mutant、24程序host语法/3.12文法和36项锁完成；native部署/查询/服务/测试/batch08创建0。最小C00_DIAGNOSTIC_ONLY完成后关闭，完整C/S/H/门/F1F4另需明确批准；新增449/512访问，完整cal硬上界62546≤100000，原300/1800及总1e6不扩。

batch07同PID/boot启动前缀、R0及原失败原件保持；旧预算/历史/误副本/blocked by policy保持。D1-PBFT-SEAL/1.1原条件、强G覆盖、严格分离0、IMPLEMENTATION_GATE=CLOSED保持。

[最终裁决](DCL-R6-C00Ready-Fix/FINAL_DECISION.md) · [batch08申请](DCL-R6-C00Ready-Fix/BATCH08_EXECUTION_REQUEST.md) · [证据索引](DCL-R6-C00Ready-Fix/EVIDENCE_INDEX.md)

以下为本轮前完整保存的历史导航，各旧阶段许可/下一步/未创建文字按相应时点理解。

---

'''
for row in base['navigation']:(ROOT/row['original']).write_bytes(intro.encode()+Path(row['snapshot']).read_bytes())
planned={P/'OUTPUT_MANIFEST.json',P/'C00READY_STATIC_REVIEW.zip',E/'DELIVERY_CHECK.json'}
count=0;errors=[]
for path,content in [(q,q.read_text(encoding='utf-8')) for q in P.glob('*.md')]+[(ROOT/'README.md',intro)]:
    assert '不是' not in content
    for target in re.findall(r'\]\(([^)]+)\)',content):
        target=target.strip('<>')
        if '://' in target or target.startswith('#'):continue
        count+=1;q=(path.parent/target.split('#')[0]).resolve()
        if not q.exists() and q not in planned:errors.append({'file':str(path),'target':target})
assert not errors,errors
for name in required:assert (P/name).is_file()
parsed=0
for directory in [P,W]:
    for q in directory.rglob('*.json'):
        if q.name not in ['OUTPUT_MANIFEST.json','DELIVERY_CHECK.json']:load(q);parsed+=1
dump(E/'REPORTING_RECEIPT.json',{'schema':'CR-offline-reporting/1','new_links_checked':count,'link_errors':errors,'JSON_parsed':parsed,
 'native_calls':0,'target_imports_or_tests':0,'script':str(Path(__file__).resolve()),
 'scope':'Host-only AST/grammar/data/hash/ZIP review; no current OS diagnostic or target replay'})
excluded={P/'OUTPUT_MANIFEST.json',P/'C00READY_STATIC_REVIEW.zip',E/'DELIVERY_CHECK.json'}
rows=[]
for directory,prefix in [(P,'research'),(W,'FROZEN_C00READY')]:
    for q in sorted(directory.rglob('*')):
        if q.is_file() and q not in excluded:rows.append({'host':str(q),'scope':prefix,'archive_path':prefix+'/'+q.relative_to(directory).as_posix(),'bytes':q.stat().st_size,'sha256':sha(q)})
for row in base['navigation']:
    q=ROOT/row['original'];rows.append({'host':str(q),'scope':'navigation','archive_path':'navigation/'+q.name,'bytes':q.stat().st_size,'sha256':sha(q)})
manifest={'schema':'CR-output-manifest/1','version':'C00Ready-static-1/r2','files':rows,'scope_counts':dict(Counter(r['scope'] for r in rows)),
 'exclusions':['OUTPUT_MANIFEST.json','C00READY_STATIC_REVIEW.zip','evidence/DELIVERY_CHECK.json'],'native_execution':'UNRUN','deployed':False}
dump(P/'OUTPUT_MANIFEST.json',manifest);archive=P/'C00READY_STATIC_REVIEW.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for row in rows:z.write(row['host'],row['archive_path'])
    z.write(P/'OUTPUT_MANIFEST.json','OUTPUT_MANIFEST.json')
with zipfile.ZipFile(archive) as z:
    assert len(set(z.namelist()))==len(rows)+1
    for row in rows:
        b=z.read(row['archive_path']);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'] and sha(row['host'])==row['sha256']
    assert z.read('OUTPUT_MANIFEST.json')==(P/'OUTPUT_MANIFEST.json').read_bytes()
delivery={'schema':'CR-delivery/1','status':'PASS_ADMIN_ONLY','version':'C00Ready-static-1/r2',
 'gates':{'CR-1':'PASS_STATIC','CR-2':'CONDITIONAL_PASS','CR-3':'CONDITIONAL_PASS','CR-4':'PASS_STATIC'},
 'required_reports':12,'candidate_files':36,'host_grammar_programs':24,'native_compile':'UNRUN','native_queries':0,
 'target_imports_or_tests':0,'batch08_created_this_task':False,'deployed_Linux':False,'new_jobs':64,'mutants':17,
 'completed_visit_bound':449,'readiness_hard':512,'full_calibration_hard':62546,'unchanged_calibration_soft':100000,
 'readiness_seconds':14,'field_cause':'C00_FAILED_FIELD_UNRESOLVED','source_bytes_preserved':15,'budget_gate_AST_preserved':24,
 'history_files':2034,'history_mismatches':0,'links_checked':count,'link_errors':[],'JSON_parsed':parsed,
 'manifest_rows':len(rows),'ZIP_entries':len(rows)+1,'ZIP_stream_errors':[],'manifest_sha256':sha(P/'OUTPUT_MANIFEST.json'),
 'ZIP_sha256':sha(archive),'ZIP_bytes':archive.stat().st_size,'source_manifest_sha256':sha(W/'inputs/static_manifest.json'),
 'execution_lock_sha256':sha(W/'inputs/execution_lock.json'),'readiness_contract_sha256':sha(W/'inputs/readiness_contract.json'),
 'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
 'IMPLEMENTATION_GATE':'CLOSED','strict_separation_instances':0,'sealed_utc':datetime.now(timezone.utc).isoformat(),
 'self_excluded_from_manifest_and_zip':True,'scope':'Offline static/code-byte/new-link/ZIP integrity only; native safety conditional'}
dump(E/'DELIVERY_CHECK.json',delivery);print(json.dumps(delivery,ensure_ascii=False,indent=2))
