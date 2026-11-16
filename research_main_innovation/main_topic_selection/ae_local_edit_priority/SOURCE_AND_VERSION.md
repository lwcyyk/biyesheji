# 局部修改算法：来源与版本核验

版本 LOCAL-SOURCE-1，2026-11-06。取证方式：公开只读HTTP、既有原文复用、文本提取和PDF目视核验。本轮使用academic-research-suite与PDF读取流程，候选机制及求解器保持未实现。

**获取结论：KU同题作者全文已取得；Damaschke2013取得可绑定的两页正式预览，全文仍缺。** 资料完整度与数学映射分别裁决。

## 1. KU2012

题录：Christian Komusiewicz、Johannes Uhlmann，*Cluster editing with locally bounded modifications*，Discrete Applied Mathematics **160:2259–2270 (2012)**，DOI [10.1016/j.dam.2012.05.019](https://doi.org/10.1016/j.dam.2012.05.019)，PII S0166218X12002259。

### 实际取得版本

- [研究组公开目录](https://fpt.akt.tu-berlin.de/publications/)直接列出[ce-bounded-degree.pdf](https://fpt.akt.tu-berlin.de/publications/ce-bounded-degree.pdf)。本地保存为 [sources/KU2012_author.pdf](sources/KU2012_author.pdf)。
- 272301字节，**28页**，SHA256 `ce554912f39a778d490f9c44d2a43b3620d50734d43c496596cce666c4c8683b`。
- 首页题名、两作者、机构一致，页脚为“Preprint submitted to Discrete Applied Mathematics”，日期**May 23, 2012**。首页还注明部分结果曾以另一题名发表于SOFSEM2011，并收入首作者2011博士论文。
- DOI关联依据为已核实出版题录的同题、同作者、同刊物，以及Damaschke2013正式预览对KU2012的4dt核/O(N³)结果的明确引用。当前PDF本身没有取得期刊排版页码/DOI标识，登记为**同工作、完整公开作者稿**。它与2012期刊12页排版版逐字一致性保持未核实。
- 本文定理编号和物理页码均来自该28页版本。期刊版正文入口本轮返回403；作者全文的取得显著缩小了原缺口，但不将它改称正式offprint。

### 实读范围

完整核读定义1、§4（pp19–25）的输入框、Rules3–8、Lemma5–7、Theorem6/7及正确性/费用证明；核读§1摘要、参数关系及结果表，§2的3-SAT构造、Theorem1/2、Corollary1（pp7–12）和删除版下界入口（pp12–14）；§3只作低度数结果定位，未独立复核全部匹配算法；参考文献用于版本和引用核对。

结构预检 **PASS**，28页均计数一致，无警告，见 [KU2012_author_preflight.json](sources/KU2012_author_preflight.json)。关键页已渲染目视核验，见sources/RENDER_LOG.json、KU2012_author_pageXX.png。原PDF保持取得字节。

## 2. Damaschke2013

题录：Peter Damaschke，*Cluster Editing with Locally Bounded Modifications Revisited*，IWOCA2013，LNCS **8288:433–437**，DOI [10.1007/978-3-642-45278-9_38](https://doi.org/10.1007/978-3-642-45278-9_38)。

### 实际取得版本

- [出版方章节页](https://link.springer.com/chapter/10.1007/978-3-642-45278-9_38)为subscription preview。正常PDF链接返回相同章节HTML。
- 章节页公开给出的[Download preview PDF](https://page-one.springer.com/pdf/preview/10.1007/978-3-642-45278-9_38)成功取得，保存为 [DAM2013_preview.pdf](sources/DAM2013_preview.pdf)。
- 88740字节，**2个物理页=印刷433–434页**，SHA256 `e4ac89a7cfbeb8da7069871fdbdd700d87823c990b697896587f20406f375b12`。
- 题名、作者、出版页脚LNCS8288及433–437、出版方DOI链接共同绑定。文件是预览节选，完整章节应有5页；**印刷435–437页缺失**。
- [Chalmers机构条目187873](https://research.chalmers.se/publication/187873)核实题名、作者、年份、页码及DOI；本轮可读条目没有提供全文附件。该结论限本次所读页面。

已完整阅读预览两页。p433给原问题定义、旧核引用及新核/时间声明；p434给edit-optimal定义、Lemma1陈述及证明首段，证明在页末截断。后续核化过程、证明和随机化细节尚缺，故没有编造其定理编号、随机成功保证或参数ε依赖。

结构预检 **UNAVAILABLE**，警告为对象866在文件中但不在活动xref链中。Windows的CLI `--output`还遇到POSIX dirfd限制，随后改为保存预检stdout，原裁决保持。两页均可解析，Poppler渲染成功；渲染有Invalid Font Weight警告。两页已目视查看，足以核对可见声明。相关记录在DAM2013_preview_preflight.json、其stderr和RENDER_LOG.json。

## 3. Damaschke2016复用范围

复用作者公开的*Sufficient Conditions for Edit-Optimal Clusters*，[edopt.pdf](https://www.cse.chalmers.se/~ptr/edopt.pdf)，9页稿，作者页标Information Processing Letters116(2016):267–272。原件和原预检只读复制于sources/frozen_inputs/ae_priority_audit/sources/。

首页脚注明确只扩展IWOCA2013的一节。它支持edit-optimal crown定义、5t充分条件及相关证明的来源关系；**2013核化部分仍需2013对应正文**。本轮复读其定义与Theorem5及首页版本说明，继承旧稿完整阅读记录，没有扩大为本轮独立重证全部2016结论。

## 4. 获取行动与限制

|记录|行动及实际结论|
|---|---|
|SEARCH_CONNECTOR_RECHECK.json|本轮两查询仍为Transport send error；检索未完成，不推断无来源|
|RETRIEVAL_01–05.json|出版方、作者页、机构搜索、正常公开搜索；KU出版页403、若干旧作者地址404、若干Python TLS失败；DAM2013预览成功|
|RETRIEVAL_NATIVE_06–08.json|改用系统curl作同类正常GET，TU研究组/目录及Chalmers条目可读，KU作者PDF成功。未关闭证书校验、未登录或改认证头|
|Google/Bing/Gupea|Google返回JS跳转页；Bing RSS返回无关词典/产品结果；Gupea返回机器人验证。均未用作数学证据，未继续挑战|
|INPUT_MANIFEST.json|绑定四份指定数学/裁决输入、2016来源及历史题录，保存原字节副本|

记录中的HTTP200仅表示收到响应，是否为正文另看文件签名和内容。没有外部消息、付费购买、机构登录或访问控制绕过。COL2026本轮没有新增获取动作，继续保持全文待取得。

## 5. 最小资料请求

详见 [sources/FULL_TEXT_REQUEST.md](sources/FULL_TEXT_REQUEST.md)。最决定性缺项是**Damaschke2013印刷435–437页**；优先提供完整5页章节PDF，以便保持页序及证明上下文。KU作者稿已足以核读其所载结果；正式期刊版用于确认指定版本等同性，按独立的小缺口保留。
