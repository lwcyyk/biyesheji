# T3其他先例与通用框架：来源与定理表

版本 AF-1，2026-11-06。当前对话内的知情模型辅助文献核读与纸面归约。数学状态沿用 T3_SUPPORTED_BY_INFORMED_AUDIT；外部数学读者复核仍待取得。历史目录保持原字节。

本轮采用 academic-research-suite 的来源核查流程及 PDF 读取流程。获取、提取、哈希和页面渲染仅承担文档取证；候选机制、求解器及数学穷尽程序均未实现。

## 1. 冻结对象与范围

输入 A∈{0,1}^{m×n}，共同显式关系 R={ρ¹,…,ρᴸ}⊆{0,1}^q，m,n,q,L≥1，r≥0。寻找 y_t∈[L] 与每行一个全串固定标签 s_i∈[q]，使

\[
\forall i\in[m]\quad \sum_{t=1}^{n}[A_{it}\ne \rho^{y_t}_{s_i}]\le r.
\]

允许重复与闲置中心、闲置模式；恢复全部原有序中心 C_s[t]=ρ_s^{y_t}。目标

\[
F_3(L,r)\operatorname{poly}(mn+qL),\qquad
F_3=2^{O(L\log(L+2)+Lr\log(Lr+2))}.
\]

COL2026：P26_SOURCE_UNRESOLVED；ACTIVE_RETRIEVAL_PAUSED_BY_USER。本轮未获取、索稿或检验该文版本。既有 COL2020、PM2020、KU 作者稿和 Damaschke2013 的局部结论继续分别管理。

四项指定历史输入及 SHA256 已固定于 sources/INPUT_MANIFEST.json，并有只读内容副本。复用结论的范围见原 ae_t3_closure_audit/T3_PRIOR_ART_DELTA.md 与 ae_t3_p26_coverage/COVERAGE_TEST.md。

## 2. 取得的来源及版本绑定

|编号|来源与身份|版本关联及完整性|本轮实际核读|
|---|---|---|---|
|NF25|Jansen, Kahler, Pirotton, Tutas, New Algorithm for Combinatorial n-Folds and Applications；IPEC 2025，LIPIcs 358，15:1–15:15；DOI 10.4230/LIPIcs.IPEC.2025.15|[正式入口](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.IPEC.2025.15)及正式15页PDF；入口和首页明确链接 arXiv:2409.04212 完整版；正式出版日期2025-12-15|正式全文15页；重点 §§1–3、Theorem 1、Lemma 5、Lemmas 6–13、Algorithm 1、Corollary 3及引用表|
|NF25-F|[arXiv:2409.04212v4](https://arxiv.org/abs/2409.04212v4)，2025-10-09，31页|首页明示v4；正式入口关联到该 arXiv 记录。按所用定义和证明实际对照；没有推定两个文件逐字节相同|pp1–13、16–25、29–31；含 Appendix A 的遗漏证明、Algorithm 2/3，以及 B.2 Closest String 的实际ILP和slack块。pp14–15参考文献用于追踪；调度应用不承担T3覆盖判断|
|FS21|Bandyapadhyay, Fomin, Golovach, Simonov, Parameterized Complexity of Feature Selection for Categorical Data Clustering；MFCS 2021，LIPIcs 202，14:1–14:14；DOI 10.4230/LIPIcs.MFCS.2021.14|[正式入口](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.MFCS.2021.14)和14页正式PDF；首页直接关联 arXiv:2105.03753；出版2021-08-18|正式全文；重点问题框、Definition 3、Theorems 1/2/4/8/9、Lemmas 10–12、Observation 13、Lemmas 14/15及§4.4|
|FS21-F|[arXiv:2105.03753v2](https://arxiv.org/abs/2105.03753v2)，2021-08-19，25页|首页给会议DOI；正式记录关联同一arXiv。完整稿实际补读所依赖的采样存在性证明|首页、pp4–5、8–13，特别 pp10–13 Lemmas 10–12、Observation 14、Lemmas 15/16、Theorem 4；其余结果仅作定理/引用定位，未宣称逐项证明复核|
|FS23-M|同题同作者；ACM Transactions on Computation Theory 15(3–4)，1–24，2023；DOI 10.1145/3604797|DOI内容协商取得出版元数据，在线日期2023-12-12；出版方HTML和元数据直链PDF均返回403错误HTML。正文未取得|元数据；SOURCE_UNRESOLVED 仅针对该期刊版本及其变化。会议/预印本已读结论独立成立|
|KKM17|Knop, Koutecký, Mnich, Combinatorial n-fold Integer Programming and Applications；ESA 2017，LIPIcs 87，54:1–54:14；DOI 10.4230/LIPIcs.ESA.2017.54|[正式入口](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ESA.2017.54)，14页正式PDF；首页明确链接 arXiv:1705.08657|正式pp1–6的模型/Theorem 2/3；本轮依赖的恢复及扩展证明另由关联完整稿列明读取；主要覆盖费用由正式源定理承担|
|KKM17-F|[arXiv:1705.08657v2](https://arxiv.org/abs/1705.08657v2)，2017-11-08，25页|完整稿首页反向关联ESA；入口comments“245 pages”与实际25页不符，页数采用PDF结构核对值|pp1–5、11–16、20–21；Definition 2、Theorem 3、§3.4可行性/恢复、Theorems 19/20、Definition 22/Corollary 23|
|KKM20|同题同作者，Mathematical Programming 184:1–34 (2020)，DOI 10.1007/s10107-019-01402-2|由NF25正式参考文献28定位，出版方[完整PDF](https://link.springer.com/content/pdf/10.1007/s10107-019-01402-2.pdf)正常取得；PDF首页/元数据含同一DOI，并声明ESA2017为extended abstract；34页完整；在线2019-11-20、卷年2020|pp1–9、14–21、25–29；Theorem 1及其恢复、Lemma 9、§4.2 succinctness、Theorem 3/Corollary 1/Theorem 4、Theorem 6及其配置证明、Definition 3/Corollary 2|

本轮从两条主线引用链中，选择 KKM17/KKM20 这项工作的正式会议版、完整稿和期刊最终版作实质核查：它直接提供块数进入固定多项式、宽度进入参数项的另一侧包络，可能改变 NF25 单独代入的判断。Gramm/Marx 仅作为引文线索；错误或失效主页请求没有取得原文，未给它们新增定理覆盖裁决。额外精读论文为一项工作，三个明确版本。

全部PDF结构预检为 PASS（STRUCTURE_ONLY）。PDF字节、页数及警告见 sources/PDF_METADATA.json、各 preflight sidecar、SOURCE_MANIFEST.json。pypdf 的 layout 提取对旋转边栏给出 incomplete 提醒；后续采用普通提取并目视检查关键整页。结构PASS不承担数学正确性或人工核读证明。

## 3. NF25的独立参数字典与源定理

使用 ν 表示块数，a 表示全局行数，w_b 表示第b块宽度，H=Σ_b w_b，Δ 表示系数绝对值上界，λ 表示完整二进制表示长度，避免复用T3的n/r/L。

源结构（正式15:2，完整稿p2）为

\[
\sum_{b=1}^{\nu}D_b x^{(b)}=\beta^\uparrow,\qquad
\mathbf1^\top x^{(b)}=\beta_b^\downarrow,\qquad
x^{(b)}\in\mathbb Z_{\ge0}^{w_b},
\]

D_b∈Z^{a×w_b}可随块变化。局部部分每块恰为一个全1行。源定理没有另带任意变量上下界；非负性和局部和给出 x_j^{(b)}≤β_b^↓。下端负RHS直接不可行。本文使用的全部RHS非负、目标恒为0。

**Theorem 1（正式15:3及15:12；完整p3及p12）** 声称线性目标最大化可在

\[
(\nu a\Delta)^{O(a)}\log\beta_{\rm def},
\quad \beta_{\rm def}=\min(\max\beta^\uparrow,\max\beta^\downarrow)
\tag{NF}
\]

时间求解。非负系数可行性版本为 Lemma 12（正式15:9–11；完整p10–11、22–25）；负系数由Lemma 13平移，每项增Δ，Δ′≤2Δ，RHS增加ΔΣβ_b^↓。本轮归约均可直接保持非负。

源过程为确定性DP、有限枚举、精确卷积及确定性小ILP调用。没有随机成功事件或需候选提供的优化oracle。实际可行解可存基表解与DP分解指针，逐次恢复 x^(i)=2x^(i−1)+x̃^(i)；整数位长为O(log(2+||β||∞))。完整显式解写出仍须Ω(H)项。

**输入/宽度补账。** 正式15:11及完整p25的简化式写出 H≤(Δ+1)^a。对非负、逐块不同矩阵，安全规范化是每块合并相同上端列，得到 w_b≤(Δ+1)^a、H≤ν(Δ+1)^a；有符号时用2Δ+1。读入、合并、保存原列ID及输出H项均单独计费。在我们的有限显式实例中，采用保守且足够的端到端包装

\[
\operatorname{poly}(\lambda)+(\nu a\max(1,\Delta))^{O(a)}
\operatorname{polylog}(2+\|\beta\|_\infty).
\tag{NF+}
\]

它保留原参数优势，也防止任意宽度成为免费输入。0/1 RHS边界将log按1+log记账，或直接处理退化实例。

阅读观察：正式式(2)/完整稿对应式使用K+z，完整Algorithm 2第11行使用K−z，正文称取K或K−1。本轮未依赖该内部符号差异判废来源；覆盖审查按源定理声称的有利保证(NF+)进行。T3映射的障碍在接受该保证时仍成立。

### Closest String应用

正式15:3 Corollary 3；完整B.2 pp29–30。源k为输入串数，源长度写h，源半径写d，T是输入列的相等关系类型数，得到

\[
((T+1)k)^{O(k)}\log(h).
\]

二元原始列型可不作符号归一化直接精确压缩；本文按完全相等的输入列型计T，给强基线保留所有可用归一化机会。源k对应受预算约束的输入对象数，无法仅凭命名变成关系模式数L。

## 4. NF25与完整稿的相关对应

|内容|IPEC正式页|完整v4页|与覆盖相关的检查|
|---|---|---|---|
|不同宽度、不同D_b、局部全1|15:2|2|同一结构|
|Theorem 1 / Corollary 3|15:3、15:12|3、12、30|相同参数界和精确目标|
|Lemma 5支持界|15:5|5–6|逐块支持；并不压缩全局约束数|
|Lemmas 6–11与分解|15:7–9|7–9、16–22|完整稿补算法与证明|
|Lemma 12 / Algorithm 1|15:9–11|10–11、22–25|精确DP、读取费用及恢复|
|负系数 / 优化|15:11–12|12|不提供未知标签的免费条件约束|
|Closest String ILP / slack块|正式转见完整稿|29–30|k条预算，上端单位矩阵slack块，局部RHS=kd|

## 5. FS21定理及模型

源输入为 p×N 矩阵，点是列；k个有序中心，逐坐标关系 Q_h⊆Σ^k；删至多o个点；非空簇；**总和编辑预算B**。正式14:3明确随后定义沿用非空簇。Definition 3/问题框为14:4，Theorem 4为14:5，完整稿p5/13。

\[
(kB)^{O(kB)}|\Sigma|^{kB}N^{O(k)}p^2.
\tag{FS}
\]

完整表示的关系读取与检查另付固定多项式；本轮将其全部计入。明确角色/tuple可以投影并保存lift表，详见 OTHER_FRAMEWORKS_AUDIT §2。没有外部 oracle。采样用于 Lemma 12 的存在性，最终算法枚举小超图及出现位置，故所读算法是确定性的。

结构工具：正式14:8 Theorem 9转述Marx的超图枚举；若小超图顶点数v、分数边覆盖数η，宿主最大边长D，费用为

\[
v^{O(v)}D^{v\eta+1}|E_G|^{\eta+1}|V_G|^2.
\]

Lemmas 10–12（正式14:9–10，完整pp9–11）得到 ≤B 个偏离位置、≤200 ln B 条边、分数覆盖≤4。Lemma 11的密度证明使用**固定聚类下总和最优中心**的单坐标交换。宿主边来自输入点的k-tuples，故 |E_G| 可达 N^k。论文没有在这一定理中给出与k无关的输入多项式次数。

公式核对：正式14:12/完整p13叙述末行出现 |Σ|^B；Theorem 4及实际编辑枚举均使用 |Σ|^{kB}。本轮采用定理的保守表达(FS)；二元时差异可被 (kB)^{O(kB)}吸收，覆盖结论保持。

## 6. KKM17/KKM20作为有利补充基线

正式54:3–4 Theorem 2：

\[
w^{O(a)}(a\Delta)^{O(a^2)}\nu^3\lambda.
\tag{KKM}
\]

同一上端D复制到各块，局部全1，非负变量及0/足够大上界，线性目标。完整v2 Definition 2/Theorem 3（p3）扩展到可分凸目标并显式列一次连续优化oracle；本轮线性可行性可用普通LP以固定多项式费用完成。完整pp11–12给初始可行解和恢复；pp20 Definition 22/Corollary 23给不同块的pre-n-fold到统一矩阵的补零归约。

完整pp13–15 Theorem 19的δ-Multi Strings允许字符可加的距离、每个给定串的上下限；时间 K^{O(k²)}log h。它的k仍为输入串数。未知的全串覆盖标签需额外处理。模型与参数代入见 NFOLD_REDUCTION_AUDIT。

ESA正式版使用线性受限合同，完整稿有更广合同与编号变化。本轮具体0目标归约同时落在已发表的正式合同内。

### 期刊最终版新增核对

取得KKM20后，以其更广正式合同作为补充基线依据。p7 Definition 1、p9 Theorem 1明确给

\[
w^{O(a)}(a\Delta)^{O(a^2)}\nu^3\lambda+\mathcal R,
\]

其中Δ=1+||D||∞，允许一般有限上下界及可分凸目标；\(\mathcal R\)为一次连续松弛优化调用。本文0目标只需普通线性规划，其编码费用为固定多项式。pp14–16给可行性、求解与辅助变量投影恢复，p16明确应用的简洁编码时间不包含原实例读入，本文已补入。

|已读旧版本|KKM20正式定位|对本轮保证的影响|
|---|---|---|
|ESA Theorem 2 / v2 Theorem 3|Theorem 1，pp4/9、证明pp14–15|相同a²型依赖；更广目标/界，0目标包络保持|
|v2 Theorems 19/20|Theorem 3 pp18–19、Corollary 1 p20、Theorem 4 p21|k仍为给定输入串数，未增加未知标签的免费选择|
|v2 Definition 22 / Corollary 23|Definition 3 p28、Corollary 2 p29|不同块补零、原变量恢复保持；p29另指出后续一般n-fold改进|
|v2 small-domain huge框架|Theorem 6 pp26–28|完整配置枚举承担域大小乘积；见NFOLD审查§5.4|

上述相关定义、参数依赖及恢复没有形成额外T3桥接。期刊p21脚注明确c-HRC中的c为固定常数；源定理参数k依旧是输入串数量。本文继续以n-fold直接表示处理一般标签域，没有借此扩张c-HRC合同。

## 7. 获取边界与读取证据

正常来源：DROPS、arXiv、DOI元数据协商。搜索连接器两次返回Transport send error；该错误没有提供查新未命中证据。期刊FS23正文403、试探性旧主页404及错误DBLP路径均按实际结果记录，未据以识别版本或作内容判断。

来源URL、获取时点/文件mtime、文件摘要、PDF哈希和实际读取范围见 sources/SOURCE_MANIFEST.json、ACQUISITION_LOG.json、READING_LOG.md。关键公式整页渲染在 sources/page_images/，含NF25正式p3/p11、完整p30、FS21正式p5/p12、KKM会议p4及期刊p9/p26/p27/p29。

本轮原文核读属于模型辅助读取，没有新增研究者人工阅读全文声明，也没有外部数学意见。哈希固定内容身份，独立性按实际过程登记。
