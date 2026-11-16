# 阶段转换与真实失败时间线

Material Passport：PTA-PhaseFinalizer-static-1/r3；DCL-R6-PTA-PhaseFinalizer-Fix；2026-11-12；HOST_STATIC_ONLY。

真实状态机继续采用七个原阶段：PRE_WINDOW → PREFLIGHT_VALIDATING → PREFLIGHT_QUALIFIED → RUNTIME_INITIALIZING → RUNTIME_READY → RUNTIME_ARMED → RUNNING。INITIALIZATION_INTENT是持久对象，WORK是受守卫的动作；本轮未另造WORK_ENABLED状态。

|转换|前提/主体|持久动作、版本及读取|失败行为|
|---|---|---|---|
|初始→PRE_WINDOW|活体sealed/claim、Owner/child正确；初始Root child|exclusive ctx；phase/events seq0|异常经原wrapper自动abort，保留无T0状态|
|→VALIDATING|专用认证预窗scope|私有phase seq1、previous SHA；manager只读预窗查询|失败停止，不取得运行资格|
|→QUALIFIED|真实health与身份通过|私有phase seq2|停止/期限优先|
|→INITIALIZING|新实例、无运行对象；单次初始化|exclusive runtime intent先持久化，phase seq3|部分对象保留，原claim消耗，拒绝回退|
|→READY|真实state/counter/COMMITTED intent完成|同一phase_guard内发布私有seq4与Root公开checkpoint/record digest|IO或发布中断后保留不一致原件并拒绝工作|
|→ARMED|原停止器活体、boot/stop_at匹配、原父资源检查；当前scheduler|同锁校验旧READY，私有seq5及公开q一起完成后解锁|超时/非法阶段/终态失败即abort|
|→RUNNING（WORK）|当前scheduler；q确为ARMED；原C00/后继资格仍各自要求|require_work同锁校验并发布seq6；成功返回后原launch_one继续|READY/未知点/损坏/关闭均拒绝发放|

每个阶段记录的序号等于状态机中的固定索引；Root校验公开phase/seq、私有phase/seq、phase记录SHA及初始化ID。发布者与Root读取者使用同一把Root私有锁，读方在锁外等待时不拼接检查点。

历史batch11的实际BOOTTIME：PRE_WINDOW66.811319376；VALIDATING66.820658042；QUALIFIED66.874374079；intent sample66.885179620；INITIALIZING66.888638365；T0=66.896850269；READY66.914956317；私有ARMED67.109909234；公开armed checkpoint sample67.118473361；STOP67.121192409；CLOSED67.139362562；child waitpid125在67.226047790；最终内部关闭confirmed67.371083714；native manifest67.382156380。

停止服务异常在清理后输出到journal，MONOTONIC67.397984出现PT_RUNTIME_PHASE_DRIFT、67.405716为systemd退出125见证。打印时间和精确抛错时刻分别保留。新版本全部上述转换和并发调度实际UNRUN。

[历史原始phase链](evidence/PTA_ORIGINALS/native/inputs/root_private/boot/pt_events.jsonl) · [持久点](evidence/PTA_ORIGINALS/native/inputs/PT_RUNTIME_CHECKPOINT.json) · [原始journal](evidence/PTA_ORIGINALS/host/RUN_BOOT_JOURNAL.stdout.raw)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原安全、条件结论及强G覆盖裁决保持。
