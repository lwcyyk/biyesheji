# batch05 F1 有界检查结果

Material Passport：DCL-R6-batch05；C09Fix-static-1/r1；真实执行后证据分析；2026-11-11；复跑 0。

实际状态：**UNRUN_RESOURCE_GATE**。RESOURCE_GATE_PASS 尚未取得；FORMAL unit/模型搜索均未启动。实际搜索0、语义状态访问0；无本批有限域完整性、覆盖或反例搜索结果。

|冻结范围|本批实际|
|---|---|
|SMOKE|UNRUN_RESOURCE_GATE|
|BRANCH|UNRUN_RESOURCE_GATE|
|CHAIN|UNRUN_RESOURCE_GATE|
|KEY|UNRUN_RESOURCE_GATE|
|规定 mutants|UNRUN_RESOURCE_GATE|
|反例重放|UNRUN_RESOURCE_GATE|
|INV1–INV8|UNRUN_RESOURCE_GATE|

PASS_BOUNDED 授予0；模型反例数量为“未搜索”，通过率及状态空间规模保持待测量。旧钥、历史责任、预算、ReadyState/ReadyUse 与迟到 IO 的冻结边界保持。 原模型和输入摘要均在启动前冻结范围内；本批修改0。

本批故障属于资源监督/权限实现，模型级性质裁决继续保留历史条件。D1-PBFT-SEAL/1.1、强G覆盖、严格分离实例0和IMPLEMENTATION_GATE=CLOSED保持。

[冻结执行锁](evidence/execution_lock.json)、[实际结果](evidence/ACTUAL_RESULTS.json)、[阻断原因](BATCH05_COUNTEREXAMPLES.md)。
