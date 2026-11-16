# 证据依赖图与对象分类

Material Passport：DCL-R6-EvidenceContract-Closure；EvidenceContract-Closure/review-1；2026-11-14（Asia/Shanghai）；有限静态合同/依赖模型审查。


阶段/版本敏感的交付图共1142个对象/族节点，拓扑排序通过。1082个计划输出叶保持content_hash=null；16个有界族节点表达可选槽位，未额外加算为物理文件。完整记录提供evidence_id、producer、source_path、content_hash、evidence_type、required_by、verification_rule、storage/retention_requirement和dependency_ids。

```mermaid
flowchart LR
 S[源码与静态输入] --> L[manifest与执行锁]
 L --> R[当批运行身份与原始事实]
 R --> Q[当批校准与资格证明]
 Q --> F[正式模型输出]
 F --> T[终态只读审查]
 T --> N[native manifest与ZIP]
 N --> A[行政审查与ZIP]
 A --> Z[最终收据]
 Z --> C[封存外的事后证书]
 C --> U[新B的use_spec与独立授权]
 U --> B[B当批检查及待批准的限定承认]
```

图中通用封存次序用于说明层级。实际机器图将旧完整正常轨迹、异常前缀替代轨迹、独立MR专项A和待批准B分别标注scope；专项A在C10后关闭，依赖图没有要求A先生成F1/F4。失败前缀仅保留已产生原件，未运行后续测试继续UNRUN，不能据此取得资源门。

|类别|对象|合同地位|
|---|---|---|
|原生原始事实|boot/InvocationID/PID、ACK/waitpid、实际单位与STOP/CLOSED、预算字节、角色/组状态、原始日志|当批强制原件；跨实例仅限拟批准的特定故障观察|
|测试输入与身份|冻结程序/输入、manifest/锁、授权、激活与当前票据|强制身份绑定；新旧实例保持区分|
|独立验证结果|MR/IPC/BC/S34/gate/模型输出|可确定性重算的部分仍按现合同保留；反例轨迹字节具有单独保全责任|
|manifest/完整性证明|native/admin清单、成员hash、包hash|强制完整性集合；排除自己的hash前像|
|行政审查报告|post-exit审查、调用/关闭说明、研究报告|正式post-exit输出与便阅材料分别标注；研究报告位于运行收集目录之外|
|归档封存元数据|native/admin ZIP、最终收据、拟议事后证书|逐层产生；后层不写回前层sealed preimage|

历史TR-A2、旧失败与UNKNOWN保留原身份，当前计划叶未借用其摘要。全量journal外部导出还需固定生成计划/边界；当前自动ROOT生产者与锁中的命令描述分别列示。

[完整机器图](evidence/EVIDENCE_GRAPH_DELIVERY.json) · [族槽位与边界](evidence/EVIDENCE_FAMILY_SCHEMAS.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
