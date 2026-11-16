> 可移交阅读副本。数学正文、章节和式号沿用冻结原件；仅转换链接、添加行定位锚点及本说明。[冻结原件](../../frozen/crypto_fi_publication_impact_audit/ORIGINAL_CLAIM_AND_PARAMETER_MAPPING.md)。历史命令按来源记录保留；本包公开重放入口为根目录 REPLAY.md。

# 两项主结果的应用优先权与发表影响核查：原声明与参数映射

2026-11-10，Asia/Shanghai。身份：**INFORMED_APPLICATION_PRIORITY_AND_ORIGINAL_CLAIM_AUDIT（知情应用优先权与原论文声明审计）**。本轮阅读既有作者证明与AI审阅后进行来源和命题比较，新增独立数学审阅计数为0。

本轮裁决绑定期刊 DOI [10.46298/fi.14425](https://doi.org/10.46298/fi.14425) 的当前23页文件，与 arXiv:2410.03948v4 逐字节相同。结果A评价声明合同中的来源隐藏安全；结果B已经支持该具体640有限配置的一步可靠性失败。作者性能表对应的实际程序仍需版本、配置和联合采样证据。

## 1. 输入和版本身份

v2四份文件及其规范化封存载荷核验通过，实际使用的历史指纹逐项对照。正文与证明继续从v2只读引用。完整指纹和当前来源记录见本目录VERDICT与evidence/INPUT_FINGERPRINT_VERIFICATION.json、SOURCE_LEDGER.json。字节核验与语义阅读分别登记。

| 公开对象 | 公开时间 | 实际取得与比较 | 与本轮结论的关系 |
|---|---|---|---|
| arXiv v1 | 2024-10-04 22:16:20 UTC | 17页PDF和6文件源包 | TG/Upd活跃源块与v4去空白后相同；Theorem4.3在PDF11，4.9在15；实现/表在15–16 |
| arXiv v2 | 2024-10-08 14:26:09 UTC | 17页PDF和5文件源包 | 同样的TG/Upd核心；Theorem4.3在PDF10，4.9在15；表在15–16 |
| arXiv v3 | 2025-08-09 00:32:48 UTC | 23页PDF和7文件源包 | 核心更新块相同；Theorem6.3在15，6.9在20；表在21 |
| arXiv v4 | 2025-12-29 13:10:25 UTC | 23页PDF和6文件源包 | 本轮主对象；articlev08.tex与v1研究稿冻结源字节相同 |
| 当前期刊 | 在线2026-01-11；接受2025-08-08；PDF卷年2025 | 2026-11-10重新获取 | PDF哈希与v4相同；当前落地页未列新增勘误链接 |

v4/期刊PDF SHA256：`bc48416b8b88c989ecf98e2d466d10b80d13fd72d88890d905bc3b991ca3d0d4`。TeX：`16b64cf629041614f1191b76ac35dbf16fb0776aa262f247c1f4d2a574127d8b`。版本日期来自arXiv原始版本表，获取时间和所有下载哈希见evidence/PUBLIC_ACQUISITION.json。源块比较只认证所列活跃代码块的文本身份；各版完整游戏与安全证明仍按其版本分别审计。

## 2. 两项冻结结果

**A（共同正确族中的来源隐藏攻击）。** FI打印算法配Ord列数规范化及独立χ640；λ≥2，n=8λ，D=8ceil(log₂n)，q=2^D，m̄=n̄=8，B=2，T=t_max=n。对每个先固定A、所有合法消息和支持内诚实随机样本，初始加密及最长n次更新逐样本正确。原rand-ind-eu-cpa游戏存在合法PPT攻击，调用≤3n+1，Δ≥1−(3/4)^n−ε_n=1−negl(λ)，故Δ→1。难度假设数量为0；条件安全定理前件另按§6评价。

**B（640一次更新可靠性）。** 固定n=640、D=15、q=32768、m̄=n̄=8、B=2；均匀Setup、全部原始χ640坐标/调用独立、既定Ord、一次诚实未筛选TG/Upd及最近整数平局向上。任意抽样前固定合法128位消息：初始完整正确率≥1−2^-132；更新后指定坐标正确率∈[0.2499054,0.2500946]，指定行全正确率∈[0.0000152532,0.000030345]，完整正确率≤0.000030345、错误率≥99.9969655%。条件于初始完整正确后，更新显示界保持。更新概率平均均匀Setup及全部诚实币；初始界还逐固定A成立。

## 3. 原论文声明对应表

以下采用精确公式和短语作原文锚点，其余内容为定位明确的中文转述。页码均为当前23页PDF的物理页码，恰与印刷页码相同；源行号指本轮取得的articlev08.tex。

| ID | 原文锚点及位置 | 算法、参数和前提 | A/B能够直接评价的部分 | 剩余证据与范围 |
|---|---|---|---|---|
| O01 | p2：Pr[UE.Dec(k_e2,ct_e2)≠m]≤negl(n) | 对消息、连续更新链定义UE正确性；正确性和安全性分别定义 | B刻画一个明确有限配置的一步高错误行为；A的族自身正确 | 单个固定n=640的数值界只承担具体配置评价；任意渐近正确性族的全称反驳另需相应族命题 |
| O02 | p11/TeX493：D∈Z>0，q=2^D，B∈{0,…,D}，n,m̄,n̄>0，8整除n | 打印参数域没有在此写D≤16；χ为小支持对称表 | CF-1满足这些明写类型及维度条件；固定25点χ640符合表分布描述 | 官方2021 API p14另写D≤16，CF-1属于打印域的扩展参数模型；LWE困难前件与成员资格分别核准 |
| O03 | pp11–12/TeX496–499：Sχ={−s,…,s}、反CDF及Frodo.SampleMatrix | 引用[1]2021、[2]2023；打印的χ矩阵记号 | χ640的精确边缘律与v2一致，A/B均携带独立采样合同 | 实际seed复用/域分离、跨矩阵联合律需代码或明确随机带说明 |
| O04 | p12/TeX509–520：A←R_q^(n×n)，B=AS+E | 打印Setup均匀A、两代共用A | B的H重量二项律与此平均模型对应；A逐固定A成立 | 官方AES/SHAKE使用128位seed展开A；实际软件分布与真正均匀A的迁移需单列 |
| O05 | p12/TeX557–560：ec(k)=kq/2^B，dc(c)=⌊c2^B/q⌉ mod2^B | 引用官方编解码 | B正确集合为{−4096,…,4095} mod32768；消息标签平移相容 | 软件舍入、整数表示、取模与打包要与规范对应 |
| O06 | p13/TeX580–590：Ord域为m̄×n̄，Tensor域为n×n̄；Remark6.1：Ord(C)Tensor_D(S)=CS | Upd实际调用Ord(C₁)，C₁有n列；TG第一块有nD行 | 最小列数重载给v2模型；一致位序重排保持A/B | 字面域在n≠n̄时类型不相容；行为变化的解释需要另一份精确定义，见§5 |
| O07 | p14/TeX633–653：P₂=U₂A+F₂，Y=HP₁+RP₂ | P₂为n×n，完整token公开；Upd仅新采R←χ | A可逆分支恢复r̂=(y−HP₁)P₂^-1并检验Sχ^n；B直接使用真实更新残差 | 未筛选TG是B合同；实际程序重试、额外噪声等均需映射 |
| O08 | p15/TeX669–703：W_print<q/(T2^(B+1))，随后短句“then the scheme is correct” | W_print=2(n²Ds³+n²s³)+nDs+ns²；T称最大epochs | B的640实例对任意整数T≥1均在前提之外；A另有完整逐样本证明 | 初始B₀与更新计数需完整计账，见§6；前提成立的源条件句保持其范围 |
| O09 | p19/TeX872–877：LWE assumption⇒Eq(6)；援引Nishimaki Lemma5.7，省略证明 | 精确样本数、秘密先验、辅助视图和时间损失未展开 | A的公开事件定位相邻端点障碍；v2保留H_rich/H_fixed分支 | 扩展版原图403，需完整参数化归约；两个源对象的引用继承尚待逐式认证 |
| O10 | p20/TeX882–886：“Under the LWE assumption”；Adv≤negl(n) | Theorem6.9，backward-leak uni-directional rand-ind-eu-cpa | A直接给同一游戏的构造级区分事实 | 非空困难前件下的条件定理反驳资格另需精确H，见§6 |
| O11 | pp20–21、Tables1/2、TeX893–959 | AES/SHAKE×640/976/1344；KG、Enc、Dec、TG、Upd的均值/标准差 | B说明标准640数值配打印iid/均匀模型需要严肃可靠性解释 | 表格未给D/B/CDF/config/代码版本；Dec输入的来源和更新后比对流程未报告 |
| O12 | pp20–22/TeX961–963：Python、NumPy及“100 independent test runs” | 作者称基于官方参考实现，100次用于计时 | 可确认实现语言与报告的计时范围 | 程序、命令、环境、随机带、成功/失败分母与日志仍缺；100次计时不等同100次更新解密验证 |
| O13 | p3：constant-size ciphertexts and keys；pp20–22部署适用性论述 | 尺寸相对更新深度保持；实用性还依赖正确性/安全性 | A/B使安全与可靠性前提成为必要核查项 | A/B并未改变所列矩阵尺寸；原始耗时数字本身没有被本轮推翻 |

源文件、PDF与图像均在本目录sources/evidence中。源包README只配置TeX编译入口和编译器。作者/资助说明、文末引用与各公开源包中，未定位作者UE仓库、运行命令或配置文件；这个观察限于实际取得材料和所列检索。

## 4. 640采用程度与性能表的准确含义

**采用程度。** 论文明确把UE测试标为FrodoPKE-640等六种变体，并测试TG和Upd。D=15、q=32768、B=2、m̄=n̄=8及χ640精确表由其引用的2021规范Table3/4（PDF25）对应；2023公开提案AnnexA TablesA.1/A.3（PDF15、印刷11）给相同640核心数值和质量。FI正文和性能表没有逐项重印这组配置。因此“作者明确测试640名称”已核准；“原性能程序逐项采用当前冻结分布与算术”仍需实物对应。

| 操作 | AES640：均值 / 标准差（秒） | SHAKE640：均值 / 标准差（秒） | 表内验证信息 |
|---|---:|---:|---|
| KG | 0.0198 / 0.0006 | 0.0198 / 0.0004 | 耗时 |
| Enc | 0.0218 / 0.0011 | 0.0218 / 0.0002 | 耗时 |
| Dec | 0.0003 / 0.00001 | 0.0002 / 0.00001 | 记为Dec(k_e,ct_e)，未交代ct_e的生成轨迹 |
| TG | 6.3251 / 0.2018 | 6.3118 / 0.0649 | 耗时 |
| Upd | 0.1224 / 0.0057 | 0.1214 / 0.0012 | 耗时 |

Tables1/2同页还列976/1344。正文报告100次独立计时运行，未报告消息比对断言、更新后的解密成功数、失败数、置信界或链深度。最准确判断为**更新后解密验证未报告**；实际是否执行过该检查仍需代码或日志。耗时测量可以在成功和失败输出上发生，因此B直接挑战的是这些配置作为可靠UE实例的解释，作者耗时数据的真实性和准确性继续需要其测量工件评价。

**T及失败预算。** Theorem6.3保留符号T，安全证明也用轮换范围；实现段没有给具体最大更新次数、可接受失败预算或多次更新的失败曲线。100是计时运行次数。对固定640，源充分式对T≥1均不满足；B已经给一步错误率下界。对更多更新深度及其它配置分别保留研究责任。

**作者软件的最小对应材料。** 一份可定位的commit/压缩包和依赖锁、六配置参数导出、运行命令及机器环境；Setup的A生成/复用合同；KeyGen/Enc/TG/Upd各随机流的seed长度、域分离和切片；Ord/Tensor顺序；矩阵整数dtype、溢出与取模位置；Decode平局/打包；筛选/拒绝/重试/失败处理；一条含消息相等断言的Enc→TG→Upd→Dec调用轨迹及100次原始计时日志。每项缺失的影响在VERDICT.software_mapping登记。此处只准备证据清单，外部消息发送为0。

## 5. Ord解释的稳定性与边界

1. **实际列数重载。** 把Ord_t的域写为m̄×t，原逐位规则按t应用，Upd取t=n。它同时满足nD行token、Tensor和Remark6.1，属于v2透明携带的最小类型规范化。
2. **位平面、逐元素或反位序的一致重排。** 对固定置换矩阵Π，令H′=HΠ，(P₁′,Q₁′)=Π^-1(P₁,Q₁)，Tensor′=Π^-1Tensor。则H′P₁′=HP₁、H′Q₁′=HQ₁。原始U/F/G行iid，重排保持联合律；H重量也保持。因此两项结果对这一类一致规范化稳定。
3. **字面m̄×n̄域。** n=640、n̄=8时无法直接应用于C₁；维度检查已经需要一个额外定义。它只给出类型缺项，不能提供另一份同类型、同分布、已正确的640算法。
4. **有符号数字展开、截断列、额外噪声、重试或改变token形状。** 这些行为改变H、抽样或算法。公开仿射恢复在相同Y=HP₁+RP₂关系下仍可分析，但v2的反集中和可靠性数字必须按新模型重新证明。当前源文给的是D位0/1展开；D位代表与标准模代表的一致转换属于第一/二类。

本轮纸面置换论证只建立上述限定等价类，作者实际Ord仍需程序对应。所有影响表随规范化标签引用。

## 6. 两个条件定理的准确评价

**Theorem6.3。** 完整充分式应计B₀+t_maxW<q/2^(B+1)，其中B₀=2ns²+s，W=2n²Ds²+2n²s³+nDs+ns²。s=12、合法维度/编码合同、整数n,D≥1、T≥1且0≤t_max≤T时，W_print−W=3168n²D≥B₀，所以打印的更松充分界若满足前提可吸收初始项。640下B₀=184332、W=3185256960、W_print=22649448960，而q/8=4096。本轮B评价的是充分前提之外的具体高错误行为。CF-1由自己的完整证明承担正确性；其有限例n=128、D=56、T=128也满足源较松充分前提，核账见evidence/SCALAR_SOURCE_ACCOUNTING.json。

**Theorem6.9。** 参数域成员资格、构造攻击和困难性前件逐项区分。CF-1属于FI明写打印域；结果A给原游戏区分事实。若H取精确χ640的丰富同秘密新独立样本困难性，v2附录A已给成熟代数算法使该前件失效。若H限定固定n/3n样本，其真实性、同预算算法以及FI完整模拟归约继续待证；更宽Gaussian也需到精确表/完整UE视图的迁移。当前最强措辞为：构造级来源隐藏结论及命名端点存在已证明障碍，非空困难前件下条件蕴含为假的资格另行核准。论文p20的量子安全/部署论述需要该精确归约和实际实例对应支持。

## 7. 本轮发现的旁支呈现差异

v2附录B的χ976分子序列把±5…±9列为1131、426、138、38、8；2021 Table3和2023 TableA.3原图/文本为1101、396、118、29、6。前者按零点一次、正负各一次总和为65718，分母写65536，无法作为该分母下归一化概率表。旧PARAMETER_CERTIFICATES.json的976 source_cdf为[5638,15915,23689,28571,31116,32217,32613,32731,32760,32766,32767]，从它导出的质量与官方表相符；64重系数文件的总质量也等于所存分母。

此处登记为**INC976：已确认的v2附录转录修正**。本轮未重算976卷积或重审其全部概率证书。结果A、B均只使用χ640，当前两个主结果的输入与裁决保持。v2历史字节保留，后续作者版本应更正该行及其重放说明。

2023引用另有书目精度问题：FI文末[2]登记1–59页，官网所列2023-03-14提案实际21个PDF页；本轮只以明确版本的表核准640参数，不据页数差异替作者判定其所用软件版本。


## 来源与复核记录入口

- **O4**：[FI期刊/arXiv v4](https://fi.episciences.org/17222/pdf)。版本：23-page current publisher PDF byte-identical to arXiv2410.03948v4；公开时间：arXiv v4:2025-12-29; journal online:2026-01-11; PDF volume year:2025。 本地：[arxiv_v4.pdf](../../frozen/crypto_fi_publication_impact_audit/sources/arxiv_v4.pdf)。
- **O1**：[FI历史公开版本](https://arxiv.org/abs/2410.03948v1)。版本：arXiv2410.03948v1；公开时间：2024-10-04。 本地：[arxiv_v1.pdf](../../frozen/crypto_fi_publication_impact_audit/sources/arxiv_v1.pdf)。
- **O2**：[FI历史公开版本](https://arxiv.org/abs/2410.03948v2)。版本：arXiv2410.03948v2；公开时间：2024-10-08。 本地：[arxiv_v2.pdf](../../frozen/crypto_fi_publication_impact_audit/sources/arxiv_v2.pdf)。
- **O3**：[FI历史公开版本](https://arxiv.org/abs/2410.03948v3)。版本：arXiv2410.03948v3；公开时间：2025-08-09。 本地：[arxiv_v3.pdf](../../frozen/crypto_fi_publication_impact_audit/sources/arxiv_v3.pdf)。
- **F21**：[FrodoKEM官方2021规范](https://frodokem.org/files/FrodoKEM-specification-20210604.pdf)。版本：59-page2021-06-04 frozen specification；公开时间：2021-06-04。 本地：[official_frodo_2021.pdf](../../frozen/crypto_fi_research_manuscript_v1/sources/official_frodo_2021.pdf)。
- **F23**：[FrodoKEM官方2023提案](https://frodokem.org/files/FrodoKEM-standard_proposal-20230314.pdf)。版本：21 physical PDF pages; printed AnnexA pp11-12；公开时间：2023-03-14。 本地：[official_frodo_2023.pdf](../../frozen/crypto_fi_publication_impact_audit/sources/official_frodo_2023.pdf)。
- **KLR**：[Klooß–Lehmann–Rupp2019](https://orbilu.uni.lu/bitstream/10993/50226/1/Publikation_UE_Eurocrypt_2019.pdf)。版本：71-page institution author version；公开时间：2019 EUROCRYPT; exact first-preprint day not newly verified。 本地：[KLR2019.pdf](../../frozen/crypto_fi_research_manuscript_v1/sources/KLR2019.pdf)。
- **N**：[Nishimaki前驱](https://eprint.iacr.org/2021/221)。版本：ePrint2021/221 landing page; exact extended PDF unavailable；公开时间：received2021-03-02; latest revision2024-04-19; note dated2024-04-18。
- **LC**：[Lattice Codes for Lattice-Based PKE](https://github.com/shx-lyu/lattice-codes-for-pke/blob/e577f664353a6ea8b679815c314a8e3f04264657/README.md)。版本：Pinned README commit e577f664353a6ea8b679815c314a8e3f04264657；公开时间：README modified date returned:2023-07-16; exact paper initial date not newly verified。
- **UHE**：[Liu等CSS2022混合UE](https://link.springer.com/chapter/10.1007/978-3-031-18067-5_6)。版本：Springer publisher abstract; pp71-85; DOI10.1007/978-3-031-18067-5_6；公开时间：2022-09-29。
- **GH**：[官方Frodo参考仓库](https://github.com/microsoft/PQCrypto-LWEKE)。版本：microsoft/PQCrypto-LWEKE directory listing; FrodoKEM tree4f337a3ee6945cc8e9949a8ddba34f51d88325d9；公开时间：current default branch viewed2026-11-10; author UE commit unspecified。

每项具体支持位置、获取时间、阅读等级及SHA256见 [SOURCE_LEDGER.json](../../frozen/crypto_fi_publication_impact_audit/evidence/SOURCE_LEDGER.json)；实际检索输入与原始返回见 [SEARCH_LEDGER.json](../../frozen/crypto_fi_publication_impact_audit/evidence/SEARCH_LEDGER.json)。
