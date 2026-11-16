# 阶段A证据索引

Material Passport：DCL-R6-PreT0-A；batch11；PreT0Recovery-static-1/r3；NORMAL_START；2026-11-12（Asia/Shanghai）；实际入口1次，重跑0，源码修复0。

|主题|工件|
|---|---|
|总裁决|[十九项回答](PTA_FINAL_DECISION.md)|
|授权/版本|[授权及锁](PTA_AUTHORIZATION_AND_LOCK.md)、[原文](evidence/TASK_REQUEST.txt)、[回执](evidence/execution_authorization.json)|
|实际机器结果|[ACTUAL_RESULTS](evidence/ACTUAL_RESULTS.json)、[源码前置](evidence/SOURCE_AND_SCOPE_ADMISSION.json)、[源码后核](evidence/SOURCE_AFTER_CHECK.json)|
|预检部署|[部署](evidence/DEPLOYMENT_RESULT.json)、[平台](evidence/ENVIRONMENT_AUDIT.json)|
|精确入口|[调用](evidence/ACTIVE_ENTRY_INVOCATION.json)、[外层返回](evidence/ACTIVE_ENTRY_RETURN.json)、[active返回](evidence/WINDOWS_ENTRY_EXIT.json)|
|原始双流|[stdout](evidence/windows_entry.stdout.raw)、[stderr](evidence/windows_entry.stderr.raw)、[journal](evidence/RUN_BOOT_JOURNAL.stdout.raw)|
|自动收尾|[计划](evidence/STARTUP_POSTEXIT_PLAN.json)、[结果](evidence/STARTUP_FINALIZATION.json)、[stderr](evidence/STARTUP_POSTEXIT.stderr.raw)|
|原生封存|[逐流核验](evidence/NATIVE_SEAL_VERIFICATION.json)|
|进程退出|[首次审计](evidence/CLOSURE_AUDIT.json)、[完整导出审计](evidence/POSTRUN_AUDIT.json)|
|原件路径/元数据|[46项Native导出锁](evidence/NATIVE_EXPORT_LOCK.json)、[51项冻结源导出锁](evidence/FROZEN_SOURCE_EXPORT_LOCK.json)|
|时间/错误|[时间线](evidence/EXECUTION_TIMELINE.json)、[journal消息](evidence/JOURNAL_MESSAGE_INDEX.json)、[反例](PTA_COUNTEREXAMPLES.md)|
|历史/交付|[启动前基线](evidence/BASELINE_LOCK.json)、[旧归档](evidence/HISTORICAL_ARCHIVE_CHECK.json)、[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)、[交付核验](evidence/DELIVERY_CHECK.json)|

完整原生46项与冻结51项位于D:/毕业设计/DCL-R6-isolated-verification/batch11/native_snapshot及FROZEN_PT；研究最终ZIP同时纳入对应export/native与export/frozen成员，manifest按实际SHA绑定。能力nonce只在私有原件和归档中保留，报告不展开。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原条件结论与强G覆盖裁决保持。
