# batch02精确时序复核

2026-11-10。Material Passport：OFFLINE_EVIDENCE_ANALYSIS；本轮新增Linux命令、代码、探针、校准和模型均0。来源索引先于计算建立。原始ZIP及文件直接核hash通过，见[ZIP_VERIFICATION](evidence/ZIP_VERIFICATION.json)。

**300秒从整批校准T0累计；其中至少298.626607199秒落在C02串行预付循环的内部观测区间。** C00/C01到结果写出仅占T0后1.109256092秒。C02没有独占300秒，也没有开始实际内存分配。

## 事件表

时钟为本次相同boot_id的CLOCK_BOOTTIME秒。完整28条含原始路径、角色/身份、时钟和未知边界见[EXECUTION_TIMELINE.json](evidence/EXECUTION_TIMELINE.json)；[全部日志时标CSV](evidence/ALL_LOGGED_STAMPS.csv)保留嵌套位置。

|事件|真实时标/边界|身份、来源与含义|
|---|---|---|
|外层Launcher提交|Windows UTC原始start/end另存|commands/22；WSL进程总300.701767秒，无法拆出纯Linux启动|
|T0|399.708633895|Root Launcher1074/start_ticks39962；batch_state|
|外部停止者启动/武装|UNKNOWN_INTERVAL，T0后、首payload之前|STOP_ARMED及1078/start_ticks39977；没有独立arm完成时标|
|systemd激活/exec/Python首指令|UNKNOWN_INTERVAL|ticket记录activating及MainPID/start_ticks；频率/各边界时标缺失，不虚填纳秒|
|C00首原生采样|400.236486130|Controller1083；startup.process.query_before|
|C00 W握手已发生|≤400.301579386|startup.after_watchdog_group；W身份在原件，首指令时标未知|
|C00 reserve1/业务probe记录|400.326142307 /400.335060234|前者为PREP起点，后者在visit返回之后|
|C00协调器结果|400.435074580|局部PASS，已观察inactive；真实退出时刻在此前|
|C01首采样/W握手上界|400.563553130 /≤400.621873415|Controller1097/W1100，startup|
|C01 reserve2/probe记录|400.647849473 /400.656647162|正常运行，记录开始点并非probe结束|
|C01协调器结果|400.817889987|局部PASS|
|C02首采样/W握手上界|400.979841037 /≤401.046893093|Controller1112；startup|
|C02入口reserve3|401.072781894|run_case开头的单次visit|
|首个子任务预付reserve4|401.081872523|prepaid_child循环第一项|
|最后reserve32191|699.708479722|PREPARED时标；COMMITTED复用同一值|
|子探针预期启动|UNREACHED|源码规定全量预付后才Popen；缺口和子文件缺失共同佐证|
|校准软截止|699.708633895=T0+300|ticket_C02.case_deadline与源码min一致|
|Watchdog停止记录|699.816997437|expired=true；stamp在日志持久写入和signal之前|
|SIGKILL发送/退出|UNKNOWN_INTERVAL，699.816997437至699.875076343|冻结调用顺序及Resultsignal/ExecMainStatus9；无发送系统调用时标|
|C02协调器结果|699.875076343|原FAIL|
|关闭标记|699.878483695|T0+300.169849800；CLOSED为权威停止|
|Root已确认空组|699.886158922|stop_result1074；此前699.878435632快照已示populated0|
|独立停止者清理确认|700.003546535|stop_result1078，empty=true|
|封存manifest取样|700.079412747|取样在manifest写入/ZIP压缩之前，非ZIP完成时刻|
|ZIP完成/Root退出|UNKNOWN_INTERVAL|原ZIP已完整；外层UTC结束是后续捕获上界，跨钟不强行相减|

## 不重叠里程碑耗时

|区间|秒|可解释范围|
|---|---:|---|
|T0→C00结果|0.726440685|初始化、外部停止/父层/运行时复核、C00启动/执行/退出；内部拆分UNKNOWN_INTERVAL|
|C00结果→C01结果|0.382815407|C01调度/运行/退出/轮询混合|
|C01结果→C02首采样|0.161951050|C02提交/启动等混合|
|C02首采样→首预付PREP4|0.102031486|W/准入、入口visit、检查/准备混合|
|PREP4→PREP32191|298.626607199|32187个连续混合预留周期，99.5422%软窗口|
|末PREP→软截止|0.000154173|最后事务仍可能继续，不能据此说最后fsync只耗154µs|
|软截止→W停止记录|0.108363542|检查/调度延迟混合，非精确信号延迟|
|W记录→C02结果|0.058078906|日志同步、signal/退出、manager及轮询混合|
|C02结果→CLOSED|0.003407352|关闭前采样/标记|
|CLOSED→Root空组确认|0.007675227|停止命令与确认|
|Root确认→独立清理确认|0.117387613|停止者检查/处理混合|
|独立确认→manifest取样|0.075866212|等待/扫描/hash准备，后续ZIP时间未知|

C02首采样到结果为298.895235306秒；以上均为观测点跨度，不声称是纯函数或纯CPU时间。没有提前截止证据，截止计算与T0+300相符。Python启动、systemd各阶段、锁/序列化/单次fsync、轮询和ZIP完成缺精确分解，统一保留UNKNOWN_INTERVAL。未把未知时间按比例分摊。

独立regex/decimal重算得到预付BOOTTIME跨度298.626607199秒，UTC跨度298.626607542秒，两锚点差343ns；这支持本区间没有实质钟漂移，仍无法补出未记录的阶段时刻。原始Windows UTC与Linux单调钟分别保留。
