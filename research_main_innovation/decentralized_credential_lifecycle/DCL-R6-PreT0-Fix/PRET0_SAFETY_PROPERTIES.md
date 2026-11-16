# PT-1–PT-10性质映射

Material Passport：PreT0Recovery-static-1/r3；静态映射；新增动态全部UNRUN。

|性质|代码/状态字段|独立测试与验收|
|---|---|---|
|PT-1 PhaseCorrectness|initial_query_scope/manager_checkpoint/runtime_checkpoint；单调phase|fresh_pre、work_before_arm、force_runtime_pre|
|PT-2 NoSyntheticRuntime|pt_context的T0/R=null；runtime intent与真实state/counter创建分开|pre_native_not_applicable、new_budget_after_fail|
|PT-3 CheckpointIntegrity|严格默认检查点、公开Root运行checkpoint、counter不可变身份|missing/corrupt/wrongbatch/boot/budget；missing_checkpoint_pass|
|PT-4 NoPreT0Work|require_work在systemd-run前；READY无工作权|work_before_begin/during_init/before_arm、正常work正控制|
|PT-5 AutomaticStartupAbort|原wrapper/STOP优先＋认证startup期限；无运行态也有停止依据|root/launcher/exception_preT0、no_auto_stop|
|PT-6 BoundedPreWindowCleanup|继承sealed120秒，不构造新deadline；后备及独立审计有界|deadline_expired、missing_deadline、exit_unconfirmed|
|PT-7 NoFalseClosure|process/application/native/admin分字段，未知保持|exit_known_app_unknown、unknown_as_success、admin_as_native|
|PT-8 EvidencePreservation|phase文件及目录同步、首错/停止/退出、自动post快照及完整双流|admin_write/manifest/digest/partialfile异常；行政SHA验证|
|PT-9 NoBudgetCreationOnFailure|独占初始化intent、原init_counter保持、失败无再次init/退款|duplicate_T0/counter、partialinit_abort、new_budget_after_fail|
|PT-10 NoReactivation|CLOSED/STOP及初始化intent优先；原claim一次性保持|closed_begin/late_work、reactivate_closed、重复seal|

oracle不导入生产lifecycle、guard或subject，独立追踪context/qualified/intent/state/counter/checkpoint/armed及终态。它既检查不安全接受，也要求合法work确实发放；纯预窗合法检查必须通过，缺上下文/过期或已初始化缺点不能误接受。

静态代码/输入/调用图提供对应责任证据。原生OS行为、磁盘持久性/调度、Root失效期间的完整停止、post导出和实际进程退出仍需阶段A及必要独立故障诊断；本轮不授RESOURCE_GATE_PASS或PASS_BOUNDED。
