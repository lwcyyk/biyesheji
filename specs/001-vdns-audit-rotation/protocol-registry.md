# VPass Spec 2.1.0 协议注册表

> 当前展示协议标签为 `VPass/2`。本注册表中的 `VDNS-PM`、`VDNS-PM-CP-2` 和相关domain字符串已经进入签名、KDF/AAD、SQLite和固定向量，因此按ADR-019作为deprecated legacy wire identifiers冻结保留。它们不再是产品展示名。

| 属性 | 值 |
|---|---|
| 注册表版本 | `2.1.0` |
| Protocol ID | `VDNS-PM`（legacy wire） |
| Protocol version | `2` |
| Suite ID | `VDNS-PM-CP-2`（legacy wire） |
| 编码 | RFC 8949 Deterministic CBOR |
| 哈希/HMAC/HKDF | SHA-256 / HMAC-SHA-256 / HKDF-SHA-256 |
| 签名 | Ed25519 |
| AEAD | AES-256-GCM，12 字节 nonce，16 字节 tag |
| HPKE | RFC 9180 Base: X25519/HKDF-SHA256/AES-256-GCM |
| 密码 KDF | Argon2id v1.3，32 字节输出 |
| 依据 | ADR-003、ADR-011～017 |

此文件是 v2 线格式和域分离字符串的唯一注册表。未知值必须拒绝，不能按最接近枚举猜测。

## 1. 固定宽度

| 类型 | 宽度 | 生成/约束 |
|---|---:|---|
| NamespaceID | 16 B | OS CSPRNG，非全零 |
| DeviceID | 16 B | OS CSPRNG，非全零 |
| CredentialID | 32 B | OS CSPRNG，非全零 |
| EventID | 32 B | OS CSPRNG，非全零 |
| CampaignID | 32 B | OS CSPRNG，非全零 |
| KeyID/ObjectDigest/DescriptorHash | 32 B | SHA-256 或随机，按字段定义 |
| OriginBinding | 32 B | HMAC-SHA-256 |
| AES key/DEK/根秘密/恢复秘密 | 32 B | OS CSPRNG 或登记 KDF |
| AES-GCM nonce | 12 B | 每 key 唯一，生产使用 OS CSPRNG |
| Ed25519 public/private/signature | 32/64/64 B | 标准格式 |
| X25519 public/private | 32/32 B | 标准格式 |
| SHA-256 digest/Merkle root | 32 B | 标准输出 |

`uint64` 用于版本、counter、final sequence、tree size、Epoch 和发行序；不得使用负数或浮点数。

## 2. 顶层协议头

所有签名、KDF、AAD 和哈希输入的逻辑头必须包含：

```text
protocol_id      = "VDNS-PM"
protocol_version = 2
suite_id         = "VDNS-PM-CP-2"
object_type      = registered enum
namespace_id     = bstr .size 16
```

域分离前缀统一为 UTF-8：

```text
"VDNS-PM/2/VDNS-PM-CP-2/" || Purpose
```

Purpose 必须来自本注册表，大小写敏感，不含尾随 NUL。

## 3. ObjectType

| 值 | 名称 | 说明 |
|---:|---|---|
| 1 | ROOT_CAPSULE | 设备绑定根胶囊 |
| 2 | RECOVERY_CAPSULE | 高熵恢复胶囊 |
| 3 | DEVICE_OPERATION_CREDENTIAL | 根签名设备能力凭证 |
| 4 | CREDENTIAL_ENVELOPE | 凭据字段密文对象 |
| 5 | CREDENTIAL_STATE_DESCRIPTOR | VDNS 当前状态描述 |
| 6 | OPERATION_EVENT | 生命周期规范事件 |
| 7 | SYNC_MANIFEST | 加密对象同步清单 |
| 8 | SECRET_ENVELOPE | HPKE 设备秘密封装 |
| 9 | AUDIT_EVENT | 加密使用/审计事件 |
| 10 | LOG_LEAF | 公开最小日志叶 |
| 11 | SIGNED_TREE_HEAD | 签名树头 |
| 12 | PROOF_BUNDLE | L1～L5 证明集合 |
| 13 | CHECKPOINT | 周期状态根检查点 |
| 14 | EXPOSURE_ANALYSIS | 可选影响分析 |
| 15 | REMEDIATION_CAMPAIGN | 可选修复活动 |
| 16 | ROTATION_ROOT | 修复结果承诺 |

v1 的同名数字不继承语义；解析必须先匹配 Protocol/Suite。

## 4. FieldType

| 值 | 名称 | 明文类型 |
|---:|---|---|
| 1 | ORIGIN | CanonicalOrigin UTF-8 |
| 2 | USERNAME | 精确 UTF-8，不隐式规范化 |
| 3 | PASSWORD | 精确字节，通常 UTF-8 |
| 4 | TOTP | 结构化 seed/算法/digits/period |
| 5 | RECOVERY_CODES | 有序精确字符串数组 |
| 6 | NOTE | UTF-8 文本 |

## 5. OperationType

| 值 | 名称 | 所需 Capability |
|---:|---|---|
| 1 | CREATE | CREATE |
| 2 | RESOLVE | READ |
| 3 | AUTOFILL | AUTOFILL |
| 4 | USE_OBSERVED | PUBLISH_AUDIT |
| 5 | UPDATE_PREPARE | UPDATE |
| 6 | UPDATE_CONFIRM | UPDATE |
| 7 | SYNC_PUBLISH | UPDATE 或 CREATE |
| 8 | SYNC_ACCEPT | READ |
| 9 | ROTATE | ROTATE |
| 10 | MIGRATE | MIGRATE |
| 11 | SUSPEND | REVOKE |
| 12 | REVOKE | REVOKE |
| 13 | DEVICE_ENROLL | DEVICE_ENROLL |
| 14 | RELATION_PUBLISH | RELATION_PUBLISH |
| 15 | AUDIT_ANALYZE | AUDIT_ANALYZE |
| 16 | EXPOSURE_ANALYZE | AUDIT_ANALYZE |
| 17 | REMEDIATION_COMMIT | ROTATE 或 REVOKE |

## 6. Capability

| bit | 名称 | 范围 |
|---:|---|---|
| 0 | READ | 解析/解密允许 scope 的凭据 |
| 1 | AUTOFILL | 向匹配 Origin 提供短期字段 handle |
| 2 | PUBLISH_AUDIT | 发布加密使用证据 |
| 3 | CREATE | 创建新 Credential |
| 4 | UPDATE | 创建候选、确认和字段更新 |
| 5 | ROTATE | 密码轮换和修复动作 |
| 6 | MIGRATE | 受控导入/迁移 |
| 7 | REVOKE | 挂起/撤销凭据、设备、token |
| 8 | DEVICE_ENROLL | 批准和签发新设备 |
| 9 | RELATION_PUBLISH | 发布加密关系事实 |
| 10 | AUDIT_ANALYZE | 解密/分析授权范围审计历史 |

其余 bit 保留且必须为 0。拥有 PUBLISH_AUDIT 不隐含 AUDIT_ANALYZE。

## 7. CredentialScope

| 值 | 名称 | 编码 |
|---:|---|---|
| 1 | NAMESPACE_ALL | null |
| 2 | CREDENTIAL_SET | 排序去重的 CredentialID bstr32 数组 |
| 3 | ORIGIN_BINDING_SET | 排序去重的 OriginBinding bstr32 数组 |
| 4 | SINGLE_CREDENTIAL | CredentialID bstr32 |

scope 比较按原始字节字典序和常量时间 membership 实现；公开日志不直接复制 scope 内容。

## 8. LifecycleStatus

### 8.1 聚合状态

| 值 | 名称 |
|---:|---|
| 1 | ACTIVE |
| 2 | UPDATE_PENDING |
| 3 | SITE_CONFIRM_PENDING |
| 4 | SUSPENDED |
| 5 | SUPERSEDED |
| 6 | REVOKED |
| 7 | CONFLICTED |

### 8.2 内部凭据版本状态

| 值 | 名称 |
|---:|---|
| 1 | CANDIDATE_LOCAL |
| 2 | SITE_CHANGE_IN_PROGRESS |
| 3 | SITE_CHANGED_LOCAL_COMMIT_PENDING |
| 4 | SITE_CONFIRM_PENDING |
| 5 | ACTIVE |
| 6 | SUPERSEDED |
| 7 | FAILED |
| 8 | UNKNOWN |
| 9 | ABORTED |

### 8.3 事件发布状态

| 值 | 名称 |
|---:|---|
| 1 | LOCAL_PENDING |
| 2 | OBJECT_STORED |
| 3 | LOG_INCLUDED |
| 4 | CHECKPOINT_ANCHORED |
| 5 | PUBLICATION_FAILED |

## 9. EvidenceLevel

| 值 | 等级 | 名称 | 含义 | 激活策略 |
|---:|---:|---|---|---|
| 0 | E0 | AUTOFILL_OBSERVED | 扩展填充过，不表示提交 | 禁止 |
| 1 | E1 | SUBMIT_OBSERVED | 观察到表单提交，不表示认证成功 | 禁止 |
| 2 | E2 | PAGE_SUCCESS_INDICATED | 页面、导航或DOM提示成功 | 禁止，进入REVIEW_REQUIRED |
| 3 | E3 | NEW_PASSWORD_RELOGIN_CONFIRMED | 独立新会话用候选密码重登录成功 | 仅严格L5策略允许 |
| 4 | E4 | SITE_SIGNED_RECEIPT | 受信站点/connector签名回执 | 验证完整后允许 |
| 5 | E5 | USER_SIGNED_CONFIRMATION | 用户对具体版本显式签名 | 允许，但不是站点证明 |

这是v2.1.0编码。v2.0.0旧值1～5的含义不同，现有对象必须标记legacy并经显式迁移；不得仅替换显示名称或按新表解释旧字节。Stage 2代码、OpenAPI和SQLite v8已使用E0～E5；真实E4 Connector仍为`NOT_IMPLEMENTED`，Mock E4不得激活。

## 9.1 FinalOrderReceipt

`final_sequence`只能来自Final Order Authority签名回执：

ADR-018补正后的研究适配器线对象为：

```cddl
final-order-receipt = {
  "payload": final-order-receipt-payload,
  "signature": bstr .size 64
}

final-order-receipt-payload = {
  "domain": "VDNS-PM:FINAL-ORDER-RECEIPT",
  "protocol_id": "VDNS-PM",
  "protocol_version": 2,
  "suite_id": "VDNS-PM-CP-2",
  "adapter_kind": "RESEARCH_ADAPTER",
  "namespace_id": bstr .size 16,
  "credential_id": bstr .size 32,
  "ordered_object_digest": bstr .size 32,
  "final_sequence": uint .ge 1,
  ? "previous_ordered_digest": bstr .size 32,
  "authority_key_id": bstr .size 32,
  "authority_key_generation": uint .ge 1
}
```

签名覆盖`final-order-receipt-payload`的确定性CBOR。`receipt_digest`由域分离前缀、载荷CBOR和签名派生，不放入线对象形成自引用。解析成功不等于可信，接收方还必须使用预置信任的Authority公钥验证签名和key generation。

回执进入满足L5策略的透明日志检查点前只能标记`PROVISIONAL_ORDERED`。同一Namespace和final_sequence对应不同对象摘要构成分叉证据。当前Authority与其恢复检查点均标记`RESEARCH_ADAPTER`，不提供生产共识或拜占庭容错。

## 10. Verdict

| 值 | 名称 |
|---:|---|
| 1 | ACCEPT |
| 2 | DEGRADED_OFFLINE |
| 3 | DEGRADED_PENDING_LOG |
| 4 | REVIEW_REQUIRED |
| 5 | REJECT_IDENTITY |
| 6 | REJECT_CAPABILITY |
| 7 | REJECT_REVOKED |
| 8 | REJECT_CAUSAL |
| 9 | REJECT_PROOF |
| 10 | REJECT_ORIGIN |
| 11 | REJECT_POLICY |
| 12 | REJECT_OBJECT |

API 可返回更细 error code，但不得把拒绝映射成 2xx 成功。

## 11. Purpose 注册表

| Purpose | 用途 |
|---|---|
| ROOT-UNLOCK | 主密码输出与设备秘密合成解锁 key |
| ROOT-CAPSULE-AAD | RootCapsule AEAD AAD |
| RECOVERY-CAPSULE | RecoveryCapsule key/AAD |
| CREDENTIAL-WRAP | 字段 DEK wrapping key |
| CREDENTIAL-NAME | RouteMap/OriginBinding key |
| FIELD-AAD | 字段 AEAD AAD |
| DEVICE-CREDENTIAL-SIGN | 设备能力凭证签名 |
| OPERATION-EVENT-SIGN | 生命周期事件签名 |
| DEVICE-SECRET-HPKE | 设备根包/代际秘密 HPKE |
| STATE-DESCRIPTOR | descriptor hash/signature |
| SYNC-MANIFEST | sync manifest hash/signature |
| AUDIT | 审计根派生 |
| AUDIT-EPOCH | Epoch key 派生 |
| RELATION | 隐私关系事实 |
| ROTATION | 修复活动 key |
| LOG-LEAF | Merkle leaf hash |
| LOG-NODE | Merkle internal node hash |
| TREE-HEAD-SIGN | 签名树头 |
| CHECKPOINT-SIGN | 周期检查点签名 |
| FINAL-ORDER-RECEIPT | 最终排序回执 |

## 12. 规范编码

### 12.1 RootCapsule

```cddl
root-capsule = {
  1: "VDNS-PM",
  2: 2,
  3: "VDNS-PM-CP-2",
  4: 1,                       ; capsule version
  5: bstr .size 16,           ; namespace_id
  6: bstr .size 16,           ; device_id
  7: bstr .size 16,           ; Argon2 salt
  8: uint, 9: uint, 10: uint, ; memoryKiB, iterations, lanes
  11: bstr .size 12,          ; nonce
  12: bstr,                   ; ciphertext || tag
  13: uint                     ; bundle schema version
}
```

### 12.2 CredentialEnvelope

```cddl
credential-envelope = {
  1: "VDNS-PM", 2: 2, 3: "VDNS-PM-CP-2",
  4: bstr .size 16,           ; namespace_id
  5: bstr .size 32,           ; credential_id
  6: uint,                    ; credential_version
  7: [1*6 field-reference],
  8: bstr .size 32,           ; origin_binding
  9: bstr .size 32,           ; descriptor_hash
  10: bstr .size 32           ; crypto_policy_hash
}

field-reference = {
  1: uint .ge 1 .le 6,        ; field_type
  2: uint,                    ; encryption_version
  3: bstr .size 32,           ; ciphertext object digest
  4: bstr .size 32,           ; wrapped-key object digest
  5: bstr .size 32            ; plaintext commitment/digest when policy allows
}
```

字段数组按 field_type 严格升序且不重复。plaintext digest 不得是无 key 的低熵密码哈希；密码字段使用隐藏承诺或省略语义值。

### 12.3 CredentialStateDescriptor

```cddl
credential-state-descriptor = {
  1: "VDNS-PM", 2: 2, 3: "VDNS-PM-CP-2",
  4: bstr .size 16,
  5: bstr .size 32,
  6: uint,                    ; active_version
  7: bstr .size 32,           ; active_envelope_hash
  8: bstr .size 32 / null,    ; previous_descriptor_hash
  9: uint,                    ; lifecycle_status
  10: bstr .size 32,          ; last_operation_event
  11: bstr .size 32,          ; authorized_device_set_root
  12: bstr .size 32,          ; audit_checkpoint
  13: uint,                   ; final_sequence
  14: bstr .size 16,          ; updater_device_id
  15: bstr .size 64           ; updater_signature
}
```

### 12.4 OperationEvent 签名体

```cddl
operation-event-body = {
  1: "VDNS-PM", 2: 2, 3: "VDNS-PM-CP-2",
  4: bstr .size 16,           ; namespace
  5: bstr .size 32,           ; event_id
  6: uint,                    ; operation_type
  7: bstr .size 16,           ; device_id
  8: bstr .size 32 / null,    ; credential_id
  9: uint / null, 10: uint / null, ; old/new version
  11: bstr .size 32,          ; payload hash
  12: uint,                   ; device counter
  13: bstr .size 32 / null,   ; previous event hash
  14: bstr .size 32,          ; capability credential hash
  15: uint                     ; secret generation
}
```

签名对象是 Purpose 前缀与上述确定性 CBOR 字节拼接后的 SHA-512/Ed25519 标准输入，不对 JSON 或数据库行签名。

## 13. Merkle 与检查点

```text
LeafHash(x) = SHA256(0x00 || Domain(LOG-LEAF) || ExactCBOR(x))
NodeHash(l,r)=SHA256(0x01 || Domain(LOG-NODE) || l || r)
EmptyTreeHash=SHA256("")
```

签名树头绑定 logID、treeSize、rootHash、finalSequence、suite 和签名 key generation。ProofBundle 明确包含 starting trusted checkpoint、candidate tree head、inclusion proof、consistency proof、device/root chain、capability/status proof 和 local policy inputs 的 hash。

检查点公开字段白名单：NamespaceStateRoot、DeviceStateRoot、CredentialStateRoot、AuditLogRoot、RevocationRoot、CryptoPolicyHash、CheckpointHeight、FinalSequence、ProviderKind 和可选 VRFOutputHash。不得加入密码、Origin、账号、完整对象、每次填充事件或稳定复用标签。

## 14. 错误与兼容

协议解析错误采用稳定分类：UNSUPPORTED_PROTOCOL、UNSUPPORTED_SUITE、NON_CANONICAL_ENCODING、INVALID_LENGTH、UNKNOWN_ENUM、INVALID_SIGNATURE、INVALID_AAD、ROLLBACK、CONFLICT、REVOKED、PROOF_INVALID、POLICY_REJECT 和 OPTIONAL_FEATURE_UNAVAILABLE。

v2 不接受 `VDNS-CREDENTIAL-AUDIT/1`、`VDNS-CP-1`、16 字节 CredentialID 或旧 AAD 作为等价输入。v1 原型尚未发布线上兼容承诺；开发数据默认重建。任何导入必须由明确 MIGRATE 操作产生新 32 字节 ID、v2 Envelope、descriptor 和事件，并保留来源摘要而非字节复用。

## 15. 固定向量与变更门禁

至少固定以下向量：RootCapsule、RecoveryCapsule、每个 KDF Purpose、六类字段 AAD/encryption、OriginBinding、DeviceOperationCredential、OperationEvent、CredentialEnvelope、StateDescriptor、HPKE SecretEnvelope、Merkle 1/2/3/7 叶、ProofBundle 和 Checkpoint。

任一 Protocol/Suite、ID 宽度、枚举数值、Purpose 字符串、CBOR key、KDF 参数解释、AAD 顺序、Merkle prefix 或签名体变化均需新 ADR、版本升级、全部 KAT 重生和 BASELINE 更新。
