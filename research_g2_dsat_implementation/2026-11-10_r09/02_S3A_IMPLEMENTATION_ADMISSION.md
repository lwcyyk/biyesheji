# S3-A 最小实施准入规格

本稿为静态工程规格；当前实现和运行均未开展。机器可读冻结值以 `S3A_SCOPE_LOCK.json` 为准；发现冲突时停止执行并重新审定。

## 1. 逐文件边界

工程根：`D:/毕业设计/auth-lifecycle`。只申请新增以下七个文件和一个夹具子树。

| 新路径 | 输入 → 输出；副作用 |
|---|---|
| `src/auth_lifecycle/online_state/dsat_commit_types.py` | JSON/typed 数据 → Proposal、Delta、Coverage、Version、Receipt 与规范摘要；纯数据处理 |
| `src/auth_lifecycle/online_state/dsat_commit.py` | 冻结源/投影/包、可信 actor、当前快照 → prepare/validate/coverage/费用计划；受控调用独立检查器适配，持久写入交给 store |
| `src/auth_lifecycle/online_state/dsat_synthetic_store.py` | 已批准专用路径、种子/提案 → read/commit/recover/历史回执；仅显式构造后连接专用 SQLite |
| `tests/test_dsat_commit_contract.py` | 合成合同输入 → 绑定、权限、覆盖、时间/证书层级断言 |
| `tests/test_dsat_commit_store.py` | 合成 DB → 版本/CAS/幂等/费用/并发和四表断言 |
| `tests/test_dsat_commit_recovery.py` | 新建专用子进程 → 握手故障点/重开库/恢复断言 |
| `tests/fixtures/dsat_commit/` | 白名单原件按哈希派生 → 新种子、固定投影清单与测试变体；原件保持 |
| `scripts/run_dsat_s3a_tests.py` | 固定范围参数 → 只载入上述三测试，组织 checker/worker、日志和哈希清单；禁止整仓发现 |

三个新增模块的导入闭包限定标准库及原有纯数据模块；模块导入阶段无 I/O、连接、服务启动或子进程。当前包 `auth_lifecycle/__init__.py` 与 `online_state/__init__.py` 为静态版本声明。未来须静态检查直接及传递导入闭包，排除 storage/services/native_provider。原 checker 以固定绝对路径显式 CLI 调用，父进程核其源码摘要、退出码及结构化结果；body 自填的 accepted 字段只作为不可信输入处理。

## 2. 唯一物理布局（字段规格，未执行 SQL）

新库的 `application_id=0x44534133`，专用 `user_version=1`，世界 schema `dsat-s3a-world/1`，mode `SYNTHETIC_CONTRACT`，codec `SyntheticJsonCodec/1`。这里的 user_version 只属于新库；S3-B 的生产迁移候选版本独立管理。

| 表 | 唯一键与字段 | 写规则 |
|---|---|---|
| `s3a_state` | `id=1`；`version` 为非负 SQLite signed64 整数 a；`payload` 为规范 UTF-8 JSON | 唯一世界权威行 |
| `s3a_events` | `version` 主键；唯一稳定 `event_id`；`operation`、`projection`、`event_digest` | 接受的世界变化才追加，与 a 对应；拒绝/重放保持 |
| `s3a_proposals` | `(authority_instance,proposal_id)` 主键；owner、proposal_digest、终态 status、receipt、receipt_digest | 每个已持久 ID 插入一次；原行与回执不可变 |
| `s3a_objects` | `object_digest` 主键；kind、canonical_bytes、byte_count | 接受证明/输入/检查记录/费用工作/风险描述同库保存；同 digest 须逐字节和 kind 相符 |

payload 包含：schema/mode/codec、authority_instance、genesis_revision、合成源快照/作用域/策略与权限、`dsat` 命名空间。dsat 包含唯一 o、typed O、已接受证明与历史引用、逻辑工作索引。a 唯一以 version 列为准，o 唯一以 `dsat.obligation_revision` 为准。实例 ID 在 genesis 固定；每份测试库使用独立实例。种子 a=120/o=0；genesis 前的历史不冒充本库事件，后续事件版本从 121 连续递增。恢复核对 schema/实例/摘要/引用及事件末端与世界版本；任何不完整情况安全拒绝启动。

`SyntheticJsonCodec` 承担严格编码和解码，合成数据明文落盘；AES-GCM 物理兼容、保密和恶意整体回滚检测归属独立工作。

## 3. 编码、绑定与四份 O

新规范 JSON：键排序、紧凑分隔符、ASCII 转义、UTF-8；接受对象/数组/字符串/布尔/null/有界整数；重复键、浮点、NaN、孤立代理字符和深度超过 32 的输入入口拒绝。ID 限安全 ASCII 1–128 字符，路径通过独立受控参数提供。布尔与整数类型严格区分，a/o 最大 `2^63−1`，费用整数上限沿旧 128 bit，溢出拒绝。

新提案摘要为域 `dsat-commit/1:proposal` 加规范完整正文（排除自摘要）。对象摘要按 `dsat-s3a-object/1`、kind 与精确内容域分离；receipt/state/event 各自独立域。现有 packet_digest/math_digest/旧绑定 digest 算法与字节保持。对象内容摘要、packet_digest、数学输入摘要各承担不同职责。

每份提案显式包含 R08 的身份、base(a/o/O/source/scope/grant)、proof/checker/math、projection、delta、dependency、cost、requested_level 和完整摘要字段。历史策略/当前依赖要求也纳入正文。无秘密或 bearer 能力进入这些对象。

四份 O：

| 对象 | 可信来源及核对 |
|---|---|
| O_before | 当前事务实际读取的 typed O；新域 base_O_digest 与 a/o 一起核对 |
| O_projection | 固定 S1 输出关系；以哈希白名单锁定 R07 既有输出及其 fixture 关系，作为合成输入清单 |
| O_proof_context | 原 packet `bindings.O_before`；按原 `digest("O_before", …)` 核对原包绑定 |
| O_after | 当前 base 加保守新项/合法覆盖替换，实际事务保存；独立摘要进入回执 |

`projection_O_digest=proof_context_O_digest=packet.digests.O_before_digest` 使用同一旧绑定算法；base/after 的新 typed O 摘要单独计算。typed O 对原四字段视图的映射显式保留；扩展风险描述通过不可变对象引用绑定。固定投影清单从可信 R07 产物建立，外部 body 无权自建“可信投影”。本阶段消费冻结输出，既有 S1/S2 算法运行和 NetworkX 求解另维持原范围。

A08/A24：未来先将 fixture 五项 O 初始化到合成库并读回；分别核六项投影及新增 close/await 项。验收默认 union 下 O_after 为六项，新增风险生效 o+1；settle→pending_source 的单独变体按覆盖规则计算项数，仍须保留原风险和 A24 审计/window。任何把两份不同 O 摘要强改相同的做法均触发验收失败。

## 4. T0–T7 顺序与所有 writer

| 步骤 | 冻结操作 |
|---|---|
| T0 | 严格解析、上限、body 摘要及外部可信身份；区分读本人历史资格与新提案写资格 |
| T1 | 独立连接；WAL、FULL、foreign_keys=ON、busy_timeout=1000ms、temp_store=MEMORY；BEGIN IMMEDIATE；一次读取 a/payload/o |
| T2 | 先确认请求实例与刚读出的固定库实例相符，不符则入口拒绝且不占ID；再查实例/ID；同 owner/body 且有历史读权返回原 receipt；异 body 冲突，异 owner/读无权拒绝披露；此步先于旧base CAS/容量检查 |
| T3 | 对新 ID 查当前管理写权/作用域、256 ID 容量、实例、a/o 和 base_O/source/scope/grant；检查本地 policy epoch |
| T4 | 核可信 checker 记录及精确包/输入/投影、当前本地依赖、固定覆盖规则、允许写集、work ID/body/费用和全部资源界 |
| T5 | 接受路径同库插对象、更新世界/O/历史/work、a+1、按 O 语义变化增 o、追加世界事件、插终态提案/不可变 receipt；状态更新带旧 a 条件并要求恰好一行 |
| T6 | 显式 COMMIT；异常时尝试受控回滚/关闭，提交结果可能未知则以同 ID 查询裁定 |
| T7 | 返回原不可变 receipt 与独立 delivery 元数据 replayed/historical_only/current-use；传输失败保留持久事实 |

昂贵数学检查放写锁外。T4 验证的是可信执行器绑定精确 packet/checker/输入字节的结果，当前权限/依赖/CAS 仍在事务内核对。历史数学包的 authority_version 保持原值，新的外层 base 独立绑定并重新核对投影/范围；包仍然只陈述原输入历史。

新合法提案 CAS/覆盖/证书失败可提交终态 REJECTED 行和小回执，世界行、a/o、O、events、objects 均保持。无权/畸形输入、容量已满或存储无法容纳拒绝行时，返回入口拒绝或 `REJECTION_NOT_PERSISTED`，明确 ID 未建立持久绑定。已有 ID 查询在容量满时仍有效。单个拒绝 ID 的后续改正文必须使用新 ID。

ACK 丢失：若 T6 已持久，T2 返回原 receipt，世界事件和逻辑工作仍各一次；若事务尚未持久，恢复后按当前基准重新处理。exactly-once 范围为同一可信实例的已持久逻辑效果；传输、检查、重试 I/O 和外部 AS 行为分别计费。

终态回执固定保存：实例/ID/owner/body摘要、ACCEPTED或REJECTED、结果原因、base与提交/拒绝依据的a/o、before/after O摘要、accepted对象/事件/work引用、输入时点与范围、原生缺口及全局false。拒绝行的accepted对象/事件引用为空，诊断只保留受限摘要。接受结果码分为 `COMMITTED_MATH_RECORD`、`COMMITTED_CONDITIONAL_RECORD`、`COMMITTED_COVER_PRESERVING_MODEL_TRANSFORM`、`COMMITTED_CONFLICT_RECORD`；重放的 `REPLAY_HISTORICAL_RECEIPT` 只存在于交付层。CAS版本不符用 `REJECTED_REVISION`；版本相同而base摘要不符用 `REJECTED_BASE_DIGEST`。覆盖/来源/数学校验/作用域/work冲突各有独立原因，详见结构化范围锁。

合成 revoke/release/late-result/third-grant/O-only/policy 事件由测试专用入口显式注入，使用同一世界事务约束：a+1、必要时 o+1；对应源/模拟权限和风险一起变化。它们只改测试世界，旧真实 grant/phase/spent/window 保持原字节和语义。管理 actor 的提交权与已撤回目标授权分别核对。

## 5. 覆盖与作用域

默认保留旧 O 并合并新项。允许的替换仅为固定规则：保留旧完整风险描述，或 `pending_source` 引用同库不可变旧描述并继承 origin/scope/依赖；再附加 close:u。validator 从旧对象内容和固定规则计算覆盖，提案的 covers 布尔值或 ID 列表无法单独建立覆盖。

H=0、F 空或负向单点观察都保留 Native 来源/未来创建/审计/窗口/效果债务。F 空仅保存冲突数学档案、investigate 项和原较宽责任。B 事件只影响自身责任。S3-A 所有回执固定原生缺口和全局未完成，允许级别仅 MATH_ARCHIVE、CONDITIONAL_ARCHIVE、COVER_PRESERVING_MODEL_TRANSFORM。

## 6. 路径与进程隔离

获批后的唯一执行根：`D:/毕业设计/research_g2_dsat_implementation/2026-11-10_r09_s3a`；数据库仅在 `synthetic_db/`，名称 `dsat_s3a_*.sqlite3`。SQLite 的 WAL/shm/journal 伴随文件同属该库的 owned 集合。运行时输出均进执行根，夹具仅进新增子树。`authority.db`、`.runtime`、真实配置/密钥路径均排除。

先验证绝对规范路径、批准子树和每个已存在祖先；重解析点/符号链接/身份变化直接拒绝。`sources/PATH_ANCHOR_REVIEW.json` 固定当前父目录 device/inode，执行前须重核。新文件采用排他创建并登记 creation ticket（规范路径、文件身份、instance、nonce、mode、schema）。仅可信 ticket 对应的已创建文件可用 read-write-existing 方式恢复；未知现存文件在连接及 PRAGMA 前拒绝。恢复核内部 application/schema/mode/instance；初始化中断的空壳拒绝使用并保留证据，后续选新 owned 文件名。

路径解析与身份快照依赖可信操作系统、受控排他测试根及无恶意本地主机；该条件下仍须在实际打开/清理前复核。`resolve()` 的一次结果无法独自承担检查后替换链接的安全责任。默认保留数据库/日志；清理只针对已登记 owned 临时产物，关闭全部句柄后按 LiteralPath 逐项检查，不跟随目录链接。

最多两个新测试子进程；Popen 使用独立句柄和登记的创建身份，Windows 隐藏窗口。终止操作仅作用于仍持有句柄的 owned worker，防止 PID 复用；无按进程名批量终止。超时/死锁关闭本轮新句柄并停止后续新工作，保留库和日志。
