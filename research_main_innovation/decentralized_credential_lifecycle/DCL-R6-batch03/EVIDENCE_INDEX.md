# batch03证据索引
Material Passport：PRELAUNCH_BLOCKED；原始只读输出、冻结来源、静态能力审查与未执行结果分别记录。

|工件|内容|
|---|---|
|[TASK_REQUEST](evidence/TASK_REQUEST.txt)、[AUTHORIZATION_RECEIPT](evidence/AUTHORIZATION_RECEIPT.json)|用户本次明确条件授权原文及研究收据；执行receipt未生成|
|[BASELINE_LOCK](evidence/BASELINE_LOCK.json)、[navigation_before](evidence/navigation_before/)|70项BudgetFix工件及四导航修订前快照|
|[HOST_FREEZE_CHECK](evidence/HOST_FREEZE_CHECK.json)|24项真实host静态文件匹配|
|[HASH_SCOPE](evidence/HASH_SCOPE.json)、[LINUX_EXPECTED](evidence/LINUX_EXPECTED.sha256)|1266唯一Linux路径预期摘要；1224树和31关键文件重叠去重|
|[COMMAND_PLAN](evidence/COMMAND_PLAN.json)、[commands](evidence/commands/)|11条只读查询完整argv、原始字节流、解释与退出|
|[CAPABILITY_MATRIX](evidence/CAPABILITY_MATRIX.json)|S1–S9逐项冻结能力与动态验收缺口|
|[guard_transition](evidence/guard_transition.txt)、[guard_formal_admission](evidence/guard_formal_admission.txt)|冻结源码的自动转换及formal admission原文摘录|
|[global_fault_rejection](evidence/global_fault_rejection.txt)、[C11_local_mirror](evidence/C11_local_mirror.txt)、[C02_C03_bound_loops](evidence/C02_C03_bound_loops.txt)|现有注入与访问次数覆盖|
|[ADMISSION_COUNTEREXAMPLE](evidence/ADMISSION_COUNTEREXAMPLE.json)|静态控制流见证，机器执行0；协议反例0个搜索样本|
|[FIRST_BLOCKING_EVENT](evidence/FIRST_BLOCKING_EVENT.json)|首次启动前阻断，用户§5/§6条件直接触发|
|[PREFLIGHT_RESULT](evidence/PREFLIGHT_RESULT.json)、[NO_RUNTIME_INITIALIZATION_CHECK](evidence/NO_RUNTIME_INITIALIZATION_CHECK.json)|当前环境核验及无T0/账/进程/运行根观察|
|[RESULTS](evidence/RESULTS.json)|逐case NOT_EXERCISED、F1/F4 UNRUN_RESOURCE_GATE及N/A资源指标|
|[HISTORICAL_PROTECTION_CHECK](evidence/HISTORICAL_PROTECTION_CHECK.json)|70项BF、110项B02研究、51项B02原件、47副本和24静态工作区未改变|
|[OUTPUT_MANIFEST](evidence/OUTPUT_MANIFEST.json)、[DELIVERY_CHECK](evidence/DELIVERY_CHECK.json)|最终报告/证据和四导航摘要、封存检查|
|[预检证据包](BATCH03_PREFLIGHT_EVIDENCE.zip)|报告与原始只读证据封存；包含manifest，自身和最终DELIVERY_CHECK排除以避免自引用|

来源见[SOURCE_INDEX](SOURCE_INDEX.json)。本轮没有实际预算账、校准/模型轨迹或native运行ZIP；对应指标保持NOT_EXERCISED/N/A，原始只读证据包按名称明确区分。
