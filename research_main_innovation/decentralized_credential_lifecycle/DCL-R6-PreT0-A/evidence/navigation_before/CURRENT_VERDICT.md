# DCL-R6-PreT0-Fix 最新静态裁决（2026-11-12）

PreT0Recovery-static-1/r3已在独立pt01冻结：MRA循环依赖定位为初始health.query要求state、state却在health之后创建。新版本使用活体sealed预窗scope与单调初始化intent，真实T0/state/counter之后发布runtime checkpoint，再armed/work gate；运行点真正缺失继续严格拒绝。停止沿用既有120秒启动TCB，不造运行窗。

35程序/51项静态检查通过，13关键程序字节及40预算/Boot/门18/正常MR函数AST保持。PT64含55safe/9mutant，actual全UNRUN；完整硬访问65,618≤100,000，原300/1800/1740/AS1GiB/4tasks保持。host退出后自动只读post审计/行政归档，与运行态native seal按对象/状态分开；MRA历史原生失败不追改。

PT-1=PASS_STATIC，PT-2/3/4=CONDITIONAL_PASS。下一A为新batch11-r3两种互斥NORMAL_START或PREWINDOW_ABORT，需新明确动态批准；关闭后另一个模式和B须新独立身份/锁。当前WSL/服务/校准/测试0，T0/R null，资源/模型资格未取得，严格分离0及实施门CLOSED保持。

[最终裁决](DCL-R6-PreT0-Fix/FINAL_DECISION.md) · [初始化依赖图](DCL-R6-PreT0-Fix/INITIALIZATION_DEPENDENCY_GRAPH.md) · [下一A申请](DCL-R6-PreT0-Fix/NEXT_DYNAMIC_AUTHORIZATION.md) · [证据索引](DCL-R6-PreT0-Fix/EVIDENCE_INDEX.md)

以下完整保留先前记录。

---

# DCL-R6-MR-A 最新动态裁决（2026-11-12）

STARTUP_FAILED_PRE_T0。ManagerRecovery-static-1/r5/batch10-r5实际入口1次；预检及same-PID exec通过，boot038cf87f…、Root12242/start699487。初始health在T0之前调用query(record=True)，query要求运行态root_checkpoint，抛IPC_STATE_MISSING。T0/deadline/R及counter/journal从未建立，C00/C09/MR64均未到达，期望C10后返回78未注入。

自动STOP/CLOSED真实发生，父协调器COORDINATOR_STOP_REQUEST的stop_tree返回0并确认组空；abort内后备stop/kill记录TimeoutExpired，内部结果UNKNOWN。Payload及独立停止器服务均未启动；事后所有受控角色为空，人工清理0。原生seal因缺batch_state而失败，行政ZIP另作证据保存，绝不升级为自动seal通过。

64实际执行/接受0、8变异检出0，状态UNRUN；systemd三次预检及事后仅mnt-e.mount基线。host调用2.0633844秒，完整300秒时间证据仍未决。当前batch10已有CLOSED/claim，不复用其目录/回执；下一步先静态修复PRE_WINDOW/ACTIVE检查点、预窗停止期限和封存。

[最终裁决](DCL-R6-MR-A/MRA_FINAL_DECISION.md) · [首错](DCL-R6-MR-A/MRA_COUNTEREXAMPLES.md) · [自动关闭](DCL-R6-MR-A/MRA_AUTOMATIC_CLOSURE_RESULTS.md) · [证据索引](DCL-R6-MR-A/EVIDENCE_INDEX.md)

历史CalDiag C09 PASS及38,729账保持。RESOURCE_GATE_PASS尚未取得，F1/F4未运行，严格分离0、IMPLEMENTATION_GATE=CLOSED。以下完整保留先前记录。

---

# DCL-R6-ManagerRecovery-Fix 最新静态裁决（2026-11-12）

最终ManagerRecovery-static-1/r5：MANAGER已据源码/轨迹定位为systemd failed-unit集合；预期c06/c07/c09实例缺类型化审查，恢复前言/普通非零返回和等待Owner监督存在关闭缺口。新模块完成实例/原件/完整C09链审查、只读历史关闭单位分类、STOP优先的统一关闭、fork/reap未知处理及单sealer。原C09 ACK和C00Ready保持字节。

MR-1=PASS_STATIC，MR-2/3/4=CONDITIONAL_PASS。31程序/46文件静态语法/3.12文法/内存compile通过；11关键程序字节、29预算/Boot/门18函数AST保持；64夹具含56safe/8mutant，独立oracle同时要求正确正向恢复/清理。新增MR完成1,089、硬1,536，全校准64,082≤100,000；原300/1800/1740/AS1GiB/4tasks保持，时间仍UNRESOLVED。

本轮目标/参考/WSL/服务/故障运行0，T0/R null。拟议新batch10-r5阶段A须新明确动态批准；C10后注入声明的关键返回78验证自动关闭，模型分支关闭。阶段B须A充分证据后另建独立身份/摘要。CalDiag38,729账、真实C09、194项/41变异及全部首错/人工关闭保持。

[最终裁决](DCL-R6-ManagerRecovery-Fix/FINAL_DECISION.md) · [源码锁](DCL-R6-ManagerRecovery-Fix/SOURCE_AND_INPUT_LOCK.md) · [下一动态申请](DCL-R6-ManagerRecovery-Fix/NEXT_DYNAMIC_AUTHORIZATION.md) · [证据索引](DCL-R6-ManagerRecovery-Fix/EVIDENCE_INDEX.md)

RESOURCE_GATE_PASS尚未取得，F1/F4=UNRUN_RESOURCE_GATE，严格分离0，IMPLEMENTATION_GATE=CLOSED。以下完整保留先前记录。

---

# DCL-R6-CalDiag 最新实际裁决（2026-11-12）

RESOURCE_GATE_FAILED / TIME_FEASIBILITY_UNRESOLVED_EARLY_FAILURE。batch09-r1方案B已实际单会话启动，Root4259/start135655跨exec；C00–C09全部PASS，READY64 47/17、C09H34 28/6、RootIPC56 48/8、BC40 30/10分别为PASS/MUTATION_DETECTED。真实C09已取得持久ACK、Receiver、waitpid exit23、fresh-read及一次分类HANDOFF_VERIFIED。

恢复scheduler4804在manager健康检查抛UNREVIEWED_MANAGER_FAILURE、exit125；本批预期c06/c07/c09故障单位仍为failed。失败前言在清理try之外，普通非零返回未自动关闭；AWAIT状态coordinator身份为空使Root停止器继续等待。原607文件快照保存后，按授权调用冻结stop_tree/seal补充关闭，预算不变，最终612文件、610行原生seal/611 ZIP条目保存，受控角色全空/父组不存在。

R38,729，1,739事务/3,478行；真实C09前缀48.592009253秒，失败区间48.699583118–48.738270904秒。CLOSED记录采样T0+299.567904452，发布完成不晚于+299.596399447，seal/角色空观测+299.993796083。全校准尚未完成，C10–C12/S34/门18均UNRUN，资源资格尚未取得，F1/F4未启动。

[最终裁决](DCL-R6-CalDiag/CALDIAG_FINAL_DECISION.md) · [首次反例](DCL-R6-CalDiag/CALDIAG_COUNTEREXAMPLES.md) · [逐case时间](DCL-R6-CalDiag/CALDIAG_CASE_DURATION_REPORT.md) · [证据索引](DCL-R6-CalDiag/EVIDENCE_INDEX.md)

D1/D2原条件、强G、严格分离0及IMPLEMENTATION_GATE=CLOSED保持。以下完整保留此前各阶段记录。

---

# DCL-R6-B09-Supplement 最新静态裁决（2026-11-12）

B09-AdmissionFix-static-1/r1已在独立cr09冻结：结构化batch09身份与新控制路径、旧17＋第18项预算异常门及强制原始资格接线完成。BS-1/2=PASS_STATIC，BS-3=UNRESOLVED，BS-4=CONDITIONAL_PASS。新ledger含1健康/13异常/4mutant，完成631/硬640访问；RANGE完成19,861≤20,000，全校准硬额62,546≤100,000，原300/1800/1740/AS1GiB/4tasks保持。

42文件/28程序语法、3.12文法与内存compile通过；10程序字节及25个预算/Boot基础函数AST保持。有效包batch08/BATCH08/cr01命中0，全部原件/diff/摘要与原17案例保留。完整300秒成功时间依据仍TIME_FEASIBILITY_UNRESOLVED，当前推荐B单次完整校准诊断，A/B均需新版本专项动态批准。

本轮目标模块导入/测试/WSL/Launcher/Root/service启动0，T0/deadline/R均null，原batch09阻断记录及batch08真实C00/64/R450与FIELD_EVIDENCE_PARTIAL保持。RESOURCE_GATE_PASS=NOT_OBTAINED，F1/F4=UNRUN_RESOURCE_GATE，严格分离0，IMPLEMENTATION_GATE=CLOSED。

[最终裁决](DCL-R6-B09-Supplement/FINAL_DECISION.md) · [源锁](DCL-R6-B09-Supplement/SOURCE_AND_INPUT_LOCK.md) · [下一动态申请](DCL-R6-B09-Supplement/NEXT_DYNAMIC_AUTHORIZATION.md) · [证据索引](DCL-R6-B09-Supplement/EVIDENCE_INDEX.md)

以下完整保留先前导航与各阶段时点状态。

---

# DCL-R6-batch09 最新静态准入裁决（2026-11-12）

BLOCKED_STATIC_ADMISSION。完整条件执行授权已接收，原C00Ready-static-1/r2的36份文件和batch08归档246清单成员/247条目逐流核验通过。新batch09运行身份与原入口/根/单位/回执的batch08固定绑定冲突；完整校准300秒成功完成依据尚缺；冻结门17缺预算账异常专项负向项。三项责任已列入最小补充申请。

本轮目标程序、WSL、systemd及源码/权限修改均0；当前boot/T0/R/运行峰值均null，运行目录与活账尚待准入。访问预算从原代码重算为62,546≤100,000，新增测试后须重新冻结总界。RESOURCE_GATE_PASS=NOT_OBTAINED，F1/F4=UNRUN_RESOURCE_GATE，PASS_BOUNDED=[]。batch08历史C00_PASS/64项接受/R450/FIELD_EVIDENCE_PARTIAL保持，batch07具体失败字段仍UNRESOLVED。

[最终裁决](DCL-R6-batch09/BATCH09_FINAL_DECISION.md) · [静态准入](DCL-R6-batch09/BATCH09_STATIC_ADMISSION.md) · [最小补充申请](DCL-R6-batch09/BATCH09_MINIMAL_SUPPLEMENT_REQUEST.md) · [证据索引](DCL-R6-batch09/EVIDENCE_INDEX.md)

D1-PBFT-SEAL/1.1、D2有限模型条件结论、强G覆盖、严格分离实例0和IMPLEMENTATION_GATE=CLOSED保持。以下保留全部先前导航，历史许可及创建状态按各阶段时点理解。

---

# DCL-R6-batch08-Diag 最新最小诊断裁决（2026-11-12）

PREFLIGHT_PASS / SAME_BOOT_CONFIRMED / C00_PASS：C00Ready-static-1/r2实际单会话启动，Root438/start4792跨exec；C00自查811/start4978同boot0cc7ff50…。真实1轮STARTING后2轮READY，首次凭据CR01–05 defer为NOT_READY，最终8项双侧全MATCH。wait返回区间0.149840881–0.155141782秒；精确pidfd/返回点未单独打点，D08-4总体FIELD_EVIDENCE_PARTIAL。

64项获准合成检查全部接受：47 PASS＋17 MUTATION_DETECTED，独立reference无差异。R450/450持久事务/900行配对；T0后10.267560352秒按C00_DIAGNOSTIC_COMPLETE正常关闭，进程/父组为空，原生100条目seal保存。源码/权限修复、重跑/恢复0，batch09创建0。

Full批准false，其余BC40/RootIPC56/C09H34/C01–C12/C09/S34/门17及F1/F4均未授权/未运行，RESOURCE_GATE_PASS仍NOT_OBTAINED。旧batch07具体失败字段保持UNRESOLVED；下一步可准备匹配新批次版本/锁的独立完整链，不恢复已CLOSED的batch08。D1-PBFT-SEAL/1.1原条件、强G覆盖、严格分离0、IMPLEMENTATION_GATE=CLOSED保持。

[最终裁决](DCL-R6-batch08-Diag/BATCH08_DIAG_FINAL_DECISION.md) · [字段证据](DCL-R6-batch08-Diag/BATCH08_C00_FIELD_RESULTS.md) · [证据索引](DCL-R6-batch08-Diag/EVIDENCE_INDEX.md)

以下完整保存本轮前历史导航，旧阶段许可/下一步/未创建文字按相应时点理解。

---

# DCL-R6-C00Ready-Fix 最新静态裁决（2026-11-11）

C00Ready-static-1/r2在host冻结：原真实8项逐字段审计/诊断、exec-ready三态与14秒同窗口屏障、双次采样/pidfd/native lease、C00/C10票据前复查；具体batch07失败字段仍C00_FAILED_FIELD_UNRESOLVED。原sealed/一次认领/exec与RootIPC/C09逻辑保持，15旧程序字节和24预算/资格函数AST保持。

CR-1/CR-4=PASS_STATIC，CR-2/CR-3=CONDITIONAL_PASS。64夹具/17mutant、24程序host语法/3.12文法和36项锁完成；native部署/查询/服务/测试/batch08创建0。最小C00_DIAGNOSTIC_ONLY完成后关闭，完整C/S/H/门/F1F4另需明确批准；新增449/512访问，完整cal硬上界62546≤100000，原300/1800及总1e6不扩。

batch07同PID/boot启动前缀、R0及原失败原件保持；旧预算/历史/误副本/blocked by policy保持。D1-PBFT-SEAL/1.1原条件、强G覆盖、严格分离0、IMPLEMENTATION_GATE=CLOSED保持。

[最终裁决](DCL-R6-C00Ready-Fix/FINAL_DECISION.md) · [batch08申请](DCL-R6-C00Ready-Fix/BATCH08_EXECUTION_REQUEST.md) · [证据索引](DCL-R6-C00Ready-Fix/EVIDENCE_INDEX.md)

以下为本轮前完整保存的历史导航，各旧阶段许可/下一步/未创建文字按相应时点理解。

---

# DCL-R6-batch07 最新实际裁决（2026-11-11）

RESOURCE_GATE_FAILED：BootContinuity-static-1/r4已实际单会话预检、sealed fd/一次认领、same-PID exec到Guard；活动boot060a08fc…、父PID828/start7252贯穿前缀。C00票据前服务复核抛BC_SERVICE_IDENTITY_OR_LIMITS，BOOT_START未发布；具体8路失配字段无快照，源码MainPID>0缺exec-ready屏障与Starting-only journal支持启动临态竞态假设。

T0=73.768774900，R0/1000000；T0+0.309347559闭合、+0.327163166组空，普通父waitpid raw32000/exit125。原生22条目seal、23 native文件、32冻结文件、34事件/15内部命令及7条run journal封存；source/权限修复、case重试、resume与batch08创建均0。BC40、RootIPC56、C09H34、真实C09、C01–C12、S34/门17及F1/F4都未完成准入；PASS_BOUNDED授予0。

下一步仅列有界exec-ready/稳定身份屏障及完整失败采样的最小静态修复方向，保持原身份/AS/ACK/停止断言。D1-PBFT-SEAL/1.1原条件、强G覆盖、严格分离0、IMPLEMENTATION_GATE=CLOSED保持。

[batch07最终裁决](DCL-R6-batch07/BATCH07_FINAL_DECISION.md) · [首次失败](DCL-R6-batch07/BATCH07_COUNTEREXAMPLES.md) · [证据索引](DCL-R6-batch07/EVIDENCE_INDEX.md)

以下为本轮启动前完整保留的历史导航，各旧阶段资格/许可/下一步按对应时点理解。

---

# DCL-R6-BootContinuity-Fix 最新静态裁决（2026-11-11）

BootContinuity-static-1/r4已在host冻结：单次WSL受信入口、same-PID exec与封印fd/持久一次认领、Root/服务内fresh复查、同一Root进程C09一次恢复；原14份程序字节与24预算/资格函数AST保持。新增40模拟回归/10变异，21程序host语法及3.12文法通过，32项包无旧pyc。

BC-1/BC-2/BC-4=PASS_STATIC；BC-3=CONDITIONAL_PASS。目标3.12原生编译、当前WSL/接口、真实启动及测试全部UNRUN；本轮新WSL调用/部署/服务/T0/账/batch07创建均为0。新许可须明确source-only、预检TCB120秒/AS1GiB、初始10秒ticket与同进程恢复；BC481与既有合计3231≤5000，运行1800/校准300及原硬额保持。

batch06的三boot/109.295102秒/PREFLIGHT_FAILED与目标启动0保持；具体触发源BOOT_CHANGE_CAUSE_UNRESOLVED。D1-PBFT-SEAL/1.1原条件、强G覆盖、严格分离0、IMPLEMENTATION_GATE=CLOSED保持。

[最终裁决](DCL-R6-BootContinuity-Fix/FINAL_DECISION.md) · [batch07申请](DCL-R6-BootContinuity-Fix/BATCH07_EXECUTION_REQUEST.md) · [证据索引](DCL-R6-BootContinuity-Fix/EVIDENCE_INDEX.md)

以下完整保留本轮之前历史导航；旧阶段许可/下一步/未创建文字按各自记录时点理解。

---

# DCL-R6-batch06 最新裁决（2026-11-11）

PREFLIGHT_FAILED / RESOURCE_GATE_FAILED_PREFLIGHT：RootIPC-static-1/r4基础hash/runtime/身份预检通过，六条冻结准备和授权安装完成；最终启动前boot由3f63d905…变为c92b8cbc…，same_boot检查失败，按首次失败规则停止。Launcher/模型启动0，T0/预算账未建立；56项RootIPC、34项C09H、C00–C12、S34、门17与F1/F4全部未运行。

事后boot为b69460ad…，专用进程与父cgroup为空；out/private空，仅两份授权文件和44项实际Linux冻结源封存。具体WSL生命周期触发源待确认；后续先收敛同boot预检与入口交接的行政编排，当前重试/恢复/代码修复0、batch07创建0。

batch05的RESOURCE_GATE_FAILED、R37293及原失败保持；D1-PBFT-SEAL/1.1原条件、强G覆盖、严格分离0和IMPLEMENTATION_GATE=CLOSED保持。

[batch06最终裁决](DCL-R6-batch06/BATCH06_FINAL_DECISION.md) · [首次失败](DCL-R6-batch06/BATCH06_COUNTEREXAMPLES.md) · [证据索引](DCL-R6-batch06/EVIDENCE_INDEX.md)

以下为本轮开始前完整保留的历史导航，各旧阶段许可/未创建/下一步文字按其记录时点理解。

---

# DCL-R6-RootIPC-Fix 最新静态裁决（2026-11-11）

RootIPC-static-1/r4完成有限静态修复：Root共享intent发布前固定999:989/0600，Root私有与payload可读收据分离；ready/RPC/父waitpid加入停止fresh-read及有限回收。修改原2份源码、新增3份；原12程序及24预算/资格函数保持，56专项夹具/8变异与最终44项文件冻结。

RI-1/RI-4=PASS_STATIC；RI-2/RI-3=CONDITIONAL_PASS。17份最终源码语法与44项host/Linuxhash通过；动态执行0，batch06未创建。下一动态申请绑定r4真实hash，并明确新增最多1个顺序降权探针TCB、完整C/C09H/IPC56/S/17门及资格后自动F1→F4。实际停止延迟和300秒可完成性仍待测量。

batch05原RESOURCE_GATE_FAILED、R37,293、303事务、真实C09 NOT_EXERCISED与全部失败证据保持。D1-PBFT-SEAL/1.1、强G原条件、严格分离0、IMPLEMENTATION_GATE=CLOSED保持。

[最终裁决](DCL-R6-RootIPC-Fix/FINAL_DECISION.md) · [batch06申请](DCL-R6-RootIPC-Fix/BATCH06_EXECUTION_REQUEST.md) · [证据索引](DCL-R6-RootIPC-Fix/EVIDENCE_INDEX.md)

以下完整保留本轮开始前的历史导航；各旧阶段“下一步/许可/未创建”文字按对应时点理解。

---

# DCL-R6-batch05 最新结果（2026-11-11）

实际RESOURCE_GATE_FAILED：C00–C08九项PASS；C09H34 accepted（28 PASS+6 MUTATION_DETECTED）；Root审查后intent变为root:root/0600，真实C09 uid999入口读取失败，持久ACK/交接退出见证尚未取得。预算37,293；payload在T0+20.927591657清空，Root约T0+300退出。C10–C12、S34、门17与F1/F4全部未运行；PASS_BOUNDED授予0。

当前batch05保持CLOSED；下一研究动作仅为审查共享账跨身份owner/mode与C09闭合等待的静态修复范围，审计全部Root全局记账路径，并在独立版本冻结后处理匹配动态许可。实现修改、权限修复、重试、恢复与batch06创建均为0。D1-PBFT-SEAL/1.1原条件、强G覆盖、严格分离0和IMPLEMENTATION_GATE=CLOSED保持；候选机制继续先过可证伪分离声明及严格实例门。

[batch05最终裁决](DCL-R6-batch05/BATCH05_FINAL_DECISION.md) · [首次失败](DCL-R6-batch05/BATCH05_COUNTEREXAMPLES.md) · [证据索引](DCL-R6-batch05/EVIDENCE_INDEX.md)

以下为本批启动前保留的历史记录；其中旧阶段“下一步/未授权/未创建”文字按其阶段理解。

---

# 当前裁决 DCL-R6-C09Fix

2026-11-11。[完整裁决](DCL-R6-C09Fix/FINAL_DECISION.md)、[时间线](DCL-R6-C09Fix/C09_EXECUTION_TIMELINE.md)、[安全属性](DCL-R6-C09Fix/C09_SAFETY_PROPERTIES.md)。

|门|状态|边界|
|---|---|---|
|C09-1 根因|PASS_STATIC|旧快照缺陷与单方交接未完成分别裁决，精确取s时刻保持未知|
|C09-2 修复|CONDITIONAL_PASS|持久ACK、真实退出见证、版本/闭合/身份/预算与一次分类齐全；IPC/故障/调度机器证据待运行|
|C09-3 静态|PASS_STATIC|14源语法、接口/状态/差异/哈希检查；10程序不变|
|C09-4 新执行|CONDITIONAL_PASS|实际版本锁、34C09H/原S34/门17/模型申请齐全；额外root协调器及时间可行性待新许可/实测|

batch04的C09退出意图已发布、exit23真实，但没有成功交接收据或接收ACK；关闭后的恢复拒绝符合安全要求。旧读取快照后等待pidfd的代码允许遗漏新意图，具体交错为源码推导。原裁决和37021账不改。

本轮不执行新退出/pidfd/socket/C/S/模型，actual为null/UNRUN。batch05未创建，T0/counter未初始化。原payload4tasks及100000/300、总1000000/1800/1740保持；新增C09H硬界5000，总cal硬界62034，可信root行政进程增量1必须明确授权。原D1/强G、严格分离0、主机制门CLOSED保持。以下历史裁决不覆盖。

---

# 当前裁决 DCL-R6-batch04

2026-11-11。[完整裁决](DCL-R6-batch04/BATCH04_FINAL_DECISION.md)、[资源账](DCL-R6-batch04/BATCH04_RESOURCE_ACCOUNTING.md)、[C09根因](DCL-R6-batch04/BATCH04_COUNTEREXAMPLES.md)。

|项目|本批实际裁决|
|---|---|
|预检|PASS：BF-static-2/r4、1274唯一Linux文件、身份/环境/单位核验；T0前boot变化已刷新|
|C校准|C00–C08共9机器PASS；C09监督器误关闭/无成功交接收据；C10–C12未运行|
|C02|单笔N32896、核心预留27.617904ms、11目标fsync合计16.141648ms；child17991操作/未用14905占用；结果T0+3.977400525秒|
|S1–S9|34job执行0，UNRUN_RESOURCE_GATE|
|门负向|17项执行/检出均0|
|资源资格|RESOURCE_GATE_FAILED；RESOURCE_GATE_PASS=NOT_OBTAINED|
|模型|F1/F4=UNRUN_RESOURCE_GATE；协议搜索/PASS_BOUNDED授予0|
|资源账/关闭|37021/1000000、31 PREP/31 COMMIT，关闭elapsed9.349857737秒，组空elapsed9.362411078秒|
|范围保护|源/输入/判据未改，resume0，无新批次或预算重置，原282研究/GC30/BF24/B02原件51/副本47保持|

C09的launcher实际按计划exit23，持久状态为expected_launcher_exit=C09、resume_count0；停止器在pidfd等待后使用先前状态快照进入UNEXPECTED分支，真实exit125。具体读时刻未打点，交错按源码与真实错误分支推导；没有附加重现试验。当前批次已CLOSED，后续另一boot的manager默认值与运行属性分开。

下一步先申请修复该监督器时序及受界回归，F2/F3前置条件尚缺。D1-PBFT-SEAL/1.1、强G、严格分离0、IMPLEMENTATION_GATE=CLOSED保持。以下为历史裁决。

---

# 当前裁决 DCL-R6-GapClosure

2026-11-11。[完整裁决](DCL-R6-GapClosure/FINAL_DECISION.md)、[测试矩阵](DCL-R6-GapClosure/S1_S9_FIXTURE_MATRIX.md)、[准入规则](DCL-R6-GapClosure/RESOURCE_GATE_EVIDENCE_RULES.md)。

|Gate|状态|范围|
|---|---|---|
|GC-1 测试完整性|PASS_STATIC|17子场景、34job、11类受限对象变异、统一oracle与实际故障/操作观察代码齐全|
|GC-2 资格门|CONDITIONAL_PASS|C/S/原始证据、17个负向门检查和健康主账强制准入；机器执行与TCB条件待验证|
|GC-3 静态安全|CONDITIONAL_PASS|N/费用/无退款、4tasks与原300秒/100000合同保持；I/O/调度/实际运行保留条件|
|GC-4 版本授权|PASS_STATIC|BF-static-2/r4及导出锁修订1真实hash/完整argv、旧许可差异与独立申请已冻结|

资源代码变更：guard.py修改，新增range_core/range_fixtures/range_evidence三文件；五业务、runner与guard_probe共7文件逐字节相同。S6双请求屏障保证两个申请在PREP前已进入；检查器安全断言不随safe/mutant变化。追加资格门拒绝陈旧/缺失/伪造字段，原始counter/journal/操作与实际触发须重算。

静态完成路径新增访问≤19229，RANGE硬限20000，含原C校准硬上界57034≤100000；仍共同T0+300、总1000000/1800/1740。11源码语法通过；17条WSL只读/编译命令有原始双流。144历史工件、原BF24项、B02原件51项及误副本47项hash保持，无清理尝试。

当前S1–S9、C00–C12与F1/F4运行0；RESOURCE_GATE_PASS=NOT_OBTAINED，F1/F4=UNRUN_RESOURCE_GATE。batch03仍为原预检停止，运行T0/账/关闭文件均未创建；新batch04仅有申请，尚未创建或授权。原D1-PBFT-SEAL/1.1、强G覆盖、严格分离0及主机制门CLOSED保持。以下为历史裁决。

---

# 当前裁决 DCL-R6-batch03

2026-11-11。[最终裁决](DCL-R6-batch03/BATCH03_FINAL_DECISION.md)、[预算安全结果](DCL-R6-batch03/BATCH03_BUDGET_SAFETY_RESULTS.md)、[首次阻断](DCL-R6-batch03/evidence/FIRST_BLOCKING_EVENT.json)。

|项目|实际裁决|
|---|---|
|授权|已收到C00–C12及全部必要条件满足后的自动F1→F4；AUTHORIZED_PREFLIGHT_BLOCKED|
|冻结源/输入|host24项和Linux1266唯一文件匹配；BF旧72项交付原锁已复核|
|当前环境|Python3.12.3、既定kernel/systemd、UID999/GID989与page4096匹配|
|启动前能力|RESOURCE_EVIDENCE_INCOMPLETE：精确范围S1–S9专项夹具缺失；formal门未检查这些必要证据|
|动态校准|C00–C12全部NOT_EXERCISED；新运行0|
|正式模型|F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED授予0|
|窗口与预算|T0/deadline/账未初始化；发放信用0，payload访问0，批耗时/峰值N/A|
|保护|BF源、五业务/runner、旧32191账/原失败、47误副本保持；配置写入/清理尝试0|

冻结launcher在13case局部PASS后自动进入FORMAL，当前测试覆盖无法满足本次§5“缺少某项故障注入能力……保持资源门关闭”和§6关键UNKNOWN排除条件；§9又要求保持BF-static-1。因此直接在初始化前阻断完整调度，未靠局部PASS或外部抢停放行。实际运行根/批03slice/cgroup均未创建；只有研究预检目录存在。

RESOURCE_GATE_PASS=NOT_OBTAINED；batch03=AUTHORIZED_PREFLIGHT_BLOCKED；主机制IMPLEMENTATION_GATE=CLOSED；严格分离0。原D1-PBFT-SEAL/1.1条件结论、D2有限模型边界和强G覆盖保持。以下为历史裁决。

---

# 当前裁决 DCL-R6-BudgetFix

2026-11-11。[完整裁决](DCL-R6-BudgetFix/FINAL_DECISION.md)、[崩溃条件证明](DCL-R6-BudgetFix/BUDGET_CRASH_SAFETY_PROOF.md)、[静态审查](DCL-R6-BudgetFix/BUDGET_STATIC_CODE_AUDIT.md)。

|Gate|状态|范围|
|---|---|---|
|BF-1 预算语义|CONDITIONAL_PASS|R/A/U及保守占用、S1–S9源码推导；存储、合作writer、时限前提与动态缺口保留|
|BF-2 代码修复|PASS_STATIC|两获准资源文件修改，最终八源语法/接口/调用点通过|
|BF-3 历史与源码|PASS_STATIC|五业务和runner字节相同，Perf/B02/副本及runtime关键文件/旧unit摘要匹配|
|BF-4 性能与准入|CONDITIONAL_PASS|BF-static-1、实际源/输入hash与完整主流程argv、独立执行申请冻结；范围专项故障夹具待另锁|

C02 N=32896，C03=4096，C04=1；新路径每task同步机会范围9+claim2=11；计费全额占用保持。遥测使用新COMMITTED stamp与持久完成事件，实际速度与fsync耗时仍未测。正常校准成功路径最大预留37034，共同校准截止仍T0+300。

batch02保持CLOSED_RESOURCE_GATE_FAILED及32191历史占用，C00/C01原PASS、C02预付298.626607199秒/child未启动事实保持。当前新target import/资源探针/C00–C12/F1/F4/性能测试/故障注入均0；只有静态准备与py_compile、只读hash/stat。误副本47项保留，原blocked by policy保持，无清理尝试。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；batch03=UNAUTHORIZED且目录/账/单位/receipt缺失；主机制IMPLEMENTATION_GATE=CLOSED、严格分离0。原WS4 E2、D1 1.1/D2条件结论及历史研究裁决保持。以下是此前裁决。

---

# 当前裁决 DCL-R6-batch02-Perf

2026-11-10。[最终裁决](DCL-R6-batch02-Perf/FINAL_DECISION.md)、[时间/账](DCL-R6-batch02-Perf/PERF_BUDGET_LEDGER_AUDIT.md)、[安全条件](DCL-R6-batch02-Perf/PERF_BUDGET_SAFETY_PROOF.md)。

|Gate|状态|范围|
|---|---|---|
|PERF-1 归因|PASS_STATIC|共同T0+300与精确里程碑/未知边界清楚，预付跨度298.627秒|
|PERF-2 预算成本|PASS_STATIC|32191来源/连续配对、同戳与O(1)逐项路径、混合周期分布有据|
|PERF-3 修复|CONDITIONAL_PASS|选精确N范围预留；BUD1–6、崩溃/并发/浪费及未来验收明确；无实现/动态验证|
|PERF-4 B03准入|PARTIAL|先有限静态修复再独立B03申请；新代码hash/完整argv尚缺，未创建环境|

关键实测：C00/C01到结果1.109256092秒；PREP4至PREP32191为298.626607199秒/99.5422%软窗；32187个周期均值9.277864ms，P99 15.226956ms，约107.783/s。COMMITTED复用PREP时间，禁止用0差值推断fsync耗时。逐完整预留7同步为源码事实，225337为静态机会值，实际细分UNKNOWN_INTERVAL。

32191拆为C00入口1、C01入口1、C02入口1、子信用预付32188。内存child未启动、F1/F4状态0；最后grant-return边界未单独记时，保持推断上下界。原账不减，不回收预付。主选A0保持N总占用/总资源/软300，减少重复事务；通用ticket pool/加窗留备选。

本轮代码/探针/Linux命令/配置/新校准/模型/新批环境均0。两个ZIP直接核验通过，误路径47文件只读匹配，拒绝原信息保持且无新清理尝试。batch02仍CLOSED_RESOURCE_GATE_FAILED，RESOURCE_GATE_PASS未取得，F1/F4仍UNRUN_RESOURCE_GATE；batch03未创建/未授权。

原WS4 E2未决、D1 1.1/D2条件结论、强G覆盖、I1/I2/I3归档、严格分离0及IMPLEMENTATION_GATE=CLOSED保持；原27/118.7340827和B02/LC/各历史工件不变。以下为历史裁决。

---
# 当前裁决 DCL-R6-batch02

2026-11-10。[实际裁决](DCL-R6-batch02/BATCH02_FINAL_DECISION.md)、[校准原结果](DCL-R6-batch02/evidence/BATCH02_RUN_RESULTS.json)、[完整资源账](DCL-R6-batch02/evidence/BATCH02_ACCOUNTING_ACTUAL.json)。

|Gate|状态|依据|
|---|---|---|
|B02-1 环境/兼容|PARTIAL|53项原生摘要匹配，3.12资源程序真实运行；五业务动态兼容未到达|
|B02-2 资源资格|FAIL|C00/C01冻结谓词PASS；C02软时限阶段原FAIL，C03–C12未完成|
|B02-3 F1|UNRUN|UNRUN_RESOURCE_GATE，真实模型访问0|
|B02-4 F4|UNRUN|UNRUN_RESOURCE_GATE，DP/REF/G64/变异未跑|
|B02-5 完整性|CONDITIONAL_PASS|账/退出/原ZIP/快照/hash可核；行政误路径副本清理尚未完成|

C02在持久预付尚未完成时达到T0+300秒，Watchdog expired，Controller信号9，Root exit65；内存分配子进程未创建，无法据此判AS触发或协议错误。原FAIL与分析INCONCLUSIVE_LIMIT_CALIBRATION_SOFT_TIME分列，未扩大软预算。

资源账32191/1000000，journal两阶段各32191，最终COMMITTED，无模糊事务/信用回收。T0+300.1698498秒CLOSED，父树空、所有实际瞬态单位MainPID0/not-found。charge峰值观测下界55,111,680字节，精确RSS瞬时树峰值未观察；指标不混用。没有C09恢复、重复启动、源码修改或batch03。

batch02=CLOSED_RESOURCE_GATE_FAILED；RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED为空；协议反例0。原state.status仍CALIBRATING，CLOSED文件是权威停止记录，原件不改。普通预付信用32191与模型状态展开0分别登记。

原batch01的27次/118.7340827秒/关闭deadline、v1/v2/v3和R1–R6各阶段/L-C保持。原WS4 E2=UNRESOLVED、D1-PBFT-SEAL/1.1、D2条件结论、强G覆盖、I1/I2/I3归档、STRICT_SEPARATION_INSTANCES=0及IMPLEMENTATION_GATE=CLOSED不变。

正确host快照/原ZIP完整；误路径副本的迁移/删除被自动审批拒绝（仅返回blocked by policy），采用安全复制替代后保留重复副本。此行政事项不改变Linux原件/资源失败。以下为历史裁决。

---
# 当前裁决 DCL-R6-LC

2026-11-10。[最终裁决](DCL-R6-LC/LC_FINAL_DECISION.md)、[静态检查](DCL-R6-LC/LC_STATIC_VERIFICATION.md)、[最终执行锁](DCL-R6-LC/evidence/LC_EXECUTION_LOCK.json)。

|Gate|状态|边界|
|---|---|---|
|LC-1 运行时|PASS_STATIC|CPY312-UBU24/1精确合同/身份/文件快照完整，兼容性尚待动态|
|LC-2 配置|PASS_STATIC|UID999/GID989、目录与两个inactive单位实际完成；verify/属性/权限一致|
|LC-3 适配|PASS_STATIC|三资源文件Linux接入和语法/差异审查；五业务hash不变；无目标模块正文执行|
|LC-4 后续准入|CONDITIONAL_PASS|真实argv/源/输入/权限/停止锁可审；特殊映射/资源资格/新batch02许可仍缺|

解释器/usr/bin/python3.12，3.12.3，SHA=e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f。静态manifest SHA=cf9442307d99f82dcec8fb542373340f9c2531ca58e9c7aa8be09edf2eab0ebd，执行锁SHA=85cd66643b0ee1f933bb035e220591ef0ce4c106e7cc71bf632702cd3b5c0be9。1224标准库代码树、31关键文件、16源/缓存条目冻结，动态解析和语义未验证。

已写两个获准单位并daemon-reload一次，均inactive/dead、MainPID0；旧mnt-e.mount失败保持。新源码仅独立lc01的guard/guard_probe/run_batch，原v3和五业务原件不动。许可/资格链结合实际OS事实，模型前拒绝缺资格；C00–C12代码尚无actual运行。

RUNTIME_COMPATIBILITY_UNVERIFIED、RESOURCE_ENFORCEMENT_UNVERIFIED、MODEL_CHECK_UNRUN；RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；batch02=UNAUTHORIZED且目录未创建。LC平台准备与账/时间窗分开，原27次/118.7340827秒/关闭deadline不变；boot代次变化保留，新批须新绑实际boot且不补窗。

原WS4 E2=UNRESOLVED、D1-PBFT-SEAL/1.1、D2条件结论、强G覆盖、I1/I2/I3归档、STRICT_SEPARATION_INSTANCES=0、IMPLEMENTATION_GATE=CLOSED保持。[新批申请](DCL-R6-LC/LC_BATCH02_AUTHORIZATION_REQUEST.md)另含新增父slice/瞬态停止/14payload单位及唯一C09同窗恢复，当前未执行。

以下为历史裁决，以本LC节为当前状态。

---
# 当前裁决 DCL-R6-LR

2026-11-10。[最终裁决](DCL-R6-LR/LR_FINAL_DECISION.md)、[兼容性审查](DCL-R6-LR/LR_PYTHON_COMPATIBILITY_AUDIT.md)、[下一专项申请](DCL-R6-LR/LR_NEXT_AUTHORIZATION.md)。

|Gate|状态|边界|
|---|---|---|
|LR-1 运行时定位|CONDITIONAL_PASS|原生3.12.3路径/包/ELF/摘要及直接库有据；完整来源/依赖/映射闭包待证|
|LR-2 兼容性|CONDITIONAL_PASS|五业务文件静态支持3.12候选；真实编译/导入/语义/跨版本实测0|
|LR-3 权限部署|PARTIAL|manager/cgroup/身份/目录/资源接入必要条件已明确，尚未配置/校准|
|LR-4 后续路线|PASS_STATIC|选择L2并形成可审L-C写入/命令/停止范围，batch02最终锁未就绪|

选择CPY312-UBU24/1候选：/usr/bin/python3.12，Python3.12.3，python3.12-minimal=3.12.3-1ubuntu0.17，SHA256=e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f。当前PROPOSED_NOT_ADOPTED；原3.14合同保留。有限目录/本地缓存未发现3.13/3.14，未全盘搜索/更新/下载。

manager Version255.4-1ubuntu8.18可读，SystemState=degraded，失败清单仅mnt-e.mount；本轮不修复/mount。根/system.slice资源相关现值无限，目标父tasks4/AS1GiB未建立；dcl-r6账户/组及/var/lib/dcl-r6/batch02路径缺失。root只读管理能力不等于已获配置许可或完整沙箱证明。

LR完成35条Linux查询，唯一Python调用为--version；另有本地静态ELF/源码/哈希行政读取。新增验证代码、配置、安装、探针、校准、模型均0。资源三文件只交付接入设计，五业务hash不变。

L-C=UNAUTHORIZED；batch02=UNAUTHORIZED；RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；原WS4 E2=UNRESOLVED。D1 1.1、D2条件结论、G覆盖、归档I1/I2/I3、STRICT_SEPARATION_INSTANCES=0及IMPLEMENTATION_GATE=CLOSED保持；27次/118.7340827秒/旧关闭deadline、v1/v2/v3与P/Envelope原件保持。

以下为历史裁决，当前状态以前置LR节为准。

---
# 当前裁决 DCL-R6-P

2026-11-10。[最终裁决](DCL-R6-P/P_FINAL_DECISION.md)、[AS4前提矩阵](DCL-R6-P/P_AS4_ASSUMPTION_MATRIX.md)、[平台原始记录](DCL-R6-P/evidence/P_COMMAND_RESULTS.json)。

|Gate|状态|含义|
|---|---|---|
|P1 运行平台|PASS_STATIC|实际kernel/架构/PID1/工具版本证据齐备，限只读资格审查|
|P2 cgroup|CONDITIONAL_PASS|实际cgroup2与根memory/pids能力、启用有据；目标slice/限制/权限未建|
|P3 身份及运行时|FAIL|root身份仅提供管理线索；两个指定native Python3.14路径缺失|
|P4 替代合同|PARTIAL|A1–A5接口承载平台获得观察；有效设置/映像/权限/特殊映射/停止仍待证|
|P5 batch02准备|PARTIAL|L精确补缺清单已给；runtime/UID/资源接入/最终命令尚缺|

P=AUTHORIZED_AND_COMPLETED：12条argv严格顺序执行，11条exit0、末条ls exit2，额外Linux命令0。实际kernel6.18.33.2-microsoft-standard-WSL2/x86_64，PID1=/usr/lib/systemd/systemd，systemctl255.4-1ubuntu8.18，根subtree_control=cpu memory pids；当前身份root。Python缺失状态限定/usr/bin/python3.14与/usr/local/bin/python3.14，未全盘搜索。

AS4-PAYLOAD/1=PRINCIPLE_ACCEPTED_FOR_REVIEW；L实现/配置与batch02仍UNAUTHORIZED；RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；原Windows WS4 E2=UNRESOLVED。当前没有目标AS1GiB/pids4共同生效的部署实例。

本轮仅启动获准Ubuntu-24.04并查询；未请求其他发行版/Docker启动，未执行停止或追加状态命令。最终客户端退出后的即时状态未另查。新增代码/校准/模型/配置/安装0。27次、118.7340827秒、过期关闭的batch01、v1/v2/v3和全部失败/ZIP/Envelope原件保持；D1 1.1、D2条件结论、强G覆盖、归档I1/I2/I3、严格分离0及IMPLEMENTATION_GATE=CLOSED保持。

以下为历史裁决，当前状态以前置P节为准。

---
# 当前裁决 DCL-R6-Envelope

2026-11-10。[最终裁决](DCL-R6-Envelope/FINAL_DECISION.md)、[后端对照](DCL-R6-Envelope/RESOURCE_BACKEND_COMPARISON.md)、[资源证明](DCL-R6-Envelope/STRICT_MEMORY_BOUND_PROOF.md)。

|Gate|状态|边界|
|---|---|---|
|E1 方案可行性|CONDITIONAL_PASS|三路线具体审查；选 C，实际平台待核|
|E2 原严格资源证明|UNRESOLVED|Windows 全生命周期/峰值窗口未闭合；cgroup charge 和暂时超限无法替代原 WS|
|E3 执行架构|STATIC_DESIGN_COMPLETE_CONDITIONAL|父 slice 总任务界、角色/首入口/全部失败停止明确；尚无运行接线|
|E4 batch02准入|PARTIAL_UNAUTHORIZED|校准/顺序/结果清单已给；实际平台/runtime/适配器/全命令摘要待补|

推荐待批准 AS4-PAYLOAD/1：native Linux 每进程 AS≤1 GiB＋同批总tasks≤4，在启动映像/映射/权限/归属前提下有 payload 驻留和≤4 GiB。外部 Launcher/systemd/pre-exec helper/宿主边界与墙钟终止假设均显式修订，当前未采用。原 RESOURCE_GATE_FAILED 保留，RESOURCE_GATE_PASS 未取得；F1/F4 正式0、PASS_BOUNDED空。

本轮只读管理查询3项：WSL列表/版本、Docker固定本地端点info。三发行版均Stopped，端点连接失败；安装kernel元数据无法证明活动Linux能力。新增验证程序/校准/模型/环境启动/配置/安装均0。v1/v2/v3、原ZIP和62文件/业务五hash、27次/118.7340827秒/旧deadline保持。

D1-PBFT-SEAL/1.1、D2条件结论、强G覆盖、I1/I2/I3归档、STRICT_SEPARATION_INSTANCES=0、IMPLEMENTATION_GATE=CLOSED不变。[独立合同/授权申请](DCL-R6-Envelope/BATCH02_AUTHORIZATION_REQUEST.md)先申请有限平台 P 阶段，当前未创建batch02。

以下为历史裁决；当前状态以前置 Envelope 节为准。

---
# 当前裁决 DCL-R6-B-Repair

2026-11-10。[修复裁决](DCL-R6-Repair/FINAL_DECISION.md)、[根因审查](DCL-R6-Repair/RESOURCE_FAILURE_ROOT_CAUSE.md)、[严格界责任](DCL-R6-Repair/RESOURCE_BOUND_PROOF.md)为最新入口。

|Gate|状态|范围|
|---|---|---|
|RG-1 根因审查|CONDITIONAL_PASS|API/ABI/原日志/时窗链已审，87唯一原因与峰值内核机制仍未认证|
|RG-2 v3修复|PARTIAL|资源三文件静态修补，五业务hash一致；严格启动包络/运行接线仍缺|
|RG-3 硬资源资格|UNRUN，保持FAILED|batch01到期关闭，新批未授权，v3未执行，暂无完整硬界证明|
|RG-4 模型资格|UNRUN_RESOURCE_GATE|F1/F4未恢复，PASS_BOUNDED为空|

v3在versions/v3独立保存，batch01/src、v1/v2、原62文件/60项ZIP和27/118.7340827旧账全部保留。仅静态代码/差异审查，新增Python/校准/模型执行0。代码拒绝自动建窗和未证资源准入；当前适配器未实现，不宣称完整可运行监督器。

确认子当前内存取自释放后，父当前内存取自退出后；Job首成员进入前已设限，旧成员前占用解释缺源码支持；4KiB与页面相等仅是线索。控制器启动窗、guardian异常/独立模型入口和计数中断防护已具体化。

下一步先建立可信启动前资源包络与指标对应，再申请独立诊断批次并完整校准；[申请草案](DCL-R6-Repair/NEXT_BATCH_AUTHORIZATION.md)保留技术前置。Docker/WSL仅查到CLI，Docker as快捷方案已由官方规则排除。当前不创建/启动新环境。

协议1.1及D2纸面条件、强G覆盖/I1–I3归档、严格分离0、机制门CLOSED保持。F2/F3、Casdoor、原生/凭据、外发均未执行。

---
# 当前裁决 DCL-R6阶段B：资源门失败

2026-11-10。[R6最终裁决](DCL-R6/R6_FINAL_DECISION.md)、[资源校准报告](DCL-R6/R6_RESOURCE_CALIBRATION_REPORT.md)与[机器清单](DCL-R6/evidence/stage_B/RUN_RESULTS.json)为当前入口。专项许可已正式取得，八程序及v1/v2已保存；F1/F4未启动。

|Gate|结果|范围|
|---|---|---|
|R6-B1 资源校准|FAIL|v1 Job设置错误87；v2 normal/counter通过，memory峰值判据失败|
|R6-B2 F1|UNRUN|INV1–8、基线/变异/重放0，状态UNRUN_RESOURCE_GATE|
|R6-B3 F4|UNRUN|独立参考/DP/交叉/G64均0，状态UNRUN_RESOURCE_GATE|
|R6-B4 证据完整性|CONDITIONAL_PASS|首次失败、版本/锁/命令/校准保存；初始化前峰值及精确树WS缺测明确保留|

统一访问27次，全部校准；118.7340827秒至v2退出，计时/计数未重置。96MiB测试Job报告109.83203125MiB提交峰值，32MiB HardWS下进程峰值多4096字节。已捕获MemoryError，但峰值/硬界指标对应未闭合；不据此认定整批实际超过4GiB，也不放宽口径继续正式模型。

本批RESOURCE_GATE_FAILED并停止，正式模型反例0、原协议缺陷观察0均只因尚未验证；PASS_BOUNDED为空。D1/D2纸面条件保持，1.1未升级，LEVEL-3/4/5协议证据0，强G覆盖/I1–I3归档/严格分离0/机制实现门CLOSED维持。原生/构建/依赖下载/外发0，R1–R5冻结。

当前阻碍为资源资格，许可已批准的同范围无需重复确认。下一步先核实峰值计账与严格合成界并完整校准，再进入F1→F4。下方保留阶段A及历史裁决。

---
# 当前裁决 DCL-R6阶段A

2026-11-10。[R6最终裁决](DCL-R6/R6_FINAL_DECISION.md)及[范围](DCL-R6/R6_VERIFICATION_SCOPE.md)为当前入口。专项执行许可尚未取得；F1/F4均UNRUN_PERMISSION，模型/参考/监督程序0、模型执行0。当前已完成允许的工具/规格预审及完整待授权合同。

|Gate|结果|边界|
|---|---|---|
|R6-A 模型规格|CONDITIONAL_PASS|F1多head/独立RHO监视、INV1–8与F4双语义/有限域/夹具/G64；代码及实际覆盖待授权|
|R6-B 机器验证|UNRUN_PERMISSION|访问/峰值/耗时/反例等机器字段null，尚无PASS_BOUNDED或LEVEL-3|
|R6-C 证明责任|CONDITIONAL_PASS|D1/D2纸面条件保持，输入完整/模型非真空/真实部署与无界责任继续待证|
|R6-D 路线|PASS（决策范围）|先专项许可及资源监督校准，再F1→F4；后续F2/F3/原生独立准入|

实际工具仅确认Java8u502、Python3.14.0；当前官方TLC要求Java11+，TLC/Apalache在已查目录未发现。最小申请复用现有Python/标准库，无下载；资源硬界/工作集口径须校准。工具版本查询2次与行政哈希不计作模型运行。

拟议F1/F4单批100万访问、30分钟、4GiB进程树峰值，所有baseline/变异/参考/校准共享限额。具体八程序、写入目录和命令见[R6专项申请](DCL-R6/R6_TOOLCHAIN_AND_PERMISSION.md)。当前不创建验证代码，不访问原生环境或外发。

D1-PBFT-SEAL/1.1继续CONDITIONAL_PROTOCOL_COMPLETE；D2有限精确模型条件定理保持。强G覆盖/I1–I3归档、严格分离0、NOVELTY_UNVERIFIED、IMPLEMENTATION_GATE=CLOSED。原R5目录/盲审包冻结复用，根四份旧导航/历史保存revisions/DCL-R5。

---
# 当前裁决 DCL-R5

2026-11-10，Asia/Shanghai。[R5最终裁决](DCL-R5/R5_FINAL_DECISION.md)与[增量索引](DCL-R5/README.md)为当前入口；下方历史按原内容保留。

|Gate|状态|范围|
|---|---|---|
|R5-A 关键证明责任|CONDITIONAL_PASS|P1–P5/D2矩阵；旧Stop/完整child激活/摘要pin分层，未登记发送及许可时点界|
|R5-B 部署证据|PARTIAL|官方ZIP/checksum摘要匹配；版本stamp hook及sqlite配置增量；真实dirty全集/运行连接待证|
|R5-C 验证准入材料|CONDITIONAL_PASS|F1–F4有限域/资源/变异及T1–T4逐端点/清理/停止齐列；代码/工具/fixture/授权绑定待补，执行未授权|
|R5-D 论文/路线|PASS|路线A验证优先，B工程化保留，C独立创新未启动；贡献与成熟技术归属明确|

D1-PBFT-SEAL/1.1继续纸面CONDITIONAL_PROTOCOL_COMPLETE，D2有限精确模型条件可靠/完备。旧quorum钥泄露的扩展目标及实际部署另有前提；本轮未发现满足全部明示模型假设的唯一历史反例。

S2(T)保留600/1800秒、10/20/24，补齐备用Gate事前当前资格、reserved/UNKNOWN和共享P服务条件。原生预登记展开最多92次HTTP，保留114封顶；NC2清理额度改为12，全局cleanup40保持。独立审查第一阶段输入已单独打包，外部审查完成0。

源码语义SOURCE_SEMANTICS_CONFIRMED，构建BUILD_CORRESPONDENCE_CONDITIONAL，实际行为DEPLOYMENT_BEHAVIOR_UNVERIFIED。强G覆盖/I1–I3归档保持，严格分离0，NOVELTY_UNVERIFIED，IMPLEMENTATION_GATE=CLOSED。模型程序/机制代码/构建/新原生请求/机器证明/外发均0。

R4目录和原182文件ZIP保持原件，仅根目录四份旧导航/历史保存在revisions/DCL-R4。原33输入及R1–R3归档继续锁定；行政核验与协议证明分列。

---
# 当前裁决 DCL-R4

2026-11-10，Asia/Shanghai。完整裁决见[DCL-R4最终报告](DCL-R4/R4_FINAL_DECISION.md)，文件导航见[R4索引](DCL-R4/README.md)。下面各轮历史按原内容保留；历史“最新”字样指各自时点。

|Gate|状态|关键边界|
|---|---|---|
|R4-A 证明复核|CONDITIONAL_PASS|P1–P5/D2同会话重新推导与反例；原生/真实费用进展条件化；外审/机器证明0|
|R4-B 部署精化|PARTIAL|A/B/C和源码—构建—Gate—P映射完成；实际仍单活，dirty构建/稳定恢复/V分离待证|
|R4-C B支持|CONDITIONAL_PASS|S1允许暂停；共主Q的单/双Gate无法满足S2；独立路径有限S2(T)条件见证与cut已给|
|R4-D 审查资料|PASS（准备范围）|本地审查ZIP、形式化/原生计划与论文边界齐备；未外发/未执行|

D1-PBFT-SEAL/1.1为CONDITIONAL_PROTOCOL_COMPLETE纸面实例。D2在有限精确模型下条件可靠/完备，包含真实中间前缀和累计费用；实际配置/求解实现及无限持续保证待证。

新增静态证据确认现存二进制声明Go1.26.10、固定commit及vcs.modified=true，本地ZIP内exe相同。源码—发行物精确对应仍UNPROVED。NC1/NC2保持SOURCE_FEASIBLE，新运行0；SC-A2A/Dyno正文SOURCE_UNRESOLVED。

I1/I2/I3继续COVERED_BY_G / MODEL_BLOCKED，严格分离0，NOVELTY_UNVERIFIED，IMPLEMENTATION_GATE=CLOSED。新增机制/模型代码、构建、原生请求、机器证明、外部审稿完成及外部联系/上传均0。原33输入及46/94/120份R1/R2/R3归档保留，完整性/链接/JSON/包哈希只作行政核验。

---
# 当前裁决 DCL-R3

2026-11-10，Asia/Shanghai。研究跨2026-11-09—10。R2的94份活动工件已完整归档于revisions/DCL-R2，R1归档与原33输入继续保留。

|审查对象|本轮结论|精确范围|
|---|---|---|
|NC1 / NC2|SOURCE_FEASIBLE|重新从调用链、XORM1.1.6、SQLite事务、主键和删除返回值构造；正常并发/DB条件下可行，原生新增实测0；额外部署串行层仍需单列|
|原生入口/截止|定义与分类已精化|NativeCreationCut覆盖全部入口、历史材料和在途handler；区分名义grant与存储GrantType；补Session/GetAccount条件创建入口|
|D1-PBFT-SEAL/1|CONDITIONAL_PROTOCOL_COMPLETE（纸面实例）|签名版静态PBFT＋唯一Seal/child＋完整验根接续；八步、消息/phase、故障流程和证明齐备。实际代码/跨域部署、移动旧钥攻击及全部署精化另待证|
|原强A停/B保留目标|按配置条件裁决|顺序Seal暂停主Q；B只有此Gate路径时原Support(B)失败，不能宣称原强目标通过。需D2验证独立持续支持及真实native截止|
|D2费用|有限精确模型下条件可靠/完备|COST1重新推导；累计费用阈值递推、非空Post、严格义务终态、费用观察与最大费用压缩条件明确；新求解执行0|
|组合|纸面条件保持证明|转交空窗EnvClosure、动态泄露包络、旧证书暂停/重验、来源/预算/义务/费用及claim不变量保持|
|新独立机制I1/I2/I3|COVERED_BY_G / MODEL_BLOCKED|每项两轮最小反证；登记责任完整性、动态证书与原生分类均缺候选专属保证或必要费用差|
|来源与独立性|SOURCE_UNRESOLVED / NOVELTY_UNVERIFIED|PBFT关键原文、XORM/SQLite新增一手证据；SC-A2A/Dyno全文仍有缺口；同一对话内重新推导，外部复核/机器证明0|

## 当前Gate

- Gate A：PASS_STATIC_SCOPED，原生与DB语义复核加强，部署实际可达/源码二进制符合性仍条件化。
- Gate B：PARTIAL_SOURCE_GAP，核心近邻/强G构造已审，全文/工件缺口保持。
- Gate C：CONDITIONAL_SPEC_CLOSED，限D1纸面实例与有限D2/组合合同。全目标、全配置、实际部署及外部验证未授予PROTOCOL_COMPLETE或REVIEW_READY。
- IMPLEMENTATION_GATE：CLOSED；严格分离实例0。协议条件完整性与原创性分别裁决。

本轮新增机制代码、机器验证程序、原生请求、实验和对外联系均为0。三项新架构创新主张按两轮覆盖/受阻结果归档，保留D1/D2作为条件安全架构与原生审计章节。具体证据入口见R3_NOVELTY_DECISION、R3_SOURCE_INDEX及各R3审查稿。

---

# DCL-R2历史裁决（保留）

2026-11-09，Asia/Shanghai。本节为最新裁决；R1历史见后文及revisions/DCL-R1。

## 本阶段结果

固定Casdoor源码HEAD与官方v4.25.0均指向528a0213f01caf70b9f41009cbf7b2f67bdd67ec；现存二进制哈希匹配历史M6锁。26份源码副本和13操作×18字段能力合同已经保存。源码→二进制可复现构建仍UNPROVED，新增原生请求/候选机制代码/实验/机器证明均为0。

|对象|当前规格/保证|创新与部署裁决|
|---|---|---|
|D1-R2|保留21转换与9条原反例；新增RHO、六类生效边界、Casdoor微步骤与NC1–7；SPEC_REFINED_CONDITIONAL|受信有限profile可接管责任、对账并继续独立B；完整BFT/部署全执行精化待证|
|D2-R2|原生行/RTcohort/session/user/app footprint、C0–C6真实配置、S_bypass及证书失效条件|有限配置/鲁棒观察博弈由通用G覆盖；配置安全依赖真实原生/托管证据|
|CD25-BOUND|M3/M4/M6的S/U/L饱和关闭前提得到源码重核|继承有限原生证据，保持可信创建者/范围/来源边界|
|CD25-LEAK|E1持password RT/密码/原生旁路时，Q变更不足以截止；共享cohort可连带B|强目标按条件MODEL_BLOCKED/INFEASIBLE；双方受同一限制|
|联合架构|保守handler相位模拟、RHO保持、旧证书失效与I_post条件已补|继续归为条件工程集成；一般精化和持续验证形式已有近邻|

## 新增关键事实

1. RFC7009端点已存在于指定版本。撤销同一Token行影响该行AT/RT，并可扩散到相同RT哈希活动行；轮换后的异哈希子行另查。
2. 刷新先读取/检查父、后插入子、再删除父。NC1/2给出撤销ACK后插入子行及同父双刷新的源码允许并发历史；新原生复现为0。
3. password grant发行的RT可在刷新时省略client_secret；专用刷新入口与统一token入口的GrantTypes检查不同。仅旋转secret或拒绝单入口不足以证明全部创建截止。
4. 普通审计在AfterExec后异步持久化，存在遮盖/分页/保留边界，缺request→新jti的原子完整来源合同。
5. COST1反驳了隐藏世界费用逐段max相加的通用精确最优性；修订为累计费用扩展＋阈值博弈。双方共用修正，原生相同轨迹的等费覆盖保持。

## 三项验收门

|Gate|状态|依据与剩余责任|
|---|---|---|
|A 原生语义精化|PASS_STATIC_SCOPED|关键指定API、21转换、M3/M4/M6条件、缓存/在途与历史bearer反例均已审；源码运行符合性及任意RP效果继续条件化|
|B 强基线审计|PARTIAL_SOURCE_GAP|AID/RQ/EB关键机制与相关证明段对照、同能力G和S1–S4反证完成；SC-A2A正文/实现获取失败，部分先例工件未重核，全面来源门暂缓|
|C 完整协议研究|PARTIAL_PROTOCOL_REFINED|D1/D2与联合规格已精化；独立创新候选按覆盖/受阻归档。一般分布式协议的具体BFT重配置、全部署精化及外部复核仍待补；PROTOCOL_COMPLETE/REVIEW_READY暂缓|

强G仍覆盖已具体化的可行功能与主要原生动作成本；S1为本轮新的最小分离尝试，加入标准计数/关闭组件后被完整G匹配。S2是双方不可行，S3信息不足，S4配置停止声明被源码反例推翻。严格分离实例仍为0，独立架构创新证据仍待取得，IMPLEMENTATION_GATE=CLOSED。

本阶段允许的研究已完成源码/规格与覆盖审计交付，来源/部署缺口明确保留。下一轮最高优先级见NEXT_ACTION；新增实现计划继续受用户既定门限约束。

---

# DCL-R1历史裁决（保留）

2026-11-09，Asia/Shanghai。裁决限本目录冻结的接口、故障、有限目录与度量。

|对象|规格状态|保证与覆盖|原创性 / 实现门|
|---|---|---|---|
|D1-R0：复制账本＋新代次接管|已被反例修订|旧 bearer 继续使用、延迟旧发送、历史派生遗漏|该版本判废|
|D1-R1：带持久责任和原生截止条件的接管|主要角色、消息、转换及异常已列明；SPEC_DRAFT|账本性质有归纳论证；原生性质依赖接口与部署；冻结有限子域 COVERED_BY_G|NOVELTY_UNVERIFIED；分离门未通过|
|D1 强原生停止，Provider 持续接受旧域已知 bearer|边界条件明确|MODEL_BLOCKED；CE1 给出直接反例及条件不可能性|边界结论的独立优先权待核|
|D2-R1：历史暴露、故障域与原生接受路径联合配置|有限模型、求解关系及证书规格已给出|显式模型下有条件可靠性/完备性证明；通用有限博弈/SMT 可表达相同问题|COVERED_BY_G 限冻结编码；NOVELTY_UNVERIFIED|
|D1+D2|配置到运行的模拟关系及迁移守卫已定义|当前归为工程集成；实际适配器精化待证|独立联合贡献未成立|

`PROTOCOL_COMPLETE` 与 `REVIEW_READY` 本轮暂缓授予。剩余责任包括：完整原生 profile、成员变更协议实例、对动态攻陷/恢复的机器检查、原生到模型的精化、公开先例覆盖的进一步核读以及外部复核。协议完整性、正确性、性能优势、发表优先权分别裁决。

本轮实质结果：

- 修订了跨域接管中的迟到请求问题：迁移 owner 的变化只转移账本职责；原生截止必须在接受方落实。
- 将重试拆为原 key 精确重放与原生终态无效果后的单继任，两条均保持原业务意图、来源和预算谱系。
- 给出 2-of-3 保管＋单点完整重建的能力传播反例；披露历史保持单调，原生可用性另行更新。
- 给出隐藏状态下“每个世界分别有解”与“同观察可执行策略存在”的区别及两世界反例。
- 为固定有限模型构造 G1 的逐转换模拟与 G2 的相同公式编码。两者消除了本轮候选的功能/主要成本分离预测。

本轮没有发现通用方法必须付更高代价的严格实例。[分离门](SEPARATION_GATE.md)记录具体输入、固定指标、G 的处理和判废条件。继续实现的前提尚待补齐。

文献范围：九类指定近邻均做检索；Horcrux、WAVE、SAGA、AID-Guard、EFFECTBOUND、Root-Scoped Quiescence、Seal、Lit 已取得可定位的一手内容，读取深度各异；SC-A2A 取得 IEEE 题录片段及 Crossref 作者/DOI，正文待补。国内数据库、部分会议/期刊、专利审查深度有限，全球首次保持待核。
