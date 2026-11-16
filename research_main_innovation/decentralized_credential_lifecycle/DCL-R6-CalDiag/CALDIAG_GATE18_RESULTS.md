# 18项负向资格门实际状态

Material Passport：DCL-R6-CalDiag；batch09-r1；B09-AdmissionFix-static-1/r1；2026-11-12；真实方案B；入口1次、测试重跑0。

顶层18项统一UNRUN_AFTER_RESUME_FAILURE。原17项没有进入执行；新增GATE-LEDGER-ANOMALY的健康控制、13异常和4个mutant也均UNRUN，实际拒绝原因/故障触发/变异检出数为null。GATE_NEGATIVE_AUDIT与GATE_LEDGER_QUALIFICATION的当前批资格文件均未生成。

实际回执、冻结输入和执行清单均绑定18项；调度在更早的恢复manager检查失败后停止，新增用例保持原件待运行状态。当前全局账的行政格式核对通过仅说明已产生账的一致性，新增异常门的动态检出责任继续未完成。

RESOURCE_GATE_PASS=NOT_OBTAINED。F1/F4维持UNRUN_RESOURCE_GATE，本次scope即使全门通过也只允许诊断关闭。后续正式批次需要重新取得当批资格。

[机器状态](evidence/CALDIAG_RESULT.json) · [原始账行政核验](evidence/JOURNAL_ACCOUNTING.json) · [冻结42项](evidence/SOURCE_AND_SCOPE_ADMISSION.json)。
