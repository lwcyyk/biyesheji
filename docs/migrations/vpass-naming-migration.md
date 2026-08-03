# VPass 命名迁移与兼容说明

## 1. 修改原因

原名容易让读者把系统理解为 DNS 或区块链项目，也容易把可验证状态控制层误解为传统 DNS。命名迁移将产品定位聚焦在可验证的密码生命周期管理，不改变 Spec 2.1.0 已冻结的密码学和安全语义。

## 2. 正式名称

- 产品简称：VPass
- 中文全称：可验证密码生命周期管理系统
- 英文全称：Verifiable Password Lifecycle Management System
- 应用场景：多设备和不可信同步存储环境

## 3. 产品名映射

| 旧名 | 新名 | 处理 |
|---|---|---|
| VDNS-PM | VPass | 仅在历史记录和 legacy 机器值中保留旧名 |
| Verifiable Password Lifecycle Management over VDNS | Verifiable Password Lifecycle Management System | 当前英文全称 |

## 4. 中文组件名映射

| 旧名 | 新名 |
|---|---|
| VDNS控制层 | 可验证状态控制层 |
| VDNS可信解析 | 可信状态解析 |
| VDNS状态发布 | 凭据状态发布 |
| VDNS五层验证 | 五层可信状态验证 |
| VDNS身份发布与解析模块 | 可信状态发布与解析模块 |
| Agent / 本地Agent | 本地安全客户端 |
| Agent接口 | 本地客户端接口 |
| Agent数据库 | 本地安全数据库 |
| 不可信云环境 | 不可信同步存储环境 |
| 同步云 | 同步存储层 |

## 5. 英文与代码名映射

| 旧名 | 新名 |
|---|---|
| Local Agent | Local Secure Client |
| Local Agent API | Local Client API |
| VDNS Resolver | State Resolver |
| VDNS Verifier | Local State Verifier |
| VDNS Control Plane | Verifiable State Control Layer |
| `Agent` | `LocalSecureClient` |
| `NewAgent` | `NewLocalSecureClient` |
| `Config`（localapi application） | `LocalSecureClientConfig` |
| `VDNSResolutionRequest` | `StateResolutionRequest` |
| `VDNSResolution` | `StateResolution` |

## 6. 文件和命令重命名

| 旧路径/名称 | 新路径/名称 |
|---|---|
| `cmd/vdns-local-agent` | `cmd/vpass-local-client` |
| `scripts/demo-vdns-pm.sh` | `scripts/demo-vpass.sh` |
| `vdns-pm-browser-extension` | `vpass-browser-extension` |
| `vdns-pm-ci` | `vpass-ci` |
| `docs/答辩/VDNS-PM项目介绍六问回答.md` | `docs/答辩/VPass项目介绍六问回答.md` |
| `docs/论文/VDNS-PM研究生毕业论文.*` | `docs/论文/VPass研究生毕业论文.*` |
| `org.vdns_pm.local_agent` | `org.vpass.local_client` |

所有受版本控制的活动路径通过 `git mv` 迁移。`test-results/` 中的历史证据文件不重命名。

## 7. Go module 迁移

Go module 从 `vdns.local/vdns` 迁移到 `vpass.local/vpass`，当前 Go 源文件、测试、命令和工具的 import 已同步更新。这是研究原型内部 module 路径，不是已发布的公共 Go API。使用旧 import 路径的本地扩展代码需要同步更新。

## 8. SQLite 兼容策略

- 迁移文件仍然 append-only，不修改已发布 SQL 文本和校验和。
- 现有数据库中的 protocol/suite/domain 机器值继续可读。
- 表名、列名、状态枚举和密码学约束不因展示名改变。
- 新写入的展示元数据使用 VPass；签名域和 suite 值继续使用冻结 legacy 机器标识。

## 9. API 兼容策略

当前路径为 `/api/v2/state-resolutions`，当前会话和 nonce 头字段为 `X-VPass-Vault-Session` 与 `X-VPass-Request-Nonce`。服务端继续接受 deprecated `/api/v2/vdns-resolutions`、`X-VDNS-Vault-Session` 和 `X-VDNS-Request-Nonce`。legacy 路径和头字段执行相同鉴权、会话、nonce、Origin 和请求体检查，没有降低安全门槛。

## 10. 协议机器标识兼容策略

当前展示协议标签是 `VPass/2`。以下值已经进入签名域、KDF/AAD、SQLite 检查或冻结测试向量，仍作为 deprecated legacy wire identifiers 保留：

```text
ProtocolID  = VDNS-PM
SuiteID     = VDNS-PM-CP-2
DomainPrefix = VDNS-PM/2/
```

新代码从 `internal/protocol` 引用这些常量，不在普通业务流程重复生成旧产品名。未来如果需要新的 wire suite，必须使用新协议版本和 ADR，不得原地改字节值。

## 11. 历史证据保留策略

- `test-results/`、历史 Stage 报告、旧 baseline、历史 ADR 和已生成的摘要保留当时名称。
- `BASELINE-v2.1.0-stage2-g6.json` 保存命名迁移前的 Stage 2 摘要，不修改原摘要制造通过。
- 当前 `BASELINE.json` 是新的显式基线修订，使用当前真实文件重新计算摘要。
- 历史文件顶部的旧名提示只说明名称关系，不改写历史事实。

## 12. 潜在破坏性变化

- Go import 路径、命令二进制名、演示脚本路径和新 Native Messaging 主机名已改变。
- 仅安装旧 Native Messaging manifest 的新版扩展无法连接，升级时需要安装新 manifest。
- 依赖旧文件路径的本地脚本需要迁移。
- 持久化协议、SQLite 结构、凭据密文和密码学域不发生破坏性变化。

## 13. 用户升级步骤

1. 关闭旧扩展和本地进程，备份现有 SQLite 数据库和 Native Messaging manifest。
2. 构建 `./cmd/vpass-local-client`。
3. 以 `apps/native-host/org.vpass.local_client.example.json` 为模板，填写绝对二进制路径和已批准扩展 ID。
4. 安装新 Native Messaging manifest，更新至 VPass 扩展。
5. 用备份副本执行 SQLite 兼容测试，再打开原数据库。
6. 运行 `go test ./...` 和 `./scripts/demo-vpass.sh --data-dir "$(mktemp -d)"` 验证安装。

## 14. 回滚方案

停止 VPass 本地安全客户端，恢复升级前二进制、旧 Native Messaging manifest 和数据库备份。为支持升级窗口，仓库保留 `org.vdns_pm.local_agent.legacy.example.json` 样例。不通过反向修改已执行的 append-only 迁移进行回滚；如果数据库结构在后续版本中变更，应恢复备份或新增前向修复迁移。
