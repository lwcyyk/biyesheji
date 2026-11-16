# PENDING生产路径完整审计

## Material Passport

DCL-R6-C09-PendingQuota-Closure；PendingQuota-Closure/review-1；2026-11-16（Asia/Shanghai，承接11月15日开始的审查）；冻结源码、历史原件、序列化代数与逻辑合同的静态审查。验证方式为 ANALYZED；原生动态验收未开展。

结论：**PQ-1=PROVED（冻结64对象、封闭原生调用域）**。唯一原生PENDING写入位置是[c09_handoff.py:277](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_handoff.py:277)，统一进入[c09_handoff.py:75](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_handoff.py:75)的event sink。全源AST和文本清单见[STATIC_PRODUCER_CENSUS.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-PendingQuota-Closure/evidence/STATIC_PRODUCER_CENSUS.json)，含所需全部生产者字段的13行矩阵见[PRODUCER_CONTEXT_MATRIX.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-PendingQuota-Closure/evidence/PRODUCER_CONTEXT_MATRIX.json)。

|producer_id|实际位置与进程|触发/状态变化|每次主日志追加|重试/并发/持久化|现行配额|
|---|---|---|---:|---|---|
|P01|Receiver.observe_exit，Root独立停止器，252–277|COMMITTED首次推进EXIT_OBSERVED；缺witness后保持revision4|1 CHECK，可为PENDING|H生命周期锁；同一Receiver反复进入；append/full write/fsync|缺少次数与总字节检查|
|P02|publish，85–89；Sender/Receiver/恢复scheduler|六类进度事件，各自前置状态见记录数证明|1 stage|同一生命周期锁；log先持久，随后state发布|依赖单次执行；崩溃重放需额外合同|
|P03|sender_prepare，189–196；初始Sender|持久COMMITTED回包核验成功|1 ACK|同锁；当前业务调用一次；等待连接不会重做ACK日志|缺少类别持久去重位|

[c09_handoff.py:79](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_handoff.py:79)使用Root0600、O_APPEND/O_NOFOLLOW、紧凑排序JSON和LF，逐行fsync；[guard.py:121](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:121)的_full只有一次os.write，短写抛异常。O_APPEND保护文件偏移，不提供配额原子性或崩溃事务。

|必须审查的上下文|源码与结论|
|---|---|
|初次/重复交接、重复task_id|[c09_handoff.py:172](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_handoff.py:172)拒绝已有handoff；[c09_handoff.py:221](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_handoff.py:221)只有PREPARING分支发布READY/COMMITTED，重复PREPARE返回既有commit。原生日志无task_id；重复对象是handoff_id，观察ordinal属于待批合同。|
|ACK等待、Receiver确认|[c09_handoff.py:138](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_handoff.py:138)的RPC/connect/send等待本身不调用event；错误回包含str(exc)，归入其他流字节缺口。|
|Launcher退出、waitpid|[guard.py:799](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:799)就绪pidfd触发观察；[guard.py:1225](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:1225)和[c09_handoff.py:297](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_handoff.py:297)产生独立waitpid/witness文件。它们不给PENDING自环收费。|
|超时、Root恢复、故障恢复|[c09_handoff.py:123](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_handoff.py:123)与classify期限拒绝；[c09_handoff.py:343](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_handoff.py:343)只增加RESUMED stage；[manager_recovery.py:251](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/manager_recovery.py:251)监督Root owner，不增加原生PENDING。|
|ManagerRecovery|[manager_recovery.py:51](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/manager_recovery.py:51)写mr_events；REVIEW_PENDING和mr_close_attempts均属独立生产族。PENDING字符串相近不构成同一sink。|
|STOP_REQUEST、CLOSED与异常清理|[guard.py:545](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:545)、[guard.py:749](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:749)及[manager_recovery.py:317](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/manager_recovery.py:317)写停止/MR/回收对象，不递归调用event。STOP可在在途检查后出现；CLOSED经H锁阻止新入口。|
|native seal前后|[guard.py:993](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:993)等待写者退出，TR检查关闭、角色退出与组空；封存仅哈希/复制，不产生PENDING。仅CLOSED存在尚不足以宣称源已静止。|
|行政finalizer|[startup_lifecycle.py:412](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/startup_lifecycle.py:412)只读导出；[startup_finalize.py:52](D:/毕业设计/DCL-R6-isolated-verification/ra01/host/startup_finalize.py:52)构造独立行政包。它们无原生PENDING写点。|
|C09H34|[c09_regression.py:59](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_regression.py:59)固定34 jobs/204事件/最大单job8步，输出各自JSON；[c09_oracle.py:42](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_oracle.py:42)核对收费。其synthetic PENDING和原生忙等路径分别计量。|

同一原生观察只调用一次event；另有首次EXIT_OBSERVED生命周期行。不同观察合法产生新CHECK；重试/恢复的重复追加风险须由持久token与禁止模糊重放条款约束。HANDOFF_FAILED只在STAGES声明，当前无原生publish调用。[H34_STATIC_INPUT_REVIEW.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-PendingQuota-Closure/evidence/H34_STATIC_INPUT_REVIEW.json)记录合成输入审查，本轮执行次数0。

历史8份原件逐字节匹配CalDiag原始导出锁；24行/27,144 bytes，17 PENDING＋1 VERIFIED＋6个前缀stage/ACK，未发生RESUMED。17条均同handoff/revision4，区间全局journal追加0行。[HISTORICAL_RECHECK.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-PendingQuota-Closure/evidence/HISTORICAL_RECHECK.json)保留实际原件路径、hash、直接锁核验及统计；这些数据只证明那次实际轨迹。


RESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
