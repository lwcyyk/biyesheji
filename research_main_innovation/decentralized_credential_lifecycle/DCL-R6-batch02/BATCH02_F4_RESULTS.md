# batch02：F4结果

2026-11-10。Material Passport：MODEL_CHECK_UNRUN。DP、TRACE-REF和比较器未被正式导入/运行。

|性质/族|实际状态|
|---|---|
|P1 Soundness|UNRUN_RESOURCE_GATE|
|P2 Completeness|UNRUN_RESOURCE_GATE|
|P3 CostAccuracy|UNRUN_RESOURCE_GATE|
|P4 ObservationUniformity|UNRUN_RESOURCE_GATE|
|P5 TerminalCorrectness|UNRUN_RESOURCE_GATE|
|P6 CompressionCorrectness|UNRUN_RESOURCE_GATE|
|13固定夹具，包括COST1/CE5/前缀/UNKNOWN等|UNRUN_RESOURCE_GATE|
|G64，h0..2、m0..20，压缩开关/独立参考|UNRUN_RESOURCE_GATE|
|10个原mutant、策略/费用/观察重放|UNRUN_RESOURCE_GATE|

Gate B02-4=UNRUN；实际DP/参考单元、具体轨迹、变异命中数均无值，访问0，PASS_BOUNDED为空。源码与原夹具构造字节保持，D2有限模型的纸面条件结论不因本次资源失败改变。

当前没有任何候选/参考差异，也没有已证实参考正确性的动态结果。后续需先解决资源资格，届时仍按原确定性顺序/完整输入域和独立语义比较。
