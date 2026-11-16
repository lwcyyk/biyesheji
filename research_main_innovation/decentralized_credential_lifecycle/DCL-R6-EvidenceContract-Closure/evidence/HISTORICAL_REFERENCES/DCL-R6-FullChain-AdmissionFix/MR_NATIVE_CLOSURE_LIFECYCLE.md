# MR关闭与完整链生命周期冲突

Material Passport：DCL-R6-FullChain-AdmissionFix；FullChainAdmission-static-1/review-1；2026-11-13；HOST_STATIC_REVIEW_ONLY。


**MR_NATIVE_CLOSURE_LIFECYCLE_CONFLICT。** 当前要求同时包含：异常测试关闭主批次A；CLOSED吸收且T0/预算保持；B资格要求当前批次异常关闭证据；同一批次继续F1/F4。前三项成立后继续工作资格终止，与第四项矛盾。

现行M.formal_gate只读取当前root/binding的MR_QUALIFICATION和MR_RECOVERY_REVIEW；旧阶段A/B申请允许B另建身份，却明确A已关闭窗口没有可复用运行资格。当前完整合同没有授予跨批次异常关闭PASS的承认规则。

本轮仅创建主机审查材料，独立原生实例0、预算/启动窗口0。专项A设计关闭其本身；测试完成后继续保持CLOSED。独立子实例共享主预算、嵌套stop责任及扩展证据承认均尚未获得第七节要求的明确批准。

具体修订申请为：允许先行A作为相同冻结实现/运行时/故障模型的“实现级异常关闭证据”；B核对A精确源/合同/hash/boot/InvocationID/关闭原件和封存，只采纳该有限实现证据，同时B自行重做当前C00–C12/C09/MR64/恢复/S34/门18/资源/预算。A的T0、R、收据和RESOURCE_GATE均不向B转移。此规则只有取得明确授权并实际集成后才生效。

A新增failed单位的后续只读审查需固定A的精确事件/关闭摘要，既有无关单位保持原样。当前未放宽任何资格门，B_release=false。

[精确矛盾与修订提案](proposals/LIFECYCLE_CONTRACT_REVISION.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。全部原生动态测试UNRUN。
