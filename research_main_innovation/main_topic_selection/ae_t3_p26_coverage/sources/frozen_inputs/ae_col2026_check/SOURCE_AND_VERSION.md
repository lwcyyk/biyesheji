# COL2026来源与版本获取记录

版本COL26-SOURCE-1，2026-11-06。

**动作等级：UNRESOLVED_SOURCE。版本限定状态：COL2026_SOURCE_UNRESOLVED。** 本轮仍未取得可靠绑定到正式版的完整正文，版本差异核对和P26蕴含检验尚未完成。按本轮失败出口，只交付本文和[FULL_TEXT_REQUEST.md](FULL_TEXT_REQUEST.md)，没有生成版本差异或覆盖分析的占位稿。

## 1. 文献身份

Fedor V. Fomin、Petr A. Golovach、Fahad Panolan、Kirill Simonov：*Low-rank binary matrix approximation in column-sum norm*，Theoretical Computer Science，2026。

- DOI：[10.1016/j.tcs.2026.116240](https://doi.org/10.1016/j.tcs.2026.116240)。
- PII：S030439752600469X；出版方正常入口：[ScienceDirect](https://www.sciencedirect.com/science/article/pii/S030439752600469X)。
- 题名、作者、DOI及2026年10月发表记录：复用上轮公开元数据和出版方locator；这仅证明文献身份。
- 正式版精确发布日期、正文页数、PDF摘要：本轮未取得正文，保持待核。没有为不存在的2026 PDF登记SHA256。
- 作者接受稿与正式版的可靠关联：尚未建立。

## 2. 本轮获取结果

|入口|实际结果及使用范围|
|---|---|
|ScienceDirect正文|本轮正常GET返回HTTP403；没有获得PDF/HTML数学正文|
|公开搜索连接器|两个定向查询均随调用返回Transport send error|
|NVA机构库|首页及公开前端配置可读；配置确认搜索端点为api.nva.unit.no/search/resources。DOI/题名查询的TLS连接失败，原生客户端复核亦失败；检索没有完成，不能登记为无记录|
|ORCID公开作者链接|Fomin记录指向旧UiB主页，复用上轮该地址重定向系首页的结果；Golovach、Panolan所读公开记录没有researcher URL条目。这不表示作者没有公开主页或稿件|
|Simonov HPI主页入口|Python及原生客户端均在TLS连接阶段失败，页面内容未读|
|本地文件名定向查找|按DOI/PII/column_norm等线索查找，命中既有2019稿和上一轮记录，没有定位到标明2026版本的PDF；未据此声称本机所有PDF均已内容搜索|

sources/RETRIEVAL01–04*.json记录本轮URL、响应/异常、文件和可得摘要；SEARCH_CONNECTOR_RESULT.json保留连接器返回。公开站点既有JS仅作为机构库端点来源读取，没有执行其中程序或实现新机制。

## 3. 2019对照稿

已复用[arXiv1904.06141v1](https://arxiv.org/abs/1904.06141v1)及原阅读记录：18页；PDF SHA256为

`d208e61764cfdff2165e5acd80ecdd738bfd0fc38273dabc89dd497fe8d1eba3`。

同题同作者支持身份对应，内容一致性及其作为2026接受稿的资格仍需证据。2019稿的定义、随机PTAS和既有代入分析按原版本保留，不能用于关闭2026缺口。

## 4. 冻结的后续检验合同

共同显式R⊆{0,1}^q、L=|R|；m条长n二元串；q个有序中心；允许重复/未使用中心和未使用模式；每条输入串距至少一个中心≤r。要求确定性精确求解，并计入关系读取、处理与全部中心输出，达到

\[
2^{O(L^2+Lr\log(Lr+2))}(mn+qL)^c,
\]

c与L、r、q无关。没有正文时，不给正式版定理编号、版本差异或覆盖推导。

数学状态AE_PROVED_PENDING_PRIORITY、整体优先权PRIORITY_UNRESOLVED保持；独立数学复核/最优性/严格分离没有新增证据，机制实现保持未开始。
