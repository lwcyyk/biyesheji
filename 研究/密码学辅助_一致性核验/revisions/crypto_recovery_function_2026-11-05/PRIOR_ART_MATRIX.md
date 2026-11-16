**逐目标先例核查与剩余差异**

本轮围绕恢复当前性和授权来源核读直接近邻。新增私密功能的业务职责未确认，以下比较用于检验组件和安全目标，当前没有存活候选获得原创性结论。原文读取位置、版本和哈希见evidence/READING_REGISTER.json。

| 编号、题名与年份 | 实际阅读位置与模型 | 对应变量/目标及已有结果 | 代价与真正剩余部分 |
|---|---|---|---|
| PA1，Authorization Revocation for Long-Running AI Agents: Root-Scoped Quiescence under Delegation and Asynchronous Execution，2026，v1 | Table2 A1/A3/A4/A5/A8/A9，Theorems1/2/3/5及Theorem5证明；根、来源、在途载体与接收端围栏 | root epoch对应g0/g1，A4对应来源完整性，A3/A9对应持久当前状态，A8对应独立支持重绑。定理结论均带这些条件 | 前沿、围栏和账本的实现/通信需计费；当前Casdoor与生产R尚未联合满足前提。没有可直接归属为新密码协议的剩余差距。[原文](https://arxiv.org/abs/2609.21284v1) |
| PA2，AID-Guard: Stateful Authorization for Delegated Agent Effects，2026，v1 | §II.C TCB，§IV A1—A6，§IV.C P2；可信权威存储、精确请求、未知结果与恢复 | reservation对应pending/计费，no-effect与fence约束后继。P2在受支持原生合同中保证效果唯一性 | 原生受控幂等、终态查询及fence有接口成本。内部恢复证明不会补出这些事实，当前缺口是符合性与原生能力。[原文](https://arxiv.org/abs/2608.21159v1) |
| PA3，Verifying Account Ecosystems With Graph Transformations，2026 | §6 Definitions17—20及账户/恢复图模型；供应商规则、用户与对手动作显式建模 | 账户身份对应resource，凭据/设备对应access method；完整性为AG ¬compromise，可恢复访问为AG EF access | 完整建模与状态探索计费。可恢复访问存在性与统一观察策略、B连续可用有不同量词。当前主要剩余是准确接口映射。[DOI](https://doi.org/10.1109/EuroSP68448.2026.00038) |
| PA4，Secure Untrusted Data Repository (SUNDR)，2004 | §2、§3开头、§3.2、§3.3.2；不可信服务器与有写权限的客户端，签名及抗碰撞哈希 | 客户端版本结构对应受认证历史；fork consistency限制服务器分叉后的视图合并。§3.2明确讨论离线客户端无法发现被丢弃更新以及更强一致性所需条件 | 版本结构可缓存差量，可信在线方、检查点或客户端通信有额外可用性代价。它没有给当前项目免费即时最新头。[会议全文](https://www.usenix.org/legacy/events/osdi04/tech/full_papers/li_j/li_j.pdf) |
| PA5，Memoir: Practical State Continuity for Protected Modules，2011 | §II.A—B、§III.A—C、§IV；可信模块/小量持久状态、不可信bulk storage及崩溃 | protected history summary对应恢复锚点；确定性执行与安全重放维护状态连续性。§IV给出低层到高层状态机精化的安全结果，作者使用TLA+ Proof System核验 | Basic与Opt都需比较，Opt的检查点/UPS条件计费。其确定性内部状态模型不能直接提供外部OAuth效果幂等和原生截止。[DOI](https://doi.org/10.1109/SP.2011.38) [作者全文](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/memoir.pdf) |
| PA6，Certificate Transparency Version 2.0，RFC9162，2021 | §1、§2.1.3—2.1.4、§4.10及审计接口；证书日志、STH和MMD | inclusion对应某根下成员，consistency对应两个根之间的append-only。最新STH的规范有MMD窗口，§1保留恶意log分视图信任限制 | 对数级证明不等同即时当前状态或完整原生事件。移植到批准日志需明确schema、写入责任及新鲜度来源。严格当前功能应补强基线和候选。[RFC全文](https://www.rfc-editor.org/rfc/rfc9162.txt) |

PA1的Theorem2还给出特定观察/围栏缺失条件下的不透明性边界。C02已取得枚举能力，当前不能把该条件直接套成Casdoor全接口不可实现性。完整枚举与截止的符合性仍需核验。

PA1/PA2是当前主线的两项直接近邻。PA4/PA5补上了恢复与认证存储方向的强对照，PA6约束“透明日志已经证明当前”这一可能误判。

Memoir的形式化安全结论按原文和其前提引用，本轮没有执行其TLA+证明。它排除拒绝服务，单点R停机时B的持续可用性仍需单独合同。SUNDR官方PDF可取得并提取正文，但结构预检因PDF加密标记返回UNAVAILABLE，故本轮只使用章节定位，不将PDF页码标为已核准。Memoir的PDF结构预检PASS。两个原始PDF均保留哈希。

**按目标拆开的覆盖判断如下。**

| 待审查子主张 | 结论 | 证据与未决边界 |
|---|---|---|
| 加签名/AEAD即可从旧快照判断当前批准 | 能力前提不足 | Memoir的问题定义和安全机制直接区分认证与当前性；F0的双历史论证保留该边界 |
| 恢复后保持历史与批准单调是一项新安全目标 | 已有直接近邻 | PA1 A3/A9、PA5状态连续性。特殊新构造的成本仍需另外证明 |
| 分叉一致性等于全局即时最新状态 | 能力前提不足 | PA4 §3.2与PA6的信任/MMD条件 |
| 来源签名和当前批准签名分别有效即可证明同一材料归属 | 关系不足 | 同一rid/material/approval绑定仍需检查，正确规范关系与本地组合可以承担 |
| 本地恢复安全可以推出外部HTTP效果唯一 | 能力前提不足 | PA2提供方合同与PA5内部状态机边界不同 |
| R已有全部输入时还必须采用私密展示 | 需求不足 | 研究者未确认独立受限验证职责，G0直接检查适用 |
| 新非撤销匿名证明或累加器有必要 | 证据未决/需求不足 | 发行/持有/验证职责未冻结；原文获取尚未完成，未据摘要判覆盖 |
| 现有标准组合在已实例化前提下仍无法达到目标 | 证据未决 | 当前没有满足全部前提的反例，也没有严格资源差距实例 |

**其他目录的处理。**

DPoP、mTLS、撤销和内省沿用上一轮已取得的RFC6750/7009/7662/8705/9449/9700及对应实现范围。它们服务于原生凭据和接收规则，新增本地批准代次需要实际消费接口。

普通ZK和恶意MPC只有在受限披露功能成立后才进入完整协议比较。现有DECO/GTP、Vega和rZK读本保留为该类比较资产，当前未把它们重新定义为新的需求。可撤销匿名凭据/动态累加器本轮只进行了原文发现请求，429失败后保持待核，当前没有完整来源支持的覆盖裁决。

**本轮检索分母。**

新增公开HTTP请求共6次，其中5次取得响应体、1次失败。取得SUNDR全文、Memoir作者页及全文、RFC9162全文和Memoir的Crossref元数据。两项题名查询分别为Memoir及Dynamic Accumulators and Application to Efficient Revocation of Anonymous Credentials，后一项返回429。Memoir题名查询取前3条，正确DOI为10.1109/SP.2011.38。HTTP日志位于evidence/HTTP_REQUESTS_01.json与02.json。

实际新增定向正文核读为2篇论文和1份标准，另重核3项本地直接近邻。其余目录按适用性和原文状态保留。本轮没有基于有限检索宣称首次证明或不存在先例。
