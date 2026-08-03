# ADR-019：VPass 命名与 legacy wire 兼容

- 状态：Accepted
- 日期：2026-08-03
- 范围：Spec 2.1.0 / G6 命名修订

## 背景

产品原名使展示定位与内部可验证状态机制过度绑定。部分旧值已进入签名域、KDF/AAD、SQLite 历史数据、OpenAPI 客户端和 Native Messaging 安装。无区分替换会破坏旧凭据和冻结证据。

## 决策

1. VPass 是唯一当前展示名和新的非密码学元数据写入名。
2. 当前 Go module 为 `vpass.local/vpass`，本地命令为 `vpass-local-client`。
3. 冻结的 `ProtocolID`、`SuiteID` 和 `DomainPrefix` 继续使用 legacy wire 字节，并由 `internal/protocol` 统一提供。
4. 当前 API 使用 `/state-resolutions` 和 `X-VPass-*`；服务端对旧路径和头字段保留完整安全校验的 deprecated 读取兼容。
5. SQLite 迁移、历史 baseline 和 `test-results/` 不修改；命名迁移以新基线进行显式修订。
6. legacy 值不得继续用作普通产品展示名。

## 安全影响

决策不改变密钥派生、签名输入、AEAD AAD、Origin 检查、安装令牌、Native Messaging 来源限制和 secret handle 机制。API legacy 入口与当前入口共用鉴权、nonce、会话和校验逻辑。

## 后果

Go import 路径、命令、Native Messaging 当前主机名和文档路径发生显式迁移。旧客户端在迁移窗口内可继续访问冻结 API。未来需要改变 wire 字节时，必须新增协议版本和 ADR。

## 验证

- 新 API 路径和头字段合同测试；
- legacy API 路径和头字段兼容测试；
- 历史 SQLite 迁移和数据库恢复测试；
- 冻结签名域和 KAT 不变性测试；
- 基线摘要验证与旧基线留存检查。
