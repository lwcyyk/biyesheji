# 64项正反、竞态及17项变异计划

Material Passport：C00Ready-static-1/r2；host有限静态修复；2026-11-11；新增WSL/服务/目标测试0。

64＝30基础场景＋17个mutant对照＋17个mutant。每项冻结初态、事件帧、实际模拟状态来源、期望结果、允许违规和原始证据；当前执行0。涵盖立即/阶段性READY、MainPID未赋值、exec阶段变化、字段次序、全部8项稳定错、错误单位/类型/proc/TasksMax/boot/PID、读取缺失、跨版本、退出、失败、超时及STOP/CLOSED。

|job|事件帧|variant|期望末态/违规|允许违规集|actual|
|---|---|---|---|---|---|
|P.immediate|ready|safe|READY|∅|UNRUN|
|P.starting|starting → ready|safe|READY|∅|UNRUN|
|P.pid_pending|pid0 → pid_assigned → ready|safe|READY|∅|UNRUN|
|P.transition|transition → ready|safe|READY|∅|UNRUN|
|P.field_order|cg_pending → starting → ready|safe|READY|∅|UNRUN|
|P.stable_lock|ready|safe|READY|∅|UNRUN|
|P.uid|uid_wrong|safe|FAILED|∅|UNRUN|
|P.gid|gid_wrong|safe|FAILED|∅|UNRUN|
|P.groups|groups_wrong|safe|FAILED|∅|UNRUN|
|P.caps|caps_wrong|safe|FAILED|∅|UNRUN|
|P.nnp|nnp_wrong|safe|FAILED|∅|UNRUN|
|P.as_hard|as_hard_wrong|safe|FAILED|∅|UNRUN|
|P.as_soft|as_soft_wrong|safe|FAILED|∅|UNRUN|
|P.cgroup|cg_wrong|safe|FAILED|∅|UNRUN|
|P.unit|wrong_unit|safe|FAILED|∅|UNRUN|
|P.type|wrong_type|safe|FAILED|∅|UNRUN|
|P.tasks|tasks_wrong|safe|FAILED|∅|UNRUN|
|P.proc_as|proc_as_wrong|safe|FAILED|∅|UNRUN|
|P.proc_cgroup|proc_cg_wrong|safe|FAILED|∅|UNRUN|
|P.boot|starting → boot_wrong|safe|FAILED|∅|UNRUN|
|P.pid_reuse|pid_reused|safe|FAILED|∅|UNRUN|
|P.read_error|read_error|safe|FAILED|∅|UNRUN|
|P.missing_field|field_missing|safe|FAILED|∅|UNRUN|
|P.snapshot|cross_version|safe|FAILED|∅|UNRUN|
|P.exit|starting → target_exit|safe|FAILED|∅|UNRUN|
|P.service_failed|service_failed|safe|FAILED|∅|UNRUN|
|P.timeout|starting → timeout|safe|FAILED|∅|UNRUN|
|P.stop|starting → stop|safe|FAILED|∅|UNRUN|
|P.closed|starting → closed|safe|FAILED|∅|UNRUN|
|P.lock|missing_lock|safe|FAILED|∅|UNRUN|
|M.CR-01.safe|uid_wrong|safe|FAILED|∅|UNRUN|
|M.CR-01.mutant|uid_wrong|mutant|CR-01|CR-01|UNRUN|
|M.CR-02.safe|gid_wrong|safe|FAILED|∅|UNRUN|
|M.CR-02.mutant|gid_wrong|mutant|CR-02|CR-02|UNRUN|
|M.CR-03.safe|groups_wrong|safe|FAILED|∅|UNRUN|
|M.CR-03.mutant|groups_wrong|mutant|CR-03|CR-03|UNRUN|
|M.CR-04.safe|caps_wrong|safe|FAILED|∅|UNRUN|
|M.CR-04.mutant|caps_wrong|mutant|CR-04|CR-04|UNRUN|
|M.CR-05.safe|nnp_wrong|safe|FAILED|∅|UNRUN|
|M.CR-05.mutant|nnp_wrong|mutant|CR-05|CR-05|UNRUN|
|M.CR-06.safe|as_hard_wrong|safe|FAILED|∅|UNRUN|
|M.CR-06.mutant|as_hard_wrong|mutant|CR-06|CR-06|UNRUN|
|M.CR-07.safe|as_soft_wrong|safe|FAILED|∅|UNRUN|
|M.CR-07.mutant|as_soft_wrong|mutant|CR-07|CR-07|UNRUN|
|M.CR-08.safe|cg_wrong|safe|FAILED|∅|UNRUN|
|M.CR-08.mutant|cg_wrong|mutant|CR-08|CR-08|UNRUN|
|M.read.safe|read_error|safe|FAILED|∅|UNRUN|
|M.read.mutant|read_error|mutant|CR-READ_ERROR|CR-01,CR-02,CR-03,CR-04,CR-05,CR-06,CR-07,CR-08,CR-READ_ERROR|UNRUN|
|M.stale.safe|starting → uid_wrong → timeout|safe|FAILED|∅|UNRUN|
|M.stale.mutant|starting → uid_wrong → timeout|mutant|CR-STALE|CR-STALE,CR-WAIT-MISMATCH,CR-TIMEOUT|UNRUN|
|M.partial.safe|gid_wrong|safe|FAILED|∅|UNRUN|
|M.partial.mutant|gid_wrong|mutant|CR-02|CR-02|UNRUN|
|M.pid.safe|pid_reused|safe|FAILED|∅|UNRUN|
|M.pid.mutant|pid_reused|mutant|CR-PID|CR-PID,CR-READ_ERROR|UNRUN|
|M.boot.safe|boot_wrong|safe|FAILED|∅|UNRUN|
|M.boot.mutant|boot_wrong|mutant|CR-BOOT|CR-BOOT|UNRUN|
|M.stable.safe|uid_wrong → ready|safe|FAILED|∅|UNRUN|
|M.stable.mutant|uid_wrong → ready|mutant|CR-WAIT-MISMATCH|CR-STALE,CR-WAIT-MISMATCH,CR-REACTIVATION|UNRUN|
|M.timeout.safe|starting → timeout|safe|FAILED|∅|UNRUN|
|M.timeout.mutant|starting → timeout|mutant|CR-TIMEOUT|CR-STALE,CR-TIMEOUT|UNRUN|
|M.lock.safe|missing_lock|safe|FAILED|∅|UNRUN|
|M.lock.mutant|missing_lock|mutant|CR-LOCK|CR-LOCK|UNRUN|
|M.version.safe|cross_version|safe|FAILED|∅|UNRUN|
|M.version.mutant|cross_version|mutant|CR-SNAPSHOT|CR-SNAPSHOT|UNRUN|

17个mutant包括逐项忽略CR-01…08、读错视为匹配、陈旧快照、只查UID、错误PID/boot、把稳定失配降级STARTING、超时仍等、无锁放行和跨版本拼接。subject使用生产纯分类器；独立oracle不导入collector/policy/subject，依据冻结帧语义与实际observed原件重算，拒绝未触发/未检测/额外未声明违规。

模拟源与原生资格隔离：fixture函数只构建带明确SIMULATION_ONLY标记的过渡状态，不能进入原生collector或构造minted lease。真实系统字段、错误errno与就绪成本另由获准C00动态诊断取得。

计费entry1＋64×(保守预付6＋Root审核1)=449，专项硬限512；共享原C00 ticket及T0+300，不创建独立账/时间窗。该阶段在原共同5000的C09H/RootIPC/BC之前，完整cal硬访问上界62034+512=62546≤100000。原1000000/1800与cal300保持，额外采样/写盘耗时动态待测。
