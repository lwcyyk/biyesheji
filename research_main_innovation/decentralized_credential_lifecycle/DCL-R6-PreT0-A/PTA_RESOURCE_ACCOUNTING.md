# 实际资源与合同边界

Material Passport：DCL-R6-PreT0-A；batch11；PreT0Recovery-static-1/r3；NORMAL_START；2026-11-12（Asia/Shanghai）；实际入口1次，重跑0，源码修复0。

**本批真实创建预算账，最终R=0；完整资源资格仍未取得。** 这里的0来自BRNGv001原件，和历史MRA的未初始化null分别保留。

|指标|实际观测/边界|
|---|---|
|T0/deadline/stop_at|66.896850269 / 1866.896850269 / 1806.896850269|
|counter|24字节，BRNGv001，used0，cap1,000,000；COMMITTED after0|
|journal|文件尚未创建；实际reserve事务0。关闭预算快照将缺journal记UNKNOWN，原字段保持|
|阶段A访问|实际0；计划正常完成1,090，硬界1,537；专项1,089/1,536均为计划界|
|完整校准访问|65,618硬界保持，当前完整校准UNRUN|
|active host时间|1.918233000秒，仅active WSL；含host启动及自动post总2.438853600秒|
|T0到首STOP|0.224342140秒|
|T0到CLOSED|0.242512293秒|
|T0到child waitpid|0.329197521秒|
|T0到最终内部cleanup采样|0.474233445秒|
|启动TCB|原起点65.510243359、deadline185.510243359；过期故障未测|
|父Payload slice|TasksMax4、MemoryMax4GiB；观察pids.current0、memory.current0、memory.peak0，cgroup populated0|
|单进程RLIMIT_AS|冻结Native预检和独立停止器设置1GiB；实际Payload未启动，无Payload工作进程限额样本|
|Root RSS及全树任务峰值|未采集精确高水位，null；三个已登记Root角色存在并行区间，最大3为结构推断，上限观察不替代全树测量|
|自动post上界|原alarm30秒/host等待35秒保持；实际0.222965900秒导入失败|

Payload空slice的内存0不代表Root、WSL或主机内存0。Root角色在父Payload slice外，其RSS和全任务峰值资料缺失。没有OOM或任务工作量校准证据，完整300秒链时间仍TIME_FEASIBILITY_UNRESOLVED_EARLY_FAILURE。

主机侧检查、部署及只读导出均为授权行政工作；未计为模型访问。原1,000,000/1,800/校准100,000与300/提前1,740/AS1GiB/父4tasks保持，没有第二T0/退款/预算重置。

[原始实际账与资源](evidence/ACTUAL_RESULTS.json) · [停止快照](evidence/CLOSURE_AUDIT.json) · [源锁核验](evidence/SOURCE_AFTER_CHECK.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原条件结论与强G覆盖裁决保持。
