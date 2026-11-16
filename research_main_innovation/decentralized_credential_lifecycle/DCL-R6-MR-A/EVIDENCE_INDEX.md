# MR-A证据索引

Material Passport：batch10-r5真实有限A；STARTUP_FAILED_PRE_T0。

|证据|范围|
|---|---|
|[用户授权](evidence/TASK_REQUEST.txt) / [实际回执](evidence/execution_authorization.json)|r5有限A及关闭注入批准；模型关闭|
|[授权/回执锁](evidence/AUTHORIZATION_RECEIPT_LOCK.json)|原文/回执SHA、唯一控制路径及scope|
|[源与范围准入](evidence/SOURCE_AND_SCOPE_ADMISSION.json)|46项/31程序核验、单C10收尾解释及旧r4文案登记|
|[原生部署](evidence/DEPLOYMENT_RESULT.json)|45份Linux源/输入、Root权限/实际3.12.3摘要与原生语法|
|[唯一入口](evidence/ACTIVE_ENTRY_INVOCATION.json) / [返回](evidence/ACTIVE_ENTRY_RETURN.json)|实际argv、host2.0633844秒/exit125，重跑0|
|[manager实际状态](evidence/MANAGER_EVENT_ACTUAL.json)|3次预检仅mnt-e基线，当前退出/恢复事件尚未产生|
|[首次错误](evidence/FIRST_FAILURE.json)|初始health→query→运行态checkpoint→IPC_STATE_MISSING及两个预窗关闭/封存依赖|
|[自动关闭](evidence/AUTOMATIC_CLOSURE_ACTUAL.json)|自动STOP/CLOSED、父stop返回、abort后备超时、UNKNOWN/原生seal缺失及角色退出|
|[回归实际数量](evidence/REGRESSION_ACTUAL.json)|64执行0、8变异检出0，状态UNRUN|
|[实际时间书签](evidence/EXECUTION_TIMELINE.json)|同boot各actor采样、故障区间、STOP→CLOSED/父停止/child wait|
|[Native快照锁](evidence/NATIVE_EXPORT_LOCK.json)|22份实际原件及权限/类型/摘要；无T0/账文件|
|[源导出锁](evidence/FROZEN_SOURCE_EXPORT_LOCK.json)|45 Linux＋1 host入口，全部最终r5字节|
|[事后审计](evidence/POSTRUN_AUDIT.json)|角色全空、父cgroup不存在、STOP/CLOSED存在、原生ZIP缺失|
|[failed集合原文](evidence/FAILED_UNITS.stdout.raw) / [当前单位只读查询](evidence/BATCH10_UNITS.stdout.raw)|仅保留原始查询，本轮没有reset-failed|
|[stdout](evidence/windows_entry.stdout.raw) / [stderr](evidence/windows_entry.stderr.raw)|预检/exec及首个异常原字节；附可读解码|
|[实际命令计划](evidence/ADMIN_COMMAND_PLAN.json)|部署与事后导出2次admin调用；active另1次；无人工清理|
|[boot过滤journal](evidence/RUN_BOOT_JOURNAL.stdout.raw)|仅当前batch10冻结单位集合，本轮服务未启动|
|[真实阶段结果](evidence/MRA_RESULT.json)|A1–A5及R/T0 null、资源/模型资格关闭|
|[历史基线](evidence/BASELINE_LOCK.json) / [保护核验](evidence/HISTORY_PROTECTION_CHECK.json)|6,068历史文件及47误路径副本原件保持|
|[nonce核验](evidence/NONCE_DISCLOSURE_CHECK.json)|实际随机值只保留私有快照/归档，普通报告零匹配|
|[交付核验](evidence/DELIVERY_CHECK.json)|9指定报告、源/Native快照、清单和行政ZIP逐流SHA；原生自动seal仍失败|

原始22文件及46份源导出位于D:/毕业设计/DCL-R6-isolated-verification/batch10/native_snapshot和FROZEN_MR；Root私有nonce保持原件。本次证据包属于行政打包，和缺失的Native out/EVIDENCE.zip分别登记，避免把人工打包当作自动关闭已验收。
