# 冻结来源、规范和缺项

来源标识S1–S13、E1–E17沿用v3，原始记录见 [REVIEW_SOURCE_REGISTRY.json](provenance/REVIEW_SOURCE_REGISTRY.json)。实际携带的每个文件及其来源/阅读路径、字节数、SHA-256见 [PATH_MAP](provenance/PATH_MAP.json) 和 [MANIFEST](MANIFEST.json)。哈希核对与语义阅读分别登记。

## 原规范阅读定位

| 来源标识/冻结版本 | 包内原件 | 准确定位及用途 |
|---|---|---|
| S1 FI期刊，arXiv2410.03948v4，23页 | [PDF](frozen/crypto_fi_research_manuscript_v1/sources/FI_journal_20261110.pdf)、[TeX articlev08](frozen/crypto_fi_research_manuscript_v1/sources/articlev08.tex) | 9–11游戏/终局；12初始PKE；13 Ord/Tensor；14 TG/Upd；15 Theorem6.3；19–20 Lemma6.8/Theorem6.9；20–22实现/性能 |
| S2 官方2021-06-04，59页 | [PDF](frozen/crypto_fi_research_manuscript_v1/sources/official_frodo_2021.pdf) | 物理10最近整数平局向上；15 Encode/Decode及CDF质量关系；16 Algorithm5严格t>Tχ(j)、末项未访问；25 Table3质量和参数 |
| S11 官方2023-03-14，21物理页 | [PDF](frozen/crypto_fi_publication_impact_audit/sources/official_frodo_2023.pdf) | 物理8/印刷4 Sample；物理15/印刷11 TableA.3质量；物理16/印刷12 TableA.4 CDF；1344须结合S10 |
| S10 官方issue35，Patrick Longa，2024-11-27 | [E16只读工具回执](frozen/crypto_fi_official_profile_review/evidence/OFFICIAL_1344_ERRATUM_LIVE_RECEIPT.json)、[回执0](frozen/crypto_fi_research_manuscript_v2_1/evidence/official_1344_erratum_0.json)、[回执1](frozen/crypto_fi_research_manuscript_v2_1/evidence/official_1344_erratum_1.json) | Tχ(5)=32765，Tχ(6)=32767；[原URL](https://github.com/microsoft/PQCrypto-LWEKE/issues/35#issuecomment-2504969837) |

关键身份：FI PDF SHA-256 `bc48416b8b88c989ecf98e2d466d10b80d13fd72d88890d905bc3b991ca3d0d4`；TeX `16b64cf629041614f1191b76ac35dbf16fb0776aa262f247c1f4d2a574127d8b`；2021规范 `5c3440b311c7ee4fba8b9a12e0ff567eb75c29fef66843f3eecc16f137164f7d`；2023规范 `4688192bf5f5ac29e622ef359860890d2e97c224216baea2216dc42ef8d1547f`。

本轮对上述三个PDF重新运行结构预检，分别23/59/21页、PASS。Windows下预检器的--output分支要求POSIX dirfd；本轮采用其stdout JSON并由外层保存，预检数学/结构逻辑保持原样。新提取文本和stdout侧录位于provenance。结构预检仅承担读取完整性。原规范关键页图和E16语义阅读范围保持在冻结溯源中。

## 必须核对的合同

Ord：实际n列、D个位平面，与Tensor_D(S)=[S;2S;…;2^(D−1)S]同序。源Ord一般记号为n̄列，Upd传入n列；S/E按KeyGen与乘积取n×n̄。稿§2及F.1明确补齐，H1判断其对象合理性。

精确χ：分母65536，0计一次、其余正负各一次。640分子9288,8720,7216,5264,3384,1918,958,422,164,56,17,4,1；976分子11278,10277,7774,4882,2545,1101,396,118,29,6,1；1344分子18286,14320,6876,2023,364,40,2。已更正976及1344勘误均由CDF与全部输入字核对。Encode/Decode最近整数平局向上给640/976正确残差[-4096,4095]、1344为[-2048,2047]，模q解释。

概率合同：同A两代、全部相关原始χ之前固定A/消息、给定A的精确iid联合律；B采用一次未筛选TG/Upd、全部P₂秩自然积分。均匀Setup界额外平均独立均匀全矩阵A。初始事件在原实验完成后条件化。

## 来源缺项与实际影响

| 缺项 | 已有材料 | 实际影响/可先审范围 |
|---|---|---|
| CJL原PDF、2025索引文本至CRYPTO2026逐版本对应 | S5指定索引节选；ePrint2025/968及DOI题录身份 | 公式原图认证、编号和方法归属/优先权需补核；附录A自含算法/证明可按当前模型判断。A来源隐藏与B有限可靠性均有自含论证 |
| Nishimaki FI所引2024扩展版§5/Lemma5.7原图、会议版编号对应 | ePrint2021/221身份、FI引用及既有转录范围 | FI继承归约和Theorem6.9完整前件链保留待核；H3按精确样本/视图/时间逐项判断。当前A/B无LWE困难性前提 |
| 可归属作者UE源、配置、依赖和原消息轨迹 | 公开来源审计及上游基础KEM参照，WAITING_FOR_AUTHOR_ARTIFACT | 六配置的软件适用性、秘密seed联合律、筛选/算术及100次计时分母保持UNRESOLVED。单条完整消息轨迹可认证具体路径，概率迁移仍需联合律/有限损失证据 |
| 全球应用优先权的完整覆盖 | E13截至2026-11-10的有界审计、E15于11-11登记的六条查询 | 现有贡献措辞按实际检索范围使用，全球优先权待外部判断 |

## 载荷及封存规则

本包携带两项结果直接证明、证书、所用原论文/规范和相关身份/修正溯源。主稿直接超链接的历史版本形成辅助阅读闭包；JSON内未被运行入口读取的更早路径作为历史标识保留，记录所载文件与原包的完整性主张分别解释。原历史MANIFEST可以核其原始载荷哈希；该MANIFEST列举的更大历史目录按其原边界解释。

阅读转换记录使用原件SHA-256和副本SHA-256。Markdown逐字符保留所有链接目标以外正文，另加明确说明和必要行定位锚点；JSON仅改完整路径字符串，反向替换后整对象相等。原章节、式号、质量、分数和身份均保持。运行脚本适配仅增加os导入及根路径替换，完整差分随包。

阅读副本统一保存为UTF-8无BOM和Windows CRLF换行；JSON按两空格缩进重新序列化。原始BOM/CRLF情况和序列化规则逐份记入READING_TRANSFORMATIONS；数学内容一致性按规范化后的正文或完整JSON值检查。
