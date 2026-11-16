# Authority 读取、副作用与秘密边界

本稿的“逻辑只读”指本次调用对 Authority 世界行、版本 a、authority_events、业务预算/phase/旧 O 的写入数为 0。操作遥测、宿主 permit 消耗、审计记录、锁等待、文件系统访问与实际时间分别登记。

## 1. 七类操作

| 操作 | 当前源码事实 | 本轮处理 / 后续边界 |
|---|---|---|
| 文件和配置静态检查 | 源码/Schema文本和文件 hash 无业务 DML；读取也可能影响 atime | 本轮仅限定源码与历史证据；运行配置/secret目录未读 |
| 新 SQLite 只读连接 | 当前 Store 使用普通 rw/c connect；独立 mode=ro 需另加实现 | 本轮连接数0；推荐方案复用既有连接 |
| Store 对象初始化 | mkdir、rw连接、WAL/PRAGMA、migration0/1→2、genesis、marker、storage_configuration | 读取入口全面避开构造器 [S01:47–91] |
| 可信解密 | cipher 每次重新读32字节 key；AES-GCM 解密整份加密行后 JSON 解析 | 一次 B1 可触及整库明文，需独立批准完整解码域 [S01:103–120] |
| 当前 a 读取 | 同一 SELECT 取得 version/ciphertext；execute 先计数和写日志，再执行语句 | 一次配对快照、读操作额度及日志 fsync [S01:93–120] |
| B1 构造 | 已绑定 context/scope、持 reader.lock，核原请求并白名单投影 | 纯净化过程复用原字节；大小界在构造后检查 [S05:417–468] |
| 净化出口 | Schema闭合、脱离源对象；额外宿主摘要尚待实现 | 首期仅管理宿主；无 Agent/IPC/全净化快照落盘 |

`recover` 是 `AuthorityStore.call` 中的特殊分支，没有独立的 `AuthorityStore.recover` 方法。该分支执行一次 read_state 并返回旧投影，世界版本保持，遥测和 key 读取发生。[S01:122–133] Controller.recover 进一步写缓存、日志并进行网络调用。[S02:70–79]

旧统一 call 除 recover 外，正常返回后统一 UPDATE a+1、event INSERT 和 COMMIT；reconciliation_context 也经过此路径，release 的某些拒绝还会 CANCELLED/reserved--。[S01:134–159,227–250,370–395] B1 的任何拒绝、重复和缺口结果均绕开这些旧分派。

## 2. A/B/C 方案比较与唯一建议

| 项目 | A：旧 recover / 旧读方法 | B：独立 ro 连接与解码器 | C：已初始化 Authority 宿主调用 R12 |
|---|---|---|---|
| 初始化/迁移 | 复用已存对象时无；重新构造时会写 | 可避开构造器，但需新连接合同 | 不构造；源对象必须已存在 |
| 一致状态 | recover 内部一次配对，但对外旧投影信息不足 | 可在恰当事务/查询中配对 | R12 一次 read_state 配对 |
| a/event | recover 特例不改；误用旧普通 call 会改 | SELECT合同下可保持 | 固定读路径，没有世界DML |
| key与原请求 | 源内可得；对外旧投影缺原请求验证材料 | 新组件需 key/codec访问，扩大处理面 | 保留既有可信 key读取域 |
| 文件副作用 | SQL遥测、传输、Controller缓存/日志 | mode=ro/WAL/SHM/VFS/atime仍需分析 | SQL遥测/fsync、key文件访问、宿主审计；物理零变化无保证 |
| 并发/旧writer | 实例锁；跨连接按SQLite快照 | 独立连接按SQLite快照，额外部署责任 | 同实例锁；其他连接仍可能后续写 |
| 权限 | 旧服务级能力宽；scope字段不足 | 需独立解密与管理权限 | 新内部精确tuple守卫，首期管理者 |
| 修改量 | 为补字段需改旧投影/RPC | 新读连接、codec、事务与WAL测试 | 新宿主模块＋离线测试；R12原字节复用 |
| 裁决 | 可作旧协议参考，完整B1接线仍缺字段 | 保留比较，不推荐本阶段实施 | **唯一推荐，先H1** |

C 的具体操作是让宿主直接调用 `read_dsat_authority_snapshot(existing_store, scope, context, limits)`，由 R12 在锁内执行唯一一次状态读。先预取 state 再调用 R12 会造成重复读取；调用私有 `_project` 则绕过公开适配器的来源、配额与错误处理。两者均移出本期方案。

## 3. SQLite 机制限定

- `mode=ro` 负责新连接的访问模式；URI 需要正确启用和转义。[SQLite URI §3.3](https://www.sqlite.org/uri.html)
- WAL 只读数据库的可打开性取决于 SQLite 版本、现有可读 WAL/SHM 或相关目录条件。逻辑读和锁/共享内存/文件行为需分别检查。[SQLite WAL §5](https://www.sqlite.org/wal.html)
- `query_only` 阻止数据修改语句，checkpoint/COMMIT等仍有各自效果；它会改变连接设置。推荐 C 保持业务共享连接配置原样，避免给旧 writer 加上 query_only。[SQLite PRAGMA query_only](https://www.sqlite.org/pragma.html#pragma_query_only)
- `immutable=1` 假定底层文件保持不变并跳过锁和变更检测。活动数据库继续使用正常并发路径，单独 immutable 打开不提供所需合同。[SQLite URI immutable](https://www.sqlite.org/uri.html)
- 单行 SELECT 给出同一语句的版本/密文配对；独立连接可继续提交。相同连接内的读写隔离需要正确串行化。[SQLite isolation](https://www.sqlite.org/isolation.html)

这些官方资料的定向阅读和本地快照在 sources。运行时库版本和 VFS 尚未测量；本轮无 SQLite 导入或连接试验。当前构造器设置 WAL，并使用同一 connection/check_same_thread=False；因此 H1 规定所有访问复用实例 RLock，读取前要求 `connection.in_transaction == false`。若出现遗留事务，固定拒绝并交管理者处理，读取路径不替他人 COMMIT/ROLLBACK。[S01:51,60–67,127–159]

`in_transaction=false`仅检查相应事务标志，连接上未释放的SELECT cursor仍需单独考虑。接线前提还包括固定宿主调用路径无遗留cursor、无回调重入读写、无任意SQL扩展；这是部署和源码封闭性责任。H1的布尔替身测试只覆盖显式事务拒绝规则，真实连接状态保持H2待验。

## 4. 真实秘密流与出口

```text
已存在的AuthorityStore引用
  → 宿主身份/读取权/精确tuple/次数/时间检查
  → 已有连接的一次read_state
  → 既有key_path一次读取与整行AES-GCM解码（Authority可信域）
  → 原完整请求摘要/handle/grant/origin私有核验
  → R12新建净化对象、闭合Schema、保守缺口
  → 宿主最小摘要白名单
  → 经批准的管理者与最小审计文件
```

R12 原始 handle 参与完整请求 digest 和 grant/origin 等式；公开数据保留既存完整 request_digest，handle、独立 handle hash、原正文及材料内容均被扣留。[S05:258–309] 内容摘要只固定版本；当前主机可信性、身份发行和授权事实仍由宿主提供。

### 秘密隔离责任矩阵

| 材料/出口 | 所在域和处理 | 尚需真实证据 |
|---|---|---|
| authority.key | 当前 Store 每次cipher读取；新宿主只借现有方法 | 路径、所属进程、ACL、key版本及使用批准 |
| 整份解密 state | 单加密行导致所有scope内容同时进入Authority内存；仅投影获准tuple | 用户明确同意整行瞬时解码；其它scope禁止导出；若要求解码也只限task，则当前格式缺条件 |
| 原handle/密码/token/client secret/私钥 | 留在源内；宿主不创建新长期缓存、副本、临时明文或IPC | 实际字段域兼容、进程权限与部署日志策略 |
| 正常响应/JSON | 新摘要仅含批准字段；R12完整净化对象仍属内部 | H1白名单/深拷贝/容量；H2实际sink检查 |
| 拒绝/异常/堆栈 | 固定错误码和执行引用；异常对象、args、cause、局部变量和repr均留在边界内 | H1含canary故障注入；运行框架的全局debug/崩溃转储政策另核 |
| 调试表示/缓存 | 上下文禁序列化，结果仅白名单；原state无新缓存 | Python内存无法保证立即清零，GC引用释放不作安全擦除保证 |
| 日志/临时文件 | 仅码、计数、字节数、受批摘要；失败同样执行出口限制 | SQL日志I/O故障也可发生在真实SELECT之前，单次额度仍可被消耗 |
| IPC/Agent | 首期出口限定Authority内部管理域；Agent出口空 | 未来RPC/委托scope/撤回与复用需另审 |

R12 闭合 Schema 防止未知字段进入净化输出；允许字符串字段仍需要真实语义与敏感性核对。固定字段名无法证明任意真实 identifier 内容均可公开。因此首次 H2 摘要省略所有 grant/rid/handle/原请求摘要/原生ID，敏感值扫描在可信域内完成，只导出结果码和计数。

现有 isolation_service 会写诊断文件，并在 ImportError 分支保存错误字符串；CLI.request 通过 Laboratory 加载全部角色配置。[S09;S06] 本期 H2 执行路径须单独冻结异常与日志策略，避免借这些初始化入口取得管理资格。

## 5. 可靠 revision、并发与当前性

设读语句所见快照为 `(a*,W*)`。B1 内全部 grant/request/disposal/window 校验来自 W*，authority_revision=a*，因此得到一次同源局部观察。`read_clock.lower/upper` 包围源读，不包围后续全部投影和网络交付；epoch 来自宿主登记，Native有效期为 UNESTABLISHED。[S05:441–458]

同实例用户撤回、release、record迟到结果、新grant均经过 RLock，位于本次受锁处理之前或之后。其他 Authority 对象或旧连接的写入可在 SQLite 允许的时点提交。快照仍可一致，但返回时可能已有新 a。跨进程写入覆盖、回滚、复制库身份和 key 生命周期保持独立前提。

AS 异步创建、旧 Refresh 延迟插入、外部持有者和 Provider日志变化不受此锁约束。即使读前后本地a相等，`native_currentness_status=UNPROVEN`。B1出口维持 math_ready=false、current_native_eligible=false、global_complete=false、authority_write_action=NONE，且不包含 O消解、native-close、新grant、issue、refresh、revoke 或 B2入口。

## 6. H2 单次调用的验证费用边界

为核验真实调用的逻辑副作用，需要独立的读前/后观察。最小计划冻结为 **一次 B1调用、最多4条源SQL、一次key读取、自动重试0**：

1. 只查询 `PRAGMA user_version`，期望1或2；0/未知值拒绝，保持无迁移。
2. 一条读前 SELECT 观察 a、密文长度及有界密文、authority_events count/max。超过16MiB只返回长度与越界码，停止解码。密文在可信域内比较，禁止导出。
3. 原 R12 的一次 SELECT version,ciphertext 与一次既有解密。
4. 一条同形读后 SELECT；比较 a/密文/event计数和最大版本，同时比较 connection.total_changes。外层保持同一 reader.RLock，排除本实例写入夹入。

读前后 event count/max 无法独自排除任意外部重写；须结合固定查询白名单、无DML/调用路径和部署writer前提。其他连接造成变化时记 `INCONCLUSIVE_CONCURRENT_CHANGE`，保存最小元数据后结束，世界回滚或自动重试均不执行。

四条语句均计入 execute 的日志及 operations。进入序列前要求 `operations+4+6<=operation_limit`（有限时）；R12内部的一读+6余量门继续原样。headroom仅保留一轮旧writer预检空间，读取消耗的4个额度与锁等待可能影响后续活性，需要明确批准。旧6操作规则也不保证无限后续任务。

首次H2的无DML验收依赖空闲连接、固定代码、标准表/无任意扩展、批准的安静观察窗口及已盘点的源；全量文件hash或主db mtime不充当世界写入证明。WAL/SHM/atime和遥测允许独立物理变化。

以上为设计，SQL和解密均未执行。10秒为软期限：超过后丢弃结果并标记超时；同步fsync/文件系统阻塞可能延迟返回，禁止以杀死Authority进程强行满足期限。需要硬期限或更强资源保证时另审运行策略。
