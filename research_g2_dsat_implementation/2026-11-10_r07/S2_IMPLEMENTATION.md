# S2实际实现

完成批准范围内NetworkX3.7整数流薄适配，不包含新的优化算法或原生操作。

`solve(math_input, limits=DEFAULT_LIMITS, *, bindings=None)`保持旧位置参数/构图字段，新增可选绑定。加载前核包路径位于隔离环境、版本固定3.7；缺包/环境不符仍BACKEND_UNAVAILABLE。

保留±h需求、m/d费用与min(c_i,h)，C_T按原容量计算。两个非空模式实际调用内置network_simplex，校验整数流、容量/守恒与费用；空U按定义给空流/零费，原C_T保持。边界特判没有代替非空核心验收。

完整残量MultiDiGraph保留原弧身份与前/反方向，零费用超源覆盖全部节点，内置Bellman–Ford生成整数势并核约化费用。不可行用显式内置Edmonds–Karp取得最大流与最小割；v=cut<h才报告EVIDENCE_CONFLICT，R/H未定义。无法证明不足割返回UNVERIFIED_INFEASIBILITY；负环/坏势停止接受；超限不截输入求解。

绑定存在时调用原assemble_*产生dsat-proof/1，无绑定只给数学向量。库信息/分项计时放结果外层。KEEP_EXISTING、真实native_admission=SOURCE_OR_REFINEMENT_GAP和global_complete=false保持；独立检查器自行建图/验证，源码未改。

实际只修改4份批准文件：dsat_flow.py、两个DSAT测试、runner依赖审计/记录。S1、dsat_types、检查器、test helper和25份夹具不变。R06八份原代码已归档sources/R06_CODE_SNAPSHOT；差异见CODE_DIFF.json/patch。

新增24项自动案例路径与14项S2专项；原77项身份全部保留。原SKIP现调用真实m/d及独立检查，缺库行为用受控模拟覆盖。runner仍只加载两个指定模块，NetworkX导入仅批准给dsat_flow。没有改运行权威/Provider、旧协议或A/B/AB算法。
