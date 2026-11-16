# batch06 停止响应与生命周期证据

Material Passport：DCL-R6-batch06；RootIPC-static-1/r4；真实预检/准备记录；动态测试0；2026-11-11。

RootIPC停止逻辑的动态执行范围为0，实际停止延迟为N/A。首次失败由行政预检发现，目标Launcher/Root协调器、receiver及额外探针都尚未启动。

|测量要求|本批实际|
|---|---|
|STOP_REQUEST发布|未产生|
|CLOSED发布|未产生；运行窗口尚未建立|
|Root首次观察停止|N/A；Root协调器未启动|
|ready等待退出|N/A；未进入|
|RPC等待取消|N/A；未进入|
|父waitpid结束|N/A；未fork Launcher|
|Root清理开始/退出|N/A；没有本批目标Root角色|
|受控进程退出确认|事后UID999与Root角色扫描为空；父cgroup不存在|
|STOP_REQUEST→Root退出延迟|N/A，缺少两端运行事件；不填0秒|
|停止后继续发放测试|0；最终预检失败后仅核查/导出|

三次boot分别为：基础预检3f63d905-84a9-47c0-b212-fdda02584774；最终启动前c92b8cbc-fada-48bd-8b61-eaaf134a06ee；事后导出b69460ad-afd5-4185-871d-43277baacf85。这些属于各行政查询时点，没有统一运行T0，禁止跨boot相减构造BOOTTIME延迟。宿主UTC从命令1开始至命令15完成跨度109.295102秒，仅是预检行政记录跨度。

命令17显示父slice inactive/dead、ControlGroup空，MemoryCurrent/TasksCurrent为[not set]；命令18批单位列表空，命令19当前boot精确17-unit journal输出空。没有启动服务后再杀进程的操作，也没有人为制造运行CLOSED文件。本批行政状态为PREFLIGHT_STOPPED；已准备目录/授权及原slice文件保留。

50ms轮询、30秒协作grace、5秒回收等冻结参数保留静态地位，当前实际响应和及时清理结论尚待验证。boot切换的具体WSL生命周期触发源为UNRESOLVED，见[反例与后续审查](BATCH06_COUNTEREXAMPLES.md)。
