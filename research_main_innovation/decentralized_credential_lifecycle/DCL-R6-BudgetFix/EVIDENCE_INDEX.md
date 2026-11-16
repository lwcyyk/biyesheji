# 证据索引
Material Passport：BF-static-1；原始、派生及未决证据分别登记。

|证据|用途|
|---|---|
|[TASK_REQUEST](evidence/TASK_REQUEST.txt)、[AUTHORIZATION_RECEIPT](evidence/AUTHORIZATION_RECEIPT.json)|本次静态专项范围，动态授权缺失|
|[BASELINE_LOCK](evidence/BASELINE_LOCK.json)、[navigation_before](evidence/navigation_before/)|Perf与旧源摘要、四导航修订前字节|
|[COMMAND_PLAN](evidence/COMMAND_PLAN.json)、[commands](evidence/commands/)|实际预登记argv、退出与原始字节流；01退出未知，02/03未启动|
|[CAPTURE_ERROR_EVENT](evidence/CAPTURE_ERROR_EVENT.json)、[COPY_COMPILE_EVENT](evidence/COPY_COMPILE_EVENT.json)|记录器/复制错误及正确最终编译归属|
|[SOURCE_DIFF_INDEX](evidence/SOURCE_DIFF_INDEX.json)、[diff](evidence/diff/)|八源新旧摘要及完整差异，只有两源改变|
|[STATIC_WORKSPACE_LOCK](evidence/STATIC_WORKSPACE_LOCK.json)|24项实际host静态源/缓存/输入/拟用slice锁|
|[static_manifest](evidence/static_manifest.json)、[execution_lock](evidence/execution_lock.json)|源/运行时/输入锁和14 payload及全部主流程argv|
|[CHILD_CONTRACTS](evidence/CHILD_CONTRACTS.json)|三个固定N合同，与lc03/inputs同字节|
|[FUTURE_COMMANDS](evidence/FUTURE_COMMANDS.md)|待批准的命令字面展开，本轮执行0|
|[runtime_critical](evidence/runtime_critical.json)、[runtime_tree_lock](evidence/runtime_tree_lock.json)|继承的运行时记录，31关键文件本轮重新核对|
|[HISTORY_AND_ENVIRONMENT_CHECK](evidence/HISTORY_AND_ENVIRONMENT_CHECK.json)|Perf37/B02原件、47副本、当前关键runtime/旧unit及新批缺失检查|
|[STATIC_CALLSITE_CHECK](evidence/STATIC_CALLSITE_CHECK.json)|签名、前置扣减与14组未来argv静态对应|
|[OUTPUT_MANIFEST](evidence/OUTPUT_MANIFEST.json)、[DELIVERY_CHECK](evidence/DELIVERY_CHECK.json)|研究输出与外部工作区哈希复核、自引用排除|

尚缺证据：新性能/真实fsync/C02子执行与资源资格、精确范围S1–S9动态故障/并发、F1/F4正式模型结果、端到端存储及精确终止时延。旧失败事实与原日志由Perf来源索引链接，不复制或重写原账。
