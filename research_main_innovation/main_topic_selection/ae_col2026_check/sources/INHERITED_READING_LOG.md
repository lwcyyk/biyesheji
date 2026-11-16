# 来源、版本、定位及获取范围

版本AE-PRIORITY-1，2026-11-06。当前主稿五份均在ae_priority_audit；数学构造版本为AE-BRANCH-1，历史证明不改写。全部获取为公开只读请求，付费购买、认证服务、账户操作、候选机制/验证器和外部消息发送均为0。

## 1. 四份指定输入与证明来源

完整核读AE-BRANCH-1的PROOF_DECISION、GENERIC_FORM_AND_PRIOR_ART、CONFLICT_DICHOTOMY_PROOF、CORRECTNESS_AND_PARAMETER_BOUND，并辅助读构造和审查记录。原字节复制为AE_BRANCH__*.md/json，路径/哈希在REUSED_SOURCE_BINDING.json。

路线提出：研究者消息中的PROPOSED_PROOF_ROUTE。证明补全：上一会话在共享上下文内完成C1/C2、正确路径、两类计数和恢复。当前会话继续共享这些输入核对，没有输入隔离，没有外部数学读者或证明助手。研究者明确核读的只有S1/S2，未扩大到新分支证明。独立性单列于PROOF_INDEPENDENCE.json。

## 2. 直接近邻：实际阅读范围

所有PDF有结构预检sidecar并与源字节哈希绑定；PASS只支持页结构，语义依据如下。物理PDF页与论文页码不混用。

|ID|题名/作者/版本/来源|实际阅读与使用|
|---|---|---|
|COL2019|*Low-rank binary matrix approximation in column-sum norm*；Fedor V. Fomin、Petr A. Golovach、Fahad Panolan、Kirill Simonov；arXiv1904.06141v1，2019-04-12，18页。[原文](https://arxiv.org/pdf/1904.06141v1)|复用并重核摘要、§1方法、物理p4 Definition1、p5问题框/Theorem2、Lemma4相关代表/例外工具，§4共同R编码。正式tuple定义与半径、运行界逐项比较；未重新独立重证随机PTAS全证明|
|PM2018-C|*Parameterized Low-Rank Binary Matrix Approximation*；Fedor V. Fomin、Petr A. Golovach、Fahad Panolan；ICALP2018出版方16页；DOI10.4230/LIPIcs.ICALP.2018.53。[PDF](https://drops.dagstuhl.de/storage/00lipics/lipics-vol107-icalp2018/LIPIcs.ICALP.2018.53/LIPIcs.ICALP.2018.53.pdf)|读取首页、§1固定模式定义、总错误及概述，并定位其full-version声明。没有用会议版的定理编号替换42页稿编号|
|PM2018-F|同题同三作者，arXiv1803.06102v1，2018-03-16，42页。[全文](https://arxiv.org/pdf/1803.06102v1)|完整核读p4–5 P-Matrix定义，p10–12 Observation4/5、Proposition2及证明；p31–36 Lemma8/9、Theorem7、Extend-P-Solution、Claim6.1正确性和费用推导；p37结论用于后续问题发现。其他r-Means/秩部分仅概述/定向读取。p32公式已渲染目视核对（lowrank2018_theorem7_page32.png）|
|BCC2018|*Approximation Schemes for Low-Rank Binary Matrix Approximation Problems*；Fomin、Golovach、Lokshtanov、Panolan、Saurabh；2018；本轮API记录最新为arXiv1807.07156v1；复用38页PDF哈希。[原文](https://arxiv.org/pdf/1807.07156v1)|物理p2 Definition1、问题框/Theorem1–2，p5共同关系例、摘要/方法概述。p2两项时间公式已渲染目视核对（bcc2018_page2.png）。没有完整复核两项近似构造。中心set记号的所有边界解释保留本轮范围限制|
|CAT2021|*Parameterized Complexity of Categorical Clustering with Size Constraints*；Fomin、Golovach、Nidhi Purohit；arXiv2104.07974v1，2021，32页；首页说明初版WADS2021接收。[原文](https://arxiv.org/pdf/2104.07974v1)|摘要/§1、Theorem1、Observation2–3、Lemma3/4及相关重复类/候选中心段；全DP未重新逐行重证。仅按总预算与大小约束原模型使用|
|MISS2025|*Binary k-Center with Missing Entries: Structure Leads to Tractability*；Farehe Soheil、Kirill Simonov、Tobias Friedrich；arXiv2503.01445v1，2025，28页，当前作者链元数据确认v1。[原文](https://arxiv.org/pdf/2503.01445v1)|复用Theorems1.1–1.3、Definition2.1、known-entry mask/图、相关工作与引文。没有重证全部图参数算法；只用于准确参数代入和R缺失比较|
|HAM2019|*On Computing Centroids According to the p-Norms of Hamming Distance Vectors*；Jiehua Chen、Danny Hermelin、Manuel Sorge；arXiv1807.06469v3，2019，21页。[原文](https://arxiv.org/pdf/1807.06469v3)|摘要/pp1–4，特别p4对Closest String小字母表算法的明确转述和参考文献。GNR2003、Ma–Sun2009、Chen–Ma–Wang2012原证明本轮未取得；对其类型和最佳常数不扩张主张|

## 3. 局部编辑、共聚类与后续来源

|ID|准确版本/来源|实读及证据等级|
|---|---|---|
|PM2016|Gregory J. Puleo、Olgica Milenkovic，*Correlation Clustering and Biclustering with Locally Bounded Errors*，arXiv1506.08189v3；元数据更新2016-05-24，PDF版面2016-05-25，20页。[全文](https://arxiv.org/pdf/1506.08189v3)|摘要/§1–2误差向量、§4 Algorithm2/Theorem6及pp8–10局部收费证明；AppendixD的一侧t-perfect定义/NP-hard入口。其2012局部修改引用是二手引述，单列未取得原文。全文取得不等于全部附录证明重证|
|MAX2019|Laurent Bulteau、Vincent Froese、Sepp Hartung、Rolf Niedermeier，*Co-Clustering Under the Maximum Norm*，arXiv1512.05693v3，2019-06-14，22页；首页说明初版ISAAC2014。[全文](https://arxiv.org/pdf/1512.05693v3)|摘要、§1、§2物理p4–5非空分区、块极差定义和Observation1；Table1/后续定理只用于筛查，未调用未读算法证明|
|BE2024|Manuel Lafond，*Improved Kernelization and Fixed-parameter Algorithms for Bicluster Editing*，arXiv2410.13123v2，2024-10-22，20页。[全文](https://arxiv.org/pdf/2410.13123v2)|摘要/§1–2、§4 Definition1冲突、Lemma4及Theorem4/相关分支说明；核化证明只定向读取。本轮未重证全部Lemma6–11。原文自己记录更快2.22^K后续，故没有将2.581^K称为最快|
|DAM2016|Peter Damaschke，*Sufficient Conditions for Edit-Optimal Clusters*；[作者PDF](https://www.cse.chalmers.se/~ptr/edopt.pdf)，9页；[作者页](https://www.cse.chalmers.se/~ptr/)标IPL116(2016):267–272|本轮完整读取9页：Definition1–3、Proposition4、Theorem5及后续充分条件证明。首页脚注明确它只扩展IWOCA2013一节，不能当成2013核化部分的全文|

## 4. 版本及全文缺口

|ID|已取得的版本信息|正文状态及限制|
|---|---|---|
|COL2026|Crossref公开搜索结果给同题同四作者、TCS、2026年10月及DOI10.1016/j.tcs.2026.116240；DOI重定向的PII S030439752600469X/题名匹配|ScienceDirect正文403；只有元数据/出版方locator，未读2026数学正文，不能以2019v1替代|
|PM2020|出版方页给2020-01-02、DMKD34:478–532、DOI10.1007/s10618-019-00669-5|lowrank2020_doi.html/preview.txt是摘要/参考文献及subscription preview，不是全文；2018v1与此正式版的全部差异未核实|
|KU2012|Christian Komusiewicz、Johannes Uhlmann，*Cluster editing with locally bounded modifications*，DAM160(2012):2259–2270；Crossref/DOI10.1016/j.dam.2012.05.019匹配|出版正文403；PM2016 p2的(d,t)-FPT转述不充当原定理/证明全文|
|DAM2013|Peter Damaschke，*Cluster Editing with Locally Bounded Modifications Revisited*，IWOCA2013，LNCS8288:433–437；DOI10.1007/978-3-642-45278-9_38|出版方摘要可读，明确核化加速目标；全文subscription preview。2016公开9页稿仅有其中一节的扩展|

期刊年份、页码、DOI来自列明公开元数据/出版方页面；数学保证仅引用实际读到的版本。没有因取得redirect HTML或摘要就登记为已读论文全文。

## 5. 当前检索可用性和边界

检索日期为2026-11-06。SEARCH_CONNECTOR_RECHECK.json记录本轮连接器四查询的Transport send error。与历史状态不同，arXiv官方页面及API本轮可用，成功记录见RETRIEVAL_DISCOVERY01–03、FOLLOWUP04/06等JSON。

查询涵盖共同/小关系、binary constrained、固定模式P-matrix、matrix/template/Hamming、binary/parameterized clustering、局部biclustering及Fomin/Golovach/Panolan/Simonov作者链。hamming查询共120条分两页取得；其他查询的total/returned和窗口保留在DISCOVERY_SCOPE.json。宽泛检索有天文、量子、统计等假阳性；只做发现。已读模型覆盖回到原文，不用“关键词未命中”推定新颖性。

新来源通过引用链获得：COL2019→PM2018完整稿；PM2016→KU2012；KU2012的出版元数据→DAM2013；作者页→DAM2016。官方标题/作者链检索补充MISS2025及其他后续记录。元数据覆盖截至抓取时实际可取的版本，未宣称穷尽整个领域、所有语言或所有期刊全文。

## 6. 获取限制的具体分类

- ScienceDirect文章正文为403；Springer两篇正式版是subscription preview。没有尝试登录、购买、代理绕过或改认证头。
- DBLP为HTTP202 HTML机器人验证，已按HTML扩展保存，保留原raw命名映射；未当作JSON元数据。
- DuckDuckGo为202 bot challenge，Google为JS验证/跳转页；没有继续验证码或挑战。
- Bing RSS返回词典/无关Cluster页面，排除于论文事实。
- 若干作者旧地址404或TLS超时；Fomin旧主页重定向系首页，BORA检索重定向NVA通用首页，均未作为匹配论文版本。
- 初次解析缺少bs4，随后使用标准库HTMLParser/re；没有安装新依赖。该文档工具缺失不阻断已完成原文读取。

RETRIEVAL_*.json保存每次URL、时间、HTTP/异常、字节hash和文件名。FETCH_ASSESSMENT.json进一步区分“收到字节”与“取得可引用正文”。没有沿用历史失败来宣称本轮不可检索。

## 7. 本轮推导及独立性

本轮新增的是精确名称映射、r/mr总预算反例、P₄模板反例、概率精确阈值代入、零误差短算法及按保证取包络。它们是手工推导/标准推论，未运行求解或数学穷尽。

四份证明稿的当前核读仍共享同一模型和上下文。独立数学复核、证明助手验证、作者原文覆盖三个状态均单列；一个状态不会自动升级另一个。当前核心数学未发现新缺口，优先权为PRIORITY_UNRESOLVED，机制门仍关闭。

## 8. 文件完整性

REUSED_SOURCE_BINDING.json绑定25项历史来源；新来源字节在SOURCE_MANIFEST.json。PRIORITY_STATUS.json登记贡献状态，PROOF_INDEPENDENCE.json登记实际独立性；DELIVERY_VALIDATION.json仅检查来源hash、JSON、链接和文档范围。它不认证数学正确性或首次性。

全部执行脚本限获取、文本提取、版本/目录登记、格式和哈希处理。新的候选机制、求解器、验证器、认证调用、真实账户操作、性能实验、付费购买及外部发布/消息发送均为0。
