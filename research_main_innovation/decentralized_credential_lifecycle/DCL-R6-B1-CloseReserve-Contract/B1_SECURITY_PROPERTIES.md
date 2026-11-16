# B1安全性质裁决

## Material Passport

DCL-R6-B1-CloseReserve-Contract，B1-CloseReserve-Contract/review-1，2026-11-16，Asia/Shanghai。证据为当前冻结文件、源码调用关系、字节语法和抽象失败轨迹。本轮DCL动态、原生故障和模型执行均为0。

|性质|裁决|当前依据|
|---|---|---|
|CR-1 MainQuotaExhaustion|PARTIAL|proposed256 quota; caller exception route must be implemented and checked|
|CR-2 CloseReserveAvailability|COUNTEREXAMPLE|ENOSPC after last main/cursor commit with no protected physical floor|
|CR-3 CloseReserveIsolation|UNRESOLVED|no current independent closing ledger/provider isolation|
|CR-4 CloseAttemptBound|CONDITIONAL_PROVED|E branch A6/S8/W1/Q3/H0; global fallback A16/S23/W2/Q7/H52|
|CR-5 NoAbortLoop|CONDITIONAL_PROVED|fixed exception leaves while, two Receiver wrappers; arbitrary API repeated calls excluded|
|CR-6 NoFalseClosed|CONDITIONAL_PROVED|current CLOSED absorption depends on existing stop marker; proposed EXHAUSTED uses distinct fixed exception|
|CR-7 LockReleaseBeforeAbort|CONDITIONAL_PROVED|valid-fd normal context exit unlock/close before caller except; syscall/death uncertainty explicit|
|CR-8 CloseIdempotence|PARTIAL|first-file exclusivity and finite source wrappers; current attempts may append and no close debit ledger exists|
|CR-9 BudgetConservation|CONDITIONAL_PROVED|close functions read budget, no reset/refund/debit; newB1 cursor rule remains proposed|
|CR-10 FailureResponsibility|PARTIAL|existing manager/Root actions explicit; guaranteed independent own-exit provider unbound|
|CR-11 UnknownPreservation|CONDITIONAL_PROVED|source returns/retainsUNKNOWN when evidence or exits fail, no newPASS|
|CR-12 EvidencePreservation|PARTIAL|minimal required facts/carriers identified; physical/provider guarantee unavailable|


结论同时保留实际source、拟B1义务和故障结果。当前系统没有激活新的main/close额度，条件证明不能自动变为实际控制事实。对缺物理保障的候选组合，CloseReserveAvailability存在明确反例，B1源修改准入保留BLOCKED。[SECURITY_PROPERTIES.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-CloseReserve-Contract/evidence/SECURITY_PROPERTIES.json) [MINIMAL_STORAGE_COUNTEREXAMPLE.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-CloseReserve-Contract/evidence/MINIMAL_STORAGE_COUNTEREXAMPLE.json)

每个正常完成判断都需对应身份、锁序、source/counter、实际barrier和真实退出事实，任何缺失或无法归属的raw/staging保持UNKNOWN/拒绝。没有把SOURCE固定布尔值或提交者的PASS用于替代实际原件/内核观察来源。


RESOURCE_GATE_PASS=NOT_OBTAINED，F1=UNRUN_RESOURCE_GATE，F4=UNRUN_RESOURCE_GATE。

MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE，STRICT_SEPARATION_INSTANCES=0，PASS_BOUNDED=[]，IMPLEMENTATION_GATE=CLOSED。
