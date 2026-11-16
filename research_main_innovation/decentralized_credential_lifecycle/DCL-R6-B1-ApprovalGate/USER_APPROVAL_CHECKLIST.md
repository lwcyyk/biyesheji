# 用户逐项审批清单

## Material Passport

DCL-R6-B1-ApprovalGate，B1-ApprovalGate/review-1，2026-11-16，Asia/Shanghai。本阶段完成合同、语义差异规划与实施准入审查。证据为冻结源码/输入、既有证明和两项分开执行的只读源审查。

用户可以对以下对象分别作出决定。当前所有user_decision均为null，审批状态记录准确绑定文件摘要。[APPROVAL_OBJECT_BINDINGS.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-ApprovalGate/evidence/APPROVAL_OBJECT_BINDINGS.json)

|对象|SHA-256|本轮状态|
|---|---|---|
|容量逻辑条款|6843341b1e7dc53b22f93a9faddb9852931d314760f07d7916d55e91c052b019|部分条款可独立审议，完整容量未生效|
|B1维护请求|a7d021d199e033c0bffd5695e204c14db45b340b7c7c03c09b34b30c9c688d16|B1_BLOCKED_BY_CLOSE_RESERVE，源码许可尚未获得|
|四权限记录|233f817c8a685068503a0f3cd84b60758d4592163773fb7dd47e6181c71c09ea|四项决定各自待批|
|原MR14条|9c7524d7af3530b27f4c35d4fef92d9f2f3e431633967b555483b0b58085d069|PROPOSED_NOT_EFFECTIVE|

|决定项|可选择文字/范围|当前记录|
|---|---|---|
|B-C1|可对所列政策或条件推导单独采纳/退修|user_decision=null，approved=false|
|B-C2|可对所列政策或条件推导单独采纳/退修|user_decision=null，approved=false|
|B-C3|可对所列政策或条件推导单独采纳/退修|user_decision=null，approved=false|
|B-C4|可对所列政策或条件推导单独采纳/退修|user_decision=null，approved=false|
|B-C5|可对所列政策或条件推导单独采纳/退修|user_decision=null，approved=false|
|B-C6|记录null及阻断，待充分材料后审议生效|user_decision=null，approved=false|
|B-C7|记录null及阻断，待充分材料后审议生效|user_decision=null，approved=false|
|B-C8|记录null及阻断，待充分材料后审议生效|user_decision=null，approved=false|
|B-C9|记录null及阻断，待充分材料后审议生效|user_decision=null，approved=false|
|B-C10|记录null及阻断，待充分材料后审议生效|user_decision=null，approved=false|
|B-C11|记录null及阻断，待充分材料后审议生效|user_decision=null，approved=false|
|B-C12|记录null及阻断，待充分材料后审议生效|user_decision=null，approved=false|
|B-C13|记录null及阻断，待充分材料后审议生效|user_decision=null，approved=false|


B-C4中持久顺序可以被采纳为逻辑要求，关闭空间数字继续由B-C6保留null。采纳B-C1至5时，记录应保留相应依赖与生效条件。完整B1源码准入需先满足本轮第六节的必要停止信息保留条件，再引用准确文件/函数和测试授权。

对于当前B1维护请求，可直接采用决定文字。

> 我接受本次两行为候选、接口依赖和语义计划的范围审查，记录B1_BLOCKED_BY_CLOSE_RESERVE。待必要关闭子合同具备充分证据后，再单独审议本请求的源码修改许可。

> 我退修该维护请求，并列明需要调整的文件、语义步骤或关闭依赖。

MR可以引用原14条单独作原则决定。当前完整资源资格链审批对象仍需容量、归档、MR所需材料、集成锁和新的执行申请。任何缺证据/部分原件/UNKNOWN都按原始事实记录。

对于完整动态请求，可直接采用下列独立记录。

> 我暂缓完整资格链动态审批，待完整容量合同、所需MR规则/证据、集成源锁及新实例静态准入条件满足后，再审议具体执行申请。

> 我拒绝当前完整动态申请，并指定退修的合同或证据条件。

四类表单各有独立选项和selected=null字段。源码与动态表单当前只记录范围审查、延期、退修或拒绝，实施准入条件按本轮门保留。[四类正式决定表单](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-ApprovalGate/proposals/FOUR_PERMISSION_REVIEW_DRAFT.json)

本轮完整交付后停止，等待用户选择条款与后续授权。具体闭合材料或新授权到达前，同一15项证明范围维持上轮终结状态。[FOUR_PERMISSION_SEPARATION.md](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-ApprovalGate/FOUR_PERMISSION_SEPARATION.md)


RESOURCE_GATE_PASS=NOT_OBTAINED

F1=UNRUN_RESOURCE_GATE，F4=UNRUN_RESOURCE_GATE

MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE

STRICT_SEPARATION_INSTANCES=0，PASS_BOUNDED=[]，IMPLEMENTATION_GATE=CLOSED。
