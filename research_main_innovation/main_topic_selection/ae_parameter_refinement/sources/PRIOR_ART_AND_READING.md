# 与参数加强直接相关的原文核读

版本 PR-1，2026-11-06。本轮复用已有原文与有效分析；没有新增网络检索或正文获取。模型辅助推导、公开算法出处、证明复核分别登记。

## 1. COL2019

Fedor V. Fomin、Petr A. Golovach、Fahad Panolan、Kirill Simonov，*Low-rank binary matrix approximation in column-sum norm*，arXiv1904.06141v1，2019-04-12，18页。

原文：https://arxiv.org/pdf/1904.06141v1 。本地复用ae_col2026_check/sources/column_norm2019.pdf，SHA256 `d208e61764cfdff2165e5acd80ecdd738bfd0fc38273dabc89dd497fe8d1eba3`，原结构预检PASS。

本轮定向复核p4 Definition1、p5问题/Theorem2和pp10–11 Lemma4及相应证明。p10公式已重新渲染目视，见COL2019_lemma4_page10.png、COL2019_RENDER_LOG.json。

- Definition1允许R_t随坐标变化；共同R是其子类。
- Theorem2：源记号的长度m_src、点数n_src给m_src^{O(1)}n_src^{O((k/ε)^4)}，成功概率≥1−2n_src⁻²。
- 映到本稿是n^{O(1)}m^{O((q₀/ε)^4)}；取ε=1/[2(r+1)]可配整数半径验收，但固定输入次数及确定性仍没有由此得到。
- Lemma4针对已给定分簇的Partition Center，每簇选择σ≥2个代表，给出在一致坐标上的加性误差≤OPT/(σ−1)，剩余坐标集大小≤σk·OPT。源文该取样数写r，本轮改记σ，避免误当目标半径。
- 该代表存在性/错误并集工具与本轮有关系；它没有在本轮实际读到的陈述中提供≤L−1次真分裂、活动类退役和待提交代表修正的确定性构造。相关取样与给定簇前提、输入规模指数仍需桥接。

这个比较限制在所读定义/定理及证明，没有排除其他来源或未完成归约。

## 2. PM2020

Fomin、Golovach、Panolan，*Parameterized low-rank binary matrix approximation*，Data Mining and Knowledge Discovery34:478–532，2020，DOI10.1007/s10618-019-00669-5。

公开期刊offprint：https://fedorvf.github.io/articles/2020/2020f.pdf 。本地ae_pm2020_check/sources/PM2020_author_public_offprint.pdf，SHA256 `0139e81f066a11fc4c17870cfa1f8596612b42334025efacfa0be36377d56c91`，57物理页（2封面+55正文/参考），印刷页=物理页+475。原预检UNAVAILABLE及两对象偏移警告保持，前轮双解析和公式目视记录沿用。

本轮复读印刷pp521–523（物理46–48）的Extendable定义、Lemma11完整代表枚举、Lemma12的枚举及最终总距离判据、Th7陈述及预处理。前轮§7完整核读继续按其记录，不扩大成本轮新独立全文验证。

- 模板p×b，要求非空角色，总编辑K；与最大逐行r的合同差别保持。
- Lemma11：ℓ种输入列下ℓᵇpoly(mn)个代表选择。b=L仍可能出现nᴸ，或经总预算核出现(L+mr)ᴸ。
- Lemma12：未决列u=|Y|+|Z|时，2^{O(p(u+logK)+p logp+b logb)}poly(mn)，还需p+K/b+K类型上限；最终按全体行距离求总和≤K。
- 原式没有直接使p=q₀≤2ᴸ的重复选择变成本稿活动类的结构历史。需要重新建立C3/并集预算/可计算提交，属于新增桥接责任。

总预算K=r及K=mr的既有反例继续有效。PM2020指定正文缺口已关闭，当前仍按PARTIAL_OVERLAP；这里没有把较慢上界当作下界。

## 3. 分区细分与零误差

有序满二叉树形≤4^k、叶块映射≤(k+1)^L、内部节点行步标记≤k^k，均为本轮给出自含编码的初等组合工具。标准树形计数本身不提供构造的发表优先权，也不负责安全消除常值位；后者由C3单独证明。

既有EQUIVALENT_FORMULATIONS §7在r=0时枚举≤L种不同输入列类型到模式的映射，得到L^{O(L)}poly(mn+qL)。该特例是强基线。正半径同签名坐标可能分拆，本轮没有直接延用零误差的统一分配断言。

## 4. 其他指定源与过程记录

KU完整作者稿、Damaschke2013两页正式预览沿ae_local_edit_priority/PRIORITY_UPDATE使用：图团目标、双侧局部预算、簇数d及核大小均不与任意模板单侧预算自动等同。D13的435–437页、KU期刊版对应及COL2026正式正文继续待核。

本轮输入哈希及只读快照见INPUT_MANIFEST.json。原路线的来源按研究者最新校正记为AI辅助回复提出、研究者转交组织；本轮C3和加强过程为当前知情模型辅助推导，非外部意见。

发表优先权继续未决；本轮没有以“未检出”或自产通用构造认定公开先例不存在。
