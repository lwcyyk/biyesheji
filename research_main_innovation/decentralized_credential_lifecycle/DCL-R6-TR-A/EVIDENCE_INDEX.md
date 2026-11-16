# TR-A证据索引

Material Passport：DCL-R6-TR-A；batch13-r1；TerminalRead-static-1/r1；2026-11-13（Asia/Shanghai）；冻结入口1次、退出125、源码修改/测试重跑0。

|主题|工件|
|---|---|
|20项回答|[TRA_FINAL_DECISION](TRA_FINAL_DECISION.md)|
|授权/锁|[原文](evidence/TASK_REQUEST.txt)、[回执锁](evidence/AUTHORIZATION_RECEIPT_LOCK.json)、[59项准入](evidence/SOURCE_AND_SCOPE_ADMISSION.json)|
|资源静态界|[预算重算](evidence/RESOURCE_ADMISSION_PROOF.json)|
|实际结果/首错|[ACTUAL_RESULTS](evidence/ACTUAL_RESULTS.json)、[FIRST_FAILURE](evidence/FIRST_FAILURE.json)|
|原始双流|[active stdout](evidence/windows_entry.stdout.raw)、[active stderr](evidence/windows_entry.stderr.raw)、[post stdout](evidence/STARTUP_POSTEXIT.stdout.raw)、[post stderr](evidence/STARTUP_POSTEXIT.stderr.raw)|
|调用时间|[active调用](evidence/ACTIVE_ENTRY_INVOCATION.json)、[active退出](evidence/WINDOWS_ENTRY_EXIT.json)、[时间线](evidence/EXECUTION_TIMELINE.json)|
|行政包|[原结果](evidence/STARTUP_FINALIZATION.json)、[14/15逐流验证](evidence/AUTOMATIC_ADMIN_VERIFICATION.json)|
|未执行项|[152项/25变异登记](evidence/UNRUN_CASE_REGISTER.json)|
|环境差异|[1241运行时核对/包日志](evidence/RUNTIME_DRIFT_AUDIT.json)、[3份实际文件导出锁](evidence/DRIFTED_RUNTIME_EXPORT_LOCK.json)|
|源码保持|[59项导出锁](evidence/FROZEN_SOURCE_EXPORT_LOCK.json)、[源后核](evidence/SOURCE_AFTER_CHECK.json)|
|历史/交付|[旧归档](evidence/HISTORICAL_ARCHIVE_CHECK.json)、[8017基线](evidence/BASELINE_LOCK.json)、[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)、[交付核验](evidence/DELIVERY_CHECK.json)|

Windows行政保存目录D:/毕业设计/DCL-R6-isolated-verification/batch13仅包含FROZEN_TR及preflight_runtime_snapshot，实际Linux /var/lib/dcl-r6/batch13不存在。最终研究包包含export/frozen与export/current-runtime成员，避免将主机保存目录解释为正式实例。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2安全与原创性结论保持。
