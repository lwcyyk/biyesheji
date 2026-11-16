# A2授权、来源前提与执行锁

Material Passport：DCL-R6-TR-A2；batch14-r1；RuntimeAdapt-static-1/r1；2026-11-13（Asia/Shanghai）；冻结入口1次、源码修改/测试重跑0。

**已在授权声明的TCB前提下完成正常最小A2：新运行时预检、WORK/C00、PT64/PF48/TR40/RA32、CLOSED/只读/活动拒绝、native及自动行政封存。** 来源条件独立保留。

|绑定|实际结果|
|---|---|
|版本|RuntimeAdapt-static-1/r1，64项/44程序，Linux部署62项|
|manifest SHA|738eb2982953971f94019b913f6b302808f9b7a8d29e784038e8e6babb50de89|
|execution_lock SHA|691f2503f2db6906552241692db0b27ec6a982a7c738839d99f3cd93f3729da6|
|源/实例/slice|/var/lib/dcl-r6/ra01；/var/lib/dcl-r6/batch14；dclr6batch14.slice|
|control|DCL-R6-RuntimeAdapt-Fix/authorization/batch14-r1，新建真实原文/回执|
|boot|27e8416d-3ba4-46fd-8b42-75e983f2dcfa，实际预检/运行/post一致|
|身份|Root Owner449/start3530；当前scheduler/stopper及Payload身份见原始实际结果|
|隔离预检|新运行目录/单位/组尚无，Root/Payload残留0；初始failed仅mnt-e.mount|
|历史保护|执行前8605份文件锁，4根导航另存原字节，误路径47只读/hash|

用户第三节允许在冻结声明的Root/dpkg/keyring及无并发特权运行时更新条件下验证；回执据此将RuntimeAdapt_provenance_assumptions位设true。缺独立8.12 .deb payload事实保持，不宣称来源完全独立。scope仅PT_STARTUP_DIAGNOSTIC_ONLY、NORMAL_START，Full/MR/预窗注入false；C09兼容位只是冻结schema字段。

完整静态计费：C00=1、PT1089、PF817、TR681、RA545，完成3133、阶段A硬4417、完整硬68498。184合成job含33变异。实际R3133，已按同一账完成，无预算重置或第二窗口。

[源码与范围](evidence/SOURCE_AND_SCOPE_ADMISSION.json) · [原文](evidence/TASK_REQUEST.txt) · [回执锁](evidence/AUTHORIZATION_RECEIPT_LOCK.json) · [计费准入](evidence/RESOURCE_ADMISSION_PROOF.json) · [源后核](evidence/SOURCE_AFTER_CHECK.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2安全与原创性裁决保持。
