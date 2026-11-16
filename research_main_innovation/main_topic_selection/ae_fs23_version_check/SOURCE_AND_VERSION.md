# FS23一轮公开来源获取记录

FS23-1，2026-11-07（Asia/Shanghai）。AUTO-RESEARCH-FS23-009。

**结束状态：FS23_SOURCE_UNRESOLVED。本轮获取动作结束，完整且可绑定的期刊正文仍缺。**

## 1. 目标身份与证据等级

Sayan Bandyapadhyay、Fedor V. Fomin、Petr A. Golovach、Kirill Simonov，*Parameterized Complexity of Feature Selection for Categorical Data Clustering*，ACM Transactions on Computation Theory15(3–4)，2023，24页。DOI：[10.1145/3604797](https://doi.org/10.1145/3604797)。

委托题录指定Article7；本地已存DOI元数据核对题名、四作者、卷期、1–24页及2023-12-12日期，article-number字段为空。Article7及正文首页、实际PDF页数/版本声明尚未由本轮全文独立核验。

已存MFCS2021正式版和arXiv2105.03753v2仍按各自版本使用。同题、同作者、同摘要或元数据关联不自动证明2021稿等于2023期刊正文。

待检T+合同保持：Q为K×w共同显式模板，逐列静态域/逐行标签列表，每行使用一个全串固定标签、Hamming半径≤1，允许闲置角色，读取及全部原有序中心恢复计费；目标2^{O(w log(w+2))}poly(N)，输入指数统一。P13/P14较弱基本FPT及2^{O(w²)}参考保持，本轮不重复推导。

## 2. 复用监督本轮已执行记录

本轮先读取监督的`research_supervision/reviews/009_FS23_RETRIEVAL_LEADS.json`，汇总记录时点2026-11-06T23:20:19Z（本地2026-11-07）。以下为**监督提供的获取记录**，本worker没有重复相同拒绝入口：

|入口|已有实际结果|本轮处理|
|---|---|---|
|[PDX机构库条目](https://pdxscholar.library.pdx.edu/compsci_fac/349/)|监督已读题录，关联期刊/作者/DOI/Download|复用身份线索，元数据不算PDF|
|[PDX直接Download](https://pdxscholar.library.pdx.edu/cgi/viewcontent.cgi?article=1355&context=compsci_fac)|监督click和普通urllib均HTTP403|本worker0次重试|
|[Fomin完整期刊目录](https://fedorvf.github.io/articles/full_fvf_publications.html)|监督已读，可见2023列表未定位本题|不重复；不推断目录其他部分或公开稿不存在|
|[Sayan主页](https://sites.google.com/view/sayan-bandyapadhyay)|监督已读首页，相关出版物/附件尚未检查|链接发现线索；监督记录没有在本地附首页正文|

## 3. 本worker一次有界核查

先按题名/DOI/FS23文件名检查本地，新增工件只有监督任务及线索记录；原目录仍是MFCS正式/v2、期刊元数据和旧错误HTML，没有新的FS23正文。

|实际动作/入口|结果|取得内容及实际读取范围|
|---|---|---|
|Sayan主页普通GET一次|curl连接失败，HTTP000，无正文；退出码1|不判为站点403，也不声称读过出版物/附件|
|检索连接器：两条精确查询＋出版方页面命令，一次批调用|Transport send error|没有得到检索/站点结果；不把它当作未命中或出版方HTTP状态|
|[ACM正常页面](https://dl.acm.org/doi/10.1145/3604797)普通GET一次|HTTP403，5447字节HTML挑战页|只读错误类型，没有文章HTML/公式/证明；未处理挑战或尝试绕过|
|Bing精确题名＋DOI查询一次|HTTP200，但可见结果为parameterized词典/编程内容|没有形成论文全文线索，不当作查新阴性证据|
|[第一作者ORCID](https://orcid.org/0000-0001-8875-0102)，来自已存DOI作者链接|HTTP200，67250字节应用外壳|仅显示需JavaScript，未取得作者出版物记录或论文链接；未猜API/附件路径|

本轮没有重复PDX Download，没有再猜PDF路径，没有联系作者或使用账户。没有可继续的本地全文链接时结束该轮。ORCID/search页的200不等于取得论文正文。

成功响应文件的保存mtime用作接收时点代理，失败连接/工具错误没有伪造精确请求时间；实际UTC/Asia-Shanghai日期、URL、类型、字节与SHA256见sources/ACQUISITION_LOG.json和SOURCE_MANIFEST.json。原始工具返回及可见文本保留于sources。

## 4. 尚未取得与禁止替代的内容

- FS23完整24页正式版，或有可靠期刊DOI关联的作者接受稿/完整公开稿。
- 与定义、MFCS Theorem4期刊对应命题、代表/交换/超图结构有关的完整证明及依赖附录。
- 若正式页码或编号改变，需要实际正文对应；本轮不填写差异表或期刊定理号。

当前只核题录与获取状态。没有完成FS23到T+的蕴含分析；旧FS21/v2分析继续独立有效。`TPLUS_IMPLICATION.md`未生成。

## 5. 最小资料清单

需要研究者通过正常公开或机构授权渠道提供下列任一项：

1. DOI10.1145/3604797的完整正式PDF/完整数学HTML，含相关证明和依赖附录；
2. 完整接受稿/作者稿，附出版方、作者或机构的可靠版本关联声明；页数可不同，数学内容必须完整。

文件应保留首页、版本说明、来源URL/接收日期。单独机构摘要、Download标记、搜索片段或2021v2不能补齐此项。本文件是资料缺项说明，没有向任何人发送索稿。

作者主页的附件发现仍未完成。若监督仍有已读首页正文，可在其缓存中提取真实publication/attachment链接供后续评估，避免重新请求首页；本worker当前本地没有该正文，不据此启动另一轮获取。
