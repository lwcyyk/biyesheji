# batch05 资源校准实际结果

Material Passport：DCL-R6-batch05；C09Fix-static-1/r1；真实执行后证据分析；2026-11-11；复跑 0。

预检通过；C00–C08 共 9 个冻结 root 机器结果 PASS。真实 C09 入口失败，C10–C12 保持 UNRUN_RESOURCE_GATE；完整校准资格尚待取得。

|case|结果|T0后秒|实际范围|
|---|---|---|---|
|[C00](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/inputs/result_C00.json>)|PASS|0.696116079|入口 kernel/身份/AS/cgroup 与冻结映射谓词|
|[C01](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/inputs/result_C01.json>)|PASS|1.100239295|正常执行与监督器握手|
|[C02](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/inputs/result_C02.json>)|PASS|4.294964805|批量预留、真实内存 child、局部 AS 与 MemoryError 判据|
|[C03](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/inputs/result_C03.json>)|PASS|5.481101063|16 MiB 共享映射、4096 预留与可见操作|
|[C04](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/inputs/result_C04.json>)|PASS|6.102340118|父组 4 tasks；第五 task EAGAIN；pids.events max 0→2|
|[C05](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/inputs/result_C05.json>)|PASS|7.117250748|普通全局/局部并发计数|
|[C06](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/inputs/result_C06.json>)|PASS|9.396951511|预期 timeout/Watchdog 停止|
|[C07](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/inputs/result_C07.json>)|PASS|9.687141365|Controller 预期 exit23|
|[C08](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/inputs/result_C08.json>)|PASS|10.050378332|Watchdog 故障后的冻结拒绝/退出|
|C09H|34 accepted|driver结果19.586482022|合成回归+后续Root独立审查|
|C09|FAIL_ENTRY_PERMISSION|20.861903589首次请求停止|交接NOT_EXERCISED|
|C10–C12|UNRUN_RESOURCE_GATE|—|首次关键失败后停止|

C02：N=32896，预留核心 43.751137 ms；child 生命周期跨度 2.720971054 秒；root 结果在 T0+4.294964805。实际操作 17991，未用 14905 信用保守占用。child 的局部 AS soft/hard 均 100663296 B（96 MiB），VM 快照 100524032 B，RSS 快照 93499392 B；这两个值分别为该 child 快照。

payload 父组本 generation 观察到 charged memory peak=125554688 B（119.738281 MiB），memory.events oom/oom_kill=0；精确 RSS 树峰值未认证。C04 实际 pids.current/max=4/4，拒绝第五 task。原父 AS4 条件仅覆盖授权 payload 边界，Root 管理进程另列外部 TCB。

STOP_REQUEST T0+20.861903589、CLOSED +20.909951317、payload 清空 +20.927591657；Root 管理层等待至约 +300 才退出，final cleanup +300.043546214。完整校准在 300 秒内完成的证据仍缺失；既有较短的 C02 结果仅证明该局部路径。完整校准静态访问上界 62,034≤100,000，当前已运行前缀占用 37,293；后缀运行成本尚未测量。

[C02实际数据](evidence/C02_ACTUAL.json)、[资源观察](evidence/RESOURCE_OBSERVATIONS.json)、[Root生命周期](BATCH05_ROOT_COORDINATOR_RESULTS.md)、[时间线](evidence/RUNTIME_TIMELINE.json)。
