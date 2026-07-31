# VDNS 架构决策记录

本目录是 Spec 001 v2.1.0 的协议决策基线。当前实现阶段为 G6，G7 冻结尚未达成。编号一经发布不复用；决策变化必须新增 ADR，并在旧记录中标记 `Superseded by ADR-xxx`，不得静默改写协议字节或安全结论。ADR-011 将产品主线重定向为完整密码生命周期管理；ADR-012～017 冻结第一阶段审计发现的信任、排序、确认、撤销、Origin 和证据边界；ADR-018补正第二阶段研究型最终序回执线格式。

| ADR | 主题 | 状态 |
|---|---|---|
| [ADR-001](ADR-001-modular-monolith.md) | 模块化单体与独立 Monitor | Accepted |
| [ADR-002](ADR-002-root-and-namespace-secrets.md) | 根签名与名称空间秘密分离 | Accepted |
| [ADR-003](ADR-003-deterministic-cbor.md) | 确定性 CBOR | Accepted |
| [ADR-004](ADR-004-final-ordering.md) | 最终检查点决定安全顺序 | Accepted |
| [ADR-005](ADR-005-split-state-machines.md) | 五状态机分离 | Accepted |
| [ADR-006](ADR-006-affected-root-claim.md) | AffectedRoot 的证明边界 | Accepted |
| [ADR-007](ADR-007-anvil-research-adapter.md) | Anvil 研究适配器 | Accepted |
| [ADR-008](ADR-008-rfc9381-provider.md) | RFC 9381 Provider 与显式模拟器 | Accepted with Gate |
| [ADR-009](ADR-009-simulator-first.md) | Event Simulator/Mock Site 优先 | Accepted |
| [ADR-010](ADR-010-g0-1-protocol-registry-amendment.md) | G0.1 协议注册表与持久引用修订 | Accepted |
| [ADR-011](ADR-011-vdns-pm-product-rebaseline.md) | VDNS-PM 产品主线与协议 v2 重基线 | Accepted |
| [ADR-012](ADR-012-vdns-deployment-trust-model.md) | VDNS 部署与信任模型 | Accepted |
| [ADR-013](ADR-013-cross-device-conflict-final-order.md) | 跨设备冲突与最终顺序 | Accepted |
| [ADR-014](ADR-014-site-confirmation-evidence-levels.md) | 网站确认证据等级 | Accepted |
| [ADR-015](ADR-015-device-revocation-boundary.md) | 设备撤销边界 | Accepted |
| [ADR-016](ADR-016-canonical-origin.md) | CanonicalOrigin 规则 | Accepted |
| [ADR-017](ADR-017-experiment-claims-evidence.md) | 实验声明与证据要求 | Accepted |
| [ADR-018](ADR-018-stage2-research-final-order-wire.md) | 第二阶段研究型最终序回执线格式 | Accepted |
