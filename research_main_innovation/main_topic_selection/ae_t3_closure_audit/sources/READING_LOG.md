# AC-1来源与核读记录

日期2026-11-06。所有数学工作在当前对话内进行，口径为知情模型辅助复核。没有新代理、外部发送、作者联系、求解器、穷尽测试或候选实现。

## 1. 冻结对象

完整读取PR-1的EXPONENT_SOURCE、REFINEMENT_LEMMA、PROOF_OR_COUNTEREXAMPLE、COMPLETE_COMPLEXITY和DECISION五稿。另绑定既有T1/T2、局部图映射和PM2020蕴含分析作为条件/优先权背景。

FROZEN_INPUTS.json记原路径、SHA256、字节及行数，frozen_inputs目录保持原字节。PR1_NUMBERED_INPUTS.txt是便于定位的衍生逐行文本。逐行文本、哈希和链接检查均不承担数学验证。

## 2. 本轮定点原文重核

|ID|版本/来源与定位|实际使用范围|
|---|---|---|
|COL2019|Fomin、Golovach、Panolan、Simonov；arXiv1904.06141v1；https://arxiv.org/pdf/1904.06141v1；18页|本轮读取现有原文提取的p4 Definition1、p5 Theorem2和pp10–11 Lemma4/证明，核对原参数、随机性、取样数和误差界；不重新独立验证整个PTAS|
|PM2020|Fomin、Golovach、Panolan；DMKD34:478–532，DOI10.1007/s10618-019-00669-5；https://fedorvf.github.io/articles/2020/2020f.pdf|本轮复读原文提取的印刷pp520–523：Prop2、Extendable定义、Lemma11/12及证明、Th7/初始化；其余§7完整核读及公式目视记录沿前轮使用|
|KU2012作者稿|Komusiewicz、Uhlmann；2012-05-23，28页；https://fpt.akt.tu-berlin.de/publications/ce-bounded-degree.pdf|本轮复读p19模型框、pp22–25规则/Th6/Th7及证明，核对所有顶点预算、d/t/K及核化费用；正式排版版未取得|
|D13预览|Damaschke；LNCS8288:433–437，DOI10.1007/978-3-642-45278-9_38|沿已取得正式433–434页及原目视记录；不把435–437页记为本轮已读|

来源文件哈希及命名接收位置复查见SOURCE_RECHECK.json。没有新匹配全文。COL2026、D13缺页、KU最终版对应未因本轮工作被关闭。

原PDF预检状态保留：COL2019、KU作者稿PASS；PM2020为UNAVAILABLE（对象114/132偏移），D13预览为UNAVAILABLE（对象866/xref），前轮双解析和目视补核范围继续限定。未修复或覆盖原PDF。

## 3. 本轮新增证据类型

- 纸面证明：正常/待提交不变量精确化、C3逐项复核、逐边预算、终止度量、编码重建、费用。
- 纸面实例：A1–A10；所有距离和事件由块计数手工推导。没有运行实例枚举器。
- 文献推导：将指定定理映到T3，并剔除内部T1/T2已覆盖参数区间；没有全领域新颖性检索或全球首次结论。
- 文档取证：原稿及源字节绑定、JSON/链接/字符检查。

## 4. 独立性和归属

原路线文本按研究者明确校正记为AI辅助回复提出、研究者转交组织。PR-1与AC-1均有模型辅助，本轮已知原构造，未尝试宣称输入隔离或外部人工独立性。已知人工S1/S2核读不扩展为T3完整核读。

最终数学等级及优先权、最优性、应用和实现门分别见主稿DECISION。DELIVERY_CHECK.json只固定交付状态与完整性。
