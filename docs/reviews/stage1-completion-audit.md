# VDNS-PM 第一阶段完成度审计

| 属性 | 值 |
|---|---|
| 审计日期 | 2026-07-31 |
| 审计范围 | 设计文档、论文、规范、ADR、OpenAPI、Go/扩展代码、测试、实验脚本和 `test-results/` |
| 当前阶段判定 | `G6`：研究原型集成；`G7` 研究原型冻结未达成 |
| 状态词 | `COMPLETE`、`PARTIAL`、`DOCUMENT_ONLY`、`CODE_ONLY`、`TEST_ONLY`、`NOT_IMPLEMENTED`、`UNVERIFIED` |
| 工作树标识 | 当前目录没有 Git 元数据，不能给出或伪造 commit SHA |

## 1. 审计方法与判定边界

本审计逐项核对“设计文档—代码模块—自动测试—实验或运行证据”。`COMPLETE` 只表示当前研究原型范围内四类材料闭合，不表示生产部署成熟。存在研究适配器、仅本地执行、缺少原始样本、缺少真实网络或缺少协议关键组件时记为 `PARTIAL`。只有文档、代码或测试单侧存在时使用对应单侧状态。没有实现时使用 `NOT_IMPLEMENTED`，无法从仓库证实时使用 `UNVERIFIED`。

本次实际执行：

- 审计开始时`GOPATH=/home/lwc/go go test ./...`通过，证明审计前代码基线可运行；
- `GOPATH=/home/lwc/go go vet ./...`：通过；
- `GOPATH=/home/lwc/go go test -race ./internal/... ./tests/...`：通过；
- `npm test`（`apps/browser-extension`）：10/10 通过；
- 完整本地 L1～L5、10 万叶夹具、101 次调用：P95 2.302853 ms，通过 25 ms 测试阈值。

v2.1.0设计冻结后再次执行`go test ./...`，除`tests/contract`外所有包通过。合同包有两项预期失败：旧测试仍要求OpenAPI 2.0.0，旧`BASELINE.json`仍要求v2.0.0摘要。该失败真实表示E0～E5和v2.1.0基线尚未迁移，归入第二阶段P0-007，未通过修改测试或伪造hash隐藏。

首次直接执行`go test ./...`因环境中预置的`GOPATH=/home/luo/go/go`无写权限而失败；改用当前用户可写的GOPATH后可运行。这是运行环境问题，不是业务测试失败。

## 2. 功能完成度表

| 功能 | 设计文档 | 代码模块 | 测试 | 实验证据 | 状态 | 问题 |
|---|---|---|---|---|---|---|
| 主密码与 RootCapsule | 开发报告 5.1；安全规范 5.2 | `internal/cryptokit` | KAT、错误密码/设备、篡改测试 | G7 E1 汇总、密码学审计 | COMPLETE | 仅研究原型；生产 OS 密钥库集成不在此结论内 |
| DeviceSecret | Spec FR-002/005；安全规范 5.2 | `internal/cryptokit`、设备领域 | 设备绑定、复制胶囊拒绝 | E1 汇总 | PARTIAL | 生成与组合已实现，生产 OS/硬件安全存储未实现 |
| RecoveryCapsule | Spec FR-004；安全规范 5.3 | `internal/cryptokit`、`internal/recovery/domain` | 正误恢复秘密、回滚/缺对象测试 | `recovery/DRILL_BACKUP_001.txt` | COMPLETE | 结论限本地自动恢复夹具，不代表异地灾备 |
| RouteMap | Spec FR-010；数据模型 4.3 | `internal/credential`、SQLite adapter | 同域多账号、重启、10k/100k | G7 E2 汇总 | COMPLETE | 云端同步 RouteMap 的真实网络部署未测 |
| OriginBinding | Spec FR-012/016；安全规范 5.5 | `internal/credential/domain`、扩展 | IDN、端口、跨 Origin、iframe | G5/G7 本地证据 | COMPLETE | 重定向链策略需要按 ADR-016 补齐代码测试 |
| 字段级加密 | Spec FR-012；安全规范 5.6 | `internal/cryptokit`、credential domain | AAD/nonce/tag/字段/版本变异 | 密码学审计、E8 最小字段证据 | COMPLETE | 使用 AES-GCM 研究实现，尚无外部密码学审计 |
| 密码生成 | Spec FR-011 | `internal/password/domain` | CSPRNG、拒绝采样、策略/统计测试 | G2/G7 测试证据 | COMPLETE | 真实网站策略适配覆盖有限 |
| 多设备加入 | Spec FR-007；安全规范 9 | `internal/device/application`、HPKE | challenge、短码、能力、一次消费 | G3 测试证据 | PARTIAL | 没有真实跨设备传输服务或 UI 联调，只验证端口与本地夹具 |
| 设备撤销 | Spec FR-008；安全规范 6 | `internal/device/domain`、resolver | 撤销序、新代际、旧设备拒绝 | E6、FI-REVOCATION、恢复演练 | PARTIAL | 控制面和代际模型已实现；最终序由外部输入，旧明文不可收回 |
| 生命周期状态机 | Spec FR-013/023/026 | `internal/credential/domain` | 创建、更新、UNKNOWN、冲突和恢复 | E4、故障/恢复日志 | COMPLETE | 完成度限本地领域状态机 |
| 网站确认 | Spec FR-023/024；安全规范 7.3 | `internal/site/application`、Mock Site | 成功、失败、丢响应、签名回执 | E4、FI-LIFECYCLE | PARTIAL | 只有 Mock Site/人工强确认；旧证据枚举尚未迁移到 E0～E5 |
| 本地 CAS | Spec FR-020/022；数据模型 6 | SQLite repository、outbox | 事务、幂等、重启、并发 | 故障和恢复证据 | COMPLETE | 只保证单数据库事务内条件写 |
| 跨设备 CAS 与冲突 | Spec FR-020/026 | sync acceptance、conflict aggregate | 两候选保留、显式裁决测试 | DRILL_CONFLICT | PARTIAL | 没有全局 CAS；两设备可各自产生 `v2-A/v2-B`，缺最终序服务 |
| VDNS L1 | Spec FR-028 | `internal/resolver/application` | 根链、签名、名称空间负向矩阵 | G4 矩阵 | COMPLETE | 研究原型本地验证 |
| VDNS L2 | Spec FR-029 | `internal/resolver/application` | capability/scope/counter/status | G4 矩阵 | COMPLETE | 依赖外部提供的可信当前凭证状态 |
| VDNS L3 | Spec FR-030 | `internal/resolver/application` | 撤销、版本、counter、前序 | G4/E6 矩阵 | PARTIAL | `finalSequence` 的权威生产者未实现 |
| VDNS L4 | Spec FR-031 | resolver、transparency、anchor | 包含/一致性/签名/Provider 变异 | G4、当前 L1～L5 测试 | PARTIAL | 单机日志和模拟/Anvil 边界，无生产多节点日志 |
| VDNS L5 | Spec FR-032 | resolver policy | 在线、离线、pending、review、拒绝 | G4 矩阵 | COMPLETE | 本地策略实现；产品策略配置面有限 |
| 透明日志 | Spec FR-033/034 | `internal/transparency`、monitor | Merkle、分叉、回滚、一致性 | E5、FI-LOG | PARTIAL | 日志为单进程研究实现，Appender 接收调用方给定最终序 |
| 最终序 | ADR-004；Spec FR-008/030 | 无独立 sequencer/consensus 实现 | 仅验证给定序号的单调性和拒绝逻辑 | E6 为本地输入矩阵 | NOT_IMPLEMENTED | 谁产生、如何终局、如何抗分叉此前未定义完整 |
| 同步协议 | Spec FR-019/025 | `internal/sync`、`memorysync` | rollback/substitution/missing/conflict | E3、本地故障日志 | PARTIAL | 10k 只测本地编码签名验证，不含网络传输；没有 `services/` |
| 隐私审计 | Spec FR-036～038 | `internal/audit` | 能力、一次句柄、复用/异常/陈旧 | E7 100k 本地结果 | PARTIAL | 本地分析器可运行，公开部署与跨节点流量隐私未验证 |
| SCOPE-ZK | Spec FR-039/040 | provider 接口与 DisabledProvider | unavailable 和接口边界测试 | E8 指标为 `null` | NOT_IMPLEMENTED | 没有 SCOPE-ZK 电路、prover、verifier 或真实 proof |
| 最小影响修复基线 | Spec FR-041～043 | `internal/remediation` | scope、成本、attempt、字段不变 | E8 本地 baseline | PARTIAL | 领域基线存在，没有真实网站批量执行器 |
| E1 解锁恢复实验 | Spec 实验 E1 | G7 research runner | 负向测试存在 | 30 次汇总指标 | PARTIAL | 未保存30次逐样本原始时延 |
| E2 日常管理实验 | Spec 实验 E2 | runner、SQLite/crypto | RouteMap/字段/自动填充测试 | 30 次汇总和历史 G5 | PARTIAL | 缺逐样本数据和真实浏览器兼容矩阵 |
| E3 多设备同步实验 | Spec 实验 E3 | 本地 manifest runner | 云攻击负向测试 | 100×100 本地汇总 | PARTIAL | 不含网络、对象上传下载或多进程端到端时延 |
| E4 生命周期实验 | Spec 实验 E4 | Mock Site/状态机 | 成功、失败、UNKNOWN、崩溃 | G3/G5、故障日志 | PARTIAL | Mock Site 不能代表真实网站 |
| E5 VDNS/日志实验 | Spec 实验 E5 | resolver/Merkle runner | 完整 L1～L5 和证明变异 | G4 L1～L5；G7 Merkle汇总 | PARTIAL | G7表中微秒值仅为 Merkle 包含验证，不能代替完整 L1～L5 |
| E6 撤销实验 | Spec 实验 E6 | device/resolver | 撤销和代际负向矩阵 | G3/G4、故障日志 | PARTIAL | 最终序是夹具输入，未测真实传播与竞争排序 |
| E7 隐私审计实验 | Spec 实验 E7 | audit runner | 真值、公开投影、跨 Epoch | G6 100k/开销汇总 | PARTIAL | 缺逐记录原始结果和网络元数据实验 |
| E8 泄露响应实验 | Spec 实验 E8 | local baseline/provider port | 越界、重放、无关字段 | G6/G7 本地汇总 | PARTIAL | SCOPE-ZK/通用 zkVM 均未实现，无法进行证明系统对比 |

## 3. 论文声明核对表

| Claim ID | 论文声明 | 对应代码 | 对应证据 | 是否可信 | 处理方式 |
|---|---|---|---|---|---|
| C-001 | 仓库处于 G7 研究原型冻结 | 多数 G1～G6 模块存在 | `final-gate-summary.json` | UNVERIFIED | 改为 G6 研究原型集成；列出 G7 阻断项 |
| C-002 | 开发报告 G0.2，论文 G7 | 两份文档元数据冲突 | 文档自身 | UNVERIFIED | 两者统一为 v2.1.0、G6，G7 未达成 |
| C-003 | E1～E8 均有真实原始结果 | runner 保存统计量 | 汇总 JSON/CSV、阶段文件 | UNVERIFIED | 改称“汇总证据”；逐样本缺失，E8 proof 不存在 |
| C-004 | Argon2id 解锁 P95 392.85 ms | `runE1` | G7 E1 30次汇总 | 可信（限定历史环境） | 保留数值，注明无逐样本和非当前重跑 |
| C-005 | 10k/100k RouteMap P95 为0.402/0.299 ms | `runE2` | G7 E2 30次汇总 | 可信（限定本地 SQLite） | 保留并限定环境和汇总性质 |
| C-006 | 10k 同步 P95 614.70 ms | `runE3` | G7 E3 汇总 | UNVERIFIED（作为网络同步） | 改称本地100×100 manifest构造/签名/验证，不含网络和对象传输 |
| C-007 | 百万叶 L1～L5 P95 16.79 μs | `runE5` 仅调用 `VerifyInclusion` | G7 E5 汇总 | UNVERIFIED | 改称百万叶 Merkle 包含证明验证；完整L1～L5另报本地测试 |
| C-008 | 10万叶完整 L1～L5 满足25 ms | resolver `Resolve` | G4 benchmark；本次 P95 2.302853 ms | 可信（限定本地夹具） | 保留为独立本地测试，不能与G7 Merkle微基准混写 |
| C-009 | 8/8全栈故障注入通过 | fault runner 调用定向 `go test` | 8个日志和清单 | UNVERIFIED（作为全栈） | 改称8/8本地适配器/协议故障回归 |
| C-010 | 7/7恢复演练真实存在 | shell 调用定向 `go test` | 7个日志和清单 | 可信（自动测试演练） | 保留7/7，明确非部署系统灾备演练 |
| C-011 | H1～H6均有实际弱化实现 | 只有完整机制代码；弱化项由runner造模 | `ablation-h1-h6.json` | UNVERIFIED | 改称“测试决策模型+完整机制回归”，不得称完整实现消融 |
| C-012 | SCOPE-ZK 已实现 | 仅 provider port/disabled provider | E8 为 UNAVAILABLE/null | NOT_IMPLEMENTED | 论文继续明确未实现，不给proof性能 |
| C-013 | 网站真实确认闭环 | Mock Site和本地签名回执 | E4/G5 Mock证据 | UNVERIFIED | 改称Mock Site/人工确认研究闭环 |
| C-014 | 设备撤销可使旧密码失效 | 代际轮换代码 | E6/恢复证据 | UNVERIFIED | 明确撤销只影响未来授权和新代际，无法收回旧明文 |
| C-015 | 当前可达漏洞为0 | 无代码映射 | 2026-07-22数据库快照 | UNVERIFIED（作为当前状态） | 改称历史扫描快照0；当前扫描需第二阶段重跑 |
| C-016 | 公开日志发现生产分叉 | 单机Monitor比较函数 | G4/FI-LOG本地夹具 | UNVERIFIED | 改称本地可验证分叉检测机制，未部署多观察者网络 |
| C-017 | 区块链提供生产最终性 | Anvil adapter明确非共识 | Provider测试 | NOT_IMPLEMENTED | 只写模拟/Anvil研究适配器，不宣称生产共识 |
| C-018 | 22个OpenAPI操作均完成产品实现 | 本地 handler与模型覆盖主要路径 | 合同测试和评分 | UNVERIFIED | 保留“合同定义22项”；逐端点真实服务集成需第二阶段映射 |

## 4. 关键审计结论

1. 仓库不是空壳。密码学、凭据领域、SQLite、生命周期、同步接受、L1～L5、Merkle、审计和浏览器扩展均存在可运行代码与测试。
2. 仓库也未满足 G7 冻结。`finalSequence` 由调用方传入，单机日志只检查单调性；跨设备冲突没有权威最终序服务；证据等级代码仍使用旧枚举。
3. `services/` 不存在。文档中的服务名是逻辑部署边界，当前实现是 Go 模块化单体与内存/SQLite/Mock/Anvil 研究适配器。
4. 历史门禁文件只能证明当时脚本返回成功，不能自动证明声明口径正确。G7 evidence manifest 也不能替代语义审计。
5. 实验文件保存了指标汇总、环境、命令和部分日志，没有保存E1～E5每次测量的原始duration数组。所有涉及置信区间复算的声明必须保持 `UNVERIFIED`，直到第二阶段补齐原始样本。
6. 当前真实阶段统一为 G6：研究原型集成。G7 需要先完成协议正确性修复、重新生成证据并复审论文声明。
