"""Research report authoring only. Target code and dynamic fixtures stay unexecuted."""
from pathlib import Path
import json
E=Path(__file__).resolve().parent;O=E.parent;B=O.parent
R=json.loads((E/'STATIC_RESULT.json').read_bytes())
passport='Material Passport：DCL-R6-TerminalRead-Fix；TerminalRead-static-1/r1；2026-11-13（Asia/Shanghai）；HOST_STATIC_ONLY。'
gates='RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原条件结论与原创性裁决保持。'
def report(name,title,body):
    with (O/name).open('x',encoding='utf-8') as f:f.write('# '+title+'\n\n'+passport+'\n\n'+body.strip()+'\n\n'+gates+'\n')
report('TERMINAL_READ_FAILURE_TIMELINE.md','终态读取失败的真实事件链','''
**历史batch12已真实关闭，native适用性审查被活动态期限辅助接口阻断；捕获异常未单列traceback。** 本轮使用原始分类、状态和冻结源码恢复依赖，不重放旧批次。

|事件|原生BOOTTIME|实际主体/状态/结果|证据|
|---|---:|---|---|
|WORK转换|88.431871955|scheduler838/start8801，RUNNING/6|pt_phase/events；公开点稍后sample88.442962756|
|C00 PASS|88.907022413|真实Payload与八项比较通过|result_C00/readiness|
|PT64接受|115.141179569|55 PASS＋9变异检出|PT_QUALIFICATION|
|PF48接受|131.275613725|40 PASS＋8变异检出|pf_qualification|
|STOP_REQUEST|不适用|本批正常结束，原文件不存在|原始文件清单/自动快照|
|CLOSED|131.278564941|child838发布PT_MINIMAL_RUNTIME_DIAGNOSTIC_COMPLETE|CLOSED.json|
|child回收|131.317379782|Owner445/start8616直接waitpid838，exit0/raw0|Root私有waitpid_838|
|期限读取/守卫拒绝|精确时刻UNKNOWN|seal适用性进入_phase_deadline→G.state；CLOSED已存在|冻结调用图，区间由CLOSED及分类限定|
|seal分类|131.332716174|NATIVE_SEAL_UNRESOLVED；G.seal未进入|pt_seal_disposition|
|停止器退出|MONOTONIC131.334190|Root停止器849成功结束|systemd journal|
|自动行政审计|131.528678948|Root1130/start13146，UID0，角色/组空；内部UNKNOWN|STARTUP_POSTEXIT stdout|
|自动行政包|UTC2026-11-12 14:28:18.387592|171清单成员/172 ZIP entries，SEALED|STARTUP_FINALIZATION|

所有运行记录的原boot均6b12daf8-f8cc-4788-bcaa-382f2d3407fb；源版本PTA-PhaseFinalizer-static-1/r3、batch12-r3。T0=88.190295781，deadline=1888.190295781，stop_at=1828.190295781；最终R1907、1907事务/3814行。

事件链实际为WORK→正常CLOSED→期限辅助读取→活动态拒绝→native适用性UNRESOLVED→自动行政成功。STOP_REQUEST环节未发生，未用默认值补全该事件。上述日期属于历史；本轮新静态报告日期为2026-11-13。

[原始事实及23份副本SHA](evidence/HISTORICAL_FAILURE_FACTS.json) · [旧分类原件](evidence/PFA_ORIGINALS/native/inputs/root_private/boot/pt_seal_disposition.json)
''')
report('ACTIVE_TERMINAL_INTERFACE_AUDIT.md','活动态与终态接口审查','''
**活动态接口维持原有严格资格检查；终态接口直接核验既有证据，不进入G.state或活动预算路径。**

|接口|实际实现/用途|权限与失败规则|
|---|---|---|
|check_active_runtime|薄封装原G.root_checkpoint；原调用者继续使用G.state/root_checkpoint及PF机制|STOP/CLOSED优先拒绝；身份、window、资源、运行点保持；失败抛原异常|
|read_terminal_evidence(REVIEW)|当前固定批次的既有window/counter/journal/phase/关闭/退出读取|Root只读描述符，身份与来源匹配，缺件损坏保留错误；无work/预算/阶段/Launcher权限|
|read_terminal_evidence(NATIVE_SEAL)|在原停止器等待之后评估既有证据|必须CLOSED、同原boot、原deadline尚有效、完整预算/检查点、稳定角色退出与直接waitpid；返回native_ready只表示输入前提|
|read_terminal_evidence(HISTORICAL_AUDIT)|同一固定namespace在新boot读取历史记录|保留original_boot和observation_boot，旧waitpid仅作历史见证，native_ready恒false|

活动接口的G.state/validate_state_document/root_checkpoint、counter创建/预留核心、PF状态事务和锁读写函数全部保持归一AST。旧terminal_inspection可选参数未扩大权限；批准的seal读取已分流到新接口，不再调用那条依赖活动期限的路径。

终态模块只打开原文件O_RDONLY|O_NOFOLLOW，既有Root目录通过原RootIPC只读目录遍历验证；未使用会创建boot目录的BC.Store。共享锁顺序counter→phase，兼容原预算写者的counter→phase顺序；最多512次/2秒获取，整个读取5秒。锁为瞬态描述符操作，无运行文件写入。

io局部until只限制行政读取耗时，不持久化为运行deadline。返回window直接来自原state并与checkpoint完全比较；没有新的T0、预算、生命周期转换或服务启动。

[调用图/只读闭包](evidence/SYNTAX_CONTROL_FLOW_READONLY_CHECK.json) · [保护语义](evidence/PROTECTED_SEMANTICS_CHECK.json) · [新接口](evidence/SOURCE_FINAL_R1/src/terminal_evidence.py)
''')
report('TERMINAL_EVIDENCE_CONTRACT.md','终态证据来源与一致性合同','''
|字段|创建/持久来源|可变性与核验|缺失/损坏裁决|
|---|---|---|---|
|batch/source/lock/auth|静态身份、Root一次认领activation和原文回执|固定namespace、manifest/执行锁/回执摘要精确匹配；不接受任意路径参数|拒绝/UNRESOLVED|
|原boot|原activation、state、checkpoint、关闭和waitpid|原运行身份各处相同；观察boot单独记录|拒绝/UNRESOLVED|
|T0/deadline/stop_at|原scheduler创建state；原checkpoint.window|只读原字段，有限数值与1800/1740关系；不取默认期限|UNRESOLVED|
|R/cap|原counter与预留协议|绑定magic/cap/device/inode，COMMITTED intent及完整journal对齐|UNRESOLVED；原字节保留|
|journal|原预算核心追加|正额连续PREPARED/COMMITTED，协议/原boot/cap一致，终点R；流式边界|缺失或不一致保持未决，R0也不补造journal|
|CLOSED/STOP与原因|原stop_tree/request_stop|原元数据与boot；CLOSED吸收，终态读取不覆盖|无终态标记拒绝终态审查|
|phase/version|原PF写者事务|共享counter/phase锁下读取公开/私有phase、seq和record/init摘要|UNRESOLVED|
|退出|原Root协调器waitpid与停止器/角色绑定|pid/start_ticks/原boot和原始exit status一致；同boot再审当前其他角色/组|缺失UNKNOWN；新boot只保留历史见证|
|内部状态|原MR关闭路径按需生成mr_close_state|读取已有值；缺失保持UNKNOWN；组空不升级|UNKNOWN|
|native状态|原生manifest/ZIP或真实SEAL_ERROR|已存在ZIP逐流/成员/当前关键原件摘要核验，未验证不报告完成|FAILED/UNRESOLVED按真实记录；纯预窗原分支NA|

各字段首次创建时间沿用原记录sample或T0，精确fsync完成时点缺少独立日志的字段继续UNKNOWN。历史PFA的T0/关闭/phase采样有原件，无法由新代码恢复旧文件未记录的具体IO时刻。

复用现有journal、Root state、运行点、终态标记和waitpid；没有新增不可变运行快照或预算检查点。原G.seal调用者在独立只读审查之后写入Root私有terminal_seal_review.json，标记PRE_NATIVE_ARCHIVE_READ_ONLY_REVIEW；该文件是新增审查报告，原始记录和journal不覆盖，native_ready不表示原生包已经完成。

真实性沿用受信kernel/Root launcher、冻结预留写者及无并发特权更新的原合同。没有为journal新增密码学认证声明。读取校验结构、身份、原件摘要和退出来源；只读描述符可能涉及文件系统自动管理的读取元数据，应用数据、预算和生命周期字节保持。

历史审查若设备身份等无法继续确认，保留未决；不将旧boot的deadline或旧PID用于当前工作资格。跨batch路径直接拒绝。源/锁或任一必要记录缺失时，不通过默认值补齐。

[逐字段详细合同](evidence/TERMINAL_FIELD_CONTRACT.json) · [只读代码与边界](evidence/SOURCE_FINAL_R1/src/terminal_evidence.py)
''')
report('DEADLINE_READ_ROOT_CAUSE.md','关闭后期限读取根因','''
**CLOSED后的只读审查进入了复用的活动态辅助函数。** 旧P.runtime_checkpoint虽然收到terminal_inspection=True，_phase_guard仍先执行_phase_deadline(G)；后者无条件G.state，G.validate_state_document看到stopped即抛BATCH_STOPPED。

terminal_inspection只影响_cancel和后续snapshot比较，无法影响之前的期限来源读取。P.seal_applicability捕获AdmissionBlocked并返回NATIVE_SEAL_UNRESOLVED，解释了没有独立SEAL_ERROR/traceback且底层G.seal未运行的现象。

旧state/phase/预算均有完整持久原件；本次关键信号是CLOSED131.278564941先于defer分类131.332716174。捕获异常精确抛出时点仍UNKNOWN，BATCH_STOPPED是冻结调用图与当时CLOSED共同限定的源码追溯结果，未伪装成实际异常日志。

新版本保留原G.state及PF期限/活动锁机制；seal直接接入独立终态只读接口。该接口从现有state读取原window，身份/完整性/预算/版本分别验证，不以活动态许可为前提。未决错误由调用者保留具体类型和摘要到新批的pt_seal_disposition，原生applicable字符串协议保持。

该修复解除已定位的前置依赖；退出等待、真实打包、落盘、最终摘要和资源时限等仍需独立动态验收。

[原依赖证据](evidence/HISTORICAL_FAILURE_FACTS.json) · [新分流diff](evidence/FULL_DIFF.patch)
''')
report('NATIVE_SEAL_DEPENDENCY_ANALYSIS.md','native seal依赖分解','''
**期限辅助读取是已确认的直接阻断，后续native成功仍为UNRESOLVED_DYNAMIC_UNRUN。**

|实际步骤|历史PFA执行范围|新版本静态接入与剩余条件|
|---|---|---|
|原state/window读取|state原件存在；适用性读取后在_phase_deadline的G.state被CLOSED拒绝|独立只读读取既有window，不调用活动态入口|
|phase/预算完整审查|PFA前缀和独立行政审计证明数据一致；旧终态路径未完成|Root身份/phase/seq/init/窗口、counter/intent/journal完整核验|
|内部状态读取|正常路径无mr_close_state，原行政结果UNKNOWN|原状态规则保持，缺件UNKNOWN，不由组空推定|
|协调器/角色/组及child回收|实际waitpid0、stop0、组空可用；底层打包未到达|原M.seal退出/单sealer规则保持；原G.seal停止器等待之后再验证当前退出前提|
|原执行锁/源码|原生预检fresh绑定通过|终态读取再验证同一原batch/source/lock/receipt和activation|
|生成seal输入审查|历史未进入|caller写独立pre-native review，包含活态接口对CLOSED的真实拒绝证据|
|Native manifest/ZIP持久化|未执行，无原生ZIP/manifest|保持原生成格式及写者，需真实IO/退出/期限证据|
|完成后审查|原自动行政成功、native UNRESOLVED|已存在Native包需成员/CRC/SHA/关键当前原件一致才读作COMPLETED；行政仍独立裁决|

原M.seal、M.permit_external_seal及MR管理器审查整体归一AST相同；新增检查在P.seal_applicability和G.seal读侧接入。前者不再使用活动态phase guard，后者不更换原停止器等待或原生打包算法。

四类状态分别处理：纯预窗无运行对象保持NOT_APPLICABLE；可信SEAL_ERROR支持FAILED；部分/不完整/损坏/错误身份或窗口不适用保持UNRESOLVED；既有完整ZIP经过实际逐流核验才COMPLETED。输入前提满足仅返回native_ready，不能预填COMPLETED。

重复审查只读取已有包；未验证的现有部分包和原失败不会触发自动重写。新boot只作历史只读核验，不发放当前native生成资格。当前尚未运行新接口或原生seal，不能由源码解除单点阻断推断全部后续步骤成功。

[具体实现](evidence/SOURCE_FINAL_R1/src/terminal_evidence.py) · [原始失败分类](evidence/PFA_ORIGINALS/native/inputs/root_private/boot/pt_seal_disposition.json)
''')
report('INTERNAL_UNKNOWN_ANALYSIS.md','内部UNKNOWN的独立来源','''
**PFA内部UNKNOWN的直接来源是正常关闭路径未生成mr_close_state.json。期限读取修复不会自动创建该关闭收据。**

旧G.stop_tree正常结束只发布CLOSED及stop_result，协调器保存waitpid；M.abort路径才维护mr_close_state。PFA没有实际Root关键异常，故该内部记录缺失。自动post读取缺件时明确返回UNKNOWN，当前原件中state.status仍CALIBRATING、phase仍RUNNING，由CLOSED支配工作拒绝。

|轴|历史PFA实际结论|新版本策略|
|---|---|---|
|受控进程退出|直接waitpid0/systemd成功退出/自动角色审计|保留各自原始见证|
|cgroup|清空|只作为相应清理事实|
|CLOSED|存在并有正常完成原因|终态只读不覆盖|
|预算|R1907/1907事务/3814行一致|核验原件，不增减R|
|应用内部状态|UNKNOWN，关闭收据缺失|继续UNKNOWN；没有新增收敛规则|
|native|UNRESOLVED|新接入仍需动态seal证据|
|行政|自动SEALED171/172|保持原finalizer实现|

新native归档可以在符合既有正常关闭规则、预算和退出证据完整时保存一个仍含internal UNKNOWN的真实快照；这只证明包完整性，不能升级内部状态。若原MR关闭记录实际存在但为UNKNOWN，原M.seal适用规则继续保留其未决限制。

本轮不重写MR关闭语义或补填旧收据，保持原自动行政成功以及历史native未决。

[源事实](evidence/HISTORICAL_FAILURE_FACTS.json) · [原自动行政结果](evidence/PFA_ORIGINALS/host/STARTUP_FINALIZATION.json)
''')
report('TERMINAL_READ_SAFETY_PROPERTIES.md','TR-1至TR-10安全性质','''
|性质|源码/字段及静态证据|裁决边界|
|---|---|---|
|TR-1 TerminalReadOnly|read_terminal_evidence调用闭包无写/创建/预算/阶段/进程动作，打开原件O_RDONLY|PASS_STATIC，原生字节前后核验待验|
|TR-2 ActiveGuardPreserved|G.state/validate_state_document/root_checkpoint与原PF函数保持；caller记录CLOSED实际拒绝|PASS_STATIC，下一Native实际拒绝待验|
|TR-3 NoTerminalReactivation|read结果runtime_authority=NONE，无work/预算/phase/Launcher资格；历史模式不授native资格|PASS_STATIC|
|TR-4 EvidenceAuthenticity|固定namespace、原activation/receipt/源码/锁、元数据/原boot/关键摘要|CONDITIONAL_PASS，继承原TCB信任假设|
|TR-5 DeadlineConsistency|原T0/deadline/stop_at直接索引、固定关系，观察boot单列|PASS_STATIC，无默认时间|
|TR-6 BudgetConservation|counter SH→phase SH；同一写锁对象；journal pair/终点/COMMITTED intent一致；读取不debit|PASS_STATIC，原生一致性/锁延迟待验|
|TR-7 SealPreconditionCorrectness|原退出等待后调用只读前提，稳定角色/waitpid/window/budget有效才native_ready|CONDITIONAL_PASS，后续原生IO未知|
|TR-8 NoFalseSealSuccess|ready与completed分开；既有ZIP成员/当前关键证据逐流校验，错误保留|PASS_STATIC，真实IO故障路径待验|
|TR-9 UnknownPreservation|缺件/坏数据抛具体错误，internal缺收据保留UNKNOWN，无组空升级|PASS_STATIC|
|TR-10 FinalizerCompatibility|host entry/finalizer逐字节相同，bootstrap除namespace外AST保持；原30/35/256/32MiB界保持|PASS_STATIC，新包联调待验|

28项静态断言、13份关键程序逐字节与70项受保护成员归一AST核对完成。整个RootIPC及MR模块归一AST保持，活动态预算/phase机制没有被替换。文件锁为内核瞬态状态，原始数据、预算和生命周期记录无修改调用。

原生flock、文件系统IO、退出与封存性能仍受原kernel/调度/存储返回假设约束，本轮没有实时系统或全链性能证明。

[断言与行号](evidence/SYNTAX_CONTROL_FLOW_READONLY_CHECK.json) · [保护语义](evidence/PROTECTED_SEMANTICS_CHECK.json)
''')
report('TERMINAL_READ_FIX_IMPLEMENTATION.md','最小修复实现与修改范围','''
最终TerminalRead-static-1/r1位于独立tr01。59文件＝39 Linux程序＋2 host程序＋18输入，未来Linux部署57项。

|位置|修改理由与行为|
|---|---|
|terminal_evidence.py（新增）|独立只读context、固定Root元数据、SH counter/phase锁、原window/预算/journal/phase/退出核验，历史boot分离及既有native包审查|
|startup_lifecycle.seal_applicability|终态读取分流，不再进入G.state依赖；缺件/错误保存类型和摘要，原纯预窗NA分支保持|
|guard.seal|保持原等待/打包，在等待后读取终态前提、验证活动接口拒绝CLOSED，再由caller写pre-native审查报告|
|guard/boot授权接口|绑定terminal合同及新的显式批准位，未来回执不足时在原生准备前拒绝|
|guard的C00后序|原PT64→PF48后接TR40，然后在同一窗口关闭；full formal prefix的TR资格另核验|
|terminal_regression/oracle（新增）|40固定job/8变异，独立原始trace审查，原预算prepay16＋audit1计费|
|输入/namespace/执行锁|新batch13-r1/tr01/控制目录及必要摘要、顺序与资源界；原Source pf01不覆盖|

13份保护程序含五业务/预算range_core/probe/S驱动/C00Ready/C09/MR套件等字节相同；原PT64/PF48 jobs相同。70成员AST、整个RootIPC/MR模块保持，原slice字节保持。两份host行政文件完全相同，admin_postexit仅固定namespace/源版本调整，流程AST不变。

没有新增运行快照或重写现有journal。terminal_seal_review是sealer新建的审查报告，不是运行资格对象。活动态G.state及原PF读取/发布机制保持原AST，原有终态标记不改写。

全部源码路径、前后摘要与文本差异见[FILE_DIFF_INDEX](evidence/FILE_DIFF_INDEX.json)和[完整diff](evidence/FULL_DIFF.patch)。r1源码/输入副本及59项锁完整保留。
''')
report('REGRESSION_AND_MUTATION_PLAN.md','TR40及兼容回归静态计划','''
**新增TR40＝32safe＋8mutant，实际UNRUN。原PT64/PF48及17项变异的历史原件保持，输入jobs精确相同。**

32safe按四类构造：正常读取8项；缺T0/deadline/journal/boot/batch/锁/版本/CLOSED/退出/native输入10项；新工作/预算/phase/Launcher/跨batch/原件修改权限6项；native完整/期限/预算/缺件/IO错误/重复/已完成/行政不同步8项。8mutant复用对应safe输入作为控制。

|变异|独立oracle目标|
|---|---|
|grant_terminal_work|TERMINAL_WORK_GRANTED|
|rebuild_budget|BUDGET_REBUILT|
|skip_identity|IDENTITY_CHECK_SKIPPED|
|default_deadline|DEFAULT_DEADLINE_USED|
|ignore_journal|JOURNAL_CORRUPTION_IGNORED|
|upgrade_unknown|UNKNOWN_UPGRADED|
|false_seal|FALSE_SEAL_SUCCESS|
|write_original|ORIGINAL_EVIDENCE_MODIFIED|

oracle只导入stdlib，以实际input/trace/hash/binding重算期望并独立分类差异，之后检查声明的目标及允许集合。没有将输入的expected标签当实际结果；当前未运行subject或oracle，检出数尚无动态值。

每job预付16、Root审查1，suite entry1；TR完成681、硬960。下一最小A选择全量PT64/PF48兼容重跑，加TR40共152合成job/25变异，再有独立真实C00。原因是新namespace/源码锁与seal调用路径已经改变；旧112动态结果只支持旧冻结版本历史范围，不能成为新窗口资格。

TR-SIMULATION/1覆盖策略和观察模型，无法替代原生文件权限、锁/损坏注入或真实seal IO。下一正常A的seal hook将提供真实CLOSED读取、活动接口拒绝、预算/原件摘要及native/admin分轴记录。任何正式实例破坏故障或其他独立启动模式仍需另外冻结与许可。

[40项输入](evidence/SOURCE_FINAL_R1/inputs/terminal_contract.json) · [独立oracle](evidence/SOURCE_FINAL_R1/src/terminal_oracle.py) · [静态配对/分支审查](evidence/FIXTURE_ORACLE_STATIC_CHECK.json)
''')
report('STATIC_VERIFICATION_RESULTS.md','静态验收结果与动态缺口','''
|检查|范围与结果|
|---|---|
|41程序语法|主机AST、3.12文法及内存compile通过；目标导入/执行0，无pyc|
|活动/终态调用分流|28静态断言通过；终态闭包无G.state/root_checkpoint或写入、创建、预算、服务动作|
|身份/window/预算|同namespace/源/执行锁/回执/原boot；精确原window；counter/intent/journal闭合核验|
|终态安全|固定Root原件只读、counter→phase锁顺序、5秒读取/2秒获取/512次；正常工作守卫保持|
|native前置|原退出等待后读取并记录活态拒绝；native_ready和实际ZIP完成分别处理|
|兼容性|13程序字节、70成员AST、完整RootIPC/MR AST保持；host两文件字节保持；PT64/PF48 jobs相同|
|TR40/oracle|32safe/8mutant输入配对、唯一ID、最多4帧、stdlib独立参考与目标类别静态检查；动态0|
|资源|TR完成681/硬960；正常A完成2588/硬3649；完整硬67730≤100000|
|历史|预锁7768文件，PFA/PF静态/PreT0-A旧包逐流核验；旧native UNRESOLVED/internal UNKNOWN/admin成功保持|
|本轮原生动作|WSL0、部署/服务/Launcher0、T0/R=null、PT/PF/TR/模型/参考运行0|

TR-G1=PASS_STATIC；TR-G2=CONDITIONAL_PASS；TR-G3=PARTIAL；TR-G4=PASS_STATIC。已定位直接前置阻断并建立分流；实际Native读取/锁/IO/归档、跨boot和全链300秒可行性仍待新授权验证。

只读扫描不产生模型搜索访问或新的运行资格，R不debit；读取属于有界行政IO，最长5秒/固定文件与journal上界。原finalizer30/35秒、256文件/32MiB界保持，新增case/报告占用的实际归档大小仍须下一批核验；遇上界直接失败并保留未决，不放宽既有限额。

[机器结果](evidence/STATIC_RESULT.json) · [控制流/只读闭包](evidence/SYNTAX_CONTROL_FLOW_READONLY_CHECK.json) · [资源重算](evidence/RESOURCE_BOUND_RECALCULATION.json) · [最终摘要链](evidence/FINAL_BINDING_REVIEW.json)
''')
report('SOURCE_AND_INPUT_LOCK.md','TerminalRead最终源码与输入锁',f'''
最终版本TerminalRead-static-1/r1；Windows工作区D:/毕业设计/DCL-R6-isolated-verification/tr01；副本evidence/SOURCE_FINAL_R1。规划Linux源/var/lib/dcl-r6/tr01、实例/var/lib/dcl-r6/batch13、slice=dclr6batch13.slice；规划控制目录DCL-R6-TerminalRead-Fix/authorization/batch13-r1。

|对象|SHA-256|
|---|---|
|static_manifest.json|{R['manifest_sha256']}|
|execution_lock.json|{R['execution_lock_sha256']}|

59项＝39 Linux程序＋2 host程序＋18输入，未来Linux57项。Source/输入→manifest，manifest/host/argv→execution_lock，最终回执绑定两锁、terminal合同和真实用户原文。当前仅保存TEMPLATE_UNAPPROVED，所有批准位false，原文SHA=null；实际control/回执、Linux实例、T0和预算均未创建。

旧pf01、batch12、PFA及其全部回执和归档保持。新静态身份不构成执行许可，也不借用历史RESOURCE_GATE_PASS。当前原生环境/boot不作fresh确认，本轮WSL调用为0。

[59项精确字节锁](evidence/STATIC_WORKSPACE_LOCK.json) · [最终源](evidence/SOURCE_FINAL_R1/inputs/static_manifest.json) · [执行锁](evidence/SOURCE_FINAL_R1/inputs/execution_lock.json) · [全部前后SHA](evidence/FILE_DIFF_INDEX.json) · [未批准模板](evidence/PHASE_A_NORMAL_START_AUTHORIZATION_TEMPLATE.json)
''')
report('NEXT_DYNAMIC_AUTHORIZATION.md','下一独立有限动态验收申请',f'''
**REQUEST_ONLY；当前动态授权0。** 唯一申请目标TerminalRead-static-1/r1；59项/41程序；manifest `{R['manifest_sha256']}`，execution_lock `{R['execution_lock_sha256']}`。

规划batch13-r1，scope=PT_STARTUP_DIAGNOSTIC_ONLY、startup_probe_mode=NORMAL_START。预检fresh核当前Ubuntu-24.04/Python3.12.3、boot、源/工具摘要、UID/GID/Root元数据/cgroup/实例全新；原batch12保持CLOSED。未来只部署57项Linux源/输入，source-only无pyc。

```text
python -X utf8 D:\\毕业设计\\DCL-R6-isolated-verification\\tr01\\host\\windows_entry.py --activate
```

host环境PYTHONDONTWRITEBYTECODE=1。唯一active Native argv：

```text
C:\\Windows\\System32\\wsl.exe --distribution Ubuntu-24.04 --user root --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/tr01/src/boot_continuity.py --activate --batch-root /var/lib/dcl-r6/batch13
```

顺序：原单会话/同PID/认领 → 正常预窗/一次intent/T0/counter → ARMED/WORK → C00 → 全量PT64 → PF48 → TR40 → 正常CLOSED/原停止与waitpid → 原停止器等待 → 终态只读window/预算/phase/退出审查 → 原活动接口拒绝CLOSED并保存原异常码 → native seal/manifest/ZIP → 原自动行政入口/归档。

只读每次5秒、共享锁每次最多2秒/512尝试，原journal读取最多32MiB/32768字节行/2*原cap+1次（含EOF探测），既有native包最多257成员/解压总32MiB。均为只读行政工作，不更改R或原deadline；当前native生成仍要求同boot和原窗口尚有效。历史审查模式不发放任何生成或执行资格。

访问预算：TR681完成/960硬；正常A2588完成/3649硬；含新增测试完整硬67730≤100000。维持总1000000/1800秒、校准100000/300秒、预T0120秒、stop_at=T0+1740、单进程AS1GiB、父TasksMax4。新Reader/归档性能和原finalizer文件容量须实测；不足时停止并保留未决，原硬限不扩。

自动post命令保持机制，仅迁移固定源namespace：

```text
C:\\Windows\\System32\\wsl.exe --distribution Ubuntu-24.04 --user root --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/tr01/src/admin_postexit.py --post-exit-export
```

原AS1GiB/单次30秒alarm先于模块加载、host32秒wait及35秒总回收、256文件/32MiB行政上界保持。请求必要的本批冻结关闭后备与原件保存，真实调用时与自动成功分开；禁止人工seal/归档冒充自动性质通过。

未来回执绑定最终两锁、terminal合同、真实原文及TerminalRead显式批准位，既有PF/PreT0/RootIPC/单会话兼容字段按schema齐备；Full/MR/预窗77注入false。当前模板全部批准位false，实际授权文件尚无。

首次非预期关键失败停止发放、保留原件和首错、自动关闭/适用封存/行政收尾；UNKNOWN保持，必要后备单列。没有现场改码、重跑、预算重置、免费第二窗或自动下一批。即使A通过，也只关闭本批，不进入MR/C09/C01–C12/S34/门18/F1/F4。完整资源与模型仍需新独立许可。

[未批准模板](evidence/PHASE_A_NORMAL_START_AUTHORIZATION_TEMPLATE.json) · [真实argv锁](evidence/SOURCE_FINAL_R1/inputs/execution_lock.json)
''')
report('FINAL_DECISION.md','TerminalRead最终静态裁决','''
**已完成有限终态读取修复并冻结TerminalRead-static-1/r1；新Native读取与封存效果尚未执行。**

|验收门|裁决|证据范围与限制|
|---|---|---|
|TR-G1 故障定位|PASS_STATIC|原CLOSED/分类时间与源码定位活动态辅助前置混用；捕获异常无独立traceback，精确抛错时点未知|
|TR-G2 终态只读安全|CONDITIONAL_PASS|独立固定批次只读、身份/原window/预算/phase/退出校验，活动守卫保持；OS/IO及字节前后动态证据待验|
|TR-G3 native与UNKNOWN|PARTIAL|直接native阻断已分流；其他生成/持久化仍UNRUN。内部UNKNOWN独立来自缺关闭收据，新代码不升级|
|TR-G4 回归与准备|PASS_STATIC|59文件/41程序、TR40/8mutant、原PT/PF兼容、摘要DAG、访问界和新最小申请齐备|

41程序语法/3.12文法及内存compile、28静态断言通过；13关键文件逐字节与70成员AST保持。整个RootIPC/MR归一AST相同，host entry/finalizer逐字节相同，原行政bootstrap除固定namespace外AST保持。原PT64/PF48输入jobs保持，新增TR40及全部新版本套件实际UNRUN。

原数据复用，无新运行快照、T0或预算创建逻辑。新终态审查读取原window和journal，caller单独保存pre-native报告及活动守卫拒绝的真实证据；没有将native_ready写作COMPLETED。缺件、坏账、错误身份或旧boot当前生成请求保持未决。

当前新增WSL/部署/Launcher/服务/预算/PT/PF/TR/生产oracle/模型运行均0；本轮T0/R=null。正常A完成2588/硬3649，完整硬67730≤100000；300秒全链及新IO耗时未证明。

历史PFA112项/17变异、R1907、进程/组空、native UNRESOLVED、内部UNKNOWN、自动行政SEALED171/172全部保持。旧batch11 native成功、旧漂移精确值UNKNOWN及更早MRA/CalDiag裁决同样冻结。修复前置读取不保证下游原生写入成功。

下一步仅审阅[独立正常A申请](NEXT_DYNAMIC_AUTHORIZATION.md)。当前没有实际回执或Linux运行实体；后续MR与完整资源链保持独立授权。

[根因](DEADLINE_READ_ROOT_CAUSE.md) · [实现](TERMINAL_READ_FIX_IMPLEMENTATION.md) · [静态结果](STATIC_VERIFICATION_RESULTS.md) · [源码锁](SOURCE_AND_INPUT_LOCK.md) · [证据索引](EVIDENCE_INDEX.md) · [交付核验](evidence/DELIVERY_CHECK.json)
''')
report('EVIDENCE_INDEX.md','终态读取证据索引','''
|主题|工件|
|---|---|
|最终裁决|[FINAL_DECISION](FINAL_DECISION.md)、[静态机器结果](evidence/STATIC_RESULT.json)|
|授权边界|[用户原文](evidence/TASK_REQUEST.txt)、[SCOPE_BOUNDARY](SCOPE_BOUNDARY.md)|
|历史原件|[23份副本/SHA及依赖](evidence/HISTORICAL_FAILURE_FACTS.json)、evidence/PFA_ORIGINALS下逐字节原件|
|历史归档|[PFA/PF/PreT0逐流核验](evidence/HISTORICAL_ARCHIVE_CHECK.json)|
|源码前后|evidence/SOURCE_BEFORE和SOURCE_FINAL_R1；[完整diff](evidence/FULL_DIFF.patch)、[逐文件SHA](evidence/FILE_DIFF_INDEX.json)|
|接口/性质|[只读闭包和28断言](evidence/SYNTAX_CONTROL_FLOW_READONLY_CHECK.json)、[保护语义](evidence/PROTECTED_SEMANTICS_CHECK.json)、[字段合同](evidence/TERMINAL_FIELD_CONTRACT.json)|
|回归/预算|[40项/8变异静态矩阵](evidence/FIXTURE_ORACLE_STATIC_CHECK.json)、[访问及IO界](evidence/RESOURCE_BOUND_RECALCULATION.json)|
|冻结与下一申请|[59项锁](evidence/STATIC_WORKSPACE_LOCK.json)、[最终摘要链核验](evidence/FINAL_BINDING_REVIEW.json)、[未批准模板](evidence/PHASE_A_NORMAL_START_AUTHORIZATION_TEMPLATE.json)|
|历史/交付保持|[7768份基线](evidence/BASELINE_LOCK.json)、[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)、[交付核验](evidence/DELIVERY_CHECK.json)|

所有新测试/原生行为保持UNRUN。私有原始能力nonce继续仅留历史私有原件及归档，报告不展开。
''')
report('README.md','DCL-R6-TerminalRead-Fix','''
TerminalRead-static-1/r1已静态冻结：独立只读原window/预算/phase/关闭/退出证据，原活动态守卫保持，native在原停止器等待后接入只读前提。原行政finalizer不重写。

TR-G1=PASS_STATIC、G2=CONDITIONAL_PASS、G3=PARTIAL、G4=PASS_STATIC。历史native UNRESOLVED与内部UNKNOWN保持，新原生效果待独立动态授权。

[最终裁决](FINAL_DECISION.md) · [失败时间线](TERMINAL_READ_FAILURE_TIMELINE.md) · [接口边界](ACTIVE_TERMINAL_INTERFACE_AUDIT.md) · [字段合同](TERMINAL_EVIDENCE_CONTRACT.md) · [期限根因](DEADLINE_READ_ROOT_CAUSE.md) · [native依赖](NATIVE_SEAL_DEPENDENCY_ANALYSIS.md) · [内部UNKNOWN](INTERNAL_UNKNOWN_ANALYSIS.md) · [安全性质](TERMINAL_READ_SAFETY_PROPERTIES.md) · [实现](TERMINAL_READ_FIX_IMPLEMENTATION.md) · [回归](REGRESSION_AND_MUTATION_PLAN.md) · [静态结果](STATIC_VERIFICATION_RESULTS.md) · [源码锁](SOURCE_AND_INPUT_LOCK.md) · [下一申请](NEXT_DYNAMIC_AUTHORIZATION.md) · [证据索引](EVIDENCE_INDEX.md)
''')
print(json.dumps({'required_reports':13,'markdown_files':len(list(O.glob('*.md'))),'version':R['version'],'new_dynamic_runs':0},ensure_ascii=False))
