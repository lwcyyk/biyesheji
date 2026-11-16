# PT64与九项变异实际结果

Material Passport：DCL-R6-PTA-PF-A；batch12-r3；PTA-PhaseFinalizer-static-1/r3；NORMAL_START；2026-11-12（Asia/Shanghai）；冻结入口1次，源码修改/测试重跑0。

**PF-A3=PASS_DYNAMIC，范围为PT-SIMULATION/1。** 冻结64项全部完成并由原生独立oracle接受：55 PASS＋9 MUTATION_DETECTED，缺件/未触发/漏检0。

该suite在真实C00后执行，预算before1、after1090，消费1089：entry1＋64×(driver预付16＋Root审查1)。64份pt_case_000–063原始文件、冻结input SHA、trace.actual_input、绑定、oracle结果及raw_sha逐项对应，执行后仅做文件/结构核验，checker重放0。

9项变异force_runtime_pre、delete_pre_validation、missing_checkpoint_pass、no_auto_stop、missing_deadline、unknown_as_success、admin_as_native、new_budget_after_fail、reactivate_closed均实际命中预期违规，且没有越过冻结allowed_violations。计数包含这些变异，未追加免费窗口。

这些结果覆盖冻结预窗/初始化/检查点/自动停止/native-admin/UNKNOWN/终态的模型事实。Subject中的T0/R等是明确标记的合成值，不写入正式账；真实120秒到期、Root崩溃及真实无T0终止并未在本次正式实例额外注入。

每项实际输入/状态/违规、原始路径、SHA、前后访问、Root审查预付与时间字段见[112项明细](evidence/TEST_CASE_RESULTS.json)。原件只有sample时点，完整每case/每oracle耗时UNKNOWN；所列prepare→raw sample间隔包含预算IO并排除后续持久化/重审，不能当作完整case耗时。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原安全与原创性裁决保持。
