# MR生命周期最小冲突证明

Material Passport：DCL-R6-EvidenceContract-Closure；EvidenceContract-Closure/review-1；2026-11-14（Asia/Shanghai）；有限静态合同/依赖模型审查。


结论分两层：**MR_LIFECYCLE_CONFLICT_PROVED**适用于“同一主批次原生异常关闭必须先于资源门和F1/F4”的强化验收合同；仅根据当前冻结M.formal_gate代码，结论为**MR_LIFECYCLE_CONFLICT_NOT_ESTABLISHED**，因为代码尚未强制要求原生异常关闭证书，存在覆盖缺口。

最小不可满足条件为四条：故障测试使B进入CLOSED；CLOSED吸收；Gate(B)要求该故障已在B发生；F1/F4要求Gate后B仍WORK。最小轨迹WORK(B)→原生异常→CLOSED(B)→Gate前提中WORK被拒绝→F1/F4无法进入。删除任一条件可以构造不同合同，但会改变当前要求。

有限合同模型穷举严格状态关系，FORMAL不可达。它是本轮静态逻辑状态探索，没有导入运行程序、运行F1/F4或建立实际T0。当前源码正常MR64与真实C09恢复的前置关系也已核对，避免将后来增加的研究验收条件误记成旧代码已经实现的条件。

保持严格同实例合同的方案A无法达到完整目标；可以只执行异常关闭专项并保留模型UNRUN。把异常关闭移到模型之后会改变资格门先决次序；只关闭专用worker、不关闭主批次，会改变所验收的主关闭性质；重新激活CLOSED或合并预算亦不属于现合同合法方案。共享预算的嵌套实例需要新的隔离/停止/证据合同，当前尚未授权。

方案B仅在明确批准限定跨实例条款后，分离A的故障能力观察与B的当前工作资格；A保持CLOSED，B独立新窗口。该顺序在抽象合同模型有条件可满足，实际原生证据仍未产生。

[状态模型与最小条件](evidence/LIFECYCLE_FORMAL_MODEL.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
