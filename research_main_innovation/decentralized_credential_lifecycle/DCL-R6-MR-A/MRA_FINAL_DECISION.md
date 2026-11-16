# MR-A最终裁决

Material Passport：DCL-R6-MR-A；batch10-r5；ManagerRecovery-static-1/r5；2026-11-12；冻结入口1次、重跑/源码修复0。

**STARTUP_FAILED_PRE_T0：预检及same-PID exec通过，r5初始健康查询触发IPC_STATE_MISSING。真实C09恢复与64项回归尚未执行。**

|最终问题|真实回答|
|---|---|
|1 批次启动|新身份/单会话/一次认领/exec成立，正式预算运行窗未建立|
|2 预检/C00/C09|PREFLIGHT_PASS；C00/C09 UNRUN|
|3 failed集合|三次预检和事后仅mnt-e.mount，按冻结基线接受|
|4 UNREVIEWED处理|当前退出实例未产生；该修复验收UNRUN|
|5 C09后恢复|UNRUN_STARTUP_FAILED_PRE_T0|
|6 64实际数量|执行0/接受0|
|7 8变异|执行0/检出0，保持UNRUN|
|8 自动关闭|真实非预期启动错误触发STOP/CLOSED；主关闭结果UNKNOWN，预期78故障点未到达|
|9 兜底|父协调器自动stop_tree返回0；abort内stop/kill超时；独立停止服务未启动，人工清理0|
|10 清理UNKNOWN|r5内部结果UNKNOWN保持；事后受控角色全空分别记录|
|11 停止/组空|见同boot时间书签；无活动Payload，组空回收耗时不适用|
|12 预算/时间|R/T0/deadline null；host2.0633844秒；Root RSS未测，无Payload资源高水位|
|13 新缺陷|预窗query要求state、预窗关闭期限及seal依赖缺口|
|14 300秒证据|无新校准性能数据，TIME_FEASIBILITY_UNRESOLVED_NO_CALIBRATION|
|15 后续完整链|尚不具备；先最小静态修复初始化及预窗关闭/封存，再新独立A验收|

A1=UNRUN_STARTUP_FAILED_PRE_T0；A2=PARTIAL_AUTOMATIC_STOP / CLEANUP_UNKNOWN / NATIVE_SEAL_FAILED；A3执行0、变异检出0；A4未初始化预算；A5需新的静态补缺。现有自动STOP和父协调器停止实际发生，所有受控进程最终退出，CLOSED保留；本轮没有用第二条人工清理命令替代自动关闭。原生seal缺失，当前研究ZIP只作行政证据包。

冻结入口只执行1次、返回125，Root child直接waitpid raw32000/125；预声明C10后返回78注入尚未发生。Source46、输入和权限保持原样，现场修复/重跑/新窗口/自动下一批均0。历史6,068份文件、误路径47及旧CalDiag38,729账保持。

RESOURCE_GATE_PASS=NOT_OBTAINED，F1/F4=UNRUN_RESOURCE_GATE，PASS_BOUNDED=[]，D1/D2原条件、强G、STRICT_SEPARATION_INSTANCES=0及IMPLEMENTATION_GATE=CLOSED保持。资源资格、模型正确性和原创性继续分别裁决。

[首次反例及下一修复](MRA_COUNTEREXAMPLES.md) · [自动关闭结果](MRA_AUTOMATIC_CLOSURE_RESULTS.md) · [时间/资源](MRA_RUNTIME_AND_RESOURCE.md) · [证据索引](EVIDENCE_INDEX.md) · [交付核验](evidence/DELIVERY_CHECK.json)
