# C00就绪时间线、双取样和14秒上界

Material Passport：DCL-R6-batch08-Diag；C00Ready-static-1/r2；真实最小诊断；2026-11-12（Asia/Shanghai）；重跑0。

时间使用同一run-boot CLOCK_BOOTTIME。源合同until=min(start+14,T0+300,stop_at,deadline)；实际until=63.776506795，其他边界更晚，因此由until−14可恢复原start请求时刻=49.776506795。该推导按冻结控制流，保持与独立时钟域分开。

|原始文件|manager双侧阶段|采样开始|采样完成|裁决|
|---|---|---|---|---|
|ready_C00_0000.json|['STARTING', 'STARTING']|49.805647354|49.837307487|STARTING|
|ready_C00_0001.json|['READY', 'READY']|49.893156808|49.926347676|READY|
|ready_C00_0002.json|['READY', 'READY']|49.931648577|49.962289818|READY|

首次完整READY决策采样在49.926347676；Native wait返回发生于该采样完成与后续confirm开始之间。相对start请求的可核验区间为 **0.149840881–0.155141782秒**。函数返回点没有独立打点，区间代替伪造的精确值。

再次完整验证结束于相对0.185783023秒，ACTUAL_SERVICE_CONFIRMED事件为相对0.195069117秒；两者均远早于14秒上界。C00 probe机器结果为T0+0.681446958秒。

第一轮读取跨度0.031660133秒，第二轮0.033190868秒，确认轮0.030641241秒。READY两轮的unit版本、InvocationID、字段值、目标身份和kernel辅助门一致；pidfd成功仅由冻结路径与无错误结果见证，其单独检查时间未记录。

没有STOP_REQUEST、FAILED或屏障超时事件；正常关闭使用C00_DIAGNOSTIC_COMPLETE，退出时刻见[资源核算](BATCH08_RESOURCE_ACCOUNTING.md)。journal MONOTONIC与Host perf_counter只在各自域计时，不与BOOTTIME混算。
