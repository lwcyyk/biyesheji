# 原文、定位及证明归属

版本TOPIC-THEORY-1，2026-11-06。本文记录助手实际核读范围；全文取得、助手核读、独立重证和研究者本人阅读分别登记。本轮没有取得研究者的全文阅读声明。所有来源字节最终列于SOURCE_MANIFEST_2026_11_06.json。

## 1. 研究输入与版本

本轮显式授权记录于STRATEGY_2026_11_06.json：允许相关理论，优先紧界、复杂度/参数化结果、可实现性和达到构造。正式主要贡献类型、周期、硬件、数据及导师验收仍为待确认。本轮纸面研究可以直接推进。

INPUT_BINDING_2026_11_06.json绑定五份指定输入。REUSED_READING_INPUTS.json与ADDITIONAL_REUSED_INPUTS.json列出复用字节和原路径。RESEARCH_CONSTRAINTS_BEFORE_2026_11_06.md保存追加前原文，完整字节前缀保留情况见DELIVERY_VALIDATION_2026_11_06.json。

R3_MATH_REVIEW.md与R3_PRIORITY_AUDIT_R3.md仅用于继承原M_r公理、固定绑定距离、资源谱范围和既有优先权边界。历史资源谱、旧机制与CS03数字的证据等级维持原记录；此次没有重新执行历史实验。

## 2. 入口A直接近邻

页码为本地PDF物理页，提取文本以`[PDF_PAGE n]`标识。各PDF对应`*_preflight.json`均为结构检查PASS，PDF字节哈希已逐一绑定。结构预检通过的范围为页结构及解析一致性；数学公式仍依阅读核对。

复用的fomin2021.txt、hamming_norm.txt保持历史字节；本轮带页标提取另存fomin2021_paged.txt、hamming_norm_paged.txt。对应记录见DERIVED_TEXT_RECORDS.json。首轮文档完整性检查识别出提取版本混用，已经分开保存并恢复原复用副本；该项处理仅涉及本输出目录，原来源文件保持原状。

|ID|准确来源、年份及版本|实际阅读与定位|使用范围及限制|
|---|---|---|---|
|COL2019|Fedor V. Fomin、Petr A. Golovach、Fahad Panolan、Kirill Simonov，*Low-rank binary matrix approximation in column-sum norm*，2019，arXiv1904.06141v1，18页。[原文](https://arxiv.org/pdf/1904.06141v1)；column_norm2019.pdf；摘要页版本已保存|摘要、§1方法/关系定义；PDF p4 Definition1，p5问题框及Theorem2；pp9–11代表串、Lemma4及其使用；§4的目标比较|本轮最直接的最大Hamming半径/坐标关系近邻。Theorem2原符号为`m^{O(1)} n^{O((k/ε)^4)}`、成功概率至少`1−2n^{-2}`。原m为串长、n为串数；代入本轮记号时交换长度/点数角色。正式问题使用有序中心tuple，允许重复及未使用中心；本轮未添加非空或互异约束。关键p4/p5已渲染目视核对。未独立重证随机PTAS全证明|
|CAT2021|Fedor V. Fomin、Petr A. Golovach、Nidhi Purohit，*Parameterized Complexity of Categorical Clustering with Size Constraints*，2021，arXiv2104.07974v1，32页；首页声明初版被WADS2021接收。[原文](https://arxiv.org/pdf/2104.07974v1)；fomin2021.pdf|摘要、§1模型，PDF p2 Theorem1、p9重述及证明入口；沿用R3对约束/重复列讨论的记录|总Hamming预算B，`2^{O(B log B)} |Σ|^B (mn)^{O(1)}`。逐行r可以总计mr；原文保证不因此成为g+r的精细界。DP细节没有在本轮重新逐行重证|
|HAM2019|Jiehua Chen、Danny Hermelin、Manuel Sorge，*On Computing Centroids According to the p-Norms of Hamming Distance Vectors*，2019-06-28修订稿，arXiv1807.06469v3，21页。[原文](https://arxiv.org/pdf/1807.06469v3)；hamming_norm.pdf|摘要及PDF pp1–4的p-norm、Closest String、复杂度概述；复用R3版本记录|p=∞对应最大Hamming距离，NP-hard性按原文背景引用。有限p的定理及下界保持原参数，未移作本轮r下界。锚定归约和本轮bounded-search证明单独归属|
|MISS2025|Farehe Soheil、Kirill Simonov、Tobias Friedrich，*Binary k-Center with Missing Entries: Structure Leads to Tractability*，2025作者稿，arXiv2503.01445，28页；取得PDF首页日期2025-03-04。[原文](https://arxiv.org/pdf/2503.01445)；binary_center2025.pdf；取得字节由哈希固定，修订号未另确证|摘要、PDF pp1–5问题/参数与Theorems1.1–1.4；§2 Definition2.1及mask/known-entry图定义；相关算法概述|pp4 Theorems1.1/1.2为`2^{O(k vc+vc² log vc)}poly`及fracture版本；Theorem1.3为`d^{O(tw)}2^{O(k tw)}poly`。完全已知矩阵的mask全1。未独立复核全部DP/ILP证明；其无约束中心没有自动强制R_g。Theorem1.4仅登记为不同参数下的ILP关系，不用于宣称A-E障碍|
|CS2023|Amir Abboud、Nick Fischer、Elazar Goldenberg、Karthik C. S.、Ron Safier，*Can You Solve Closest String Faster than Exhaustive Search?*，2023作者稿，arXiv2305.16878，28页。[原文](https://arxiv.org/pdf/2305.16878)；closest_fine2023.pdf；修订号未另确证|摘要及PDF pp1–3，尤其Theorem1.1及连续/离散中心区分|二元连续中心在维度d下，SETH排除`2^{(1−ε)d}poly(nd)`；本轮没有从该结论制造按半径r的下界。其完整归约证明未独立重推|
|BCC2018|Fedor V. Fomin、Petr A. Golovach、Daniel Lokshtanov、Fahad Panolan、Saket Saurabh，*Approximation Schemes for Low-Rank Binary Matrix Approximation Problems*，2018作者稿，arXiv1807.07156，取得38页。[原文](https://arxiv.org/pdf/1807.07156)；binary_constraints2018.pdf；修订号未另确证|摘要、概述及Binary Constrained Clustering定义，含PDF p4–5|总和目标的近邻和2019关系模型的来源链；未将其算法细节当作本轮已重证结果|
|MIR2018|Jiehua Chen、Danny Hermelin、Manuel Sorge，*A Note on Clustering Aggregation for Binary Clusterings*，arXiv1807.08949v2；2018编号，取得稿版面日期2023-11-10，14页。[原文](https://arxiv.org/pdf/1807.08949v2)；binary_aggregation2018.pdf|摘要、PDF pp1–3引言/定义和Mirkin距离公式|目标为对多个输入二分的Mirkin距离之和，按成对成员关系计费。与原M_r逐请求成员迁移的最大值分别比较；未调用其NP-hard/ETH证明来替代A2|
|CHANGE2013|Jan van den Heuvel，*The Complexity of Change*，2013，arXiv1312.2816v1，28页。[原文](https://arxiv.org/pdf/1312.2816v1)；change_survey.pdf，从R3原样复用|摘要、§1、PDF pp2–4的A-to-B-Path、Path-between-All-Pairs、configuration graph及紧凑可行性检查条件；新提取change_survey_paged.txt|用于比较中间态约束与完整Hamming绑定图。本轮未把综述中的一般PSPACE框架或其他受约束图的定理视作A的直接覆盖。该文为综述，其介绍的原理不作本轮原创|

出版状态采用已取得作者稿及明确记录。缺少已核实的出版方信息时，保持作者稿标识；取得全文不等同于阅读所有证明。

## 3. 入口B：复用原文及本轮使用

更详细的既有读页、作者与版本记录原样保存为INHERITED_B_READING_LOG.md。以下仅列本轮实际依赖的部分。

|来源|版本/链接与本地文件|核对位置及本轮使用|
|---|---|---|
|Marisa Kirisame、Steven Lyubomirsky、Altan Haan、Jennifer Brennan、Mike He、Jared Roesch、Tianqi Chen、Zachary Tatlock，*Dynamic Tensor Rematerialization*|ICLR2021；[arXiv2006.09616](https://arxiv.org/pdf/2006.09616)，dtr.pdf，31页；具体取得版本以复用哈希为准|§2生成依赖/pin/递归重算，PDF p4 Theorems3.1–3.2及offline可重排条件；§7未来工作仅作历史线索。没有把允许重排的offline对照写成同外部顺序的结果|
|Paras Jain等，*Checkmate: Breaking the Memory Wall with Optimal Tensor Rematerialization*|MLSys2020；[arXiv1910.02653](https://arxiv.org/pdf/1910.02653)，checkmate.pdf，15页|§4，PDF pp4–7固定阶段、峰值内存、frontier与目标。静态离线规划能力与在线PRP保证分开|
|Nikhil Bansal、Christian Coester、Ravi Kumar、Manish Purohit、Erik Vee，*Learning-Augmented Weighted Paging*|SODA2022；实际arXiv2011.09076v2，2021-11-09；[原文](https://arxiv.org/pdf/2011.09076v2)，weighted_predictions.pdf，23页|PDF pp2–3 Theorems1.1–1.4、PRP/η_w；§2接口。固定page weights与生成DAG状态相关费用的差别保持；不声称此文已覆盖B-H|
|Zhihao Jiang、Debmalya Panigrahi、Kevin Sun，*Online Algorithms for Weighted Paging with Predictions*|arXiv2006.09509v1，2020；[原文](https://arxiv.org/pdf/2006.09509v1)，weighted_limits.pdf，27页|§1/§2 PRP与更强SPRP、权重下界及适用信息。单位费用、有限依赖锥的B-H需要另作模拟证明才能继承任意权重下界|
|Julien Dallot、Amirmehdi Jafari Fesharaki、Maciej Pacut、Stefan Schmid，*Dependency-Aware Online Caching*|INFOCOM2024作者稿，arXiv2401.17146；[原文](https://arxiv.org/pdf/2401.17146)，dependency_caching.pdf，21页|PDF p5 §3永久驻留闭包及参数定义，p11 Theorem6、p12 Theorem7；本轮不把永久闭包可行域套成仅在生成时需要父节点的模型|
|Jakob Nordström，*Pebble Games, Proof Complexity, and Time-Space Trade-offs*|LMCS9(3:15)，2013；arXiv1307.3913v3；[原文](https://arxiv.org/pdf/1307.3913v3)，pebble_survey.pdf，63页|PDF pp14–15 Definition2.10黑pebbling规则和时间/空间。其余证明复杂度结果保持引用范围外|

本轮B的四节点例为手工合成数学对象。它只反驳永久工作区预留方法；动态工作区算法和一般B-H都未被该例排除。

## 4. 检索记录与缺口

发现页面保存于RETRIEVAL_THEORY_DISCOVERY*.json、RETRIEVAL_A_NEIGHBORS.json与RETRIEVAL_A_COLUMN_NORM.json。关键词包括binary constrained center、binary clustering、local budget、complement closest string及相关matrix approximation。标题检索与目录命中仅用于发现，覆盖结论回到原文定义与定理。

搜索连接器出现传输失败；arXiv后续四项元数据查询出现HTTP429或超时，逐项见RETRIEVAL_FOLLOWUP_QUERIES.json。遇到限额后停止该服务的继续请求，没有通过其他入口绕过该限额。首次2019 PDF下载SSL EOF后的一次成功获取单列保存。上述限制未妨碍本地原文、归约和证明工作。

**优先权状态：UNRESOLVED_PRIORITY。** 已核读原文没有直接给出所写A-E，但后续查证尚有缺口。当前材料支持一个精确的集中证明任务；它们尚不足以宣布A-E为截至2026年已确认开放、首次提出或已成立的理论创新。关键缺口为：是否已有方法对小palette/隐式处置中心的相同精确半径问题给出`2^{O(g²+gr log(gr+2))}poly(mn)`或更强界。检索未命中保留为检索结果。

## 5. 推导和原创性归属

|项目|证据类型/完成程度|
|---|---|
|原M_r固定配置距离、公理及资源谱|INHERITED_CONDITIONAL_RESULT；本轮保留原前提|
|A1与有序受约束q-center的双向编码|DERIVED_COMPLETE_MANUAL；原文提供关系模型|
|A2两根NP-complete|DERIVED_COMPLETE_MANUAL；使用已知Binary Closest String NP-hard基础及标准公共锚工具|
|A3两根r-FPT|STANDARD_TOOLS_WITH_MANUAL_PROOF；定向及有界修复|
|A4受约束中心FPT搜索|DERIVED_GENERIC_BASELINE；从标准bounded search重推，未冒充2019已陈述定理；只提供上界|
|A5至多g−1分离行、r(g−1)例外任务|DERIVED_COMPLETE_MANUAL；初等分离/并集工具；存在性与定位效率分开|
|A-E见证候选枚举目标|CONJECTURE；目标时间、候选规模及量词已写出，候选生成步骤待证明|
|B固定workspace反例|DERIVED_COMPLETE_MANUAL；指定方法的下界，OPT=4；一般强方法分离尚缺|

“完整手工证明”表示推导已写出可逐行检查；独立外审和证明助手验证均未进行。候选机制代码、求解器/验证器实现和新增实验为0。运行的脚本限于文献获取、文本提取、文档链接/JSON/哈希检查。文档工具的UTF-8预检包装问题及解决见DOCUMENT_TOOL_LIMITATIONS.json。
