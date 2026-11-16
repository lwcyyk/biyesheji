# 停止状态优先级与交接并发规则

Material Passport：RootIPC-static-1/r4；有限静态修复与证据分析；2026-11-11；动态UNRUN。

状态优先级：CLOSED吸收 → STOP_REQUEST/必要监督丢失/失败 → boot或绝对期限失效 → 当前正常准备/ACK/验证。终止判据优先于ready、exit23及迟到ACK。每次wait不长期复用之前的成功状态。

|状态|允许动作|转移与线性化|
|---|---|---|
|RUNNING/CALIBRATING|原case、C09H及RootIPC前置检查|每轮checkpoint核boot/stop_at/deadline/终止标记|
|STOP_REQUEST_SEEN|停止新资格，进入stop_tree|请求是取消事实；Root在生命周期锁下发布CLOSED|
|CLOSED|组停止、子回收、原始证据写入与seal|吸收态；后续收据/ACK不恢复|
|HANDOFF_PREPARING/READY/COMMITTED|原身份/账/窗口核对及持久ACK|receiver commit屏障后才答复；答复前同锁重新检查停止|
|EXIT_OBSERVED/PENDING|父waitpid见证、fresh-read、期限内等待|缺ACK/receiver或超时失败关闭|
|HANDOFF_VERIFIED/RESUMED|一次受控恢复、原窗口继续|原classification_count=1、摘要/receiver/once bit全检；CLOSED先拒绝|
|CLEANUP/SEALED|重复停止确认、普通退出记录、父最终seal|无需重置账或T0；无法回收明确失败|

STOP_REQUEST可由payload异步发布，其到达与已经开始的I/O可能重叠。Root每次观察后阻断后续资格；CLOSED发布和handoff状态变更由同一flock串行。若ACK在锁内检查后才遇到请求，sender/parent/receiver后续fresh检查仍会拒绝恢复；CLOSED后ACK不能生成合法新资格。当前不声称中断已进入内核的fsync/systemctl调用。

父协调器保留直接waitpid及稳定身份；普通退出记录写入root_private，成功交接见证仍另由原handoff合同生成。新的父最终seal顺序保证普通退出记录在本批最终封存之前产生。新顺序与正常、异常、强制终止下的行为均待动态核验。

[安全性质](ROOT_IPC_SAFETY_PROPERTIES.md)、[专项夹具](ROOT_IPC_REGRESSION_PLAN.md)、[原交接状态机](../DCL-R6-C09Fix/C09_HANDOFF_STATE_MACHINE.md)。
