# 进程树、权限与失效模型

2026-11-10。Material Passport：静态威胁模型与失败时序；实际故障注入 0。采用 AS4-PAYLOAD/1 候选边界，原合同仍为 E2=UNRESOLVED。

## 1. 受信边界

TCB 包含 Windows/WSL 宿主、固定 Linux 内核、systemd 系统 manager、外部 Launcher、pre-exec 设置助手，以及只服务本批的特权配置权限。TCB 负责先设 pids/AS 属性、不可改策略、绝对停止源、固定映像加载和整组终止。管理员恶意改组、内核缺陷、宿主无限暂停均超出可证明调度假设；这些假设随替代合同一起提交批准。

P_L 包含 C（主 Controller，内含顺序 F1/F4 Worker、预算、日志）、W（独立 Watchdog）及全部派生/校准进程。C 的一个监督线程、W 主线程和 C 主线程共用最多 4 个任务额度，额外进程/线程仍耗同一 pids.max。每个新进程的 AS 硬限额继承，任何未登记成员均触发关闭。

建议系统级 service 在专用非特权身份下执行，Delegate=no，AS 硬限额禁止提高，能力集合清空，NoNewPrivileges=yes；cgroup 控制文件由外部管理器独占。普通 WSL 登录身份与 payload 身份隔离；禁止 payload 访问 systemd/用户 manager、Docker、cron/at、WSL interop 等可代建组外工作的接口。可通过单位文件系统/IPC/网络策略落实，最终规则须锁定和校准。[NoNewPrivileges 官方说明](https://raw.githubusercontent.com/systemd/systemd/v255/man/systemd.exec.xml)明确提醒，代理服务代执行仍需单独封闭。

这是针对固定、已审查验证程序和失效注入的部署模型。面向恶意任意程序的完整沙箱安全证明仍缺；仅凭 NoNewPrivileges 或 cgroup 归属无法排除外部代理。native Linux Python 为必要条件，禁止经 WSL 调用 Windows python.exe 充任受 cgroup 限制的 Worker。

## 2. 封闭性归纳

单批父 slice 在空成员时设 pids.max=4，涵盖全部后代 service；manager 负责在目标执行前关联。后继只允许在组内 fork/clone/exec；同一组继承、AS 继承和禁止特权提高共同保持不变量。禁止任意 cgroup.procs 写入、运行期更改 pids.max、迁入旧任务和未登记的外部再激活。父层更严限制可以造成提前失败，需读回有效祖先配置。

[内核 pids 说明](https://docs.kernel.org/admin-guide/cgroup-v2.html)区分创建限制与组织操作；迁入额外成员可以突破简单数量推导。故“所有孩子通常继承组”只完成其中一项责任。PID 复用通过 boot_id、starttime、pidfd/稳定进程身份处理；发现 PID 缺失或权限拒绝时保留 UNKNOWN，整组状态与退出信号共同取证。

Windows 候选保留：Job 层级固定、两类 breakaway 均关闭、Launcher 控所有创建、Job handle 不向普通 child 继承。嵌套 Job 只在锁定父层并验证有效限制后允许。[Job 官方语义](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)说明子孙/逃逸与句柄关闭规则。KILL_ON_JOB_CLOSE 依赖最后一个句柄关闭；外部还持查询句柄时须显式 TerminateJobObject，不能以 Controller 退出推定 Job 已终止。

## 3. 失败处理时序

所有失败统一进入 ABORTING：停止 grant→记录原因/已占用额度（日志故障则保留残片）→请求 manager 结束整组→核对 populated=0/稳定身份退出→CLOSED_*。W 只具向稳定 C 身份发送终止信号的最小权限；manager 因主进程退出执行 KillMode=control-group；W 无须广泛管理服务权限。外部绝对停止事件提前安装且独立于 Launcher 存活。

预声明的破坏性校准 case 使用一次性故障票据；expected exit 和完整清理/账证据均匹配后，外部 Launcher 才能按冻结清单激活下一 case，同一父 slice/账/deadline 持续有效。模糊账、额外错误或停止未确认都关闭整批。事务中断测试用已全额预收费的局部测试账；真实总账出现模糊预留时禁止继续。

|故障/输入|检测与停止源|封存与限制|
|---|---|---|
|Launcher 在提交前退出|尚未激活；一次性票据失效|batch 身份记中止；已花平台时间另列|
|Launcher 提交后退出/断线|manager 保留单位/绝对停止事件；C/W 失去启动租约即停|禁止重复 launch 创建第二账；manager/租约机制须校准|
|C 崩溃/正常提前退出|manager 主进程退出事件＋W pidfd|整组 KillMode，资源失败优先于业务 exit0|
|W 意外退出|C 监督线程 waitpid/pidfd/心跳；下一 grant 必查|停止业务，C 退出触发组清理；C 也失去响应时由 manager 外部停止源兜底|
|Worker 无响应/GIL 或 IO 阻塞|W 心跳/进度租约到期，向 C 发送 SIGKILL|C 退出引发整组清理；不可中断等待保留时间责任|
|子进程/线程出现|内核 pids/继承 AS 立即约束，身份注册检查|未经批准即关闭；第 5 任务创建应被内核拒绝|
|AS 耗尽/栈扩张失败|ENOMEM/MemoryError/SIGSEGV，W/manager 观察|INCONCLUSIVE_LIMIT；失败分配记录后退出，禁止自动降低模型域重跑|
|cgroup OOM|OOMPolicy=kill＋memory.oom.group=1，配置读回|payload oom_score_adj 避免 -1000；事件/退出封存；cgroup charge 峰值另列|
|累计状态额度耗尽|grant 前原子持久预留检查|最后合法额度之后拒绝；模糊预留保持已耗|
|T0+1740/绝对 deadline|manager 预置停止源、W、C 三方固定同一 deadline|提前 SIGKILL；截止仍存活记 INCONCLUSIVE_LIMIT/STOP_UNCONFIRMED|
|日志短写/磁盘满/fsync 失败|日志组件失败回传→停止 grant；W 心跳失效|保留原残片和预留意图；后续启动一律拒绝|
|计数 PREPARED/COMMITTED 中断|重读账发现模糊事务|占用预留，停止批次；禁止自动回滚或补窗|
|宿主/WSL/kernel 重启|新 boot_id 与锁冲突|关闭旧批，禁止自动恢复/Restart；保存重启后只读审查|
|manager/内核失效或无限暂停|超出普通用户态监督可保证的响应边界|原时间/终止证明保持未决；替代合同显式接受假设或拒绝执行|

## 4. 终止与证据语义

[systemd KillMode](https://raw.githubusercontent.com/systemd/systemd/v255/man/systemd.kill.xml)选 control-group；Restart=no，RemainAfterExit=no，无 ExecStop 辅助命令；首停信号拟用 SIGKILL，避免先等待用户清理。日志由运行期预先持续落盘，封存由组退出后外部完成。OOMPolicy=kill 的 [官方映射](https://raw.githubusercontent.com/systemd/systemd/v255/man/systemd.service.xml)是 memory.oom.group=1，不能仅根据属性名推定本机已经应用。

manager、C、W 均可能受调度延迟影响。文中的停止动作是可校准的故障处理设计，尚无固定毫秒响应上界证明。当前全部故障 actual=null，未将纸面动作登记为已观察安全终止。
