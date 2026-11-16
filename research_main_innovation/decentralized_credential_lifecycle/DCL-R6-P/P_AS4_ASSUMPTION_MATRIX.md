# P：AS4-PAYLOAD/1 前提逐项更新

2026-11-10。Material Passport：条件证明更新；P只读平台证据，RESOURCE_GATE_PASS=NOT_OBTAINED。合同原则接受的范围见本次授权§1，正式执行合同仍待批准。

## 1. 编号对应关系

本次任务将A1聚焦于设置顺序、A2聚焦于映像/后续映射、A5聚焦于权限/代理。Envelope原表的A1还包含初始AS、A2包含增长与权限、A5包含角色/TCB边界。为保留历史，采用下列对应，旧文件原文保持。

|本次编号|Envelope责任对应|
|---|---|
|P-A1 目标入口前设置|Envelope A1 的设置时序|
|P-A2 完整映像/后续AS|Envelope A1 的初始AS＋A2 的增长/继承|
|P-A3 父层总任务数|Envelope A3|
|P-A4 特殊/共享映射与计量|Envelope A4|
|P-A5 权限/代理/管理封闭|Envelope A2 的不可提额＋A3 的归属＋A5 的角色/TCB边界|

## 2. 前提状态

|前提|静态支持与平台实际证据|当前状态|尚缺证明/证据|
|---|---|---|---|
|P-A1|Linux x86_64；PID1为systemd；工具255匹配所用v255文档；LimitAS可作为exec前属性|STATIC_SUPPORTED；平台入口PLATFORM_OBSERVED；实际限制REQUIRES_CONFIGURATION/UNRESOLVED|具体目标runtime/单位/属性解析与readback；pre-exec助手边界；首用户态指令前设置；入口加载路径审计/校准|
|P-A2|RLIMIT_AS的地址空间/继承语义有官方依据；本机实际Linux内核已知|STATIC_SUPPORTED；CONDITIONAL；REQUIRES_DYNAMIC_CALIBRATION|native Python3.14缺已知路径；loader/stdlib/初始AS、全部映射增长、权限不可提额及exec/fork证据|
|P-A3|cgroup2fs；根controllers与subtree_control含pids；当前命令在init.scope|PLATFORM_OBSERVED（能力）；REQUIRES_CONFIGURATION；REQUIRES_DYNAMIC_CALIBRATION|单批父slice pids.max=4的真实设置；全部子service/线程纳入；迁入/迁出/提额/替换封闭；第5任务拒绝|
|P-A4|Linux RSS/AS条件关系已静态定义；mountinfo见hugetlbfs及WSL驱动/库|CONDITIONAL；UNRESOLVED|普通/固定特殊/PFN/设备/hugetlb映射的计入边界；实际runtime映射和限制；共享页重复计量；字段/单位/时间窗兼容|
|P-A5|本次查询为root；外部TCB/payload边界获原则接受；root挂载可见Windows盘|PLATFORM_OBSERVED（当前身份）；REQUIRES_CONFIGURATION；UNRESOLVED|专用非特权UID、capabilities、NoNewPrivileges、组写权限/manager/cron/Docker/WSLinterop等代理封闭；全部角色登记/故障终止|

本轮没有证据要求将某个整体前提登记UNSUPPORTED；也没有一个整体前提已经从接口支持升级为有效执行不变量。各行的PLATFORM_OBSERVED严格限于注明的子事实。

## 3. AS 1 GiB 与总 pids4 的共同建立条件

当前没有发现这两种Linux机制的接口冲突：RLIMIT_AS属每进程，pids属分层任务数；systemd255具有对应设置接口。它们仍需在一次受信部署中共同成立：

1. manager先建立空的单批父slice及总任务限制，再按冻结顺序创建子service；任何合法并发配置都由同一父限额覆盖。
2. 每个目标映像在exec前获得soft=hard=1,073,741,824字节；成功exec的初态AS及A4映射覆盖独立认证。仅setter成功无法证明原有超限地址空间已减少。
3. payload专用非特权身份无法提高硬限额或借管理/外部代理逃逸。父slice控制权由外部TCB独占。
4. 任务数包含线程，C主线程＋监督线程＋W预计占3task；第4槽只按冻结用途使用。多service串行、前一空组确认、无额外helper漏计；pre-exec TCB排除边界明确保留。

满足这些前提时可继续使用`Σ R_p≤|P_L|×AS_max≤4×2^30=2^32`的条件推导。P阶段没有配置任何一个目标限额，也没有从controller名称推出此不等式已在本机执行中成立。

## 4. 原合同、替代合同和时间责任

原Windows WS4：E2=UNRESOLVED。AS4-PAYLOAD/1：原则认可用于平台审查与后续申请，正式批次合同未批准。外部Launcher/systemd/pre-exec/kernel/宿主排除的范围获原则确认，相关TCB开销仍单列。

Linux普通用户映射实际驻留页和、跨进程共享/别名重复计量、特殊映射审计、charge诊断分别保留。memory.max暂时超限和Linux RSS计账/快照限制继续有效；P无法用新平台名称覆盖原失败。

本次未设置绝对停止事件、执行CLOCK_BOOTTIME查询、暂停/重启或终止校准。T0+1740提前停止与1800秒统一窗口的调度/宿主暂停/停止响应假设继续UNRESOLVED/REQUIRES_DYNAMIC_CALIBRATION。原则接受也无法替代其实际证据。

Gate P4=PARTIAL：接口承载平台获得更多真实支持，执行不变量与严格资源资格继续未取得。
