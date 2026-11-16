# batch04证据索引

Material Passport：真实运行，首次C09失败后关闭；原始证据与分析派生分开。

|工件|内容|
|---|---|
|[TASK_REQUEST](evidence/TASK_REQUEST.txt)、[授权收据](evidence/AUTHORIZATION_RECEIPT.json)、[实际执行许可](evidence/execution_authorization.json)|用户授权原文、研究登记和安装到root inputs的匹配许可|
|[BASELINE_LOCK](evidence/BASELINE_LOCK.json)、[旧导航](evidence/navigation_before/)|282历史工件和四导航修订前摘要|
|[HASH_SCOPE](evidence/HASH_SCOPE.json)、[LINUX_EXPECTED](evidence/LINUX_EXPECTED.sha256)|1274唯一Linux文件核验范围|
|[初次预检](evidence/PREFLIGHT_BASE_FIRST_BOOT.json)、[最终预检](evidence/PREFLIGHT_FINAL.json)|boot变化在T0前全量刷新；唯一窗口随后初始化|
|[COMMAND_PLAN](evidence/COMMAND_PLAN.json)、[commands](evidence/commands/)、[命令汇总](evidence/COMMAND_RESULTS_SUMMARY.json)|34条实际WSL命令的argv/双流/退出；29为唯一launcher，resume0|
|[首次失败](evidence/FIRST_FAILURE.json)、[根因](evidence/C09_ROOT_CAUSE.json)、[源码摘录](evidence/C09_SOURCE_EXCERPT.txt)|真实UNEXPECTED关闭与最终C09标记、源码推导的旧快照竞态|
|[原始journal](evidence/commands/30.stdout.raw)、[journal时间线](evidence/JOURNAL_TIMELINE.json)|运行boot内40条限定16-unit记录，含stopper实际exit125|
|[boot与关闭时间线](evidence/BOOT_AND_CLOSURE_TIMELINE.json)|T0/close/cleanup及后续另一boot观察分开|
|[校准实际](evidence/CALIBRATION_ACTUAL.json)、[S/门实际](evidence/S_AND_GATE_ACTUAL.json)|9机器PASS、C09无成功收据、后续UNRUN|
|[原始账独立行政检查](evidence/LEDGER_AUDIT.json)|counter37021，31事务，三范围事实与child计数|
|[C02性能](evidence/C02_PERFORMANCE.json)、[资源观察](evidence/RESOURCE_OBSERVATIONS.json)|原始分阶段聚合、11目标fsync、17991操作、AS/RSS/charge/pids口径|
|[native导出锁](evidence/NATIVE_EXPORT_LOCK.json)、[冻结源导出锁](evidence/FROZEN_SOURCE_EXPORT_LOCK.json)|停止后94native文件和30源/输入/缓存逐字节导出；未假称native程序自动seal|
|[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)|282研究、GC30/BF24、batch02原件51与47误副本保持|
|[SOURCE_INDEX](SOURCE_INDEX.json)|正式F1/F4规格、前置合同和历史来源|
|[OUTPUT_MANIFEST](evidence/OUTPUT_MANIFEST.json)、[DELIVERY_CHECK](evidence/DELIVERY_CHECK.json)|本轮输出、host native/source快照、ZIP逐流与链接检查|
|[完整证据包](BATCH04_EVIDENCE.zip)|研究文档、命令双流、native94、冻结源30及manifest；自身/最终delivery排除自引用|

原Linux目录保持原始；host快照位于D:\毕业设计\DCL-R6-isolated-verification\batch04。所有S/F1/F4未运行字段保持，SOURCE/判据没有现场修订。
