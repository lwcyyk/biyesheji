# 自动关闭、兜底与退出

Material Passport：DCL-R6-MR-A；batch10-r5；ManagerRecovery-static-1/r5；2026-11-12；冻结入口1次、重跑/源码修复0。

A2=PARTIAL_PREWINDOW_STOP_OBSERVED，r5内部结果CLEANUP_UNKNOWN，原生seal失败。本次是非预期真实启动异常；预声明的C10后故障注入未到达。

|职责|实际结果|
|---|---|
|主触发|初始scheduler在异常wrapper中自动设置HALTED并生成STOP_REQUEST|
|STOP/CLOSED|均为自动路径产生；CLOSED原因COORDINATOR_STOP_REQUEST|
|父协调器停止|观察STOP，调用原stop_tree；stop_exit=0、empty=true|
|abort内部后备|当前slice stop/kill有尝试，记录两项TimeoutExpired；没有足够日志给出各命令完整返回|
|独立external-stop服务|尚未启动，因此该来源本次未验证|
|人工/第二条清理命令|0；仅做事后只读导出|
|r5关闭结果|两轮记录UNKNOWN，含DEADLINE_UNKNOWN/PRIMARY_CLEANUP:LimitReached/两个EXTERNAL_STOP:TimeoutExpired|
|原生封存|SEAL_ERROR=FileNotFoundError，缺batch_state；out/EVIDENCE.zip不存在|
|最终退出|scheduler直接waitpid exit125/raw32000；事后Root/Payload角色全空，父cgroup不存在|

STOP记录→CLOSED记录书签差0.005649209秒；STOP→父停止返回采样0.023635593秒；STOP→child wait采样0.051644074秒。它们是已有书签跨度，CLOSED精确持久完成在记录采样与停止结果之间；异常指令/ABORTING瞬时转换缺独立打点。

本批Payload从未启动，现有组空证据只能说明无残留，尚不证明活动Payload回收能力。实际角色全空与producer保留UNKNOWN分别登记，不据事后观察改写旧UNKNOWN。主路径产生停止信号，父协调器既有停止路径完成关闭；原生自动seal责任仍失败。最终研究ZIP属于行政证据打包，不能充当原生自动seal通过。

[关闭实际数据](evidence/AUTOMATIC_CLOSURE_ACTUAL.json) · [退出/时间](evidence/EXECUTION_TIMELINE.json) · [原生事后审计](evidence/POSTRUN_AUDIT.json)。
