# G2-R46：T20全程I/O与90/115/120秒准入

逐项合同见 [R46_T20_FULL_IO_ACCOUNTING.json](R46_T20_FULL_IO_ACCOUNTING.json)、[R46_MEMORY_AND_PROCESS_TREE_BUDGET.json](R46_MEMORY_AND_PROCESS_TREE_BUDGET.json) 和 [R46_DEADLINE_COST_MODEL.json](R46_DEADLINE_COST_MODEL.json)。

## T20边界与分层成本

主操作继续为 `State.observe_result(A01,PASS,1000000)`。Driver596–624先准备观察/故障、取snapshot，606行调用，随后核验保留的原结果、持久知识与零write记录，再进入RECOVERY。T20两分支的原期望保持；本轮静态保留该边界，实际执行状态为NOT_RUN。

| 成本 | 边界 | 与其他项的关系 |
|---|---|---|
| C_MAIN | 上述单次调用，退出于原拒绝判定 | 精确主操作范围；原零write断言仍按原规则 |
| C_SUT | Runner被选择的MODEL Journal和状态操作，含相应setup/main/recovery | Child内SUT归属，MODEL与原生文件分开 |
| C_CHILD | Child从创建、Python初始化/导入到Driver装配、验证、清理、退出 | 包含Child侧主操作、harness和证据 |
| C_SUPERVISOR | 父启动、预检、Job/Child管理、采样、Pipe、receipt与退出 | 独立父进程成本 |
| C_HARNESS | 故障调度/观察/fixture/断言及装配 | 按父/子owner计入各自进程，不能再全额相加 |
| C_EVIDENCE | 文件/日志/witness写入、flush/fsync及关闭 | 已归属写入进程，按同一操作计一次 |
| C_JOB | 新建Job的当前及曾关联成员会计 | 与Child重叠，父在此Job之外 |

父/Child以创建句柄与creation time绑定，Job以本次私有创建与策略绑定。六维进程计数依次为ReadOperationCount、WriteOperationCount、OtherOperationCount、ReadTransferCount、WriteTransferCount、OtherTransferCount；Job使用BasicAndIo结构。进程快照与Job查询在父中执行，其调用成本归父，会计内容归被查询对象。

## 观测覆盖

初始Child快照在suspended时取得，首次恢复前的生命周期基线可观察；后续生命周期累计计数在查询成功时包含此前bootstrap。before/after的差值只代表两个查询之间的区间。父首次快照发生在预检和部分输出之后：生命周期累计包含早期工作，但从首次快照做差会排除它；最后采样之后的receipt、关闭、退出尾部继续缺失。

资源快照先后查询两个进程和Job，读值时点不同。OS六维计数提供进程会计，不能从中重构Python metadata/open/read/write/flush等调用次数、全部内核操作或物理磁盘写入；网络/设备/缓存/后台写回的语义遵从API定义。`ETW=NOT_ENABLED`、`physical_IO=NOT_PROVED`。

Driver的audit.events保存在内存中，最终ledger写出suite级owner/realm/phase计数，其自身及后续产物I/O也发生在快照之后。没有逐T20完整可持久enter/exit、观察器成功/不完整标志和结果进度桥接。适配器进入后可能先在audit.check失败，因而零条记录要求先证明观察完整性。父仅凭资源和退出状态无法恢复被终止Child内存中的已完成PASS。

T20主边界可登记 `PRESERVED`；`T20_FULL_IO_BOUNDARY_PROVED=false`。R44的独立Driver桥接申请沿用，本轮Driver改动0。

## 内存计量

父与Child均通过K32GetProcessMemoryInfo分别读取WorkingSetSize、PeakWorkingSetSize、PrivateUsage、PeakPagefileUsage。OS生命周期peak仅覆盖成功查询时点之前；after-exit可能UNKNOWN，父最后查询之后的分配仍需外部覆盖。Job PeakJobMemoryUsed/PeakProcessMemoryUsed为提交字节，无法替代Working Set。

若获得完整生命周期的两个峰值Pparent、Pchild，数学上 `sup_t(WSparent(t)+WSchild(t))≤Pparent+Pchild`，只能标记 `CONSERVATIVE_AGGREGATE_UPPER_BOUND`。两个峰值可发生于不同时刻；相加无法成为实测同时峰值，且共享页使其不同于唯一物理内存。当前完整峰值均未测得，`SIMULTANEOUS_TREE_PEAK=UNKNOWN`，所有内存候选完整值为null。

现有WS限制为查询后的超额检测。父不在其自有Child Job内，Child/Job提交quota也需要独立非null批准。内存分配与native阻塞可能先于下一次检测，完整硬上界继续未证。

## 固定120秒合同的精确成本分区

`T_whole = T_bootstrap + T_preflight + T_DLL/QPF + T_QPC_anchored + T_exit_tail`。

QPC起点位于Deadline464行，处于Python/标准库导入、策略读取、来源哈希、输出路径预检、WindowsApi DLL/导出绑定与QPF之后。该前置段耗时计入真实父生命周期，当前120门的锚点无法覆盖它。

| 阶段 | 现有语义 | 尚需证明 |
|---|---|---|
| Job、Pipe、Child创建及后续采样 | QPC锚点之后，调用前检查 | 单个native操作耗时及调度延迟 |
| 90秒 | 在下一个可达检查点请求终止自有Job/进程 | 精确时点送达、Child实际退出；无cooperative stop-dispatch IPC |
| 115秒 | 停止新的读/采样及普通和final append写/flush/fsync准入 | 既发I/O返回、最终receipt完整落盘 |
| 清理wait | 最多一次，计算至115的剩余等待量 | 计算/调度/终止I/O滞后 |
| 120秒 | 停止新CloseHandle/FileIO close准入 | 已开始close完成及进程退出 |
| 最后记录之后 | 返回判定与解释器退出 | 外部父尾部覆盖 |

F为失败字节预留，未提供独立耗时保证。最终receipt每个写/flush/fsync准入仍使用115秒默认门，115–120段仅具有关闭准入用途。若进入finally时已到115，final append可能直接拒绝，字节预留也无法保证生成记录。

TerminateJobObject/TerminateProcess为异步请求，pending I/O可能延迟退出。wait信号与GetExitCode共同决定已确认状态；达到120只会拒绝新关闭，并记录/保留未知或未关闭状态。同步native调用可能在准入后跨过截止点。延长grace为0，严格120秒完成证明继续false。

因此有据的成果是完整时间分区与现有检查语义；`HARD_DEADLINE_SUPERVISION_PROVED=false`。后续外部启动锚点/父尾部/进程退出观测均需单独合同与授权，有限动态样本也不能直接升级为全称完成证明。
