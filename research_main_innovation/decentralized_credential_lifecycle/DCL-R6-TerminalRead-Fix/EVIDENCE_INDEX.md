# 终态读取证据索引

Material Passport：DCL-R6-TerminalRead-Fix；TerminalRead-static-1/r1；2026-11-13（Asia/Shanghai）；HOST_STATIC_ONLY。

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

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原条件结论与原创性裁决保持。
