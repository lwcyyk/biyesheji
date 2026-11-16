# DCL-R6-batch02实际执行交付

2026-11-10。Material Passport：DYNAMIC_CALIBRATION_STOPPED。C00/C01按冻结谓词PASS；C02在300秒软截止到达时仍在持久预付，原FAIL/分析INCONCLUSIVE_LIMIT。分配子探针、后续C03–C12、兼容性和F1/F4未启动。

|报告|内容|
|---|---|
|[授权/锁](BATCH02_AUTHORIZATION_AND_LOCK.md)|实际范围/53项摘要/单次启动|
|[兼容性](BATCH02_RUNTIME_COMPATIBILITY.md)|资源层入口有据，五业务未达|
|[校准](BATCH02_RESOURCE_CALIBRATION.md)|各case、首失败、活时/退出观测范围|
|[资源账](BATCH02_RESOURCE_ACCOUNTING.md)|32191、300.1698498秒、关闭/空组/ZIP|
|[F1](BATCH02_F1_RESULTS.md)|全部UNRUN_RESOURCE_GATE|
|[F4](BATCH02_F4_RESULTS.md)|全部UNRUN_RESOURCE_GATE|
|[失败/反例](BATCH02_COUNTEREXAMPLES.md)|资源首次失败与行政事件，协议反例0|
|[最终裁决](BATCH02_FINAL_DECISION.md)|B02-1至5/后续边界|

[实际JSON](evidence/BATCH02_RUN_RESULTS.json)、[原命令](evidence/B02_COMMAND_RESULTS.json)、[证据索引](EVIDENCE_INDEX.md)、[来源](SOURCE_INDEX.json)、[交付核对](evidence/BATCH02_DELIVERY_CHECK.json)、[独立包](evidence/BATCH02_PACKAGE.json)。

最终预留32191、journal两阶段各32191、COMMITTED无模糊事务，未用信用不回收。资源门未取得，模型访问0，无PASS_BOUNDED或协议反例；父树和全部本批进程已退出，batch02关闭，不重开预算。旧源码/账/失败/各阶段保持。

行政误路径副本已另外复制到正确专用根并核hash；自动审批拒绝误路径的迁移/删除，重复副本保留待清理，见完整事件记录。
