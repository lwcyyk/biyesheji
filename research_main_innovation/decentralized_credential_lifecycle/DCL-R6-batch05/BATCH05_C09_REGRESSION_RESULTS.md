# batch05 C09H 34 项合成回归

Material Passport：DCL-R6-batch05；C09Fix-static-1/r1；真实执行后证据分析；2026-11-11；复跑 0。

34 项全部执行、完成并获得冻结 Root 独立 oracle 接受：**28 PASS，6 MUTATION_DETECTED**。逐项原始摘要离线核对错误 0；checker SHA-256 `7770f85435089af3e2cb0bda28ba9e759ba6624b3f766ce1823514b788e126da`。driver 的 root 结果文件记录在 T0+19.586482022 秒；其后执行 Root 34 次记账与独立重算，产生 `C09H_QUALIFICATION.json`（accepted=true）。该时间仅表示 driver 结果，独立 Root 资格文件未单列完成时刻。

合成初态及每步 facts、ACK/receiver/witness、事件偏序、分类次数、binding 和原始摘要见各 case 目录的 event 文件及 result。`write_interrupted`、`fsync_failed`、receiver 故障等注入在合成事实层执行。真实 socket ACK、实际接收进程崩溃、物理 fsync 故障与交接 waitpid/pidfd 顺序覆盖仍由真实 C09 另取证。表中空违规集代表相应 oracle 接受。

|case/原始目录|冻结事件顺序|variant|期望终态|实际终态|结果|H 违规|
|---|---|---|---|---|---|---|
|[P.commit_before_exit](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/P.commit_before_exit>)|prepare → commit → exit23 → witness23 → observe → verify|safe|VERIFIED|VERIFIED|PASS|∅|
|[P.stale_read_then_commit](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/P.stale_read_then_commit>)|prepare → read_old → commit → exit23 → witness23 → observe → verify|safe|VERIFIED|VERIFIED|PASS|∅|
|[P.witness_first](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/P.witness_first>)|prepare → commit → exit23 → witness23 → observe → verify|safe|VERIFIED|VERIFIED|PASS|∅|
|[P.event_first](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/P.event_first>)|prepare → commit → exit23 → observe → witness23 → verify|safe|VERIFIED|VERIFIED|PASS|∅|
|[P.live_receiver](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/P.live_receiver>)|prepare → commit → exit23 → observe → witness23 → verify → repeat|safe|VERIFIED|VERIFIED|PASS|∅|
|[N.no_receipt](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/N.no_receipt>)|prepare → exit23 → witness23 → expire → observe|safe|FAILED|FAILED|PASS|∅|
|[N.other_exit](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/N.other_exit>)|prepare → commit → exit_other → witness_other → observe|safe|FAILED|FAILED|PASS|∅|
|[N.bad_batch](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/N.bad_batch>)|prepare → commit → bad_batch → exit23 → witness23 → observe|safe|FAILED|FAILED|PASS|∅|
|[N.bad_boot](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/N.bad_boot>)|prepare → commit → bad_boot → exit23 → witness23 → observe|safe|FAILED|FAILED|PASS|∅|
|[N.old_lock](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/N.old_lock>)|prepare → commit → bad_lock → exit23 → witness23 → observe|safe|FAILED|FAILED|PASS|∅|
|[N.receiver_unready](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/N.receiver_unready>)|prepare → unready → commit → exit23 → witness23 → observe|safe|FAILED|FAILED|PASS|∅|
|[N.write_interrupted](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/N.write_interrupted>)|prepare → write_interrupted → exit23 → witness23 → expire → observe|safe|FAILED|FAILED|PASS|∅|
|[N.fsync_failed](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/N.fsync_failed>)|prepare → fsync_failed → exit23 → witness23 → expire → observe|safe|FAILED|FAILED|PASS|∅|
|[N.receiver_died](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/N.receiver_died>)|prepare → commit → receiver_dead → exit23 → witness23 → observe|safe|FAILED|FAILED|PASS|∅|
|[N.stop_lost](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/N.stop_lost>)|prepare → commit → stop_lost → exit23 → witness23 → observe|safe|FAILED|FAILED|PASS|∅|
|[N.budget_bad](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/N.budget_bad>)|prepare → commit → bad_budget → exit23 → witness23 → observe|safe|FAILED|FAILED|PASS|∅|
|[N.closed_late](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/N.closed_late>)|prepare → close → commit → exit23 → witness23 → observe|safe|CLOSED|CLOSED|PASS|∅|
|[N.timeout](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/N.timeout>)|prepare → commit → exit23 → observe → expire → verify|safe|FAILED|FAILED|PASS|∅|
|[N.sender_bad](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/N.sender_bad>)|prepare → commit → bad_sender → exit23 → witness23 → observe|safe|FAILED|FAILED|PASS|∅|
|[N.version_bad](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/N.version_bad>)|prepare → commit → bad_version → exit23 → witness23 → observe|safe|FAILED|FAILED|PASS|∅|
|[P.repeat_event](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/P.repeat_event>)|prepare → commit → exit23 → witness23 → observe → verify → repeat → repeat|safe|VERIFIED|VERIFIED|PASS|∅|
|[N.window_reset](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/N.window_reset>)|prepare → commit → bad_window → exit23 → witness23 → observe|safe|FAILED|FAILED|PASS|∅|
|[M.stale.safe](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/M.stale.safe>)|prepare → read_old → commit → exit23 → witness23 → observe → verify|safe|VERIFIED|VERIFIED|PASS|∅|
|[M.stale.mutant](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/M.stale.mutant>)|prepare → read_old → commit → exit23 → witness23 → observe → verify|mutant|None|FAILED|MUTATION_DETECTED|H2|
|[M.version.safe](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/M.version.safe>)|prepare → commit → bad_version → exit23 → witness23 → observe|safe|FAILED|FAILED|PASS|∅|
|[M.version.mutant](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/M.version.mutant>)|prepare → commit → bad_version → exit23 → witness23 → observe|mutant|None|VERIFIED|MUTATION_DETECTED|H1,H8|
|[M.exit_only.safe](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/M.exit_only.safe>)|prepare → exit23 → witness23 → expire → observe|safe|FAILED|FAILED|PASS|∅|
|[M.exit_only.mutant](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/M.exit_only.mutant>)|prepare → exit23 → witness23 → expire → observe|mutant|None|VERIFIED|MUTATION_DETECTED|H1|
|[M.closed.safe](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/M.closed.safe>)|prepare → close → commit → exit23 → witness23 → observe|safe|CLOSED|CLOSED|PASS|∅|
|[M.closed.mutant](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/M.closed.mutant>)|prepare → close → commit → exit23 → witness23 → observe|mutant|None|VERIFIED|MUTATION_DETECTED|H1,H4|
|[M.duplicate.safe](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/M.duplicate.safe>)|prepare → commit → exit23 → witness23 → observe → verify → repeat → repeat|safe|VERIFIED|VERIFIED|PASS|∅|
|[M.duplicate.mutant](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/M.duplicate.mutant>)|prepare → commit → exit23 → witness23 → observe → verify → repeat → repeat|mutant|None|VERIFIED|MUTATION_DETECTED|H6|
|[M.unknown.safe](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/M.unknown.safe>)|prepare → exit23 → observe|safe|PENDING|PENDING|PASS|∅|
|[M.unknown.mutant](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/c09_tests/M.unknown.mutant>)|prepare → exit23 → observe|mutant|None|VERIFIED|MUTATION_DETECTED|H1|

6 个 mutant 分别命中：stale/H2；version/H1,H8；exit_only/H1；closed/H1,H4；duplicate/H6；unknown/H1。预期异常的安全拒绝归为 PASS；变异终态为 VERIFIED 时，违规见证仍明确记为 MUTATION_DETECTED。Root 使用独立 c09_oracle 从冻结事件重建事实，无候选 subject 导入。

该阶段开始 R=37,020，driver 消耗 239、Root 审查消耗 34，共 273；273≤静态完成路径上界2,245≤硬限5,000。原校准共享 T0 与总访问额度保持。Root 审查最后一次 intent 由 euid0 替换，随后触发真实 C09 权限失败，详见 [预算](BATCH05_RESOURCE_ACCOUNTING.md)。

[逐项机器汇总](evidence/C09_REGRESSION_ACTUAL.json)、[Root资格原件](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/inputs/C09H_QUALIFICATION.json>)、[冻结合同](evidence/c09_contract.json)。
