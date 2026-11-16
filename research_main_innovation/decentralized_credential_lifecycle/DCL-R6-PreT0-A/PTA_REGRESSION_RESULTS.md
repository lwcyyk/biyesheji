# PT64与九项变异实际结果

Material Passport：DCL-R6-PreT0-A；batch11；PreT0Recovery-static-1/r3；NORMAL_START；2026-11-12（Asia/Shanghai）；实际入口1次，重跑0，源码修复0。

**实际执行0/64、接受0/64；变异触发0/9、检出0/9。** C00开始前收到真实STOP，冻结首失败规则已阻断后续资格。

|冻结项目|计划数|实际执行/接受|
|---|---:|---|
|safe夹具|55|0/0，UNRUN_BEFORE_C00|
|mutant夹具|9|0/0，NOT_EXERCISED|
|全部PT64|64|0/0，UNRUN_BEFORE_C00|
|独立oracle|64项原始trace重审|调用0；没有pt_case原件或PT_QUALIFICATION|
|真实C00|1|UNRUN_BEFORE_DISPATCH；ticket/worker/ready原件均无|

九项变异force_runtime_pre、delete_pre_validation、missing_checkpoint_pass、no_auto_stop、missing_deadline、unknown_as_success、admin_as_native、new_budget_after_fail、reactivate_closed均记NOT_EXERCISED。MUTATION_NOT_DETECTED适用于已触发且漏检情形，本批未到达该条件。

现有PT64实现声明origin=PT-SIMULATION/1，在真实C00后同账执行。即使未来全部通过，它也只能证明对应合成状态/事件模型与独立oracle的有限一致性；真实Root/Launcher/fsync/期限/自动post仍需各自进程证据。本批既未运行这些合成夹具，也未运行PREWINDOW_ABORT。

没有将35份语法通过记成测试通过，没有将实际phase序列代入PT64重放，也未在预算窗口外调用独立oracle补结果。

[计划输入原件](evidence/FROZEN_SOURCE_REFERENCE/inputs/startup_contract.json) · [实际数量](evidence/ACTUAL_RESULTS.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原条件结论与强G覆盖裁决保持。
