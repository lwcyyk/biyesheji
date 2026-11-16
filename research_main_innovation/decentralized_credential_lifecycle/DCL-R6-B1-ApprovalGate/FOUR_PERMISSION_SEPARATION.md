# 四类权限的独立审批记录

## Material Passport

DCL-R6-B1-ApprovalGate，B1-ApprovalGate/review-1，2026-11-16，Asia/Shanghai。本阶段完成合同、语义差异规划与实施准入审查。证据为冻结源码/输入、既有证明和两项分开执行的只读源审查。

正式审议对象为FOUR_PERMISSION_REVIEW_DRAFT.json，SHA-256为`233f817c8a685068503a0f3cd84b60758d4592163773fb7dd47e6181c71c09ea`。四个用户决定字段均为null，当前执行许可为false。[权限记录JSON](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-ApprovalGate/proposals/FOUR_PERMISSION_REVIEW_DRAFT.json)

|权限|本次可审对象|当前裁决|用户决定后仍需履行|
|---|---|---|---|
|CAPACITY_CONTRACT_APPROVAL|B-C1至5的有限政策/条件证明|CONDITIONAL_PASS，完整容量BLOCKED_NULLS|相应TCB/接线、关闭子合同和各null字段生效条件|
|MR_CROSS_INSTANCE_APPROVAL|原14条及原hash|PROPOSED_NOT_EFFECTIVE|实际原生A证据、精确pair、有限use与B当批重证|
|NATIVE_IMPLEMENTATION_AUTHORIZATION|两行为候选、输入绑定、明确测试/oracle/回退|B1_BLOCKED_BY_CLOSE_RESERVE|先满足本轮B1直接门，再取得准确文件/函数/检查授权|
|FULLCHAIN_DYNAMIC_AUTHORIZATION|完整新链的独立执行申请|BLOCKED|完整合同、集成锁、MR所需材料、原件/资源/当前preflight条件和用户执行许可|

审批值相互独立。逻辑政策决定只记录条款采纳，MR决定只采纳有限证据承认原则，源码决定固定允许差异，动态决定固定新实例/argv/限额和检查范围。实际RESOURCE_GATE_PASS由获准的当批校准产生，F1/F4随后受它支配。[DEPENDENCY_GRAPH.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-ApprovalGate/evidence/DEPENDENCY_GRAPH.json)

维护请求当前为待审且eligibility=false。提前把源码许可记录成已批准会跳过本轮第六节明确的关闭条件。最终文本将“材料范围具备审查对象”和“当前实施准入BLOCKED”同时记录。[B1维护请求](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-ApprovalGate/proposals/B1_MAINTENANCE_REQUEST_DRAFT.json)


RESOURCE_GATE_PASS=NOT_OBTAINED

F1=UNRUN_RESOURCE_GATE，F4=UNRUN_RESOURCE_GATE

MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE

STRICT_SEPARATION_INSTANCES=0，PASS_BOUNDED=[]，IMPLEMENTATION_GATE=CLOSED。
