# PreT0静态修复证据索引

Material Passport：最终PreT0Recovery-static-1/r3；新增动态UNRUN。

|证据|范围|
|---|---|
|[用户原文](evidence/TASK_REQUEST.txt)|有限静态修复授权与原对象保持要求|
|[旧归档](evidence/HISTORICAL_ARCHIVE_CHECK.json)|MRA184/Manager366成员及原ZIP SHA|
|[旧磁盘锁](evidence/PREVIOUS_LOCK_DISK_CHECK.json)|6068旧baseline及MRA当前184成员实际磁盘核验|
|[原失败事实](evidence/HISTORICAL_FAILURE_FACTS.json)|初始化到125/STOP/CLOSED/UNKNOWN/seal失败的实际书签和调用链|
|[历史基线](evidence/BASELINE_LOCK.json)|6257份旧文件，导航另存原文|
|[原r5源码](evidence/SOURCE_BEFORE/inputs/static_manifest.json)|完整51项修订的原46项基线|
|[最终源](evidence/SOURCE_FINAL_R3/inputs/static_manifest.json)|35程序/16输入，最终r3|
|[最终锁](evidence/STATIC_WORKSPACE_LOCK.json)|51项实际字节数/SHA/路径与未部署状态|
|[完整diff](evidence/FULL_DIFF.patch) / [差异索引](evidence/FILE_DIFF_INDEX.json)|原mr01→最终pt01的全部变更、保持、更名及前后SHA|
|[语法/调用图](evidence/SYNTAX_CALL_GRAPH.json)|35程序AST、3.12文法、内存compile，目标import0|
|[保护语义](evidence/PROTECTED_SEMANTICS_CHECK.json)|13程序字节、40函数AST、RootIPC及slice保持|
|[生命周期义务](evidence/LIFECYCLE_STATIC_CHECKS.json)|pre-scope/intent/T0/counter/checkpoint/armed/work顺序、封存分界|
|[夹具/oracle](evidence/FIXTURE_ORACLE_CONSISTENCY.json)|64唯一ID、55safe/9mutant、独立合法armed追踪；actual UNRUN|
|[资源重算](evidence/RESOURCE_BOUND_RECALCULATION.json)|PT1089/1536、完整65618、最小1537、原120及自动行政30/35上界|
|[正常模式模板](evidence/PHASE_A_NORMAL_START_AUTHORIZATION_TEMPLATE.json) / [预窗失败模式模板](evidence/PHASE_A_PREWINDOW_ABORT_AUTHORIZATION_TEMPLATE.json)|互斥新batch11-r3，批准位false、实际原文SHA空|
|[r1锁](evidence/versions/r1/STATIC_WORKSPACE_LOCK.json) / [r2锁](evidence/versions/r2/STATIC_WORKSPACE_LOCK.json)|候选SOURCE_AFTER、SOURCE_FINAL_R2及前期构造记录保留|
|[静态审查登记](evidence/STATIC_REVIEW_LOG.json)|scope/intent/独立reference/阶段限定变异/封存校验及行政时限|
|[最终机器裁决](evidence/STATIC_RESULT.json)|四门、source/lock摘要、目标0/T0/R null|
|[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)|最终6257旧文件及47误路径副本、导航原文后缀|
|[交付核验](evidence/DELIVERY_CHECK.json)|13报告、JSON/链接、候选/最终源与ZIP SHA，ADMIN_ONLY|

自动host收尾与native post导出的新路径尚未运行。未来ADMIN_EVIDENCE_SEALED和NATIVE_SEAL状态分别由实际证据决定；本轮研究ZIP也只说明静态交付完整性。所有历史失败及旧真实C09 PASS保持。
