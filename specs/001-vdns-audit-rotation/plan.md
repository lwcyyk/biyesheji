# VDNS-PM v2 实施计划

| 属性 | 值 |
|---|---|
| 版本 | `2.1.0` |
| 阶段 | G6研究原型集成；Stage 1协议设计冻结；G7未达成 |
| 产品主线 | 解锁 → 生成/保存 → VDNS 解析 → 填充 → 同步 → 更新/确认/撤销 |
| 架构 | Go 模块化单体 + 端口/适配器 + 独立 Monitor |
| 协议 | `VDNS-PM/2` / `VDNS-PM-CP-2` |
| 规范依据 | `spec.md`、ADR-011～017、开发报告 v2.1.0 |

> 本文件的G0.2～G7章节保留原阶段路线，用于比较计划与实际。当前执行入口已经切换到`tasks.md`的P0～P3清单；历史阶段标题不表示相应任务已经完成。

## 1. 计划原则

1. 日常密码管理先于审计增强：先交付解锁、创建、填充、同步、更新和恢复，再接 SCOPE-ZK。
2. 本地代理是唯一明文边界；浏览器扩展只取得短期 secret handle，不持久化密码。
3. 云端保存对象，VDNS 决定可验证当前状态；链和 VRF 不进入普通填充关键路径。
4. 所有安全决定进入领域状态机和验证器，HTTP、SQL、扩展与链适配器不得自行推进状态。
5. v1.0.1 代码作为迁移资产；v2 协议字节、ID 宽度和 API 不做静默兼容。
6. 每个阶段同时交付正向功能、负向路径、自动化证据和对应文档。

## 2. 目标架构与模块边界

```text
apps/browser-extension ─┐
apps/desktop-client     ├─ local authenticated API ─ apps/local-agent
apps/security-dashboard ┘                             │
                                                       ▼
packages/vault + crypto + route + lifecycle + verifier
           │                 │                  │
           ▼                 ▼                  ▼
 object-store adapter   sync adapter       VDNS/log adapters
           │                 │                  │
           ▼                 ▼                  ▼
       local disk      untrusted cloud     log/anchor/monitor
```

领域包分为：

| 包 | 职责 | 禁止依赖 |
|---|---|---|
| `crypto-core` | KDF、AEAD、HKDF、签名、HPKE、清零 | HTTP、SQL、浏览器 |
| `credential-vault` | 胶囊、会话、字段、Envelope、RouteMap | 云状态裁决 |
| `password-generator` | 无偏随机和版本化策略 | 普通 PRNG |
| `lifecycle-state-machine` | 创建、更新、确认、撤销、冲突 | adapter 自定义状态 |
| `device-capability` | 设备凭证、scope、撤销和代际 | 墙钟安全排序 |
| `sync-protocol` | manifest、pull/publish、CAS、恢复 | 解密根 |
| `vdns-verifier` | L1～L5、Verdict、ProofBundle | 直接信任云返回 |
| `audit-event` | Epoch 见证和本地安全检查 | 公开稳定 ReuseTag |
| `scope-zk` | 可选影响集合证明 | 日常查询/填充调用 |

数据库、对象库、云、日志、锚定、VRF、网站 Connector 都通过端口接入。首版不拆成网络微服务，避免为了部署形态引入分布式事务。

## 3. 阶段与交付

### G0.2：产品与规范重基线

目标：将项目从审计/轮换导向原型重定为完整密码生命周期管理器。

交付：

- v2 开发报告、Spec、计划、安全模型、数据模型和研究方案；
- `VDNS-PM/2` 注册表、`/api/v2` OpenAPI 和 API 评审；
- ADR-011、v1 历史清单、v2 冻结清单；
- 43 FR、30 NFR、21 AC、97 任务追踪通过。

退出条件：基线与追踪脚本通过，无未决占位符，所有相关文档一致将 SCOPE-ZK 标为可选。

### G1.1：v2 密码学与协议迁移

目标：复用已验证的 v1 原语，实现 v2 线格式和本地解锁底座。

交付：

- Protocol/Suite 域分离、32 字节 CredentialID 和 v2 固定向量；
- Argon2id 参数校准、RootCapsule、RecoveryCapsule 和会话锁定；
- `Kwrap/Kname/Kaudit/Krelation/Krotation` 域分离；
- Origin 字段、OriginBinding 和六字段 AAD；
- DeviceOperationCredential v2 和能力注册表；
- v1 测试数据显式重建工具或受限导入器。

退出条件：KAT、篡改、跨域重放、错误设备、错误密码、secret scan、race 和 fuzz 全通过。

### G2：日常密码库核心

目标：完成单设备的生成、保存、查询和填充前授权主闭环。

交付：

- 本地加密 RouteMap，支持同 Origin 多账号和规范化；
- 密码生成器和站点策略引擎；
- CredentialEnvelope/StateDescriptor、字段级最小更新；
- 内容寻址对象库、SQLite 事务、CAS 和 outbox v2；
- `/api/v2` vault session、password generation、credential 和 autofill resources；
- 锁定、崩溃恢复和 10k/100k 查询基准。

退出条件：AC-001～003、AC-011～015 的适用部分通过，错误 Origin/对象/版本不返回部分明文。

### G3：生命周期、多设备与恢复

目标：让多个设备在不可信同步服务上独立接受当前版本。

交付：

- CREATE、UPDATE、SITE_CONFIRM、SUSPEND、REVOKE 状态机；
- 网站 Connector 回执、UNKNOWN 和 `SITE_CHANGED_LOCAL_COMMIT_PENDING` 恢复；
- sync manifest、pull/publish、对象补齐、幂等重试和冲突证据；
- HPKE 加入通道、DEVICE_ENROLL、设备撤销和新 `Rᵤ` 代际；
- RecoverySecret 恢复和 RouteMap/检查点恢复一致性。

退出条件：双设备及多设备同步、回滚、替换、并发、撤销、每个崩溃点和恢复演练通过。

### G4：VDNS、透明日志与检查点

目标：把云端版本选择替换为设备本地可验证解析。

交付：

- L1 主体、L2 能力、L3 动态状态、L4 日志、L5 本地策略验证；
- ProofBundle、RFC 9162 风格包含/一致性证明和签名树头；
- ACCEPT/DEGRADED/REVIEW_REQUIRED/REJECT Verdict；
- 周期 Namespace/Device/Credential/Audit/Revocation roots；
- Monitor 双视图、回滚、同版本双 descriptor 和锚定冲突检测；
- 模拟公告层与 Anvil 研究适配器，清楚标记非生产性质。

退出条件：破坏每层证据均得到预期拒绝/降级，合法追加无分叉误报，日常缓存命中填充不等待锚定。

### G5：用户交互与日常场景

目标：用浏览器扩展和本地控制台呈现真实密码管理体验。

交付：

- Manifest V3 扩展、Native Messaging/受认证回环通信；
- Origin/iframe/top-frame 校验、账号选择、生成和填充；
- Mock Site 注册、登录、改密、策略拒绝、MFA、超时和查询回执；
- 密码库列表、版本历史、设备和冲突处理 UI；
- 单命令演示：初始化、创建、填充、双设备同步、改密和撤销。

退出条件：AC-002、AC-005、AC-015～016、AC-020 在空数据目录可复现，扩展存储与日志无秘密。

### G6：隐私审计与可选响应

目标：在已完成的密码生命周期上增加安全检查和事故处理能力。

交付：

- Epoch 审计密钥、加密使用事件、耐久异步发布；
- 重复、异常设备、长期未更新、回滚和冲突分析；
- 公开投影和跨 Epoch 不可链接实验；
- 可插拔 SCOPE-ZK、AffectedRoot、修复规划和 RecoverySafetyGuard；
- Completed/Pending/Failed/Unknown、RotationRoot 和越界修改拒绝；
- 未启用可选模块时稳定错误且主功能不受影响。

退出条件：E7 满足预设真值，E8 证明/基线数据完整，失败修复不改变无关字段。

### G7：集成、实验、论文与发布

目标：完成端到端证据链和研究生毕业设计材料。

交付：

- E1～E8 固定数据、运行器、JSON/CSV schema 和可视化；
- 10k/100k 凭据、100k/1m 日志叶、多设备和故障注入；
- `go test`、`vet`、race、fuzz、OpenAPI、SBOM、依赖/许可证/秘密扫描；
- 安全论证、性能对比、残余风险、论文八章、答辩演示和运行手册。

退出条件：AC-001～021 均有证据；所有失败结果保留；界面和论文不夸大链、VRF、撤销或零知识能力。

## 4. 关键依赖顺序

```text
G0.2
  → G1.1 protocol/crypto
  → G2 vault ─────────────┐
  → G3 lifecycle/sync ────┼→ G5 UX
  → G4 VDNS/log ──────────┘
             ↓
            G6 audit/optional remediation
             ↓
            G7 experiments/thesis
```

G4 可在 G2 后与 G3 后半段并行，但其 current-version 接口必须先固定。G6 不得反向要求修改日常填充关键路径。

## 5. 数据迁移策略

v1.0.1 是未发布原型。默认开发迁移采用：导出明确标记的测试 fixture、删除专用测试数据库、以 v2 schema 重建、重新生成 KAT 和演示数据。禁止删除非项目路径或用户真实数据。

若后续需要 v1 导入，则使用独立离线导入器：验证 v1 suite 和 16 字节 ID，解密后生成新的 32 字节 CredentialID、OriginBinding、v2 Envelope 和 CREATE/MIGRATE 事件；旧字节不能直接进入 v2 验证器。

## 6. 测试策略

| 层 | 测试 | 代表性故障 |
|---|---|---|
| 密码学 | KAT、属性、fuzz、篡改 | nonce/AAD/tag、跨 Namespace/Field 重放 |
| 状态机 | 表驱动/模型测试 | 非法边、双激活、确认前覆盖 |
| 持久化 | 事务与崩溃注入 | CAS 双写、outbox 丢失、半写对象 |
| 同步 | 多设备集成 | 云回滚、删除、替换、重排、冲突 |
| VDNS | 证明变异 | 坏签名、scope、撤销、counter、Merkle 路径 |
| 扩展 | E2E | iframe、IDN、默认端口、错误账号、会话过期 |
| 安全 | secret/dependency/SBOM | 日志泄密、错误堆栈、供应链漏洞 |
| 实验 | 固定场景重复 | 抖动、规模、故障恢复、结果可复现 |

## 7. 性能预算

- Argon2id 解锁 P95 不高于 1.5 s；
- 10k RouteMap 查询 P95 不高于 5 ms；
- 单凭据字段解密 P95 不高于 10 ms；
- 本地缓存命中填充 P95 不高于 100 ms；
- 100k 叶单对象 L1～L5 P95 不高于 25 ms；
- 1m 叶包含证明不超过 32 个哈希加固定元数据；
- 100k 审计事件扫描不高于 5 s；
- 只改密码时无关字段重加密字节为 0。

基准记录机器与软件环境、预热、重复次数和原始分位数。若硬件不足导致目标不合理，通过 ADR 调整，不隐藏未达标结果。

## 8. 风险与处理

| 风险 | 影响 | 处理 |
|---|---|---|
| v1/v2 语义混用 | 证明和数据不可解释 | 协议版本硬拒绝、独立 KAT、显式迁移 |
| 浏览器页面误导 | 跨站填充或虚假确认 | 本地重验 Origin、top-frame 门禁、证据分级 |
| 网站改密结果未知 | 用户被锁号 | 新密码先耐久、UNKNOWN/Review、Connector 查询 |
| 云回滚/删除 | 旧密码或不可用 | VDNS current version、对象缓存、明确缺失错误 |
| 撤销设备保留旧秘密 | 历史机密残余 | 新代际、停止封装、论文明确边界 |
| 日志/链泄露关系 | 隐私损失 | 随机伪名、粗粒度元数据、Epoch 隔离、最小锚定 |
| SCOPE-ZK 工期过大 | 挤压日常主线 | P2 可插拔、稳定 unavailable、最后实施 |
| 模拟器结论夸大 | 学术有效性下降 | Provider 标签和残余风险强制展示 |

## 9. 完成定义

任务完成需同时满足代码、负向测试、需求/验收映射、安全扫描、接口与数据文档同步、机器证据和审查。单元测试通过不等于阶段完成；没有 current-version 证明的云同步、没有网站确认的改密、没有设备绑定的胶囊和没有 Origin 重验的填充均不能进入完成状态。
