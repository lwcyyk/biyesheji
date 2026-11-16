# S1–S9专项结果

Material Passport：DCL-R6-FullChain-B；2026-11-13（Asia/Shanghai）；审查基线 RuntimeAdapt-static-1/r1 / ra01；仅主机静态审查；BLOCKED_STATIC_ADMISSION。


当前完成0/34；safe夹具17项、mutant夹具17项均为UNRUN_STATIC_ADMISSION。PREPARED/COMMITTED、持久与并发预留、重复task_id、故障恢复、journal短写/EIO、N+1拒绝、CLOSED与身份拒绝各项覆盖均待当前批运行。

冻结RANGE驱动逐job建立独立local ledger，保留原始counter/intent/journal/事件及实际退出；即时range_evidence.check_job后，再由Root重新读取每个原始job。当前脚本只解析静态JSON/AST，生产checker、fixture、oracle调用数均0。

保守成功路径每actor界281=256事件＋19次API＋1部分写捕获＋5语义操作；总actor上界68。RANGE总20,000收费封套同时覆盖S34、Root重查、门18、预算聚合及两次重审，其完整静态推导见[预算核算](FULLCHAIN_RESOURCE_ACCOUNTING.md)。实际耗时、访问增量、退出状态均为null。

本轮动态用例0、WSL调用0、部署0、active entry0、目标模块导入0、源码修订0、重跑0。T0/deadline/R均为null；新增访问消耗0。历史结果单独引用。

[S34冻结输入](evidence/FROZEN_RA_ORIGINALS/inputs/safety_contract.json) · [完整静态登记](evidence/PLANNED_CASE_REGISTER.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
