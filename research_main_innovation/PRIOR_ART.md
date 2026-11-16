# 三个候选问题的直接先例

核查日期为2026-11-04。以下只比较与候选技术差异直接相关的定义和结果。取得全文与完整证明复核分别记录，作者性能数字仅作为作者报告引用。本轮没有复现外部工件。

## L1 动态账户生态与恢复

**Verifying Account Ecosystems With Graph Transformations**，Freya Murphy、Saša Radomirović，IEEE EuroS&P 2026，DOI 10.1109/EuroSP68448.2026.00038。当前已取得22页作者稿，核读§1、§3.1—3.3、§5、§6.2—6.5、§8。RAG用资源、主体和访问方法顶点表达AND/OR访问条件，以图重写表达供应商提供的登录、改密、恢复方法、设备管理及对手动作。Remark 3还用被消费的counter顶点限制动作次数。[原文](D:/毕业设计/关键论文与可行性核查_2026-11-04/阅读记录/P08_全文.txt) [DOI](https://doi.org/10.1109/EuroSP68448.2026.00038)

Definition 18以AG ¬compromise刻画完整性，Definition 20以AG EF access刻画可恢复访问。Apple案例中SDP限制了移除可信设备的路径，模型内可用性改善但完整性仍可失败，随后修改访问条件使两者在声明模型内成立。作者明确限定设备被盗次数及用户模型。一般恢复图、攻击搜索与恢复可达性已有直接覆盖。AG EF与统一观察策略下的强有界完成有不同量词，后者可以由通用博弈/信念规划表达。[Definition 15、17—20及案例限制](D:/毕业设计/关键论文与可行性核查_2026-11-04/阅读记录/P08_全文.txt)

## L2 根范围撤销闭包

**Authorization Revocation for Long-Running AI Agents: Root-Scoped Quiescence under Delegation and Asynchronous Execution**，Genliang Zhu、Chu Wang，2026预印本，arXiv 2609.21284v1。核读威胁模型、Assumptions A1—A11、Definition 3和Lemma/Theorem陈述。支持来源包含最小充分根集合、实际选定支持、在途载体和接收端围栏。[全文](D:/毕业设计/关键论文与可行性核查_2026-11-04/阅读记录/P03_全文.txt) [原文入口](https://arxiv.org/abs/2609.21284v1)

A1覆盖issue、delegate、reactivate和扩大授权。A3要求根纪元单调，A8要求原子独立支持重绑，A9要求恢复不回滚纪元、围栏、终态处置或关闭前沿。Theorem 1给出条件性无错误quiescence，Theorem 3给出独立支持保留，Theorem 5给出crash/replay稳定性，Theorem 6另依赖证据稳定与公平排空条件。因而恢复、重绑、派生与撤销共同出现本身已在近邻范围内。删除A3/A9所造成的失败首先属于前提失效。[A1—A11与定理1—6](D:/毕业设计/关键论文与可行性核查_2026-11-04/阅读记录/P03_全文.txt)

## L3 授权、未知结果与恢复

**AID-Guard: Stateful Authorization for Delegated Agent Effects**，Yingzhe Tong、Leyu Dai、Songhui Guo，2026预印本，arXiv 2608.21159v1。核读威胁假设、提交/恢复流程、§IV的P2及相邻论证。其授权存储要求线性化和可信时间，提供方需满足原子或受控幂等契约。[全文](D:/毕业设计/关键论文与可行性核查_2026-11-04/阅读记录/P05_全文.txt) [原文入口](https://arxiv.org/abs/2608.21159v1)

结果不明时保留原reservation和计费，释放或唯一后继需经过certified no-effect与delivery fence。P2在A1—A6及恢复窗口内保证每个reservation至多一个提供方效果。缺少所需原子/幂等能力的服务在该恢复profile之外，普通提交后的不明确状态保留。因此“丢响应后不盲重试”“确认无效果才允许后继”属于直接先例。[P2及提供方资格](D:/毕业设计/关键论文与可行性核查_2026-11-04/阅读记录/P05_全文.txt)

## L4 可重随机化凭据证明预计算

**Vega: Low-Latency Zero-Knowledge Proofs over Existing Credentials**，Darya Kaviani、Srinath Setty，2026作者稿。通过Microsoft Research取得19页全文，核读§1.2.1、§2协议、§6、§7—8相关段落及官方prepare文档。其静态见证和承诺进入可复用预计算，动态输入进入online witness，各次证明重新随机化预计算承诺。[取得全文](D:/毕业设计/research_main_innovation/sources/vega.pdf) [作者入口](https://www.microsoft.com/en-us/research/publication/vega-low-latency-zero-knowledge-proofs-over-existing-credentials/)

原文明确重随机化所得承诺与新承诺不可区分，并讨论SplitSpartan、SplitNeutronNova和NovaBlindFold。§6借用相应折叠引理解释honest-verifier ZK，本文未据此扩写任意恢复攻击下的完整定理。官方prepare说明每次prove用新鲜隐藏随机性更新共享承诺/盲量，缓存仅作内部优化，并检查公开值变化。文摘报告1920字节凭据的92ms证明、23ms验证与108kB证明，这些是作者场景数据。CS03的强对照应享有同等静态预计算，不能只比较每次重算全部工作。[协议与安全解释](D:/毕业设计/research_main_innovation/sources/vega.txt) [官方预计算接口](D:/毕业设计/research_main_innovation/sources/vega_prep.txt)

## L5 重置安全零知识

**Resettable Zero-Knowledge**，Ran Canetti、Oded Goldreich、Shafi Goldwasser、Silvio Micali，STOC 2000。取得作者修订PostScript并转换为PDF，核读摘要、§4及Definition 4.1、主要定理陈述，同时阅读作者页勘误。其对手可反复调用同一输入、辅助输入和固定随机带所定义的证明者副本，并交错执行、复现前缀和选择不同后续消息。[作者页及勘误](https://www.wisdom.weizmann.ac.il/~oded/p_cggm.html) [取得原稿](D:/毕业设计/research_main_innovation/sources/resettable_revised.pdf)

Definition 4.1要求相应对手视图可模拟。主要结果包括一般复杂性假设下NP的rZK证明、常数轮rWI，以及弱公钥设置下的常数轮rZK论证。作者勘误特别要求多实例共同输入序列使用不同字符串，并说明原证明的其他修正。本轮按带勘误的范围比较。该模型中对手选择并知道调用的incarnation索引，隐藏“两个未知实例是否共享缓存祖先”需独立映射，不能仅凭reset一词直接宣告覆盖或新颖。[定义原文](D:/毕业设计/research_main_innovation/sources/resettable_layout.txt) [勘误快照](D:/毕业设计/research_main_innovation/sources/resettable_page.txt)

## L6 共同补空间

**Common Complements of Linear Subspaces and the Sparseness of MRD Codes**，Anina Gruica、Alberto Ravagnani，期刊入口为SIAM Journal on Applied Algebra and Geometry，DOI 10.1137/21M1428947。本轮取得2022-01-17的arXiv 2011.02993v2，共28页，核读引言、Problem A/B、Theorem 2.2和3.6相关陈述。原文研究有限域子空间族的公共补空间、数量界及其与MRD码的关系。[全文](D:/毕业设计/research_main_innovation/sources/common_complements.pdf) [原文入口](https://arxiv.org/abs/2011.02993v2) [DOI](https://doi.org/10.1137/21M1428947)

CS03在给定仿射视图和允许刷新子空间后，使用子空间求交、补基和配对合成。这一数学核心已具有通用线性代数解释。当前可重新评估的对象是完整密码协议历史的可靠映射与同安全目标成本，公共补空间合成本身保留已有工具归属。[CS03 §5—6](D:/毕业设计/research_main_innovation/sources/cs03.txt)

## L7 VBP的准确安全目标

**Mitigating Injection Attacks against E2EE Applications via View-Based Partitioning**，Andrés Fábrega、Samuel Breckenridge、Armin Namavari、Thomas Ristenpart，USENIX Security 2025。用户提供21页全文后，核读§2—4、§6.1—6.3、Definition 2、Theorem 1—2及Corollary 1。模型允许经合法客户端接口自适应注入，并观察加密导出。框架在导出阶段按用户可读视图划分数据，对各分区独立压缩或去重。[本轮全文](D:/毕业设计/research_main_innovation/sources/vbp.pdf) [会议入口](https://www.usenix.org/conference/usenixsecurity25/presentation/fabrega-partitioning)

安全定义是injection simulatability，比较有注入对手与无注入模拟器在同一挑战序列上的成功概率差。Theorem 1给出Adv_IS≤2Adv_ROR+ε，Theorem 2由view non-interference得到perfect length independence。原文明确把passive leakage留在本项保证之外，并对任意视图策略Π陈述结果。动态视图、批准事件或时序的组合需要映射其接口与不干扰前提，较强的全轨迹保密目标无法由备份分区自动推出。[§6原文](D:/毕业设计/research_main_innovation/sources/vbp.txt)

## L8 FIDES的信息流边界

**Securing AI Agents with Information-Flow Control**，Manuel Costa等，2025，arXiv 2505.23643v2。核读§2.1、§3—5相关定义、Proposition 1及explicit secrecy说明。对手可影响工具返回，并观察某些工具效果，配置、工具描述和模型属于可信设置。[全文](D:/毕业设计/research_main_innovation/sources/fides.pdf) [原文入口](https://arxiv.org/abs/2505.23643v2)

Proposition 1在正确施加P-T/P-F政策时提供工具调用及数据完整性的不干扰，以及机密性的explicit secrecy。原文明确允许机密数据影响控制流，工具序列可泄漏有限信息，并指出改变政策可以增强机密性，但会限制可完成任务。其隐藏变量、隔离检查和类型化揭示属于强基线能力，任何新方案须匹配合法任务集合再比较开销。[Proposition 1与§5](D:/毕业设计/research_main_innovation/sources/fides.txt)

## L9 私密策略求值

**Privacy-preserving policy evaluation in multi-party access control**，Mina Sheikhalishahi、Ischa Stork、Nicola Zannone，Journal of Computer Security 29(6)，613—650，2021，DOI 10.3233/JCS-200007。核读§1、§3.2及§6。该文在多所有者、单请求者模型下表示ABAC目标和多值策略组合，以Paillier同态计算及SFE实现私密求值。[机构全文](D:/毕业设计/关键论文与可行性核查_2026-11-04/阅读记录/P16_全文.txt) [DOI](https://doi.org/10.3233/JCS-200007)

声明模型为半诚实、Data Server与STP不串谋，至少两个data holders诚实，最终决策属于允许输出。原文还讨论穷举查询可恢复整体策略的输出泄漏。该结果支持“隐藏求值内部过程”已有方案，持续决策和公开控制轨迹的允许泄漏仍须单独定义。本文未把原文的组件组合叙述提升为已审定的恶意安全完整协议。[§3.2与§6.2](D:/毕业设计/关键论文与可行性核查_2026-11-04/阅读记录/P16_全文.txt)

## 本轮对先例状态的更新

RAG和VBP全文均已实际核读，相关取得缺口关闭。Vega的具体重随机化路径也进入强对照，CS03仍缺自身原始工件。这里得到的主要结果是把三个问题的比较前提收紧，当前尚无候选机制相对这些正确强组合的严格分离实例。
