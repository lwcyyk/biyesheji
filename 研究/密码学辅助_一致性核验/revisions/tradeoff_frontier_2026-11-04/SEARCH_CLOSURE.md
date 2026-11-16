# S1–S5查新判定与检索闭合记录

2026-11-04。判定范围为本轮取得全文并核读的章节。机器生成部分仅整理HTTP响应、书目和计数，命题判断来自MAPPING_UPDATE的人工分析。

## 1. 逐项判定

| 主张 | 本轮判定 | 已有部分与剩余差异 |
|---|---|---|
| S1 精确δ* | 未发现覆盖，限已核读分母 | NW06/IK02/Arithmetic Sketching涵盖矩阵盲化与随机编码。共享2×3、硬无抹除、全≤3、任意幅值、TV minimax的完整公式仍待优先权闭合 |
| S2 唯一核边缘 | 未发现完整覆盖，对称化子项覆盖 | Orbanz有限群平均及IK02轨道不变性归入已有工具。h/l跨轨道权重唯一、秩2必然性与严格互补仍是单独候选 |
| S3 表示敏感性 | 未发现精确δ*分离覆盖 | 拟阵多表示已有经典理论。r5中同一U₍₃,ₙ₎对应具体TV极值严格不同这一组合，在已读章节未见直接归约 |
| S4 全局极值族 | 未发现完整覆盖，几何构造子项覆盖 | 经典二次曲线加核点、有限域零点界与域嵌入分别归属已有工具。T端点到δ*端点的结合继续依赖S1。扩展纯几何关键词检索受阻，优先权仍有明显缺口 |
| S5 低故障完美幅值隐私/三故障最坏 | 覆盖，保留为构造推论 | 均匀frame轨道不变性及TV投影收缩给出结论。δ*具体数值归S1 |

“未发现覆盖”表示在明确分母内取得的负检索结果，首次证明和强独立原创仍待确认。S1–S4的总体优先权状态均为UNRESOLVED。S4还保留纯有限几何原始文献缺口。

## 2. 实际检索分母

- 12篇指定论文均取得全文。另核读或复核IK00、Giorgi2026、Common Information…与P04，合计16篇，包含15份PDF和1份历史HTML。核读范围逐份列于MAPPING_UPDATE。
- Q01–Q15每组均有arXiv有效返回，分页和零结果分别登记。另有A01组合检索及AQ12N术语补检。DBLP的15次搜索均未取得有效JSON结果。
- 三组Semantic Scholar前向集合共有310条返回记录。它们为索引快照，正文覆盖判断仅使用已经取得并定位的论文。三份预期原始被引网页存档仍缺失。
- Arithmetic Sketching参考表共50项，已读取所在PDF33–35页的书目文本。[33]/[34]已闭合到IK00/IK02正文。其他书目仅在已读原文条目范围内进入覆盖证据。
- Giorgi2026参考表55项沿用历史登记。此次补齐其中MV24、HLPS26、GLOV24及CD01正文。全部55篇原始文献的全文核读仍待完成。

机器统计如下。

```json
{
  "request_count": 59,
  "expected_papers_fulltext": 12,
  "fulltext_targeted_read_papers": 16,
  "pdf_papers": 15,
  "html_papers": 1,
  "forward_sets": 3,
  "forward_records": 310,
  "q_matrix_valid_result_groups": 15,
  "arxiv_successful_response_pages": 18,
  "arxiv_metadata_unique": 636,
  "forward_unique": 310
}
```

检索库的分词可能扩展短语。AQ12实际返回大量随机多项式零点论文，故额外执行randomized encoding补检。arXiv对Arithmetic Sketching和Giorgi期刊论文的题名查询未定位到目标，正文通过其他入口取得。零结果只反映该检索式和该索引。

## 3. Q01–Q15执行矩阵

| 编号 | DBLP原始关键词 | DBLP执行 | arXiv实际检索式 | 取得记录/接口总数 |
|---|---|---|---|---|
| Q01 | optimal simulation error masking statistical distance | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | `all:"optimal simulation error" OR (all:"statistical distance" AND all:masking)` | 2/2 |
| Q02 | statistical distance secret sharing masking | HTTP 202，响应为HTML验证页 | `all:"statistical distance" AND all:"secret sharing"` | 2/2 |
| Q03 | private sparse recovery lower bound | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | `all:"private sparse recovery" OR (all:"sparse recovery" AND all:privacy)` | 7/7 |
| Q04 | sketch privacy statistical | HTTP 202，响应为HTML验证页 | `all:sketch AND all:privacy AND all:statistical` | 18/18 |
| Q05 | matroid port entropy | HTTP 202，响应为HTML验证页 | `all:"matroid port" OR (all:matroid AND all:entropy)` | 34/34 |
| Q06 | ideal secret sharing matroid | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | `all:"ideal secret sharing" AND all:matroid` | 3/3 |
| Q07 | projective arc finite geometry leakage | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | `all:"projective arc" AND (all:leakage OR all:privacy)` | 0/0 |
| Q08 | secant finite geometry privacy | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | `all:secant AND all:"finite geometry" AND all:privacy` | 0/0 |
| Q09 | oblivious linear algebra matrix blinding | HTTP Error 429: Too Many Requests | `all:"oblivious linear algebra" OR all:"matrix blinding"` | 1/1 |
| Q10 | matrix blinding leaks only rank | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | `all:"matrix blinding" AND all:rank` | 1/1 |
| Q11 | Arithmetic Sketching | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | `all:"Arithmetic Sketching"` | 1/1 |
| Q12 | Randomizing Polynomials statistical randomized encodings | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | `all:"randomizing polynomials" OR all:"statistical randomized encodings"` | 541/541 |
| Q13 | Constant-Round Secure Distributed Decoding and HQC Threshold Decryption | HTTP Error 429: Too Many Requests | `all:"Constant-Round Secure Distributed Decoding"` | 0/0 |
| Q14 | fractional triangle decomposition complete graph edge weights | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | `all:"fractional triangle decomposition"` | 10/10 |
| Q15 | inclusion matrix edges triangles inverse | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | `all:"inclusion matrix" AND (all:triangle OR all:inverse)` | 1/1 |

### 补充检索

| ID | 检索式 | 记录/总数 |
|---|---|---|
| A01 | `arxiv API access and Q05 Q11 broad` | 7/7 |
| AQ12N | `all:"randomized encoding" AND (all:statistical OR all:privacy)` | 18/18 |

AQ07N/AQ07NR尝试移除privacy关键词，仅查arc、secant/concurrent与finite/projective，两次均遇到TLS传输失败。该纯几何查询待PI或后续会话补取。

## 4. 前向被引集合

| 集合 | 接口记录数 | 分页 | 核验范围 |
|---|---|---|---|
| F01 Arithmetic Sketching | 10 | next=缺省 | 当前DOI对应索引快照，跨版本合并与全球完整性未核实 |
| F04 IK00 | 300 | next=缺省 | 当前DOI对应索引快照，跨版本合并与全球完整性未核实 |
| F03 Giorgi2026 | 0 | next=缺省 | 当前DOI对应索引快照，跨版本合并与全球完整性未核实 |

F03的0条仅表示该期刊DOI当次接口无被引记录。ePrint版本可能另建记录，全球被引数仍未知。F04请求上限1000，返回300条且无next字段，按接口返回已结束处理。数据库遗漏、重复与版本拆分仍保留限制。

下表完整保留API返回题名。所有“书目级”行均未用作覆盖或未覆盖的原文证据。

| 来源集合 | 年份 | 题名 | 标识 | 阅读级别 |
|---|---|---|---|---|
| F01 | 2026 | Characterization and Optimization of Ideal Secret Sharing Schemes via Algebraic Matroid Theory | 10.31185/bsj.vol22.iss43.1603 | 书目级，正文判断另见N01–N16 |
| F01 | 2025 | Improved Constructions for Distributed Multi-Point Functions | 10.1109/SP61157.2025.00044 | 书目级，正文判断另见N01–N16 |
| F01 | 2025 | PREAMBLE: Private and Efficient Aggregation via Block Sparse Vectors | 10.52202/085713-0680 | 书目级，正文判断另见N01–N16 |
| F01 | 2024 | PLASMA: Private, Lightweight Aggregated Statistics against Malicious Adversaries | 10.56553/popets-2024-0064 | 书目级，正文判断另见N01–N16 |
| F01 | 2024 | Private Analytics via Streaming, Sketching, and Silently Verifiable Proofs | 10.1109/SP54263.2024.00245 | 书目级，正文判断另见N01–N16 |
| F01 | 2023 | Samplable Anonymous Aggregation for Private Federated Data Analysis | 10.1145/3658644.3690224 | 书目级，正文判断另见N01–N16 |
| F01 | 2026 | Nudge: A Private Recommendations Engine | d1c64a001a1db96a1ab9e4a54cd13f45bda2b643 | 书目级，正文判断另见N01–N16 |
| F01 | 2025 | Fraud Mitigation in Privacy-Preserving Attribution | 343cd52b28a289dcd4a72a5b0846b991afe55dc5 | 书目级，正文判断另见N01–N16 |
| F01 | 2025 | Malicious Homomorphic Secret Sharing with Applications to DV-NIZK and More | 10.1007/978-3-032-26740-5_7 | 书目级，正文判断另见N01–N16 |
| F01 | 2023 | Cicada: A framework for private non-interactive on-chain auctions and voting | 540bf81da128a028c4398791811446f78eee5af1 | 书目级，正文判断另见N01–N16 |
| F04 | 2026 | A novel FPGA-based mixed garbled circuit hardware accelerator (MixGCAcc) | 10.1007/s11227-026-08842-6 | 书目级，正文判断另见N01–N16 |
| F04 | 2026 | Verifiable quantum advantage in extremely low depth | 2609.01448 | 书目级，正文判断另见N01–N16 |
| F04 | 2026 | Time-Lock Puzzles with Preprocessing: an Instantiation from Average-Case Hardness Assumptions on Graphs and Lattices | 10.1109/CSF68417.2026.00038 | 书目级，正文判断另见N01–N16 |
| F04 | 2026 | Shuffling Is Universal: Statistical Additive Randomized Encodings for All Functions | 10.1145/3798129.3800890 | 书目级，正文判断另见N01–N16 |
| F04 | 2026 | Pseudoentanglement in constant depth: How trivial states can have non-trivial entanglement structure | 10.48550/arXiv.2605.31448 | 书目级，正文判断另见N01–N16 |
| F04 | 2026 | Obfuscation of Arbitrary Quantum Circuits | 10.48550/arXiv.2601.08969 | 书目级，正文判断另见N01–N16 |
| F04 | 2025 | Succinct Homomorphic MACs from Groups and Applications | 10.1109/FOCS63196.2025.00131 | 书目级，正文判断另见N01–N16 |
| F04 | 2025 | Amplifying Randomized Encodings&Applications | 2505.21442 | 书目级，正文判断另见N01–N16 |
| F04 | 2025 | Proofs of Useful Work from Arbitrary Matrix Multiplication | 10.48550/arXiv.2504.09971 | 书目级，正文判断另见N01–N16 |
| F04 | 2024 | PP-GWAS: Privacy Preserving Multi-Site Genome-wide Association Studies | 10.1038/s41467-025-66771-z | 书目级，正文判断另见N01–N16 |
| F04 | 2024 | Low-Latency Privacy-Preserving Deep Learning Design via Secure MPC | 10.48550/arXiv.2407.18982 | 书目级，正文判断另见N01–N16 |
| F04 | 2023 | Advisor-Verifier-Prover Games and the Hardness of Information Theoretic Cryptography | 10.1109/FOCS57990.2023.00039 | 书目级，正文判断另见N01–N16 |
| F04 | 2023 | Quadratic Secret Sharing and Conditional Disclosure of Secrets | 10.1109/TIT.2023.3296588 | 书目级，正文判断另见N01–N16 |
| F04 | 2023 | Fine-Grained Secure Attribute-Based Encryption | 10.1007/s00145-023-09479-x | 书目级，正文判断另见N01–N16 |
| F04 | 2023 | The Round Complexity of Statistical MPC with Optimal Resiliency | 10.1145/3564246.3585228 | 书目级，正文判断另见N01–N16 |
| F04 | 2023 | Range Avoidance for Constant-Depth Circuits: Hardness and Algorithms | 10.48550/arXiv.2303.05044 | 书目级，正文判断另见N01–N16 |
| F04 | 2022 | Geometry of Secure Two-party Computation | 10.1109/FOCS54457.2022.00101 | 书目级，正文判断另见N01–N16 |
| F04 | 2022 | On the Range Avoidance Problem for Circuits | 10.1109/FOCS54457.2022.00067 | 书目级，正文判断另见N01–N16 |
| F04 | 2021 | Polymath: Low-Latency MPC via Secure Polynomial Evaluations and Its Applications | 10.2478/popets-2022-0020 | 书目级，正文判断另见N01–N16 |
| F04 | 2021 | Hardness of KT characterizes parallel cryptography | 10.4230/LIPIcs.CCC.2021.35 | 书目级，正文判断另见N01–N16 |
| F04 | 2020 | The Round Complexity of Perfect MPC with Active Security and Optimal Resiliency | 10.1109/FOCS46700.2020.00121 | 书目级，正文判断另见N01–N16 |
| F04 | 2020 | New Techniques for Zero-Knowledge: Leveraging Inefficient Provers to Reduce Assumptions, Interaction, and Trust | 10.1007/978-3-030-56877-1_24 | 书目级，正文判断另见N01–N16 |
| F04 | 2020 | Black-Box Transformations from Passive to Covert Security with Public Verifiability | 10.1007/978-3-030-56880-1_23 | 书目级，正文判断另见N01–N16 |
| F04 | 2020 | Quantum garbled circuits | 10.1145/3519935.3520073 | 书目级，正文判断另见N01–N16 |
| F04 | 2020 | Compact Adaptively Secure ABE from k-Lin: Beyond NC1 and Towards NL | 10.1007/978-3-030-45727-3_9 | 书目级，正文判断另见N01–N16 |
| F04 | 2020 | Broadcast-Optimal Two-Round MPC | 10.1007/978-3-030-45724-2_28 | 书目级，正文判断另见N01–N16 |
| F04 | 2020 | Cryptographic Obfuscation: A Survey | 10.1007/978-3-319-98041-6 | 书目级，正文判断另见N01–N16 |
| F04 | 2020 | Expand-and-Randomize: An Algebraic Approach to Secure Computation | 10.3390/e23111461 | 书目级，正文判断另见N01–N16 |
| F04 | 2019 | Fine-Grained Cryptography Revisited | 10.1007/s00145-021-09390-3 | 书目级，正文判断另见N01–N16 |
| F04 | 2019 | Output Compression, MPC, and iO for Turing Machines | 10.1007/978-3-030-34578-5_13 | 书目级，正文判断另见N01–N16 |
| F04 | 2019 | Crypto-Oriented Neural Architecture Design | 10.1109/ICASSP39728.2021.9413592 | 书目级，正文判断另见N01–N16 |
| F04 | 2019 | Arithmetic Garbling from Bilinear Maps | 10.1007/978-3-030-29962-0_9 | 书目级，正文判断另见N01–N16 |
| F04 | 2019 | Multiplicative Linear Secret Sharing Without Interaction | 10.1007/978-3-030-24271-8_16 | 书目级，正文判断另见N01–N16 |
| F04 | 2019 | Offline Witness Encryption from Witness PRF and Randomized Encoding in CRS Model | 10.1007/978-3-030-21548-4_5 | 书目级，正文判断另见N01–N16 |
| F04 | 2019 | Setup-Free Secure Search on Encrypted Data: Faster and Post-Processing Free | 10.2478/popets-2019-0038 | 书目级，正文判断另见N01–N16 |
| F04 | 2019 | Uncovering Algebraic Structures in the MPC Landscape | 10.1007/978-3-030-17656-3_14 | 书目级，正文判断另见N01–N16 |
| F04 | 2019 | Indistinguishability Obfuscation Without Multilinear Maps: New Methods for Bootstrapping and Instantiation | 10.1007/978-3-030-17653-2_7 | 书目级，正文判断另见N01–N16 |
| F04 | 2019 | Degree 2 is Complete for the Round-Complexity of Malicious MPC | 10.1007/978-3-030-17656-3_18 | 书目级，正文判断另见N01–N16 |
| F04 | 2019 | Two Round Information-Theoretic MPC with Malicious Security | 10.1007/978-3-030-17656-3_19 | 书目级，正文判断另见N01–N16 |
| F04 | 2019 | Secure Data Retrieval On The Cloud Homomorphic Encryption Meets Coresets | 10.13154/TCHES.V2019.I2.80-106 | 书目级，正文判断另见N01–N16 |
| F04 | 2018 | Fine-Grained Secure Computation | 10.1007/978-3-030-03810-6_3 | 书目级，正文判断另见N01–N16 |
| F04 | 2018 | On the Power of Amortization in Secret Sharing | 10.1145/3417756 | 书目级，正文判断另见N01–N16 |
| F04 | 2018 | Best Possible Information-Theoretic MPC | 10.1007/978-3-030-03810-6_10 | 书目级，正文判断另见N01–N16 |
| F04 | 2018 | Round Optimal Black-Box “Commit-and-Prove” | 10.1007/978-3-030-03807-6_11 | 书目级，正文判断另见N01–N16 |
| F04 | 2018 | Perfect Secure Computation in Two Rounds | 10.1007/978-3-030-03807-6_6 | 书目级，正文判断另见N01–N16 |
| F04 | 2018 | Two-Round MPC: Information-Theoretic and Black-Box | 10.1007/978-3-030-03807-6_5 | 书目级，正文判断另见N01–N16 |
| F04 | 2018 | Exploring Crypto Dark Matter: - New Simple PRF Candidates and Their Applications | 10.1007/978-3-030-03810-6_25 | 书目级，正文判断另见N01–N16 |
| F04 | 2018 | On the Inner Product Predicate and a Generalization of Matching Vector Families | 10.48550/arXiv.1810.02396 | 书目级，正文判断另见N01–N16 |
| F04 | 2018 | Round-Optimal Secure Multiparty Computation with Honest Majority | 10.1007/978-3-319-96881-0_14 | 书目级，正文判断另见N01–N16 |
| F04 | 2018 | Limits on the Power of Garbling Techniques for Public-Key Encryption | 10.1007/978-3-319-96878-0_12 | 书目级，正文判断另见N01–N16 |
| F04 | 2018 | Brief Announcement: On Secure m-Party Computation, Commuting Permutation Systems and Unassisted Non-Interactive MPC | 10.4230/LIPIcs.ICALP.2018.103 | 书目级，正文判断另见N01–N16 |
| F04 | 2018 | The Communication Complexity of Private Simultaneous Messages, Revisited | 10.1007/s00145-019-09334-y | 书目级，正文判断另见N01–N16 |
| F04 | 2018 | Towards Breaking the Exponential Barrier for General Secret Sharing | 10.1007/978-3-319-78381-9_21 | 书目级，正文判断另见N01–N16 |
| F04 | 2018 | Two-round Multiparty Secure Computation from Minimal Assumptions | 10.1145/3566048 | 书目级，正文判断另见N01–N16 |
| F04 | 2018 | Simple and Generic Constructions of Succinct Functional Encryption | 10.1007/s00145-021-09396-x | 书目级，正文判断另见N01–N16 |
| F04 | 2017 | On the Untapped Potential of Encoding Predicates by Arithmetic Circuits and Their Applications | 10.1007/978-3-319-70700-6_4 | 书目级，正文判断另见N01–N16 |
| F04 | 2017 | Verifiably Multiplicative Secret Sharing | 10.1007/978-3-319-72089-0_5 | 书目级，正文判断另见N01–N16 |
| F04 | 2017 | On Secure Two-Party Computation in Three Rounds | 10.1007/978-3-319-70500-2_21 | 书目级，正文判断另见N01–N16 |
| F04 | 2017 | Homomorphic Secret Sharing from Paillier Encryption | 10.1007/978-3-319-68637-0_23 | 书目级，正文判断另见N01–N16 |
| F04 | 2017 | Exponentially-Hard Gap-CSP and Local PRG via Local Hardcore Functions | 10.1109/FOCS.2017.82 | 书目级，正文判断另见N01–N16 |
| F04 | 2017 | Concrete Efficiency Improvements for Multiparty Garbling with an Honest Majority | 10.1007/978-3-030-25283-0_16 | 书目级，正文判断另见N01–N16 |
| F04 | 2017 | Conditional Disclosure of Secrets: Amplification, Closure, Amortization, Lower-Bounds, and Separations | 10.1007/978-3-319-63688-7_24 | 书目级，正文判断另见N01–N16 |
| F04 | 2017 | Indistinguishability Obfuscation for Turing Machines: Constant Overhead and Amortization | 10.1007/978-3-319-63715-0_9 | 书目级，正文判断另见N01–N16 |
| F04 | 2017 | A New Approach to Round-Optimal Secure Multiparty Computation | 10.1007/978-3-319-63688-7_16 | 书目级，正文判断另见N01–N16 |
| F04 | 2017 | Conditional Disclosure of Secrets via Non-linear Reconstruction | 10.1007/978-3-319-63688-7_25 | 书目级，正文判断另见N01–N16 |
| F04 | 2017 | Secure Arithmetic Computation with Constant Computational Overhead | 10.1007/978-3-319-63688-7_8 | 书目级，正文判断另见N01–N16 |
| F04 | 2017 | Group-Based Secure Computation: Optimizing Rounds, Communication, and Computation | 10.1007/978-3-319-56614-6_6 | 书目级，正文判断另见N01–N16 |
| F04 | 2017 | Functional Encryption: Deterministic to Randomized Functions from Simple Assumptions | 10.1007/978-3-319-56614-6_2 | 书目级，正文判断另见N01–N16 |
| F04 | 2017 | Projective Arithmetic Functional Encryption and Indistinguishability Obfuscation from Degree-5 Multilinear Maps | 10.1007/978-3-319-56620-7_6 | 书目级，正文判断另见N01–N16 |
| F04 | 2017 | Cryptography with Updates | 10.1007/978-3-319-56614-6_15 | 书目级，正文判断另见N01–N16 |
| F04 | 2017 | Arithmetic Cryptography | 10.1145/3046675 | 书目级，正文判断另见N01–N16 |
| F04 | 2017 | Bounded-Collusion Attribute-Based Encryption from Minimal Assumptions | 10.1007/978-3-662-54388-7_3 | 书目级，正文判断另见N01–N16 |
| F04 | 2016 | An efficient instance hiding scheme | 10.1145/3011077.3011100 | 书目级，正文判断另见N01–N16 |
| F04 | 2016 | Composable Security in the Tamper-Proof Hardware Model Under Minimal Complexity | 10.1007/978-3-662-53641-4_15 | 书目级，正文判断另见N01–N16 |
| F04 | 2016 | Optimizing Semi-Honest Secure Multiparty Computation for the Internet | 10.1145/2976749.2978347 | 书目级，正文判断另见N01–N16 |
| F04 | 2016 | Minimizing Locality of One-Way Functions via Semi-private Randomized Encodings | 10.1007/s00145-016-9244-6 | 书目级，正文判断另见N01–N16 |
| F04 | 2016 | On Garbling Schemes with and Without Privacy | 10.1007/978-3-319-44618-9_25 | 书目级，正文判断另见N01–N16 |
| F04 | 2016 | On the Power of Secure Two-Party Computation | 10.1007/s00145-019-09314-2 | 书目级，正文判断另见N01–N16 |
| F04 | 2016 | On the Relationship Between Statistical Zero-Knowledge and Statistical Randomized Encodings | 10.1007/s00037-018-0170-x | 书目级，正文判断另见N01–N16 |
| F04 | 2016 | Fine-Grained Cryptography | 10.1007/978-3-662-53015-3_19 | 书目级，正文判断另见N01–N16 |
| F04 | 2016 | Two-Message, Oblivious Evaluation of Cryptographic Functionalities | 10.1007/978-3-662-53015-3_22 | 书目级，正文判断另见N01–N16 |
| F04 | 2016 | Spooky Encryption and Its Applications | 10.1007/978-3-662-53015-3_4 | 书目级，正文判断另见N01–N16 |
| F04 | 2016 | On the Communication Required for Unconditionally Secure Multiplication | 10.1007/978-3-662-53008-5_16 | 书目级，正文判断另见N01–N16 |
| F04 | 2016 | Adaptively Secure Garbled Circuits from One-Way Functions | 10.1007/978-3-662-53015-3_6 | 书目级，正文判断另见N01–N16 |
| F04 | 2016 | Two Round Multiparty Computation via Multi-key FHE | 10.1007/978-3-662-49896-5_26 | 书目级，正文判断另见N01–N16 |
| F04 | 2016 | Unconditionally Secure Computation with Reduced Interaction | 10.1007/978-3-662-49896-5_15 | 书目级，正文判断另见N01–N16 |
| F04 | 2016 | Private Web Search with an Expected Constant Round | 10.48550/arXiv.1604.02782 | 书目级，正文判断另见N01–N16 |
| F04 | 2016 | On Program Obfuscation | 69bc9fc1f32a2931ab228219b1e6e30ce345a50e | 书目级，正文判断另见N01–N16 |
| F04 | 2016 | Cryptography for Parallel RAM from Indistinguishability Obfuscation | 10.1145/2840728.2840769 | 书目级，正文判断另见N01–N16 |
| F04 | 2016 | Time-Lock Puzzles from Randomized Encodings | 10.1145/2840728.2840745 | 书目级，正文判断另见N01–N16 |
| F04 | 2016 | From Private Simultaneous Messages to Zero-Information Arthur–Merlin Protocols and Back | 10.1007/s00145-016-9239-3 | 书目级，正文判断另见N01–N16 |
| F04 | 2016 | Functional Encryption Without Obfuscation | 10.1007/978-3-662-49099-0_18 | 书目级，正文判断另见N01–N16 |
| F04 | 2016 | Output-Compressing Randomized Encodings and Applications | 10.1007/978-3-662-49096-9_5 | 书目级，正文判断另见N01–N16 |
| F04 | 2015 | Garbling Scheme for Formulas with Constant Size of Garbled Gates | 10.1007/978-3-662-48797-6_31 | 书目级，正文判断另见N01–N16 |
| F04 | 2015 | On Cut-and-Choose Oblivious Transfer and Its Variants | 10.1007/978-3-662-48797-6_17 | 书目级，正文判断另见N01–N16 |
| F04 | 2015 | Secret Sharing and Statistical Zero Knowledge | 10.1007/978-3-662-48797-6_27 | 书目级，正文判断另见N01–N16 |
| F04 | 2015 | Indistinguishability Obfuscation from Functional Encryption | 10.1145/3234511 | 书目级，正文判断另见N01–N16 |
| F04 | 2015 | Indistinguishability Obfuscation from Compact Functional Encryption | 10.1007/978-3-662-47989-6_15 | 书目级，正文判断另见N01–N16 |
| F04 | 2015 | From Selective to Adaptive Security in Functional Encryption | 10.1007/978-3-662-48000-7_32 | 书目级，正文判断另见N01–N16 |
| F04 | 2015 | Constant-Round Concurrent Zero-Knowledge from Indistinguishability Obfuscation | 10.1007/978-3-662-47989-6_14 | 书目级，正文判断另见N01–N16 |
| F04 | 2015 | Statistical Randomized Encodings: A Complexity Theoretic View | 10.1007/978-3-662-47672-7_1 | 书目级，正文判断另见N01–N16 |
| F04 | 2015 | Succinct Randomized Encodings and their Applications | 10.1145/2746539.2746574 | 书目级，正文判断另见N01–N16 |
| F04 | 2015 | Indistinguishability Obfuscation for Turing Machines with Unbounded Memory | 10.1145/2746539.2746614 | 书目级，正文判断另见N01–N16 |
| F04 | 2015 | Encoding Functions with Constant Online Rate, or How to Compress Garbled Circuit Keys | 10.1137/130929643 | 书目级，正文判断另见N01–N16 |
| F04 | 2015 | Public-Coin Differing-Inputs Obfuscation and Its Applications | 10.1007/978-3-662-46497-7_26 | 书目级，正文判断另见N01–N16 |
| F04 | 2015 | Obfuscation of Probabilistic Circuits and Applications | 10.1007/978-3-662-46497-7_19 | 书目级，正文判断另见N01–N16 |
| F04 | 2015 | Arithmetic Cryptography: Extended Abstract | 10.1145/2688073.2688114 | 书目级，正文判断另见N01–N16 |
| F04 | 2014 | Bootstrapping Obfuscators via Fast Pseudorandom Functions | 10.1007/978-3-662-45608-8_9 | 书目级，正文判断另见N01–N16 |
| F04 | 2014 | Indistinguishability Obfuscation and UCEs: The Case of Computationally Unpredictable Sources | 10.1007/978-3-662-44371-2_11 | 书目级，正文判断另见N01–N16 |
| F04 | 2014 | Non-Interactive Secure Multiparty Computation | 10.1007/978-3-662-44381-1_22 | 书目级，正文判断另见N01–N16 |
| F04 | 2014 | Partial Garbling Schemes and Their Applications | 10.1007/978-3-662-43948-7_54 | 书目级，正文判断另见N01–N16 |
| F04 | 2014 | Secure and scalable match: overcoming the universal circuit bottleneck using group programs | 10.1515/popets-2015-0013 | 书目级，正文判断另见N01–N16 |
| F04 | 2014 | Achieving Privacy in Verifiable Computation with Multiple Servers - Without FHE and without Pre-processing | 10.1007/978-3-642-54631-0_9 | 书目级，正文判断另见N01–N16 |
| F04 | 2014 | On the Cryptographic Complexity of the Worst Functions | 10.1007/978-3-642-54242-8_14 | 书目级，正文判断另见N01–N16 |
| F04 | 2014 | Dual System Encryption via Predicate Encodings | 10.1007/978-3-642-54242-8_26 | 书目级，正文判断另见N01–N16 |
| F04 | 2014 | Theory of Cryptography | 10.1007/978-3-642-54242-8 | 书目级，正文判断另见N01–N16 |
| F04 | 2014 | Lower Bounds in the Hardware Token Model | 10.1007/978-3-642-54242-8_28 | 书目级，正文判断另见N01–N16 |
| F04 | 2013 | Cryptography in Constant Parallel Time | 10.1007/978-3-642-17367-7 | 书目级，正文判断另见N01–N16 |
| F04 | 2013 | Encoding Functions with Constant Online Rate or How to Compress Garbled Circuits Keys | 10.1007/978-3-642-40084-1_10 | 书目级，正文判断另见N01–N16 |
| F04 | 2013 | Optimizing ORAM and Using It Efficiently for Secure Computation | 10.1007/978-3-642-39077-7_1 | 书目级，正文判断另见N01–N16 |
| F04 | 2013 | Garbled Circuits via Structured Encryption | 10.1007/978-3-642-41320-9_12 | 书目级，正文判断另见N01–N16 |
| F04 | 2013 | Parallel Homomorphic Encryption | 10.1007/978-3-642-41320-9_15 | 书目级，正文判断另见N01–N16 |
| F04 | 2013 | Garbling XOR Gates “For Free” in the Standard Model | 10.1007/s00145-015-9201-9 | 书目级，正文判断另见N01–N16 |
| F04 | 2012 | Adaptively Secure Garbling with Applications to One-Time Programs and Secure Outsourcing | 10.1007/978-3-642-34961-4_10 | 书目级，正文判断另见N01–N16 |
| F04 | 2012 | Foundations of garbled circuits | 10.1145/2382196.2382279 | 书目级，正文判断另见N01–N16 |
| F04 | 2012 | Improved Secure Two-Party Computation via Information-Theoretic Garbled Circuits | 10.1007/978-3-642-32928-9_12 | 书目级，正文判断另见N01–N16 |
| F04 | 2012 | Functional Encryption with Bounded Collusions via Multi-party Computation | 10.1007/978-3-642-32009-5_11 | 书目级，正文判断另见N01–N16 |
| F04 | 2012 | Information-Flow Control for Programming on Encrypted Data | 10.1109/CSF.2012.30 | 书目级，正文判断另见N01–N16 |
| F04 | 2012 | Multiparty Computation with Low Communication, Computation and Interaction via Threshold FHE | 10.1007/978-3-642-29011-4_29 | 书目级，正文判断另见N01–N16 |
| F04 | 2012 | Short Round Sub-Linear Zero-Knowledge Argument for Linear Algebraic Relations | 10.1587/TRANSFUN.E95.A.776 | 书目级，正文判断另见N01–N16 |
| F04 | 2012 | From randomizing polynomials to parallel algorithms | 10.1145/2090236.2090244 | 书目级，正文判断另见N01–N16 |
| F04 | 2012 | On beating the hybrid argument | 10.1145/2090236.2090273 | 书目级，正文判断另见N01–N16 |
| F04 | 2011 | How to Garble Arithmetic Circuits | 10.1137/120875193 | 书目级，正文判断另见N01–N16 |
| F04 | 2011 | Randomly Encoding Functions: A New Cryptographic Paradigm - (Invited Talk) | 10.1007/978-3-642-20728-0_3 | 书目级，正文判断另见N01–N16 |
| F04 | 2011 | Key-Dependent Message Security: Generic Amplification and Completeness | 10.1007/s00145-013-9149-6 | 书目级，正文判断另见N01–N16 |
| F04 | 2011 | Homomorphic Signatures for Polynomial Functions | 10.1007/978-3-642-20465-4_10 | 书目级，正文判断另见N01–N16 |
| F04 | 2011 | Limits on the Stretch of Non-adaptive Constructions of Pseudo-Random Generators | 10.1007/978-3-642-19571-6_30 | 书目级，正文判断另见N01–N16 |
| F04 | 2011 | Round-Efficient Sub-linear Zero-Knowledge Arguments for Linear Algebra | 10.1007/978-3-642-19379-8_24 | 书目级，正文判断另见N01–N16 |
| F04 | 2010 | On d-Multiplicative Secret Sharing | 10.1007/s00145-010-9056-z | 书目级，正文判断另见N01–N16 |
| F04 | 2010 | Secure Multiparty Computation with Minimal Interaction | 10.1007/978-3-642-14623-7_31 | 书目级，正文判断另见N01–N16 |
| F04 | 2010 | From Secrecy to Soundness: Efficient Verification via Secure Computation | 10.1007/978-3-642-14165-2_14 | 书目级，正文判断另见N01–N16 |
| F04 | 2010 | Efficient and Secure Evaluation of Multivariate Polynomials and Applications | 10.1007/978-3-642-13708-2_15 | 书目级，正文判断另见N01–N16 |
| F04 | 2010 | Research on the Secure Multi-Party Computation of some Linear Algebra Problems | 10.4028/www.scientific.net/AMM.20-23.265 | 书目级，正文判断另见N01–N16 |
| F04 | 2009 | Secure Multi-party Computation Minimizing Online Rounds | 10.1007/978-3-642-10366-7_16 | 书目级，正文判断另见N01–N16 |
| F04 | 2009 | Secret Sharing Comparison by Transformation and Rotation | 10.1007/978-3-642-10230-1_14 | 书目级，正文判断另见N01–N16 |
| F04 | 2008 | t-Private and t-Secure Auctions | 10.1007/s11390-008-9174-3 | 书目级，正文判断另见N01–N16 |
| F04 | 2008 | The cost of protecting privacy in multimedia applications | 10.1145/1454586.1454595 | 书目级，正文判断另见N01–N16 |
| F04 | 2007 | Secure Multiparty Computation of DNF | 10.1007/978-3-540-77048-0_20 | 书目级，正文判断另见N01–N16 |
| F04 | 2007 | Cryptography with Constant Input Locality | 10.1007/s00145-009-9039-0 | 书目级，正文判断另见N01–N16 |
| F04 | 2007 | Universally-Composable Two-Party Computation in Two Rounds | 10.1007/978-3-540-74143-5_7 | 书目级，正文判断另见N01–N16 |
| F04 | 2007 | A Note on Secure Computation of the Moore-Penrose Pseudoinverse and Its Application to Secure Linear Algebra | 10.1007/978-3-540-74143-5_34 | 书目级，正文判断另见N01–N16 |
| F04 | 2007 | t -Private and Secure Auctions | 10.1007/978-3-540-72504-6_44 | 书目级，正文判断另见N01–N16 |
| F04 | 2007 | Evaluating Branching Programs on Encrypted Data | 10.1007/978-3-540-70936-7_31 | 书目级，正文判断另见N01–N16 |
| F04 | 2006 | Protecting the privacy of user's QoS preferences for multimedia applications | 10.1145/1163698.1163705 | 书目级，正文判断另见N01–N16 |
| F04 | 2006 | Scalable Secure Multiparty Computation | 10.1007/11818175_30 | 书目级，正文判断另见N01–N16 |
| F04 | 2006 | On Combining Privacy with Guaranteed Output Delivery in Secure Multiparty Computation | 10.1007/11818175_29 | 书目级，正文判断另见N01–N16 |
| F04 | 2006 | Oblivious Polynomial Evaluation | 10.1137/S0097539704383633 | 书目级，正文判断另见N01–N16 |
| F04 | 2006 | Efficient Polynomial Operations in the Shared-Coefficients Setting | 10.1007/11745853_4 | 书目级，正文判断另见N01–N16 |
| F04 | 2006 | Unconditionally Secure Constant Round Multi-Party Computation for Equality, Comparison, Bits and Exponentiation | 10.1007/11681878_15 | 书目级，正文判断另见N01–N16 |
| F04 | 2006 | A Round and Communication Efficient Secure Ranking Protocol | 10.1007/11605805_22 | 书目级，正文判断另见N01–N16 |
| F04 | 2005 | Gate Evaluation Secret Sharing and Secure One-Round Two-Party Computation | 10.1007/11593447_8 | 书目级，正文判断另见N01–N16 |
| F04 | 2005 | Efficient Cryptographic Protocol Design Based on Distributed El Gamal Encryption | 10.1007/11734727_5 | 书目级，正文判断另见N01–N16 |
| F04 | 2005 | Secure Computation of Constant-Depth Circuits with Applications to Database Search Problems | 10.1007/11535218_24 | 书目级，正文判断另见N01–N16 |
| F04 | 2005 | Constant-Round Multiparty Computation Using a Black-Box Pseudorandom Generator | 10.1007/11535218_23 | 书目级，正文判断另见N01–N16 |
| F04 | 2005 | COMPUTATIONALLY PRIVATE RANDOMIZING POLYNOMIALS AND THEIR APPLICATIONS | 10.1007/s00037-006-0211-8 | 书目级，正文判断另见N01–N16 |
| F04 | 2005 | Share Conversion, Pseudorandom Secret-Sharing and Applications to Secure Computation | 10.1007/978-3-540-30576-7_19 | 书目级，正文判断另见N01–N16 |
| F04 | 2004 | Cryptography in NC0 | 10.1137/S0097539705446950 | 书目级，正文判断另见N01–N16 |
| F04 | 2004 | Round-Optimal Secure Two-Party Computation | 10.1007/978-3-540-28628-8_21 | 书目级，正文判断另见N01–N16 |
| F04 | 2004 | On the Hardness of Information-Theoretic Multiparty Computation | 10.1007/978-3-540-24676-3_26 | 书目级，正文判断另见N01–N16 |
| F04 | 2003 | Efficient Multi-party Computation over Rings | 10.1007/3-540-39200-9_37 | 书目级，正文判断另见N01–N16 |
| F04 | 2003 | Round Efficiency of Multi-party Computation with a Dishonest Majority | 10.1007/3-540-39200-9_36 | 书目级，正文判断另见N01–N16 |
| F04 | 2002 | Some Applications of Polynomials for the Design of Cryptographic Protocols | 10.1007/3-540-36413-7_1 | 书目级，正文判断另见N01–N16 |
| F04 | 2002 | On 2-Round Secure Multiparty Computation | 10.1007/3-540-45708-9_12 | 书目级，正文判断另见N01–N16 |
| F04 | 2002 | Perfect Constant-Round Secure Computation via Perfect Randomizing Polynomials | 10.1007/3-540-45465-9_22 | 书目级，正文判断另见N01–N16 |
| F04 | 2001 | Oblivious polynomial evaluation and oblivious neural learning | 10.1016/j.tcs.2005.03.049 | 书目级，正文判断另见N01–N16 |
| F04 | 2001 | Communication Complexity and Secure Function Evaluation | 10.48550/arXiv.cs/0109011 | 书目级，正文判断另见N01–N16 |
| F04 | 2001 | Robustness for Free in Unconditional Multi-party Computation | 10.1007/3-540-44647-8_6 | 书目级，正文判断另见N01–N16 |
| F04 | 2001 | Secure Distributed Linear Algebra in a Constant Number of Rounds | 10.1007/3-540-44647-8_7 | 书目级，正文判断另见N01–N16 |
| F04 | 2001 | Cryptography and mechanism design | 53911ce7d987bbf6808b96c461aa140051159a36 | 书目级，正文判断另见N01–N16 |
| F04 | 2001 | Communication preserving protocols for secure function evaluation | 10.1145/380752.380855 | 书目级，正文判断另见N01–N16 |
| F04 | 2001 | The round complexity of verifiable secret sharing and secure multicast | 10.1145/380752.380853 | 书目级，正文判断另见N01–N16 |
| F04 | 2025 | Efficient Garbled Pseudorandom Functions and Lookup Tables from Minimal Assumption | 10.1007/978-3-032-12287-2_3 | 书目级，正文判断另见N01–N16 |
| F04 | 2025 | Breaking the 1/λ-Rate Barrier for Arithmetic Garbling | 10.1007/978-3-031-91095-1_7 | 书目级，正文判断另见N01–N16 |
| F04 | 2024 | Simplified PIR and CDS Protocols and Improved Linear Secret-Sharing Schemes | 10.1007/978-3-032-12293-3_12 | 书目级，正文判断另见N01–N16 |
| F04 | 2024 | On the Feasibility of Sliced Garbling | ec1d982e0abacec3e2b76f9a098b442bc5e7d16f | 书目级，正文判断另见N01–N16 |
| F04 | 2024 | Garbled Circuit Lookup Tables with Logarithmic Number of Ciphertexts | 10.1007/978-3-031-58740-5_7 | 书目级，正文判断另见N01–N16 |
| F04 | 2024 | Succinct Randomized Encodings from Non-compact Functional Encryption, Faster and Simpler | a3632cd80d673169bd0089df6545d681273ff424 | 书目级，正文判断另见N01–N16 |
| F04 | 2023 | Additive Randomized Encodings and Their Applications | 10.1007/978-3-031-38557-5_7 | 书目级，正文判断另见N01–N16 |
| F04 | 2023 | A New Approach to Garbled Circuits | 10.1007/978-3-031-33491-7_23 | 书目级，正文判断另见N01–N16 |
| F04 | 2023 | On the Invalidity of LV16/Lin17 Obfuscation Schemes | 98d98c06957c72cf23d615e47b3fa030bcd00e77 | 书目级，正文判断另见N01–N16 |
| F04 | 2023 | Black-Box Reusable NISC with Random Oracles | 10.1007/978-3-031-30617-4_3 | 书目级，正文判断另见N01–N16 |
| F04 | 2023 | Unconditionally Secure Multiparty Computation for Symmetric Functions with Low Bottleneck Complexity | 10.1007/978-981-99-8721-4_11 | 书目级，正文判断另见N01–N16 |
| F04 | 2023 | Actively Secure Arithmetic Computation and VOLE with Constant Computational Overhead | 10.1007/978-3-031-30617-4_7 | 书目级，正文判断另见N01–N16 |
| F04 | 2023 | A Framework for Statistically Sender Private OT with Optimal Rate | 10.1007/978-3-031-38557-5_18 | 书目级，正文判断另见N01–N16 |
| F04 | 2023 | Arithmetic Sketching | 10.1007/978-3-031-38557-5_6 | 书目级，正文判断另见N01–N16 |
| F04 | 2023 | One-Message Secure Reductions: On the Cost of Converting Correlations | 10.1007/978-3-031-38557-5_17 | 书目级，正文判断另见N01–N16 |
| F04 | 2023 | How to Garble Mixed Circuits that Combine Boolean and Arithmetic Computations | 10.1007/978-3-031-58751-1_12 | 书目级，正文判断另见N01–N16 |
| F04 | 2022 | Quadratic Multiparty Randomized Encodings Beyond Honest Majority and Their Applications | 10.1007/978-3-031-15985-5_16 | 书目级，正文判断另见N01–N16 |
| F04 | 2022 | SCALES - MPC with Small Clients and Larger Ephemeral Servers | 10.1007/978-3-031-22365-5_18 | 书目级，正文判断另见N01–N16 |
| F04 | 2022 | Arithmetic Tuples for MPC | bd464e1157a18a0ec26707c687847973d8ca474a | 书目级，正文判断另见N01–N16 |
| F04 | 2022 | Round-Optimal Black-Box Protocol Compilers | 10.1007/978-3-031-06944-4_8 | 书目级，正文判断另见N01–N16 |
| F04 | 2022 | Non-Interactive Zero-Knowledge Proofs with Fine-Grained Security | 10.1007/978-3-031-07085-3_11 | 书目级，正文判断另见N01–N16 |
| F04 | 2022 | A Note on the Complexity of Private Simultaneous Messages with Many Parties | 10.4230/LIPIcs.ITC.2022.7 | 书目级，正文判断另见N01–N16 |
| F04 | 2022 | Maliciously Circuit-Private FHE from Information-Theoretic Principles | 10.4230/LIPIcs.ITC.2022.4 | 书目级，正文判断另见N01–N16 |
| F04 | 2022 | Two-Round MPC without Round Collapsing Revisited - Towards Efficient Malicious Protocols | 10.1007/978-3-031-15802-5_13 | 书目级，正文判断另见N01–N16 |
| F04 | 2022 | Set (Non-)Membership NIZKs from Determinantal Accumulators | 10.1007/978-3-031-44469-2_18 | 书目级，正文判断另见N01–N16 |
| F04 | 2022 | On the Invalidity of Lin16/Lin17 Obfuscation Schemes | 19dc306296bfa6207c8fcece1d12326971598b0c | 书目级，正文判断另见N01–N16 |
| F04 | 2022 | SECURELY COMPUTING PIECEWISE CONSTANT CODES new arithmetic encodings for boolean functions, and applications to committed two-party computation | 356f929eb02d8af953cceb743d401bd0319dcf80 | 书目级，正文判断另见N01–N16 |
| F04 | 2022 | Secure Non-interactive Simulation: Feasibility and Rate | 10.1007/978-3-031-07082-2_27 | 书目级，正文判断另见N01–N16 |
| F04 | 2022 | Notes on Reusable Garbling | c3e45f1cda9a53a5c7871c0e2ae196d754e7822e | 书目级，正文判断另见N01–N16 |
| F04 | 2021 | On Actively-Secure Elementary MPC Reductions | 10.1007/978-3-030-90459-3_24 | 书目级，正文判断另见N01–N16 |
| F04 | 2021 | Size of IK00 Branching Program | f893e1b3a7a9e1524cd9ae1b6752d726437daa6d | 书目级，正文判断另见N01–N16 |
| F04 | 2021 | Boolean Functions from Hyperplane Coverings | a4a08cfca2f0409de119fbb4801e439960a3f5c7 | 书目级，正文判断另见N01–N16 |
| F04 | 2021 | Large Scale, Actively Secure Computation from LPN and Free-XOR Garbled Circuits | 10.1007/978-3-030-77883-5_2 | 书目级，正文判断另见N01–N16 |
| F04 | 2021 | Updatable Signatures and Message Authentication Codes | 10.1007/978-3-030-75245-3_25 | 书目级，正文判断另见N01–N16 |
| F04 | 2021 | On Communication Models and Best-Achievable Security in Two-Round MPC | 10.1007/978-3-030-90453-1_4 | 书目级，正文判断另见N01–N16 |
| F04 | 2021 | Threshold Garbled Circuits and Ad Hoc Secure Computation | 10.1007/978-3-030-77883-5_3 | 书目级，正文判断另见N01–N16 |
| F04 | 2021 | Multiparty Reusable Non-Interactive Secure Computation from LWE | 10.1007/978-3-030-77886-6_25 | 书目级，正文判断另见N01–N16 |
| F04 | 2021 | Bounded Indistinguishability for Simple Sources | 10.4230/LIPIcs.ITCS.2022.26 | 书目级，正文判断另见N01–N16 |
| F04 | 2021 | Memory-Hard Puzzles in the Standard Model with Applications to Memory-Hard Functions and Resource-Bounded Locally Decodable Codes | 10.1007/978-3-031-14791-3_3 | 书目级，正文判断另见N01–N16 |
| F04 | 2021 | Versatile and Sustainable Timed-Release Encryption and Sequential Time-Lock Puzzles (Extended Abstract) | 10.1007/978-3-030-88428-4_4 | 书目级，正文判断另见N01–N16 |
| F04 | 2021 | The Round Complexity of Quantum Zero-Knowledge | 10.1007/978-3-030-90459-3_5 | 书目级，正文判断另见N01–N16 |
| F04 | 2021 | Polynomial Representation Is Tricky: Maliciously Secure Private Set Intersection Revisited | 10.1007/978-3-030-88428-4_35 | 书目级，正文判断另见N01–N16 |
| F04 | 2021 | Efficient NIZKs for Algebraic Sets | 10.1007/978-3-030-92078-4_5 | 书目级，正文判断另见N01–N16 |
| F04 | 2021 | Round-optimal Honest-majority MPC in Minicrypt and with Everlasting Security | 10.1007/978-3-031-22365-5_4 | 书目级，正文判断另见N01–N16 |
| F04 | 2021 | Traceable Secret Sharing and Applications | 10.1007/978-3-030-84252-9_24 | 书目级，正文判断另见N01–N16 |
| F04 | 2020 | Cryptography from Information Loss | 10.4230/LIPIcs.ITCS.2020.81 | 书目级，正文判断另见N01–N16 |
| F04 | 2020 | Affine Determinant Programs: A Framework for Obfuscation and Witness Encryption | 10.4230/LIPIcs.ITCS.2020.82 | 书目级，正文判断另见N01–N16 |
| F04 | 2020 | On the Complexity of Decomposable Randomized Encodings, Or: How Friendly Can a Garbling-Friendly PRF Be? | 10.4230/LIPIcs.ITCS.2020.86 | 书目级，正文判断另见N01–N16 |
| F04 | 2020 | Separating Two-Round Secure Computation From Oblivious Transfer | 10.4230/LIPIcs.ITCS.2020.71 | 书目级，正文判断另见N01–N16 |
| F04 | 2020 | Secure Non-interactive Simulation: Hardness & Feasibility | f4b7418c2c538c6a194d429c45ed1bfb76c51a2b | 书目级，正文判断另见N01–N16 |
| F04 | 2020 | Compact Adaptively Secure ABE from k-Lin: Beyond NC1 and towards NL | 2e632945260fbf433922c1e51b0990a59f8d7822 | 书目级，正文判断另见N01–N16 |
| F04 | 2020 | Towards Efficiency-Preserving Round Compression in MPC: Do fewer rounds mean more computation? | 10.1007/978-3-030-64840-4_7 | 书目级，正文判断另见N01–N16 |
| F04 | 2020 | Information-Theoretic 2-Round MPC without Round Collapsing: Adaptive Security, and More | 10.1007/978-3-030-64378-2_18 | 书目级，正文判断另见N01–N16 |
| F04 | 2020 | Multiparty Reusable Non-Interactive Secure Computation | 10.1007/978-3-030-64378-2_13 | 书目级，正文判断另见N01–N16 |
| F04 | 2020 | Secure Health Monitoring in the Cloud Using Homomorphic Encryption | 10.4018/978-1-5225-9863-3.ch004 | 书目级，正文判断另见N01–N16 |
| F04 | 2020 | The Resiliency of MPC with Low Interaction: The Benefit of Making Errors | 10.1007/978-3-030-64378-2_20 | 书目级，正文判断另见N01–N16 |
| F04 | 2019 | On polynomial secret sharing schemes | 10.4230/LIPIcs.ITC.2020.12 | 书目级，正文判断另见N01–N16 |
| F04 | 2019 | Cryptographic Sensing | 10.1007/978-3-030-26954-8_19 | 书目级，正文判断另见N01–N16 |
| F04 | 2019 | Multi-Party PSM, Revisited | 10.1007/978-3-030-90453-1_7 | 书目级，正文判断另见N01–N16 |
| F04 | 2018 | New Methods for Indistinguishability Obfuscation: Bootstrapping and Instantiation | 5ca46affead8e6e899626924eb2d57be3e7b9c76 | 书目级，正文判断另见N01–N16 |
| F04 | 2018 | Constructing Witness PRF and Offline Witness Encryption Without Multilinear Maps | fa6021a62532fd0c8607eedb2c17488ccb2a84d5 | 书目级，正文判断另见N01–N16 |
| F04 | 2018 | Rationality and Efficient Verifiable Computation | 20ed1dddf97fdc168f804fc398e7c370eea86d71 | 书目级，正文判断另见N01–N16 |
| F04 | 2018 | 41 : 2 On the Inner Product Predicate and a Generalization of Matching Vector Families 1 | 8bc33fd9a500e089d0ba57cc8d4de30527c0b47a | 书目级，正文判断另见N01–N16 |
| F04 | 2017 | Low-Complexity Cryptographic Hash Functions | 10.4230/LIPIcs.ITCS.2017.7 | 书目级，正文判断另见N01–N16 |
| F04 | 2017 | Garbled Circuits as Randomized Encodings of Functions: a Primer | 10.1007/978-3-319-57048-8_1 | 书目级，正文判断另见N01–N16 |
| F04 | 2017 | New Protocols for Conditional Disclosure of Secrets (and More) | ddc29f6c21578ec6c849e2ada3ca107cfa9771ba | 书目级，正文判断另见N01–N16 |
| F04 | 2017 | Conditional Disclosure of Secrets and d-Uniform Secret Sharing with Constant Information Rate | ef2faa0f1f5bb66418538f1a1d06480d882d150d | 书目级，正文判断另见N01–N16 |
| F04 | 2017 | 7 : 2 On the Average-Case Complexity of MCSP and Its Variants | 5937a46d3130ec18cca58bd3069a347716f7eb92 | 书目级，正文判断另见N01–N16 |
| F04 | 2017 | Some Open Problems in Information-Theoretic Cryptography | 10.4230/LIPIcs.FSTTCS.2017.5 | 书目级，正文判断另见N01–N16 |
| F04 | 2016 | Improved OT Extension for Transferring Short Secrets and Application to Secure Multi-Party Computation | f7e4a8d370cad4b91270780e6041edb3c1544c26 | 书目级，正文判断另见N01–N16 |
| F04 | 2016 | Composable Security in the Tamper Proof Model under Minimal Complexity | e464dc9fc74ba5ef3fb57c9133beeb3f0e10ab72 | 书目级，正文判断另见N01–N16 |
| F04 | 2016 | Advances in Cryptology – CRYPTO 2016 | 10.1007/978-3-662-53008-5 | 书目级，正文判断另见N01–N16 |
| F04 | 2016 | FIFE : a Framework for Investigating Functional Encryption | 83384a5fcb2fe94a250d69e83ab885b79ce9cbdf | 书目级，正文判断另见N01–N16 |
| F04 | 2015 | From Statistical Zero Knowledge to Secret Sharing | b9edc158eaad17eaecadef0eceef3cb1072c7994 | 书目级，正文判断另见N01–N16 |
| F04 | 2015 | Indistinguishability Obfuscation from Functional Encryption for Simple Functions Prabhanjan Ananth | e9a55a44146845815eb8c39c8a43c1c2b3111908 | 书目级，正文判断另见N01–N16 |
| F04 | 2015 | Computation-Trace Indistinguishability Obfuscation and its Applications | 29224780bce1722c75f3909334f115419dea3b96 | 书目级，正文判断另见N01–N16 |
| F04 | 2015 | Secure Health Monitoring in the Cloud Using Homomorphic Encryption: A Branching-Program Formulation | 10.4018/978-1-4666-8662-5.CH004 | 书目级，正文判断另见N01–N16 |
| F04 | 2015 | Succinct Adaptive Garbled RAM | 4dfa2198d6b88d130122a4b716a512d02f53e15f | 书目级，正文判断另见N01–N16 |
| F04 | 2015 | Two Round MPC from LWE via Multi-Key FHE | 1b70ef9a18ffea1a685aa8cd468c452a8174420c | 书目级，正文判断另见N01–N16 |
| F04 | 2015 | Achieving Compactness Generically: Indistinguishability Obfuscation from Non-Compact Functional Encryption | bcf89fab24478255ffb7cddd7c6af52f4442d84b | 书目级，正文判断另见N01–N16 |
| F04 | 2015 | Constructions of Functional Encryption | 3d5d11bdbc5fbcef4c52759ca02bc19347a4e85a | 书目级，正文判断另见N01–N16 |
| F04 | 2015 | A study of efficient secret sharing | dde8a819b5518e2085ef0c38870385dfc89fe175 | 书目级，正文判断另见N01–N16 |
| F04 | 2014 | Automata, Languages, and Programming | 10.1007/978-3-662-43948-7 | 书目级，正文判断另见N01–N16 |
| F04 | 2014 | Fully Secure Functional Encryption without Obfuscation | a1e297afb206b81b23ae054a9667f4ff891c7970 | 书目级，正文判断另见N01–N16 |
| F04 | 2014 | The Trojan Method in Functional Encryption: From Selective to Adaptive Security, Generically | bbac12e7ed3f8d95812a3f66767d0ff4e4a6c84f | 书目级，正文判断另见N01–N16 |
| F04 | 2014 | Randomized Encoding of Functions | 10.1007/978-3-642-17367-7_3 | 书目级，正文判断另见N01–N16 |
| F04 | 2014 | One-Way Functions with Optimal Output Locality | 10.1007/978-3-642-17367-7_6 | 书目级，正文判断另见N01–N16 |
| F04 | 2013 | Randomization Techniques for Secure Computation | 10.3233/978-1-61499-169-4-222 | 书目级，正文判断另见N01–N16 |
| F04 | 2012 | Secure computation with minimal interaction | 28f8500f87f411e437dd383366471f519ead0783 | 书目级，正文判断另见N01–N16 |
| F04 | 2012 | Broadcast and Verifiable Secret Sharing: New Security Models and Round Optimal Constructions | ee1464bc5d4ec106c9b0521c47a8b3a65586d562 | 书目级，正文判断另见N01–N16 |
| F04 | 2012 | Garbling Schemes | 45c33298694500bc489b66f25235da6c4f8790e6 | 书目级，正文判断另见N01–N16 |
| F04 | 2012 | Functional Encryption: Constructions and Lower Bounds | 3754a42b271eeb29397a315f4e77f6514be82e84 | 书目级，正文判断另见N01–N16 |
| F04 | 2012 | A General Framework for Multiparty Computations | 316f2dc323f32d6fa6f593c818fe252cca0930c1 | 书目级，正文判断另见N01–N16 |
| F04 | 2011 | A Domain-Specific Language for Computing on Encrypted Data | c314ea0763ad247eccffc3edcea9128e3bded554 | 书目级，正文判断另见N01–N16 |
| F04 | 2010 | On Approximating the Entropy of Polynomial Mappings | bd421d0ab2ebc2642e448d5a830485a95facf5e5 | 书目级，正文判断另见N01–N16 |
| F04 | 2010 | Studies on Verifiable Secret Sharing, Byzantine Agreement and Multiparty Computation | d70cb1eb8261f818cedc18492ff09d4fdbd9c84f | 书目级，正文判断另见N01–N16 |
| F04 | 2010 | Lower Bounds for Round and Communication Complexities of Unconditional Verifiable Secret Sharing | 647be8ddd48f661f78c9898de0c5252628779135 | 书目级，正文判断另见N01–N16 |
| F04 | 2010 | Cryptography by Cellular Automata or How Fast Can Complexity Emerge in Nature? | c4814bc105b50c0140c3763c86879aad0c810e71 | 书目级，正文判断另见N01–N16 |
| F04 | 2010 | Constructions, Lower Bounds, and New Directions in Cryptography and Computational Complexity | 0f4f30e98ef7caa009d95feb575e0faa3216fa20 | 书目级，正文判断另见N01–N16 |
| F04 | 2009 | Efficient Statistical Asynchronous Verifiable Secret Sharing and Multiparty Computation with Optimal Resilience | 5353a3e3a647d591e3667d29b423151fa25e535d | 书目级，正文判断另见N01–N16 |
| F04 | 2009 | A Novel Unconditionally Secure Oblivious Polynomial Evaluation Protocol | 7e8f05097d26c7aff849f40227ed3d6da6ac3068 | 书目级，正文判断另见N01–N16 |
| F04 | 2008 | Almost-Asynchronous MPC with Faulty Minority | 65f6e3bf019cea9ba5d13eae51f5b970046c76dc | 书目级，正文判断另见N01–N16 |
| F04 | 2007 | Expressiveness of Definitions and Efficiency of Constructions in Computational Cryptography | e0f0057c20b622e53d7b4312c974f6ce9c15d883 | 书目级，正文判断另见N01–N16 |
| F04 | 2007 | Êóùòò Ae Blockin Blockin Blockinò Blockiný Óó Åùðøø¹èöøý Óñôùøøøøóò Ûûøø ××óòò×ø Ååóööøý | c223b198b15bd28b29778de6975912014cbd4839 | 书目级，正文判断另见N01–N16 |
| F04 | 2006 | Secure two-party computation and communication | 131d4556c64de8f707ae9572d0b30195d20d9b23 | 书目级，正文判断另见N01–N16 |
| F04 | 2005 | How to Split a Shared Secret into Shared Bits in Constant-Round | e88776f94b5bd1b6c83be77270245a91f0d46c8e | 书目级，正文判断另见N01–N16 |
| F04 | 2005 | Share conversion , pseudorandom secret-sharing and applications to secure distributed computing | 96317e8e38cc956da308026e5328948ebd9d49ad | 书目级，正文判断另见N01–N16 |
| F04 | 2005 | Secure and private online collaboration | 507becf3ad08d23f3dbfef820cff0881fd353188 | 书目级，正文判断另见N01–N16 |
| F04 | 2005 | Turing Functional Ciphertext | 8baa700517aca556954db19efc6f376b4087314e | 书目级，正文判断另见N01–N16 |
| F04 | 2005 | A qos content adaptation framework for nomadic users | 10.20381/RUOR-12825 | 书目级，正文判断另见N01–N16 |
| F04 | 2004 | Cryptography in NC/sup 0/ | cf5563f7071d94a92877bbcefaf51024ebed0d59 | 书目级，正文判断另见N01–N16 |
| F04 | 2004 | Efficient Multi-Party Computation Secure Against a Faulty Minority | bfb25347503e7a4f4159cdfa6607b199d3d2bb54 | 书目级，正文判断另见N01–N16 |
| F04 | 2003 | Secure Multi-Player Protocols: Fundamentals, Generality, and Efficiency | fe48d8922128d788e66daa47127c95500ab31754 | 书目级，正文判断另见N01–N16 |
| F04 | 2003 | Title word cross-reference | a26aac6dd7ccb4b978ed592c19a04f5f800ea0ba | 书目级，正文判断另见N01–N16 |
| F04 | 2000 | Mathematisches Forschungsinstitut Oberwolfach | 9372f8e4f474a1cef4db463272491b43179325c6 | 书目级，正文判断另见N01–N16 |
| F04 | 2023 | Evaluation of Arithmetic Sum-of-Products Expressions in Linear Secret Sharing Schemes with a Non-Interactive Computation Phase | e7aee4c39bd45746e5372a372f7be8087d1418be | 书目级，正文判断另见N01–N16 |
| F04 | None | Eﬃcient NIZKs for Algebraic Sets | 0f0ff4b4b02b0c8d157c4b326a4a96422f8783f6 | 书目级，正文判断另见N01–N16 |
| F04 | None | Perfect Somewhat Homomorphic Encryption and 2-Party Computation | 68eb0a9ea2663d972958dd5f4c1f92b81c2b3aa1 | 书目级，正文判断另见N01–N16 |
| F04 | None | Perfect 2-Party Computation from Additive Somewhat Homomorphic Encryption | 5e4ea703fe55e61b3f49492286ebd4186572932e | 书目级，正文判断另见N01–N16 |

## 5. 全部HTTP请求台账

HTTP_REQUESTS.jsonl保存每次请求起止UTC时间、实际URL、状态、重定向终点、响应哈希和字节数。下表为完整索引。失败请求也保留原始错误。

| ID | 起始UTC | URL | 结果 | 原始响应 |
|---|---|---|---|---|
| D01 | 2026-11-04T08:02:37.244767+00:00 | https://iacr.org/archive/tcc2006/38760526/38760526.pdf | HTTP Error 403: Forbidden | http\D01.error |
| D02 | 2026-11-04T08:02:37.246765+00:00 | https://www.cs.columbia.edu/~tal/6261/SP20/reading/IKicalp02.pdf | HTTP 200 / application/pdf / 231421 bytes | http\D02.pdf |
| D03 | 2026-11-04T08:02:37.246765+00:00 | https://www.cs.bgu.ac.il/~beimel/Papers/Survey.pdf | HTTP 200 / application/pdf / 343208 bytes | http\D03.pdf |
| D04 | 2026-11-04T08:02:37.247767+00:00 | https://arxiv.org/pdf/2402.07613 | HTTP 200 / application/pdf / 702725 bytes | http\D04.pdf |
| D05 | 2026-11-04T08:02:38.747756+00:00 | https://eccc.weizmann.ac.il/report/2015/186/download | HTTP 200 / application/pdf / 567152 bytes | http\D05.pdf |
| D06 | 2026-11-04T08:02:39.726812+00:00 | https://eprint.iacr.org/2001/035.pdf | HTTP Error 403: Forbidden | http\D06.error |
| D07 | 2026-11-04T08:02:40.720515+00:00 | https://drops.dagstuhl.de/storage/00lipics/lipics-vol299-itc2024/LIPIcs.ITC.2024.11/LIPIcs.ITC.2024.11.pdf | HTTP Error 404: Not Found | http\D07.error |
| Q01 | 2026-11-04T08:03:53.947537+00:00 | https://dblp.org/search/publ/api?q=optimal+simulation+error+masking+statistical+distance&format=json&h=100 | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | 传输失败，无响应体 |
| Q02 | 2026-11-04T08:03:53.947537+00:00 | https://dblp.org/search/publ/api?q=statistical+distance+secret+sharing+masking&format=json&h=100 | HTTP 202 / text/html; charset=utf-8 / 3334 bytes | http\Q02.body |
| Q03 | 2026-11-04T08:03:53.948732+00:00 | https://dblp.org/search/publ/api?q=private+sparse+recovery+lower+bound&format=json&h=100 | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | 传输失败，无响应体 |
| Q04 | 2026-11-04T08:03:53.948732+00:00 | https://dblp.org/search/publ/api?q=sketch+privacy+statistical&format=json&h=100 | HTTP 202 / text/html; charset=utf-8 / 2941 bytes | http\Q04.body |
| Q05 | 2026-11-04T08:03:56.078139+00:00 | https://dblp.org/search/publ/api?q=matroid+port+entropy&format=json&h=100 | HTTP 202 / text/html; charset=utf-8 / 3307 bytes | http\Q05.body |
| Q06 | 2026-11-04T08:03:57.573241+00:00 | https://dblp.org/search/publ/api?q=ideal+secret+sharing+matroid&format=json&h=100 | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | 传输失败，无响应体 |
| Q07 | 2026-11-04T08:03:57.764703+00:00 | https://dblp.org/search/publ/api?q=projective+arc+finite+geometry+leakage&format=json&h=100 | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | 传输失败，无响应体 |
| Q08 | 2026-11-04T08:03:58.680303+00:00 | https://dblp.org/search/publ/api?q=secant+finite+geometry+privacy&format=json&h=100 | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | 传输失败，无响应体 |
| Q09 | 2026-11-04T08:04:00.449281+00:00 | https://dblp.org/search/publ/api?q=oblivious+linear+algebra+matrix+blinding&format=json&h=100 | HTTP Error 429: Too Many Requests | http\Q09.error |
| Q10 | 2026-11-04T08:04:00.450284+00:00 | https://dblp.org/search/publ/api?q=matrix+blinding+leaks+only+rank&format=json&h=100 | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | 传输失败，无响应体 |
| Q11 | 2026-11-04T08:04:00.450284+00:00 | https://dblp.org/search/publ/api?q=Arithmetic+Sketching&format=json&h=100 | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | 传输失败，无响应体 |
| Q12 | 2026-11-04T08:04:00.450284+00:00 | https://dblp.org/search/publ/api?q=Randomizing+Polynomials+statistical+randomized+encodings&format=json&h=100 | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | 传输失败，无响应体 |
| Q13 | 2026-11-04T08:04:01.549188+00:00 | https://dblp.org/search/publ/api?q=Constant-Round+Secure+Distributed+Decoding+and+HQC+Threshold+Decryption&format=json&h=100 | HTTP Error 429: Too Many Requests | http\Q13.error |
| Q14 | 2026-11-04T08:04:01.552814+00:00 | https://dblp.org/search/publ/api?q=fractional+triangle+decomposition+complete+graph+edge+weights&format=json&h=100 | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | 传输失败，无响应体 |
| Q15 | 2026-11-04T08:04:01.688770+00:00 | https://dblp.org/search/publ/api?q=inclusion+matrix+edges+triangles+inverse&format=json&h=100 | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | 传输失败，无响应体 |
| M01 | 2026-11-04T08:04:01.885681+00:00 | https://dblp.org/search/publ/api?q=Nissim+Weinreb+2006+linear&format=json&h=100 | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | 传输失败，无响应体 |
| M02 | 2026-11-04T08:04:02.908947+00:00 | https://api.semanticscholar.org/graph/v1/paper/search?query=Communication+Efficient+Secure+Linear+Algebra&limit=10&fields=title%2Cyear%2CexternalIds%2CopenAccessPdf%2Curl | HTTP Error 429:  | http\M02.error |
| D08 | 2026-11-04T08:04:02.965231+00:00 | https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITC.2024.11 | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | 传输失败，无响应体 |
| D09 | 2026-11-04T08:05:12.514882+00:00 | https://iacr.org/archive/tcc2006/38760522/38760522.pdf | HTTP Error 403: Forbidden | http\D09.error |
| D10 | 2026-11-04T08:05:12.515882+00:00 | https://link.springer.com/content/pdf/10.1007/11681878_27.pdf | HTTP 200 / application/pdf / 260358 bytes | http\D10.pdf |
| D11 | 2026-11-04T08:05:12.515882+00:00 | https://link.springer.com/content/pdf/10.1007/3-540-44647-8_7.pdf | HTTP 200 / application/pdf / 204307 bytes | http\D11.pdf |
| D12 | 2026-11-04T08:05:12.515882+00:00 | https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITC.2024.11 | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | 传输失败，无响应体 |
| F01 | 2026-11-04T08:05:13.419353+00:00 | https://api.semanticscholar.org/graph/v1/paper/DOI:10.1007/978-3-031-38557-5_6/citations?fields=title,year,externalIds&limit=1000 | HTTP 200 / application/json / 2750 bytes | http\F01.body |
| F02 | 2026-11-04T08:05:14.325592+00:00 | https://api.semanticscholar.org/graph/v1/paper/DOI:10.1109/SFCS.2000.892118/citations?fields=title,year,externalIds&limit=1000 | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | 传输失败，无响应体 |
| F03 | 2026-11-04T08:05:18.959490+00:00 | https://api.semanticscholar.org/graph/v1/paper/DOI:10.62056/ay4fvu7sf/citations?fields=title,year,externalIds&limit=1000 | HTTP 200 / application/json / 26 bytes | http\F03.body |
| A01 | 2026-11-04T08:05:19.829987+00:00 | https://export.arxiv.org/api/query?search_query=all%3A%22matroid+port%22+OR+all%3A%22arithmetic+sketching%22&start=0&max_results=30 | HTTP 200 / application/atom+xml; charset=utf-8 / 13567 bytes | http\A01.body |
| AQ01 | 2026-11-04T08:06:52.231027+00:00 | https://export.arxiv.org/api/query?search_query=all%3A%22optimal+simulation+error%22+OR+%28all%3A%22statistical+distance%22+AND+all%3Amasking%29&start=0&max_results=100 | HTTP 200 / application/atom+xml; charset=utf-8 / 5700 bytes | http\AQ01.body |
| AQ02 | 2026-11-04T08:06:57.081897+00:00 | https://export.arxiv.org/api/query?search_query=all%3A%22statistical+distance%22+AND+all%3A%22secret+sharing%22&start=0&max_results=100 | HTTP 200 / application/atom+xml; charset=utf-8 / 5002 bytes | http\AQ02.body |
| AQ03 | 2026-11-04T08:07:01.813160+00:00 | https://export.arxiv.org/api/query?search_query=all%3A%22private+sparse+recovery%22+OR+%28all%3A%22sparse+recovery%22+AND+all%3Aprivacy%29&start=0&max_results=100 | HTTP 200 / application/atom+xml; charset=utf-8 / 15552 bytes | http\AQ03.body |
| AQ04 | 2026-11-04T08:07:06.727589+00:00 | https://export.arxiv.org/api/query?search_query=all%3Asketch+AND+all%3Aprivacy+AND+all%3Astatistical&start=0&max_results=100 | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | 传输失败，无响应体 |
| AQ05 | 2026-11-04T08:07:11.345148+00:00 | https://export.arxiv.org/api/query?search_query=all%3A%22matroid+port%22+OR+%28all%3Amatroid+AND+all%3Aentropy%29&start=0&max_results=100 | HTTP 200 / application/atom+xml; charset=utf-8 / 65922 bytes | http\AQ05.body |
| AQ06 | 2026-11-04T08:07:17.517074+00:00 | https://export.arxiv.org/api/query?search_query=all%3A%22ideal+secret+sharing%22+AND+all%3Amatroid&start=0&max_results=100 | HTTP 200 / application/atom+xml; charset=utf-8 / 7886 bytes | http\AQ06.body |
| AQ07 | 2026-11-04T08:07:22.333351+00:00 | https://export.arxiv.org/api/query?search_query=all%3A%22projective+arc%22+AND+%28all%3Aleakage+OR+all%3Aprivacy%29&start=0&max_results=100 | HTTP 200 / application/atom+xml; charset=utf-8 / 787 bytes | http\AQ07.body |
| AQ08 | 2026-11-04T08:07:26.643573+00:00 | https://export.arxiv.org/api/query?search_query=all%3Asecant+AND+all%3A%22finite+geometry%22+AND+all%3Aprivacy&start=0&max_results=100 | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | 传输失败，无响应体 |
| AQ09 | 2026-11-04T08:07:30.834444+00:00 | https://export.arxiv.org/api/query?search_query=all%3A%22oblivious+linear+algebra%22+OR+all%3A%22matrix+blinding%22&start=0&max_results=100 | HTTP 200 / application/atom+xml; charset=utf-8 / 2545 bytes | http\AQ09.body |
| AQ10 | 2026-11-04T08:07:35.090925+00:00 | https://export.arxiv.org/api/query?search_query=all%3A%22matrix+blinding%22+AND+all%3Arank&start=0&max_results=100 | HTTP 200 / application/atom+xml; charset=utf-8 / 2499 bytes | http\AQ10.body |
| AQ11 | 2026-11-04T08:07:42.093596+00:00 | https://export.arxiv.org/api/query?search_query=all%3A%22Arithmetic+Sketching%22&start=0&max_results=100 | HTTP 200 / application/atom+xml; charset=utf-8 / 2462 bytes | http\AQ11.body |
| AQ12 | 2026-11-04T08:07:46.758792+00:00 | https://export.arxiv.org/api/query?search_query=all%3A%22randomizing+polynomials%22+OR+all%3A%22statistical+randomized+encodings%22&start=0&max_results=100 | HTTP 200 / application/atom+xml; charset=utf-8 / 165218 bytes | http\AQ12.body |
| AQ13 | 2026-11-04T08:08:07.844910+00:00 | https://export.arxiv.org/api/query?search_query=all%3A%22Constant-Round+Secure+Distributed+Decoding%22&start=0&max_results=100 | HTTP 200 / application/atom+xml; charset=utf-8 / 777 bytes | http\AQ13.body |
| AQ14 | 2026-11-04T08:08:12.279658+00:00 | https://export.arxiv.org/api/query?search_query=all%3A%22fractional+triangle+decomposition%22&start=0&max_results=100 | HTTP 200 / application/atom+xml; charset=utf-8 / 15944 bytes | http\AQ14.body |
| AQ15 | 2026-11-04T08:08:17.483357+00:00 | https://export.arxiv.org/api/query?search_query=all%3A%22inclusion+matrix%22+AND+%28all%3Atriangle+OR+all%3Ainverse%29&start=0&max_results=100 | HTTP 200 / application/atom+xml; charset=utf-8 / 2505 bytes | http\AQ15.body |
| D13 | 2026-11-04T08:08:22.215197+00:00 | https://doi.org/10.4230/LIPIcs.ITC.2024.11 | HTTP 200 / text/html; charset=utf-8 / 133604 bytes | http\D13.body |
| D14 | 2026-11-04T08:08:30.873254+00:00 | https://arxiv.org/pdf/2002.08108 | HTTP 200 / application/pdf / 286081 bytes | http\D14.pdf |
| F04 | 2026-11-04T08:08:36.215895+00:00 | https://api.semanticscholar.org/graph/v1/paper/DOI:10.1109/SFCS.2000.892118/citations?fields=title,year,externalIds&limit=1000 | HTTP 200 / application/json / 83948 bytes | http\F04.body |
| D15 | 2026-11-04T08:09:57.462955+00:00 | https://drops.dagstuhl.de/storage/00lipics/lipics-vol304-itc2024/LIPIcs.ITC.2024.11/LIPIcs.ITC.2024.11.pdf | HTTP 200 / application/pdf / 938968 bytes | http\D15.pdf |
| AQ04R | 2026-11-04T08:15:28.486515+00:00 | https://export.arxiv.org/api/query?search_query=all%3Asketch+AND+all%3Aprivacy+AND+all%3Astatistical&start=0&max_results=100 | HTTP 200 / application/atom+xml; charset=utf-8 / 43370 bytes | http\AQ04R.body |
| AQ08R | 2026-11-04T08:15:33.440630+00:00 | https://export.arxiv.org/api/query?search_query=all%3Asecant+AND+all%3A%22finite+geometry%22+AND+all%3Aprivacy&start=0&max_results=100 | HTTP 200 / application/atom+xml; charset=utf-8 / 787 bytes | http\AQ08R.body |
| AQ12P | 2026-11-04T08:15:38.282445+00:00 | https://export.arxiv.org/api/query?search_query=all%3A%22randomizing+polynomials%22+OR+all%3A%22statistical+randomized+encodings%22&start=100&max_results=1000 | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | 传输失败，无响应体 |
| AQ12N | 2026-11-04T08:15:42.982197+00:00 | https://export.arxiv.org/api/query?search_query=all%3A%22randomized+encoding%22+AND+%28all%3Astatistical+OR+all%3Aprivacy%29&start=0&max_results=100 | HTTP 200 / application/atom+xml; charset=utf-8 / 43588 bytes | http\AQ12N.body |
| AQ07N | 2026-11-04T08:15:47.656197+00:00 | https://export.arxiv.org/api/query?search_query=all%3Aarc+AND+%28all%3Asecant+OR+all%3Aconcurrent%29+AND+%28all%3Afinite+OR+all%3Aprojective%29&start=0&max_results=100 | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | 传输失败，无响应体 |
| AQ12PR | 2026-11-04T08:27:54.844666+00:00 | https://export.arxiv.org/api/query?search_query=all%3A%22randomizing+polynomials%22+OR+all%3A%22statistical+randomized+encodings%22&start=100&max_results=1000 | HTTP 200 / application/atom+xml; charset=utf-8 / 860864 bytes | http\AQ12PR.body |
| AQ07NR | 2026-11-04T08:28:03.255555+00:00 | https://export.arxiv.org/api/query?search_query=all%3Aarc+AND+%28all%3Asecant+OR+all%3Aconcurrent%29+AND+%28all%3Afinite+OR+all%3Aprojective%29&start=0&max_results=100 | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)> | 传输失败，无响应体 |

## 6. 强独立原创的建议口径

可表述为“在16篇已核读全文、3组前向索引集合与Q01–Q15检索分母中，尚未发现对S1–S4完整命题的直接覆盖。若干证明工具及S5属于已有结论或直接推论。优先权仍需原始几何文献、三篇port/熵原文和后续引文全文核读”。

当前支持的工作定位为受限模型中的精确极值候选。强独立密码学原创、通用支持隐私正误差下界以及同契约端到端优势，分别处于待建立状态。

本报告各“覆盖”子项的死因为可写出变量代入的既有结论，见MAPPING_UPDATE。剩余候选的存活依据为本轮检索范围与命题差异，独立推导和查无同式均不足以确立优先权。
