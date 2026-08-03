# VPass Spec 2.1.0 安全规范与威胁模型

| 属性 | 值 |
|---|---|
| 版本 | `2.1.0` |
| 当前展示协议 | `VPass/2` |
| legacy wire协议 | `VDNS-PM/2` |
| legacy wire密码套件 | `VDNS-PM-CP-2` |
| 威胁建模 | STRIDE + 资产/信任边界分析 |
| 规范依据 | Spec 001 v2.1.0、ADR-002～005、ADR-011～019 |

本文规定实现必须满足的安全边界。不得以“使用了加密、可验证状态控制层或区块链”替代逐项威胁分析。

## 1. 安全目标与优先级

1. **字段机密性**：同步存储层、日志、可验证状态控制层和公告层不能得到 Origin、账号、密码、TOTP、恢复码和备注明文；
2. **本地解锁安全**：主密码不离开设备，同步存储中的 RootCapsule 单独不足以验证主密码猜测；
3. **授权完整性**：只有当时具有相应能力且未撤销的设备可以产生可接受操作；
4. **版本新鲜性**：持有可信检查点的设备拒绝同步存储回滚、替换和冲突伪装；
5. **Origin 完整性**：页面不能请求或填充其他 Origin/账号的凭据；
6. **失败安全**：网站确认、持久化或证明不明确时，不猜测、不返回部分明文、不静默推进；
7. **历史可审计性**：分叉、回滚、同版本双状态和撤销后操作可被发现；
8. **隐私最小化**：公开层不产生稳定密码复用关系，事故分析不进入日常关键路径。

## 2. 信任边界与数据流

```text
[Untrusted Web Page]
       │ Origin/form messages
       ▼
[Browser Extension] -- authenticated local channel --> [Local Secure Client]
                                                         │ plaintext boundary
                                    ┌────────────────────┼───────────────────┐
                                    ▼                    ▼                   ▼
                              [Local DB/Object]   [Untrusted Storage] [State/Log/Anchor]
                                    │ encrypted          │ encrypted          │ public proofs
                                    └────────────────────┴───────────────────┘
```

浏览器页面始终不可信。扩展是受限客户端，不是安全裁判。本地安全客户端必须独立获取/验证 top-frame Origin、安装令牌、短期 nonce、vault session、Credential route 和 Capability。同步存储响应、状态解析响应、日志证明和链上数据都需在本地验证后采信。

## 3. 资产分类

| 等级 | 资产 | 存储/传输要求 |
|---|---|---|
| S0 极密 | 主密码、设备秘密、RecoverySecret、`Rᵤ[g]`、`SKroot`、设备私钥、活动 DEK | 仅设备安全存储/受控内存；不得遥测 |
| S1 机密 | RouteMap、字段明文、站点策略细节、审计解密结果 | 本地加密；短期最小暴露 |
| S2 敏感伪名 | CredentialID、DeviceID、对象访问模式、状态/事件引用 | 按需披露、分域伪名、限流 |
| S3 可公开 | 签名树头、允许字段的根、序号、套件 ID | 完整性保护并最小化元数据 |

CredentialID 是随机值并不意味着可以无条件公开；访问模式仍可能形成关联。

## 4. 攻击者模型

### 4.1 覆盖的攻击能力

- 获取服务器数据库、对象桶、备份和日志；
- 控制同步服务，删除、替换、回滚、重排和重放对象；
- 控制网络并观察时间、大小、频率元数据；
- 运行恶意网页、iframe 或扩展消息发送者；
- 持有已撤销设备及其撤销前取得的历史秘密；
- 提供错误状态解析响应、Merkle 路径、树头或旧检查点；
- 触发并发更新、崩溃、超时、重试和幂等键冲突；
- 读取公开公告层并对低熵密码进行离线字典尝试。

### 4.2 不覆盖的能力

- 完全控制解锁后的本地安全客户端/内核并实时读取明文；
- 破坏标准原语的安全假设；
- 强制真实网站提供可验证改密 API；
- 远程抹除撤销设备已经复制的历史明文。

这些边界必须在论文、UI 和演示中明示。

## 5. 密码学规范

### 5.1 根生成与独立性

初始化使用 OS CSPRNG 独立生成：

```text
Rᵤ[1]          ← random(32)
SKroot/PKroot  ← Ed25519.KeyGen()
DeviceSecretᵢ ← random(32)
RecoverySecret← random(32)
```

不得从主密码派生 `Rᵤ`，不得从 `Rᵤ` 派生 `SKroot`，不得跨设备复制 DeviceSecret。测试随机源必须通过依赖注入并在生产构建中拒绝。

### 5.2 Argon2id 与 RootCapsule

```text
Kpwd = Argon2id(
  password = ExactUTF8(masterPassword),
  salt = capsuleSalt,
  memory = m, iterations = t, lanes = p,
  output = 32)

Kunlockᵢ = HKDF-SHA-256(
  IKM = Kpwd || DeviceSecretᵢ,
  salt = NamespaceID,
  info = "VDNS-PM/2/ROOT-UNLOCK" || DeviceIDᵢ,
  L = 32)
```

RootCapsule 使用 AES-256-GCM；AAD 为确定性编码的 ProtocolID、suite、capsule version、NamespaceID、DeviceID、Argon2 参数和 bundle schema version。nonce 为 12 字节随机值，禁止在相同 key 下重复。

主密码、Kpwd、Kunlock、DeviceSecret 不得上传。服务器只得到 RootCapsule 时缺少 DeviceSecret，不能直接验证主密码猜测；本机胶囊与 DeviceSecret 同时泄露后仍可离线猜测，这是残余风险而非已消除风险。

建议实现首次运行基准校准 Argon2id，使目标设备 P95 接近 0.5～1.5 秒并记录内存；参数下调必须由明确兼容策略完成。拒绝未登记版本、过低参数和资源耗尽参数。

### 5.3 RecoveryCapsule

```text
Krecovery = HKDF-SHA-256(
  IKM = RecoverySecret,
  salt = recoverySalt,
  info = "VDNS-PM/2/RECOVERY-CAPSULE",
  L = 32)
```

RecoverySecret 是 256 位随机恢复材料，不是用户选择的提示问题。恢复胶囊 AAD 绑定 Namespace、恢复策略、版本和创建序。恢复后必须签发新设备凭证；疑似泄露时更换恢复秘密和胶囊。

### 5.4 域分离派生

所有派生使用 HKDF-SHA-256，并包括协议、套件、Namespace、秘密代际和用途：

```text
Kwrap     = Derive(Rᵤ[g], "CREDENTIAL-WRAP")
Kname     = Derive(Rᵤ[g], "CREDENTIAL-NAME")
Kaudit    = Derive(Rᵤ[g], "AUDIT")
Krelation = Derive(Rᵤ[g], "RELATION")
Krotation = Derive(Rᵤ[g], "ROTATION")
```

签名 key、HPKE key、RootCapsule key、字段 DEK、审计/关系/轮换 key 不得混用。每类对象必须有独立 label 和固定向量。

### 5.5 RouteMap 与 Origin 规范化

只允许 `https` 和明确的loopback `http`开发例外；远程HTTP、opaque origin、含用户信息URL、无效IDN、非法端口和未解析主机必须拒绝。CanonicalOrigin由小写scheme、小写IDNA ASCII/Punycode host和可选非默认端口构成。默认80/443端口省略，非默认端口保留。path、query和fragment不属于Origin；作为Origin输入携带这些部分时拒绝，不得静默截断。

子域名精确隔离，不按eTLD+1自动共享。iframe默认禁止，只有策略允许且top-frame与target精确同源时例外。每次重定向后重新计算top-level CanonicalOrigin、重新RouteMap/可信状态/OriginBinding验证；旧secret handle不得跨Origin使用。HTTPS降级到HTTP永不自动携带秘密。

```text
OriginBinding = HMAC-SHA-256(
  Kname,
  ExactEncode("VDNS-PM/2/ORIGIN-BINDING",
              CanonicalOrigin, AccountID))
```

RouteMap 本地加密保存真实映射；OriginBinding 可进入字段 AAD/加密 descriptor，但不得作为稳定公共日志键。扩展自报的 CredentialID 仅是提示，本地安全客户端必须重新路由并做常量时间比较。

### 5.6 字段加密

每个 Credential/Field/Version 使用随机 32 字节 DEK；AES-256-GCM nonce 为随机 12 字节。字段 AAD 的确定性顺序为：

```text
ProtocolID, ProtocolVersion, SuiteID,
NamespaceID, CredentialID(32), CredentialVersion,
FieldType, EncryptionVersion, CryptoPolicyHash,
OriginBinding
```

六类 FieldType 为 ORIGIN、USERNAME、PASSWORD、TOTP、RECOVERY_CODES、NOTE。AAD 不包含明文 Origin。任何 nonce、AAD、tag、field type、version、binding 或 policy hash 不符都必须在返回部分明文前失败。

### 5.7 HPKE 与设备分发

设备根包和代际秘密使用 HPKE Base mode：DHKEM(X25519, HKDF-SHA256)、HKDF-SHA256、AES-256-GCM。Info/AAD 绑定协议、Namespace、recipient DeviceID、公钥指纹、secret generation、发行序和 object type。禁止把一个设备的封装重放给另一设备。

### 5.8 签名与编码

Ed25519 签署确定性 CBOR 的域分离字节；不签署 JSON 序列化。整数使用规范最短表示，map key 次序固定，禁止浮点、重复 key、未登记字段和 Unicode 隐式规范化。验证器先检查版本/尺寸/枚举/规范编码，再检查签名。

## 6. 身份、能力和撤销

DeviceOperationCredential 根签名内容至少绑定 NamespaceID、DeviceID、认证/HPKE 公钥、allowedOperations、credentialScope、validFrom、validUntil、issuanceCounter、statusRef、secretGeneration 和 credentialVersion。

事件接受条件：

```text
Accept(E) =
  SignatureValid(E)
  ∧ RootChainValid(E.credential)
  ∧ CapabilityAllows(E.operation, E.credentialId)
  ∧ FinalSequence(E) within validity
  ∧ DeviceNotRevokedAt(E.finalSequence)
  ∧ CounterAndPredecessorFresh(E)
  ∧ LogIncluded(E)
  ∧ LocalPolicyAccepts(E)
```

墙钟 `observedAt` 不决定撤销先后。撤销按最终日志/锚定序生效；攻击者回填旧时间不能恢复权限。撤销后生成独立 `Rᵤ[g+1]` 并仅向剩余设备封装。旧代际仍可解历史对象，因此撤销不等同于历史秘密擦除。

## 7. 生命周期与失败安全

### 7.1 创建

ACTIVE(v1) 前必须满足：字段对象耐久、RouteMap 事务成功、CREATE 事件签名、设备能力允许、StateDescriptor 唯一且进入 outbox。任一步失败均保持 NONEXISTENT/CREATE_PENDING，不留下可填充半对象。

### 7.2 读取和自动填充

顺序不可颠倒：路由 → 可信当前状态 → L1～L5 → 对象 hash/version/policy → 字段解密 → OriginBinding 重验 → 单次 secret handle。日志、锚定或同步存储离线时只可在明确缓存策略内读取已接受版本；不能因此接受新版本。

secret handle 必须绑定 vault session、extension installation、top-frame Origin、CredentialID、FieldType、到期时间和单次使用计数。不得通过 URL、命令行、环境变量或可持久化前端存储传递密码。

### 7.3 更新和网站确认

新密码在调用网站前必须本地加密耐久。回执分类：

| 等级/结果 | 状态 | 处理 |
|---|---|---|
| E0 AUTOFILL_OBSERVED | UNKNOWN | 禁止激活 |
| E1 SUBMIT_OBSERVED | UNKNOWN | 禁止激活 |
| E2 PAGE_SUCCESS_INDICATED | REVIEW_REQUIRED | 页面提示不得作为网站证明 |
| E3 NEW_PASSWORD_RELOGIN_CONFIRMED | REVIEW_REQUIRED/可激活 | 仅新会话、精确Origin、候选版本和新鲜证据均满足时由L5决定 |
| E4 SITE_SIGNED_RECEIPT | SITE_CONFIRMED | 验证站点信任、nonce、版本、有效期和签名后可激活 |
| E5 USER_SIGNED_CONFIRMATION | USER_CONFIRMED | 可按策略激活，必须显示其不是站点证明 |
| 明确失败 | FAILED | 保持ACTIVE(v)，保存可解释原因 |
| 超时/连接断开/不明确结果 | UNKNOWN | 禁止猜测，允许查询或获取新证据 |
| 网站已成功、本地提交未完 | SITE_CHANGED_LOCAL_COMMIT_PENDING | 使用本地耐久候选恢复发布 |

Mock Site回执只具有研究夹具语义，不能外推为真实网站证明。

### 7.4 CAS 与 outbox

同一事务校验 expectedVersion、previousDescriptorHash 和 deviceCounter，写 version/descriptor、对象引用、事件和 outbox。幂等 key 相同且 body digest 相同返回原结果；相同 key 异 body 返回 409。失败事务不产生悬空 accepted pointer 或第二条 outbox。

该CAS只约束一个本地数据库。两设备可以分别产生有效`v2-A/v2-B`。发现相同base的不同候选或同版本不同摘要时必须保留分支并进入CONFLICTED。云顺序、墙钟和先到先得不能裁决；用户授权的CONFLICT_RESOLVE事件与FinalOrderReceipt共同形成最终选择。

## 8. 可验证状态、日志和检查点

可验证状态控制层继承VDNS可验证私有名称状态的信任模型，不是传统DNS。名称空间根集中治理设备授权；设备、State Resolver、Local State Verifier、Monitor和见证者分布式验证。State Resolver返回ProofBundle不等于可信，Local State Verifier始终是采信点。

Final Order Authority是`finalSequence`的唯一逻辑生产者。透明日志只追加带排序回执的对象。回执进入受信透明日志检查点前为provisional；达到L5要求后才作为最终安全顺序。Stage 2已实现可持久化的`ResearchSingleNodeFinalOrderAuthority`及签名回执/研究检查点，部署标签为`RESEARCH_ADAPTER`。它没有实现多节点共识或拜占庭容错，单机日志、模拟器和Anvil同样只能作为研究适配器。

L1～L5 必须逐层返回机器可读原因，不能把“签名有效”当成全部验证。

| 层 | 必查项 | 典型拒绝 |
|---|---|---|
| L1 | 根链、Namespace、设备签名、key generation | BAD_SIGNATURE、WRONG_NAMESPACE |
| L2 | operation、scope、有效序、发行 counter | CAPABILITY_DENIED、OUT_OF_SCOPE |
| L3 | revoke sequence、version、counter、predecessor、状态边 | REVOKED、ROLLBACK、CONFLICT |
| L4 | leaf、inclusion、consistency、tree-head、anchor | BAD_PROOF、FORK、STALE_CHECKPOINT |
| L5 | 操作风险、缓存年龄、用户策略 | DEGRADED、REVIEW_REQUIRED、POLICY_REJECT |

日志叶必须是最小公开投影，禁止 Origin、账号、密码、字段 ciphertext、wrapped DEK、稳定审计见证和完整 CredentialID。Merkle 哈希使用独立 leaf/node prefix，树头签名绑定 tree size、root、timestamp/sequence、log ID 和 suite。

公告层只锚定周期根和策略 hash。普通自动填充不得执行链交易、等待区块确认或请求 VRF。模拟器和 Anvil adapter 必须在 Provider 字段中标识，不得被描述为生产共识。新设备的可信初始检查点必须由已有设备、恢复承诺或带外核对引入；同步存储TOFU不得授权高风险写。

Stage 2的网络同步实现固定标记`RESEARCH_HTTP_SYNC_ADAPTER`。它提供localhost真实HTTP、内容hash、manifest、cursor、幂等、超时/重试和请求体限制，也能模拟对象替换、旧manifest和隐藏分支。该适配器没有生产身份认证、租户隔离、服务发现、公网TLS运维或高可用，不能称为生产同步存储。任何HTTP响应仍是不可信输入，只有与可验证最终/冲突状态和完整对象验证一致后才可更新本地accepted pointer。

Monitor 必须持久化相互冲突的签名树头、验证路径和来源摘要；告警不能包含秘密。双视图、同大小异根、无法从可信树头一致扩展、旧锚定覆盖和同版本双 descriptor 均为 finding。

## 9. 同步与恢复安全

同步存储层没有 current-version 权限。pull 返回对象前后，设备都以可信状态 descriptor 验证 CredentialID、version、envelope hash、policy hash 和对象 digest。`returnedVersion < currentVersion`、同版本 hash 不同或对象缺失均 fail closed。

新设备加入要求一次性挑战、短码/二维码人工核对、DEVICE_ENROLL 能力、HPKE 接收 key 所有权证明和新设备凭证发布。一次性挑战消费必须原子化并设短时有效期。

备份必须包含加密 Root/Recovery capsule、RouteMap、对象引用、版本历史、可信检查点和恢复策略；恢复后不得跳过五层可信状态验证。备份完整性不等于可用性，恢复演练必须实际解锁、路由、验证和填充 Mock Site。

## 10. 隐私审计和可选响应

```text
Kaudit,e = HKDF(Rᵤ[g], "VDNS-PM/2/AUDIT" || e || VRFMaterial)
Witness  = HMAC(Kaudit,e, H(ExactEncode(password)))
```

本文出现的 `VDNS-PM/2/*` 是冻结 legacy KDF/AAD 域字节，仅为保持旧密文、签名和SQLite数据可读而保留。命名迁移不改变它们。

Witness 只放入加密事件。公共层不得保存可跨 Epoch 稳定关联同密码的标签。分析需要 AUDIT_ANALYZE 能力、相应代际秘密、已验证 ProofBundle 和一次性 secret handle。分析结果保存风险类别和证据引用，不保存密码或稳定标签。

SCOPE-ZK 是可选插件。禁用或不可用时返回 OPTIONAL_FEATURE_UNAVAILABLE；解锁、读取、自动填充和普通同步不得依赖它。AffectedRoot 只承诺特定输入快照和输出集合，不单独证明语义或全局完整性。

事故修复只允许 Completed 项改变有效状态；Pending、Failed、Unknown 保持原状态。修改密码时其他字段 ciphertext、wrapped key 和 digest 不变。RotationRoot 绑定 attempt 和真实结果，不能由计划项冒充完成项。

## 11. STRIDE 风险登记

评分采用影响/可能性 1～5，风险为乘积。

| ID | 类别 | 威胁 | 风险 | 控制 | 残余风险 |
|---|---|---|---:|---|---|
| T-01 | S/I/E | 根或设备私钥泄露 | 20 | OS key store、独立 key、撤销、新代际、恢复根 | 历史明文无法收回 |
| T-02 | I | 同步存储替换/回滚对象 | 20 | 可验证version/hash、检查点、CAS | 缓存全丢时可用性下降 |
| T-03 | S/E | 恶意页面跨站请求 | 20 | top-frame Origin、RouteMap、OriginBinding、单次 handle | 本地端点完全控制不覆盖 |
| T-04 | T/R | 网站确认伪造 | 16 | 证据分级、可信 Connector、用户签名、UNKNOWN | 网站缺少强回执 |
| T-05 | T | 同版本并发覆盖 | 16 | expectedVersion、descriptor hash、counter、CAS | 需要人工解冲突 |
| T-06 | R/I | 日志分叉/回滚 | 15 | consistency、签名 tree head、Monitor、锚定 | 多观察者不足时发现延迟 |
| T-07 | E | 撤销设备继续提交 | 20 | final sequence、revocation root、新代际 | 撤销前秘密仍在 |
| T-08 | I/D | 崩溃导致站点/本地不一致 | 20 | 新密码先耐久、独立状态、outbox、恢复查询 | 站点无查询接口时人工确认 |
| T-09 | I | nonce 重用或 AAD 缺域 | 20 | CSPRNG、统一构造器、KAT/fuzz | RNG/平台故障 |
| T-10 | I/E | 反序列化歧义 | 15 | 确定性 CBOR、尺寸/枚举限制、先解析后验证 | 第三方库缺陷 |
| T-11 | I | 主密码离线猜测 | 20 | DeviceSecret、Argon2id、强密码提示、硬件保护 | 本机材料同时泄露仍可猜测 |
| T-12 | I | RecoverySecret 丢失/泄露 | 15 | 256 位随机、离线备份、恢复演练、轮换 | 用户永久丢失会导致不可恢复 |
| T-13 | I | 日志/错误/遥测泄密 | 20 | 结构化脱敏、统一错误、secret scan | 依赖库意外输出 |
| T-14 | I | 公开元数据关联 | 12 | 随机伪名、Epoch、padding/批量、最小根 | 全局观察者仍见时间/大小 |
| T-15 | D | 证明/Argon2 资源耗尽 | 12 | 参数上限、输入限长、速率限制、缓存 | 合法高负载 |
| T-16 | T | v1 字节被当成 v2 | 16 | protocol/suite 硬拒绝、显式导入 | 导入器自身缺陷 |

## 12. API 和浏览器安全

- 优先 Unix domain socket 或 Native Messaging；使用回环 HTTP 时必须绑定 127.0.0.1、随机安装令牌和短期 CSRF nonce；
- CORS 不允许通配符，Host/Origin/extension ID 必须 allowlist；
- vault session 短时、空闲超时、锁屏销毁，并限制单会话并发 secret handles；
- 密码、恢复码和根秘密不进入 URL、query、错误、审计字段和前端持久化；
- CSP 禁止远程脚本和动态 eval；content script 与页面 world 隔离；
- iframe 默认禁止填充，只有策略允许且 top-frame/target Origin 均匹配时例外；
- clipboard 写入需要用户动作、短时清除并显示警告；
- 统一错误不暴露凭据是否存在给未授权调用者。

## 13. 密钥生命周期与事件响应

| 事件 | 立即动作 | 后续动作 |
|---|---|---|
| 主密码疑似泄露 | 锁定会话、改主密码并重封本机胶囊 | 审计本机访问；无需直接更换网站密码，除非有使用证据 |
| DeviceSecret/认证 key 泄露 | 挂起设备、发布撤销 | 新 `Rᵤ` 代际、检查异常事件、重签设备状态 |
| `Rᵤ[g]` 泄露 | 停止向该代际写入 | 独立生成 g+1、重新封装、评估相关网站凭据 |
| `SKroot` 泄露 | 停止普通签发 | 使用独立恢复授权替换根、锚定 compromise recovery |
| RecoverySecret 泄露 | 撤销旧恢复策略 | 生成新秘密和胶囊、演练恢复 |
| 云/日志泄露 | 禁止销毁证据 | 核对检查点、扫描秘密、必要时轮换受影响 key |

密钥轮换不得通过对旧根哈希得到新根；新代际必须独立随机。历史数据重加密和未来写入换代是不同操作，必须分别记录。

设备撤销的报告必须拆为三层：控制面撤销、秘密代际隔离、外部凭据修复。控制面成功不能表示旧密码被收回；秘密代际完成不能表示网站密码已修改；外部修复逐站点以E3～E5证据判断。

## 14. 安全测试门禁

1. RootCapsule 正确/错误密码、错误设备、篡改参数和资源上限测试；
2. 字段 nonce/AAD/tag/OriginBinding/FieldType/version 变异测试；
3. 签名、能力、scope、撤销、counter、predecessor 和 suite 跨域重放；
4. 云回滚、替换、删除、并发 descriptor 和部分对象；
5. 网站成功/失败/MFA/超时及每个事务点崩溃；
6. Merkle 包含/一致性、同 tree size 异根和旧锚定；
7. 扩展 iframe、IDN、默认端口、恶意消息、handle 重用和会话过期；
8. 日志、错误、对象元数据、SQLite、前端存储和实验产物秘密扫描；
9. `go test`、race、fuzz、静态检查、依赖漏洞、许可证与 SBOM；
10. 可选模块关闭时完整日常路径仍通过。

任何密码学或证明失败后仍返回字段明文、任何确认前激活、任何撤销后接受、任何跨 Origin 填充均为阻断发布的问题。
