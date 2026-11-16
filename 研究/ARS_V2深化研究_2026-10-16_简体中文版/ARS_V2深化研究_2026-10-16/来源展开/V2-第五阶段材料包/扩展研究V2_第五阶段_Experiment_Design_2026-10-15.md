# 扩展研究 V2｜第五阶段：Experiment Design

- **Revision**：V2-DESIGN-r1
- **日期**：2026-10-15
- **适用 Skill**：`50_EXPERIMENT_DESIGN_SKILL.md`
- **研究点**：RP-2026-005 / RP-2026-006 / RP-2026-008（拟议 `VALIDATION_DESIGN`）；RP-2026-007 维持 `PARKED`
- **原始依据**：`扩展研究V2_第四阶段_Hypothesis_Critique_2026-10-15.md`、`扩展研究V2_第四阶段_第五阶段交接摘要_2026-10-15.md`、此前 V2 第 1—3 阶段及 V1 已候选研究点。
- **实证状态**：**仅实验设计；未运行真实攻防实验、模型检查或性能基准。** 下文所有预测均为 `[HYPOTHESIS]`，阈值属于预注册建议。不得将方案预期写成研究发现。

## 0. Executive Decision：本阶段最重要的决定

**建议首先实现独立 Reference Oracle + 统一事件状态机，完成 E0，再实施 E1 的跨故障域分离实验。** 目前没有证明区块链对强独立 Witness/公告板的必然优越性。把“Witness+链”同时与强 Witness-only、等独立无链公告和许可型 BFT 进行公平比较；区分 `R1 同认证信息` 与 `R2 新增独立故障域`。Web2/Web3 授权与多观测面隐私分别设计可否定拟议方案的实验。完整系统和高成本 ZK/公链部署须以 E0/E1 的实际结果为条件。

硕士暂定题目：《面向恶意同步环境的分布式凭据状态恢复与跨范式授权一致性研究》。研究价值优先定位为**跨故障域恢复的精确安全界、跨范式控制权时序一致性及可复现的隐私—成本评价**，并允许负结果形成研究结论。

## 1. Claims to Test：从主张到证据

| Claim | Research Point | 待验证原子主张 | 第一实验 | 安全属性 |
|---|---|---|---|---|
| `C01` | RP-2026-005 | 外部最终性仅证明已公告且已最终化状态的可信下界，不等于业务最新状态 | `E0-02` | `P_FRESH` |
| `C02` | RP-2026-005 | 外部共识历史证据必须与账户授权、原子状态根和前驱链同时验证 | `E0-01` | `P_AUTH` |
| `C03` | RP-2026-005 | 跨独立故障域可以在部分 Witness 故障阈值被突破时提供条件性恢复分离 | `E1-01` | `P_HIST` |
| `C04` | RP-2026-005 | 同等认证信息与信任预算下链后端不具有天然判定优势 | `E1-02` | `P_FAIR` |
| `C05` | RP-2026-006 | 恶意 RPC 旧状态下重要操作授权依赖有界新鲜度及可信状态证明 | `E2-01` | `P_RP` |
| `C06` | RP-2026-006 | 在匹配可信证明与同步条件下拟议方案相对强标准组合才可能有独立收益 | `E2-03` | `P_RP` |
| `C07` | RP-2026-008 | 匿名投影对联合观测攻击的保护超越固定批处理与匿名转发 | `E3-01` | `P_PRIV` |
| `C08` | RP-2026-005 | 链审查和证明延迟引起安全拒绝与恢复可用性之间的权衡 | `E4-01` | `P_LIVE` |
| `C09` | RP-2026-005 | 链上不可改写性不能代替密文可取回性和数据可用性 | `E4-02` | `P_AVAIL` |
| `C10` | CROSS | 新增机制的任何优势须在相同合法功能、资源与信任预算中可归因 | `E1-04` | `P_FAIR` |

每个 claim 均明确对应实验；不以“增加吞吐测试”代替机制识别。`C03` 和 `C07` 是候选创新主张，`C01/C02/C09` 主要是边界正确性，`C04/C10` 是因果与公平审查要求。

## 2. 系统模型、状态与独立 Oracle

### 2.1 信任主体和攻击能力

- `U`：合法账户所有者及受信本地 Core，产生设备签名，管理凭据、权限与撤销纪元；设备私钥在对应信任假设下未泄漏。
- `S`：完全恶意云同步服务器，能删除、延迟、拼接、回滚并向不同设备分叉历史合法密文与事件；不能伪造诚实设备签名。
- `W`：四个见证者的**示例模型**为 `(n=4,f=1,q=3)`，主试验在 `f` 内和超过 `f` 的范围分别进行；Witness 的身份独立性必须通过组织和基础设施假设记录。
- `A`：独立公告域，包括无链认证公告、许可型 BFT 和公链/L2 最终化公告。每一种都有独立信任起点、成员治理及发布时延。
- `RP`：可自愿接入 SIWE/ERC-1271 的网站，维护 Cookie/会话及高风险操作 API；RPC 可以恶意或陈旧。
- `O`：可联合观察链交易、Witness 查询、RPC 元数据和公开钱包交互的隐私攻击者。

### 2.2 统一状态与证据

一次账户状态 `S_e` 至少包含 `AccountPseudonym, epoch, parent_state_hash, DeviceRoot, CredentialRoot, PolicyRoot, WalletBindingRoot, RevocationRoot, signer_set`，并计算域分离承诺：

`C_e = H("vpass-state-v2" || account_context || e || H(S_e) || prev || policy_version)`。

事件记录必须关联合法操作主体、权限版本、撤销生效纪元、签名上下文和前驱根。见证检查点 `Q_e` 必须携带法定人数签名和历史一致性证据；外部公告 `A_e` 必须携带经过认证的包含证明、链/公告最终性证据及可信引导点。**只有有效的共识证明且与有效应用状态根匹配，才能组合成业务上可接纳的状态。**

定义 `L_W` 与 `L_A` 为对应证据支持的恢复新鲜度下界，它们可能不在同一时间更新。仅对同一合法祖先链兼容的下界进行合并；若两份有效证据锚定不同冲突分支，返回 `CONFLICT`，禁止通过简单 `max(epoch)` 掩盖历史不一致。

### 2.3 Oracle 的输出

| 结果 | 语义 | 统计归类 |
|---|---|---|
| `ACCEPT` | 应用授权、前驱与证据、恢复下界均验证通过，目标数据可取回 | 合法接纳 |
| `REJECT_AUTH` | 签名主体、权限版本、撤销生效纪元或状态绑定不合法 | 安全拒绝 |
| `REJECT_FORK` | 历史/法定人数证明与已认证祖先链冲突 | 安全拒绝 |
| `REJECT_STALE` | 待恢复状态低于已认证新鲜度下界 | 安全拒绝 |
| `HOLD_INSUFFICIENT_PROOF` | 证据不足以达到预注册的接纳政策 | 受控等待/降级 |
| `HOLD_UNAVAILABLE` | 已确认状态的业务密文不可取回 | 可用性失败 |
| `CONFLICT` | 独立可信证据互相矛盾，需要人工审查/隔离 | 冲突告警 |

错误旧状态接纳率只能在 Oracle 明确标记 `REJECT_*` 的情况下计入分子。`HOLD`、`REJECT` 和真正完成解密恢复必须分开报告。参考 Oracle 不复用被测客户端的核心状态验证函数；建议双实现交叉检查或以小状态空间有界穷举校准。

### 2.4 目标谓词（设计草案，不是形式化安全证明）

```text
AcceptRecovery(state, event, proofSet, policy):
    if not VerifySignatureAndDeviceAuthority(event, state.policy):
        return REJECT_AUTH
    if not VerifyRevocationEpochAndAtomicRoots(state, event):
        return REJECT_AUTH
    if not VerifyAuthenticatedHistoryProof(proofSet):
        return REJECT_FORK or HOLD_INSUFFICIENT_PROOF
    if HasAuthenticatedConflictingBranch(proofSet):
        return CONFLICT
    L = CertifiedLowerBoundOnCompatibleHistory(proofSet, policy)
    if L is unknown:
        return HOLD_INSUFFICIENT_PROOF
    if not DescendsFromCertifiedAnchor(state, proofSet):
        return REJECT_FORK
    if state.epoch < L:
        return REJECT_STALE
    if not CiphertextAvailableAndVerified(state):
        return HOLD_UNAVAILABLE
    return ACCEPT

AuthorizeRPHighRisk(session, stateProof, action, policy):
    if not ValidateRPBoundSessionAndOriginNonceChainId(session):
        return REJECT_AUTH
    if not CheckStateProofAgainstTrustedFinality(stateProof, policy):
        return HOLD_INSUFFICIENT_PROOF
    if not HasCurrentAllowedControlVersion(session, stateProof, action):
        return REJECT_AUTH
    return ACCEPT
```

## 3. 公平基线及研究比较的两个层次

| ID | 基线 | 主要解决的反对意见 |
|---|---|---|
| `B0` | 弱基线：本地签名/AEAD记录，仅验证对象，省略可信历史与新鲜度；仅用于错误示范。 | 弱对照/拟议方案 |
| `B2` | 强 Witness-only：应用签名与原子账户根、可验证前驱、合法法定人数、经过认证的外部恢复下界。 | 强基线 |
| `B3` | B2 + 非链独立认证公告：独立主体签名、不可静默改写及公告分发；与B4同频率同预算。 | 强基线 |
| `B4` | B2 + 公开链/L2最终化批量锚定：含经过认证的链信任起点、共识最终性/包含证明、应用根绑定。 | 强基线 |
| `B5` | B2 + 许可型独立BFT公告：同等节点独立性、共识容错预算与批量频率。 | 强基线 |
| `W0` | 仅在SIWE初始登录时验签，随后固定Cookie，会话不随控制权变更重检（弱）。 | 弱对照/拟议方案 |
| `W1` | SIWE/ERC-1271 + 短TTL + 常规通知/登出，未完整验证恶意RPC的数据来源。 | 弱对照/拟议方案 |
| `W_STAR` | 强标准组合：SIWE/ERC-1271 + 可信最终化链状态 + nonce/domain/chainId + TTL + OIDC Logout + 高风险重检。 | 强基线 |
| `W_P` | 拟议跨层执行门禁；必须与W_STAR采用同信任状态输入和高风险功能能力。 | 弱对照/拟议方案 |
| `P0` | 单账户、直接发布锚定（弱隐私基线）。 | 弱对照/拟议方案 |
| `P1` | 单发布者、固定周期批处理，但无独立匿名中继。 | 弱对照/拟议方案 |
| `P2` | 固定批次 + 独立发布者群组，允许多个账户共享批次。 | 弱对照/拟议方案 |
| `P3` | 强隐私基线：固定时间和大小批处理 + 匿名转发/发布 + 等效观察预算。 | 强基线 |
| `P4` | 拟议匿名投影/隐私证明 + 对照组相同批处理和转发预算。 | 弱对照/拟议方案 |

### 3.1 R1：同可信信息与同信任预算

保证输入的已认证事实、下界、发布确认时点、签名合法性、链历史和验收谓词等价。若 B4 具有比 B2 更多独立且可靠的证据，就属于 R2 而非 R1。在 R1 中出现差异时，先检查实现或策略差异，不能直接解释为密码学新性质。

### 3.2 R2：明确增加独立故障域

允许外部公告在 Witness 越界串谋后保存前序合法状态根；将 B3、B4、B5 的公告频率、主体验证能力、组织独立性、部署成本和证明可取回性设为可比较。若 B3/B5 与 B4 同样拒绝恶意回滚，研究结论应为“独立故障域带来条件性增益”，并对多种公告基础设施的 Pareto 边界进行评价。

公平性清单：相同合法业务功能、设备和签名可信假设、合法见证恢复下界、攻击可控对象、最迟接受时间/失败关闭政策、硬件与网络负载；单独记录共识独立性、信任引导成本、公告延迟与网络/隐私观察面。

## 4. Competing Hypotheses：主要预测及反证

| H | 主张 | 若成立观察 | 若被削弱观察 |
|---|---|---|---|
| `H0-L` | 链仅提供额外实现成本 | R1 安全判定一致；R2 中等独立公告等效 | 相同可信输入下存在确定性新增可验证性质 |
| `H1-L` | 公告跨故障域提供条件性恢复下界 | Witness 越界串谋后链曾锚定状态仍可被验证 | 在独立链已最终化条件下仍接受不一致旧状态 |
| `H2-L` | 无链独立公告/BFT 足以替代链 | B3/B5 与 B4 具有相同安全边界 | B4 在一致信任预算下有不可替代性质 |
| `H3-L` | 错误源于原始应用授权/历史检查缺陷 | 补齐 B2 应用认证后回滚/非法状态被拒 | 正确 B2 在有效同源下界仍失败 |
| `H0-W` | W_P 相比 W_STAR 无安全增益 | 同高度、TTL、通知时序下判定相同 | 强 W_STAR 仍有可复现额外攻击 |
| `H1-W` | 恶意 RPC 下存在新的跨层撤销门禁缺口 | 同证据下 W_STAR 错授权、W_P 拒绝 | W_STAR 已拒绝，差异仅来自额外查询 |
| `H0-P` | ZK 投影没有额外隐私作用 | 固定批处理+匿名转发与 P4 的优势相近 | 同预算下 P4 明显降低联合观测关联 |
| `H1-P` | 匿名投影降低真实联合观察泄漏 | 两世界攻击区分优势更低，合法恢复可用 | 真实RPC/时间辅助信息恢复关联优势 |

## 5. Experiment Matrix：强制映射 Claim/Hypothesis/Variable/Baseline

按 `E0 Sanity → E1 Mechanism/Discrimination → E2 Authorization → E3 Privacy → E4 Full/Failure` 的顺序实施。完整矩阵在随附 CSV 和 JSON，下面给出机制判断所必需的摘要。

| ID | Trace | Claim | 干预变量 | 必选对照 | 指标 | 若 H1 成立 | 若 H2/H0 成立 |
|---|---|---|---|---|---|---|---|
| `E0-01` | `TL5` | C02 | 错误授权设备/正确签名结构/已最终化公告 | B0,B2,B4 | invalid_accept_rate, business_auth_false_positive | 仅业务和历史双重核验拒绝 C_bad | 正确B2与B4均拒绝，链只提供历史证据 |
| `E0-02` | `TL1` | C01 | 见证确认e11；公告已最终化e10；S交付e10 | B2,B4 | verified_lower_bound_epoch, freshness_lag_epochs | 只取链公告时仅证e10，不构成绝对最新证据 | B4获完整见证下界11时与B2一致拒绝e10 |
| `E0-03` | `TL2` | C02,C03 | 见证诚实f内；旧签名状态e10重放，已认证e12 | B2,B3,B4,B5 | invalid_accept_rate, fork_detection | f内正确系统拒绝无新鲜度旧状态 | 所有强实现给出一致安全结论 |
| `E0-04` | `TL6` | C09 | 云端删除e12密文但元数据公告有效 | B2,B4 | true_recovery_rate, safe_reject_rate | 安全判定可获证据、业务无法恢复 | 任何共识后端均无法强迫云端交付 |
| `E1-01` | `TL2` | C03 | 见证串谋3/4；独立公告共识诚实；e12曾最终化；云回滚e10 | B2,B3,B4,B5 | invalid_accept_rate, certified_lower_bound | B4与B3/B5可拒绝基于恶意见证的旧回滚 | B3/B5具有同等安全，差异来自独立公告域 |
| `E1-02` | `TL2` | C04 | 给B2/B3/B4/B5相同认证转录/下界/应用谓词 | B2,B3,B4,B5 | decision_mismatch_rate, trusted_input_budget | 若出现可重复分离，需解释新信息来源 | 相同可信输入和策略得到相同判断 |
| `E1-03` | `TL2` | C03 | 见证串谋0,1,2,3,4；公告故障域独立与相关 | B2,B3,B4,B5 | fault_tolerance_envelope, invalid_accept_rate | 收益仅在独立公告保持诚实时出现 | 同等BFT/公告独立性具有同等容错边界 |
| `E1-04` | `TL2` | C10 | 同发布批次、同验证时点、同独立主体数与被监控状态 | B3,B4,B5 | safety_delta, proof_verify_ms | B4显示在一致安全语义下的额外可归因收益 | 强独立公告实现等效且成本可能较低 |
| `E2-01` | `TL3` | C05 | t_rev/t_fin/t_seen/t_admit；伪旧RPC h0；钱包h1撤销 | W0,W1,W_STAR,W_P | unauthorized_highrisk_accept_rate, revocation_reject_delay_ms | W_P比正确W_STAR具有显著额外安全边界 | W_STAR可信状态重检已拒绝旧控制权 |
| `E2-02` | `TL3` | C05 | 已最终化但RP延迟不可达；证据缓存TTL变化；fail-open/close | W1,W_STAR,W_P | stale_authorization_window_ms, legitimate_rejection_rate | 有界刷新能缩小可接受暴露窗口 | 只要等TTL与重检策略，差异即消失 |
| `E2-03` | `TL3` | C06 | 同验证链高度/同可信RPC/同登出事件/同会话TTL | W_STAR,W_P | paired_violation_delta, latency_p99_ms | 同证据条件仍可找到W_STAR失败而W_P成功轨迹 | 安全等效，复杂度/开销决定选择 |
| `E3-01` | `TL4` | C07 | 账户活动密度/批大小/固定间隔/发布者混淆/零知识投影 | P0,P1,P2,P3,P4 | linkability_advantage, top1_attribution_rate | P4在等额允许泄漏与预算下改善跨域关联 | P3普通固定批处理+匿名转发达到同等隐私 |
| `E3-02` | `TL4` | C07 | 观察者合并RPC IP地址、钱包活动、交易时序；账户稀疏 | P3,P4 | joint_view_advantage, account_activity_density | 隐私增益在严苛观察者下仍可量化 | 侧信道抵消密码学隐藏，改进很小 |
| `E4-01` | `TL6` | C08 | 链审查概率、最终化延迟、故障恢复网络分区 | B2,B3,B4,B5 | true_recovery_rate, safe_reject_rate | 增加独立公告域使跨故障场景更稳健 | 链审查引入新阻塞；无链备选可用性更高 |
| `E4-02` | `TL6` | C09 | 密文删除、见证日志不响应、RPC故障、公告存在 | B2,B3,B4,B5 | data_unavailable_rate, true_recovery_rate | 系统显式分类安全正确和数据可取回性 | 只增共识仍无法弥补云数据缺失 |
| `E4-03` | `ALL` | C10 | 账户数10^2/10^3/10^4；设备数2/4/8；事件突发/稀疏/混合 | B2,B3,B4,B5,W_STAR,W_P | p50_latency, p95_latency | 安全收益与资源开销在多负载下可控 | 强基线效果相同，新增开销成为代价 |

## 6. Minimum Viable Experiment（优先实现）

### E0：Sanity Check 与独立 Oracle

最小配置：1 个账户、2 台合法设备、1 台已撤销设备、1 个云服务器、4 个 Witness（示例 q=3）、两条合法历史分支、一个链/公告模拟器、一个独立 Oracle。先用 TL5 判定已最终化但未授权事件必须 `REJECT_AUTH`；再用 TL1 判定已确认而尚未锚定的更新只能从真实证据来源取得正确下界；附加验证云端删密文应标记 `HOLD_UNAVAILABLE`。**E0 可以用离散事件模拟器及有界状态机执行，无需部署公链。**

**门槛 E0-GATE**：对预注册的确定性轨迹，所有正确强基线与 Oracle 的业务授权、历史冲突和证据不足语义一致；如有偏离，记录独立实现错误并修复，暂停后续“安全领先”比较。零错误仅表示覆盖轨迹上的一致性，不构成任意攻击者下的密码学证明。

### E1：跨故障域最小区分性实验（最高信息增益）

先发布账户已授权 `S_12`，令一个独立外部公告获得可验证的最终化 `A_12`；之后让 `W` 中 3/4 见证者（超出示例 `f=1` 阈值）合谋向恢复客户端宣称历史合法但旧的 `S_10`，而无权伪造设备私钥。对 B2、B3、B4、B5 逐个回放，记录真实的 Oracle 结果、恢复策略对最新下界的处理、冲突检测和代价。

- **R1 反证对照**：将 `A_12` 包含的经过认证的信息等价地交给每个客户端，要求 B2/B3/B4/B5 在相同验收政策下判定一致。若 B2 能正确验证 `S_12` 的合法证据，回滚应被拒绝。
- **R2 独立域对照**：B2 在见证越界串谋后的下界可能受到污染，B3/B4/B5 依靠额外独立历史拒绝回滚。仅据此可以主张增加独立可信记录提高容错边界。
- **额外控制**：让外部公告与 Witness 同组织受控，验证独立性破坏后保证退化；并扫过串谋数量、发布间隔和见证客户端离线时间。

**E1 停止条件**：正确的 B3/B5 与 B4 无差异且 B4 无显著成本/隐私优势时，将链从核心创新降级为可替换后端；重点研究跨信任域可验证恢复规范及比较框架。

### E2：Web2/Web3 可验证会话撤销

在模拟合约账户中使 signer X 对链高度 h0 有效；RP 发放 SIWE 会话。在 h1 最终化撤销 X，恶意 RPC 向 RP 返回 h0。独立的 RP Oracle 依据已认证最终化状态与事先定义的会话新鲜度策略判断重要操作。分别测试 W0、W1、W_STAR、W_P。

**严格记录四个时间**：`t_rev`（撤销发出）、`t_fin`（撤销满足最终性）、`t_seen`（RP 获取有效证明）、`t_admit`（批准重要操作）。不能将 `t_fin` 后未观察到撤销的任意滞后都归为协议安全漏洞；要分别给出观察后安全、有界通知/刷新条件下的撤销窗口及证据过期后的失败关闭比例。W_STAR 已涵盖 ERC-1271/4361 + 可信状态源 + 短 TTL + OIDC Back-Channel Logout + 高风险重检。将其刻意弱化会产生无效创新结论。

### E3：多观察面账户不可关联性实验

定义两世界实验：隐藏位 `b∈{0,1}`，两个世界在允许泄漏 `ℒ` 上匹配账户数、公开批次槽位、总更新数和公开费用；差异只在用户真实账户与发布事件的隐藏对应。攻击者同时观察链、Witness、RPC 与指定钱包公开历史，输出对 b 的猜测。

`Adv_link = |Pr[hat_b=b] - 1/2|`，同时报告 Top-1 归属率、Top-k、实验世界基数、发布失败和恢复新鲜度延迟。若攻击者已拥有可唯一识别的 IP/钱包地址，仍应如实报告相关性泄漏。对照至少 P3（固定批处理+匿名中继）与 P4（匿名投影），匹配批大小、消息速率及允许的查询次数。采用稀疏/密集/突发三类合成行为负载，并公开生成器，真实工作负载仅在合法授权和去标识条件下使用。

### E4：审查与故障（Failure Oriented）

对锚定审查、链不可达、RPC 长时间返回旧头、Witness 超阈值串谋、云密文删除分别触发独立故障。输出 `safe_reject_rate`、`true_recovery_rate`、`timeout_rate`、`time_to_recovery`、`conflict_detection`。不要将拒绝风险状态计作成功恢复，也不要把链上公告误称为密文可用性保证。

## 7. Variables、Workloads 和消融

**独立变量**：`faulty_witness_count`、故障域相关性、`anchor_period`、`finality_delay`、`network_delay`、`rpc_state_age`、`session_ttl`、`logout_delay`、`batch_size`、`account_activity_skew`、`publication_id`、隐私中继开关、证明类型。**因变量**：业务/历史非法接纳、下界滞后、用户正确恢复/安全拒绝、RP误授权及撤销传播延迟、隐私区分优势、P50/P95/P99、验证CPU、存储/证明字节、原生Gas/成本。

**固定控制**：相同安全策略和合法功能、密码算法与密钥长度、设备签名注入方式、网络拓扑/故障概率、账户并发与日志规模、同一硬件容器、同样的最终性和可信引导、相同时间源、相同数据生成器种子。强基线与候选机制都应有等质量实现。不可直接把单节点 mock 链模拟器的延时结果当作真实公链吞吐结果。

**负载分层**：

1. 合成控制：1—10 个账户、2—4 台设备、小纪元数，进行有界全状态探索；便于归因。
2. 代表性合成：同时覆盖密码、TOTP、WebAuthn 元数据、Web3 钱包绑定、撤销、共享与恢复；可用外部文献选取频率参数，未经验证时明示“假设性分布”。
3. 压力与边界：示例规模 10²/10³/10⁴ 账户，2/4/8 设备，批量突发、失联/重组、长离线恢复、故障相关性极高。规模只是待测试网格，**不是已经达到的工程性能**。

**因果消融**：对 B4 移除链最终性校验、应用授权绑定、独立恢复信任点、见证回执、业务数据可取回性；对 W_P 分别关闭高风险操作重检、状态高度绑定、TTL 和登出通知；对 P4 关闭匿名投影而保留相同批次/中继。若消融移除了合法功能，需单列兼容损失，避免以关闭功能减少攻击当作胜利。

## 8. Metrics、统计与预注册

| 指标 | 定义和解释 | 容易误用之处 |
|---|---|---|
| `InvalidAcceptRate` | Oracle 确定业务非法/回滚的操作中，系统批准的比例 | 将 HOLD 与拒绝混合导致偏差 |
| `TrueRecoveryRate` | 同时完成最新可信状态核验、密文获取、解密加载的合法恢复比例 | 正确阻止回滚被误记成功 |
| `FreshnessLag` | 客户端验证下界相对真实已确认纪元的差异；必须说明真值来源 | 把链块高度直接当账户业务高度 |
| `ForkProofSuccess` | 有冲突时提供可第三方验证的相反证据的比例 | 仅给出告警不提供证据 |
| `RevocationWindow` | `t_fin→t_reject` 与 `t_seen→t_reject` 分开估计 | 混淆共识确认时间与RP知晓时间 |
| `Adv_link` | 均匀两世界条件下 `|Pr[猜中]-0.5|` | 攻击样本重复、世界先验不平衡 |
| `Latency` | P50/P95/P99，区分正常热路径、恢复冷路径与证明验证 | 不区分缓存预热和网络往返 |
| `Trust/Cost` | 独立组织/治理主体数、证明/消息字节、交易费用和部署成本 | 将增加额外可信资源误归因算法 |

安全性质主要采用 Oracle 一致性、最小反例、故障阈值和有界模型探索；不能以“统计不显著”证明两协议安全等价。隐私两世界实验建议先对每条件 30 个独立随机种子做 pilot，再基于观测方差决定样本量及最小有意义效应；事前定义 95% 置信区间和配对采样方案。性能实验建议每个配置至少 30 次独立重复并报告中位数、P95/P99 与自助法置信区间（极端尾延迟需要更多采样才能稳定）；具体样本量将通过 pilot 校准。多工作负载结果保留反例与全部原始日志，不只报告平均数。

建议预先设定分层判定：正确性不变量为零容忍（在测试覆盖内）；关键主张需形成最小可复现分离轨迹并通过独立 Oracle；真正的工程优越性需报告置信区间与实用效应值。显著性不能替代安全机制因果解释。不得在观察结果后临时修改 H1 成立门槛。

## 9. Reproducibility：软件设施与原始记录

**拟议实现**：Python 3.11+ 模型与攻击轨迹生成器；Rust 1.8x 稳定版或 Go 1.2x 稳定版账户Core/Witness服务；容器化网络与故障注入；本地模拟 EVM/RPC（真实 RPC/链上成本实验另列）；SQLite/RocksDB 可选作为日志后端。版本在真正开工时锁定 commit、digest、依赖文件与工具链，当前仅说明技术选项，不虚构运行环境。标准仿真可参考 C2SP Witness、Parakeet、SIWE/ERC-1271 与 OIDC Logout；实际实现需要核对具体开源项目许可证和兼容性。

**最低仓库模块**：`core/`、`oracle/`、`witness/`、`announcement/{signed-board,bft,evm}/`、`rp/`、`fault-injector/`、`privacy-attacker/`、`workloads/`、`analysis/`。先实现 `oracle/` 与 `fault-injector/`，实现 E0/E1 后再扩展 RP/隐私模块。

**单次运行日志必需字段**（详见 JSON manifest）：`run_id, experiment_id, baseline_id, seed, simulated_time, actor_id, action, event_id, epoch, predecessor_root, account_root, device_signature_valid, authorization_version, witness_votes, external_checkpoint, checkpoint_finalized, recovery_lower_bound, rp_session_version, rpc_reported_height, oracle_decision, system_decision, latency_ns, bytes_tx, proof_bytes, error_code`。

每次执行保存硬件规格、操作系统、容器镜像 digest、编译器/依赖版本、系统时钟、故障配置、随机种子、原始事件日志与错误输出，实验矩阵必须有 `source_revision` 和 `baseline_commit`。上传匿名样例时不得包含真实账户名、个人钱包助记词或会话令牌。

## 10. Failure-oriented experiments：主动寻找新方案最差场景

- 链审查无限延迟而 Witness 可访问：比较阻塞时间和业务可用性。
- 见证越界串谋且发布者与见证受同一组织控制：检验安全增益依赖的真实独立性。
- 公告与 Witness 提供互斥的已认证分支：输出 `CONFLICT`，不得盲目选择更高 epoch。
- 旧 RP 会话在撤销已最终化、RPC 离线及通知失联下申请高风险操作：严格区分可靠撤销与合法业务中断。
- 隐私攻击者同时拥有钱包地址和单用户稀疏事件：评估链/RPC 侧信道导致的身份关联。
- 云端删除全部最新密文：测量安全拒绝与真实恢复的不同边界。

## 11. Stop / Pivot / Go 门槛（当前预注册建议）

| 决策 | 准入依据 | 科研点处理 |
|---|---|---|
| **GO—安全协议** | 正确最强基线在公平条件下存在独立 Oracle 证实的最小攻击轨迹，拟议机制拒绝且保持同功能；排除额外未经声明的可信输入差异 | 深化形式化模型、协议设计与完整系统实现 |
| **GO—条件性容错** | R2 条件下新增独立公告域提供证明级故障边界；与 B3/B5 成本/隐私/治理对照有明确新发现 | 表述为跨故障域保证与实施权衡，勿声称链必然优越 |
| **PIVOT—系统评测** | B3/B4/B5 安全相同，但隐私、吞吐、证据成本或离线恢复存在可复现 Pareto 权衡 | 将贡献定位为定量模型、评价框架和优化机制 |
| **PIVOT—跨范式** | W_STAR 存在实际验证难题或不可接受的安全/可用性取舍，而 W_P 展现可证明的改进 | 聚焦 Web2/Web3 的高风险授权与恢复 |
| **PARK—新增链机制** | 相同可信预算下 B4 无独立收益，且等独立B3/B5安全覆盖并具有更低成本 | 链作为可选公告后端，不列为主创新 |
| **STOP/REVISE** | E0基础Oracle不可信、强基线难以公平实现或真实系统要求与威胁模型矛盾 | 暂停完整 benchmark，返回 Discovery/Critique 重定义问题 |

停止规则是对具体主张的判断，允许负面结果成为有效的科学研究产物。所有决策在实测后才形成最终 Decision。

## 12. Research Point 与阶段交接

| 研究点 | 前序建议 | 本阶段拟议 | 最大未解问题 | 下一信息增益 |
|---|---|---|---|---|
| RP-2026-005 | CHALLENGE | VALIDATION_DESIGN（建议） | B4与B3/B5是否可分离，安全收益是否仅来自独立域 | 实现 E0/E1 并保存差分轨迹 |
| RP-2026-006 | CHALLENGE | VALIDATION_DESIGN（建议） | 强 W_STAR 下是否存在可复现缺口 | E2 TL3 |
| RP-2026-008 | CHALLENGE | VALIDATION_DESIGN（建议） | P4超越普通匿名批处理的优势是否真实 | E3 TL4 |
| RP-2026-007 | PARKED | PARKED | 网站主动接入必要性及推广成本 | Mock RP WebAuthn/SIWE/OIDC接口演示 |

与 V1 的关系保持：RP-001—003 仍为 `CANDIDATE` 的历史卡；RP-004 仍为 `PARKED`；不合并或静默改写旧卡。当前 **FROZEN = 0（对 V2 新研究点而言）**，执行结果为零，Gap 最高保持 `POSSIBLE`。

**Next Best Action**：实现最小离散事件 Oracle 与 E0-TL1/TL5 预注册回归，随后执行 TL2 的 R1/R2 公平分离性实验；只有E1存在有价值证据时再启动完整区块链、智能账户和匿名证明系统。

## 13. 核心参考与事实/推断边界

### [SOURCE] 项目资料

- `00_PROJECT_CHARTER.md`：Observation、Hypothesis、Evidence 和 Decision 分离；Research Point 生命周期。
- `50_EXPERIMENT_DESIGN_SKILL.md`：Claims→Hypotheses→Baselines→Variables→Metrics→Ablation→Failure/Stop。
- `扩展研究V2_第四阶段_Hypothesis_Critique_2026-10-15.md`：TL1—TL6、R1/R2及主假设。
- `密码管理器研究方案_整合版.docx`：PACW、FICAP、RSPK及本地可信执行边界。

### [PRIMARY] 外部论文/规范（供实现时再次校验）

1. Malvai et al., *Parakeet: Practical Key Transparency for End-to-End Encrypted Messaging*, NDSS 2023, https://www.ndss-symposium.org/ndss-paper/parakeet-practical-key-transparency-for-end-to-end-encrypted-messaging/
2. C2SP, *Transparency Log Witness Protocol*, https://c2sp.org/tlog-witness
3. C2SP, *Transparency Log Policy*, https://c2sp.org/tlog-policy
4. Ethereum, *Weak Subjectivity*, https://ethereum.org/developers/docs/consensus-mechanisms/pos/weak-subjectivity
5. ERC-4361, *Sign-In with Ethereum*, https://eips.ethereum.org/EIPS/eip-4361
6. ERC-1271, *Standard Signature Validation Method for Contracts*, https://eips.ethereum.org/EIPS/eip-1271
7. OpenID Foundation, *OpenID Connect Back-Channel Logout 1.0*, https://openid.net/specs/openid-connect-backchannel-1_0-final.html
8. W3C, *Bitstring Status List v1.0*, https://www.w3.org/TR/vc-bitstring-status-list/
9. Pang et al., *Zanzibar: Google's Consistent, Global Authorization System*, USENIX ATC 2019, https://www.usenix.org/conference/atc19/presentation/pang

以上原始文献支持“基线存在及其声明的功能”，**不直接证明本项目提出的新协议已有独立创新**。新增状态语义、假设模型和预期攻击分离均属于 `[INFERENCE]` / `[HYPOTHESIS]`。

## 14. 版本与决策日志

- **V2-DESIGN-r1**（2026-10-15）：继承 V2-Critique-r1，预注册 Claims C01—C10、16组实验、R1/R2公平性、Oracle和Fail-oriented方案；建议 RP-005/006/008 进入 `VALIDATION_DESIGN`，不修改既有已冻结/候选卡。**本阶段不记录实测成功率、延迟或创新证明。**
