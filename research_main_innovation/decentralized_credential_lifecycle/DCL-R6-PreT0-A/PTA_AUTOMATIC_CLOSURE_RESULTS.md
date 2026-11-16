# 自动STOP、回收与内部状态

Material Passport：DCL-R6-PreT0-A；batch11；PreT0Recovery-static-1/r3；NORMAL_START；2026-11-12（Asia/Shanghai）；实际入口1次，重跑0，源码修复0。

**关键错误自动触发STOP/CLOSED，角色和组已空，额外兜底及人工清理均为0。内部状态先出现UNKNOWN，后依据冻结角色退出审查收敛为CLOSED_CLEANUP_CONFIRMED。**

|责任源|实际行为|
|---|---|
|独立Root停止服务892|Receiver.poll抛PT_RUNTIME_PHASE_DRIFT，自动abort发布首个STOP；多层异常wrapper继续执行冻结收敛|
|Launcher child887|观察STOP后root_checkpoint拒绝；异常自动abort，退出125|
|Root协调器827|直接waitpid见证child887/raw32000/125，自动stop_tree，保留首错及关闭记录|
|systemd|当前batch11 slice停止成功；停止服务最终退出125，原journal保留failed记录|
|外部/人工兜底|0；事后只读导出和行政打包没有调用关闭函数|

首个STOP sample67.121192409，reason=MR_CRITICAL:C09_OR_SUPERVISOR_FAILURE。首次持久错误记录在67.129488196，由child先获得锁，保存LAUNCHER_ERROR/IPC_STOP_REQUEST_DOMINATES。它与触发STOP的外部异常属于不同证据层，原件均保留。

CLOSED sample67.139362562；child停止结果67.152813419显示stop_exit0、empty=true、group不存在；父协调器停止结果67.249958981同样成功。child直接waitpid在67.226047790。停止服务journal退出见证为MONOTONIC67.405716，精确内核退出瞬间缺少专门打点。

mr_close_attempts前两条为UNKNOWN：owner退出/child reap仍待定。后续三条依据冻结角色审查记CLOSED_CLEANUP_CONFIRMED，最终sample67.371083714。外部服务67.329851722的记录观察827和887均退出；其自身退出另由systemd见证。所有UNKNOWN原行保留。预算快照中缺少journal的UNKNOWN字段同样保留；关闭成功不授予完整资源资格。

首次独立事后audit在同boot BOOTTIME131.041344651：Root角色0、UID999进程0、parent cgroup不存在；后续只读完整导出再次确认。systemd瞬时show在较晚查询显示inactive/dead与success，原journal中实际125和failed记录保持，判定优先保留该次退出原始见证。

[首次进程审计](evidence/CLOSURE_AUDIT.json) · [导出审计](evidence/POSTRUN_AUDIT.json) · [journal消息索引](evidence/JOURNAL_MESSAGE_INDEX.json) · [自动关闭原件汇总](evidence/ACTUAL_RESULTS.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原条件结论与强G覆盖裁决保持。
