# LR：cgroup部署缺口与AS4责任

2026-11-10。Material Passport：PLATFORM_READONLY_LR。根层与现有system.slice实值来自15/16/22–24/27；新批次资源限制仍未设置。

## 1. 真实层级

|层级/字段|观测值|
|---|---|
|当前cat任务|0::/init.scope|
|根slice ControlGroup|/；TasksMax、MemoryMax、MemorySwapMax均infinity|
|根controllers|cpuset cpu io memory hugetlb pids rdma|
|根subtree_control|cpu memory pids|
|system.slice cgroup.type|domain|
|system.slice pids.max/memory.max/memory.swap.max|max/max/max|
|system.slice controllers/subtree_control|cpu memory pids / memory pids|

根cgroup.type读取ENOENT，命令23整体exit1，但随后两个控制器文件读取成功；27独立确认非根system.slice为domain。[内核文档](https://docs.kernel.org/admin-guide/cgroup-v2.html)规定cgroup.type在非根组存在，因此此项缺失符合该接口范围。保留原错误，不将其解释为cgroup v2不可用。

现有slice清单含system.slice、user.slice及若干系统子slice，无本批专用单位。未来`dclr6batch02.slice`拟为根直接子slice，各case/service通过Slice属性归属；system.slice为已观察的既有样本，不能自动当作新slice祖先。单批父slice总TasksMax=4须覆盖全部case及正式任务。

## 2. 五项证明责任

|责任|LR增量|当前结论|
|---|---|---|
|A1 首目标入口前设置|manager255实际接口可读，LimitAS现值无限|支持配置候选；exec前设置/初态仍未证|
|A2 完整映像/后续AS|已锁3.12原生ELF、直接库和关键stdlib|runtime合同变更待批准；初始AS、映射/继承与硬限额不可提高待证|
|A3 父总任务界|根pids已启用，实际样本层级domain|max并非4；创建、线程计数、禁止迁入/提额与重叠case待证|
|A4 映射计量|ELF静态依赖可列；hugetlb/WSL设备历史线索保留|特殊/PFN/hugetlb/驱动映射、RSS口径与全部闭包仍未决|
|A5 权限/代理/角色|root查询有据，专用身份缺失|专用UID/capability/cgroup写权/外部代理封闭未建立|

读到控制器/无限现值给出可部署基础，尚无`AS≤1GiB∧tasks≤4`同时生效的执行实例。仍需初态映像覆盖、出生/迁入时序、继承与角色闭包；只有这些成立，才适用ΣR≤4×2^30的条件定理。

## 3. 部署规则

由systemd作为资源层级单一管理者，目标普通UID无法写控制文件。创建前配置父层总限额，子service各自也设4task与AS双限；case串行且前一空组确认后进入下一项。已声明破坏性校准、失败重放和正式F1/F4共享一账/时窗，任何不确定账或退出未确认都关闭批次。

pids.max的迁入/下调组织操作例外、线程计数及后台helper责任继续保留。MemoryMax只作charge次级保护，无法由memory.max推导原ΣWindows WS或严格瞬时charge≤阈值。root/system.slice无限值还表明当前尚无所需批次上界，用户配置前不可准入。

AS4-PAYLOAD/1仅原则接受；原Windows WS4的E2=UNRESOLVED，RESOURCE_GATE_PASS=NOT_OBTAINED。CLOCK_BOOTTIME、T0+1740提前停止、1800秒全批窗口和整树终止仍待实际锁定/校准；新kernel boot_id与P不同，未来绝对计时必须绑定新的启动身份，禁止复用旧窗口。
