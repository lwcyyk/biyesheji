# 阶段漂移根因与证据强度

Material Passport：PTA-PhaseFinalizer-static-1/r3；DCL-R6-PTA-PhaseFinalizer-Fix；2026-11-12；HOST_STATIC_ONLY。

**源码中的跨文件一致性缺陷已由具体合法交错证明。历史抛错瞬间的操作数缺少记录，精确历史根因保留PT_RUNTIME_PHASE_DRIFT_ROOT_CAUSE_UNRESOLVED；PF-G1=PARTIAL。**

|必须恢复的字段|证据支持的结论|
|---|---|
|产生错误的函数|旧startup_lifecycle.runtime_checkpoint，第184行|
|失败调用链|Root停止服务892 → guard._external_stop_impl:777 → Receiver.poll:207 → G.root_checkpoint:138 → P.runtime_checkpoint:184|
|调用时阶段|正常初始化已推进到ARMED发布附近；精确读取瞬间阶段值UNKNOWN|
|检查器期望|条件要求sha(runtime intent)==q.initialization_id且私有phase.phase==q.phase；q读值未逐次记录|
|实际观测操作数|q.phase、当次private.phase及该次digest比较结果均UNKNOWN；组合OR异常没有区分分支|
|持久位置|inputs/root_private/boot/pt_phase.json、pt_events.jsonl；inputs/PT_RUNTIME_CHECKPOINT.json；pt_runtime_intent.json|
|更新者|Launcher child887/start6672，boot24fc4fce-f68c-4ab5-8662-261ed17d831b|
|核验者|独立停止服务892/start6693，同boot；其Receiver在没有收到C09请求时也轮询运行点|
|持久顺序|_set_phase持锁写events/私有phase并释放；之后单独读取/发布公开q；reader没有共同锁|
|运行对象一致性|最终原件T0=66.896850269、R=0、COMMITTED after0；公开/私有均ARMED、sequence5，intent digest匹配；这些是封存时快照|

源码反例输入是同批、同boot、同intent的READY→ARMED转换，调度如下：reader取公开READY/4；writer持久化私有ARMED/5；reader比较旧q与新私有phase并抛错；writer发布公开ARMED/5。所有写入都遵守旧状态机。此四步是SOURCE_SCHEDULE_WITNESS_ONLY，本轮没有执行重放。它证明旧程序存在合法转换被错误拒绝的输入调度。

|情况|裁决|
|---|---|
|A 合法转换未完成|源码顺序允许；原始记录与此相容，精确发生情况UNKNOWN|
|B 跨时刻拼接/旧快照|源码确定存在该读取风险；历史精确交错UNKNOWN|
|C 真实非法转换|持久phase链未显示回退或跳转；历史瞬时损坏或组合条件另一分支缺少排除证据|

本轮修复已证明存在的源码一致性缺口，并为新版本异常增加公开/私有phase、sequence及digest比较布尔值，供下一批定位。保持旧首错槽位和旧报告原文；本轮对证据强度的精化单独登记。

[恢复事实和原件SHA](evidence/HISTORICAL_FAILURE_FACTS.json) · [源码diff](evidence/FULL_DIFF.patch) · [时间线](PHASE_TRANSITION_TIMELINE.md)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原安全、条件结论及强G覆盖裁决保持。
