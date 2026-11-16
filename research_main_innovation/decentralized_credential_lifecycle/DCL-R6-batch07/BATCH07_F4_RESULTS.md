# batch07 F4实际机器检查结果

Material Passport：DCL-R6-batch07；BootContinuity-static-1/r4；真实启动后首次失败；2026-11-11；复跑0。

状态**UNRUN_RESOURCE_GATE**，实际模型启动/搜索/语义状态访问均0，PASS_BOUNDED授予0。资源门在C00服务复核阶段失败，FORMAL未启动。

|冻结范围|实际|
|---|---|
|COST1|UNRUN_RESOURCE_GATE|
|CE5/固定夹具|UNRUN_RESOURCE_GATE|
|D2-DP|UNRUN_RESOURCE_GATE|
|TRACE-REF|UNRUN_RESOURCE_GATE|
|G64|UNRUN_RESOURCE_GATE|
|压缩开关比较|UNRUN_RESOURCE_GATE|
|冻结mutants|UNRUN_RESOURCE_GATE|
|反例重放|UNRUN_RESOURCE_GATE|

候选与独立参考的业务语义隔离要求保持。 冻结文件hash与原始输入匹配只支持版本身份，当前没有有限域完整覆盖、模型反例或运行费用结果。反例数量按“未搜索”记录，不能写作性质成立。
