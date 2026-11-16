# batch05 17 项资格门负向检查

Material Passport：DCL-R6-batch05；C09Fix-static-1/r1；真实执行后证据分析；2026-11-11；复跑 0。

计划 17 项，实际执行 0，实际拒绝见证 0。当前批次因 C09 首次失败停止；17 项检查的有效拒绝能力仍待动态证据。源码拒绝规则和本批未调用的字段保持原锁。

|case|冻结构造|期望拒绝前缀|实际结果|
|---|---|---|---|
|gate.status.UNRUN|status|RANGE_REQUIRED_RESULT_|UNRUN_RESOURCE_GATE|
|gate.status.FAIL|status|RANGE_REQUIRED_RESULT_|UNRUN_RESOURCE_GATE|
|gate.status.INCONCLUSIVE|status|RANGE_REQUIRED_RESULT_|UNRUN_RESOURCE_GATE|
|gate.status.MUTATION_NOT_DETECTED|status|RANGE_REQUIRED_RESULT_|UNRUN_RESOURCE_GATE|
|gate.status.EVIDENCE_MISSING|status|RANGE_REQUIRED_RESULT_|UNRUN_RESOURCE_GATE|
|gate.status.HASH_MISMATCH|status|RANGE_REQUIRED_RESULT_|UNRUN_RESOURCE_GATE|
|gate.status.UNEXPECTED_RECOVERY|status|RANGE_REQUIRED_RESULT_|UNRUN_RESOURCE_GATE|
|gate.missing_job|missing_job|RANGE_RECEIPT_JOB_SET|UNRUN_RESOURCE_GATE|
|gate.missing_raw|missing_raw|RANGE_RAW_EVIDENCE_MISSING|UNRUN_RESOURCE_GATE|
|gate.raw_hash|raw_hash|RANGE_RAW_HASH_MISMATCH|UNRUN_RESOURCE_GATE|
|gate.binding.boot_id|binding|RANGE_RECEIPT_BINDING|UNRUN_RESOURCE_GATE|
|gate.binding.static_manifest_sha256|binding|RANGE_RECEIPT_BINDING|UNRUN_RESOURCE_GATE|
|gate.binding.fixture_contract_sha256|binding|RANGE_RECEIPT_BINDING|UNRUN_RESOURCE_GATE|
|gate.binding.execution_lock_sha256|binding|RANGE_RECEIPT_BINDING|UNRUN_RESOURCE_GATE|
|gate.binding.T0|binding|RANGE_RECEIPT_BINDING|UNRUN_RESOURCE_GATE|
|gate.checker_hash|checker_hash|RANGE_CHECKER_DRIFT|UNRUN_RESOURCE_GATE|
|gate.forged_PASS|forged_PASS|RANGE_RAW_EVIDENCE_MISSING|UNRUN_RESOURCE_GATE|

RESOURCE_GATE_PASS=NOT_OBTAINED。C09 入口 FAIL、真实交接 NOT_EXERCISED、C10–C12/S34/门17 UNRUN 均阻断资格。Root 全局账内容配对完整与行政封存核对通过分别保留其窄范围，无法补足测试链。

[合同](evidence/safety_contract.json)、[校准](BATCH05_RESOURCE_CALIBRATION.md)、[最终裁决](BATCH05_FINAL_DECISION.md)。
