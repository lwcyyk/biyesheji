# ManagerRecovery证据索引

Material Passport：最终ManagerRecovery-static-1/r5；HOST_STATIC_ONLY。

|证据|范围|
|---|---|
|[用户原文](evidence/TASK_REQUEST.txt)|有限静态授权、动态/系统配置排除范围|
|[CalDiag归档重核](evidence/CALDIAG_ARCHIVE_RECHECK.json)|1,398成员逐流SHA和原ZIP摘要|
|[真实失败时间线](evidence/ACTUAL_FAILURE_TIMELINE.json)|15事件逐项发生/缺失、C09原始事件、Root/Receiver/waitpid与人工关闭|
|[H1–H5](evidence/ROOT_CAUSE_HYPOTHESES.json)|SOURCE/TRACE/CONTRADICTED/UNRESOLVED分项裁决|
|[上下文索引](evidence/CONTEXT_SOURCE_INDEX.json)|指定旧报告的实际字节和SHA|
|[历史基线](evidence/BASELINE_LOCK.json)|5,657份旧研究/隔离文件；根导航原文另存|
|[原源码](evidence/SOURCE_BEFORE/inputs/static_manifest.json)|原B09-r1完整42文件|
|[最终源码](evidence/SOURCE_FINAL_R5/inputs/static_manifest.json)|最终46项，原协议/测试受保护对象保持|
|[最终源锁](evidence/STATIC_WORKSPACE_LOCK.json)|实际host/未来Linux路径、46项字节数/SHA|
|[完整diff](evidence/FULL_DIFF.patch) / [差异索引](evidence/FILE_DIFF_INDEX.json)|原cr09→最终mr01，前后SHA与修改分类|
|[语法与调用图](evidence/SYNTAX_CALL_GRAPH.json)|31程序/3.12文法/内存compile、Root关闭/管理器审查路径|
|[保护语义](evidence/PROTECTED_SEMANTICS_CHECK.json)|11程序字节、29函数AST、RootIPC既有权限及原slice字节保持|
|[关闭覆盖](evidence/STATIC_CLOSURE_COVERAGE.json)|前言/返回/Root丢失/独立停止/fork未知/单sealer等静态责任|
|[输入/oracle](evidence/FIXTURE_ORACLE_CONSISTENCY.json)|64ID、56safe/8mutant、≤2帧、故障来源和独立导入|
|[资源重算](evidence/RESOURCE_BOUND_RECALCULATION.json)|MR833＋预付256=1,089/硬1,536；全校准64,082|
|[阶段A模板](evidence/PHASE_A_AUTHORIZATION_TEMPLATE.json)|新batch10-r5/scope/摘要，批准位false、真实授权SHA空|
|[阶段B条件模板](evidence/PHASE_B_CONDITIONAL_REQUEST.json)|待A充分证据后的独立batch11身份/最终摘要；当前不可执行|
|[静态迭代](evidence/FINAL_REVIEW_LOG.json)|STOP顺序/目录同步/正控制/错boot/身份未确认与回执路径修正|
|[r1候选锁](evidence/versions/r1/STATIC_WORKSPACE_LOCK.json) / [r2](evidence/versions/r2/STATIC_WORKSPACE_LOCK.json) / [r3](evidence/versions/r3/STATIC_WORKSPACE_LOCK.json) / [r4](evidence/versions/r4/STATIC_WORKSPACE_LOCK.json)|对应SOURCE_AFTER、SOURCE_AFTER_FINAL、SOURCE_FINAL_R3、SOURCE_FINAL_R4候选原件保持|
|[最终机器裁决](evidence/STATIC_RESULT.json)|MR四门、动态0/T0/R null及模型资格关闭|
|[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)|最终旧文件、误路径47及导航原文后缀核验|
|[交付核验](evidence/DELIVERY_CHECK.json)|12报告、所有候选/最终清单/JSON/链接/ZIP SHA，ADMIN_ONLY|

本轮未复制CalDiag真实随机nonce或私有原件正文到普通报告；相关原件继续留在原冻结快照及归档。新64输入和新程序实际结果统一UNRUN。所有Source中的PASS/MUTATION_DETECTED分支均为未来逻辑。本轮无外发。
