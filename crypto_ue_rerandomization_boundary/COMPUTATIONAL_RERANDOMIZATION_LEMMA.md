# 公开线性混合的计算型引理

ROUND-006，2026-11-07。结论：**VERIFIED，标准 normal-form LWE 的直接推论**。mod 2 选基版本明确限于 q=2^D。该工具本身尚未提供新协议或严格资源分离。

## 1. 源实验与目标实验

令 d≥1、κ≥0，t=2d+κ，χ 可有效采样。源实验为

\[
(A_0,v),\quad A_0\leftarrow U(\mathbb Z_q^{d\times d}),\qquad
v=sA_0+e\ \text{或}\ v\leftarrow U(\mathbb Z_q^d),
\]

其中 s,e 独立 χ^d，源优势 δ_nf 采用两种输入下输出1的概率差。目标为

\[
(M,rM)\quad\text{与}\quad(M,U_d),
\qquad M\leftarrow U(\mathbb Z_q^{t\times d}),\ r\leftarrow\chi^t.
\tag{CR}
\]

χ 可以非均匀。归约是分布推论；其困难性须对具体 d、q、χ 成立。

## 2. 完整归约与真实分布

归约先独立采 L∈Z_q^((d+κ)×d)。令 G 表示 L mod2 满列秩。G 上按固定高效规则选择行索引 I，|I|=d，令 B=L_I，其余行记 C=L_(Iᶜ)。B 在 Z_(2^D) 可逆。选择规则仅依赖 L，完整 L、I 和 B 都可保留。

给定源 (A₀,v)，构造

\[
M=\begin{bmatrix}A_0B\\L\end{bmatrix},\qquad
z=vB+wC,\quad w\leftarrow\chi^\kappa.
\tag{R}
\]

目标系数按**原行索引**赋值：上 d 行取 s，下块选中 I 的 d 行取 e，余行取 w。条件于任意固定 L∈G，A₀B 为均匀 d×d 矩阵，并独立于 L；s、e、w 仍相互独立 χ，行选择未读取它们。源为真实 LWE 时

\[
z=(sA_0+e)B+wC=s(A_0B)+eL_I+wL_{I^c}=rM.
\]

因此 (R) 精确生成目标真实分布条件于 G 的联合律，包含所有选基信息。选择信息是 L 的确定函数，额外公布它并不增加本证明的隐藏义务。

源为均匀时，固定 A₀、L、w 后 vB 仍独立均匀；加 wC 保持均匀。于是精确生成目标均匀分支条件于 G。

Gᶜ 时归约忽略源，独立采上块和 r，输出真实目标样本交给判定器。两种源在该分支给出相同输出分布。将目标 signed gap 按 G/Gᶜ 分解可得

\[
\operatorname{Adv}_{CR}(\mathcal D)
\le\operatorname{Adv}_{nfLWE}(\mathcal B)+\delta_{\rm rank}.
\tag{CR-bound}
\]

这里没有除以 Pr(G)；失败部分的目标差绝对值至多 δ_rank。也可条件化／拒绝采样得到另一种模拟，但须相应支付时间及分布距离。本轮使用上面的有界无重试归约。

## 3. 失败率、复杂度与样本

均匀 (d+κ)×d 二元矩阵的精确满列秩概率为

\[
\Pr(G)=\prod_{i=0}^{d-1}(1-2^{i-d-\kappa}),\quad
\delta_{rank}=1-\Pr(G)
\le2^{-\kappa}(1-2^{-d})<2^{-\kappa}.
\]

这是逐列计数及乘积并集界。单次归约消耗一个 nf-DLWE(d,d,q,χ) 实例，共 d 个同秘密样本；自行采 κ 个 χ 系数。开销为二元行选基、环矩阵乘法 O(d³+κd²)，以及 O(κd+d²) 的向量计算；所有环操作按 D 位收费。输入维度、D、κ 及采样时间为 poly(λ) 时归约为 PPT。κ≥λ+⌈log₂J⌉ 可把 J 次使用的秩失败并集界压至2^−λ；计算优势还须 J 次混合总计。

上述 κ 个系数指 G 分支；Gᶜ 的 dummy 真实样本至多自行采 t 个 χ 系数及 d² 个均匀环元素。最坏采样预算取两者最大值，仍有界多项式，无拒绝重试。

M 可带有能由 M 与独立已知随机量生成的上下文 W；归约照样生成 W 并运行判定器。若 W 涉及源秘密、r、隐藏选择币或 M 的不可生成密钥关联，需新的辅助信息证明。CR 没有给任意关联辅助信息的免费保证。

## 4. 模数和分布反控制

**COUNTEREXAMPLE（一般 q 上直接 mod2 选基）**：q=3，B=[[1,2],[2,1]] 的 mod2 满秩，但 det B=−3，模3奇异。于是 A₀B 无法保持全矩阵均匀。q=p^D 时可改用 mod p 满秩；精确失败率为 1−∏_(i=0)^(d−1)(1−p^(i−d−κ))≤p^−κ/(p−1)。一般合数需要另行处理单位子式，当前证明未扩张到该域。

**COUNTEREXAMPLE（偶数模数与 χ=U({−1,+1}) 的困难性）**：r mod2 恒为全1，故 rM mod2 等于 M 的各行之和，可公开检查。真实接受率1，均匀接受率2^−d，gap=1−2^−d。源 sA₀+e mod2 同样是公开已知值，nf-LWE 假设也失效。CR 的条件蕴含仍正确；由它推出该分布伪随机性会使用一个已被反例推翻的前提。

这项反控制约束把 Nishimaki 的打印 ±1 系数直接移到 q=2^D 的尝试；前驱的完整模数约束尚待核准，本文据此没有宣称破坏其原参数定理。

## 5. 工具来源与分类

Peikert2016 PDF p25／印刷p23 的 normal-form 变换已将均匀块消元为“小秘密＋小误差”；p39／印刷p37 说明 Regev 的 normal-form 参数优化；p41／印刷p39 的 dual Regev 证明在均匀公钥下直接用 LWE 响应替换；p42–43／印刷pp40–41 的 LP11 紧凑方案用两次 nf-LWE，替代 statistical regularity。相关页已定向阅读，关键原图核准范围见 sources 记录。

CR 将已知的 [A₀;I] 型 nf-LWE 输出经公开可逆 B 变换并加自采行，属于这些标准工具的直接分布推论。本轮没有定位逐字相同的 t=2d+κ 定理先例，因此精确文句的发表优先权留项；其内容分类为 **DIRECT_COROLLARY_OF_STANDARD_NORMAL_FORM_LWE**，无需新通用抽取假设。

普通 Regev 的高熵统计 proof、dual Regev 的 LWE 输出 proof 和 CR 的条件性应分别保留。将“均匀公开矩阵＋计算伪随机线性输出”视作完整 UE 安全定理，仍缺 COMPOSITION_AND_CORRECTNESS 中的联合混合责任。
