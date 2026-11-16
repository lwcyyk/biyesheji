# B1范围与依赖裁决

## Material Passport

DCL-R6-B1-ApprovalGate，B1-ApprovalGate/review-1，2026-11-16，Asia/Shanghai。本阶段完成合同、语义差异规划与实施准入审查。证据为冻结源码/输入、既有证明和两项分开执行的只读源审查。

**B1_BLOCKED_BY_CLOSE_RESERVE，BG-2=BLOCKED。** 主日志有限合同具备独立逻辑审议对象。本轮第六节要求实施前证明额度耗尽后关闭调用、必要停止信息保留、预算/CLOSED和资格语义。当前必要关闭子集的剩余空间、隔离与失败责任尚缺充分证据。完整审查逐项列于独立性门文件。[B1_INDEPENDENCE_GATE.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-ApprovalGate/evidence/B1_INDEPENDENCE_GATE.json)

|工作范围|当前依据|实施依赖|
|---|---|---|
|B1主日志有限维护|256尝试、六stage＋ACK1、263主行、345148字节的政策和条件推导|准确预付/绑定、全部sink约束、caller退出、必要关闭子合同和独立源码许可|
|完整关闭保留量|H≤52、core≤212及条件字节式|R_budget/T/E/V、实际关闭原件和持久化故障责任|
|全证据容量|旧scope 4450/4451/4452的条件数量界|各必要对象字节、精确Δ、工作内存/FD/IO和版本合同|
|归档与校验|既有manifest/ZIP/原件oracle规则|原件完整集合、codec、资源约束、当前关闭与quiescence事实|
|MR跨实例承认|原14条独立待批规则|用户原则决定、实际A证据、精确源码pair及B新鲜使用责任|

直接阻断B1的是额度耗尽路径的关闭子合同。可独立定义足以覆盖该路径的较小关闭集合，并证明其受信来源、可用空间和失败责任。本轮现有证据未形成这一充分子合同。全admin/native容量的其他null属于完整资格链后层依赖，后续解除B1直接门时应准确固定证明范围。[DEPENDENCY_GRAPH.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-ApprovalGate/evidence/DEPENDENCY_GRAPH.json)

真实路径从guard的就绪pidfd调用进入observe_exit，在H锁内构造facts、classify并event。异常离开该H上下文后，guard808和外层817各可能执行一次M.abort。MR保存STOP、首错、ABORTING、关闭/回收及最终收据。这些独立对象需要空间。[src/guard.py:799](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:799) [src/c09_handoff.py:252](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_handoff.py:252) [src/manager_recovery.py:317](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/manager_recovery.py:317)

一个最小组合前缀让最后一条PENDING和完成cursor成功持久，随后STOP/CLOSED的新staging创建返回ENOSPC。已有回收动作仍可尝试，持久停止信息保留为UNKNOWN。该前缀用于评估候选组合的准入责任，动态执行数为0。[src/root_ipc.py:105](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/root_ipc.py:105) [B1_INDEPENDENCE_GATE.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-ApprovalGate/evidence/B1_INDEPENDENCE_GATE.json)

ResidualBounds的“可以提交B1有限维护申请”是待审请求。本轮按用户明确给出的实施独立性门完成审查，结果为BLOCKED。有限逻辑条款可以单独获得用户决定，B1实施许可仍需关闭门条件和独立源修改授权。[本轮任务原文](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-ApprovalGate/evidence/TASK_REQUEST.txt) [上轮审批包](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-ResidualBounds-Decision/APPROVAL_DECISION_PACKAGE.md)


RESOURCE_GATE_PASS=NOT_OBTAINED

F1=UNRUN_RESOURCE_GATE，F4=UNRUN_RESOURCE_GATE

MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE

STRICT_SEPARATION_INSTANCES=0，PASS_BOUNDED=[]，IMPLEMENTATION_GATE=CLOSED。
