# DCL-R4：外部独立审查包说明

2026-11-10。本地准备包：`review_package/DCL-R4_REVIEW_PACKET.zip`；目录镜像：`review_package/payload`。交付检查记录在`evidence/DELIVERY_CHECK.json`，包内`PACKAGE_MANIFEST.json`锁定每项相对路径/字节/SHA-256，包外`REVIEW_PACKET_SHA256.json`锁定ZIP。包创建后仍保留研究工作目录原件。

外部发送/上传/联系0，外部审查完成0。材料已打包与获得独立认证分别记录。未来交给导师/研究者或工具时，需指定对象、范围、内容与相应授权。

## 1. 独立性披露与复核方法

R4在同一已知上下文中重新推导；无法回溯形成真正盲审。代码路径/源码/公开文献的交叉证据，纸面重新推导，工具运行证明，外部人工审稿分别登记。目前新增安全工具运行0、机器证明0、外部人工审查0。

建议接收者先阅读问题、模型与定理陈述，自己构造证明/反例并封存初稿，再对照已有证明。报告中记录审查者身份/工具版本、先前接触范围、读过的文档/段、方法、利益关系、使用证据和剩余限制；“不同模型输出”本身不提供独立正确性认证。

## 2. 十二项材料索引

|审查项|包内入口（保留研究根相对布局）|
|---|---|
|研究问题/任务|D1/PROBLEM_AND_THREAT_MODEL.md；DCL-R4/evidence/TASK_REQUEST.txt|
|攻击/故障/信任|D1/BFT_RECONFIGURATION_PROTOCOL.md §§1–3；D2/CONFIGURATION_MODEL.md；DCL-R4/R4_DEPLOYMENT_REFINEMENT.md|
|D1完整协议|D1/PROTOCOL_SPEC.md＋BFT_RECONFIGURATION_PROTOCOL.md＋DCL-R4/R4_PROTOCOL_REFINEMENT_DELTA.md（1.1规范增量）|
|D2联合模型|D2/CONFIGURATION_MODEL.md、ALGORITHM_AND_CERTIFICATES.md、COST_SEMANTICS_R3.md|
|核心定理|D1/PROOF_OBLIGATIONS_R3.md；D2/COST_SEMANTICS_R3.md；DCL-R4/R4_PROOF_REVIEW.md|
|证明依赖与组合|JOINT/R3_COMPOSITION_CONTRACT.md＋R4规范增量/部署映射|
|反例/失败方案|D1/PROOFS_AND_COUNTEREXAMPLES.md；NATIVE_SEMANTICS_REFINEMENT.md；DCL-R4/R4_PROOF_REVIEW.md、R4_TASK_B_CONTINUITY.md|
|Casdoor原生合同|CASDOOR_NATIVE_CONTRACT_AUDIT.md；R3_INDEPENDENT_CONCURRENCY_AUDIT.md；R3_NATIVE_ENTRY_CUT_AUDIT.md；evidence/r2/native/NATIVE_CAPABILITIES.json|
|最强G等价构造|BASELINE_G.md；STRONG_G_COVERAGE_AUDIT.md；R3_STRONG_G_REASSESSMENT.md；DCL-R4/R4_PRIOR_WORK_CLOSURE.md|
|原创性裁决|R3_NOVELTY_DECISION.md；DCL-R4/R4_FINAL_DECISION.md|
|未解责任与验证|DCL-R4/R4_DEPLOYMENT_REFINEMENT.md、R4_FORMAL_VERIFICATION_PLAN.md、R4_NATIVE_EXPERIMENT_PLAN.md|
|论文贡献与挑战|DCL-R4/R4_THESIS_CONTRIBUTION_BOUNDARY.md及下节问题|

冻结R3关键文稿还以`revisions/DCL-R3`相同相对布局收入，R3锁记录完整120工件；包只收入指定审查文稿/元数据，未收入的工件在PACKAGE_SCOPE标明。以1.1增量修正/限定旧文中的Ready与费用/进展表述。历史文稿按原版本保留，其当时“最新”字样仅指历史时点。

## 3. 优先挑战问题及验收标准

1. 在A1–A6及1.1前提全部成立时，能否构造两个有效Stop/child或两个授权历史？重点核无交集、连续重配、旧钥生命周期和近期anchor。反例需给完整状态/消息/签名者及哪条正确守卫允许它。
2. 逐项检查F是否保持全部origin、UNKNOWN、quota、Hist、send_right和全局dedup；恶意E隐瞒native创建时，登记完整性与外部全集边界是否清楚？
3. 当前challenge和Gate资格是否仍允许旧授权在Revoke/Seal后到达P？其在途责任是否全部进入EnvClosure及实际费用？C_local与更强截止点是否分明？
4. ReadyState/ReadyUse是否仍有秘密泄露或授权循环？V/Gate更新、恢复和旧材料输出是否完整进入模型？
5. 是否存在满足S2(T)正例全部故障/时限/工作负载条件、却在某个中间前缀失去Support的轨迹？检查B-ROT、Q_B当前性、单Gate崩溃、只读重试和预算/时钟裕量。
6. D2的Post是否遗漏合法观察/中间坏前缀？费用是否沿同一历史累计？压缩是否遗漏影响未来或观察的变量？有界可靠性/精确完备性的方向是否成立？
7. Casdoor调度在XORM/SQLite和实际部署串行化下能否实现？dirty构建与实效配置还需要什么证据？阴性实验应如何收缩结论？
8. 强G能否逐事件复现上述行为/证书和费用？如声称候选优势，请给输入族、固定指标、相同能力/观察/资源的G，以及G必要更高代价的实例或证明。

审查结果按VERIFIED_WITHIN_MODEL、CONDITIONAL、COUNTEREXAMPLE_FOUND、PROOF_GAP、NEEDS_MACHINE_CHECK、NEEDS_EXTERNAL_REVIEW报告。指出来源范围/证明前提/部署/原创性中的哪一层受影响，保留失败和INCONCLUSIVE。

## 4. 包范围、秘密边界与可移植性

仅收入研究Markdown、能力/主张/来源JSON、任务文本、锁、脱敏buildinfo与元数据视图；未收入密码/AT/RT/cookie、私钥、数据库、`.runtime`原文件、原始HTTP秘密响应、可执行二进制、完整原生源码树或整篇论文正文。源码以commit、公网URL、局部行号与哈希定位；接收者需自行取得公开源，不能据包内元数据声称已读完整源代码。

`PACKAGE_START_HERE.md`和`PACKAGE_SCOPE.md`提供离线导航与未打包依赖。相对Markdown链接检查覆盖包内可导航文件；外部本地证据、原始输入与源副本只作为明确外部依赖。包内和包外manifest的哈希属于工件完整性检查，语义正确性由审查承担。
