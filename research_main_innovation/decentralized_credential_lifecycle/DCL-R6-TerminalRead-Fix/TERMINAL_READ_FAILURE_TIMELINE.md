# 终态读取失败的真实事件链

Material Passport：DCL-R6-TerminalRead-Fix；TerminalRead-static-1/r1；2026-11-13（Asia/Shanghai）；HOST_STATIC_ONLY。

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

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原条件结论与原创性裁决保持。
