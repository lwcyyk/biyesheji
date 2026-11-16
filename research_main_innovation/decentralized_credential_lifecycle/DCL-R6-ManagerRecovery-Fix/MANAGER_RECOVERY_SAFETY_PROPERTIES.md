# MR-1–MR-10性质映射

Material Passport：ManagerRecovery-static-1/r5；静态责任映射；动态全部UNRUN。

|性质|代码/状态约束|对应夹具与验收|
|---|---|---|
|MR-1 ReviewedExpectedExit|capture、review_case、handoff_facts、historical；唯一event_id和实例属性|valid_review、wrong_exit23、forged_pass、missing_ack、missing_waitpid|
|MR-2 NoUnreviewedResume|classify及resume；PENDING无dispatch，原H.resume守卫继续检查|unreviewed_exit、pending_then_complete策略片段、skip_review变异|
|MR-3 FreshManagerState|stable两次单位读、failed集合书签、InvocationID/ExecMainPID与当前版本|stale_snapshot、version_between_reads、current_unit_restart、stale_snapshot变异|
|MR-4 NoFalseManagerSuccess|真实ACK/Receiver/直接waitpid/意图/来源/原预算和窗口；合成资格不能替代真实证书|receiver_missing、contradictory_ack、wrong_boot/batch、missing_ack变异|
|MR-5 AutomaticFailClosed|前言/普通返回/外部停止入口wrapper→abort；本地HALTED和STOP先于账快照|return_error、exception、root/controller/watchdog_lost、no_auto_close|
|MR-6 SingleClose|mr_close锁、首错exclusive、CLOSED吸收、close_attempts；相同事件复核返回同证书|close_repeat、concurrent_close及不同event_id；重复关闭重建window变异|
|MR-7 NoReactivation|CLOSED/STOP优先，Boot once保持，重复resume只返回dispatch=false事实|closed_resume、closed_late_review、reactivate_closed、ignore_stop|
|MR-8 BudgetConservation|原17预算/状态函数和range核心保持；检查前置预付，停止无init/reset|budget_unknown、new_window_repeat；阶段A原T0/账摘要比对|
|MR-9 EvidencePreservation|manager原始查询、文件及目录fsync、首错/各次close错误、原账快照|corrupt_log、short_log、receipt_write_fail、首次错误持续存在|
|MR-10 BoundedCleanup|原期限内的stop/grace/reap；未确认角色/IO失败保留UNKNOWN；固定本批目标|child_unresponsive、cleanup_error、false_cleanup_success；阶段A实际退出/封存|

合成Subject调用生产classify和closure_status，独立oracle只读取固定输入与实际模拟轨迹，重新计算充分证据、禁止发放、终态、预算和退出约束。它不导入guard、生产策略或subject驱动。输入fault_source/injection_point与静态调用图对应，合成结果仅说明相应有限策略/关闭状态模型，原生流程另行验收。

MR-1的历史根因有实际轨迹支持；本轮新恢复、自动停止、系统调用与归档行为继续条件化。尤其SPAWNING身份未发布、不可回收内核任务、全部停止源/IO失效、尾部调用者尚未实际退出等场景保留UNKNOWN/UNRESOLVED，静态PASS不升级为一般机器证明或PASS_BOUNDED。
