# 启动连续性40项正反夹具与独立oracle

Material Passport：BootContinuity-static-1/r4；host离线静态修复；2026-11-11；WSL查询/目标执行0。

40项＝20个基础场景＋10个变异对照＋10个mutant；当前实际执行0。[boot_continuity_regression.py:8 Kernel](<../../../DCL-R6-isolated-verification/bc01/src/boot_continuity_regression.py>)为显式模拟内核：reboot递增epoch，旧进程死亡、cap/manager活动状态失效；持久静态对象、旧预算和CLOSED保留。新actor必须fresh检查，模拟PID/start_ticks复用仍受boot约束。身份/资源/静态漂移包含具体UID/GID/cgroup、tasks_max和对象摘要值。

每job初态、完整事件、当前模拟状态来源、预期末态/激活数、允许违规集及必须保存证据在[冻结合同](evidence/boot_contract.json)。生产eligibility/ticket_policy/service_policy被fixture实际调用；指定错误行为仅存在合成subject，不改真实boot、预算或系统对象。错误ticket通过“重新构造带错误绑定的对象”注入，未声称改写真实sealed fd。

|case|事件序列|variant|期望末态或违规|允许违规集|actual|
|---|---|---|---|---|---|
|P.same_boot|inspect → prepare → final → issue → exec → initialize_window → service_active|safe|STARTED|∅|UNRUN|
|P.cache_refresh|static_cache → reboot → new_process → inspect → prepare → final → issue → exec → initialize_window → service_active|safe|STARTED|∅|UNRUN|
|P.after_first|inspect → reboot → new_process → prepare → final → issue → exec|safe|REJECTED|∅|UNRUN|
|P.during_prepare|inspect → prepare → reboot → new_process → final → issue → exec|safe|REJECTED|∅|UNRUN|
|P.after_final|inspect → prepare → final → reboot → new_process → issue → exec|safe|REJECTED|∅|UNRUN|
|P.during_exec|inspect → prepare → final → issue → reboot → new_process → exec|safe|REJECTED|∅|UNRUN|
|P.old_receipt|inspect → prepare → final → issue → reboot → recycle_owner → reload_old_cap → exec|safe|REJECTED|∅|UNRUN|
|P.duplicate|inspect → prepare → final → issue → exec → exec|safe|REJECTED|∅|UNRUN|
|P.request_only|inspect → prepare → final → issue → exec → request_ok → confirm|safe|REJECTED|∅|UNRUN|
|P.launcher_exit|inspect → prepare → final → issue → exec → launcher_exit → confirm|safe|REJECTED|∅|UNRUN|
|P.orchestrator_exit|inspect → prepare → final → issue → orchestrator_exit → exec|safe|REJECTED|∅|UNRUN|
|P.stop|inspect → prepare → stop → final → issue → exec|safe|REJECTED|∅|UNRUN|
|P.bad_batch|inspect → prepare → final → issue → bad_batch → exec|safe|REJECTED|∅|UNRUN|
|P.bad_lock|inspect → prepare → final → issue → bad_lock → exec|safe|REJECTED|∅|UNRUN|
|P.closed|prior_closed → inspect → prepare → final → issue → exec|safe|REJECTED|∅|UNRUN|
|P.resources|inspect → prepare → final → issue → resources_change → exec|safe|REJECTED|∅|UNRUN|
|P.identity|inspect → prepare → final → issue → identity_change → exec|safe|REJECTED|∅|UNRUN|
|P.cache_invalid|static_cache → cache_rule_change → inspect → prepare → final → issue → exec → initialize_window → service_active|safe|STARTED|∅|UNRUN|
|P.artifact_drift|static_cache → artifact_drift → inspect → prepare → final → issue → exec|safe|REJECTED|∅|UNRUN|
|P.old_window|prior_window → reboot → new_process → inspect → prepare → final → issue → exec|safe|REJECTED|∅|UNRUN|
|M.epoch.safe|inspect → prepare → final → issue → reboot → recycle_owner → reload_old_cap → exec|safe|REJECTED|∅|UNRUN|
|M.epoch.mutant|inspect → prepare → final → issue → reboot → recycle_owner → reload_old_cap → exec|mutant|BC-1|BC-1,BC-3|UNRUN|
|M.snapshot.safe|inspect → prepare → final → issue → reboot → new_process → exec|safe|REJECTED|∅|UNRUN|
|M.snapshot.mutant|inspect → prepare → final → issue → reboot → new_process → exec|mutant|BC-3|BC-1,BC-3,BC-8|UNRUN|
|M.duplicate.safe|inspect → prepare → final → issue → exec → exec|safe|REJECTED|∅|UNRUN|
|M.duplicate.mutant|inspect → prepare → final → issue → exec → exec|mutant|BC-4|BC-4|UNRUN|
|M.request.safe|inspect → prepare → final → issue → exec → request_ok → confirm|safe|REJECTED|∅|UNRUN|
|M.request.mutant|inspect → prepare → final → issue → exec → request_ok → confirm|mutant|BC-7|BC-7|UNRUN|
|M.closed.safe|prior_closed → inspect → prepare → final → issue → exec|safe|REJECTED|∅|UNRUN|
|M.closed.mutant|prior_closed → inspect → prepare → final → issue → exec|mutant|BC-5|BC-3,BC-5|UNRUN|
|M.budget.safe|prior_window → reboot → new_process → inspect → prepare → final → issue → exec|safe|REJECTED|∅|UNRUN|
|M.budget.mutant|prior_window → reboot → new_process → inspect → prepare → final → issue → exec|mutant|BC-6|BC-6|UNRUN|
|M.binding.safe|inspect → prepare → final → issue → bad_lock → exec|safe|REJECTED|∅|UNRUN|
|M.binding.mutant|inspect → prepare → final → issue → bad_lock → exec|mutant|BC-3|BC-3|UNRUN|
|M.resources.safe|inspect → prepare → final → issue → resources_change → exec|safe|REJECTED|∅|UNRUN|
|M.resources.mutant|inspect → prepare → final → issue → resources_change → exec|mutant|BC-2|BC-2,BC-5|UNRUN|
|M.identity.safe|inspect → prepare → final → issue → identity_change → exec|safe|REJECTED|∅|UNRUN|
|M.identity.mutant|inspect → prepare → final → issue → identity_change → exec|mutant|BC-8|BC-8|UNRUN|
|M.cache.safe|static_cache → artifact_drift → inspect → prepare → final → issue → exec|safe|REJECTED|∅|UNRUN|
|M.cache.mutant|static_cache → artifact_drift → inspect → prepare → final → issue → exec|mutant|BC-2|BC-2,BC-3,BC-5|UNRUN|

独立oracle不导入Guard、生产gate、模拟subject或业务后继；从冻结事件重建epoch/存活、manager代次、权限、资源和静态对象真值，再核实际决策、认领数、service事实和原账单调。原始记录Root:Root/0600，包含当前真实运行binding/actor/时钟/访问占用，模拟字段另标SIMULATED_RESTART/1。物理WSL重启、实际exec fd继承及真实服务启动仍是独立动态责任。

每job最多10个事件，保守预付11次（语义步及即时oracle），另付整套Root重算1次；entry1＋40×12=481，硬限512，不退款。与C09H/RootIPC同一5000硬额、同一T0/300秒校准窗，额外进程0。未命中变异、缺原件、额外违规、错误绑定、超限或意外错误均阻断；首个失败即保存并停止。

需要真实平台重新启动诊断时必须另取许可。本轮这些测试未运行；输入中的“reboot”仅定义模型状态变换，绝不发出wsl shutdown/terminate。
