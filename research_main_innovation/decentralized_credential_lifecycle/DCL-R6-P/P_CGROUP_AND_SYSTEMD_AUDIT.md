# P：cgroup 与 systemd 审查

2026-11-10。Material Passport：实际平台观测＋既有官方接口语义复核；未创建/修改任何 service、slice、cgroup 或资源属性。

## 1. 三类直接证据

|对象|证据|可确认范围|
|---|---|---|
|文件系统|命令06为cgroup2fs；07挂载点/sys/fs/cgroup，类型cgroup2，rw、nsdelegate|实际使用cgroup v2挂载；rw为挂载属性|
|可用与启用|09含memory、pids；10含cpu memory pids|所读根层向子层可提供需要的控制器，相关名称已在该层启用|
|当前归属|08为0::/init.scope|本次cat进程的统一层级路径；拟议批次尚无对应slice/service|

PID1路径和systemctl255分别由命令03/04取得。default-hierarchy=unified为程序构建默认值，实际挂载/归属由06–10独立支撑。`nsdelegate`属于观测到的挂载选项，无法仅凭它推导目标UID得到资源写权限。

## 2. 拟议单位的接口对照

|部署要求|官方v255/内核静态语义|本机观察|剩余责任|
|---|---|---|---|
|系统service启动|Type=exec，目标exec前应用进程属性|PID1为systemd，工具255|实际manager版本/权限/命令锁、入口映像审计|
|AS上限|LimitAS支持soft:hard；RLIMIT_AS约束地址空间|Linux x86_64/WSL2；尚未读取/设置任何目标rlimit|soft=hard=1GiB的有效设置、初始映像/继承/特殊映射|
|父slice任务总数|TasksMax映射pids.max，包含线程；向子层分层生效|根层pids可用且启用|实际父slice/子service限制、禁止迁入/提额、运行校准|
|额外charge保护|MemoryMax/MemorySwapMax/OOMPolicy|根memory可用且启用|具体文件存在/有效值/祖先限制；oom保护例外|
|整组退出|KillMode=control-group/SendSIGKILL/禁止Restart|systemd程序存在|manager失效/时限/残留/辅助进程与停止事件的真实证据|
|权限封闭|Delegate=no、能力清空、NoNewPrivileges及IPC/文件系统策略|当前查询为root|专用payload身份、实际策略与外部代理封闭|

复用官方来源：[systemd.exec v255](https://raw.githubusercontent.com/systemd/systemd/v255/man/systemd.exec.xml)、[资源控制v255](https://raw.githubusercontent.com/systemd/systemd/v255/man/systemd.resource-control.xml)、[service v255](https://raw.githubusercontent.com/systemd/systemd/v255/man/systemd.service.xml)、[kill v255](https://raw.githubusercontent.com/systemd/systemd/v255/man/systemd.kill.xml)、[cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html)。这些来源已在Envelope核验，当前用实际主版本对照，未将公开文档当作本机setter/readback记录。

## 3. 仍未读取的层级事实

本次白名单未读取拟议system.slice/父slice的controller、cgroup.type、pids.max/current、memory.max/swap/peak/events、文件属主/模式、manager属性或实际写权限。目录尚未创建。根层有控制器，意味着后续路径具备候选基础；目标层级是否能正确配置仍需L阶段具体审查与授权。

未来保持systemd单一资源管理者，父slice覆盖所有case和正式service；同批总tasks≤4，而每个case的独立4任务配置只作为冗余限制。禁止外部迁入、上调限额和代理执行；每一case确认空组后进入下一case。pids控制器的组织操作例外继续保留。

memory.max暂时超限及charge/RSS区别继续适用。P阶段发现memory控制器无法消除这两个语义边界；内存主证明仍依赖AS＋任务数及其全部前提。

## 4. 文件系统与特殊映射线索

mountinfo显示根目录为ext4；在当前挂载快照中，拟议`/var/lib/dcl-r6/batch02`的已观察祖先落在根ext4。路径存在、属主、可用空间、持久性测试及最终runtime位置均待授权核验。Linux活账优先该原生文件系统，host封存复制保留原字节；`/mnt/d`为9p/DrvFS，当前未认证其活账锁/fsync语义。

`/dev/hugepages`存在hugetlbfs，另见WSL驱动/库挂载。这使特殊映射/设备可达性成为具体审计对象。挂载存在本身无法证明payload已使用巨大页/设备，也无法证明其已被禁止；A4/A5继续未决。

Gate P2=CONDITIONAL_PASS：cgroup v2与所需根控制器已观察，拟议执行层级/限制/权限仍待建立；原WS4的E2保持UNRESOLVED。
