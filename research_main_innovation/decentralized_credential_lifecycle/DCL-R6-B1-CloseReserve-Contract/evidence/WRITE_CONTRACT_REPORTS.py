"""Write the fourteen authorized close-contract reports and evidence index."""
import json
from pathlib import Path
from READ_INPUTS import ROOT, PREVIOUS, OUT, E, RUNTIME, read, sha, save

def link(label, path, line=None):
    target = str(path).replace('\\','/') + ((':'+str(line)) if line is not None else '')
    return '['+label+']('+target+')'
def source(name, line): return link(name+':'+str(line),RUNTIME/name,line)
def ev(name): return link(name,E/name)
def doc(name): return link(name,OUT/name)
contract_path = OUT/'proposals/B1_MINIMAL_CLOSE_RESERVE_DRAFT.json'
intro = ('## Material Passport\n\nDCL-R6-B1-CloseReserve-Contract，B1-CloseReserve-Contract/review-1，'
         '2026-11-16，Asia/Shanghai。证据为当前冻结文件、源码调用关系、字节语法和抽象失败轨迹。'
         '本轮DCL动态、原生故障和模型执行均为0。\n\n')
tail = ('\n\nRESOURCE_GATE_PASS=NOT_OBTAINED，F1=UNRUN_RESOURCE_GATE，F4=UNRUN_RESOURCE_GATE。\n\n'
        'MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE，STRICT_SEPARATION_INSTANCES=0，'
        'PASS_BOUNDED=[]，IMPLEMENTATION_GATE=CLOSED。\n')
reports = {}
calls = read(E/'B1_CLOSE_CALL_GRAPH.json')
call_table = '|节点|函数/调用者|结果/前提|锁、日志和预算|失败出口|\n|---|---|---|---|---|\n'
for item in calls['nodes']:
    call_table += f"|{item['id']}|{item['function']}，caller={item['caller']}|{item['return_or_result']}，{item['preconditions']}|{item['lock_state']}，{item['possible_records']}，{item['budget_effect']}|{item['failure_exit']}|\n"
reports['B1_CLOSE_CALL_GRAPH.md'] = f'''# B1真实关闭调用图

当前64份源码/输入已先核对摘要。调用图逐节点记录函数、调用方、结果、前提、锁、原件、预算和失败出口。额度检查、cursor与EXHAUSTED属于待批B1语义，其接入点以原生真实调用路径固定。{ev('INITIAL_CHECK.json')} {ev('CURRENT_SOURCE_EXCERPTS.json')}

{call_table}

```mermaid
flowchart TD
  G[guard pidfd就绪799-800] --> H[observe_exit取得H锁254]
  H --> Q[拟B1额度前置检查]
  Q --> F[事实与classify276]
  F --> R[原始CHECK append/fsync277]
  R --> U[H上下文退出]
  U -->|普通PENDING| G
  U -->|真实VERIFIED| N[close=False交接回收281]
  N --> V[H内验证/结果/状态发布]
  V --> RS[原授权条件下恢复]
  U -->|配额耗尽固定异常| A[第一层abort808]
  A --> S[STOP/首错/ABORTING/停止/退出/预算收据]
  A --> B[第二层abort817]
  B --> S
  B --> X[finally独立sealer检查822]
  X --> P[后层native/admin结果]
```

直接返回EXHAUSTED时，801–805分支无法消费该新值，已就绪pidfd可再进入观察。其他deadline/异常仍可能结束循环，quota自身没有给该调用次数终止界。实际额外分类或日志是否生成取决于拟议额度门，当前冻结代码没有EXHAUSTED返回分支。{source('src/guard.py',799)}

映射成CLOSED会调用close=False，仍尝试payload stop/empty确认，该调用不发布CLOSED，也未在该分支执行MR首错/共享STOP及Root角色回收。现有CLOSED吸收返回来自真实STOP/CLOSED存在判断。{source('src/c09_handoff.py',255)} {source('src/guard.py',803)}

唯一推荐语义是最后完整PENDING与拟cursor完成后抛出现有固定AdmissionBlocked，经H上下文退出交给808/817。正常有效fd语义下，lifecycle_lock的finally先unlock再close，outer except随后进入abort。unlock/close错误、Root死亡和kernel完成时延进入独立故障矩阵，释放锁事实需要对应前提。{source('src/c09_handoff.py',40)} {source('src/guard.py',806)}
'''

required = read(E/'B1_CLOSE_REQUIRED_EVIDENCE.json')['items']
required_table = '|ID|必要事实/层|实际或拟议载体|生成与丢失裁决|\n|---|---|---|---|\n'
for item in required:
    required_table += f"|{item['id']}|{item['fact']}，{item['tier']}|{item['existing_or_proposed_carrier']}|{item['producer']}，{item['when']}，{item['on_loss']}|\n"
reports['B1_REQUIRED_CLOSE_EVIDENCE.md'] = f'''# B1最小必要关闭证据

定义B1_CLOSE_REQUIRED_EVIDENCE为下列事实、来源和实际载体集合。安全关闭原件必须在行政归档工作前已被捕获并具有可用保留来源，索引只定位原件。每项的必要性、持久化、重复规则、主日志归属和独立来源详列于机器矩阵。{ev('B1_CLOSE_REQUIRED_EVIDENCE.json')}

{required_table}

安全最小集合包含身份/绑定、quota与最后raw、首错、共享取消、实际payload/其他Root退出、最终预算及有限关闭尝试/结果。正常VERIFIED路径还保存原cleanup、更新handoff、result_C09和batch_state。native层读取既有activation/checkpoint/phase/runtime-intent/role/budget/marker/waitpid等输入，完整ZIP和行政归档由后层负责。{source('src/c09_handoff.py',281)} {source('src/terminal_evidence.py',193)}

ABORTING与final共用mr_close_state，源代码会覆盖中间版本。其数据写入需要空间，最终集合以实际终态或残留partial/staging为准。现有实现没有为每个被覆盖中间版本另建历史副本。close_attempts的多行同属一个文件。{source('src/manager_recovery.py',355)} {source('src/manager_recovery.py',390)}

Receiver的结果含caller_exit_pending=true。当前进程无法在死亡前写入自己的已死亡事实，最终自身退出需要独立guardian/systemd/host的身份绑定观察及保留保障。当前专用、可保证保留的外部渠道为null，后层可能失败的admin任务不足以单独承担这一必要来源。{source('src/manager_recovery.py',392)} {source('src/startup_lifecycle.py',386)}

资源失败关闭可以用真实pidfd事实证明某目标已经退出，精确退出23和合法handoff仍需其原生来源。父waitpid缺失时保留该精确状态及native readiness的UNKNOWN，禁止重构失去的亲子见证。{source('src/guard.py',1225)} {source('src/c09_handoff.py',297)}

旧v2的334字节quota摘要属于待议辅助载体。若最终profile采用它，就计入实际写入/暂存成本。quota事实本身由原始log/cursor及MR首错共同绑定。原commit/resources和全部4,450份全系统原件均按既有原始层保留，B1关闭池仅计其实际必要保护/新增写入责任。
'''

reports['B1_CLOSE_RECORD_COUNT_PROOF.md'] = f'''# B1关闭调用与记录数证明

**CONDITIONAL_PROVED。** 定义E域为一次新鲜的第256条PENDING耗尽事件，初始C09阶段Sender已经退出，HANDOFF_VERIFIED尚未建立，恢复尚未发生，观察/关闭没有新global debit，拟异常吸收语义生效。原全scope界H52/core212、A16/S23/Q7/W2另行保留。{ev('SCOPED_CLOSE_COUNT_PROOF.json')}

|类型|E域最多调用/生产|唯一目标/稳定路径|重复与池归属|
|---|---:|---:|---|
|Receiver第一层abort|1|多原件节点|最多9项核心生产尝试，健康串行前缀8写/7路径|
|Receiver第二层abort|1|复用固定目标及新stop路径|最多9尝试，健康串行追加6写，前后合计14写/9路径|
|同阶段coordinator abort|4|同固定目标及其stop路径|继承一阶段有限异常包装器，已退出Sender的Python finally不执行|
|STOP_REQUEST|≤6次Root发布|1|存在检查可并发覆盖，按写量和稳定路径分别计|
|first_failure|≤6次put尝试|1|exclusive首次文件，无独立随机staging|
|external_closing|≤6次put|1|同一受信delegate原件，替换写产生临时对象|
|ABORTING/final|各≤6次put|同1文件|两个版本写成本，最终路径一次计量|
|CLOSED|primary/fallback尝试共同受S/A约束|1|H锁保护首次终态，部分发布失败仍可后续尝试|
|stop_event|≤8次primary marker候选|≤8|CLOSED已存在时创建，来自实际有限stop调用|
|stop_result|≤8|≤8|每次到达结果发布的stop调用一个路径|
|close_attempt行|≤6|1文件|每个非announce abort至多一行|
|waitpid|≤1|≤1|只在当前initial phase实际父进程reap时发布|
|sealer调用|≤3|后层对象另计|coordinator finally、boot异常、Receiver external tail各一次|

E域active coordinator至多一个阶段，其abort≤4；Receiver两层≤2，故A_E≤6。每abort至多一次primary stop_tree，coordinator另外两个直接stop位置各至多一次，故S_E≤8。W_E≤1、Q_E≤3、H_E=0。由原七项非stop-tree生产规则得到。

\\[N_{{E,production}}\\le7\\times6+2\\times8+1=59.\\]

核心稳定目标粗界为5个固定异常目标＋2×8个stop路径＋close_attempt文件1＋waitpid1=23。BC随机staging创建尝试≤3A=18，RootIPC≤2A＋2S＋W=29，合计47；稳定与失败staging路径类的粗合并界为70。它们是不同计量，极值也可能互斥。空mr_close.lock、必要目录与后层sealer lock等metadata另需inode/资源。{source('src/manager_recovery.py',33)} {source('src/root_ipc.py',105)} {source('src/boot_continuity.py',99)}

健康串行示例的第一层写STOP、first、delegate、ABORTING、CLOSED、result、attempt、final共8次。第二层复用STOP/first，写delegate、ABORTING、stop_event、result、attempt、final共6次。ABORTING/final同路径，最终共9个稳定核心路径。该示例需要Receiver首错胜出、普通持久化成功且两次primary cleanup均完成。

正常VERIFIED路径执行一次close=False，并发生HANDOFF_VERIFIED状态、result_C09、AWAIT状态、RESUMED状态及恢复batch_state五次其他数据发布，共6次真实发布、4个稳定载体。其stage主行已经属于263/345148。预付/bind/ACK/resume失败等E域外的B1故障使用原更宽冻结角色包络，212次尝试持续保留其作用域。

现有first文件有幂等首错性质，其他attempt/event仍会追加。当前没有close请求ID或单独关闭grant账，因此“恢复不重发关闭额度”和“CLOSED后冻结新预留”是拟合同义务。已经预留的有限关闭操作需要在CLOSED之后完成final/退出证据，普通新观察和新的关闭预留发行同时吸收。域外任意E_n不属于原次数界。
'''

reports['B1_CLOSE_BYTE_BOUND_PROOF.md'] = f'''# B1关闭字节边界

**PARTIAL，B_B1-close=null。** 逐字段语法复核采用原compact/RootIPC编码和明确ABI宽度，并对E域作范围收敛。原件唯一集合、失败staging与累计生产写量分别计量。{ev('B1_CLOSE_BYTE_ALGEBRA.json')}

|记录|条件encoded bytes|
|---|---:|
|ABORTING|237|
|external_closing|260|
|normal waitpid|1223|
|fallback waitpid|565|
|marker|144＋R|
|固定43字节quota reason marker|189|
|通用Root MR marker|194|
|first，R_MR≤38|25092＋T＋B|
|cleanup state / attempt行|997＋11T＋B / 998＋11T＋B|
|stop_result|1151＋E＋ΣV_j|

R为包含引号的reason JSON token，R_MR固定调用值与R_budget异常str分开。T为异常类名token，B为三份原budget hash/size或UNKNOWN/type映射，E仅来自stop_tree的lock/marker发布try中的repr，V为12个原kernel值token。B≤69＋3max(106,29＋T)，健康B≤387。compact ensure_ascii=True每code point最多12，RootIPC UTF-8/转义最多6；字段键、括号、分隔符、缩进及LF都已按实际codec计入。

PID正int32≤10、ticks/device/inode/预算长度u64≤20、clock_ns≤20、binary64 JSON≤25、waitstatus≤11、stat_ctime_ns≤29及冻结namespace是明确条件。EIO/乱码或profile外数据不能借这些条件获得正常完成证据。{link('原逐字段代数',ROOT/'DCL-R6-C09-CloseReserve-Closure/evidence/CLOSE_SCHEMA_BYTE_ALGEBRA.json')}

对A6/S8/W1/H0的E域，沿实际生产次数求和得核心累计生成字节包络。

\\[W_{{E,core}}\\le179815+138T+18B+8E+8\\sum V_j.\\]

按实际唯一目标计稳定数据，再单列不同临时路径，可得两个保守式。

\\[B_{{stable,E}}\\le44708+78T+8B+8E+8\\sum V_j.\\]
\\[B_{{failed-stage,E}}\\le23275+66T+6B+8E+8\\sum V_j.\\]

路径类合并后为67983＋144T＋14B＋16E＋16ΣV。它是同一稳定路径一次、每个实际临时路径一次的粗并集上界，单项极大值未被证明同时可达。生产量式是另一保守包络，条件参数给定后可取适用上界中较小者。

健康串行Receiver示例中，原始quota故障代码31字节ASCII、AdmissionBlocked类名16、首个reason25，健康budget387且notes为空。于是first≤941、marker≤183、cleanup≤1119，14次数据发布的累计字节≤9272＋2ΣV。该示例仍欠完整V profile及真实物理保留。

正常handoff新增/替换的4个稳定载体为stop_result、handoff、result_C09、batch_state，保留字节≤7098＋3ΣV。计入verified/resumed两次state和batch更新，6次发布累计≤11189＋4ΣV。cleanup在3个真实稳定载体中各出现一次，源码写入次数中复制4次，按真实对象计量。{ev('NORMAL_HANDOFF_BYTE_MODEL.json')}

最终合同按唯一必要目标求ΣN_iL_i，加实际失败metadata/staging、所选quota补充、外部退出证据和引用index。encoded数据与物理allocation用不同单位。完整T/E/V、外部witness/index字节和FS metadata/provider参数未实例化，完整关闭数值保留null。{link('最小合同草案',contract_path)}
'''

reports['B1_MAIN_AND_CLOSE_QUOTA_SEPARATION.md'] = f'''# 主日志与关闭保留域

345148只对应拟主日志槽，close独立余额/请求绑定/发行规则及实际存储保障需要最小合同。当前主quota与关闭quota均未激活，LOGICAL_QUOTA_RESERVED的B1-close事实尚未建立，PHYSICAL_STORAGE_RESERVED尚未取得。{ev('PHYSICAL_STORAGE_AUDIT.json')}

|域|实际对象/计量|重叠处理|
|---|---|---|
|main|c09_events.jsonl，分类/stage/ACK，345148条件界|包含最后PENDING、VERIFIED等原主行|
|local quota|拟cursor和可选334摘要及其失败staging|原350166已包含声明main/marker等，不能再次整项相加|
|close core|STOP/first/delegate/state/attempt/CLOSED/event/result/父waitpid|同路径覆盖只计稳定版本，写入累计另算|
|global prepay|visits.bin、intent、journal原件|close中的budget map只引用hash/size|
|external witness/index|受信独立退出和实际原件引用|provider、profile和容量当前null|
|native/admin|原始输入引用、后层产物与实际层复制|由后层容量/资源合同约束|

每个健康scalar预付有PREPARED/COMMITTED两条compact＋LF journal，行界238/239，256事务共512行、增长≤122112。两次Root intent replace写累计142592，counter每次8字节共2048，因此266752=122112＋142592＋2048。122112和512行已经属于该总写量。{ev('PREPAY_AND_CLOSE_PARTITION.json')}

142592是intent多次替换写量，当前profile最终单份intent≤279；2048是counter覆盖写量，counter原件仍24字节。累计写入量与实际保留磁盘占用分别计算，B1 close不能把266752当作新可用关闭空间。Root健康2304次fsync只覆盖该256事务的两个跨目录intent、两个journal和counter共9次/事务。

拟closing reservation应在普通main进入前绑定一次，普通观察不能消费其计数/字节/物理底线，重复请求不能发新额度。STOP/CLOSED之后冻结普通观察和新reservation发行，已经预留的有限清理任务按合同继续完成。当前没有这套close额度执行对象，恢复缺失/模糊凭据时拒绝重新初始化是待实现义务。

本轮不分配新limit或改变budget事务。原始预付前缀/阶段限额和旧T0持续约束未来方案，任何关闭失败都不退款、不创建新免费窗口。
'''

reports['B1_PHYSICAL_RESERVE_AUDIT.md'] = f'''# B1物理空间与持久化审查

**PHYSICAL_STORAGE_RESERVED=NOT_OBTAINED。** 当前close相关五模块未找到fallocate/posix_fallocate/ftruncate、statvfs/disk_usage调用；冻结B1材料缺少物理保留provider或凭据。该审查根据当前代码和已取得材料记录结论，Linux活动存储状态未查询。{ev('PHYSICAL_STORAGE_AUDIT.json')}

RootIPC保证private/out的st_dev一致，按目标策略编码后创建新的随机.publish文件，写入、file fsync、rename及目录fsync。BC.Store在boot目录为替换创建.bc随机临时对象，并执行文件/目录barrier。当前代码未为这些新对象建立独立可消费的关闭空间底线。{source('src/root_ipc.py',71)} {source('src/boot_continuity.py',86)}

物理合同至少需要绑定每个target/staging的真实device/filesystem/目录generation、data extents、inode、目录项/rename、journal/COW metadata，以及old/new版本重叠和允许其他writer的排除规则。空mr_close.lock即便数据字节0也需要inode与目录metadata。内存page_size=4096并未提供磁盘allocation unit。当前这些参数保持null。

\\[P_{{close}}\\ge\\sum_i\\lceil s_i/a\\rceil a+P_{{inode}}+P_{{directory}}+P_{{FSjournal/COW}}+P_{{temporary}}.\\]

式中a和各metadata费用必须来自实际受信backend。仅做namespace权限和相同st_dev检查无法得到其他日志不占用关闭底线的结论；fsync或rename还可能在数据写入之后需要metadata空间。外部host路径也需独立绑定故障域与保留责任。

最小反例选择健康介质上的容量分配压力，最后raw和cursor已提交，逻辑close余额仍正，新的STOP/CLOSED staging却返回ENOSPC。它没有违反已配置的应用路径权限，也无需任意新DCL调用。当前无保护底线的组合不能保证必要持久停止记录。{ev('MINIMAL_STORAGE_COUNTEREXAMPLE.json')}

标准可选方向为真实预分配/受信存储保留服务及排除普通writer的等价保障。若方案变更RootIPC的同文件系统rename关系、目标policy或helper，需要在后续单独申请准确范围。当前只记录合同义务，没有实际配置、分配或源码变更。
'''

failure_rows = read(E/'PERSISTENCE_FAILURE_MATRIX.json')['rows']
failure_table = '|失败|本地与外部停止|退出与预算|内部/native/admin|\n|---|---|---|---|\n'
for item in failure_rows:
    failure_table += f"|{item['id']} {item['failure']}|{item['local_behavior']}，{item['external_stop_behavior']}|{item['exit_evidence']}，{item['budget_state']}|{item['internal_state']}，{item['native_seal']}，{item['administrative_result']}|\n"
reports['B1_PERSISTENCE_FAILURE_MATRIX.md'] = f'''# B1持久化失败矩阵

本地准入停止、实际进程回收、最小证据持久/完整、native/admin完成是独立结果轴。允许UNKNOWN的故障模型与正常存储下的空间充分性分别记录，任意I/O故障下完整持久化的承诺为false。{ev('PERSISTENCE_FAILURE_MATRIX.json')}

{failure_table}

RootIPC的_full短写会抛异常，完整write返回以后仍需对应fsync和目录barrier。持久化成功与数据存在于内存或page cache分别取证。_HALTED是本进程状态，共享STOP失败时其他Root/UID999 actor的停止事实仍需现有marker、intent健康、监督或独立退出证据。{source('src/guard.py',121)} {source('src/guard.py',82)}

父进程死亡前未保存的直接waitpid不能由Receiver补造。pidfd可提供目标已经退出的受信观察，精确exit code23和native门的必要输入继续按实际原件判定。当前caller_exit_pending=true也要求独立外部最终退出来源。

预算不因故障重建，已付prefix与模糊intent保留，缺失quota/close凭据拒绝恢复发新额度。固定source包装器有次数界，所有新增恢复/重试的策略都需要重新审批，当前未增加额外actor或调用。
'''

reports['B1_FAILURE_RESPONSIBILITY.md'] = f'''# Root、管理器、存储和外部TCB责任

|责任者|现有动作与证据|失败责任边界|
|---|---|---|
|Receiver Root|原pidfd观察、quota候选终态、808/817异常链、MR收据|自身死亡/marker缺失时不能凭本地_HALTED证明全局停止|
|直接父协调者|真实os.waitpid、原状态/exit_code发布、旧有限异常回收|死亡或发布失败后精确亲子见证可能永久缺失|
|systemd与kernel|stop/kill、pidfd、身份与cgroup empty观察|正确来源需新鲜绑定，失败/阻塞和实际退出时刻分别核验|
|RootIPC/BC.Store|权限、类型/无链接、编码、原子替换与fsync顺序|当前没有独立物理容量底线或任意介质故障成功保证|
|存储保障provider|拟提供close data/inode/metadata/temp底线及排除其他writer|实际provider、配额/分配凭据、持久性/故障域均null|
|外部guardian/host|拟在Receiver退出后提供独立身份绑定witness与保留来源|当前专用可保证渠道未绑定，不能依赖必定成功的后层归档|
|native/admin|按实际close、exit、预算、原件和空间前提完成或保留失败/UNKNOWN|部分产物不获得完整完成状态|

source的primary cleanup与fallback会尝试停止payload、Root角色回收及最终收据，真实Root/manager责任见当前调用段。{source('src/manager_recovery.py',369)} {source('src/manager_recovery.py',291)}

外部TCB合同需要指定操作者、准确监控对象/boot/PID-start/unit generation、停止动作、保存路径/权限/字节、期限与失败出口。仅有“外部会处理”不足以实例化该来源。必要安全证据应在后层archive开始前取得保留保障，index或admin receipt可以引用已有原件。

当前最小缺口是定量wire、物理资源/排他底线和独立caller-exit保留责任。这些责任可以针对B1关闭子集定义，完整4,450原件集合由后层负责。与受信kernel/Root故障模型一致的UNKNOWN和原预算保持规则保留。
'''

contract = read(contract_path)
field_table = '|序号|合同字段|值/责任|\n|---:|---|---|\n'
for item in contract['fields']:
    value = item['value']
    if value is None:
        text = 'null'
    elif item['field'] == 'fault_responsibility':
        text = '十类故障矩阵，逐项保持本地/外部/退出/预算/内部/native/admin轴'
    else:
        text = json.dumps(value,ensure_ascii=False) if isinstance(value,(dict,list)) else str(value)
    field_table += f"|{item['number']}|{item['field']}|{text}|\n"
reports['B1_MINIMAL_CLOSE_RESERVE_CONTRACT.md'] = f'''# B1最小关闭保留合同待批稿

精确对象为B1_MINIMAL_CLOSE_RESERVE_DRAFT.json，版本B1-CloseReserve-Contract/review-1，SHA-256为`{sha(contract_path)}`。当前approved/user_approved/effective/runtime_enabled均false，B_B1-close、物理保留和外部provider保持未实例化。{link('合同JSON',contract_path)}

{field_table}

本合同以B1安全事实和实际source载体为边界。scope_E的59次/23稳定路径/47失败staging是条件粗界，normal和其他B1故障各按独立域核算，具体数据/物理总量继续null。主log、预付、close、外部witness和后层archive必须分域绑定，实际路径只计一次。

独立逻辑closing reservation需要与source/batch/boot/handoff/generation绑定一次，普通写者不能花其余额，重放/恢复不发新额度。当前source尚无这样的close ledger。资源pool须真实排他可用，并包括原子发布峰值与metadata，审批前必须提供可信provider凭据及正常/故障责任。

当前可审议必要集合、scope、条件计数、持久顺序、失败责任和oracle规格。完整子合同生效及B1源修改仍受COUNTEREXAMPLE和null阻断。用户决定只按四类独立许可记录，当前决策为待批。

强通用G的有界append、物理预分配/受信保留、幂等事件、固定typed token与原子allowance可覆盖本候选。输入族为同一handoff额度耗尽及有限失败关闭，度量为真实原件字节、生产/staging次数、排他空间和预算/退出安全，预测严格差距0，严格分离实例0。{ev('GENERAL_G_COMPARISON.json')}
'''

props = read(E/'SECURITY_PROPERTIES.json')['properties']
property_table = '|性质|裁决|当前依据|\n|---|---|---|\n'
for item in props:
    property_table += f"|{item['id']} {item['name']}|{item['verdict']}|{item['basis']}|\n"
reports['B1_SECURITY_PROPERTIES.md'] = f'''# B1安全性质裁决

{property_table}

结论同时保留实际source、拟B1义务和故障结果。当前系统没有激活新的main/close额度，条件证明不能自动变为实际控制事实。对缺物理保障的候选组合，CloseReserveAvailability存在明确反例，B1源修改准入保留BLOCKED。{ev('SECURITY_PROPERTIES.json')} {ev('MINIMAL_STORAGE_COUNTEREXAMPLE.json')}

每个正常完成判断都需对应身份、锁序、source/counter、实际barrier和真实退出事实，任何缺失或无法归属的raw/staging保持UNKNOWN/拒绝。没有把SOURCE固定布尔值或提交者的PASS用于替代实际原件/内核观察来源。
'''

cases = read(E/'REGRESSION_ORACLE_SPEC.json')['cases']
case_table = '|性质|正常输入与失败输入|并发/崩溃交错|预期状态与字节|变异|\n|---|---|---|---|---|\n'
for item in cases:
    case_table += f"|{item['id']} {item['name']}|{item['normal_input']}，{item['failure_input']}|{item['concurrent_input']}，{item['crash_interleaving']}|{item['expected_state']}，{item['expected_bytes']}|{item['mutation_target']}|\n"
reports['B1_REGRESSION_AND_ORACLE_PLAN.md'] = f'''# CR-1至CR-12独立oracle与负向规格

本轮只设计数据规格和静态判断规则，十二项执行数均为0。未来oracle/harness/test清单位置继承上轮五个PROPOSED_ABSENT位置，实施门满足且用户准确授权后才可创建。{ev('REGRESSION_ORACLE_SPEC.json')}

{case_table}

每项独立oracle读取原始identity/boot/source/input/authorization、main完整行与partial尾部、cursor预扣/完成、实际close原件、budget及独立退出/provider凭据。单独实现判断规则，不导入target classifier/logger/Store，不把提交者PASS视作事实。结果类别为ACCEPT_CONDITIONAL_EVIDENCE、REJECT、UNKNOWN、UNSUPPORTED_BOUND、SCOPE_VIOLATION。

必须拒绝missing/foreign/duplicate/extra、hash/size/type/mode/binding不符、回滚预算/重发token、逻辑保留冒充物理保障、把快照标成新鲜退出事实和null伪装数值PASS。scope选择和数据引用层也属于校验对象。

测试前需要精确输入、字节/FS/provider参数、资源/时间约束及原件保留方法。scope_E反例是推导输入，当前没有故障注入、Root死亡或原生关闭测试。未来变异检查须逐个击中所指不变量并保留失败原件。
'''

reports['B1_RESOURCE_IMPACT.md'] = f'''# B1关闭资源与预付影响

本轮将累计写入量、稳定/临时保留数据和物理分配分别核算。预付数据按来源分区，字段全部来自上轮已核对源码codec/调用数，语义原件保持可追溯。{ev('PREPAY_AND_CLOSE_PARTITION.json')}

|计量|条件值|适用范围|
|---|---:|---|
|main保留|345148 bytes|拟main三类slot、codec和身份profile|
|global预付|256事务/512行journal|C09 controller/ready/counter固定前，原票据/deadline|
|journal新增数据|122112 bytes|256×(238＋239)，compact＋LF|
|intent累计替换写|142592 bytes|256×(278＋279)，同目标多次替换|
|counter累计覆盖写|2048 bytes|256×8，原文件24字节|
|上述预付总写|266752 bytes|三项一次相加，1280次数据写|
|Root健康预付fsync|2304|每txn两个Root intent各3、两个journal和counter各1|
|健康Receiver双abort例|14数据发布、31次helper fsync、12次budget文件扫描|8写首层＋6写外层，无清理错误，scope前提完整|
|E域core|59生产尝试、23稳定路径、47可能失败staging|A6/S8/W1/H0，encoded总量仍为符号式|

prepay数据已包含journal122112，closing snapshot仅嵌入三file hash/size；再次增加全journal会重复计量。稳定文件和暂存数据实际大小与累计写总和不同。FS data/inode/metadata/temp的保障须在它自己的单位和故障域求值。

正常handoff6次发布共≤11189＋4ΣV，稳定4载体≤7098＋3ΣV，主stage行已在main。fullIO/heap/FD/syscall/外部witness及原件index字节、kernel V profile和临界空间保障未闭合，当前不赋新资源上限。{ev('NORMAL_HANDOFF_BYTE_MODEL.json')}

既有5秒terminal read、30秒Linux admin child、300校准、1800全批和1740stop政策维持其原作用域。有限fsync/调用数不推出严格墙钟，端到端native/host时间仍需定量环境假设或获准的限定验证方案。本轮新T0/预算/WSL/动态均为0。
'''

reports['B1_IMPLEMENTATION_ADMISSION_REQUEST.md'] = f'''# B1源码实施准入记录

**B1_CLOSE_RESERVE_COUNTEREXAMPLE，B1_BLOCKED_BY_CLOSE_RESERVE。** 当前最小关闭合同不足以作为B1独立源修改准入依据，本轮停止B1实施申请提交，状态为SUSPENDED_UNTIL_MINIMAL_CONTRACT_SUFFICIENT。{ev('IMPLEMENTATION_ADMISSION.json')}

直接待补条件为适用close wire参数、真实data/inode/metadata/temp保留与普通writer排除、独立caller-exit保留来源及当前ownership/recovery映射。现有最小集合和计数已固定，完整4,450集合、全native/admin容量和端到端时间属于后层合同责任。必要安全事实仍须在后层archive前获得保留保障。

未来如果这些条件满足，条件性申请仅限c09_handoff.py、guard.py及对应quota输入/测试/oracle/harness/review-lock。manager_recovery为只读接口，runtime_tree_lock为只读TCB。精确五个位置和十项文件属性继承上轮，不创建该future目录。{link('上轮精确维护范围',PREVIOUS/'B1_FILE_LEVEL_MAINTENANCE_REQUEST.md')} {link('五个拟议文件位置',PREVIOUS/'evidence/FUTURE_FILE_SLOTS.json')}

后续申请需绑定当前hash/函数行、语义diff、保持式、正常/负向/变异检查、量化资源、候选回退、历史保护、新版本manifest和独立动态验收请求。当前这些字段作为申请条件索引保留，已发生的预算/终态永不回滚或重开。

四类决定各自待批。CAPACITY_CONTRACT_APPROVAL可审主256/263/345148等逻辑条款，MR原14条继续PROPOSED_NOT_EFFECTIVE，NATIVE_IMPLEMENTATION_AUTHORIZATION和FULLCHAIN_DYNAMIC_AUTHORIZATION均未授予。当前未收到任何新的用户批准，原source/locks和256/257守卫保持。
'''

answers = [
    ('真实调用链是否完整','18节点含normal/stopped/异常三分支、父进程旁路、两层abort与后层seal/admin，每节点有9个source属性。'),
    ('EXHAUSTED循环风险','直接返回时caller未消费，会在其他deadline/异常前反复进入；无quota局部次数界。推荐固定异常消费。'),
    ('H在abort前释放','正常valid-fd上下文finally先unlock/close再outer except；unlock/close失败或实际死亡延迟进入明确故障模型。'),
    ('两层abort记录','第一层健康串行8写，外层复用STOP/first再6写，合计14写/9路径；一般本地每层最多9核心尝试。'),
    ('必要集合','18项事实/载体涵盖身份/quota/首错/marker/回收/角色/预算/锁和后层引用，外部自身退出provider未绑定。'),
    ('212与唯一数关系','212为全冻结包络生产尝试，稳定路径粗界54；本轮E域59尝试/23稳定路径，47失败stage粗界另计。'),
    ('记录数量是否有限','CONDITIONAL_PROVED，E域A6/S8/W1/Q3/H0，局部Receiver两abort；域外调用和其他B1故障作用域分别处理。'),
    ('关闭字节有无数值','B_B1-close=null。得到E域生产179815＋138T＋18B＋8E＋8ΣV和唯一/暂存公式，TCB/provider/index等未实例化。'),
    ('345148与close是否独立','主log路径独立；当前close独立计数/物理底线尚未建立，旧350166组合按真实路径去重。'),
    ('512行与122112归属','原global journal的256PREPARED和256COMMITTED，各238/239条件行界，已经包含在预付总写内。'),
    ('266752是否重复','122112journal＋142592intent替换写＋2048counter覆盖写，一次相加。该值计量预付累计写入，关闭可用空间另需保留证明。'),
    ('RootIPC/Store物理保障','权限/metadata/发布/fsync来源明确，data/inode/metadata/temp保留provider及排他凭据未取得。'),
    ('耗尽时能保留停止记录吗','无保障组合存在ENOSPC最小反例，实际回收可尝试，必要持久信息无法保证，当前B1准入BLOCKED。'),
    ('short/ENOSPC/EIO结果','拒绝新授权、烧掉模糊slot、保留raw/partial/staging与原账；共享取消/实际退出/native/admin按证据分别UNKNOWN/失败。'),
    ('外部TCB责任','真实身份绑定stop/kill/pidfd/cgroup/manager观察及独立Receiver自身退出保留；provider、路径、byte和故障域需明确。'),
    ('native/admin最低输入','原activation/state/checkpoint/phase/runtime-intent/budget/role/marker/waitpid及最小已保存事实索引；admin不能补造丢失亲子/退出事实。'),
    ('B1可否独立实施','当前B1_BLOCKED_BY_CLOSE_RESERVE；充分受限子合同可成为直接门输入，其余完整容量null后层继续负责。'),
    ('最小源码文件','未来具备条件时c09_handoff.py和guard.py；MR/runtime_tree_lock只读。当前额外allocator/helper变化须单独申请。'),
    ('是否可提交实施申请','当前SUSPENDED，反例与关键null尚在。本轮保留条件索引和继承范围，源码/补丁写入0。'),
    ('还缺哪些审批','主quota逻辑及本最小合同定量/存储/退出来源、原MR有限规则、独立源码和完整动态四类决定均未实际授予。')]
answer_table = '|序号|验收问题|答复|\n|---:|---|---|\n'
for index,(question,answer) in enumerate(answers,1):
    answer_table += f'|{index}|{question}|{answer}|\n'
reports['FINAL_DECISION.md'] = f'''# B1最小关闭合同最终裁决

**B1_CLOSE_RESERVE_COUNTEREXAMPLE，B1_BLOCKED_BY_CLOSE_RESERVE。** 本轮完成所授权的最小合同、scope计数/字节式、物理保障审查、失败责任与独立oracle规格。当前无物理保留的组合存在具体容量分配反例，源码实施申请暂停。

|证明面|状态|结果|
|---|---|---|
|调用链/推荐语义|CONDITIONAL_PROVED|固定异常通过H退出到808/817，保留normal close=False路径和原CLOSED事实|
|E域关闭次数|CONDITIONAL_PROVED|A6/S8/W1/Q3/H0，59生产尝试/23稳定路径/47失败staging粗界|
|Receiver健康串行例|CONDITIONAL_PROVED|14数据发布/9路径，first941、marker183、cleanup1119，数据≤9272＋2ΣV|
|完整最小encoded/physical数值|PARTIAL|B_B1-close、FS分配及外部witness/index参数继续null|
|保留空间可用性|COUNTEREXAMPLE|最后main/cursor持久后新close staging可ENOSPC，逻辑余额不提供物理底线|
|实施准入|BLOCKED|B1_BLOCKED_BY_CLOSE_RESERVE，停止本轮实施申请提交|

反例目标为当前无物理保留组合的必要停止信息保存承诺。它是source-bound候选组合推导，原生故障执行0，存储故障下UNKNOWN与现有模型一致。该不完整结果仍不足以达到本轮实施直接门。外部TCB需实际承担并保留可信停止/退出事实，不能通过可能无法执行的admin阶段弥补缺失来源。{ev('MINIMAL_STORAGE_COUNTEREXAMPLE.json')}

E域仅对应初始C09第256条PENDING、无VERIFIED/无恢复及无新预算操作。正常成功handoff另有6次发布/4载体，其他B1故障继续使用全scope212/54及原A16/S23/Q7/W2/H52。两层abort追加并非一般API完整幂等，当前没有单独close额度账。{doc('B1_CLOSE_RECORD_COUNT_PROOF.md')}

主log345148、预付266752和其内journal122112各有明确来源，数据按实际层/路径一次计量。累计预付写量不代表保留容量，关闭预算映射不重复复制journal。最小合同20字段中数值不足者保留null，所有approved/effective/runtime_enabled=false。{doc('B1_MINIMAL_CLOSE_RESERVE_CONTRACT.md')} {doc('B1_MAIN_AND_CLOSE_QUOTA_SEPARATION.md')}

{answer_table}

强G比较为COVERED_BY_G，严格差距0、分离实例0。未升级架构原创性。四类实际批准均缺席，原MR14条摘要与状态按原绑定保留。当前完整native/admin容量、B_other和端到端资源/时间继续由后层负责，原256/257合同下完整成功目标的既有矛盾保持。{ev('GENERAL_G_COMPARISON.json')}

本轮14报告、18证据项、18调用节点、12项CR规格、10类故障矩阵及最小合同准备完成。9867历史文件加此前728交付件合计10595旧文件、64源/输入及原导航字节后缀将由最终交付核验逐件核对。source/预算核心/C09/MR/Guard/native/admin/gate/D1/D2改动0，新批次/T0/预算/补丁0，WSL/动态/真实故障/F1/F4执行0。{ev('DELIVERY_CHECK.json')}

下一步限定为用户决定和缺失的定量wire、真实存储保留/排他及独立退出保留来源。当前暂停实施申请，等待充分子合同证据与独立权限。{doc('B1_IMPLEMENTATION_ADMISSION_REQUEST.md')} {doc('EVIDENCE_INDEX.md')}
'''

for filename, body in reports.items():
    heading, text = body.split('\n',1)
    (OUT/filename).write_text(heading+'\n\n'+intro+text.lstrip()+tail,encoding='utf-8')
index = '# B1最小关闭合同证据索引\n\n'+intro
index += '本轮状态B1_CLOSE_RESERVE_COUNTEREXAMPLE / B1_BLOCKED_BY_CLOSE_RESERVE。\n\n'
for filename in reports:
    index += '- '+doc(filename)+'\n'
index += '\n机器证据与规格\n\n'
for name in ['INITIAL_CHECK.json','FROZEN_SOURCE_LOCK.json','PREVIOUS_ARCHIVE_RECHECK.json','CURRENT_SOURCE_EXCERPTS.json',
             'B1_CLOSE_CALL_GRAPH.json','B1_CLOSE_REQUIRED_EVIDENCE.json','SCOPED_CLOSE_COUNT_PROOF.json','B1_CLOSE_BYTE_ALGEBRA.json',
             'NORMAL_HANDOFF_BYTE_MODEL.json','PREPAY_AND_CLOSE_PARTITION.json','PHYSICAL_STORAGE_AUDIT.json',
             'MINIMAL_STORAGE_COUNTEREXAMPLE.json','PERSISTENCE_FAILURE_MATRIX.json','SECURITY_PROPERTIES.json',
             'REGRESSION_ORACLE_SPEC.json','IMPLEMENTATION_ADMISSION.json','CONTRACT_BINDING.json','GENERAL_G_COMPARISON.json','DELIVERY_CHECK.json']:
    index += '- '+ev(name)+'\n'
index += '\n'+link('最小合同待批JSON',contract_path)+tail
(OUT/'EVIDENCE_INDEX.md').write_text(index,encoding='utf-8')
save('FINAL_TWENTY_ANSWERS.json', {'answers':[{'number':index,'question':question,'answer':answer} for index,(question,answer) in enumerate(answers,1)],
                                 'close_verdict':'B1_CLOSE_RESERVE_COUNTEREXAMPLE','implementation':'B1_BLOCKED_BY_CLOSE_RESERVE'})
print(json.dumps({'reports':len(reports),'answers':len(answers),'contract_sha256':sha(contract_path),
                  'verdict':'B1_CLOSE_RESERVE_COUNTEREXAMPLE'}))
