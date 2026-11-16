# batch07 17项资格门负向检查

Material Passport：DCL-R6-batch07；BootContinuity-static-1/r4；真实启动后首次失败；2026-11-11；复跑0。

计划17，实际尝试0、有效拒绝/检出0；Root gate审查及GATE_NEGATIVE_AUDIT未执行/生成。

|case|冻结recipe|期望拒绝|实际|
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

RESOURCE_GATE_PASS=NOT_OBTAINED。C00失败、其他C与40/56/34/S34/门17未运行均独立阻断FORMAL；bootstrap预检局部通过无法替代资源门。
