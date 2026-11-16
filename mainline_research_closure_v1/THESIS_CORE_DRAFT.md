# 可组装的论文核心段落

本稿采用已有B版“条件性资源理论＋原生前提测量”口径，补入M1—M6成熟运行组合及部署证据。括号内主张ID对应CLAIMS.json，事实性段落附原始路径。文稿为当前研究过程内的章节初稿，未声称完成外部同行评议或优先权封口。

## 1 研究问题与贡献

面向代理的认证生命周期同时涉及任务身份、账户、批准来源、材料字符串与原生撤销效果域。用户撤回一项任务后，可信控制器需要决定是否允许新的调用、如何保留在途结果的原来源，以及何种证据足以关闭指定原生义务。本研究分别采用L、R、E描述受控入口准入、声明原生接受路径与效果提交，避免用单个本地状态替代不同层次的终止判断。（F01）[原规格P0037](D:/毕业设计/thesis_draft/sources/technical_report.txt) [形式模型](D:/毕业设计/thesis_draft/chapters/03_FORMAL_MODEL.md)

本文组织三类核心成果。第一类是包含批准、预算、不确定结果与严格义务的有限规约和可检查证书，论证在完整转移覆盖与终态反映条件下的有界完成。第二类是M_r模型下固定绑定迁移距离、静态退化与完整资源节省谱。第三类是分层验证和可追溯原生测量，并以成熟事务、托管及对账组合形成限定部署profile。三类成果分别承担规格、条件性数学和工程/实测证据责任。（F02/F03/T01/T02/E01–E09）[语义论证](D:/毕业设计/auth-lifecycle/docs/SEMANTICS.md) [R3结论](D:/毕业设计/research_recipe_r3/VERDICT.md) [M6验收](D:/毕业设计/mainline_native_isolation_v1/ACCEPTANCE_REPORT.md)

## 2 模型、资源与信任前提

有限信息状态K同时包含服务语义与外部状态的不确定性。相同观察下的全部允许后继进入Post；动作在每个可能节点中满足账户、批准、预算与前置要求。W_0要求K非空、目标与安全条件成立且严格义务为空，W_h按全部观察后继和递减决策步定义。由h归纳可得声明模型内的条件性完成结论；h承担决策步界，实际网络和调度活性由适配合同另证。（F02）[SEMANTICS §3–8](D:/毕业设计/auth-lifecycle/docs/SEMANTICS.md) [有限抽象条件](D:/毕业设计/auth-lifecycle/docs/ABSTRACTION.md)

多世界证书绑定模型、当前信息及查询范围。可行证书给出统一观察策略；不可行证书为每个动作提供真实阻断或允许的失败分支。三世界共同方案冲突说明世界对不足以覆盖任意有限世界的共同决策。模型摘要提供字节绑定，其认证来源、完整性及真实服务符合性仍由外部输入契约承担。（F03）[证书规约](D:/毕业设计/auth-lifecycle/docs/CERTIFICATES.md) [检查实现](D:/毕业设计/auth-lifecycle/src/auth_lifecycle/checker.py)

在资源模型M_r中，初始配置在首次停止请求前共同确定，每个任务有一个当前支持；目标根完全可用、容量充分，迁移为单任务原子交接并同步退役旧支持，空备用根计入资源G。在这些条件下，固定配置的最少迁移数等于两标签错配距离。对固定k≥2、r≥1，允许有限任务集及同签名重数随实例变化，最优根数节省值恰遍历0至k−2。其量词为共同初态的∃b0—∀请求—∃执行；固定实例的大预算退化与跨实例完整谱分别成立。（T01/T02）[完整陈述和量词表](D:/毕业设计/research_recipe_r3/MATH_REVIEW.md) [隔离上下文推导](D:/毕业设计/research_recipe_r3/BLIND_DERIVATION.md)

当前部署选择CASDOOR_NATIVE_ISOLATED_V1：单机、单活可信R、可信在线权威、专用组织和受限代理进程。R托管原生材料，代理持任务句柄与自身服务能力；AS为Casdoor4.25.0，接受观察限定于cookie-free UserInfo及声明内省接口。环境管理凭据、评分私钥和私有响应分别受ACL保护。R本地旧缓存可回滚，权威状态和必要密钥位于该故障范围之外。（E07/E08）[profile](D:/毕业设计/mainline_native_isolation_v1/NATIVE_ISOLATION_PROFILE.md) [主体/材料矩阵](D:/毕业设计/mainline_native_isolation_v1/PRINCIPAL_MATERIAL_CHANNEL_MATRIX.md)

## 3 分层验证设计与结果

资源理论的扩容核对包括268,310个固定配置预算查询、5,000个随机全局需求族及224个谱构造。后者36例完成更少根配置全枚举，其余188例核对执行见证与手工引理前提。这些有限数据支持登记范围中的一致性；全称结论由手工证明承担，同模型隔离重推导与外部数学审阅的状态分别保留。（T01/T02）[原始摘要](D:/毕业设计/research_recipe_r3/results/expanded01/summary.json) [验证范围](D:/毕业设计/research_recipe_r3/MATH_REVIEW.md)

原生实证包含Keycloak26.8.1与Casdoor4.25.0的52次受控语义调查，以及288对、576次六方法校准。校准输入为已知契约，各方法每96次包含20完成、56拒绝和20UNKNOWN；三组成本比均为1。研究A查询选择及AB具体反馈激活数为0。该结果按负控制和校准使用，H-A/H-B/H-AB的总体优势没有在当前论文中主张。（E01/A05/H01）[调查原始数据](D:/毕业设计/auth-lifecycle/results/experiments/survey04/observations.json) [576次原始运行](D:/毕业设计/auth-lifecycle/results/experiments/pilot02/runs.jsonl) [结果及成本](D:/毕业设计/auth-lifecycle/docs/experiments/RESULTS.md)

M1以假provider验证持久接纳和恢复，完整21槽保留20通过与1初始化中止。M2四条原生轨迹保留原始3通过/1报警，固定启动次数规则经离线复核修订为4通过，原生没有重采；M2-04原中断期接纳缺项由单独零原生本地补核登记。M3的两条关闭轨迹依赖预启用标识日志及精确点读；M4的两条轨迹使用额外专用组织授权完成无标识发现，清理修复3次HTTP保留在最终98次费用中。（E02–E05）[M1分母](D:/毕业设计/mainline_online_state_v1/M1_AGGREGATE.json) [M2修订及补核](D:/毕业设计/mainline_native_casdoor_v1/ACCEPTANCE_REPORT.md) [M3](D:/毕业设计/mainline_native_reconciliation_v1/ACCEPTANCE_REPORT.md) [M4](D:/毕业设计/mainline_native_unidentified_v1/ACCEPTANCE_REPORT.md)

M5在合成材料下完成12项OS权限场景，原生请求0。M6以相同受限令牌结构连接真实Casdoor，两条各一次，分别为已知材料处置和条件性关闭；每条43项检查属于同一轨迹内的检查项目。正式M6使用84次原生HTTP，当前运行态最终义务均为空，B在账户级清理前合法继续。157项是本轮证据口径修订后的开发回归数；它与历史M5的141项、M6的148项分版本登记。（E06/E07/E12）[M5](D:/毕业设计/mainline_agent_isolation_v1/CUSTODY_ACCEPTANCE_REPORT.md) [M6原始结果](D:/毕业设计/mainline_native_isolation_v1/batch01/RESULTS.json) [历史M6成本](D:/毕业设计/mainline_native_isolation_v1/COST_AND_RESULTS.json) [本轮回归](D:/毕业设计/mainline_research_closure_v1/FULL_REGRESSION_V2.log)

## 4 条件性关闭与反例

M6-02在A1进入权威前终止R，关闭完整inbox和标识日志；运行者查询前只持pending、原批准与摘要等允许输入。获准组织查询返回4行，目标账户2行，扣除已知来源后形成唯一候选。四批准各预算10给出生命周期记录上界40，容量100覆盖单Find快照；单发送、单效果上界与唯一可归属观察一起使该尝试剩余创建能力为0。A处置及B保留成立后，普通收据提交条件性CLOSED。（E09）[输入与轨迹](D:/毕业设计/mainline_native_isolation_v1/batch01/M6-02/trusted/runner/outcome.json) [收据](D:/毕业设计/mainline_native_isolation_v1/batch01/M6-02/trusted/runner/closure_receipt.json) [源条件](D:/毕业设计/mainline_native_isolation_v1/NATIVE_ISOLATION_PROFILE.md)

完整当前集合仍允许查询后迟到创建；两个未知来源使同账户剩余候选失去唯一归属；重试或每请求多效果使一次发现无法耗尽前沿。分页容量不足和并发跨页变化分别破坏集合覆盖。M4的迟到创建轨迹及开发负例为这些区别提供具体见证。关闭的充分性依赖登记合同，而单条轨迹只排除相应实例中的反例。（E05/E09/E11）[M4完整性论证](D:/毕业设计/mainline_native_unidentified_v1/COMPLETENESS_AND_ATTRIBUTION.md) [原枚举负例](D:/毕业设计/auth-lifecycle/tests/test_unidentified.py)

本地ACK、内省和资源接受各有范围。RT内省inactive不代表发送过刷新请求；刷新4xx及响应无材料也不能独自排除AS已发生效果。M6的RT证据来自只读内省，资源观察为指定UserInfo，E效果和其它RP需要自己的接受与截止依据。原query.reported_pages保存data2计数，当前字段已明确区分计数、返回行数、页容量及读快照完整性。（F01/E10/E11）[冻结测量源](D:/毕业设计/mainline_native_isolation_v1/source_frozen/scripts/measure_native_casdoor.py) [本轮规范视图](D:/毕业设计/auth-lifecycle/src/auth_lifecycle/online_state/evidence_semantics.py) [字段映射](D:/毕业设计/mainline_research_closure_v1/EVIDENCE_SEMANTICS.md)

## 5 算法、密码学与工程的定位

研究A/B/AB已经在有限模型中实现，早期已知契约校准也有B配置到原生执行的受限绑定。M1—M6由固定验收入口安排动作，持久Controller实施当前批准、来源、预算和成熟对账判断，未调用这些求解器。有限source→L0及表间抽象关系检查不能替代持久状态/原生微步骤→W_h的精化。当前论文保留这些实际边，而把端到端算法闭环作为接口缺口登记。（A01/A04/A05）[有限算法](D:/毕业设计/research_v12/FORMAL.md) [旧原生绑定](D:/毕业设计/auth-lifecycle/src/auth_lifecycle/experiment/planning.py) [M6入口](D:/毕业设计/mainline_native_isolation_v1/source_frozen/src/auth_lifecycle/online_state/native_isolation.py) [调用图](D:/毕业设计/mainline_research_closure_v1/ALGORITHM_RUNTIME_MAP.md)

B4的受限类数压缩可由同等通用预处理复现；AB3历史scope检查反例使其广义实现健全性主张收缩。七项淘汰机制与密码学候选B的归档状态保留。当前成熟组合在登记合同内承担事务、托管、在线当前性和条件对账职责，尚无明确新增密码学功能或严格分离实例。（A02/A03/C01/C02）[B4与AB边界](D:/毕业设计/research_v12/REVIEW.md) [scope反例](D:/毕业设计/research_secret_recipe/SCOPE_AUDIT.json) [七机制记录](D:/毕业设计/research_secret_recipe/REPORT.md) [密码学冻结裁决](D:/毕业设计/研究/密码学辅助_一致性核验/revisions/crypto_state_cost_review_2026-11-05/DECISION.md)

资源谱当前具有条件性数学论证和有限核对，整体优先权保持近邻未决。最新临时理论策略选定A-E：小分离行/例外任务见证的存在性已经给出，在目标参数界内定位候选仍未证明。因此高强度算法主创新继续是研究目标；下一动作可精确限制为该证明步骤或其障碍，工程验收不承担这一新颖性判断。（T02/H02）[优先权状态](D:/毕业设计/research_recipe_r3/PRIORITY_AUDIT_R3.md) [当前选题决定](D:/毕业设计/research_main_innovation/main_topic_selection/TOPIC_DECISION.md) [证明状态](D:/毕业设计/research_main_innovation/main_topic_selection/sources/PROOF_STATUS.json)

## 6 局限与有效性威胁

论文中的有限规约以转移、原生效果及终态覆盖为条件；M_r额外要求完全资格、原子支持交接和旧支持退役。M6的原子接纳和刷新不会自动证明这些公理。当前native profile与资源理论之间的关系保持条件化，多活、跨机器、权威自身回滚、灾难恢复、任意RP和不可逆业务效果均留在已列缺项内。（F02/T03/E07/E09）[M_r原生前提](D:/毕业设计/research_recipe_r3/NATIVE_PREMISES.md) [M1—M6总表](D:/毕业设计/mainline_native_isolation_v1/MAINLINE_EVIDENCE_MAP.md)

实现、独立参考与评分器存在共享schema、解释器或传输组件；本轮新字段解析也是共享数据基础。手工证明、同模型隔离重推导、有限实现一致性与外部人工审阅分别登记。历史v2.15 DOCX原件仍缺失，当前资源定理由R2/R3的冻结重述和证明支持。校验程序支持所登记工件的完整性与来源追踪，无法认证全部主张已经被语义提取或所有现实行为均被覆盖。（T02/A03）[论证独立性](D:/毕业设计/research_recipe_r3/MATH_REVIEW.md) [历史缺项](D:/毕业设计/thesis_draft/POSTPONED_UPGRADES.md) [本轮只读校验](D:/毕业设计/mainline_research_closure_v1/verify_evidence.py)
