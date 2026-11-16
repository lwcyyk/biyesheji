# 研究证据索引

Material Passport：PTA-PhaseFinalizer-static-1/r3；DCL-R6-PTA-PhaseFinalizer-Fix；2026-11-12；HOST_STATIC_ONLY。

|主题|工件|
|---|---|
|总裁决|[FINAL_DECISION](FINAL_DECISION.md)、[机器结果](evidence/STATIC_RESULT.json)|
|授权/边界|[用户原文](evidence/TASK_REQUEST.txt)、[实施门边界](SCOPE_BOUNDARY.md)|
|历史真实事实|[原始错误字段](evidence/HISTORICAL_FAILURE_FACTS.json)、evidence/PTA_ORIGINALS下23份逐字节原件副本|
|旧归档|[逐流核验](evidence/HISTORICAL_ARCHIVE_CHECK.json)|
|源码历史|evidence/SOURCE_BEFORE、SOURCE_FINAL_R1/R2/R3；[修订记录](evidence/REVISION_LOG.json)|
|最终锁/差异|[55项锁](evidence/STATIC_WORKSPACE_LOCK.json)、[diff](evidence/FULL_DIFF.patch)、[前后SHA](evidence/FILE_DIFF_INDEX.json)|
|静态控制流|[语法/28断言/行号](evidence/SYNTAX_AND_CONTROL_FLOW_CHECK.json)、[13文件/57成员](evidence/PROTECTED_SEMANTICS_CHECK.json)|
|导入|[AST关系图](evidence/IMPORT_GRAPH.json)、[最终受控探针](evidence/CONTROLLED_IMPORT_RESULTS.json)、[最终补充审查](evidence/FINAL_REVIEW_SUPPLEMENT.json)|
|回归/资源|[PF48/8静态矩阵](evidence/FIXTURE_ORACLE_STATIC_CHECK.json)、[资源重算](evidence/RESOURCE_BOUND_RECALCULATION.json)|
|下一授权|[未批准模板](evidence/PHASE_A_NORMAL_START_AUTHORIZATION_TEMPLATE.json)、[有限申请](NEXT_DYNAMIC_AUTHORIZATION.md)|
|历史/交付完整性|[基线](evidence/BASELINE_LOCK.json)、[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)、[最终交付](evidence/DELIVERY_CHECK.json)|

版本r1/r2的锁/检查结果和探针保留在evidence/versions及各自controlled_import_probes目录。最终只使用SOURCE_FINAL_R3与当前STATIC_WORKSPACE_LOCK。正式控制目录尚未建立，全部执行模板未批准。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原安全、条件结论及强G覆盖裁决保持。
