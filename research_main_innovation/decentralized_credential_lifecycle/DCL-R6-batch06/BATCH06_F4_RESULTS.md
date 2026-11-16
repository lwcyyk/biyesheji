# batch06 F4实际有界检查结果

Material Passport：DCL-R6-batch06；RootIPC-static-1/r4；真实预检/准备记录；动态测试0；2026-11-11。

实际状态 **UNRUN_RESOURCE_GATE**。入口在最终预检时停止，FORMAL及业务模块启动0；模型搜索0、状态/语义访问0，PASS_BOUNDED授予0。

|冻结检查范围|实际|
|---|---|
|COST1|UNRUN_RESOURCE_GATE|
|CE5/固定夹具|UNRUN_RESOURCE_GATE|
|D2-DP|UNRUN_RESOURCE_GATE|
|TRACE-REF|UNRUN_RESOURCE_GATE|
|压缩开关对照|UNRUN_RESOURCE_GATE|
|G64|UNRUN_RESOURCE_GATE|
|指定mutants|UNRUN_RESOURCE_GATE|
|反例重放|UNRUN_RESOURCE_GATE|

模型反例计数为“未搜索”，覆盖率/状态空间/运行时间保持N/A。独立参考语义和候选后继/终态隔离要求保持。 source与正式输入hash匹配仅证明冻结版本，当前没有新有界性质通过证据。

[实际结果](evidence/ACTUAL_RESULTS.json)、[资格失败](BATCH06_FINAL_DECISION.md)、[执行锁](evidence/execution_lock.json)。
