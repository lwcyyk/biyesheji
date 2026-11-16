# B1最小关闭保留合同待批稿

## Material Passport

DCL-R6-B1-CloseReserve-Contract，B1-CloseReserve-Contract/review-1，2026-11-16，Asia/Shanghai。证据为当前冻结文件、源码调用关系、字节语法和抽象失败轨迹。本轮DCL动态、原生故障和模型执行均为0。

精确对象为B1_MINIMAL_CLOSE_RESERVE_DRAFT.json，版本B1-CloseReserve-Contract/review-1，SHA-256为`e6dbcffab36b55fdf14b3df7531cb6a14e6f1b54dac91c6968c7383b8e681963`。当前approved/user_approved/effective/runtime_enabled均false，B_B1-close、物理保留和外部provider保持未实例化。[合同JSON](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-CloseReserve-Contract/proposals/B1_MINIMAL_CLOSE_RESERVE_DRAFT.json)

|序号|合同字段|值/责任|
|---:|---|---|
|1|scope|fresh single B1 initial-handoff E incident and declared normal path; other failures use stated global fallback|
|2|main_quota|{"attempts": 256, "rows": 263, "bytes": 345148, "effective": false}|
|3|close_record_types|["RE01", "RE02", "RE03", "RE04", "RE05", "RE06", "RE07", "RE08", "RE09", "RE10", "RE11", "RE12", "RE13", "RE14", "RE15", "RE16", "RE17", "RE18"]|
|4|record_count|{"Receiver_abort": 2, "core_E_attempts": 59, "core_stable_E_paths": 23, "failed_core_staging_E": 47, "scope_conditions_required": true}|
|5|per_record_bytes|{"ABORTING": 237, "external_closing": 260, "waitpid_normal": 1223, "waitpid_fallback": 565, "marker": "144+R", "fixed43_reason_marker": 189, "Root_generic_marker": 194, "first": "25092+T+B with R_MR<=38", "cleanup_state": "997+11T+B", "cleanup_line": "998+11T+B", "stop_result": "1151+E+sumV", "B": "69+3max(106,29+T)", "healthy_B": 387}|
|6|total_close_bytes|null|
|7|logical_reservation|{"close_limit": null, "request_binding": "same source/batch/boot/handoff/generation, one initial reservation, no refund/regrant", "state": "PROPOSED_NOT_EFFECTIVE"}|
|8|physical_reservation|{"provider": null, "domain_map": null, "data_bytes": null, "inode_count": null, "metadata_bytes": null, "exclusion_guarantee": null}|
|9|access_control|existing RootIPC/BC owner/type/mode/no-link/ACL checks plus provider identity binding|
|10|concurrency_idempotence|ordinary observations and new reservation issuance freeze at stop; already reserved finite cleanup operations may complete afterCLOSED|
|11|durability_order|pre-admission provider proof and logical reservation, local slot debit, full lastRaw/fsync, completion/exhaustion, H exit, existing abort path, actual exit evidence|
|12|fault_responsibility|十类故障矩阵，逐项保持本地/外部/退出/预算/内部/native/admin轴|
|13|overflow|deny new admission, keep actual raw/partial/staging and trigger existing bounded cleanup; incomplete evidence staysUNKNOWN|
|14|unknown|never infer own exit, exact wait status, complete native/admin seal or shared cancellation from missing raw facts|
|15|native_inputs|minimum retained original identity/state/checkpoint/budget/role/marker/waitpid references; native output remains later layer|
|16|admin_inputs|minimum index is a reference to already captured safety raw; cannot serve as deferred-only capture of those facts|
|17|failed_close_path|source808/817+fallback and bounded Root coordinator paths; no new API retries or role restart|
|18|resource_consumption|{"healthy_prepay_write_bytes": 266752, "healthy_prepay_journal_part": 122112, "healthy_prepay_fsync": 2304, "close_full_IO_memory_FD_time": null}|
|19|effectiveness|all numeric/profile/provider/exit-source obligations and exact version proof plus independent user source/run approvals|
|20|version_binding|{"source_lock": "RuntimeAdapt-static-1/r1 current digest set", "future_contract_hash": null, "approval_receipt": null, "execution_identity": null}|


本合同以B1安全事实和实际source载体为边界。scope_E的59次/23稳定路径/47失败staging是条件粗界，normal和其他B1故障各按独立域核算，具体数据/物理总量继续null。主log、预付、close、外部witness和后层archive必须分域绑定，实际路径只计一次。

独立逻辑closing reservation需要与source/batch/boot/handoff/generation绑定一次，普通写者不能花其余额，重放/恢复不发新额度。当前source尚无这样的close ledger。资源pool须真实排他可用，并包括原子发布峰值与metadata，审批前必须提供可信provider凭据及正常/故障责任。

当前可审议必要集合、scope、条件计数、持久顺序、失败责任和oracle规格。完整子合同生效及B1源修改仍受COUNTEREXAMPLE和null阻断。用户决定只按四类独立许可记录，当前决策为待批。

强通用G的有界append、物理预分配/受信保留、幂等事件、固定typed token与原子allowance可覆盖本候选。输入族为同一handoff额度耗尽及有限失败关闭，度量为真实原件字节、生产/staging次数、排他空间和预算/退出安全，预测严格差距0，严格分离实例0。[GENERAL_G_COMPARISON.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-CloseReserve-Contract/evidence/GENERAL_G_COMPARISON.json)


RESOURCE_GATE_PASS=NOT_OBTAINED，F1=UNRUN_RESOURCE_GATE，F4=UNRUN_RESOURCE_GATE。

MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE，STRICT_SEPARATION_INSTANCES=0，PASS_BOUNDED=[]，IMPLEMENTATION_GATE=CLOSED。
