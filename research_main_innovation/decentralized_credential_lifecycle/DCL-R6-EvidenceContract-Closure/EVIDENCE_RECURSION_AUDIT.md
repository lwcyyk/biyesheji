# 递归、自摘要与封存层级审查

Material Passport：DCL-R6-EvidenceContract-Closure；EvidenceContract-Closure/review-1；2026-11-14（Asia/Shanghai）；有限静态合同/依赖模型审查。


现行冻结收集边界没有形成自动扩张的证据递归。guard.seal收集ROOT常规原件并按文件名排除EVIDENCE_MANIFEST.json/EVIDENCE.zip，随后加入manifest一次；行政快照和报告写在ROOT之外，host manifest不收集其自身、最终ZIP或含该ZIP摘要的最终收据。额外研究报告也位于收集前像之外。

三条最小潜在环需要在合同中显式阻断：

1. 事后MR证书→native manifest→native ZIP→事后MR证书。触发条件：验收器要求先看到native/admin seal，同时证书被要求在创建该native包之前进入ROOT。新oracle的from_snapshot需要事后admin证明；其未接入入口，当前属于接线风险，未作为已发生动态循环。
2. 最终行政收据→admin manifest→admin ZIP→最终行政收据。触发条件：把包含admin ZIP hash的最终收据纳入同一个ZIP。现有层级已经切断。
3. B授权收据↔B最终use record。触发条件：授权绑定use record hash，use record又绑定该授权hash。草案采用独立use_spec→授权收据→实际use record，顺序单向。

机器图按文件的阶段版本区分预算前缀/终态预算、pre-native review/post-seal review，避免将原地更新的同一文件名误当成自引用hash。模型中的可重算报告与用户便阅报告不反向增加更早的必需集合。证据分类不会删除原件。

每个环都有明确触发条款和切断位置。将环反复展开不会产生有效的无限文件要求；它首先构成不可同时满足的hash/先后约束。固定点由分层集合求得，包内嵌已有ZIP只按当前层一个成员计数，内部完整性仍逐件核验。

[候选最小环与拓扑顺序](evidence/EVIDENCE_GRAPH_DELIVERY.json) · [源行证据](evidence/SOURCE_EXCERPTS.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
