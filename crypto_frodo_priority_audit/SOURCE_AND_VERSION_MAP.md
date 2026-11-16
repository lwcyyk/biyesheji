# Frodo-FI 优先权与参数来源：冻结记录

日期：2026-11-06（Asia/Shanghai）。本轮身份为 **DIRECTED_LITERATURE_AND_PARAMETER_SOURCE_AUDIT**。当前会话已参与上一阶段数学复核，继承其结论；上一阶段 `INDEPENDENT_AI_REVIEW` 是当时的会话身份记录，原文件保持冻结。本轮新增推导 N1 在参数文件单列。执行为单一 AI，人工同行复核和证明助手复核均为0。

主判断：**NEW_OBJECT_CRYPTANALYSIS_WITHIN_CHECKED_SOURCES**。这一判断限定于下列实际检索和核读范围。当前证据支持新对象上的安全分析，全球首次与完整优先权认证保留开放状态。

## 1. 输入冻结与对象

已读取上一阶段五份交付及参数算术、来源记录、PDF 原图证据，重读攻击稿第I部分，并读取 SELECT 的 `CONTRIBUTION_VERDICT.md`。七个输入文件的绝对路径、字节数和 SHA-256 位于 `sources/input_manifest.json`。复用的 PDF、官方2021/2023规范及旧 evidence 以旧来源记录中的哈希引用。

SELECT 已定位为已有群构造的有限证明扩展和规格化，可作为辅助贡献；本轮 Frodo 结果独立评价。SELECT 文件中“Frodo 独立数学复核待进行”描述的是其定稿时状态，本轮沿用后来数学复核的结果。

冻结攻击：公开 Δ=((P1,Q1),(P2,Q2))、普通父 C、挑战第一块 Y；q=2^D，P2 为 n×n，H=Ord_n(C1)，更新 Y=HP1+RP2，R∈S_q^{m̄×n}。P2 奇异时公平猜测；可逆时检查 (Y−HP1)P2^−1 的支持。Ord 的列数参数化、隐藏挑战带、固定合法查询及假设范围沿用数学审阅。

## 2. C1—C9 主张登记

| ID | 对象、量词与版本 | 原文／已有证据 | 本轮裁定与待证内容 |
|---|---|---|---|
| C1 | v3/v4 原 rand-ind-eu-cpa；存在一个固定 PPT 攻击 | v4 pp9–11；Enc_0(M),Next,Corr(token,1),Chall(M,parent)，K*=∅ | VERIFIED；同构造公开先例在已检索来源中未定位；v1/v2 游戏的排版缺口另列 |
| C2 | 每个合法父和诚实 token 的第一块 | v1/v2 p10，v3/v4 p14：Y=HP1+RP2 | VERIFIED；四版均存在；公开小支撑像成员测试为核心应用 |
| C3 | 每个可逆 P2，模2^D精确恢复 R | 同上，加环上矩阵求逆恒等式 | VERIFIED；属于经典线性代数工具的直接应用 |
| C4 | 固定串、无失败理想采样；全部真实分布 | 审阅概率表：成功率=1/2+(α−β_real)/2 | VERIFIED；通用事件分解，FI 优势为 bias 的2倍 |
| C5 | 指定 nf-DLWE 族及实际运行预算；共享 A | 审阅 LWE audit B–E；Frodo2021 Definitions 2.7–2.9 | VERIFIED（条件归约）；n 行 P2 边缘混合、m̄ 行 fresh 联合投影混合；任意辅助信息或完整 fresh 第二块的替换另有义务 |
| C6 | ε_P、ε_ct 可忽略且 θ 与1保持距离的参数族 | bias≥[p_n(1−θ)−ε_P−ε_ct]/2，截断于0 | VERIFIED（有条件）；有限性能配置的 ε 仍保留符号 |
| C7 | 2021表640/976，F2 各项独立且与 A,U2 独立；固定任意 A | 2021 pp24–25；本轮 CDF 有理数核对 | VERIFIED；α=p_n 精确，消去该子域 ε_P；1344 扩展见新增 N1 |
| C8 | 冻结构造的来源隐藏性质 | v3/v4 Theorem6.9，v1/v2 §4.1 的相应声明 | COUNTEREXAMPLE（有条件）；普通 FrodoPKE 消息安全与 LWE 困难性保持独立作用域 |
| C9 | FI p21 六组实际计时配置 | 100次计时、Python/NumPy、引用官方实现；源包及公开仓库检索 | SOURCE_UNRESOLVED；缺少作者基准代码／commit和运行配置，标准参数无法代替这些证据 |

## 3. 四个公开版本逐式比较

| 版本 | 官方时间；页数 | SHA-256 | 实际核读／结果 |
|---|---|---|---|
| [v1](https://arxiv.org/abs/2410.03948v1) | 2024-10-04；17页 | `f29c48ca6737164456094d78fcf7d13a1243dab97e514592520bbe825e95e5cb` | pp4–5游戏、pp8–10参数/Enc/Ord/TG/Upd；p4、p10原图。p10有完整待审关系 |
| [v2](https://arxiv.org/abs/2410.03948v2) | 2024-10-08；17页 | `5fc24633e6f8320a0c495795fa177ecfb9f7a41913ed0c4c06789affddd79420` | pp4–5游戏、pp8–12参数/算法/噪声；p4、p10原图。待审关系保留 |
| [v3](https://arxiv.org/abs/2410.03948v3) | 2025-08-09；23页 | `24e6c3d193cadef1f4fd43831a5e92f0601a522d8cfad8a29c3097fa7844dc12` | pp9–20与v4定向比较，p14原图；p10、12、14、15、17、18归一化文本完全相同，其余目标页主要为引用号及分页差别 |
| [v4](https://arxiv.org/abs/2410.03948v4) | 2025-12-29；23页 | `bc48416b8b88c989ecf98e2d466d10b80d13fd72d88890d905bc3b991ca3d0d4` | 复用已核准全文及原图；[出版版](https://fi.episciences.org/17222)字节相同，出版日期2026-01-11 |

新增版本证据：v1/v2 p4 的 O.Next 第1行印为 `qid←qid+1`，其后使用 e、k_(e−1)；e 缺少递增。O.Upd 的资格检查也使用 `qid−1`。按字面执行，这两版游戏无法直接承载此前最小串。因此：**四版算法公式受同一支撑分析影响；v3/v4 原游戏的合法反例已核准；v1/v2 的游戏级结论需显式采用 epoch 递增修正。** 这项修正与原图观察分别登记，避免把 v4 游戏直接回填到旧版。

v1/v2 的 Ord 形式域同样写 n̄ 列，逐位定义及正确性恒等式支持此前的列数参数化。其χ均为有限支持表分布，P2 的形状与 R 的维度保持相同。未发现四版中的目标 Upd 添加逐次独立加性噪声。

v3/v4定向差分位于 `sources/v3_v4_target_page_comparison.json`。三份新 PDF 均已通过结构预检；预检只覆盖文件结构。全文取得与上述定向核读范围分别记录。

## 4. 补充材料、实现与勘误

取得 [arXiv v4源包](https://arxiv.org/src/2410.03948v4)，37734字节，SHA-256 `eb20e59259f9f848405bf8e5212f81e9417cc49d347f2958ad0a6c4e174a3b9a`。成员为 `00_my_def.tex`、`00README.json`、`articlev08.bbl`、`articlev08.tex`、`fundam.bst`、`fundam.cls`。包内包含论文排版材料；Python 基准程序与参数配置文件数量为0。主 TeX 的 implementation、seed、CDF、GitHub 等关键词也已检查。这个结论只描述该公开源包。

出版页、arXiv版本记录、精确题名／作者／编号检索中，未定位到针对该支撑问题的官方勘误。公开仓库查询 `FrodoPKE` 返回空列表；`updatable Frodo` 返回的库与目标论文无关。索引空结果保留其查询范围含义，无法证明实现从未公开。

参数方面已取得具有决定作用的公开纠错链：

- [官方 issue #35](https://github.com/microsoft/PQCrypto-LWEKE/issues/35)，2024-11-27提出1344 CDF缺项；[Patrick Longa 的回复](https://github.com/microsoft/PQCrypto-LWEKE/issues/35#issuecomment-2504969837)明确指出表A.4排版错误，正确 Tχ(5)=32765、Tχ(6)=32767，并确认最后一个CDF元素按设计无需比较。
- [2024-12-05规范](https://frodokem.org/files/FrodoKEM_standard_proposal_20241205.pdf)与[2025-09-29规范](https://frodokem.org/files/FrodoKEM_standard_proposal_20250929.pdf)，均在PDF p16／印刷p12表A.4给出修正值。两份原图均已检查。
- 官方仓库固定 commit `e1edeb3af1fae0d5727683bd2f5465280ec2437a`（2026-09-15），`FrodoKEM/src/frodo1344.c`与`noise.c`一致。此次仅保存、阅读原有代码，执行次数为0。

该纠错链收口官方规范的1344支持疑点，同时保留 FI 作者实际使用哪份程序的来源缺项。

## 5. 技术近邻来源及读取层级

| ID | 来源 | 取得与实际核读 | 对优先权的作用 |
|---|---|---|---|
| FI | 四版目标论文及TeX源包 | 本地PDF；范围见上表 | 固定对象及声明 |
| F21/F23 | 官方2021规范／2023提案 | 复用已冻结PDF；参数表、采样、nf-DLWE定义 | 标准参数和既有概率工具 |
| F24/F25 | 官方2024／2025修订 | 完整PDF取得，p16 CDF原图定向核读；其他章节未全文复核 | 公开纠错证据 |
| FA23 | [2023更新附录](https://frodokem.org/files/FrodoKEM-annex-20230418.pdf) | 12页PDF取得；pp3–4说明定向核读 | seedSE加长及盐属于KEM变体变化，不能自动当作UE采样规格 |
| CP | Kluczniak, *Circuit Privacy for FHEW/TFHE-Style Fully Homomorphic Encryption in Practice*, DOI10.62056/av11c3w9p | 出版PDF通过网页工具可读，共40页；pp1–3、8、18文本定向阅读；本地下载403，复杂公式的原图未得到可保存核准件 | 与公开辅助信息下重随机化、噪声淹没有关；限定为所读结论，未把全篇定理认证 |
| AG26 | [Olejnik–Naskrecki，arXiv:2608.21986v1](https://arxiv.org/abs/2608.21986v1) | 33页PDF取得；§4.5 pp15–16及参考文献原文核读，pp15–16原图 | Hollow-LWE攻击，接口及目标与FI不同；排除同对象覆盖 |
| N22/N24 | [Nishimaki PKC2022](https://doi.org/10.1007/978-3-030-97131-1_7)；[ePrint2021/221](https://eprint.iacr.org/2021/221) | 出版题录、摘要、作者页及修订记录已读；两条公开PDF路线403，全文未取得 | FI Lemma6.8最直接前驱；其§5/Lemma5.7的完整映射保留SOURCE_UNRESOLVED |
| KLR19 | [(R)CCA Secure Updatable Encryption with Integrity Protection](https://doi.org/10.1007/978-3-030-17653-2_3) | KIT/机构题录及检索返回的定义11、附录B.2段落；全文下载受403/证书/连接失败阻碍 | 公共更新一致性有技术近邻；片段级候选，覆盖结论保持条件式 |

Nishimaki 的ePrint页面记2024-04-19为最近修订，并注明撤回 obfuscation-based construction。这项记录指向其另一构造，不能扩张成对LWE构造或FI的勘误。未取得的修订正文保留来源缺项。

## 6. 检索账本与局限

全部检索日期为2026-11-06，来源为连接的网页搜索工具；每个 `sources/Q*.json` 保存完整查询和实际返回。检索源包、GitHub、官方页面的额外读取另存receipt。查询关键词和筛选结果如下：

| ID | 查询 | 实际结果与处置 |
|---|---|---|
| Q1 | 精确题名 + attack cryptanalysis | 目标论文、出版页及二手摘要；未定位同对象攻击 |
| Q2 | 2410.03948 correction erratum | 目标条目和索引；无已定位正式勘误 |
| Q3 | updatable encryption Frodo attack | 目标论文、普通Frodo侧信道等异对象；后者排除 |
| Q4 | fixed token updatable encryption security attack | KLR19、BDGJ20、扩展UE等候选 |
| Q5 | updatable encryption cryptanalysis lattice | 发现AG26；优先核读并排除同对象覆盖 |
| Q6 | rerandomization small support ciphertext | 大量统计学同词误命中；选CP相关近邻 |
| Q7 | key switching circuit privacy distinguish | CP出版全文及其他FHE材料 |
| Q8 | The Direction of Updatable Encryption Does Matter | Nishimaki题录及ePrint编号 |
| Q9 | Frodo Jurkiewicz github | 目标论文及无关词项；没有已定位实现 |
| Q10 | 精确题名并排除部分摘要站点 | 出版页、题录与作者索引 |
| Q11 | noise flooding auxiliary information | 可撤销密码与辅助信息LWE等候选；未列作同一攻击 |
| Q12 | affine support encryption distinguisher | 大量AFFiNE软件／经典仿射密码误命中；无覆盖证据 |
| Q13 | Frodo support updatable | 目标文本及无关Frodo词项 |
| Q14 | Nishimaki完整题名 + pdf | 公共IACR路线及作者页；PDF获取失败单列 |
| Q15 | Nishimaki 2021/221 pdf | 题录、引用论文；全文缺项持续 |
| Q16 | (R)CCA Secure Updatable Encryption pdf | KLR的KIT/ORBilu/出版记录；全文获取失败单列 |
| Q17 | 精确题名 + citations | 目标条目及引用展示页；未得到可核读的后续攻击清单 |
| Q18 | lattice rerandomization support distinguisher | ABE、mix-net等异目标；无直接FI覆盖证据 |
| Q19 | 2410.03948 attack，排除摘要站点 | 索引明确返回空结果 |
| Q20 | updatable encryption small support | 目标原文和综述片段 |
| Q21 | Jurkiewicz Prabucka cryptanalysis | 期刊目录、作者机构页；无已定位同对象攻击 |
| Q22 | updatable encryption fresh distinguisher | FMM21、KLR19、其他UE；仅登记实际取得层级 |

后续引用核查的结果是“在这些渠道中未定位同对象攻击全文”。搜索片段里的零引用、第三方自动摘要、其它论文的被引计数均未用于宣布全球首次。最关键的近邻全文缺项为 **Nishimaki ePrint2021/221 最近公开修订的§5及Lemma5.7**；它决定能否闭合FI自称继承的具体随机化／辅助信息证明。实际基准适用性另由作者代码与配置证据决定，两项作用域在裁决中分开。

本轮候选协议实现、大参数密码实验、作者联系、邮件、原生AS/RP请求均为0。
