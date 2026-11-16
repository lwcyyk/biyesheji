# PF48与八项变异实际结果

Material Passport：DCL-R6-PTA-PF-A；batch12-r3；PTA-PhaseFinalizer-static-1/r3；NORMAL_START；2026-11-12（Asia/Shanghai）；冻结入口1次，源码修改/测试重跑0。

**PF-A4=PASS_DYNAMIC，范围为PF-SIMULATION/1。** 冻结48项全部完成并由独立原生oracle接受：40 PASS＋8 MUTATION_DETECTED，NOT_EXERCISED/MUTATION_NOT_DETECTED均0。

预算before1090、after1907，消费817：entry1＋48×(driver16＋Root审查1)。48份pf_case_000–047原件与合同、资格文件和checker SHA对应。oracle只导入stdlib，按真实原始trace独立分类违规，再比对预期及允许伴随集合；执行后没有重跑该oracle。

|变异|实际检出目标|
|---|---|
|allow_illegal_phase|ILLEGAL_PHASE_ACCEPTED|
|skip_work|PREMATURE_WORK|
|stale_snapshot|STALE_SNAPSHOT_ACCEPTED|
|ignore_version|VERSION_MISMATCH_ACCEPTED|
|no_auto_stop|NO_AUTO_STOP|
|swallow_import_error|IMPORT_ERROR_SWALLOWED|
|overwrite_native|NATIVE_RESULT_OVERWRITTEN|
|reactivate_closed|REACTIVATION|

前四项允许放行造成的NO_AUTO_STOP伴随，原结果违规集合保持。锁竞争/延迟、身份、导入/权限/未知和关闭等帧是受冻结模型输入驱动的真实策略调用，无法替代真实OS注入；新模块的真实成功加载另见[行政收尾结果](PFA_ADMIN_FINALIZER_RESULTS.md)。

[逐项实际结果/原件/预算/时间范围](evidence/TEST_CASE_RESULTS.json) · [源与checker保持](evidence/SOURCE_AFTER_CHECK.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原安全与原创性裁决保持。
