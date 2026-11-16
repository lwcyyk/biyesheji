# 时间计量修订
Material Passport：BF-static-1 / STATIC_REVIEW；新遥测实际运行次数0。

## 时钟与保存
CLOCK_BOOTTIME的整型纳秒用于持续时间，覆盖Linux挂起；time.time_ns()用于UTC相关绝对记录，两者分别保存。旧stamp仍带boot_id与BOOTTIME秒值。跨boot比较被拒，UTC可跳变，耗时统一由BOOTTIME差计算。

_TIMING按固定阶段名保存count、total_ns、min_ns、max_ns、errors、first_samples最多8项及last_sample；样本有begin/end_boottime_ns、begin/end_utc_ns、duration_ns和error。长度随固定阶段数有界，随访问次数保持常数级存储；int大小随计数增长。没有计算全部fsync的P99，早期8项和末项无法代表完整分布。

timed在调用前取样，finally记录返回/抛异常后时间。系统调用包裹区间含微小Python计时/调用开销，不能由其反推存储设备独立物理延迟。file与directory的fsync分别命名；编码、write/pwrite与锁等待分别命名。操作系统/文件系统/WSL宿主持久化合同仍是证明前提。

## 测点映射
|阶段|源码点|解释|
|---|---|---|
|reserve.request|_reserve入口|请求事件；在锁前|
|budget.lock_wait|RLock+flock取得后|从申请锁至取得锁；持有锁后的合同校验另属路径耗时|
|budget.intent.prepared.encode/write/file.fsync/directory.fsync|atomic(PREP intent)|各阶段开始与返回/异常|
|budget.journal.prepared.encode/write/fsync|_append_journal(PREP)|PREPARED日志真实写入边界|
|budget.counter.write/fsync|pwrite与sync_fd|计数更新与同步分开|
|budget.journal.committed.*|counter同步后新stamp及COMMIT日志|stamp对应COMMIT记录构造，最终intent的持久完成另有测点|
|budget.registry.reserved.*|精确范围事实|新增两个同步屏障|
|budget.intent.committed.* / reserve.committed_barriers_done|最终intent屏障及紧随其后的事件|已完成全部预留同步；后续deadline再检查|
|local_credit.dispatch_once|首次新对象派发|仅派发事实；child尚须claim|
|budget.registry.claimed.* / local_credit.granted_to_executor|child一次认领持久化/局部对象完成|实际child正文已运行的证据|
|local_credit.debit|LocalCredits.visit|身份、父/期限检查、等待局部锁及扣减的包裹耗时|
|child.spawn_request / child.wait_return|父进程subprocess.run前后|申请exec和观察wait返回；child实际退出内核指令时刻仍未知|
|single_credit.grant_emit|普通visit成功返回前|单信用路径可区分预留与发放|

## 输出与缺失
Controller finally写case.timing.json一次，child在child.json写其聚合；最后输出自身的编码/同步发生在快照之后，单独视作未包含的收尾开销。心跳、普通结果写入及初始化等也有metadata统计，输出同步机会单列。进程强杀、崩溃、未进入finally、输出MemoryError会丢失部分或全部遥测；原残片保持，缺失写UNKNOWN_INTERVAL。C06–C09故障退出本就可能缺少最终聚合，禁止以缺失推定零耗时。

父进程的observed_process_span_ns包括创建、调度、child执行和wait返回；若subprocess.run抛异常，则终止与异常由既有外层停止路径处理，该成功返回遥测文件可能缺失。未来应同时核对持久claim、child结果、exit_code与管理器信息。新COMMITTED不会沿用PREPARED时标，旧batch02日志保持原字节。

## 可证伪验收
后续独立授权后核对：C02范围事务1次、child claim最多1次、N=32896、额度覆盖；分阶段计时可加总并用请求至grant的总跨度检查剩余间隙；fsync错误样本、遥测缺失、突变UTC、boot变化分开登记。校准仍须在共同T0+300内完成；单项耗时改善与资源资格分别裁决。
