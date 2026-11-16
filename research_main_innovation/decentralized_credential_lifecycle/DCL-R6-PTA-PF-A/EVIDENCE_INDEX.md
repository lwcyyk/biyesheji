# 阶段A证据索引

Material Passport：DCL-R6-PTA-PF-A；batch12-r3；PTA-PhaseFinalizer-static-1/r3；NORMAL_START；2026-11-12（Asia/Shanghai）；冻结入口1次，源码修改/测试重跑0。

|主题|工件|
|---|---|
|总裁决/21问|[PFA_FINAL_DECISION](PFA_FINAL_DECISION.md)|
|授权/准入|[原文](evidence/TASK_REQUEST.txt)、[回执锁](evidence/AUTHORIZATION_RECEIPT_LOCK.json)、[范围/55项锁](evidence/SOURCE_AND_SCOPE_ADMISSION.json)、[资源界](evidence/RESOURCE_ADMISSION_PROOF.json)|
|部署/原生预检|[53项部署](evidence/DEPLOYMENT_RESULT.json)、[环境](evidence/ENVIRONMENT_AUDIT.json)、[active stdout](evidence/windows_entry.stdout.raw)|
|实际全量结果|[ACTUAL_RESULTS](evidence/ACTUAL_RESULTS.json)、[字段/UNKNOWN](evidence/FIELD_MAPPING_AND_UNKNOWN.json)、[phase及锁](evidence/LOCK_AND_PHASE_EVIDENCE.json)|
|C00|[八项比较](evidence/C00_READINESS_SUMMARY.json)|
|PT64/PF48|[112项input/状态/oracle/hash/预算/时间细目](evidence/TEST_CASE_RESULTS.json)|
|预算|[1907事务独立结构审计](evidence/BUDGET_AUDIT.json)|
|自动行政|[原计划](evidence/STARTUP_POSTEXIT_PLAN.json)、[原结果](evidence/STARTUP_FINALIZATION.json)、[逐流校验](evidence/AUTOMATIC_ADMIN_VERIFICATION.json)|
|原生封存|[缺口/原分类](evidence/NATIVE_SEAL_GAP.json)|
|时间/退出|[时间线](evidence/EXECUTION_TIMELINE.json)、[journal消息](evidence/JOURNAL_MESSAGE_INDEX.json)、[完整原journal](evidence/RUN_BOOT_JOURNAL.stdout.raw)|
|完整原件|[157 Native导出锁](evidence/NATIVE_EXPORT_LOCK.json)、[55源导出锁](evidence/FROZEN_SOURCE_EXPORT_LOCK.json)、[退出后审计](evidence/POSTRUN_AUDIT.json)|
|源/历史|[执行后55项保持](evidence/SOURCE_AFTER_CHECK.json)、[历史包](evidence/HISTORICAL_ARCHIVE_CHECK.json)、[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)、[交付核验](evidence/DELIVERY_CHECK.json)|

完整157项Native原件和55项源位于D:/毕业设计/DCL-R6-isolated-verification/batch12/native_snapshot及FROZEN_PF；最终研究ZIP另纳入export/native与export/frozen成员。自动行政原包由冻结程序真实产生，保留在control及evidence/STARTUP_ADMIN_EVIDENCE.zip。能力nonce仅保留私有原件/本地归档，报告不展开。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原安全与原创性裁决保持。
