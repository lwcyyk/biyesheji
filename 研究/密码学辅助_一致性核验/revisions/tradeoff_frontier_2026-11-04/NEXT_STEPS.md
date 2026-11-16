# 下一阶段进入条件与增量获取清单

2026-11-04。本轮结论由来源核验、定向全文映射和T1手工论证构成。16篇全文来源中包含12篇指定论文，另有3组被引API集合和15组Q矩阵检索结果。总体优先权仍为未决。

## 1. 当前已经交付

| 交付 | 文件 | 状态 |
|---|---|---|
| 来源、哈希、页数、版本 | SOURCES_LEDGER.md / SOURCES.json | 完成实际到件登记，12篇预期论文已补齐 |
| 逐篇正文定位与变量映射 | MAPPING_UPDATE.md | 完成指定问题的定向核读，3篇port/熵原始版本继续排队 |
| S1–S5判定和检索分母 | SEARCH_CLOSURE.md / SEARCH_DATA.json | 有分母的受限判定，前向原文覆盖未闭合 |
| T1形式化、证明与反例 | TRADEOFF_FRONTIER.md | 总状态OPEN，三个子模型分别裁决 |
| 机器可读状态 | VERDICT_UPDATE.json | 与报告范围绑定 |
| 原始请求和复现工具 | HTTP_REQUESTS.jsonl、http、readings、evidence_tools.py、compile_search.py | 已保留原始响应、提取文本与预检结果 |

## 2. 优先处理的理论缺口

### 2.1 先固定同一个功能

下一轮先写一页理想功能，指定E看什么、R收到什么、支持是否向R开放、R是否也必须隐藏原始幅值。成功域继续采用全部≤3支持并包含空支持。若选择部分泄漏，使用独立profile登记ℓ，且让所有基线接受同一契约。

现有δ*对应给定S后的幅值误差。完美隐藏全部支持的点态契约通过空支持锚点已经强制完整公开分布相同，误差下界应转向受限资源或近似隐私条件。首先决定可比较的资源类，再提出新猜想。

### 2.2 明确通用方法的能力

固定允许加性随机量、每列独立随机量、私密侧信息、共享零判断、MPC乘法、重试和输出长度的范围。把全部预处理计入资源。以同域、同功能、同安全模型的通用安全计算及标准加性syndrome基线作参考。

TRADEOFF_FRONTIER的§7已经表明，一部分自然的“六行/六份随机量”界来自经典线性码与平移不变性。继续研究应先排除这种直接推论，再寻找具有独立内容的极值或协议下界。

### 2.3 r5可继续接受独立审稿

审稿顺序为完整观察到核LP的双向归约、所有原始掩码分布的覆盖、对偶符号、严格互补及核边缘唯一性、S4几何端点。优先权查新与数学正确性各用独立检查表。当前本文只复查其作用域，未把历史有限证书提升为一般证明。

S1–S4保留为受限理论候选。把它们称为强独立密码学贡献，还需要同契约功能意义、清楚的先例差异以及相对通用方法的必要代价证据。

## 3. 实现前的分离门

进入任何候选机制实现前，必须同时提交下列四项及至少一个实际成立的实例。

1. 具体输入族，包含域、字典、全部允许支持与幅值范围。
2. 单一主度量及约束，特别区分公开通信、私密预处理、随机性熵、求解计算和错误概率。
3. 当前最强适用通用方法及其允许接口，列出可以被使用的标准优化。
4. 可证伪差距与必要性论证，证明该通用方法在至少一个同契约输入上需要更高代价。

本轮该门处于未通过状态。新增程序仅用于证据获取与台账整理，候选机制代码、MPC实验、性能测量和机器证明均未开始。

## 4. 给PI的增量获取清单

### 4.1 缺失材料与版本

- 三份原始被引页面存档仍缺失。现已有Semantic Scholar快照，可用于交叉核对原来的页面、抓取日期和版本聚合方式。
- N09已取得2026年CiC期刊版。旧题名的ePrint版本如需逐句比对，可补取指定日期版本。[ePrint记录](https://eprint.iacr.org/2026/514)
- Beimel已取得作者稿。如需版式级来源比对，补2011年 *Coding and Cryptology* 印刷11–46页出版者版本。当前作者稿保留为可读证据。[作者稿](https://www.cs.bgu.ac.il/~beimel/Papers/Survey.pdf)

### 4.2 优先补取原始论文

| 优先级 | 原始来源或精确题名 | 当前证据位置 | 增量目的 |
|---|---|---|---|
| P1 | Brickell–Davenport，On the Classification of Ideal Secret Sharing Schemes，1991期刊版及1990会议版 | N04参考[22]，N06参考[22] | 核对port理想性定理的原始条件和版本差异 |
| P1 | Martí-Farré–Padró，On Secret Sharing Schemes, Matroids and Polymatroids，2007/2010 | N04参考[49]，N06参考[18] | 原文核对1.5信息比门槛及熵LP范围 |
| P1 | Csirmaz，The Size of a Share Must Be Large，1995/1997 | N04参考[29] | 对比一般访问结构资源下界与T1量词 |
| P1 | Mohassel–Weinreb，Efficient Secure Linear Algebra in the Presence of Covert or Computationally Unbounded Adversaries，2008 | N05参考[40]，N02后向引用 | 完整统一通用线性代数基线。[DOI](https://doi.org/10.1007/978-3-540-85174-5_27) |
| P1 | Andoni、Nguyen、Polyanskiy、Wu，Tight Lower Bound for Linear Sketches of Moments，2013 | N05参考[3]，PDF33 | 核对全体线性草图下界的量词及适用度量 |
| P1 | Boneh等，Zero-Knowledge Proofs on Secret-Shared Data via Fully Linear PCPs，2019 | N05参考[9]，PDF33 | 对照隐藏支持的验证功能及通用通信成本 |
| P1 | Boneh等，Lightweight Techniques for Private Heavy Hitters，2021 | N05参考[10]，PDF33 | 核对隐藏稀疏输入与授权输出的协议契约 |
| P2 | Compact Zero-Knowledge Proofs of Small Hamming Weight，2018 | N05参考[19] | 核对稀疏语言私密验证的成本与泄漏契约 |
| P2 | A Local Decision Test for Sparse Polynomials，2010 | N05参考[30] | 排除稀疏判定与定位机制的既有覆盖 |
| P2 | Amplifying Randomized Encodings & Applications，arXiv2505.21442v3 | AQ12N检索题名级记录 | 优先阅读统计误差放大/消除的适用类。[当前索引入口](https://arxiv.org/abs/2505.21442v3) |
| P2 | On the Complexity of Symmetric Boolean Functions in Multiparty Private Simultaneous Messages，arXiv2610.21216v1 | AQ12N检索题名级记录 | 核对多方私密消息的资源下界，全文尚待取得。[当前索引入口](https://arxiv.org/abs/2610.21216v1) |

前三行的原始DOI仍待核实。按题名、作者、版本和所在综述书目获取，避免使用未经确认的标识。上述后两项仅凭索引进入获取队列，覆盖判定保持未决。

### 4.3 仍失败的检索

纯几何补检两次TLS失败。精确请求如下，可由PI通过可用学术网络复查。失败详情见AQ07N/AQ07NR原始日志。[arXiv检索请求](https://export.arxiv.org/api/query?search_query=all%3Aarc+AND+%28all%3Asecant+OR+all%3Aconcurrent%29+AND+%28all%3Afinite+OR+all%3Aprojective%29&start=0&max_results=100)

DBLP的Q01–Q15全部返回验证页、限流或TLS错误，完整URL已逐条列在SEARCH_CLOSURE第5节。对应arXiv检索已补齐，两库结果尚待交叉核对。S4仍需脱离privacy关键词核读有限几何原始文献，特别是割线并发计数、一般位置弧和超椭圆极值。主结论中保留该缺口。

## 5. 可复现命令

以下PowerShell命令只重建证据派生文件。联网重抓会追加新的请求时间和响应版本，应在需要更新文献快照时单独运行。

```powershell
$python = 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$study = 'D:\毕业设计\研究\密码学辅助_一致性核验\revisions\tradeoff_frontier_2026-11-04'
& $python -X utf8 -B "$study\compile_search.py"
& $python -X utf8 -B "$study\evidence_tools.py" inspect "$study\inspect_local.json"
& $python -X utf8 -B "$study\evidence_tools.py" inspect "$study\inspect_downloads.json"
& $python -X utf8 -B "$study\evidence_tools.py" inspect "$study\inspect_round2.json"
& $python -X utf8 -B "$study\evidence_tools.py" inspect "$study\inspect_round3.json"
```

可选的联网复查命令如下。先核对服务的速率限制，优先串行执行。

```powershell
& $python -X utf8 -B "$study\evidence_tools.py" fetch_serial "$study\arxiv_requests.json"
```

原始运行覆盖download_requests、search_requests、followup_requests、arxiv_requests、round3_requests、glov_request、arxiv_followup和last_retries八个请求批次。具体成功和失败以HTTP_REQUESTS.jsonl为准。

本轮证据管理校验共25项通过、0项失败，原始结果保存为VALIDATION.json。检查内容包括六份交付存在、两份工具脚本语法、16份来源哈希、40个已保存HTTP响应哈希、59个请求ID、15组检索分页、状态分母一致性，以及两份r5历史定理文件哈希。ARTIFACT_SHA256.json固定本次交付的文件哈希。该校验的范围仅为证据文件与台账一致性。

## 6. 反方审查

- 全部16篇正文仍只是有限文献样本。经典有限几何与全部前向原文的覆盖尚待核对，强原创性判断保持开放。
- 纯齐次模型中的不可能性依赖空支持、输入独立随机量和完整公开视图。允许秘密输入相关计算时应重写协议类。
- 加性反例借助私密侧信息，必须计费。它同时显示观察权限影响结论，无法用来否定一个明确排除此资源的受限定理。
- §6.2允许R恢复随机化残差z，其条件分布仅依赖S。若功能要求R连S也隐藏，接收者角色需要再次划分。
- 本轮的资源下界是标准方法的推论。增加名称、认证字段或包装层不足以改变其先例归属。
- r5表示间误差差值很小。数学极值与端到端优势各有独立验收条件。
- 59次HTTP请求、页数校验和文档一致性校验属于证据管理结果。它们无法替代密码学证明或实验隐私验证。

## 7. 与主线的边界

本目录交付保持诊断和研究性质。S1–S5、T1及代数证书的结论范围均为公开数学模型。真实认证语义、主线可撤销单元G、配置安全和AB补证决策需要各自来源与检查。本文的协议反例和文献判断均无主线执行权限。
