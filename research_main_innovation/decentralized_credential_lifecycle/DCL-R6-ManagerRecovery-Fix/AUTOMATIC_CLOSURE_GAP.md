# 自动关闭缺口与修复覆盖

Material Passport：ManagerRecovery-static-1/r5；MR-3=CONDITIONAL_PASS；真实停止响应UNRUN。

关闭复用CalDiag实际完成回收的原stop_tree和seal，并增加共同abort入口。Root调用先设置本地HALTED并尝试持久STOP，随后读取预算快照与固定首错，进入ABORTING；发布原CLOSED标记，执行既有停止，失败时尝试固定本批slice的stop/kill与稳定pidfd补充回收。原T0、deadline、预算和预留不被清理路径重建。

|失败来源|停止责任与保留结果|
|---|---|
|恢复前言错误/抛异常|_launcher_body外层覆盖权限、授权、版本、manager、lock等前言；统一abort|
|普通非零返回|Root协调器wait路径保留原码并abort；23必须有原真实交接证据|
|Root协调器丢失|独立停止器从当前state或保护handoff核对Owner，AWAIT期间身份继续受监督|
|Controller/Watchdog异常|原局部监督保持；非预期FAIL/退出传回Root后调用fail/abort；指定C06–C09故障按原测试语义审查|
|独立停止器构造/循环异常|完整external_stop外层覆盖，保持Root外部停止能力；角色丢失还由Root主循环/检查点发现|
|STOP/CLOSED已存在|STOP保持取消优先；CLOSED不可回退，首错与关闭事实保持，后续调用幂等|
|日志/收据/预算不确定|继续尝试停止，保留UNKNOWN及各次失败信息；预算原件保持|
|子进程拒退/未回收|先STOP，稳定pidfd与原有限回收；未确认退出保持UNKNOWN，禁止假报全退出|
|清理再次失败|原停止＋固定本批systemctl后备；错误留在close_attempts和首错，缺证据继续UNKNOWN|

fork前发布SPAWNING标记，child和parent在发go之前发布稳定子进程身份。Root局部reap未完成时，确认/封存均受阻。Root在SPAWNING而身份未发布时死亡，外部停止可以阻断本批Payload，但全体进程退出证明保留UNKNOWN；该状态不会被空目标集合误判成功。

关闭使用mr_close锁固定首个失败和原window，后续close_attempts保留每次错误。当前CLOSED保持原不可变标记，重复stop可追加观察记录。Root预算流式hash避免读取大journal形成整块内存负担；并发的已预留操作可能结束，原保守占用语义保持，未知账状态单独标注。

封存由正常Root owner或仅剩的独立停止源尾部执行，使用独立seal锁。正常分支等待独立停止器退出；当停止源负责失败关闭时，parent主动委托尾部，避免相互等待。尾部须证明其他已登记角色退出、Receiver关闭、CLOSED及Payload为空，记录caller_exit_pending；调用者自己的最终退出由事后审计验收。未回收或未发布身份禁止伪造完整封存成功。

时界：查询单次≤1秒/审查≤2秒，锁等待2秒；复用原停止15＋5秒，仅在原deadline尚余20秒时调用；Root角色grace30/reap5及seal等待20均受剩余原deadline约束。未取得可信deadline时只做有限后备并保留UNKNOWN，不建立新的预算时间窗。有限性依赖内核、systemd及IO按声明条件返回；全部停止源、PID1/内核或不可返回IO同时失效的通用保证继续UNRESOLVED。
