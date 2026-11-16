# 强通用基线与实现门

Material Passport：DCL-R6-C09-BoundClosure；C09-BoundClosure/review-1；2026-11-15（Asia/Shanghai）；有限源码/历史原件/数学合同审查。


|候选方向|具体输入族|度量|适用强G|预测差距|裁决|
|---|---|---|---|---|---|
|PENDING quota|X_n: one handoff, n repeated valid missing-witness observations|Persisted bytes, observation work, durable write count|Bounded append log + pre-debited event/byte quota + fail-closed cursor|Same chosenQ and schema bounds: O(Q*L), no strict difference|COVERED_BY_G|
|Versioned capacity|Y_m: m original files with explicit path/byte/hash manifest|Metadata bytes, total read/write/hash work|Versioned verification contract + standard ZIP manifest and explicit file/byte caps|Same O(m+B) verification and same original set|COVERED_BY_G|
|Segmented archive|Z_{m,s}: m originals partitioned into s standard segments|Complete-set validation work and lossless retained bytes|Standard archives + content-addressed/versioned root and per-segment manifests|Same full-set/hash checks; generic method can use identical segmentation|COVERED_BY_G|
|MR cross-instance evidence|A native scenario certificate applicable to one explicitly bound B instance|Native fault-test count and verifier/current-state check work|Version-bound software qualification evidence + exact target/current-state revalidation|Same limited evidence class and same current B obligations|COVERED_BY_G|

每个方向都有可构造的同费用覆盖实例：n=17或257的PENDING前缀、1082路径清单、两标准分段、一个A证书与一个B目标。成熟有界日志/预付配额、标准ZIP与内容寻址/版本化manifest、目标绑定的软件资格证据都能采用相同检查和同样的停止决策。当前没有证明G在这些实例中必须付更高代价。

C09自环反例揭示的是验证基础设施资源合同缺口；它没有构成D1/D2架构的严格分离实例。以上预测严格差距均为0，未形成满足实现门的候选。全局所有算法的最优性也未由本地比较声称。

原BASELINE_G/SEPARATION_GATE的同能力/共同费用及既有D1/D2覆盖裁决继续有效。日志限额等属于通用工程合同维护方向，任何未来最小维护代码仍需明确授权；当前候选机制、日志/预算/封装/资格门实现修改均0。

[具体比较与输入实例](evidence/GENERAL_G_COMPARISON.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
