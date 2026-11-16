# 三类资源后端：原合同下的裁决

2026-11-10。Material Passport：静态平台选型；输入为冻结 Repair、batch01、官方接口文档和本轮只读管理查询；新增校准/模型运行均为 0。实现门 CLOSED，严格分离实例 0。本文研究验证基础设施，未提出新的凭据协议机制或原创性分离声明。

## 1. 判定基准

原合同为累计访问 ≤1,000,000、总墙钟 ≤1,800 秒、全部受控角色的 **Windows 每进程 Working Set 之和**在每一时刻 ≤4,294,967,296 字节。共享页按进程重复计入；提交量、虚拟地址空间、Linux RSS、cgroup charge、VM 宿主工作集分别保留名称。

状态标签可以同时成立：PROVABLE_STATIC 表示写明前提的推导成立；REQUIRES_RUNTIME_VALIDATION 表示部署能力/故障证据待验；REQUIRES_CONTRACT_CHANGE 表示指标或边界发生变化；PLATFORM_UNAVAILABLE 指本轮未获得可用后端；UNSUPPORTED 指具体接口/用法缺乏支持。PLATFORM_UNAVAILABLE 只描述本次观察范围。

|比较维度|A：Windows Job|B：cgroup v2|C：完整 AS＋任务数|
|---|---|---|---|
|首指令前|预配 Job＋JOB_LIST＋暂停创建可覆盖目标主线程恢复后的执行；创建期/Launcher 仍需界|先设空组限制，再由受信启动器在组内创建；后移入组留窗口|systemd 在目标 exec 前设置 soft/hard AS；首个目标映像入口可条件覆盖；pre-exec helper 属额外边界|
|子孙封闭|关闭两类 breakaway；固定 Job 层级；所有创建由 Launcher；HardWS 逐成员复核|继承组；封闭迁组/管理 IPC/代理执行；组写权限独占|继承 AS，cgroup pids 控并发；同时满足 B 的归属条件|
|内存硬限制|HardWS 有官方上界语义；JobMemoryLimit 约束 commit；原峰值窗口待解|memory.max 允许暂时超限，缺少严格 overshoot 上界|条件引理 RSS≤AS，最多 4 个进程各 AS≤1 GiB；须核对完整映射与初始映像|
|原指标兼容|稳态兼容；完整生命周期证据仍缺|指标不同，charge 无法直接替换 ΣWS|Linux RSS/目标 payload 边界与原合同有差异|
|墙钟停止|绝对定时器＋整 Job 终止；响应延迟假设待证|组终止配合绝对 deadline；D 状态/宿主暂停仍是责任|同 B；RuntimeMaxSec 单独不足以证明 1,800 秒内全退出|
|访问计数|同一不可回滚账，grant 前持久预留|同左|同左；单 Worker 顺序运行简化并发|
|本机可用|Windows 存在，v3 静态候选且适配器缺失|三个 WSL2 发行版均 Stopped；Docker 固定本地端点连接失败|拟选 Ubuntu-24.04，systemd/cgroup/原生 Python 尚未认证|
|新增依赖|受信外部 Launcher/句柄及创建策略，尚未完成|Linux 内核、启动管理器和 native runtime|同 B；无需 Docker；仍需资源适配器与版本锁|
|本轮裁决|REQUIRES_RUNTIME_VALIDATION；排除外置 Launcher 时另属 REQUIRES_CONTRACT_CHANGE|REQUIRES_CONTRACT_CHANGE；PLATFORM_UNAVAILABLE；严格 memory.max-only 主张不足|PROVABLE_STATIC（条件引理）；REQUIRES_CONTRACT_CHANGE；REQUIRES_RUNTIME_VALIDATION；PLATFORM_UNAVAILABLE|

## 2. A 的具体结论

[Microsoft HardWS](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-setprocessworkingsetsizeex)给出 MAX_ENABLE 的上界语义。[JOB_LIST](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute)支持创建时 Job 列表；[CREATE_SUSPENDED](https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags)只承诺主线程暂停。二者提高目标入口覆盖，创建本身已存在映像/内核开销，仍须单列。

Controller 启动后自设 Job 的后置条件只约束设置之后。若 Launcher 也计入 P(t)，Launcher 自身首入口需要更外层包络；若将其作为外部 TCB，则发生计量边界变化。当前证据支持“此具体路径证明有缺口”，尚不足以给出 Windows 全部方案不可行的定理。

Job 工作集策略可进一步研究，但当前 32 MiB HardWS 对应历史 PeakWS 多 4,096 字节的时窗/统计兼容性仍缺证据。96 MiB Job commit 测试的历史峰值为 115,167,232 字节。两项均保留失败事实；增加容差无法完成原严格指标证明。[扩展限制结构](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information)明确区分提交限制。

## 3. B 的具体结论

[内核 cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html)的 memory.max 定义含暂时越界情形。该接口缺少可直接用于本合同的通用有限超调量，因此将阈值简单下调一页或固定百分比也缺乏充分依据。memory.peak/current/events 记录 charge；OOM 分组和任务数控制各有独立作用，详见证明文档。将这些字段登记为原 ΣWS 通过会混淆指标。

本轮未启动 WSL/Docker，尚未观察活动 Linux cgroup、权限及有效宿主限制；仅有 CLI 安装信息。Docker CLI 的 [as 选项官方说明为不支持](https://docs.docker.com/reference/cli/docker/container/run/#set-ulimits-in-container---ulimit)，据此排除该快捷命令。

## 4. C 的收敛选择

推荐 **C：WSL2 Ubuntu-24.04＋systemd 系统 service，RLIMIT_AS soft=hard=1 GiB、TasksMax=4**，以 cgroup 提供归属/任务数/组退出，memory.max 只作次级保护。这是待批准的 AS4-PAYLOAD/1 合同候选；原 Windows WS4 保持 UNRESOLVED。

此选择保留 4 GiB 数值和共享页重复计量的保守推导，代价是 AS 预留可能很早拒绝分配，并改变平台/范围/计时前提。[systemd 的 LimitAS 警示](https://raw.githubusercontent.com/systemd/systemd/v255/man/systemd.exec.xml)也提示其约束地址空间，常规内存配额通常宜用 MemoryMax；本方案有意选择保守 AS 上界，F1/F4 能否在其内完成仍待校准。方案搜索在此收敛，当前新增 guard 版本为 0。

Windows C 路线在本轮已审 Job 接口集合内为 UNSUPPORTED：ProcessMemoryLimit/JobMemoryLimit 给提交界，HardWS 给驻留界，尚缺覆盖全部映射/保留地址的完整 AS 强制接口证据。Linux 的 RLIMIT_AS 有明确接口；RLIMIT_DATA 只约束部分资源，RLIMIT_RSS/LimitRSS 在现代 Linux 缺少所需硬约束。该判断限于已审接口，保留将来新平台能力另行举证的空间。
