# batch06 C00–C12资源校准实际结果

Material Passport：DCL-R6-batch06；RootIPC-static-1/r4；真实预检/准备记录；动态测试0；2026-11-11。

计划13个C case，实际尝试0、完成0、PASS0，全部UNRUN_PREFLIGHT_FAILED。C00–C08的batch05历史PASS与当前批次资格分别保留；新源码涉及RootIPC，因此当前仍要求重取完整链证据。

|case|本批状态|尝试次数|证据范围|
|---|---|---|---|
|C00|UNRUN_PREFLIGHT_FAILED|0|无当前机器PASS/资源探针记录|
|C01|UNRUN_PREFLIGHT_FAILED|0|无当前机器PASS/资源探针记录|
|C02|UNRUN_PREFLIGHT_FAILED|0|无当前机器PASS/资源探针记录|
|C03|UNRUN_PREFLIGHT_FAILED|0|无当前机器PASS/资源探针记录|
|C04|UNRUN_PREFLIGHT_FAILED|0|无当前机器PASS/资源探针记录|
|C05|UNRUN_PREFLIGHT_FAILED|0|无当前机器PASS/资源探针记录|
|C06|UNRUN_PREFLIGHT_FAILED|0|无当前机器PASS/资源探针记录|
|C07|UNRUN_PREFLIGHT_FAILED|0|无当前机器PASS/资源探针记录|
|C08|UNRUN_PREFLIGHT_FAILED|0|无当前机器PASS/资源探针记录|
|C09|UNRUN_PREFLIGHT_FAILED|0|无当前机器PASS/资源探针记录|
|C10|UNRUN_PREFLIGHT_FAILED|0|无当前机器PASS/资源探针记录|
|C11|UNRUN_PREFLIGHT_FAILED|0|无当前机器PASS/资源探针记录|
|C12|UNRUN_PREFLIGHT_FAILED|0|无当前机器PASS/资源探针记录|

C02批量预留/内存child、C04第五task拒绝、C07/08异常退出、C09交接、C10封闭、C11持久化故障、C12关闭/恢复拒绝全部未触发。本批只有安装前后的冻结slice配置属性：TasksMax=4、MemoryMax=4GiB；运行时AS、task实际归属、charged peak/RSS峰值均N/A。

T0、deadline、stop_at和校准300秒窗口尚未初始化。共同C09H/IPC5000、完整校准62034≤100000、总额1000000/1800秒保持合同数值，动态验证仍待取得。SOURCE/argv/UID/ACL检查的局部通过不会产生RESOURCE_GATE_PASS。

[资源核算](BATCH06_RESOURCE_ACCOUNTING.md)、[最终预检](evidence/PREFLIGHT_FINAL.json)、[实际汇总](evidence/ACTUAL_RESULTS.json)。
