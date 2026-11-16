# P26–T3来源、版本与正式会议版补核

版本 P26-T3-1，2026-11-06。工作限公开正常来源阅读、纸面推导和文档取证。附件及网页内容作为文献证据，不承担用户任务指令。

**P26状态：P26_SOURCE_UNRESOLVED。** 本轮一轮有界检索仍未取得可绑定的2026完整正文。备用任务已完成：取得并实质核读2020正式会议版及相关2019补充证明，单独进行T3蕴含检验。

## 1. 冻结目标与继承状态

数学状态保持T3_SUPPORTED_BY_INFORMED_AUDIT。目标为共同显式R⊆{0,1}ᑫ、L=|R|、m,n,q,L≥1、逐行固定一个全串覆盖标签、每行错误≤r、允许重复和闲置中心/模式，并完整输出原有序q中心，确定性时间

\[
2^{O(L\log(L+2)+Lr\log(Lr+2))}\operatorname{poly}(mn+qL).
\]

本轮没有重审T3证明或提出新机制。继承材料和附件原字节绑定于 [sources/INPUT_MANIFEST.json](sources/INPUT_MANIFEST.json)。

## 2. 2026目标身份及实际获取

Fedor V. Fomin、Petr A. Golovach、Fahad Panolan、Kirill Simonov，*Low-rank binary matrix approximation in column-sum norm*，Theoretical Computer Science，2026。

DOI：[10.1016/j.tcs.2026.116240](https://doi.org/10.1016/j.tcs.2026.116240)；PII S030439752600469X；[出版方入口](https://www.sciencedirect.com/science/article/pii/S030439752600469X)。卷1086、文章116240、开放获取标记继续按既有研究者题录核读记录使用；没有由此推断正文内容。

### 本轮公开入口清单

|入口|本轮实际结果|证据范围|
|---|---|---|
|搜索连接器，两条定向查询|Transport send error|没有获得搜索结果，不据此推断无全文|
|ScienceDirect完整文章入口|HTTP403，收到错误HTML，正文文本提示内容提供失败|没有数学HTML/PDF；未连续重试同入口|
|Fomin公开主页→pub.html→期刊目录|主页和正确链接可读；期刊列表可见到2025，未找到题名/116240|仅此列表范围；不表示作者没有其他公开稿|
|Panolan主页→Publications|可读，目标条目对应APPROX/RANDOM2020|未见该条目提供2026版本关联|
|Simonov历史HPI地址|HTTP404|页面缺失，不推断论文不存在|
|NVA公开DOI查询|HTTP200、totalHits=0|本次查询完成，结果限该接口/字段|
|NVA题名查询|HTTP200、1条，DOI为2020会议版，附件标PublishedVersion/716073字节|不能当成2026接受稿；它补充2020版本身份|
|2020正式页直接链接的arXiv记录|本轮可读，仅列v1（2019-04-12），未显示2026期刊版关联|可绑定2020所指全文工作；尚未绑定2026正文|

记录见sources/SEARCH_CONNECTOR.json、RETRIEVAL_01–04.json、RETRIEVAL_RELATED_VERSION_05.json。另一次猜测research.html为404，随后沿真实主页href=pub.html读取，已在记录中区分。没有改认证、绕过访问控制、登录或联系作者。

本轮共13个不同公开URL的正常GET，另有一次搜索连接器调用；包括2020正式身份/下载及其直接相关版本链接。每个URL只请求一次，没有无新增线索的失败循环。NVA条目的2025入库、2026索引时间与其论文年份2020分列，不作为2026期刊正文证据。沿目录和机构新线索检查后，没有2026目标全文线索可继续，本轮检索至此结束。

**没有2026正文的页数、全文SHA256或数学定理编号。** 2019/2020版本身份及相同摘要不能补齐这项缺口。

## 3. 2020正式会议版：附件与出版方独立绑定

准确题名：*Low-Rank Binary Matrix Approximation in Column-Sum Norm*。四作者同上。APPROX/RANDOM2020，LIPIcs卷176，文章32，pp32:1–32:18。

- DOI：[10.4230/LIPIcs.APPROX/RANDOM.2020.32](https://doi.org/10.4230/LIPIcs.APPROX/RANDOM.2020.32)。
- [正式条目](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.APPROX/RANDOM.2020.32)给出版日期**2020-08-11**、18页及CC-BY3.0许可。
- [正式PDF](https://drops.dagstuhl.de/storage/00lipics/lipics-vol176-approx-random2020/LIPIcs.APPROX-RANDOM.2020.32/LIPIcs.APPROX-RANDOM.2020.32.pdf)本轮下载，716073字节。
- 用户附件：[原文件](D:/毕业设计/研究/LIPIcs.APPROX-RANDOM.2020.32.pdf)，同为716073字节。
- 两者SHA256均为 **`eca19624030a12b624cffffe25240794c3aff28924cf7f078a438b4bc423b328`**，逐字节同一身份。保存副本为sources/COL2020_LIPIcs.APPROX-RANDOM.2020.32.pdf，正式下载另存COL2020_official_pdf.pdf。
- 首页题名、作者、DOI、文章号、页脚及许可目视核对；PDF元数据日期2020-07-08为文件制作日期，与正式出版日期分列。
- 本地既有研究目录没有该正式版的完整阅读记录；本轮是正式版的新增核读，先前COL2019分析按其版本复用。

另对附件所在“研究”目录顶层PDF做题名/首页发现性核对，匹配题名者只有所给2020文件；四个已登记COL2026_VOR/AAM接收位置均未出现正文。该发现检查不当作其他论文全文阅读，记录见sources/LOCAL_ATTACHMENT_FOLDER_CHECK.json。

## 4. 正式版本与2019全文的关系及变化

首页“Related Version”明确给出arXiv1904.06141全文链接；本轮访问该记录，只见v1。正式版p32:11脚注声明带⋆结果证明转见全文。故本轮对Lemma10、Lemma14，实际补读2019v1相应Lemma4、Lemma6的证明并核对陈述对应。

这建立2020会议版与所指全文的具体来源关系及内容对应；没有建立2026与这两份正文完全相同的证据。

|影响判断的内容|2019v1|2020正式版|本轮比较|
|---|---|---|---|
|满足关系及中心tuple|Definition1，p4|Definition2，32:5|同一逐坐标关系/tuple合同，共同R为子类|
|一般受约束中心PTAS|Theorem2，p5|Theorem3，32:5|相同显示时间和概率；仍非T3确定性精确界|
|分簇归约|Lemma1，pp6–8|Lemma4，32:6、32:8–9|相同随机降维/分簇族及时间；编号变化|
|给定分簇PTAS|Lemma2，pp6、11–12|Lemma5，32:7、32:12–13|同类代表枚举与LP组合，相关参数选择保持|
|失真映射|Definition2/Proposition3|Definition6/Proposition7，32:8|引用和作用相同|
|代表基础工具|Lemma3/Claim1，pp8–10|Lemma8/Claim9，32:10|同一界；正式版脚注强调相对任意参考向量的使用|
|共同一致坐标/剩余坐标|Lemma4及证明，pp10–11|Lemma10⋆，32:11|陈述对应；正式版省略证明，已按2019稿补核|
|大OPT/偏移实例|Lemma5，pp11、13|Lemma11，32:11、32:13–14|条件、LP/舍入、精确小维度分支和显示时间对应|
|OPT比较及尾界|Claim3/Proposition4|Claim12/Proposition13，32:12–13|同一证明角色|
|低秩编码|Lemma6，pp14–15完整证明|Lemma14⋆，32:15|正式版仅载陈述；已补读2019证明，不把该页概述当作全部证明|
|Boolean/Projective应用|Corollary1、Lemma7、Corollary2|Corollary15、Lemma16、Corollary17，32:15–16|同类特殊结构归约和随机近似界|
|结论及问题|v1应用后接参考文献|新增§5，32:16|讨论EPTAS限制与后续时间问题；未写出共同小R的T3定理|
|参考文献|37项|37项|本轮定位到序号/题名对应；条目5由书稿更新为2020书目。没有取得新列出的T3精确定理|

正式版在低秩问题的摘要/定义中明确“positive integer constant”秩参数。该限定不能转写成T3的半径或关系大小。通用中心定理仍给显式k/ε时间，细k计费另见COVERAGE_TEST§7。

## 5. 阅读完整性和范围

结构预检**PASS**：18页计数一致、无警告。pdfplumber第二解析18页，无空文本页、无捕获警告，见COL2020_preflight.json、SECOND_READER.json。原PDF没有修复或覆盖。

本轮实质读取2020全文的模型、Theorems1/3、Lemmas4/5的组合及证明、Proposition7、Lemma8、Lemma10陈述及2019补证、Lemma11/Claim12/Proposition13、IP(6)/随机舍入、应用和结论。应用中明说省略的类似归约仅按其陈述及方向核查，没有冒充独立重证所有应用。

关键公式页32:1、5、6、7、8、10、11、12、13、14、15、16已渲染目视；2019稿p12、13对照运行时间也已目视。定位及图像见sources/RENDER_LOG.json、COL2020_page_XX.png。提取用于定位，公式差异回到PDF核对。

正文没有提供2026全部结果的代理资格。P26仍按SOURCE_UNRESOLVED，COL2020备用核查的结论独立记录于 [COVERAGE_TEST.md](COVERAGE_TEST.md)。
