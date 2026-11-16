# batch06 F1实际有界检查结果

Material Passport：DCL-R6-batch06；RootIPC-static-1/r4；真实预检/准备记录；动态测试0；2026-11-11。

实际状态 **UNRUN_RESOURCE_GATE**。入口在最终预检时停止，FORMAL及业务模块启动0；模型搜索0、状态/语义访问0，PASS_BOUNDED授予0。

|冻结检查范围|实际|
|---|---|
|SMOKE|UNRUN_RESOURCE_GATE|
|BRANCH|UNRUN_RESOURCE_GATE|
|CHAIN|UNRUN_RESOURCE_GATE|
|KEY|UNRUN_RESOURCE_GATE|
|指定mutants|UNRUN_RESOURCE_GATE|
|反例重放|UNRUN_RESOURCE_GATE|
|INV1–INV8|UNRUN_RESOURCE_GATE|

模型反例计数为“未搜索”，覆盖率/状态空间/运行时间保持N/A。旧钥、历史责任、预算、ReadyState/ReadyUse及迟到IO冻结边界保持。 source与正式输入hash匹配仅证明冻结版本，当前没有新有界性质通过证据。

[实际结果](evidence/ACTUAL_RESULTS.json)、[资格失败](BATCH06_FINAL_DECISION.md)、[执行锁](evidence/execution_lock.json)。
