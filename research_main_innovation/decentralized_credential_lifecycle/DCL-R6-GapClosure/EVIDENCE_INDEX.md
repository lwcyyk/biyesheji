# 证据索引

Material Passport：BF-static-2/r4 / export_lock_revision=1。所有动态结果为UNRUN，源码中的PASS分支属于未来判据。

|工件|用途|
|---|---|
|[TASK_REQUEST](evidence/TASK_REQUEST.txt)、[授权收据](evidence/AUTHORIZATION_RECEIPT.json)|本次明确静态许可及范围；动态许可缺失|
|[编码前合同](evidence/PREIMPLEMENTATION_CONTRACT.md)|输入族、工程对照、通用方法同等与严格分离0|
|[BASELINE_LOCK](evidence/BASELINE_LOCK.json)、[旧导航](evidence/navigation_before/)|144历史工件摘要、旧源、原batch03包76项复核|
|[SAFETY_CONTRACT](evidence/SAFETY_CONTRACT.json)|34独立job、17负向门case及全部初态/触发/判据/上界|
|[SOURCE_DIFF_INDEX](evidence/SOURCE_DIFF_INDEX.json)、[diff](evidence/diff/)|11源旧新摘要，1修改、3新增、7不变|
|[STATIC_WORKSPACE_LOCK](evidence/STATIC_WORKSPACE_LOCK.json)|30项真实host/Linux源/缓存/输入锁|
|[static_manifest](evidence/static_manifest.json)、[execution_lock](evidence/execution_lock.json)|最终源码/32关键工具运行时/完整树输入锁及所有未来argv|
|[FREEZE_REVISION](evidence/FREEZE_REVISION.json)|候选到r4的静态审查修订；无中间动态运行|
|[candidate1](evidence/freeze_candidate_1/)、[r1](evidence/freeze_candidate_r1/)、[r2](evidence/freeze_candidate_r2/)、[r3](evidence/freeze_candidate_r3/)|被替代候选及摘要/源码保存；不参与执行输入|
|[COMMAND_PLAN](evidence/COMMAND_PLAN.json)、[commands](evidence/commands/)、[命令汇总](evidence/COMMAND_RESULTS_SUMMARY.json)|17条真实WSL检查/编译，原始双流与退出|
|[ADMIN_ERROR_EVENT](evidence/ADMIN_ERROR_EVENT.json)|命令长度/脚本解析/清单空字段行政错误及最终证据归属|
|[STATIC_CONTROL_FLOW_CHECK](evidence/STATIC_CONTROL_FLOW_CHECK.json)|统一oracle、接口、预算、前置计费、并发与绑定静态核对|
|[ARGV_STATIC_CHECK](evidence/ARGV_STATIC_CHECK.json)、[未来命令字面表](evidence/FUTURE_COMMANDS.md)|15组payload×36属性、34 worker模板、入口/恢复/stop/准备及本批journal导出|
|[HISTORY_CHECK](evidence/HISTORY_CHECK.json)|144研究、24原BF工作区、51batch02原件和47误副本只读hash复核|
|[EXECUTION_STATUS](evidence/EXECUTION_STATUS.json)|实际34job/17门case/C00–C12/F1/F4未运行；账/T0未初始化|
|[OUTPUT_MANIFEST](evidence/OUTPUT_MANIFEST.json)、[DELIVERY_CHECK](evidence/DELIVERY_CHECK.json)|最终工件与外部静态工作区行政核对；自引用排除|
|[静态审查包](GAPCLOSURE_STATIC_REVIEW.zip)|报告、源码/缓存/输入副本、原始静态输出及manifest；不含自身和最终delivery check|

[SOURCE_INDEX](SOURCE_INDEX.json)链接全部主要原始来源。当前不存在新的动态故障日志、预算账或模型轨迹；实际编译与只读输出按原始字节保留。
