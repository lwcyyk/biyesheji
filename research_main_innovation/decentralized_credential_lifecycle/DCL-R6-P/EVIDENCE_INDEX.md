# P证据导航与审查强度

2026-11-10。Material Passport：本地证据索引。平台读取、行政摘要验证和资源/模型执行的分类分别保留。

|记录|范围|
|---|---|
|[授权原文](evidence/P_AUTHORIZATION_TEXT.txt)|本次用户P任务副本|
|[授权收据](evidence/P_AUTHORIZATION_RECEIPT.json)|12命令/唯一发行版/原则合同/排除事项|
|[冻结argv](evidence/P_COMMAND_PLAN.json)|与Envelope逐条比较相符|
|[总执行记录](evidence/P_COMMAND_RESULTS.json)|12条顺序、UTC/单调耗时、exit/双流/解释/权限|
|[首命令](evidence/commands/01.result.json)|启动并取得实际kernel，含编码修订说明|
|[PID1](evidence/commands/03.result.json)|实际readlink|
|[systemd](evidence/commands/04.result.json)|工具255及构建特性|
|[挂载](evidence/commands/07.result.json)|根ext4/cgroup2/9p/hugetlbfs|
|[控制器](evidence/commands/09.result.json)|根controllers|
|[启用项](evidence/commands/10.result.json)|根subtree_control|
|[Python缺失](evidence/commands/12.result.json)|exit2、混合编码更正、两条ENOENT|
|[入场锁](evidence/P_BASELINE_LOCK.json)|Envelope全21文件、原23项manifest入场核对、4导航快照|
|[历史复核](evidence/P_HISTORY_INTEGRITY_CHECK.json)|batch01/ZIP/v3/Envelope及历史锁链保持|
|[行政交付核对](evidence/P_DELIVERY_CHECK.json)|必需文件、argv/顺序、raw hash、链接/JSON及范围|
|[输出锁](evidence/P_OUTPUT_MANIFEST.json)|P文件及4当前根导航；排除自身和交付核对避免循环|
|[来源索引](SOURCE_INDEX.json)|实际证据/官方语义来源复用及未决边界|

所有NN.stdout.txt/NN.stderr.txt均按进程重定向流保存原字节。metadata中的文本按UTF-8、UTF-16LE或混合分段解码；原始数据未覆写。01和12的初次错误编码视图以initial-decode.json保留；修订只发生在本地解释层，没有重复执行命令。原始boot_id、身份及设备/系统路径留在本地，报告省略不必要唯一标识。

Envelope的旧根导航manifest条目从P/evidence/navigation_before复核；更早Repair/R6-B继续沿用各自原快照。所有旧manifest保持原字节。P的ADMIN_CHECK无法替代资源动态校准、MODEL_CHECK、PASS_BOUNDED或独立外部审查。

L阶段建议命令只在P_NEXT_STAGE_REQUIREMENTS文本出现，未列入本次执行记录。当前无batch02目录、Linux活账目录创建、单位配置/写cgroup、安装、Python执行、探针、模型或发行版停止动作。
