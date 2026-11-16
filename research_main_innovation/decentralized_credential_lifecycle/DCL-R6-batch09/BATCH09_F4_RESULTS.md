# batch09 F4双实现有界检查状态

Material Passport：DCL-R6-batch09；2026-11-12；F4=UNRUN_RESOURCE_GATE。

冻结f4_dp.py、f4_reference.py、compare.py及runner摘要匹配，代码语义执行0。固定夹具13份、G64生成族64份，h∈{0,1,2}、m∈0…20、压缩开/关、参考重放及十个mutant的运行记录均尚待产生。COST1、CE5_FULL等纸面预期保持输入定义，actual结果为null。

Soundness、Completeness、CostAccuracy、ObservationUniformity、TerminalCorrectness、CompressionCorrectness本轮统一UNRUN_RESOURCE_GATE。PASS_BOUNDED=[]；DP/参考不一致、真实协议反例、变异实际检出均无本轮运行数据。

双实现保留既有逻辑分工：D2-DP使用知识状态与费用递推；TRACE-REF独立枚举共同观察策略并逐具体轨迹解释。压缩开关三方比较及DP策略重放使用同批预算。非法空/部分Post夹具独立分类，完整G64族完成前保留首个未完成编号，已完成单元范围按实际报告声明。

本轮仅做源码/输入字节与AST静态读取；逻辑独立仍需实际运行证据支持，外部人员独立审查保持原责任。D2有限模型条件结论和强G覆盖保持。

[源核验](evidence/FROZEN_HASH_CHECK.json)；[规格索引](evidence/CONTEXT_SOURCE_INDEX.json)；[预算](BATCH09_RESOURCE_ACCOUNTING.md)。
