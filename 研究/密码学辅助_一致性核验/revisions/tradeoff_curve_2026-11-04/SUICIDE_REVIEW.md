# T2 自杀式审查

2026-11-04。本轮审查先接受可推翻候选的标准方法。通过“数学可推导”与通过“具有实质独立原创价值”分别判定。历史16篇全文之外，本轮取得6篇新全文，9组arXiv检索有效返回。HTTP原始响应与失败请求保存在本目录。

## 1. 新原文与实际阅读位置

| 来源、年份及版本 | 实际阅读位置 | 已有结论及T2变量映射 |
|---|---|---|
| TD05，G. R. Blakley、C. Meadows，Security of Ramp Schemes，CRYPTO’84论文集，1985，27页 | §2，PDF8–11，印刷249–252；§3，PDF12–15；Shamir例PDF17 | 秘密维数、重构所需份额数和部分泄漏的权衡已经出现。原文(d,k,n)分别对应秘密大小、恢复阈值、份额数，与T2的(d,k,r)含义不同。Theorem3.5按线性纤维交集计数证明相对安全。[DOI](https://doi.org/10.1007/3-540-39568-7_20) |
| TD01，M. Iwamoto、H. Yamamoto，Strongly Secure Ramp Secret Sharing Schemes for General Access Structures，arXiv cs/0506065v1 | Definition1 PDF2，Definition7 PDF5，Theorem9及证明PDF7，Theorem11 PDF8，参考PDF9 | 条件熵比例、秘密子向量独立性、公开可逆变换与子矩阵秩条件。秘密“各部分均隐藏”与“全部秘密的联合泄漏为零”有明确区别。版本页首2005，正文日期2018-09-03，按实际PDF固定。[全文](https://arxiv.org/pdf/cs/0506065v1) |
| TD02，R. A. Chou、J. Kliewer，Secure Distributed Storage: Optimal Trade-Off Between Storage Rate and Privacy Leakage，2024，v1 | Definitions1–3 PDF2–3，Theorems1/2 PDF4–5，构造PDF5–6，逆定理PDF6–7及附录 | 同时优化存储大小、归一化互信息泄漏和编码随机性，已具有分段曲线和转折阈值。符号α为互信息比例，z为合谋阈值，τ为恢复阈值。[全文](https://arxiv.org/pdf/2403.10676v1) |
| TD03，U. Gupta、H. Mahdavifar，Bounds on the Statistical Leakage-Resilience of Shamir’s Secret Sharing，2024，v1 | §II–III PDF2–3，Proposition4及证明PDF3–4 | 使用独立噪声泄漏信道和互信息约束，并引用语义安全、区分距离与互信息的转换。T2共享M引入跨列相关性，映射到其独立信道假设需要论证。[全文](https://arxiv.org/pdf/2405.04622v1) |
| TD04，R. Peled、A. Yadin、A. Yehudayoff，The Maximal Probability that k-wise Independent Bits are All 1，v3，2011 | §1 PDF2–3，Theorem1.1 PDF5 | 有限阶独立、编码构造、小支持随机分布与LP/矩问题均属既有工具。RESOURCE_LEDGER的非零掩码优化由多项式插值直接给出，原文并非专门构造该掩码。[全文](https://arxiv.org/pdf/0801.0059v3) |
| TD08，M. El-Khamy、R. J. McEliece，The Partition Weight Enumerator of MDS Codes and its Applications，2005，v1 | §II式(2)，PDF1；Theorems1/3及Corollary5，PDF2 | MDS码重量分布及坐标分区重量计数已有闭式。原文码维数k对应本轮d，原文最小距离d对应n−d+1。取重量i=n即得到本轮A_n(C)。[全文](https://arxiv.org/pdf/cs/0505054v1) |

Beimel2011的已读版本主要介绍完美秘密共享、份额大小及理想结构。它为本轮提供定义和下界入口，ramp的直接细节由TD05、TD01和TD02补齐。TD05为扫描PDF，公式缺字处按原图核对或采用独立代数推导。

## 2. ramp曲线的精确归约与限度

### 2.1 已有资源曲线

TD02的Theorem1在其泄漏对称条件下给出

\[
\frac{\lambda_t^*(\alpha,z,\tau)}{H(F)}
=\max\left\{\frac{1-\alpha}{\tau-z},\frac1\tau\right\},\qquad
\frac{\rho^*(\alpha,z,\tau)}{H(F)}
=\frac{[z-\tau\alpha]^+}{\tau-z}.
\]

因此“给出泄漏—随机量—恢复阈值的完整曲线并具有相变”这一宽泛创新声明已经有直接先例。新贡献必须落到不同且明确的协议类、度量及未被上述结论推出的内容。原文所称linear ramp有时指泄漏访问函数线性增长，引用时应与代数线性编码区分。

### 2.2 经典线性分享的TV模拟半径

固定一个窃听份额集合。若视图为Y=As+BR，其中R在一个有限域向量空间均匀，令H=im(B)，则给定s后的视图在As+H上均匀。不同消息诱导相同或不相交的陪集。

设消息域的商像数为N。对任意模拟器Q，至少一个陪集获得的Q质量≤1/N，故该消息的TV距离≥1−1/N。令Q均匀混合这N个陪集即达到该界。因此

\[
\delta_{\rm affine\ coset}=1-\frac1N.
\]

全消息空间s∈F^ℓ时，N=q^t，其中t=rank[A B]−rank(B)，从而δ=1−q⁻ᵗ，均匀秘密时I(s;Y)=t log₂q。若模拟器已知某个获准泄漏值，则逐泄漏纤维应用同一计数。

这项转换是经典线性陪集机制的直接推论，与历史q-polymatroid的rank/互信息公式一致。将其重新命名为新“误差—秩曲线”应予淘汰。

### 2.3 r5与均匀仿射陪集模型的结构差异

r5规范分布在所有合法核点上具有正质量。固定一个三列基，合法核集合排除了该基以外的m=n−3个全非零字典点。对角缩放可以改变这m个禁点的位置，因为其所在轨道大小(q−1)²>m。

选一个确实改变禁点集的缩放，两个幅值输入产生的核分布具有共同的合法点，也有只对一方合法的点。因此两分布满足0<TV<1。均匀仿射陪集模型任意两消息的TV始终为0或1。

若两种统计实验间存在双向保真随机变换，数据处理在两个方向都成立，成对TV应相等。上述差异排除了这一特定的保真同构。一般秘密共享允许更广的随机编码，其他归约仍待查证。排除单一同构本身尚不足以确认新密码学理论。

## 3. P04广义秩界查杀

历史P04的Theorem5对均匀稠密矩阵A、加性低秩噪声K及可逆盲化，给出最大相关系数约q⁻ʳ的下界。本轮的条件采样上界也呈q⁻ʳ量级，单凭量级相同只能提出进一步归约问题。

| 必须保留的项目 | P04 | 本轮主分支 | 核验结果 |
|---|---|---|---|
| 输入量词 | 全矩阵上的均匀先验 | 固定支持下任意非零幅值 | 尚无保真转换 |
| 秩预算 | 加性噪声K的秩 | 乘法映射M的行数/秩 | 约束对象不同 |
| 度量 | 最大相关系数ρ_m | 最坏TV模拟半径Δ | 一般度量转换已有文献，精确值转换待证 |
| 正确性与功能 | 外包矩阵乘积 | 诊断观察、逐位置无抹除 | 功能及侧信息需同时匹配 |

**判定为REDUCTION_UNESTABLISHED。** 已核读P04并未直接给出T2共享掩码LP的最优值，宽泛的低秩隐私权衡主题已有明确先例。

## 4. T2-FULLSUPPORT精确边界族的归属

TRADEOFF_CURVE给出Δ(r,n)=1−A_n(C)/(q−1)ⁿ。其证明由两部分构成。

1. 秩1构造将问题化成非零坐标乘法群上的均匀集合重叠，最优模拟距离由集合大小直接决定。
2. q>n时，任意无零列高秩矩阵均存在一个全坐标非零的线性投影。该投影给出同一重叠上界，排除更高秩降低误差的可能。

对于弧字典，A_n(C)与TD08式(2)完全相同。令原文重量i=n、码维数等于本轮d、最小距离等于n−d+1，换求和变量后即得到本轮包含—排除公式。单回路闭式进一步由非零元素和为0的标准计数得到。

**归属判断。** 码字计数子项已覆盖。TV公式与跨秩投影论证有自包含手工证明，当前按“群平均和编码计数的自然组合”降级为边界命题。尚未确认其完整表述的最早来源，正文会保留来源未决。它对参数纠错有用，独立密码学价值尚待更强论证。

## 5. 逐子定理的查杀账本

| ID | 主张 | 数学状态 | 创新处置/死因 | 判废条件 |
|---|---|---|---|---|
| T2-ZH | r≥k可让同一原始观察隐藏支持且无抹除 | REFUTED | 空支持与单支持事件完全区分 | 改成私密输出或部分泄漏后另立profile |
| T2-ZA | d=k<n时r≥d当且仅当完美条件幅值隐私可行 | 手工复核旧证明 | 历史端点，新增原创主张淘汰 | q=2、n=d或观察类变化 |
| T2-MON | r弱递减、k弱递增 | 手工成立 | 可行集包含的直接推论 | 更换V或限定恰好满行秩 |
| T2-UB | 条件化均匀满秩分布的包含—排除上界 | 手工成立 | 旧遗漏概率加条件化TV，属于直接组合 | 字典相关秩不同则重新计算p_j |
| T2-LB | p₁/[2L(d)]下界 | 手工复核旧证明 | 历史非紧下界，新增原创主张淘汰 | 群生成条件失效 |
| T2-LP | 任意r,d主分支的核—轨道有限LP | 手工双向归约 | 标准对称化和有限优化的自然推广，单独算法优势未建立 | 模拟器或状态压缩遗漏可观察变量 |
| T2-RANK1 | 主分支秩1层的精确误差1−A_n(C)/(q−1)ᵈ | 手工成立 | 群传递性与MDS计数的直接推论 | 输入支持不覆盖基或秩限制改变 |
| T2-I24/T2-I34 | d=k=4、r=2或3精确最优值及匹配构造 | OPEN | 已有上下界，匹配对偶缺失 | 任一候选对偶出现负松弛或漏秩层 |
| T2-GAP | d=k=4、q+1>400n时，中间误差区间内最小行数恰为3 | 手工成立 | 上界与旧下界的推论型组合，完整优先权未决，独立价值待评估 | 更换观察类、取消无抹除或允许逐列独立掩码 |
| T2-PHASE | r=k−1处有额外特殊相变 | OPEN | 现有论证只给r=d的零/正边界 | 对“相变”未给可检验数值定义 |
| T2-FULLSUPPORT | 全支持家族的精确值与r无关 | 手工成立 | MDS计数已覆盖，整体按自然组合降级，完整优先权未决 | q≤n、限制矩阵必须恰好高秩或只允许k<n时原证明失去前提 |
| T2-RNG-N | 任意零误差幅值掩码均需Θ(n)独立随机量 | REFUTED | k-wise独立标准构造提供反例 | 严格限定逐项独立采样后仅为该算法成本 |
| T2-RNG-K | 非零坐标掩码至少k log₂(q−1)熵，特定域可达到 | 手工成立 | 有限阶独立和插值的直接推论 | q−1非素数幂时匹配构造尚需另证 |
| T2-OTP | 固定加性syndrome需要min(n,2k)行和相应噪声熵 | 手工成立 | 经典稀疏恢复、平移不变性和MDS推论 | 任意非线性/交互协议尚无该下界 |
| T2-TRUST | 必须存在单一私密接收方 | 更强说法淘汰 | 必要的是观察权限分离，授权集合/共享输出也可实现 | 若功能明确只允许单接收者，则属于功能前提 |
| T2-INC | 空支持冲突引理 | 手工成立 | 完美保密定义的直接推论，保留为边界引理 | 见独立引理中的观察和输入前提 |

## 6. 查新分母与未决项

有效检索式、返回记录、完整HTTP台账见SEARCH_LEDGER.md及SEARCH_DATA.json。本轮9组arXiv查询有效，3次Semantic Scholar题名查询均429。Yamamoto原始英译与Shannon1949的两个出版者PDF入口403，保留为待获取。

TD01的参考[10] *Nonperfect Secret Sharing Schemes and Matroids*，EUROCRYPT’93论文集，及[12] *Lower Bound on the Size of Shares of Nonperfect Secret Sharing Schemes*，ASIACRYPT’94论文集，是下一轮原始先例重点。TD02的[22] *Improving the Linear Programming Technique in the Search for Lower Bounds in Secret Sharing*，2020，以及[26] *Randomness in Distribution Protocols*，1996，仍需独立全文核读。

检索未覆盖整个密码学文献。一般主分支精确闭式仍为OPEN，强独立原创仍待建立。保留的理论工作定位为严格参数化的受限观察极值研究与边界审查。
