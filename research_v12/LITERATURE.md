# 文献定位与原创性边界

本轮 web 搜索连接两次失败；改用官方原文 URL 抓取并保存 literature/。抓取成功不等于阅读完成。一次 NeurIPS URL 返回 MEST 稀疏训练论文，判定为错配并排除，不列入先例依据。CEGAR PDF 请求失败；Transition dominance 的 Dagstuhl 页面连接失败，不编造全文能力。

|工作|年份/可核实定位|实际阅读范围|对主张的影响|
|---|---|---|---|
|The Value Equivalence Principle for Model-Based Reinforcement Learning|2020，https://arxiv.org/abs/2011.03506 ，DOI 10.48550/arXiv.2011.03506|原文摘要、§1—3（含定义及命题陈述），未全面核对附录证明|以规划用途限制模型等价早已有之；A4 全分支义务/批准的证书条件是领域化充分条件，不能声称发明价值保持抽象|
|Multi-Cost-Bounded Reachability Analysis of POMDPs|2025，https://proceedings.mlr.press/v286/bork25a.html|官方元数据、原文摘要及§1/部分§1.1|多维实际资源约束和部分成本可观测已有直接近邻；本轮全分支有限鲁棒目标与概率可达目标不同，不能据此推断对方不能处理认证实例|
|Near Optimal Bayesian Active Learning for Decision Making|2014，https://proceedings.mlr.press/v33/javdani14.html|官方元数据、原文§1—2；旧阅读记录另保留|重叠决策域/超边冲突是经典工具；三世界冲突不是新理论。原文固定假设到测试结果的映射不能未经重证移到有状态故障核验|
|Solving logic-based benders decomposition master problems with constraint programming and domain-independent dynamic programming|2025，DOI 10.1007/s10601-025-09382-1|出版社摘要、元数据、可用性说明及参考文献；付费全文未读|组合可行性 cut、状态约束和前置条件编码已有；AB3 proof replay 不能凭名称认定超越 LBBD|
|Z3 Guide: Basic Commands|官方持续更新文档，https://microsoft.github.io/z3guide/docs/logic/basiccommands/|包括 Using Scopes 的正文|push/pop 是标准成熟功能；本轮增量基线真实使用该机制，不以重新启动求解器冒充增量|
|Safe Reinforcement Learning via Shielding under Partial Observability|2023，DOI 10.1609/aaai.v37i12.26723|沿用 v1.1 经核验的§3.1—3.3、§4.1脚注；本轮未再宣称全文阅读|belief-support 安全筛选与有限时域屏障并非本轮原创|
|Enforcing Almost-Sure Reachability in POMDPs|2021，DOI 10.1007/978-3-030-81688-9_28|沿用 v1.1 摘要与引言范围|almost-sure 和全允许结果有限完成不同，比较须同目标|
|Logic-based Benders decomposition|2003，DOI 10.1007/s10107-003-0375-9|沿用 v1.1；本轮不提升阅读等级|分解、证据依赖和条件 cuts 的经典来源|
|Tactics for Account Access Graphs|2024出版/ESORICS2023，DOI 10.1007/978-3-031-51479-1_23|沿用 v1.1 作者稿选定章节|账户图转换与接口前置条件是近邻；缺乏逐实现匹配时不能写成对方没有|
|Transition dominance in domain-independent dynamic programming|2025，Zhang/Beck出版社参考文献给出作者与题名；本轮直接原文请求失败|仅二手书目线索|与 B4 支配/压缩接近，优先权仍未决；不把待核实 DOI 写成已验证|

UAI 页面为 PMLR 286；抓取 PDF 首页页脚出现 244，登记为来源内不一致，书目信息采用官方卷页面，不静默“修复”原件。

具体可主张范围：A4 有比完整轨迹等价更弱的可检查充分条件与正例；B4 有固定模型下的类数参数压缩和全局字典序证明；AB3 有完整动态 Post 上的证书重放与失败闭合实现。通用方法获得同一机制即可复现相应行为，因此三项均未排除成熟通用方法等效，不能确认强独立原创性。新研究价值需在更有代表性的结构、原生语义来源和端到端成本上继续建立。
