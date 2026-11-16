# 硕士毕业设计扩展研究 V2：第二阶段 Literature Scan

**课题背景**：VPass-Continuity / PACW / FICAP / RSPK / VDNS；引入分布式系统、区块链、Web3，另保留网页登录范式演化长期方向。

**日期**：2026-10-15　**版本**：V2-LS-r1　**状态**：`EVIDENCE_SCAN`　**依据**：`20_LITERATURE_SCAN_SKILL.md`　**研究数据与实验**：尚未执行任何真实实验。

**证据规范**：`[SOURCE]` 为项目自有 Word / V2 第一阶段陈述；`[PRIMARY]` 为原始论文、官方标准/源码；`[PREPRINT]` 为预印本；`[INFERENCE]` 为本研究推论；`[HYPOTHESIS]` 为可证伪新设想；`[UNKNOWN]` 为当前证据不足的命题。资料限于可核验页面可得内容；摘要级论文避免自行补全实验细节。本文是快速文献侦察（Literature Reconnaissance），**不是系统性文献综述（Systematic Literature Review）**。

## 0. Executive Decision：研究主线如何改变

**阶段结论**：多凭据密码管理器 + 区块链状态锚定 + Web3 登录的简单叠加已存在大量先例。项目可以形成较大系统工作量，创新性仍取决于**分布式信任假设下的实质性安全性质、可证明的安全—隐私—可用性边界或可归因的性能/恢复成本改进**。

**最重要的反方证据**：Parakeet（NDSS 2023）已经给出不依赖共识的密钥透明性承诺分发系统 [L04]；CoSi（IEEE S&P 2016）和 C2SP Witness [L01,L05,L06] 已支持联合见证与检查点一致性；CertLedger（2019）已将区块链用于对抗透明性分叉视图 [L07]。以太坊自身的新设备引导要求弱主观性检查点 [L11]。因此，尚无证据足以宣称“加一条链就解决旧设备全丢失的可信恢复”。

**另一条硬约束**：ERC-4361（钱包登录）、ERC-1271（合约签名状态验证）、ERC-4337（账户抽象）、OIDC Back-Channel Logout（会话失效）、WebAuthn Level 3、OpenID4VP、W3C DID/VC 等已经定义关键身份认证基础结构 [L12-L23]。研究“首次跨 Web2/Web3 统一登录”易与这些先例重复。

**本阶段建议**：主研究问题改为“**在恶意同步与部分见证故障条件下，链下见证、共识终局与异构认证/撤销之间的可验证安全边界及代价是什么？**”；以 RP-005 作为证据核验第一优先级，RP-006 作为可形成独立论文子问题的第二优先级，RP-008 作为必要的隐私/测量贡献，RP-007 仍为后续方向。

## 1. Inputs and Search Scope

### 1.1 继承材料与生命周期

- `[SOURCE]` 原《密码管理器研究方案_整合版.docx》第 5 章定义 PACW 状态连续性、FICAP 动态功能影响授权、RSPK 可重建 Passkey，本地安全核心负责最终裁决。
- `[SOURCE]` 《VDNS_可验证凭据操作审计与最小影响轮换系统白皮书_最终方案稿.docx》已经提出“密文/日志链下、紧凑根与检查点链上”的总体思路；VPass 整合版进一步删除每条凭据/每次登录上链的路线。
- `[SOURCE]` V1 第六阶段 RP-001~003 为 `CANDIDATE`，RP-004 为 `PARKED`，全体无真实分离性实验、无 `FROZEN`。新一轮不得改变旧卡 revision。
- `[SOURCE]` V2 第一阶段提出 RP-005（链/见证安全分离）、RP-006（Web2/Web3 控制与会话）、RP-007（未来网站协议演化）及 RP-008（链上隐私/成本）；前一阶段分别 `EXPLORE/EXPLORE/PARKED/EXPLORE`。

### 1.2 检索窗口与可追溯性

检索时间：2026-10-15；检索范围：计算机系统安全、分布式可信状态、透明日志、密码管理器、区块链及身份协议。优先 IEEE S&P、USENIX Security、NDSS、ACM CCS、ACM PODC、USENIX ATC、W3C、OpenID Foundation、Ethereum ERC 官方页面、官方源码。附录 A 记录 **29 个可核验锚点**，其中并非 29 篇同行评审论文，明确区分规范、实现、工程案例和预印本。

Vocabulary Expansion：
- **State**：fork consistency / equivocation / split-view / rollback / freshness / verifiable key directory / auditable map / recovery bootstrap / weak subjectivity / light client / finality。
- **Ledger**：anchored transparency log / witness cosigning / quorum / BFT ordering / censorship / data availability / commitment distribution / gossip / accountable log。
- **Identity**：SIWE / Sign-in with X / contract signature validation / account abstraction / wallet control rotation / WebAuthn / OIDC / session revocation / back-channel logout / DID resolution / credential status / OpenID4VP。
- **Privacy**：linkability / correlation / membership inference / timing side channel / issuer tracking / status-list privacy / batching / anonymity set / metadata minimization。

按 `20_LITERATURE_SCAN_SKILL` 的 A-D 四步开展词汇扩张、锚点工作发现、基于源文献的关系扩展及反方检索。引文扩展基于已公开的关联论文、标准依赖与项目维护说明；**尚未对所有论文完成逐一的前向引用图穷尽检查**，这一点留给第三阶段高风险 claim 的核验。

## 2. Literature Matrix：跨方向核心比较

| ID / 来源 | 研究问题 | 方法 HOW | 实际研究对象/工作负载 | 主要 WHAT | 适用性与限制 | Relation |
|---|---|---|---|---|---|---|
| L01 CoSi (2016) | 权威提交/证书声明被恶意篡改 | 多 Witness 联合签名、广泛见证 | 证书、时间与日志服务；作者原型 | 公开见证让隐蔽操纵更难 | 对所签名声明的业务语义并非自动保证 | COMPETING |
| L02 CONIKS (2015) | 密钥目录对不同用户展示不同视图 | 认证目录、可审计一致性 | E2EE 身份—公钥映射 | 已建立隐私保护目录的先例 | 非密码保险库全生命周期 | COMPETING |
| L03 SEEMless (2019) | 更快更新隐私密钥目录 | 隐私保护可验证目录 | E2EE 公钥更新 | 作者报告更快更新生效 | 主要是密钥目录场景 | COMPETING |
| L04 Parakeet (2023) | 大规模隐私密钥透明性 | 内存优化可验证目录、共识无关的小承诺分发 | 真实部署导向的消息密钥目录 | 公开对照中**无共识**仍可持续分发一致承诺 | 需要核验其恶意参与者与断连恢复假设 | COMPETING |
| L05-L06 C2SP Witness & Policy | 如何自动校验日志检查点、法定人数 | 附加一致性证明、Witness cosign、quorum | 透明日志 | 已有可执行标准模型 | 不自动保证无历史设备取得“最新”状态 | ENABLING |
| L07 CertLedger (2019) | CT 分叉视图风险 | 区块链 PKI/吊销状态 | TLS 证书透明性 | 链上透明性曾被完整研究 | 与个人保险库的隐私/恢复场景不同 | DIRECT |
| L08 PassChain (2024) | 区块链密码管理器 | 去中心化存储/架构 | 密码管理器 | 产品类别已经存在 | 当前仅核实 IEEE 摘要；具体证明/性能待查 | DIRECT |
| L09 SecureVault (2026) | 云服务器腐败的完整性问题 | 客户端加密 + 合约哈希锚定 | 浏览器密码库 | 已出现链上哈希锚定密码管理器 | 已核实期刊摘要；独立恢复保证及全部实验待查 | DIRECT |
| L10 HotStuff (2019) | 许可型恶意节点一致性 | 部分同步条件下的 BFT 状态机复制 | 分布式副本 | 可作为许可链强对照 | 需要独立运营与明确故障阈值 | ENABLING |
| L11 Ethereum Weak Subjectivity | PoS 长期离线节点如何安全初始化 | 近期可信检查点引导 | PoS 轻/新节点 | 链共识同样存在引导信任假设 | 不保证数据交付与零延迟终局 | COMPETING |
| L12 ERC-4361 (SIWE) | 钱包如何向链下 Web 服务登录 | 域/URI/chainId/nonce/签名、会话绑定 | Web3-Web2 登录 | 标准化钱包登录流程 | RP 会话仍由网站维护 | DIRECT |
| L13 ERC-1271 | 合约钱包如何证明签名 | 读取合约状态 `isValidSignature` | 状态依赖钱包 | 签名有效可随时间/授权变化 | 历史区块、链重组、RPC 可信度需应用定义 | DIRECT |
| L14-L15 ERC-4337/6492 | 智能账户与未部署钱包签名 | UserOperation / 反事实部署验签 | EVM 智能账户 | 强兼容基础 | 不自动撤销 RP Cookie | ENABLING |
| L16 Zanzibar (2019) | 授权与内容的因果一致性 | 外部一致性/授权状态检查 | 大规模在线服务 | 动态授权一致性已成熟 | 假设可信授权基础设施 | COMPETING |
| L17 OIDC Back-Channel Logout | RP 已建立的登录会话如何失效 | Logout Token 与 RP 自身会话终止 | Web2 RP / IdP | 已有远端会话撤销流程 | 依赖 RP 配合；通信延迟仍存在 | COMPETING |
| L18 zkLogin (2024) | Web2 凭据能否控制 Web3 账户 | OIDC Token + ZK 证明 + 临时密钥 | Sui 账户 | Web2→Web3 已有预印本与部署 | 更窄的风险与恢复需要独立检查 | DIRECT |
| L19 WebAuthn Level 3 | RP 域绑定无密码身份认证 | 浏览器—认证器—RP 公钥协议 | 网站 | 标准化无密码认证 | 不接受修改的 RP 需主动支持 | ENABLING |
| L20 OpenID4VP | 网站/验证者获取 VC 呈示 | OAuth 基底上的 VC Presentations | 证书/资格证明 | 可做有权限的 RP 接入 | 凭据真实性取决于发行者与验证政策 | ENABLING |
| L21-L22 DID/VC | 去中心化标识与可验证声明 | DID Document、issuer-holder-verifier | 跨机构身份 | Web3 身份的术语和验证基础 | DID 不要求公共区块链；不等于网页登录协议 | ENABLING |
| L23 VC Bitstring Status | 状态撤销的扩展与隐私 | 大批量可压缩状态位图 | VC 大规模状态 | 已有链下批量撤销隐私机制 | 发行方/验证方时效与策略仍需确定 | COMPETING |
| L24-L25 Google/WhatsApp KT | E2EE 公钥真实更新 | Gossip、第三方透明审计 | 大规模真实消息服务 | 非区块链信任方案已有真实部署 | 与密码管理器的账户恢复语义不同 | COMPETING |
| L27 CAIP-122 | 链无关统一登录 | SIWx 通用声明 | 多区块链身份 | 跨链登录已有标准提案 | 当前 Review，状态不得误写 Final | COMPETING |
| L28 Bitcoin 去匿名化 | 公开账本地址关联 | 链交易分析 | Bitcoin 交易网络 | 假名可被关联的明确先例 | 与检查点批交易泄漏非同一模型 | EXPLANATORY |

此矩阵将“同样安全目标但不同机制”标为 `COMPETING`，正式安全目标近似的体系标为 `DIRECT`。一般背景文献不能单独用来否定新颖性。

## 3. Anchor Papers：WHY / HOW / WHAT / Limitations

### 3.1 Parakeet — 最强 Witness-only 反方 [L04]

**WHY**：在 E2EE 消息系统中，服务器可能向不同用户分发不同密钥，要求公钥目录既可追责又可规模化。**HOW**：隐私目录、分布式持久存储，以及无需共识的简短一致性承诺分发机制。**WHAT**：NDSS 2023 论文公开系统架构、实现及 benchmark，可作为“必须区块链”的强反证。**Limitations**：该论文主要证明其目标密钥目录模型中的一致承诺分发；是否覆盖密钥保险库中“全设备无历史恢复+细粒度授权+外部数据缺失”的完整目标需要第三阶段逐节精读。原文：https://www.ndss-symposium.org/ndss-paper/parakeet-practical-key-transparency-for-end-to-end-encrypted-messaging/ 。

### 3.2 CoSi / C2SP Witness — 法定人数不是创新本身 [L01,L05,L06]

**WHY**：避免单独权威对不同对象发出隐藏的矛盾声明。**HOW**：多见证者对权威检查点联合签名，审核日志历史一致性；C2SP 提供操作规约及多见证者接受政策。**WHAT**：法定人数检查点、离线可验证的签名已经具有研究论文与实现。**Limitations**：Cosigning 只证明若干节点看过某些哈希或历史，不证明签名的业务数据满足用户授权，也无法让完全断网新设备得知“刚刚确认的最新状态”。原文：https://dedis.cs.yale.edu/dissent/papers/witness-abs/ 、https://c2sp.org/tlog-witness 、https://c2sp.org/tlog-policy 。

### 3.3 CertLedger — 链上透明性最接近先行方向 [L07]

**WHY**：既有证书透明性日志可对受害者与审计方展示不同视图。**HOW**：将 PKI/证书状态及撤销管理放入区块链透明框架。**WHAT**：2019 年同行评审论文主张对抗 split-world。**Limitations**：结论依赖链共识安全、链视图和部署边界；证书状态与私人多凭据状态的泄漏和恢复要求不同。对本项目的含义是“用链避免分叉”已形成直接先例。原文：https://doi.org/10.1016/j.cose.2019.05.013 。

### 3.4 SecureVault / PassChain — 直接阻止宽泛首创宣称 [L08,L09]

**WHY**：密码保存在中心云造成单点风险和历史完整性问题。**HOW**：SecureVault 摘要描述客户端 AES-256-GCM 密文、云存储和合约哈希/时间戳锚定；PassChain 使用区块链式密码管理架构。**WHAT**：两项不同的公开密码管理器方案已经存在。**Limitations**：本次可见证据为论文摘要，尚未核验它们是否给出了全设备丢失恢复的新鲜度定义、隐私聚合批处理或经过公平强基线比较的性能数据。因此只能得出“宽泛方案已有先例”，不得推断其覆盖或未覆盖所有 PACW 目标。原文：https://doi.org/10.1016/j.procs.2026.06.037 、https://doi.org/10.1109/ICBDS61829.2024.10837098 。

### 3.5 Ethereum Weak Subjectivity — 最重要的边界约束 [L11]

**WHY**：PoS 中久未在线的新节点可能遇到长程替代历史。**HOW**：共识规格要求从近期可信检查点开始验证链状态；区分终局检查点与弱主观性检查点。**WHAT**：区块链验证器本身也存在历史可信引导条件。**Limitations**：不同的 BFT 许可网络与公共 PoS/PoW 假设不同；不能把 Ethereum 的要求直接推广到任意共识实现。**关键影响**：若研究要解决 VPass 全设备丢失，则必须写清“恢复客户端如何得到可信链检查点”，不能把 RPC 返回的最新区块高度视为密码学证明。原文：https://ethereum.github.io/consensus-specs/specs/phase0/weak-subjectivity/ 。

### 3.6 ERC-4361、ERC-1271 与 OIDC 会话 [L12,L13,L17]

**WHY**：钱包使用者希望向链下服务认证，同时智能账户控制者可以变化。**HOW**：SIWE 定义域、chainId、nonce 和结构化登录声明；ERC-1271 对合约执行 `isValidSignature`，可依赖当前状态；OIDC Back-Channel Logout 定义将登出事件传达到 RP。**WHAT**：签名登录、动态合约验签与 Web2 会话撤销分别拥有成熟规范。**Limitations**：三个协议涉及的授权时点不同；合约所有权变化不会自动通知所有使用该身份建立会话的网站，RP 是否及时失效须通过集成方案和策略定义。**候选 gap** 限定在“同一资源会话接受决策怎样与可信链状态、新鲜度边界及凭据授权状态保持可验证时序关系”，且必须先排除标准 Logout + 缩短 TTL 已等价满足目标。原文：https://eips.ethereum.org/EIPS/eip-4361 、https://eips.ethereum.org/EIPS/eip-1271 、https://openid.net/specs/openid-connect-backchannel-1_0-final.html 。

### 3.7 zkLogin 与 OpenID4VP — 登录范式已有双向路线 [L18,L20]

**WHY**：钱包管理存在复杂密钥门槛，网站也希望接收数字身份凭据。**HOW**：zkLogin 将现有 OIDC 身份、短时签名材料和零知识证明组合；OpenID4VP 标准化验证者请求与凭据呈示。**WHAT**：已有 Web2 控制链账户和网站消费 VC 的具体协议。**Limitations**：zkLogin 为预印本加真实实现，不能据其证明消除了所有信任边界；OpenID4VP 不决定发行机构可信度，RP 仍需验证策略。对未来网页登录改造，重点是 RP 可主动接入时的迁移和撤销语义，而非“首次使用钱包登录”。原文：https://arxiv.org/abs/2401.11735 、https://openid.net/specs/openid-4-verifiable-presentations-1_0-final.html 。

### 3.8 W3C Status List 与链上隐私 [L21,L23,L28]

**WHY**：逐凭据检查撤销状态可能使发行方观察每次验证者访问。**HOW**：把大量凭据状态汇成可压缩的位图；DID Core 提醒全球可观察标识符/端点带来可关联风险。**WHAT**：链下批量、群体隐私和公开标识符关联风险已有标准层处理。**Limitations**：区块链提交的聚合哈希具体是否泄漏账户，由提交频率、交易发送者、账户伪名复用以及 adversarial side-information 决定；与 Bitcoin 交易聚类不能直接等价。原文：https://www.w3.org/TR/vc-bitstring-status-list/ 、https://www.w3.org/TR/did-core/ 。

## 4. Established Knowledge：已有结论与不可扩大解释

1. `[PRIMARY]` 见证者可以通过检查点一致性证明及联合签名限制日志分叉；法定人数策略已被规范化 [L01,L05,L06]。
2. `[PRIMARY]` 密钥透明目录可以在不使用公共区块链的条件下实现可审计一致性；Parakeet 提供独立先例 [L02-L04,L24-L25]。
3. `[PRIMARY]` 区块链 PKI/透明性与区块链密码管理器已有公开研究 [L07-L09]。
4. `[PRIMARY]` 公共 PoS 区块链的绝对最新状态、新节点同步与数据可用性是不同命题，正确的恢复客户端也需可信引导 [L11,L29]。
5. `[PRIMARY]` WebAuthn 与 SIWE 是不同的认证协议，ERC-1271 验签可与状态/时间相关；DID 标识和 VC 凭据呈示也有独立数据模型 [L12-L22]。
6. `[PRIMARY]` OIDC 的远程登出和 VC Bitstring 状态已经提出状态变化传播与撤销检查机制 [L17,L23]。
7. `[INFERENCE]` 将多种成熟机制组合仍可能存在跨模块缺口，但目前没有证据足以证明该缺口必然存在，更不能把复杂工程集成自动认定为创新。

## 5. Competing Approaches：必须对比的系统方案

| 方案 | 安全依托 | 预计优势（待实测） | 主要攻击/限制 | 研究价值 | 原型复杂度 |
|---|---|---|---|---|---|
| B0 单云+本地签名 | 用户密钥；云提供旧状态 | 简单低成本 | 服务器回滚、全丢失恢复 | 弱基线，仅 sanity | 低 |
| **B1 Witness+Gossip** | 独立见证、可信审计源、已获检查点 | 无链交易成本、成熟机制 | 见证串谋、查验隔离、引导下界 | **必选强基线** | 中 |
| **B2 B1+独立恢复下界** | B1+独立发布/监视者 | 能单独恢复较强下界 | 同样需要可信发布与发现 | **关键竞争** | 中高 |
| B3 公共链单独锚定 | 共识终局 + 恢复轻客户端 | 共用公共历史 | 弱主观性、审查/延迟、关联 | 必选比较 | 中高 |
| **B4 Witness+批量链锚定** | B1 与链验证的两个信任域 | 可能增强部分失效边界 | 发布延迟/隐私成本 | **候选方案 P** | 高 |
| B5 许可型 BFT 共识 | 独立管理的 3f+1 类副本 | 可控确认与成员治理 | 同一管理方串谋、运维成本 | 强竞争 | 中高 |
| B6 成熟 Web2/Web3 网关 | WebAuthn+SIWE+1271+OIDC Logout | 易适配网站 | RP 不协作、会话超期 | RP-006 最强基线 | 中 |

比较中的“强”仅在明确网络、同步/最终性与可信方数目之后才有意义。链上锚定只能给出已经提交并满足其最终性规则的下界，不能对尚未提交的更新自动保证最新，也不能使被删除的保险库密文重新出现。

## 6. Contradictions & Counter Search：反方检索

| 待审主张 | 最强反证来源 | 当前判定 | 需要采取的动作 |
|---|---|---|---|
| “有区块链才可解决分叉” | Parakeet、CoSi、C2SP [L01,L04-L06] | 广义表述已削弱 | 改成特定故障模型与恢复条件 |
| “链上锚定是新方法” | CertLedger、SecureVault [L07,L09] | 宽泛首创主张不成立 | 寻找应用特定安全语义 |
| “公共链能无需信任引导绝对恢复最新状态” | Ethereum Weak Subjectivity [L11] | 广义保证不成立 | 明确可信链输入/同步证明/下界语义 |
| “引入 DID 就解决网页登录” | DID Core/VC、SIWE、WebAuthn [L12,L19-L22] | 概念混淆 | 拆成身份标识、凭据验证、会话授权 |
| “钱包密钥撤销自动导致网站退出” | OIDC Logout/网站 Session [L17] | 缺少传播机制 | 定义 RP 接入与撤销时效上界 |
| “跨 Web2/Web3 统一登录第一次实现” | SIWE、zkLogin、CAIP-122 [L12,L18,L27] | 广义表述已有先例 | 研究时序/隐私/恢复差异 |
| “链上批量状态是新的隐私机制” | Bitstring Status List、CONIKS [L02,L23] | 广义创新已削弱 | 测量批次数/账户相关性/可信提交者 |
| “使用智能账户即构成新授权协议” | ERC-1271/4337/6492 [L13-L15] | 现有规范覆盖基础能力 | 比较攻击模型及状态恢复一致性 |

反向检索的核心结论是**课题依然具有交叉领域应用价值，而每一个宏观功能点都已有公开先例**。剩余差异必须进入第三阶段更严格的 claim-level 核验。

## 7. Candidate Gaps：按 Research Point 分离

### RP-2026-005：链下见证与链上共识锚定在恶意同步恢复中的安全分离性

- **Candidate Gap Type**：Mechanism / Evidence / Evaluation。
- **Gap Statement `[INFERENCE]`**：当前检索中，CertLedger 重点面向 PKI 透明性、Parakeet 面向 E2EE 密钥目录、Witness 系统面向日志检查点、SecureVault 抽象面向密码库哈希锚定；尚未完成充分检索以判定是否有工作在**同等见证故障预算、独立可信恢复下界、账户隐私、全设备丢失**共同条件下量化 Witness-only 与 Witness+公共链的可区分保证。
- **Confidence**：`POSSIBLE`（存在可比较的具体问题，尚无强证据确认 gap 存在）。
- **Potential Novelty**：精确界定信任失败域和安全性下界；或构造经济成本/隐私代价严格优于基线的机制；**不是“首次区块链锚定”**。
- **Strongest Falsifier**：通过 B1/B2 已有机制，在相同可信方与同步能力下，所有 B4 能拒绝的历史旧状态均被拒绝。另一证伪是链侧依赖同样的外部可信引导，使优势仅来自额外信任输入。
- **Next Search**：Parakeet full proof、C2SP quorum 条件、论文中 Recovery Bootstrap 类威胁、CertLedger 完整证明与实现。

### RP-2026-006：Web2/Web3 身份控制权与网站 Session 的可验证授权一致性

- **Candidate Gap Type**：Mechanism / Domain / Evaluation。
- **Gap Statement `[INFERENCE]`**：ERC-1271 给出状态依赖签名校验，SIWE 定义登录声明，OIDC Back-Channel Logout 定义 RP 会话失效，Zanzibar 定义一致性授权；仍需确认这些机制在**敌对链 RPC、旧授权状态、断网、链上所有权轮换、网站 Session 不同 TTL**条件下如何形式化统一接受语义，是否已由标准组合完整覆盖。
- **Confidence**：`POSSIBLE`。
- **Potential Novelty**：`AuthStateEpoch` 与链上最终性/网站会话的显式安全约束、不可逆操作的受控延迟、可验证降级策略；需要独立攻击区分证明。
- **Strongest Falsifier**：指定最终化 block 的 ERC-1271 + SIWE + 短 TTL + OIDC Back-Channel Logout + RP 服务端检查，已经达到相同撤销上界、安全性和可用性。
- **Next Search**：SIWE 安全注意、跨链重放、RPC state proof、Session management 对比、zkLogin 安全形式化。

### RP-2026-008：区块链账户隐私与可验证最终性的代价边界

- **Candidate Gap Type**：Measurement / Evaluation / Privacy。
- **Gap Statement `[HYPOTHESIS]`**：匿名账户投票、固定间隔聚合和链上提交可能产生跨账户关联性和时间泄漏，具有专门测量空间。**现有标准已详细处理别名相关与大批量撤销隐私，因此一般性匿名化方法的独立创新风险较高。**
- **Confidence**：`POSSIBLE`（面向该 workload 的测量角度）；算法独立创新 `UNKNOWN`。
- **Strongest Falsifier**：普通批处理+定时提交已达到相同攻击者区分优势，所谓新增 ZK 同根证明只增加资源成本。
- **Next Search**：DID Core Section 10、Bitstring Status List Section 6、区块链日志元数据观察/聚类与差分隐私模型。

### RP-2026-007：未来网页登录范式演化与可接入认证网关

- **Candidate Gap Type**：Domain / Usability / Deployment。
- **Gap Statement `[UNKNOWN]`**：已存在 WebAuthn、SIWE、OIDC、OpenID4VP、CAIP-122、zkLogin 等完整路径；本项目若只添加协议开关与界面，将是有用的系统工程。若要成为科研课题，须找到 RP 授权迁移、跨域恢复或用户实验等明确且未覆盖的问题。
- **Confidence**：`UNKNOWN`；**状态维持 `PARKED`**。
- **Future Feasibility**：只接受传统口令的网站只能走其原有注册/认证流程；需要 RP 支持 WebAuthn、SIWE、OIDC/VC 或可配置身份提供方，才能真正更换其验证路径。
- **Falsifier**：成熟认证网关、浏览器 Credential Manager 和已有联邦身份方案在同约束条件下可达到全部目标。

## 8. 登录范式接入实证边界（研究方案，不是已实施）

| RP 类型 | 现实接入路径 | 网站侧改动 | VPass 侧改动 | 当前建议 |
|---|---|---|---|---|
| 仅支持用户名口令 | 安全自动填充、用户经官方流程加 Passkey | 现有模式无需改；切换需 RP 支持 | Vault/扩展/Origin 安全校验 | 核心保留 |
| 原生支持 WebAuthn | RP 验证 Challenge + Origin + RP ID + Signature | 已支持或增加 WebAuthn 服务端 | 平台 API / Authenticator 适配 | 允许 Mock RP 演示 |
| 接受 EVM 钱包身份 | SIWE nonce → 签名 → EOA/1271 验证 → RP Session | RP 登录端点、合约校验服务、Session 规则 | 钱包密钥隔离、可信签名 UI | 允许 Mock RP 演示 |
| 可配置 OIDC 的 RP | VPass Identity Gateway 作为经 RP 允许的 IdP | RP 联邦信任/配置 | OIDC Provider + back-channel logout | 未来可行性验证 |
| 接收可验证凭据的 RP | OpenID4VP 提交最小声明 | RP 凭据验证策略 | Holder/Wallet + Verifiable Presentation | `PARKED` |

登录改变的关键边界：RP 接受什么认证证明属于 RP 侧政策；链/钱包控制权只是认证材料的一部分。**用户端应用没有权限单方面强制别人的服务端接受新登录格式**。

## 9. Cross-Study Synthesis：真正能够主张的贡献类型

| 贡献类型 | 已有研究覆盖 | 可保留的新研究条件 |
|---|---|---|
| Problem Novelty | 分叉、回滚、身份登录均为已知问题 | 将恢复历史、动态授权、链上终局以新的、必要的联合条件形式化 |
| Mechanism Novelty | Witness、BFT、Merkle、批量哈希和 SIWE 已有 | 找到必须改变的机制，提供与最强组合基线可区分保证 |
| Architecture Novelty | 区块链密码管理器和身份网关已有 | 可验证端到端信任传递及安全退出/恢复边界真正独立 |
| Evaluation Novelty | 多个相关系统各有实验 | 同等信任预算、同等隐私保证的 B1/B2/B3/B4 大规模可复现差分评价 |
| Measurement Novelty | 链隐私、密钥透明目录已有 | 账户恢复/匿名见证的专用时序关联泄漏实测与可归因对比 |
| Combination Novelty | 多系统组合应用普遍存在 | 跨层模型提出新的可证伪性质且已有组合做不到 |

**当前最稳妥的硕士论文定位**：以恶意同步账户恢复为中心提出统一安全语义、构建研究原型和强对照；将区块链作为经过独立验证的可选信任平面；Web3 作为异构认证状态验证场景。该安排满足较大系统工作量，能够通过真实结果决定最后的创新主张。

## 10. Search Stop Rule & What to Verify Next

已找到每条研究线的关键竞争：RP-005 的 Parakeet/CoSi/C2SP/CertLedger；RP-006 的 SIWE/1271/OIDC Logout/Zanzibar/zkLogin；RP-008 的 W3C Bitstring/DID 隐私。当前文献侦察达到初步停止条件：下一步更高价值的是对**有决定性影响的原子 claim**精读核验，而非增加不相关论文数量。

第三阶段 `30_VERIFICATION_SKILL.md` 优先核验：

- **V2-C1 [NOVELTY]**：是否存在完全同等条件下、B2（可信 Witness-only 恢复下界）不能拒绝而 B4（Witness+链）能拒绝的最小轨迹；排除链侧新增信任输入的混杂。
- **V2-C2 [FACT/CAUSAL]**：Parakeet 的“consensusless”实际针对哪些承诺一致性保证，是否覆盖离线新设备和恶意目录的不同攻击类型。
- **V2-C3 [FACT]**：CertLedger、SecureVault、PassChain 已经实现哪些真实功能、证明、性能和恢复目标；全文/代码待取得时标为 `UNVERIFIED`。
- **V2-C4 [FACT]**：公开链最终性、PoS Weak Subjectivity、数据可用性、RPC 隔离的准确威胁边界；不得承诺链上数据等于绝对最新。
- **V2-C5 [NOVELTY]**：SIWE+1271+指定最终化状态+OIDC Logout+短 TTL 能否覆盖提出的跨 Web2/Web3 控制权撤销目标。
- **V2-C6 [FACT]**：OpenID4VP、WebAuthn、DID Core、Bitstring Status List 对 RP、凭据状态和隐私的明确保证与接口权限。
- **V2-C7 [PRIVACY]**：在公开链仅写聚合根时，攻击者能否通过时间、交易发送者、网络访问、公开旧根做跨账户关联。必须定义对应泄漏函数。
- **V2-C8 [EVALUATION]**：B1/B2/B3/B4 信任预算、故障阈值、同步/网络边界和成本是否可公平归一。

**唯一最高优先行动**：逐节阅读 Parakeet 与 C2SP 规格，形成 B2 对 B4 的**最小可区分安全性质及具体攻击轨迹**。如果这个性质无法构造，应把链改为可选测量对照，并将 RP-006/008 的安全性/隐私测量作为下一位候选主线。

## 11. Research Point 状态与交接

| Research Point | 继承状态 | V2 第二阶段建议状态 | Gap 信心 | 与既有 RP 的关系 |
|---|---|---|---|---|
| RP-2026-001/002/003 | CANDIDATE | 旧版不修改 | 旧版记录 | V2 父/重叠 |
| RP-2026-004 | PARKED | 不修改 | UNKNOWN | Passkey 演示储备 |
| **RP-2026-005** | EXPLORE | **EVIDENCE_SCAN** | **POSSIBLE** | RP-002 子研究/重叠 RP-001 |
| **RP-2026-006** | EXPLORE | **EVIDENCE_SCAN** | **POSSIBLE** | RP-001 子研究/重叠 RP-003 |
| **RP-2026-007** | PARKED | **PARKED** | **UNKNOWN** | 未来网页协议迁移 |
| **RP-2026-008** | EXPLORE | **EVIDENCE_SCAN** | **POSSIBLE（仅测量型）** | RP-005 子研究/重叠 RP-002 |

本阶段**没有冻结 Research Point、没有执行实验、没有对新颖性给出 `CONFIRMED`**。状态建议由研究者审批；仅创建 V2 索引修订，避免覆盖 V1 注册表。

## Appendix A. Primary References and Verification Status

以下文献和规范均提供出版机构、官方标准或作者项目可核验网址。正文引用 `[Lxx]` 与此表对应。`publisher abstract`/`preprint abstract` 表示限度：不能借摘要声称全文已证明未直接公开的细节。

- **[L01] CoSi** (2016, IEEE S&P) [PRIMARY; abstract+project page]. https://dedis.cs.yale.edu/dissent/papers/witness-abs/ 。关联：DIRECT；主题：witness cosigning; transparency。
- **[L02] CONIKS** (2015, USENIX Security) [PRIMARY; publisher abstract]. https://collaborate.princeton.edu/en/publications/coniks-bringing-key-transparency-to-end-users/ 。关联：COMPETING；主题：private key directory; anti-equivocation。
- **[L03] SEEMless** (2019, ACM CCS) [PRIMARY; author abstract]. https://www.microsoft.com/en-us/research/publication/seemless-secure-end-to-end-encrypted-messaging-with-less-trust/ 。关联：COMPETING；主题：private verifiable key directory; recovery and rapid updates。
- **[L04] Parakeet** (2023, NDSS) [PRIMARY; conference abstract]. https://www.ndss-symposium.org/ndss-paper/parakeet-practical-key-transparency-for-end-to-end-encrypted-messaging/ 。关联：COMPETING；主题：consensusless commitment distribution; private directory。
- **[L05] C2SP Witness Protocol** (2026, C2SP) [PRIMARY; specification]. https://c2sp.org/tlog-witness 。关联：ENABLING；主题：checkpoint signatures; consistency proofs。
- **[L06] C2SP Transparency Log Policy** (2026, C2SP) [PRIMARY; specification]. https://c2sp.org/tlog-policy 。关联：ENABLING；主题：quorum policy。
- **[L07] CertLedger** (2019, Computers & Security) [PRIMARY; publisher abstract]. https://doi.org/10.1016/j.cose.2019.05.013 。关联：DIRECT；主题：blockchain transparency; split-view。
- **[L08] PassChain** (2024, IEEE ICBDS) [PRIMARY; IEEE abstract only]. https://doi.org/10.1109/ICBDS61829.2024.10837098 。关联：DIRECT；主题：decentralized password management。
- **[L09] SecureVault** (2026, Procedia Computer Science 282) [PRIMARY; publisher abstract only]. https://doi.org/10.1016/j.procs.2026.06.037 。关联：DIRECT；主题：client encryption; hash anchoring。
- **[L10] HotStuff** (2019, ACM PODC) [PRIMARY; conference abstract]. https://doi.org/10.1145/3293611.3331591 。关联：ENABLING；主题：permissioned BFT alternative to public chain。
- **[L11] Ethereum Weak Subjectivity** (2026, Ethereum consensus specification) [PRIMARY; normative specification]. https://ethereum.github.io/consensus-specs/specs/phase0/weak-subjectivity/ 。关联：COMPETING；主题：bootstrap trust under PoS。
- **[L12] ERC-4361 SIWE** (2021, Ethereum ERC) [PRIMARY; normative specification]. https://eips.ethereum.org/EIPS/eip-4361 。关联：DIRECT；主题：wallet sign-in to off-chain websites。
- **[L13] ERC-1271** (2018, Ethereum ERC) [PRIMARY; normative specification]. https://eips.ethereum.org/EIPS/eip-1271 。关联：DIRECT；主题：contract signature state dependent。
- **[L14] ERC-4337** (2023, Ethereum ERC) [PRIMARY; specification]. https://eips.ethereum.org/EIPS/eip-4337 。关联：ENABLING；主题：contract accounts; UserOperation。
- **[L15] ERC-6492** (2023, Ethereum ERC) [PRIMARY; normative specification]. https://eips.ethereum.org/EIPS/eip-6492 。关联：ENABLING；主题：signatures before wallet contract deployment。
- **[L16] Zanzibar** (2019, USENIX ATC) [PRIMARY; conference abstract]. https://www.usenix.org/conference/atc19/presentation/pang 。关联：COMPETING；主题：causal external consistent ACL。
- **[L17] OIDC Back-Channel Logout** (2022, OpenID Foundation) [PRIMARY; final specification]. https://openid.net/specs/openid-connect-backchannel-1_0-final.html 。关联：COMPETING；主题：logout token and RP session termination。
- **[L18] zkLogin** (2024, arXiv preprint / Sui deployment) [PREPRINT; preprint abstract + official design]. https://arxiv.org/abs/2401.11735 。关联：DIRECT；主题：Web2 identity to Web3 wallet。
- **[L19] WebAuthn Level 3** (2026, W3C Recommendation) [PRIMARY; normative recommendation]. https://www.w3.org/TR/2026/REC-webauthn-3-20260825/ 。关联：ENABLING；主题：web relying-party public-key sign-in。
- **[L20] OpenID4VP 1.0** (2025, OpenID Foundation Final) [PRIMARY; final specification]. https://openid.net/specs/openid-4-verifiable-presentations-1_0-final.html 。关联：ENABLING；主题：verifiable credentials to relying parties。
- **[L21] W3C DID Core 1.0** (2022, W3C Recommendation) [PRIMARY; recommendation]. https://www.w3.org/TR/did-core/ 。关联：ENABLING；主题：identity controllers; resolution; privacy。
- **[L22] W3C VC Data Model 2.0** (2025, W3C Recommendation) [PRIMARY; recommendation]. https://www.w3.org/TR/vc-data-model-2.0/ 。关联：ENABLING；主题：issuer holder verifier architecture。
- **[L23] Bitstring Status List 1.0** (2025, W3C Recommendation) [PRIMARY; recommendation]. https://www.w3.org/TR/vc-bitstring-status-list/ 。关联：COMPETING；主题：private, compressed credential revocation。
- **[L24] Google Key Transparency design** (2026, Google open source design) [CODE; official design]. https://github.com/google/keytransparency/blob/master/docs/design.md 。关联：COMPETING；主题：gossip log audit of key directory。
- **[L25] WhatsApp Key Transparency** (2023, Meta Engineering) [PRIMARY; first-party engineering report]. https://engineering.fb.com/2023/04/13/security/whatsapp-key-transparency/ 。关联：ADJACENT；主题：real-world external audit checkpoint。
- **[L26] Certificate Transparency Witness** (2026, transparency-dev official source) [CODE; official code]. https://github.com/transparency-dev/witness 。关联：ENABLING；主题：independent witness PoC。
- **[L27] CAIP-122 Sign-in With X** (2022, ChainAgnostic CAIP) [PRIMARY; review-stage standard draft]. https://github.com/ChainAgnostic/CAIPs/blob/main/CAIPs/caip-122.md 。关联：COMPETING；主题：chain-agnostic sign in message。
- **[L28] Blockchain transaction de-anonymization** (2013, USENIX ;login:) [PRIMARY; original article]. https://www.usenix.org/publications/login/december-2013-volume-38-number-6/fistful-bitcoins-characterizing-payments-among 。关联：EXPLANATORY；主题：public transaction linkage。
- **[L29] Ethereum PoS consensus finality** (2026, Ethereum official documentation) [PRIMARY; official documentation]. https://ethereum.org/developers/docs/consensus-mechanisms/pos/ 。关联：ENABLING；主题：economic finality model。

## Appendix B. Reproducibility and Evidence Trace

- 当前资料覆盖文献/规范数量见 Appendix A，尚未对每项源文献开展系统化正向引文穷尽与完整复现实验。
- 当前无真实共识网络部署、无 RP 演示实验、无链上费用观测、无 T1-T5/新增轨迹执行结果；所有性能与隐私结论仅限已公开原始来源或者有标记的设计假设。
- 建议后续保存 DOI、源文献原 PDF、版本化 commit、标准日期以及原始实验日志；对规范主页版本变动特别记录获取日期。
- 加密签名根、钱包密钥、真实用户密码和真实个人 DID 不用于对抗实验，实验采用专用测试账户与合成工作负载。

**结论**：第二阶段把“再加上区块链和 Web3”转换为一组具体、安全边界明确且能被既有强基线否定的研究问题；尚未证明独立创新性，但已经知道下一阶段最应该精确核验什么。
