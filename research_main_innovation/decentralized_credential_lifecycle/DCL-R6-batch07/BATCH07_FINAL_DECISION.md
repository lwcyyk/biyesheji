# batch07最终裁决

Material Passport：DCL-R6-batch07；BootContinuity-static-1/r4；真实启动后首次失败；2026-11-11；复跑0。

**RESOURCE_GATE_FAILED；首个关键失败为C00启动复核BC_SERVICE_IDENTITY_OR_LIMITS。** 本批真实执行了单会话预检、sealed能力/一次认领和same-PID exec；这些前缀成功证据保留，服务内完整资格失败，后续C/40/56/34/S/门和模型停止。

|用户要求|实际结果|
|---|---|
|1 单会话预检|实际执行，PREFLIGHT_QUALIFIED|
|2 同进程exec|实际成功到Guard入口；PID828/start7252两侧相同|
|3 boot贯穿|预检/Root入口/子scheduler均一致；完整服务证书未通过|
|4 封印凭据|实际生成，seals15及SHA见摘要|
|5 一次认领|实际消费一次；重复拒绝专项测试未运行|
|6 服务内复核|C00失败，BC_SERVICE_IDENTITY_OR_LIMITS|
|7 BC40|尝试/完成0|
|8 10变异|实际检出0，均未运行|
|9 RootIPC56|尝试0/检出0|
|10 C09H/真实C09|34未运行；真实交接NOT_EXERCISED|
|11 C00–C12|C00启动门失败/探针0；C01–C12未运行|
|12 S34/门17|均0|
|13 RESOURCE_GATE_PASS|NOT_OBTAINED|
|14 F1/F4|均UNRUN_RESOURCE_GATE，模型搜索0|
|15 PASS_BOUNDED|授予0|
|16 资源|R0/1000000，T0已建，0.309秒关闭，0.327秒组空；charged peak782336B|
|17 首次失败/下一步|8项复核聚合拒绝；补exec-ready屏障与失败快照，精确字段仍待证|

运行boot=060a08fc-fceb-48ff-a264-50c34312f97a，Root父828/start7252，scheduler886/start7372，外部stop890/start7379。T0=73.768774900、deadline=1873.768774900、stop_at=1813.768774900，原窗口只建1次。最终R=0、COMMITTED初始intent，journal尚无事务。CLOSED在T0+0.309347559，首次组空+0.327163166，普通父waitpid raw32000/exit125；原生自动封存22条目通过字节核对。

当前观测的活动前缀没有batch06式跨boot，具体WSL历史触发源仍非本批诊断范围。事后不同boot仅用于文件/清理观察；当前service默认值不回写运行结果。精确失配字段没有原始采样，源码就绪屏障缺失、Starting-only journal和小charge峰值支持启动临态误拒绝假设，结论保持其证据边界。

主机冻结32项/部署31项与所有版本hash一致，21份程序身份核验完成；native3.12实际语法路径通过20源码。Root/全局资源源代码未改，现场权限修复0、case重跑0、resume0、主动WSL shutdown0、batch08创建0。核查确认专用进程与父组为空；全部23个native普通文件、32最终文件、34条BC事件、15条内部命令双流、7条run-boot journal及私有凭据证据已封存。

1920项R6历史研究、旧工作区/旧原件、47误副本与原包hash保持，旧batch06 PREFLIGHT_FAILED、batch05 R37293及其他历史失败不改。原票据秘密内容只保留private原件，普通报告/日志仅用摘要与验证状态。

D1-PBFT-SEAL/1.1原条件、强G覆盖、STRICT_SEPARATION_INSTANCES=0、IMPLEMENTATION_GATE=CLOSED保持。机器前缀观察与完整资源资格、有限模型性质及原创性分别裁决。

[启动前缀](BATCH07_BOOT_CONTINUITY_RESULTS.md)、[资源核算](BATCH07_RESOURCE_ACCOUNTING.md)、[首次失败](BATCH07_COUNTEREXAMPLES.md)、[证据索引](EVIDENCE_INDEX.md)、[交付核验](evidence/DELIVERY_CHECK.json)。
