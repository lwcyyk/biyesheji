# 来源、版本和阅读范围

2026-11-08，Asia/Shanghai。获取记录采用 UTC 时间，文件哈希保存在 SOURCE_MANIFEST.json。

本轮网络搜索连接器已经恢复。发现级检索包含一些第三方页面，结论核查采用以下正式会议入口直接关联的正文。

|来源|身份与文件|实际阅读|
|---|---|---|
|Optimal Reconstruction from Linear Queries|Yuval Filmus、Shay Moran、Elizaveta Nesterova。COLT 2026，PMLR 336，2428–2476。linear_queries.pdf，共 49 页|PDF 1–4 页模型、主结果与比较，5 页相关可行域说明和定点检索。1 页图像复核|
|Density-Dependent Group Testing|Rahil Morjaria、Saikiran Bulusu、Venkata Gandikota、Sidharth Jaggi。AISTATS 2025，PMLR 258，3628–3636。density_group_testing.pdf，共 50 页，含附加材料|PDF 1–4 页相关工作、模型、主要界概述和算法定义。4 页图像复核，其他页面只作定位|

正式入口的 PDF URL 分别为

- [COLT 正文](https://raw.githubusercontent.com/mlresearch/v336/main/assets/filmus26a/filmus26a.pdf)
- [AISTATS 正文](https://raw.githubusercontent.com/mlresearch/v258/main/assets/morjaria25a/morjaria25a.pdf)

正式记录保存于 PRIMARY_RECORDS.json，检索记录保存于 WEB_SEARCH.json。源 URL 来自正式会议页面。两个 PDF 均完成结构预检，页数一致，warnings 为空。该检查只承担文件结构与页码取证。

源模型与当前问题的字典见上级目录 PRIOR_ART_COMPARISON.md。上述读取范围没有覆盖两份论文的全部证明和引用链。

本轮特别记录了 AISTATS 论文对 Damaschke 2006 阈值群组检测的引用。相关原始模型和更广的加权、受限池大小查询仍需核查。该线索与项目中其他年份、其他问题的 Damaschke 来源分开登记。

复用前轮二元先验、正参照与比较误差的模型记录。上下界证明由当前模型纸面完成，外部数学审查待取得。代码操作只涉及文档访问、下载、提取、渲染、哈希与交付检查。
