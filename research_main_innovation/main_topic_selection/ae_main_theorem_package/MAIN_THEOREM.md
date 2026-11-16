# 带列表约束的二元模板半径一拟合：参数化算法与条件紧性

*List-Constrained Binary Template Fitting at Radius One: A Parameterized Algorithm and Conditional Tightness*

研究稿 MT-1，2026-11-07。本文及自含附录为知情模型辅助纸面研究成果；外部数学复核、形式化验证和发表优先权各自保持待核。本文给出一个可独立评价的理论候选，不作全球首次或实测速度主张。

**摘要。** 给定具有w种全局模式的显式二元模板，每个观测列选择一个允许模式，每个观测行选择一个全串固定的允许标签，并要求每行至多一次Hamming错误。我们给出确定性精确2^{O(w log(w+2))}poly(N)算法，读取全部模板、列表和观测，并恢复原模式、行标签及全部原有序中心。算法维护模式块与少量例外，通过失败行的小冲突、延后提交及代表修复避免逐次枚举完整标签。一个从同阶Subgraph Isomorphism出发的多项式归约证明：在确定性ETH下，即使YES最优半径恰为1，也排除2^{o(w log w)}poly(N)时间。已核读近邻分别覆盖模型、精确基底、总预算或其他参数化方法；完整主定理的发表优先权继续未决。

**Abstract.** We consider binary template fitting with a global palette of w column patterns, coordinate domains, row-label lists, and at most one Hamming error per observation row. A single label must explain each entire row. We give a deterministic exact algorithm with running time 2^{O(w log(w+2))}poly(N), including explicit input processing and recovery of all original ordered centers. The search uses pattern refinement, a small conflict certificate, delayed commitments, and representative repair. A polynomial reduction from equal-order Subgraph Isomorphism excludes 2^{o(w log w)}poly(N) deterministic algorithms under ETH, even when every YES instance has optimum radius exactly one. The result is an algorithm-theorem candidate with a source-bounded priority audit; global novelty and practical speed advantages remain separate questions.

## 1. 规范问题

输入Q∈{0,1}^{K×w}、A∈{0,1}^{M×v}、每列显式域Ω_t⊆[w]和每行显式标签列表Λ_i⊆[K]。w,K≥1，M,v≥0；模板为输入，角色有序，可重复或闲置。

选择共享η_t∈Ω_t以及每行一个p_i∈Λ_i，要求

\[
\forall i\in[M]:\quad
\sum_{t=1}^{v}[A_{it}\ne Q[p_i,\eta_t]]\le1.\tag{L}
\]

N为完整显式二进制编码长度。YES输出η、各行原标签和全部原有序K个中心C_p[t]=Q[p,η_t]；NO须正确。完整输出、读取和恢复计费，输入多项式次数与所有参数无关。

等价成本形式允许τ_i(p)∈{0,1,2}，要求τ_i(p)+距离≤1。列表外用成本2禁用；反向只需复制标签并增加一个强制辅助模式/坐标，模式数w+1。成本1将该标签的剩余半径变成0。这些字段是标准表达，不单独承担新增模型主张。

在Binary Constrained K-Center术语下，中心为C₁,…,C_K，逐坐标关系R_t={Q[:,ℓ]:ℓ∈Ω_t}，所有关系来自同一个至多w种tuple的全局库。Ω满域时是共同关系。列表再限制每个点可用中心。对应列表型二部模板时，A的行/列是两侧对象、Q的行/列是两侧角色，错误只按左对象逐行计数，右对象无错误预算。

## 2. 主要定理

**定理U（半径一上界）。** 问题(L)及成本形式可在确定性时间

\[
2^{O(w\log(w+2))}N^c\tag{U}
\]

精确求解，并恢复全部规定输出。c统一。重复模式可合法合并，因而也可按不同Q列数计费；重复预测标签需按每行成本/列表保存原ID preimage。

**定理D（真正正半径的条件紧性）。** 假设确定性ETH成立，则不存在2^{o(w log w)}N^c的确定性精确算法，即使列表和域全满、成本0、Q有w个不同列、K=O(w²)，并且YES实例的最优最大行半径恰为1。该排除继承到完整列表/成本模型。

证明见[自含附录](D:/毕业设计/research_main_innovation/main_topic_selection/ae_main_theorem_package/COMPLETE_PROOF.md)P0–P12。定理D由已发表的JACM2017 Theorem1.3[6]接本稿多项式归约取得；源ETH结论与本稿目标映射分工明确。它只说明w log w指数阶条件匹配，精确常数、各实例难度、一般半径的其他项和实际运行性能仍有独立问题。

## 3. 核心困难与算法责任

固定η后，逐行扫描K标签即可验收。困难在于未知η的全局共享：一行的错误不能用另一行的余量支付；一个行标签须解释全部坐标；不同输入列型可因错误共享模式，同列型也可拆分。直接猜全部标签付K^M，猜错误位置付(v+1)^M，普通精确角色扩展会引入wv种模式。

算法维护已提交行、模式块、带值码及至多w−1个坐标例外。失败行在“当前模式×观测位”的2w桶中每桶保留2项，得到≤4w的冲突。固定真实解只用于证明：失败时，真实标签会分裂某个活动块，或冲突内有一个旧行真实例外。

新行只猜有序细分。未分裂块的新位由当前支持代表给出，待提交时逐行扫描一个同时满足全部位和预算的标签。代表若相对固定真实解出错，就将它作为例外；代表都正确时可以提交。合法提交已经存在时也保留代表例外，以免误删正确路径。支持为空的块退出E外选择，原模式仍可用于例外赋值。

真二分与例外各至多w−1次，提交至多w−1次。结构树、原模式到叶的映射、R/E/C动作词和例外编号可重建全部搜索前缀，总数为2^{O(w log(w+2))}。完整标签只扫描、不作为分支序列，避开K^{w−1}。域、成本和被拒选项的费用均在附录计入。

这段预算感知的定位/代表修复及历史解码是项目候选的核心证明责任。树形计数、鸽巢、列表和辅助位gadget本身均为标准工具。

## 4. 直接近邻及最有利比较

|来源|真实保证/接口|和定理U之间的责任|
|---|---|---|
|通用有界修复参考（早期项目A4标准重推，附录P13）|(1+max{w,3K₀})^{2K₀+1}poly(N)，完整列表/成本/域；K₀≤2^w后为2^{O(w2^w)}poly(N)|基本w-FPT已有可核对通用组合；当前候选增量是精细依赖。整项发表出处未绑定，不冒充已发表定理|
|已有项目T1/T2型参考，附录P14|(K₀+1)^{O(w)}(w+2)^{O(w)}poly(N)≤2^{O(w²)}poly(N)，成本/域保持已补齐|比通用修复更强；K₀≤poly(w)时已达F(w)，当前增量限剩余一般标签域|
|Fomin等，COL2020[1]，Definition2/Theorem3，32:5|逐坐标中心关系；随机PTAS，v^{O(1)}M^{O((K/ε)^4)}|基本模型已有；半径1取小常数ε可得随机精确阈值，但增长K进入输入指数；行标签列表/未知成本接口另需保持|
|Feder等，List Partitions[2]，作者稿Cor7.1，pp26–27|固定无*模板的精确列表识别；同邻域工具|零误差基底有标准F(w)处理。半径1已完成的两条编译分别付(v+1)^M或输入相关模板wv|
|Jansen等，NF25[3] Th1及KKM2020[4] Th1/Cor2|组合n-fold确定性精确算法，保留新旧最小包络|固定行标签的表示有a=M个全局预算行；未知标签另有K^M，或a≤MK的条件约束。尚无完整w参数代入|
|Bandyapadhyay等，FS21[5] Th4，14:5|逐坐标关系、总编辑预算B及代表/超图枚举；(kB)^{O(kB)}2^{kB}n_p^{O(k)}d²|总预算与最大逐行预算不同；交换行列也会交换预算对象，相关定位引理仍需新的保持证明|
|Cygan等[6] Th1.3，18:7|ETH下同阶普通子图嵌入排除2^{o(n_s log n_s)}|归属已发表作者；本稿给目标映射、真正半径1及完整参数恢复|

比较允许所有方法使用相同去重、结构信息、精确基底、固定K、小v、给定标签和角色闲置包装。标准保证还包括w^v poly(N)、固定K的[K(v+1)+1]^{O(K)}poly(N)，以及固定实际错误掩码后的精确识别。已核读结果没有形成完整U的覆盖链；该局部结论不等于全球无先例。

K可以有2^{Θ(w)}种不同标签签名，而K只以显式输入多项式进入(U)。这与含K的搜索深度/输入指数有可定位的保证差异。较慢的已知上界仍不提供通用算法的必要代价，也没有建立候选的实测优势。

## 5. 适用范围与B的条件推论

理论适用于小全局模式库、任意数量观测及静态列表/域。w增长时F(w)本身迅速增长，隐藏常数和显式K扫描均可能使实际运行昂贵；本稿未实现算法或运行新实验。

研究B的M₁条件模型给一项简短特化：w=g为预建、独立可撤销原生根，标签是允许的非恒定根处置向量δ，Q[δ,j]=δ_j；A_it表示请求i是否停止任务t，η_t是共同初始绑定。矩阵只收非平凡停止请求；空/全请求按模型零重绑直接处理。若任意单任务都能获准原子重绑到任一既有根并退役旧支持、容量足够、保留任务逐前缀可用，则Hamming错配数恰等于所需最少重绑数。g≥2时可取K=2^g−2，定理U给固定g、一次重绑预算的配置判定2^{O(g log(g+2))}poly(Mv)。

该推论以M₁执行合同为条件。当前B停止引擎只有撤销/关闭，G计数也与M₁付费空根不同；真实平台原子迁移和旧副本完整处置尚缺接口证据。[VALUE_AND_SCOPE.md](D:/毕业设计/research_main_innovation/main_topic_selection/ae_main_theorem_package/VALUE_AND_SCOPE.md)给双向距离证明、合法实例、违反前提反例和最小缺失合同。A/AB的部分观测、连续请求、并发派生和崩溃恢复没有由本定理扩展。

## 6. 主张、证据与局限

本文可支持“半径一列表模板拟合的确定性精细参数算法及条件紧性”这一精确命题包。基本w-FPT及2^{O(w²)}项目粗界已在P13/P14明确，主候选是剩余一般标签域的w log w依赖。整项发表出处与精细界优先权仍分别待核。已发表模型/工具、标准包装和项目核心证明分别登记。原T3的变化半径共同关系上界保持原合同，本稿没有将成本/域迁移外推到任意半径。

集中来源状态和贡献判废条件在[DECISION.md](D:/毕业设计/research_main_innovation/main_topic_selection/ae_main_theorem_package/DECISION.md)。COL2026按用户指示暂停获取；若任何已发表定理或标准短推论覆盖U，原创定位须按实际覆盖收缩。外部数学读者、形式化审查和相对具体G的严格代价分离仍待取得；实现门继续关闭。

## 参考文献与实际版本

[1] F. V. Fomin, P. A. Golovach, F. Panolan, K. Simonov. *Low-Rank Binary Matrix Approximation in Column-Sum Norm*. APPROX/RANDOM2020, LIPIcs176,32:1–32:18. DOI [10.4230/LIPIcs.APPROX/RANDOM.2020.32](https://doi.org/10.4230/LIPIcs.APPROX/RANDOM.2020.32). 正式版及其2019遗漏证明按已核读范围使用。

[2] T. Feder, P. Hell, S. Klein, R. Motwani. *List Partitions*. SIAM J.Discrete Math.16(3):449–478,2003. DOI [10.1137/S0895480100384055](https://doi.org/10.1137/S0895480100384055). 实际核读为作者30页PS转换稿，编号按作者页，未假定VOR逐字一致。

[3] K. Jansen, K. Kahler, L. Pirotton, M. Tutas. *New Algorithm for Combinatorial n-Folds and Applications*. IPEC2025. DOI [10.4230/LIPIcs.IPEC.2025.15](https://doi.org/10.4230/LIPIcs.IPEC.2025.15). 正式及arXiv2409.04212v4相关证明。

[4] D. Knop, M. Koutecký, M. Mnich. *Combinatorial n-fold integer programming and applications*. Mathematical Programming184:1–34,2020. DOI [10.1007/s10107-019-01402-2](https://doi.org/10.1007/s10107-019-01402-2).

[5] S. Bandyapadhyay, F. V. Fomin, P. A. Golovach, K. Simonov. *Parameterized Complexity of Feature Selection for Categorical Data Clustering*. MFCS2021. DOI [10.4230/LIPIcs.MFCS.2021.14](https://doi.org/10.4230/LIPIcs.MFCS.2021.14). 正式及arXiv2105.03753v2相关证明。

[6] M. Cygan, F. V. Fomin, A. Golovnev, A. S. Kulikov, I. Mihajlin, J. Pachocki, A. Socała. *Tight Lower Bounds on Graph Embedding Problems*. JACM64(3),Article18,2017. DOI [10.1145/3051094](https://doi.org/10.1145/3051094). 作者公开JACM排版全文，Theorems1.3/4.4/4.5。

本地原文及版本/页定位索引见sources/SOURCE_INDEX.md，不要求读者先阅读阶段报告来理解正文证明。
