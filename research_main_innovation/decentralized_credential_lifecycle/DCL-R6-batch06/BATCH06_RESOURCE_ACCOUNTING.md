# batch06 预算、时间与进程核算

Material Passport：DCL-R6-batch06；RootIPC-static-1/r4；真实预检/准备记录；动态测试0；2026-11-11。

本批持久预算账尚未初始化：R=null，T0/deadline/stop_at=null，journal/intent均不存在。实际测试与模型语义访问0、模型搜索0、退款0、重置0、恢复0。这里将“测试访问0”与“有效账R=0”分别记录，当前没有可供运行准入的账。

|资源项|合同|本批实际|
|---|---|---|
|全局访问|1000000|未初始化账；实际测试访问0|
|总墙钟/提前停止|1800秒/T0+1740|无T0；实际运行耗时N/A|
|校准窗口/软额|300秒/100000|未进入|
|C09H/IPC共同硬额|5000|未进入；静态完成上界2750|
|IPC56|505完成上界/512硬额|实际访问0|
|完整校准硬额|62034|未验证|
|payload AS/task|1GiB每进程/父4tasks|源/配置保持；实际payload0|
|Root顺序探针|最多1，AS1GiB|启动0|
|峰值内存/RSS/Root开销|按原payload/外部TCB边界解释|N/A，目标程序未运行|
|预检行政跨度|执行窗口之前|宿主UTC差109.295102秒；跨boot，不作为批次运行耗时|

六条准备命令与两条授权安装均执行，只有两份native常规文件。当前out/private为空；事后专用UID与Root角色进程为空，parent cgroup不存在。父slice inactive/dead，未启动服务。原生seal程序执行0，EVIDENCE.zip原生文件未生成，当前封存为行政导出/打包。

历史batch05 R37293、batch04 R37021、batch02 R32191从host原件再次读取，原失败与已关闭状态保持。[独立核算JSON](evidence/RESOURCE_ACCOUNTING.json)、[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)、[事后审计](evidence/POSTFAIL_AUDIT.json)。
