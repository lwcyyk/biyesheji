# 图嵌入下界：准确源定理与ETH前提

版本 EL-1，2026-11-07（Asia/Shanghai）。任务 AUTO-RESEARCH-ETH-004。当前对话内知情模型辅助原文核读与纸面证明。外部数学复核及形式化验证待取得。

## 1. 已绑定的主来源

Marek Cygan, Fedor V. Fomin, Alexander Golovnev, Alexander S. Kulikov, Ivan Mihajlin, Jakub Pachocki, Arkadiusz Socała.
**Tight Lower Bounds on Graph Embedding Problems.** Journal of the ACM 64(3), Article 18, June 2017, 22 pages. DOI [10.1145/3051094](https://doi.org/10.1145/3051094).

实际取得：[作者公开JACM排版PDF](https://fedorvf.github.io/articles/2017/2017d.pdf)，本地sources/CFGKMPSo2017_author_JACM.pdf。

- 首页直接给题名、七位作者、完整ACM引用、DOI和22页说明；页脚为JACM64(3)、Article18、June2017。
- DOI内容协商取得题录元数据，作者/题名/卷期及22页长度匹配，在线日期2017-06-16；元数据另列印刷日期2017-06-30。文章号18取自PDF首页及印刷页码，元数据的article-number字段为空。首页按June2017记。
- 本文件为作者网站公开的期刊排版副本，内部身份直接绑定正式论文。本轮未与ACM网站另下载文件作字节比较。
- SHA256：`efb2e8b9236c354a2bda126597696e7b304170df2fb2330437e1ed84a0331b1b`；PDF结构预检PASS，物理22页。预检仅验证结构。

下文“18:x”指印刷页号，也恰为物理第x页。相关整页图及预检见sources。

## 2. 源模型与被引用的定理

18:4定义普通Subgraph Isomorphism：存在单射π:V(G)→V(H)，满足

\[
uv\in E(G)\Longrightarrow \pi(u)\pi(v)\in E(H).
\]

非边没有保留要求。18:7的Preliminaries明确全文考虑**简单无向图**，无环及重边。源图G为待嵌入图，H为宿主；18:19重述时符号次序互换，命题方向仍是普通包含关系。

**Theorem 1.3，18:7，准确原文：**

> Unless ETH fails, there is no algorithm solving SUBGRAPH ISOMORPHISM for graphs G and H in time 2^{o(n log n)}, where n = |V(G)| = |V(H)|.

因此可直接使用两个同阶图；本项目归约无需补孤立点或调用不同规模下界。有限n=0/1不影响渐近排除。

**Theorem 4.5，18:19（Theorem 1.3 restated）：** ETH下存在常数c>0，排除时间O(n^{cn})的同阶普通子图包含判定算法。本文最终使用1.3的little-o表述，避免把此c与T+输入多项式次数混用。

这是判定下界。源定理不要求算法返回嵌入；目标若还要返回模式、行标签和全部中心，只会具有更强输出要求。项目另给从任意目标可行解恢复嵌入的确定性多项式过程。

## 3. ETH、随机性与多项式因子

18:8的ETH问题框：存在常数q>0，使n个变量、m个子句的3-CNF-SAT无法在2^{qn}(n+m)^{O(1)}时间求解。本文使用通常的**确定性ETH**口径。

Theorem 1.3的正文写2^{o(n log n)}，没有再显式乘输入多项式。对两个显式n顶点简单图，编码长度为n^{O(1)}，任一固定多项式因子等于2^{O(log n)}，可吸收入little-o指数。因此其直接排除

\[
2^{o(n\log n)}\operatorname{poly}(\text{graph encoding}).
\]

本轮只对确定性目标算法转移下界。有限枚举、贪心构造及复制均确定；没有将普通ETH升级为随机化ETH，也未声称源定理排除所有随机算法。

## 4. 已核读的源证明依赖

|源位置|实际命题/作用|参数及费用|
|---|---|---|
|18:8 Proposition 2.1 / Lemma 2.2|从ETH得到度至多4图的3-COLORING指数下界|存在q>0排除O*(2^{qn})；引用标准前置结果，本轮未重读其全部外部原始文献|
|18:9–12 Lemmas 3.1/3.2|平衡着色和分桶；分桶图平方着色、桶独立、桶间至多一边|固定最大度d；确定性多项式贪心算法，桶数≤n/r_s；源r_s为分组参数|
|18:12–14 Lemma 3.3|3-COLORING→List Graph Homomorphism|输入n顶点最大度d，r_s=o(√n)；输出≤n/r_s和≤γ(d)^{r_s}个顶点；poly(input+output)|
|18:14–17 Lemma 3.4、Claims 3.5–3.8|用锚gadget消除同态列表|输入规模(n,h)，h≥3；输出≤n+25h²和≤25h²；多项式；任意同态的投影保留列表|
|18:17–18 Theorem 4.1（重述1.1）|ETH下Graph Homomorphism的n log h级下界|任意固定D>0；合理非降、可构造3≤h(n)≤n^D；存在c(D)>0排除O(2^{c n log h(n)})|
|18:19 Theorem 4.4及完整证明|同态→多个同阶Subgraph Isomorphism实例|p=n_h+h_h；≤2^p个实例，每图n_h顶点；总构造poly(p)2^p；YES为OR|
|18:19 Theorem 4.5|由4.1+4.4得到1.3|取h_h≤n_h的适用区间，枚举费为2^{O(n_h)}，可被n_h log n_h尺度吸收|

这里r_s、源n_h/h_h、ETH常数q和源D均与项目半径1、模式数w、标签数K无关。

### 4.1 Theorem 4.4的实际OR归约

枚举同态各宿主顶点的原像大小(a_z)_{z∈V(H)}，非负、总和n_h。向量数量

\[
\binom{n_h+h_h-1}{h_h-1}\le2^{n_h+h_h}.
\]

宿主z复制a_z次，同一原型的副本形成独立集；原宿主的每条边展开成相应完全二部边。图G保持，宿主副本总数也是n_h。同态可提升为每个原顶点用私人副本的双射，任一嵌入按副本原型投影回同态。

这是源论文自身的指数时间多实例归约。若同阶子图可在2^{o(n_h log n_h)}时间求解，取h_h≤n_h，全部调用与构造为

\[
2^{O(n_h)}2^{o(n_h\log n_h)}\operatorname{poly}(n_h)
=2^{o(n_h\log n_h)},
\]

与Theorem 4.1的h(n_h)=n_h子情形矛盾。若用4.5的固定小常数版本，先选比4.1常数更小的指数，再让O(n_h)项被剩余n_h log n_h项支配。

本项目从1.3继续时只新增一个多项式、单实例映射。源2^{O(n_h)}枚举费已由发表定理证明支付，无需再错误地把它乘进项目的同阶图输入规模。

## 5. 版本及早期弱界的区别

### 5.1 同题2016预印本

取得arXiv:1602.05016v1（2016-02-16），23页，首页七位作者及同题；首页同时说明初步版本发表于ICALP2015和SODA2016。JACM首页也有这一声明。arXiv当前条目没有本轮可见的期刊DOI声明；本文依据题名、作者、版本正文对应和期刊首页身份分别记录，不推定全文逐字相同。

本轮定点读取v1首页、p6及pp18–19：

|2016v1|JACM2017|影响|
|---|---|---|
|Theorem 3，p6，n=两图顶点总数；后段明确同阶子情形|Theorem 1.3，18:7，直接用每图阶n|只是本轮相关参数陈述更明确；同阶时总数=2n，little-o尺度等价|
|Theorem 6，p18；输出图数≤2^p，证明中每图|V(G)|顶点|Theorem 4.4，18:19，陈述直接写每图|V(G)|顶点|以正式版及两版实际复制证明为准|
|Theorem 7，p19，排除O(n^{cn})同阶判定|Theorem 4.5，18:19|同级下界；本轮绑定JACM版本|

未宣称2016稿全部23页均已证明复核。其余部分只作定位；主证明阅读依据为JACM18:6–19。

### 5.2 另一项早期工作

arXiv:1504.02876（2015-04-11），**The Hardness of Subgraph Isomorphism**，Marek Cygan、Jakub Pachocki、Arkadiusz Socała；本轮只读取公开条目的题录和摘要，正文未读。

该摘要宣称其自有归约给2^{Ω(n√log n)}下界，组合当时同态结果可得近紧2^{Ω(n log n/log log n)}。它是不同题名、不同作者集合的早期工作，不能用其弱界替代本轮已核实的JACM1.3；本轮紧下界也不借这份摘要证明。

## 6. 阅读与责任范围

实际核读范围：首页；18:4的Subgraph定义；18:6–8的主定理、图定义和ETH前提；18:9–19的相关引理及证明，包括§3.1/§3.2以及§4.1/§4.2所需构造、计算。18:20–22主要作参考文献和发表信息定位，其他应用未审。

pypdf在部分符号上输出`/Delta1`、作者名和间距异常；关键定理/参数回到PDF整页目视核对。结构预检无修复警告。没有把源论文发表地位或结构PASS等同于本项目独立数学验证。

- **已发表责任**：ETH→同阶Subgraph Isomorphism的n log n下界及全部源OR归约。
- **项目当前证明责任**：同阶子图到共同关系层A的精确归约、任意解恢复、追加列强制真正正半径、显式参数计费。
- **优先权范围**：项目这段映射是否早有发表先例仍待核；本轮仅对其数学正确性给出知情模型辅助纸面证据。
