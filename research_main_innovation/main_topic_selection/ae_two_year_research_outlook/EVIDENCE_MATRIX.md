# 原文证据矩阵与阅读范围

OUTLOOK-1；2026-11-07。页码均为本地PDF页序，1起算。这里的“读”指模型辅助读取，研究者人工核读身份沿用历史记录。

## 1. 范围与证据强度

45份PDF共1072页，8份草案。逐篇初筛完成，直接相邻模型/前提有定点展开。下表“范围”是读过的段落所在页，通常为摘要及相关摘段；全文提取不等于全页核读。4张关键完整页已视觉核查。

新生成sources/Pxx_text.txt、Pxx_pages.json仅为阅读衍生件，原PDF仍在用户给定目录。sources/CORPUS_MANIFEST.json固定45份PDF及8份草案的原路径和SHA-256；sources/READING_SCOPE.json区分定点读取、完整页视觉复核和未重验部分。

结论等级：

- **原文事实**：源文件在定位处明确提供的模型/结论/限制。
- **原文报告**：作者给出的实验或安全结果，本轮未复现。
- **研究推断**：据前提提出的候选方向，仍需查新及验证。
- **来源限定**：身份、附录或证明范围尚有限制。

## 2. 45篇逐篇比较

|ID与材料|本轮定点范围|直接影响研究判断的内容|选题处理|
|---|---|---|---|
|P01 SUDP|第1、13页；复用既有定义/合同核查|有界secret-use、custodian不向请求者交付可重用权力；讨论审批成本、粒度、自主性和非人类authorizer|基础秘密代理已有强近邻；新贡献需超出托管|
|P02 Beyond OAuth / PAuth|第1、3–4、7–8、12–13页；§III/IV/VI|server派生NL slice，签名envelope连接运算来源；任务要求明确自含，语义不确定时回退确认|任务级参数与跨服务来源已覆盖；歧义及规格可信性单独处理|
|P03 Root-Scoped Quiescence|第1、3、31–32页；§1.4/10.3/11；复用既有范围核查|完整manifest、fence、frontier和channel accounting下给root相对闭包；opaque保持Indeterminate|闭包语义及不可观察边界已有先例；不能将“有cookie残留”直接当新空白|
|P04 ResidualAuth|第1、3–6、9页；Theorems 1–3；附录片段|未来可区分状态；一般及受父数限制的状态位数界；信息不足的平均错误下界|仅保留当前reachability不足已有证明；新压缩要保持原更新语义|
|P05 AID-Guard|第1、3–5、12页；安全模型、H1–H3、§VII|effect合同由maintainer定义，D0针对登记目录；重试、模糊结果及恢复需要provider terminality/fence|主线A直接证据；普通commit recheck/幂等lineage重叠大|
|P06 Authorization Closure Graph|第1、9–10、12页；§5/附录A.1|版本图、选择性失效、最小修复；依赖正确effect/dependency规格和认证观测|主线A/C强基线；仅引入版本依赖不够|
|P07 OASIS / OAuth Account Linking|第1、12、16、20页；§6.4/9及附录意见|40家COSF和8家OaaS问题为作者报告；静态callback启发式有漏报/误报、动态操作人工成本|主线A测量与分析近邻；本轮没有开展真实平台探测|
|P08 Verifying Account Ecosystems With Graph Transformations|第1–2、14–16页；§8.2；第15页视觉核查|RAG/图重写＋CTL；状态空间扩展、规则变化、行动建议列为后续工作|主线C直接依据；通用图模型及GROOVE已有覆盖|
|P09 Near Optimal Bayesian Active Learning for Decision Making|第1、8页；问题及结论|重叠决策区域、HEC及adaptive submodularity；原文讨论无噪声与超边规模限制|主动询问/补证的重要强基线；换场景名不构成新算法|
|P10 Safe RL via Shielding under Partial Observability|第1、7页|POMDP下shield和RL；屏蔽不自动保证快速达成目标|安全探索/屏蔽工具已存在；新授权问题需独立映射和界|
|P11 Multi-Cost-Bounded Reachability Analysis of POMDPs|第1、9页|多维上下界、cost-aware及部分cost观察、unfolding与STORM|多预算规划的强通用框架；论文已有建模能力不等于新授权贡献|
|P12 Tactics for Account Access Graphs|第1–2、17页；结论|AAG state/transitions/tactics，账号恢复与安全/可用性权衡|动态账号行为与策略程序已有基础|
|P13 CaMeL / Defeating Prompt Injections by Design|第1–2、5、23–24页|可信query控制/数据流，capability/IFC；规格维护、declassification和用户疲劳是限制|主线A/B基线；纯能力隔离或两模型规划已相邻|
|P14 DECO|第1、13页|无服务端改动的TLS来源证明及隐私断言；context integrity|网页数据真实与最小披露已有协议；不同于证明服务端无残留权力|
|P15 Lightweight Authentication of Web Data via Garble-Then-Prove|第1–2、10页|TLS来源证明的2PC/证明优化，作者报告通信和计算改进|密码学储备线先例；本轮未重验全部协议|
|P16 Privacy-preserving policy evaluation in multi-party access control|第1–2页|HE/SFE评估私有多方策略并给实验|私有策略求值已覆盖基本想法；仅加MPC较弱|
|P17 Heartbeat-Bound Hierarchical Credentials|第1、18、20、22页|heartbeat新鲜度、时钟/密钥安全前提、服务端验证；分区和clock依赖|短期/心跳层级撤销近邻；作者与OAuth比较受具体profile限制|
|P18 Vault-Mediated Execution Boundary|第1、3–6页；§6.5/9|16个定向probe；API header映射失败；redirect/refresh/browser等未覆盖|主线A有直接部署证据；拓展测试清单需要方法级贡献|
|P19 SAGA|第1、9页|Provider注册、联系策略、OTK及token、形式分析与架构扩展|agent身份治理和通信授权已有系统；未核其full-version附录全部证明|
|P20 Universal Cross-app Attacks|第1–2、11、14、16页|OAuth角色/应用混淆，COVScan，16/18为作者报告|跨应用安全分析已有强测量方法；新scanner须超出规则再包装|
|P21 Towards Automating Data Access Permissions in AI Agents|第1–2、11、13–14页；第14页视觉核查|用户研究、混合预测，阈值精度/覆盖；变化偏好、纠错、撤回和交互仍需研究|主线B最强直接依据；静态高置信预测已有覆盖|
|P22 Position: AI Agents Need Authenticated Delegation|第1、4、6页|OAuth/OIDC/VC混合框架，NL到结构权限再由用户核对|位置论文提供方向，不能按完成安全验证计；框架本身已有先例|
|P23 Task Shield|第1、9页|LLM判断操作对用户目标的贡献，AgentDojo实验；模型失误/调用成本限制|再加一个task-alignment判别器重叠很高|
|P24 Private Record Certification / Anonymous Credential Revocation|第1–2、4、8、15页|PIR/MPC的匿名凭证状态认证，规模实验；RA信任及主动恶意限制|隐私撤销已有高门槛结果；本轮只读模型/限制，不重验密码学|
|P25 Prompts Don’t Protect / MCP Proxy|第1、5页|ABAC过滤discovery，在作者受控条件下0违规；模型无法自强制|过滤registry与完整请求/效果强制分别比较；基本proxy已相邻|
|P26 Towards Verifiably Safe Tool Use|第1、4页，整页视觉核查第1页|STPA、mandatory labels、Alloy有界分析；开放市场元数据需可信来源|主线A直接邻居；本地稿DOI占位、模板年份冲突，发表身份待绑定|
|P27 Clinical Hypergraph Delegation|第1、6页|临床场景时间衰减和trace replay，synthetic workflow；baseline配置有影响|医疗方向需领域资源；macaroon基线未穷尽配置，不能推普遍优越|
|P28 APEX / Protocols and Formal Models for Delegated Authorisation with Server-Side Secrecy|第1、6、13、22页|RAD/加密资源委托和协议；末页将余下证明指向项目站|不可信server下加密资源已有强基线；本轮未取得/重验所有外链证明|
|P29 AgentBound|第1、5–6、18页|资源manifest、source生成、Docker enforcement；policy内语义/配置问题未覆盖|主线A基线；不能拿仅提示型防御作最强对手|
|P30 Securing Agents With Tracked Capabilities|第1、3、7、9页|Scala capture checking、local purity、能力安全的代码表达与benchmark|能力语言/静态effect safety已有直接方法；应比较可信wrapper假设|
|P31 When Lower Privileges Suffice|第1、9页|低权限替代工具、失败后升级、privilege-aware post-training；模拟与简单可替代工具前提|权限规划/训练已有结果；P42提出的成本规划实验并非全新切口|
|P32 AgentSpec|第1、11页|trigger/predicate/enforcement DSL，自动规则生成；离散checkpoint与trajectory限制|运行时规则语言已存在；trajectory空白需同时比较P39|
|P33 Audience Injection Attacks|第1、16页|多endpoint的audience/client-authentication注入及修复，提出完整形式分析方向|协议组合形式化仍可研究，但新攻击类须区别已知audience结果|
|P34 MCP Landscape|第1、15页|生命周期/16类威胁及case taxonomy|综述提供线索；taxonomy和代码案例不能代替可证创新|
|P35 AGentVLM|第1、4、11页|复杂条件/目的的policy生成＋验证；完整requirements欠缺影响质量判断|自动NL策略生成已有工作；泛化完整语义保证另需证据|
|P36 GrantBox|第1–4页相关段|真实MCP工具sandbox，request生成及privilege评估；10server等实验设置|真实工具benchmark已存在；新数据量本身较难作主贡献|
|P37 CapChain|第1、15、28页及结论相关段|shared-state reducer的字段能力/来源架构，原型实验为特定gate|共享state强制已有邻居；门触发率不等于防止泄漏率|
|P38 MCPTox|第1、7页|45server、353tool、1348case，metadata poisoning；后续自适应攻击|工具投毒benchmark已存在；需更强机制或实验辨识度|
|P39 ProbGuard|第1、10–12页|DTMC风险预测、条件性PAC讨论、主动干预；扩展规模和在线适应|“AgentSpec缺trajectory，所以加预测”已被后续覆盖；本地DOI占位|
|P40 ASTRA|第1、3、7–8页|task-to-scope matching与dataset，复杂任务精度/召回权衡|语义scope分类已经成线；更换embedding/LLM通常偏小|
|P41 CASA|第1、7–9页|确定性完整性检查＋多轮任务提取/语义匹配；单对话单tool基本设置|多轮task authorization已有近邻；组合tool语义仍需与P02等比较|
|P42 Towards Elastic Least Privilege|第1–3、9–12页|基线/包络/lease/预算/成本规划与re-baseline；自述研究议程|议程不能当完整实现，也不能忽略其概念优先；风险预算储备线|
|P43 Progent|第1、4–7、11页；第11页视觉核查|SMT比较allowed calls，monotonic confinement；初始化忠实度、用户误批存在责任|主线A/B/C组合强基线；新授权策略须超出标准narrowing|
|P44 Irreversibility Budget|第1、5–6页|fleet累计risk accounting，相关性/定价开放；实验由构造价格支撑|相关风险定价可形成大问题；短期落地/验证风险高|
|P45 Intent-Governed Tool Authorization|第1、10–12、26–28页及结论限制段|EffectSound、CertRefines前提，区分draft/path/effect；严格归一化影响utility|主线A直接依据；证书签名与置信度无法自动证明语义忠实|

## 3. 8份草案定点对照

均按本地固定编号版本使用。Internet-Draft为work in progress，其存在说明相关设计已公开，当前实施和标准化采纳分别核查。

|ID、固定版本|定点范围|已覆盖内容|剩余责任/研究提醒|
|---|---|---|---|
|D1 draft-chen-oauth-agent-revocation-01|摘要、目录、§3.3/4|按agent批量/级联撤销、状态统计、审计与权限检查|completed和tokens_revoked有明确对象；真实effect closure另验|
|D2 draft-asor-wimse-agent-delegation-chain-03|摘要、目录、§4.5/6.4/9.4|逐hop衰减、parent hash、principal不变、离线校验|syntactic scope不证明跨域语义；总budget不由每边token校验实现，草案已明确指出|
|D3 draft-mcguinness-oauth-mission-02|摘要、目录、§5.1/17.1.3/17.3.1|Mission对象、mechanical authority derivation、consent绑定、issuance lifecycle|configured lookup与narrowing已有；runtime与语义忠实仍有独立前提|
|D4 draft-liu-oauth-authorization-evidence-02|摘要、目录、§9.5/9.9/10|approval/disclosure签名、撤回与治理record|AS签名不证明实际屏幕展示/用户理解；token传播与隐私另验|
|D5 draft-thaha-wimse-agent-evidence-binding-03|摘要、目录、§5/8|AIMS/SCITT/in-toto证据绑定与逐call admission|registration receipt不证明真实性、完整性或全部活动覆盖，原文明确|
|D6 draft-sweeney-wimse-credential-delegation-02|摘要、目录、§6.2–7/10.9|DS保管与proxy exercise、consent和级联revoke|DS内失效时限与外部token/在途commit分开；DS本身受信任|
|D7 draft-reddy-wimse-oauth-dialog-binding-00|摘要、目录、§12–15|dialog的origin、完整性、sender、request/response和token绑定|dialog ID不自带权限；实际revocation依赖其他信号/强制路径|
|D8 draft-watts-oauth-agent-revocation-closure-03|摘要、目录、§10/17/18|epoch、admission fence、outstanding和UNKNOWN、closure receipt、可证伪case|完整发现所有dependency未被自动保证；通用conformance方法仍需独立查新|

## 4. 影响选题的三项直接证据链

### A. 真实工具效果合同

P26要求可信标签 → P29自动生成的是资源manifest → P05效果合同由maintainer定义、D0检查已登记路径 → P06正确性依赖正确spec → P45请求约束进一步依赖EffectSound → P18暴露一个secure-but-nonfunctional映射实例。

**推断**：从实现/接口证据建立效果合同有实质研究责任。**尚缺**：证明通用静态/动态分析与增量验证组合无法同级完成；自动契约合成的专项先例仍需核读。

### B. 偏好与用户交互

P21实证偏好与context相关，阈值降低覆盖 → P13讨论declassification疲劳 → P02对不明确任务回退确认 → P43用户误批/模糊任务影响最小权限 → P45有confidence路由但reference fidelity独立。

**推断**：长期变化与选择性反馈下的低打扰风险控制值得验证。**尚缺**：在线校准/主动学习、可用权限的专项覆盖以及真实用户研究资源。

### C. 动态授权状态

P04同reachability不同未来＋父数约束状态界 → P03独立支持反链 → P06依赖版本化 → P08规则演化与state explosion。

**推断**：保留多来源支持的结构化增量验证是理论候选。**尚缺**：一个可计算、真实较小且未被现有动态/组合算法覆盖的结构参数。

## 5. 版本与公开核对

新取证见sources/PUBLIC_RETRIEVAL.json：

- Progent：公开arXiv记录确认2504.11703，最近修订2026-05-14，v3，与本地页眉一致。只核对元数据，不把摘要页视为补读全文。
- PAuth：公开记录确认2603.17170v2，2026-08-25，与本地正文版本一致。
- IETF Mission固定版、MCP授权规范URL本轮TLS失败，保留本地固定版本证据及已有官方文档记录，不断言其后版本未变化。
- web检索服务传输错误，未据此宣称没有其他先例；本轮没有对暂停来源发请求。

P01–P18来源URL可复用原目录来源清单。P19–P45部分元数据仅由PDF本身与历史速览给出，不能统一标记为出版社正式版。P28末页明确有部分证明外链，当前比较限定已读部分。

## 6. 方法与复核状态

这是有边界的语料阅读与研究机会评估，未采用PRISMA式全库检索；没有执行新安全机制、参考实现、solver、数学穷尽、真实账号测试或LLM实验。统计数字作为原文报告，所有候选的性能目标作为待验证主张。

研究责任与工程责任分别登记；未来正式开题需完成目标候选的专题先例表、独立的真实需求证据，以及用户规定的可证伪分离声明。

