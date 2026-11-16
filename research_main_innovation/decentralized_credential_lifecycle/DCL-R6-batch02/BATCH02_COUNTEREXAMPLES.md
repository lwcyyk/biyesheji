# batch02失败与反例登记

2026-11-10。Material Passport：资源执行失败证据；正式协议/算法反例0。

|ID|证据与分类|结论|
|---|---|---|
|B02-C02-SOFTTIME-001|原result_C02.status=FAIL，Controller信号9，Watchdog expired，300秒软截止；分配子探针未启动|RESOURCE_CALIBRATION；分析INCONCLUSIVE_LIMIT_CALIBRATION_SOFT_TIME|
|B02-POSTEXIT-OBS-001|C00/C01回收后的unit_show为空User/infinity/默认TasksMax；活时票据及native值正确|观测时窗/瞬态回收；不能据退出后默认值判断活时限制失效|
|B02-ADMIN-COPY-001|PowerShell Host保留变量导致封存副本误路径；已复制到正确根并核hash，Linux原件不变|行政错误；自动审批拒绝迁移/删除，误路径副本保留待清理|

首个资源失败原件位于host batch02/native_snapshot/inputs/result_C02.json，对应ticket/startup/watchdog_stop、Root关闭/空组、counter/journal均保留。没有MemoryError/AS触发/分配后状态或F1/F4轨迹；模型假设/协议安全/参考算法均未被这条资源失败检验。

静态最小后续方向为审查持久预留粒度/预付调度的成本与同一安全不变量，再提出具体资源接入修订及独立诊断授权。当前未编写修复、放宽预算、重启batch02或创建batch03；原失败和L-C哈希保持。

现有32k级预付成本的观测不足以唯一归因某个存储/内核因素。后续任何性能诊断也需匹配范围，不能用剩余额度临时做未冻结实验。主机制门CLOSED、严格分离0及强G覆盖不变。
