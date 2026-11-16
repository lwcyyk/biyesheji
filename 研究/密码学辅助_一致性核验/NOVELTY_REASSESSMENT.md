# 原创性重新核验：收缩主张，而不是更换名字

## Material Passport

origin_skill: academic-research-suite；origin_mode: citation-and-counterargument；origin_date: 2026-11-02；verification_status: UNVERIFIED；version_label: crypto-aux-novelty-02；repro_lock: null。

结论：目前可以提出并分析“支持集泄漏受限的稀疏诊断构造”，但还不能确认达到用户要求的较强独立密码学原创性。真实 MPC 接入增加了实现证据，不构成原创性证明。

## 最直接的已核实先例

**Dan Boneh、Elette Boyle、Henry Corrigan-Gibbs、Niv Gilboa、Yuval Ishai，Arithmetic Sketching，CRYPTO 2023。** DOI：[10.1007/978-3-031-38557-5_6](https://doi.org/10.1007/978-3-031-38557-5_6)。[ePrint](https://eprint.iacr.org/2023/1012)，[机构全文](https://ntt-research.com/wp-content/uploads/2023/08/Arithmetic-Sketching.pdf)。

本轮核对了摘要、§4.1–4.2、Lemma 18、Construction 21、Theorem 22、Corollary 23 及相关附录片段。该文已处理低汉明重量的算术草图，使用 Hankel 秩结构，并区分秘密计算和公开判定；其动机也包括不依赖持有完整见证的单一客户端。因此以下内容均不能作为本项目独立创新：低维线性草图加小 MPC、通过矩阵秩检查稀疏性、不需要额外客户端证明、公开判定经过隐藏的草图。我们的移位矩阵与其具体矩阵不同，不足以据此断言具有实质新颖性。

**Elette Boyle、Niv Gilboa、Yuval Ishai，Function Secret Sharing: Improvements and Extensions，CCS 2016。** DOI：[10.1145/2976749.2978429](https://doi.org/10.1145/2976749.2978429)；[完整版本](https://eprint.iacr.org/2018/707.pdf)。其线性草图核验是更早先例；完整版本 Claim 4.5 的逆元草图适用于任意有限域，某些平方公式另要求特征大于二。不能把特征二中某个未经限定的平方公式反例写成整个 FSS 或 Express 系统漏洞。

**Marc Damie，SparseMPC: Secure Sparse Operations using Multi-Party Computation，2026 预印本。** [原文页面](https://eprint.iacr.org/2026/1675)。本轮仅核实摘要与元数据：重点为 outsourced MPC 的 Scatter、Gather 与稀疏矩阵运算。没有据此断言它覆盖或不覆盖我们的诊断功能；全文关系仍待核对。

**Marcel Keller、Emmanuela Orsini、Peter Scholl，MASCOT: Faster Malicious Arithmetic Secure Computation with Oblivious Transfer，CCS 2016。** DOI：[10.1145/2976749.2978357](https://doi.org/10.1145/2976749.2978357)；[原文](https://eprint.iacr.org/2016/505)。这提供本轮采用的恶意安全算术底座，而不是本项目发明。

## 当前贡献拆分

| 项目 | 本轮证据 | 可作出的表述 | 不可作出的表述 |
|---|---|---|---|
| 移位矩阵/稀疏 gate | 原条件性证明、已有论文近邻 | 一种可实现的 gate 选择 | 新稀疏核验原理 |
| 3k−1 乘法掩码层 | 明确转置公式、受限下界、有限验证 | 利用经典算术得到的具体实现与成本边界 | 首创中间积或全协议最优 |
| 秘密范数组合 | 原模拟误差界和反例 | 对完整转录计入误差的设计与分析 | 首创范数或首创安全放大 |
| 三点无零 affine 掩码紧界 | 新的完整下界及可达性推导、675 个分布比较 | 本项目推导出的受限隐私权衡定理 | 已确认的首创一般密码学下界 |
| 一般多项式掩码的紧模拟界 | 群平均归约、MDS 满重量计数、匹配分布、58 组计数检查 | 更强的限定模型最优权衡候选；见 TIGHT_LEAKAGE_BOUND.md | 新 MDS 重量公式或已确认的原创密码学定理 |
| 支持集泄漏受限的定位功能 | 掩码、公开解码、遗漏复核联合规格 | 继续核验独立新颖性的候选贡献 | 已排除所有草图/随机编码先例 |
| MP-SPDZ 两方实现 | 固定版本、真实预处理、同功能基线 | 诚实执行和成本的开发验证 | 新主动安全底座、实用端到端 TLS 系统 |

## 反方审查

1. 最强反驳是：现有算术草图完成 gate，再以已有稀疏插值与随机化技术实现定位，可能就是自然扩展。必须正面比较，不能凭没有找到完全相同标题认定原创。
2. 三点紧泄漏界及进一步的一般多项式掩码模拟紧界虽然比“存在泄漏反例”更完整，仍可能是已知群作用/随机编码结果的推论。MDS 满重量计数属于经典结果；将它用于这里的隐私游戏是否足够新，必须独立核验。
3. 乘法数不是总成本。随机相关量生成、输入共享、公开解码和 MAC 检查均可能主导实测。当前简单基线在小批次和在线耗时上存在优势。
4. 稀疏定位允许泄漏错误位置。若主线真正需要的是完全隐藏失败位置，本功能不适配，不能通过重新命名掩盖泄漏。
5. 残差来源绑定尚未实现。仅给任意输入 d 作诊断，不能解决执行器向 AI 代理提供虚假服务语义证据的问题。
6. 没有外部审稿人、第二模型独立审查或证明助手认证；本文件是本轮自审，不将其包装成独立专家结论。

## 下一步进入条件

需要先完成“同功能归约审查”：将 Arithmetic Sketching 的 gate 与最直接的私密定位实现列为明确基线，检查当前协议是否只是其参数化实例。对紧泄漏界检索 affine randomized encodings、support disclosure、multiplicative masking、zero-free polynomial masks 的直接先例。若均为自然推论，应如实定位为机制优化与安全工程，不继续声称强独立密码学原创。

真正可提升原创性的方向是证明一项已有方法不直接给出的诊断功能/泄漏/成本权衡，并提供匹配构造；本轮的紧界是这种形式的一个受限候选，还不满足完整优先权核验。不得为了达成目标临时降低安全定义、删去负控制或改变成本函数。
