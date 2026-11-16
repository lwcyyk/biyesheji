"""Write requested research reports only. No mechanism implementation or execution."""
from RESEARCH_AUDIT import ROOT, OLD, OUT, E, RUNTIME, read, sha

def link(label,path,line=None):
    target=str(path).replace('\\','/')+(f':{line}' if line else '')
    return f'[{label}]({target})'
def src(name,line): return link(f'{name}:{line}',RUNTIME/'src'/name,line)
def ev(name): return link(name,E/name)
def doc(name): return link(name,OUT/name)
def prior(name): return link(name,OLD/name)

Q=OUT/'proposals/C09_PENDING_QUOTA_FINAL_PROPOSAL.json'
QHASH=sha(Q)
M=OLD/'proposals/MR_CROSS_INSTANCE_FINAL_RULE_DRAFT.json'
MHASH=sha(M)
passport=('## Material Passport\n\nDCL-R6-C09-PendingQuota-Closure；PendingQuota-Closure/review-1；'
          '2026-11-16（Asia/Shanghai，承接11月15日开始的审查）；冻结源码、历史原件、序列化代数与逻辑合同的静态审查。'
          '验证方式为 ANALYZED；原生动态验收未开展。\n\n')
footer=('\n\nRESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；'
        'PASS_BOUNDED=[]；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；'
        'STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。\n')
reports={}
reports['C09_PENDING_PATH_AUDIT.md']=f'''# PENDING生产路径完整审计

结论：**PQ-1=PROVED（冻结64对象、封闭原生调用域）**。唯一原生PENDING写入位置是{src('c09_handoff.py',277)}，统一进入{src('c09_handoff.py',75)}的event sink。全源AST和文本清单见{ev('STATIC_PRODUCER_CENSUS.json')}，含所需全部生产者字段的13行矩阵见{ev('PRODUCER_CONTEXT_MATRIX.json')}。

|producer_id|实际位置与进程|触发/状态变化|每次主日志追加|重试/并发/持久化|现行配额|
|---|---|---|---:|---|---|
|P01|Receiver.observe_exit，Root独立停止器，252–277|COMMITTED首次推进EXIT_OBSERVED；缺witness后保持revision4|1 CHECK，可为PENDING|H生命周期锁；同一Receiver反复进入；append/full write/fsync|缺少次数与总字节检查|
|P02|publish，85–89；Sender/Receiver/恢复scheduler|六类进度事件，各自前置状态见记录数证明|1 stage|同一生命周期锁；log先持久，随后state发布|依赖单次执行；崩溃重放需额外合同|
|P03|sender_prepare，189–196；初始Sender|持久COMMITTED回包核验成功|1 ACK|同锁；当前业务调用一次；等待连接不会重做ACK日志|缺少类别持久去重位|

{src('c09_handoff.py',79)}使用Root0600、O_APPEND/O_NOFOLLOW、紧凑排序JSON和LF，逐行fsync；{src('guard.py',121)}的_full只有一次os.write，短写抛异常。O_APPEND保护文件偏移，不提供配额原子性或崩溃事务。

|必须审查的上下文|源码与结论|
|---|---|
|初次/重复交接、重复task_id|{src('c09_handoff.py',172)}拒绝已有handoff；{src('c09_handoff.py',221)}只有PREPARING分支发布READY/COMMITTED，重复PREPARE返回既有commit。原生日志无task_id；重复对象是handoff_id，观察ordinal属于待批合同。|
|ACK等待、Receiver确认|{src('c09_handoff.py',138)}的RPC/connect/send等待本身不调用event；错误回包含str(exc)，归入其他流字节缺口。|
|Launcher退出、waitpid|{src('guard.py',799)}就绪pidfd触发观察；{src('guard.py',1225)}和{src('c09_handoff.py',297)}产生独立waitpid/witness文件。它们不给PENDING自环收费。|
|超时、Root恢复、故障恢复|{src('c09_handoff.py',123)}与classify期限拒绝；{src('c09_handoff.py',343)}只增加RESUMED stage；{src('manager_recovery.py',251)}监督Root owner，不增加原生PENDING。|
|ManagerRecovery|{src('manager_recovery.py',51)}写mr_events；REVIEW_PENDING和mr_close_attempts均属独立生产族。PENDING字符串相近不构成同一sink。|
|STOP_REQUEST、CLOSED与异常清理|{src('guard.py',545)}、{src('guard.py',749)}及{src('manager_recovery.py',317)}写停止/MR/回收对象，不递归调用event。STOP可在在途检查后出现；CLOSED经H锁阻止新入口。|
|native seal前后|{src('guard.py',993)}等待写者退出，TR检查关闭、角色退出与组空；封存仅哈希/复制，不产生PENDING。仅CLOSED存在尚不足以宣称源已静止。|
|行政finalizer|{src('startup_lifecycle.py',412)}只读导出；{link('startup_finalize.py:52',RUNTIME/'host/startup_finalize.py',52)}构造独立行政包。它们无原生PENDING写点。|
|C09H34|{src('c09_regression.py',59)}固定34 jobs/204事件/最大单job8步，输出各自JSON；{src('c09_oracle.py',42)}核对收费。其synthetic PENDING和原生忙等路径分别计量。|

同一原生观察只调用一次event；另有首次EXIT_OBSERVED生命周期行。不同观察合法产生新CHECK；重试/恢复的重复追加风险须由持久token与禁止模糊重放条款约束。HANDOFF_FAILED只在STAGES声明，当前无原生publish调用。{ev('H34_STATIC_INPUT_REVIEW.json')}记录合成输入审查，本轮执行次数0。

历史8份原件逐字节匹配CalDiag原始导出锁；24行/27,144 bytes，17 PENDING＋1 VERIFIED＋6个前缀stage/ACK，未发生RESUMED。17条均同handoff/revision4，区间全局journal追加0行。{ev('HISTORICAL_RECHECK.json')}保留实际原件路径、hash、直接锁核验及统计；这些数据只证明那次实际轨迹。
'''
reports['C09_OBSERVATION_SEMANTICS.md']=f'''# 观察语义、重复轨迹与耗尽规则

现行代码的“观察”是{src('guard.py',800)}调用Receiver.observe_exit；classify仅在{src('c09_handoff.py',276)}计算一次，随后一条CHECK。poll/socket等待、已有VERIFIED的早返回和已CLOSED的早返回均不属于新分类。现行classification_count只约束成功推进HANDOFF_VERIFIED，PENDING返回时保持0。

最小轨迹族X_n：一个有效handoff，Receiver在Sender活着时取得pidfd；COMMITTED/ACK已经持久，Sender退出23；Root父进程存活，waitpid见证发布暂延。在deadline正余量内，Receiver重复“检查相同绑定/计数→witness缺→PENDING→append/fsync”。首次stage从revision3变4，此后handoff/revision4/classification_count0/resume_count0/R均不变。就绪pidfd保持就绪，PENDING分支没有清fd或else sleep，见{src('guard.py',781)}及{src('c09_handoff.py',252)}。

X_257是反驳现行256政策界的具体合同调度前缀；它仅改变调度次序，原生重放0。量词限于底层表示、存储和时间环境允许的有限n。源码合同未给每轮可靠最短耗时，因此12秒窗口无法推导256上界。Linux signed64 off_t等附加假设只给极粗表示界；上一轮n=30,532的固定骨架超过32MiB示例继续作为抽象规模反例，当前未验证它在实际12秒内可达。{prior('evidence/COUNTEREXAMPLE_FAMILY.json')}、{prior('evidence/REPRESENTATION_LIMIT_CAVEAT.json')}保持原字节。

待批v2将一次“新观察尝试”定义为：当前认证Receiver通过基本身份/终态门后，进入一次新的observe_exit检查。**在完整check_base/事实采集/分类前持久消费1个分类槽**；随后失败也烧掉该槽。异实例、过期、重复ordinal、已停止和缓存VERIFIED返回获得0个新槽。每个通过准入的不同ordinal消耗一次；相同ordinal重发只拒绝/返回既有状态，不再append，也不重新发额度。

分类额度256覆盖所有已准入尝试，包含产生PENDING、VERIFIED、FAILED、在事实构造或I/O阶段失败的尝试。因此“256个成功接纳的日志行”不能代替尝试计数。失败尝试可能0行或1个保留的部分行，行数始终受已预扣槽数约束。

第256次若仍PENDING：完整原始facts/结果先写入已预留槽并fsync，持久完成cursor并进入EXHAUSTED_FAIL_CLOSED，再保留单份固定失败摘要和请求停止。第257次获得0额度、0分类、0主日志、0重复紧急记录。若第256次得到VERIFIED，终态锁存先持久，再解锁回收；其余源码资格保持。任何有限配额都可能先于一个合法的延迟witness耗尽，合同接受资源耗尽关闭，未给成功活性保证。

正式条款和宽度示例见{link('C09配额v2草案',Q)}。当前代码未接线，状态为RECORD_BOUND_CONDITIONAL / PROPOSED_NOT_EFFECTIVE。
'''
reports['C09_RECORD_COUNT_BOUND_PROOF.md']=f'''# 256次观察与263条主日志的记录数证明

**PQ-2=CONDITIONAL_PROVED；现行256上界为COUNTEREXAMPLE；RECORD_BOUND_CONDITIONAL。** 以下归纳针对待批合同。当前冻结程序继续保留PENDING自环。

设A为已持久预扣的分类尝试，P为完整PENDING行，T为终态CHECK，E为生命周期行，K为ACK行，U为未完成的部分行/已烧掉空槽。取“记录”时同时约束完整行和占用槽，避免把短写尾部遗漏：

\\[P+T+U\\le A\\le256,\\quad E\\le6,\\quad K\\le1,\\quad N_{{main}}\\le A+E+K\\le263.\\]

T≤1要求认证单Receiver及终态锁存；成功路径T=1⇒P≤255。失败路径允许P=256；它停在EXIT_OBSERVED前缀，通常仅4个stage＋1ACK，故261行已是该耗尽轨迹的更紧界。263为所有路径的共同包络。对完成恢复的正常轨迹，旧源码公式N=P＋8；代入成功P≤255得到263。

|额外类别|实际调用位置|固定上界的来源|崩溃/并发条件|
|---|---|---|---|
|HANDOFF_PREPARING|{src('c09_handoff.py',187)}|sender_prepare已有state即拒绝|持久类别位先扣；发布中断后关闭|
|HANDOFF_READY|{src('c09_handoff.py',226)}|只从PREPARING进入|同锁/类别位；重复PREPARE不给新stage|
|HANDOFF_COMMITTED|{src('c09_handoff.py',232)}|同一PREPARE分支提交一次|同锁/类别位；commit原件保留|
|LAUNCHER_EXIT_OBSERVED|{src('c09_handoff.py',262)}|只从COMMITTED进入；PENDING维持revision4|同锁/类别位；重放时烧掉的位保持|
|HANDOFF_VERIFIED|{src('c09_handoff.py',286)}|classification_count从0变1|终态锁存先于解锁cleanup，随后类别位一次|
|RESUMED|{src('c09_handoff.py',343)}|VERIFIED、resume_count0与AWAIT等门|类别位先扣；状态发布模糊即关闭|
|SENDER_ACK_OBSERVED|{src('c09_handoff.py',196)}|原生sender_prepare业务调用一次|独立第7位；相同token不得再次append|

公式可写为f(O_max,E_max,R_max)=O_max+E_max+ACK_max+R_max=256+6+1+0。R_max=0只指额外主日志恢复/补充行：当前Root恢复仅RESUMED，HANDOFF_FAILED无原生发布；MR/STOP/回收文件属于独立集合。未来增加生产点或恢复重试必须重审R_max和字节表。

归纳不变量：每次授权写入先在同一个durable cursor递增ordinal和reserved/debited计数；七个类别位只从0变1，A只增不减。所有角色用同一稳定H锁，锁内重新读取cursor，检查终态并持久预扣，完成后最多一次os.write。每个被消耗token只对应一次写入尝试；部分写入保留，整行重试关闭。由注入映射“写入尝试→不同持久槽”得到N≤263。

并发临界点为**预扣cursor的原子发布及其必需fsync成功，且H锁尚未释放**。最终分类另有completion写入，在释放锁去stop_tree前锁存TERMINAL_LATCHED。最后一额只会发给第一个完成预扣者；第二个看到A=256或终态，获得0额。稳定锁inode、受信Root、无回滚和存储持久性都是显式条件。

最小反例CE-LAST：A/B都先读255，分别append，再写256，得到257次记录；CE-TERMINAL：A写VERIFIED解锁cleanup，B在VERIFIED stage落盘前再写VERIFIED；CE-REPLAY：stage日志fsync成功、state落盘前崩溃，恢复者重做publish。三者说明仅有计数变量/状态名/顺序执行论证不足以证明并发及恢复。见{ev('CRASH_AND_CONCURRENCY_MATRIX.json')}。这些是静态交错，未运行测试。
'''
reports['C09_RECORD_SIZE_BOUND_PROOF.md']=f'''# 逐字段单行字节上界

**单行结论为CONDITIONAL_PROVED。** {src('c09_handoff.py',15)}使用sort_keys、逗号/冒号紧凑分隔、默认ensure_ascii=True；{src('c09_handoff.py',83)}追加LF后UTF-8编码。以下长度均含1字节LF。完整模板、骨架和调整量见{ev('RECORD_BYTE_ALGEBRA.json')}；新实例尚未签发，batch14只作宽度样例。

|字段族|最大编码长度|条件与编码责任|
|---|---:|---|
|event/verdict/阶段|固定枚举；最长stage22|取现行六种stage、ACK和EXIT_CLASSIFICATION_CHECK；额外键需重审|
|batch_id / execution_mode|7 / 27|冻结ASCII白名单；未来身份超长时重算|
|handoff_id、commit摘要、window四摘要|各64|SHA-256小写hex；引号/字段键已计骨架|
|boot_id（identity/window/stamp）|各36|规范UUID，源kernel及绑定；白名单ASCII|
|PID / start_ticks|10 / 20|正pid_t32、u64十进制；布尔冒充整数需拒绝|
|utc_ns|20|受审signed64十进制；符号已计|
|T0/deadline/stop_at/boottime/now/expires|各25|有限binary64 JSON宽度；未来须在编码前验证数值/类型和宽度|
|revision|1|范围1至6；重复PENDING保持4|
|facts布尔|每项≤5|13个固定布尔键，true4/false5；无递归容器|
|witness|null4或退出整数≤11|直接parent waitstatus来源；类型和范围需固定|
|task_id、错误码/errno、systemd原文、traceback引用、校验头|主行中均无此字段|这些对象位于commit/resources、socket错误流、MR或停止/封存族；独立计量|

公共数值调整：PID从1变10增加9；start_ticks增加19；utc_ns增加19；window三浮点＋boottime共4项各增加24，合计143。分类再含now/expires两浮点，增加48。模板骨架已包括所有字段名、引号、括号、嵌套、逗号/冒号和LF。

|类别|骨架与调整|上界bytes|
|---|---|---:|
|缺witness、durable ACK真实的PENDING|1107＋143＋48|1298|
|通用分类schema|对全部13布尔取false、witness取11字符退出整数后重算|1318|
|合同分类预留槽|沿用既有1322，较通用schema代数多4|1322|
|stage最大|805＋143|948|
|ACK|885＋143|1028|

六种stage逐项上界为943、939、943、948、942、933，总5648；合同仍按6×948=5688预留，保留40字节余量。1298仅用于正常缺见证自环，其他标量事实组合一律按1322；本轮把这一证明范围写明，容量安全无需依赖1298覆盖全部异常分支。

字符串白名单中没有引号、反斜线、控制字符、换行和非ASCII，因此字符长度等于UTF-8长度。若未来接纳任意Unicode，JSON ensure_ascii=True每code point最多12个ASCII字节，当前表须重新计算。通用event(kind,**data)本身可接任意键值，未施加schema/字宽检查；封闭调用者与ABI前提为当前证明边界。

主机研究脚本仅按JSON语法统计固定模板与最大十进制宽度，未导入运行源码；主机Python版本不构成原生3.12兼容验收。未来实现须把全部profile检查置于不受限序列化分配之前，完成原生宽度和异常回归，才能取得源码约束证明。
'''
reports['C09_TOTAL_BYTE_BOUND_PROOF.md']=f'''# 主日志预留与全PENDING证据字节裁决

**PQ-3=PARTIAL；PENDING_BYTE_BOUND_PARTIAL。** 345,148 bytes可以作为受审主日志的条件预留，完整PENDING及关闭/封存证据仍需独立项。当前运行源码缺次数配额，当前总量为PENDING_BYTE_BOUND_UNRESOLVED。

从真实3个原生调用点和六个stage得到：

\\[B_{{main,reserved}}=256\\times1322+6\\times948+1\\times1028=338432+5688+1028=345148.\\]

主行LF已包含；metadata/reserve不能隐含为0。全部schema采用更紧1318及实际六stage时可得344084的条件包络，合同继续保留345148。正常ACK缺witness自环的成功路径上界255×1298＋1322＋6×948＋1028=339028；它的6120字节余量只用于比较，额度已预扣且不退款，未给关闭生产者发放新授权。

|需覆盖对象|345148中的位置|本轮精确结果|
|---|---|---|
|最多263个主行/部分尾部|已含256分类槽、6stage槽、1ACK槽|CONDITIONAL_PROVED|
|quota cursor、类别位、终态锁存、预付桥接|独立元数据|v2 cursor≤1198；旧956缺新字段与持久完成责任|
|首份失败摘要|独立紧急对象|≤334；全局只写一次，固定代码，原始facts仍在主行|
|STOP_REQUEST / CLOSED|独立既有路径|限定ASCII reason≤43、RootIPC原编码下各≤189，稳定标记合计预留378缺席于345148|
|必要恢复/回收收据|独立stop_result、mr_close_state等|含snapshot/errors/roles；整体最大字节尚未闭合|
|native seal输入|原ACK/commit/witness/预算/角色退出/阶段/终态等|主日志之外；完整输入集合仍有未决项|
|native/admin manifest、ZIP、host原始流|独立派生与复制层|全局容量另算；345148从未覆盖这些对象|

新cursor按旧字段加lifecycle_mask、terminal_latched、ordinal、prepay_before/after、journal-prefix bytes/hash构造封闭schema：骨架1107＋三浮点72＋journal字节计数19=1198。七类位提供生命周期幂等；每次分类追加后有一笔持久completion，终态先锁存再解锁cleanup。旧合同保留原字节，新字段及工作量只存在于v2待批附件。

限于cursor/首错/两个标记的最小子项，稳定保留量为345148＋1198＋334＋2×189=347058；再保留两份失败cursor staging、一份失败摘要staging、两个标记失败staging，得到：

\\[B_{{local}}\\le345148+3\\times1198+2\\times334+4\\times189=350166.\\]

相对主日志的独立子项差额为5018；其中378是STOP/CLOSED稳定预留。相对旧348684局部提案的变化为1482。**350166仅为明确列出的局部集合界**；stop_result、MR、seal/admin尚有正的附加责任，完整关闭差额写作5018＋B_other_required_close＋B_seal/admin，后两项UNRESOLVED。这里保留345148原数，逐项说明缺失，不把新子项合计当作完整证据配额。

{ev('QUOTA_AND_MINIMAL_MARKER_ALGEBRA.json')}给出每个模板和编码等式。逻辑reservation与磁盘物理预分配分别登记，当前无物理保留证明。内核/存储EIO下，即使字节额度足够也可能无法保存标记，真实状态保持UNKNOWN。
'''
reports['C09_OVERFLOW_AND_CLOSE_RESERVE.md']=f'''# 主额度耗尽与关闭保留区

**PQ-4=UNRESOLVED；CLOSE_RESERVE_BOUND_UNRESOLVED。** 已精确划分主日志、局部紧急对象和完整关闭链；完整关闭证据空间及系统调用结果仍缺证明。

题设“256次观察、263条主记录、345148预留都已耗尽”在配额意义上可作为最坏包络。按正常typed schema，实际文件通常小于预留量；失败PENDING路径也达不到六个成功进度stage。安全策略仍按预留余额0处理，保留字节不回收，不把可观察余量当成新授权。

|分区|允许事件/角色|稳定数量与单项界|重入/失败行为|
|---|---|---|---|
|主PENDING/C09日志|认证Sender、Receiver、恢复scheduler|256分类＋6stage＋ACK1；345148|相同token重放0写；第257次0分类|
|局部首错摘要|首个拿到关闭资格的Root角色|1×334；所有角色共享同一不可变首错|失败留下raw staging；最多一次摘要尝试；后续异常不再追加摘要|
|STOP_REQUEST|序列化后的首关闭责任者|1×189，已有路径|现行writer可覆盖且多角色使用；v2所需单次门尚未实施|
|CLOSED|既有stop_tree/MR责任者|1×189，已有路径|失败后按原生收敛语义处理；stop_event/stop_result另列|
|cursor/staging|同H锁内的配额责任者|1198/次；两份失败cursor staging等已计350166|模糊预扣/完成立即烧额、停止；禁止退款和重建|
|native seal|唯一当批封存责任者|manifest/ZIP与必需输入另计|必须等待写者静止；封存失败留下真实原件和UNKNOWN|
|行政finalizer|post-exit行政进程|全部导出及host流另计|保留当前32MiB和256数量守卫，整体超限如实失败|

主日志耗尽后，状态机先永久拒绝新分类，完整保留最后一条已计算facts。持久写入completion/EXHAUSTED，尝试独立首错和STOP；释放H锁后调用冻结stop_tree/abort。{src('guard.py',758)}再次获取H锁，因此锁内调用stop_tree会产生重入等待风险；合同明确拆开这两个步骤。

第257次及关闭后的重复错误请求只返回拒绝状态，无per-request错误行。首错已经存在时，后续关键异常不能把bounded emergency扩展成追加日志。独立原始系统错误仍按各自来源保留，其总量证明属于未决关闭集合；汇总代码不得替换/截断原始证据。

当前停止链的精确缺口：{src('guard.py',766)}的stop_result包含closure_persistence_error=repr(exc)与before_stop_charged_snapshot；{src('manager_recovery.py',355)}首错含reason、error_type、2048字符error和预算快照；{src('manager_recovery.py',390)}close结果含roles/errors/预算后快照并追加mr_close_attempts。reason及若干系统返回/异常表示缺统一字段/编码/聚合界。{src('guard.py',759)}还可能写不同stop_event；不能仅以固定STOP/CLOSED两个名字涵盖整条链。

2048字符error经BC紧凑JSON默认ensure_ascii=True后，字符串内容最坏可占24576个ASCII字节，再加引号和字段结构；2048不能当成字节界。socket错误的str(exc)、SEAL_ERROR的repr以及stop_result的closure_persistence_error没有相同截取合同。完整关闭保留区须分别证明这些字段、嵌套快照和所有实际追加次数，当前没有可用的统一差额数字。

最小反例CE-CLOSE-EIO：第256条PENDING已经完整持久，新的独立STOP/CLOSED文件创建或fsync返回EIO/ENOSPC。预留字节未提供物理磁盘空间和可写性保证。合同可证明拒绝后续工作并烧掉额度；无法从配额推出CLOSED必达、真实角色已退出或native seal已完成。缺失记录如实UNKNOWN，保留原预算/T0，继续按原有责任尝试清理，不创建免费重试窗口。

要完成严格关闭空间证明，需先数值化全部实际回收/MR/终态/行政输入、每角色最大尝试与锁序，证明其他生产者无法消耗关闭分区，再完成静态适配和独立授权的原生验收。{ev('QUOTA_AND_MINIMAL_MARKER_ALGEBRA.json')}中的350166仅能批准为局部条件子项。
'''
reports['C09_CONCURRENCY_AND_CRASH_ANALYSIS.md']=f'''# 并发、重放与十二类故障交错

**PQ-5=PARTIAL。** v2具有条件性的额度安全归纳；冻结运行程序尚无该配额机制，原生故障验收0。完整矩阵与最小反例见{ev('CRASH_AND_CONCURRENCY_MATRIX.json')}。

|交错|额度/记录裁决|关闭与证据裁决|
|---|---|---|
|I01 预扣前崩溃|新额度未发放；已完成全球预付前缀保留|原实例关闭，缺cursor不初始化重发|
|I02 预扣后、事实前崩溃|该槽永久烧掉；可无主行|cursor INFLIGHT或角色死亡触发关闭|
|I03 主行中途/短写|该槽保持已扣；仅保留原始部分行|原字节不整行重写，不继续观察；UNKNOWN|
|I04 full write后fsync前崩溃/EIO|持久性不确定，额度保持|失败证据不足仍UNKNOWN|
|I05 fsync后、完成cursor/确认前崩溃|完整行可能已经存在；不重发原token|INFLIGHT恢复路径只关闭；不凭未收到响应退款|
|I06 COMMITTED预扣或完成后崩溃|全球R和local ordinal保持，返回缺失不回滚|重启不重建T0/账/额度|
|I07 同task/ordinal重复提交|原生无task_id；绑定token复用获得0新额|不同ordinal为新观察，照常消耗剩余额|
|I08 两写者争最后额度|同一稳定H锁内fresh-read→durable debit，仅一者成功|后一者看到终态/256；拒绝无额外行|
|I09 global journal短写|沿用原预算核心halt与模糊intent拒绝|原journal部分字节保留，local cursor无权初始化|
|I10 cursor/log/STOP/CLOSED EIO|不退款；停止继续工作|固定错误码可尝试写；持久关闭/回收未知保持UNKNOWN|
|I11 CLOSED/STOP/terminal cleanup期间请求|吸收态，0新授权/0分类|原始终态标记不撤销，停止新入口|
|I12 native seal读取期间变化|需真实角色退出/写者静止，缺前提即拒绝|仅CLOSED存在尚不足够；禁止先hash后变更混包|

线性化次序：所有原生角色共享H生命周期锁；先核身份和当前cursor，原子持久预扣全部计数/类别位，才进行一次日志写入尝试。分类原始行fsync后再持久completion；对终态，在释放锁进入回收之前持久锁存。每笔模糊状态都烧额；角色/进程重启一律关闭该实例。两次持久更新避免把“已预扣”误写成“原始行已保存”。

TERMINAL_LATCHED只封闭新分类；VERIFIED后的未用HANDOFF_VERIFIED/RESUMED类别槽仍须按原始guard消费，计入六stage。FAILED进入POISONED；EXHAUSTED/STOP/CLOSED封闭全部新类别。这一区别避免把成功交接所需的最后两个stage一并阻断。

三个边界条件必须保留：锁文件inode受信且不可被并发Root替换；所有实际写者遵循相同锁和schema；文件及父目录fsync按受审存储模型生效。特权回滚、外部写者和任意重启属于证明域之外，遇到这些情况拒绝资格。正常代码单Receiver的事实不能自动推广到任意两个observer；v2要求锁存封闭cleanup间隙，见CE-TERMINAL。

与现有预算核心的关系：{src('guard.py',568)}用线程RLock与flock检查健康counter/intent，{src('guard.py',629)}的scalar reserve先PREPARED、journal、counter持久，再COMMITTED；模糊错误halt。{src('range_core.py',22)}具备固定task的幂等range，但生产_task_contract目前限定C02/C03/C04，Root C09不能直接假定获得该能力。

v2建议在C09 controller/ready/counter固定之前，用既有scalar primitive预付256次，cursor记录before/after和journal前缀长度/hash；中断后关闭并烧掉已付前缀。初始化幂等采取“已有/残留/模糊即拒绝第二次初始化”，不再铸造新block。观察阶段只花已付local额度，全局R与C09 ACK counter保持。local cursor承担资源槽与类别位，不复制全局预算账或重新定义T0。

锁等待次数、辅助query输出及原停止链多角色交错仍需具体实现的静态证明。配额不变量给出有限授权写入工作量；它没有给任意外部请求洪泛/lock-spin次数或底层fsync时延上界。

522更新及两份cursor失败staging另依赖全局“失败写不重试、单首错/poison责任、后续拒绝不再写”的调用界。残留staging/INFLIGHT必须使所有角色拒绝后续工作；EIO连失败标记都未能发布时的跨角色传播仍属完整关闭/集成未决项。该调用界是待实现合同条件，当前未把它登记为冻结源码已有保证。
'''
reports['C09_WORK_COMPLEXITY_BOUND.md']=f'''# 日志、归档与资源工作量界

**PQ-6相关工作量为PARTIAL；WALL_TIME_BOUND_UNRESOLVED。** 所有数字针对未生效v2的明确局部集合，详见{ev('WORK_BOUND_RECALCULATION.json')}。

|局部操作|最坏次数|字节工作量/条件|
|---|---:|---|
|主日志os.write尝试|263|≤345148；部分写也占用完整预扣槽，禁止整行重试|
|cursor持久更新|522|init1＋bind1＋predebit263＋分类completion256＋poison1；每次≤1198|
|首错摘要|1|≤334；固定一次，无错误追加循环|
|STOP_REQUEST/CLOSED局部发布|2|各≤189；完整回收/MR文件另计|
|以上数据write调用|788|263＋522＋1＋2；≤971216总写入字节|
|文件/目录fsync尝试|1316|263＋2×522＋2（摘要）＋1（初始主log目录）＋3×2（跨目录标记）|
|cursor数据读取|≤522|数据≤625356；另有必要stat/ACL/目录检查，不能把此项当全部syscall次数|
|静止局部集合一次hash pass|1|≤350166输入字节；包括列明的失败staging|
|native ZIP局部raw输入|一份|≤350166；ZIP元数据/压缩膨胀另外计算|
|两个独立archive oracle局部payload|2遍|解压/CRC/hash对应≤700332 payload字节；嵌套ZIP与manifest扫描另计|

971216=345148＋522×1198＋334＋2×189。旧599778/798仅属于较窄的旧cursor/预扣模型；v2新增256笔分类completion，且明确跨目录标记持久责任。因此旧工作表保持历史原样，本轮按新schema和持久顺序重算。

上述工作量还要求全局单次失败/poison责任和失败写不重试；多角色关闭传播及EIO无标记场景的实际强制机制尚待接线证明。故这些数字仅是明确有界调用合同的代数结果。cursor采用紧凑排序JSON＋至多1 LF、同一私有目录原子发布时满足表中界；复用现有BC.Store的紧凑无LF编码会少1字节。若改用RootIPC的indent2编码，必须重新计算cursor及全部工作量，不能直接沿用1198。

在n个给定有界文件总字节B的条件下，流式SHA-256输入量为B；独立核验O(n+B)，排序路径O(n log n)。局部集合至多10个对象（含既有main/STOP/CLOSED、局部新对象和失败staging）。按上一轮F≤1535、ZIP32/无extra/comment/保守descriptor profile，局部头开销H≤22＋10×(92＋2×1535)=31642；ZIP_STORED条件界381808。若另证pinned zlib默认参数满足上一轮compressBound式，deflate条件界382044。该结果依赖格式/压缩库前提，当前未升级或替换压缩实现，完整包需要将其余成员统一计算，不能逐层漏掉ZIP的再复制。

增量数据FD的局部峰值可列为生命周期锁1＋数据FD1；cursor位于同一Root私有目录时另有现有目录FD，跨目录STOP/CLOSED复用RootIPC目录链。完整进程还持有socket、pidfd、输出流、运行库和query子进程资源，当前缺少统一FD常数和实际NOFILE合同。TasksMax4约束任务数量，FD需独立证明。

固定scalar schema使编码输入/结果缓冲有限；1198/1322字节并不等于CPython对象分配峰值。完整观察调用{src('c09_handoff.py',115)}会执行源/输入hash、trusted/read、unit_show和/proc；{src('guard.py',718)}捕获PIPE缺前置字节界。native构建{src('guard.py',1022)}使用整文件read_bytes哈希；post-exit和host helper含z.read整成员物化。1GiB是硬拒绝线，当前未证明所有必要步骤可在其内完成。

访问额：旧完整范围68498保持；若新独立预付256获准，现有项未变时得到68754，再加全部新增测试/适配/核验ΔV。原calibration100000、global1000000及各scope硬额度保持；MR256不可挪用。可选3269＋256=3525≤5000仅在未来明确同context授权后成立，当前不采用隐式合并。

分项裁决：有界授权日志写工作量CONDITIONAL_PROVED；global访问额CONDITIONAL_PROVED（68754仅含已列项）；完整读取/内存/FD为PARTIAL或UNRESOLVED；任意锁等待/反复拒绝请求次数未获统一界。有限fsync调用无法推出300秒必达，完整300秒、terminal5秒、admin30秒及停止时延继续UNRESOLVED。preT0120、全窗1800和stop1740原合同保持。
'''
reports['FULL_EVIDENCE_BYTE_RECALCULATION.md']=f'''# 完整证据数量、分层字节和处理量重算

**PQ-6=PARTIAL；CAPACITY_CONTRACT_NOT_READY。** 旧4450/4451/4452为冻结完整scope的条件数量包络；345148的主日志子项成立不会替代其他生产族的字节责任。见{ev('CAPACITY_RECALCULATION.json')}与{prior('evidence/COUNT_SCOPE_COVERAGE_REVIEW.json')}。

|集合/层级|旧数量上界|C09计数方式|
|---|---:|---|
|封存前raw原件|4450|inputs/root_private/c09_events.jsonl已占一个文件槽；263行仍是一份文件|
|Native ZIP成员|4451|raw集合＋native manifest1|
|行政导出原件|4452|raw集合＋native manifest1＋native ZIP1|
|行政ZIP成员|4467|导出原件＋旧host/source sidecars与行政manifest；仅适用于旧scope|

上轮修正已包含mr_events.lock；完整CALIBRATE_S1S9_THEN_F1_F4 scope不可达的pt_expected_abort槽退出覆盖表。该修正和旧数字保持，新scope/新配额代码不得自动继承全部前提。

假设将来实施v2，原main/STOP/CLOSED路径继续属于旧集合。新cursor和失败摘要最多2个稳定文件，另有cursor失败staging2和摘要失败staging1，共新增集合Q≤5；标记失败staging若已有旧RootIPC异常族覆盖则不新增，若覆盖之外需另加Δ_close。新的源码/测试/授权收据及集成差额也单独计量：

\\[K_{{new}}\\le4450+|Q\\setminus K_{{old}}|+\\Delta_{{close,uncovered}}+\\Delta_{{integration/tests}}.\\]

集成前尚未固定这些集合，故4455/4456/4457仅能成为特定零增量假设下的算式，当前未签为新容量。增量记录数与文件数分别计算，不新增263个raw文件，不重复增加旧三个路径。

用集合差而非无条件叠加重算字节：先从B_other_raw中拿出已计的STOP/CLOSED及其staging，再把一次main＋cursor/失败/staging＋一次STOP/CLOSED/staging纳入局部350166包络，随后加其余原始C09/MR/回收/系统/测试对象。这样B_total不重算同一raw路径；行政层实际又复制原件并包含native ZIP，实际物理复制成本须保留。

\\[U_N=R_{{raw}}+M_N,\\quad Z_N=ZIP(U_N;paths,codec),\\quad E_A=R_{{raw}}+M_N+Z_N.\\]
\\[U_A=E_A+H_{{host}}+S_{{locks}}+M_A.\\]

|完整生产族|可用局部事实|完整资源缺口|
|---|---|---|
|C09|主日志345148；局部v2子集350166|cursor/配额尚未实施；commit.resources、cleanup和其他原件需逐schema界|
|C00–C12|counter24、C03固定16MiB等|局部journal、结果、快照与输出需同scope总和|
|RootIPC/Boot/readiness|4MiB/128KiB读取接受cap，readiness602×131072=78905344的cap乘积|生成/异常staging与aggregate匹配未闭合；cap乘积超32MiB不证明极值同时可达|
|ManagerRecovery|event32KiB、query接受8192/2048|接受限制位于capture之后；close/errors/预算snapshot聚合仍需界|
|S1–S9|48×256×4096=50331648 trace cap乘积|registry/metadata/journal/snapshot和其余证据另计|
|Global journal|旧完整校准条件15441008；全1m窗口条件471876988|writer与range/terminal后验32MiB接受义务尚未统一|
|Gate、F1/F4|固定槽位/访问额|状态树、策略、trace/report和序列化字节未完备；模型运行0|
|Metadata/封存/行政|manifest/ZIP接受cap与流式部分checker|raw generator、整文件哈希、压缩膨胀、嵌套复制、host stdout/stderr/traceback的总量与峰值未闭合|

这些数值为上一轮源码条件界/接受cap的复核延续，见{prior('evidence/TOTAL_BYTE_FAMILY_AUDIT.json')}、{prior('evidence/GLOBAL_JOURNAL_BYTE_MODEL.json')}、{prior('evidence/ZIP_BOUND_ALGEBRA.json')}。没有把高于cap的保守上界误作必然实际超限。

native收集会遍历ROOT内全部常规文件，完整性仍要求无symlink/错路径/缺件/重复/跨实例成员，逐件hash/size以及真实quiescence。旧256/257拒绝线保持，新材料不授予大包许可。对已接纳且总字节受限的包，独立oracle具有O(N+B)条件工作量；native生成前处理、环境扫描和admin整体尚未闭合，CAPACITY_CONTRACT_NOT_READY继续成立。
'''
reports['CAPACITY_CONTRACT_FINAL_PROPOSAL.md']=f'''# 配额与容量合同最终待批材料

当前有两类独立决定：**C09逻辑配额v2为PROPOSED_NOT_EFFECTIVE；完整容量合同为CAPACITY_CONTRACT_NOT_READY。** 容量新上限尚未选定，现行256行政原件/257 native成员守卫原字节保持。

可审阅的固定对象为{link('C09-PENDING-QUOTA-CONTRACT/2-DRAFT',Q)}，版本PendingQuota-Closure/review-1，SHA-256 `{QHASH}`。该文件给出256次全部准入尝试、263主行、345148主预留、schema、类别去重、终态锁存、预付顺序、耗尽与崩溃烧额/关闭规则。

精化的独立元数据参数为cursor1198、更新522次；主日志/配额/首错/STOP/CLOSED及声明的失败staging子集≤350166，写量≤971216、durability尝试≤1316。它们由具体schema和持久顺序推导，作用域限于列明子集。完整关闭回收/MR/seal/admin字节仍UNRESOLVED；批准逻辑条款不构成完整关闭保留量、容量、实现或动态验收批准。

配额最终待批条款：

1. 只对一次全新、唯一batch/boot/handoff/执行锁/授权绑定生效；当前实际身份null。样例batch14仅作宽度占位，历史batch14保持CLOSED。
2. 256次独立预付在C09 controller/ready/counter冻结前完成；沿用原scalar持久预算核心，无MR额度转移，无观察阶段全局R变更。预付中断或重复初始化关闭原实例。
3. 七个生命周期/ACK类别位和分类ordinal在同一个Root保护cursor持久预扣，全部写者用同一稳定H锁；相同token永不重授额度。
4. 准入后检查/事实/分类失败也烧额。完整raw append/fsync后再写completion；终态锁存先于释放锁回收。第256条PENDING完整保留，第257次拒绝且不追加错误行。
5. 仅允许现行封闭scalar schema、明确宽度和固定编码；先验证输入再分配/编码。原始错误输入、部分行和失败staging保留，缺证据则UNKNOWN。
6. cursor预扣或完成模糊、短写、EIO、重启、外来cursor、过期/终态均关闭；不退款、不重建T0/预算/新免费窗口，不把摘要写入成功当作实际回收成功。
7. 单份首错与停止标记独立于主额度；原始ACK/commit/witness/预算/角色退出和原native/admin证据仍全部必需。完整关闭分区待未决字段闭合，容量准入保持关闭。
8. 现行停止/封存/行政/守卫/MR跨实例规则保持；后续静态维护和原生验收需新明确授权与完整增量重算。

可直接采用的独立决定文字：

> 批准逻辑草案：我批准上述版本及SHA-256的C09配额逻辑条款用于下一阶段静态维护申请，接受有限配额可能提前关闭合法延迟见证轨迹。完整关闭保留量和完整容量仍待闭合；本决定不授权实现、WSL、真实故障、T0/预算建立或F1/F4，MR规则仍单独待批。

> 拒绝或退修：我拒绝当前C09配额逻辑草案，或要求先闭合完整关闭保留量；现行源码、守卫和资源门继续保持。

完整容量最终审批应等待：所有raw单项/总量、部分/异常/staging集合、新增文件/访问Δ、ZIP格式和压缩膨胀、native/admin嵌套、manifest最大尺寸、读写/哈希/解压/内存/FD与期限、逐件原始oracle及原生异常关闭证据均具备完整参数。现阶段不建议填写一个更大的任意cap。{doc('CONTRACT_APPROVAL_CHECKLIST.md')}逐项列出阻断。
'''
reports['MR_CROSS_INSTANCE_STATUS.md']=f'''# MR跨实例规则独立状态

**MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE。** 本轮配额进展未改变MR规则。当前user_approved=false、runtime_enabled=false、approved artifact pairs为空，A/B identity与certificate/use记录仍未签发。

保持原待批对象{link('MR-CROSS-INSTANCE-ADMISSION-FINAL-TEXT/1-DRAFT',M)}，SHA-256 `{MHASH}`，及{prior('MR_CROSS_INSTANCE_FINAL_APPROVAL_TEXT.md')}。本轮仅复核hash和独立状态，规则文件原字节保持。

限定承认项仍为：独立A在特定原生受控服务故障下，主自动STOP/CLOSED、真实角色退出/组空、原预算保持、native/admin封存及独立raw oracle所支持的有限实现能力。fallback-only、缺证据或必需UNKNOWN不能充当该项资格。A/B需同boot、精确受审source pair和namespace-only AST映射、TCB前提、新鲜授权及单B nonce绑定，证书位于A封存前像之外，use_spec→授权→实际use避免自摘要环。

主B继续当批重证boot_id、源/输入/执行锁、单位/InvocationID/PID、UID/GID/运行时、预算/T0/期限、WORK/C00、真实C09、正常MR、管理器当前健康、当前监督/停止责任和完整资源资格。A的预算/窗口/额度不会转移给B，C09 quota的逻辑上界也不产生异常关闭证书。

MR原则批准、C09配额逻辑批准、完整容量批准、具体静态维护和动态执行分别记录。当前所有实际承认与执行项继续未生效。
'''
reports['CONTRACT_APPROVAL_CHECKLIST.md']=f'''# 合同审批与证据清单

|审批对象|当前状态|可审查内容|仍需条件|
|---|---|---|---|
|C09配额逻辑v2|PROPOSED_NOT_EFFECTIVE / PARTIAL|256尝试、263行、345148主预留、持久类别位/终态锁存、失败烧额|用户按版本/hash明确决定；后续实施另授权|
|局部cursor/失败/标记子项|CONDITIONAL_PROVED|1198/334/189字段代数；350166 retained；971216写量；1316 durability|显式schema、单次生产/无重试、正确目录fsync与存储前提；完整关闭仍未决|
|完整关闭保留量|UNRESOLVED|真实stop_result/MR/exit/seal/admin路径已识别|reason/异常/快照/roles/journal/总量、所有角色与staging闭包|
|完整容量合同|BLOCKED|旧4450/4451/4452条件包络和分层公式|所有字节/内存/IO/新增Δ及包格式条件闭合|
|MR跨实例规则|PROPOSED_NOT_EFFECTIVE|原14条限定规则原hash保持|用户独立批准；精确pair/A/B/use和实际原生证据|
|最小静态维护|BLOCKED（当前任务范围）|{doc('MINIMAL_STATIC_MAINTENANCE_APPLICATION.md')}已具体列明|新授权及研究实施门适用范围明确|
|WSL/C09真实故障/F1/F4|BLOCKED|本轮动态结果0|未来独立授权、新锁/身份、当前真实资源资格与有效窗口|

v2准确审批hash：`{QHASH}`；MR准确审批hash：`{MHASH}`。绑定对象见{ev('FINAL_PROPOSAL_BINDING.json')}。本轮无用户审批回执，任何文字建议均未登记为APPROVED。

|验收门|状态|裁决|
|---|---|---|
|PQ-1 写入路径|PROVED|冻结封闭原生调用域内3个event调用/1个PENDING写点及全部上下文枚举|
|PQ-2 记录数|CONDITIONAL_PROVED|v2持久槽不变量推出256＋7=263；现行源码缺quota、保留COUNTEREXAMPLE|
|PQ-3 字节数|PARTIAL|345148主日志条件证明；完整PENDING/关闭证据为PENDING_BYTE_BOUND_PARTIAL|
|PQ-4 配额耗尽|UNRESOLVED|局部标记空间已列明；CLOSE_RESERVE_BOUND_UNRESOLVED；EIO下持久关闭无保证|
|PQ-5 故障一致性|PARTIAL|12类交错与条件归纳完整；当前实现/原生验证0，停止/存储结果待证|
|PQ-6 完整容量|PARTIAL|旧文件槽和新集合差核算明确；完整字节/工作量继续UNRESOLVED|
|PQ-7 审批准备|PARTIAL|逻辑草案可明确批准/拒绝；完整端到端容量/关闭合同保持BLOCKED|

历史冻结要求：9867份历史文件逐件hash与原始基线匹配；另行固定上一轮全部160工件、64运行源码/输入、8上轮维护审查对象及21合同审查对象。研究包交付核验单独列出，不能视作native/runtime seal或资源资格。
'''
reports['GENERAL_BASELINE_AND_SEPARATION.md']=f'''# 通用方法与实施门

本轮全部条款属于**COVERED_BY_G**：有界追加日志、串行持久预扣、transaction token幂等、固定schema/长度、终态锁存、独立关闭预留和内容寻址manifest均已有通用方法覆盖。

输入族为单一有效handoff的n次缺witness观察，加并发/模糊持久交错；指标为原始保留字节、持久写次数、至多一次额度和关闭证据完整性。最强适用G可采用同一有界WAL/预付资源槽/串行事务/独立紧急分区，满足相同约束。预测严格差距0；未构造出任何使G必需承担更高代价的实例。{ev('GENERAL_METHOD_COMPARISON.json')}记录输入族、指标、G和裁决。

CE-LAST/CE-REPLAY等用于揭示不充分工程条款，不构成架构原创性分离；17条历史PENDING用于证明重复可达，不能证明比G更优。STRICT_SEPARATION_INSTANCES=0，IMPLEMENTATION_GATE=CLOSED。本轮新机制实现、运行源码修改、原生模型检查均0。
'''
reports['MINIMAL_STATIC_MAINTENANCE_APPLICATION.md']=f'''# 下一阶段最小静态维护申请材料

申请对象为受G覆盖的工程合同适配审查，依据{link('配额v2精确对象',Q)}（SHA-256 `{QHASH}`）。本文件仅准备具体范围；当前IMPLEMENTATION_GATE=CLOSED，尚无实施授权，也未用工程标签自动绕过用户要求的分离门。

建议先申请的静态工作：

1. 给全部实际C09/关闭/MR/schema逐字段界，先闭合stop_result、首错、close_attempts、terminal review和host流；明确350166之外的必要差额。
2. 审核现有H锁、RootIPC/BC发布、scalar预付的最小接线图，列出允许改动的精确文件及新注册目标，维持预算核心/封存/finalizer/MR承认/256与257守卫原样。
3. 若用户后续明确授权常规静态维护实现，并明确该工程维护与研究实施门的适用关系，再在独立目录提出字段校验、单cursor、类别位、预扣与completion、terminal latch、首错/停止分区的最小diff；先重算全部schema/调用/文件/访问/字节增量。
4. 静态回归应覆盖最后一额竞争、双终态间隙、stage事件/状态发布崩溃、短写/fsync/EIO、cursor缺失/foreign/replay、最后PENDING完整保留、STOP/CLOSED不重开以及seal静止前提。测试计划不构成动态授权。

未来交付应有新源/输入/contract/执行锁、逐件diff、负向测试义务、独立计数与raw oracle和完整新增Δ。旧batch14/ra01及所有旧T0/账/回执持续CLOSED并保持原字节。

当前无严格分离实例；若工作被定义为新的架构候选，实现申请仍须先提供“具体输入族＋度量＋最强G＋严格差距＋必要更高代价实例”。当前材料只支持继续静态合同维护。容量批准、MR批准、原生执行和F1/F4均在本申请范围之外。
'''
reports['NEXT_ACTION.md']=f'''# 下一步

当前交付已完成本轮授权的静态审计与合同准备。优先处理完整关闭保留量：按实际stop_result/MR/exit/seal/admin对象逐字段补界，固定所有角色尝试及staging集合，再核全部raw与归档工作量。C09逻辑v2可独立审阅，尚未生效。

本轮确认345148只覆盖主日志；局部cursor/首错/两标记及失败staging条件界350166并不覆盖全链。记录数263依赖持久类别位、预扣/完成和终态锁存；冻结源码仍保留重复反例。精确材料见{doc('CONTRACT_APPROVAL_CHECKLIST.md')}与{doc('MINIMAL_STATIC_MAINTENANCE_APPLICATION.md')}。

CAPACITY_CONTRACT_NOT_READY；CLOSE_RESERVE_BOUND_UNRESOLVED；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE。完成新明确审批和所需静态维护之前，保持全部运行源、预算核心、native seal、行政finalizer及256/257原守卫。任何未来原生资格申请需新唯一身份/锁/授权和当前有效资源链；旧窗口和账不会重开。
'''
reports['FINAL_DECISION.md']=f'''# PendingQuota-Closure最终裁决

**主日志256次尝试→263行→345148 bytes的条件证明已闭合；完整关闭保留量和完整容量继续未决。** 最终状态为 `C09_MAIN_BOUND_CONDITIONAL_CLOSE_RESERVE_UNRESOLVED_CAPACITY_NOT_READY`。

|验收门|裁决|证据和适用范围|
|---|---|---|
|PQ-1|PROVED|3个原生event调用、1个PENDING写点、6个stage发布，13类上下文完整枚举；{doc('C09_PENDING_PATH_AUDIT.md')}|
|PQ-2|CONDITIONAL_PROVED|持久预扣与七个类别位得到A≤256、E≤6、ACK≤1、N≤263；现行源码COUNTEREXAMPLE保持；{doc('C09_RECORD_COUNT_BOUND_PROOF.md')}|
|PQ-3|PARTIAL|1322/948/1028逐字段→345148主预留；cursor/关闭等另计；PENDING_BYTE_BOUND_PARTIAL；{doc('C09_TOTAL_BYTE_BOUND_PROOF.md')}|
|PQ-4|UNRESOLVED|两个稳定标记独立预留378，完整stop/MR/seal/admin差额未闭合；CLOSE_RESERVE_BOUND_UNRESOLVED；{doc('C09_OVERFLOW_AND_CLOSE_RESERVE.md')}|
|PQ-5|PARTIAL|12类交错及5个最小反例已列明，v2额度安全为条件归纳；无运行实现/原生故障验收；{doc('C09_CONCURRENCY_AND_CRASH_ANALYSIS.md')}|
|PQ-6|PARTIAL|旧4450/4451/4452适用域保持，新quota文件集合差及字节分层明确；完整容量/内存/工作未决；{doc('FULL_EVIDENCE_BYTE_RECALCULATION.md')}|
|PQ-7|PARTIAL|精确hash的逻辑v2批准/拒绝文本与最小静态维护申请已完成；完整端到端合同审批仍BLOCKED；{doc('CAPACITY_CONTRACT_FINAL_PROPOSAL.md')}|

本轮关键数值：历史17 PENDING/24行/27144 bytes，经原始导出锁直接核验；新原生执行0。分类通用schema界1318，合同沿用1322；345148=256×1322＋6×948＋1028。1298仅用于正常缺witness、durable ACK有效的PENDING子路径。

v2新增持久类别位/终态锁存、预付桥接字段及每分类完成cursor责任：cursor1198、更新522；局部retained350166（相对main独立差额5018）、写量971216、durability1316。旧956/266/348684/599778/798保持历史原样，新数值只绑定v2声明的子集。完整PENDING原件/回收/MR/封存/行政空间仍超出该子集，不能用它宣称完整CAPACITY就绪。WALL_TIME_BOUND_UNRESOLVED保持。

反例已补齐：无原子序列化争最后一额、日志后state前崩溃重放、双observer终态cleanup间隙、关闭写EIO、hash后文件变化。配额终态要求最后一次完整raw保留、拒绝257、首错单次、预扣烧额不退款；EIO时关闭证据缺失仍为UNKNOWN，T0/预算不重建。

待批逻辑合同为{link('C09-PENDING-QUOTA-CONTRACT/2-DRAFT',Q)}，SHA-256 `{QHASH}`。完整容量继续CAPACITY_CONTRACT_NOT_READY；MR跨实例规则保持原SHA和PROPOSED_NOT_EFFECTIVE。全部候选均COVERED_BY_G，预测严格差距0，严格分离实例0。

本轮14份指定报告、额外基线/实施申请、机器代数/路径/故障表及研究索引已经形成。9867历史文件、前轮160工件及64运行源/输入将由{ev('DELIVERY_CHECK.json')}最终逐件核验；根导航只前置新结论并保留旧字节后缀。研究ZIP的manifest与核验回执属于本轮行政研究交付，不属于运行实例native/admin seal。

运行源/预算核心/日志实现/native seal/finalizer/256与257/MR规则修改0；WSL调用、动态测试、真实注入、F1/F4均0；T0/deadline/R=null。冻结失败、UNKNOWN和旧关闭窗口完整保留。
'''

for name,body in reports.items():
    (OUT/name).write_text('# '+body.split('\n',1)[0].lstrip('# ')+'\n\n'+passport+body.split('\n',1)[1].lstrip()+footer,encoding='utf-8')
index='# PendingQuota-Closure研究证据索引\n\n'+passport
index+='所有运行结果保持历史范围；本轮只完成静态证据审查与逻辑条款。\n\n'
for name in reports:index+=f'- {doc(name)}\n'
index+='\n机器证据：\n\n'
for name in ['INITIAL_INTEGRITY.json','PREVIOUS_ZIP_FULL_VERIFICATION.json','FROZEN_SOURCE_LOCK.json','STATIC_PRODUCER_CENSUS.json',
 'PRODUCER_CONTEXT_MATRIX.json','SOURCE_EXCERPTS.json','HISTORICAL_RECHECK.json','H34_STATIC_INPUT_REVIEW.json',
 'RECORD_BYTE_ALGEBRA.json','QUOTA_AND_MINIMAL_MARKER_ALGEBRA.json','CRASH_AND_CONCURRENCY_MATRIX.json',
 'WORK_BOUND_RECALCULATION.json','CAPACITY_RECALCULATION.json','FINAL_PROPOSAL_BINDING.json','GENERAL_METHOD_COMPARISON.json','DELIVERY_CHECK.json']:
    index+=f'- {ev(name)}\n'
index+='\n'+link('待批C09逻辑合同v2',Q)+'\n\n'+prior('EVIDENCE_INDEX.md')+footer
(OUT/'EVIDENCE_INDEX.md').write_text(index,encoding='utf-8')

print({'reports_written':len(reports),'specified_reports':14,'index':1,'proposal_sha256':QHASH})
