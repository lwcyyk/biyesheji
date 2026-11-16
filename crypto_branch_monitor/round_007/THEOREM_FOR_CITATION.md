# 普通更新随机带暴露下的线性作用安全边界

2026-11-07。本稿按两阶段数学审阅整理。ROUND-007的差分提取、诚实行模学习、合法轨迹及CF2先经作者证明不可见的独立推导，再作作者稿比对。合并X=(H,r)的扩展于第二阶段首次送达，登记为知情审查。下文将审阅要求的输出充分性及采样条件显式写入。

## 模型与适用条件

取整数q≥2，R=Z/qZ，固定epoch边界的隐藏token含固定矩阵W∈R^(m×d)，m为安全参数的多项式。对诚实父密文C和合法更新随机输入ω，可有效计算公开特征X(C,ω)∈R^m，普通更新转录给出标签

\[
Z=X(C,\omega)W.
\]

普通更新的完整返回带允许有效解码所需系数。边界内的W固定复用。条件于固定公开参数、有关钥匙和token，训练父来自Q次独立诚实Enc(M0)，各训练更新使用其真实条件随机输入，联合特征X_i为iid。

攻击者具有公开有效的本地更新采样器。它对目标父C产生一次完整合法输入ω_loc，其条件分布等于真实更新随机输入分布。抽样独立于训练随机带和挑战生成币，并发生于成员测试之前。fresh挑战来自独立Enc(M0)，故其目标联合特征与训练联合特征条件同分布。

需要公开有效的Rec及输出投影Π，对两类诚实挑战支持中的每个C及合法ω满足

\[
\operatorname{Rec}(C,\omega,X(C,\omega)W)
=\Pi\bigl(\operatorname{Upd}(\Delta,C;\omega)\bigr).
\]

持有目标代完整钥匙时，Π输出足以计算标签ℓ(M)，选取ℓ(M0)≠ℓ(M1)。完整密文可以取Π为恒等映射。FI矩阵实例可以取第一行，并解码其中一个指定消息位。这个条件限定了从可观察线性作用到有效挑战判定的推理。

环特征可有效进行模成员判断及系数表示。维度、log q、训练数和相关算法成本均为多项式。

## 作用学习定理

令L_Q=span_R(X_1,…,X_Q)。对上述条件iid的fresh目标X*，有

\[
\Pr_0[X^*\notin L_Q]
\le\varepsilon_Q
=\min\{1,m\log_2q/(Q+1)\}.
\]

每次新样本严格扩大生成模时，其基数至少翻倍，总增长次数至多floor(m log2q)。iid产生的平均遗漏质量随训练数单调下降，故(Q+1)倍最终遗漏概率至多该容量。这个论证对每个固定上下文成立，可以再对真实上下文平均。

若X*∈L_Q，使用带变换记录的整数HNF/SNF求α，使X*=Σα_iX_i，则Σα_iZ_i=X*W。系数无需短，q的因数分解也无需作为输入。该部分使用成熟的有限模及整数线性代数工具。

## 合法轨迹及优势

采用游戏S的实际返回版本登记规则。epoch1先生成M1的普通父，Next到2，在epoch2生成Q个M0训练父并发起唯一Challenge。保存epoch2挑战，Next到3，跳过Get3，token3保持隐藏。对每个训练父各执行一次普通UpdLeak，最后查询完整Key3。

最终直接集合及闭包为

\[
K^*=\{3\},\qquad T^*=\varnothing,\qquad C^*=\{2\}.
\]

因此该轨迹在声明的游戏S中合法。原FI-v4的Next还会登记新挑战代，其相同Key查询触发公平评分。原FI的普通接口也未返回完整带，这些接口区别随引用保留。

对保存挑战生成X*。非成员时输出update。成员时由Rec重建目标更新投影，用Key3计算标签，标签为ℓ(M0)时输出fresh，其余输出update。

令m0为fresh遗漏概率，e0为fresh成员内的错误标签联合概率，e1为update成员内得到ℓ(M0)的联合概率。按全执行定义虚拟真实本地更新，两分支的一次／两次累计标签错误率分别为δ0、δ1。于是

\[
p_0=m_0+e_0,\quad p_1=1-e_1,\quad
d_{sign}=p_1-p_0=1-m_0-e_0-e_1,
\]

\[
\Delta=|d_{sign}|\ge\max\{0,1-\varepsilon_Q-\delta_0-\delta_1\}.
\]

均匀位游戏的bias为Δ/2，实际猜对概率为1/2+d_sign/2。update挑战特征的分布无需与普通父相同。训练数量与消息预先固定，成员失败后按已登记规则输出。

调用数为EncLeak Q+1、UpdLeak Q、Next 2、Challenge 1、Key 1，总数2Q+5。Token、GetChallenge、Dec的oracle调用数为0。本地计算使用合法的真实更新随机输入。

## 具体正确实例及范围

对FI-v4的矩阵算法，采用n列且位平面顺序匹配token的Ord。取第一行H=Ord_n(C1[1,:])、r=R[1,:]，令

\[
X=(H,r),\quad
W=\begin{bmatrix}P1&Q1\\P2&Q2\end{bmatrix},\quad
m=nD+n.
\]

可观察标签为Z=(C1prime[1,:],C2prime[1,:]−C2[1,:])。它足以重构目标更新第一行，并由目标钥匙解码选定位。

取整数λ≥2，n=8λ，D=8ceil(log2n)，q=2^D，χ=χ640，mbar=nbar=8，B=2。逐样本两次更新正确性满足

\[
B0=288n+12,\quad
W_{noise}=288n^2D+3456n^2+12nD+144n,
\quad B0+2W_{noise}<q/8.
\]

令Q=4nD(D+1)，则ε_Q<1/4，δ0=δ1=0，得到

\[
\Delta>3/4,\qquad\operatorname{bias}>3/8,
\qquad N_{calls}=8nD(D+1)+5.
\]

这个增强游戏预算与原差分版本t+κ+2Q+5各自固定。采用各自的常数遗漏保证时，联合版本在本族的调用数更大，改进体现在更弱的适用条件。

联合方法允许任意整数模数和更新系数分布，其前提集中于公开特征、固定作用、条件分布匹配、有效表示及输出充分性。GP23和RISE的群实例未提供这一有效公开表示，Nishimaki目前属于档案文本级的条件映射。实际seeded程序、完整文献优先权和原生凭据业务需要各自证据。

## 审阅依据

- [第一阶段独立推导](D:/毕业设计/crypto_branch_monitor/round_007/independent_review_packet/review_output/phase1/PHASE1_DERIVATION.md)
- [第二阶段比对及最小补充](D:/毕业设计/crypto_branch_monitor/round_007/independent_review_packet/review_output/phase2/COMPARISON.md)
- [最终数学裁决](D:/毕业设计/crypto_branch_monitor/round_007/independent_review_packet/review_output/phase2/FINAL_REVIEW_VERDICT.json)
- [限定优先权与实例裁决](D:/毕业设计/crypto_token_exposure_priority/CONTRIBUTION_VERDICT.md)

本稿为主会话根据已审定公式和补充文本完成的整合。其数学支持与方法原创性分别依据相应记录。
