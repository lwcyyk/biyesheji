# batch09证据索引

Material Passport：DCL-R6-batch09；2026-11-12；ADMIN_INTEGRITY与动态资格分别登记。

|证据|内容|
|---|---|
|[TASK_REQUEST](evidence/TASK_REQUEST.txt)|用户实际完整条件执行授权原文|
|[AUTHORIZATION_RECEIVED](evidence/AUTHORIZATION_RECEIVED.json)|原文SHA、范围和运行回执尚待建立的状态|
|[STATIC_EXECUTION_LOCK](evidence/STATIC_EXECUTION_LOCK.json)|三项阻断、runnable=false、实际argv空、T0/R null|
|[FROZEN_HASH_CHECK](evidence/FROZEN_HASH_CHECK.json)|36份冻结文件、长度、摘要与manifest/锁交叉绑定|
|[FROZEN_C00READY_REFERENCE](evidence/FROZEN_C00READY_REFERENCE/inputs/static_manifest.json)|原36份源/输入只读参考副本；源码实现保持原字节|
|[AST_SOURCE_INDEX](evidence/AST_SOURCE_INDEX.json)|24份程序host AST索引；目标导入0|
|[BATCH08_ARCHIVE_CHECK](evidence/BATCH08_ARCHIVE_CHECK.json)|旧包246成员/247条目直接核验及内部原生ZIP CRC|
|[FROZEN_TEST_INVENTORY](evidence/FROZEN_TEST_INVENTORY.json)|各套job集合、依赖、原batch08参考argv及实际执行空集|
|[NAMESPACE_BINDING_AUDIT](evidence/NAMESPACE_BINDING_AUDIT.json)|旧批次215处内容命中及入口绑定|
|[NAMESPACE_MIGRATION_REVIEW](evidence/NAMESPACE_MIGRATION_REVIEW.json)|16份文件的命名空间静态适配责任，当前变更0|
|[GATE_NEGATIVE_COVERAGE_AUDIT](evidence/GATE_NEGATIVE_COVERAGE_AUDIT.json)|17项原recipe与预算异常负向覆盖缺项|
|[RESOURCE_BOUND_RECALCULATION](evidence/RESOURCE_BOUND_RECALCULATION.json)|62,546拆算、剩余额度及300秒证据缺口|
|[CONTEXT_SOURCE_INDEX](evidence/CONTEXT_SOURCE_INDEX.json)|19份指定历史报告/原规格的真实字节SHA|
|[BASELINE_LOCK](evidence/BASELINE_LOCK.json)|4,010份历史研究/隔离工作区文件基线；4份根导航另存快照|
|[ADMIN_OPERATIONS](evidence/ADMIN_OPERATIONS.json)|本轮host hash/AST/ZIP行政操作的解释器、命令与时间|
|[ADMIN_ADMISSION_AUDIT](evidence/ADMIN_ADMISSION_AUDIT.txt)|仅host行政审计源文本；目标模块导入/运行0|
|[HISTORY_PROTECTION_CHECK](evidence/HISTORY_PROTECTION_CHECK.json)|交付前历史字节保持及导航原文后缀核验|
|[DELIVERY_CHECK](evidence/DELIVERY_CHECK.json)|行政JSON/链接/清单/ZIP核验；动态资格保持关闭|

十二份用户要求的结果报告及补充准入材料均位于本目录。原始stdout/stderr、当前boot、ACK及模型轨迹的batch09运行文件尚待产生，实际目标命令为空；对应报告明确UNRUN/null。旧batch08包保留原位置，本轮仅直接读取验证，私有运行记录正文未复制到普通报告。
