# 原创优先权矩阵与检索分母

2026-11-04，Asia/Shanghai。判断单位为具体子主张。全文取得、定向核读和完整证明复核分别登记。未取得全文的来源只用于定位后续材料。标准组件已覆盖与整个新应用功能已覆盖分别判断。

## 1. 已核读的直接先例

| 编号与来源 | 版本及实际核读位置 | 原文结果与变量映射 | 对候选的判定及剩余问题 |
|---|---|---|---|
| P01，Zhang等，DECO: Liberating Web Data Using Decentralized Oracles for TLS，2020 | 本地arXiv1909.00938v4，§3.2 Figure1/Definition3.1，§4.3 Theorem4.1，§5.2 Definition5.1 | P映射独立材料持有者O，S映射真实来源I，Query(θ)映射绑定私密凭据的请求，Stmt(R)映射输出谓词。静态恶意且可中止，包含查询/响应来源与上下文完整性。AES-GCM需密钥承诺 | A的同源、同上下文私密证明子项已有覆盖。P0隐藏结果、当前批准及恢复权威需另外组合。本地R全知的事实削弱应用必要性。[原文](https://research.chain.link/deco.pdf) [DOI](https://doi.org/10.1145/3372297.3417239) |
| P02，Xie、Yang、Wang、Yu，Lightweight Authentication of Web Data via Garble-Then-Prove，2024 | USENIX会议全文，§2.2 Figure1，§3.2.1—3.2.2，§4.2写操作及依赖响应的多轮限制。扩展版2023/964全文获取失败 | FAuthData的cid绑定同一Q/R，轻量计算输出与承诺输入通过事后ZK连接。FGP2PC要求相应秘密最终可向证明者释放，写操作使用更强noerr条件 | “轻量计算再证明正确性”已有直接构造，不能作为B的新原理。其选择性错误处理面向TLS秘密和接口，尚无到PSCD精确D_V分布的完整归约。扩展证明细节未核完。[会议全文](https://www.usenix.org/system/files/usenixsecurity24-xie-xiang.pdf) [扩展版](https://eprint.iacr.org/2023/964) |
| P03，Kaviani、Setty，Vega: Low-Latency Zero-Knowledge Proofs over Existing Credentials，2026 | MSR元数据日期2026/05/01，本地作者稿§2.1、§6.1.3—6.2和官方prep文档 | 静态W_shared含凭据和签名检查，动态w含nonce/设备验证/日期，复用承诺逐次重新随机化。正文相关ZK解释依NovaBlindFold的honest-verifier性质 | A的静态昂贵部分复用与新展示绑定已有近邻。完整恢复祖先隐藏、安全擦除及当前状态仍需游戏映射，不能自动声称覆盖这些扩展。[作者入口](https://www.microsoft.com/en-us/research/publication/vega-low-latency-zero-knowledge-proofs-over-existing-credentials/) |
| P04，Canetti、Goldreich、Goldwasser、Micali，Resettable Zero-Knowledge，2000 | 作者修订稿§4.1 Definition4.1，作者页勘误 | P_(i,j)对应共同输入、见证及固定随机带的incarnation。对手可复现前缀并交错调用。勘误要求共同输入序列具有不同字符串 | 恢复固定随机带的ZK目标已有经典模型。隐藏缓存祖先游戏若改变对手已知索引或公开语句，需要明确归约，当前未据此确认新定义。[作者稿及勘误](https://www.wisdom.weizmann.ac.il/~oded/p_cggm.html) |
| P05，Zhu、Wang，Authorization Revocation for Long-Running AI Agents: Root-Scoped Quiescence under Delegation and Asynchronous Execution，2026 | arXiv2609.21284v1，本地全文A1/A3/A8/A9及Theorem5证明，本轮在线标题版本再确认 | root epoch对应批准代次，cut/fence对应接收边界，A3/A9要求可信单调状态及恢复不回滚，完整支持记录缺失形成unknown | 单纯新增epoch、签名谱系与恢复单调性已在直接近邻前提内。原生接口能否满足这些前提仍开放，这个缺口本身没有产生新密码协议。[固定版本](https://arxiv.org/abs/2609.21284v1) |
| P06，Tong、Dai、Guo，AID-Guard: Stateful Authorization for Delegated Agent Effects，2026 | arXiv2608.21159v1，§II.C TCB，§IV A1—A6，§IV.C P2，本轮在线标题版本再确认 | 当前授权由线性化存储和防回滚时间维护，未知效果保留reservation，恢复需无效果证据、delivery fence和唯一后继 | 当前状态与精确请求绑定、未知结果和恢复围栏已有明确条件组合。跨原生提供方的符合性仍需实际接口和事件，当前PSCD并未提供这些事实。[固定版本](https://arxiv.org/abs/2608.21159v1) |
| P07，Lodderstedt等，OAuth 2.0 Token Revocation，2013 | RFC7009，§2.1—2.2、§5 | 单token撤销、同grant的条件级联、200对已无效token也适用及传播边界 | 明确来源证明究竟证明哪一条响应事实。对全派生闭包的扩写缺少依据。[RFC全文](https://www.rfc-editor.org/rfc/rfc7009.txt) |
| P08，Richer，OAuth 2.0 Token Introspection，2015 | RFC7662，§2、§2.2、§4 | active与查询资源、时间和AS适用检查相关，缓存带来新鲜度权衡 | 证明某次active响应不等于证明任务授权、整个撤销族或将来的接受结果。[RFC全文](https://www.rfc-editor.org/rfc/rfc7662.txt) |

P01—P06为6篇论文全文的定向核读，P07—P08为2份标准原文。两篇2026预印本按作者条件结果使用。所有原文哈希、版本和阅读范围列于evidence/PRIMARY_READING_REGISTER.json。Vega官方文档和rZK勘误是附属一手技术资料，单独保留其出处。

## 2. 已核实存在、全文仍缺的来源

| 编号 | 题名、年份及入口 | 当前取得等级 | 待核问题 |
|---|---|---|---|
| P09 | Abram、Damgård、Scholl、Trieflinger，Oblivious TLS via Multi-party Computation，2021。[DOI](https://doi.org/10.1007/978-3-030-75539-3_3) [ePrint](https://eprint.iacr.org/2021/318) | Crossref、OpenAlex、大学页面及作者发表表相符。Springer的PDF URL返回HTML，ePrint为403 | 客户端秘密分配、输出接收者、恶意模型、TLS源事实及与F_A/F_B的保真映射 |
| P10 | Keller、Orsini、Scholl，MASCOT: Faster Malicious Arithmetic Secure Computation with Oblivious Transfer，2016。[DOI](https://doi.org/10.1145/2976749.2978357) [ePrint](https://eprint.iacr.org/2016/505) | 元数据及作者页已核实，本轮原文403。现有项目有底座和运行工件 | 特定F_B完整实例的联合随机性、偏置、中止及σ核算。运行工件没有替代该组合证明 |
| P11 | Fiore、Tucker，Efficient Zero-Knowledge Proofs on Signed Data with Applications to Verifiable Computation on Data Streams，2022。[DOI](https://doi.org/10.1145/3548606.3560630) [作者提供全文入口](https://eprint.iacr.org/2022/1393) | Crossref与作者发表表相符，全文403 | 已签名流的同源关系、更新、聚合/预计算、动态状态及准确成本，是否直接覆盖A的潜在增强 |
| P12 | ZEXE: Enabling Decentralized Private Computation，2020。[DOI](https://doi.org/10.1109/SP40000.2020.00050) [ePrint线索](https://eprint.iacr.org/2018/962) | DOI标题元数据已核实，全文与项目入口均未成功取得 | 私密状态消耗与防重复使用怎样依赖外部账本，哪些资源可公平提供给恢复方案 |

Nova和Cleve硬币翻转论文的本轮查询未闭环，留在检索台账中，当前不承担覆盖结论。Vega正文对NovaBlindFold的引用只用于准确说明Vega已读部分的证明依赖。

## 3. 子主张裁决

| 子主张 | 判定 | 依据与剩余差异 |
|---|---|---|
| A-source，同源材料与上下文私密证明 | 已有结果直接覆盖主要子项 | DECO/GTP。完整当前授权功能还需权威状态 |
| A-cache，静态材料预计算并新鲜展示 | 已有直接近邻，通用组合可采用 | Vega。恢复游戏的完整归约仍需条件核对 |
| A-current，从旧有效状态产生当前新鲜性 | 候选陈述在无外部新鲜输入时不成立 | E2反例，P05/P06明确外部状态前提 |
| A-wrapper，承诺、加密结果、ZK、当前状态组合 | 当前写法为直接组合，独立主贡献淘汰 | 与明确G6逐操作相同。未来专用协议的可能性未被此结论排除 |
| A-application，R已知输入时必须用私密证据 | 当前需求未成立 | 用户确认与G0功能实现，未提出委托计算瓶颈 |
| B-membership，合法掩码证明推出正确采样 | 被反例证伪 | E3固定M0合法且直接泄漏单支持幅值 |
| B-joint，从诚实隐藏份额得到联合均匀币 | 基础概率事实及标准组合起点 | 不含目标采样、选择性中止和恢复的完整证明 |
| B-distribution，恶意完整协议仍达到目标D_V | OPEN | 尚无专用协议及完整模拟，GTP/OTLS到本合同的归约未建立 |
| B-cost，严格低于最强恶意MPC | OPEN，分离门未过 | 缺具体上界、强G计费及手算差距实例 |
| G4-stream，同域k-wise非零基线补全 | 正确性手工推导，按强基线应用登记 | 有限阶独立与逐坐标函数的直接组合。原创性主张为0 |

上述判断没有使用摘要级材料判定某个完整候选“已覆盖”或“未覆盖”。当前没有一项被登记为强独立原创已成立。

## 4. 可复核检索分母

本轮使用脚本HTTP。完整日志位于evidence/HTTP_SEARCH_02.json及HTTP_SOURCE_01至06.json。第一次12个请求的日志输出因本地GBK编码失败中断，已有响应体以attempt01保留，HTTP状态未完整恢复。随后相同12组请求重新执行，原失败另记HTTP_SEARCH_01_INTERRUPTED.json。

可完整审计的HTTP请求尝试共38次，其中21次取得响应体、17次失败。另有上述12次首次尝试的部分状态。取得响应体包含HTML、API元数据和标准文本，不能等同取得论文全文。未使用浏览器自动化，未发起原生认证服务请求。

| 查询编号 | 数据库与关键词 | 本次执行结果及有效用途 |
|---|---|---|
| Q01 | Crossref，Oblivious TLS | 返回5项，首项匹配 |
| Q02 | Crossref，Lightweight Authentication of Web Data via Garble-Then-Prove | 返回5项但无正确命中，使用已有会议全文 |
| Q03 | Crossref，DECO Liberating Web Data Using Decentralized Oracles for TLS | 返回5项，首项匹配DOI |
| Q04 | Crossref，Vega Low-Latency Zero-Knowledge Proofs over Existing Credentials | 429，改用已有MSR官方页面和作者全文 |
| Q05 | Crossref，Zexe Enabling Decentralized Private Computation | 返回5项，首项匹配 |
| Q06 | Crossref，Nova Recursive Zero-Knowledge Arguments from Folding Schemes | TLS连接失败 |
| Q07 | Crossref，MASCOT Faster Malicious Arithmetic Secure Computation with Oblivious Transfer | 返回5项，DOI与作者发表表确认 |
| Q08 | Crossref，Limits on the Security of Coin Flips when Half the Processors Are Faulty | TLS连接失败 |
| Q09 | Crossref，verifiable stateful computation zero knowledge rollback recovery | 返回5项，定位到Fiore–Tucker已签名数据原文 |
| Q10 | Crossref，zero knowledge authenticated data freshness revocation private output | 返回5项，仅作为发现线索 |
| Q11 | arXiv API，精确短语Oblivious TLS | 成功返回，条目为0 |
| Q12 | Semantic Scholar API，Oblivious TLS | 429 |
| Q13/N07 | Bing RSS，精确题名加pdf | 响应成功，10项均为无关词典/娱乐结果，相关有效命中0 |

七组成功的Crossref查询共返回35个元数据候选条目，逐组最多5条，存在截断，未视为35篇已读全文。OpenAlex用于两项DOI位置查证，一项成功、一项连接失败。原文获取采用已观察到的作者页面链接、标准官方入口和明确登记的镜像探测。当前分母支持对列明子主张的判断，独立优先权检索的穷尽性尚未建立。

## 5. 给PI的增量原文清单

优先取得P11全文及其状态/更新模型，其次为P09全文和P02扩展版的FGP2PC/noerr完整证明。若主线新事实确立F_B需求，再补P10的完整安全及具体成本核验。P12仅在真实私密状态/消费账本需求出现后提升优先级。

收尾已纳入ci01的真实userinfo、refresh及应用凭据枚举有限见证，见evidence/CI01_CLOSURE_AUDIT.json。本轮剩余最能改变总体判断的输入是生产RT交付及不可绕过中介边界。原文取得可以改变某一技术子项的归属，无法替代已经缺失的真实功能需求。
