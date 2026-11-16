# 运行时负向与变异准备

Material Passport：DCL-R6-RuntimeAdapt-Fix；RuntimeAdapt-static-1/r1；2026-11-13（Asia/Shanghai）；READ_ONLY_PLATFORM_AND_HOST_STATIC；业务动态测试0。

新增RA32＝24safe＋8mutant，当前全部UNRUN；真实系统库从未被改动制造故障。输入覆盖新三摘要/同源/依赖/包、旧新混用、单项hash、symlink、包不符、Build-ID、搜索覆盖、来源缺失、读取失败、预检后变化、自动重锁、仅版本判断、跨批资格、CLOSED工作等。

八项变异missing_digest_pass、alias_change_pass、package_change_pass、build_id_pass、loader_override_pass、stale_mapping_pass、cross_batch_pass、silent_relock_pass复用对应safe输入。独立oracle只导入stdlib，按实际trace判断IDENTITY_BYPASS/SILENT_RELOCK或其他违规，再检查声明目标，原始input/binding/hash必须对应。

RA-SIMULATION/1是合成身份决策/观察测试，未替代真实映射、包目录或换库故障的OS证明。未来若需要实际故障注入只能使用独立文件副本/冻结对象，不能写系统loader/libc/libm。本轮只完成schema/源码/配对静态审查与只读平台取证；RA32和oracle没有调用。

RA每job16预付＋1审查，entry1，完成545/硬768。下一A2全量PT64/PF48/TR40/RA32共184合成job，其中33变异，另有真实C00。完成3133、阶段A硬4417；完整硬68498≤100000。真实hash/包/maps读取为5秒有界行政IO，新增子进程0，不能变成修改预算或追加窗口的权限。

[32项冻结输入](evidence/SOURCE_FINAL_R1/inputs/runtime_regression_contract.json) · [独立oracle](evidence/SOURCE_FINAL_R1/src/runtime_oracle.py) · [静态变异矩阵](evidence/RUNTIME_REGRESSION_STATIC_CHECK.json) · [资源界](evidence/RESOURCE_BOUND_RECALCULATION.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。历史安全与原创性裁决保持。
