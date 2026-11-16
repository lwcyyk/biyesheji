> 可移交阅读副本。数学正文、章节和式号沿用冻结原件；仅转换链接、添加行定位锚点及本说明。[冻结原件](../../../frozen/crypto_branch_monitor/round_005/THEOREM_FOR_CITATION.md)。历史命令按来源记录保留；本包公开重放入口为根目录 REPLAY.md。

# 固定公开矩阵下的仿射支撑攻击

2026-11-07。本引用稿整理ROUND-005及无历史独立AI审阅已核准的数学核心，补入审阅要求的联合事件定义、Ord行序和轮换计数。一般证明与精确证书来自作者冻结稿及两阶段审阅。第二阶段裁决为 `PASS_WITH_MINOR_PRESENTATION_CLARIFICATIONS`。

## 模型与记号

取q=2^D，公开A∈Z_q^(n×n)在有关χ采样之前固定。χ在Z_q上的支持为S，h=|S|，a=max_zχ(z)。相关矩阵的χ坐标及调用按理想模型独立采样。

Ord采用n列参数化

\[
\operatorname{Ord}_n:\mathbb Z_q^{\bar m\times n}
\longrightarrow\{0,1\}^{\bar m\times nD}.
\]

若c_(j,b)是第j个坐标的第b位，一行输出顺序为

\[
(c_{1,0},\ldots,c_{n,0},c_{1,1},\ldots,c_{n,1},\ldots,
c_{1,D-1},\ldots,c_{n,D-1}).
\]

令牌P1、Q1及Tensor-D使用同一位平面行序。该解释明确处理FI-v4第13页的nbar列字面域与第14页n列调用之间的记号差异。

以第一行为例，普通父C=U0A+F0，H=Ord_n(C)，P1=U1A+F1，P2=U2A+F2。fresh挑战Y=SfA+Ff，update挑战Y=HP1+rP2，其中r∈χ^n。各维度与冻结FI-v4算法对应。判定器在P2可逆时检验(Y−HP1)P2^−1∈S^n，奇异时公平猜测。

## 单次定理

对1≤w0≤n，定义模q卷积峰值

\[
\mu_{w0}=\max_z\Pr[X_1+\cdots+X_{w0}=z\bmod q],
\qquad X_i\overset{iid}{\sim}\chi,
\]

\[
\varepsilon_n=\min\{1,\binom n{w0-1}a^{n-w0+1}+(h\mu_{w0})^n\}.
\]

记E为fresh支撑事件，α=Pr[P2可逆]，β=Pr_fresh[P2可逆且E]。对每个固定A及每个有正概率的P2=p，有Pr(E|A,P2=p)≤ε_n。因此

\[
\beta\le\alpha\varepsilon_n,\qquad
\Delta=\alpha-\beta\ge\alpha(1-\varepsilon_n).
\]

Δ采用原游戏两个分支输出1概率之差，均匀隐藏位猜测的成功率为(1+Δ)/2，bias为Δ/2。w0=n+1也可作为平凡端点加入，此时ε_n=1。

证明先以F0的最大原子控制父行低汉明重量事件，再在固定A、父、U1、P2及fresh Y时保留F1随机性。对每个固定r的等式使用独立列卷积峰值，并对S^n取并集。作者与独立审阅者均给出此条件界的一般证明。

## 自适应定理与调用预算

每轮重新调用Enc产生普通父，再调用Next及Corr(token)。选择J只取决于P2序列的首次可逆位置，最多k轮，最后发起一次挑战。定义

\[
p_k=\Pr[J\le k],\qquad
\beta_{selected}=\Pr_{fresh}[J\le k\ \land\ E_J].
\]

β_selected为联合概率。全部失败时公平猜测的两分支贡献抵消，故

\[
\beta_{selected}\le p_k\varepsilon_n,\qquad
\Delta_k=p_k-\beta_{selected}\ge p_k(1-\varepsilon_n).
\]

T在本稿表示Next轮换次数上界。T次轮换访问epoch标签0,…,T，共T+1个状态。k≤T时至多使用k次Enc、k次Next、k次Corr及一次Challenge，总调用数至多3k+1。原游戏普通父登记和空钥匙腐化闭包已由独立审阅核准。

## 有限证书与正确性族

取w0=64，官方2021概率表的整数卷积给出下表。概率上界由完整两项有理数之和单独认证。

| χ表与n,D | fresh误接受上界ε_n |
|---|---:|
| 640，n=640，D=15 | 2^−751 |
| 976，n=976，D=16 | 2^−1118 |
| 1344，n=1344，D=16 | 2^−1532 |

对χ640及χ976，可逆概率为α_n=∏_{i=1}^n(1−2^−i)。三组fresh证书均已独立重算。χ1344完整优势中使用的旧N1秩区间保留其既有证明与审阅范围。

共同正确性族取整数λ≥2，n=8λ，D=8ceil(log2n)，q=2^D，χ=χ640，mbar=nbar=8，B=2，T=k=t_max=n。其逐样本界为

\[
B0=288n+12,\quad
W=288n^2D+3456n^2+12nD+144n,\quad
B0+nW<q/8.
\]

该族对最长n次更新正确。n≥64时采用上述w0=64概率式，n<64取ε_n=1。由α_n>1/4、a<1/4及25μ64<1/2，得到

\[
\Delta_n\ge1-(3/4)^n-\varepsilon_n=1-\operatorname{negl}(\lambda).
\]

以上结论适用于声明的独立采样模型和任意预先固定A，计算困难性假设数量为0。CF-1位于FI打印的大D参数域，严格官方D≤16接口下采用扩展参数模型标签。具体程序的联合噪声流、版本配置与失败行为仍需实现对应证据。

## 可追溯依据

- 作者一般证明位于 [DIRECT_PROBABILITY_PROOF.md](../../crypto_frodo_unconditional_support/DIRECT_PROBABILITY_PROOF.md)。
- 第一阶段的无历史推导及原始来源核验位于 [PHASE1_DERIVATION.md](independent_review_packet/review_output/phase1/PHASE1_DERIVATION.md)。
- 第二阶段逐项比对及三项呈现补充位于 [COMPARISON.md](independent_review_packet/review_output/phase2/COMPARISON.md)。
- 最终独立AI审阅裁决位于 [FINAL_REVIEW_VERDICT.json](../../../frozen/crypto_branch_monitor/round_005/independent_review_packet/review_output/phase2/FINAL_REVIEW_VERDICT.json)。

本稿由主会话按已审定公式作呈现整理，其文稿身份为审阅后的整合。优先权和真实业务部署需求使用各自的证据记录。
