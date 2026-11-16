# S2接线审查与待授权实施范围

阶段D实际代码差异为0。`solve()`仍保持R06的BACKEND_UNAVAILABLE；没有导入或执行NetworkX。以下为已审定的阶段E最小方案。

1. 只在批准的隔离环境载入固定3.7包，校验版本/导入路径与安装记录；保持无extras、无外部插件后端。S1、数据Schema和独立检查器数学语义保持原样。
2. 保留build_network的原始I/T/c/U/E/D_P、±h需求和min(c_i,h)，C_T使用原值。采用network_simplex分别解m/d，检查结果为精确整数；库公开返回费用和流字典，不直接返回势。
3. 从每个原弧构造全部正容量前/反残量弧，保留原弧身份；加入零费用超源覆盖所有节点，用NetworkX内置Bellman–Ford求势，费用单列。残量负环或无有效势则停止接受该包。
4. 不可行分支用明确指定的成熟最大流/最小割方法取得值v与割S；仅在v<h及独立割核验成立时报告EVIDENCE_CONFLICT。原网络用DiGraph，避免把不支持MultiDiGraph的最大流API误用于残量多弧对象。
5. U空时采用定义上的空流/零费用边界，保留原C_T；T空仅出空目标scope。一般非空核心案例必须真正调用库，不能以边界特判代替验收。
6. 向现有assemble_*接口交付流/势/割和绑定，检查器独立重建。库版本/性能信息放结果外层，不扩展或弱化dsat-proof/1数学字段。

现有solve签名允许最小向后兼容扩展，例如关键字bindings；缺绑定时仅返回数学结果/向量，不伪造原生证据。取值超限返回UNKNOWN_RESOURCE_LIMIT，不删边/见证。原生资格始终保持SOURCE_OR_REFINEMENT_GAP，O不被真实写回。

## 需批准的文件范围

- src/auth_lifecycle/online_state/dsat_flow.py：加载成熟后端、自动证明与分项计时。
- tests/test_dsat_projection.py、tests/test_dsat_certificate.py：保留原77项，缺库路径用受控模拟覆盖，原SKIP改成真实自动求解及独立检查；新增明确登记的纯S2反例。
- scripts/run_dsat_offline_tests.py：若实际需要，最小调整依赖导入审计/结果记录，仍只运行指定离线模块。
- 依赖锁/安装收据及R07合成证明/结果资料。

独立检查器保持标准库且不导入求解器；仅发现真实缺陷时按最小反例另限定修复。阶段E尚未获准，本轮未改以上文件。
