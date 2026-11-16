# 严格内存上界：原合同缺口与条件替代证明

2026-11-10。Material Passport：静态数学推导/平台责任；机器校准 0。E2（原合同）=UNRESOLVED；下述条件定理尚未成为本机运行资格。

## 1. 冻结指标

设 B=2^32=4,294,967,296 字节。原指标为 M_W(t)=Σ[p∈P_W(t)]WS_p(t)，要求 ∀t M_W(t)≤B。WS 为 Windows WorkingSetSize；页按进程重复计入。PeakWorkingSetSize 是一个进程的历史峰值，Σ 各进程历史峰值可以作保守上界，前提是所有生命周期均有兼容、完整峰值且角色数/替换规则已证明；采样最大值只给已观察下界。

## 2. Windows 条件引理及未决责任

若对每一允许角色及其创建/退出过渡均有 WS_p(t)≤U_p，且合法并发配置集 K 封闭，便有 M_W(t)≤max[k∈K]Σ[p∈k]U_p。4×768 MiB=3 GiB 仅是此前稳态配置乘积。

本轮仍缺：首 Launcher/Controller 的完整启动界、暂停创建至 HardWS 应用阶段的界、所有子孙限制的不可绕过性，以及历史 PeakWS 与限制有效窗口的相容证据。v2 的 33,558,528 字节 PeakWS 比 33,554,432 字节 HardWS 多一页；设置前峰值/暂态/其他内部机制均尚未唯一鉴别。保留失败，缺口用 UNRESOLVED 表示。

[HardWS 官方语义](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-setprocessworkingsetsizeex)支持有效限制之后的条件推导。[Job 提交限制](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information)覆盖 commit。共享文件驻留页等计量差异使“Job commit≤B ⇒ ΣWS≤B”缺少一般依据。

## 3. cgroup-only 路线的严格障碍

memory.current 为组及后代的内存 charge；memory.peak 记录同一 charge 域的历史最大值，具体 reset 接口依内核版本核对；memory.events 与 local 需分开取基线/增量。memory.oom.group=1 是 OOM 整体处理，oom_score_adj=-1000 有例外。pids.max 约束 fork/clone，迁入或下调已有组可造成 current>max。

内核明确允许 memory.max 暂时超限。于是设 memory.max=B 的前提允许某时刻 charge>B，无法推出严格 charge≤B，更无法推出不同指标 M_W≤B。官方文档未给可直接代入的统一 overshoot 上界；预留固定百分比/页面余量不足以补证。来源：[cgroup v2 官方文档](https://docs.kernel.org/admin-guide/cgroup-v2.html)。

## 4. C 的条件定理

拟议合同 AS4-PAYLOAD/1：对 P_L 中每个进程定义 R_p(t) 为批准的普通用户映射的实际驻留虚拟页字节数；同一物理页跨进程/别名映射依各自驻留虚拟页计入。同一 TGID 的线程共享 mm，进程计一次。使用 Linux RSS 的映射含义，保留其与原 WS 的平台差异。内核页表、内核栈、未映射文件缓存、socket charge、VM/宿主、外部 TCB/pre-exec helper 开销列入范围差异。

前提逐项列明：

|编号|必要前提|本轮证据状态|
|---|---|---|
|A1|成功目标 exec 后、首条用户态指令前，其全部批准映射 AS_p≤A=1,073,741,824；RLIMIT_AS soft=hard=A 已设置|官方接口＋条件时序；实际加载路径未认证|
|A2|每次后继映射/栈增长均受该限制；硬限额无法提高；fork/exec 继承有效|官方 getrlimit 语义；实际权限/runtime 待核|
|A3|初始 payload 数≤4，pids.max=4 在任何成员出生前生效，组无越权迁入/迁出、调高限额或外部代理工作|静态安全策略；本机 cgroup/权限未核|
|A4|R_p 的每一计入页面属于受 A 约束的地址空间；普通匿名/文件/共享映射均覆盖；特殊设备/PFN/hugetlb/固定特殊映射逐项审计|需要目标 kernel/runtime 映射核对；当前保留条件|
|A5|全部业务/预算/日志/探针子孙都在 P_L；外部 TCB 边界获明确批准|角色已列；边界待批准|

**推导**：驻留页是其有效映射页的子集，故 R_p(t)≤AS_p(t)≤A。任务数包含各线程，因而活进程数 |P_L(t)|≤tasks(t)≤4。初始成立；普通分配受 A 限制；fork/clone 受 pids 限制且继承/共享受限映像；exec 重新满足 A1/A2；退出只移除条目。对合法转换归纳得：

\[
\forall t\ge t_{payload},\quad M_L(t)=\sum_{p\in P_L(t)}R_p(t)\le4\times2^{30}=2^{32}.
\]

共享页在每个进程中仍只占其相应虚拟页，重复计数已由四份 A 覆盖。A 按系统页粒度向下取整；确认页大小后使用 floor(A/q)q，推导保持 ≤B。巨大页/特殊映射先审计；缺少 A4 时禁止把该公式升级为完整 Linux RSS 定理。

降低 AS 软硬限制可能对已有超限映像成功；因此 setter 成功与初态 AS≤A 分别认证。Linux [getrlimit](https://man7.org/linux/man-pages/man2/getrlimit.2.html)给地址空间/继承/权限语义，[systemd LimitAS](https://raw.githubusercontent.com/systemd/systemd/v255/man/systemd.exec.xml)给目标进程属性接口。Windows Job 的 process-memory 提交上限、RLIMIT_DATA、Linux LimitRSS、Docker CLI as 均不能替代本前提。

## 5. 观测与证明的兼容性

VmRSS/VmHWM 作为观测字段保留；内核说明 RSS 计账存在异步性，可使用 smaps 作更精确快照。[proc 官方说明](https://docs.kernel.org/filesystems/proc.html)。跨进程依次读取也有时差，smaps 样本最大值仍无法直接认证所有瞬时峰值。memory.peak 继续标为 charged_peak，数值另列。

资格依靠已认证的 A1–A5 及内核强制界；观测用于发现前提违反和保留故障证据。任何观测超界、单位/字段范围不清、未登记映射、成员遗漏，都判资格失败/INCONCLUSIVE。避免用当前值减历史峰值、进程退出后的零值或配置值充作 actual_peak。

## 6. 结论强度

原合同：E2=UNRESOLVED。替代：**条件数学上界成立；实际前提未认证；合同未批准**。AS4-PAYLOAD/1 改变平台、计量范围、首入口和墙钟保证前提，必须单独接受。当前 RESOURCE_GATE_PASS=未取得，F1/F4=UNRUN_RESOURCE_GATE。当前输出符合“给出准确障碍＋提出候选替代”的终止分支。
