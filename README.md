# VPass

VPass（Verifiable Password Lifecycle Management System）是一套面向多设备和不可信同步存储环境的可验证密码生命周期管理研究原型。

> 当前基线：Spec 2.1.0，G6 研究原型集成，Stage 1 协议设计已冻结，G7 未达成。

系统的日常主线：

```text
主密码解锁
  → 生成并加密保存
  → 可信状态解析
  → 自动填充
  → 多设备同步
  → 网站确认更新
  → 撤销与恢复
```

核心设计：

> AEAD 保护密码内容，可验证状态控制层保证凭据版本和生命周期状态可信。

同步存储层只保存和分发加密对象，无权决定哪一个凭据版本当前有效。本地安全客户端通过主体真实性、操作资格、动态状态、透明历史和本地策略五层验证，独立判断状态是否可以接受。

## 当前实现状态

- 研究型最终顺序模块已完成研究范围内的闭环，支持候选提交、单调最终序、冲突集合、显式裁决、签名回执、研究检查点和 SQLite 恢复。它的部署类型是 `RESEARCH_ADAPTER`，没有实现多节点共识、BFT 或生产级最终性。
- E0～E5 已进入领域模型、本地客户端接口和 SQLite v2.1。E0、E1 不能激活新版本，E2 进入 `REVIEW_REQUIRED`，E3 需要严格站点策略，E4 当前只有 Mock 测试实现，E5 是用户裁决。真实网站 E4 可信签名接口仍为 `NOT_IMPLEMENTED`。
- localhost 真实 HTTP 研究同步适配器已完成，已测试 10,000 个对象的分批传输，支持分页、幂等、重试和故障模拟，覆盖损坏对象、旧清单、网络中断和隐藏分支。部署标识为 `RESEARCH_HTTP_SYNC_ADAPTER`。
- 五层可信状态验证核心逻辑已实现。本地客户端接口需要注入真实本地状态验证器，未配置时返回明确错误，不生成模拟成功结果。
- CanonicalOrigin、RouteMap、OriginBinding、字段级信封加密、凭据状态机、透明日志及撤销边界均已形成研究实现和测试。

## 快速演示

依赖 Linux、Go 1.25.12（`go.mod` 已固定 toolchain）、Node.js 18+、SQLite 3 和 `jq`。

```bash
demo_dir="$(mktemp -d)"
./scripts/demo-vpass.sh --data-dir "${demo_dir}"
```

脚本只接受安全的空目录，使用 `TEST_ONLY` 数据验证凭据生命周期、可信状态解析、隐私审计、故障注入和可选模块边界。不要导入真实密码、TOTP 或恢复材料。

## 本地验证

```bash
go mod verify
test -z "$(gofmt -l cmd internal tests migrations)"
go vet ./...
go test ./... -count=1
go test -race ./internal/... ./tests/contract ./tests/e2e -count=1

(cd apps/browser-extension && npm test)

./scripts/check-g7-api.sh
./scripts/check-secrets.sh
./scripts/check-spec-trace.sh
./scripts/drill-g7-recovery.sh
```

`scripts/check-g7.sh` 和 `scripts/run-g7-experiments.sh` 用于历史 G7 证据复查与未来固定环境实验，不会仅因脚本成功就把当前阶段提升为 G7。

## 目录

```text
apps/browser-extension       VPass 浏览器扩展
apps/native-host             Native Messaging 配置及 legacy 配置样例
cmd/vpass-local-client       本地安全客户端命令
internal/                    领域核心、端口和适配器
migrations/                  SQLite append-only 迁移
specs/001-vdns-audit-rotation
                             保留的 legacy spec 目录 ID，内含 Spec 2.1.0
docs/                        开发、审计、论文、答辩和运行文档
scripts/                     门禁、演示、实验与恢复演练
tests/                       架构、合同、E2E 和性能测试
```

## 文档入口

- [命名迁移与兼容策略](docs/migrations/vpass-naming-migration.md)
- [研究生毕业论文](docs/论文/VPass研究生毕业论文.md)
- [开发报告](docs/VPass研究生毕业设计开发报告.md)
- [Stage 2 完成报告](STAGE2_COMPLETION_REPORT.md)
- [Stage 2 代码审计](docs/reviews/stage2-code-audit.md)
- [Stage 2 API 覆盖](docs/reviews/stage2-api-coverage.md)
- [运行与恢复手册](docs/runbooks/VPass运行与恢复手册.md)
- [答辩六问回答](docs/答辩/VPass项目介绍六问回答.md)
- [架构图集](docs/diagrams/index.html)
- [Spec 2.1.0](specs/001-vdns-audit-rotation/spec.md)

## 兼容策略

VPass 是唯一当前展示名和新写入名。旧产品名 `VDNS-PM`、旧路径 `/api/v2/vdns-resolutions`、旧头字段 `X-VDNS-*` 和旧 Native Messaging 主机名仅在 legacy 读取、迁移、冻结合同或历史证据中保留。冻结的签名域、KDF/AAD 域和 SQLite 迁移值继续使用旧机器标识，避免改名改变密码学语义或破坏旧数据。详细规则见命名迁移文档。

## 已知边界

- 当前仍为 G6 研究原型集成，G7 未达成。
- 生产多节点/BFT 最终顺序服务未实现。
- 真实公网同步存储、生产鉴权、TLS 运维、租户隔离和高可用未实现。
- 真实网站 E4 可信签名接口、平台操作系统安全存储、真实浏览器自动化和移动端均未实现。
- SCOPE-ZK 未实现。
- 设备撤销完整 API、界面和真实网站修复编排为 `PARTIAL`。
- 新设备可信初始检查点的完整产品流程为 `PARTIAL`。
- 最终 E1～E8 实验和固定环境证据尚未冻结。
- Mock Site、研究日志、单节点排序和模拟锚定都不代表生产服务。
- 撤销可阻止未来权限和新秘密代际，无法擦除设备在撤销前已取得的旧密码。

## 数据与安全

实验固定 seed `20260723` 仅用于可复现的 `TEST_ONLY` 数据，不得进入生产随机生成路径。公开日志、论文和仓库不得包含主密码、网站密码、恢复秘密、字段 DEK 或真实账户关系。
