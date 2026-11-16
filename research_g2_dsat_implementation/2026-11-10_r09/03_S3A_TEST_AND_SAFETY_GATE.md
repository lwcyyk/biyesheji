# 46 项测试与安全验收门

全部为未来执行规格，`NOT_RUN`。本轮没有创建测试模块、数据库或启动测试子进程。完整逐项操作与预期在 `S3A_TEST_MATRIX.json`；原 R08 ID、名称、期望及来源定位保留。

## 1. 执行口径与输入

46 个顶层 ID：NORMAL 5、CONCURRENCY 10、OBLIGATION 8、CRASH 14、ADVERSARIAL 9。子断言单独报告，顶层分母固定。某项所有必需子断言成功才记 PASS；缺少真实恢复证据记 BLOCKED/NOT_RUN，预期安全拒绝由精确 reason/state 断言后可记 PASS。禁止用总 PASS 数替代覆盖范围。

输入来自按哈希固定的旧 A01–A24 合成夹具、R07 的 23 份 AUTO 证明及既存 `VAR_MISSING_D_A.json`；新副本与变体只写新增夹具目录。T019 使用该既存变体，其原声明为 R=0/H=1；A16 的实际声明为 R=2/H=3，仅用于单点负向观察的检查。可信测试 actor 为 `syn:manager`，权限在 runner/测试世界建立，body 自报身份/权限不产生信任。一般初值为独立实例 a120/o0；ID 使用 `r09:Txxx:variant`；每项创建独立库。旧原件、旧115用例和25夹具保持。

种子保守保留 fixture 原 O 及完整描述。可信冻结投影清单以 R07 输出/fixture 关联建立；独立 checker 重新读取这些精确包，检查 source/packet/math/scope/dependency 摘要。证明生成、NetworkX 和 S1/S2 重算不列入执行范围。

## 2. 四表 oracle 与关键断言

独立测试 oracle 直接读取新库四表并计算规范摘要、引用可解析性和固定期望风险集；它与 store 的 coverage/commit helper 分开编写。覆盖期望采用手写小输入的完整描述与风险组件，避免测试再次调用生产覆盖函数得出同一结论。既有数学独立检查器只承担数学包范围。

成功：world/event/objects/proposal/receipt 全齐、a 恰增1、o 仅在成员/覆盖/状态/依赖改变时增1、work逻辑费用去重。拒绝：world 的精确规范字节及 a/o/O、events、objects 相等，只有合法拒绝提案行可新增。重放：四表和原 receipt 字节保持；delivery 元数据单独检查。崩溃：重开 SQLite 后只能观测旧提交或完整新提交；K8/K9分别锁定前后两种情况。

A08 必测：数据库读回原五项，投影/包各六项且新增 `close:c2`，原 origin/隔离责任保留，默认 O_after六项。

A24 必测：数据库五项、投影/包六项且新增 `await_terminal:i1`；H=0 只存条件档案，await/window/effect/native前提继续待结，`global_complete=false`。两例分别计算 base 与 proof 摘要，允许且要求实际差异得到保留。

## 3. P1–P10 对应（采用 R09 编号）

R08 的 P 编号部分不同。本轮以下编号为唯一测试映射；R08 原性质原文继续保留。

| 性质 | 主要测试 ID | 输入、验收 |
|---|---|---|
| P1 世界原子性 | T001,T003,T031,T032 | 版本+O+对象+历史+回执整体；COMMIT前后握手 |
| P2 责任覆盖 | T016–T022,T036,T042 | 未知/歧义、部分转换、迟到、空F；逐组件保留 |
| P3 严格CAS | T006–T014,T039 | 双提案、所有合成writer和各摘要；旧base只入拒绝簿 |
| P4 持久幂等 | T002,T013,T015,T032–T034 | 同体/异体/异owner/ACK丢失；原持久结果稳定 |
| P5 不可变历史回执 | T002,T012,T032–T035 | 已失当前资格仍可按历史读权读原回执；无权不披露 |
| P6 费用去重 | T002,T003,T023,T031–T034 | 跨新ID重用同work去重；异body费用冲突；实际工作另计 |
| P7 证书范围 | T004,T005,T019,T020,T038,T043,T045 | 数学/条件/原生分层；改包、错误强关闭拒绝 |
| P8 崩溃恢复 | T024–T037,T046 | 前置模拟与真实事务kill分别取证；坏schema/codec安全拒绝 |
| P9 旧系统隔离 | T015,T021,T040,T041,T046 + 全局哈希门 | 全部旧字节保持，进程/路径/导入闭包受限 |
| P10 原生当前性边界 | T010,T014,T035,T044,T045 | 外部模型变化不经本地版本；始终保持原生缺口/全局false |

## 4. 并发与故障注入

C1–C10 原10场景分别映射 T006–T015。采用新子进程/连接和显式 barrier，按握手释放顺序复现并发；禁止用 sleep 碰运气代替排序证明。撤回、迟到、第三批准、O变更与策略变更只用合成 domain 事务。C5的 AS 变化仅更新独立测试模型，结论限定为原生资格未授予；实际 Casdoor 原子性仍属 S3-B。

K01–K14 分别对应 T024–T037：

| K | 后续执行方式和证明范围 |
|---|---|
| K01–K06 | worker 在冻结快照/部分证据/投影/未交付求解结果/固定proof/检查结果交接边界停下；世界未提交。K04 为边界模型，未终止真实流求解器 |
| K07 | 新 worker 在 BEGIN 前握手，父进程终止后重开 |
| K08 | 真实 SQLite worker 在同一事务写入对象、部分世界更新等后，COMMIT前握手；分别切在多处 SQL 边界，父进程终止并重开 |
| K09 | worker 完成 COMMIT且返回成功后发握手，ACK前父进程终止；重开后同ID/body得原receipt，逻辑费用/事件各一次 |
| K10/K11 | 在 K09 的持久状态上测试同体/异体重放；历史、a/o和O保持 |
| K12 | 重开后推进合成逻辑时钟；原历史可读，新current-required提案过期拒绝，历史策略显式绑定 |
| K13/K14 | 重开后注入合成迟到/撤回事务，再提交旧提案；新责任和原origin保留 |

只能终止本轮新建并持有句柄的合成 worker；不会调用 Controller/Provider/真实 API。kill测试覆盖进程突然退出；机器断电、存储设备虚假fsync、恶意DB整体回滚、主机受攻或多主分叉另列为模型外。

## 5. 资源界与失败门

沿 R08：proof4MiB、world8MiB、O1024项、风险组件4096、持久proposal ID256、revision≤`2^63−1`。补充冻结：总proposal8MiB、单receipt256KiB、单event1MiB、每提案新objects合计8MiB、JSON深度32；数学输入沿1MiB和既有attempt/witness/edge上限。拒绝前检查大小；checker上限4MiB且单worker10s，超限返回资源结果。

每库新建4096字节页、max_page_count=16384（64MiB逻辑主库），WAL/FULL，busy_timeout1000ms；显式SQL事务以短读者和单次提交为准，自动重试0。单worker10s、最多2并发、整次suite180s；超时保留分母并停止新工作。

WAL64MiB、shm4MiB、整执行根256MiB为监测停止阈值，按受控writer/reader检查；值达到后先停止新写，等待/终止 owned readers，再作受控checkpoint，失败保留文件并退出。`journal_size_limit`、autocheckpoint和监测本身都不提供严格的WAL瞬时硬配额；操作系统/文件系统磁盘耗尽可能先发生。所有这种错误都走安全状态/未知持久结果处理；该限定属于验收预期。

新ID容量满：已有ID查询先执行，新工作拒绝且不淘汰tombstone。revision将溢出：事务拒绝，原值保留。work ID同内容仅记一次；同ID异内容拒绝。无法写入拒绝记录时报告 `REJECTION_NOT_PERSISTED`；COMMIT异常时报告 `UNKNOWN_COMMIT_OUTCOME` 并用同ID查询；不把未持久结果声称成已绑定。ID保留期覆盖该instance的整个测试生命周期；默认保留整个库和日志。

上述边界/越界、满簿重放、版本耗尽、重复键/浮点/布尔整数、坏schema、未知现存文件、链接路径、导入副作用作为 T001/T015/T023/T038/T046 的强制子断言，仍保留46顶层ID。

## 6. 执行退出门与费用

授权后必须记录：全部46项逐项结果、P1–P10覆盖、K8/K9握手/child身份/退出码/重开四表快照、A08/A24四份O摘要、并发实际排序、checker结果、旧字节哈希、新文件manifest、资源超限与失败日志。

费用拆为 prepare/read、checker、coverage/hash、lockwait、SQL/COMMIT、reopen/recovery、receipt/replay；记录wall time、输入字节、对象/DB/WAL大小、逻辑work引用和实际尝试次数。S3-A无新S2求解，复用费用说明其历史来源；崩溃最后一段耗时无法精确恢复时标 `NOT_MEASURED` 或区间。C_native本阶段 `NOT_APPLICABLE`，旧成本保持历史标签。

完成条件为所有要求断言实际执行且通过，安全预期拒绝也有精确证明。失败可在已批准新增文件内作最小修复并保留每轮日志；需要旧文件修改、真实服务、更多依赖或范围扩张时停止重新申请。S3-A完成后仍只产生合成事务/恢复证据。
