# 完整校准时间可行性

Material Passport：DCL-R6-FullChain-B；2026-11-13（Asia/Shanghai）；审查基线 RuntimeAdapt-static-1/r1 / ra01；仅主机静态审查；BLOCKED_STATIC_ADMISSION。


当前完整校准耗时=null；300秒判断=UNRUN_STATIC_ADMISSION。TIME_FEASIBILITY_OBSERVED_PASS尚未取得；本轮也没有触发INCONCLUSIVE_LIMIT，静态拒绝为实际裁决。

完整校准的300秒软截止从唯一T0起算；总墙钟1800秒、提前停止1740秒、pre-T0 TCB120秒保持冻结。访问上界不能推出存储I/O、调度、systemd切换和原始证据重查的严格时间上界。

历史CalDiag的C00–C09通过、C09H服务包络7.135260秒、IPC56跨度11.392948秒、BC40跨度10.200091秒及Ready64跨度8.899268秒继续属于旧轨迹。部分区间相互嵌套，原始fsync累计也可能与服务包络重叠；其合计无法给出当前完整链的300秒证明。历史在C09后恢复失败，C10–C12/S34/门18保持未完成。

当前[逐case登记](evidence/PLANNED_CASE_REGISTER.json)将开始/结束/耗时/访问增量/持久化/等待/服务切换/清理/证据检查/退出状态均保存为null。字段完整性与测量完成度分别判定。

本轮动态用例0、WSL调用0、部署0、active entry0、目标模块导入0、源码修订0、重跑0。T0/deadline/R均为null；新增访问消耗0。历史结果单独引用。

[历史测量原文](evidence/HISTORICAL_REFERENCES/DCL-R6-CalDiag/CALDIAG_CASE_DURATION_REPORT.md)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
