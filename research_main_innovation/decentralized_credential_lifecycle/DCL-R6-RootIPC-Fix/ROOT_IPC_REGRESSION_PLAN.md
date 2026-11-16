# 新增56项权限与停止夹具冻结计划

Material Passport：RootIPC-static-1/r4；有限静态修复与证据分析；2026-11-11；动态UNRUN。

冻结56项：48个safe（含8个变异对照）、8个mutant；实际执行0。原C09H34、S34、负向门17均作为独立原测试保留。新增Root套件只在未来授权Root scheduler内、C09H通过且真实C09之前调用，无新增systemd单位或standalone入口。

文件层fixture实际调用新publisher、读取真实lstat及一次降权UID999/65534的open结果和原始waitpid；历史root600、replace与合成路径/故障仅影响`ipc_fixture_*`。私有/保护收据分别测试Root私有拒绝及group-read/禁止写入。文件fsync故障属于受限EIO注入，物理介质失败与掉电保持额外责任。

停止层在Root私有合成命名空间建立真实ready/STOP/CLOSED文件，调用生产wait_ready/wait_fd/receive检查。payload/receiver失效为liveness观察回调的投影；ACK/退出/重复分类使用冻结合成subject。真正socket端到端确认、实际receiver进程失效、父waitpid/pidfd交错仍由真实C09及原C07–C12链取得；本套件不会把这些投影称为真实交接成功。

|case|层|scenario|variant|允许违规集|实际|
|---|---|---|---|---|---|
|P.read|file|read|safe|∅|UNRUN|
|P.replace|file|replace|safe|∅|UNRUN|
|P.unauthorized|file|unauthorized|safe|∅|UNRUN|
|P.private_write|file|private_write|safe|∅|UNRUN|
|P.private_read|file|private_read|safe|∅|UNRUN|
|P.receipt_read|file|receipt_read|safe|∅|UNRUN|
|P.receipt_write|file|receipt_write|safe|∅|UNRUN|
|P.historical|file|historical|safe|∅|UNRUN|
|P.bad_metadata|file|bad_metadata|safe|∅|UNRUN|
|P.outside|file|outside|safe|∅|UNRUN|
|P.symlink|file|symlink|safe|∅|UNRUN|
|P.hardlink|file|hardlink|safe|∅|UNRUN|
|P.fault_after_create|file|fault_after_create|safe|∅|UNRUN|
|P.fault_file_fsync|file|fault_file_fsync|safe|∅|UNRUN|
|P.fault_rename|file|fault_rename|safe|∅|UNRUN|
|P.fault_directory_fsync|file|fault_directory_fsync|safe|∅|UNRUN|
|P.bad_batch|file|bad_batch|safe|∅|UNRUN|
|P.bad_boot|file|bad_boot|safe|∅|UNRUN|
|P.bad_lock|file|bad_lock|safe|∅|UNRUN|
|P.bad_digest|file|bad_digest|safe|∅|UNRUN|
|P.umask|file|umask|safe|∅|UNRUN|
|P.repeat|file|repeat|safe|∅|UNRUN|
|T.ready|wait|ready|safe|∅|UNRUN|
|T.stop_before|wait|stop_before|safe|∅|UNRUN|
|T.stop_after_ready|wait|stop_after_ready|safe|∅|UNRUN|
|T.closed_wait|wait|closed_wait|safe|∅|UNRUN|
|T.closed|wait|closed|safe|∅|UNRUN|
|T.ack_stop|wait|ack_stop|safe|∅|UNRUN|
|T.repeat_stop|wait|repeat_stop|safe|∅|UNRUN|
|T.payload_dead|wait|payload_dead|safe|∅|UNRUN|
|T.receiver_dead|wait|receiver_dead|safe|∅|UNRUN|
|T.read_error|wait|read_error|safe|∅|UNRUN|
|T.stale|wait|stale|safe|∅|UNRUN|
|T.late_ack|wait|late_ack|safe|∅|UNRUN|
|T.timeout|wait|timeout|safe|∅|UNRUN|
|T.exception|wait|exception|safe|∅|UNRUN|
|T.deadline|wait|deadline|safe|∅|UNRUN|
|T.fd_cancel|wait|fd_cancel|safe|∅|UNRUN|
|T.socket_cancel|wait|socket_cancel|safe|∅|UNRUN|
|T.socket_eof|wait|socket_eof|safe|∅|UNRUN|
|M.root600.safe|file|read|safe|∅|UNRUN|
|M.root600.mutant|file|read|mutant|IPC-1,IPC-3|UNRUN|
|M.permissions.safe|file|bad_metadata|safe|∅|UNRUN|
|M.permissions.mutant|file|bad_metadata|mutant|IPC-1,IPC-3|UNRUN|
|M.stop.safe|wait|stop_before|safe|∅|UNRUN|
|M.stop.mutant|wait|stop_before|mutant|IPC-7|UNRUN|
|M.closed.safe|wait|closed|safe|∅|UNRUN|
|M.closed.mutant|wait|closed|mutant|IPC-7,IPC-8|UNRUN|
|M.exit23.safe|semantic|exit_only|safe|∅|UNRUN|
|M.exit23.mutant|semantic|exit_only|mutant|IPC-6|UNRUN|
|M.reactivate.safe|semantic|reactivate|safe|∅|UNRUN|
|M.reactivate.mutant|semantic|reactivate|mutant|IPC-8|UNRUN|
|M.batch.safe|file|bad_batch|safe|∅|UNRUN|
|M.batch.mutant|file|bad_batch|mutant|IPC-5|UNRUN|
|M.duplicate.safe|semantic|duplicate|safe|∅|UNRUN|
|M.duplicate.mutant|semantic|duplicate|mutant|IPC-9|UNRUN|

每job保存绑定、输入摘要、Root稳定身份、时钟、全局访问前后值，以及metadata/probe errno/真实子退出或合成事件原件。独立oracle拒绝错误UID/GID/saved身份/CapEff、原件缺失/非Root写入/错mode/超限/错误绑定、未触发历史故障和未命中或额外未声明违规。逐job即时审查失败即停止；整套完成后再独立重算并发布Root保护资格。

计费为entry1＋每job保守预付8＋Root整套审查1：1+56×9=505（未用占用保留），硬限512。原C09H完成路径上界2245，合计2750≤5000；二者共用原C09H ticket的5000上限。完整校准硬上界62034≤100000保持，全部共享T0+300软窗。新增进程、磁盘屏障及实际耗时待测；任何窗口不足即停止，现有预算/期限保持。

[冻结合同](evidence/root_ipc_contract.json)、[root_ipc_regression.py:212 run_suite](<../../../DCL-R6-isolated-verification/ri01/src/root_ipc_regression.py>)、[root_ipc_oracle.py:78 check_job](<../../../DCL-R6-isolated-verification/ri01/src/root_ipc_oracle.py>)、[batch06申请](BATCH06_EXECUTION_REQUEST.md)。
