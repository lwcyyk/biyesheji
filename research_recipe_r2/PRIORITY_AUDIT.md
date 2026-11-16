# 优先权核查记录

核查日期为2026-11-04。当前允许的表述包括条件性定理、有限模型核验和版本限定的原生测量。首次性与独立原创性按下表逐项登记。

## 1 主张判定

|编号|拟主张内容|核查结果|允许表述|
|---|---|---|---|
|P1|固定分区的最少重绑距离|与二值簇中心的逐坐标多数代价密切对应，通用原则已有先例|M_r下的准确刻画与语义对应|
|P2|重绑预算的静态退化、紧界和全部节省谱|本轮给出完整证明，等价数值谱的文献优先权仍未决|条件性资源谱定理，原创候选|
|P3|根切断、在途派生、提交fence和独立支持重绑的形式化首次|root-scoped quiescence原文直接覆盖这些要素|已有结果的OAuth领域实例化与测量衔接|
|P4|时变分区相对通用静态展开的求解理论优势|同语义状态图可展开，通用DAG共享复现表示节约|有限表示规模分析|
|P5|首次系统实证揭示撤销平台差异|RFC已描述若干差异来源，既有测量文献的全面核验尚有缺口|两个指定版本的可追溯受控测量|
|P6|共享账户根处置后的并发刷新存活实测|现有并发脚本调用旧RT revoke，范围不匹配|局部RT撤销与刷新竞争的内省轨迹|

## 2 动态重绑的近邻

### 2.1 Categorical Clustering

Fedor V. Fomin、Petr A. Golovach、Nidhi Purohit，Parameterized Complexity of Categorical Clustering with Size Constraints，2021预印本，arXiv:2104.07974v1。取得32页原文，阅读摘要、§1、§2.1及§2.2。Observation 1明确给出固定聚类后按多数规则选择Hamming中心。本文引理2与此原则具有直接联系。[原文](https://arxiv.org/abs/2104.07974)

设停止矩阵A的行为需求、列为任务，初始根绑定对应列的分组，U给每行各根标注停留命运。本文约束每一行的不一致数至多r，并要求非平凡行具有两种可用根命运。该文读取范围中的目标为全部Hamming距离之和。相同总误差可分布成(2,0)或(1,1)，两者在逐行上限1下具有不同可行性。精确预算位置需要继续与逐维约束聚类核对。

因此多数代价计算按通用原则登记。完整节省谱的优先权保留未决，新增认证字段不计入新颖性。

### 2.2 Tactics for Account Access Graphs

Luca Arnaboldi、David Aspinall、Christina Kolb、Saša Radomirović，Tactics for Account Access Graphs，ESORICS 2023会议、2024出版，DOI 10.1007/978-3-031-51479-1_23。取得20页作者稿，核对§2、§3.1—3.3、Definition 5和Proposition 1。原文提供账户图状态、访问变更和tactic执行语义。[作者稿](https://www.pure.ed.ac.uk/ws/portalfiles/portal/478371898/ArnaboldiEtalESORICS2023TacticsForAccountAccessGraphs.pdf)

本轮谱定理的指标为既有根数、逐请求迁移预算与签名类重数。一般动态图操作的优先权归于既有工作。该精确数值谱的等价覆盖仍需逐命题核查。

### 2.3 RAG

Freya Murphy、Saša Radomirović，Verifying Account Ecosystems With Graph Transformations，2026，DOI 10.1109/EuroSP68448.2026.00038。机构页面确认动态图重写、CTL和GROOVE分析。作者稿链接此次仍返回HTTP403。阅读层次为摘要与元数据，完整命题覆盖登记为未决。[机构入口](https://researchportal.hw.ac.uk/en/publications/verifying-account-ecosystems-with-graph-transformations/)

### 2.4 Hamming范数近邻

Jiehua Chen、Danny Hermelin、Manuel Sorge，On Computing Centroids According to the p-Norms of Hamming Distance Vectors，2018初稿、2019修订，arXiv:1807.06469v3。当前核对官方摘要与元数据。其对象是字符串到一个中心的距离向量范数。全文等价关系尚未核查，作为进一步排查逐维预算的入口保留。[元数据](https://arxiv.org/abs/1807.06469)

## 3 并发撤销的直接覆盖

### 3.1 Root-Scoped Quiescence

Genliang Zhu、Chu Wang，Authorization Revocation for Long-Running AI Agents: Root-Scoped Quiescence under Delegation and Asynchronous Execution，2026预印本，arXiv:2609.21284v1。取得39页原文，阅读§1—2、§4的定义和假设、§5的协议步骤，以及Appendix A.3的对应证明。[原文](https://arxiv.org/abs/2609.21284)

该文明确绑定根代次、切点、接收端fence、在途载体及重绑支持，并给出条件性闭包与组合结果。因此这些原理按已有结果登记。本文保留OAuth轨迹的范围核对、有限契约规格及静态分区定理的适用边界。原文取得不等于其完整工件已复现。

### 3.2 Linearizability

Maurice P. Herlihy、Jeannette M. Wing，Linearizability: A Correctness Condition for Concurrent Objects，1990。取得作者机构提供的全文，阅读摘要、§1与§2定义。并发请求的响应顺序与抽象操作的线性化顺序需区分。[原文](https://cs.brown.edu/~mph/HerlihyW90/p463-herlihy.pdf)

这一原则直接限制对Casdoor日志的解释。当前客户端事件能证明请求重叠及观察先后，服务端事务线性化点仍需额外证据。

### 3.3 Zanzibar

Ruoming Pang等，Zanzibar: Google’s Consistent, Global Authorization System，USENIX ATC 2019。取得会议全文并核对摘要、外部一致性说明及相关工作中的一致性讨论。授权状态更新与检查之间的时序保证已有直接系统先例。[会议入口](https://www.usenix.org/conference/atc19/presentation/pang)

### 3.4 OAuth规范

RFC7009（2013）的§2.1讨论相关令牌撤销策略与传播窗口，RFC7662（2015）的§2.2及§4讨论查询者语境和资源缓存，RFC9700（2025）的§4.14.2讨论刷新令牌轮换与关联信息。这些内容沿上一轮已核实原文继续使用。[RFC7009](https://www.rfc-editor.org/rfc/rfc7009.html) [RFC7662](https://www.rfc-editor.org/rfc/rfc7662.html) [RFC9700](https://www.rfc-editor.org/rfc/rfc9700.html)

## 4 THO24与GLOV26的准确身份

|缩写|核实题名与版本|本轮阅读范围|覆盖状态|
|---|---|---|---|
|THO24|Chosen-ciphertext secure code-based threshold public key encryptions with short ciphertext，Takahashi、Hashimoto、Ogata，2024卷期，在线发表2023|官方题名、作者、摘要及开放全文入口|摘要主题为码基阈值PKE，完整等价覆盖未决|
|GLOV26|Threshold Niederreiter: chosen-ciphertext security and improved distributed decoding，Giorgi、Laguillaumie、Ottow、Vergnaud，2026|官方题名、作者、摘要，订阅全文未取得|摘要主题为阈值Niederreiter和分布式解码，完整等价覆盖未决|

两项代码标识来自既有密码学材料。本文按准确题名引用，密码学原理继续沿用占坑约束。[THO24](https://doi.org/10.1007/s10623-023-01309-2) [GLOV26](https://doi.org/10.1007/s10623-025-01795-6)

## 5 检索范围与缺口

本轮检索服务工具发生传输失败，随后使用可访问的一手页面和arXiv官方检索。查询包括revocation rebinding、credential migration lower bound、clustering recourse partition、binary clustering Hamming、categorical clustering和partition reconfiguration。检索页面、原文及取得状态保存在sources。

前两组精确词检索分别找到root-scoped quiescence与一项SSH KEM工作。后者的题名与本研究的资源谱问题距离较远，仅作为检索结果保留。二值聚类检索定位到2021年的直接数学近邻。较宽的partition reconfiguration结果具有较多应用噪声，当前只筛查第一页题名，未覆盖全部结果。

查询命中数用于说明检索过程。完整资源谱的优先权仍需追查逐维误差聚类、布尔矩阵分组和受限重配置的直接文献，并由研究者复核。本轮没有发布首次或独创的已确认声明。

## 6 排序修订

新增全文核对后，排名1的先例距离从3调整为2，原因是固定分区多数代价已有明确数学近邻。排名2从2调整为1，原因是root-scoped quiescence直接覆盖共有并发原理。两项继续分别以“资源谱候选数学贡献”和“测量支撑的领域契约规格”完成本轮交付。原始排序记录保留于RANKING_STAGE0.md。
