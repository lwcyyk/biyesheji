# 主线在线状态集成与本地恢复验收

2026-11-05，Asia/Shanghai。

ONLINE_TRUSTED_STATE_V1 已形成可执行的成熟组合实例。本地持久接纳、预算、派发、返回、撤回和在线恢复均可从 `auth-lifecycle/scripts/online_state.py` 调用。M1 的 21 个授权计划槽位最终为 **20 通过、1 初始化中止、安全失败 0、未运行 0、INCONCLUSIVE 0**。原生 Casdoor、Keycloak、真实 AS/RP 请求为 0。

当前达到有限本地恢复证据的交付条件，可以准备下一阶段限定 provider/profile 的原生补证。生产托管闭包、真实认证批准和原生关闭能力各自保留验收要求。密码学辅助线保持 FROZEN。

## 交付入口

| 工件 | 路径及用途 |
|---|---|
| 运行层源码 | [online_state](D:/毕业设计/auth-lifecycle/src/auth_lifecycle/online_state) |
| 迁移 | [migration.sql](D:/毕业设计/auth-lifecycle/src/auth_lifecycle/online_state/migration.sql) |
| 启动和调用 | [online_state.py](D:/毕业设计/auth-lifecycle/scripts/online_state.py)，提供 init、serve、request、trace、m1 |
| 开发回归 | [test_online_state.py](D:/毕业设计/auth-lifecycle/tests/test_online_state.py) |
| 独立评分 | [score_online_state.py](D:/毕业设计/auth-lifecycle/scripts/score_online_state.py) |
| 架构与不变量 | [ARCHITECTURE_AND_INVARIANTS.md](ARCHITECTURE_AND_INVARIANTS.md) |
| 最终运行环境与源码 | [ENVIRONMENT_LOCK_v2.json](ENVIRONMENT_LOCK_v2.json)、source_snapshot_v2/ |
| 初始版本 | ENVIRONMENT_LOCK.json、source_snapshot/，用于绑定首条初始化中止 |
| 修改前状态 | PRECHANGE_MANIFEST.json、prechange/，记录 68 个源码/测试/脚本/项目文件及 Git 缺失事实 |
| 可检查补丁 | [implementation.patch](implementation.patch)、CHANGE_MANIFEST.json |
| 完整验收分母 | [M1_AGGREGATE.json](M1_AGGREGATE.json) |
| 原始批次 | m1_batch01/、m1_batch01_continuation/，含批次锁、逐条轨迹和独立评分 |
| 清理 | CLEANUP_STATUS.json，最终本任务测试服务进程数为 0 |

仓库增加 11 个文件，修改 pyproject.toml 和 README.md。66 个既有清单文件的字节匹配修改前摘要。原历史合同文件的摘要匹配起始记录。pyproject 增加可选 online-state 依赖和 SQL 包数据。既有算法代码按起始字节保留，本轮实现属于新增运行层。

## 开发证据与修复链

| 记录 | 结果 | 范围及后续 |
|---|---|---|
| dev01/unittest.txt | 11/11 通过，49.537 秒 | 新运行层首次集成。Windows icacls 本地编码导致输出读取线程警告，随后改为字节捕获 |
| dev02/unittest.txt | 109/109 通过，85.507 秒 | 含 96 个既有测试及 13 个新测试。保留旧 CLI 编码警告与单活锁句柄警告 |
| dev03/unittest.txt | 109/109 通过，88.916 秒 | 统一子进程 UTF-8。单活锁在异常处理之前读取锁区仍产生句柄警告，随后改用文件大小检查并覆盖异常关闭 |
| dev04/unittest.txt | 2/2 通过，9.061 秒 | 最终单活锁和独立评分器针对性回归 |
| dev_smoke/normal | 独立评分 PASS | 开发范围的运行器正常路径，73 次显式 SQL，独立于 M1 分母 |
| M1 初始 normal_1 | 初始化 ABORTED | 隐藏进程的 whoami 输出包含本地编码用户名，UTF-8 解码失败。发生在服务启动、数据库操作和业务请求之前 |
| dev05/unittest.txt | 2/2 通过，10.653 秒 | 改为从原始字节提取 ASCII SID。新增针对性回归验证本地编码输入，以及续行只消费原授权 NOT_RUN 槽位 |

最终源码中的开发测试共 15 项。全仓 109 项的结果绑定 dev03 版本，后续修订由上述针对性测试及最终 M1 覆盖。每轮保留原始日志和源码版本引用，测试次数按各自执行范围解释。

新测试覆盖正常 TLS 入口、错误身份/任务/账户/受众/代次/操作、并发预算、重复 rid 与冲突正文、队列与撤回竞争、先放行后撤回、ACK 丢失后的收据查询、放行后未知、迟到和重复结果、旧缓存、权威不可达、必要密钥不可用、A 未决时 B 恢复、事务中途失败、单活及秘密投影。评分器负控制将 provider 来源代次篡改为另一代次，独立检查按预期拒绝。

## M1 结果及分母

首条初始化失败后，初始执行段停止，记录为 1 ABORTED 和 20 NOT_RUN。修复完成后，在同一原授权内续行这 20 个未执行槽位。续行没有重复已经尝试的槽位。初始段及修复段分别冻结版本，原始批次记录保留。完整 21 条重跑未执行。

| 原计划场景 | 通过 | 中止 | 安全失败 | 未运行 |
|---|---:|---:|---:|---:|
| 正常运行 | 2 | 1 | 0 | 0 |
| pending 提交前中断 | 3 | 0 | 0 | 0 |
| 放行提交后、外发前中断 | 3 | 0 | 0 | 0 |
| 外发后、结果登记前中断 | 3 | 0 | 0 | 0 |
| 撤回提交前中断 | 3 | 0 | 0 | 0 |
| 撤回 ACK 后旧缓存恢复 | 3 | 0 | 0 | 0 |
| 权威不可达后恢复 | 3 | 0 | 0 | 0 |
| 总计 | 20 | 1 | 0 | 0 |

两个执行段累计 200.391 秒。首个批次锁至最后结果文件的墙钟跨度为 427.046 秒，包含修复期间，低于 30 分钟。已运行轨迹为 4.906–13.922 秒，低于每条 60 秒。每条显式 SQL 为 53–83 次，包含初始化和评分器两次只读查询，低于每条 100 次。

后续汇总单独执行了每条通过轨迹一次的离线只读 SQL 查询，共 20 次，用于定位 B 首次接纳版本。即使把该查询计入对应轨迹，每条仍至多 84 次。该离线读取不进入运行者决策。

故障由屏障确定位置，再真实终止控制器进程并 wait 退出。新进程重新获取权威状态。权威不可达场景真实终止并重启权威进程，DB、WAL 和密钥目录保留。旧快照恢复只覆盖 cache/view.json。每条评分包含进程启动/退出序列和清理检查。

## 不变量的验证范围

20 条通过轨迹均满足已检查的事务序列、预算、来源、结果和效果对应关系。每个 provider 效果对应一个同来源的持久派发尝试。A 撤回 ACK 后的新增请求被拒绝，A 未知请求的重复调用保持既有记录。迟到 A 材料保留 g0 来源并进入隔离。B.g1 在相应恢复后完成自己的请求。

放行后、发送前的三条轨迹保留 A1 为 DISPATCHED_UNKNOWN。产生结果的轨迹在撤回后保留 A1 的 QUARANTINED 处置义务。pending 前中断的三条轨迹尚未建立 A1 请求。最终 17 条通过轨迹保留 A1 的未知或隔离义务，另 3 条的该义务为空。这些状态如实保留了原生处置责任。

运行者通过已知尝试的 lookup 接口补收结果，评分器独立读取 provider 真值和权威密文。评分器的 accesses 字段列明额外读取路径。评分器没有导入运行层实现，源码检验和篡改负控制支持这一独立读取范围。

## 成本记录

以下范围仅覆盖本机两批准实例、一个 A 请求和一个 B 请求的 20 条通过轨迹。

| 指标 | 实测范围或总量 | 口径 |
|---|---|---|
| 显式 SQL | 每条 53–83，共 1424 | 权威 SQL 调用、初始化、事务控制与独立评分两次查询 |
| 提交事务 | 每条 7–11，共 205 | authority_events 中的提交版本，含拒绝/重复决策的审计提交 |
| M1 冲突及 SQLite 自动重试 | 均为 0 | M1 顺序轨迹范围。开发并发回归单独记录 |
| 逻辑状态快照写入 | 每条 8982–19908 字节 | 各提交加密前完整应用状态的规范 JSON 长度累计 |
| 恢复响应量 | 每条 2189–4329 字节 | 控制器 recover RPC 的响应 JSON 字节累计 |
| 控制器内部 RPC 请求 | 每条 1796–3624 字节 | R→权威/provider 的请求 JSON，包含可信侧材料传输长度 |
| 控制器内部 RPC 响应 | 每条 4307–8878 字节 | 权威/provider→R 的响应 JSON |
| B 接纳观察延迟 | 0.078–0.156 秒 | 同一控制器进程中，最后恢复完成事件到 B 接纳响应的可观察时间 |
| B 请求完成延迟 | 0.156–0.281 秒 | 运行者发起最后恢复至 B 结果持久返回，包含中间检查 |

B 的首次合法接纳以权威提交 version 单独登记在 M1_AGGREGATE.json。时间字段为客户端/进程局部可观察时间，提交顺序依据事务版本。

JSON 字节计数覆盖协议正文，TLS、HTTP 头及 TCP 开销未测。SQLite 参数长度是逻辑代理指标。数据库/WAL 文件大小是评分时的文件快照，物理累计 WAL 写入和 fsync 次数为 null。原型每次提交写完整加密状态，规模成本需要另行测量。B 的已确认合同为最终恢复，以上范围没有被提升为硬时限或总体分位数。

## 从新目录复现

以下使用源码入口。当前环境已具备 cryptography 50.0.2。干净 Python 环境可先安装项目的 online-state 可选依赖。

```powershell
Set-Location -LiteralPath 'D:\毕业设计\auth-lifecycle'
$runtimePython = 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$env:PYTHONPATH = 'D:\毕业设计\auth-lifecycle\src'
$env:PYTHONUTF8 = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
# 仅在新 Python 环境需要时执行
# & $runtimePython -m pip install -e '.[online-state]'

$newTestRoot = 'D:\毕业设计\mainline_online_state_v1\reproduce_dev_new01'
if (Test-Path -LiteralPath $newTestRoot) { throw '请选择全新的测试目录' }
New-Item -ItemType Directory -Path "$newTestRoot\tmp" | Out-Null
$env:ONLINE_STATE_TEST_ROOT = "$newTestRoot\work"
$env:TEMP = "$newTestRoot\tmp"
$env:TMP = $env:TEMP
& $runtimePython -B -m unittest discover -s tests -v 2>&1 |
    Tee-Object -FilePath "$newTestRoot\unittest.txt"
```

单条开发轨迹可完成建环境、启动三个组件、正常流程和进程退出。独立评分随后读取真值并生成 result.json。

```powershell
$newTrace = 'D:\毕业设计\mainline_online_state_v1\reproduce_trace_new01'
& $runtimePython -B scripts/online_state.py trace --root $newTrace --scenario normal
& $runtimePython -B scripts/score_online_state.py --root $newTrace
```

完整 M1 复跑需要单独登记执行授权和新目录。下面为后续已授权批次的命令模板，本轮执行记录见两个实际批次目录。

```powershell
& $runtimePython -B scripts/online_state.py m1 `
    --out 'D:\毕业设计\mainline_online_state_v1\reproduce_m1_new01' `
    --authorization-id '填写另行确认的完整复跑授权编号'
```

本轮实际续行命令在控制台日志对应记录，使用 `--continue-from m1_batch01/results.json` 和同一原授权编号。续行器仅执行 NOT_RUN 槽位，对安全失败后的续行予以拒绝。

每条轨迹的 Laboratory.close 会终止并 wait 本条拥有的服务进程，超时路径终止本条进程树。原始证据及合成密钥保留在本轮目录用于复核。最终 CLEANUP_STATUS.json 记录测试服务进程为 0。

## 后续工程与原生补证

当前可进入限定范围的原生补证准备。下一次运行需固定一个 provider/profile、新测试账户、批准和请求预算，明确以下事项。

- 将真实 provider 适配器连接到持久运行层，冻结其请求/结果来源映射、AT/RT 束结构和错误语义。
- 审计真实代理的进程/文件权限、浏览器状态、管理响应、重定向和日志，验证任务句柄的完整托管边界。
- 对已知材料逐项验证原生失效，独立记录原生撤销单元 G。
- 对全部后代关闭取得完整来源、分页/并发枚举及派生截止证据，明确未知句柄和在途结果的终结条件。
- 对实际 RP 固定最终接受、提交和外部效果终态，核验关闭点与本地 ACK 的映射。
- 验证共享根处置对 B 的影响，以及真实批准 UI/身份、密钥备份、权威恢复和单活运维。

当前工程边界还包括单字符串合成材料、受限整数业务载荷、整状态加密写入、同机可信 OS 用户和独立恢复域的目录/进程范围。主机掉电、磁盘损坏、权威自身回滚、跨主机多活和生产认证部署均有各自待验收项。

该交付登记为实现符合性、有限故障验证和工程支撑。严格密码学分离实例仍为 0，重开条件沿已确认的证据链执行。
