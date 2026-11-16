# PF-1至PF-10安全性质与关闭审查

Material Passport：PTA-PhaseFinalizer-static-1/r3；DCL-R6-PTA-PhaseFinalizer-Fix；2026-11-12；HOST_STATIC_ONLY。

|性质|源码/字段与静态断言|证据范围|
|---|---|---|
|PF-1 PhaseMonotonicity|_set_phase_locked；PHASES、sequence、previous_sha256；固定seq索引和相邻转换检查|PASS_STATIC，Native转换UNRUN|
|PF-2 RuntimeIdentityConsistency|binding、window、initialization_id、counter身份；scheduler pid/starttime/boot；当前回执导出绑定|PASS_STATIC，真实跨进程检查待验|
|PF-3 NoPrematureWork|require_work只允许ARMED/RUNNING；当前scheduler；原launch_one/C00资格保持|PASS_STATIC，原守卫接线保留|
|PF-4 IllegalDriftRejected|同锁读取；phase/sequence/record SHA/初始化ID匹配；缺件和错误抛出|PASS_STATIC，真实损坏注入UNRUN|
|PF-5 BoundedPhaseTransition|原pt_phase.lock，512尝试/2秒及原期限取小；STOP/CLOSED每轮优先|CONDITIONAL_PASS，OS响应/性能待验|
|PF-6 AutomaticShutdown|新异常向原_launcher_body/launcher/外部停止wrapper传播，M.abort路径保持|PASS_STATIC，新增错误真实关闭UNRUN|
|PF-7 NoFalseCleanupSuccess|角色/组、internal_status、native、admin四轴；进程组空不覆盖内部UNKNOWN|PASS_STATIC，部分身份未知时拒绝确认|
|PF-8 AdministrativeFinalization|固定Root源引导、隔离argv、模块origin；主机受控装载5项|CONDITIONAL_PASS，Native导入与IO待验|
|PF-9 EvidenceIntegrity|post仅写当前control；原生对象只读；回执/boot绑定、manifest/ZIP双重SHA|PASS_STATIC，源/历史摘要另核|
|PF-10 NoReactivation|原claim/exclusive intent/T0/counter核心保持；CLOSED/STOP支配及writer身份|PASS_STATIC，回归实际UNRUN|

原guard的_launcher_body、协调器、external_stop异常路径维持M.abort，停止、回收及seal调用不更换。新增PF48缺件、未检出或越界时抛关键错误并进入同一wrapper。新增锁在异常中finally解锁，IO部分发布保持原件；稳定非法状态获得锁后立即拒绝。terminal_inspection仅用于关闭后只读适用性审查，没有工作发放能力。

历史batch11确实自动STOP/CLOSED、child waitpid125、父stop_exit0及角色/组空，额外兜底0；早期内部UNKNOWN原件保留，后续按冻结角色证据收敛。该事实作为历史记录，无法直接给新版本动态PASS。旧native封存成功44/45及自动post失败均保持。

[静态断言及源码行](evidence/SYNTAX_AND_CONTROL_FLOW_CHECK.json) · [13文件/57成员保持](evidence/PROTECTED_SEMANTICS_CHECK.json) · [补充身份审查](evidence/FINAL_REVIEW_SUPPLEMENT.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原安全、条件结论及强G覆盖裁决保持。
