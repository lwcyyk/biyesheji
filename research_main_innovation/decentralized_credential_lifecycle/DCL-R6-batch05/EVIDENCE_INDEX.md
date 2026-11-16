# batch05 研究证据索引

Material Passport：DCL-R6-batch05；C09Fix-static-1/r1；真实执行后证据分析；2026-11-11；复跑 0。

本索引串联真实运行与本轮封存报告。资源资格=FAILED；模型状态=UNRUN_RESOURCE_GATE；行政核对与实验裁决分列。

## 报告

|材料|范围|
|---|---|
|[BATCH05_AUTHORIZATION_AND_LOCK.md](<BATCH05_AUTHORIZATION_AND_LOCK.md>)|授权、预检、源/运行时/argv锁|
|[BATCH05_ROOT_COORDINATOR_RESULTS.md](<BATCH05_ROOT_COORDINATOR_RESULTS.md>)|Root外部TCB与实际退出延迟|
|[BATCH05_C09_HANDOFF_RESULTS.md](<BATCH05_C09_HANDOFF_RESULTS.md>)|真实交接NOT_EXERCISED|
|[BATCH05_C09_REGRESSION_RESULTS.md](<BATCH05_C09_REGRESSION_RESULTS.md>)|34合成回归及6变异命中|
|[BATCH05_RESOURCE_CALIBRATION.md](<BATCH05_RESOURCE_CALIBRATION.md>)|C00–C08/C09与C02局部数据|
|[BATCH05_S1_S9_RESULTS.md](<BATCH05_S1_S9_RESULTS.md>)|34项逐项未运行|
|[BATCH05_GATE_NEGATIVE_RESULTS.md](<BATCH05_GATE_NEGATIVE_RESULTS.md>)|17项逐项未运行|
|[BATCH05_RESOURCE_ACCOUNTING.md](<BATCH05_RESOURCE_ACCOUNTING.md>)|37,293账、内存与时间范围|
|[BATCH05_F1_RESULTS.md](<BATCH05_F1_RESULTS.md>)|F1未运行|
|[BATCH05_F4_RESULTS.md](<BATCH05_F4_RESULTS.md>)|F4未运行|
|[BATCH05_COUNTEREXAMPLES.md](<BATCH05_COUNTEREXAMPLES.md>)|权限与闭合响应缺陷|
|[BATCH05_FINAL_DECISION.md](<BATCH05_FINAL_DECISION.md>)|四轴裁决|

## 原始来源与独立核对

[SOURCE_INDEX](SOURCE_INDEX.json)列出全部源/输入/native字节映射；[命令摘要](COMMAND_SUMMARY.md)链接31条精确argv与原始双流；[原始执行计划](evidence/COMMAND_PLAN.json)保留每次启动前登记。

[Root C09H资格原件](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/inputs/C09H_QUALIFICATION.json>)、[34项原始事件目录](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests>)、[停止器身份](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/inputs/STOP_ARMED.json>)、[首次权限错误](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/STOP_REQUEST.json>)、[原闭合记录](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/inputs/CLOSED.json>)。

[独立预算核算](evidence/BUDGET_AUDIT.json)、[首次失败](evidence/FIRST_FAILURE.json)、[时间线](evidence/RUNTIME_TIMELINE.json)、[资源观察](evidence/RESOURCE_OBSERVATIONS.json)、[原始权限](evidence/commands/26.result.json)、[运行boot最终journal](evidence/commands/31.stdout.raw)。

原始waitpid/pidfd交接见证、ACK、commit/receiver确认在本批未生成；其缺失属于实验结果。socket保存[类型/身份锁](evidence/NATIVE_EXPORT_LOCK.json)，常规文件347份；冻结代码副本37份。最终Root异常清理确实自动seal，[native ZIP](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/EVIDENCE.zip>)逐流核对346项，详情[NATIVE_ZIP_CHECK](evidence/NATIVE_ZIP_CHECK.json)。

[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)保留旧账、误副本及先前策略拒绝；旧batch04/GC/C09Fix的研究结果及原件字节保持。Root四导航文件在新结果前保存完整旧字节快照。封存索引[OUTPUT_MANIFEST](OUTPUT_MANIFEST.json)、审阅包[BATCH05_EVIDENCE.zip](BATCH05_EVIDENCE.zip)、[DELIVERY_CHECK](evidence/DELIVERY_CHECK.json)分开记录。

Manifest覆盖本轮研究材料、四份当前导航、347 native文件及37 frozen文件，排除manifest自身、交付检查和最终ZIP避免自引用；交付检查单独记录manifest与ZIP的SHA-256。审阅包以research/navigation/native/FROZEN_C09组织，manifest记录每个archive_path。行政核对只证明所列字节与本批导出锁一致，外部研究者实际重跑0、文件系统持久化及可信Root假设仍保持原条件。
