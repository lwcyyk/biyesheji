# MR回归、竞态与变异计划

Material Passport：ManagerRecovery-static-1/r5；64项固定夹具；实际执行0。

输入由48个safe场景和8组safe/mutant对照组成，共56 safe＋8 mutant。每项最多2帧，固定facts、动作、故障来源、注入位置、实际模拟响应、event_id、T0/R、退出与清理观察及独立判据；原始轨迹在未来Root私有mr_case_###.json保存，输入与原件SHA入受保护MR_QUALIFICATION。

覆盖正常review/resume、旧预期退出、当前责任有效、重复审查/恢复事实、PENDING策略片段；缺ACK/Receiver/waitpid、身份/boot/batch、旧快照、未审查退出、收据/日志错误、当前监督丢失、CLOSED、事件冲突；返回错误/异常、Root/Controller/Watchdog丢失、重复关闭、清理错误、已有STOP、预算未知、短写、子进程不退出、外部停止及并发/迟到事件。

|mutant|实际错误行为|独立检出条件|
|---|---|---|
|skip_review|把REVIEW_PENDING升级为预期成功|原始充分证据仍缺而实际成功/发放|
|missing_ack|在shadow中补ACK|原始ACK缺失仍实际成功|
|stale_snapshot|复用首次snapshot|原始当前fresh=false，subject使用旧状态发放|
|ignore_stop|忽略当前STOP|原始停止存在而实际发放|
|no_auto_close|关键故障不触发STOP/CLOSED|实际轨迹缺自动关闭|
|reactivate_closed|清除终态并恢复|终态后实际发放/closed回退|
|new_window_repeat|重复关闭重置T0/R|原始窗口/预算守恒失败|
|false_cleanup_success|未退出却报告确认|独立真实角色/错误观察与成功声明冲突|

oracle独立重算，safe要求无违规，mutant要求命中指定违规且违规集合属于冻结声明；未触发/未检出/意外错误/原件缺失立即停止。源码中的PASS条件仅为未来验收分支，当前所有actual、fault_exercised和detected均UNRUN。

原生验收阶段A使用新明确授权，运行真实C09→证据审查→恢复→C10，然后触发冻结返回78并要求原生关闭、账保持、退出和seal证据；它不进入S34/门18/模型。Root突然丢失等其他真实失效来源，如单次诊断仍缺充分证据，须另行明确独立故障诊断范围，不能把逻辑64项自动扩成全部物理覆盖。

计费：regression=1＋64×(12预付＋1总审)=833，专项硬界1,024；原生审查前置预付256，总完成1,089，总硬界1,536。原全校准62,546增加到64,082≤100,000；原共同5,000、RANGE20,000及所有时间/内存/任务上限保持。Root检查游标只在现有T0内单调消耗，未用部分保守占用。

[冻结输入](evidence/SOURCE_FINAL_R5/inputs/manager_contract.json) · [oracle导入/夹具一致性](evidence/FIXTURE_ORACLE_CONSISTENCY.json) · [资源重算](evidence/RESOURCE_BOUND_RECALCULATION.json)。

独立oracle还要求充分证据下确实形成REVIEWED_EXPECTED及首次恢复dispatch，并要求健康清理确实得到确认；总是拒绝或总是UNKNOWN的实现会触发FALSE_REJECTION/MISSING_LEGITIMATE_RESUME/FALSE_CLEANUP_REJECTION。
