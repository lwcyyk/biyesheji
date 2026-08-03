# VPass 研究生毕业设计开发报告

## VPass：可验证密码生命周期管理系统的设计与实现

| 属性 | 内容 |
|---|---|
| 系统名称 | `VPass: Verifiable Password Lifecycle Management System` |
| 文档版本 | `2.1.0` |
| 冻结阶段 | `G6` |
| 当前状态 | 研究原型集成；Stage 2核心协议闭环；G7研究原型冻结未达成 |
| 日期 | 2026-08-03 |
| 当前展示协议 | `VPass/2` |
| legacy wire标识 | `VDNS-PM/2`、`VDNS-PM-CP-2`，仅用于冻结签名/KDF/AAD和旧数据兼容 |
| 规范入口 | `specs/001-vdns-audit-rotation/spec.md` |
| 架构决定 | ADR-001～ADR-019 |

> 本报告同时记录原计划和2026-07-31两个阶段审计后的真实完成度。仓库已经形成可运行的v2研究原型，当前统一为G6。Stage 2完成了单节点研究型最终序、跨设备冲突保留与裁决、E0～E5迁移、CanonicalOrigin统一、完整L1～L5回执校验和localhost HTTP同步试验台。生产多节点共识、真实E4 Connector、平台安全存储、SCOPE-ZK和最终逐样本实验仍未闭合，因此不得宣称G7已经冻结。详细证据见`STAGE2_COMPLETION_REPORT.md`。

## 摘要

VPass 是一个面向多设备和不可信同步存储环境的完整密码管理器研究原型。用户只需记忆一个主密码，系统负责复杂密码生成、字段级加密保存、网站账户识别、可信查询、自动填充、多设备同步、密码更新、网站确认、版本管理、设备加入与撤销、备份恢复和操作历史审计。

系统的研究重点是让设备独立验证密码控制过程。密码内容由本地高熵根、随机字段密钥和 AEAD 保护；可验证状态控制层联合验证设备身份、操作资格、动态撤销、版本因果、透明日志和本地策略。同步存储层只保存对象，无权决定哪个密码版本当前有效。区块链或公告层只周期锚定状态根，不参与普通登录。

隐私审计持续提供重复使用、异常设备、长期未轮换、版本回滚和冲突检测。SCOPE-ZK 只在用户明确发起事故分析时作为可选增强，用于证明影响集合和真实修复状态；它不参与解锁、查询、填充或普通同步。

系统纲领可以概括为：

```text
AEAD保护密码内容，可验证状态控制层保证凭据版本和生命周期状态可信。
```

## 1. 课题定位

### 1.1 研究问题

本课题研究：在多设备和不可信同步存储环境中，如何使用户仅凭一个主密码管理多个网站的复杂凭据，同时让每台设备独立确认当前版本、操作主体、授权状态、撤销状态和历史完整性，并避免向同步存储层、可验证状态节点或链上公告层暴露密码、网站、用户名及真实账户关系。

该问题分为四个子问题：

1. 如何在服务器数据泄露后继续保护密码内容和账户关系；
2. 如何拒绝同步存储层返回的旧版本、错误对象和冲突状态；
3. 如何把创建、使用、更新、确认、同步、撤销和恢复组织为可验证生命周期；
4. 如何在不公开稳定复用标签的前提下完成安全检查和可选事故修复。

前三项构成系统主线，第四项是建立在可信生命周期之上的增强能力。

### 1.2 研究目标

- 实现可日常使用的密码生成、保存、识别、填充、更新和同步闭环；
- 建立名称空间授权的设备操作主体模型；
- 让同步存储层从“状态裁判”降为加密对象保存和分发者；
- 以透明日志和周期检查点发现回滚、分叉与历史篡改；
- 将本地候选密码与目标网站真实确认绑定，避免保存值与网站值失配；
- 对隐私、安全、性能、失败恢复和多设备一致性提供可复现实验证据。

### 1.3 非目标

- 不发明新的 AEAD、签名、KDF、HPKE、VRF 或零知识基础原语；
- 不防御能够读取已解锁进程内存的完全本地控制者；
- 不把 Origin、用户名、密码、TOTP、恢复码或稳定密码关系写入公开层；
- 不要求链、VRF、日志服务或 SCOPE-ZK 在线才能完成已有凭据的日常填充；
- 不把自动填充、表单提交或页面跳转误称为网站登录成功证明；
- 不声称撤销能抹除设备在撤销前已经取得的历史秘密。

## 2. 需求基线

v2.1.0第一阶段冻结43项功能需求：根、解锁与恢复为FR-001～008；日常密码库与自动填充为FR-009～018；生命周期、同步与版本为FR-019～027；可验证状态、透明日志与锚定为FR-028～035；隐私审计与可选响应为FR-036～043。

非功能需求包括 NFR-SEC-001～007、NFR-COR-001～004、NFR-PERF-001～008、NFR-AVL-001～004、NFR-MNT-001～004 和 NFR-API-001～003。系统以 AC-001～021 作为端到端验收边界。所有范围、优先级和 Given–When–Then 细节以规范文件为准。

主要用例为：

| 用例 | 用户结果 | 失败安全要求 |
|---|---|---|
| 初始化和解锁 | 本机输入主密码后打开密码库 | 缺设备秘密或错误密码不能解开根胶囊 |
| 创建凭据 | 生成复杂密码并形成 ACTIVE(v1) | 密文、本地路由或事件任一失败均不宣布完成 |
| 查询和填充 | 当前网站得到经证明的当前密码 | Origin、版本、哈希或证明不符即不填充 |
| 更新密码 | 网站确认后激活 v+1 | 模糊结果进入 UNKNOWN/REVIEW，不猜测 |
| 多设备同步 | 设备 B 接受设备 A 的可信更新 | 云回滚、替换和同版本冲突被拒绝 |
| 加入和撤销设备 | 授权设备共享根包，撤销设备失去新代际 | 只凭主密码和同步存储数据不能恢复 |
| 安全检查 | 查看重复、异常、陈旧和冲突风险 | 公开投影不暴露稳定密码关系 |
| 可选事故响应 | 计算影响范围并执行最小修复 | 仅真实完成项改变有效状态 |

## 3. 威胁模型与信任边界

### 3.1 参与者

- 用户：控制主密码、恢复秘密和确认动作；
- 浏览器扩展：观察当前 Origin 并请求生成、查询、填充和改密辅助；
- 本地安全客户端：唯一长期处理解锁后根秘密和字段明文的组件；
- 合法设备：持有独立签名与 HPKE 密钥，并获得能力凭证；
- 加密同步存储层：保存密文对象，可恶意删除、替换、回滚、重放或制造冲突；
- 状态解析、透明日志和 Monitor：提供状态与证明，任何单个外部响应都不自动可信；
- 周期公告层：只固定少量状态根和序号。

### 3.2 受保护资产

主密码、设备秘密、RecoverySecret、`Rᵤ[g]`、`SKroot`、设备私钥、RouteMap、字段明文、字段 DEK、审计密钥和未公开账户关系均为秘密。CredentialID 虽为随机值，仍按敏感伪名处理，不进入不必要的公开投影。

### 3.3 攻击能力

攻击者可获得同步存储层全部数据、控制网络、返回旧对象、重排同步、伪造未签名状态、重放合法消息、控制已撤销设备、观察公开日志和周期根，并诱导浏览器页面请求错误凭据。攻击者不能同时被假设拥有未泄露的设备秘密、正确主密码、独立根签名私钥和合法日志证明。

### 3.4 核心不变量

```text
AcceptedTransition
  ⇒ IdentityValid
  ∧ AuthorizationValid
  ∧ NotRevoked
  ∧ CausallyFresh
  ∧ LogIncluded
  ∧ PolicyAccepted
```

```text
returnedVersion < TrustedStateVersion ⇒ REJECT
returnedEnvelopeHash ≠ TrustedEnvelopeHash ⇒ REJECT
CurrentOriginBinding ≠ CredentialOriginBinding ⇒ NO_AUTOFILL
```

网站改密还需满足：

```text
E0/E1/E2 ⇒ NOT_ACTIVE
E3 ⇒ L5_CONDITIONAL
E4/E5 ∧ PolicyAccepted ⇒ ACTIVE(v+1)
AMBIGUOUS_RESULT ⇒ REVIEW_REQUIRED
```

## 4. 总体架构

系统采用模块化单体与端口/适配器结构。首版用一个 Go 进程降低分布式事务复杂度，但密码学核心、状态机和验证器不依赖 HTTP、数据库、浏览器或链 SDK。

```text
Browser Extension / Desktop UI / Mobile UI
                    │ local authenticated channel
                    ▼
          Local Secure Client API
       ┌────────────┼────────────┐
       ▼            ▼            ▼
  Vault/Crypto   Lifecycle     RouteMap
       │            │            │
       ├────────────┼────────────┤
       ▼            ▼            ▼
 Object Store   Sync Adapter   State Resolver
       │                         │
       ▼                         ▼
Untrusted Storage        Log / Proof / Checkpoint
                                  │
                                  ▼
                              Monitor
```

六个逻辑平面分别是交互、本地密码学与数据、生命周期与同步、可验证状态控制、加密存储与检查点、隐私审计与响应。前五层承担日常功能，第六层中的重型事故分析按需启动。

## 5. 本地密码学与密码库

### 5.1 独立根与主密码解锁

初始化时由 OS CSPRNG 独立生成 256 位对称名称空间根 `Rᵤ[1]`、Ed25519 根签名密钥 `SKroot`、设备秘密 `Dᵢ` 和 `RecoverySecret`。共同封装不意味着互相派生。

```text
Kpwd = Argon2id(Pm, salt, m, t, p)
Kunlock,i = HKDF(Kpwd || Dᵢ,
                 "VDNS-PM-ROOT-UNLOCK" || DeviceIDᵢ)
RootCapsuleᵢ = AEAD.Enc(Kunlock,i, RootSecretBundle, CapsuleAADᵢ)
```

主密码从不发送到服务器，也不作为服务器身份凭据。设备高熵秘密使“只拿到同步存储胶囊”不足以执行主密码离线验证；若攻击者同时取得本机胶囊和设备秘密，低熵主密码仍存在离线猜测风险，因此 Argon2id 参数、设备安全存储和用户密码质量仍必须保留。

`RootSecretBundle` 至少包含 `Rᵤ[g]`、`SKroot`、本地映射种子、恢复策略版本和代际元数据。锁定时活动派生密钥和明文缓存应尽力清零。

### 5.2 严格密钥域分离

```text
Kwrap     = HKDF(Rᵤ[g], "VDNS-PM/CREDENTIAL-WRAP")
Kname     = HKDF(Rᵤ[g], "VDNS-PM/CREDENTIAL-NAME")
Kaudit    = HKDF(Rᵤ[g], "VDNS-PM/AUDIT")
Krelation = HKDF(Rᵤ[g], "VDNS-PM/RELATION")
Krotation = HKDF(Rᵤ[g], "VDNS-PM/ROTATION")
```

设备认证使用独立 Ed25519 私钥；设备秘密、认证密钥、字段解密密钥、审计密钥和轮换密钥不得混用。

> 上述 `VDNS-PM-*` 字符串是 Spec 2.1.0 冻结的 legacy KDF/AAD 域标识。它们为保持旧密文和测试向量可读而保留，不再作为产品展示名。

### 5.3 私有 RouteMap 与 OriginBinding

每个账户随机生成 32 字节 CredentialID。本地 RouteMap 加密保存 `CanonicalOrigin + AccountID → CredentialID`。为避免“同步存储层看不到 Origin”与“字段 AAD 直接包含 Origin”的矛盾，协议使用：

```text
OriginBinding = HMAC(Kname,
  ExactEncode(CanonicalOrigin, AccountID))
```

字段 AAD 绑定 NamespaceID、CredentialID、credentialVersion、FieldType、CryptoPolicyHash 和 OriginBinding。Origin 自身仍作为加密字段保存。自动填充前，本地安全客户端依据当前浏览器 Origin 和所选账号重新计算绑定值；扩展不能传入任意 CredentialID 绕过路由检查。

### 5.4 字段级信封加密

Origin、用户名、密码、TOTP、恢复码和备注各自使用随机 32 字节 DEK。DEK 经 `Kwrap` 或相应设备接收密钥封装，字段 ciphertext 与 wrapped key 分离。只更新密码时，其他字段的 ciphertext、wrapped key 和 digest 保持逐字节不变，从而支持最小写入和实验验证。

CredentialEnvelope 保存密文字段、版本、descriptor hash、policy hash 和对象引用；CredentialStateDescriptor 只保存当前版本、envelope hash、前序 descriptor、生命周期状态、操作主体、设备集根和检查点。同步存储层可见前者的密文对象，可验证状态控制层只解析后者及 ProofBundle。

### 5.5 密码生成策略

密码生成器使用 OS CSPRNG 或经过明确域分离的高熵 PRF，采用无偏采样满足长度、字符类、禁止字符和站点最大长度策略。策略带版本和哈希，生成结果只通过一次性 secret handle 进入扩展，不写普通日志或 API 响应历史。

## 6. 可验证生命周期协议

### 6.1 设备操作主体

每台设备生成 Ed25519 认证密钥和 X25519/HPKE 接收密钥。根控制者签发 DeviceOperationCredential，绑定设备公钥、允许操作、CredentialScope、有效期、发行计数器、状态引用、秘密代际和根签名。

权限包括 READ、AUTOFILL、PUBLISH_AUDIT、CREATE、UPDATE、ROTATE、MIGRATE、REVOKE、DEVICE_ENROLL、RELATION_PUBLISH 和 AUDIT_ANALYZE。设备签名只证明消息来自私钥持有者；能力凭证进一步证明该设备在最终顺序上的相应时刻有权执行该操作。

### 6.2 状态机

创建流程：

```text
NONEXISTENT → CREATE_PENDING → ACTIVE(v1)
```

日常使用不会改变密码版本，证据必须区分：

```text
E0 AUTOFILL_OBSERVED
E1 SUBMIT_OBSERVED
E2 PAGE_SUCCESS_INDICATED
E3 NEW_PASSWORD_RELOGIN_CONFIRMED
E4 SITE_SIGNED_RECEIPT
E5 USER_SIGNED_CONFIRMATION
```

更新流程：

```text
ACTIVE(v)
  → UPDATE_PENDING(v+1)
  → SITE_CONFIRM_PENDING
  → ACTIVE(v+1)
```

失败返回 ACTIVE(v)；响应丢失进入 UNKNOWN/REVIEW_REQUIRED；网站已经改密但本地尚未完成全局发布时进入 `SITE_CHANGED_LOCAL_COMMIT_PENDING`，新密码必须已经本地耐久，不能回退填充旧密码。

撤销流程：

```text
ACTIVE → SUSPENDED → REVOKED
```

凭据聚合状态与凭据版本状态分开；事件发布状态 `LOCAL_PENDING → OBJECT_STORED → LOG_INCLUDED → CHECKPOINT_ANCHORED` 也独立保存，避免把业务状态和证明可用性混成一个枚举。

### 6.3 CAS、计数器和因果

每次写入携带`expectedVersion`、`previousDescriptorHash`、设备单调counter和前序事件hash。数据库事务同时完成候选状态、内容对象引用和outbox；同一数据库内并发双写最多一个成功。两台设备可分别成功生成`v2-A/v2-B`，发现后必须保留两个分支并进入CONFLICTED。具有冲突裁决能力的主体显式选择，Final Order Authority签发排序回执后才形成可验证终局。

### 6.4 网站确认边界

本地生成候选密码并不等于网站已修改。E0填充、E1提交和E2页面提示均不能激活。E3独立新会话重登录只有在精确Origin、候选版本和新鲜性等严格策略满足时才能激活；E4验证受信站点签名回执，E5表示用户对具体版本的签名声明。Mock Site回执只证明研究connector行为。

## 7. 五层可信状态验证

可验证状态控制层是私有凭据状态的验证与解析平面，不是传统DNS。名称空间根集中治理设备授权；授权设备发布候选状态；State Resolver返回状态和ProofBundle；Local State Verifier执行L1～L5并决定采信；透明日志提供追加历史；公告/区块链Provider只周期锚定根。Stage 2实现`ResearchSingleNodeFinalOrderAuthority`产生单调序、签名回执、冲突集合和研究恢复检查点。该实现明确标记`RESEARCH_ADAPTER`，没有多节点共识或拜占庭容错；回执仍需经过L4/L5透明历史与本地策略。

可信状态解析语义为：

```text
CredentialName
  → State + Principal + Authorization
  + CurrentVersion + AuditCheckpoint + ProofBundle
```

- L1 主体真实性：设备签名、名称空间归属、根凭证链和签名代际；
- L2 操作资格：Capability、CredentialScope、有效期、发行计数器和状态引用；
- L3 动态状态：最终撤销序、版本单调、counter、前序 hash、生命周期边和冲突；
- L4 透明历史：Merkle 包含、一致性路径、签名树头和周期检查点；
- L5 本地采信：按操作风险、缓存年龄和用户策略输出 Verdict。

Verdict 为 ACCEPT、DEGRADED_OFFLINE、DEGRADED_PENDING_LOG、REVIEW_REQUIRED 或带原因的 REJECT。读取已有可信版本可在有限缓存窗口内降级；UPDATE、REVOKE 和 DEVICE_ENROLL 不得在缺少所需证明时静默完成。

透明日志采用 RFC 9162 风格树哈希和确定性叶编码。Monitor 比较树头、验证一致性、发现同 tree size 异根、旧根回滚、同版本双 descriptor 和锚定冲突。公告层只周期保存 NamespaceStateRoot、DeviceStateRoot、CredentialStateRoot、AuditLogRoot、RevocationRoot、CryptoPolicyHash、CheckpointHeight 和可选 VRFOutputHash。

## 8. 日常主流程

### 8.1 创建与自动填充

1. 扩展提交当前 HTTPS Origin 和账号选择，本地安全客户端重新规范化；
2. 密码生成器生成候选，本地安全客户端创建随机 CredentialID 和六类字段对象；
3. 本地事务写 RouteMap、对象引用、CREATE 事件和 outbox；
4. 凭据状态发布层接受 ACTIVE(v1) 后，该版本成为可同步当前状态；
5. 再次访问时 RouteMap 解析 CredentialID，设备先验证可信状态和 ProofBundle；
6. 设备按可信 hash 从本地缓存或同步存储层取 Envelope，验证后只解开密码字段；
7. 本地安全客户端再次核对 OriginBinding，向扩展返回短期、单次使用 secret handle；
8. 扩展填充并发布加密 AUTOFILL_OBSERVED 事件。

此流程不等待链、VRF 或 SCOPE-ZK，也不声称填充等于网站登录成功。

### 8.2 多设备同步

设备 A 发布新 descriptor 与对象后，设备 B 首先解析可信当前版本，再拉取匹配对象。若同步存储层返回更旧版本、错误 hash、错误 policy 或其他 Credential 的对象，设备 B 拒绝。并发候选依靠 CAS 和 descriptor 冲突证据处理，同步存储层无权自行选择赢家。

### 8.3 设备加入与恢复

已有设备批准路径使用一次性挑战、短码/二维码核对、DEVICE_ENROLL 能力和 HPKE 端到端通道传输 RootSecretBundle。新设备随后生成自己的设备秘密和 RootCapsule。

恢复路径使用 256 位 RecoverySecret 解开 RecoveryCapsule，并按恢复策略重新签发设备凭证。只拥有主密码和同步存储层数据的实体不能恢复根包。撤销后产生独立 `Rᵤ[g+1]`，仅封装给剩余设备；历史代际只用于读取合法历史数据。

## 9. 隐私审计与可选事故响应

Epoch 审计密钥为：

```text
Kaudit,e = HKDF(Rᵤ[g],
  "VDNS-PM-AUDIT" || epoch || VRFMaterial)
WP,e = HMAC(Kaudit,e, H(ExactEncode(password)))
```

`VDNS-PM-AUDIT` 是与现有审计对象绑定的 legacy KDF 域字节，仅为兼容保留。

见证仅存在于加密审计事件中，公开叶只保存允许的摘要。安全检查在本地验证 ProofBundle、解密事件，再分析重复使用、最近使用、异常设备、长期未更新、回滚和冲突。跨 Epoch 的公开伪名必须变化；本方案不宣称对全局流量观察者隐藏所有时间和大小元数据。

用户明确确认密码可能泄露时，可固定快照和时间窗口并启动 SCOPE-ZK。该模块可证明 `A = C ˙∪ P`、`C ⊆ F` 和 `ChangedSet = C`，但这些公式只描述单次事故修复活动。未启用模块必须返回明确的可选功能错误，不能阻断密码管理主线。

修复动作可以是改密、撤销会话、改变恢复通道、移除 SSO、重置 MFA、撤销设备或 API token。Completed、Pending、Failed 和 Unknown 依据真实回执记录；只有 Completed 项可改变有效状态，未受影响凭据和无关字段不变。

## 10. 数据与接口设计

核心数据分为本地秘密层、加密对象层、可验证控制层和公开检查点层：

| 层 | 主要对象 | 允许持有明文 |
|---|---|---:|
| 本地秘密 | RootCapsule、RouteMap、活动会话、恢复元数据 | 解锁窗口内允许 |
| 加密对象 | CredentialEnvelope、字段 ciphertext、wrapped DEK、同步 manifest | 否 |
| 控制对象 | StateDescriptor、DeviceCredential、OperationEvent、ProofBundle | 否 |
| 公开检查点 | tree root、state root、revocation root、序号、策略 hash | 否 |

本地 API 统一使用 `/api/v2`，密码和根秘密不作为普通 JSON 字段往返，而使用受会话和 Origin 约束的短期 secret handle。写接口使用 Idempotency-Key；版本写使用 expectedVersion；列表使用 cursor；错误返回稳定 code、message、requestId 和可选安全 details，不返回堆栈、路径、SQL 或秘密。

主要资源为 vault-sessions、password-generations、credential-route-resolutions、credentials、credential-versions、site-confirmations、autofill-authorizations、sync-pulls、sync-publications、device-enrollments、device-revocations、recovery-sessions、vdns-resolutions、audit-events、security-analyses，以及可选 exposure-analyses 和 remediation-campaigns。

## 11. 实现计划与现状

### 11.1 目标模块

```text
apps: browser-extension, local-agent, security-dashboard, remediation-console
services: encrypted-sync, vdns-resolver/verifier, transparency-log,
          checkpoint-anchor, monitor
packages: crypto-core, credential-vault, password-generator,
          lifecycle-state-machine, device-capability, sync-protocol,
          proof-bundle, audit-event, scope-zk, remediation-planner
```

首版仍以单仓库模块化单体实现，服务名表示逻辑边界，不要求立即拆分微服务。

### 11.2 原计划内容

原G0.2计划按G1～G7依次完成协议/密码学迁移、日常密码库、生命周期与同步、可验证状态与透明历史、本地客户端接口和浏览器扩展、隐私审计/可选响应、最终实验与论文冻结。目标形态包含逻辑上的sync service、State Resolver、Local State Verifier、透明日志、检查点公告、Monitor、Mock Site和可选SCOPE-ZK。

### 11.3 实际完成内容

- RootCapsule、RecoveryCapsule、Argon2id、设备绑定解锁和域分离密钥；
- 六字段信封加密、内容寻址对象、RouteMap、OriginBinding和密码生成；
- SQLite事务、幂等、outbox、凭据创建/读取/版本和生命周期状态机；
- 本地安全客户端、当前23项OpenAPI合同、浏览器扩展与Native Messaging边界；
- 设备加入领域流程、HPKE分发、控制面撤销与秘密代际模型；
- 同步manifest、接收端回滚/替换/缺失/冲突拒绝；
- 五层可信状态本地验证、Merkle包含/一致性、Monitor和检查点Provider边界；
- 隐私审计分析器、本地Affected/Remediation基线、SCOPE-ZK unavailable路径；
- 78个Go/扩展测试文件，历史8项故障回归和7项自动恢复测试日志。

Stage 2已把OpenAPI合同测试更新为2.1.0，旧v2.0.0摘要保留为历史文件，当前摘要由真实规范字节重新计算；任务追踪也改为动态统计。阶段结束的全量测试、vet、race、fuzz和安全扫描结果以`test-results/stage2/`为准，任何未实际运行的工具保持`UNVERIFIED`。

### 11.4 部分完成内容

| 内容 | 已完成 | 尚缺 |
|---|---|---|
| 多设备加入 | challenge、能力、HPKE和本地测试 | 真实跨设备网络传输和产品UI |
| 设备撤销 | 控制面、秘密代际、外部修复集合与四态规则 | 完整API/UI、真实站点修复编排 |
| 网站确认 | 耐久候选、E0～E5、Mock E4、UNKNOWN恢复 | 真实E4 connector与信任治理 |
| 跨设备同步 | localhost HTTP、10k分批、manifest与接收验证 | 生产鉴权/TLS/租户隔离/高可用，多进程冲突组合 |
| 可验证状态/透明日志 | L1～L5、单机Merkle/Monitor、研究型最终顺序 | 生产多节点/BFT、见证网络 |
| 隐私审计 | 本地授权分析和100k历史结果 | 部署侧流量隐私和逐样本证据 |
| 实验 | 汇总JSON/CSV和部分原始日志 | E1～E5逐轮原始时延和准确claim映射 |

### 11.5 未完成内容

- 生产多节点/BFT Final Order Authority和生产级最终性；
- 跨设备两个独立进程/SQLite经HTTP产生冲突的完整组合试验；
- 真实公网同步存储和真实浏览器兼容矩阵；
- 真实网站签名回执或经过治理的connector；
- SCOPE-ZK电路、prover、verifier及proof性能实验；
- 最终E1～E8固定环境证据和G7冻结。

### 11.6 研究适配器与生产组件

当前`internal/transparency/application`是单进程研究日志，`memorysync`是本地同步适配器，Mock Site是生命周期测试站点，`memoryanchor`和Anvil是模拟/本地EVM公告适配器。它们验证算法、ABI、状态机和错误路径，不提供生产复制、拜占庭共识、真实站点覆盖、网络SLA或运维安全。仓库没有`services/`目录，开发报告中的service名称表示逻辑部署边界。

### 11.7 功能—代码—测试—证据映射

| 功能族 | 代码 | 测试 | 证据 | 状态 |
|---|---|---|---|---|
| 解锁/胶囊/字段密码学 | `internal/cryptokit` | KAT、篡改、race | G7 E1/crypto快照 | 研究原型完成 |
| RouteMap/Origin/凭据 | credential、SQLite | 单元、合同、E2 | E2汇总 | 研究原型完成 |
| 生命周期/网站确认 | credential/site | Mock、崩溃、UNKNOWN | E4/FI | 部分完成 |
| 设备/撤销/恢复 | device/recovery/resolver | 加入、代际、7项恢复 | E6/recovery | 部分完成 |
| 同步 | sync/memorysync | 云负向矩阵 | E3/FI | 部分完成 |
| 可验证状态/日志 | resolver/transparency/monitor | L1～L5、proof、fork | G4/G7 E5 | 研究核心完成；生产部署未实现 |
| 审计/响应 | audit/exposure/remediation | 权限、集合、重放 | E7/E8 | 部分完成；SCOPE-ZK未实现 |

完整逐项表见`docs/reviews/stage1-completion-audit.md`。

### 11.8 已知限制

本地CAS不提供全局唯一版本；研究Authority提供单节点顺序，生产最终序仍未实现。设备撤销不能收回旧密码，三层撤销尚未完整接入全部API/UI。页面提示不能证明网站已改密，真实E4 Connector未实现。Stage 2的10k同步是localhost HTTP研究适配器，不是公网或生产同步存储。历史漏洞扫描只代表其数据库和日期，只有本阶段真实扫描报告才能支持当前结论。SCOPE-ZK未实现。

### 11.9 协议债务

ADR-012～017冻结信任模型、跨设备冲突/最终序、网站证据等级、撤销边界、CanonicalOrigin和实验声明规则；ADR-018冻结研究型最终序回执；ADR-019冻结VPass命名和legacy wire兼容。E0～E5已使用schema version 2和显式迁移实现，历史对象不被静默重解释。当前协议债务集中在生产共识、多进程组合、可信初始检查点产品流程和外部修复编排。

### 11.10 下一阶段任务

第三阶段按`docs/reviews/stage2-remaining-gaps.md`推进。P0继续完成可信初始检查点产品流程、撤销三层API/UI编排和研究模块组合接线；P1补平台安全存储、真实浏览器/Native Messaging与真实E4信任注册；P2冻结原始实验数据、网络化多进程故障恢复和当前安全扫描；P3在固定环境重测完整L1～L5、网络同步和E1～E8，最后才评估是否达到G7。

## 12. 实验与评价

| 实验 | 自变量/攻击 | 指标 | 判定重点 |
|---|---|---|---|
| E1 解锁恢复 | Argon2 参数、正确/错误密码、复制胶囊 | P50/P95/P99、内存、拒绝率 | 设备绑定和恢复边界 |
| E2 日常管理 | 1、10k、100k 凭据 | 生成、RouteMap、解密、填充延迟 | 主路径不等待链 |
| E3 多设备同步 | 2～N 设备、回滚、替换、并发 | 同步延迟、错误拒绝、冲突率 | 同步存储层无权决定当前版本 |
| E4 生命周期 | 成功、失败、超时、各崩溃点 | 密码丢失、错误激活、恢复时间 | 网站确认一致性 |
| E5 可信状态/日志 | 叶规模、坏证明、双视图 | L1～L5 时延、证明大小、检测率 | 合法输入无误报 |
| E6 撤销代际 | 撤销序、离线设备、旧秘密 | 误接纳率、传播延迟 | 撤销后新操作为零 |
| E7 隐私审计 | 两个 Epoch、已知风险真值 | precision/recall、扫描时间、链接率 | 不公开稳定关系 |
| E8 可选响应 | SCOPE-ZK/基线、部分失败 | 证明时间/大小、越界修改、最小字节 | 不影响日常路径 |

所有性能报告记录 CPU、内存、OS、Go 版本、构建参数、数据生成规则、非安全 seed、预热、重复次数和原始 JSON/CSV。达不到目标时不得删除失败数据或修改口径；应通过正式基线变更说明原因。

## 13. 安全与正确性论证目标

论文需要分别论证而不是混为“系统安全”：

1. 内容机密性：在标准 AEAD/KDF/HPKE 假设及本地端点未被完全控制时，外部存储不能得到字段明文；
2. 授权完整性：没有合法根链、设备签名和允许能力的操作不能被接受；
3. 版本新鲜性：持有可信检查点的设备拒绝低于可信当前版本的对象；
4. 因果一致性：counter、前序 hash、expectedVersion 和 CAS 防止静默覆盖；
5. 撤销安全：最终撤销序后的设备操作被拒绝，但撤销前已取得秘密无法远程收回；
6. 日志可审计性：不一致树头和无一致性路径可产生可验证 finding；
7. Origin 安全：页面不能跨 Origin 请求或填充其他账户密码；
8. 审计隐私：公开投影不含密码、Origin 或稳定见证，但时间/大小模式仍是残余元数据；
9. 修复一致性：可选事故活动中 ChangedSet 只包含真实 Completed 项。

## 14. 论文结构

1. 绪论：密码管理器、多设备同步与不可信同步存储问题；
2. 需求分析与威胁模型：参与者、攻击能力、资产和非目标；
3. VPass 总体架构：六平面、信任边界和数据流；
4. 密码学存储与多设备同步：根胶囊、字段加密、路由和同步；
5. 可验证凭据生命周期：主体、能力、状态机、版本解析与网站确认；
6. 隐私审计与泄露响应增强：Epoch 见证、SCOPE-ZK 和最小修复；
7. 安全分析与形式化定义：机密性、授权、回滚、撤销和隐私；
8. 系统实现与实验：日常性能、同步、日志、审计和可选响应。

## 15. 项目门禁与交付标准

实现以 `spec.md` 为规范、`protocol-registry.md` 为线级格式、`security.md` 为安全边界、`data-model.md` 为持久化语义、OpenAPI 为接口合同、`tasks.md` 为工作分解。任何 ID 宽度、KDF、AAD、状态边、公开字段或安全结论变化都要新增 ADR、更新固定向量并重生冻结基线。

交付必须通过格式化、静态检查、单元、集成、竞态、fuzz、合同、秘密扫描、需求追踪和基线哈希门禁。AC-001～021 均需机器证据或可重复演示。界面、README 和论文必须准确描述模拟器、Anvil、撤销残余风险和 SCOPE-ZK 的可选地位。

## 16. 结论

VPass 是以可验证状态控制层为可信控制骨架的完整密码管理研究原型。主密码用于本地解锁，高熵根和字段加密保护内容，RouteMap 和 OriginBinding 保护账户关系与填充边界，可信状态和透明历史验证主体、授权、版本、撤销和因果，多设备据此独立接受当前状态。隐私审计与 SCOPE-ZK 建立在这条主线之上，增强安全检查和事故修复，不取代密码生成、保存、填充、同步、更新和恢复这些日常核心能力。
