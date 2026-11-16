# 硕士毕业设计立项研究 V2：第一阶段 Research Discovery

**主题**：在现有 VPass-Continuity、PACW、FICAP、RSPK、VDNS 研究基础上，纳入分布式系统/区块链、Web3 身份与授权；单列未来网页登录范式改造的可行性和接入研究。

**日期**：2026-10-15；**修订**：V2-D1-r1；**研究生命周期**：新增研究点 `EXPLORE`（登录扩展可 `PARKED`），不宣布独立创新性成立。

**执行规则**：严格遵循 `00_PROJECT_CHARTER.md` 和 `10_DISCOVERY_SKILL.md`，下一轮经 `20_LITERATURE_SCAN_SKILL.md` 扩展文献扫描，再进入 `30_VERIFICATION`、`40_HYPOTHESIS_CRITIQUE`、`50_EXPERIMENT_DESIGN` 和 `60_RESEARCH_POINT_SCHEMA`。本报告允许引用少量核验过的标准和直接先例作为**问题边界**；其作用是初筛显然重复的创新主张，并不表示第二阶段系统检索已经完成。

## 0. 结论与研究范围决定建议（非已批准决策）

**暂拟主课题**：《面向不可信云环境的多凭据管理与去中心化身份认证协同安全机制研究》。

可解释性较强的具体系统题目备选：《融合分布式可信状态见证与 Web3 身份适配的多凭据密码管理系统设计与安全性研究》。两个题目均为 `[IDEA]`，最终命名由分离性证据、论文周期和导师要求决定。

**课题组织方式**：以恶意云同步中的可验证账户状态为核心；采用链下签名事件日志 + 多见证者 + **可选、批量、低频** 链上状态检查点作为安全控制平面；向上提供跨密码、Passkey、Web3 钱包/DID 的授权一致性接口。将“改变现有网站登录范式”放到后续路线（协议接入验证可以做，完整社会化替代与跨站普及暂不承诺）。

当前最重要的科学未知是：**当云同步服务器可作恶、Witness 可能部分串谋且客户端可能丢失全部本地历史时，引入具有最终性的分布式账本能否在同等隐私与信任条件下获得独立的状态恢复/授权一致性收益，还是透明日志+见证+Gossip 已经足够？**

另一条重要未知是：**对于 Web2/Web3 共享身份的生命周期，如何定义“链上密钥撤销/轮换—离线签名有效性—网站会话有效期”的可验证时序，并与客户端凭据使用门禁保持一致？**

## 1. 输入范围与原项目继承关系

### 1.1 [SOURCE] 原始 Word 与六阶段产物

1. `密码管理器研究方案_整合版.docx` 第 5 章：PACW、FICAP、RSPK；本地核心是最终安全执行边界；VDNS 保留 Witness Registry、透明日志、外部检查点、恢复引导；明确削减逐凭据上链、日常登录查链、高频链上交易。
2. `VDNS_可验证凭据操作审计与最小影响轮换系统白皮书_最终方案稿.docx` 第 1—3 章：已有“完整操作/日志密文链下、状态根/检查点链上”设计，包含可验证主体、权限、状态和日志。**因此‘给密码管理器增加区块链’属于原项目既有构想，并非本次新增的首创性研究主张。**
3. `RSPK_基于根种子的可重建同步_Passkey_协议.docx`：种子派生 Passkey 与 PACW 元数据恢复；设计承认根秘密隔离和已复制私钥不可远程撤销等边界，相关创新在前六阶段被收缩。
4. 前一轮六阶段报告/Research Point Registry：RP-2026-001（跨层状态授权一致性）、002（匿名见证/恢复）、003（动态授权信息流）为 `CANDIDATE`，004（RSPK）为 `PARKED`；此状态属于旧版研究范围下的研究准备度，不代表已有安全差分证据；E0—E4 尚未执行。

### 1.2 与新增想法的关系

- 原 RP-001 是整个新系统安全语义的父级约束，增加链上共识/钱包验证后应**另建 revision**，避免默默改写旧候选卡。
- RP-002 的 Witness/VCC 与新研究“分布式账本最终性、恢复新鲜度”直接 `OVERLAP`；任何新机制须相对可信 Witness-only 强基线进行差分比较。
- RP-003 的共享功能权限与 Web3 钱包签名/会话授权在安全语义上 `PARENT/CHILD`，尤其涉及权限更新和撤销。
- RP-004 可作为 WebAuthn/Passkey 身份适配演示模块，维持 `PARKED`，防止技术路线在单篇硕士论文中无限扩张。

## 2. Current Observation：实际观察与未知分离

**O1 [SOURCE]** VDNS 早期材料将区块链作为状态锚定/低频公告层，真正加密数据及事件保存在链下。`密码管理器研究方案_整合版.docx` 进一步收缩链上职责。

**O2 [SOURCE]** 项目已有 PACW 恶意同步状态、FICAP 动态功能权限、RSPK 同步 Passkey 三组设计；前五阶段提出了一组具体安全目标与区分性测试，但**实际安全基线实验尚未执行**。

**O3 [PRIMARY]** W3C DID Core v1.0 已规范去中心化标识符及 DID Document；W3C VC Data Model v2.0 已提供发行方—持有方—验证方的数据模型；二者并不将公共区块链规定为所有使用场景的强制底层。来源：https://www.w3.org/TR/did-core/ 、https://www.w3.org/TR/2025/REC-vc-data-model-2.0-20250515/ 。

**O4 [PRIMARY]** ERC-4361 Sign-In with Ethereum 已将钱包签名登录用于链下网站会话；ERC-1271 支持合约账户签名验证，ERC-4337 支持 UserOperation/智能合约账户；WebAuthn Level 3 规定 RP 侧注册和验证流程。来源：https://eips.ethereum.org/EIPS/eip-4361 、https://eips.ethereum.org/EIPS/eip-1271 、https://eips.ethereum.org/EIPS/eip-4337 、https://www.w3.org/TR/2026/REC-webauthn-3-20260825/ 。

**O5 [PRIMARY—摘要级]** 2026 年《SecureVault: A Zero-Knowledge Password Manager with Blockchain-Anchored Integrity》已有客户端加密/云端存储/链上哈希锚定构造，完整实现和实验方法尚未读到。来源 DOI:10.1016/j.procs.2026.06.037；另有 2024 IEEE ICBDS《PassChain: A Blockchain-Based Decentralized Password Manager》 DOI:10.1109/ICBDS61829.2024.10837098。**由此排除“首次区块链密码管理器/首次哈希锚定”的宽泛创新主张。**

**未知 [UNKNOWN]**：是否有直接研究“隐私法定人数+链上可验证最终性+丢失历史恢复+跨 Web2/Web3 会话撤销”并满足同样威胁模型、功能与成本边界；不同账本/见证选择产生哪些可复现的安全与隐私差异；具体研究资源与截止期限。

**当前只是推测 [INFERENCE]**：区块链提供一个独立于同步服务器和部分见证方的公共排序/可验证终局参考后，可能减少串谋下的私下分叉，但会引入链上可链接的时序元数据、最终性等待和链治理风险。尚无数据支持收益明显大于成熟 Witness+Gossip 方案。

## 3. Current Interpretation：提出者的隐含解释与审查

- I1：“去中心化”意味着更安全。实际需要针对治理主体、法定人数、合谋、数据可用性与成本定义安全属性；私有链中同一管理方控制多数验证者时，去中心化的实际信任收益可能很小。
- I2：“有区块链就不会回滚”。链上能帮助固定已发布且达到最终性条件的检查点；仍需可信账户绑定、可靠证明、发布者不被篡改、链终局、链数据获取，且不能保证服务器立即公布每次更新，也不能强迫云端交付最新密文。
- I3：“DID 等于去中心化登录”。DID 是标识符及控制验证设施；网站登录仍需要 RP 的身份绑定、挑战响应、信任/授权策略以及会话建立。VC 的真实性还依赖发行方可信性和状态检查。
- I4：“密码管理器能替所有网站更换登录协议”。若网站仅接受口令，客户端无法单边使其验证钱包签名或 VC；需要网站、身份提供方或接受现有协议的集成渠道参与。
- I5：“整合 Web3 会增加论文创新性”。工作量会增加，独立新颖性取决于已发表协议无法覆盖的具体安全性质、必要机制或有价值的系统权衡。

## 4. Competing Explanations：至少两类竞争解释

### H-A：分布式账本提供真正新的独立故障域

在部分 Witness 失效或多视图串谋下，公共最终性锚点可能提供单一可审计恢复下界，从而降低全设备丢失的历史歧义。

**H-B（强竞争）**：Witness-only + Gossip + 认证 Checkpoint + 独立恢复下界已达到相同保证。区块链仅以更高成本替代一组独立见证者；链上可链接性反而恶化隐私。

**H-C（简单解释）**：过去的攻击来自 Witness 协议错误、缺少独立检查点或实现时序不正确，而非缺少账本共识；强化日志/审计器即可修复。

**H-D（隐含前提）**：链条多数节点/排序服务可被攻击者控制或审查；恢复客户端读到的 RPC/轻节点证明同样可被隔离。新增账本可能并不改善攻击者模型中的关键瓶颈。

### H-E：统一身份状态提高 Web2/Web3 授权安全

由独立可验证账户版本绑定 DID/钱包控制权、共享权限、WebAuthn 凭据及网站会话，可以建立可审计撤销语义。

**H-F（强竞争）**：WebAuthn + OIDC + ERC-4361/1271 + 现有授权缓存失效机制已能实现目标；新方案只是一套协议网关。

**H-G（其他解释）**：可能观察到的未授权会话主要源于网站未检查 Session、钱包假签名弹窗、第三方合约校验或跨链重放，与密码库状态协议无关。

## 5. Researchable Questions：重新定义科学问题

**RQ-0 总问题**：在受管理可信客户端、恶意云同步、有限诚实见证者与可选公共区块链最终性条件下，链上/链下不同信任分配策略如何影响多凭据账户的恢复新鲜度、动态授权与认证操作的一致性、隐私泄漏及系统成本？

**RQ-D1（核心）**：对于恶意云同步服务器可长期隔离设备、且 Witness 可能部分串谋的场景，增加经过确定终局判定的链上检查点，是否比最强 Witness-only + Gossip 基线获得严格更强的恢复状态下界/分叉可发现性？若获得收益，其必要的信任、最终性和发布频率条件是什么？

**RQ-D2（核心）**：在稀疏锚定、链重组、交易延迟、审查和多设备并发更新条件下，如何定义与可验证地维护 `OperationalStable` 与 `RecoveryStable` 的顺序关系，而不将链上最终性错误地等同于全局实时最新？

**RQ-D3（隐私）**：匿名/伪名 Witness 投票与链上批量检查点会泄漏多少账户关联、更新时间和凭据使用频率？固定时间批处理、固定大小区块、混合账户根与零知识关系证明之间的成本—隐私权衡是什么？

**RQ-W1（Web3 身份）**：Web2 的 Passkey/密码会话与 ERC-4361 钱包登录、ERC-1271 智能账户以及 DID/VC 身份呈示之间，如何统一描述账户控制权、授权时间点与撤销，使离线签名、链上密钥轮换和服务器会话不出现不一致接受？

**RQ-W2（可扩展性）**：当 Web2 站点、EVM 钱包和 WebAuthn 分别采用不同曲线、控制根、密钥恢复和信任验证方法时，可验证状态句柄能否隔离密钥语义并减少跨协议混淆？哪些简单标准网关已经能够等效解决？

**RQ-F1（未来、暂不纳入核心）**：在 RP 可主动接入的条件下，能否将用户从记忆密码/网站账户数据库迁移为基于 Passkey、钱包签名或可验证凭据的统一认证入口，并以可逆兼容机制对接传统 OIDC 网站？其抗钓鱼、隐私、迁移摩擦与恢复成本如何比较？

## 6. Architecture Options：供后续证据挑战的架构选择

### A. 本地可信执行与凭据分离

本地 Vault Core 维护账户根和域分离密钥：`VaultRoot`（保险库密钥）；`WebAuthn Credential/Authenticator`（RP 作用域签名能力）；`Wallet Controller`（Web3 钱包/合约账户控制）；`DID Controller`（可选身份验证方法）；`Session Tokens`（目标 RP 颁发的会话）。默认使用**独立根秘密**并单独恢复策略；只有安全证明成立时才考虑从统一根派生，尤其避免“丢失一个秘密同时丢失全部 Web2/Web3 账户”的集中灾难。

### B. 链下可信状态平面

账户状态 `S_e=(VaultRootHash, ACLRoot, DeviceRevocationRoot, FeaturePolicyRoot, IdentityBindingsRoot, OptionalPasskeyMetaRoot)`，由经过权限检查的设备事件产生。Witness 对状态前驱/序号/确认语义进行验证，透明日志保留包含与一致性证据。保留旧方案的 PACW/FICAP 安全边界。

### C. 可选分布式账本终局平面

每 `K` 次已稳定更新或每 `Δ` 时间，将**批量聚合**后的账户无关检查点（如 `H(version || epoch || witness_quorum_root || log_roots || registry_root)`）经批处理发布到公共链/L2 或独立 BFT 共识日志。链上只验证必要序号、承诺及发布权限；不放密码、TOTP、Passkey 私钥、用户名、域名、账户映射、DID 文档明文与逐次登录事件。合约拒绝同一发布域的明显无序版本，但其有效性仍依赖链下成员/签名验证和终局规则。

**注意**：跨账户批根减少直接账户标签，无法自动消除时间相关性、同一交易发送者和访问模式泄漏。若采用账户专用合约，将承担更明显的长期关联风险。

### D. Web3 身份适配平面

- DID/VC：为管理设备、组织成员和恢复主体表示可验证声明与验证方法；发行方可信度、吊销状态、Proof of Possession 需单独处理；DID 方案可采用链上或链下方法。
- 钱包/智能账户：针对 SIWE 提供挑战处理、origin/domain/chainId/nonce/expiry 校验；支持 EOA、ERC-1271 合约签名（必须从指定链和已定义区块上下文验证）；ERC-6492 只对未部署合约钱包有兼容价值；ERC-4337 属于执行与授权基础设施，无须每次网页登录产生链上交易。
- 可信 Web 认证：采用 WebAuthn RP 原生流程，保留 RP ID/Origin/Challenge/User Verification 的平台验证边界；避免误将钱包签名解释为 WebAuthn assertion。
- RP 集成网关：具备接入权限的网站可选择原生 WebAuthn、SIWE 会话服务、OIDC Federation/Identity Provider 适配或 OpenID4VP（验证 VC 呈示）。

### E. 数据平面与安全门禁

云端同步仍保留端到端加密对象的存放/传输功能；正常自动填充和 WebAuthn 签名依赖本地可信核心，日常操作不等待链上确认；高风险设备撤销、主密钥恢复、新设备接纳等事件按明确策略要求 `RecoveryStable` 或可信下界。判定接口输出 `ACCEPT/DEGRADED/REJECT` 与具备版本、证明来源、授权能力范围的理由码。链离线时必须按安全降级策略执行，而不是自动接受过期状态。

## 7. 方案横向比较（Discovery 阶段，定性，不作性能声明）

| 方案 | 原理 | 主要优点 | 适用场景 | 实现难度 | 运行成本 | 此阶段选择 |
|---|---|---|---|---|---|---|
| A0 单云同步 + 本地签名 | 密文同步与本地元数据认证 | 简洁、低延迟 | 基础安全对照 | 低 | 低 | 弱基线，不能支持创新主张 |
| A1 Witness + Gossip + 认证恢复下界 | 独立多观察者监督日志一致性 | 低交互成本、传统机制成熟 | 默认强基线 | 中 | 低—中 | **必须完整实现对照** |
| A2 Witness + 公共链/L2 批量锚定 | 离线证据 + 公共终局参考 | 可能增强某些合谋/全设备丢失情形 | 候选核心机制 | 高 | 变化较大 | **待分离性证据决定** |
| A3 许可型 BFT 共识账本 | 多机构共同确认状态检查点 | 明确治理与成员准入，确定性终局实现路径 | 校园/企业共同管理 | 中—高 | 运维较高 | 强竞争方案；信任方独立性关键 |
| A4 全链上密码库/频繁交易 | 密文或元数据上链执行 | 可查询历史证据 | 特定链原生应用 | 很高 | 高且可链接 | 不作主线，作成本/隐私反例 |
| A5 标准 WebAuthn/OIDC/SIWE 网关 | 依赖 RP 主动接入的标准身份认证 | 兼容性较好、无自造认证协议 | 未来身份系统 | 中 | 低—中 | **后续适配验证，不替代现有网站规则** |

方案选择不以“链越多越先进”为依据。统一控制公共链终局、隐私和可用性的变量，在实验中测量其信息增益。

## 8. 登录范式演化的三种实际可行路径

**路径 F0：保留老网站兼容**。如果 RP 只接受口令，浏览器扩展只做真实 RP 交互中的安全自动填充、凭据更新和提示，不宣称已替换其服务端身份认证协议。涉及账户迁移时，需要用户使用目标网站官方提供的 Passkey、SSO 或钱包登录注册选项。

**路径 F1：网站主动接入的无密码化**。RP 可在服务端新增 `WebAuthn credential registration/assertion verification`；本项目本地核心实现 Credential Manager/Authenticator 适配；网站建立正常 cookie/session。此路径已具有成熟标准，需要研究的新问题是本项目额外提供了什么恢复/撤销一致性，而非“重新发明 Passkey”。

**路径 F2：Web3 登录并与现有网站融合**。自主开发演示 RP 增加 SIWE 登录：RP 创建一次性 nonce 和域绑定声明 → 用户选择钱包/智能账户 → 可信钱包 UI 对 origin/chainId/资源与请求签名进行独立验证 → RP 按 EOA/指定链 ERC-1271 验签 → RP 与本地用户 ID 建立可更新绑定 → RP 颁发正常网页会话 → 钱包控制权轮换/撤销触发按明确传播上界失效或短生命周期处理。对只支持 OIDC 的网站，可在**网站允许配置自定义身份提供方**时部署 OIDC Bridge；未经 RP 配置或授权无法强制其接受新的 IdP。

**路径 F3：面向 VC/DID 的可选择性身份陈述**。当 RP 或业务系统需要年龄、成员资格、证书而不是公开钱包地址时，OpenID4VP 或其他合适规范可要求最小化的 VC 呈示。身份真实性/现实身份依赖所信任的发行方，匿名性取决于具体凭据格式与证明机制。适宜研究选择性披露与认证结果绑定，但规模可晚于毕业设计。

**实际网页登录范式改变的必要条件**：RP 的登录接口/认证服务接受新凭据或经其认可的 OIDC/SSO；用户对身份绑定和签名给予真实授权；浏览器/钱包平台支持安全请求来源；退出登录、账户找回、密钥轮换、session invalidation 的责任明确。任何一项未满足时，系统只提供兼容能力，不能单方面修改对方服务器的认证协议。

## 9. 主要科学假设及可以否定它的证据

**H1-Ledger [HYPOTHESIS]**：在预设的部分 Witness 串谋和同步服务器分叉下，稀疏链上终局能够使新设备拒绝至少一类最强 Witness-only 基线可能接纳的历史状态，同时不增加额外的可信身份服务。**证伪**：在完全相同可信输入下，Witness + Gossip 已拒绝所有这些旧状态；或同样隐私成本下链上方案达不到承诺的保证。

**H2-Epoch [HYPOTHESIS]**：链上终局检查点与状态/授权/签名执行版本统一绑定，可缩小跨 Web2/Web3 认证撤销的状态混淆窗口。**证伪**：使用现成 SIWE+短会话、OIDC 会话失效、ERC-1271 当前状态查询已达到相同保证，或新方案只是以增加确认等待为代价减少窗口。

**H3-Privacy [HYPOTHESIS]**：批量承诺+隐私同根证明能够在指定对手观察范围内显著降低链上账户可链接性。**证伪**：交易时序或访问模式仍能高优势关联账户；或者采用普通固定间隔批处理已取得等价收益。

**H0 [HYPOTHESIS]**：增加分布式账本不提供可归因的独立安全优势，甚至在某些配置下恶化可用性和隐私。**能否继续主线**取决于公平基线对照，而非选择符合预期的样本。

## 10. Research Type 与 Value Test

- **主研究类型**：Systems + Security + Distributed Systems + Architecture + Measurement；身份协议适配兼具 Applied Cryptography/Identity。
- **Scientific value**：有条件地回答“链上共识对多凭据状态恢复/授权到底增加何种安全保证”“混合身份认证系统中的撤销语义是什么”。如已有机制可等价解决，应将贡献降级为有用的负结果/测量方法。
- **Technical value**：可形成独立的模拟恶意同步服务器、Witness、共识锚定器、本地凭据安全核心、多协议 RP 演示和可复现实验工具。
- **Generalizability**：目标安全性质适用于端到端加密同步协作、跨设备密钥库及钱包权限管理；需要通过至少两类工作负载验证。
- **Falsifiability**：通过同攻击轨迹、同发布频率、同信任边界、同等隐私和业务能力下的多基线测试来否定。
- **Feasibility**：实验先采用本地可控 BFT/链模拟器 + 独立签名验证器和 Mock RP，随后选择一条真实网络进行锚定/延迟实验；正式资源和时间尚待用户确认。

## 11. 研究点提议及生命周期

**旧研究点（保留旧 revision，不默改）**：RP-2026-001/002/003 = `CANDIDATE`（旧范围准备度）；RP-2026-004 = `PARKED`；所有条目 `FROZEN=false`。

**RP-2026-005 [EXPLORE]** 《链下见证与链上共识锚定在恶意同步恢复中的安全分离性》：Parent/Overlap RP-002、RP-001；主要机制 BFT、最终性、认证 Checkpoint、恢复下界；最大风险是通用 Witness+Gossip 等价。

**RP-2026-006 [EXPLORE]** 《跨 Web2/Web3 凭据状态与动态账户控制权的可验证授权一致性》：Parent/Overlap RP-001、RP-003；核心观察是 ERC-1271 签名有效性可随链状态变动、网站会话有独立有效期；最大风险是标准身份/会话机制已经足够。

**RP-2026-007 [PARKED / future]** 《可渐进部署的多范式网页登录与去中心化身份接入网关》：涉及 WebAuthn、SIWE、OIDC、DID/VC/OpenID4VP；该方向可以进行方案设计和 Mock RP 演示，但用户明确允许暂不执行。其最大反证是已有身份协议已覆盖绝大多数功能、站点接入意愿/可用性构成主要瓶颈。

**RP-2026-008 [EXPLORE]** 《公共链锚定条件下账户隐私与最终性可验证性的成本—泄漏边界》：RP-005 子点，与 RP-002 匿名见证重叠；最大风险是数据上链后的长期可链接性无法达到预期或通用批量技术已经足够。

## 12. 创新性主张的禁止与允许范围

**禁用（已有先例）**：首个区块链密码管理器、首次链上哈希锚定、首次去中心化登录、首次 DID/VC、首次智能合约账户、首次见证日志、首次 Passkey 种子生成、首次将 Web2 与 Web3 放在一个 App。

**候选并待证**：恶意同步下链上/链下组合的精确安全性质；已确认状态在 RPC 隔离/链重组/部分 Witness 串谋下恢复安全的必要边界；隐私见证同根投票与链终局证据的低泄漏组合；跨 Web2/Web3 状态撤销与网站 session 的时间绑定；同等安全保证下减少恢复、证明或隐私成本的新机制。

Gap confidence 暂定：RP-005 `POSSIBLE`、RP-006 `POSSIBLE`、RP-007 `UNKNOWN`、RP-008 `UNKNOWN`。根据 Charter，**这些标签仅表示候选空白而非新颖性已成立**。

## 13. 下一阶段的最有信息增益任务（Literature Scan Handoff）

优先对 **RP-005** 开展 direct + counter scan，特别查：Blockchain-Anchored Password Managers（SecureVault/PassChain）、BFT ledger + audit logs、Certificate Transparency/CertLedger、Accountability/Equivocation、Gossip Witness、Client Recovery Freshness 和隐私透明目录；确认“何种攻击强 Witness-only 拒绝不了，而区块链能拒绝”。这是当前最可能改变主课题价值判断的证据。

随后对 **RP-006** 查：ERC-4361 Session Invalidation、ERC-1271 动态验签、ERC-4337 可编程验证、ERC-6492 未部署钱包、OIDC/OAuth 会话/凭据撤销、WebAuthn 认证器模型、OpenID4VP 等。优先找已研究合约账户密钥轮换与离线网页登录会话冲突的原始论文。

第二阶段须分类 DIRECT / COMPETING / ENABLING / ADJACENT，提取 WHY/HOW/WHAT；第三阶段逐条核验“已有谁解决什么”及否定性创新主张；第四阶段反方挑战；第五阶段 E0-E4；第六阶段更新卡片、新增 revision、按证据决定 `CANDIDATE/FROZEN/PARKED`。

**最小预验证（未来 E0，未执行）**：恶意同步服 + 3/4 Witness + 本地两条分叉历史 + 认证检查点 + 可模拟最终性/重组的链，按同一 T1/T2/T5 派生轨迹比较 Witness-only、BFT-only、Witness+Chain；测量错误接受、可证明恢复下界、账户可链接性、重组后的双重确认、恢复时延和单位状态锚定成本。

## 14. 工程模块划分与预期工作量（建议性）

| 模块 | 最小研究范围 | 后续扩展 |
|---|---|---|
| M1 本地多凭据核心 | 统一版本状态、认证加密、设备签名、独立密钥域、授权门禁 | 生产级浏览器/手机客户端 |
| M2 恶意 Sync 与回放器 | 回滚、删改、分叉、延迟、交叉版本合成、拒绝服务 | 分布式网络仿真 |
| M3 Witness/PACW | 法定人数、签名日志、恢复下界、检查点比对 | 隐私 ZK-QC |
| M4 可插拔共识锚定 | Witness-only、公链/L2、许可型 BFT 三后端的检查点证据验证 | 公开部署与链治理分析 |
| M5 功能影响权限 | 共享对象、动态 ACL、功能效应门禁、撤销 | 信息流攻击和非干扰证明 |
| M6 Web3 身份适配 | SIWE 验证/合约钱包密钥状态、最小 Mock RP | DID/VC/OpenID4VP/OIDC Bridge |
| M7 实验与 Oracle | 统一状态机、攻击轨迹、差分判定器、统计框架 | 开源复现套件/用户实验 |

核心论文优先完成 M1—M5、M7；M6 先做只读接口契约与一个不触及真实资金的钱包登录演示。对钱包权限和签名演示使用测试网络与测试密钥，业务身份和资产保持隔离。

## 15. 失败条件、伦理风险和边界

- 如果强 Witness-only 基线在同等恶意服务器/恢复假设下实现全部保证，则不以“上链”作为独立创新，而转向性能、治理或负面安全结果。
- 公链 Checkpoint 存在公共观察者、跨时间关联、区块重组、交易审查、费用波动、RPC 欺骗/隔离风险；许可链依赖治理成员真正独立。
- 区块链上的最终确认不证明业务密文一定存在，更不证明当前账户全球实时最新；加密不阻止账户频次/访问模式泄漏。
- 对现有 RP 登录方式的更改需要其主动接入；任何代理式自动化不得绕过 RP 访问控制或用户授权。
- DID/VC/钱包地址不能直接证明用户现实身份、资格或资产所有权之外的任意结论；需发行方信任和正确上下文验证。
- Web3 钱包被攻破可能造成不可逆经济损失，本项目原型只用隔离测试账户与模拟资产。
- 研究不承诺让已复制的 WebAuthn 私钥在 RP 不改变时自动失效；不承诺撤回第三方已接受的历史会话或交易。

## 16. 关键原始来源和访问等级（2026-10-15）

- [PRIMARY] W3C, Decentralized Identifiers (DIDs) v1.0, 2022. https://www.w3.org/TR/did-core/
- [PRIMARY] W3C, Verifiable Credentials Data Model v2.0, Recommendation 2025-05-15. https://www.w3.org/TR/2025/REC-vc-data-model-2.0-20250515/
- [PRIMARY] W3C, WebAuthn Level 3, Recommendation 2026-08-25. https://www.w3.org/TR/2026/REC-webauthn-3-20260825/
- [PRIMARY] OpenID, OpenID Connect Core 1.0 (errata2), 2023. https://openid.net/specs/openid-connect-core-1_0.html
- [PRIMARY] OpenID, OpenID4VP 1.0 (Final), 2025. https://openid.net/specs/openid-4-verifiable-presentations-1_0.html
- [PRIMARY] OpenID, OpenID4VCI 1.0 (Final), 2025. https://openid.net/specs/openid-4-verifiable-credential-issuance-1_0-final.html
- [PRIMARY] ERC-4361, Sign-In with Ethereum. https://eips.ethereum.org/EIPS/eip-4361
- [PRIMARY] ERC-1271, Standard Signature Validation Method for Contracts. https://eips.ethereum.org/EIPS/eip-1271
- [PRIMARY] ERC-4337, Account Abstraction Using Alt Mempool. https://eips.ethereum.org/EIPS/eip-4337
- [PRIMARY] ERC-6492, Signature Validation for Predeploy Contracts. https://eips.ethereum.org/EIPS/eip-6492
- [PRIMARY] EIP-6963, Multi Injected Provider Discovery. https://eips.ethereum.org/EIPS/eip-6963
- [PRIMARY] RFC 9162, Certificate Transparency Version 2.0. https://www.rfc-editor.org/rfc/rfc9162.html
- [PRIMARY—Abstract reviewed, full methods unverified] SecureVault: A Zero-Knowledge Password Manager with Blockchain-Anchored Integrity, Procedia Computer Science 282 (2026). DOI:10.1016/j.procs.2026.06.037 https://www.sciencedirect.com/science/article/pii/S1877050926016686
- [PRIMARY—Abstract reviewed, full methods unverified] PassChain: A Blockchain-Based Decentralized Password Manager, IEEE ICBDS 2024. DOI:10.1109/ICBDS61829.2024.10837098 https://ieeexplore.ieee.org/document/10837098/
- [PRIMARY—Abstract reviewed, full methods unverified] CertLedger: A new PKI model with Certificate Transparency based on blockchain, Computers & Security 85 (2019). DOI:10.1016/j.cose.2019.05.013
- [PRIMARY] Fábrega et al., Mitigating Injection Attacks against E2EE Applications via View-Based Partitioning, USENIX Security 2025. https://www.usenix.org/conference/usenixsecurity25/presentation/fabrega-partitioning
- [PRIMARY] Pang et al., Zanzibar: Google's Consistent, Global Authorization System, USENIX ATC 2019. https://www.usenix.org/conference/atc19/presentation/pang
- [CODE] transparency-dev Witness. https://github.com/transparency-dev/witness
- [PRIMARY] C2SP Transparency Log Trust Policy. https://c2sp.org/tlog-policy

## 17. 本阶段严格结论

- **Current Status**：新增研究 RP-005、006、008 为 `EXPLORE`，RP-007 为 `PARKED`（未来可恢复）；旧 RP 维持旧 revision 的既定状态，不自动冻结或撤销。
- **已完成**：Observation/Interpretation 分离、竞争解释、研究问题、研究类型、价值测试、架构候选、跨 Web2/Web3 接入条件和 Literature Scan handoff。
- **未完成**：本轮重启的第二至第六阶段；任何新增机制创新的原始安全证明、区分性实验和工程结果。
- **下一最佳行动**：启动 `20_LITERATURE_SCAN_SKILL`，优先搜齐 RP-005 最强直接竞争工作，并建立“Witness-only 与区块链锚定提供差异保证”文献矩阵。
