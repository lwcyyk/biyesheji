# 第6章 双平台撤销语义异质性的受控测量

## 6.1 测量目标与数据范围

本章考察指定认证实现中的撤销范围、观察语境和并发派生后效，目标是为配置模型的原生前提提供可追溯证据。数据来自2026年11月2日的历史测量，覆盖Keycloak 26.8.1和Casdoor 4.25.0。原生能力调查采用13个条件、每平台每条件两次重复，共52次观察。另一批576次六方法校准独立呈现。[原实证章](D:/毕业设计/research_recipe_r2/EMPIRICAL_CHAPTER_FINAL.md) [能力调查](D:/毕业设计/auth-lifecycle/docs/experiments/CAPABILITIES.md) [校准结果](D:/毕业设计/auth-lifecycle/docs/experiments/RESULTS.md)

本轮组装只复核既有文件和汇总，原生实验执行次数为0。H-A、H-B、H-AB在历史登记中仍为NOT_TESTED，其成本优势主张已退出当前论文。下述测量因此用于描述实现差异和模型边界，校准数据用于保留分母、负控制及工具链证据。[当前论文范围](D:/毕业设计/thesis_draft/TASK_SCOPE.md) [历史假设状态](D:/毕业设计/auth-lifecycle/results/experiments/pilot02/summary.json)

## 6.2 实现、夹具与环境

|层次|实际对象|证据含义|
|---|---|---|
|完整独立认证实现|Keycloak 26.8.1、Casdoor 4.25.0|真实发行、刷新、撤销、内省和管理操作|
|原生认证组件及记录|Keycloak user session及client关系，Casdoor OAuth token record|材料与原生单位匹配，结合处置效果解释G|
|自写资源与控制夹具|资源端缓存/离线JWT检查、代理门控、批准预算Gate、响应隐藏和调度屏障|声明的RP谓词或实验干预，归属与AS行为分别标记|
|有限模型与评分|L0表、独立参考、校准见证及评分器|模型一致性与观察评价，真实状态不回流方法决策|

上述分类依据已核实能力表、归档实现说明及信息隔离记录。自写RP层的缓存结果仅支持其配置中的接受谓词。[组件来源](D:/毕业设计/auth-lifecycle/docs/experiments/CAPABILITIES.md) [隔离与评分边界](D:/毕业设计/auth-lifecycle/docs/experiments/RESULTS.md)

|环境项|Keycloak|Casdoor|
|---|---|---|
|版本|26.8.1|4.25.0|
|隔离空间|专用realm l1-research|专用organization l1-study|
|客户端|l1-client-0与l1-client-1|同owner下两个测试应用对应客户端|
|授权profile|fresh password grant|fresh password grant|
|AT寿命基线|300秒|1小时|
|关键配置|刷新轮换开启，最大重用0，fullScopeAllowed=false，显式audience|JWT及应用内授权/刷新配置按锁文件|
|账户级操作|结束测试用户全部会话|把测试账户isForbidden设为true|

每次重复均使用新建自有测试用户。平台版本、配置和端点以既有环境锁为准，Casdoor账户级适配器的实际操作按R3源码审计解释。日志中令牌失活已有内省观察，令牌内部到期字段变化仍缺单独核验。[环境与拓扑](D:/毕业设计/research_recipe_r2/evidence/environment.lock.json) [原生操作修正](D:/毕业设计/research_recipe_r3/NATIVE_PREMISES.md)

## 6.3 历史测量流程与判定规则

调查流程依次创建测试用户、发行材料、核对初始账户和材料、执行指定操作或故障、读取独立见证、记录结果并处置测试主体。grant局部撤销与AT撤销条件在同一客户端建立目标及兄弟授权，共享根条件覆盖两个客户端。并发条件用屏障释放refresh(old_RT)和revoke(old_RT)，迟到条件则在撤销响应后发送刷新。[冻结协议及调用序列](D:/毕业设计/research_recipe_r2/EMPIRICAL_CHAPTER_FINAL.md) [调查源码归档](D:/毕业设计/auth-lifecycle/results/experiments/survey04/source_bundle.zip)

判断对象包括授权方内省active、离线签名与期限检查、原生记录、请求响应及未决材料。观察均绑定调用者、材料、时间和profile。RFC 7662所规定的查询者范围、RFC 7009允许的连带撤销差异和传播边界，为这些结果的解释提供规范背景。[R16/R17核验](D:/毕业设计/当前方案双报告_2026-11-03/文献核验表.json) [能力解释](D:/毕业设计/auth-lifecycle/docs/experiments/CAPABILITIES.md)

每条事件链保存run_id、序号、UTC时间、单调时钟、角色以及前项/本项摘要，材料使用摘要引用。调查源码集合摘要为`a8254f0a4a8224b3ebb786919c077f53c062e51bf0cbabaa7586719a2739b3c1`。历史审计记录核对808条调查事件和10,148条校准事件，哈希链承担归档一致性证据，部署和语义来源另有可信前提。[原始证据审计](D:/毕业设计/research_secret_recipe/EVIDENCE_AUDIT.json) [原实证章§3](D:/毕业设计/research_recipe_r2/EMPIRICAL_CHAPTER_FINAL.md)

## 6.4 行为矩阵

|原始条件|Keycloak观察|Casdoor观察|契约含义与范围|
|---|---|---|---|
|局部RT撤销|目标AT/RT为false，兄弟AT/RT为true|相同|fresh-grant条件下的即时独立处置证据|
|AT撤销|AT为false，RT为true|AT/RT均false|相同操作名具有不同连带效果|
|账户共享根处置|结束用户会话，跨客户端材料失活|禁用账户，跨客户端材料失活|管理动作、副作用和后续登录范围分别解释|
|查询者受限active|发行客户端true，另一客户端false|当前同owner配置下两者true|查询者语境影响观察|
|内省缓存|AS已false，RP缓存暂true|相同|缓存属于自写RP层|
|核验副作用|密码认证式核验新增user session，随后内省未新增该类记录|新增OAuth token record，随后内省未新增该类记录|核验可创建真实材料，副作用类型不同|
|强停止目标不支持|账户处置后在线false，旧AT离线签名/期限仍通过|相同|到期前、指定离线RP谓词的R边界|
|批准撤回|发送前阻止stop，材料仍活跃|相同|实验授权层干预|
|响应丢失|方法未取得结果，服务器已创建材料|相同|未知句柄和处置义务须保留|
|迟到刷新|已测序列拒绝刷新|相同|特定响应后发送顺序的样本|
|并发刷新与旧RT撤销|一次刷新成功后新AT失活，另一次刷新被拒绝|一次刷新被拒绝，另一次成功且新AT活跃|实际发生的不同后效，当前只有两次重复|
|可观察语义漂移|关闭刷新重用限制后旧RT重用行为改变|寿命改为2小时后expires_in=7200|两种不同原生字段的可观察变化|
|核验后预算不足|发行和内省耗尽预算，stop被阻断|相同|核验后的合法处置可行性取决于共享预算|

本表以52行原始观察为事实来源，并采用R3对Casdoor并发与账户级动作的修正。每个单元格仅描述记录中的版本、profile和重复范围。[完整观察](D:/毕业设计/auth-lifecycle/results/experiments/survey04/observations.json) [能力表](D:/毕业设计/auth-lifecycle/docs/experiments/CAPABILITIES.md) [范围修正](D:/毕业设计/research_recipe_r3/NATIVE_PREMISES.md)

## 6.5 旧RT撤销竞争的关键轨迹

头条轨迹为survey-casdoor-concurrent_race-1。该条件针对同一旧RT并发调用刷新和撤销，客户端先收到撤销响应，再收到刷新的成功响应，随后观察到旧AT内省false、新AT内省true。共享账户根处置在另一实验分支中执行，两者按各自调用对象归档。[原事件链](D:/毕业设计/auth-lifecycle/results/experiments/survey04/survey-casdoor-concurrent_race-1.jsonl) [调用范围核对](D:/毕业设计/research_recipe_r2/REPORT.md)

|seq|客户端记录|结果|
|---|---|---|
|6|屏障释放两个HTTP请求|竞争开始|
|8|旧RT的stop发送|request_id=2|
|10|旧RT的refresh发送|request_id=3|
|11|stop响应|HTTP 200|
|12|refresh响应|HTTP 200|
|13|新材料见证|记录新AT摘要|
|14|旧AT内省|同一发行客户端，active=false|
|15|新AT内省|同一发行客户端，active=true|
|16|调查结束后处置|账户清理与删除|

表内顺序来自客户端事件。服务端事务的线性化点、新材料原生单位的独立匹配、该新AT的完整业务资源HTTP接受，在这条轨迹中仍有缺口。[逐事件来源](D:/毕业设计/auth-lifecycle/results/experiments/survey04/survey-casdoor-concurrent_race-1.jsonl) [轨迹解释](D:/毕业设计/research_recipe_r2/EMPIRICAL_CHAPTER_FINAL.md)

该轨迹反驳该profile下“旧RT revoke响应已保证全部并发派生AT在授权方内省中失活”的承诺。结论限定为R_AS观察条件，业务资源侧R需其实际验证策略和接受见证。L和E在该条件中的状态保持UNKNOWN。单条反例足以否定对应全称承诺，发生概率和调度覆盖仍由样本范围限制。[作用域判定](D:/毕业设计/research_recipe_r2/REPORT.md)

账户共享根处置后在线失活与离线JWT检查通过属于另一独立结果，针对到期前的声明离线验证谓词。共享根处置与并发刷新的组合实验尚待授权，本文仅引用已有待执行协议。[原强停止条件](D:/毕业设计/auth-lifecycle/docs/experiments/CAPABILITIES.md) [既有共享根协议](D:/毕业设计/research_recipe_r3/SHARED_ROOT_PROTOCOL.md)

## 6.6 从观察到配置理论前提

第一，原生根G需要效果与身份依据。相同字符串数量可能对应不同独立根数，当前profile通过原生记录匹配以及“撤目标、保留兄弟”的效果矩阵支持单位识别。一般SSO、跨客户端共享会话和刷新链的完整单位映射仍有边界。[G的审计](D:/毕业设计/auth-lifecycle/docs/experiments/CAPABILITIES.md)

第二，停止承诺需要说明在途材料和接受时点。旧RT竞争说明，仅列出处置时已知材料可能遗漏稍后返回的派生结果。已有并发模型把材料分区、谱系、在途请求和资源验证方式分别记入状态，未来稳定性由允许后继闭包解释。根范围静止工作已提供相关围栏和组合原理，本文采用其领域对应。[并发模型](D:/毕业设计/research_recipe_r2/CONCURRENT_CONTRACTS.md) [R15](D:/毕业设计/thesis_draft/sources/quiescence.txt)

第三，资源谱达到构造依赖原子支持转换。现有两平台调查核实了发行、刷新、内省、撤销与账户级管理操作，已测接口中尚无直接原子重绑记录。目标资格、旧支持同步退役、逐前缀可用和并发闭包需要另行符合性证据。因此测量为M_r提供公理审计，而完整谱仍按条件模型陈述。[公理—操作矩阵](D:/毕业设计/research_recipe_r3/NATIVE_PREMISES.md)

## 6.7 576次校准的完整分母

校准共288对、576次运行，六方法各96次。每方法覆盖两个实现、四个操作性资源策略家族、两个目标档、三种运行条件和两次重复。两类故障加无故障对照构成三种条件，重复账户和种子保持原统计单位。[设计与分母](D:/毕业设计/auth-lifecycle/docs/experiments/RESULTS.md)

|方法|运行数|合法完成|拒绝|UNKNOWN|TIMEOUT / INCONCLUSIVE|
|---|---:|---:|---:|---:|---:|
|A1|96|20|56|20|0 / 0|
|B-A|96|20|56|20|0 / 0|
|B|96|20|56|20|0 / 0|
|B-B|96|20|56|20|0 / 0|
|AB1|96|20|56|20|0 / 0|
|B-AB|96|20|56|20|0 / 0|
|合计|576|120|336|120|0 / 0|

表中计数来自全量运行行。另有156项未决条件，其中132项为批准撤回后未满足的停止目标，24项为声明离线策略下仍可验证的未知创建材料。零E/FA事件与这些未结条件分别解释，完成率20.83%绑定含预定诊断和不可实现条件的校准分布。[原始运行](D:/毕业设计/auth-lifecycle/results/experiments/pilot02/runs.jsonl) [评分解释](D:/毕业设计/auth-lifecycle/docs/experiments/RESULTS.md)

三组历史候选/基线主要成本均值比均为1，合法完成率差为0。A/AB查询选择和具体反馈激活次数均为0，输入属于共同已知契约负控制。方法请求合计744次，其中认证服务588次、资源/代理HTTP控制156次，含建户、复位和独立测量的原生HTTP总量为5,652次。52次调查的方法请求另为116次，其完整基础设施HTTP计量仍有缺口，两批计量分别保留。[完整成本](D:/毕业设计/auth-lifecycle/docs/experiments/RESULTS.md) [调查成本限制](D:/毕业设计/research_recipe_r2/EMPIRICAL_CHAPTER_FINAL.md)

reference02另对两实现分别比较A1与R-J，均合法完成且G=2，A1总Q=5、R-J总Q=3，认证服务请求同为3。差额来自两次重复代理门控调用。该既有反例说明安全菜单的有限进度与请求最优性是不同性质，也为移除算法成本优势主张提供证据。[R-J补充记录](D:/毕业设计/auth-lifecycle/results/experiments/reference02/runs.json) [解释](D:/毕业设计/auth-lifecycle/docs/experiments/RESULTS.md)

历史校准仅有每实现一个构造谱系，独立性获确认家族为0。原配对差分方差为0，簇bootstrap的退化描述分位数承担工具检查用途。本文保留这些负结果，确认性实验与阈值不进入当前贡献的支持链。[统计限制](D:/毕业设计/auth-lifecycle/docs/experiments/RESULTS.md) [论文范围决定](D:/毕业设计/thesis_draft/TASK_SCOPE.md)

## 6.8 有效性威胁

**外部范围。** 两实现、一个主要授权profile、每条件两次重复，支持具体版本行为的描述。授权码、普通SSO、跨owner关系及更多资源策略的普遍结论仍缺样本。本文使用“版本限定受控测量”的定位。[样本限制](D:/毕业设计/research_recipe_r2/EMPIRICAL_CHAPTER_FINAL.md)

**调度与时间。** 单机屏障控制客户端释放，线程交错、网络完成和服务器事务顺序仍有多种可能。决策步界与墙钟时限分别定义，观察到的先后次序需要按客户端证据解释。[并发边界](D:/毕业设计/research_recipe_r2/EMPIRICAL_CHAPTER_FINAL.md) [决策步语义](D:/毕业设计/auth-lifecycle/docs/SEMANTICS.md)

**测量与构念。** active、签名有效、真实业务接受和后续效果分别属于不同谓词。自写RP缓存、批准Gate和传输故障均标明组件归属，观察值只支撑其声明范围。Casdoor账户动作的令牌到期字段变化保留未核验状态。[能力与组件](D:/毕业设计/auth-lifecycle/docs/experiments/CAPABILITIES.md) [R3修正](D:/毕业设计/research_recipe_r3/NATIVE_PREMISES.md)

**来源与复现。** 原始日志、源码包和环境锁支持版本可追踪性，哈希本身无法建立部署真实性。真实令牌、UUID及墙钟时间可随运行改变，并发调度也未承诺逐字节重放。数据二次分析与确定性离线核对按各自规则复现。[复现限制](D:/毕业设计/auth-lifecycle/docs/experiments/RESULTS.md)

## 6.9 本章小结

本章形成两平台的行为矩阵、关键竞争轨迹及其配置含义。测量结果把抽象资源理论的独立根、效果闭包和原子重绑前提连接到具体服务操作，并揭示尚需符合性证据的部分。经验贡献限定在已记录版本和profile内，与第4章条件性资源谱共同支撑当前论文定位。[原生前提总结](D:/毕业设计/research_recipe_r3/NATIVE_PREMISES.md) [当前贡献](D:/毕业设计/thesis_draft/chapters/00_CONTRIBUTIONS.md)
