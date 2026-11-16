# 本轮检索台账

2026-11-04。所有请求均由脚本HTTP执行。题名和摘要仅用于发现全文，覆盖判定以SUICIDE_REVIEW的正文定位为依据。

```json
{
  "http_requests": 20,
  "arxiv_successful_query_groups": 9,
  "retrieved_records": 60,
  "unique_arxiv_records": 58,
  "new_fulltexts": 6,
  "legacy_sources_verified": 16,
  "failed_requests": 5
}
```

## 关键词组

| ID | 实际检索式 | 已取/总数 |
|---|---|---|
| TQ01 | `all:"ramp secret sharing" AND (all:entropy OR all:bound OR all:information)` | 29/29 |
| TQ02 | `all:"leakage resilient" AND all:"secret sharing"` | 13/13 |
| TQ03 | `all:"k-wise independent" AND (all:polynomial OR all:"orthogonal array")` | 16/16 |
| TQ04 | `all:"statistical distance" AND all:"coset" AND all:"secret sharing"` | 0/0 |
| TQ05 | `all:"linear randomized encoding" AND all:privacy` | 0/0 |
| TQ06 | `all:"homogeneous" AND all:"perfect secrecy"` | 0/0 |
| TQ07 | `ti:"weight" AND ti:"MDS" AND ti:"enumerator"` | 1/1 |
| TQ08 | `all:"minimax" AND all:"invariant" AND all:"total variation"` | 1/1 |
| TQ09 | `all:"statistical privacy" AND (all:"nonzero" OR all:"non-zero")` | 0/0 |

所有检索组已取回接口声明的全部记录。零结果仅反映当前索引与检索式。原始结果和哈希位于http与HTTP_REQUESTS.jsonl。

## 完整请求索引

| ID | URL | 状态 | 保存响应 |
|---|---|---|---|
| TQ01 | https://export.arxiv.org/api/query?search_query=all%3A%22ramp+secret+sharing%22+AND+%28all%3Aentropy+OR+all%3Abound+OR+all%3Ainformation%29&start=0&max_results=100 | 200 | http\TQ01.body |
| TQ02 | https://export.arxiv.org/api/query?search_query=all%3A%22leakage+resilient%22+AND+all%3A%22secret+sharing%22&start=0&max_results=100 | 200 | http\TQ02.body |
| TQ03 | https://export.arxiv.org/api/query?search_query=all%3A%22k-wise+independent%22+AND+%28all%3Apolynomial+OR+all%3A%22orthogonal+array%22%29&start=0&max_results=100 | 200 | http\TQ03.body |
| TQ04 | https://export.arxiv.org/api/query?search_query=all%3A%22statistical+distance%22+AND+all%3A%22coset%22+AND+all%3A%22secret+sharing%22&start=0&max_results=100 | 200 | http\TQ04.body |
| TQ05 | https://export.arxiv.org/api/query?search_query=all%3A%22linear+randomized+encoding%22+AND+all%3Aprivacy&start=0&max_results=100 | 200 | http\TQ05.body |
| TQ06 | https://export.arxiv.org/api/query?search_query=all%3A%22homogeneous%22+AND+all%3A%22perfect+secrecy%22&start=0&max_results=100 | 200 | http\TQ06.body |
| TM01 | https://api.semanticscholar.org/graph/v1/paper/search?query=Security+of+ramp+schemes&limit=5&fields=title%2Cyear%2CexternalIds%2CopenAccessPdf | HTTP Error 429:  | http\TM01.error |
| TM02 | https://api.semanticscholar.org/graph/v1/paper/search?query=Secret+sharing+system+using+a+k+L+n+threshold+scheme&limit=5&fields=title%2Cyear%2CexternalIds%2CopenAccessPdf | HTTP Error 429:  | http\TM02.error |
| TM03 | https://api.semanticscholar.org/graph/v1/paper/search?query=Strongly+secure+ramp+secret+sharing+schemes+for+general+access+structures&limit=5&fields=title%2Cyear%2CexternalIds%2CopenAccessPdf | HTTP Error 429:  | http\TM03.error |
| TD01 | https://arxiv.org/pdf/cs/0506065v1 | 200 | http\TD01.pdf |
| TD02 | https://arxiv.org/pdf/2403.10676v1 | 200 | http\TD02.pdf |
| TD03 | https://arxiv.org/pdf/2405.04622v1 | 200 | http\TD03.pdf |
| TD04 | https://arxiv.org/pdf/0801.0059v3 | 200 | http\TD04.pdf |
| TD05 | https://link.springer.com/content/pdf/10.1007/3-540-39568-7_20.pdf | 200 | http\TD05.pdf |
| TD06 | https://onlinelibrary.wiley.com/doi/pdf/10.1002/ecja.4410690906 | HTTP Error 403: Forbidden | http\TD06.error |
| TD07 | https://onlinelibrary.wiley.com/doi/pdf/10.1002/j.1538-7305.1949.tb00928.x | HTTP Error 403: Forbidden | http\TD07.error |
| TQ07 | https://export.arxiv.org/api/query?search_query=ti%3A%22weight%22+AND+ti%3A%22MDS%22+AND+ti%3A%22enumerator%22&start=0&max_results=50 | 200 | http\TQ07.body |
| TQ08 | https://export.arxiv.org/api/query?search_query=all%3A%22minimax%22+AND+all%3A%22invariant%22+AND+all%3A%22total+variation%22&start=0&max_results=50 | 200 | http\TQ08.body |
| TQ09 | https://export.arxiv.org/api/query?search_query=all%3A%22statistical+privacy%22+AND+%28all%3A%22nonzero%22+OR+all%3A%22non-zero%22%29&start=0&max_results=50 | 200 | http\TQ09.body |
| TD08 | https://arxiv.org/pdf/cs/0505054v1 | 200 | http\TD08.pdf |

## 返回书目

下列元数据用于显示检索分母，正文已核读的6篇另在SOURCES_LEDGER登记。其余条目保留未核读状态。

| 查询 | 题名 | 原文入口 |
|---|---|---|
| TQ01 | Quantum Strongly Secure Ramp Secret Sharing | http://arxiv.org/abs/1404.5749v3 |
| TQ01 | Considerate Ramp Secret Sharing | http://arxiv.org/abs/2412.17987v4 |
| TQ01 | On asymptotically good ramp secret sharing schemes | http://arxiv.org/abs/1502.05507v7 |
| TQ01 | Coding Theoretic Construction of Quantum Ramp Secret Sharing | http://arxiv.org/abs/1405.0149v5 |
| TQ01 | Strongly secure ramp secret sharing schemes for general access structures | http://arxiv.org/abs/cs/0506065v1 |
| TQ01 | Quantum ramp secret sharing from Haar scrambling | http://arxiv.org/abs/2512.00970v1 |
| TQ01 | Strongly Secure Quantum Ramp Secret Sharing Constructed from Algebraic Curves over Finite Fields | http://arxiv.org/abs/1410.5126v1 |
| TQ01 | New Asymptotic Metrics for Relative Generalized Hamming Weight | http://arxiv.org/abs/1404.0434v1 |
| TQ01 | Secure Distributed Storage: Optimal Trade-Off Between Storage Rate and Privacy Leakage | http://arxiv.org/abs/2403.10676v1 |
| TQ01 | Classical Access Structures of Ramp Secret Sharing Based on Quantum Stabilizer Codes | http://arxiv.org/abs/1811.05217v7 |
| TQ01 | Refined analysis of RGHWs of code pairs coming from Garcia-Stichtenoth's second tower | http://arxiv.org/abs/1511.06230v1 |
| TQ01 | Message Randomization and Strong Security in Quantum Stabilizer-Based Secret Sharing for Classical Secrets | http://arxiv.org/abs/1904.11114v3 |
| TQ01 | Relative generalized Hamming weights of one-point algebraic geometric codes | http://arxiv.org/abs/1403.7985v3 |
| TQ01 | Secret Sharing with Binary Shares | http://arxiv.org/abs/1808.02974v3 |
| TQ01 | Relative Generalized Hamming Weights of Cyclic Codes | http://arxiv.org/abs/1505.07277v1 |
| TQ01 | Detecting Algebraic Manipulation in Leaky Storage Systems | http://arxiv.org/abs/1607.00089v2 |
| TQ01 | Improved constructions of nested code pairs | http://arxiv.org/abs/1610.06363v3 |
| TQ01 | Secret Sharing for DNA Probability Vectors | http://arxiv.org/abs/2504.18970v1 |
| TQ01 | Quantum Optimal Multiple Assignment Scheme for Realizing General Access Structure of Secret Sharing | http://arxiv.org/abs/1702.00942v1 |
| TQ01 | Entanglement Sharing Protocol via Quantum Error Correcting Codes | http://arxiv.org/abs/1212.4217v2 |
| TQ01 | On secret sharing from extended norm-trace curves | http://arxiv.org/abs/2603.14009v3 |
| TQ01 | Big Secrets Small Shares: Revisiting Secure Multi-Party Computation | http://arxiv.org/abs/2610.27609v1 |
| TQ01 | Anonymous Shamir's Secret Sharing via Reed-Solomon Codes Against Permutations, Insertions, and Deletions | http://arxiv.org/abs/2412.17003v3 |
| TQ01 | On nested code pairs from the Hermitian curve | http://arxiv.org/abs/1807.04042v3 |
| TQ01 | The weight hierarchy of decreasing norm-trace codes | http://arxiv.org/abs/2411.13375v1 |
| TQ01 | ByzSecAgg: A Byzantine-Resistant Secure Aggregation Scheme for Federated Learning Based on Coded Computing and Vector Commitment | http://arxiv.org/abs/2302.09913v4 |
| TQ01 | Discrepancy for Random Linear Codes | http://arxiv.org/abs/2606.24471v3 |
| TQ01 | Approximate degree, secret sharing, and concentration phenomena | http://arxiv.org/abs/1906.00326v1 |
| TQ01 | Leakage-Resilient Secret Sharing with Constant Share Size | http://arxiv.org/abs/2105.03074v2 |
| TQ02 | Leakage-Resilient Secret Sharing with Constant Share Size | http://arxiv.org/abs/2105.03074v2 |
| TQ02 | Leakage-Resilient Non-Malleable Secret Sharing in Non-compartmentalized Models | http://arxiv.org/abs/1902.06195v2 |
| TQ02 | Partial Derandomization for Leakage-Resilient Shamir's Secret Sharing over Composite Order Fields | http://arxiv.org/abs/2607.28757v1 |
| TQ02 | Quantum Leakage Resilience of Shamir Secret Sharing | http://arxiv.org/abs/2609.37276v1 |
| TQ02 | Improved Local Leakage Resilience of Shamir Secret Sharing and Worst-Case Optimal Polynomial Intersection | http://arxiv.org/abs/2610.12357v2 |
| TQ02 | Bounds on the Statistical Leakage-Resilience of Shamir's Secret Sharing | http://arxiv.org/abs/2405.04622v1 |
| TQ02 | Local Leakage Resilience of Shamir Secret Sharing: Below Half Threshold Rate | http://arxiv.org/abs/2610.17711v1 |
| TQ02 | Secret Sharing Despite Non-Extractable Randomness | http://arxiv.org/abs/2610.20173v2 |
| TQ02 | Thinking Inside The Box: Privacy Against Stronger Adversaries | http://arxiv.org/abs/2406.16313v1 |
| TQ02 | Repairing Reed-Solomon Codes over Prime Fields via Exponential Sums | http://arxiv.org/abs/2402.02358v1 |
| TQ02 | Simultaneous Haar Indistinguishability with Applications to Unclonable Cryptography | http://arxiv.org/abs/2405.10274v1 |
| TQ02 | On Worst-Case Optimal Polynomial Intersection | http://arxiv.org/abs/2604.09533v1 |
| TQ02 | Discrepancy for Random Linear Codes | http://arxiv.org/abs/2606.24471v3 |
| TQ03 | The Maximal Probability that k-wise Independent Bits are All 1 | http://arxiv.org/abs/0801.0059v3 |
| TQ03 | Derandomizing Chernoff Bound with Union Bound with an Application to $k$-wise Independent Sets | http://arxiv.org/abs/1608.01568v1 |
| TQ03 | Polynomial Threshold Functions: Structure, Approximation and Pseudorandomness | http://arxiv.org/abs/0911.3473v3 |
| TQ03 | Inequalities and tail bounds for elementary symmetric polynomial with applications | http://arxiv.org/abs/1402.3543v2 |
| TQ03 | Bounded Independence Fools Degree-2 Threshold Functions | http://arxiv.org/abs/0911.3389v2 |
| TQ03 | On the tightness of Tietäväinen's bound for distributions with limited independence | http://arxiv.org/abs/1707.00552v1 |
| TQ03 | Deriving differential approximation results for $k\,$CSPs from combinatorial designs | http://arxiv.org/abs/2409.03903v2 |
| TQ03 | Bounded independence for the inverse star discrepancy | http://arxiv.org/abs/2608.15865v1 |
| TQ03 | Efficient unitary designs and pseudorandom unitaries from permutations | http://arxiv.org/abs/2404.16751v2 |
| TQ03 | Universal set families for maximization of nonnegative submodular and XOS functions | http://arxiv.org/abs/2609.19528v1 |
| TQ03 | A Counterexample to the Generalized Linial-Nisan Conjecture | http://arxiv.org/abs/1110.6126v1 |
| TQ03 | Limited Independence Suffices for Large-k Min-wise Hashing | http://arxiv.org/abs/2607.10255v3 |
| TQ03 | Quantum Speedup for Graph Sparsification, Cut Approximation and Laplacian Solving | http://arxiv.org/abs/1911.07306v4 |
| TQ03 | Logspace Reducibility From Secret Leakage Planted Clique | http://arxiv.org/abs/2107.11886v2 |
| TQ03 | Pseudorandom Permutations from Random Reversible Circuits | http://arxiv.org/abs/2404.14648v4 |
| TQ03 | Improved parallel derandomization via finite automata with applications | http://arxiv.org/abs/2411.18028v3 |
| TQ07 | The Partition Weight Enumerator of MDS Codes and its Applications | http://arxiv.org/abs/cs/0505054v1 |
| TQ08 | Total Variation Regularized Fréchet Regression for Metric-Space Valued Data | http://arxiv.org/abs/1904.09647v5 |
