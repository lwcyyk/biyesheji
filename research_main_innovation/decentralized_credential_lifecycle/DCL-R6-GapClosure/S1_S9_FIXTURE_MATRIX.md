# S1–S9 夹具矩阵

Material Passport：17 子场景 × safe/mutant = 34 job；输入与源码已冻结，实际运行 0 次。

每行生成“场景.safe”和“场景.mutant”两个 case_id。具体 task、请求绑定、原始初态和字节限制见合同 JSON。

|场景|故障或操作点|变异行为|独立预期违例|
|---|---|---|---|
|S1.before|before_reserve / exit71|early_grant|EARLY_GRANT|
|S2.unsynced|prepared.after_write / exit71|refund_prepared|RECOVERY_GRANT|
|S2.confirmed|prepared.after_dirsync / exit71|refund_prepared|RECOVERY_GRANT|
|S2.unknown|prepared.file.sync_return_unobserved / exit71|refund_prepared|RECOVERY_GRANT|
|S3.committed|committed.after_dirsync / exit71|reissue|RECOVERY_GRANT|
|S4.claimed|partial.after_semantic / exit71|reset_claim|DUPLICATE_CLAIM|
|S5.same|相同请求两次|duplicate_task|DUPLICATE_TASK|
|S5.conflict|同 task、不同 payload_digest|duplicate_task|CONFLICT_ACCEPTED|
|S6.concurrent|两 actor 的 start/request 屏障；变异另在读余额处同步|lost_update|RANGE_OVERLAP|
|S7.short|prepared.before_write，实际写入请求的一部分|ignore_short_write|ERROR_GRANT|
|S7.fsync|journal_prepared.before_fsync，适配器抛 EIO|ignore_fsync|ERROR_GRANT|
|S8.closed|claim 后设置合成 CLOSED|bypass_validity|INVALID_EXECUTION|
|S8.expired|claim 后设置合成 deadline 已过|bypass_validity|INVALID_EXECUTION|
|S8.boot|claim 后改变合成 boot_id|bypass_validity|INVALID_EXECUTION|
|S8.lock|claim 后改变合成执行锁摘要|bypass_validity|INVALID_EXECUTION|
|S8.restart|对已存在的合成状态/账再次初始化|free_restart|FREE_RESTART|
|S9.exhausted|N=4 后再尝试两次|allow_extra|LOCAL_OVERSPEND|

S2 的三个场景分别保存确认进度；S5 两种请求分别验收。S4 的局部重发可同时产生重复 claim 与局部超额，两项原始真值均保留。expected_violation 与 allowed_violation_set 预注册在合同中；其余违例产生 UNEXPECTED_RECOVERY 并阻断资源门。

## 原始观察

每 actor 独立 trace，包含 batch/boot/T0/源/执行锁/输入绑定、真实 PID/start_ticks、阶段事件与实际时钟。合成语义文件在许可返回后才写，检查器独立数操作、核对内容摘要和操作序号。counter、intent、journal、facts、故障快照、短写原始字节和父进程观察到的退出均保留。开始/结束时间可由 INITIAL/BEGIN、JOB_CLOSED 和 CLOSED 原始记录重建，结果摘要链接这些原件。

S1–S4 的预期崩溃用真实单个 worker 的 os._exit(71)；父进程先核验握手身份，再观察退出。S6 只使用主线程与同一个类型的单 worker。Controller 主线程＋监控线程＋Watchdog＋worker=4 tasks，没有新增并发测试线程。

## 静态资源上界

每 actor：事件≤256、语义写入≤5、reserve≤4、claim≤3、dispatch≤4、visit≤8、短写副本≤1。
每 job≤2 actor；setup/独立检查各一计费；34 job。
另含34次 root原始核查计费、18次资格门正反控制计费、RANGE入口1次：
34×[2×(256+5+4+3+4+8+1)+2]+34+18+1=19229。
RANGE真实主账硬限20000；原C00–C12最大37034，总校准硬上界57034≤100000。共同T0+300保持。运行耗时、fsync耗时与是否全部完成尚未测量，超界即停止。
