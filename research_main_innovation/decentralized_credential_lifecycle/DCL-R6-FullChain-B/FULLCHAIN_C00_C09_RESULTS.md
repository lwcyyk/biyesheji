# C00–C09前置校准

Material Passport：DCL-R6-FullChain-B；2026-11-13（Asia/Shanghai）；审查基线 RuntimeAdapt-static-1/r1 / ra01；仅主机静态审查；BLOCKED_STATIC_ADMISSION。


当前C00–C09各项均为UNRUN_STATIC_ADMISSION。WORK、单会话预检、sealed capability、一次性认领、同进程exec、PreT0初始化、T0与预算建立、检查点和当前管理器健康均保持未观测。

|冻结阶段|主检查|当前结果|
|---|---|---|
|C00|内核身份/AS/cgroup/票据/映射等启动资格|UNRUN|
|C01|watchdog与当前组观测|UNRUN|
|C02|32896操作上界预付，96MiB受限内存子进程|UNRUN|
|C03|16MiB共享映射、4096页操作预付|UNRUN|
|C04|第5任务拒绝，task credit1|UNRUN|
|C05|local cap17、并发18次尝试与1次拒绝|UNRUN|
|C06|真实watchdog超时终止；MR审查预期退出|UNRUN|
|C07|controller exit23；MR审查预期退出|UNRUN|
|C08|watchdog死亡、后续grant拒绝/监视退出|UNRUN|
|C09前回归|C09H34→Root原件oracle→IPC56→BC40|UNRUN|
|真实C09|持久交接与直接父进程退出见证|UNRUN|

C00后的PT64/PF48/TR40/RA32/Ready64/MR64属于当前冻结完整路径中的必需回归，因容量冲突停在执行前。逐case开始/结束/耗时/访问/持久化/等待/切换/清理/检查/退出字段均以null记入[计划登记表](evidence/PLANNED_CASE_REGISTER.json)，没有以0秒代替测量缺失。

历史CalDiag C00–C09及真实交接PASS、TR-A2 WORK/C00 PASS分别保留其旧身份。

本轮动态用例0、WSL调用0、部署0、active entry0、目标模块导入0、源码修订0、重跑0。T0/deadline/R均为null；新增访问消耗0。历史结果单独引用。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
