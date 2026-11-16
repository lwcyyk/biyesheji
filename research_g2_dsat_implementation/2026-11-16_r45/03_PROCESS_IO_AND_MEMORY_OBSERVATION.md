# I/O、内存与父进程成本

ResourceObserver提供CHILD_PROCESS_IO、JOB_AGGREGATE_IO和SUPERVISOR_PROCESS_IO三个有来源的快照。父API调用次数、静态输入读取字节、pipe读取量和witness charge/confirmed作为SUPERVISOR_OVERHEAD单独记录。

IO_COUNTERS保留ReadOperationCount、WriteOperationCount、OtherOperationCount、ReadTransferCount、WriteTransferCount、OtherTransferCount。Job使用BasicAndIo信息类8，扩展限制结构中的IoInfo保留字段未作为I/O数据源。

进程、Job和父进程计数都有真实时间范围，child与Job存在覆盖重叠，JSON逐项保存。全程初始值和最终值分别存在，模型API、内核事件及物理磁盘计数口径各自标注。ETW字段固定NOT_ENABLED，FULL_IO_COUNT_PROVED和PHYSICAL_DISK_IO_PROVED均为false。

## T20

T20的源调用保持State.observe_result(A01,PASS,1000000)。父进程Windows会计支持child生命周期资源观察，准确的T20主区间标记仍依赖Driver证据桥接。R43聚合和末态witness之外的逐事件内容未由本轮新增代码补造。强制终止前的内存case状态继续UNKNOWN。

## 内存

process快照分别保存PeakWorkingSetSize、WorkingSetSize、PrivateUsage和PeakPagefileUsage。Job保存提交峰值及历史进程峰值，当前JobMemoryUsage保留UNKNOWN。父进程使用自身伪句柄查询，峰值比较用独立批准的父额度。

live阶段内存查询失败使监督失败。确认退出后的查询失败保留last-good数值及QPC覆盖终点，尾部未知。SIMULTANEOUS_TREE_PEAK保持UNKNOWN，个体峰值没有被相加成实测同时峰值。

## 持久化与当前数据

普通观察、pipe数据和最终receipt进入一个SHA链JSONL。写入前全长扣费，完整write/flush/fsync之后推进确认字节和链头。部分/未知持久化使流Poison，保留此前确认前缀。

最终receipt在自身close之前写出，因此cleanup_status仍为CLEANUP_UNCONFIRMED，已完成的API句柄清理另有字段。最终文件关闭与父退出状态需要外部观察。所有实际计数当前为NOT_MEASURED或UNKNOWN。
