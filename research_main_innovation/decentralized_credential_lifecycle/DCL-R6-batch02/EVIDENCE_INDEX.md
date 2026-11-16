# batch02证据导航

2026-11-10。Material Passport：原始执行与行政来源链。所有敏感路径/boot标识只存本地，未对外发送。

|记录|内容|
|---|---|
|[授权](evidence/BATCH02_AUTHORIZATION_RECEIPT.json)|实际原文与范围|
|[入场锁](evidence/BATCH02_BASELINE_LOCK.json)|LC原件与4导航快照|
|[53项原生复核](evidence/BATCH02_PREFLIGHT_HASHES.json)|runtime/源/缓存/输入/配置全部匹配|
|[命令](evidence/B02_COMMAND_RESULTS.json)|精确argv/时间/双流/退出|
|[动态启动](evidence/commands/22.result.json)|单次Launcher exit65/约300.7秒|
|[退出确认](evidence/commands/23.result.json)|父inactive、全部实际瞬态MainPID0/not-found|
|[实际账](evidence/BATCH02_ACCOUNTING_ACTUAL.json)|完整交易/时限/峰值口径/关闭|
|[结果](evidence/BATCH02_RUN_RESULTS.json)|C00/C01 PASS、C02 FAIL、其余UNRUN|
|[原生导出](evidence/BATCH02_EXPORT_LOCK.json)|Linux到正确host32文件逐字节核对|
|[原ZIP](evidence/BATCH02_NATIVE_ARCHIVE_CHECK.json)|30 manifest文件＋manifest、31流，逐流核验|
|[误路径事件](evidence/BATCH02_COPY_CORRECTION.json)|保留原错误/策略拒绝/安全复制替代/重复副本待清理|
|[历史](evidence/BATCH02_HISTORY_INTEGRITY_CHECK.json)|原batch01/版本/LC及研究锁保持|
|[独立包](evidence/BATCH02_PACKAGE.json)|native快照、冻结LC副本、报告和当前导航的完整byte来源|
|[行政核对](evidence/BATCH02_DELIVERY_CHECK.json)|文档、JSON、链接、hash与范围|
|[输出锁](evidence/BATCH02_OUTPUT_MANIFEST.json)|本轮研究/根导航及host包，排除自身/交付核对避免循环|

原始Linux文件保留/var/lib/dcl-r6/batch02；正确host native_snapshot与FROZEN_LC供独立复核。自动EVIDENCE.zip原字节SHA=910af1ca01bf8e2258a18f95d1a12187eb2b7efd23f44fbe11146c66c5d97c84。外层自包含包另存，不改原自动manifest。

C02预付款尚未完毕，未创建allocator child。所有模型/变异/参考实际值为空。原state.status的CALIBRATING与CLOSED权威记录并存，报告保留原状。统计使用保守已预留信用，快照RSS/charge/AS各自命名。

原LC输出4根导航由本轮evidence/navigation_before复核，更早阶段沿用各自原快照；没有重写任何旧manifest。行政核验无法授资源、模型、外部审查或原创性层级通过。
