# CLOSED后活动态拒绝与权限边界

Material Passport：DCL-R6-TR-A2；batch14-r1；RuntimeAdapt-static-1/r1；2026-11-13（Asia/Shanghai）；冻结入口1次、源码修改/测试重跑0。

**真实活动接口拒绝已取得，TR-D2=CONDITIONAL_PASS，范围边界分别保留。**

只读返回后，冻结caller执行check_active_runtime→原G.root_checkpoint，实际抛IPC_CLOSED_DOMINATES，sample102.255073341；原异常码和读取者身份保存。CLOSED在102.107384106已持久化，该拒绝没有发放工作或修改预算。

terminal decision中work_allowed/budget_init_allowed/phase_write_allowed/launcher_allowed全false，runtime_authority=NONE；原G.state/预算/一次认领/phase保护代码保持。TR40与PT/PF/RA模型覆盖闭态预算重建、信用、状态恢复、身份/损坏等拒绝。

主实例未在CLOSED后直接调用真实Budget初始化/预留、Launcher重启或真实WORK写入制造破坏；这些实际写路径的强行负向执行保持未覆盖。实际健康/RootIPC拒绝与合成权限模型分开，保持条件性结论。

[实际拒绝与不变性](evidence/TERMINAL_READ_CONSERVATION_AUDIT.json) · [TR40/其他合成结果](evidence/TEST_CASE_RESULTS.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2安全与原创性裁决保持。
