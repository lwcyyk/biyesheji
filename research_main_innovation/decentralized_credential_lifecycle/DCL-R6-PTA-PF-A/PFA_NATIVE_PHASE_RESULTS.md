# 原生阶段转换结果

Material Passport：DCL-R6-PTA-PF-A；batch12-r3；PTA-PhaseFinalizer-static-1/r3；NORMAL_START；2026-11-12（Asia/Shanghai）；冻结入口1次，源码修改/测试重跑0。

**PF-A1=PASS_DYNAMIC（本批真实正常路径）。** 初始化成功越过历史失败位置，ARMED合法进入RUNNING，实际C00八项检查全部MATCH。本批实际进程stderr/journal未观察到PT_RUNTIME_PHASE_DRIFT。

|事件|BOOTTIME秒|T0偏移秒|
|---|---:|---:|
|PRE_WINDOW|88.095196965|-0.095098816|
|PREFLIGHT_VALIDATING|88.112471464|-0.077824317|
|PREFLIGHT_QUALIFIED|88.166150713|-0.024145068|
|RUNTIME_INITIALIZING|88.177949748|-0.012346033|
|T0|88.190295781|0.000000000|
|RUNTIME_READY|88.215273509|0.024977728|
|RUNTIME_ARMED|88.414624368|0.224328587|
|RUNNING|88.431871955|0.241576174|
|C00 PASS|88.907022413|0.716726632|

私有phase链完整0–6、previous_sha256逐项匹配；最终公开/私有均RUNNING、seq6，phase_record_sha256与初始化ID匹配。真实T0=88.190295781、deadline=1888.190295781、stop_at=1828.190295781，counter只建立一次并单调到1907。

实际发布者由当前scheduler身份守卫与持久状态838/start8801绑定；Root读取者包括停止器849及Root工作流程。phase事件没有独立actor字段，主体映射来自相同批次的角色记录与冻结调用链，精确逐次读写主体时间仍按观测边界保留。

本批结果只属于batch12。旧batch11的精确q/private读取值继续UNKNOWN；新批次正常成功不倒填旧字段。

[原生phase/lock证据](evidence/LOCK_AND_PHASE_EVIDENCE.json) · [C00八项原始比较](evidence/C00_READINESS_SUMMARY.json) · [完整实际结果](evidence/ACTUAL_RESULTS.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原安全与原创性裁决保持。
