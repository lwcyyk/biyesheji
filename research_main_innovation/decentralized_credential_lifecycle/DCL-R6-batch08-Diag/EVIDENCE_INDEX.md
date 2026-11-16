# batch08-Diag证据索引

Material Passport：DCL-R6-batch08-Diag；C00Ready-static-1/r2；真实最小诊断；2026-11-12（Asia/Shanghai）；重跑0。

|交付材料|范围|
|---|---|
|[BATCH08_DIAG_AUTHORIZATION_AND_LOCK.md](<BATCH08_DIAG_AUTHORIZATION_AND_LOCK.md>)|BATCH08_DIAG_AUTHORIZATION_AND_LOCK|
|[BATCH08_DIAG_RUNTIME.md](<BATCH08_DIAG_RUNTIME.md>)|BATCH08_DIAG_RUNTIME|
|[BATCH08_DIAG_BOOT_IDENTITY.md](<BATCH08_DIAG_BOOT_IDENTITY.md>)|BATCH08_DIAG_BOOT_IDENTITY|
|[BATCH08_C00_FIELD_RESULTS.md](<BATCH08_C00_FIELD_RESULTS.md>)|BATCH08_C00_FIELD_RESULTS|
|[BATCH08_C00_READINESS_TIMELINE.md](<BATCH08_C00_READINESS_TIMELINE.md>)|BATCH08_C00_READINESS_TIMELINE|
|[BATCH08_C00_REGRESSION_RESULTS.md](<BATCH08_C00_REGRESSION_RESULTS.md>)|BATCH08_C00_REGRESSION_RESULTS|
|[BATCH08_RESOURCE_ACCOUNTING.md](<BATCH08_RESOURCE_ACCOUNTING.md>)|BATCH08_RESOURCE_ACCOUNTING|
|[BATCH08_DIAG_COUNTEREXAMPLES.md](<BATCH08_DIAG_COUNTEREXAMPLES.md>)|BATCH08_DIAG_COUNTEREXAMPLES|
|[BATCH08_DIAG_FINAL_DECISION.md](<BATCH08_DIAG_FINAL_DECISION.md>)|BATCH08_DIAG_FINAL_DECISION|

[字段独立重算](evidence/C00_FIELD_ACTUAL.json)、[时序](evidence/READINESS_TIMELINE.json)、[boot身份](evidence/BOOT_IDENTITY_ACTUAL.json)、[64原始参考检查](evidence/REGRESSION_REFERENCE_CHECK.json)、[账核算](evidence/RESOURCE_ACCOUNTING.json)、[实际状态](evidence/ACTUAL_RESULTS.json)。

[入口原始stdout](evidence/windows_entry.stdout.raw)、[原始stderr](evidence/windows_entry.stderr.raw)、[stderr解码](evidence/STDERR_DECODE.json)、[实际命令](COMMAND_SUMMARY.md)、[run journal](evidence/JOURNAL_SUMMARY.json)、[原始journal字节](evidence/RUN_BOOT_JOURNAL.stdout.raw)。当前数据来源于真实当前接口及标记清楚的合成套件，未从expected回填observed。

[101 native锁](evidence/NATIVE_EXPORT_LOCK.json)、[36最终源码/输入锁](evidence/FROZEN_SOURCE_EXPORT_LOCK.json)、[路径映射](SOURCE_INDEX.json)、[原生100条目seal](evidence/NATIVE_ZIP_CHECK.json)、[关闭后核查](evidence/POSTRUN_AUDIT.json)、[历史原件保护](evidence/HISTORY_PROTECTION_CHECK.json)。当前sealed秘密原件只保留Root私有相对路径；Linux原权限/ACL/inode在导出锁，host副本证明字节。

[BATCH08_DIAG_EVIDENCE.zip](BATCH08_DIAG_EVIDENCE.zip)是授权私有审阅包，含研究、native101、最终36、原冻结控制文件与四导航。[OUTPUT_MANIFEST](OUTPUT_MANIFEST.json)列路径/字节/sha/archive_path，[DELIVERY_CHECK](evidence/DELIVERY_CHECK.json)另记manifest/ZIP摘要，排除自引用。行政PASS只证明字节和索引，不升级本轮为完整资源门或模型结论。

旧batch07所有字段缺口/失败和原包保留，未来完整链需要独立新批次准入；本轮没有创建batch09。
