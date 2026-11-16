# 运行时与启动代次边界

Material Passport：DCL-R6-FullChain-B；2026-11-13（Asia/Shanghai）；审查基线 RuntimeAdapt-static-1/r1 / ra01；仅主机静态审查；BLOCKED_STATIC_ADMISSION。


本轮停止于主机静态准入；当前Linux平台、boot_id、UID/GID和实际加载映射均为UNRUN_STATIC_ADMISSION。既有运行时锁得到字节核验，表中摘要为冻结期望，当前平台观测列保持空值。

|对象|冻结期望|本轮观测|
|---|---|---|
|GNU libc/Ubuntu包|2.39 / 2.39-0ubuntu8.12|UNRUN|
|Python|/usr/bin/python3.12；3.12.3；SHA e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f|UNRUN|
|loader SHA|5fc0940888e9d2e1a00e66d6b1a559c36364ee867683652e1074fa576952cc3f|UNRUN|
|libc SHA|755a371e86cc9f564ab54f66140747700fb0a103f698f659f2060f707897e09a|UNRUN|
|libm SHA|5dcc4d25466e29ca390ed6fabb371c69b65dff6fa4e91c34561057a020d6994a|UNRUN|
|systemd/kernel|255.4-1ubuntu8.18 / 6.18.33.2-microsoft-standard-WSL2|UNRUN|
|Payload UID/GID/cgroup|999 /989 /v2；父TasksMax4|UNRUN|
|本轮boot_id/进程/单位|未创建运行实例|N/A|

继承来源裁决：Root/dpkg/keyring受信且执行中无并发特权更新；新8.12 .deb payload尚缺独立再提取。既有包目录/签名/索引及已观测maps只支持既有条件性来源结论。path→exec原子性和后续特权替换边界保持。本轮授权原文保存了“保留现有运行时来源的条件性证明”的要求；执行收据因静态拒绝保持未签发。

TR-A2历史boot `27e8416d-3ba4-46fd-8b42-75e983f2dcfa`、R3133及实际映射结果只属于batch14。当前boot字段null，旧boot与旧nonce保持历史身份。

本轮动态用例0、WSL调用0、部署0、active entry0、目标模块导入0、源码修订0、重跑0。T0/deadline/R均为null；新增访问消耗0。历史结果单独引用。

[冻结运行时合同](evidence/FROZEN_RA_ORIGINALS/inputs/runtime_identity_contract.json) · [来源条件原件](evidence/HISTORICAL_REFERENCES/DCL-R6-RuntimeAdapt-Fix/evidence/PROVENANCE_DECISION.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
