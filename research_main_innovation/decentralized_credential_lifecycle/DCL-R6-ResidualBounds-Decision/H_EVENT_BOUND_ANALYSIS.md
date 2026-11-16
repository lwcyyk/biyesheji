# H的完整执行域上界

## Material Passport

DCL-R6-ResidualBounds-Decision；ResidualBounds-Decision/review-1；2026-11-16（Asia/Shanghai）；最后一轮既有15项责任的定向静态证明与合同决策。ANALYZED：未启动DCL业务、原生故障或模型执行。

**BOUND_PROVED：H≤52，N_close,core≤212。** 范围是原冻结完整工作流的有限角色/任务图和失败前缀，包含C00–C12、C09H、RANGE、FORMAL以及最多一次C09恢复；旧实例保持CLOSED，本结果不提供新的运行授权。

|可发生H的上下文|数量|每上下文最多halt|小计|
|---|---:|---:|---:|
|Root initial/resume scheduler|2|1|2|
|C00-C12 controller main threads|13|2|26|
|C05 additional budget worker thread|1|2|2|
|C09H controller main|1|2|2|
|FORMAL controller main|1|2|2|
|RANGE controller main|1|1|1|
|RANGE worker processes|14|1|14|
|C02/C03/C04 prepaid child claimers|3|1|3|


总计36个可能的预算执行上下文，计权后52；它们并非同时运行。C00–C12有13个controller，C05另建1条预算worker线程；RANGE冻结34 jobs中12 crash＋2 concurrent各spawn一次，共14个worker；C02/C03/C04各一个prepaid claimer。controller monitor/watchdog没有halt_budget调用，合成Store mode非None时禁用生产halt catch。所有输入和调用证据见[H_FULL_SCOPE_PROOF.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-ResidualBounds-Decision/evidence/H_FULL_SCOPE_PROOF.json)。

单上下文归纳的关键是单调_HALTED：[src/guard.py:630](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:630)在_reserve的try之前检查budget_health；[src/guard.py:703](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:703)在Budget.visit的try之前检查execution_deadline；[src/range_core.py:116](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/range_core.py:116)与[src/range_core.py:168](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/range_core.py:168)也在reserve/claim的try之前valid。第一笔失败可在global_reserve catch688和Budget.visit catch709各调用一次halt；同线程随后入口在try外被拒绝。production range catch163/192最多一笔，之后同样被入口拒绝。无clear或重置；source模块alias由controller844固定，helper进程各只有一个自己的guard实例。

每个列明线程只允许一笔同步在途失败；C05并发的两个线程分别计入。固定父子spawn、Restart=no及无额外API调用闭合上下文数。Root initial/resume scheduler各用直接scalar reserve，至多一次；父协调者、外部停止器和watchdog没有global-reservation事务。继承16次abort、23次stop_tree和2次waitpid后：

\[H\le52,\qquad N_{core,attempt}\le160+52=212.\]

|待回答关系|裁决|
|---|---|
|新任务/恢复/交接数量|通过固定actor/spawn图决定52；C09交接最多一次，恢复最多一次|
|预算事务/访问总量|成功事务上限不能独自约束失败H；在counter写入前错误可使R增量0却H增加|
|零访问重复|Budget嵌套同一次错误可能增加H两次；入口HALTED检查与有限线程数阻止无限重入。直接反复调用halt_budget(x_n)属于域外|
|CLOSED后增长|在途失败或尚未HALT的直接scalar入口，仍可在counter-lock deadline发现CLOSED后记录一次失败；它不会发grant，之后入口停在try外，总52已含此情形|
|idle前缀|没有新预算调用的C09 idle/no-new-budget关闭前缀继续H=0，作用域保持|

H计量budget-origin halt调用/STOP发布尝试，M.abort的STOP另已计入160；相同STOP路径覆盖写不会变成52个独立文件。因此稳定核心路径粗界54保持，212没有成为新关闭配额。_HALTED仍为进程内flag，52并不证明共享停止、组空或证据完整性。


RESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
