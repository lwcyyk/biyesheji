"""Requested mathematical/contract decision reports, no runtime implementation."""
from INPUT_AUDIT import ROOT,PREV,OUT,E,RUNTIME,read,save,sha
import json

def L(label,p,line=None):return '['+label+']('+str(p).replace('\\','/')+(f':{line}' if line else '')+')'
def S(file,line):return L(f'{file}:{line}',RUNTIME/file,line)
def J(n):return L(n,E/n)
def D(n):return L(n,OUT/n)
def P(n):return L(n,PREV/n)
A=OUT/'proposals/OPTION_A_KEEP_CURRENT.json';B=OUT/'proposals/OPTION_B_MINIMAL_REVISION.json'
matrix=read(E/'RESIDUAL_15_GAP_MATRIX.json')['rows'];hp=read(E/'H_FULL_SCOPE_PROOF.json')
intro=('## Material Passport\n\nDCL-R6-ResidualBounds-Decision；ResidualBounds-Decision/review-1；'
       '2026-11-16（Asia/Shanghai）；最后一轮既有15项责任的定向静态证明与合同决策。'
       'ANALYZED：未启动DCL业务、原生故障或模型执行。\n\n')
tail=('\n\nRESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；'
      'MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；PASS_BOUNDED=[]；'
      'STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。\n')
r={}
mt='|缺口|实际变量/范围|最终分类|最小处置|\n|---|---|---|---|\n'
for x in matrix:mt+=f"|{x['gap_id']}|{x['unresolved_variable']}；{x['occurrence_bound']}|{x['verdict']}|{x['minimum_constraint']}|\n"
r['RESIDUAL_15_GAP_MATRIX.md']=f'''# 15项剩余责任的终局分类

本轮结束同一冻结范围的静态审计。**当前合同CURRENT_CONTRACT_UNSAT；后续采用CONTRACT_REVISION_REQUIRED。** 不再以相同源/输入重复打开15项清单。新用户决定、量化TCB材料、批准后的具体diff或新证据可以定义新的审查输入。

{mt}

{J('RESIDUAL_15_GAP_MATRIX.json')}为每项保留全部要求属性：gap_id、producer、source、unresolved_variable、input_domain、occurrence_bound、byte_bound、trusted_assumption、existing_evidence、counterexample、minimum_constraint和唯一verdict。原编号G01–G15一一保持。

具体收敛：H已由角色图给出52，关闭核心最多212次生产尝试；MR固定调用reason的JSON token≤38。T/B/E/V仍依赖量化TCB/kernel profile，其中source-owned异常类名和健康预算映射已有子界。G12得到P5环境输入反例，目标是slice TasksMax4无法约束全局发现角色数；G13归入尚未存在的新实施/测试域，不再通过重读旧代码填造Δ。

stderr_m及一般API重复族E_n继续属于域外/未证明pinned可达性的接口风险。上界乘积超过32MiB没有被登记为实际超限实例；内存/物理文件表示空间也未被用来填应用层cap。
'''
r['VARIABLE_R_T_B_E_V_BOUND_AUDIT.md']=f'''# R/T/B/E/ΣV_j编码与实际输入域

最终状态：**R_MR为BOUND_PROVED（继承ABI/冻结调用域）；B为CONDITIONAL_BOUND；R_budget/T/E/V的完整数值为UNRESOLVED_EXACT，定量profile或新合同必须替代重复审计。** 变量的实际来源见{J('REASON_AND_VARIABLE_DECISION.json')}及{J('SOURCE_EXCEPTION_CLASS_CENSUS.json')}。

|变量|真实字段和生成者|现有边界|终局限制|
|---|---|---|---|
|R_MR|{S('src/manager_recovery.py',355)}first.reason；来自固定M.abort/M.fail调用|字面量、launch_one状态PASS/FAIL、COORDINATOR_CHILD_RETURN_＋原生退出整数。最大内容36字节ASCII、token38|仅这些调用方；任意abort(reason=x_n)属于域外|
|R_budget|{S('src/guard.py',84)}BUDGET_HALTED:＋str(exception)|H≤52；文件/锁/counter/JSON/clock/序列化错误来源|无source字节截取；完整pinned诊断目录/环境profile未给出数字|
|T|type(exception).__name__的JSON token|冻结应用自定义类名最大18 bytes；optional null以T≥4覆盖|导入的builtin/stdlib/native类名全集仍缺量化证书；18不能推广为全TCB|
|B|{S('src/manager_recovery.py',266)}三份ledger原件的hash/size或UNKNOWN/type映射|健康全成功≤387；一般B≤69＋3max(106,29＋T)|hash64和size≤20字符是继承ABI；读取整份ledger的工作量另算|
|E|{S('src/guard.py',761)}closure_persistence_error=repr(exception)|仅H锁、stamp和RootIPC marker发布的try产生；失败时可为null|后面的systemctl调用不在该try内，stderr_m没有已证路径进入E；需固定TCB文件/ACL/clock/JSON异常repr profile|
|V_j|{S('src/guard.py',175)}12个cgroup文件read_text().strip()的JSON token|文件名集合固定；pids与内存配置、stat位宽已知|导出键集、计数宽度、缺件/null及并发进程/线程列表语义尚未量化；parent slice文件未设MemorySwapMax|

Root reason逐调用证明：固定字面量有有限长度；r['status']由launch_one自行赋PASS或FAIL，最多4；退出code沿用signed32十进制≤11的保守ABI界。COORDINATOR_CHILD_RETURN_长度25，因此reason≤36。加MR_CRITICAL:/MR_FALLBACK:各12后，Root marker的reason token≤50，整行≤194。它是新的来源子界，未改变任何守卫。原固定43字节quota reason对应189继续成立。

first_failure中的str(error)[:2048]限制Unicode code point数。BC compact编码默认ensure_ascii=True，每code point最多12字节，内容≤24576、带引号≤24578。该限制不作用于reason、type名或E。RootIPC/payload metadata采用ensure_ascii=False的UTF-8 pretty JSON，任意单code point的编码/转义可达6字节；固定ASCII无需额外转义。各token定义含引号，字节、字符、JSON结构分别计量。

12个V依次来自pids.current、pids.max、pids.events、memory.current、memory.peak、memory.max、memory.swap.max、memory.events、memory.oom.group、cgroup.events、cgroup.procs、cgroup.threads。TasksMax4约束同时存在的受管task，单凭这一值无法完成所有seq-file列表及churn语义的字节证明。所有值经kernel接口生成，当前没有任意V_n是合法冻结内输入的证明。

R_budget与E也不能从“通用str/repr可很长”直接推出冻结域真实无界：两者的当前事务路径没有任意业务文本注入点，E尤其不接后续systemctl stderr。缺少完整定量TCB异常目录时，数值保持null；若选择强制有界错误wire/acquisition profile，则属于待批准合同。TCB目录或新限制是下一输入，旧源码同范围审计到此结束。

task_id在C09原生日志中缺席；生产range任务来自固定child_contracts的三个ID，ASCII长度最大{read(E/'FIXED_INPUT_WIDTHS.json')['production_task_id_ASCII_max']}；合成S1–S9固定job及L/R后缀最大{read(E/'FIXED_INPUT_WIDTHS.json')['synthetic_task_id_ASCII_max_with_LR']}。二者均与R/T/E分开，见{J('FIXED_INPUT_WIDTHS.json')}。PID/ticks/clock/hash/namespace的既有profile继续作为明确条件，未以OS物理内存有限代替应用层界。
'''
ht='|可发生H的上下文|数量|每上下文最多halt|小计|\n|---|---:|---:|---:|\n'
for x in hp['roles']:ht+=f"|{x['role']}|{x['count']}|{x['halts_per_context']}|{x['count']*x['halts_per_context']}|\n"
r['H_EVENT_BOUND_ANALYSIS.md']=f'''# H的完整执行域上界

**BOUND_PROVED：H≤52，N_close,core≤212。** 范围是原冻结完整工作流的有限角色/任务图和失败前缀，包含C00–C12、C09H、RANGE、FORMAL以及最多一次C09恢复；旧实例保持CLOSED，本结果不提供新的运行授权。

{ht}

总计36个可能的预算执行上下文，计权后52；它们并非同时运行。C00–C12有13个controller，C05另建1条预算worker线程；RANGE冻结34 jobs中12 crash＋2 concurrent各spawn一次，共14个worker；C02/C03/C04各一个prepaid claimer。controller monitor/watchdog没有halt_budget调用，合成Store mode非None时禁用生产halt catch。所有输入和调用证据见{J('H_FULL_SCOPE_PROOF.json')}。

单上下文归纳的关键是单调_HALTED：{S('src/guard.py',630)}在_reserve的try之前检查budget_health；{S('src/guard.py',703)}在Budget.visit的try之前检查execution_deadline；{S('src/range_core.py',116)}与{S('src/range_core.py',168)}也在reserve/claim的try之前valid。第一笔失败可在global_reserve catch688和Budget.visit catch709各调用一次halt；同线程随后入口在try外被拒绝。production range catch163/192最多一笔，之后同样被入口拒绝。无clear或重置；source模块alias由controller844固定，helper进程各只有一个自己的guard实例。

每个列明线程只允许一笔同步在途失败；C05并发的两个线程分别计入。固定父子spawn、Restart=no及无额外API调用闭合上下文数。Root initial/resume scheduler各用直接scalar reserve，至多一次；父协调者、外部停止器和watchdog没有global-reservation事务。继承16次abort、23次stop_tree和2次waitpid后：

\\[H\\le52,\\qquad N_{{core,attempt}}\\le160+52=212.\\]

|待回答关系|裁决|
|---|---|
|新任务/恢复/交接数量|通过固定actor/spawn图决定52；C09交接最多一次，恢复最多一次|
|预算事务/访问总量|成功事务上限不能独自约束失败H；在counter写入前错误可使R增量0却H增加|
|零访问重复|Budget嵌套同一次错误可能增加H两次；入口HALTED检查与有限线程数阻止无限重入。直接反复调用halt_budget(x_n)属于域外|
|CLOSED后增长|在途失败或尚未HALT的直接scalar入口，仍可在counter-lock deadline发现CLOSED后记录一次失败；它不会发grant，之后入口停在try外，总52已含此情形|
|idle前缀|没有新预算调用的C09 idle/no-new-budget关闭前缀继续H=0，作用域保持|

H计量budget-origin halt调用/STOP发布尝试，M.abort的STOP另已计入160；相同STOP路径覆盖写不会变成52个独立文件。因此稳定核心路径粗界54保持，212没有成为新关闭配额。_HALTED仍为进程内flag，52并不证明共享停止、组空或证据完整性。
'''
r['OTHER_PRODUCER_BYTE_BOUND.md']=f'''# 其他必要生产者的终局处理

本报告只处理G04–G12/G15已有责任。**CONTRACT_REVISION_REQUIRED**：固定生产次数、读取接受cap与可用的生成字节/内存上界分别维护；域外输入不冒充冻结漏洞。

|生产者|次数/固定结构|来源与剩余最小合同|
|---|---|---|
|MR first/cleanup|abort≤16，attempt行≤16；错误notes有限；首错固定路径|R_MR已闭合；T/B由pinned错误profile实例化，随后使用既有逐字段式|
|payload timing|每key最多8 first_samples＋last，固定调用labels来自锁定程序|repr(error)文本、计数宽度与全部key集合需要量化wire profile；样本数不会限制每样本文本|
|stdout/stderr|固定服务/helper/host stream槽位；一次错误逐层展开，无自动无限重启|已收到raw保持；helper/解释器实际输出的字节/acquisition/总量必须由合同决定|
|TerminalRead|每原JSON接受4MiB，固定元数据；保存native review为exclusive一次|嵌入raw树与metadata组成的输出wire包络；读者接受cap不能自动当writer cap|
|readiness/RootIPC/MR/S1–S9|固定jobs/actor，现有单记录cap、旧4450集合|78905344/50331648等cap乘积仅为上界；聚合超限判据、全部异常/staging仍需统一|
|journals|visit≤1m、固定range任务；conditional字节模型已有|生成字节/行数应与所有validator接受条件统一；上界大于32MiB不证明实际达到该值|
|F1/F4输出|固定输入、visit slices和任务数，无本轮模型执行|邻居生成/trace/strategy/report编码和峰值对象常数未认证；精确输出profile字段留null|
|native/行政构建|once流程、现有archive/raw完整性检查|新总量、单成员、manifest、压缩膨胀、heap/FD/IO需审批前闭合|
|host最终错误|一次finalization-error，可嵌入preserved audit|它位于admin ZIP前像之外，仍需单独保留字节；不并入4452 runtime快照原件数|

JSON重编码有一项可终结的子结论：普通成功解析JSON树无自定义hook/环，compact ensure_ascii=True重编码≤25×原输入字节。字符串每code point≤12输出字节，float≤25，integer十进制不扩大，容器/键从不重叠的原token逐项求和。Terminal返回最多4个可能的raw根（closed、stop、waitpid、SEAL_ERROR），各4MiB，故这些嵌入根的保守贡献≤419430400 bytes，再加固定/已验证metadata的K。此为CONDITIONAL_BOUND，未证明全部极值同时可达，也不证明输出适配32MiB、heap足够或整个报告最终总值。见{J('TERMINAL_REENCODING_LEMMA.json')}。

G12有一个冻结环境域内的具体反例，目标为“slice TasksMax4推出admin发现角色≤4”。令5个不同UID的普通进程在当前slice之外运行，实际执行无关程序，argv包含当前source/guard.py、--batch-root及ROOT；在合法preflight后、行政扫描前出现。{S('src/startup_lifecycle.py',392)}的role分支只匹配argv，不校验该分支的UID或InvocationID，因此roles≥5，同时当前slice可以为0。它们不写ROOT、不调用DCL函数、不修改TCB。返回会如实defer/UNKNOWN，未出现漏准入PASS。反例详情与环境前提见{J('AMBIENT_PROCESS_COUNTEREXAMPLE.json')}。

P_n说明全局/proc元数据需要自己的数量/argv/错误界，或正式批准等价的known-identity/current-cgroup发现合同；后者必须保留真实逃逸角色检查。当前旧writer域没有冻结整个主机的无关进程。若新合同另加全主机quiescence/no-lookalike假设，该更强域需要独立标明。

错误传播没有新增一个自动无限写循环：固定异常包装器按16/23/7/4包络展开；STOP可被覆盖，close_attempt可追加，native失败的SEAL_ERROR/处置走后续raw/admin层，行政失败收据在包前像外。一般API族E_n和stderr_m的pinned实际可达性继续与冻结调用图分开。源/输入不变时，这些责任不再重复审计，下一输入限定为合同决定或量化材料。
'''
r['CLOSE_RESERVE_FINAL_BOUND.md']=f'''# 关闭保留量最终表达式

**CONDITIONAL_BOUND已精化；完整关闭量为UNRESOLVED_EXACT。** 新结果消去了H与固定MR reason这两项自由量，未选定新的容量数字。机器等式见{J('CLOSE_CORE_REDUCED_FORMULA.json')}。

继承A≤16、S≤23、W≤2，代入H≤52、Root MR marker≤194、first≤25092＋T＋B、external260、ABORTING237、cleanup line998＋11T＋B、cleanup state997＋11T＋B、stop_result1151＋E＋ΣV和waitpid≤1223，可得：

\\[W_{{core}}\\le488421+368T+48B+23E+23\\sum_jV_j+52R_{{budget}}.\\]

B≤69＋3max(106,29＋T)。W_core为212次核心生产尝试的字节总和包络，可以保守上界这些目标/实际失败staging的保留量。ABORTING和final共用mr_close_state；STOP固定路径、attempt多行单文件；生产成本多次计，保留文件按路径/实际版本只计一次。式中没有把字节系数选为新quota。

关闭分区按原producer矩阵去重：core已经包含MR first/cleanup、stop_event/result、两个phase的waitpid及预算hash/size映射；exit额外项仅指尚未计入core的外部/行政退出原件；normal MR review、terminal/native/admin和其他raw流另列。完整量：

\\[B_{{close}}\\le W_{{core}}+B_{{exit,extra}}+B_{{MR,normal}}+B_{{terminal}}+B_{{other,disjoint}}.\\]
\\[B_{{C09,total}}\\le345148+B_{{close}}+B_{{otherC09,disjoint}}.\\]

旧350166局部集合已含main、cursor、首错摘要、两个标记及声明staging。组合时把这些对象分配到各集合一次，不能把350166完整再叠加345148或完整close集合。global ledger原件只保留一次，core中的B是嵌入摘要，不复制原始ledger全体。

完整数值仍需R_budget/T/E/V的定量TCB profile，以及exit/terminal/stdio/model/admin等既有字段包络。任一必需对象未闭合，保持CLOSE_RESERVE_UNRESOLVED、FULL_BYTE_BOUND_UNRESOLVED和CAPACITY_CONTRACT_NOT_READY。已得到的212、194、387、488421等都不授予动态准入。

短写/模糊持久化下，已消耗额度烧掉、已捕获raw保留，缺共享取消/父见证/组空/完整包时保留UNKNOWN。关闭池需要足够空间及隔离，普通存储成功前提须明确；任意存储故障下完成native seal的承诺保持关闭。此处的未决量已转为精确合同责任，旧范围证明到此终结。
'''
r['FULL_EVIDENCE_BYTE_AND_WORK_BOUND.md']=f'''# 全证据字节与工作量最终裁决

**FULL_BYTE_BOUND_UNRESOLVED；CONTRACT_REVISION_REQUIRED。** 保留旧scope条件性数量4450 raw、4451 native成员、4452行政导出；完整参数须加未来精确diff的Δ。G13属于未来域，当前无法通过旧代码实例化Δ。

令R_raw为唯一路径raw和、M_N为native manifest、Z_N为nativeZIP、H_host为host原始流/审计输入、S_lock为源锁、M_A为行政manifest：

\\[U_N=R_{{raw}}+M_N,\\quad Z_N=ZIP(U_N),\\quad E_A=R_{{raw}}+M_N+Z_N.\\]
\\[U_A=E_A+H_{{host}}+S_{{lock}}+M_A,\\quad Z_A=ZIP(U_A).\\]

Root原件与snapshot均保留时还应计量两份E_A及host、行政归档、最终收据的实际磁盘路径。nativeZIP在行政层重读和包内包的真实复制成本保留；相同字节内容不会使独立原件/输出消失。

|要求项|当前实际参数/计算|终局状态|
|---|---|---|
|总未压缩量|U_N/U_A上述式；R_raw、host/输出profile和Δ未填|UNRESOLVED_EXACT|
|单成员最大|各reader接受4MiB/32MiB或局部source cap；没有完整生成max|UNRESOLVED_EXACT|
|native manifest|ASCII名字F≤1535、off_t19、N4450时粗界7436121|CONDITIONAL_BOUND；大于4MiB接受cap不作实际超限证明|
|native ZIP|U_N=32MiB且ZIP32 profile时stored≤47628516；额外pinned zlib条件下deflate≤47696620|条件上界；实际完整生成U_N尚未闭合|
|行政ZIP|对R_raw＋M_N＋Z_N＋host＋source＋M_A按独立codec再次计算|UNRESOLVED_EXACT|
|hash/独立读取量|已接受输入每遍O(N+B)；MR预算snapshot最多32次三文件扫描；native hash＋ZIP read；admin copy/hash/ZIP/verify分别计遍|局部CONDITIONAL_BOUND，全链未闭合|
|工作内存|整文件read_bytes、JSON/ZipInfo/trace对象、pipe capture、host多个审计视图|UNRESOLVED_EXACT；AS1GiB为失败界|
|FD|TR列明增量13；helper/socket/pidfd/继承基线另计|完整max为null|
|syscall/存储I/O|212 core尝试已有有限结构；每项字节、glob/scan、短读/重试/环境前提另计|完整max为null|

冻结SOURCE的读取接受cap、固定记录数和表示空间分别保留。4450×(2^63−1)之类物理表示粗界不会成为精确应用层容量，任意上界超过cap也不会自动产生可达违例。阻断完整闭包的最小量化参数已列入方案B，未补入默认长度。

有限归档输入的流式独立checker可以维持O(N+B)；native builder在全raw界定前整文件哈希，postexit/host有z.read整成员，/proc扫描也有独立环境域。文件描述符与TasksMax分别计量；前置ZipFile目录分配与后置count检查的内存责任保持。

失败/处置/最后收据按时间前像分层：成功native构建取静止raw，后续失败raw不回填已经消费的native前像；admin输出在ROOT之外，receipt在自己ZIP前像之外。没有自动递归归档直到成功。部分包、后层UNKNOWN和完整性缺失持续保留。
'''
r['WALL_TIME_ASSUMPTIONS.md']=f'''# 完成时间与有限工作量的分离裁决

**UNRESOLVED_EXACT：WALL_TIME_BOUND_UNRESOLVED。** 已核实的5/30/300/1800分别属于不同作用域，不能合并为全链成功完成时间。见{J('RESOURCE_TERMINATION_DECISION.json')}。

|数值|真实绑定位置|可宣称的作用域|
|---:|---|---|
|5秒|{S('src/terminal_evidence.py',196)}及terminal_contract.read_seconds|terminal只读检查的截止；guard.seal还含运行时核查、停止等待和归档，缺整体5秒包络|
|30秒|{S('src/admin_postexit.py',46)}、startup_contract.postexit_admin_timeout_seconds|Linux行政child的alarm；host父进程等待32/35秒后还有自身ZIP/hash，无整体30秒deadline|
|300秒|boot_contract.calibration_seconds及当前calibration检查|软校准窗口/准入与停止判断，未得到完整成功WCET|
|1800秒|共享state.deadline与boot total_seconds|全批原截止；1740 stop策略和unit RuntimeMax维持，不构成任意kernel阻塞下的真实退出上界|

Windows active入口{S('host/windows_entry.py',42)}的process.wait自身没有timeout。deadline检查依赖获得CPU并从syscall返回；SIGALRM/systemd timeout/kill是处理机制，D-state或外部响应延迟仍需明确模型。普通可信kernel和fsync正确性前提没有提供最大调度/响应时延。

若要声称严格成功完成时间，至少需要T_cpu/scheduling、read/write/fsync、systemd/query/stop/kill/reap、host/WSL返回的定量最坏界，及资源内存/FD/吞吐峰值证明。给定操作计数n_i也只能写总时间≤Σn_iτ_i＋T_cpu＋T_schedule；缺τ_i不能求值。

允许环境模型里可选择一次足够长的调度或存储延迟，使有限工作错过300秒；该推理反例针对“有限工作⇒严格时间”的推导，证据类型为静态分析，原生故障执行仍为0。合同须决定采用定量环境前提，或明确以超时/UNKNOWN和限定环境实测为目标。当前无新动态授权，不进行时延测试，不放宽已有期限。
'''
r['CURRENT_CONTRACT_UNSAT_PROOF.md']=f'''# 原256/257合同下完整成功链不可满足

**CURRENT_CONTRACT_UNSAT**，正式标签`FULLCHAIN_UNSAT_UNDER_CURRENT_CAPACITY_CONTRACT`。目标为包含全部必需原件、被接受native封存和行政导出的完整成功链。该结论覆盖所要求的验收目标；某个业务进程是否能启动是另一个命题。

证明使用强制生成的下界，不使用4450等上界。{S('src/c09_regression.py',59)}按冻结34 jobs产生204个事件JSON和34个oracle.json，合计238个互异regular文件。{S('src/root_ipc_regression.py',222)}按56 jobs产生互异ipc_case_000…055。{S('src/guard.py',1086)}的完整C09前置流程要求两套回归成功，它们的路径互不相交且成功流程不删除这些原始文件。

|独立矛盾|最小路径子集|包含义务|接受守卫|结论|
|---|---|---|---|---|
|Native|238个C09H原件＋前19个IPC原件=257 raw|全raw＋native manifest1⇒至少258成员|{S('src/terminal_evidence.py',158)}≤257|258≤257，矛盾|
|Admin|238个C09H原件＋前17个IPC原件=255 raw|quiescent导出全raw＋native manifest＋nativeZIP⇒至少257文件|{S('src/startup_lifecycle.py',503)}及startup_contract.admin_max_files=256|257≤256，矛盾|

每个三子句矛盾核心分别为：①完整成功要求对应raw子集，②全量包含关系，③原count cap。删除任一子句都可给非负整数的计数满足赋值；native移除一个witness raw后256＋1=257可满足该单独守卫，admin移除一个后254＋2=256可满足该单独守卫。此为计数核心的包含极小性/见证基数极小性，未声称删一份原件后程序还能完成全部资格。

{J('CURRENT_CAPACITY_UNSAT_WITNESSES.json')}列出257和255条实际必需路径、源位置及每一删句满足赋值。原887/1082/1083等更强下界继续保留，无需重复求解。byte/ZIP粗上界越界没有被用来证明UNSAT。

native builder可能先创建大于257成员的文件，257守卫在既有ZIP被TR验证时检查；“文件已创建”与“被当前合同接受”分别判断。行政导出256是实际复制时的拒绝线。保持全部原始证据、现行判据和256/257时，完整成功验收集合为空；直接启动只能制造已知不满足目标的尝试。

方案A可以作为“冻结现行合同并接受该负面结果”的明确决定。当前拒绝其下完整成功链/F1F4动态申请，不自动减少必需测试、删除原件、改变格式或扩大守卫。
'''
bp=read(B)
pt='|参数|数值/表达式|依据与审批状态|\n|---|---|---|\n'
for x in bp['parameters']:
    pt+=f"|{x['parameter_id']}|{x['value'] if x['value'] is not None else 'null'}|{x['derivation']}|\n"
r['MINIMAL_CONTRACT_REVISION.md']=f'''# 方案B的最小版本化合同修订

**CONTRACT_REVISION_REQUIRED。** 精确对象{L('OPTION_B_MINIMAL_REVISION.json',B)}，SHA-256 `{sha(B)}`。其approved/user_approved/effective/runtime_enabled全部false，当前守卫保持原字节。

{pt}

每个参数在JSON中独立给出真实producer、必须限制的input_family、derivation、overflow、安全影响、candidate_files、negative_tests和生效前提。256是显式工程政策；263和345148由实际生产者/codec推导。新文件/member/总字节/关闭/错误profile等数值保持null，现有4450/4451/4452只作为旧scope的基线表达式，实施Δ出现前不选新cap。

待审阅的最小条款：

1. 主额度为256个准入分类尝试、6类进度和ACK各一次，主行≤263、按1322/948/1028预扣345148；身份/boot/源/授权绑定与原ACK/commit/witness标准保持。
2. 在C09 controller/ready/counter固定前用既有scalar primitive预付；七类别位、cursor预扣/完成、终态锁存、不可退款/重建、最后PENDING完整保留及拒绝257无新增错误行。合法延迟见证可能资源耗尽关闭，活性代价明确。
3. 关闭池独立计量，H52与核心212作为当前图的证明结果；B_close及跨角色无标记EIO责任须在新版本量化，禁止把212解释为自动获批日志配额。
4. 量化实际pinned TCB/kernel异常与V profile，或批准有界typed control与raw acquisition合同。若采用有界acquisition，已捕获原始字节完整保留，超额或未捕获尾部明确标为证据不完整/UNKNOWN，不能声称完整原始封存或PASS。此项改变完整性责任，必须明确批准。
5. 所有原件/成员按精确diff集合差计算，新raw/member/export数量及单项/总raw、manifest、ZIP、heap、FD、IO值留null；既有journal等producer生成责任与所有接受oracle统一。
6. 对G12选择全局进程/argv/错误输入包络，或批准以已知身份/当前cgroup为域且保留等价逃逸角色检查的发现规则。batch task cap不会自动转成host输入cap。
7. 超限为资源失败，停止新工作；保留预算/期限、raw/partial/staging、首错、独立退出与原件oracle。缺失/IO失败/部分归档保留UNKNOWN，禁止省略必要证据以获得通过。
8. 新合同、输入/源/执行锁及namespace必须版本隔离。容量生效、MR、源码修改、动态执行四类许可分开；任何原则批准均不激活旧实例或新批次。

可以审阅主quota三项、版本隔离/原件完整性原则及停止/UNKNOWN政策；完整容量生效仍被null参数阻断。当前只能提交限定维护申请；完整工程适配/部署和完整链动态执行条件尚未齐备。
'''
r['GENERAL_BASELINE_AND_SEPARATION.md']=f'''# 通用方法与分离门终局

**COVERED_BY_G；STRICT_SEPARATION_INSTANCES=0。** 输入族为同一handoff的缺witness观察、预算失败、重复关闭/错误和受约束raw证据；指标为保留字节、生产/持久化次数、额度至多一次、证据完整性及处理工作量。

强通用G采用标准有界WAL、预付slot、持久幂等token、独立关闭/紧急保留、固定typed错误与raw通道、版本化manifest/ZIP和独立原件oracle，可覆盖现有工程选项。预测严格差距0；没有实例证明G必须承担更高必要代价。

H52/R_MR38为冻结源码证明精化，P5和计数UNSAT为现行约束反例/不可满足性分析，均未构成原创架构的严格分离。方案B属于成熟工程维护候选。架构实施门继续CLOSED；源码修改仍等待明确维护授权，本轮实现代码0。

未来如提出研究机制，仍须先提供具体输入族、指标、最强G、严格差距和必要更高代价实例。当前审计不再以扩大问题范围寻找一个替代性原创声明。
'''
r['APPROVAL_DECISION_PACKAGE.md']=f'''# 两方案与四类独立审批

本轮明确建议：**停止旧范围重复审计；方案A下完整成功链申请判CURRENT_CONTRACT_UNSAT；如继续工程工作，选择方案B的有限原则与分阶段维护申请。** 当前没有代用户作任何批准/拒绝记录。

方案A对象{L('OPTION_A_KEEP_CURRENT.json',A)}，SHA-256 `{sha(A)}`。方案B对象{L('OPTION_B_MINIMAL_REVISION.json',B)}，SHA-256 `{sha(B)}`。旧关闭/容量草案hash分别44980a113bda747f5e4e64ce47d6b782290a47e8bd3699f59623ecb0b045714a、44308e849c9ea2451cc1eb1443c00b88a874f523739d4129c202446132246d07；原文件使用user_approved=false，没有字面approved字段，effective/runtime_enabled均false，未决cap仍null。

|许可类别|当前状态|具体可决定事项|当前拒绝/阻断|
|---|---|---|---|
|CAPACITY_CONTRACT_APPROVAL|未批准；已知逻辑子条款REVIEW_READY|B主quota256/263/345148、隔离、原件与溢出UNKNOWN等原则|完整总cap/关闭/文本/内存/FD等null未填，生效审批BLOCKED|
|MR_CROSS_INSTANCE_APPROVAL|PROPOSED_NOT_EFFECTIVE|原14条有限证据承认原则可独立审阅|A/B/pair/use尚缺；历史MR不授予新RESOURCE_GATE_PASS|
|NATIVE_IMPLEMENTATION_AUTHORIZATION|尚未授予|B1两行为文件和列明输入的独立静态维护diff请求|当前运行源/旧锁/预算核心、未列范围及任何执行保持冻结|
|FULLCHAIN_DYNAMIC_AUTHORIZATION|尚未授予|未来满足全部量化合同/精确锁/当批门后单独申请|A完整成功目标UNSAT；B尚缺数值与当前资格；WSL/注入/F1F4均0|

可直接采用的独立决定文本：

> A：我选择维持现行合同，接受该合同下完整成功资格链不可满足的裁决；不再对相同冻结范围重复静态审计或启动完整链尝试。该决定不授予新的动态权限。

> B逻辑：我采纳所列方案B的256/263/345148主quota及版本隔离、原件完整性、溢出/UNKNOWN原则，供下一阶段限定维护。其余null项目继续作为生效阻断；此决定不等于源码修改、总容量生效、MR或动态批准。

> B1维护许可申请：在逻辑条款明确后，申请仅在独立副本对src/c09_handoff.py、src/guard.py及列明quota输入/manifest/静态审查锁编写可审阅维护diff；既有预算核心、旧256/257、MR承认和全部历史保持。当前申请文件尚非许可，动态运行仍需独立授权。

MR原文本与SHA-256保持{L('原14条规则',ROOT/'DCL-R6-C09-BoundClosure/proposals/MR_CROSS_INSTANCE_FINAL_RULE_DRAFT.json')}，摘要9c7524d7af3530b27f4c35d4fef92d9f2f3e431633967b555483b0b58085d069。核查记录见{J('MR_RULE_RECHECK.json')}；承认类别、当批重证、精确source/TCB pair、故障真实性、主自动关闭/组空、预算与两层封存、nonce/use顺序、失效撤销和强制拒绝分别保持。两份新方案也全部approved/effective/runtime_enabled=false。

明确拒绝以默认大整数填cap、直接放宽旧守卫、把域外stderr_m/E_n当原生漏洞、把已有hist测试当新PASS，以及把部分原则批准合并成四类许可。后续输入应为明确决定/量化profile/精确diff，旧范围审计在此结束。
'''
r['NEXT_STAGE_AUTHORIZATION_REQUEST.md']=f'''# 下一阶段有限维护申请

**CONTRACT_REVISION_REQUIRED。** 同一冻结范围的静态审计到此终止。下一步应由用户选择A保留负面结果，或明确采纳B的逻辑条款后，单独决定B1源码维护请求。当前SOURCE修改和动态权限均未获得。

最小B1行为范围只有两份独立副本文件：{S('src/c09_handoff.py',75)}的event/publish/sender_prepare/Receiver.observe_exit，以及{S('src/guard.py',1084)}的C09预付编排、输入/授权hash绑定和现有异常路径衔接。使用既有scalar预付，放在controller/ready/counter固定前；不改预算事务核心。quota cursor/首错可复用现有Root-private BC.Store.json域，所有stage/ACK/分类token按原v2规则共享H锁，终态完成后解锁再调用既有停止器。

输入范围为拟新增inputs/c09_quota_contract.json、受影响的inputs/c09_contract.json，以及新static_manifest/execution静态审查锁。任何因hash/namespace更动产生的依赖输入和既有9文件AST namespace映射必须逐项列入diff与Δ，旧batch14/ra01路径不可执行或重开。正式部署身份/资源/argv锁仍未签发。

申请的必需负向检查覆盖最后额度并发、stage/ACK重放、terminal cleanup间隙、预扣/完成崩溃、短写/EIO、foreign/missing cursor、256th raw保留和257拒绝。它们是未来明确授权后的检查义务，本轮未编写或执行这些运行机制/故障检查。

B1不包含全部15缺口的广泛实现。R_budget/T/E/V、terminal/model/timing/raw-stream、admin发现域和后层错误profile必须由量化材料或明确新合同给出数值/完整性政策；后续若需manager_recovery、terminal、startup或host writer变化，应另提交精确范围。G13新产物Δ只有具体diff后才可计算，继续重读旧代码不能生成该证据。

完整容量生效与完整链动态许可都保持阻断。主quota标准工程维护不构成架构原创性升级；原研究分离门CLOSED和严格实例0保持。只有用户明确的维护源码授权才能启动B1，任何逻辑选项/elapsed time/报告完成均不自动授权。
'''
answers=[
 ('R/T/B/E/ΣV意义','R_MR为固定角色reason token，R_budget为预算异常str token；T为异常类名；B为三ledger摘要map；E为marker发布try中的repr；V来自12cgroup文本。'),
 ('源码已有界','MR reason token≤38/Root marker≤194；source-owned异常类名token≤18；健康B≤387、B(T)函数；H52/core212；固定jobs、reader/local caps。'),
 ('待批准限制','主256/263/345148未生效；完整diagnostic/cgroup/model/stream/admin/wire/总量/资源profile尚需明确数值或合同，禁止默认填充。'),
 ('H完整域是否有限','BOUND_PROVED：36个固定可能上下文计权H≤52；failed visits不必付R，有限界来自HALTED入口与actor图，不来自成功访问数。'),
 ('哪些增长族域外','一般API E_n、直接任意halt/abort reason=x_n、未验证pinned可达的stderr_m；它们没有推翻冻结有限调用图。'),
 ('其他原始流是否未限','helper/payload/host stdout/stderr、timing repr、后层错误与模型/terminal输出缺统一生成wire/aggregate；固定槽位与样本数不能替代。'),
 ('关闭量是否闭合','完整数值未闭合；core精化为488421＋368T＋48B＋23E＋23ΣV＋52R_budget，再加互斥归属的其他必要对象。'),
 ('C09总量是否闭合','345148＋B_close＋B_other_disjoint，后两者未实例化；旧350166仅局部声明集合。'),
 ('全证据字节是否闭合','FULL_BYTE_BOUND_UNRESOLVED；任一强制对象缺数值就维持CAPACITY_CONTRACT_NOT_READY。'),
 ('native/admin工作是否闭合','已接受有界oracle仍O(N+B)条件界；全生成/hash/捕获/扫描/heap/FD/syscall/IO缺完整数字。'),
 ('墙钟缺什么','5只绑定terminal reader，30绑定Linux admin child，300/1800为现有窗口；全native/host ZIP没有对应总5/30界；缺最大调度/IO/manager/host返回时延。'),
 ('旧守卫完整链可满足吗','CURRENT_CONTRACT_UNSAT：257必需raw＋manifest⇒native≥258>257；255raw＋native两输出⇒admin≥257>256。'),
 ('最小修订条款','B的13组参数逐项给producer/族/推导/溢出/安全/文件/负向检查/生效前提；已知主quota与隔离原则可审，其他保持null。'),
 ('哪些可审批','逻辑256/263/345148、版本隔离/完整原件/溢出UNKNOWN原则；MR原14条独立原则；B1限定维护申请可单独提交，当前仍未批准。'),
 ('哪些null','完整关闭、TCB诊断/cgroup/profile、mandatory wire/raw流、admin环境域、新file/member cap、总raw/ZIP、内存/FD/IO/syscalls及严格时延。'),
 ('哪些被G覆盖','有界WAL/预付slot、幂等写、独立关闭预留、typed错误/raw通道、标准manifest/ZIP及版本合同全部COVERED_BY_G。'),
 ('严格分离实例','0；预测严格差距0；未出现迫使最强G承担更高必要代价的输入。'),
 ('是否具备实施申请条件','可以提交精确B1成熟维护diff申请；当前未获得源码许可。完整容量/部署实现仍被null与Δ阻断。'),
 ('下一步批准/拒绝','选择A接受UNSAT并结束该实验路线，或审B逻辑/B1有限维护；拒绝A完整成功执行、任意放宽守卫、null生效和四类许可混用。'),
 ('可进资源链/F1F4吗','当前不能；完整成功目标A不可满足，B未生效/未集成/未取得当批资格，动态权限0，F1/F4继续UNRUN。')]
at='|序号|验收问题|最终答复|\n|---:|---|---|\n'+''.join(f'|{i}|{q}|{a}|\n' for i,(q,a) in enumerate(answers,1))
r['FINAL_DECISION.md']=f'''# ResidualBounds最终决策

**CURRENT_CONTRACT_UNSAT；CONTRACT_REVISION_REQUIRED。** 本轮终结既有15项定向静态审计：已证界保留，域外输入单独归档，未闭合项目转化为明确合同参数/证书/diff责任，停止同一范围重复扫描。

新增BOUND_PROVED：冻结有限角色图H≤52，关闭core≤212次生产尝试；MR固定reason token≤38，Root MR marker≤194。CONDITIONAL_BOUND：core生成字节≤488421＋368T＋48B＋23E＋23ΣV＋52R_budget，B≤69＋3max(106,29＋T)；健康B≤387。完整C09/关闭/全raw/native/admin字节及工作资源保持UNRESOLVED_EXACT，主345148与旧局部350166的待批条件维持。

COUNTEREXAMPLE分类分开：现行C09 stutter257保留其有限前缀前提；P5在既有/proc环境域反驳TasksMax4对admin角色数的推导，代码如实defer而非授予通过。一般API E_n/任意reason输入和未验证pinned可达stderr_m保持OUTSIDE_SCOPE/接口风险，未被当作实际无界漏洞。

原256/257合同的成功目标存在两组计数极小矛盾核心，见{D('CURRENT_CONTRACT_UNSAT_PROOF.md')}：257个不可省原件加manifest至少258 native成员；255原件加native两输出至少257行政导出文件。已写出archive或业务进程启动均不等于当前全量证据合同接受。现行守卫和所有历史保持。

方案A为冻结当前合同并接受完整成功链UNSAT；方案B只在明确批准逻辑子条款、量化剩余profile、精确独立维护diff/Δ和新锁后才能申请容量生效/动态。四类许可各自裁决：CAPACITY_CONTRACT_APPROVAL、MR_CROSS_INSTANCE_APPROVAL、NATIVE_IMPLEMENTATION_AUTHORIZATION、FULLCHAIN_DYNAMIC_AUTHORIZATION。当前均未授予生效/运行权限。精确可审对象与文本见{D('APPROVAL_DECISION_PACKAGE.md')}。

{at}

15项唯一分类与全部属性在{D('RESIDUAL_15_GAP_MATRIX.md')}；H、变量及其他producer各有源码位置/输入域/精确理由。下一阶段只有明确用户决定、新量化材料或获准diff会重新定义审查输入。Root导航同步为该决策，未设自动推进或重复审计任务。

旧关闭/容量草案hash与flags已核验：原字段为user_approved=false，字面approved字段缺席，effective/runtime_enabled=false；未决cap仍null。本轮新A/B对象approved/user_approved/effective/runtime_enabled均false。原MR14条规则hash9c7524d7af3530b27f4c35d4fef92d9f2f3e431633967b555483b0b58085d069保持。

历史9867与此前450交付工件共10317件旧文件及64运行源/输入纳入最终hash核对，原4导航完整字节后缀保留。运行源/预算核心/C09/MR/Guard/native/admin/gate修改0；WSL、动态/真实故障/F1/F4运行0；T0/deadline/R=null。研究分析/报告/数学核验程序只操作新研究工件，不实现任何DCL运行机制。

{D('EVIDENCE_INDEX.md')} · {J('DELIVERY_CHECK.json')}。
'''
for name,body in r.items():
    h,b=body.split('\n',1);(OUT/name).write_text(h+'\n\n'+intro+b.lstrip()+tail,encoding='utf-8')
index='# ResidualBounds研究决策证据索引\n\n'+intro
index+='结论：CURRENT_CONTRACT_UNSAT / CONTRACT_REVISION_REQUIRED；本轮同范围静态审计结束。\n\n'
for n in r:index+='- '+D(n)+'\n'
index+='\n定向机器证据：\n\n'
for n in ['INITIAL_CHECK.json','FROZEN_SOURCE_LOCK.json','H_FULL_SCOPE_PROOF.json','REASON_AND_VARIABLE_DECISION.json',
 'SOURCE_EXCEPTION_CLASS_CENSUS.json','CURRENT_CAPACITY_UNSAT_WITNESSES.json','AMBIENT_PROCESS_COUNTEREXAMPLE.json',
 'RESIDUAL_15_GAP_MATRIX.json','CLOSE_CORE_REDUCED_FORMULA.json','TERMINAL_REENCODING_LEMMA.json',
 'RESOURCE_TERMINATION_DECISION.json','FINAL_BOUND_STATUS.json','FOUR_AUTHORIZATION_DECISIONS.json',
 'DECISION_BINDINGS.json','MR_RULE_RECHECK.json','DELIVERY_CHECK.json']:
    index+='- '+J(n)+'\n'
index+='\n'+L('方案A',A)+' · '+L('方案B',B)+tail
(OUT/'EVIDENCE_INDEX.md').write_text(index,encoding='utf-8')
save('FINAL_TWENTY_ANSWERS.json',{'answers':[{'number':i,'question':q,'answer':a} for i,(q,a) in enumerate(answers,1)],
 'final_states':['CURRENT_CONTRACT_UNSAT','CONTRACT_REVISION_REQUIRED','BOUND_PROVED','CONDITIONAL_BOUND','COUNTEREXAMPLE','OUTSIDE_SCOPE','UNRESOLVED_EXACT'],
 'same_scope_review_closed':True})
print({'reports':len(r),'answers':len(answers),'A_sha256':sha(A),'B_sha256':sha(B)})
