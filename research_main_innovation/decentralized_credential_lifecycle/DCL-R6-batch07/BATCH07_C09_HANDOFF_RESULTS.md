# batch07 C09H34与真实C09交接

Material Passport：DCL-R6-batch07；BootContinuity-static-1/r4；真实启动后首次失败；2026-11-11；复跑0。

真实C09=NOT_EXERCISED。C09H34计划34（原28 safe接受路径、6 mutant），尝试0、完成0、接受0；下列全为UNRUN_RESOURCE_GATE。

|C09H case|variant|actual|
|---|---|---|
|P.commit_before_exit|safe|UNRUN_RESOURCE_GATE|
|P.stale_read_then_commit|safe|UNRUN_RESOURCE_GATE|
|P.witness_first|safe|UNRUN_RESOURCE_GATE|
|P.event_first|safe|UNRUN_RESOURCE_GATE|
|P.live_receiver|safe|UNRUN_RESOURCE_GATE|
|N.no_receipt|safe|UNRUN_RESOURCE_GATE|
|N.other_exit|safe|UNRUN_RESOURCE_GATE|
|N.bad_batch|safe|UNRUN_RESOURCE_GATE|
|N.bad_boot|safe|UNRUN_RESOURCE_GATE|
|N.old_lock|safe|UNRUN_RESOURCE_GATE|
|N.receiver_unready|safe|UNRUN_RESOURCE_GATE|
|N.write_interrupted|safe|UNRUN_RESOURCE_GATE|
|N.fsync_failed|safe|UNRUN_RESOURCE_GATE|
|N.receiver_died|safe|UNRUN_RESOURCE_GATE|
|N.stop_lost|safe|UNRUN_RESOURCE_GATE|
|N.budget_bad|safe|UNRUN_RESOURCE_GATE|
|N.closed_late|safe|UNRUN_RESOURCE_GATE|
|N.timeout|safe|UNRUN_RESOURCE_GATE|
|N.sender_bad|safe|UNRUN_RESOURCE_GATE|
|N.version_bad|safe|UNRUN_RESOURCE_GATE|
|P.repeat_event|safe|UNRUN_RESOURCE_GATE|
|N.window_reset|safe|UNRUN_RESOURCE_GATE|
|M.stale.safe|safe|UNRUN_RESOURCE_GATE|
|M.stale.mutant|mutant|UNRUN_RESOURCE_GATE|
|M.version.safe|safe|UNRUN_RESOURCE_GATE|
|M.version.mutant|mutant|UNRUN_RESOURCE_GATE|
|M.exit_only.safe|safe|UNRUN_RESOURCE_GATE|
|M.exit_only.mutant|mutant|UNRUN_RESOURCE_GATE|
|M.closed.safe|safe|UNRUN_RESOURCE_GATE|
|M.closed.mutant|mutant|UNRUN_RESOURCE_GATE|
|M.duplicate.safe|safe|UNRUN_RESOURCE_GATE|
|M.duplicate.mutant|mutant|UNRUN_RESOURCE_GATE|
|M.unknown.safe|safe|UNRUN_RESOURCE_GATE|
|M.unknown.mutant|mutant|UNRUN_RESOURCE_GATE|

C09.ready、handoff意图、commit/持久ACK、receiver确认、handoff退出23见证均未生成。父协调器确实执行普通waitpid并记录child exit125/raw32000，这是首次启动失败的回收见证，未进入交接分类。resume_count=0、内部恢复0、独立resume调用0。

本次bootstrap认领、sealed memfd与C09持久交接属于不同责任：前者有实际前缀证据，后者未执行。exit125和缺ACK均阻断C09成功，原Root/H1–H8条件继续保持。[普通waitpid原件](<../../../DCL-R6-isolated-verification/batch07/native_snapshot/inputs/root_private/waitpid_886.json>)。
