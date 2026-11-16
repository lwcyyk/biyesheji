# Root 等待缺口与取消处理审查

Material Passport：RootIPC-static-1/r4；有限静态修复与证据分析；2026-11-11；动态UNRUN。

batch05缺口定位于旧guard.py:834–835：ready不存在时只看时间，忽略已发布CLOSED/STOP_REQUEST。payload约21秒已退出，scheduler直到共享T0+300才以C09_NOT_READY结束。当前真实证据保持原结论。

|等待/处理点|修复后行为|期限/清理范围|
|---|---|---|
|C09 ready|每轮checkpoint fresh读标记及状态；检查payload与receiver活性；ready可见后再检查|50ms轮询参数；原min(T0+300,stop_at)期限保持|
|一般case PID/退出等待|每轮checkpoint；原C07/08异常退出判据保持|原PID/单case期限保持|
|Root父子握手|wait_fd有限select与取消复查|原5秒握手期限|
|socket connect/send/recv|非阻塞/有限阻塞片段，每轮取消检查；保留原交接观察期|client至原12秒上限；receiver读/发送各原有0.5秒层级内|
|父waitpid|每轮fresh标记；首次停止后有限30秒协作grace，仍受原deadline；到期pidfd kill|异常路径kill后最多5秒非阻塞回收；无法确认回收则明确失败|
|RPC ACK并发闭合|lifecycle锁内重新检查；sender ACK后与exit23前再检查|已CLOSED不再准入；在途I/O按失败或清理处理|
|finally seal|scheduler将封存交给父；父先回收子、保存普通raw_wait_status，再等待外部停止器退出封存|原20秒seal等待/manager清理条件；不形成新执行窗|

源码：[root_ipc.py:143 checkpoint](<../../../DCL-R6-isolated-verification/ri01/src/root_ipc.py>)、[root_ipc.py:159 wait_ready](<../../../DCL-R6-isolated-verification/ri01/src/root_ipc.py>)、[root_ipc.py:179 receive](<../../../DCL-R6-isolated-verification/ri01/src/root_ipc.py>)、[root_ipc.py:192 connect](<../../../DCL-R6-isolated-verification/ri01/src/root_ipc.py>)、[root_ipc.py:204 send_packet](<../../../DCL-R6-isolated-verification/ri01/src/root_ipc.py>)、[guard.py:990 launcher](<../../../DCL-R6-isolated-verification/ri01/src/guard.py>)。状态优先级与工程延迟参数见[状态机](ROOT_STOP_STATE_MACHINE.md)。

终止通知采用“首个CLOSED记录＋幂等重复清理”：CLOSED原件保留，后续stop_event/stop_result记录复核。多可信管理进程可以重复请求systemctl stop；该行为不产生重复交接成功分类。停止后只允许必要的回收、持久化和封存。ticket/局部PASS文件本身无法授予运行资格，controller、恢复与FORMAL仍fresh核对停止状态。

RI-3=CONDITIONAL_PASS：缺失的取消读取和有限回收路径已实现。50ms、30秒和5秒是配置参数；实际调度、fsync、systemd阻塞及停止总延迟仍UNMEASURED，尚未证明新硬界。
