# batch05 S1–S9 资格测试结果

Material Passport：DCL-R6-batch05；C09Fix-static-1/r1；真实执行后证据分析；2026-11-11；复跑 0。

计划 34 项；实际尝试 0、完成 0、通过 0、变异检出 0。C09 入口首次关键失败使 RANGE 前置条件缺失，S1–S9 结果全部为 UNRUN_RESOURCE_GATE。此前静态夹具完整性与 batch04 结果均保留各自范围。

|冻结 job|性质|variant|故障点|实际结果|
|---|---|---|---|---|
|S1.before.safe|S1|safe|before_reserve|UNRUN_RESOURCE_GATE|
|S1.before.mutant|S1|mutant|before_reserve|UNRUN_RESOURCE_GATE|
|S2.unsynced.safe|S2|safe|prepared.after_write|UNRUN_RESOURCE_GATE|
|S2.unsynced.mutant|S2|mutant|prepared.after_write|UNRUN_RESOURCE_GATE|
|S2.confirmed.safe|S2|safe|prepared.after_dirsync|UNRUN_RESOURCE_GATE|
|S2.confirmed.mutant|S2|mutant|prepared.after_dirsync|UNRUN_RESOURCE_GATE|
|S2.unknown.safe|S2|safe|prepared.file.sync_return_unobserved|UNRUN_RESOURCE_GATE|
|S2.unknown.mutant|S2|mutant|prepared.file.sync_return_unobserved|UNRUN_RESOURCE_GATE|
|S3.committed.safe|S3|safe|committed.after_dirsync|UNRUN_RESOURCE_GATE|
|S3.committed.mutant|S3|mutant|committed.after_dirsync|UNRUN_RESOURCE_GATE|
|S4.claimed.safe|S4|safe|partial.after_semantic|UNRUN_RESOURCE_GATE|
|S4.claimed.mutant|S4|mutant|partial.after_semantic|UNRUN_RESOURCE_GATE|
|S5.same.safe|S5|safe|None|UNRUN_RESOURCE_GATE|
|S5.same.mutant|S5|mutant|None|UNRUN_RESOURCE_GATE|
|S5.conflict.safe|S5|safe|None|UNRUN_RESOURCE_GATE|
|S5.conflict.mutant|S5|mutant|None|UNRUN_RESOURCE_GATE|
|S6.concurrent.safe|S6|safe|None|UNRUN_RESOURCE_GATE|
|S6.concurrent.mutant|S6|mutant|None|UNRUN_RESOURCE_GATE|
|S7.short.safe|S7|safe|prepared.before_write|UNRUN_RESOURCE_GATE|
|S7.short.mutant|S7|mutant|prepared.before_write|UNRUN_RESOURCE_GATE|
|S7.fsync.safe|S7|safe|journal_prepared.before_fsync|UNRUN_RESOURCE_GATE|
|S7.fsync.mutant|S7|mutant|journal_prepared.before_fsync|UNRUN_RESOURCE_GATE|
|S8.closed.safe|S8|safe|None|UNRUN_RESOURCE_GATE|
|S8.closed.mutant|S8|mutant|None|UNRUN_RESOURCE_GATE|
|S8.expired.safe|S8|safe|None|UNRUN_RESOURCE_GATE|
|S8.expired.mutant|S8|mutant|None|UNRUN_RESOURCE_GATE|
|S8.boot.safe|S8|safe|None|UNRUN_RESOURCE_GATE|
|S8.boot.mutant|S8|mutant|None|UNRUN_RESOURCE_GATE|
|S8.lock.safe|S8|safe|None|UNRUN_RESOURCE_GATE|
|S8.lock.mutant|S8|mutant|None|UNRUN_RESOURCE_GATE|
|S8.restart.safe|S8|safe|None|UNRUN_RESOURCE_GATE|
|S8.restart.mutant|S8|mutant|None|UNRUN_RESOURCE_GATE|
|S9.exhausted.safe|S9|safe|None|UNRUN_RESOURCE_GATE|
|S9.exhausted.mutant|S9|mutant|None|UNRUN_RESOURCE_GATE|

S1–S9 的独立 Root 原始重算与 RANGE_QUALIFICATION 均未执行/生成。主账内容审计仅针对已发生的 303 笔事务，尚未形成这些崩溃、幂等、并发、持久化故障、关闭与 N+1 路径的动态资格。后续审查应覆盖全部特权全局记账路径，因为 C09H 的 intent 所有权缺陷可能同样影响 Root S/gate 审查。

[冻结 S 合同](evidence/safety_contract.json)、[实际状态](evidence/ACTUAL_RESULTS.json)、[首次失败](BATCH05_COUNTEREXAMPLES.md)。
