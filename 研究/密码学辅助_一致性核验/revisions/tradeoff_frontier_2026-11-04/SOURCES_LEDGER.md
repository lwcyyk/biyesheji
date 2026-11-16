# 来源登记与完整性核对

核验日为2026-11-04。本文件在初始来源检查后建立，现补齐定向核读信息。

## 实际到件情况

用户指定的 sources 子目录初次扫描时缺失，实际文件数为0。五份新提供PDF位于 D:\毕业设计\研究。七份缺少的预期论文通过脚本HTTP取得，保存于本目录的http子目录。sources保留初始状态。预期12篇论文现均取得全文。三份预期被引页面存档仍缺失，本轮另取得三组Semantic Scholar被引API快照，二者分别登记。

12篇预期论文中，Beimel为作者稿，HLPS为已发表期刊版，qPolymatroid为v2。源文件哈希用于固定本轮判断版本。PDF页码为物理页码，印刷页码另行注明。全部15份PDF结构预检PASS，预检范围仅为页面树和读取结构。

## 逐份登记

| 文件名与实际路径 | SHA-256 | 题名、页数、版本 | 对应查新编号 | 首要核读章节 |
|---|---|---|---|---|
| `D:\毕业设计\研究\密码学辅助_一致性核验\revisions\tradeoff_frontier_2026-11-04\http\D10.pdf` | `bd343d63bf4db9f86745be721a9edfd19443bd5c5e05ee6c0788e9b85d859e53` | Communication Efficient Secure Linear Algebra，20页。2006，TCC LNCS 3876，印刷522–541 | N01 / NissimWeinreb2006 | §2–4，PDF4–10、13，附录A PDF18 |
| `D:\毕业设计\研究\1-1-29.pdf` | `f10625a2b8a2d1e99577c9e3ce0df4c920c9463c6e533d13bdc3da286b8ec233` | Secure Multi-Party Linear Algebra with Perfect Correctness，25页。2024，CiC 1(1)，25页 | N02 / MV24(CiC) | §2–5、附录9，PDF4–5、11–14、18、25 |
| `D:\毕业设计\研究\密码学辅助_一致性核验\revisions\tradeoff_frontier_2026-11-04\http\D02.pdf` | `274a0c2d59494844cc6fe1e3cfb53f58de0801fbf11289f8c4cd5be0236994f1` | Perfect Constant-Round Secure Computation via Perfect Randomizing Polynomials，13页。2002，ICALP，印刷244–256 | N03 / IK02(ICALP) | §2–4，PDF4–11，重点Lemma2–4及Theorem1 |
| `D:\毕业设计\研究\密码学辅助_一致性核验\revisions\tradeoff_frontier_2026-11-04\http\D03.pdf` | `36907bebf42488248ba68c6b223cd5154aec5d6a056483db50b5cd48362a9b57` | Secret-Sharing Schemes: A Survey，36页。2011，作者36页稿，元数据2011-02-28 | N04 / BeimelSurvey2011 | Definition3、§5.1–5.4及§7，PDF5、19–22、31，参考34–35 |
| `D:\毕业设计\研究\2023-1012.pdf` | `f55e6c597ec1dfdc3c9809409f9f25b4b4db91b3201a4c13f6df2ea939a3bb88` | Arithmetic Sketching，52页。2023，ePrint全文52页，文件生成2023-07-24 | N05 / ArithmeticSketching_ePrint1012 | Definitions1/2/17，Construction21，Theorem22，Corollary23，参考33/34，PDF10、20–26、34–35 |
| `D:\毕业设计\研究\2601.07567v2.pdf` | `bf730655d770e02442cc6b61109843aa842f457bcd14f58986c0dbb18935eaa5` | A q-Polymatroid Framework for Information Leakage in Secure Linear Network Coding，32页。arXiv2601.07567v2，2026-10-08 | N06 / qPolymatroid2601.07567 | §II–III，PDF7–11，参考30–32 |
| `D:\毕业设计\研究\密码学辅助_一致性核验\revisions\tradeoff_frontier_2026-11-04\http\D04.pdf` | `481a064dd80d2fe73aeadc56ccf1d9942b797c901279948a0fa2e19b52750d3f` | Global optimality under amenable symmetry constraints，45页。arXiv2402.07613v2，2024-07-19 | N07 / Orbanz2402.07613 | §1式2、Theorem6/10、Proposition11，PDF2、8、10–12 |
| `D:\毕业设计\研究\2018-707.pdf` | `4bf3a8166d94541f5d2cf55bd9136b7402765f3850fadaa683c546c951077a61` | Function Secret Sharing: Improvements and Extensions，49页。2018-07-24 full version of CCS2016，49页 | N08 / FSS2018_707 | Definitions2.1–2.3，§3.1、§4.2–4.3，PDF5–9、28 |
| `D:\毕业设计\研究\2026-514.pdf` | `2ea0a05e0580a73e280142294243ab39148898613e2a47745f2d1622d3f62830` | Secure Multi-party Matrix Invertibility Testing over Small Finite Fields，27页。2026，CiC3(2)期刊版，27页，2026-07-20文件 | N09 / HLPS26_514 | §2.2、§4.4、§5，PDF6–7、19–22 |
| `D:\毕业设计\研究\密码学辅助_一致性核验\revisions\tradeoff_frontier_2026-11-04\http\D15.pdf` | `f1d60d77a90aeee903ababb5da2e605f44973c56cb8a48be6a953d35f465d9e9` | Fast Secure Computations on Shared Polynomials and Applications to Private Set Operations，24页。2024，LIPIcs304，article11，24页 | N10 / GLOV24_ITC | §4.1–4.2，Theorems9/10及附录证明，PDF17–18、24 |
| `D:\毕业设计\研究\密码学辅助_一致性核验\revisions\tradeoff_frontier_2026-11-04\http\D11.pdf` | `9601561b2678d9e26e130edea943e03397c7c162810cbe1619f7c242538487e6` | Secure Distributed Linear Algebra in a Constant Number of Rounds，18页。2001，CRYPTO，印刷119–136 | N11 / CD01 | §2–3及ProtocolΠ0，PDF2、4、8 |
| `D:\毕业设计\研究\密码学辅助_一致性核验\revisions\tradeoff_frontier_2026-11-04\http\D05.pdf` | `9bb50b7b22895d37899e6b71344242f4ed6bcf698936add1785c1d167196496c` | On the Relationship between Statistical Zero-Knowledge and Statistical Randomized Encodings，24页。2015，TR15-186，24页 | N12 / ECCC2015-186 | §2、§4–5.1，PDF5–6、9–10 |
| `D:\毕业设计\研究\3-3-4.pdf` | `8688a088693f77ca84525520081357cd5d838ffdb04a662c01d67a4c52668f37` | Constant-Round Secure Distributed Decoding and HQC Threshold Decryption，43页。2026，CiC3(3)，43页 | N13 / 附加Giorgi2026 | §2.2，§4.2，§6.2，沿用并核对原文位置 |
| `D:\毕业设计\研究\Randomizing_polynomials_A_new_representation_with_applications_to_round-efficient_secure_computation.pdf` | `963e0063ed3ff75206db802acefc1da010e77bc1e637c421ab16c04acf835791` | Randomizing Polynomials: A New Representation with Applications to Round-Efficient Secure Computation，11页。2000，FOCS extended abstract，11页 | N14 / 附加IK00 | Lemma3.3，印刷298–299，沿用前轮全文核读并重核 |
| `D:\毕业设计\研究\密码学辅助_一致性核验\revisions\tradeoff_frontier_2026-11-04\http\D14.pdf` | `9b7d28f25460c2b86dbcb7a05c20c160f8ea5a00e2cdaae62899f74cbad04fe8` | Common Information, Matroid Representation, and Secret Sharing for Matroid Ports，24页。arXiv2002.08108v2，页首2022-03-30，正文日期03-31 | N15 / 补检matroid ports | Definitions2.3/2.4，LP3.8/3.9，Theorem5.1，PDF6–9、19 |
| `D:\毕业设计\研究\密码学辅助_一致性核验\revisions\novelty_search_2026-11-03_r2\sources\lowrank2026.html` | `d0f46914bcc01a3918eac8408bd4dc95c7a0c5991a22cab81cd0f63274643565` | Low-Rank Masking for Single-Server Matrix Multiplication，HTML无固定页。arXiv2609.18876v1，2026-09-16，历史缓存HTML | N16 / 附加P04 | §2.1–2.5，Theorems4/5及§3证明 |

## 版本差异与完整性限制

- HLPS旧清单题名为 Secure Matrix Invertibility Testing over Fields of Small Order or Characteristics。实际文件题名、作者与期刊DOI按N09首页登记，旧题名对应ePrint版本仍待单独比对。
- qPolymatroid旧定位中的“命题17、定理18”发生变化。v2的17为Remark17，18为Proposition18，泄漏主公式现位于Theorem19。
- NW06的PDF元数据题名为整本会议论文集，本文身份用首页作者、题名、页码及DOI核对。
- Beimel作者稿的36页与书目所列印刷11–46相符。逐字等同期刊排版稿的核验尚待出版者版本。
- IK02部分证明在会议版明确省略。MAPPING_UPDATE仅使用实际出现的证明与陈述。
- pypdf初次批量提取时发出重复/Group字典键警告，单文件归属未在该次日志中绑定。结构预检PASS，重要公式以正文位置和原PDF共同绑定。
- P04使用历史HTML缓存，本轮未独立重取其在线版本。其优先权与发表状态按缓存版本限定。

## 原文入口

- N01，Communication Efficient Secure Linear Algebra。[原文或出版记录](https://doi.org/10.1007/11681878_27)
- N02，Secure Multi-Party Linear Algebra with Perfect Correctness。[原文或出版记录](https://doi.org/10.62056/avzojbkrz)
- N03，Perfect Constant-Round Secure Computation via Perfect Randomizing Polynomials。[原文或出版记录](https://www.cs.columbia.edu/~tal/6261/SP20/reading/IKicalp02.pdf)
- N04，Secret-Sharing Schemes: A Survey。[原文或出版记录](https://www.cs.bgu.ac.il/~beimel/Papers/Survey.pdf)
- N05，Arithmetic Sketching。[原文或出版记录](https://eprint.iacr.org/2023/1012)
- N06，A q-Polymatroid Framework for Information Leakage in Secure Linear Network Coding。[原文或出版记录](https://arxiv.org/abs/2601.07567v2)
- N07，Global optimality under amenable symmetry constraints。[原文或出版记录](https://arxiv.org/abs/2402.07613v2)
- N08，Function Secret Sharing: Improvements and Extensions。[原文或出版记录](https://eprint.iacr.org/2018/707)
- N09，Secure Multi-party Matrix Invertibility Testing over Small Finite Fields。[原文或出版记录](https://doi.org/10.62056/av11fh888)
- N10，Fast Secure Computations on Shared Polynomials and Applications to Private Set Operations。[原文或出版记录](https://doi.org/10.4230/LIPIcs.ITC.2024.11)
- N11，Secure Distributed Linear Algebra in a Constant Number of Rounds。[原文或出版记录](https://doi.org/10.1007/3-540-44647-8_7)
- N12，On the Relationship between Statistical Zero-Knowledge and Statistical Randomized Encodings。[原文或出版记录](https://eccc.weizmann.ac.il/report/2015/186/)
- N13，Constant-Round Secure Distributed Decoding and HQC Threshold Decryption。[原文或出版记录](https://doi.org/10.62056/ay4fvu7sf)
- N14，Randomizing Polynomials: A New Representation with Applications to Round-Efficient Secure Computation。[原文或出版记录](https://doi.org/10.1109/SFCS.2000.892118)
- N15，Common Information, Matroid Representation, and Secret Sharing for Matroid Ports。[原文或出版记录](https://arxiv.org/abs/2002.08108v2)
- N16，Low-Rank Masking for Single-Server Matrix Multiplication。[原文或出版记录](https://arxiv.org/html/2609.18876v1)

## 获取与复核

HTTP_REQUESTS.jsonl记录全部脚本获取尝试、起止时间、HTTP状态、错误、返回字节与哈希。http内保留原始响应。SOURCES.json为可机读逐份登记。inspect_*_inventory.json与readings/*.preflight.json保存页数及结构预检结果。请求失败与无搜索结果分别记录。

## 三份预期被引存档

| 预期存档 | 到件状态 | 本轮替代证据 | 范围 |
|---|---|---|---|
| Arithmetic Sketching被引页 | 缺失 | F01.body，10条 | Semantic Scholar该DOI当次接口快照 |
| IK00被引页 | 缺失 | F04.body，300条 | 同上，无next字段 |
| Giorgi2026被引页 | 缺失 | F03.body，0条 | 接口当次无记录，全球被引数仍未知 |

以上三个API集合的内容、逐条书目和完整性限制见SEARCH_CLOSURE.md。
