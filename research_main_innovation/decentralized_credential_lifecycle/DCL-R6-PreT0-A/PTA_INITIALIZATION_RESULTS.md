# 真实预窗与初始化结果

Material Passport：DCL-R6-PreT0-A；batch11；PreT0Recovery-static-1/r3；NORMAL_START；2026-11-12（Asia/Shanghai）；实际入口1次，重跑0，源码修复0。

**正常预窗认证已通过，真实初始化推进到RUNTIME_ARMED；首次工作发放前停止。** 本轮没有重现IPC_STATE_MISSING。

|实际阶段|BOOTTIME秒|原始见证|
|---|---:|---|
|启动TCB起点|65.510243359|sealed preflight_deadline−120|
|Native预检qualified|66.403873152|原始stdout的PREFLIGHT_QUALIFIED|
|same-PID入口验证|66.715489008|ENTRY_VERIFIED；Owner仍827/start6546|
|PRE_WINDOW|66.811319376|pt_events序号0，Root保护ctx已建立|
|PREFLIGHT_VALIDATING|66.820658042|序号1；仅认证预窗query scope|
|初始manager健康通过|66.870763982|两次实际query返回0，failed仅mnt-e.mount|
|PREFLIGHT_QUALIFIED|66.874374079|序号2|
|runtime intent采样|66.885179620|独占pt_runtime_intent，当前boot/源/授权绑定|
|RUNTIME_INITIALIZING|66.888638365|序号3，intent已持久化|
|真实T0|66.896850269|batch_state中的真实时钟值|
|RUNTIME_READY|66.914956317|序号4，state/counter/COMMITTED intent已核验|
|RUNTIME_ARMED|67.109909234|序号5；STOP_ARMED已存在，父TasksMax检查通过|
|公开armed检查点采样|67.118473361|PT_RUNTIME_CHECKPOINT.phase=RUNTIME_ARMED|

ctx中的T0/R仍为null，正确表达预窗快照；真实batch_state和预算随后独立建立。窗口deadline=1866.896850269、stop_at=1806.896850269；未重置。初始化intent的hash与公开检查点initialization_id一致，phase链previous_sha256逐项一致。RUNNING没有发生，C00未发放。

预窗health走专用scope并取得真实成功，这为旧循环依赖的拆分提供本次正向证据。严格运行检查点在state/counter建立后被调用，随后暴露跨文件phase快照竞态。运行损坏拒绝、关闭重入和所有故障分支的动态覆盖仍待PT64实际运行。

[实际结果](evidence/ACTUAL_RESULTS.json) · [时序原件索引](evidence/EXECUTION_TIMELINE.json) · [首次反例](PTA_COUNTEREXAMPLES.md)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原条件结论与强G覆盖裁决保持。
