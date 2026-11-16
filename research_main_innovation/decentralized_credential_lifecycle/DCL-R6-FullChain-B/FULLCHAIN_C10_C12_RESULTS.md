# C10–C12资格结果

Material Passport：DCL-R6-FullChain-B；2026-11-13（Asia/Shanghai）；审查基线 RuntimeAdapt-static-1/r1 / ra01；仅主机静态审查；BLOCKED_STATIC_ADMISSION。


|case|冻结检查|本轮结果|静态全局访问界|
|---|---|---|---:|
|C10|提升AS/写cgroup/访问manager socket/AF_INET拒绝；Ready屏障|UNRUN_STATIC_ADMISSION|1|
|C11|PREPARED、short_write、counter_fsynced、journal_fsynced本地镜像故障；后续信用拒绝|UNRUN_STATIC_ADMISSION|5|
|C12|错误boot、deadline、CLOSED、root、重复初始化和独立formal拒绝；实际状态保持|UNRUN_STATIC_ADMISSION|7|

C10仅在真实C09恢复健康成立后进入。C11局部账故障与MR原生异常关闭验收分别登记；C12中的CLOSED文档测试与真实CLOSED后的只读证据也分别登记。当前清理幂等、预算保持及终态读取均无本批动态证据。

本轮动态用例0、WSL调用0、部署0、active entry0、目标模块导入0、源码修订0、重跑0。T0/deadline/R均为null；新增访问消耗0。历史结果单独引用。

[冻结probe](evidence/FROZEN_RA_ORIGINALS/src/guard_probe.py) · [逐case登记](evidence/PLANNED_CASE_REGISTER.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
