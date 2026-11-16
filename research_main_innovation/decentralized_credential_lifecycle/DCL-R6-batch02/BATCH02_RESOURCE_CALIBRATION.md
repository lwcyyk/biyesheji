# batch02资源校准实际报告

2026-11-10。Material Passport：RESOURCE_CALIBRATION。完整原件在host batch02/native_snapshot，未经改写的自动证据ZIP另留存。

|case|原始状态|实际范围|
|---|---|---|
|C00|PASS|冻结入口谓词通过；实际AS双限1GiB、UID/组/权限、父/子pids4及memory/swap/OOM策略读取匹配|
|C01|PASS|正常Controller/W握手、运行和退出，约3task在组内|
|C02|FAIL|300秒校准软截止在持久预付阶段到达，ExecMainStatus9/Resultsignal；分配子探针未创建|
|C03–C12|UNRUN|首个关键失败阻断；含数量/并发/故障/逃逸/事务/恢复完整矩阵未完成|

C00观测：Controller VmSize111,886,336字节，RSS异步值29,442,048字节，AS软/硬均1,073,741,824；父/子pids.max=4，pids.current=3。普通映射RSS快照29,446,144字节，无未审IO/PFN/hugetlb标志；kernel特殊区vvar/vvar_vclock的本次RSS为0，vdso为4096。它们按获批条件范围单列，快照无法证明所有瞬时峰值或原WindowsWS。

C00/C01退出后的瞬态单位可能已被manager回收，原unit_after会显示默认空User/infinity等值；这是退出/回收时窗，活时ticket及原生rlimit/cgroup实值另外保留，不能把默认桩值当作活时漂移或有效限制。

## C02首次失败定位

父程序先逐项调用Budget.visit持久预付，随后才会启动96MiB局部AS子探针。本次总账达到32191，缺少C02.child_process.json/child.json；目录和原调度证明分配子进程尚未启动。没有MemoryError、RLIMIT_AS触发结果或持有分配快照可供判定。

最后意图boottime699.708479722，case/校准截止699.708633895。Watchdog实际记录expired=true，并在截止附近终止Controller；根协调器保留C02原始FAIL，随后关闭父树。分析分类为**INCONCLUSIVE_LIMIT：CALIBRATION_SOFT_TIME**，资源资格门为FAIL。保持原始FAIL与原因分类两层，未改判为AS机制失败或通过。

静态源码每次额度预留包含文件/目录/journal/counter持久屏障；本次在预付阶段累计约300秒。现有证据支持“持久预付未能在软窗口内完成”，尚无syscall耗时剖析或唯一存储内部原因证明。未扩大300秒/10万软预算，也未更改计数实现。

Gate B02-2=FAIL，RESOURCE_GATE_PASS=NOT_OBTAINED。C00/C01局部成功不足以开放模型门。真实批次终止约300.17秒，1800秒全局窗口未耗尽；剩余额度/时间没有恢复资格。
