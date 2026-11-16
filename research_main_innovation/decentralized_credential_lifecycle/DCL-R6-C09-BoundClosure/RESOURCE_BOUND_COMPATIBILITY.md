# 访问合同、数量前提与资源兼容性

Material Passport：DCL-R6-C09-BoundClosure；C09-BoundClosure/review-1；2026-11-15（Asia/Shanghai）；有限源码/历史原件/数学合同审查。


旧冻结校准访问硬界68498仍只属于旧程序/测试范围。本轮R/T0/deadline未建立，模型访问消耗0。

日志草案若另行批准并集成独立256预付，分开计的保守估计为68754，再加新负向/原件验证等收费项。若明确把该256放入原H/IPC/BC共同5000封套且保持精确合法收费上下文，则旧联合保守3269＋256=3525，存在1475余量；这需要版本化合同明确承认，当前没有自动吸收或重复计费。新完整实现尚未冻结，因此完整新访问硬界继续UNRESOLVED。

预付时点必须在C09 controller启动/ready marker及handoff.counter固定之前。固定后不得逐次修改全局R；新cursor只能消耗先付额度。预算核心、持久ACK、RootIPC权限及deadline语义当前保持原字节。

数量前提复核发现上一轮表漏列manager_recovery.event实际创建的mr_events.lock（历史native manifest已有该零字节原件）。对本轮明确的CALIBRATE_S1S9_THEN_F1_F4 scope，pt_expected_abort.json只由PT_STARTUP_DIAGNOSTIC_ONLY分支产生，因而不可达。修复固定族的一对一覆盖后，raw4450/native4451/admin原件4452仍可作为该完整scope的保守包络；旧报告不改写。该修正不把旧表视为无遗漏，也不向其他诊断scope无条件外推。

新配额sidecar/失败摘要/可能staging、新测试及未来MR use证据会带来ΔE和ΔV。其未实现生成规则不能直接套用4450，后续应按同一源级族方法重算。当前旧256/257守卫保持，未建立新执行锁/身份/nonce。

总访问1,000,000、校准软访问100,000、总墙钟1800、软校准300、pre-T0 TCB120、提前1740、单进程AS1GiB、父slice TasksMax4继续冻结。历史TR-A2 WORK/C00与CalDiag前缀的实际资源/退出证据保留其原批次边界；当前新批资格和完整封存成功没有动态证据。

[覆盖修正与历史lock原件hash](evidence/COUNT_COVERAGE_FINDING.json) · [完整scope固定族复核](evidence/COUNT_SCOPE_COVERAGE_REVIEW.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
