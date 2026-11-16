# T20主操作与全程计数

主操作按原“结果检查点拒绝”输入和R42明确的primary提案，落实为真实调用 `State.observe_result("A01","PASS",1000000)`。其源调用链为observe_result→commit_case_record(TEST_ASSERTION)→checkpoint→reserve_bytes，只有通过准入才可能到io_write。

## 主操作边界

开始点为夹具行、既有前缀、预算及故障计划完成后，实际observe_result调用之前的独立事件索引；结束点为该函数真实抛出RESULT_CHECKPOINT_UNCONFIRMED并被窄类型捕获之后，begin_terminal之前。

已知拒绝变体在容量guard前拒绝；未知变体在真实WRITE_STARTED赋值后、write进入前中断。两者都可观察到0次write进入，但后者的目标知识保持UNKNOWN/Poison。原0仅约束这段主操作的受保护payload-write次数。

原合成PASS输入须保留；拒绝记录没有收到确认引用。后续真实finalize_evidence必须返回整体false，原结果不能被后续证据重新标成可靠。原测试输入/预期完整复制，未删除责任；原A01测试体未运行。

## 所有者与层次

| 类别 | 范围 |
|---|---|
| SUT_IO | 实际目标方法发起的模型Journal、虚拟产物及元数据/描述符操作 |
| HARNESS_IO | 夹具及独立核验、native输入读取、进程内存查询 |
| EVIDENCE_IO | 驱动自己的结果、日志、失败证据、来源和资源文件 |

每条事件同时有realm=MODEL/NATIVE和阶段INITIALIZATION/SETUP/PRIMARY/RECOVERY/CLEANUP/EVIDENCE_OUTPUT。所有者互斥；全套共同输入/产物只归suite共享，不在28项中重复加账。

TOTAL_IO按这些互斥维度汇总，并分别保留模型和native Python API。一次Python write可能对应零个或多个OS调用，更无法直接等同于一次物理落盘。read/write/flush/fsync/close、open、stat/lstat、metadata、listdir、tell/fileno、mkdir和进程查询均有边界说明；driver未使用rename/replace/unlink。

## 全生命周期可观察范围

逻辑总范围从进程/driver启动，经过模块加载、Journal/前缀准备、主操作、注入、结果/摘要核验、恢复、清理、失败receipt及所有证据输出，直至最终句柄关闭和外部观察的进程退出。

本文件能记录其中明确包装的Python API与模型调用。bootstrap/import loader、部分隐式路径/ctypes元数据、异常格式化的linecache、最后receipt之后的I/O及解释器退出缺少完整独立观察，因此 **FULL_IO_COUNT_UNPROVEN**，R43_T20_FULL_IO_BOUNDARY_PROVED=false。

资源账本标明自身写入前快照，最后写入/关闭需要外部见证。不会将这些尾部漏记项登记成0。

## 时钟与资源采样

目标虚拟90/115/120时钟与宿主真实perf_counter分开。Windows K32GetProcessMemoryInfo读取进程生命周期PeakWorkingSetSize；它可包含两次采样之间的峰值，检测超额发生在采样返回之后，不能证明从未越过硬上限。

当前没有运行代码。主操作或全程实际调用、native syscall、RSS峰值均为NOT_MEASURED或UNKNOWN。源码整数上界单独标STATIC_BOUND。恢复追加和宿主证据写入可以为正，不能据主操作0推得整个用例0。
