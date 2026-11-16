# TR40与八项变异结果

Material Passport：DCL-R6-TR-A；batch13-r1；TerminalRead-static-1/r1；2026-11-13（Asia/Shanghai）；冻结入口1次、退出125、源码修改/测试重跑0。

**TR-A4=UNRUN：TR40执行0/40，8项变异触发0/8、检出0/8。** 原生窗口未创建，独立oracle调用0。

grant_terminal_work、rebuild_budget、skip_identity、default_deadline、ignore_journal、upgrade_unknown、false_seal、write_original全部NOT_EXERCISED；不存在已触发漏检的本轮结果。所有safe项记UNRUN_PREFLIGHT_FAILED。

冻结输入、safe控制配对、source/oracle SHA均匹配。输入中预期结果未当作实际执行结果；未在窗口外运行subject、reference或checker补数据。

[152项逐项未执行登记](evidence/UNRUN_CASE_REGISTER.json) · [源码锁](evidence/SOURCE_AND_SCOPE_ADMISSION.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2安全与原创性结论保持。
