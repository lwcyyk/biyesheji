# 32191次预留的语义与来源

Material Passport：离线ledger/source审查；原visits.bin、journal、intent逐字节保持。32191 PREPARED与32191 COMMITTED连续配对，无序号/容量错误，最终intent COMMITTED/after32191。CSV及计算在[evidence/JOURNAL_STATS.json](evidence/JOURNAL_STATS.json)、[来源拆解](evidence/BUDGET_SOURCE_BREAKDOWN.json)。

|来源|序号/数量|真实依据|
|---|---|---|
|C00入口|1：1次|单次run_case.visit，C00结果counter1；首PREP400.326142307|
|C01入口|2：1次|正常结果counter2；PREP400.647849473|
|C02入口|3：1次|源码先visit再分支；其后PREP4证明入口已返回|
|C02子操作预付|4…32191：32188次|串行prepaid_child的visit循环，独立服务未交叠且子探针未进入|
|监督/轮询|0次budget reserve|W/监督线程只读状态/写心跳，不调用Budget.visit；它们仍占时间/内存/task|
|重放/恢复/模型/其他case|0|源/运行记录均未达，resume_count0|

journal自身未记录PID/case，来源是**时间线＋冻结串行调度＋调用图推断**；不将其表述为日志自带标签。Global counter是持久占用高水位，包含未来任务预付，F1/F4实际状态展开0、内存子操作0。原账不减，不回收未用预付。

## 真正的状态流

调用顺序：检查/加锁→写PREPARED意图并同步→追加PREPARED并同步→counter+1并同步→追加COMMITTED并同步→COMMITTED意图/目录同步→解锁/返回grant→上层继续。原实现没有逐操作SETTLE、消费ACK或退款；ABORT时保守烧掉已占用额度。

COMMITTED代表事务记录状态，不能直接证明对应业务EXECUTE。下一PREPARED证明前一顺序调用已返回，因此已返回grant的保守边界为32190…32191；最后一项缺显式return事件，记录UNKNOWN_INTERVAL。C00/C01的probe取样在visit返回之后，另有实际返回证据。

父程序需预付全部最大子操作后才启动allocator。按锁定x86_64 Linux的4KiB基页静态合同，C02最大128次分配＋128×256次触页=32896；截至关闭只付32188，差708。SC_PAGE_SIZE返回值未单独记录，4KiB为静态平台推断，应在后续诊断补记；不能仅凭缺child_process.json断言未启动，因为该文件本来在子进程返回后才写。这里用预付不足、冻结控制流、后续case未达和文件缺失共同定位。

总量关系：模型执行E_model=0；内存子操作E_child=0；durable占用D=32191。D与实际消费之间缺独立消费日志，不能把32191登记为已处理模型状态或已触页数。不存在同一信用在本批日志中被重复分配的证据；PREP/COMMIT两条是同一事务两状态，不是两次访问收费。

当前超额保护在global锁内检查1,000,000；cal软阈值100000的预检在锁外，未来并发边界需要单独加强为同一锁内检查。此次32191距离该边界很远，此潜在软阈值竞态与本次停止无关。
