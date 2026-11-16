# 预窗与运行态状态模型

Material Passport：PreT0Recovery-static-1/r3；状态定义及持久化合同。

|阶段|Root保护对象及允许动作|失败解释|
|---|---|---|
|PRE_WINDOW|pt_context由已认证ticket/claim/Owner生成；T0/R=null|无运行对象是正常状态|
|PREFLIGHT_VALIDATING|临时认证query scope，只读部署/身份/manager|失败自动停止，不能授运行资格|
|PREFLIGHT_QUALIFIED|预窗检查通过的phase记录|只允许进入一次初始化或预声明77失败诊断|
|RUNTIME_INITIALIZING|独占pt_runtime_intent先于真实T0/state/counter|部分创建即失败，不再降级预窗|
|RUNTIME_READY|真实state/counter/intent及公开Root checkpoint持久完成|允许健康读取及停止器初始化，工作关闭|
|RUNTIME_ARMED|停止器、Owner及父资源条件已验证|允许首次真实工作入口|
|RUNNING|实际工作前单调转换；原C/模型资格仍逐项要求|checkpoint真实缺失/损坏继续fail-closed|
|STOP_REQUESTED/ABORTING|原HALTED/STOP优先，首错固定|保留实际对象、原window及预算|
|CLOSED/STARTUP_ABORTED|原CLOSED吸收，预窗T0/R保持null|原claim/namespace不可重新使用|

pt_context是启动前认证收据，包含Root owner、当前boot/源/执行锁/授权SHA、ticket摘要和既有preflight_deadline。它不包含运行T0、预算或工作许可，也不能替代C00/资源资格。

phase记录有序号、前条SHA和append事件，每次文件及目录同步；Root公共runtime checkpoint绑定初始化ID、真实window和counter不可变身份。运行时失去checkpoint时拒绝继续，初始化intent避免“丢文件→猜成新批”的回退路径。

进程清理、应用关闭与封存是不同字段：CLEANUP_CONFIRMED只表示对应退出观察；内部未知仍记UNKNOWN；ADMIN_EVIDENCE_SEALED只表示行政快照/日志摘要完整；native状态另列。尾部caller退出继续由自动事后审计或后续外部审计确认。
