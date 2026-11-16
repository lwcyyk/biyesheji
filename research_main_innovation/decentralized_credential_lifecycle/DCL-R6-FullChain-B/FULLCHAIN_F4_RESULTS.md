# F4动态规划与独立参考检查

Material Passport：DCL-R6-FullChain-B；2026-11-13（Asia/Shanghai）；审查基线 RuntimeAdapt-static-1/r1 / ra01；仅主机静态审查；BLOCKED_STATIC_ADMISSION。


F4实际执行0，状态UNRUN_RESOURCE_GATE；Soundness、Completeness、CostAccuracy、ObservationUniformity、TerminalCorrectness、CompressionCorrectness均无当前PASS_BOUNDED证据。

静态输入清单为13个fixture：COST1、CE5_FULL、COMP_SAME_X、EMPTY_POST_INVALID、PARTIAL_POST_INVALID、OPEN_UNKNOWN、NONUNIFORM、REAL_QUERY_COST、ZERO_INTERNAL、PREFIX_BAD、VISIBLE_COST、QUOTA_MODE、MISSING_OBSERVATION。G64来自16组费用×2个替代成本×2种可见性，共64；总77个基线游戏。此处为源码计划计数，输入构造函数执行0。

每个游戏计划h∈{0,1,2}、m∈{0,…,20}，普通DP与compression分别比较；参考solve按具体策略表/轨迹独立穷举，DP可行证据由REF.interpret重放。DP.decide和REF.solve各在输入状态验证前预付len(states)访问，语义文件字节隔离保持。计划10项mutant包括stagewise_max、drop_mode、两种empty_post、ignore_unknown、worldwise、zero_query_cost、ignore_prefix、drop_permission和omit_observation。

当前耗时、访问、参考策略数量、DP/REF一致性、压缩比较与最小反例均UNRUN；业务轨迹文件数量0。计划域和既有设计假设保留其研究边界。

本轮动态用例0、WSL调用0、部署0、active entry0、目标模块导入0、源码修订0、重跑0。T0/deadline/R均为null；新增访问消耗0。历史结果单独引用。

[冻结比较器](evidence/FROZEN_RA_ORIGINALS/src/compare.py) · [DP](evidence/FROZEN_RA_ORIGINALS/src/f4_dp.py) · [独立参考](evidence/FROZEN_RA_ORIGINALS/src/f4_reference.py)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
