# batch09负向资格门覆盖审计

Material Passport：DCL-R6-batch09；2026-11-12；STATIC_ONLY；17项动态执行0。

|现有recipe|数量|直接检查目标|
|---|---:|---|
|status|7|UNRUN/FAIL/INCONCLUSIVE/MUTATION_NOT_DETECTED/EVIDENCE_MISSING/HASH_MISMATCH/UNEXPECTED_RECOVERY|
|missing_job|1|完整job集合|
|missing_raw|1|原始文件缺失|
|raw_hash|1|原始文件摘要|
|binding|5|boot_id、manifest、fixture、execution_lock、T0|
|checker_hash|1|独立checker摘要|
|forged_PASS|1|伪造结果且缺原件|

以上17项的actual_detected、rejected_by及运行轨迹均null。guard.exercise_gate_negatives对隔离receipt副本调用verify_sealed_safety，未设置全局预算账异常recipe。

用户本轮§6.7明确列出预算账异常；当前17项无法提供该专项负向见证。root_verify_safety会在审核前后对真实账调用check_global_ledger，require_formal_admission还做fresh健康复核；这些是正向健康检查。S1–S9故障作用局部合成账。当前代码中尚缺独立异常账副本进入预算资格检查并被拒绝的冻结测试。

**D09-A03=REQUIRED_TEST_MISSING。** 原17项保留；最小补充建议添加至少一项“counter/intent不一致”的合成账拒绝测试，并用一致副本作正控制，隔离真实活账。该建议尚待静态实现授权，新增代码和测试运行均为0。修订后需重算计费，原62,546上界只适用当前冻结清单。

[逐项审计](evidence/GATE_NEGATIVE_COVERAGE_AUDIT.json)；[补充申请](BATCH09_MINIMAL_SUPPLEMENT_REQUEST.md)。
