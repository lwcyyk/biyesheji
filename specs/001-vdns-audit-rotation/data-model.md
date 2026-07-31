# VDNS-PM v2 数据模型

| 属性 | 值 |
|---|---|
| 版本 | `2.1.0` |
| 协议 | `VDNS-PM/2` / `VDNS-PM-CP-2` |
| 主存储 | SQLite（本地元数据）+ 内容寻址对象库（密文） |
| 目标 | 支持密码库、生命周期、多设备、VDNS 和可选审计 |

本文定义v2.1逻辑模型和事务不变量。仓库已经存在`0002_v2_initial.sql`～`0007_g6_privacy_response.sql`研究迁移；证据等级、排序回执和冲突终局的v2.1物理迁移尚未实现，不能因为现有表名相似而宣称schema已经兼容。

## 1. 分层与所有权

| 数据层 | 主要数据 | 所有者 | 明文策略 |
|---|---|---|---|
| 解锁层 | VaultProfile、RootCapsule、RecoveryCapsule、session | 本地代理 | 仅活动内存解密 |
| 私有映射层 | RouteMap、账号显示元数据 | 本地代理 | 持久化前加密 |
| 密文对象层 | 字段 ciphertext、wrapped DEK、Envelope、manifest | 本地/不可信云 | 不含字段明文 |
| 控制层 | DeviceCredential、StateDescriptor、OperationEvent、Verdict | 本地/VDNS | 只含伪名和摘要 |
| 透明层 | log leaf、tree head、proof、checkpoint、finding | 日志/Monitor | 最小公开投影 |
| 审计层 | encrypted audit event、analysis、campaign/item | 本地 | 结果最小化 |

## 2. ID 与时间规则

- NamespaceID、DeviceID 固定 16 字节；
- CredentialID、EventID、CampaignID、digest、root 固定 32 字节；
- version、counter、final_sequence、tree_size、Epoch 为非负 uint64；
- 安全排序使用经FinalOrderReceipt证明并满足检查点策略的final_sequence；墙钟只用于显示、KDF/能力有效期和审计窗口；
- SQLite BLOB 必须在 repository 边界验证长度，不能只依赖应用层注释。

## 3. 核心实体关系

```text
VAULT_PROFILE 1──* ROOT_CAPSULE
VAULT_PROFILE 1──* RECOVERY_CAPSULE
VAULT_PROFILE 1──* DEVICE 1──* DEVICE_CREDENTIAL
VAULT_PROFILE 1──* ROUTE_ENTRY *──1 CREDENTIAL
CREDENTIAL 1──* CREDENTIAL_VERSION 1──* VERSION_FIELD
CREDENTIAL 1──* STATE_DESCRIPTOR
DEVICE 1──* OPERATION_EVENT 1──1 OUTBOX_ITEM
SYNC_MANIFEST 1──* SYNC_MANIFEST_OBJECT *──1 CONTENT_OBJECT
LOG 1──* LOG_LEAF 1──* PROOF_CACHE
LOG 1──* TREE_HEAD 1──* CHECKPOINT
AUDIT_EVENT *──1 CREDENTIAL
EXPOSURE_ANALYSIS 1──* REMEDIATION_CAMPAIGN 1──* REMEDIATION_ITEM
```

RootCapsule 与 Credential ciphertext 都可同步，但 RouteMap 的解密和写入只在合法设备本地完成。公开日志不保存 RouteEntry。

## 4. 表字典

### 4.1 解锁与恢复

#### `vault_profiles`

| 列 | 类型 | 约束 |
|---|---|---|
| namespace_id | BLOB(16) | PK、非全零 |
| protocol_version | INTEGER | 固定 2 |
| suite_id | TEXT | `VDNS-PM-CP-2` |
| active_secret_generation | INTEGER | ≥1 |
| root_public_key | BLOB(32) | NOT NULL |
| crypto_policy_hash | BLOB(32) | NOT NULL |
| created_at_ms | INTEGER | 展示时间 |

不得保存主密码、Kpwd、Kunlock 或裸 `Rᵤ/SKroot`。

#### `root_capsules`

| 列 | 类型 | 约束 |
|---|---|---|
| namespace_id/device_id | BLOB(16) | 复合 PK |
| capsule_version | INTEGER | 当前 1 |
| argon_salt | BLOB(16) | NOT NULL |
| argon_memory_kib/iterations/lanes | INTEGER | 按安全策略范围 |
| nonce | BLOB(12) | NOT NULL |
| ciphertext | BLOB | 含 tag |
| bundle_schema_version | INTEGER | NOT NULL |
| object_digest | BLOB(32) | 唯一 |

#### `recovery_capsules`

保存 recovery_id、namespace_id、policy_version、salt、nonce、ciphertext、object_digest、status 和 created_sequence。RecoverySecret 本身不入库。

#### `vault_sessions`

只允许内存 adapter 持有 session_id、device_id、created/idle/expires、Origin allowlist、handle quota 和 sensitive buffer registry。生产 SQLite 不创建此表。

### 4.2 设备、能力和代际

#### `devices`

保存 namespace_id、device_id、auth_public_key、hpke_public_key、status、issued_sequence、suspended_sequence、revoked_sequence、last_counter 和 current_credential_hash。`revoked_sequence` 一旦设置不得清除。

#### `device_credentials`

保存 credential_hash、namespace_id、device_id、public keys、capability_bits、scope_type、scope_digest、valid_from/to_sequence、issuance_counter、status_ref、secret_generation、root_signature 和 canonical_object_digest。

#### `device_scope_items`

当 scope 为集合时保存 credential_hash、item_type 和 item_value。CredentialID 项为 32 字节，OriginBinding 项为 32 字节。集合排序、去重后再计算 scope_digest。

#### `secret_envelopes`

保存 recipient_device_id、secret_generation、HPKE enc/ciphertext、info_hash、object_digest、issued_sequence 和 revoked flag。新代际不得向已撤销设备插入新行。

### 4.3 私有路由与密码策略

#### `route_entries`

| 列 | 类型 | 说明 |
|---|---|---|
| route_id | BLOB(32) | `HMAC(Kname, ExactEncode(origin, account))` 的本地索引派生值 |
| namespace_id | BLOB(16) | FK |
| credential_id | BLOB(32) | FK |
| encrypted_origin | BLOB | 本地 RouteMap AEAD ciphertext |
| encrypted_account_id | BLOB | 本地 RouteMap AEAD ciphertext |
| origin_binding | BLOB(32) | 加密/本地保护投影，不公开 |
| route_version | INTEGER | CAS 版本 |
| status | INTEGER | ACTIVE/REMOVED |

同一 CanonicalOrigin 可对应多账号；唯一约束为 namespace_id + route_id。RouteMap key 来自 Kname 的专用子域，不与字段 DEK wrapping 共用。

#### `password_policies`

保存 policy_hash、origin_binding、policy_version、长度/字符类/禁止字符的加密 policy object digest、source 和 verification_level。生成器以 policy_hash 绑定结果，不保存生成密码。

### 4.4 内容寻址对象

#### `content_objects`

| 列 | 类型 | 约束 |
|---|---|---|
| object_digest | BLOB(32) | PK，SHA-256(canonical bytes) |
| object_type | INTEGER | 注册枚举 |
| byte_length | INTEGER | 上限校验 |
| storage_state | INTEGER | LOCAL_ONLY/SYNC_PENDING/SYNCED/MISSING |
| local_locator | TEXT | 受限项目数据目录 |
| created_sequence | INTEGER | 逻辑顺序 |

对象写采用 temporary file、fsync、atomic rename，再提交引用事务。路径由 digest 编码生成，禁止调用方提供任意路径。

### 4.5 凭据、版本和字段

#### `credentials`

保存 namespace_id + credential_id(32) 复合 PK、aggregate_status、local_version、accepted_version、accepted_descriptor_hash、accepted_envelope_hash、origin_binding、latest_event_hash、updated_sequence。accepted 指针只能由生命周期服务在验证通过后写入。

#### `credential_versions`

保存 credential_id、version、internal_status、envelope_digest、descriptor_hash、previous_descriptor_hash、expected_base_version、site_evidence_level、site_receipt_digest、created_by_device、created_event_id、created_sequence 和 error_code。

唯一约束：`(namespace_id, credential_id, version, descriptor_hash)`；另有部分唯一语义保证同一版本最多一个 accepted descriptor。出现另一个 descriptor 时保存为冲突证据，不覆盖 accepted 指针。

#### `credential_version_fields`

保存 credential_id、version、field_type、encryption_version、ciphertext_digest、wrapped_key_digest、field_commitment、crypto_policy_hash 和 origin_binding。主键为 credential_id + version + field_type。

密码的 field_commitment 不得是裸 SHA-256(password)。可使用带 key 隐藏承诺或空值，具体由策略登记。

#### `state_descriptors`

保存 descriptor_hash、credential_id、active_version、active_envelope_hash、previous_descriptor_hash、lifecycle_status、last_event_id、authorized_device_set_root、audit_checkpoint、final_sequence、updater_device_id、signature 和 proof_state。

### 4.6 事件、事务和 outbox

#### `operation_events`

保存 event_id、namespace_id、operation_type、device_id、credential_id、old/new_version、payload_hash、device_counter、previous_event_hash、capability_hash、secret_generation、signature、publication_state 和 final_sequence。

唯一约束：`(namespace_id, device_id, device_counter)` 和 event_id。counter 冲突必须在同一事务中拒绝。

#### `outbox_items`

保存 outbox_id、event_id、object_digest、destination、state、attempt_count、next_attempt_at、last_error_code 和 lease。payload 引用 content object，不复制秘密。处理器至少一次投递，接收端以 event_id/object_digest 幂等。

#### `idempotency_records`

保存 namespace/device、idempotency_key_hash、request_body_hash、status、result_reference 和 expires_at。相同 key 异 body 在事务外也必须返回冲突而不是复用结果。

### 4.7 同步

#### `sync_manifests`

保存 manifest_digest、namespace_id、device_id、base_checkpoint、target_checkpoint、highest_device_counter、object_set_root、signature、created_sequence 和 sync_state。

#### `sync_manifest_objects`

保存 manifest_digest、object_digest、object_type、credential_id、version 和 ordinal。ordinal/对象集合按规范字节排序，防止不同设备形成不同 root。

#### `sync_peers`

本地保存 peer/device、last_accepted_checkpoint、last_manifest_digest、last_pull_cursor 和 error_state。云端 cursor 只用于分页，不作为可信顺序。

#### `credential_conflicts_v2`

保存credential_id、base_descriptor_hash、candidate_descriptor_hash、candidate_version、device_id、local_counter、provisional_sequence、final_order_receipt_hash和status。同一base出现不同候选时全部保留并把凭据聚合置为CONFLICTED。冲突裁决记录必须引用完整候选集合和选中摘要。

### 4.8 VDNS、日志和 Monitor

#### `verdicts`

保存 resolution_id、credential_id、operation、candidate_descriptor_hash、trusted_checkpoint_hash、L1～L5 result codes、final_verdict、policy_hash、evaluated_sequence 和 expires_at。不得缓存字段明文。

#### `logs`、`log_leaves`、`tree_heads`

- logs：log_id、public_key、suite、status；
- log_leaves：log_id、leaf_index、leaf_hash、public_leaf_object_digest；
- tree_heads：log_id、tree_size、root_hash、final_sequence、signature、provider_kind。

同 log_id + tree_size 若出现两个 root，均保留并生成 finding，不能依唯一约束丢掉第二份证据。

#### `final_order_receipts_v2`（第二阶段新增）

SQLite v8新增：

- `final_order_snapshots_v2`：带revision CAS的研究Authority完整恢复快照；
- `final_order_candidates_v2`：base/candidate版本、base/候选descriptor摘要、设备、幂等键、disposition和排序引用；
- `final_order_receipts_v2`：namespace、credential、ordered object、单调序、前序、Authority key和签名；
- `final_order_checkpoints_v2`：单节点恢复检查点、状态根和最后回执；
- `final_order_resolutions_v2`：完整冲突集合承诺、用户选择、依据、新版本和排序回执。

当前研究Authority使用进程级全局单调`final_sequence`，数据库因此对`final_sequence`设置全局唯一约束。若同一位置出现不同摘要，不能覆盖现有行，Monitor需将两份签名对象另存为分叉证据并停止高风险写。生产多节点排序仍未实现。

`log_leaves.final_sequence`不得由普通调用方直接声明。日志append只接受已验证FinalOrderReceipt；检查点前标记`PROVISIONAL_ORDERED`，达到策略要求后标记`FINALIZED`。

#### `site_confirmation_evidence_v21`

保存`change_id`、Namespace/Credential、候选版本、固定`evidence_schema=2`、E0～E5、`trust_kind`、决策状态和可选回执摘要。旧表中的1～5值没有v2.1行时拒绝读取，禁止原地重解释。`MOCK_SITE_E4`只能进入`REVIEW_REQUIRED`。

#### `device_revocation_layers_v2`

分别保存控制面撤销、秘密代际隔离和外部凭据修复状态，并承诺`KnownCredentialSet`、`FutureAccessBlockedSet`和`RemediationRequiredSet`。修复状态只允许`COMPLETED/PENDING/FAILED/UNKNOWN`；只有`COMPLETED`可从待修复集合移除。控制面完成必须带最终序，秘密隔离完成必须带新代际。

#### `proof_cache`

保存 subject_hash、tree_head_hash、inclusion_object_digest、consistency_object_digest、verified_at、expires_at 和 verifier_version。坏 proof 不进入正缓存。

#### `checkpoints`

保存 checkpoint_hash、namespace/device/credential/audit/revocation roots、crypto_policy_hash、height、final_sequence、provider_kind、optional_vrf_hash、signature 和 anchor_receipt_digest。

#### `monitor_findings`

保存 finding_id、type、severity、first/last_seen、evidence_object_digests、status 和 public_summary。summary 禁止出现 Origin、账号、密码或完整 scope。

### 4.9 审计与可选事故响应

#### `audit_events`

保存event_id、credential_id、device_id、epoch、encrypted_payload_digest、evidence_schema_version、evidence_level(E0～E5)、observed_time_bucket、publication_state和final_sequence。隐藏密码见证只存在于encrypted payload。旧数值1～5必须带legacy schema version，不能按v2.1语义读取。

#### `security_analyses`

保存 analysis_id、requested_by_device、window_start/end_bucket、policy_hash、source_checkpoint、result_object_digest、risk_counts 和 created_sequence。结果对象保存凭据伪名和证明引用，不保存输入密码/secret handle。

#### `exposure_analyses`

可选表，保存 snapshot_root、incident_commitment、affected_root、proof_system、proof_digest、status 和统计。禁用 SCOPE-ZK 时不创建伪成功记录。

#### `remediation_campaigns` / `remediation_items`

Campaign 保存 campaign_id、affected_root、policy/cost model、status 和 rotation_root。Item 保存 action、credential_id、old/new_version、attempt、precondition_hash、status、receipt_digest、error_code。Completed、Pending、Failed、Unknown 分开；只有 Completed 可进入 ChangedSet。

## 5. 状态机与约束

### 5.1 Vault session

```text
LOCKED --correct password + local device secret--> UNLOCKED
UNLOCKED --lock/idle/OS lock/exit--> LOCKED
```

错误解锁不创建 session；跨设备复制 RootCapsule 不得成功。

### 5.2 Credential aggregate

```text
NONEXISTENT → CREATE_PENDING → ACTIVE
ACTIVE → UPDATE_PENDING → SITE_CONFIRM_PENDING → ACTIVE
ACTIVE → SUSPENDED → REVOKED
ACTIVE/UPDATE_PENDING → CONFLICTED
```

SUPERSEDED 是历史版本状态，不应删除字段对象；垃圾回收必须先证明没有版本、备份、事件或证明引用。

### 5.3 Version crash recovery

```text
CANDIDATE_LOCAL
 → SITE_CHANGE_IN_PROGRESS
 → SITE_CHANGED_LOCAL_COMMIT_PENDING
 → SITE_CONFIRM_PENDING
 → ACTIVE
```

明确失败可进入 FAILED；模糊回执进入 UNKNOWN；用户取消且网站未改变时进入 ABORTED。UNKNOWN 不能直接变 ACTIVE，需新增确认证据。

### 5.4 Device

```text
PENDING_ENROLL → ACTIVE → SUSPENDED → REVOKED
```

REVOKED 为终态；恢复设备使用新 DeviceID 和新 credential，不复活旧行。

## 6. 关键事务

### 6.1 初始化

1. 在内存生成独立根、设备 key 和恢复秘密；
2. 构造 Root/Recovery capsule 和首个 DeviceCredential；
3. 原子写 vault profile、capsule、device、credential 和初始 outbox；
4. fsync 后才向用户展示 RecoverySecret；
5. 任一步失败清理活动秘密并不留下可误解初始化状态。

### 6.2 创建凭据

1. 规范 Origin、生成 CredentialID/密码/字段 DEK；
2. 先原子写所有内容对象；
3. SQLite 事务插入 route、credential、v1 fields、candidate descriptor、CREATE event 和 outbox；
4. VDNS 接受后以 CAS 更新 accepted 指针；
5. 失败保留可恢复 outbox 或明确 CREATE_PENDING，不删除仍被引用对象。

### 6.3 自动填充只读事务

1. 解锁会话和 Origin 校验；
2. RouteMap 定位 CredentialID；
3. 读取 trusted checkpoint 和 VDNS descriptor，验证 L1～L5；
4. 取对象并核对 digest/version/policy；
5. 解密密码并再次核对 OriginBinding；
6. 创建内存 secret handle；
7. 独立小事务写 encrypted USE_OBSERVED/outbox。

审计 outbox 失败不能泄露密码，也不能把未验证版本变成可填充；本地耐久失败需在 UI 明确降级。

### 6.4 修改密码

1. 在事务中写 v+1 候选和状态；
2. 确认本地 ciphertext/object fsync 后调用网站；
3. 根据回执原子写证据和内部状态；
4. 成功时发布 descriptor/event，VDNS 接受后 CAS active pointer；
5. 崩溃恢复根据内部状态重试发布或查询网站，不重新生成密码。

### 6.5 同步接受

sync manifest只描述候选对象。接收端验证VDNS current descriptor、对象齐全、hash、version、previous descriptor、counter、FinalOrderReceipt和local policy，再在本地事务中更新accepted pointer/peer checkpoint。若同一base出现不同候选，先写入冲突集合并进入CONFLICTED，不自动更新accepted。云cursor、object mtime、到达时间不参与信任决定。

### 6.6 撤销与新代际

先发布并以FinalOrderReceipt/检查点最终化控制面撤销，再独立生成g+1，仅给非撤销设备创建secret envelope，最后切换profile active generation。外部网站密码、TOTP、恢复码、会话和token使用独立remediation items跟踪。任一步中断都保留可恢复阶段；不得在控制面最终化前称权限已撤销，不得把代际切换称为收回旧密码。

### 6.7 新设备可信检查点

设备记录bootstrap_checkpoint_digest、source_kind（EXISTING_DEVICE、RECOVERY_COMMITMENT、OUT_OF_BAND）和source_evidence_digest。普通云端返回或无提示TOFU不能创建可用于高风险写的初始信任。

## 7. 索引与规模

| 查询 | 索引 |
|---|---|
| Origin/账号路由 | route_entries(namespace_id, route_id, status) |
| 当前凭据 | credentials(namespace_id, credential_id) |
| 版本历史 | credential_versions(credential_id, version DESC) |
| 设备 counter | operation_events(namespace_id, device_id, device_counter) UNIQUE |
| outbox 拉取 | outbox_items(state, next_attempt_at, outbox_id) |
| 同步缺失对象 | content_objects(storage_state, object_digest) |
| 审计窗口 | audit_events(epoch, observed_time_bucket, event_id) |
| tree head | tree_heads(log_id, tree_size)；允许冲突根证据 |
| findings | monitor_findings(status, severity, last_seen) |

10k/100k 凭据和 100k/1m 日志叶实验必须用同一逻辑 schema；不得用与生产查询无关的内存 map 代替数据库基准。

## 8. 保留、备份与垃圾回收

- Root/Recovery capsule、RouteMap、accepted descriptor、版本历史和可信检查点进入加密备份；
- secret handle、Kpwd、Kunlock、活动 DEK 不进入备份；
- 操作事件和证明按论文实验窗口保留；生产策略可压缩但不得破坏一致性证明；
- 对象 GC 前计算所有版本、manifest、outbox、proof、backup 和 remediation 引用；
- 撤销设备相关历史对象不因撤销自动删除；
- 删除测试数据只针对已解析并校验的项目专用目录，禁止宽泛路径或未解析变量。

## 9. v1 到 v2

v1 `0001_initial.sql` 的 16 字节 CredentialID、旧枚举和 CP-1 ciphertext 不符合本模型。G1.1 必须选择并记录以下实现之一：

1. 对未发布开发数据执行安全、可复现的 v2 重建；或
2. 新增离线 v1 reader，将解密后的逻辑字段重新生成 32 字节 ID、OriginBinding、v2 ciphertext、descriptor 和 MIGRATE event。

不得通过 ALTER 宽度后沿用旧签名/AAD，也不得让同一 repository 同时把 16/32 字节 ID 当成 v2。migration 完成后，v2 repository 边界对错误宽度立即返回 INVALID_LENGTH。

## 10. 数据模型验收

- 错误密码、错误 DeviceSecret 和复制胶囊不能产生 vault session；
- 同一 Origin 多账号能精确路由，跨 Origin 失败；
- 同一本地数据库的Credential/version最多一个accepted descriptor；跨设备双候选进入CONFLICTED；
- 本地CAS失败不产生部分outbox或accepted pointer；
- final_sequence均能追溯到排序回执，检查点前不会标记final；
- 网站成功后每个崩溃点都能恢复新密码；
- 云回滚和 hash 替换不改变 accepted pointer；
- 撤销后新代际没有被撤销设备的 secret envelope；
- 同 tree size 异根两份证据均保留；
- 只改密码时其他五类字段引用逐字节不变；
- 数据库、对象元数据、错误、公开叶和备份扫描不出现被禁止明文。
