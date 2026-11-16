# 编码前依赖、分离边界与最小范围

2026-11-11；C09Fix-static-1。当前只创建静态源/输入/文档，动态测试0。

工程输入族：receiver在pidfd等待前取旧快照；sender随后持久发布退出意图并exit23；pidfd返回。指标为“必要交接前提齐备时错误关闭/缺证据时错误放行”的数量。旧冻结分支可错误关闭；标准的版本化收据＋接收确认＋真实退出见证方法与本修复预期等效。通用方法更高代价分离实例0，主凭据机制实现门CLOSED。本轮依据用户明确的资源设施静态修复授权实施，未提出新凭据机制候选。

历史结论：batch04只有sender意图标记、payload ready和STOP_ARMED；没有成功交接收据、接收确认或责任转移提交。旧快照分类缺陷与未完成交接分开裁决。缺少成功证据时禁止恢复符合fail-closed。

最小代码依赖：
1. guard.py：C09入口/退出观察/恢复接线、闭合锁、只限C09H的回归调度。
2. c09_handoff.py：root保护的版本化状态/收据；Receiver在fsync完成后经受保护AF_UNIX通道返回确认；pidfd就绪后fresh-read。
3. 同一guard父协调器waitpid真实子Launcher：pidfd本身无法提供非子进程退出码。父进程记录kernel wait状态，作为退出分类的独立见证；额外1个可信root行政进程位于payload slice之外，须在下一动态申请明确批准。payload父slice仍4tasks。
4. c09_regression.py与c09_oracle.py：冻结事件交错/受限错误行为与独立H1–H8断言；不改原探针、S核心/driver/oracle、runner或业务代码。

IPC不新增系统服务/账户/依赖；使用已有Python标准库和既有root停止服务。root socket仅当前batch inputs下，0600；SO_PEERCRED及PID/start_ticks/boot绑定。一次退出终态只允许一份。CLOSED与C09状态发布共享生命周期锁；关闭即吸收。receiver崩溃后拒绝推进，原case Watchdog/systemd边界保留。

下一批命名batch05；本轮不创建其运行根/单位/预算/T0。新增C09H预留访问上界5000（同原全局账，逐步骤预付），加原cal硬界57034，合计62034≤100000；cal300/总1000000/1800/1740保持。全部动态性质UNRUN。
