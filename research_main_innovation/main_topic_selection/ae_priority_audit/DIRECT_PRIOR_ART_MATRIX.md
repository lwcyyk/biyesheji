# 逐定理先例矩阵与强基线包络

版本AE-PRIORITY-1，2026-11-06。覆盖等级严格分为DIRECT_THEOREM_COVERAGE、STANDARD_COROLLARY_COVERAGE、PARTIAL_OVERLAP及UNRESOLVED_SOURCE。下列结论限于列明版本和命题；完整读页、哈希及获取日志在sources。候选为AE-BRANCH-1通用共同关系算法，未当作此前公开算法加入优先权证据。

## 1. COL2019：共同关系最大半径的直接模型先例

**题名/作者/版本。** *Low-rank binary matrix approximation in column-sum norm*，Fedor V. Fomin、Petr A. Golovach、Fahad Panolan、Kirill Simonov；arXiv1904.06141v1，2019-04-12，18页。[作者稿](https://arxiv.org/pdf/1904.06141v1)

|字段|原文及代入|
|---|---|
|原问题|Binary Constrained k-Center；PDF p4 Definition1、p5问题框/Theorem2|
|原参数|k中心、ε近似精度；原m为长度、n为点数|
|原预算|最大点到最近中心的Hamming距离；不是总误差|
|共同关系|允许任意R_t；取全部R_t=R即当前子域|
|重复/未使用中心|正式问题使用有序tuple；未要求中心互异或每中心非空|
|表示大小|输入串与每坐标显式关系；当前共享关系可重复展开，规模增加最多多项式因子|
|确定性/随机性|Theorem2为随机PTAS，成功概率至少1−2n_src^{-2}|
|准确原界|`m_src^{O(1)} n_src^{O((k/ε)^4)}`|
|本模型代入|k=q，长度n、点数m；`n^{O(1)}m^{O((q/ε)^4)}`，关系读取/输出另纳入输入因子|
|新增步骤|共同模式数L、准确半径r的固定输入指数及确定性尚需论证；本轮C2并未由该定理陈述自动给出|
|覆盖等级|共同关系模型为DIRECT_THEOREM_COVERAGE；T1/T2算法为PARTIAL_OVERLAP|

**精确阈值的可复核代入。** r≥1时取ε=1/[2(r+1)]。若OPT≤r，成功事件下输出整数半径≤(1+ε)r<r+1，所以≤r；若OPT≥r+1，任何合法输出都不会在精确验收时通过。独立重复可放大概率，但仍可能误判NO，不能称确定性。先做相同L位处置的安全去重，k可置q₀≤min(q,2^L)，得到

\[
\operatorname{poly}(mn+qL)+n^{O(1)}m^{O((q_0(r+1))^4)}.
\]

概率放大按m≥2使用原成功界；单输入行先用表中直接算法处理，避免把1−2m^{-2}在m=1时的无效数值当成正成功概率。

这仍是输入点数指数依参数的保证，无法直接给T2的固定输入多项式指数。把这一上界称为慢方法的必要代价同样没有依据。

## 2. PM2018：固定模板与精确编辑分支

**来源。** Fedor V. Fomin、Petr A. Golovach、Fahad Panolan，*Parameterized Low-Rank Binary Matrix Approximation*。取得ICALP2018出版方16页版，DOI [10.4230/LIPIcs.ICALP.2018.53](https://doi.org/10.4230/LIPIcs.ICALP.2018.53)，以及公开完整作者稿[arXiv1803.06102v1](https://arxiv.org/pdf/1803.06102v1)，42页。下面编号/运行界取完整作者稿，不混用会议版编号。

设原模板尺寸为p×ℓ，总错误参数为K；对应当前模板B时p=q、ℓ=L。

|字段|原文及代入|
|---|---|
|原问题|P-Matrix Approximation，PDF pp4–5固定模板及块分组|
|原参数|p、ℓ、全矩阵总编辑K；不是最大行误差r|
|原预算|\(\sum_{i,t}[A_{it}\ne\widehat A_{it}]\le K\)|
|共同关系|固定模式矩阵，结构上对应共同R；同一模板用于全矩阵|
|重复/未使用|模板本身可有重复行/列，但分区各块非空；m<p/n<ℓ被拒绝。当前允许未使用角色，需另外包装|
|表示大小|mn+pℓ及K的编码|
|确定性/随机性|下面精确算法为确定性|
|Proposition2，p11–12|`2^{O(K(log p+log ℓ)+p log p+ℓ log ℓ)}(mn)^{O(1)}`|
|Theorem7，p32|`2^{O((p+ℓ) sqrt(K log(p+K))+p log p+ℓ log ℓ+ℓ log(ℓ+K))}(mn)^{O(1)}`；公式已渲染目视核对|
|代入K=r|不是等价实例；EQUIVALENT_FORMULATIONS §6的I_N例会误拒YES|
|代入K=mr|最多是必要条件/总费用问题；同节00/11例会接受局部NO，原算法输出不满足当前合同|
|新增引理|必须保持每行预算、允许空角色，并消除输入规模对选例外的参数指数；原文没有在已读陈述中提供这一转换|
|覆盖等级|PARTIAL_OVERLAP；固定模板及精确分支是明确先例，尚无T1/T2的直接/短推论覆盖|

**实际证明比较。** Proposition2取输入的相同行/列块，选至多(p+1)(ℓ+1)个块对，翻某一项并消耗总K；对称性保证块内可取任意代表。Theorem7使用代表列X/Y/Z、总预算驱动的平均费用阈值与extendable子问题。已核读p11–12及pp31–36相关过程/证明；本文的“失败行细分模式或找到W真实例外”以及|E|≤r|W|不能由这些总预算量直接代入。

更具体地，p35 Claim6.1从剩余全局误差总量推出代表的平均距离阈值；局部合同只能给总量≤mr，不能由此改为Lr。把Proposition2改成逐行扣预算，也仅直接得到至多mr次翻位的深度，没有给出Lr深度。本轮的二择一与码类进展正是仍需论证的步骤。原文p36还允许同时转置A/P；对其总预算算法应取两个方向的最好保证，不能删掉这项优化。

这确认局部障碍分支、少数代表和预算递减已有工具来源。若要以此覆盖整项定理，仍需写出局部预算的保持步骤；重新证明完整C2后才得到的算法应登记为新推导，不算原文的直接覆盖。

## 3. BCC2018：关系模型与总和近似

**来源。** Fedor V. Fomin、Petr A. Golovach、Daniel Lokshtanov、Fahad Panolan、Saket Saurabh，*Approximation Schemes for Low-Rank Binary Matrix Approximation Problems*，[arXiv1807.07156v1](https://arxiv.org/pdf/1807.07156v1)，2018，38页；本轮元数据重新确认v1。PDF p2定义/Theorem1–2，p5明确全部R_t相同的例子。

原问题为总和\(\sum_i d_H(A_i,C)\)，k中心、ε精度；共同关系作为子例已有。原文以set记中心，重复/未用中心的全部解释未在本轮独立封口；本文不以这一处为覆盖依据。显式关系表示与COL2019相似。

Theorem1是确定性PTAS：原符号`m_src n_src^{O((k²/ε²) log(1/ε))}`。Theorem2随机线性输入因子，参数函数为

\[
2^{O((k^4/\epsilon^2)\log(1/\epsilon))}
(1/\epsilon)^{O((k/\epsilon^2)\log(1/\epsilon))}\,n_{src}m_{src},
\]

成功概率至少1−1/e；p2公式已渲染核对。即使将其变为总和精确阈值算法，K=mr也不能保证每行≤r。缺少局部预算转换及相应精确构造。

**等级：PARTIAL_OVERLAP。** 共同坐标关系/预处理复用的认识已有；总和近似或其参数函数不覆盖当前最大行精确合同。

## 4. CAT2021：总预算与重复类型结构

**来源。** Fomin、Golovach、Purohit，*Parameterized Complexity of Categorical Clustering with Size Constraints*，[arXiv2104.07974v1](https://arxiv.org/pdf/2104.07974v1)，2021，32页，首页注明初版获WADS2021接收。实读§1、Theorem1、Observation2–3、Lemma3/4及相应证明范围。

原问题为有限字母表Σ的median总预算K，并控制k个簇大小。重复median没有互异限制；非空/空簇及大小p/q条件须按其实际profile使用，不当作当前默认合同。它没有给定同一中心tuple关系R。表示为mn个字母加k/K及大小约束。

Theorem1确定性时间`2^{O(K log K)}|Σ|^K(mn)^{O(1)}`。代Σ={0,1}、K=mr仍含m进入参数；还缺给定模板关系及max预算的保证。Observation2的大重数和Lemma3的拆分结构是直接工具近邻，没有自动包含C2。

**等级：PARTIAL_OVERLAP。** 不用它把FPT(K)误记为FPT(L+r)。

## 5. 局部误差和图编辑的近邻

|来源/实际命题|原模型、预算、关系/空类及表示|原保证和运行界|代入情况与覆盖等级|
|---|---|---|---|
|Gregory J. Puleo、Olgica Milenkovic，*Correlation Clustering and Biclustering with Locally Bounded Errors*，[1506.08189v3](https://arxiv.org/pdf/1506.08189v3)，2016修订；PDF §4 Algorithm2/Theorem6，pp8–10|完全二部符号图；只控制一侧每顶点错误，另一侧无界；目标为未知数量的bicluster，不是任意给定B；允许singleton。输入为跨部边和提供的fractional clustering|确定性舍入；局部误差≤c倍fractional误差，原文给c≤10的参数；给定分数解的过程多项式，定理未单列细化比特时间|局部预算一侧性直接相关；常数放宽不能决定精确r，任意模板也不匹配。PARTIAL_OVERLAP|
|Laurent Bulteau、Vincent Froese、Sepp Hartung、Rolf Niedermeier，*Co-Clustering Under the Maximum Norm*，[1512.05693v3](https://arxiv.org/pdf/1512.05693v3)，2019修订，22页；初版ISAAC2014，PDF §2/Observation1|给定行块数k、列块数ℓ，非空分区；目标为每块max−min的最大值；模板未知，无编辑预算r；数值矩阵显式mn|Observation1在二元输入/零极差时确定性O(mn)|entry极差与最大行编辑和不同，没有同预算代入。PARTIAL_OVERLAP，仅模型术语近邻|
|Manuel Lafond，*Improved Kernelization and Fixed-parameter Algorithms for Bicluster Editing*，[2410.13123v2](https://arxiv.org/pdf/2410.13123v2)，2024，20页；§2、Theorem4及冲突引理|二部图编辑为不交biclique，孤立顶点可有；总编辑K；非给定任意模板。输入可为稀疏图，与本轮显式矩阵大小另计|确定性O*(2.581^K)，4.5K顶点kernel；论文明确提到已有更快2.22^K方法，本文不称其全局最快|任意B的P₄零误差例否定直接映射；总K不可换r。邻域冲突分支不是C2整体出处。PARTIAL_OVERLAP|
|Peter Damaschke，*Sufficient Conditions for Edit-Optimal Clusters*，[作者全文](https://www.cse.chalmers.se/~ptr/edopt.pdf)，作者页标IPL116(2016),267–272；9页稿|不交团目标；判断给定局部crown是否出现在某个总编辑最优解中；无给定R；图输入|Theorem5：c≥5t时可安全隔离；只需检查该局部条件，未给本模型精确参数算法|已完整读此9页稿。它仅扩展2013章节的一节，不能当成2013核化部分全文。PARTIAL_OVERLAP|
|Farehe Soheil、Kirill Simonov、Tobias Friedrich，*Binary k-Center with Missing Entries: Structure Leads to Tractability*，[2503.01445v1](https://arxiv.org/pdf/2503.01445v1)，2025，28页；Theorems1.1–1.3/Definition2.1|未缺失位置上的最大Hamming半径d，至多k种中心；无给定共同tuple关系；known-entry图M刻画稀疏结构；输入矩阵/mask显式|确定性：`2^{O(k vc+vc² log vc)}poly(mn)`及fr版本；`d^{O(tw)}2^{O(k tw)}poly(mn)`|全已知I_N的图为K_N,N；q=1、L=2、r=1已可行而vc/tw随N增长。图参数不能直接换成L+r，亦缺R保持。PARTIAL_OVERLAP|

## 6. 指定版本/原文缺口

|来源|已核实信息|缺失及可能影响|等级|
|---|---|---|---|
|COL2026：同题同四作者期刊版|Crossref公开网页给TCS、2026年10月、DOI [10.1016/j.tcs.2026.116240](https://doi.org/10.1016/j.tcs.2026.116240)；DOI出版方重定向题名匹配|正文403；无法确认是否保留2019全部定理或新增精确参数结果。它是与候选模型最直接的版本缺口|UNRESOLVED_SOURCE|
|PM2020：*Parameterized low-rank binary matrix approximation*期刊版|出版方页给2020-01-02、DMKD34:478–532、DOI [10.1007/s10618-019-00669-5](https://doi.org/10.1007/s10618-019-00669-5)|只有摘要/参考文献，全文为subscription preview；不能把公开2018稿自动认证为全部2020结果|UNRESOLVED_SOURCE|
|Christian Komusiewicz、Johannes Uhlmann，*Cluster editing with locally bounded modifications*|2012 DAM160:2259–2270；Crossref及DOI [10.1016/j.dam.2012.05.019](https://doi.org/10.1016/j.dam.2012.05.019)核实；2016源p2转述(d,t)-FPT|原正文403；其模型为团目标、所有顶点局部τ≤t，并有总预算K。准确运行界/证明及推广能力未读，不能用二手FPT宣告T1/T2覆盖|UNRESOLVED_SOURCE|
|Peter Damaschke，*Cluster Editing with Locally Bounded Modifications Revisited*|IWOCA2013，LNCS8288:433–437；DOI [10.1007/978-3-642-45278-9_38](https://doi.org/10.1007/978-3-642-45278-9_38)；出版方摘要说改进核化约一个n因子|仅subscription preview；2016公开扩展稿不含完整核化部分。原参数界与证明尚缺|UNRESOLVED_SOURCE|

上述缺口中的原问题和性质若来自后续源转述，已明确标注；没有冒充对该原文的定理核读。

## 7. 先前公开方法的保证包络

定义不适用分支的时间为∞。下表保留相同输入、共同R表示、中心去重及全部输出，不使用本轮C2给基线赋予“此前已发表”的地位。

|适用区间|可核对的已有/标准保证|
|---|---|
|任意输入|精确枚举L^n个坐标模式，每个按原共同R检查全部行；确定性`O(L^n mnq+qL+nq)`，标准精确参考|
|r=0|模板识别的标准列类型枚举，`L^{O(L)}poly(mn+qL)`；第E7节给短证明，属于STANDARD_COROLLARY_COVERAGE的特例|
|L=1或单输入行|直接按可用bit/模式检查，读取、验证与输出均多项式；不给候选记指数收益|
|r≥n且R非空|任取一个模式用于全部坐标即满足半径；仍输出完整中心|
|q=1、R={0,1}|正是二元Closest String。HAM2019 p4转述小字母表已有`O(mn+n·2^{O(r)})`，强于本轮该特例的r^{O(r)}；Ma–Sun2009/Chen–Ma–Wang2012原证明本轮未取得，该界按明确二手出处登记，不称本轮首次|
|任意输入，允许单侧失败概率|COL2019精确阈值调用，使用同样q₀去重；时间为本文件§1式，重复/验收费用保留|
|额外合同为总K及相应固定模板/图目标|PM2018等精确总预算算法适用，取公开可验证最快分支；它们不能直接放进当前一般局部合同的完成算法包络|

确定性公开参考包络取适用的标准枚举、零误差、直接特例和已知Closest String方法的最小值；随机精确阈值包络另可取与COL2019的最小值。T1与T2属于候选算法的两种保证，单独列出并可与公开包络再取最小值，但这不增加公开先例数量。

Closest String方法按原文已确认的确定性/随机性分档；上表由HAM2019转述的小字母表强界本轮没有直接核读其原证明，故不自动将它的算法类型填成确定性，也不在该特例声称本轮新增优势。

PM2018在K=mr的总费用NO可以作为局部NO的必要条件检验（先正确处理角色可空）；它给出的YES仍需局部验收，未通过时要回退。不能把这一部分判定器的时间当作整个问题的精确完成界。

该包络限于本轮核实的来源。正文未取得的新版/更强算法存在明确缺口，所以没有宣称已经找到截至本日的全球最快通用方法，也不由两个上界的差异推出必要运行代价差距。

## 8. 覆盖总结

共同关系、固定模板和局部误差需求均已有先例。已读全文没有直接给出当前一般合同的T1/T2，也没有一条已完成的标准短归约得到它们；直接总预算/范数/身份模板转换已有明确反例。

另一方面，COL2026、PM2020和局部修改精确算法的指定正文尚缺，不能将“已读结果没有覆盖”提升为完整优先权结论。本轮总体裁决因此为PRIORITY_UNRESOLVED。
