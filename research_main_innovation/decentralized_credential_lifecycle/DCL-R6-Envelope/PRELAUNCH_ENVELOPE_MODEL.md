# 启动前资源包络模型

2026-11-10。Material Passport：纸面状态机与证明责任；无启动器代码、无执行。原合同 E2=UNRESOLVED；AS4-PAYLOAD/1 为待批准的条件替代。

## 1. 两个集合与明确边界

P_W(t)：原合同中的 Controller、Watchdog、Worker、Probe、预算/日志辅助进程及其子孙；Launcher 若作为批次工作角色新增，必须说明计入情况。每进程采用原 Windows WorkingSetSize，进程间共享页重复计量。

P_L(t)：拟议 Linux service 中**已成功进入批准目标映像**的活进程及它们的全部子孙；按 TGID 计一次进程，同一进程的多个线程共享地址空间。角色 C（Controller＋顺序 Worker＋预算＋日志）、W（独立 Watchdog）和意外/校准子进程全部计入，最多 4 个任务的内核限制比进程数限制更保守。主进程的动态链接器、解释器加载和模块导入均在计量范围内。

拟议边界排除：预先存在的 Windows/WSL 宿主、Linux 内核、systemd 系统 manager、外部 Launcher，以及 systemd 从 fork 到目标 exec 成功之前的可信设置助手。这些开销明确列入外部 TCB 记录；目标 exec 失败的设置助手仍属 TCB。将所有单位内 pre-exec helper 自动视为已受 AS 约束缺乏依据。该排除需要用户对合同边界的明确批准。

## 2. 状态与准入顺序

|状态|允许动作/证据|失败后行为|
|---|---|---|
|S0 SEALED_UNAUTHORIZED|只读旧锁、纸面合同；当前状态|保持关闭|
|S1 PLATFORM_READY|获独立部署授权后认证实际 kernel/systemd/cgroup/native Python/权限|任何能力缺失停在平台记录|
|S2 LOCKED|冻结授权、runtime/模型/资源适配器/单位属性/输入/全部命令摘要；单次批次身份|摘要不符或旧批次身份即拒绝|
|S3 ENVELOPE_ARMED|外部受信 Launcher 登记 boot_id、T0/deadline，预置停止事件，manager 建立 pids 限制与限制属性|创建/计时事件确认失败即撤销整个新单位|
|S4 PREEXEC_TCB|systemd helper 在 exec 前设置 AS soft/hard、降权、封闭管理能力|设置失败以失败退出；model 运行 0|
|S5 PAYLOAD_ENTRY|exec 成功，动态链接器第一条用户态指令之前 AS 已生效；这是拟议 RSS 内存计量起点|缺映像/限制继承证据则资格失败|
|S6 REGISTERED|C 创建 W；W 通过继承已受限；双向身份/心跳/固定 deadline/账摘要握手|任一握手失败整组终止|
|S7 CALIBRATION|完整矩阵共享一份账、一个 deadline|关键 FAIL/INCONCLUSIVE 即关闭|
|S8 QUALIFIED|实际校准全部通过后持久化匹配摘要的资源收据|收据缺失/更改输入即拒绝模型|
|S9 F1_THEN_F4|原业务五文件和冻结输入，F1→F4 顺序；同一全局账|超限、故障或语义异常立即封存|
|S10 CLOSED|全部 payload 退出、组 populated=0、封存峰值/账/结果|残留任务或日志不完整按失败封存|

这是一份非可执行的部署规格。当前 v3 的 `require_strict_bound_adapter()` 仍主动拒绝，S1–S10 未实现/未运行。

## 3. 首指令责任证明

Linux 目标程序自行 setrlimit 的顺序为“先执行解释器，后设限制”，覆盖从 t_apply 起的后缀。由该后缀无法推出 t<t_apply 的上界。systemd 方案将设置放在目标 exec 前，配合受信内核的新映像加载语义，条件性覆盖链接器与 Python 首入口。[LimitAS 的官方接口](https://raw.githubusercontent.com/systemd/systemd/v255/man/systemd.exec.xml)支持 soft:hard；目标平台的有效配置与加载路径仍须认证。

降低 rlimit 可在已有地址空间超过限额时成功，因而“helper 的 setter 成功”单独无法证明其当前 AS≤A。本文将该阶段明确保留在外部 TCB；成功 exec 的初始映像 AS 以及特殊映射须由固定 kernel/runtime 的入口审计确认，后续才使用增长限制和继承归纳。

Windows 候选时序为：预建 Job/属性→暂停创建→读回身份/归属→应用 HardWS→读回→Resume。JOB_LIST 能提前成员归属；HardWS 应用前的创建阶段和 Launcher 仍是原合同证明责任。主线程暂停也无法推出 WS=0。

## 4. 墙钟边界

替代合同仍给批次预算 1,800 秒。T0 在外部 Launcher 向 manager 提交首次批次激活**之前**持久化；从 T0 起所有启动、校准、故障、重放和退出等待均消耗同一窗口。平台安装/首次启动认证若单独授权，则明确处于批次外。P_L 内存起点晚于 T0，两个起点分别登记。

绝对 deadline=T0+1,800 秒，使用含挂起时间的 Linux [CLOCK_BOOTTIME](https://man7.org/linux/man-pages/man2/clock_gettime.2.html) 语义并绑定 boot_id；宿主/WSL 暂停如何推进实际时钟尚待认证。可在 T0+1,740 秒停止工作并发送整组 SIGKILL，留 60 秒退出核对；这是一项工程余量，缺少内核终止延迟上界时无法推出固定时限全退出。`RuntimeMaxSec` 按服务 active 时间触发，与 T0 有差异。[service 文档](https://raw.githubusercontent.com/systemd/systemd/v255/man/systemd.service.xml)的 timeout/kill 提供终止机制，未提供实时调度和不可中断等待的统一上界。

替代申请须明确：接受“绝对截止停止发放＋提前整组终止＋退出取证；超时退出为 INCONCLUSIVE_LIMIT”，或提供可认证的实时平台保证。原合同的无条件 1,800 秒全退出主张继续未决；用户回复授权也无法替代技术前提。
