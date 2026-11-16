# B09静态补充证据索引

Material Passport：B09-AdmissionFix-static-1/r1；HOST_STATIC_ONLY。

|证据|范围|
|---|---|
|[用户原文](evidence/TASK_REQUEST.txt)|本轮静态授权及动态排除范围|
|[旧归档直接核验](evidence/HISTORICAL_ARCHIVE_CHECK.json)|batch09 80成员、batch08 246成员，摘要及逐流读取|
|[历史基线](evidence/BASELINE_LOCK.json)|4,089份旧研究及隔离目录文件；根导航另存快照|
|[原源码](evidence/SOURCE_BEFORE/inputs/static_manifest.json)|cr01原36份源码/输入完整副本|
|[最终源码](evidence/SOURCE_AFTER/inputs/static_manifest.json)|cr09最终42份源码/输入副本|
|[完整diff](evidence/FULL_DIFF.patch)|前后所有文件内容差异|
|[文件差异索引](evidence/FILE_DIFF_INDEX.json)|实际前后SHA、新增/修改/保持/更名分类|
|[最终源/输入锁](evidence/STATIC_WORKSPACE_LOCK.json)|42项实际字节数及摘要|
|[离线迁移日志](evidence/STATIC_TRANSFORMATION_LOG.json)|静态literal/绑定/资格接线的构造记录；最终diff为最终版本依据|
|[语法与调用图](evidence/SYNTAX_AND_CALL_GRAPH.json)|28程序、3.12文法、内存compile、AST调用路径|
|[保护语义](evidence/PROTECTED_SEMANTICS_CHECK.json)|10份字节、25个预算/身份函数AST及ACK/权限边界|
|[绑定/资格一致性](evidence/BINDING_AND_GATE_STATIC_CHECK.json)|旧身份命中0、17→18、内部18/4及oracle导入独立性|
|[资源重算](evidence/RESOURCE_BOUND_RECALCULATION.json)|631/640、19,861/20,000、全校准62,546及持久化原语|
|[历史性能](evidence/HISTORICAL_PERFORMANCE_EVIDENCE.json)|旧C02/其他case fsync聚合、journal同域包络、batch08范围；新测量0|
|[关键路径机器模型](evidence/CRITICAL_PATH_MODEL.json)|15个payload service、14个S worker任务、83个READY frame、273个BC事件与计费/持久化公式|
|[误路径保护](evidence/MISPATH_PROTECTION_CHECK.json)|47份副本仅读hash，与旧登记一致，执行拒绝保持|
|[历史字段登记](evidence/HISTORICAL_REFERENCE_REGISTER.json)|原件/diff中的旧身份、继承的非执行元数据与实际新scope区别|
|[A模板](evidence/DYNAMIC_A_AUTHORIZATION_TEMPLATE.json) / [B模板](evidence/DYNAMIC_B_AUTHORIZATION_TEMPLATE.json)|批准位false、真实原文SHA空、独立版本与scope|
|[静态裁决JSON](evidence/STATIC_RESULT.json)|BS四门、UNRESOLVED时间、当前T0/R null及模型UNRUN|
|[行政构造](evidence/BUILD_STATIC.txt) / [冻结审查](evidence/FREEZE_AND_REVIEW.txt)|只做host文件/AST/字节操作；目标导入0|
|[历史保持](evidence/HISTORY_PROTECTION_CHECK.json)|最终旧文件摘要及导航原文后缀核验|
|[交付核验](evidence/DELIVERY_CHECK.json)|清单、ZIP逐流、JSON/链接与最终SHA；ADMIN_ONLY|

11份指定报告均在本目录。当前没有目标运行stdout/stderr、T0、ACK或模型轨迹，新动态字段为UNRUN/null。操作日志、源码和输入副本均可供本地复核；项目内容没有外发。
