# 强G比较与原创性门

## Material Passport

DCL-R6-B1-ApprovalGate，B1-ApprovalGate/review-1，2026-11-16，Asia/Shanghai。本阶段完成合同、语义差异规划与实施准入审查。证据为冻结源码/输入、既有证明和两项分开执行的只读源审查。

所有本轮B1工程候选为**COVERED_BY_G**。输入族为同一handoff的n次缺witness观察、并发token重放及预扣/append/关闭持久化失败。度量为原始行/字节、持久写次数、至多一次额度和必要关闭证据完整性。[GENERAL_G_COMPARISON.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-ApprovalGate/evidence/GENERAL_G_COMPARISON.json)

|候选|适用的成熟通用方法G|预测严格差距|
|---|---|---:|
|有界追加日志|固定行/字节slot、sink统一计量|0|
|原子额度计数|串行读改写和持久单调counter|0|
|预付持久化|现有持久预留核心与local allowance|0|
|幂等task/token|绑定交易ID、one-use类别和重放拒绝|0|
|固定reason|有限typed控制码及明确raw来源|0|
|独立关闭预留|保留必要空间、有限首错与失败责任|0|
|manifest与版本容量|标准逐件hash/size/集合检查和版本化输入|0|

未构造使最强G必须付更高必要代价的实例，STRICT_SEPARATION_INSTANCES=0。当前范围为标准工程维护的审批规划，架构原创性状态保持COVERED_BY_G。任何新研究机制的实现仍先满足用户的可证伪分离声明要求。现行IMPLEMENTATION_GATE=CLOSED，源码许可按独立审批处理。


RESOURCE_GATE_PASS=NOT_OBTAINED

F1=UNRUN_RESOURCE_GATE，F4=UNRUN_RESOURCE_GATE

MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE

STRICT_SEPARATION_INSTANCES=0，PASS_BOUNDED=[]，IMPLEMENTATION_GATE=CLOSED。
