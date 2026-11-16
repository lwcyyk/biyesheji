# 证据索引与主张强度

2026-11-10。Material Passport：证据导航与行政核对。只读管理查询、静态推导、动态资格分别登记。

|证据|内容/范围|
|---|---|
|[TASK_REQUEST](evidence/TASK_REQUEST.txt)|本次授权范围的原文副本|
|[BASELINE_LOCK](evidence/BASELINE_LOCK.json)|Repair 35文件冻结；原输出37项入场复核；四根导航快照|
|[WSL 列表](evidence/WSL_READONLY_LIST.json)|三个发行版均 Stopped/WSL2，无内部 Linux 命令|
|[WSL 版本](evidence/WSL_READONLY_VERSION.json)|安装组件版本，active_linux_kernel_observed=false|
|[Docker 状态](evidence/DOCKER_READONLY_INFO.json)|固定本地管道 info exit1；未启动 engine/container|
|[官方来源定位](SOURCE_INDEX.json)|各接口 URL、章节、读取状态及未认证的运行条件|
|[网页检索元数据](evidence/web/RETRIEVAL_INDEX.json)|只存 URL/状态/定位，latest systemd 超时与官方 v255 回退|
|[历史核对](evidence/HISTORY_INTEGRITY_CHECK.json)|原 batch62、ZIP60/59流、v3及历史研究锁行政复核|
|[交付核对](evidence/DELIVERY_CHECK.json)|九文档、JSON/链接、无新程序、未建batch02、历史账保持|
|[输出锁](evidence/OUTPUT_MANIFEST.json)|本轮文件及四根导航摘要；排除自身与 DELIVERY_CHECK，后者保存 manifest 摘要以避免循环|

旧原件入口：batch01/EVIDENCE_MANIFEST.json、DCL-R6/evidence/R6_OUTPUT_MANIFEST.json、DCL-R6-Repair/evidence/OUTPUT_MANIFEST.json。旧根导航条目分别从 revisions/DCL-R6-B 与 revisions/DCL-R6-Repair 验证；当前根文档只添加本轮导航，旧锁原文保持。

行政哈希复核不产生模型访问、资源校准、独立机器证明或外部复核。数学部分为当前会话辅助静态推导；原合同 E2 继续 UNRESOLVED。来源阅读范围足以支持接口边界，实际 kernel/systemd/权限仍待 P 阶段取证。
