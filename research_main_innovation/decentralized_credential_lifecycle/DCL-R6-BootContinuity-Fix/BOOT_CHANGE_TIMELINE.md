# batch06 三次boot观测与完整事件时间线

Material Passport：BootContinuity-static-1/r4；host离线静态修复；2026-11-11；WSL查询/目标执行0。

batch06预检/准备由19次相互独立的`wsl.exe --distribution Ubuntu-24.04 --exec …`组成。原Host EXEC_NATIVE逐次Popen/wait，返回后Linux命令进程结束；Host脚本之间还存在间隙。原记录中没有一个Linux受信进程贯穿全部预检、准备和Launcher交接的身份见证。

|原始编号|事件|宿主UTC开始|宿主UTC完成|elapsed ms|Windows wsl PID|实际观测boot|exit|
|---|---|---|---|---|---|---|---|
|[1](<../DCL-R6-batch06/evidence/commands/01.result.json>)|静态文件/运行时摘要核对|2026-11-11T08:56:19.003568+00:00|2026-11-11T08:56:21.635673+00:00|2632.105|9916|未采集|0|
|[2](<../DCL-R6-batch06/evidence/commands/02.result.json>)|首次boot/基础环境|2026-11-11T08:56:21.649946+00:00|2026-11-11T08:56:21.904747+00:00|254.801|57160|3f63d905-84a9-47c0-b212-fdda02584774|0|
|[3](<../DCL-R6-batch06/evidence/commands/03.result.json>)|systemd Version|2026-11-11T08:56:21.932811+00:00|2026-11-11T08:56:22.195109+00:00|262.298|88132|未采集|0|
|[4](<../DCL-R6-batch06/evidence/commands/04.result.json>)|单位冲突检查|2026-11-11T08:56:22.214344+00:00|2026-11-11T08:56:22.525220+00:00|310.876|81888|未采集|0|
|[5](<../DCL-R6-batch06/evidence/commands/05.result.json>)|manager失败检查|2026-11-11T08:56:22.542517+00:00|2026-11-11T08:56:22.865283+00:00|322.766|117072|未采集|0|
|[6](<../DCL-R6-batch06/evidence/commands/06.result.json>)|准备1批根|2026-11-11T08:57:59.792578+00:00|2026-11-11T08:58:05.829004+00:00|6036.426|108144|未采集|0|
|[7](<../DCL-R6-batch06/evidence/commands/07.result.json>)|准备2 out|2026-11-11T08:58:05.844457+00:00|2026-11-11T08:58:06.102927+00:00|258.470|8912|未采集|0|
|[8](<../DCL-R6-batch06/evidence/commands/08.result.json>)|准备3 private|2026-11-11T08:58:06.122137+00:00|2026-11-11T08:58:06.351516+00:00|229.379|115264|未采集|0|
|[9](<../DCL-R6-batch06/evidence/commands/09.result.json>)|准备4 slice安装|2026-11-11T08:58:06.366638+00:00|2026-11-11T08:58:06.623119+00:00|256.481|72300|未采集|0|
|[10](<../DCL-R6-batch06/evidence/commands/10.result.json>)|准备5 unit verify|2026-11-11T08:58:06.638179+00:00|2026-11-11T08:58:06.916540+00:00|278.361|118520|未采集|0|
|[11](<../DCL-R6-batch06/evidence/commands/11.result.json>)|准备6 daemon-reload|2026-11-11T08:58:06.938008+00:00|2026-11-11T08:58:07.281302+00:00|343.294|90880|未采集|0|
|[12](<../DCL-R6-batch06/evidence/commands/12.result.json>)|授权原文安装|2026-11-11T08:58:07.295610+00:00|2026-11-11T08:58:07.553085+00:00|257.475|114500|未采集|0|
|[13](<../DCL-R6-batch06/evidence/commands/13.result.json>)|授权回执安装|2026-11-11T08:58:07.571433+00:00|2026-11-11T08:58:07.822186+00:00|250.753|96056|未采集|0|
|[14](<../DCL-R6-batch06/evidence/commands/14.result.json>)|父slice属性|2026-11-11T08:58:07.837293+00:00|2026-11-11T08:58:08.065387+00:00|228.094|96428|未采集|0|
|[15](<../DCL-R6-batch06/evidence/commands/15.result.json>)|最终boot/元数据→拒绝|2026-11-11T08:58:08.088657+00:00|2026-11-11T08:58:08.298670+00:00|210.013|113224|c92b8cbc-fada-48bd-8b61-eaaf134a06ee|0|
|[16](<../DCL-R6-batch06/evidence/commands/16.result.json>)|证据导出/事后boot|2026-11-11T09:01:42.278640+00:00|2026-11-11T09:01:49.157684+00:00|6879.044|97872|b69460ad-afd5-4185-871d-43277baacf85|0|
|[17](<../DCL-R6-batch06/evidence/commands/17.result.json>)|事后父组状态|2026-11-11T09:01:49.189572+00:00|2026-11-11T09:01:49.429957+00:00|240.385|117248|未采集|0|
|[18](<../DCL-R6-batch06/evidence/commands/18.result.json>)|事后单位列表|2026-11-11T09:01:49.453302+00:00|2026-11-11T09:01:49.680741+00:00|227.439|73624|未采集|0|
|[19](<../DCL-R6-batch06/evidence/commands/19.result.json>)|当前boot限定journal|2026-11-11T09:01:49.696331+00:00|2026-11-11T09:01:49.928581+00:00|232.250|115764|未采集|0|

表中时间全部源于Windows datetime UTC；elapsed为该时钟差，原脚本未使用单调计时。Linux reader PID/start_ticks均未记录；仅命令2明确输出euid0。Windows子PID具有宿主含义，不能代作Linux进程身份。每项精确完整argv含`-c`源及双流见链接原JSON，[机器时间线](evidence/BOOT_TIMELINE.json)保留全部Windows argv。

只在命令2、15、16采集boot：`3f63d905-84a9-47c0-b212-fdda02584774`、`c92b8cbc-fada-48bd-8b61-eaaf134a06ee`、`b69460ad-afd5-4185-871d-43277baacf85`。命令1的1326摘要核对exit0，其boot未采集；命令6–14的具体boot同样未知。当前证据不能把六条准备逐一分配给某个boot。两次变化只可界定在相邻boot读取区间之间。

命令1开始至15完成跨度109.295102秒，命令5完成至6开始间隙96.927295秒。命令14观测父slice inactive/dead、4tasks/4GiB；最终15其余谓词true、same_boot=false，PREFLIGHT_FAILED成立。命令16–19为失败后导出/核查；最终查询进程为空、cgroup不存在。没有Launcher/T0/预算账/目标测试，本轮也没有恢复或重试。

原Windows宿主驱动路径：[EXEC_NATIVE.py](<../DCL-R6-batch06/evidence/EXEC_NATIVE.py>)、[PREPARE_AND_RUN.py](<../DCL-R6-batch06/evidence/PREPARE_AND_RUN.py>)。原包[BATCH06_EVIDENCE.zip](<../DCL-R6-batch06/BATCH06_EVIDENCE.zip>)与157个ZIP条目逐流复核，历史字节保持。
