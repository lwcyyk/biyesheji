# batch06 RootIPC56 与 C09H34 结果

Material Passport：DCL-R6-batch06；RootIPC-static-1/r4；真实预检/准备记录；动态测试0；2026-11-11。

RootIPC计划56项（48个safe、8个mutant）；实际尝试0、完成0、通过0、变异检出0。8个mutant均保持UNRUN，未形成“已检出”结论。下列输入及独立oracle均在冻结范围内，程序实际调用0。

|case|层|variant|期望违规|实际状态|访问计数|
|---|---|---|---|---|---|
|P.read|file|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|P.replace|file|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|P.unauthorized|file|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|P.private_write|file|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|P.private_read|file|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|P.receipt_read|file|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|P.receipt_write|file|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|P.historical|file|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|P.bad_metadata|file|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|P.outside|file|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|P.symlink|file|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|P.hardlink|file|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|P.fault_after_create|file|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|P.fault_file_fsync|file|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|P.fault_rename|file|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|P.fault_directory_fsync|file|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|P.bad_batch|file|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|P.bad_boot|file|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|P.bad_lock|file|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|P.bad_digest|file|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|P.umask|file|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|P.repeat|file|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|T.ready|wait|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|T.stop_before|wait|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|T.stop_after_ready|wait|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|T.closed_wait|wait|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|T.closed|wait|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|T.ack_stop|wait|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|T.repeat_stop|wait|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|T.payload_dead|wait|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|T.receiver_dead|wait|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|T.read_error|wait|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|T.stale|wait|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|T.late_ack|wait|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|T.timeout|wait|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|T.exception|wait|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|T.deadline|wait|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|T.fd_cancel|wait|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|T.socket_cancel|wait|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|T.socket_eof|wait|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|M.root600.safe|file|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|M.root600.mutant|file|mutant|IPC-1|UNRUN_PREFLIGHT_FAILED|0|
|M.permissions.safe|file|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|M.permissions.mutant|file|mutant|IPC-1|UNRUN_PREFLIGHT_FAILED|0|
|M.stop.safe|wait|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|M.stop.mutant|wait|mutant|IPC-7|UNRUN_PREFLIGHT_FAILED|0|
|M.closed.safe|wait|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|M.closed.mutant|wait|mutant|IPC-8|UNRUN_PREFLIGHT_FAILED|0|
|M.exit23.safe|semantic|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|M.exit23.mutant|semantic|mutant|IPC-6|UNRUN_PREFLIGHT_FAILED|0|
|M.reactivate.safe|semantic|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|M.reactivate.mutant|semantic|mutant|IPC-8|UNRUN_PREFLIGHT_FAILED|0|
|M.batch.safe|file|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|M.batch.mutant|file|mutant|IPC-5|UNRUN_PREFLIGHT_FAILED|0|
|M.duplicate.safe|semantic|safe|∅|UNRUN_PREFLIGHT_FAILED|0|
|M.duplicate.mutant|semantic|mutant|IPC-9|UNRUN_PREFLIGHT_FAILED|0|

C09H计划34项；实际尝试0、完成0、28个safe路径和6个mutant均UNRUN_PREFLIGHT_FAILED。batch05的28 PASS+6 MUTATION_DETECTED保留其旧版本/旧批次范围。

|C09H case|冻结variant|本批实际|
|---|---|---|
|P.commit_before_exit|safe|UNRUN_PREFLIGHT_FAILED|
|P.stale_read_then_commit|safe|UNRUN_PREFLIGHT_FAILED|
|P.witness_first|safe|UNRUN_PREFLIGHT_FAILED|
|P.event_first|safe|UNRUN_PREFLIGHT_FAILED|
|P.live_receiver|safe|UNRUN_PREFLIGHT_FAILED|
|N.no_receipt|safe|UNRUN_PREFLIGHT_FAILED|
|N.other_exit|safe|UNRUN_PREFLIGHT_FAILED|
|N.bad_batch|safe|UNRUN_PREFLIGHT_FAILED|
|N.bad_boot|safe|UNRUN_PREFLIGHT_FAILED|
|N.old_lock|safe|UNRUN_PREFLIGHT_FAILED|
|N.receiver_unready|safe|UNRUN_PREFLIGHT_FAILED|
|N.write_interrupted|safe|UNRUN_PREFLIGHT_FAILED|
|N.fsync_failed|safe|UNRUN_PREFLIGHT_FAILED|
|N.receiver_died|safe|UNRUN_PREFLIGHT_FAILED|
|N.stop_lost|safe|UNRUN_PREFLIGHT_FAILED|
|N.budget_bad|safe|UNRUN_PREFLIGHT_FAILED|
|N.closed_late|safe|UNRUN_PREFLIGHT_FAILED|
|N.timeout|safe|UNRUN_PREFLIGHT_FAILED|
|N.sender_bad|safe|UNRUN_PREFLIGHT_FAILED|
|N.version_bad|safe|UNRUN_PREFLIGHT_FAILED|
|P.repeat_event|safe|UNRUN_PREFLIGHT_FAILED|
|N.window_reset|safe|UNRUN_PREFLIGHT_FAILED|
|M.stale.safe|safe|UNRUN_PREFLIGHT_FAILED|
|M.stale.mutant|mutant|UNRUN_PREFLIGHT_FAILED|
|M.version.safe|safe|UNRUN_PREFLIGHT_FAILED|
|M.version.mutant|mutant|UNRUN_PREFLIGHT_FAILED|
|M.exit_only.safe|safe|UNRUN_PREFLIGHT_FAILED|
|M.exit_only.mutant|mutant|UNRUN_PREFLIGHT_FAILED|
|M.closed.safe|safe|UNRUN_PREFLIGHT_FAILED|
|M.closed.mutant|mutant|UNRUN_PREFLIGHT_FAILED|
|M.duplicate.safe|safe|UNRUN_PREFLIGHT_FAILED|
|M.duplicate.mutant|mutant|UNRUN_PREFLIGHT_FAILED|
|M.unknown.safe|safe|UNRUN_PREFLIGHT_FAILED|
|M.unknown.mutant|mutant|UNRUN_PREFLIGHT_FAILED|

本批实际输入锁与静态源码可复核，逐项实际注入/文件或进程原件/退出/oracle/耗时均N/A，实际访问0。未来完整路径静态505、共同2750≤5000仍是预测上界，本批没有动态验证。ACL拒绝等更强操作覆盖以冻结清单与实际日志为准，当前无实际ACL注入见证。

[冻结RootIPC合同](evidence/root_ipc_contract.json)、[C09H合同](evidence/c09_contract.json)、[实际状态](evidence/ACTUAL_RESULTS.json)。
