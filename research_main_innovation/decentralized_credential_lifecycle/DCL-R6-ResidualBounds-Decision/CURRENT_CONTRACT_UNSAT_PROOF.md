# 原256/257合同下完整成功链不可满足

## Material Passport

DCL-R6-ResidualBounds-Decision；ResidualBounds-Decision/review-1；2026-11-16（Asia/Shanghai）；最后一轮既有15项责任的定向静态证明与合同决策。ANALYZED：未启动DCL业务、原生故障或模型执行。

**CURRENT_CONTRACT_UNSAT**，正式标签`FULLCHAIN_UNSAT_UNDER_CURRENT_CAPACITY_CONTRACT`。目标为包含全部必需原件、被接受native封存和行政导出的完整成功链。该结论覆盖所要求的验收目标；某个业务进程是否能启动是另一个命题。

证明使用强制生成的下界，不使用4450等上界。[src/c09_regression.py:59](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_regression.py:59)按冻结34 jobs产生204个事件JSON和34个oracle.json，合计238个互异regular文件。[src/root_ipc_regression.py:222](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/root_ipc_regression.py:222)按56 jobs产生互异ipc_case_000…055。[src/guard.py:1086](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:1086)的完整C09前置流程要求两套回归成功，它们的路径互不相交且成功流程不删除这些原始文件。

|独立矛盾|最小路径子集|包含义务|接受守卫|结论|
|---|---|---|---|---|
|Native|238个C09H原件＋前19个IPC原件=257 raw|全raw＋native manifest1⇒至少258成员|[src/terminal_evidence.py:158](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/terminal_evidence.py:158)≤257|258≤257，矛盾|
|Admin|238个C09H原件＋前17个IPC原件=255 raw|quiescent导出全raw＋native manifest＋nativeZIP⇒至少257文件|[src/startup_lifecycle.py:503](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/startup_lifecycle.py:503)及startup_contract.admin_max_files=256|257≤256，矛盾|

每个三子句矛盾核心分别为：①完整成功要求对应raw子集，②全量包含关系，③原count cap。删除任一子句都可给非负整数的计数满足赋值；native移除一个witness raw后256＋1=257可满足该单独守卫，admin移除一个后254＋2=256可满足该单独守卫。此为计数核心的包含极小性/见证基数极小性，未声称删一份原件后程序还能完成全部资格。

[CURRENT_CAPACITY_UNSAT_WITNESSES.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-ResidualBounds-Decision/evidence/CURRENT_CAPACITY_UNSAT_WITNESSES.json)列出257和255条实际必需路径、源位置及每一删句满足赋值。原887/1082/1083等更强下界继续保留，无需重复求解。byte/ZIP粗上界越界没有被用来证明UNSAT。

native builder可能先创建大于257成员的文件，257守卫在既有ZIP被TR验证时检查；“文件已创建”与“被当前合同接受”分别判断。行政导出256是实际复制时的拒绝线。保持全部原始证据、现行判据和256/257时，完整成功验收集合为空；直接启动只能制造已知不满足目标的尝试。

方案A可以作为“冻结现行合同并接受该负面结果”的明确决定。当前拒绝其下完整成功链/F1F4动态申请，不自动减少必需测试、删除原件、改变格式或扩大守卫。


RESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
