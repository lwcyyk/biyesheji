# batch07 BootContinuity40执行结果

Material Passport：DCL-R6-batch07；BootContinuity-static-1/r4；真实启动后首次失败；2026-11-11；复跑0。

计划40项（30 safe、10 mutant）；实际尝试0、完成0、通过0、变异检出0，全部UNRUN_RESOURCE_GATE。源中该套件在原C09H与RootIPC56之后、真实C09之前运行，本次在C00票据发布前停止。

|冻结case|variant|预期末态/违规|实际|
|---|---|---|---|
|P.same_boot|safe|STARTED|UNRUN_RESOURCE_GATE|
|P.cache_refresh|safe|STARTED|UNRUN_RESOURCE_GATE|
|P.after_first|safe|REJECTED|UNRUN_RESOURCE_GATE|
|P.during_prepare|safe|REJECTED|UNRUN_RESOURCE_GATE|
|P.after_final|safe|REJECTED|UNRUN_RESOURCE_GATE|
|P.during_exec|safe|REJECTED|UNRUN_RESOURCE_GATE|
|P.old_receipt|safe|REJECTED|UNRUN_RESOURCE_GATE|
|P.duplicate|safe|REJECTED|UNRUN_RESOURCE_GATE|
|P.request_only|safe|REJECTED|UNRUN_RESOURCE_GATE|
|P.launcher_exit|safe|REJECTED|UNRUN_RESOURCE_GATE|
|P.orchestrator_exit|safe|REJECTED|UNRUN_RESOURCE_GATE|
|P.stop|safe|REJECTED|UNRUN_RESOURCE_GATE|
|P.bad_batch|safe|REJECTED|UNRUN_RESOURCE_GATE|
|P.bad_lock|safe|REJECTED|UNRUN_RESOURCE_GATE|
|P.closed|safe|REJECTED|UNRUN_RESOURCE_GATE|
|P.resources|safe|REJECTED|UNRUN_RESOURCE_GATE|
|P.identity|safe|REJECTED|UNRUN_RESOURCE_GATE|
|P.cache_invalid|safe|STARTED|UNRUN_RESOURCE_GATE|
|P.artifact_drift|safe|REJECTED|UNRUN_RESOURCE_GATE|
|P.old_window|safe|REJECTED|UNRUN_RESOURCE_GATE|
|M.epoch.safe|safe|REJECTED|UNRUN_RESOURCE_GATE|
|M.epoch.mutant|mutant|BC-1|UNRUN_RESOURCE_GATE|
|M.snapshot.safe|safe|REJECTED|UNRUN_RESOURCE_GATE|
|M.snapshot.mutant|mutant|BC-3|UNRUN_RESOURCE_GATE|
|M.duplicate.safe|safe|REJECTED|UNRUN_RESOURCE_GATE|
|M.duplicate.mutant|mutant|BC-4|UNRUN_RESOURCE_GATE|
|M.request.safe|safe|REJECTED|UNRUN_RESOURCE_GATE|
|M.request.mutant|mutant|BC-7|UNRUN_RESOURCE_GATE|
|M.closed.safe|safe|REJECTED|UNRUN_RESOURCE_GATE|
|M.closed.mutant|mutant|BC-5|UNRUN_RESOURCE_GATE|
|M.budget.safe|safe|REJECTED|UNRUN_RESOURCE_GATE|
|M.budget.mutant|mutant|BC-6|UNRUN_RESOURCE_GATE|
|M.binding.safe|safe|REJECTED|UNRUN_RESOURCE_GATE|
|M.binding.mutant|mutant|BC-3|UNRUN_RESOURCE_GATE|
|M.resources.safe|safe|REJECTED|UNRUN_RESOURCE_GATE|
|M.resources.mutant|mutant|BC-2|UNRUN_RESOURCE_GATE|
|M.identity.safe|safe|REJECTED|UNRUN_RESOURCE_GATE|
|M.identity.mutant|mutant|BC-8|UNRUN_RESOURCE_GATE|
|M.cache.safe|safe|REJECTED|UNRUN_RESOURCE_GATE|
|M.cache.mutant|mutant|BC-2|UNRUN_RESOURCE_GATE|

没有模拟boot事件、注入、bc_case原始轨迹或BOOT_CONTINUITY_QUALIFICATION。本次真实sealed fd/exec观察与合成40项结果分别登记，Root入口消费一次不等于重复认领拒绝已测试。预付/审查481次是静态完成上界，本批这些语义访问0。
