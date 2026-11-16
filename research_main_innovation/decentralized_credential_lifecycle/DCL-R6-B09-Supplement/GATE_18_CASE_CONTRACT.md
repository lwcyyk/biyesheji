# 18项资格门合同

Material Passport：B09-AdmissionFix-static-1/r1；动态UNRUN；旧17项定义保持。

原17项case_id、recipe、预期拒绝前缀与旧合同逐项相同：7项错误状态；缺job；缺原件；原件hash错误；boot、manifest、fixture、execution_lock、T0五项绑定；checker摘要；伪造PASS。新增case_id=GATE-LEDGER-ANOMALY，recipe=ledger_anomaly。

|对象|必须满足的实际结果|
|---|---|
|旧17项|每项MUTATION_DETECTED及对应真实拒绝前缀|
|第18项聚合|REJECT_LEDGER_ANOMALY，受保护资格摘要与原件重算一致|
|聚合健康控制|PASS，subject实际接纳且独立原始检查无异常|
|13个异常原件|REJECT_LEDGER_ANOMALY，原始异常家族被实际触发|
|4个mutant|MUTATION_DETECTED，实际错误接纳被独立原始参考发现|

顶层18与聚合内部18分别计数。执行器遍历冻结顶层完整集合，verify_gate_audit要求恰18个唯一case_id；ledger资格要求内部恰18个唯一ID及4个实际检出，Root读取原件重新计算，FORMAL复核Root资格文件和摘要。配置定义、调度分支、原始oracle与最终资格使用同一当前输入摘要。

新增case尚未运行、原件缺失、输入/源/锁错误、异常未触发、mutant未检出或额外非预期失败时，执行停止且资源资格关闭。顶层结果在完整run_suite返回并通过verify_qualification之后产生，单独填写PASS/REJECT字符串无法形成完整资格链。

[顶层合同](evidence/SOURCE_AFTER/inputs/safety_contract.json) · [聚合合同](evidence/SOURCE_AFTER/inputs/ledger_gate_contract.json) · [一致性检查](GATE_EVIDENCE_CONSISTENCY.md)。
