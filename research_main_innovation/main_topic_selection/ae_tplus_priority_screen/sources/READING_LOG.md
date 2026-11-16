# TP-1来源阅读及定位记录

记录日期2026-11-07，获取/初读跨2026-11-06/07。实际阅读由同一当前对话的模型辅助完成，接续后复用保存的正文和上下文摘要，并定点重读相关段落。未新增独立读者、研究者人工核读或形式化验证声明。

## 1. 冻结项目依据

INPUT_MANIFEST.json的六份输入及snapshot均由接续前阶段完整读取；当前阶段又读取规范合同、TT-1裁决/成本组合和两个既有来源总表。数学证明来源保持PROJECT_T3_DEPENDENT。INPUT_MANIFEST承担版本固定，当前末次哈希复验另见DELIVERY_VALIDATION.json。

## 2. 新增实质深读：两项工作

|来源|实际范围|本轮使用的定义/结果及PDF页|版本限制|
|---|---|---|---|
|FHS2013.pdf，与FHS2013v2.pdf同字节|12页全文|p2矩阵划分、空部和列表；p6 Theorem 2.5旧界O(n^{kℓ})；pp9–10 Theorem 4.1/Proposition 4.2及二部障碍证明|arXiv1306.1967v2，2013-06-20；以arXiv版本号和正文为准，PDF转换元数据日期不充当投稿日期|
|FHS2014_author_journal.pdf|13页全文；接续后重读pp1–7及相关定位|p1自称2013-10-02 submitted preprint；p2列表/非列表；pp6–7 Theorem 2.5更有利n^{O(k+ℓ)}；pp10–12 Theorem 4.1/Proposition 4.2和2^{2ℓ}(k+ℓ)(2ℓ+3)界|作者目录把同一split.pdf关联CoRR2013和DAM166:91–96 (2014)，DOI元数据佐证题录；未声明这是VOR/接受稿|
|BK2024.pdf，与BK2024v2.pdf同字节|21页全文含附录；接续后定点重读pp3–8|pp3–4 Definitions 2.1/2.2/2.4及各poset；p6 Theorem 3.2/Corollary 3.3；pp7–8 Theorem 4.1/Lemma 4.5；pp9–12 Lemmas 5.3/5.4、Theorem 5.5/Proposition 5.6；pp15–18 Theorem 7.2/Lemma 7.3；p19附录证明|arXiv2107.13809v2，2024-06-04，元数据关联TCS1007:114652 (2024)及DOI；VOR未读，未推定逐字一致|

六张整页图的生成记录在RENDER_LOG.json；接续前已目视核对。对应BK pp4/7/15、FHS v2 p6、FHS修订pp6/11。结构预检sidecar均PASS，范围仅STRUCTURE_ONLY。

FHS Theorem 2.5使用List Partitions (2003)的稀疏—稠密步骤。本轮接受其源论文声称的有利识别界，不把未读依赖伪记为已审。该定理没有未知单侧编辑，完整T+覆盖仍需新的桥接。

## 3. 复用来源及本轮定点新增阅读

- COL2020：ae_t3_p26_coverage/sources/COL2020_official_pdf.pdf，18页完整正式版；此前全文/相关证明范围沿用原READING_REGISTER。TP-1重读PDF pp5、10–14，重点Definition 2/Theorem 3、Partition Center⋆输入、IP(6)和d_x的量词。2019v1遗漏证明依赖沿用原记录。
- FS21正式版/完整v2：沿用ae_t3_alternative_frameworks/SOURCE_AND_THEOREM_MAP及sources/SOURCE_MANIFEST的实际范围；本轮核查域/成本在原/对偶方向的接口，未给FS23期刊版本新增正文声明。
- NF25正式/完整v4、KKM17/KKM20：模型、源定理、slack块、宽度规范化和恢复沿用AF-1实质读取；本轮推导混合0/1预算和域感知列型。没有新读一份NF25版本。

SOURCE_MANIFEST.json指向这些既有原文并复核文件哈希。旧版本的阅读范围为复用，接续摘要和同模型重读不计为独立复核。

## 4. 发现/筛选层，正文未深读

|项目|实际取得与读取|允许承担的证据|
|---|---|---|
|List Partitions (2003)|作者目录题录及原始partitions.ps已取得；PS正文未读|FHS依赖线索和版本获取状态|
|Full Constraint Satisfaction Problems (2006)|作者目录题录及cspthree.ps已取得；正文未读|检索字典线索|
|Two Algorithms for General List Matrix Partitions (2005)|作者目录题录及partsize.ps已取得；正文未读|算法线索|
|Extension Problems with Degree Bounds (2009)|16页作者PDF取得并结构预检；只读第一页题名、摘要和开头定义|其degree bounds是输入图度约束；未作该文所有定理的覆盖裁决|
|Clustering with Locally Bounded Ignorance，arXiv2605.13917|仅arXiv标题检索结果中的摘要|总加权相关聚类/局部模糊性线索；正文和定理未审|
|FHS/BK出版方XML、DOI元数据|题录信息；标准XML无正文，FULL请求认证失败|身份/卷页/日期；不承担正文定理覆盖|

原本三份以.pdf后缀保存的404 HTML已改名.http404.html，内容字节保留。没有把这些文件算入PDF页数或阅读全文。

## 5. 过程归属及边界

T3原路线、证明补全及后续复核的AI参与沿用既有过程记录；本轮没有新增人工或外部作者结论。TP-1的成本/list gadget与图字典为当前模型辅助纸面推导，按标准有限归约登记；先例归属和完整参数算法来源分别审查。

检索范围以实际查询、可读原文和完成的蕴含链为限；没有全库穷尽声明。搜索传输错误、无关页面和未读来源均不支持“全球无先例”。COL2026请求数0，暂停状态保持。
