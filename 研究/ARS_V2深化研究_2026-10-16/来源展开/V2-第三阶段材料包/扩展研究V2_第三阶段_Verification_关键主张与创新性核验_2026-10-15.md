# 硕士毕业设计扩展研究 V2：第三阶段关键主张核验与创新性审查

**日期**：2026-10-15　**版本**：V2-VERIFY-r1　**Skill**：`30_VERIFICATION_SKILL.md`　**状态**：`EVIDENCE_SCAN` → `CHALLENGE` 建议交接（非自动冻结）。

**审查范围**：RP-2026-005（分布式见证/链上锚定）、RP-2026-006（Web2/Web3 状态与会话）、RP-2026-008（公开锚定隐私与成本）；RP-2026-007（网页范式改造）仅验证接口标准与部署边界。继承 V1 研究点状态且不修改原始研究卡。

**证据类别**：`[SOURCE]` 为用户提供的 Word 与 V2 第一、二阶段资料；`[PRIMARY]` 原始会议论文/正式技术标准/出版商记录；`[INFERENCE]` 明示推论；`[HYPOTHESIS]` 待验证实验主张；`[UNKNOWN]` 不足以断言的命题。

**工作性质**：这一阶段完成网页公开原始资料与 Parakeet 全文关键章节核验、规范条款核验、摘要级研究边界核验。没有执行真实协议实验、没有部署真实链，也没有为新颖性给出 CONFIRMED。报告使用来源标识 S01–S18 对应可核验网址/文档，非论文原文的内容明确标出。

## 0. Executive Decision

1. **RP-005：核心“链天然胜过 Witness-only”目前为 UNVERIFIED。** Parakeet 是具有明确故障阈值及异步安全语义的强替代基线。额外链锚定只有在增加了不同的可信公共历史或故障容忍假设、且对应更新已被最终化时才可能增加可检测性；这需要独立定义其信任成本。
2. **RP-006：宽泛“合约控制变化后首次撤销网站会话”主张为 CONTRADICTED。** ERC-4361 已在 Session Invalidation 章节提到依照 ERC-1271 状态变更失效会话，并提出 webhook 示例。具体创新候选仅剩恶意链查询条件下的跨层时序/确认语义、可验证状态证明与撤销窗口界。
3. **RP-008：哈希上链并不保证账户不可关联。** W3C Bitstring Status List 提供成熟链下批量隐私基础，研究点仍可作为有条件的测量/权衡贡献保留。
4. **RP-007：保留长期候选。** WebAuthn、SIWE、OpenID4VP、DID Core 已有正式标准，无法在任意不合作网站上直接替代 RP 的认证流程。
5. **核心风险**：即使获得法定人数签名或区块链终局性，仍须单独证明应用层账户状态迁移、授权签名与凭据状态语义；一致的历史不能自动推出合法的业务操作。

## 1. Verification Target 与原子命题划分

以第二阶段 V2-C1—C8 为检索入口，本阶段细化为 **18 条**原子命题（V2-C01—V2-C18）。Claim Type 分为 FACT、NOVELTY、NEGATIVE、CAUSAL、HYPOTHESIS、EVALUATION；对新颖性与不存在已有方法的陈述采用最高验证门槛。完整内容另见 CSV。

### 1.1 证据置信度含义

- `VERIFIED`：原始论文、规范中有明确支撑的具体事实（只在特定前提内使用）。
- `PARTIALLY_SUPPORTED`：命题部分成立，重要范围或因果关系需要收缩。
- `CONTESTED`：正反证并存，无法直接下结论。
- `UNVERIFIED`：仍未取得足够证据支持，创新主张不可确认为事实。
- `CONTRADICTED`：现有原始工作或机制反例与宽泛主张明确冲突。

## 2. Atomic Claims — 完整核验记录

| ID / 研究点 | 核验命题（简写） | 类别 | 当前结论 | 核心证据 | 对研究点影响 |
|---|---|---|---|---|---|
| V2-C01 / RP-005 | 链相对 B2 的独立安全分离性 | NOVELTY | `UNVERIFIED` | S01, S02, S03, S04 | RP-005 不得宣称区块链带来必然新鲜度保证。 |

| V2-C02 / RP-005 | Parakeet consensusless 适用边界 | FACT | `VERIFIED` | S01 | 构成 RP-005 强竞争基础。 |

| V2-C03 / RP-005 | C2SP Witness 和 Policy 现有功能 | FACT | `VERIFIED` | S02, S03 | 不得将 quorum 签名视为 PACW 首创。 |

| V2-C04 / RP-005 | 无历史设备必然无法使用 Witness-only | NEGATIVE | `CONTESTED` | S01, S02 | 收缩恢复 gap 到明确故障和新鲜度定义。 |

| V2-C05 / RP-005 | 链上密码管理和透明性已有先例 | FACT | `VERIFIED` | S09, S10, S11 | 禁止主张首次提出链上密码管理器或哈希锚定。 |

| V2-C06 / RP-005 | 链上检查点=绝对最新状态 | FACT | `CONTRADICTED` | S04, S05 | 从 RP-005 删除绝对最新保证。 |

| V2-C07 / RP-005 | 见证串谋时链终局的条件性收益 | HYPOTHESIS | `PARTIALLY_SUPPORTED` | S04, S05, S09 | 应研究信任失效组合而非无条件安全优越。 |

| V2-C08 / RP-006 | ERC-1271 动态验签 | FACT | `VERIFIED` | S07 | 可作为 RP-006 准确背景事实。 |

| V2-C09 / RP-006 | 首创合约状态变化的会话失效 | NOVELTY | `CONTRADICTED` | S06, S07 | RP-006 缩小创新范围。 |

| V2-C10 / RP-006 | OIDC 后通道登出 | FACT | `VERIFIED` | S08 | RP-006 必须以此为强对照。 |

| V2-C11 / RP-006 | 跨 Web2/Web3 撤销的独立 gap | NOVELTY | `UNVERIFIED` | S06, S07, S08, S16 | 暂保留 RP-006 CHALLENGE 候选。 |

| V2-C12 / RP-007 | WebAuthn/SIWE/DID/VC 接入边界 | FACT | `VERIFIED` | S06, S13, S14, S15 | RP-007 PARKED，兼容验证可做。 |

| V2-C13 / RP-008 | 哈希上链自动保证隐私 | FACT | `CONTRADICTED` | S12, S15 | RP-008 有风险分析与测量价值。 |

| V2-C14 / RP-008 | Bitstring 批量隐私先例 | FACT | `VERIFIED` | S12 | RP-008 广义批处理隐私非首创。 |

| V2-C15 / RP-008 | 隐私投影显著优于固定批处理 | HYPOTHESIS | `UNVERIFIED` | S12, S18 | 仅保留测量型 POSSIBLE Gap。 |

| V2-C16 / RP-005/006 | 强基线公平比较 | EVALUATION | `PARTIALLY_SUPPORTED` | S01, S03, S04, S17 | 严禁只比较不公平弱基线与新增链。 |

| V2-C17 / RP-005/006 | 终局性=应用授权合法性 | CAUSAL | `CONTRADICTED` | S01, S02, S16, S18 | 应将认证授权与历史一致性作为两个独立证明义务。 |

| V2-C18 / RP-005/008 | 链锚定=数据可用性 | FACT | `CONTRADICTED` | S04, S09, S18 | 立项不得承诺链上锚定解决数据丢失。 |

## 2.1 按命题逐项记录（证据支持/反证/剩余不确定性）

### V2-C01｜RP-005｜`UNVERIFIED`

**原子命题**：在相同信任输入下，B2 无法拒绝而 B4 可以拒绝至少一类过期状态。

**类型**：NOVELTY。

**支持证据**：Parakeet 已在异步网络和恶意见证者模型下实现一致承诺分发；链可作为独立公共检查点。。

**最强反证或限制**：无法得到相同信任输入、等确认时点的差分攻击轨迹；新增共识本身意味着扩大信任来源。。

**来源质量与范围**：S01;S02;S03;S04；证据等级依附附录来源表标记，摘要级来源仅用于验证是否存在相应设计，不推断其完整证明。

**剩余不确定性/下一验证动作**：严格定义两个方案可观测信息、可访问可信方及最终化时点，设计可区分轨迹。

**影响**：RP-005 不得宣称区块链带来必然新鲜度保证。

### V2-C02｜RP-005｜`VERIFIED`

**原子命题**：Parakeet 完全无需区块链共识即可达到其定义的承诺一致性。

**类型**：FACT。

**支持证据**：NDSS 原论文明确提出 consensusless、3f+1 见证者、2f+1 quorum、异步最终消息投递、同一 epoch 非双视图。。

**最强反证或限制**：目标限于其密钥透明性一致性模型，并信任 IdP 正确授权用户操作，需至少每 epoch 一名诚实审计者。。

**来源质量与范围**：S01；证据等级依附附录来源表标记，摘要级来源仅用于验证是否存在相应设计，不推断其完整证明。

**剩余不确定性/下一验证动作**：避免把其保证误写成完整恶意密码库恢复或实时最新性。

**影响**：构成 RP-005 强竞争基础。

### V2-C03｜RP-005｜`VERIFIED`

**原子命题**：C2SP Witness 和 Policy 已具备检查点一致性与法定人数离线验签。

**类型**：FACT。

**支持证据**：规范定义签名验证、Merkle consistency、cosign、原子持久化、quorum/group。。

**最强反证或限制**：策略验证检查点而不验证日志中业务凭据授权；v1.0.0 Monitor Retrieval 仍标注 TBD。。

**来源质量与范围**：S02;S03；证据等级依附附录来源表标记，摘要级来源仅用于验证是否存在相应设计，不推断其完整证明。

**剩余不确定性/下一验证动作**：对照完整状态认证和可信恢复下界时需另设业务验证与监控端。

**影响**：不得将 quorum 签名视为 PACW 首创。

### V2-C04｜RP-005｜`CONTESTED`

**原子命题**：已有 Witness-only 系统无法支持无历史设备恢复。

**类型**：NEGATIVE。

**支持证据**：恶意云可提供旧签名状态而新设备无历史时产生歧义。。

**最强反证或限制**：Parakeet WitnessAPI.GetCom、独立见证查询与 B2 外部恢复下界已是可能替代路径。。

**来源质量与范围**：S01;S02；证据等级依附附录来源表标记，摘要级来源仅用于验证是否存在相应设计，不推断其完整证明。

**剩余不确定性/下一验证动作**：按是否存在认证且可访问的最新下界源分情况陈述。

**影响**：收缩恢复 gap 到明确故障和新鲜度定义。

### V2-C05｜RP-005｜`VERIFIED`

**原子命题**：区块链锚定及区块链密码管理器为已有公开研究。

**类型**：FACT。

**支持证据**：CertLedger、SecureVault、PassChain 出版商原始记录包含相关构造。。

**最强反证或限制**：全文证明、实测攻击复现和新设备恢复性能无充分可得原始细节；仅凭摘要无法推定覆盖全部目标。。

**来源质量与范围**：S09;S10;S11；证据等级依附附录来源表标记，摘要级来源仅用于验证是否存在相应设计，不推断其完整证明。

**剩余不确定性/下一验证动作**：冻结 novelty 前获取论文正文/代码并复核可比威胁模型。

**影响**：禁止主张首次提出链上密码管理器或哈希锚定。

### V2-C06｜RP-005｜`CONTRADICTED`

**原子命题**：已最终化的链上检查点可直接证明绝对最新账户状态。

**类型**：FACT。

**支持证据**：共识最终性确认已被纳入的区块内容。。

**最强反证或限制**：存在更新未发布、交易审查、离线/分区、数据库不可用、PoS 新节点弱主观性等边界。。

**来源质量与范围**：S04;S05；证据等级依附附录来源表标记，摘要级来源仅用于验证是否存在相应设计，不推断其完整证明。

**剩余不确定性/下一验证动作**：将安全保证定义为某可信提交时点的下界；记录可用性与发布时延。

**影响**：从 RP-005 删除绝对最新保证。

### V2-C07｜RP-005｜`PARTIALLY_SUPPORTED`

**原子命题**：公开链能在所有见证者串谋时提供额外不可抵赖历史。

**类型**：HYPOTHESIS。

**支持证据**：如果链最终性独立且客户端拥有可信链检查点、相关应用状态已锚定，则已最终化承诺可被验证。。

**最强反证或限制**：新增独立共识信任；未发布更新、锚定器恶意提交、链数据不可达、账户绑定错配都可能失败。。

**来源质量与范围**：S04;S05;S09；证据等级依附附录来源表标记，摘要级来源仅用于验证是否存在相应设计，不推断其完整证明。

**剩余不确定性/下一验证动作**：明确公开链独立假设及证据，和 BFT 替代来源进行等信任资源对照。

**影响**：应研究信任失效组合而非无条件安全优越。

### V2-C08｜RP-006｜`VERIFIED`

**原子命题**：ERC-1271 验签具有状态/时间上下文依赖性。

**类型**：FACT。

**支持证据**：标准允许依赖钱包授权、时间、合约状态的 isValidSignature 检查，并须用调用而非 EOA recovery 验证。。

**最强反证或限制**：合约状态的可信高度、链身份、最终性、RPC 来源由部署者额外决定。。

**来源质量与范围**：S07；证据等级依附附录来源表标记，摘要级来源仅用于验证是否存在相应设计，不推断其完整证明。

**剩余不确定性/下一验证动作**：把 chainId, block reference, proof provenance 与 session state 绑定。

**影响**：可作为 RP-006 准确背景事实。

### V2-C09｜RP-006｜`CONTRADICTED`

**原子命题**：首次提出 ERC-1271 账户控制权改变后撤销 Web2 会话。

**类型**：NOVELTY。

**支持证据**：ERC-4361 的 Session Invalidation 已明确提示对 ERC-1271 状态改变使相关会话失效，举 webhook 方案。。

**最强反证或限制**：尚无一般网络条件下的硬时限保证，具体业务策略需另定义。。

**来源质量与范围**：S06;S07；证据等级依附附录来源表标记，摘要级来源仅用于验证是否存在相应设计，不推断其完整证明。

**剩余不确定性/下一验证动作**：删除“首次撤销”主张，聚焦可验证链状态与传播时限。

**影响**：RP-006 缩小创新范围。

### V2-C10｜RP-006｜`VERIFIED`

**原子命题**：OIDC Back-Channel Logout 已提供 RP 服务器间登出通知。

**类型**：FACT。

**支持证据**：Final 规范定义 Logout Token，RP 维护会话并收取 OP HTTP POST。。

**最强反证或限制**：要求双方采用协议，消息可靠性、RP 处理和网络条件影响最终失效时间。。

**来源质量与范围**：S08；证据等级依附附录来源表标记，摘要级来源仅用于验证是否存在相应设计，不推断其完整证明。

**剩余不确定性/下一验证动作**：对比 nonce, TTL, logout token, webhook, 重新验签组合基线。

**影响**：RP-006 必须以此为强对照。

### V2-C11｜RP-006｜`UNVERIFIED`

**原子命题**：在恶意 RPC 和链重组风险下跨 Web2/Web3 撤销一致性存在独立 gap。

**类型**：NOVELTY。

**支持证据**：1271 的链状态上下文与网站独立会话构成可比较的时序边界。。

**最强反证或限制**：SIWE+finalized block+webhook/short TTL+Logout 可能等价满足指定性质。。

**来源质量与范围**：S06;S07;S08;S16；证据等级依附附录来源表标记，摘要级来源仅用于验证是否存在相应设计，不推断其完整证明。

**剩余不确定性/下一验证动作**：定义何时安全终止、允许的在线查询与延迟，构造强基线失败轨迹。

**影响**：暂保留 RP-006 CHALLENGE 候选。

### V2-C12｜RP-007｜`VERIFIED`

**原子命题**：WebAuthn、SIWE、OpenID4VP 和 DID/VC 已有互操作基础。

**类型**：FACT。

**支持证据**：W3C WebAuthn3、ERC-4361、OpenID4VP Final、DID Core 分别提供认证、钱包签名、VC 呈示与标识解析。。

**最强反证或限制**：各协议角色不同；DID 并不天然需链；RP 需要主动接入/授权；无单方改变任意网站认证条件。。

**来源质量与范围**：S06;S13;S14;S15；证据等级依附附录来源表标记，摘要级来源仅用于验证是否存在相应设计，不推断其完整证明。

**剩余不确定性/下一验证动作**：以 Mock RP 和自愿接入网站的接口适配为可行性研究边界。

**影响**：RP-007 PARKED，兼容验证可做。

### V2-C13｜RP-008｜`CONTRADICTED`

**原子命题**：链上只写哈希意味着账户状态隐私有密码学保证。

**类型**：FACT。

**支持证据**：哈希承诺隐藏直接密文内容取决于输入熵、承诺方式与攻击模型。。

**最强反证或限制**：可观察时序、发送地址复用、成员事件、访问请求及已知字典可能泄露关联。。

**来源质量与范围**：S12;S15；证据等级依附附录来源表标记，摘要级来源仅用于验证是否存在相应设计，不推断其完整证明。

**剩余不确定性/下一验证动作**：定义链上及链下联合观察面，不声称无链接性。

**影响**：RP-008 有风险分析与测量价值。

### V2-C14｜RP-008｜`VERIFIED`

**原子命题**：隐私保护的批量凭据状态与撤销机制已有标准。

**类型**：FACT。

**支持证据**：W3C Bitstring Status List 1.0 以大规模状态位图和缓存降低用户跟踪，讨论相关性。。

**最强反证或限制**：规范明确恶意发行方/验证者共谋和唯一标识符仍能破坏群体隐私。。

**来源质量与范围**：S12；证据等级依附附录来源表标记，摘要级来源仅用于验证是否存在相应设计，不推断其完整证明。

**剩余不确定性/下一验证动作**：与固定时间批处理、混合发布和无链位图强基线比较。

**影响**：RP-008 广义批处理隐私非首创。

### V2-C15｜RP-008｜`UNVERIFIED`

**原子命题**：批量锚定与隐私投影优于固定批处理和公开链最小元数据方案。

**类型**：HYPOTHESIS。

**支持证据**：跨账户承诺与匿名投影有潜在可归因的隐私收益。。

**最强反证或限制**：无真实交易、客户端访问信道观测及隐私攻击，优势可能来自批大小及访问策略。。

**来源质量与范围**：S12;S18；证据等级依附附录来源表标记，摘要级来源仅用于验证是否存在相应设计，不推断其完整证明。

**剩余不确定性/下一验证动作**：设计隐私区分游戏，控制发送者、时间桶、批大小和受攻击者辅助知识。

**影响**：仅保留测量型 POSSIBLE Gap。

### V2-C16｜RP-005/006｜`PARTIALLY_SUPPORTED`

**原子命题**：B1/B2/B3/B4 可在绝对一致的信任资源与故障条件下公平比较。

**类型**：EVALUATION。

**支持证据**：可以统一业务功能、攻击输入、恢复窗口及观测指标。。

**最强反证或限制**：公共链最终性与 Witness quorum 的独立主体及信任边界天然不同。。

**来源质量与范围**：S01;S03;S04;S17；证据等级依附附录来源表标记，摘要级来源仅用于验证是否存在相应设计，不推断其完整证明。

**剩余不确定性/下一验证动作**：设计固定资源消融和目标差异威胁模型两套比较，分别解释。

**影响**：严禁只比较不公平弱基线与新增链。

### V2-C17｜RP-005/006｜`CONTRADICTED`

**原子命题**：在不可信同步情况下状态最终性足以证明账户授权的正确性。

**类型**：CAUSAL。

**支持证据**：已最终化承诺可对历史数据作哈希绑定。。

**最强反证或限制**：共识不会自动验证应用签名、成员资格、撤销资格、WebAuthn RP 或功能授权语义。。

**来源质量与范围**：S01;S02;S16;S18；证据等级依附附录来源表标记，摘要级来源仅用于验证是否存在相应设计，不推断其完整证明。

**剩余不确定性/下一验证动作**：独立检查应用状态转移证明、撤销事件与同纪元授权，再做最终性判定。

**影响**：应将认证授权与历史一致性作为两个独立证明义务。

### V2-C18｜RP-005/008｜`CONTRADICTED`

**原子命题**：链上仅批量提交检查点就可保证数据可用性及恢复成功。

**类型**：FACT。

**支持证据**：链能公开批量承诺的时间和根。。

**最强反证或限制**：云端恶意删除密文时链上根无法重建原密文；需要额外副本与检索机制。。

**来源质量与范围**：S04;S09;S18；证据等级依附附录来源表标记，摘要级来源仅用于验证是否存在相应设计，不推断其完整证明。

**剩余不确定性/下一验证动作**：区分 safety / freshness / data availability / liveness 四类结果。

**影响**：立项不得承诺链上锚定解决数据丢失。

## 3. 最强支持证据及真正研究边界

### 3.1 Parakeet：全文审查结果（S01）

- `[PRIMARY]` §II.A：`n=3f+1` witness、`q=2f+1`、至多 `f` Byzantine，允许完全异步消息调度且最终交付；同纪元输出的一致承诺必须相同，提供 Validity/Termination 的特定含义。任意两法定人数至少重叠 `2q−n=f+1` 名见证者，因至多 f 为恶意，交集至少含 1 名诚实节点。
- `[PRIMARY]` §II.A 与 §II.C：IdP 被信任能正确执行用户操作授权；并非所有 IdP 行为都由 Parakeet 的一致承诺保证。VKD 的私钥映射审计还依赖每个 epoch 至少一名诚实审计者。
- `[PRIMARY]` §II.C：WitnessAPI 提供每纪元 commitment 查询与证书验证机制（ProposeNewEp/GetCom/VerifyCert），需与 PACW 全设备丢失恢复基线比较。
- `[PRIMARY]` §VII：作者明确指出 EthIKS、Catena 已将区块链用于密钥透明度，并讨论无需共识的替代方式。
- `[INFERENCE]` 该论文足以否定“必须使用区块链才可能获得非分叉见证历史”的通用表述；尚无法直接否定“恶意凭据服务器+多对象跨版本授权+用户全设备丢失”的更窄复合研究问题。

### 3.2 C2SP：检查点签名与业务状态资格的边界（S02–S03）

C2SP tlog-witness v1.0.0 通过可信日志签名、Merkle 一致性证明、见证者签名和原子持久化维护历史演进。tlog-policy 已支持按组配置的阈值法定人数。当前稳定公开文本对 Monitor Retrieval Mechanism 仍列为讨论中（TBD）；这一事实表示该版本尚缺少完整标准化监控取回流程描述，**不意味着没有任何可实现监控或见证查询实现**。

其检查点只对日志身份及历史一致性提供特定认证，应用层必须单独处理设备能力、撤销、账户状态以及恢复时使用哪个已确认下界。

### 3.3 区块链：保证精确拆分（S04–S05,S09）

设 `S_e` 为第 e 纪元账户状态，`C_e=Commit(S_e)` 为检查点承诺；`A_k` 为区块 k 内已最终化的锚定。可以讨论的核心结论是：拥有**可信共识检查点、真实成员/状态证明、包含证明、正确应用绑定**的恢复方，可以验证某个 `C_e` 在已经最终化的公共历史中。该证据只为 `e` 提供可信下界，不证明不存在 `e+1` 已被用户确认但尚未发布的更新。

需拆分五种性质：`Historical Integrity`（历史不可悄然改写）、`Fork Consistency`（同纪元分支不能同时被采信）、`Recovery Freshness Lower Bound`（恢复达到可信新鲜度下界）、`Data Availability`（密文实际可获取）和 `Authorization Validity`（更新符合用户权限）。链锚定主要作用于前两者及特定条件下的第三者，后两者需要独立机制。

### 3.4 Web2/Web3：正式标准已覆盖的范围（S06–S08,S13–S15）

- ERC-1271 允许当前智能账户合约根据状态与时间验证签名，并要求函数为只读调用；其输出不是永久有效的证据。
- ERC-4361 §Session Invalidation 已提出当 1271 等合约签名验证规则变化时应使相关网站会话失效，并举出 webhook 触发的设计例子。
- OpenID Back-Channel Logout Final 定义 OP 给 RP 发送签名 Logout Token 的流程；要有效终止具体会话，RP 必须支持协议并维护会话映射。
- WebAuthn 3、OpenID4VP 1.0、DID Core 分别覆盖网站公钥认证、可验证凭据呈示、DID 标识与解析；三者角色不同。需要网站支持相应 RP 接口。

### 3.5 隐私：承诺与可链接性不同（S12）

W3C Bitstring Status List Recommendation 的隐私章节明确考虑唯一标识符、状态访问、缓存、恶意发行方/验证者、时序更新及状态消息关联；标准还指出批量发布隐私增益可因攻击者与发行方共谋而减弱。由此推论，公共链聚合根对口令明文的隐藏与账户关联隐私属于两种安全目标，应分别衡量。

## 4. Reviewer 式最强反对意见

**O1：为什么不用 Parakeet + 可信恢复下界而额外增加区块链？**

在 q 法定人数与认证观察者可访问条件相同的模型中，单单多一个哈希副本不必然阻止此前无法阻止的旧状态接受。若方案靠“独立公链多数诚实”而获益，它实际上引入另一组治理/信任主体。此类收益可以合法研究，但必须明确增加了什么输入、代价与容错假设。

**O2：为什么不是 ERC-4361 原有 Session Invalidation 与 OIDC Back-Channel Logout 的正常组合？**

需选择一项更窄的可验证命题：恶意 RPC、链重组、延迟通知、错位授权纪元下，某网站能否在已接受的最终化下界之后执行不该执行的操作。若原有短 TTL + webhook + 1271 重验签满足同一谓词，则研究应改为量化窗口/负载代价。

**O3：承诺频次、链费用和可关联风险是否只是显然的工程权衡？**

必须给出有可复现方法的侧信道攻击者视图、泄漏函数、误检、区分优势、链最终性/检查点刷新等联合指标，否则无法形成独立测量研究。

## 5. 最小可证伪轨迹与公平对照——仅为设计，未执行

### T-L1：已确认但未上链的安全状态（戳穿“绝对最新”）

`e0` 已在 Witness 与链上；`e1` 经合法设备及 Witness 已确认但尚未锚定。服务器对新设备提供 `e0`。可信 Witness 查询可返回 `e1`，仅依赖最新已最终化链状态的恢复方最多得知 `e0`。**解释**：链最终性不等于更新及时性；正确行为取决于业务定义哪类确认是 RecoveryStable。

### T-L2：Witness 完全串谋但独立共识仍诚实

见证者可能同签冲突分支；一条分支的根已独立上链最终化。拥有可信链状态及包含证明的客户端可拒绝与该已锚定根不匹配的恢复状态。**解释**：这是“不同信任域下的条件安全收益”，证明时需明确区块链的独立诚实多数假设，不能与只给 B2 恶意见证者且不允许其外部观察的基线做错误对照。

### T-L3：身份控制权轮换与旧会话

RP 在链状态 `h0` 验证 1271 并签发 session；在新最终化状态 `h1` 撤销旧 signer；恶意 RPC 回复 `h0`。对比：A=只在登录时验证；B=登录验证+短 TTL；C=B+可靠 Back-Channel Logout；D=C+可信 finalized proof+危险操作前再次检查。**解释**：控制链数据被恶意投喂时的额外证据价值必须与“只需更可信 RPC/轻客户端”相区分。

### T-L4：匿名聚合锚定的时间相关攻击

多账户事件属于同一批量检查点，但攻击者可观察提交时间、交易发送地址、发布者网络请求及相关账户公开事件。比较固定间隔批处理、随机延迟、匿名转发与账户专用提交，测量区分优势。**解释**：不要把加密哈希隐藏数据内容和用户行为不可链接混为一谈。

### 统一 Oracle 判定

`Accept(state, op, t)` 由独立程序同时检查：已验证的根/连续历史、设备签名、实际有效权限、凭据元数据与状态纪元、恢复新鲜度下界、RP 特定授权。输出 `ACCEPT / DEGRADE / REJECT / UNDECIDABLE` 并记录证明缺失原因。未取得足够新鲜度证据时，采用 `DEGRADE` 或 `REJECT` 的策略须先定义，避免把拒绝服务与安全失效混算。

## 6. 未决事项与下一阶段单一最高优先问题

1. **最高优先**：在相同信任事实和相同新鲜度下界下，是否存在合法业务场景中的 `AttackSuccess(B2)=1, AttackSuccess(B4)=0`？如果没有，应优先接受“区块链是可选部署/成本分解因素”。
2. 其次：跨链合约签名状态从最终化撤销事件到 RP 终止权限的安全界，可否在可获得标准级 Logout/短会话的系统上提供严格改善。
3. 再次：账户隐私的泄漏函数需要独立定义客户端到见证者网络侧观测、链观察、验证者行为和账户辅助知识。
4. SecureVault、CertLedger、PassChain 的全文与复现代码可能显著改变“组合架构”空白的具体判断；目前只能用可核实的出版商摘要支持已有类似构造。

## 7. Revised Safe Wording（开题可使用的安全表述）

**RP-005：** “在恶意同步服务器及部分独立见证者故障条件下，比较无链见证与链上锚定对已确认账户状态恢复的可检测性保证；在相同业务语义和显式可信条件下，研究跨信任域终局检查点对恢复下界、安全性、隐私和成本的影响。”

**RP-006：** “针对智能合约钱包状态依赖的签名有效性及网站会话的独立生命周期，研究最终化链状态证明、撤销事件传播与 RP 重要操作授权之间的可验证时序约束，量化现有 Web3 登录与 OIDC 失效组合在恶意状态输入下的边界。”

**RP-008：** “在统一账户工作负载和攻击者可观测模型下，评价批量状态承诺发布策略对账户关联风险、恢复新鲜度、确认延迟和链上成本的多目标权衡。”

**RP-007（future）：** “在 RP 主动接入条件下设计 WebAuthn、SIWE 与 OpenID4VP 的模块化身份接入接口，明确账户绑定、会话失效与旧网站兼容条件；暂不作为主要学术创新。”

## 8. 对 Research Points 的影响与 Skill Handoff

| ID | 建议状态 | Gap 状态 | 处理 |
|---|---|---|---|
| RP-2026-005 | `EVIDENCE_SCAN` → `CHALLENGE`（建议） | `POSSIBLE` | 修改原广义主张，下一阶段核心攻击新链必要性 |
| RP-2026-006 | `EVIDENCE_SCAN` → `CHALLENGE`（建议） | `POSSIBLE` | 收缩到链状态证明、撤销时序与 RP 授权一致性 |
| RP-2026-007 | `PARKED` | `UNKNOWN` | 继续标准接入可行性研究，保留后续空间 |
| RP-2026-008 | `EVIDENCE_SCAN` → `CHALLENGE`（建议） | `POSSIBLE`（测量型） | 优先检验简单固定批处理是否足够 |
| RP-2026-001—004 | 原状态不变 | 原记录 | 不修改既有 Research Point revision |

**第四阶段交接 `40_HYPOTHESIS_CRITIQUE_SKILL`：** 明确 H1（链独立收益）、H2（强 Witness-only 足够）、H3（新增查询/发布主体解释全部收益）、H0（无增益）；同时针对 Web3 会话和链隐私设置相应竞争解释。先尝试找出最小反例再继续完整开发。

## 9. 审查限制、声明与更新记录

- 本报告检索以公开一手资料为主，未对所有论文做穷尽式前向引文或代码审计，故创新缺口不写 `CONFIRMED`。
- `VERIFIED` 仅用于实际核查到的技术文本、源论文模型或出版信息；形式化证明的正确性仍依赖原文假设与实际实现。
- 没有执行 T-L1–L4，也没有真实安全率、Gas、延迟、关联成功率或成本结果。
- 没有把 VDNS 原版链上设计重新描述为 V2 独立首次创新。
- 被否定的广义“首创”主张保留在审查记录中，不再作为建议论文创新点。
- `Decision Log r1`：第三阶段核验，保持旧 Research Point 原修订版本不变，对新 RP 仅建议状态演进与重新表述。

## Appendix A：可追溯原始证据与查阅范围

- **[S01] Parakeet (NDSS 2023) full paper**；PRIMARY / peer-reviewed；来源：https://www.ndss-symposium.org/wp-content/uploads/2023-545-paper.pdf；核验范围：§II.A; §II.C; §VII; pp.2–3, 14。
- **[S02] C2SP Transparency Log Witness Protocol v1.0.0**；PRIMARY / protocol；来源：https://c2sp.org/tlog-witness@v1.0.0；核验范围：Introduction; add-checkpoint; TBD Monitor Retrieval Mechanism。
- **[S03] C2SP Transparency Log Trust Policy**；PRIMARY / protocol；来源：https://c2sp.org/tlog-policy；核验范围：Introduction; quorum; witnesses。
- **[S04] Ethereum Consensus Specs — Weak Subjectivity**；PRIMARY / protocol；来源：https://ethereum.github.io/consensus-specs/specs/phase0/weak-subjectivity/；核验范围：Weak Subjectivity Sync Procedure。
- **[S05] ethereum.org Weak Subjectivity**；PRIMARY / official documentation；来源：https://ethereum.org/developers/docs/consensus-mechanisms/pos/weak-subjectivity/；核验范围：Weak subjectivity; trusted checkpoint。
- **[S06] ERC-4361 Sign-In with Ethereum**；PRIMARY / standard；来源：https://eips.ethereum.org/EIPS/eip-4361；核验范围：Session Invalidation; Relying Party Implementer Steps。
- **[S07] ERC-1271 Standard Signature Validation for Contracts**；PRIMARY / standard；来源：https://eips.ethereum.org/EIPS/eip-1271；核验范围：Specification; Rationale。
- **[S08] OpenID Connect Back-Channel Logout 1.0 Final**；PRIMARY / standard；来源：https://openid.net/specs/openid-connect-backchannel-1_0-final.html；核验范围：§2.3–§2.5, Logout Token。
- **[S09] CertLedger (Computers & Security, 2019)**；PRIMARY / peer-reviewed abstract；来源：https://www.sciencedirect.com/science/article/abs/pii/S0167404818313014；核验范围：publisher abstract only; full proof scope not verified。
- **[S10] SecureVault (Procedia Computer Science, 2026)**；PRIMARY / publisher abstract；来源：https://www.sciencedirect.com/science/article/pii/S1877050926016686；核验范围：publisher abstract; full protocol proof and recovery tests not verified。
- **[S11] PassChain (IEEE ICBDS 2024)**；PRIMARY / publisher abstract；来源：https://ieeexplore.ieee.org/document/10837098/；核验范围：IEEE abstract only。
- **[S12] W3C Bitstring Status List v1.0, Recommendation 2025**；PRIMARY / standard；来源：https://www.w3.org/TR/vc-bitstring-status-list/；核验范围：§1.1; §6.1–§6.9, privacy。
- **[S13] W3C WebAuthn Level 3, Recommendation 2026**；PRIMARY / standard；来源：https://www.w3.org/TR/2026/REC-webauthn-3-20260825/；核验范围：normative RP/platform boundary。
- **[S14] OpenID4VP 1.0 Final**；PRIMARY / standard；来源：https://openid.net/specs/openid-4-verifiable-presentations-1_0-final.html；核验范围：presentation request/response; RP collaboration。
- **[S15] W3C DID Core 1.0**；PRIMARY / standard；来源：https://www.w3.org/TR/did-core/；核验范围：definitions; method-specific resolution; privacy。
- **[S16] Zanzibar (USENIX ATC 2019)**；PRIMARY / paper；来源：https://www.usenix.org/conference/atc19/presentation/pang；核验范围：causal consistency of authorization and content。
- **[S17] HotStuff (PODC 2019)**；PRIMARY / paper；来源：https://doi.org/10.1145/3293611.3331591；核验范围：permissioned BFT baseline。
- **[S18] VPass-Continuity / VDNS (user-supplied source)**；SOURCE / project original；来源：密码管理器研究方案_整合版.docx; VDNS_可验证凭据操作审计与最小影响轮换系统白皮书_最终方案稿.docx；核验范围：Chapter 5; on/off-chain role prior design。
