# 当前裁决 DCL-R6-Envelope

2026-11-10。[最终裁决](DCL-R6-Envelope/FINAL_DECISION.md)、[后端对照](DCL-R6-Envelope/RESOURCE_BACKEND_COMPARISON.md)、[资源证明](DCL-R6-Envelope/STRICT_MEMORY_BOUND_PROOF.md)。

|Gate|状态|边界|
|---|---|---|
|E1 方案可行性|CONDITIONAL_PASS|三路线具体审查；选 C，实际平台待核|
|E2 原严格资源证明|UNRESOLVED|Windows 全生命周期/峰值窗口未闭合；cgroup charge 和暂时超限无法替代原 WS|
|E3 执行架构|STATIC_DESIGN_COMPLETE_CONDITIONAL|父 slice 总任务界、角色/首入口/全部失败停止明确；尚无运行接线|
|E4 batch02准入|PARTIAL_UNAUTHORIZED|校准/顺序/结果清单已给；实际平台/runtime/适配器/全命令摘要待补|

推荐待批准 AS4-PAYLOAD/1：native Linux 每进程 AS≤1 GiB＋同批总tasks≤4，在启动映像/映射/权限/归属前提下有 payload 驻留和≤4 GiB。外部 Launcher/systemd/pre-exec helper/宿主边界与墙钟终止假设均显式修订，当前未采用。原 RESOURCE_GATE_FAILED 保留，RESOURCE_GATE_PASS 未取得；F1/F4 正式0、PASS_BOUNDED空。

本轮只读管理查询3项：WSL列表/版本、Docker固定本地端点info。三发行版均Stopped，端点连接失败；安装kernel元数据无法证明活动Linux能力。新增验证程序/校准/模型/环境启动/配置/安装均0。v1/v2/v3、原ZIP和62文件/业务五hash、27次/118.7340827秒/旧deadline保持。

D1-PBFT-SEAL/1.1、D2条件结论、强G覆盖、I1/I2/I3归档、STRICT_SEPARATION_INSTANCES=0、IMPLEMENTATION_GATE=CLOSED不变。[独立合同/授权申请](DCL-R6-Envelope/BATCH02_AUTHORIZATION_REQUEST.md)先申请有限平台 P 阶段，当前未创建batch02。

以下为历史裁决；当前状态以前置 Envelope 节为准。

---
# 当前裁决 DCL-R6-B-Repair

2026-11-10。[修复裁决](DCL-R6-Repair/FINAL_DECISION.md)、[根因审查](DCL-R6-Repair/RESOURCE_FAILURE_ROOT_CAUSE.md)、[严格界责任](DCL-R6-Repair/RESOURCE_BOUND_PROOF.md)为最新入口。

|Gate|状态|范围|
|---|---|---|
|RG-1 根因审查|CONDITIONAL_PASS|API/ABI/原日志/时窗链已审，87唯一原因与峰值内核机制仍未认证|
|RG-2 v3修复|PARTIAL|资源三文件静态修补，五业务hash一致；严格启动包络/运行接线仍缺|
|RG-3 硬资源资格|UNRUN，保持FAILED|batch01到期关闭，新批未授权，v3未执行，暂无完整硬界证明|
|RG-4 模型资格|UNRUN_RESOURCE_GATE|F1/F4未恢复，PASS_BOUNDED为空|

v3在versions/v3独立保存，batch01/src、v1/v2、原62文件/60项ZIP和27/118.7340827旧账全部保留。仅静态代码/差异审查，新增Python/校准/模型执行0。代码拒绝自动建窗和未证资源准入；当前适配器未实现，不宣称完整可运行监督器。

确认子当前内存取自释放后，父当前内存取自退出后；Job首成员进入前已设限，旧成员前占用解释缺源码支持；4KiB与页面相等仅是线索。控制器启动窗、guardian异常/独立模型入口和计数中断防护已具体化。

下一步先建立可信启动前资源包络与指标对应，再申请独立诊断批次并完整校准；[申请草案](DCL-R6-Repair/NEXT_BATCH_AUTHORIZATION.md)保留技术前置。Docker/WSL仅查到CLI，Docker as快捷方案已由官方规则排除。当前不创建/启动新环境。

协议1.1及D2纸面条件、强G覆盖/I1–I3归档、严格分离0、机制门CLOSED保持。F2/F3、Casdoor、原生/凭据、外发均未执行。

---
# 当前裁决 DCL-R6阶段B：资源门失败

2026-11-10。[R6最终裁决](DCL-R6/R6_FINAL_DECISION.md)、[资源校准报告](DCL-R6/R6_RESOURCE_CALIBRATION_REPORT.md)与[机器清单](DCL-R6/evidence/stage_B/RUN_RESULTS.json)为当前入口。专项许可已正式取得，八程序及v1/v2已保存；F1/F4未启动。

|Gate|结果|范围|
|---|---|---|
|R6-B1 资源校准|FAIL|v1 Job设置错误87；v2 normal/counter通过，memory峰值判据失败|
|R6-B2 F1|UNRUN|INV1–8、基线/变异/重放0，状态UNRUN_RESOURCE_GATE|
|R6-B3 F4|UNRUN|独立参考/DP/交叉/G64均0，状态UNRUN_RESOURCE_GATE|
|R6-B4 证据完整性|CONDITIONAL_PASS|首次失败、版本/锁/命令/校准保存；初始化前峰值及精确树WS缺测明确保留|

统一访问27次，全部校准；118.7340827秒至v2退出，计时/计数未重置。96MiB测试Job报告109.83203125MiB提交峰值，32MiB HardWS下进程峰值多4096字节。已捕获MemoryError，但峰值/硬界指标对应未闭合；不据此认定整批实际超过4GiB，也不放宽口径继续正式模型。

本批RESOURCE_GATE_FAILED并停止，正式模型反例0、原协议缺陷观察0均只因尚未验证；PASS_BOUNDED为空。D1/D2纸面条件保持，1.1未升级，LEVEL-3/4/5协议证据0，强G覆盖/I1–I3归档/严格分离0/机制实现门CLOSED维持。原生/构建/依赖下载/外发0，R1–R5冻结。

当前阻碍为资源资格，许可已批准的同范围无需重复确认。下一步先核实峰值计账与严格合成界并完整校准，再进入F1→F4。下方保留阶段A及历史裁决。

---
# 当前裁决 DCL-R6阶段A

2026-11-10。[R6最终裁决](DCL-R6/R6_FINAL_DECISION.md)及[范围](DCL-R6/R6_VERIFICATION_SCOPE.md)为当前入口。专项执行许可尚未取得；F1/F4均UNRUN_PERMISSION，模型/参考/监督程序0、模型执行0。当前已完成允许的工具/规格预审及完整待授权合同。

|Gate|结果|边界|
|---|---|---|
|R6-A 模型规格|CONDITIONAL_PASS|F1多head/独立RHO监视、INV1–8与F4双语义/有限域/夹具/G64；代码及实际覆盖待授权|
|R6-B 机器验证|UNRUN_PERMISSION|访问/峰值/耗时/反例等机器字段null，尚无PASS_BOUNDED或LEVEL-3|
|R6-C 证明责任|CONDITIONAL_PASS|D1/D2纸面条件保持，输入完整/模型非真空/真实部署与无界责任继续待证|
|R6-D 路线|PASS（决策范围）|先专项许可及资源监督校准，再F1→F4；后续F2/F3/原生独立准入|

实际工具仅确认Java8u502、Python3.14.0；当前官方TLC要求Java11+，TLC/Apalache在已查目录未发现。最小申请复用现有Python/标准库，无下载；资源硬界/工作集口径须校准。工具版本查询2次与行政哈希不计作模型运行。

拟议F1/F4单批100万访问、30分钟、4GiB进程树峰值，所有baseline/变异/参考/校准共享限额。具体八程序、写入目录和命令见[R6专项申请](DCL-R6/R6_TOOLCHAIN_AND_PERMISSION.md)。当前不创建验证代码，不访问原生环境或外发。

D1-PBFT-SEAL/1.1继续CONDITIONAL_PROTOCOL_COMPLETE；D2有限精确模型条件定理保持。强G覆盖/I1–I3归档、严格分离0、NOVELTY_UNVERIFIED、IMPLEMENTATION_GATE=CLOSED。原R5目录/盲审包冻结复用，根四份旧导航/历史保存revisions/DCL-R5。

---
# 当前裁决 DCL-R5

2026-11-10，Asia/Shanghai。[R5最终裁决](DCL-R5/R5_FINAL_DECISION.md)与[增量索引](DCL-R5/README.md)为当前入口；下方历史按原内容保留。

|Gate|状态|范围|
|---|---|---|
|R5-A 关键证明责任|CONDITIONAL_PASS|P1–P5/D2矩阵；旧Stop/完整child激活/摘要pin分层，未登记发送及许可时点界|
|R5-B 部署证据|PARTIAL|官方ZIP/checksum摘要匹配；版本stamp hook及sqlite配置增量；真实dirty全集/运行连接待证|
|R5-C 验证准入材料|CONDITIONAL_PASS|F1–F4有限域/资源/变异及T1–T4逐端点/清理/停止齐列；代码/工具/fixture/授权绑定待补，执行未授权|
|R5-D 论文/路线|PASS|路线A验证优先，B工程化保留，C独立创新未启动；贡献与成熟技术归属明确|

D1-PBFT-SEAL/1.1继续纸面CONDITIONAL_PROTOCOL_COMPLETE，D2有限精确模型条件可靠/完备。旧quorum钥泄露的扩展目标及实际部署另有前提；本轮未发现满足全部明示模型假设的唯一历史反例。

S2(T)保留600/1800秒、10/20/24，补齐备用Gate事前当前资格、reserved/UNKNOWN和共享P服务条件。原生预登记展开最多92次HTTP，保留114封顶；NC2清理额度改为12，全局cleanup40保持。独立审查第一阶段输入已单独打包，外部审查完成0。

源码语义SOURCE_SEMANTICS_CONFIRMED，构建BUILD_CORRESPONDENCE_CONDITIONAL，实际行为DEPLOYMENT_BEHAVIOR_UNVERIFIED。强G覆盖/I1–I3归档保持，严格分离0，NOVELTY_UNVERIFIED，IMPLEMENTATION_GATE=CLOSED。模型程序/机制代码/构建/新原生请求/机器证明/外发均0。

R4目录和原182文件ZIP保持原件，仅根目录四份旧导航/历史保存在revisions/DCL-R4。原33输入及R1–R3归档继续锁定；行政核验与协议证明分列。

---
# 当前裁决 DCL-R4

2026-11-10，Asia/Shanghai。完整裁决见[DCL-R4最终报告](DCL-R4/R4_FINAL_DECISION.md)，文件导航见[R4索引](DCL-R4/README.md)。下面各轮历史按原内容保留；历史“最新”字样指各自时点。

|Gate|状态|关键边界|
|---|---|---|
|R4-A 证明复核|CONDITIONAL_PASS|P1–P5/D2同会话重新推导与反例；原生/真实费用进展条件化；外审/机器证明0|
|R4-B 部署精化|PARTIAL|A/B/C和源码—构建—Gate—P映射完成；实际仍单活，dirty构建/稳定恢复/V分离待证|
|R4-C B支持|CONDITIONAL_PASS|S1允许暂停；共主Q的单/双Gate无法满足S2；独立路径有限S2(T)条件见证与cut已给|
|R4-D 审查资料|PASS（准备范围）|本地审查ZIP、形式化/原生计划与论文边界齐备；未外发/未执行|

D1-PBFT-SEAL/1.1为CONDITIONAL_PROTOCOL_COMPLETE纸面实例。D2在有限精确模型下条件可靠/完备，包含真实中间前缀和累计费用；实际配置/求解实现及无限持续保证待证。

新增静态证据确认现存二进制声明Go1.26.10、固定commit及vcs.modified=true，本地ZIP内exe相同。源码—发行物精确对应仍UNPROVED。NC1/NC2保持SOURCE_FEASIBLE，新运行0；SC-A2A/Dyno正文SOURCE_UNRESOLVED。

I1/I2/I3继续COVERED_BY_G / MODEL_BLOCKED，严格分离0，NOVELTY_UNVERIFIED，IMPLEMENTATION_GATE=CLOSED。新增机制/模型代码、构建、原生请求、机器证明、外部审稿完成及外部联系/上传均0。原33输入及46/94/120份R1/R2/R3归档保留，完整性/链接/JSON/包哈希只作行政核验。

---
# 当前裁决 DCL-R3

2026-11-10，Asia/Shanghai。研究跨2026-11-09—10。R2的94份活动工件已完整归档于revisions/DCL-R2，R1归档与原33输入继续保留。

|审查对象|本轮结论|精确范围|
|---|---|---|
|NC1 / NC2|SOURCE_FEASIBLE|重新从调用链、XORM1.1.6、SQLite事务、主键和删除返回值构造；正常并发/DB条件下可行，原生新增实测0；额外部署串行层仍需单列|
|原生入口/截止|定义与分类已精化|NativeCreationCut覆盖全部入口、历史材料和在途handler；区分名义grant与存储GrantType；补Session/GetAccount条件创建入口|
|D1-PBFT-SEAL/1|CONDITIONAL_PROTOCOL_COMPLETE（纸面实例）|签名版静态PBFT＋唯一Seal/child＋完整验根接续；八步、消息/phase、故障流程和证明齐备。实际代码/跨域部署、移动旧钥攻击及全部署精化另待证|
|原强A停/B保留目标|按配置条件裁决|顺序Seal暂停主Q；B只有此Gate路径时原Support(B)失败，不能宣称原强目标通过。需D2验证独立持续支持及真实native截止|
|D2费用|有限精确模型下条件可靠/完备|COST1重新推导；累计费用阈值递推、非空Post、严格义务终态、费用观察与最大费用压缩条件明确；新求解执行0|
|组合|纸面条件保持证明|转交空窗EnvClosure、动态泄露包络、旧证书暂停/重验、来源/预算/义务/费用及claim不变量保持|
|新独立机制I1/I2/I3|COVERED_BY_G / MODEL_BLOCKED|每项两轮最小反证；登记责任完整性、动态证书与原生分类均缺候选专属保证或必要费用差|
|来源与独立性|SOURCE_UNRESOLVED / NOVELTY_UNVERIFIED|PBFT关键原文、XORM/SQLite新增一手证据；SC-A2A/Dyno全文仍有缺口；同一对话内重新推导，外部复核/机器证明0|

## 当前Gate

- Gate A：PASS_STATIC_SCOPED，原生与DB语义复核加强，部署实际可达/源码二进制符合性仍条件化。
- Gate B：PARTIAL_SOURCE_GAP，核心近邻/强G构造已审，全文/工件缺口保持。
- Gate C：CONDITIONAL_SPEC_CLOSED，限D1纸面实例与有限D2/组合合同。全目标、全配置、实际部署及外部验证未授予PROTOCOL_COMPLETE或REVIEW_READY。
- IMPLEMENTATION_GATE：CLOSED；严格分离实例0。协议条件完整性与原创性分别裁决。

本轮新增机制代码、机器验证程序、原生请求、实验和对外联系均为0。三项新架构创新主张按两轮覆盖/受阻结果归档，保留D1/D2作为条件安全架构与原生审计章节。具体证据入口见R3_NOVELTY_DECISION、R3_SOURCE_INDEX及各R3审查稿。

---

# DCL-R2历史裁决（保留）

2026-11-09，Asia/Shanghai。本节为最新裁决；R1历史见后文及revisions/DCL-R1。

## 本阶段结果

固定Casdoor源码HEAD与官方v4.25.0均指向528a0213f01caf70b9f41009cbf7b2f67bdd67ec；现存二进制哈希匹配历史M6锁。26份源码副本和13操作×18字段能力合同已经保存。源码→二进制可复现构建仍UNPROVED，新增原生请求/候选机制代码/实验/机器证明均为0。

|对象|当前规格/保证|创新与部署裁决|
|---|---|---|
|D1-R2|保留21转换与9条原反例；新增RHO、六类生效边界、Casdoor微步骤与NC1–7；SPEC_REFINED_CONDITIONAL|受信有限profile可接管责任、对账并继续独立B；完整BFT/部署全执行精化待证|
|D2-R2|原生行/RTcohort/session/user/app footprint、C0–C6真实配置、S_bypass及证书失效条件|有限配置/鲁棒观察博弈由通用G覆盖；配置安全依赖真实原生/托管证据|
|CD25-BOUND|M3/M4/M6的S/U/L饱和关闭前提得到源码重核|继承有限原生证据，保持可信创建者/范围/来源边界|
|CD25-LEAK|E1持password RT/密码/原生旁路时，Q变更不足以截止；共享cohort可连带B|强目标按条件MODEL_BLOCKED/INFEASIBLE；双方受同一限制|
|联合架构|保守handler相位模拟、RHO保持、旧证书失效与I_post条件已补|继续归为条件工程集成；一般精化和持续验证形式已有近邻|

## 新增关键事实

1. RFC7009端点已存在于指定版本。撤销同一Token行影响该行AT/RT，并可扩散到相同RT哈希活动行；轮换后的异哈希子行另查。
2. 刷新先读取/检查父、后插入子、再删除父。NC1/2给出撤销ACK后插入子行及同父双刷新的源码允许并发历史；新原生复现为0。
3. password grant发行的RT可在刷新时省略client_secret；专用刷新入口与统一token入口的GrantTypes检查不同。仅旋转secret或拒绝单入口不足以证明全部创建截止。
4. 普通审计在AfterExec后异步持久化，存在遮盖/分页/保留边界，缺request→新jti的原子完整来源合同。
5. COST1反驳了隐藏世界费用逐段max相加的通用精确最优性；修订为累计费用扩展＋阈值博弈。双方共用修正，原生相同轨迹的等费覆盖保持。

## 三项验收门

|Gate|状态|依据与剩余责任|
|---|---|---|
|A 原生语义精化|PASS_STATIC_SCOPED|关键指定API、21转换、M3/M4/M6条件、缓存/在途与历史bearer反例均已审；源码运行符合性及任意RP效果继续条件化|
|B 强基线审计|PARTIAL_SOURCE_GAP|AID/RQ/EB关键机制与相关证明段对照、同能力G和S1–S4反证完成；SC-A2A正文/实现获取失败，部分先例工件未重核，全面来源门暂缓|
|C 完整协议研究|PARTIAL_PROTOCOL_REFINED|D1/D2与联合规格已精化；独立创新候选按覆盖/受阻归档。一般分布式协议的具体BFT重配置、全部署精化及外部复核仍待补；PROTOCOL_COMPLETE/REVIEW_READY暂缓|

强G仍覆盖已具体化的可行功能与主要原生动作成本；S1为本轮新的最小分离尝试，加入标准计数/关闭组件后被完整G匹配。S2是双方不可行，S3信息不足，S4配置停止声明被源码反例推翻。严格分离实例仍为0，独立架构创新证据仍待取得，IMPLEMENTATION_GATE=CLOSED。

本阶段允许的研究已完成源码/规格与覆盖审计交付，来源/部署缺口明确保留。下一轮最高优先级见NEXT_ACTION；新增实现计划继续受用户既定门限约束。

---

# DCL-R1历史裁决（保留）

2026-11-09，Asia/Shanghai。裁决限本目录冻结的接口、故障、有限目录与度量。

|对象|规格状态|保证与覆盖|原创性 / 实现门|
|---|---|---|---|
|D1-R0：复制账本＋新代次接管|已被反例修订|旧 bearer 继续使用、延迟旧发送、历史派生遗漏|该版本判废|
|D1-R1：带持久责任和原生截止条件的接管|主要角色、消息、转换及异常已列明；SPEC_DRAFT|账本性质有归纳论证；原生性质依赖接口与部署；冻结有限子域 COVERED_BY_G|NOVELTY_UNVERIFIED；分离门未通过|
|D1 强原生停止，Provider 持续接受旧域已知 bearer|边界条件明确|MODEL_BLOCKED；CE1 给出直接反例及条件不可能性|边界结论的独立优先权待核|
|D2-R1：历史暴露、故障域与原生接受路径联合配置|有限模型、求解关系及证书规格已给出|显式模型下有条件可靠性/完备性证明；通用有限博弈/SMT 可表达相同问题|COVERED_BY_G 限冻结编码；NOVELTY_UNVERIFIED|
|D1+D2|配置到运行的模拟关系及迁移守卫已定义|当前归为工程集成；实际适配器精化待证|独立联合贡献未成立|

`PROTOCOL_COMPLETE` 与 `REVIEW_READY` 本轮暂缓授予。剩余责任包括：完整原生 profile、成员变更协议实例、对动态攻陷/恢复的机器检查、原生到模型的精化、公开先例覆盖的进一步核读以及外部复核。协议完整性、正确性、性能优势、发表优先权分别裁决。

本轮实质结果：

- 修订了跨域接管中的迟到请求问题：迁移 owner 的变化只转移账本职责；原生截止必须在接受方落实。
- 将重试拆为原 key 精确重放与原生终态无效果后的单继任，两条均保持原业务意图、来源和预算谱系。
- 给出 2-of-3 保管＋单点完整重建的能力传播反例；披露历史保持单调，原生可用性另行更新。
- 给出隐藏状态下“每个世界分别有解”与“同观察可执行策略存在”的区别及两世界反例。
- 为固定有限模型构造 G1 的逐转换模拟与 G2 的相同公式编码。两者消除了本轮候选的功能/主要成本分离预测。

本轮没有发现通用方法必须付更高代价的严格实例。[分离门](SEPARATION_GATE.md)记录具体输入、固定指标、G 的处理和判废条件。继续实现的前提尚待补齐。

文献范围：九类指定近邻均做检索；Horcrux、WAVE、SAGA、AID-Guard、EFFECTBOUND、Root-Scoped Quiescence、Seal、Lit 已取得可定位的一手内容，读取深度各异；SC-A2A 取得 IEEE 题录片段及 Crossref 作者/DOI，正文待补。国内数据库、部分会议/期刊、专利审查深度有限，全球首次保持待核。
