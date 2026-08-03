# VPass `/api/v2` 设计评审

| 属性 | 值 |
|---|---|
| 合同 | `contracts/openapi.json` v2.1.0 |
| 日期 | 2026-07-31 |
| 结论 | 当前23项均已核对，13 COMPLETE、8 PARTIAL（含1个legacy路径）、2 NOT_IMPLEMENTED |
| 设计评分 | 91/100（Stage 1人工设计评分，不代表实现完成度） |

## 1. 结论

v2 API 已从旧版“审计/暴露/轮换优先”调整为密码管理器日常资源优先：

```text
vault session
  → password generation / route resolution
  → credential create/read/autofill
  → version candidate / site confirmation
  → sync / device / recovery
  → trusted state / audit
  → optional exposure/remediation
```

合同满足 `/api/v2` 版本隔离、资源名词、camelCase、统一错误、cursor 分页、幂等写、版本 CAS、受认证本地通道和可选模块边界。它不把密码、主密码或恢复秘密定义成普通 JSON 字段。机器可读覆盖报告由`scripts/generate_api_coverage.py`生成；当前不能宣称23项全部完成。

## 2. 评分卡

| 维度 | 权重 | 得分 | 说明 |
|---|---:|---:|---|
| 资源与命名一致性 | 15 | 14 | 资源使用复数名词；异步动作建模为 operation |
| HTTP 语义 | 15 | 13 | create 使用 201/202，lock 使用 DELETE；本地 API 的部分流程天然是命令式资源 |
| 版本与兼容 | 10 | 10 | `/api/v2`、info 2.1.0、32 B ID，明确不兼容 v1 |
| 安全与秘密边界 | 20 | 19 | InstallToken + vault session + nonce + secretHandle；需实现层验证 Host/CORS/CSP |
| 幂等与并发 | 15 | 14 | 所有写要求 Idempotency-Key，版本写带 expectedVersion/descriptor hash |
| 错误与可观测性 | 10 | 9 | 稳定 Error；实现需维护完整 error-code registry |
| 分页与资源限制 | 5 | 5 | cursor、limit 上限、proof/object 仍需 server hard limit |
| 研究目标一致性 | 10 | 7 | trusted-state layer results 可观测；证明下载/Monitor 查询可在实现阶段补充只读资源 |
| **合计** | **100** | **91** | 可进入实现 |

## 3. 关键设计决定

### 3.1 主密码不经过普通 HTTP JSON

`POST /vault-sessions` 接收 `masterPasswordHandle`。该 handle 必须由 Native Messaging 或本机 secure-input bridge 创建，绑定扩展安装、设备、短时 nonce 和单次消费；OpenAPI 不提供“上传明文主密码”的资源。

同理，生成密码、用户名、TOTP、RecoverySecret 和事故密码均通过 secret handle 引用。API 响应只返回 handle、期限和字段类型，不返回秘密内容。扩展通过受信本地通道消费 handle，并受到 top-frame Origin 约束。

### 3.2 Autofill 是授权资源

`POST /credentials/{credentialId}/autofill-authorizations` 不等于直接“取密码”。服务必须按以下顺序执行：

1. vault session/nonce/install token；
2. 本地 RouteMap 与当前 Origin；
3. 可信当前descriptor与 L1～L5；
4. Envelope version/hash/policy；
5. 字段解密与 OriginBinding 重验；
6. 创建单次 secret handle。

任一步失败返回 401/403/409/422/503，不返回部分 handle 或明文。

### 3.3 更新和网站确认分离

创建候选使用 `POST /credentials/{id}/versions`，需要 Idempotency-Key、expectedVersion、previousDescriptorHash 和 fieldUpdates。网站/用户证据使用独立 `site-confirmations` 资源，避免调用创建候选就隐含 ACTIVE。

明确失败、MFA、策略拒绝和 UNKNOWN 是正常业务结果，不应全部折叠为 500。CAS 或 descriptor 冲突使用 409；当前版本可通过冲突安全 details 返回，但不能泄露未授权凭据是否存在。

### 3.4 同步存储层不返回可信 current

`sync-publications` 和 `sync-pulls` 是异步 operation。pull 中的存储 cursor 只用于分页；接受对象时仍调用 trusted-state resolution。响应 202 只表示任务已排队，不表示全局同步、日志包含或检查点锚定已经完成。

### 3.5 可选增强隔离

`exposure-analyses` 和 `remediation-campaigns` 位于最后的可选 tag。模块未启用返回 501 与稳定 `OPTIONAL_FEATURE_UNAVAILABLE`，而不是 503 整个密码库不可用。任何日常端点不得内部依赖这些资源。

## 4. 端点审查

| 资源 | 主要权限 | 幂等/CAS | 安全重点 |
|---|---|---|---|
| vault-sessions | 本机安装令牌 + secure input | create 幂等 | 错密码限速；无主密码日志 |
| password-generations | unlocked vault | 幂等 | CSPRNG；只返 secret handle |
| credential-route-resolutions | READ | 只读 | Origin 规范化和本地映射 |
| credentials | CREATE/READ | create 幂等 | 六字段加密，列表不返明文 |
| autofill-authorizations | AUTOFILL | 幂等短时 | 可信状态+对象+Origin 三重门禁 |
| credential versions | UPDATE | expectedVersion + previous hash | 候选先耐久，不直接 ACTIVE |
| site-confirmations | UPDATE | expected/candidate version | 证据等级和 UNKNOWN |
| sync publications/pulls | UPDATE/READ | operation 幂等 | 存储层 current 不可信 |
| device enrollments | DEVICE_ENROLL | challenge 一次性 | 短码、HPKE、scope |
| device revocations | REVOKE | issuance counter | final sequence、新代际 |
| recovery-sessions | RecoverySecret policy | 严格限速 | 只凭主密码不可恢复 |
| vdns-resolutions | 按 operation | 只读/可缓存 | L1～L5 和明确 Verdict |
| audit-events | PUBLISH_AUDIT | 幂等 | encrypted payload |
| security-analyses | AUDIT_ANALYZE | 异步幂等 | scope/ProofBundle/结果最小化 |
| exposure/remediation | AUDIT_ANALYZE/ROTATE/REVOKE | 快照和 attempt | 可选、不可越界 |

## 5. 错误模型

统一结构为：

```json
{
  "code": "ROLLBACK_DETECTED",
  "message": "candidate version is older than the verified current version",
  "requestId": "00000000-0000-0000-0000-000000000000",
  "details": {
    "currentVersion": 2
  }
}
```

`details` 必须按 code 白名单生成。500 不返回 stack、文件路径、SQL、object locator、密码策略秘密、Origin、账号、secret handle 或密码学 key。建议稳定分类：

- 400/422：INVALID_ORIGIN、INVALID_LENGTH、UNKNOWN_ENUM、POLICY_REJECTED；
- 401：INSTALL_TOKEN_INVALID、VAULT_SESSION_EXPIRED、REQUEST_NONCE_INVALID；
- 403：CAPABILITY_DENIED、OUT_OF_SCOPE、ORIGIN_MISMATCH、DEVICE_REVOKED；
- 404：RESOURCE_NOT_FOUND（授权范围内统一）；
- 409：VERSION_CONFLICT、DESCRIPTOR_CONFLICT、IDEMPOTENCY_CONFLICT、LIFECYCLE_CONFLICT、ROLLBACK_DETECTED；
- 429：UNLOCK_RATE_LIMITED、PROOF_RATE_LIMITED；
- 501：OPTIONAL_FEATURE_UNAVAILABLE；
- 503：CURRENT_OBJECT_UNAVAILABLE、PROOF_UNAVAILABLE、CHECKPOINT_UNAVAILABLE。

读取缓存允许降级时仍返回 201 autofill authorization，并在响应 Verdict 中明确 `DEGRADED_*`；不允许降级时返回 503/403。高风险写不能以 2xx + degraded 模糊完成。

## 6. 幂等、并发和异步语义

- 所有状态改变端点要求 16～128 字符 Idempotency-Key；服务只持久化其 key hash；
- 相同 key + 相同 canonical request hash 返回原状态/资源；相同 key + 不同 body 返回 409；
- credential version 写同时要求 expectedVersion 和 previousDescriptorHash；
- device revoke 要求 expectedIssuanceCounter；
- enrollment challenge 一次性原子消费；
- 202 表示本地任务/outbox 已耐久，不表示对象已同步、日志已包含或链已锚定；
- `GET /operations/{id}` 用于查询 QUEUED/RUNNING/COMPLETED/PENDING/FAILED/UNKNOWN；
- Operation result 不得把 Pending/Unknown 映射为 Completed。

## 7. 本地通道安全要求

OpenAPI 描述 loopback 形态，生产实现优先 Native Messaging 或 Unix domain socket。若使用 loopback：

- 仅绑定 127.0.0.1/::1 的明确地址，不绑定所有接口；
- 随机端口和高熵 InstallToken 存入受限文件或 OS key store；
- 校验 Host、Origin、extension ID 和一次性 `X-VPass-Request-Nonce`；服务端对legacy `X-VDNS-Request-Nonce`执行相同校验；
- CORS 使用精确 allowlist，拒绝 `*` 和 null origin；
- 限制 body、数组、proof、对象和批次尺寸；
- unlock/recovery/analysis 分别限速；
- vault session 空闲/绝对超时，OS 锁屏立即删除；
- 请求日志默认不记录 body/header，尤其不记录 Authorization、session、nonce 和 handle。

## 8. 分页和查询

列表使用 opaque cursor，不使用 offset 作为安全顺序。cursor 绑定 query filter、Namespace、caller Device 和过期时间，并经认证保护。limit 默认 50、最大 200；sync batch 最大 10,000。返回顺序需要协议定义：凭据列表按本地显示键和 CredentialID 破平，版本按 version 降序，不能依赖 SQLite 未指定顺序。

## 9. v1 → v2 Breaking Changes

这是有意的 major break：

- base path `/api/v1` → `/api/v2`；
- 历史Protocol `VDNS-CREDENTIAL-AUDIT/1` → legacy wire `VDNS-PM/2`；当前展示标签为`VPass/2`；
- CredentialID 16 B → 32 B；
- API 主资源从 audit/exposure/rotation 转为 vault/credential/autofill/sync；
- 新增 RootCapsule、RouteMap、password generation、site confirmation、recovery 和 trusted-state resolution；
- 旧 CP-1 ciphertext/AAD/枚举不能直接由 v2 API 接受；
- secret 明文输入替换为 secure-input secret handles；
- SCOPE-ZK 改为显式可选 501 边界。

因为 v1 是未发布原型，不提供线上无损兼容承诺。若需要导入，使用离线 MIGRATE 工具而不是在 v2 handler 内兼容两套字节。

## 10. Stage 2实现覆盖与剩余细节

当前机器核对结果为：

| 状态 | 数量 | 说明 |
|---|---:|---|
| COMPLETE | 13 | 本地研究实现、handler和测试标记均存在 |
| PARTIAL | 8 | sync/device/recovery/audit为排队或组合边界；state resolution需注入真实L1～L5 verifier；另含1个deprecated legacy路径 |
| NOT_IMPLEMENTED | 2 | SCOPE-ZK exposure和remediation显式返回501 |

接口存在不等于后端生产能力完成。仍需：

1. 建立完整 error-code registry 并为每个 endpoint 生成合同测试；
2. 选择 Native Messaging/UDS/loopback 的实际部署组合并做威胁测试；
3. 定义 secure-input bridge 与 secret handle 消费协议，确保不会落入普通 HTTP 日志；
4. 为 proof/object/batch 制定按字节硬上限和负载基准；
5. 增加只读 Monitor findings、tree heads/checkpoints 和 proof diagnostics 资源时，先保证不泄露敏感伪名；
6. 用生成客户端/服务 stub 或 schema validator 阻止实现漂移。

本阶段已移除local agent合成的L1～L5成功字符串。未配置完整Verifier时`POST /vdns-resolutions`返回`OPTIONAL_FEATURE_UNAVAILABLE`，不能把内存凭据摘要伪装为经过L1～L5的结果。

## 11. 发布门禁

- OpenAPI 3.1 JSON 可解析且所有 `$ref` 可解析；
- operationId 全局唯一；所有状态写含幂等规则；
- 所有凭据版本写含 expectedVersion；
- 所有列表 cursor 分页且有上限；
- 所有秘密输入都是 local handle/ref，不是 password/recovery 明文 schema；
- 401/403/409/422/429/5xx 使用统一 Error；
- state Verdict 和业务 operation state 不混用；
- SCOPE-ZK 关闭时日常 API 合同测试仍全通过；
- 实现、OpenAPI、Spec、注册表和 UI 枚举一致；
- secret scan、fuzz、race 和端到端 Origin 攻击用例通过。
