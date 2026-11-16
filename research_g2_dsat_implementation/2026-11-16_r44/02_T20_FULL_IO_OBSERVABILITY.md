# T20全程I/O可观察性

T20主操作保持实际 `State.observe_result("A01","PASS",1000000)`。开始在源调用前的事件索引，结束在RESULT_CHECKPOINT_UNCONFIRMED被捕获之后、begin_terminal之前。原0约束这段主操作的受保护payload-write，恢复和宿主取证可以为正。

## 五种范围

- C_main：冻结主区间内、指定层次的SUT事件。
- C_sut：整个用例生命周期的SUT事件。
- C_harness：初始化、独立核验和计量等驱动工作。
- C_evidence：driver自己的结果/日志/receipt输出。
- C_process：唯一测试进程生命周期的Windows会计向量。

同一层次和realm下C_main属于C_sut。内部三种所有者可以定义成互斥；未观察项仍需独立记录。模型write次数不能与Windows操作数直接比较或相加。父观察器另有C_observer，不能作为免费工作隐藏。loader等缺少可靠归属的事件保留C_unknown。适配器内部fstat再调用stat时，Python进入数与逻辑请求数也要分开；当前缺少parent/request身份，不能把嵌套进入直接当独立逻辑I/O。

[IO_COUNTERS](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-io_counters)定义读、写、其他操作数及其传输字节。完整进程优先保留最终生命周期绝对值，初始快照可能非零；final-initial只表示该采样区间，不能丢掉启动计数后再称全程。

## 生命周期与观察主体

| 阶段 | 内部/外部观察 | 仍需保留的边界 |
|---|---|---|
| CreateProcess之前至返回 | 父进程launch意图、QPC、源身份 | 父创建行为属于父成本，不能从child计数复原 |
| Python启动/模块加载 | 唯一process句柄及私有Job会计 | 原内部观察器尚未建立；loader/native细节未分项 |
| fixture/Journal/前缀 | driver类型/字节和parent进程计数 | 种子ACK为输入前提，未重放真实68 |
| T20主调用 | 真实函数、独立模型适配器 | 观察器本身失败时不能信任记录0 |
| 恢复/最终化 | 独立阶段标记及原源方法 | 新证据不替代原缺失结果ACK |
| 核验、输出、清理 | 完整字节/链、费用、父计数 | child账本快照后仍有取证I/O |
| 退出 | held process handle signal及退出值、final Job会计 | API失败/未退出保持UNKNOWN |

最小外部组合为：新建私有Job、创建时关联且初始suspended、持有process/thread句柄和PID/创建FILETIME、resume前身份/成员检查、退出后查询会计。[Job基本I/O结构](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_and_io_accounting_information)保留曾关联成员，适合父进程在child退出后留存Job做交叉核验。扩展内存限制结构的IoInfo是保留字段，不能误用。

## 新确认的证据桥接缺口

1. R43的audit.events是内存列表，落盘ledger主要按owner/realm/phase/op作全套汇总；witness是末态快照和event_index。现有产物无法独立复原T20逐事件区间。
2. ObservedFileIO.write已经进入方法后才调用audit.event；event的时间/内存/额度检查可能在append之前失败。故记录0需要“观察链成功”的前提；该失败窗口应报UNKNOWN。
3. case结果在晚期输出前仍可只存在内存。强制终止可能失去已完成case的持久证据，父进程不能根据仍有文件或累计CPU推断PASS。

上述结论登记为静态缺口，动态执行结果保持NOT_RUN。单独的T20证据桥接申请已登记；本轮Driver修改0，未将其并入监督器创建申请。

## 分层计量

主区间模型API可在观察成功条件下检查write0；它不覆盖所有native活动。GetProcessIoCounters属于PROCESS_COUNTER_OBSERVED能力层。ETW属于经provider/schema/filter/loss核查后的KERNEL_EVENT_OBSERVED层；[官方说明](https://learn.microsoft.com/en-us/windows/win32/etw/about-event-tracing)明确存在丢事件情形。

物理磁盘仍PHYSICAL_IO_UNMEASURED。缓存、共享页、延迟回写、内核归属与设备稳定性不能从单进程会计推出。当前所有层的实际数据均NOT_MEASURED，FULL_IO_UNPROVEN保持。
