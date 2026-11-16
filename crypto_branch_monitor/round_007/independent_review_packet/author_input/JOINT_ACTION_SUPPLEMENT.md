# 合并作用学习：ROUND-007的纸面补充

ROUND-008，2026-11-07。由主会话提出，当前会话作知情核查；没有新增独立审阅。原ROUND-007文件保持原字节。输入锁SHA-256：**a8176e46d4ca369b477399f0af20a811e9c87d4898c26f88bdd21bf646523c98**，见 `sources/input_record.json`。

**结论：VERIFIED，既有Module引理的标准直接应用。** 它删除了分别提取N所需的奇偶／秩条件，进一步弱化类定理的前提。

## 1. 直接学习目标作用

固定token，令

\[
W=\begin{bmatrix}K\\N\end{bmatrix}\in\mathbb Z_q^{(g+t)\times d},
\quad X=(H,r),\quad Z=XW,
\]

q≥2为任意整数。公开H可有效计算，普通完整带可解码r；所有未写入X的新输出项须已知且可扣除。为Q个独立诚实普通父各执行一次普通更新，获得(X_i,Z_i)。条件于固定参数、epoch钥匙和token，训练X_i必须为iid；各Upd新币来自公开可采的真实分布并独立于父加密币。

fresh挑战H*与训练H同律；另在成员测试之前独立采合法本地更新币r_loc，置X*=(H*,r_loc)。于是X*与训练X_i条件iid。在V=Z_q^(g+t)应用Module引理：

\[
\Pr_0[X^*\notin L_Q]\le
\epsilon_{joint}:=\min\{1,(g+t)\log_2q/(Q+1)\},
\quad L_Q=\operatorname{span}_{\mathbb Z_q}(X_1,\ldots,X_Q).
\]

若X*∈L_Q，求λ使X*=Σλ_iX_i，精确计算Σλ_iZ_i=X*W，即真实本地Upd所需的token作用。任意整数q可用带变换记录的整数HNF/SNF，在rows_Z(X_i)+qZ^(g+t)中求表示；无需模2主元或q的因数分解。输出位长与时间为输入维度及logq的多项式。

## 2. 分类与正确性

保留同一合法轨迹：epoch1普通父、epoch2训练Enc与Challenge、Next3隐藏token并跳过Get、对Q个训练父各一次UpdLeak、Key3。X*不在L_Q时输出update；在模内时用所得精确作用生成真实Upd输出，解密为M₀时输出fresh，其余输出update。

令m₀为fresh的联合遗漏概率，e₀为fresh在模内却解密标签出错的概率，e₁为update在模内却解密为M₀的概率。则

\[
p_0=m_0+e_0,\quad p_1=1-e_1,
\quad p_1-p_0=1-m_0-e_0-e_1.
\]

若一／两次更新的错误率分别≤δ₀、δ₁，

\[
\Delta\ge\max\{0,1-\epsilon_{joint}-\delta_0-\delta_1\},
\qquad\operatorname{bias}=\Delta/2.
\]

这里同样无需update挑战H的同律条件。本地r_loc无论最终是否落模都先独立按真实分布产生，可用一份虚拟真实更新界定错误事件。

## 3. 权限、次数及范围

调用数为EncLeak Q+1、UpdLeak Q、Next 2、Challenge 1、Key 1，总数**2Q+5**；Token/Get/Dec为0。训练父在Challenge前固定。无需同父重复、无需N可逆／方阵、无需任何χ奇偶平衡；甚至单独N信息论不可辨认时，合法目标的作用仍可学习。

原SELECT最终K*={3}、T*=∅、C*={2}。原FI的Next登记新C，仍使该未来钥匙轨迹非法；本补充没有修改任何游戏闭包。真实采样失败与错误响应按原规则处理，有限迁移仍需逐分支耦合损失。

对ROUND-007 CF2的同一数值构造，另立本补充预算Q=4(g+t)D，q=2^D。其两次更新逐样本正确性保持，故Δ>3/4、bias>3/8，总预算2Q+5。该预算与旧CF2及更早3n+1预算分别记录，未宣称查询数单调减少。

此结果是有限模线性作用学习的直接推论。其用途是更准确的实例分类与增强接口边界，通用数学方法的原创性主张为0。它不设计修复机制，也不提供原型。
