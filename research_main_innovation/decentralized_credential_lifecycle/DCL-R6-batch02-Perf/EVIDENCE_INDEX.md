# Perf证据与重算索引

|证据|来源/强度|
|---|---|
|[TASK_REQUEST](evidence/TASK_REQUEST.txt)|本轮只读与设计授权|
|[BASELINE_LOCK](evidence/BASELINE_LOCK.json)|B02全目录/host工件入场核对、4根导航快照|
|[ZIP_VERIFICATION](evidence/ZIP_VERIFICATION.json)|外层161/原生31项逐流及SHA直接重核|
|[EXECUTION_TIMELINE](evidence/EXECUTION_TIMELINE.json)|28项事件/身份/clock/输入输出/未知标记|
|[ALL_LOGGED_STAMPS](evidence/ALL_LOGGED_STAMPS.csv)|原JSON嵌套时标定位；重复对象保留来源|
|[TIMELINE_INTERVALS](evidence/TIMELINE_INTERVALS.csv)|不重叠里程碑跨度，便于复算|
|[RESERVATION_STAMPS](evidence/RESERVATION_STAMPS.csv)|32191 PREP起点/序号与来源推断|
|[周期样本](evidence/PREPARED_CYCLE_INTERVALS.csv)|相邻PREP跨度，非单次fsync延迟|
|[JOURNAL_STATS](evidence/JOURNAL_STATS.json)|连续配对、同戳、均值/分位数/速率|
|[独立参考检查](evidence/INDEPENDENT_REFERENCE_CHECK.json)|第二套regex/decimal解析与UTC/BOOTTIME跨度交叉核对|
|[序号分组](evidence/CYCLE_SEQUENCE_BINS.csv)|4096周期分组，非新基准|
|[最长周期](evidence/LONGEST_CYCLES.json)|20项最长混合跨度|
|[账来源](evidence/BUDGET_SOURCE_BREAKDOWN.json)|入口3＋预付32188，消费/return边界|
|[修复计数模型](evidence/REPAIR_COUNT_MODEL.json)|事务/同步机会与软窗备选，非墙钟实测|
|[副本登记](evidence/DUPLICATE_REGISTER.json)|47文件只读双hash一致，操作0|
|[历史核对](evidence/HISTORY_INTEGRITY_CHECK.json)|B02/LC/旧批次/版本与hash链|
|[交付核对](evidence/DELIVERY_CHECK.json)|JSON/链接/数据一致性/未建B03/无代码|
|[输出锁](evidence/OUTPUT_MANIFEST.json)|本轮派生文件和根导航，排除自身/交付核对|

所有计算从正确host batch02/native_snapshot与FROZEN_LC读取，误路径仅登记。原包、journal、计数、源码和审批拒绝原件不改。派生脚本只在行政工具内用于读取/计算，没有保存可执行程序或执行性能负载。

初始SOURCE_INDEX先于归因分析建立；最终索引补充派生物。旧B02输出4导航条目由本轮navigation_before验证，更早阶段沿用各自原快照。ADMIN_CHECK不授资源、模型、原创性或独立外审通过。
