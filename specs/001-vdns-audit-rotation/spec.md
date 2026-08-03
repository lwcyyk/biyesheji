# Spec 001：VPass 可验证密码生命周期管理系统

| 属性 | 值 |
|---|---|
| Spec ID | `001-vpass`（仓库沿用历史目录名） |
| 版本 | `2.1.0` |
| 状态 | Stage 1 protocol design frozen；实现阶段 G6，G7 未达成 |
| 日期 | 2026-08-03 |
| 产品名 | `VPass: Verifiable Password Lifecycle Management System` |
| 论文题目 | VPass：可验证密码生命周期管理系统的设计与实现 |
| 当前展示协议 | `VPass/2` |
| legacy wire协议 | `VDNS-PM/2`，`VDNS-PM-CP-2`，冻结签名/KDF/AAD与旧数据兼容 |
| 上位依据 | `docs/VPass研究生毕业设计开发报告.md` v2.1.0、ADR-011～019 |

> 本文件是 v2 实现、测试和论文结论的规范性依据。“必须（MUST）”“不得（MUST NOT）”“应当（SHOULD）”“可以（MAY）”具有规范性。`protocol-registry.md`、`security.md`、`data-model.md` 和 OpenAPI 合同属于同一 v2.1.0 设计基线。Stage 2已完成部分研究原型闭环，生产共识、真实E4 Connector、SCOPE-ZK和G7证据仍未完成；文档或单元测试存在不等于生产能力完成。

> v1.0.1 是预发布的审计/轮换导向原型。其已完成代码可以复用，但 16 字节 CredentialID、CP-1 AAD、旧枚举和旧 API 不得被宣称为 v2。兼容与重建规则见 ADR-011。

## 1. 产品定位与成功定义

VPass 首先是完整密码管理器。用户只记一个主密码，系统负责生成、加密保存、识别、查询、自动填充、同步、更新、撤销、备份和恢复各网站复杂凭据。其差异化研究目标是：

```text
AEAD 保护密码内容，可验证状态控制层保证凭据版本和生命周期状态可信。
```

系统必须同时提供四类能力：

1. 安全保存密码内容和本地 Origin/账号映射；
2. 验证创建、解析、填充、更新、同步、撤销和迁移等生命周期操作；
3. 在不可信同步存储环境中支持多设备独立解析当前可信版本；
4. 提供隐私化安全审计，并可选地执行 SCOPE-ZK 泄露分析和最小影响修复。

首版成功定义：AC-001～AC-021 全部通过；日常密码管理主路径不依赖链、VRF 或 SCOPE-ZK 在线；E1～E8 产生机器可读证据；所有 FR/NFR/AC 均有任务和测试映射。

## 2. 研究问题、范围与术语

### 2.1 核心研究问题

> 在多设备和不可信同步存储环境中，如何构建可验证密码生命周期管理机制，使用户仅凭一个主密码管理多个网站的复杂凭据，同时让每台设备独立验证凭据当前版本、操作来源、授权状态、撤销状态和历史完整性，而不向同步存储层、可验证状态控制节点或区块链暴露密码、网站和账号关系？

研究主线依次为：内容机密性、可信版本解析、生命周期操作验证、多设备同步；泄露响应是附加增强。

### 2.2 六平面架构

| 平面 | 日常职责 | 信任边界 |
|---|---|---|
| 交互平面 | 浏览器扩展、桌面 UI、网站识别、生成、填充、改密辅助 | 页面输入不可信，本地安全客户端重验 Origin |
| 本地密码学/数据平面 | 主密码解锁、RootCapsule、RouteMap、字段加密、策略 | 唯一明文秘密边界 |
| 生命周期/同步平面 | 创建、查询、版本、冲突、同步、备份、恢复 | 同步存储对象可删改回滚 |
| 可验证状态控制平面 | 身份、能力、撤销、L1～L5、Verdict | 状态解析器返回证明，本地验证器按本地信任根判定 |
| 透明存储/检查点平面 | 密文对象、Merkle 日志、状态根、最小锚定 | 链和日志不保存秘密 |
| 隐私审计/响应平面 | 重复检测、异常使用、SCOPE-ZK、修复规划 | 仅用户明确发起重任务 |

### 2.3 首版范围

- Go 模块化单体、本地安全客户端 API/CLI、独立 Monitor；
- RootCapsule、Argon2id 解锁、密码生成器、本地 RouteMap；
- 六类字段的信封加密和内容寻址对象；
- 凭据创建、可信解析、自动填充、更新、冲突与版本历史；
- 多设备加入、HPKE 分发、加密同步、撤销和新秘密代际；
- RFC 9162 风格透明日志、ProofBundle、五层可信状态验证；
- 密码重复/异常使用审计和 Epoch 隔离见证；
- 可选 SCOPE-ZK 接口、AffectedRoot、修复任务和 RotationRoot；
- Manifest V3 扩展、React 控制台、Mock Site、E1～E8 实验。

### 2.4 关键术语

| 术语 | 规范含义 |
|---|---|
| `SKroot` | 与数据根独立生成的名称空间 Ed25519 根签名密钥 |
| `Rᵤ[g]` | 第 g 代 32 字节高熵名称空间对称根，不由主密码派生 |
| `RootSecretBundle` | 本地封装的根秘密集合；共同封装不代表密钥互相派生 |
| `RootCapsule_i` | 由主密码 KDF 输出与设备秘密共同保护的设备 i 根胶囊 |
| `RouteMap` | 本地加密保存的 `CanonicalOrigin + AccountID → CredentialID` 映射 |
| `CredentialID` | v2 固定为 32 字节随机标识；公开日志仍不得直接暴露 |
| `OriginBinding` | `HMAC(Kname, Encode(CanonicalOrigin, AccountID))`，用于 AAD/路由绑定 |
| `DeviceOperationCredential` | 根签名的设备能力、作用域、有效期与状态凭证 |
| `CredentialStateDescriptor` | 可验证状态解析返回的版本、状态、主体、授权与检查点摘要 |
| `ProofBundle` | L1～L5 所需身份、能力、撤销、因果、日志和本地策略证据 |
| `Final Order Authority` | 为竞争事件签发唯一最终序回执的逻辑权威；当前仅实现`RESEARCH_ADAPTER`单节点版本，未实现生产或多节点共识 |
| `SCOPE-ZK` | 可选泄露影响集合证明模块，不在日常解锁/填充主路径 |

## 3. 用户故事

### US-001 初始化、解锁和锁定（P0）

用户首次初始化独立 `SKroot`、`Rᵤ[1]`、设备秘密和恢复秘密；以后只输入主密码即可在该设备解锁，锁定后敏感材料从活动内存清除。

追踪：FR-001～004；AC-001、AC-011～013。

### US-002 生成、创建和自动填充密码（P0）

用户在网站注册/登录时生成符合策略的复杂密码，本地创建加密凭据；再次访问时通过 RouteMap 和可信状态解析取得当前版本，再安全填充。

追踪：FR-009～018；AC-002、AC-015～016、AC-019。

### US-003 多设备可信同步（P0）

用户在设备 A 更新后，设备 B 从不可信同步存储层下载对象，但只接受可验证状态控制层指定的版本和哈希，拒绝旧密文、冲突版本和错误对象。

追踪：FR-019～027；AC-003～008。

### US-004 可验证更新和网站确认（P0）

新密码必须先本地耐久，再调用网站；网站明确确认或用户签名确认后才激活，模糊结果进入可恢复状态而不猜测。

追踪：FR-020～026；AC-005～006、AC-014。

### US-005 设备加入与撤销（P0）

新设备通过已有授权设备或高熵恢复秘密加入；撤销设备后按最终序拒绝其新操作，并把新代际秘密只封装给剩余设备。

追踪：FR-005～008、FR-027；AC-007～008。

### US-006 独立可信状态解析（P0）

设备依次执行 L1～L5，得到 `ACCEPT/DEGRADED/REVIEW_REQUIRED/REJECT`，同步存储层无权决定当前状态。

追踪：FR-028～035；AC-003、AC-009～010、AC-012～013、AC-016。

### US-007 隐私安全检查（P1）

用户可检查重复密码、异常设备、长期未更新和历史使用；Epoch 见证不在公开层形成稳定密码关联。

追踪：FR-036～038；AC-011、AC-017、AC-019。

### US-008 可选泄露响应与最小影响修复（P2）

用户明确发起事故分析时，可用 SCOPE-ZK 固定影响集合并规划最小动作；只有真实完成项改变状态，Pending/Failed 项不冒充成功。

追踪：FR-039～043；AC-014、AC-018～019。

## 4. 明确非目标

1. 不宣称发明新的 AEAD、签名、KDF、HPKE、VRF 或零知识基础原语；
2. 不防御已完全控制本地安全客户端、浏览器或内核且能读取解锁后明文的恶意软件；
3. 不把主密码、网站密码、Origin、账号、完整凭据或稳定关系写入公开日志/链；
4. 不要求区块链、VRF 或 SCOPE-ZK 在线才能解锁、查询或自动填充；
5. 不把 `AUTOFILL_OBSERVED` 或页面推断当作网站认证成功证明；
6. 不承诺任意真实网站无人值守改密；首版以 Mock Site 和人工/可信 Connector 为验收边界；
7. 不声称设备撤销能够远程擦除其撤销前已经得到的历史秘密或明文；
8. 不声称 AffectedRoot 自身证明影响集合语义正确或全局完整；
9. 不要求新设备仅凭低熵主密码从同步存储层恢复全部根秘密；
10. 不把 Anvil、单机日志或 `SIMULATED` Provider 描述为生产拜占庭共识或真实随机信标。

## 5. 规范性功能需求

### 5.1 根、解锁、设备与恢复

| ID | Pri | 规范性要求 | 验收 |
|---|---:|---|---|
| FR-001 | P0 | 初始化必须由 OS CSPRNG 独立生成 NamespaceID、`SKroot`、`Rᵤ[1]`、设备秘密和 256 位 RecoverySecret；`SKroot` 与 `Rᵤ` 不得互相派生。 | AC-001、AC-013 |
| FR-002 | P0 | 主密码必须经 Argon2id v1.3 派生 `Kpwd`，再与设备 32 字节高熵秘密、DeviceID 经 HKDF 得到设备专属 `Kunlock`；参数进入胶囊格式并可升级。 | AC-001、AC-011、AC-019 |
| FR-003 | P0 | `RootCapsule_i` 必须以 AEAD 封装 `RootSecretBundle`，AAD 绑定 Namespace、Device、胶囊版本和 KDF 参数；主密码、设备秘密和 `Kunlock` 不得上传或记录。 | AC-001、AC-011～013 |
| FR-004 | P0 | 恢复必须使用已有合法设备批准或 256 位 RecoverySecret；仅有主密码和同步存储数据不得恢复完整根秘密。 | AC-008、AC-011 |
| FR-005 | P0 | 每台设备必须拥有独立 Ed25519 认证密钥、X25519/HPKE 接收密钥和稳定 DeviceID，私钥不得离开设备安全边界。 | AC-007～009、AC-013 |
| FR-006 | P0 | `DeviceOperationCredential` 必须绑定 Namespace、设备公钥、能力、CredentialScope、有效期、发行计数器、状态引用、秘密代际和根签名。 | AC-007、AC-009、AC-012～013 |
| FR-007 | P0 | 新设备加入必须验证一次性挑战及 `DEVICE_ENROLL` 权限，通过端到端加密通道传输根包，并发布新设备凭证。 | AC-008、AC-012～013 |
| FR-008 | P0 | 撤销有效性按最终日志/锚定顺序判断；撤销后生成独立 `Rᵤ[g+1]`，只封装给剩余设备，旧代际只用于历史解密。 | AC-007、AC-009、AC-016 |

### 5.2 日常密码库与自动填充

| ID | Pri | 规范性要求 | 验收 |
|---|---:|---|---|
| FR-009 | P0 | v2 CredentialID、EventID、CampaignID 必须为 32 字节不可预测随机值；不得把 Origin 或账号直接用作公开标识。 | AC-002、AC-013 |
| FR-010 | P0 | RouteMap 必须在本地加密保存 `CanonicalOrigin + AccountID → CredentialID`，支持一个 Origin 多账号并拒绝不规范/opaque Origin。 | AC-002、AC-015 |
| FR-011 | P0 | 密码生成器必须使用 OS CSPRNG 或域分离的高熵 PRF，满足版本化站点策略；不得使用普通 PRNG 或简单取模。 | AC-002、AC-019 |
| FR-012 | P0 | Origin、用户名、密码、TOTP、恢复码和备注必须使用独立随机 DEK 信封加密；字段 AAD 绑定 Namespace、CredentialID、原 encryption version、FieldType、CryptoPolicyHash 和 OriginBinding。 | AC-002、AC-011～015 |
| FR-013 | P0 | 创建流程必须经过 `NONEXISTENT → CREATE_PENDING → ACTIVE(v1)`；只有密文对象、本地映射、签名 CREATE 事件和可验证状态均满足时才发布 ACTIVE。 | AC-002、AC-009、AC-012 |
| FR-014 | P0 | 查询/填充前必须先解析 `CredentialStateDescriptor` 和 ProofBundle，得到可信 current version、envelope hash、授权状态和 Verdict。 | AC-002～003、AC-009 |
| FR-015 | P0 | 从同步存储层获取的 CredentialEnvelope 必须匹配可信状态解析返回的 CredentialID、version、envelope hash、policy hash 和字段引用；旧版、缺失、冲突或错误密文 fail closed。 | AC-003、AC-012～013 |
| FR-016 | P0 | 解密前后必须重新规范化并核对当前浏览器 Origin 与 OriginBinding；扩展不得指定任意 CredentialID 绕过 RouteMap。 | AC-002、AC-012、AC-015 |
| FR-017 | P0 | 自动填充只产生 `USE_OBSERVED/AUTOFILL_OBSERVED`；提交、登录推断、网站确认必须保持不同证据等级。 | AC-002、AC-017 |
| FR-018 | P0 | 查询和填充不得等待链、VRF 或 SCOPE-ZK；使用事件只等待本地耐久 outbox，后台完成日志和检查点发布。 | AC-002、AC-016、AC-019 |

### 5.3 生命周期、同步和版本

| ID | Pri | 规范性要求 | 验收 |
|---|---:|---|---|
| FR-019 | P0 | 同步服务只保存/分发加密对象、版本索引和证明，不持有解密根，不得决定当前可信版本。 | AC-003～004、AC-011 |
| FR-020 | P0 | 所有版本写必须携带 `expected_version` 和 `previous_descriptor_hash`。持久层 CAS 只保证单个本地事务边界内至多一个 accepted pointer 更新；跨设备并发候选必须由冲突检测、Final Order Receipt 和显式裁决处理，不得声称本地 CAS 提供全局唯一版本。 | AC-004、AC-006 |
| FR-021 | P0 | 规范事件必须绑定操作类型、主体、CredentialID、旧/新版本、载荷哈希、设备计数器、前序事件哈希、能力引用和签名。 | AC-004、AC-009、AC-012～013 |
| FR-022 | P0 | 同一设备计数器必须单调递增；counter、前序摘要或已接受 descriptor 冲突必须原子拒绝且不产生部分 outbox/指针更新。 | AC-004、AC-006、AC-012 |
| FR-023 | P0 | 修改必须经过 `ACTIVE(v) → UPDATE_PENDING(v+1) → SITE_CONFIRM_PENDING → ACTIVE(v+1)`；E0～E2不得激活，E3仅在严格L5策略下激活，E4/E5可按策略激活；确认前旧版本保持可用。 | AC-005、AC-014 |
| FR-024 | P0 | 网站已改密后，新密码必须先本地加密耐久并进入 `SITE_CHANGED_LOCAL_COMMIT_PENDING`；外部失败不得丢失新密码或回退使用旧密码。 | AC-005、AC-014、AC-016 |
| FR-025 | P0 | 其他设备必须以可验证当前版本和 envelope hash 接受同步；`returned_version < trusted_version` 或 hash 不一致必须拒绝。 | AC-003～004、AC-012 |
| FR-026 | P0 | 同版本多 descriptor、模糊网站结果或无法证明当前值必须进入 `CONFLICTED/REVIEW_REQUIRED/UNKNOWN`，不得自动选择或覆盖。 | AC-004～005、AC-009 |
| FR-027 | P0 | 备份、恢复和设备迁移必须保持 RootCapsule、RouteMap、版本历史、对象引用和可信检查点一致；恢复后仍需执行五层可信状态验证。 | AC-008、AC-012、AC-016 |

### 5.4 可验证状态控制、透明历史与最小锚定

| ID | Pri | 规范性要求 | 验收 |
|---|---:|---|---|
| FR-028 | P0 | L1 必须验证设备签名、名称空间归属、根凭证链和签名 key generation。 | AC-009、AC-012～013 |
| FR-029 | P0 | L2 必须验证操作 Capability、CredentialScope、有效期、发行计数器和状态引用。 | AC-007、AC-009 |
| FR-030 | P0 | L3 必须验证最终撤销序、排序回执、版本单调、前序哈希、设备 counter、生命周期边和并发冲突；未经 Final Order Authority 签发并达到策略要求检查点的序号不得称为最终序。 | AC-004、AC-006～007、AC-009 |
| FR-031 | P0 | L4 必须验证日志包含、从本地可信检查点到候选树头的一致性、树头签名和所需周期锚定。 | AC-003、AC-009～010、AC-012 |
| FR-032 | P0 | L5 必须按操作风险、缓存年龄、策略和本地用户决定输出 `ACCEPT/DEGRADED/REVIEW_REQUIRED/REJECT`；高风险写不得静默降级。 | AC-009、AC-016 |
| FR-033 | P0 | 透明日志必须支持追加、包含/一致性证明、签名检查点和批量锚定；公开叶只含允许的伪名、类型、摘要和粗粒度元数据。 | AC-009～012、AC-017 |
| FR-034 | P0 | Monitor 必须检测同 tree size 异根、无一致性路径、回滚、同版本双 descriptor 和锚定冲突，并保留可验证证据。 | AC-010、AC-012 |
| FR-035 | P0 | 链/公告层只周期保存状态根、日志根、撤销根、策略哈希、序号和可选 VRF 摘要；不得保存密码、Origin、账号、完整事件或每次填充。 | AC-010～011、AC-016 |

### 5.5 隐私审计与可选泄露响应

| ID | Pri | 规范性要求 | 验收 |
|---|---:|---|---|
| FR-036 | P1 | 审计见证必须由 `Kaudit_e` 和 `ExactEncode(password)` 产生并置于加密事件；Epoch 改变时公开伪名/见证不可稳定链接。 | AC-011、AC-017 |
| FR-037 | P1 | 密码重复、历史使用和异常设备分析必须要求 `AUDIT_ANALYZE` 能力、一次性 secret handle 和已验证 ProofBundle，分析结果不保存密码或稳定 ReuseTag。 | AC-011、AC-017 |
| FR-038 | P1 | 安全检查必须至少输出重复使用、长期未更新、异常设备、回滚/冲突版本和证据置信度，并允许用户逐项查看支持证明。 | AC-010、AC-017、AC-019 |
| FR-039 | P2 | SCOPE-ZK 仅在用户明确发起事故分析时运行；未实现或未启用时必须返回 `OPTIONAL_FEATURE_UNAVAILABLE`，不得阻断日常密码管理。 | AC-016、AC-018 |
| FR-040 | P2 | AffectedRoot 只提供快照和集合的提交后绑定性；`A=C ˙∪ P` 等关系只适用于泄露响应活动，不代表整个系统。 | AC-018、AC-021 |
| FR-041 | P2 | 修复规划器可选择改密、撤销会话/设备/API token、重置 MFA、改变恢复通道等动作，并记录成本、前置条件和恢复风险。 | AC-018 |
| FR-042 | P2 | 只有网站/系统真实确认完成的项可以改变有效状态；Pending/Failed/Unknown 项不得冒充成功，未受影响凭据及无关字段逐字节不变。 | AC-014、AC-018 |
| FR-043 | P2 | RotationRoot 必须绑定每项动作、旧/新版本、最终状态、证据摘要和 attempt，并与 Completed/Pending/Failed 计数一致。 | AC-018～019 |

## 6. 非功能需求

### 6.1 安全与隐私

| ID | Pri | 要求 | 验收 |
|---|---:|---|---|
| NFR-SEC-001 | P0 | 主密码、设备秘密、RecoverySecret、根秘密、私钥、字段明文、DEK 和审计见证不得进入日志、URL、命令参数、环境变量、遥测或公开检查点。 | AC-011 |
| NFR-SEC-002 | P0 | 所有安全随机数来自 OS CSPRNG；测试随机源必须显式标记且生产入口拒绝。 | AC-001、AC-013 |
| NFR-SEC-003 | P0 | KDF、AEAD、签名、哈希、Merkle 和证明均带协议/套件/对象/Namespace/用途域分离。 | AC-012～013 |
| NFR-SEC-004 | P0 | 密码学、解析、证明或 Origin 核对失败必须 fail closed，不返回部分明文、不填充、不迁移状态。 | AC-012、AC-015 |
| NFR-SEC-005 | P0 | 敏感缓冲使用后尽力清零；锁屏、超时、进程退出必须销毁活动解锁会话。 | AC-001、AC-011 |
| NFR-SEC-006 | P0 | 扩展仅通过 Native Messaging/受认证回环连接本地安全客户端，校验安装令牌、Origin 和短期 CSRF nonce。 | AC-002、AC-015 |
| NFR-SEC-007 | P1 | 依赖锁版本并生成 SBOM；发布前执行漏洞、许可证和秘密扫描。 | AC-020～021 |

### 6.2 正确性与一致性

| ID | Pri | 要求 | 验收 |
|---|---:|---|---|
| NFR-COR-001 | P0 | 状态迁移只能经领域状态机；API、扩展和 SQL adapter 不得直接拼写下一状态。 | AC-005～006、AC-009 |
| NFR-COR-002 | P0 | 关键写使用事务、write-ahead 和 outbox；崩溃后恢复到确定状态或显式 UNKNOWN。 | AC-004～006、AC-014 |
| NFR-COR-003 | P0 | 相同可信检查点、对象和策略在合法设备上产生相同 current version、DescriptorHash、Merkle root 和 Verdict。 | AC-003、AC-009～010 |
| NFR-COR-004 | P0 | 安全顺序使用日志/锚定序；墙钟只用于展示、KDF 参数生效期和审计窗口。 | AC-007、AC-017 |

### 6.3 性能

| ID | Pri | 目标 | 验收 |
|---|---:|---|---|
| NFR-PERF-001 | P0 | Argon2id 解锁在基准机 P95 ≤ 1.5 s，峰值内存符合已记录参数。 | AC-019 |
| NFR-PERF-002 | P0 | 10,000 凭据 RouteMap 查询 P95 ≤ 5 ms。 | AC-019 |
| NFR-PERF-003 | P0 | 单凭据字段解密 P95 ≤ 10 ms（不含 Argon2id 解锁）。 | AC-019 |
| NFR-PERF-004 | P0 | 本地缓存命中时自动填充端到端 P95 ≤ 100 ms，不等待链或 VRF。 | AC-002、AC-019 |
| NFR-PERF-005 | P0 | 10,000 凭据初始同步和增量同步均输出吞吐、P50/P95/P99 与错误率。 | AC-004、AC-019 |
| NFR-PERF-006 | P0 | 100,000 叶下单对象 L1～L5 验证 P95 ≤ 25 ms。 | AC-009、AC-019 |
| NFR-PERF-007 | P0 | 1,000,000 叶包含证明不超过 32 个哈希加固定元数据。 | AC-010、AC-019 |
| NFR-PERF-008 | P1 | 100,000 加密审计事件扫描 ≤ 5 s；只更新密码时无关字段重加密字节为 0。 | AC-014、AC-017、AC-019 |

### 6.4 可用性与恢复

| ID | Pri | 要求 | 验收 |
|---|---:|---|---|
| NFR-AVL-001 | P0 | RootCapsule、RouteMap、outbox、pending version、可信检查点和恢复元数据在重启后可恢复。 | AC-005、AC-008、AC-016 |
| NFR-AVL-002 | P0 | 对象库/云不可用时允许使用已验证本地缓存，不得激活未耐久对象或声称已同步。 | AC-003、AC-016 |
| NFR-AVL-003 | P0 | 日志/锚定层不可用时 READ/AUTOFILL 仅在缓存策略内降级；UPDATE/REVOKE/ENROLL 默认拒绝或等待。 | AC-009、AC-016 |
| NFR-AVL-004 | P1 | 演示数据可一键重建；示例不含生产秘密，备份/恢复测试不得依赖公网业务服务。 | AC-020～021 |

### 6.5 可维护性、API 与复现

| ID | Pri | 要求 | 验收 |
|---|---:|---|---|
| NFR-MNT-001 | P0 | 领域核心不依赖 HTTP、数据库、文件系统、浏览器或链 SDK，采用端口/适配器。 | AC-020～021 |
| NFR-MNT-002 | P0 | 密钥库、对象库、同步、日志、锚定、站点 Connector 均有测试适配器和明确生产替换边界。 | AC-020～021 |
| NFR-MNT-003 | P0 | E1～E8 固定数据规则、非安全 seed、重复次数、环境字段及 JSON/CSV schema。 | AC-019～020 |
| NFR-MNT-004 | P1 | CI 运行格式化、静态检查、单元、集成、竞态、fuzz、合同和秘密扫描。 | AC-020～021 |
| NFR-API-001 | P0 | API 使用 `/api/v2`、统一 camelCase 字段、回环/Unix Socket 鉴权和细粒度能力校验。 | AC-002、AC-009、AC-021 |
| NFR-API-002 | P0 | 所有写接口要求 Idempotency-Key；同 key 异 body 返回 409；版本写要求 expectedVersion。 | AC-004、AC-006 |
| NFR-API-003 | P0 | 统一错误结构；500 不返回堆栈、路径、SQL 或密码材料；列表使用 cursor 分页，输入/证明有尺寸和速率上限。 | AC-011～012、AC-021 |

## 7. 协议、状态与主路径

### 7.1 日常自动填充主路径

```text
Browser Origin
  → local RouteMap
  → CredentialID
  → State Resolve(State + Version + ProofBundle)
  → verify L1-L5
  → fetch encrypted object
  → verify version/hash/policy
  → unwrap field DEK
  → decrypt password
  → re-check OriginBinding
  → autofill
  → durable encrypted USE_OBSERVED outbox
```

除本地安全客户端和已验证缓存外，任一外部组件离线都不能导致设备接受未经证明的新版本。普通填充不得调用 SCOPE-ZK。

### 7.2 独立状态机

1. Vault：`LOCKED ↔ UNLOCKED`，失败/超时回到 `LOCKED`；
2. Device：`ACTIVE ↔ SUSPENDED → REVOKED`；
3. Credential aggregate：`ACTIVE/SUSPENDED/REVOKED/CONFLICTED`，保存 local/accepted 指针；
4. Credential version：保留候选、网站更新、未知、本地提交待证明、ACTIVE、SUPERSEDED、ABORTED 等内部崩溃恢复状态；
5. Event publication：`LOCAL_PENDING → OBJECT_STORED → LOG_INCLUDED → CHECKPOINT_ANCHORED`；
6. Optional remediation：Campaign/Item 分离，Completed/Pending/Failed 可独立重算。

### 7.3 Verdict 门禁

| Verdict | READ/AUTOFILL | CREATE/UPDATE | ENROLL/REVOKE | AUDIT/SCOPE-ZK |
|---|---:|---:|---:|---:|
| `ACCEPT` | 允许 | 允许 | 允许 | 按能力允许 |
| `DEGRADED_OFFLINE` | 缓存窗口内允许并告警 | 禁止新全局状态 | 禁止 | 本地草稿/排队 |
| `DEGRADED_PENDING_LOG` | 允许既有 accepted version | 不宣布全局完成 | 禁止 | 本地排队 |
| `REVIEW_REQUIRED` | 默认不填充冲突项 | 只允许解决冲突 | 用户明确确认 | 允许查看证据 |
| `REJECT_*` | 禁止 | 禁止 | 禁止 | 禁止 |

### 7.4 可验证状态控制层部署与最终序

可验证状态控制层继承VDNS可验证私有名称状态的信任模型，不是传统DNS或DNSSEC替代。名称空间根负责中心化授权治理；设备、State Resolver、Local State Verifier、Monitor和见证者执行分布式验证。授权设备发布候选对象，State Resolver收集并返回解析包，Local State Verifier作最终采信。

`finalSequence`只能由Final Order Authority通过签名排序回执产生。透明日志记录已排序对象并给出包含/一致性证明；检查点公告层周期发布根。检查点前的日志位置属于provisional，达到L5要求的受信检查点后才作为final。当前仓库实现了`ResearchSingleNodeFinalOrderAuthority`、`SINGLE_PROCESS_RESEARCH_LOG`与模拟/Anvil研究适配器，没有实现多节点共识或拜占庭容错。Authority自身的恢复检查点不替代透明日志/公告层检查点。

新设备必须通过已有设备、恢复胶囊绑定承诺或用户带外核对取得可信初始检查点。高风险写在最终序或一致历史不可得时失败关闭。只读仅可在已接受缓存和年龄策略内降级。

### 7.5 跨设备冲突

两台设备可同时从v1生成`v2-A`和`v2-B`。各自本地CAS成功不代表全局成功。发现相同base上的不同候选或同版本不同DescriptorHash时必须保留两分支并进入`CONFLICTED`。同步存储层、到达时间、墙钟和设备ID均无裁决权。具有`CONFLICT_RESOLVE`能力的用户主体显式选择后，裁决事件引用全部候选并进入最终序。

### 7.6 网站证据等级

| 等级 | 名称 | 默认处理 |
|---:|---|---|
| E0 | `AUTOFILL_OBSERVED` | `UNKNOWN`，禁止激活 |
| E1 | `SUBMIT_OBSERVED` | `UNKNOWN`，禁止激活 |
| E2 | `PAGE_SUCCESS_INDICATED` | `REVIEW_REQUIRED`，禁止激活 |
| E3 | `NEW_PASSWORD_RELOGIN_CONFIRMED` | 严格绑定新会话、Origin、候选版本后由L5决定，否则review |
| E4 | `SITE_SIGNED_RECEIPT` | 验证站点信任、nonce、版本和签名后可激活 |
| E5 | `USER_SIGNED_CONFIRMATION` | 可按策略激活，只表示用户声明 |

Mock Site的签名只能证明研究connector行为，不代表真实网站证明。旧证据枚举不得按新值静默解释。

### 7.7 撤销与CanonicalOrigin

设备撤销分为控制面撤销、秘密代际隔离和外部凭据修复。前两层完成仍不能收回设备已经知道的旧密码。外部凭据只有获得各站点对应确认后才可标记完成。

CanonicalOrigin由小写scheme、IDNA/Punycode小写hostname和非默认端口组成。HTTPS为默认允许方案；远程HTTP拒绝，loopback开发例外需显式开启。默认端口省略，非默认端口保留，子域精确隔离。iframe默认禁止且只能在top-frame与target精确同源时例外。每次重定向后必须重新路由和授权，原secret handle不得跨Origin复用。

## 8. Given–When–Then 验收场景

### AC-001 独立根与设备绑定解锁

**Given** 新名称空间和两台设备；**When** 初始化、正确/错误主密码解锁、复制另一设备胶囊；**Then** `SKroot` 与 `Rᵤ` 独立，正确设备可解锁，错误密码或缺失设备秘密失败，秘密不进入日志。

### AC-002 创建、解析和自动填充主闭环

**Given** 用户在规范 HTTPS Origin 创建账号；**When** 生成密码、创建 v1、再次打开网站并填充；**Then** 先完成可信状态解析和对象验证，填充正确密码，总流程不等待链、VRF 或 SCOPE-ZK。

### AC-003 不可信同步存储回滚/替换被拒绝

**Given** 可验证当前版本为 v2；**When** 同步存储层返回 v1、其他 Credential 的对象、错误 hash 或缺失字段；**Then** 本地拒绝且不返回/填充部分明文。

### AC-004 多设备同步与冲突

**Given** 两设备共享可信根；**When** A 发布 v2、B 同步，以及两者并发提交不同 v2；**Then** 单设备本地CAS保持原子，两台设备可形成两个候选；接收端检测后进入CONFLICTED，只有带最终排序回执的显式裁决可形成唯一已接受版本。

### AC-005 网站确认与崩溃恢复

**Given** ACTIVE(v) 和本地耐久候选 v+1；**When** 网站成功、失败、响应丢失并在每个持久化点崩溃；**Then** 成功后不丢新密码，失败保留 v，未知进入 REVIEW/UNKNOWN，不猜测网站状态。

### AC-006 CAS 和前序摘要

**Given** 相同 expectedVersion 和 previousDescriptorHash；**When** 同一数据库并发双写或伪造前序；**Then** 本地最多一个事务成功，失败响应含currentVersion且无部分outbox；跨设备并发按AC-004形成并处理冲突。

### AC-007 最终撤销序

**Given** 设备在 anchor sequence s 被撤销；**When** 它在 s 后提交并回填 observedAt；**Then** L3 按最终序拒绝，新代际秘密只分发给剩余设备。

### AC-008 新设备加入与恢复

**Given** 新设备密钥和一次性挑战；**When** 有/无 DEVICE_ENROLL 授权、正确/错误恢复秘密；**Then** 只有合法路径得到新胶囊，只有主密码和云数据不能完成恢复。

### AC-009 五层解析与 Verdict

**Given** 一份有效 ProofBundle；**When** 分别破坏身份、能力、撤销、因果、日志和策略；**Then** 有效输入 ACCEPT，破坏项返回相应 DEGRADED/REVIEW_REQUIRED/REJECT，禁止模糊成功。

### AC-010 日志回滚和分叉检测

**Given** 合法树头及双视图/旧根/错误一致性路径；**When** Monitor 比较；**Then** 全部攻击产生可验证 finding，合法追加无误报。

### AC-011 公开面无秘密

**Given** 完整 E1～E8；**When** 扫描日志、链、API、错误、对象元数据和前端存储；**Then** 不出现主密码、设备秘密、RecoverySecret、Origin、账号、密码、DEK、稳定审计见证或私钥。

### AC-012 篡改 fail closed

**Given** 有效胶囊、字段对象、事件和 ProofBundle；**When** 篡改 nonce/AAD/tag、签名、字段类型、OriginBinding、Merkle 路径或检查点；**Then** 无部分明文、无填充、无状态迁移。

### AC-013 跨域重放拒绝

**Given** 对象在特定 Namespace/Device/Credential/Field/版本/套件有效；**When** 重放到另一上下文；**Then** 验证失败且原状态不变。

### AC-014 字段级最小更新

**Given** 含六类字段的凭据；**When** 只修改密码；**Then** 只有密码字段、密码版本、descriptor 和允许元数据变化，其他字段对象/DEK envelope/digest 逐字节不变。

### AC-015 RouteMap 与 Origin 绑定

**Given** 同域多账号、IDN、默认端口和恶意 iframe；**When** 查找/填充；**Then** 规范 Origin 与账号精确选择凭据，跨 Origin 或扩展自报 CredentialID 被拒绝。

### AC-016 离线降级不进入链关键路径

**Given** 云、日志、锚定、VRF 或 SCOPE-ZK 分别离线；**When** 查询/填充已有 accepted version；**Then** 缓存策略内可 DEGRADED 填充，写/撤销/加入不静默完成，SCOPE-ZK 离线不阻断主功能。

### AC-017 Epoch 隐私审计

**Given** 重复密码、正常/异常设备事件和两个 Epoch；**When** 运行本地安全检查；**Then** 可发现预设风险，公开投影不出现稳定密码关联，跨 Epoch 伪名不同。

### AC-018 可选泄露响应边界

**Given** 已启用或未启用 SCOPE-ZK；**When** 用户发起事故分析和部分失败修复；**Then** 未启用返回明确可选功能错误，启用时 `A=C ˙∪ P` 只描述该活动，Completed/Pending/Failed 与真实结果一致。

### AC-019 性能和规模

**Given** 固定实验机和 NFR-PERF-001～008 数据集；**When** 运行规定重复次数；**Then** 输出 P50/P95/P99、CPU、内存、OS、构建参数并达到阈值或先完成正式阈值变更。

### AC-020 一键演示与机器证据

**Given** 空数据目录和已安装工具链；**When** 执行单一顶层命令；**Then** 初始化、创建/填充、双设备同步、更新、撤销、五层可信状态验证、审计和可选响应演示均可复现并导出 JSON/CSV。

### AC-021 论文与 UI 声明准确

**Given** 所有界面、README 和论文材料；**When** 审核术语与结论；**Then** 系统被描述为密码生命周期管理器，SCOPE-ZK 标为可选增强，Anvil/模拟器/撤销/完整性残余风险均准确标注。

## 9. 实验体系

| 实验 | 目标 | 强制输出/条件 |
|---|---|---|
| E1 | 解锁、胶囊、设备加入和恢复 | 正/负向成功率、Argon2 时间/内存、跨设备胶囊拒绝 |
| E2 | 日常密码管理 | 生成、创建、RouteMap、解密、自动填充延迟；10k/100k 查询 |
| E3 | 多设备与不可信同步存储 | 同步延迟、回滚/替换拒绝、冲突解析、离线恢复 |
| E4 | 生命周期与网站确认 | CREATE/UPDATE/CONFIRM/UNKNOWN/崩溃点，锁号和密码丢失均为 0 |
| E5 | 可验证状态与透明日志 | 分别报告完整L1～L5延迟和Merkle微基准、证明大小、检查点、分叉/回滚检测 |
| E6 | 撤销和新代际 | 撤销后误接纳 0，新代际解密成功 0，传播延迟 |
| E7 | 隐私审计 | 写入/窗口扫描开销、风险 precision/recall、跨 Epoch 不可链接投影 |
| E8 | 可选泄露响应 | SCOPE-ZK/基线对比、部分失败、越界修改拒绝、最小影响字节数 |

## 10. 追踪与完成门禁

- FR-001～008 → 根/设备/恢复 → AC-001、007～009、011～013、016 → G1/G3；
- FR-009～018 → 日常密码管理 → AC-002～003、011～016、019 → G1/G2/G5；
- FR-019～027 → 生命周期/同步 → AC-003～008、012、014、016 → G2/G3；
- FR-028～035 → 可验证状态/透明日志 → AC-003、007、009～013、016 → G4；
- FR-036～043 → 审计/可选响应 → AC-011、014、016～019、021 → G6；
- 全部 NFR 必须至少映射一个 AC 并在 `tasks.md` 有实现或验证任务。

需求完成必须同时满足：实现与负向路径、自动测试、对应 AC 证据、无秘密泄露、文档/API/状态/ADR 同步。协议字段、ID 宽度、KDF/AAD、状态边或安全结论变化必须新建 ADR 并重生基线与固定向量。实验必须保存逐样本原始值并标记MODEL、UNIT_TEST、LOCAL_INTEGRATION、MULTI_PROCESS_LOCAL、NETWORKED_TESTBED、PUBLIC_TESTNET或PRODUCTION，不得以弱证据等级替代强声明。
