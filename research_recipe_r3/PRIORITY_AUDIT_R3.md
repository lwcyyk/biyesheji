# 完整资源节省谱的优先权核查

核查日期为2026-11-04。判定对象为单任务原子重绑、既有独立根计费模型中的完整谱命题。固定签名数k≥2和预算r≥1，允许有限任务数及同签名重数变化，资源节省恰取遍0至k−2。当前总判定为**近邻未决**。

## 1 判定规则与取得范围

“已覆盖”要求从原文明确命题经符号对应即可导出完整谱、全部参数量词与紧性。“近邻但未覆盖”表示核读的原文结果与该谱之间仍需新增问题映射、构造或证明。“未决”用于全文缺失、版本不清或尚未核读的分支。后两类均保留继续发现先例的可能。

本轮取得12项全文，阅读重点为问题定义、约束、优化目标、主要命题和与谱构造相关的证明。逐篇阅读范围列于下文，用户人工阅读状态未作推定。数学共同工具的优先权分别登记，谱命题的优先权以整体量词和结论判定。

检索工具发生传输失败，改用arXiv官方检索、作者页面、官方摘要页和原文下载。查询包含categorical clustering、constrained clustering must-link、cluster editing anchors、reconfiguring partitions、partition distance、revocation cost、role revocation、role mining。检索覆盖受索引、关键词和版本限制。原始检索页、下载记录、PDF与提取文本保存在sources目录，文献登记同时写入LITERATURE_REGISTER.json。

## 2 Categorical clustering与Hamming近邻

### P01 Fomin、Golovach、Purohit

**Parameterized Complexity of Categorical Clustering with Size Constraints**，2021，arXiv 2104.07974v1。本轮复用R2从arXiv取得的32页全文，两份PDF的SHA256一致，并扩读§1、§2.1—2.3、§3.1的Observation 1—4与Lemma 1—4、主要定理陈述，以及§4—5的Observation 6、Lemma 9—12和Theorem 4。§3.2详细动态规划未逐行复核。[原文](https://arxiv.org/abs/2104.07974v1)

对应关系可精确写为停止矩阵A的列对应任务，列簇对应初始根，中心在一行上的字符对应该根的终态停留标签。固定簇的多数字符最小化Hamming误差，直接覆盖本项目距离计算的基本工具。重复列和大重类迫使中心取值也属于已有计数方法。

仍需加工的部分有三项。

1. 原文以全部列到中心的总Hamming成本为预算，本项目要求每个备选请求行的误差分别≤r。误差向量(2,0)和(1,1)总和相同，在r=1时可行性不同。
2. 本项目每个非平凡请求必须同时具有可用的停止根和保留根。一行两列[0,1]置于单簇时，普通Hamming中心成本为1，本模型的单既有根距离为∞。两根各含一停二留时，逐根多数成本为2，带两标签约束的距离为3。
3. 原文核读结果主要给出既定簇数下的算法、核化与复杂度。本项目谱还需固定k、r后，针对每个目标根数构造需求族，并排除所有更小的共同初始配置。

判定为**近邻但未覆盖**，限于上述原文命题。多数距离、重数放大与鸽巢原理应明确归于通用工具。完整谱仍可作为待确认优先权的刻画结果。

### P02 Chen、Hermelin、Sorge

**On Computing Centroids According to the p-Norms of Hamming Distance Vectors**，2018初稿，取得2019修订版arXiv 1807.06469v3。读取§1问题定义、§2 Theorem 1及其构造入口、§3 Theorem 2—3与Proposition 3、§4总结。复杂度证明的全部技术细节未逐行重证。[原文](https://arxiv.org/abs/1807.06469v3)

该文的p=∞情形明确对应最大Hamming距离受限的Closest String。由此，“将总误差换成最大误差”本身也有成熟先例。其变量为一个公共中心字符串，本项目选择共同任务分组并允许每个请求另选根标签，含付费空根与两标签可用性。要从单中心结果导出资源谱，需要重建变量、可行域和构造。判定为**近邻但未覆盖**，同时收回任何把最大误差预算本身视为新工具的解释。

## 3 相关性、半监督与约束聚类

### P03 Wagstaff、Cardie、Rogers、Schrödl

**Constrained K-means Clustering with Background Knowledge**，2001。取得作者提供的8页PDF，读取摘要、§2—3的must-link/cannot-link定义及COP-KMeans过程。[作者全文](https://www.wkiri.com/research/papers/wagstaff-kmeans-01.pdf)

must-link将一对对象限定在同簇。M_r中的同签名类允许拆到多个根，其大重数通过移动预算产生必要根占据，直接把它替换为must-link会缩小可行配置集合。该文以距离聚类和硬约束为核心，核读部分未给逐请求迁移预算下的根数谱。判定为**近邻但未覆盖**。

### P04 Bibi、Alqahtani、Ghanem

**Constrained Clustering: General Pairwise and Cardinality Constraints**，2019初稿，取得arXiv 1907.10410v2，版面日期2023-01-27。读取§I—III、式(1)—(7)、Proposition 1—2与ADMM约束化表达。[原文](https://arxiv.org/abs/1907.10410v2)

该文将pairwise与cardinality约束编码到聚类优化。固定基数约束与重数设计存在工具联系，平方欧氏目标及硬配对约束仍与每行最少迁移量不同。原文命题没有直接给本项目量词下的完整谱，判定为**近邻但未覆盖**。PDF中的DOI字段为模板占位符，本登记仅引用arXiv版本。

### P05 Bansal、Blum、Chawla

**Correlation Clustering**，FOCS 2002会议版，期刊版发表于2004年。最初两个PDF候选地址失败，随后从作者论文索引找到clustering.ps，取得10页全文并在R3内转换为PDF。阅读摘要、§1定义及贡献陈述。部分数学字符提取为字体编码，比较依据限于可辨识的定义与文字陈述。期刊DOI与出版信息由作者索引核实，取得的本地全文按会议稿登记。[作者原稿](https://www.cs.cmu.edu/~avrim/Papers/clustering.ps) [期刊入口](https://doi.org/10.1023/B:MACH.0000033116.57574.95)

该问题最小化正边被分开及负边被合并的总数，簇数随优化结果变化。项目D计算任务要求与根标签的不一致成员数。边代价与成员代价需要额外归约，资源目标也不同。读取的原文结果为近似算法及相关复杂度，判定为**近邻但未覆盖**。此次取得全文使该会议稿从获取未决转为已核读，期刊扩展版的新增结果仍需另核。

### P06 Adriaens

**CKR Partitions and Lower Bounds for Constrained Correlation Clustering and Variants**，2026，arXiv 2608.08291v2。读取§1及§1.1—1.2、§2归约的题目与目标、§3的LP_CCC及CKR-PIVOT定义、Theorem 1.1、§4讨论。[原文](https://arxiv.org/abs/2608.08291v2)

LP_CCC以成对距离变量表达must-link、cannot-link和三角约束，优化边不一致总和。文中确有约束聚类近似和困难性结果，也讨论多层情形。它们要求额外问题转换才能处理共同初始根、逐请求任务迁移预算及计费空根，完整谱构造仍需另证。判定为**近邻但未覆盖**，多层/局部相关性聚类文献的全文追溯保留未决。

### 该分支保留的风险

固定锚点、允许成员重分配且控制每层误差的聚类问题，可能比本轮取得的通用pairwise约束论文更近。anchors检索结果有较多无关应用，当前证据不足以排除全部锚定聚类与cluster editing分支。由“可归约为某类CSP或整数规划”只能确认可表达性，完整谱是否已在该类的具体定理中出现仍需逐篇核验。

## 4 组合重配置与分区距离

### P07 van den Heuvel

**The Complexity of Change**，2013，arXiv 1312.2816v1。取得全文，读取§1的重配置定义、给定端点可达性、所有对连通性与距离框架，检查与一步修改相关的讨论。[原文](https://arxiv.org/abs/1312.2816v1)

单步重绑可作为重配置图的一条边，预算对应路径长度，这一抽象属于既有框架。谱命题还要求先选一个共同起点，再对所有请求分别选合适终点，并按可用根数优化。原文框架能够容纳此问题，完整谱需专门构造。判定为**近邻但未覆盖**。

### P08 Akitaya等

**Reconfiguration of Connected Graph Partitions**，2019初稿，取得arXiv 1902.10765v3的2026版PDF。读取模型、1-switch定义及主要定理陈述，涵盖Theorem 5、8、9、17、20、22、23、24、29。比较仅使用取得PDF的定义，复杂度定理的全部证明未重证。[版本入口](https://arxiv.org/abs/1902.10765v3)

该文要求非空连通district，并按图邻接进行单点迁移。本模型允许计费空根、完全迁移资格和一族满足标签的终态。连通性、非空性与目标集合均需实质改写。判定为**近邻但未覆盖**。

取得的PDF与摘要页在作者列表及NP/PSPACE措辞上存在差异，登记保留两个文件和摘要，复杂度结论与作者全表待版本核对。此差异使跨版本命题合并需要额外校验。

### P09 Rossi

**Partition distances**，arXiv 1106.4579v1，版本标识2011。PDF封面另有2018编译日期，引用按arXiv版本保留。读取§2式(2)及分区距离定义、Claims 10—12与结尾极值讨论。[原文](https://arxiv.org/abs/1106.4579v1)

标准partition-distance可由删除最少成员后使两分区诱导结构一致来定义，端点是两个确定分区。M_r的终点允许任意满足停留标签的细分结构。例取四单例初始分区与S={a,b}，直接撤销a、b对应根即可，M_r距离为0，而到精确二分区{{a,b},{c,d}}的该标准距离为2。把终态固定成精确二分区会改变问题。原文的距离极值与本项目根数预算谱仍需额外加工，判定为**近邻但未覆盖**。

### P10 Nishimura相关综述线索

2018年Algorithms卷11第4期文章52的PDF入口返回403。本轮取得范围不足以独立核实全文标题、章节和命题，登记为**未决**。该项只作为待取文献线索，概括性覆盖判断留待全文。[获取入口](https://www.mdpi.com/1999-4893/11/4/52/pdf)

## 5 访问控制中的撤销与成员代价

### P11 Blundo、Cimato

**Constrained Role Mining**，2012，arXiv 1203.3744v1。读取RBAC矩阵定义、Problem 2.1—2.3、Theorem 2.1—2.3陈述及相关工作。[原文](https://arxiv.org/abs/1203.3744v1)

角色挖掘允许用户同时拥有多个角色，权限由Boolean OR组合。M_r要求任务在每一状态恰有一个当前支持，优化一次首次停止请求下的根资源。原文含约束和角色数优化工具，逐请求迁移预算与全谱仍需新映射。判定为**近邻但未覆盖**。其Vertex Cover相关近似论断需要另行审查，本项目未借用这些论断支持复杂度结论。

### P12 Tripunitara

**Minimizing the Number of Roles in Bottom-Up Role-Mining using Maximal Biclique Enumeration**，2024，arXiv 2407.15278v1。读取§1、§3问题定义与Theorem 1、Theorem 2—3陈述及biclique cover对应。[原文](https://arxiv.org/abs/2407.15278v1)

最少角色与最少根在资源计数层面近似，角色的多重覆盖和授权合成规则具有不同可行域。原文的最大双团枚举和覆盖结论不能只经符号更名导出逐请求重绑谱，判定为**近邻但未覆盖**。

### P13 Garrison、Shull、Myers、Lee

**On the Practicality of Cryptographically Enforcing Dynamic Access Control Policies in the Cloud (Extended Version)**，2016，arXiv 1602.09069v3。读取§III假设、§IV构造、revokeU伪代码、§V-D撤销成本与图5相关讨论。[原文](https://arxiv.org/abs/1602.09069v3)

该文直接量化撤销用户角色成员资格所需的重发密钥、重加密和相关更新。因此“撤销引起成员关联材料迁移成本”已有安全领域先例。其成本为密码运算、密钥版本与文件操作，完整资源谱的指标为既有独立根数，预算为逐任务原子重绑次数。核读命题没有直接提供本谱，判定为**近邻但未覆盖**。

### P14 Revocations—A Classification

2001年文献，DOI入口返回0字节。retrieval01.json中最初的RETRIEVED是获取程序把空响应计为成功造成的记录错误。本次归一化登记为**EMPTY_RESPONSE / 全文未取得 / 未决**，原始获取记录保留以便追溯。[DOI入口](https://doi.org/10.1109/CSFW.2001.930135)

论文标题与书目线索来自历史优先权记录，当前正文读取范围为空，任何关于其命题是否覆盖资源谱的结论均待全文。

## 6 与上一轮近邻的衔接

Tactics的账户图操作、root-scoped quiescence的重绑支持和撤销闭包、通用重配置及Hamming工具继续按已有原理登记。RAG作者稿的历史获取仍为403，全文覆盖保留未决。本轮集中处理用户指定的四类风险，R2其他文献的读取记录沿用原有证据层级。[上一轮核查](D:/毕业设计/research_recipe_r2/PRIORITY_AUDIT.md)

当前最接近固定距离工具的是P01，最接近预算聚合方式的补充来源为P02，最接近撤销成本领域建模的来源为P13。谱命题的候选增量集中在固定k、r后的精确全值、紧性和共同初始配置量词，认证术语与通用距离计算均不承担原创性主张。

## 7 最终判定与可改变判定的证据

当前选择**近邻未决**。在本轮实际核读的12项全文中，尚未定位到无实质加工即可推出完整谱的命题。固定锚点/局部误差聚类、若干重配置综述、撤销分类和RAG全文仍有取得或核读缺口，故“近邻已排除”尚无充分依据。

如发现原文已经同时给出固定签名数、任意正迁移预算、计费可用根和全部0至k−2值的构造与下界，应降级为已有结果的领域实例化。如新增文献只覆盖多数距离、重数迫使标签或重配置框架，应引用该工具并继续单独审查整体谱。

论文当前可使用“条件性完整资源谱定理”和“优先权待核实的数学贡献候选”。首次、独创及优于通用动态算法的表述需额外证据。数学正确性和原生前提分别见MATH_REVIEW.md及NATIVE_PREMISES.md。
