# DCL-R4最终研究裁决

2026-11-10，Asia/Shanghai。本轮完成同会话证明重新推导、部署映射、B支持合同/见证、定点来源补查及后续审查/验证准备。历史33输入、46份R1、94份R2和120份R3归档保留；哈希检查范围见[evidence/HISTORY_INTEGRITY_CHECK.json](evidence/HISTORY_INTEGRITY_CHECK.json)。

## 1. 四项Gate

|Gate|裁决|直接证据|条件/剩余责任|
|---|---|---|---|
|R4-A 证明复核|CONDITIONAL_PASS|[证明复核](R4_PROOF_REVIEW.md) §§2–10；[1.1规范增量](R4_PROTOCOL_REFINEMENT_DELTA.md)|P1/P2/P3-local/P4及有限D2在模型内重建；native/effect、费用/进展实际精化条件化；外审/机器证明0|
|R4-B 部署精化|PARTIAL|[A/B/C映射](R4_DEPLOYMENT_REFINEMENT.md)；[源码二进制证据链](R4_SOURCE_BINARY_PROVENANCE.md)|现状单活A子域；分布式Q、元数据/V分离、稳定防回滚、实际入口/事务及dirty构建对应待证|
|R4-C B支持合同|CONDITIONAL_PASS|[S1/S2(T)、配置、B-ROT及cut见证](R4_TASK_B_CONTINUITY.md)|单/双Gate共主Q失败；独立Q_B路径在有限时间、故障/网络/期限/只读工作负载/费用条件下成立；实际S2部署0|
|R4-D 审查资料完整|PASS（准备范围）|[审查包](R4_EXTERNAL_REVIEW_PACKAGE.md)、[机器验证计划](R4_FORMAL_VERIFICATION_PLAN.md)、[原生实验计划](R4_NATIVE_EXPERIMENT_PLAN.md)、[论文贡献边界](R4_THESIS_CONTRIBUTION_BOUNDARY.md)|材料准备与独立审查完成分别登记；本地ZIP/manifest校验见DELIVERY_CHECK。外发/执行0|

Gate R4-D的PASS仅指所要求材料和本地工件齐备。全部Gate的状态都不授予实现资格、真实部署安全认证或REVIEW_READY。

## 2. D1与D2的完整性

**D1**：`D1-PBFT-SEAL/1.1 = CONDITIONAL_PROTOCOL_COMPLETE`，限R3的21业务转换、八步重配及R4增量规定的纸面模型。唯一Seal/child、固定genesis、完整责任状态接续和恢复安全具有模型内归纳。ReadyState与ReadyUse分别验收，避免将秘密明文分发给Q或预检变成执行权限。实际PBFT/跨域V-Gate部署和全部原生停止仍有明确精化责任。单路径B要求S2时该配置失败；接受S1时保留条件恢复。

**D2**：有限精确模型中，累计费用知识状态、合法观察/非空Post、共同策略、严格终态和阈值递推的可靠性/完备性重建成立。最大z压缩受完整Markov状态/同未来同观察条件约束；CE5展示遗漏模式的错误。配置已加入S2全部路径、期限、故障、费用和中间前缀义务。真实模型完整性、求解实现、无限h及无界维护另待证。

组合安全需全真实步覆盖；实际费用需逐尝试标签保持；进展需公平/可达/有限实现段。CE3无限安全stutter及CE4免费查询stutter证明额外义务的必要性。h仍是决策段数，T/δ是单独的时间合同。

## 3. 本轮证据、反例与未解决项

- 复核P1–P5和D2，形成CE1回滚旧ACTIVE、CE2旧无序缓存当前化、CE3进展stutter、CE4费用stutter、CE5遗漏隐藏模式；它们定位前提/部署缺项。原R3全部明示假设内的唯一历史反例本轮尚未发现。
- B-ROT展示单根refresh在父删除与子材料到达之间的支持空窗。独立B静态Q/Gate/V/预取得材料给出S2(10分钟)有限正例，CUT-ALL、CUT-SHARED及有限预算/期限给出不可行见证；不外推无界S2。
- 静态buildinfo声明固定commit、Go1.26.10、依赖与`vcs.modified=true`；本地ZIP内exe与现存exe相同。官方asset摘要、dirty差异及精确构建对应仍未闭合。
- DB main-file头最后写入者指示3.39.3；实际活跃引擎/PRAGMA/WAL视图未在本轮运行认证，Python SQLite版本另列。
- SC-A2A正文/实现、Dyno定理正文仍SOURCE_UNRESOLVED；空OpenAlex投影已修正为无可用元数据证据。来源闭合总体PARTIAL。

## 4. 强G与原创性

I1/I2/I3继续按R3归档为COVERED_BY_G / MODEL_BLOCKED。强G可取得同一Ready分工、费用/进展修订、独立支持路径、全部资源和标准配置/博弈技术。在已给逐事件构造中双方native动作相同，费用相等；尚无G必要更高代价的输入。

`STRICT_SEPARATION_INSTANCES = 0`，`NOVELTY_UNVERIFIED`，`IMPLEMENTATION_GATE = CLOSED`。本轮未重开创新候选，未编写机制或模型检查代码。

## 5. 外部审查与下一阶段最小工作

外部审查优先挑战唯一child/旧钥/恢复、Ready与秘密流、真实发送/Seal/native相位、费用观察与B所有中间前缀。随后按未来明确授权与适用门槛选择：F1应用层小模型、F2缓存handler、F3支持路径、F4 COST1/CE5；以及四条隔离原生轨迹T1–T4。原生首批拟议总上限114次尝试，逐端点清单及依赖范围需在执行前核定。

优先只读补证为官方构建摘要/日志、dirty差异、实际DB/入口串行层和新正文入口。新实验与构建在本轮保持计划状态。原工程、历史账户和端口18081保持冻结。

## 6. 可准确用于论文的结论

可以陈述：建立了凭据生命周期的责任/原生边界模型，给出条件跨配置协议与有限联合配置形式化，审计固定版本Casdoor并构造源码允许交错，提出S1/S2合同、可行条件与不可行见证，整理部署与验证义务。成熟技术归属及强G覆盖同步说明。

正式机器证明、外部独立评审、真实跨域PBFT部署、新原生并发观测、严格优势实例及独立原创性仍待取得。具体可用段落与五类证据见[R4_THESIS_CONTRIBUTION_BOUNDARY.md](R4_THESIS_CONTRIBUTION_BOUNDARY.md)。

## 7. 活动与行政核验

新增机制代码0；模型检查程序0；构建0；新增native请求0；新实验0；机器证明0；外部审查完成0；外部联系/上传0。开展了静态文件/二进制元数据/DB头读取、公开来源访问、纸面推导与文档打包。

文件存在、JSON、链接、哈希及包扫描属于ADMIN_CHECK；不承担协议证明或漏洞实测。首次归档检查器误把根数组视为包裹对象，产生伪缺失；初次结果完整保留，修正类型处理后的全部锁核对通过。最终行政结果以[evidence/DELIVERY_CHECK.json](evidence/DELIVERY_CHECK.json)为准。
