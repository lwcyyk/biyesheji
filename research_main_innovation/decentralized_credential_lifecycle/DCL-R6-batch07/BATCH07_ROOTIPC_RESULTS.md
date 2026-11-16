# batch07 RootIPC56与权限实际结果

Material Passport：DCL-R6-batch07；BootContinuity-static-1/r4；真实启动后首次失败；2026-11-11；复跑0。

RootIPC56计划56（含8 mutant），实际尝试0、完成0、通过0、变异检出0。入口初始化了global counter/intent，metadata为999:989/0600，ACL为空，Root私有boot文件0:0/0600及目录0700；这些是实际元数据与发布路径范围。

UID999读取共享intent的业务证据为NOT_EXERCISED：C00票据未发放，controller未进入Budget/probe，global counter保持0。Root读文件、元数据符合或memfd消费都无法替代非Root实际open。Root私有拒绝写入、65534拒绝、原子替换故障与8个mutant仍UNRUN。

|case|variant|实际|
|---|---|---|
|P.read|safe|UNRUN_RESOURCE_GATE|
|P.replace|safe|UNRUN_RESOURCE_GATE|
|P.unauthorized|safe|UNRUN_RESOURCE_GATE|
|P.private_write|safe|UNRUN_RESOURCE_GATE|
|P.private_read|safe|UNRUN_RESOURCE_GATE|
|P.receipt_read|safe|UNRUN_RESOURCE_GATE|
|P.receipt_write|safe|UNRUN_RESOURCE_GATE|
|P.historical|safe|UNRUN_RESOURCE_GATE|
|P.bad_metadata|safe|UNRUN_RESOURCE_GATE|
|P.outside|safe|UNRUN_RESOURCE_GATE|
|P.symlink|safe|UNRUN_RESOURCE_GATE|
|P.hardlink|safe|UNRUN_RESOURCE_GATE|
|P.fault_after_create|safe|UNRUN_RESOURCE_GATE|
|P.fault_file_fsync|safe|UNRUN_RESOURCE_GATE|
|P.fault_rename|safe|UNRUN_RESOURCE_GATE|
|P.fault_directory_fsync|safe|UNRUN_RESOURCE_GATE|
|P.bad_batch|safe|UNRUN_RESOURCE_GATE|
|P.bad_boot|safe|UNRUN_RESOURCE_GATE|
|P.bad_lock|safe|UNRUN_RESOURCE_GATE|
|P.bad_digest|safe|UNRUN_RESOURCE_GATE|
|P.umask|safe|UNRUN_RESOURCE_GATE|
|P.repeat|safe|UNRUN_RESOURCE_GATE|
|T.ready|safe|UNRUN_RESOURCE_GATE|
|T.stop_before|safe|UNRUN_RESOURCE_GATE|
|T.stop_after_ready|safe|UNRUN_RESOURCE_GATE|
|T.closed_wait|safe|UNRUN_RESOURCE_GATE|
|T.closed|safe|UNRUN_RESOURCE_GATE|
|T.ack_stop|safe|UNRUN_RESOURCE_GATE|
|T.repeat_stop|safe|UNRUN_RESOURCE_GATE|
|T.payload_dead|safe|UNRUN_RESOURCE_GATE|
|T.receiver_dead|safe|UNRUN_RESOURCE_GATE|
|T.read_error|safe|UNRUN_RESOURCE_GATE|
|T.stale|safe|UNRUN_RESOURCE_GATE|
|T.late_ack|safe|UNRUN_RESOURCE_GATE|
|T.timeout|safe|UNRUN_RESOURCE_GATE|
|T.exception|safe|UNRUN_RESOURCE_GATE|
|T.deadline|safe|UNRUN_RESOURCE_GATE|
|T.fd_cancel|safe|UNRUN_RESOURCE_GATE|
|T.socket_cancel|safe|UNRUN_RESOURCE_GATE|
|T.socket_eof|safe|UNRUN_RESOURCE_GATE|
|M.root600.safe|safe|UNRUN_RESOURCE_GATE|
|M.root600.mutant|mutant|UNRUN_RESOURCE_GATE|
|M.permissions.safe|safe|UNRUN_RESOURCE_GATE|
|M.permissions.mutant|mutant|UNRUN_RESOURCE_GATE|
|M.stop.safe|safe|UNRUN_RESOURCE_GATE|
|M.stop.mutant|mutant|UNRUN_RESOURCE_GATE|
|M.closed.safe|safe|UNRUN_RESOURCE_GATE|
|M.closed.mutant|mutant|UNRUN_RESOURCE_GATE|
|M.exit23.safe|safe|UNRUN_RESOURCE_GATE|
|M.exit23.mutant|mutant|UNRUN_RESOURCE_GATE|
|M.reactivate.safe|safe|UNRUN_RESOURCE_GATE|
|M.reactivate.mutant|mutant|UNRUN_RESOURCE_GATE|
|M.batch.safe|safe|UNRUN_RESOURCE_GATE|
|M.batch.mutant|mutant|UNRUN_RESOURCE_GATE|
|M.duplicate.safe|safe|UNRUN_RESOURCE_GATE|
|M.duplicate.mutant|mutant|UNRUN_RESOURCE_GATE|

本次Root直接LAUNCHER_ERROR触发停止，没有STOP_REQUEST。RootIPC关于C09 ready/RPC取消、迟到ACK与全部停止交错仍待动态覆盖。[实际meta导出锁](evidence/NATIVE_EXPORT_LOCK.json)、[资源核算](evidence/RESOURCE_ACCOUNTING.json)。
