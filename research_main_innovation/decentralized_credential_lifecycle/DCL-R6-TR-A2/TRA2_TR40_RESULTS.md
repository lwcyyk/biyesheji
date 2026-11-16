# TR40与八项变异原生结果

Material Passport：DCL-R6-TR-A2；batch14-r1；RuntimeAdapt-static-1/r1；2026-11-13（Asia/Shanghai）；冻结入口1次、源码修改/测试重跑0。

**TR-D3=PASS_DYNAMIC，范围TR-SIMULATION/1。** 40/40接受：32 PASS＋8 MUTATION_DETECTED；未触发/漏检0。

预算before1907、after2588，消费681＝entry1＋40×(driver16＋Root审查1)。实际40份tr_case、input SHA、raw trace、binding、native oracle结果和raw_sha逐项对应，退出后只核验字节/结构，没有重放checker。

grant_terminal_work、rebuild_budget、skip_identity、default_deadline、ignore_journal、upgrade_unknown、false_seal、write_original均实际命中各冻结目标违规。主实例预算和状态没有为合成故障被修改。

TR40提供策略和观察模型覆盖，真实CLOSED后的读取另有独立terminal_seal_review、native输入摘要和活动拒绝回执。每case提供driver访问区间、审查预付、raw sample及charged-prefix时间，完整独立case/oracle耗时未打点，保持UNKNOWN。

[184项逐项输入/结果/路径/SHA/预算/时间范围](evidence/TEST_CASE_RESULTS.json) · [真实终态读取](TRA2_TERMINAL_READ_RESULTS.md)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2安全与原创性裁决保持。
