# ADR-010：G0.1 协议注册表与持久引用修订

- 状态：Accepted
- 日期：2026-07-21
- 决策者：VDNS 毕业设计技术评审
- 影响：Crypto Profile v1、PolicyHash、SQLite migration 0001、项目 KAT

## 背景

G0 v1.0.0 已要求“枚举使用冻结整数值”，但没有列出数值映射；实现无法在不猜测的情况下产生一致字节。同期交叉评审还发现：

1. 实现初稿错把六种 ID 统一为 32 B，而 FR-001/数据模型已冻结 NamespaceID、DeviceID、CredentialID 为 16 B；
2. SQLite 草案把 16 B DevicePseudonym 写成 32 B；
3. 字段密文 AAD 绑定创建版本，但持久引用没有显式保存原始 `encryption_version`；
4. PolicyHash 没有规范化 schema，存在“已承诺 hash B，实际用策略 A”的脱钩风险；
5. 开发报告已引入 `AUDIT_ANALYZE/ANALYZE_EXPOSURE`，但 SQLite 枚举投影遗漏了两者。

此时尚无对外发布字节、持久用户库或实验原始结果，修订不会破坏已承诺的兼容性。

## 决策

1. 新增 `protocol-registry.md` 作为规范性附件，冻结 ID 宽度、整数枚举、PolicyHash 和 FieldReference。
2. Spec/报告/安全/数据模型文档版本升为 1.0.1，基线升为 `spec-001-v1.0.1-g0.1`。
3. 保持 `protocol_version=1` 和 `VDNS-CP-1`，因为 v1.0.0 从未形成可互操作的线上注册表；v1.0.1 是该协议版本的首个可实现定义。
4. 修正 migration 0001 而不新增 0002，因为 0001 从未对持久数据发布；更新 DDL checksum 并重跑空库/约束测试。
5. 丢弃任何按 G0 未登记字节生成的本地测试数据，不提供启发式迁移。

## 后果

- 跨语言实现可以对同一输入生成完全相同的 CBOR/hash/KDF 字节。
- 凭据 v2 可安全引用凭据 v1 的未变字段，不会错把 v1 AAD 验证为 v2。
- PolicyEncode 必须校验 committed PolicyHash 与编译策略相同。
- 后续任何枚举、Policy schema、FieldReference 或 ID 宽度变更都必须升级协议/套件，不得再以文档澄清方式更改。

