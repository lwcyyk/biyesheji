"""Write authorized source-audit/proof/contract reports; no mechanism code."""
from AUDIT_INPUTS import ROOT, PREV, BOUND, OUT, E, RUNTIME, read, sha

def L(label,p,line=None):return '['+label+']('+str(p).replace('\\','/')+(f':{line}' if line else '')+')'
def S(file,line):return L(f'{file}:{line}',RUNTIME/file,line)
def J(name):return L(name,E/name)
def D(name):return L(name,OUT/name)
def Q(name):return L(name,PREV/name)
def B(name):return L(name,BOUND/name)
CP=OUT/'proposals/CAPACITY_REVIEW_DRAFT.json'
CL=OUT/'proposals/CLOSE_RESERVE_REVIEW_DRAFT.json'
MP=BOUND/'proposals/MR_CROSS_INSTANCE_FINAL_RULE_DRAFT.json'
intro=('## Material Passport\n\nDCL-R6-C09-CloseReserve-Closure；CloseReserve-Closure/review-1；'
       '2026-11-16（Asia/Shanghai）；只读源码、冻结输入、字节代数和抽象轨迹审查。'
       '结论类型ANALYZED；运行实例、原生故障和模型检查均未启动。\n\n')
tail=('\n\nRESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；'
      'MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；STRICT_SEPARATION_INSTANCES=0；'
      'PASS_BOUNDED=[]；IMPLEMENTATION_GATE=CLOSED。\n')
r={}
rows=read(E/'CLOSE_PRODUCER_MATRIX.json')['rows']
producer_table='|ID|真实生产者与位置|记录/对象|次数与字节责任|\n|---|---|---|---|\n'
for x in rows:
    producer_table+=f"|{x['producer_id']}|{x['producer']}；{x['source_site']}|{x['record_or_path']}|{x['maximum_count']}；{x['maximum_encoded_bytes']}|\n"
r['CLOSE_RECORD_PRODUCER_AUDIT.md']=f'''# 关闭记录生产者审计

**CRB-1=PROVED，范围为冻结64份源码/输入及其封闭调用域。** 源摘要先核对再分析，见{J('INITIAL_INPUT_CHECK.json')}。共解析204个相关调用点，形成36类生产者；完整矩阵为{J('CLOSE_PRODUCER_MATRIX.json')}，逐行上下文为{J('SOURCE_EXCERPTS.json')}。

矩阵逐项给出producer、实际进程、trigger、phase、maximum_count、maximum_bytes、persistence、quota_domain、required_for_close、after_closed和failure_behavior。以下汇总保留记录数、写入次数、唯一文件数三种计量的区别。它们均指保守包络，未宣称全部极值可在同一轨迹同时达到。

{producer_table}

当前代码没有“第257次配额拒绝日志”生产者；待批v2要求拒绝本身0条新增主日志，首个额度耗尽摘要另占一次。原生CHECK中可能出现FAILED分类，仍属于345148的主日志槽位；HANDOFF_FAILED没有实际publish调用。

关键别名：STOP的Root与budget-halt生产者写同一out/STOP_REQUEST.json；ABORTING与最终cleanup写同一mr_close_state.json；正常waitpid与异常reap分支在同一phase互斥、使用同一路径；mr_close_attempts的多行仍为一个文件。CLOSED首次写入后，{S('src/guard.py',759)}把新的关闭标记改写到新stop_event路径；stop_result另为独立文件。

外部停止器没有独立Receiver_exit.json生产者。native external-tail允许当前封存者自身尚存活，要求其他已知角色退出；其自身退出与全局quiescence由post-exit行政审计再证明。{S('src/manager_recovery.py',405)}、{S('src/startup_lifecycle.py',441)}给出两种责任。CLOSED、组空、Root退出和证据完整度分别判断。

预算最终状态属于已存在counter/intent/journal及其hash/size快照，关闭函数不新建预算账。独立terminal reader只返回对象，由sealer保存一份terminal review；未接线的maintenance oracle也没有自动递归生产运行原件。正常关闭缺mr_first_failure或mr_close_state时保留真实内部UNKNOWN，不能为凑齐数量而制造记录。
'''
r['CLOSE_RESERVE_BOUND_PROOF.md']=f'''# 关闭记录数和字节保留量证明

总体裁决：**CLOSE_RESERVE_UNRESOLVED**。与上轮CLOSE_RESERVE_BOUND_UNRESOLVED含义一致。部分源码结构次数与单条schema已得到CONDITIONAL_PROVED；完整N_close,max和B_close,max仍未具备统一数值。

在冻结完整scope、单次activation、最多一次C09恢复、Restart=no、首个异常展开退出、无外加Root调用的前提下，继承并复核：A_abort≤2×3＋2×4＋2=16；S_stop_tree≤16＋4＋1＋1＋1=23；Q_seal≤7。两个phase的正常/异常waitpid写入互斥，合计W≤2。源码依据为{S('src/guard.py',1140)}、{S('src/guard.py',1222)}、{S('src/boot_continuity.py',415)}和{S('src/manager_recovery.py',317)}；完整展开见{J('CLOSE_COUNT_DERIVATION.json')}。

每次abort在stop_tree之外至多7项数据生产尝试：STOP、first_failure、external_closing、ABORTING、fallback CLOSED、close_attempt一行、final close_state。stop_tree至多一份CLOSED/stop_event及一份stop_result。于是：

\\[N_{{core,attempt}}\\le7A+2S+W+H=160+H.\\]

H单独表示budget-halt的额外STOP写入。在C09 idle/no-new-budget的关闭前缀中H=0；完整scope的每角色halt工作量还需单独核算。该160界排除主日志/配额元数据、MR正常审查、payload退出遥测、native/admin证据。核心唯一稳定路径的保守界为5个固定异常目标＋2S＋close_attempts文件1＋W=54，失败staging另列；**160是生产尝试数，54是局部路径数，两者都未作为完整关闭配额获批。**

单个健康Receiver异常关闭分支，STOP和首错均未存在时，可发生8次核心数据发布，落在7个核心路径：STOP、first、external_closing、ABORTING、CLOSED、stop_result、attempt、final state；ABORTING/final共用路径。父waitpid、退出证明、封存/行政材料继续另计。因此“仅两个停止标记”不足以枚举必需关闭证据。

定义R为reason的JSON编码token长度（含引号），T为适用异常类名token上界且T≥4，B为三份预算hash/size/error映射长度，E为关闭异常repr的编码token长度，V_j为12个cgroup值token长度。{J('CLOSE_SCHEMA_BYTE_ALGEBRA.json')}给出固定键、JSON标点/缩进、数值及逐字段代数：

|记录|编码|条件上界bytes|
|---|---|---:|
|STOP/CLOSED/stop_event|RootIPC indent2 UTF-8，无LF|144＋R；reason为43字节ASCII时189|
|ABORTING|BC compact ensure_ascii=True，无LF|237|
|external_closing|BC compact，无LF|260|
|first_failure|BC compact；error≤2048 code points|25054＋R＋T＋B|
|cleanup state（分支并集包络）|BC compact|997＋11T＋B|
|close_attempt行|相同compact＋LF|998＋11T＋B|
|stop_result|RootIPC indent2|1151＋E＋ΣV_j|
|正常waitpid含完整当前source state|RootIPC indent2|1223|
|异常reap waitpid|RootIPC indent2|565|

B≤69＋3max(106,29＋T)。error的2048字符经ensure_ascii=True最坏占24576内容字节，加引号24578；notes持久化前保守计10项，角色分支取字段并集、至多2个目标。实际成功/失败分支通常更小。

数值前提明确保留：PID正int32≤10、ticks/dev/inode/预算长度u64≤20、clock_ns signed64≤20、binary64 JSON≤25、waitstatus≤11；stat_ctime_ns采用signed64秒换算纳秒的29字符界，单独处理其与clock_ns的表示差异。冻结namespace、source state键集合及无额外Root字段为条件，当前没有新宽度验证实现。

核心字节公式为：

\\[W_{{core}}\\le A(L_{{STOP}}+L_{{first}}+260+237+L_{{fallback}}+L_{{cleanup}}+1+L_{{cleanup}})+S(L_{{marker}}+L_{{result}})+W\\max(1223,565)+W_{{budgetSTOP}}.\\]

单次生产的数据要么保留于目标，要么留下部分staging；累计生成字节可以保守上界这些目标/staging的保留总量。文件别名按集合计一次，覆盖写的多次成本只进入W。全关闭还需加pre-seal、SEAL_ERROR、payload退出原件、外部见证和独立native/admin集合，见{J('CLOSE_TOTAL_FORMULA.json')}。

派生兼容义务：若另行证明适用异常类名T≤502，则16×[998＋11T＋69＋3max(106,29＋T)]≤131072，与MR oracle现有整个close_attempts文件读取界相容；T=502给130912，T=503的保守式给131136。{J('MR_CLOSE_ORACLE_COMPATIBILITY.json')}记录这项推导。502仅为代数阈值，当前未选择新政策或证明完整TCB的T界。

最终未决项是R_budget、T的完整TCB来源、E、V_j、terminal review、payload/host流及全部派生集合。存在这些未决项时，B_close保持null，停止猜测更大的容量数值。通用重复调用反例与冻结调用界分别审查，不能用域外任意调用否定上述有条件16/23界。
'''
r['QUOTA_EXHAUSTION_COUNTEREXAMPLES.md']=f'''# 五类配额边界输入族与最小反例

全部轨迹为静态源码/合同输入族，执行和故障注入0。详细初态、事件、状态、记录、字节、预算和终态见{J('QUOTA_BOUNDARY_FAMILIES_A_E.json')}；反例登记含适用域，见{J('COUNTEREXAMPLE_REGISTER.json')}。

|族|初态及事件序列|记录与字节变化|预算、终态和前提|
|---|---|---|---|
|A 主分类额度耗尽|单handoff、有效ACK、见证暂缺；完成256次PENDING，再触发资源停止|主日志256 CHECK＋4个已到达stage＋ACK=261行；分类槽按1322预扣时主前缀≤343252。干净Receiver abort可再有8次核心发布/7路径，封存另计|观察/关闭R增量0；256预付只在此前已获准的假设中成立。存储/监督满足时可关闭，内部/原生/行政状态独立|
|B 第257次请求|256槽已耗尽；重发相同或新ordinal请求k次|待批v2拒绝所有新分类、0拒绝日志、0新增主行；当前源码仍可沿PENDING自环append|无新增预算账；当前deadline/STOP终止与v2 quota终止分别登记。旧源码257前缀为缺quota反例|
|C 耗尽与管理器/Root故障并发|A后manager stop报错、父Root退出或见证尚未发布；主停止转fallback|STOP/CLOSED/MR/回收/错误/角色证据另写；原件保留，缺失的父waitpid不能补造|group空可能已确认，native仍因缺退出原件保持UNKNOWN。真实管理器、Root生命周期和外部TCB条件必须明示|
|D 短写/EIO|接近耗尽时已预扣一次，append/fsync/marker发布失败|一槽烧掉，部分原始行/失败staging保留；可能0份持久停止标记|逻辑额度与物理持久性分别裁决；不退款/重建T0；外部退出/组空/证据完整性分别观察|
|E 重复关闭|CLOSED已存在、ZIP尚缺；两个已有Root角色先后abort|可重写ABORTING/final，追加close_attempts，产生stop_event/stop_result；冻结域append≤16；扩展API族E_n可随n增长|关闭函数自身不扣新visit；E_n任意外加调用超出4450的once/no-reentry前提，不能作为冻结域无界轨迹|

族A的261行接近共同包络263；六个成功stage与256条未完成PENDING在同一耗尽轨迹上无法同时出现。主分类耗尽也不会使剩余成功生命周期槽自动变成关闭额度。此前345148保留为共同主日志合同界。

CE-STOP-RACE：两个Root在{S('src/manager_recovery.py',328)}同时看到STOP缺失，然后各自publish；该检查在mr_close锁之外，同一路径可能被覆盖两次。唯一文件数仍为1，写量与durability成本增加。CLOSED在H锁内保持一个固定终态路径，但后续{S('src/guard.py',759)}明确创建不同stop_event。

CE-PARENT-WITNESS：C09 Sender已退出，父协调者尚未完成{S('src/guard.py',1225)}的真实waitpid发布就死亡/被停止。Receiver可以按现有责任回收payload并观察角色退出；{S('src/terminal_evidence.py',129)}仍可能缺少直接父见证，native_ready保持false。健康存储和足够配额不能恢复已经失去的内核亲子见证。

CE-EIO-NO-MARKER：{S('src/guard.py',82)}设置的_HALTED属于当前进程；若共享STOP发布和产生模糊intent之前就写失败，其他进程仅凭该内存标志无法知晓停止。待批配额的跨角色失败传播和实际退出证据仍需独立证明。

CE-SEAL-TEXT(m)：在接口故障模型下，sealer的STOP查询经{S('src/guard.py',718)}返回非零及m字节stderr，异常携带全文，最终可能写入{S('src/guard.py',1149)}的SEAL_ERROR。m=400000展示局部350166未给该字段分配空间。此例只反驳“未约束接口输出也受局部配额覆盖”的推理；pinned systemctl在当前可信环境生成该输出的实际可达性未验证，本轮不将其宣称为原生执行反例。

所有增长族只量化底层表示、实际存储和期限允许的有限前缀；本轮没有物理无限吞吐、无限文件或任意n必能在12秒内完成的主张。
'''
r['C09_TOTAL_LOG_BOUND.md']=f'''# 主日志、关闭和其他C09对象的无重复组合

345148是待批主日志预留，N_main≤263依赖256次尝试、七个生命周期/ACK类别位、持久预扣/完成和终态锁存。冻结代码尚未实施这些约束；继承{Q('C09_RECORD_COUNT_BOUND_PROOF.md')}和{Q('C09_TOTAL_BYTE_BOUND_PROOF.md')}的条件范围。

以真实路径定义互不重叠的三个集合：M为c09_events.jsonl；C为选定完整关闭原件及其实际失败staging；O为C09其他原件及未计入C的配额元数据。令B(X)按唯一路径/实际保留版本求和：

\\[B_{{C09,total}}=B(M)+B(C)+B(O)\\le345148+B_{{close,max}}+B_{{other,max}}.\\]

|对象|组合归属|计量注意|
|---|---|---|
|PENDING/CHECK/六stage/ACK|M|CHECK可能含FAILED或在途晚于STOP，均消耗原主槽；无额外HANDOFF_FAILED生产者|
|STOP/CLOSED、mr_first、mr_close_state、attempts、stop_event/result、关闭staging|C|STOP/CLOSED独立于主行；ABORTING/final同一文件，attempts多行一个文件|
|quota摘要/cursor/各自staging|按最终划分放C或O一次|旧350166已经包含main、这些对象、两标记及声明staging；不能再完整叠加345148或完整C|
|handoff state、commit/resources、exit_witness、ticket/ready及源/输入授权|O或既有raw族|native/admin读取和复制原件；未通过读取就绪/证明的字段仍有字节责任|
|global counter/intent/journal|既有全局raw族|预算快照只是hash/size映射，不再复制整份journal到MR记录；原journal本身仍保留一次|
|native manifest/ZIP|独立native派生层|哈希/归档会再读取M/C/O；数据流工作量另计|
|admin audit/stdout/快照/manifest/ZIP/最终收据|独立行政层|原件复制和包内nativeZIP产生真实新增字节，不能因内容重现而省略|

主日志不承担STOP/CLOSED、ABORTING、回收结果、MR关闭、父waitpid或native/admin的空间责任。旧局部350166的独立差额5018继续保留其原声明作用域；本轮新增237/260/1223等schema子界没有替完整关闭池选定总cap。

原始交接安全仍依赖真实ACK/commit、身份/boot/预算绑定、pidfd与直接父waitpid、一次验证/恢复以及当前监督。额度耗尽只给资源失败停止，无法把延迟witness变成VERIFIED。父见证缺失、raw部分行、角色退出未证或任意必要UNKNOWN均保持真实失败强度。主日志有界本身不能推出整个交接最终成功。

最终B_close、B_other及B_C09,total数值均为UNRESOLVED，见{J('CLOSE_TOTAL_FORMULA.json')}。既有off_t64表示界只用于区分表示空间与资源合同，没有满足32MiB或1GiB准入的作用。
'''
r['PERSISTENCE_FAILURE_BOUNDARY.md']=f'''# 逻辑保留、I/O故障和外部停止边界

总体为**PARTIAL**：可证明的预算/日志动作不变量与实际停止、持久证据和封存结果分别报告。有限逻辑quota提供正常存储条件下的空间需求约束；未建立磁盘物理预分配、关闭池隔离或任意介质故障下的完成定理。

|事件/前提|仍可保留的保证|需要实际证据的部分|
|---|---|---|
|预扣完整持久，尚未append|待批v2槽烧掉；无重发授权|cursor真实持久性、恢复读与所有写者遵约|
|主行短写|当前_full一次write，短写抛异常；原部分字节保留|后续清理/终态/归档能否保存；部分行无法冒充完整事实|
|write成功、fsync EIO或确认前死亡|不退款，不据未收到返回再次append|完整行是否持久未知；cursor完成/退出收据须核原件|
|STOP/CLOSED已存在，即使内容损坏|RootIPC presence取消活动准入|该标记的身份/boot/格式、真实回收和native_ready另验|
|标记发布失败，只有_HALTED|当前进程的预算health拒绝；新配额需拒绝本角色新观察|跨进程可见停止尚未由内存flag推出；共享intent/监督/marker/退出证明必需|
|systemctl stop/kill报错或超时|现行代码尝试fallback并记录错误|payload_empty、已知Root角色退出、亲子waitpid分别确认；超时返回不保证全部退出|
|Root协调者死亡|外部停止器可按当前责任尝试回收|父waitpid若未保存，Receiver无法补造；native证据可保持UNKNOWN|
|native seal失败或部分ZIP|保留原raw与SEAL_ERROR/处置材料|完整包/hash/成员集合/版本校验，缺失保持NATIVE_SEAL_UNRESOLVED/FAILED|
|行政finalizer失败|host保留原始流、失败或finalization-error收据|行政归档独立UNRESOLVED；历史native结论按实际原件保留|

{S('src/manager_recovery.py',317)}的first_failure、ABORTING、回收、close_attempts与final状态按既有错误模型保留。其错误码/UNKNOWN不能替代真正退出。正常路径内部mr_close_state缺失时也可为UNKNOWN，与native/admin是否已封存分别呈现。

预留主日志、关闭记录、外部见证、native输出和行政输出是不同域。关闭池需要保证其他生产者不能先消耗其必要空间；当前只有数字草案，没有已部署的隔离/物理保留证据。外部host/control与Linux ROOT路径分离也未证明独立磁盘故障域。外部TCB的系统查询、原始日志或post-exit快照仅在自身确已取得并校验时可作停止证据。

T0、deadline、budget/R及旧关闭状态持续保留。停止/封存/terminal reader无预算初始化或新授权路径；异常不会产生新免费窗口。全局R在C09 idle关闭期间应保持，存在并发合法budget actor时还需核对最终原件。{J('COUNTEREXAMPLE_REGISTER.json')}登记缺共享标记和缺父见证边界。

本轮没有执行fsync/短写/EIO故障实验、真实组停止或Root注入。所有“可停止”结论保持对可信kernel/systemd/Root、可用当前监督、有效权限/期限和实际I/O结果的条件性；任意存储故障下成功native seal的承诺仍关闭。
'''
r['FULL_EVIDENCE_BYTE_CLOSURE.md']=f'''# 完整证据字节闭包与分层依赖

**COUNT_BOUND_PROVED：条件性继承旧scope；BYTE_BOUND_PROVED：完整资源合同尚未取得；CAPACITY_CONTRACT_NOT_READY。** {J('FULL_CAPACITY_GAP_TABLE.json')}列出15项具体缺口；{J('MANIFEST_ZIP_BOUND_ARITHMETIC.json')}提供manifest/ZIP代数。

旧封闭完整scope仍为raw≤4450、native成员≤4451、行政导出≤4452，普通成功行政ZIP≤4467。其前提为原源码/输入、单次activation、最多一次resume、固定actor/首错展开、无外加写者。mr_events.lock覆盖修正保持，PT-only的pt_expected_abort在该scope不可达。C09主日志已经占raw一个路径，行数增加不新增文件数。新quota/关闭/测试/外部oracle的真实集合差需要重算，旧值未自动覆盖新实施。

令R为全体raw唯一路径字节和，M_N为native manifest，Z_N为nativeZIP，H为host原始流/审计输入，S为源锁输入，M_A为行政manifest：

\\[U_N=R+M_N,\\quad Z_N=ZIP(U_N),\\quad E_A=R+M_N+Z_N,\\quad U_A=E_A+H+S+M_A.\\]

U表示每层ZIP未压缩输入，E_A表示实际snapshot导出字节。Root原件和admin快照都保留时，新增磁盘保留还需计算两份E_A、host原件、M_A、行政ZIP和最终收据；source locks既有原件与新副本按实际路径区分。含在行政ZIP中的nativeZIP是一个独立成员，同时raw原件又被复制，两个成本均保留。

|组成|可核实子界/接受界|未闭合义务|
|---|---|---|
|C09 main|345148，v2条件；原源码无quota|待批未生效；关闭/其他原件未涵盖|
|关闭core|160＋H次尝试；237/260/1223/565等单项界|R/T/E/V、跨角色失败传播及其他关闭对象|
|其他logs/预算|条件校准journal15441008；全1m窗口471876988|writer生成与range/terminal32MiB接受条件统一|
|readiness/RootIPC/MR|read cap4MiB/128KiB；readiness602×131072=78905344|aggregate、失败staging、捕获前helper输出|
|S1–S9与Gate|trace cap乘积48×256×4096=50331648；固定测试列表|registry/journal/metadata/派生证明与异常联合字节|
|F1/F4及模型文件|固定输入/任务数和访问限额|状态/策略/trace/report编码、峰值对象分配|
|native metadata/ZIP|下述条件格式代数|R未闭合；格式和压缩参数前提；整文件hash内存|
|admin audit/host/raw streams|128次quiescence采样、一次host调用、旧读取cap|环境/proc角色数组、原始stdout/stderr、嵌入审计、最终错误收据|

单成员当前仅有部分读取接受cap和额外off_t64表示界；没有完整资源兼容的最大生成字节。假设4450个regular raw均受signed64 off_t约束，可给粗表示和41044005564003752341150 bytes；该值不会变成可用容量或完成保证。

Native manifest用RootIPC pretty indent2。取ASCII相对名F≤1535、off_t decimal≤19、clock宽度25/20，逐行语法代数得到M_N≤7436121。现有读取接受4MiB；粗界高于cap仅说明此证明无法覆盖接受要求，未证明真实固定路径可达到该极值。需要继续用实际路径族收紧，或在未来明确批准的版本内重新制定合同。

ZIP32既有profile下，4451项头部粗界14074084。若整个已接受U_N≤33554432，ZIP_STORED条件界47628516；另证pinned zlib默认参数compressBound式时，deflate条件界47696620。压缩后更小没有作为前提；这些粗界超cap也没有被当成实际必然超限。源R、native/行政两个归档输出的可用上界仍为空。

递归核验见{J('ARCHIVE_RECURSION_REVIEW.json')}与{J('EVIDENCE_LAYER_DAG.json')}。现行native按basename排除自身manifest/ZIP，然后只加入manifest一次；固定写者还需避免嵌套同名碰撞。control与ROOT不同域，行政outputs不会回流Root集合；最终收据及windows_entry的STARTUP_FINALIZATION_ERROR位于行政ZIP前像外。独立oracle只读或在前像外写收据，当前没有自动“直到成功”的归档递归。

DAG按首次成功、写者静止的native构建再接行政层分相。失败/部分native之后新增的SEAL_ERROR或处置记录只能进入随后真实可取的raw/admin集合；它们不会追加入已经消费的native前像。部分包始终按部分包裁决，不能用后层报告把它升级为完整封存。

新增识别的容量边界：STARTUP_NATIVE_AUDIT在export之前保存，files尚为空；完成export后stdout包含完整files和first_failure摘要；host最终收据又嵌入stdout解析对象。它们是不同实际视图，字节须分别计入。最终finalization-error也可能嵌入preserved audit，属于旧4452快照原件集合之外。数量有限不自动给这些内容一个可部署的字节界。
'''
r['ARCHIVE_WORK_AND_MEMORY_BOUND.md']=f'''# native、行政及独立校验的工作量与内存

**CRB-5=PARTIAL；完整WORK_BOUND_PROVED尚未取得；WALL_TIME_BOUND_UNRESOLVED。** 已接受且受完整输入cap约束的流式校验具有条件工作量界，整个生成/回收/构建链仍缺总输入和峰值证明。

|步骤|可明确的工作量|剩余边界|
|---|---|---|
|关闭核心生产|160＋H次记录尝试；字节W_core使用精确schema公式|160计量核心尝试，完整关闭另含其他文件；E/V/T等及staging/原始流仍缺数字|
|MR预算快照|每abort前后至多2次，A≤16时最多32次三文件扫描|每次读取counter＋intent＋journal；需J的生成字节界与扫描时静止性|
|待批v2局部日志|旧971216写字节、1316 durability尝试、retained350166保持原声明子集|调用界/失败不重试/跨角色责任尚未接线；不可加成全关闭证明|
|native构建|排序O(N log N)，raw hash一次＋ZIP读取一次，加manifest|{S('src/guard.py',96)}digest整文件read_bytes；未知最大raw会影响峰值；压缩库参数/输出未闭合|
|runtime TR独立读|已接受compressed/uncompressed各32MiB；manifest4MiB；成员当前257；64KiB块CRC/hash|ZipFile构造与中央目录分配先于成员count检查；对象常数和TCB内存尚需证明|
|maintenance双oracle|原审查组件各受32MiB/4MiB/名字/EOCD/成员集合约束，O(N+B)流式校验|未部署；不能把组件read限制自动当成现行生成/资格合同|
|post-exit原生核查|按manifest逐成员hash；导出64KiB读取/hash/copy|{S('src/startup_lifecycle.py',461)}使用z.read整成员；/proc环境扫描不受当前slice TasksMax4约束|
|host finalizer|逐份copy hash、归档、z.read复核；nativeZIP作为成员再读取|raw host流、审计数组和最终收据可能多次物化；未有全量峰值界|

对一份已接受总未压缩B、成员N、路径最大F的归档，读取/CRC/hash可写O(B＋NF)，排序比较需O(N log N×F)。两个oracle各自完整扫描，不共享单个hash结论；行政层nested nativeZIP本身的压缩文件字节亦需处理。单份输入有限的结论只对已接纳集合成立，不能替代全部必需生成对象均会通过检查的证明。

数据I/O调用次数也单独计量：BC私有put通常file＋同目录fsync；RootIPC跨目录put为file＋destination＋private fsync；mr_close_attempt append只有file fsync。payload和host write_text/ZIP close并未形成与RootIPC相同的磁盘durability合同。上轮1316已经含其声明的两标记，不能再次当作全链fsync总数。

FD方面，TR固定目录链8、boot1、counter1、phase1、ZIP open/dup2构成13个已列增量FD；还需进程既有FD、短时文件、pidfd、socket和helper PIPE。stop_other_roots至多2个目标pidfd，异常分支和并行角色另计。当前未批准新NOFILE值，完整峰值FD为UNRESOLVED。

工作内存包含raw read_bytes、JSON对象、路径/manifest列表、ZipInfo索引、hash/压缩缓冲、异常文本、subprocess捕获和行政审计的多份视图。AS1GiB可强制失败，但它不提供所需工作能在该内存内完成的结论。32MiB压缩输入也会在ZipFile内部先展开目录对象，提前成员cap与对象常数应独立审查。

保持旧visit68498和潜在新预付256→68754（仅旧项＋该预付，未含新增测试/核验Δ）。global1m、calibration100k、300s、preT0120、stop1740、全窗1800及terminal5s/admin30s原合同保持。有限循环次数/fsync次数不足以推出最坏墙钟；调度、存储、阻塞syscall、manager和外部Windows wait均需另证。当前无新动态时间或资源资格证据。
'''
contract=read(CP)
field_table='|字段|依据/候选子值|状态|\n|---|---|---|\n'
for f in contract['fields']:
    field_table+=f"|{f['field']}|{f['basis']}；{f['candidate_component_or_old_value'] if f['candidate_component_or_old_value'] is not None else '待证明，未选择数值'}|{f['status']}|\n"
r['CAPACITY_CONTRACT_APPROVAL_DRAFT.md']=f'''# 版本化容量合同审查稿

**CAPACITY_CONTRACT_NOT_READY；正式生效审批BLOCKED。** 精确对象为{L('DCL-CLOSE-CAPACITY-REVIEW/1-DRAFT',CP)}，版本CloseReserve-Closure/review-1，SHA-256 `{sha(CP)}`。关闭子审查对象{L('DCL-CLOSE-RESERVE-REVIEW/1-DRAFT',CL)}的SHA-256为`{sha(CL)}`。

以下15字段完整保留当前依据和未决值；它们是待审查的版本化材料，没有把旧包络、接受cap或数学表示界转换成新的生产上限。

{field_table}

原件/成员/导出4450/4451/4452只适用于旧冻结scope；new quota/测试/新关闭处理及后层证据须按集合差再算。完整raw、单文件、归档输出、关闭池、manifest/索引、内存/FD/IO和墙钟闭合之前，新版本的总限额与生效标志均保持null/false。现行256/257守卫保持逐字节一致。

可明确审阅的决定文本：

> 接受审查结论：我确认本版本的来源、条件子界及未决项清单用于继续静态闭合；这项决定不批准新容量、关闭保留量、实现或动态准入，MR规则继续单独待批。

> 退修：我要求进一步补齐所列字段和必要生产者证明后再审容量合同；原有效守卫与资源门继续保持。

当前不提供批准完整容量生效的选项。未来可批准版本须逐项填实并绑定：唯一source/input/execution锁、真实writer集合、路径/类型/权限、单项与总量、main/close隔离、完整原件集合/独立oracle、超额失败/UNKNOWN、包编码和IO/内存/FD、旧版本隔离、明确用户批准及独立实施/执行授权。审批容量和审批MR始终分开。
'''
r['MR_CROSS_INSTANCE_APPROVAL_STATUS.md']=f'''# MR独立审批材料状态

**MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE。** 原待批14条文本和规则均保持原字节，见{B('MR_CROSS_INSTANCE_FINAL_APPROVAL_TEXT.md')}、{L('MR原规则',MP)}，SHA-256 `{sha(MP)}`。本轮仅查材料完整性，用户批准/有效pair/A证书/B身份/use记录均未产生。

|独立审批项|原文本已规定的要求|当前状态|
|---|---|---|
|可承认类别|一个特定原生受控服务故障下观察到的自动关闭能力|原则草案；无通用未来关闭定理|
|当批重证|B的boot、WORK/C00、真实C09、管理器健康、budget/T0、单位/身份/运行时、当前监督与资源门|全部保持当批责任，历史A不能授予RESOURCE_GATE_PASS|
|等价条件|精确source/input/lock pair；namespace-only AST映射；同boot/TCB/UID/GID/kernel/systemd/Python/libc等|pair表为空；来源和独立.deb复现缺口保留条件性|
|故障真实性|原生raw query/journal、单位InvocationID/PID、事件码/时间、未审查拒绝|合成夹具和MR-SIMULATION不替代|
|自动关闭与组空|主自动路径STOP/CLOSED、真实已知角色退出、payload组空、原预算保持|fallback-only/缺失/必需UNKNOWN强制拒绝该类别|
|封存与oracle|A native/admin分别完整；逐件raw核验；后层certificate在A包前像外|当前无已接受A证书|
|单B使用/撤销|use_spec→新授权→use记录、fresh nonce；版本/boot/源/作用域/撤销变化即失效|未知授权/撤销状态或重放拒绝|
|批准范围|只替换强化合同那一项有限异常场景观察证据来源|实现、扩容、动态A/B和F1/F4均需独立授权|

容量与关闭草案的任何条件证明均不激活MR。历史服务故障、组空或native成功封存只归属其原实例和实际作用域；本轮没有将其转入新批次资格。
'''
r['GENERAL_BASELINE_AND_SEPARATION.md']=f'''# 强通用方法与分离门

全部工程选项为**COVERED_BY_G**。比较输入族为单handoff的n次缺witness观察、有限并发关闭、诊断输出和存储异常；指标为保留字节、写入/fsync工作、至多一次额度和关闭证据完整性。

最强适用G可以采用标准有界WAL/预付槽、持久幂等token、串行首错/关闭、独立预留空间/外部见证、标准manifest与ZIP。它能够实现本轮相同的逻辑合同和分层证据结构。预测严格差距0；没有找到一个输入实例迫使G支付更高的必要代价。{J('GENERAL_G_COMPARISON.json')}给出完整比较字段。

CE-257与重复关闭说明现行工程合同的缺项；CLOSE/IO/parent-witness反例说明容量、终止与证据可用性前提。它们没有构成相对最强G的架构分离。普通工程维护选项可以保留供以后具体审批；本轮实现与新机制代码均0。

STRICT_SEPARATION_INSTANCES=0，IMPLEMENTATION_GATE=CLOSED。任何未来架构候选仍须在实现前给出具体输入族、指标、最强G、预测严格差距及至少一个必要更高代价实例。当前没有原创性升级。
'''
gap_table='|ID|真实生产者/位置|缺少的准确约束|\n|---|---|---|\n'
for g in read(E/'FULL_CAPACITY_GAP_TABLE.json')['gaps']:
    gap_table+=f"|{g['id']}|{g['producer']}；{g['site']}|{g['missing']}|\n"
r['UNRESOLVED_BOUND_CHECKLIST.md']=f'''# 未闭合约束清单

**当前按此表停止扩容数值猜测。** 每项有真实生产者；完成静态来源/TCB/编码证明或提出明确待批字段合同后，才能继续选定新上限。

{gap_table}

优先顺序为关闭core的R/T/E/V、全部关闭原件/角色责任、terminal review与payload/host错误流，再做全raw/manifest/ZIP/admin总量。237、260、1223等子界是新进展；完整N_close,max/B_close,max/B_C09,max/R_raw/U_native/Z_native/U_admin/Z_admin均未取得资源兼容数值。

核验T阈值502、manifest粗界7436121和ZIP条件界时，必须保留适用profile；这些分析数值没有成为新限制。1322/948/1028及345148仍只属于原v2主日志合同；350166仍为局部声明集合。所有新测试/元数据/关闭尝试和外部材料均需计入Δ文件/字节/visit/IO。

状态独立维护：COUNT_BOUND_PROVED（旧scope条件性）；BYTE_BOUND_PROVED（完整未取得）；WORK_BOUND_PROVED（仅已接纳输入的局部检查条件性）；WALL_TIME_BOUND_UNRESOLVED。原256/257与预算/期限规则保持，审批、生效、实现和运行收据均未生成。
'''
scope=read(E/'FUTURE_CHANGE_SCOPE.json')
change_table='|候选文件|未来需审查的函数|合同变更责任|\n|---|---|---|\n'
for x in scope['minimum_behavioral_candidates']:
    change_table+=f"|{L(x['file'],RUNTIME/x['file'])}|{', '.join(x['functions'])}|{x['contract_change']}|\n"
r['NEXT_STAGE_AUTHORIZATION_REQUEST.md']=f'''# 下一阶段专项授权申请材料

本文件准备具体范围，**当前申请尚未获批，IMPLEMENTATION_GATE=CLOSED**。推荐先继续数值化关闭/错误/环境profile，全部条件明确后，再单独申请受G覆盖的最小静态维护。新动态链、WSL、真实故障和F1/F4均在本申请之外。

{change_table}

这些候选的diff只能位于将来新建的独立审查副本，旧ra01、batch14和所有历史字节继续冻结。最低输入合同集合为inputs/c09_contract.json、manager_contract.json、batch_identity.json、static_manifest.json、execution_lock.json、runtime_tree_lock.json，以及拟新增c09_quota_contract.json和close_reserve_contract.json；相关contract/schema/hash依赖须逐项重冻结。当前均未创建可执行新锁、身份、T0或预算。

如最终关闭/字段合同影响读者，src/terminal_evidence.py需要独立适配授权；完整行政容量若需生产端界，还涉及src/startup_lifecycle.py、host/startup_finalize.py，以及产生active-entry原始流、finalization-error和host wait的host/windows_entry.py。src/root_ipc.py仅在新target无法复用现有BC.Store私有.json域时纳入；权限、fsync和取消语义保持。具体条件与9个namespace字面量源文件的精确AST复核清单见{J('FUTURE_CHANGE_SCOPE.json')}，禁止宽泛字符串替换。

未来授权需要明确：采用的准确合同hash和字段上限依据；允许变更的文件/函数；全部原始字节及失败staging的保留规则；单首错/重复关闭/无标记EIO的责任；新文件/字节/visit/IO与静态负向检查增量；源码/输入/namespace/执行锁及独立raw oracle。常规工程维护与研究实施门的适用关系应随新授权明确，当前稿不自动获得例外。

继续保持预算预留核心、原native/admin安全准入、256/257和MR跨实例规则。完整关闭/字节/工作量未决时，可以申请继续静态证明；完整资源资格链申请仍需容量合同及所需独立规则、集成源锁和新的当批授权/资源条件全部到位。
'''
answers=[
 ('实际关闭生产者','36类，含主quota摘要草案、STOP两来源、MR首错/中间/最终/attempt、stop_event/result、真实父waitpid、native/行政/host收据；完整属性见生产者矩阵。'),
 ('耗尽后还需多少记录','完整最大值未定；干净Receiver abort已有8次核心发布/7路径；冻结核心包络160＋H次尝试、54稳定路径，封存/行政/退出遥测和staging另计。'),
 ('单条字节界','189只限固定43字节ASCII marker；ABORTING237、external260、waitpid1223/565条件成立；其余给R/T/B/E/V的逐字段式。'),
 ('关闭总字节界','CLOSE_RESERVE_UNRESOLVED；有明确总公式，B_close保持null。'),
 ('重复关闭是否无界追加','冻结once模型close_attempt≤16；一般API的E_n有n增长反例，属于旧数量界之外。CLOSED本身不禁止append。'),
 ('第257次如何拒绝','待批v2要求额度前置核验后0分类/0拒绝日志；当前源尚无该检查，仍保留257前缀反例。'),
 ('耗尽与故障并发能否安全停止','当前路径可尝试主停止/fallback；实际退出、组空、父见证和native/admin分别确认，容量与外部TCB条件尚不足以证明全路径完成。'),
 ('短写/EIO仍有什么保证','原始部分字节保留、失败槽不返还属待批义务；当前本进程HALTED/已有marker取消有源码依据；无共享marker时全局停止未由内存flag推出；UNKNOWN保留。'),
 ('345148与关闭是否重计','主行不含STOP/MR/回收；将旧350166中的marker/摘要/staging分配到C或O一次，不能整包再次叠加。'),
 ('全部C09最终条件字节界','345148＋B_close＋B_other_disjoint，后两项未闭合，尚无最终数值。'),
 ('完整证据字节是否闭合','完整资源兼容BYTE_BOUND_PROVED未取得；15项缺口具名，CAPACITY_CONTRACT_NOT_READY。'),
 ('native/admin资源工作是否闭合','仅已接受有界归档检查有O(N+B)等条件界；生成、raw/hash物化、环境扫描、内存、FD及全部IO未闭合。'),
 ('4450/4451/4452是否有效','原冻结scope和once/固定writer/first-failure前提保持时继续条件性有效；新quota/测试/错误收据/外部证明须单算集合差。'),
 ('完整容量是否可正式批准','BLOCKED；15字段审查稿完整、未决值null，原256/257保持，未提供生效扩容选项。'),
 ('哪些依赖待生效quota','256尝试/263行/345148、拒绝257、v2类别位/持久completion/终态锁存以及局部350166/971216/1316；当前源未自动拥有这些保证。'),
 ('哪些依赖Root/FS/外部TCB','稳定锁inode/无特权回滚、封闭writer、kernel pidfd/亲子身份、systemd/运行时来源、ABI/编码、fsync与当前监督/外部证据；EIO和Root死亡边界保留。'),
 ('MR是否未生效','PROPOSED_NOT_EFFECTIVE；原14条及hash保持，pair/A/B/use证据空，历史故障不产生新主批次资格。'),
 ('下一轮最小变更','先闭合R/T/E/V及terminal/host/profile；拟静态行为文件c09_handoff.py、guard.py、manager_recovery.py和精确合同/锁变更，依赖读者/行政/namespace调整单独列明。当前无实施授权。'),
 ('严格分离实例','0；COVERED_BY_G，预测严格差距0，IMPLEMENTATION_GATE=CLOSED。'),
 ('可申请完整资源资格链吗','当前条件尚缺；容量、关闭及工作量、所需审批/集成锁和新当批授权未齐；RESOURCE_GATE_PASS=NOT_OBTAINED，F1/F4保持UNRUN。')]
gates=[('CRB-1','PROVED','冻结域36类生产者和204相关调用点已枚举，属性和失败行为完备。'),
 ('CRB-2','PARTIAL','核心次数与部分单行条件界成立；重复API反例及字节符号缺口明确；CLOSE_RESERVE_UNRESOLVED。'),
 ('CRB-3','UNRESOLVED','完整关闭池/隔离/物理空间、跨角色失败及必要退出原件未形成充分资源证明。'),
 ('CRB-4','UNRESOLVED','全raw/native/admin字节闭包未完成。'),
 ('CRB-5','PARTIAL','已接受归档校验有条件界；全生成/内存/FD/IO与墙钟未闭合。'),
 ('CRB-6','BLOCKED','15字段版本稿与审批前提齐备；正式生效所需数值仍缺。'),
 ('CRB-7','PROVED','强G比较覆盖全部选项；严格分离0；无实现/动态。')]
gate_table='|验收门|状态|裁决|\n|---|---|---|\n'+''.join(f'|{a}|{b}|{c}|\n' for a,b,c in gates)
answer_table='|序号|最终问题|真实回答|\n|---:|---|---|\n'+''.join(f'|{i}|{a}|{b}|\n' for i,(a,b) in enumerate(answers,1))
r['FINAL_DECISION.md']=f'''# CloseReserve-Closure最终裁决

**关闭core次数与若干单行条件界已精化；完整关闭保留量、全证据字节与资源工作量继续未决。** 当前为`CLOSE_RESERVE_UNRESOLVED`、`CAPACITY_CONTRACT_NOT_READY`。本轮完成授权的只读审计、形式化代数、反例构造和合同材料，未启动实现或动态准入。

{gate_table}

新得到的可核验结果：36类关闭/退出/封存/行政生产者，204个相关静态调用点；旧scope A_abort≤16、S_stop≤23、Q_seal≤7及W_waitpid≤2，关闭核心≤160＋H次生产尝试、54个稳定路径粗界。H=0只适用于C09 idle/no-new-budget前缀；这些数字均未被当成完整关闭配额或新容量守卫。

ABI/固定schema下，ABORTING≤237、external_closing≤260、正常waitpid≤1223、异常waitpid≤565 bytes；marker为144＋R，quota固定43字节reason时189。first≤25054＋R＋T＋B；cleanup line≤998＋11T＋B；stop_result≤1151＋E＋ΣV_j。完整B_close仍含未决字段和其他必要对象。

上轮主日志345148及局部350166原条件保持；C09完整界写为345148＋B_close＋B_other_disjoint，尚无最终数值。当前关闭和封存空间不能由这两个旧数推出。MR、payload timing/stdio、terminal review、host/admin原始流和封存后错误收据均列入缺口。

重复关闭结论限定适用域：CLOSED后没有ZIP时，abort仍能追加close_attempts及stop_event/result；冻结单次角色图把它限制在声明次数内。域外E_n和接口stderr_m族分别标注，不将它们宣称为冻结执行的物理无界或已观察原生反例。短写/EIO允许UNKNOWN；本进程HALTED、真实清理、共享取消和证据完整性分别判断。缺父waitpid的Root故障轨迹可能已组空而native未就绪。

旧4450/4451/4452继续条件性适用原scope；完整BYTE_BOUND_PROVED和WORK_BOUND_PROVED尚未取得。已接受有界archive检查有O(N+B)条件界，native/admin生成、内存/FD和墙钟300/5/30秒继续未决。manifest7436121、ZIP条件粗界等均作为证明责任保留，没有用来扩大守卫或声称实际必达极值。

精确审查稿：{L('容量15字段草案',CP)} SHA-256 `{sha(CP)}`；{L('关闭审查草案',CL)} SHA-256 `{sha(CL)}`。两个稿的approved/effective/runtime_enabled全部false，完整总cap保持null。MR规则继续原SHA及PROPOSED_NOT_EFFECTIVE。

{answer_table}

完整证据索引为{D('EVIDENCE_INDEX.md')}；详细缺口为{D('UNRESOLVED_BOUND_CHECKLIST.md')}；未来精确文件/合同申请见{D('NEXT_STAGE_AUTHORIZATION_REQUEST.md')}。历史9867与前两轮307交付工件合计10174件保留字节，64运行源/输入、原维护/合同/预算/执行锁均纳入交付核验；根导航只前置新记录并保持原字节后缀，最终凭{J('DELIVERY_CHECK.json')}逐件核对。

本轮研究分析/报告脚本只读冻结材料、生成语法代数/表格和研究包，不含新日志/配额/关闭/封存机制实现。运行实现修改、WSL调用、动态测试、真实故障、F1/F4均0；T0/deadline/R=null。未授予任何动态PASS或重新开启旧实例。
'''

for n,body in r.items():
    heading,body=body.split('\n',1)
    (OUT/n).write_text(heading+'\n\n'+intro+body.lstrip()+tail,encoding='utf-8')
index='# CloseReserve-Closure研究证据索引\n\n'+intro
index+='本轮13份指定报告；所有运行资格与待批合同保持原状态。\n\n'
for n in r:index+='- '+D(n)+'\n'
index+='\n机器审查与证明：\n\n'
for n in ['INITIAL_INPUT_CHECK.json','FROZEN_SOURCE_LOCK.json','PRIOR_ARCHIVE_CHECK.json','SOURCE_CALL_CENSUS.json',
          'SOURCE_EXCERPTS.json','CLOSE_PRODUCER_MATRIX.json','CLOSE_COUNT_DERIVATION.json','CLOSE_SCHEMA_BYTE_ALGEBRA.json',
          'MR_CLOSE_ORACLE_COMPATIBILITY.json','CLOSE_TOTAL_FORMULA.json','QUOTA_BOUNDARY_FAMILIES_A_E.json',
          'COUNTEREXAMPLE_REGISTER.json','MANIFEST_ZIP_BOUND_ARITHMETIC.json','ARCHIVE_RECURSION_REVIEW.json',
          'EVIDENCE_LAYER_DAG.json','FULL_CAPACITY_GAP_TABLE.json','FUTURE_CHANGE_SCOPE.json','GENERAL_G_COMPARISON.json',
          'PROPOSAL_BINDINGS.json','DELIVERY_CHECK.json']:
    index+='- '+J(n)+'\n'
index+='\n'+Q('EVIDENCE_INDEX.md')+' · '+B('EVIDENCE_INDEX.md')+tail
(OUT/'EVIDENCE_INDEX.md').write_text(index,encoding='utf-8')
(E/'FINAL_GATE_DECISIONS.json').write_text(__import__('json').dumps({'gates':[{'id':a,'status':b,'basis':c} for a,b,c in gates],
  'final_answers':[{'number':i,'question':a,'answer':b} for i,(a,b) in enumerate(answers,1)]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print({'reports':len(r),'index':1,'answers':len(answers),'capacity_sha256':sha(CP),'close_sha256':sha(CL)})
