# 两项主结果的应用优先权与发表影响裁决

2026-11-10，Asia/Shanghai。身份：知情应用优先权与原论文声明审计。**A、B在本轮实际核读与公开检索范围内均保留具体新对象应用候选地位；相同FI对象、完整等价命题的公开直接先例尚未定位。** 这是一项检索有界的应用判断，全球首次与本项目公开发表优先权仍待独立证据。

本轮沿用v2的数学状态和精确模型，新增工作为公开版本、声明、代码线索、先例与影响比较。方法、对象贡献、条件安全前件及作者性能实例分别评价。原论文声明的逐条位置见ORIGINAL_CLAIM_AND_PARAMETER_MAPPING.md；本目录VERDICT固化输入、检索与交付字节。

## 1. 检索范围与时间界

复用截至2026-11-08的APPLICATION_PRIORITY_AUDIT及四份原始检索回执；本轮新增31条公开网页检索查询，覆盖题名、DOI、arXiv、作者、修订/勘误/公开讨论、Frodo型UE错误/噪声/正确性、公开token/仿射支撑/来源隐藏、代码、论文及学位材料。另做4条GitHub代码查询、2条格式正确的issue查询；初次issue请求422后按服务要求修正。所有实际查询及原始返回在evidence/SEARCH_LEDGER.json和web_01…09.json、github_*.json保存，截止2026-11-10。

| 路线 | 本轮实际观察 | 证据含义 |
|---|---|---|
| 出版社、arXiv原始记录 | 公开版本仍为v1–v4，期刊当前PDF=v4；页面未列新增勘误链接 | 只认证所见版本与页面状态 |
| 版本PDF/源包 | 4版PDF、4版源包均取得；TG/Upd活跃源块去空白后相同 | 算法核心沿版本保留；完整游戏/证明分别定位 |
| OpenAlex DOI记录 | cited_by_count=0，updated_date=2026-11-07 | 该数据库这一记录的索引状态 |
| Crossref DOI记录 | is-referenced-by-count=0；update-to未返回；关联预印本版本可见 | 登记的引用与更新字段，覆盖面另有边界 |
| Semantic Scholar | 429限流；保留错误回执 | 该路线未完成；其引用数与引用全文状态保持未知 |
| GitHub arXiv/题名/算法查询 | 返回RSS归档、基础PKE或异对象材料；FrodoPKE UE.TG返回空；两个issue精确查询total_count=0 | 未在所查默认分支/词法issue范围定位作者UE代码或同题攻击；全平台不存在代码的断言仍缺证据 |
| 搜索聚合、AI摘要与转引 | 多数返回原文转载和二手概述 | 仅作发现线索；其新颖性判断和重复转引不作为证明 |

查询批次的网页结果由工具合并返回。本报告保留批次与原始条目，不为每个查询虚构独立的零命中数字。精确数字查询未返回目标证明，同样只承担当前返回范围的观察。数据库引用数、搜索未命中与原文未取得具有不同含义。

## 2. 最强已核原始近邻与完整命题覆盖

| 来源及定位 | 同一构造/权限/事件 | 对A的覆盖 | 对B的覆盖 | 裁决和重开材料 |
|---|---|---|---|---|
| KLR2019，71页作者稿PDF17 Def11、27 Def14、44 AppB.2 | 确定性公开token一致性和概率重加密分布匹配；发表于FI之前 | 覆盖思想和攻击骨架：已知token下检验公开可测更新像；FI方阵逆使检验高效。未给FI原游戏、真实fresh、CF-1或3n+1预算命题 | 没有FI640的TG残差、联合列包或一步高错误下界 | **最强已核方法近邻**；同对象完整结果覆盖尚未建立 |
| 官方Frodo2021 §2.2.7，PDF18–19及Tables3/4 p25 | 基础PKE残差S′E+E″−E′S；精确有限产品律/卷积及全消息并集 | 精确χ表、采样和成熟分布工具已有来源 | 覆盖B的初始残差与成熟失败概率方法；未包含FI的TG/Upd、随机系数和行八阶混合矩 | **B的最强计算方法先例**；其基础PKE失败率无法直接给FI更新失败下界 |
| FI自身v1–v4 Theorem4.3/6.3 | 相同更新递推与W_print充分上界 | 已有噪声递推工具；CF-1需给同族完整正确性与预算 | 充分上界超过半宽只使判据失效，不能从中推出失败概率下界；源码四版均未给当前B命题 | 同对象先有正确性充分分析；**当前高错误概率结论尚无直接覆盖** |
| Nishimaki ePrint2021/221，最新2024-04-19 | 同研究链的LWE UE；FI援引其Lemma5.7 | 历史定点转录记录较长随机向量/不同矩阵接口；完整源图与映射当前缺失 | 未取得可核读的相同640一次更新概率命题 | **潜在同链先例的逐式覆盖未决**。最小材料为2024扩展版PDF、Lemma5.7及构造/参数邻文，附公开日期与哈希 |
| Lyu等作者代码README，固定commit e577f…，ePrint2022/874线索 | 基础FrodoPKE的格编码与AWGN近似/rounded Gaussian模拟 | README没有FI token或原游戏轨迹 | README研究改变编码的基础PKE DFR，采样也不同；未提供相同FI更新命题 | **作者README级筛选**；论文完整公式未核读，保留该层级，不作全文覆盖裁决 |
| Liu等CSS2022，DOI10.1007/978-3-031-18067-5_6，出版社摘要 | REACT+iO+puncturable PRF的混合UE；2022-09-29公开 | 摘要对象与当前FI公开矩阵token不同 | 摘要未给640一次诚实更新失败概率 | **原始摘要级近邻**。正文订阅受限，完整公式比较待合法全文；摘要差异只支持当前筛选 |
| FrodoKEM故障/侧信道/key-mismatch搜索线索 | 依赖故障、侧信道或不同解密反馈接口 | 权限与同一诚实原游戏尚无等价映射 | 改变密钥误差的攻击实验与诚实TG/Upd有不同输入族 | 作为发现线索排出当前直接证据集；若取得同算法同权限命题则重开 |

旧PRE/残差平均近邻的实读与权限比较沿用2026-11-08审计：腐化接收方秘密、隐藏token或同父重复输出与A的零Key、单挑战轨迹分别核账。本轮未为它们新增全文审阅认证。

## 3. 逐式迁移检验

**KLR到A。** KLR Def14给固定sp、old/new钥匙、token及密文的decrypt-then-encrypt与ReEnc分布相同要求。AppB.2展示公开token下，确定性重加密结果可用于发现不相容的混合替换。令FI公开上下文w=(父第一行h、P₁、P₂)，在P₂可逆时定义

\[
E_w=\{y:(y-hP_1)P_2^{-1}\in\mathcal S^n\}.
\]

这是成熟仿射代数对公开一致性思路的直接实例化。真实update必通过；独立均匀行通过概率为(25/q)^n。结果A的比较端是**真实fresh Enc**，它与token共享A；其概率不能由均匀行计数替代。v2用父低重量界、保留F₁的独立列卷积、逐固定P₂条件界给β≤αε_n，再证明P₂-only停止的付费放大。KLR固定上下文分布定义也没有直接给当前四查询的合法性和CF-1共同正确性。因此思想与骨架已有明确归属，完整FI对象命题仍包含实际新增的参数与概率工作。

**基础Frodo到B。** 官方规范的初始误差η₀=U₀E_old−F₀S_old+G₀对A消去。FI额外产生

\[
\delta=(HU_1+RU_2)E_{new}-(HF_1+RF_2)S_{new}+HG_1+RG_2.
\]

不能把该误差简单当成更多独立XY项：H与父币相关，新钥匙在多个项和行间共享。B分别固定单坐标环境F及同行环境V；在较小B环境下积分真实1280个a/b系数，使用绝对Fourier矩、差值律、全频率包络和点态弦线。行上界经事件包含推出完整上界，条件于初始正确再使用事件比率。精确有限分布、Fourier、Chernoff、Cauchy–Schwarz、Jensen和有向算术均属经典工具；本轮对象增量为把它们用于该残差及其真实依赖，给出严格有限数值。初始规范、粗最坏界和Gaussian近似均未单独达到B的完整命题。

## 4. A的应用与影响裁决

**已核准对象内容。** 在期刊/v4打印算法、列数规范化和iid χ640下，原游戏合法且无需Key腐化的高效支撑区分；逐固定A/P₂的真实fresh界；真实轮换预算内放大；同一CF-1族的最长n次逐样本正确性。来源、权限与参数的具体匹配构成对象贡献。

**成熟覆盖。** 公开token一致性和分布匹配归属KLR，矩阵逆、支撑成员检查、卷积收缩、并集、二元秩及停止放大各有成熟基础。当前证据支持具体密码分析应用，通用技术首创和相对所有成熟方法的资源分离均另需证明。

**对原文影响。** A对源rand-ind-eu-cpa构造级来源隐藏声明形成直接障碍；它同时展示正确性与来源隐藏失败可在同一打印参数族出现。Theorem6.9的条件逻辑继续采用v2精确审计：H_rich在CF-1已失效；H_fixed和完整归约未认证。常量尺寸关系、基础FrodoPKE/KEM的安全声明、明文恢复能力和实际软件破坏分别有自己的证据责任。

**允许的最强措辞。** “我们给出FI期刊/v4打印构造在明确Ord与独立采样合同下的原游戏来源隐藏攻击，并在同一逐样本正确族上用≤3n+1次调用得到Δ→1；在截至2026-11-10的实际核读与定向检索范围内，未定位相同构造、权限和完整命题的公开直接先例。”

**最小改变材料。** 带可核公开时间、完整同对象攻击/直接推导的原文；改变游戏或更新公式的正式版本；对Ord合同、F₁保留或停止条件的具体反例；精确可用LWE归约及其真实困难前件。

## 5. B的应用与影响裁决

**已核准对象内容。** 官方640核心数值可由原论文引用对应；对打印均匀Setup及独立精确χ模型，近乎全正确的初始消息经过一次诚实未筛选更新后，完整错误率≥99.9969655%，初始正确条件下保持该显示下界。该结论直接支持**该具体有限配置的一步可靠性失败**。

**成熟覆盖。** 原FI有更新误差递推与充分最坏界，基础Frodo有初始PKE精确卷积失败分析。二者尚未提供当前同行混合矩、完整消息上界或同一条件化数值。当前贡献为具体有限模型可靠性密码分析与认证概率，工具归属按经典方法登记。

**对原文影响。** 640不满足Theorem6.3打印前提，B评价前提之外的具体行为。原文p2使用渐近negl(n)定义；单个有限n的错误下界本身不能裁定任意渐近族。性能段明确测试640/TG/Upd，却未报告更新后消息比对、成功分母或深度预算。B使“标准640配该打印机制构成可靠实用UE”的解释需要更正或配置解释。原始耗时数据是否准确、作者程序是否具有同一错误率，需代码/日志和分布算术对应。

**允许的最强措辞。** “FI打印算法配官方640数值参数，在均匀Setup、iid χ640、既定Ord、一次未筛选诚实TG/Upd和官方舍入模型下，初始完整正确率≥1−2^-132，更新完整错误率≥99.9969655%，且初始正确条件下显示下界保持。当前公开性能报告缺少把实测程序与这一模型逐项对应的工件。”

**最小改变材料。** 已日期认证且同算法/参数/联合律的一步高错误命题；指出当前列包/特征函数/有向证书的具体错误；作者完整commit/config/随机带/整数与舍入证据；明确修改后的参数或算法及其新正确性证明。

## 6. 当前贡献层级与下一步

当前最强统一定位为：**对已发表Frodo型UE的构造级来源隐藏密码分析及具体640配置可靠性分析，并附条件安全前提与发表声明范围审计。** 两个主结果各自有精确对象、量词、纸面证明与有限证书，具备独立密码分析短文或毕业论文核心研究章节的实质内容。通用新方法、全球优先权、标准FrodoKEM被攻破、作者软件实测失败和期刊接收均有独立的证据门槛。

最高价值的外部输入是作者UE实现的准确版本及一条有消息比对的完整调用轨迹；它决定性能表与B之间的迁移。最高价值的人工数学复核为HUMAN_REVIEW_ENTRY的三个明确问题。Nishimaki扩展版Lemma5.7与构造邻文可补齐先例/继承链；S2限流解除后可补其引用图。本轮无需为已完成的有限可靠性下界扩大采样或实现攻击。

旁支INC976已确认需在后续作者版本修正；它不进入A/B。本轮完成条件为在可复核范围内形成上述应用与影响裁决，受阻来源均给重开输入，历史材料保留原字节。


## 来源与复核记录入口

- **O4**：[FI期刊/arXiv v4](https://fi.episciences.org/17222/pdf)。版本：23-page current publisher PDF byte-identical to arXiv2410.03948v4；公开时间：arXiv v4:2025-12-29; journal online:2026-01-11; PDF volume year:2025。 本地：[arxiv_v4.pdf](D:/毕业设计/crypto_fi_publication_impact_audit/sources/arxiv_v4.pdf)。
- **O1**：[FI历史公开版本](https://arxiv.org/abs/2410.03948v1)。版本：arXiv2410.03948v1；公开时间：2024-10-04。 本地：[arxiv_v1.pdf](D:/毕业设计/crypto_fi_publication_impact_audit/sources/arxiv_v1.pdf)。
- **O2**：[FI历史公开版本](https://arxiv.org/abs/2410.03948v2)。版本：arXiv2410.03948v2；公开时间：2024-10-08。 本地：[arxiv_v2.pdf](D:/毕业设计/crypto_fi_publication_impact_audit/sources/arxiv_v2.pdf)。
- **O3**：[FI历史公开版本](https://arxiv.org/abs/2410.03948v3)。版本：arXiv2410.03948v3；公开时间：2025-08-09。 本地：[arxiv_v3.pdf](D:/毕业设计/crypto_fi_publication_impact_audit/sources/arxiv_v3.pdf)。
- **F21**：[FrodoKEM官方2021规范](https://frodokem.org/files/FrodoKEM-specification-20210604.pdf)。版本：59-page2021-06-04 frozen specification；公开时间：2021-06-04。 本地：[official_frodo_2021.pdf](D:/毕业设计/crypto_fi_research_manuscript_v1/sources/official_frodo_2021.pdf)。
- **F23**：[FrodoKEM官方2023提案](https://frodokem.org/files/FrodoKEM-standard_proposal-20230314.pdf)。版本：21 physical PDF pages; printed AnnexA pp11-12；公开时间：2023-03-14。 本地：[official_frodo_2023.pdf](D:/毕业设计/crypto_fi_publication_impact_audit/sources/official_frodo_2023.pdf)。
- **KLR**：[Klooß–Lehmann–Rupp2019](https://orbilu.uni.lu/bitstream/10993/50226/1/Publikation_UE_Eurocrypt_2019.pdf)。版本：71-page institution author version；公开时间：2019 EUROCRYPT; exact first-preprint day not newly verified。 本地：[KLR2019.pdf](D:/毕业设计/crypto_fi_research_manuscript_v1/sources/KLR2019.pdf)。
- **N**：[Nishimaki前驱](https://eprint.iacr.org/2021/221)。版本：ePrint2021/221 landing page; exact extended PDF unavailable；公开时间：received2021-03-02; latest revision2024-04-19; note dated2024-04-18。
- **LC**：[Lattice Codes for Lattice-Based PKE](https://github.com/shx-lyu/lattice-codes-for-pke/blob/e577f664353a6ea8b679815c314a8e3f04264657/README.md)。版本：Pinned README commit e577f664353a6ea8b679815c314a8e3f04264657；公开时间：README modified date returned:2023-07-16; exact paper initial date not newly verified。
- **UHE**：[Liu等CSS2022混合UE](https://link.springer.com/chapter/10.1007/978-3-031-18067-5_6)。版本：Springer publisher abstract; pp71-85; DOI10.1007/978-3-031-18067-5_6；公开时间：2022-09-29。
- **GH**：[官方Frodo参考仓库](https://github.com/microsoft/PQCrypto-LWEKE)。版本：microsoft/PQCrypto-LWEKE directory listing; FrodoKEM tree4f337a3ee6945cc8e9949a8ddba34f51d88325d9；公开时间：current default branch viewed2026-11-10; author UE commit unspecified。

每项具体支持位置、获取时间、阅读等级及SHA256见 [SOURCE_LEDGER.json](D:/毕业设计/crypto_fi_publication_impact_audit/evidence/SOURCE_LEDGER.json)；实际检索输入与原始返回见 [SEARCH_LEDGER.json](D:/毕业设计/crypto_fi_publication_impact_audit/evidence/SEARCH_LEDGER.json)。
