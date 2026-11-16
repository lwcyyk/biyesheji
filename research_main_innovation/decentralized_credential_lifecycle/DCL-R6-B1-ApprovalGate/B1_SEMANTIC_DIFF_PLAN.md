# B1最小语义差异计划

## Material Passport

DCL-R6-B1-ApprovalGate，B1-ApprovalGate/review-1，2026-11-16，Asia/Shanghai。本阶段完成合同、语义差异规划与实施准入审查。证据为冻结源码/输入、既有证明和两项分开执行的只读源审查。

该计划以现有Receiver.observe_exit()调用签名、main/window字段集合和原关闭接口为边界。候选耗尽路线采用现有AdmissionBlocked及固定quota耗尽代码，经H上下文退出进入既有异常包装器。该规划仍受B1关闭门约束。[SEMANTIC_DIFF_STEPS.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-ApprovalGate/evidence/SEMANTIC_DIFF_STEPS.json)

|步骤|主题|拟议语义|源码位置|
|---|---|---|---|
|SD01|绑定与版本|static_manifest/execution_lock/authorization及quota输入全部精确绑定，profile字段有唯一schema标识|guard.py:232-278|
|SD02|预付位置|C09H、RootIPC和BC资格结束后，在launch_one(C09)前完成256次scalar预付，依赖有效C00 ticket及原calibration deadline|guard.py:1095-1096,629-691|
|SD03|初始化与handoff绑定|预付cursor初始化独占一次，已有/foreign/残留/模糊记录进入拒绝，handoff_id确定后同H锁绑定一次|c09_handoff.py:168-187|
|SD04|全部主行sink|event、六publish与ACK共享类别/slot/字节预扣，新增policy/ordinal放cursor以维持原main schema|c09_handoff.py:75-89,196,277|
|SD05|观察准入|停止、身份和现有终态门后，在check_base/facts/classify/event前消费一个新观察资格，失败烧额|c09_handoff.py:252-277|
|SD06|持久完成|预扣cursor持久后进行一次raw append/fsync，再发布完成cursor，成功终态先锁存后解锁cleanup|c09_handoff.py:277-287|
|SD07|额度耗尽|256th PENDING原始facts完整保留，发布耗尽吸收状态。候选采用现有AdmissionBlocked及固定quota耗尽代码衔接，H上下文退出后由外层异常路径消费，257分类/主行增量0|guard.py:799-818|
|SD08|既有异常关闭|固定异常经过H上下文释放后交付808和817两层现有M.abort，实际退出及所有必要收据计量，耗尽异常终止原观察循环|guard.py:806-823;manager_recovery.py:317-400|
|SD09|重放与恢复|相同binding/handoff/kind/ordinal再次提交为已消耗，模糊持久化恢复进入停止/UNKNOWN，T0和账保留原来源|c09_handoff.py:323-347|
|SD10|封存和oracle|新raw/cursor/首错/staging按唯一路径计入未来Δ，独立oracle重算，原封存和资格接口接受完整原件|guard.py:993-1027|


|入口/分支|当前行为|申请中的必要接线义务|
|---|---|---|
|guard799–800|就绪pidfd触发observe_exit|每次调用先经过当前终态和quota准入|
|observe_exit261–277|check_base、facts、classify、event|第257次在这些新观察动作之前被拒绝|
|PENDING返回278|当前就绪fd保留，caller再次迭代|第256条保存后耗尽状态被消费，观察循环退出|
|caller801–805|仅VERIFIED/CLOSED有专门处理|新增EXHAUSTED返回值需要实际消费，当前最小计划选择异常路线|
|CLOSED分支804|stop_tree(close=False)|CLOSED返回值须基于已经存在的真实停止事实|
|两个异常包装器|808 abort后抛出，817可再次abort|按既有有限责任计量两次关闭，不将每次重试重新交回while|
|锁序|observe_exit持H，stop_tree758会再取H|cursor/raw/终态持久阶段完成后由上下文释放H，再进入M.abort/stop_tree|

全部三event调用及六stage都进入同一总行/字节约束。修改observe_exit的单个计数检查无法覆盖publish与ACK成本。新增policy hash、ordinal和类别位存入独立cursor，main/window字段变化须重新推导1322/948/1028。[src/c09_handoff.py:75](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_handoff.py:75) [src/c09_handoff.py:196](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_handoff.py:196)

相同facts的后续合法观察是新的付费ordinal。幂等责任针对已预扣token、stage类别和ACK，已有observe_exit零参数API由内部身份/序号管理支持。BC.Store的.bc随机staging没有目标名标签，关联当前B1 writer/绑定及辨认失败遗留的规则需要在候选中明确。如果方案要求helper API变化，应先扩大对应文件申请。[src/boot_continuity.py:86](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/boot_continuity.py:86) [BINDING_SCOPE_REFINEMENTS.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-ApprovalGate/evidence/BINDING_SCOPE_REFINEMENTS.json)

预付需要256次scalar调用。guard640拒绝amount=256的普通scalar请求，生产range接口的固定task目前属于C02/C03/C04。可审查的位置为1095之后、1096启动C09之前，并显式借用有效C00票据检查原deadline，在所有路径恢复_TICKET。prepay_after与最终handoff.counter之间还应核对C09 controller初始一次合法Budget.visit。[src/guard.py:629](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:629) [src/manager_recovery.py:462](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/manager_recovery.py:462) [src/guard_probe.py:99](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard_probe.py:99)

旧v2的顶层schema实际为字段说明字符串，原文件hash和version可准确定位该历史对象。未来机器契约应使用唯一schema标识，将字段说明另置profile字段，并生成新待批摘要。[DRAFT_HASH_AND_STATUS_CHECK.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-ApprovalGate/evidence/DRAFT_HASH_AND_STATUS_CHECK.json)


RESOURCE_GATE_PASS=NOT_OBTAINED

F1=UNRUN_RESOURCE_GATE，F4=UNRUN_RESOURCE_GATE

MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE

STRICT_SEPARATION_INSTANCES=0，PASS_BOUNDED=[]，IMPLEMENTATION_GATE=CLOSED。
