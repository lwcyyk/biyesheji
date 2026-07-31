# ADR-011：VDNS-PM 产品主线与协议 v2 重基线

| 属性 | 值 |
|---|---|
| 状态 | Accepted |
| 日期 | 2026-07-22 |
| 决策范围 | 产品定位、论文问题、协议命名、日常主路径、泄露响应边界 |
| 取代 | v1.0.1 中“暴露分析与最小影响轮换为主闭环”的产品优先级；不否定 ADR-001～010 的通用安全结论 |

## 背景

v1.0.1 已实现确定性 CBOR、Ed25519、密钥域分离、字段级信封加密、HPKE、不可变事件、内容寻址对象和凭据 CAS。这些机制是完整密码管理器的安全基础，但原规格把暴露窗口、AffectedRoot、VRF 和批量轮换放在目标定义的中心，使系统被误解为泄露响应工具。

项目的真实目标是：用户只记一个主密码，由本地可信代理完成复杂密码生成、加密保存、查询、自动填充、多设备同步、更新、撤销、备份与恢复；VDNS 验证控制过程，隐私审计和 SCOPE-ZK 只作为增强能力。

## 决策

1. 项目正式命名为 **VDNS-PM: Verifiable Password Lifecycle Management over VDNS**；推荐论文题目为《基于VDNS的可验证密码生命周期管理与隐私审计方法研究》。
2. 系统的第一主路径固定为：`解锁 → 路由解析 → VDNS 状态解析 → 密文获取 → 本地解密 → Origin 复核 → 自动填充 → 异步审计`。
3. 研究贡献优先级固定为：可验证生命周期解析、多设备可信同步、名称空间授权操作主体、网站确认绑定；隐私审计为辅助创新，SCOPE-ZK/批量修复为可选增强。
4. 保留模块化单体、六边形边界、独立 Monitor、字段级加密、最终撤销序、透明日志和最小链上锚定；普通登录、查询和填充不等待链、VRF 或 SCOPE-ZK。
5. 根签名密钥 `SKroot` 与高熵名称空间秘密 `Rᵤ[g]` 继续独立生成。它们可以共同装入本地 `RootSecretBundle`，但不得互相派生或跨用途使用。
6. 主密码只参与 Argon2id 本地解锁；设备高熵秘密与主密码共同保护每设备 RootCapsule。主密码、设备秘密和解锁密钥不得发送到同步服务。
7. 为满足“不公开 Origin”与“防跨站替换”两个目标，字段 AAD 绑定 `OriginBinding = HMAC(Kname, Encode(CanonicalOrigin, AccountID))`，不得把明文 CanonicalOrigin 放入云端可见 AAD。
8. `CredentialID` 在协议 v2 中提升为 32 字节；新增 Origin 字段、解锁胶囊、路由映射、同步对象、恢复对象、能力和状态投影。由于线上字段、枚举和 AAD 变化，协议升级为 `VDNS-PM/2`、套件升级为 `VDNS-PM-CP-2`。
9. v1 数据和代码仅视为预发布研究原型。不得把 16 字节 CredentialID 或 CP-1 对象静默解释为 v2；测试数据重建，迁移工具必须显式识别并拒绝歧义输入。
10. 旧目录名 `specs/001-vdns-audit-rotation` 暂时保留，以避免破坏现有脚本和历史基线；目录名不再表示产品定位。

## 后果

- G1/G2 已完成实现仍提供可复用代码，但 ID 宽度、FieldType、KDF/AAD、状态和 API 必须经过 v2 适配任务后才能宣称符合新规格。
- 开发报告、Spec、计划、安全规范、协议注册表、数据模型、OpenAPI、任务和实验体系必须在同一 G0.2 基线更新。
- 日常密码管理性能成为首要实验；泄露证明不再作为首版日常可用性的门禁。
- SCOPE-ZK 可以因时间或依赖风险延期，不影响密码管理主闭环验收，但相关接口和结论必须明确标记 `OPTIONAL/EXPERIMENTAL`。

## 不变量

```text
AEAD protects credential contents.
VDNS validates credential control transitions.

AcceptedTransition =>
  IdentityValid && AuthorizationValid && NotRevoked &&
  CausallyFresh && LogIncluded && PolicyAccepted
```

任何后续实现不得以“改成密码管理器”为由降低确定性编码、密钥分离、撤销顺序、CAS、透明证明或 fail-closed 要求。
