# batch06 最终预检失败裁决

Material Passport：DCL-R6-batch06；RootIPC-static-1/r4；真实预检/准备记录；动态测试0；2026-11-11。

**PREFLIGHT_FAILED；RESOURCE_GATE_FAILED_PREFLIGHT；动态Launcher/测试/模型启动均为0。** 本次专项许可已绑定RootIPC-static-1/r4并完成六条冻结准备及授权安装；最终启动前boot连续性检查失败，按首次失败规则停止并封存。

|用户要求的最终问题|真实结果|
|---|---|
|1 预检|基础通过；最终PREFLIGHT_FAILED（boot变化）|
|2 UID999读取共享intent|NOT_EXERCISED；共享intent尚未创建|
|3 Root私有控制|目录0:0/0700/无ACL符合准备合同；实际越权测试UNRUN|
|4 RootIPC56执行/通过|0/0；全部UNRUN_PREFLIGHT_FAILED|
|5 8变异检出|实际0；全部未执行|
|6 STOP_REQUEST→Root退出延迟|N/A；两端运行事件均未产生|
|7 持久ACK/receiver确认|均未产生|
|8 Launcher waitpid|N/A；Launcher未调用/未fork|
|9 C09成功|NOT_EXERCISED|
|10 C00–C12|13项全部UNRUN_PREFLIGHT_FAILED|
|11 S34/门17|均执行0|
|12 RESOURCE_GATE_PASS|NOT_OBTAINED|
|13 F1/F4启动|均0，UNRUN_RESOURCE_GATE|
|14 PASS_BOUNDED|授予0|
|15 预算/时间/峰值|R/T0/deadline=null；测试访问0；实际运行峰值N/A|
|16 新缺口|预检/准备证据链跨boot；具体WSL触发源待确认；目标协议代码未执行|

基础命令2 boot=3f63d905-84a9-47c0-b212-fdda02584774；最终命令15 boot=c92b8cbc-fada-48bd-8b61-eaaf134a06ee；事后命令16 boot=b69460ad-afd5-4185-871d-43277baacf85。禁止把这些查询拼接为同一运行窗口。源码、输入、授权、目录与原slice属性均未出现已观测的hash/metadata不符；最终唯一失败项是same_boot。宿主UTC预检记录跨度109.295102秒，属于T0之前的行政过程。

当前Linux目录保留批根/inputs/out/reports/root_private和两份授权文件；out/private为空；counter、journal、batch_state、STOP_REQUEST、CLOSED、ACK、waitpid证据及native EVIDENCE.zip均未生成。控制进程为空、父cgroup不存在、slice inactive/dead，无需停止未启动的服务。

19条native调用均exit0，属于只读预检/六条冻结准备/授权安装/事后核对与导出；行政脚本的PREFLIGHT_FAILED与命令exit0分别保留。代码/锁修改0、现场权限修复0、重试0、恢复0、新窗口0、batch07创建0。已保存44个实际Linux冻结文件、2个native准备文件及全部命令原始双流/元数据。

790项历史研究基线、当前ri01与旧静态工作区/原导出、误副本47逐字节核对；RootIPC r4和batch05原包逐流核对无差异。历史R37293/R37021/R32191、batch05 RESOURCE_GATE_FAILED、先前blocked by policy和所有首次失败保持。

后续先处理[预检连续性缺口](BATCH06_COUNTEREXAMPLES.md)及可审阅编排，不自动重启本批。D1-PBFT-SEAL/1.1原条件、强G覆盖、STRICT_SEPARATION_INSTANCES=0、IMPLEMENTATION_GATE=CLOSED保持。当前没有资源资格或协议原创性升级。

[授权与锁](BATCH06_AUTHORIZATION_AND_LOCK.md)、[权限实际范围](BATCH06_ROOTIPC_PERMISSION_RESULTS.md)、[停止记录](BATCH06_ROOT_STOP_RESULTS.md)、[全部实际结果](evidence/ACTUAL_RESULTS.json)、[证据索引](EVIDENCE_INDEX.md)、[交付核验](evidence/DELIVERY_CHECK.json)。
