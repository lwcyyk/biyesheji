# VDNS-PM

VDNS-PM（Verifiable Password Lifecycle Management over VDNS）是一个面向多设备和不可信云环境的完整密码管理器研究原型。

> 当前统一状态：文档v2.1.0，代码阶段G6，第一阶段协议设计已冻结，G7研究原型冻结未达成。当前单机日志、Mock Site、memorysync和Anvil均为研究适配器。详见[第一阶段完成度审计](docs/reviews/stage1-completion-audit.md)。

它的日常主线是：

```text
主密码解锁 → 生成/加密保存 → VDNS 可信解析 → 自动填充
          → 多设备同步 → 网站确认更新 → 撤销与恢复
```

核心设计：

> AEAD 保护密码内容，VDNS 保护密码控制过程。

云端只保存和分发加密对象，不决定哪个凭据版本是当前真实版本。设备通过主体、权限、动态撤销、版本因果、透明历史和本地策略五层验证独立接受状态。

隐私审计用于重复、历史、陈旧、异常、回滚和冲突分析。SCOPE-ZK 是事故时可选 provider，当前未配置，日常路径不依赖它、区块链或 VRF 在线。

## 快速演示

依赖：

- Linux；
- Go 1.25.12（`go.mod` 已固定 toolchain）；
- Node.js 18+；
- SQLite 3、`jq`。

在仓库根目录执行：

```bash
demo_dir="$(mktemp -d)"
./scripts/demo-vdns-pm.sh --data-dir "${demo_dir}"
```

脚本只接受安全的空目标目录，使用固定 TEST_ONLY 数据完成初始化、创建/填充、同步、网站确认更新、撤销、离线、VDNS、隐私审计和可选响应边界。

不要把真实密码库、主密码、TOTP 或恢复材料导入演示。

## 验证

快速检查：

```bash
env -u GOPATH go test ./...
./scripts/check-spec-trace.sh
./scripts/check-g7-api.sh
./scripts/check-g7-security.sh
./scripts/check-g7-crypto.sh
./scripts/drill-g7-recovery.sh
```

历史G7门禁（只用于复查旧证据，不能据此声明当前G7完成）：

```bash
./scripts/check-g7.sh
```

重跑固定 E1～E8、故障、消融和恢复实验：

```bash
./scripts/run-g7-experiments.sh
```

历史机器证据集中在`test-results/g7/`。`evidence-manifest.json`证明旧文件摘要和映射存在，不等于声明语义已经核验。v2.1.0 OpenAPI已冻结新证据等级，旧合同测试在第二阶段代码迁移前预期报告版本/基线差异。

生成可编辑论文和最终提交归档：

```bash
./scripts/check-thesis-docx.sh
./scripts/package-submission.sh
sha256sum -c dist/SHA256SUMS
```

提交归档排除 task-local 工具、`node_modules`、数据库、私钥和环境文件；归档内的 `SUBMISSION-MANIFEST.json` 可逐文件验证内容。

## 目录

```text
apps/browser-extension      浏览器扩展
cmd/                        本地服务与 G7 研究命令
internal/                   领域核心、端口和适配器
migrations/                 SQLite append-only 迁移
specs/001-vdns-audit-rotation
                            v2.1设计冻结spec、P0～P3 tasks和contracts
experiments/g7/             固定数据集、schema 和 AC 证据映射
docs/                       开发、审计、论文、答辩和运行手册
scripts/                    阶段门禁、演示、实验与恢复演练
tests/                      架构、合同、e2e 和性能测试
```

## 文档入口

- [研究生毕业论文](docs/论文/VDNS-PM研究生毕业论文.md)
- [可编辑论文 DOCX](docs/论文/VDNS-PM研究生毕业论文.docx)
- [提交前检查表](docs/提交前检查表.md)
- [开发报告](docs/VDNS研究生毕业设计开发报告.md)
- [G7 实施记录](docs/G7阶段实施记录.md)
- [密码学与协议审计](docs/audits/G7密码学与协议审计.md)
- [API 复审](docs/audits/G7-API复审.md)
- [威胁模型与安全审计](docs/security/G7威胁模型与安全审计.md)
- [运行与恢复手册](docs/runbooks/VDNS-PM运行与恢复手册.md)
- [论文与架构图集](docs/diagrams/index.html)
- [答辩演示](docs/答辩/VDNS-PM答辩演示.pptx)
- [规范入口](specs/001-vdns-audit-rotation/spec.md)
- [第一阶段完成报告](STAGE1_COMPLETION_REPORT.md)

## 已知边界

- 研究工作区没有 Git 元数据，证据记录为 `WORKTREE_NO_GIT`；
- 浏览器未安装，扩展以合同、TAP 和本地 e2e 验证，未形成真实浏览器兼容矩阵；
- Mock Site、模拟日志和 Anvil 适配器不等于真实网站或生产共识；
- Final Order Authority尚未实现，本地CAS不能保证跨设备全局唯一版本；
- 代码仍使用旧网站证据枚举，E0～E5迁移属于第二阶段P0；
- 单份 10k 对象 manifest 会超过冻结的 64 KiB 公共签名载荷，当前采用 100×100 分批；
- SCOPE-ZK 和通用 zkVM provider 为 `UNAVAILABLE`，没有 proof 时间/大小数据；
- 历史E1～E5没有保存逐轮原始时延，统计独立复算为`UNVERIFIED`；
- 撤销阻止未来权限和新秘密代际，不能擦除设备撤销前已取得的历史秘密；
- 完全控制已解锁端点的攻击者不在当前防御范围。

## 数据与安全

仓库实验数据使用固定 seed `20260723`，只用于可复现测量，不得进入生产随机生成路径。公开日志和论文材料不得包含主密码、网站密码、恢复秘密、字段 DEK 或真实账户关系。
