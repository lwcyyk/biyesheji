# TR-A2证据索引

Material Passport：DCL-R6-TR-A2；batch14-r1；RuntimeAdapt-static-1/r1；2026-11-13（Asia/Shanghai）；冻结入口1次、源码修改/测试重跑0。

|主题|工件|
|---|---|
|裁决|[TRA2_FINAL_DECISION](TRA2_FINAL_DECISION.md)、[全量实际JSON](evidence/ACTUAL_RESULTS.json)|
|授权/锁|[用户原文](evidence/TASK_REQUEST.txt)、[回执](evidence/execution_authorization.json)、[绑定](evidence/AUTHORIZATION_RECEIPT_LOCK.json)、[64项准入](evidence/SOURCE_AND_SCOPE_ADMISSION.json)|
|运行时/兼容|[实际Root/Payload身份回执](evidence/RUNTIME_IDENTITY_RECEIPTS.json)、[C00八项](evidence/C00_READINESS_SUMMARY.json)|
|四套184项|[原input/trace/hash/oracle/预算/时间范围](evidence/TEST_CASE_RESULTS.json)|
|终态/守卫|[关键原件摘要不变与实际拒绝](evidence/TERMINAL_READ_CONSERVATION_AUDIT.json)|
|预算|[3133事务/6266行独立审计](evidence/BUDGET_AUDIT.json)|
|Native|[233/234逐流核验](evidence/NATIVE_SEAL_VERIFICATION.json)|
|自动行政|[原计划](evidence/STARTUP_POSTEXIT_PLAN.json)、[原结果](evidence/STARTUP_FINALIZATION.json)、[249/250核验](evidence/AUTOMATIC_ADMIN_VERIFICATION.json)|
|时间/退出|[时间线](evidence/EXECUTION_TIMELINE.json)、[journal原文](evidence/RUN_BOOT_JOURNAL.stdout.raw)、[消息索引](evidence/JOURNAL_MESSAGE_INDEX.json)、[退出后审计](evidence/POSTRUN_AUDIT.json)|
|原件和源码|[235 Native导出锁](evidence/NATIVE_EXPORT_LOCK.json)、[64源导出锁](evidence/FROZEN_SOURCE_EXPORT_LOCK.json)、[源后核](evidence/SOURCE_AFTER_CHECK.json)|
|历史/交付|[旧包](evidence/HISTORICAL_ARCHIVE_CHECK.json)、[8605基线](evidence/BASELINE_LOCK.json)、[历史保持](evidence/HISTORY_PROTECTION_CHECK.json)、[交付核验](evidence/DELIVERY_CHECK.json)|

完整原件D:/毕业设计/DCL-R6-isolated-verification/batch14/native_snapshot、FROZEN_RA；最终研究ZIP对应export/native和export/frozen。自动Native/行政包保持原名及真实hash，研究包只汇总。能力nonce保留私有原件/本地包，不在报告展开。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2安全与原创性裁决保持。
