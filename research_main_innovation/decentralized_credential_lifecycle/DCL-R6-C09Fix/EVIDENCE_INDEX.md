# C09Fix证据索引

|工件|用途|
|---|---|
|[任务](evidence/TASK_REQUEST.txt)、[授权登记](evidence/AUTHORIZATION_RECEIPT.json)|当前仅静态权限|
|[编码前范围](evidence/PREIMPLEMENTATION_SCOPE.md)|依赖说明、工程输入族、标准方法同等与严格分离0|
|[基线](evidence/BASELINE_LOCK.json)、[旧导航](evidence/navigation_before/)|batch04/GC原件、276项包核验、原源摘要|
|[重建时间线](evidence/RECONSTRUCTED_TIMELINE.json)、[H1/H2裁决](evidence/HYPOTHESIS_DECISION.json)|历史实测、源码偏序及缺失事件分开|
|[C09合同](evidence/c09_contract.json)、[S合同](evidence/safety_contract.json)|34个C09H输入；原S仅命名绑定batch05|
|[源差异](evidence/SOURCE_DIFF_INDEX.json)、[diff](evidence/diff/)|14源的修改/新增/不变与全文差异|
|[工作区锁](evidence/STATIC_WORKSPACE_LOCK.json)、[manifest](evidence/static_manifest.json)、[执行锁](evidence/execution_lock.json)|37实际文件，源码/缓存/输入/运行时与所有未来argv|
|[安全检查](evidence/STATIC_SAFETY_CHECK.json)、[历史](evidence/HISTORY_CHECK.json)|静态性质与原件/47误副本只读hash|
|[命令计划](evidence/COMMAND_PLAN.json)、[双流](evidence/commands/)、[汇总](evidence/COMMAND_RESULTS_SUMMARY.json)|6条只读/编译，源码正文执行0|
|[动态实际字段](evidence/ACTUAL_STATUS.json)|actual=null、全部新动态UNRUN|
|[未来命令](evidence/FUTURE_COMMANDS.md)、[来源](SOURCE_INDEX.json)|下一许可的真实锁与原始依据|
|[输出锁](evidence/OUTPUT_MANIFEST.json)、[交付核对](evidence/DELIVERY_CHECK.json)|行政完整性，不构成动态通过|
|[完整静态包](C09FIX_STATIC_REVIEW.zip)|报告、原始静态输出、37源/缓存/输入副本与manifest；自身/delivery排除自引用|

唯一执行源码路径为c09f01/src。旧BF-static-2/r4和batch04账/收据/证据包保持，batch05运行根未创建。
