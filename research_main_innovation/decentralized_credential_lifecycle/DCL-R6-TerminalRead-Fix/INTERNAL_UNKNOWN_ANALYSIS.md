# 内部UNKNOWN的独立来源

Material Passport：DCL-R6-TerminalRead-Fix；TerminalRead-static-1/r1；2026-11-13（Asia/Shanghai）；HOST_STATIC_ONLY。

**PFA内部UNKNOWN的直接来源是正常关闭路径未生成mr_close_state.json。期限读取修复不会自动创建该关闭收据。**

旧G.stop_tree正常结束只发布CLOSED及stop_result，协调器保存waitpid；M.abort路径才维护mr_close_state。PFA没有实际Root关键异常，故该内部记录缺失。自动post读取缺件时明确返回UNKNOWN，当前原件中state.status仍CALIBRATING、phase仍RUNNING，由CLOSED支配工作拒绝。

|轴|历史PFA实际结论|新版本策略|
|---|---|---|
|受控进程退出|直接waitpid0/systemd成功退出/自动角色审计|保留各自原始见证|
|cgroup|清空|只作为相应清理事实|
|CLOSED|存在并有正常完成原因|终态只读不覆盖|
|预算|R1907/1907事务/3814行一致|核验原件，不增减R|
|应用内部状态|UNKNOWN，关闭收据缺失|继续UNKNOWN；没有新增收敛规则|
|native|UNRESOLVED|新接入仍需动态seal证据|
|行政|自动SEALED171/172|保持原finalizer实现|

新native归档可以在符合既有正常关闭规则、预算和退出证据完整时保存一个仍含internal UNKNOWN的真实快照；这只证明包完整性，不能升级内部状态。若原MR关闭记录实际存在但为UNKNOWN，原M.seal适用规则继续保留其未决限制。

本轮不重写MR关闭语义或补填旧收据，保持原自动行政成功以及历史native未决。

[源事实](evidence/HISTORICAL_FAILURE_FACTS.json) · [原自动行政结果](evidence/PFA_ORIGINALS/host/STARTUP_FINALIZATION.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原条件结论与原创性裁决保持。
