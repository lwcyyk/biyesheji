# PreT0首次失败真实调用链

Material Passport：历史=MRA/batch10-r5；本轮=PreT0Recovery-static-1/r3；2026-11-12；新增动态0。

首先重核原MRA归档184成员、ManagerRecovery归档366成员；上轮baseline6,068文件及MRA当前184清单成员均匹配，当前历史基线6,257文件。原r5、CalDiag真实C09、MRA退出125、T0/R null、自动STOP/CLOSED、UNKNOWN、原生seal失败与行政ZIP完整性保持原件。

|步骤|真实调用/对象|状态及实际书签（BOOTTIME）|
|---|---|---|
|外部入口/预检|windows_entry→boot_continuity.prepare_activation|6994.920257185开始；r5/boot/源/资源预检通过6996.079301350|
|sealed认领/exec|同Root12242/start699487；entry_initial|6996.379147975；无T0/预算|
|Root child初始化|child_admission/child_initial|scheduler12300/start699639，记录后进入初始health|
|预窗状态读取|manager_recovery.health(initial)|state路径不存在，属于正常尚未创建|
|首个错误前提|failed_set→query(record=True)→G.root_checkpoint|manager_recovery.py:83首次无条件进入运行态checkpoint|
|异常产生|root_ipc.checkpoint|root_ipc.py:150要求batch_state，抛IPC_STATE_MISSING|
|向上传播|_launcher_work→_launcher_body wrapper→child异常处理|AdmissionBlocked，最终child/入口exit125，raw32000|
|自动STOP|abort/local HALTED/STOP_REQUEST|6996.456509400；先阻断新工作|
|固定首错|mr_first_failure|6996.461565999；error=IPC_STATE_MISSING、window=null|
|自动CLOSED|父协调器COORDINATOR_STOP_REQUEST→stop_tree|记录6996.462158609|
|父停止结果|stop_result|STOP后0.023635593秒，stop_exit0、empty=true|
|child退出见证|直接waitpid|6996.508153474；125|
|内部UNKNOWN|无runtime deadline/BOOT_START/STOP_ARMED；后备超时|6996.523022119；UNKNOWN保留|
|原生seal失败|G.seal→Boot.before_seal读取batch_state|6996.532321472，FileNotFoundError|
|事后退出/行政封存|只读审计及研究ZIP|角色全空、无父cgroup；22原件保存，行政ZIP独立成功|

batch_state本应由_root launcher在初始health之后创建，紧接原T0、deadline及counter初始化。缺失属于合法启动前状态；不存在已建立窗口的checkpoint被删除证据。旧依赖为“health通过才创建state，health又要求state”，构成确定性初始化循环。

旧静态审查覆盖了异常调用路径和语法，却未把调用者的生命周期阶段与被调函数的持久前提做对应；因此“有关闭wrapper”没有发现“尚无state却调用运行态检查点”。本轮新增显式phase及顺序检查，动态仍待后续许可。

[原始调用链/书签](evidence/HISTORICAL_FAILURE_FACTS.json) · [旧归档核验](evidence/HISTORICAL_ARCHIVE_CHECK.json) · [旧磁盘锁重核](evidence/PREVIOUS_LOCK_DISK_CHECK.json)。
