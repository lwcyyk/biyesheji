# 访问、容量与期限重新核算

Material Passport：DCL-R6-FullChain-AdmissionFix；FullChainAdmission-static-1/review-1；2026-11-13；HOST_STATIC_REVIEW_ONLY。


实际全局访问消耗0，T0/deadline/R均null。既有冻结可达完整校准硬界68,498保持；新增原生入口代码固定预付512，因此仅该入口集成时条件界69,010。原生独立检查工作须包含在这笔预付范围内，否则重新核算。

拟将79项主机检查移入未来受控回归时，若最终计费合同明确每job预付32＋Root oracle1、driver入口1，则额外1＋79×33=2,608，合计条件估计71,618，距100,000余28,382。当前收费driver未集成、精确新容量N对应输入/工作量尚未闭合，故actual_new_formal_hard_bound=null；71,618仅供申请估算，完整新上界UNRESOLVED。

79=27新archive＋6旧guard＋10旧MR纯判据＋21新MRoracle＋15变异。两份历史包只读兼容检查单列，历史通过不充当新批回归。当前主机解析/静态测试属于明确授权的无业务检查，预算账创建0。

固定资源：校准100,000/300秒、全批1,000,000/1800秒、提前1740、pre-T0 TCB120、AS1GiB/进程、父TasksMax4。专用fault worker仅在C10结束后占用同父slice一个进程，不增加持久Root角色。

维护archive读取的中央目录预界为1582×N字节（46头＋1024名称＋256extra＋256comment），manifest≤4MiB，流式块64KiB/32KiB，总解压/压缩各32MiB，顺序打开一成员。Python对象常数与RSS峰值尚无原生证书，保持O(N)分析及UNRESOLVED。FD为archive源与一个成员流的顺序包络，解释器内部FD仍待审计。

磁盘包括原件、native ZIP和行政副本；原admin32MiB计数包含native ZIP，不能仅由每个归档32MiB推导整体可容纳。新N还需验证这一字节义务。ZIP构建、两次独立读验、5秒终态读取、30秒行政及完整300秒均保持UNRESOLVED，主机小夹具耗时不能充当原生保证。

[机器算式与未决项](evidence/RESOURCE_RECALCULATION.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。全部原生动态测试UNRUN。
