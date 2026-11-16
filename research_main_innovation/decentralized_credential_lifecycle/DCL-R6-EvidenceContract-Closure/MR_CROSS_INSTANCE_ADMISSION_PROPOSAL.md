# 限定跨实例承认合同草案

Material Passport：DCL-R6-EvidenceContract-Closure；EvidenceContract-Closure/review-1；2026-11-14（Asia/Shanghai）；有限静态合同/依赖模型审查。


**DRAFT / PENDING_USER_APPROVAL / runtime_enabled=false。** 本轮只有规则设计权限，草案没有改变当前资格门。

候选推导规则：Approved(rule) ∧ NativeObserved(A,scenario) ∧ PrimaryAutoClosed(A) ∧ SealedAndRechecked(A) ∧ ReviewedSourcePair(A,B) ∧ SameBootEquivalentTCB(A,B) ∧ ExactFreshUse(B) ⇒ ApplicableObservedImplementationScenario(A→B)。该结论仅用于替代强化验收中的那一项异常场景观察义务；B的WORK、当前监督、预算、C09及RESOURCE_GATE均需要各自前提。

|条款|名称|正式前提|
|---|---|---|
|R01|POLICY_AUTHORITY|Current explicit user approval of this exact rule digest plus a separate fresh authorization for target B|
|R02|A_UNIQUE_NATIVE_ORIGIN|Distinct A batch/boot/InvocationID/PID/source lock; actual unit exit79 and raw journal/query events, never a simulation flag alone|
|R03|SOURCE_PAIR_RELATION|A/B exact artifact locks both explicitly reviewed; security-relevant code has identical projected AST under a closed, per-node namespace-only map|
|R04|SAME_BOOT_TCB|A.boot==B.boot; exact kernel/systemd/Python/loader/libc/libm/TCB fingerprints and effective sandbox contract match; actual B refreshed|
|R05|FAULT_SCOPE|Only dedicated current service failure -> unreviewed failed-unit detection -> main A automatic close with Root/stopper otherwise available|
|R06|PRIMARY_AUTOMATIC_CLOSE|A STOP/CLOSED/role exits/group empty/budget and deadline preservation confirmed; fallback/manual cleanup alone cannot satisfy this class|
|R07|INDEPENDENT_RAW_ORACLE|Named independent checker hashes and re-evaluation of immutable raw originals; shared parser/TCB assumptions disclosed|
|R08|SEALED_ARTIFACTS|A native and administrative seals completed and separately verified; missing/partial/UNKNOWN status refuses the capability-observation class|
|R09|POSTSEAL_CERTIFICATE|Certificate written after A seals, outside both sealed preimages; commits both archive/manifest hashes and actual oracle result|
|R10|TARGET_B_USE_BINDING|One predeclared B batch/boot/lock + fresh use nonce + approval digest + certificate hash. Use spec precedes B receipt; realized record follows receipt|
|R11|CURRENT_B_PROOFS|Every listed current-instance obligation is independently checked by B; A approval cannot grant B WORK/RESOURCE_GATE or change budgets|
|R12|INVALIDATION|Boot, source, TCB, fault scope, approval or target/use mismatch invalidates; no wildcard new target or indefinite cached admission|
|R13|FRESH_OPERATOR_AUTH|Current B direct user authority pins certificate/policy/use-spec hashes; withdrawn or superseded authority rejects; no unproved monotonic registry assumption|
|R14|EVIDENCE_COMPLETE|Every required raw/member/source artifact available and bound; missing/extra/substituted/cross-version files reject|

始终由B当批重新证明：

- boot_id
- execution_lock
- systemd unit instances/InvocationIDs
- UID/GID/groups
- runtime/ELF/map identity
- budget counter/intent/journal health
- T0/deadline/stop_at
- WORK/C00
- real C09 ACK/waitpid/fresh classification
- normal ManagerRecovery health and current supervision
- RLIMIT_AS/TasksMax/cgroup restrictions
- current independent stop source and closure preconditions
- C00-C12/BC/IPC/C09H/MR64/PT/PF/TR/RA/S34/gate18 as current contract requires
- current original-byte rechecks and all other resource-gate mandatory fields

事后证书C_A在A native/admin封存和原始复核后，写在两者hash前像外；随后生成独立use_spec，固定C_A、rule、artifact-pair和B身份/boot/执行锁/nonce；B授权收据固定use_spec hash；最后实际use record绑定授权hash。任何缺值或逆向自hash均拒绝。当前证书、nonce、B身份与授权收据均未签发。

A新增failed单位的后续只读分类只能依赖精确A单位/InvocationID/PID/boot/退出及CLOSED原件hash；禁止reset-failed、广泛白名单或把A的故障状态授为B监督职责。实际实现仍须在明确批准后单独审查。

[完整机器规则](proposals/MR_CROSS_INSTANCE_RULE_DRAFT.json) · [证书及use记录顺序](proposals/MR_CERTIFICATE_AND_USE_SCHEMA.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
