# 来源、版本、定位与读取台账

日期2026-11-06。此台账记录本轮真实读取范围，原获取与预检记录保持原字节。文档提取、渲染、哈希和链接检查仅为证据整理；候选算法、求解器和数学穷尽程序均未实现。

## 1. PM2020

- 题名：Parameterized low-rank binary matrix approximation。
- 作者：Fedor V. Fomin、Petr A. Golovach、Fahad Panolan。
- 发表状态：Data Mining and Knowledge Discovery 34(2):478–532 (2020)期刊offprint，页眉Author's personal copy。
- DOI：https://doi.org/10.1007/s10618-019-00669-5 。公开作者稿入口：https://fedorvf.github.io/articles/2020/2020f.pdf 。
- 本地原件：[PM2020_author_public_offprint.pdf](PM2020_author_public_offprint.pdf)，886729字节；SHA256：0139e81f066a11fc4c17870cfa1f8596612b42334025efacfa0be36377d56c91。
- 57物理页。p1封面，p2使用说明，p3开始期刊478页。正文到印刷532页。映射见 [PM2020_PAGE_MAP.json](PM2020_PAGE_MAP.json)。
- 版本绑定：物理p3有完整题名、作者、DOI、卷页、收录/接受/online日期和ICALP2018初版说明；封面与所有正文页眉一致。没有以2018稿替代本文件。
- 原获取日志：[PM2020_ACQUISITION_2026_11_06.json](PM2020_ACQUISITION_2026_11_06.json)，HTTP200，获取动作当时只读封面/摘要。该旧read_scope保持。

## 2. 解析、警告与视觉核验

|步骤|实际结果|证据文件|
|---|---|---|
|pypdf读取与结构预检|57页；预检**UNAVAILABLE**，警告object114、132 wrong pointing offset0|PM2020_preflight.json、PM2020_pypdf.txt|
|pdfplumber/pdfminer第二解析|57页，各页有文本；warning捕获文件为空|PM2020_SECOND_READER.json、PM2020_pdfplumber.txt、PM2020_pdfplumber_warnings.txt|
|Poppler pdfinfo|识别57页、元数据、无加密；file size字段为0，与文件系统886729字节矛盾|PM2020_PDFINFO.txt；实际字节/哈希采用原件|
|Poppler渲染|关键14页全部return0|PM2020_RENDER_RECORD.json及各PNG|
|目视核查|下表逐页内容已查看；公式回到PNG|PM2020_page_XX.png|

没有修复、覆盖或重写PDF。预检UNAVAILABLE保持，其含义不能提升为PASS。补充读取用于相关定位可靠性核查，外部读者仍可用同一SHA256复核警告。

|物理页|印刷页|目视核查内容|
|---|---|---|
|3|478|题录、日期、摘要、期刊及ICALP2018声明|
|8|483|固定P定义、非空块、总Hamming预算|
|33|508|Th5根号内aK log(K+a)、根号外log a；定义及辅助引理|
|38|513|Th6：a√(K log(aK))；秩公式与参数|
|43|518|Obs4/5、块角色识别、非空角色基数|
|44|519|Lemma10核维数、Rule1/2、Claim7首段|
|45|520|Claim7恢复、Rule3、Prop2准确对数式|
|46|521|Extendable定义、Lemma11及代表列枚举完整证明|
|47|522|Lemma12前提、枚举量、距离总和判据|
|48|523|Lemma12结束、Th7显示公式和核后初始化|
|49|524|算法5全部行；i∈Y∪Z及i∈Z时j代表替换|
|50|525|可靠性与归纳开始；最小h*定义|
|51|526|总K平均误差不等式、正确分支、复杂度开始|
|52|527|完整复杂度、转置、低秩模板应用|

文本实质核读范围：题录与摘要；§1相关定义/结果概述；§7印刷pp518–528中P模板定义援引、Obs4/5、Lemma10–12、Prop2、Th7及算法5相关证明；§§5–6的Th5/Th6陈述和有关预处理/代表说明；§8印刷p529的预算与公开问题。相邻章节的所有技术证明没有重新独立验证。关键词用于定位，数学判断使用原定义和上述实质证明。

## 3. PM2018 v1与历史输入

- 题名和三作者同上，arXiv1803.06102v1，2018-03-16，42页：https://arxiv.org/pdf/1803.06102v1 。
- 原件、旧文本和PASS预检复用于 ae_priority_audit/sources/；本轮只读副本及SHA256见 [INPUT_MANIFEST.json](INPUT_MANIFEST.json)。
- 文本核读：p1版本/摘要；pp4–5模板定义；pp10–12 Obs4/5及Prop2；p24 Th5及相关结构；p27 Th6；pp31–36 Lemma8/9、Th7、代表集合(d)、分支、证明与时间。
- 公式与流程对照回到原PDF渲染，物理pp11、24、27、32、33、34均目视核对；图像及返回码见PM2018_RENDER_RECORD.json。p32的Th7公式与期刊p523比较，p33–34的代表条件/分支与期刊pp521、524比较。
- 16页ICALP2018会稿为不同版本，本轮没有以其编号替代42页v1。

历史数学输入：ae_math_review/REVIEW_DECISION.md、PROOF_REVIEW.md及ae_branching_proof目录五份md，均读到/继承完整证明范围；THEOREM_IDENTITY用于合同核对。读取清单和快照包含于INPUT_MANIFEST.json。原第一阶段封存副本与底层PHASE1/PHASE2回执没有改写。

## 4. 引用与结论等级

- **原文事实**：版本、定义、原定理及公式；以印刷/物理双页码定位。
- **本文推导**：模板映射、预算反例、完整成本代入、角色包装及桥接责任。
- **数学正确性证据**：本轮知情整合与既有模型辅助复核；外部人工及证明助手状态分开。
- **优先权状态**：PM2020指定缺口关闭、PARTIAL_OVERLAP；COL2026全文及其他指定源按原状态保留；整体PRIORITY_UNRESOLVED。

便于回查的原文文本片段按原物理页标记保存在PM2020_LOCATED_EXCERPTS.txt和PM2018_LOCATED_EXCERPTS.txt。文本仅承担定位，公式以原PDF及已核PNG为准。

本轮没有重试COL2026获取、联系作者、外部上传或发消息。公开题录、全文取得、公式已读和整项优先权封口分别登记。
