"""Author the twelve requested review reports from declarative B1 evidence."""
import json
from pathlib import Path
from AUDIT_INPUTS import ROOT, PREVIOUS, OUT, EVIDENCE, RUNTIME, read_json, digest, save

def link(label, path, line=None):
    target = str(path).replace('\\', '/')
    if line is not None:
        target += ':' + str(line)
    return '[' + label + '](' + target + ')'

def source(relative, line):
    return link(relative + ':' + str(line), RUNTIME / relative, line)

def evidence(name):
    return link(name, EVIDENCE / name)

def report(name):
    return link(name, OUT / name)

logical = OUT / 'proposals/CAPACITY_LOGICAL_CLAUSES_DRAFT.json'
maintenance = OUT / 'proposals/B1_MAINTENANCE_REQUEST_DRAFT.json'
permissions = OUT / 'proposals/FOUR_PERMISSION_REVIEW_DRAFT.json'
mr = read_json(EVIDENCE / 'MR_APPROVAL_RECHECK.json')
plans = read_json(EVIDENCE / 'B1_FILE_PLAN.json')
slots = read_json(EVIDENCE / 'FUTURE_FILE_SLOTS.json')
clauses = read_json(EVIDENCE / 'CAPACITY_CLAUSE_MATRIX.json')['clauses']
intro = ('## Material Passport\n\nDCL-R6-B1-ApprovalGate，B1-ApprovalGate/review-1，'
         '2026-11-16，Asia/Shanghai。本阶段完成合同、语义差异规划与实施准入审查。'
         '证据为冻结源码/输入、既有证明和两项分开执行的只读源审查。\n\n')
footer = ('\n\nRESOURCE_GATE_PASS=NOT_OBTAINED\n\nF1=UNRUN_RESOURCE_GATE，F4=UNRUN_RESOURCE_GATE\n\n'
          'MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE\n\n'
          'STRICT_SEPARATION_INSTANCES=0，PASS_BOUNDED=[]，IMPLEMENTATION_GATE=CLOSED。\n')
reports = {}

reports['B1_SCOPE_AND_DEPENDENCY.md'] = f'''# B1范围与依赖裁决

**B1_BLOCKED_BY_CLOSE_RESERVE，BG-2=BLOCKED。** 主日志有限合同具备独立逻辑审议对象。本轮第六节要求实施前证明额度耗尽后关闭调用、必要停止信息保留、预算/CLOSED和资格语义。当前必要关闭子集的剩余空间、隔离与失败责任尚缺充分证据。完整审查逐项列于独立性门文件。{evidence('B1_INDEPENDENCE_GATE.json')}

|工作范围|当前依据|实施依赖|
|---|---|---|
|B1主日志有限维护|256尝试、六stage＋ACK1、263主行、345148字节的政策和条件推导|准确预付/绑定、全部sink约束、caller退出、必要关闭子合同和独立源码许可|
|完整关闭保留量|H≤52、core≤212及条件字节式|R_budget/T/E/V、实际关闭原件和持久化故障责任|
|全证据容量|旧scope 4450/4451/4452的条件数量界|各必要对象字节、精确Δ、工作内存/FD/IO和版本合同|
|归档与校验|既有manifest/ZIP/原件oracle规则|原件完整集合、codec、资源约束、当前关闭与quiescence事实|
|MR跨实例承认|原14条独立待批规则|用户原则决定、实际A证据、精确源码pair及B新鲜使用责任|

直接阻断B1的是额度耗尽路径的关闭子合同。可独立定义足以覆盖该路径的较小关闭集合，并证明其受信来源、可用空间和失败责任。本轮现有证据未形成这一充分子合同。全admin/native容量的其他null属于完整资格链后层依赖，后续解除B1直接门时应准确固定证明范围。{evidence('DEPENDENCY_GRAPH.json')}

真实路径从guard的就绪pidfd调用进入observe_exit，在H锁内构造facts、classify并event。异常离开该H上下文后，guard808和外层817各可能执行一次M.abort。MR保存STOP、首错、ABORTING、关闭/回收及最终收据。这些独立对象需要空间。{source('src/guard.py',799)} {source('src/c09_handoff.py',252)} {source('src/manager_recovery.py',317)}

一个最小组合前缀让最后一条PENDING和完成cursor成功持久，随后STOP/CLOSED的新staging创建返回ENOSPC。已有回收动作仍可尝试，持久停止信息保留为UNKNOWN。该前缀用于评估候选组合的准入责任，动态执行数为0。{source('src/root_ipc.py',105)} {evidence('B1_INDEPENDENCE_GATE.json')}

ResidualBounds的“可以提交B1有限维护申请”是待审请求。本轮按用户明确给出的实施独立性门完成审查，结果为BLOCKED。有限逻辑条款可以单独获得用户决定，B1实施许可仍需关闭门条件和独立源修改授权。{link('本轮任务原文', EVIDENCE/'TASK_REQUEST.txt')} {link('上轮审批包', PREVIOUS/'APPROVAL_DECISION_PACKAGE.md')}
'''

file_sections = []
for item in plans['files']:
    functions = ', '.join(item['affected_function'])
    file_sections.append(f'''### {item['relative']}

|项目|内容|
|---|---|
|file|{item['file']}|
|current_hash|{item['current_hash']}|
|category|{item['category']}|
|affected_function|{functions}|
|issue|{item['issue']}|
|proposed_delta|{item['proposed_delta']}|
|invariant|{item['invariant']}|
|regression|{', '.join(item['regression'])}|
|dependency|{', '.join(item['dependency'])}|
|rollback|{item['rollback']}|

{link('原文件', Path(item['file']))}
''')
future_sections = []
for item in slots['files']:
    future_sections.append(f'''|{item['file']}|{item['role']}|PROPOSED_ABSENT，current_hash=null|''')
reports['B1_FILE_LEVEL_MAINTENANCE_REQUEST.md'] = f'''# B1文件级维护申请

**范围审查PASS_STATIC，实施准入B1_BLOCKED_BY_CLOSE_RESERVE。** 行为候选为c09_handoff.py和guard.py。manager_recovery.py列为必须核验的接口依赖，涉及MR关闭责任变化时需新增明确申请。以下全部摘要直接取自已核对的ra01文件。{evidence('B1_FILE_PLAN.json')} {evidence('FUNCTION_SOURCE_INDEX.json')}

{''.join(file_sections)}

### 拟新增文件位置

建议的独立静态评审目录为{plans['future_review_root']}。目录名由本轮规划提出，采纳决定由用户作出。该目录与下列五个对象当前均为PROPOSED_ABSENT。完整十属性表记录在未来文件清单。{evidence('FUTURE_FILE_SLOTS.json')}

|拟议绝对路径|用途|当前状态|
|---|---|---|
{chr(10).join(future_sections)}

runtime_tree_lock的files绑定/usr/lib/python3.12标准库树，应用源码条目数为0。当前最小维护将其列为只读TCB依赖。准确需重冻结的绑定是source_hashes、bound_inputs、新quota输入、c09契约及对应静态审查锁。新运行namespace与执行身份属于后续独立申请。{evidence('BINDING_SCOPE_REFINEMENTS.json')}

回退适用于未来尚未执行的独立候选及其引用。若将来已经产生执行事实，该实例的原预算、T0、终态和全部原始证据永久保留，源码回退也须采用新的身份/锁。当前rollback字段属于计划。{link('待批维护请求', maintenance)}
'''

steps = read_json(EVIDENCE/'SEMANTIC_DIFF_STEPS.json')['steps']
step_table = '|步骤|主题|拟议语义|源码位置|\n|---|---|---|---|\n'
for item in steps:
    step_table += f"|{item['id']}|{item['subject']}|{item['required_semantics']}|{item['source']}|\n"
reports['B1_SEMANTIC_DIFF_PLAN.md'] = f'''# B1最小语义差异计划

该计划以现有Receiver.observe_exit()调用签名、main/window字段集合和原关闭接口为边界。候选耗尽路线采用现有AdmissionBlocked及固定quota耗尽代码，经H上下文退出进入既有异常包装器。该规划仍受B1关闭门约束。{evidence('SEMANTIC_DIFF_STEPS.json')}

{step_table}

|入口/分支|当前行为|申请中的必要接线义务|
|---|---|---|
|guard799–800|就绪pidfd触发observe_exit|每次调用先经过当前终态和quota准入|
|observe_exit261–277|check_base、facts、classify、event|第257次在这些新观察动作之前被拒绝|
|PENDING返回278|当前就绪fd保留，caller再次迭代|第256条保存后耗尽状态被消费，观察循环退出|
|caller801–805|仅VERIFIED/CLOSED有专门处理|新增EXHAUSTED返回值需要实际消费，当前最小计划选择异常路线|
|CLOSED分支804|stop_tree(close=False)|CLOSED返回值须基于已经存在的真实停止事实|
|两个异常包装器|808 abort后抛出，817可再次abort|按既有有限责任计量两次关闭，不将每次重试重新交回while|
|锁序|observe_exit持H，stop_tree758会再取H|cursor/raw/终态持久阶段完成后由上下文释放H，再进入M.abort/stop_tree|

全部三event调用及六stage都进入同一总行/字节约束。修改observe_exit的单个计数检查无法覆盖publish与ACK成本。新增policy hash、ordinal和类别位存入独立cursor，main/window字段变化须重新推导1322/948/1028。{source('src/c09_handoff.py',75)} {source('src/c09_handoff.py',196)}

相同facts的后续合法观察是新的付费ordinal。幂等责任针对已预扣token、stage类别和ACK，已有observe_exit零参数API由内部身份/序号管理支持。BC.Store的.bc随机staging没有目标名标签，关联当前B1 writer/绑定及辨认失败遗留的规则需要在候选中明确。如果方案要求helper API变化，应先扩大对应文件申请。{source('src/boot_continuity.py',86)} {evidence('BINDING_SCOPE_REFINEMENTS.json')}

预付需要256次scalar调用。guard640拒绝amount=256的普通scalar请求，生产range接口的固定task目前属于C02/C03/C04。可审查的位置为1095之后、1096启动C09之前，并显式借用有效C00票据检查原deadline，在所有路径恢复_TICKET。prepay_after与最终handoff.counter之间还应核对C09 controller初始一次合法Budget.visit。{source('src/guard.py',629)} {source('src/manager_recovery.py',462)} {source('src/guard_probe.py',99)}

旧v2的顶层schema实际为字段说明字符串，原文件hash和version可准确定位该历史对象。未来机器契约应使用唯一schema标识，将字段说明另置profile字段，并生成新待批摘要。{evidence('DRAFT_HASH_AND_STATUS_CHECK.json')}
'''

clause_table = '|条款|分类|参数|闭合范围|依赖|\n|---|---|---|---|---|\n'
for item in clauses:
    value = 'null' if item['parameter'] is None else json.dumps(item['parameter'],ensure_ascii=False)
    clause_table += f"|{item['id']} {item['title']}|{item['class']}|{value}|{item['closure_status']}|{'，'.join(item['dependencies'])}|\n"
reports['CAPACITY_LOGICAL_CLAUSES_APPROVAL.md'] = f'''# 容量逻辑条款审批稿

本次正式审议对象为{logical.name}，SHA-256为`{digest(logical)}`。每个B-C条款独立记录证明、源码、输入域、参数、闭合程度、依赖、差异文件、负向测试、适用范围和生效条件，全部用户决定为null。{link('待批条款JSON', logical)} {evidence('CAPACITY_CLAUSE_MATRIX.json')}

分类A为可单独选择的政策，分类B为有条件证明及其显式TCB/接线义务，分类C为数值null并阻断完整容量生效。

{clause_table}

B-C1的256是显式工程选择，合法witness延迟可能导致提前资源关闭。B-C2的263依赖全部生产者共享七类别位和256分类槽。B-C3按256×1322＋6×948＋1028=345148预留，包含紧凑JSON和LF。原始行已写字节与cursor已预扣数量分别核对。

B-C4可以单独审阅预付、预扣、append/fsync、completion及终态锁存的逻辑顺序。关闭空间的充分性继续由B-C6承担。B-C5要求257次前置拒绝的分类和主行增量为0，并明确caller终止和有限关闭责任。类B条款的审批文字须保留source profile、身份、稳定锁与存储语义条件。

可供用户选择的逻辑决定文字如下。

> 我批准B-C1的256次有限观察政策，并认可B-C2的263行、B-C3的345148字节条件推导，以及B-C4持久顺序和B-C5前置拒绝的逻辑要求。实际生效等待本轮列明的TCB、关闭子合同、源码许可及对应检查。完整容量和其余权限继续按独立条款审议。

> 我要求调整或退修所列逻辑条款，具体以条款ID和参数记录用户决定。

条款1至5的逻辑审批对象与B-C6至13的null阻断对象在同一审议表中显式列出。B1实施门当前为B1_BLOCKED_BY_CLOSE_RESERVE。{report('USER_APPROVAL_CHECKLIST.md')}
'''

null_table = '|条款|未决量|当前已知值/责任|解除条件|\n|---|---|---|---|\n'
for item in clauses[5:]:
    null_table += f"|{item['id']} {item['title']}|null|{item['existing_proof']}|{item['effectiveness']}|\n"
reports['CAPACITY_NULL_BLOCKERS.md'] = f'''# 容量null阻断表

**CAPACITY_CONTRACT_NOT_READY。** B_close、B_other、完整raw/ZIP/行政字节、单文件profile、完整内存/FD/IO/syscall及端到端时延继续为null或未闭合。旧条件数量4450/4451/4452作为来源记录，拟新生效cap等待实际差异集合。{evidence('CAPACITY_CLAUSE_MATRIX.json')}

{null_table}

本轮继承H≤52、core≤212、MR reason token≤38、Root marker≤194、健康B≤387和条件式。

\\[B_{{core}}\\le488421+368T+48B+23E+23\\sum V_j+52R_{{budget}}.\\]

这些来源子界为关闭合同提供输入，必要停止子集的总空间和隔离责任尚需可核验充分性证据。旧350166包含声明的局部main/cursor/首错/marker/staging，使用时按路径分区计量。{link('ResidualBounds最终界', PREVIOUS/'evidence/FINAL_BOUND_STATUS.json')}

B1直接门聚焦其耗尽路径。后续可以提出精确受限关闭子合同来证明主日志维护所需的停止信息与失败责任。完整admin/native量、全部其他raw和归档工作量仍是完整资格链依赖，本轮采用的图将这些层次各自标识。{evidence('DEPENDENCY_GRAPH.json')}

原合同的两组计数矛盾继续成立，native所需至少258成员而接受值为257，行政所需至少257文件而接受值为256。修改生效上限需要量化新版本、真实Δ和独立批准。{link('冻结UNSAT证明', PREVIOUS/'CURRENT_CONTRACT_UNSAT_PROOF.md')}
'''

reports['MR_CROSS_INSTANCE_APPROVAL_DECISION.md'] = f'''# MR跨实例规则独立审批

**MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE。** 当前用户批准记录缺席，user_approved=false、runtime_enabled=false、evidence_usable_now=false。原14条文本编号和JSON摘要已核对。{evidence('MR_APPROVAL_RECHECK.json')}

正式对象为MR-CROSS-INSTANCE-ADMISSION-FINAL-TEXT/1-DRAFT，版本C09-BoundClosure/review-1，SHA-256为`{mr['rule']['sha256']}`。原文本、source/input/lock、pair/A/B/use证据的责任继续按该对象审议。{link('原规则JSON', Path(mr['rule']['path']))} {link('原14条审批文本', Path(mr['text']['path']))}

|审批责任|具体信任范围和强制前提|
|---|---|
|可承认类别|独立A在一个特定原生受控服务故障下观察到的主自动关闭能力|
|当批B责任|boot、WORK/C00、真实C09、当前manager健康、预算/T0/期限、资源/监督和全部资格门重新证明|
|源与运行时|准确A/B source/input/execution pair、namespace-only AST映射、同boot和TCB条件|
|故障真实性|raw query/journal、单位/InvocationID/PID、原生故障码与时间、拒绝事实|
|关闭与退出|STOP/CLOSED、主自动路径、真实角色退出/组空、原预算保持、native/admin与独立raw oracle|
|有限使用|certificate位于A封存前像外，use_spec→新授权→use，目标B和nonce绑定|
|失效/撤销|版本/boot/源/作用域/授权变化或撤销导致失效，未知撤销状态拒绝|
|证据拒绝|必需缺件、fallback-only、UNKNOWN、重放、pair/use未填均拒绝该承认类别|

可直接采用独立决定文字。

> 我批准原14条MR有限跨实例承认原则及上述摘要。实际证书使用仍须满足原规则全部证据、pair与B当前资格条件。容量、源码和动态权限按独立决定办理。

> 我拒绝或退修该MR规则，并指定需要调整的原条款编号。

当前材料将用户决定字段保留为null。用户对B-C1至5的决定不改变该MR审批记录。{link('四权限待批对象', permissions)}
'''

reports['FOUR_PERMISSION_SEPARATION.md'] = f'''# 四类权限的独立审批记录

正式审议对象为{permissions.name}，SHA-256为`{digest(permissions)}`。四个用户决定字段均为null，当前执行许可为false。{link('权限记录JSON', permissions)}

|权限|本次可审对象|当前裁决|用户决定后仍需履行|
|---|---|---|---|
|CAPACITY_CONTRACT_APPROVAL|B-C1至5的有限政策/条件证明|CONDITIONAL_PASS，完整容量BLOCKED_NULLS|相应TCB/接线、关闭子合同和各null字段生效条件|
|MR_CROSS_INSTANCE_APPROVAL|原14条及原hash|PROPOSED_NOT_EFFECTIVE|实际原生A证据、精确pair、有限use与B当批重证|
|NATIVE_IMPLEMENTATION_AUTHORIZATION|两行为候选、输入绑定、明确测试/oracle/回退|B1_BLOCKED_BY_CLOSE_RESERVE|先满足本轮B1直接门，再取得准确文件/函数/检查授权|
|FULLCHAIN_DYNAMIC_AUTHORIZATION|完整新链的独立执行申请|BLOCKED|完整合同、集成锁、MR所需材料、原件/资源/当前preflight条件和用户执行许可|

审批值相互独立。逻辑政策决定只记录条款采纳，MR决定只采纳有限证据承认原则，源码决定固定允许差异，动态决定固定新实例/argv/限额和检查范围。实际RESOURCE_GATE_PASS由获准的当批校准产生，F1/F4随后受它支配。{evidence('DEPENDENCY_GRAPH.json')}

维护请求当前为待审且eligibility=false。提前把源码许可记录成已批准会跳过本轮第六节明确的关闭条件。最终文本将“材料范围具备审查对象”和“当前实施准入BLOCKED”同时记录。{link('B1维护请求', maintenance)}
'''

reports['FULLCHAIN_ADMISSION_DEPENDENCY.md'] = f'''# 完整资格链依赖图

旧成功验收目标维持CURRENT_CONTRACT_UNSAT。新B1局部实施门为B1_BLOCKED_BY_CLOSE_RESERVE，完整资格链还需要其他容量、归档、MR及新鲜授权输入。下图展示证明/审批和实际运行事实的产生顺序。{evidence('DEPENDENCY_GRAPH.json')}

```mermaid
flowchart TD
  L[有限逻辑条款] --> B1[B1实施门]
  S[精确文件与语义计划] --> B1
  C[耗尽路径关闭子合同] --> B1
  B1 --> N[独立源码修改许可]
  N --> I[隔离候选与授权检查]
  I --> D[准确source/input/测试差异]
  CAll[完整关闭与其他对象profile] --> K[完整版本化容量合同]
  D --> K
  O[归档与独立oracle资源证明] --> K
  K --> A[完整归档与原件接受合同]
  M[独立MR原则及实际A/pair/use] --> X[完整链独立执行许可]
  A --> X
  D --> X
  X --> P[新身份/锁与当前preflight]
  P --> Q[当批资源校准]
  Q --> R[RESOURCE_GATE_PASS]
  R --> F[F1/F4条件执行]
```

RESOURCE_GATE_PASS是校准结果。完整执行许可的静态申请需先具备相应限额/来源/监督/原件条件，获准后当前运行内完成校准，模型入口再核对实际PASS。该顺序避免把一个未来校准结果作为启动该校准本身的先决事实。{source('src/guard.py',530)}

现有终态reader负责原件/身份/窗口/退出与既有ZIP验证，5秒属于该只读阶段。原生builder的运行时核查、停止等待和ZIP/hash另有工作量责任。行政30秒属于Linux child，host后层ZIP/hash也需完整合同。{source('src/terminal_evidence.py',193)} {source('src/guard.py',993)} {source('host/startup_finalize.py',52)}

当前B1图的直接缺口限定在必要停止信息保留与耗尽安全接线。完整容量中的其余null继续作为后层门记录。任何放行应引用精确子合同和边界，现有记录无法据此解除当前B1门。{evidence('B1_INDEPENDENCE_GATE.json')}
'''

impact = read_json(EVIDENCE/'RESOURCE_IMPACT_MODEL.json')
reports['RESOURCE_AND_TIME_IMPACT.md'] = f'''# B1资源与时间影响

本次为语法长度和源码调用次数分析，新增执行数为0。预付、local quota和完整关闭/归档各有原件与成本责任，准确模型见资源文件。{evidence('RESOURCE_IMPACT_MODEL.json')}

|组件|条件成本|来源与范围|
|---|---:|---|
|Root健康预付|256次scalar事务，global R增加256|当前calibration/global限额和有效C00 ticket约束|
|新增global journal|512行，编码字节≤122112|PREPARED每行≤238、COMMITTED≤239，含LF|
|intent数据写|512次、字节≤142592|RootIPC pretty编码，P≤278、C≤279|
|counter数据写|256次×8=2048 bytes|同一原counter持久递增|
|上述预付数据总量|1280次数据写，≤266752 bytes|两个intent、两个journal、counter各一项|
|上述Root预付fsync|2304次|每事务两次跨目录intent各3次sync、journal两次、counter一次，共9次|
|旧v2 local模型|cursor1198、更新522，局部retained350166、写量971216、durability1316|仅旧声明集合和正确codec/调用/失败owner条件|

预付行长由guard597的compact codec、624的LF、658/670固定record及已有数值ABI推导。RootIPC的file/destination/private三次sync用于两个Root intent发布。该表按健康成功前缀计算，失败前缀保留已发生写入和预算消耗，完整失败责任继续计入关闭子合同。{source('src/guard.py',597)} {source('src/guard.py',624)} {source('src/root_ipc.py',115)}

local1316包含主日志及声明marker的一些既有写路径，预付2304为新增加的256事务成本。需要准确diff才能给出与原程序的净增量和全系统syscall、heap、FD、读写/存储成本。新增quota源输入、五个未来评审对象及其结果/失败staging须按真实保存层分别计数。当前full_runtime_raw_delta和新export/member cap为null。

上轮访问模型68498加新预付256为68754，尚需新增检查Δ。各phase和原全局1m/calibration100k及原票据deadline继续约束任何未来运行。旧MR256属于独立预付责任，额度转移没有本轮审批对象。主log345148与预付journal成本均需进入完整字节合同。

256次scalar会增加顺序持久化延迟。已有5/30/300/1800窗口、Root停止策略和AS/TasksMax并不提供所需动作的最坏成功时延。当前全部TCB/文件系统/syscall latency与完整native/host时间仍未闭合。{link('冻结时间裁决', PREVIOUS/'WALL_TIME_ASSUMPTIONS.md')}

H≤52/core≤212来自原冻结角色图。候选在相同线程图内增加scalar调用仍需按精确diff复核单调HALTED入口和异常包络，当前源证明保持其原作用域。原件完整、真实退出、UNKNOWN和所有资格来源均为后续检查保持式。
'''

reports['GENERAL_BASELINE_AND_SEPARATION.md'] = f'''# 强G比较与原创性门

所有本轮B1工程候选为**COVERED_BY_G**。输入族为同一handoff的n次缺witness观察、并发token重放及预扣/append/关闭持久化失败。度量为原始行/字节、持久写次数、至多一次额度和必要关闭证据完整性。{evidence('GENERAL_G_COMPARISON.json')}

|候选|适用的成熟通用方法G|预测严格差距|
|---|---|---:|
|有界追加日志|固定行/字节slot、sink统一计量|0|
|原子额度计数|串行读改写和持久单调counter|0|
|预付持久化|现有持久预留核心与local allowance|0|
|幂等task/token|绑定交易ID、one-use类别和重放拒绝|0|
|固定reason|有限typed控制码及明确raw来源|0|
|独立关闭预留|保留必要空间、有限首错与失败责任|0|
|manifest与版本容量|标准逐件hash/size/集合检查和版本化输入|0|

未构造使最强G必须付更高必要代价的实例，STRICT_SEPARATION_INSTANCES=0。当前范围为标准工程维护的审批规划，架构原创性状态保持COVERED_BY_G。任何新研究机制的实现仍先满足用户的可证伪分离声明要求。现行IMPLEMENTATION_GATE=CLOSED，源码许可按独立审批处理。
'''

check_table = '|决定项|可选择文字/范围|当前记录|\n|---|---|---|\n'
for item in clauses:
    action = '可对所列政策或条件推导单独采纳/退修' if item['class'] in ('A','B') else '记录null及阻断，待充分材料后审议生效'
    check_table += f"|{item['id']}|{action}|user_decision=null，approved=false|\n"
reports['USER_APPROVAL_CHECKLIST.md'] = f'''# 用户逐项审批清单

用户可以对以下对象分别作出决定。当前所有user_decision均为null，审批状态记录准确绑定文件摘要。{evidence('APPROVAL_OBJECT_BINDINGS.json')}

|对象|SHA-256|本轮状态|
|---|---|---|
|容量逻辑条款|{digest(logical)}|部分条款可独立审议，完整容量未生效|
|B1维护请求|{digest(maintenance)}|B1_BLOCKED_BY_CLOSE_RESERVE，源码许可尚未获得|
|四权限记录|{digest(permissions)}|四项决定各自待批|
|原MR14条|{mr['rule']['sha256']}|PROPOSED_NOT_EFFECTIVE|

{check_table}

B-C4中持久顺序可以被采纳为逻辑要求，关闭空间数字继续由B-C6保留null。采纳B-C1至5时，记录应保留相应依赖与生效条件。完整B1源码准入需先满足本轮第六节的必要停止信息保留条件，再引用准确文件/函数和测试授权。

对于当前B1维护请求，可直接采用决定文字。

> 我接受本次两行为候选、接口依赖和语义计划的范围审查，记录B1_BLOCKED_BY_CLOSE_RESERVE。待必要关闭子合同具备充分证据后，再单独审议本请求的源码修改许可。

> 我退修该维护请求，并列明需要调整的文件、语义步骤或关闭依赖。

MR可以引用原14条单独作原则决定。当前完整资源资格链审批对象仍需容量、归档、MR所需材料、集成锁和新的执行申请。任何缺证据/部分原件/UNKNOWN都按原始事实记录。

对于完整动态请求，可直接采用下列独立记录。

> 我暂缓完整资格链动态审批，待完整容量合同、所需MR规则/证据、集成源锁及新实例静态准入条件满足后，再审议具体执行申请。

> 我拒绝当前完整动态申请，并指定退修的合同或证据条件。

四类表单各有独立选项和selected=null字段。源码与动态表单当前只记录范围审查、延期、退修或拒绝，实施准入条件按本轮门保留。{link('四类正式决定表单', permissions)}

本轮完整交付后停止，等待用户选择条款与后续授权。具体闭合材料或新授权到达前，同一15项证明范围维持上轮终结状态。{report('FOUR_PERMISSION_SEPARATION.md')}
'''

gates = [
    {'id':'BG-1','status':'PASS_STATIC','basis':'16个既有文件的hash/函数/语义/保持式/测试/依赖/回退及5个明确未来位置已建立'},
    {'id':'BG-2','status':'BLOCKED','basis':'B1_BLOCKED_BY_CLOSE_RESERVE，必要停止信息剩余空间、隔离及失败责任尚缺充分子合同'},
    {'id':'BG-3','status':'CONDITIONAL_PASS','basis':'256政策、263/345148条件及TCB、caller/sink、预付/持久/关闭生效边界明确'},
    {'id':'BG-4','status':'PASS_STATIC','basis':'原14条、原SHA、信任/当批重证/失效/拒绝完整，用户批准仍待记录'},
    {'id':'BG-5','status':'PASS_STATIC','basis':'四类用户决定均null，当前执行/生效状态false，权限无隐式传递'},
    {'id':'BG-6','status':'PASS_STATIC','basis':'标准G覆盖全部候选，严格分离实例0，原创性/实施门状态明确'}]
gate_table = '|门|状态|裁决依据|\n|---|---|---|\n'
for item in gates:
    gate_table += f"|{item['id']}|{item['status']}|{item['basis']}|\n"
reports['FINAL_DECISION.md'] = f'''# B1审批与实施准入最终裁决

**本轮审批材料准备完成，B1实施准入为BLOCKED，正式状态B1_BLOCKED_BY_CLOSE_RESERVE。** 256、263、345148及持久顺序/前置拒绝可以作为独立逻辑决定对象，完整容量和源码实施生效仍受明确条件支配。

{gate_table}

真实调用链为guard799–800到observe_exit254–277，在H锁内进入分类和event。当前caller只消费VERIFIED/CLOSED。候选仅增加EXHAUSTED返回值会回到循环，提前映射CLOSED会进入close=False路径。最小语义计划选择固定现有异常衔接，H释放后到808和817两层M.abort，并计入全部停止/回收收据。这些义务覆盖全部sink和caller。{report('B1_SEMANTIC_DIFF_PLAN.md')}

本轮第六节要求主额度耗尽时必要停止信息有受信保留来源。当前RootIPC/BC.Store给出权限和发布持久顺序，必要关闭子集的剩余空间/隔离/失败责任仍未获得充分证明。B_close=null、B_other=null和全量native/admin资源值保持未决。较小且充分的B1关闭子合同可以成为直接门的证明输入，其余完整容量null继续按后层门处理。{report('B1_SCOPE_AND_DEPENDENCY.md')} {report('CAPACITY_NULL_BLOCKERS.md')}

范围已收敛为c09_handoff.py、guard.py两份行为候选及其契约/manifest/静态审查绑定。manager_recovery.py为必须核验的现有接口依赖，当前MR改动未选定。runtime_tree_lock绑定标准库，当前作为只读TCB输入。五个未来quota/test/oracle/harness/review-lock位置均为PROPOSED_ABSENT，其独立目录名为本轮规划建议。{report('B1_FILE_LEVEL_MAINTENANCE_REQUEST.md')}

旧v2工件的顶层schema值为profile文义字符串，原hash7effe4e39e1eae665153bae4e16f7d2a20513a574fc26a4873ded5a81ef680ae已核对。新机器契约的唯一schema标识为未来输入义务。当前实际关闭/容量草案位于CloseReserve目录，ResidualBounds的DECISION_BINDINGS给出其准确引用。{evidence('DRAFT_HASH_AND_STATUS_CHECK.json')}

资源影响已包含新预付的512 journal行、条件字节122112、Root健康2304次fsync与完整预付数据写上界266752。旧v2 cursor1198/更新522及local1316仍只适用其原声明集合和调用/codec前提。完整I/O、内存、FD、syscall和端到端时间继续未闭合。{report('RESOURCE_AND_TIME_IMPACT.md')}

四类用户决定均待记录。MR原14条规则摘要9c7524d7af3530b27f4c35d4fef92d9f2f3e431633967b555483b0b58085d069，状态PROPOSED_NOT_EFFECTIVE。现行完整成功链CURRENT_CONTRACT_UNSAT由已证明的计数矛盾维持。主逻辑审批与MR原则审批可以分别进行，B1源码许可及完整动态申请当前仍受阻断。{report('USER_APPROVAL_CHECKLIST.md')} {report('FULLCHAIN_ADMISSION_DEPENDENCY.md')}

原草案、源码/输入锁与历史执行索引经过摘要核验。旧容量SHA为44308e849c9ea2451cc1eb1443c00b88a874f523739d4129c202446132246d07，旧关闭SHA为44980a113bda747f5e4e64ce47d6b782290a47e8bd3699f59623ecb0b045714a。两份原对象使用user_approved=false，approved字面字段缺席，effective/runtime_enabled=false。新审批对象的approved/user_approved/effective/runtime_enabled也均false，user_decision=null。{evidence('DRAFT_HASH_AND_STATUS_CHECK.json')} {evidence('APPROVAL_OBJECT_BINDINGS.json')}

9867份历史文件与此前587份交付工件合计10454件旧文件、64运行源/输入和原导航后缀纳入最终交付核验。本轮产出12报告、13条款矩阵、16既有文件/5未来位置表、10步语义计划、15项检查义务及依赖图。运行机制/预算核心/C09/MR/Guard/native/admin/gate/D1/D2改动0，可运行补丁0，新批次/T0/预算0，WSL/动态/真实故障/F1/F4均0。{evidence('DELIVERY_CHECK.json')}

本轮按请求完成后停止。下一步等待用户逐条决定逻辑条款、独立MR原则和后续申请，当前B1门记录与全部null责任随审批对象保留。{report('EVIDENCE_INDEX.md')}
'''

for name, body in reports.items():
    heading, content = body.split('\n',1)
    (OUT/name).write_text(heading+'\n\n'+intro+content.lstrip()+footer,encoding='utf-8')

index = '# B1审批研究证据索引\n\n'+intro
index += '本轮结果为B1_BLOCKED_BY_CLOSE_RESERVE，逻辑条款与独立权限材料待用户决定。\n\n'
for name in reports:
    index += '- '+report(name)+'\n'
index += '\n机器审查与绑定文件\n\n'
for name in ['INITIAL_INTEGRITY.json','DRAFT_HASH_AND_STATUS_CHECK.json','FROZEN_SOURCE_LOCK.json',
             'PRIOR_ARCHIVE_RECHECK.json','FUNCTION_SOURCE_INDEX.json','CAPACITY_CLAUSE_MATRIX.json',
             'B1_FILE_PLAN.json','FUTURE_FILE_SLOTS.json','SEMANTIC_DIFF_STEPS.json','B1_INDEPENDENCE_GATE.json',
             'DEPENDENCY_GRAPH.json','B1_TEST_OBLIGATIONS.json','BINDING_SCOPE_REFINEMENTS.json',
             'RESOURCE_IMPACT_MODEL.json','MR_APPROVAL_RECHECK.json','APPROVAL_OBJECT_BINDINGS.json',
             'GENERAL_G_COMPARISON.json','DELIVERY_CHECK.json']:
    index += '- '+evidence(name)+'\n'
index += '\n'+link('逻辑审批对象',logical)+' · '+link('B1维护请求',maintenance)+' · '+link('四权限对象',permissions)+footer
(OUT/'EVIDENCE_INDEX.md').write_text(index,encoding='utf-8')
save('FINAL_GATE_DECISIONS.json',{'gates':gates,'overall':'B1_BLOCKED_BY_CLOSE_RESERVE',
                                 'reports_complete':12,'user_approval_received':False,
                                 'task_status':'CONTRACT_REVIEW_AND_PLANNING_DELIVERED'})
print(json.dumps({'reports':len(reports),'index':1,'B1_admission':'B1_BLOCKED_BY_CLOSE_RESERVE',
                  'logical_sha256':digest(logical),'maintenance_sha256':digest(maintenance)}))
