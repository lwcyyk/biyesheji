# 完整版本集成与首次静态阻断

Material Passport：DCL-R6-FullChain-B；2026-11-13（Asia/Shanghai）；审查基线 RuntimeAdapt-static-1/r1 / ra01；仅主机静态审查；BLOCKED_STATIC_ADMISSION。


现有源码字节与最终锁一致。功能模块和调用关系已经接线；完整运行的输出规模与最小运行封存合同存在冲突。

|既有修复|当前实际文件及调用点|静态结论|
|---|---|---|
|BootContinuity|boot_continuity.entry→launcher；同Root父进程内部一次resume；guard_admission/child_admission/before_seal|已集成|
|RootIPC|guard.root_checkpoint→root_ipc.checkpoint；Root固定路径/权限/发布/等待|已集成；现绑定batch14|
|C09Fix|guard.launch_one(C09)→sender_prepare→真实exit23；协调者waitpid与交接验证|已集成|
|C00Ready|guard.launch_one(C00/C10)→service_readiness.wait_native与ticket_admit|已集成|
|ManagerRecovery r5|guard._launcher_work→prepay/MR64；恢复调用M.resume；M.formal_gate|已集成；原生异常诊断仅另一scope可达|
|PreT0 r3|P.enter→initial_query_scope/health→qualify→begin_runtime→runtime_ready→arm|已集成|
|PT/PF r3|startup_lifecycle阶段锁/检查点/post_exit_export；PF48|已集成；行政文件cap256与完整链冲突|
|TerminalRead r1|guard.seal→read_terminal_evidence(NATIVE_SEAL)；终态成员上限257|已集成；完整链成员规模冲突|
|RuntimeAdapt r1|manifest/prelaunch/postexec/own-map/native/admin检查；RA32|已集成；来源条件继续保留|
|B09 AdmissionFix r1|root_verify_safety→ledger_gate.require_current；门18→ledger异常聚合→独立oracle|已集成|

首次确认的阻断FC-S01：完整scope在C00后依次保存PT64/PF48/TR40/RA32/READY64/MR64的独立文件，共312个；startup_lifecycle.py:496–503遍历全部运行目录，256份上限在成功轨迹下必被越过。仅原始case文件就超出56份，辅助材料与后续测试尚未计入。

FC-S02：guard.py:1019–1026将上述全部原件放入native ZIP并添加manifest；最低313个成员。terminal_evidence.py:158要求成员≤257，最低超出56个。ZIP创建和终态独立接受是两个环节；本轮只证明后者与完整规模冲突，实际ZIP生成保持UNRUN。

FC-S03：完整scope缺少本次第7.4节要求的原生异常关闭验收路径。MR64通过进程内Subject改变布尔状态，其origin明确为MR-SIMULATION/1。原生fault78诊断受MR_RECOVERY_DIAGNOSTIC_ONLY分支限制，随后永久关闭，无法在同一完整scope内形成该项验收并继续S34/模型。

最小差异范围：完整链封存容量合同及其读取/导出守卫；原生异常路径的独立执行清单/计费/停止与验收边界。调整这些内容属于下一轮静态修复工作。本轮保留全部冻结字节，动态启动0。

[312条静态路径证据](evidence/SEAL_CAPACITY_STATIC_WITNESS.json) · [源码行摘录](evidence/SOURCE_EXCERPTS.json) · [原生覆盖分析](evidence/NATIVE_ANOMALY_COVERAGE.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
