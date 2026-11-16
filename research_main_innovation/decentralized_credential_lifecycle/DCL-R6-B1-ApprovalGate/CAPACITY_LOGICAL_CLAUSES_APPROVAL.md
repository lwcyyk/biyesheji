# 容量逻辑条款审批稿

## Material Passport

DCL-R6-B1-ApprovalGate，B1-ApprovalGate/review-1，2026-11-16，Asia/Shanghai。本阶段完成合同、语义差异规划与实施准入审查。证据为冻结源码/输入、既有证明和两项分开执行的只读源审查。

本次正式审议对象为CAPACITY_LOGICAL_CLAUSES_DRAFT.json，SHA-256为`6843341b1e7dc53b22f93a9faddb9852931d314760f07d7916d55e91c052b019`。每个B-C条款独立记录证明、源码、输入域、参数、闭合程度、依赖、差异文件、负向测试、适用范围和生效条件，全部用户决定为null。[待批条款JSON](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-ApprovalGate/proposals/CAPACITY_LOGICAL_CLAUSES_DRAFT.json) [CAPACITY_CLAUSE_MATRIX.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-ApprovalGate/evidence/CAPACITY_CLAUSE_MATRIX.json)

分类A为可单独选择的政策，分类B为有条件证明及其显式TCB/接线义务，分类C为数值null并阻断完整容量生效。

|条款|分类|参数|闭合范围|依赖|
|---|---|---|---|---|
|B-C1 C09观察尝试上限|A|256|POLICY_REVIEW_READY|B-C4，B-C5，B-C6耗尽关闭子合同|
|B-C2 主日志记录数|B|263|CONDITIONAL_PROVED|B-C1，B-C4，稳定H锁inode，存储持久性和可信Root|
|B-C3 主日志字节预留|B|345148|CONDITIONAL_PROVED|B-C2，B-C4，编码前字段验证，batch和mode长度profile|
|B-C4 预付、持久预扣和关闭空间责任|B|{"prepay_visits": 256, "main_reserved_bytes": 345148, "physical_close_space": null}|PARTIAL_ORDER_PROVED_SPACE_OPEN|有效C00 ticket和旧deadline，单次预付绑定，B-C6，跨角色失败可见性|
|B-C5 超额观察前置拒绝|B|{"rejected_attempt": 257, "new_classifications": 0, "new_main_rows": 0}|SEMANTIC_OBLIGATION_READY|B-C1，B-C4，B-C6，outer abort责任有限|
|B-C6 完整关闭保留量|C|null|NULL_BLOCKS_EFFECTIVENESS|ResidualBounds最终未决责任，确切源码/输入/测试差异和审批|
|B-C7 行政证据最大数量|C|null|NULL_BLOCKS_EFFECTIVENESS|ResidualBounds最终未决责任，确切源码/输入/测试差异和审批|
|B-C8 Native ZIP最大成员数|C|null|NULL_BLOCKS_EFFECTIVENESS|ResidualBounds最终未决责任，确切源码/输入/测试差异和审批|
|B-C9 完整总字节|C|null|NULL_BLOCKS_EFFECTIVENESS|ResidualBounds最终未决责任，确切源码/输入/测试差异和审批|
|B-C10 单文件最大大小|C|null|NULL_BLOCKS_EFFECTIVENESS|ResidualBounds最终未决责任，确切源码/输入/测试差异和审批|
|B-C11 内存、FD、IO与syscall|C|null|NULL_BLOCKS_EFFECTIVENESS|ResidualBounds最终未决责任，确切源码/输入/测试差异和审批|
|B-C12 native与行政封存资源|C|null|NULL_BLOCKS_EFFECTIVENESS|ResidualBounds最终未决责任，确切源码/输入/测试差异和审批|
|B-C13 墙钟与外部TCB假设|C|null|NULL_BLOCKS_EFFECTIVENESS|ResidualBounds最终未决责任，确切源码/输入/测试差异和审批|


B-C1的256是显式工程选择，合法witness延迟可能导致提前资源关闭。B-C2的263依赖全部生产者共享七类别位和256分类槽。B-C3按256×1322＋6×948＋1028=345148预留，包含紧凑JSON和LF。原始行已写字节与cursor已预扣数量分别核对。

B-C4可以单独审阅预付、预扣、append/fsync、completion及终态锁存的逻辑顺序。关闭空间的充分性继续由B-C6承担。B-C5要求257次前置拒绝的分类和主行增量为0，并明确caller终止和有限关闭责任。类B条款的审批文字须保留source profile、身份、稳定锁与存储语义条件。

可供用户选择的逻辑决定文字如下。

> 我批准B-C1的256次有限观察政策，并认可B-C2的263行、B-C3的345148字节条件推导，以及B-C4持久顺序和B-C5前置拒绝的逻辑要求。实际生效等待本轮列明的TCB、关闭子合同、源码许可及对应检查。完整容量和其余权限继续按独立条款审议。

> 我要求调整或退修所列逻辑条款，具体以条款ID和参数记录用户决定。

条款1至5的逻辑审批对象与B-C6至13的null阻断对象在同一审议表中显式列出。B1实施门当前为B1_BLOCKED_BY_CLOSE_RESERVE。[USER_APPROVAL_CHECKLIST.md](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-ApprovalGate/USER_APPROVAL_CHECKLIST.md)


RESOURCE_GATE_PASS=NOT_OBTAINED

F1=UNRUN_RESOURCE_GATE，F4=UNRUN_RESOURCE_GATE

MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE

STRICT_SEPARATION_INSTANCES=0，PASS_BOUNDED=[]，IMPLEMENTATION_GATE=CLOSED。
