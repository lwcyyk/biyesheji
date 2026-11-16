# 授权与执行锁裁决

Material Passport：DCL-R6-FullChain-B；2026-11-13（Asia/Shanghai）；审查基线 RuntimeAdapt-static-1/r1 / ra01；仅主机静态审查；BLOCKED_STATIC_ADMISSION。


用户[本轮授权原文](evidence/TASK_REQUEST.txt)允许先审查完整链、再在条件满足时执行F1→F4，并要求关键静态冲突时停止。依据第三节的“若发现代码集成冲突或冻结版本不一致：BLOCKED_STATIC_ADMISSION”以及第一节必需执行清单条件，本轮执行静态拒绝。

|项目|实际结果|
|---|---|
|最新既有基线|RuntimeAdapt-static-1/r1；64/64文件匹配最终静态锁与SOURCE_FINAL_R1|
|程序|42 Linux程序＋2 host程序；44份通过3.12文法及主机内存compile；目标执行0|
|static_manifest SHA-256|`738eb2982953971f94019b913f6b302808f9b7a8d29e784038e8e6babb50de89`|
|execution_lock SHA-256|`691f2503f2db6906552241692db0b27ec6a982a7c738839d99f3cd93f3729da6`|
|条件完整scope|CALIBRATE_S1S9_THEN_F1_F4|
|新运行批次/部署目录/动态收据/新执行锁|均未签发；静态冲突已先于身份发布被确认|
|本轮研究身份|DCL-R6-FullChain-B，仅静态证据归档身份|

原锁绑定batch14/ra01及其历史授权路径；历史批次保持CLOSED。新批次原本需要机械重绑定全部路径/单位/授权摘要，静态拒绝发生在该操作之前。原锁的当前授权文字“STATIC_ONLY”、诊断说明及旧65618说明值均作为既有材料保留，具体可达调用由源码核对。

本轮动态用例0、WSL调用0、部署0、active entry0、目标模块导入0、源码修订0、重跑0。T0/deadline/R均为null；新增访问消耗0。历史结果单独引用。

[逐文件核验](evidence/SOURCE_LOCK_VERIFICATION.json) · [裁决机器记录](evidence/STATIC_DECISION.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
