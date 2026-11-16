# H1–H8源码与证据对应

Material Passport：静态条件审查；新动态性质UNRUN。

|性质|代码与证据|
|---|---|
|H1 NoFalseSuccess|classify要求完整commit/ACK、exit+witness23、所有绑定及liveness；sender_prepare需root资格与认证RPC；receiver.observe_exit重核|
|H2 NoFalseFailureWithinContract|pidfd就绪后fresh-read；缺退出见证只在允许期限内PENDING；已有完整事实按同一谓词分类|
|H3 FailClosed|RPC/持久化/身份/主账/监督错误抛出并停止；stop_tree即使关闭记录失败仍尝试实际停止组|
|H4 MonotonicClosure|lifecycle_lock串行CLOSED与状态发布；publish/resume/formal均先查CLOSED；晚收据不能重开|
|H5 NoBudgetReset|window完整等值＋counter字节/inode/额度指纹；恢复只换身份和一次bit，T0/deadline不改|
|H6 SingleClassification|当前handoff_id与revision；classification_count必须0→1；重复观察返回原VERIFIED|
|H7 IndependentStopSource|receiver实际unit active、PID匹配且位于payload父slice外；协调器和case/watchdog身份检查；恢复与FORMAL再次检查|
|H8 EvidenceProvenance|root保护的状态/commit/waitpid见证/C09H资格、RPC peercred、ticket/ready摘要及全window绑定|

真实退出码来自新增同guard父协调器的直接waitpid，记录raw_wait_status与身份。该root进程在payload4tasks之外，属于新增TCB行政进程，下一授权必须明确接受；本轮没有实际fork测试。

条件边界：同UID任意恶意代码、root/内核失陷、介质回滚、宿主掉电和严格实时调度没有新认证。receiver在ACK后崩溃不能继续推进；既有独立case边界保持。完整机器拒绝/通过及资源开销需要下一动态执行。
