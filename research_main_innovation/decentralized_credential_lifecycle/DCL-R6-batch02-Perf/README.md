# batch02-Perf静态诊断交付

Material Passport：OFFLINE_ONLY。原ZIP/快照直接核验通过。300秒是共同T0起的软窗；预付内部跨度298.626607199秒/99.5422%，C00/C01到结果仅1.109秒。所有COMMIT复用PREP时标，单次fsync耗时仍未知。

|交付|内容|
|---|---|
|[时间线](PERF_EXECUTION_TIMELINE.md)|精确观测、未知边界、阶段表|
|[账审查](PERF_BUDGET_LEDGER_AUDIT.md)|32191来源/状态/未使用预付|
|[持久成本](PERF_PERSISTENCE_COST_ANALYSIS.md)|周期分布/代码调用数/缺测点|
|[根因](PERF_ROOT_CAUSE.md)|控制流因果链与归因限度|
|[三方案](PERF_REPAIR_OPTIONS.md)|主选精确N范围，保留300秒|
|[预算安全](PERF_BUDGET_SAFETY_PROOF.md)|BUD-1…6/崩溃/并发/浪费|
|[误路径登记](PERF_DUPLICATE_PATH_REGISTER.md)|47文件只读匹配，禁止正式输入|
|[B03计划](BATCH03_EXECUTION_PLAN.md)|先静态修复锁，再独立执行|
|[授权请求](BATCH03_AUTHORIZATION_REQUEST.md)|有限代码/诊断范围与缺口|
|[最终裁决](FINAL_DECISION.md)|PERF1–4与不变项|

[来源索引](SOURCE_INDEX.json)、[ZIP核验](evidence/ZIP_VERIFICATION.json)、[派生周期统计](evidence/JOURNAL_STATS.json)、[交付核对](evidence/DELIVERY_CHECK.json)。

本轮无新Linux命令、实现代码、探针、校准、模型、配置或执行环境。batch03未创建/未授权；原C00/C01局部通过和C02失败原样保留。主机制门CLOSED、严格分离0。
