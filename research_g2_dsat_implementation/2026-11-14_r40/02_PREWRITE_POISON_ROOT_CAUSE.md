# Write前拒绝的真实根因

当前源码存在三个宽泛Poison处理点。其中两处包装器对检查点异常直接设置Poison；第三处将受保护write之前的截止拒绝也纳入持久化未知。

| 位置 | 实际行为 | 问题范围 |
|---|---|---|
| `commit_case_record` 653—672，尤其663—668 | 用 `WRITE_ATTEMPTED_BYTES` 增量选择记录FAILED或UNKNOWN，随后只要ledger存在就Poison | 已判为零write的FAILED仍触发Poison |
| `safe_checkpoint` 892—901，尤其899 | 任何检查点异常都Poison现有ledger | 没有本次调用边界分类 |
| `io_write` 1003—1029，尤其1005、1008、1023 | 先设置WRITE_STARTED；截止检查在实际write之前；except统一Poison并标UNKNOWN | 零payload-write且已经扣费的截止拒绝也会走此分支 |

`Poison`在这些处理器中由异常进入路径和ledger存在性触发。异常类型没有承担可靠的副作用分类。`commit_case_record`的字节增量仅参与结果状态选择，未限制Poison触发。

## 检查、扣费、write与确认的实际次序

`checkpoint`在831执行路径检查，832取得现有RLock，833—835检查关闭/尝试上限并消费一次构造尝试。836—847完成字段、压缩、完整行和public sink检查。848调用 `reserve_bytes`。

`reserve_bytes`首先在973—975检查90秒工作或115秒terminal截止。此处失败尚未扣费。976—981检查路径并在terminal时消费一次terminal尝试。982—987建立或取得ledger；988先拒绝Poison。990将工作Journal cap设为983040，terminal仍为1048576。991—992检查本次长度和总charge，失败同样尚未增加字节charge。

993—995的可见extent检查承担所有权前提。它失败时，即使新payload-write为零，健康前缀也已缺乏可信依据。996—998增加SERIALIZED/charged并改变状态；1000才做全局检查。普通不变量成立时，逐文件caps之和小于2MiB，因而这个末端全局guard通常由原不变量推出；若实际触发，须审查账本一致性，维持保守处理。

848之后，849—852可能首次exclusive创建文件并取身份；853—856检查dev/inode、文件长度及tell与旧Journal状态。857才调用 `io_write`。1008又检查截止；1009—1010在实际调用前增加尝试计数；1011调用 `stream.write(data)`；1013核对完整返回；1015、1018分别为flush/fsync前截止检查。1019 fsync返回后，1020—1021更新已确认字节与PUBLISHED。checkpoint858—860再逐项推进seq/head/Journal长度，862返回确认引用。

因此：

- 975、992的指定同步拒绝可由实际控制位置证明发生在扣费及payload-write之前。
- 1008的指定同步拒绝发生在扣费之后、payload-write之前；已有费用保持。
- `WRITE_STARTED`这个现有字符串不能单独证明实际write已开始。
- 字节尝试计数的递增早于调用本身。它是保守记账，实际调用与计数分别记录。
- 只看异常代码、errno、异常类别或零字节增量，无法排除所有权故障、旧状态、ACK间隙或部分账本更新。

## 收尾预留为何被阻断

原Journal总cap1048576，工作cap983040，其差65536是原独立保护的收尾headroom。该身份通过阶段选择cap实现，缺少一个可随意重置的“新授权账户”。其他三份最终JSON共655360，receipt65536，合计原收尾份额786432，均已包含在13文件caps中。

在975或992零扣费拒绝后，旧前缀与这65536字节身份保持。包装器随后Poison健康ledger。下一次合法terminal调用先在981消费一次原有terminal尝试，然后988以 `EVIDENCE_STREAM_POISONED` 拒绝，尚未审查可容纳的字节长度。空间保留但提交资格被错误关闭，形成局部阻塞。

“收尾仍有空间”只证明空间条件的一部分。其调用同时受115秒、32次terminal预留、8320次checkpoint构造、原路径、所有权和表示合同约束。原生I/O与调度可晚返，120秒是原关闭准入边界。

## 分类与修复范围

本轮冻结正交分类：I/O阶段、前缀可信性、提交确认、预算状态和整体验收状态分开记录。BEFORE_IO专指受保护payload-write之前，路径stat等元数据读取可能已经发生。

安全保持健康需要同时具备：本次调用的新鲜匹配状态、已验证健康的现有独占Journal、明确的同步事前拒绝位置、write可能开始边界尚未跨越、完整保留已花费用、缺少任何身份或账本未知。未知或冲突继续fail closed。任何Poison真值都保持单调，本次修复只避免错误的新转换。

只改两个包装器无法处理1008的内层Poison。冻结申请因此精确增加 `checkpoint`、`reserve_bytes`、`io_write` 三个边界传播函数。未来单独授权需覆盖同一个Runner的这五个函数及至多一个有界局部helper。当前实际源修改0。

全局 `persistence_ok=false`、原失败事实、停止测试和完整验收失败继续成立。保持Journal健康使独立合格的既有收尾动作仍有机会提交；原失败记录保持FAILED/UNKNOWN，原授权、失败尝试和已扣字节均保留。
