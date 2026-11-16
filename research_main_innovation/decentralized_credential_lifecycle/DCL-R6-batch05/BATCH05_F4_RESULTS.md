# batch05 F4 有界检查结果

Material Passport：DCL-R6-batch05；C09Fix-static-1/r1；真实执行后证据分析；2026-11-11；复跑 0。

实际状态：**UNRUN_RESOURCE_GATE**。RESOURCE_GATE_PASS 尚未取得；FORMAL unit/模型搜索均未启动。实际搜索0、语义状态访问0；无本批有限域完整性、覆盖或反例搜索结果。

|冻结范围|本批实际|
|---|---|
|COST1|UNRUN_RESOURCE_GATE|
|CE5/其他冻结夹具|UNRUN_RESOURCE_GATE|
|D2-DP|UNRUN_RESOURCE_GATE|
|TRACE-REF|UNRUN_RESOURCE_GATE|
|压缩开关对照|UNRUN_RESOURCE_GATE|
|G64|UNRUN_RESOURCE_GATE|
|规定 mutants|UNRUN_RESOURCE_GATE|
|反例重放|UNRUN_RESOURCE_GATE|

PASS_BOUNDED 授予0；模型反例数量为“未搜索”，通过率及状态空间规模保持待测量。独立参考与候选后继/终态判定隔离的原要求保持；本批尚无动态对照数据。 原模型和输入摘要均在启动前冻结范围内；本批修改0。

本批故障属于资源监督/权限实现，模型级性质裁决继续保留历史条件。D1-PBFT-SEAL/1.1、强G覆盖、严格分离实例0和IMPLEMENTATION_GATE=CLOSED保持。

[冻结执行锁](evidence/execution_lock.json)、[实际结果](evidence/ACTUAL_RESULTS.json)、[阻断原因](BATCH05_COUNTEREXAMPLES.md)。
