# 资格门负向检查

Material Passport：17项负向检查＋1项正向控制已实现并冻结；当前全部UNRUN。

根验证器先以真实34项原始重算结果作正向控制，再深拷贝该候选收据，改变指定错误行为/字段，将投影交给同一verify_sealed_safety。原始预算、断言函数和原始文件保持。每项必须由指定前缀拒绝；其他异常、未拒绝或未执行均阻断。每次检查计入同一主账。

|投影|必要拒绝|
|---|---|
|状态UNRUN / FAIL / INCONCLUSIVE|RANGE_REQUIRED_RESULT|
|MUTATION_NOT_DETECTED|RANGE_REQUIRED_RESULT|
|EVIDENCE_MISSING / HASH_MISMATCH / UNEXPECTED_RECOVERY|RANGE_REQUIRED_RESULT|
|缺一个job|RANGE_RECEIPT_JOB_SET|
|缺原始文件摘要集合|RANGE_RAW_EVIDENCE_MISSING|
|原始文件hash不匹配|RANGE_RAW_HASH_MISMATCH|
|boot / 源manifest / 输入 / 执行锁 / T0绑定错误（5项）|RANGE_RECEIPT_BINDING|
|独立检查器hash错误|RANGE_CHECKER_DRIFT|
|只保留伪造PASS/accepted标志、移除原件|RANGE_RAW_EVIDENCE_MISSING|

完整case_id、投影recipe和预期拒绝前缀在合同gate_negative_cases中。结果写入root保护的GATE_NEGATIVE_AUDIT：输入投影摘要、真实拒绝原因、前后时标、当前绑定与root身份。FORMAL再检查该审计集的完整性与摘要。仅写布尔标志或删除某项检查不构成资格。

下一动态运行还须核对这17项是否真实被拒绝；本轮的静态分支审阅和编译不会填写其动态结果。详见evidence/EXECUTION_STATUS.json。
