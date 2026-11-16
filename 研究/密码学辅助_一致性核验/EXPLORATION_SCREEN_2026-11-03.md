# 强独立原创目标下的本轮筛选记录

## Material Passport

origin_skill: academic-research-suite；origin_mode: prior-art-screening-and-theory；origin_date: 2026-11-03；verification_status: UNVERIFIED；version_label: exploration-screen-01；repro_lock: null。

本轮未把“又实现一个算法”作为成功标准。先检查新思路是否已被经典工作覆盖，再保留可独立陈述、能反驳且与主线有联系的问题。尚未宣布强独立密码学原创性达标。

## A. 剔除：把特征二 Hankel 抵消当作新发现

核对发现，不加移位的Hankel稀疏检查在特征二中会出现恒等抵消。例如阈值k=1、系数[1,1,1]时，行列式恒为零。但该现象已在以下工作明确讨论：

Zhiwei Hao、Erich L. Kaltofen、Lihong Zhi，Numerical Sparsity Determination and Early Termination，ISSAC 2016，DOI：[10.1145/2930889.2930924](https://doi.org/10.1145/2930889.2930924)。[作者公开PDF](https://users.cs.duke.edu/~elk27/bibliography/16/HKZ16.pdf)。已取得并阅读第4节相关论证及第6节附录，不能把同类反例包装为本项目原创。

该文还讨论从指数1开始的移位处理，并引用 Kaltofen、Lee 的 Early termination in sparse interpolation algorithms，2003，DOI：[10.1016/S0747-7171(03)00088-9](https://doi.org/10.1016/S0747-7171(03)00088-9)。因此单纯“移位后恢复可靠性”也不能直接作为新密码学机制。

Arithmetic Sketching 的汇总表已标明通常考虑特征大于2，故本轮反例不构成对其该范围结论的攻击，也不是实际系统漏洞声明。[2023论文全文](https://ntt-research.com/wp-content/uploads/2023/08/Arithmetic-Sketching.pdf)

本地原文SHA-256：2229f5fc82fc3cb68308a04c848d4193b5e37e2c325cd77055a14a48968593cb。128次独立行列式计算记录在 results/hankel_scope01。该方向只作为适用性边界及基线修正材料，不列为创新点。

## B. 保留候选：结构限制下的完整可行性与资源刻画

此前结论依赖所有支持都可能出现以及满火花字典。本轮放宽到相关列和声明的支持族，得到：

1. 允许支持包含依赖关系时，线性观察模型满足ε+η≥1：保持位置会造成可完全区分的幅值关系，完美隐藏则迫使抹除。
2. 在无零列的给定字典上，存在完美隐藏且不抹除的掩码，当且仅当每个允许支持都独立。
3. 当允许族是列拟阵的全部独立集，最少掩码行数由最大连通分量秩决定，随机性由各分量GL群基数的乘积决定，并有达到界的构造。
4. 这些条件可以产生绑定策略/世界/约束引用的可检查冲突证书，能够识别把两项独立可变残差错误合并成同一诊断方向的设计。

完整模型、证明与反例见 STRUCTURAL_PRIVACY_2026-11-03.md。这比继续微调两故障乘法次数更贴近“哪些共享/隔离结构允许安全补证”的研究问题。

## C. 仍须承认的先例与负结果

拟阵连通分量、基本回路和直和分解是经典工具；可核对 [Macaulay2官方文档](https://macaulay2.com/doc/Macaulay2/share/doc/Macaulay2/Matroids/html/_components_lp__Matroid_rp.html)。本项目不能把这些对象或独立分块本身作为发明。

若结构已是公开直和，匹配构造就是简单正确的分块组合；没有独立算法优势。本轮的潜在贡献只能落在给定观察模型下的必要条件、完整分布/资源刻画和可检查冲突，而非重新命名分块。

另检索到 Ball等，On the Complexity of Symmetric Boolean Functions in Multiparty Private Simultaneous Messages，2026预印本，[arXiv:2610.21216](https://arxiv.org/abs/2610.21216)。其support privacy指消息分布的支撑相同，与本项目允许泄漏错误位置集合S不是同一个概念。本轮只核对摘要与定义，不能按相同关键词认定它证明了或排除了当前结果。

2026/946共享解码全文缺口仍保留。新增结构定理也可能被评为已有群不变性与拟阵结果的直接推论；定向检索没有排除这种可能性。没有把“搜索不到同名公式”作为原创证明。

## 本轮结论

已剔除一个被先例明确覆盖的方向，保留一个覆盖面更广、与主线配置约束更相关的理论候选，并完成独立有限检查。但当前证据仍不能诚实地宣布“较强独立密码学原创结果已经成立”。

后续关键工作是对结构定理进行独立证明与优先权审查，并检验秘密支持的结构合规如何在相同泄漏和预算下实现。若合规检查代价吞掉全部收益，或者该理论已被现有随机编码结果直接包含，应如实降级，不继续用工程量维持强创新主张。
