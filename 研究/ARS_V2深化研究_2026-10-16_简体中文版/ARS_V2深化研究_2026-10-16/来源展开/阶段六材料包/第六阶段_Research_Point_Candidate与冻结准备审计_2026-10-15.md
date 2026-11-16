# 硕士毕业设计立项研究：第六阶段 Research Point Card / Freeze Readiness

**报告编号**：V6-r1　**日期**：2026-10-15　**依据**：`00_PROJECT_CHARTER.md`、`60_RESEARCH_POINT_SCHEMA.md`、第一至第五阶段报告及项目原始研究 Word。

**阶段性质**：研究点候选化、版本化和冻结准备审查。用户要求进入下一阶段，本轮实施结构化记录和决策审查；不伪造 E0—E4 已运行结果，不提前将任何研究点标记为 `FROZEN`。

## 0. 执行结论

- **建议主线**：RP-2026-001；立项题目暂定《面向恶意同步环境的多凭据密码管理器可验证状态接纳与动态功能授权一致性研究》。
- **相互支撑的子问题**：RP-2026-002（匿名见证与恢复）、RP-2026-003（动态功能授权的信息流）。
- **储备问题**：RP-2026-004（RSPK）；已有确定性 WebAuthn 派生先例，保持 `PARKED`。
- **候选状态**：001、002、003 满足 Charter 对 `CANDIDATE` 的文字要求：明确问题、初步文献定位、可证伪主假设、竞争解释、可执行验证计划。**该状态属于研究准备成熟度判断，不代表创新已证实、实验通过或课题最终冻结。**
- **冻结门槛**：缺少可复现实验数据、独立 Oracle 与经过公平核对的 `B*` 实现；故 0 项达到 FROZEN。

## 1. 阶段输入与可追溯性

### 已有设计事实（SOURCE）

《密码管理器研究方案_整合版》第5章设计了 PACW、FICAP、RSPK 及类型化可信状态接口；《RSPK_基于根种子的可重建同步_Passkey_协议》定义根秘密派生与恢复设计；VDNS 白皮书提供早期见证和审计架构。原设计中的安全性质属于**待验证安全主张**，不能从文档文本自动转化成证明。

### 已有研究先例（PRIMARY / CODE）

- [PRIMARY] Fábrega 等, Mitigating Injection Attacks against E2EE Applications via View-Based Partitioning, USENIX Security 2025. https://www.usenix.org/conference/usenixsecurity25/presentation/fabrega-partitioning
- [PRIMARY] Pang 等, Zanzibar: Google’s Consistent, Global Authorization System, USENIX ATC 2019. https://www.usenix.org/conference/atc19/presentation/pang
- [PRIMARY] Birgisson 等, Macaroons: Cookies with Contextual Caveats for Decentralized Authorization in the Cloud, NDSS 2014. https://www.ndss-symposium.org/ndss2014/ndss-2014-programme/macaroons-cookies-contextual-caveats-decentralized-authorization-cloud/
- [CODE] Transparency.dev, witness (透明日志见证实现). https://github.com/transparency-dev/witness
- [PRIMARY] C2SP, Transparency Log Trust Policy. https://c2sp.org/tlog-policy
- [CODE] DiceKeys, seeding-webauthn (种子派生 WebAuthn 先例). https://github.com/dicekeys/seeding-webauthn
- [PRIMARY] W3C, Web Authentication: An API for accessing Public Key Credentials Level 3. https://www.w3.org/TR/webauthn-3/

### 尚未取得的研究证据（UNKNOWN）

- 无实际 `ReferenceOracle` 运行结果、T1/T2 的 `B*` 通过记录、T3/T5 的正反实验及严格比较报告。
- `JointEffectProof` 和 `PrivateQuorumProof` 仍为第五阶段定义的机制占位符，缺少形式化语义及真正实现。
- 未取得论文创新性的可重复原始证据或有效的安全证明；未确定最终工程环境、工作期限与设备条件。

## 2. 第六阶段 Research Point 决策表

| Research Point | 主要方向 | 建议状态 | Gap confidence | 最大威胁 | 最高信息增益行动 |
|---|---|---|---|---|---|
| RP-2026-001 | 跨层状态—授权—执行一致性 | `CANDIDATE` | POSSIBLE | 正确 B* 已满足全部安全性质 | 实施 E0-0/1/2 的独立 Oracle 与配对回放 |
| RP-2026-002 | 匿名 Witness 同根恢复 | `CANDIDATE` | POSSIBLE | 现成匿名见证与通用关系证明足够 | 明确 T5 关系语句，先尝试通用构造 |
| RP-2026-003 | 动态功能授权控制面泄漏 | `CANDIDATE` | POSSIBLE | VBP 完整 policy 已覆盖 | 同隐私定义下进行 T3 两世界试验 |
| RP-2026-004 | RSPK 可重建同步 Passkey | `PARKED` | UNKNOWN | seeded WebAuthn 与强加密备份已有等价路线 | 先保存材料，主线通过分离性门槛后恢复 |

## 3. 概念主线与父子关系

`RP-2026-001`（总安全语义与公平组合比较）

- `RP-2026-002`：为状态接纳提供隐私保护的恢复下界/见证关联证据。
- `RP-2026-003`：研究共享对象的功能影响授权及其控制面转录的隐私性质。
- `RP-2026-004`：可选应用扩展；依赖跨设备恢复结果，当前不纳入主线开发成本。

关系检查：RP-002 与 RP-003 是 RP-001 的不同子问题；RP-004 与 RP-002 存在恢复对象的 Overlap；RP-001 的最大竞争解释是已有机制正确组合 `B*`；RP-002、003 都与最强既有工作存在直接竞争。

## 4. 候选课题定位与贡献候选

**暂定课题题目**：《面向恶意同步环境的多凭据密码管理器可验证状态接纳与动态功能授权一致性研究》。

**研究目标**：在明确的恶意 Sync、可信本地核心、有限 Witness 故障和可信恢复下界条件下，区分“成熟机制即可保证组合安全”与“需要额外安全语义”，并将结论落实到可复现状态机、原型和实验数据。

**拟议输入**：凭据/授权/设备撤销/功能策略状态 `S_e`、见证头 `C_e`、可信恢复下界 `L`、功能操作和攻击者控制的同步轨迹。

**拟议输出**：统一事件和权限判定、ReferenceOracle 判决、接受/拒绝及理由码、最小反例、匿名见证验证记录、隐私优势和成本测量。

**技术路线**：现有文献模型 → 状态/授权不变量 → B0/B1/B*/P 差分原型 → T1/T2 Sanity → T3/T5 分离实验 → 如出现可归因收益再实施完整原型及跨负载评价。

**潜在贡献类别**：安全模型、分离性攻击或反证、可复现评价框架、有效条件下的证明/效率权衡。均为候选，须由未来研究证据支撑。

## 5. 冻结门槛与人工核查清单

| Gate | 必要的原始证据 | 当前情况 | 失败处理 |
|---|---|---|---|
| F0 研究卡完备 | 研究问题、术语、竞争假设、反证、关键引用和决策历史 | 已准备 | 修订 r2 |
| F1 Oracle 正确 | 自测、阳性/阴性变异、可复现运行命令与原始轨迹 | 未执行 | 暂缓比较 |
| F2 强基线公平 | B* 的完整功能、Witness 与可信 L、view policy、授权重检、公平性清单 | 未执行 | 重新配对 |
| F3 科学区分 | 可重放的 B* 独有反例，或同保证下可归因成本/隐私优势 | 未取得 | 接受 H2/H3；Pivot |
| F4 机制和边界 | 明确的安全性质、必要证明/反例、撤销时序与隐私范围 | 未完成 | 继续挑战 |
| F5 实用复核 | 故障、恢复、合法操作保留、成本与跨配置推广 | 未执行 | 暂缓完整系统承诺 |
| F6 研究者确认 | 导师/研究者确定最终研究范围、目标与冻结修订号 | 待确认 | 保留候选 |

**冻结判定**：只有所选研究点的相关门槛得到可追溯证据，并经研究者明确确认，才可将其版本状态改为 `FROZEN`；否则保持 `CANDIDATE` / `PARKED`。其中 F3 若不成立，也可以以新的系统测量问题重建 Research Point，而不必伪造机制收益。

## 6. 课题科学风险与范围裁剪

**范围内**：受管理本地核心、同步历史重放、账户状态验证、共享对象动态授权、恢复时可信下界、匿名见证同根、已知撤销的本地批准时序、跨模块攻击与误拒绝。

**范围外**：终端完全失陷、同步服务拒绝提供数据造成的可用性保证、已复制 Passkey 私钥在 RP 不变时远程撤销、所有外部第三方的最终提交撤回；RSPK 独立完整协议仅保留储备。

**最致命反证**：`B*` 在完全相同能力下已满足全部安全目标，新语义仅为已有机制组装。此时应基于实测决定转向安全基线测量、匿名恢复效率或新的研究问题，不以工程规模替代科研价值。

## 7. 论文工作量与创新性分配建议（条件性）

1. **理论与安全模型**：威胁模型、可信下界、安全不变量、Oracle 及对不可达到保证的限制。
2. **系统实现**：恶意 Sync、状态承诺/见证、动态授权与效应门禁、回放平台、可选 Passkey 元数据接口。
3. **实验评价**：强基线 B*、T1—T5、两世界攻击优势、匿名见证投票、故障恢复、资源成本、消融及可复现记录。

该组合具有硕士级工程工作量的规划空间。能否形成创新性结论，应以 F3/F4 的证据为准。当前不存在已测得的增益幅度或真实系统攻击结果。

## 8. 版本控制与后续交接

- **V6-r1**：第六阶段形成 4 份研究点卡、综合审查与机器可读索引；未将任何科研点冻结。
- **V6-r2（条件）**：执行 E0 并保留实际实验数据后更新 RP-001；T3/T5 出现区分或严谨阴性结果后更新 RP-003/RP-002。
- **冻结交接**：任何 `FROZEN` 卡应记录具体证据 manifest、软件 commit、参考文献版本、适用的实验条件和确认日期；如有修改，以新 revision 保留原冻结版本。
- **最高信息增益下一步**：实现独立 Oracle 与 B* 的 E0 最小状态机回放，先验证 T1/T2 的“强基线应通过”的事实，再决定投入 T3/T5 和全栈原型。

## 9. 阶段声明

第六阶段“候选卡结构化＋冻结准备审查”已完成；**研究点正式冻结尚未完成，创新性未宣称得到证明**。这一结论保留了项目章程区分 Observation / Interpretation / Evidence / Decision 的基本原则。
